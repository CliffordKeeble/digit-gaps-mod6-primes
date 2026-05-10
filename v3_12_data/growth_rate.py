#!/usr/bin/env python3
"""Task 1 (Paper 3 v3.15): §6.5.1 extended-window growth-rate characterisation.

PRINCIPAL fifth-star item. v3.14 §6.5.1 reports natural-ordering z at three
windows {100, 500, 1000}; Mr Adversary asks whether z(n) follows a clean
power-law and how the exponent compares to the naive √n prediction.

Naive prediction. If natural-order tie excess grows linearly in n (constant
rate r per prime) and shuffle std grows as √n, then z grows as √n — i.e.,
z ∝ n^α with α = 0.5. The three-point v3.14 sample gives z/√n =
{0.308, 0.151, 0.176} (Def C) — non-monotone, suggesting either sub-linear
excess or a regime change near n ≈ 500.

Computation. Six windows n ∈ {100, 200, 300, 500, 750, 1000}, both Defs.
For each: natural T, shuffle baseline (1000 trials, seed = trial * 137 + 42)
mean and std, z = (T − μ) / σ, z/√n. Then fit log z ∝ α log n + const,
report α with standard error.

Verification gate. Reproduce v3.14 z at n ∈ {100, 500, 1000} within ±0.10.
"""
import math
import os
import sys
import csv
import random
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve, chi5, five_series_primes, t_pvalue_twotail
from task1_orderings import chi_seq_def_A, chi_seq_def_C, tie_count, order_natural

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

SIEVE_LIMIT = 200_000
N_SHUFFLE = 1000

# Six windows: 3 anchors from v3.14 + 3 new
WINDOWS = [100, 200, 300, 500, 750, 1000]
ANCHORS_V3_14 = {
    'A': {100: 3.21, 500: 3.48, 1000: 5.70},
    'C': {100: 3.08, 500: 3.37, 1000: 5.57},
}
ANCHOR_TOL = 0.10


def shuffle_tie_count(chi_seq, trial):
    rng = random.Random(trial * 137 + 42)
    perm = list(range(len(chi_seq)))
    rng.shuffle(perm)
    return tie_count(chi_seq, perm)


def run_one(p5, n, def_label, chi_builder):
    chi_seq = chi_builder(p5, n)
    L = len(chi_seq)
    natural_T = tie_count(chi_seq, order_natural(L))
    t0 = time.time()
    shuf_counts = [shuffle_tie_count(chi_seq, i) for i in range(N_SHUFFLE)]
    t1 = time.time()
    mean = sum(shuf_counts) / N_SHUFFLE
    std = math.sqrt(sum((x - mean) ** 2 for x in shuf_counts) / (N_SHUFFLE - 1))
    z = (natural_T - mean) / std if std > 0 else 0.0
    p_ge = sum(1 for x in shuf_counts if x >= natural_T) / N_SHUFFLE
    return {
        'n': n, 'definition': def_label, 'L': L,
        'T_nat': natural_T, 'shuf_mean': mean, 'shuf_std': std,
        'z': z, 'p_ge': p_ge, 'z_over_sqrtn': z / math.sqrt(n),
        'shuf_runtime': t1 - t0,
    }


