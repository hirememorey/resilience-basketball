# Current State: NBA Playoff Resilience Engine

**Date**: December 2025  
**Status**: Phase 0 & 1 Complete - Ready for Phase 2 (Usage-Aware Model Implementation)

---

## Project Overview

**Goal**: Identify players who consistently perform better than expected in the playoffs and explain *why* using mechanistic insights.

**Current Model**: XGBoost Classifier that predicts playoff archetypes (King, Bulldozer, Sniper, Victim) from regular season stress vectors.

**Accuracy**: 59.4% (899 player-seasons, 2015-2024)

---

## What Exists (Current State)

### Data Pipeline

**Complete Dataset**: 10 seasons (2015-2024), 5,312 player-season records

**Key Data Files**:
- `results/predictive_dataset.csv`: Stress vectors (5,312 player-seasons)
- `results/resilience_archetypes.csv`: Playoff archetypes (labels)
- `results/pressure_features.csv`: Pressure vector features
- `data/playoff_pie_data.csv`: Playoff advanced stats

**Data Coverage**:
- Stress vectors: 100% coverage
- Usage (USG_PCT): 100% coverage (added in Phase 1)
- Age: 100% coverage (added in Phase 1)
- Clock data: 100% coverage (all seasons)

### Model Architecture

**Algorithm**: XGBoost Classifier (Multi-Class)

**Features (32 total)**:
- **Creation Vector**: CREATION_TAX, CREATION_VOLUME_RATIO
- **Leverage Vector**: LEVERAGE_TS_DELTA, LEVERAGE_USG_DELTA, CLUTCH_MIN_TOTAL
- **Pressure Vector**: RS_PRESSURE_APPETITE, RS_PRESSURE_RESILIENCE, clock features (late/early)
- **Physicality Vector**: RS_FTr, FTr_RESILIENCE, RIM_PRESSURE_RESILIENCE
- **Plasticity Vector**: SHOT_DISTANCE_DELTA, SPATIAL_VARIANCE_DELTA
- **Context Vector**: QOC_TS_DELTA, opponent defensive context

**Model File**: `models/resilience_xgb.pkl`

**Training Script**: `src/nba_data/scripts/train_predictive_model.py`

### Key Scripts

**Feature Generation**:
- `evaluate_plasticity_potential.py`: Generates Creation, Leverage, Plasticity vectors
- `calculate_shot_difficulty_features.py`: Generates Pressure vector features
- `collect_shot_quality_with_clock.py`: Collects clock data (parallelized)

**Model Training**:
- `train_predictive_model.py`: Trains XGBoost classifier (needs modification for Phase 2)

**Analysis**:
- `component_analysis.py`: Correlates stress vectors with playoff outcomes
- `calculate_simple_resilience.py`: Generates archetype labels

**Phase 0 & 1 (New)**:
- `validate_model_behavior.py`: Model behavior discovery and validation
- `quality_filters.py`: Quality filter infrastructure for filtering false positives

---

## What's Missing (The Problem)

### Current Limitation

The model predicts performance at the **current usage level**, not at different usage levels.

**What it does**:
- Takes stress vectors (skills) as input
- Predicts archetype (performance) as output
- Implicitly assumes usage is fixed at player's current level

**What it can't do**:
- Predict what performance would be at a different usage level
- Answer "If this player had 25% usage instead of 19.6%, would they be a King?"

### The Brunson Example

**Jalen Brunson (2020-21)**:
- Current Usage: 19.6%
- Stress Vectors: High creation ratio (0.692), positive leverage USG delta (0.029)
- Model Prediction: "Victim" (correct for 19.6% usage)
- Actual Performance: Low production (backup role)

**Jalen Brunson (2022-23)**:
- Current Usage: 26.6%
- Stress Vectors: Similar skills (creation ratio 0.862)
- Actual Performance: "King" (high production, high efficiency)
- Model Prediction: Would be "King" (correct for 26.6% usage)

**The Insight**: Skills are relatively stable. Performance depends on opportunity (usage). The model needs to learn: `archetype = f(stress_vectors, usage)`

---

## Implementation Progress

### ✅ Phase 0: Model Behavior Discovery (COMPLETE)

**What Was Done:**
- Created validation test suite testing model on 20-30 known cases
- Documented model behavior patterns
- Confirmed model predicts "King" correctly for known stars
- Identified that predictions don't change with usage (expected - USG_PCT not a feature yet)

