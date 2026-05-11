#!/usr/bin/env python3
"""Paper 3 v4.5 Task 4 — Density of skipped digit-lengths across [60, 1000].

Per pre-registration `v3_12_data/briefs/
task4_density_measurement_pre_registration.md`.

Exploratory measurement (not falsificatory).  Computes per-decade and
cumulative skip statistics, fits three asymptotic forms, and produces
a two-panel chart for §8 Open Questions.

Outputs:
  v3_12_data/results/task4_density_measurement_per_decade.csv
  v3_12_data/results/task4_density_measurement_cumulative.csv
  v3_12_data/results/task4_density_measurement.png
  v3_12_data/results/task4_density_measurement_summary.md
"""
import os
import sys
import csv
import math

import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve

HERE = os.path.dirname(__file__)
RESULTS_DIR = os.path.join(HERE, 'results')
CSV_DECADE = os.path.join(RESULTS_DIR,
                          'task4_density_measurement_per_decade.csv')
CSV_CUMULATIVE = os.path.join(RESULTS_DIR,
                              'task4_density_measurement_cumulative.csv')
PNG_OUT = os.path.join(RESULTS_DIR, 'task4_density_measurement.png')
MD_OUT = os.path.join(RESULTS_DIR, 'task4_density_measurement_summary.md')

SIEVE_LIMIT = 200_000
N_MAX = 500
D_LO = 60
D_HI = 1000

# Decade bins (pre-registered)
BIN_EDGES = [60, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]


def compute_D(series, n_max):
    prod = 1
    out = []
    for p in series[:n_max]:
        prod *= p
        out.append(len(str(prod)))
    return out


def collect_skip_set(D):
    s = set()
    for i in range(len(D) - 1):
        if D[i + 1] - D[i] >= 2:
            for d in range(D[i] + 1, D[i + 1]):
                s.add(d)
    return s


def cluster_contiguous(sorted_ds):
    if not sorted_ds:
        return []
    out = []
    start = prev = sorted_ds[0]
    for d in sorted_ds[1:]:
        if d == prev + 1:
            prev = d
        else:
            out.append((start, prev))
            start = prev = d
    out.append((start, prev))
    return out


def fit_inv_log(D_arr, f_arr):
    """f = 1 - a/log(D); returns (a, RSS, adj_R2)."""
    y = 1.0 - f_arr
    x = 1.0 / np.log(D_arr)
    a = np.sum(x * y) / np.sum(x * x)
    pred = 1.0 - a / np.log(D_arr)
    rss = np.sum((f_arr - pred) ** 2)
    tss = np.sum((f_arr - np.mean(f_arr)) ** 2)
    n = len(f_arr)
    adj = 1 - (rss / max(1, n - 1)) / (tss / max(1, n - 1)) if tss > 0 else 1.0
    return a, rss, adj, pred


def fit_inv_log2(D_arr, f_arr):
    """f = 1 - a/log^2(D); returns (a, RSS, adj_R2)."""
    y = 1.0 - f_arr
    x = 1.0 / (np.log(D_arr) ** 2)
    a = np.sum(x * y) / np.sum(x * x)
    pred = 1.0 - a / (np.log(D_arr) ** 2)
    rss = np.sum((f_arr - pred) ** 2)
    tss = np.sum((f_arr - np.mean(f_arr)) ** 2)
    n = len(f_arr)
    adj = 1 - (rss / max(1, n - 1)) / (tss / max(1, n - 1)) if tss > 0 else 1.0
    return a, rss, adj, pred


