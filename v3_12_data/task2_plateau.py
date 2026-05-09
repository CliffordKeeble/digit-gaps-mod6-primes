#!/usr/bin/env python3
"""Task 2 (Paper 3 v3.12): Plateau extension for §6.5.3.

Extend the §6.5.3 cumulative tie-count vs random-walk-expectation table from
N ∈ {100, 500, 1k, 2k, 5k, 10k, 20k, 50k} (8 rows) to add N ∈ {100k, 200k, 500k}
(11 rows total).

Convention (matches §8.5):
    T(N) = #{n ≤ N : S_5(n) = 0}
where S_5(n) is the running sum of chi5(p_i) over the first n 5-series primes
(natural ascending size order, including the ramified p=5 at i=1 — so
S_5(1) = 0 always counts as a tie).

Outputs:
    11-row ratio table (N, observed, expected = sqrt(2N/pi), ratio)
    Linear fit on full range (11 rows) and restricted (N >= 1k, 9 rows):
        slope, t-statistic on n-2 dof, two-tailed p-value
    Plot: ratio vs log10(N) with both fit lines

Verification gate: at N=50k the ratio must reproduce 5.16 (matches §8.5
exactly under §8.5's convention). Halt if not matched.
"""
import math
import os
import sys
import csv
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve, chi5, five_series_primes, t_pvalue_twotail

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

# Empirical sieve sizing: the 1M-th prime is ~15.5M; 5-series density is ~1/2
# of primes coprime to 6 (i.e., ~1/2 of primes >3). So 500k 5-series primes
# need ~1M total primes -> sieve to ~16M. 25M gives comfortable headroom.
SIEVE_LIMIT = 25_000_000

# Existing v3.11 data points from §8.5
EXISTING = [
    (100,    29),
    (500,    72),
    (1_000,  141),
    (2_000,  None),  # filled by computation; v3.11 had ratio 6.50 here
    (5_000,  327),
    (10_000, 437),
    (20_000, 683),
    (50_000, 921),
]
# New data points for v3.12
NEW_TARGETS = [100_000, 200_000, 500_000]

ALL_N = [n for n, _ in EXISTING] + NEW_TARGETS


def cumulative_ties(p5):
    """Return list ties[i] = T(i+1) for i = 0 .. len(p5)-1.

    T(n) = #{k <= n : S_5(k) = 0}, where S_5(k) is running sum of chi5 over
    the first k 5-series primes (including p=5 at k=1, contributing 0).
    """
    s = 0
    ties = 0
    out = [0] * len(p5)
    for i, p in enumerate(p5):
        s += chi5(p)
        if s == 0:
            ties += 1
        out[i] = ties
    return out


def linear_fit(xs, ys):
    """OLS regression of ys on xs. Returns slope, intercept, t_slope, p, r2."""
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
    p_value = t_pvalue_twotail(t_slope, df) if se_slope > 0 else float('nan')
    return {
        'n': n, 'slope': slope, 'intercept': intercept,
        'se_slope': se_slope, 't_slope': t_slope, 'df': df,
        'p_value': p_value, 'r2': r2,
    }


