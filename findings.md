# Findings: Verification and Null Testing of Digit Gaps Mod-6 v2.3

**Mr Code pass — April 13 2026**
**Paper:** Digit_Gaps_Mod6_v2_3.md (v2.3)
**Script:** `full_null_model.py` (extracted from v2.0 PDF appendix)

---

## 1. Reproduction Status

Every headline numerical claim in the paper reproduced to exact match against `full_null_model.py`. No discrepancies found.

| Claim | Paper | Reproduced | Status |
|---|---|---|---|
| 5-series count | 485,503 | 485,503 | REPRODUCED |
| 7-series count | 485,199 | 485,199 | REPRODUCED |
| Max digit-length | 3,254,959 | 3,254,959 | REPRODUCED |
| Spacings in {1,2,3} | 99.9998% | 99.9998% | REPRODUCED |
| Spacing exceptions | 3x5, 1x7, 1x23 | {5:3, 7:1, 23:1} | REPRODUCED |
| s=1/s=2/s=3 distribution | ~68:26:6 | 68.0:25.8:6.2 | REPRODUCED |
| Coincident gap % | 72.4% | 72.4% | REPRODUCED |
| Cluster count (200k) | 13 | 13 | REPRODUCED |
| Power-law beta | 0.637 +/- 0.029 | 0.6371 +/- 0.0293 | REPRODUCED |
| R-squared | 0.979 | 0.979 | REPRODUCED |
| Cluster z-score | -2.04 | -2.04 | REPRODUCED |
| Band-by-band Table 4 | 6 bands | All exact | REPRODUCED |
| Null model Table 5 | 6 metrics | All exact | REPRODUCED |
| Sensitivity Table 7 | 5 windows | All exact | REPRODUCED |
| Null beta range | 0.45-0.83 | 0.45-0.83 | REPRODUCED |

Runtime: 59.1s on test hardware (paper claims ~32s; hardware difference only).

Full details in `verification/reproduction_log.md`.

---

## 2. Phase-Transition Null Test (Section 4.2)

### Method

The paper observes that digit gaps transition from staggered (gaps at different digits in each series) to coincident (gaps at the same digits) as scale increases. Specifically: staggered at 10^61, coincident at 10^80.

We measured synchronisation fraction (proportion of gaps that are coincident) in sliding windows across the full digit range, for real primes and 10 null-model trials. We tested at four window sizes (100, 200, 500, 1000) and four synchronisation thresholds (0.80, 0.85, 0.90, 0.95). We also measured the stagger percentage at early scales (1-100, 1-500, 1-1000, 1-5000, 1-10000 digits).

### Null Distribution

All 10 null trials found transition points at every threshold tested. The transition from staggered to coincident is not unique to real primes -- pseudo-random sequences with PNT density also transition.

### Separation Statistic

| Window | Threshold | Real transition | Null mean | z-score |
|---|---|---|---|---|
| 100 | 0.80 | 4,551 | 14,806 | -1.24 |
| 100 | 0.85 | 4,551 | 17,386 | -1.38 |
| 200 | 0.80 | 9,101 | 29,201 | -1.40 |
| 200 | 0.90 | 36,601 | 77,221 | -0.78 |
| 500 | 0.90 | 126,851 | 214,001 | -0.57 |
| 1000 | 0.90 | 385,101 | 397,768 | -0.06 |

Real primes transition slightly earlier than null (most z-scores negative), but no z-score exceeds |2| and the effect is inconsistent across window sizes.

### Window Sensitivity

The transition point is highly sensitive to window size. At threshold 0.90: real primes transition at digit 15,451 (window=100), 36,601 (window=200), 126,851 (window=500), 385,101 (window=1000). A factor of 10x in window yields a factor of 25x in transition point. This is the classic Pattern 75 concern: the window is doing hidden work.

### Early-Scale Stagger

One finding of note: at the 1-500 digit band, real primes show 58.3% stagger vs null mean 47.3% (z = 6.37). Real primes are significantly more staggered at very small scales. This signal dissipates rapidly: z = 0.69 at 1-1000 and z = -0.36 at 1-10000.

