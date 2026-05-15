#!/usr/bin/env python3
"""
R-squared vs Cumulative Scale (v2.6 -> v2.7 Task 3)
====================================================

v2.6 claims a "200k regime" where cluster-spacing R² = 0.979 (z = +2.20
vs 100-trial null) and reports R² = 0.226 at full scale (3.25M). The
trajectory between these endpoints is uncharacterised. This script
computes R² of the cluster-spacing power-law fit at 8 cumulative scales
with 100-trial null bands at each.

Parameters (canonical §5.2 set, fixed across all scales):
  window = 50
  min_gaps = 20
  merge_dist = 500

Scales (cumulative digits): 50k, 100k, 200k, 300k, 500k, 1M, 2M, 3.25M.

Seed scheme:
  seed = trial * 137 + 42 + scale_offset
where scale_offset = 0 for ALL scales — i.e. the SAME 100 pseudo-prime
draws are re-used and truncated at each cumulative scale. Rationale:
the goal of this task is to characterise the trajectory of R² as the
cumulative scale grows. Truncating a fixed draw at successive scales
produces *correlated* null bands across scales, which is the natural
view of "how does R² evolve within a sample as the data grows." Using
independent draws per scale would make the trajectory between scales
appear noisier than the underlying R²(scale) curve is. We document
scale_offset = 0 explicitly so a re-runner can choose an alternative
(e.g. scale_offset = scale_index × 1_000_000) if independent samples
are preferred.

Outputs:
  - null-tests/results/r2_vs_scale_per_trial.csv   (full per-trial data)
  - null-tests/results/r2_vs_scale_summary.csv     (one row per scale)
  - figures/r2_vs_scale.png  +  figures/r2_vs_scale.svg
  - findings.md §12.3 summary (written by hand after run completes)
"""
import math, random, time, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
N_TRIALS = 100
SCALES = [50_000, 100_000, 200_000, 300_000, 500_000, 1_000_000, 2_000_000, 3_250_000]
WINDOW = 50
MIN_GAPS = 20
MERGE_DIST = 500
SCALE_OFFSET = 0  # see docstring; same null draws re-used across scales

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'figures')


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


def find_clusters(is_gap1, is_gap2, max_d, window=WINDOW, min_gaps=MIN_GAPS,
                  merge_dist=MERGE_DIST):
    sync_starts = []
    step = 10
    for start in range(1, max_d - window + 1, step):
        end = start + window
        if end > max_d:
            break
        cb = ca = 0
        for d in range(start, end):
            g1, g2 = is_gap1[d], is_gap2[d]
            if g1 and g2:
                cb += 1
                ca += 1
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


