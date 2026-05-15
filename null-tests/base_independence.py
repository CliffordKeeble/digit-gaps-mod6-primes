#!/usr/bin/env python3
"""
Base-Independence Test for R² (v2.6 -> v2.7 Task 4)
====================================================

v2.6 §9 acknowledges base-independence as an open question for β only.
Mr Adversary's correct catch: the cluster structure itself is defined on
base-10 digit bands, so R² (the headline result) is also base-dependent
in its definition. This script repeats the 200k cluster-spacing analysis
under base-2 (bit-length) and base-6 (base-6 digit-length) accumulation
and compares R² with null at each base.

Scale equivalence — 200,000 base-10 digits in each base:
  base 10: 200,000 digits        (canonical)
  base  2: 664,386 bits           = 200,000 × log_2(10)
  base  6: 257,019 base-6 digits  = 200,000 × log_6(10) = 200,000 / log_10(6)

(Brief gives 257,773 for base 6; correct value rounded is 257,019. Negligible
difference — we use the correct value and note the brief discrepancy.)

Parameter scaling — cluster-detection window, merge_dist, and step all
scale by the same factor as the cumulative scale, preserving the "50 base-10
digit-equivalent window" semantics:

  base 10: window=50,   min_gaps=20, merge_dist=500,  step=10
  base  2: window=166,  min_gaps=20, merge_dist=1661, step=33
  base  6: window=64,   min_gaps=20, merge_dist=643,  step=13

min_gaps=20 is fixed across bases per the brief's wording ("≥20 coincident
gaps"). Note: from Task 2 we know min_gaps in [20, 35] is redundant at
window=50 in base 10 (every coincident-only 50-window has ≥35 gaps); the
brief-literal min_gaps=20 should remain non-binding at the scaled larger
windows in base 2 and base 6 as well.

Seed scheme:
  seed = trial * 137 + 42 + base_offset
where **base_offset = 0** for all bases. The SAME pseudo-prime draw is
re-used and only the log base is varied. This is the natural design for a
base-independence test — we want to test whether the same underlying
random configuration produces clean power-law R² regardless of which base
defines the digit bands, isolating the base-mapping effect. Independent
draws per base (e.g. base_offset = base_index × 1_000_000) would conflate
sample-to-sample variation with base effect.

Outputs:
  - null-tests/results/base_independence_per_trial.csv
  - null-tests/results/base_independence_summary.csv
  - findings.md §12.4 (written by hand)
"""
import math, random, time, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
N_TRIALS = 100
BASE_OFFSET = 0

LN10 = math.log(10)
LN2 = math.log(2)
LN6 = math.log(6)

# Conversion factors for scaling parameters from base-10 to other bases
LOG2_OF_10 = LN10 / LN2     # ~3.32193
LOG6_OF_10 = LN10 / LN6     # ~1.28509

BASES = [
    {
        'label': 'base-10',
        'log_base': 10,
        'inv_log_base': 1.0 / LN10,
        'scale_factor': 1.0,
        'scale': 200_000,
        'window': 50,
        'min_gaps': 20,
        'merge_dist': 500,
        'step': 10,
    },
    {
        'label': 'base-2',
        'log_base': 2,
        'inv_log_base': 1.0 / LN2,
        'scale_factor': LOG2_OF_10,
        'scale': int(round(200_000 * LOG2_OF_10)),     # 664386
        'window': int(round(50 * LOG2_OF_10)),         # 166
        'min_gaps': 20,
        'merge_dist': int(round(500 * LOG2_OF_10)),    # 1661
        'step': int(round(10 * LOG2_OF_10)),           # 33
    },
    {
        'label': 'base-6',
        'log_base': 6,
        'inv_log_base': 1.0 / LN6,
        'scale_factor': LOG6_OF_10,
        'scale': int(round(200_000 * LOG6_OF_10)),     # 257019
        'window': int(round(50 * LOG6_OF_10)),         # 64
        'min_gaps': 20,
        'merge_dist': int(round(500 * LOG6_OF_10)),    # 643
        'step': int(round(10 * LOG6_OF_10)),           # 13
    },
]

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')


