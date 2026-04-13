#!/usr/bin/env python3
"""
JUMP/PAIR Heartbeat Null Test (Section 5.3)
=============================================

The paper observes that inter-cluster gap ratios alternate between:
  - JUMP: ratio > 1.5 (large gap establishing a new scale)
  - PAIR: ratio ~ 0.99 (near-identical echo)

Specific examples from the paper:
  (10,642 / 10,282) ratio 0.97
  (17,972 / 17,861) ratio 0.99
  (54,801 / 54,323) ratio 0.99
  (137,148 / 135,838) ratio 0.99

The paper reports 44% of consecutive gap ratios show this pattern.

This test asks: does the alternating JUMP/PAIR pattern occur in null-model
cluster sequences too, or is it prime-specific?

METHOD:
  1. Detect synchronisation clusters (same algorithm as full_null_model.py)
  2. Compute consecutive inter-cluster gaps
  3. Compute ratios of consecutive gaps: r_i = gap_{i+1} / gap_i
  4. Classify each ratio as JUMP (> threshold_jump), PAIR (within threshold_pair
     of 1.0), or OTHER
  5. Count alternating JUMP-PAIR sequences
  6. Compare real primes to null model

We test sensitivity to:
  - PAIR threshold (how close to 1.0 counts as a "pair")
  - JUMP threshold (how large counts as a "jump")
  - Cluster detection parameters (window, min_gaps, merge_dist)

SEED: null trials use seed = trial * 137 + 42 (matching full_null_model.py).
"""
import math, random, time, sys, csv, os
from collections import Counter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
N_TRIALS = 20  # More trials for better null statistics
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def sieve(limit):
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def compute_gap_arrays(logs1, logs2):
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


