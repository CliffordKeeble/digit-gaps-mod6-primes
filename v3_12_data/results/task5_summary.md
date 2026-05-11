# Task 5 — Instance-4 doubling-pattern test: summary

**Date:** 11 May 2026.
**Pre-registration:** `v3_12_data/briefs/task5_instance_4_doubling_pre_registration.md`.
**N_MAX:** 4000. **Analysis range:** [60, 17600).

## Layer 0 — Anchors

- Strict-23 [90, 200] cluster count: OK.
- Instance 1 (172, 482): OK.
- Instance 2 (952, 1717): OK.

## Layer 1 — Instance-3 upper-edge measurement

- Instance 3 cluster: (2812, 4231); width = 1420.
- Truncated at D_HI: no.

## Layer 2 — Instance-4 detection + doubling-pattern test

**Outcome: (β-broken)**.  Doubling-pattern breakdown: width_ratio = 1.624 outside [2.07, 2.53]; gap_ratio = 1.628 outside [2.07, 2.53]

### All detected instances

| # | Bounded range | Width | Pre-regime gap | Width ratio | Gap ratio | Lands at hi+1 |
|---|---|---|---|---|---|---|
| 1 | (172, 482) | 311 | — | — | — | — |
| 2 | (952, 1717) | 766 | 469 | 2.4630 | — | both |
| 3 | (2812, 4231) | 1420 | 1094 | 1.8538 | 2.3326 | both |
| 4 | (6013, 8318) | 2306 | 1781 | 1.6239 | 1.6280 | both |
| 5 | (10979, 15045) | 4067 | 2660 | 1.7637 | 1.4935 | both |
| 6 | (17539, 17690) (past D_HI) | 152 | 2493 | 0.0374 | 0.9372 | 7 |

**width(4) / width(3) = 1.6239**  (window [2.07, 2.53]).
**gap(3 → 4) / gap(2 → 3) = 1.6280**  (window [2.07, 2.53]).

## Layer 3 — Asymptotic-form refinement

| Form | Parameter(s) | adj R² |
|---|---|---|
| 1 − a/log(D) | a = 0.5190 | 0.0313 |
| 1 − a/log²(D) | a = 4.1801 | 0.0353 |
| blend | a = 0.2251, b = 2.4092 | 0.0350 |

**Outcome: (β-Q4)**.  best adj R² = 0.0353 (< 0.5).

## Structural observations

### Layer 2 outcome — (β-broken), decisively

Both binding ratios at instance-3 → instance-4 fell **far below** the
pre-registered 10% window around 2.3× (the [2.07, 2.53] band):

- **width(4) / width(3) = 1.624** (window [2.07, 2.53]).
- **gap(3 → 4) / gap(2 → 3) = 1.628** (window [2.07, 2.53]).

The doubling-pattern hypothesis at constant ratio ≈ 2.3× is
**falsified**.  Per the brief's framing of (β-broken):
*"publication-strengthening — honest naming of the breakdown
improves the paper."*

### Corrected ratio sequence over five instances

With Layer 1 fixing instance-3's actual width (1420, not the truncated
≥ 929 reported in Task 4b), AND with two additional bounded merged
regimes detected beyond instance 4 (instances 5 and 6, the latter
truncated at D_HI), the full sequence of transition ratios is:

| Transition | Width ratio | Gap ratio |
|------------|-------------|-----------|
| 1 → 2 | 2.463 | — |
| 2 → 3 | **1.854** (was unmeasurable, 2.30× was inferred) | 2.333 |
| 3 → 4 | 1.624 | 1.628 |
| 4 → 5 | 1.764 | 1.494 |

The v4.9 anchor of "≈ 2.3× per transition" was built on **two** data
points (width 1→2 and gap 2→3) that happened to land near 2.3
by coincidence.  Task 5 provides **four** width-ratio data points
and **three** gap-ratio data points; both sequences sit in a **lower
band, roughly [1.5, 1.9]**, not at 2.3×.

The width-ratio sequence (2.46, 1.85, 1.62, 1.76) is decreasing-with-
recovery shape; the gap-ratio sequence (2.33, 1.63, 1.49) is
monotone-decreasing across three observations.  Neither is consistent
with a constant doubling factor.

