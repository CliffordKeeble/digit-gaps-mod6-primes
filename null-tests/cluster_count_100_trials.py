#!/usr/bin/env python3
"""
Cluster Count + R² Null Distribution at 200k (Adversary follow-up, Tasks 2+3)
===============================================================================

Task 2: The headline z = -2.04 for cluster count comes from 10 null trials.
With only 10 trials the std of the null mean is poorly characterised. This
script runs 100 trials to determine whether z stays near -2.0 or drifts.

Task 3: The paper claims R² = 0.979 is prime-specific but never quotes the
null R² distribution. We extract the power-law R² for each null trial that
produces >= 4 clusters and report the distribution.

Parameters: 200k scale, window=50, min_gaps=20, 100% coincidence, merge_dist=500.
Same as paper §6.2 and full_null_model.py.

SEED: trial * 137 + 42 (consistent with all previous tests).
"""
import math, random, time, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
N_TRIALS = 100
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


def fit_power_law(clusters):
    if len(clusters) < 4:
        return None, None, None
    gaps = [clusters[i + 1]['centre'] - clusters[i]['centre']
            for i in range(len(clusters) - 1)]
    centres = [(clusters[i]['centre'] + clusters[i + 1]['centre']) / 2
               for i in range(len(clusters) - 1)]
    pairs = [(c, g) for c, g in zip(centres, gaps) if c > 0 and g > 0]
    if len(pairs) < 3:
        return None, None, None
    log_c = [math.log(c) for c, _ in pairs]
    log_g = [math.log(g) for _, g in pairs]
    n = len(log_c)
    mean_x = sum(log_c) / n
    mean_y = sum(log_g) / n
    ss_xx = sum((x - mean_x) ** 2 for x in log_c)
    ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_c, log_g))
    if ss_xx == 0:
        return None, None, None
    beta = ss_xy / ss_xx
    alpha = math.exp(mean_y - beta * mean_x)
    ss_res = sum((y - (math.log(alpha) + beta * x)) ** 2 for x, y in zip(log_c, log_g))
    ss_tot = sum((y - mean_y) ** 2 for y in log_g)
    r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    se_beta = math.sqrt(ss_res / ((n - 2) * ss_xx)) if n > 2 and ss_xx > 0 else 0
    return beta, r_sq, se_beta


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


