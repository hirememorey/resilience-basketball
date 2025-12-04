# Current State: NBA Playoff Resilience Engine

**Date**: December 2025  
**Status**: Phase 2 Complete - Usage-Aware Model Implemented ✅

---

## Project Overview

**Goal**: Identify players who consistently perform better than expected in the playoffs and explain *why* using mechanistic insights.

**Current Model**: XGBoost Classifier that predicts playoff archetypes (King, Bulldozer, Sniper, Victim) from regular season stress vectors with **usage-aware conditional predictions**.

**Accuracy**: 62.22% (899 player-seasons, 2015-2024) - Improved from 59.4% with usage-aware features

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

**Features (38 total - includes 6 usage-aware features)**:
- **Creation Vector**: CREATION_TAX, CREATION_VOLUME_RATIO
- **Leverage Vector**: LEVERAGE_TS_DELTA, LEVERAGE_USG_DELTA, CLUTCH_MIN_TOTAL
- **Pressure Vector**: RS_PRESSURE_APPETITE, RS_PRESSURE_RESILIENCE, clock features (late/early)
- **Physicality Vector**: RS_FTr, FTr_RESILIENCE, RIM_PRESSURE_RESILIENCE
- **Plasticity Vector**: SHOT_DISTANCE_DELTA, SPATIAL_VARIANCE_DELTA
- **Context Vector**: QOC_TS_DELTA, opponent defensive context
- **Usage-Aware Features (Phase 2)**: USG_PCT + 5 interaction terms (USG_PCT × top stress vectors)

**Model File**: `models/resilience_xgb.pkl`

**Training Script**: `src/nba_data/scripts/train_predictive_model.py`

### Key Scripts

**Feature Generation**:
- `evaluate_plasticity_potential.py`: Generates Creation, Leverage, Plasticity vectors
- `calculate_shot_difficulty_features.py`: Generates Pressure vector features
- `collect_shot_quality_with_clock.py`: Collects clock data (parallelized)

**Model Training**:
- `train_predictive_model.py`: Trains XGBoost classifier with usage-aware features ✅

**Analysis**:
- `component_analysis.py`: Correlates stress vectors with playoff outcomes
- `calculate_simple_resilience.py`: Generates archetype labels

**Phase 0 & 1 (Complete)**:
- `validate_model_behavior.py`: Model behavior discovery and validation
- `quality_filters.py`: Quality filter infrastructure for filtering false positives

**Phase 2 (Complete)**:
- `predict_conditional_archetype.py`: Conditional prediction function (predict at any usage level)
- `test_conditional_predictions.py`: Validation test suite for conditional predictions
- `detect_latent_stars_v2.py`: Latent star detection (Use Case B - age < 26, usage < 25%)

---

## ✅ Phase 2 Complete: Usage-Aware Model

### What Was Built

The model now predicts performance at **different usage levels**, not just current usage.

**What it can do**:
- ✅ Predict archetype at any usage level: `predict_archetype_at_usage(stress_vectors, usage_level)`
- ✅ Answer "If this player had 25% usage instead of 19.6%, would they be a King?"
- ✅ Identify latent stars (players with high skills but low opportunity)

### The Brunson Example (Validated)

**Jalen Brunson (2020-21)**:
- Current Usage: 19.6%
- Stress Vectors: High creation ratio (0.692), positive leverage USG delta (0.029)
- Model Prediction at 19.6%: "Victim" (0.77% star-level) ✅ Correct
- Model Prediction at 25%: "Victim" (18.19% star-level)
- Model Prediction at 28%: "Victim" (51.61% star-level)
- Model Prediction at 32%: "Bulldozer" (94.02% star-level) ✅ Correct

**The Insight**: Skills are relatively stable. Performance depends on opportunity (usage). The model now learns: `archetype = f(stress_vectors, usage)` ✅

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

## ✅ Phase 2 Implementation (Complete)

### Usage-Aware Conditional Prediction Model

**Status**: ✅ **COMPLETE**

**What Was Done**:
1. ✅ Added `USG_PCT` as explicit feature (#1 feature: 15.0% importance)
2. ✅ Added 5 interaction terms with top stress vectors
3. ✅ Retrained model with usage-aware features (accuracy: 59.4% → 62.22%)
4. ✅ Created conditional prediction function: `predict_archetype_at_usage()`
5. ✅ Implemented Use Case B: Latent Star Detection (age < 26, usage < 25%)

**Key Results**:
- Model accuracy improved: **62.22%** (from 59.4%)
- Predictions change with usage level (validated on test cases)
- Brunson test passes: Victim at low usage → high star-level at high usage
- Latent star detection works: Identifies young players with high star potential

**See**: `results/phase2_implementation_summary.md` for complete details.

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

1. ✅ **Usage interaction**: Resolved - Model can now predict at different usage levels
2. ✅ **Usage assumption**: Resolved - Usage is now an explicit feature
3. ✅ **Latent star question**: Resolved - Can predict "what if this player had more opportunity?"
4. ✅ **Accuracy improvement**: Model accuracy improved to 62.22% with usage-aware features

**Remaining Considerations**:
- Latent star detection threshold tuning (currently 15% star potential at 25% usage)
- Some known breakouts (Haliburton, Maxey) show lower star potential pre-breakout (may be due to missing data)

---

## Next Steps (Phase 3)

1. **Refine latent star detection**: Test different thresholds and usage levels to optimize identification
2. **Expand validation**: Test conditional predictions on more seasons and known breakouts
3. **Use Case A implementation**: Create production-ready script for current performance prediction
4. **Threshold optimization**: Analyze optimal star-level potential thresholds for different use cases
5. **Documentation**: Prepare findings for Sloan paper submission

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