### Verdict

**GENERIC.** The staggered-to-coincident phase transition is a property of logarithmic accumulation, not of prime distribution. All null trials show the same transition. Real primes transition slightly earlier but not significantly so. The window sensitivity means the specific transition digit reported depends heavily on measurement parameters.

**Recommended status for Section 4.2 in v2.4:** KEEP-AS-OBSERVATION with explicit reclassification as GENERIC. The specific digits (10^61, 10^80) in Theorems 1-2 remain proved by direct computation. The broader phenomenon -- that coincidence emerges with scale -- should be acknowledged as generic to logarithmic sequences, not prime-specific. The z = 6.37 early-stagger signal at 1-500 digits is a genuine curiosity but too localised (one band) and too sensitive to band boundaries to elevate.

---

## 3. JUMP/PAIR Null Test (Section 5.3)

### Method

The paper observes that consecutive inter-cluster gap ratios alternate between JUMPs (ratio > 1.5) and PAIRs (ratio near 1.0), with 44% of ratios being pairs and specific examples like (17,972 / 17,861) ratio 0.99.

We computed inter-cluster gaps and their consecutive ratios for real primes at two scales (200k as in the paper, and full 3.25M digits) and for 20 null-model trials at full scale. We tested sensitivity to pair-threshold width ([0.90, 1.10] through [0.99, 1.01]).

### The Small-Sample Problem

The paper's analysis at 200k digits uses 13 clusters, producing 12 gaps and 11 ratios. At this scale, 45.5% of ratios (5/11) are pairs and 50% (5/10) show JUMP-PAIR alternation -- consistent with the paper's 44% claim.

At full scale (3.25M digits, 48 clusters, 46 ratios), pair fraction drops to 17.4% and alternation to 22.2%. The pattern does not persist at scale.

### Null Distribution

| Pair range | Real pair% | Null mean% | Null std% | z(pair) |
|---|---|---|---|---|
| [0.90, 1.10] | 17.4% | 39.4% | 13.6% | -1.62 |
| [0.95, 1.05] | 8.7% | 22.4% | 9.0% | -1.52 |
| [0.97, 1.03] | 8.7% | 13.3% | 6.9% | -0.67 |
| [0.99, 1.01] | 6.5% | 4.2% | 3.1% | +0.75 |

Real primes have FEWER near-unity ratios than null at all but the tightest threshold. This is the opposite direction from the paper's observation.

### Ratio Distribution

The ratio distributions are qualitatively different. Real primes show a bimodal distribution: 21.7% of ratios below 0.5, 23.9% above 2.0, only 17.4% in [0.9, 1.1]. The null model clusters around unity: 42.1% in [0.9, 1.1], with much less weight in the tails.

This reflects the structural difference already documented in Section 6.2: real primes have fewer, larger clusters, so inter-cluster gaps are more variable. The "heartbeat" is not an additional phenomenon -- it is the same cluster-count disparity (z = -2.04) viewed through a different lens.

### Alternation Signal at Tight Thresholds

At very tight pair thresholds ([0.97, 1.03] and tighter), real primes show higher alternation fraction than null (z = 2.52 at [0.97, 1.03], z = 3.47 at [0.99, 1.01]). However, these z-scores come from tiny counts: 4 alternations out of 45 ratios vs null mean of 1.3. With only 48 clusters, the statistical power is too low to draw conclusions from counts this small.

### Sensitivity

The pair fraction is steeply sensitive to threshold width: from 17.4% at [0.90, 1.10] to 6.5% at [0.99, 1.01]. This is the Pattern 75 concern. The paper's 44% was measured at 200k scale with a de facto wide window (ratios of 0.97 and 0.94 both counted as "pairs"). The effect collapses at tighter thresholds and at larger scales.

### Verdict

**DEMOTE.** The JUMP/PAIR heartbeat at 200k scale is a small-sample artefact from 11 ratios that does not survive extension to full scale. At full scale, real primes show fewer near-unity ratios than null, not more. The paper's own pareidolia warning (Section 5.3) was correct and should be acted on.