def linear_fit(xs, ys):
    """OLS regression. Returns dict with slope, intercept, SE, t, p, r2."""
    n = len(xs)
    if n < 3:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    ss_xx = sum((x - mean_x) ** 2 for x in xs)
    ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    ss_yy = sum((y - mean_y) ** 2 for y in ys)
    slope = ss_xy / ss_xx
    intercept = mean_y - slope * mean_x
    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_yy if ss_yy > 0 else 0.0
    df = n - 2
    se_slope = math.sqrt(ss_res / (df * ss_xx)) if df > 0 and ss_xx > 0 else 0.0
    t_slope = slope / se_slope if se_slope > 0 else 0.0
    # Hypothesis: alpha != 0.5 (compare to the naive prediction)
    t_vs_half = (slope - 0.5) / se_slope if se_slope > 0 else 0.0
    p_value_vs_zero = t_pvalue_twotail(t_slope, df) if se_slope > 0 else float('nan')
    p_value_vs_half = t_pvalue_twotail(t_vs_half, df) if se_slope > 0 else float('nan')
    return {
        'n': n, 'slope': slope, 'intercept': intercept,
        'se_slope': se_slope, 't_slope': t_slope, 'df': df,
        't_vs_half': t_vs_half, 'p_vs_half': p_value_vs_half,
        'p_vs_zero': p_value_vs_zero, 'r2': r2,
    }


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Sieving primes up to {SIEVE_LIMIT}...")
    primes = sieve(SIEVE_LIMIT)
    p5 = five_series_primes(primes)
    print(f"  5-series primes: {len(p5)}")

    rows_a = []
    rows_c = []
    print(f"\n{'='*76}")
    print(f"Six-window sweep: n in {WINDOWS}, both definitions")
    print(f"{'='*76}")
    print(f"  {'def':>3}  {'n':>4} {'L':>4} {'T_nat':>5}  {'shuf_mean':>9}  "
          f"{'shuf_std':>8}  {'z':>7}  {'z/sqrt(n)':>10}  {'p_ge':>7}  "
          f"{'time':>5}")
    for n in WINDOWS:
        for def_label, chi_builder, rows in [
            ('A', chi_seq_def_A, rows_a),
            ('C', chi_seq_def_C, rows_c),
        ]:
            r = run_one(p5, n, def_label, chi_builder)
            rows.append(r)
            print(f"  {def_label:>3}  {r['n']:>4} {r['L']:>4} {r['T_nat']:>5}  "
                  f"{r['shuf_mean']:>9.3f}  {r['shuf_std']:>8.3f}  "
                  f"{r['z']:>+7.3f}  {r['z_over_sqrtn']:>10.4f}  "
                  f"{r['p_ge']:>7.4f}  {r['shuf_runtime']:>4.1f}s")

    # ---- Verification gate ----
    print(f"\n{'='*76}")
    print(f"Verification gate: v3.14 anchors (tolerance ±{ANCHOR_TOL})")
    print(f"{'='*76}")
    fail = False
    for def_label, rows in [('A', rows_a), ('C', rows_c)]:
        for r in rows:
            n = r['n']
            if n in ANCHORS_V3_14[def_label]:
                target = ANCHORS_V3_14[def_label][n]
                got = r['z']
                ok = abs(got - target) <= ANCHOR_TOL
                flag = 'OK' if ok else 'FAIL'
                print(f"  Def {def_label} n={n:>4}: z = {got:+.3f}  "
                      f"(target {target:+.2f})  {flag}")
                if not ok:
                    fail = True
    if fail:
        print("\n  HALT: v3.14 anchor mismatch.")
        sys.exit(1)
    print("  All anchors OK.")

    # ---- Power-law fit ----
    print(f"\n{'='*76}")
    print("Power-law fit: log(z) vs log(n)")
    print(f"{'='*76}")

    fits = {}
    for def_label, rows in [('A', rows_a), ('C', rows_c)]:
        # Filter out any z <= 0 (shouldn't happen, but defensive)
        usable = [r for r in rows if r['z'] > 0]
        if len(usable) < len(rows):
            print(f"  Def {def_label}: dropping {len(rows) - len(usable)} non-positive z values")
        log_n = [math.log10(r['n']) for r in usable]
        log_z = [math.log10(r['z']) for r in usable]
        fit = linear_fit(log_n, log_z)
        fits[def_label] = fit
        print(f"\n  Definition {def_label}:")
        print(f"    n points    = {fit['n']}")
        print(f"    slope alpha = {fit['slope']:.4f}")
        print(f"    SE(alpha)   = {fit['se_slope']:.4f}")
        print(f"    intercept   = {fit['intercept']:.4f}")
        print(f"    R^2         = {fit['r2']:.4f}")
        print(f"    df          = {fit['df']}")
        print(f"    t(alpha)    = {fit['t_slope']:.3f}    "
              f"two-tail p (alpha=0)  = {fit['p_vs_zero']:.4f}")
        print(f"    t(alpha-0.5)= {fit['t_vs_half']:.3f}  "
              f"two-tail p (alpha=0.5) = {fit['p_vs_half']:.4f}")

    # ---- Verdict ----
    print(f"\n{'='*76}")
    print("Brief scenario classification (Def C, primary)")
    print(f"{'='*76}")
    alpha_c = fits['C']['slope']
    se_c = fits['C']['se_slope']
    p_half_c = fits['C']['p_vs_half']
    if abs(alpha_c - 0.5) <= 0.10:
        verdict = (f"(a) alpha ≈ 0.5 within {abs(alpha_c-0.5):.2f}: rate of tie "
                   f"excess approximately constant per prime.")
    elif alpha_c < 0.4:
        verdict = (f"(b) alpha = {alpha_c:.3f} < 0.5 substantially: SUB-LINEAR "
                   f"excess; rate-of-tie-excess declines per prime as n grows.")
    elif 0.4 <= alpha_c < 0.5:
        verdict = (f"(b) alpha = {alpha_c:.3f} just below 0.5: mildly sub-linear; "
                   f"rate-of-tie-excess fades slightly with n.")
    elif 0.5 < alpha_c <= 0.6:
        verdict = (f"(c) alpha = {alpha_c:.3f} just above 0.5: mildly super-linear.")
    else:
        verdict = (f"(c) alpha = {alpha_c:.3f} > 0.5 substantially: SUPER-LINEAR "
                   f"excess; rate-of-tie-excess increases per prime as n grows.")
    print(f"  Def C alpha = {alpha_c:.3f} ± {se_c:.3f}")
    print(f"  vs naive 0.5: t = {fits['C']['t_vs_half']:.2f}, "
          f"p = {p_half_c:.4f}")
    if p_half_c < 0.05:
        print(f"  Reject naive alpha=0.5 hypothesis at p={p_half_c:.4f} (significant).")
    else:
        print(f"  Cannot reject naive alpha=0.5 at p<0.05 (p={p_half_c:.4f}).")
    print(f"\n  -> {verdict}")

    # ---- One-line summary for §6.5.1 ----
    print(f"\n{'='*76}")
    print("One-line summary for §6.5.1")
    print(f"{'='*76}")
    sentence = (
        f"Across n ∈ {{100, 200, 300, 500, 750, 1000}}, z grows as n^alpha "
        f"with alpha = {fits['C']['slope']:.3f} ± {fits['C']['se_slope']:.3f} "
        f"(Def C) and alpha = {fits['A']['slope']:.3f} ± {fits['A']['se_slope']:.3f} "
        f"(Def A); compare to the naive constant-rate-excess prediction of "
        f"alpha = 0.5."
    )
    print(f"\n  {sentence}")

    # ---- CSVs ----
    csv_path = os.path.join(RESULTS_DIR, 'v3_15_task1_growth_rate.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['definition', 'n', 'L_eff', 'T_nat', 'shuf_mean',
                    'shuf_std', 'z', 'z_over_sqrtn', 'p_ge'])
        for rows in (rows_a, rows_c):
            for r in rows:
                w.writerow([r['definition'], r['n'], r['L'], r['T_nat'],
                            f"{r['shuf_mean']:.6f}", f"{r['shuf_std']:.6f}",
                            f"{r['z']:.6f}", f"{r['z_over_sqrtn']:.6f}",
                            f"{r['p_ge']:.6f}"])
    print(f"\n  Saved: {csv_path}")

    fits_path = os.path.join(RESULTS_DIR, 'v3_15_task1_powerlaw_fits.csv')
    with open(fits_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['definition', 'n_points', 'alpha', 'se_alpha', 'intercept',
                    'r2', 'df', 't_alpha_vs_zero', 'p_alpha_vs_zero',
                    't_alpha_vs_half', 'p_alpha_vs_half'])
        for d, fit in fits.items():
            w.writerow([d, fit['n'], f"{fit['slope']:.6f}",
                        f"{fit['se_slope']:.6f}", f"{fit['intercept']:.6f}",
                        f"{fit['r2']:.6f}", fit['df'],
                        f"{fit['t_slope']:.6f}", f"{fit['p_vs_zero']:.6e}",
                        f"{fit['t_vs_half']:.6f}", f"{fit['p_vs_half']:.6e}"])
    print(f"  Saved: {fits_path}")

    # ---- Plot ----
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("  [warning] matplotlib unavailable; skipping plot")
        return

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    # Left panel: log-log z vs n with fit lines
    ax = axes[0]
    ns = [r['n'] for r in rows_a]
    zs_a = [r['z'] for r in rows_a]
    zs_c = [r['z'] for r in rows_c]

    ax.loglog(ns, zs_a, 'o-', color='#1f77b4', markersize=8, linewidth=1.2,
              label=f"Def A: alpha = {fits['A']['slope']:.3f} ± {fits['A']['se_slope']:.3f}")
    ax.loglog(ns, zs_c, 's-', color='#d62728', markersize=8, linewidth=1.2,
              label=f"Def C: alpha = {fits['C']['slope']:.3f} ± {fits['C']['se_slope']:.3f}")

    # Reference: alpha = 0.5 line (z proportional sqrt(n))
    n_ref = np.logspace(math.log10(min(ns)), math.log10(max(ns)), 50)
    # Anchor at the geometric centre
    n_centre = math.sqrt(min(ns) * max(ns))
    z_centre = math.sqrt(zs_c[0] * zs_c[-1])  # geometric mean of endpoint z's
    z_ref = z_centre * (n_ref / n_centre) ** 0.5
    ax.loglog(n_ref, z_ref, '--', color='gray', linewidth=1.2, alpha=0.7,
              label=r'naive alpha = 0.5 (z $\propto \sqrt{n}$)')

    ax.set_xlabel('Window size n (log scale)')
    ax.set_ylabel('Natural-ordering z (log scale)')
    ax.set_title(r'Power-law fit of $z(n)$')
    ax.set_xticks(ns)
    ax.set_xticklabels([str(n) for n in ns])
    ax.grid(True, which='both', alpha=0.3)
    ax.legend(loc='upper left', fontsize=9)

    # Right panel: z/sqrt(n) vs n on linear axes (as in v3.14 brief)
    ax = axes[1]
    z_over_a = [r['z_over_sqrtn'] for r in rows_a]
    z_over_c = [r['z_over_sqrtn'] for r in rows_c]
    ax.plot(ns, z_over_a, 'o-', color='#1f77b4', markersize=8,
            label='Def A')
    ax.plot(ns, z_over_c, 's-', color='#d62728', markersize=8,
            label='Def C')
    ax.set_xscale('log')
    ax.set_xticks(ns)
    ax.set_xticklabels([str(n) for n in ns])
    ax.axhline(0, color='black', linewidth=0.5, alpha=0.5)
    ax.set_xlabel('Window size n (log scale)')
    ax.set_ylabel(r'$z(n) / \sqrt{n}$')
    ax.set_title(r'$z/\sqrt{n}$ — flat under naive $\alpha = 0.5$')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)

    fig.suptitle('Paper 3 v3.15 Task 1 — §6.5.1 z-growth-rate characterisation')
    fig.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, 'v3_15_task1_growth_rate.png')
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"  Saved: {plot_path}")


if __name__ == '__main__':
    main()
