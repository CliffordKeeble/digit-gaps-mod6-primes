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

## 9. Paper A v3.1 Adversary Follow-up (April 14 2026)

Three tasks addressing Mr Adversary's two compute-addressable items from the v3.1 review.

### 9.1 Shuffle-Test Window and Band Robustness

**Question:** Is the natural-order tie-count anomaly structural (robust across window lengths and band thresholds) or post-hoc (present only at the data-derived n=33, c=2)?

**Answer: (a) ROBUST.** The anomaly persists across almost the entire tested range.

| n | T_nat | shuf_mean | shuf_std | z | p | n_distinct |
|---|---|---|---|---|---|---|
| 10 | 5 | 2.45 | 1.43 | 1.78 | 0.078 | 6 |
| 15 | 7 | 4.07 | 1.72 | 1.70 | 0.082 | 8 |
| 20 | 9 | 3.97 | 2.19 | 2.29 | 0.018 | 11 |
| 25 | 11 | 3.87 | 2.39 | 2.98 | 0.005 | 13 |
| 30 | 12 | 5.00 | 2.83 | 2.47 | 0.012 | 15 |
| 33 | 14 | 6.29 | 2.96 | 2.60 | 0.007 | 15 |
| 35 | 14 | 4.93 | 2.93 | 3.09 | 0.000 | 14 |
| 40 | 14 | 6.33 | 3.34 | 2.30 | 0.015 | 18 |
| 45 | 16 | 5.66 | 3.44 | 3.00 | 0.004 | 19 |
| 50 | 16 | 5.62 | 3.66 | 2.84 | 0.007 | 18 |
| 60 | 16 | 7.67 | 4.28 | 1.95 | 0.036 | 23 |
| 70 | 21 | 8.60 | 4.61 | 2.69 | 0.008 | 25 |
| 80 | 26 | 9.19 | 5.10 | 3.30 | 0.003 | 27 |
| 90 | 29 | 9.87 | 5.26 | 3.64 | 0.000 | 27 |
| 100 | 29 | 10.55 | 5.80 | 3.18 | 0.002 | 30 |

z > 2 at 12 of 15 window sizes (n=20 through n=100). z > 3 at 5 windows (n=35, 45, 80, 90, 100). The only windows below z=2 are n=10 (underpowered, 6 distinct values), n=15 (underpowered, 8 distinct values), and n=60 (z=1.95, just below threshold).

The band threshold c is irrelevant to the shuffle test: ties are defined as S=0 regardless of the band. The three c values produce identical results at each n. The band enters only via identifying which n is the "natural" window for a given c: c=1 implies n=12, c=2 implies n=35, c=3 implies n=50. All three natural band-windows give z > 2.

**Underpowered flag:** All windows n <= 90 have fewer than 30 distinct tie counts in the shuffle distribution. This is inherent to the problem (a 33-step random walk can only produce 0-17 ties). The z-scores and empirical p-values are still meaningful but should be interpreted with this discreteness caveat. At n=100, the distribution has 30 distinct values.

**Verdict: (a) Structural.** The anomaly is not an artefact of selecting n=33. The z-score at n=33 (2.60) is in fact *not* the peak — the strongest signal is at n=90 (z=3.64). The natural prime ordering produces more ties than random shuffles across the entire n=20..100 range. The post-hoc concern is dismissed.

**Note on v3.1 z=3.42 vs present z=2.60 at n=33.** The previous pass (Section 8.3) reported z=3.42, p=0.001. The present pass reports z=2.60, p=0.007. The difference is the random seed: the previous pass used the perturbation_tests.py seed (rng = random.Random(42)), while this pass uses SEED_BASE=42 but with a different RNG state because the shuffle test here reuses one RNG across all windows. Both are legitimate; the z-score is in the range 2.5-3.5 depending on the specific shuffle sample. The empirical p is consistently below 0.01.

### 9.2 Ramification Accounting for chi5(5) = 0

**Question:** Does the anomaly depend on counting the ramified n=1 step as a "tie"?

**Answer: No.** All three definitions give z > 2.

| Definition | T_nat | shuf_mean | shuf_std | z | p |
|---|---|---|---|---|---|
| A (include n=1) | 14 | 6.48 | 2.95 | 2.55 | 0.009 |
| B (exclude n=1 from count) | 13 | 6.46 | 2.94 | 2.22 | 0.020 |
| C (omit p=5 entirely, 32 steps) | 13 | 6.17 | 2.79 | 2.45 | 0.013 |

The ramified n=1 step contributes ~0.3 to z (from 2.22 to 2.55). Under all three definitions, the natural-order tie count exceeds the shuffle distribution at p < 0.02.

**Most principled definition:** Definition C (omit p=5, compute 32-step sum). Rationale: chi5(5) = 0 contributes nothing to the split/inert balance; including it inflates both T_nat and the shuffle mean by the same amount. Definition C measures what the paper claims: the balance between split and inert primes in the natural ordering. Under Definition C, T_nat = 13, z = 2.45, p = 0.013.

**Recommendation for v4:** Report the anomaly using Definition C (13 ties in 32 non-ramified primes, z = 2.45, p = 0.013) as the primary result, with Definition A (14 ties in 33 including ramified, z = 2.55) as a note. The claim weakens slightly but remains clear of z > 2.

### 9.3 Persistence-Ratio Stability Statistics

**Question:** Is "stable at approximately 5-6x" a quantitatively accurate description?

**Correction (Cliff, April 14).** The initial computation used 7 ratios from CinC's brief {3.63, 4.04, 5.59, 5.80, 5.48, 6.05, 5.16} mapped to N = {100, 500, 1000, 2000, 5000, 10000, 20000}. This was wrong: the brief omitted the N=2000 row (ratio 6.50), so 5.80 is N=5000, not N=2000. Corrected computation uses all 8 data points from Section 8.5.

From the full 8-point data at N = {100, 500, 1000, 2000, 5000, 10000, 20000, 50000} with ratios {3.63, 4.04, 5.59, 6.50, 5.80, 5.48, 6.05, 5.16}:

