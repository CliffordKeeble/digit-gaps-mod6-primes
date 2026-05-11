# Task 4b — F3 formal test + extended density: summary

**Date:** 11 May 2026.
**Pre-registration:** `v3_12_data/briefs/task4b_F3_and_extended_density_pre_registration.md`.
**N_MAX:** 1000. **Analysis range:** [60, 3600).

## Anchors

- Strict-23 [90, 200] cluster count: OK (23).
- Cluster (172, X): X = 482; skip-monotonicity X ≥ 482: OK.

## Layer 1 — F3 formal test

X = 482. Growth = 0 (0.0% of v4.2 width).

**Outcome: (α-F3)**.  null holds — (172, 482) bounded; no extension. F3 does not fire.

## Layer 2 — §8 Q5 bounded merged regime detection

Detection criteria: d_lo ≥ 200, width ≥ 100, bounded edges.

**2 bounded merged regime(s) detected.**

| Lower edge | Upper edge | Width | Lower bounded | Upper bounded | Past analysis range |
|---|---|---|---|---|---|
| 952 | 1717 | 766 | yes | yes | no |
| 2812 | 3740 | 929 | yes | yes | yes |

**Outcome: (β-Q5)**.  2 bounded merged regime(s) detected; quasi-periodic structure empirically anchored at multiple instances.

## Layer 3 — §8 Q4 asymptotic-form refinement

Re-fit on extended decade table (n = 36 bins).

| Form | Parameter(s) | adj R² |
|---|---|---|
| 1 − a/log(D) | a = 0.5699 | 0.0643 |
| 1 − a/log²(D) | a = 3.8107 | 0.0984 |
| 1 − a/log(D) − b/log²(D) | a = -0.0254, b = 3.9738 | 0.0719 |

Pre-registered substantive-improvement threshold: adj R² ≥ 0.5.

**Q4 verdict:** no substantive improvement (best adj R² = 0.0984 < 0.5); structural non-monotonicity persists at larger scales.

## Per-decade table

| Bin | Width | Skipped | Fraction | Clusters starting | Mean width |
|-----|-------|---------|----------|-------------------|------------|
| [60, 100) | 40 | 30 | 0.7500 | 11 | 3.00 |
| [100, 200) | 100 | 79 | 0.7900 | 21 | 17.10 |
| [200, 300) | 100 | 100 | 1.0000 | 0 | — |
| [300, 400) | 100 | 100 | 1.0000 | 0 | — |
| [400, 500) | 100 | 99 | 0.9900 | 1 | 53.00 |
| [500, 600) | 100 | 91 | 0.9100 | 8 | 6.75 |
| [600, 700) | 100 | 77 | 0.7700 | 24 | 3.21 |
| [700, 800) | 100 | 82 | 0.8200 | 17 | 4.82 |
| [800, 900) | 100 | 86 | 0.8600 | 15 | 5.73 |
| [900, 1000) | 100 | 94 | 0.9400 | 6 | 135.33 |
| [1000, 1100) | 100 | 100 | 1.0000 | 0 | — |
| [1100, 1200) | 100 | 100 | 1.0000 | 0 | — |
| [1200, 1300) | 100 | 100 | 1.0000 | 0 | — |
| [1300, 1400) | 100 | 100 | 1.0000 | 0 | — |
| [1400, 1500) | 100 | 100 | 1.0000 | 0 | — |
| [1500, 1600) | 100 | 100 | 1.0000 | 0 | — |
| [1600, 1700) | 100 | 100 | 1.0000 | 0 | — |
| [1700, 1800) | 100 | 96 | 0.9600 | 4 | 20.50 |
| [1800, 1900) | 100 | 85 | 0.8500 | 15 | 7.13 |
| [1900, 2000) | 100 | 84 | 0.8400 | 16 | 5.94 |
| [2000, 2100) | 100 | 84 | 0.8400 | 16 | 3.00 |
| [2100, 2200) | 100 | 75 | 0.7500 | 25 | 3.00 |
| [2200, 2300) | 100 | 77 | 0.7700 | 23 | 3.39 |
| [2300, 2400) | 100 | 78 | 0.7800 | 22 | 3.95 |
| [2400, 2500) | 100 | 83 | 0.8300 | 17 | 4.24 |
| [2500, 2600) | 100 | 87 | 0.8700 | 13 | 6.85 |
| [2600, 2700) | 100 | 90 | 0.9000 | 10 | 8.80 |
| [2700, 2800) | 100 | 97 | 0.9700 | 3 | 36.00 |
| [2800, 2900) | 100 | 99 | 0.9900 | 1 | 929.00 |
| [2900, 3000) | 100 | 100 | 1.0000 | 0 | — |
| [3000, 3100) | 100 | 100 | 1.0000 | 0 | — |
| [3100, 3200) | 100 | 100 | 1.0000 | 0 | — |
| [3200, 3300) | 100 | 100 | 1.0000 | 0 | — |
| [3300, 3400) | 100 | 100 | 1.0000 | 0 | — |
| [3400, 3500) | 100 | 100 | 1.0000 | 0 | — |
| [3500, 3600) | 100 | 100 | 1.0000 | 0 | — |

