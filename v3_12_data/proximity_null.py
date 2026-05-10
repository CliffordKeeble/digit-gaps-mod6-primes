#!/usr/bin/env python3
"""Task 2 (Paper 3 v3.15): chi5-boundary proximity null assessment.

§6.6 reports that the end of the 5-series tight-oscillation regime is "within
~10 primes" of the first digital boundary crossing (first onset n=43, first
boundary n=30, lag 13). Mr Adversary asks for a quantitative null. Without
one, "proximity" describes the data rather than pointing at a structural
connection.

Method.
- Tie-desert onset: position n where S_5(n-1) = 0 (or n=1 with S_5(0)=0 by
  convention) AND S_5(n+i) != 0 for i = 0..9. I.e., the first non-tie of a
  run of >= 10 consecutive non-ties. (S_5 here is the running sum of chi5
  over 5-series primes in natural size order.)
- Digit-jump definitions (computed for both per the brief's wording / typo):
    (i) ΔD ≥ 2 (brief's literal computation; first occurs at n=3 — yes, the
        first 5-series prime that causes a digit-skip is p_4=23, jumping
        D from 3 to 5)
    (ii) ΔD ≥ 3 (matches the §7.3 / §6.6 "boundary" framing; first at n=30,
         which is what the brief verification anchor presumes)
  PRIMARY = (ii) per the verification anchor and §6.6 framing. (i) reported
  alongside as the all-jumps comparison.

For each onset, distance to nearest jump (in n-units). Empirical p =
P(any onset within 10 primes of any jump under uniform random placement
of K onsets in [1, 5000]). 10000 shuffles.

Verification gate.
- First tie-desert onset of length ≥ 10 at n=43.
- First boundary (ΔD ≥ 3) at n=30.
- Lag 30 → 43 = 13 primes.
"""
import math
import os
import sys
import csv
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Python 3.11+ has a default int->str conversion limit of 4300 digits.
# Our cumulative product of 5000 5-series primes is ~22000 digits.
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(100_000)

sys.path.insert(0, os.path.dirname(__file__))
from prime_utils import sieve, chi5, five_series_primes

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

SIEVE_LIMIT = 250_000  # 5000 5-series primes need ~10k primes overall (~p_max ~ 105k)
N_MAX = 5_000
DESERT_LEN = 10  # require >= 10 consecutive non-ties
WITHIN = 10
K_SHUFFLES = 10_000
SHUFFLE_BASE_SEED = 42  # numpy default_rng(SHUFFLE_BASE_SEED + trial * 137)


def find_tie_desert_onsets(chi_values, desert_len=DESERT_LEN, n_max=N_MAX):
    """Return list of n's (1-indexed) such that S_5(n) = 0 (a tie at n) AND
    the next desert_len positions S_5(n+1), ..., S_5(n+desert_len) are all
    non-zero. I.e., n is the LAST TIE before a run of >= desert_len consecutive
    non-ties — matches v3.13 §6.1's "first desert n=43 to n=61" framing.

    S_5(0) = 0 by convention. S_5(n) = sum_{i=1}^n chi5(p_i).
    """
    s = 0
    cum = [0]  # cum[0] = S_5(0) = 0
    for c in chi_values[:n_max + desert_len + 5]:
        s += c
        cum.append(s)
    onsets = []
    for n in range(1, n_max + 1):
        if cum[n] != 0:  # need a tie at n
            continue
        ok = True
        for i in range(1, desert_len + 1):
            idx = n + i
            if idx >= len(cum) or cum[idx] == 0:
                ok = False
                break
        if ok:
            onsets.append(n)
    return onsets


def find_jumps_DDelta(D, n_max=N_MAX, dD_min=2):
    """Return n's (1-indexed) where D[n+1] - D[n] >= dD_min.

    D is 1-indexed list (D[0] is index for n=1 ... no wait, we store D as
    0-indexed internally with D[i] = D after first i+1 primes). The "n where
    jump occurs" means the n-th step where D went from D[n-1] (1-indexed
    n=k → array index k-1) to D[n] (array index k).

    Convention: a jump "at n" means: adding the (n+1)-th prime caused
    D[n+1] - D[n] >= dD_min. Per the brief: "the n-values in the 5-series
    at which D_5(n+1) - D_5(n) >= 2". So n is 1-indexed and refers to the
    state BEFORE the jump.
    """
    jumps = []
    for n in range(1, min(n_max, len(D) - 1) + 1):
        # D[n-1] corresponds to D_5(n), D[n] to D_5(n+1)
        if D[n] - D[n - 1] >= dD_min:
            jumps.append(n)
    return jumps


