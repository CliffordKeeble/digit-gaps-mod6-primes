#!/usr/bin/env python3
"""Paper 201 Task 8 — Paper 199 chi_5 running-sum cross-test at
bounded merged regime upper edges.

Per pre-registration `v3_12_data/briefs/mr_code_brief_paper_201_task8.md`
(committed at 7dedc6f BEFORE this implementation).

Operational definitions (brief §3, verbatim):
  - P_5 = {p prime: p ≡ 5 (mod 6)}, sorted ascending.
  - chi_5 = real Legendre symbol (p/5): {0, 1, 4 mod 5} → {0, +1, +1},
    {2, 3 mod 5} → {-1, -1}.
  - S_5(n) = Σ_{i=1}^{n} chi_5(P_5[i]).  S_5(1) = chi_5(5) = 0.

Test statistic — Concordant Extremity Index (CEI):
  For V_r = S_5(n_5_r) at evaluation points r ∈ {2, 3, 4, 5},
  compute percentile rank π_r in a 1000-draw baseline distribution
  B = {S_5(n) : n in baseline draws from [200, 4000] excluding ±50
  around evaluation points; seed 8088}.
  Classify π_r: 'upper' if > 0.75; 'lower' if < 0.25; else 'central'.
  CEI = max(#upper, #lower) ∈ {0, 1, 2, 3, 4}.

Thresholds (HEADLINE CEI):
  (α) CEI ≤ 2  (null P ≈ 0.92, accumulated)
  (γ) CEI = 3  (null P ≈ 0.094)
  (β) CEI = 4  (null P ≈ 0.0078)

Outputs:
  v3_12_data/results/task8_paper199_crosstest.csv
  v3_12_data/results/task8_paper199_crosstest_summary.md
  v3_12_data/results/task8_baseline_distribution.png
"""
import os
import sys
import csv
import time

import numpy as np
import mpmath

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve

HERE = os.path.dirname(__file__)
RESULTS_DIR = os.path.join(HERE, 'results')
CSV_OUT = os.path.join(RESULTS_DIR, 'task8_paper199_crosstest.csv')
MD_OUT = os.path.join(RESULTS_DIR,
                      'task8_paper199_crosstest_summary.md')
PNG_OUT = os.path.join(RESULTS_DIR,
                       'task8_baseline_distribution.png')
TASK5_CSV = os.path.join(RESULTS_DIR,
                         'task5_merged_regimes_detected.csv')

SIEVE_LIMIT = 200_000
BASELINE_LO = 200
BASELINE_HI = 4000
N_MAX = BASELINE_HI    # must cover both largest evaluation point (3458)
                       # AND the baseline upper bound (4000)
BASELINE_N = 1000
BASELINE_SEED = 8088
EXCLUSION_HALF = 50

# Expected anchors (brief §3, §6)
EXPECTED_REGIMES = [
    # (regime, u_r, n_5_expected)
    (2, 1717,  506),
    (3, 4231, 1116),
    (4, 8318, 2034),
    (5, 15045, 3458),
]
EXPECTED_S5_AT_10 = 1  # Anchor B reference (brief §6)


def chi5(p):
    """Legendre symbol (p/5). Returns +1, -1, or 0 (only at p = 5)."""
    r = p % 5
    if r == 0:
        return 0
    if r in (1, 4):
        return 1
    return -1


def compute_D5_via_logsum(p5_list, n_max):
    """Compute D_5[i] = digit-length of Π of first (i+1) 5-series primes
    using mpmath log10-sum (matches Task 5/6/7 approach)."""
    mpmath.mp.dps = 200
    D = []
    log10_prod = mpmath.mpf(0)
    for p in p5_list[:n_max]:
        log10_prod += mpmath.log10(mpmath.mpf(p))
        d = int(mpmath.floor(log10_prod)) + 1
        D.append(d)
    return D