def sieve(limit):
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def compute_gap_arrays(natural_logs_1, natural_logs_2, inv_log_base):
    """Convert natural logs to chosen-base logs via inv_log_base = 1/ln(base),
    then build cumulative-sum gap arrays in that base.
    inv_log_base = 1/ln(base): log_base(x) = ln(x) / ln(base) = ln(x) * inv_log_base.
    """
    d1 = set()
    s = 0.0
    for ln in natural_logs_1:
        s += ln * inv_log_base
        d1.add(int(s) + 1)
    d2 = set()
    s = 0.0
    for ln in natural_logs_2:
        s += ln * inv_log_base
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


def find_clusters(is_gap1, is_gap2, max_d, window, min_gaps, merge_dist, step):
    sync_starts = []
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


def generate_pseudo_prime_natural_logs(limit, seed):
    """Return (class1, class2) lists of natural logs of pseudo-primes.
    Base-agnostic — caller converts via inv_log_base for each desired base.
    Density and class-assignment match the existing generate_pseudo_primes."""
    rng = random.Random(seed)
    c1_logs, c2_logs = [], []
    for n in range(5, limit):
        if rng.random() < 1.0 / math.log(n):
            ln = math.log(n)
            if rng.random() < 0.5:
                c1_logs.append(ln)
            else:
                c2_logs.append(ln)
    return c1_logs, c2_logs


def avg(vals):
    return sum(vals) / len(vals) if vals else 0


def std_dev(vals):
    if len(vals) < 2:
        return 0
    m = avg(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))


