# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 26, 2025
**Status**: 🏗️ **PHASE 5: RE-ARCHITECTURE & SLOAN PREP** - "The Factory Model"
- **Action**: Retrained Telescope model with Subsidy Index v2 (Ownership Matrix).
- **Validation**:
    - **Subsidy Logic**: `Skill = Max(TimeOfPoss/9.0, AstPct/0.45)`. (Fixed Anchors).
    - **Christian Wood**: Subsidy `0.756`. Potential dropped to **2.40** (Sniper/Victim). ✅ "Empty Calories" Resolved.
    - **Ben Simmons**: Subsidy `0.316`. Potential **2.62** (Borderline Bulldozer). ❌ Still the "Fragility Paradox".
    - **Verdict**: 88.9% Pass Rate. Physics compliance achieved on "System Merchants".
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
    - **Jalen Brunson ('22)**: Subsidy Index **0.522** (Moderate Dependence).
    - **Jordan Poole ('22)**: Subsidy Index **0.522** (Moderate Dependence).
    - **Tyrese Maxey ('22)**: Subsidy Index **0.356** (High Ownership).
    - **Christian Wood ('21)**: Subsidy Index **0.756** (Extreme Dependence).
- **Verdict**: The model now mechanistically discounts efficiency derived from system gravity using Fixed Anchors (9.0 min Poss, 45% AST) rather than relative percentiles.

---

## Next Steps

1.  **Fix "Big Man Blindspot"**: Integrate `ELBOW_TOUCH_EFFICIENCY` and `POST_TOUCH_EFFICIENCY` into the Skill Index. (Jokic 2.74 is a physics violation).
2.  **Refactor**: Update `evaluate_plasticity_potential.py` to use `src/nba_data/core/models.py`. (Partial Complete - Schema enforced).
3.  **Visualization**: Final polish on the Sloan Risk Matrix.
