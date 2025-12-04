# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Current Status & Key Insight (V5.0 - Usage-Aware Model Complete, Phase 3.5 Complete, Phase 3.6 Ready for Implementation)**

The project has successfully developed a complete "Stylistic Stress Test" system to predict and explain playoff resilience with **usage-aware conditional predictions**. Phase 3.5 fixes have been implemented with partial success. Phase 3.6 addresses remaining physics failures with first principles fixes.

- **`V5.0 Predictive Model`**: An XGBoost Classifier that achieves **62.22% accuracy** (improved from 59.4%) in predicting a player's Playoff Archetype (King, Bulldozer, Sniper, Victim) based on five Regular Season "Stress Vectors" **plus usage-aware features**:
    1.  **Creation Vector**: Measures efficiency drop-off when forced to create own shot.
    2.  **Leverage Vector**: Measures how efficiency and usage scale in clutch situations.
    3.  **Pressure Vector (V4.2 Refined)**: Measures willingness to take tight shots with **Clock Distinction** (late-clock bailouts vs. early-clock bad shots).
    4.  **Physicality Vector**: **Rim Pressure Resilience** - maintains rim attack volume in playoffs.
    5.  **Plasticity Vector**: Spatial and temporal shot distribution changes.

- **`Complete Dataset`**: **10 seasons (2015-2024)** with 5,312 player-season records and full historical context data.
- **`Clock Data Coverage`**: **100% coverage** across all seasons (2015-16 through 2024-25) with optimized parallel collection.

## ✅ Phase 2 Complete: Usage-Aware Conditional Prediction Model

The model now predicts playoff archetypes at **different usage levels**, enabling both use cases:

1. **Question 1 (Archetype Prediction)**: ✅ "How will this player perform in playoffs given their current role?" - Can predict at any usage level
2. **Question 2 (Latent Star Detection)**: ✅ "Who has the skills but hasn't been given opportunity?" - Can identify latent stars (age < 26, usage < 25%)

