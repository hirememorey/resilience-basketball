# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Current Status & Key Insight (V4.2 - Complete)**

The project has successfully developed a complete "Stylistic Stress Test" system to predict and explain playoff resilience.

- **`V4.2 Predictive Model`**: An XGBoost Classifier that achieves **59.4% accuracy** in predicting a player's Playoff Archetype (King, Bulldozer, Sniper, Victim) based on five Regular Season "Stress Vectors":
    1.  **Creation Vector**: Measures efficiency drop-off when forced to create own shot.
    2.  **Leverage Vector**: Measures how efficiency and usage scale in clutch situations.
    3.  **Pressure Vector (V4.2 Refined)**: Measures willingness to take tight shots with **Clock Distinction** (late-clock bailouts vs. early-clock bad shots).
    4.  **Physicality Vector**: **Rim Pressure Resilience** - maintains rim attack volume in playoffs.
    5.  **Plasticity Vector**: Spatial and temporal shot distribution changes.

- **`Complete Dataset`**: **10 seasons (2015-2024)** with 5,312 player-season records and full historical context data.
- **`Clock Data Coverage`**: **100% coverage** across all seasons (2015-16 through 2024-25) with optimized parallel collection.

## Next Developer Mission: Refine Latent Star Detection

The predictive engine and component analysis are production-ready. The current focus is refining the latent star detection system to better identify undervalued players.

### Current State

**✅ Completed:**
- **Component Analysis**: Direct correlations between stress vectors and playoff outcomes (PIE, NET_RATING, etc.)
- **Playoff PIE Data**: Collected 2,175 player-seasons with 100% coverage
- **Basic Latent Star Detection**: Identifies 25 candidates with high stress profiles

**⚠️ Needs Refinement:**
- **Latent Star Detection**: Currently includes established stars (LeBron, Luka) - needs filtering to focus on true "sleeping giants"
- **Usage Filtering**: Should exclude players with high regular season usage (they're already stars)
- **Validation**: Need to validate that identified "sleeping giants" actually broke out when given opportunity

### How to Work on Latent Star Detection

1.  **Review Current Implementation**:
    *   Script: `src/nba_data/scripts/detect_latent_stars.py`
    *   Current Results: `results/latent_stars.csv`
    *   Report: `results/latent_star_detection_report.md`

2.  **Understand the Criteria**:
    *   Currently identifies players with:
        *   Top stress profile (≥80th percentile)
        *   High creation ability (top 30% in Creation Volume Ratio)
        *   High pressure resilience (top 30% in Pressure Resilience)
    *   **Problem**: This includes established stars who already have high usage

3.  **Refinement Goals**:
    *   Add usage filtering: Exclude players with RS USG% > 25% (they're already stars)
    *   Focus on role players: Target players with < 20% usage but high stress profiles
    *   Add validation: Check if identified players actually broke out in subsequent seasons
    *   Improve scoring: Weight stress vectors by their correlation with playoff outcomes

4.  **Run the Analysis**:
    ```bash
    # Run component analysis (if needed)
    python src/nba_data/scripts/component_analysis.py
    
    # Run latent star detection
    python src/nba_data/scripts/detect_latent_stars.py
    ```

5.  **Review Component Analysis** (for context):
    *   See `results/component_analysis_report.md` for stress vector correlations
    *   Use correlation data to weight stress profile scores

## Quick Start for New Developers

### 1. Understand the Vision & Current State
*   **`LUKA_SIMMONS_PARADOX.md`**: **CRITICAL.** Understands the core *descriptive* problem we solved.
*   **`IMPLEMENTATION_PLAN.md`**: The roadmap, now completed through Phase 8.
*   **`BRUNSON_TEST_ANALYSIS.md`**: First principles analysis of why certain players were identified.
*   **`MAXEY_ANALYSIS.md`**: False negative case study revealing system weaknesses.

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
python src/nba_data/scripts/collect_shot_quality_aggregates.py --seasons 2015-16 2016-17 2017-18 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 2024-25
# 3a. Generate Pressure Features with Shot Clock (V4.2 - Required for full accuracy)
python src/nba_data/scripts/collect_shot_quality_with_clock.py --seasons 2015-16 2016-17 2017-18 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 2024-25 --workers 8
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

### 4. Run Component Analysis & Latent Star Detection

```bash
# Collect playoff PIE data (if not already collected)
python src/nba_data/scripts/collect_playoff_pie.py

# Run component analysis
python src/nba_data/scripts/component_analysis.py

# Run latent star detection
python src/nba_data/scripts/detect_latent_stars.py

# Run Brunson Test for historical validation
python src/nba_data/scripts/brunson_test.py --detection-season 2020-21 --subsequent-seasons 2021-22 2022-23 2023-24
```

**Component Analysis Outputs:**
*   `data/playoff_pie_data.csv`: Playoff PIE and advanced stats
*   `results/component_analysis_correlations.csv`: Full correlation matrix
*   `results/component_analysis_report.md`: Detailed analysis with actionable insights
*   `results/component_analysis_heatmap.png`: Correlation visualizations

**Latent Star Detection Outputs:**
*   `results/latent_stars.csv`: Current latent star candidates
*   `results/latent_star_detection_report.md`: Analysis report
*   `results/brunson_test_2020_21.csv`: Historical validation results
*   `results/brunson_test_2020_21_report.md`: Validation report

---

## The "Sloan Path" (Phase 6)

We have achieved the core goal of building a predictive model. The next phase is to refine it and prepare the findings for publication.

**Core Finding Validated:** Playoff resilience is predicted by a player's ability to **create their own offense**, **absorb responsibility in the clutch**, and **force the issue** (Pressure Appetite).

**Current Status:** Model accuracy is **59.4%** with full clock data coverage. The model successfully predicts playoff archetypes using mechanistic stress vectors.

See **`IMPLEMENTATION_PLAN.md`** for the detailed roadmap.

---

## Project Structure

```
├── LUKA_SIMMONS_PARADOX.md         # The Theoretical Foundation
├── IMPLEMENTATION_PLAN.md          # The Roadmap
├── results/
│   ├── predictive_model_report.md  # Performance of our V4.2 Predictive Model
│   ├── resilience_archetypes.csv   # The Labels
│   ├── predictive_dataset.csv      # The Features
│   ├── pressure_features.csv       # The Pressure Features
│   ├── component_analysis_correlations.csv  # Stress Vector → Outcome Correlations
│   ├── component_analysis_report.md  # Component Analysis Report
│   ├── latent_stars.csv            # Latent Star Candidates
│   └── latent_star_detection_report.md  # Latent Star Analysis
├── data/
│   └── playoff_pie_data.csv        # Playoff PIE & Advanced Stats
├── src/
│   └── nba_data/scripts/
│       ├── calculate_simple_resilience.py      # Descriptive Engine (Generates Labels)
│       ├── evaluate_plasticity_potential.py  # Feature Engine (Generates Features)
│       ├── collect_shot_quality_aggregates.py # Data Collection (Pressure Vector)
│       ├── calculate_shot_difficulty_features.py # Feature Engine (Pressure Vector)
│       ├── train_predictive_model.py         # Predictive Engine (Trains Model)
│       ├── collect_playoff_pie.py            # Collect Playoff PIE Data
│       ├── component_analysis.py              # Component Analysis (Stress Vectors → Outcomes)
│       ├── detect_latent_stars.py            # Latent Star Detection (Sleeping Giants)
│       └── brunson_test.py                   # Historical Validation Framework
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
