# Task 5 Pre-Registration — Instance-4 doubling-pattern test (Paper 3 v5.x)

**Date:** 11 May 2026 (committed before computation per Pattern 19/27)
**Brief:** `mr_code_brief_paper_3_v5_x_task_5.md` (parent, in ~/Downloads).
**Parent task chain:** v4.2 comparative tabulation (`e60bb5b`), v4.5
Tasks 1–4b (`b844639`, `340cb80`, `6ef2d59`, `345b97a`, `502b194`);
v4.9 Adversary cycle-5 ★★★★★ rating + sixth-star path.

## Layered structure (mirrors Task 4b)

### Layer 0 — Anchor verification (Pattern 75)

Re-verify under v5.x's larger N_MAX:
- Strict-23 [90, 200] cluster count = 23.
- Cluster containing d = 172: upper edge = 482 (instance 1 unchanged).
- Cluster containing d = 952: upper edge = 1717 (instance 2 unchanged).

Halt on any mismatch.

### Layer 1 — Instance-3 upper-edge completion (precondition, measurement)

Task 4b reported instance 3 as `(2812, ≥ 3740)` with the upper edge
truncated at D_HI = 3600. Layer 1 measures the actual upper edge of
the cluster containing d = 2812 within v5.x's extended D_HI.

Not pre-registerable as a falsifier (the truth value is the
measurement); load-bearing as precondition for Layer 2's ratio test.

If the cluster containing d = 2812 is *still* truncated at D_HI at
v5.x's N_MAX (i.e., upper edge = D_HI − 1 and `D_HI` ∈ skip set),
that triggers the **(γ-no-instance-3-completion)** outcome of
Layer 2.

### Layer 2 — Instance-4 detection + doubling-pattern test (BINDING)

After Layer 1 fixes instance-3's upper edge and width, test the
doubling-pattern hypothesis at instance-3 → instance-4.

**Reference (from v4.9 / Task 4b):**

| Regime | Bounded range | Width | Pre-regime gap |
|--------|---------------|-------|----------------|
| 1 | (172, 482) | 311 | — |
| 2 | (952, 1717) | 766 | 469 |
| 3 | (2812, ≥ 3740) | ≥ 929 (truncated) | 1094 |

Width ratio observed at instance-1 → instance-2: 766 / 311 ≈ 2.46.
Gap ratio observed at instance-2 → instance-3: 1094 / 469 ≈ 2.33.
**Empirical mean of the two ratios: ≈ 2.3×.** Binding hypothesis:
the doubling pattern continues at ratio 2.3× ± 10% at instance-3 →
instance-4 for both width and gap.

**10% windows (binding, committed before data inspection):**

- `width_ratio_window = [2.07, 2.53]` where width_ratio = width(4) / width(3).
- `gap_ratio_window = [2.07, 2.53]` where gap_ratio = gap(3→4) / gap(2→3) = gap(3→4) / 1094.
- Predicted `gap(3→4) ≈ 2.3 × 1094 = 2516`. Window: `[2264, 2768]`.
- Predicted `width(4) ≈ 2.3 × width(3)`. Window scales with width(3) from Layer 1.

**Pre-registered outcomes:**

- **(α) Doubling pattern empirically anchored.** Instance 4 detected
  within tested D_HI; **both** width_ratio AND gap_ratio land within
  the 10% windows ([2.07, 2.53]). The structural-pattern reading
  hardens substantially; sixth-star path landed.
- **(β-broken) Doubling pattern breakdown.** Instance 4 detected
  within tested D_HI; one or both ratios outside the 10% window.
  Honest naming of the breakdown — the empirical anchor moves from
  "doubling pattern at ≈ 2.3×" to whatever the data shows.
  Publication-strengthening per Mr Adversary's framing (either
  outcome).
- **(γ-1) Out-of-range consistent with gap-doubling.** Instance 4
  not detected; `D_HI < instance-3_upper_edge + 2264`. The doubling
  hypothesis is not refuted — instance 4 is predicted just above
  D_HI; Task 5b at higher N_MAX warranted.
- **(γ-2) Out-of-range refutes gap-doubling.** Instance 4 not
  detected; `D_HI ≥ instance-3_upper_edge + 2768`. The gap-doubling
  hypothesis is refuted in the direction of "accelerating spacing".
  Honest naming.
