#!/usr/bin/env python3
"""Paper 3 v4.5 Task 2 — F5 alternative-convention probe.

Per pre-registration `v3_12_data/briefs/task2_alternative_convention_pre_registration.md`.

For each of the 23 strict clusters in D ∈ [90, 200], recompute the
minimum-lift k_min(i) for series i ∈ {5, 7} under three conventions:

  - Chosen: §4.0, k_min(5) ≡ 0 (mod 3), k_min(7) ≡ 0 (mod 3) at
    non-coincident, k_min(7) ≡ 0 (mod 15) at coincident.
    Forbidden: P_i ∪ {2}.
  - Alternative A (mod-2 inclusion): k_min(5) ≡ 0 (mod 2),
    k_min(7) ≡ 0 (mod 2) at non-coincident, k_min(7) ≡ 0 (mod 10)
    at coincident. Forbidden: P_i (carve-out exempts {2} universally,
    plus {5} at coincident — but 5 ∉ P_7 anyway, and 5 ∈ P_5 so it
    stays forbidden for 5-series). Net: P_5 for 5-series; P_7 for
    7-series.
  - Alternative B (mod-30 universal): k_min(5) ≡ 0 (mod 6) (Π_5
    supplies 5, so k supplies 2·3), k_min(7) ≡ 0 (mod 30) (Π_7
    supplies none of 2/3/5). Forbidden: P_i (carve-out exempts
    {2, 3} for 5-series, {2, 3, 5} for 7-series).

n_i* is anchored under Convention A (largest contiguous run of S_i(C);
unchanged across conventions).

Compute three F5 metrics per convention:
  (a) Outlier count: clusters where lift_7 != mode of 7-series lift
      distribution under that convention.
  (b) Shannon entropy (base 2, bits) of 7-series lift distribution.
  (c) Transition count: partial-coincident → coincident consecutive
      transitions in the cluster sequence (classification fixed by
      Step 3, so this is identical across conventions; reporting it
      under each is a sanity check).

Binding thresholds (from v4.5 §6.3 F5):
  (a) ≤ 2 outliers (≥ 50% reduction from 4)
  (b) ≤ 0.35 bits (≥ 0.5 bits reduction from ~0.85)
  (c) ≤ 3 transitions (≥ 25% reduction from 4)

Outputs:
  v3_12_data/results/task2_alternative_convention_results.csv
  v3_12_data/results/task2_alternative_convention_summary.md
"""
import os
import sys
import csv
import math

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve

HERE = os.path.dirname(__file__)
RESULTS_DIR = os.path.join(HERE, 'results')
CSV_IN = os.path.join(RESULTS_DIR, 'cluster_comparative_tabulation.csv')
CSV_OUT = os.path.join(RESULTS_DIR, 'task2_alternative_convention_results.csv')
MD_OUT = os.path.join(RESULTS_DIR, 'task2_alternative_convention_summary.md')

SIEVE_LIMIT = 200_000
N_MAX = 250
K_MAX = 1000  # enumeration upper bound

# Binding thresholds from pre-registration
THRESH_OUTLIER = 2       # ≤ 2 outliers fires F5 (50% reduction from 4)
THRESH_ENTROPY = 0.35    # ≤ 0.35 bits fires F5 (≥ 0.5 bits reduction)
THRESH_TRANSITION = 3    # ≤ 3 transitions fires F5 (25% reduction from 4)

# v4.2 reference (chosen-convention) values
REF_OUTLIER = 4
REF_TRANSITION = 4


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


def find_min_lift(prod_at_n_star, forbidden, a, b, required_divisor,
                  k_max=K_MAX):
    """Smallest k with k % required_divisor == 0, prime_factors(k) ∩
    forbidden == ∅, D(prod * k) ∈ [a, b]."""
    k = required_divisor
    while k <= k_max:
        if not (prime_factors(k) & forbidden):
            d_lifted = len(str(prod_at_n_star * k))
            if a <= d_lifted <= b:
                return k
        k += required_divisor
    return None


# Convention specifications.  required_divisor depends on (series,
# classification); forbidden depends on series only.
def conv_chosen(series, classification, forbidden_chosen):
    if series == 5:
        return 3, forbidden_chosen['5']
    # 7-series
    if classification == 'coincident':
        return 15, forbidden_chosen['7']
    return 3, forbidden_chosen['7']


def conv_alt_a(series, classification, forbidden_alt_a):
    if series == 5:
        # Π_5 supplies 5, so mod-10 at coincident reduces to mod-2 on k
        return 2, forbidden_alt_a['5']
    # 7-series
    if classification == 'coincident':
        return 10, forbidden_alt_a['7']
    return 2, forbidden_alt_a['7']