def analyze_jump_pair(clusters, jump_thresh=1.5, pair_lo=0.85, pair_hi=1.15):
    """
    Analyze inter-cluster gaps for JUMP/PAIR alternation.

    Returns dict with:
      - gaps: list of inter-cluster gaps
      - ratios: list of consecutive gap ratios
      - pair_count: number of ratios in [pair_lo, pair_hi]
      - jump_count: number of ratios > jump_thresh or < 1/jump_thresh
      - alternation_count: number of JUMP immediately followed by PAIR (or vice versa)
      - pair_fraction: fraction of ratios that are "pairs"
    """
    if len(clusters) < 3:
        return None

    gaps = [clusters[i + 1]['centre'] - clusters[i]['centre']
            for i in range(len(clusters) - 1)]

    if len(gaps) < 2:
        return None

    ratios = [gaps[i + 1] / gaps[i] if gaps[i] > 0 else float('inf')
              for i in range(len(gaps) - 1)]

    pair_count = sum(1 for r in ratios if pair_lo <= r <= pair_hi)
    jump_count = sum(1 for r in ratios if r > jump_thresh or r < 1.0 / jump_thresh)

    # Count JUMP->PAIR and PAIR->JUMP alternations
    alternation_count = 0
    for i in range(len(ratios) - 1):
        r1, r2 = ratios[i], ratios[i + 1]
        is_jump1 = r1 > jump_thresh or r1 < 1.0 / jump_thresh
        is_pair1 = pair_lo <= r1 <= pair_hi
        is_jump2 = r2 > jump_thresh or r2 < 1.0 / jump_thresh
        is_pair2 = pair_lo <= r2 <= pair_hi
        if (is_jump1 and is_pair2) or (is_pair1 and is_jump2):
            alternation_count += 1

    n_ratios = len(ratios)
    return {
        'n_gaps': len(gaps),
        'n_ratios': n_ratios,
        'ratios': ratios,
        'pair_count': pair_count,
        'jump_count': jump_count,
        'alternation_count': alternation_count,
        'pair_fraction': pair_count / n_ratios if n_ratios > 0 else 0,
        'jump_fraction': jump_count / n_ratios if n_ratios > 0 else 0,
        'alternation_fraction': alternation_count / max(n_ratios - 1, 1),
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
    print("JUMP/PAIR HEARTBEAT NULL TEST (Section 5.3)")
    print("=" * 72)

    # --- Real primes ---
    print("\n[1] Sieving primes...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    p5_logs = [math.log10(p) for p in p5]
    p7_logs = [math.log10(p) for p in p7]
    n_use = min(len(p5_logs), len(p7_logs))

    print("\n[2] Computing clusters for real primes...")
    is_gap1, is_gap2, max_d = compute_gap_arrays(p5_logs[:n_use], p7_logs[:n_use])

    # Test at multiple scales (200k as in paper, plus full range)
    scales = [200000, max_d]
    scale_labels = ['200k (paper)', 'full (3.25M)']

    for scale, label in zip(scales, scale_labels):
        print(f"\n  --- Scale: {label} ---")
        clusters = find_clusters(is_gap1, is_gap2, min(scale, max_d))
        print(f"  Clusters found: {len(clusters)}")

        if len(clusters) >= 3:
            gaps = [clusters[i + 1]['centre'] - clusters[i]['centre']
                    for i in range(len(clusters) - 1)]
            print(f"  Inter-cluster gaps: {gaps}")

            result = analyze_jump_pair(clusters)
            if result:
                print(f"  Ratios: {[f'{r:.3f}' for r in result['ratios']]}")
                print(f"  Pair fraction: {result['pair_fraction']:.3f}"
                      f" ({result['pair_count']}/{result['n_ratios']})")
                print(f"  Jump fraction: {result['jump_fraction']:.3f}"
                      f" ({result['jump_count']}/{result['n_ratios']})")
                print(f"  Alternation fraction: {result['alternation_fraction']:.3f}"
                      f" ({result['alternation_count']}/{result['n_ratios']-1})")

    # --- Sensitivity to PAIR threshold ---
    print(f"\n{'='*72}")
    print("SENSITIVITY TO PAIR THRESHOLD (real primes, full scale)")
    print(f"{'='*72}")
    clusters_full = find_clusters(is_gap1, is_gap2, max_d)
    pair_thresholds = [
        (0.90, 1.10), (0.93, 1.07), (0.95, 1.05),
        (0.97, 1.03), (0.98, 1.02), (0.99, 1.01),
    ]
    real_results_by_thresh = {}
    print(f"  {'Pair range':<16} {'Pair%':>8} {'Jump%':>8} {'Alt%':>8}")
    for plo, phi in pair_thresholds:
        r = analyze_jump_pair(clusters_full, pair_lo=plo, pair_hi=phi)
        if r:
            real_results_by_thresh[(plo, phi)] = r
            print(f"  [{plo:.2f}, {phi:.2f}]   {r['pair_fraction']*100:>7.1f}% "
                  f"{r['jump_fraction']*100:>7.1f}% {r['alternation_fraction']*100:>7.1f}%")

    # --- Null model ---
    print(f"\n{'='*72}")
    print(f"[3] Running {N_TRIALS} null model trials...")
    print(f"{'='*72}")

    null_pair_fracs = {k: [] for k in real_results_by_thresh.keys()}
    null_alt_fracs = {k: [] for k in real_results_by_thresh.keys()}
    null_n_clusters = []

    # Also collect null ratios at default threshold for distribution comparison
    null_all_ratios = []

    for trial in range(N_TRIALS):
        t1 = time.time()
        logs1, logs2 = generate_pseudo_primes(SIEVE_LIMIT, seed=trial * 137 + 42)
        n_null = min(len(logs1), len(logs2), n_use)
        ng1, ng2, nmax = compute_gap_arrays(logs1[:n_null], logs2[:n_null])

        ncl = find_clusters(ng1, ng2, nmax)
        null_n_clusters.append(len(ncl))

        for plo, phi in pair_thresholds:
            r = analyze_jump_pair(ncl, pair_lo=plo, pair_hi=phi)
            if r:
                null_pair_fracs[(plo, phi)].append(r['pair_fraction'])
                null_alt_fracs[(plo, phi)].append(r['alternation_fraction'])
                if (plo, phi) == (0.90, 1.10):
                    null_all_ratios.extend(r['ratios'])

        elapsed = time.time() - t1
        print(f"  Trial {trial:2d}: {len(ncl)} clusters [{elapsed:.1f}s]")

    # --- Comparison ---
    print(f"\n{'='*72}")
    print("JUMP/PAIR COMPARISON: REAL vs NULL")
    print(f"{'='*72}")
    print(f"  {'Pair range':<16} {'Real pair%':>10} {'Null mean%':>11} {'Null std%':>10} "
          f"{'z(pair)':>8}  {'Real alt%':>10} {'Null mean%':>11} {'z(alt)':>8}")

    for plo, phi in pair_thresholds:
        rr = real_results_by_thresh.get((plo, phi))
        if not rr:
            continue
        npf = null_pair_fracs[(plo, phi)]
        naf = null_alt_fracs[(plo, phi)]
        if len(npf) < 2:
            continue
        npm = avg(npf)
        nps = std_dev(npf)
        nam = avg(naf)
        nas = std_dev(naf)
        zp = (rr['pair_fraction'] - npm) / nps if nps > 0 else 0
        za = (rr['alternation_fraction'] - nam) / nas if nas > 0 else 0
        print(f"  [{plo:.2f}, {phi:.2f}]   {rr['pair_fraction']*100:>9.1f}% "
              f"{npm*100:>10.1f}% {nps*100:>9.1f}%  {zp:>7.2f}  "
              f"{rr['alternation_fraction']*100:>9.1f}% {nam*100:>10.1f}%  {za:>7.2f}")

    # --- Ratio distribution comparison ---
    print(f"\n{'='*72}")
    print("RATIO DISTRIBUTION (full scale, default thresholds)")
    print(f"{'='*72}")
    real_r = analyze_jump_pair(clusters_full)
    if real_r:
        real_ratios = real_r['ratios']
        print(f"  Real primes: {len(real_ratios)} ratios")
        print(f"    Mean: {avg(real_ratios):.3f}")
        print(f"    Std:  {std_dev(real_ratios):.3f}")
        print(f"    Min:  {min(real_ratios):.3f}")
        print(f"    Max:  {max(real_ratios):.3f}")
        # Bin the ratios
        bins = [(0, 0.5), (0.5, 0.75), (0.75, 0.9), (0.9, 1.1),
                (1.1, 1.25), (1.25, 1.5), (1.5, 2.0), (2.0, float('inf'))]
        print(f"\n    {'Bin':<15} {'Real count':>12} {'Real%':>8}")
        for lo, hi in bins:
            rc = sum(1 for r in real_ratios if lo <= r < hi)
            label = f"[{lo:.1f}, {hi:.1f})" if hi < float('inf') else f"[{lo:.1f}, inf)"
            print(f"    {label:<15} {rc:>12} {100*rc/len(real_ratios):>7.1f}%")

    if null_all_ratios:
        print(f"\n  Null model: {len(null_all_ratios)} ratios across {N_TRIALS} trials")
        print(f"    Mean: {avg(null_all_ratios):.3f}")
        print(f"    Std:  {std_dev(null_all_ratios):.3f}")
        print(f"\n    {'Bin':<15} {'Null count':>12} {'Null%':>8}")
        for lo, hi in bins:
            nc = sum(1 for r in null_all_ratios if lo <= r < hi)
            label = f"[{lo:.1f}, {hi:.1f})" if hi < float('inf') else f"[{lo:.1f}, inf)"
            print(f"    {label:<15} {nc:>12} {100*nc/len(null_all_ratios):>7.1f}%")

    # --- Save CSV ---
    csv_path = os.path.join(RESULTS_DIR, 'jump_pair_results.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['pair_lo', 'pair_hi', 'real_pair_frac', 'null_pair_mean',
                     'null_pair_std', 'z_pair', 'real_alt_frac', 'null_alt_mean',
                     'null_alt_std', 'z_alt'])
        for plo, phi in pair_thresholds:
            rr = real_results_by_thresh.get((plo, phi))
            if not rr:
                continue
            npf = null_pair_fracs[(plo, phi)]
            naf = null_alt_fracs[(plo, phi)]
            if len(npf) < 2:
                continue
            npm, nps = avg(npf), std_dev(npf)
            nam, nas = avg(naf), std_dev(naf)
            zp = (rr['pair_fraction'] - npm) / nps if nps > 0 else ''
            za = (rr['alternation_fraction'] - nam) / nas if nas > 0 else ''
            w.writerow([plo, phi, rr['pair_fraction'], npm, nps, zp,
                        rr['alternation_fraction'], nam, nas, za])
    print(f"\n  Results saved to {csv_path}")

    print(f"\nTotal runtime: {time.time()-T0:.1f}s")


if __name__ == '__main__':
    main()
