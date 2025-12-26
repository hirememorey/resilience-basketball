# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 26, 2025
**Status**: 🏗️ **PHASE 5: RE-ARCHITECTURE & SLOAN PREP** - "The Factory Model"
- **Action**: Retrained Telescope model with Subsidy Index v2 (Ownership Matrix).
- **Validation**:
    - **Subsidy Logic**: `Skill = Max(TimeOfPoss, AstPct)`. (Speed removed to fix "Activity Merchant" trap).
    - **Jalen Brunson**: Subsidy `0.288` (High Ownership). Potential: **6.55**.
    - **Jordan Poole**: Subsidy `0.223` (High Dependence). Potential: **2.69**.
    - **Nikola Jokic**: Subsidy `0.163` (High Ownership). Potential: **2.74**.
    - **Verdict**: Jokic > Poole order restored, but Jokic's magnitude (2.74) is still a "False Low" (should be >6.0). This remains the primary active failure mode ("The Big Man Blindspot").
- **Focus**: Integrating "Touch Efficiency" (Post/Elbow) to fix Big Man valuation.

---

## Project Goal

To build a **Simulation Engine** ("Universal Avatar") that projects how a player's efficiency scales with usage and defensive pressure, distinguishing between "Floor Raisers" and "Helio Engines."

---

## Core Architecture: The "Factory" Pipeline (New)

We have transitioned from ad-hoc scripts to a linear "Data Factory" pipeline.

### 1. Ingestion & Feature Engineering (The Engine)
- **Script**: `src/nba_data/scripts/evaluate_plasticity_potential.py`
- **Output**: `results/predictive_dataset_with_friction.csv`
- **Key Metrics**: `HELIO_POTENTIAL_SCORE`, `FRICTION_COEFFICIENT`, `SUBSIDY_INDEX`.

### 2. Universal Projection (The Physics)
- **Module**: `src/nba_data/utils/projection_utils.py`
- **Logic**: Applies empirically derived friction coefficients to project `TS%` at higher usage.
- **Status**: ✅ Stress Tested (Brunson vs. Poole).

### 3. Visualization (The Deliverable)
- **Script**: `src/nba_data/scripts/visualize_risk_matrix.py`
- **Output**: Streamlit App (2D Risk Matrix).

### 4. Data Integrity (In Progress)
- **Schema**: `src/nba_data/core/models.py` (Pydantic Models).
- **Goal**: Move away from loose CSVs to typed objects.

---

## Validation Results: Physics Compliance Achieved

### ✅ **The "Empty Calories" Antidote**
- **Hypothesis**: Distinguishing "Source of Offense" (Creation vs. Consumption) is the highest leverage action.
- **Correction**: Stabilized `SHOT_QUALITY_GENERATION_DELTA` with calibrated volume thresholds.

### ✅ **Magnitude Matching (Brunson/Maxey Cases)**
- **Jalen Brunson ('21)**: Predicted 7.06 vs Actual 7.73.
- **Verdict**: Non-linearity feature has corrected the previously conservative magnitude of star projections.

### ✅ **The "Mirage Breakout" Detection (Poole Case)**
- **Jordan Poole ('22)**: Predicted **2.59**.
- **The Physics**: Despite high raw stats (18.5 PPG), the model detected the low `SHOT_QUALITY_GENERATION_DELTA` (0.142).

### ✅ **The "System Merchant" Filter (Subsidy Index)**
- **Hypothesis**: Efficiency is "Rented" from the ecosystem, not owned by the player.
- **Implementation**: `Subsidy Index = 1.0 - Max(TimeOfPoss, AstPct)`.
- **Result**: 
    - **Jalen Brunson ('22)**: Subsidy Index **0.015** (Pure Skill).
    - **Jordan Poole ('22)**: Subsidy Index **0.223** (High Dependence).
- **Verdict**: The model now mechanistically discounts efficiency derived from system gravity.

---

## Next Steps

1.  **Fix "Big Man Blindspot"**: Integrate `ELBOW_TOUCH_EFFICIENCY` and `POST_TOUCH_EFFICIENCY` into the Skill Index. (Jokic 2.74 is a physics violation).
2.  **Refactor**: Update `evaluate_plasticity_potential.py` to use `src/nba_data/core/models.py`. (Partial Complete - Schema enforced).
3.  **Visualization**: Final polish on the Sloan Risk Matrix.
