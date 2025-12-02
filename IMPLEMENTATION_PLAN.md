# NBA Playoff Resilience: The Sloan Path Implementation Plan

## Executive Summary

**Goal:** Identify "16-game players" who perform better than expected in the playoffs and **explain why** using mechanistic data.

**Target:** Submission to MIT Sloan Sports Analytics Conference.

**Core Breakthrough (Dec 2025):** We have solved the **Luka/Simmons Paradox** by establishing the **Dual-Grade Archetype System**. Resilience is defined as the interaction between **Adaptability** (Resilience Quotient) and **Dominance** (Absolute Value).

---

## ✅ Completed Phases (The Foundation)

We have successfully built the Descriptive, Predictive, and Mechanistic engines.

*   **Phase 1: Data Integrity:** ✅ Solved. Full historical dataset (2015-2024) collected and verified.
*   **Phase 2: Descriptive Resilience:** ✅ Solved. The "Dual-Grade" system correctly classifies historical outliers.
*   **Phase 3: Predictive Engine:** ✅ Initial "Plasticity" model showed promise; now needs retraining on the new Archetype labels.
*   **Phase 4: The Paradox Fix:** ✅ Solved. `LUKA_SIMMONS_PARADOX.md` details the resolution.
*   **Phase 5: The "Stylistic Stress Test" (V2):** ✅ Solved. Validated that Self-Creation and Clutch Usage predict resilience.

---

## ✅ Phase 6: The "Shaq Problem" Fix (V3 Model)

**Status:** ✅ **Success.** (Dec 2025)

**Outcome:** We successfully upgraded the predictive engine to **V3** by incorporating **Pressure Vectors** (Shot Difficulty) to solve the "Shaq Problem" (Dominant Rigidity).

### Key Achievements
1.  **Prediction Accuracy:** 53.5% (up from 50.5% in V2).
2.  **Validation:** Confirmed that **Pressure Appetite** (willingness to take tight shots) is the 2nd strongest predictor of playoff resilience.
3.  **Methodology:** Successfully aggregated 5 years of defender distance data using `leaguedashplayerptshot`.

### Artifacts
*   **Model:** `models/resilience_xgb.pkl`
*   **Dataset:** `results/pressure_features.csv`
*   **Report:** `results/predictive_model_report.md`
*   **Scripts:**
    *   `src/nba_data/scripts/collect_shot_quality_aggregates.py`
    *   `src/nba_data/scripts/calculate_shot_difficulty_features.py`

---

## Phase 7: The "Physicality" & "Expansion" Phase (Current)

**Objective**: Boost predictive accuracy to >60% by capturing the missing "Force" dimension and learning from more historical failures.

### **Step 1: The Physicality Vector (Free Throw Rate Resilience)**

**Hypothesis**: Playoff resilience is often physical. Can the player get to their spot when the whistle is swallowed? We need to measure the ability to force the issue.

**Action Plan**:
1.  **Metric**: `FTr Resilience` = Playoff FTr / Regular Season FTr.
2.  **Context**: Filter for games against Top-10 defenses in RS to see if FTr drops.
3.  **Implementation**:
    *   Create `src/nba_data/scripts/calculate_physicality_features.py`.
    *   Integrate into `train_predictive_model.py`.

### **Step 2: Historical Data Expansion (2015-2019)**

**Hypothesis**: Machine Learning needs more failures to learn from. We are currently training on only 5 seasons. Expanding back to 2015 will provide critical data on "good regular season, bad playoff" players (e.g., DeMar DeRozan's Toronto years).

**Action Plan**:
1.  **Run Collection Pipeline**:
    *   Run `collect_shot_charts.py` for 2015-16 to 2018-19.
    *   Run `collect_shot_quality_aggregates.py` for 2015-16 to 2018-19.
2.  **Re-run Feature Engineering**:
    *   Re-run `evaluate_plasticity_potential.py` (Creation/Leverage vectors).
    *   Re-run `calculate_shot_difficulty_features.py` (Pressure vector).
3.  **Retrain V4 Model**:
    *   Train on the full 9-year dataset.

### **Step 3: Sloan Paper Write-Up**

**Objective**: Draft the Sloan paper, focusing on the project's compelling narrative.

**Key Narrative Points**:
1.  **The Core Problem**: Deconstructing "playoff resilience."
2.  **The Breakthrough**: The Dual-Grade Archetype system.
3.  **The Predictive Leap**: The "Stress Vectors" (Creation, Leverage, Pressure, Physicality).

---

## Historical Implementation Details (For Context)

### The V2 Plan: The "Stylistic Stress Test" Pipeline (COMPLETED)
**The Hypothesis:** A player's resilience is visible in RS situations that mimic the three core stylistic shifts of the playoffs: **1) Increased Self-Creation**, **2) Higher Leverage**, and **3) Schematic Pressure**.

#### Step 1: Feature Engineering (The "Stress Vectors")
*   **Vector 1: The "Isolation" Vector (Self-Creation)** - ✅ Implemented
*   **Vector 2: The "Clutch" Vector (Leverage)** - ✅ Implemented
*   **Vector 3: The "Pressure" Vector (Shot Difficulty)** - ✅ Implemented (V3)

#### Step 2: Modeling (Non-Linearity is Key)
*   **Methodology:** An **XGBoost Classifier**. - ✅ Implemented
*   **Target:** The `archetype` column from `results/resilience_archetypes.csv`. - ✅ Implemented
