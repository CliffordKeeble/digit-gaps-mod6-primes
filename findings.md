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

*Mr Code, April 13 2026*
