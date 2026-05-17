# Mr Code Brief — Paper 201 Task 7: Dynamic-Null Variant for the 7-Series-Lands-First Magnitude Excess

**Author:** Dr. Clifford Keeble — ORCID 0009-0003-6828-2155
**Paper:** Paper 201 v1.1 (post-Mr-Adversary cycle-4 review, ★★★★ verdict; path 1 to fifth star)
**Task:** Task 7 — dynamic-null variant of Task 6, testing whether the aggregate +0.93-prime-index excess survives a null that preserves the arrival time-profile of P_5 and P_7 primes (not only their static count)
**Branch:** `paper-201-v1-1-task7`
**Pre-registration commit:** this file, committed to `v3_12_data/briefs/` before any computation runs
**Status:** PRE-COMPUTATION — all scientific parameters locked in this brief

---

## 1. Context

Paper 201 v1.1 §5.4 reports an aggregate +0.93-prime-index excess at the four fully-detected bounded merged regime upper edges (regimes 2, 3, 4, 5), surviving the static-count label-permutation null of Task 6 at p_magnitude = 0/10,000 and Fisher's combined p ≈ 2.22 × 10⁻⁵.

Paper 201 v1.1 §9 Q4 candidate (c) identifies the substantively decisive follow-up test: a *dynamic* version of the label-permutation null that preserves not only the static count of P_5 and P_7 primes within each window (which Task 6's null already preserves) but also the *arrival time-profile* — how P_5 and P_7 primes interleave across the window in order of prime size. Task 6's null shuffles labels freely across the full ±200-digit-length window subject only to total-count preservation; a dynamic null instead preserves the local arrival structure at finer resolution.

The categorical role of candidate (c) (§9 Q4 in v1.1):
- (c) is a *baseline-extension*, not a *generating mechanism*. If the dynamic null absorbs the +0.93-excess, the v1.1 §5.4 structural-property framing must be narrowed to "an artefact of static-count baseline choice." If the excess survives, candidate (c) is ruled out as the sole explanation and substantive mechanisms (a), (b), (d) remain as candidate generating structures.

**Mr Adversary cycle-4 review of Paper 201 v1.1 (May 2026), ★★★★ verdict.** Mr A's cycle-4 closing note:

> Running the dynamic-null variant (Q4 follow-up (ii)) before Zenodo upload, so that the §5.4 structural framing is tested against its substantively decisive alternative before publication rather than after... I would take (1) if you have the compute budget for it.

Task 7's purpose is to execute that substantively decisive test before v1.1's Zenodo upload — either confirming the structural framing against the dynamic null, or narrowing it before the public record.

---

## 2. Pre-registered question

Does the aggregate +0.93-prime-index excess at the four fully-detected regime upper edges survive a label-permutation null that preserves the arrival time-profile of P_5 and P_7 primes within each window, in addition to preserving the static count that Task 6 already preserved?

---

## 3. Pre-registered null model (Null B' — dynamic-arrival-profile-preserving)

The dynamic-null variant strengthens Task 6's static-count label-permutation null by adding sub-window-stratified count preservation.

**Null hypothesis (H'₀).** Within each sub-window of the ±200-digit-length window around regime r's upper edge u_r, the residue-class label (P_5 vs P_7) of each prime is exchangeable subject to *sub-window-local* count preservation. That is, the observed labelling is one of many equally likely labellings preserving the counts of P_5 and P_7 primes within each sub-window separately, rather than only the totals across the full window.

**Sub-window definition (pre-committed).** The ±200-digit-length window W_r around each regime upper edge u_r is partitioned into **K = 8 contiguous sub-windows of ±50 digit-lengths each**: four sub-windows below u_r at d ∈ [u_r − 200, u_r − 150), [u_r − 150, u_r − 100), [u_r − 100, u_r − 50), [u_r − 50, u_r); four sub-windows above u_r at d ∈ [u_r, u_r + 50), [u_r + 50, u_r + 100), [u_r + 100, u_r + 150), [u_r + 150, u_r + 200]. Sub-window assignment for each prime p is determined by the digit-length D_i(n) the prime occupies in its series's cumulative-product trajectory (the same digit-length variable Task 6 uses for window membership).

The sub-window width of ±50 digit-lengths is the substantive design choice of Task 7 and is locked here before computation. The rationale: fine enough to preserve meaningful within-window time-profile structure (each sub-window contains roughly 10–12 primes per series at regime 5 sizes, so eight strata across the window resolve the arrival profile at ≈ 1/8th-window resolution); coarse enough to leave non-trivial randomisation room within each sub-window. ±50 is the pre-committed value; sensitivity to alternative sub-window widths is out of scope for Task 7 (see §9 below).

**Permutation procedure.**

1. Identify the same ±200-digit-length windows W_r around each regime upper edge that Task 6 used. Anchor verification (§5 below) confirms these are unchanged.
2. Within each W_r, partition the pooled P_5 and P_7 primes by sub-window assignment (eight sub-windows, ±50 each).
3. For each sub-window j ∈ {1, ..., 8}: record m_5,j and m_7,j, the actual counts of P_5 and P_7 primes in sub-window j.
4. For each Monte Carlo trial: independently within each sub-window j, uniformly at random select m_7,j of the m_5,j + m_7,j pooled primes to relabel as "7-series," with the remaining m_5,j relabelled as "5-series." This preserves both the static total counts (M_5, M_7) and the sub-window-stratified counts (m_5,j, m_7,j for each j).
5. Concatenate the relabelled sub-windows into a single relabelled window; form simulated cumulative products as in Task 6 (prefix deterministic cumulative products of P_5 and P_7 up to the prime immediately before W_r starts; append products over the relabelled 5-set and 7-set in size order).
6. Compute n_5^sim and n_7^sim at digit-length u_r + 1.
7. Lead^sim_r = n_5^sim − n_7^sim.

**Null B' is strictly more restrictive than Null B (Task 6).** Every Task 7 relabelling is also a valid Task 6 relabelling (sub-window-local count preservation implies total count preservation), but not every Task 6 relabelling is a valid Task 7 relabelling. The simulated lead distribution under Null B' is therefore *concentrated* around the dynamic-profile expectation, not just the static-count expectation. The substantive content of Task 7's result is whether the observed leads ({3, 4, 5, 6}) are still distinguished from this narrower null.

**Number of trials.** N_TRIALS = 10,000 per regime, matching Task 6 for direct comparability of p-values across the two nulls.

**Random seed.** Master seed = 1042 (distinct from Task 6's master seed 42 to ensure cross-task seed-namespace independence). Per-regime seeds = 1042 + r for r ∈ {2, 3, 4, 5}: regime 2 uses 1044, regime 3 uses 1045, regime 4 uses 1046, regime 5 uses 1047.

**Numerical precision.** mpmath at 200-decimal-place precision throughout, matching Task 6's implementation precision (Task 6 used 200-dps for all regimes per its implementation simplification, documented in the Task 6 summary).

---

## 4. Pre-registered joint test statistics

Three statistics are reported (matching Task 6 structure):

**(J-i) Joint sign p-value.** P(Lead^sim_r > 0 for all r ∈ {2, 3, 4, 5}). Under Task 6's null this saturated at 1.0000 due to static-count Chebyshev imbalance; under Task 7's dynamic null the result is empirically open.

**(J-ii) Joint magnitude p-value (HEADLINE).** P(Lead^sim_r ≥ {3, 4, 5, 6} respectively, jointly across all four regimes). This is the pre-registered headline for Task 7, in direct comparability with Task 6's headline.

**(J-iii) Per-regime tail probabilities and Fisher combined.** Per-regime p_r = (1/N_TRIALS) × #{trials where Lead^sim_r ≥ observed lead at r}; Fisher combined via mpmath.gammainc as in Task 6 (Laplace-rule regularisation if any p_r saturates at zero).

All three statistics are reported regardless of outcome, alongside Task 6's already-published values for direct comparison.

---

## 5. Pre-registered pass/fail thresholds

Committed BEFORE computation runs. The headline statistic is **p_magnitude (J-ii)**, identical to Task 6 for direct comparison.

- **(α) Null absorbs the excess — §5.4 framing retreats.** p_magnitude ≥ 0.10. Paper 201 v1.1 §5.4 is narrowed: the aggregate +0.93-prime-index excess is consistent with the dynamic-arrival-profile null, so the structural framing of v1.1 §5.4 must be reframed as "an artefact of static-count baseline choice." §9 Q4 candidate (c) becomes the operative reading; the "structural" reading retires. Abstract finding (iii) softens to flag that the magnitude excess does not survive the time-profile-preserving null.
- **(γ) Intermediate — no framing change.** 0.05 ≤ p_magnitude < 0.10. Paper 201 v1.1 §5.4 retains v1.1 framing; the result is reported transparently as "Null B' gives p_magnitude = [value], not sub-5% but suggestive of partial absorption by the dynamic null." The v1.1 §5.4 structural reading is bounded explicitly to "survives the static-count null but only suggestively against the dynamic null."
- **(β) Excess survives the substantively decisive null — §5.4 stands and strengthens.** p_magnitude < 0.05. Paper 201 v1.1 §5.4 stands as drafted: the aggregate +0.93 excess survives both the static-count and the dynamic-arrival-profile-preserving label-permutation nulls. Candidate (c) in §9 Q4 is ruled out as the sole explanation; substantive mechanisms (a), (b), (d) remain as candidate generating structures with the structural claim hardening. Mr A cycle-4 path 1 satisfied; the fifth-star verdict expected.

In all three outcomes, both Task 6 and Task 7 p-values are reported alongside each other for full transparency.

**The discipline:** thresholds are committed here, not after the data is seen. Whichever way p_magnitude lands, the framing-update rule above is applied without rhetorical manoeuvring.

---

## 6. Anchor verification gates (HALT-ON-MISMATCH)

Before any null result is reported, the script must reproduce the following deterministic anchors:

**Anchor A — Observed leads.** Compute deterministic cumulative products over actual P_5 and P_7 and verify the observed (n_7, n_5) pairs at u_r + 1 for r ∈ {2, 3, 4, 5}, matching Task 6:

| Regime r | u_r + 1 | Expected n_7 | Expected n_5 | Expected lead |
|---|---|---|---|---|
| 2 | 1718 | 503 | 506 | 3 |
| 3 | 4232 | 1112 | 1116 | 4 |
| 4 | 8319 | 2029 | 2034 | 5 |
| 5 | 15046 | 3452 | 3458 | 6 |

Any mismatch halts the pipeline.

**Anchor B — Regime upper edges.** Verify the regime upper edges {1717, 4231, 8318, 15045} from Paper 201 §5.2 / Task 5. Halt on mismatch.

**Anchor C — Task 6 cross-reference.** Read `v3_12_data/results/task6_seven_series_first_null_summary.md` and assert agreement with Task 6's published values: per-regime tail probabilities (p_2 = 0.0304, p_3 = 0.1973, p_4 = 0.0336, p_5 = 0.0000) and joint statistics (p_magnitude = 0/10,000, Fisher's combined p ≈ 2.22 × 10⁻⁵, p_sign = 1.0000). Halt on mismatch. Anchor C is the cross-task discipline check.

**Anchor D — Sub-window count balance (Task 7-specific).** For each regime r and each sub-window j ∈ {1, ..., 8}, record m_5,j and m_7,j and assert m_5,j + m_7,j > 0 (no empty sub-windows). At regime 5 sizes with primes around log₁₀(p) ≈ 4.7, each ±50-digit-length sub-window should contain ~10–12 primes per series; lighter at regime 2. Halt on any empty sub-window — that would indicate the sub-window width is too narrow for the regime size and the pre-committed K = 8 partition is inappropriate.

The anchor-verification discipline matches Tasks 1–6. The pipeline halts rather than overwriting on mismatch.

---

## 7. Implementation specification

**Language and libraries.** Python 3.11+, mpmath, sympy (or hard-coded prime sieve), numpy, pandas, matplotlib. Matches Task 6 dependency set; no scipy (Fisher's via mpmath.gammainc, same as Task 6).

**Repository location.** `v3_12_data/task7_dynamic_null_variant.py` in the digit-gaps-mod6-primes repository.

**Code structure.** The Task 7 script is permitted to reuse Task 6's prime-enumeration, cumulative-product, and window-identification routines via import or copy-paste; only the relabelling procedure (sub-window stratification) is novel. The cross-reference to Task 6's CSV in Anchor C is the verification that the shared infrastructure produces the same values.

**Budget guidance.** Task 6 completed in 25.8s; Task 7's additional per-trial cost is one sub-window-stratified permutation rather than a single full-window permutation. Total Task 7 runtime estimated at 30–45 seconds. Well under 30-minute budget.

**Branch and commits.** Pre-registration commit (this brief): on branch `paper-201-v1-1-task7`, BEFORE any implementation work. Implementation commits follow. Results commits happen only after anchor verification gates pass.

---

## 8. Output deliverables

The following files are produced and committed once the pipeline runs to completion:

1. **`v3_12_data/results/task7_dynamic_null_variant.csv`** — long-format trial data:
   `regime, trial_id, n_5_sim, n_7_sim, lead_sim, lead_observed`
   40,000 rows (4 regimes × 10,000 trials).

2. **`v3_12_data/results/task7_dynamic_null_variant_summary.md`** — aggregate summary including:
   - Per-regime histograms of Lead^sim_r under Task 7's null, with summary statistics (mean, median, IQR, range).
   - p_sign (J-i), p_magnitude (J-ii) — the headline, p-magnitude.
   - Per-regime tail p_r values and Fisher's combined.
   - Pre-registered threshold this result triggers (α / γ / β).
   - **Side-by-side comparison with Task 6:** for each regime r, Task 6 vs Task 7 null means and p-values; identification of which simulated lead distribution is narrower (expected: Task 7 narrower since strictly more restrictive null) and by how much.
   - Diagnostic: comparison of static-count counts (M_5, M_7) vs sub-window-stratified counts (m_5,j, m_7,j) per regime — exhibits the additional structure Task 7 preserves over Task 6.
   - One paragraph stating the framing-update applied to Paper 201 v1.1 §5.4, per §5 above.

3. **`v3_12_data/results/task7_lead_distribution.png`** — four-panel figure, one panel per regime, showing the histogram of Lead^sim_r under Task 7's dynamic null alongside Task 6's static-count null distribution for direct comparison. Observed lead marked by a vertical line on each panel. Caption includes p_r per panel under both nulls.

4. **`v3_12_data/briefs/mr_code_brief_paper_201_task7.md`** — this brief, committed BEFORE the implementation.

---

## 9. Honest-reporting commitment

The pre-registration discipline of the 2I Programme commits to:

- Reporting the result faithfully regardless of which threshold (α / γ / β) is triggered.
- No post-hoc adjustment of the sub-window width (±50 is pre-committed), the precision budget (200-dps), the threshold values (β < 0.05, γ ∈ [0.05, 0.10), α ≥ 0.10), or the test statistic (p_magnitude as headline).
- No selective reporting of regime-level results: all four per-regime histograms and tail p-values are reported.
- If anchor verification fails, the failure is reported and investigated, not silently masked.
- The framing update in Paper 201 v1.1 §5.4 follows the rule in §5 above mechanically, not strategically.
- The (α) outcome — null absorbs the excess — would be a substantial retreat from the v1.1 §5.4 framing. It would also be exactly the result the dynamic null is run to expose; that is what the test is for. The (α) outcome is published if it occurs.

Track record: F1 (cascade conjecture, refined out of v3.4); F3 (structural-distinguishing-features, refined out at v4.2); F4 (doubling-at-2.3× anchor, refined out at v5.0); Task 6's headline statistic outcome (β; reported faithfully with the +0.93 reading anchored at its pre-registered scale and per-regime heterogeneity disclosed).

Task 7 falls under the same discipline.

---

## 10. What is NOT in scope for Task 7

Out of scope (do not perform; do not report on):

- **Sub-window width sensitivity sweep.** Pre-committed value ±50 is the substantive design choice for Task 7. Alternative widths (±25, ±100) are not run as part of Task 7's pre-registered confirmatory analysis. An exploratory sensitivity sweep on Task 7's sub-window width is a natural post-publication follow-up to record under §9 Q4 if outcome is (β).
- **Window-width sensitivity** (Mr A cycle-4 NULL — window-width concern). The main ±200 window is pre-committed and unchanged from Task 6; alternative main-window widths are still under §9 Q4 follow-up (iv) post-publication.
- **Alternative arrival-profile-preservation operationalisations.** Task 7 commits to sub-window-stratified count preservation as the dynamic-null mechanism. Alternative operationalisations (block-bootstrapping, copula-based preservation, conditional-density estimation) are out of scope; should the result be (γ) or (α), they may be explored under §9 Q4 follow-up at a later cycle.
- **Q4(d) cross-test against Paper 199.** That is a separate Mr Code task (Task 8, possibly) — out of scope for Task 7. Mr A cycle-4 noted Q4(d) as a "nice to have."
- **Modifications to F5 specification, the §2 condition (ii) amendment, or other v1.1 content.** Task 7 is a null-distribution computation only; it does not modify the paper's structure beyond the §5.4 framing-update conditional on outcome.

---

## 11. Acceptance criteria for Mr Code

When Task 7 is complete and ready for CinC review:

1. All four anchor verification gates passed (§6).
2. All four output deliverables produced (§8).
3. The summary markdown explicitly states which threshold (α / γ / β) fired and which framing-update applies to Paper 201 v1.1 §5.4.
4. Side-by-side comparison with Task 6 (per §8 deliverable 2) is included.
5. Git commits show: pre-registration brief committed BEFORE implementation; implementation committed; results committed after anchor verification.
6. Total Task 7 runtime documented in the summary.
7. Honest-reporting commitment in §9 stands: any departure from the pre-registered specification (sub-window width, N_TRIALS, seeds, precision budget, test statistics, thresholds) is documented and flagged in the summary as a deviation, with reasoning.

If Task 7 surfaces a methodological problem with the brief itself (e.g., empty sub-windows at smaller regimes, or numerical pathology at high mpmath precision), Mr Code surfaces the problem to CinC for resolution rather than improvising. This brief is load-bearing pre-registration: changes require CinC sign-off and a brief amendment, recorded in git.

---

**Pre-registration commit timestamp:** [to be filled by Mr Code's first commit]
**Mr Code working context:** fresh context, briefed only on this file plus pointers to (a) `task6_seven_series_first_null.py` (implementation reference), (b) `task6_seven_series_first_null_summary.md` (Anchor C target), (c) `task5_merged_regimes_detected.csv` (anchor verification source for Anchors A and B).
**CinC review of Mr Code's deliverables:** required before any update to Paper 201 v1.1 §5.4.

🐕☕⬡
