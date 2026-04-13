#!/usr/bin/env python3
"""
Power-Law Full-Scale Refit (Follow-up to findings.md §4 flag)
==============================================================

The paper's β = 0.637 ± 0.029 (R² = 0.979) is fitted to 12 data points
from 13 clusters at the 200k-digit scale. This script refits the same
log-log regression at full scale (3.25M digits, ~48 clusters, ~47 gaps)
and compares.

Method: identical to paper §5.2 — OLS regression of log(gap) on log(centre),
where gap = distance between consecutive cluster centres, and centre =
midpoint of the two clusters bounding each gap.

Also: sensitivity to trimming extreme points, and null-model comparison
at full scale (reusing the same null framework).
"""
import math, random, time, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
N_TRIALS = 20
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


def fit_power_law(clusters, skip_first=0, skip_last=0):
    """
    Log-log OLS regression: log(gap) = log(alpha) + beta * log(centre).
    Returns (beta, r_sq, se_beta, alpha, n_points) or (None,...) if insufficient data.
    Optional: skip_first / skip_last points for trimmed fits.
    """
    if len(clusters) < 4:
        return None, None, None, None, 0
    gaps = [clusters[i + 1]['centre'] - clusters[i]['centre']
            for i in range(len(clusters) - 1)]
    centres = [(clusters[i]['centre'] + clusters[i + 1]['centre']) / 2
               for i in range(len(clusters) - 1)]
    pairs = [(c, g) for c, g in zip(centres, gaps) if c > 0 and g > 0]
    if skip_first > 0:
        pairs = pairs[skip_first:]
    if skip_last > 0 and skip_last < len(pairs):
        pairs = pairs[:-skip_last]
    if len(pairs) < 3:
        return None, None, None, None, 0
    log_c = [math.log(c) for c, _ in pairs]
    log_g = [math.log(g) for _, g in pairs]
    n = len(log_c)
    mean_x = sum(log_c) / n
    mean_y = sum(log_g) / n
    ss_xx = sum((x - mean_x) ** 2 for x in log_c)
    ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_c, log_g))
    if ss_xx == 0:
        return None, None, None, None, 0
    beta = ss_xy / ss_xx
    alpha = math.exp(mean_y - beta * mean_x)
    ss_res = sum((y - (math.log(alpha) + beta * x)) ** 2 for x, y in zip(log_c, log_g))
    ss_tot = sum((y - mean_y) ** 2 for y in log_g)
    r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    se_beta = math.sqrt(ss_res / ((n - 2) * ss_xx)) if n > 2 and ss_xx > 0 else 0
    return beta, r_sq, se_beta, alpha, n


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
    print("POWER-LAW FULL-SCALE REFIT")
    print("=" * 72)

    # --- Sieve and compute ---
    print("\n[1] Sieving primes...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    p5_logs = [math.log10(p) for p in p5]
    p7_logs = [math.log10(p) for p in p7]
    n_use = min(len(p5_logs), len(p7_logs))

    print("\n[2] Computing gap arrays...")
    is_gap1, is_gap2, max_d = compute_gap_arrays(p5_logs[:n_use], p7_logs[:n_use])
    print(f"  Max digit: {max_d:,}")

    # --- Clusters at 200k (paper scale) ---
    print("\n[3] Cluster detection...")
    cl_200k = find_clusters(is_gap1, is_gap2, min(200000, max_d))
    cl_full = find_clusters(is_gap1, is_gap2, max_d)
    print(f"  200k scale: {len(cl_200k)} clusters")
    print(f"  Full scale: {len(cl_full)} clusters")

    # --- Fit at 200k (reproduce paper) ---
    print(f"\n{'='*72}")
    print("[4] POWER-LAW FIT COMPARISON")
    print(f"{'='*72}")

    b200, r200, se200, a200, n200 = fit_power_law(cl_200k)
    bfull, rfull, sefull, afull, nfull = fit_power_law(cl_full)

    print(f"\n  {'Scale':<20} {'n':>4} {'beta':>10} {'se(beta)':>10} {'R2':>8} {'alpha':>10}")
    print(f"  {'-'*62}")
    if b200 is not None:
        print(f"  {'200k (paper)':<20} {n200:>4} {b200:>10.4f} {se200:>10.4f} {r200:>8.4f} {a200:>10.2f}")
    if bfull is not None:
        print(f"  {'Full (3.25M)':<20} {nfull:>4} {bfull:>10.4f} {sefull:>10.4f} {rfull:>8.4f} {afull:>10.2f}")
    print(f"  {'ln(2)/ln(3)':<20} {'':>4} {math.log(2)/math.log(3):>10.4f}")

    # --- Show the data points ---
    print(f"\n  Full-scale cluster centres and inter-cluster gaps:")
    gaps_full = [cl_full[i + 1]['centre'] - cl_full[i]['centre']
                 for i in range(len(cl_full) - 1)]
    centres_full = [(cl_full[i]['centre'] + cl_full[i + 1]['centre']) / 2
                    for i in range(len(cl_full) - 1)]
    print(f"  {'#':>4} {'Centre':>12} {'Gap':>10} {'log(C)':>8} {'log(G)':>8} {'Predicted':>10} {'Residual':>10}")
    if bfull is not None:
        for i, (c, g) in enumerate(zip(centres_full, gaps_full)):
            if c > 0 and g > 0:
                pred = afull * c ** bfull
                resid = g - pred
                print(f"  {i+1:>4} {c:>12,.0f} {g:>10,} {math.log(c):>8.2f} {math.log(g):>8.2f} "
                      f"{pred:>10,.0f} {resid:>10,.0f}")

    # --- Sensitivity: trimming ---
    print(f"\n{'='*72}")
    print("[5] SENSITIVITY: TRIMMED FITS (full scale)")
    print(f"{'='*72}")
    trims = [
        ("No trim", 0, 0),
        ("Drop first 2", 2, 0),
        ("Drop last 2", 0, 2),
        ("Drop first 2 + last 2", 2, 2),
        ("Drop first 5", 5, 0),
        ("Drop last 5", 0, 5),
        ("Drop first 5 + last 5", 5, 5),
    ]
    print(f"\n  {'Trim':<28} {'n':>4} {'beta':>10} {'se(beta)':>10} {'R2':>8}")
    print(f"  {'-'*60}")
    trim_results = []
    for label, sf, sl in trims:
        bt, rt, set_, at, nt = fit_power_law(cl_full, skip_first=sf, skip_last=sl)
        if bt is not None:
            print(f"  {label:<28} {nt:>4} {bt:>10.4f} {set_:>10.4f} {rt:>8.4f}")
            trim_results.append((label, nt, bt, set_, rt))

    # --- Null model at full scale ---
    print(f"\n{'='*72}")
    print(f"[6] NULL MODEL AT FULL SCALE ({N_TRIALS} trials)")
    print(f"{'='*72}")

    null_betas = []
    null_r2s = []
    null_n_clusters = []

    for trial in range(N_TRIALS):
        t1 = time.time()
        logs1, logs2 = generate_pseudo_primes(SIEVE_LIMIT, seed=trial * 137 + 42)
        n_null = min(len(logs1), len(logs2), n_use)
        ng1, ng2, nmax = compute_gap_arrays(logs1[:n_null], logs2[:n_null])
        ncl = find_clusters(ng1, ng2, nmax)
        null_n_clusters.append(len(ncl))
        nb, nr2, nse, na, nn = fit_power_law(ncl)
        if nb is not None:
            null_betas.append(nb)
            null_r2s.append(nr2)
        print(f"  Trial {trial:2d}: {len(ncl)} clusters" +
              (f", beta={nb:.4f}, R2={nr2:.4f}" if nb is not None else "") +
              f"  [{time.time()-t1:.1f}s]")

    print(f"\n  Null summary (full scale):")
    print(f"    Clusters: {avg(null_n_clusters):.1f} +/- {std_dev(null_n_clusters):.1f}")
    if null_betas:
        print(f"    beta:     {avg(null_betas):.4f} +/- {std_dev(null_betas):.4f}")
        print(f"    R2:       {avg(null_r2s):.4f} +/- {std_dev(null_r2s):.4f}")
        print(f"    beta range: [{min(null_betas):.4f}, {max(null_betas):.4f}]")
        print(f"    R2 range:   [{min(null_r2s):.4f}, {max(null_r2s):.4f}]")

    # --- z-scores ---
    if bfull is not None and null_betas and std_dev(null_betas) > 0:
        z_beta = (bfull - avg(null_betas)) / std_dev(null_betas)
        print(f"\n    z(beta, real vs null): {z_beta:.2f}")
    if rfull is not None and null_r2s and std_dev(null_r2s) > 0:
        z_r2 = (rfull - avg(null_r2s)) / std_dev(null_r2s)
        print(f"    z(R2, real vs null):   {z_r2:.2f}")

    # --- Summary table ---
    print(f"\n{'='*72}")
    print("SUMMARY TABLE")
    print(f"{'='*72}")
    print(f"\n  {'Scale':<25} {'n':>4} {'beta':>10} {'se':>10} {'R2':>8}")
    print(f"  {'-'*57}")
    if b200 is not None:
        print(f"  {'200k (paper)':<25} {n200:>4} {b200:>10.4f} {se200:>10.4f} {r200:>8.4f}")
    if bfull is not None:
        print(f"  {'Full 3.25M (real)':<25} {nfull:>4} {bfull:>10.4f} {sefull:>10.4f} {rfull:>8.4f}")
    if null_betas:
        print(f"  {'Full 3.25M (null mean)':<25} {'':>4} {avg(null_betas):>10.4f} "
              f"{std_dev(null_betas):>10.4f} {avg(null_r2s):>8.4f}")
    print(f"  {'ln(2)/ln(3)':<25} {'':>4} {math.log(2)/math.log(3):>10.4f}")

    # --- Save CSV ---
    csv_path = os.path.join(RESULTS_DIR, 'power_law_full_scale.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['scale', 'n_points', 'beta', 'se_beta', 'r_squared', 'alpha'])
        if b200 is not None:
            w.writerow(['200k', n200, b200, se200, r200, a200])
        if bfull is not None:
            w.writerow(['full', nfull, bfull, sefull, rfull, afull])
        for label, nt, bt, set_, rt in trim_results:
            w.writerow([f'full_trim_{label}', nt, bt, set_, rt, ''])
    print(f"\n  Results saved to {csv_path}")

    # --- Generate plot data for external plotting ---
    plot_csv = os.path.join(RESULTS_DIR, 'power_law_plot_data.csv')
    with open(plot_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['centre', 'gap', 'log_centre', 'log_gap', 'scale'])
        # 200k data
        gaps_200k = [cl_200k[i + 1]['centre'] - cl_200k[i]['centre']
                     for i in range(len(cl_200k) - 1)]
        centres_200k = [(cl_200k[i]['centre'] + cl_200k[i + 1]['centre']) / 2
                        for i in range(len(cl_200k) - 1)]
        for c, g in zip(centres_200k, gaps_200k):
            if c > 0 and g > 0:
                w.writerow([c, g, math.log10(c), math.log10(g), '200k'])
        # Full data
        for c, g in zip(centres_full, gaps_full):
            if c > 0 and g > 0:
                w.writerow([c, g, math.log10(c), math.log10(g), 'full'])
    print(f"  Plot data saved to {plot_csv}")

    print(f"\nTotal runtime: {time.time()-T0:.1f}s")


if __name__ == '__main__':
    main()
