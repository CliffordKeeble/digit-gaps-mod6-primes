# Mr Code Brief — Paper 199 v1.0 → v1.1

**Target:** Paper 199 v1.1
**Source:** Paper 199 v1.0 (split from Paper 3 v3.18; this paper houses the χ₅ tight-oscillation work and its retraction record)
**Repository:** `github.com/CliffordKeeble/digit-gaps-mod6-primes`
**Working branch:** `v3-12-data` (continuation; the v3.x work directory `v3_12_data/` continues for Paper 199 v1.x χ₅-thread scripts)
**Brief version:** v1.0 (initial)
**Date:** 10 May 2026

🐕☕⬡

---

## Role-card

Mr Code is the implementation specialist for the 2I Universe Programme (Pattern 97). Scope-limited to: **executing pre-registered computations and reporting numerical results faithfully**. Out of scope: changing the pre-registered direction or falsifier; deciding whether a claim survives; rewriting the paper's framing; making interpretive judgments. CinC owns interpretation; Mr Adversary owns review; Mr Library owns publication. Mr Code reports numbers and lets the brief's pre-registration speak.

**Stop-on-fail protocols (Pattern 75)** are enforced at every anchor verification gate. If a published anchor fails to reproduce bit-exactly (within documented tolerance), Mr Code halts the task and reports the discrepancy *without* proceeding to the new computation. Mr Code does not attempt to reconcile or explain anchor mismatches; that is CinC's job.

**Pre-registration discipline (Pattern 19, Pattern 27).** Each task below has a *direction* and a *falsifier* committed before computation. Mr Code's report includes the direction-confirmation and falsifier-test result, computed from the new data, alongside the new numerical content. The falsifier is binding: if the data falsify the pre-registration, the result is reported as falsification, not as something to explain away.

---

## Background

Paper 199 v1.0 contains three forward commitments queued for v1.1, each addressing a Mr Adversary v3.18 review item:

| Task | Item type | Mr Adversary v3.18 query |
|------|-----------|--------------------------|
| 1 | NULL | "the §6.5.2 comparable-moduli test uses q ∈ {4, 6, 8, 12}, which are deeply nested. […] the qualitative claim […] would be much stronger with at least one truly independent comparison, q ∈ {7, 11, 13} for instance. The current four moduli are essentially three observations dressed as four." |
| 2 | GAP/FALSIFIER | "run the §6.5.1 monotone-ordering analysis on the 7-series. If the 7-series under monotone size-ordering also produces an anomaly relative to permuted reorderings of the same primes, candidate (d) is favoured […]. If only the 5-series shows it, candidate (b) is favoured […]. I would expect this to be in v3.19." |
| 3 | NULL/STATUS | "I see no Monte Carlo or bootstrap SE on the present ratios; '5.18' at N = 500k is a single observed count. […] Recommend reporting a bootstrap SE on each row of the ratio table, and pairing the v3.16 supplementary commitment ('at or below 4.5') with an explicit 'above the SE on the next measurement,' so that the falsifier is computable rather than nominal." |

All three tasks are independent — they can be run in parallel or in any order; no task's anchors depend on another task's results. The combined output of v1.1 will resolve three of Mr Adversary's v3.18 substantive items.

---

## Task 1 — Independent modulus test (NULL)

### Question

Under the cyclotomic-split-bias hypothesis (small primes p ≡ 1 mod q biased toward χ₅ = −1 / mod-5 non-residues), do *truly independent* moduli q ∈ {7, 11, 13} show inert excess in the predicted direction at the same magnitude scale (~1%) as the nested q ∈ {4, 6, 8, 12}?

### Why it matters

