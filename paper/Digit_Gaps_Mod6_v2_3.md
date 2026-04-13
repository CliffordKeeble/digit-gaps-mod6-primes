# Digit Gaps and Synchronisation Clusters in Mod-6 Prime Products: Analysis to 3.25 Million Digits with Null Model Verification

**Dr. Clifford Keeble, PhD** — ORCID: 0009-0003-6828-2155
*In collaboration with Claude (Anthropic)*
Woodbridge, UK — April 2026 — **Version 2.3**

## Abstract

All primes greater than 3 belong to exactly one of two residue classes modulo 6: the 5-series (p ≡ 5 mod 6) or the 7-series (p ≡ 1 mod 6). We study the cumulative products of primes from each series across four orders of magnitude in digit-length, from 10³ to 10⁶ digits. These products exhibit digit gaps — decimal scales at which no product exists — that undergo phase transitions from staggered to coincident as scale increases.

We establish three categories of result. First, universal properties of logarithmic sequences: the spacing between coincident gaps lies in {1, 2, 3} for 99.9998% of 2.35 million spacings, with a distribution of approximately 68:26:6 — confirmed by a null model using random pseudo-primes with prime-number-theorem density. Second, prime-specific structure: the synchronisation clusters where both series gap at identical digits are fewer and larger for real primes than for random sequences (z = −2.04), and their spacing follows a power law with exponent β = 0.637 ± 0.029 (R² = 0.979), robust across all parameter choices and near ln(2)/ln(3) = 0.6309. Third, the residue N mod 3 of any RSA modulus N = pq classifies whether its prime factors belong to the same or different mod-6 classes — a result elementary from the ring structure of (ℤ/6ℤ)*, consistent with an independently-posted observation of Gocgen [6] and with folklore in elementary number theory.

A self-contained Python verification script confirms all results in 32 seconds using only the standard library.

## 1. Introduction

The security of RSA encryption rests on the difficulty of factoring the product of two large primes. The prime number theorem describes how primes thin out at large scales, but says little about the *multiplicative structure* of primes separated by residue class. In this paper, we show that cumulative products of primes from each mod-6 class exhibit a rich structure of digit gaps, phase transitions, and synchronisation clusters that persists unchanged across four orders of magnitude in digit-length.

We do not claim this structure enables a factoring attack. We demonstrate that the multiplicative landscape of primes at all scales possesses structural order that has not previously been characterised as such, distinguish rigorously between properties generic to logarithmic sequences and those specific to primes, and argue this merits further investigation.

**Relation to prior work.** The analytic-number-theory literature on primes in arithmetic progressions has studied the *reciprocal* Mertens product ∏(1 − 1/p)⁻¹ over primes in residue classes extensively — Williams (1974), Languasco & Zaccagnini [9], Jung [10] for the function-field analogue, Chen & Luo [11] for multiple-variable extensions. These works produce constants and log-growth asymptotics. The distributional behaviour of primes across residue classes has been studied under the heading of *prime races* — Rubinstein & Sarnak [12], Granville & Martin [13], Ford, Konyagin, Harper and Lamzouri on extremes and transitions, Ford & Sneed [14] extending to products of two primes, Meng to k-almost-primes. These works study additive counts π(x; q, a).

The present paper's object is different: the raw cumulative product Π_a(n) = ∏_{p≡a (mod 6), p≤p_n} p, analysed at the scale of its decimal digit length, and the joint behaviour of Π₅ and Π₇ under this digit-length lens. This is a signal-processing framing of a multiplicative object rather than a counting or asymptotic framing. To our knowledge, the digit-gap structure of residue-class-restricted cumulative prime products at these scales has not previously been reported.

