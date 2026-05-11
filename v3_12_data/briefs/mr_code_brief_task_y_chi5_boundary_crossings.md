# Mr Code Brief — Task Y: χ₅ Running-Sum Behaviour at Mod-6 Prime Product Boundary Crossings

**Repository:** `github.com/CliffordKeeble/digit-gaps-mod6-primes`
**Working branch:** `paper-199-v1-1-data`
**Brief version:** v1.0 (pre-registration)
**Date:** 11 May 2026

🐕☕⬡

---

## Context

Paper 199 Observation 6.3 reports `S_5(31) = 0` at the step n = 30 → 31 that crosses the first staggered boundary (digit-length 59 → 62 in the 5-series mod-6 prime product). This task characterises the running-sum behaviour at the next three boundary-crossing primes to test whether the boundary→tie association is α-exhaustion-specific or generic.

Convention used in this task (matching Paper 199 v1.0 §6.1 / `task1_orderings.py` Definition A): `S_i(n) = Σ_{k=1}^{n} χ₅(p_{i,k})` where `p_{i,k}` is the k-th size-ordered prime of series i (5-series: p > 3, p ≡ 5 mod 6; 7-series: p > 3, p ≡ 1 mod 6). For the 5-series the first prime is the ramified p = 5 with χ₅(5) = 0 and contributes nothing to the sum.

## Pre-registered hypothesis

The χ₅ running-sum reset `S_i(n) = 0` is specific to **digital boundaries** (α-exhaustion at e^{α⁻¹} ≈ 10^{59.5}) and does NOT occur at **coincident boundaries** (lattice-tension at e^{184} ≈ 10^{80}).

Specifically:

| Crossing | Series | Post-crossing n | Scale | Predicted S |
|---|---|---|---|---|
| Staggered (already verified) | 5 | 31 | 10^{61} | = 0 |
| Coincident | 5 | 39 | 10^{80} | ≠ 0 |
| Staggered | 7 | 31 | 10^{63} | ≠ 0 (predict negative) |
| Coincident | 7 | 38 | 10^{80} | ≠ 0 (predict negative) |

The 7-series predictions are negative because Paper 199 §4 reports S₇ ties only at n = 4 and n = 26 in the first 5000 primes — the 7-series is in persistent drift toward negative values.

## Method

For each of the four crossings — (i = 5, n = 31), (i = 5, n = 39), (i = 7, n = 31), (i = 7, n = 38):

1. Compute the size-ordered series i primes up to a sieve limit sufficient to obtain at least n + 25 primes (to allow tie-search ±20).
2. Compute χ₅ values and the running sum array `S_i[k]` for k = 1..N.
3. Report exact `S_i(n)`.
4. Identify the **previous tie** k < n with `S_i(k) = 0` and the **next tie** k > n with `S_i(k) = 0`, both within ±20. Report the gap in primes.
5. Verify the digit-length of the running prime product crosses the named threshold at the named step (anchor check).

## Pre-registered decision tree

Committed before execution. The row selected is determined by the observed pattern.

| Pattern | Interpretation |
|---|---|
| Only `S_5(31) = 0`; the other three ≠ 0 | **Hypothesis confirmed.** Reset is α-exhaustion-specific. Paper 200's load-bearing claim — that the χ₅ reset is a digital-boundary signature, not a generic-boundary signature — is supported. |
| `S_5(31) = 0` AND `S_5(39) = 0`; 7-series both ≠ 0 | Reset is 5-series-specific. The mod-5 carrier resets; the mod-5-deficit carrier doesn't. Asymmetric reset — flag for structural explanation. |
| Some 7-series crossing also = 0 | 7-series has its own reset at one of its crossings. Unexpected; flag for CinC investigation. |
| All four = 0 | Generic boundary reset (mechanism-agnostic). Strongly supports a unifying framework across α-exhaustion and lattice-tension. |
| All four ≠ 0 (including `S_5(31)`) | Paper 199's known `S_5(31) = 0` was numerical coincidence. Framework needs major rework. (Unlikely — but pre-registered for honesty.) |

## Anchors to reproduce (verification gates)

- 5-series primes p₁..p₁₀ = (5, 11, 17, 23, 29, 41, 47, 53, 59, 71).
- 7-series primes p₁..p₁₀ = (7, 13, 19, 31, 37, 43, 61, 67, 73, 79).
- `S_5(31) = 0` (Paper 199 §6.3 anchor — load-bearing).
- 7-series first two ties at n = 4 and n = 26 (Paper 199 §4).
- Digit-length of 5-series prime product at n = 30 < 60; at n = 31 ≥ 62 (skip 60, 61 confirms staggered).
- Digit-length of 5-series prime product at n = 38 < 80; at n = 39 ≥ 80 (coincident step).
- Digit-length of 7-series prime product at n = 30 < 63; at n = 31 ≥ 63.
- Digit-length of 7-series prime product at n = 37 < 80; at n = 38 ≥ 80 (coincident step).

If `S_5(31) = 0` fails to reproduce, HALT.

## Deliverables

- Script `v3_12_data/task_y_boundary_chi5_sums.py`.
- CSV `v3_12_data/results/task_y_boundary_chi5_sums.csv` with columns: `series, crossing_type, n_post, digit_length_pre, digit_length_post, S_i_n, tie_prev_n, tie_prev_gap, tie_next_n, tie_next_gap`.
- Findings section appended to `v3_12_data/findings.md` as "v1.1 Task Y results" with the decision-tree row identified.

## Stop-on-fail (Pattern 75)

If `S_5(31) ≠ 0`, halt and report. Do not proceed with the new computations until CinC has reviewed the anchor failure.

## Pre-registration commit

This brief is committed to git as `v3_12_data/briefs/mr_code_brief_task_y_chi5_boundary_crossings.md` **before** `task_y_boundary_chi5_sums.py` runs. The "Pre-registered hypothesis" and "Pre-registered decision tree" sections are not modified during execution.

🐕☕⬡
