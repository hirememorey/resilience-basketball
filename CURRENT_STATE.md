# Current State: NBA Playoff Resilience Engine

Date: December 7, 2025

Status: Data Leakage Fixes Complete ✅ | Previous Playoff Features Integrated ✅ | Temporal Train/Test Split Implemented ✅ | 2D Risk Matrix Complete ✅ | Universal Projection Implemented ✅ | Feature Distribution Alignment Complete ✅ | USG_PCT Normalization Complete ✅

## 🏗️ Project Structure & Cleanup

We are currently consolidating the codebase. Obsolete frameworks (Linear Regression, Complex 5-Pathway) are being archived to focus on the Active XGBoost Pipeline.

### Active Pipeline Components

These are the core files driving the current 53.54% accuracy model:

**Data Ingestion:**
- `src/nba_data/scripts/collect_regular_season_stats.py`
- `src/nba_data/scripts/collect_playoff_logs.py`
- `src/nba_data/scripts/collect_shot_charts.py` (with predictive dataset support)
- `src/nba_data/scripts/collect_shot_quality_with_clock.py`

**Feature Engineering (Stress Vectors):**
- `src/nba_data/scripts/calculate_simple_resilience.py` (Target Generation)
- `src/nba_data/scripts/evaluate_plasticity_potential.py` (Creation, Leverage, Context)
- `src/nba_data/scripts/calculate_rim_pressure.py` (Physicality)
- `src/nba_data/scripts/calculate_shot_difficulty_features.py` (Pressure)
- `src/nba_data/scripts/calculate_dependence_score.py` (2D Risk Y-Axis)
- `src/nba_data/scripts/generate_trajectory_features.py` (Priors/Trajectory)
- `src/nba_data/scripts/generate_gate_features.py` (Soft Gates)
- `src/nba_data/scripts/generate_previous_playoff_features.py` (Past PO Performance)

**Modeling & Inference:**
- `src/nba_data/scripts/train_rfe_model.py` (Primary Trainer)
- `src/nba_data/scripts/predict_conditional_archetype.py` (Core Inference Engine)
- `src/nba_data/scripts/detect_latent_stars_v2.py` (Latent Star Detection)
- `run_expanded_predictions.py` (Batch Inference)

**Validation:**
- `test_latent_star_cases.py` (Critical Case Suite)
- `test_2d_risk_matrix.py` (Risk Matrix Suite)
- `analyze_model_misses.py` (Miss Analysis)

## Project Overview

**Goal:** Identify players who consistently perform better than expected in the playoffs and explain why using mechanistic insights.

**Current Model:** XGBoost Classifier that predicts playoff archetypes (King, Bulldozer, Sniper, Victim) from regular season stress vectors with usage-aware conditional predictions. RFE-optimized to 10 core features (reduced from 65).

**Accuracy:** 53.85% (RFE model, 10 features) - True predictive power using only Regular Season data with temporal train/test split (899 player-seasons, 2015-2024, retrained December 7, 2025)

## What Exists (Current State)

### Data Pipeline

**Complete Dataset:** 10 seasons (2015-2024), 5,312 player-season records

**Key Data Files:**
- `results/predictive_dataset.csv`: Stress vectors (5,312 player-seasons)
- `results/resilience_archetypes.csv`: Playoff archetypes (labels)
- `results/pressure_features.csv`: Pressure vector features
- `data/playoff_pie_data.csv`: Playoff advanced stats

**Data Coverage:**
- Stress vectors: 100% coverage
- Usage (USG_PCT): 100% coverage
- Age: 100% coverage
- Clock data: 100% coverage (all seasons)
- Rim pressure data: 95.9% coverage (1,773/1,849 in expanded predictions) - Fixed December 5, 2025 ✅

### Model Architecture

**Algorithm:** XGBoost Classifier (Multi-Class)

**RFE-Optimized Model (10 features) - CURRENT:**
1. USG_PCT (41.26% importance) - Usage level (highest importance!)
2. USG_PCT_X_EFG_ISO_WEIGHTED (8.85% importance) - Usage × Isolation efficiency
3. CREATION_TAX (8.54% importance) - Creation efficiency drop-off
4. USG_PCT_X_RS_LATE_CLOCK_PRESSURE_RESILIENCE (7.16% importance) - Usage × Late clock resilience
5. ABDICATION_RISK (6.71% importance) - Gate feature (negative leverage signal)
6. RS_LATE_CLOCK_PRESSURE_APPETITE (6.33% importance) - Late clock pressure willingness
7. CLUTCH_MIN_TOTAL (5.39% importance) - Clutch minutes
8. QOC_USG_DELTA (5.28% importance) - Quality of competition usage delta
9. CREATION_TAX_YOY_DELTA (5.26% importance) - Year-over-year change in creation tax
10. AGE_X_RS_PRESSURE_RESILIENCE_YOY_DELTA (5.21% importance) - Age × Pressure resilience trajectory

