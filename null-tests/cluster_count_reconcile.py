#!/usr/bin/env python3
"""
Cluster-Count Reconciliation: 36 vs 47/48 (v2.6 -> v2.7 Task 2)
================================================================

v2.6 section 5.2 reports two seemingly inconsistent cluster counts at
full scale (3.25M digits):

  - Paragraph 1 (headline): "we identify 36 such clusters"
  - Paragraph 3 (full-scale refit): "47 inter-cluster gaps"  (=> 48 clusters)

Mr A's arithmetic: 36 clusters -> 35 gaps; 47 gaps -> 48 clusters.

This script sweeps cluster-detection parameters at full scale to identify
which parameter set produces each count, and produces a definitive table.
Real primes only — no null trials needed for this reconciliation task.

Method:
  - Compute real-prime gap arrays once at full scale (sieve to 15M).
  - For each combination of (window, min_gaps), compute the raw
    `sync_starts` list (positions where every gap in the window is
    coincident with cb >= min_gaps).
  - For each `sync_starts`, apply merge with multiple merge_dist
    values cheaply. The (window, min_gaps, merge_dist) triple uniquely
    determines (cluster_count, inter_cluster_gaps, total_span, budget).

Output: CSV table and console summary highlighting any parameter set
producing 36 clusters and the canonical §5.2 parameter set (window=50,
min_gaps=20, merge_dist=500).
"""
import math, time, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def sieve(limit):
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def compute_gap_arrays(logs1, logs2):
    d1 = set()
    s = 0.0
    for lg in logs1:
        s += lg
        d1.add(int(s) + 1)
    d2 = set()
    s = 0.0
    for lg in logs2:
        s += lg
        d2.add(int(s) + 1)
    max_d = min(max(d1), max(d2))
    is_gap1 = bytearray(b'\x01') * (max_d + 1)
    is_gap2 = bytearray(b'\x01') * (max_d + 1)
    for d in d1:
        if d <= max_d:
            is_gap1[d] = 0
    for d in d2:
        if d <= max_d:
            is_gap2[d] = 0
    return is_gap1, is_gap2, max_d


def find_sync_starts(is_gap1, is_gap2, max_d, window, min_gaps, step=10):
    """All start positions where every gap in [start, start+window) is
    coincident across both series AND >= min_gaps total gaps. Matches
    `find_clusters_fast` cb==ca && ca>=min_gaps logic from full_null_model.py."""
    sync_starts = []
    for start in range(1, max_d - window + 1, step):
        end = start + window
        cb = ca = 0
        for d in range(start, end):
            g1, g2 = is_gap1[d], is_gap2[d]
            if g1 and g2:
                cb += 1
                ca += 1
            elif g1 or g2:
                ca += 1
        if ca >= min_gaps and cb == ca:
            sync_starts.append(start)
    return sync_starts


