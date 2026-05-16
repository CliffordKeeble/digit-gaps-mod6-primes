# Mr Code Brief — Paper 201 Task 6: Null Distribution for the 7-Series-Lands-First Observation

**Author:** Dr. Clifford Keeble — ORCID 0009-0003-6828-2155
**Paper:** Paper 201 v1.1 candidate (post-Mr-Adversary cycle-1 review)
**Task:** Task 6 — null-distribution computation for the §5.4 observation
**Branch:** `paper-201-v1-1-task6`
**Pre-registration commit:** this file, committed to `v3_12_data/briefs/` before any computation runs
**Status:** PRE-COMPUTATION — all scientific parameters locked in this brief

---

## 1. Context

Paper 201 v1.0 §5.4 reports an auxiliary observation surfaced by Task 5: at every fully-detected bounded merged regime's upper edge, the 7-series lands first (i.e., the 7-series cumulative product reaches digit-length `u_r + 1` at a smaller prime index than the 5-series does), with leads as follows:

| Regime r | Upper edge u_r | u_r + 1 | n_7 | n_5 | Lead (n_5 − n_7) |
|---|---|---|---|---|---|
| 2 | 1717 | 1718 | 503 | 506 | 3 primes |
| 3 | 4231 | 4232 | 1112 | 1116 | 4 primes |
| 4 | 8318 | 8319 | 2029 | 2034 | 5 primes |
| 5 | 15045 | 15046 | 3452 | 3458 | 6 primes |

The observation is 4 of 4 fully-detected instances. It was surfaced auxiliarily, not pre-registered.

**Mr Adversary cycle-1 review of Paper 201 v1.0 (May 2026)** required a NULL gate before this observation can be promoted from "clean per-regime structural fact" to a falsifier-grade structural claim. Mr A. observed:

> The binary "which series lands first" coin-flip null gives (1/2)⁴ = 6.25% — barely sub-5% one-tailed, and not at all decisive at four instances. The lead-size null is the stronger test: under random ordering of the n_5 and n_7 prime indices near each regime upper edge, the probability of observing 7-series lead sizes of {3, 4, 5, 6} respectively is substantially smaller than 1/16, and gives the claim genuine weight if borne out.

Task 6's purpose is to execute both nulls and report results honestly.

---

## 2. Pre-registered question

Is the four-regime pattern (7-series first at all four fully-detected regimes, with leads {3, 4, 5, 6} primes) distinguished from chance under (a) a binary coin-flip null and (b) a label-permutation null that preserves prime size distribution but randomises residue-class assignment within a window around each regime upper edge?

---

## 3. Pre-registered nulls

### 3.1 Null A — Binary coin-flip (analytic, no computation)

Under the null hypothesis that the 7-series leads each regime with probability 1/2 independently across regimes:

- P(7-series leads at all 4 regimes) = (1/2)⁴ = 0.0625.

This is the trivial floor. It is reported for completeness; no computation is required. It is *not decisive at four instances* by itself.

### 3.2 Null B — Label-permutation null (Monte Carlo)

The substantive test. Operational specification follows.

**Null hypothesis (H₀).** Within a digit-length window around regime r's upper edge u_r, the residue-class label (P₅ vs P₇) of each prime is exchangeable. That is, the observed labelling is one of many equally likely labellings preserving the *count* of P₅ and P₇ primes in the window.

**Window definition.** Pre-committed window: for regime r ∈ {2, 3, 4, 5}, the window W_r consists of all primes p with `log₁₀(p)` such that the partial cumulative product of either series visits digit-length within `[u_r − 200, u_r + 200]`. In practice, the window is defined operationally by enumerating primes whose presence in the cumulative-product sequence is bracketed by these digit-length bounds in either series. The half-width `200 digit-lengths` is committed here and not adjusted post hoc.

**Permutation procedure.**

1. Enumerate the actual P₅ and P₇ primes contributing to either cumulative product within W_r.
2. Let M_5 = |W_r ∩ P₅| and M_7 = |W_r ∩ P₇| be the observed counts.
3. Pool the M_5 + M_7 primes from W_r. Their *sizes* are fixed by the data. Only their *labels* are randomised.
4. For each Monte Carlo trial: uniformly at random select M_7 of the M_5 + M_7 pooled primes to relabel as "7-series", with the remaining M_5 relabelled as "5-series". This preserves both counts and the prime-size distribution.
5. Form simulated cumulative products: prefix the deterministic cumulative products of P₅ and P₇ up to the prime immediately before W_r starts (computed once); then append products over the relabelled 5-set and 7-set respectively, in size order.
6. Compute n_5^sim and n_7^sim — the simulated smallest n in each series such that D_i^sim(n) ≥ u_r + 1.
7. Lead^sim_r = n_5^sim − n_7^sim. Positive means 7-series first; negative means 5-series first.

**Number of trials.** N_TRIALS = 10,000 per regime. The four regimes are simulated independently (different seeded streams per regime).

**Random seed.** Master seed = 42 (canonical 2I Programme seed). Per-regime seeds = 42 + r where r is the regime index (so regime 2 uses seed 44, regime 3 uses 45, regime 4 uses 46, regime 5 uses 47).