def percentile(sorted_vals, p):
    idx = int(len(sorted_vals) * p / 100)
    return sorted_vals[min(idx, len(sorted_vals) - 1)]


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    T0 = time.time()

    print("=" * 72)
    print("CLUSTER COUNT + R² NULL DISTRIBUTION (Adversary follow-up)")
    print(f"100 null trials at {CMAX:,} digits")
    print("=" * 72)

    # --- Real primes ---
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
    real_beta, real_r2, real_se = fit_power_law(real_cl)
    print(f"  Clusters: {len(real_cl)}")
    print(f"  beta = {real_beta:.4f} +/- {real_se:.4f}")
    print(f"  R2 = {real_r2:.4f}")

    # --- 100 null trials ---
    print(f"\n[3] Running {N_TRIALS} null trials...")
    null_cluster_counts = []
    null_betas = []
    null_r2s = []
    null_per_trial = []  # for CSV

    for trial in range(N_TRIALS):
        t1 = time.time()
        logs1, logs2 = generate_pseudo_primes(SIEVE_LIMIT, seed=trial * 137 + 42)
        n_null = min(len(logs1), len(logs2), n_use)
        ng1, ng2, nmax = compute_gap_arrays(logs1[:n_null], logs2[:n_null])
        ncl = find_clusters(ng1, ng2, min(CMAX, nmax))
        n_cl = len(ncl)
        null_cluster_counts.append(n_cl)

        nb, nr2, nse = fit_power_law(ncl)
        if nb is not None:
            null_betas.append(nb)
            null_r2s.append(nr2)
            null_per_trial.append((trial, n_cl, nb, nr2, nse))
        else:
            null_per_trial.append((trial, n_cl, None, None, None))

        if trial % 20 == 0 or trial == N_TRIALS - 1:
            beta_str = f"beta={nb:.4f}, R2={nr2:.4f}" if nb is not None else "too few clusters"
            print(f"  Trial {trial:3d}: {n_cl} clusters, {beta_str} [{time.time()-t1:.1f}s]")

    # === TASK 2: CLUSTER COUNT ===
    print(f"\n{'='*72}")
    print("TASK 2: CLUSTER COUNT DISTRIBUTION (100 trials)")
    print(f"{'='*72}")

    cc_sorted = sorted(null_cluster_counts)
    cc_mean = avg(null_cluster_counts)
    cc_std = std_dev(null_cluster_counts)
    z_cc = (len(real_cl) - cc_mean) / cc_std if cc_std > 0 else 0

    print(f"\n  Real-prime cluster count: {len(real_cl)}")
    print(f"  Null distribution ({N_TRIALS} trials):")
    print(f"    Mean:   {cc_mean:.2f}")
    print(f"    Std:    {cc_std:.2f}")
    print(f"    Min:    {cc_sorted[0]}")
    print(f"    Q1:     {percentile(cc_sorted, 25)}")
    print(f"    Median: {percentile(cc_sorted, 50)}")
    print(f"    Q3:     {percentile(cc_sorted, 75)}")
    print(f"    Max:    {cc_sorted[-1]}")
    print(f"\n  z-score (real vs null): {z_cc:.2f}")
    print(f"  (Paper's z with 10 trials: -2.04)")

    # How many null trials have cluster count <= real?
    n_le = sum(1 for c in null_cluster_counts if c <= len(real_cl))
    print(f"  Null trials with count <= {len(real_cl)}: {n_le}/{N_TRIALS} "
          f"= {100*n_le/N_TRIALS:.1f}%")

    # Histogram
    print(f"\n  Histogram of null cluster counts:")
    from collections import Counter
    cc_counter = Counter(null_cluster_counts)
    for count in sorted(cc_counter.keys()):
        bar = '#' * cc_counter[count]
        marker = " <-- REAL" if count == len(real_cl) else ""
        print(f"    {count:3d}: {bar} ({cc_counter[count]}){marker}")

    # === TASK 3: R² DISTRIBUTION ===
    print(f"\n{'='*72}")
    print("TASK 3: NULL R² DISTRIBUTION AT 200k (power-law fit)")
    print(f"{'='*72}")

    r2_sorted = sorted(null_r2s)
    r2_mean = avg(null_r2s)
    r2_std = std_dev(null_r2s)
    z_r2 = (real_r2 - r2_mean) / r2_std if r2_std > 0 else 0

    print(f"\n  Real-prime R²: {real_r2:.4f}")
    print(f"  Null R² distribution ({len(null_r2s)} trials with >= 4 clusters):")
    print(f"    Mean:   {r2_mean:.4f}")
    print(f"    Std:    {r2_std:.4f}")
    print(f"    Min:    {r2_sorted[0]:.4f}")
    print(f"    Q1:     {percentile(r2_sorted, 25):.4f}")
    print(f"    Median: {percentile(r2_sorted, 50):.4f}")
    print(f"    Q3:     {percentile(r2_sorted, 75):.4f}")
    print(f"    Max:    {r2_sorted[-1]:.4f}")
    print(f"\n  z-score (real R² vs null): {z_r2:.2f}")

    # How many null trials have R² >= real?
    n_ge = sum(1 for r in null_r2s if r >= real_r2)
    print(f"  Null trials with R² >= {real_r2:.4f}: {n_ge}/{len(null_r2s)} "
          f"= {100*n_ge/len(null_r2s):.1f}%")

    # Also report null beta distribution for reference
    print(f"\n  Null beta distribution (for reference):")
    b_sorted = sorted(null_betas)
    print(f"    Mean:   {avg(null_betas):.4f}")
    print(f"    Std:    {std_dev(null_betas):.4f}")
    print(f"    Min:    {b_sorted[0]:.4f}")
    print(f"    Median: {percentile(b_sorted, 50):.4f}")
    print(f"    Max:    {b_sorted[-1]:.4f}")
    z_beta = (real_beta - avg(null_betas)) / std_dev(null_betas) if std_dev(null_betas) > 0 else 0
    print(f"    z(beta): {z_beta:.2f}")

    # === COMBINED SUMMARY ===
    print(f"\n{'='*72}")
    print("COMBINED SUMMARY")
    print(f"{'='*72}")
    print(f"\n  {'Metric':<25} {'Real':>10} {'Null mean':>10} {'Null std':>10} {'z':>8}")
    print(f"  {'-'*63}")
    print(f"  {'Cluster count':<25} {len(real_cl):>10} {cc_mean:>10.2f} {cc_std:>10.2f} {z_cc:>8.2f}")
    print(f"  {'Power-law beta':<25} {real_beta:>10.4f} {avg(null_betas):>10.4f} "
          f"{std_dev(null_betas):>10.4f} {z_beta:>8.2f}")
    print(f"  {'Power-law R2':<25} {real_r2:>10.4f} {r2_mean:>10.4f} {r2_std:>10.4f} {z_r2:>8.2f}")

    # --- Save per-trial CSV ---
    csv_path = os.path.join(RESULTS_DIR, 'cluster_count_100_trials.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['trial', 'n_clusters', 'beta', 'r_squared', 'se_beta'])
        for trial, n_cl, nb, nr2, nse in null_per_trial:
            w.writerow([trial, n_cl,
                        f"{nb:.6f}" if nb is not None else '',
                        f"{nr2:.6f}" if nr2 is not None else '',
                        f"{nse:.6f}" if nse is not None else ''])
    print(f"\n  Per-trial data saved to {csv_path}")

    # --- Save summary CSV ---
    summary_path = os.path.join(RESULTS_DIR, 'cluster_r2_summary.csv')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['metric', 'real', 'null_mean', 'null_std', 'z_score',
                     'null_min', 'null_q1', 'null_median', 'null_q3', 'null_max'])
        w.writerow(['cluster_count', len(real_cl), cc_mean, cc_std, z_cc,
                     cc_sorted[0], percentile(cc_sorted, 25), percentile(cc_sorted, 50),
                     percentile(cc_sorted, 75), cc_sorted[-1]])
        w.writerow(['r_squared', real_r2, r2_mean, r2_std, z_r2,
                     r2_sorted[0], percentile(r2_sorted, 25), percentile(r2_sorted, 50),
                     percentile(r2_sorted, 75), r2_sorted[-1]])
        w.writerow(['beta', real_beta, avg(null_betas), std_dev(null_betas), z_beta,
                     b_sorted[0], percentile(b_sorted, 25), percentile(b_sorted, 50),
                     percentile(b_sorted, 75), b_sorted[-1]])
    print(f"  Summary saved to {summary_path}")

    print(f"\nTotal runtime: {time.time()-T0:.1f}s")


if __name__ == '__main__':
    main()
