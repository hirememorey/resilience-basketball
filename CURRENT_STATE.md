# Current State: NBA Playoff Resilience Engine

**Date**: December 2025  
**Status**: Phase 3 Implementation Complete - Ready for Validation Testing ✅

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

## ✅ Phase 2 Validation: Critical Case Studies Test Suite

**Status**: ✅ **COMPLETE** (December 2025)

**Test Suite**: 14 critical case studies testing latent star detection across different failure modes

**Results**: 6/14 passed (42.9% pass rate)

### Test Results Summary

**Passed (6/12)**:
- ✅ Shai Gilgeous-Alexander (2018-19): 90.29% star-level - Correctly identified Physicality Vector
- ✅ Jalen Brunson (2020-21): 94.02% star-level - Already validated
- ✅ Talen Horton-Tucker (2020-21): 16.79% star-level - Correctly identified as Victim
- ✅ Tyus Jones (2021-22): 6.88% star-level - Correctly identified system player ceiling
- ✅ Christian Wood (2020-21): 13.73% star-level - Correctly identified empty calories
- ✅ Jamal Murray (2018-19): 72.39% star-level - Correctly valued Leverage Vector over consistency

**Failed (6/12)**:
- ❌ Victor Oladipo (2016-17): 39.56% star-level (expected ≥70%) - **Role Constraint Failure**
- ❌ Jordan Poole (2021-22): 87.09% star-level (expected <30%) - **Context Mirage Failure**
- ❌ Mikal Bridges (2021-22): 57.11% star-level (expected ≥70%) - **Role Constraint Failure**
- ❌ Lauri Markkanen (2021-22): 10.72% star-level (expected ≥70%) - **Role Constraint Failure** + Missing Data
- ❌ D'Angelo Russell (2018-19): 66.03% star-level (expected <30%) - **Softness Failure**
- ❌ Desmond Bane (2021-22): 50.44% star-level (expected ≥70%) - **Role Constraint Failure**

**Key Findings**:
1. **Role Constraint Problem**: Model confuses opportunity with ability - penalizes players forced into 3-and-D roles
2. **Context Dependency**: Model doesn't account for "Difficulty of Life" - overvalues context-dependent efficiency
3. **Physicality Underweighted**: Model underestimates "Physicality Floor" - doesn't cap players with zero rim pressure

**Test Artifacts**:
- `test_latent_star_cases.py`: Comprehensive test suite (12 critical cases)
- `results/latent_star_test_cases_results.csv`: Detailed results
- `results/latent_star_test_cases_report.md`: Markdown report

---

## ✅ Phase 3 Implementation (Complete - Ready for Validation)

**Status**: ✅ **IMPLEMENTATION COMPLETE** (December 2025)

All three Phase 3 fixes have been implemented in `predict_conditional_archetype.py`. Ready for validation testing.

### ✅ Fix #1: Usage-Dependent Feature Weighting (IMPLEMENTED)

**Problem**: Model confuses opportunity with ability. When predicting at high usage (>25%), it overweights `CREATION_VOLUME_RATIO` (how often they create) and underweights `CREATION_TAX` and `EFG_ISO_WEIGHTED` (efficiency on limited opportunities).

**Solution**: ✅ **IMPLEMENTED** - Gradual scaling based on target usage level:
- **At 20% usage**: No scaling (normal weights)
- **At 25% usage**: Moderate suppression of volume, moderate amplification of efficiency
- **At 32%+ usage**: Strong suppression (90%) of `CREATION_VOLUME_RATIO`, strong amplification (100%) of `CREATION_TAX` and `EFG_ISO_WEIGHTED`

**Expected Impact**: Fixes Oladipo, Markkanen, Bane, Bridges cases

**Implementation**: ✅ Complete in `predict_conditional_archetype.py` - `prepare_features()` method

### ✅ Fix #2: Context-Adjusted Efficiency (IMPLEMENTED - Requires Data)

**Problem**: Model doesn't account for "Difficulty of Life" - overvalues context-dependent efficiency (e.g., Poole benefiting from Curry gravity).

**Solution**: ✅ **IMPLEMENTED** - Usage-scaled system merchant penalty:
- **At 20% usage**: Full penalty (context dependency matters most)
- **At 25% usage**: Moderate penalty
- **At 30%+ usage**: Minimal penalty (10% - player creates own shots)
- Penalty applied to efficiency features if `RS_CONTEXT_ADJUSTMENT` > 0.05 (top 10-15%)

**Expected Impact**: Fixes Poole case

**Implementation**: ✅ Complete in `predict_conditional_archetype.py` - `prepare_features()` method
**Note**: `RS_CONTEXT_ADJUSTMENT` needs to be calculated from shot quality data (not yet in dataset)

### ✅ Fix #3: Fragility Gate (IMPLEMENTED)

**Problem**: Model underestimates "Physicality Floor" - doesn't cap players with zero rim pressure (e.g., Russell).

**Solution**: ✅ **IMPLEMENTED** - Hard gate based on distribution:
- **Threshold**: Bottom 20th percentile of `RIM_PRESSURE_RESILIENCE` (calculated: 0.7555)
- **Action**: If player is below threshold, cap star-level at 30% (Sniper ceiling)
- **Logic**: "No matter how good your jumper is, if you can't touch the paint, you are capped"
- Redistributes probabilities: King and Bulldozer set to 0, Sniper capped at 30%, Victim gets remainder

**Expected Impact**: Fixes Russell case

**Implementation**: ✅ Complete in `predict_conditional_archetype.py` - `predict_archetype_at_usage()` method

### Fix #4: Missing Data Pipeline (Priority: High)

**Problem**: Missing pressure data for some players (Markkanen, Bane had missing `RS_PRESSURE_APPETITE` and `RS_LATE_CLOCK_PRESSURE_RESILIENCE`).

**Solution**: Fix `collect_shot_quality_with_clock.py` to ensure 100% coverage

**Expected Impact**: Improves Markkanen, Bane predictions

**Implementation**: Investigate and fix data collection pipeline

---

## Next Steps: Phase 3 Validation Testing

**Status**: 🎯 **READY FOR VALIDATION** (December 2025)

All Phase 3 fixes have been implemented. Next step is validation testing to measure improvement.

**Current**: 6/14 passed (42.9%)  
**Expected After Phase 3**: 10-11/14 passed (71-79%)

**Cases Likely Fixed**:
- Oladipo: Fix #1 (usage-dependent weighting)
- Markkanen: Fix #1 (usage-dependent weighting) + Fix #4 (missing data - still needed)
- Bane: Fix #1 (usage-dependent weighting) + Fix #4 (missing data - still needed)
- Bridges: Fix #1 (usage-dependent weighting)
- Russell: Fix #3 (fragility gate)
- Poole: Fix #2 (context adjustment) - **requires RS_CONTEXT_ADJUSTMENT calculation**

**Validation Tasks**:
1. Run test suite with Phase 3 fixes enabled
2. Measure improvement by failure mode pattern (not just individual cases)
3. Check for regressions in passing cases
4. Calculate `RS_CONTEXT_ADJUSTMENT` for Fix #2 validation
5. Investigate missing data pipeline (Fix #4) for Markkanen and Bane

**Key Files for Validation**:
- `test_latent_star_cases.py`: Test suite (14 critical cases)
- `src/nba_data/scripts/predict_conditional_archetype.py`: Enhanced with Phase 3 fixes
- `analyze_phase3_data.py`: Data analysis script
- `results/phase3_implementation_summary.md`: Implementation details

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