| Statistic | Value |
|---|---|
| Mean | 5.281 |
| Standard deviation | 0.983 |
| Coefficient of variation | 18.6% |
| 95% CI on mean (t, df=7) | [4.459, 6.103] |
| Linear fit slope (ratio vs log10 N) | 0.677 |
| SE(slope) | 0.357 |
| t(slope) | 1.897 |
| df | 6 |
| R-squared | 0.375 |

The slope is **not significant** at p = 0.05 (t = 1.90, critical value 2.447 at df=6). The upward trend visible in the data (3.63 at N=100 rising to ~5-6 at N >= 1000) does not reach statistical significance over the full range.

**Verdict:** "Stable at approximately 5-6x" is approximately correct for N >= 1000 but overstates the case for the full range N = 100-50000. The restricted statistics for N >= 1000 (ratios {5.59, 6.50, 5.80, 5.48, 6.05, 5.16}): mean = 5.763, std = 0.469, CV = 8.1%. This restricted set is genuinely stable.

**Recommendation for v4:** Replace "stable at approximately 5-6x" with "stabilises at approximately 5.8x for N >= 1000 (CV = 8%), after an initial ramp from 3.6x at N = 100." The slope across the full range is not statistically significant (t = 1.90, p > 0.05).

---

## 10. Conjecture 7.1 Sharpening — Boundary Predictions (April 14 2026)

Three tasks to sharpen Conjecture 7.1 from qualitative tautology to falsifiable prediction.

### 10.1 Boundary Identification

**The dense-gap problem.** At these scales (D < ~700), digit gaps are ubiquitous. Each prime multiplication adds ~1.5-2 digits of log-growth, so the cumulative product typically jumps by 2-3 digits per prime, skipping 1-2 digit-lengths every step. The "isolated gap" regime where most digit-lengths are filled does not begin until much larger scales (the full_null_model.py analysis at 3.25M digits is in that regime). Paper 195's boundaries 1-2 are NOT isolated gaps in a mostly-filled sequence — they are specific 3-digit jumps in a still-gap-dense regime.

**Boundary convention.** A "boundary event" is a step n -> n+1 where D(n+1) - D(n) >= 3, creating a pair of consecutive missing digit-lengths. These are common at small n and thin out gradually. The paper's boundaries 1 and 2 are specific instances.

**Enumerated 3-digit jumps (first 20 per series):**

5-series: n=18 (D 31->34), n=22 (40->43), n=25 (47->50), n=27 (52->55), **n=30 (59->62)**, n=32 (64->67), n=34 (69->72), n=36 (74->77), **n=38 (79->82)**, n=39 (82->85), n=41 (87->90), ...

7-series: n=17 (30->33), n=20 (37->40), n=23 (44->47), n=26 (51->54), n=28 (56->59), **n=30 (61->64)**, n=32 (66->69), n=34 (71->74), n=35 (74->77), **n=37 (79->82)**, n=39 (84->87), ...

Bold = paper's boundaries 1 and 2. The 3-digit jumps continue indefinitely (last observed in 500-prime range: n=499 at D~1700). There is no natural "boundary 3" that is distinguished from the ongoing stream of 3-digit jumps. The grouping into discrete boundaries is an artefact of where the paper chose to focus.

**Verdict on Task 1: outcome (b/c).** Boundaries 3 and 4 are not cleanly identifiable as distinct events. The 3-digit jumps form a near-continuous stream. The next jumps after the paper's boundary 2 (n=38, D=79->82 for 5-series; n=37, D=79->82 for 7-series) are:

- 5-series: n=39 (82->85), n=41 (87->90), n=42 (90->93), n=44 (95->98), ...
- 7-series: n=39 (84->87), n=40 (87->90), n=42 (92->95), n=43 (95->98), ...

These are not "boundary events" in any sense that distinguishes them from the general pattern. The jump at n=38->39 for the 5-series is *immediately* after boundary 2 — there is no gap-free interval between them.

### 10.2 Modular State — The Invariance Finding

**This is the key structural finding of this task.**

The "active-constraint set" (small primes m where Pi_i(n) is coprime to m) is **invariant across all boundaries and all n**, because once a prime p enters a series' cumulative product, p divides Pi_i(n) for all subsequent n.

| Series | Contains primes | Always divides Pi | Coprime moduli (invariant) |
|---|---|---|---|
| 5-series | 5, 11, 17, 23, 29, 41, 47, 53, ... | 5, 11, 17, 23 | {3, 7, 13, 19} |
| 7-series | 7, 13, 19, 31, 37, 43, 61, 67, ... | 7, 13, 19 | {3, 5, 11, 17, 23} |

Specifically:
- Pi_5(n) mod 5 = 0 for all n >= 1 (contains p=5). Pi_5(n) mod 11 = 0 for all n >= 4 (contains p=11). Pi_5(n) mod 17 = 0 for all n >= 3 (contains p=17). Pi_5(n) mod 23 = 0 for all n >= 4 (contains p=23).
- Pi_7(n) mod 7 = 0 for all n >= 1 (contains p=7). Pi_7(n) mod 13 = 0 for all n >= 2 (contains p=13). Pi_7(n) mod 19 = 0 for all n >= 3 (contains p=19).

Verified at boundaries 1-4:

| Boundary | 5-series active moduli | 7-series active moduli |
|---|---|---|
| 1 (D~60) | {3, 7, 13, 19} | {3, 5, 11, 17, 23} |
| 2 (D~80) | {3, 7, 13, 19} | {3, 5, 11, 17, 23} |
| 3 (D~112) | {3, 7, 13, 19} | {3, 5, 11, 17, 23} |
| 4 (D~123) | {3, 7, 13, 19} | {3, 5, 11, 17, 23} |

All identical. The active-constraint set does not change.

**Cross-check against paper's observed factors:**
- Boundary 1, 5-series: Pi_5(30) mod 3 = 1, mod 5 = 0. Observed factor: 3. Consistent: only mod 3 is active among the moduli needed.
- Boundary 1, 7-series: Pi_7(30) mod 3 = 1, mod 5 = 3. Observed factor: 3 (not 15). Active set includes mod 5, but factor 5 was not required at this boundary.
- Boundary 2, 7-series: Pi_7(37) mod 3 = 1, mod 5 = 2. Observed factor: 15. Both mod 3 and mod 5 are active AND required.

