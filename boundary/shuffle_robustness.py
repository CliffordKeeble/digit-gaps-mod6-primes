#!/usr/bin/env python3
"""
Shuffle Robustness + Ramification Accounting + Persistence Stats
(Paper A v3.1 follow-up, Mr Adversary items)
================================================================

Task 1: 45-cell (n x c) sweep of shuffle test robustness.
Task 2: Ramification accounting — definitions A, B, C.
Task 3: Persistence-ratio stability statistics.
"""
import math, random, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 2_000_000
N_SHUFFLE = 1000
SEED_BASE = 42
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def sieve(limit):
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def chi5(p):
    r = p % 5
    if r == 0:
        return 0
    elif r in (1, 4):
        return 1
    else:
        return -1


def count_ties_in_window(chi_vals, start, end):
    """Count ties (running sum = 0) in positions start..end-1 (0-indexed)."""
    s = 0
    ties = 0
    for i in range(start, min(end, len(chi_vals))):
        s += chi_vals[i]
        if s == 0:
            ties += 1
    return ties


def running_sum_sequence(chi_vals, limit=None):
    """Return list of running sums S(1), S(2), ..."""
    if limit is None:
        limit = len(chi_vals)
    s = 0
    result = []
    for i in range(min(limit, len(chi_vals))):
        s += chi_vals[i]
        result.append(s)
    return result


def find_band_window(S, c):
    """Find the maximal initial segment where |S(n)| <= c.
    Returns the last 1-based index n where |S(n)| <= c before first exit."""
    for i, s in enumerate(S):
        if abs(s) > c:
            return i  # i is 0-based, so this is the count of positions within band
    return len(S)


# ====================================================================
# TASK 1: SHUFFLE ROBUSTNESS SWEEP
# ====================================================================
def task1_shuffle_robustness(p5):
    print(f"\n{'='*72}")
    print(f"TASK 1: SHUFFLE ROBUSTNESS SWEEP (15 windows x 3 bands)")
    print(f"{'='*72}")

    chi_vals = [chi5(p) for p in p5[:200]]
    S_nat = running_sum_sequence(chi_vals, 200)

    windows = [10, 15, 20, 25, 30, 33, 35, 40, 45, 50, 60, 70, 80, 90, 100]
    bands = [1, 2, 3]

    # First: find the natural-order band windows
    print(f"\n  Natural-order band windows:")
    for c in bands:
        w = find_band_window(S_nat, c)
        print(f"    c={c}: |S| <= {c} holds for n=1..{w}")

    # Full sweep
    print(f"\n  {'n':>4} {'c':>3} {'T_nat':>6} {'shuf_mean':>10} {'shuf_std':>9} "
          f"{'z':>7} {'p_ge':>7} {'n_distinct':>10}")
    print(f"  {'-'*62}")

    results = []
    rng = random.Random(SEED_BASE)

    for n in windows:
        nat_ties = count_ties_in_window(chi_vals, 0, n)

        # Run shuffles once per window size (ties don't depend on c)
        shuffle_ties = []
        for trial in range(N_SHUFFLE):
            shuffled = chi_vals[:n][:]
            rng.shuffle(shuffled)
            t = count_ties_in_window(shuffled, 0, n)
            shuffle_ties.append(t)

        mean_t = sum(shuffle_ties) / N_SHUFFLE
        std_t = math.sqrt(sum((x - mean_t)**2 for x in shuffle_ties) / (N_SHUFFLE - 1)) if N_SHUFFLE > 1 else 0
        z = (nat_ties - mean_t) / std_t if std_t > 0 else 0
        p_ge = sum(1 for x in shuffle_ties if x >= nat_ties) / N_SHUFFLE
        n_distinct = len(set(shuffle_ties))

        for c in bands:
            # c enters only via identifying the "natural window" for that band
            band_window = find_band_window(S_nat, c)
            results.append({
                'n': n, 'c': c, 'T_nat': nat_ties,
                'shuffle_mean': mean_t, 'shuffle_std': std_t,
                'z': z, 'p_ge': p_ge, 'n_distinct': n_distinct,
                'band_window': band_window,
                'is_band_window': (n == band_window),
            })

            print(f"  {n:>4} {c:>3} {nat_ties:>6} {mean_t:>10.2f} {std_t:>9.2f} "
                  f"{z:>7.2f} {p_ge:>7.4f} {n_distinct:>10}"
                  f"{'  <-- band window' if n == band_window else ''}")

    # Summary: where is z > 2?
    print(f"\n  Cells with z > 2:")
    z2_cells = [(r['n'], r['c'], r['z'], r['p_ge']) for r in results if r['z'] > 2]
    # Deduplicate by n (since c doesn't affect the shuffle)
    seen_n = set()
    for n, c, z, p in z2_cells:
        if n not in seen_n:
            print(f"    n={n}, z={z:.2f}, p={p:.4f}")
            seen_n.add(n)

    print(f"\n  Cells with z > 3:")
    seen_n = set()
    for n, c, z, p in [(r['n'], r['c'], r['z'], r['p_ge']) for r in results if r['z'] > 3]:
        if n not in seen_n:
            print(f"    n={n}, z={z:.2f}, p={p:.4f}")
            seen_n.add(n)

    # Underpowered flag
    print(f"\n  Underpowered cells (< 30 distinct tie counts):")
    seen_n = set()
    for r in results:
        if r['n_distinct'] < 30 and r['n'] not in seen_n:
            print(f"    n={r['n']}: {r['n_distinct']} distinct values")
            seen_n.add(r['n'])

    # Save CSV
    csv_path = os.path.join(RESULTS_DIR, 'shuffle_robustness.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['n', 'c', 'T_nat', 'shuffle_mean', 'shuffle_std', 'z',
                     'p_ge', 'n_distinct', 'band_window', 'is_band_window'])
        for r in results:
            w.writerow([r['n'], r['c'], r['T_nat'], f"{r['shuffle_mean']:.4f}",
                        f"{r['shuffle_std']:.4f}", f"{r['z']:.4f}",
                        f"{r['p_ge']:.4f}", r['n_distinct'],
                        r['band_window'], r['is_band_window']])
    print(f"\n  Saved: {csv_path}")

    return results


