# Task 3 Pre-Registration — F5 (refined) under re-classifying alternatives

**Date:** 11 May 2026 (committed before computation per Pattern 19/27)
**Brief origin:** Cliff + CinC, post-Task-2 adjudication, 11 May 2026.
**Parent task chain:** v4.2 comparative tabulation (commit `e60bb5b`);
v4.5 Task 1 outcome (α) (commit `b844639`); v4.5 Task 2 literal-(β) /
refined-(α) (commit `340cb80`); Calibration 3 = F5 non-degeneracy
clause (v4.6 finish-pass content, CinC).

## Question

Task 2 surfaced a degeneracy in the originally-binding F5 thresholds:
maximally-conservative alternatives (e.g., Alt B / mod-30 universal)
trivially fire the outlier-count and entropy thresholds by collapsing
the 7-series lift distribution to a delta. Calibration 3 refines F5
with a non-degeneracy clause: threshold-crossing only counts as
F5-firing if the alternative's lift distribution is non-degenerate
(≥ 2 distinct lift values across the 23-cluster sample; equivalently
mode frequency < 100%; equivalently H > 0 bits).

Task 3 tests the refined F5 against two **re-classifying** alternatives
— alternatives that genuinely vary the required-divisor by cluster
classification (unlike Task 2's Alt A/Alt B which scaled or
universalised the requirement). One alternative is *less* asymmetric
than chosen, one *more*. Both produce non-degenerate distributions by
the classification mechanism — but their threshold-crossing depends on
the cluster geometry.

## Two alternatives

### Alt(C) — "mod-3 always"

(i-a) for 7-series at every cluster type (incl. coincident):
k ≡ 0 (mod 3). Drops the mod-15 escalation at coincident.

