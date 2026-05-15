#!/usr/bin/env python3
"""
Synchronisation-Budget Null Comparison (v2.6 -> v2.7 Task 1)
=============================================================

v2.6 paper, section 5.4, reports a cumulative synchronisation budget that
converges near 6% at full scale (3.25M digits) but does not compare it to
the null model. This script extends the existing null framework to compute
the synch-budget metric per trial and reports mean, std, and z-score
against the real-prime value.

Definition (per v2.6 section 5.4 and brief):
  budget = total digit-space inside 100% synchronisation windows / max_d
where a "100% synchronisation window" is detected with the same
parameters as paper section 5.2: window=50, min_gaps>=20, cb==ca
(every gap in the window is coincident across both series), with
adjacent windows merged with merge_dist=500 into clusters. The budget
sums the per-cluster span over the full digit range.

Parameters: full scale (max_d ~ 3.25M), 10 trials. Matches existing
universal-statistics null at full scale; no escalation per the brief.

SEED: trial * 137 + 42 (consistent with full_null_model.py and other null-tests).
"""
import math, random, time, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
N_TRIALS = 10
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


def find_clusters(is_gap1, is_gap2, max_d, window=50, min_gaps=20, merge_dist=500):
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
                             'span': c_end - c_start,
                             'start': c_start, 'end': c_end})
            c_start, c_end = s, s + window
    clusters.append({'centre': (c_start + c_end) // 2,
                     'span': c_end - c_start,
                     'start': c_start, 'end': c_end})
    return clusters


def synch_budget(clusters, max_d):
    """Cumulative synch budget: total digit-space inside 100% sync clusters / max_d."""
    if not clusters or max_d <= 0:
        return 0.0, 0
    total_span = sum(c['span'] for c in clusters)
    return total_span / max_d, total_span


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
    print("SYNCHRONISATION-BUDGET NULL COMPARISON  (v2.6 -> v2.7 Task 1)")
    print(f"  Parameters: window=50, min_gaps>=20, merge_dist=500")
    print(f"  Scale: full (max_d derived from sieve to {SIEVE_LIMIT:,})")
    print(f"  Trials: {N_TRIALS}")
    print("=" * 72)

    # --- Real primes ---
    print("\n[1] Sieving primes...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    p5_logs = [math.log10(p) for p in p5]
    p7_logs = [math.log10(p) for p in p7]
    n_use = min(len(p5_logs), len(p7_logs))
    print(f"  5-series: {len(p5):,}, 7-series: {len(p7):,}, n_use={n_use:,}")

    print("\n[2] Real-prime gap arrays + clusters (full scale)...")
    t1 = time.time()
    is_gap1, is_gap2, max_d_real = compute_gap_arrays(p5_logs[:n_use], p7_logs[:n_use])
    real_cl = find_clusters(is_gap1, is_gap2, max_d_real)
    budget_real, span_real = synch_budget(real_cl, max_d_real)
    print(f"  max_d = {max_d_real:,}")
    print(f"  clusters = {len(real_cl)}")
    print(f"  total span = {span_real:,}")
    print(f"  budget_real = {budget_real:.6f} ({100 * budget_real:.4f}%)")
    print(f"  [{time.time() - t1:.1f}s]")

    # --- Null trials ---
    print(f"\n[3] Running {N_TRIALS} null trials at full scale...")
    null_budgets = []
    null_spans = []
    null_max_d = []
    null_cluster_counts = []
    null_per_trial = []

    for trial in range(N_TRIALS):
        t1 = time.time()
        seed = trial * 137 + 42
        logs1, logs2 = generate_pseudo_primes(SIEVE_LIMIT, seed=seed)
        n_null = min(len(logs1), len(logs2), n_use)
        ng1, ng2, nmax = compute_gap_arrays(logs1[:n_null], logs2[:n_null])
        ncl = find_clusters(ng1, ng2, nmax)
        b, sp = synch_budget(ncl, nmax)
        null_budgets.append(b)
        null_spans.append(sp)
        null_max_d.append(nmax)
        null_cluster_counts.append(len(ncl))
        null_per_trial.append((trial, seed, nmax, len(ncl), sp, b))
        print(f"  Trial {trial:2d}: max_d={nmax:>9,}  clusters={len(ncl):>3}  "
              f"span={sp:>8,}  budget={b:.6f} ({100*b:.4f}%)  [{time.time()-t1:.1f}s]")

    # --- Summary ---
    print(f"\n{'=' * 72}")
    print("SYNCH-BUDGET SUMMARY")
    print(f"{'=' * 72}")

    null_mean = avg(null_budgets)
    null_std = std_dev(null_budgets)
    z = (budget_real - null_mean) / null_std if null_std > 0 else float('nan')

    print(f"\n  {'Metric':<25} {'Value':>14}")
    print(f"  {'-' * 41}")
    print(f"  {'budget_real':<25} {budget_real:>14.6f}")
    print(f"  {'budget_null_mean':<25} {null_mean:>14.6f}")
    print(f"  {'budget_null_std':<25} {null_std:>14.6f}")
    print(f"  {'z_score':<25} {z:>14.3f}")
    print(f"  {'budget_real (%)':<25} {100 * budget_real:>14.4f}")
    print(f"  {'budget_null_mean (%)':<25} {100 * null_mean:>14.4f}")
    print(f"  {'budget_null_std (%)':<25} {100 * null_std:>14.4f}")
    print(f"\n  Null range: [{min(null_budgets):.6f}, {max(null_budgets):.6f}]")
    n_ge = sum(1 for b in null_budgets if b >= budget_real)
    print(f"  Null trials with budget >= real: {n_ge}/{N_TRIALS}")

    # --- Save per-trial CSV ---
    csv_path = os.path.join(RESULTS_DIR, 'synch_budget_null.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['trial', 'seed', 'max_d', 'n_clusters', 'total_span', 'budget'])
        w.writerow(['real', '', max_d_real, len(real_cl), span_real, budget_real])
        for trial, seed, nmax, ncl, sp, b in null_per_trial:
            w.writerow([trial, seed, nmax, ncl, sp, b])
    print(f"\n  Per-trial data saved to {csv_path}")

    # --- Save summary CSV ---
    summary_path = os.path.join(RESULTS_DIR, 'synch_budget_summary.csv')
    with open(summary_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['metric', 'value'])
        w.writerow(['budget_real', budget_real])
        w.writerow(['budget_null_mean', null_mean])
        w.writerow(['budget_null_std', null_std])
        w.writerow(['z_score', z])
        w.writerow(['n_trials', N_TRIALS])
        w.writerow(['null_min', min(null_budgets)])
        w.writerow(['null_max', max(null_budgets)])
    print(f"  Summary saved to {summary_path}")

    print(f"\nTotal runtime: {time.time() - T0:.1f}s")


if __name__ == '__main__':
    main()
