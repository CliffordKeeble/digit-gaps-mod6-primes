# Task 8 — Paper 199 chi_5 running-sum cross-test: summary

**Date:** 17 May 2026.
**Pre-registration:** `v3_12_data/briefs/mr_code_brief_paper_201_task8.md`.
**Runtime:** 3.7s.
**Baseline:** 1000 draws from [200, 4000]; seed 8088; excluding ±50 around evaluation points.

## Anchors

- Anchor A (four n_5 values from D_5 cumulative product): OK.
- Anchor B (S_5(10) = +1, hand-computed reference): OK.
- Anchor C (Paper 199 reference table): no pointer provided; B binding.
- Anchor D (baseline excludes ±50 around evaluation points): OK.

## Evaluation values V_r and percentile ranks

| Regime r | u_r | n_5_r | V_r = S_5(n_5_r) | Percentile rank π_r | Tail |
|---|---|---|---|---|---|
| 2 | 1717 | 506 | -1 | 0.2725 | central |
| 3 | 4231 | 1116 | +3 | 0.5395 | central |
| 4 | 8318 | 2034 | +3 | 0.5395 | central |
| 5 | 15045 | 3458 | -1 | 0.2725 | central |

**# upper-tail (π > 0.75):** 0
**# lower-tail (π < 0.25):** 0
**# central:** 4

**CEI = max(#upper, #lower) = 0**

## Baseline distribution summary

| Statistic | Value |
|---|---|
| n (draws) | 1000 |
| min | -13 |
| max | 21 |
| median | 2.0 |
| mean | 2.868 |
| std | 6.428 |
| 25th percentile | -1.0 |
| 75th percentile | 7.0 |
| IQR width | 8.0 |

## Pre-registered outcome — (α) 

**CEI = 0.**  Pre-registered: CEI ≤ 2 → (α) [P ≈ 0.92 under null]; CEI = 3 → (γ) [P ≈ 0.094]; CEI = 4 → (β) [P ≈ 0.0078].

Outcome: **(α)**.

**Framing update applied to Paper 201 §9 Q4 candidate (d):**  No systematic pattern.  Paper 201 §9 Q4 candidate (d) becomes 'tested with no systematic evidence at four-point cross-test'; the χ_5 candidate weakens relative to candidates (a) and (b).

## Honest-reporting commitments (per brief §9)

- All four evaluation values, percentile ranks, and tail classifications reported.
- No post-hoc adjustment of baseline range, baseline size, exclusion margin, tail thresholds, or test statistic.
- No selection of alternative readings if outcome lands at (α).

## Deviations from pre-registration

None.

## Structural observations (post-run, authored by Mr Code, fact-only)

### 1. CEI = 0 is the lowest possible value

All four V_r land in the central bin (π ∈ [0.25, 0.75]).  Under the
null hypothesis (each π_r uniform on [0, 1]), the probability of all
four landing central is 0.5⁴ = 0.0625 — i.e. CEI = 0 is itself a
mildly extreme outcome in the *absence-of-evidence* direction (most
random draws would land 1-2 evaluation values in a tail).  This
does not modify the pre-registered (α) classification, which is
binding: CEI ≤ 2 → (α) regardless of whether CEI is exactly 0, 1,
or 2.

### 2. V_r pair up by value: V_2 = V_5 = −1, V_3 = V_4 = +3

| Regime r | n_5_r | V_r | π_r |
|----------|-------|-----|-----|
| 2 | 506 | −1 | 0.2725 |
| 5 | 3458 | −1 | 0.2725 |
| 3 | 1116 | +3 | 0.5395 |
| 4 | 2034 | +3 | 0.5395 |

The four evaluation values reduce to two distinct integers (−1 and
+3), each occurring twice.  Whether this within-pair coincidence
carries any structural content connecting regimes 2 & 5 (V = −1)
and regimes 3 & 4 (V = +3) is *not* tested by Task 8's
pre-registered statistic (CEI) and is not for Mr Code to interpret;
it is recorded here as a descriptive fact for CinC.

The integer-valued nature of S_5(n) and the baseline std ≈ 6.4 make
small same-value coincidences across four sparse evaluation points
unsurprising under any model; this fact does not change the (α)
reading.

### 3. V_2 and V_5 are near the lower-tail boundary

Both V_2 = V_5 = −1 have π = 0.2725, just above the strict 0.25
lower-tail cutoff.  At a slightly more generous tail threshold (e.g.
π < 0.30 for lower), two of four would classify as lower-tail,
giving CEI = 2 — still pre-registered (α).  Sensitivity to the
25/75 cutoff is out of scope for Task 8 (brief §10), but the
proximity is recorded honestly so any post-hoc sensitivity
discussion can reference the actual π values rather than re-deriving
them.

### Implications for Paper 201 §9 Q4 candidate (d)

The framing-update per brief §5 (α) is applied as pre-registered:
candidate (d) becomes *"tested with no systematic evidence at
four-point cross-test"*; the χ_5 candidate weakens relative to
candidates (a) (L(s, χ_5) zero spacings) and (b) (additive
distribution of log_10(p) across residue classes).  Mr Adversary
cycle-5 path (ii) honest-naming-of-the-test discipline satisfied.

🐕☕⬡

— Mr Code, 17 May 2026 (Paper 201 v1.2 Task 8)