**Numerical precision.** All cumulative-product digit-length computations use `mpmath` at 200-decimal-place precision for the regime-4 and regime-5 windows (digit-lengths > 8000). Regime-2 and regime-3 windows can use `mpmath` at 100-dps as a precision budget (digit-lengths < 5000). Anchor verification (§5 below) must match the deterministic observed values exactly under the chosen precision; any mismatch halts the pipeline.

### 3.3 Joint test statistics

Three joint statistics are pre-committed for reporting:

**(J-i) Joint sign p-value.** Under H₀, what is the probability that the simulated 7-series leads at ALL FOUR regimes? Formally:

`p_sign = (1/N_TRIALS) × #{trials where Lead^sim_r > 0 for all r ∈ {2,3,4,5}}`

Computed by taking the trial-by-trial Cartesian product across the four regimes' independent simulation streams (pair the 1st trial of regime 2 with the 1st trial of regime 3 with the 1st of regime 4 with the 1st of regime 5, etc.).

**(J-ii) Joint magnitude p-value.** Under H₀, what is the probability that the simulated 7-series leads exceed the observed leads at ALL FOUR regimes simultaneously?

`p_magnitude = (1/N_TRIALS) × #{trials where Lead^sim_r ≥ {3, 4, 5, 6} respectively}`

This is the headline statistic.

**(J-iii) Per-regime tail probabilities and Fisher combined.** For each regime r individually:

`p_r = (1/N_TRIALS) × #{trials where Lead^sim_r ≥ observed lead at r}`

Combined via Fisher's method: `χ² = −2 Σ ln(p_r)`, df = 8, with combined p-value from the χ²₈ distribution.

All three statistics are reported regardless of outcome.

---

## 4. Pre-registered pass/fail thresholds

Committed BEFORE computation runs. The headline statistic is **p_magnitude (J-ii)**.

- **(α) Null does not fire — observation stays at "clean per-regime fact".** p_magnitude ≥ 0.10. The §5.4 framing in Paper 201 v1.1 is unchanged: 4-of-4 observation reported as auxiliary positive structural fact with Q4 open.
- **(γ) Intermediate — no framing change.** 0.05 ≤ p_magnitude < 0.10. Paper 201 v1.1 retains the v1.0 framing and reports the null result with intermediate-range honesty: "Null B gives p_magnitude = [value], not sub-5% but suggestive."
- **(β) Null fires — observation hardens.** p_magnitude < 0.05. Paper 201 v1.1 §5.4 is rewritten: the 7-series-first observation is promoted from auxiliary positive fact to falsifier-grade structural signal. Q4 (in §9) is reframed: instead of "what about the 7-series's prime structure determines the upper edges", the question becomes "the 7-series-first signal is distinguished from null at p_magnitude = [value]; analytic-number-theory candidate mechanisms (L(s, χ₅) zero spacings, additive distribution of log₁₀(p) across residue classes, Chebyshev-bias-adjacent effects) are open avenues."

In all three outcomes, the binary null result (p_binary = 0.0625) is reported alongside as context.

**The discipline:** thresholds are committed here, not after the data is seen. Whichever way p_magnitude lands, the framing-update rule above is applied without rhetorical manoeuvring.

---

## 5. Anchor verification gates (HALT-ON-MISMATCH)

Before any null result is reported, the script must reproduce the following deterministic anchors:

**Anchor A — Observed leads.** Compute deterministic cumulative products over actual P₅ and P₇ and verify the observed (n_7, n_5) pairs at u_r + 1 for r ∈ {2, 3, 4, 5}:

| Regime r | u_r + 1 | Expected n_7 | Expected n_5 | Expected lead |
|---|---|---|---|---|
| 2 | 1718 | 503 | 506 | 3 |
| 3 | 4232 | 1112 | 1116 | 4 |
| 4 | 8319 | 2029 | 2034 | 5 |
| 5 | 15046 | 3452 | 3458 | 6 |

Any mismatch halts the pipeline with an error before Null B trials are run.

**Anchor B — Regime upper edges.** Verify the regime upper edges from Paper 201 §5.2 / Task 5: {1717, 4231, 8318, 15045}. Halt on mismatch.

**Anchor C — Reference implementation cross-check.** The Paper 201 §8 / Task 5 verification script `task5_merged_regimes_detected.csv` already records these values from Task 5 (May 2026, N_MAX = 4000). Task 6 must read this CSV and assert agreement before proceeding. Halt on mismatch.

The anchor-verification discipline is the same one used in all previous Mr Code tasks. The pipeline halts rather than overwriting on mismatch.

---

## 6. Implementation specification

**Language and libraries.** Python 3.11+, `mpmath` for high-precision arithmetic, `sympy` (or hard-coded prime sieve) for prime enumeration, `numpy` for trial-array bookkeeping, `pandas` for output CSV, `matplotlib` for the histogram plot.

**Repository location.** `v3_12_data/task6_seven_series_first_null.py` in the digit-gaps-mod6-primes repository.

