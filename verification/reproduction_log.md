# Reproduction Log

**Script:** `verification/full_null_model.py` (extracted from Digit_Gaps_Mod6 v2.0 PDF appendix)
**Paper:** Digit_Gaps_Mod6_v2_3.md (v2.3, April 2026)
**Run date:** 2026-04-13
**Runtime:** 59.1 seconds (paper claims ~32s; hardware difference, not a concern)
**Python:** 3.13, standard library only

## Headline Claims vs Reproduction

| Paper claim | Paper value | Reproduced value | Match |
|---|---|---|---|
| 5-series prime count | 485,503 | 485,503 | EXACT |
| 7-series prime count | 485,199 | 485,199 | EXACT |
| Max digit-length | 3,254,959 | 3,254,959 | EXACT |
| Spacings in {1,2,3} | 99.9998% | 99.9998% | EXACT |
| Total spacings | 2,355,220 | 2,355,220 | EXACT |
| Max spacing | 23 | 23 | EXACT |
| Spacing exceptions | "three at 5, one at 7, one at 23" | {5: 3, 7: 1, 23: 1} | EXACT |
| s=1 frequency | ~68% | 68.0% | EXACT |
| s=2 frequency | ~26% | 25.8% | EXACT |
| s=3 frequency | ~6% | 6.2% | EXACT |
| Coincident gap % | 72.4% | 72.4% | EXACT |
| Cluster count (200k) | 13 | 13 | EXACT |
| Power-law beta | 0.637 +/- 0.029 | 0.6371 +/- 0.0293 | EXACT |
| R-squared | 0.979 | 0.979 | EXACT |
| Cluster z-score | -2.04 | -2.04 | EXACT |
| ln(2)/ln(3) | 0.6309 | 0.6309 | EXACT |

## Band-by-Band Statistics (Table 4)

| Band | Paper spacings | Reproduced | Paper s1/s2/s3 | Reproduced |
|---|---|---|---|---|
| 0-500k | 343,737 | 343,737 | 62.9/28.8/8.3 | 62.9/28.8/8.3 |
| 500k-1M | 357,423 | 357,423 | 66.7/26.8/6.5 | 66.7/26.8/6.5 |
| 1M-1.5M | 361,454 | 361,454 | 67.3/27.2/5.6 | 67.3/27.2/5.6 |
| 1.5M-2M | 365,192 | 365,192 | 68.4/26.2/5.4 | 68.4/26.2/5.4 |
| 2M-2.5M | 367,540 | 367,540 | 69.6/24.8/5.6 | 69.6/24.8/5.6 |
| 2.5M-3.25M | 559,869 | 559,869 | 71.1/23.0/5.9 | 71.1/23.0/5.9 |

## Null Model Comparison (Table 5)

| Metric | Paper null mean | Reproduced null mean | Paper null std | Reproduced null std |
|---|---|---|---|---|
| In {1,2,3} | 100.000% | 100.000% | 0.000% | 0.000 |
| Max spacing | 10.7 | 10.7 | 1.9 | 1.947 |
| s=1 freq | 68.1% | 68.1% | 0.9% | 0.936 |
| s=2 freq | 25.9% | 25.9% | 1.1% | 1.140 |
| s=3 freq | 6.0% | 6.0% | 0.3% | 0.337 |
| Coinc gap % | 72.6% | 72.6% | 0.4% | 0.437 |

## Sensitivity Analysis (Table 7)

| Window | Paper clusters | Reproduced | Paper beta | Reproduced | Paper R2 | Reproduced |
|---|---|---|---|---|---|---|
| 30 | 13 | 13 | 0.6371 | 0.6371 | 0.978 | 0.978 |
| 40 | 13 | 13 | 0.6373 | 0.6373 | 0.979 | 0.979 |
| 50 | 13 | 13 | 0.6371 | 0.6371 | 0.979 | 0.979 |
| 60 | 13 | 13 | 0.6366 | 0.6366 | 0.980 | 0.980 |
| 70 | 12 | 12 | 0.6229 | 0.6229 | 0.964 | 0.964 |

Note: Paper Table 7 shows "min gaps: 10-20" as a range, stating the exponent is "completely insensitive to minimum gap count." Reproduction confirms this -- all min_gaps values (10, 15, 20) produce identical results at each window size.

## Null Model Cluster Counts (Table 6)

| Trial | Clusters | beta |
|---|---|---|
| 0 | 29 | 0.4883 |
| 1 | 34 | 0.7091 |
| 2 | 25 | 0.6263 |
| 3 | 38 | 0.7099 |
| 4 | 40 | 0.5338 |
| 5 | 27 | 0.8272 |
| 6 | 38 | 0.4789 |
| 7 | 20 | 0.5067 |
| 8 | 23 | 0.4516 |
| 9 | 18 | 0.6146 |