**Key Findings:**
- Model DOES predict "King" (Jokić: 66%, LeBron: 74%, Giannis: 55%)
- Known Kings have high star-level potential (57-76%)
- Known breakouts show varying potential pre-breakout (0.6-16%)

**Artifacts:**
- `src/nba_data/scripts/validate_model_behavior.py`
- `results/model_behavior_validation.csv`
- `results/model_behavior_rules.md`

### ✅ Phase 1: Quality Filters Infrastructure (COMPLETE)

**What Was Done:**
- Created quality filter module with data completeness scoring
- Implemented base signal strength calculation
- Created quality filter validation on known cases

**Key Features:**
- Quality filter checks positive signals across key stress vectors
- Data completeness score (requires 4 of 6 key features)
- Base signal strength (weighted average of top stress vectors)

**Artifacts:**
- `src/nba_data/scripts/quality_filters.py`
- `results/quality_filter_validation.csv`

**Note**: Quality filters are designed to catch FALSE POSITIVES in rankings, not to validate known stars. Thresholds can be refined in Phase 4.

---

## What Needs to Be Built (Phase 2)

### Usage-Aware Conditional Prediction Model

**Goal**: Make the model predict performance at different usage levels.

**Approach**:
1. Add `USG_PCT` as explicit feature
2. Add interaction terms: `USG_PCT * CREATION_VOLUME_RATIO`, `USG_PCT * LEVERAGE_USG_DELTA`, etc.
3. Retrain model with usage-aware features
4. Create conditional prediction function: `predict_archetype_at_usage(stress_vectors, usage_level)`

**See**: `USAGE_AWARE_MODEL_PLAN.md` for complete implementation plan.

---

## Key Files & Their Purpose

### Core Documentation
- **`USAGE_AWARE_MODEL_PLAN.md`**: **START HERE** - Implementation plan for usage-aware model
- **`KEY_INSIGHTS.md`**: Hard-won lessons (quick reference)
- **`LUKA_SIMMONS_PARADOX.md`**: Theoretical foundation
- **`extended_resilience_framework.md`**: Stress vectors explained
- **`DATA_REQUIREMENTS.md`**: Data sources and requirements

### Model & Data
- **`models/resilience_xgb.pkl`**: Trained XGBoost model (current)
- **`results/predictive_dataset.csv`**: Stress vectors (features)
- **`results/resilience_archetypes.csv`**: Playoff archetypes (labels)
- **`results/predictive_model_report.md`**: Current model performance

### Scripts
- **`src/nba_data/scripts/train_predictive_model.py`**: Model training (needs modification)
- **`src/nba_data/scripts/evaluate_plasticity_potential.py`**: Feature generation
- **`src/nba_data/scripts/calculate_shot_difficulty_features.py`**: Pressure features

---

## Known Issues & Limitations

1. **No usage interaction**: Model can't predict at different usage levels
2. **Implicit usage assumption**: Model assumes usage is fixed
3. **Can't answer latent star question**: Can't predict "what if this player had more opportunity?"
4. **Accuracy plateau**: 59.4% may be near ceiling, or may improve with usage-aware features

---

## Next Steps (Phase 2)

1. **Read `USAGE_AWARE_MODEL_PLAN.md`**: Complete implementation plan (includes Phase 0 & 1 completion)
2. **Review `results/model_behavior_rules.md`**: Understand model behavior patterns discovered in Phase 0
3. **Review `src/nba_data/scripts/quality_filters.py`**: Understand quality filter infrastructure (for Phase 4)
4. **Modify `train_predictive_model.py`**: Add USG_PCT and interaction terms
5. **Retrain model**: Validate accuracy maintained/improved
6. **Test conditional predictions**: Use `validate_model_behavior.py` as template, test on known cases at different usage levels
7. **Create conditional prediction function**: `predict_archetype_at_usage(stress_vectors, usage_level)`

---

## Archived Content

Latent star detection work has been archived to `archive/latent_star_detection/`. This includes:
- Phase 0, 1, 2 implementation details
- Brunson test analysis
- Maxey analysis
- Consultant feedback on latent star detection

**Why archived**: Latent star detection revealed the model's limitation (can't predict at different usage levels). Focus shifted to fixing the foundation first.

---

**See Also**:
- `USAGE_AWARE_MODEL_PLAN.md` - Implementation plan
- `KEY_INSIGHTS.md` - Hard-won lessons
- `README.md` - Project overview