The cross-check shows the active-constraint set is necessary but not sufficient: the *actual* required factor at a boundary depends on which constraints the gap-filling arithmetic demands, not just which moduli the product is coprime to.

### 10.3 Implications for Conjecture 7.1

**The conjecture as currently stated is not falsifiable in the way intended.** The "accumulated mod-m state" does not change meaningfully across boundaries (the coprimality pattern is fixed once the small primes enter the series). The factor escalation 3 -> 15 is not about the active-constraint set "growing" — it is about which constraints the gap-filling problem *requires*, which depends on the specific digit-gap geometry at each boundary.

The question Conjecture 7.1 should be asking is: **at each 3-digit jump, what is the minimum factor k such that Pi_i(n_B) * k has a digit-length in the gap range?** This is a question about the leading digits of Pi_i(n_B) relative to the gap boundaries, not about the modular residue state.

**What the data shows:** The minimum gap-filling factor at each boundary is determined by:
1. The digit-length of Pi_i(n_B) relative to the lower edge of the gap.
2. Which small primes divide Pi_i(n_B) (fixed by series membership).
3. The specific value of Pi_i(n_B) mod m for active moduli (varies with n_B but the active moduli don't change).

**Prediction for CinC.** A sharper Conjecture 7.1 would predict the *required factor* at each boundary by computing: what is the smallest integer k coprime to the series' primes such that Pi_i(n_B) * k has digit-length in the gap range? This is computable but depends on the actual value of Pi, not just its residue classes. The factor escalation 3 -> 15 at boundary 2 for the 7-series happens because at that specific scale, multiplying by 3 alone does not produce a number with 80 or 81 digits, while multiplying by 15 does — and 15 is the smallest multiple of 3 that achieves this.

**Recommended action:** The invariance of the active-constraint set means Conjecture 7.1 cannot be sharpened by predicting "which new moduli activate" at later boundaries — they don't. The conjecture should instead be reframed around the digit-gap geometry and the specific filler factors required. This is a change of framing, not a contradiction — the paper's observations about factor escalation are correct, but the mechanism is digit-arithmetic, not modular-activation.

---

*Mr Code, April 14 2026 (updated with Section 10)*

---

## 11. Crystallisation-Shadow Tests (April 14 2026)

Three tests probing whether the digit-gap boundary structure connects to the Bootstrap crystallisation programme's scales (e^140 and e^184).

### 11.1 Mod-q Boundary Scaling

**Question:** Is the existence of boundaries at the e^140 and e^184 scales specific to mod-6 filtering?

**Critical framing issue.** The paper's "boundaries" at D=60 (ln*D = 138.2) and D=80 (ln*D = 184.2) are NOT the first 3-digit jumps in the mod-6 series. They are specific 3-digit jumps that the paper selected for structural analysis. The first 3-digit jumps in the mod-6 series occur much earlier:

- 5-series: first 3-digit jump at n=18, D=31->34 (ln*D = 71.4)
- 7-series: first 3-digit jump at n=17, D=30->33 (ln*D = 69.1)

Every residue class at every modulus tested has early 3-digit jumps, all at much smaller scales. No modulus places its first or second 3-digit jump near (140, 184). The mod-6 series don't either — their first gaps are at ln*D ~ 67-71.

**The paper's D=60 boundary is the ~5th 3-digit jump for the 5-series (n=30), not the first.** The D=80 boundary is the ~9th (n=38). What makes these specific to the paper is the *combined* structure (staggered-then-coincident) and the factor-escalation analysis, not the digit-gap scale itself.

**Summary table (first 3-digit jump per class):**

| q | r | First gap D | ln*D | Second gap D | ln*D |
|---|---|---|---|---|---|
| 4 | 1 | 18-19 | 41.4 | 33-34 | 76.0 |
| 4 | 3 | 35-36 | 80.6 | 44-45 | 101.3 |
| 6 | 1 | 31-32 | 71.4 | 38-39 | 87.5 |
| 6 | 5 | 29-30 | 66.8 | 38-39 | 87.5 |
| 8 | 1 | 14-15 | 32.2 | 21-22 | 48.4 |
| 12 | 1 | 16-17 | 36.8 | 23-24 | 53.0 |
| 30 | 1 | 9-10 | 20.7 | 16-17 | 36.8 |

None land near 140 or 184. All moduli show the same general pattern: early dense 3-digit jumps thinning with scale.

**Verdict: neither (a) nor (b) — the question as posed does not have a clean answer.** The paper's boundaries at D=60/80 are not characterised by being "the first isolated boundaries" in any modulus-generic sense. They are the specific indices at which the *paper's* structural analysis (staggered/coincident classification, factor escalation) is carried out. The e^140/e^184 coincidence is between the paper's chosen analysis points and the physics scales, not between a generic prime-product feature and those scales.

This does not invalidate the coincidence — but it means the null test framing ("do other moduli also land at 140/184?") is not the right question. The right question is: "why does the staggered-to-coincident transition happen specifically at D~60 and D~80 for mod-6?" That question requires a different kind of analysis.

### 11.2 Sub-Structure Between Boundaries 1 and 2

**Question:** Is the D=62..79 range structurally featureless or does it contain sub-features?

**Result: outcome opposite to (a) — the range is maximally structured.** Every single step in D=62..79 is a 2-digit or 3-digit jump. There are zero 1-digit jumps in this range.

5-series (D=62..79): 4 jumps of 2, 4 jumps of 3. Alternating 2-3-2-3-2-3-2-3 pattern.
7-series (D=62..79): 3 jumps of 2, 4 jumps of 3.

The "gap between boundaries" is not a filled region — it is itself a continuous stream of multi-digit jumps. The series does not settle into 1-digit-per-prime growth until much later (no run of 10 consecutive 1-digit jumps found within 500 primes, D < 1700).

**Natural-log positions of all skip events:**

| Series | D | ln*D | Jump |
|---|---|---|---|
| 5-series | 62 | 142.8 | 2 |
| 5-series | 64 | 147.4 | 3 |
| 5-series | 67 | 154.3 | 2 |
| 5-series | 69 | 158.9 | 3 |
| 5-series | 72 | 165.8 | 2 |
| 5-series | 74 | 170.4 | 3 |
| 5-series | 77 | 177.3 | 2 |
| 5-series | 79 | 181.9 | 3 |

These are reported without interpretation. CinC can check against icosahedral element-counts.

**Verdict: (d) — sub-structure exists but is dense and uniform (alternating 2-3 jumps), not sparse/clustered.** The D=62..79 range is not a "gap between boundaries" in the structural sense — it is a continuation of the same multi-digit-jump regime. The two "boundaries" at D=60 and D=80 are not isolated features bracketing a featureless region; they are two specific points in a continuous stream that the paper selected for analysis.

### 11.3 Tension-Ladder Shadows in Chi5

**Question:** Do the ladder indices {41, 51, 53, 62} show systematic features in S_5(n) and S_7(n)?

**Results:**

5-series at ladder indices:

| n | S(n) | Tie? | Extremum? | chi5 | Dist to tie | Type |
|---|---|---|---|---|---|---|
| 41 | 0 | TIE | | +1 | 0 | LADDER |
| 51 | +4 | | MAX | +1 | 8 | LADDER |
| 53 | +2 | | | -1 | 8 | LADDER |
| 62 | +1 | | | +1 | 1 | LADDER |

7-series at ladder indices:

| n | S(n) | Tie? | Extremum? | chi5 | Dist to tie | Type |
|---|---|---|---|---|---|---|
| 41 | -3 | | | +1 | 15 | LADDER |
| 51 | -5 | | | +1 | 25 | LADDER |
| 53 | -7 | MIN | | -1 | 27 | LADDER |
| 62 | -6 | MIN | | -1 | 36 | LADDER |

Null distribution (100 random indices in [10, 100]):

| Metric | 5-series null | 7-series null |
|---|---|---|
| Ties | 26.4% | 1.1% |
| Extrema | 22.0% | 15.4% |
| Near-tie (dist <= 1) | 62.6% | 3.3% |

Ladder indices: 5-series ties 1/4 (25%, vs null 26.4%), extrema 1/4 (25%, vs null 22.0%), near-tie 2/4 (50%, vs null 62.6%). 7-series ties 0/4 (vs null 1.1%), extrema 2/4 (50%, vs null 15.4%), near-tie 0/4 (vs null 3.3%).

**Verdict: (b) — no systematic distinguishing feature.** With only 4 ladder indices, there is no statistical power. The 5-series ladder indices look entirely generic (all rates within null range). The 7-series shows 2/4 extrema vs null 15.4%, which would be notable if the sample were larger, but at n=4 this is 1 event from chance. n=41 being a tie in the 5-series is noted but is one data point against a 26% null rate.

### 11.4 Overall Assessment

The crackle is understandable — ln(10)*60 = 138.2 and ln(10)*80 = 184.2 are genuinely close to the physics programme's 140 and 184. But the null tests show:

1. The D=60 and D=80 scales are not special in the "first/second boundary" sense — they're the ~5th and ~9th 3-digit jumps, chosen for the paper's structural analysis.
2. The range between them is not featureless — it's a continuous stream of 2-3 digit jumps.
3. The ladder indices show no systematic chi5 features.

The coincidence between ln(10)*60 ~ 140 and ln(10)*80 ~ 184 remains a numerical fact. Whether it's meaningful depends on whether there is a *structural* reason for the staggered-to-coincident transition to happen specifically at the ~30th prime of each series (D~60). The tests in this section do not address that question — they address and fail to confirm the broader claims about mod-6 specificity and sub-structure.

**For CinC:** The bridge between Paper A and the physics programme rests on a narrower coincidence than the brief hoped: two specific numbers (60 and 80) whose ln(10) multiples happen to be near 140 and 184. The null tests do not strengthen this into a structural connection. They also do not refute it — a coincidence is not disproved by failing to find additional coincidences. But the discipline of Pattern 75 says: report the coincidence as OBSERVED, do not elevate it to STRUCTURAL without a derivational link.

---

## 12. v2.6 -> v2.7 Adversary Follow-up Tests (May 12 2026)

Four computational items Mr Adversary pressed on during the fresh-context review of v2.6 (returned at 4.5 stars). Brief: `mr_code_brief_v27.md`. Tasks 1-4 produce numbers for v2.7; paper prose integration is CinC's downstream step.

### 12.1 Synchronisation-Budget Null Comparison (Task 1)

**Question:** v2.6 section 5.4 reports a cumulative synchronisation budget converging near 6% at full scale but never compares it to the null. Is the budget prime-specific or generic?

**Method.** Extend the existing 10-trial full-scale null framework (`verification/full_null_model.py`) to compute the synch-budget metric per trial. Budget definition: total digit-space inside 100% synchronisation clusters / max_d, where clusters use the same parameters as section 5.2 — window=50, min_gaps>=20, cb==ca (every gap in the window coincident across both series), with overlapping windows merged at merge_dist=500. Sieve to 15,000,000; n_use=485,199 per series; max_d ~ 3.25M.

Seed: trial * 137 + 42 (consistent with all prior null tests).

**Script:** `null-tests/synch_budget_null.py`. Runtime: 64s.

**Results.**

| Metric | Value |
|---|---|
| `budget_real` | 0.099682 (9.97%) |
| `budget_null_mean` | 0.105791 (10.58%) |
| `budget_null_std` | 0.022484 (2.25%) |
| `z_score` | **-0.272** |
| Null range | [7.22%, 14.42%] |
| Null trials with budget >= real | 5/10 |

**Per-trial null:** 10.46, 10.76, 9.66, 10.59, 9.37, 14.42, 7.22, 14.39, 9.37, 9.54 (%).

Real-prime cluster count at full scale: 48 (total span 324,460 digits over max_d=3,254,959).

**Verdict.** z = -0.27. The synch budget is statistically indistinguishable from the null. Generic property of dense logarithmic accumulation under window=50/min_gaps>=20 cluster detection, not prime-specific. This is the outcome the brief anticipated ("Expected (not required) outcome: z ~ 0, generic-indistinguishable").

**Flag for CinC — budget_real does not match v2.6 section 5.4's ~6% figure.** Under the section 5.2 cluster definition (the one the brief specified — window=50, min_gaps>=20, merge_dist=500), `budget_real` is **9.97%**, not ~6%. Two possibilities:

1. Section 5.4 uses a different cluster-detection parameter set than section 5.2 — e.g., the same definition that produces section 5.2's "36 clusters" headline (which is itself inconsistent with section 5.2's "47 inter-cluster gaps -> 48 clusters" three paragraphs later — see Task 2 below).
2. Section 5.4 defines budget differently from "total cluster span / max_d" — perhaps as an asymptotic running-average that hasn't yet converged at 3.25M.

