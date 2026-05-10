#!/usr/bin/env python3
"""Task 2 (Paper 3 v3.14): §7.3 isolated-boundary quantitative threshold.

Computes nearest-jump distances at boundaries 1 and 2 (D ≈ 60, 80) and across
the d ∈ [90, 200] range, under three definitions of "nearest jump":

  (i) per-d, excluding same d, across both series
  (ii) per-cluster (PRIMARY per CinC Q1) — contiguous skipped d's collapse
       into a cluster; distance is between nearest cluster endpoints. Reasoning:
       boundary 1's 5-series skip {60,61} is adjacent to the 7-series skip
       {62,63}; reading (i) treats this inter-series adjacency as a "near-jump"
       when actually they're parts of the same boundary event. (ii) collapses
       this correctly.
  (iii) per-d including same d (degenerate, always 0) — reported for transparency.

A "digit-jump at n" in series i is any case where D_i(n+1) − D_i(n) ≥ 2.
Skip set at jump = {D_i(n)+1, ..., D_i(n+1)−1}. Combined skip set = union
across both series.

Verification gate. D_5(30) = 59, D_5(31) = 62, D_5(38) = 79, D_5(39) = 82
(per v3.13 Tables 1 and 2). Halt if not.
"""
import os
import sys
import csv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

SIEVE_LIMIT = 200_000  # plenty for the first ~250 primes per series
N_MAX = 250            # number of primes per series to multiply in
D_RANGE_LO = 90        # lower bound of [90, 200] aggregate range
D_RANGE_HI = 200       # upper bound


def compute_D(series, n_max):
    """Return list D[0..n_max-1] where D[i] = digit length of product of
    series[0..i] using Python int arithmetic and len(str(prod))."""
    prod = 1
    out = []
    for p in series[:n_max]:
        prod *= p
        out.append(len(str(prod)))
    return out


def find_jumps(D):
    """Return list of (n_1indexed, D_before, D_after, skip_set) for each
    digit-jump (D[i+1] - D[i] >= 2). n is 1-indexed (the prime number that
    was multiplied in to cause the jump)."""
    jumps = []
    for i in range(len(D) - 1):
        if D[i+1] - D[i] >= 2:
            skipped = list(range(D[i] + 1, D[i+1]))
            jumps.append((i + 2, D[i], D[i+1], skipped))
            # (i+2 because: D[i] is product of first i+1 primes, D[i+1] is
            # product of first i+2 primes, so the jump occurred when
            # multiplying in prime number (i+2).)
    return jumps


def collect_skip_set(jumps):
    """Return sorted list of all skipped d's from a series' jumps."""
    s = set()
    for _, _, _, skipped in jumps:
        s.update(skipped)
    return sorted(s)


def cluster_contiguous(sorted_ds):
    """Group a sorted list of d's into maximally-contiguous runs.
    Returns list of (d_min, d_max) for each cluster."""
    if not sorted_ds:
        return []
    clusters = []
    start = sorted_ds[0]
    prev = sorted_ds[0]
    for d in sorted_ds[1:]:
        if d == prev + 1:
            prev = d
        else:
            clusters.append((start, prev))
            start = d
            prev = d
    clusters.append((start, prev))
    return clusters


def nearest_jump_per_d(sorted_ds, d):
    """(i) min over d' != d of |d - d'|."""
    best = None
    for d2 in sorted_ds:
        if d2 == d:
            continue
        diff = abs(d - d2)
        if best is None or diff < best:
            best = diff
    return best


def nearest_jump_per_cluster(clusters, cluster_idx):
    """(ii) min distance from cluster[cluster_idx] to any other cluster.
    Distance between non-overlapping clusters [a_min, a_max] and [b_min, b_max]
    with a_max < b_min is b_min - a_max."""
    if len(clusters) <= 1:
        return None
    a_min, a_max = clusters[cluster_idx]
    best = None
    for j, (b_min, b_max) in enumerate(clusters):
        if j == cluster_idx:
            continue
        if b_max < a_min:
            d = a_min - b_max
        elif b_min > a_max:
            d = b_min - a_max
        else:
            d = 0  # overlap (shouldn't happen with disjoint sorted clusters)
        if best is None or d < best:
            best = d
    return best