def find_n_for_digit_length(D, target_d):
    for n in range(1, len(D) + 1):
        if D[n - 1] >= target_d:
            return n
    return None


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    t_start = time.time()

    print("=" * 72)
    print("Task 8 — Paper 199 chi_5 cross-test at bounded merged regime "
          "upper edges")
    print("=" * 72)
    print(f"  Evaluation points (n_5_r): "
          f"{[n for _, _, n in EXPECTED_REGIMES]}")
    print(f"  Baseline: {BASELINE_N} draws from [{BASELINE_LO}, "
          f"{BASELINE_HI}] excluding ±{EXCLUSION_HALF} around "
          f"evaluation points; seed {BASELINE_SEED}")

    # ---- Sieve and P_5 ----
    print(f"\nSieving primes up to {SIEVE_LIMIT}; building P_5 "
          f"(5-series natural ordering)...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p % 6 == 5]
    # Brief §3: P_5[1] = 5, P_5[2] = 11, P_5[3] = 17, ...
    assert p5[0] == 5, f"P_5[1] should be 5, got {p5[0]}"
    assert p5[1] == 11, f"P_5[2] should be 11, got {p5[1]}"
    assert p5[2] == 17, f"P_5[3] should be 17, got {p5[2]}"
    print(f"  First 10 P_5 primes: {p5[:10]}  "
          f"(matches brief §6 Anchor B reference)")
    print(f"  Total P_5 primes available: {len(p5)}")
    assert len(p5) > N_MAX, f"Need at least {N_MAX} P_5 primes"

    # ---- Compute S_5(n) ----
    print(f"\nComputing S_5(n) for n in [1, {N_MAX}]...")
    S5 = [None]  # 1-indexed; S5[0] unused (None for clarity)
    cum = 0
    for i, p in enumerate(p5[:N_MAX], start=1):
        cum += chi5(p)
        S5.append(cum)
    # S5[n] = sum of chi_5 over first n P_5 primes

    # ---- Anchor B — S_5(10) = +1 ----
    print("\n" + "=" * 72)
    print("Anchor B — S_5(10) reference check")
    print("=" * 72)
    # Echo per-prime chi_5 to make the trace visible
    print("  Per-prime chi_5 over P_5[1..10]:")
    cum_check = 0
    for i in range(1, 11):
        c = chi5(p5[i - 1])
        cum_check += c
        print(f"    P_5[{i}] = {p5[i-1]:3d}  (mod 5 = {p5[i-1] % 5})  "
              f"chi_5 = {c:+d}  running = {cum_check:+d}")
    print(f"  S_5(10) = {S5[10]}  (expected {EXPECTED_S5_AT_10})  "
          f"{'OK' if S5[10] == EXPECTED_S5_AT_10 else 'FAIL'}")
    if S5[10] != EXPECTED_S5_AT_10:
        print("  HALT: Anchor B mismatch.")
        sys.exit(1)

    # ---- Compute D_5 for Anchor A ----
    print("\nComputing D_5(n) (mpmath log10-sum) for Anchor A...")
    t0 = time.time()
    D5 = compute_D5_via_logsum(p5, N_MAX)
    print(f"  D_5 done in {time.time() - t0:.1f}s; "
          f"D_5({N_MAX}) = {D5[-1]}")

    # ---- Anchor A — four-point n_5 values ----
    print("\n" + "=" * 72)
    print("Anchor A — four-point n_5 values")
    print("=" * 72)
    halt = False
    for r, u_r, n5_exp in EXPECTED_REGIMES:
        n5 = find_n_for_digit_length(D5, u_r + 1)
        ok = (n5 == n5_exp)
        print(f"  Regime {r}: u_r + 1 = {u_r + 1}, computed n_5 = "
              f"{n5}  (want {n5_exp})  "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            halt = True
    if halt:
        sys.exit(1)

    # ---- Anchor C — Paper 199 cross-reference ----
    print("\n" + "=" * 72)
    print("Anchor C — Paper 199 reference")
    print("=" * 72)
    print("  No Paper 199 reference table pointer provided in brief; "
          "Anchor B (S_5(10) = +1) is the binding sanity check.")

    # ---- Compute V_r = S_5(n_5_r) ----
    print("\n" + "=" * 72)
    print("Evaluation values V_r")
    print("=" * 72)
    V = {}
    for r, u_r, n5 in EXPECTED_REGIMES:
        V[r] = S5[n5]
        print(f"  V_{r} = S_5({n5}) = {V[r]:+d}  "
              f"(regime {r}: u_r = {u_r})")

    # ---- Baseline draw ----
    print("\n" + "=" * 72)
    print(f"Baseline draw — {BASELINE_N} samples from "
          f"[{BASELINE_LO}, {BASELINE_HI}] excluding ±"
          f"{EXCLUSION_HALF} around evaluation points")
    print("=" * 72)
    eval_n5 = {n5 for _, _, n5 in EXPECTED_REGIMES}
    excluded = set()
    for n5 in eval_n5:
        for n in range(n5 - EXCLUSION_HALF, n5 + EXCLUSION_HALF + 1):
            if BASELINE_LO <= n <= BASELINE_HI:
                excluded.add(n)
    available = [n for n in range(BASELINE_LO, BASELINE_HI + 1)
                  if n not in excluded]
    print(f"  Available baseline integers: {len(available)} "
          f"({BASELINE_HI - BASELINE_LO + 1} - "
          f"{len(excluded)} excluded)")
    rng = np.random.default_rng(BASELINE_SEED)
    baseline_idx = rng.choice(len(available), size=BASELINE_N,
                              replace=False)
    baseline_n = sorted(available[i] for i in baseline_idx)
    # Anchor D
    bad = [n for n in baseline_n if n in excluded]
    print(f"  Anchor D — baseline draws in excluded region: "
          f"{len(bad)}  {'FAIL' if bad else 'OK'}")
    if bad:
        sys.exit(1)
    baseline_S5 = [S5[n] for n in baseline_n]

    # ---- Baseline distribution summary ----
    B = np.array(baseline_S5)
    print(f"\n  Baseline distribution summary (n = {len(B)}):")
    print(f"    min = {B.min()}, max = {B.max()}")
    print(f"    median = {np.median(B):.1f}, IQR = "
          f"[{np.percentile(B, 25):.1f}, {np.percentile(B, 75):.1f}]")
    print(f"    mean = {B.mean():.3f}, std = {B.std():.3f}")
    p25 = np.percentile(B, 25)
    p75 = np.percentile(B, 75)
    print(f"    25th percentile = {p25}, 75th percentile = {p75}")

    # ---- Percentile ranks π_r ----
    print("\n" + "=" * 72)
    print("Percentile ranks and tail classification")
    print("=" * 72)

    def midrank_percentile(v, ref):
        """Fraction strictly less than v + 0.5 × fraction of ties, in ref."""
        ref_arr = np.asarray(ref)
        less = np.sum(ref_arr < v)
        ties = np.sum(ref_arr == v)
        return (less + 0.5 * ties) / len(ref_arr)

    pi = {}
    tail = {}
    for r, _, _ in EXPECTED_REGIMES:
        pi_r = midrank_percentile(V[r], B)
        pi[r] = pi_r
        if pi_r > 0.75:
            tail[r] = 'upper'
        elif pi_r < 0.25:
            tail[r] = 'lower'
        else:
            tail[r] = 'central'
        print(f"  V_{r} = {V[r]:+d}: π_{r} = {pi_r:.4f}  → "
              f"{tail[r]}")

    # ---- CEI ----
    n_upper = sum(1 for r in tail if tail[r] == 'upper')
    n_lower = sum(1 for r in tail if tail[r] == 'lower')
    CEI = max(n_upper, n_lower)
    print(f"\n  # upper-tail: {n_upper}; # lower-tail: {n_lower}; "
          f"# central: {4 - n_upper - n_lower}")
    print(f"  CEI = max(upper, lower) = {CEI}")

    # ---- Outcome ----
    print("\n" + "=" * 72)
    print("Pre-registered outcome")
    print("=" * 72)
    if CEI <= 2:
        outcome = 'α'
        framing = ("No systematic pattern.  Paper 201 §9 Q4 candidate "
                   "(d) becomes 'tested with no systematic evidence at "
                   "four-point cross-test'; the χ_5 candidate weakens "
                   "relative to candidates (a) and (b).")
    elif CEI == 3:
        outcome = 'γ'
        framing = ("Suggestive concordance.  Paper 201 §9 Q4 candidate "
                   "(d) becomes 'tested with suggestive concordance at "
                   "three of four points'; the χ_5 candidate is not "
                   "eliminated but is not decisively strengthened.")
    else:  # CEI == 4
        outcome = 'β'
        framing = ("Decisive concordance.  Paper 201 §9 Q4 candidate "
                   "(d) becomes 'tested with decisive four-point "
                   "concordance'; the χ_5 candidate is strengthened to "
                   "'leading structural-mechanism candidate among "
                   "(a), (b), (d)'.")
    print(f"  CEI = {CEI}  →  Outcome ({outcome})")
    print(f"  Framing update: {framing}")

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
        fig, ax = plt.subplots(1, 1, figsize=(11, 6.5))
        bins = np.arange(B.min() - 0.5, B.max() + 1.5, 1)
        ax.hist(B, bins=bins, color='#1f77b4', alpha=0.65,
                label=f'baseline (n = {BASELINE_N})')
        ax.axvline(p25, color='gray', linestyle=':', linewidth=2,
                   label=f'25th pctile = {p25:.1f}')
        ax.axvline(p75, color='gray', linestyle=':', linewidth=2,
                   label=f'75th pctile = {p75:.1f}')
        colors = ['#d62728', '#ff7f0e', '#2ca02c', '#9467bd']
        for (r, _, n5), color in zip(EXPECTED_REGIMES, colors):
            ax.axvline(V[r], color=color, linestyle='-', linewidth=2,
                       label=f'V_{r} = S_5({n5}) = {V[r]:+d}  '
                             f'(π = {pi[r]:.3f}, {tail[r]})')
        ax.set_xlabel('S_5(n) = Σ χ_5 over first n P_5 primes')
        ax.set_ylabel('baseline draw count')
        ax.set_title(f'Task 8 — chi_5 running-sum cross-test\n'
                     f'CEI = {CEI}; outcome ({outcome})',
                     fontsize=11)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(PNG_OUT, dpi=120)
        plt.close(fig)
        print(f"  Saved: {PNG_OUT}")

    # ---- CSV ----
    print(f"\nWriting CSV (4 evaluation rows + {BASELINE_N} baseline rows)...")
    with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['n', 'S_5_n', 'source', 'regime', 'percentile_rank',
                    'tail'])
        for r, _, n5 in EXPECTED_REGIMES:
            w.writerow([n5, V[r], 'evaluation', r,
                        f"{pi[r]:.6f}", tail[r]])
        for n in baseline_n:
            w.writerow([n, S5[n], 'baseline', '', '', ''])
    print(f"  Saved: {CSV_OUT}")

    # ---- Summary md ----
    write_summary(V, pi, tail, CEI, outcome, framing, B, p25, p75,
                  baseline_n, time.time() - t_start)
    print(f"  Saved: {MD_OUT}")

    # ---- Final status ----
    print("\n" + "=" * 72)
    print("TASK 8 — STATUS")
    print("=" * 72)
    print(f"All anchors (A, B, D): PASS  (C: no Paper 199 reference; "
          f"B binding)")
    print(f"V values: " +
          ", ".join(f"V_{r} = {V[r]:+d}" for r, *_ in EXPECTED_REGIMES))
    print(f"π ranks : " +
          ", ".join(f"π_{r} = {pi[r]:.4f}" for r, *_ in EXPECTED_REGIMES))
    print(f"Tails   : " +
          ", ".join(f"{r}:{tail[r]}" for r, *_ in EXPECTED_REGIMES))
    print(f"CEI = {CEI}  →  outcome ({outcome})")
    print(f"Total runtime: {time.time() - t_start:.1f}s")
    print("\nEnd-of-task: PASS")


def write_summary(V, pi, tail, CEI, outcome, framing, B, p25, p75,
                  baseline_n, total_runtime):
    with open(MD_OUT, 'w', encoding='utf-8') as f:
        f.write("# Task 8 — Paper 199 chi_5 running-sum cross-test: "
                "summary\n\n")
        f.write(f"**Date:** 17 May 2026.\n")
        f.write(f"**Pre-registration:** `v3_12_data/briefs/"
                f"mr_code_brief_paper_201_task8.md`.\n")
        f.write(f"**Runtime:** {total_runtime:.1f}s.\n")
        f.write(f"**Baseline:** {BASELINE_N} draws from "
                f"[{BASELINE_LO}, {BASELINE_HI}]; "
                f"seed {BASELINE_SEED}; excluding ±"
                f"{EXCLUSION_HALF} around evaluation points.\n\n")

        f.write("## Anchors\n\n")
        f.write("- Anchor A (four n_5 values from D_5 cumulative "
                "product): OK.\n")
        f.write("- Anchor B (S_5(10) = +1, hand-computed reference): "
                "OK.\n")
        f.write("- Anchor C (Paper 199 reference table): no pointer "
                "provided; B binding.\n")
        f.write("- Anchor D (baseline excludes ±50 around evaluation "
                "points): OK.\n\n")

        f.write("## Evaluation values V_r and percentile ranks\n\n")
        f.write("| Regime r | u_r | n_5_r | V_r = S_5(n_5_r) | "
                "Percentile rank π_r | Tail |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r, u_r, n5 in EXPECTED_REGIMES:
            f.write(f"| {r} | {u_r} | {n5} | {V[r]:+d} | "
                    f"{pi[r]:.4f} | {tail[r]} |\n")
        f.write("\n")

        n_upper = sum(1 for r in tail if tail[r] == 'upper')
        n_lower = sum(1 for r in tail if tail[r] == 'lower')
        f.write(f"**# upper-tail (π > 0.75):** {n_upper}\n")
        f.write(f"**# lower-tail (π < 0.25):** {n_lower}\n")
        f.write(f"**# central:** {4 - n_upper - n_lower}\n\n")
        f.write(f"**CEI = max(#upper, #lower) = {CEI}**\n\n")

        f.write("## Baseline distribution summary\n\n")
        f.write(f"| Statistic | Value |\n|---|---|\n")
        f.write(f"| n (draws) | {len(B)} |\n")
        f.write(f"| min | {int(B.min())} |\n")
        f.write(f"| max | {int(B.max())} |\n")
        f.write(f"| median | {np.median(B):.1f} |\n")
        f.write(f"| mean | {B.mean():.3f} |\n")
        f.write(f"| std | {B.std():.3f} |\n")
        f.write(f"| 25th percentile | {p25:.1f} |\n")
        f.write(f"| 75th percentile | {p75:.1f} |\n")
        f.write(f"| IQR width | {p75 - p25:.1f} |\n\n")

        f.write("## Pre-registered outcome — ({}) \n\n".format(outcome))
        f.write(f"**CEI = {CEI}.**  "
                f"Pre-registered: CEI ≤ 2 → (α) [P ≈ 0.92 under null]; "
                f"CEI = 3 → (γ) [P ≈ 0.094]; CEI = 4 → (β) "
                f"[P ≈ 0.0078].\n\n")
        f.write(f"Outcome: **({outcome})**.\n\n")
        f.write(f"**Framing update applied to Paper 201 §9 Q4 candidate "
                f"(d):**  {framing}\n\n")

        f.write("## Honest-reporting commitments (per brief §9)\n\n")
        f.write("- All four evaluation values, percentile ranks, and "
                "tail classifications reported.\n")
        f.write("- No post-hoc adjustment of baseline range, baseline "
                "size, exclusion margin, tail thresholds, or test "
                "statistic.\n")
        f.write("- No selection of alternative readings if outcome "
                "lands at (α).\n\n")

        f.write("## Deviations from pre-registration\n\n")
        f.write("None.\n\n")

        f.write("🐕☕⬡\n\n")
        f.write("— Mr Code, 17 May 2026 (Paper 201 v1.2 Task 8)\n")


if __name__ == '__main__':
    main()
