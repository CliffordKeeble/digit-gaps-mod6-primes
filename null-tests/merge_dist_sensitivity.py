#!/usr/bin/env python3
"""
merge_dist Sensitivity (v2.7 -> v2.8 Task B)
=============================================

Mr A flagged that Table 7 reports sensitivity to window and min_gaps but
not to merge_dist — yet merge_dist is the parameter that changed the
cluster count from 36 (v2.6, merge_dist=2000) to 48 (v2.7, merge_dist=500).
The load-bearing R² result depends on cluster identification, which
depends on merge_dist. This task characterises R² and β sensitivity to
merge_dist at canonical window=50, min_gaps=20.

Pre-registered hypotheses (briefs/v2_7_to_v2_8_brief.md):
  H_B0 (robust):     R² > 0.95 across merge_dist in {100, 250, 500,
                     1000, 2000, 5000} at 200k scale, AND β stable to
                     ±0.05 across the sweep.
  H_B1 (conditional): R² varies > 0.05 or β varies > 0.05. Report the
                     interval over which R² > 0.95.

Method:
  - Real primes only (single sieve).
  - Canonical window=50, min_gaps=20, 200k scale (mandatory).
  - merge_dist ∈ {100, 250, 500, 1000, 2000, 5000}.
  - Cross-scale at 50k, 100k, 300k (optional; brief says yes if cheap).
  - For each (scale, merge_dist) pair: cluster count, β, se(β), R², n_data_points.

Decision rule (per brief): report; CinC integrates into Table 7 / 7a.
"""
import math, time, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
WINDOW = 50
MIN_GAPS = 20
MERGE_DISTS = [100, 250, 500, 1000, 2000, 5000]
SCALES_MANDATORY = [200_000]
SCALES_OPTIONAL = [50_000, 100_000, 300_000]
SCALES = SCALES_MANDATORY + SCALES_OPTIONAL

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def sieve(limit):
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
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
        if d <= max_d:
            is_gap1[d] = 0
    for d in d2:
        if d <= max_d:
            is_gap2[d] = 0
    return is_gap1, is_gap2, max_d


def find_sync_starts(is_gap1, is_gap2, max_d, window, min_gaps, step=10):
    """Same logic as `find_clusters_fast` cb==ca && ca>=min_gaps; returns
    starts list. Merging applied separately so we can sweep merge_dist
    cheaply over a single computed sync_starts."""
    starts = []
    for start in range(1, max_d - window + 1, step):
        end = start + window
        cb = ca = 0
        for d in range(start, end):
            g1, g2 = is_gap1[d], is_gap2[d]
            if g1 and g2:
                cb += 1
                ca += 1
            elif g1 or g2:
                ca += 1
        if ca >= min_gaps and cb == ca:
            starts.append(start)
    return starts