Separately, a small but active literature on fractal and self-similar structure in prime sequences — Wolf [15a], Cattani & Ciancio [16], and related work — reports power-law and multifractal scaling in various prime statistics. The exponent β ≈ ln(2)/ln(3) we observe in Section 5.2 is adjacent in framing but is, to our knowledge, not previously reported for mod-6 cumulative products. Wolf [15b], studying nearest-neighbour spacings of primes, reports residual oscillations "of the very profound period of length six" after rescaling — a statistical echo of the same mod-6 class structure that organises the objects analysed here, though Wolf does not pursue this connection.

The mod-6 classification of prime pairs and its implications for RSA moduli have attracted independent attention. Gocgen [6] explores the residue-class partition from the perspective of prime gaps, deriving Diophantine constraints on factorisation search spaces. The observation that N mod 3 (equivalently N mod 6 for N coprime to 6) classifies whether the two factors of an RSA modulus share or differ in mod-6 class is, strictly speaking, elementary folklore — a direct consequence of the ring structure of (ℤ/6ℤ)* = {1, 5} — and appears in pedagogical and informal sources (hexagonal prime-spiral visualisations, Kurzweg [17]). The present paper's contribution here is contextual rather than novel: we situate this folklore observation within the framework of digit gaps and synchronisation clusters developed in Sections 4–6.

## 2. The Two Prime Series

**Definition.** For any prime p > 3: the 5-series P₅ = {5, 11, 17, 23, 29, 41, 47, …} where p ≡ 5 (mod 6), and the 7-series P₇ = {7, 13, 19, 31, 37, 43, 61, …} where p ≡ 1 (mod 6).

**Lemma 1.** Every prime p > 3 satisfies p ∈ P₅ ∪ P₇. *Proof.* If p > 3 is prime, then p is coprime to both 2 and 3. The residues modulo 6 coprime to 6 are exactly {1, 5}. ∎

We define cumulative products Π₅(n) = ∏ᵢ₌₁ⁿ p₅,ᵢ and Π₇(n) = ∏ᵢ₌₁ⁿ p₇,ᵢ, and their digit-length sequences D₅(n) = ⌊log₁₀ Π₅(n)⌋ + 1 and similarly D₇(n). A digit gap at digit-length d means no index n exists such that D(n) = d.

## 3. The Mod-3 Exclusion Property

**Lemma 2.** Π₅(n) ≢ 0 (mod 3) for all n ≥ 1. *Proof.* Each p ∈ P₅ satisfies p ≡ 2 (mod 3). Therefore Π₅(n) ≡ 2ⁿ (mod 3), which cycles through {2, 1} and is never 0. ∎

**Lemma 3.** Π₇(n) ≢ 0 (mod 3) for all n ≥ 1. *Proof.* Each p ∈ P₇ satisfies p ≡ 1 (mod 3). Therefore Π₇(n) ≡ 1 (mod 3) ≠ 0. ∎

**Corollary.** Products of primes from either series alone can never be divisible by 3. To produce a number divisible by 3 at any scale, an external factor of 3 is required.

## 4. Digit Gaps at Small Scales

### 4.1 Staggered Gaps at the 10⁶¹ Scale

| Series | n | Digits | mod 3 | Notes |
|---|---|---|---|---|
| 5-series | 30 | 59 | 1 | |
| 5-series | — | 60, 61 | — | GAP |
| 5-series | 31 | 62 | 2 | |
| 7-series | 30 | 61 | 1 | |
| 7-series | — | 62, 63 | — | GAP |
| 7-series | 31 | 64 | 1 | |

*Table 1. Staggered digit gaps at the 10⁶¹ scale.*

**Theorem 1 (Staggered Gaps).** At the 10⁶¹ scale, the digit gaps are staggered: the 5-series gaps at 60–61 digits, the 7-series at 62–63 digits. Both products are ≡ 1 (mod 3) at the gap boundary, and both require an external factor of 3 to produce numbers at the missing scales.

### 4.2 Coincident Gaps at the 10⁸⁰ Scale

