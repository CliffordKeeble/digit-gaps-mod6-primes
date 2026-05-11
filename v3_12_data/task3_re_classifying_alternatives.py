#!/usr/bin/env python3
"""Paper 3 v4.5 Task 3 — F5 (refined) under re-classifying alternatives.

Per pre-registration `v3_12_data/briefs/
task3_re_classifying_alternatives_pre_registration.md`.

Two alternatives, both genuinely re-classifying (vary required_divisor by
cluster type rather than universalising it):

  - Alt(C) 'mod-3 always' — drops chosen's mod-15 escalation at coincident.
    7-series: k ≡ 0 (mod 3) at every cluster type.
  - Alt(D) 'asymmetric pcm → mod-15' — escalates the 4 partial-coincident
    clusters from mod-3 to mod-15. 7-series:
        coincident: mod-15 (same as chosen)
        partial-coincident: mod-15 (NEW)
        staggered/single-*: mod-3 (same as chosen; 0 clusters in sample)

Refined F5 (Calibration 3): an alternative fires F5 iff
    (non-degenerate: ≥ 2 distinct lift values, equivalently
     mode_freq < 100%, equivalently H > 0)
  AND
    (outliers ≤ 2 OR H ≤ 0.35 bits OR transitions ≤ 3).

Outputs:
  v3_12_data/results/task3_re_classifying_alternatives_results.csv
  v3_12_data/results/task3_re_classifying_alternatives_summary.md
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
CSV_OUT = os.path.join(RESULTS_DIR,
                       'task3_re_classifying_alternatives_results.csv')
MD_OUT = os.path.join(RESULTS_DIR,
                      'task3_re_classifying_alternatives_summary.md')

SIEVE_LIMIT = 200_000
N_MAX = 250
K_MAX = 1000

THRESH_OUTLIER = 2
THRESH_ENTROPY = 0.35
THRESH_TRANSITION = 3
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
    k = required_divisor
    while k <= k_max:
        if not (prime_factors(k) & forbidden):
            d_lifted = len(str(prod_at_n_star * k))
            if a <= d_lifted <= b:
                return k
        k += required_divisor
    return None


# Required divisors per (convention, series, classification)
def req_div_chosen(series, cls):
    if series == 5:
        return 3
    return 15 if cls == 'coincident' else 3


def req_div_alt_c(series, cls):
    if series == 5:
        return 3
    return 3  # mod-3 always at 7-series


def req_div_alt_d(series, cls):
    if series == 5:
        return 3
    if cls in ('coincident', 'partial-coincident'):
        return 15
    return 3


def shannon_entropy(counts):
    total = sum(counts)
    h = 0.0
    for c in counts:
        if c == 0:
            continue
        p = c / total
        h -= p * math.log2(p)
    return h


def main():
    # ---- Load v4.2 CSV; restrict to 23 comparative clusters ----
    with open(CSV_IN, encoding='utf-8') as f:
        all_rows = list(csv.DictReader(f))
    sample = [r for r in all_rows if r['cluster_id'].startswith('C_')]
    print(f"Loaded {len(sample)} comparative-sample clusters from {CSV_IN}.")
    assert len(sample) == 23

    # ---- Sieve and Π_i ----
    print(f"\nSieving primes up to {SIEVE_LIMIT}...")
    primes = sieve(SIEVE_LIMIT)
    p7_list = [p for p in primes if p > 3 and p % 6 == 1]
    prods7 = []
    prod = 1
    for p in p7_list[:N_MAX]:
        prod *= p
        prods7.append(prod)

    # Forbidden for 7-series under all three conventions: P_7 ∪ {2}.
    # (No (i-a)-driven carve-out shift across conventions, since
    # chosen/Alt(C)/Alt(D) all use mod-3-or-mod-15 — neither 3 nor 5
    # is in P_7, so the chosen forbidden set is unchanged.)
    forbidden_7 = {2} | {p for p in primes if p > 3 and p % 6 == 1
                         and p <= K_MAX}

    conventions = [
        ('chosen', req_div_chosen),
        ('alt_c',  req_div_alt_c),
        ('alt_d',  req_div_alt_d),
    ]

    # ---- Recompute 7-series lifts per cluster per convention ----
    print("\n" + "=" * 72)
    print("Per-cluster 7-series lift under three conventions")
    print("=" * 72)
    out_rows = []
    for r in sample:
        cid = r['cluster_id']
        a = int(r['d_lower'])
        b = int(r['d_upper'])
        cls = r['classification']
        n7_star = int(r['n7_star'])
        prod7 = prods7[n7_star - 1]

        row = {
            'cluster_id': cid,
            'd_range': f'({a},{b})',
            'classification': cls,
            'n_7_star': n7_star,
            'D_7_at_n_star': len(str(prod7)),
        }
        for cname, rdfunc in conventions:
            req = rdfunc(7, cls)
            k = find_min_lift(prod7, forbidden_7, a, b, req)
            row[f'lift7_{cname}'] = k if k is not None else 'none'
            row[f'req_div_7_{cname}'] = req
        out_rows.append(row)

    # Display
    print(f"  {'cluster':6s}  {'cls':19s}  "
          f"{'chosen':>10s}  {'Alt(C)':>10s}  {'Alt(D)':>10s}")
    for r in out_rows:
        print(f"  {r['cluster_id']:6s}  {r['classification']:19s}  "
              f"{str(r['lift7_chosen']):>10s}  "
              f"{str(r['lift7_alt_c']):>10s}  "
              f"{str(r['lift7_alt_d']):>10s}")

    # Verify chosen reproduces v4.2 distribution
    chosen_vals = [r['lift7_chosen'] for r in out_rows]
    freq_chosen = {}
    for v in chosen_vals:
        freq_chosen[v] = freq_chosen.get(v, 0) + 1
    print(f"\n  Chosen reproduces v4.2 distribution: {freq_chosen}")
    expected_chosen = {15: 19, 3: 2, 9: 2}
    if freq_chosen != expected_chosen:
        print(f"  HALT: chosen distribution {freq_chosen} != v4.2 "
              f"{expected_chosen}")
        sys.exit(1)
    print("  OK")

    # ---- F5 metrics + non-degeneracy per convention ----
    print("\n" + "=" * 72)
    print("Refined-F5 metrics per convention")
    print("=" * 72)

    transitions = 0
    transition_pairs = []
    for i in range(len(out_rows) - 1):
        a_cls = out_rows[i]['classification']
        b_cls = out_rows[i + 1]['classification']
        if a_cls in ('staggered', 'partial-coincident') \
                and b_cls == 'coincident':
            transitions += 1
            transition_pairs.append((out_rows[i]['cluster_id'],
                                     out_rows[i + 1]['cluster_id']))

    metrics_table = []
    for cname, _ in conventions:
        vals = [r[f'lift7_{cname}'] for r in out_rows
                if r[f'lift7_{cname}'] != 'none']
        freq = {}
        for v in vals:
            freq[v] = freq.get(v, 0) + 1
        mode = max(freq, key=lambda k: freq[k])
        outliers = sum(1 for v in vals if v != mode)
        H = shannon_entropy(list(freq.values()))
        n_distinct = len(freq)
        mode_freq_pct = 100 * freq[mode] / len(vals)
        non_degenerate = n_distinct >= 2
        metrics_table.append({
            'convention': cname,
            'lift7_freq': dict(freq),
            'mode': mode,
            'mode_freq_pct': mode_freq_pct,
            'outlier_count': outliers,
            'entropy_bits': H,
            'transition_count': transitions,
            'n_distinct': n_distinct,
            'non_degenerate': non_degenerate,
        })
        print(f"\n  Convention: {cname}")
        print(f"    distribution: "
              f"{dict(sorted(freq.items(), key=lambda kv: -kv[1]))}")
        print(f"    mode = {mode} ({mode_freq_pct:.1f}% of clusters)")
        print(f"    outliers = {outliers}; H = {H:.4f} bits; "
              f"transitions = {transitions}")
        print(f"    distinct values = {n_distinct}; non-degenerate = "
              f"{non_degenerate}")

    # ---- Refined-F5 verdict per alternative ----
    print("\n" + "=" * 72)
    print("Refined F5 verdict (non-degeneracy clause + binding thresholds)")
    print("=" * 72)
    print(f"  Thresholds: outliers ≤ {THRESH_OUTLIER}, "
          f"entropy ≤ {THRESH_ENTROPY} bits, "
          f"transitions ≤ {THRESH_TRANSITION}")
    print(f"  Non-degeneracy clause: distribution has ≥ 2 distinct values")

    any_alt_fires_refined = False
    near_degenerate_flags = []
    fire_summary = []
    for m in metrics_table:
        if m['convention'] == 'chosen':
            continue
        cname = m['convention']
        nd = m['non_degenerate']
        outl_xed = m['outlier_count'] <= THRESH_OUTLIER
        H_xed = m['entropy_bits'] <= THRESH_ENTROPY
        trans_xed = m['transition_count'] <= THRESH_TRANSITION
        threshold_crossed = outl_xed or H_xed or trans_xed
        fires_refined = nd and threshold_crossed
        print(f"\n  {cname}:")
        print(f"    non-degenerate: {nd}  ({m['n_distinct']} distinct "
              f"values; mode freq = {m['mode_freq_pct']:.1f}%)")
        print(f"    outliers = {m['outlier_count']} "
              f"({'≤' if outl_xed else '>'} {THRESH_OUTLIER})")
        print(f"    entropy  = {m['entropy_bits']:.4f} bits "
              f"({'≤' if H_xed else '>'} {THRESH_ENTROPY})")
        print(f"    transitions = {m['transition_count']} "
              f"({'≤' if trans_xed else '>'} {THRESH_TRANSITION})")
        print(f"    Refined F5: "
              f"{'FIRES' if fires_refined else 'does not fire'}")
        if fires_refined:
            any_alt_fires_refined = True
            fire_summary.append((cname, outl_xed, H_xed, trans_xed))
        # Pattern-N near-degeneracy check: non-degenerate but with very
        # high mode frequency (≥ 95%) AND threshold crossed
        if nd and threshold_crossed and m['mode_freq_pct'] >= 95.0:
            near_degenerate_flags.append({
                'convention': cname,
                'mode_freq_pct': m['mode_freq_pct'],
                'n_distinct': m['n_distinct'],
                'distribution': m['lift7_freq'],
            })

    # ---- Outcome ----
    print("\n" + "=" * 72)
    print("Pre-registered outcome (refined F5)")
    print("=" * 72)
    if any_alt_fires_refined:
        outcome = 'β'
        print(f"  Outcome: (β) — at least one re-classifying alternative "
              f"fires refined F5.")
        for cname, ou, he, tr in fire_summary:
            triggers = []
            if ou:
                triggers.append("outlier count")
            if he:
                triggers.append("entropy")
            if tr:
                triggers.append("transition count")
            print(f"    {cname} fires on: {', '.join(triggers)}")
    else:
        # (α) or (γ): (γ) if any alt is non-degenerate AND
        # sub-threshold improvement on any metric vs chosen
        chosen_m = metrics_table[0]
        alt_ms = [m for m in metrics_table if m['convention'] != 'chosen']
        any_subthresh = False
        for m in alt_ms:
            if not m['non_degenerate']:
                continue
            if (m['outlier_count'] < chosen_m['outlier_count']
                    or m['entropy_bits'] < chosen_m['entropy_bits']
                    or m['transition_count'] < chosen_m['transition_count']):
                any_subthresh = True
                break
        if any_subthresh:
            outcome = 'γ'
            print(f"  Outcome: (γ) — marginal-zone strengthening.")
            print(f"    No alternative crosses any binding threshold, but")
            print(f"    at least one is non-degenerate AND shows")
            print(f"    sub-threshold improvement on at least one metric.")
        else:
            outcome = 'α'
            print(f"  Outcome: (α) — chosen convention wins.")
            print(f"    No non-degenerate alternative improves on any "
                  f"binding metric.")

    if near_degenerate_flags:
        print("\n  Pattern-N flag — near-degeneracy under refined F5:")
        for f in near_degenerate_flags:
            print(f"    {f['convention']}: mode_freq = "
                  f"{f['mode_freq_pct']:.1f}% (≥ 95% threshold); "
                  f"distribution {f['distribution']}")
        print("    The refined F5's binary non-degeneracy clause allows "
              "this firing,")
        print("    but the distribution is structurally near-degenerate. "
              "CinC may want")
        print("    a second-order calibration (e.g., mode_freq cap < 95%).")

    # ---- Write outputs ----
    write_csv(out_rows, metrics_table)
    write_summary(out_rows, metrics_table, transitions, transition_pairs,
                  outcome, near_degenerate_flags)

    print("\n" + "=" * 72)
    print("TASK 3 — STATUS")
    print("=" * 72)
    print(f"Anchor verification: PASS")
    print(f"  Chosen reproduces v4.2 distribution: {freq_chosen}")
    print(f"Outcome (refined F5): ({outcome})")
    if near_degenerate_flags:
        print(f"Pattern-N near-degeneracy: FLAGGED")
        print(f"  Affected: "
              + ", ".join(f['convention'] for f in near_degenerate_flags))
    print(f"Numerical summary:")
    for m in metrics_table:
        nd_str = "non-degen" if m['non_degenerate'] else "DEGEN"
        print(f"  {m['convention']:7s}: outliers={m['outlier_count']}, "
              f"H={m['entropy_bits']:.4f} bits, "
              f"mode={m['mode']} ({m['mode_freq_pct']:.1f}%), {nd_str}, "
              f"distribution={dict(sorted(m['lift7_freq'].items(), key=lambda kv: -kv[1]))}")
    print(f"Files produced:")
    print(f"  {CSV_OUT}")
    print(f"  {MD_OUT}")
    print("\nEnd-of-task: PASS")


def write_csv(out_rows, metrics_table):
    fieldnames = ['cluster_id', 'd_range', 'classification',
                  'n_7_star', 'D_7_at_n_star',
                  'lift7_chosen', 'req_div_7_chosen',
                  'lift7_alt_c', 'req_div_7_alt_c',
                  'lift7_alt_d', 'req_div_7_alt_d']
    with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)


def write_summary(out_rows, metrics_table, transitions, transition_pairs,
                  outcome, near_degenerate_flags):
    with open(MD_OUT, 'w', encoding='utf-8') as f:
        f.write("# Task 3 — F5 (refined) under re-classifying "
                "alternatives: summary\n\n")
        f.write(f"**Date:** 11 May 2026.\n")
        f.write(f"**Pre-registration:** `v3_12_data/briefs/"
                f"task3_re_classifying_alternatives_pre_registration.md`.\n")
        f.write(f"**Outcome (refined F5): ({outcome})**\n\n")

        f.write("## Three-convention comparative table "
                "(7-series, [90, 200] sample, n = 23)\n\n")
        f.write("| Convention | distribution | mode (freq) | "
                "outliers | H (bits) | transitions | non-degenerate |\n")
        f.write("|------------|--------------|-------------|"
                "----------|----------|-------------|----------------|\n")
        for m in metrics_table:
            dist = dict(sorted(m['lift7_freq'].items(),
                               key=lambda kv: -kv[1]))
            f.write(f"| {m['convention']} | {dist} | "
                    f"{m['mode']} ({m['mode_freq_pct']:.1f}%) | "
                    f"{m['outlier_count']} | "
                    f"{m['entropy_bits']:.4f} | "
                    f"{m['transition_count']} | "
                    f"{'yes' if m['non_degenerate'] else 'NO (delta)'} |\n")
        f.write("\n")
        f.write(f"Refined F5 binding: non-degenerate AND "
                f"(outliers ≤ {THRESH_OUTLIER} OR "
                f"H ≤ {THRESH_ENTROPY} bits OR "
                f"transitions ≤ {THRESH_TRANSITION}).\n")
        f.write(f"Reference (chosen-convention) values from v4.2: "
                f"outliers = {REF_OUTLIER}, H = 0.8405 bits, "
                f"transitions = {REF_TRANSITION}.\n\n")

        if outcome == 'α':
            f.write("## Outcome paragraph — (α) chosen wins under "
                    "non-degenerate competition\n\n"
                    "Neither re-classifying alternative crosses any "
                    "binding refined-F5 threshold while remaining "
                    "non-degenerate. The chosen mod-3 / mod-15 convention "
                    "is preserved against both *less-asymmetric* "
                    "(Alt(C) drops the mod-15 escalation) and "
                    "*more-asymmetric* (Alt(D) extends mod-15 to "
                    "partial-coincident) competition. Warrant tightens.\n")
        elif outcome == 'β':
            f.write("## Outcome paragraph — (β) re-classifying "
                    "alternative fires refined F5\n\n"
                    "At least one re-classifying alternative is "
                    "non-degenerate AND crosses at least one refined-F5 "
                    "binding threshold. The chosen convention's claim to "
                    "being the right lens on the data is challenged on "
                    "non-artefactual grounds. CinC to consider whether "
                    "the firing alternative warrants §4.0 revision (this "
                    "is a substantive (β), unlike Task 2's literal-(β) "
                    "via Alt B which was degenerate).\n")
        elif outcome == 'γ':
            f.write("## Outcome paragraph — (γ) marginal-zone "
                    "strengthening\n\n"
                    "At least one non-degenerate alternative produces "
                    "measurable but sub-threshold improvement on a "
                    "metric. No refined-F5 firing; the chosen "
                    "convention's parsimony is preserved against "
                    "re-classifying competition with measurable but "
                    "sub-threshold near-competition.\n")

        if near_degenerate_flags:
            f.write("\n## Pattern-N flag — near-degeneracy under "
                    "binary non-degeneracy clause\n\n"
                    "The refined F5's binary non-degeneracy clause "
                    "(≥ 2 distinct values, mode_freq < 100%) allows "
                    "the following alternative(s) to fire refined F5 "
                    "while having mode frequency ≥ 95%:\n\n")
            for fl in near_degenerate_flags:
                f.write(f"- **{fl['convention']}**: mode_freq = "
                        f"{fl['mode_freq_pct']:.1f}%, distribution = "
                        f"{fl['distribution']}.\n")
            f.write("\nThe distribution is structurally near-degenerate "
                    "but technically passes the binary clause. CinC may "
                    "want a second-order calibration: e.g., a "
                    "mode-frequency cap (mode_freq < 95% or < 90%) or "
                    "an entropy floor (H ≥ some positive value). "
                    "Pattern N applies — refine the test's operational "
                    "form rather than walking back the pre-registered "
                    "outcome.\n")

        f.write("\n## Per-cluster table\n\n")
        f.write("| Cluster | d-range | classification | n_7* | D_7(n_7*) | "
                "chosen | Alt(C) | Alt(D) |\n")
        f.write("|---------|---------|----------------|------|-----------|"
                "--------|--------|--------|\n")
        for r in out_rows:
            f.write(f"| {r['cluster_id']} | {r['d_range']} | "
                    f"{r['classification']} | {r['n_7_star']} | "
                    f"{r['D_7_at_n_star']} | "
                    f"{r['lift7_chosen']} | {r['lift7_alt_c']} | "
                    f"{r['lift7_alt_d']} |\n")
        f.write("\n🐕☕⬡\n")
        f.write("\n— Mr Code, 11 May 2026 (Paper 3 v4.5 Task 3)\n")


if __name__ == '__main__':
    main()
