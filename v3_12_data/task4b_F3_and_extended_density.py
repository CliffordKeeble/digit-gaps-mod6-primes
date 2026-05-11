#!/usr/bin/env python3
"""Paper 3 v4.5 Task 4b — F3 formal test + extended density [60, ~3000].

Per pre-registration `v3_12_data/briefs/
task4b_F3_and_extended_density_pre_registration.md`.

Three layers:

  Layer 1 (binding): F3 merged-regime supersession.
    Measure X = upper edge of cluster containing d = 172.
    Compare to v4.2 = 482, 10% threshold = 513, F3-trigger = 600.

  Layer 2 (exploratory): §8 Q5 second-merged-regime detection.
    Detect clusters in [200, D_HI] with width ≥ 100 and bounded edges.

  Layer 3 (exploratory): §8 Q4 asymptotic-form refinement.
    Three fits on extended per-decade skip fraction.

Outputs:
  v3_12_data/results/task4b_F3_test_results.md
  v3_12_data/results/task4b_extended_density_per_decade.csv
  v3_12_data/results/task4b_merged_regimes_detected.csv
  v3_12_data/results/task4b_density_measurement.png
  v3_12_data/results/task4b_summary.md
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
F3_OUT = os.path.join(RESULTS_DIR, 'task4b_F3_test_results.md')
CSV_DECADE = os.path.join(RESULTS_DIR,
                          'task4b_extended_density_per_decade.csv')
CSV_MERGED = os.path.join(RESULTS_DIR,
                          'task4b_merged_regimes_detected.csv')
PNG_OUT = os.path.join(RESULTS_DIR, 'task4b_density_measurement.png')
MD_OUT = os.path.join(RESULTS_DIR, 'task4b_summary.md')

SIEVE_LIMIT = 200_000
N_MAX = 1000
D_LO = 60
F3_TRIGGER = 600
F3_TEN_PCT = 513
F3_BASELINE = 482

Q5_MIN_LO = 200
Q5_MIN_WIDTH = 100

Q4_SUBSTANTIVE_R2 = 0.5


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
    y = 1.0 - f_arr
    x = 1.0 / np.log(D_arr)
    a = np.sum(x * y) / np.sum(x * x)
    pred = 1.0 - a / np.log(D_arr)
    rss = np.sum((f_arr - pred) ** 2)
    tss = np.sum((f_arr - np.mean(f_arr)) ** 2)
    n = len(f_arr)
    adj = (1 - (rss / max(1, n - 1)) / (tss / max(1, n - 1))
           if tss > 0 else 1.0)
    return a, rss, adj


def fit_inv_log2(D_arr, f_arr):
    y = 1.0 - f_arr
    x = 1.0 / (np.log(D_arr) ** 2)
    a = np.sum(x * y) / np.sum(x * x)
    pred = 1.0 - a / (np.log(D_arr) ** 2)
    rss = np.sum((f_arr - pred) ** 2)
    tss = np.sum((f_arr - np.mean(f_arr)) ** 2)
    n = len(f_arr)
    adj = (1 - (rss / max(1, n - 1)) / (tss / max(1, n - 1))
           if tss > 0 else 1.0)
    return a, rss, adj


def fit_inv_log_blend(D_arr, f_arr):
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
    adj = (1 - (rss / max(1, n - p)) / (tss / max(1, n - 1))
           if tss > 0 else 1.0)
    return (a, b), rss, adj


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Sieving primes up to {SIEVE_LIMIT}; taking N_MAX = {N_MAX}...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    D5 = compute_D(p5, N_MAX)
    D7 = compute_D(p7, N_MAX)
    print(f"  5-series: D_5({N_MAX}) = {D5[-1]}")
    print(f"  7-series: D_7({N_MAX}) = {D7[-1]}")

    # ---- Determine analysis range D_HI ----
    D_HI = (min(D5[-1], D7[-1]) - 50) // 100 * 100
    if D_HI < 2000:
        print(f"  HALT: D_HI = {D_HI} < 2000 (insufficient extension over "
              f"Task 4's 1000).")
        sys.exit(1)
    print(f"  Analysis range: [{D_LO}, {D_HI})")

    # ---- Skip sets and clusters ----
    skip5 = collect_skip_set(D5)
    skip7 = collect_skip_set(D7)
    skip_combined = skip5 | skip7
    skip_sorted = sorted(skip_combined)
    clusters_full = cluster_contiguous(skip_sorted)
    print(f"\n  Combined skip-set size (all D): {len(skip_combined)}")
    print(f"  Combined clusters (all D): {len(clusters_full)}")

    # ---- Anchor verification ----
    print("\n" + "=" * 72)
    print("Anchor verification")
    print("=" * 72)
    strict_90_200 = [c for c in clusters_full if 90 <= c[0] and c[1] <= 200]
    print(f"  Strict-23 [90, 200] count: {len(strict_90_200)} "
          f"(want 23)  {'OK' if len(strict_90_200) == 23 else 'FAIL'}")
    if len(strict_90_200) != 23:
        sys.exit(1)
    cluster_with_172 = [c for c in clusters_full if c[0] == 172]
    print(f"  Cluster with lower edge 172 exists: "
          f"{'OK' if cluster_with_172 else 'FAIL'}")
    if not cluster_with_172:
        sys.exit(1)
    X = cluster_with_172[0][1]
    print(f"  Cluster (172, X) measured at N_MAX = {N_MAX}: "
          f"(172, {X})")
    if X < F3_BASELINE:
        print(f"  HALT: X = {X} < {F3_BASELINE} (skip-monotonicity violated; "
              f"impossible if script is correct).")
        sys.exit(1)
    print(f"  Skip-monotonicity: X = {X} ≥ {F3_BASELINE}  OK")

    # ---- F3 formal test ----
    print("\n" + "=" * 72)
    print("Layer 1 — F3 formal test (binding)")
    print("=" * 72)
    print(f"  Measurement: cluster (172, X) at N_MAX = {N_MAX}, "
          f"X = {X}")
    print(f"  Baseline (v4.2): X_v4.2 = {F3_BASELINE}")
    print(f"  10% growth threshold: {F3_TEN_PCT}")
    print(f"  F3 binding trigger: {F3_TRIGGER}")
    if X <= F3_BASELINE:
        f3_outcome = 'α-F3'
        f3_verdict = ('null holds — (172, 482) bounded; no extension. '
                      'F3 does not fire.')
    elif X <= F3_TRIGGER:
        f3_outcome = 'β-F3'
        f3_verdict = ('between-zone — surprise; Task 4 forecloses this; '
                      'HALT and consult CinC.')
    else:
        f3_outcome = 'γ-F3'
        f3_verdict = ('F3 fires — merged-regime supersession; '
                      'Retraction 4 indicated.')
    growth_abs = X - F3_BASELINE
    growth_pct = 100 * (X - F3_BASELINE) / (F3_BASELINE - 172)
    print(f"  Growth (absolute): {growth_abs} (from baseline 310)")
    print(f"  Growth (pct of baseline width): {growth_pct:.1f}%")
    print(f"  F3 outcome: ({f3_outcome})")
    print(f"  Verdict: {f3_verdict}")

    if f3_outcome == 'β-F3':
        print("\n  HALT (Pattern 75): F3 between-zone is a major surprise; "
              "Task 4 forecloses it.")
        # Continue computation to surface the surprise; do NOT short-circuit
        # additional work — write everything out so CinC has full data.

    # ---- Layer 2 — §8 Q5: bounded merged regime detection ----
    print("\n" + "=" * 72)
    print(f"Layer 2 — §8 Q5: bounded merged regime detection "
          f"(d_lo ≥ {Q5_MIN_LO}, width ≥ {Q5_MIN_WIDTH})")
    print("=" * 72)

    bounded_regimes = []
    for c in clusters_full:
        lo, hi = c
        width = hi - lo + 1
        if lo < Q5_MIN_LO:
            continue
        if width < Q5_MIN_WIDTH:
            continue
        if hi > D_HI:
            # Cluster extends past analysis range — record but flag
            past_range = True
        else:
            past_range = False
        # Bounded edges: lo - 1 is landed (not in skip), hi + 1 is landed
        lower_bounded = (lo - 1) not in skip_combined
        upper_bounded = (hi + 1) not in skip_combined
        bounded_regimes.append({
            'lower_edge': lo,
            'upper_edge': hi,
            'width': width,
            'lower_bounded': lower_bounded,
            'upper_bounded': upper_bounded,
            'past_range': past_range,
        })
    n_bounded = len(bounded_regimes)
    print(f"  Bounded merged regimes detected in [{Q5_MIN_LO}, "
          f"{D_HI}]: {n_bounded}")
    for r in bounded_regimes:
        flag = ''
        if not r['lower_bounded']:
            flag += ' [lower not bounded]'
        if not r['upper_bounded']:
            flag += ' [upper not bounded]'
        if r['past_range']:
            flag += ' [upper past analysis range]'
        print(f"    ({r['lower_edge']}, {r['upper_edge']}) width "
              f"{r['width']}{flag}")

    if n_bounded == 0:
        q5_outcome = 'α-Q5'
        q5_verdict = ('no second bounded merged regime detected; '
                      '(172, 482) is structurally isolated in tested '
                      'range; quasi-periodic-alternation hypothesis '
                      'weakened.')
    else:
        q5_outcome = 'β-Q5'
        q5_verdict = (f'{n_bounded} bounded merged regime(s) detected; '
                      'quasi-periodic structure empirically anchored at '
                      'multiple instances.')
    print(f"  Q5 outcome: ({q5_outcome})")
    print(f"  Verdict: {q5_verdict}")

    # Q5 surprise check: > 5 regimes or any width ≥ 500 unbounded
    q5_halt = False
    if n_bounded > 5:
        print(f"  WARNING: > 5 bounded merged regimes detected — "
              "potential structural surprise.")
        q5_halt = True
    for r in bounded_regimes:
        if r['width'] >= 500 and not (r['lower_bounded']
                                      and r['upper_bounded']):
            print(f"  WARNING: regime ({r['lower_edge']}, "
                  f"{r['upper_edge']}) has width ≥ 500 and is not "
                  "fully bounded.")
            q5_halt = True

    # ---- Per-decade table ----
    print("\n" + "=" * 72)
    print(f"Per-decade analysis (bins of width 100; [60, 100) first)")
    print("=" * 72)
    bin_edges = [60, 100]
    while bin_edges[-1] < D_HI:
        bin_edges.append(bin_edges[-1] + 100)
    decade_rows = []
    for i in range(len(bin_edges) - 1):
        lo = bin_edges[i]
        hi = bin_edges[i + 1]
        width = hi - lo
        midpoint = (lo + hi) / 2
        n_skipped = sum(1 for d in skip_sorted if lo <= d < hi)
        skip_fraction = n_skipped / width
        clusters_starting = [c for c in clusters_full
                              if lo <= c[0] < hi]
        n_clusters = len(clusters_starting)
        if clusters_starting:
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

    # Display every 5th
    for r in decade_rows:
        mw = (f"{r['mean_cluster_width']:7.2f}"
              if not math.isnan(r['mean_cluster_width']) else "    n/a")
        print(f"  [{r['bin_lo']:4d}, {r['bin_hi']:4d}) skipped "
              f"{r['n_skipped']:4d}/{r['bin_width']:<3d}  "
              f"frac = {r['skip_fraction']:.4f}  "
              f"clusters_starting = {r['n_clusters_starting']:3d}  "
              f"mean_width = {mw}")

    # ---- Layer 3 — §8 Q4 asymptotic-form refinement ----
    print("\n" + "=" * 72)
    print("Layer 3 — §8 Q4: asymptotic-form refinement at extended range")
    print("=" * 72)
    D_arr = np.array([r['midpoint'] for r in decade_rows])
    f_arr = np.array([r['skip_fraction'] for r in decade_rows])
    a1, rss1, adj1 = fit_inv_log(D_arr, f_arr)
    a2, rss2, adj2 = fit_inv_log2(D_arr, f_arr)
    (ab3), rss3, adj3 = fit_inv_log_blend(D_arr, f_arr)
    a3, b3 = ab3
    print(f"  Fit 1: 1 − {a1:.4f}/log(D)         "
          f"adj R² = {adj1:.4f}")
    print(f"  Fit 2: 1 − {a2:.4f}/log²(D)        "
          f"adj R² = {adj2:.4f}")
    print(f"  Fit 3: 1 − {a3:.4f}/log(D) − {b3:.4f}/log²(D)  "
          f"adj R² = {adj3:.4f}")

    best_adj = max(adj1, adj2, adj3)
    q4_substantive = best_adj >= Q4_SUBSTANTIVE_R2
    if q4_substantive:
        q4_verdict = (f'substantive improvement reached (best adj R² = '
                      f'{best_adj:.4f} ≥ {Q4_SUBSTANTIVE_R2}); evidence '
                      'asymptotic form holds at larger scales.')
    else:
        q4_verdict = (f'no substantive improvement (best adj R² = '
                      f'{best_adj:.4f} < {Q4_SUBSTANTIVE_R2}); '
                      'structural non-monotonicity persists at larger '
                      'scales.')
    print(f"  Q4 verdict: {q4_verdict}")

    # ---- Plot ----
    print("\n" + "=" * 72)
    print("Generating chart")
    print("=" * 72)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        plt = None

    if plt is not None:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9))
        # Panel A: skip fraction + fits
        ax1.plot(D_arr, f_arr, 'o', color='#1f77b4', markersize=6,
                 label=f'per-decade skip fraction (n = {len(D_arr)})')
        D_smooth = np.linspace(D_arr[0], D_arr[-1], 400)
        ax1.plot(D_smooth, 1 - a1 / np.log(D_smooth),
                 '-', color='#ff7f0e',
                 label=f'fit 1: 1 − {a1:.3f}/log(D)  '
                       f'(adj R² = {adj1:.3f})')
        ax1.plot(D_smooth, 1 - a2 / (np.log(D_smooth) ** 2),
                 '--', color='#2ca02c',
                 label=f'fit 2: 1 − {a2:.3f}/log²(D)  '
                       f'(adj R² = {adj2:.3f})')
        ax1.plot(D_smooth,
                 1 - a3 / np.log(D_smooth) - b3 / (np.log(D_smooth) ** 2),
                 ':', color='#d62728',
                 label=f'fit 3: blend, a={a3:.3f}, b={b3:.3f}  '
                       f'(adj R² = {adj3:.3f})')
        ax1.axhline(1.0, color='gray', linestyle=':', alpha=0.5)
        ax1.set_xlabel('digit-length D (bin midpoint)')
        ax1.set_ylabel('skip fraction in decade')
        ax1.set_title(f'Density of combined-skip digit-lengths vs D '
                      f'(D ∈ [{D_LO}, {D_HI}); N_MAX = {N_MAX})')
        ax1.set_ylim(-0.05, 1.10)
        ax1.legend(loc='lower right', fontsize=9)
        ax1.grid(True, alpha=0.3)

        # Panel B: clusters + mean width
        cl_count = np.array([r['n_clusters_starting'] for r in decade_rows])
        mw = np.array([r['mean_cluster_width'] for r in decade_rows])
        ax2.bar(D_arr, cl_count, width=80, color='#1f77b4', alpha=0.7,
                label='clusters starting in decade')
        ax2.set_xlabel('digit-length D (bin midpoint)')
        ax2.set_ylabel('clusters starting in decade', color='#1f77b4')
        ax2.tick_params(axis='y', labelcolor='#1f77b4')
        ax2.grid(True, alpha=0.3)
        ax2.set_title('Cluster count and mean cluster width per decade')
        ax2b = ax2.twinx()
        mw_finite = np.where(np.isnan(mw), 0, mw)
        ax2b.plot(D_arr, mw_finite, 'o-', color='#d62728',
                  markersize=6, label='mean cluster width (symlog)')
        ax2b.set_yscale('symlog')
        ax2b.set_ylabel('mean cluster width [symlog]', color='#d62728')
        ax2b.tick_params(axis='y', labelcolor='#d62728')
        # Mark detected bounded merged regimes
        for r in bounded_regimes:
            ax1.axvspan(r['lower_edge'], r['upper_edge'],
                        alpha=0.15, color='purple')
            ax2.axvspan(r['lower_edge'], r['upper_edge'],
                        alpha=0.15, color='purple')

        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2b.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2,
                   loc='upper right', fontsize=9)

        fig.suptitle(f'Paper 3 v4.5 Task 4b — F3 test (X = {X}) + '
                     f'extended density [60, {D_HI})\n'
                     f'F3 outcome ({f3_outcome}); Q5 outcome ({q5_outcome}); '
                     f'best adj R² = {best_adj:.4f}',
                     fontsize=10)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(PNG_OUT, dpi=120)
        plt.close(fig)
        print(f"  Saved: {PNG_OUT}")

    # ---- Write CSVs ----
    fn_dec = ['bin_lo', 'bin_hi', 'bin_width', 'midpoint',
              'n_skipped', 'skip_fraction',
              'n_clusters_starting', 'mean_cluster_width']
    with open(CSV_DECADE, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fn_dec)
        w.writeheader()
        for r in decade_rows:
            w.writerow(r)
    print(f"  Saved: {CSV_DECADE}")

    fn_mer = ['lower_edge', 'upper_edge', 'width',
              'lower_bounded', 'upper_bounded', 'past_range']
    with open(CSV_MERGED, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fn_mer)
        w.writeheader()
        for r in bounded_regimes:
            w.writerow(r)
    print(f"  Saved: {CSV_MERGED}")

    # ---- F3 results markdown ----
    with open(F3_OUT, 'w', encoding='utf-8') as f:
        f.write("# Task 4b — F3 formal test result\n\n")
        f.write(f"**Date:** 11 May 2026.\n\n")
        f.write(f"**Measurement:** cluster containing d = 172 at "
                f"N_MAX = {N_MAX} is `(172, {X})`.\n\n")
        f.write(f"| Quantity | Value |\n|---|---|\n")
        f.write(f"| X (upper edge) | {X} |\n")
        f.write(f"| Baseline (v4.2 / Task 4) | {F3_BASELINE} |\n")
        f.write(f"| Growth (absolute) | {growth_abs} |\n")
        f.write(f"| Growth (% of v4.2 width = 310) | "
                f"{growth_pct:.1f}% |\n")
        f.write(f"| 10% threshold | {F3_TEN_PCT} |\n")
        f.write(f"| F3 binding trigger | > {F3_TRIGGER} |\n\n")
        f.write(f"**Outcome: ({f3_outcome})**.  {f3_verdict}\n")
    print(f"  Saved: {F3_OUT}")

    # ---- Combined summary markdown (fact-only) ----
    with open(MD_OUT, 'w', encoding='utf-8') as f:
        f.write("# Task 4b — F3 formal test + extended density: summary\n\n")
        f.write(f"**Date:** 11 May 2026.\n")
        f.write(f"**Pre-registration:** `v3_12_data/briefs/"
                f"task4b_F3_and_extended_density_pre_registration.md`.\n")
        f.write(f"**N_MAX:** {N_MAX}. **Analysis range:** "
                f"[{D_LO}, {D_HI}).\n\n")
        f.write(f"## Anchors\n\n")
        f.write(f"- Strict-23 [90, 200] cluster count: OK ({len(strict_90_200)}).\n")
        f.write(f"- Cluster (172, X): X = {X}; "
                f"skip-monotonicity X ≥ {F3_BASELINE}: OK.\n\n")
        f.write(f"## Layer 1 — F3 formal test\n\n")
        f.write(f"X = {X}. Growth = {growth_abs} ({growth_pct:.1f}% of "
                f"v4.2 width).\n\n")
        f.write(f"**Outcome: ({f3_outcome})**.  {f3_verdict}\n\n")
        f.write(f"## Layer 2 — §8 Q5 bounded merged regime detection\n\n")
        f.write(f"Detection criteria: d_lo ≥ {Q5_MIN_LO}, "
                f"width ≥ {Q5_MIN_WIDTH}, bounded edges.\n\n")
        f.write(f"**{n_bounded} bounded merged regime(s) detected.**\n\n")
        if bounded_regimes:
            f.write("| Lower edge | Upper edge | Width | Lower bounded | "
                    "Upper bounded | Past analysis range |\n")
            f.write("|---|---|---|---|---|---|\n")
            for r in bounded_regimes:
                f.write(f"| {r['lower_edge']} | {r['upper_edge']} | "
                        f"{r['width']} | "
                        f"{'yes' if r['lower_bounded'] else 'NO'} | "
                        f"{'yes' if r['upper_bounded'] else 'NO'} | "
                        f"{'yes' if r['past_range'] else 'no'} |\n")
        f.write(f"\n**Outcome: ({q5_outcome})**.  {q5_verdict}\n\n")
        f.write(f"## Layer 3 — §8 Q4 asymptotic-form refinement\n\n")
        f.write(f"Re-fit on extended decade table "
                f"(n = {len(D_arr)} bins).\n\n")
        f.write("| Form | Parameter(s) | adj R² |\n")
        f.write("|---|---|---|\n")
        f.write(f"| 1 − a/log(D) | a = {a1:.4f} | {adj1:.4f} |\n")
        f.write(f"| 1 − a/log²(D) | a = {a2:.4f} | {adj2:.4f} |\n")
        f.write(f"| 1 − a/log(D) − b/log²(D) | "
                f"a = {a3:.4f}, b = {b3:.4f} | {adj3:.4f} |\n\n")
        f.write(f"Pre-registered substantive-improvement threshold: "
                f"adj R² ≥ {Q4_SUBSTANTIVE_R2}.\n\n")
        f.write(f"**Q4 verdict:** {q4_verdict}\n\n")
        f.write(f"## Per-decade table\n\n")
        f.write("| Bin | Width | Skipped | Fraction | Clusters starting | "
                "Mean width |\n")
        f.write("|-----|-------|---------|----------|-------------------|"
                "------------|\n")
        for r in decade_rows:
            mw = (f"{r['mean_cluster_width']:.2f}"
                  if not math.isnan(r['mean_cluster_width']) else "—")
            f.write(f"| [{r['bin_lo']}, {r['bin_hi']}) | "
                    f"{r['bin_width']} | {r['n_skipped']} | "
                    f"{r['skip_fraction']:.4f} | "
                    f"{r['n_clusters_starting']} | {mw} |\n")
        f.write(f"\n## Structural observations\n\n")
        f.write(f"(Authored by Mr Code post-run based on the data above; "
                f"the script writes facts only.  See the run report for "
                f"the structural reading.)\n\n")
        f.write("🐕☕⬡\n\n")
        f.write("— Mr Code, 11 May 2026 (Paper 3 v4.5 Task 4b)\n")
    print(f"  Saved: {MD_OUT}")

    # ---- Final status ----
    print("\n" + "=" * 72)
    print("TASK 4b — STATUS")
    print("=" * 72)
    print(f"F3 outcome: ({f3_outcome})  — X = {X}")
    print(f"Q5 outcome: ({q5_outcome})  — {n_bounded} bounded regimes")
    print(f"Q4 verdict: best adj R² = {best_adj:.4f} "
          f"({'≥' if q4_substantive else '<'} {Q4_SUBSTANTIVE_R2})")
    print(f"Files produced:")
    print(f"  {F3_OUT}")
    print(f"  {CSV_DECADE}")
    print(f"  {CSV_MERGED}")
    print(f"  {PNG_OUT}")
    print(f"  {MD_OUT}")
    if f3_outcome == 'β-F3' or q5_halt:
        print(f"\nEnd-of-task: PASS with surprises — see flags above.")
    else:
        print(f"\nEnd-of-task: PASS")


if __name__ == '__main__':
    main()