| Series | n | Digits | mod 3 | mod 5 | Notes |
|---|---|---|---|---|---|
| 5-series | 38 | 79 | 1 | 0 | |
| 5-series | — | 80, 81 | — | — | GAP |
| 5-series | 39 | 82 | 2 | 0 | |
| 7-series | 37 | 79 | 1 | 2 | |
| 7-series | — | 80, 81 | — | — | GAP |
| 7-series | 38 | 82 | 1 | 3 | |

*Table 2. Coincident gaps at the 10⁸⁰ scale.*

**Theorem 2 (Coincident Gap and Factor Escalation).** At the 10⁸⁰ scale, both series gap at the same digits (80–81). The factor requirement escalates: the 5-series (Π₅(38) ≡ 0 mod 5) needs only factor 3, while the 7-series (Π₇(37) ≡ 2 mod 5) needs factor 15 = 3 × 5.

| Scale | Gap Pattern | 5-Series Factor | 7-Series Factor |
|---|---|---|---|
| 10⁶¹ | Staggered | 3 | 3 |
| 10⁸⁰ | Coincident | 3 | 15 = 3 × 5 |

*Table 3. Phase transition from staggered to coincident gaps.*

**Status note.** Tables 1–3 establish the staggered-to-coincident transition by direct computation at the 10⁶¹ and 10⁸⁰ scales. The broader phenomenon — that coincidence between the two series emerges as cumulative products grow — is confirmed at scale by the cluster analysis in §6.2 (13 synchronisation clusters observed vs 29 ± 8 expected under null, z = −2.04). What remains an open question is whether the specific *factor-escalation pattern* (3 → 15) recurs predictably at larger scales or represents a one-time structural event. §9 lists this as open.

## 5. Extension to 3.25 Million Digits

We extend the analysis by four orders of magnitude, computing cumulative log₁₀ sums for 485,503 primes in the 5-series and 485,199 in the 7-series (sieved to 15,000,000), reaching a maximum digit-length of 3,254,959. The computation uses floating-point log₁₀ accumulation (no large-integer arithmetic) and completes in under 13 seconds.

### 5.1 Gap Spacing Statistics

When coincident gaps are sorted in ascending order, the spacing between consecutive elements lies in {1, 2, 3} for 99.9998% of all 2,355,220 spacings. Five exceptions were found: three at spacing 5, one at spacing 7, and one at spacing 23.

| Band | Spacings | % in {1,2,3} | s = 1 | s = 2 | s = 3 |
|---|---|---|---|---|---|
| 0–500k | 343,737 | 100.00% | 62.9% | 28.8% | 8.3% |
| 500k–1M | 357,423 | 100.00% | 66.7% | 26.8% | 6.5% |
| 1M–1.5M | 361,454 | 100.00% | 67.3% | 27.2% | 5.6% |
| 1.5M–2M | 365,192 | 100.00% | 68.4% | 26.2% | 5.4% |
| 2M–2.5M | 367,540 | 100.00% | 69.6% | 24.8% | 5.6% |
| 2.5M–3.25M | 559,869 | 100.00% | 71.1% | 23.0% | 5.9% |

*Table 4. Spacing statistics by band. The s = 1 frequency rises monotonically from 63% to 71%, indicating progressive compaction. The distribution is approximately 68:26:6, not uniform.*

### 5.2 Synchronisation Clusters

A 100% synchronisation window at position d is a 50-digit band [d, d + 49] containing at least 20 gaps, all of which are coincident (every gap in each series is also a gap in the other). Overlapping windows are merged into contiguous clusters. Across 3.25 million digits, we identify 36 such clusters, with spans ranging from 134 to 61,876 digits.

The gap between consecutive cluster centres follows a power law:

$$\text{gap} \approx 18.2 \times \text{centre}^\beta$$

