#!/usr/bin/env python3
"""Paper 3 v3.16 single task: α-robustness on the §6.5.1 power-law fit.

v3.15 §6.5.1 reports α = 0.21 ± 0.08 (Def C; α = 0.20 ± 0.08 Def A) over
six windows n ∈ {100, 200, 300, 500, 750, 1000}. Mr Adversary's GAP/NULL
item: the parametric ± 0.08 assumes i.i.d. residuals, but the trajectory
z = (3.08, 3.80, 3.38, 3.37, 4.64, 5.57) is non-monotone with localised
acceleration near n = 750; residuals are visibly structured. He also
asks for the sub-set fit on the first four windows alongside the full
fit so the reader can judge whether α ≈ 0.21 is a stable feature or an
emergent feature of large n.

Three robustness calculations on the existing six (n, z) data points,
both definitions:

  Part A — Bootstrap CI. Resample the six (n_i, log z_i) pairs with
           replacement, K = 10,000 trials, refit each. Report mean,
           median, std, 95% CI, 90% CI.

  Part B — Leave-one-out. Refit using the remaining five for each of
           the six windows. Report (window-removed, α, SE) tuples and
           the range/std of α across LOO samples.

  Part C — Sub-set fits. First four (100..500), last three (500..1000),
           last four (300..1000). Plus the full six for comparison.

Verification gate: reproduce v3.15 parametric α = 0.21 ± 0.08 (Def C)
from the loaded (n, z) pairs before running bootstrap. Halt if off.

Reads existing six-window data from results/v3_15_task1_growth_rate.csv.
Writes results/v3_16_alpha_*.csv and results/v3_16_alpha_robustness.png.
"""
import csv
import math
import os
import random
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from growth_rate import linear_fit  # reuse v3.15 OLS implementation

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
INPUT_CSV = os.path.join(RESULTS_DIR, 'v3_15_task1_growth_rate.csv')

K_BOOTSTRAP = 10_000
SEED_BASE = 42  # default_rng(trial * 137 + 42) convention; trial=0 here
ANCHOR_ALPHA_C = 0.21
ANCHOR_SE_C = 0.08
ANCHOR_TOL = 0.01  # parametric fit is deterministic; require tight match


def load_six_windows():
    """Load the six (n, z) pairs per definition from the v3.15 CSV."""
    by_def = {'A': [], 'C': []}
    with open(INPUT_CSV, newline='') as f:
        for r in csv.DictReader(f):
            by_def[r['definition']].append((int(r['n']), float(r['z'])))
    for d in by_def:
        by_def[d].sort()
    return by_def


def parametric_fit(points):
    """OLS fit log10(z) = α log10(n) + β over the supplied (n, z) pairs."""
    log_n = [math.log10(n) for n, _ in points]
    log_z = [math.log10(z) for _, z in points]
    return linear_fit(log_n, log_z)


def bootstrap_alpha(points, k, seed):
    """Resample the six (log n, log z) pairs with replacement, k trials."""
    rng = random.Random(seed)
    L = len(points)
    log_n = [math.log10(n) for n, _ in points]
    log_z = [math.log10(z) for _, z in points]
    alphas = []
    degenerate = 0
    for _ in range(k):
        idx = [rng.randrange(L) for _ in range(L)]
        xs = [log_n[i] for i in idx]
        ys = [log_z[i] for i in idx]
        # Degenerate sample: all draws identical or x-variance zero.
        if len(set(xs)) < 2:
            degenerate += 1
            continue
        fit = linear_fit(xs, ys)
        if fit is None:
            degenerate += 1
            continue
        alphas.append(fit['slope'])
    alphas.sort()
    return alphas, degenerate


