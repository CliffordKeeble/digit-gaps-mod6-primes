#!/usr/bin/env python3
"""Paper 3 v5.x Task 5 — Instance-4 doubling-pattern test.

Per pre-registration `v3_12_data/briefs/
task5_instance_4_doubling_pre_registration.md`.

Three layers:

  Layer 0 (Pattern 75 anchor verification at N_MAX = 4000):
    strict-23 [90, 200]; (172, 482); (952, 1717).
  Layer 1 (measurement, precondition): complete instance-3 upper edge
    (Task 4b had it truncated at D_HI = 3600).
  Layer 2 (BINDING): instance-4 detection + width/gap ratio test
    against ≈ 2.3× with 10% windows [2.07, 2.53].
  Layer 3 (exploratory): three asymptotic fits at extended range.

Auxiliary: per-regime upper-edge landing-series (5 or 7) record.

Outputs:
  v3_12_data/results/task5_instance_4_doubling_per_decade.csv
  v3_12_data/results/task5_merged_regimes_detected.csv
  v3_12_data/results/task5_density_measurement.png
  v3_12_data/results/task5_summary.md
"""
import os
import sys
import csv
import math

import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Python 3.11+ default int-to-str conversion cap is 4300 digits; at
# N_MAX = 4000 our running products reach ~14000 digits. Disable the
# cap (0 = unlimited) — we only use str() for length measurement.
sys.set_int_max_str_digits(0)

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve

HERE = os.path.dirname(__file__)
RESULTS_DIR = os.path.join(HERE, 'results')
CSV_DECADE = os.path.join(RESULTS_DIR,
                          'task5_instance_4_doubling_per_decade.csv')
CSV_MERGED = os.path.join(RESULTS_DIR,
                          'task5_merged_regimes_detected.csv')
PNG_OUT = os.path.join(RESULTS_DIR, 'task5_density_measurement.png')
MD_OUT = os.path.join(RESULTS_DIR, 'task5_summary.md')

SIEVE_LIMIT = 200_000
N_MAX = 4000
D_LO = 60

Q5_MIN_LO = 200
Q5_MIN_WIDTH = 100

# Doubling-pattern test windows (binding, per pre-registration)
RATIO_TARGET = 2.3
RATIO_LO = 2.07   # 0.9 × 2.3
RATIO_HI = 2.53   # 1.1 × 2.3

Q4_SUBSTANTIVE_R2 = 0.5

# Reference values from v4.9 / Task 4b
INSTANCE_1 = (172, 482)   # width 311
INSTANCE_2 = (952, 1717)  # width 766
INSTANCE_2_GAP = 469       # gap(1→2) = 952 − 482 − 1
INSTANCE_3_LO = 2812       # truncated upper at Task 4b
INSTANCE_3_GAP_2_TO_3 = 1094  # gap(2→3) = 2812 − 1717 − 1


