#!/usr/bin/env python3
"""
Shuffle Test — Mod-6 vs Primes-Generic (v2.7 -> v2.8 Task A, LOAD-BEARING)
===========================================================================

Mr A's third-review challenge: the v2.7 §5.2 / §6.2 R² cleanness in the
50k-300k regime is shown against a PNT-density null. That null preserves
prime number theorem density and Dirichlet equidistribution but breaks
prime-prime correlations (twin-prime clustering, Hardy-Littlewood tuple
statistics, etc.). It therefore cannot distinguish:

  (a) mod-6 grouping is what creates the clean R² — i.e., the structure
      lives in how primes split mod 6, not in the primes themselves; or
  (b) primes already have cluster-spacing structure beyond density,
      which the PNT-density null cannot see.

The shuffle test resolves this by REUSING the same primes but reassigning
each one to a random pseudo-class. This preserves prime-prime correlations
exactly and breaks only the mod-6 grouping.

Pre-registered hypotheses (from briefs/v2_7_to_v2_8_brief.md):
  H_A1 (mod-6 specific):    z_AB = (R²_real - mean(R²_shuffle))
                                   / std(R²_shuffle)  ≥ +2.0
  H_A2 (primes-generic):    z_BC = (mean(R²_shuffle) - mean(R²_PNT-null))
                                   / std(R²_PNT-null) ≥ +2.0

Four outcomes:
  z_AB ≥ +2 AND z_BC <  +2 → mod-6 specifically the cause
  z_AB <  +2 AND z_BC ≥ +2 → primes-generic the cause
  z_AB ≥ +2 AND z_BC ≥ +2 → both contribute (layered finding)
  z_AB <  +2 AND z_BC <  +2 → no effect / pipeline issue

Method:
  1. Sieve primes to 15M; restrict to p > 3 (matching the real-mod-6 filter
     that excludes 2 and 3 from both series).
  2. For each shuffle trial t in 0..99:
       seed = t * 137 + 42
       For each prime p (ascending), draw a random bit in {0, 1}:
         bit = 0 -> class A
         bit = 1 -> class B
       Compute cumulative log_10 product for each pseudo-class.
       Build coincident-gap arrays at each target scale.
       Identify clusters under canonical params (window=50, min_gaps=20,
         merge_dist=500). Fit power law.
  3. Target scales: 50k, 100k, 200k, 300k (mandatory).
     Add 500k for phase-boundary check (cheap when other scales done).

Comparison reference (PNT-density null from findings.md §12.3, 100 trials):
  Scale     R²_real    R²_PNT-null mean    R²_PNT-null std
  50,000    0.9840     0.3727              0.2315
  100,000   0.9859     0.4816              0.1968
  200,000   0.9792     0.5767              0.1833
  300,000   0.9786     0.5270              0.2164
  500,000   0.5955     0.5851              0.1874

Hardwired into REFERENCE below for z computation at run time.

Seed: trial * 137 + 42 (consistent with the rest of the project).
"""
import math, random, time, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
N_TRIALS = 100
SCALES = [50_000, 100_000, 200_000, 300_000, 500_000]
WINDOW = 50
MIN_GAPS = 20
MERGE_DIST = 500

# PNT-density null reference numbers from findings.md §12.3 (Task 3 output)
REFERENCE = {
    50_000:    {'r2_real': 0.9840, 'r2_pnt_mean': 0.3727, 'r2_pnt_std': 0.2315},
    100_000:   {'r2_real': 0.9859, 'r2_pnt_mean': 0.4816, 'r2_pnt_std': 0.1968},
    200_000:   {'r2_real': 0.9792, 'r2_pnt_mean': 0.5767, 'r2_pnt_std': 0.1833},
    300_000:   {'r2_real': 0.9786, 'r2_pnt_mean': 0.5270, 'r2_pnt_std': 0.2164},
    500_000:   {'r2_real': 0.5955, 'r2_pnt_mean': 0.5851, 'r2_pnt_std': 0.1874},
}

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


def shuffle_split(primes_p_gt_3, seed):
    """For each prime in order, assign to class A (bit=0) or class B (bit=1).
    Returns (logs_A, logs_B) — already in ascending prime order since primes are."""
    rng = random.Random(seed)
    logs_A, logs_B = [], []
    for p in primes_p_gt_3:
        if rng.random() < 0.5:
            logs_A.append(math.log10(p))
        else:
            logs_B.append(math.log10(p))
    return logs_A, logs_B


def avg(vals):
    return sum(vals) / len(vals) if vals else 0


def std_dev(vals):
    if len(vals) < 2:
        return 0
    m = avg(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))