def make_plot(rows, fit_full, fit_restricted, out_path):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print(f"  [warning] matplotlib unavailable; skipping plot")
        return

    log_N = [math.log10(r['N']) for r in rows]
    ratios = [r['ratio'] for r in rows]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.scatter(log_N, ratios, s=70, color='#1f77b4', zorder=3,
               edgecolors='black', linewidths=0.5,
               label=f'5-series tie ratio ({len(rows)} points)')

    # Vertical guide at the v3.11 boundary (largest existing N = 50k)
    ax.axvline(math.log10(50_000), color='gray', linestyle=':', alpha=0.6,
               label='v3.11 upper bound (N=50k)')

    # Fit lines
    x_fit = [min(log_N), max(log_N)]
    if fit_full:
        y_fit = [fit_full['intercept'] + fit_full['slope'] * x for x in x_fit]
        ax.plot(x_fit, y_fit, '--', color='#d62728', alpha=0.85,
                label=f"Full range (n={fit_full['n']}): slope={fit_full['slope']:.3f}, "
                      f"t={fit_full['t_slope']:.2f}, p={fit_full['p_value']:.3f}")
    if fit_restricted:
        # Only show fit line over the restricted x range
        log_N_restricted = [math.log10(r['N']) for r in rows if r['N'] >= 1000]
        x_fit_r = [min(log_N_restricted), max(log_N_restricted)]
        y_fit_r = [fit_restricted['intercept'] + fit_restricted['slope'] * x
                   for x in x_fit_r]
        ax.plot(x_fit_r, y_fit_r, '-', color='#2ca02c', alpha=0.85,
                label=f"N>=1k (n={fit_restricted['n']}): slope={fit_restricted['slope']:.3f}, "
                      f"t={fit_restricted['t_slope']:.2f}, p={fit_restricted['p_value']:.3f}")

    ax.set_xlabel(r'$\log_{10}(N)$')
    ax.set_ylabel(r'Ratio $T(N) / \sqrt{2N/\pi}$')
    ax.set_title('5-series cumulative tie count vs random-walk expectation\n'
                 'Paper 3 v3.12 plateau extension')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right', fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    print(f"  Saved: {out_path}")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Sieving primes up to {SIEVE_LIMIT}...")
    t0 = time.time()
    primes = sieve(SIEVE_LIMIT)
    t1 = time.time()
    print(f"  Sieved {len(primes)} primes in {t1 - t0:.1f}s")

    p5 = five_series_primes(primes)
    print(f"  5-series primes available: {len(p5)} (need >= {max(ALL_N)})")
    assert len(p5) >= max(ALL_N), f"Insufficient 5-series primes — increase SIEVE_LIMIT"

    print(f"\nComputing cumulative tie counts up to N = {max(ALL_N):,}...")
    t0 = time.time()
    ties = cumulative_ties(p5)
    t1 = time.time()
    print(f"  Done in {t1 - t0:.1f}s")

    rows = []
    for N in ALL_N:
        T = ties[N - 1]
        expected = math.sqrt(2 * N / math.pi)
        ratio = T / expected
        rows.append({'N': N, 'T': T, 'expected': expected, 'ratio': ratio})

    rows.sort(key=lambda r: r['N'])

    # ----- Verification gate -----
    n50k = next(r for r in rows if r['N'] == 50_000)
    print(f"\n  Verification: N=50,000 -> T={n50k['T']}, expected={n50k['expected']:.2f}, "
          f"ratio={n50k['ratio']:.3f} (target 5.16)")
    if abs(n50k['ratio'] - 5.16) > 0.01:
        print(f"  HALT: N=50k ratio mismatch (got {n50k['ratio']:.3f}, expected 5.16).")
        sys.exit(1)
    print("  OK: §8.5 anchor reproduces.")

    # ----- 11-row table -----
    print(f"\n  {'N':>10} {'T(N)':>10} {'sqrt(2N/pi)':>15} {'ratio':>10}")
    print(f"  {'-'*48}")
    for r in rows:
        flag = '   *NEW*' if r['N'] in NEW_TARGETS else ''
        print(f"  {r['N']:>10,d} {r['T']:>10d} {r['expected']:>15.3f} "
              f"{r['ratio']:>10.4f}{flag}")

    # ----- Linear fits -----
    log_N_full = [math.log10(r['N']) for r in rows]
    ratios_full = [r['ratio'] for r in rows]
    fit_full = linear_fit(log_N_full, ratios_full)

    rows_restricted = [r for r in rows if r['N'] >= 1000]
    log_N_r = [math.log10(r['N']) for r in rows_restricted]
    ratios_r = [r['ratio'] for r in rows_restricted]
    fit_restricted = linear_fit(log_N_r, ratios_r)

    print(f"\n  Linear fit — full range (n={fit_full['n']}, df={fit_full['df']}):")
    print(f"    slope     = {fit_full['slope']:.4f}")
    print(f"    intercept = {fit_full['intercept']:.4f}")
    print(f"    SE(slope) = {fit_full['se_slope']:.4f}")
    print(f"    t(slope)  = {fit_full['t_slope']:.3f}")
    print(f"    p (2-tail)= {fit_full['p_value']:.4f}")
    print(f"    R^2       = {fit_full['r2']:.4f}")

    print(f"\n  Linear fit — N >= 1k (n={fit_restricted['n']}, df={fit_restricted['df']}):")
    print(f"    slope     = {fit_restricted['slope']:.4f}")
    print(f"    intercept = {fit_restricted['intercept']:.4f}")
    print(f"    SE(slope) = {fit_restricted['se_slope']:.4f}")
    print(f"    t(slope)  = {fit_restricted['t_slope']:.3f}")
    print(f"    p (2-tail)= {fit_restricted['p_value']:.4f}")
    print(f"    R^2       = {fit_restricted['r2']:.4f}")

    # CV stats for the restricted set
    n_r = len(ratios_r)
    mean_r = sum(ratios_r) / n_r
    std_r = math.sqrt(sum((x - mean_r) ** 2 for x in ratios_r) / (n_r - 1))
    cv_r = std_r / mean_r
    print(f"\n  Restricted (N>=1k) descriptive stats:")
    print(f"    n         = {n_r}")
    print(f"    mean      = {mean_r:.4f}")
    print(f"    std       = {std_r:.4f}")
    print(f"    CV        = {cv_r*100:.2f}%")
    print(f"    min/max   = {min(ratios_r):.4f} / {max(ratios_r):.4f}")

    # ----- Save CSV -----
    csv_path = os.path.join(RESULTS_DIR, 'task2_plateau.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['N', 'T', 'expected_sqrt_2N_pi', 'ratio', 'is_new_v3_12'])
        for r in rows:
            w.writerow([r['N'], r['T'], f"{r['expected']:.6f}",
                        f"{r['ratio']:.6f}", '1' if r['N'] in NEW_TARGETS else '0'])
    print(f"\n  Saved: {csv_path}")

    # Fits CSV
    fits_path = os.path.join(RESULTS_DIR, 'task2_fits.csv')
    with open(fits_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['range', 'n', 'df', 'slope', 'intercept',
                    'se_slope', 't_slope', 'p_two_tail', 'r2'])
        w.writerow(['full', fit_full['n'], fit_full['df'],
                    f"{fit_full['slope']:.6f}", f"{fit_full['intercept']:.6f}",
                    f"{fit_full['se_slope']:.6f}", f"{fit_full['t_slope']:.6f}",
                    f"{fit_full['p_value']:.6f}", f"{fit_full['r2']:.6f}"])
        w.writerow(['N>=1k', fit_restricted['n'], fit_restricted['df'],
                    f"{fit_restricted['slope']:.6f}", f"{fit_restricted['intercept']:.6f}",
                    f"{fit_restricted['se_slope']:.6f}", f"{fit_restricted['t_slope']:.6f}",
                    f"{fit_restricted['p_value']:.6f}", f"{fit_restricted['r2']:.6f}"])
    print(f"  Saved: {fits_path}")

    # ----- Plot -----
    plot_path = os.path.join(RESULTS_DIR, 'task2_plateau.png')
    make_plot(rows, fit_full, fit_restricted, plot_path)


if __name__ == '__main__':
    main()
