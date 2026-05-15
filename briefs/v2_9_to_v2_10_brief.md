# Paper 4 v2.9 → v2.10 — Mr Code Brief: Task D (residuals)

**Date.** 15 May 2026.
**Source.** Mr Adversary's fifth review of v2.9 (five stars awarded; this is the last of four improvement items he flagged, all explicitly non-blocking).
**Scope.** One quick computational task. CinC handles three prose items in parallel; Item 5 is a reference-currency check pending input from Cliff.

**Pre-registration discipline.** Commit this brief to `briefs/v2_9_to_v2_10_brief.md` on a fresh branch BEFORE implementing. Single per-task branch off main. findings.md uses §14.

---

## Task D — Residuals of the 200k power-law fit

**Purpose.** Mr A's fifth review notes: "Twelve data points, R² = 0.979, β = 0.637 ± 0.029. The fit is clean. Would you indulge me by glancing at the residuals? I do not expect to find structure there, but with only twelve points a power-law fit can be very good while masking a slow oscillation or a systematic curvature that would tell a different story about the cluster spacings." The §5.2 R² result is load-bearing; this bound it from the "what could the residuals be hiding" direction.

**Pre-registered hypotheses.**
- **H_D0 (white noise):** residuals from the power-law fit log(spacing) = log(a) + β · log(centre) at 200k under canonical parameters show no systematic structure — Durbin-Watson statistic in [1.5, 2.5] (no significant autocorrelation at lag 1), no monotonic trend (Spearman ρ vs centre with p > 0.05), and no significant peak in a Lomb-Scargle periodogram (at the 95% level if 12 points permit).
- **H_D1 (structured residuals):** at least one of the above tests rejects, indicating a slow oscillation, systematic curvature, or other deterministic structure under the clean R².

**Method.**
1. Load the 12 (centre, spacing) pairs from the 200k cluster analysis. Source: re-run the canonical §5.2 analysis at 200k (window=50, min_gaps=20, merge_dist=500) on real primes, OR if the pairs are already serialised in a results CSV from the v2.7/v2.8 pipeline, read from there. Either is fine; document which.
2. Fit power law in log-log space: log(spacing) = log(a) + β · log(centre); record a, β, R² (sanity-check against the paper's a = 18.2, β = 0.637, R² = 0.979).
3. Compute residuals: r_i = log(spacing_i) − [log(a) + β · log(centre_i)] for i = 1, …, 12.
4. Examine:
   - **Sign pattern.** Sequence of signs of r_i; count of sign changes. Under white noise, expected sign-changes ≈ (n−1)/2 = 5.5.
   - **Monotonic trend.** Spearman correlation of r_i vs centre_i with p-value.
   - **Lag-1 autocorrelation.** Durbin-Watson statistic. Under white noise, DW ≈ 2.
   - **Periodic structure.** Lomb-Scargle periodogram (or simple FFT after detrending) if 12 points support it; otherwise note that 12 points is at the edge of what's tractable and report only the time-domain diagnostics.
5. Plot residuals vs centre as a small figure (SVG or PNG, embeddable in v2.10).

**Outputs.**
- `null-tests/residuals_analysis.py` — implementation.
- `null-tests/results/residuals_200k.csv` — per-point (centre, spacing, predicted, residual) table.
- `null-tests/results/residuals_diagnostics.txt` — DW statistic, Spearman ρ + p, sign-change count, periodogram top peak if computed.
- `figures/residuals_200k.png` (or `.svg`) — residuals-vs-centre plot.
- `findings.md` §14.1 — write-up with verdict and recommended §5.2 / §9 paper-passage updates.

**Decision rule.**
- All three time-domain tests pass H_D0 thresholds → white noise verdict. v2.10 §5.2 gets a footnote stating residuals examined and found unstructured.
- Any test rejects → structure exists; describe it in the findings write-up. CinC will integrate into §5.2 and §9 (the latter as a new open question on the mechanism producing the structure).

**Estimated runtime.** Under 5 minutes including plot generation. Total brief well under 15 minutes.

🐕☕⬡
