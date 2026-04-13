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
