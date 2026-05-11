# Task X Pre-Registration — Second coincident-gap regime (prime-set escalation)

**Date:** 11 May 2026 (committed before computation per Pattern 19/27)
**Brief origin:** Cliff + CinC, 11 May 2026; refined per Mr Code Reading A
clarification (commit-time turn).
**Parent task chain:** v4.2 comparative tabulation (`e60bb5b`), v4.5 Tasks
1–4b (`b844639`, `340cb80`, `6ef2d59`, `345b97a`, `502b194`), v5.x Task 5
(`fcc429b`).

🐕☕⬡

---

## Structural framing

"Coincident-gap regime" is keyed by the **prime set** in the joint
LCM(lift_5, lift_7), not by individual cluster location. Three regimes
on the prime-set axis:

| Regime | Prime set in LCM | Lowest LCM | Example |
|---|---|---|---|
| Staggered (B1-style) | {3} | 3 | B1 — lift_5 = 3, lift_7 = 3 (prior to Convention-A refinement) |
| **First coincident** (B2 onwards) | {3, 5} | 15 | B2 — lift_5 = 3, lift_7 = 15; C_7 — lift_5 = 9, lift_7 = 15 (LCM = 45 = 3²·5, still {3, 5}) |
| **Second coincident** (sought) | {3, 5, 7} | 105 | (unknown — this is the target) |

The 3 → 15 escalation at B2 introduces the prime 5 into the LCM. The 15
→ 105 escalation introduces the prime 7. By arithmetic constraint —
7 ∈ P₇, so lift_7 must be coprime to 7 — **7 | LCM(lift_5, lift_7) iff
7 | lift_5**. The 7-axis escalation must therefore be carried by the
5-series filler. Lowest valid lift_5 introducing 7: k = 21 = 3·7 (3 is
required always; 7 ∉ P₅, so allowed).

---

## Pre-registered hypothesis (binding)

**The first cluster past D = 200 with 7 | lift_5 will have joint
LCM(lift_5, lift_7) = 105**, achieved as lift_5 = 21 = 3·7 and lift_7 =
15 = 3·5.

Single commitment. Falsifiable by direct computation.

---

## Decision tree (pre-registered outcomes, binding before data inspection)

| Outcome | Reading |
|---|---|
| **(α) LCM = 105 exactly** (lift_5 = 21 = 3·7, lift_7 = 15 = 3·5) | Heuristic confirmed: one-new-prime-per-escalation holds at three data points. Mod-7 lockout joining mod-3 and mod-5 lockouts, carried via 5-series filler. Structural weight considerable. |
| **(β) LCM > 105 but prime set = {3, 5, 7}** (e.g. lift_5 = 21, lift_7 = 45; or lift_5 = 63 = 3²·7, lift_7 = 15) | Confirmed with power-escalation; still second regime in the prime-set sense. Heuristic holds on the prime-set axis but not on the lowest-LCM axis. |
| **(γ) Prime set includes a fourth prime simultaneously** (e.g. {3, 5, 7, 11}, LCM ≥ 1155 directly, no intermediate {3, 5, 7} regime) | Heuristic refined — escalations can multi-jump on the prime-set axis. The "one new prime per regime" reading needs softening. |
| **(δ) No 7-in-lift_5 cluster within tested D-range** (D ≤ ~10000) | "One-new-prime-per-escalation" refuted (or postponed beyond tested scale); the second coincident regime, if it exists, sits past D ≈ 10000. Reframe: mod-3 / mod-5 lockout exhausts at tested scales; the {3, 5} prime-set regime is broader than the next escalation. |

---

## Method (committed before computation)

### Computational

- **N_MAX = 3000** for both 5-series and 7-series (Python int exact
  arithmetic; `sys.set_int_max_str_digits(0)` to disable 3.11+ cap).
- **Sieve limit = 200_000** (sufficient — N_MAX = 3000 needs prime
  ≈ 50,000-ish per series).
