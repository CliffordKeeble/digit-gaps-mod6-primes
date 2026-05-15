#!/usr/bin/env python3
"""
Base-Independence (Coprime to 6): Base 5, Base 7 (v2.7 -> v2.8 Task C)
=======================================================================

Mr A's third-review critique: the v2.7 base-independence test (bases
{2, 6, 10}) are all even — they all share factor 2. A genuine
base-independence test should include a base coprime to 6, because the
striking coincidence β ≈ ln(2)/ln(3) = 0.6309 references the prime 2
and the prime 3. If β were base-dependent in a hidden way, the most
sensitive probe is a base coprime to {2, 3}, i.e. a base coprime to 6.
The two smallest such bases are 5 and 7.

This task runs base 5 (primary) and base 7 (if budget permits).
Base 10 is included as a sanity-check row reproducing the v2.7
canonical result.

Pre-registered hypotheses (briefs/v2_7_to_v2_8_brief.md):
  H_C0 (β survives in coprime-to-6 base): β at canonical 200k-
        equivalent scale lies within ±0.02 of base-10 β = 0.637, AND
        zero of 100 null trials reach the real R².
  H_C1 (β drifts in coprime-to-6 base): β shifts by > 0.02. The
        ln(2)/ln(3) reading would need re-examination.

Method (parallel to v2.7 Task 4 base_independence.py):
  - Sieve to 15M; restrict to p > 3 (matching real-mod-6 pipeline).
  - For each base b ∈ {10, 5, 7} (10 included as sanity check):
      - scale = 200,000 × log_b(10)
      - window = 50 × log_b(10)
      - merge_dist = 500 × log_b(10)
      - min_gaps = 20 (unchanged — count, not a length)
      - step = 10 × log_b(10)
  - 100 null trials per base; shared random draws across bases
    (seed = trial * 137 + 42 + base_offset, with base_offset = 0
    consistent with Task 4 conventions).

Numerical scale equivalents:
  base 10: scale=200,000     window=50     merge_dist=500     step=10
  base  5: scale=286,135     window=72     merge_dist=715     step=14
  base  7: scale=236,659     window=59     merge_dist=592     step=12

(Brief gives 286,073 / 237,225 for the base-5 / base-7 scales; correct
values rounded are 286,135 / 236,659. Small slip in the brief; we use
the correct values and note it.)
"""
import math, random, time, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
N_TRIALS = 100
BASE_OFFSET = 0

LN5 = math.log(5)
LN7 = math.log(7)
LN10 = math.log(10)

LOG5_OF_10 = LN10 / LN5     # ≈ 1.4307
LOG7_OF_10 = LN10 / LN7     # ≈ 1.1833

