#!/usr/bin/env python3
"""Task X — Second coincident-gap regime (prime-set escalation).

Per pre-registration `v3_12_data/briefs/task_x_second_regime_pre_registration.md`.

Pre-registered hypothesis: the first cluster past D = 200 with 7 | lift_5
has joint LCM(lift_5, lift_7) = 105 (achieved as lift_5 = 21 = 3·7,
lift_7 = 15 = 3·5).

Structural framing: "coincident-gap regime" is keyed by the prime set in
LCM(lift_5, lift_7). First coincident regime (B2 onwards) has prime set
{3, 5}; second coincident regime (sought) has prime set {3, 5, 7}.
Carried via 5-series filler because 7 ∈ P_7 forces lift_7 coprime to 7.

Method:
  - Layer 0 (Pattern 75): reproduce all v4.2 anchors before extending.
  - Layer 1: scan all clusters in [201, D_HI] for the first cluster with
    7 | lift_5; continue to one further confirmation cluster.
  - Layer 2 (stretch): if R2_first + confirmation land, continue scan for
    first 11-in-lift_5 or 11-in-lift_7 cluster (predicted third-regime
    entry).

Merged regimes (width ≥ 100): recorded as asymptotic-merged; lifts
degenerate; excluded from the 7-in-lift_5 search.

Outputs:
  v3_12_data/results/cluster_comparative_tabulation_extended.csv
  v3_12_data/results/task_x_second_regime_summary.md
"""
import os
import sys
import csv
import math

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Python 3.11+ default int-to-str conversion cap is 4300 digits;
# at N_MAX = 3000 our running products reach ~10000+ digits.
sys.set_int_max_str_digits(0)

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve

HERE = os.path.dirname(__file__)
RESULTS_DIR = os.path.join(HERE, 'results')
CSV_OUT = os.path.join(RESULTS_DIR, 'cluster_comparative_tabulation_extended.csv')
MD_OUT = os.path.join(RESULTS_DIR, 'task_x_second_regime_summary.md')

SIEVE_LIMIT = 200_000
N_MAX = 3000
D_RANGE_LO = 90       # v4.2 anchor range
D_RANGE_HI = 200      # v4.2 anchor range
D_LO_SCAN = 201       # extended scan starts here
D_HI_TARGET = 10_000  # scan ceiling per brief
MERGED_WIDTH_THRESH = 100

LIFT_K_PRIMARY = 100
LIFT_K_EXTENDED = 1000


# ----------------------------------------------------------------------------
# Helpers — copied verbatim from cluster_comparative_tabulation.py so the
# v4.2 anchor block reproduces exactly under the same logic.
# ----------------------------------------------------------------------------

def compute_products_and_D(series, n_max):
    prods, D = [], []
    prod = 1
    for p in series[:n_max]:
        prod *= p
        prods.append(prod)
        D.append(len(str(prod)))
    return prods, D


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


def per_cluster_distance(clusters, idx):
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
    if not S_local:
        return None
    s = sorted(S_local)
    runs = []
    start = prev = s[0]
    for d in s[1:]:
        if d == prev + 1:
            prev = d
        else:
            runs.append((start, prev))
            start = prev = d
    runs.append((start, prev))
    largest = max(runs, key=lambda r: (r[1] - r[0], -r[0]))
    return largest[0]


def find_n_star_for_skip_range(D, S_local):
    threshold = largest_contiguous_run_min(S_local)
    if threshold is None:
        return 0
    for n in range(len(D), 0, -1):
        if D[n - 1] < threshold:
            return n
    return 0


def prime_factors(k):
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
    k = required_divisor
    while k <= k_max:
        if not (prime_factors(k) & forbidden_primes):
            d_lifted = len(str(prod_at_n_star * k))
            if a <= d_lifted <= b:
                return k
        k += required_divisor
    return None


