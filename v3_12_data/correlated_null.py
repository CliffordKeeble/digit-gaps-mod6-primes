#!/usr/bin/env python3
"""Task 1 (Paper 3 v3.14): §6.4 Test correlated null. PRINCIPAL fifth-star item.

Background. v3.13 §6.4 Test reports inert counts for first 100/1000 non-ramified
primes p ≡ 1 (mod q) across q ∈ {4, 6, 8, 12} with joint p ≈ 0.063 (sign-test)
and Stouffer ≈ 0.07 under independence. The four moduli are NOT independent:
p ≡ 1 (mod 12) ⊂ p ≡ 1 (mod 4) ∩ p ≡ 1 (mod 6); p ≡ 1 (mod 8) ⊂ p ≡ 1 (mod 4).
A single small inert prime in an inner class contributes to multiple rows of
the §6.4 Test table, so the independence-based joint p is optimistic.

Method. Build the correlated null by permuting χ₅ values across all primes in
the universe U = first M = 20,000 non-ramified primes, recomputing the four-q
test on each shuffle, and forming empirical null distributions for the joint
sign-test count and Stouffer combined Z.

Per CinC Q2 confirmation: Stouffer route uses parametric one-tailed
z = (k − 500) / √250 per q; Z_combined = Σ z / √4. Right-tailed direction.

Per CinC Q3: M = 20,000 is sufficient (1000 primes ≡ 1 mod 12 needs ~4000
from U; ample margin).

Verification gate. Per-q natural inert counts must reproduce v3.13 §6.4 Test:
{508, 509, 516, 514} for q ∈ {4, 6, 8, 12} at n=1000. Halt if not.

Reproducibility. Numpy seed = trial * 137 + 42 per shuffle, matching the
v3.11/v3.12/v3.13 shuffle convention.
"""
import math
import os
import sys
import csv
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve, chi5

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

SIEVE_LIMIT = 300_000  # 1000 primes ≡ 1 mod 12 reach ~ p ~ 30k; 300k is generous
M = 20_000              # universe size: first M non-ramified primes
K = 10_000              # number of shuffles
QS = [4, 6, 8, 12]
N_PER_Q = 1000          # first 1000 primes ≡ 1 mod q in U
NATURAL_INERTS_V3_13 = {4: 508, 6: 509, 8: 516, 12: 514}


def parametric_z(k, n=N_PER_Q, p=0.5):
    """Right-tailed parametric z for binomial(n, p): z = (k - np) / sqrt(np(1-p))."""
    return (k - n * p) / math.sqrt(n * p * (1 - p))


