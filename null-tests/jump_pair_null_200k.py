#!/usr/bin/env python3
"""
JUMP/PAIR Null Test at 200k Scale (Adversary follow-up, Task 1)
================================================================

The previous full-scale test (46 ratios, 20 trials) gave z = -1.62 at
[0.90, 1.10] and the paper called JUMP/PAIR a "small-sample artefact."
But the original observation was at 200k scale (11 ratios from 13 clusters).

Mr Adversary correctly notes: we need to test whether 11-ratio null
trials at 200k *routinely* produce 40-50% pair fractions before calling
the observation an artefact. If they don't, JUMP/PAIR could be a real
bounded finite-scale phenomenon (like the power law at 200k).

METHOD: 50 null-model trials at 200k scale. For each: detect clusters
(same parameters), extract ~11 inter-cluster gap ratios, compute pair
fraction at four thresholds. Compare to real-prime 200k value.

Real-prime 200k values (from previous pass):
  Pair fraction at [0.90, 1.10]: 45.5% (5/11 ratios)
  Alternation fraction: 50.0% (5/10 consecutive pairs)

SEED: trial * 137 + 42 (consistent with all previous tests).
"""
import math, random, time, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
N_TRIALS = 50
CMAX = 200_000
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def sieve(limit):
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def compute_gap_arrays(logs1, logs2, max_limit=None):
    d1 = set()
    s = 0.0
    for lg in logs1:
        s += lg
        d1.add(int(s) + 1)
    d2 = set()
    s = 0.0
    for lg in logs2:
        s += lg
        d2.add(int(s) + 1)
    max_d = min(max(d1), max(d2))
    if max_limit:
        max_d = min(max_d, max_limit)
    is_gap1 = bytearray(b'\x01') * (max_d + 1)
    is_gap2 = bytearray(b'\x01') * (max_d + 1)
    for d in d1:
        if d <= max_d: is_gap1[d] = 0
    for d in d2:
        if d <= max_d: is_gap2[d] = 0
    return is_gap1, is_gap2, max_d