def compute_D_and_landings(series, n_max):
    """Return (D, landing_n_for_d) using mpmath log10-sum.

      D[i] = digit-length of product of first (i+1) primes;
      landing_n_for_d[d] = smallest 1-indexed n such that D[n-1] = d
                          (or absent if d never landed on within N_MAX).

    Implementation: maintain running log10 of product as an mpmath mpf
    at 50 dps; digit count = floor(log10) + 1. Avoids O(n²) str() on
    14000-digit integers. Correct because Π_i is never a power of 10
    (Π_5 contains a single factor of 5, no factor of 2; Π_7 contains
    no factor of 2 or 5), so log10(Π_i(n)) is irrational and never
    within 10⁻⁵⁰ of an integer at the scale we're operating in.
    """
    import mpmath
    mpmath.mp.dps = 50
    D = []
    landing_n_for_d = {}
    log10_prod = mpmath.mpf(0)
    for i, p in enumerate(series[:n_max]):
        log10_prod += mpmath.log10(mpmath.mpf(p))
        d = int(mpmath.floor(log10_prod)) + 1
        D.append(d)
        if d not in landing_n_for_d:
            landing_n_for_d[d] = i + 1
    return D, landing_n_for_d


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
    assert len(p5) >= N_MAX and len(p7) >= N_MAX, \
        f"Not enough primes for N_MAX = {N_MAX}"

    print(f"  Computing D_5 and D_7 (may take a couple of minutes at "
          f"N_MAX = {N_MAX})...")
    import time
    t0 = time.time()
    D5, landings5 = compute_D_and_landings(p5, N_MAX)
    print(f"    5-series done in {time.time() - t0:.1f}s; "
          f"D_5({N_MAX}) = {D5[-1]}")
    t0 = time.time()
    D7, landings7 = compute_D_and_landings(p7, N_MAX)
    print(f"    7-series done in {time.time() - t0:.1f}s; "
          f"D_7({N_MAX}) = {D7[-1]}")

    # ---- D_HI ----
    D_HI = (min(D5[-1], D7[-1]) - 50) // 100 * 100
    if D_HI < 5000:
        print(f"  HALT: D_HI = {D_HI} < 5000 (insufficient extension).")
        sys.exit(1)
    print(f"  Analysis range: [{D_LO}, {D_HI})")

    # ---- Skip sets ----
    skip5 = collect_skip_set(D5)
    skip7 = collect_skip_set(D7)
    skip_combined = skip5 | skip7
    skip_sorted = sorted(skip_combined)
    clusters_full = cluster_contiguous(skip_sorted)
    print(f"\n  Combined skip-set size (all D): {len(skip_combined)}")
    print(f"  Combined clusters (all D): {len(clusters_full)}")

    # ---- Layer 0 anchors ----
    print("\n" + "=" * 72)
    print("Layer 0 — Anchor verification (Pattern 75)")
    print("=" * 72)
    strict_90_200 = [c for c in clusters_full if 90 <= c[0] and c[1] <= 200]
    print(f"  Strict-23 [90, 200] count: {len(strict_90_200)} (want 23)  "
          f"{'OK' if len(strict_90_200) == 23 else 'FAIL'}")
    if len(strict_90_200) != 23:
        sys.exit(1)
    inst1 = [c for c in clusters_full if c[0] == 172]
    inst2 = [c for c in clusters_full if c[0] == 952]
    if not inst1 or inst1[0] != INSTANCE_1:
        print(f"  HALT: instance-1 anchor — found {inst1}, want "
              f"{INSTANCE_1}")
        sys.exit(1)
    print(f"  Instance 1 (172, 482): {inst1[0]}  OK")
    if not inst2 or inst2[0] != INSTANCE_2:
        print(f"  HALT: instance-2 anchor — found {inst2}, want "
              f"{INSTANCE_2}")
        sys.exit(1)
    print(f"  Instance 2 (952, 1717): {inst2[0]}  OK")

    # ---- Layer 1: instance-3 upper edge ----
    print("\n" + "=" * 72)
    print("Layer 1 — Instance-3 upper-edge measurement")
    print("=" * 72)
    inst3_clusters = [c for c in clusters_full
                       if c[0] <= INSTANCE_3_LO <= c[1]]
    if not inst3_clusters:
        print(f"  HALT: no cluster contains d = {INSTANCE_3_LO}.")
        sys.exit(1)
    inst3 = inst3_clusters[0]
    inst3_lo, inst3_hi = inst3
    inst3_width = inst3_hi - inst3_lo + 1
    # Check whether truncated by D_HI
    # Truncation = cluster's upper edge is at D_HI - 1 AND D_HI is in skip
    inst3_truncated = (inst3_hi == D_HI - 1 and D_HI in skip_combined)
    print(f"  Instance 3 cluster: {inst3}  width = {inst3_width}")
    if inst3_truncated:
        print(f"  TRUNCATED at D_HI = {D_HI} — Layer 1 fails to fix "
              f"upper edge")
    else:
        print(f"  Upper edge resolved: {inst3_hi} (D_HI = {D_HI} > "
              f"{inst3_hi}; clean measurement)")

    # ---- Bounded merged regime detection (run before Layer 2 verdict) ----
    print("\n" + "=" * 72)
    print(f"Bounded merged regime detection (d_lo ≥ {Q5_MIN_LO}, "
          f"width ≥ {Q5_MIN_WIDTH}, both edges bounded)")
    print("=" * 72)

    bounded_regimes = []
    for c in clusters_full:
        lo, hi = c
        width = hi - lo + 1
        if lo < Q5_MIN_LO:
            continue
        if width < Q5_MIN_WIDTH:
            continue
        past_range = (hi >= D_HI)
        # Bounded edges: lo - 1 and hi + 1 are NOT in skip set
        lower_bounded = (lo - 1) not in skip_combined
        upper_bounded = (hi + 1) not in skip_combined
        # Auxiliary: which series lands at hi + 1?
        landing_5 = landings5.get(hi + 1)
        landing_7 = landings7.get(hi + 1)
        if landing_5 is None and landing_7 is None:
            landing_series = 'neither'
            landing_first = None
        elif landing_5 is None:
            landing_series = '7'
            landing_first = '7'
        elif landing_7 is None:
            landing_series = '5'
            landing_first = '5'
        else:
            landing_series = 'both'
            # Compare by index — smaller n means landed at fewer primes
            landing_first = '5' if landing_5 < landing_7 else \
                            '7' if landing_7 < landing_5 else 'tied'
        bounded_regimes.append({
            'lower_edge': lo,
            'upper_edge': hi,
            'width': width,
            'lower_bounded': lower_bounded,
            'upper_bounded': upper_bounded,
            'past_range': past_range,
            'landing_5_n': landing_5,
            'landing_7_n': landing_7,
            'landing_series': landing_series,
            'landing_first': landing_first,
        })
    print(f"  Detected: {len(bounded_regimes)} bounded merged regime(s)")
    for r in bounded_regimes:
        flag = ''
        if not r['lower_bounded']:
            flag += ' [lower not bounded]'
        if not r['upper_bounded']:
            flag += ' [upper not bounded]'
        if r['past_range']:
            flag += ' [past D_HI]'
        print(f"    ({r['lower_edge']}, {r['upper_edge']}) width "
              f"{r['width']}; lands at hi+1: series {r['landing_series']}"
              f" (first={r['landing_first']}, n_5={r['landing_5_n']}, "
              f"n_7={r['landing_7_n']}){flag}")

    # ---- Layer 2: instance-4 detection + doubling-pattern test ----
    print("\n" + "=" * 72)
    print("Layer 2 — Instance-4 detection + doubling-pattern test (BINDING)")
    print("=" * 72)

    # Compose the full instance list (instance 1 + bounded_regimes).
    # Instance 1 (172, 482) is excluded by d_lo ≥ 200, so we prepend it.
    all_instances = [{'lower_edge': INSTANCE_1[0],
                      'upper_edge': INSTANCE_1[1],
                      'width': INSTANCE_1[1] - INSTANCE_1[0] + 1}]
    for r in bounded_regimes:
        all_instances.append(r)
    all_instances.sort(key=lambda r: r['lower_edge'])
    print(f"  Total instances (incl. instance 1): {len(all_instances)}")

    # Check Layer 1 outcome propagation
    if inst3_truncated:
        layer2_outcome = 'γ-no-instance-3-completion'
        layer2_verdict = (f'Layer 1 fails — instance 3 truncated at '
                          f'D_HI = {D_HI}. Implies width(3) ≥ '
                          f'{inst3_width}. '
                          f'Width-doubling at instance-2 → instance-3 '
                          f'would predict width(3) ∈ [2.07, 2.53] × 766 = '
                          f'[1586, 1939]. Outcome (γ-no-3-completion) '
                          f'fires per pre-reg.')
        instance_4 = None
        width_ratio = None
        gap_ratio = None
    else:
        # Find instance 4: next bounded regime after instance 3
        instance_4 = None
        for r in bounded_regimes:
            if r['lower_edge'] > inst3_hi:
                instance_4 = r
                break
        if instance_4 is None:
            # No instance 4 detected — γ-1 or γ-2
            # γ-1: D_HI - inst3_hi < predicted_min_gap = 0.9 × 2.3 × 1094 = 2264
            # γ-2: D_HI - inst3_hi >= predicted_max_gap = 1.1 × 2.3 × 1094 = 2768
            available_above = D_HI - inst3_hi
            print(f"  No instance 4 detected. Available D above "
                  f"instance 3 upper edge: {available_above}.")
            print(f"  Predicted gap-window: [2264, 2768].")
            if available_above < 2264:
                layer2_outcome = 'γ-1'
                layer2_verdict = (f'Out-of-range consistent with '
                                  f'gap-doubling: D_HI − inst3_hi = '
                                  f'{available_above} < 2264 (min '
                                  f'predicted gap). Doubling hypothesis '
                                  f'not refuted; Task 5b at higher '
                                  f'N_MAX warranted.')
            elif available_above >= 2768:
                layer2_outcome = 'γ-2'
                layer2_verdict = (f'Out-of-range refutes gap-doubling '
                                  f'in the accelerating direction: '
                                  f'D_HI − inst3_hi = {available_above} '
                                  f'≥ 2768 (max predicted gap), but no '
                                  f'instance 4 in range. Gap exceeds '
                                  f'2.3× × 1094.')
            else:
                # Between 2264 and 2768 — neither γ-1 nor γ-2 cleanly
                layer2_outcome = 'γ-between'
                layer2_verdict = (f'Available range {available_above} '
                                  f'∈ [2264, 2768] (within window) but '
                                  f'no instance 4 detected. Edge-case: '
                                  f'instance 4 may begin just at D_HI '
                                  f'or just past it; not in '
                                  f'pre-registered set — halting for '
                                  f'CinC.')
            width_ratio = None
            gap_ratio = None
        else:
            # Instance 4 detected
            inst4_lo, inst4_hi = (instance_4['lower_edge'],
                                  instance_4['upper_edge'])
            inst4_width = instance_4['width']
            inst4_truncated = instance_4['past_range']
            width_ratio = inst4_width / inst3_width
            gap_3_to_4 = inst4_lo - inst3_hi - 1
            gap_ratio = gap_3_to_4 / INSTANCE_3_GAP_2_TO_3
            print(f"  Instance 4 detected: ({inst4_lo}, {inst4_hi})  "
                  f"width = {inst4_width}{'  (TRUNCATED)' if inst4_truncated else ''}")
            print(f"  width(4) / width(3) = {inst4_width} / "
                  f"{inst3_width} = {width_ratio:.4f}  "
                  f"(window [{RATIO_LO}, {RATIO_HI}])")
            print(f"  gap(3 → 4) / gap(2 → 3) = {gap_3_to_4} / "
                  f"{INSTANCE_3_GAP_2_TO_3} = {gap_ratio:.4f}  "
                  f"(window [{RATIO_LO}, {RATIO_HI}])")
            width_ok = RATIO_LO <= width_ratio <= RATIO_HI
            gap_ok = RATIO_LO <= gap_ratio <= RATIO_HI
            if width_ok and gap_ok:
                layer2_outcome = 'α'
                layer2_verdict = (f'Both ratios within 10% window. '
                                  f'Doubling pattern empirically '
                                  f'anchored at instance-3 → instance-4.')
            else:
                layer2_outcome = 'β-broken'
                broken = []
                if not width_ok:
                    broken.append(f'width_ratio = {width_ratio:.3f} '
                                  f'outside [{RATIO_LO}, {RATIO_HI}]')
                if not gap_ok:
                    broken.append(f'gap_ratio = {gap_ratio:.3f} '
                                  f'outside [{RATIO_LO}, {RATIO_HI}]')
                layer2_verdict = (f'Doubling-pattern breakdown: '
                                  + '; '.join(broken))
            if inst4_truncated:
                layer2_verdict += (' Instance-4 upper edge truncated by '
                                   'D_HI — width is a lower bound.')

    print(f"\n  Layer 2 outcome: ({layer2_outcome})")
    print(f"  Verdict: {layer2_verdict}")

    # ---- Per-decade table ----
    print("\n" + "=" * 72)
    print("Per-decade analysis")
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

    print(f"  ({len(decade_rows)} decade bins; full table in CSV)")
    # Echo a few key bins (around each merged regime)
    interesting_d = [60, 100, 200, 482, 600, 952, 1717, 1800, 2812,
                     3740, 4000, 6000, 8000, 10000, 12000, 13900]
    for r in decade_rows:
        if any(r['bin_lo'] <= d < r['bin_hi'] for d in interesting_d):
            mw = (f"{r['mean_cluster_width']:7.2f}"
                  if not math.isnan(r['mean_cluster_width']) else "    n/a")
            print(f"  [{r['bin_lo']:5d}, {r['bin_hi']:5d}) "
                  f"skipped {r['n_skipped']:4d}/{r['bin_width']:<3d}  "
                  f"frac = {r['skip_fraction']:.4f}  "
                  f"clusters_starting = "
                  f"{r['n_clusters_starting']:3d}  "
                  f"mean_width = {mw}")

    # ---- Layer 3 ----
    print("\n" + "=" * 72)
    print("Layer 3 — Asymptotic-form refinement (exploratory)")
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
    q4_outcome = 'α-Q4' if q4_substantive else 'β-Q4'
    print(f"  Q4 outcome: ({q4_outcome})  best adj R² = "
          f"{best_adj:.4f} ({'≥' if q4_substantive else '<'} "
          f"{Q4_SUBSTANTIVE_R2})")

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

    # All instances incl. instance 1 for chart shading
    chart_regimes = [
        {'lower_edge': INSTANCE_1[0], 'upper_edge': INSTANCE_1[1],
         'past_range': False},
    ] + bounded_regimes

    if plt is not None:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9))
        ax1.plot(D_arr, f_arr, 'o', color='#1f77b4', markersize=4,
                 label=f'per-decade skip fraction (n = {len(D_arr)})')
        D_smooth = np.linspace(D_arr[0], D_arr[-1], 600)
        ax1.plot(D_smooth, 1 - a1 / np.log(D_smooth), '-',
                 color='#ff7f0e',
                 label=f'fit 1: 1 − {a1:.3f}/log(D)  '
                       f'(adj R² = {adj1:.3f})')
        ax1.plot(D_smooth, 1 - a2 / (np.log(D_smooth) ** 2), '--',
                 color='#2ca02c',
                 label=f'fit 2: 1 − {a2:.3f}/log²(D)  '
                       f'(adj R² = {adj2:.3f})')
        ax1.plot(D_smooth,
                 1 - a3 / np.log(D_smooth) - b3 / (np.log(D_smooth) ** 2),
                 ':', color='#d62728',
                 label=f'fit 3: blend  (adj R² = {adj3:.3f})')
        ax1.axhline(1.0, color='gray', linestyle=':', alpha=0.5)
        for r in chart_regimes:
            ax1.axvspan(r['lower_edge'], r['upper_edge'],
                        alpha=0.15, color='purple')
        ax1.set_xlabel('digit-length D (bin midpoint)')
        ax1.set_ylabel('skip fraction in decade')
        ax1.set_title(f'Density of combined-skip digit-lengths vs D '
                      f'(D ∈ [{D_LO}, {D_HI}); N_MAX = {N_MAX})')
        ax1.set_ylim(-0.05, 1.10)
        ax1.legend(loc='lower right', fontsize=9)
        ax1.grid(True, alpha=0.3)

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
                  markersize=4, label='mean cluster width (symlog)')
        ax2b.set_yscale('symlog')
        ax2b.set_ylabel('mean cluster width [symlog]', color='#d62728')
        ax2b.tick_params(axis='y', labelcolor='#d62728')
        for r in chart_regimes:
            ax2.axvspan(r['lower_edge'], r['upper_edge'],
                        alpha=0.15, color='purple')
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2b.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2,
                   loc='upper right', fontsize=9)
        fig.suptitle(f'Paper 3 v5.x Task 5 — extended density + '
                     f'instance-4 doubling-pattern test\n'
                     f'Layer 2 outcome ({layer2_outcome}); Layer 3 '
                     f'best adj R² = {best_adj:.4f}',
                     fontsize=10)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(PNG_OUT, dpi=120)
        plt.close(fig)
        print(f"  Saved: {PNG_OUT}")

    # ---- CSVs ----
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
              'lower_bounded', 'upper_bounded', 'past_range',
              'landing_5_n', 'landing_7_n', 'landing_series',
              'landing_first']
    with open(CSV_MERGED, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fn_mer)
        w.writeheader()
        for r in bounded_regimes:
            w.writerow(r)
    print(f"  Saved: {CSV_MERGED}")

    # ---- Fact-only summary ----
    write_summary(D_HI, inst3_hi, inst3_width, inst3_truncated,
                  bounded_regimes, all_instances, instance_4,
                  width_ratio, gap_ratio, layer2_outcome, layer2_verdict,
                  decade_rows, a1, adj1, a2, adj2, a3, b3, adj3,
                  best_adj, q4_outcome, q4_substantive)
    print(f"  Saved: {MD_OUT}")

    # ---- Final status ----
    print("\n" + "=" * 72)
    print("TASK 5 — STATUS")
    print("=" * 72)
    print(f"Layer 0: PASS")
    print(f"Layer 1: instance 3 = (2812, {inst3_hi}), width = "
          f"{inst3_width}, truncated = {inst3_truncated}")
    print(f"Layer 2: ({layer2_outcome})  — {layer2_verdict}")
    print(f"Layer 3: ({q4_outcome})  best adj R² = {best_adj:.4f}")
    print(f"Files: {CSV_DECADE}, {CSV_MERGED}, {PNG_OUT}, {MD_OUT}")
    if layer2_outcome.startswith('γ-between'):
        print(f"\nEnd-of-task: HALT — layer 2 outcome outside pre-reg set.")
        sys.exit(1)
    print(f"\nEnd-of-task: PASS")