Null mean: 29.2, null std: 7.9 -- matches paper Table 6 exactly.
Null betas range 0.45 to 0.83 -- matches paper's "scattered from 0.45 to 0.83."

## Verdict

**All headline claims reproduced exactly.** No discrepancies found. The script extracted from the PDF appendix is faithful to the paper's numerical results across every table and every metric checked.

## Note on script provenance

The script was extracted from the v2.0 PDF appendix (Appendix A). The paper text is v2.3, but v2.1-v2.3 revisions were prose/citation corrections only -- no mathematical content changed. The script therefore correctly reproduces v2.3 claims.

---

## v2.6 -> v2.7 Adversary Follow-up Runs (May 12 2026)

### Task 1 — Synchronisation-Budget Null Comparison

**Script:** `null-tests/synch_budget_null.py`
**Run date:** 2026-05-12
**Runtime:** 64.1s
**Seed:** trial * 137 + 42 (10 trials, full scale, sieve to 15M)

| Metric | Reproduced value |
|---|---|
| budget_real | 0.099682 (9.97%) |
| budget_null_mean | 0.105791 (10.58%) |
| budget_null_std | 0.022484 (2.25%) |
| z_score | -0.272 |
| Real-prime cluster count (full scale) | 48 |
| Real-prime total cluster span | 324,460 digits |
| max_d (real) | 3,254,959 |

Determinism: re-running with the same seed scheme produces identical numbers (verified by single run -- algorithm is fully deterministic given seeds).

**Flag (v2.6 §5.4 mismatch):** under the §5.2 cluster definition (window=50, min_gaps>=20, merge_dist=500) the real-prime budget is 9.97%, not the ~6% v2.6 §5.4 reports. See findings.md §12.1 for hypothesis (likely tied to the §5.2 36-vs-47 cluster-count discrepancy investigated in Task 2).

### Task 5 — §5.3 Alternation Statistic Pre-Registration

**Type:** Git archaeology, no compute.
**Run date:** 2026-05-15

| Artefact | Commit | Date (UTC+1) |
|---|---|---|
| Earliest §5.3 specification (paper text) | `74b18be` | 2026-04-13 10:45:51 |
| Earliest null-test computation | `314ab85` | 2026-04-13 10:58:41 |
| First explicit pre-reg commit anywhere in repo | `06d7e6e` / `7fa5e38` | 2026-05-10 15:57:47 |

**Verdict:** NOT PRE-REGISTERED. §5.3 paper text explicitly labels the alternation statistic "(Observational, Pending Null Test)" with self-disclaimed pareidolia risk. No separate prediction commit exists for §5.3 prior to its null test. The 44% descriptive statistic was already computed when the repo was scaffolded (it appears in the paper text from commit zero). Pattern 19/27 pre-reg practice began 2026-05-10, ~4 weeks after §5.3 was written.

See findings.md §12.5.

### Task 6 — §6.2 Cluster-Count Direction Pre-Registration

**Type:** Git archaeology, no compute.
**Run date:** 2026-05-15

| Artefact | Commit | Date (UTC+1) |
|---|---|---|
| Earliest test definition (`full_null_model.py`) | `74b18be` | 2026-04-13 10:45:51 |
| Earliest paper specification (§6.2 text + z = -2.04 result) | `74b18be` | 2026-04-13 10:45:51 |
| Earliest reproduction (reproduction_log.md verifying z = -2.04) | `858b97e` | 2026-04-13 10:49:57 |
| First pre-reg commit anywhere in repo | `06d7e6e` / `7fa5e38` | 2026-05-10 15:57:47 |

**Verdict:** DIRECTION NOT PRE-COMMITTED. Two-tailed p-value required for v2.7.

Corrected p-values (key numbers):
- v2.3 headline (10 trials): z = -2.04, one-tailed p = 0.0207, **two-tailed p = 0.0414** (significant at α=0.05).
- 100-trial follow-up (findings §7.2): z = -1.37, one-tailed p = 0.0853, **two-tailed p = 0.1707** (NOT significant at α=0.05).
- 100-trial empirical: 4/100 trials ≤ 13 clusters; **two-tailed empirical p ≈ 0.08** (NOT significant at α=0.05).

With the 100-trial follow-up applied two-tailed, the cluster-count separation is no longer significant. The R² result (findings §7.3, 0/100 null trials reach R² ≥ 0.979) is robust to direction and remains the cleanest surviving prime-specific claim.

See findings.md §12.6.

### Task 2 — Cluster-Count Reconciliation (36 vs 47/48)

**Script:** `null-tests/cluster_count_reconcile.py`
**Run date:** 2026-05-15
**Runtime:** 49.9s
**Real primes only** (no null trials)

Full-scale parameter sweep at window in {30, 40, 50, 60, 70}, min_gaps in {20, 22, 25, 28, 30, 35, 40}, merge_dist in {200, 500, 1000, 2000, 5000}.

**Result.** The §5.2 discrepancy is purely a `merge_dist` parameter difference:

