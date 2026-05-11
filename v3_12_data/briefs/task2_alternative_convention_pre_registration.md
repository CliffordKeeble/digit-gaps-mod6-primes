# Task 2 Pre-Registration — F5 alternative-convention probe (Paper 3 v4.5)

**Date:** 11 May 2026 (committed before computation per Pattern 19/27)
**Brief:** `mr_code_brief_paper_3_v4_5.md` (parent, in `~/Downloads/`)
**Path-strengthener** — optional but recommended.

## Question

Run the comparative tabulation across D ∈ [90, 200] under two
alternative conventions (replacing the §4.0 chosen convention with
each in turn) and report the three F5 metrics for each. Determine
which of the three pre-registered outcomes obtains.

## Chosen convention (reference; v4.5 §4.0)

For series i ∈ {5, 7} at cluster C with combined d-range G:

- (i-a) divisible by 3 at every cluster; additionally divisible by 5
  at coincident clusters (filled product div by 15 at coincident).
- (i-b) k coprime to `P_i ∪ {2}` except for primes that (i-a)
  specifically requires k to contain (the carve-out — see general
  principle below).
- (ii) Convention A on n_i*.

## Alternative conventions

### Alternative A — mod-2 inclusion

(i-a) replaced by:

- filled product divisible by 2 at every cluster, AND
- additionally divisible by 10 at every coincident cluster.

Per-series reduction (Π_i is built from primes ≡ ±2 (mod 6), all of
which are odd; Π_5 contains 5 as one of its factors, Π_7 does not):

- 5-series anywhere: Π_5 already contains 5, so the mod-10 requirement
  at coincident reduces to mod-2 (k ≡ 0 (mod 2)). At non-coincident
  clusters, k need only supply mod-2 (k ≡ 0 (mod 2)). So k_min(5) must
  be a multiple of 2 in both cases.
- 7-series at staggered / single / partial-coincident: only mod-2
  required, k ≡ 0 (mod 2).
- 7-series at coincident: k must supply both mod-2 and mod-5,
  k ≡ 0 (mod 10).

### Alternative B — mod-30 inclusion (most-conservative)

(i-a) replaced by:

- filled product divisible by 30 (= 2 × 3 × 5) at every cluster.

Per-series reduction:

- 5-series anywhere: Π_5 supplies 5, so k must supply mod-2 and
  mod-3, k ≡ 0 (mod 6).
- 7-series anywhere: k must supply mod-2, mod-3, mod-5,
  k ≡ 0 (mod 30).

## Principle for (i-b) carve-out under any alternative

Per CinC (11 May 2026): clause (i-b) under an alternative convention
reads as

> "k introduces no prime to the lifted product that is already in
> Π_i, except for primes that the alternative convention's (i-a)
> specifically requires k to contain."

The chosen convention already exhibits this pattern — its (i-b)
implicitly carves out {3} (and at 7-series-coincident, {3, 5}) from
the no-reintroduction rule because (i-a) requires those factors. For
the alternatives, the carve-out relocates to whichever primes the new
(i-a) requires:

- **Alternative A:** carve-out = {2} universally (and {2, 5} at
  coincident). All other (i-b) constraints stay: no re-introduction
  of any prime already in Π_i.
- **Alternative B:** carve-out = {2, 3, 5} universally for both
  series at every cluster.

Without the carve-out, both alternatives have no satisfying k at the
5-series (since 5 ∈ P_5). The "structurally complete element"
interpretation — Π_i provides the coprime-to-mod-N component, k
supplies the missing factor(s) — generalises across conventions.

## F5 binding thresholds (from v4.5 §6.3)

Reference values are taken from the v4.2 chosen-convention
distribution across 23 strict clusters in [90, 200]:

| Metric | Chosen-convention value | (β) fires if alternative reaches |
|--------|-------------------------|----------------------------------|
| (a) Lift-outlier count | 4 (clusters where lift_7 ≠ mode = 15) | ≤ 2 (≥ 50% reduction) |
| (b) Lift-distribution Shannon entropy | H ≈ 0.85 bits (7-series lift) | ≤ 0.35 bits (≥ 0.5 bits reduction) |
| (c) Classification bin-edge sharpness | 4 partial-coincident → coincident transitions | ≤ 3 (≥ 25% reduction) |

