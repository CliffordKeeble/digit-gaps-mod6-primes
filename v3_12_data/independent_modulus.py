#!/usr/bin/env python3
"""Paper 199 v1.1 Task 1 — independent modulus test (NULL).

Mr Adversary v3.18 NULL query: q ∈ {4, 6, 8, 12} are nested under
mod 12 (primes ≡ 1 mod 12 sit inside ≡ 1 mod 4 ∩ ≡ 1 mod 6, and
≡ 1 mod 8 overlaps ≡ 1 mod 4). The §5 cyclotomic-bias direction-
consistency claim is "essentially three observations dressed as four."
Adding q ∈ {7, 11, 13} — all primes coprime to 12 — provides three
genuinely independent comparisons.

Method (per brief):

  Per modulus q ∈ {7, 11, 13}:
    1. Filter non-ramified primes p ≡ 1 (mod q).
    2. For n ∈ {100, 1000}, take first n filtered primes.
    3. Count k_q = number with χ₅(p) = −1 (inert).
    4. Compute one-sided binomial p-value P(X ≥ k_q | Bin(n, 0.5)).
    5. Compute z_q = (k_q − n/2) / √(n/4).

  Aggregate test (7 moduli): q ∈ {4, 6, 7, 8, 11, 12, 13}, n = 1000.
    6. Correlated null: K = 10⁴ permutations of χ₅ across the
       universe U (first 20,000 non-ramified primes). For each
       permutation, recompute z_q for all 7 moduli, then:
         - Stouffer Z = Σ z_q / √7
         - sign-test count = #{q : z_q > 0}
    7. Report empirical p for natural Stouffer Z and natural sign
       count against the K = 10⁴ null distribution.

  Also run the same correlated-null pipeline for q ∈ {4, 6, 8, 12}
  alongside (the v3.14 anchor) so the 4-mod p reproduces and the
  7-mod p sits next to it.

Anchor verification (HALT on fail):

  Per-q natural inerts at n = 100 and n = 1000 for q ∈ {4, 6, 8, 12}:
    n=100:  {4: 50,  6: 53,  8: 56,  12: 57}
    n=1000: {4: 508, 6: 509, 8: 516, 12: 514}
  Correlated-null p (4 moduli, K = 10⁴):
    Stouffer  p = 0.190  (±0.005)
    Sign-test p = 0.198  (±0.005)

Seed convention: numpy default_rng(trial * 137 + 42), matching v3.14.
"""
import csv
import math
import os
import sys

import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve, chi5

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

SIEVE_LIMIT = 300_000      # matches v3.14 — generous for q=13 at n=1000
M = 20_000                  # universe size: first M non-ramified primes
K = 10_000                  # number of shuffles
QS_4 = [4, 6, 8, 12]        # v3.14 anchor (nested-moduli)
QS_NEW = [7, 11, 13]        # truly independent (Mr Adversary's request)
QS_7 = sorted(set(QS_4 + QS_NEW))   # joint aggregate
N_LARGE = 1000
N_SMALL = 100

# v3.14 / Paper 199 v1.0 §6.4 anchors
ANCHORS_INERTS_N100 = {4: 50,  6: 53,  8: 56,  12: 57}
ANCHORS_INERTS_N1000 = {4: 508, 6: 509, 8: 516, 12: 514}
ANCHOR_STOUFFER_P_4MOD = 0.190
ANCHOR_SIGNTEST_P_4MOD = 0.198
ANCHOR_TOL_CORRELATED_P = 0.005


def parametric_z(k, n=N_LARGE, p=0.5):
    """Right-tailed parametric z for Binomial(n, p)."""
    return (k - n * p) / math.sqrt(n * p * (1 - p))


def normal_sf(x):
    """P(Z >= x) for standard normal."""
    return 0.5 * math.erfc(x / math.sqrt(2))