## Structural observations

**Three bounded merged regimes** are present in `[60, 3600)` once the
original `(172, 482)` is included with the two detected by Q5:

| Regime # | Lower edge | Upper edge | Width | Pre-regime gap | Bounded? |
|----------|------------|------------|-------|----------------|----------|
| 1 | 172 | 482 | 311 | (start of analysis range) | yes |
| 2 | 952 | 1717 | 766 | 469 (in [483, 951]) | yes |
| 3 | 2812 | 3740 | 929 | 1094 (in [1718, 2811]) | upper past D_HI |

- **Both widths and pre-regime gaps roughly double between successive
  regimes** within tested range.  Width ratios: 766 / 311 ≈ 2.46;
  (≥ 929) / 766 ≥ 1.21 (regime 3 truncated).  Pre-regime gap ratio:
  1094 / 469 ≈ 2.33.
- **Q5 (β-Q5) confirmed.** The quasi-periodic-alternation hypothesis
  Task 4 raised is now empirically anchored at three instances.
  `(172, 482)` is *not* structurally isolated.
- **F3 (α-F3) confirmed.** X = 482 unchanged from N_MAX = 250 / 500.
  F3 does not fire.  The first regime is bounded; the empirical
  question shifts from *"does the first regime grow with N_MAX?"*
  (foreclosed: no) to *"how many regimes are there, and how does
  their structure scale?"* (Q5).
- **Q4: simple asymptotic forms still don't fit at extended range.**
  Best adj R² = 0.0984 on `[60, 3600)` (vs 0.144 on Task 4's
  `[60, 1000)`).  Saturated stretches inside each regime (skip
  fraction = 1.000 across 7 consecutive decades in regime 2; 7+ in
  regime 3) alternate with pre-asymptotic stretches (fraction
  0.75–0.95) — a shape no single log / log² damping can capture.

**Per-decade fully-saturated stretches** (skip fraction = 1.000):

- D ∈ [200, 400): regime 1.
- D ∈ [1000, 1700): regime 2 (7 consecutive decades).
- D ∈ [2900, 3600): regime 3 (7+ decades, truncated at D_HI).

### Implications for §8 framing

**§8 Q3** ("first bounded merged regime"): needs replacement.  The
first regime is one of (at least) three; the structural object to
name in §6.4 / §8 is the *sequence* of bounded merged regimes, not
the first instance alone.

**§8 Q4** (asymptotic-density form): unchanged from Task 4 — no
simple asymptotic form fits across the extended range either.

**§8 Q5** (quasi-periodic alternation): now empirically anchored at
three instances within `[60, 3600]`.  Width and pre-regime-gap
doubling between successive regimes is characterised within tested
range; whether this is the asymptotic behaviour (constant ratio in
the limit) or transient (ratio drifts at higher D) is the natural
follow-up question.

### v4.6 / v4.9 §6.4 calibration note

v4.2 Calibration 1 recorded `(172, 482)` as *"the leading edge of
the asymptotic merged regime within N_MAX = 250"*.  Both halves of
that phrase need softening in light of Task 4 + Task 4b:

- "leading edge" → "first instance" (regime 1 of three within tested
  range);
- "asymptotic" → "successive bounded" (the structure is a sequence
  of bounded regimes with alternation, not a single asymptotic
  boundary).

Suggested v4.6 wording: *"The first of (at least) three bounded
merged regimes detected in D ∈ [60, 3600] under N_MAX = 1000:
`(172, 482)`, `(952, 1717)`, and `(2812, 3740)` (third truncated
by analysis range).  Within this range, successive regime widths
grow roughly 2× per step and pre-regime gaps grow similarly."*

🐕☕⬡

— Mr Code, 11 May 2026 (Paper 3 v4.5 Task 4b)
