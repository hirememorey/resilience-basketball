# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 25, 2025
**Status**: 🏗️ **PHASE 5: RE-ARCHITECTURE & SLOAN PREP** - "The Factory Model"
- **Action**: Purged ~50 "Explorer Mode" scripts to `archive/`.
- **Focus**: Hardening the "Universal Avatar" pipeline for the Sloan Conference.

---

## Project Goal

To build a **Simulation Engine** ("Universal Avatar") that projects how a player's efficiency scales with usage and defensive pressure, distinguishing between "Floor Raisers" and "Helio Engines."

---

## Core Architecture: The "Factory" Pipeline (New)

We have transitioned from ad-hoc scripts to a linear "Data Factory" pipeline.

### 1. Ingestion & Feature Engineering (The Engine)
- **Script**: `src/nba_data/scripts/evaluate_plasticity_potential.py`
- **Output**: `results/predictive_dataset_with_friction.csv`
- **Key Metrics**: `HELIO_POTENTIAL_SCORE`, `FRICTION_COEFFICIENT`, `SHOT_QUALITY_GENERATION_DELTA`.

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

---

## Next Steps

1.  **Refactor**: Update `evaluate_plasticity_potential.py` to use `src/nba_data/core/models.py`.
2.  **Visualization**: Final polish on the Sloan Risk Matrix.
