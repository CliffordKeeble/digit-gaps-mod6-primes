# Addendum 2 to Mr Code Brief — Paper 3 v4.2

**Date:** 10 May 2026 (after Anchor-5 HALT; before re-run)
**Subject:** n_i* convention (Step 4) + Step 3 typology refinement
**Trigger:** Pattern-75 HALT during Anchor 5 verification, 10 May 2026.

## Discrepancy

The script halted at Anchor 5 with two issues:

1. **B1 classification** strict-Step-3 application produced *partial-coincident*,
   while the brief's text-table asserted *staggered*. The actual data:
   `S_5(B1) = {60, 61, 63}` and `S_7(B1) = {60, 62, 63}` — both d=60 and d=63
   are dual-skipped.

2. **B1 7-series lift** under brief Step 4 (n_i* = "largest n with D_i(n)
   below the lower edge of C") gave **k = 9**, not the cited Proposition-1
   anchor of **k = 3**. Strict reading puts n_7* = 29 (D_7(29) = 59 < 60),
   and Π_7(29) · 3 has 59 digits (still below [60, 63]).

## Resolution (CinC, 10 May 2026)

### Issue 2 — n_i* convention: adopt Convention A.

**New definition:**

> Let `n_i* = max{n : D_i(n) < min(S_i(C))}` — the largest n such that
> `D_i(n)` sits just before series i's first skip event within C.
> Equivalently: the largest n at which Π_i is just below the lower edge
> of *its own* skip range within the cluster, rather than the lower edge
> of the cluster's combined d-range.

This matches Propositions 1 and 2 at every boundary anchor:

| Boundary | Series | min(S_i(C)) | n_i* | D_i(n_i*) | Lift |
|----------|--------|-------------|------|-----------|------|
| B1       | 5      | 60          | 30   | 59        | 3    |
| B1       | 7      | 62          | 30   | 61        | 3    |
| B2       | 5      | 80          | 38   | 79        | 3    |
| B2       | 7      | 80          | 37   | 79        | 15   |

The brief's "lower edge of cluster's combined d-range" reading happens to
coincide with Convention A at *coincident* clusters (where S_i(C) = cluster
d-range for both i), which is why B2 reproduces under either reading.
At *staggered* and *partial-coincident* clusters, the conventions diverge,
and the published anchors use Convention A. The brief language is the slip;
the underlying mathematics is consistent across Propositions 1, 2 and the
v4.2 generalisation.

**Step 4 amendment:** the first paragraph after "For each (cluster C,
series i) pair where C is i-series-active:" now reads —

> Let n_i* be the largest n such that D_i(n) is below `min(S_i(C))`,
> the lower edge of series i's skip range within the cluster
> (equivalently: the largest n such that D_i(n) sits just before
> series i's first skip event within C). Define
> `prod_i = Π_i(n_i*)`.

Conditions (a), (b), (c) on k are unchanged from the parent brief.

### Issue 1 — B1 classification: accept partial-coincident.

Mr Code's strict-Step-3 enumeration is correct. v4.1's §6 prose described
the *staggered cores* of B1 — the 5-series jump skipping {60, 61} and the
7-series jump skipping {62, 63} — but missed the dual-skipped *edges* at
d=60 (caused by D_7(29)→D_7(30) skipping {60}) and d=63 (caused by
D_5(31)→D_5(32) skipping {63}). The strict trinary
{staggered / partial-coincident / coincident} of brief Step 3 is the
more precise typology; v4.1's binary {staggered / coincident} maps onto
it with B1 falling into partial-coincident, not staggered.

**This is a refinement, not a retraction.** v4.1's "staggered → coincident
transition" claim (B1 → B2) becomes "partial-coincident → coincident
transition" in v4.2, with the same direction (more dual-skipping at the
later boundary) and richer structure. The factor-escalation pattern
3 → 15 is unaffected (lift_7(B1) = 3 under either classification, given
Convention A on n_i*).

**Step 3 amendment:** the typology rule is precise as written
(*coincident* iff `S_5(C) = S_7(C)`; *partial-coincident* iff overlap
but not equal; *staggered* iff disjoint and both active). The amendment
is a clarifying note rather than a definitional change:

> Note: under the strict trinary, *staggered* requires
> `S_5(C) ∩ S_7(C) = ∅` AND both series active. Boundary 1 falls into
> *partial-coincident* under this definition; v4.1's prose-level
> "staggered" was a binary {staggered / coincident} approximation
> that the v4.2 trinary refines.

### Updated Anchor 5

| Boundary | Classification     | lift_5 | lift_7 |
|----------|--------------------|--------|--------|
| B1       | partial-coincident | 3      | 3      |
| B2       | coincident         | 3      | 15     |

### Falsifier-test interpretation under the refined typology

The pre-registered prediction in the parent brief used "coincident-dual"
without anticipating partial-coincident as a distinct category. CinC
ruling:

- **(α)/(β) coincident counts:** **strict equality only** — `S_5(C) = S_7(C)`.
  Partial-coincident clusters are reported separately for completeness
  but do not count toward the coincident-dual threshold.
- **Lift counts ("≤ 4 with 7-series lift > 3"):** unaffected; remain
  binding as in the parent brief.
- **Recurrence test:** read "no recurrence of the staggered → coincident
  transition between consecutive clusters" under v4.2 typology as
  "no recurrence of the {staggered or partial-coincident} → coincident
  transition between consecutive clusters" — since B1 → B2 under the
  refined typology is partial-coincident → coincident.

The (α), (β), and intermediate rows are otherwise binding without
modification.

### Findings.md update (now two calibrations)

The v4.2 findings section will document:

1. **Calibration 1 (count):** v3.14's loose 24-count → v4.2's strict 23
   in [90, 200]; (172, 482) recorded as merged_regime_edge.
2. **Calibration 2 (classification):** v4.1 prose-level "staggered" for
   B1 → v4.2 strict-trinary "partial-coincident"; the structural
   transition narrative refined to "partial-coincident → coincident"
   for B1 → B2.

Both stay in the calibration template (not retraction).

## Scope of this addendum

This addendum modifies:
- Step 4's n_i* definition (clarification to Convention A).
- Step 3's typology note (clarification on the trinary).
- Anchor 5's B1 entry (staggered → partial-coincident).
- Falsifier-test interpretation (strict coincident; recurrence on
  {staggered or partial-coincident} → coincident).

It does not modify:
- The pre-registered prediction targets (≤ 3 coincident, ≤ 4 lift7>3,
  ≤ 1 B2-pattern repro, no recurrence).
- The (α), (β), intermediate row definitions otherwise.
- The lift-predicate cluster-type-dependent rule (mod-3 default,
  mod-15 for coincident-7-series).
- The 23 strict comparative-sample clusters or the
  merged_regime_edge row.

Pre-registration commits binding for v4.2:
- `7fa5e38` — parent brief.
- `2abe020` — addendum 1 (cluster-count calibration).
- *this commit* — addendum 2 (n_i* convention + Step 3 typology).

— CinC + Mr Code, 10 May 2026

🐕☕⬡
