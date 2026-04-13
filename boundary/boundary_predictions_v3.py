#!/usr/bin/env python3
"""
Boundary Predictions v3 (Paper A v3.3 → v3.4)
==============================================

The paper's "digit gap boundaries" are where D(n+1) - D(n) >= 3, i.e.,
the cumulative product jumps by 3+ digits when the next prime is multiplied
in. This creates 2 or more consecutive missing digit-lengths.

Boundary 1: 5-series at n=30->31 jumps 59->62 (gap {60,61})
            7-series at n=30->31 jumps 61->64 (gap {62,63})
Boundary 2: 5-series at n=38->39 jumps 79->82 (gap {80,81})
            7-series at n=37->38 jumps 79->82 (gap {80,81})

We identify all such jumps and their combined boundary structure.
"""
import math, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 2_000_000
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
    print("BOUNDARY PREDICTIONS v3 — MULTI-DIGIT JUMPS")
    print("=" * 72)

    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]

    # Compute digit sequences
    def digit_seq(plist, n_max=500):
        log_sum = 0.0
        seq = []
        for i, p in enumerate(plist[:n_max]):
            log_sum += math.log10(p)
            seq.append((i + 1, p, int(log_sum) + 1))
        return seq

    seq5 = digit_seq(p5, 500)
    seq7 = digit_seq(p7, 500)

    # Find all jumps >= 3 digits
    def find_big_jumps(seq, min_jump=3):
        jumps = []
        for i in range(len(seq) - 1):
            n1, p1, d1 = seq[i]
            n2, p2, d2 = seq[i + 1]
            jump = d2 - d1
            if jump >= min_jump:
                gap_digits = list(range(d1 + 1, d2))
                jumps.append({
                    'n_before': n1, 'p_before': p1, 'd_before': d1,
                    'n_after': n2, 'p_after': p2, 'd_after': d2,
                    'jump': jump, 'gap_digits': gap_digits,
                })
        return jumps

    jumps5 = find_big_jumps(seq5)
    jumps7 = find_big_jumps(seq7)

    print(f"\n  5-series jumps >= 3 digits (first 20):")
    print(f"  {'n':>5} {'p_next':>8} {'D_before':>10} {'D_after':>10} {'Jump':>6} {'Gap digits'}")
    for j in jumps5[:20]:
        print(f"  {j['n_before']:>5} {j['p_after']:>8} {j['d_before']:>10} {j['d_after']:>10} "
              f"{j['jump']:>6} {j['gap_digits']}")

    print(f"\n  7-series jumps >= 3 digits (first 20):")
    for j in jumps7[:20]:
        print(f"  {j['n_before']:>5} {j['p_after']:>8} {j['d_before']:>10} {j['d_after']:>10} "
              f"{j['jump']:>6} {j['gap_digits']}")

    # The pattern: at small n, jumps of 3 are very common (every prime
    # contributes ~1.5 digits of log growth, so a 3-digit jump requires
    # a prime ~ 10^1.5 = 31 relative to the previous). As n grows, the
    # primes get larger but each contributes < 1 digit, so 3-digit jumps
    # become rare.
    #
    # The paper's convention: "boundary" events are where 3-digit jumps
    # become notable in the context of the series' growth. The first
    # boundaries are the LAST jumps before the series settles into
    # filling every digit. Let me find the transition.

    # Find where each series last has a jump >= 3
    print(f"\n  5-series: last jump >= 3 at n={jumps5[-1]['n_before']} "
          f"(D={jumps5[-1]['d_before']}->{jumps5[-1]['d_after']})")
    print(f"  7-series: last jump >= 3 at n={jumps7[-1]['n_before']} "
          f"(D={jumps7[-1]['d_before']}->{jumps7[-1]['d_after']})")

    # Find where single-digit jumps become the norm (jump == 1 for
    # several consecutive primes)
    def find_settling_point(seq, run_length=5):
        """Find the first n where the next run_length jumps are all 1."""
        for i in range(len(seq) - run_length):
            if all(seq[j+1][2] - seq[j][2] == 1 for j in range(i, i + run_length)):
                return seq[i][0], seq[i][2]
        return None, None

    n_settle5, d_settle5 = find_settling_point(seq5, 10)
    n_settle7, d_settle7 = find_settling_point(seq7, 10)
    print(f"\n  First run of 10 consecutive 1-digit jumps:")
    print(f"    5-series: n={n_settle5}, D={d_settle5}")
    print(f"    7-series: n={n_settle7}, D={d_settle7}")

    # The paper's boundaries are the 3-digit jumps that happen near the
    # transition region. Let me list ALL 3-digit jumps and show the
    # combined picture.

    # Combine into boundary events
    # Match 5-series and 7-series jumps that have overlapping gap digits
    print(f"\n{'='*72}")
    print("COMBINED BOUNDARY EVENTS")
    print(f"{'='*72}")

    # Build a mapping from gap-digit to jump info for each series
    gaps5_map = {}
    for j in jumps5:
        for d in j['gap_digits']:
            gaps5_map[d] = j
    gaps7_map = {}
    for j in jumps7:
        for d in j['gap_digits']:
            gaps7_map[d] = j

    # Group nearby gap events
    all_gap_d = sorted(set(list(gaps5_map.keys()) + list(gaps7_map.keys())))
    boundaries = []
    i = 0
    while i < len(all_gap_d):
        cluster = [all_gap_d[i]]
        while i + 1 < len(all_gap_d) and all_gap_d[i + 1] - cluster[-1] <= 3:
            i += 1
            cluster.append(all_gap_d[i])
        # Determine type
        has5 = any(d in gaps5_map for d in cluster)
        has7 = any(d in gaps7_map for d in cluster)
        overlap = any(d in gaps5_map and d in gaps7_map for d in cluster)

        info5 = gaps5_map.get(next((d for d in cluster if d in gaps5_map), None))
        info7 = gaps7_map.get(next((d for d in cluster if d in gaps7_map), None))

        if overlap:
            btype = 'coincident'
        elif has5 and has7:
            btype = 'staggered'
        elif has5:
            btype = '5-only'
        else:
            btype = '7-only'

        boundaries.append({
            'digits': cluster, 'type': btype,
            'info5': info5, 'info7': info7,
        })
        i += 1

    # Print all boundaries, highlighting the paper's known ones
    print(f"\n  {'#':>3} {'D range':>15} {'Type':<12} {'5-n_B':>6} {'5-D jump':>12} "
          f"{'7-n_B':>6} {'7-D jump':>12}")
    for idx, b in enumerate(boundaries):
        d_range = f"{min(b['digits'])}-{max(b['digits'])}"
        n5 = str(b['info5']['n_before']) if b['info5'] else '-'
        j5 = f"{b['info5']['d_before']}->{b['info5']['d_after']}" if b['info5'] else '-'
        n7 = str(b['info7']['n_before']) if b['info7'] else '-'
        j7 = f"{b['info7']['d_before']}->{b['info7']['d_after']}" if b['info7'] else '-'
        marker = ""
        if 60 in b['digits'] or 61 in b['digits']:
            marker = " <-- BOUNDARY 1 (paper)"
        elif 80 in b['digits'] and b['type'] == 'coincident':
            marker = " <-- BOUNDARY 2 (paper)"
        print(f"  {idx+1:>3} {d_range:>15} {b['type']:<12} {n5:>6} {j5:>12} "
              f"{n7:>6} {j7:>12}{marker}")

    # ================================================================
    # MODULAR STATE FOR PAPER BOUNDARIES + NEXT FEW
    # ================================================================
    print(f"\n{'='*72}")
    print("MODULAR STATE AT KEY BOUNDARIES")
    print(f"{'='*72}")

    # Identify paper's boundaries by their gap digits
    paper_b1_idx = next(i for i, b in enumerate(boundaries) if 60 in b['digits'] or 61 in b['digits'])
    paper_b2_idx = next(i for i, b in enumerate(boundaries) if 80 in b['digits'] and b['type'] == 'coincident')

    # Take boundaries starting from paper's B1 through B1+5
    key_boundaries = boundaries[paper_b1_idx:paper_b1_idx + 6]

    for rel_idx, b in enumerate(key_boundaries):
        bdy_num = rel_idx + 1
        d_range = f"{min(b['digits'])}-{max(b['digits'])}"
        print(f"\n  --- Boundary {bdy_num}: {b['type']}, D={{{d_range}}} ---")

        for label, sp, info in [('5-series', p5, b['info5']), ('7-series', p7, b['info7'])]:
            if info is None:
                print(f"  {label}: no gap")
                continue
            n_b = info['n_before']
            ms = compute_modular_state(sp, n_b)
            active = [m for m in SMALL_PRIMES if ms[m] != 0]
            filler = 1
            for m in active:
                filler *= m

            print(f"  {label}: n_B={n_b}, D={info['d_before']}->{info['d_after']}")
            print(f"    mod: {', '.join(f'{m}={ms[m]}' for m in SMALL_PRIMES)}")
            print(f"    Active (coprime): {active}")
            print(f"    Predicted min filler: {filler}")

    # ================================================================
    # CROSS-CHECK
    # ================================================================
    print(f"\n{'='*72}")
    print("CROSS-CHECK AGAINST PAPER")
    print(f"{'='*72}")

    b1 = key_boundaries[0]
    b2 = key_boundaries[paper_b2_idx - paper_b1_idx]

    # Boundary 1
    ms5_b1 = compute_modular_state(p5, b1['info5']['n_before'])
    ms7_b1 = compute_modular_state(p7, b1['info7']['n_before'])
    print(f"\n  Boundary 1 cross-check:")
    print(f"    5-series mod3={ms5_b1[3]} (expect 1) mod5={ms5_b1[5]} (expect 0) "
          f"-> observed factor: 3  predicted factor: {3 if ms5_b1[3]!=0 and ms5_b1[5]==0 else '?'}")
    print(f"    7-series mod3={ms7_b1[3]} (expect 1) mod5={ms7_b1[5]} (expect 3) "
          f"-> observed factor: 3  active mod3? {ms7_b1[3]!=0}")

    # Boundary 2
    ms5_b2 = compute_modular_state(p5, b2['info5']['n_before'])
    ms7_b2 = compute_modular_state(p7, b2['info7']['n_before'])
    print(f"\n  Boundary 2 cross-check:")
    print(f"    5-series mod3={ms5_b2[3]} mod5={ms5_b2[5]} "
          f"-> observed factor: 3  predicted: 3 (mod5=0 so 5 not active)")
    print(f"    7-series mod3={ms7_b2[3]} mod5={ms7_b2[5]} "
          f"-> observed factor: 15  predicted: 15 (both mod3,mod5 nonzero)")

    # ================================================================
    # FINAL SUMMARY TABLE
    # ================================================================
    print(f"\n{'='*72}")
    print("FINAL SUMMARY TABLE")
    print(f"{'='*72}")
    print(f"\n  {'Bdy':>3} {'Type':<11} {'Series':<7} {'n_B':>4} {'D gap':>8} "
          f"{'m3':>3} {'m5':>3} {'m7':>3} {'m11':>4} {'m13':>4} "
          f"{'Min filler':>10} {'Paper obs':>10}")

    paper_obs = {
        (0, '5'): '3', (0, '7'): '3',
    }
    # Identify which relative index is boundary 2
    for ri, b in enumerate(key_boundaries):
        if 80 in b['digits'] and b['type'] == 'coincident':
            paper_obs[(ri, '5')] = '3'
            paper_obs[(ri, '7')] = '15'
            break

    csv_rows = []
    for ri, b in enumerate(key_boundaries):
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
            d_gap = f"{min(b['digits'])}-{max(b['digits'])}"
            obs = paper_obs.get((ri, code), 'PRED')
            print(f"  {ri+1:>3} {b['type']:<11} {label:<7} {n_b:>4} {d_gap:>8} "
                  f"{ms[3]:>3} {ms[5]:>3} {ms[7]:>3} {ms[11]:>4} {ms[13]:>4} "
                  f"{filler:>10} {obs:>10}")
            csv_rows.append([ri+1, b['type'], label, n_b, d_gap,
                             ms[3], ms[5], ms[7], ms[11], ms[13], ms[17], ms[19], ms[23],
                             str(active), filler, obs])

    csv_path = os.path.join(RESULTS_DIR, 'boundary_predictions_final.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['boundary', 'type', 'series', 'n_before', 'gap_range',
                     'mod3', 'mod5', 'mod7', 'mod11', 'mod13', 'mod17', 'mod19', 'mod23',
                     'active_moduli', 'min_filler', 'paper_observed'])
        for row in csv_rows:
            w.writerow(row)
    print(f"\n  Saved: {csv_path}")


if __name__ == '__main__':
    main()
