#!/usr/bin/env python3
"""
Full-Scale Null Model: Primes vs Pseudo-Primes
===============================================
Optimised version: uses arrays and bisect for cluster detection.
"""
import math, random, time, sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter
from bisect import bisect_left, bisect_right


def sieve(limit):
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def compute_gap_stats(logs1, logs2, label=""):
    """Full gap and spacing analysis."""
    t0 = time.time()
    s = 0.0
    d1_set = set()
    for lg in logs1:
        s += lg
        d1_set.add(int(s) + 1)
    s = 0.0
    d2_set = set()
    for lg in logs2:
        s += lg
        d2_set.add(int(s) + 1)
    max_d = min(max(d1_set), max(d2_set))
    is_gap1 = bytearray(b'\x01') * (max_d + 1)
    is_gap2 = bytearray(b'\x01') * (max_d + 1)
    for d in d1_set:
        if d <= max_d: is_gap1[d] = 0
    for d in d2_set:
        if d <= max_d: is_gap2[d] = 0
    gc_sorted = []
    n_g1 = n_g2 = 0
    for d in range(1, max_d + 1):
        if is_gap1[d]: n_g1 += 1
        if is_gap2[d]: n_g2 += 1
        if is_gap1[d] and is_gap2[d]:
            gc_sorted.append(d)
    spacings = [gc_sorted[i+1] - gc_sorted[i] for i in range(len(gc_sorted)-1)]
    total_sp = len(spacings)
    counter = Counter(spacings)
    in_123 = sum(counter[k] for k in [1,2,3])
    pct_123 = 100.0 * in_123 / total_sp if total_sp else 0
    max_sp = max(spacings) if spacings else 0
    s1_pct = 100.0 * counter.get(1, 0) / total_sp if total_sp else 0
    s2_pct = 100.0 * counter.get(2, 0) / total_sp if total_sp else 0
    s3_pct = 100.0 * counter.get(3, 0) / total_sp if total_sp else 0
    bands = [(0, 500000), (500000, 1000000), (1000000, 1500000),
             (1500000, 2000000), (2000000, 2500000), (2500000, max_d+1)]
    band_stats = []
    for lo, hi in bands:
        if lo >= max_d: break
        hi = min(hi, max_d)
        i_lo = bisect_left(gc_sorted, lo)
        i_hi = bisect_left(gc_sorted, hi)
        band_gc = gc_sorted[i_lo:i_hi]
        if len(band_gc) < 2: continue
        band_sp = [band_gc[j+1] - band_gc[j] for j in range(len(band_gc)-1)]
        bc = Counter(band_sp)
        bt = len(band_sp)
        band_in123 = sum(bc[k] for k in [1,2,3])
        band_stats.append({
            'band': f"{lo//1000}k-{hi//1000}k", 'spacings': bt,
            'pct_123': 100.0 * band_in123 / bt if bt else 0,
            's1': 100.0 * bc.get(1,0) / bt if bt else 0,
            's2': 100.0 * bc.get(2,0) / bt if bt else 0,
            's3': 100.0 * bc.get(3,0) / bt if bt else 0,
        })
    elapsed = time.time() - t0
    return {
        'label': label, 'max_digit': max_d, 'gaps_c': len(gc_sorted),
        'coinc_pct': 100.0*len(gc_sorted)/max_d, 'n_spacings': total_sp,
        'pct_123': pct_123, 'max_spacing': max_sp,
        's1_pct': s1_pct, 's2_pct': s2_pct, 's3_pct': s3_pct,
        'spacing_counter': counter, 'band_stats': band_stats,
        'elapsed': elapsed, 'is_gap1': is_gap1, 'is_gap2': is_gap2,
        'gc_sorted': gc_sorted,
    }


