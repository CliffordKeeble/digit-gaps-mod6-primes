# Task 4b Pre-Registration — F3 formal test + extended density [60, 3000]

**Date:** 11 May 2026 (committed before computation per Pattern 19/27)
**Brief origin:** Cliff + CinC, 11 May 2026, post-Task-4 follow-on.
**Three layers:** F3 formal test (binding falsifier); §8 Q5 second
merged-regime characterisation (exploratory); §8 Q4 asymptotic-form
refinement (exploratory).

## Layer 1 — F3 formal test (binding)

### Concept (from v4.4 §6.3, motivation strengthened in v4.5)

"Merged-regime supersession": whether the `(172, 482)` cluster grows
as N_MAX grows in a way that supersedes the discrete cluster-and-gap
typology of §6.3, making the merged regime the dominant asymptotic
structural object.

### Null

The `(172, 482)` merged regime is a fixed structural feature with a
ceiling independent of N_MAX; its upper edge does not extend as N_MAX
grows beyond v4.2's measurement (482 at N_MAX = 250, 482 at N_MAX =
500 per Task 4).

### Binding trigger

At N_MAX = 1000, the cluster containing d = 172 extends to `(172, X)`
with **X > 600** (≥ 25% growth from v4.2's measured extent of 310
digit-lengths; under a roughly 4× increase in N_MAX from N_MAX = 250).

### Threshold motivation (from v4.5)

- X ≤ 513 (≤ 10% growth) → consistent with edge-finding under
  continued enumeration; null holds.
- 513 < X ≤ 600 → between-zone; not a binding fire.
- X > 600 (≥ 25% growth) → substantially exceeds edge-finding null;
  merged regime is growing as a fraction of accessible digit-length
  range, not asymptotically bounded; F3 fires.

### Pre-registered outcomes

- **(α-F3) X ≤ 482.** Skip-set monotonicity holds (in fact strictly:
  X cannot decrease as N_MAX grows). Task 4's `(172, 482)` finding
  is preserved. F3 does not fire. Foreclosure from Task 4's
  d = 483 landing record confirmed.
- **(β-F3) 482 < X ≤ 600.** Between-zone. Would require Task 4's
  d = 483 landing record to be incorrect or skip-monotonicity to
  fail in some unexpected way. Major surprise; halt and consult CinC.
- **(γ-F3) X > 600.** F3 fires. Merged-regime supersession is
  empirically anchored. Retraction 4 of v4.8's "first bounded merged
  regime" framing; v4.9 substantially rewrites §6.3 and §8 Q3.

### Expected outcome

(α-F3), with X = 482. Task 4 found d = 483 lands at N_MAX = 500;
skip-set monotonicity guarantees d = 483 remains landed at all higher
N_MAX. The merged regime is foreclosed from extending past 482 at any
N_MAX ≥ 500.

Running F3 anyway is the discipline-binding step: the pre-registered
null is verified, not assumed.

## Layer 2 — §8 Q5 empirical characterisation (exploratory)

### Concept

Detect and characterise any bounded merged regimes at D > 482 within
the extended analysis range. Task 4 noted the `[900, 1000)` decade
has mean cluster width 132 — the first candidate for a second merged
regime.

### Detection definition (committed)

A "bounded merged regime" in the extended range is a cluster
satisfying:

1. Lower edge d_lo ≥ 200 (excludes the `(172, 482)` regime and small
   pre-merged structure).
2. Width ≥ 100 digit-lengths.
3. d_lo + 1 not in skip set (lower edge is bounded — preceded by a
   landing).
4. d_hi + 1 not in skip set (upper edge is bounded — followed by a
   landing).

For each detected regime, record: lower edge d_lo, upper edge d_hi,
width, skip fraction in the decade(s) immediately preceding and
following, mean cluster width in the decade(s) immediately preceding
and following.

### Pre-registered outcomes

- **(α-Q5) No second bounded merged regime detected** in
  `[200, ~3000]` (other than the existing `(172, 482)`). The
  `[900, 1000)` candidate from Task 4 does not satisfy the width-≥-100
  + bounded-edges criteria; the quasi-periodic-alternation hypothesis
  is weakened. `(172, 482)` may be structurally isolated.
