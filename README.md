# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Current Status & Key Insight (V4)**

The project has successfully developed a "Stylistic Stress Test" to predict Playoff Archetypes using only Regular Season data.

- **`V4 Predictive Model`**: An XGBoost Classifier that achieves **57.2% accuracy** in predicting a player's Playoff Archetype (King, Bulldozer, Sniper, Victim) based on four Regular Season "Stress Vectors":
    1.  **Creation Vector**: Measures a player's efficiency drop-off when forced to create their own shot.
    2.  **Leverage Vector**: Measures how a player's efficiency and usage scale in clutch situations.
    3.  **Pressure Vector**: Measures a player's willingness to take tight shots (`Pressure Appetite`).
    4.  **Physicality Vector (NEW)**: Measures a player's ability to get to the line (`FTr Resilience`), proxying for "Force."

- **`Historical Expansion`**: We have expanded the training dataset to **9 seasons (2015-2024)**, giving the model nearly double the examples to learn from.

## Next Developer Mission: The Sloan Write-Up

The predictive engine is now robust. The path forward is to finalize the findings and draft the paper.

1.  **Review the Results**: See `results/predictive_model_report.md` (needs update with V4 results).
2.  **Draft the Paper**: Synthesize the narrative around "Stress Vectors" predicting resilience.

## Quick Start for New Developers

### 1. Understand the Vision & Current State
*   **`LUKA_SIMMONS_PARADOX.md`**: **CRITICAL.** Understands the core *descriptive* problem we solved.
*   **`IMPLEMENTATION_PLAN.md`**: The roadmap, now completed through Phase 7.

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
python src/nba_data/scripts/calculate_simple_resilience.py

# 2. Generate Predictive Features (The Stress Vectors)
python src/nba_data/scripts/evaluate_plasticity_potential.py
python src/nba_data/scripts/calculate_physicality_features.py # NEW V4

# 3. Generate Pressure Features
python src/nba_data/scripts/collect_shot_quality_aggregates.py --seasons 2015-16 2016-17 2017-18 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24
python src/nba_data/scripts/calculate_shot_difficulty_features.py

# 4. Train the Predictive Model
python src/nba_data/scripts/train_predictive_model.py
```

**Key Outputs:**
*   `results/resilience_archetypes.csv`: The descriptive labels.
*   `results/predictive_dataset.csv`: The predictive features.
*   `results/pressure_features.csv`: The pressure vector features.
*   `models/resilience_xgb.pkl`: The trained XGBoost model.
*   `results/feature_importance.png`: Explains *why* the model works.

---

## The "Sloan Path" (Phase 6)

We have achieved the core goal of building a predictive model. The next phase is to refine it and prepare the findings for publication.

**Core Finding Validated:** Playoff resilience is predicted by a player's ability to **create their own offense**, **absorb responsibility in the clutch**, and **force the issue** (Pressure Appetite).

**Next Step:** Improve model accuracy to >60% by incorporating the "Physicality Vector" and expanding the historical dataset.

See **`IMPLEMENTATION_PLAN.md`** for the detailed roadmap.

---

## Project Structure

```
├── LUKA_SIMMONS_PARADOX.md         # The Theoretical Foundation
├── IMPLEMENTATION_PLAN.md          # The Roadmap
├── results/
│   ├── predictive_model_report.md  # Performance of our V3 Predictive Model
│   ├── resilience_archetypes.csv   # The Labels
│   ├── predictive_dataset.csv      # The Features
│   └── pressure_features.csv       # The Pressure Features (New)
├── src/
│   └── nba_data/scripts/
│       ├── calculate_simple_resilience.py      # Descriptive Engine (Generates Labels)
│       ├── evaluate_plasticity_potential.py  # Feature Engine (Generates Features)
│       ├── collect_shot_quality_aggregates.py # Data Collection (Pressure Vector)
│       ├── calculate_shot_difficulty_features.py # Feature Engine (Pressure Vector)
│       └── train_predictive_model.py         # Predictive Engine (Trains Model)
├── models/
│   └── resilience_xgb.pkl          # The Trained Model
```

---

## Key Principles

1.  **First Principles Thinking:** Don't just measure *what* happened. Isolate the *stylistic shifts* that explain *why*.
2.  **Resilience = Efficiency × Volume:** The "Abdication Tax" is real. Passivity is failure.
3.  **Self-Creation is King:** The strongest predictor of playoff success is the ability to generate your own offense.
4.  **Dominance is Rigid:** Some players (Shaq/Giannis) are resilient not because they adapt, but because they impose their will. We measure this as "Pressure Appetite."

---

## Support
*   **Technical questions:** Review `src/nba_data/api/nba_stats_client.py` to see how we handle rate limits.
*   **Conceptual questions:** Review `LUKA_SIMMONS_PARADOX.md`.
