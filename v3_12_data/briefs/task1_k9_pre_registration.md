# Task 1 Pre-Registration — k = 9 outlier verification (Paper 3 v4.5)

**Date:** 11 May 2026 (committed before computation per Pattern 19/27)
**Brief:** `mr_code_brief_paper_3_v4_5.md` (parent, in `~/Downloads/`)
**Parent task chain:** v4.2 comparative tabulation
(`cluster_comparative_tabulation.csv`, commit `e60bb5b` on
`paper-3-v4-2-data`, inherited into `paper-3-v4-5-data`).

## Question

In `v3_12_data/results/cluster_comparative_tabulation.csv`, the 23
strict clusters in D ∈ [90, 200] have 7-series minimum-lift distribution:

- 19 clusters with k = 15
- 2 clusters with k = 3
- 2 clusters with k = 9

A parallel-instance Mr Adversary review of v4.3 flagged the v4.5 §6.3
GAP paragraph as internally inconsistent with the §4.0 convention: the
paragraph attributes k = 9 outliers to "coincident clusters where the
gap geometry is wider than typical", but 9 is not divisible by 15, so a
k = 9 outlier at a coincident cluster would violate the §4.0
requirement that the filled product be divisible by 15 at coincident
clusters.

Determine which of the three pre-registered outcomes below obtains.

## §4.0 convention (v4.5 symmetric statement)

The minimum-lift factor for series i ∈ {5, 7} at cluster C is the
smallest positive integer k such that Π_i(n_i*) · k satisfies:

- **(i-a)** divisible by 3 at every cluster; additionally divisible by
  5 at every coincident cluster (so divisible by 15 there).
- **(i-b)** k's prime factorisation contains only primes outside
  `P_i ∪ {2}` (no re-introduction of factors already in Π_i, no factor
  of 2).
- **(ii)** D(Π_i(n_i*) · k) ∈ G, where n_i* is the largest n such that
  D_i(n) is below the lower edge of series i's specific skip range
  within C (Convention A; addendum 2).

Per-series reduction (from §3 Lemmas 2, 3, 4):

- 5-series anywhere: Π_5 already contains 5, so k need only supply
  mod-3.
- 7-series at staggered / single-series / partial-coincident: only
  mod-3 required, k ≡ 0 (mod 3).
- 7-series at coincident: k must supply both mod-3 and mod-5,
  k ≡ 0 (mod 15).

## Pre-registered outcomes

### (α) — Wording fix only

All k = 9 outlier rows in the CSV have
`classification ∈ {partial-coincident, staggered, single-5, single-7}`,
i.e., **not** fully coincident. At these classifications the §4.0
convention requires only mod-3 for the 7-series, and k = 9 = 3² is the
smallest multiple-of-3 that satisfies (i-b) (only prime factor is 3,
which is not in P_7 ∪ {2}) and (ii) (geometric landing in G).

Implication: data consistent with §4.0 convention. The §6.3 GAP
paragraph wording — "coincident clusters where the geometry of the gap
is wider than typical" — is wrong and needs correction (substitute
"partial-coincident" for "coincident", and remove the "geometry wider
than typical" gloss; the geometric reason is simply that
Π_7(n_7*) · 3 falls below G's lower edge for these clusters).

This is the **expected** outcome based on the convention's structure.

### (β) — Calibration 3 entry required

At least one k = 9 outlier row has `classification = coincident`, AND
no smaller k' < 15 with k' ≡ 0 (mod 15) exists that satisfies
condition (ii) at that cluster (i.e., the cluster genuinely cannot be
filled by k = 15 with a smaller k mod-15 candidate).

Wait — there is no smaller positive multiple of 15 than 15 itself. So
the (β) reading needs to read: at least one k = 9 outlier has
`classification = coincident`, meaning the §4.0 convention is
**violated** at that cluster (the script accepted k = 9 even though
k = 9 doesn't satisfy (i-a) at coincident). Implication: §4.0
convention does not universally describe the 7-series at coincident;
it describes the dominant pattern (~85% of 7-series-at-coincident
cases under this reading) but allows exceptions. A Calibration 3
entry is required in §6.4 stating the convention's universality scope;
§6.3 GAP paragraph is rewritten to reflect the actual classification
of the k = 9 outliers.

### (γ) — Data error / script bug

The k = 9 entries are an artefact of computation. Re-running the
lift-enumeration with k ∈ {1, ..., 1000} (default v4.2 was {1, ...,
100}, then {1, ..., 1000}) at each k = 9 outlier produces a
*different* minimum k that satisfies (i-a), (i-b), (ii). Most likely
candidate sources of (γ):

- Classification error in the v4.2 script (wrong typology assigned).
- Lift-enumeration bug (e.g., found 9 because of an incorrect divisor
  rule).
- Geometric condition (ii) computed with wrong n_i* anchor.

Report the corrected lift values; the v4.2 CSV would need a corrigendum.

## Method

1. Open `v3_12_data/results/cluster_comparative_tabulation.csv`.
   Identify all rows with `lift_7 == 9` in the comparative sample
   (cluster_id starting with `C_`). Record cluster_id, d_range,
   classification, n_5*, n_7*, S5_skips, S7_skips.
2. For each such row, **recompute** the minimum-lift k satisfying
   §4.0 (i-a), (i-b), (ii), with k enumeration over k ∈ {1, ..., 1000}.
   The recomputation is fully redundant with v4.2's logic at
   classification ∈ partial-coincident / staggered / single-* (where
   required_divisor = 3), but uses required_divisor = 15 at
   classification == coincident as a contradiction-check.
3. Per row, determine which outcome applies:
   - Recomputed k == 9 AND classification != coincident → (α) for this row.
   - Recomputed k == 9 AND classification == coincident → (β) for this row.
   - Recomputed k != 9 → (γ) for this row.
4. Aggregate across all k = 9 outliers. If all rows produce the same
   outcome → that outcome obtains. If mixed → **HALT** (Pattern 75):
   not in the pre-registered set, consult CinC.

## Outputs

- `v3_12_data/results/task1_k9_verification_results.csv`:
  one row per k = 9 outlier with
  `cluster_id, d_range, classification, n_5_star, n_7_star,
   recomputed_lift_7, outcome_for_this_row`.
- `v3_12_data/results/task1_k9_verification_summary.md`:
  aggregate outcome (α / β / γ); one paragraph of findings; suggested
  wording correction or Calibration 3 entry as appropriate.

## Stop-on-fail

Per Pattern 75: if the verification produces a fourth outcome category
(e.g., mixed across rows, or an unexpected structural surprise), halt
and consult CinC. Do not improvise.

— CinC + Mr Code, 11 May 2026
🐕☕⬡
