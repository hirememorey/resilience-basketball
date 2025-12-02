# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Current Status:**
*   ✅ **Data Foundation:** Complete historical dataset (2015-2024).
*   ✅ **The Paradox Solved:** The **Dual-Grade Archetype System** correctly classifies historical player performance (e.g., Jokić, Simmons).
*   ✅ **Predictive Engine V1 Complete:** We have successfully built a model that **predicts Playoff Archetypes from Regular Season data with 50.5% accuracy** (2x random chance).
*   ✅ **Mechanism Validated:** The model confirmed that **Self-Creation Volume** and **Clutch Usage Scaling** are the strongest predictors of playoff resilience.

---

## Quick Start for New Developers

### 1. Understand the Vision & Current State
*   **`LUKA_SIMMONS_PARADOX.md`**: **CRITICAL.** Understands the core *descriptive* problem we solved.
*   **`IMPLEMENTATION_PLAN.md`**: The roadmap, updated to reflect the completion of the V1 predictive model.
*   **`results/predictive_model_report.md`**: **NEW.** Summarizes the performance and findings of our successful predictive model.

### 2. Set Up Environment
```bash
# Install dependencies
pip install pandas numpy scikit-learn scipy tenacity requests xgboost tqdm tabulate seaborn matplotlib joblib

# Create required directories
mkdir -p data/cache models results logs
```

### 3. Run the Full Pipeline
This generates the two key artifacts: the *labels* (Archetypes) and the *features* (Stress Vectors), then trains the model.

```bash
# 1. Generate Historical Archetypes (The Labels)
# This is the "Descriptive Engine" that defines our ground truth.
python src/nba_data/scripts/calculate_simple_resilience.py

# 2. Generate Predictive Features (The Stress Vectors)
# This is the "Stylistic Stress Test" that analyzes Regular Season data.
python src/nba_data/scripts/evaluate_plasticity_potential.py

# 3. Train the Predictive Model
# This uses the features to predict the labels.
python src/nba_data/scripts/train_predictive_model.py
```

**Key Outputs:**
*   `results/resilience_archetypes.csv`: The descriptive labels.
*   `results/predictive_dataset.csv`: The predictive features.
*   `models/resilience_xgb.pkl`: The trained XGBoost model.
*   `results/feature_importance.png`: Explains *why* the model works.

---

## The "Sloan Path" (Phase 6)

We have achieved the core goal of building a predictive model. The next phase is to refine it and prepare the findings for publication.

**Core Finding Validated:** Playoff resilience is predicted by a player's ability to **create their own offense** and **absorb responsibility in the clutch**.

**Next Step:** Improve model accuracy to >60% by incorporating the "Context Vector" (performance vs. top defenses) and prepare a draft of the Sloan paper.

See **`IMPLEMENTATION_PLAN.md`** for the detailed roadmap.

---

## Project Structure

```
├── LUKA_SIMMONS_PARADOX.md         # The Theoretical Foundation
├── IMPLEMENTATION_PLAN.md          # The Roadmap
├── results/
│   ├── predictive_model_report.md  # Performance of our V1 Predictive Model
│   ├── resilience_archetypes.csv   # The Labels
│   └── predictive_dataset.csv      # The Features
├── src/
│   └── nba_data/scripts/
│       ├── calculate_simple_resilience.py      # Descriptive Engine (Generates Labels)
│       ├── evaluate_plasticity_potential.py  # Feature Engine (Generates Features)
│       └── train_predictive_model.py         # Predictive Engine (Trains Model)
├── models/
│   └── resilience_xgb.pkl          # The Trained Model
```

---

## Key Principles

1.  **First Principles Thinking:** Don't just measure *what* happened. Isolate the *stylistic shifts* that explain *why*.
2.  **Resilience = Efficiency × Volume:** The "Abdication Tax" is real. Passivity is failure.
3.  **Self-Creation is King:** The strongest predictor of playoff success is the ability to generate your own offense.

---

## Support
*   **Technical questions:** Review `src/nba_data/api/nba_stats_client.py` to see how we handle rate limits.
*   **Conceptual questions:** Review `LUKA_SIMMONS_PARADOX.md`.