def write_summary(D_HI, inst3_hi, inst3_width, inst3_truncated,
                  bounded_regimes, all_instances, instance_4,
                  width_ratio, gap_ratio, layer2_outcome, layer2_verdict,
                  decade_rows, a1, adj1, a2, adj2, a3, b3, adj3,
                  best_adj, q4_outcome, q4_substantive):
    with open(MD_OUT, 'w', encoding='utf-8') as f:
        f.write("# Task 5 — Instance-4 doubling-pattern test: summary\n\n")
        f.write(f"**Date:** 11 May 2026.\n")
        f.write(f"**Pre-registration:** `v3_12_data/briefs/"
                f"task5_instance_4_doubling_pre_registration.md`.\n")
        f.write(f"**N_MAX:** {N_MAX}. **Analysis range:** "
                f"[{D_LO}, {D_HI}).\n\n")

        f.write(f"## Layer 0 — Anchors\n\n")
        f.write(f"- Strict-23 [90, 200] cluster count: OK.\n")
        f.write(f"- Instance 1 (172, 482): OK.\n")
        f.write(f"- Instance 2 (952, 1717): OK.\n\n")

        f.write(f"## Layer 1 — Instance-3 upper-edge measurement\n\n")
        f.write(f"- Instance 3 cluster: (2812, {inst3_hi}); "
                f"width = {inst3_width}.\n")
        f.write(f"- Truncated at D_HI: "
                f"{'YES' if inst3_truncated else 'no'}.\n\n")

        f.write(f"## Layer 2 — Instance-4 detection + doubling-pattern "
                f"test\n\n")
        f.write(f"**Outcome: ({layer2_outcome})**.  {layer2_verdict}\n\n")
        f.write(f"### All detected instances\n\n")
        f.write("| # | Bounded range | Width | Pre-regime gap | "
                "Width ratio | Gap ratio | Lands at hi+1 |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for i, inst in enumerate(all_instances, start=1):
            lo, hi, w = inst['lower_edge'], inst['upper_edge'], \
                        inst['width']
            if i == 1:
                gap = '—'
                wr = '—'
                gr = '—'
            else:
                prev = all_instances[i - 2]
                gap = lo - prev['upper_edge'] - 1
                if prev['width'] > 0:
                    wr = f"{w / prev['width']:.4f}"
                else:
                    wr = '—'
                if i >= 3:
                    prev_prev = all_instances[i - 3]
                    prev_gap = prev['lower_edge'] - \
                               prev_prev['upper_edge'] - 1
                    gr = (f"{gap / prev_gap:.4f}"
                          if prev_gap > 0 else '—')
                else:
                    gr = '—'
            landing = inst.get('landing_series', '—')
            past = ' (past D_HI)' if inst.get('past_range') else ''
            f.write(f"| {i} | ({lo}, {hi}){past} | {w} | "
                    f"{gap} | {wr} | {gr} | {landing} |\n")
        f.write("\n")
        if width_ratio is not None:
            f.write(f"**width(4) / width(3) = {width_ratio:.4f}**  "
                    f"(window [{RATIO_LO}, {RATIO_HI}]).\n")
        if gap_ratio is not None:
            f.write(f"**gap(3 → 4) / gap(2 → 3) = {gap_ratio:.4f}**  "
                    f"(window [{RATIO_LO}, {RATIO_HI}]).\n\n")

        f.write(f"## Layer 3 — Asymptotic-form refinement\n\n")
        f.write("| Form | Parameter(s) | adj R² |\n")
        f.write("|---|---|---|\n")
        f.write(f"| 1 − a/log(D) | a = {a1:.4f} | {adj1:.4f} |\n")
        f.write(f"| 1 − a/log²(D) | a = {a2:.4f} | {adj2:.4f} |\n")
        f.write(f"| blend | a = {a3:.4f}, b = {b3:.4f} | {adj3:.4f} |\n\n")
        f.write(f"**Outcome: ({q4_outcome})**.  best adj R² = "
                f"{best_adj:.4f} "
                f"({'≥' if q4_substantive else '<'} "
                f"{Q4_SUBSTANTIVE_R2}).\n\n")

        f.write(f"## Structural observations\n\n")
        f.write(f"(Authored by Mr Code post-run based on the data above; "
                f"the script writes facts only.)\n\n")
        f.write("🐕☕⬡\n\n")
        f.write("— Mr Code, 11 May 2026 (Paper 3 v5.x Task 5)\n")


if __name__ == '__main__':
    main()
