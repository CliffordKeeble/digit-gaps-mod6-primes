# Task 3 — F5 (refined) under re-classifying alternatives: summary

**Date:** 11 May 2026.
**Pre-registration:** `v3_12_data/briefs/task3_re_classifying_alternatives_pre_registration.md`.
**Outcome (refined F5): (α)**

## Three-convention comparative table (7-series, [90, 200] sample, n = 23)

| Convention | distribution | mode (freq) | outliers | H (bits) | transitions | non-degenerate |
|------------|--------------|-------------|----------|----------|-------------|----------------|
| chosen | {15: 19, 3: 2, 9: 2} | 15 (82.6%) | 4 | 0.8405 | 4 | yes |
| alt_c | {3: 15, 9: 8} | 3 (65.2%) | 8 | 0.9321 | 4 | yes |
| alt_d | {15: 23} | 15 (100.0%) | 0 | 0.0000 | 4 | NO (delta) |

Refined F5 binding: non-degenerate AND (outliers ≤ 2 OR H ≤ 0.35 bits OR transitions ≤ 3).
Reference (chosen-convention) values from v4.2: outliers = 4, H = 0.8405 bits, transitions = 4.

## Outcome paragraph — (α) chosen wins under non-degenerate competition

Neither re-classifying alternative crosses any binding refined-F5 threshold while remaining non-degenerate. The chosen mod-3 / mod-15 convention is preserved against both *less-asymmetric* (Alt(C) drops the mod-15 escalation) and *more-asymmetric* (Alt(D) extends mod-15 to partial-coincident) competition. Warrant tightens.

## Per-cluster table

| Cluster | d-range | classification | n_7* | D_7(n_7*) | chosen | Alt(C) | Alt(D) |
|---------|---------|----------------|------|-----------|--------|--------|--------|
| C_3 | (91,94) | partial-coincident | 42 | 92 | 3 | 3 | 15 |
| C_4 | (96,97) | coincident | 43 | 95 | 15 | 9 | 15 |
| C_5 | (99,102) | partial-coincident | 45 | 100 | 3 | 3 | 15 |
| C_6 | (104,105) | coincident | 46 | 103 | 15 | 3 | 15 |
| C_7 | (107,108) | coincident | 47 | 106 | 15 | 9 | 15 |
| C_8 | (110,110) | coincident | 48 | 109 | 15 | 9 | 15 |
| C_9 | (112,113) | coincident | 49 | 111 | 15 | 3 | 15 |
| C_10 | (115,116) | coincident | 50 | 114 | 15 | 3 | 15 |
| C_11 | (118,119) | coincident | 51 | 117 | 15 | 9 | 15 |
| C_12 | (121,121) | coincident | 52 | 120 | 15 | 9 | 15 |
| C_13 | (123,124) | coincident | 53 | 122 | 15 | 3 | 15 |
| C_14 | (126,127) | coincident | 54 | 125 | 15 | 3 | 15 |
| C_15 | (129,130) | coincident | 55 | 128 | 15 | 9 | 15 |
| C_16 | (132,135) | partial-coincident | 56 | 131 | 9 | 9 | 15 |
| C_17 | (137,138) | coincident | 58 | 136 | 15 | 3 | 15 |
| C_18 | (140,141) | coincident | 59 | 139 | 15 | 3 | 15 |
| C_19 | (143,144) | coincident | 60 | 142 | 15 | 3 | 15 |
| C_20 | (146,147) | coincident | 61 | 145 | 15 | 3 | 15 |
| C_21 | (149,158) | partial-coincident | 62 | 148 | 9 | 9 | 15 |
| C_22 | (160,161) | coincident | 66 | 159 | 15 | 3 | 15 |
| C_23 | (163,164) | coincident | 67 | 162 | 15 | 3 | 15 |
| C_24 | (166,167) | coincident | 68 | 165 | 15 | 3 | 15 |
| C_25 | (169,170) | coincident | 69 | 168 | 15 | 3 | 15 |

🐕☕⬡

— Mr Code, 11 May 2026 (Paper 3 v4.5 Task 3)