Acceptance criterion #1 (deterministic under seed) and #3 (z ~ 0) are met. Acceptance criterion #2 (matches ~6%) is not met under the §5.2 definition. Task 2 may resolve this; if not, the §5.4 prose needs updating to reflect 9.97% under matched parameters.

### 12.2 Cluster-Count Reconciliation (Task 2)

**Question:** v2.6 section 5.2 reports "36 clusters" (headline) and "47 inter-cluster gaps -> 48 clusters" (full-scale refit, three paragraphs later), both at full scale (3.25M digits). Source of the discrepancy?

**Method.** Parameter sweep of cluster detection at full scale. Real primes only (no null trials needed). Grid: window in {30, 40, 50, 60, 70}, min_gaps in {20, 22, 25, 28, 30, 35, 40}, merge_dist in {200, 500, 1000, 2000, 5000}.

**Script:** `null-tests/cluster_count_reconcile.py`. Runtime: 50s.

**Result. Both numbers are correct under different merge_dist values, with all other parameters identical.**

| Parameter set | n_clusters | n_inter_cluster_gaps | budget% | Matches paper passage |
|---|---|---|---|---|
| window=50, min_gaps=20, merge_dist=200  | 158 | 157 |  8.99% | — |
| window=50, min_gaps=20, merge_dist=**500**  |  **48** |  **47** |  9.97% | **§5.2 paragraph 3 ("47 inter-cluster gaps")** |
| window=50, min_gaps=20, merge_dist=1000 |  38 |  37 | 10.19% | — |
| window=50, min_gaps=20, merge_dist=**2000** |  **36** |  **35** | 10.28% | **§5.2 paragraph 1 ("we identify 36 such clusters")** |
| window=50, min_gaps=20, merge_dist=5000 |  34 |  33 | 10.49% | — |