def per_onset_min_dist(onsets, jumps):
    """For each onset, min |n_onset - n_jump| over jumps. Returns sorted list."""
    if not jumps:
        return [None] * len(onsets)
    js = np.array(jumps)
    return [int(np.min(np.abs(js - n))) for n in onsets]


def empirical_proximity_p(K, jumps, n_max, within, n_shuffles, base_seed):
    """For each shuffle: place K onsets uniformly at random in [1, n_max]
    (without replacement to mirror natural's distinct-positions structure).
    Return fraction of shuffles where at least one onset is within `within`
    of any jump."""
    js = np.array(jumps)
    js_sorted = np.sort(js)
    # Build a binary mask of "is_within" for fast lookup
    proximate = np.zeros(n_max + 1, dtype=bool)
    for j in jumps:
        lo = max(1, j - within)
        hi = min(n_max, j + within)
        proximate[lo:hi + 1] = True

    n_any = 0
    n_min_close = []  # null distribution of (min-distance over onsets)
    for trial in range(n_shuffles):
        rng = np.random.default_rng(base_seed + trial * 137)
        # Sample K positions uniformly without replacement from [1, n_max]
        sampled = rng.choice(n_max, size=K, replace=False) + 1  # shift to 1-indexed
        # Min distance from any sampled to any jump
        # Faster: check proximate mask
        any_close = bool(np.any(proximate[sampled]))
        if any_close:
            n_any += 1
        # Also compute min distance for richer null
        min_dist = int(np.min(np.abs(sampled[:, None] - js_sorted[None, :])))
        n_min_close.append(min_dist)
    return n_any / n_shuffles, np.array(n_min_close)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Sieving primes up to {SIEVE_LIMIT}...")
    primes = sieve(SIEVE_LIMIT)
    p5 = five_series_primes(primes)
    print(f"  5-series primes: {len(p5)} (need >= {N_MAX})")
    if len(p5) < N_MAX:
        print(f"  ERROR: need at least {N_MAX} 5-series primes")
        sys.exit(1)

    chi_values = [chi5(p) for p in p5[:N_MAX + DESERT_LEN + 10]]

    # ---- Compute D for both series (just 5-series for jumps; brief's verification
    # only refers to 5-series jumps) ----
    print(f"\nComputing D_5(n) up to n = {N_MAX} via Python int product...")
    prod = 1
    D = []
    for p in p5[:N_MAX + 1]:
        prod *= p
        D.append(len(str(prod)))
    print(f"  D_5(1) = {D[0]}, D_5({N_MAX}) = {D[N_MAX - 1]}")

    # ---- Find onsets ----
    print(f"\n{'='*72}")
    print(f"Tie-desert onsets (run of >= {DESERT_LEN} consecutive non-ties)")
    print(f"{'='*72}")
    onsets = find_tie_desert_onsets(chi_values, DESERT_LEN, N_MAX)
    K = len(onsets)
    print(f"  K = {K} onsets in n in [1, {N_MAX}]")
    if K > 0:
        print(f"  First onset: n = {onsets[0]}")
        print(f"  First 10 onsets: {onsets[:10]}")
        print(f"  Last 5 onsets: {onsets[-5:]}")

    # ---- Find jumps under multiple definitions ----
    jumps_dD2 = find_jumps_DDelta(D, N_MAX, dD_min=2)
    jumps_dD3 = find_jumps_DDelta(D, N_MAX, dD_min=3)
    L_dD2 = len(jumps_dD2)
    L_dD3 = len(jumps_dD3)

    # Paper-specific boundaries: the ones v3.13 §7.3 named.
    # B1 is the first 3-digit jump where D crosses 60 (D_5(n)=59 → D_5(n+1)=62, n=30).
    # B2: 3-digit jump where D crosses 80 (n=38, D 79→82).
    # B3: D~112 per §7.3.
    # B4: D~123 per §7.3.
    # Algorithm: a "named boundary" is a 3-digit jump whose pre-jump D value
    # is in {59, 79, ~110-112, ~121-123}. Find the FIRST 3-digit jump for
    # each target D-band.
    paper_boundaries = []
    target_D_bands = [(58, 62), (78, 82), (108, 114), (120, 125)]
    for lo, hi in target_D_bands:
        # Find first 3-digit jump with D[n-1] in [lo, hi]
        for n in jumps_dD3:
            d_pre = D[n - 1]
            if lo <= d_pre <= hi:
                paper_boundaries.append((n, d_pre, D[n]))
                break

    print(f"\n{'='*72}")
    print(f"Digit-jump positions in n in [1, {N_MAX}]")
    print(f"{'='*72}")
    print(f"  (i) ΔD ≥ 2 (brief's literal): L = {L_dD2}")
    if L_dD2 > 0:
        print(f"      First jump at n = {jumps_dD2[0]} (D_5({jumps_dD2[0]}) = "
              f"{D[jumps_dD2[0] - 1]} → D_5({jumps_dD2[0] + 1}) = "
              f"{D[jumps_dD2[0]]})")
    print(f"  (ii) ΔD ≥ 3 (all 3-digit jumps): L = {L_dD3}")
    if L_dD3 > 0:
        print(f"      First 3-digit jump at n = {jumps_dD3[0]} (D_5({jumps_dD3[0]}) = "
              f"{D[jumps_dD3[0] - 1]} → D_5({jumps_dD3[0] + 1}) = "
              f"{D[jumps_dD3[0]]})")
    print(f"  (iii) Paper-named boundaries B1-B4 (PRIMARY for §6.6 proximity claim):")
    for i, (n, d_pre, d_post) in enumerate(paper_boundaries, 1):
        print(f"      B{i}: n = {n}, D {d_pre} → {d_post}")
    paper_boundary_ns = [b[0] for b in paper_boundaries]
    L_paper = len(paper_boundary_ns)

    # ---- Verification gate ----
    print(f"\n{'='*72}")
    print("Verification gate")
    print(f"{'='*72}")
    fail = False
    if onsets[0] != 43:
        print(f"  FAIL: first onset = {onsets[0]} (expected 43)")
        fail = True
    else:
        print(f"  OK: first onset n = {onsets[0]}")
    # n=30 is the paper's "boundary 1" specifically — verify it's present in
    # the 3-digit jumps list (not necessarily the first; the FIRST 3-digit
    # jump is at n=18, but boundary 1 is the labelled one at n=30).
    if 30 not in jumps_dD3:
        print(f"  FAIL: n=30 not in ΔD≥3 jumps")
        fail = True
    else:
        idx = jumps_dD3.index(30)
        print(f"  OK: n=30 is the {idx+1}th 3-digit jump in 5-series "
              f"(first 3-digit jump is at n={jumps_dD3[0]}; n=30 is paper boundary 1)")
    expected_lag = onsets[0] - 30
    if expected_lag != 13:
        print(f"  FAIL: lag from n=30 to first onset = {expected_lag} (expected 13)")
        fail = True
    else:
        print(f"  OK: lag from boundary 1 (n=30) to first onset (n={onsets[0]}) = {expected_lag}")
    if fail:
        print("\n  HALT: anchor mismatch.")
        sys.exit(1)

    # ---- Per-onset min distance (natural) ----
    print(f"\n{'='*72}")
    print("Per-onset distance to nearest digit-jump (natural)")
    print(f"{'='*72}")
    for label, jumps, L in [
        ('(i) ΔD ≥ 2', jumps_dD2, L_dD2),
        ('(ii) ΔD ≥ 3 (all 3-digit jumps)', jumps_dD3, L_dD3),
        ('(iii) paper boundaries B1-B4 [PRIMARY]', paper_boundary_ns, L_paper),
    ]:
        dists = per_onset_min_dist(onsets, jumps)
        srt = sorted(dists)
        n_within = sum(1 for d in dists if d is not None and d <= WITHIN)
        median = srt[len(srt) // 2] if srt and srt[0] is not None else None
        print(f"\n  {label}: jumps L = {L}")
        if not jumps:
            print("    (no jumps; skipping distance computation)")
            continue
        print(f"    First-onset distance: {dists[0]}  "
              f"(onset n={onsets[0]} ↔ nearest jump)")
        print(f"    median min-distance over all {K} onsets: {median}")
        print(f"    range: {min(dists)} … {max(dists)}")
        print(f"    onsets within {WITHIN} of a jump: {n_within} / {K}")
        # Distribution percentiles
        srt_arr = np.array(srt)
        for pct in (5, 25, 50, 75, 95):
            v = np.percentile(srt_arr, pct)
            print(f"    {pct:>2}th percentile: {v:.1f}")

    # ---- Empirical null: P(any onset within `within` of any jump) ----
    print(f"\n{'='*72}")
    print(f"Random-placement null: K = {K_SHUFFLES} shuffles, "
          f"K = {len(onsets)} onsets uniform in [1, {N_MAX}]")
    print(f"{'='*72}")

    null_rows = []
    for label, jumps, L in [
        ('(i) ΔD ≥ 2', jumps_dD2, L_dD2),
        ('(ii) ΔD ≥ 3 (all 3-digit jumps)', jumps_dD3, L_dD3),
        ('(iii) paper boundaries B1-B4 [PRIMARY]', paper_boundary_ns, L_paper),
    ]:
        if not jumps:
            continue
        # Natural test: any onset within `within` of any jump?
        natural_dists = per_onset_min_dist(onsets, jumps)
        natural_min = min(d for d in natural_dists if d is not None)
        natural_any_close = (natural_min <= WITHIN)

        # Empirical null
        p_emp, null_min_dists = empirical_proximity_p(
            K, jumps, N_MAX, WITHIN, K_SHUFFLES, SHUFFLE_BASE_SEED)

        # Also: where does natural's overall-min fall in the null overall-min distribution?
        p_min = float((null_min_dists <= natural_min).sum()) / K_SHUFFLES

        print(f"\n  {label}:")
        print(f"    Natural overall min-distance (any onset to any jump): {natural_min}")
        print(f"    Natural any-onset-within-{WITHIN}? {'YES' if natural_any_close else 'NO'}")
        print(f"    Null P(any onset within {WITHIN} of any jump) = "
              f"{p_emp:.4f} ({int(p_emp * K_SHUFFLES)}/{K_SHUFFLES})")
        print(f"    Null P(overall min ≤ natural min = {natural_min}) = "
              f"{p_min:.4f}")
        # Null distribution percentiles
        for pct in (5, 25, 50, 75, 95):
            v = float(np.percentile(null_min_dists, pct))
            print(f"    Null overall-min {pct:>2}th pct: {v:.1f}")

        null_rows.append({
            'definition': label,
            'L': L,
            'natural_min': natural_min,
            'natural_any_close': natural_any_close,
            'p_within': p_emp,
            'p_overall_min': p_min,
            'null_min_dists': null_min_dists,
        })

    # ---- Verdict ----
    print(f"\n{'='*72}")
    print("Brief scenario classification (using ΔD ≥ 3 PRIMARY)")
    print(f"{'='*72}")
    primary = [r for r in null_rows if 'PRIMARY' in r['definition']][0]
    p = primary['p_within']
    if p < 0.10:
        verdict = ("(a) p < 0.10: proximity is meaningfully unlikely under null; "
                   "'concurrent' framing is supported quantitatively.")
    elif p <= 0.50:
        verdict = ("(b) p in [0.10, 0.50]: proximity is plausible but not "
                   "striking; soften to 'co-located at the same scale' with "
                   "the null acknowledged.")
    else:
        verdict = ("(c) p > 0.50: proximity is statistically unremarkable; "
                   "retract any structural framing of the proximity claim. "
                   "Pattern 75 / fourth retraction candidate.")
    print(f"  Empirical p = {p:.4f}")
    print(f"  -> {verdict}")

    # ---- One-line summary ----
    print(f"\n{'='*72}")
    print("One-line summary for §6.6")
    print(f"{'='*72}")
    sentence = (
        f"K = {K} tie-desert onsets and L = {primary['L']} paper-defined "
        f"boundaries B1-B4 (n = {paper_boundary_ns}) in n ≤ {N_MAX}; "
        f"empirical p = {p:.4f} for at least one onset within {WITHIN} primes "
        f"of a boundary under uniform-random placement of K onsets."
    )
    print(f"\n  {sentence}")

    # ---- Save CSVs ----
    onsets_path = os.path.join(RESULTS_DIR, 'v3_15_task2_onsets_jumps.csv')
    with open(onsets_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['type', 'n', 'D_at_n', 'D_at_n_plus_1'])
        for n in onsets:
            w.writerow(['onset', n, D[n - 1] if n - 1 < len(D) else '',
                        D[n] if n < len(D) else ''])
        for n in jumps_dD3:
            w.writerow(['boundary_dD3', n, D[n - 1], D[n]])
        for n in jumps_dD2:
            w.writerow(['jump_dD2', n, D[n - 1], D[n]])
    print(f"\n  Saved: {onsets_path}")

    summary_path = os.path.join(RESULTS_DIR, 'v3_15_task2_summary.csv')
    with open(summary_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['definition', 'K_onsets', 'L_jumps', 'natural_min_dist',
                    'natural_any_within_10', 'empirical_p_within_10',
                    'empirical_p_overall_min'])
        for r in null_rows:
            w.writerow([r['definition'], K, r['L'], r['natural_min'],
                        int(r['natural_any_close']),
                        f"{r['p_within']:.6f}",
                        f"{r['p_overall_min']:.6f}"])
    print(f"  Saved: {summary_path}")

    # ---- Plot ----
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [warning] matplotlib unavailable; skipping plot")
        return

    fig, axes = plt.subplots(2, 1, figsize=(11, 7))

    # Top panel: timeline of onsets and jump definitions
    ax = axes[0]
    n_plot_max = 500
    onsets_plot = [n for n in onsets if n <= n_plot_max]
    jumps_dD2_plot = [n for n in jumps_dD2 if n <= n_plot_max]
    jumps_dD3_plot = [n for n in jumps_dD3 if n <= n_plot_max]
    paper_b_plot = [n for n in paper_boundary_ns if n <= n_plot_max]

    ax.plot(onsets_plot, [4] * len(onsets_plot), '|', color='#9467bd',
            markersize=18, markeredgewidth=2,
            label=f'tie-desert onsets ({len(onsets_plot)}/{K} shown)')
    ax.plot(paper_b_plot, [3] * len(paper_b_plot), '|', color='#2ca02c',
            markersize=18, markeredgewidth=2.5,
            label=f'paper boundaries B1-B4 ({len(paper_b_plot)}/{L_paper} shown)')
    ax.plot(jumps_dD3_plot, [2] * len(jumps_dD3_plot), '|', color='#d62728',
            markersize=10, markeredgewidth=1.4, alpha=0.6,
            label=f'all 3-digit jumps ΔD ≥ 3 ({len(jumps_dD3_plot)} shown)')
    ax.plot(jumps_dD2_plot, [1] * len(jumps_dD2_plot), '|', color='#888',
            markersize=8, markeredgewidth=1.0, alpha=0.5,
            label=f'all jumps ΔD ≥ 2 ({len(jumps_dD2_plot)} shown)')
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(['ΔD ≥ 2', 'ΔD ≥ 3', 'B1-B4 (PRIMARY)', 'onsets'])
    ax.set_xlabel(f'n (5-series prime index, showing 1–{n_plot_max})')
    ax.set_xlim(0, n_plot_max)
    ax.set_ylim(0.5, 4.5)
    ax.set_title('Timeline of tie-desert onsets vs digit-jumps')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, axis='x', alpha=0.3)

    # Bottom panel: null distribution of overall min-distance under PRIMARY
    ax = axes[1]
    primary_dists = primary['null_min_dists']
    bins = np.arange(0, max(int(primary_dists.max()) + 2, WITHIN + 5), 1)
    ax.hist(primary_dists, bins=bins, color='#4c72b0', alpha=0.85,
            edgecolor='black', linewidth=0.4,
            label=f'null overall-min distance ({K_SHUFFLES} shuffles)')
    ax.axvline(primary['natural_min'], color='red', linestyle='--', linewidth=1.7,
               label=f"natural min = {primary['natural_min']}")
    ax.axvline(WITHIN + 0.5, color='gray', linestyle=':', linewidth=1.3,
               label=f'within-{WITHIN} threshold')
    ax.set_xlabel('Overall min distance from any onset to any paper boundary (B1-B4)')
    ax.set_ylabel(f'Count out of {K_SHUFFLES}')
    ax.set_title(
        f"Random-placement null vs natural's min distance "
        f"(empirical p = {primary['p_within']:.3f})"
    )
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle('Paper 3 v3.15 Task 2 — §6.6 chi5-boundary proximity null')
    fig.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, 'v3_15_task2_proximity_null.png')
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"  Saved: {plot_path}")


if __name__ == '__main__':
    main()
