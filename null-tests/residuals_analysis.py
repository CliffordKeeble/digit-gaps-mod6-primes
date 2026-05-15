#!/usr/bin/env python3
"""
Residuals of the 200k Power-Law Fit (v2.9 -> v2.10 Task D)
==========================================================

Mr A's fifth-review item #4 (non-blocking, five stars already awarded):
"Twelve data points, R² = 0.979, β = 0.637 ± 0.029. The fit is clean.
Would you indulge me by glancing at the residuals? I do not expect to
find structure there, but with only twelve points a power-law fit can
be very good while masking a slow oscillation or a systematic curvature
that would tell a different story about the cluster spacings."

This task probes the load-bearing §5.2 R² result from the "what could
the residuals be hiding" direction.

Pre-registered hypotheses (briefs/v2_9_to_v2_10_brief.md):
  H_D0 (white noise):
    - Durbin-Watson statistic in [1.5, 2.5]  (no lag-1 autocorrelation)
    - Spearman ρ vs centre with p > 0.05      (no monotonic trend)
    - No significant Lomb-Scargle peak at 95% (if 12 points permit)
  H_D1 (structured residuals): at least one test rejects.

Method:
  1. Recompute the canonical 200k cluster analysis (window=50,
     min_gaps=20, merge_dist=500) on real mod-6 primes.
  2. Fit power law in log-log space; sanity-check against paper
     headline a = 18.2, β = 0.637, R² = 0.979.
  3. Compute residuals r_i = log(spacing_i) - [log(a) + β log(centre_i)].
  4. Diagnostics:
       - Sign pattern + sign-change count
       - Spearman ρ + p
       - Durbin-Watson
       - Lomb-Scargle (acknowledge n=12 is at the edge of tractable)
  5. Plot residuals vs centre.

Outputs:
  - null-tests/results/residuals_200k.csv          (per-point table)
  - null-tests/results/residuals_diagnostics.txt   (test statistics)
  - figures/residuals_200k.png + .svg              (plot)
"""
import math, time, sys, csv, os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SIEVE_LIMIT = 15_000_000
SCALE = 200_000
WINDOW = 50
MIN_GAPS = 20
MERGE_DIST = 500
STEP = 10

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
                  merge_dist=MERGE_DIST, step=STEP):
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


def fit_power_law(centres, spacings):
    """OLS log(spacing) = log(a) + β log(centre). Returns (log_a, β, R², se_β)."""
    n = len(centres)
    log_c = [math.log(c) for c in centres]
    log_g = [math.log(g) for g in spacings]
    mean_x = sum(log_c) / n
    mean_y = sum(log_g) / n
    ss_xx = sum((x - mean_x) ** 2 for x in log_c)
    ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_c, log_g))
    beta = ss_xy / ss_xx
    log_a = mean_y - beta * mean_x
    ss_res = sum((y - (log_a + beta * x)) ** 2 for x, y in zip(log_c, log_g))
    ss_tot = sum((y - mean_y) ** 2 for y in log_g)
    r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    se_beta = math.sqrt(ss_res / ((n - 2) * ss_xx)) if n > 2 and ss_xx > 0 else 0
    return log_a, beta, r_sq, se_beta


def durbin_watson(residuals):
    """DW = Σ(r_i - r_{i-1})² / Σ r_i². ≈ 2 under white noise; <2 positive
    autocorrelation; >2 negative autocorrelation."""
    num = sum((residuals[i] - residuals[i - 1]) ** 2
              for i in range(1, len(residuals)))
    den = sum(r ** 2 for r in residuals)
    return num / den if den > 0 else float('nan')


