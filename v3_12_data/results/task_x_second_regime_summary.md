# Task X — Second coincident-gap regime summary
**Date:** 11 May 2026
**N_MAX:** 3000 per series
**D_5(3000):** 12845 | **D_7(3000):** 12871
**Scan range:** D ∈ [201, 10000]
**Clusters scanned (non-degenerate):** 631

## Anchor verification

All v4.2 anchors PASS.

## Primary observation — R2_first
- Cluster: (740, 741), classification: coincident
- lift_5 = 21, lift_7 = 15, LCM = 105, prime set = {3,5,7}
- n_5* = 244, n_7* = 242
- Π_5(n_5*) mod 5 = 0, mod 7 = 1
- Π_7(n_7*) mod 5 = 3, mod 7 = 0
- S5_skips: 740,741; S7_skips: 740,741

## Confirmation cluster — R2_confirm
- Cluster: (2299, 2301), classification: coincident
- lift_5 = 21, lift_7 = 15, LCM = 105, prime set = {3,5,7}

## Stretch — third-regime entry (11-in-lift)
No cluster with 11 | lift_5 or 11 | lift_7 found in scan range.

## Decision-tree outcome: (α)

R2_first lcm = 105 exactly (lift_5 = 21 = 3·7, lift_7 = 15 = 3·5). One-new-prime-per-escalation heuristic confirmed at three data points.
