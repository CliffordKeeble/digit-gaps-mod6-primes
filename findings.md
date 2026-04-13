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

## 7. Adversary Follow-up Tests (April 13 2026, evening)

Three tests requested by Mr Adversary's review of v2.4, addressing gaps in the empirical evidence behind the paper's headline claims.

### 7.1 JUMP/PAIR Null at 200k Scale (Task 1)

**The gap.** The previous JUMP/PAIR test (Section 3 above) ran at full scale (46 ratios, 20 trials) and called the observation a "small-sample artefact." But the original observation was at 200k scale (11 ratios from 13 clusters). Mr Adversary correctly noted we had not tested whether 11-ratio null trials at 200k routinely produce similar pair fractions.

**Method.** 50 null-model trials at 200k scale. Same cluster parameters (window=50, min_gaps=20, merge_dist=500). Pair fraction and alternation fraction at four thresholds.

**Important threshold note.** The paper's "44%" pair fraction and the previous pass's "45.5%" were computed at a pair threshold of [0.85, 1.15]. This test, per CinC's brief, uses [0.90, 1.10] as the widest threshold. At [0.90, 1.10], real primes show 27.3% (3/11 ratios), not 45.5%. The two numbers are not comparable without noting the threshold difference.

**Results.**

| Pair range | Real pair% | Null mean% | Null std% | z(pair) | Real alt% | Null alt mean% | z(alt) |
|---|---|---|---|---|---|---|---|
| [0.90, 1.10] | 27.3% | 27.6% | 14.1% | -0.02 | 30.0% | 10.2% | 2.22 |
| [0.95, 1.05] | 18.2% | 13.5% | 9.1% | 0.51 | 30.0% | 4.7% | 4.75 |
| [0.97, 1.03] | 18.2% | 8.0% | 6.3% | 1.63 | 30.0% | 2.6% | 7.28 |
| [0.99, 1.01] | 9.1% | 2.6% | 3.6% | 1.81 | 10.0% | 1.1% | 4.31 |

Null pair-fraction distribution at [0.90, 1.10]: median 27.8%, range [6.2%, 72.5%]. 50% of null trials equal or exceed the real-prime pair fraction.

**Interpretation.** The pair fraction at 200k is dead centre of the null distribution (z = -0.02). The previous pass's "artefact" framing is confirmed for the pair fraction itself.

However, the *alternation* fraction — JUMP followed by PAIR or vice versa — is significantly above null at every threshold tested (z = 2.22 to 7.28). Real primes show 30% alternation at [0.90, 1.10] vs null's 10%. The sequential *ordering* of gap ratios is prime-specific at 200k, even though the individual pair fraction is generic.

**Caveat.** The alternation z-scores are high but come from small counts (3 alternations in 10 consecutive-ratio pairs, vs null mean ~2.6). With 11 ratios, a single ratio shifting classification can change the count substantially. The z-scores are computed from the distribution of alternation fractions across 50 null trials, which properly accounts for the variance — but the underlying counts are still small. This signal warrants cautious reporting, not a strong claim.

**Verdict.** The pair-fraction observation is NULL-INDISTINGUISHABLE at 200k (z = -0.02). The alternation pattern is PRIME-SPECIFIC at 200k (z = 2.22+), but from small counts. The Section 3 demotion was correct for pair fraction; the alternation signal is a new finding that Section 5.3 did not originally distinguish from the pair-fraction claim.

**Recommended status for v2.5:** Pair fraction → confirmed generic. Alternation at 200k → cautious observation, prime-specific but small-sample.

### 7.2 Cluster Count at 100 Trials (Task 2)

**The gap.** The headline z = -2.04 came from 10 null trials. With only 10 trials, the std estimate is noisy and z barely clears |2|.

**Method.** 100 null-model trials at 200k scale, same cluster detection parameters as published.

**Results.**

| Metric | Real | Null mean | Null std | z-score |
|---|---|---|---|---|
| Cluster count | 13 | 28.12 | 11.02 | -1.37 |

Null distribution: min 7, Q1 21, median 25, Q3 33, max 60.
Null trials with count <= 13: 4/100 (empirical p = 0.04, one-tailed).

**The paper's z = -2.04 with 10 trials used null mean 29.2 and null std 7.9.** At 100 trials the null mean is similar (28.12) but the std is substantially larger (11.02 vs 7.9), pulling z below 2. The 10-trial std was an underestimate.

**Interpretation.** The cluster-count separation weakens from z = -2.04 to z = -1.37. This is below the |z| > 2 threshold the paper uses elsewhere. However, the empirical p-value (4%) is still noteworthy — only 4 of 100 null trials produce 13 or fewer clusters. The result is at the edge of conventional significance (p = 0.04 one-tailed), not noise, but not as clean as z = -2.04 implied.

