#!/usr/bin/env python3
"""
Perturbation Tests (Paper A, Tasks 3-5)
========================================

Task 3: Shuffle test — is the 5-series tight-oscillation regime about
         the natural ordering by prime size, or the set of primes?
Task 4: Comparable moduli — is the opposite-direction Chebyshev bias
         specific to mod-6 filtering, or general?
Task 5: Higher-scale tie density — does 5-series tie density drop like
         1/sqrt(n) or stabilise?
"""
import math, random, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 2_000_000
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
SEED = 42


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


def count_ties(values, start=0, end=None):
    """Count positions where running sum = 0."""
    if end is None:
        end = len(values)
    s = 0
    ties = 0
    for i in range(start, min(end, len(values))):
        s += values[i]
        if s == 0:
            ties += 1
    return ties


def running_sum_ties(values, limit=None):
    """Return list of 1-based indices where running sum = 0."""
    if limit is None:
        limit = len(values)
    s = 0
    ties = []
    for i in range(min(limit, len(values))):
        s += values[i]
        if s == 0:
            ties.append(i + 1)
    return ties


# ====================================================================
# TASK 3: SHUFFLE TEST
# ====================================================================
def shuffle_test(primes, n_trials=1000):
    print(f"\n{'='*72}")
    print(f"TASK 3: SHUFFLE TEST ({n_trials} trials)")
    print(f"{'='*72}")

    # Natural order chi5 values for first 200 5-series primes
    chi_vals = [chi5(p) for p in primes[:200]]

    # Natural order: ties in first 33 and next 33
    nat_ties_33 = count_ties(chi_vals, 0, 33)
    nat_ties_34_66 = count_ties(chi_vals[33:], 0, 33)
    print(f"\n  Natural order: {nat_ties_33} ties in n=1..33, {nat_ties_34_66} ties in n=34..66")

    rng = random.Random(SEED)
    shuffle_ties_33 = []
    shuffle_ties_34_66 = []

    for trial in range(n_trials):
        shuffled = chi_vals[:]
        rng.shuffle(shuffled)
        t33 = count_ties(shuffled, 0, 33)
        t34_66 = count_ties(shuffled[33:], 0, 33)
        shuffle_ties_33.append(t33)
        shuffle_ties_34_66.append(t34_66)

    mean_33 = sum(shuffle_ties_33) / n_trials
    std_33 = math.sqrt(sum((x - mean_33)**2 for x in shuffle_ties_33) / (n_trials - 1))
    mean_34_66 = sum(shuffle_ties_34_66) / n_trials
    std_34_66 = math.sqrt(sum((x - mean_34_66)**2 for x in shuffle_ties_34_66) / (n_trials - 1))

    z_33 = (nat_ties_33 - mean_33) / std_33 if std_33 > 0 else 0
    z_34_66 = (nat_ties_34_66 - mean_34_66) / std_34_66 if std_34_66 > 0 else 0

    p_ge_14 = sum(1 for x in shuffle_ties_33 if x >= nat_ties_33) / n_trials

    print(f"\n  Shuffle results (n=1..33):")
    print(f"    Mean ties: {mean_33:.2f}")
    print(f"    Std ties:  {std_33:.2f}")
    print(f"    Natural order: {nat_ties_33}")
    print(f"    z-score: {z_33:.2f}")
    print(f"    P(shuffle >= {nat_ties_33}): {p_ge_14:.4f} ({100*p_ge_14:.1f}%)")

    print(f"\n  Shuffle results (n=34..66):")
    print(f"    Mean ties: {mean_34_66:.2f}")
    print(f"    Std ties:  {std_34_66:.2f}")
    print(f"    Natural order: {nat_ties_34_66}")
    print(f"    z-score: {z_34_66:.2f}")

    # Distribution of ties in first 33
    from collections import Counter
    c = Counter(shuffle_ties_33)
    print(f"\n  Distribution of ties in first 33 positions ({n_trials} shuffles):")
    for k in sorted(c.keys()):
        bar = '#' * (c[k] // 5)
        marker = " <-- NATURAL" if k == nat_ties_33 else ""
        print(f"    {k:3d}: {bar} ({c[k]}){marker}")

    return {
        'nat_ties_33': nat_ties_33,
        'mean_33': mean_33, 'std_33': std_33, 'z_33': z_33,
        'p_ge_nat': p_ge_14,
        'nat_ties_34_66': nat_ties_34_66,
        'mean_34_66': mean_34_66, 'std_34_66': std_34_66, 'z_34_66': z_34_66,
    }


# ====================================================================
# TASK 4: COMPARABLE RESIDUE CLASSES
# ====================================================================
def other_moduli_test(all_primes):
    print(f"\n{'='*72}")
    print("TASK 4: COMPARABLE RESIDUE CLASSES")
    print(f"{'='*72}")

    LIMIT = 5000
    expected = math.sqrt(2 * LIMIT / math.pi)

    # Define filterings: (modulus, class, label)
    filterings = []

    # Mod 4 classes
    for c in [1, 3]:
        primes_c = [p for p in all_primes if p > 2 and p % 4 == c]
        filterings.append((4, c, f"mod4={c}", primes_c))

    # Mod 8 classes
    for c in [1, 3, 5, 7]:
        primes_c = [p for p in all_primes if p > 2 and p % 8 == c]
        filterings.append((8, c, f"mod8={c}", primes_c))

    # Mod 12 classes (coprime to 12)
    for c in [1, 5, 7, 11]:
        primes_c = [p for p in all_primes if p > 3 and p % 12 == c]
        filterings.append((12, c, f"mod12={c}", primes_c))

    # Mod 6 (our series) for reference
    p5 = [p for p in all_primes if p > 3 and p % 6 == 5]
    p7 = [p for p in all_primes if p > 3 and p % 6 == 1]
    filterings.append((6, 5, "mod6=5 (5-series)", p5))
    filterings.append((6, 1, "mod6=1 (7-series)", p7))

    print(f"\n  N = {LIMIT}, expected ties (random walk) = {expected:.1f}")
    print(f"\n  {'Label':<25} {'N_primes':>10} {'N_ties':>8} {'Ratio':>8} {'Direction':>12}")
    print(f"  {'-'*63}")

    results = []
    for mod, cls, label, primes_c in filterings:
        if len(primes_c) < LIMIT:
            print(f"  {label:<25} (only {len(primes_c)} primes, need {LIMIT})")
            continue
        chi_vals = [chi5(p) for p in primes_c[:LIMIT]]
        ties = running_sum_ties(chi_vals, LIMIT)
        n_ties = len(ties)
        if n_ties > expected:
            ratio = n_ties / expected
            direction = f"{ratio:.1f}x MORE"
        elif n_ties > 0:
            ratio = expected / n_ties
            direction = f"{ratio:.1f}x FEWER"
        else:
            ratio = float('inf')
            direction = "NO TIES"
        results.append((label, len(primes_c), n_ties, ratio, direction))
        print(f"  {label:<25} {len(primes_c):>10} {n_ties:>8} {ratio:>8.1f} {direction:>12}")

    return results


# ====================================================================
# TASK 5: HIGHER-SCALE TIE DENSITY
# ====================================================================
def high_scale_tie_density(p5):
    print(f"\n{'='*72}")
    print("TASK 5: HIGHER-SCALE TIE DENSITY (N=50000)")
    print(f"{'='*72}")

    LIMIT = 50000
    if len(p5) < LIMIT:
        print(f"  ERROR: only {len(p5)} 5-series primes, need {LIMIT}")
        return

    chi_vals = [chi5(p) for p in p5[:LIMIT]]
    ties = running_sum_ties(chi_vals, LIMIT)
    print(f"\n  Total ties in first {LIMIT}: {len(ties)}")

    # Tie density in windows of 500
    window = 500
    print(f"\n  Tie density in windows of {window}:")
    print(f"  {'Window':<15} {'Ties':>6} {'Density%':>10} {'Expected (1/sqrt)':>18}")

    densities = []
    for start in range(0, LIMIT, window):
        end = min(start + window, LIMIT)
        midpoint = (start + end) / 2
        t = sum(1 for x in ties if start < x <= end)
        w = end - start
        density = t / w
        # Random walk expected density: ~1/sqrt(pi*n/2) at position n
        # More precisely, for a window at position n of width w:
        # expected ties in window ~ w / sqrt(pi * midpoint / 2)
        expected_density = 1.0 / math.sqrt(math.pi * midpoint / 2) if midpoint > 0 else 0
        densities.append((start + 1, end, midpoint, t, density, expected_density))
        if start < 5000 or start % 5000 == 0 or start >= LIMIT - 1000:
            print(f"  {start+1}-{end:<10} {t:>6} {density*100:>9.2f}% {expected_density*100:>17.2f}%")

    # Fit comparison: observed vs 1/sqrt(n) model
    # Use windows where midpoint >= 500 to avoid edge effects
    valid = [(d[2], d[4]) for d in densities if d[2] >= 500 and d[3] > 0]
    if len(valid) >= 5:
        # Fit: density = a / sqrt(n) + b
        # Log-log: log(density) = log(a) - 0.5 * log(n)
        log_n = [math.log(n) for n, _ in valid]
        log_d = [math.log(d) for _, d in valid]
        n_pts = len(log_n)
        mean_x = sum(log_n) / n_pts
        mean_y = sum(log_d) / n_pts
        ss_xx = sum((x - mean_x)**2 for x in log_n)
        ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_n, log_d))
        if ss_xx > 0:
            slope = ss_xy / ss_xx
            intercept = mean_y - slope * mean_x
            ss_res = sum((y - (intercept + slope * x))**2 for x, y in zip(log_n, log_d))
            ss_tot = sum((y - mean_y)**2 for y in log_d)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            print(f"\n  Power-law fit: density ~ n^{slope:.3f}")
            print(f"    Expected for random walk: -0.500")
            print(f"    Observed exponent: {slope:.3f}")
            print(f"    R2: {r2:.4f}")
            print(f"    Interpretation: {'consistent with 1/sqrt(n) decay' if abs(slope + 0.5) < 0.1 else 'deviates from 1/sqrt(n)'}")

    # Cumulative tie count vs sqrt(n) model
    print(f"\n  Cumulative ties at key scales:")
    print(f"  {'N':>8} {'Observed':>10} {'Expected':>10} {'Ratio':>8}")
    for checkpoint in [100, 500, 1000, 2000, 5000, 10000, 20000, 50000]:
        if checkpoint > LIMIT:
            break
        obs = sum(1 for t in ties if t <= checkpoint)
        exp = math.sqrt(2 * checkpoint / math.pi)
        ratio = obs / exp if exp > 0 else 0
        print(f"  {checkpoint:>8} {obs:>10} {exp:>10.1f} {ratio:>8.2f}")

    # Save density CSV
    csv_path = os.path.join(RESULTS_DIR, 'tie_density_50k.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['window_start', 'window_end', 'midpoint', 'ties', 'density',
                     'expected_density_rw'])
        for row in densities:
            w.writerow(row)
    print(f"\n  Saved: {csv_path}")

    return densities


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 72)
    print("PERTURBATION TESTS (Paper A, Tasks 3-5)")
    print("=" * 72)

    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    print(f"  Available: {len(p5)} 5-series, {len(p7)} 7-series")

    # Task 3
    shuffle_results = shuffle_test(p5, n_trials=1000)

    # Task 4
    moduli_results = other_moduli_test(primes)

    # Task 5
    density_results = high_scale_tie_density(p5)

    # Save moduli CSV
    csv_path = os.path.join(RESULTS_DIR, 'comparable_moduli.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['label', 'n_primes', 'n_ties', 'ratio', 'direction'])
        for row in moduli_results:
            w.writerow(row)
    print(f"\n  Saved: {csv_path}")

    print(f"\n{'='*72}")
    print("ALL PERTURBATION TESTS COMPLETE")
    print(f"{'='*72}")


if __name__ == '__main__':
    main()
