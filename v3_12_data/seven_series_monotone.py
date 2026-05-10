#!/usr/bin/env python3
"""Paper 199 v1.1 Task 2 — 7-series monotone-ordering test (GAP/FALSIFIER).

Mr Adversary v3.18 GAP/FALSIFIER query: discriminate §10 Q1 candidates
(b) "structural-position" (5-series-specific) from (d) "any monotone
ordering" (residue-class general). Cheap discriminant: run the §6.1
(formerly §6.5.1) test on the 7-series.

Method (per brief):
  1. First 1000 7-series primes (p ≡ 1 mod 6, sorted ascending).
     None ramified (no p=5 in 7-series), so χ₅(p) ∈ {+1, -1} always —
     no Def A/B/C distinction needed.
  2. For each window n ∈ {20, 33, 50, 70, 90, 100} (matching 5-series):
     - Natural-ordering tie count
     - Shuffle distribution: 1000 random permutations
     - z(n) = (T_natural − T_shuffle_mean) / T_shuffle_std
  3. Multi-window aggregate (Statistic A only — Stouffer omitted per
     Paper 199 v1.0 §6.1 editorial decision):
     - Per-trial: per-window z, take max-z across windows
     - 1000 max-z values form null distribution
     - Empirical p of natural max-z against this null
  4. Structured-ordering controls at n=33:
     - Reversed-size (descending size order)
     - Every-other-prime (1-indexed odds then evens)
     - Index-interleaved (first half / second half alternated)
     - For each, compute z(33) under the same shuffle baseline

Pre-registered prediction (binding before computation):
  - Q1(b) "structural-position": predicted |z(33)| ≤ 1.0
    (7-series has no monotone-ordering structure to be specific to)
  - Q1(d) "any monotone ordering": predicted |z(33)| ≥ 1.5
    (deviation comparable in magnitude to 5-series; sign may differ)

Falsifier table:
  |z(33)| ≤ 1.0           → Q1(b) favoured
  1.0 < |z(33)| < 1.5     → inconclusive; aggregate p decides
  |z(33)| ≥ 1.5           → Q1(d) favoured (parsimonious)
  |z(33)| ≥ 1.5 + structured controls match 5-series pattern → strong Q1(d)
  |z(33)| ≥ 1.5 + controls don't match → mixed, new reading

5-series benchmark (anchors to reproduce, halt if fail by ±0.05 on z
or ±0.005 on p):
  - Def C n=33: T=13, shuffle mean ≈ 6.185, std ≈ 2.780, z ≈ 2.45
  - Def A n=90: z = 3.61
  - Multi-window max-z empirical p (Def C) = 0.005

Seed convention: trial * 137 + 42 (matches v3.11/v3.12/v3.13/v3.14).
"""
import csv
import math
import os
import random
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve, chi5, five_series_primes
from task1_orderings import (
    chi_seq_def_A, chi_seq_def_C,
    order_natural, order_reversed_size, order_every_other,
    order_index_interleaved,
    tie_count, shuffle_baseline, stats, z_and_p,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

SIEVE_LIMIT = 200_000   # > p_max for first 1000 7-series primes (~7,919 ish)
N_FOR_7 = 1000          # first 1000 7-series primes
WINDOWS = [20, 33, 50, 70, 90, 100]   # match 5-series test windows
N_SHUFFLE = 1000        # match v3.12/v3.13 shuffle baseline
ANCHOR_TOL_Z = 0.05
ANCHOR_TOL_P = 0.005

# 5-series benchmark anchors
ANCHOR_5S_DEF_C_N33 = {'T': 13, 'shuf_mean': 6.185, 'shuf_std': 2.780, 'z': 2.45}
ANCHOR_5S_DEF_A_N90_Z = 3.61
ANCHOR_5S_MULTIWINDOW_P_DEF_C = 0.005


def seven_series_primes(primes):
    """7-series primes per repo convention: p > 3 and p % 6 == 1.

    First few: 7, 13, 19, 31, 37, 43, 61, 67, 73, 79, ...
    None of these are χ₅-ramified (only p=5 is, and 5 % 6 == 5).
    """
    return [p for p in primes if p > 3 and p % 6 == 1]


def per_window_z_under_shuffle(chi_seq, perm):
    """For one shuffle perm, walk the running sum and record per-window
    counts at the key window-lengths in WINDOWS. Returns dict {n: T(n)}.

    Note: for the 7-series (length-1000 chi_seq), each window n means
    'first n positions of the permuted sequence.' Tie count at window
    n = number of positions k ∈ [1, n] where running sum is 0.
    """
    counts = {}
    s = 0
    n_set = set(WINDOWS)
    n_max = max(WINDOWS)
    ties = 0
    for k, idx in enumerate(perm[:n_max], start=1):
        s += chi_seq[idx]
        if s == 0:
            ties += 1
        if k in n_set:
            counts[k] = ties
    return counts


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print('=' * 78)
    print('Paper 199 v1.1 Task 2 — 7-series monotone-ordering test')
    print('=' * 78)
    print(f"  Windows W : {WINDOWS}")
    print(f"  N_shuffle : {N_SHUFFLE:,}")
    print(f"  Sieve     : {SIEVE_LIMIT:,}")

    # ---- Sieve and build prime sets ----
    print(f"\nSieving primes up to {SIEVE_LIMIT:,} ...")
    primes = sieve(SIEVE_LIMIT)
    p5 = five_series_primes(primes)
    p7 = seven_series_primes(primes)
    print(f"  Total primes      : {len(primes):,}")
    print(f"  5-series primes   : {len(p5):,}")
    print(f"  7-series primes   : {len(p7):,}")
    if len(p7) < N_FOR_7:
        print(f"  HALT: need ≥ {N_FOR_7} 7-series primes; have {len(p7):,}")
        sys.exit(1)
    p7_first = p7[:N_FOR_7]
    print(f"  7-series p_min={p7_first[0]}, p_max={p7_first[-1]:,}")

    # ---- Anchor reproduction (5-series) ----
    print('\n' + '=' * 78)
    print('Anchor reproduction — 5-series benchmark')
    print('=' * 78)
    fail = False

    # 5-series Def C n=33: T=13, mean ≈ 6.185, std ≈ 2.780, z ≈ 2.45
    chi_5s_C_33 = chi_seq_def_C(p5, 33)
    L = len(chi_5s_C_33)
    T_natural_5s_C_33 = tie_count(chi_5s_C_33, order_natural(L))
    shuf_5s_C_33 = shuffle_baseline(chi_5s_C_33, N_SHUFFLE)
    mean_5s_C_33, std_5s_C_33, _ = stats(shuf_5s_C_33)
    z_5s_C_33 = (T_natural_5s_C_33 - mean_5s_C_33) / std_5s_C_33
    print(f"\n  5-series Def C, n=33:")
    print(f"    T_natural   = {T_natural_5s_C_33}  (anchor {ANCHOR_5S_DEF_C_N33['T']})")
    print(f"    shuf_mean   = {mean_5s_C_33:.3f}  (anchor {ANCHOR_5S_DEF_C_N33['shuf_mean']:.3f})")
    print(f"    shuf_std    = {std_5s_C_33:.3f}  (anchor {ANCHOR_5S_DEF_C_N33['shuf_std']:.3f})")
    print(f"    z           = {z_5s_C_33:.3f}  (anchor {ANCHOR_5S_DEF_C_N33['z']:.3f})")
    if T_natural_5s_C_33 != ANCHOR_5S_DEF_C_N33['T']:
        print(f"    FAIL: T mismatch")
        fail = True
    if abs(z_5s_C_33 - ANCHOR_5S_DEF_C_N33['z']) > ANCHOR_TOL_Z:
        print(f"    FAIL: z mismatch (Δ={abs(z_5s_C_33 - ANCHOR_5S_DEF_C_N33['z']):.3f} > {ANCHOR_TOL_Z})")
        fail = True
    if not fail:
        print(f"    OK")

    # 5-series Def A n=90: z = 3.61
    chi_5s_A_90 = chi_seq_def_A(p5, 90)
    L = len(chi_5s_A_90)
    T_natural_5s_A_90 = tie_count(chi_5s_A_90, order_natural(L))
    shuf_5s_A_90 = shuffle_baseline(chi_5s_A_90, N_SHUFFLE)
    mean_5s_A_90, std_5s_A_90, _ = stats(shuf_5s_A_90)
    z_5s_A_90 = (T_natural_5s_A_90 - mean_5s_A_90) / std_5s_A_90
    print(f"\n  5-series Def A, n=90:")
    print(f"    T_natural   = {T_natural_5s_A_90}")
    print(f"    z           = {z_5s_A_90:.3f}  (anchor {ANCHOR_5S_DEF_A_N90_Z:.3f})")
    if abs(z_5s_A_90 - ANCHOR_5S_DEF_A_N90_Z) > ANCHOR_TOL_Z:
        print(f"    FAIL: z mismatch (Δ={abs(z_5s_A_90 - ANCHOR_5S_DEF_A_N90_Z):.3f} > {ANCHOR_TOL_Z})")
        fail = True
    else:
        print(f"    OK")

    # 5-series multi-window max-z empirical p (Def C) = 0.005
    print(f"\n  5-series multi-window max-z empirical p (Def C):")
    chi_5s_C_per_n = {n: chi_seq_def_C(p5, n) for n in WINDOWS}
    nat_z_5s_C = {}
    counts_per_window_5s_C = {n: shuffle_baseline(chi_5s_C_per_n[n], N_SHUFFLE)
                              for n in WINDOWS}
    means_5s_C = {n: stats(counts_per_window_5s_C[n])[0] for n in WINDOWS}
    stds_5s_C = {n: stats(counts_per_window_5s_C[n])[1] for n in WINDOWS}
    for n in WINDOWS:
        cs = chi_5s_C_per_n[n]
        T = tie_count(cs, order_natural(len(cs)))
        nat_z_5s_C[n] = ((T - means_5s_C[n]) / stds_5s_C[n]
                         if stds_5s_C[n] > 0 else 0.0)
    natural_max_z_5s_C = max(nat_z_5s_C.values())
    natural_max_window_5s_C = max(WINDOWS, key=lambda n: nat_z_5s_C[n])
    # Per-trial max-z null
    max_z_null_5s_C = []
    for i in range(N_SHUFFLE):
        zs = []
        for n in WINDOWS:
            if stds_5s_C[n] > 0:
                zs.append((counts_per_window_5s_C[n][i] - means_5s_C[n])
                          / stds_5s_C[n])
            else:
                zs.append(0.0)
        max_z_null_5s_C.append(max(zs))
    p_max_z_5s_C = sum(1 for z in max_z_null_5s_C
                       if z >= natural_max_z_5s_C) / N_SHUFFLE
    print(f"    Natural max-z = {natural_max_z_5s_C:.3f} at n={natural_max_window_5s_C}")
    print(f"    Empirical p   = {p_max_z_5s_C:.4f}  "
          f"(anchor {ANCHOR_5S_MULTIWINDOW_P_DEF_C})")
    if abs(p_max_z_5s_C - ANCHOR_5S_MULTIWINDOW_P_DEF_C) > ANCHOR_TOL_P:
        print(f"    FAIL: p mismatch (Δ={abs(p_max_z_5s_C - ANCHOR_5S_MULTIWINDOW_P_DEF_C):.4f} > {ANCHOR_TOL_P})")
        fail = True
    else:
        print(f"    OK")

    if fail:
        print('\n  HALT: 5-series anchor mismatch.')
        sys.exit(1)
    print('\n  All 5-series anchors reproduce within tolerance.')

    # ---- 7-series core test ----
    print('\n' + '=' * 78)
    print('7-series natural-vs-shuffle (single-definition: χ₅ ∈ {+1, -1})')
    print('=' * 78)

    # Build chi sequences per window (subsets of first 100 7-series primes, the
    # max window size). Note: 7-series has no ramification, so each chi_seq is
    # a strict ±1 vector of length n.
    chi_7s_per_n = {n: [chi5(p) for p in p7_first[:n]] for n in WINDOWS}

    # Per-window shuffle distributions
    counts_per_window_7s = {}
    nat_T_7s = {}
    nat_z_7s = {}
    means_7s = {}
    stds_7s = {}
    print(f"\n  {'n':>4}  {'L':>4}  {'T_nat':>5}  {'shuf_mean':>9}  "
          f"{'shuf_std':>8}  {'z_nat':>7}  {'p_ge':>7}")
    for n in WINDOWS:
        cs = chi_7s_per_n[n]
        L = len(cs)
        nat_T_7s[n] = tie_count(cs, order_natural(L))
        counts_per_window_7s[n] = shuffle_baseline(cs, N_SHUFFLE)
        m, s, _ = stats(counts_per_window_7s[n])
        means_7s[n] = m
        stds_7s[n] = s
        z = (nat_T_7s[n] - m) / s if s > 0 else 0.0
        nat_z_7s[n] = z
        p_ge = (sum(1 for x in counts_per_window_7s[n] if x >= nat_T_7s[n])
                / N_SHUFFLE)
        print(f"  {n:>4}  {L:>4}  {nat_T_7s[n]:>5}  {m:>9.3f}  "
              f"{s:>8.3f}  {z:>+7.3f}  {p_ge:>7.4f}")

    # ---- Multi-window aggregate (Statistic A) ----
    print('\n' + '=' * 78)
    print('7-series multi-window aggregate test (Statistic A only)')
    print('=' * 78)
    natural_max_z_7s = max(nat_z_7s.values())
    natural_max_window_7s = max(WINDOWS, key=lambda n: nat_z_7s[n])
    natural_min_z_7s = min(nat_z_7s.values())
    natural_min_window_7s = min(WINDOWS, key=lambda n: nat_z_7s[n])
    natural_absmax_z_7s = max(natural_max_z_7s, abs(natural_min_z_7s))

    max_z_null_7s = []
    absmax_z_null_7s = []
    for i in range(N_SHUFFLE):
        zs = []
        for n in WINDOWS:
            if stds_7s[n] > 0:
                zs.append((counts_per_window_7s[n][i] - means_7s[n])
                          / stds_7s[n])
            else:
                zs.append(0.0)
        max_z_null_7s.append(max(zs))
        absmax_z_null_7s.append(max(abs(z) for z in zs))

    p_maxz_7s = (sum(1 for z in max_z_null_7s if z >= natural_max_z_7s)
                 / N_SHUFFLE)
    p_absmaxz_7s = (sum(1 for z in absmax_z_null_7s
                        if z >= natural_absmax_z_7s) / N_SHUFFLE)

    print(f"\n  Natural max-z   = {natural_max_z_7s:+.3f}  (at n={natural_max_window_7s})")
    print(f"  Natural min-z   = {natural_min_z_7s:+.3f}  (at n={natural_min_window_7s})")
    print(f"  Natural |z|max  = {natural_absmax_z_7s:.3f}")
    print(f"  Empirical p (max-z ≥ natural)         = {p_maxz_7s:.4f}")
    print(f"  Empirical p (|z|max ≥ natural |z|max) = {p_absmaxz_7s:.4f}")

    # Null percentiles
    sorted_max_z = sorted(max_z_null_7s)
    sorted_absmax_z = sorted(absmax_z_null_7s)

    def pct(arr, q):
        idx = q * (len(arr) - 1)
        lo = int(idx)
        hi = min(lo + 1, len(arr) - 1)
        return arr[lo] * (hi - idx) + arr[hi] * (idx - lo) if hi != lo else arr[lo]
    print(f"\n  max-z null percentiles:")
    for q in (0.05, 0.50, 0.95, 0.99):
        print(f"    {q*100:>4.0f}th = {pct(sorted_max_z, q):+.3f}")
    print(f"    max  = {sorted_max_z[-1]:+.3f}")
    print(f"\n  |z|max null percentiles:")
    for q in (0.05, 0.50, 0.95, 0.99):
        print(f"    {q*100:>4.0f}th = {pct(sorted_absmax_z, q):.3f}")
    print(f"    max  = {sorted_absmax_z[-1]:.3f}")

    # ---- Pre-registered |z(33)| classification ----
    z_33_7s = nat_z_7s[33]
    abs_z_33_7s = abs(z_33_7s)
    print('\n' + '=' * 78)
    print('Pre-registered falsifier-table outcome: |z(33)| classification')
    print('=' * 78)
    print(f"  Natural z(33) for 7-series = {z_33_7s:+.4f}")
    print(f"  |z(33)| = {abs_z_33_7s:.4f}")
    print(f"  Pre-registered thresholds:")
    print(f"    |z(33)| ≤ 1.0   → Q1(b) structural-position favoured")
    print(f"    1.0 < |z(33)| < 1.5  → inconclusive, aggregate p decides")
    print(f"    |z(33)| ≥ 1.5   → Q1(d) any-monotone-ordering favoured")
    if abs_z_33_7s <= 1.0:
        primary = 'Row 1: Q1(b) "structural-position" favoured (|z(33)| ≤ 1.0)'
        primary_tag = 'Q1(b)'
    elif abs_z_33_7s < 1.5:
        primary = ('Row 2: Inconclusive (1.0 < |z(33)| < 1.5); aggregate p '
                   f'is deciding (max-z p = {p_maxz_7s:.4f}, |z|max p = '
                   f'{p_absmaxz_7s:.4f})')
        primary_tag = 'inconclusive'
    else:
        primary = 'Row 3: Q1(d) "any-monotone-ordering" favoured (|z(33)| ≥ 1.5)'
        primary_tag = 'Q1(d)'
    print(f"\n  → {primary}")

    # ---- Structured-ordering controls at n=33 ----
    print('\n' + '=' * 78)
    print('Structured-ordering controls (at n=33, 7-series)')
    print('=' * 78)
    chi_7s_33 = chi_7s_per_n[33]
    L_33 = len(chi_7s_33)
    shuf_7s_33 = counts_per_window_7s[33]
    mean_33, std_33, _ = stats(shuf_7s_33)

    structured_orderings = [
        ('natural', order_natural(L_33)),
        ('reversed_size', order_reversed_size(L_33)),
        ('every_other', order_every_other(L_33)),
        ('index_interleaved', order_index_interleaved(L_33)),
    ]
    print(f"\n  Per-ordering at n=33 (shuf_mean={mean_33:.3f}, "
          f"shuf_std={std_33:.3f}):")
    print(f"  {'ordering':>22}  {'T':>4}  {'z':>7}  {'|z|':>7}")
    structured_results = {}
    for name, perm in structured_orderings:
        T = tie_count(chi_7s_33, perm)
        z = (T - mean_33) / std_33 if std_33 > 0 else 0.0
        structured_results[name] = {'T': T, 'z': z, 'abs_z': abs(z)}
        print(f"  {name:>22}  {T:>4}  {z:>+7.3f}  {abs(z):>7.3f}")

    # 5-series structured-ordering pattern reference (from v3.12 task1_orderings):
    # Def C n=33: natural=2.45, reversed_size=2.45, every_other=-0.43,
    #             index_interleaved=1.90 (per v3.12 findings.md table)
    print(f"\n  5-series Def C n=33 reference (from v3.12 task1_orderings):")
    print(f"    natural=2.45, reversed_size=2.45, every_other=-0.43, "
          f"index_interleaved=1.90")
    print(f"  Pattern: natural ≈ reversed_size (both monotone) >> permuted controls")

    # Compare 7-series structured-ordering pattern to 5-series
    nat_z_7 = structured_results['natural']['z']
    rev_z_7 = structured_results['reversed_size']['z']
    eo_z_7 = structured_results['every_other']['z']
    il_z_7 = structured_results['index_interleaved']['z']
    monotone_align = abs(nat_z_7 - rev_z_7) < 0.5
    permuted_smaller = (abs(eo_z_7) < abs(nat_z_7) - 0.3
                        and abs(il_z_7) < abs(nat_z_7) - 0.3)
    pattern_match = monotone_align and permuted_smaller
    print(f"\n  7-series structured-ordering pattern check:")
    print(f"    natural z = {nat_z_7:+.3f}, reversed_size z = {rev_z_7:+.3f}: "
          f"|Δ| = {abs(nat_z_7 - rev_z_7):.3f}  "
          f"({'≈ aligned' if monotone_align else 'NOT aligned'})")
    print(f"    every_other z = {eo_z_7:+.3f}, index_interleaved z = {il_z_7:+.3f}: "
          f"{'both substantially smaller |z|' if permuted_smaller else 'NOT both substantially smaller'}")
    print(f"  Pattern matches 5-series? {'YES' if pattern_match else 'NO'}")

    # ---- Updated falsifier interpretation given controls ----
    if primary_tag == 'Q1(d)':
        if pattern_match:
            updated = ('STRONG Q1(d) (Row 4): |z(33)| ≥ 1.5 AND structured '
                       'controls match 5-series pattern (monotone orderings '
                       'aligned, permuted controls weaker).')
        else:
            updated = ('MIXED (Row 5): |z(33)| ≥ 1.5 BUT structured controls '
                       'do NOT match 5-series pattern. New reading suggested; '
                       'CinC interprets.')
    elif primary_tag == 'inconclusive':
        # Aggregate p as deciding statistic
        aggregate_p = min(p_maxz_7s, p_absmaxz_7s)
        if aggregate_p <= 0.05:
            updated = (f'Inconclusive |z(33)|, but aggregate p = '
                       f'{aggregate_p:.4f} ≤ 0.05 → lean toward Q1(d).')
        elif aggregate_p > 0.10:
            updated = (f'Inconclusive |z(33)|, aggregate p = {aggregate_p:.4f} '
                       f'> 0.10 → lean toward Q1(b).')
        else:
            updated = (f'Inconclusive |z(33)|, aggregate p = {aggregate_p:.4f} '
                       f'∈ (0.05, 0.10] → genuinely indeterminate.')
    else:  # Q1(b)
        updated = (f'Q1(b) "structural-position" favoured: |z(33)| = '
                   f'{abs_z_33_7s:.3f} ≤ 1.0. The 5-series tight-oscillation '
                   f'regime is 5-series-specific; not generalised to '
                   f'monotone size-orderings of mod-6 prime sequences.')
    print(f"\n  Updated falsifier verdict: {updated}")

    # ---- CSVs ----
    csv1 = os.path.join(RESULTS_DIR, 'seven_series_monotone_results.csv')
    with open(csv1, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['ordering', 'window_n', 'T_observed', 'T_shuffle_mean',
                    'T_shuffle_std', 'z', 'p_one_sided'])
        # natural ordering at all windows
        for n in WINDOWS:
            T = nat_T_7s[n]
            m = means_7s[n]
            s = stds_7s[n]
            z = nat_z_7s[n]
            p_ge = (sum(1 for x in counts_per_window_7s[n] if x >= T)
                    / N_SHUFFLE)
            w.writerow(['natural', n, T, f"{m:.6f}", f"{s:.6f}",
                        f"{z:.6f}", f"{p_ge:.6f}"])
        # structured orderings at n=33 only
        for name, perm in structured_orderings:
            if name == 'natural':
                continue
            T = structured_results[name]['T']
            z = structured_results[name]['z']
            p_ge = sum(1 for x in shuf_7s_33 if x >= T) / N_SHUFFLE
            w.writerow([name, 33, T, f"{mean_33:.6f}", f"{std_33:.6f}",
                        f"{z:.6f}", f"{p_ge:.6f}"])
    print(f"\n  Saved: {csv1}")

    csv2 = os.path.join(RESULTS_DIR, 'seven_series_aggregate_null.csv')
    with open(csv2, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['ordering', 'max_z_observed', 'max_z_null_95th',
                    'max_z_null_99p5th', 'empirical_p',
                    'absmax_z_observed', 'absmax_z_null_95th',
                    'absmax_z_null_99p5th', 'empirical_p_absmax'])
        w.writerow(['natural',
                    f"{natural_max_z_7s:.6f}",
                    f"{pct(sorted_max_z, 0.95):.6f}",
                    f"{pct(sorted_max_z, 0.995):.6f}",
                    f"{p_maxz_7s:.6f}",
                    f"{natural_absmax_z_7s:.6f}",
                    f"{pct(sorted_absmax_z, 0.95):.6f}",
                    f"{pct(sorted_absmax_z, 0.995):.6f}",
                    f"{p_absmaxz_7s:.6f}"])
    print(f"  Saved: {csv2}")

    # ---- Plot ----
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print('  [warning] matplotlib unavailable; skipping plot')
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: per-window z for 7-series natural with 5-series Def C overlay
    ax = axes[0]
    ns = WINDOWS
    z7 = [nat_z_7s[n] for n in WINDOWS]
    z5_C = [nat_z_5s_C[n] for n in WINDOWS]
    ax.plot(ns, z7, 'o-', color='#dd8452', markersize=10, linewidth=1.6,
            label='7-series natural z')
    ax.plot(ns, z5_C, 's--', color='#4c72b0', markersize=8, linewidth=1.2,
            alpha=0.7, label='5-series Def C natural z (reference)')
    ax.axhline(0, color='black', linewidth=0.6)
    ax.axhline(1.0, color='gray', linestyle=':', linewidth=1.0,
               label='Q1(b) threshold (|z(33)| = 1.0)')
    ax.axhline(-1.0, color='gray', linestyle=':', linewidth=1.0)
    ax.axhline(1.5, color='red', linestyle=':', linewidth=1.0,
               label='Q1(d) threshold (|z(33)| = 1.5)')
    ax.axhline(-1.5, color='red', linestyle=':', linewidth=1.0)
    ax.set_xticks(ns)
    ax.set_xticklabels([str(n) for n in ns])
    ax.set_xlabel('Window n')
    ax.set_ylabel('Natural-ordering z')
    ax.set_title(f'Per-window z: 7-series vs 5-series\n'
                 f'7-series z(33) = {z_33_7s:+.3f}, |z(33)| = {abs_z_33_7s:.3f}')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=9)

    # Right: max-z null distribution for 7-series with natural marked
    ax = axes[1]
    bins = np.linspace(min(min(max_z_null_7s), -3.5),
                       max(max(max_z_null_7s), natural_max_z_7s) + 0.3, 35)
    ax.hist(max_z_null_7s, bins=bins, color='#dd8452', alpha=0.85,
            edgecolor='#7f3a17', linewidth=0.4,
            label=f'7-series max-z null (K={N_SHUFFLE})')
    ax.axvline(natural_max_z_7s, color='red', linestyle='--', linewidth=1.7,
               label=f'natural max-z = {natural_max_z_7s:+.3f}, '
                     f'p = {p_maxz_7s:.4f}')
    ax.axvline(pct(sorted_max_z, 0.95), color='gray', linestyle=':',
               linewidth=1.3, label=f'null 95th = {pct(sorted_max_z, 0.95):+.3f}')
    ax.set_xlabel('Max-z over 6 windows')
    ax.set_ylabel(f'Count out of K = {N_SHUFFLE}')
    ax.set_title('7-series multi-window aggregate (Statistic A)')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)

    fig.suptitle('Paper 199 v1.1 Task 2 — 7-series monotone-ordering test')
    fig.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, 'seven_series_monotone.png')
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"  Saved: {plot_path}")


if __name__ == '__main__':
    main()
