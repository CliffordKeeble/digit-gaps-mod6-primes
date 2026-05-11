# Task 1 — k = 9 outlier verification: results summary

**Date:** 11 May 2026.
**Pre-registration:** `v3_12_data/briefs/task1_k9_pre_registration.md`.
**Input CSV:** `v3_12_data/results/cluster_comparative_tabulation.csv`.
**Output CSV:** `v3_12_data/results/task1_k9_verification_results.csv`.

## Aggregate outcome: (α)

All k = 9 outlier rows in the v4.2 comparative tabulation
CSV are at **non-coincident** clusters
(`classification ∈ {partial-coincident, staggered, single-5, single-7}`).
At these classifications the §4.0 convention requires
only mod-3 for the 7-series, and k = 9 = 3² is the
smallest multiple-of-3 satisfying both (i-b) (only prime
factor is 3, not in P_7 ∪ {2}) and (ii) (geometric
landing in G). The data is consistent with the §4.0
convention.

**The §6.3 GAP paragraph wording is wrong** in two
places:

1. The phrase *"coincident clusters where the geometry
   of the gap is wider than typical"* attributes k = 9
   outliers to coincident clusters, but the actual
   outliers are all at **partial-coincident** clusters.
2. The gloss *"requiring k > 3"* is correct in form
   but the geometric reason is simpler than "wider
   gap": Π_7(n_7*) · 3 falls short of the lower edge of
   the cluster's d-range, so k = 9 is the next
   multiple-of-3 that lands geometrically. The cluster
   geometries themselves are typical of
   partial-coincident structure (a B1-like
   dual-skipped-edge + singly-skipped-middle pattern).

### Suggested wording correction for §6.3 GAP paragraph

Replace:

> *"The k = 9 outliers occur at coincident clusters
> where the geometry of the gap is wider than typical,
> requiring k > 3 but where the smallest-k satisfying
> mod-15 + Convention A is 9 rather than 15."*

With:

> *"The k = 9 outliers occur at partial-coincident
> clusters where the §4.0 convention requires only
> mod-3 (not mod-15), but where the geometric anchor
> Π_7(n_7*) · 3 falls just short of the cluster's
> d-range lower edge; k = 9 = 3² is the next multiple
> of 3 that lands geometrically. These clusters exhibit
> a partial-coincident structure (dual-skipped edges
> with singly-skipped middle digits) analogous to
> boundary 1 but at higher D."*

No Calibration 3 entry required; the §4.0 convention is
consistent with all 23 strict clusters in [90, 200].
Task 1 outcome (α) confirmed.

## Per-row results

| Cluster | d-range | classification | n_7* | CSV lift | Recomputed | Outcome |
|---------|---------|----------------|------|----------|------------|---------|
| C_16 | (132,135) | partial-coincident | 56 | 9 | 9 | (α) |
| C_21 | (149,158) | partial-coincident | 62 | 9 | 9 | (α) |

🐕☕⬡

— Mr Code, 11 May 2026 (Paper 3 v4.5 Task 1)
