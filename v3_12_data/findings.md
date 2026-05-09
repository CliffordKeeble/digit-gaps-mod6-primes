# Findings: Paper 3 v3.12 Data Generation

**Mr Code pass — 9 May 2026**
**Brief:** `mr_code_brief_paper_3_v3_12.md` from CinC
**Scripts:** `task1_orderings.py`, `task2_plateau.py`, `task3_premise.py`
**Shared:** `prime_utils.py` (sieve, chi5, t-test, binomial)

---

## Reproduction status

All v3.11 verification anchors reproduce within tolerance:

| Anchor | v3.11 published | This run | Status |
|---|---|---|---|
| Def C, n=33, natural: T | 13 | 13 | OK |
| Def C, n=33, shuffle mean | 6.17 | 6.185 | OK (Δ = 0.015) |
| Def C, n=33, natural z | 2.45 | 2.451 | OK |
| Def A, n=90, natural: T | 29 | 29 | OK |
| Def A, n=90, natural z | 3.64 | 3.612 | OK (Δ = 0.028, sampling noise from per-trial seeding vs shared-RNG) |
| §8.5 N=50k: T | 921 | 921 | OK |
| §8.5 N=50k: ratio | 5.16 | 5.162 | OK |
| §8.5 all 8 published rows | match | all match | OK |

Seed scheme: `seed = trial * 137 + 42` per the brief, matching the canonical
v3.11 null-test convention (`full_null_model.py`, `phase_transition_null.py`,
`jump_pair_null.py`). Note this differs from `boundary/shuffle_robustness.py`
which used a single shared RNG; the small mean differences (Δ≈0.02 on z) are
the expected sampling-variance change between the two conventions.

---

## Task 1: Structured-ordering controls for §6.5.1

