# Task 2 — F5 alternative-convention probe: summary

**Date:** 11 May 2026.
**Pre-registration:** `v3_12_data/briefs/task2_alternative_convention_pre_registration.md`.
**Outcome: (β)**

## Three-convention comparative table (7-series lift distribution, F5 metrics)

| Convention | 7-series lift distribution | Outlier count | Entropy (bits) | Transitions |
|------------|----------------------------|---------------|----------------|-------------|
| chosen | {15: 19, 3: 2, 9: 2} | 4 | 0.8405 | 4 |
| alt_a | {10: 19, 2: 2, 6: 2} | 4 | 0.8405 | 4 |
| alt_b | {30: 23} | 0 | 0.0000 | 4 |

Binding thresholds: outliers ≤ 2, entropy ≤ 0.35 bits, transitions ≤ 3.

Reference (chosen-convention) values from v4.2: outliers = 4, entropy ≈ 0.85 bits, transitions = 4.

## Per-cluster lift recomputation

| Cluster | d-range | classification | (lift5, lift7) chosen | (lift5, lift7) Alt A | (lift5, lift7) Alt B |
|---------|---------|----------------|----------------------|----------------------|----------------------|
| C_3 | (91,94) | partial-coincident | (9, 3) | (4, 2) | (6, 30) |
| C_4 | (96,97) | coincident | (3, 15) | (2, 10) | (6, 30) |
| C_5 | (99,102) | partial-coincident | (9, 3) | (4, 2) | (6, 30) |
| C_6 | (104,105) | coincident | (3, 15) | (2, 10) | (6, 30) |
| C_7 | (107,108) | coincident | (9, 15) | (4, 10) | (6, 30) |
| C_8 | (110,110) | coincident | (9, 15) | (8, 10) | (12, 30) |
| C_9 | (112,113) | coincident | (3, 15) | (2, 10) | (6, 30) |
| C_10 | (115,116) | coincident | (3, 15) | (4, 10) | (6, 30) |
| C_11 | (118,119) | coincident | (9, 15) | (6, 10) | (6, 30) |
| C_12 | (121,121) | coincident | (9, 15) | (12, 10) | (12, 30) |
| C_13 | (123,124) | coincident | (3, 15) | (2, 10) | (6, 30) |
| C_14 | (126,127) | coincident | (3, 15) | (4, 10) | (6, 30) |
| C_15 | (129,130) | coincident | (9, 15) | (6, 10) | (6, 30) |
| C_16 | (132,135) | partial-coincident | (3, 9) | (2, 6) | (6, 30) |
| C_17 | (137,138) | coincident | (3, 15) | (2, 10) | (6, 30) |
| C_18 | (140,141) | coincident | (3, 15) | (4, 10) | (6, 30) |
| C_19 | (143,144) | coincident | (9, 15) | (6, 10) | (6, 30) |
| C_20 | (146,147) | coincident | (9, 15) | (8, 10) | (12, 30) |
| C_21 | (149,158) | partial-coincident | (3, 9) | (2, 6) | (6, 30) |
| C_22 | (160,161) | coincident | (9, 15) | (4, 10) | (6, 30) |
| C_23 | (163,164) | coincident | (9, 15) | (6, 10) | (6, 30) |
| C_24 | (166,167) | coincident | (9, 15) | (8, 10) | (12, 30) |
| C_25 | (169,170) | coincident | (9, 15) | (12, 10) | (12, 30) |

## Outcome paragraph — (β) alternative fires F5

At least one alternative convention crosses at least one binding F5 threshold. The chosen convention's claim to being the right lens on the data is **refuted**. Retraction 4 (specifically of convention choice) is indicated.

## Transition pairs (fixed across conventions)

- C_3 → C_4
- C_5 → C_6
- C_16 → C_17
- C_21 → C_22

🐕☕⬡

— Mr Code, 11 May 2026 (Paper 3 v4.5 Task 2)