**Reference H calculation** (sanity check): p(15) = 19/23, p(3) =
2/23, p(9) = 2/23.
H = −(19/23)·log₂(19/23) − 2·(2/23)·log₂(2/23) ≈ 0.84 bits.
Matches the v4.5 §6.3 "H ≈ 0.85 bits" anchor to within rounding.

## Pre-registered outcomes

### (α) — Chosen convention wins

Neither alternative crosses any of the three binding thresholds:

- Both alternatives produce outlier count ≥ 4.
- Both produce entropy ≥ 0.85 bits.
- Both produce transition count ≥ 4.

F5 does not fire under either alternative. The warrant for the chosen
mod-3 / mod-15 convention tightens substantively.

### (β) — An alternative fires F5

At least one alternative crosses at least one binding threshold:

- outlier count ≤ 2, OR
- entropy ≤ 0.35 bits, OR
- transition count ≤ 3.

The chosen convention's claim to being the right lens on the data is
**refuted**. Retraction 4 (specifically of the convention choice) is
indicated; §4.0 to be rewritten with the dominant alternative as the
new chosen convention; v5.0 is the natural version increment (not a
finish pass).

### (γ) — Marginal-outcome zone

An alternative produces measurable but sub-threshold improvement on
at least one metric without crossing any binding threshold. F5 does
not fire; the comparative analysis is documented in §6.3 as a
**strengthening** of the convention warrant rather than a refutation.
Becomes a supplementary §6.3 / §8 Q1 paragraph reporting that
alternatives were tested and the chosen convention still dominates by
sub-threshold margin.

## Method

1. For each alternative convention (A and B), at each of the 23 strict
   clusters in [90, 200], recompute the minimum-lift k_min(i) for
   each series i ∈ {5, 7}:
   - Apply the alternative's (i-a) divisibility rule.
   - Apply the (i-b) carve-out principle.
   - Apply Convention A on n_i* (unchanged across alternatives — n_i*
     is anchored on the series-specific skip range, not the
     convention).
   - Enumerate k ∈ {required_divisor, 2·required_divisor, ...,
     up to 1000}.
2. Aggregate the 7-series lift distribution under each convention.
3. Compute three F5 metrics per convention:
   - **Outlier count:** number of clusters where lift_7 ≠ mode
     of the 7-series lift distribution under that convention.
   - **Entropy:** Shannon entropy (base 2, in bits) of the 7-series
     lift distribution.
   - **Transition count:** number of consecutive (C_n → C_{n+1}) pairs
     where the classification transitions from
     `{staggered or partial-coincident}` to `coincident`. The
     classification scheme is unchanged across conventions; the
     transition count is therefore identical across conventions.
     (Reporting it under each convention is a sanity check.)
4. Compare each alternative's metrics to the binding thresholds.
5. Identify the obtaining outcome (α / β / γ).

## Outputs

- `v3_12_data/results/task2_alternative_convention_results.csv`:
  per-cluster lift values under three conventions (chosen + A + B),
  classification under each convention (classification is fixed by
  Step 3 of v4.2; conventions don't reclassify).
- `v3_12_data/results/task2_alternative_convention_summary.md`:
  three-convention comparative table; outcome paragraph identifying
  which of (α) / (β) / (γ) obtains; if (γ), suggested §6.3
  supplementary paragraph text.

## Stop-on-fail

Per Pattern 75: if either alternative produces structural surprises
not in (α) / (β) / (γ) — e.g., a third pattern in the lift
distribution that doesn't correspond to "dominated by [the mode]" or
"dominated by some other multiple"; or a classification reclassification
under one convention; or an unexpected non-monotone behaviour — halt
and consult CinC.

— CinC + Mr Code, 11 May 2026
🐕☕⬡
