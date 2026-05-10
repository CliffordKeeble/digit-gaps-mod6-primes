#!/usr/bin/env python3
"""Paper 3 v4.2 — Comparative cluster tabulation across D ∈ [90, 200].

For each cluster in [90, 200] (plus boundaries 1 and 2 for direct comparison),
record: series presence (5-active, 7-active, both); staggered/coincident
classification; minimum-lift factor for each active series.

Lift predicate is cluster-type-dependent (this is the §6 framing — not optional):

  * staggered, single-5, single-7, partial-coincident (default):
        k ≡ 0 (mod 3), coprime to P_i ∪ {2}
  * coincident, 5-series:
        k ≡ 0 (mod 3), coprime to P_5 ∪ {2}     (5 ∈ P_5 already)
  * coincident, 7-series:
        k ≡ 0 (mod 15), coprime to P_7 ∪ {2}    (5 ∉ P_7; mod-15 escalation)

  plus  D(Π_i(n_i*) · k) ∈ [a, b],
        where n_i* = max{n : D_i(n) < min(S_i(C))} (Convention A; per addendum 2,
        10 May 2026 — series-specific skip-range lower edge, not cluster's
        combined d-range; matches Propositions 1, 2 at all boundary anchors).

Anchor verification (Pattern 75 — HALT on failure):
  - D_5(30)=59, D_5(31)=62, D_5(38)=79, D_5(39)=82 (v3.13 / v4.1 Tables)
  - D_7(36)=77, D_7(37)=79, D_7(38)=82
  - mpmath at 200-dps reproduces those D values
  - Cluster count in [90, 200] = 23 under strict "entirely contained" reading
    (calibrated from v3.14's loose 24-count; see addendum
     mr_code_brief_paper_3_v4_2_addendum_cluster_count.md)
  - Per-cluster nearest-cluster distance: median = max = 2 across [90, 200],
    0/23 at distance ≥ 3, 0/23 at distance ≥ 5
  - Boundary 1 lifts (5-series, 7-series) = (3, 3)
  - Boundary 2 lifts (5-series, 7-series) = (3, 15)

The (172, 482) cluster — leading edge of the asymptotic merged regime
within N_MAX = 250 — is recorded separately as `merged_regime_edge` row,
classification `asymptotic-merged`, lifts marked degenerate.

Outputs:
  v3_12_data/results/cluster_comparative_tabulation.csv
  v3_12_data/results/cluster_comparative_tabulation_summary.txt
"""
import os
import sys
import csv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

SIEVE_LIMIT = 200_000
N_MAX = 250
D_RANGE_LO = 90
D_RANGE_HI = 200

LIFT_K_PRIMARY = 100
LIFT_K_EXTENDED = 1000


# ----------------------------------------------------------------------------
# core helpers
# ----------------------------------------------------------------------------

def compute_products_and_D(series, n_max):
    """Return (prods, D) where prods[i] = Π of first i+1 primes (Python int,
    exact), and D[i] = digit length of prods[i]."""
    prods, D = [], []
    prod = 1
    for p in series[:n_max]:
        prod *= p
        prods.append(prod)
        D.append(len(str(prod)))
    return prods, D


def collect_skip_set(D):
    """Set of digit-lengths skipped by the series (any d strictly between
    consecutive D values when the gap is >= 2)."""
    s = set()
    for i in range(len(D) - 1):
        if D[i + 1] - D[i] >= 2:
            for d in range(D[i] + 1, D[i + 1]):
                s.add(d)
    return s


def cluster_contiguous(sorted_ds):
    """Group sorted list of d's into maximally-contiguous (lo, hi) runs."""
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


def per_cluster_distance(clusters, idx):
    """Min cluster-endpoint distance from clusters[idx] to any other cluster.
    Distance between disjoint (a_lo, a_hi) and (b_lo, b_hi) with a_hi < b_lo
    is b_lo - a_hi."""
    a_lo, a_hi = clusters[idx]
    best = None
    for j, (b_lo, b_hi) in enumerate(clusters):
        if j == idx:
            continue
        if b_hi < a_lo:
            d = a_lo - b_hi
        elif b_lo > a_hi:
            d = b_lo - a_hi
        else:
            d = 0
        if best is None or d < best:
            best = d
    return best