with β = 0.637 ± 0.029 and R² = 0.979 (first 200,000 digits; see Section 6 for robustness). This exponent is numerically close to ln(2)/ln(3) = 0.6309, the Hausdorff dimension of the Cantor middle-thirds set. **We report this numerical coincidence as observed; no derivation of this exponent from prime-product considerations is currently available to us.** The naive argument via 6 = 2 × 3 would yield ln(2)/ln(6) ≈ 0.3869, not ln(2)/ln(3); hence the observed value demands a different structural explanation than the simplest mod-6 counting. This is an open question (see Section 9).

### 5.3 The JUMP/PAIR Heartbeat (Observational, Pending Null Test)

The ratio of consecutive inter-cluster gaps reveals a visually striking alternating pattern: the system appears to produce a large jump (ratio > 1.5) to establish a new scale, followed by a near-identical echo (ratio ≈ 0.99). The clearest pairings include: (10,642 / 10,282) ratio 0.97; (17,972 / 17,861) ratio 0.99; (54,801 / 54,323) ratio 0.99; and (137,148 / 135,838) ratio 0.99. This reverberation pattern accounts for 44% of consecutive gap ratios.

**Status.** This observation has not yet been null-tested. Patterns of this kind are particularly susceptible to pattern-recognition artefacts (pareidolia) when extracted from stochastic-looking sequences. Accordingly, we present this as an empirical observation of potential interest, not as an established phenomenon. Null-model testing comparable to that in Section 6.2 is identified as immediate future work. If the alternation survives null testing, the mechanism — possibly related to period-doubling or renormalisation-group structure — would require separate investigation.

### 5.4 Cumulative Synchronisation Budget

The fraction of total digit-space occupied by 100%-synchronisation windows stabilises near 5–8% after an initial transient, with the long-term average converging toward approximately 6% — meaning roughly 1 in 17 digits lies within a zone of perfect synchronisation between the two mod-6 prime classes.

## 6. Null Model Verification

A critical question is whether these phenomena are specific to primes or generic to any interleaved logarithmic-growth sequences. We test this by generating pseudo-primes: random integers included with probability 1/ln(n) (matching prime number theorem density), assigned to two classes with equal probability (matching Dirichlet equidistribution). Ten independent trials were computed at the same scale as the real primes (sieve limit 15,000,000, same number of products per series).

### 6.1 Spacing Statistics: Generic

| Metric | Real Primes | Null (mean) | Null (std) |
|---|---|---|---|
| In {1, 2, 3} | 99.9998% | 100.000% | 0.000% |
| Max spacing | 23 | 10.7 | 1.9 |
| s = 1 frequency | 68.0% | 68.1% | 0.9% |
| s = 2 frequency | 25.8% | 25.9% | 1.1% |
| s = 3 frequency | 6.2% | 6.0% | 0.3% |
| Coincident gap % | 72.4% | 72.6% | 0.4% |

*Table 5. All spacing statistics are indistinguishable between real primes and pseudo-primes.*

The {1, 2, 3} spacing bound, the 68:26:6 distribution, the gap density, and the compaction trend are all reproduced by the null model. These are properties of logarithmic accumulation, not of prime distribution. The one notable difference: real primes have max spacing 23 (consistent across computations) while the null model ranges from 8 to 14. Real primes produce rarer but larger spacing violations.

### 6.2 Cluster Structure: Prime-Specific

| Metric | Real Primes | Null (mean) | Null (std) | z-score |
|---|---|---|---|---|
| Cluster count | 13 | 29.2 | 7.9 | −2.04 |
| Power-law β | 0.637 | 0.595 | 0.124 | +0.34 |
| R² | 0.979 | (scattered) | — | — |

*Table 6. Cluster comparison (first 200,000 digits). Real primes produce fewer, larger clusters with a dramatically cleaner power law.*

Real primes produce 13 clusters where the null model produces 29 ± 8 (z = −2.04). The power-law exponent for real primes (β = 0.637 ± 0.029, R² = 0.979) shows an exceptionally clean scaling relationship. The null model produces exponents scattered from 0.45 to 0.83 with no consistent power-law structure. The null model generates clusters (this is generic) but does not generate a clean power law (this is prime-specific).

