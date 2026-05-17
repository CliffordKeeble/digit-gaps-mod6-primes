# Mr Code Brief — Paper 201 Task 8: Paper 199 χ₅ Running-Sum Cross-Test at Bounded Merged Regime Upper Edges

**Author:** Dr. Clifford Keeble — ORCID 0009-0003-6828-2155
**Paper:** Paper 201 v1.2 (post-Mr-Adversary cycle-5 review, ★★★★ verdict; path (ii) to fifth star)
**Task:** Task 8 — cross-test of companion paper [7] (Paper 199, DOI 10.5281/zenodo.20242472) at the four n_5 values corresponding to Paper 201's bounded merged regime upper edges
**Branch:** `paper-201-v1-2-task8`
**Pre-registration commit:** this file, committed to `v3_12_data/briefs/` before any computation runs
**Status:** PRE-COMPUTATION — all scientific parameters locked in this brief

---

## 1. Context

Paper 201 v1.2 §5.4 reports a +1 integer increment in the observed 7-series lead at every fully-detected bounded merged regime upper edge: at u_r + 1 for r ∈ {2, 3, 4, 5} the 5-series prime index is exactly one above the integer baseline n_lo_5(r) − n_lo_7(r) that the dynamic-arrival-profile-preserving null produces (Task 7, May 2026).

Paper 201 §9 Q4 candidate (d) proposes that the +1 increment may be structurally connected to companion paper [7]'s χ₅ tight-oscillation thread: Paper 199 reports an OBSERVED monotone-size-ordering anomaly in the χ₅ running sum S₅(n) over 5-series primes at small n ≤ 100, multi-window-aggregate-corrected at empirical p ≤ 0.005. The proposed cross-test (Paper 201 v1.2 §9 Q4(iii)): evaluate Paper 199's χ₅ running sum in 5-series natural ordering at the n_5 values corresponding to Paper 201's bounded merged regime upper edges {506, 1116, 2034, 3458}, and test whether systematic phase or magnitude patterns appear at these four points that would be consistent with a +1-prime-index delay mechanism.

**Mr Adversary cycle-5 review of Paper 201 v1.2 (May 2026), ★★★★ verdict.** Mr A's cycle-5 path (ii) closing note:

> Running the §9 Q4(iii) Paper 199 cross-test before publication, or producing a clear defence of why not... I confess I cannot see why it should not be done. The four upper-edge n_5 values {506, 1116, 2034, 3458} are computable; Paper 199's running sum is in hand; the test is well-specified... It is the difference between a paper that proposes a candidate mechanism and a paper that has already tested it.

Task 8's purpose is to execute this cross-test before v1.2's Zenodo upload — converting Paper 201 §9 Q4 candidate (d) from "candidate mechanism" to "tested mechanism with named outcome" (positive / inconclusive / negative).

---

## 2. Pre-registered question

At the four n_5 values corresponding to Paper 201's bounded merged regime upper edges — n_5 ∈ {506, 1116, 2034, 3458} — does Paper 199's χ₅ running sum S₅(n) in 5-series natural ordering exhibit systematic phase or magnitude patterns relative to a randomly-sampled baseline distribution?

---

## 3. Operational definitions