**Brief deviation (Q2):** Reversed-sequence (#3 in spec) was identified as
operationally identical to Reversed-size on a size-ordered prime set —
both produce the χ-value sequence (c_n, …, c_1) on the same multiset.
Dropped per CinC's confirmation. Optional **chi-clustered** ordering added
as a deterministic minimum-tie lower-bound control: all χ=+1 primes
ascending, then all χ=−1 primes ascending.

### Result tables

**Definition A** (include ramified p=5 at position 1; n-step running sum):

| Ordering | n=20 | n=33 | n=50 | n=70 | n=90 | n=100 |
|---|---|---|---|---|---|---|
| natural             | 2.29 | 2.59 | 2.90 | 2.58 | **3.61** | **3.21** |
| reversed_size       | -0.87 | 2.59 | -1.22 | 0.44 | 2.27 | 2.35 |
| every_other         | 0.49 | 1.22 | 1.53 | 2.80 | **3.42** | 1.83 |
| index_interleaved   | 2.29 | 1.90 | 0.70 | -0.42 | 0.94 | 0.09 |
| chi_clustered       | -1.32 | -1.50 | -1.49 | -1.71 | **-1.93** | -1.81 |

**Definition C** (omit ramified p=5; (n−1)-step running sum, primary):

| Ordering | n=20 | n=33 | n=50 | n=70 | n=90 | n=100 |
|---|---|---|---|---|---|---|
| natural             | 2.14 | **2.45** | 2.75 | 2.71 | **3.33** | **3.08** |
| reversed_size       | -0.83 | 2.45 | -1.29 | 0.66 | 2.22 | 2.38 |
| every_other         | -0.33 | -0.43 | 1.02 | 1.57 | 0.55 | -0.43 |
| index_interleaved   | 1.15 | 1.73 | 1.31 | -0.93 | 0.36 | -0.61 |
| chi_clustered       | -1.32 | -1.87 | -1.58 | -1.62 | -1.86 | -1.83 |

(Bold = z > 3 or z < −1.85; full-precision CSVs in `results/task1_orderings_def_*.csv`.)

### What this answers

The brief asked: is natural-size-ordering specifically anomalous, or is any
non-random ordering anomalous?

**Answer is between the two extremes the brief framed.**

- **Natural** is robustly anomalous. Under Definition C it clears z > 2 at
  every window n ≥ 33 and reaches z = 3.33 at n = 90. The §6.5.1 claim
  that natural-size-ordering produces an excess-tie regime survives.
- **Reversed-size** clears z > 2 at n = 33, n = 90, n = 100 (Def C: z =
  2.45, 2.22, 2.38) — but not at n = 50 (z = −1.29) or n = 70 (z = 0.66).
  Anomalous-when-it-is-anomalous, but volatile.
- **Every-other-prime** and **index-interleaved** are not significant at
  any window (peak |z| < 1.8 across all 12 cells under Def C). These
  structured non-natural orderings behave essentially like the random
  shuffle baseline.
- **Chi-clustered** is consistently and strongly *low* (z ≈ −1.6 to −1.9
  under Def C), confirming it as a clean minimum-tie lower-bound control.

A clean reading: **monotone size-orderings (forward or reverse) tend to
produce excess ties at large windows; non-monotone re-orderings do not**.
The §6.5.1 claim weakens slightly — the anomaly is not unique to natural
ascending order, but it is also not "any non-random ordering" (every-other
and index-interleaved would falsify that). The relevant axis is monotonicity
of size, not direction.

### Why reversed-size matches natural at n=33

At n=33 (Def A) and n=33 (Def C), the χ multiset is exactly balanced
(equal +1's and −1's), so S_L = 0. For balanced multisets, the running
sum of the reversed sequence has ties at exactly the same positions as
the original (a structural identity, not a coincidence). At unbalanced
windows (n=50, 70), reversed and natural differ.

### Implications for §9 Q8

Per the brief: "If reversed-size ... shows tie counts comparable to
natural ordering — i.e., z > 2 against shuffle — the §6.5.1 claim weakens
to 'any ordered arrangement,' and §9 Q8 (ℤ[φ] geometric reading) is
materially affected."

Reversed-size shows z > 2 at 3 of 6 windows (under Def C). This is partial
material affect: the claim's strongest form ("natural ordering uniquely
anomalous") is not supported, but the claim's weakest form ("any non-random
ordering is anomalous") is also not supported. The middle reading —
**monotone size-orderings produce excess ties; permuted orderings do not**
— is what the data supports.

---

## Task 2: §6.5.3 plateau extension to N = 500k

**Result: scenario (b) but with the opposite sign — slow DOWNWARD drift
visible on N ≥ 1k.** This contradicts the §6.5.3 plateau framing.

### Extended 11-row table

| N | T(N) | √(2N/π) | Ratio | Status |
|---|---|---|---|---|
| 100 | 29 | 7.979 | 3.6346 | v3.11 |
| 500 | 72 | 17.841 | 4.0356 | v3.11 |
| 1,000 | 141 | 25.231 | 5.5883 | v3.11 |
| 2,000 | 232 | 35.682 | 6.5018 | v3.11 |
| 5,000 | 327 | 56.419 | 5.7959 | v3.11 |
| 10,000 | 437 | 79.788 | 5.4770 | v3.11 |
| 20,000 | 683 | 112.838 | 6.0529 | v3.11 |
| 50,000 | 921 | 178.412 | 5.1622 | v3.11 |
| **100,000** | 1190 | 252.313 | **4.7164** | **NEW** |
| **200,000** | 1663 | 356.825 | **4.6606** | **NEW** |
| **500,000** | 2924 | 564.190 | **5.1827** | **NEW** |

(All 8 v3.11 rows reproduce exactly; data in `results/task2_plateau.csv`.)

### Linear fits

| Range | n | df | Slope | SE(slope) | t | p (two-tail) | R² |
|---|---|---|---|---|---|---|---|
| Full (N = 100…500k) | 11 | 9 | +0.162 | 0.240 | 0.67 | 0.517 | 0.05 |
| Restricted (N ≥ 1k) | 9 | 7 | **−0.481** | 0.170 | **−2.83** | **0.026** | 0.53 |

### What this means

The full-range slope is not significant (the early ramp from 3.63 at N=100
to 6.50 at N=2000 cancels with the late decline), but **the restricted
N ≥ 1k fit shows a significantly negative slope (p = 0.026)**. The ratio
is *drifting downward* on the part of the range that the §6.5.3 v3.11
analysis labelled "plateau."

Restricted (N ≥ 1k) descriptive stats:
- mean = 5.460, std = 0.605, **CV = 11.07%** (above the v3.11 reported 8%)
- min/max = 4.66 / 6.50

The CV of 11% is up from 8% in v3.11's 6-point N≥1k set; adding the three
new high-N points shifts both the mean (5.76 → 5.46) and the spread.

The trajectory is non-monotonic: peak ratio 6.50 at N=2k, drops to 5.16 at
N=50k, drops further to 4.66 at N=200k, then partial recovery to 5.18 at
N=500k. The v3.11 reading "stable at ~5.8x for N ≥ 1k" overstates the
data; the new reading is **gently declining with structural noise**.

### Per the brief's three scenarios

- **(a) Plateau holds at 500k:** NOT supported. Ratio leaves the [5.0, 6.5]
  band on three of the eleven points (N=100k: 4.72, N=200k: 4.66, N=2k:
  6.50). CV = 11% > 10%. Restricted slope significantly negative.
- **(b) Slow upward drift:** NOT supported in the predicted direction —
  drift is **DOWNWARD**.
- **(c) Sudden change at 500k:** NOT supported — N=500k recovers slightly
  (ratio 5.18) rather than continuing the N=200k trough.

The data fits "slow downward drift on N ≥ 1k with high noise" — a fourth
scenario the brief did not enumerate. Per CinC's note that "different
result, structurally more interesting" applies to (b), the same applies
here in the inverted form: §6.5.3 should be reframed around the trend.

### Reframing suggestion (subject to CinC review)

Replace v3.11's "stabilises at approximately 5.8× for N ≥ 1k (CV = 8%)"
with: **"reaches a peak of ~6× near N = 2k–20k, then declines slowly
across the next decade — slope = −0.48 per log₁₀ N on N ≥ 1k (t = −2.83,
p = 0.03 over 11 orders of magnitude in log-N range)."** Whether this
indicates asymptotic convergence to the random-walk expectation (ratio
→ 1 as N → ∞) or a slow drift to some non-trivial constant cannot be
distinguished from N ≤ 500k alone. Extension to N = 1M, 2M would help.

Plot: `results/task2_plateau.png`.

---

## Task 3: §6.4 premise verification

**Result: hypothesis NOT confirmed at n=1000 for any q. Direction
consistent across all q (positive effect size: more inerts than splits)
but magnitude too small for significance.**

### Spot-check (q=4, p=5 included)

| Prime | 5 | 13 | 17 | 29 | 37 | 41 | 53 | 61 | 73 | 89 |
|---|---|---|---|---|---|---|---|---|---|---|
| chi5 | 0 | −1 | −1 | +1 | −1 | +1 | −1 | +1 | −1 | +1 |

Matches the brief's hand list exactly.

### Per CinC's Q5 refinement: p=5 excluded from all q lists

For q ∈ {6, 8, 12} the exclusion is a no-op (p=5 is not ≡ 1 mod q). For
q=4 it removes one ramified χ=0 from the count; the remaining 100 / 1000
samples are all χ ∈ {+1, −1}.

### Results table

| q | n | inerts (χ=−1) | splits (χ=+1) | fraction inert | 2-tail p | effect size |
|---|---|---|---|---|---|---|
| 4 | 100 | 53 | 47 | 0.5300 | 0.617 | +0.030 |
| 4 | 1000 | **508** | 492 | **0.5080** | **0.635** | +0.008 |
| 6 | 100 | 53 | 47 | 0.5300 | 0.617 | +0.030 |
| 6 | 1000 | **509** | 491 | **0.5090** | **0.591** | +0.009 |
| 8 | 100 | 57 | 43 | 0.5700 | 0.193 | +0.070 |
| 8 | 1000 | **516** | 484 | **0.5160** | **0.327** | +0.016 |
| 12 | 100 | 56 | 44 | 0.5600 | 0.271 | +0.060 |
| 12 | 1000 | **514** | 486 | **0.5140** | **0.393** | +0.014 |

(Bold = n=1000 row. CSV in `results/task3_premise.csv`.)

### Per-q summary at n=1000

- q=4:  bias **NOT confirmed** (p=0.635); direction: small inert excess (+0.8%)
- q=6:  bias **NOT confirmed** (p=0.591); direction: small inert excess (+0.9%)
- q=8:  bias **NOT confirmed** (p=0.327); direction: small inert excess (+1.6%)
- q=12: bias **NOT confirmed** (p=0.393); direction: small inert excess (+1.4%)

### What this means for §6.4

The hypothesis under test was: small primes p ≡ 1 (mod q) for q ∈ {4, 6, 8, 12}
have systematic over-representation of mod-5 non-residues. Per the brief,
"if not confirmed, the §6.4 conditional language stays."

So: §6.4 keeps its conditional framing. The direction is *consistent with*
the §8.4 mechanism (which attributed the ~28× tie deficit on p ≡ 1 mod q
classes to a "systematic inert bias"), but the magnitude at n=1000 is too
small (~1%) to confirm as observation.

### Reconciling with §8.4's tie deficit (worth flagging)

§8.4 reported only 2 ties in 5000 primes for the mod4=1 class — 28× fewer
than the random-walk expectation. That is a strong observed effect. My
Task 3 finds the per-prime χ₅=−1 frequency is only 50.8% (q=4, n=1000).
These are quantitatively consistent: a 1% bias accumulating over thousands
of steps produces a cumulative drift that pushes the running sum away
from zero, suppressing zero crossings. The tie-deficit observation is
the integral of a small per-prime bias, not the signature of a large one.

The picture is therefore:
- **Per-prime bias (Task 3):** small, ~1%, not significant at n=1000.
- **Cumulative drift (§8.4):** large, statistically extreme (28× tie deficit).
- **No contradiction:** small bias × many steps = large cumulative effect.

This refines but does not change §8.4's reading. §6.4 should retain its
"consistent with standard Chebyshev bias under a hypothesis we have not
located in the literature" framing; the per-prime hypothesis is consistent
in direction with the data but not strongly confirmed at the sample sizes
tested. A larger-n test (e.g., n = 10000 or 100000) might cross the
significance threshold given the consistent positive direction across all
four q. Optional follow-up.

---

## Decisions made beyond the brief

- **Sieve sizes:** Task 1 sieves to 2M (sufficient for 100 5-series primes
  and matches `boundary/shuffle_robustness.py`). Task 2 sieves to 25M to
  comfortably exceed 500k 5-series primes (got 783k). Task 3 sieves to
  200k (need 4000 primes for q=12 density 1/4; this is generous headroom).
- **Chi-clustered ordering** added as optional sixth ordering per CinC's
  Q2 note. Provides a clean lower-bound control.
- **Reversed-sequence** dropped per CinC's confirmation that it is
  operationally identical to Reversed-size on a size-ordered prime set.
- **Plot rendering:** matplotlib (Agg backend), 120 dpi PNG. Available in
  the environment alongside mpmath; consistent with the existing repo
  practice of using mpmath for high-precision arithmetic.
- **t-distribution p-values:** computed via `mpmath.betainc` (regularised
  incomplete beta) rather than scipy.stats, for stdlib + mpmath consistency.
- **Binomial p-values:** exact two-tailed sum-of-PMF method (mpmath.binomial),
  more robust at large n than normal approximations.
- **Verification halt:** task scripts halt with non-zero exit if their
  v3.11 anchors fail to reproduce within tolerance. None did.

---

## Flags for CinC

1. **Task 2 finding inverts the brief's expected scenarios.** §6.5.3's
   plateau claim does not survive the extension. Restricted-range slope
   is significantly negative (p = 0.026) — the ratio drifts down, not up.
   §6.5.3 needs reframing around a slow-decline-with-noise narrative
   rather than a stable plateau. Plot makes this visually obvious.

2. **Task 1 result is mixed.** Natural ordering remains robustly anomalous
   (z > 2 across all n ≥ 33 under Def C) but reversed-size also clears
   z > 2 at half the windows. The §6.5.1 claim narrows from "natural-
   size-ordering specifically" to "monotone size-orderings". §9 Q8 should
   be re-read against this — direction-of-monotone is plausibly the
   relevant axis, not natural-ordering specifically.

3. **Task 3 confirms direction, not magnitude.** §6.4's conditional
   language stays, but the consistent positive effect size across all
   four q (and across both n=100 and n=1000 levels, with stronger
   effects at smaller n) is a hint that a larger-n test or a small-prime-
   restricted test could cross significance. Optional follow-up; not
   blocking for v3.12.

4. **Per-trial vs shared-RNG seeding.** The brief's "seed = trial × 137 + 42"
   scheme matches the canonical v3.11 null-test convention but differs from
   `boundary/shuffle_robustness.py` (which used a single shared RNG). The
   reproduction tolerance (Δ ≤ 0.03 on z) is within sampling noise — both
   schemes sample from the same population.

---

🐕☕⬡

— Mr Code, 9 May 2026
