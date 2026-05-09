#!/usr/bin/env python3
"""Task 1 (Paper 3 v3.13): §6.4 accumulation simulation.

Tests whether the small per-prime inert bias measured in v3.12 §6.4 (~1%
chi5=-1 excess among p ≡ 1 mod q for various q) can plausibly accumulate
over N≈5000 steps to produce the observed S_7(5000)=2 ties (vs random-walk
expectation ~56.4) reported in §8.4.

Method. Simulate biased ±1 random walks. Each step is +1 with probability
(1+μ)/2 and −1 with probability (1−μ)/2, so E[step] = μ. Negative μ means
inert excess. For each μ ∈ {-0.01, -0.015, -0.02, -0.025, -0.03}, generate
K = 10,000 walks of N = 5000 steps and count zero crossings (positions
where the running sum equals 0).

The 7-series has no ramified prime (no chi5(p)=0), so this is a clean ±1
walk and the simulation directly applies. K = 10,000 trials gives
P(ties ≤ 2) precision to ~1 / sqrt(K * P) which is fine down to P ~ 0.001.

Verification gate. K = 1000 unbiased trials must reproduce mean tie count
within ~3 standard errors of √(2N/π) ≈ 56.42. Halt if not.

Reproducibility. Numpy seed = 20260509 (today's date). Each μ uses an
offset of this seed for independent draws.
"""
import numpy as np
import math
import os
import sys
import csv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

NUMPY_SEED = 20260509  # 2026-05-09
N_STEPS = 5000
K_MAIN = 10_000
K_VERIFY = 1_000
MUS = [-0.01, -0.015, -0.02, -0.025, -0.03]
OBSERVED_TIES_7SERIES = 2  # §8.4 observation: S_7(5000) = 2


def simulate_walks(mu, K, N, seed):
    """Vectorised: K independent biased ±1 walks of N steps each.

    Returns array of length K with the zero-crossing count of each walk.
    """
    rng = np.random.default_rng(seed)
    p_plus = (1 + mu) / 2
    # Each step: +1 with prob p_plus, else -1
    steps = np.where(rng.random((K, N)) < p_plus, 1, -1).astype(np.int32)
    cumsums = np.cumsum(steps, axis=1)
    return (cumsums == 0).sum(axis=1)


