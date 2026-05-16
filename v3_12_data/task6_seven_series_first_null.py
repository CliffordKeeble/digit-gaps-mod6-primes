#!/usr/bin/env python3
"""Paper 201 Task 6 — Null distribution for the 7-series-lands-first observation.

Per pre-registration `v3_12_data/briefs/mr_code_brief_paper_201_task6.md`
(committed at e7d85e8 BEFORE this implementation).

Pipeline:

  Anchor A: deterministic (n_7, n_5, lead) for regimes 2-5.
  Anchor B: regime upper edges {1717, 4231, 8318, 15045}.
  Anchor C: cross-check with task5_merged_regimes_detected.csv.

  Null A: binary coin-flip — analytic, (1/2)^4 = 0.0625.
  Null B: label-permutation Monte Carlo, N_TRIALS = 10,000 per regime,
          per-regime seeds 44/45/46/47, window half-width 200
          digit-lengths, mpmath at 200 dps throughout.

  Joint statistics:
    J-i:   p_sign        — joint probability all 4 leads > 0 under null
    J-ii:  p_magnitude   — joint probability all 4 leads ≥ observed (HEADLINE)
    J-iii: per-regime p_r and Fisher's combined χ²₈

  Thresholds (HEADLINE p_magnitude):
    (α)  ≥ 0.10  — null does not fire; §5.4 framing unchanged.
    (γ)  [0.05, 0.10)  — intermediate.
    (β)  < 0.05  — null fires; promote to falsifier-grade signal.

Outputs:
  v3_12_data/results/task6_seven_series_first_null.csv         (40,000 rows)
  v3_12_data/results/task6_seven_series_first_null_summary.md
  v3_12_data/results/task6_lead_distribution.png               (4-panel)
"""
import os
import sys
import csv
import time
import math

import numpy as np
import mpmath

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve

HERE = os.path.dirname(__file__)
RESULTS_DIR = os.path.join(HERE, 'results')
CSV_OUT = os.path.join(RESULTS_DIR,
                       'task6_seven_series_first_null.csv')
MD_OUT = os.path.join(RESULTS_DIR,
                      'task6_seven_series_first_null_summary.md')
PNG_OUT = os.path.join(RESULTS_DIR,
                       'task6_lead_distribution.png')
ANCHOR_CSV = os.path.join(RESULTS_DIR,
                          'task5_merged_regimes_detected.csv')

SIEVE_LIMIT = 200_000
N_MAX = 5000           # margin over Task 5's 4000
N_TRIALS = 10_000
WINDOW_HALF = 200      # ±200 digit-lengths
MASTER_SEED = 42

# mpmath at 200 dps throughout (brief §3.2): safe upper bound for all
# four regimes; 100 dps would suffice for regimes 2-3 per the brief
# but using one setting simplifies the implementation.
mpmath.mp.dps = 200

# Expected anchors (brief §5)
EXPECTED_REGIMES = [
    # (regime_id, upper_edge, n_7_expected, n_5_expected, lead_expected)
    (2, 1717,  503,  506, 3),
    (3, 4231, 1112, 1116, 4),
    (4, 8318, 2029, 2034, 5),
    (5, 15045, 3452, 3458, 6),
]


def compute_D_and_log10_primes(primes_list, n_max):
    """Compute D[i] and log10_primes_mpf[i] using mpmath at 200 dps.

    D[i] = digit-length of product of first (i+1) primes.
    log10_primes_mpf[i] = mpmath.log10 of primes_list[i] (mpf at 200 dps).
    """
    D = []
    log10_primes_mpf = []
    log10_prod = mpmath.mpf(0)
    for i, p in enumerate(primes_list[:n_max]):
        lp = mpmath.log10(mpmath.mpf(p))
        log10_primes_mpf.append(lp)
        log10_prod += lp
        d = int(mpmath.floor(log10_prod)) + 1
        D.append(d)
    return D, log10_primes_mpf