def fit_inv_log_blend(D_arr, f_arr):
    """f = 1 - a/log(D) - b/log^2(D); returns ((a, b), RSS, adj_R2)."""
    y = 1.0 - f_arr
    x1 = 1.0 / np.log(D_arr)
    x2 = 1.0 / (np.log(D_arr) ** 2)
    X = np.column_stack([x1, x2])
    (ab, *_) = np.linalg.lstsq(X, y, rcond=None)
    a, b = ab
    pred = 1.0 - a / np.log(D_arr) - b / (np.log(D_arr) ** 2)
    rss = np.sum((f_arr - pred) ** 2)
    tss = np.sum((f_arr - np.mean(f_arr)) ** 2)
    n = len(f_arr)
    p = 2
    adj = 1 - (rss / max(1, n - p)) / (tss / max(1, n - 1)) if tss > 0 else 1.0
    return (a, b), rss, adj, pred


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Sieving primes up to {SIEVE_LIMIT}, taking N_MAX = {N_MAX}...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    D5 = compute_D(p5, N_MAX)
    D7 = compute_D(p7, N_MAX)
    print(f"  5-series: D_5(N_MAX) = {D5[-1]}")
    print(f"  7-series: D_7(N_MAX) = {D7[-1]}")
    assert min(D5[-1], D7[-1]) >= D_HI, \
        f"Both series must reach D ≥ {D_HI}; got D_5={D5[-1]}, D_7={D7[-1]}"

    # ---- Skip sets and clusters ----
    skip5 = collect_skip_set(D5)
    skip7 = collect_skip_set(D7)
    skip_combined_full = sorted(skip5 | skip7)
    clusters_full = cluster_contiguous(skip_combined_full)
    print(f"\n  Combined skip-set size (all D): {len(skip_combined_full)}")
    print(f"  Combined clusters (all D): {len(clusters_full)}")

    # ---- Anchor checks (Pattern 75) ----
    print("\n" + "=" * 72)
    print("Anchor verification under N_MAX = 500")
    print("=" * 72)
    # 23 strict clusters in [90, 200] (v4.2 anchor)
    strict_90_200 = [c for c in clusters_full if 90 <= c[0] and c[1] <= 200]
    print(f"  Strict-23 anchor: {len(strict_90_200)} clusters in [90, 200] "
          f"with d-range entirely in range (want 23)  "
          f"{'OK' if len(strict_90_200) == 23 else 'FAIL'}")
    if len(strict_90_200) != 23:
        print("  HALT: strict-23 anchor fails under N_MAX = 500.")
        sys.exit(1)
    # Merged-regime cluster lower edge = 172
    merged_edge = [c for c in clusters_full if c[0] == 172]
    print(f"  Merged-regime anchor: cluster with lower edge 172 exists  "
          f"{'OK' if merged_edge else 'FAIL'}")
    if not merged_edge:
        print("  HALT: merged-regime anchor (lower edge = 172) fails.")
        sys.exit(1)
    print(f"    merged-regime cluster at N_MAX = 500: {merged_edge[0]} "
          f"(width = {merged_edge[0][1] - merged_edge[0][0] + 1})")
    if merged_edge[0][1] < 482:
        print(f"  HALT: merged-regime upper edge "
              f"{merged_edge[0][1]} < 482 (was 482 at N_MAX = 250). "
              f"Skip-set monotonicity violated.")
        sys.exit(1)
    print("  OK (skip-set monotonicity preserved)")

    # ---- Restrict analysis to [D_LO, D_HI] ----
    skip_in_range = sorted(d for d in skip_combined_full if D_LO <= d < D_HI)
    n_in_range = D_HI - D_LO  # 940
    print(f"\n  Skipped d-values in [{D_LO}, {D_HI}): "
          f"{len(skip_in_range)} of {n_in_range}  "
          f"(overall fraction {len(skip_in_range)/n_in_range:.4f})")

    # ---- Per-decade metrics ----
    print("\n" + "=" * 72)
    print(f"Per-decade analysis (bins: {BIN_EDGES})")
    print("=" * 72)
    decade_rows = []
    for i in range(len(BIN_EDGES) - 1):
        lo = BIN_EDGES[i]
        hi = BIN_EDGES[i + 1]
        width = hi - lo
        midpoint = (lo + hi) / 2
        n_skipped = sum(1 for d in skip_in_range if lo <= d < hi)
        skip_fraction = n_skipped / width
        # Clusters starting in bin (lower edge in [lo, hi))
        clusters_starting = [c for c in clusters_full if lo <= c[0] < hi]
        n_clusters = len(clusters_starting)
        if clusters_starting:
            # Mean width, possibly truncated by cluster extending past hi
            widths = [c[1] - c[0] + 1 for c in clusters_starting]
            mean_width = sum(widths) / len(widths)
        else:
            mean_width = float('nan')
        decade_rows.append({
            'bin_lo': lo,
            'bin_hi': hi,
            'bin_width': width,
            'midpoint': midpoint,
            'n_skipped': n_skipped,
            'skip_fraction': skip_fraction,
            'n_clusters_starting': n_clusters,
            'mean_cluster_width': mean_width,
        })
        print(f"  [{lo:4d}, {hi:4d}) width {width:3d}  "
              f"skipped {n_skipped:4d}/{width:<3d}  "
              f"frac = {skip_fraction:.4f}  "
              f"clusters_starting = {n_clusters:3d}  "
              f"mean_width = "
              f"{mean_width:7.2f}" if not math.isnan(mean_width) else
              f"  [{lo:4d}, {hi:4d}) width {width:3d}  "
              f"skipped {n_skipped:4d}/{width:<3d}  "
              f"frac = {skip_fraction:.4f}  "
              f"clusters_starting = {n_clusters:3d}  "
              f"mean_width =     n/a")

    # ---- Cumulative metrics ----
    print("\n" + "=" * 72)
    print(f"Cumulative skip count in {D_LO}-step-{D_HI} (sample at "
          f"every 10th D)")
    print("=" * 72)
    cumulative_rows = []
    for D in range(D_LO, D_HI + 1, 10):
        cum_count = sum(1 for d in skip_in_range if d < D)
        # Instantaneous fraction in [D-10, D)
        inst_count = sum(1 for d in skip_in_range
                         if max(D_LO, D - 10) <= d < D)
        inst_width = D - max(D_LO, D - 10)
        inst_fraction = inst_count / inst_width if inst_width > 0 else 0
        cumulative_rows.append({
            'D': D,
            'cumulative_skipped': cum_count,
            'instant_window_lo': max(D_LO, D - 10),
            'instant_window_hi': D,
            'instant_fraction': inst_fraction,
        })

    # Show every 100th
    for r in cumulative_rows[::10]:
        print(f"  D = {r['D']:4d}: cumulative = {r['cumulative_skipped']:4d}, "
              f"inst_fraction in [{r['instant_window_lo']:4d}, "
              f"{r['instant_window_hi']:4d}) = {r['instant_fraction']:.4f}")

    # ---- Fits ----
    print("\n" + "=" * 72)
    print("Fits to per-decade skip fraction")
    print("=" * 72)
    D_arr = np.array([r['midpoint'] for r in decade_rows])
    f_arr = np.array([r['skip_fraction'] for r in decade_rows])

    a1, rss1, adj1, pred1 = fit_inv_log(D_arr, f_arr)
    a2, rss2, adj2, pred2 = fit_inv_log2(D_arr, f_arr)
    (ab3), rss3, adj3, pred3 = fit_inv_log_blend(D_arr, f_arr)
    a3, b3 = ab3

    print(f"  Fit 1: f(D) = 1 - {a1:.4f}/log(D)   "
          f"RSS = {rss1:.6f}  adj_R² = {adj1:.4f}")
    print(f"  Fit 2: f(D) = 1 - {a2:.4f}/log²(D)  "
          f"RSS = {rss2:.6f}  adj_R² = {adj2:.4f}")
    print(f"  Fit 3: f(D) = 1 - {a3:.4f}/log(D) - {b3:.4f}/log²(D)  "
          f"RSS = {rss3:.6f}  adj_R² = {adj3:.4f}")

    # ---- Plot ----
    print("\n" + "=" * 72)
    print("Generating chart")
    print("=" * 72)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not available; skipping chart.")
        plt = None

    if plt is not None:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9))

        # --- Panel A: skip fraction vs D, with fits ---
        ax1.plot(D_arr, f_arr, 'o', color='#1f77b4', markersize=10,
                 label='per-decade skip fraction')
        D_smooth = np.linspace(D_arr[0], D_arr[-1], 200)
        ax1.plot(D_smooth, 1 - a1 / np.log(D_smooth),
                 '-', color='#ff7f0e',
                 label=f'fit 1: 1 − {a1:.3f}/log(D)  (adj R² = {adj1:.3f})')
        ax1.plot(D_smooth, 1 - a2 / (np.log(D_smooth) ** 2),
                 '--', color='#2ca02c',
                 label=f'fit 2: 1 − {a2:.3f}/log²(D)  (adj R² = {adj2:.3f})')
        ax1.plot(D_smooth,
                 1 - a3 / np.log(D_smooth) - b3 / (np.log(D_smooth) ** 2),
                 ':', color='#d62728',
                 label=f'fit 3: blend, a = {a3:.3f}, b = {b3:.3f}  '
                       f'(adj R² = {adj3:.3f})')
        ax1.axhline(1.0, color='gray', linestyle=':', alpha=0.5)
        ax1.set_xlabel('digit-length D (bin midpoint)')
        ax1.set_ylabel('skip fraction in decade')
        ax1.set_title('Density of combined-skip digit-lengths vs D '
                      '(D ∈ [60, 1000])')
        ax1.set_ylim(-0.05, 1.10)
        ax1.legend(loc='lower right', fontsize=9)
        ax1.grid(True, alpha=0.3)

        # --- Panel B: cluster count + mean cluster width ---
        cl_count = np.array([r['n_clusters_starting'] for r in decade_rows])
        mw = np.array([r['mean_cluster_width'] for r in decade_rows])
        ax2.bar(D_arr, cl_count, width=80, color='#1f77b4', alpha=0.7,
                label='clusters starting in decade')
        ax2.set_xlabel('digit-length D (bin midpoint)')
        ax2.set_ylabel('clusters starting in decade', color='#1f77b4')
        ax2.tick_params(axis='y', labelcolor='#1f77b4')
        ax2.grid(True, alpha=0.3)
        ax2.set_title('Cluster count and mean cluster width per decade')

        # Twin axis: mean cluster width
        ax2b = ax2.twinx()
        # Use log scale to make the merged-regime cluster width visible
        # alongside the small ones
        mw_finite = np.where(np.isnan(mw), 0, mw)
        ax2b.plot(D_arr, mw_finite, 'o-', color='#d62728',
                  markersize=8, label='mean cluster width (log scale)')
        ax2b.set_yscale('symlog')
        ax2b.set_ylabel('mean cluster width [log]', color='#d62728')
        ax2b.tick_params(axis='y', labelcolor='#d62728')

        # Combine legends
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2b.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right',
                   fontsize=9)

        fig.suptitle('Paper 3 v4.5 Task 4 — density of skipped '
                     'digit-lengths across [60, 1000]\n'
                     f'(N_MAX = {N_MAX}; 23-cluster strict-anchor '
                     f'preserved; merged-regime edge anchor preserved)',
                     fontsize=10)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(PNG_OUT, dpi=120)
        plt.close(fig)
        print(f"  Saved: {PNG_OUT}")

    # ---- Write CSVs ----
    fieldnames_dec = ['bin_lo', 'bin_hi', 'bin_width', 'midpoint',
                      'n_skipped', 'skip_fraction',
                      'n_clusters_starting', 'mean_cluster_width']
    with open(CSV_DECADE, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames_dec)
        w.writeheader()
        for r in decade_rows:
            w.writerow(r)
    print(f"  Saved: {CSV_DECADE}")

    fieldnames_cum = ['D', 'cumulative_skipped',
                      'instant_window_lo', 'instant_window_hi',
                      'instant_fraction']
    with open(CSV_CUMULATIVE, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames_cum)
        w.writeheader()
        for r in cumulative_rows:
            w.writerow(r)
    print(f"  Saved: {CSV_CUMULATIVE}")

    # ---- Summary markdown ----
    write_summary(decade_rows, cumulative_rows,
                  (a1, rss1, adj1),
                  (a2, rss2, adj2),
                  (a3, b3, rss3, adj3),
                  merged_edge[0])
    print(f"  Saved: {MD_OUT}")

    # ---- Final status ----
    print("\n" + "=" * 72)
    print("TASK 4 — STATUS")
    print("=" * 72)
    print(f"Anchor verification: PASS")
    print(f"  N_MAX = {N_MAX}; strict-23 [90, 200] anchor: OK")
    print(f"  merged-regime cluster: {merged_edge[0]} (vs (172, 482) at "
          f"N_MAX = 250; expected to extend)")
    print(f"Per-decade skip fractions: "
          + ", ".join(f"[{r['bin_lo']}-{r['bin_hi']}]={r['skip_fraction']:.3f}"
                       for r in decade_rows))
    print(f"Fits (adj R²): inv-log = {adj1:.4f}, inv-log² = {adj2:.4f}, "
          f"blend = {adj3:.4f}")
    print(f"Files produced:")
    print(f"  {CSV_DECADE}")
    print(f"  {CSV_CUMULATIVE}")
    print(f"  {PNG_OUT}")
    print(f"  {MD_OUT}")
    print("\nEnd-of-task: PASS")