**Key Insight:** All features are RS-only or trajectory-based. Usage-aware features dominate (57.27% combined importance). Model retrained December 7, 2025 with feature distribution alignment fixes.

**Model File:** `models/resilience_xgb_rfe_10.pkl` (primary), `models/resilience_xgb.pkl` (fallback)

### Validation Results

**Test Case Pass Rate:** **81.2%** (26/32) - Updated December 7, 2025 with expanded test suite ✅

**Test Suite Expansion:** Expanded from 16 to 32 test cases, adding:
- Mikal Bridges (2021-22) - True Positive ✅
- Desmond Bane (2021-22) - True Positive ✅
- Karl-Anthony Towns (6 seasons: 2015-16 through 2020-21) - True Negative (all passed) ✅
- Markelle Fultz (7 seasons: 2017-18 through 2023-24) - True Negative (4 passed, 3 failed)

**True Positives:** **88.9%** (8/9) ✅
- ✅ Shai Gilgeous-Alexander (2018-19): 99.16% (PASS)
- ✅ Victor Oladipo (2016-17): 94.71% (PASS)
- ✅ Jalen Brunson (2020-21): 99.50% (PASS)
- ✅ Tyrese Maxey (2021-22): 84.12% (PASS)
- ✅ Pascal Siakam (2018-19): 94.47% (PASS)
- ✅ Jayson Tatum (2017-18): 84.97% (PASS)
- ✅ Mikal Bridges (2021-22): 99.55% (PASS)
- ✅ Desmond Bane (2021-22): 83.09% (PASS)
- ❌ Tyrese Haliburton (2021-22): 30.00% (FAIL - expected ≥65%, got 30.00%)

**False Positives:** **60.0%** (3/5) ⚠️
- ✅ Talen Horton-Tucker (2020-21): 30.00% (PASS)
- ✅ Christian Wood (2020-21): 30.00% (PASS)
- ✅ D'Angelo Russell (2018-19): 30.00% (PASS)
- ❌ Jordan Poole (2021-22): 87.62% (FAIL - expected <55%, got 87.62%)
- ❌ Julius Randle (2020-21): 61.33% (FAIL - expected <55%, got 61.33%)

**True Negatives:** **82.4%** (14/17) ✅
- ✅ Ben Simmons (3 seasons: 2017-18, 2018-19, 2020-21): All passed
- ✅ Domantas Sabonis (2021-22): 30.00% (PASS)
- ✅ Karl-Anthony Towns (6 seasons: 2015-16 through 2020-21): All passed
- ✅ Markelle Fultz (2017-18, 2018-19, 2020-21, 2021-22): All passed
- ❌ Markelle Fultz (2019-20): 73.04% (FAIL - expected <55%, got 73.04%)
- ❌ Markelle Fultz (2022-23): 74.87% (FAIL - expected <55%, got 74.87%)
- ❌ Markelle Fultz (2023-24): 66.08% (FAIL - expected <55%, got 66.08%)

**System Player:** **100.0%** (1/1) ✅
- ✅ Tyus Jones (2021-22): 30.00% (PASS)

**Remaining Failures (6 cases):**
- ❌ Jordan Poole (2021-22): 87.62% (expected <55%) - False positive case, needs investigation
- ❌ Julius Randle (2020-21): 61.33% (expected <55%) - False positive case, close to threshold
- ❌ Tyrese Haliburton (2021-22): 30.00% (expected ≥65%) - True positive case, needs investigation (may be gate issue)
- ❌ Markelle Fultz (2019-20, 2022-23, 2023-24): 3 seasons failing - True negative cases, model overvaluing Fultz in certain seasons

## 2D Risk Matrix Implementation (December 2025) ✅ COMPLETE

**The Discovery:** The model correctly predicts Performance (outcomes), but we're trying to predict two different things in one dimension.

