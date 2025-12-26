# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 25, 2025
**Status**: 🔭 **TELESCOPE MODEL V2.1 CALIBRATED** - Structural repairs complete. `HELIO_POTENTIAL_SCORE` (Non-linear) and "Revealed Capacity" target logic have corrected the magnitude mismatch for future stars.

---

## Project Goal

To build a predictive system that can accurately distinguish between immediate playoff contributors, future stars, and "fool's gold" players by modeling the orthogonal physics of **Viability** and **Scalability**.

---

## Core Architecture: The "Two-Clock" System

### 1. The Crucible (The "Camera" - Viability Engine)
- **Status**: ✅ Implemented & Validated
- **Purpose**: Answers the question: *"If you drop this player into a playoff series **today**, will they survive?"*
- **Target Variable**: `Current_Season_Playoff_PIE`
- **Output**: `CRUCIBLE_SCORE` (1 - Probability of Liability)

### 2. The Telescope (The "Projection" - Potential Engine)
- **Status**: ✅ **V2.1 CALIBRATED**
- **Purpose**: Answers the question: *"What is this player's **peak scalability** over the next 3 seasons?"*
- **Target Variable**: `FUTURE_PEAK_HELIO` - MAX(HELIO_LOAD_INDEX) over next 3 playoff runs.
- **Top Feature**: `HELIO_POTENTIAL_SCORE` (26.5% importance).
- **Insight**: The model now identifies the **Non-Linear Force Multiplier** of stardom.

---

## Validation Results: Physics Compliance Achieved

### ✅ **The "Empty Calories" Antidote**
- **Hypothesis**: Distinguishing "Source of Offense" (Creation vs. Consumption) is the highest leverage action.
- **Correction**: Stabilized `SHOT_QUALITY_GENERATION_DELTA` with calibrated volume thresholds (>1.5 FGA for catch-and-shoot, >0.5 FGA for ISO).
- **Validation**: Correctly identifies low-usage finishers (Lively II, Robinson) as high-quality generators.

### ✅ **The "Lottery Star" Trap Fix**
- **Issue**: Marked non-playoff players as 0, teaching the model that high usage on bad teams = washout.
- **Correction**: Adopted "Revealed Capacity" logic. Training set now **drops** censored data (lottery years) instead of marking as zero.
- **Result**: Model correctly projects stars even during their "lottery development" phase.

### ✅ **Magnitude Matching (Brunson/Maxey Cases)**
- **Jalen Brunson ('21)**: Predicted 7.30 vs Actual 7.73.
- **Tyrese Maxey ('22)**: Predicted 5.53 vs Actual 5.35.
- **Verdict**: Non-linearity feature has corrected the previously conservative magnitude of star projections.

---

## Next Developer: Start Here

**Current State**: Phase 4 Pivot is complete. The Telescope is now calibrated to detect future heliocentric engines.

**Next Priority**: **Universal Projection Integration**
1.  **Avatar Projection**: Ensure `HELIO_POTENTIAL_SCORE` and `SHOT_QUALITY_GENERATION_DELTA` are correctly handled in the projection engine (`src/nba_data/utils/projection_utils.py`).
2.  **Visualization**: Add the "Heliocentric Potential" chart to the Streamlit app to distinguish between "System Scalers" and "Helio Engines."
3.  **Benchmarking**: Run the 2D Risk Matrix analysis using the new calibrated Telescope scores.

**Key Scripts**:
- `src/nba_data/scripts/evaluate_plasticity_potential.py` (Feature Origin)
- `src/nba_data/scripts/generate_helio_targets.py` (Censored Data Target Logic)
- `src/nba_data/scripts/train_telescope_model.py` (Final Regressor)
- `scripts/validate_latent_stars.py` (Validation Suite)