| Parameter set | n_clusters | n_inter_gaps | budget% |
|---|---|---|---|
| window=50, min_gaps=20, merge_dist=500 (canonical) | 48 | 47 | 9.97% |
| window=50, min_gaps=20, merge_dist=2000 | 36 | 35 | 10.28% |

Both numbers in v2.6 §5.2 are correct under their respective parameter sets, but only merge_dist=500 is the script-level default used everywhere else in the repo. The 36-cluster headline uses an undocumented merge_dist=2000.

**Determinism:** real-prime computation only; no random component; identical on re-run.

**Auxiliary:** at window=50, min_gaps is redundant in [20, 35] — every coincident-only 50-window contains >= 35 coincident gaps at full scale.

**Updates:** docstring of `null-tests/power_law_full_scale.py` now documents the canonical parameter set explicitly.

**Note re Task 1 §5.4 mismatch:** not resolved here. Even merge_dist=2000 gives budget 10.28%, far from §5.4's headline ~6%. §5.4 uses a different metric. See findings.md §12.2.

See findings.md §12.2.

### Task 3 — R² vs Cumulative Scale (8 scales × 100 trials)

**Script:** `null-tests/r2_vs_scale.py`
**Run date:** 2026-05-15
**Runtime:** 502.3s (~8.4 min)
**Seeds:** trial * 137 + 42 + scale_offset; scale_offset = 0 for all scales (shared draws). Documented in script docstring.
**Params:** window=50, min_gaps=20, merge_dist=500 (canonical).

| Scale | n_cl real | R²_real | R²_null mean | R²_null std | z |
|---|---|---|---|---|---|
| 50,000 | 7 | 0.9840 | 0.3727 | 0.2315 | +2.64 |
| 100,000 | 10 | 0.9859 | 0.4816 | 0.1968 | +2.56 |
| 200,000 | 13 | 0.9792 | 0.5767 | 0.1833 | +2.20 |
| 300,000 | 15 | 0.9786 | 0.5270 | 0.2164 | +2.09 |
| 500,000 | 19 | 0.5955 | 0.5851 | 0.1874 | +0.06 |
| 1,000,000 | 29 | 0.1960 | 0.5697 | 0.1976 | -1.89 |
| 2,000,000 | 36 | 0.3502 | 0.5643 | 0.1976 | -1.08 |
| 3,250,000 | 48 | 0.2264 | 0.2900 | 0.1928 | -0.33 |

**200k headline reproduces exactly** under canonical merge_dist=500: R² = 0.9792, β = 0.6371 (paper: 0.979, 0.637). Confirms Task 2's canonical-parameter recommendation.

**Trajectory:** clean phase boundary at ~300k → 500k. R² above null +2σ from 50k–300k, collapses at 500k, falls below null mean from 1M onward. The "200k regime" extends 50k–300k, not narrowly 200k.

**Outputs:**
- `null-tests/results/r2_vs_scale_per_trial.csv` (800 trial-rows + 8 real-prime rows)
- `null-tests/results/r2_vs_scale_summary.csv` (8 scale-summary rows)
- `figures/r2_vs_scale.png` and `figures/r2_vs_scale.svg`

See findings.md §12.3.

### Task 4 — Base-Independence Test for R²

**Script:** `null-tests/base_independence.py`
**Run date:** 2026-05-15
**Runtime:** 412.9s (~7 min)
**Seeds:** trial * 137 + 42 + base_offset; base_offset = 0 for all bases (shared draws across bases).

**Scales (all = 200,000-base-10-digit-equivalent):**

| Base | Cumulative scale | window | min_gaps | merge_dist |
|---|---|---|---|---|
| base-10 |       200,000 digits |  50 | 20 |    500 |
| base-2  | 664,386 bits         | 166 | 20 | 1,661 |
| base-6  | 257,019 base-6 digits|  64 | 20 |    643 |

**Real-prime results:**

| Base | n_cl | β_real | R²_real |
|---|---|---|---|
| base-10 | 13 | 0.6371 | 0.9792 |
| base-2  | 11 | 0.6173 | 0.9399 |
| base-6  | 13 | 0.6335 | 0.9765 |

**Real-vs-null:**

| Base | z(R²) | z(β) | #null ≥ real R² |
|---|---|---|---|
| base-10 | +2.20 | +0.53 | 0/100 |
| base-2  | +2.87 | +0.81 | 0/99  |
| base-6  | +2.10 | +0.43 | 0/100 |

**Verdict: R² and β are both base-independent.** Power-law structure survives base change cleanly: z(R²) ≥ +2.0 in every base, 0 null trials reach the real R², β within ±0.02 across bases (all close to ln(2)/ln(3) = 0.6309).

**Outputs:**
- `null-tests/results/base_independence_per_trial.csv`
- `null-tests/results/base_independence_summary.csv`

See findings.md §12.4.
