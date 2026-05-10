#!/usr/bin/env python3
"""Task 3 (Paper 3 v3.14): §6.5.1 extended windows at n = 500 and n = 1000.

v3.13 §6.5.1 establishes monotone-size-ordering specificity at windows n in
{20, 33, 50, 70, 90, 100} with multi-window aggregate p ≤ 0.005. Mr Adversary
asks: does the anomaly persist at larger windows or fade as small primes give
way to larger ones?

  (a) Small-prime phenomenon: z drops toward random as n grows.
  (b) Structural-position effect: z stays anomalous at all n.
  (c) Mixed / transition.

Computation. 1000-trial shuffle test (seed = trial * 137 + 42, matching v3.12)
at n in {500, 1000} for natural ordering only, both Definition A and Definition C.

Verification gate. Reproduce v3.13 Def C n=100 natural z within tolerance
(~3.08-3.10 per the published table). CinC noted small wobble is OK; halt
only if substantially different.
"""
import math
import os
import sys
import csv
import random
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve, chi5, five_series_primes
from task1_orderings import chi_seq_def_A, chi_seq_def_C, tie_count, order_natural

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

SIEVE_LIMIT = 200_000  # 1000 5-series primes ≈ 13k; 200k is generous
N_SHUFFLE = 1000
NEW_WINDOWS = [500, 1000]
ANCHOR_WINDOW = 100  # for verification


def shuffle_tie_count(chi_seq, trial):
    rng = random.Random(trial * 137 + 42)
    perm = list(range(len(chi_seq)))
    rng.shuffle(perm)
    return tie_count(chi_seq, perm)


