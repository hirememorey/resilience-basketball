# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Current Status:** ✅ **CRUCIBLE-WEIGHTED TRAINING IMPLEMENTED** - Model now learns from physics-based loss function that prioritizes high-stress moments. Accuracy: 52.31% with principled weighting. **Latent Star Detection: 52.4% pass rate (22/42)**. **Overall Star Prediction: 56.6% accuracy (325/574)**. Next developer: Implement Synthetic Crucible v2 for improved latent star detection.

---

## Quick Start

### 1. Understand the Project
- **`ACTIVE_CONTEXT.md`** - **START HERE** - Current project state, metrics, and next priorities
- **`LUKA_SIMMONS_PARADOX.md`** - Theoretical foundation (why we built this)
- **`2D_RISK_MATRIX_IMPLEMENTATION.md`** - ✅ **COMPLETE** - 2D framework implementation
- **`src/streamlit_app/README.md`** - Interactive app documentation
- **`KEY_INSIGHTS.md`** - Critical lessons to avoid mistakes (see Insight #59: Crucible-Weighted Training)

### 2. Set Up Environment
```bash
# Install dependencies
pip install pandas numpy scikit-learn scipy tenacity requests xgboost tqdm tabulate seaborn matplotlib joblib

# Create required directories
mkdir -p data/cache models results logs
```

### 3. Run the Pipeline
```bash
# 1. Generate Historical Archetypes (The Labels)
python src/nba_data/scripts/calculate_simple_resilience.py

# 2. Generate Predictive Features (The Stress Vectors)
python src/nba_data/scripts/evaluate_plasticity_potential.py
python src/nba_data/scripts/calculate_physicality_features.py

# 3. Generate Pressure Features with Shot Clock
python src/nba_data/scripts/collect_shot_quality_with_clock.py --seasons 2015-16 2016-17 2017-18 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 2024-25 --workers 8
python src/nba_data/scripts/calculate_shot_difficulty_features.py

# 3.5. Generate Plasticity Features (requires playoff shot charts)
python src/nba_data/scripts/calculate_shot_plasticity.py --seasons 2015-16 2016-17 2017-18 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 2024-25
python src/nba_data/scripts/combine_plasticity_scores.py

# 4. Train the Predictive Model (RFE-optimized, recommended)
python src/nba_data/scripts/train_rfe_model.py
```

**Key Outputs:**
- `results/resilience_archetypes.csv`: Playoff archetypes (labels)
- `results/predictive_dataset.csv`: Stress vectors (features)
- `results/pressure_features.csv`: Pressure vector features
- `models/resilience_xgb_rfe_15.pkl`: **CURRENT MODEL** (16 features including physics-based friction simulation, 58.15% accuracy, RS-only, temporal split)

### 3.5. Combine Plasticity Data (if recalculating plasticity)
```bash
# If you recalculated plasticity scores, combine them into the comprehensive dataset
python src/nba_data/scripts/combine_plasticity_scores.py
# Or use the convenience script:
./scripts/combine_plasticity.sh
```

# 4. Run Validation Tests
```bash
# Run latent star detection test suite (elevated usage projections)
python tests/validation/test_latent_star_cases.py

# Run overall star prediction test suite (current usage, Franchise Cornerstone classification)
python -m tests.validation.test_overall_star_prediction

# Run expanded dataset predictions (optional)
python run_expanded_predictions.py --min-minutes 500 --max-age 25
```

### 5. Launch Interactive App
```bash
# Generate 2D data for all players (one-time setup)
python scripts/generate_2d_data_for_all.py

# Launch the Streamlit app
python scripts/run_streamlit_app.py
```

**App Features:**
- **2D Risk Matrix**: Interactive scatter plot with Performance vs Dependence quadrants
- **Stress Vector Profiles**: Radar charts showing percentile rankings across 5 dimensions
- **Usage Simulations**: "What-if" scenarios at different usage levels
- **Complete Coverage**: 5,312 players with 2D risk assessments

---

## Interactive Streamlit App

The project now includes a fully functional web application for exploring the 2D Risk Matrix:

### Key Capabilities
- **Player Analysis**: Select any player from 2015-2025 seasons
- **Risk Assessment**: View Performance vs Dependence scores with proper categorization
- **Stress Profiles**: Radar charts showing percentile rankings for Creation, Leverage, Pressure, Physicality, Plasticity
- **Usage Projections**: Simulate archetype changes at different usage levels using Universal Projection

### Data Coverage
- **5,312 Players**: Complete dataset from 2015-2025
- **2D Risk Matrix**: Performance + Dependence scores for all players
- **Stress Vectors**: Creation (100%), Leverage (60%), Pressure (85%), Physicality (100%), Plasticity (17%)
- **Interactive Features**: Real-time usage simulations and comparisons

### Risk Categories
```
Franchise Cornerstone: High Performance + Low Dependence (22.9%)
Luxury Component: High Performance + High Dependence (2.1%)
Depth: Low Performance + Low Dependence (52.1%)
Avoid: Low Performance + High Dependence (22.9%)
```

---

## Current Model

**Algorithm:** XGBoost Classifier (Multi-Class)
**Features:** 16 core features (RFE-optimized from 65, RS-only, includes physics-based friction simulation)
**Accuracy:** **52.31%** (Crucible-Weighted Training with principled loss function)
**Test Suite Performance:**
- **Latent Star Detection:** 52.4% (22/42) - Principled regression due to honest uncertainty modeling
- **Overall Star Prediction:** 56.6% (325/574) - Tests Franchise Cornerstone classification at current usage
- **Enhanced Diagnostics:** 63+ column analysis available for complete feature-level debugging (Two Doors components included)

**Key Innovation:** Crucible-Weighted Training - Model prioritizes learning from high-stress moments (playoffs, high-quality opponents, efficient clutch situations) rather than treating all data points equally.

### Top 12 Features (RS-Only, Crucible-Weighted Training)
1. `USG_PCT` (42.3% importance) - Usage level (most important in crucible context)
2. `PROJECTED_PLAYOFF_OUTPUT` (8.4% importance) - Physics-based playoff simulation
3. `FRICTION_COEFF_0_DRIBBLE` (5.7% importance) - Off-ball efficiency drop-off
4. `SHOT_QUALITY_GENERATION_DELTA` (5.6% importance) - Shot quality generation ability
5. `USG_PCT_X_CREATION_VOLUME_RATIO` (5.3% importance) - Usage × creation efficiency
6. `USG_PCT_X_LEVERAGE_USG_DELTA` (5.0% importance) - Usage × clutch usage scaling
7. `HELIO_ABOVE_REPLACEMENT_VALUE` (4.9% importance) - Volume immunity measure
8. `FRICTION_COEFF_ISO` (4.9% importance) - Isolation efficiency drop-off
9. `INEFFICIENT_VOLUME_SCORE` (4.8% importance) - Efficiency penalty for volume
10. `USG_PCT_X_EFG_ISO_WEIGHTED` (4.6% importance) - Usage × isolation efficiency
11. `PROJECTED_PLAYOFF_PPS` (4.4% importance) - Projected playoff points per shot
12. `EFG_PCT_0_DRIBBLE` (4.1% importance) - Catch-and-shoot efficiency

**Key Insight:** Usage-aware features dominate (5 of 10 features, 65.9% combined importance).

---

## The Five Stress Vectors

The model predicts playoff archetypes based on five Regular Season "Stress Vectors":

1. **Creation Vector**: Measures efficiency drop-off when forced to create own shot (3+ dribble shots)
2. **Leverage Vector**: Measures how efficiency and usage scale in clutch situations
3. **Pressure Vector**: Measures willingness to take tight shots with **Clock Distinction**:
   - **Late Clock Pressure** (7-4s, 4-0s): Bailout shots - valuable ability
   - **Early Clock Pressure** (22-18s, 18-15s): Bad shot selection - negative signal
4. **Physicality Vector**: **Rim Pressure Resilience** - maintains rim attack volume in playoffs
5. **Plasticity Vector**: Spatial and temporal shot distribution adaptability

---

## The Archetype System

Four archetypes based on two axes:

| Archetype | RQ (Resilience) | Dominance | Example |
|-----------|-----------------|-----------|---------|
| **King** | High (>0.95) | High (>20) | Jokić, Giannis |
| **Bulldozer** | Low (<0.95) | High (>20) | Luka, LeBron |
| **Sniper** | High (>0.95) | Low (<20) | Aaron Gordon |
| **Victim** | Low (<0.95) | Low (<20) | Ben Simmons |

- **Resilience Quotient (RQ)**: Adaptability (volume × efficiency ratio)
- **Dominance Score**: Absolute value (points per 75 possessions)

---

## Usage-Aware Conditional Predictions

The model can predict at **any usage level**, enabling two use cases:

1. **Archetype Prediction**: "How will this player perform in playoffs given their current role?"
2. **Latent Star Detection**: "Who has the skills but hasn't been given opportunity?"

**Key Principle:** Skills (stress vectors) are relatively stable across seasons. Performance (archetype) depends on opportunity (usage). The model learns: `archetype = f(stress_vectors, usage)`

**Example:** Jalen Brunson (2020-21)
- At 19.6% usage: "Victim" (0.77% star-level) ✅ Correct
- At 32% usage: "Bulldozer" (94.02% star-level) ✅ Correct

---

## Key Files

### Core Scripts
- `src/nba_data/scripts/predict_conditional_archetype.py` - Main prediction function
- `src/nba_data/scripts/detect_latent_stars.py` - Latent star detection
- `src/nba_data/scripts/train_rfe_model.py` - Train RFE-optimized model

### Test Scripts
- `test_latent_star_cases.py` - Latent star detection validation (elevated usage projections)
- `test_overall_star_prediction.py` - Overall star prediction validation (Franchise Cornerstone classification at current usage)
- `test_2d_risk_matrix.py` - 2D Risk Matrix validation suite
- `run_expanded_predictions.py` - Run model on expanded dataset (Age ≤ 25, Min minutes)
- `analyze_model_misses.py` - Diagnostic script to analyze specific model misses

### Data Files
- `results/predictive_dataset.csv` - Stress vectors (5,312 player-seasons)
- `results/resilience_archetypes.csv` - Playoff archetypes (labels)
- `results/pressure_features.csv` - Pressure vector features

### Model Files
- `models/resilience_xgb_rfe_10.pkl` - **CURRENT MODEL** (10 features)
- `models/resilience_xgb.pkl` - Full model (65 features, fallback)

---

## Key Principles

1. **First Principles Thinking:** Don't just measure *what* happened. Isolate the *stylistic shifts* that explain *why*.
2. **Resilience = Efficiency × Volume:** The "Abdication Tax" is real. Passivity is failure.
3. **Self-Creation is King:** The strongest predictor of playoff success is the ability to generate your own offense.
4. **Dominance is Rigid:** Some players (Shaq/Giannis) are resilient not because they adapt, but because they impose their will.

---

## Documentation

- **`ACTIVE_CONTEXT.md`** - **START HERE** - Current project state, metrics, and priorities
- **`KEY_INSIGHTS.md`** - Hard-won lessons (63+ principles, see #59: Crucible-Weighted Training)
- **`LUKA_SIMMONS_PARADOX.md`** - Theoretical foundation
- **`2D_RISK_MATRIX_IMPLEMENTATION.md`** - ✅ **COMPLETE** - 2D framework implementation
- **`UNIVERSAL_PROJECTION_IMPLEMENTATION.md`** - ✅ **COMPLETE** - Universal projection implementation (fixes "Static Avatar" Fallacy)
- **`results/latent_star_test_cases_report_trust_fall.md`** - Trust Fall experiment results
- **`results/latent_star_test_cases_report.md`** - Latest latent star validation results
- **`results/overall_star_prediction_test_report.md`** - Overall star prediction validation results
- **`results/latent_star_test_cases_diagnostics.csv`** - Enhanced diagnostic data (63+ columns) for latent star test cases
- **`results/overall_star_prediction_diagnostics.csv`** - Enhanced diagnostic data (62+ columns) for overall star prediction test cases
- **`results/universal_projection_validation.md`** - Universal projection validation results
- **`results/rfe_model_comparison.md`** - RFE model analysis
- **`results/expanded_predictions.csv`** - Expanded dataset predictions (1,849 player-seasons)
- **`results/model_misses_analysis.md`** - Analysis of model misses and recommendations

---

## Support

- **Technical questions:** Review `src/nba_data/api/nba_stats_client.py` for rate limit handling
- **Conceptual questions:** Review `LUKA_SIMMONS_PARADOX.md`
