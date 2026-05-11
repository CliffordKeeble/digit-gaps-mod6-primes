# Task 4 Pre-Registration — Density of skipped digit-lengths across [60, 1000]

**Date:** 11 May 2026 (committed before computation per Pattern 19/27)
**Brief origin:** Cliff + CinC, 11 May 2026 (task-queue follow-up after
Task 3 (α)).
**Goal:** Empirical anchor for the asymptotic-density question that
§8 Open Questions points at; produces a single chart for §8 and bridges
to the Mertens-product / log-additive structure literature.

## Question (descriptive, not falsificatory)

Measure the density of combined-skip digit-lengths in the (Π_5, Π_7)
digit-jump landscape across D ∈ [60, 1000]. Report:

1. The cumulative skip count up to each D-value, and the per-decade
   skip fraction.
2. The cluster count per decade (count of maximally-contiguous
   combined-skip runs whose lower edge sits in the decade).
3. The mean cluster width per decade.
4. The fit of asymptotic forms to the per-decade skip-fraction
   measurement.

This is an exploratory measurement, not a falsifier. No (α)/(β)/(γ)
outcomes. The discipline is committing to the protocol so the
resulting numbers can't be cherry-picked or re-binned post-hoc.

## Method (committed)

### Computational

- **N_MAX = 500** for both 5-series (primes ≡ 5 mod 6, p > 3) and
  7-series (primes ≡ 1 mod 6, p > 3). N_MAX = 500 produces D_i ≈ 1500+
  for both series, well beyond the [60, 1000] analysis range.
- **Sieve limit = 200_000** (unchanged from v4.2). Sufficient to source
  N_MAX = 500 primes per series.
- Combined skip set = union of per-series skip sets, restricted to
  D ∈ [60, 1000].
- Skip sets are monotone in n; clusters at high D may extend beyond
  the analysis range; for cluster counting we restrict to clusters
  whose lower edge is ≤ 1000 (and report the cluster's full extent
  separately).

### Binning

10 bins of width 100, with the first bin narrower:

- Bin 1: [60, 100) (width 40)
- Bin 2: [100, 200) (width 100)
- Bin 3: [200, 300) (width 100)
- ...
- Bin 10: [900, 1000) (width 100)

Per bin, compute:

- `bin_width`: D-values in the bin.
- `n_skipped`: count of d-values in [bin_lo, bin_hi) in the combined
  skip set.
- `skip_fraction = n_skipped / bin_width`.
- `n_clusters_starting_in_bin`: count of clusters whose lower edge
  is in [bin_lo, bin_hi).
- `mean_cluster_width`: average width of clusters in this bin (if any).

### Cumulative measurement

For D ∈ {60, 70, 80, …, 1000} (in steps of 10), report cumulative
skip count up to D and instantaneous skip fraction in [D-10, D).

### Fits

Three candidate asymptotic forms for the skip-fraction
f(D) ∈ [0, 1] vs D:

1. **`1 - a / log(D)`** — Mertens-like, one parameter `a`.
2. **`1 - a / log²(D)`** — log² damping, one parameter `a`.
3. **`1 - a / log(D) - b / log²(D)`** — two-parameter blend.

Fit each via least squares to the per-decade `skip_fraction`
data points (using bin midpoints as the D-coordinate). Report
parameter estimates, residual sum of squares, and adjusted R². No
goodness-of-fit threshold is pre-registered as binding — this is
exploratory, the fits are descriptive.

### Chart

Two-panel figure saved as `v3_12_data/results/
task4_density_measurement.png`:

- **Panel A:** per-decade skip fraction vs bin midpoint D, with the
  three fit overlays.
- **Panel B:** cluster count starting in each decade vs bin midpoint D,
  and mean cluster width per decade (twin-y or annotated).

### Outputs

- `v3_12_data/results/task4_density_measurement_per_decade.csv` —
  one row per decade with the columns above.
- `v3_12_data/results/task4_density_measurement_cumulative.csv` —
  one row per D in {60, 70, …, 1000}.
- `v3_12_data/results/task4_density_measurement.png` — the two-panel
  chart.
- `v3_12_data/results/task4_density_measurement_summary.md` —
  per-decade table; fit parameters and R²; one paragraph describing
  what the chart shows; explicit flag if a high-D cluster extends
  beyond the analysis range (the merged-regime cluster from v4.2
  Calibration 1; expected to be present and to extend further at
  N_MAX = 500 vs N_MAX = 250).

## Decisions made beyond the instruction (recorded here so the choices
## bind the run)

- **N_MAX = 500.** Chosen to comfortably exceed D = 1000 in both
  series; the v4.2 N_MAX = 250 produced D ~ 480 max which would not
  cover the analysis range.
- **Bin width 100** (with first bin width 40). 10 bins gives a
  resolution adequate for a single-chart visualisation; finer
  binning would add noise; coarser would erase the transition near
  the merged-regime onset (~D = 172 in v4.2).
- **Bin midpoints as D-coordinate for fits.** Standard. Width-weighted
  least squares would be slightly more honest given the narrower
  first bin; not used here for simplicity — the first bin's narrower
  width is a minor effect on parameter estimates.
- **Adjusted R² as fit-quality metric.** Standard, reported but not
  pre-registered as a selection criterion.

## Stop-on-fail

Per Pattern 75: halt if the run produces a result inconsistent with
the v4.2 calibration anchors — e.g., if the 23 strict clusters in
[90, 200] are not reproduced under N_MAX = 500, or if the
merged-regime cluster's lower edge is not at 172. The skip-set
monotonicity in n means N_MAX = 500 must contain the N_MAX = 250
clusters as substructure.

— CinC + Mr Code, 11 May 2026
🐕☕⬡