**The Solution**: Model is now **usage-aware** with `USG_PCT` as explicit feature (#1 feature: 15.0% importance) plus 5 interaction terms with top stress vectors.

**Key Principle**: Skills (stress vectors) are relatively stable across seasons. Performance (archetype) depends on opportunity (usage). The model now learns: `archetype = f(stress_vectors, usage)` ✅

### 📚 Documentation

**For current status and next steps, see:**
- **`CURRENT_STATE.md`**: **START HERE** - Current project state with Phase 3.5 results and Phase 3.6 plan
- **`PHASE3_6_IMPLEMENTATION_PLAN.md`**: **START HERE FOR PHASE 3.6** - Implementation plan for remaining physics fixes
- **`results/phase3_5_validation_report.md`**: Phase 3.5 validation results (43.8% pass rate)
- **`PHASE3_5_IMPLEMENTATION_STATUS.md`**: Phase 3.5 implementation details
- **`KEY_INSIGHTS.md`**: Hard-won lessons (updated with Phase 3.5/3.6 insights)

### Quick Reference

- **`USAGE_AWARE_MODEL_PLAN.md`**: **START HERE** - Complete implementation plan
- **`KEY_INSIGHTS.md`**: Hard-won lessons (condensed reference)
- **`LUKA_SIMMONS_PARADOX.md`**: Theoretical foundation
- **`extended_resilience_framework.md`**: Stress vectors explained
- **`results/predictive_model_report.md`**: Current model performance

## Quick Start for New Developers

### 1. Understand the Vision & Current State
*   **`USAGE_AWARE_MODEL_PLAN.md`**: **START HERE** - Complete implementation plan for usage-aware conditional prediction model
*   **`CURRENT_STATE.md`**: What exists, what's missing, and what needs to be built
*   **`KEY_INSIGHTS.md`**: Hard-won lessons (condensed reference for quick lookup)
*   **`LUKA_SIMMONS_PARADOX.md`**: **CRITICAL.** The theoretical foundation - understands the core problem we solved.
*   **`extended_resilience_framework.md`**: Stress vectors explained (what they measure and why)
*   **`results/predictive_model_report.md`**: Current model performance and architecture
*   **`IMPLEMENTATION_PLAN.md`**: Historical roadmap (for context, but focus on USAGE_AWARE_MODEL_PLAN.md)

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

### 4. Run Component Analysis

```bash
# Collect playoff PIE data (if not already collected)
python src/nba_data/scripts/collect_playoff_pie.py

# Run component analysis
python src/nba_data/scripts/component_analysis.py
```

**Component Analysis Outputs:**
*   `data/playoff_pie_data.csv`: Playoff PIE and advanced stats
*   `results/component_analysis_correlations.csv`: Full correlation matrix
*   `results/component_analysis_report.md`: Detailed analysis with actionable insights
*   `results/component_analysis_heatmap.png`: Correlation visualizations

**Note**: Latent star detection has been re-implemented in Phase 2. See `src/nba_data/scripts/detect_latent_stars_v2.py` for the new implementation with usage-aware conditional predictions.

---

## The "Sloan Path" (Phase 6)

We have achieved the core goal of building a predictive model. The next phase is to refine it and prepare the findings for publication.

**Core Finding Validated:** Playoff resilience is predicted by a player's ability to **create their own offense**, **absorb responsibility in the clutch**, and **force the issue** (Pressure Appetite).

**Current Status:** Model accuracy is **62.22%** (improved from 59.4%) with full clock data coverage and usage-aware features. The model successfully predicts playoff archetypes using mechanistic stress vectors **at different usage levels**.

**Next Step:** Phase 3.5 Implementation - Phase 3 fixes were implemented but validation revealed fundamental flaws:
1. ⚠️ Usage-Dependent Feature Weighting - Failed (linear scaling doesn't cross tree model boundaries)
2. ⚠️ Context-Adjusted Efficiency - Cannot be applied (missing data)
3. ⚠️ Fragility Gate - Failed (used ratio instead of absolute volume)

**Phase 3.5 Fixes**:
1. Switch fragility gate to `RS_RIM_APPETITE` (absolute volume) instead of `RIM_PRESSURE_RESILIENCE` (ratio)
2. Implement projected volume features instead of linear scaling
3. Calculate `RS_CONTEXT_ADJUSTMENT` data before re-validation

See **`CURRENT_STATE.md`** for current status and **`PHASE3_5_IMPLEMENTATION_PLAN.md`** for implementation plan. Phase 3 validation: 6/14 passed (42.9%), expected 10-11/14 (71-79%) after Phase 3.5.

---

## Project Structure

```
├── USAGE_AWARE_MODEL_PLAN.md       # START HERE - Implementation plan for usage-aware model
├── CURRENT_STATE.md                # What exists, what's missing, what needs to be built
├── KEY_INSIGHTS.md                 # Hard-won lessons (quick reference)
├── LUKA_SIMMONS_PARADOX.md         # The Theoretical Foundation
├── extended_resilience_framework.md # Stress Vectors Explained
├── IMPLEMENTATION_PLAN.md          # Historical Roadmap (for context)
├── results/
│   ├── predictive_model_report.md  # Performance of our V4.2 Predictive Model
│   ├── resilience_archetypes.csv   # The Labels
│   ├── predictive_dataset.csv      # The Features
│   ├── pressure_features.csv       # The Pressure Features
│   ├── component_analysis_correlations.csv  # Stress Vector → Outcome Correlations
│   └── component_analysis_report.md  # Component Analysis Report
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
│       └── component_analysis.py              # Component Analysis (Stress Vectors → Outcomes)
├── models/
│   └── resilience_xgb.pkl          # The Trained Model
├── archive/
│   └── latent_star_detection/      # Archived latent star detection work (paused)
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
