# Mr Code Brief — Paper 3 v4.1 → v4.2

**Target:** Paper 3 v4.2
**Source:** Paper 3 v4.1 (Mr Adversary v4.0 surgical items absorbed; v4.2 cluster tabulation queued)
**Repository:** `github.com/CliffordKeeble/digit-gaps-mod6-primes`
**Working directory:** `v3_12_data/` (continuation; the v3.x data directory remains the cumulative archive)
**Brief version:** v1.0 (initial)
**Date:** 10 May 2026

🐕☕⬡

---

## Role-card

Mr Code is the implementation specialist for the 2I Universe Programme (Pattern 97). Scope-limited to: **executing pre-registered computations and reporting numerical results faithfully**. Out of scope: changing the pre-registered direction or falsifier; deciding whether a claim survives; rewriting the paper's framing; making interpretive judgments. CinC owns interpretation; Mr Adversary owns review; Mr Library owns publication.

**Stop-on-fail protocols (Pattern 75).** If a published anchor fails to reproduce bit-exactly (within documented tolerance), Mr Code halts and reports the discrepancy *without* proceeding. Mr Code does not attempt to reconcile or explain anchor mismatches.

**Pre-registration discipline (Pattern 19, 27).** This brief contains the pre-registered direction and falsifier for the single task below. Mr Code does NOT modify these during execution. If the data falsify the prediction, that is the result.

---

## Background

Paper 3 v4.0's Mr Adversary review identified one substantive **GAP / NULL** item that holds the fifth star:

> "Your claim in §6 and §7, post-retraction, is that boundaries 1 and 2 are distinguished from later clusters by staggered/coincident structure and by the factor 3 → 15 lifting pattern. §8 Q1 honestly flags that recurrence of these features at later clusters is an open empirical question. I respect the honesty. But you have already enumerated 24 clusters in D ∈ [90, 200] for the per-cluster-distance computation that supported Retraction 2 — adding two columns to that table (staggered-vs-coincident classification, and minimum-lift factor) is, on my reading, a one-session computation. Without it, the structural-distinction reading rests on two data points. With it, you would either (a) confirm that {3, 3, 3, 15} is unusual among the 24+ later clusters, in which case the structural claim hardens considerably; or (b) discover that factor-15 lifts and coincident structures recur often, in which case a third retraction is honestly indicated. Either outcome is a publication strengthener."

The task below produces that comparative tabulation, with pre-registered outcomes (α) or (β) committed before the data are inspected.

This brief contains a **single task**. v4.2 of Paper 3 ships when this task lands.

---

## Task — Comparative cluster tabulation across D ∈ [90, 200]

### Question

For each of the 24+ clusters in the digit-jump structure of (Π₅, Π₇) across D ∈ [90, 200], record:
1. **Series presence:** does the cluster cover digit-lengths skipped by the 5-series only, the 7-series only, or both?
2. **Staggered vs coincident:** if both series skip into the cluster's d-range, do they skip *the same* digit-lengths (coincident) or *different* digit-lengths within the cluster (staggered)?
3. **Minimum-lift factor:** for each (cluster, series) pair where the cluster covers digits the series skips, compute the smallest positive integer k satisfying:
   - k is coprime to the active-constraint set of the series (Lemmas 4 / 5 generalised);
   - k satisfies the natural divisibility constraint for "fillable integer" at this cluster (divisible by 3 always; additionally divisible by 5 if the series is 7 and the cluster covers a digit-length where Π₇(n)·k ≡ 0 mod 5 is required by the gap geometry);
   - D(Π_i(n_i)·k) lies in the cluster's d-range, where n_i is the largest n with D_i(n) below the cluster.

Tabulate with these new columns alongside the v3.14 per-cluster nearest-distance data.

### Why it matters

The §6 framing of Paper 3 v4.1 claims that staggered/coincident structure and the 3 → 15 factor-escalation are *structural distinguishing features* of boundaries 1 and 2. This claim currently rests on n = 2 data points. Mr Adversary correctly observes that the 24-cluster enumeration already exists from `v3_12_data/isolated_threshold.py` (which supported Retraction 2), and adding two columns produces a 24-point empirical distribution against which the claim either hardens or falsifies.

### Method

**Step 1 — Reproduce the v3.14 cluster enumeration.**

Load or recompute the cluster list from `v3_12_data/isolated_threshold.py` (or its underlying digit-jump computation). The cluster definition (per v3.14):

> For each digit-length d ∈ ℕ, mark d as *skipped* if D_i(n+1) − D_i(n) ≥ 2 for either series i ∈ {5, 7} and d lies in the skipped range. Form maximal contiguous runs of skipped d-values as *clusters*.