**Verdict.** The headline z = -2.04 was inflated by an underestimated null std from 10 trials. At 100 trials: z = -1.37, empirical p = 0.04. MARGINAL — the claim that real primes produce "fewer clusters" is directionally correct and the empirical p-value is suggestive, but z no longer clears |2|. The paper should not call this "the surviving headline statistical result" without the 100-trial caveat.

**Recommended status for v2.5:** Revise z-score to -1.37 (100 trials), report empirical p = 0.04, soften language from "prime-specific" to "suggestive of prime-specific structure at marginal significance."

### 7.3 Null R-squared Distribution at 200k (Task 3)

**The gap.** The paper says null produces "no comparable clean fit" and writes "(scattered)" in the R² cell. Mr Adversary noted we never quoted a number.

**Method.** From the 100-trial run, extract power-law R² for each null trial producing >= 4 clusters.

**Results.**

| Metric | Real | Null mean | Null std | z-score |
|---|---|---|---|---|
| R-squared | 0.9792 | 0.5767 | 0.1833 | +2.20 |
| Beta | 0.6371 | 0.5395 | 0.1852 | +0.53 |

Null R² distribution: min 0.016, Q1 0.499, median 0.615, Q3 0.703, max 0.856.
**Zero null trials out of 100 reach R² >= 0.979.** The maximum null R² is 0.856.