The current §5 Test (Paper 199 v1.0) reports four-q directional consistency at corrected joint p = 0.190 (Stouffer) / 0.198 (sign-test) under v3.14's nested-modulus correlated null. Mr Adversary's v3.18 NULL observation is that q ∈ {4, 6, 8, 12} are deeply nested under mod 12: primes ≡ 1 (mod 12) sit inside both ≡ 1 (mod 4) and ≡ 1 (mod 6), and primes ≡ 1 (mod 8) overlap with primes ≡ 1 (mod 4). The four moduli are "essentially three observations dressed as four." Adding q ∈ {7, 11, 13} — all primes coprime to 12 — provides three genuinely independent comparisons. If the cyclotomic-split bias is real, the direction must persist on truly independent moduli.

### Method

For each q ∈ {7, 11, 13}:

1. Sieve primes up to a cap sufficient to give n ≥ 1000 primes p ≡ 1 (mod q).
2. Filter primes p satisfying p ≡ 1 (mod q) AND p ≠ 5 (exclude the χ₅-ramified prime).
3. For each n ∈ {100, 1000}, take the first n filtered primes and count those with χ₅(p) = −1 (inert; equivalently p ≡ 2 or 3 mod 5).
4. Compute one-sided binomial p-value for the directional hypothesis "inerts ≥ n/2" (i.e., P(X ≥ observed | binomial(n, 0.5))).
5. Compute z_q = (k_q − n/2) / √(n/4) for q ∈ {7, 11, 13} at n = 1000.

For the **aggregate test combining all 7 moduli** (q ∈ {4, 6, 7, 8, 11, 12, 13}):