Restrict to clusters with d-range entirely contained in [90, 200]. Boundaries 1 (60–63) and 2 (80–81) are recorded separately for comparison; they are NOT counted in the [90, 200] sample.

**Step 2 — Series-presence classification.**

For each cluster C with d-range [a, b]:
- Mark C as **5-series-active** if there exists n with D_5(n) < a and D_5(n+1) ≥ a, with D_5(n) jumping over some digit-length in [a, b].
- Mark C as **7-series-active** if the analogous statement holds for the 7-series.
- A cluster is **single-series** if exactly one of the above; **dual-series** if both.

**Step 3 — Staggered vs coincident classification (for dual-series clusters only).**

For a dual-series cluster C with d-range [a, b]:
- Identify the specific digit-lengths the 5-series skips within [a, b]: $S_5(C) = \{d \in [a,b] : d \text{ is skipped by Π}_5\}$.
- Identify the specific digit-lengths the 7-series skips within [a, b]: $S_7(C)$.
- **Coincident** if $S_5(C) = S_7(C)$ (both series skip exactly the same digit-lengths within the cluster).
- **Staggered** if $S_5(C) \neq S_7(C)$ (the two series skip different digit-lengths within the cluster, but the skips form a single contiguous cluster overall).
- Edge-case: if $S_5(C) \cap S_7(C) \neq \emptyset$ but $S_5(C) \neq S_7(C)$, classify as **partial-coincident** (some shared, some staggered).

**Step 4 — Minimum-lift factor.**

For each (cluster C, series i) pair where C is i-series-active:

Let $n_i^{\,*}$ be the largest n with D_i(n) below the lower edge of C (i.e., the prime-index just before Π_i jumps into or over C). The lift question: what is the smallest positive integer k such that

(a) k is coprime to the active-constraint set of series i: $k \notin (\text{primes} \in P_i) \cup \{2\}$ for a prime k, or for composite k all prime factors avoid $P_i \cup \{2\}$;

(b) k satisfies the appropriate divisibility constraint (the "natural" filler condition, generalising Lemmas 4 / 5):
  - **Always:** $k \equiv 0 \pmod{3}$ (every digit-jump filler must be divisible by 3 — both series products are coprime to 3 by Lemmas 2, 3);
  - **Additionally for 7-series at coincident clusters covering 5-divisible digit-position regions:** $k \equiv 0 \pmod{5}$ — required when the gap geometry forces $\Pi_7(n_7^*) \cdot k$ to land on a digit-length where the 5-residue is constrained; specifically, when the cluster's d-range demands a k that, multiplied by Π₇'s mod-5 residue, gives a fillable integer with mod-5 = 0;

(c) $D(\Pi_i(n_i^*) \cdot k) \in [a, b]$ (the lifted product lands in the cluster).

Enumerate k ∈ {1, 2, …, 100} (matching the Proposition 1 / Proposition 2 enumeration range); report the minimum k satisfying (a)–(c). If no k ≤ 100 satisfies all three conditions, report "none ≤ 100" and extend the search to k ≤ 1000.

For 5-series clusters: the "always" mod-3 condition holds; mod-5 is automatic since 5 ∈ P₅ (so k can be coprime to 5 without affecting the mod-5 = 0 status of Π₅·k).

