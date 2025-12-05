# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Current Status & Key Insight (V5.2 - RFE Model Complete ✅)**

The project has successfully developed a complete "Stylistic Stress Test" system to predict and explain playoff resilience with **usage-aware conditional predictions**. **RFE analysis identified optimal feature set (10 features)**, achieving **63.33% accuracy** and **81.2% test case pass rate** (improved from 62.5%). See `NEXT_STEPS.md` for remaining edge cases.

- **`V5.2 Predictive Model (RFE-Optimized)`**: An XGBoost Classifier that achieves **63.33% accuracy** with **10 core features** (reduced from 65) in predicting a player's Playoff Archetype (King, Bulldozer, Sniper, Victim) based on five Regular Season "Stress Vectors" **with usage-aware conditional predictions**:
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

**The Solution**: Model is now **usage-aware** with `USG_PCT` as explicit feature (#1 feature: 28.9% importance in RFE model) plus 4 interaction terms with top stress vectors. **RFE analysis revealed that 10 features achieve optimal accuracy (63.33%), validating that usage-aware features are the core innovation.**

**Key Principle**: Skills (stress vectors) are relatively stable across seasons. Performance (archetype) depends on opportunity (usage). The model now learns: `archetype = f(stress_vectors, usage)` ✅

### 📚 Documentation

**For current status and next steps, see:**
- **`ONBOARDING.md`**: **START HERE** - Onboarding guide for new developers
- **`CURRENT_STATE.md`**: Current project state (updated with RFE model)
- **`NEXT_STEPS.md`**: Next priorities (Phase 4.2 edge case fixes)
- **`KEY_INSIGHTS.md`**: Hard-won lessons (critical reference, updated with RFE insights)
- **`results/rfe_model_comparison.md`**: RFE model analysis and results

### Quick Reference

- **`PHASE4_IMPLEMENTATION_PLAN.md`**: **START HERE** - Phase 4 implementation plan
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
# Option A: Train RFE-optimized model (recommended - 10 features)
python src/nba_data/scripts/train_rfe_model.py

# Option B: Train full model (65 features)
python src/nba_data/scripts/train_predictive_model.py
```

**Key Outputs:**
*   `results/resilience_archetypes.csv`: The descriptive labels.
*   `results/predictive_dataset.csv`: The predictive features.
*   `results/pressure_features.csv`: The pressure vector features.
*   `models/resilience_xgb_rfe_10.pkl`: **CURRENT MODEL** - RFE-optimized (10 features, 63.33% accuracy)
*   `models/resilience_xgb.pkl`: Full model (65 features, fallback)
*   `results/feature_importance_rfe_10.png`: Feature importance for RFE model.

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

**Current Status:** Model accuracy is **63.33%** (RFE-optimized with 10 features) with **81.2% test case pass rate** (improved from 62.5%). The model successfully predicts playoff archetypes using mechanistic stress vectors **at different usage levels**.

**RFE Model Complete:** Feature Simplification implemented:
1. ✅ **RFE Analysis** - Identified optimal feature count (10 features)
2. ✅ **Model Retraining** - Retrained with top 10 RFE-selected features
3. ✅ **Model Accuracy** - 63.33% (improved from 62.89% with 65 features)
4. ✅ **Test Case Pass Rate** - 81.2% (13/16) - Improved from 62.5% (+18.7 pp)

**Key Finding**: RFE analysis revealed that 10 features achieve peak accuracy. Most trajectory and gate features (55 of 65) add noise, not signal. Usage-aware features dominate (5 of 10 features, 65.9% combined importance).

**Key Achievements**:
- ✅ **RFE model achieves 81.2% pass rate** (13/16) - Major improvement from 62.5%
- ✅ **True positive detection: 87.5%** (7/8) - Improved from 50.0% (+37.5 pp)
- ✅ **Oladipo, Haliburton, Maxey all passing** - Fixed with RFE model
- ✅ **Sabonis correctly filtered** (30.00%) - Validates "Dependency = Fragility" principle
- ⚠️ **Poole still failing** (95.50%) - Tax needs strengthening
- ⚠️ **Bridges still failing** (30.00%) - Needs exemption refinement
- ⚠️ **Markkanen close** (60.37%) - Only 4.63% away from threshold

**Key Insight**: RFE analysis validated that feature bloat was real. Simplifying to 10 core features improved both accuracy and test case pass rate. Usage-aware features are the core innovation (5 of 10 features, 65.9% importance).

See **`CURRENT_STATE.md`** for current status, **`results/rfe_model_comparison.md`** for RFE analysis, and **`NEXT_STEPS.md`** for remaining edge cases.

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