**Computational budget guidance.** Regime 5's window contains primes contributing through digit-length ~15200. Prime enumeration up to ~25,000 is sufficient (with margin). The full Task 6 should complete in well under 30 minutes on a standard laptop.

**Branch and commits.** Pre-registration commit (this brief): on branch `paper-201-v1-1-task6`, BEFORE any implementation work. Implementation commits follow. Results commits happen only after anchor verification gates pass.

---

## 7. Output deliverables

The following files are produced and committed once the pipeline runs to completion:

1. **`v3_12_data/results/task6_seven_series_first_null.csv`** — long-format trial data:
   `regime, trial_id, n_5_sim, n_7_sim, lead_sim, lead_observed`
   40,000 rows (4 regimes × 10,000 trials).

2. **`v3_12_data/results/task6_seven_series_first_null_summary.md`** — aggregate summary including:
   - The four per-regime histograms' summary statistics (mean, median, IQR, range of Lead^sim_r).
   - p_binary = 0.0625 (analytic, no computation).
   - p_sign (J-i).
   - p_magnitude (J-ii) — the headline.
   - Per-regime tail p_r values and Fisher's combined.
   - The pre-registered threshold this result triggers (α / γ / β).
   - One paragraph stating the framing-update applied to Paper 201 §5.4, per §4 above.

3. **`v3_12_data/results/task6_lead_distribution.png`** — four-panel figure, one panel per regime, showing the histogram of Lead^sim_r with the observed lead value marked by a vertical line. Caption includes p_r per panel.

4. **`v3_12_data/briefs/mr_code_brief_paper_201_task6.md`** — this brief, committed BEFORE the implementation. (Already done by the time Mr Code reads this.)

---

## 8. Honest-reporting commitment

The pre-registration discipline of the 2I Programme commits to:

- Reporting the result faithfully regardless of which threshold is triggered.
- No post-hoc adjustment of the window width, the precision budget, the threshold values, or the test statistic.
- No selective reporting of regime-level results to fit a desired story: all four per-regime histograms and tail p-values are reported.
- If anchor verification fails, the failure is reported and investigated, not silently masked.
- The framing update in Paper 201 v1.1 §5.4 follows the rule in §4 above mechanically, not strategically.

Track record: F1 (cascade conjecture, refined out of v3.4); F3 (structural-distinguishing-features, refined out at v4.2); F4 (doubling-at-2.3× anchor, refined out at v5.0). Each pre-registered, each refined faithfully on (β-broken) outcome. F4 in particular: the (β-broken) outcome at the 3→4 transition (width 1.624, gap 1.628 vs predicted 2.07–2.53) was absorbed without rhetorical manoeuvring, producing the decelerating-ratio reframing that is now Paper 201 §5.3.

Task 6 falls under the same discipline.

---

## 9. What is NOT in scope for Task 6

Out of scope (do not perform; do not report on):

- Modelling the "physical" mechanism behind the 7-first observation. The brief tests *whether the observation is distinguished from null*, not why. Mechanism candidates (L(s, χ₅) zero spacings; Chebyshev-bias-adjacent effects) are mentioned in Paper 201 §9 Q4 and remain open regardless of Task 6's outcome.
- Re-deriving Chebyshev's bias counts for π(x; 6, 5) and π(x; 6, 1) within the window. The label-permutation null preserves these counts as observed; it does not interrogate them.
- Extending the analysis to regime 6 (truncated; upper edge past tested D_HI). Regime 6 has no observed lead to test.
- Probing further empirical regimes at N_MAX > 4000. That is a separate empirical-extension task; reference Paper 201 §9 Q2(c) as the natural follow-up.
- Modifications to the F5 falsifier specification (Paper 3 v5.1 §6.3 / Paper 201 §6). The F5 thresholds are unchanged and unaffected by Task 6's outcome.

---

## 10. Acceptance criteria for Mr Code

When Task 6 is complete and ready for CinC review:

1. All four anchor verification gates passed (§5).
2. All four output deliverables produced (§7).
3. The summary markdown explicitly states which threshold (α / γ / β) fired and which framing-update applies.
4. Git commits show: pre-registration brief committed BEFORE implementation; implementation committed; results committed after anchor verification.
5. The total Task 6 runtime is documented in the summary (for budget/reproducibility tracking).
6. Honest-reporting commitment in §8 stands: any departure from the pre-registered specification (window width, N_TRIALS, seeds, precision budget, test statistics, thresholds) is documented and flagged in the summary as a deviation, with reasoning.

If Task 6 surfaces a methodological problem with the brief itself (e.g., the window definition is ambiguous in some edge case), Mr Code surfaces the problem to CinC for resolution rather than improvising. This brief is load-bearing pre-registration: changes require CinC sign-off and a brief amendment, recorded in git.

---

**Pre-registration commit timestamp:** [to be filled by Mr Code's first commit]
**Mr Code working context:** fresh context, briefed only on this file plus a pointer to `task5_merged_regimes_detected.csv` for anchor verification.
**CinC review of Mr Code's deliverables:** required before any update to Paper 201 §5.4.

🐕☕⬡
