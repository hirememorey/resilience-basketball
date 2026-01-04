# Failure Diagnosis: Stephen Curry (2016-17)

## The Failure
- **Expected**: Franchise Engine
- **Got**: Strong Creator (CII: 68.5)
- **Gap**: 5.5 points below the 74.0 threshold.

## Path Analysis

| Path | Score | Elite? | Good? | Issue |
|---|---|---|---|---|
| ISO | 68.0 | No | Yes | **Incorrect Primary Mode**. The model defaults to ISO because the Gravity score is too low. |
| Drive-Kick | 52.8 | No | No | Reasonable. Not his primary mode. |
| Post Hub | 49.5 | No | No | Reasonable. Not his primary mode. |
| Gravity | 60.1 | No | Yes | **The Root Cause**. This score is far too low for one of the greatest off-ball players ever. The spec projected an 85+ score. |

Similar to the LeBron case, the model fails to identify Curry's true creation engine (Gravity) and instead defaults to a respectable but inaccurate ISO classification. The Gravity path score of 60.1 is the core problem.

## Component Analysis

| Component | Score | Issue |
|---|---|---|
| C1 Self-Created | 71.0 | **Primary Failure Point**. The score is suppressed because the `gravity.py` calculation is not correctly capturing his value. |
| C2 Pressure | 81.3 | Seems correct. Curry steps up under pressure. |
| C3 Difficulty | 64.9 | Reasonable, reflects his pull-up game. |
| C4 Defense | 62.4 | Reasonable. |
| C5 Force | 53.6 | Correct, he is not a force-based player. |

## Root Cause Hypothesis

The `gravity.py` path calculation is not properly weighted or is missing key inputs. The proxy metrics used (screen assists, catch-and-shoot %, movement proxy) are not being translated into a score that reflects his true impact. A score of 60.1 for the player who warped NBA defenses is a clear sign that the formula is flawed. For example, his `screen_ast` is 0.0 in the `tracking_data_merged.csv`, which is incorrect and points to a data collection or processing issue for that specific metric. Other gravity-related fields might also be missing or undervalued.

## Proposed Fix Category

- [x] **Path formula issue (weights, thresholds)**: The formula in `gravity.py` needs to be reviewed. The weights and thresholds are not producing a score commensurate with his known impact.
- [x] **Missing data (field not captured)**: The `screen_ast` data appears to be missing or zeroed out for Curry in the 2016-17 season, which is a critical input for this path. This suggests a potential upstream data collection problem that needs to be investigated.
- [ ] Missing creation mode (need new path)
- [ ] Component issue (C2-C5 problem)
- [ ] Threshold issue (74 is wrong cutoff)
- [ ] Legitimate edge case (model is actually correct)