5-series unchanged from chosen (k ≡ 0 (mod 3)).
Forbidden = P_7 ∪ {2} for 7-series; P_5 ∪ {2} for 5-series (carve-out
exempts {3}, which isn't in either P_i anyway).

**Less asymmetric than chosen.** At coincident clusters where chosen
requires k=15, Alt(C) only requires mod-3, so the smallest mod-3
candidate that lands is the lift. Coprime-mod-3 candidates ≤ 100 for
7-series: 3, 9, 27, 33, 45, 51, 69, 75, 81, 87, 99 (excluding
multiples of any prime in P_7 = {7, 13, 19, 31, 37, 43, 61, 67, 73,
79, 97}). Expected distribution: spread among {3, 9, 27, ...}
depending on where Π_7(n_7*) sits within its decade at each coincident
cluster.

### Alt(D) — "asymmetric partial-coincident → mod-15"

(i-a) for 7-series:
- coincident: k ≡ 0 (mod 15) — same as chosen.
- **partial-coincident: k ≡ 0 (mod 15)** — NEW (chosen had mod-3 here).
- staggered / single-*: k ≡ 0 (mod 3) — same as chosen.
  (Zero such clusters in the [90, 200] sample; included for completeness.)

5-series unchanged.
Forbidden = P_7 ∪ {2} for 7-series; P_5 ∪ {2} for 5-series.

**More asymmetric than chosen.** Escalates the 4 partial-coincident
clusters (C_3, C_5, C_16, C_21) from mod-3 → mod-15.

Predicted shape: the 19 coincident clusters already lift to 15 under
chosen; under Alt(D) the 4 partial-coincident also reclass into the
mod-15 regime. If Π_7(n_7*) · 15 lands geometrically at each, Alt(D)
distribution is `{15: 23}` — a delta, which the refined F5
non-degeneracy clause excludes. If a partial-coincident cluster needs
k > 15 (e.g., k = 45 because k = 15 overshoots [a, b] or k = 45·m
because of forbidden-set hits), the distribution becomes near-delta
with 1–2 outliers — non-degenerate by the binary clause but still
structurally near-degenerate. **Either outcome is informative**:
pure delta → non-degeneracy clause works cleanly; near-delta →
surfaces a potential second design flaw in the refined F5
(binary clause may be too permissive against near-degenerate cases),
which CinC may want to refine further in a Calibration 3b.

## Refined F5 binding thresholds + non-degeneracy clause

For an alternative to **fire refined F5**, both must hold:

1. **Non-degeneracy:** the alternative's 7-series lift distribution
   across the 23 strict clusters has ≥ 2 distinct lift values
   (equivalently: mode frequency < 100%; equivalently: H > 0 bits).

AND at least one of the following:

2a. Outlier count ≤ 2 (≥ 50% reduction from chosen's 4).
2b. Shannon entropy ≤ 0.35 bits (≥ 0.5-bit reduction from chosen's ~0.85).
2c. Partial-coincident → coincident transition count ≤ 3
    (≥ 25% reduction from chosen's 4). [Note: transitions are
    fixed by Step-3 classification; identical across conventions in
    this design.]

Reference (chosen-convention) values from v4.2: outliers = 4,
H = 0.8405 bits, transitions = 4.

## Pre-registered outcomes

### (α) — Chosen wins, warrant tightens

Neither Alt(C) nor Alt(D) fires refined F5. Either both are
non-degenerate but fail to cross any threshold, or one/both is
degenerate (delta distribution), or both. The chosen convention's
claim to being the right lens on the data is **strengthened** —
non-degenerate competition fails to displace it.

### (β) — A re-classifying alternative fires refined F5

At least one of Alt(C) or Alt(D) is non-degenerate AND crosses at
least one binding threshold (outliers ≤ 2 OR entropy ≤ 0.35 bits OR
transitions ≤ 3). The firing alternative is a substantive challenger
to chosen; CinC's v4.6 §4.0 may be reconsidered with the firing
alternative as a candidate (cf. Task 2's literal-(β) but with the
non-degeneracy filter applied this time — a genuine refutation, not
an artefactual one).

### (γ) — Marginal-zone strengthening

At least one alternative is non-degenerate and produces measurable
but sub-threshold improvement on at least one metric (e.g., outliers
= 3 vs 4 chosen; or H = 0.5 bits vs 0.85 chosen). No binding
threshold crossed. Reported in §6.3 as supplementary cross-validation:
the chosen convention's parsimony is preserved against re-classifying
competition but the alternatives are sub-threshold competitive on
some axes.

## Method

1. For each alternative (Alt(C), Alt(D)) at each of the 23 strict
   clusters in [90, 200], apply Convention A on n_i* (unchanged from
   v4.2) and recompute the minimum-lift k for the 7-series.
2. Aggregate the 7-series lift distribution per alternative. Verify
   the chosen-convention reference (should reproduce v4.2 distribution
   `{15: 19, 3: 2, 9: 2}`).
3. Compute three F5 metrics + non-degeneracy check per alternative.
4. Apply refined-F5 logic: alternative fires iff non-degenerate AND
   ≥ 1 threshold crossed.
5. Identify obtaining outcome.

## Stop-on-fail

Per Pattern 75: halt if either alternative produces a result outside
{α, β, γ} — e.g., a mixed within-alternative pattern not captured by
the three categories, an unexpected non-monotone distribution, or a
classification reclassification under the alternative.

Per Pattern N (calibrate-on-execution-surprise, articulated 11 May
2026): if an alternative fires the refined F5 in a way that's
surface-level legitimate but structurally suspect — e.g., Alt(D)
producing a near-delta with 1–2 outliers that technically passes the
binary non-degeneracy clause but is still near-degenerate in spirit —
record the literal outcome but flag it for CinC; the refined F5 may
need a second-order calibration (e.g., a mode-frequency cap below
100%, or an H > some-positive-floor).

## Outputs

- `v3_12_data/results/task3_re_classifying_alternatives_results.csv`:
  per-cluster lift values under three conventions (chosen, Alt(C),
  Alt(D)); per-convention F5 metric values; per-convention
  non-degeneracy verdict.
- `v3_12_data/results/task3_re_classifying_alternatives_summary.md`:
  three-convention comparative table; outcome paragraph identifying
  (α) / (β) / (γ) under refined F5; flag block if Pattern-N
  near-degeneracy surfaces; suggested §6.3 supplementary text under
  the obtaining outcome.

— CinC + Mr Code, 11 May 2026
🐕☕⬡