### 6.3 Sensitivity Analysis

| Window | Min gaps | Clusters | β | Std error | R² |
|---|---|---|---|---|---|
| 30 | 10–20 | 13 | 0.6371 | 0.0299 | 0.978 |
| 40 | 10–20 | 13 | 0.6373 | 0.0295 | 0.979 |
| 50 | 10–20 | 13 | 0.6371 | 0.0293 | 0.979 |
| 60 | 10–20 | 13 | 0.6366 | 0.0290 | 0.980 |
| 70 | 10–20 | 12 | 0.6229 | 0.0399 | 0.964 |

*Table 7. The exponent is stable to ±0.001 across window sizes 30–60 and is completely insensitive to minimum gap count. This is not an artefact of parameter choice.*

## 7. RSA Modular Fingerprint

**Theorem 3 (Class Fingerprint).** Let N = pq with p, q > 5 prime. Then:

- N ≡ 1 (mod 3) ⟺ p and q belong to the same mod-6 class
- N ≡ 2 (mod 3) ⟺ p and q belong to different mod-6 classes
- N ≡ 0 (mod 3) is impossible (since neither factor can be 3)

*Proof.* If p ≡ q ≡ 5 (mod 6), then p ≡ q ≡ 2 (mod 3), so N ≡ 4 ≡ 1 (mod 3). If p ≡ q ≡ 1 (mod 6), then p ≡ q ≡ 1 (mod 3), so N ≡ 1 (mod 3). If p ≡ 5, q ≡ 1 (mod 6), then N ≡ 2 × 1 ≡ 2 (mod 3). ∎

A finer classification uses mod 30. For primes p > 5:

| N mod 30 | Class combinations |
|---|---|
| 1, 7, 13, 19 | Same class: both (5,5) or both (7,7) |
| 11, 17, 23, 29 | Cross class: one (5) and one (7) |

*Table 8. Mod-30 partition of RSA moduli. No computation beyond a single modular reduction is required.*

**On priority and attribution.** Theorem 3 follows directly from the ring structure of (ℤ/6ℤ)* = {1, 5} and Lemma 1, and is therefore elementary number theory. It appears in informal and pedagogical contexts — hexagonal prime-spiral visualisations (implicit), Kurzweg's lecture notes [17] ("a semi-prime N must have its mod(6) operation yield a value of 1 or −1 … both p and q lie along the same diagonal [of the hexagonal integer spiral] if and only if N mod 6 = 1"), and statistical-distribution papers that use the form-conservation property p ≡ ±1 (mod 6) ⟹ pq ≡ ±1 (mod 6). Gocgen [6] develops the observation formally in a cryptanalytic setting, independent of the present work. We therefore present Theorem 3 as **a folklore observation formalised here within the digit-gap / synchronisation framework**; the contribution of Sections 7–8 lies in situating the residue classification alongside the gap and cluster structure of Sections 4–6, not in claiming priority for the modular observation itself.

By itself, this classification provides a binary partition reducing the prime-class search space by roughly half. Its significance in the present work lies in its context: the mod-6 classes are not merely abstract residue labels but represent different multiplicative growth trajectories with distinct gap patterns, factor requirements, and synchronisation behaviour.

## 8. Summary of Results

| Result | Status | Evidence |
|---|---|---|
| Digit gaps exist in both series | Proved | Theorems 1, 2 |
| Phase transition: staggered → coincident | Proved | Tables 1–3, generalised via cluster structure in §6.2 |
| Factor escalation (3 → 15) at 10⁸⁰ | Proved | Theorem 2 |
| Recurrence of factor-escalation pattern at larger scales | Open | §4.2 status note, §9 open question |
| {1,2,3} spacing (99.9998%) | Generic | Null model matches (Table 5) |
| Spacing distribution ~68:26:6 | Generic | Null model matches |
| Gap density ~72% | Generic | Null model matches |
| Compaction trend | Generic | Follows from gap density growth |
| Fewer, larger clusters | Prime-specific | z = −2.04 vs null model (Table 6) |
| Power law β = 0.637, R² = 0.979 | Prime-specific | Null model scattered (Table 6) |
| Exponent robust to parameters | Confirmed | Sensitivity analysis (Table 7) |
| β ≈ ln(2)/ln(3) derivation | Open question | Section 5.2, Section 9 |
| JUMP/PAIR heartbeat | Observed, null-test pending | Section 5.3 |
| N mod 3 classifies RSA factors | Proved (folklore formalisation) | Theorem 3 |