def normal_sf(x):
    """P(Z >= x) for standard normal."""
    return 0.5 * math.erfc(x / math.sqrt(2))


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Sieving primes up to {SIEVE_LIMIT}...")
    primes = sieve(SIEVE_LIMIT)
    # Universe: first M non-ramified primes (excluding p=5).
    non_ramified = [p for p in primes if chi5(p) != 0]
    if len(non_ramified) < M:
        print(f"  ERROR: only {len(non_ramified)} non-ramified primes available; need {M}")
        sys.exit(1)
    U = np.array(non_ramified[:M], dtype=np.int64)
    chi_natural = np.array([chi5(int(p)) for p in U], dtype=np.int8)
    print(f"  Universe U = first {M} non-ramified primes "
          f"(p_min = {int(U[0])}, p_max = {int(U[-1])})")
    print(f"  chi5 multiset: +1 count = {(chi_natural == 1).sum()}, "
          f"-1 count = {(chi_natural == -1).sum()}, "
          f"0 count = {(chi_natural == 0).sum()}")

    # Per-q index lists (fixed across shuffles)
    indices_per_q = {}
    for q in QS:
        mask = (U % q == 1)
        idx = np.where(mask)[0]
        if len(idx) < N_PER_Q:
            print(f"  ERROR: only {len(idx)} primes ≡ 1 mod {q} in U; need {N_PER_Q}")
            sys.exit(1)
        indices_per_q[q] = idx[:N_PER_Q]
        print(f"  q={q:>2}: first {N_PER_Q} primes ≡ 1 mod q span U-indices "
              f"{int(idx[0])}…{int(idx[N_PER_Q-1])} "
              f"(p_max = {int(U[idx[N_PER_Q-1]])})")

    # ---- Verification gate: per-q natural inert counts ----
    print(f"\n{'='*72}")
    print("Verification gate: per-q natural inert counts")
    print(f"{'='*72}")
    natural_inerts = {}
    fail = False
    for q in QS:
        k = int((chi_natural[indices_per_q[q]] == -1).sum())
        natural_inerts[q] = k
        target = NATURAL_INERTS_V3_13[q]
        ok = (k == target)
        flag = 'OK' if ok else 'FAIL'
        print(f"  q={q:>2}: natural inerts = {k}  (target {target})  {flag}")
        if not ok:
            fail = True
    if fail:
        print("  HALT: per-q anchor mismatch.")
        sys.exit(1)

    # Natural's Stouffer Z and sign-count
    natural_z = {q: parametric_z(natural_inerts[q]) for q in QS}
    natural_z_sum = sum(natural_z.values())
    natural_stouffer = natural_z_sum / math.sqrt(len(QS))
    natural_stouffer_p_indep = normal_sf(natural_stouffer)
    natural_sign_count = sum(1 for q in QS if natural_inerts[q] > N_PER_Q / 2)

    print(f"\n  Natural per-q parametric one-tailed z:")
    for q in QS:
        print(f"    q={q:>2}: z = {natural_z[q]:.4f}  (inerts = {natural_inerts[q]})")
    print(f"  Sum of z = {natural_z_sum:.4f}")
    print(f"  Stouffer Z_combined = sum / sqrt({len(QS)}) = {natural_stouffer:.4f}")
    print(f"  Stouffer p (one-sided, independent normal) = {natural_stouffer_p_indep:.4f}")
    print(f"  Sign-test count (q with inerts > 500) = {natural_sign_count} of {len(QS)}")
    print(f"  Sign-test p (one-sided, independent binomial) = "
          f"{0.5**len(QS):.4f}")

    # ---- Shuffle null distribution ----
    print(f"\n{'='*72}")
    print(f"Building correlated null: K = {K} shuffles of chi5 over U")
    print(f"{'='*72}")
    sign_counts_null = np.zeros(K, dtype=np.int8)
    stouffer_null = np.zeros(K)
    per_q_inerts_null = {q: np.zeros(K, dtype=np.int32) for q in QS}

    indices_array = {q: indices_per_q[q] for q in QS}

    for trial in range(K):
        rng = np.random.default_rng(trial * 137 + 42)
        chi_shuf = rng.permutation(chi_natural)
        sign_count = 0
        z_sum = 0.0
        for q in QS:
            k = int((chi_shuf[indices_array[q]] == -1).sum())
            per_q_inerts_null[q][trial] = k
            z_sum += parametric_z(k)
            if k > N_PER_Q / 2:
                sign_count += 1
        sign_counts_null[trial] = sign_count
        stouffer_null[trial] = z_sum / math.sqrt(len(QS))

    # ---- Sanity: per-q shuffle mean should be ~500 ----
    print(f"  Per-q shuffle inert-count means (target ~500):")
    for q in QS:
        m = float(per_q_inerts_null[q].mean())
        s = float(per_q_inerts_null[q].std(ddof=1))
        print(f"    q={q:>2}: mean = {m:.2f}, std = {s:.2f}")

    # ---- Empirical null distributions ----
    print(f"\n  Sign-test count distribution (out of K = {K}):")
    for c in range(len(QS) + 1):
        n = int((sign_counts_null == c).sum())
        print(f"    sign-count = {c}: {n} ({n/K*100:.1f}%)")

    p_sign_correlated = float((sign_counts_null >= natural_sign_count).sum()) / K
    print(f"\n  Empirical p(sign >= {natural_sign_count} | shuffle) = "
          f"{p_sign_correlated:.4f} ({int(p_sign_correlated * K)}/{K})")
    print(f"  v3.13 reported sign-test p (independent) = {0.5**len(QS):.4f}")

    # Stouffer percentiles
    quantiles = (0.05, 0.50, 0.95, 0.99)
    pct = {q: float(np.quantile(stouffer_null, q)) for q in quantiles}
    print(f"\n  Stouffer Z_combined null distribution percentiles:")
    print(f"    5th  = {pct[0.05]:.3f}")
    print(f"    50th = {pct[0.50]:.3f}")
    print(f"    95th = {pct[0.95]:.3f}")
    print(f"    99th = {pct[0.99]:.3f}")
    print(f"    max  = {float(stouffer_null.max()):.3f}")

    p_stouffer_correlated = float((stouffer_null >= natural_stouffer).sum()) / K
    print(f"\n  Natural Stouffer Z = {natural_stouffer:.4f}")
    print(f"  Empirical p(Z_combined >= natural | shuffle) = "
          f"{p_stouffer_correlated:.4f} ({int(p_stouffer_correlated * K)}/{K})")
    print(f"  v3.13 reported Stouffer p (independent normal) = "
          f"{natural_stouffer_p_indep:.4f}")

    # ---- Verdict ----
    print(f"\n{'='*72}")
    print("Brief scenario classification (Stouffer)")
    print(f"{'='*72}")
    p_corr = p_stouffer_correlated
    if p_corr < 0.05:
        verdict = ("(c) UNEXPECTED. Corrected p < 0.05 — dependence is "
                   "amplifying rather than protective. Report as such.")
    elif p_corr <= 0.15:
        verdict = ("(a) Corrected joint p in suggestive range [0.05, 0.15]. "
                   "§6.4 Test framing largely stands; v3.14 reports the "
                   "corrected p alongside the dependence note.")
    elif p_corr <= 0.20:
        verdict = ("(a/b boundary) Corrected p in (0.15, 0.20]. Suggestive but "
                   "soft; consider both framings.")
    else:
        verdict = ("(b) WEAKENED. Corrected p > 0.20. Direction-confirmation "
                   "claim weakens; reframe §6.4 as 'directionally consistent "
                   "across four nested moduli; corrected joint significance "
                   "is suggestive but not confirmed.'")
    print(f"  Empirical Stouffer p (correlated) = {p_corr:.4f}")
    print(f"  v3.13 (independence-assumed) p     = "
          f"{natural_stouffer_p_indep:.4f}")
    print(f"  Direction of correction: "
          f"{'p decreased' if p_corr < natural_stouffer_p_indep else 'p increased' if p_corr > natural_stouffer_p_indep else 'p unchanged'} "
          f"under correlated null")
    print(f"\n  -> {verdict}")

    # ---- Save CSVs ----
    summary_path = os.path.join(RESULTS_DIR, 'v3_14_task1_summary.csv')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['metric', 'natural', 'p_independent', 'p_correlated_empirical'])
        w.writerow(['sign_test_count', natural_sign_count,
                    f"{0.5**len(QS):.6f}", f"{p_sign_correlated:.6f}"])
        w.writerow(['stouffer_Z', f"{natural_stouffer:.6f}",
                    f"{natural_stouffer_p_indep:.6f}",
                    f"{p_stouffer_correlated:.6f}"])
    print(f"\n  Saved: {summary_path}")

    perq_path = os.path.join(RESULTS_DIR, 'v3_14_task1_per_q_natural.csv')
    with open(perq_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['q', 'n', 'natural_inerts', 'parametric_z', 'one_tail_p'])
        for q in QS:
            z = natural_z[q]
            w.writerow([q, N_PER_Q, natural_inerts[q],
                        f"{z:.6f}", f"{normal_sf(z):.6f}"])
    print(f"  Saved: {perq_path}")

    null_path = os.path.join(RESULTS_DIR, 'v3_14_task1_null_distribution.csv')
    with open(null_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['trial', 'sign_count', 'stouffer_Z'] +
                   [f'inerts_q{q}' for q in QS])
        for i in range(K):
            w.writerow([i, int(sign_counts_null[i]),
                        f"{stouffer_null[i]:.6f}"] +
                       [int(per_q_inerts_null[q][i]) for q in QS])
    print(f"  Saved: {null_path}")

    # ---- Plot ----
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [warning] matplotlib unavailable; skipping plot")
        return

    fig, ax = plt.subplots(figsize=(9, 5.5))
    z_min, z_max = float(stouffer_null.min()), float(stouffer_null.max())
    bins = np.linspace(min(z_min, -3) - 0.1, max(z_max, natural_stouffer) + 0.1, 50)
    ax.hist(stouffer_null, bins=bins, color='#4c72b0', alpha=0.85,
            edgecolor='black', linewidth=0.4,
            label=f'Correlated null (K = {K} shuffles)')
    ax.axvline(natural_stouffer, color='red', linestyle='--', linewidth=1.7,
               label=f'natural Z = {natural_stouffer:.3f} '
                     f'(empirical p = {p_stouffer_correlated:.4f})')
    ax.axvline(pct[0.95], color='gray', linestyle=':', linewidth=1.3,
               label=f'null 95th pct = {pct[0.95]:.3f}')
    ax.axvline(pct[0.99], color='gray', linestyle='-.', linewidth=1.0, alpha=0.7,
               label=f'null 99th pct = {pct[0.99]:.3f}')
    # Reference: parametric independence-assumed N(0,1)
    z_ref = np.linspace(bins[0], bins[-1], 200)
    pdf_ref = (1 / math.sqrt(2 * math.pi)) * np.exp(-z_ref**2 / 2)
    pdf_scaled = pdf_ref * (bins[1] - bins[0]) * K
    ax.plot(z_ref, pdf_scaled, color='black', linewidth=1.0, alpha=0.55,
            label='N(0,1) (independence prediction)')
    ax.set_xlabel(r'Stouffer combined $Z$ across $q \in \{4, 6, 8, 12\}$')
    ax.set_ylabel(f'Count out of K = {K}')
    ax.set_title('§6.4 Test correlated null distribution\n'
                 'Paper 3 v3.14 Task 1 — chi5 permutation across U')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=8.5)
    fig.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, 'v3_14_task1_correlated_null.png')
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"  Saved: {plot_path}")


if __name__ == '__main__':
    main()
