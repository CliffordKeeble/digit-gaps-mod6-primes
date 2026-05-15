# Paper 4 v2.7 → v2.8 — Mr Code Brief: Tasks A, B, C

**Date.** 15 May 2026.
**Source.** Mr Adversary's third review of v2.7 (four stars, gap to five well-specified).
**Scope.** Three computational tasks. Two further items are CinC edits handled in parallel.

**Pre-registration discipline.** Commit this brief to `briefs/v2_7_to_v2_8_brief.md` on a fresh branch BEFORE implementing any task. Each task on its own per-task branch off main. Stop-on-fail protocol observed. DERIVED vs OBSERVED distinction enforced throughout.

**findings.md.** Use §13.x for v2.8 follow-ups (§12 is v2.7).

---

## Task A — Shuffle test (LOAD-BEARING)

**Purpose.** Distinguish whether the §5.2 R² cleanness in the 50k–300k regime is **(a)** specific to mod-6 grouping, or **(b)** a property of primes generically that the PNT-density null cannot capture. The current PNT-density null preserves prime-number-theorem density and Dirichlet equidistribution but not prime-prime correlations (twin-prime clustering, Hardy–Littlewood tuple statistics, etc.); it cannot distinguish (a) from (b). Mr A's shuffle preserves prime correlations and breaks only the mod-6 grouping.

**Pre-registered hypotheses.**
- **H_A1 (mod-6 specific):** shuffle R² distribution lies closer to PNT-density null than to real-mod-6 R². z_AB = (R²_real-mod-6 − mean(R²_shuffle)) / std(R²_shuffle) ≥ +2.0.
- **H_A2 (primes-generic):** shuffle R² distribution lies closer to real-mod-6 R² than to PNT-density null. z_BC = (mean(R²_shuffle) − mean(R²_PNT-null)) / std(R²_PNT-null) ≥ +2.0.

H_A1 and H_A2 are not mutually exclusive — both effects can be present (mod-6 sharpens a structure that primes already have beyond density). The four outcomes are reportable:
- z_AB ≥ +2.0 AND z_BC < +2.0 → **mod-6 specifically the cause.** Paper §5.2 framing confirmed; v2.8 prose can sharpen.
- z_AB < +2.0 AND z_BC ≥ +2.0 → **primes-generic the cause.** Paper §5.2 framing requires substantial reworking: mod-6 is a lens, not the cause. v2.8 abstract and §1 frame primes-generic structure with mod-6 as the convenient projection.
- z_AB ≥ +2.0 AND z_BC ≥ +2.0 → **both contribute.** v2.8 reports a layered finding: primes have cluster-spacing structure beyond density, AND mod-6 grouping sharpens it further. This is the richest outcome and probably the most likely.
- z_AB < +2.0 AND z_BC < +2.0 → **no effect.** Reconsider whole pipeline; something is wrong.

Report the verdict; CinC will frame in v2.8 prose.