def median(vals):
    if not vals:
        return 0
    s = sorted(vals)
    n = len(s)
    return s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    T0 = time.time()

    print("=" * 78)
    print("SHUFFLE TEST  (v2.7 -> v2.8 Task A, LOAD-BEARING)")
    print(f"  Parameters: window={WINDOW}, min_gaps={MIN_GAPS}, merge_dist={MERGE_DIST}")
    print(f"  Scales: {[f'{s:,}' for s in SCALES]}")
    print(f"  Trials: {N_TRIALS}")
    print(f"  Seed: trial * 137 + 42")
    print("=" * 78)

    print("\n[1] Sieving primes (one-off)...")
    primes = sieve(SIEVE_LIMIT)
    primes_p_gt_3 = [p for p in primes if p > 3]
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    n_use = min(len(p5), len(p7))
    print(f"  total primes > 3: {len(primes_p_gt_3):,}")
    print(f"  real mod-6:  p5={len(p5):,}, p7={len(p7):,}, n_use={n_use:,}")

    # --- Shuffle trials ---
    print(f"\n[2] {N_TRIALS} shuffle trials...")
    per_trial_rows = []
    shuffle_data = {s: {'r2': [], 'beta': [], 'n_clusters': []} for s in SCALES}

    for trial in range(N_TRIALS):
        t1 = time.time()
        seed = trial * 137 + 42
        logs_A, logs_B = shuffle_split(primes_p_gt_3, seed)
        n_min = min(len(logs_A), len(logs_B), n_use)
        is_gap1, is_gap2, nmax = compute_gap_arrays(logs_A[:n_min], logs_B[:n_min])

        per_scale_brief = []
        for scale in SCALES:
            sc = min(scale, nmax)
            cl = find_clusters(is_gap1, is_gap2, sc)
            beta, r2, se_beta = fit_power_law(cl)
            shuffle_data[scale]['n_clusters'].append(len(cl))
            if r2 is not None:
                shuffle_data[scale]['r2'].append(r2)
                shuffle_data[scale]['beta'].append(beta)
            per_trial_rows.append({
                'trial': trial, 'seed': seed, 'scale': scale,
                'n_clusters': len(cl), 'beta': beta, 'r2': r2,
                'se_beta': se_beta, 'max_d': nmax,
                'runtime_s': None,  # filled in after the whole trial
            })
            if scale in (200_000, 300_000):
                r2_s = f"R²={r2:.3f}" if r2 is not None else "R²=n/a"
                per_scale_brief.append(f"{scale//1000}k:{len(cl):>3}cl/{r2_s}")
        elapsed = time.time() - t1
        # Fill in runtime for this trial's rows
        for r in per_trial_rows[-len(SCALES):]:
            r['runtime_s'] = round(elapsed, 3)
        print(f"  Trial {trial:3d}: |A|={len(logs_A):>6,} |B|={len(logs_B):>6,} "
              f"nmax={nmax:>9,}  " + "  ".join(per_scale_brief) +
              f"  [{elapsed:.1f}s]")

    # --- Pathology checks ---
    print(f"\n[3] Pathology checks...")
    pathology = []
    for scale in SCALES:
        r2s = shuffle_data[scale]['r2']
        if not r2s:
            continue
        if any(r < 0 or r > 1 for r in r2s):
            pathology.append(f"scale={scale}: R² outside [0, 1]")
    if pathology:
        print(f"  PATHOLOGY DETECTED:")
        for p in pathology:
            print(f"    {p}")
    else:
        print(f"  No pathology. All R² in [0, 1].")

    # --- Summary per scale ---
    print(f"\n{'=' * 78}")
    print("SHUFFLE R² SUMMARY AND DECISION RULE")
    print(f"{'=' * 78}")

    summary_rows = []
    for scale in SCALES:
        r2s = shuffle_data[scale]['r2']
        betas = shuffle_data[scale]['beta']
        ncls = shuffle_data[scale]['n_clusters']

        sh_mean = avg(r2s)
        sh_std = std_dev(r2s)
        sh_median = median(r2s)
        sh_min = min(r2s) if r2s else float('nan')
        sh_max = max(r2s) if r2s else float('nan')
        beta_mean = avg(betas) if betas else float('nan')
        beta_std = std_dev(betas) if len(betas) >= 2 else 0.0

        ref = REFERENCE.get(scale, {})
        r2_real = ref.get('r2_real')
        r2_pnt_mean = ref.get('r2_pnt_mean')
        r2_pnt_std = ref.get('r2_pnt_std')

        z_AB = ((r2_real - sh_mean) / sh_std
                if r2_real is not None and sh_std > 0 else float('nan'))
        z_BC = ((sh_mean - r2_pnt_mean) / r2_pnt_std
                if r2_pnt_mean is not None and r2_pnt_std > 0 else float('nan'))

        h_a1 = (not math.isnan(z_AB)) and z_AB >= 2.0
        h_a2 = (not math.isnan(z_BC)) and z_BC >= 2.0

        verdict_code = ""
        if h_a1 and not h_a2:
            verdict_code = "mod-6 specific"
        elif (not h_a1) and h_a2:
            verdict_code = "primes-generic"
        elif h_a1 and h_a2:
            verdict_code = "both (layered)"
        else:
            verdict_code = "no effect"

        summary_rows.append({
            'scale': scale, 'n_trials_fit': len(r2s),
            'r2_real': r2_real,
            'r2_shuffle_mean': sh_mean, 'r2_shuffle_std': sh_std,
            'r2_shuffle_median': sh_median,
            'r2_shuffle_min': sh_min, 'r2_shuffle_max': sh_max,
            'beta_shuffle_mean': beta_mean, 'beta_shuffle_std': beta_std,
            'n_clusters_shuffle_mean': avg(ncls),
            'r2_pnt_null_mean': r2_pnt_mean, 'r2_pnt_null_std': r2_pnt_std,
            'z_AB': z_AB, 'z_BC': z_BC,
            'h_a1_mod6_specific': h_a1, 'h_a2_primes_generic': h_a2,
            'verdict': verdict_code,
        })

    print(f"\n  {'Scale':>9}  {'R²_real':>8} {'R²_sh_mn':>9} {'R²_sh_sd':>9} "
          f"{'R²_sh_md':>9} {'R²_PNT_mn':>10} {'z_AB':>7} {'z_BC':>7} "
          f"{'verdict':<16}")
    print(f"  {'-' * 100}")
    for r in summary_rows:
        z_AB_s = f"{r['z_AB']:+.2f}" if not math.isnan(r['z_AB']) else "n/a"
        z_BC_s = f"{r['z_BC']:+.2f}" if not math.isnan(r['z_BC']) else "n/a"
        r2_real_s = f"{r['r2_real']:.4f}" if r['r2_real'] is not None else "n/a"
        r2_pnt_s = f"{r['r2_pnt_null_mean']:.4f}" if r['r2_pnt_null_mean'] is not None else "n/a"
        print(f"  {r['scale']:>9,}  {r2_real_s:>8} {r['r2_shuffle_mean']:>9.4f} "
              f"{r['r2_shuffle_std']:>9.4f} {r['r2_shuffle_median']:>9.4f} "
              f"{r2_pnt_s:>10} {z_AB_s:>7} {z_BC_s:>7}  {r['verdict']:<16}")

    # --- Save per-trial CSV ---
    per_trial_path = os.path.join(RESULTS_DIR, 'shuffle_summary.csv')
    with open(per_trial_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['trial', 'seed', 'scale', 'n_clusters',
                    'beta', 'r_squared', 'se_beta', 'max_d', 'runtime_s'])
        for r in per_trial_rows:
            w.writerow([
                r['trial'], r['seed'], r['scale'], r['n_clusters'],
                f"{r['beta']:.6f}" if r['beta'] is not None else '',
                f"{r['r2']:.6f}" if r['r2'] is not None else '',
                f"{r['se_beta']:.6f}" if r['se_beta'] is not None else '',
                r['max_d'], r['runtime_s'],
            ])
    print(f"\n  Per-trial CSV saved to {per_trial_path}  ({len(per_trial_rows)} rows)")

    # Summary CSV
    summary_path = os.path.join(RESULTS_DIR, 'shuffle_summary_per_scale.csv')
    def f6(v):
        return (f"{v:.6f}" if v is not None and
                not (isinstance(v, float) and math.isnan(v))
                else '')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['scale', 'n_trials_fit', 'r2_real',
                    'r2_shuffle_mean', 'r2_shuffle_std', 'r2_shuffle_median',
                    'r2_shuffle_min', 'r2_shuffle_max',
                    'beta_shuffle_mean', 'beta_shuffle_std',
                    'n_clusters_shuffle_mean',
                    'r2_pnt_null_mean', 'r2_pnt_null_std',
                    'z_AB', 'z_BC',
                    'h_a1_mod6_specific', 'h_a2_primes_generic', 'verdict'])
        for r in summary_rows:
            w.writerow([
                r['scale'], r['n_trials_fit'],
                f6(r['r2_real']),
                f6(r['r2_shuffle_mean']), f6(r['r2_shuffle_std']),
                f6(r['r2_shuffle_median']),
                f6(r['r2_shuffle_min']), f6(r['r2_shuffle_max']),
                f6(r['beta_shuffle_mean']), f6(r['beta_shuffle_std']),
                f"{r['n_clusters_shuffle_mean']:.2f}",
                f6(r['r2_pnt_null_mean']), f6(r['r2_pnt_null_std']),
                f6(r['z_AB']), f6(r['z_BC']),
                r['h_a1_mod6_specific'], r['h_a2_primes_generic'],
                r['verdict'],
            ])
    print(f"  Per-scale summary saved to {summary_path}")

    print(f"\nTotal runtime: {time.time() - T0:.1f}s")


if __name__ == '__main__':
    main()
