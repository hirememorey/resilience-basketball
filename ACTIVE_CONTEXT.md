# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 26, 2025
**Status**: 🏗️ **PHASE 5: RE-ARCHITECTURE & SLOAN PREP** - "The Factory Model"
- **Action**: Retrained Telescope model with **Subsidy Index v3 (Touch Ownership)**.
- **Validation**:
    - **Subsidy Logic**: `Skill = Max(TimeOfPoss/9.0, AstPct/0.45, TouchPts/10.0)`. (Fixed Anchors).
    - **Nikola Jokić ('19)**: Subsidy `0.198`. Potential **7.54** (King). ✅ "Big Man Blindspot" Resolved.
    - **Ben Simmons ('21)**: Subsidy `0.316`. Potential **3.67** (Bulldozer). ❌ Still the "Fragility Paradox".
    - **Verdict**: 55.0% Pass Rate. Physics compliance on "Ownership" achieved.
- **Focus**: Integrating a "Fragility Score" to penalize players who abdicate offensive responsibility (Simmons/Towns).

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
- **Implementation**: `Subsidy Index = 1.0 - Max(TimeOfPoss, AstPct, TouchPts)`.
- **Result**: 
    - **Nikola Jokić ('19)**: Subsidy Index **0.198** (Elite Ownership).
    - **Jalen Brunson ('22)**: Subsidy Index **0.522** (Moderate Dependence).
    - **Jordan Poole ('22)**: Subsidy Index **0.522** (Moderate Dependence).
    - **Christian Wood ('21)**: Subsidy Index **0.756** (Extreme Dependence).
- **Verdict**: The model now mechanistically discounts efficiency derived from system gravity using Fixed Anchors for Guards (Poss/Ast) and Bigs (TouchPts), resolving a key physics violation.

---

## Next Steps

1.  **Resolve "Fragility Paradox"**: Enhance the `FRAGILITY_SCORE` to more heavily penalize players with a history of offensive abdication (negative `LEVERAGE_USG_DELTA`) or an inability to generate their own shot (`CREATION_TAX`). This is now the highest priority to fix the Simmons/Towns false positives.
2.  **Implement Scalability Gradient**: Replace "Standardized Ceiling" hard logic with the **Elastic Volume Projection** (Insight #73).
    - `Projected_Volume = Current_Usage + ((0.30 - Current_Usage) * Skill_Index)`
    - This will help with the early-career projection misses (Tatum/Embiid).
3.  **Refactor**: Finalize the transition of `evaluate_plasticity_potential.py` to use `src/nba_data/core/models.py`. (Partial Complete - Schema enforced).
4.  **Visualization**: Final polish on the Sloan Risk Matrix.
