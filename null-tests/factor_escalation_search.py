#!/usr/bin/env python3
"""
Factor-105 Escalation Search (v2.6 -> v2.7 Task 9, optional)
==============================================================

v2.6 §4.2 names a heuristic: that the required factor set S_d expands
from {3} (at 10⁶¹ scale, staggered, both series need factor 3) to {3, 5}
(at 10⁸⁰ scale, coincident, 7-series needs factor 15 = 3 × 5), and that
at some larger coincident-gap scale S_d should expand again to {3, 5, 7}
with the 7-series needing factor 105 = 3 × 5 × 7. The paper notes the
hypothesis is cheap to refute and has not been searched.

Factor Requirement (v2.6 §4 definition, per the brief):
  for series a at boundary index n, under required set S:
    k_a(S) = product of primes p ∈ S such that p ∤ Π_a(n)
  i.e. smallest squarefree integer coprime to Π_a(n) such that
  Π_a(n) × k is divisible by every prime in S.

Structural observation (before any computation):
  - p5 = {primes ≡ 5 mod 6} = {5, 11, 17, 23, 29, 41, ...}
        First prime is 5, so Π_5(n) is divisible by 5 for all n ≥ 1.
        No element ≡ 1 mod 6, so 7 ∉ p5 — Π_5(n) is NEVER divisible by 7.
  - p7 = {primes ≡ 1 mod 6} = {7, 13, 19, 31, 37, ...}
        First prime is 7, so Π_7(n) is divisible by 7 for all n ≥ 1.
        No element ≡ 5 mod 6, so 5 ∉ p7 — Π_7(n) is NEVER divisible by 5.

Consequences under S = {3, 5, 7}:
  - For the 5-series, factor 7 is ALWAYS required (since 7 ∤ Π_5);
    factor 5 is NEVER required; factor 3 may or may not be required.
    So k_5({3, 5, 7}) ∈ {7, 21}, never 105.
  - For the 7-series, factor 5 is ALWAYS required (since 5 ∤ Π_7);
    factor 7 is NEVER required; factor 3 may or may not be required.
    So k_7({3, 5, 7}) ∈ {5, 15}, never 105.

Therefore: under the brief's Factor Requirement definition, factor 105
(= 3 × 5 × 7) CANNOT be required by either series at any scale, because
each series always contains one of {5, 7} by membership of the residue
class.  This is a structural refutation, prior to any empirical search.

This script confirms the structural refutation empirically by searching
every coincident-gap run at scales beyond 10⁸⁰ (the brief-required range)
and verifying that no instance produces k_a = 105 for either series.
It also reports the actual factor pattern under S = {3, 5, 7} and the
broader distribution of mod-states at gap boundaries up to full scale.

Outputs:
  - null-tests/results/factor_escalation_search.csv   (per-gap factor data)
  - null-tests/results/factor_escalation_summary.csv  (aggregate stats)
"""
import math, time, sys, csv, os
from collections import Counter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
MIN_GAP_DIGIT = 80  # "beyond 10⁸⁰" per brief
MOD_PRIMES = [2, 3, 5, 7, 11, 13]  # small-prime mod-state tracking
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def sieve(limit):
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def compute_series_arrays(primes_in_series, mod_primes):
    """For a list of primes in a single mod-6 series, compute:
      - digit_length[n] = digit-length of Π(n) (cumulative product through index n, 1-indexed)
      - mod_state[p][n] = Π(n) mod p, for each p in mod_primes
    Index 0 = empty product (Π = 1, digit_length 1, mod = 1).
    """
    N = len(primes_in_series)
    cum_log = 0.0
    digit_lengths = [1]  # Π(0) = 1, 1 digit
    mod_state = {p: [1] for p in mod_primes}  # Π(0) = 1, all mods = 1

    for i, q in enumerate(primes_in_series, start=1):
        cum_log += math.log10(q)
        digit_lengths.append(int(cum_log) + 1)
        for p in mod_primes:
            mod_state[p].append((mod_state[p][i - 1] * (q % p)) % p)
    return digit_lengths, mod_state


def boundary_index_for_digit(digit_lengths, d):
    """Return largest index n such that digit_lengths[n] < d.
    digit_lengths is non-decreasing. Uses linear scan to handle ties cleanly.
    Returns -1 if no such index exists.
    """
    # Binary search for first index with digit_length >= d, then step back
    lo, hi = 0, len(digit_lengths)
    while lo < hi:
        mid = (lo + hi) // 2
        if digit_lengths[mid] < d:
            lo = mid + 1
        else:
            hi = mid
    return lo - 1  # last index with digit_length < d (i.e., < d_start of gap)