def write_summary(decade_rows, cumulative_rows,
                  fit1, fit2, fit3, merged_edge_cluster):
    a1, rss1, adj1 = fit1
    a2, rss2, adj2 = fit2
    a3, b3, rss3, adj3 = fit3
    with open(MD_OUT, 'w', encoding='utf-8') as f:
        f.write("# Task 4 — density of skipped digit-lengths [60, 1000]: "
                "summary\n\n")
        f.write(f"**Date:** 11 May 2026.\n")
        f.write(f"**Pre-registration:** `v3_12_data/briefs/"
                f"task4_density_measurement_pre_registration.md`.\n\n")
        f.write(f"## Anchors\n\n")
        f.write(f"- Strict-23 [90, 200] cluster count under "
                f"N_MAX = {N_MAX}: **OK**.\n")
        f.write(f"- Merged-regime cluster lower edge = 172: **OK**. "
                f"Cluster at N_MAX = {N_MAX} is "
                f"`{merged_edge_cluster}` (was `(172, 482)` at N_MAX = "
                f"250). Skip-set monotonicity preserved.\n\n")
        f.write(f"## Per-decade skip statistics\n\n")
        f.write("| Bin | Width | Skipped d's | Fraction | "
                "Clusters starting | Mean cluster width |\n")
        f.write("|-----|-------|-------------|----------|"
                "-------------------|--------------------|\n")
        for r in decade_rows:
            mw = (f"{r['mean_cluster_width']:.2f}"
                  if not math.isnan(r['mean_cluster_width']) else "—")
            f.write(f"| [{r['bin_lo']}, {r['bin_hi']}) | "
                    f"{r['bin_width']} | "
                    f"{r['n_skipped']} | {r['skip_fraction']:.4f} | "
                    f"{r['n_clusters_starting']} | {mw} |\n")
        f.write("\n")
        f.write(f"## Asymptotic-form fits to skip fraction\n\n")
        f.write("| Form | Parameter(s) | RSS | adj R² |\n")
        f.write("|------|--------------|-----|--------|\n")
        f.write(f"| `1 − a/log(D)` | a = {a1:.4f} | "
                f"{rss1:.6f} | {adj1:.4f} |\n")
        f.write(f"| `1 − a/log²(D)` | a = {a2:.4f} | "
                f"{rss2:.6f} | {adj2:.4f} |\n")
        f.write(f"| `1 − a/log(D) − b/log²(D)` | "
                f"a = {a3:.4f}, b = {b3:.4f} | "
                f"{rss3:.6f} | {adj3:.4f} |\n")
        f.write("\n")
        f.write(f"## Chart\n\n")
        f.write(f"`v3_12_data/results/task4_density_measurement.png` — "
                f"two-panel figure:\n\n")
        f.write(f"- Panel A: per-decade skip fraction vs bin midpoint D, "
                f"with three fit overlays.\n")
        f.write(f"- Panel B: cluster count starting in decade, with mean "
                f"cluster width (log scale, twin-y) overlaid.\n\n")
        f.write(f"## Cumulative skip count\n\n")
        f.write(f"At D = 60 (start): 0 skipped.\n")
        f.write(f"At D = 100: {cumulative_rows[4]['cumulative_skipped']} "
                f"skipped of 40 in [60, 100).\n")
        f.write(f"At D = 200: "
                f"{cumulative_rows[14]['cumulative_skipped']} "
                f"skipped of 140 in [60, 200).\n")
        f.write(f"At D = 500: "
                f"{cumulative_rows[44]['cumulative_skipped']} "
                f"skipped of 440 in [60, 500).\n")
        f.write(f"At D = 1000: "
                f"{cumulative_rows[-1]['cumulative_skipped']} "
                f"skipped of 940 in [60, 1000).\n\n")
        f.write(f"Full cumulative trace at every 10th D in "
                f"`task4_density_measurement_cumulative.csv`.\n\n")
        # Structural observations are data-dependent and authored by
        # Mr Code after reading the actual run output; the script writes
        # facts only here (per CinC's "no narrative, exact-figure
        # outputs only" discipline reminder).  See the run-specific
        # interpretation section appended manually to this summary
        # markdown.
        f.write(f"## Structural observations\n\n")
        f.write(f"(Authored by Mr Code post-run based on the data above; "
                f"the script writes facts only.  See the run report or "
                f"the in-place edits to this file for the structural "
                f"reading.)\n\n")
        f.write("🐕☕⬡\n\n")
        f.write("— Mr Code, 11 May 2026 (Paper 3 v4.5 Task 4)\n")


if __name__ == '__main__':
    main()
