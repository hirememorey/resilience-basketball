# Failure Diagnosis: Ja Morant (2021-22)

## The Failure
- **Expected**: Franchise Engine
- **Got**: Strong Creator (CII: 65.5)
- **Gap**: 8.5 points below the 74.0 threshold.

## Path Analysis

| Path | Score | Elite? | Good? | Issue |
|---|---|---|---|---|
| ISO | 68.8 | No | Yes | **Incorrect Primary Mode**. The model defaults to ISO, but this is not his true engine. |
| Drive-Kick | 0.0 | No | No | **CRITICAL DATA ISSUE**. The score is zero, which indicates missing or zeroed-out tracking data. This is a data collection problem, not a formula issue. |
| Post Hub | 41.2 | No | No | Reasonable. Not his mode. |
| Gravity | 10.0 | No | No | Reasonable floor score. Not his mode. |

The model incorrectly identifies ISO as his primary mode because the Drive-Kick path is returning 0.0 due to missing data. This is a **data availability issue**, not a calculation problem.

## Component Analysis

| Component | Score | Issue |
|---|---|---|
| C1 Self-Created | 68.8 | **Suppressed by Missing Data**. The score would be much higher if Drive-Kick data were available. |
| C2 Pressure | 90.0 | **Correct**. He steps up under pressure. |
| C3 Difficulty | 43.0 | Reasonable. Reflects his limited pull-up game. |
| C4 Defense | 49.2 | Reasonable. |
| C5 Force | 75.3 | **Correct**. He is a force-based player. |

## Root Cause Hypothesis

This is a **data collection/availability issue**, not a model architecture problem. The `drives_per_game`, `drive_pts`, `drive_ast`, and related fields are either:
1. Not collected for the 2021-22 season in the `tracking_data_merged.csv`
2. Zeroed out or null for Ja Morant specifically
3. Not properly merged from the tracking data source

The `drive_kick.py` calculation is likely correct, but it cannot produce a valid score when all inputs are zero. This needs to be investigated at the data pipeline level.

## Proposed Fix Category

- [ ] Path formula issue (weights, thresholds)
- [x] **Missing data (field not captured)**: The Drive-Kick tracking data is missing for Ja Morant in 2021-22. This needs to be collected or the data merge process needs to be fixed.
- [ ] Missing creation mode (need new path)
- [ ] Component issue (C2-C5 problem)
- [ ] Threshold issue (74 is wrong cutoff)
- [ ] Legitimate edge case (model is actually correct)