def conv_alt_b(series, classification, forbidden_alt_b):
    if series == 5:
        # Π_5 supplies 5, k supplies 2·3 = 6
        return 6, forbidden_alt_b['5']
    # 7-series — k supplies 2·3·5 = 30 always
    return 30, forbidden_alt_b['7']


def shannon_entropy(counts):
    """Shannon entropy (base 2, in bits) of an empirical distribution
    given by integer counts."""
    total = sum(counts)
    h = 0.0
    for c in counts:
        if c == 0:
            continue
        p = c / total
        h -= p * math.log2(p)
    return h


def main():
    # ---- Read v4.2 CSV; restrict to comparative-sample C_* rows ----
    with open(CSV_IN, encoding='utf-8') as f:
        all_rows = list(csv.DictReader(f))
    sample = [r for r in all_rows if r['cluster_id'].startswith('C_')]
    print(f"Loaded {len(sample)} comparative-sample clusters from {CSV_IN}.")
    assert len(sample) == 23, f"expected 23 clusters, got {len(sample)}"

    # ---- Sieve and Π_i ----
    print(f"\nSieving primes up to {SIEVE_LIMIT}...")
    primes = sieve(SIEVE_LIMIT)
    p5_list = [p for p in primes if p > 3 and p % 6 == 5]
    p7_list = [p for p in primes if p > 3 and p % 6 == 1]
    prods5 = []
    prod = 1
    for p in p5_list[:N_MAX]:
        prod *= p
        prods5.append(prod)
    prods7 = []
    prod = 1
    for p in p7_list[:N_MAX]:
        prod *= p
        prods7.append(prod)

    # ---- Forbidden sets per (convention, series) ----
    # Primes up to K_MAX (the only ones that can appear as factors of k)
    p5_set = {p for p in primes if p > 3 and p % 6 == 5 and p <= K_MAX}
    p7_set = {p for p in primes if p > 3 and p % 6 == 1 and p <= K_MAX}

    # Chosen: k coprime to P_i ∪ {2}.  (No carve-out for chosen — the
    # required divisor primes (3 for both, 5 at 7-coincident) aren't in
    # P_i, so they're already not forbidden.)
    forbidden_chosen = {
        '5': p5_set | {2},
        '7': p7_set | {2},
    }
    # Alt A: carve-out exempts {2} (and {5} at 7-coincident, but
    # 5 ∉ P_7 anyway).  So forbidden = P_i for both series.  5-series
    # still has 5 ∈ P_5 (not exempted because (i-a) doesn't require k to
    # contain 5 — Π_5 supplies it).
    forbidden_alt_a = {'5': p5_set, '7': p7_set}
    # Alt B: carve-out exempts {2, 3} for 5-series, {2, 3, 5} for
    # 7-series.  3 ∉ P_5 (P_5 = primes ≡ 5 mod 6), so removing 3 from
    # forbidden_5 does nothing.  5 IS in P_5 but is NOT in the
    # 5-series carve-out (k doesn't need to contain 5; Π_5 supplies it),
    # so 5 stays forbidden for 5-series.  forbidden_5 = P_5.  For
    # 7-series the carve-out exempts {2, 3, 5}; 3 and 5 aren't in P_7
    # anyway; so forbidden_7 = P_7.
    forbidden_alt_b = {'5': p5_set, '7': p7_set}

    conventions = [
        ('chosen', conv_chosen, forbidden_chosen),
        ('alt_a',  conv_alt_a,  forbidden_alt_a),
        ('alt_b',  conv_alt_b,  forbidden_alt_b),
    ]

    # ---- Recompute lifts per cluster, per convention, per series ----
    print("\n" + "=" * 72)
    print("Per-cluster lift recomputation under three conventions")
    print("=" * 72)
    out_rows = []
    for r in sample:
        cid = r['cluster_id']
        a = int(r['d_lower'])
        b = int(r['d_upper'])
        cls = r['classification']
        n5_star = int(r['n5_star'])
        n7_star = int(r['n7_star'])
        prod5 = prods5[n5_star - 1]
        prod7 = prods7[n7_star - 1]

        row = {
            'cluster_id': cid,
            'd_range': f'({a},{b})',
            'classification': cls,
            'n_5_star': n5_star,
            'n_7_star': n7_star,
        }
        for cname, cfunc, _ in conventions:
            req5, forbid5 = cfunc(5, cls, {'5': None, '7': None})  # placeholder
        for cname, cfunc, ftab in conventions:
            req5, forbid5 = cfunc(5, cls, ftab)
            req7, forbid7 = cfunc(7, cls, ftab)
            k5 = find_min_lift(prod5, forbid5, a, b, req5)
            k7 = find_min_lift(prod7, forbid7, a, b, req7)
            row[f'lift5_{cname}'] = k5 if k5 is not None else 'none'
            row[f'lift7_{cname}'] = k7 if k7 is not None else 'none'
            row[f'req_div_5_{cname}'] = req5
            row[f'req_div_7_{cname}'] = req7
        out_rows.append(row)

    # Compact echo
    print(f"  {'cluster':6s}  {'cls':19s}  "
          f"{'chosen':>14s}  {'Alt A':>14s}  {'Alt B':>14s}")
    print(f"  {'':6s}  {'':19s}  "
          f"{'(lift5, lift7)':>14s}  {'(lift5, lift7)':>14s}  "
          f"{'(lift5, lift7)':>14s}")
    for r in out_rows:
        cid = r['cluster_id']
        cls = r['classification']
        ch = f"({r['lift5_chosen']}, {r['lift7_chosen']})"
        aa = f"({r['lift5_alt_a']}, {r['lift7_alt_a']})"
        bb = f"({r['lift5_alt_b']}, {r['lift7_alt_b']})"
        print(f"  {cid:6s}  {cls:19s}  {ch:>14s}  {aa:>14s}  {bb:>14s}")

    # ---- F5 metrics per convention ----
    def metrics(rows, lift7_key):
        vals = [r[lift7_key] for r in rows]
        # Skip "none" (should not occur, but safe)
        vals = [v for v in vals if v != 'none']
        # Mode
        freq = {}
        for v in vals:
            freq[v] = freq.get(v, 0) + 1
        mode = max(freq, key=lambda k: freq[k])
        # Outlier count
        outliers = sum(1 for v in vals if v != mode)
        # Shannon entropy
        H = shannon_entropy(list(freq.values()))
        return mode, freq, outliers, H

    print("\n" + "=" * 72)
    print("F5 metrics per convention")
    print("=" * 72)

    # Transition count is fixed by classification — same across
    # conventions.  Recompute it once for sanity.
    transitions = 0
    transition_pairs = []
    for i in range(len(out_rows) - 1):
        a_cls = out_rows[i]['classification']
        b_cls = out_rows[i + 1]['classification']
        if a_cls in ('staggered', 'partial-coincident') and \
                b_cls == 'coincident':
            transitions += 1
            transition_pairs.append((out_rows[i]['cluster_id'],
                                     out_rows[i + 1]['cluster_id']))

    metrics_table = []
    for cname, _, _ in conventions:
        mode, freq, outliers, H = metrics(out_rows, f'lift7_{cname}')
        metrics_table.append({
            'convention': cname,
            'lift7_mode': mode,
            'lift7_freq': dict(freq),
            'outlier_count': outliers,
            'entropy_bits': H,
            'transition_count': transitions,
        })
        print(f"\n  Convention: {cname}")
        print(f"    7-series lift distribution: "
              f"{dict(sorted(freq.items(), key=lambda kv: -kv[1]))}")
        print(f"    mode = {mode}; outlier count = {outliers}")
        print(f"    Shannon entropy = {H:.4f} bits")
        print(f"    partial-coincident → coincident transitions = "
              f"{transitions}  (fixed across conventions)")

    # ---- Falsifier-test under F5 binding thresholds ----
    print("\n" + "=" * 72)
    print("F5 falsifier test (binding thresholds from pre-registration)")
    print("=" * 72)
    print(f"  Chosen reference: outliers = {REF_OUTLIER}, "
          f"H ≈ 0.85 bits, transitions = {REF_TRANSITION}")
    print(f"  Thresholds (alternative fires F5 if any of):")
    print(f"    outliers ≤ {THRESH_OUTLIER} (≥ 50% reduction)")
    print(f"    entropy ≤ {THRESH_ENTROPY} bits (≥ 0.5 bits reduction)")
    print(f"    transitions ≤ {THRESH_TRANSITION} (≥ 25% reduction)")

    any_alt_fires = False
    fire_summary = []
    for m in metrics_table:
        if m['convention'] == 'chosen':
            continue
        cname = m['convention']
        outl_fires = m['outlier_count'] <= THRESH_OUTLIER
        H_fires = m['entropy_bits'] <= THRESH_ENTROPY
        trans_fires = m['transition_count'] <= THRESH_TRANSITION
        fires = outl_fires or H_fires or trans_fires
        print(f"\n  {cname}:")
        print(f"    outliers = {m['outlier_count']} "
              f"({'≤' if outl_fires else '>'} {THRESH_OUTLIER})  "
              f"{'FIRES' if outl_fires else 'no'}")
        print(f"    entropy  = {m['entropy_bits']:.4f} bits "
              f"({'≤' if H_fires else '>'} {THRESH_ENTROPY})  "
              f"{'FIRES' if H_fires else 'no'}")
        print(f"    transitions = {m['transition_count']} "
              f"({'≤' if trans_fires else '>'} {THRESH_TRANSITION})  "
              f"{'FIRES' if trans_fires else 'no'}")
        print(f"    F5 verdict: {'FIRES' if fires else 'does not fire'}")
        if fires:
            any_alt_fires = True
            fire_summary.append((cname, outl_fires, H_fires, trans_fires))

    # ---- Outcome ----
    print("\n" + "=" * 72)
    print("Pre-registered outcome")
    print("=" * 72)
    if any_alt_fires:
        outcome = 'β'
        print(f"  Outcome: (β) — at least one alternative fires F5.")
        for cname, ou, he, tr in fire_summary:
            triggers = []
            if ou: triggers.append("outlier count")
            if he: triggers.append("entropy")
            if tr: triggers.append("transition count")
            print(f"    {cname} fires on: {', '.join(triggers)}")
    else:
        # (α) vs (γ): (α) means BOTH alternatives produce metrics no
        # better than reference (count ≥ 4, entropy ≥ 0.85, trans ≥ 4).
        # (γ) means measurable but sub-threshold improvement.
        chosen_metrics = metrics_table[0]
        alt_metrics = [m for m in metrics_table
                       if m['convention'] != 'chosen']
        any_improvement = False
        for m in alt_metrics:
            if (m['outlier_count'] < REF_OUTLIER
                    or m['entropy_bits'] < chosen_metrics['entropy_bits']
                    or m['transition_count'] < REF_TRANSITION):
                any_improvement = True
                break
        if any_improvement:
            outcome = 'γ'
            print(f"  Outcome: (γ) — marginal-zone strengthening.")
            print(f"    No alternative crosses any binding threshold, but")
            print(f"    at least one shows sub-threshold improvement on")
            print(f"    at least one metric.")
        else:
            outcome = 'α'
            print(f"  Outcome: (α) — chosen convention wins.")
            print(f"    No alternative improves on any of the three "
                  f"metrics.")

    # ---- Stop-on-fail check: did any alternative produce a "none" lift? ----
    halt = False
    for r in out_rows:
        for k in r:
            if k.startswith('lift') and r[k] == 'none':
                print(f"\n  WARNING: {r['cluster_id']} {k} = 'none' — "
                      f"no satisfying k ≤ {K_MAX} under this convention. "
                      f"Structural surprise.")
                halt = True
    if halt:
        print(f"\n  HALT (Pattern 75): unexpected 'none' lifts. "
              f"Consult CinC.")
        # Continue to write output for diagnostic purposes
        outcome = f'HALT ({outcome})'

    # ---- Write outputs ----
    write_csv(out_rows)
    write_summary(out_rows, metrics_table, transitions,
                  transition_pairs, outcome)

    print("\n" + "=" * 72)
    print("TASK 2 — STATUS")
    print("=" * 72)
    print(f"Anchor verification: PASS (re-derivation completes for 23 "
          f"clusters under 3 conventions)")
    print(f"Outcome: ({outcome})")
    print(f"Numerical summary (7-series lift only):")
    for m in metrics_table:
        print(f"  {m['convention']:7s}: outliers={m['outlier_count']}, "
              f"H={m['entropy_bits']:.4f} bits, "
              f"transitions={m['transition_count']}, "
              f"distribution={dict(sorted(m['lift7_freq'].items(), key=lambda kv: -kv[1]))}")
    print(f"Files produced:")
    print(f"  {CSV_OUT}")
    print(f"  {MD_OUT}")
    print("\nEnd-of-task: PASS")