*Table 9. Complete classification of results with Status honestly labelled.*

## 9. Open Questions

1. **Does β converge to ln(2)/ln(3) exactly?** The current value (0.637 ± 0.029) is consistent but not conclusive.
2. **What is the correct fractal-theoretic derivation for the appearance of ln(2)/ln(3)?** The naive argument via 6 = 2 × 3 yields ln(2)/ln(6), not ln(2)/ln(3). A different self-similar construction, with scale factor 3 rather than 6, would need to be identified.
3. **Is the JUMP/PAIR heartbeat prime-specific, or an artefact?** This requires full-scale null-model detection, directly analogous to Section 6.2 for cluster counts.
4. **Does the phase transition (Theorems 1, 2) generalise?** Staggered-to-coincident behaviour at 10⁶¹ → 10⁸⁰ is proved; whether similar transitions recur at predictable scales at the 10⁶ digit range is not established.
5. **Can the structural order in prime products at cryptographic scales be connected to known results in analytic number theory** (Chebyshev bias, prime races under the additive-count framing of Rubinstein–Sarnak [12], Fiorilli–Martin, Ford and collaborators)? The multiplicative-magnitude framing of the present paper appears distinct from the additive-counting literature; the relationship is an open question.
6. **Does the cluster structure have implications for the difficulty of integer factorisation?**

## 10. Computational Verification

All results are verified by the accompanying Python script (`full_null_model.py`), which requires only the Python 3 standard library. The script sieves primes to 15,000,000, computes cumulative log₁₀ products for both series, verifies all spacing statistics, runs 10 null-model trials at identical scale, performs cluster detection with sensitivity analysis, and reports all comparisons. Total runtime: 32 seconds on standard hardware.

    Run: python3 full_null_model.py

## References

[1] Keeble, C. (2026). *Digit Gaps in Prime Series Products.* Zenodo. DOI: 10.5281/zenodo.18412764
[2] Keeble, C. (2026). *The Icosahedral Digital Boundary.* Zenodo. DOI: 10.5281/zenodo.18413140
[3] Keeble, C. (2025). *Bootstrap Universe: Complete Derivation.* Zenodo. DOI: 10.5281/zenodo.17906573
[4] Hardy, G.H. & Wright, E.M. (2008). *An Introduction to the Theory of Numbers,* 6th ed. Oxford.
[5] Falconer, K. (2014). *Fractal Geometry: Mathematical Foundations and Applications.* 3rd ed. Wiley.
[6] Gocgen, A.F. (2025). *RSA from the Perspective of Modular Analysis of Prime Gaps.* Preprints. DOI: 10.20944/preprints202510.1729.v1
[7] Dirichlet, P.G.L. (1837). *Beweis des Satzes, dass jede unbegrenzte arithmetische Progression...* Abh. Königlich Preussischen Akad. Wiss., 45–71.
[8] Rivest, R., Shamir, A., & Adleman, L. (1978). *A Method for Obtaining Digital Signatures.* CACM 21(2), 120–126.
[9] Languasco, A. & Zaccagnini, A. (2010). *On the constant in the Mertens product for arithmetic progressions. I: Identities.* Funct. Approx. Comment. Math. 42, 17–27.
[10] Jung, H. (2026). *Mertens products in arithmetic progressions over function fields.* arXiv:2602.05788.
[11] Chen, Z. & Luo, J. (2025). *Multiple Mertens theorems for arithmetic progressions.* arXiv:2512.07336.
[12] Rubinstein, M. & Sarnak, P. (1994). *Chebyshev's bias.* Experimental Mathematics 3(3), 173–197.
[13] Granville, A. & Martin, G. (2006). *Prime number races.* American Mathematical Monthly 113(1), 1–33.
[14] Ford, K. & Sneed, J. (2010). *Chebyshev's bias for products of two primes.* Experimental Mathematics 19(4), 385–398.
[15a] Wolf, M. (1989). *Multifractality of prime numbers.* Physica A **160**(1), 24–42.
[15b] Wolf, M. (2014). *Nearest-neighbor-spacing distribution of prime numbers and quantum chaos.* Physical Review E **89**, 022922. arXiv:1212.3841.
[16] Cattani, C. & Ciancio, A. (2016). *On the fractal distribution of primes and prime-indexed primes by the binary image analysis.* Physica A **460**, 222–229.
[17] Kurzweg, U.H. (2013). *Finding Large Semi-Primes.* Lecture notes, University of Florida, Department of Mechanical & Aerospace Engineering. https://web.mae.ufl.edu/uhk/FINDING-LARGE-SEMI-PRIMES.pdf

