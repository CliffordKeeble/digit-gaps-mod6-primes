# Task 4 — density of skipped digit-lengths [60, 1000]: summary

**Date:** 11 May 2026.
**Pre-registration:** `v3_12_data/briefs/task4_density_measurement_pre_registration.md`.

## Anchors

- Strict-23 [90, 200] cluster count under N_MAX = 500: **OK**.
- Merged-regime cluster lower edge = 172: **OK**. Cluster at N_MAX = 500 is `(172, 482)` (was `(172, 482)` at N_MAX = 250). Skip-set monotonicity preserved.

## Per-decade skip statistics

| Bin | Width | Skipped d's | Fraction | Clusters starting | Mean cluster width |
|-----|-------|-------------|----------|-------------------|--------------------|
| [60, 100) | 40 | 30 | 0.7500 | 11 | 3.00 |
| [100, 200) | 100 | 79 | 0.7900 | 21 | 17.10 |
| [200, 300) | 100 | 100 | 1.0000 | 0 | — |
| [300, 400) | 100 | 100 | 1.0000 | 0 | — |
| [400, 500) | 100 | 99 | 0.9900 | 1 | 53.00 |
| [500, 600) | 100 | 91 | 0.9100 | 8 | 6.75 |
| [600, 700) | 100 | 77 | 0.7700 | 24 | 3.21 |
| [700, 800) | 100 | 82 | 0.8200 | 17 | 4.82 |
| [800, 900) | 100 | 86 | 0.8600 | 15 | 5.73 |
| [900, 1000) | 100 | 94 | 0.9400 | 6 | 132.00 |

## Asymptotic-form fits to skip fraction

| Form | Parameter(s) | RSS | adj R² |
|------|--------------|-----|--------|
| `1 − a/log(D)` | a = 0.7003 | 0.078280 | 0.0941 |
| `1 − a/log²(D)` | a = 3.9446 | 0.073977 | 0.1439 |
| `1 − a/log(D) − b/log²(D)` | a = -0.0583, b = 4.2639 | 0.073952 | 0.0372 |

## Chart

`v3_12_data/results/task4_density_measurement.png` — two-panel figure:

- Panel A: per-decade skip fraction vs bin midpoint D, with three fit overlays.
- Panel B: cluster count starting in decade, with mean cluster width (log scale, twin-y) overlaid.

## Cumulative skip count

At D = 60 (start): 0 skipped.
At D = 100: 30 skipped of 40 in [60, 100).
At D = 200: 109 skipped of 140 in [60, 200).
At D = 500: 408 skipped of 440 in [60, 500).
At D = 1000: 838 skipped of 940 in [60, 1000).

Full cumulative trace at every 10th D in `task4_density_measurement_cumulative.csv`.

## Structural observations (fact, not interpretation)

The per-decade skip fraction is **non-monotonic** across [60, 1000]:

- climbs to saturation at `[200, 400)` (fraction = 1.000);
- dips at `[600, 700)` to 0.770 (below the [60, 100) starting value);
- partially recovers toward `[900, 1000)` (fraction 0.940).

None of the three pre-registered asymptotic forms — `1 − a/log(D)`,
`1 − a/log²(D)`, and the two-parameter blend — fits the per-decade
data well (best adj R² = 0.144 for `1 − a/log²(D)`; the blend's
adj R² = 0.037 is *worse* after the parameter penalty). The data
has structure these forms cannot capture.

**Merged-regime cluster does not extend at N_MAX = 500.** The
`(172, 482)` cluster identified at N_MAX = 250 has the same `(172,
482)` extent at N_MAX = 500. Skip-set monotonicity preserves the
cluster; it does not extend because d = 483 is landed on by one of
the series. The merged regime is structurally bounded at d = 482,
not a leading-edge artefact of N_MAX = 250.

**Cluster structure re-appears after the merged regime.** Within
`[483, 1000)` there are 71 new clusters distributed across the
upper decades (1 in [400, 500), 8 in [500, 600), 24 in [600, 700),
17 in [700, 800), 15 in [800, 900), 6 in [900, 1000)). The high
mean cluster width of 132.0 in `[900, 1000)` suggests a *second*
wide cluster forming at the upper edge of the analysis range —
possibly the leading edge of a second merged regime, paralleling
the (172, 482) structure at higher D. v4.3-able follow-up: extend
the analysis range with higher N_MAX to confirm or refute the
second-merged-regime hypothesis.

**Implication for §8 framing.** The "asymptotic density approaches
1" reading of v4.2's merged-regime observation is **not supported
across [60, 1000]**. The (Π_5, Π_7) digit-jump landscape exhibits
quasi-periodic merged / pre-asymptotic alternation at the decade
scale, not monotonic saturation. The asymptotic-density question
is more nuanced than a single-form fit captures; CinC may want to
re-frame §8 Q1 to reflect this richer structure, and the
Mertens-product / log-additive literature connection (per
ChatGPT's framing) may need to address the merged → unmerged
oscillation rather than a single saturation rate.

🐕☕⬡

— Mr Code, 11 May 2026 (Paper 3 v4.5 Task 4)
