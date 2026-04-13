#!/usr/bin/env python3
"""
Crystallisation-Shadow Tests (Paper A / Bootstrap Bridge)
==========================================================

Task 1: Mod-q boundary scaling — is the two-isolated-boundary structure
         at e^140 and e^184 specific to mod-6, or generic?
Task 2: Sub-structure between boundaries 1 and 2 (D=62..79).
Task 3: Tension-ladder shadows in chi5 running sums.
"""
import math, random, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 2_000_000
LN10 = math.log(10)
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
    if r == 0: return 0
    elif r in (1, 4): return 1
    else: return -1


def coprime_classes(q):
    """Return residue classes mod q that are coprime to q (and > 1 for filtering)."""
    return [r for r in range(1, q) if math.gcd(r, q) == 1]


def digit_sequence(primes_list, n_max=500):
    log_sum = 0.0
    seq = []
    for i, p in enumerate(primes_list[:n_max]):
        log_sum += math.log10(p)
        seq.append((i + 1, p, int(log_sum) + 1, log_sum))
    return seq


def find_3digit_jumps(seq):
    """Find all jumps >= 3 digits. Returns list of dicts."""
    jumps = []
    for i in range(len(seq) - 1):
        n1, p1, d1, lg1 = seq[i]
        n2, p2, d2, lg2 = seq[i + 1]
        if d2 - d1 >= 3:
            jumps.append({
                'n_before': n1, 'd_before': d1, 'ln_before': lg1 * LN10,
                'n_after': n2, 'd_after': d2, 'p_after': p2,
                'jump': d2 - d1,
                'gap_digits': list(range(d1 + 1, d2)),
            })
    return jumps