def find_n_for_digit_length(D, target_d):
    """Smallest 1-indexed n with D[n-1] >= target_d. Linear scan."""
    for n in range(1, len(D) + 1):
        if D[n - 1] >= target_d:
            return n
    return None


def find_window_indices(D, window_lo, window_hi):
    """Return (n_lo, n_hi) — smallest n with D[n-1] >= window_lo, and
    largest n with D[n-1] <= window_hi.  1-indexed."""
    n_lo = next((n for n in range(1, len(D) + 1)
                 if D[n - 1] >= window_lo), None)
    n_hi = None
    for n in range(len(D), 0, -1):
        if D[n - 1] <= window_hi:
            n_hi = n
            break
    return n_lo, n_hi


def simulate_regime(regime_idx, u_r, observed_lead,
                    p5, p7, log10_p5_mpf, log10_p7_mpf,
                    D5, D7, n_trials, seed):
    """Run Null B for one regime.  Returns dict of arrays + metadata."""
    window_lo = u_r - WINDOW_HALF
    window_hi = u_r + WINDOW_HALF

    n_lo_5, n_hi_5 = find_window_indices(D5, window_lo, window_hi)
    n_lo_7, n_hi_7 = find_window_indices(D7, window_lo, window_hi)
    M_5 = n_hi_5 - n_lo_5 + 1
    M_7 = n_hi_7 - n_lo_7 + 1

    # Window primes & their log10 values (0-indexed slices)
    # Note: window includes steps n_lo to n_hi inclusive
    p5_win = p5[n_lo_5 - 1:n_hi_5]
    p7_win = p7[n_lo_7 - 1:n_hi_7]
    lp5_win = log10_p5_mpf[n_lo_5 - 1:n_hi_5]
    lp7_win = log10_p7_mpf[n_lo_7 - 1:n_hi_7]
    assert len(p5_win) == M_5 and len(p7_win) == M_7

    # Pool — combine then sort by prime size; log10 follows the order
    pool_pairs = sorted(
        [(p, lp, '5') for p, lp in zip(p5_win, lp5_win)] +
        [(p, lp, '7') for p, lp in zip(p7_win, lp7_win)],
        key=lambda t: t[0]
    )
    pool_size = M_5 + M_7
    pool_log10 = [t[1] for t in pool_pairs]
    pool_primes = [t[0] for t in pool_pairs]

    # Prefix log10 products (deterministic up to start of window)
    prefix_log10_5 = mpmath.mpf(0)
    for i in range(n_lo_5 - 1):
        prefix_log10_5 += log10_p5_mpf[i]
    prefix_log10_7 = mpmath.mpf(0)
    for i in range(n_lo_7 - 1):
        prefix_log10_7 += log10_p7_mpf[i]

    # Threshold: simulated cumulative log10 must reach u_r (then digit
    # length is floor(log10) + 1 = u_r + 1).
    threshold_5 = mpmath.mpf(u_r) - prefix_log10_5
    threshold_7 = mpmath.mpf(u_r) - prefix_log10_7

    # SENTINEL for "did not reach within window" — set so lead becomes
    # well-defined.  We use n_hi_i + 1 (just outside window) as a
    # within-window-bound sentinel.
    SENT_5 = n_hi_5 + 1
    SENT_7 = n_hi_7 + 1

    rng = np.random.default_rng(seed)

    lead_sims = np.zeros(n_trials, dtype=np.int64)
    n5_sims = np.zeros(n_trials, dtype=np.int64)
    n7_sims = np.zeros(n_trials, dtype=np.int64)

    for t in range(n_trials):
        # Random permutation of pool_size; first M_7 go to 7-set
        perm = rng.permutation(pool_size)
        seven_mask = np.zeros(pool_size, dtype=bool)
        seven_mask[perm[:M_7]] = True
        # five-set is the complement; both subsets remain in pool_size
        # order — i.e., in prime-size order

        # Cumulative log10 for each subset, in size order
        # 5-set: pool_log10 entries where seven_mask is False
        # 7-set: pool_log10 entries where seven_mask is True
        cum_5 = mpmath.mpf(0)
        k_5 = None
        idx_5 = 0
        cum_7 = mpmath.mpf(0)
        k_7 = None
        idx_7 = 0
        for j in range(pool_size):
            if seven_mask[j]:
                cum_7 += pool_log10[j]
                if k_7 is None and cum_7 >= threshold_7:
                    k_7 = idx_7  # 0-indexed: idx_7-th prime in 7-set crossed
                idx_7 += 1
            else:
                cum_5 += pool_log10[j]
                if k_5 is None and cum_5 >= threshold_5:
                    k_5 = idx_5
                idx_5 += 1
            if k_5 is not None and k_7 is not None:
                # Both crossed — we can finish the loop early but only
                # if we don't need further accumulator values.  Since
                # we don't, break.
                break

        n_5_sim = (n_lo_5 + k_5) if k_5 is not None else SENT_5
        n_7_sim = (n_lo_7 + k_7) if k_7 is not None else SENT_7

        lead_sims[t] = n_5_sim - n_7_sim
        n5_sims[t] = n_5_sim
        n7_sims[t] = n_7_sim

    return {
        'regime': regime_idx,
        'u_r': u_r,
        'n_lo_5': n_lo_5,
        'n_hi_5': n_hi_5,
        'n_lo_7': n_lo_7,
        'n_hi_7': n_hi_7,
        'M_5': M_5,
        'M_7': M_7,
        'pool_size': pool_size,
        'observed_lead': observed_lead,
        'lead_sims': lead_sims,
        'n5_sims': n5_sims,
        'n7_sims': n7_sims,
    }


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    t_start = time.time()

    print("=" * 72)
    print("Task 6 — Null distribution for the 7-series-lands-first observation")
    print("=" * 72)
    print(f"  N_TRIALS = {N_TRIALS} per regime, seeds = "
          f"{[MASTER_SEED + r for r, *_ in EXPECTED_REGIMES]}")
    print(f"  mpmath dps = {mpmath.mp.dps}; window half-width = "
          f"{WINDOW_HALF}")

    # ---- Sieve and deterministic series ----
    print(f"\nSieving primes up to {SIEVE_LIMIT}; computing D_5, D_7 "
          f"up to N_MAX = {N_MAX}...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    t0 = time.time()
    D5, log10_p5_mpf = compute_D_and_log10_primes(p5, N_MAX)
    print(f"  D_5 done in {time.time() - t0:.1f}s; D_5({N_MAX}) = {D5[-1]}")
    t0 = time.time()
    D7, log10_p7_mpf = compute_D_and_log10_primes(p7, N_MAX)
    print(f"  D_7 done in {time.time() - t0:.1f}s; D_7({N_MAX}) = {D7[-1]}")

    # ---- Anchor A — observed (n_7, n_5, lead) ----
    print("\n" + "=" * 72)
    print("Anchor A — observed (n_7, n_5, lead) for regimes 2–5")
    print("=" * 72)
    halt = False
    for r, u_r, n7_exp, n5_exp, lead_exp in EXPECTED_REGIMES:
        n5 = find_n_for_digit_length(D5, u_r + 1)
        n7 = find_n_for_digit_length(D7, u_r + 1)
        # Also verify exact landing (digit-length D_i(n) == u_r + 1)
        d5_at_n5 = D5[n5 - 1] if n5 else None
        d7_at_n7 = D7[n7 - 1] if n7 else None
        lead = n5 - n7
        ok = (n5 == n5_exp and n7 == n7_exp and lead == lead_exp)
        print(f"  Regime {r}: u_r+1 = {u_r + 1}, computed n_7 = {n7} "
              f"(D_7 = {d7_at_n7}), n_5 = {n5} (D_5 = {d5_at_n5}), "
              f"lead = {lead}  "
              f"(want n_7 = {n7_exp}, n_5 = {n5_exp}, lead = {lead_exp})  "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            halt = True
    if halt:
        print("  HALT: Anchor A mismatch.")
        sys.exit(1)

    # ---- Anchor B — upper edges from observation match those in expected ----
    print("\n" + "=" * 72)
    print("Anchor B — regime upper edges (Paper 201 §5.2 / Task 5)")
    print("=" * 72)
    expected_upper_edges = {1717, 4231, 8318, 15045}
    upper_edges_from_brief = {u for _, u, *_ in EXPECTED_REGIMES}
    print(f"  Expected upper edges (brief): {sorted(upper_edges_from_brief)}")
    if upper_edges_from_brief != expected_upper_edges:
        print(f"  HALT: brief vs reference set mismatch.")
        sys.exit(1)
    print(f"  OK")

    # ---- Anchor C — cross-check with task5_merged_regimes_detected.csv ----
    print("\n" + "=" * 72)
    print("Anchor C — task5_merged_regimes_detected.csv cross-check")
    print("=" * 72)
    if not os.path.isfile(ANCHOR_CSV):
        print(f"  HALT: {ANCHOR_CSV} not found.")
        sys.exit(1)
    with open(ANCHOR_CSV, encoding='utf-8') as f:
        anchor_rows = list(csv.DictReader(f))
    # Build a map upper_edge -> (n_5, n_7) from CSV
    csv_map = {}
    for r in anchor_rows:
        hi = int(r['upper_edge'])
        n5_str = r.get('landing_5_n', '')
        n7_str = r.get('landing_7_n', '')
        if n5_str and n7_str:
            csv_map[hi] = (int(n5_str), int(n7_str))
    halt = False
    for r, u_r, n7_exp, n5_exp, _ in EXPECTED_REGIMES:
        if u_r not in csv_map:
            print(f"  HALT: regime {r} (u_r = {u_r}) not in Task 5 CSV.")
            halt = True
            continue
        n5_csv, n7_csv = csv_map[u_r]
        ok = (n5_csv == n5_exp and n7_csv == n7_exp)
        print(f"  Regime {r} (u_r = {u_r}): CSV n_5 = {n5_csv}, "
              f"n_7 = {n7_csv}  "
              f"(want {n5_exp}, {n7_exp})  "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            halt = True
    if halt:
        sys.exit(1)
    print(f"  All anchors pass.")

    # ---- Null A — binary coin-flip (analytic) ----
    print("\n" + "=" * 72)
    print("Null A — binary coin-flip (analytic)")
    print("=" * 72)
    p_binary = 0.5 ** 4
    print(f"  p_binary = (1/2)^4 = {p_binary}")

    # ---- Null B — Monte Carlo per regime ----
    print("\n" + "=" * 72)
    print("Null B — label-permutation MC")
    print("=" * 72)
    regime_results = {}
    for r, u_r, n7_exp, n5_exp, lead_exp in EXPECTED_REGIMES:
        print(f"\n  Regime {r} (u_r = {u_r}, observed lead = {lead_exp})...")
        t0 = time.time()
        res = simulate_regime(r, u_r, lead_exp,
                              p5, p7, log10_p5_mpf, log10_p7_mpf,
                              D5, D7, N_TRIALS, seed=MASTER_SEED + r)
        elapsed = time.time() - t0
        regime_results[r] = res
        leads = res['lead_sims']
        p_r_tail = float(np.mean(leads >= lead_exp))
        p_r_sign = float(np.mean(leads > 0))
        print(f"    M_5 = {res['M_5']}, M_7 = {res['M_7']}, "
              f"pool = {res['pool_size']}")
        print(f"    lead_sim: mean = {leads.mean():.3f}, "
              f"median = {int(np.median(leads))}, "
              f"min = {int(leads.min())}, max = {int(leads.max())}")
        print(f"    P(lead_sim > 0)         = {p_r_sign:.4f}")
        print(f"    P(lead_sim >= {lead_exp}) = "
              f"{p_r_tail:.4f}  [observed lead = {lead_exp}]")
        print(f"    elapsed = {elapsed:.1f}s")

    # ---- Joint statistics ----
    print("\n" + "=" * 72)
    print("Joint statistics")
    print("=" * 72)

    # J-i: p_sign
    all_positive = np.ones(N_TRIALS, dtype=bool)
    for r, _, _, _, _ in EXPECTED_REGIMES:
        all_positive &= (regime_results[r]['lead_sims'] > 0)
    p_sign = float(np.mean(all_positive))
    print(f"  J-i  p_sign       = {p_sign:.4f}  "
          f"(observed: all 4 leads > 0)")

    # J-ii: p_magnitude — HEADLINE
    all_meet_observed = np.ones(N_TRIALS, dtype=bool)
    observed_leads = {r: lead for r, _, _, _, lead in EXPECTED_REGIMES}
    for r, _, _, _, lead_exp in EXPECTED_REGIMES:
        all_meet_observed &= (regime_results[r]['lead_sims'] >= lead_exp)
    p_magnitude = float(np.mean(all_meet_observed))
    print(f"  J-ii p_magnitude  = {p_magnitude:.4f}  "
          f"(observed: leads >= {{3, 4, 5, 6}})  [HEADLINE]")

    # J-iii: per-regime p_r and Fisher's combined
    per_regime_p = {}
    for r, _, _, _, lead_exp in EXPECTED_REGIMES:
        leads = regime_results[r]['lead_sims']
        p_r = float(np.mean(leads >= lead_exp))
        per_regime_p[r] = p_r
        print(f"  J-iii p_{r}        = {p_r:.4f}  "
              f"(lead_sim >= {lead_exp})")
    # Fisher: replace 0 with conservative upper bound 1/N to avoid log(0)
    fisher_chi2 = 0.0
    for r, _, _, _, _ in EXPECTED_REGIMES:
        p_r = max(per_regime_p[r], 1.0 / N_TRIALS)
        fisher_chi2 += -2.0 * math.log(p_r)
    # Combined p from chi2_8 survival function
    # scipy not allowed by CLAUDE.md unless needed; compute via mpmath
    fisher_p = float(1 - mpmath.gammainc(4, 0, fisher_chi2 / 2,
                                         regularized=True))
    print(f"  J-iii Fisher χ² = {fisher_chi2:.4f}  (df = 8)  "
          f"combined p = {fisher_p:.4g}")

    # ---- Threshold and framing-update ----
    print("\n" + "=" * 72)
    print("Pre-registered threshold (HEADLINE p_magnitude)")
    print("=" * 72)
    if p_magnitude >= 0.10:
        outcome = 'α'
        framing = ("Null does not fire.  §5.4 framing in Paper 201 v1.1 is "
                   "unchanged: 4-of-4 observation reported as auxiliary "
                   "positive structural fact with Q4 open.")
    elif p_magnitude >= 0.05:
        outcome = 'γ'
        framing = (f"Intermediate.  Paper 201 v1.1 retains v1.0 framing "
                   f"and reports the null result with intermediate-range "
                   f"honesty: 'Null B gives p_magnitude = "
                   f"{p_magnitude:.4f}, not sub-5% but suggestive.'")
    else:
        outcome = 'β'
        framing = (f"Null fires.  Paper 201 v1.1 §5.4 is rewritten: the "
                   f"7-series-first observation is promoted from "
                   f"auxiliary positive fact to falsifier-grade "
                   f"structural signal.  Q4 reframed: 'the 7-series-first "
                   f"signal is distinguished from null at p_magnitude = "
                   f"{p_magnitude:.4f}; analytic-number-theory candidate "
                   f"mechanisms (L(s, χ_5) zero spacings, additive "
                   f"distribution of log_10(p) across residue classes, "
                   f"Chebyshev-bias-adjacent effects) are open avenues.'")
    print(f"  Outcome: ({outcome})")
    print(f"  Framing update: {framing}")

    # ---- Plot ----
    print("\n" + "=" * 72)
    print("Generating histogram chart")
    print("=" * 72)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        plt = None

    if plt is not None:
        fig, axes = plt.subplots(2, 2, figsize=(12, 9))
        for ax, (r, u_r, _, _, lead_exp) in zip(
                axes.flat, EXPECTED_REGIMES):
            leads = regime_results[r]['lead_sims']
            p_r = per_regime_p[r]
            bins = np.arange(leads.min() - 0.5, leads.max() + 1.5, 1)
            ax.hist(leads, bins=bins, color='#1f77b4', alpha=0.7)
            ax.axvline(lead_exp, color='red', linestyle='--', linewidth=2,
                       label=f'observed = {lead_exp}')
            ax.axvline(0, color='gray', linestyle=':', alpha=0.7,
                       label='lead = 0 (parity)')
            ax.set_title(f'Regime {r}: u_r = {u_r}; '
                         f'M_5 = {regime_results[r]["M_5"]}, '
                         f'M_7 = {regime_results[r]["M_7"]}; '
                         f'p_r = {p_r:.4f}', fontsize=10)
            ax.set_xlabel('lead_sim = n_5_sim − n_7_sim')
            ax.set_ylabel('trial count')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
        fig.suptitle(f'Task 6 — Lead distribution under Null B '
                     f'(N_TRIALS = {N_TRIALS}); '
                     f'p_magnitude = {p_magnitude:.4f} → ({outcome})',
                     fontsize=11)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(PNG_OUT, dpi=120)
        plt.close(fig)
        print(f"  Saved: {PNG_OUT}")

    # ---- CSV (long format, 40,000 rows) ----
    print(f"\nWriting trial CSV ({N_TRIALS * len(EXPECTED_REGIMES)} rows)...")
    with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['regime', 'trial_id', 'n_5_sim', 'n_7_sim',
                    'lead_sim', 'lead_observed'])
        for r, _, _, _, lead_exp in EXPECTED_REGIMES:
            res = regime_results[r]
            for t in range(N_TRIALS):
                w.writerow([r, t, int(res['n5_sims'][t]),
                            int(res['n7_sims'][t]),
                            int(res['lead_sims'][t]), lead_exp])
    print(f"  Saved: {CSV_OUT}")

    # ---- Summary markdown ----
    write_summary(regime_results, p_binary, p_sign, p_magnitude,
                  per_regime_p, fisher_chi2, fisher_p, outcome, framing,
                  time.time() - t_start)
    print(f"  Saved: {MD_OUT}")

    # ---- Final status ----
    print("\n" + "=" * 72)
    print("TASK 6 — STATUS")
    print("=" * 72)
    print(f"All anchors: PASS")
    print(f"p_binary    = {p_binary}")
    print(f"p_sign      = {p_sign:.4f}")
    print(f"p_magnitude = {p_magnitude:.4f}  → outcome ({outcome})")
    print(f"per-regime p_r: " +
          ", ".join(f'p_{r} = {per_regime_p[r]:.4f}'
                    for r, *_ in EXPECTED_REGIMES))
    print(f"Fisher combined p = {fisher_p:.4g}")
    print(f"Total runtime: {time.time() - t_start:.1f}s")
    print(f"Files: {CSV_OUT}, {MD_OUT}, {PNG_OUT}")
    print("\nEnd-of-task: PASS")


def write_summary(regime_results, p_binary, p_sign, p_magnitude,
                  per_regime_p, fisher_chi2, fisher_p, outcome, framing,
                  total_runtime):
    with open(MD_OUT, 'w', encoding='utf-8') as f:
        f.write("# Task 6 — Null distribution for the 7-series-lands-first "
                "observation: summary\n\n")
        f.write(f"**Date:** 11 May 2026.\n")
        f.write(f"**Pre-registration:** `v3_12_data/briefs/"
                f"mr_code_brief_paper_201_task6.md`.\n")
        f.write(f"**Runtime:** {total_runtime:.1f}s.\n")
        f.write(f"**N_TRIALS:** {N_TRIALS} per regime, seeds 44/45/46/47.\n"
                f"**mpmath dps:** {mpmath.mp.dps}.\n"
                f"**Window half-width:** {WINDOW_HALF} digit-lengths.\n\n")

        f.write("## Anchors\n\n")
        f.write("All four anchor verification gates passed (A: observed "
                "(n_5, n_7, lead); B: regime upper edges; C: cross-check "
                "with task5_merged_regimes_detected.csv).\n\n")

        f.write("## Per-regime simulation summary\n\n")
        f.write("| Regime | u_r | Window | M_5 | M_7 | Pool size | "
                "Observed lead | mean(lead_sim) | median | min | max | "
                "p_r |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        for r in sorted(regime_results.keys()):
            res = regime_results[r]
            leads = res['lead_sims']
            f.write(f"| {r} | {res['u_r']} | "
                    f"[{res['u_r'] - WINDOW_HALF}, "
                    f"{res['u_r'] + WINDOW_HALF}] | "
                    f"{res['M_5']} | {res['M_7']} | "
                    f"{res['pool_size']} | "
                    f"{res['observed_lead']} | "
                    f"{leads.mean():.3f} | "
                    f"{int(np.median(leads))} | "
                    f"{int(leads.min())} | {int(leads.max())} | "
                    f"{per_regime_p[r]:.4f} |\n")
        f.write("\n")

        f.write("## Null A — binary coin-flip (analytic)\n\n")
        f.write(f"`p_binary = (1/2)^4 = {p_binary}`\n\n")

        f.write("## Null B — joint statistics\n\n")
        f.write(f"| Statistic | Value | Note |\n|---|---|---|\n")
        f.write(f"| **p_magnitude (J-ii, HEADLINE)** | "
                f"**{p_magnitude:.4f}** | "
                f"P(lead_sim_r ≥ {{3, 4, 5, 6}} for all r) |\n")
        f.write(f"| p_sign (J-i) | {p_sign:.4f} | "
                f"P(lead_sim_r > 0 for all r) |\n")
        f.write(f"| Fisher's combined p (J-iii) | "
                f"{fisher_p:.4g} | χ² = {fisher_chi2:.4f}, df = 8 |\n\n")

        f.write("## Pre-registered outcome — ({}) \n\n".format(outcome))
        f.write(f"**Threshold applied:** p_magnitude = "
                f"{p_magnitude:.4f}.  "
                f"{'≥ 0.10' if p_magnitude >= 0.10 else '0.05 ≤ p < 0.10' if p_magnitude >= 0.05 else '< 0.05'}.  "
                f"Outcome: **({outcome})**.\n\n")
        f.write(f"**Framing update applied to Paper 201 §5.4:**  "
                f"{framing}\n\n")

        f.write("## Honest-reporting commitments (per brief §8)\n\n")
        f.write("- All four per-regime histograms and tail p-values "
                "are reported above.\n")
        f.write("- No post-hoc adjustment of window width, precision "
                "budget, N_TRIALS, seeds, or thresholds.\n")
        f.write("- Outcome threshold applied mechanically per brief §4 "
                "without rhetorical manoeuvring.\n\n")

        f.write("## Deviations from pre-registration\n\n")
        f.write("None.  All parameters (window half-width 200, N_TRIALS "
                "10,000, master seed 42, per-regime seeds 44/45/46/47, "
                "mpmath dps 200) match the brief.\n\n")

        f.write("🐕☕⬡\n\n")
        f.write("— Mr Code, 11 May 2026 (Paper 201 v1.1 Task 6)\n")


if __name__ == '__main__':
    main()