**Recommended status for Section 5.3 in v2.4:** DEMOTE from "observation pending null test" to "acknowledged small-sample artefact that does not survive full-scale null testing." The tight-threshold alternation signal (z = 2.52-3.47) is suggestive but rests on counts too small for any claim. If this is mentioned at all in v2.4, it should be with full disclosure of the sample sizes and the reversal of direction at wider thresholds.

---

## 4. Honest Flags

### Things a careful reviewer would notice

1. **The power-law fit uses 12 points.** Beta = 0.637, R^2 = 0.979 from 12 (gap, centre) pairs at 200k scale. At full scale (47 gaps), the fit should be rechecked -- the extremely variable gaps at large scales (ratios from 0.02 to 198) may degrade R^2 considerably. The paper's cluster analysis is scoped to 200,000 digits; this is disclosed but a reviewer may ask whether the power law holds at full scale.

2. **Null model seeds are deterministic.** Seeds = trial * 137 + 42. This is disclosed and standard practice. A reviewer may request verification with different seed schemes. We used the same seeds throughout for reproducibility.

3. **The v2.0 PDF script and v2.3 paper.** The verification script is from the v2.0 PDF. Versions 2.1-2.3 changed prose and citations only, not mathematics. This is internally consistent but a reviewer may want the script to carry a version note.

4. **Runtime 59s vs claimed 32s.** Hardware-dependent. Not a concern for correctness, but the README should qualify "approximately 32 seconds on the original test hardware."

5. **The z = 6.37 early-stagger signal.** This was not reported in the paper. It is localised to one band (1-500 digits) and the z-score is sensitive to band boundaries. It may warrant a footnote in v2.4, presented honestly as a post-hoc observation.

### Things I could not verify

- Theorems 1 and 2 (specific gap locations at 10^61 and 10^80 scales) are proved by direct computation in the paper, not by the verification script. The script verifies the large-scale statistical claims. Verifying the small-scale theorems would require a separate computation using exact integer arithmetic (mpmath or similar). This is straightforward but was not in scope for this pass.

- The mod-30 classification (Table 8) is algebraic and does not require numerical verification.

---

## 5. Recommended Changes for v2.4

1. **Section 4.2 (Phase Transition):** Add a note that the staggered-to-coincident transition is generic to logarithmic sequences, not prime-specific. The specific examples at 10^61 and 10^80 (Theorems 1-2) remain valid as proved computations. The "Status note" after Table 3 already partially addresses this via the cluster z-score reference; a sentence acknowledging the null-test result would complete it.

2. **Section 5.3 (JUMP/PAIR):** Demote from "observation pending null test" to "observation that did not survive null testing." The paper already carries a pareidolia warning; the recommended edit is to move this section from "pending" to "tested and not confirmed." Full disclosure: at the paper's 200k scale with 11 ratios, the pattern is visually present but statistically empty; at full scale it reverses direction. The tight-threshold alternation signal (z = 2.52-3.47) can be mentioned as a residual curiosity with explicit sample-size caveats.

3. **Table 9 (Summary):** Update JUMP/PAIR row from "Observed, null-test pending" to "Tested, not confirmed (small-sample artefact)." Update Phase Transition row to note generic status.

4. **Section 10 (Computational Verification):** Add version note that the script is from v2.0; v2.1-2.3 changes were prose/citation only.

5. **Open Question 3:** Can be closed. The JUMP/PAIR heartbeat is not prime-specific.

6. **Minor:** README runtime claim of "32 seconds" should add "on original test hardware" qualifier.

---

## 6. Power-Law Fit at Full Scale (follow-up pass, April 13 2026)

### Method

