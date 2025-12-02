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

## 🚀 Phase 6: Model Refinement & Sloan Paper Preparation

**The Goal:** Increase predictive accuracy to >60% and package our findings for publication. The current 50.5% accuracy is a strong proof of concept, but not yet definitive.

**The Next Developer's Mission:** Implement the "Context Vector" to push the model's accuracy higher.

---

### Step 1: Implement the "Context Vector" (Accuracy Boost)
Our V1 predictive model confirmed that "how" you score matters (Creation & Leverage vectors). The next step is to incorporate "who" you score against.

*   **Hypothesis:** A player's performance against Top-10 Regular Season defenses is a strong predictor of how they will handle elite playoff defenses.
*   **Action:** Create a new feature engineering script or extend the existing one (`evaluate_plasticity_potential.py`) to:
    1.  **Collect Regular Season Game Logs:** Create a new collection script (`collect_rs_game_logs.py`) to fetch per-game data for every qualified player.
    2.  **Identify Top Defenses:** Load the `defensive_context_{season}.csv` files.
    3.  **Calculate Performance Splits:** For each player, calculate their aggregate performance (TS%, USG%) against Top-10 Defenses vs. Bottom-10 Defenses.
    4.  **Create the Vector:** Engineer a `QoC_Delta` feature (e.g., TS% vs Top 10 - TS% vs Bottom 10).

### Step 2: Retrain and Evaluate Model V2
*   **Action:** Add the new `QoC_Delta` feature to the XGBoost model in `train_predictive_model.py`.
*   **Expected Outcome:** Accuracy should improve, particularly in distinguishing "Bulldozers" from "Kings," as many stars who appear inefficient in the playoffs were simply facing the league's best defenses.

### Step 3: Write the Paper
*   **Narrative:** The story is compelling. We started with a paradox (Luka/Simmons), solved it with a new descriptive framework (Dual-Grade), and then successfully predicted it with a mechanistic model (Stress Vectors).
*   **Key Visuals:**
    1.  The Dual-Grade Archetype Scatter Plot.
    2.  The Predictive Model Feature Importance Bar Chart.
    3.  The V2 Model Confusion Matrix.

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