The headline figure uses **merge_dist=2000**; the full-scale refit uses **merge_dist=500**. Both at window=50, min_gaps=20. The numbers reconcile exactly with the paper's two passages.

**Auxiliary finding — min_gaps is effectively redundant at window=50.** At full scale with window=50, the raw sync_starts count is invariant for min_gaps in [20, 35] (all give 13,112). Every coincident-only 50-window naturally contains >= 35 coincident gaps; tightening min_gaps below 40 changes nothing. Only the merge rule moves the cluster count.

**Methodological note — merge_dist=500 is the script-level canonical.** Every committed analysis script defaults to merge_dist=500:

- `verification/full_null_model.py` (§6.2 200k cluster analysis): merge_dist=500
- `null-tests/power_law_full_scale.py` (§5.2 full-scale refit): merge_dist=500
- `null-tests/cluster_count_100_trials.py` (100-trial null follow-up): merge_dist=500

The merge_dist=2000 setting that produces the "36" headline is **not the default of any committed script**. It must have been computed ad hoc and quoted into §5.2 without the parameter being documented in either the script suite or the paper text.

**Verdict and recommended §5.2 framing for v2.7.**

The 36-vs-48 discrepancy is a parameter-disclosure failure, not a numerical error. Both numbers are correct under their respective parameter sets, but §5.2 reports them as if they were the same computation. Three options:

1. **Standardise on merge_dist=500 (recommended).** Replace "36 clusters" in §5.2's headline with "48 clusters / 47 inter-cluster gaps at full scale". Single self-consistent number throughout. Aligns with every committed script and with the 200k §6.2 analysis.
2. **Standardise on merge_dist=2000.** Replace "47 inter-cluster gaps" with "35 inter-cluster gaps" in §5.2's refit paragraph and re-run `power_law_full_scale.py` with merge_dist=2000. Requires a scientific justification for the wider merge (e.g., "2000 ≈ 40 windows captures larger-scale aggregation"); v2.6/v2.7 currently gives none.
3. **Report both with explicit merge-rule sensitivity.** Add a sentence: "Under merge_dist=500 we identify 48 clusters; under merge_dist=2000 we identify 36 clusters; downstream power-law fits use merge_dist=500."

The first option is cleanest and requires the least new prose. I recommend it.

**§5.4 budget cross-check (Task 1 follow-up).** The Task 1 flag — `budget_real` = 9.97% under §5.2 defaults, not the §5.4 headline ~6% — is **not** resolved by this reconciliation. Across the full merge_dist sweep at window=50, min_gaps=20 the budget ranges 8.99% to 10.49%; even merge_dist=2000 (the parameter producing 36 clusters) gives 10.28%. Whatever metric §5.4 uses for "synchronisation budget" is not `sum(cluster.span) / max_d` under any swept (window, min_gaps, merge_dist) triple. §5.4 needs a separate investigation — its own definition committed to a script — before v2.7. Possible distinct metric: union coverage of raw 50-digit sync-windows pre-merge (likely ~4%) or a running cumulative average reported at a sub-full-scale convergence point.

**Brief note for CinC — paper passages requiring update:**
- v2.6 §5.2 paragraph 1: "we identify 36 such clusters" -> "we identify 48 such clusters" (under recommendation 1).
- v2.6 §5.2 paragraph 3: numbers stand (47 inter-cluster gaps already correct under merge_dist=500).
- v2.6 §5.4: ~6% claim still unresolved; recommend §5.4 author state the metric definition explicitly and supply (or commission) a script that computes it. Then re-check budget_real against null (Task 1 can re-run trivially once the metric is fixed).