def find_cluster_for_d(clusters, d):
    """Return index of cluster containing d, or None."""
    for j, (lo, hi) in enumerate(clusters):
        if lo <= d <= hi:
            return j
    return None


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Sieving primes up to {SIEVE_LIMIT}...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    print(f"  5-series: {len(p5)} available, taking first {N_MAX}")
    print(f"  7-series: {len(p7)} available, taking first {N_MAX}")

    D5 = compute_D(p5, N_MAX)
    D7 = compute_D(p7, N_MAX)

    # ---- Verification gate ----
    print(f"\n{'='*72}")
    print("Verification gate: v3.13 boundary positions")
    print(f"{'='*72}")
    targets = [(30, D5[29], 59), (31, D5[30], 62),
               (38, D5[37], 79), (39, D5[38], 82)]
    fail = False
    for n, got, want in targets:
        ok = (got == want)
        flag = 'OK' if ok else 'FAIL'
        print(f"  D_5({n}) = {got}  (want {want})  {flag}")
        if not ok:
            fail = True
    if fail:
        print("  HALT: boundary anchor mismatch.")
        sys.exit(1)

    # Show D_5(N_MAX) and D_7(N_MAX) for reference
    print(f"\n  D_5({N_MAX}) = {D5[-1]}")
    print(f"  D_7({N_MAX}) = {D7[-1]}")
    if D5[-1] < D_RANGE_HI or D7[-1] < D_RANGE_HI:
        print(f"  WARNING: max D < {D_RANGE_HI}, may need to extend N_MAX")

    # ---- Find jumps and skip sets ----
    jumps5 = find_jumps(D5)
    jumps7 = find_jumps(D7)
    print(f"\n  5-series jumps (n_max={N_MAX}): {len(jumps5)} total")
    print(f"  7-series jumps (n_max={N_MAX}): {len(jumps7)} total")

    skip5 = collect_skip_set(jumps5)
    skip7 = collect_skip_set(jumps7)
    skip_combined = sorted(set(skip5) | set(skip7))
    print(f"  Total skipped d's (combined): {len(skip_combined)}, "
          f"range [{skip_combined[0]}, {skip_combined[-1]}]")

    # ---- Clusters ----
    clusters = cluster_contiguous(skip_combined)
    print(f"\n  Combined skip clusters: {len(clusters)}")
    print(f"  First 12 clusters: {clusters[:12]}")

    # ---- Boundary 1 and 2 detail ----
    print(f"\n{'='*72}")
    print("Boundary detail")
    print(f"{'='*72}")
    print("\n  Boundary 1 region (d in 58..68):")
    for d in range(58, 69):
        in5 = '5' if d in skip5 else '.'
        in7 = '7' if d in skip7 else '.'
        c_idx = find_cluster_for_d(clusters, d)
        c_str = f"cluster #{c_idx}" if c_idx is not None else 'not skipped'
        print(f"    d={d}: {in5}{in7}  ({c_str})")

    print("\n  Boundary 2 region (d in 78..88):")
    for d in range(78, 89):
        in5 = '5' if d in skip5 else '.'
        in7 = '7' if d in skip7 else '.'
        c_idx = find_cluster_for_d(clusters, d)
        c_str = f"cluster #{c_idx}" if c_idx is not None else 'not skipped'
        print(f"    d={d}: {in5}{in7}  ({c_str})")

    # ---- nearest_jump under three definitions ----
    print(f"\n{'='*72}")
    print("nearest_jump(d) at boundary 1 and boundary 2")
    print(f"{'='*72}")

    rows = []
    boundary_targets = [(60, '1'), (61, '1'), (62, '1'), (63, '1'),
                        (80, '2'), (81, '2')]
    for d, blabel in boundary_targets:
        if d not in skip_combined:
            print(f"  d={d}: not in combined skip set!")
            continue
        i_def = nearest_jump_per_d(skip_combined, d)
        c_idx = find_cluster_for_d(clusters, d)
        ii_def = nearest_jump_per_cluster(clusters, c_idx)
        iii_def = 0  # degenerate
        rows.append({
            'd': d, 'boundary': blabel,
            'def_i': i_def, 'def_ii': ii_def, 'def_iii': iii_def,
            'cluster': clusters[c_idx],
        })
        print(f"  d={d} (boundary {blabel}, cluster {clusters[c_idx]}):")
        print(f"    (i) per-d, exclude self     = {i_def}")
        print(f"    (ii) per-cluster [PRIMARY]  = {ii_def}")
        print(f"    (iii) per-d, include self   = {iii_def}  (degenerate)")

    # ---- Distribution over [D_RANGE_LO, D_RANGE_HI] ----
    print(f"\n{'='*72}")
    print(f"Distribution: nearest_jump(d) for d in [{D_RANGE_LO}, {D_RANGE_HI}]")
    print(f"{'='*72}")

    range_ds = [d for d in skip_combined if D_RANGE_LO <= d <= D_RANGE_HI]
    print(f"  skipped d's in range: {len(range_ds)}")

    # Definition (i): per-d
    nj_i = [nearest_jump_per_d(skip_combined, d) for d in range_ds]
    # Definition (ii): per-cluster — assign each d its cluster's nearest_jump
    nj_ii_per_d = []
    for d in range_ds:
        c_idx = find_cluster_for_d(clusters, d)
        nj_ii_per_d.append(nearest_jump_per_cluster(clusters, c_idx))

    # Per-cluster aggregation in range
    range_clusters = [(j, c) for j, c in enumerate(clusters)
                      if D_RANGE_LO <= c[0] <= D_RANGE_HI
                      or D_RANGE_LO <= c[1] <= D_RANGE_HI]
    range_cluster_njs = [nearest_jump_per_cluster(clusters, j)
                         for j, _ in range_clusters]

    def summarise(label, vals):
        if not vals:
            print(f"  {label}: (empty)")
            return
        srt = sorted(vals)
        n = len(srt)
        median = srt[n // 2] if n % 2 == 1 else (srt[n//2 - 1] + srt[n//2]) / 2
        ge5 = sum(1 for v in vals if v >= 5)
        ge3 = sum(1 for v in vals if v >= 3)
        print(f"  {label}: n={n}, median={median}, mean={sum(vals)/n:.2f}, "
              f"max={max(vals)}, count(>=3)={ge3}, count(>=5)={ge5}")

    print()
    summarise("(i) per-d  ", nj_i)
    summarise("(ii) per-d (cluster-based, dup per d)", nj_ii_per_d)
    summarise("(ii) per-cluster (one entry per cluster) [PRIMARY]",
              range_cluster_njs)

    # ---- §7.3 sentence draft (using definition ii) ----
    print(f"\n{'='*72}")
    print("§7.3 sentence draft (using definition (ii) per-cluster)")
    print(f"{'='*72}")

    # Boundary 1 cluster: find the cluster that contains d=60 and 61
    b1_cluster_idx = find_cluster_for_d(clusters, 60)
    b1_nj = nearest_jump_per_cluster(clusters, b1_cluster_idx)
    b1_cluster = clusters[b1_cluster_idx]
    # Boundary 2 cluster
    b2_cluster_idx = find_cluster_for_d(clusters, 80)
    b2_nj = nearest_jump_per_cluster(clusters, b2_cluster_idx)
    b2_cluster = clusters[b2_cluster_idx]

    range_med = sorted(range_cluster_njs)[len(range_cluster_njs) // 2] \
        if range_cluster_njs else None
    range_max = max(range_cluster_njs) if range_cluster_njs else None
    range_ge5 = sum(1 for v in range_cluster_njs if v >= 5)
    range_ge3 = sum(1 for v in range_cluster_njs if v >= 3)

    sentence = (
        f"At boundary 1 (cluster d ∈ [{b1_cluster[0]}, {b1_cluster[1]}]) the "
        f"nearest skipped digit-length cluster in either series is {b1_nj} "
        f"digits away; at boundary 2 (cluster d ∈ [{b2_cluster[0]}, {b2_cluster[1]}]) "
        f"it is {b2_nj} digits away; in the range d ∈ [{D_RANGE_LO}, {D_RANGE_HI}] "
        f"the median per-cluster nearest-jump distance is {range_med} "
        f"(max = {range_max}; {range_ge3} of {len(range_cluster_njs)} "
        f"clusters are ≥ 3 digits away; {range_ge5} are ≥ 5 digits away)."
    )
    print(f"\n  {sentence}")

    # ---- Save CSVs ----
    boundary_path = os.path.join(RESULTS_DIR, 'v3_14_task2_boundary_detail.csv')
    with open(boundary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['d', 'boundary', 'in_5series', 'in_7series',
                    'cluster_lo', 'cluster_hi',
                    'nj_def_i', 'nj_def_ii_per_cluster', 'nj_def_iii'])
        for r in rows:
            d = r['d']
            w.writerow([
                d, r['boundary'],
                int(d in skip5), int(d in skip7),
                r['cluster'][0], r['cluster'][1],
                r['def_i'], r['def_ii'], r['def_iii'],
            ])
    print(f"\n  Saved: {boundary_path}")

    range_path = os.path.join(RESULTS_DIR, 'v3_14_task2_range_clusters.csv')
    with open(range_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cluster_idx', 'd_min', 'd_max',
                    'span', 'nj_per_cluster'])
        for j, c in range_clusters:
            w.writerow([j, c[0], c[1], c[1] - c[0] + 1,
                        nearest_jump_per_cluster(clusters, j)])
    print(f"  Saved: {range_path}")

    # All skipped d's CSV (for downstream analysis)
    all_path = os.path.join(RESULTS_DIR, 'v3_14_task2_all_skipped.csv')
    with open(all_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['d', 'in_5series', 'in_7series',
                    'cluster_idx', 'cluster_lo', 'cluster_hi',
                    'nj_def_i', 'nj_def_ii'])
        for d in skip_combined:
            c_idx = find_cluster_for_d(clusters, d)
            c = clusters[c_idx]
            w.writerow([d, int(d in skip5), int(d in skip7),
                        c_idx, c[0], c[1],
                        nearest_jump_per_d(skip_combined, d),
                        nearest_jump_per_cluster(clusters, c_idx)])
    print(f"  Saved: {all_path}")

    # ---- Plot ----
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("  [warning] matplotlib unavailable; skipping plot")
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

    # Top panel: skip-set diagram with cluster boundaries
    d_max_plot = min(220, max(skip_combined))
    d_min_plot = 50
    for d in skip_combined:
        if d_min_plot <= d <= d_max_plot:
            in_5 = d in skip5
            in_7 = d in skip7
            if in_5 and in_7:
                ax1.plot(d, 0.5, 's', color='purple', markersize=4)
            elif in_5:
                ax1.plot(d, 0.7, 's', color='#1f77b4', markersize=4)
            elif in_7:
                ax1.plot(d, 0.3, 's', color='#d62728', markersize=4)
    # Shade clusters
    for j, c in enumerate(clusters):
        if c[1] >= d_min_plot and c[0] <= d_max_plot:
            ax1.axvspan(c[0] - 0.4, c[1] + 0.4, alpha=0.12, color='gray')
    # Boundary markers
    ax1.axvline(60.5, color='black', linestyle='--', alpha=0.5)
    ax1.axvline(80.5, color='black', linestyle='--', alpha=0.5)
    ax1.text(60.5, 0.95, 'B1', ha='center', fontsize=9)
    ax1.text(80.5, 0.95, 'B2', ha='center', fontsize=9)
    ax1.set_ylim(0, 1.05)
    ax1.set_yticks([0.3, 0.5, 0.7])
    ax1.set_yticklabels(['7-series only', 'both', '5-series only'])
    ax1.set_title('Skipped digit-lengths and cluster boundaries')
    ax1.grid(True, alpha=0.3, axis='x')

    # Bottom panel: nearest_jump per cluster vs d
    cluster_centers = [(c[0] + c[1]) / 2 for c in clusters
                       if c[1] >= d_min_plot and c[0] <= d_max_plot]
    cluster_njs = [nearest_jump_per_cluster(clusters, j) for j, c in
                   enumerate(clusters) if c[1] >= d_min_plot and c[0] <= d_max_plot]

    ax2.plot(cluster_centers, cluster_njs, 'o-', color='#2ca02c',
             markersize=5, linewidth=1, label='per-cluster nearest-jump (ii)')
    ax2.axhline(5, color='gray', linestyle=':', alpha=0.7,
                label='isolation threshold = 5')
    ax2.axhline(3, color='gray', linestyle=':', alpha=0.4)
    ax2.axvline(60.5, color='black', linestyle='--', alpha=0.5)
    ax2.axvline(80.5, color='black', linestyle='--', alpha=0.5)

    # Highlight boundary clusters
    if b1_cluster_idx is not None:
        ax2.plot((b1_cluster[0] + b1_cluster[1]) / 2,
                 b1_nj, 's', color='red', markersize=10,
                 markerfacecolor='none', markeredgewidth=2,
                 label=f'B1 cluster {b1_cluster}, nj={b1_nj}')
    if b2_cluster_idx is not None:
        ax2.plot((b2_cluster[0] + b2_cluster[1]) / 2,
                 b2_nj, 's', color='orange', markersize=10,
                 markerfacecolor='none', markeredgewidth=2,
                 label=f'B2 cluster {b2_cluster}, nj={b2_nj}')

    ax2.set_xlabel('digit-length d (cluster centre)')
    ax2.set_ylabel('nearest-jump distance')
    ax2.set_title('Per-cluster nearest-jump distance vs d (definition ii)')
    ax2.legend(loc='upper right', fontsize=8)
    ax2.grid(True, alpha=0.3)

    fig.suptitle('Paper 3 v3.14 Task 2 — §7.3 isolated-boundary threshold')
    fig.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, 'v3_14_task2_isolation.png')
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"  Saved: {plot_path}")


if __name__ == '__main__':
    main()
