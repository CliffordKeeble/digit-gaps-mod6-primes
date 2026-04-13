#!/usr/bin/env python3
"""
Phase Transition Null Test (Section 4.2)
=========================================

The paper observes that digit gaps transition from STAGGERED (gaps at different
digits in each series) to COINCIDENT (gaps at same digits) as cumulative products
grow. Specifically:
  - At 10^61 scale: staggered (5-series gaps at 60-61, 7-series at 62-63)
  - At 10^80 scale: coincident (both gap at 80-81)

This test asks: is the staggered-to-coincident transition prime-specific, or does
it also occur in random pseudo-prime sequences with PNT density?

METHOD:
  For each sequence (real primes and N null trials), we measure "synchronisation"
  at each scale by computing the fraction of gaps that are coincident (present in
  both series) within sliding windows. We define:

    sync_fraction(d, w) = |gaps_in_window that are coincident| / |gaps_in_window|

  where the window is [d, d+w). A PHASE TRANSITION is detected when sync_fraction
  crosses a threshold (e.g., 0.9) and stays above it for a sustained region.

  We measure:
  1. The digit at which sync_fraction first crosses 0.9 for 10 consecutive windows
  2. The overall sync_fraction trajectory as a function of scale
  3. Sensitivity to window size and threshold

SEED: null trials use seed = trial * 137 + 42 (matching full_null_model.py).
"""
import math, random, time, sys, csv, os
from collections import Counter
from bisect import bisect_left

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
N_TRIALS = 10
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def sieve(limit):
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def compute_digit_sets(logs):
    """Return set of digit-lengths reached by cumulative product."""
    s = 0.0
    d_set = set()
    for lg in logs:
        s += lg
        d_set.add(int(s) + 1)
    return d_set


def compute_gap_arrays(logs1, logs2):
    """Return gap bytearrays and max_d for two log sequences."""
    d1 = compute_digit_sets(logs1)
    d2 = compute_digit_sets(logs2)
    max_d = min(max(d1), max(d2))
    is_gap1 = bytearray(b'\x01') * (max_d + 1)
    is_gap2 = bytearray(b'\x01') * (max_d + 1)
    for d in d1:
        if d <= max_d: is_gap1[d] = 0
    for d in d2:
        if d <= max_d: is_gap2[d] = 0
    return is_gap1, is_gap2, max_d


def measure_sync_trajectory(is_gap1, is_gap2, max_d, window=200, step=100):
    """
    Compute sync_fraction at each position: fraction of gaps in window
    that are coincident (both series gap) vs total gaps (either series gaps).

    Returns list of (position, sync_fraction, n_gaps_in_window).
    """
    trajectory = []
    for d in range(1, max_d - window + 1, step):
        both = 0
        either = 0
        for i in range(d, d + window):
            g1 = is_gap1[i]
            g2 = is_gap2[i]
            if g1 and g2:
                both += 1
                either += 1
            elif g1 or g2:
                either += 1
        frac = both / either if either > 0 else 0
        trajectory.append((d, frac, either))
    return trajectory


def find_transition_point(trajectory, threshold=0.9, sustain=10):
    """
    Find the first position where sync_fraction >= threshold for
    `sustain` consecutive windows.
    Returns the digit position, or None if never sustained.
    """
    count = 0
    for d, frac, _ in trajectory:
        if frac >= threshold:
            count += 1
            if count >= sustain:
                return d - (sustain - 1) * 100  # approximate start
        else:
            count = 0
    return None


