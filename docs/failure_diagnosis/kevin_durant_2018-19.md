# Failure Diagnosis: Kevin Durant (2018-19)

## The Failure
- **Expected**: Franchise Engine
- **Got**: Strong Creator (CII: 72.0)
- **Gap**: 2.0 points below the 74.0 threshold. This is a narrow miss.

## Path Analysis

| Path | Score | Elite? | Good? | Issue |
|---|---|---|---|---|
| ISO | 72.9 | No | Yes | **Correct Primary Mode**. His ISO game is elite, but the score is just below the 75.0 elite threshold. |
| Drive-Kick | 56.2 | No | No | Reasonable. Not his primary mode. |
| Post Hub | 69.3 | No | Yes | Reasonable for his post-up game. |
| Gravity | 55.4 | No | No | Reasonable. Not his primary mode. |

The model correctly identifies ISO as his primary mode. The issue is that the ISO path score (72.9) is just below the elite threshold (75.0), which prevents him from getting the multi-modal bonus and pushes his C1 score down.

## Component Analysis

| Component | Score | Issue |
|---|---|---|
| C1 Self-Created | 72.9 | **Just Below Threshold**. The score is 2.1 points below the 75.0 elite threshold. This is a calibration issue, not a fundamental flaw. |
| C2 Pressure | 76.3 | Reasonable. |
| C3 Difficulty | 72.4 | Reasonable. Reflects his pull-up and mid-range game. |
| C4 Defense | 66.7 | Reasonable. |
| C5 Force | 69.5 | Reasonable. |

## Root Cause Hypothesis

This is a **calibration/threshold issue**, not a fundamental architectural problem. Durant's ISO path score of 72.9 is very close to the elite threshold of 75.0. The sub-components of the ISO path (unassisted rate, pull-up volume, efficiency, usage) are likely all scoring well, but the weighted combination is just slightly below the threshold. This could be due to:
1. The normalization thresholds in `iso.py` being slightly too strict
2. One of his sub-components (likely pull-up volume or efficiency) being slightly below the elite benchmark
3. The weights in the ISO path not being optimally calibrated

This is a much easier fix than the LeBron/Curry/Giannis cases because the architecture is working correctly; it's just a matter of fine-tuning thresholds or weights.

## Proposed Fix Category

- [x] **Path formula issue (weights, thresholds)**: The ISO path thresholds or weights need minor calibration. This is a fine-tuning issue, not a fundamental flaw.
- [ ] Missing data (field not captured)
- [ ] Missing creation mode (need new path)
- [ ] Component issue (C2-C5 problem)
- [ ] Threshold issue (74 is wrong cutoff)
- [ ] Legitimate edge case (model is actually correct)

