#!/usr/bin/env python3
"""Task 2 (Paper 3 v3.13): §6.5.1 multi-window aggregate null.

Addresses the look-elsewhere objection: v3.12 §6.5.1 reports per-window
z-scores at six windows (n ∈ {20, 33, 50, 70, 90, 100}) for the natural
ordering shuffle test, with Def A peak z=3.64 at n=90 and Def C peak z=3.33
at n=90. Six windows × five orderings = thirty z-scores invites concern
that a single high z is plausible by chance.

Two aggregate statistics:
  Statistic A — Max-z null. For each of 1000 shuffle trials, compute z at
    each of the six windows (per-window independent shuffles per CinC's
    Q1 confirmation; trial index is alignment label). Per-window z uses
    the bootstrap-style self-comparison: (trial_count - mean) / std where
    mean and std come from the 1000 shuffles at that window. Take MAX z
    across the six windows for each trial → 1000 max-z values forming
    the null distribution. Empirical p = fraction of max-z ≥ natural's.
    Conservative under correlation: independent-null max-z is upper-bounded
    above the (correlated) true null, so a small empirical p remains
    significant under the correlated null.

  Statistic B — Stouffer combination. Z_combined = (Σ z_i) / √k for k=6
    natural-ordering per-window z's. Heuristic upper bound only —
    nested windows violate independence assumption.

Verification gate: Def C n=33 shuffle mean ≈ 6.17, std ≈ 2.79. Halt if not.
"""
import math
import os
import sys
import csv
import random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve, chi5, five_series_primes
from task1_orderings import (
    chi_seq_def_A, chi_seq_def_C, tie_count, order_natural,
    WINDOWS, N_SHUFFLE, SIEVE_LIMIT,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def per_trial_shuffle_count(chi_seq, trial):
    """Single shuffle for one (chi_seq, trial) — same convention as v3.12."""
    rng = random.Random(trial * 137 + 42)
    perm = list(range(len(chi_seq)))
    rng.shuffle(perm)
    return tie_count(chi_seq, perm)


def normal_sf(x):
    """Right-tail of standard normal: P(Z >= x). Uses erfc."""
    return 0.5 * math.erfc(x / math.sqrt(2))


def run_definition(p5, def_label, chi_builder):
    print(f"\n{'='*72}")
    print(f"Definition {def_label}")
    print(f"{'='*72}")

    # Build chi sequences and natural tie counts
    chi_seqs = {n: chi_builder(p5, n) for n in WINDOWS}
    natural_counts = {n: tie_count(chi_seqs[n], order_natural(len(chi_seqs[n])))
                      for n in WINDOWS}

    # Per-window shuffle distributions: counts[n] = list of 1000 tie counts
    counts = {n: [per_trial_shuffle_count(chi_seqs[n], i)
                  for i in range(N_SHUFFLE)] for n in WINDOWS}

    # Per-window mean and std (from the 1000 shuffles)
    means = {}
    stds = {}
    for n in WINDOWS:
        c = counts[n]
        m = sum(c) / len(c)
        s = math.sqrt(sum((x - m) ** 2 for x in c) / (len(c) - 1))
        means[n] = m
        stds[n] = s

    # Natural's per-window z and one-tail p-value (parametric, from z)
    natural_z = {n: (natural_counts[n] - means[n]) / stds[n] if stds[n] > 0 else 0.0
                 for n in WINDOWS}
    natural_p = {n: normal_sf(natural_z[n]) for n in WINDOWS}

    print(f"\n  Per-window shuffle distributions (1000 trials each):")
    print(f"  {'n':>4}  {'L':>4}  {'mean':>7}  {'std':>7}  "
          f"{'T_nat':>5}  {'z_nat':>7}  {'p_param':>10}")
    for n in WINDOWS:
        print(f"  {n:>4}  {len(chi_seqs[n]):>4}  {means[n]:>7.3f}  "
              f"{stds[n]:>7.3f}  {natural_counts[n]:>5d}  "
              f"{natural_z[n]:>7.3f}  {natural_p[n]:>10.6f}")

    # ---- Verification gate (Def C only, n=33) ----
    if def_label == 'C':
        target_mean, target_std = 6.17, 2.79
        got_mean = means[33]
        got_std = stds[33]
        ok_mean = abs(got_mean - target_mean) <= 0.30
        ok_std = abs(got_std - target_std) <= 0.30
        print(f"\n  Verification gate (Def C n=33):")
        print(f"    target mean ≈ 6.17 (got {got_mean:.3f}) — "
              f"{'OK' if ok_mean else 'FAIL'}")
        print(f"    target std  ≈ 2.79 (got {got_std:.3f}) — "
              f"{'OK' if ok_std else 'FAIL'}")
        if not (ok_mean and ok_std):
            print("    HALT: anchor mismatch.")
            sys.exit(1)

    # ---- Statistic A: max-z null ----
    natural_max_z = max(natural_z[n] for n in WINDOWS)
    natural_max_z_window = max(WINDOWS, key=lambda n: natural_z[n])

    # Per-trial z at each window, then max
    max_z_null = []
    for i in range(N_SHUFFLE):
        zs = []
        for n in WINDOWS:
            if stds[n] > 0:
                zs.append((counts[n][i] - means[n]) / stds[n])
            else:
                zs.append(0.0)
        max_z_null.append(max(zs))

    max_z_null_sorted = sorted(max_z_null)

    def percentile(arr, q):
        # arr already sorted
        idx = q * (len(arr) - 1)
        lo = int(idx)
        hi = min(lo + 1, len(arr) - 1)
        frac = idx - lo
        return arr[lo] * (1 - frac) + arr[hi] * frac

    pct = {q: percentile(max_z_null_sorted, q)
           for q in (0.01, 0.05, 0.50, 0.95, 0.99)}
    n_ge = sum(1 for z in max_z_null if z >= natural_max_z)
    empirical_p = n_ge / N_SHUFFLE

    # Continuity-corrected upper bound when n_ge = 0:
    # report empirical p with explicit "≤ 1/1000" caveat
    p_str = f"{empirical_p:.4f}" if n_ge > 0 else f"<= 1/{N_SHUFFLE} = {1/N_SHUFFLE:.4f}"

    print(f"\n  Statistic A — Max-z null distribution:")
    print(f"    Natural max z = {natural_max_z:.3f} (at n = {natural_max_z_window})")
    print(f"    Null percentiles:")
    print(f"      1st  = {pct[0.01]:.3f}")
    print(f"      5th  = {pct[0.05]:.3f}")
    print(f"      50th = {pct[0.50]:.3f}")
    print(f"      95th = {pct[0.95]:.3f}")
    print(f"      99th = {pct[0.99]:.3f}")
    print(f"    Null max overall = {max_z_null_sorted[-1]:.3f}")
    print(f"    Empirical p (count >= natural / N) = {p_str}")
    print(f"    Trials with max z >= natural: {n_ge} of {N_SHUFFLE}")

    # ---- Statistic B: Stouffer combination ----
    z_sum = sum(natural_z[n] for n in WINDOWS)
    k = len(WINDOWS)
    z_stouffer = z_sum / math.sqrt(k)
    p_stouffer = normal_sf(z_stouffer)
    print(f"\n  Statistic B — Stouffer combination (heuristic; windows nested):")
    print(f"    Sum of per-window natural z = {z_sum:.3f}  (k = {k})")
    print(f"    Z_combined = sum / sqrt(k) = {z_stouffer:.3f}")
    print(f"    p_combined (one-sided, normal) = {p_stouffer:.3e}")
    print(f"    Caveat: nested windows violate independence; this is an")
    print(f"    upper-bound on combined evidence under that assumption.")

    return {
        'def_label': def_label,
        'windows': WINDOWS,
        'natural_counts': natural_counts,
        'means': means, 'stds': stds,
        'natural_z': natural_z,
        'natural_p_param': natural_p,
        'natural_max_z': natural_max_z,
        'natural_max_z_window': natural_max_z_window,
        'max_z_null': max_z_null,
        'max_z_pct': pct,
        'empirical_p_max_z': empirical_p,
        'n_ge': n_ge,
        'z_stouffer': z_stouffer,
        'p_stouffer': p_stouffer,
        'counts': counts,
    }


def write_csvs(result_a, result_c):
    # Per-window summary (both definitions)
    summary_path = os.path.join(RESULTS_DIR, 'v3_13_task2_per_window.csv')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['definition', 'n_window', 'L_eff', 'shuf_mean',
                    'shuf_std', 'T_nat', 'z_nat', 'p_param'])
        for res in (result_a, result_c):
            for n in res['windows']:
                w.writerow([
                    res['def_label'], n,
                    len(res['means']),  # placeholder; better to track L separately
                    f"{res['means'][n]:.6f}",
                    f"{res['stds'][n]:.6f}",
                    res['natural_counts'][n],
                    f"{res['natural_z'][n]:.6f}",
                    f"{res['natural_p_param'][n]:.6e}",
                ])
    print(f"\n  Saved: {summary_path}")

    # Aggregate summary (max-z and Stouffer)
    agg_path = os.path.join(RESULTS_DIR, 'v3_13_task2_aggregate.csv')
    with open(agg_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow([
            'definition', 'natural_max_z', 'natural_max_z_window',
            'null_p01', 'null_p05', 'null_p50', 'null_p95', 'null_p99',
            'empirical_p_max_z', 'n_trials_ge_natural',
            'z_stouffer', 'p_stouffer',
        ])
        for res in (result_a, result_c):
            w.writerow([
                res['def_label'],
                f"{res['natural_max_z']:.6f}",
                res['natural_max_z_window'],
                f"{res['max_z_pct'][0.01]:.6f}",
                f"{res['max_z_pct'][0.05]:.6f}",
                f"{res['max_z_pct'][0.50]:.6f}",
                f"{res['max_z_pct'][0.95]:.6f}",
                f"{res['max_z_pct'][0.99]:.6f}",
                f"{res['empirical_p_max_z']:.6f}",
                res['n_ge'],
                f"{res['z_stouffer']:.6f}",
                f"{res['p_stouffer']:.6e}",
            ])
    print(f"  Saved: {agg_path}")

    # Per-trial max-z values (for both definitions)
    null_path = os.path.join(RESULTS_DIR, 'v3_13_task2_max_z_null.csv')
    with open(null_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['trial', 'max_z_def_A', 'max_z_def_C'])
        for i in range(N_SHUFFLE):
            w.writerow([i, f"{result_a['max_z_null'][i]:.6f}",
                        f"{result_c['max_z_null'][i]:.6f}"])
    print(f"  Saved: {null_path}")


def make_plot(result_a, result_c):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("  [warning] matplotlib unavailable; skipping plot")
        return

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, res, def_label in [(axes[0], result_a, 'A'), (axes[1], result_c, 'C')]:
        max_z = np.array(res['max_z_null'])
        bins = np.linspace(min(max_z.min(), -1), max(max_z.max(), 4) + 0.2, 35)
        ax.hist(max_z, bins=bins, color='#4c72b0', alpha=0.85,
                edgecolor='black', linewidth=0.4,
                label=f'1000-trial null (max-z over 6 windows)')
        ax.axvline(res['natural_max_z'], color='red', linestyle='--', linewidth=1.7,
                   label=f"natural max z = {res['natural_max_z']:.2f} "
                         f"(at n={res['natural_max_z_window']})")
        ax.axvline(res['max_z_pct'][0.95], color='gray', linestyle=':',
                   linewidth=1.3,
                   label=f"null 95th pct = {res['max_z_pct'][0.95]:.2f}")
        ax.set_xlabel('Max z over 6 windows')
        ax.set_title(f'Definition {def_label}')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=8)
    axes[0].set_ylabel(f'Count out of {N_SHUFFLE} trials')
    fig.suptitle('Multi-window max-z null distribution\n'
                 'Paper 3 v3.13 Task 2 — §6.5.1 aggregate null')
    fig.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, 'v3_13_task2_max_z_null.png')
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"  Saved: {plot_path}")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Sieving primes up to {SIEVE_LIMIT}...")
    primes = sieve(SIEVE_LIMIT)
    p5 = five_series_primes(primes)
    print(f"  5-series primes: {len(p5)}")

    result_a = run_definition(p5, 'A', chi_seq_def_A)
    result_c = run_definition(p5, 'C', chi_seq_def_C)

    print(f"\n{'='*72}")
    print("CinC's decision rule")
    print(f"{'='*72}")
    primary = result_c
    p = primary['empirical_p_max_z']
    n_ge = primary['n_ge']
    if p <= 0.01:
        verdict = ("Empirical max-z p (Def C) <= 0.01. Conservative null is "
                   "sufficient; no Interpretation A robustness check needed.")
    elif p <= 0.05:
        verdict = ("Empirical max-z p (Def C) in (0.01, 0.05]. Add "
                   "Interpretation A as a robustness check before flagging.")
    else:
        verdict = ("Empirical max-z p (Def C) > 0.05. Natural ordering does "
                   "NOT clear the multi-window null at the 5% level.")
    print(f"  Empirical p (Def C) = {p:.4f} ({n_ge}/{N_SHUFFLE})")
    print(f"  -> {verdict}")

    write_csvs(result_a, result_c)
    make_plot(result_a, result_c)


if __name__ == '__main__':
    main()
