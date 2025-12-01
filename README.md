# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Current Status:**
*   ✅ **Descriptive Engine:** Fully functional. Calculates "Resilience Scores" for historical playoffs based on performance vs. expectation (accounting for defensive context).
*   ✅ **Predictive Engine:** Fully functional. Predicts future resilience with positive R² using "Performance vs. Top-10 Defenses" and "Consistency" metrics.
*   🚧 **Mechanistic Engine (The Sloan Path):** In progress. Developing "Shot Diet Plasticity" metrics to explain *how* resilient players adapt their game.

---

## Quick Start for New Developers

### 1. Understand the Vision
*   **`README.md`**: You're here! High-level overview.
*   **`IMPLEMENTATION_PLAN.md`**: **CRITICAL.** Read this to understand the "Sloan Path" and your specific next steps.
*   **`HISTORICAL_CONTEXT.md`**: (Optional) Lessons learned from past failures (why we don't use simple ratios anymore).

### 2. Set Up Environment
```bash
# Install dependencies
pip install pandas numpy scikit-learn scipy tenacity requests xgboost tqdm

# Create required directories
mkdir -p data/cache models results logs
```

### 3. Run the Predictive Pipeline
This pipeline collects data, generates features, trains the predictive model, and outputs resilience scores.

```bash
# 1. Collect Data (Regular Season Game Logs) - Takes ~20 mins for 6 seasons
python src/nba_data/scripts/collect_rs_game_logs.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 --workers 5

# 2. Generate Predictive Features (Consistency, vs Top-10)
python src/nba_data/scripts/generate_predictive_features.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24

# 3. Assemble Training Data
python src/nba_data/scripts/assemble_predictive_dataset.py

# 4. Train Model & Evaluate
python src/nba_data/scripts/train_predictive_model.py
```

---

## The "Sloan Path" (Next Phase)

We are aiming for a paper worthy of the **MIT Sloan Sports Analytics Conference**. To do this, we must move beyond *prediction* to *explanation*.

**Core Hypothesis:** Resilience is "Shot Diet Plasticity"—the ability to change *where* and *how* you shoot when playoff defenses take away your primary options.

**Your Mission:**
1.  Collect Shot Chart data for RS vs. Playoffs.
2.  Quantify the "Shot Diet Shift" (e.g., Hellinger Distance between heatmaps).
3.  Correlate this shift with our existing Resilience Scores.

See **`IMPLEMENTATION_PLAN.md`** for the detailed roadmap.

---

## Project Structure

```
├── IMPLEMENTATION_PLAN.md          # **START HERE** - The Roadmap
├── DATA_REQUIREMENTS.md            # Data specifications (updated for Shot Charts)
├── src/
│   └── nba_data/
│       ├── api/                    # NBA Stats API client
│       └── scripts/                # All implementation scripts
├── data/                           # Data storage
│   ├── rs_game_logs_*.csv          # Granular RS data
│   ├── predictive_features_*.csv   # Feature engineering output
│   └── predictive_model_training_data.csv
├── models/                         # Trained XGBoost models
└── results/                        # Final Resilience Scores
```

---

## Key Principles

1.  **First Principles Thinking:** Don't just measure *what* happened. Ask *why* it happened given the context.
2.  **Mechanism over Correlation:** For Sloan, we need to explain the *mechanism* (e.g., "He stopped driving and started pulling up").
3.  **Simplicity in Execution:** Don't build a complex framework until a simple metric (like Shot Distance Delta) fails.

---

## Support
*   **Technical questions:** Review `src/nba_data/api/nba_stats_client.py` to see how we handle rate limits.
*   **Conceptual questions:** Review `IMPLEMENTATION_PLAN.md`.
