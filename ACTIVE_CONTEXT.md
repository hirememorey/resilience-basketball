# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 26, 2025
**Status**: 🏗️ **PHASE 5: RE-ARCHITECTURE & SLOAN PREP** - "The Factory Model"
- **Action**: Retrained Telescope model with **Fragility Score v3.5 (Abdication + Choke Tax)**.
- **Validation**:
    - **Subsidy Logic**: `Skill = Max(TimeOfPoss/9.0, AstPct/0.45, TouchPts/10.0)`. (Fixed Anchors).
    - **Fragility Logic**: `Fragility = Base + (Abdication * 15.0) + (Choking * 5.0)`.
    - **D'Angelo Russell ('19)**: Corrected from **King (5.81)** to **Sniper (1.43)**. ✅ The "Abdication Tax" works.
    - **Ben Simmons ('19)**: Potential reduced (7.17 -> 4.32), but still **King**. ❌ "The Linearity Trap".
    - **KAT ('19)**: Potential reduced (7.37 -> 4.95), but still **King**. ❌ Raw volume overpowers fragility.
    - **Verdict**: 60.0% Pass Rate. Physics of "Fragility" are sound, but the model architecture (XGBoost) struggles to enforce hard penalties on elite volume.

---

## Project Goal

To build a **Simulation Engine** ("Universal Avatar") that projects how a player's efficiency scales with usage and defensive pressure, distinguishing between "Floor Raisers" and "Helio Engines."

---

## Core Architecture: The "Factory" Pipeline (New)

We have transitioned from ad-hoc scripts to a linear "Data Factory" pipeline.

### 1. Ingestion & Feature Engineering (The Engine)
- **Script**: `src/nba_data/scripts/evaluate_plasticity_potential.py`
- **Output**: `results/predictive_dataset_with_friction.csv`
- **Key Metrics**: `HELIO_POTENTIAL_SCORE`, `SUBSIDY_INDEX`, `FRAGILITY_SCORE`.
- **New Logic (Dec 26)**:
    - **Abdication Tax**: Penalizes `LEVERAGE_USG_DELTA` (Simmons/D-Lo).
    - **Choke Tax**: Penalizes `LEVERAGE_TS_DELTA` (KAT).

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

### ✅ **The "Glass Cannon" Fix (D-Lo Case)**
- **Hypothesis**: High Ownership (Subsidy) is not enough; one must maintain intent under pressure.
- **Correction**: `FRAGILITY_SCORE` now includes an **Abdication Multiplier** (Slope -15.0).
- **Result**: D'Angelo Russell ('19) usage drop (-6.7%) triggered massive penalty. Prediction moved from **King** to **Sniper**.

### ✅ **The "System Merchant" Filter (Subsidy Index)**
- **Hypothesis**: Efficiency is "Rented" from the ecosystem, not owned by the player.
- **Implementation**: `Subsidy Index = 1.0 - Max(TimeOfPoss, AstPct, TouchPts)`.
- **Result**: 
    - **Nikola Jokić ('19)**: Subsidy Index **0.198** (Elite Ownership).
    - **Jalen Brunson ('22)**: Subsidy Index **0.522** (Moderate Dependence).
    - **Jordan Poole ('22)**: Subsidy Index **0.522** (Moderate Dependence).
    - **Christian Wood ('21)**: Subsidy Index **0.756** (Extreme Dependence).
- **Verdict**: The model now mechanistically discounts efficiency derived from system gravity.

---

## Next Steps

1.  **Resolve "The Linearity Trap" (Simmons/KAT)**: The Fragility Score is high, but the XGBoost model overpowers it with volume signals.
    - **Action**: Implement a "Hard Gate" or "Penalty Injection" into the target variable itself, or use a 2-stage model (Filter -> Rank).
2.  **Implement Scalability Gradient**: Replace "Standardized Ceiling" hard logic with the **Elastic Volume Projection** (Insight #73).
    - `Projected_Volume = Current_Usage + ((0.30 - Current_Usage) * Skill_Index)`
    - This will help with the early-career projection misses (Tatum/Embiid).
3.  **Refactor**: Finalize the transition of `evaluate_plasticity_potential.py` to use `src/nba_data/core/models.py`. (Partial Complete - Schema enforced).
4.  **Visualization**: Final polish on the Sloan Risk Matrix.