def largest_contiguous_run_min(S_local):
    """For Convention A: return min of the LARGEST CONTIGUOUS RUN within
    S_local. CinC's anchor table for B1 7-series uses 62 (= min of {62, 63})
    as the threshold even though full S_7(B1) = {60, 62, 63} (min 60); the
    'series-i skip range within C' phrase resolves to the largest contiguous
    skip-piece of series i, not the full per-series skip set within [a, b].

    For coincident clusters (single run) this equals min(S_local).
    For partial-coincident / staggered clusters with multiple runs,
    pick the longest run; tiebreak: smallest min (earliest d).

    Returns None if S_local is empty.
    """
    if not S_local:
        return None
    s = sorted(S_local)
    runs = []  # list of (start, end)
    start = prev = s[0]
    for d in s[1:]:
        if d == prev + 1:
            prev = d
        else:
            runs.append((start, prev))
            start = prev = d
    runs.append((start, prev))
    # Largest run by length; tiebreak by smallest start
    largest = max(runs, key=lambda r: (r[1] - r[0], -r[0]))
    return largest[0]


def find_n_star_for_skip_range(D, S_local):
    """Convention A (per addendum 2, operational reading): largest n
    (1-indexed) with D[n-1] < min(largest_contiguous_run(S_local)).

    Returns 0 if no such n, or if S_local is empty (series not active)."""
    threshold = largest_contiguous_run_min(S_local)
    if threshold is None:
        return 0
    for n in range(len(D), 0, -1):
        if D[n - 1] < threshold:
            return n
    return 0


def prime_factors(k):
    """Set of distinct prime factors of positive integer k."""
    factors = set()
    n = k
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def find_min_lift(prod_at_n_star, forbidden_primes, a, b, required_divisor,
                  k_max):
    """Smallest k satisfying:
       - k % required_divisor == 0
       - prime_factors(k) disjoint from forbidden_primes
       - D(prod_at_n_star * k) ∈ [a, b]
    Returns int k, or None if no k <= k_max satisfies."""
    k = required_divisor
    while k <= k_max:
        if not (prime_factors(k) & forbidden_primes):
            d_lifted = len(str(prod_at_n_star * k))
            if a <= d_lifted <= b:
                return k
        k += required_divisor
    return None