def render_figure(summary_rows, fig_dir):
    """Render R² vs scale figure. Returns paths to PNG/SVG or None on failure."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not available — skipping figure.")
        return None, None

    os.makedirs(fig_dir, exist_ok=True)
    scales = [r['scale'] for r in summary_rows]
    r2_real = [r['r2_real'] for r in summary_rows]
    r2_null_mean = [r['r2_null_mean'] for r in summary_rows]
    r2_null_std = [r['r2_null_std'] for r in summary_rows]
    r2_null_max = [r['r2_null_max'] for r in summary_rows]

    band_lo = [m - s for m, s in zip(r2_null_mean, r2_null_std)]
    band_hi = [m + s for m, s in zip(r2_null_mean, r2_null_std)]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.fill_between(scales, band_lo, band_hi, color='#9ec5e8', alpha=0.55,
                    label=r'null mean $\pm 1\sigma$')
    ax.plot(scales, r2_null_mean, color='#2466a8', lw=1.8, marker='s',
            ms=5, label='null mean (100 trials)')
    ax.plot(scales, r2_null_max, color='#7d2222', lw=1.0, ls='--', marker='v',
            ms=4, label='null max (100 trials)')
    ax.plot(scales, r2_real, color='#1d6b1d', lw=2.4, marker='o', ms=7,
            label='real primes')

    ax.set_xscale('log')
    ax.set_xlabel('Cumulative scale (digits)')
    ax.set_ylabel(r'Cluster-spacing power-law $R^2$')
    ax.set_title(r'$R^2$ vs cumulative scale (window=50, min_gaps=20, merge_dist=500)')
    ax.grid(True, which='both', linestyle=':', alpha=0.55)
    ax.set_ylim(-0.05, 1.05)
    ax.axhline(1.0, color='black', lw=0.5, alpha=0.4)
    ax.axhline(0.0, color='black', lw=0.5, alpha=0.4)
    ax.legend(loc='lower left', framealpha=0.92)
    fig.tight_layout()

    png_path = os.path.join(fig_dir, 'r2_vs_scale.png')
    svg_path = os.path.join(fig_dir, 'r2_vs_scale.svg')
    fig.savefig(png_path, dpi=140)
    fig.savefig(svg_path)
    plt.close(fig)
    return png_path, svg_path


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    T0 = time.time()

    print("=" * 78)
    print("R^2 VS CUMULATIVE SCALE  (v2.6 -> v2.7 Task 3)")
    print(f"  Parameters: window={WINDOW}, min_gaps={MIN_GAPS}, merge_dist={MERGE_DIST}")
    print(f"  Scales: {[f'{s:,}' for s in SCALES]}")
    print(f"  Trials per scale: {N_TRIALS}")
    print(f"  Seed: trial*137 + 42 + scale_offset (scale_offset={SCALE_OFFSET}, shared draws)")
    print("=" * 78)

    print("\n[1] Sieving primes (one-off)...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    p5_logs = [math.log10(p) for p in p5]
    p7_logs = [math.log10(p) for p in p7]
    n_use = min(len(p5_logs), len(p7_logs))
    print(f"  5-series: {len(p5):,}, 7-series: {len(p7):,}, n_use={n_use:,}")

    print("\n[2] Real-prime gap arrays at full scale (one-off)...")
    t1 = time.time()
    real_g1, real_g2, real_max_d = compute_gap_arrays(p5_logs[:n_use], p7_logs[:n_use])
    print(f"  max_d (real) = {real_max_d:,}  [{time.time() - t1:.1f}s]")

    # --- Real-prime side: R^2 at each scale ---
    print(f"\n[3] Real-prime R^2 at each scale...")
    real_per_scale = {}
    for scale in SCALES:
        t1 = time.time()
        sc = min(scale, real_max_d)
        cl = find_clusters(real_g1, real_g2, sc)
        beta, r2, se_beta = fit_power_law(cl)
        real_per_scale[scale] = {
            'n_clusters': len(cl), 'beta': beta, 'r2': r2, 'se_beta': se_beta,
        }
        beta_s = f"{beta:.4f}" if beta is not None else "  n/a"
        r2_s = f"{r2:.4f}" if r2 is not None else "  n/a"
        print(f"  scale={scale:>9,}: clusters={len(cl):>3}  beta={beta_s}  "
              f"R^2={r2_s}  [{time.time() - t1:.2f}s]")

    # --- Null side: 100 trials, all scales per trial ---
    print(f"\n[4] Null trials: {N_TRIALS} pseudo-prime samples, "
          f"clusters at all {len(SCALES)} scales per trial...")
    # null_data[scale] = list of {n_clusters, beta, r2, se_beta} dicts
    null_data = {s: [] for s in SCALES}
    per_trial_rows = []

    for trial in range(N_TRIALS):
        t1 = time.time()
        seed = trial * 137 + 42 + SCALE_OFFSET
        logs1, logs2 = generate_pseudo_primes(SIEVE_LIMIT, seed=seed)
        n_null = min(len(logs1), len(logs2), n_use)
        ng1, ng2, nmax = compute_gap_arrays(logs1[:n_null], logs2[:n_null])

        per_scale_brief = []
        for scale in SCALES:
            sc = min(scale, nmax)
            cl = find_clusters(ng1, ng2, sc)
            beta, r2, se_beta = fit_power_law(cl)
            entry = {'n_clusters': len(cl), 'beta': beta, 'r2': r2, 'se_beta': se_beta}
            null_data[scale].append(entry)
            per_trial_rows.append({
                'trial': trial, 'seed': seed, 'scale': scale,
                'n_clusters': len(cl), 'beta': beta, 'r2': r2, 'se_beta': se_beta,
                'max_d': nmax,
            })
            if scale in (200_000, 3_250_000):
                r2_s = f"R^2={r2:.3f}" if r2 is not None else "R^2=n/a"
                per_scale_brief.append(f"{scale//1000}k:{r2_s}")
        elapsed = time.time() - t1
        print(f"  Trial {trial:3d}: nmax={nmax:>9,}  " +
              "  ".join(per_scale_brief) +
              f"  [{elapsed:.1f}s]")

    # --- Summarise per scale ---
    print(f"\n{'=' * 78}")
    print("SUMMARY: R^2 vs SCALE")
    print(f"{'=' * 78}")

    summary_rows = []
    for scale in SCALES:
        # Filter null trials with successful fits at this scale
        r2_list = [e['r2'] for e in null_data[scale] if e['r2'] is not None]
        beta_list = [e['beta'] for e in null_data[scale] if e['beta'] is not None]
        ncl_list = [e['n_clusters'] for e in null_data[scale]]

        r2_real = real_per_scale[scale]['r2']
        beta_real = real_per_scale[scale]['beta']
        ncl_real = real_per_scale[scale]['n_clusters']

        null_r2_mean = avg(r2_list) if r2_list else float('nan')
        null_r2_std = std_dev(r2_list) if len(r2_list) >= 2 else 0.0
        null_r2_max = max(r2_list) if r2_list else float('nan')
        null_r2_min = min(r2_list) if r2_list else float('nan')
        null_beta_mean = avg(beta_list) if beta_list else float('nan')
        null_beta_std = std_dev(beta_list) if len(beta_list) >= 2 else 0.0
        null_ncl_mean = avg(ncl_list) if ncl_list else 0
        null_ncl_std = std_dev(ncl_list) if len(ncl_list) >= 2 else 0

        z_r2 = ((r2_real - null_r2_mean) / null_r2_std
                if r2_real is not None and null_r2_std > 0 else float('nan'))

        summary_rows.append({
            'scale': scale, 'n_trials_fit': len(r2_list),
            'r2_real': r2_real, 'beta_real': beta_real, 'n_clusters_real': ncl_real,
            'r2_null_mean': null_r2_mean, 'r2_null_std': null_r2_std,
            'r2_null_min': null_r2_min, 'r2_null_max': null_r2_max,
            'beta_null_mean': null_beta_mean, 'beta_null_std': null_beta_std,
            'n_clusters_null_mean': null_ncl_mean, 'n_clusters_null_std': null_ncl_std,
            'z_r2': z_r2,
        })

    print(f"\n  {'Scale':>9} {'NC_r':>5} {'NC_null':>9} {'R2_real':>8} "
          f"{'R2_null_mn':>11} {'R2_null_sd':>11} {'R2_null_mx':>11} {'z_R2':>7}")
    print(f"  {'-' * 80}")
    for r in summary_rows:
        r2r = f"{r['r2_real']:.4f}" if r['r2_real'] is not None else "  n/a"
        zs = f"{r['z_r2']:+.2f}" if not math.isnan(r['z_r2']) else "  n/a"
        print(f"  {r['scale']:>9,} {r['n_clusters_real']:>5} "
              f"{r['n_clusters_null_mean']:>9.1f} {r2r:>8} "
              f"{r['r2_null_mean']:>11.4f} {r['r2_null_std']:>11.4f} "
              f"{r['r2_null_max']:>11.4f} {zs:>7}")

    # --- Save CSVs ---
    per_trial_path = os.path.join(RESULTS_DIR, 'r2_vs_scale_per_trial.csv')
    with open(per_trial_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['trial', 'seed', 'scale', 'n_clusters', 'beta', 'r_squared',
                    'se_beta', 'max_d'])
        for r in per_trial_rows:
            w.writerow([
                r['trial'], r['seed'], r['scale'], r['n_clusters'],
                f"{r['beta']:.6f}" if r['beta'] is not None else '',
                f"{r['r2']:.6f}" if r['r2'] is not None else '',
                f"{r['se_beta']:.6f}" if r['se_beta'] is not None else '',
                r['max_d'],
            ])
    # Real-prime rows for completeness
    with open(per_trial_path, 'a', newline='') as f:
        w = csv.writer(f)
        for scale in SCALES:
            r = real_per_scale[scale]
            w.writerow([
                'real', '', scale, r['n_clusters'],
                f"{r['beta']:.6f}" if r['beta'] is not None else '',
                f"{r['r2']:.6f}" if r['r2'] is not None else '',
                f"{r['se_beta']:.6f}" if r['se_beta'] is not None else '',
                real_max_d,
            ])
    print(f"\n  Per-trial data saved to {per_trial_path}")

    summary_path = os.path.join(RESULTS_DIR, 'r2_vs_scale_summary.csv')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['scale', 'n_trials_fit',
                    'n_clusters_real', 'beta_real', 'r2_real',
                    'n_clusters_null_mean', 'n_clusters_null_std',
                    'beta_null_mean', 'beta_null_std',
                    'r2_null_mean', 'r2_null_std', 'r2_null_min', 'r2_null_max',
                    'z_r2'])
        for r in summary_rows:
            def f6(v):
                return f"{v:.6f}" if v is not None and not (isinstance(v, float) and math.isnan(v)) else ''
            w.writerow([
                r['scale'], r['n_trials_fit'],
                r['n_clusters_real'], f6(r['beta_real']), f6(r['r2_real']),
                f"{r['n_clusters_null_mean']:.2f}",
                f"{r['n_clusters_null_std']:.2f}",
                f6(r['beta_null_mean']), f6(r['beta_null_std']),
                f6(r['r2_null_mean']), f6(r['r2_null_std']),
                f6(r['r2_null_min']), f6(r['r2_null_max']),
                f6(r['z_r2']),
            ])
    print(f"  Summary saved to {summary_path}")

    # --- Figure ---
    print(f"\n[5] Rendering figure...")
    # Only include scales where r2_real is valid for clean plotting
    valid_summary = [r for r in summary_rows
                     if r['r2_real'] is not None
                     and not math.isnan(r['r2_null_mean'])]
    png, svg = render_figure(valid_summary, FIG_DIR)
    if png:
        print(f"  PNG: {png}")
        print(f"  SVG: {svg}")

    print(f"\nTotal runtime: {time.time() - T0:.1f}s")


if __name__ == '__main__':
    main()
