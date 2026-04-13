#!/usr/bin/env python3
"""
Boundary Predictions v2 (Paper A v3.3 → v3.4, Conjecture 7.1 Sharpening)
=========================================================================

Identifies digit gaps in the isolated-gap regime (after ~digit 50 where
most digit-lengths are filled). Computes modular state and active
constraints at each boundary.
"""
import math, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 1_000_000
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
SMALL_PRIMES = [3, 5, 7, 11, 13, 17, 19, 23]


def sieve(limit):
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def compute_modular_state(primes_list, n):
    mod_states = {}
    for m in SMALL_PRIMES + [15]:
        prod_mod = 1
        for p in primes_list[:n]:
            prod_mod = (prod_mod * p) % m
        mod_states[m] = prod_mod
    return mod_states


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 72)
    print("BOUNDARY PREDICTIONS v2")
    print("=" * 72)

    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]

    # Compute digit-length sequences via log10 accumulation
    def digit_sequence(plist, limit=None):
        """Return list of (n, prime, digits) where digits = floor(log10(cum_prod)) + 1."""
        log_sum = 0.0
        seq = []
        for i, p in enumerate(plist):
            if limit and i >= limit:
                break
            log_sum += math.log10(p)
            d = int(log_sum) + 1
            seq.append((i + 1, p, d))
        return seq

    # Use enough primes to reach ~500 digits
    seq5 = digit_sequence(p5, 250)
    seq7 = digit_sequence(p7, 250)

    print(f"  5-series: {len(seq5)} primes, max digit = {seq5[-1][2]}")
    print(f"  7-series: {len(seq7)} primes, max digit = {seq7[-1][2]}")

    # Find isolated gaps: digit values d where no n gives D(n) = d
    # Focus on d >= 50 where gaps become isolated events
    d5_set = set(s[2] for s in seq5)
    d7_set = set(s[2] for s in seq7)
    max_d = min(max(d5_set), max(d7_set))

    # For each gap, record the n and D before/after
    def gap_info(seq, d_set):
        """For each gap digit d, find (n_before, D_before, n_after, D_after)."""
        gaps = {}
        for i in range(len(seq) - 1):
            n1, p1, d1 = seq[i]
            n2, p2, d2 = seq[i + 1]
            if d2 - d1 > 1:
                for d in range(d1 + 1, d2):
                    gaps[d] = {
                        'n_before': n1, 'd_before': d1, 'p_before': p1,
                        'n_after': n2, 'd_after': d2, 'p_after': p2,
                    }
        return gaps

    gaps5 = gap_info(seq5, d5_set)
    gaps7 = gap_info(seq7, d7_set)

    # Show gap structure starting from d=50
    print(f"\n  5-series gaps from D=50:")
    for d in sorted(gaps5.keys()):
        if d >= 50:
            g = gaps5[d]
            print(f"    D={d}: n={g['n_before']}->{g['n_after']}, "
                  f"digits {g['d_before']}->{g['d_after']}")

    print(f"\n  7-series gaps from D=50:")
    for d in sorted(gaps7.keys()):
        if d >= 50:
            g = gaps7[d]
            print(f"    D={d}: n={g['n_before']}->{g['n_after']}, "
                  f"digits {g['d_before']}->{g['d_after']}")

    # Now identify boundaries in the paper's sense
    # A boundary is a group of gap-digits that are close together
    # The paper identifies:
    #   Boundary 1: 5-series {60,61}, 7-series {62,63} (staggered)
    #   Boundary 2: 5-series {80,81}, 7-series {80,81} (coincident)
    # We need boundary 3 and 4.

    # Let's look at the raw gap pattern from D=50 onwards
    print(f"\n  Gap digit map from D=50 (. = filled, 5 = 5-only gap, 7 = 7-only gap, B = both):")
    for d_start in range(50, min(max_d + 1, 300), 50):
        d_end = min(d_start + 50, max_d + 1)
        row = []
        for d in range(d_start, d_end):
            g5 = d in gaps5 and d >= 50
            g7 = d in gaps7 and d >= 50
            # More precisely: is d NOT in the digit set?
            g5 = d not in d5_set
            g7 = d not in d7_set
            if g5 and g7:
                row.append('B')
            elif g5:
                row.append('5')
            elif g7:
                row.append('7')
            else:
                row.append('.')
        print(f"    D={d_start:3d}-{d_end-1:3d}: {''.join(row)}")

    # Identify isolated gap clusters from D=50 onwards
    # Group consecutive gap-digits within 3 of each other
    all_gap_d = set()
    for d in range(50, max_d + 1):
        if d not in d5_set or d not in d7_set:
            all_gap_d.add(d)

    # Actually let me be more precise. At small D, MOST digits are gaps.
    # The transition to "most digits are filled" happens gradually.
    # Let me find where the gap density drops below 50%
    for window_start in range(1, 200, 10):
        window_end = window_start + 20
        total = window_end - window_start
        g5_count = sum(1 for d in range(window_start, window_end) if d not in d5_set)
        g7_count = sum(1 for d in range(window_start, window_end) if d not in d7_set)
        if window_start >= 40 and window_start <= 100:
            print(f"    D={window_start}-{window_end-1}: 5-gap={g5_count}/{total} ({100*g5_count/total:.0f}%), "
                  f"7-gap={g7_count}/{total} ({100*g7_count/total:.0f}%)")

    # The paper's convention: boundaries are where isolated gaps appear
    # after the series transitions to filling most digits.
    # Let's identify the gap groups precisely by looking for gaps after
    # the series has started filling every digit for at least 5 consecutive digits.

    # Find transition point: first d where 10 consecutive digits are all filled
    def find_fill_transition(d_set, max_d):
        for d in range(1, max_d - 10):
            if all(dd in d_set for dd in range(d, d + 10)):
                return d
        return max_d

    t5 = find_fill_transition(d5_set, max_d)
    t7 = find_fill_transition(d7_set, max_d)
    print(f"\n  Fill transition (first 10 consecutive filled):")
    print(f"    5-series: D = {t5}")
    print(f"    7-series: D = {t7}")

    # Gaps AFTER the fill transition
    print(f"\n  5-series gaps after fill transition (D >= {t5}):")
    post_gaps5 = []
    for d in sorted(gaps5.keys()):
        if d >= t5:
            g = gaps5[d]
            post_gaps5.append((d, g))
            print(f"    D={d}: n={g['n_before']}->{g['n_after']}, "
                  f"digits {g['d_before']}->{g['d_after']}")

    print(f"\n  7-series gaps after fill transition (D >= {t7}):")
    post_gaps7 = []
    for d in sorted(gaps7.keys()):
        if d >= t7:
            g = gaps7[d]
            post_gaps7.append((d, g))
            print(f"    D={d}: n={g['n_before']}->{g['n_after']}, "
                  f"digits {g['d_before']}->{g['d_after']}")

    # Group into boundaries
    def group_into_boundaries(post_gaps5, post_gaps7):
        """Group gap digits from both series into boundary events."""
        # Collect all gap digits
        events = {}
        for d, g in post_gaps5:
            events.setdefault(d, {})['5'] = g
        for d, g in post_gaps7:
            events.setdefault(d, {})['7'] = g

        # Group: consecutive or near-consecutive gap digits
        sorted_d = sorted(events.keys())
        if not sorted_d:
            return []
        boundaries = []
        current = [sorted_d[0]]
        for d in sorted_d[1:]:
            if d - current[-1] <= 2:
                current.append(d)
            else:
                boundaries.append(current)
                current = [d]
        boundaries.append(current)

        result = []
        for digits in boundaries:
            has5 = any('5' in events[d] for d in digits)
            has7 = any('7' in events[d] for d in digits)
            both = any('5' in events[d] and '7' in events[d] for d in digits)
            if both:
                btype = 'coincident'
            elif has5 and has7:
                btype = 'staggered'
            elif has5:
                btype = '5-only'
            else:
                btype = '7-only'

            info5 = events[digits[0]].get('5') if has5 else None
            info7 = events[digits[0]].get('7') if has7 else None
            # For staggered: find correct info for each series
            if has5:
                for d in digits:
                    if '5' in events[d]:
                        info5 = events[d]['5']
                        break
            if has7:
                for d in digits:
                    if '7' in events[d]:
                        info7 = events[d]['7']
                        break

            result.append({
                'digits': digits,
                'type': btype,
                'info5': info5,
                'info7': info7,
            })
        return result

    boundaries = group_into_boundaries(post_gaps5, post_gaps7)

    print(f"\n  Identified {len(boundaries)} boundary events:")
    for i, b in enumerate(boundaries):
        print(f"    {i+1}. Type={b['type']}, D={{{min(b['digits'])}..{max(b['digits'])}}}")
        if b['info5']:
            print(f"       5-series: n={b['info5']['n_before']}->{b['info5']['n_after']}, "
                  f"D={b['info5']['d_before']}->{b['info5']['d_after']}")
        if b['info7']:
            print(f"       7-series: n={b['info7']['n_before']}->{b['info7']['n_after']}, "
                  f"D={b['info7']['d_before']}->{b['info7']['d_after']}")

    # ================================================================
    # MODULAR STATE AND ACTIVE CONSTRAINTS
    # ================================================================
    print(f"\n{'='*72}")
    print("MODULAR STATE AND ACTIVE CONSTRAINTS")
    print(f"{'='*72}")

    for i, b in enumerate(boundaries[:6]):
        print(f"\n  --- Boundary {i+1}: {b['type']}, D={{{min(b['digits'])}..{max(b['digits'])}}} ---")

        for label, series_primes, info in [
            ('5-series', p5, b['info5']),
            ('7-series', p7, b['info7']),
        ]:
            if info is None:
                print(f"  {label}: no gap")
                continue
            n_b = info['n_before']
            ms = compute_modular_state(series_primes, n_b)
            active = [m for m in SMALL_PRIMES if ms[m] != 0]
            inactive = [m for m in SMALL_PRIMES if ms[m] == 0]
            min_filler = 1
            for m in active:
                min_filler *= m

            print(f"  {label}: n_B={n_b}, D={info['d_before']}->{info['d_after']}")
            mods_str = ', '.join(f"mod{m}={ms[m]}" for m in SMALL_PRIMES)
            print(f"    {mods_str}")
            print(f"    Active (coprime): {active}")
            print(f"    Inactive (divides): {inactive}")
            print(f"    Minimum filler: {min_filler} = {'*'.join(str(m) for m in active) if active else '1'}")

    # ================================================================
    # SUMMARY TABLE
    # ================================================================
    print(f"\n{'='*72}")
    print("SUMMARY TABLE FOR CinC")
    print(f"{'='*72}")

    print(f"\n  {'Bdy':>3} {'Type':<11} {'Series':<9} {'n_B':>4} {'Gap D':>12} "
          f"{'m3':>3} {'m5':>3} {'m7':>3} {'m11':>4} {'m13':>4} {'Active':>22} {'Filler':>8}")

    csv_rows = []
    for i, b in enumerate(boundaries[:6]):
        for label, code, sp, info in [
            ('5-ser', '5', p5, b['info5']),
            ('7-ser', '7', p7, b['info7']),
        ]:
            if info is None:
                continue
            n_b = info['n_before']
            ms = compute_modular_state(sp, n_b)
            active = [m for m in SMALL_PRIMES if ms[m] != 0]
            filler = 1
            for m in active:
                filler *= m
            gap_str = f"{min(b['digits'])}-{max(b['digits'])}"
            print(f"  {i+1:>3} {b['type']:<11} {label:<9} {n_b:>4} {gap_str:>12} "
                  f"{ms[3]:>3} {ms[5]:>3} {ms[7]:>3} {ms[11]:>4} {ms[13]:>4} "
                  f"{str(active):>22} {filler:>8}")
            csv_rows.append([i+1, b['type'], label, n_b, gap_str,
                             ms[3], ms[5], ms[7], ms[11], ms[13], ms[17], ms[19], ms[23],
                             str(active), filler])

    csv_path = os.path.join(RESULTS_DIR, 'boundary_predictions_v2.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['boundary', 'type', 'series', 'n_before', 'gap_range',
                     'mod3', 'mod5', 'mod7', 'mod11', 'mod13', 'mod17', 'mod19', 'mod23',
                     'active_moduli', 'min_filler'])
        for row in csv_rows:
            w.writerow(row)
    print(f"\n  Saved: {csv_path}")


if __name__ == '__main__':
    main()