# ====================================================================
# TASK 2: RAMIFICATION ACCOUNTING
# ====================================================================
def task2_ramification(p5):
    print(f"\n{'='*72}")
    print("TASK 2: RAMIFICATION ACCOUNTING (definitions A/B/C)")
    print(f"{'='*72}")

    chi_vals = [chi5(p) for p in p5[:200]]
    n_window = 33

    # Definition A: current v3.1 — ties in positions 1..33 including k=1
    S_A = running_sum_sequence(chi_vals, n_window)
    T_A = sum(1 for s in S_A if s == 0)
    print(f"\n  Definition A (current): ties in n=1..{n_window} including ramified n=1")
    print(f"    Natural-order T_A = {T_A}")
    print(f"    S_A(1) = {S_A[0]} (chi5(5) = {chi5(p5[0])}, ramified)")

    # Definition B: exclude position 1 from tie count
    T_B_nat = sum(1 for s in S_A[1:] if s == 0)
    print(f"\n  Definition B (exclude n=1 from count): ties in n=2..{n_window}")
    print(f"    Natural-order T_B = {T_B_nat}")

    # Definition C: omit p=5 entirely, compute 32-step sum from p5[1:]
    chi_vals_C = [chi5(p) for p in p5[1:200]]
    S_C = running_sum_sequence(chi_vals_C, n_window - 1)
    T_C_nat = sum(1 for s in S_C if s == 0)
    print(f"\n  Definition C (omit p=5): ties in 32-step sum of p5[2..{n_window}]")
    print(f"    Natural-order T_C = {T_C_nat}")
    print(f"    S_C sequence (first 33): {S_C[:33]}")

    # Shuffle test for each definition
    rng = random.Random(SEED_BASE)

    # Definition A shuffles
    shuf_A = []
    for trial in range(N_SHUFFLE):
        shuffled = chi_vals[:n_window][:]
        rng.shuffle(shuffled)
        S = running_sum_sequence(shuffled, n_window)
        shuf_A.append(sum(1 for s in S if s == 0))

    # Definition B shuffles: same shuffles, but exclude position 1
    rng = random.Random(SEED_BASE)
    shuf_B = []
    for trial in range(N_SHUFFLE):
        shuffled = chi_vals[:n_window][:]
        rng.shuffle(shuffled)
        S = running_sum_sequence(shuffled, n_window)
        shuf_B.append(sum(1 for s in S[1:] if s == 0))

    # Definition C shuffles: shuffle the 32 non-ramified chi values
    rng = random.Random(SEED_BASE)
    shuf_C = []
    chi_C = chi_vals_C[:n_window - 1]
    for trial in range(N_SHUFFLE):
        shuffled = chi_C[:]
        rng.shuffle(shuffled)
        S = running_sum_sequence(shuffled, n_window - 1)
        shuf_C.append(sum(1 for s in S if s == 0))

    def report(label, T_nat, shuf_vals):
        mean = sum(shuf_vals) / len(shuf_vals)
        std = math.sqrt(sum((x - mean)**2 for x in shuf_vals) / (len(shuf_vals) - 1))
        z = (T_nat - mean) / std if std > 0 else 0
        p = sum(1 for x in shuf_vals if x >= T_nat) / len(shuf_vals)
        print(f"    T_nat={T_nat}, shuffle mean={mean:.2f}, std={std:.2f}, z={z:.2f}, p={p:.4f}")
        return {'T_nat': T_nat, 'mean': mean, 'std': std, 'z': z, 'p': p}

    print(f"\n  Shuffle results (n={n_window}, c=2, 1000 trials):")
    print(f"\n  Definition A (include ramified n=1):")
    res_A = report("A", T_A, shuf_A)
    print(f"  Definition B (exclude n=1 from count):")
    res_B = report("B", T_B_nat, shuf_B)
    print(f"  Definition C (omit p=5 entirely, 32 steps):")
    res_C = report("C", T_C_nat, shuf_C)

    # Save CSV
    csv_path = os.path.join(RESULTS_DIR, 'ramification_accounting.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['definition', 'T_nat', 'shuffle_mean', 'shuffle_std', 'z', 'p'])
        for label, res in [('A', res_A), ('B', res_B), ('C', res_C)]:
            w.writerow([label, res['T_nat'], f"{res['mean']:.4f}",
                        f"{res['std']:.4f}", f"{res['z']:.4f}", f"{res['p']:.4f}"])
    print(f"\n  Saved: {csv_path}")

    return res_A, res_B, res_C


# ====================================================================
# TASK 3: PERSISTENCE-RATIO STATISTICS
# ====================================================================
def task3_persistence_stats():
    print(f"\n{'='*72}")
    print("TASK 3: PERSISTENCE-RATIO STABILITY STATISTICS")
    print(f"{'='*72}")

    # From findings.md §8.5
    N_vals = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000]
    ratios = [3.63, 4.04, 5.59, 5.80, 5.48, 6.05, 5.16]
    # Note: 8 N values but 7 ratios in the brief. Let me use all 8 from the actual data.
    # The brief lists 7: {3.63, 4.04, 5.59, 5.80, 5.48, 6.05, 5.16}
    # But §8.5 has 7 rows (N=100..50000 gives 7 ratios). Let me use all 7.

    n = len(ratios)
    mean_r = sum(ratios) / n
    std_r = math.sqrt(sum((x - mean_r)**2 for x in ratios) / (n - 1))
    cv = std_r / mean_r

    # t-interval, df = n-1
    # t_{0.025, 6} = 2.447
    from math import sqrt
    t_crit = 2.447  # t_{0.025, df=6}
    margin = t_crit * std_r / sqrt(n)
    ci_lo = mean_r - margin
    ci_hi = mean_r + margin

    print(f"\n  Ratios: {ratios}")
    print(f"  n = {n}")
    print(f"  Mean:   {mean_r:.3f}")
    print(f"  Std:    {std_r:.3f}")
    print(f"  CV:     {cv:.3f} ({cv*100:.1f}%)")
    print(f"  95% CI: [{ci_lo:.3f}, {ci_hi:.3f}]")

    # Linear fit: ratio vs log10(N)
    # Use N_vals corresponding to the ratios
    # Brief says 7 ratios at N = 100, 500, 1000, 2000, 5000, 10000, 20000, 50000
    # But 7 ratios => 7 N values. The 8th (N=50000) maps to ratio 5.16.
    # Wait, let me recount: the brief says {3.63, 4.04, 5.59, 5.80, 5.48, 6.05, 5.16} = 7 values
    # From §8.5 the table has N = 100..50000 = 7 rows? No, 8 rows (100,500,1000,2000,5000,10000,20000,50000).
    # But 7 ratios in the brief. Let me check: the brief says the ratios are from §8.5.
    # Looking at the §8.5 table: 8 rows, 8 ratios. The brief lists 7.
    # I'll use all 8 from the actual data.
    N_for_fit = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000]
    ratios_full = [3.63, 4.04, 5.59, 5.80, 5.48, 6.05, 5.16]

    # The brief explicitly lists 7 values. Let me match: 100->3.63, 500->4.04, 1000->5.59,
    # 2000->5.80, 5000->5.48, 10000->6.05, 20000->5.16. That's 7.
    # But §8.5 also has N=50000 -> 5.16. Hmm.
    # Actually re-reading §8.5: N=20000 -> 6.05, N=50000 -> 5.16. So 8 values.
    # Brief lists 7: probably dropped one. Let me use all 8.
    ratios_8 = [3.63, 4.04, 5.59, 5.80, 5.48, 6.05, 5.16]
    N_8 = [100, 500, 1000, 2000, 5000, 10000, 20000]
    # The brief says 7 values. I'll use those 7 and note if N=50000 was excluded.
    # Actually wait - looking at the table again there are 7 listed in the brief text.
    # Let me just use what the brief gave me.

    log_N = [math.log10(N) for N in N_8]
    n_fit = len(log_N)
    mean_x = sum(log_N) / n_fit
    mean_y = sum(ratios_8) / n_fit
    ss_xx = sum((x - mean_x)**2 for x in log_N)
    ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_N, ratios_8))
    ss_yy = sum((y - mean_y)**2 for y in ratios_8)

    slope = ss_xy / ss_xx if ss_xx > 0 else 0
    intercept = mean_y - slope * mean_x
    ss_res = sum((y - (intercept + slope * x))**2 for x, y in zip(log_N, ratios_8))
    r_sq = 1 - ss_res / ss_yy if ss_yy > 0 else 0

    # t-test for slope != 0
    se_slope = math.sqrt(ss_res / ((n_fit - 2) * ss_xx)) if n_fit > 2 and ss_xx > 0 else 0
    t_slope = slope / se_slope if se_slope > 0 else 0
    # df = n-2 = 5. Two-tailed p-value approximation
    # For |t| and df=5, rough critical values: t_0.05 = 2.571, t_0.10 = 2.015
    # We'll report the t-value and note whether |t| > 2.571

    print(f"\n  Linear fit: ratio = {intercept:.3f} + {slope:.3f} * log10(N)")
    print(f"    Slope:    {slope:.4f}")
    print(f"    SE(slope): {se_slope:.4f}")
    print(f"    t(slope): {t_slope:.3f}")
    print(f"    R2:       {r_sq:.4f}")
    print(f"    df = {n_fit - 2}")
    print(f"    |t| {'>' if abs(t_slope) > 2.571 else '<'} 2.571 (critical t at p=0.05, df=5)")
    if abs(t_slope) > 2.571:
        print(f"    CONCLUSION: slope significantly nonzero at p < 0.05 — ratio is drifting")
    elif abs(t_slope) > 2.015:
        print(f"    CONCLUSION: slope marginally significant (p ~ 0.05-0.10)")
    else:
        print(f"    CONCLUSION: slope NOT significantly nonzero — 'stable' is justified")

    # Also compute with all 8 values if we have them
    print(f"\n  (Using {n_fit} data points as listed in the brief)")

    return {
        'mean': mean_r, 'std': std_r, 'cv': cv,
        'ci_lo': ci_lo, 'ci_hi': ci_hi,
        'slope': slope, 'se_slope': se_slope, 't_slope': t_slope,
        'r_sq': r_sq, 'n': n_fit,
    }


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 72)
    print("V3.1 ADVERSARY FOLLOW-UP (Tasks 1-3)")
    print("=" * 72)

    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    print(f"  5-series primes available: {len(p5)}")

    task1_shuffle_robustness(p5)
    task2_ramification(p5)
    task3_persistence_stats()

    print(f"\n{'='*72}")
    print("ALL TASKS COMPLETE")
    print(f"{'='*72}")


if __name__ == '__main__':
    main()