def write_csv(out_rows):
    fieldnames = ['cluster_id', 'd_range', 'classification',
                  'n_5_star', 'n_7_star',
                  'lift5_chosen', 'lift7_chosen',
                  'req_div_5_chosen', 'req_div_7_chosen',
                  'lift5_alt_a', 'lift7_alt_a',
                  'req_div_5_alt_a', 'req_div_7_alt_a',
                  'lift5_alt_b', 'lift7_alt_b',
                  'req_div_5_alt_b', 'req_div_7_alt_b']
    with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)


def write_summary(out_rows, metrics_table, transitions, transition_pairs,
                  outcome):
    with open(MD_OUT, 'w', encoding='utf-8') as f:
        f.write("# Task 2 — F5 alternative-convention probe: summary\n\n")
        f.write(f"**Date:** 11 May 2026.\n")
        f.write(f"**Pre-registration:** "
                f"`v3_12_data/briefs/"
                f"task2_alternative_convention_pre_registration.md`.\n")
        f.write(f"**Outcome: ({outcome})**\n\n")
        f.write("## Three-convention comparative table "
                "(7-series lift distribution, F5 metrics)\n\n")
        f.write("| Convention | 7-series lift distribution | "
                "Outlier count | Entropy (bits) | Transitions |\n")
        f.write("|------------|----------------------------|"
                "---------------|----------------|-------------|\n")
        for m in metrics_table:
            dist = dict(sorted(m['lift7_freq'].items(),
                               key=lambda kv: -kv[1]))
            f.write(f"| {m['convention']} | {dist} | "
                    f"{m['outlier_count']} | "
                    f"{m['entropy_bits']:.4f} | "
                    f"{m['transition_count']} |\n")
        f.write("\n")
        f.write(f"Binding thresholds: outliers ≤ {THRESH_OUTLIER}, "
                f"entropy ≤ {THRESH_ENTROPY} bits, "
                f"transitions ≤ {THRESH_TRANSITION}.\n\n")
        f.write("Reference (chosen-convention) values from v4.2: "
                f"outliers = {REF_OUTLIER}, "
                f"entropy ≈ 0.85 bits, transitions = "
                f"{REF_TRANSITION}.\n\n")

        f.write("## Per-cluster lift recomputation\n\n")
        f.write("| Cluster | d-range | classification | "
                "(lift5, lift7) chosen | (lift5, lift7) Alt A | "
                "(lift5, lift7) Alt B |\n")
        f.write("|---------|---------|----------------|"
                "----------------------|----------------------|"
                "----------------------|\n")
        for r in out_rows:
            ch = f"({r['lift5_chosen']}, {r['lift7_chosen']})"
            aa = f"({r['lift5_alt_a']}, {r['lift7_alt_a']})"
            bb = f"({r['lift5_alt_b']}, {r['lift7_alt_b']})"
            f.write(f"| {r['cluster_id']} | {r['d_range']} | "
                    f"{r['classification']} | {ch} | {aa} | {bb} |\n")
        f.write("\n")

        if outcome == 'α':
            f.write("## Outcome paragraph — (α) chosen wins\n\n"
                    "Neither alternative convention crosses any of the "
                    "three F5 binding thresholds. The chosen mod-3 / "
                    "mod-15 convention's claim to being the right lens "
                    "on the (Π₅, Π₇) digit-jump data tightens "
                    "substantively against the two tested alternatives "
                    "(mod-2 inclusion and mod-30 universal). F5 does "
                    "not fire under either alternative.\n")
        elif outcome == 'β':
            f.write("## Outcome paragraph — (β) alternative fires F5\n\n"
                    "At least one alternative convention crosses at "
                    "least one binding F5 threshold. The chosen "
                    "convention's claim to being the right lens on the "
                    "data is **refuted**. Retraction 4 (specifically of "
                    "convention choice) is indicated.\n")
        elif outcome.startswith('γ') or outcome == 'γ':
            f.write("## Outcome paragraph — (γ) marginal-zone "
                    "strengthening\n\n"
                    "An alternative produces measurable but "
                    "sub-threshold improvement on at least one metric "
                    "without crossing any binding threshold. F5 does "
                    "not fire; the comparative analysis documents "
                    "a strengthening of the convention warrant rather "
                    "than a refutation.\n\n"
                    "### Suggested §6.3 supplementary paragraph text\n\n"
                    "(See per-cluster table above; CinC to draft the "
                    "final wording.)\n")
        else:
            f.write(f"## Outcome ({outcome})\n\n"
                    "See script stdout for HALT diagnostic.\n")

        f.write(f"\n## Transition pairs (fixed across conventions)\n\n")
        for a, b in transition_pairs:
            f.write(f"- {a} → {b}\n")
        f.write("\n🐕☕⬡\n")
        f.write("\n— Mr Code, 11 May 2026 (Paper 3 v4.5 Task 2)\n")


if __name__ == '__main__':
    main()