def merge_into_clusters(sync_starts, window, merge_dist):
    """Same merge rule as full_null_model.find_clusters_fast."""
    if not sync_starts:
        return []
    clusters = []
    c_start = sync_starts[0]
    c_end = sync_starts[0] + window
    for s in sync_starts[1:]:
        if s <= c_end + merge_dist:
            c_end = s + window
        else:
            clusters.append({'centre': (c_start + c_end) // 2,
                             'span': c_end - c_start,
                             'start': c_start, 'end': c_end})
            c_start, c_end = s, s + window
    clusters.append({'centre': (c_start + c_end) // 2,
                     'span': c_end - c_start,
                     'start': c_start, 'end': c_end})
    return clusters


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    T0 = time.time()

    print("=" * 78)
    print("CLUSTER-COUNT RECONCILIATION  (v2.6 -> v2.7 Task 2)")
    print("  Real primes only at full scale.")
    print("  Sweep: window × min_gaps × merge_dist. Identify which combinations")
    print("  produce 36 clusters and which produce 48 (47 inter-cluster gaps).")
    print("=" * 78)

    print("\n[1] Sieving primes...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    p5_logs = [math.log10(p) for p in p5]
    p7_logs = [math.log10(p) for p in p7]
    n_use = min(len(p5_logs), len(p7_logs))
    print(f"  5-series: {len(p5):,}, 7-series: {len(p7):,}, n_use={n_use:,}")

    print("\n[2] Real-prime gap arrays at full scale...")
    is_gap1, is_gap2, max_d = compute_gap_arrays(p5_logs[:n_use], p7_logs[:n_use])
    print(f"  max_d = {max_d:,}")

    # Sweep grid
    windows = [30, 40, 50, 60, 70]
    min_gaps_list = [20, 22, 25, 28, 30, 35, 40]
    merge_dists = [200, 500, 1000, 2000, 5000]

    print(f"\n[3] Computing sync_starts for each (window, min_gaps) combination...")
    print(f"   {len(windows)} windows × {len(min_gaps_list)} min_gaps "
          f"= {len(windows) * len(min_gaps_list)} combos")

    sync_starts_cache = {}
    for w in windows:
        for mg in min_gaps_list:
            t1 = time.time()
            ss = find_sync_starts(is_gap1, is_gap2, max_d, w, mg)
            sync_starts_cache[(w, mg)] = ss
            print(f"  window={w:2d} min_gaps={mg:2d}: {len(ss):>4} sync_starts "
                  f"[{time.time()-t1:.1f}s]")

    # Merge sweep
    print(f"\n[4] Applying merge with merge_dist sweep "
          f"({len(merge_dists)} values per (window, min_gaps))...")
    rows = []
    targets = {36, 48}  # of interest
    for w in windows:
        for mg in min_gaps_list:
            ss = sync_starts_cache[(w, mg)]
            for md in merge_dists:
                cl = merge_into_clusters(ss, w, md)
                n_cl = len(cl)
                n_gaps = max(0, n_cl - 1)
                total_span = sum(c['span'] for c in cl)
                budget = total_span / max_d if max_d > 0 else 0.0
                rows.append({
                    'window': w, 'min_gaps': mg, 'merge_dist': md,
                    'sync_starts': len(ss),
                    'n_clusters': n_cl, 'n_inter_gaps': n_gaps,
                    'total_span': total_span, 'budget': budget,
                })

    # ---- Highlight canonical §5.2 default ----
    canonical = next((r for r in rows
                      if r['window'] == 50 and r['min_gaps'] == 20
                      and r['merge_dist'] == 500), None)
    print(f"\n{'=' * 78}")
    print("CANONICAL §5.2 DEFAULT (window=50, min_gaps=20, merge_dist=500)")
    print(f"{'=' * 78}")
    if canonical:
        print(f"  n_clusters       = {canonical['n_clusters']}")
        print(f"  n_inter_gaps     = {canonical['n_inter_gaps']}")
        print(f"  total_span       = {canonical['total_span']:,}")
        print(f"  budget           = {canonical['budget']:.6f} "
              f"({100*canonical['budget']:.4f}%)")

    # ---- Find any param sets producing 36 clusters ----
    print(f"\n{'=' * 78}")
    print("PARAMETER SETS PRODUCING 36 CLUSTERS")
    print(f"{'=' * 78}")
    matches_36 = [r for r in rows if r['n_clusters'] == 36]
    if matches_36:
        print(f"  {'window':>6} {'min_gaps':>9} {'merge_dist':>11} "
              f"{'n_clusters':>11} {'n_gaps':>7} {'budget%':>8}")
        for r in matches_36:
            print(f"  {r['window']:>6} {r['min_gaps']:>9} {r['merge_dist']:>11} "
                  f"{r['n_clusters']:>11} {r['n_inter_gaps']:>7} "
                  f"{100*r['budget']:>8.4f}")
    else:
        print("  NONE within swept grid.")

    # ---- Find any param sets producing 48 clusters (47 inter-gaps) ----
    print(f"\n{'=' * 78}")
    print("PARAMETER SETS PRODUCING 48 CLUSTERS / 47 INTER-CLUSTER GAPS")
    print(f"{'=' * 78}")
    matches_48 = [r for r in rows if r['n_clusters'] == 48]
    if matches_48:
        print(f"  {'window':>6} {'min_gaps':>9} {'merge_dist':>11} "
              f"{'n_clusters':>11} {'n_gaps':>7} {'budget%':>8}")
        for r in matches_48:
            print(f"  {r['window']:>6} {r['min_gaps']:>9} {r['merge_dist']:>11} "
                  f"{r['n_clusters']:>11} {r['n_inter_gaps']:>7} "
                  f"{100*r['budget']:>8.4f}")
    else:
        print("  NONE within swept grid.")

    # ---- Closest neighbours to 36 ----
    print(f"\n{'=' * 78}")
    print("CLOSEST PARAM SETS TO 36 CLUSTERS (|delta| <= 3)")
    print(f"{'=' * 78}")
    near = sorted([r for r in rows if abs(r['n_clusters'] - 36) <= 3],
                  key=lambda r: (abs(r['n_clusters'] - 36),
                                 r['window'], r['min_gaps'], r['merge_dist']))
    print(f"  {'window':>6} {'min_gaps':>9} {'merge_dist':>11} "
          f"{'n_clusters':>11} {'n_gaps':>7} {'budget%':>8}")
    for r in near[:25]:
        marker = "  *" if r['n_clusters'] == 36 else "   "
        print(f"  {r['window']:>6} {r['min_gaps']:>9} {r['merge_dist']:>11} "
              f"{r['n_clusters']:>11} {r['n_inter_gaps']:>7} "
              f"{100*r['budget']:>8.4f}{marker}")

    # ---- Full table by window=50 (canonical column) ----
    print(f"\n{'=' * 78}")
    print("FULL TABLE FOR window=50 (canonical §5.2 column)")
    print(f"{'=' * 78}")
    print(f"  {'min_gaps':>9} {'merge_dist':>11} {'n_clusters':>11} "
          f"{'n_gaps':>7} {'budget%':>8}")
    for r in [x for x in rows if x['window'] == 50]:
        marker = ""
        if r['n_clusters'] == 36:
            marker = "  ← matches §5.2 'we identify 36 such clusters'"
        elif r['n_clusters'] == 48:
            marker = "  ← matches §5.2 full-scale refit (47 inter-cluster gaps)"
        print(f"  {r['min_gaps']:>9} {r['merge_dist']:>11} {r['n_clusters']:>11} "
              f"{r['n_inter_gaps']:>7} {100*r['budget']:>8.4f}{marker}")

    # ---- Save CSV ----
    csv_path = os.path.join(RESULTS_DIR, 'cluster_count_reconcile.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['window', 'min_gaps', 'merge_dist', 'sync_starts',
                    'n_clusters', 'n_inter_cluster_gaps',
                    'total_span', 'budget', 'max_d'])
        for r in rows:
            w.writerow([r['window'], r['min_gaps'], r['merge_dist'],
                        r['sync_starts'],
                        r['n_clusters'], r['n_inter_gaps'],
                        r['total_span'], f"{r['budget']:.6f}", max_d])
    print(f"\n  Full table saved to {csv_path}")

    # ---- Summary ----
    print(f"\n{'=' * 78}")
    print("SUMMARY")
    print(f"{'=' * 78}")
    if canonical:
        print(f"  Canonical §5.2 (50/20/500): {canonical['n_clusters']} clusters, "
              f"{canonical['n_inter_gaps']} inter-cluster gaps")
        print(f"  -> matches v2.6 §5.2 paragraph 3 ('47 inter-cluster gaps')")
    if matches_36:
        m = matches_36[0]
        print(f"  Closest param set producing 36 clusters: "
              f"window={m['window']}, min_gaps={m['min_gaps']}, merge_dist={m['merge_dist']}")
    else:
        print(f"  No param set in the swept grid produces exactly 36 clusters.")
        print(f"  Suggests v2.6 §5.2 'we identify 36 such clusters' either:")
        print(f"   (a) uses a parameter set outside this grid,")
        print(f"   (b) uses a different cluster detection algorithm, or")
        print(f"   (c) is a typo/legacy figure that should be corrected.")

    print(f"\nTotal runtime: {time.time() - T0:.1f}s")


if __name__ == '__main__':
    main()
