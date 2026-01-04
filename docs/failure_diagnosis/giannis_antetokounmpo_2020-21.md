# Failure Diagnosis: Giannis Antetokounmpo (2020-21)

## The Failure
- **Expected**: Franchise Engine
- **Got**: Strong Creator (CII: 60.6)
- **Gap**: 13.4 points below the 74.0 threshold. This is a significant failure.

## Path Analysis

| Path | Score | Elite? | Good? | Issue |
|---|---|---|---|---|
| ISO | 67.8 | No | Yes | Incorrectly high. His ISO game is not his primary engine. |
| Drive-Kick | 62.8 | No | Yes | **Major Underestimation**. This should be his primary mode and score much higher (spec projected 85+). |
| Post Hub | 64.0 | No | Yes | Reasonable score for his post game. |
| Gravity | 72.8 | No | Yes | **Incorrect Primary Mode**. The model picks Gravity, which is a component of his game but not the engine itself. The high score is likely due to flawed logic in the gravity path that over-indexes on his high `paint_touches` as a proxy for movement. |

The model is confused. It incorrectly identifies Gravity as his primary mode, likely due to a flawed proxy, while severely undervaluing his dominant Drive-and-Kick engine.

## Component Analysis

| Component | Score | Issue |
|---|---|---|
| C1 Self-Created | 75.8 | **Misleadingly Inflated**. The final score is propped up by an incorrect Gravity calculation. The true engine, Drive-Kick (62.8), is too low. |
| C2 Pressure | 44.0 | **Potential Issue**. This seems very low for a player who won a championship this season. Needs investigation. |
| C3 Difficulty | 43.0 | Seems low but reflects his limited pull-up game. This is expected. |
| C4 Defense | 49.2 | Seems low. |
| C5 Force | 83.5 | **Correct**. This accurately captures his elite physical force. |

## Root Cause Hypothesis

There are two core problems:
1.  **Drive-Kick Path Failure**: Similar to LeBron, the `drive_kick.py` formula is not correctly valuing his elite rim pressure. His `drives_per_game` (11.1) is high, but the formula isn't translating that volume and his scoring/passing outcomes into an elite score.
2.  **Gravity Path Flaw**: The `gravity.py` path is likely over-relying on a poor proxy like `paint_touches` for its "movement" component, causing it to incorrectly score a high-volume driver like Giannis as a "Gravity" player. This masks the failure of the Drive-Kick path.
3.  **Pressure Score (C2)**: A score of 44.0 for `pressure_appetite` is suspicious for a Finals MVP and needs to be decomposed. It's possible his `leverage_usg_delta` is negative, which might be penalizing him too harshly.

## Proposed Fix Category

- [x] **Path formula issue (weights, thresholds)**: Both `drive_kick.py` and `gravity.py` require fundamental review. Drive-Kick is under-scoring him, and Gravity is over-scoring him for the wrong reasons.
- [ ] Missing data (field not captured)
- [ ] Missing creation mode (need new path)
- [x] **Component issue (C2-C5 problem)**: The C2 (Pressure Appetite) score of 44.0 is a red flag and needs to be investigated.
- [ ] Threshold issue (74 is wrong cutoff)
- [ ] Legitimate edge case (model is actually correct)