def quantiles(arr, qs=(0.05, 0.25, 0.50, 0.75, 0.95)):
    return {q: float(np.quantile(arr, q)) for q in qs}


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    expected_unbiased = math.sqrt(2 * N_STEPS / math.pi)
    print(f"N = {N_STEPS}, K_main = {K_MAIN}, K_verify = {K_VERIFY}")
    print(f"Random-walk expected mean tie count = sqrt(2N/pi) = {expected_unbiased:.3f}")
    print(f"Numpy seed = {NUMPY_SEED}\n")

    # ---- Verification gate ----
    print("="*70)
    print("Verification gate: mu = 0, K = 1000 unbiased walks")
    print("="*70)
    ties_unb = simulate_walks(0.0, K_VERIFY, N_STEPS, NUMPY_SEED)
    mean_unb = ties_unb.mean()
    std_unb = ties_unb.std(ddof=1)
    se_unb = std_unb / math.sqrt(K_VERIFY)
    diff = mean_unb - expected_unbiased
    n_se = abs(diff) / se_unb
    print(f"  Observed mean = {mean_unb:.3f} (std = {std_unb:.3f}, SE = {se_unb:.3f})")
    print(f"  Expected      = {expected_unbiased:.3f}")
    print(f"  Difference    = {diff:+.3f} ({n_se:.2f} SE)")
    if n_se > 3:
        print("  HALT: discrepancy > 3 SE.")
        sys.exit(1)
    print("  OK: anchor reproduces.\n")

    # ---- Main sweep ----
    print("="*70)
    print(f"Main sweep: K = {K_MAIN} walks per mu, {len(MUS)} mu values")
    print("="*70)
    rows = []
    all_ties = {}
    for i, mu in enumerate(MUS):
        seed = NUMPY_SEED + (i + 1) * 1000003  # large prime offset, distinct per mu
        ties = simulate_walks(mu, K_MAIN, N_STEPS, seed)
        all_ties[mu] = ties
        mean = float(ties.mean())
        std = float(ties.std(ddof=1))
        qs = quantiles(ties)
        p_le_2 = float((ties <= OBSERVED_TIES_7SERIES).mean())
        p_le_5 = float((ties <= 5).mean())
        p_le_10 = float((ties <= 10).mean())
        rows.append({
            'mu': mu,
            'inert_fraction': (1 - mu) / 2,
            'K': K_MAIN,
            'mean': mean, 'std': std,
            'q05': qs[0.05], 'q25': qs[0.25], 'q50': qs[0.50],
            'q75': qs[0.75], 'q95': qs[0.95],
            'P_le_2': p_le_2, 'P_le_5': p_le_5, 'P_le_10': p_le_10,
            'min': int(ties.min()), 'max': int(ties.max()),
        })
        print(f"\n  mu = {mu:+.3f} (inert frac {(1-mu)/2*100:.2f}%)")
        print(f"    mean = {mean:.2f},  std = {std:.2f}")
        print(f"    quantiles 5/25/50/75/95 = "
              f"{qs[0.05]:.0f} / {qs[0.25]:.0f} / {qs[0.50]:.0f} / "
              f"{qs[0.75]:.0f} / {qs[0.95]:.0f}")
        print(f"    min/max          = {int(ties.min())} / {int(ties.max())}")
        print(f"    P(ties <= 2)     = {p_le_2:.4f}  ({int(p_le_2*K_MAIN)}/{K_MAIN})")
        print(f"    P(ties <= 5)     = {p_le_5:.4f}")
        print(f"    P(ties <= 10)    = {p_le_10:.4f}")

    # ---- Summary table ----
    print(f"\n{'='*70}")
    print(f"Summary: P(ties <= 2 | mu) for each tested mu (vs S_7(5000)=2)")
    print(f"{'='*70}")
    print(f"  {'mu':>7} {'inert%':>8} {'mean':>7} {'std':>7} "
          f"{'P<=2':>9} {'P<=5':>9} {'P<=10':>9}")
    for r in rows:
        print(f"  {r['mu']:>+7.3f} {r['inert_fraction']*100:>7.2f}% "
              f"{r['mean']:>7.2f} {r['std']:>7.2f} "
              f"{r['P_le_2']:>9.4f} {r['P_le_5']:>9.4f} {r['P_le_10']:>9.4f}")

    # ---- Verdict per brief ----
    print(f"\n{'='*70}")
    print("Brief scenario classification")
    print(f"{'='*70}")
    p_max = max(r['P_le_2'] for r in rows)
    p_min = min(r['P_le_2'] for r in rows)
    print(f"  Max P(ties<=2) across mu range = {p_max:.4f}")
    print(f"  Min P(ties<=2) across mu range = {p_min:.4f}")
    if p_max >= 0.05:
        verdict = ("(a) Accumulation claim SUPPORTED. Some mu in range "
                   "produces P(ties<=2) >= 0.05.")
    elif p_max < 0.01:
        verdict = ("(b) Accumulation claim INSUFFICIENT. All tested mu produce "
                   "P(ties<=2) < 0.01. The per-prime bias measured by §6.4 "
                   "Test cannot account for the observed tie deficit alone.")
    else:
        verdict = ("(c) MARGINAL. P(ties<=2) in [0.01, 0.05] across the "
                   "bias range. Reframe §6.4 as 'consistent with accumulation "
                   "at the upper end of the bias range.'")
    print(f"  -> {verdict}")

    # ---- Write CSVs ----
    summary_path = os.path.join(RESULTS_DIR, 'v3_13_task1_accumulation_summary.csv')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        fields = ['mu', 'inert_fraction', 'K', 'mean', 'std',
                  'q05', 'q25', 'q50', 'q75', 'q95',
                  'P_le_2', 'P_le_5', 'P_le_10', 'min', 'max']
        w.writerow(fields)
        for r in rows:
            w.writerow([r[k] if isinstance(r[k], (int, str))
                        else f"{r[k]:.6f}" for k in fields])
    print(f"\n  Saved: {summary_path}")

    # Per-realisation tie counts (one column per mu) — for downstream plotting
    perreal_path = os.path.join(RESULTS_DIR, 'v3_13_task1_per_realisation.csv')
    with open(perreal_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow([f"mu_{mu}" for mu in MUS])
        for k in range(K_MAIN):
            w.writerow([int(all_ties[mu][k]) for mu in MUS])
    print(f"  Saved: {perreal_path}")

    # ---- Plot ----
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [warning] matplotlib unavailable; skipping plot")
        return

    fig, ax = plt.subplots(figsize=(9, 5.5))
    # Common bins so histograms align visually
    max_observed = max(int(all_ties[mu].max()) for mu in MUS)
    bins = np.arange(0, max_observed + 4, 2)
    colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(MUS)))
    for mu, color in zip(MUS, colors):
        ax.hist(all_ties[mu], bins=bins, alpha=0.45, color=color,
                label=f"μ = {mu} (inert {(1-mu)/2*100:.2f}%)",
                histtype='stepfilled', edgecolor='black', linewidth=0.4)
    ax.axvline(OBSERVED_TIES_7SERIES, color='red', linestyle='--', linewidth=1.6,
               label=f'observed: $S_7(5000) = {OBSERVED_TIES_7SERIES}$')
    ax.axvline(expected_unbiased, color='gray', linestyle=':', linewidth=1.4,
               label=fr'unbiased expectation $\sqrt{{2N/\pi}} \approx {expected_unbiased:.1f}$')

    ax.set_xlabel('Zero crossings in N=5000 steps')
    ax.set_ylabel(f'Count out of K={K_MAIN}')
    ax.set_title('Biased ±1 random walk: zero-crossing distribution by per-step bias\n'
                 'Paper 3 v3.13 Task 1 — §6.4 accumulation test')
    ax.legend(loc='upper right', fontsize=8.5)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, 'v3_13_task1_accumulation.png')
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"  Saved: {plot_path}")


if __name__ == '__main__':
    main()