- **(β-Q5) One or more bounded merged regimes detected.** Quasi-periodic
  structure empirically anchored at multiple instances; characterise
  spacing, onset, width pattern. §8 Q5 gains empirical content; v4.6
  §6.4 may absorb a "merged-regime spacing" observation.

No binding threshold for Q5 — exploratory.

## Layer 3 — §8 Q4 asymptotic-form refinement (exploratory)

### Concept

Task 4 found none of the three asymptotic forms `1 − a/log(D)`,
`1 − a/log²(D)`, blend fit the per-decade skip fraction across
`[60, 1000]` (best adj R² = 0.144). Re-running the fits on the
extended `[60, ~3000]` data tests whether the poor fit at small D
was a finite-range artefact or whether the structure persists.

### Method

Same three fits, same per-decade bin width (100), now over the
extended decade table.

### Pre-registered comparison

- **Substantive improvement at extended range:** if any of the three
  fits reaches adj R² ≥ 0.5 on `[60, ~3000]` data (vs ≤ 0.144 on
  `[60, 1000]` data), this is evidence the simple asymptotic form
  holds at larger scales and the small-D non-monotonicity was a
  finite-range artefact. §8 Q4 framing tightens toward "asymptotic
  density → 1 with [chosen form] damping".
- **No improvement:** if all three fits remain at adj R² ≤ 0.3 on
  the extended data, the structural non-monotonicity persists at
  larger scales; no simple asymptotic form captures the data;
  §8 Q4 framing stays as Task 4 left it ("quasi-periodic / structured
  non-monotonic alternation; asymptotic form open").

The 0.5 threshold is the "substantive improvement" anchor; it is
exploratory-binding (recorded for transparency, not gating any
retraction).

## Method (committed for all three layers)

### Computational

- **N_MAX = 1000** for both 5-series and 7-series.
- **Sieve limit = 200_000** (sufficient).
- Both series should reach D ≈ 3300–3500 at N_MAX = 1000.
- **Analysis range:** `[60, D_HI]`, where D_HI = floor((min(D_5(N_MAX),
  D_7(N_MAX)) - 50) / 100) * 100 — the largest 100-multiple at least
  50 below the lower of the two series' max-D. Expected D_HI ≈ 3000
  (or 3100, 3200, depending on the run). If D_HI < 2000, **halt**
  (insufficient extension over Task 4's 1000).

### Binning

100-width decade bins from 60 to D_HI. First bin `[60, 100)` width
40 as in Task 4. Remaining bins width 100.

### Anchors (Pattern 75 — halt on fail)

1. Strict-23 [90, 200] cluster count = 23 under N_MAX = 1000.
2. Cluster with lower edge 172 exists.
3. Skip-monotonicity: cluster (172, X) at N_MAX = 1000 has X ≥ 482.
   (Skip sets are monotone in n, so X_at_1000 ≥ X_at_500 = 482 by
   construction. A reduction would be a script bug.)

### Stop-on-fail

Per Pattern 75 / Pattern N:

- F3 outcome (β-F3) is a major surprise (Task 4 forecloses it) → halt,
  consult CinC.
- Q5 surprises: if more than 5 bounded merged regimes are detected
  in `[200, 3000]`, or if any cluster of width ≥ 500 not anchored
  by series landings is found, halt and consult.
- Q4 surprises: if a fourth-class fit shape is needed (e.g., the
  data is bimodal or has clear periodic structure not captured by
  the three forms), halt.

## Outputs

- `v3_12_data/results/task4b_F3_test_results.md` — F3 binding test
  result + measurement of X.
- `v3_12_data/results/task4b_extended_density_per_decade.csv` —
  per-decade table for [60, D_HI].
- `v3_12_data/results/task4b_merged_regimes_detected.csv` — one row
  per detected bounded merged regime under Q5 detection definition.
- `v3_12_data/results/task4b_density_measurement.png` — extended
  two-panel chart.
- `v3_12_data/results/task4b_summary.md` — combined summary.

## Auto-narrative discipline

Per Task 4's operational note: the script writes fact-only summaries
(tables, fit values, anchor results). Manual "Structural observations"
section authored post-run if surprises emerge. If outcomes are clean
(α-F3, plus either α-Q5 or β-Q5 with a clean characterisation), the
script's default summary may stand; if surprises arise, fact-only +
post-run manual section as in Task 4.

— CinC + Mr Code, 11 May 2026
🐕☕⬡