### Five bounded merged regimes within tested range

| # | Bounded range | Width | Pre-regime gap |
|---|---------------|-------|----------------|
| 1 | (172, 482) | 311 | — |
| 2 | (952, 1717) | 766 | 469 |
| 3 | (2812, 4231) | 1420 | 1094 |
| 4 | (6013, 8318) | 2306 | 1781 |
| 5 | (10979, 15045) | 4067 | 2660 |
| 6 | (17539, 17690) — truncated by D_HI | ≥ 152 | 2493 |

(Instance 6's width is a lower bound; its lower edge is bounded and
within D_HI but its upper edge is at D_HI − 10 — barely entering the
analysis range, so width / gap statistics for the 5 → 6 transition are
not yet measurable.  Width-ratio 0.04 in the table is the
within-range width / instance-5 width and is not the structural
quantity of interest.)

### Auxiliary measurement — 7-series lands first at every upper edge

For each fully-detected regime (instances 2 through 5), recorded the
prime-index n at which each series first reaches digit-length
`upper_edge + 1`:

| Regime | upper_edge + 1 | n_5 | n_7 | First |
|--------|----------------|-----|-----|-------|
| 2 | 1718 | 506 | **503** | 7-series |
| 3 | 4232 | 1116 | **1112** | 7-series |
| 4 | 8319 | 2034 | **2029** | 7-series |
| 5 | 15046 | 3458 | **3452** | 7-series |

**The 7-series lands first at every regime's upper edge** — n_7 < n_5
by 3–6 in each case.  This is a clean per-regime structural fact,
not pre-registered as a hypothesis but recorded as data for §8 Q5's
χ_5-structure question.

A plausible reading (for CinC to evaluate, not Mr Code's territory):
the 7-series is "ahead" in the index race at each regime boundary
because it accumulates digit-length faster on average — but the small
n-gap (3–6 primes) suggests the lead is structural and persistent,
not random drift.

### Layer 3 — (β-Q4) confirmed

Best adj R² = 0.0353 across 176 bins in [60, 17600).  Down from Task
4b's 0.0984 over 36 bins.  Adding more data makes the simple
asymptotic forms fit *worse* in proportional terms — consistent with
the data being structurally alternating (saturated stretches inside
each merged regime; pre-asymptotic stretches between them) rather
than a smooth asymptote.

### Implications for §8 framing

**§8 Q5** (the doubling-pattern question Mr Adversary's cycle-5
review named as the sixth-star path): the doubling-at-2.3× hypothesis
is falsified.  The actual pattern is more nuanced — width and gap
ratios decline from ~2.4 at the first transition to roughly 1.5–1.8
at later transitions.  Honest naming of the breakdown is the
sixth-star content; the empirical anchor for the structural-pattern
reading is *the decelerating ratio sequence*, not constant doubling.

**Auxiliary §8 Q5 angle**: the 7-series-lands-first observation
across four regimes is a clean structural pattern that gives §8 Q5
empirical content connecting to the χ_5 question.  v5.x can offer
this as a publication-strengthening positive finding alongside the
honest-naming-of-the-doubling-breakdown.

**§8 Q4** (asymptotic-density form): unchanged.  No simple
log/log² form captures the alternating structure even at extended
range.  The structural object is the *sequence of bounded merged
regimes*, not a smooth density curve.

**v4.9 § calibration entry suggested**: *"v4.9's anchor of
'≈ 2.3× per transition' was built on two data points (width 1→2 and
gap 2→3) and held until instance-3's truncated upper edge was
resolved at N_MAX = 4000.  With four width-ratios and three
gap-ratios now in hand, the ratio sequence is decelerating, not
constant; the doubling-pattern hypothesis is replaced by an
empirically-anchored decelerating-ratio reading.  The 7-series
lands first at every regime's upper edge — a clean per-regime
structural pattern connecting to §8 Q5's χ_5 question."*

🐕☕⬡

— Mr Code, 11 May 2026 (Paper 3 v5.x Task 5)
