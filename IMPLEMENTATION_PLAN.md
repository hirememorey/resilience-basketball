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

## Phase 7: The "Physicality" & "Expansion" Phase (In Progress)

**Objective**: Boost predictive accuracy to >60% by capturing the missing "Force" dimension and learning from more historical failures.

### **Step 1: The Physicality Vector (Free Throw Rate Resilience) - ✅ DONE**

**Status**: ✅ Implemented and Integrated (Dec 2025)

**Implementation**:
*   **Script**: `src/nba_data/scripts/calculate_physicality_features.py`
*   **Metric**: `FTr Resilience` = Playoff FTr / Regular Season FTr.
*   **Integration**: Integrated into `train_predictive_model.py`.
*   **Impact**: `RS_FTr` is a top-5 feature. Model accuracy improved to **55.0%**.

### **Step 2: Historical Data Expansion (2015-2019) - ⚠️ PARTIALLY DONE**

**Status**: ⚠️ Partial (Aggregates collected, Shot Charts pending)

**Progress**:
1.  **Collection**:
    *   ✅ `collect_shot_quality_aggregates.py` run for 2015-16 to 2018-19.
    *   ✅ `evaluate_plasticity_potential.py` run for 2015-16 to 2018-19 (Creation/Leverage).
    *   ❌ `collect_shot_charts.py` **NOT RUN** (Time intensive). Plasticity features missing for these years.
2.  **Model**:
    *   ✅ Retrained on 9-year dataset (899 samples).
    *   **Accuracy**: 55.0% (up from 53.5%).

**Next Actions**:
1.  **Run Shot Chart Collection**: Execute `python src/nba_data/scripts/collect_shot_charts.py --seasons 2015-16 2016-17 2017-18 2018-19` (Warning: Takes ~80 mins).
2.  **Run Plasticity Calculation**: Execute `python src/nba_data/scripts/calculate_shot_plasticity.py` to fill missing features.
3.  **Final Retrain**: Retrain model to potentially reach >60%.

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
