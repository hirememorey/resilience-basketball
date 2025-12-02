# Extended Playoff Resilience Framework

## 🎯 Project Status: The Five-Vector Model with Clock Refinement (COMPLETE - Dec 2025)

**Note:** This document outlines the complete theoretical and implementation framework. The project has successfully deployed the **Five-Vector Stress Test Model** with **59.4% predictive accuracy** and **100% clock data coverage**.

**Current Implementation:**
The framework has been synthesized into five primary "Stress Vectors" that predict playoff archetypes from Regular Season data:

1.  **Creation Vector:** Measures self-creation ability (efficiency on 3+ dribble shots).
2.  **Leverage Vector:** Measures clutch performance (usage and efficiency in high-pressure moments).
3.  **Pressure Vector (V4.2 Refined):** Measures "Dominant Rigidity" with **Clock Distinction**:
    *   **Late Clock Pressure:** Bailout shots (7-4s, 4-0s) - valuable ability
    *   **Early Clock Pressure:** Bad shot selection (22-18s, 18-15s) - negative signal
4.  **Physicality Vector (COMPLETE):** Measures "Force" via **Rim Pressure Resilience** (maintaining rim attack volume in playoffs).
5.  **Plasticity Vector:** Measures spatial and temporal shot distribution adaptability.
6.  **Context Vector (V4.1):** Measures opponent defensive quality and quality of competition.

**See `results/predictive_model_report.md` for the current model performance (59.4% accuracy with full V4.2 clock features).**

---

## 1. The Goal (The "Why")

The ultimate goal is to build a predictive model that moves beyond traditional box score stats to identify the factors that make an NBA player's performance resilient to postseason pressure. We aim to create a quantifiable "Playoff Resilience Score" that can help basketball decision-makers make more informed, championship-focused investments.

## 2. The Core Problem

Regular-season performance is an imperfect predictor of postseason success. The game changes—defensive intensity increases, rotations shorten, and opponents exploit specific weaknesses. This project addresses the critical gap in understanding the *leading indicators* of playoff adaptability.

## 3. Core Hypotheses (Validated ✅)

1.  **Self-Creation Predicts Playoff Success:** ✅ Validated. `CREATION_VOLUME_RATIO` is the #1 predictor.
2.  **Clutch Performance Matters:** ✅ Validated. `LEVERAGE_USG_DELTA` is a top-5 predictor.
3.  **Dominance is Rigid:** ✅ Validated. `RS_PRESSURE_APPETITE` is the #2 predictor. Some players succeed not by adapting, but by imposing their will.

## 4. The "Shaq Problem" and Its Resolution

A critical insight from V2 was the **"Shaq Problem"**: the Plasticity hypothesis assumed "change is good." But some "Kings" are resilient because they are unmovable, not because they are flexible. If Giannis gets to the rim every time, his spatial variance is low (rigid), but his resilience is high.

**Solution:** The **Pressure Vector**. We measure a player's *willingness* to take tightly contested shots (`Pressure Appetite`) and their *efficiency* on those shots (`Pressure Resilience`). This captures "Dominant Rigidity."

---

## 5. Technical Implementation & Current Status

### Data Foundation
- **Scope:** **COMPLETE** - 10 seasons (2015-16 to 2024-25) with 5,312 player-season records.
- **Coverage:** Full historical context data for 8 seasons, with current season data collection in progress.
- **Architecture:** CSV-based data lake in `data/` and `results/` with integrated caching and validation.

### Core Scripts
- **`calculate_simple_resilience.py`**: The Descriptive Engine. Calculates the Dual-Grade Archetypes (RQ + Dominance).
- **`evaluate_plasticity_potential.py`**: Generates Creation, Leverage, Plasticity, and Context vectors.
- **`collect_shot_quality_aggregates.py`**: Collects Pressure vector raw data (defender distance).
- **`collect_shot_quality_with_clock.py`**: **V4.2** - Collects Pressure vector data with shot clock ranges.
- **`calculate_shot_difficulty_features.py`**: Calculates Pressure Appetite, Resilience, and Clock features.
- **`calculate_rim_pressure.py`**: Calculates Rim Pressure Resilience (Physicality Vector).
- **`calculate_physicality_features.py`**: Calculates Free Throw Rate features.
- **`train_predictive_model.py`**: Trains the XGBoost classifier with stress vector features (now includes clock features).

### Current Status & Achievements
1.  **✅ Complete Dataset:** 10 seasons (2015-2024) with full stress vectors.
2.  **✅ Five-Vector Model:** All stress vectors implemented and validated.
3.  **✅ Improved Performance:** 59.4% accuracy on 899 player-season training set (up from 58.3% baseline).
4.  **✅ Full Clock Data Coverage:** 100% coverage across all seasons (2015-16 through 2024-25).
5.  **✅ Data Quality:** All eFG% values validated, minimum sample size thresholds applied.
6.  **✅ Optimized Collection:** Clock data collection parallelized with ThreadPoolExecutor (4-5x faster).
7.  **✅ Mechanistic Insights:** Each vector provides interpretable explanations.

### Next Steps: Sloan Paper Development
1.  **Visualization Creation:** Build "Pressure Appetite vs. Playoff Performance" charts.
2.  **Narrative Development:** Focus on "Abdication Tax" and mechanistic stress vectors.
3.  **Paper Drafting:** Prepare submission for MIT Sloan Sports Analytics Conference.
