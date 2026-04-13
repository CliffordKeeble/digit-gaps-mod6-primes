#!/usr/bin/env python3
"""
Chi5 Regime Analysis (Paper A, Task 2)
=======================================

Computes the running sum S(n) = sum chi_5(p_i) for each mod-6 series
over the first 5000 primes. Reports ties, tie deserts, tie density by
window, and Chebyshev-bias comparison.

chi_5(p) = +1 if p === +/-1 (mod 5) [split in Z[phi]]
chi_5(p) = -1 if p === +/-2 (mod 5) [inert in Z[phi]]
chi_5(5) = 0  [ramified]
"""
import math, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 2_000_000  # enough for 50000+ primes per series
LIMIT = 5000
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
    """Legendre symbol mod 5."""
    r = p % 5
    if r == 0:
        return 0  # ramified
    elif r in (1, 4):
        return 1  # split
    else:
        return -1  # inert


def compute_running_sum(primes_list, limit):
    """Compute S(n) = sum chi5(p_i) for i=1..n, for n=1..limit."""
    s = 0
    running = []
    for i, p in enumerate(primes_list[:limit]):
        s += chi5(p)
        running.append(s)
    return running


def find_ties(running):
    """Return list of indices (1-based) where S(n) = 0."""
    return [i + 1 for i, s in enumerate(running) if s == 0]


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 72)
    print(f"CHI5 REGIME ANALYSIS (first {LIMIT} primes per series)")
    print("=" * 72)

    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    print(f"  5-series available: {len(p5)}, 7-series available: {len(p7)}")

    # === Running sums ===
    S5 = compute_running_sum(p5, LIMIT)
    S7 = compute_running_sum(p7, LIMIT)

    ties_5 = find_ties(S5)
    ties_7 = find_ties(S7)

    print(f"\n  5-series ties (S=0): {len(ties_5)} in first {LIMIT}")
    print(f"  7-series ties (S=0): {len(ties_7)} in first {LIMIT}")

    # === 2.1 Full tie sequences ===
    print(f"\n{'='*72}")
    print("2.1 TIE INVENTORY")
    print(f"{'='*72}")

    # 5-series ties
    print(f"\n  5-series: {len(ties_5)} ties")
    print(f"  First 50 ties: {ties_5[:50]}")
    if len(ties_5) > 50:
        print(f"  Last 10 ties: {ties_5[-10:]}")

    # 7-series ties — exhaustive since few
    print(f"\n  7-series: {len(ties_7)} ties (exhaustive list):")
    for t in ties_7:
        print(f"    n={t}, p={p7[t-1]}, S7({t})=0")

    # === 2.2 Tie density by window ===
    print(f"\n{'='*72}")
    print("2.2 TIE DENSITY BY WINDOW")
    print(f"{'='*72}")

    window = 33  # matches draft's first regime window
    print(f"\n  Window size: {window}")
    print(f"  {'Window':<15} {'5-series ties':>14} {'5-series %':>12} {'7-series ties':>14} {'7-series %':>12}")

    density_data = []
    for start in range(0, LIMIT, window):
        end = min(start + window, LIMIT)
        t5 = sum(1 for t in ties_5 if start < t <= end)
        t7 = sum(1 for t in ties_7 if start < t <= end)
        w = end - start
        d5 = 100.0 * t5 / w
        d7 = 100.0 * t7 / w
        label = f"{start+1}-{end}"
        density_data.append((label, start + 1, end, t5, d5, t7, d7))
        if start < 330 or start >= LIMIT - 66:  # show first 10 and last 2 windows
            print(f"  {label:<15} {t5:>14} {d5:>11.1f}% {t7:>14} {d7:>11.1f}%")
        elif start == 330:
            print(f"  {'...':<15}")

    # Also show with window=100 for broader view
    print(f"\n  Window size: 100")
    print(f"  {'Window':<15} {'5-series ties':>14} {'5-series %':>12} {'7-series ties':>14} {'7-series %':>12}")
    for start in range(0, min(LIMIT, 1000), 100):
        end = min(start + 100, LIMIT)
        t5 = sum(1 for t in ties_5 if start < t <= end)
        t7 = sum(1 for t in ties_7 if start < t <= end)
        w = end - start
        print(f"  {start+1}-{end:<10} {t5:>14} {100*t5/w:>11.1f}% {t7:>14} {100*t7/w:>11.1f}%")

    # === 2.3 Chebyshev-bias comparison ===
    print(f"\n{'='*72}")
    print("2.3 CHEBYSHEV-BIAS COMPARISON")
    print(f"{'='*72}")

    expected_ties = math.sqrt(2 * LIMIT / math.pi)
    ratio_5 = len(ties_5) / expected_ties
    ratio_7 = expected_ties / len(ties_7) if len(ties_7) > 0 else float('inf')

    print(f"\n  N = {LIMIT}")
    print(f"  Expected ties (random walk): sqrt(2*{LIMIT}/pi) = {expected_ties:.1f}")
    print(f"  5-series observed: {len(ties_5)} ties")
    print(f"  7-series observed: {len(ties_7)} ties")
    print(f"  RATIO_5 = {len(ties_5)}/{expected_ties:.1f} = {ratio_5:.2f}x MORE than expected")
    print(f"  RATIO_7 = {expected_ties:.1f}/{len(ties_7)} = {ratio_7:.1f}x FEWER than expected")

    # === 2.4 Tie deserts ===
    print(f"\n{'='*72}")
    print("2.4 TIE DESERTS (5-series)")
    print(f"{'='*72}")

    # Compute gaps between consecutive ties
    if len(ties_5) >= 2:
        gaps_5 = [(ties_5[i], ties_5[i+1], ties_5[i+1] - ties_5[i])
                  for i in range(len(ties_5) - 1)]
        # Sort by gap size
        large_gaps = sorted(gaps_5, key=lambda x: -x[2])
        print(f"\n  Largest 10 tie gaps (5-series):")
        print(f"  {'From':>6} {'To':>6} {'Gap':>6}  {'Max |S| in gap':>16}")
        for from_n, to_n, gap in large_gaps[:10]:
            max_abs_s = max(abs(S5[i]) for i in range(from_n, to_n - 1))
            print(f"  {from_n:>6} {to_n:>6} {gap:>6}  {max_abs_s:>16}")

    # First desert >= 8 steps
    print(f"\n  First tie-desert (gap >= 8):")
    for from_n, to_n, gap in gaps_5:
        if gap >= 8:
            max_abs_s = max(abs(S5[i]) for i in range(from_n, to_n - 1))
            print(f"    From n={from_n} to n={to_n}, gap={gap}")
            print(f"    Max |S| during desert: {max_abs_s}")
            break

    # First desert >= 10 steps
    print(f"\n  First tie-desert (gap >= 10):")
    for from_n, to_n, gap in gaps_5:
        if gap >= 10:
            max_abs_s = max(abs(S5[i]) for i in range(from_n, to_n - 1))
            print(f"    From n={from_n} to n={to_n}, gap={gap}")
            print(f"    Max |S| during desert: {max_abs_s}")
            break

    # === 2.5 7-series tie inventory ===
    print(f"\n{'='*72}")
    print("2.5 7-SERIES TIE INVENTORY")
    print(f"{'='*72}")
    print(f"\n  Complete list of n where S7(n) = 0 in [1, {LIMIT}]:")
    for t in ties_7:
        print(f"    n={t}, prime={p7[t-1]}, chi5={chi5(p7[t-1])}")
    print(f"  Total: {len(ties_7)}")
    if ties_7:
        print(f"  Last tie at n={ties_7[-1]}; S7 does not return to zero after that in [{ties_7[-1]+1}, {LIMIT}]")

    # S7 range
    print(f"\n  S7 range in [{1}, {LIMIT}]:")
    print(f"    Min: {min(S7)}")
    print(f"    Max: {max(S7)}")
    print(f"    S7({LIMIT}) = {S7[-1]}")

    # === Detailed S5 and S7 for first 70 steps ===
    print(f"\n{'='*72}")
    print("DETAILED S(n) FOR FIRST 70 PRIMES")
    print(f"{'='*72}")
    print(f"\n  {'n':>4} {'p5':>6} {'chi5':>5} {'S5(n)':>6} {'tie?':>5}  |  {'p7':>6} {'chi5':>5} {'S7(n)':>6} {'tie?':>5}")
    for i in range(min(70, LIMIT)):
        c5 = chi5(p5[i])
        c7 = chi5(p7[i])
        t5 = "TIE" if S5[i] == 0 else ""
        t7 = "TIE" if S7[i] == 0 else ""
        print(f"  {i+1:>4} {p5[i]:>6} {c5:>+5d} {S5[i]:>+6d} {t5:>5}  |  {p7[i]:>6} {c7:>+5d} {S7[i]:>+6d} {t7:>5}")

    # === PLACEHOLDER VALUES FOR DRAFT ===
    print(f"\n{'='*72}")
    print("PLACEHOLDER VALUES FOR DRAFT")
    print(f"{'='*72}")
    print(f"  [LIMIT] = {LIMIT}")
    print(f"  [N_TIES_5] = {len(ties_5)}")
    print(f"  [N_TIES_7] = {len(ties_7)}")
    print(f"  [EXPECTED_TIES] = {expected_ties:.1f}")
    print(f"  [RATIO_5] = {ratio_5:.1f}")
    print(f"  [RATIO_7] = {ratio_7:.1f}")

    # Max |S| in first desert
    for from_n, to_n, gap in gaps_5:
        if gap >= 10:
            max_s = max(abs(S5[i]) for i in range(from_n, to_n - 1))
            print(f"  [MAX_S_IN_FIRST_DESERT] = {max_s} (gap {from_n}->{to_n})")
            break

    # Tight oscillation range
    max_s_1_33 = max(abs(S5[i]) for i in range(33))
    print(f"  Max |S5| in n=1..33: {max_s_1_33}")
    print(f"  Ties in n=1..33: {sum(1 for t in ties_5 if t <= 33)}")

    # === Save CSVs ===
    csv5_path = os.path.join(RESULTS_DIR, 'ties_5series.csv')
    with open(csv5_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['n', 'prime', 'chi5', 'S_n', 'is_tie', 'gap_to_next_tie'])
        for i in range(LIMIT):
            is_tie = S5[i] == 0
            # Find gap to next tie
            gap_next = ''
            if is_tie:
                next_ties = [t for t in ties_5 if t > i + 1]
                if next_ties:
                    gap_next = next_ties[0] - (i + 1)
            w.writerow([i + 1, p5[i], chi5(p5[i]), S5[i], is_tie, gap_next])

    csv7_path = os.path.join(RESULTS_DIR, 'ties_7series.csv')
    with open(csv7_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['n', 'prime', 'chi5', 'S_n', 'is_tie', 'gap_to_next_tie'])
        for i in range(LIMIT):
            is_tie = S7[i] == 0
            gap_next = ''
            if is_tie:
                next_ties = [t for t in ties_7 if t > i + 1]
                if next_ties:
                    gap_next = next_ties[0] - (i + 1)
            w.writerow([i + 1, p7[i], chi5(p7[i]), S7[i], is_tie, gap_next])

    print(f"\n  Saved: {csv5_path}")
    print(f"  Saved: {csv7_path}")


if __name__ == '__main__':
    main()
