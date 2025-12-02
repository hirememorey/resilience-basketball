# Extended Playoff Resilience Framework

## 🚨 Project Update: The Four-Vector Model (Dec 2025)

**Note:** This document outlines the theoretical framework. The implementation has evolved into the **Four-Vector Stress Test Model**.

**Current Implementation:**
The framework has been synthesized into four primary "Stress Vectors" that predict playoff archetypes from Regular Season data:

1.  **Creation Vector:** Measures self-creation ability (efficiency on 3+ dribble shots).
2.  **Leverage Vector:** Measures clutch performance (usage and efficiency in high-pressure moments).
3.  **Pressure Vector:** Measures "Dominant Rigidity" (willingness and efficiency on tightly contested shots).
4.  **Physicality Vector (Planned):** Will measure "Force" (ability to get to the free throw line).

**See `results/predictive_model_report.md` for the current model performance.**

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
- **Scope:** 5 seasons (2019-20 to 2023-24). Expansion to 2015-16 is the next major goal.
- **Architecture:** CSV-based data lake in `data/` and `results/`.

### Core Scripts
- **`calculate_simple_resilience.py`**: The Descriptive Engine. Calculates the Dual-Grade Archetypes (RQ + Dominance).
- **`evaluate_plasticity_potential.py`**: Generates Creation and Leverage vectors.
- **`collect_shot_quality_aggregates.py`**: Collects Pressure vector raw data.
- **`calculate_shot_difficulty_features.py`**: Calculates Pressure Appetite and Resilience.
- **`train_predictive_model.py`**: Trains the XGBoost classifier.

### Next Steps
1.  **Physicality Vector:** Implement Free Throw Rate Resilience.
2.  **Historical Expansion:** Collect data for 2015-16 through 2018-19.
3.  **Model Tuning:** Hyperparameter optimization on the expanded dataset.