Same log-log OLS regression as paper Section 5.2: log(gap) regressed on log(centre), where gap is the distance between consecutive synchronisation-cluster centres. Fitted at 200k (paper's scale, 13 clusters, 12 data points) and at full 3.25M-digit scale (48 clusters, 47 data points). Null model: 20 pseudo-prime trials at full scale with same cluster-detection parameters.

### Results

| Scale | n | beta | se(beta) | R-squared | alpha |
|---|---|---|---|---|---|
| 200k (paper) | 12 | 0.6371 | 0.0293 | 0.9792 | 15.85 |
| Full 3.25M (real) | 47 | 0.3906 | 0.1076 | 0.2264 | 185.75 |
| Full 3.25M (null mean) | — | 0.3871 | 0.0872 | 0.3068 | — |
| ln(2)/ln(3) | — | 0.6309 | — | — | — |

z-scores (real vs null at full scale): z(beta) = 0.04, z(R-squared) = -0.51.

### What happened

The first 12 cluster gaps (up to digit ~200k) follow an exceptionally clean power law. Beyond 200k, the inter-cluster gaps become wildly variable — ranging from 860 to 244,795 at the same scale — and the power-law relationship collapses. Residuals at full scale are an order of magnitude larger than the fit: predicted gaps of ~60k alongside actual gaps from 860 to 244,795.

The full-scale fit is statistically indistinguishable from null: beta = 0.391 (real) vs 0.387 (null mean), z = 0.04. The null model achieves comparable or better R-squared (0.307 vs 0.226). The clean power law at 200k is not a general property of primes at all scales.

### Sensitivity

| Trim | n | beta | se(beta) | R-squared |
|---|---|---|---|---|
| No trim | 47 | 0.3906 | 0.1076 | 0.2264 |
| Drop first 2 | 45 | 0.3321 | 0.1352 | 0.1230 |
| Drop last 2 | 45 | 0.4060 | 0.1079 | 0.2478 |
| Drop first 5 | 42 | 0.2631 | 0.1830 | 0.0491 |
| Drop last 5 | 42 | 0.4761 | 0.0979 | 0.3718 |
| Drop first 5 + last 5 | 37 | 0.4191 | 0.1744 | 0.1416 |

Beta ranges from 0.26 to 0.48 depending on trim. No trim choice recovers the 200k-scale exponent or R-squared. The best R-squared from any trim (0.372, dropping last 5) is still far below the paper's 0.979. The fit is not steeply sensitive to trim — it is uniformly poor. This is Pattern 75 compliant: no trim choice is being cherry-picked; none of them work.

### Verdict

**DEGRADES.** The power-law beta = 0.637 (R-squared = 0.979) is a real and robust property of the first 200,000 digits. It does not extend to 3.25 million digits. At full scale, the fit collapses (R-squared = 0.226) and becomes indistinguishable from the null model (z = 0.04).

Classification:
- beta = 0.637 at 200k scale: **OBSERVED** (real, robust, scoped to 200k, prime-specific at that scale per existing z = -2.04 cluster count)
- beta at full scale: **NULL-INDISTINGUISHABLE** (no prime-specific structure in the power-law exponent beyond 200k)
- beta approximately equals ln(2)/ln(3): **OPEN QUESTION, now weakened** (the coincidence holds at 200k; the full-scale exponent is 0.39, nowhere near 0.631)

### Recommended edit to Section 5.2 for v2.4

The paper currently states: "The gap between consecutive cluster centres follows a power law: gap approximately equals 18.2 times centre^beta with beta = 0.637 +/- 0.029 and R-squared = 0.979 (first 200,000 digits; see Section 6 for robustness)."

The qualification "(first 200,000 digits)" is already present and accurate. Recommended addition for v2.4: a sentence noting that the power law does not extend beyond 200k digits. At full scale (3.25M digits), the inter-cluster gaps become highly variable and the fit degrades to R-squared = 0.23, indistinguishable from the null model. The beta approximately equals ln(2)/ln(3) coincidence should be noted as holding only at the 200k scale.

Open Question 1 ("Does beta converge to ln(2)/ln(3) exactly?") should be updated to note that the question is now less well-posed: the exponent is not stable across scales, so convergence in the usual sense may not apply.

---

*Mr Code, April 13 2026 (updated with Section 6, same date)*
