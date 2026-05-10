# Addendum to Mr Code Brief — Paper 3 v4.2

**Date:** 10 May 2026 (added during execution; before the tabulation run)
**Subject:** Cluster-count anchor calibration (Anchor 3, Anchor 4)
**Trigger:** Pattern-75 HALT during initial run, 10 May 2026.

## Discrepancy

Mr Code halted at Anchor 3 of the parent brief: the reference anchor stated
**24** clusters in D ∈ [90, 200] (per the v3.14 enumeration), but the strict
*"entirely contained"* reading specified by the brief produced **23**.
Diagnostic showed the 24th cluster is `(172, 482)` — a 311-digit-wide
combined-skip cluster whose lower endpoint (172) sits inside [90, 200] but
whose upper endpoint (482) extends far past it. The v3.14 reference
implementation (`v3_12_data/isolated_threshold.py`) used a permissive
*"either endpoint in [90, 200]"* matching and admitted `(172, 482)` as the
24th cluster.

## Resolution (CinC, 10 May 2026)

Adopt **strict reading: 23 clusters in [90, 200]**.

`(172, 482)` is the leading edge of the **asymptotic merged regime** within
N_MAX = 250 — at sufficiently large n the per-series skip densities drive
the combined skip set into a single contiguous run. It is not a
boundary-like cluster: it is 311 digit-lengths wide, far outside the
2–4-digit-wide range of the v4.1 §6.3 clusters that v4.2 is comparing
against B1 and B2. Its lift question is degenerate (any k = 3 lands
somewhere in a 311-digit range trivially), so the geometric meaning of
"minimum lift" does not carry across the regime boundary.

The substantive v3.14 conclusion (*"median = max = 2 inter-cluster
distance, 0 at distance ≥ 3"*) holds under both readings: the gap from
`(169, 170)` to `(172, 482)` is `172 − 170 = 2`, satisfying either
boundary. The 24-count was a counting choice, not a load-bearing finding.

## Updated anchors

- **Anchor 3:** cluster count in [90, 200] = **23** (was 24).
- **Anchor 4:** per-cluster nearest-cluster distance over [90, 200],
  median = max = **2**, **0/23 at distance ≥ 3, 0/23 at distance ≥ 5**
  (was 0/24).

## Output specification update

`cluster_comparative_tabulation.csv` records one row **outside** the
23-cluster comparative sample, capturing the `(172, 482)` discovery:

- `cluster_id = "merged_regime_edge"`
- `d_lower = 172, d_upper = 482`
- `classification = "asymptotic-merged"` (new label, distinct from the five
  comparative-sample labels)
- `lift_5 = "n/a (degenerate; cluster width 311)"`
- `lift_7 = "n/a (degenerate; cluster width 311)"`
- `notes = "leading edge of asymptotic merged regime within N_MAX = 250;
  digit skips contiguous, individual cluster-and-gap structure breaks
  down"`

The 23 comparative-sample rows (`C_3` through `C_25`) plus the two
boundaries (`B1`, `B2`) remain as in the parent brief; the
`merged_regime_edge` row is appended.

## Findings.md update

The v4.2 findings section adds a *"v3.14 → v4.2 enumeration calibration"*
note documenting the count change as a methodological calibration, not a
retraction. The `(172, 482)` cluster is recorded as a substantive
separate discovery — possibly integrated into v4.2 §6.4 by CinC during
paper drafting.

## N_MAX

No N_MAX extension is required for v4.2: per-series skip sets are
monotone in n, so `(172, 482)` cannot break up at higher N_MAX (it can
only extend further as more series-jumps merge with it). Confirming the
upper bound of the merged regime at higher N_MAX is a v4.3-able
follow-up, not a v4.2 gating concern.

## Scope of this addendum

This addendum modifies **only** the Anchor 3 / Anchor 4 expectations and
the output specification (one extra CSV row). It does not modify:
- the pre-registered prediction in the parent brief;
- the falsifier-test rows (α, β, intermediate);
- the lift-predicate rule (cluster-type-dependent mod-3 vs mod-15);
- the comparative sample (still the 23 strict clusters in [90, 200]).

The pre-registration commit of the parent brief (`7fa5e38`) on
`paper-3-v4-2-data` and this addendum together constitute the binding
specification for the v4.2 task.

— CinC + Mr Code, 10 May 2026

🐕☕⬡