def percentile(sorted_xs, q):
    """Linear-interpolation percentile (numpy default behaviour)."""
    if not sorted_xs:
        return float('nan')
    if len(sorted_xs) == 1:
        return sorted_xs[0]
    pos = q / 100.0 * (len(sorted_xs) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_xs[lo]
    frac = pos - lo
    return sorted_xs[lo] * (1 - frac) + sorted_xs[hi] * frac


def summarise_bootstrap(alphas):
    n = len(alphas)
    mean = sum(alphas) / n
    var = sum((a - mean) ** 2 for a in alphas) / (n - 1)
    std = math.sqrt(var)
    return {
        'n': n,
        'mean': mean,
        'median': percentile(alphas, 50),
        'std': std,
        'ci95_lo': percentile(alphas, 2.5),
        'ci95_hi': percentile(alphas, 97.5),
        'ci90_lo': percentile(alphas, 5.0),
        'ci90_hi': percentile(alphas, 95.0),
    }


def leave_one_out(points):
    out = []
    for i, (n_drop, _) in enumerate(points):
        kept = points[:i] + points[i + 1:]
        fit = parametric_fit(kept)
        out.append({'window_removed': n_drop, 'alpha': fit['slope'],
                    'se': fit['se_slope'], 'r2': fit['r2']})
    return out


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    by_def = load_six_windows()

    # ---- Verification gate (Def C) ----
    full_c = parametric_fit(by_def['C'])
    print('=' * 76)
    print('Verification gate: reproduce v3.15 Def C parametric fit')
    print('=' * 76)
    print(f"  Loaded six (n, z) for Def C: "
          + ', '.join(f"({n}, {z:.2f})" for n, z in by_def['C']))
    print(f"  α (this run)   = {full_c['slope']:.4f}")
    print(f"  SE α           = {full_c['se_slope']:.4f}")
    print(f"  v3.15 anchor   = {ANCHOR_ALPHA_C} ± {ANCHOR_SE_C}")
    if (abs(full_c['slope'] - ANCHOR_ALPHA_C) > ANCHOR_TOL
            or abs(full_c['se_slope'] - ANCHOR_SE_C) > ANCHOR_TOL):
        print('  HALT: v3.15 anchor mismatch beyond ±{:.2f}.'.format(ANCHOR_TOL))
        sys.exit(1)
    print('  Anchor OK.')

    # Both definitions reported in parallel.
    full_a = parametric_fit(by_def['A'])
    print(f"\n  Def A (for completeness): α = {full_a['slope']:.4f} "
          f"± {full_a['se_slope']:.4f}")

    summary_rows = []  # for the single-page summary CSV
    boot_summary = {}
    loo_summary = {}
    subset_summary = {}

    for def_label in ('C', 'A'):
        pts = by_def[def_label]
        full = parametric_fit(pts)
        print(f"\n{'=' * 76}")
        print(f"Definition {def_label}: full six-window parametric fit")
        print('=' * 76)
        print(f"  α = {full['slope']:.4f} ± {full['se_slope']:.4f}  "
              f"(R² = {full['r2']:.3f}, df = {full['df']})")

        # ---- Part A: Bootstrap ----
        print(f"\n--- Part A: Bootstrap CI (K = {K_BOOTSTRAP:,}) ---")
        seed = SEED_BASE + (1 if def_label == 'A' else 0)
        alphas, degen = bootstrap_alpha(pts, K_BOOTSTRAP, seed)
        boot = summarise_bootstrap(alphas)
        boot_summary[def_label] = boot
        if degen:
            print(f"  Degenerate samples (constant x): {degen} of {K_BOOTSTRAP}")
        print(f"  Usable resamples : {boot['n']:,}")
        print(f"  α mean           = {boot['mean']:+.4f}")
        print(f"  α median         = {boot['median']:+.4f}")
        print(f"  α std            = {boot['std']:.4f}")
        print(f"  95% CI [2.5, 97.5] = [{boot['ci95_lo']:+.4f}, "
              f"{boot['ci95_hi']:+.4f}]  (width {boot['ci95_hi']-boot['ci95_lo']:.4f})")
        print(f"  90% CI [5.0, 95.0] = [{boot['ci90_lo']:+.4f}, "
              f"{boot['ci90_hi']:+.4f}]  (width {boot['ci90_hi']-boot['ci90_lo']:.4f})")
        parametric_ci_lo = full['slope'] - 1.96 * full['se_slope']
        parametric_ci_hi = full['slope'] + 1.96 * full['se_slope']
        print(f"  Parametric 95% CI ≈ [{parametric_ci_lo:+.4f}, "
              f"{parametric_ci_hi:+.4f}]  (width {parametric_ci_hi-parametric_ci_lo:.4f})")

        # ---- Part B: LOO ----
        print(f"\n--- Part B: Leave-one-out (six fits) ---")
        loo = leave_one_out(pts)
        loo_summary[def_label] = loo
        loo_alphas = [r['alpha'] for r in loo]
        loo_min, loo_max = min(loo_alphas), max(loo_alphas)
        loo_mean = sum(loo_alphas) / len(loo_alphas)
        loo_std = math.sqrt(sum((a - loo_mean) ** 2 for a in loo_alphas)
                            / (len(loo_alphas) - 1))
        print(f"  {'window_removed':>15}  {'α':>8}  {'SE α':>8}  {'Δ from full':>11}")
        for r in loo:
            delta = r['alpha'] - full['slope']
            print(f"  {r['window_removed']:>15}  {r['alpha']:>+8.4f}  "
                  f"{r['se']:>8.4f}  {delta:>+11.4f}")
        print(f"  range α (max - min) = {loo_max - loo_min:.4f}  "
              f"[{loo_min:+.4f}, {loo_max:+.4f}]")
        print(f"  std α (across 6 LOO) = {loo_std:.4f}")
        n750 = next(r for r in loo if r['window_removed'] == 750)
        print(f"  → drop n=750: α shifts from {full['slope']:+.4f} "
              f"to {n750['alpha']:+.4f} (Δ = {n750['alpha']-full['slope']:+.4f})")

        # ---- Part C: Sub-set fits ----
        print(f"\n--- Part C: Sub-set fits ---")
        early = [(n, z) for n, z in pts if n <= 500]      # 100, 200, 300, 500
        late = [(n, z) for n, z in pts if n >= 500]        # 500, 750, 1000
        mid_late = [(n, z) for n, z in pts if n >= 300]    # 300, 500, 750, 1000
        sub_fits = {
            'early (100..500, 4 pts)': parametric_fit(early),
            'late (500..1000, 3 pts)': parametric_fit(late),
            'mid-late (300..1000, 4 pts)': parametric_fit(mid_late),
        }
        subset_summary[def_label] = sub_fits
        print(f"  {'subset':>30}  {'α':>8}  {'SE α':>8}  {'R²':>6}")
        for name, fit in sub_fits.items():
            print(f"  {name:>30}  {fit['slope']:>+8.4f}  "
                  f"{fit['se_slope']:>8.4f}  {fit['r2']:>6.3f}")

        # ---- Build summary table rows ----
        if def_label == 'C':
            summary_rows.append(['Full (parametric)', '6 windows (100..1000)',
                                 f"{full['slope']:.3f}",
                                 f"± {full['se_slope']:.3f} (parametric SE)"])
            summary_rows.append([f'Full (bootstrap, K={K_BOOTSTRAP:,})',
                                 '6 windows (100..1000)',
                                 f"{boot['mean']:.3f}",
                                 f"[{boot['ci95_lo']:.3f}, {boot['ci95_hi']:.3f}] "
                                 f"(95% bootstrap)"])
            summary_rows.append(['Sub-set (early)', '4 windows (100..500)',
                                 f"{sub_fits['early (100..500, 4 pts)']['slope']:.3f}",
                                 f"± {sub_fits['early (100..500, 4 pts)']['se_slope']:.3f}"])
            summary_rows.append(['Sub-set (late)', '3 windows (500..1000)',
                                 f"{sub_fits['late (500..1000, 3 pts)']['slope']:.3f}",
                                 f"± {sub_fits['late (500..1000, 3 pts)']['se_slope']:.3f}"])
            summary_rows.append(['Sub-set (mid-late)', '4 windows (300..1000)',
                                 f"{sub_fits['mid-late (300..1000, 4 pts)']['slope']:.3f}",
                                 f"± {sub_fits['mid-late (300..1000, 4 pts)']['se_slope']:.3f}"])
            summary_rows.append(['Leave-one-out range', '6 LOO samples',
                                 f"{loo_min:.3f}..{loo_max:.3f}",
                                 f"std {loo_std:.3f} across samples"])

    # ---- Single-page summary table (Def C, primary) ----
    print(f"\n{'=' * 76}")
    print('Single-page summary (Def C, primary)')
    print('=' * 76)
    col_w = [32, 24, 10, 36]
    headers = ['Fit', 'Windows', 'α', '95% CI / SE']
    print('  | ' + ' | '.join(h.ljust(w) for h, w in zip(headers, col_w)) + ' |')
    print('  |' + '|'.join('-' * (w + 2) for w in col_w) + '|')
    for row in summary_rows:
        print('  | ' + ' | '.join(c.ljust(w) for c, w in zip(row, col_w)) + ' |')

    # ---- One-paragraph summary for §6.5.1 ----
    boot_c = boot_summary['C']
    early_c = subset_summary['C']['early (100..500, 4 pts)']
    loo_c_alphas = [r['alpha'] for r in loo_summary['C']]
    print(f"\n{'=' * 76}")
    print('Paragraph for §6.5.1 (Def C)')
    print('=' * 76)
    para = (
        f"Bootstrap on the six (n, log z) pairs (K = {K_BOOTSTRAP:,}, "
        f"resampled with replacement) gives α = {boot_c['mean']:.2f} "
        f"[{boot_c['ci95_lo']:+.2f}, {boot_c['ci95_hi']:+.2f}] (95% CI) "
        f"for Def C, substantially wider than the parametric ± "
        f"{full_c['se_slope']:.2f}. The early-window sub-set fit on n ∈ "
        f"{{100, 200, 300, 500}} alone gives α = {early_c['slope']:.2f} "
        f"(SE = {early_c['se_slope']:.2f}); the late-window sub-set on n ∈ "
        f"{{500, 750, 1000}} gives α = "
        f"{subset_summary['C']['late (500..1000, 3 pts)']['slope']:.2f} "
        f"(SE = {subset_summary['C']['late (500..1000, 3 pts)']['se_slope']:.2f}). "
        f"Leave-one-out across the six windows yields α ∈ "
        f"[{min(loo_c_alphas):+.2f}, {max(loo_c_alphas):+.2f}]. The "
        f"parametric ± {full_c['se_slope']:.2f} under-represents the "
        f"actual uncertainty given the non-monotone residual structure."
    )
    print('\n  ' + para)

    # ---- CSV outputs ----
    summary_csv = os.path.join(RESULTS_DIR, 'v3_16_alpha_summary.csv')
    with open(summary_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['fit', 'windows', 'alpha', 'ci_or_se'])
        for row in summary_rows:
            w.writerow(row)
    print(f"\n  Saved: {summary_csv}")

    boot_csv = os.path.join(RESULTS_DIR, 'v3_16_alpha_bootstrap.csv')
    with open(boot_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['definition', 'k_bootstrap', 'mean', 'median', 'std',
                    'ci95_lo', 'ci95_hi', 'ci90_lo', 'ci90_hi',
                    'parametric_alpha', 'parametric_se'])
        for d in ('C', 'A'):
            b = boot_summary[d]
            full = parametric_fit(by_def[d])
            w.writerow([d, b['n'], f"{b['mean']:.6f}", f"{b['median']:.6f}",
                        f"{b['std']:.6f}", f"{b['ci95_lo']:.6f}",
                        f"{b['ci95_hi']:.6f}", f"{b['ci90_lo']:.6f}",
                        f"{b['ci90_hi']:.6f}", f"{full['slope']:.6f}",
                        f"{full['se_slope']:.6f}"])
    print(f"  Saved: {boot_csv}")

    loo_csv = os.path.join(RESULTS_DIR, 'v3_16_alpha_leave_one_out.csv')
    with open(loo_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['definition', 'window_removed', 'alpha', 'se', 'r2',
                    'delta_from_full'])
        for d in ('C', 'A'):
            full = parametric_fit(by_def[d])
            for r in loo_summary[d]:
                w.writerow([d, r['window_removed'], f"{r['alpha']:.6f}",
                            f"{r['se']:.6f}", f"{r['r2']:.6f}",
                            f"{r['alpha'] - full['slope']:+.6f}"])
    print(f"  Saved: {loo_csv}")

    subset_csv = os.path.join(RESULTS_DIR, 'v3_16_alpha_subsets.csv')
    with open(subset_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['definition', 'subset', 'n_points', 'alpha', 'se', 'r2'])
        for d in ('C', 'A'):
            full = parametric_fit(by_def[d])
            w.writerow([d, 'full (100..1000)', 6, f"{full['slope']:.6f}",
                        f"{full['se_slope']:.6f}", f"{full['r2']:.6f}"])
            for name, fit in subset_summary[d].items():
                w.writerow([d, name, fit['n'], f"{fit['slope']:.6f}",
                            f"{fit['se_slope']:.6f}", f"{fit['r2']:.6f}"])
    print(f"  Saved: {subset_csv}")

    # ---- Plot ----
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print('  [warning] matplotlib unavailable; skipping plot')
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Def C log-log with full fit, bootstrap band, sub-set lines
    ax = axes[0]
    pts_c = by_def['C']
    ns = [n for n, _ in pts_c]
    zs = [z for _, z in pts_c]
    log_ns = np.array([math.log10(n) for n in ns])

    full_c_fit = parametric_fit(pts_c)
    boot_c = boot_summary['C']

    # Plot data points
    ax.loglog(ns, zs, 'o', color='#d62728', markersize=10, zorder=5,
              label='Def C six-window data')

    # Full fit line
    n_grid = np.logspace(math.log10(min(ns)), math.log10(max(ns)), 80)
    log_n_grid = np.log10(n_grid)
    z_full = 10 ** (full_c_fit['intercept'] + full_c_fit['slope'] * log_n_grid)
    ax.loglog(n_grid, z_full, '-', color='#d62728', linewidth=2.0,
              label=(f"Full fit: α = {full_c_fit['slope']:.3f} "
                     f"± {full_c_fit['se_slope']:.3f} (parametric)"))

    # Bootstrap 95% band — re-derive per-x quantiles from a fresh sample
    rng = random.Random(SEED_BASE)
    L = len(pts_c)
    log_n_data = [math.log10(n) for n, _ in pts_c]
    log_z_data = [math.log10(z) for _, z in pts_c]
    band_samples = []
    for _ in range(2000):
        idx = [rng.randrange(L) for _ in range(L)]
        xs = [log_n_data[i] for i in idx]
        if len(set(xs)) < 2:
            continue
        ys = [log_z_data[i] for i in idx]
        fit = linear_fit(xs, ys)
        if fit is None:
            continue
        band_samples.append((fit['intercept'], fit['slope']))
    band_lo = []
    band_hi = []
    for lng in log_n_grid:
        vals = sorted(b + a * lng for b, a in band_samples)
        band_lo.append(10 ** percentile(vals, 2.5))
        band_hi.append(10 ** percentile(vals, 97.5))
    ax.fill_between(n_grid, band_lo, band_hi, color='#d62728', alpha=0.15,
                    label='Bootstrap 95% band')

    # Sub-set fit lines (early + late)
    early_pts = [(n, z) for n, z in pts_c if n <= 500]
    late_pts = [(n, z) for n, z in pts_c if n >= 500]
    early_fit = parametric_fit(early_pts)
    late_fit = parametric_fit(late_pts)

    n_early = np.logspace(math.log10(100), math.log10(500), 30)
    z_early = 10 ** (early_fit['intercept']
                     + early_fit['slope'] * np.log10(n_early))
    ax.loglog(n_early, z_early, '--', color='#1f77b4', linewidth=1.6,
              label=(f"Early (100..500): α = {early_fit['slope']:+.3f} "
                     f"± {early_fit['se_slope']:.3f}"))

    n_late = np.logspace(math.log10(500), math.log10(1000), 30)
    z_late = 10 ** (late_fit['intercept']
                    + late_fit['slope'] * np.log10(n_late))
    ax.loglog(n_late, z_late, '--', color='#2ca02c', linewidth=1.6,
              label=(f"Late (500..1000): α = {late_fit['slope']:+.3f} "
                     f"± {late_fit['se_slope']:.3f}"))

    ax.set_xticks(ns)
    ax.set_xticklabels([str(n) for n in ns])
    ax.set_xlabel('Window size n (log scale)')
    ax.set_ylabel('Natural-ordering z (log scale)')
    ax.set_title('Def C: full fit, bootstrap 95% band, sub-set fits')
    ax.grid(True, which='both', alpha=0.3)
    ax.legend(loc='upper left', fontsize=8.5)

    # Right: Bootstrap α distribution (Def C) with parametric overlay
    ax = axes[1]
    rng2 = random.Random(SEED_BASE)
    alphas_c, _ = bootstrap_alpha(pts_c, K_BOOTSTRAP, SEED_BASE)
    ax.hist(alphas_c, bins=60, color='#d62728', alpha=0.55,
            edgecolor='#7f1212', linewidth=0.4, density=True)
    ax.axvline(full_c_fit['slope'], color='black', linewidth=1.6,
               label=f"Parametric α = {full_c_fit['slope']:.3f}")
    ax.axvline(boot_c['ci95_lo'], color='#444', linestyle=':', linewidth=1.3,
               label=(f"Bootstrap 95% CI "
                      f"[{boot_c['ci95_lo']:+.2f}, {boot_c['ci95_hi']:+.2f}]"))
    ax.axvline(boot_c['ci95_hi'], color='#444', linestyle=':', linewidth=1.3)
    ax.axvline(0.0, color='gray', linestyle='--', linewidth=1.0, alpha=0.6,
               label='α = 0 (no growth)')
    ax.set_xlabel('Bootstrap α')
    ax.set_ylabel('Density')
    ax.set_title(f'Def C bootstrap α distribution (K = {K_BOOTSTRAP:,})')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.suptitle('Paper 3 v3.16 — α-robustness on the §6.5.1 six-window fit')
    fig.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, 'v3_16_alpha_robustness.png')
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"  Saved: {plot_path}")


if __name__ == '__main__':
    main()