def required_factor(mod_state_at_boundary, required_set):
    """k = product of primes in required_set such that p ∤ Π (i.e., Π mod p != 0)."""
    k = 1
    for p in required_set:
        if mod_state_at_boundary[p] != 0:
            k *= p
    return k


def identify_gap_runs(is_gap1, is_gap2, max_d, min_d_start=1):
    """Return list of (d_start, d_end) tuples for maximal connected coincident
    gap runs with d_start >= min_d_start.
    """
    runs = []
    d = max(1, min_d_start)
    while d <= max_d:
        if is_gap1[d] == 1 and is_gap2[d] == 1:
            d_start = d
            while d <= max_d and is_gap1[d] == 1 and is_gap2[d] == 1:
                d += 1
            runs.append((d_start, d - 1))
        else:
            d += 1
    return runs


def compute_gap_arrays(series_logs):
    """series_logs is a dict {label: [log10(p) for p in series]}.
    Returns (is_gap1, is_gap2, max_d) per the existing convention."""
    sets = []
    for label, logs in series_logs.items():
        d_set = set()
        s = 0.0
        for lg in logs:
            s += lg
            d_set.add(int(s) + 1)
        sets.append(d_set)
    max_d = min(max(s) for s in sets)
    is_gaps = []
    for d_set in sets:
        ig = bytearray(b'\x01') * (max_d + 1)
        for d in d_set:
            if d <= max_d:
                ig[d] = 0
        is_gaps.append(ig)
    return is_gaps[0], is_gaps[1], max_d


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    T0 = time.time()

    print("=" * 78)
    print("FACTOR-105 ESCALATION SEARCH  (v2.6 -> v2.7 Task 9, optional)")
    print(f"  Search range: coincident gaps with d_start > {MIN_GAP_DIGIT} (beyond 10⁸⁰)")
    print(f"  Required-set candidates: S = {{3}}, {{3, 5}}, {{3, 5, 7}}")
    print(f"  Mod primes tracked: {MOD_PRIMES}")
    print("=" * 78)

    print(f"\n[1] Sieving primes to {SIEVE_LIMIT:,}...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    n_use = min(len(p5), len(p7))
    p5 = p5[:n_use]
    p7 = p7[:n_use]
    print(f"  5-series: {len(p5):,}  (starts 5, 11, 17, ...; 5 always in Π_5, 7 never)")
    print(f"  7-series: {len(p7):,}  (starts 7, 13, 19, ...; 7 always in Π_7, 5 never)")

    print(f"\n[2] Cumulative digit-length and mod-state arrays for both series...")
    t1 = time.time()
    digit_len_5, mod_state_5 = compute_series_arrays(p5, MOD_PRIMES)
    digit_len_7, mod_state_7 = compute_series_arrays(p7, MOD_PRIMES)
    print(f"  Done  [{time.time() - t1:.1f}s]")

    # Verify structural claim
    print(f"\n[2a] Structural verification of mod-state invariants:")
    invariant_5_for_5 = all(m == 0 for m in mod_state_5[5][1:])  # Π_5(n) ≡ 0 mod 5 for n ≥ 1
    invariant_5_for_7 = all(m != 0 for m in mod_state_5[7][1:])  # Π_5(n) ≢ 0 mod 7 for n ≥ 1
    invariant_7_for_7 = all(m == 0 for m in mod_state_7[7][1:])  # Π_7(n) ≡ 0 mod 7 for n ≥ 1
    invariant_7_for_5 = all(m != 0 for m in mod_state_7[5][1:])  # Π_7(n) ≢ 0 mod 5 for n ≥ 1
    print(f"  Π_5(n) ≡ 0 mod 5 for all n ≥ 1:  {invariant_5_for_5}")
    print(f"  Π_5(n) ≢ 0 mod 7 for all n ≥ 1:  {invariant_5_for_7}")
    print(f"  Π_7(n) ≡ 0 mod 7 for all n ≥ 1:  {invariant_7_for_7}")
    print(f"  Π_7(n) ≢ 0 mod 5 for all n ≥ 1:  {invariant_7_for_5}")

    print(f"\n[3] Computing gap arrays and identifying coincident gap runs...")
    t1 = time.time()
    series_logs = {'5': [math.log10(p) for p in p5],
                   '7': [math.log10(p) for p in p7]}
    is_gap1, is_gap2, max_d = compute_gap_arrays(series_logs)
    print(f"  max_d = {max_d:,}")
    runs = identify_gap_runs(is_gap1, is_gap2, max_d, min_d_start=MIN_GAP_DIGIT + 1)
    print(f"  Coincident-gap runs with d_start > {MIN_GAP_DIGIT}: {len(runs):,}  "
          f"[{time.time() - t1:.1f}s]")

    # --- For each gap run, compute boundary indices and factors ---
    print(f"\n[4] Computing factor requirements for each gap run...")
    t1 = time.time()
    REQUIRED_SETS = [
        ('S={3}', [3]),
        ('S={3,5}', [3, 5]),
        ('S={3,5,7}', [3, 5, 7]),
    ]

    rows = []
    factor_dist = {label: {'5': Counter(), '7': Counter()} for label, _ in REQUIRED_SETS}
    factor_105_hits = {'5': [], '7': []}

    for d_start, d_end in runs:
        n5 = boundary_index_for_digit(digit_len_5, d_start)
        n7 = boundary_index_for_digit(digit_len_7, d_start)
        if n5 < 0 or n7 < 0:
            continue
        ms5 = {p: mod_state_5[p][n5] for p in MOD_PRIMES}
        ms7 = {p: mod_state_7[p][n7] for p in MOD_PRIMES}

        factors_5 = {}
        factors_7 = {}
        for label, req in REQUIRED_SETS:
            k5 = required_factor(ms5, req)
            k7 = required_factor(ms7, req)
            factors_5[label] = k5
            factors_7[label] = k7
            factor_dist[label]['5'][k5] += 1
            factor_dist[label]['7'][k7] += 1
            if k5 == 105:
                factor_105_hits['5'].append((d_start, d_end, n5, n7))
            if k7 == 105:
                factor_105_hits['7'].append((d_start, d_end, n5, n7))

        rows.append({
            'd_start': d_start, 'd_end': d_end,
            'gap_len': d_end - d_start + 1,
            'n5': n5, 'n7': n7,
            'mod5_3': ms5[3], 'mod5_5': ms5[5], 'mod5_7': ms5[7],
            'mod5_11': ms5[11], 'mod5_13': ms5[13],
            'mod7_3': ms7[3], 'mod7_5': ms7[5], 'mod7_7': ms7[7],
            'mod7_11': ms7[11], 'mod7_13': ms7[13],
            'k5_S3': factors_5['S={3}'],
            'k5_S35': factors_5['S={3,5}'],
            'k5_S357': factors_5['S={3,5,7}'],
            'k7_S3': factors_7['S={3}'],
            'k7_S35': factors_7['S={3,5}'],
            'k7_S357': factors_7['S={3,5,7}'],
        })
    print(f"  Done. {len(rows):,} gap-row records  [{time.time() - t1:.1f}s]")

    # --- Show the §4.2 anchor gap (d_start = 80) for cross-check ---
    print(f"\n[4a] Cross-check against v2.6 §4.2 anchor (coincident gap at d=80-81):")
    anchor_runs = identify_gap_runs(is_gap1, is_gap2, max_d, min_d_start=1)
    anchor = next((r for r in anchor_runs if r[0] == 80), None)
    if anchor:
        n5_anch = boundary_index_for_digit(digit_len_5, 80)
        n7_anch = boundary_index_for_digit(digit_len_7, 80)
        ms5a = {p: mod_state_5[p][n5_anch] for p in MOD_PRIMES}
        ms7a = {p: mod_state_7[p][n7_anch] for p in MOD_PRIMES}
        print(f"  Gap run: digits {anchor[0]}-{anchor[1]} ({anchor[1]-anchor[0]+1} digits)")
        print(f"  5-series boundary: n={n5_anch} (Π_5({n5_anch}), digit-length "
              f"{digit_len_5[n5_anch]})")
        print(f"    mod 3 = {ms5a[3]}, mod 5 = {ms5a[5]}, mod 7 = {ms5a[7]}")
        print(f"    factor under S={{3}}    = {required_factor(ms5a, [3])}")
        print(f"    factor under S={{3,5}}  = {required_factor(ms5a, [3, 5])}")
        print(f"    factor under S={{3,5,7}} = {required_factor(ms5a, [3, 5, 7])}")
        print(f"  7-series boundary: n={n7_anch} (Π_7({n7_anch}), digit-length "
              f"{digit_len_7[n7_anch]})")
        print(f"    mod 3 = {ms7a[3]}, mod 5 = {ms7a[5]}, mod 7 = {ms7a[7]}")
        print(f"    factor under S={{3}}    = {required_factor(ms7a, [3])}")
        print(f"    factor under S={{3,5}}  = {required_factor(ms7a, [3, 5])}")
        print(f"    factor under S={{3,5,7}} = {required_factor(ms7a, [3, 5, 7])}")
        print(f"  (Paper §4.2 reports: 5-series mod 3 = 1, mod 5 = 0 -> factor 3;")
        print(f"                       7-series mod 3 = 1, mod 5 = 2 -> factor 15)")

    # --- Aggregate distribution of factors ---
    print(f"\n{'=' * 78}")
    print(f"FACTOR DISTRIBUTION ACROSS {len(rows):,} GAP RUNS (d_start > {MIN_GAP_DIGIT})")
    print(f"{'=' * 78}")
    for label, _ in REQUIRED_SETS:
        print(f"\n  Required set {label}:")
        print(f"    5-series factor counts: "
              f"{dict(sorted(factor_dist[label]['5'].items()))}")
        print(f"    7-series factor counts: "
              f"{dict(sorted(factor_dist[label]['7'].items()))}")

    # --- The key check ---
    print(f"\n{'=' * 78}")
    print(f"FACTOR-105 CHECK")
    print(f"{'=' * 78}")
    print(f"\n  Gap runs where 5-series requires factor 105 under S={{3,5,7}}: "
          f"{len(factor_105_hits['5'])}")
    print(f"  Gap runs where 7-series requires factor 105 under S={{3,5,7}}: "
          f"{len(factor_105_hits['7'])}")
    if len(factor_105_hits['5']) == 0 and len(factor_105_hits['7']) == 0:
        print(f"\n  RESULT: no escalation to factor 105 found within 3.25M digits.")
        print(f"  This is the EXPECTED outcome by structural analysis:")
        print(f"    - 5-series always has 5 in Π (so never needs factor 5 ⇒")
        print(f"      k_5(S={{3,5,7}}) ∈ {{7, 21}}, never 105)")
        print(f"    - 7-series always has 7 in Π (so never needs factor 7 ⇒")
        print(f"      k_7(S={{3,5,7}}) ∈ {{5, 15}}, never 105)")
        print(f"  The §4.2 'factor 105' hypothesis is structurally impossible")
        print(f"  under the Factor Requirement definition: each series always")
        print(f"  contains its own characteristic small prime by class membership.")
    else:
        print(f"\n  POSITIVE HITS:")
        for series, hits in factor_105_hits.items():
            for d_start, d_end, n5, n7 in hits[:10]:
                print(f"    {series}-series: gap at digits {d_start}-{d_end}, "
                      f"n5={n5}, n7={n7}")

    # --- Save per-gap CSV ---
    csv_path = os.path.join(RESULTS_DIR, 'factor_escalation_search.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['d_start', 'd_end', 'gap_len',
                    'n5', 'n7',
                    'mod5_3', 'mod5_5', 'mod5_7', 'mod5_11', 'mod5_13',
                    'mod7_3', 'mod7_5', 'mod7_7', 'mod7_11', 'mod7_13',
                    'k5_S3', 'k5_S35', 'k5_S357',
                    'k7_S3', 'k7_S35', 'k7_S357'])
        for r in rows:
            w.writerow([r['d_start'], r['d_end'], r['gap_len'], r['n5'], r['n7'],
                        r['mod5_3'], r['mod5_5'], r['mod5_7'], r['mod5_11'], r['mod5_13'],
                        r['mod7_3'], r['mod7_5'], r['mod7_7'], r['mod7_11'], r['mod7_13'],
                        r['k5_S3'], r['k5_S35'], r['k5_S357'],
                        r['k7_S3'], r['k7_S35'], r['k7_S357']])
    print(f"\n  Per-gap data saved to {csv_path}  ({len(rows):,} rows)")

    # --- Summary CSV ---
    summary_path = os.path.join(RESULTS_DIR, 'factor_escalation_summary.csv')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['required_set', 'series', 'factor', 'count'])
        for label, _ in REQUIRED_SETS:
            for series in ['5', '7']:
                for k, c in sorted(factor_dist[label][series].items()):
                    w.writerow([label, series, k, c])
    print(f"  Summary saved to {summary_path}")

    print(f"\nTotal runtime: {time.time() - T0:.1f}s")


if __name__ == '__main__':
    main()