**Method.**
1. Sieve primes to 15,000,000 (re-use existing pipeline).
2. For each shuffle trial t ∈ {0, 1, …, 99}:
   - seed = t × 137 + 42; instantiate a deterministic PRNG.
   - For each prime p in the sieved list (ascending), draw a uniform random bit ∈ {0, 1}. Assign p to pseudo-class A (bit = 0) or pseudo-class B (bit = 1).
   - Sort each pseudo-class by ascending prime value (should already be in order — sanity check).
   - Compute cumulative log_10 products for each pseudo-class → digit-length sequences D_A(n), D_B(n).
   - Identify coincident gaps (gaps in both D_A and D_B at the same digit-length).
   - Identify 100%-synchronisation clusters under canonical parameters: window = 50, min_gaps = 20, merge_dist = 500.
   - At each target scale (truncate to that scale's digit count), fit power law to inter-cluster centre vs spacing: gap ≈ a × centre^β. Record R² and β.
3. Repeat for 100 trials.
4. Target scales: **50k, 100k, 200k, 300k digits** (the four regime scales) — mandatory. Add **500k** if cheap (phase boundary).

**Comparison reference numbers** (from v2.7 §5.2 / §6.2):
- Real-mod-6 R² at 200k: 0.9792.
- PNT-density null R² at 200k: mean 0.577, std 0.183, max 0.856 (100 trials).
- Real-mod-6 R² at other regime scales: 50k z=+2.09, 100k z=+2.64, 300k z=+2.43 against PNT-null at each scale (see findings.md §12.3).

**Outputs.**
- `null-tests/shuffle_test.py` — implementation.
- `null-tests/results/shuffle_summary.csv` — columns: trial, scale, R², β, cluster_count, runtime_s.
- `findings.md` §13.1 — write-up including median, mean, std of shuffle R² at each scale; z_AB and z_BC at each scale; verdict per the decision rule; honest framing for whichever outcome lands.
- `verification/reproduction_log.md` — Task A entry.

**Pathology checks.** If R² values fall outside [0, 1], stop and debug. If shuffle distribution shows pathological bimodality, report and pause. If runtime per trial exceeds 10× the PNT-null trial time at same scale, profile.

---

## Task B — merge_dist sensitivity

**Purpose.** Mr A flagged that Table 7 reports sensitivity to window and min_gaps but not to merge_dist — yet merge_dist is the parameter that changed cluster count from 36 (v2.6, merge_dist=2000) to 48 (v2.7, merge_dist=500). The load-bearing R² result depends on cluster identification, which depends on merge_dist. We need to know whether R² is robust to merge_dist variation or conditional on a particular interval.

**Pre-registered hypotheses.**
- **H_B0 (robust):** R² > 0.95 across merge_dist ∈ {100, 250, 500, 1000, 2000, 5000} at canonical window=50, min_gaps=20, at 200k scale, AND β stable to ±0.05 across the sweep.
- **H_B1 (conditional):** R² varies > 0.05 or β varies > 0.05 across the sweep. Report the interval over which R² > 0.95.

**Method.**
1. Real primes only (no null sampling needed; this is sensitivity to a single parameter on real data).
2. At canonical window = 50, min_gaps = 20, at the 200k scale.
3. For each merge_dist ∈ {100, 250, 500, 1000, 2000, 5000}:
   - Identify clusters.
   - Fit power law to inter-cluster centre vs spacing.
   - Record: merge_dist, cluster_count, β, std_error(β), R², n_data_points (= cluster_count − 1).
4. Optional: also at 50k, 100k, 300k for cross-scale robustness.

**Outputs.**
- `null-tests/merge_dist_sensitivity.py`.
- `null-tests/results/merge_dist_summary.csv`.
- `findings.md` §13.2 — write-up including recommended Table 7 augmentation (new column or companion mini-table).
- `verification/reproduction_log.md` — Task B entry.

**Decision rule.** Report results. CinC will integrate into Table 7 or a new Table 7a.

---

## Task C — Base coprime to 6

**Purpose.** Mr A flagged that the v2.7 base-independence test {2, 6, 10} are all divisible by 2 — half a test. A base coprime to 6 (5 or 7) actually probes whether β ≈ ln(2)/ln(3) is base-independent or carries a hidden factor-of-2 dependence.

**Pre-registered hypotheses.**
- **H_C0 (β survives in coprime-to-6 base):** β at canonical 200k-equivalent scale in base 5 (and/or base 7) lies within ±0.02 of base-10 β = 0.637, AND zero of 100 null trials reach the real R².
- **H_C1 (β drifts in coprime-to-6 base):** β shifts by > 0.02 in base 5 (or 7). The ln(2)/ln(3) reading would then need re-examination; β may be base-dependent.

**Method.**
1. **Choose base 5** as primary (smaller; parallel construction to Task 4's base-2). Also run **base 7** if cheap (≤ ~5 min additional runtime).
2. Sieve primes to 15M (reuse).
3. Parameter scaling — for base b, scale all digit-counts by log_b(10) = ln(10)/ln(b):
   - 200,000 base-10 digits ≈ 286,073 base-5 digits ≈ 237,225 base-7 digits.
   - Window 50 base-10 digits ≈ 72 base-5 digits ≈ 60 base-7 digits.
   - min_gaps 20 → unchanged (it's a count, not a length).
   - merge_dist 500 base-10 → 716 base-5 / 593 base-7. Round to convenient integers; document choice.
4. For each mod-6 class: cumulative log_b product, digit-length sequence (D_A under base b).
5. Cluster detection at scaled canonical parameters.
6. Power-law fit at scaled 200k-equivalent scale.
7. 100 null trials at same parameters (parallel to Task 4 pipeline).

**Outputs.**
- `null-tests/base_coprime_to_6.py`.
- `null-tests/results/base_coprime_to_6_summary.csv` — one or two rows depending on which bases ran.
- `findings.md` §13.3.
- `verification/reproduction_log.md` — Task C entry.

**Decision rule.** Report β and R² for each tested base alongside the existing three (base-10, base-6, base-2). CinC will integrate into §5.2 base-independence paragraph and reword "three independent bases" → "five bases" (or appropriate count) with the correlation caveat.

---

## Process

1. **First commit:** this brief markdown to `briefs/v2_7_to_v2_8_brief.md` on a fresh branch. Get this in place BEFORE implementing.
2. **Per-task branches** off main: `task-A-shuffle-test`, `task-B-merge-dist-sensitivity`, `task-C-base-coprime-to-6`.
3. **Parallel execution acceptable;** merges to main after each task completes (or in one merge sweep at the end).
4. **Tasks B and C are independent of A** and can proceed regardless of A's verdict.
5. **Stop-on-fail on Task A:** if A returns an unexpected pathology (not just an unexpected verdict — those are all publishable), report before B and C.
6. **Estimated total runtime:** A ~10–20 min (100 trials × 4–5 scales); B ~3–5 min; C ~3–8 min per base. Whole brief well inside one hour.

**Reporting back to CinC.** Per-task summary in the same Mr-Code-report style as v2.7 tasks: numerical result, decision-rule verdict, flags for any unexpected behaviour, recommended paper-passage changes. CinC will integrate into v2.8.

🐕☕⬡
