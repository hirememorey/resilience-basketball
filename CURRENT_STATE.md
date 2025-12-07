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

**Test Case Pass Rate:** **81.2%** (13/16) - Stable after feature distribution fixes ✅

**True Positives:** **75.0%** (6/8) ✅
- ✅ Shai Gilgeous-Alexander (2018-19): 99.16% (PASS)
- ✅ Victor Oladipo (2016-17): 94.71% (PASS)
- ✅ Jalen Brunson (2020-21): 99.50% (PASS)
- ✅ Jamal Murray (2018-19): 82.31% (PASS)
- ✅ Desmond Bane (2021-22): 72.02% (PASS)
- ✅ Tyrese Maxey (2021-22): 84.12% (PASS)

**False Positives:** **83.3%** (5/6) ✅
- ✅ Talen Horton-Tucker: 30.00% (PASS)
- ✅ Christian Wood: 30.00% (PASS)
- ✅ D'Angelo Russell: 30.00% (PASS)
- ✅ Tobias Harris: 30.00% (PASS)
- ✅ Domantas Sabonis: 30.00% (PASS)
- ❌ Jordan Poole: 87.62% (FAIL - expected <55%, got 87.62%)

**System Player & Usage Shock:** **100.0%** (2/2) ✅
- ✅ Tyus Jones: 30.00% (PASS)
- ✅ Mikal Bridges: 92.85% (PASS)

**Remaining Failures (3 cases):**
- ❌ Jordan Poole (2021-22): 87.62% (expected <55%) - False positive case, needs investigation
- ❌ Lauri Markkanen (2021-22): 64.16% (expected ≥65%) - Close to threshold, may be acceptable
- ❌ Tyrese Haliburton (2021-22): 30.00% (expected ≥65%) - Needs investigation (may be gate issue)

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

**Remaining Failures (3 cases):**

1. **Jordan Poole (2021-22)**: 87.62% (expected <55%)
   - **Root Cause**: False positive case incorrectly predicting high star-level
   - **Note**: Previously passing at 38.85%, now failing after fixes
   - **Next Steps**: Investigate why model is overvaluing Poole after feature alignment

2. **Lauri Markkanen (2021-22)**: 64.16% (expected ≥65%)
   - **Root Cause**: Close to threshold, may be acceptable
   - **Note**: Improved from previous failures
   - **Next Steps**: Evaluate if this is a legitimate prediction or needs adjustment

3. **Tyrese Haliburton (2021-22)**: 30.00% (expected ≥65%)
   - **Root Cause**: Needs investigation - may be gate application or missing data
   - **Next Steps**: Check data completeness and gate logic for Haliburton case
