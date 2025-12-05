# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Current Status:** 2D Risk Matrix implementation complete ✅ | Data-driven thresholds calculated | RFE-optimized model with **63.33% accuracy** and **87.5% test case pass rate** (14/16 with gates). Model uses 10 core features to predict playoff archetypes with usage-aware conditional predictions. **2D framework** separates Performance (outcomes) from Dependence (portability) using data-driven thresholds (33rd/66th percentiles).

---

## Quick Start

### 1. Understand the Project
- **`LUKA_SIMMONS_PARADOX.md`** - **START HERE** - Theoretical foundation (why we built this)
- **`CURRENT_STATE.md`** - What exists, current metrics, what works
- **`2D_RISK_MATRIX_IMPLEMENTATION.md`** - ✅ **COMPLETE** - 2D framework implementation
- **`NEXT_STEPS.md`** - What to work on next (D'Angelo Russell investigation)
- **`KEY_INSIGHTS.md`** - Critical lessons to avoid mistakes (see Insight #37: Trust Fall & Ground Truth Trap)

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

# 4. Train the Predictive Model (RFE-optimized, recommended)
python src/nba_data/scripts/train_rfe_model.py
```

**Key Outputs:**
- `results/resilience_archetypes.csv`: Playoff archetypes (labels)
- `results/predictive_dataset.csv`: Stress vectors (features)
- `results/pressure_features.csv`: Pressure vector features
- `models/resilience_xgb_rfe_10.pkl`: **CURRENT MODEL** (10 features, 63.33% accuracy)

### 4. Run Validation Tests
```bash
# Run test suite
python test_latent_star_cases.py
```

---

## Current Model

**Algorithm:** XGBoost Classifier (Multi-Class)  
**Features:** 10 core features (RFE-optimized from 65)  
**Accuracy:** 63.33% (899 player-seasons, 2015-2024)  
**Test Case Pass Rate:** 87.5% (14/16)

### Top 10 Features
1. `USG_PCT` (28.9% importance) - Usage level
2. `USG_PCT_X_EFG_ISO_WEIGHTED` (18.7% importance) - Usage × Isolation efficiency
3. `NEGATIVE_SIGNAL_COUNT` (10.5% importance) - Gate feature
4. `EFG_PCT_0_DRIBBLE` (6.8% importance) - Catch-and-shoot efficiency
5. `LEVERAGE_USG_DELTA` (6.1% importance) - #1 predictor (Abdication Detector)
6. `USG_PCT_X_RS_PRESSURE_APPETITE` (5.9% importance)
7. `PREV_RS_PRESSURE_RESILIENCE` (5.9% importance)
8. `LATE_CLOCK_PRESSURE_APPETITE_DELTA` (5.9% importance)
9. `USG_PCT_X_CREATION_VOLUME_RATIO` (5.7% importance)
10. `USG_PCT_X_LEVERAGE_USG_DELTA` (5.7% importance)

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
- `test_latent_star_cases.py` - Validation test suite (16 critical cases)

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

- **`CURRENT_STATE.md`** - Detailed current state, what exists, known issues
- **`2D_RISK_MATRIX_IMPLEMENTATION.md`** - ✅ **COMPLETE** - 2D framework implementation
- **`NEXT_STEPS.md`** - What to work on next (D'Angelo Russell investigation)
- **`KEY_INSIGHTS.md`** - Hard-won lessons (37+ principles, see #37: Trust Fall & Ground Truth Trap)
- **`LUKA_SIMMONS_PARADOX.md`** - Theoretical foundation
- **`results/latent_star_test_cases_report_trust_fall.md`** - Trust Fall experiment results
- **`results/latent_star_test_cases_report.md`** - Latest validation results (with gates)
- **`results/rfe_model_comparison.md`** - RFE model analysis

---

## Support

- **Technical questions:** Review `src/nba_data/api/nba_stats_client.py` for rate limit handling
- **Conceptual questions:** Review `LUKA_SIMMONS_PARADOX.md`