def analyse_one_base(g1, g2, base_config):
    """Run gap-array + cluster + fit at the given base. Returns dict."""
    is_gap1, is_gap2, max_d = compute_gap_arrays(g1, g2, base_config['inv_log_base'])
    sc = min(base_config['scale'], max_d)
    cl = find_clusters(is_gap1, is_gap2, sc,
                       window=base_config['window'],
                       min_gaps=base_config['min_gaps'],
                       merge_dist=base_config['merge_dist'],
                       step=base_config['step'])
    beta, r2, se_beta = fit_power_law(cl)
    return {
        'max_d': max_d, 'n_clusters': len(cl),
        'beta': beta, 'r2': r2, 'se_beta': se_beta,
    }


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    T0 = time.time()

    print("=" * 78)
    print("BASE-INDEPENDENCE TEST FOR R²  (v2.6 -> v2.7 Task 4)")
    print("=" * 78)
    print("\n  Base configurations:")
    for b in BASES:
        print(f"    {b['label']:>8}: scale={b['scale']:>7,}  window={b['window']:>4}  "
              f"min_gaps={b['min_gaps']:>2}  merge_dist={b['merge_dist']:>5}  "
              f"step={b['step']:>3}")
    print(f"  Trials per base: {N_TRIALS}")
    print(f"  Seed: trial*137 + 42 + base_offset  (base_offset={BASE_OFFSET}, shared draws)")

    # --- Sieve and natural logs (one-off) ---
    print("\n[1] Sieving primes (one-off)...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    p5_nlogs = [math.log(p) for p in p5]
    p7_nlogs = [math.log(p) for p in p7]
    n_use = min(len(p5_nlogs), len(p7_nlogs))
    print(f"  5-series: {len(p5):,}, 7-series: {len(p7):,}, n_use={n_use:,}")

    # --- Real primes at each base ---
    print(f"\n[2] Real-prime analysis at each base...")
    real_per_base = {}
    for bc in BASES:
        t1 = time.time()
        res = analyse_one_base(p5_nlogs[:n_use], p7_nlogs[:n_use], bc)
        real_per_base[bc['label']] = res
        b_s = f"{res['beta']:.4f}" if res['beta'] is not None else "  n/a"
        r2_s = f"{res['r2']:.4f}" if res['r2'] is not None else "  n/a"
        print(f"  {bc['label']:>8}: max_d={res['max_d']:>9,}  "
              f"clusters={res['n_clusters']:>3}  beta={b_s}  R²={r2_s}  "
              f"[{time.time()-t1:.2f}s]")

    # --- Null trials ---
    print(f"\n[3] Null trials: {N_TRIALS} pseudo-prime draws, each analysed at all bases...")
    null_per_base = {b['label']: [] for b in BASES}
    per_trial_rows = []

    for trial in range(N_TRIALS):
        t1 = time.time()
        seed = trial * 137 + 42 + BASE_OFFSET
        g1, g2 = generate_pseudo_prime_natural_logs(SIEVE_LIMIT, seed=seed)
        n_null = min(len(g1), len(g2), n_use)
        g1 = g1[:n_null]
        g2 = g2[:n_null]
        msgs = []
        for bc in BASES:
            res = analyse_one_base(g1, g2, bc)
            null_per_base[bc['label']].append(res)
            per_trial_rows.append({
                'trial': trial, 'seed': seed,
                'base': bc['label'], 'log_base': bc['log_base'],
                'scale': bc['scale'], 'window': bc['window'],
                'min_gaps': bc['min_gaps'], 'merge_dist': bc['merge_dist'],
                'max_d': res['max_d'], 'n_clusters': res['n_clusters'],
                'beta': res['beta'], 'r2': res['r2'], 'se_beta': res['se_beta'],
            })
            r2_s = f"R²={res['r2']:.3f}" if res['r2'] is not None else "R²=n/a"
            msgs.append(f"{bc['label']}:{res['n_clusters']:>3}cl/{r2_s}")
        print(f"  Trial {trial:3d}: " + "  ".join(msgs) + f"  [{time.time()-t1:.1f}s]")

    # --- Summarise per base ---
    print(f"\n{'=' * 78}")
    print("SUMMARY: R² AND β BY BASE")
    print(f"{'=' * 78}")
    summary_rows = []
    for bc in BASES:
        label = bc['label']
        real = real_per_base[label]
        null_list = null_per_base[label]

        r2_real = real['r2']
        beta_real = real['beta']
        ncl_real = real['n_clusters']

        r2s = [e['r2'] for e in null_list if e['r2'] is not None]
        betas = [e['beta'] for e in null_list if e['beta'] is not None]
        ncls = [e['n_clusters'] for e in null_list]

        r2_mean = avg(r2s) if r2s else float('nan')
        r2_std = std_dev(r2s) if len(r2s) >= 2 else 0.0
        r2_max = max(r2s) if r2s else float('nan')
        r2_min = min(r2s) if r2s else float('nan')
        beta_mean = avg(betas) if betas else float('nan')
        beta_std = std_dev(betas) if len(betas) >= 2 else 0.0
        ncl_mean = avg(ncls) if ncls else 0
        ncl_std = std_dev(ncls) if len(ncls) >= 2 else 0

        z_r2 = ((r2_real - r2_mean) / r2_std
                if r2_real is not None and r2_std > 0 else float('nan'))
        z_beta = ((beta_real - beta_mean) / beta_std
                  if beta_real is not None and beta_std > 0 else float('nan'))
        n_ge_real_r2 = (sum(1 for r in r2s if r >= r2_real)
                        if r2_real is not None else None)

        summary_rows.append({
            'base': label, 'log_base': bc['log_base'],
            'scale': bc['scale'], 'window': bc['window'],
            'min_gaps': bc['min_gaps'], 'merge_dist': bc['merge_dist'],
            'n_clusters_real': ncl_real, 'beta_real': beta_real, 'r2_real': r2_real,
            'n_clusters_null_mean': ncl_mean, 'n_clusters_null_std': ncl_std,
            'beta_null_mean': beta_mean, 'beta_null_std': beta_std,
            'r2_null_mean': r2_mean, 'r2_null_std': r2_std,
            'r2_null_min': r2_min, 'r2_null_max': r2_max,
            'z_r2': z_r2, 'z_beta': z_beta,
            'n_trials_fit': len(r2s),
            'n_null_ge_real_r2': n_ge_real_r2,
        })

    # Print summary
    print(f"\n  Real-prime results:")
    print(f"  {'base':>8} {'NC_r':>5} {'beta_real':>10} {'R²_real':>10}")
    print(f"  {'-' * 40}")
    for r in summary_rows:
        b_s = f"{r['beta_real']:.4f}" if r['beta_real'] is not None else "n/a"
        r2_s = f"{r['r2_real']:.4f}" if r['r2_real'] is not None else "n/a"
        print(f"  {r['base']:>8} {r['n_clusters_real']:>5} {b_s:>10} {r2_s:>10}")

    print(f"\n  Null statistics ({N_TRIALS} trials per base):")
    print(f"  {'base':>8} {'NC_null':>9} {'beta_null':>10} {'beta_std':>10} "
          f"{'R²_null':>10} {'R²_std':>9} {'R²_max':>9}")
    print(f"  {'-' * 80}")
    for r in summary_rows:
        print(f"  {r['base']:>8} {r['n_clusters_null_mean']:>9.1f} "
              f"{r['beta_null_mean']:>10.4f} {r['beta_null_std']:>10.4f} "
              f"{r['r2_null_mean']:>10.4f} {r['r2_null_std']:>9.4f} "
              f"{r['r2_null_max']:>9.4f}")

    print(f"\n  Real-vs-null z-scores and tail counts:")
    print(f"  {'base':>8} {'z(R²)':>7} {'z(beta)':>9} {'#null ≥ real R²':>17}")
    print(f"  {'-' * 47}")
    for r in summary_rows:
        z_r2_s = f"{r['z_r2']:+.2f}" if not math.isnan(r['z_r2']) else "n/a"
        z_beta_s = f"{r['z_beta']:+.2f}" if not math.isnan(r['z_beta']) else "n/a"
        nge_s = (f"{r['n_null_ge_real_r2']}/{r['n_trials_fit']}"
                 if r['n_null_ge_real_r2'] is not None else "n/a")
        print(f"  {r['base']:>8} {z_r2_s:>7} {z_beta_s:>9} {nge_s:>17}")

    # --- Save CSVs ---
    per_trial_path = os.path.join(RESULTS_DIR, 'base_independence_per_trial.csv')
    with open(per_trial_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['trial', 'seed', 'base', 'log_base', 'scale', 'window',
                    'min_gaps', 'merge_dist', 'max_d',
                    'n_clusters', 'beta', 'r_squared', 'se_beta'])
        for r in per_trial_rows:
            w.writerow([
                r['trial'], r['seed'], r['base'], r['log_base'],
                r['scale'], r['window'], r['min_gaps'], r['merge_dist'],
                r['max_d'], r['n_clusters'],
                f"{r['beta']:.6f}" if r['beta'] is not None else '',
                f"{r['r2']:.6f}" if r['r2'] is not None else '',
                f"{r['se_beta']:.6f}" if r['se_beta'] is not None else '',
            ])
        # Real-prime rows
        for bc in BASES:
            r = real_per_base[bc['label']]
            w.writerow([
                'real', '', bc['label'], bc['log_base'],
                bc['scale'], bc['window'], bc['min_gaps'], bc['merge_dist'],
                r['max_d'], r['n_clusters'],
                f"{r['beta']:.6f}" if r['beta'] is not None else '',
                f"{r['r2']:.6f}" if r['r2'] is not None else '',
                f"{r['se_beta']:.6f}" if r['se_beta'] is not None else '',
            ])
    print(f"\n  Per-trial data saved to {per_trial_path}")

    summary_path = os.path.join(RESULTS_DIR, 'base_independence_summary.csv')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['base', 'log_base', 'scale', 'window', 'min_gaps', 'merge_dist',
                    'n_clusters_real', 'beta_real', 'r2_real',
                    'n_clusters_null_mean', 'n_clusters_null_std',
                    'beta_null_mean', 'beta_null_std',
                    'r2_null_mean', 'r2_null_std', 'r2_null_min', 'r2_null_max',
                    'z_r2', 'z_beta', 'n_trials_fit', 'n_null_ge_real_r2'])
        def f6(v):
            return (f"{v:.6f}" if v is not None and
                    not (isinstance(v, float) and math.isnan(v))
                    else '')
        for r in summary_rows:
            w.writerow([
                r['base'], r['log_base'], r['scale'], r['window'],
                r['min_gaps'], r['merge_dist'],
                r['n_clusters_real'], f6(r['beta_real']), f6(r['r2_real']),
                f"{r['n_clusters_null_mean']:.2f}",
                f"{r['n_clusters_null_std']:.2f}",
                f6(r['beta_null_mean']), f6(r['beta_null_std']),
                f6(r['r2_null_mean']), f6(r['r2_null_std']),
                f6(r['r2_null_min']), f6(r['r2_null_max']),
                f6(r['z_r2']), f6(r['z_beta']),
                r['n_trials_fit'], r['n_null_ge_real_r2'],
            ])
    print(f"  Summary saved to {summary_path}")

    print(f"\nTotal runtime: {time.time() - T0:.1f}s")


if __name__ == '__main__':
    main()