def sign_changes(residuals):
    """Number of sign changes in the residual sequence."""
    signs = [(1 if r > 0 else (-1 if r < 0 else 0)) for r in residuals]
    # Skip zeros for sign-change counting (treat as continuation)
    last_nonzero = 0
    changes = 0
    for s in signs:
        if s == 0:
            continue
        if last_nonzero != 0 and s != last_nonzero:
            changes += 1
        last_nonzero = s
    return changes, signs


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    T0 = time.time()

    print("=" * 78)
    print("RESIDUALS OF 200k POWER-LAW FIT  (v2.9 -> v2.10 Task D)")
    print(f"  Parameters: window={WINDOW}, min_gaps={MIN_GAPS}, merge_dist={MERGE_DIST}")
    print(f"  Scale: {SCALE:,}")
    print("=" * 78)

    # --- Reproduce the 200k cluster analysis ---
    print("\n[1] Sieving primes...")
    primes = sieve(SIEVE_LIMIT)
    p5 = [p for p in primes if p > 3 and p % 6 == 5]
    p7 = [p for p in primes if p > 3 and p % 6 == 1]
    p5_logs = [math.log10(p) for p in p5]
    p7_logs = [math.log10(p) for p in p7]
    n_use = min(len(p5_logs), len(p7_logs))
    print(f"  p5={len(p5):,}  p7={len(p7):,}  n_use={n_use:,}")

    print("\n[2] Computing gap arrays + clusters at 200k...")
    is_gap1, is_gap2, max_d = compute_gap_arrays(p5_logs[:n_use], p7_logs[:n_use])
    clusters = find_clusters(is_gap1, is_gap2, min(SCALE, max_d))
    print(f"  Clusters at 200k: {len(clusters)}")

    # --- Extract (centre, spacing) pairs ---
    pairs = []
    for i in range(len(clusters) - 1):
        c_left, c_right = clusters[i]['centre'], clusters[i + 1]['centre']
        spacing = c_right - c_left
        centre = (c_left + c_right) / 2.0
        if centre > 0 and spacing > 0:
            pairs.append((centre, spacing))
    n = len(pairs)
    print(f"  (centre, spacing) pairs: {n}")
    if n != 12:
        print(f"  NOTE: paper reports 12 pairs; got {n}. Continuing with {n}.")

    centres = [p[0] for p in pairs]
    spacings = [p[1] for p in pairs]

    # --- Fit power law ---
    log_a, beta, r_sq, se_beta = fit_power_law(centres, spacings)
    a = math.exp(log_a)
    print(f"\n[3] Power-law fit (sanity-check against paper a=18.2, β=0.637, R²=0.979):")
    print(f"  a       = {a:.4f}   (paper: 18.2)")
    print(f"  beta    = {beta:.4f}   (paper: 0.637)")
    print(f"  se(β)   = {se_beta:.4f}")
    print(f"  R²      = {r_sq:.4f}   (paper: 0.979)")

    # --- Residuals ---
    residuals = []
    predicted_log = []
    for c, g in pairs:
        pred = log_a + beta * math.log(c)
        actual = math.log(g)
        residuals.append(actual - pred)
        predicted_log.append(pred)

    print(f"\n[4] Residuals (i, centre, spacing, predicted, residual):")
    for i, ((c, g), pred, r) in enumerate(zip(pairs, predicted_log, residuals), 1):
        sign = '+' if r >= 0 else '-'
        print(f"  {i:>2}: c={c:>11,.1f}  g={g:>7,.0f}  "
              f"log(g)={math.log(g):>7.3f}  log(g_pred)={pred:>7.3f}  "
              f"r={r:>+8.4f} ({sign})")

    # --- Sign pattern ---
    n_changes, signs = sign_changes(residuals)
    sign_str = ' '.join('+' if s > 0 else ('-' if s < 0 else '0') for s in signs)
    expected_changes = (n - 1) / 2
    print(f"\n[5] Sign pattern:")
    print(f"  Signs:     {sign_str}")
    print(f"  Changes:   {n_changes}  (expected under white noise: {expected_changes})")

    # --- Spearman ρ ---
    from scipy.stats import spearmanr
    rho, p_spearman = spearmanr(centres, residuals)
    print(f"\n[6] Spearman ρ (residual vs centre):")
    print(f"  ρ = {rho:.4f}")
    print(f"  p = {p_spearman:.4f}")
    spearman_passes = p_spearman > 0.05

    # --- Durbin-Watson ---
    dw = durbin_watson(residuals)
    print(f"\n[7] Durbin-Watson (lag-1 autocorrelation):")
    print(f"  DW = {dw:.4f}  (white-noise expectation: ≈ 2; H_D0 range: [1.5, 2.5])")
    dw_passes = 1.5 <= dw <= 2.5

    # --- Lomb-Scargle ---
    print(f"\n[8] Lomb-Scargle periodogram (n={n} is small; reporting top peak):")
    try:
        import numpy as np
        from scipy.signal import lombscargle
        # Use log(centre) as the irregular "time" axis since centres are
        # log-spaced (cluster centres grow with the power law).
        t = np.array([math.log(c) for c in centres])
        y = np.array(residuals) - np.mean(residuals)
        # Frequency grid: heuristic over the range of t.
        t_range = t.max() - t.min()
        # n_freqs roughly = n/2; freq range [2π / t_range, n/(2 t_range)].
        f_min = 2 * math.pi / t_range
        f_max = math.pi * n / t_range
        freqs = np.linspace(f_min, f_max, 200)
        power = lombscargle(t, y, freqs, normalize=True)
        peak_idx = int(np.argmax(power))
        peak_power = float(power[peak_idx])
        peak_freq = float(freqs[peak_idx])
        # Approximate 95% significance threshold for normalized periodogram (n_eff small):
        #   under white noise, normalized power follows approximately exp(-power)
        #   per Scargle 1982; 95% threshold = -log(1 - 0.95^(1/M)) where M = n_freqs.
        M = len(freqs)
        thresh_95 = -math.log(1.0 - 0.95 ** (1.0 / M))
        print(f"  Top peak: freq={peak_freq:.4f}  power={peak_power:.4f}")
        print(f"  Approx 95% threshold (Scargle, M={M}): {thresh_95:.4f}")
        ls_passes = peak_power < thresh_95
        print(f"  Significant peak at 95% level: {not ls_passes}")
    except Exception as e:
        peak_freq = peak_power = thresh_95 = float('nan')
        ls_passes = None
        print(f"  Lomb-Scargle skipped: {e}")

    # --- Verdict ---
    print(f"\n{'=' * 78}")
    print("DECISION RULE EVALUATION (H_D0 vs H_D1)")
    print(f"{'=' * 78}")
    print(f"\n  Durbin-Watson in [1.5, 2.5]:    {dw_passes}  (DW = {dw:.4f})")
    print(f"  Spearman p > 0.05:              {spearman_passes}  (p = {p_spearman:.4f})")
    print(f"  No significant Lomb-Scargle peak: {ls_passes}  "
          f"(peak power {peak_power:.4f} vs threshold {thresh_95:.4f})")
    all_pass = dw_passes and spearman_passes and (ls_passes is None or ls_passes)
    print(f"\n  All H_D0 tests pass: {all_pass}")
    verdict = "H_D0 (white noise)" if all_pass else "H_D1 (structured residuals)"
    print(f"  Verdict: {verdict}")

    # --- Save per-point CSV ---
    csv_path = os.path.join(RESULTS_DIR, 'residuals_200k.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['i', 'centre', 'spacing', 'log_centre', 'log_spacing',
                    'predicted_log_spacing', 'residual', 'sign'])
        for i, ((c, g), pred, r) in enumerate(zip(pairs, predicted_log, residuals), 1):
            s = '+' if r > 0 else ('-' if r < 0 else '0')
            w.writerow([i, f"{c:.4f}", g, f"{math.log(c):.6f}",
                        f"{math.log(g):.6f}", f"{pred:.6f}",
                        f"{r:.6f}", s])
    print(f"\n  CSV saved to {csv_path}")

    # --- Save diagnostics txt ---
    diag_path = os.path.join(RESULTS_DIR, 'residuals_diagnostics.txt')
    with open(diag_path, 'w', encoding='utf-8') as f:
        f.write(f"Residuals diagnostics — 200k power-law fit (v2.10 Task D)\n")
        f.write(f"==========================================================\n\n")
        f.write(f"Source: real mod-6 primes, sieve {SIEVE_LIMIT:,}, scale {SCALE:,},\n")
        f.write(f"        window={WINDOW}, min_gaps={MIN_GAPS}, merge_dist={MERGE_DIST},\n")
        f.write(f"        step={STEP}.\n\n")
        f.write(f"Fit:\n")
        f.write(f"  a    = {a:.6f}   (paper: 18.2)\n")
        f.write(f"  beta = {beta:.6f}   (paper: 0.637)\n")
        f.write(f"  se(beta) = {se_beta:.6f}\n")
        f.write(f"  R² = {r_sq:.6f}   (paper: 0.979)\n")
        f.write(f"  n  = {n} (centre, spacing) pairs\n\n")
        f.write(f"Sign pattern:\n")
        f.write(f"  Signs: {sign_str}\n")
        f.write(f"  Sign changes: {n_changes}  (expected under white noise: {expected_changes})\n\n")
        f.write(f"Spearman ρ (residual vs centre):\n")
        f.write(f"  ρ = {rho:.6f}\n")
        f.write(f"  p = {p_spearman:.6f}\n")
        f.write(f"  H_D0 (p > 0.05): {spearman_passes}\n\n")
        f.write(f"Durbin-Watson:\n")
        f.write(f"  DW = {dw:.6f}\n")
        f.write(f"  H_D0 range [1.5, 2.5]: {dw_passes}\n\n")
        f.write(f"Lomb-Scargle:\n")
        if not math.isnan(peak_power):
            f.write(f"  Top peak: freq = {peak_freq:.6f}, power = {peak_power:.6f}\n")
            f.write(f"  95% threshold (Scargle, M=200): {thresh_95:.6f}\n")
            f.write(f"  Significant peak: {not ls_passes}\n")
            f.write(f"  H_D0 (no significant peak): {ls_passes}\n")
        else:
            f.write(f"  Skipped.\n")
        f.write(f"\nVerdict: {verdict}\n")
    print(f"  Diagnostics saved to {diag_path}")

    # --- Plot ---
    print(f"\n[9] Rendering figure...")
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.axhline(0, color='black', lw=0.7, alpha=0.5)
        ax.plot(centres, residuals, color='#1d6b1d', lw=1.5, marker='o',
                markersize=7, label='residuals')
        for i, (c, r) in enumerate(zip(centres, residuals)):
            ax.annotate(str(i + 1), (c, r), fontsize=8,
                        xytext=(5, 5), textcoords='offset points',
                        color='#444')
        ax.set_xscale('log')
        ax.set_xlabel('Cluster-pair centre (digits)')
        ax.set_ylabel(r'Residual  $r_i = \log(\mathrm{spacing}_i) - [\log a + \beta \log(\mathrm{centre}_i)]$')
        ax.set_title(rf'Residuals of 200k power-law fit ($a$={a:.2f}, $\beta$={beta:.4f}, $R^2$={r_sq:.4f}, n={n})')
        ax.grid(True, which='both', linestyle=':', alpha=0.55)
        ax.legend(loc='best')
        fig.tight_layout()
        png_path = os.path.join(FIG_DIR, 'residuals_200k.png')
        svg_path = os.path.join(FIG_DIR, 'residuals_200k.svg')
        fig.savefig(png_path, dpi=140)
        fig.savefig(svg_path)
        plt.close(fig)
        print(f"  PNG: {png_path}")
        print(f"  SVG: {svg_path}")
    except Exception as e:
        print(f"  Figure rendering skipped: {e}")

    print(f"\nTotal runtime: {time.time() - T0:.1f}s")


if __name__ == '__main__':
    main()