def find_clusters_fast(is_gap1, is_gap2, max_d, window=50, min_gaps=20, merge_dist=500):
    """Optimised cluster detection using sliding window on arrays."""
    sync_starts = []
    step = 10
    for start in range(1, max_d - window + 1, step):
        end = start + window
        if end > max_d: break
        cb = ca = 0
        for d in range(start, end):
            g1, g2 = is_gap1[d], is_gap2[d]
            if g1 and g2: cb += 1; ca += 1
            elif g1 or g2: ca += 1
        if ca >= min_gaps and cb == ca:
            sync_starts.append(start)
    if not sync_starts: return []
    clusters = []
    c_start = sync_starts[0]
    c_end = sync_starts[0] + window
    for s in sync_starts[1:]:
        if s <= c_end + merge_dist:
            c_end = s + window
        else:
            clusters.append({'centre': (c_start+c_end)//2, 'span': c_end-c_start})
            c_start, c_end = s, s + window
    clusters.append({'centre': (c_start+c_end)//2, 'span': c_end-c_start})
    return clusters


def fit_power_law(clusters):
    if len(clusters) < 4: return None, None, None
    gaps = [clusters[i+1]['centre'] - clusters[i]['centre']
            for i in range(len(clusters)-1)]
    centres = [(clusters[i]['centre'] + clusters[i+1]['centre']) / 2
               for i in range(len(clusters)-1)]
    pairs = [(c, g) for c, g in zip(centres, gaps) if c > 0 and g > 0]
    if len(pairs) < 3: return None, None, None
    log_c = [math.log(c) for c, _ in pairs]
    log_g = [math.log(g) for _, g in pairs]
    n = len(log_c)
    mean_x, mean_y = sum(log_c)/n, sum(log_g)/n
    ss_xx = sum((x-mean_x)**2 for x in log_c)
    ss_xy = sum((x-mean_x)*(y-mean_y) for x, y in zip(log_c, log_g))
    if ss_xx == 0: return None, None, None
    beta = ss_xy / ss_xx
    alpha = math.exp(mean_y - beta * mean_x)
    ss_res = sum((y-(math.log(alpha)+beta*x))**2 for x, y in zip(log_c, log_g))
    ss_tot = sum((y-mean_y)**2 for y in log_g)
    r_sq = 1 - ss_res/ss_tot if ss_tot > 0 else 0
    se_beta = math.sqrt(ss_res/((n-2)*ss_xx)) if n > 2 and ss_xx > 0 else 0
    return beta, r_sq, se_beta


def generate_pseudo_primes(limit, seed):
    rng = random.Random(seed)
    c1_logs, c2_logs = [], []
    for n in range(5, limit):
        if rng.random() < 1.0 / math.log(n):
            lg = math.log10(n)
            if rng.random() < 0.5: c1_logs.append(lg)
            else: c2_logs.append(lg)
    return c1_logs, c2_logs


def avg(vals): return sum(vals)/len(vals) if vals else 0


def std_dev(vals):
    if len(vals) < 2: return 0
    m = avg(vals)
    return math.sqrt(sum((v-m)**2 for v in vals) / (len(vals)-1))


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
def main():
    print("=" * 72)
    print("FULL-SCALE NULL MODEL TEST")
    print("Primes vs Pseudo-Primes — Spacing + Cluster Analysis")
    print("=" * 72)

    T0 = time.time()

    print("\n[1] Sieving primes to 15,000,000...")
    primes = sieve(15_000_000)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    p5_logs = [math.log10(p) for p in p5]
    p7_logs = [math.log10(p) for p in p7]
    n_use = min(len(p5_logs), len(p7_logs))
    print(f"  5-series: {len(p5):,}, 7-series: {len(p7):,}")

    print("\n[2] Real prime gap statistics...")
    real = compute_gap_stats(p5_logs[:n_use], p7_logs[:n_use], "REAL PRIMES")

    print(f"\n  — REAL PRIMES —")
    print(f"  Max digit: {real['max_digit']:,}")
    print(f"  Coincident gaps: {real['gaps_c']:,} ({real['coinc_pct']:.1f}%)")
    print(f"  Spacings: {real['n_spacings']:,}")
    print(f"  In {{1,2,3}}: {real['pct_123']:.4f}%")
    print(f"  Max spacing: {real['max_spacing']}")
    print(f"  s=1: {real['s1_pct']:.1f}% s=2: {real['s2_pct']:.1f}% s=3: {real['s3_pct']:.1f}%")
    outside = {k: v for k, v in real['spacing_counter'].items() if k > 3}
    print(f"  Spacings > 3: {outside if outside else 'NONE'}")

    print(f"\n  Band-by-band:")
    for b in real['band_stats']:
        print(f"  {b['band']:<15} {b['spacings']:>8,} {b['pct_123']:>7.2f}%"
              f" {b['s1']:>6.1f}% {b['s2']:>6.1f}% {b['s3']:>6.1f}%")

    N_TRIALS = 10
    print(f"\n[3] Running {N_TRIALS} null model trials...")
    null_results = []
    for trial in range(N_TRIALS):
        t1 = time.time()
        logs1, logs2 = generate_pseudo_primes(15_000_000, seed=trial*137+42)
        n_null = min(len(logs1), len(logs2), n_use)
        nr = compute_gap_stats(logs1[:n_null], logs2[:n_null], f"NULL {trial}")
        null_results.append(nr)
        print(f"  Trial {trial:2d}: {{1,2,3}}={nr['pct_123']:>7.3f}%"
              f"  max_sp={nr['max_spacing']:>3d}"
              f"  s1={nr['s1_pct']:.0f}% s2={nr['s2_pct']:.0f}% s3={nr['s3_pct']:.0f}%"
              f"  [{time.time()-t1:.1f}s]")

    print(f"\n{'='*72}")
    print("SPACING COMPARISON")
    print(f"{'='*72}")

    metrics = [
        ('In {1,2,3}', real['pct_123'], [r['pct_123'] for r in null_results], '%'),
        ('Max spacing', real['max_spacing'], [r['max_spacing'] for r in null_results], ''),
        ('s=1 freq', real['s1_pct'], [r['s1_pct'] for r in null_results], '%'),
        ('s=2 freq', real['s2_pct'], [r['s2_pct'] for r in null_results], '%'),
        ('s=3 freq', real['s3_pct'], [r['s3_pct'] for r in null_results], '%'),
        ('Coinc gap %', real['coinc_pct'], [r['coinc_pct'] for r in null_results], '%'),
    ]
    for name, rval, nvals, unit in metrics:
        print(f"  {name:<25} {rval:>11.3f}{unit} {avg(nvals):>11.3f}{unit}"
              f" {std_dev(nvals):>9.3f}")

    CMAX = 200000
    print(f"\n{'='*72}")
    print(f"[4] CLUSTER ANALYSIS (first {CMAX:,} digits)")
    print(f"{'='*72}")

    real_cl = find_clusters_fast(real['is_gap1'], real['is_gap2'],
                                 min(CMAX, real['max_digit']))
    real_beta, real_r2, real_se = fit_power_law(real_cl)
    print(f"  Real: {len(real_cl)} clusters")
    if real_beta is not None:
        print(f"  β = {real_beta:.4f} ± {real_se:.4f} (R² = {real_r2:.3f})")

    null_cls, null_betas = [], []
    for trial, nr in enumerate(null_results):
        ncl = find_clusters_fast(nr['is_gap1'], nr['is_gap2'],
                                  min(CMAX, nr['max_digit']))
        null_cls.append(len(ncl))
        nb, nr2, nse = fit_power_law(ncl)
        if nb is not None: null_betas.append(nb)
        print(f"  Null {trial:2d}: {len(ncl)} clusters" +
              (f", β = {nb:.4f}" if nb is not None else ""))

    if null_cls and std_dev(null_cls) > 0:
        z = (len(real_cl) - avg(null_cls)) / std_dev(null_cls)
        print(f"\n  Cluster count z-score: {z:.2f}")

    if real_beta: print(f"  ln(2)/ln(3) = {math.log(2)/math.log(3):.4f}")

    print(f"\n{'='*72}")
    print("SENSITIVITY (real primes)")
    print(f"{'='*72}")
    for win in [30, 40, 50, 60, 70]:
        for mg in [10, 15, 20]:
            cl = find_clusters_fast(real['is_gap1'], real['is_gap2'],
                                    min(CMAX, real['max_digit']),
                                    window=win, min_gaps=mg)
            b, r2, se = fit_power_law(cl)
            if b is not None:
                print(f"  win={win:3d} min={mg:2d}: {len(cl):3d} clusters"
                      f"  β={b:.4f}±{se:.4f} R²={r2:.3f}")

    print(f"\nTotal runtime: {time.time()-T0:.1f}s")


if __name__ == '__main__':
    main()