BASES = [
    {  # canonical sanity-check row
        'label': 'base-10',
        'log_base': 10,
        'inv_log_base': 1.0 / LN10,
        'scale': 200_000,
        'window': 50,
        'min_gaps': 20,
        'merge_dist': 500,
        'step': 10,
    },
    {
        'label': 'base-5',
        'log_base': 5,
        'inv_log_base': 1.0 / LN5,
        'scale': int(round(200_000 * LOG5_OF_10)),     # 286135
        'window': int(round(50 * LOG5_OF_10)),         # 72
        'min_gaps': 20,
        'merge_dist': int(round(500 * LOG5_OF_10)),    # 715
        'step': int(round(10 * LOG5_OF_10)),           # 14
    },
    {
        'label': 'base-7',
        'log_base': 7,
        'inv_log_base': 1.0 / LN7,
        'scale': int(round(200_000 * LOG7_OF_10)),     # 236659
        'window': int(round(50 * LOG7_OF_10)),         # 59
        'min_gaps': 20,
        'merge_dist': int(round(500 * LOG7_OF_10)),    # 592
        'step': int(round(10 * LOG7_OF_10)),           # 12
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
    """natural logs → base-b digit-length gap arrays."""
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


def analyse_one_base(g1, g2, bc):
    is_gap1, is_gap2, max_d = compute_gap_arrays(g1, g2, bc['inv_log_base'])
    sc = min(bc['scale'], max_d)
    cl = find_clusters(is_gap1, is_gap2, sc,
                       window=bc['window'],
                       min_gaps=bc['min_gaps'],
                       merge_dist=bc['merge_dist'],
                       step=bc['step'])
    beta, r2, se_beta = fit_power_law(cl)
    return {
        'max_d': max_d, 'n_clusters': len(cl),
        'beta': beta, 'r2': r2, 'se_beta': se_beta,
    }


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    T0 = time.time()

    print("=" * 78)
    print("BASE-INDEPENDENCE (COPRIME TO 6): BASE 5, BASE 7  (v2.7 -> v2.8 Task C)")
    print("=" * 78)
    print("\n  Base configurations:")
    for b in BASES:
        print(f"    {b['label']:>8}: scale={b['scale']:>7,}  window={b['window']:>4}  "
              f"min_gaps={b['min_gaps']:>2}  merge_dist={b['merge_dist']:>5}  "
              f"step={b['step']:>3}")
    print(f"  Trials per base: {N_TRIALS}")
    print(f"  Seed: trial*137 + 42 + base_offset (base_offset={BASE_OFFSET}, shared draws)")

    print("\n[1] Sieving primes (one-off)...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    p5_nlogs = [math.log(p) for p in p5]
    p7_nlogs = [math.log(p) for p in p7]
    n_use = min(len(p5_nlogs), len(p7_nlogs))
    print(f"  5-series: {len(p5):,}, 7-series: {len(p7):,}, n_use={n_use:,}")

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

        # Pre-registered hypothesis-check (vs base-10 β = 0.6371 from v2.7)
        beta_drift_from_b10 = (abs(beta_real - 0.6371)
                               if beta_real is not None else float('nan'))
        h_c0_beta_within_002 = (not math.isnan(beta_drift_from_b10)
                                and beta_drift_from_b10 <= 0.02)
        h_c0_zero_null_at_real = (n_ge_real_r2 == 0)
        h_c0_passes = h_c0_beta_within_002 and h_c0_zero_null_at_real

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
            'beta_drift_from_base10': beta_drift_from_b10,
            'h_c0_beta_within_002': h_c0_beta_within_002,
            'h_c0_zero_null_at_real': h_c0_zero_null_at_real,
            'h_c0_passes': h_c0_passes,
        })

    print(f"\n  Real-prime results:")
    print(f"  {'base':>8} {'NC_r':>5} {'beta_real':>10} {'R²_real':>10} "
          f"{'|β−0.637|':>11}")
    print(f"  {'-' * 50}")
    for r in summary_rows:
        b_s = f"{r['beta_real']:.4f}" if r['beta_real'] is not None else "n/a"
        r2_s = f"{r['r2_real']:.4f}" if r['r2_real'] is not None else "n/a"
        dr = f"{r['beta_drift_from_base10']:.4f}" if not math.isnan(
            r['beta_drift_from_base10']) else "n/a"
        print(f"  {r['base']:>8} {r['n_clusters_real']:>5} {b_s:>10} {r2_s:>10} "
              f"{dr:>11}")

    print(f"\n  Null and z-scores ({N_TRIALS} trials per base):")
    print(f"  {'base':>8} {'NC_null':>9} {'beta_null':>10} {'R²_null':>10} "
          f"{'R²_null_std':>12} {'z(R²)':>7} {'z(β)':>7} {'#null≥real':>11}")
    print(f"  {'-' * 90}")
    for r in summary_rows:
        z_r2_s = f"{r['z_r2']:+.2f}" if not math.isnan(r['z_r2']) else "n/a"
        z_beta_s = f"{r['z_beta']:+.2f}" if not math.isnan(r['z_beta']) else "n/a"
        nge_s = (f"{r['n_null_ge_real_r2']}/{r['n_trials_fit']}"
                 if r['n_null_ge_real_r2'] is not None else "n/a")
        print(f"  {r['base']:>8} {r['n_clusters_null_mean']:>9.1f} "
              f"{r['beta_null_mean']:>10.4f} {r['r2_null_mean']:>10.4f} "
              f"{r['r2_null_std']:>12.4f} {z_r2_s:>7} {z_beta_s:>7} {nge_s:>11}")

    print(f"\n  Pre-registered hypothesis check (H_C0: β within ±0.02 of 0.6371 "
          f"AND zero null ≥ real R²):")
    print(f"  {'base':>8} {'|β−0.637|':>11} {'within 0.02?':>15} "
          f"{'0 null ≥ real?':>17} {'H_C0?':>7}")
    print(f"  {'-' * 65}")
    for r in summary_rows:
        dr = f"{r['beta_drift_from_base10']:.4f}" if not math.isnan(
            r['beta_drift_from_base10']) else "n/a"
        print(f"  {r['base']:>8} {dr:>11} {str(r['h_c0_beta_within_002']):>15} "
              f"{str(r['h_c0_zero_null_at_real']):>17} {str(r['h_c0_passes']):>7}")

    # --- Save CSVs ---
    per_trial_path = os.path.join(RESULTS_DIR, 'base_coprime_to_6_per_trial.csv')
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
    print(f"\n  Per-trial CSV saved to {per_trial_path}")

    summary_path = os.path.join(RESULTS_DIR, 'base_coprime_to_6_summary.csv')
    def f6(v):
        return (f"{v:.6f}" if v is not None and
                not (isinstance(v, float) and math.isnan(v))
                else '')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['base', 'log_base', 'scale', 'window', 'min_gaps', 'merge_dist',
                    'n_clusters_real', 'beta_real', 'r2_real',
                    'n_clusters_null_mean', 'n_clusters_null_std',
                    'beta_null_mean', 'beta_null_std',
                    'r2_null_mean', 'r2_null_std', 'r2_null_min', 'r2_null_max',
                    'z_r2', 'z_beta', 'n_trials_fit', 'n_null_ge_real_r2',
                    'beta_drift_from_base10', 'h_c0_passes'])
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
                f6(r['beta_drift_from_base10']), r['h_c0_passes'],
            ])
    print(f"  Summary saved to {summary_path}")

    print(f"\nTotal runtime: {time.time() - T0:.1f}s")


if __name__ == '__main__':
    main()