def classify_cluster(a, b, skip5, skip7):
    """Return (classification, S5_local, S7_local).
    Classification ∈ {'single-5', 'single-7', 'staggered', 'coincident',
                      'partial-coincident', 'NONE'}."""
    S5 = sorted(d for d in skip5 if a <= d <= b)
    S7 = sorted(d for d in skip7 if a <= d <= b)
    if S5 and S7:
        if S5 == S7:
            return 'coincident', S5, S7
        elif set(S5) & set(S7):
            return 'partial-coincident', S5, S7
        else:
            return 'staggered', S5, S7
    if S5:
        return 'single-5', S5, S7
    if S7:
        return 'single-7', S5, S7
    return 'NONE', S5, S7


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Sieving primes up to {SIEVE_LIMIT}...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    print(f"  5-series: {len(p5)} primes available, taking first {N_MAX}")
    print(f"  7-series: {len(p7)} primes available, taking first {N_MAX}")

    prods5, D5 = compute_products_and_D(p5, N_MAX)
    prods7, D7 = compute_products_and_D(p7, N_MAX)

    # ---- Anchor 1: D_i(n) values from v4.1 Tables 2/3 ----
    print("\n" + "=" * 72)
    print("Anchor 1: D_i(n) values (v4.1 Tables)")
    print("=" * 72)
    anchors = [
        ('D_5(30)', D5[29], 59),
        ('D_5(31)', D5[30], 62),
        ('D_5(38)', D5[37], 79),
        ('D_5(39)', D5[38], 82),
        ('D_7(36)', D7[35], 77),
        ('D_7(37)', D7[36], 79),
        ('D_7(38)', D7[37], 82),
    ]
    halt = False
    for label, got, want in anchors:
        ok = (got == want)
        flag = 'OK' if ok else 'FAIL'
        print(f"  {label} = {got}  (want {want})  {flag}")
        if not ok:
            halt = True
    if halt:
        print("  HALT: D-value anchor mismatch.")
        sys.exit(1)

    # ---- Anchor 2: mpmath at 200-dps reproduces D values ----
    print("\n" + "=" * 72)
    print("Anchor 2: mpmath at 200-dps reproduces D_i(n) for anchor indices")
    print("=" * 72)
    import mpmath
    mpmath.mp.dps = 200
    mp_targets = [
        ('5', 29, 59), ('5', 30, 62), ('5', 37, 79), ('5', 38, 82),
        ('7', 35, 77), ('7', 36, 79), ('7', 37, 82),
    ]
    for series, idx, want in mp_targets:
        prod = prods5[idx] if series == '5' else prods7[idx]
        log10p = mpmath.log10(mpmath.mpf(prod))
        d_mp = int(mpmath.floor(log10p)) + 1
        ok = (d_mp == want)
        flag = 'OK' if ok else 'FAIL'
        print(f"  D_{series}({idx + 1}) [mpmath 200-dps] = {d_mp}  "
              f"(want {want})  {flag}")
        if not ok:
            halt = True
    if halt:
        print("  HALT: mpmath D-value mismatch.")
        sys.exit(1)

    # ---- Skip sets and clusters ----
    skip5 = collect_skip_set(D5)
    skip7 = collect_skip_set(D7)
    skip_combined = sorted(skip5 | skip7)
    all_clusters = cluster_contiguous(skip_combined)
    print(f"\n  Total combined-skip clusters (any d): {len(all_clusters)}")
    print(f"  First 12 clusters: {all_clusters[:12]}")

    # ---- Anchor 3: cluster count in [90, 200] = 23 (strict reading,
    #                per addendum 10 May 2026) ----
    print("\n" + "=" * 72)
    print(f"Anchor 3: cluster count in [{D_RANGE_LO}, {D_RANGE_HI}] = 23 "
          "(strict 'entirely contained' reading)")
    print("=" * 72)
    range_indices = [i for i, c in enumerate(all_clusters)
                     if D_RANGE_LO <= c[0] and c[1] <= D_RANGE_HI]
    range_clusters = [all_clusters[i] for i in range_indices]
    print(f"  Clusters with d-range entirely in [{D_RANGE_LO}, "
          f"{D_RANGE_HI}]: {len(range_clusters)}")
    if len(range_clusters) != 23:
        print(f"  HALT: count {len(range_clusters)} != 23")
        sys.exit(1)
    print("  OK (count = 23, strict reading)")

    # Identify the merged_regime_edge cluster (lower endpoint in [90, 200],
    # upper endpoint > 200) — recorded separately, not in comparative sample
    merged_edge_clusters = [c for c in all_clusters
                            if D_RANGE_LO <= c[0] <= D_RANGE_HI
                            and c[1] > D_RANGE_HI]
    print(f"\n  merged_regime_edge clusters (lower in range, upper > "
          f"{D_RANGE_HI}): {len(merged_edge_clusters)}")
    for c in merged_edge_clusters:
        width = c[1] - c[0] + 1
        print(f"    {c}  (width = {width})")
    if len(merged_edge_clusters) != 1 or merged_edge_clusters[0] != (172, 482):
        print(f"  HALT: expected exactly one merged_regime_edge cluster "
              f"at (172, 482); got {merged_edge_clusters}")
        sys.exit(1)
    print("  OK (exactly one: (172, 482), width = 311)")

    # ---- Anchor 4: per-cluster nearest-cluster distance: median = max = 2,
    #                0/24 at distance >= 3, 0/24 at distance >= 5 ----
    print("\n" + "=" * 72)
    print(f"Anchor 4: per-cluster nearest-cluster distance over "
          f"[{D_RANGE_LO}, {D_RANGE_HI}]")
    print("=" * 72)
    range_dists = [per_cluster_distance(all_clusters, i) for i in range_indices]
    sorted_d = sorted(range_dists)
    n = len(sorted_d)
    median = sorted_d[n // 2] if n % 2 == 1 else \
        (sorted_d[n // 2 - 1] + sorted_d[n // 2]) / 2
    mx = max(range_dists)
    ge3 = sum(1 for d in range_dists if d >= 3)
    ge5 = sum(1 for d in range_dists if d >= 5)
    print(f"  median = {median} (want 2)")
    print(f"  max    = {mx} (want 2)")
    print(f"  count(>=3) = {ge3}/{n} (want 0/23)")
    print(f"  count(>=5) = {ge5}/{n} (want 0/23)")
    if median != 2 or mx != 2 or ge3 != 0 or ge5 != 0 or n != 23:
        print("  HALT: per-cluster distance anchor mismatch.")
        sys.exit(1)
    print("  OK")

    # ---- Identify boundary clusters ----
    b1_idx = next(i for i, c in enumerate(all_clusters) if c[0] <= 60 <= c[1])
    b2_idx = next(i for i, c in enumerate(all_clusters) if c[0] <= 80 <= c[1])
    b1 = all_clusters[b1_idx]
    b2 = all_clusters[b2_idx]
    print(f"\n  Boundary 1 cluster (contains d=60): {b1}")
    print(f"  Boundary 2 cluster (contains d=80): {b2}")

    # ---- Forbidden prime sets for k <= LIFT_K_EXTENDED ----
    # k coprime to P_i means no prime factor of k is in P_i.
    # P_5 = primes ≡ 5 mod 6 above 3 (5, 11, 17, 23, 29, ...)
    # P_7 = primes ≡ 1 mod 6 above 3 (7, 13, 19, 31, 37, ...)
    # Plus 2 in both forbidden sets.
    forbidden_5 = {2} | {p for p in primes if p > 3 and p % 6 == 5
                         and p <= LIFT_K_EXTENDED}
    forbidden_7 = {2} | {p for p in primes if p > 3 and p % 6 == 1
                         and p <= LIFT_K_EXTENDED}

    # ---- Lift computation per (cluster, series) ----
    def compute_lift(cluster, series, classification, S_i_local):
        """Compute minimum lift k under Convention A:
            n_i* = max{n : D_i(n) < min(S_i_local)}
        S_i_local is the cluster-local skip set for series i."""
        a, b = cluster
        if series == 5:
            D_i, prods, forbidden = D5, prods5, forbidden_5
        else:
            D_i, prods, forbidden = D7, prods7, forbidden_7

        if classification == 'coincident' and series == 7:
            req_div = 15
        else:
            req_div = 3

        n_star = find_n_star_for_skip_range(D_i, S_i_local)
        if n_star == 0:
            return None, n_star, 'no n_star (S_i_local empty or Π exceeds)'
        prod_n = prods[n_star - 1]

        for k_max in (LIFT_K_PRIMARY, LIFT_K_EXTENDED):
            k = find_min_lift(prod_n, forbidden, a, b, req_div, k_max)
            if k is not None:
                note = ''
                if k_max == LIFT_K_EXTENDED and k > LIFT_K_PRIMARY:
                    note = f'k > {LIFT_K_PRIMARY}; found in extended range'
                return k, n_star, note
        return f'none <= {LIFT_K_EXTENDED}', n_star, \
            f'no k <= {LIFT_K_EXTENDED} satisfies all conditions'

    # ---- Build the comparative table ----
    rows = []  # list of dicts, one per cluster
    table_clusters = [('B1', b1), ('B2', b2)]
    for i, c in enumerate(range_clusters):
        # Numbering starts at C_3 per the brief
        table_clusters.append((f'C_{i + 3}', c))

    for cid, cluster in table_clusters:
        a, b = cluster
        cls, S5_local, S7_local = classify_cluster(a, b, skip5, skip7)
        s5_active = bool(S5_local)
        s7_active = bool(S7_local)

        notes = []
        if cls == 'coincident' and s7_active:
            notes.append('coincident: 7-series mod-15 escalation active')
        if cls == 'partial-coincident':
            notes.append('partial-coincident: defaulted to mod-3 lifts; '
                         'flag for CinC review')

        if s5_active:
            lift5_val, n5_star, lift5_note = compute_lift(cluster, 5, cls,
                                                           S5_local)
        else:
            lift5_val, n5_star, lift5_note = 'n/a', None, ''
        if s7_active:
            lift7_val, n7_star, lift7_note = compute_lift(cluster, 7, cls,
                                                           S7_local)
        else:
            lift7_val, n7_star, lift7_note = 'n/a', None, ''

        if lift5_note:
            notes.append(f'lift5: {lift5_note}')
        if lift7_note:
            notes.append(f'lift7: {lift7_note}')

        rows.append({
            'cluster_id': cid,
            'd_lower': a,
            'd_upper': b,
            'series_5_active': s5_active,
            'series_7_active': s7_active,
            'classification': cls,
            'S5_skips': ','.join(str(d) for d in S5_local),
            'S7_skips': ','.join(str(d) for d in S7_local),
            'n5_star': n5_star if n5_star is not None else '',
            'n7_star': n7_star if n7_star is not None else '',
            'lift_5': lift5_val,
            'lift_7': lift7_val,
            'notes': '; '.join(notes),
        })

    # ---- Append merged_regime_edge row (outside comparative sample) ----
    # Per addendum 10 May 2026: (172, 482) is the leading edge of the
    # asymptotic merged regime within N_MAX = 250. Recorded as a substantive
    # separate observation; classification 'asymptotic-merged'; lifts marked
    # degenerate because cluster width 311 makes minimum-lift geometrically
    # meaningless.
    me_a, me_b = merged_edge_clusters[0]
    rows.append({
        'cluster_id': 'merged_regime_edge',
        'd_lower': me_a,
        'd_upper': me_b,
        'series_5_active': '',
        'series_7_active': '',
        'classification': 'asymptotic-merged',
        'S5_skips': '',
        'S7_skips': '',
        'n5_star': '',
        'n7_star': '',
        'lift_5': f'n/a (degenerate; cluster width {me_b - me_a + 1})',
        'lift_7': f'n/a (degenerate; cluster width {me_b - me_a + 1})',
        'notes': ('leading edge of asymptotic merged regime within '
                  f'N_MAX = {N_MAX}; digit skips contiguous, individual '
                  'cluster-and-gap structure breaks down'),
    })

    # ---- Anchor 5: B1 lifts (3, 3); B2 lifts (3, 15) ----
    print("\n" + "=" * 72)
    print("Anchor 5: boundary lift values")
    print("=" * 72)
    b1_row = next(r for r in rows if r['cluster_id'] == 'B1')
    b2_row = next(r for r in rows if r['cluster_id'] == 'B2')
    # Per addendum 2: B1 is partial-coincident under strict trinary (was
    # 'staggered' in v4.1 prose). Lifts (3, 3) per Convention A on n_i*.
    b1_ok = (b1_row['lift_5'] == 3 and b1_row['lift_7'] == 3 and
             b1_row['classification'] == 'partial-coincident')
    b2_ok = (b2_row['lift_5'] == 3 and b2_row['lift_7'] == 15 and
             b2_row['classification'] == 'coincident')
    print(f"  B1 ({b1[0]}-{b1[1]}, {b1_row['classification']}): "
          f"5-lift = {b1_row['lift_5']}, 7-lift = {b1_row['lift_7']}  "
          f"(want partial-coincident, 3, 3)  {'OK' if b1_ok else 'FAIL'}")
    print(f"  B2 ({b2[0]}-{b2[1]}, {b2_row['classification']}): "
          f"5-lift = {b2_row['lift_5']}, 7-lift = {b2_row['lift_7']}  "
          f"(want coincident, 3, 15)  {'OK' if b2_ok else 'FAIL'}")
    if not (b1_ok and b2_ok):
        print("  HALT: boundary lift anchor mismatch.")
        sys.exit(1)
    print("  OK")

    # ---- Tabulate to CSV ----
    csv_path = os.path.join(RESULTS_DIR, 'cluster_comparative_tabulation.csv')
    fieldnames = ['cluster_id', 'd_lower', 'd_upper',
                  'series_5_active', 'series_7_active', 'classification',
                  'S5_skips', 'S7_skips', 'n5_star', 'n7_star',
                  'lift_5', 'lift_7', 'notes']
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\n  Saved: {csv_path}")

    # ---- Summary block: classification breakdown, lift histograms,
    #      falsifier-test result ----
    range_rows = [r for r in rows if r['cluster_id'].startswith('C_')]
    print("\n" + "=" * 72)
    print(f"Classification breakdown "
          f"([{D_RANGE_LO}, {D_RANGE_HI}] only — {len(range_rows)} clusters)")
    print("=" * 72)
    cls_counts = {}
    for r in range_rows:
        cls_counts[r['classification']] = cls_counts.get(
            r['classification'], 0) + 1
    for cls in ('single-5', 'single-7', 'staggered', 'coincident',
                'partial-coincident'):
        print(f"  {cls:22s}: {cls_counts.get(cls, 0)}")

    # Lift histograms
    print("\n" + "=" * 72)
    print("Lift-factor distribution ([90, 200] only)")
    print("=" * 72)

    def hist(values):
        h = {}
        for v in values:
            key = str(v)
            h[key] = h.get(key, 0) + 1
        return h

    lift5_vals = [r['lift_5'] for r in range_rows if r['lift_5'] != 'n/a']
    lift7_vals = [r['lift_7'] for r in range_rows if r['lift_7'] != 'n/a']
    h5 = hist(lift5_vals)
    h7 = hist(lift7_vals)
    print(f"  5-series lifts (n={len(lift5_vals)} active 5-series clusters):")
    for k in sorted(h5.keys(), key=lambda s: (s == 'n/a', s)):
        print(f"    k = {k:>10s}: {h5[k]}")
    print(f"  7-series lifts (n={len(lift7_vals)} active 7-series clusters):")
    for k in sorted(h7.keys(), key=lambda s: (s == 'n/a', s)):
        print(f"    k = {k:>10s}: {h7[k]}")

    # ---- Specific findings vs falsifier table ----
    n_coincident = cls_counts.get('coincident', 0)
    n_partial_coincident = cls_counts.get('partial-coincident', 0)
    n_lift7_gt3 = sum(
        1 for r in range_rows
        if r['lift_7'] != 'n/a' and isinstance(r['lift_7'], int)
        and r['lift_7'] > 3
    )
    n_b2_pattern = sum(
        1 for r in range_rows
        if r['classification'] == 'coincident'
        and r['lift_5'] == 3 and r['lift_7'] == 15
    )
    n_factor15 = sum(
        1 for r in range_rows
        if r['lift_7'] == 15
    )

    # Recurrence of {staggered or partial-coincident} → coincident transition
    # between consecutive clusters in the comparative sample. Per addendum 2,
    # under v4.2 typology the B1 → B2 transition is partial-coincident →
    # coincident; the falsifier-test recurrence reads as either non-coincident
    # dual classification followed by coincident.
    recurrence = False
    consec_pairs = []
    for i in range(len(range_rows) - 1):
        a_cls = range_rows[i]['classification']
        b_cls = range_rows[i + 1]['classification']
        if a_cls in ('staggered', 'partial-coincident') \
                and b_cls == 'coincident':
            recurrence = True
            consec_pairs.append((range_rows[i]['cluster_id'],
                                 range_rows[i + 1]['cluster_id'],
                                 f'{a_cls} → {b_cls}'))

    print("\n" + "=" * 72)
    print("Specific findings vs pre-registered falsifier")
    print("=" * 72)
    print(f"  coincident-dual clusters in [90, 200]:        {n_coincident}")
    print(f"  partial-coincident clusters in [90, 200]:     "
          f"{n_partial_coincident}")
    print(f"  clusters with 7-series lift > 3:              {n_lift7_gt3}")
    print(f"  clusters reproducing B2 pattern (5=3, 7=15):  {n_b2_pattern}")
    print(f"  clusters with 7-series lift == 15:            {n_factor15}")
    print(f"  {{staggered or partial-coincident}} → coincident "
          f"consecutive transition: "
          f"{'YES' if recurrence else 'NO'}")
    if consec_pairs:
        for a, b, kind in consec_pairs:
            print(f"    transition: {a} → {b}  ({kind})")

    # Falsifier-test outcome
    # (α) ≤ 3 coincident-dual AND ≤ 4 lift7>3 AND no recurrence → confirmed
    # (β) > 6 coincident-dual OR > 6 lift7>3 OR factor-15 at >= 3 later
    #     clusters → falsified
    # else → intermediate
    print("\n" + "=" * 72)
    print("Falsifier-test outcome")
    print("=" * 72)
    alpha = (n_coincident <= 3 and n_lift7_gt3 <= 4 and not recurrence)
    beta = (n_coincident > 6 or n_lift7_gt3 > 6 or n_factor15 >= 3)
    if alpha and not beta:
        outcome = 'α (pre-registered prediction confirmed)'
    elif beta and not alpha:
        outcome = 'β (pre-registered prediction falsified — Retraction 3)'
    else:
        outcome = 'intermediate (mixed result)'
    print(f"  {outcome}")

    # ---- Save summary text for findings.md append ----
    summary_path = os.path.join(RESULTS_DIR,
                                'cluster_comparative_tabulation_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"Paper 3 v4.2 Comparative cluster tabulation — summary\n\n")
        f.write(f"Anchor verification: PASS\n")
        f.write(f"  - D_i(n) values: 7/7 OK\n")
        f.write(f"  - mpmath 200-dps: 7/7 OK\n")
        f.write(f"  - Cluster count in [90, 200]: 23/23 OK "
                f"(strict 'entirely contained' reading; addendum 10 May 2026)\n")
        f.write(f"  - merged_regime_edge: (172, 482), width 311 "
                f"(leading edge of asymptotic merged regime)\n")
        f.write(f"  - Per-cluster distance: median={median}, max={mx}, "
                f">=3: {ge3}/{n}, >=5: {ge5}/{n}  OK\n")
        f.write(f"  - Boundary 1 lifts: (5, 7) = (3, 3) staggered  OK\n")
        f.write(f"  - Boundary 2 lifts: (5, 7) = (3, 15) coincident  OK\n")
        f.write(f"\n")
        f.write(f"Cluster count in [90, 200]: 23 "
                f"(strict reading; v3.14's 24-count was loose, see addendum)\n")
        f.write(f"merged_regime_edge: (172, 482), width 311, "
                f"recorded outside the comparative sample\n")
        f.write(f"\n")
        f.write(f"Classification breakdown (24 clusters):\n")
        for cls in ('single-5', 'single-7', 'staggered', 'coincident',
                    'partial-coincident'):
            f.write(f"  {cls:22s}: {cls_counts.get(cls, 0)}\n")
        f.write(f"\n")
        f.write(f"5-series lift distribution "
                f"(n={len(lift5_vals)} active):\n")
        for k in sorted(h5.keys(), key=lambda s: (s == 'n/a', s)):
            f.write(f"  k = {k:>10s}: {h5[k]}\n")
        f.write(f"7-series lift distribution "
                f"(n={len(lift7_vals)} active):\n")
        for k in sorted(h7.keys(), key=lambda s: (s == 'n/a', s)):
            f.write(f"  k = {k:>10s}: {h7[k]}\n")
        f.write(f"\n")
        f.write(f"Specific findings:\n")
        f.write(f"  coincident-dual: {n_coincident}\n")
        f.write(f"  partial-coincident: {n_partial_coincident}\n")
        f.write(f"  7-series lift > 3: {n_lift7_gt3}\n")
        f.write(f"  B2 pattern (coincident, 5=3, 7=15): {n_b2_pattern}\n")
        f.write(f"  7-series lift == 15: {n_factor15}\n")
        f.write(f"  {{staggered or partial-coincident}} → coincident "
                f"consecutive transition: "
                f"{'YES' if recurrence else 'NO'}\n")
        if consec_pairs:
            for a, b, kind in consec_pairs:
                f.write(f"    transition: {a} → {b}  ({kind})\n")
        f.write(f"\n")
        f.write(f"Falsifier-test outcome: {outcome}\n")
    print(f"\n  Saved: {summary_path}")

    # ---- Final status ----
    print("\n" + "=" * 72)
    print("TASK — STATUS")
    print("=" * 72)
    print("Anchor verification: PASS")
    print(f"Falsifier-test result: {outcome}")
    print(f"Files produced:")
    print(f"  {csv_path}")
    print(f"  {summary_path}")
    print(f"\nEnd-of-task: PASS")


if __name__ == '__main__':
    main()
