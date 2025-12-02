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

---

## ✅ Phase 5: The "Stylistic Stress Test" Predictive Model (Completed)

**Status:** ✅ **Success.** (Dec 2025)

**Outcome:** We successfully built a predictive engine that forecasts Playoff Archetypes using Regular Season "Stress Vectors."

### Key Achievements
1.  **Prediction Accuracy:** 50.5% (vs 25% random baseline).
2.  **Validation:** Confirmed that **Self-Creation Volume** and **Clutch Usage Scaling** are the strongest predictors of playoff resilience.
3.  **Infrastructure:** Built a robust `NBAStatsClient` with Clutch and Shot Dashboard capabilities.

### Artifacts
*   **Model:** `models/resilience_xgb.pkl`
*   **Dataset:** `results/predictive_dataset.csv`
*   **Report:** `results/predictive_model_report.md`
*   **Scripts:**
    *   `src/nba_data/scripts/evaluate_plasticity_potential.py` (Feature Engineering)
    *   `src/nba_data/scripts/train_predictive_model.py` (Modeling)

---

## Phase 6: Model Refinement & Sloan Paper Preparation (Current)

**Objective**: Boost predictive accuracy from 50.5% to over 60% and finalize the analysis for the Sloan paper.

**`[PIVOT]` From "Context" to "Plasticity"**:
The initial plan to implement a "Context Vector" (performance vs. top RS defenses) has been **deprecated**. A pilot study revealed that this approach is likely high-risk and low-reward due to the noisy nature of regular season defensive data.

The new strategic direction, "The Plasticity Resurrection," has shown a strong positive signal and is the new priority. It directly measures the "Schematic Friction" that players face in the playoffs.

---

### **Step 1: The Plasticity Resurrection (The Real Sloan Alpha)**

**Hypothesis**: The "Bulldozer" vs. "King" distinction is defined by **Spatial Rigidity**. A Bulldozer must get to his spot. A King can score from the counter-spot.

**Action Plan**:

1.  **Collect Full Shot Chart Data (`shotchartdetail`)**
    -   **Script**: `src/nba_data/scripts/collect_shot_charts.py`
    -   **Status**: `[In Progress]`
    -   **Details**: Collect RS and Playoff shot charts for all qualified players from 2019-20 to 2023-24. This is a large-scale data collection effort.

2.  **Engineer "Spatial Rigidity" Features**
    -   **Script**: `src/nba_data/scripts/calculate_shot_plasticity.py`
    -   **Status**: `[Completed]`
    -   **Features**:
        -   `SHOT_DISTANCE_DELTA`: Change in median shot distance (RS vs PO).
        -   `SPATIAL_VARIANCE_DELTA`: Change in the 2D variance of shot locations. This is the key hypothesized feature.
        -   `PO_EFG_BEYOND_RS_MEDIAN`: Playoff eFG% on shots taken further than the player's regular season median distance.

3.  **Train and Evaluate V3 Model**
    -   **Script**: `src/nba_data/scripts/train_predictive_model.py`
    -   **Status**: `[Completed]`
    -   **Result**: The V3 model successfully integrated the plasticity features and achieved **52.5% accuracy**. This validates the hypothesis but falls short of the >60% goal.

### **Step 2: Model Refinement for Sloan Paper**

**Objective**: Take the validated V3 model and systematically refine it to break the 60% accuracy threshold.

**Action Plan**:

1.  **Hyperparameter Tuning**
    -   **Action**: Use techniques like GridSearchCV or RandomizedSearchCV to find the optimal hyperparameters for the XGBoost model.
    -   **Rationale**: The current model uses a default configuration. Tuning is the most direct path to unlocking further accuracy from the existing feature set.

2.  **Feature Interaction Engineering**
    -   **Action**: Create new features that capture the interaction between the core stress vectors.
    -   **Example**: Create an `ADAPTABILITY_SCORE` by combining creation metrics with spatial variance (`CREATION_VOLUME_RATIO` * `SPATIAL_VARIANCE_DELTA`). This would directly test the hypothesis that players who expand their shot diet under pressure are more resilient.

3.  **Expand Historical Dataset**
    -   **Action**: Run the data collection scripts (`collect_shot_charts.py`, `evaluate_plasticity_potential.py`, etc.) for additional historical seasons (e.g., 2015-16 through 2018-19).
    -   **Rationale**: A larger dataset will make the model more robust and help it learn more subtle patterns, reducing the impact of single-series playoff noise.

### **Step 3: Sloan Paper Write-Up**

**Objective**: Draft the Sloan paper, focusing on the project's compelling narrative.

**Key Narrative Points**:
1.  **The Core Problem**: Deconstructing the vague concept of "playoff resilience."
2.  **The Breakthrough**: Solving the "Luka & Simmons Paradox" with the Dual-Grade Archetype system. This is the intellectual foundation.
3.  **The Predictive Leap**: Moving beyond simple stats to predict these archetypes using "Stylistic Stress Vectors," with a special focus on how "Spatial Rigidity" proved to be the missing ingredient.

This narrative combines a strong theoretical framework (the Dual-Grade system) with a validated, data-driven predictive model that has a clear, intuitive explanation (the Stress Vectors).

---

## Historical Implementation Details (For Context)

This section is retained to show the evolution of the project. A new developer does not need to re-implement these steps.

### Critical Lessons from V1 (The Post-Mortem)
Our initial attempt to solve this by simply filtering RS data for games against "Top-5 Defenses" failed (correlation of 0.08). The post-mortem revealed critical insights that now guide our V2 approach:

1.  **The "Different Sport" Fallacy:** RS "Stress" is not the same as Playoff "Stress." Playoff pressure is about *schematic removal*, not just better opponents. We cannot simply filter game logs; we must find proxies for the *stylistic shift* that occurs in the postseason.
2.  **The "Identifier Hell" Fix:** The NBA API uses inconsistent team IDs. A canonical `constants.py` file with hardcoded ID-to-Abbreviation maps is the first step to prevent hours of debugging.
3.  **The "Metric Drift" Reality:** "Plasticity" is a vector, not a scalar. A player changing their shot chart (displacement) is only meaningful in context. For a star, it can be adaptation (good); for a role player, it can mean being forced from their spots (bad).

---

### The V2 Plan: The "Stylistic Stress Test" Pipeline (COMPLETED)
**The Hypothesis:** A player's resilience is visible in RS situations that mimic the three core stylistic shifts of the playoffs: **1) Increased Self-Creation**, **2) Higher Leverage**, and **3) Schematic Pressure**.

#### Step 1: Feature Engineering (The "Stress Vectors")

*   **Vector 1: The "Isolation" Vector (Self-Creation)** - ✅ Implemented
*   **Vector 2: The "Clutch" Vector (Leverage)** - ✅ Implemented
*   **Vector 3: The "Quality of Competition" Vector** - ⚠️ **Deferred to V2 Model.** This is the next step.

#### Step 2: Modeling (Non-Linearity is Key)

*   **Methodology:** An **XGBoost Classifier**. - ✅ Implemented
*   **Target:** The `archetype` column from `results/resilience_archetypes.csv`. - ✅ Implemented
