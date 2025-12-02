# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Current Status & Key Insight (V2)**

The project has successfully developed a "Stylistic Stress Test" to predict Playoff Archetypes using only Regular Season data.

- **`V2 Predictive Model`**: An XGBoost Classifier that achieves **50.5% accuracy** in predicting a player's Playoff Archetype (King, Bulldozer, Sniper, Victim) based on two Regular Season "Stress Vectors":
    1.  **Creation Vector**: Measures a player's efficiency drop-off when forced to create their own shot (e.g., stats on 3+ dribbles vs. 0 dribbles).
    2.  **Leverage Vector**: Measures how a player's efficiency and usage scale in clutch situations.

- **`The "Plasticity" Pivot (The Sloan Alpha)`**: Initial plans to add a "Context Vector" (performance vs. top defenses) were superseded by a more powerful insight. A pilot study and subsequent model run have validated that **Spatial Rigidity** is the key missing variable. Our V3 model, incorporating these features, achieved **52.5% accuracy**, a notable improvement from the baseline.

## Next Developer Mission: Break 60% Accuracy

The theoretical breakthrough is complete. The path to >60% accuracy is now one of systematic machine learning refinement. Your mission is to take the V3 model and elevate it.

This involves three primary tasks:
1.  **Hyperparameter Tuning**: The current XGBoost model uses a default configuration. Systematically tune the model's hyperparameters (`n_estimators`, `max_depth`, `learning_rate`, etc.) to maximize performance.
2.  **Feature Interaction Engineering**: Create new, more powerful features by combining the existing vectors. For example, an `ADAPTABILITY_SCORE` (`CREATION_VOLUME_RATIO` * `SPATIAL_VARIANCE_DELTA`) could explicitly reward players who diversify their shot profile under a heavy creation burden.
3.  **Expand the Dataset**: The current model is trained on five seasons. Expand the data collection pipeline to include more historical seasons (e.g., back to 2015-16) to provide the model with more data to learn from.

This is the core work required to prepare the analysis for the Sloan paper.

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
