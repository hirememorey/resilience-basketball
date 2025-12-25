# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 25, 2025
**Status**: 🔭 **TELESCOPE MODEL TRAINED** - `HELIO_LOAD_INDEX` targets generated and Telescope Model v1 trained. R-squared is 0.11, identifying `USG_PCT` and `CREATION_VOLUME` as key drivers. Baseline established; next focus is feature engineering to capture "System Dependence."

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
- **Status**: ⚠️ **V1 TRAINED (Low R2)** - Model is directionally correct but lacks explanatory power (R2 = 0.11).
- **Purpose**: Answers the question: *"What is this player's **peak scalability** over the next 3 seasons?"*
- **Target Variable**: `FUTURE_PEAK_HELIO` - MAX(HELIO_LOAD_INDEX) over next 3 playoff runs.
- **Formula**: `(OFFENSIVE_LOAD^1.3) × EFFICIENCY_DELTA` where `EFFICIENCY_DELTA` is relative to **Replacement Level** (League Avg - 5.0).
- **Current Drivers**: `USG_PCT`, `USG_PCT_X_CREATION_VOLUME_RATIO`, `USG_PCT_X_LEVERAGE_USG_DELTA`.
- **Missing Signal**: Differentiation between "Self-Creators" and "System Merchants."

---

## The 2D Risk Matrix

The system now categorizes players based on the intersection of the two clocks:

| Category | Crucible Score | Telescope Score | Interpretation | Example Result |
| :--- | :--- | :--- | :--- | :--- |
| **Franchise Cornerstone** | High | High | Great Now, Great Later | **Nikola Jokić (2018-19)** |
| **Latent Star** | Low | High | Bad Now, Great Later | *Jalen Brunson (Early Career)* |
| **Win-Now Piece** | High | Low | Great Now, Capped Later | *Veteran Role Player* |
| **Ghost/Avoid** | Low | Low | Bad Now, Bad Later | **Jordan Poole (2021-22)** |

---

## Validation Results: Physics Compliance Achieved

### ✅ **HELIO Formula Validation (Target Pivot Success)**
- **Diagnostic Check**: Validated that `HELIO_LOAD_INDEX` correctly values high-load/low-efficiency stars (Westbrook '18) above Washouts (0.0).
- **Logic Upgrade**: Shifted baseline from "League Average" to "Replacement Level" to properly capture value of volume creation.

### 🔍 **Telescope Model v1 Performance**
- **RMSE**: 1.1344
- **R2 Score**: 0.1102 (Weak but non-zero)
- **Top Feature**: `USG_PCT` (0.21 importance) - confirms "Opportunity is Prerequisite" principle.
- **Insight**: Model currently over-indexes on raw usage. Needs "Antidote" features to punish empty calories.

---

## Next Developer: Start Here

**Current State**: Telescope Model v1 trained on `FUTURE_PEAK_HELIO` targets. R-squared is low (0.11), indicating the need for better features to explain variance.

**Highest Leverage Action**: Implement the **"Empty Calories" Antidote**
- **Feature**: `SHOT_QUALITY_GENERATION_DELTA`
- **Why**: Distinguish between players who *create* their own shots (Scalable) vs. those who consume created shots (System Dependent).
- **Goal**: Differentiate `Trae Young` (High Delta) from `D'Angelo Russell` (Low Delta).

**Secondary Priorities**:
1.  **Refine Feature Set**: Add interaction terms for `SHOT_QUALITY` x `TS_PCT` to avoid the "Chucker Trap."
2.  **Expand Dataset**: Process more historical seasons to increase training sample size.
3.  **Visualization**: Add Telescope outputs to the Streamlit dashboard.

**Key Scripts**:
- `src/nba_data/scripts/generate_helio_targets.py` (Target Generation - **UPDATED**)
- `src/nba_data/scripts/train_telescope_model.py` (Model Training - **UPDATED**)
- `results/training_targets_helio.csv` (Current Ground Truth)