For 7-series clusters: mod-3 holds; mod-5 is required only for clusters where the gap geometry demands it (the analogue of boundary-2's k = 15 requirement). Most clusters will not require mod-5 = 0; the test is whether minimum k > 3 occurs at clusters where it does.

**Step 5 — Tabulate.**

Produce a single table covering all clusters (including boundaries 1 and 2 for direct comparison):

| Cluster ID | d-range | Series presence | Staggered/Coincident | 5-series min lift | 7-series min lift | Notes |
|------------|---------|-----------------|----------------------|-------------------|-------------------|-------|
| Boundary 1 | 60–63   | dual            | staggered            | 3                 | 3                 | (anchor) |
| Boundary 2 | 80–81   | dual            | coincident           | 3                 | 15                | (anchor) |
| C_3 (first cluster in [90, 200]) | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... |

### Pre-registered prediction (commit before computation)

**Heuristic basis for prediction.** The factor-15 requirement at boundary 2's 7-series arises because the gap geometry there forces a lift that must hit both mod-3 = 0 and mod-5 = 0. In general, mod-5 = 0 is required for the 7-series filler only when the cluster sits at a digit-position where Π₇'s mod-5 residue × k mod 5 is constrained by the lift target. For most cluster geometries, k = 3 will suffice (the smallest valid lift coprime to the active-constraint set is usually 3, since the gap is 1–2 digits and a factor-3 lift adds approximately 0.477 to log₁₀, generally enough to cross a 1-digit gap without requiring mod-5 alignment).

Coincident clusters (both series skip the same digit-lengths) require *both* prime densities to align at the same scale. As n grows, the asymptotic densities of 5-series and 7-series gaps follow (different) prime-counting laws; coincidence at any specific cluster is geometrically infrequent.

**Pre-registered prediction:**

- **Most clusters in [90, 200] are single-series or staggered-dual; coincident-dual is rare.** Specifically: out of the ~24 clusters expected in [90, 200], at most 3 are coincident-dual (≤ 13%). The rest are either single-series (covering only 5-series or only 7-series skips) or staggered-dual (both series skip into the cluster's range but at different specific digit-lengths).

- **Most 7-series minimum lifts are k = 3.** Specifically: out of all (cluster, 7-series) pairs in [90, 200], at most 4 require k > 3 (≤ ~15% of 7-series-active clusters). The factor-15 lift at boundary 2 is one of the few cluster geometries forcing mod-5 = 0; later clusters, with larger Π_7(n) magnitudes, generally allow k = 3 to bridge the gap.

- **The {3, 3, 3, 15} pattern at boundaries 1 and 2 is unusual.** Specifically: at most 1 cluster in [90, 200] reproduces a (5-series lift = 3, 7-series lift = 15) pattern (coincident or otherwise); and the staggered → coincident transition between consecutive clusters (the structural transition between boundaries 1 and 2) does not recur in [90, 200].

### Falsifier on-record (binding before computation)

| Outcome | Reading |
|---------|---------|
| **(α) ≤ 3 coincident-dual clusters in [90, 200] AND ≤ 4 clusters with 7-series lift > 3 AND no recurrence of the staggered → coincident transition between consecutive clusters** | **Pre-registered prediction confirmed.** The {3, 3, 3, 15} pattern at boundaries 1 and 2 is unusual among the 24+ later clusters. Paper 3 v4.2 §6 retains and strengthens the structural-distinguishing-features framing; this is the (α) outcome of the v4.1 forward commitment. |
| **(β) > 6 coincident-dual clusters in [90, 200] OR > 6 clusters with 7-series lift > 3 OR factor-15 lifts recurring at ≥ 3 distinct later clusters** | **Pre-registered prediction falsified — Retraction 3 indicated.** The structural-distinguishing-features framing is withdrawn. Paper 3 v4.2 §6 is reframed as "we analyse the first cluster on its own terms" with structural claims restricted to the from-1, first-encountered, exhaustive-enumeration content of §4–§5; the staggered/coincident transition and 3 → 15 escalation become characteristic-features-of-the-first-cluster observations rather than distinguishing features. Retraction 3 added to §6.4 with the standard template. |
| **Intermediate (4–6 coincident-dual; or 5–6 lift > 3; or factor-15 at exactly 1–2 later clusters)** | **Mixed result.** v4.2 records the comparative tabulation as v4.1 promised but does not commit to either (α) or (β) pre-registered framings; instead, the §6 language is calibrated to "the staggered/coincident transition and 3 → 15 escalation occur primarily at the first two clusters but with [N] later instances" with the actual numbers reported. CinC interprets whether this constitutes a mid-strength distinguishing feature or a softened framing. Mr Adversary's v4.2 review will likely have an opinion. |

### Anchors to reproduce (verification gates)

Before tabulating, Mr Code reproduces:

- **v3.14 per-cluster nearest-cluster distance**: median = max = 2 across D ∈ [90, 200], 0/24 at distance ≥ 3, 0/24 at distance ≥ 5.
- **Boundary 1 minimum lifts**: 5-series k = 3, 7-series k = 3 (Proposition 1).
- **Boundary 2 minimum lifts**: 5-series k = 3, 7-series k = 15 (Proposition 2).
- **D₅(30) = 59, D₅(31) = 62, D₅(38) = 79, D₅(39) = 82, D₇(36) = 77, D₇(37) = 79, D₇(38) = 82** from Table 2 / Table 3 of v4.1.
- **mpmath verification at 200-digit precision** for all D_i(n) values used.

If any anchor fails, **HALT** and report.

### Expected output

A new script `v3_12_data/cluster_comparative_tabulation.py` and a results CSV `v3_12_data/results/cluster_comparative_tabulation.csv` with columns:

```
cluster_id, d_lower, d_upper, series_5_active, series_7_active, classification, S5_skips, S7_skips, lift_5, lift_7, notes
```

where:
- `cluster_id` is a string identifier ("B1" for boundary 1, "B2" for boundary 2, "C_3" through "C_N" for [90, 200] clusters in order of d_lower);
- `d_lower`, `d_upper` are the cluster's d-range;
- `series_5_active`, `series_7_active` are booleans;
- `classification` ∈ {"single-5", "single-7", "staggered", "coincident", "partial-coincident"};
- `S5_skips`, `S7_skips` are comma-separated lists of skipped digit-lengths within the cluster (or "" if not active);
- `lift_5`, `lift_7` are the minimum k satisfying conditions (a)–(c) of Step 4 (or "n/a" if series not active; or "none ≤ 1000" if not found within search range);
- `notes` flags any edge cases (e.g., "factor-15 required due to mod-5 alignment").

A markdown summary at `v3_12_data/findings.md` (appended as new section "v4.2 Comparative cluster tabulation"):

1. Anchor verification status (PASS / FAIL).
2. Total cluster count in [90, 200] (target ≥ 24 to match v3.14's enumeration).
3. Classification breakdown: counts of single-5, single-7, staggered, coincident, partial-coincident.
4. Lift-factor distribution: histogram of `lift_5` values; histogram of `lift_7` values.
5. Specific findings:
   - Number of coincident-dual clusters.
   - Number of clusters with 7-series lift > 3.
   - Number of (5-lift = 3, 7-lift = 15) coincident clusters (matching boundary-2 pattern).
   - Recurrence (yes/no) of the staggered → coincident transition between consecutive clusters at any point in [90, 200].
6. Falsifier-test result: which outcome row above applies (α, β, or intermediate).

---

## Cross-cutting requirements

### Repository conventions

- Script under `v3_12_data/` (cumulative work directory).
- Python 3.11+ with `numpy`, `mpmath` (no new dependencies).
- High-precision arithmetic via mpmath at 200-digit precision (matching the verification standard for Theorems 1–3).
- Self-contained: imports from `prime_utils.py` (existing) and standard library; invokable as `python3 v3_12_data/cluster_comparative_tabulation.py` from repo root.

### Output discipline

- CSV with header row matching the column list above.
- Script prints structured summary to stdout: anchor-verification block, results block, falsifier-test block, end-of-task status (PASS / HALT / FAIL).
- `findings.md` updates appended (not overwriting); new section header "v4.2 Comparative cluster tabulation".

### Pre-registration commit

The brief is the pre-registration. Mr Code does NOT modify "Pre-registered prediction" or "Falsifier on-record" sections during execution. The brief is committed to git at `v3_12_data/briefs/mr_code_brief_paper_3_v4_2.md` (or similar) before the computation runs.

### Stop-on-fail (Pattern 75)

If any anchor verification gate fails:
1. Halt immediately.
2. Report anchor name, expected value, observed value, tolerance.
3. Do NOT proceed.
4. Do NOT attempt to "fix" or "explain" the discrepancy.

### Reporting format

```
TASK — STATUS

Anchor verification: PASS / HALT (with detail if HALT)
Pre-registered prediction direction: confirmed / refuted / mixed
Falsifier-test result: row [α / β / intermediate] applies
Numerical summary: [the key counts, 5-7 lines]
Files produced: [list]
```

---

## What v4.2 will look like with these results

If outcome **(α)** lands: §6 of Paper 3 v4.2 retains the structural-distinguishing-features framing. The §6.3 cluster-uniformity discussion gains a new subsection (or extended paragraph) reporting the [90, 200] tabulation and confirming that boundary 1 and boundary 2 are the only clusters in the tested range exhibiting the staggered → coincident transition and the (3, 15) factor pattern. §8 Q1 is updated to reflect the comparative result. The "structural" word in §6 is now well-earned. Ship to Mr Adversary cycle 2 → fifth star → Mr Library / Zenodo.

If outcome **(β)** lands: §6 is rewritten — Retraction 3 added at §6.4; structural-distinguishing-features framing withdrawn; §6 reframed as "we analyse the first cluster on its own terms"; abstract softened to drop "structural transition" claims about boundary 1 / boundary 2 distinction; §8 Q1 dropped or significantly recast. The paper is still substantive (Theorems 1–3 unchanged; from-1 status of boundary 1 unchanged; mpmath verification unchanged; cluster-uniformity observation unchanged) but more modest. Ship the modest version to Mr Adversary cycle 2.

If **intermediate** lands: §6 is calibrated; specific counts are reported. CinC and Mr Adversary collaborate on whether the calibration is sufficient or whether one of (α) or (β) framings should be selected on-balance.

---

🐕☕⬡

*CinC + Mr Code + Mr Adversary + Mr Library = the partnership architecture of the 2I Programme. Each role scope-limited per Pattern 97. Pre-registration discipline (Pattern 19, 27) and stop-on-fail (Pattern 75) are non-negotiable.*