---

*Version 2.3 — April 2026. Revisions from v2.2 (Mr Adversary review of v2.2): (i) §1 fractal-primes paragraph: removed unsourced "0.5–0.85" exponent range (Pattern 39 hygiene — no per-reference anchor available); (ii) removed prose-only mentions of Bershadskii and Selvam (named without reference entries — outreach-grade requires verified citations or no name); (iii) softened "[Wolf's period-six] is a statistical shadow of the mod-6 structure treated analytically in the present paper" to "a statistical echo of the same mod-6 class structure that organises the objects analysed here" — accurate kinship without implying derivational reach; (iv) dropped "we note in passing" filler. No mathematical content changed; all edits are §1 prose hygiene. Supersedes v2.2.*

*Version 2.2 — April 2026. Revisions from v2.1 (citation verification pass by Mr Dig, April 13 2026): (i) [10] Jung initial corrected from Y. to H. (Hwanyup); (ii) [15] Wolf 2014 replaced with [15a] Wolf 1989 Physica A carrying the multifractal power-law claim, with [15b] Wolf 2014 retained as the source for the period-six residual observation in prime nearest-neighbour spacings; §1 fractal-primes paragraph extended to note the period-six chord; (iii) [16] "Cattani 2020 Fractal Fract" corrected to Cattani & Ciancio 2016 Physica A — the cited title "Primality, Fractality, and Image Analysis" is Guariglia's (Entropy 2019), not Cattani's; (iv) [17] author corrected from "Kurt, O." to "Kurzweg, U.H." (Ulrich H. Kurzweg, UF MAE emeritus), date from "undated" to "2013", with §1 and §7 attributions updated. No substantive mathematical content changed; all edits are citation accuracy corrections. Supersedes v2.1.*

*Version 2.1 — April 2026. Revisions from v2.0: (i) Theorem 3 reframed as folklore formalisation rather than independent discovery, with Kurt [17] and folklore sources added alongside Gocgen [6]; (ii) Section 1 extended with explicit relation-to-prior-work situating the paper against the Mertens-AP literature [9, 10, 11], the additive prime-race literature [12, 13, 14], and the fractal-prime literature [15, 16]; (iii) Section 5.3 (JUMP/PAIR) and Section 4.2 status note reframed as observations pending null-model testing rather than established phenomena; (iv) Section 5.2 derivation-gap for ln(2)/ln(3) made more prominent; (v) Section 8 status table made honest about which results are proved, which are observational-pending-null-test, which are open questions. Supersedes v2.0.*

*Correspondence: ORCID 0009-0003-6828-2155 | Woodbridge, UK*

🐕☕⬡