def generate_pseudo_primes(limit, seed):
    rng = random.Random(seed)
    c1_logs, c2_logs = [], []
    for n in range(5, limit):
        if rng.random() < 1.0 / math.log(n):
            lg = math.log10(n)
            if rng.random() < 0.5:
                c1_logs.append(lg)
            else:
                c2_logs.append(lg)
    return c1_logs, c2_logs


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    T0 = time.time()

    print("=" * 72)
    print("PHASE TRANSITION NULL TEST (Section 4.2)")
    print("=" * 72)

    # --- Real primes ---
    print("\n[1] Sieving primes...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    p5_logs = [math.log10(p) for p in p5]
    p7_logs = [math.log10(p) for p in p7]
    n_use = min(len(p5_logs), len(p7_logs))
    print(f"  5-series: {len(p5):,}, 7-series: {len(p7):,}")

    print("\n[2] Computing gap arrays for real primes...")
    is_gap1, is_gap2, max_d = compute_gap_arrays(p5_logs[:n_use], p7_logs[:n_use])
    print(f"  Max digit: {max_d:,}")

    # --- Measure sync trajectory at multiple window sizes ---
    print("\n[3] Measuring synchronisation trajectory (real primes)...")
    windows = [100, 200, 500, 1000]
    real_transitions = {}
    thresholds = [0.8, 0.85, 0.9, 0.95]

    for w in windows:
        traj = measure_sync_trajectory(is_gap1, is_gap2, max_d, window=w, step=w//2)
        for thresh in thresholds:
            tp = find_transition_point(traj, threshold=thresh, sustain=10)
            real_transitions[(w, thresh)] = tp

        # Save trajectory for the default window
        if w == 200:
            real_traj = traj

    print("  Real prime transition points (digit where sync >= threshold sustained):")
    for thresh in thresholds:
        print(f"    threshold={thresh}:")
        for w in windows:
            tp = real_transitions[(w, thresh)]
            print(f"      window={w:5d}: {tp if tp else 'never'}")

    # --- Measure early-scale stagger ---
    print("\n[4] Early-scale gap stagger analysis...")
    # At small scales, count how many gaps are series-1-only, series-2-only, or both
    early_bands = [(1, 100), (1, 500), (1, 1000), (1, 5000), (1, 10000)]
    print("  Real primes -- gap classification by band:")
    print(f"  {'Band':<15} {'Only-1':>8} {'Only-2':>8} {'Both':>8} {'Stagger%':>10}")
    real_early = []
    for lo, hi in early_bands:
        only1 = only2 = both = 0
        for d in range(lo, min(hi + 1, max_d + 1)):
            g1 = is_gap1[d]
            g2 = is_gap2[d]
            if g1 and g2:
                both += 1
            elif g1:
                only1 += 1
            elif g2:
                only2 += 1
        total_gaps = only1 + only2 + both
        stagger_pct = 100.0 * (only1 + only2) / total_gaps if total_gaps > 0 else 0
        coincident_pct = 100.0 * both / total_gaps if total_gaps > 0 else 0
        real_early.append({'band': f"{lo}-{hi}", 'only1': only1, 'only2': only2,
                          'both': both, 'stagger_pct': stagger_pct})
        print(f"  {lo}-{hi:<10} {only1:>8} {only2:>8} {both:>8} {stagger_pct:>9.1f}%")

    # --- Null model ---
    print(f"\n[5] Running {N_TRIALS} null model trials...")
    null_transitions = {k: [] for k in real_transitions.keys()}
    null_early = {b['band']: [] for b in real_early}

    for trial in range(N_TRIALS):
        t1 = time.time()
        logs1, logs2 = generate_pseudo_primes(SIEVE_LIMIT, seed=trial * 137 + 42)
        n_null = min(len(logs1), len(logs2), n_use)
        ng1, ng2, nmax = compute_gap_arrays(logs1[:n_null], logs2[:n_null])

        for w in windows:
            traj = measure_sync_trajectory(ng1, ng2, nmax, window=w, step=w//2)
            for thresh in thresholds:
                tp = find_transition_point(traj, threshold=thresh, sustain=10)
                null_transitions[(w, thresh)].append(tp)

        # Early-scale analysis
        for lo, hi in early_bands:
            only1 = only2 = both = 0
            for d in range(lo, min(hi + 1, nmax + 1)):
                g1 = ng1[d]
                g2 = ng2[d]
                if g1 and g2:
                    both += 1
                elif g1:
                    only1 += 1
                elif g2:
                    only2 += 1
            total_gaps = only1 + only2 + both
            stagger_pct = 100.0 * (only1 + only2) / total_gaps if total_gaps > 0 else 0
            null_early[f"{lo}-{hi}"].append(stagger_pct)

        print(f"  Trial {trial:2d}: [{time.time()-t1:.1f}s]")

    # --- Comparison ---
    print(f"\n{'='*72}")
    print("TRANSITION POINT COMPARISON")
    print(f"{'='*72}")
    print(f"  {'Window':<8} {'Thresh':<8} {'Real':>10} {'Null mean':>10} {'Null std':>10} {'z':>8}")

    for w in windows:
        for thresh in thresholds:
            rp = real_transitions[(w, thresh)]
            nps = [x for x in null_transitions[(w, thresh)] if x is not None]
            if rp is None:
                print(f"  {w:<8} {thresh:<8} {'never':>10} ", end="")
            else:
                print(f"  {w:<8} {thresh:<8} {rp:>10,} ", end="")
            if len(nps) >= 2:
                nm = sum(nps) / len(nps)
                ns = math.sqrt(sum((x - nm)**2 for x in nps) / (len(nps) - 1))
                n_found = len(nps)
                print(f"{nm:>10,.0f} {ns:>10,.0f}", end="")
                if rp is not None and ns > 0:
                    z = (rp - nm) / ns
                    print(f" {z:>8.2f}", end="")
                else:
                    print(f" {'—':>8}", end="")
                print(f"  ({n_found}/{N_TRIALS} found)")
            else:
                n_found = len(nps)
                print(f"  ({n_found}/{N_TRIALS} found transition)")

    # --- Early-scale stagger comparison ---
    print(f"\n{'='*72}")
    print("EARLY-SCALE STAGGER COMPARISON")
    print(f"{'='*72}")
    print(f"  {'Band':<15} {'Real stagger%':>14} {'Null mean%':>12} {'Null std%':>10} {'z':>8}")

    for b in real_early:
        band = b['band']
        rval = b['stagger_pct']
        nvals = null_early[band]
        if len(nvals) >= 2:
            nm = sum(nvals) / len(nvals)
            ns = math.sqrt(sum((x - nm)**2 for x in nvals) / (len(nvals) - 1))
            z = (rval - nm) / ns if ns > 0 else 0
            print(f"  {band:<15} {rval:>13.1f}% {nm:>11.1f}% {ns:>9.1f}% {z:>8.2f}")
        else:
            print(f"  {band:<15} {rval:>13.1f}%  (insufficient null data)")

    # --- Save CSV ---
    csv_path = os.path.join(RESULTS_DIR, 'phase_transition_results.csv')
    with open(csv_path, 'w', newline='') as f:
        w_csv = csv.writer(f)
        w_csv.writerow(['window', 'threshold', 'real_transition', 'null_mean', 'null_std',
                        'null_found', 'z_score'])
        for w in windows:
            for thresh in thresholds:
                rp = real_transitions[(w, thresh)]
                nps = [x for x in null_transitions[(w, thresh)] if x is not None]
                nm = sum(nps) / len(nps) if nps else ''
                ns = (math.sqrt(sum((x - nm)**2 for x in nps) / (len(nps) - 1))
                      if len(nps) >= 2 else '')
                z = (rp - nm) / ns if (rp is not None and nm != '' and ns != '' and ns > 0) else ''
                w_csv.writerow([w, thresh, rp if rp else '', nm, ns, len(nps), z])
    print(f"\n  Results saved to {csv_path}")

    # --- Sync trajectory comparison at scale ---
    print(f"\n{'='*72}")
    print("SYNC FRACTION AT KEY SCALES")
    print(f"{'='*72}")
    key_digits = [50, 100, 500, 1000, 5000, 10000, 50000, 100000]
    print(f"  {'Digit':<10} {'Real sync%':>12}")
    for d, frac, n_gaps in real_traj:
        if d in key_digits or any(abs(d - kd) < 100 for kd in key_digits):
            if d in key_digits:
                print(f"  {d:<10} {frac*100:>11.1f}%  (n_gaps={n_gaps})")

    print(f"\nTotal runtime: {time.time()-T0:.1f}s")


if __name__ == '__main__':
    main()