def merge_into_clusters(sync_starts, window, merge_dist):
    if not sync_starts:
        return []
    clusters = []
    c_start = sync_starts[0]
    c_end = sync_starts[0] + window
    for s in sync_starts[1:]:
        if s <= c_end + merge_dist:
            c_end = s + window
        else:
            clusters.append({'centre': (c_start + c_end) // 2,
                             'span': c_end - c_start})
            c_start, c_end = s, s + window
    clusters.append({'centre': (c_start + c_end) // 2,
                     'span': c_end - c_start})
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


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    T0 = time.time()

    print("=" * 78)
    print("merge_dist SENSITIVITY  (v2.7 -> v2.8 Task B)")
    print(f"  window={WINDOW}, min_gaps={MIN_GAPS}")
    print(f"  merge_dist values: {MERGE_DISTS}")
    print(f"  Scales: {SCALES_MANDATORY} (mandatory)  +  {SCALES_OPTIONAL} (cross-scale)")
    print("=" * 78)

    print("\n[1] Sieving primes...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    p5_logs = [math.log10(p) for p in p5]
    p7_logs = [math.log10(p) for p in p7]
    n_use = min(len(p5_logs), len(p7_logs))
    print(f"  p5={len(p5):,}  p7={len(p7):,}  n_use={n_use:,}")

    print("\n[2] Computing full gap arrays (one-off)...")
    t1 = time.time()
    is_gap1, is_gap2, max_d = compute_gap_arrays(p5_logs[:n_use], p7_logs[:n_use])
    print(f"  max_d={max_d:,}  [{time.time()-t1:.1f}s]")

    # For each scale, compute sync_starts once at that scale's truncated max_d,
    # then sweep merge_dist cheaply.
    rows = []
    print(f"\n[3] Sync_starts + merge_dist sweep at each scale...")
    for scale in SCALES:
        t1 = time.time()
        sc = min(scale, max_d)
        starts = find_sync_starts(is_gap1, is_gap2, sc, WINDOW, MIN_GAPS)
        sync_starts_time = time.time() - t1
        for md in MERGE_DISTS:
            cl = merge_into_clusters(starts, WINDOW, md)
            beta, r2, se_beta = fit_power_law(cl)
            n_pts = max(0, len(cl) - 1)
            rows.append({
                'scale': scale, 'merge_dist': md,
                'sync_starts': len(starts),
                'n_clusters': len(cl), 'n_data_points': n_pts,
                'beta': beta, 'se_beta': se_beta, 'r_squared': r2,
            })
        print(f"  scale={scale:>7,}: {len(starts):>5} sync_starts  "
              f"[{sync_starts_time:.2f}s for starts; merge sweep negligible]")

    # --- Console summary at canonical 200k ---
    print(f"\n{'=' * 78}")
    print("CANONICAL 200k SCALE — merge_dist SENSITIVITY")
    print(f"{'=' * 78}")
    print(f"\n  {'merge_dist':>10} {'n_clusters':>11} {'n_pts':>6} "
          f"{'beta':>10} {'se(beta)':>10} {'R²':>10}")
    print(f"  {'-' * 60}")
    rows_200k = [r for r in rows if r['scale'] == 200_000]
    for r in rows_200k:
        b_s = f"{r['beta']:.4f}" if r['beta'] is not None else "n/a"
        se_s = f"{r['se_beta']:.4f}" if r['se_beta'] is not None else "n/a"
        r2_s = f"{r['r_squared']:.4f}" if r['r_squared'] is not None else "n/a"
        print(f"  {r['merge_dist']:>10} {r['n_clusters']:>11} {r['n_data_points']:>6} "
              f"{b_s:>10} {se_s:>10} {r2_s:>10}")

    # --- Decision rule evaluation at 200k ---
    betas = [r['beta'] for r in rows_200k if r['beta'] is not None]
    r2s = [r['r_squared'] for r in rows_200k if r['r_squared'] is not None]
    if betas and r2s:
        beta_min, beta_max = min(betas), max(betas)
        beta_range = beta_max - beta_min
        r2_min, r2_max = min(r2s), max(r2s)
        r2_range = r2_max - r2_min
        all_r2_above_095 = all(r > 0.95 for r in r2s)
        beta_stable_pm_005 = beta_range <= 0.05

        print(f"\n  beta range:  [{beta_min:.4f}, {beta_max:.4f}]  span = {beta_range:.4f}")
        print(f"  R²   range:  [{r2_min:.4f}, {r2_max:.4f}]  span = {r2_range:.4f}")
        print(f"\n  H_B0 (R² > 0.95 across sweep AND beta stable ±0.05): "
              f"{all_r2_above_095 and beta_stable_pm_005}")
        print(f"    R² > 0.95 across sweep:  {all_r2_above_095}")
        print(f"    beta range ≤ 0.05:       {beta_stable_pm_005}")
        if not (all_r2_above_095 and beta_stable_pm_005):
            print(f"\n  H_B1 verdict: report interval where R² > 0.95")
            for r in rows_200k:
                marker = " ← R² > 0.95" if r['r_squared'] and r['r_squared'] > 0.95 else ""
                print(f"    merge_dist={r['merge_dist']:>4}: "
                      f"R²={r['r_squared']:.4f}{marker}")

    # --- Cross-scale check ---
    print(f"\n{'=' * 78}")
    print("CROSS-SCALE merge_dist SENSITIVITY")
    print(f"{'=' * 78}")
    for scale in SCALES:
        scale_rows = [r for r in rows if r['scale'] == scale]
        print(f"\n  scale = {scale:,}:")
        print(f"    {'merge_dist':>10} {'n_cl':>5} {'beta':>8} {'R²':>8}")
        for r in scale_rows:
            b_s = f"{r['beta']:.4f}" if r['beta'] is not None else "n/a"
            r2_s = f"{r['r_squared']:.4f}" if r['r_squared'] is not None else "n/a"
            print(f"    {r['merge_dist']:>10} {r['n_clusters']:>5} "
                  f"{b_s:>8} {r2_s:>8}")

    # --- Save CSV ---
    csv_path = os.path.join(RESULTS_DIR, 'merge_dist_summary.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['scale', 'window', 'min_gaps', 'merge_dist',
                    'sync_starts', 'n_clusters', 'n_data_points',
                    'beta', 'se_beta', 'r_squared'])
        for r in rows:
            def f6(v):
                return f"{v:.6f}" if v is not None else ''
            w.writerow([r['scale'], WINDOW, MIN_GAPS, r['merge_dist'],
                        r['sync_starts'], r['n_clusters'], r['n_data_points'],
                        f6(r['beta']), f6(r['se_beta']), f6(r['r_squared'])])
    print(f"\n  CSV saved to {csv_path}  ({len(rows)} rows)")

    print(f"\nTotal runtime: {time.time() - T0:.1f}s")


if __name__ == '__main__':
    main()