**Interpretation.** The R² is the strongest surviving prime-specific result. z = +2.20 clears the |z| > 2 threshold. The empirical p-value is < 1/100 (none of 100 trials reach the real value). The exponent beta is null-indistinguishable (z = 0.53, confirming the paper's existing +0.34) — but the *cleanness* of the fit (R²) is genuinely prime-specific.

This means: random pseudo-primes at 200k produce cluster-spacing patterns with similar *slope* but much more *scatter* than real primes. The structural order is in the regularity of cluster spacing, not in the exponent itself.

**Verdict.** R² = 0.979 is **PRIME-SPECIFIC** (z = +2.20, 0/100 null trials reach it). This is the cleanest statistical claim in the paper and should be promoted as such in v2.5.

### 7.4 Revised Picture of Prime-Specific Structure

After the adversary follow-up, the paper's prime-specific claims rank as follows:

| Claim | z-score | Empirical p | Status |
|---|---|---|---|
| R² = 0.979 at 200k | +2.20 | < 1% | PRIME-SPECIFIC |
| Cluster count = 13 at 200k | -1.37 | 4% | MARGINAL |
| JUMP/PAIR alternation at 200k | +2.22 to +7.28 | — | CAUTIOUS (small counts) |
| Beta = 0.637 at 200k | +0.53 | — | NULL-INDISTINGUISHABLE |
| JUMP/PAIR pair fraction at 200k | -0.02 | 50% | NULL-INDISTINGUISHABLE |
| All spacing statistics | ~0 | — | GENERIC |
| Phase transition | ~0 | — | GENERIC |
| Power law at full scale | +0.04 | — | NULL-INDISTINGUISHABLE |

The R-squared cleanness is the load-bearing prime-specific result. The cluster count is supportive but marginal. Everything else is either generic or null-indistinguishable.

---

## 8. Paper A (First Boundary) Verification Pass (April 13 2026, evening)

Five tasks for the in-depth structural analysis of the first digital boundary (Paper A v3.0). High-precision verification of the existing theorems plus the new chi5 regime analysis and three robustness tests.

### 8.1 High-Precision Verification of Theorems 1-6

All six theorems verified at 200-digit mpmath precision with cross-check (len(str(prod)) vs floor(log10(prod)) + 1).

| Theorem | Product | Digits (str) | Digits (log10) | mod 3 | mod 5 | Status |
|---|---|---|---|---|---|---|
| 1 (5-series gap 60-61) | Pi_5(30) | 59 | 59 | 1 | 0 | VERIFIED |
| 1 (continued) | Pi_5(31) | 62 | 62 | — | — | gap at 60, 61 |
| 2 (7-series gap 62-63) | Pi_7(30) | 61 | 61 | 1 | 3 | VERIFIED |
| 2 (continued) | Pi_7(31) | 64 | 64 | — | — | gap at 62, 63 |
| 3 (factor 3 at 10^61) | Pi_5(30) mod 3 = 1 | — | — | 1 | — | VERIFIED |
| 4 (coincident 80-81) | Pi_5(38)=79d, Pi_5(39)=82d | — | — | — | — | VERIFIED |
| 4 (continued) | Pi_7(37)=79d, Pi_7(38)=82d | — | — | — | — | VERIFIED |
| 5 (factor 3 at 10^80) | Pi_5(38) mod 3 = 1 | — | — | 1 | 0 | VERIFIED |
| 6 (factor 15 at 10^80) | Pi_7(37) mod 3 = 1, mod 5 = 2 | — | — | 1 | 2 | VERIFIED |

Additional data for draft Section 7:
- 5-series first 30 primes: 14 split, 15 inert, 1 ramified (p=5)
- 7-series first 30 primes: 13 split, 17 inert, 0 ramified
- Pi_7(30) mod 5 = 3

Pi_5(30) = 72251183559254646712892154220296432236377519679774785052215 (59 digits).
ln Pi_5(30) = 135.52749900896194... (verified to 200-digit precision).

### 8.2 Chi5 Regime Analysis

**Placeholder values for draft (all confirmed against CinC's preliminary numbers):**

| Placeholder | Value |
|---|---|
| [LIMIT] | 5000 |
| [N_TIES_5] | 327 |
| [N_TIES_7] | 2 |
| [EXPECTED_TIES] | 56.4 |
| [RATIO_5] | 5.8 |
| [RATIO_7] | 28.2 |
| [MAX_S_IN_FIRST_DESERT] | 4 (gap n=43 to n=61) |

**Observation 6.1 confirmed.** S5(n) in [-2, +2] for n=1..33. 14 ties in this range (42.4% density). Ties at n = {1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 27, 31, 33}.

**Observation 6.2 confirmed.** First tie-desert (gap >= 8): n=33 to n=41 (8-step gap, max |S| = 3). First tie-desert (gap >= 10): n=43 to n=61 (18-step gap, max |S| = 4). Tie density in n=34..66: 5/33 = 15.2%.

**Observation 6.3 confirmed.** At n=31 (crossing the first digital boundary), S5(31) = 0 (a tie). The tight-oscillation regime ends between n=33 and n=43.

**Observation 6.4 confirmed.** 7-series ties occur at exactly n=4 (p=31) and n=26 (p=271). S7 does not return to zero after n=26 within the first 5000 primes. S7 range: [0, -43]. S7(5000) = -30.

**Observation 6.5 confirmed.** 5-series: 327 ties, 5.8x more than expected. 7-series: 2 ties, 28.2x fewer than expected. Opposite directions confirmed.

### 8.3 Perturbation Test 1: Shuffle

**Question:** Is the 14-tie tight oscillation in the first 33 positions about the natural prime ordering, or about the set of primes?

**Result: NATURAL ORDER IS ANOMALOUS.** z = 3.42, empirical p = 0.001.

| Metric | Natural order | Shuffle mean | Shuffle std | z-score |
|---|---|---|---|---|
| Ties in n=1..33 | 14 | 3.94 | 2.95 | 3.42 |
| Ties in n=34..66 | 5 | 3.90 | 2.90 | 0.38 |

Only 1 in 1000 random shuffles produce >= 14 ties in the first 33 positions. The tight-oscillation regime is about the *specific ordering by prime size*: the smallest 5-series primes happen to alternate split/inert with unusual regularity. This is the stronger of the two possible outcomes — the ordering matters, not just the composition.

The n=34..66 window (5 ties) is unremarkable (z = 0.38), consistent with the regime-change interpretation: the anomalous balance is specific to the first ~33 primes, not a persistent feature of the set.

**Status:** OBSERVED, prime-ordering-specific. The tight-oscillation regime is a real feature of the natural prime ordering, not a generic property of any arrangement of these primes.

### 8.4 Perturbation Test 2: Comparable Residue Classes

**Question:** Is the opposite-direction Chebyshev deviation specific to mod-6 filtering?

**Result: NOT MOD-6 SPECIFIC.** The pattern is systematic across all filterings tested.

| Class | N ties (of 5000) | Ratio | Direction |
|---|---|---|---|
| mod4=1 | 2 | 28.2 | FEWER |
| mod4=3 | 189 | 3.3 | MORE |
| mod8=1 | 3 | 18.8 | FEWER |
| mod8=3 | 216 | 3.8 | MORE |
| mod8=5 | 204 | 3.6 | MORE |
| mod8=7 | 255 | 4.5 | MORE |
| mod12=1 | 2 | 28.2 | FEWER |
| mod12=5 | 272 | 4.8 | MORE |
| mod12=7 | 266 | 4.7 | MORE |
| mod12=11 | 152 | 2.7 | MORE |
| mod6=5 (5-series) | 327 | 5.8 | MORE |
| mod6=1 (7-series) | 2 | 28.2 | FEWER |

The discriminating feature is **p === 1 (mod q)**: classes where p === 1 show extreme tie deficit (2-3 ties, ~28x fewer than expected). All other classes show tie surplus (2.7-5.8x more). The 7-series (p === 1 mod 6) is a specific instance of a general phenomenon.

**Why p === 1 classes are different.** Primes p === 1 (mod q) are precisely the primes that split completely in the cyclotomic field Q(zeta_q). The Legendre symbol chi5 applied to these primes has a systematic inert bias (more p === 2, 3 (mod 5) than p === 1, 4 (mod 5) among small primes p === 1 (mod q)), producing persistent negative drift in the running sum. This connects to Chebyshev's bias in the standard sense: among small primes in a given residue class, quadratic non-residues are overrepresented.

**Status:** OBSERVED, not mod-6 specific. The draft's Section 6.4 should be reframed: the opposite-direction deviations are a feature of the p === 1 (mod q) vs p !== 1 partition, not uniquely of mod-6. This weakens the claim that mod-6 filtering reveals special structure but strengthens the connection to known Chebyshev-bias phenomena.

### 8.5 Perturbation Test 3: Higher-Scale Tie Density

**Question:** Does 5-series tie density drop like 1/sqrt(n) or stabilise?

**Result: SLOWER THAN RANDOM WALK, BUT STILL DECAYING.**

Observed decay exponent: -0.263 (vs random-walk -0.500). R-squared of power-law fit: 0.066 (very poor — the decay is noisy, not clean power-law).

Cumulative ratio (observed/expected) at key scales:

| N | Observed ties | Expected (random walk) | Ratio |
|---|---|---|---|
| 100 | 29 | 8.0 | 3.63 |
| 500 | 72 | 17.8 | 4.04 |
| 1000 | 141 | 25.2 | 5.59 |
| 5000 | 327 | 56.4 | 5.80 |
| 10000 | 437 | 79.8 | 5.48 |
| 20000 | 683 | 112.8 | 6.05 |
| 50000 | 921 | 178.4 | 5.16 |

The ratio is remarkably stable at 5-6x across four orders of magnitude (N = 100 to 50000). The 5-series is not converging to random-walk behaviour — it has a persistent systematic tie-generation excess that scales with sqrt(N) (i.e., the excess tie count grows as sqrt(N), same as the expected count, maintaining the ~5.5x ratio).

The tie density within windows is highly variable (0% to 14% in successive 500-prime windows), consistent with a process that generates tie-rich and tie-desert patches rather than smooth decay. The R-squared of 0.066 for any simple decay model reflects this patchiness.

**Status:** OBSERVED. The 5-series tie excess is not a finite-scale transient — it persists at 50,000 primes with a stable ~5-6x ratio over expected. This is consistent with a systematic mechanism (not random walk) but the mechanism is not identified. The draft's Section 6 should note this persistence.

### 8.6 Corrections to CinC's Preliminary Numbers

CinC's preliminary numbers were all correct:
- 5-series: 327 ties, ratio 5.8x MORE -- confirmed exactly
- 7-series: 2 ties, ratio 28.2x FEWER -- confirmed exactly
- Tight oscillation n=1..33: 14 ties in [-2, +2] -- confirmed exactly
- First desert (gap >= 10): n=43 to n=61 -- confirmed exactly

No corrections needed.

### 8.7 Flag for CinC

**The comparable-moduli result (Task 4) materially affects the paper's framing.** The draft's Section 6.4 presents the opposite-direction Chebyshev deviation as potentially specific to mod-6 filtering ("We have not located this observation in the standard Chebyshev-bias literature... the double filtering may place the phenomenon outside the scope of work primarily concerned with primes unfiltered or filtered by a single modulus"). The comparable-moduli test shows the pattern is general: every p === 1 (mod q) class shows extreme tie deficit. This means:

1. The observation is real but not special to mod-6.
2. Open Question 2 in Section 9 ("Why do the 5-series and 7-series deviate in opposite directions? Is this a feature of the double-filtering mod-6 -> mod-5?") can be partially answered: the deviation is a feature of p === 1 classes generally, likely connected to Chebyshev's bias.
3. The draft's framing should be adjusted from "we have not located this" to "this is consistent with known Chebyshev-bias phenomena applied to residue-class-restricted sequences."

The shuffle result (Task 3) is the genuinely surprising finding: the natural ordering produces an anomalous tight-oscillation pattern (z = 3.42) that random arrangements of the same primes do not. This is the novel structural observation that Section 6 should foreground.

---

*Mr Code, April 13 2026 (updated with Section 8)*