**5-series natural ordering.** P_5 = {p prime : p ≡ 5 (mod 6)}, sorted ascending. So P_5[1] = 5, P_5[2] = 11, P_5[3] = 17, P_5[4] = 23, P_5[5] = 29, P_5[6] = 41, ... The natural ordering is the size-ascending ordering of mod-6-filtered 5-series primes. *(Cliff: verify this matches Paper 199's "5-series natural ordering" operationalisation before commit; if Paper 199 uses a different filter (e.g., p ≡ 4 mod 5 rather than p ≡ 5 mod 6), the brief amends.)*

**χ₅ Dirichlet character.** The non-principal real character mod 5, equivalent to the Legendre symbol (p/5):

| p mod 5 | χ₅(p) |
|---|---|
| 0 (p = 5 only) | 0 |
| 1 | +1 |
| 2 | −1 |
| 3 | −1 |
| 4 | +1 |

So χ₅(p) ∈ {+1, −1} for primes p > 5, and χ₅(5) = 0. *(Cliff: verify Paper 199 uses this real character — Legendre (p/5) — and not the complex character (which would have values in {+1, +i, −1, −i}). If complex, the brief amends to use real or imaginary part of the running sum, as Paper 199 specifies.)*

**Running sum.** S₅(n) = Σ_{i=1}^{n} χ₅(P_5[i]). Initial term S₅(1) = χ₅(5) = 0; running sum proceeds over the natural-ordered 5-series primes from there.

**Four evaluation points (pre-committed).** n_5 ∈ {506, 1116, 2034, 3458} — the smallest n such that D_5(n) ≥ u_r + 1 for regimes r ∈ {2, 3, 4, 5} respectively (matching Paper 201 §5.4 / Task 6 Anchor A).

**Baseline distribution.** S₅(n) is also computed at 1000 baseline n values drawn from the integers [200, 4000] uniformly at random, excluding any n falling within ±50 of the four evaluation points {506, 1116, 2034, 3458} to avoid contamination. The baseline range [200, 4000] spans the relevant scale range for the four evaluation points (regime 2 at n=506 to regime 5 at n=3458). Random seed for baseline draw: 8088 (distinct from Task 6's 42-family and Task 7's 1042-family; namespace-clean).

---

## 4. Pre-registered test statistic

The binding pre-registered statistic is the **concordant-extremity index (CEI)**: how many of the four S₅(n_5_r) values fall in the same tail (upper or lower 25%) of the baseline distribution.

**Procedure.**

1. Compute the four evaluation values: V_r = S₅(n_5_r) for r ∈ {2, 3, 4, 5}.
2. Compute the baseline distribution: B = {S₅(n) : n in the 1000 baseline draws}.
3. For each evaluation value V_r, compute its percentile rank π_r ∈ [0, 1] within B (the fraction of baseline values strictly less than V_r, plus half the ties).
4. Classify each π_r: "upper tail" if π_r > 0.75; "lower tail" if π_r < 0.25; "central" otherwise.
5. CEI is defined as max(#{upper tail}, #{lower tail}) ∈ {0, 1, 2, 3, 4}.

**Null distribution of CEI under uniform percentile ranking.** Under the null hypothesis that the four V_r values are exchangeable with random baseline draws (no systematic pattern at regime upper edges), each π_r is independently uniformly distributed on [0, 1], so each π_r falls in the upper, lower, or central bin with probabilities 0.25, 0.25, 0.50 respectively. The exact null distribution of CEI is computable from a trinomial:

| CEI | P(CEI | null) |
|---|---|
| 4 | 2 × 0.25⁴ = 0.0078 |
| 3 | 2 × C(4,3) × 0.25³ × 0.75 = 0.094 |
| 2 | computable, ≈ 0.422 |
| ≤ 1 | ≈ 0.476 |

(P(CEI = 4) is conservative; "either all-upper or all-lower" with each tail having p = 0.25 yields 2 × 0.25⁴ = 1/128.)

---

## 5. Pre-registered pass/fail thresholds

Committed BEFORE computation runs.

- **(α) No systematic pattern.** CEI ≤ 2 (P ≥ 0.42 under null). Paper 201 §9 Q4 candidate (d) becomes "tested with no systematic evidence at four-point cross-test"; the χ₅ candidate weakens relative to candidates (a) and (b). The §9 Q4(iii) follow-up entry is updated to "completed; null result reported"; candidate (d)'s prose is sharpened to note that the four-point cross-test gave no evidence for systematic phase-or-magnitude patterns.
- **(γ) Suggestive concordance.** CEI = 3 (P ≈ 0.094 under null). Paper 201 §9 Q4 candidate (d) becomes "tested with suggestive concordance at three of four points"; the χ₅ candidate is not eliminated but is not decisively strengthened either. Reported transparently; recommend further empirical work in a future cycle.
- **(β) Decisive concordance.** CEI = 4 (P ≈ 0.0078 under null). Paper 201 §9 Q4 candidate (d) becomes "tested with decisive four-point concordance"; the χ₅ candidate is strengthened to "leading structural-mechanism candidate among (a), (b), (d)". The §9 Q4 prose is updated to reflect this elevation; the Paper 199 connection becomes a tested structural feature rather than a candidate.

In all three outcomes, the four V_r values, their four percentile ranks π_r, the baseline distribution summary statistics (median, IQR, range), the sign pattern of V_r, and the CEI value are reported.

**The discipline:** thresholds are committed here, not after data is seen. Whichever way CEI lands, the framing-update rule above is applied without rhetorical manoeuvring.

---

## 6. Anchor verification gates (HALT-ON-MISMATCH)

Before any cross-test result is reported, the script must reproduce the following deterministic anchors:

**Anchor A — Four-point n_5 values.** Compute deterministic 5-series cumulative-product digit-lengths and verify that the smallest n with D_5(n) ≥ u_r + 1 for r ∈ {2, 3, 4, 5} equals {506, 1116, 2034, 3458} respectively. These are the same anchors as Tasks 6 and 7 (the "observed n_5" column).

**Anchor B — S₅(n) sanity check.** Compute S₅(n) at a small reference value and check against a known reference (or hand-computed expectation): for example, S₅(10) should be the sum of χ₅ over the first 10 5-series primes {5, 11, 17, 23, 29, 41, 47, 53, 59, 71}. Compute by hand or by independent code: χ₅ values for these primes are:
- 5 → 0
- 11 → 1 (11 ≡ 1 mod 5)
- 17 → −1 (17 ≡ 2 mod 5)
- 23 → −1 (23 ≡ 3 mod 5)
- 29 → 1 (29 ≡ 4 mod 5)
- 41 → 1 (41 ≡ 1 mod 5)
- 47 → −1 (47 ≡ 2 mod 5)
- 53 → −1 (53 ≡ 3 mod 5)
- 59 → 1 (59 ≡ 4 mod 5)
- 71 → 1 (71 ≡ 1 mod 5)

Sum: 0 + 1 − 1 − 1 + 1 + 1 − 1 − 1 + 1 + 1 = +1. Therefore S₅(10) = +1 is the expected reference value. Halt on mismatch.

**Anchor C — Paper 199 cross-reference.** If Paper 199's repository contains a published S₅(n) reference table or trajectory CSV, verify the script's S₅(n) computation against three or more points from Paper 199's published values. *(Cliff: confirm location of Paper 199's S₅(n) reference data; brief amends with explicit pointer if available.)* If no reference table is published, Anchor B's hand-computed value is the binding sanity check.

**Anchor D — Baseline exclusion.** Verify that the 1000 baseline draws contain no n within ±50 of any of {506, 1116, 2034, 3458}. Halt if any excluded n appears in the baseline sample.

---

## 7. Implementation specification

**Language and libraries.** Python 3.11+, sympy (or hard-coded sieve) for prime enumeration, numpy for baseline distribution computation, pandas for output CSV, matplotlib for visualisation. No mpmath needed (S₅(n) is integer-valued and bounded; no high-precision arithmetic required).

**Repository location.** `v3_12_data/task8_paper199_crosstest.py` in the digit-gaps-mod6-primes repository.

**Code structure.** The Task 8 script:
1. Enumerates primes up to a bound sufficient for the 4000-th 5-series prime (estimated ~50,000 by PNT for arithmetic progressions; the script should overshoot safely).
2. Filters to P_5 = {p ≡ 5 mod 6}, sorted ascending.
3. Computes S_5(n) for all n ∈ [1, 3500] (covers the largest evaluation point n = 3458).
4. Verifies Anchors A, B, D.
5. Computes V_r at four evaluation points.
6. Draws 1000 baseline n values (seed 8088) from [200, 4000] excluding ±50 around evaluation points.
7. Computes baseline distribution B = {S₅(n) : n in baseline draws}.
8. Computes percentile ranks π_r and CEI.
9. Reports outcome, updates Paper 201 §9 Q4 candidate (d) per pre-registered framing-update rule.

**Computational budget guidance.** Prime enumeration up to ~50,000 and S_5(n) computation up to n = 3500 are both lightweight (< 1 second each). Baseline distribution computation at 1000 points adds a few seconds. Total Task 8 runtime expected < 30 seconds. Well under any meaningful budget.

**Branch and commits.** Pre-registration commit (this brief): on branch `paper-201-v1-2-task8`, BEFORE any implementation work. Implementation commits follow. Results commits happen only after anchor verification gates pass.

---

## 8. Output deliverables

The following files are produced and committed once the pipeline runs to completion:

1. **`v3_12_data/results/task8_paper199_crosstest.csv`** — long-format data:
   `n, S_5_n, source` where source ∈ {evaluation, baseline}.
   1004 rows total (4 evaluation + 1000 baseline).

2. **`v3_12_data/results/task8_paper199_crosstest_summary.md`** — aggregate summary including:
   - The four V_r = S₅(n_5_r) values.
   - The four percentile ranks π_r.
   - The classification of each π_r (upper / lower / central tail).
   - CEI value.
   - Baseline distribution summary (median, IQR, range, n = 1000).
   - The pre-registered threshold this result triggers (α / γ / β).
   - One paragraph stating the framing-update applied to Paper 201 §9 Q4 candidate (d), per §5 above.

3. **`v3_12_data/results/task8_baseline_distribution.png`** — single-panel figure showing the baseline distribution of S₅(n) as a histogram, with the four V_r values marked by labelled vertical lines, the upper/lower tail thresholds (25th, 75th percentile) marked, and the CEI value annotated.

4. **`v3_12_data/briefs/mr_code_brief_paper_201_task8.md`** — this brief, committed BEFORE the implementation.

---

## 9. Honest-reporting commitment

The pre-registration discipline of the 2I Programme commits to:

- Reporting the result faithfully regardless of which threshold (α / γ / β) is triggered.
- No post-hoc adjustment of the baseline range (n ∈ [200, 4000]), the baseline size (1000 draws), the exclusion margin (±50 around evaluation points), the tail thresholds (25th / 75th percentile), or the test statistic (CEI).
- No post-hoc selection of "any of the four S₅(n_5_r) is large" or similar alternative readings if CEI lands at α.
- If anchor verification fails, the failure is reported and investigated, not silently masked.
- The framing update in Paper 201 v1.3 §9 Q4 candidate (d) follows the rule in §5 above mechanically, not strategically.

Track record: F1 (cascade conjecture, refined out of v3.4); F3 (structural-distinguishing-features, refined out at v4.2); F4 (doubling-at-2.3× anchor, refined out at v5.0); Task 6 (static-count null, β fired, framing honestly absorbed); Task 7 (dynamic null, β fired, integer-valued reading honestly absorbed without rhetorical overreach). Task 8's outcome — positive, suggestive, or negative — falls under the same discipline.

The (α) outcome — no systematic pattern — would weaken candidate (d) relative to (a) and (b) in Paper 201 §9 Q4. That is what the test is for. The (α) outcome is published if it occurs.

---

## 10. What is NOT in scope for Task 8

Out of scope (do not perform; do not report on):

- **Modifications to Paper 199's pre-registration.** Task 8 evaluates Paper 199's already-published S₅(n) trajectory at four new n_5 points. It does not re-run Paper 199's monotone-size-ordering test, does not add to or modify Paper 199's pre-registered statistics, and does not affect Paper 199's published findings. Paper 199's record is referenced, not modified.
- **Sensitivity analysis on baseline range, tail threshold, baseline size.** The pre-committed values [200, 4000], 25th/75th percentiles, and 1000 draws are the substantive choices for the confirmatory test. Exploratory sweeps on these parameters are post-publication follow-ups if the result is (γ).
- **Alternative test statistics on the same data.** CEI is pre-committed; sign-only tests, magnitude-only tests, derivative-based tests etc. are not pre-registered for Task 8 and would be exploratory follow-ups.
- **Sub-window analysis or stratification.** The Task 8 test is a four-point cross-test against a global baseline, not a window-stratified analysis.
- **Modifications to Paper 201 §§ other than §9 Q4 candidate (d).** Task 8's framing-update affects only §9 Q4 candidate (d)'s status; §5.4, §5.6, abstract finding (iii), and other §9 candidates are unchanged regardless of outcome.

---

## 11. Acceptance criteria for Mr Code

When Task 8 is complete and ready for CinC review:

1. All four anchor verification gates passed (§6).
2. All four output deliverables produced (§8).
3. The summary markdown explicitly states the CEI value, the pre-registered threshold it triggers (α / γ / β), and the framing-update applies to Paper 201 §9 Q4 candidate (d).
4. Git commits show: pre-registration brief committed BEFORE implementation; implementation committed; results committed after anchor verification.
5. Total Task 8 runtime documented in the summary.
6. Honest-reporting commitment in §9 stands: any departure from the pre-registered specification (baseline range, tail thresholds, baseline size, test statistic, framing-update rule) is documented and flagged in the summary as a deviation, with reasoning.

If Task 8 surfaces a methodological problem with the brief itself (e.g., the operational definition of S₅(n) at §3 disagrees with Paper 199's published definition, or the baseline range is inappropriate given the prime distribution), Mr Code surfaces the problem to CinC for resolution rather than improvising. This brief is load-bearing pre-registration: changes require CinC sign-off and a brief amendment, recorded in git.

---

**Pre-registration commit timestamp:** [to be filled by Mr Code's first commit]
**Mr Code working context:** fresh context, briefed only on this file plus pointers to (a) `task5_merged_regimes_detected.csv` (Anchor A reference for the four n_5 values; same source as Tasks 6 and 7 used), (b) `task7_dynamic_null_variant_summary.md` (cross-reference for the four n_5 values appearing consistently across the bounded-merged-regime computational record), and (c) Paper 199's repository at the GitHub address provided by Cliff if available (for Anchor C reference; otherwise Anchor B's hand-computed S₅(10) = +1 is binding).
**CinC review of Mr Code's deliverables:** required before any update to Paper 201 v1.2 §9 Q4 candidate (d).

🐕☕⬡