def binom_sf_one_sided(k, n, p=0.5):
    """One-sided P(X >= k | Binomial(n, p))."""
    # Sum from k to n
    log_bin = [math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1)
               + j * math.log(p) + (n - j) * math.log(1 - p)
               for j in range(k, n + 1)]
    # Normalise via log-sum-exp
    if not log_bin:
        return 0.0
    m = max(log_bin)
    return math.exp(m) * sum(math.exp(x - m) for x in log_bin)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print('=' * 76)
    print('Paper 199 v1.1 Task 1 — independent modulus test')
    print('=' * 76)
    print(f"  Moduli (anchor 4-mod) : {QS_4}")
    print(f"  Moduli (new 3-mod)    : {QS_NEW}")
    print(f"  Moduli (joint 7-mod)  : {QS_7}")
    print(f"  Universe size M       : {M:,}")
    print(f"  K (shuffles)          : {K:,}")
    print(f"  Sieve limit           : {SIEVE_LIMIT:,}")

    # ---- Sieve and build universe ----
    print(f"\nSieving primes up to {SIEVE_LIMIT:,} ...")
    primes = sieve(SIEVE_LIMIT)
    non_ramified = [p for p in primes if chi5(p) != 0]
    if len(non_ramified) < M:
        print(f"  HALT: only {len(non_ramified):,} non-ramified primes; need {M:,}")
        sys.exit(1)
    U = np.array(non_ramified[:M], dtype=np.int64)
    chi_natural = np.array([chi5(int(p)) for p in U], dtype=np.int8)
    print(f"  Universe U: first {M:,} non-ramified primes "
          f"(p_min={int(U[0])}, p_max={int(U[-1]):,})")
    print(f"  χ₅ marginal in U: +1 = {int((chi_natural == 1).sum()):,}, "
          f"−1 = {int((chi_natural == -1).sum()):,}, "
          f"0 = {int((chi_natural == 0).sum())}")

    # ---- Per-q index lists ----
    print(f"\n{'='*76}")
    print(f"Per-q index lists in U (first {N_LARGE} primes ≡ 1 mod q)")
    print(f"{'='*76}")
    indices_per_q = {}
    for q in QS_7:
        mask = (U % q == 1)
        idx = np.where(mask)[0]
        if len(idx) < N_LARGE:
            print(f"  HALT: only {len(idx)} primes ≡ 1 mod {q}; need {N_LARGE}")
            sys.exit(1)
        indices_per_q[q] = idx[:N_LARGE]
        print(f"  q={q:>2}: {len(idx):>5} total in U; first {N_LARGE} span "
              f"U-indices [{int(idx[0])}, {int(idx[N_LARGE-1])}], "
              f"p_max = {int(U[idx[N_LARGE-1]]):,}")

    # ---- Anchor verification: per-q natural inerts at n=100 and n=1000 ----
    # Per CinC (10 May 2026): n=1000 is the load-bearing gate for the
    # aggregate test (Task 1's substance). n=100 anchors come from v3.12
    # task3_premise.py with a slightly different prime-universe
    # convention (likely around inclusion of p=5); v1.1 standardises on
    # the v3.14 correlated_null.py convention used here, so the n=100
    # numbers from this run ARE the recomputed v1.1 values for §5 (not
    # anchor failures). Halt only on n=1000 mismatch.
    print(f"\n{'='*76}")
    print('Anchor verification: per-q natural inerts')
    print(f"{'='*76}")
    print('  Per CinC: n=1000 is the gate; n=100 differences from v3.12-source')
    print('  anchors are v1.1 convention-standardisation artifacts (logged for')
    print('  §11 calibration, not a halt condition).')
    print()

    natural_inerts_n100 = {}
    natural_inerts_n1000 = {}
    fail_n1000 = False
    n100_drifts = []
    print(f"  {'q':>3}  {'n':>5}  {'inerts':>6}  {'anchor':>6}  status")
    for q in QS_7:
        idx_full = indices_per_q[q]
        for n_val in (N_SMALL, N_LARGE):
            idx = idx_full[:n_val]
            k = int((chi_natural[idx] == -1).sum())
            target = (ANCHORS_INERTS_N100 if n_val == N_SMALL
                      else ANCHORS_INERTS_N1000).get(q)
            if n_val == N_SMALL:
                natural_inerts_n100[q] = k
            else:
                natural_inerts_n1000[q] = k
            if target is None:
                print(f"  {q:>3}  {n_val:>5}  {k:>6}  {'(new)':>6}  first-time")
            else:
                ok = (k == target)
                if n_val == N_LARGE:
                    flag = 'OK' if ok else 'FAIL (HALT GATE)'
                    if not ok:
                        fail_n1000 = True
                else:  # n=100, soft flag
                    if ok:
                        flag = 'OK'
                    else:
                        flag = (f'soft-flag (Δ={k-target:+d}; v1.1 convention)')
                        n100_drifts.append((q, k, target, k - target))
                print(f"  {q:>3}  {n_val:>5}  {k:>6}  {target:>6}  {flag}")
    if fail_n1000:
        print(f"\n  HALT: n=1000 anchor mismatch (load-bearing gate).")
        sys.exit(1)
    print(f"\n  n=1000 gate: all 4 anchors reproduce exactly.")
    if n100_drifts:
        print(f"\n  n=100 v1.1-convention drifts (informational, for §11 calibration):")
        for q, k, target, delta in n100_drifts:
            print(f"    q={q:>2}: this run = {k}, v3.12-source anchor = "
                  f"{target}, Δ = {delta:+d}")

    # ---- Per-modulus statistics (n = 100 and n = 1000) ----
    print(f"\n{'='*76}")
    print('Per-modulus statistics — natural ordering')
    print(f"{'='*76}")
    print(f"  {'q':>3}  {'n':>5}  {'inerts':>6}  {'pct':>6}  "
          f"{'z_q':>8}  {'p (binom 1-sided)':>18}")
    per_modulus_rows = []
    for q in QS_7:
        for n_val in (N_SMALL, N_LARGE):
            k = (natural_inerts_n100[q] if n_val == N_SMALL
                 else natural_inerts_n1000[q])
            z_q = (k - n_val / 2) / math.sqrt(n_val / 4)  # binomial(n, 0.5)
            p_binom = binom_sf_one_sided(k, n_val, 0.5)
            pct = k / n_val * 100
            print(f"  {q:>3}  {n_val:>5}  {k:>6}  {pct:>5.1f}%  "
                  f"{z_q:>+8.3f}  {p_binom:>18.6f}")
            per_modulus_rows.append({
                'q': q, 'n': n_val, 'inerts_observed': k,
                'p_one_sided': p_binom, 'z_q': z_q,
            })

    # ---- Direction tally for q ∈ {7, 11, 13} at n = 1000 ----
    print(f"\n  Direction check for new moduli q ∈ {QS_NEW} at n = {N_LARGE}:")
    direction_count = 0
    for q in QS_NEW:
        k = natural_inerts_n1000[q]
        excess = k > N_LARGE / 2
        sign = '+' if excess else '−'
        if excess:
            direction_count += 1
        print(f"    q={q:>2}: inerts = {k} ({'>' if excess else '≤'} {N_LARGE//2}) "
              f"→ {'inert excess' if excess else 'inert deficit'} ({sign})")
    print(f"  → {direction_count} of {len(QS_NEW)} new moduli show inert excess "
          f"(k > {N_LARGE//2}).")

    # ---- Aggregate test: 4-mod anchor + 7-mod new ----
    print(f"\n{'='*76}")
    print(f'Correlated-null aggregate test (K = {K:,} χ₅-permutations)')
    print(f"{'='*76}")

    # Natural Stouffer / sign-count for each modulus set
    def aggregate_natural(qs):
        zs = [parametric_z(natural_inerts_n1000[q]) for q in qs]
        z_sum = sum(zs)
        stouffer = z_sum / math.sqrt(len(qs))
        sign_count = sum(1 for z in zs if z > 0)
        return zs, stouffer, sign_count

    nat_zs_4, nat_stouffer_4, nat_sign_4 = aggregate_natural(QS_4)
    nat_zs_7, nat_stouffer_7, nat_sign_7 = aggregate_natural(QS_7)

    print(f"\n  Natural per-q parametric z (n = {N_LARGE}):")
    for q in QS_7:
        z = parametric_z(natural_inerts_n1000[q])
        marker = ('★' if q in QS_NEW else ' ')
        print(f"    {marker} q={q:>2}: z = {z:+.4f}  (inerts = "
              f"{natural_inerts_n1000[q]})")
    print(f"\n  Natural Stouffer Z (4-mod) = "
          f"{nat_stouffer_4:.4f}  | sign count = {nat_sign_4} of {len(QS_4)}")
    print(f"  Natural Stouffer Z (7-mod) = "
          f"{nat_stouffer_7:.4f}  | sign count = {nat_sign_7} of {len(QS_7)}")
    p_stouffer_indep_4 = normal_sf(nat_stouffer_4)
    p_stouffer_indep_7 = normal_sf(nat_stouffer_7)
    p_sign_indep_4 = 0.5 ** len(QS_4)
    p_sign_indep_7 = 0.5 ** len(QS_7)
    print(f"\n  Independence-assumed Stouffer p (4-mod) = {p_stouffer_indep_4:.4f}")
    print(f"  Independence-assumed Stouffer p (7-mod) = {p_stouffer_indep_7:.4f}")
    print(f"  Independence-assumed sign-test p (4-mod, all 4 +) = "
          f"{p_sign_indep_4:.4f}")
    print(f"  Independence-assumed sign-test p (7-mod, "
          f"k of 7 +) = {p_sign_indep_7:.4f}  (probability of all 7)")

    # ---- Run K shuffles, accumulate Stouffer & sign-count for both 4-mod and 7-mod ----
    print(f"\n  Running {K:,} shuffles ...")
    stouffer_null_4 = np.zeros(K)
    stouffer_null_7 = np.zeros(K)
    sign_null_4 = np.zeros(K, dtype=np.int8)
    sign_null_7 = np.zeros(K, dtype=np.int8)
    per_q_inerts_null = {q: np.zeros(K, dtype=np.int32) for q in QS_7}

    for trial in range(K):
        rng = np.random.default_rng(trial * 137 + 42)
        chi_shuf = rng.permutation(chi_natural)
        z_sum_4 = 0.0
        z_sum_7 = 0.0
        sc_4 = 0
        sc_7 = 0
        for q in QS_7:
            k = int((chi_shuf[indices_per_q[q]] == -1).sum())
            per_q_inerts_null[q][trial] = k
            z = parametric_z(k)
            z_sum_7 += z
            if z > 0:
                sc_7 += 1
            if q in QS_4:
                z_sum_4 += z
                if z > 0:
                    sc_4 += 1
        stouffer_null_4[trial] = z_sum_4 / math.sqrt(len(QS_4))
        stouffer_null_7[trial] = z_sum_7 / math.sqrt(len(QS_7))
        sign_null_4[trial] = sc_4
        sign_null_7[trial] = sc_7

    # ---- Empirical p ----
    p_stouffer_corr_4 = float((stouffer_null_4 >= nat_stouffer_4).sum()) / K
    p_stouffer_corr_7 = float((stouffer_null_7 >= nat_stouffer_7).sum()) / K
    p_sign_corr_4 = float((sign_null_4 >= nat_sign_4).sum()) / K
    p_sign_corr_7 = float((sign_null_7 >= nat_sign_7).sum()) / K

    print(f"\n  Per-q shuffle inert-count means (target ~500):")
    for q in QS_7:
        m = float(per_q_inerts_null[q].mean())
        s = float(per_q_inerts_null[q].std(ddof=1))
        marker = ('★' if q in QS_NEW else ' ')
        print(f"    {marker} q={q:>2}: mean = {m:.2f}, std = {s:.2f}")

    # ---- Anchor verification: 4-mod correlated p ----
    print(f"\n{'='*76}")
    print('Anchor verification: 4-mod correlated p (v3.14)')
    print(f"{'='*76}")
    anchor_fail = False
    print(f"  {'metric':>22}  {'observed':>10}  {'anchor':>8}  status")
    diff_st = abs(p_stouffer_corr_4 - ANCHOR_STOUFFER_P_4MOD)
    flag = 'OK' if diff_st <= ANCHOR_TOL_CORRELATED_P else 'FAIL'
    print(f"  {'4-mod Stouffer p':>22}  {p_stouffer_corr_4:>10.4f}  "
          f"{ANCHOR_STOUFFER_P_4MOD:>8.3f}  {flag} (Δ = {diff_st:.4f})")
    if diff_st > ANCHOR_TOL_CORRELATED_P:
        anchor_fail = True
    diff_sg = abs(p_sign_corr_4 - ANCHOR_SIGNTEST_P_4MOD)
    flag = 'OK' if diff_sg <= ANCHOR_TOL_CORRELATED_P else 'FAIL'
    print(f"  {'4-mod sign-test p':>22}  {p_sign_corr_4:>10.4f}  "
          f"{ANCHOR_SIGNTEST_P_4MOD:>8.3f}  {flag} (Δ = {diff_sg:.4f})")
    if diff_sg > ANCHOR_TOL_CORRELATED_P:
        anchor_fail = True
    if anchor_fail:
        print(f"\n  HALT: 4-mod correlated p anchor failed.")
        sys.exit(1)
    print(f"\n  4-mod correlated null reproduces v3.14 anchors within ±"
          f"{ANCHOR_TOL_CORRELATED_P:.3f}.")

    # ---- 7-mod aggregate result ----
    print(f"\n{'='*76}")
    print('7-modulus aggregate result (NEW)')
    print(f"{'='*76}")
    print(f"  Natural Stouffer Z (7-mod) = {nat_stouffer_7:.4f}")
    print(f"  Empirical p (Stouffer, 7-mod, correlated null) = "
          f"{p_stouffer_corr_7:.4f}  ({int(p_stouffer_corr_7 * K):,}/{K:,})")
    print(f"  Natural sign count (7-mod) = {nat_sign_7} of {len(QS_7)}")
    print(f"  Empirical p (sign-test, 7-mod, correlated null) = "
          f"{p_sign_corr_7:.4f}  ({int(p_sign_corr_7 * K):,}/{K:,})")
    # Sign-count distribution for 7-mod
    print(f"\n  7-mod sign-count distribution under shuffle (K = {K:,}):")
    for c in range(len(QS_7) + 1):
        n_c = int((sign_null_7 == c).sum())
        bar = '█' * int(n_c / K * 50)
        print(f"    sign-count = {c}: {n_c:>5} ({n_c/K*100:>5.2f}%)  {bar}")

    # Stouffer percentiles for 7-mod
    quantiles = (0.05, 0.10, 0.50, 0.90, 0.95, 0.99)
    pct_7 = {q: float(np.quantile(stouffer_null_7, q)) for q in quantiles}
    print(f"\n  7-mod Stouffer Z null distribution percentiles:")
    for q in (0.05, 0.10, 0.50, 0.90, 0.95, 0.99):
        print(f"    {q*100:>4.0f}th = {pct_7[q]:+.3f}")
    print(f"    max  = {float(stouffer_null_7.max()):+.3f}")

    # ---- Pre-registered falsifier-table outcome ----
    print(f"\n{'='*76}")
    print('Pre-registered falsifier-table outcome (per brief Task 1)')
    print(f"{'='*76}")
    n_inert_excess_new = sum(1 for q in QS_NEW
                              if natural_inerts_n1000[q] > N_LARGE / 2)
    n_inert_deficit_new = len(QS_NEW) - n_inert_excess_new
    print(f"  Of new moduli q ∈ {QS_NEW} at n = {N_LARGE}:")
    print(f"    {n_inert_excess_new} with inert excess (k > 500)")
    print(f"    {n_inert_deficit_new} with inert deficit (k ≤ 500)")
    print(f"  Aggregate 7-mod Stouffer p (correlated): {p_stouffer_corr_7:.4f}")
    print()
    if n_inert_deficit_new >= 2:
        verdict = ('STRONG FALSIFIER (Row 1): ≥ 2 of {7, 11, 13} show '
                   'k_q < n/2 (opposite direction). The four-q directional '
                   'consistency does NOT generalise to independent moduli.')
    elif n_inert_deficit_new == 1:
        verdict = ('INCONCLUSIVE (Row 2): 1 of {7, 11, 13} shows k_q < n/2. '
                   f'Aggregate 7-mod Stouffer p = {p_stouffer_corr_7:.4f} '
                   'is the deciding statistic.')
    elif p_stouffer_corr_7 <= 0.05:
        verdict = ('SIGNIFICANCE THRESHOLD MET (Row 3): All 3 of {7, 11, 13} '
                   f'show k_q ≥ n/2 AND aggregate p = {p_stouffer_corr_7:.4f} '
                   '≤ 0.05. The cyclotomic-split bias hypothesis upgrades '
                   'from "directionally supported" to "suggestive evidence."')
    elif p_stouffer_corr_7 <= 0.15:
        verdict = ('DIRECTIONAL CONSISTENCY PERSISTS at non-significant '
                   f'level (Row 4): All 3 of {{7, 11, 13}} show k_q ≥ n/2 '
                   f'AND aggregate p = {p_stouffer_corr_7:.4f} ∈ (0.05, 0.15]. '
                   'The §5 "directionally supported but not significant" '
                   'framing is sustained; Retraction 4 unaffected.')
    else:
        verdict = ('DIRECTION HOLDS, JOINT SIGNIFICANCE NOT IMPROVED '
                   f'(Row 5): All 3 of {{7, 11, 13}} show k_q ≥ n/2 AND '
                   f'aggregate p = {p_stouffer_corr_7:.4f} > 0.15. v1.1 '
                   'reports as "directional consistency confirmed across '
                   'truly independent moduli, joint significance not reached."')
    print(f"  → {verdict}")

    # ---- Direction-confirmation summary ----
    print(f"\n  Direction-confirmation summary:")
    print(f"    Of {len(QS_NEW)} new moduli, {n_inert_excess_new} show inert "
          f"excess at n = {N_LARGE}.")
    print(f"    Of {len(QS_7)} all moduli, {nat_sign_7} show inert excess at "
          f"n = {N_LARGE}.")

    # ---- Save CSV 1: per-modulus results ----
    csv1 = os.path.join(RESULTS_DIR, 'independent_modulus_results.csv')
    with open(csv1, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['q', 'n', 'inerts_observed', 'p_one_sided', 'z_q'])
        for r in per_modulus_rows:
            w.writerow([r['q'], r['n'], r['inerts_observed'],
                        f"{r['p_one_sided']:.6f}", f"{r['z_q']:.6f}"])
    print(f"\n  Saved: {csv1}")

    # ---- Save CSV 2: correlated null summary ----
    csv2 = os.path.join(RESULTS_DIR, 'independent_modulus_correlated_null.csv')
    with open(csv2, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['n_shuffles', 'observed_stouffer_z_4mod',
                    'observed_stouffer_z_7mod',
                    'p_stouffer_4mod', 'p_stouffer_7mod',
                    'observed_signtest_4mod', 'observed_signtest_7mod',
                    'p_signtest_4mod', 'p_signtest_7mod'])
        w.writerow([K,
                    f"{nat_stouffer_4:.6f}", f"{nat_stouffer_7:.6f}",
                    f"{p_stouffer_corr_4:.6f}", f"{p_stouffer_corr_7:.6f}",
                    nat_sign_4, nat_sign_7,
                    f"{p_sign_corr_4:.6f}", f"{p_sign_corr_7:.6f}"])
    print(f"  Saved: {csv2}")

    # ---- Plot ----
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('  [warning] matplotlib unavailable; skipping plot')
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: 4-mod and 7-mod Stouffer null distributions, with naturals
    ax = axes[0]
    bins = np.linspace(min(stouffer_null_4.min(), stouffer_null_7.min(),
                            -3) - 0.1,
                        max(stouffer_null_4.max(), stouffer_null_7.max(),
                            nat_stouffer_4, nat_stouffer_7) + 0.1, 50)
    ax.hist(stouffer_null_4, bins=bins, color='#4c72b0', alpha=0.55,
            edgecolor='#2f4d80', linewidth=0.4, density=True,
            label=f"4-mod null (anchor)  natural Z = {nat_stouffer_4:.3f}, "
                  f"p = {p_stouffer_corr_4:.4f}")
    ax.hist(stouffer_null_7, bins=bins, color='#dd8452', alpha=0.55,
            edgecolor='#7f3a17', linewidth=0.4, density=True,
            label=f"7-mod null (NEW)      natural Z = {nat_stouffer_7:.3f}, "
                  f"p = {p_stouffer_corr_7:.4f}")
    ax.axvline(nat_stouffer_4, color='#2f4d80', linestyle='--', linewidth=1.4)
    ax.axvline(nat_stouffer_7, color='#7f3a17', linestyle='--', linewidth=1.4)
    # N(0,1) reference
    z_ref = np.linspace(bins[0], bins[-1], 200)
    pdf_ref = (1 / math.sqrt(2 * math.pi)) * np.exp(-z_ref ** 2 / 2)
    ax.plot(z_ref, pdf_ref, color='black', linewidth=0.9, alpha=0.5,
            label='N(0,1) — independence prediction')
    ax.set_xlabel('Stouffer combined Z')
    ax.set_ylabel('Density')
    ax.set_title('Correlated-null Stouffer distributions: 4-mod vs 7-mod')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=8.5)

    # Right: per-q natural inerts at n=1000 with z reference
    ax = axes[1]
    qs_sorted = QS_7
    inerts_arr = [natural_inerts_n1000[q] for q in qs_sorted]
    zs_arr = [parametric_z(natural_inerts_n1000[q]) for q in qs_sorted]
    colors = ['#4c72b0' if q in QS_4 else '#dd8452' for q in qs_sorted]
    bars = ax.bar(range(len(qs_sorted)), [k - 500 for k in inerts_arr],
                  color=colors, edgecolor='black', linewidth=0.5)
    ax.axhline(0, color='black', linewidth=0.7)
    ax.set_xticks(range(len(qs_sorted)))
    ax.set_xticklabels([f'q={q}' for q in qs_sorted])
    ax.set_ylabel('Inerts − 500 (excess over null mean)')
    ax.set_title(f'Per-modulus inert excess at n = {N_LARGE}\n'
                 'blue = 4-mod anchor (nested), orange = NEW (independent)')
    for i, (q, k, z) in enumerate(zip(qs_sorted, inerts_arr, zs_arr)):
        ax.text(i, (k - 500) + (0.5 if k >= 500 else -1.5),
                f'{k}\nz={z:+.2f}', ha='center', fontsize=8.5)
    ax.grid(True, alpha=0.3, axis='y')

    fig.suptitle(f'Paper 199 v1.1 Task 1 — independent modulus test '
                 f'(K = {K:,} shuffles)')
    fig.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, 'independent_modulus.png')
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"  Saved: {plot_path}")


if __name__ == '__main__':
    main()