**The Ground Truth Trap:** Training labels are based on outcomes (Poole = "King" because he succeeded), but we want to predict portability (Poole = "System Merchant" because his production isn't portable).

**The Solution:** 2D Risk Matrix separating Performance (what happened) from Dependence (is it portable?).

**Validation Results:**
- ✅ Luka Dončić: Franchise Cornerstone (96.87% Performance, 26.59% Dependence)
- ✅ Jordan Poole: Luxury Component (58.62% Performance, 51.42% Dependence)

## ✅ Completed: Universal Projection Implementation (December 2025)

**Status:** ✅ **COMPLETE** - December 7, 2025

**The Problem:** "Static Avatar" Fallacy - When predicting at different usage levels, only `USG_PCT` was updated while `CREATION_VOLUME_RATIO` stayed at role-player level, creating impossible profiles (high usage + low creation = "off-ball chucker").

**The Solution:** Universal Projection with Empirical Distributions:
1. **Always project** when usage differs (not just upward)
2. **Use empirical bucket medians** for upward projections (respects non-linear relationships)
3. **Project multiple features together** (CREATION_VOLUME_RATIO, LEVERAGE_USG_DELTA, RS_PRESSURE_APPETITE)

**Results:**
- ✅ **Test Suite Pass Rate**: 68.8% → **81.2%** (+12.4 percentage points)
- ✅ **False Positive Detection**: 83.3% → **100.0%** (6/6) - Perfect
- ✅ **True Positive Detection**: 62.5% → **75.0%** (6/8)
- ✅ **Brunson (2020-21) at 30% usage**: 99.75% star-level ✅
- ✅ **Maxey (2021-22) at 30% usage**: 98.97% star-level ✅

**Key Insight:** Features must scale together, not independently. Empirical distributions capture non-linear relationships (20-25% bucket: 0.4178 → 25-30% bucket: 0.6145 = +47% jump).

**See**: `UNIVERSAL_PROJECTION_IMPLEMENTATION.md` and `results/universal_projection_validation.md` for complete details.

## ✅ Completed: Feature Distribution Alignment & USG_PCT Normalization (December 7, 2025)

**Status:** ✅ **COMPLETE**

**The Problem**: Two critical bugs were identified:
1. **Feature Distribution Mismatch**: Model was trained on raw features, but prediction pipeline applied transformations (Flash Multiplier, Playoff Volume Tax) before creating interaction terms, causing structural differences.
2. **USG_PCT Format Mismatch**: USG_PCT was stored as percentage (26.0) but model expected decimal (0.26), causing incorrect projections and interaction terms.

**The Fix**:
1. **Feature Transformations During Training**: Applied Flash Multiplier and Playoff Volume Tax transformations to base features *before* creating interaction terms in both `train_rfe_model.py` and `rfe_feature_selection.py`.
2. **USG_PCT Normalization**: Normalized USG_PCT from percentage to decimal format in:
   - `predict_conditional_archetype.py` (get_player_data, prepare_features, _load_features)
   - `train_rfe_model.py` (during feature preparation)
   - `rfe_feature_selection.py` (during feature preparation)

**Results**:
- ✅ **Test Suite Pass Rate**: 43.8% → **81.2%** (+37.4 percentage points)
- ✅ **True Positive Detection**: 0/8 → **6/8** (75.0%)
- ✅ **Model Accuracy**: Stable at 53.85% (RFE model, 10 features)
- ✅ **Feature Consistency**: Training and prediction now use identical feature distributions

**Key Insight**: Order of operations matters critically. Transformations must be applied to base features before interaction terms are calculated, and all features must use consistent units (decimal vs percentage).

## Next Priority: Investigate Remaining Test Failures

**Status:** 🔴 HIGH PRIORITY

**Remaining Failures (6 cases):**

1. **Jordan Poole (2021-22)**: 87.62% (expected <55%)
   - **Root Cause**: False positive case incorrectly predicting high star-level
   - **Category**: False Positive
   - **Next Steps**: Investigate why model is overvaluing Poole - may need additional gate features

2. **Julius Randle (2020-21)**: 61.33% (expected <55%)
   - **Root Cause**: False positive case - All-NBA regular season but playoff collapse
   - **Category**: False Positive
   - **Note**: Close to threshold (61.33% vs 55%), may indicate model correctly identifying borderline case
   - **Next Steps**: Evaluate if this is acceptable or needs refinement

3. **Tyrese Haliburton (2021-22)**: 30.00% (expected ≥65%)
   - **Root Cause**: True positive case incorrectly predicting low star-level
   - **Category**: True Positive
   - **Next Steps**: Check data completeness and gate logic - may be gate capping at 30%

4. **Markelle Fultz (2019-20)**: 73.04% (expected <55%)
   - **Root Cause**: True negative case - model overvaluing Fultz
   - **Category**: True Negative
   - **Next Steps**: Investigate why model predicts high star-level for Fultz in this season

5. **Markelle Fultz (2022-23)**: 74.87% (expected <55%)
   - **Root Cause**: True negative case - model overvaluing Fultz
   - **Category**: True Negative
   - **Next Steps**: Same as above - pattern suggests model may be responding to certain features incorrectly

6. **Markelle Fultz (2023-24)**: 66.08% (expected <55%)
   - **Root Cause**: True negative case - model overvaluing Fultz
   - **Category**: True Negative
   - **Note**: Pattern of 3 Fultz seasons failing suggests systematic issue
   - **Next Steps**: Investigate what features are driving high predictions for Fultz in these specific seasons