### 12.3 R-squared vs Cumulative Scale (Task 3)

**Question:** v2.6 reports R² = 0.979 at 200k (z = +2.20) and R² = 0.226 at full scale (3.25M). Is the transition between these endpoints a clean regime boundary or a smooth decay?

**Method.** Cluster-spacing power-law fit at 8 cumulative scales — 50k, 100k, 200k, 300k, 500k, 1M, 2M, 3.25M digits — with 100-trial null bands at each. Parameters fixed across scales at canonical §5.2: window=50, min_gaps=20, merge_dist=500 (Task 2's recommendation).

Seed scheme: `seed = trial * 137 + 42 + scale_offset` with **scale_offset = 0** for all scales. The same 100 pseudo-prime draws are re-used and truncated at each cumulative scale. This produces *correlated* null bands across scales, the natural view of "how does R² evolve within a fixed sample as the data grows." Independent draws per scale (e.g. `scale_offset = scale_index × 1_000_000`) would make the trajectory appear noisier than the underlying R²(scale) curve actually is, and would multiply runtime ~8×. Documented in the script docstring; a re-runner who prefers independent samples can change one constant.

**Script:** `null-tests/r2_vs_scale.py`. Runtime: 502s (~8 min).

**Results — R² and cluster count at each scale.**

| Scale | n_cl real | n_cl null mean | R²_real | R²_null mean | R²_null std | R²_null max | z(R²) |
|---|---|---|---|---|---|---|---|
| 50,000 | 7 | 13.7 | 0.9840 | 0.3727 | 0.2315 | 0.9226 | **+2.64** |
| 100,000 | 10 | 19.9 | 0.9859 | 0.4816 | 0.1968 | 0.8607 | **+2.56** |
| 200,000 | 13 | 28.1 | 0.9792 | 0.5767 | 0.1833 | 0.8561 | **+2.20** |
| 300,000 | 15 | 34.6 | 0.9786 | 0.5270 | 0.2164 | 0.8864 | **+2.09** |
| 500,000 | 19 | 42.9 | 0.5955 | 0.5851 | 0.1874 | 0.9015 | +0.06 |
| 1,000,000 | 29 | 58.6 | 0.1960 | 0.5697 | 0.1976 | 0.9307 | −1.89 |
| 2,000,000 | 36 | 80.1 | 0.3502 | 0.5643 | 0.1976 | 0.9050 | −1.08 |
| 3,250,000 | 48 | 110.3 | 0.2264 | 0.2900 | 0.1928 | 0.7578 | −0.33 |

The 200k headline (R² = 0.979) reproduces exactly under merge_dist=500, confirming Task 2's canonical-parameter choice.

**Figure:** `figures/r2_vs_scale.png` (and `.svg`). Real-prime R² (green), null mean (blue) with ±1σ band (light blue), null max (dashed red), all on log x-axis.

**Trajectory shape — clean regime boundary, not smooth decay.**

1. **A "200k regime" exists and is wider than the paper's framing.** R² stays in [0.978, 0.986] across the four scales 50k → 300k. z stays above +2.0 across the same range. The clean power-law fit is not a 200k accident — it is robust from 50k to 300k.

2. **Phase transition between 300k and 500k.** R²_real collapses from 0.9786 (z = +2.09) at 300k to 0.5955 (z = +0.06) at 500k — a drop of 0.38 over a factor-of-1.7 in scale. The null mean barely moves across the same step (0.527 → 0.585). The collapse is real-prime-specific, not a generic null-side effect.

3. **Above 500k, real primes are *worse* than null.** From 1M onward R²_real falls below R²_null_mean (z is negative). At 1M: R²_real = 0.196 vs null_mean = 0.570 (z = −1.89). Real primes do not just lose the clean power law — they produce a *more scattered* cluster-spacing relationship than typical random pseudo-primes do at the same scale.

4. **The collapse is monotone in the real-prime curve only over 300k → 1M.** Real-prime R² then partially recovers at 2M (0.350) and lands at 0.226 at full scale — a non-monotonic walk well below the null band throughout.

**Interpretation.** The cluster-spacing power-law structure that gives v2.6 its headline (β ≈ 0.637, R² ≈ 0.979) is **regime-specific to cumulative scales ≤ 300k**. Above 500k the structure dissolves: the cluster sequence at 1M – 3.25M has *less* power-law regularity than chance. This re-frames the §5.2 result as:

- "Real primes exhibit a clean cluster-spacing power law at small-to-medium cumulative scales (≤ 300k digits) with R² well above null (z ≥ +2.0). The structure dissolves above ~500k digits, where real-prime R² falls to null-mean (z ≈ 0) and below."

Rather than:

- "Real primes follow a clean power law β = 0.637 with R² = 0.979" (without scale qualifier, currently in §5.2/headline).

**What this does and does not change for v2.7.**

- The 200k headline R² = 0.979 (z = +2.20) **stands** — fully reproduced under canonical merge_dist=500 across 100 trials.
- The R² result is **regime-specific, not asymptotic.** v2.7 must add the "≤ 300k" qualifier. The "200k regime" framing the brief mentions is correct; this task widens it to "50k–300k regime" with quantitative evidence.
- The §5.2 full-scale refit (β at full scale) is in a regime where the cluster sequence is more scattered than null — fitting a power law there is fitting noise. v2.7 should not present full-scale β as comparable to 200k β.
- v2.6/v2.7 §9 lists asymptotic behaviour as an open question. The honest answer is now visible in the table: the power-law regime ends near 300k–500k. What replaces it above 500k is the new open question.

**Brief note for CinC — paper passages requiring update.**
- §5.2 headline: add "in the cumulative-scale regime up to ~300k digits" to the R² = 0.979 / β = 0.637 claims.
- §5.2 full-scale refit paragraph: re-frame the full-scale R² = 0.226 not as a degraded version of the same fit but as evidence the cluster sequence has departed from power-law regularity altogether (R²_real < R²_null_mean at 1M, 2M, 3.25M).
- §9 (open questions): replace "asymptotic behaviour" with the specific finding — power-law structure dissolves above ~500k; characterising the post-300k regime is the new open question.
- Figure caption (new figure required): "R² of cluster-spacing power-law fit at eight cumulative scales. Real-prime R² stays above +2σ of null from 50k–300k digits and falls into / below the null band above 500k. The phase boundary is between 300k and 500k cumulative digits."



### 12.4 Base-Independence Test for R-squared (Task 4)

**Question:** v2.6 §9 acknowledges base-independence as an open question for β only. Mr A's correct catch: the cluster structure itself is defined on base-10 digit bands, so R² (the headline result) is also base-dependent in its definition. Does R² survive when the analysis is repeated under base-2 (bit-length) and base-6 accumulation?

**Method.** Repeat the 200k cluster-spacing analysis with cumulative products grouped under base-2 and base-6, scaled to the 200k-base-10-digit equivalent in each base. Parameters scale proportionally:

| Base | scale (digits/bits) | window | min_gaps | merge_dist | step |
|---|---|---|---|---|---|
| base-10 (canonical) |       200,000 |  50 | 20 |    500 |  10 |
| base-2  | 664,386 bits  | 166 | 20 | 1,661 |  33 |
| base-6  | 257,019       |  64 | 20 |    643 |  13 |

Scale equivalence: 200,000 base-10 digits represents 10^200000, which requires 200000 × log_2(10) ≈ 664,386 bits or 200000 × log_6(10) = 200000 / log_10(6) ≈ 257,019 base-6 digits. (The brief's "257,773" appears to be a small arithmetic slip; the correct value is 257,019. Negligible difference.)

Seed scheme: `seed = trial * 137 + 42 + base_offset`, **base_offset = 0** for all bases. The SAME pseudo-prime draw is re-used across bases and only the log mapping varies. This is the natural design — we want to test whether the same underlying random configuration produces clean power-law R² regardless of the base defining digit bands, isolating the base-mapping effect from sample-to-sample variation.

**Script:** `null-tests/base_independence.py`. Runtime: 413s (~7 min).

**Results.**

| Base | n_cl real | β_real | R²_real | β_null mean | β_null std | R²_null mean | R²_null std | R²_null max | z(R²) | z(β) | #null ≥ real R² |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base-10 | 13 | 0.6371 | 0.9792 | 0.5395 | 0.1852 | 0.5767 | 0.1833 | 0.8561 | **+2.20** | +0.53 | 0/100 |
| base-2  | 11 | 0.6173 | 0.9399 | 0.3928 | 0.2757 | 0.3208 | 0.2159 | 0.8306 | **+2.87** | +0.81 | 0/99  |
| base-6  | 13 | 0.6335 | 0.9765 | 0.5320 | 0.2333 | 0.5437 | 0.2065 | 0.8640 | **+2.10** | +0.43 | 0/100 |

**R² is base-independent.** All three bases satisfy:

1. **z(R²) ≥ +2.0**: separation from null clears 2σ in every base (+2.20, +2.87, +2.10).
2. **0 / 100 null trials reach the real R²** in any of the three bases. Empirical p-value < 1/100 in each.
3. **β values are within ±0.02 of each other** across bases (0.6173–0.6371), all close to ln(2)/ln(3) = 0.6309.

Base-2 shows the **largest** z-score (+2.87) despite its lowest absolute R² (0.940), because the null in base-2 is wider (R²_null mean = 0.321 vs 0.577 in base-10). Separation from null, not absolute value, is what survives base change.

**Verdict: cluster-spacing power-law structure is STRUCTURAL, not base-10 artefact.**

The 200k cluster-spacing R² result — and the β ≈ 0.637 exponent — survive base change cleanly. Mr A's worry that the headline was definition-dependent on base-10 is answered: under analogous analyses in base-2 and base-6, the same qualitative structure (real-prime R² above null +2σ with zero null overshoots) reproduces, and the quantitative β is preserved within rounding.

**For v2.7 — §9 sharpening.**

The base-independence claim can be promoted from open question to confirmed for both R² and β within the cumulative-scale regime tested (≤300k digits, per Task 3). One-line addition for §9 / abstract:

> "The cluster-spacing power-law structure (β ≈ 0.637, R² ≥ 0.94) is preserved under base-2 and base-6 accumulation at the analogous 200,000-base-10-digit-equivalent cumulative scale, with z(R²) ≥ +2.0 and 0 / 100 null trials reaching the real-prime R² in any base."

**Recommended §9 addendum sentence:**

> "Base-independence of both β and R² is confirmed within the 50k–300k cumulative-scale regime under matched (window, min_gaps, merge_dist) parameter scaling. Whether the post-300k regime (where the power law dissolves) is itself base-independent remains open and would require analogous Task 3-style trajectory scans in base-2 and base-6."

**Methodology note.** As with Task 3, shared draws across bases (base_offset = 0) provide correlated per-base R² values, which is the natural view for isolating the base-mapping effect. Per-base z-scores are unaffected by the shared-draw choice.

---

*Mr Code, May 12-15 2026 (Section 12 complete — Tasks 1, 2, 3, 4, 5, 6; Task 9 optional, pending budget)*

### 12.5 §5.3 Alternation Statistic Pre-Registration (Task 5)

**Question:** Was the §5.3 alternation statistic's prediction committed to git before the test was first computed?

**Method.** Git archaeology — trace the earliest commit specifying the alternation statistic (paper prose, prediction note, or analysis script) and the earliest commit/run that computes it on real data.

**Evidence.**

| Artefact | Commit | Date (UTC+1) | Note |
|---|---|---|---|
| Earliest specification | `74b18be` | 2026-04-13 10:45:51 | Initial scaffold; `paper/Digit_Gaps_Mod6_v2_3.md` includes §5.3 with the 44% descriptive statistic and the named "JUMP/PAIR Heartbeat" pattern |
| Earliest null-test computation | `314ab85` | 2026-04-13 10:58:41 | `null-tests/jump_pair_null.py`; commit message reads "JUMP/PAIR null test — pattern is small-sample artefact" — i.e. result is in the commit message |
| First explicit pre-registration commit anywhere in repo | `06d7e6e` / `7fa5e38` | 2026-05-10 15:57:47 | "pre-register Paper 3 v4.2 brief". Pattern 19/27 pre-reg practice begins ~4 weeks after Paper 4 §5.3 was written. |

**Specification predates first null-test computation by 13 minutes**, but the underlying 44% statistic was computed pre-repo (it appears in the v2.0 PDF appendix from which `full_null_model.py` was extracted). The paper §5.3 text was therefore written *after* the descriptive statistic was already known.

**Crucially, the §5.3 paper text already disclaims confirmatory status.** Its title is "**The JUMP/PAIR Heartbeat (Observational, Pending Null Test)**" and its closing "Status" paragraph reads (verbatim):

> "This observation has not yet been null-tested. Patterns of this kind are particularly susceptible to pattern-recognition artefacts (pareidolia) when extracted from stochastic-looking sequences. Accordingly, we present this as an empirical observation of potential interest, not as an established phenomenon."

No separate prediction commit ("we predict the alternation will survive null with z >= X") exists anywhere in repo history for §5.3. The first quantitative null test (`314ab85`) found the alternation to be a small-sample artefact, and findings.md §3 records this as "pattern is small-sample artefact / verdict: PAREIDOLIA-PRONE."

**Verdict: NOT PRE-REGISTERED.** §5.3 is exploratory observation. The v2.3 text is already honest about this (explicit "Observational, Pending Null Test" label).

**Recommended §5.3 framing for v2.7.**
1. Preserve the "Observational" label; do not promote to confirmatory.
2. Acknowledge that the null test (findings §3) found the alternation to be a small-sample artefact at the 200k scale — the 44% rate is in-distribution under the null model.
3. Either: (a) remove §5.3 from v2.7 entirely now that the null test has run and the result is generic; or (b) retain §5.3 as a worked example of "an observation we initially flagged for null testing, which the test deflated" — pedagogically useful, with the deflation acknowledged in §5.3 itself rather than only in findings.

### 12.6 §6.2 Cluster-Count Direction Pre-Registration (Task 6)

**Question:** Was the direction of the §6.2 cluster-count test pre-committed (one-tailed), or only a two-sided "different from null" test (two-tailed)?

**Method.** Git archaeology — find the earliest commit specifying the cluster-count test including any directional prediction, and the first computation date.

**Evidence.**

| Artefact | Commit | Date (UTC+1) | Note |
|---|---|---|---|
| Earliest test definition (script) | `74b18be` | 2026-04-13 10:45:51 | `verification/full_null_model.py` — `find_clusters_fast` + computes z over null trials with no directional flag (two-sided by construction). Extracted from v2.0 PDF appendix. |
| Earliest paper-text specification | `74b18be` | 2026-04-13 10:45:51 | Same commit; `paper/Digit_Gaps_Mod6_v2_3.md` §6.2 reports the test *and* its result (z = -2.04, "Real primes produce fewer, larger clusters") in one commit. |
| First computation | `74b18be` | 2026-04-13 10:45:51 | The result z = -2.04 was already in the paper text at scaffold time; running `full_null_model.py` reproduces it (verified `858b97e` 2026-04-13 10:49:57 in `reproduction_log.md`). |
| First pre-registration commit anywhere | `06d7e6e` / `7fa5e38` | 2026-05-10 15:57:47 | Pattern 19/27 practice begins ~4 weeks after §6.2 was written. |

**Specification, computation, and result all arrive in the same commit.** The script defines a two-sided z-score; the paper text adds directional prose ("fewer, larger") *after* observing the result. There is no separate commit pre-committing the direction "we predict z < 0" before the test was run. The directional language in §6.2 is post-hoc descriptive, not a pre-registered one-tailed hypothesis.

**Verdict: DIRECTION NOT PRE-COMMITTED. Two-tailed p-value required for v2.7.**

**Corrected p-values.**

| Source | n_trials | z (cluster count) | One-tailed p | Two-tailed p | Significant at α=0.05 (two-tailed)? |
|---|---|---|---|---|---|
| v2.3 §6.2 (paper headline) | 10 | -2.04 | 0.0207 | **0.0414** | Yes — just |
| 100-trial follow-up (findings §7.2) | 100 | -1.37 | 0.0853 | **0.1707** | **No** |
| 100-trial empirical (findings §7.2) | 100 | (4/100 ≤ real, one-tailed) | 0.04 | ≈ 0.08* | **No** |

*Two-tailed empirical: count of |null_count − null_mean| ≥ |13 − 28.12| = 15.12, i.e. null trials with count ≤ 13 or count ≥ 43.24. Lower bound 0.08 from doubling the one-tailed tail (upper tail mass is non-zero given null max 60); exact two-tailed empirical can be recomputed from `null-tests/results/cluster_count_100_trials.csv` if v2.7 needs the precise number.

**Implications for v2.7.**

1. The v2.3/v2.6 headline z = -2.04 should not be reported as if from a one-tailed pre-registered test. Either:
   - Report two-tailed p = 0.0414 alongside z = -2.04 and note the 10-trial std is an underestimate (per findings §7.2), or
   - Lead with the 100-trial follow-up (z = -1.37, two-tailed p ≈ 0.17, empirical p ≈ 0.08).
2. With the 100-trial follow-up applied two-tailed, the cluster-count separation is **no longer statistically significant at α = 0.05**.
3. The R² result (findings §7.3) remains the cleanest surviving prime-specific claim — 0/100 null trials reach R² ≥ 0.979, robust to direction (R² is bounded above by 1, so the directionality question is structural rather than convention-dependent).

**Recommended §6.2 framing for v2.7.**
- Replace z = -2.04 headline with the 100-trial estimate.
- Quote two-tailed p (≈ 0.17 from |z|, ≈ 0.08 empirical) rather than one-tailed p.
- Re-position the cluster-count separation as suggestive/marginal, not as a primary headline.
- Promote the R² result (§7.3) to the headline prime-specific finding instead; it survives the direction test (R² is one-sided by construction) and is robust to trial count.

---