def find_clusters(is_gap1, is_gap2, max_d, window=50, min_gaps=20, merge_dist=500):
    sync_starts = []
    step = 10
    for start in range(1, max_d - window + 1, step):
        end = start + window
        if end > max_d: break
        cb = ca = 0
        for d in range(start, end):
            g1, g2 = is_gap1[d], is_gap2[d]
            if g1 and g2:
                cb += 1; ca += 1
            elif g1 or g2:
                ca += 1
        if ca >= min_gaps and cb == ca:
            sync_starts.append(start)
    if not sync_starts:
        return []
    clusters = []
    c_start = sync_starts[0]
    c_end = sync_starts[0] + window
    for s in sync_starts[1:]:
        if s <= c_end + merge_dist:
            c_end = s + window
        else:
            clusters.append({'centre': (c_start + c_end) // 2, 'span': c_end - c_start})
            c_start, c_end = s, s + window
    clusters.append({'centre': (c_start + c_end) // 2, 'span': c_end - c_start})
    return clusters


def analyze_jump_pair(clusters, pair_lo=0.90, pair_hi=1.10, jump_thresh=1.5):
    if len(clusters) < 3:
        return None
    gaps = [clusters[i + 1]['centre'] - clusters[i]['centre']
            for i in range(len(clusters) - 1)]
    if len(gaps) < 2:
        return None
    ratios = [gaps[i + 1] / gaps[i] if gaps[i] > 0 else float('inf')
              for i in range(len(gaps) - 1)]
    n_ratios = len(ratios)
    pair_count = sum(1 for r in ratios if pair_lo <= r <= pair_hi)
    jump_count = sum(1 for r in ratios if r > jump_thresh or r < 1.0 / jump_thresh)
    # Alternation: JUMP followed by PAIR or vice versa
    alt_count = 0
    for i in range(len(ratios) - 1):
        r1, r2 = ratios[i], ratios[i + 1]
        j1 = r1 > jump_thresh or r1 < 1.0 / jump_thresh
        p1 = pair_lo <= r1 <= pair_hi
        j2 = r2 > jump_thresh or r2 < 1.0 / jump_thresh
        p2 = pair_lo <= r2 <= pair_hi
        if (j1 and p2) or (p1 and j2):
            alt_count += 1
    return {
        'n_ratios': n_ratios,
        'pair_count': pair_count,
        'pair_frac': pair_count / n_ratios if n_ratios > 0 else 0,
        'jump_count': jump_count,
        'alt_count': alt_count,
        'alt_frac': alt_count / max(n_ratios - 1, 1),
    }


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


def avg(vals):
    return sum(vals) / len(vals) if vals else 0


def std_dev(vals):
    if len(vals) < 2:
        return 0
    m = avg(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    T0 = time.time()

    print("=" * 72)
    print("JUMP/PAIR NULL TEST AT 200k SCALE (Adversary follow-up)")
    print(f"50 null trials, cluster detection at {CMAX:,} digits")
    print("=" * 72)

    # --- Real primes at 200k ---
    print("\n[1] Sieving primes...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    p5_logs = [math.log10(p) for p in p5]
    p7_logs = [math.log10(p) for p in p7]
    n_use = min(len(p5_logs), len(p7_logs))

    print("\n[2] Real primes at 200k...")
    is_gap1, is_gap2, max_d = compute_gap_arrays(p5_logs[:n_use], p7_logs[:n_use])
    real_cl = find_clusters(is_gap1, is_gap2, min(CMAX, max_d))
    print(f"  Clusters: {len(real_cl)}")

    thresholds = [(0.90, 1.10), (0.95, 1.05), (0.97, 1.03), (0.99, 1.01)]
    real_results = {}
    print(f"\n  Real-prime 200k JUMP/PAIR:")
    print(f"  {'Pair range':<16} {'Pair%':>8} {'n_pair':>8} {'n_ratios':>10} {'Alt%':>8}")
    for plo, phi in thresholds:
        r = analyze_jump_pair(real_cl, pair_lo=plo, pair_hi=phi)
        if r:
            real_results[(plo, phi)] = r
            print(f"  [{plo:.2f}, {phi:.2f}]   {r['pair_frac']*100:>7.1f}% "
                  f"{r['pair_count']:>8} {r['n_ratios']:>10} {r['alt_frac']*100:>7.1f}%")

    # --- Null model at 200k ---
    print(f"\n[3] Running {N_TRIALS} null trials at 200k scale...")
    null_data = {k: {'pair_fracs': [], 'alt_fracs': [], 'n_clusters': [],
                     'n_ratios': []} for k in thresholds}

    for trial in range(N_TRIALS):
        t1 = time.time()
        logs1, logs2 = generate_pseudo_primes(SIEVE_LIMIT, seed=trial * 137 + 42)
        n_null = min(len(logs1), len(logs2), n_use)
        ng1, ng2, nmax = compute_gap_arrays(logs1[:n_null], logs2[:n_null])
        ncl = find_clusters(ng1, ng2, min(CMAX, nmax))
        n_cl = len(ncl)

        for plo, phi in thresholds:
            r = analyze_jump_pair(ncl, pair_lo=plo, pair_hi=phi)
            if r:
                null_data[(plo, phi)]['pair_fracs'].append(r['pair_frac'])
                null_data[(plo, phi)]['alt_fracs'].append(r['alt_frac'])
                null_data[(plo, phi)]['n_clusters'].append(n_cl)
                null_data[(plo, phi)]['n_ratios'].append(r['n_ratios'])

        if trial % 10 == 0 or trial == N_TRIALS - 1:
            print(f"  Trial {trial:2d}: {n_cl} clusters [{time.time()-t1:.1f}s]")

    # --- Comparison ---
    print(f"\n{'='*72}")
    print("COMPARISON: REAL PRIMES vs NULL AT 200k SCALE")
    print(f"{'='*72}")

    print(f"\n  Null cluster counts at 200k: "
          f"mean={avg([len(find_clusters(ng1, ng2, CMAX)) for _ in [0]]):.1f}")
    # Use the data we already collected
    nc_vals = null_data[thresholds[0]]['n_clusters']
    print(f"  Null clusters (from {len(nc_vals)} valid trials): "
          f"mean={avg(nc_vals):.1f} +/- {std_dev(nc_vals):.1f}, "
          f"range=[{min(nc_vals)}, {max(nc_vals)}]")
    nr_vals = null_data[thresholds[0]]['n_ratios']
    print(f"  Null n_ratios: mean={avg(nr_vals):.1f} +/- {std_dev(nr_vals):.1f}")

    print(f"\n  {'Pair range':<16} {'Real pair%':>10} {'Null mean%':>11} {'Null std%':>10} "
          f"{'z(pair)':>8}  {'Real alt%':>10} {'Null alt mean%':>15} {'z(alt)':>8}")

    for plo, phi in thresholds:
        rr = real_results.get((plo, phi))
        if not rr:
            continue
        nd = null_data[(plo, phi)]
        pf = nd['pair_fracs']
        af = nd['alt_fracs']
        if len(pf) < 2:
            continue
        pm, ps = avg(pf), std_dev(pf)
        am, as_ = avg(af), std_dev(af)
        zp = (rr['pair_frac'] - pm) / ps if ps > 0 else 0
        za = (rr['alt_frac'] - am) / as_ if as_ > 0 else 0
        print(f"  [{plo:.2f}, {phi:.2f}]   {rr['pair_frac']*100:>9.1f}% "
              f"{pm*100:>10.1f}% {ps*100:>9.1f}%  {zp:>7.2f}  "
              f"{rr['alt_frac']*100:>9.1f}% {am*100:>14.1f}%  {za:>7.2f}")

    # --- Null pair-fraction distribution detail ---
    print(f"\n  Null pair-fraction distribution at [0.90, 1.10]:")
    pf_dist = null_data[(0.90, 1.10)]['pair_fracs']
    pf_pcts = sorted([x * 100 for x in pf_dist])
    print(f"    N trials with valid data: {len(pf_pcts)}")
    print(f"    Min: {pf_pcts[0]:.1f}%")
    print(f"    Q1:  {pf_pcts[len(pf_pcts)//4]:.1f}%")
    print(f"    Median: {pf_pcts[len(pf_pcts)//2]:.1f}%")
    print(f"    Q3:  {pf_pcts[3*len(pf_pcts)//4]:.1f}%")
    print(f"    Max: {pf_pcts[-1]:.1f}%")
    # Count how many null trials have pair% >= real
    real_pf = real_results[(0.90, 1.10)]['pair_frac'] * 100
    n_ge = sum(1 for x in pf_pcts if x >= real_pf)
    print(f"    Null trials with pair% >= real ({real_pf:.1f}%): "
          f"{n_ge}/{len(pf_pcts)} = {100*n_ge/len(pf_pcts):.1f}%")

    # --- Save CSV ---
    csv_path = os.path.join(RESULTS_DIR, 'jump_pair_200k_results.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['pair_lo', 'pair_hi', 'real_pair_frac', 'null_pair_mean',
                     'null_pair_std', 'z_pair', 'real_alt_frac', 'null_alt_mean',
                     'null_alt_std', 'z_alt', 'n_valid_trials'])
        for plo, phi in thresholds:
            rr = real_results.get((plo, phi))
            nd = null_data[(plo, phi)]
            pf = nd['pair_fracs']
            af = nd['alt_fracs']
            if not rr or len(pf) < 2:
                continue
            pm, ps = avg(pf), std_dev(pf)
            am, as_ = avg(af), std_dev(af)
            zp = (rr['pair_frac'] - pm) / ps if ps > 0 else 0
            za = (rr['alt_frac'] - am) / as_ if as_ > 0 else 0
            w.writerow([plo, phi, rr['pair_frac'], pm, ps, zp,
                        rr['alt_frac'], am, as_, za, len(pf)])
    print(f"\n  Results saved to {csv_path}")
    print(f"\nTotal runtime: {time.time()-T0:.1f}s")


if __name__ == '__main__':
    main()