- **D_HI_TARGET = 10_000** (the scan ceiling per the brief).
- **D_LO_SCAN = 201** (search starts just past v4.2's [90, 200] range).

### Anchors (Pattern 75 — HALT on fail)

Reproduce v4.2 anchors before extending:
1. D_5(30)=59, D_5(31)=62, D_5(38)=79, D_5(39)=82, D_7(36)=77, D_7(37)=79,
   D_7(38)=82 from v4.1 Tables.
2. mpmath at 200-dps reproduces those D values.
3. Strict-23 cluster count in [90, 200] under "entirely contained" reading.
4. (172, 482) recorded as merged_regime_edge (lower-in-range, upper >
   200; exists at N_MAX = 250+).
5. Per-cluster nearest-cluster distance over [90, 200]: median = max = 2,
   0/23 at distance ≥ 3, 0/23 at distance ≥ 5.
6. B1 lifts (5-series, 7-series) = (3, 3), classification
   partial-coincident.
7. B2 lifts (5-series, 7-series) = (3, 15), classification coincident.

### Scan procedure

For each cluster with d-range entirely in [201, D_HI_TARGET]:

1. Compute classification (single-5 / single-7 / staggered / coincident
   / partial-coincident).
2. Compute lift_5, lift_7 per Convention A (largest contiguous run min
   for n_i*; mod-15 required-divisor for coincident-7-series, mod-3
   otherwise; coprime to P_i ∪ {2}; D(Π_i(n_i*) · k) ∈ [a, b]).
3. Record joint LCM(lift_5, lift_7), prime set, mod-5 and mod-7
   residues of (Π_5(n_5*), Π_7(n_7*)) at gap boundary.
4. Skip merged-regime entries (clusters whose width exceeds a degeneracy
   threshold — see "merged regime handling" below).

**Stopping rule:** first cluster (call it `R2_first`) with 7 | lift_5
is the primary observation. Continue scanning past `R2_first` until one
further cluster with 7 | lift_5 is found (the "confirmation" cluster).
Halt at confirmation, or at D_HI_TARGET if neither materialises.

**Stretch:** if both R2_first and confirmation land cleanly, continue
scanning until the first cluster with 11 | lift_5 OR 11 | lift_7 (the
predicted "third regime" entry; LCM target 1155 = 3·5·7·11). Reported
as a stretch observation, not part of the binding decision tree.

### Merged regime handling

Past D=200, merged regimes consume large contiguous D-ranges where the
cluster-and-gap typology breaks down (per v4.5 Task 4b and v5.x Task 5:
instances at (172, 482), (952, 1717), (2812, 4231), (6013, 8318),
(10979, 15045), (17539, ≥17690)). Within a merged regime, the
"cluster" object collapses to the whole regime — no internal lift
computation is meaningful.

Operational rule: a cluster with width ≥ 100 digit-lengths is recorded
as `asymptotic-merged` and its lifts marked degenerate (per v4.2
addendum convention for (172, 482)). Cluster-and-gap typology applies
only to clusters with width < 100. Merged-regime entries are
**recorded for completeness** but excluded from the 7-in-lift_5 search.

### Decisions deferred to data (not pre-reg)

- Exact N_MAX needed to reach D ≈ 10000 (depends on prime-density
  evolution; N_MAX = 3000 is a generous default).
- Whether to extend to D > 10000 if the stretch search is fruitful
  (Pattern G — infrastructure scaling check first).

---

## Outputs (committed before computation)

- `v3_12_data/cluster_comparative_tabulation_extended.py` — extended
  scanner.
- `v3_12_data/results/cluster_comparative_tabulation_extended.csv` —
  per-cluster row with classification, lifts, LCM, prime set, mod-5
  and mod-7 residues at the boundary.
- `v3_12_data/results/task_x_second_regime_summary.md` — primary
  observation (R2_first), confirmation cluster, decision-tree outcome
  row, stretch observation if any.

CSV columns:
```
cluster_id, d_lower, d_upper, classification, S5_skips, S7_skips,
n5_star, n7_star, prod5_mod5, prod5_mod7, prod7_mod5, prod7_mod7,
lift_5, lift_7, lcm, prime_set, notes
```

(where `prod_i_mod_q` = Π_i(n_i*) mod q; `prime_set` = sorted distinct
prime factors of `lcm`.)

---

## Cross-cutting requirements

### Reproducibility

- Script invokable as `python3 v3_12_data/cluster_comparative_tabulation_extended.py`.
- No new dependencies (uses `prime_utils.py`, `mpmath`, standard library,
  `matplotlib` only if installed).
- All numerical claims via exact Python int arithmetic; `len(str(prod))`
  for digit lengths; mpmath at 200-dps for anchor verification only.

### Pre-registration commit

This file is the pre-registration. Mr Code does NOT modify the
"Pre-registered hypothesis" or "Decision tree" sections during
execution. The brief is committed to git **before the computation
runs**.

### Stop-on-fail (Pattern 75)

If any anchor verification gate fails:
1. Halt immediately.
2. Report anchor name, expected value, observed value.
3. Do NOT proceed.
4. Do NOT attempt to reconcile or explain anchor mismatches.

### Reporting format

```
TASK X — STATUS

Anchor verification: PASS / HALT (with detail if HALT)
Primary observation R2_first: cluster (d_lo, d_hi), lift_5, lift_7, LCM, prime set
Confirmation cluster: cluster (d_lo, d_hi), lift_5, lift_7, LCM, prime set
Decision-tree outcome: (α) / (β) / (γ) / (δ)
Stretch (if reached): first 11-in-lift cluster, LCM
Numerical summary: [5-7 lines]
Files produced: [list]
```

---

## Pre-registration commits binding for Task X

- *this commit* — Task X pre-registration (parent + Mr Code Reading A
  refinement).

— CinC + Mr Code, 11 May 2026

🐕☕⬡