def classify_cluster(a, b, skip5, skip7):
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
    if len(p5) < N_MAX or len(p7) < N_MAX:
        print(f"  HALT: insufficient primes for N_MAX = {N_MAX}")
        sys.exit(1)

    prods5, D5 = compute_products_and_D(p5, N_MAX)
    prods7, D7 = compute_products_and_D(p7, N_MAX)
    print(f"  D_5({N_MAX}) = {D5[-1]}")
    print(f"  D_7({N_MAX}) = {D7[-1]}")

    # ====================================================================
    # Layer 0 — Pattern 75 anchor verification
    # ====================================================================
    print("\n" + "=" * 72)
    print("Layer 0: v4.2 anchor verification (Pattern 75)")
    print("=" * 72)

    halt = False

    # Anchor 1: D_i(n) values
    print("\nAnchor 1: D_i(n) values (v4.1 Tables 2/3)")
    anchors = [
        ('D_5(30)', D5[29], 59),
        ('D_5(31)', D5[30], 62),
        ('D_5(38)', D5[37], 79),
        ('D_5(39)', D5[38], 82),
        ('D_7(36)', D7[35], 77),
        ('D_7(37)', D7[36], 79),
        ('D_7(38)', D7[37], 82),
    ]
    for label, got, want in anchors:
        ok = (got == want)
        print(f"  {label} = {got}  (want {want})  {'OK' if ok else 'FAIL'}")
        if not ok:
            halt = True
    if halt:
        print("  HALT: D-value anchor mismatch.")
        sys.exit(1)

    # Anchor 2: mpmath at 200-dps
    print("\nAnchor 2: mpmath at 200-dps reproduces D_i(n) for anchor indices")
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
        print(f"  D_{series}({idx + 1}) [mpmath] = {d_mp}  (want {want})  "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            halt = True
    if halt:
        print("  HALT: mpmath D-value mismatch.")
        sys.exit(1)

    # Skip sets + clusters
    skip5 = collect_skip_set(D5)
    skip7 = collect_skip_set(D7)
    skip_combined = sorted(skip5 | skip7)
    all_clusters = cluster_contiguous(skip_combined)
    print(f"\n  Total combined-skip clusters (any d): {len(all_clusters)}")

    # Anchor 3: strict-23 cluster count in [90, 200]
    print(f"\nAnchor 3: cluster count in [{D_RANGE_LO}, {D_RANGE_HI}] = 23 "
          "(strict 'entirely contained')")
    range_indices_v42 = [i for i, c in enumerate(all_clusters)
                        if D_RANGE_LO <= c[0] and c[1] <= D_RANGE_HI]
    range_clusters_v42 = [all_clusters[i] for i in range_indices_v42]
    print(f"  Clusters entirely in [{D_RANGE_LO}, {D_RANGE_HI}]: "
          f"{len(range_clusters_v42)}")
    if len(range_clusters_v42) != 23:
        print(f"  HALT: count {len(range_clusters_v42)} != 23")
        sys.exit(1)
    print("  OK")

    # Anchor 4: (172, 482) merged_regime_edge exists at N_MAX >= 250
    print("\nAnchor 4: cluster containing d=172 has lower edge 172 and upper "
          ">= 482 (v4.2 merged_regime_edge)")
    edge_cluster = next((c for c in all_clusters if c[0] <= 172 <= c[1]), None)
    if edge_cluster is None or edge_cluster[0] != 172 or edge_cluster[1] < 482:
        print(f"  HALT: expected cluster starting at 172 with upper >= 482; "
              f"got {edge_cluster}")
        sys.exit(1)
    print(f"  cluster = {edge_cluster} (width = "
          f"{edge_cluster[1] - edge_cluster[0] + 1})  OK")

    # Anchor 5: per-cluster nearest-cluster distance over [90, 200]
    print(f"\nAnchor 5: per-cluster nearest distance over [{D_RANGE_LO}, "
          f"{D_RANGE_HI}]")
    range_dists = [per_cluster_distance(all_clusters, i)
                   for i in range_indices_v42]
    sorted_d = sorted(range_dists)
    n_v42 = len(sorted_d)
    median = sorted_d[n_v42 // 2] if n_v42 % 2 == 1 else \
        (sorted_d[n_v42 // 2 - 1] + sorted_d[n_v42 // 2]) / 2
    mx = max(range_dists)
    ge3 = sum(1 for d in range_dists if d >= 3)
    ge5 = sum(1 for d in range_dists if d >= 5)
    print(f"  median = {median}  max = {mx}  ge3 = {ge3}/{n_v42}  "
          f"ge5 = {ge5}/{n_v42}")
    if median != 2 or mx != 2 or ge3 != 0 or ge5 != 0 or n_v42 != 23:
        print("  HALT: per-cluster distance anchor mismatch.")
        sys.exit(1)
    print("  OK")

    # Anchors 6, 7: B1 (3, 3) partial-coincident; B2 (3, 15) coincident
    print("\nAnchors 6, 7: B1 and B2 lifts")
    b1_idx = next(i for i, c in enumerate(all_clusters) if c[0] <= 60 <= c[1])
    b2_idx = next(i for i, c in enumerate(all_clusters) if c[0] <= 80 <= c[1])
    b1, b2 = all_clusters[b1_idx], all_clusters[b2_idx]

    forbidden_5 = {2} | {p for p in primes if p > 3 and p % 6 == 5
                         and p <= LIFT_K_EXTENDED}
    forbidden_7 = {2} | {p for p in primes if p > 3 and p % 6 == 1
                         and p <= LIFT_K_EXTENDED}

    def compute_lift(cluster, series, classification, S_i_local):
        a, b = cluster
        if series == 5:
            D_i, prods, forbidden = D5, prods5, forbidden_5
        else:
            D_i, prods, forbidden = D7, prods7, forbidden_7
        req_div = 15 if (classification == 'coincident' and series == 7) else 3
        n_star = find_n_star_for_skip_range(D_i, S_i_local)
        if n_star == 0:
            return None, n_star, 'no n_star'
        prod_n = prods[n_star - 1]
        for k_max in (LIFT_K_PRIMARY, LIFT_K_EXTENDED):
            k = find_min_lift(prod_n, forbidden, a, b, req_div, k_max)
            if k is not None:
                note = (f'k > {LIFT_K_PRIMARY}; extended'
                        if (k_max == LIFT_K_EXTENDED and k > LIFT_K_PRIMARY)
                        else '')
                return k, n_star, note
        return None, n_star, f'none <= {LIFT_K_EXTENDED}'

    for label, cl, want_class, want_l5, want_l7 in [
        ('B1', b1, 'partial-coincident', 3, 3),
        ('B2', b2, 'coincident', 3, 15),
    ]:
        cls, S5_l, S7_l = classify_cluster(cl[0], cl[1], skip5, skip7)
        l5, _, _ = compute_lift(cl, 5, cls, S5_l)
        l7, _, _ = compute_lift(cl, 7, cls, S7_l)
        ok = (cls == want_class and l5 == want_l5 and l7 == want_l7)
        print(f"  {label} {cl}: class={cls}, lift_5={l5}, lift_7={l7}  "
              f"(want {want_class}, {want_l5}, {want_l7})  "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            halt = True
    if halt:
        print("  HALT: B1/B2 lift anchor mismatch.")
        sys.exit(1)

    print("\nAll Pattern 75 anchors PASS.")

    # ====================================================================
    # Layer 1 — Extended scan for 7-in-lift_5
    # ====================================================================
    print("\n" + "=" * 72)
    print(f"Layer 1: scan clusters in [{D_LO_SCAN}, {D_HI_TARGET}]")
    print("=" * 72)

    scan_clusters = [(i, c) for i, c in enumerate(all_clusters)
                    if c[0] >= D_LO_SCAN and c[1] <= D_HI_TARGET]
    print(f"  Clusters entirely in [{D_LO_SCAN}, {D_HI_TARGET}]: "
          f"{len(scan_clusters)}")

    rows = []
    r2_first = None
    r2_confirm = None
    third_regime_first = None  # stretch: 11-in-lift

    for _, cl in scan_clusters:
        a, b = cl
        width = b - a + 1
        cls, S5_l, S7_l = classify_cluster(a, b, skip5, skip7)
        s5_active = bool(S5_l)
        s7_active = bool(S7_l)

        if width >= MERGED_WIDTH_THRESH:
            # asymptotic-merged: lifts degenerate; not part of search
            row = {
                'cluster_id': f'M_{a}_{b}',
                'd_lower': a, 'd_upper': b,
                'classification': 'asymptotic-merged',
                'S5_skips': '', 'S7_skips': '',
                'n5_star': '', 'n7_star': '',
                'prod5_mod5': '', 'prod5_mod7': '',
                'prod7_mod5': '', 'prod7_mod7': '',
                'lift_5': f'n/a (width {width})',
                'lift_7': f'n/a (width {width})',
                'lcm': '', 'prime_set': '',
                'notes': f'asymptotic-merged regime (width {width} >= '
                        f'{MERGED_WIDTH_THRESH})',
            }
            rows.append(row)
            continue

        if s5_active:
            l5, n5s, l5_note = compute_lift(cl, 5, cls, S5_l)
        else:
            l5, n5s, l5_note = None, 0, ''
        if s7_active:
            l7, n7s, l7_note = compute_lift(cl, 7, cls, S7_l)
        else:
            l7, n7s, l7_note = None, 0, ''

        # mod residues at gap boundary
        def mod_or_blank(prods, n, q):
            if n <= 0:
                return ''
            return str(prods[n - 1] % q)

        if l5 is not None and l7 is not None:
            lcm = (l5 * l7) // math.gcd(l5, l7)
            pset = sorted(prime_factors(lcm))
        elif l5 is not None:
            lcm = l5
            pset = sorted(prime_factors(l5))
        elif l7 is not None:
            lcm = l7
            pset = sorted(prime_factors(l7))
        else:
            lcm = None
            pset = []

        notes_parts = []
        if cls == 'coincident' and s7_active:
            notes_parts.append('coincident: 7-series mod-15 required-divisor')
        if cls == 'partial-coincident':
            notes_parts.append('partial-coincident: defaulted to mod-3 lifts')
        if l5_note:
            notes_parts.append(f'lift5: {l5_note}')
        if l7_note:
            notes_parts.append(f'lift7: {l7_note}')

        row = {
            'cluster_id': f'C_{a}_{b}',
            'd_lower': a, 'd_upper': b,
            'classification': cls,
            'S5_skips': ','.join(str(d) for d in S5_l),
            'S7_skips': ','.join(str(d) for d in S7_l),
            'n5_star': n5s if s5_active else '',
            'n7_star': n7s if s7_active else '',
            'prod5_mod5': mod_or_blank(prods5, n5s, 5) if s5_active else '',
            'prod5_mod7': mod_or_blank(prods5, n5s, 7) if s5_active else '',
            'prod7_mod5': mod_or_blank(prods7, n7s, 5) if s7_active else '',
            'prod7_mod7': mod_or_blank(prods7, n7s, 7) if s7_active else '',
            'lift_5': l5 if l5 is not None else 'n/a',
            'lift_7': l7 if l7 is not None else 'n/a',
            'lcm': lcm if lcm is not None else '',
            'prime_set': ','.join(str(p) for p in pset),
            'notes': '; '.join(notes_parts),
        }
        rows.append(row)

        # Search trigger: 7 | lift_5
        if l5 is not None and (l5 % 7 == 0):
            if r2_first is None:
                r2_first = row
                print(f"\n  *** R2_first found: cluster ({a}, {b}), "
                      f"lift_5 = {l5}, lift_7 = {l7}, LCM = {lcm}, "
                      f"prime_set = {pset}")
            elif r2_confirm is None:
                r2_confirm = row
                print(f"  *** R2_confirmation found: cluster ({a}, {b}), "
                      f"lift_5 = {l5}, lift_7 = {l7}, LCM = {lcm}, "
                      f"prime_set = {pset}")

        # Stretch: 11 | lift_5 or 11 | lift_7
        if (l5 is not None and l5 % 11 == 0) or \
           (l7 is not None and l7 % 11 == 0):
            if third_regime_first is None:
                third_regime_first = row
                print(f"  *** Stretch — third-regime entry: cluster "
                      f"({a}, {b}), lift_5 = {l5}, lift_7 = {l7}, "
                      f"LCM = {lcm}, prime_set = {pset}")

        # Early termination: confirmation + stretch all observed
        # (we still tabulate all clusters in CSV but no need to keep printing)

    print(f"\n  Total rows recorded: {len(rows)} (incl. asymptotic-merged)")
    n_normal = sum(1 for r in rows if r['classification'] != 'asymptotic-merged')
    print(f"  Non-degenerate clusters scanned: {n_normal}")

    # ====================================================================
    # Decision-tree outcome
    # ====================================================================
    print("\n" + "=" * 72)
    print("Decision-tree outcome")
    print("=" * 72)

    if r2_first is None:
        outcome = 'δ'
        outcome_reading = (
            "No cluster with 7 | lift_5 in [201, {0}]. The one-new-prime-"
            "per-escalation heuristic is refuted at tested scale, or the "
            "second coincident regime sits past D ≈ {0}.".format(D_HI_TARGET)
        )
    else:
        l5 = r2_first['lift_5']
        l7 = r2_first['lift_7']
        lcm = r2_first['lcm']
        pset = set(r2_first['prime_set'].split(','))
        if pset == {'3', '5', '7'} and lcm == 105:
            outcome = 'α'
            outcome_reading = (
                f"R2_first lcm = 105 exactly (lift_5 = {l5} = 3·7, "
                f"lift_7 = {l7} = 3·5). One-new-prime-per-escalation "
                "heuristic confirmed at three data points."
            )
        elif pset == {'3', '5', '7'}:
            outcome = 'β'
            outcome_reading = (
                f"R2_first lcm = {lcm} (lift_5 = {l5}, lift_7 = {l7}); "
                "prime set = {{3, 5, 7}} but with power escalation beyond "
                "the lowest LCM of 105. Heuristic holds on prime-set axis."
            )
        else:
            outcome = 'γ'
            outcome_reading = (
                f"R2_first prime set = {sorted(pset)} (lcm = {lcm}); "
                "introduces additional prime(s) beyond {{3, 5, 7}}. "
                "Heuristic refined — escalations can multi-jump on the "
                "prime-set axis."
            )

    print(f"\n  Outcome: ({outcome})")
    print(f"  Reading: {outcome_reading}")

    # ====================================================================
    # Save CSV
    # ====================================================================
    with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:
        cols = ['cluster_id', 'd_lower', 'd_upper', 'classification',
                'S5_skips', 'S7_skips', 'n5_star', 'n7_star',
                'prod5_mod5', 'prod5_mod7', 'prod7_mod5', 'prod7_mod7',
                'lift_5', 'lift_7', 'lcm', 'prime_set', 'notes']
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\n  Saved: {CSV_OUT}")

    # ====================================================================
    # Save summary markdown
    # ====================================================================
    lines = []
    lines.append("# Task X — Second coincident-gap regime summary\n")
    lines.append(f"**Date:** 11 May 2026\n")
    lines.append(f"**N_MAX:** {N_MAX} per series\n")
    lines.append(f"**D_5({N_MAX}):** {D5[-1]} | **D_7({N_MAX}):** {D7[-1]}\n")
    lines.append(f"**Scan range:** D ∈ [{D_LO_SCAN}, {D_HI_TARGET}]\n")
    lines.append(f"**Clusters scanned (non-degenerate):** {n_normal}\n")
    lines.append("\n## Anchor verification\n\nAll v4.2 anchors PASS.\n")

    lines.append("\n## Primary observation — R2_first\n")
    if r2_first is None:
        lines.append("No cluster with 7 | lift_5 found in scan range.\n")
    else:
        lines.append(
            f"- Cluster: ({r2_first['d_lower']}, {r2_first['d_upper']}), "
            f"classification: {r2_first['classification']}\n"
            f"- lift_5 = {r2_first['lift_5']}, lift_7 = {r2_first['lift_7']}, "
            f"LCM = {r2_first['lcm']}, prime set = {{{r2_first['prime_set']}}}\n"
            f"- n_5* = {r2_first['n5_star']}, n_7* = {r2_first['n7_star']}\n"
            f"- Π_5(n_5*) mod 5 = {r2_first['prod5_mod5']}, "
            f"mod 7 = {r2_first['prod5_mod7']}\n"
            f"- Π_7(n_7*) mod 5 = {r2_first['prod7_mod5']}, "
            f"mod 7 = {r2_first['prod7_mod7']}\n"
            f"- S5_skips: {r2_first['S5_skips']}; "
            f"S7_skips: {r2_first['S7_skips']}\n"
        )

    lines.append("\n## Confirmation cluster — R2_confirm\n")
    if r2_confirm is None:
        lines.append(
            "No second cluster with 7 | lift_5 found in scan range.\n"
        )
    else:
        lines.append(
            f"- Cluster: ({r2_confirm['d_lower']}, {r2_confirm['d_upper']}), "
            f"classification: {r2_confirm['classification']}\n"
            f"- lift_5 = {r2_confirm['lift_5']}, "
            f"lift_7 = {r2_confirm['lift_7']}, "
            f"LCM = {r2_confirm['lcm']}, "
            f"prime set = {{{r2_confirm['prime_set']}}}\n"
        )

    lines.append("\n## Stretch — third-regime entry (11-in-lift)\n")
    if third_regime_first is None:
        lines.append(
            "No cluster with 11 | lift_5 or 11 | lift_7 found in scan range.\n"
        )
    else:
        lines.append(
            f"- Cluster: ({third_regime_first['d_lower']}, "
            f"{third_regime_first['d_upper']}), "
            f"classification: {third_regime_first['classification']}\n"
            f"- lift_5 = {third_regime_first['lift_5']}, "
            f"lift_7 = {third_regime_first['lift_7']}, "
            f"LCM = {third_regime_first['lcm']}, "
            f"prime set = {{{third_regime_first['prime_set']}}}\n"
        )

    lines.append(f"\n## Decision-tree outcome: ({outcome})\n\n{outcome_reading}\n")

    with open(MD_OUT, 'w', encoding='utf-8') as f:
        f.write(''.join(lines))
    print(f"  Saved: {MD_OUT}")

    print(f"\nTASK X — STATUS: COMPLETE  (outcome: {outcome})\n")


if __name__ == '__main__':
    main()