- **(γ-no-instance-3-completion)** Layer 1 fails — cluster containing
  d = 2812 still truncated at D_HI. Implies instance 3 width ≥
  D_HI − 2812; refutes the width-doubling hypothesis at instance-2 →
  instance-3 if D_HI − 2812 > 1.1 × 2.3 × 766 ≈ 1937 (i.e., width(3)
  ≥ 1937 → width(3) / width(2) ≥ 2.53 → outside window). Honest naming.

**Decision precedence:** Layer-1 outcome dictates first; if Layer 1
succeeds, Layer 2's α/β/γ split applies.

### Layer 3 — Asymptotic-density refinement at extended range (exploratory)

Re-run the three asymptotic forms (`1 − a/log(D)`, `1 − a/log²(D)`,
blend) against the extended per-decade table.

- **(α-Q4)** Substantive improvement: best adj R² ≥ 0.5 → simple
  asymptotic form holds at larger scales.
- **(β-Q4)** No improvement (best adj R² < 0.5) → Task 4b's reading
  preserved; alternating saturated stretches remain the operative
  structural object.

## Operational parameters (committed)

- **N_MAX = 4000** (stretch goal per brief §2). Default
  recommendation was 2000; selecting 4000 to resolve Layer 2 in a
  single run without (γ-1) ambiguity at instance-4's predicted lower
  edge ~7090. Runtime cost manageable (estimated ≤ 5 minutes).
- **D_HI** determined at runtime as `(min(D_5(N_MAX), D_7(N_MAX))
  − 50) // 100 × 100`. Expected D_HI ≈ 14000 at N_MAX = 4000. Halt
  if D_HI < 5000 (insufficient extension over Task 4b's 3600).
- **Detection criteria (carried from Task 4b, validated):**
  - `d_lo ≥ 200` (exclude small-N baseline noise band).
  - `width ≥ 100` (minimum width to count as merged regime).
  - both edges bounded — upper edge must be a true landing point,
    not D_HI truncation.
- **Pattern-N defensive 95% mode-frequency check:** carried forward
  from Task 3 as operational depth (no convention distribution here,
  so this check is structurally inapplicable; noted for completeness).
- **Bin width = 100** for per-decade table (consistent with Tasks 4
  and 4b).

## Auxiliary measurement (not pre-registered)

For each detected merged regime, record which series (5 or 7) lands
*first* at the regime's upper edge — i.e., for upper edge X, find the
smallest n with D_i(n) = X + 1 for i ∈ {5, 7}, and identify which i
has the smaller n. (Or equivalently, identify the series whose
landing at X + 1 was the first to occur as n grows.)

Connects to §8 Q5's χ_5 structure question. Recorded as data; no
hypothesis pre-registered.

## Stop-on-fail

Per Pattern 75:
- Anchor mismatch in Layer 0 → halt.
- Layer 2 outcome not in {α, β-broken, γ-1, γ-2,
  γ-no-instance-3-completion} → halt (e.g., multiple instance-4
  candidates, or a regime detected with width or boundary structure
  inconsistent with the four detected so far).

Per Pattern N (calibrate-on-execution-surprise):
- If a structural surprise emerges in Layer 1 or Layer 2 that's
  surface-legitimate but suggests a refinement of the
  detection-criteria or ratio framing (e.g., a 4th regime that
  satisfies the criteria but has anomalous boundary shape), report
  literal outcome AND flag the refinement candidate for CinC.

## Auto-narrative discipline

Per Task 4 / Task 4b pattern: the script writes fact-only summaries
(tables, fit values, outcome row applied). Manual structural
observations live in `task5_summary.md` outside the auto-generated
zone, written post-run.

## Outputs

- `v3_12_data/briefs/task5_instance_4_doubling_pre_registration.md`
  (this file)
- `v3_12_data/task5_instance_4_doubling.py`
- `v3_12_data/results/task5_instance_4_doubling_per_decade.csv`
- `v3_12_data/results/task5_merged_regimes_detected.csv`
- `v3_12_data/results/task5_density_measurement.png` (extended chart;
  detected merged regimes shaded)
- `v3_12_data/results/task5_summary.md`

Commit on branch `paper-3-v5-x-data`. Push to origin.

— CinC + Mr Code, 11 May 2026
🐕☕⬡