def run_one(p5, n, def_label, chi_builder):
    chi_seq = chi_builder(p5, n)
    L = len(chi_seq)
    natural_T = tie_count(chi_seq, order_natural(L))
    t0 = time.time()
    shuf_counts = [shuffle_tie_count(chi_seq, i) for i in range(N_SHUFFLE)]
    t1 = time.time()
    mean = sum(shuf_counts) / N_SHUFFLE
    std = math.sqrt(sum((x - mean) ** 2 for x in shuf_counts) / (N_SHUFFLE - 1))
    z = (natural_T - mean) / std if std > 0 else 0.0
    p_ge = sum(1 for x in shuf_counts if x >= natural_T) / N_SHUFFLE
    n_distinct = len(set(shuf_counts))
    print(f"  Def {def_label} n={n:>4} L={L:>4}: T_nat={natural_T:>4}, "
          f"shuf_mean={mean:>7.2f}, shuf_std={std:>6.2f}, "
          f"z={z:>+6.3f}, p_ge={p_ge:>6.4f}  "
          f"[{t1-t0:.1f}s, n_distinct={n_distinct}]")
    return {
        'n': n, 'definition': def_label, 'L': L,
        'T_nat': natural_T, 'shuf_mean': mean, 'shuf_std': std,
        'z': z, 'p_ge': p_ge, 'n_distinct': n_distinct,
    }


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Sieving primes up to {SIEVE_LIMIT}...")
    primes = sieve(SIEVE_LIMIT)
    p5 = five_series_primes(primes)
    print(f"  5-series primes: {len(p5)}")

    # ---- Verification gate: Def C n=100 anchor ----
    print(f"\n{'='*72}")
    print("Verification gate: Def C n=100 natural z (target ~3.08-3.10)")
    print(f"{'='*72}")
    anchor = run_one(p5, ANCHOR_WINDOW, 'C', chi_seq_def_C)
    target_lo, target_hi = 3.00, 3.20
    if not (target_lo <= anchor['z'] <= target_hi):
        # Allow a wider tolerance per CinC's note ("halt only if substantially
        # different"); ±0.10 is the reported wobble range.
        print(f"  z = {anchor['z']:.3f} outside [{target_lo}, {target_hi}].")
        print(f"  HALT: anchor mismatch.")
        sys.exit(1)
    print(f"  z = {anchor['z']:.3f} within tolerance. OK.")

    # ---- Extended windows ----
    print(f"\n{'='*72}")
    print(f"Extended windows: n in {NEW_WINDOWS}, both definitions")
    print(f"{'='*72}")
    rows = [anchor]  # include the anchor as part of the table
    for n in NEW_WINDOWS:
        rows.append(run_one(p5, n, 'A', chi_seq_def_A))
        rows.append(run_one(p5, n, 'C', chi_seq_def_C))

    # ---- Combined table with v3.13 row context ----
    print(f"\n{'='*72}")
    print("Combined table (v3.13 windows + v3.14 extension)")
    print(f"{'='*72}")
    # v3.13 published values (Def A and Def C, natural z) — for the printed
    # table only; not re-run here.
    v3_13 = {
        'A': {20: 2.29, 33: 2.59, 50: 2.90, 70: 2.58, 90: 3.61, 100: 3.21},
        'C': {20: 2.14, 33: 2.45, 50: 2.75, 70: 2.71, 90: 3.33, 100: 3.08},
    }
    # New rows from this run (drop the n=100 anchor since v3.13 has it)
    new_rows = {(r['n'], r['definition']): r for r in rows
                if r['n'] in NEW_WINDOWS}

    print(f"\n  Definition A:")
    print(f"    {'n':>5}  {'z (this run)':>12}  {'v3.13 published':>16}  {'source':>10}")
    for n in [20, 33, 50, 70, 90, 100]:
        print(f"    {n:>5}  {'—':>12}  {v3_13['A'][n]:>16.2f}  {'v3.13':>10}")
    for n in NEW_WINDOWS:
        r = new_rows[(n, 'A')]
        print(f"    {n:>5}  {r['z']:>+12.3f}  {'—':>16}  {'v3.14 NEW':>10}")

    print(f"\n  Definition C (primary):")
    print(f"    {'n':>5}  {'z (this run)':>12}  {'v3.13 published':>16}  {'source':>10}")
    for n in [20, 33, 50, 70, 90]:
        print(f"    {n:>5}  {'—':>12}  {v3_13['C'][n]:>16.2f}  {'v3.13':>10}")
    print(f"    {ANCHOR_WINDOW:>5}  {anchor['z']:>+12.3f}  {v3_13['C'][100]:>16.2f}  "
          f"{'v3.14 anchor':>10}")
    for n in NEW_WINDOWS:
        r = new_rows[(n, 'C')]
        print(f"    {n:>5}  {r['z']:>+12.3f}  {'—':>16}  {'v3.14 NEW':>10}")

    # ---- Verdict per brief ----
    print(f"\n{'='*72}")
    print("Brief scenario classification")
    print(f"{'='*72}")
    z_500_C = new_rows[(500, 'C')]['z']
    z_1000_C = new_rows[(1000, 'C')]['z']
    z_500_A = new_rows[(500, 'A')]['z']
    z_1000_A = new_rows[(1000, 'A')]['z']

    print(f"  Def C: n=500 z = {z_500_C:+.3f}, n=1000 z = {z_1000_C:+.3f}")
    print(f"  Def A: n=500 z = {z_500_A:+.3f}, n=1000 z = {z_1000_A:+.3f}")

    def classify(z500, z1000):
        elev500 = abs(z500) > 2
        elev1000 = abs(z1000) > 2
        small500 = abs(z500) < 1
        small1000 = abs(z1000) < 1
        if elev500 and elev1000:
            return ("(b) STRUCTURAL-POSITION effect at all scales — z stays "
                    "elevated. Novel claim.")
        elif small500 and small1000:
            return ("(a) SMALL-PRIME phenomenon — z drops toward random as n "
                    "grows. §9 Q1(a) sharpens.")
        elif elev500 and not elev1000:
            return ("(c) TRANSITION near n ≈ 500-1000 — z elevated at 500, "
                    "drops at 1000. Worth reporting verbatim.")
        elif not elev500 and elev1000:
            return ("(c) Unexpected — z low at 500 but elevated at 1000. "
                    "Worth reporting verbatim.")
        else:
            return ("(c) MIXED / intermediate — neither cleanly elevated nor "
                    "cleanly dropped. Report as soft signal.")

    print(f"\n  Def C verdict: {classify(z_500_C, z_1000_C)}")
    print(f"  Def A verdict: {classify(z_500_A, z_1000_A)}")

    # ---- CSV ----
    csv_path = os.path.join(RESULTS_DIR, 'v3_14_task3_extended_windows.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['source', 'definition', 'n_window', 'L_eff',
                    'T_nat', 'shuf_mean', 'shuf_std', 'z', 'p_ge', 'n_distinct'])
        # v3.13 values for context (without recomputation; just published z's)
        for d in ('A', 'C'):
            for n in [20, 33, 50, 70, 90, 100]:
                w.writerow(['v3.13', d, n, '', '', '', '',
                            f"{v3_13[d][n]:.4f}", '', ''])
        # This run's anchor + new windows
        w.writerow(['v3.14_anchor', anchor['definition'], anchor['n'],
                    anchor['L'], anchor['T_nat'],
                    f"{anchor['shuf_mean']:.4f}", f"{anchor['shuf_std']:.4f}",
                    f"{anchor['z']:.4f}", f"{anchor['p_ge']:.4f}",
                    anchor['n_distinct']])
        for n in NEW_WINDOWS:
            for d in ('A', 'C'):
                r = new_rows[(n, d)]
                w.writerow(['v3.14_NEW', d, n, r['L'], r['T_nat'],
                            f"{r['shuf_mean']:.4f}", f"{r['shuf_std']:.4f}",
                            f"{r['z']:.4f}", f"{r['p_ge']:.4f}",
                            r['n_distinct']])
    print(f"\n  Saved: {csv_path}")

    # ---- Plot ----
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [warning] matplotlib unavailable; skipping plot")
        return

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ns_plot = [20, 33, 50, 70, 90, 100, 500, 1000]
    z_a = [v3_13['A'][n] for n in [20, 33, 50, 70, 90, 100]] + \
          [new_rows[(500, 'A')]['z'], new_rows[(1000, 'A')]['z']]
    z_c = [v3_13['C'][n] for n in [20, 33, 50, 70, 90]] + \
          [anchor['z']] + [new_rows[(500, 'C')]['z'], new_rows[(1000, 'C')]['z']]

    ax.plot(ns_plot, z_a, 'o-', color='#1f77b4', label='Definition A (natural)',
            markersize=7)
    ax.plot(ns_plot, z_c, 's-', color='#d62728', label='Definition C (natural, primary)',
            markersize=7)
    ax.axhline(2, color='gray', linestyle=':', alpha=0.7, label='z = 2 threshold')
    ax.axhline(0, color='black', linewidth=0.5, alpha=0.5)
    ax.axvline(100, color='gray', linestyle='--', alpha=0.5,
               label='v3.13 upper bound (n=100)')
    ax.set_xscale('log')
    ax.set_xticks(ns_plot)
    ax.set_xticklabels([str(n) for n in ns_plot])
    ax.set_xlabel('Window size n (5-series prime count, log scale)')
    ax.set_ylabel('Natural-ordering z (vs 1000-shuffle null)')
    ax.set_title('§6.5.1 z-score persistence: extended windows\n'
                 'Paper 3 v3.14 Task 3')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    fig.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, 'v3_14_task3_extended_windows.png')
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"  Saved: {plot_path}")


if __name__ == '__main__':
    main()