# ====================================================================
# TASK 1: MOD-q BOUNDARY SCALING
# ====================================================================
def task1_mod_q_scaling(all_primes):
    print(f"\n{'='*72}")
    print("TASK 1: MOD-q BOUNDARY SCALING")
    print(f"{'='*72}")

    moduli = [4, 6, 8, 10, 12, 30]
    results = []

    for q in moduli:
        classes = coprime_classes(q)
        print(f"\n  --- mod {q}, classes: {classes} ---")

        for r in classes:
            # Filter primes: p > q and p === r (mod q)
            # For q=6: classes are {1, 5}, primes > 3
            # For q=4: classes are {1, 3}, primes > 2
            if q == 4:
                plist = [p for p in all_primes if p > 2 and p % q == r]
            elif q in (6, 10, 12, 30):
                plist = [p for p in all_primes if p > q and p % q == r]
            elif q == 8:
                plist = [p for p in all_primes if p > 2 and p % q == r]
            else:
                plist = [p for p in all_primes if p > q and p % q == r]

            if len(plist) < 100:
                print(f"    r={r}: only {len(plist)} primes, skipping")
                continue

            seq = digit_sequence(plist, min(500, len(plist)))
            jumps = find_3digit_jumps(seq)

            # Find the first few 3-digit jumps
            first_jumps = jumps[:5] if jumps else []

            # For each jump, check if it's "isolated" (nearest other jump >= 5 gap-digits away)
            for j_idx, j in enumerate(first_jumps):
                isolated = True
                for k_idx, k in enumerate(first_jumps):
                    if k_idx == j_idx:
                        continue
                    # Check if gap digits overlap or are close
                    if k['gap_digits'] and j['gap_digits']:
                        dist = min(abs(max(j['gap_digits']) - min(k['gap_digits'])),
                                   abs(max(k['gap_digits']) - min(j['gap_digits'])))
                        if dist < 5:
                            isolated = False
                j['isolated'] = isolated

            row = {
                'q': q, 'r': r, 'n_primes': len(plist),
                'jumps': first_jumps,
            }
            results.append(row)

            if first_jumps:
                for ji, j in enumerate(first_jumps[:3]):
                    gap_str = f"{{{min(j['gap_digits'])}..{max(j['gap_digits'])}}}"
                    ln_d = min(j['gap_digits']) * LN10
                    iso_str = "isolated" if j.get('isolated') else "clustered"
                    print(f"    r={r} gap {ji+1}: D={gap_str}, n={j['n_before']}->{j['n_after']}, "
                          f"ln(10)*D={ln_d:.1f}, {iso_str}")
            else:
                print(f"    r={r}: no 3-digit jumps in first {min(500, len(plist))} primes")

    # Summary table
    print(f"\n{'='*72}")
    print("TASK 1 SUMMARY: FIRST TWO BOUNDARIES PER (q, r)")
    print(f"{'='*72}")
    print(f"  {'q':>3} {'r':>3} {'Gap1 D':>10} {'ln*D1':>8} {'Gap2 D':>10} {'ln*D2':>8} {'Gap3 D':>10} {'Near 140?':>10} {'Near 184?':>10}")

    csv_rows = []
    for row in results:
        q, r = row['q'], row['r']
        jumps = row['jumps']
        g1 = g2 = g3 = '-'
        ln1 = ln2 = '-'
        near140 = near184 = ''
        if len(jumps) >= 1:
            d1 = min(jumps[0]['gap_digits'])
            g1 = f"{d1}-{max(jumps[0]['gap_digits'])}"
            ln1 = f"{d1 * LN10:.1f}"
            near140 = 'YES' if abs(d1 * LN10 - 140) < 10 else ''
        if len(jumps) >= 2:
            d2 = min(jumps[1]['gap_digits'])
            g2 = f"{d2}-{max(jumps[1]['gap_digits'])}"
            ln2 = f"{d2 * LN10:.1f}"
            near184 = 'YES' if abs(d2 * LN10 - 184) < 10 else ''
        if len(jumps) >= 3:
            d3 = min(jumps[2]['gap_digits'])
            g3 = f"{d3}-{max(jumps[2]['gap_digits'])}"

        print(f"  {q:>3} {r:>3} {g1:>10} {ln1:>8} {g2:>10} {ln2:>8} {g3:>10} {near140:>10} {near184:>10}")
        csv_rows.append([q, r, g1, ln1, g2, ln2, g3, near140, near184])

    # Specific check: mod-6 boundaries
    print(f"\n  Reference: ln(10) * 60 = {60 * LN10:.1f}, ln(10) * 80 = {80 * LN10:.1f}")
    print(f"  Target: 140 and 184")

    csv_path = os.path.join(RESULTS_DIR, 'mod_q_boundaries.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['q', 'r', 'gap1_D', 'ln_D1', 'gap2_D', 'ln_D2', 'gap3_D', 'near_140', 'near_184'])
        for row in csv_rows:
            w.writerow(row)
    print(f"  Saved: {csv_path}")

    return results


# ====================================================================
# TASK 2: SUB-STRUCTURE BETWEEN BOUNDARIES 1 AND 2
# ====================================================================
def task2_substructure(p5, p7):
    print(f"\n{'='*72}")
    print("TASK 2: SUB-STRUCTURE IN D = 62 ... 79")
    print(f"{'='*72}")

    for label, plist in [('5-series', p5), ('7-series', p7)]:
        seq = digit_sequence(plist, 200)
        print(f"\n  --- {label} ---")
        print(f"  {'n':>4} {'D(n)':>6} {'D(n+1)':>8} {'Jump':>5} {'Prime added':>12} {'ln(10)*D(n)':>12} {'Skip?':>6}")

        skip_events = []
        for i in range(len(seq) - 1):
            n1, p1, d1, lg1 = seq[i]
            n2, p2, d2, lg2 = seq[i + 1]
            if 62 <= d1 <= 79:
                jump = d2 - d1
                skip = jump > 1
                ln_d = d1 * LN10
                print(f"  {n1:>4} {d1:>6} {d2:>8} {jump:>5} {p2:>12} {ln_d:>12.1f} {'YES' if skip else '':>6}")
                if skip:
                    skip_events.append({
                        'n': n1, 'd': d1, 'd_next': d2, 'jump': jump,
                        'prime': p2, 'ln_d': ln_d,
                    })

        print(f"\n  Skip events (jump > 1) in D=62..79:")
        if skip_events:
            for s in skip_events:
                print(f"    n={s['n']}, D={s['d']}->{s['d_next']}, jump={s['jump']}, "
                      f"ln(10)*D={s['ln_d']:.1f}, prime={s['prime']}")
        else:
            print(f"    NONE — all jumps are exactly 1 digit")

        # Jump histogram
        jumps_in_range = []
        for i in range(len(seq) - 1):
            n1, p1, d1, lg1 = seq[i]
            n2, p2, d2, lg2 = seq[i + 1]
            if 62 <= d1 <= 79:
                jumps_in_range.append(d2 - d1)
        if jumps_in_range:
            from collections import Counter
            jc = Counter(jumps_in_range)
            print(f"\n  Jump histogram in D=62..79:")
            for j in sorted(jc.keys()):
                print(f"    jump={j}: {jc[j]} ({'#' * jc[j]})")


# ====================================================================
# TASK 3: TENSION-LADDER SHADOWS IN CHI5
# ====================================================================
def task3_tension_ladder(p5, p7):
    print(f"\n{'='*72}")
    print("TASK 3: TENSION-LADDER SHADOWS IN CHI5")
    print(f"{'='*72}")

    ladder_indices = [41, 51, 53, 62]
    control_indices = [30, 31, 33, 43, 61, 66]
    all_test = sorted(set(ladder_indices + control_indices))

    for label, plist in [('5-series', p5), ('7-series', p7)]:
        chi_vals = [chi5(p) for p in plist[:200]]
        S = []
        running = 0
        for c in chi_vals:
            running += c
            S.append(running)

        # Find all ties
        ties = [i + 1 for i, s in enumerate(S) if s == 0]

        print(f"\n  --- {label} ---")
        print(f"  {'n':>4} {'S(n)':>6} {'Tie?':>5} {'LocalExt?':>10} {'chi5(p_n)':>10} {'Dist to tie':>12} {'Type':>8}")

        for n in all_test:
            if n > len(S):
                continue
            s_n = S[n - 1]
            is_tie = s_n == 0
            # Local extremum within +/- 5
            lo = max(0, n - 6)
            hi = min(len(S), n + 5)
            neighborhood = S[lo:hi]
            is_local_max = s_n == max(neighborhood) and s_n > 0
            is_local_min = s_n == min(neighborhood) and s_n < 0
            is_extremum = is_local_max or is_local_min

            chi_val = chi5(plist[n - 1])

            # Distance to nearest tie
            if ties:
                dist = min(abs(n - t) for t in ties)
            else:
                dist = float('inf')

            ntype = 'LADDER' if n in ladder_indices else 'CONTROL'
            ext_str = 'MAX' if is_local_max else ('MIN' if is_local_min else '')

            print(f"  {n:>4} {s_n:>+6d} {'TIE' if is_tie else '':>5} {ext_str:>10} "
                  f"{chi_val:>+10d} {dist:>12} {ntype:>8}")

    # Null distribution: 100 random indices in [10, 100]
    print(f"\n  --- NULL DISTRIBUTION (100 random indices in [10, 100]) ---")
    rng = random.Random(42)
    null_indices = sorted(rng.sample(range(10, 101), min(91, 100)))

    for label, plist in [('5-series', p5), ('7-series', p7)]:
        chi_vals = [chi5(p) for p in plist[:200]]
        S = []
        running = 0
        for c in chi_vals:
            running += c
            S.append(running)
        ties = [i + 1 for i, s in enumerate(S) if s == 0]

        n_ties_null = 0
        n_extrema_null = 0
        n_near_tie_null = 0  # within 1 of a tie

        for n in null_indices:
            if n > len(S):
                continue
            s_n = S[n - 1]
            if s_n == 0:
                n_ties_null += 1
            lo = max(0, n - 6)
            hi = min(len(S), n + 5)
            neighborhood = S[lo:hi]
            if (s_n == max(neighborhood) and s_n > 0) or (s_n == min(neighborhood) and s_n < 0):
                n_extrema_null += 1
            if ties:
                dist = min(abs(n - t) for t in ties)
                if dist <= 1:
                    n_near_tie_null += 1

        n_total = len([n for n in null_indices if n <= len(S)])
        print(f"\n  {label}:")
        print(f"    Ties:       {n_ties_null}/{n_total} = {100*n_ties_null/n_total:.1f}%")
        print(f"    Extrema:    {n_extrema_null}/{n_total} = {100*n_extrema_null/n_total:.1f}%")
        print(f"    Near-tie:   {n_near_tie_null}/{n_total} = {100*n_near_tie_null/n_total:.1f}%")

    # Ladder-index statistics
    print(f"\n  --- LADDER vs NULL COMPARISON ---")
    for label, plist in [('5-series', p5), ('7-series', p7)]:
        chi_vals = [chi5(p) for p in plist[:200]]
        S = []
        running = 0
        for c in chi_vals:
            running += c
            S.append(running)
        ties = [i + 1 for i, s in enumerate(S) if s == 0]

        ladder_ties = sum(1 for n in ladder_indices if n <= len(S) and S[n-1] == 0)
        ladder_extrema = 0
        ladder_near = 0
        for n in ladder_indices:
            if n > len(S): continue
            s_n = S[n-1]
            lo = max(0, n - 6)
            hi = min(len(S), n + 5)
            nb = S[lo:hi]
            if (s_n == max(nb) and s_n > 0) or (s_n == min(nb) and s_n < 0):
                ladder_extrema += 1
            if ties:
                dist = min(abs(n - t) for t in ties)
                if dist <= 1:
                    ladder_near += 1

        n_ladder = len([n for n in ladder_indices if n <= len(S)])
        print(f"\n  {label} ladder indices {ladder_indices}:")
        print(f"    Ties:     {ladder_ties}/{n_ladder}")
        print(f"    Extrema:  {ladder_extrema}/{n_ladder}")
        print(f"    Near-tie: {ladder_near}/{n_ladder}")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 72)
    print("CRYSTALLISATION-SHADOW TESTS")
    print("=" * 72)

    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]

    task1_mod_q_scaling(primes)
    task2_substructure(p5, p7)
    task3_tension_ladder(p5, p7)

    print(f"\n{'='*72}")
    print("ALL TASKS COMPLETE")
    print(f"{'='*72}")


if __name__ == '__main__':
    main()