6. Run a correlated null over 10,000 χ₅-shuffles preserving the marginal split/inert balance across non-ramified primes (the same null methodology as v3.14's `correlated_null.py`). For each shuffle:
   - Recompute z_q for all 7 moduli.
   - Compute joint Stouffer Z = Σ z_q / √7.
   - Compute joint sign-test count (number of moduli with z_q > 0).
7. Report empirical p-values for observed Stouffer Z and sign-test count against the null distribution.

### Pre-registered prediction (commit before computation)

**Per-modulus direction** (q ∈ {7, 11, 13}, n = 1000):

- **Cyclotomic-split bias hypothesis predicts:** all three of q ∈ {7, 11, 13} show inert excess (k_q > 500 at n = 1000) at magnitude ~1% (k_q in range [505, 525], same scale as q ∈ {4, 6, 8, 12} which gave {508, 509, 516, 514}).

- **One-sided p-value range expected:** p_one-sided ∈ [0.10, 0.45] per modulus at n = 1000 (none individually significant, all directionally consistent).

**Aggregate (7 moduli) under correlated null:**

- **Cyclotomic-split bias hypothesis predicts:** corrected joint p ≤ 0.10 (Stouffer) under correlated null over 7 moduli — tighter than the 4-modulus result of 0.19 because the three new moduli are independent (less correlation drag) and add three new directional confirmations.

- **Conservative range:** corrected joint p ∈ [0.05, 0.15] would be consistent with the hypothesis surviving but not significant.

### Falsifier on-record (binding before computation)

| Outcome | Reading |
|---------|---------|
| **≥ 2 of {7, 11, 13} show k_q < n/2 at n = 1000 (opposite direction)** | **STRONG falsifier**: the four-q directional consistency does not generalise to independent moduli. The cyclotomic-split bias hypothesis is falsified across truly independent moduli. Retraction 4 (mechanistic accumulation downgrade) is sustained; the §5 directional observation also softens to "directional pattern within nested moduli only, not generalised." |
| **1 of {7, 11, 13} shows k_q < n/2 at n = 1000** | Inconclusive within sampling fluctuation. Aggregate joint p across 7 moduli is the deciding statistic. |
| **All 3 of {7, 11, 13} show k_q ≥ n/2 at n = 1000 AND aggregate joint p ≤ 0.05** | **Significance threshold met** under correlated null over 7 moduli. The cyclotomic-split bias hypothesis upgrades from "directionally supported" to "suggestive evidence." |
| **All 3 of {7, 11, 13} show k_q ≥ n/2 AND aggregate joint p ∈ (0.05, 0.15]** | Directional consistency persists at non-significant level. §5's "directionally supported but not significant" framing is sustained, with the marginal-evidence concern (Retraction 4) unaffected. |
| **All 3 show k_q ≥ n/2 AND aggregate joint p > 0.15** | Direction holds but joint significance does not improve over the 4-modulus result. Mechanism remains not-established; v1.1 reports the result as "directional consistency confirmed across truly independent moduli, joint significance not reached." |

### Anchors to reproduce (verification gates)

The new q ∈ {7, 11, 13} computation must be done within the same framework as the existing q ∈ {4, 6, 8, 12} computation. Before reporting new values, Mr Code reproduces:

- **Existing inert counts** for q ∈ {4, 6, 8, 12} at n = 100: {50, 53, 56, 57}.
- **Existing inert counts** for q ∈ {4, 6, 8, 12} at n = 1000: {508, 509, 516, 514}.
- **Correlated-null Stouffer p (4 moduli)** = 0.190 within tolerance ±0.005 (10⁴ shuffles).
- **Correlated-null sign-test p (4 moduli)** = 0.198 within tolerance ±0.005.

If any anchor fails to reproduce, **HALT** and report the discrepancy. Do not proceed to q ∈ {7, 11, 13} until the framework is confirmed reproducible.

### Expected output

A new script `v3_12_data/independent_modulus.py` and a results CSV `v3_12_data/results/independent_modulus_results.csv`. The CSV has columns:

```
q, n, inerts_observed, p_one_sided, z_q
```

with rows for q ∈ {4, 6, 7, 8, 11, 12, 13} × n ∈ {100, 1000}.

A second CSV `v3_12_data/results/independent_modulus_correlated_null.csv` reports:

```
n_shuffles, observed_stouffer_z, p_stouffer_4mod, p_stouffer_7mod, observed_signtest, p_signtest_7mod
```

A markdown summary at `v3_12_data/findings.md` (appended as a new "v1.1 Task 1 results" section) reports:

1. Anchor verification status (PASS / FAIL).
2. Per-modulus inert counts and one-sided p-values for q ∈ {7, 11, 13}.
3. Aggregate (7-moduli) joint Stouffer Z and sign-test count, with correlated-null empirical p.
4. Direction-confirmation summary: how many of {7, 11, 13} show inert excess at n = 1000.
5. Falsifier-test result: which row of the table above applies.

---

## Task 2 — 7-series monotone-ordering test (GAP/FALSIFIER)

### Question

Does the 7-series under monotone size-ordering exhibit a tie-count anomaly relative to permuted reorderings of its own primes, comparable in magnitude (|z|) to the 5-series anomaly? This discriminates §10 Q1(b) "structural-position" reading (where the anomaly is 5-series-specific) from §10 Q1(d) "any monotone ordering" reading (where the phenomenon is monotone-vs-permuted regardless of which residue class).

### Why it matters

§10 Q1 lists four candidate readings of the 5-series tight-oscillation regime: (a) small-prime-decay (falsified v3.14), (b) structural-position, (c) geometric-shadow, (d) bare any-monotone-ordering. Of the surviving (b), (c), (d), Mr Adversary's v3.18 GAP/FALSIFIER query identifies a cheap discriminant: run the §6.1 (formerly §6.5.1) test on the 7-series. The 7-series has no tight-oscillation regime in *natural* ordering (it is in persistent drift, only 2 ties in 5000), so the question is whether its natural ordering still produces an anomaly in the |z| sense — that is, does it deviate from its own shuffle distribution by an unusual amount, even if in the opposite direction (tie *deficit* rather than *excess*)?

### Method

Mirror the v3.13 §6.5.1 / Paper 199 v1.0 §6.1 test on the 7-series:

1. Compute the first 1000 7-series primes (p ≡ 1 mod 6, sorted ascending). Note: no prime in the 7-series is χ₅-ramified, so χ₅(p₇,j) ∈ {+1, −1} for all j; tie-count is well-defined without the Definition A/B/C ramification accounting needed for the 5-series. Use a single definition: count positions k ∈ {1, …, n} with S₇(k) = 0.

2. For each window n ∈ {20, 33, 50, 70, 90, 100} (matching the 5-series test windows), compute:
   - Natural-ordering tie count under the natural size-ordering of the first n 7-series primes.
   - Shuffle distribution: 1000 random permutations of the same first n 7-series primes; for each, compute tie count at window n.
   - Per-window z-score: z(n) = (T_natural − T_shuffle_mean) / T_shuffle_std.

3. **Multi-window aggregate test (Statistic A only — Statistic B Stouffer omitted per Paper 199 v1.0 §6.1 editorial decision).** For each shuffle trial, compute the per-window z-score and take the maximum z across windows. The 1000 max-z values form the null distribution. Compare natural ordering's max z against this null; report empirical p.

4. **Structured-ordering controls** (matching v3.12 task1_orderings.py):
   - Reversed-size (descending) ordering of the first 100 7-series primes.
   - Every-other-prime ordering (alternate selection from the size-ordered list).
   - Index-interleaved ordering.
   - For each, compute z(33) under the same shuffle baseline.

### Pre-registered prediction (commit before computation)

**Under candidate Q1(b) "structural-position" reading:**
- The 7-series is in persistent drift; natural ordering has very few ties at small n. The shuffle distribution of the same primes will also have very few ties (the χ₅ marginal favours inerts, so most random walks drift away from zero quickly). Natural-vs-shuffle gap is small.
- **Predicted |z(33)| ≤ 1.0** under candidate (b); the 7-series has no monotone-ordering structure to be specific to.

**Under candidate Q1(d) "any monotone ordering" reading:**
- Monotone size-ordering produces structure not present under permutation, regardless of residue class. The 7-series under natural ordering should deviate from its own shuffle distribution by an amount comparable to the 5-series deviation.
- **Predicted |z(33)| ≥ 1.5** under candidate (d); the direction may be positive (tie excess) or negative (tie deficit), but the magnitude should be elevated.

**5-series benchmark for comparison** (Paper 199 v1.0 §6.1, Definition C):
- Natural-ordering z(33) = 2.45 (positive direction; tie excess).
- Multi-window aggregate empirical p = 0.005.

### Falsifier on-record (binding before computation)

| Outcome | Reading |
|---------|---------|
| **\|z(33)\| ≤ 1.0 for 7-series natural-vs-permuted** | **Favours Q1(b) structural-position** over Q1(d). The phenomenon is 5-series-specific (or at least tied to residue classes that exhibit a tight-oscillation regime in natural ordering). Q1(d) "any monotone ordering" reading is weakened. |
| **1.0 < \|z(33)\| < 1.5** | **Inconclusive.** Multi-window aggregate p (across the 6 windows) is the deciding statistic. If aggregate p ≤ 0.05, lean toward (d); if aggregate p > 0.10, lean toward (b). |
| **\|z(33)\| ≥ 1.5 for 7-series natural-vs-permuted** | **Favours Q1(d) any-monotone-ordering** over Q1(b). The phenomenon is general to monotone size-ordering of mod-6 prime sequences; the 5-series specificity claim weakens. *Note:* this reading is actually the *parsimonious* one (no specific structural content beyond monotone-vs-permuted), so this outcome is the more likely one a priori. |
| **\|z(33)\| ≥ 1.5 AND structured-ordering controls (reversed-size, every-other, index-interleaved) show z patterns matching the 5-series pattern (reversed-size matches natural; permuted controls do not)** | **Strongly favours Q1(d).** The monotone-vs-permuted distinction reproduces in a residue class with no tight-oscillation regime. |
| **\|z(33)\| ≥ 1.5 AND structured-ordering controls do NOT match 5-series pattern (e.g., reversed-size shows weaker z than natural in 7-series; or every-other shows comparable z)** | **Mixed — neither (b) nor (d) cleanly favoured.** A new reading — perhaps that monotone-orderings produce |z| anomalies but with residue-class-specific symmetry properties — is suggested. CinC interprets. |

### Anchors to reproduce (verification gates)

Before computing the 7-series test, Mr Code reproduces the 5-series benchmark anchors:

- **5-series Definition C** at n = 33: natural T = 13, shuffle mean ≈ 6.185, shuffle std ≈ 2.780, z ≈ 2.45.
- **5-series Definition A** at n = 90: natural z = 3.61.
- **5-series multi-window max-z empirical p (Definition C)** = 0.005 (5/1000).

If any 5-series anchor fails to reproduce within tolerance ±0.05 on z and ±0.005 on p, **HALT** and report.

### Expected output

A new script `v3_12_data/seven_series_monotone.py` and a results CSV `v3_12_data/results/seven_series_monotone_results.csv` with columns:

```
ordering, window_n, T_observed, T_shuffle_mean, T_shuffle_std, z, p_one_sided
```

with rows for ordering ∈ {natural, reversed_size, every_other, index_interleaved} × n ∈ {20, 33, 50, 70, 90, 100}.

A multi-window aggregate CSV `v3_12_data/results/seven_series_aggregate_null.csv`:

```
ordering, max_z_observed, max_z_null_95th, max_z_null_99p5th, empirical_p
```

A markdown summary at `v3_12_data/findings.md` (appended as "v1.1 Task 2 results"):

1. Anchor verification status.
2. Per-window z-scores for 7-series natural ordering.
3. Multi-window aggregate empirical p for natural vs structured orderings.
4. Direction-confirmation summary: which candidate (Q1(b) or Q1(d)) is favoured by |z(33)|.
5. Structured-ordering pattern comparison: does the 7-series reproduce the 5-series pattern (reversed-size matches; permuted does not)?
6. Falsifier-test result.

---

## Task 3 — Bootstrap SEs on §6.3 ratio table (NULL/STATUS)

### Question

What is the finite-sample standard error on each row of the §6.3 (formerly §6.5.3) tie-excess ratio table? Is the v3.16 supplementary directional bound "ratio ≤ 4.5 at N = 10⁷" computable as "above the SE on the next measurement," or only nominal?

### Why it matters

The §6.3 ratio table reports the 5-series tie-excess ratio T(N) / E[T_random_walk(N)] for 11 values of N ∈ {100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000}. Each ratio is a single observed count; no SE is published. Mr Adversary's v3.18 NULL/STATUS query observes that "5.18" at N = 500k is a single number, and the difference between, say, 5.18 and 5.30 at N = 10⁷ may be smaller than the finite-sample SD. The pre-registered falsifier "ratio ≤ 5.18 at N = 10⁷" requires the next measurement to be on the same precision footing as the existing one — that is, computable rather than nominal.

### Method

For each of the 11 rows of the existing §6.3 table (N values from 100 to 500,000):

1. Take the actual χ₅ sequence over the first N 5-series primes (size-ordered): a vector of ±1 values.
2. Bootstrap resample: B = 10,000 random permutations of the χ₅ vector (preserving the marginal +1/−1 balance). For each permutation, compute T(N) = number of zero-crossings of the running sum.
3. Compute the bootstrap distribution of T(N): mean, std, 95% CI (2.5th and 97.5th percentiles).
4. Bootstrap SE for the ratio: SE_ratio = std(T_bootstrap) / E[T_random_walk(N)].

For a comparison-relevant test:

5. For the v3.16 supplementary directional bound at N = 10⁷ ("ratio ≤ 4.5"), compute the bootstrap SE at N = 500k and extrapolate (with documented assumptions) to N = 10⁷ as a precision projection. Report the projection so that v1.2's eventual N = 10⁷ measurement can be compared cleanly.

### Pre-registered prediction (commit before computation)

**Bootstrap SE at large N**:
- At N = 500k, the random-walk expectation E[T] ≈ √(2N/π) × (some logarithmic factor); for the 5-series the published ratio is approximately 5.16 with T = 921. Under random shuffling of χ₅ values, T should be near √(2N/π) × correction, with relative SE on the order of 1/√T ≈ 3.3% × T ≈ 30 ties.
- **Predicted SE_ratio at N = 500k**: SE_ratio ∈ [0.05, 0.20] (ratio 5.16 ± 0.10ish).

**Computability of the v3.16 falsifier**:
- The falsifier "ratio ≤ 4.5 at N = 10⁷" should be ≥ 2 × SE below the published 5.16 baseline. With predicted SE_ratio ≈ 0.05–0.20 at N = 500k, the gap 5.16 − 4.5 = 0.66 is approximately 3–13 SE, depending on bootstrap variance.
- **Predicted: the v3.16 supplementary falsifier is *computable* under the bootstrap framework**, not nominal — the gap between the published baseline and the falsifier threshold is well above the SE.

### Falsifier on-record (binding before computation)

This task does not have a binary falsifier in the same sense as Tasks 1 and 2 (it is a precision-quantification task, not a hypothesis test). The pre-registered outcome is:

| Outcome | Reading |
|---------|---------|
| **All 11 SE_ratio values < 0.30** | The bootstrap framework gives well-defined precision per row; v3.16's supplementary "≤ 4.5" falsifier is computable. v1.1 reports the table with SE; the v3.16 falsifier is upgraded from nominal to computable. |
| **Some SE_ratio values ≥ 0.30** | Bootstrap precision is looser than expected at certain N. v1.1 reports the SE table and notes which falsifier-relevant rows have wider precision than assumed. Mr Adversary's NULL/STATUS query is partially answered (table now has SE) but the v3.16 supplementary falsifier may need re-stating with the actual SE in mind. |
| **Bootstrap procedure shows the χ₅ sequence is NOT well-modelled by random ±1 permutations** (e.g., bootstrap distribution non-Gaussian, heavy-tailed, or shows structural autocorrelation) | The bootstrap framework itself is questioned. v1.1 reports the issue and Mr Code halts before reporting SEs that may be misleading. CinC interprets and may queue a v1.2 task with a different null. |

### Anchors to reproduce (verification gates)

Before bootstrap, Mr Code reproduces:

- **N = 50,000 anchor**: published T = 921, ratio = 5.16. (From v3.11 §6.5.3 / Paper 199 v1.0 §6.3.)
- **N = 100 anchor**: bootstrap mean T should be approximately E[T_random_walk(N=100)] ≈ √(2·100/π) ≈ 7.98; the published natural T at N = 100 should be well above this (consistent with the ~3.6× ratio at N = 100 noted in Paper 199 §10 Q3).
- **All 11 published ratios** (the existing table) should reproduce within ±0.01.

If any anchor fails, **HALT**.

### Expected output

A new script `v3_12_data/persistence_bootstrap_se.py` and a results CSV `v3_12_data/results/persistence_bootstrap_se.csv` with columns:

```
N, T_natural, E_random_walk, ratio_natural, T_bootstrap_mean, T_bootstrap_std, ratio_bootstrap_mean, ratio_bootstrap_std, ratio_95_lower, ratio_95_upper
```

11 rows, one per N value. The columns `ratio_bootstrap_mean` and `ratio_bootstrap_std` are the new precision quantities.

A markdown summary at `v3_12_data/findings.md` (appended as "v1.1 Task 3 results"):

1. Anchor verification status.
2. The 11-row table with bootstrap SE per row.
3. Computability assessment of the v3.16 supplementary directional bound at N = 10⁷ ("ratio ≤ 4.5"): explicit SE-based gap from baseline 5.16 (or appropriate large-N value).
4. Bootstrap-distribution diagnostics: skewness, kurtosis, comment on Gaussianity per row.
5. Falsifier-table outcome: which row applies.

---

## Cross-cutting requirements

### Repository conventions

- All new scripts under `v3_12_data/` (continuation of v3.x work directory; the directory name does not change despite Paper 199 being v1.x — the scripts archive is one cumulative store).
- Seed scheme: `seed = trial × 137 + 42` (consistent with all prior Mr Code work).
- Python 3.11+ with `numpy`, `scipy`, `mpmath`. No new dependencies without CinC approval.
- Each script is self-contained: imports only from `prime_utils.py` (existing) and standard library; can be invoked as `python3 v3_12_data/<script>.py` from repo root.

### Output discipline

- Every CSV has a header row with column names matching this brief.
- Every script prints a structured summary to stdout: anchor-verification block, results block, falsifier-test block, and end-of-task status (PASS / HALT / FAIL).
- The `findings.md` updates are appended (not overwriting). The "v1.1 Task N results" section header marks the new content.
- Long scripts (over ~300 lines) are split into helper modules within `v3_12_data/`.

### Pre-registration commit

**Critical**: this brief is the pre-registration. Mr Code does NOT modify the brief's "Pre-registered prediction" or "Falsifier on-record" sections during execution. If the data falsify the prediction, that is the result. If anchors fail to reproduce, that is the result.

The pre-registered direction and falsifier are committed to git as part of the brief itself (this file at `v3_12_data/briefs/mr_code_brief_paper_199_v1_1.md` or similar) before the computation runs.

### Stop-on-fail (Pattern 75)

If any anchor verification gate fails:
1. Halt the task immediately.
2. Report the anchor name, expected value, observed value, and tolerance.
3. Do NOT proceed to the new computation.
4. Do NOT attempt to "fix" or "explain" the discrepancy — that is CinC's job.

### Reporting format

Each task's output is a single `findings.md` section plus the CSVs and the script. Mr Code's report back to CinC takes the form:

```
TASK N — STATUS

Anchor verification: PASS / HALT (with detail if HALT)
Pre-registered prediction direction: confirmed / refuted / inconclusive
Falsifier-test result: row [X] of the falsifier table applies
Numerical summary: [the key numbers, 3-5 lines]
Files produced: [list]
```

---

## Session order

CinC suggests the following order (parallelisable but commit each before next):

1. **Task 3 first** (bootstrap SEs) — fastest, no new sieve work, just bootstrap on existing data.
2. **Task 1 next** (independent moduli) — reuses correlated-null framework from v3.14.
3. **Task 2 last** (7-series monotone) — most novel; reuses v3.12 task1_orderings framework.

Each task ends with a stop-on-fail gate before the next begins. CinC reviews the Task N results before queueing Task N+1.

---

## What v1.1 will look like with these results

If all three tasks land cleanly:

- **Task 1 outcome incorporated into §5 / §8**: the §5 cyclotomic-split-bias section gains a paragraph reporting the 7-modulus correlated-null result; if joint p ≤ 0.05, Retraction 4 (mechanistic accumulation downgrade) is partially lifted (the directional pattern survives on independent moduli, even if the accumulation simulation remains marginal); if joint p > 0.05, Retraction 4 is sustained and the §5 framing remains "directional consistency, mechanism not established."

- **Task 2 outcome incorporated into §10 Q1**: the candidate-discrimination question is updated. If |z(33)| ≥ 1.5 for the 7-series, Q1(d) is favoured and Q1(b) weakened; if ≤ 1.0, the reverse. §10 Q1 gains a new candidate-status column reflecting the discrimination.

- **Task 3 outcome incorporated into §6.3**: the ratio table gains a "bootstrap SE" column; the v3.16 supplementary directional bound is upgraded from nominal to computable, with the explicit SE-relative gap stated.

A v1.1 cycle of Mr Adversary review (after CinC integrates these results) is the natural next step.

---

🐕☕⬡

*CinC + Mr Code + Mr Adversary + Mr Library = the partnership architecture of the 2I Programme. Each role scope-limited per Pattern 97. Pre-registration discipline (Pattern 19, 27) and stop-on-fail (Pattern 75) are non-negotiable.*
