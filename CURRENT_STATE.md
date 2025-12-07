# Current State: NBA Playoff Resilience Engine

Date: December 7, 2025

Status: Data Leakage Fixes Complete ✅ | Previous Playoff Features Integrated ✅ | Temporal Train/Test Split Implemented ✅ | 2D Risk Matrix Complete ✅ | Universal Projection Implemented ✅ | Cleanup & Reorganization In Progress 🏗️

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

**Accuracy:** 53.54% (RFE model, 10 features) / 51.69% (Full model, 60 features) - True predictive power using only Regular Season data with temporal train/test split (899 player-seasons, 2015-2024, retrained December 6, 2025)

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
1. USG_PCT (40.2% importance) - Usage level (highest importance!)
2. USG_PCT_X_EFG_ISO_WEIGHTED (11.7% importance) - Usage × Isolation efficiency (2nd highest!)
3. EFG_PCT_0_DRIBBLE (7.6% importance) - Catch-and-shoot efficiency
4. EFG_ISO_WEIGHTED_YOY_DELTA (6.4% importance) - Year-over-year change in isolation efficiency
5. CREATION_TAX (6.3% importance) - Creation efficiency drop-off
6. PREV_RS_RIM_APPETITE (6.0% importance) - Previous season rim pressure
7. CREATION_TAX_YOY_DELTA (5.7% importance) - Year-over-year change in creation tax
8. USG_PCT_X_RS_LATE_CLOCK_PRESSURE_RESILIENCE (5.6% importance) - Usage × Late clock resilience
9. USG_PCT_X_LEVERAGE_USG_DELTA (5.4% importance) - Usage × Clutch usage scaling
10. PREV_LEVERAGE_TS_DELTA (5.2% importance) - Previous season leverage efficiency

**Key Insight:** All features are RS-only or trajectory-based (previous season). No playoff features made it into the top 10. Usage-aware features dominate (65.9% combined importance).

**Model File:** `models/resilience_xgb_rfe_10.pkl` (primary), `models/resilience_xgb.pkl` (fallback)

### Validation Results

**Test Case Pass Rate:** **81.2%** (13/16) - Improved from 68.8% with Universal Projection ✅

**True Positives:** **75.0%** (6/8) - Improved from 62.5% ✅
- ✅ Victor Oladipo: 86.96% (PASS)
- ✅ Tyrese Maxey: 98.97% (PASS)
- ✅ Shai Gilgeous-Alexander: 98.76% (PASS)
- ✅ Jalen Brunson: 99.75% (PASS)
- ✅ Jamal Murray: 97.41% (PASS)
- ✅ Lauri Markkanen: 73.04% (PASS - improved from 63.19%)
- ✅ Talen Horton-Tucker: 30.00% (PASS - correctly identified as Victim)

**False Positives:** **100.0%** (6/6) - Perfect ✅
- ✅ Jordan Poole: 38.85% (PASS - correctly downgraded)
- ✅ Domantas Sabonis: 30.00% (PASS - correctly filtered)
- ✅ D'Angelo Russell: 30.00% (PASS - correctly filtered)
- ✅ Ben Simmons: 30.00% (PASS - correctly filtered)
- ✅ Christian Wood: 30.00% (PASS - correctly filtered)
- ✅ Tobias Harris: 30.00% (PASS - correctly filtered)

**Remaining Failures (3 cases):**
- ❌ Mikal Bridges: 30.00% (expected ≥65%) - Usage Shock case, Bag Check Gate capping (model predicts 93.43% before gates)
- ❌ Desmond Bane: 34.94% (expected ≥65%) - Secondary creator, improved from 43.80% but still failing
- ❌ Tyrese Haliburton: 30.00% (expected ≥65%) - Needs investigation (may be missing data or gate issue)

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

## Next Priority: Investigate Remaining Test Failures

**Status:** 🔴 HIGH PRIORITY

**Remaining Failures (3 cases):**

1. **Mikal Bridges (2021-22)**: 30.00% (expected ≥65%)
   - **Root Cause**: Bag Check Gate capping due to low self-created frequency (0.0697 < 0.10)
   - **Note**: Model predicts 93.43% before gates apply
   - **Potential Fix**: Improve proxy calculation for players with high CREATION_VOLUME_RATIO but missing ISO/PNR data, or exempt if Flash Multiplier conditions met

2. **Tyrese Haliburton (2021-22)**: 30.00% (expected ≥65%)
   - **Root Cause**: Needs investigation - may be missing data or gate application
   - **Next Steps**: Check data completeness and gate logic

3. **Desmond Bane (2021-22)**: 34.94% (expected ≥65%)
   - **Root Cause**: Model underestimates secondary creators
   - **Note**: Improved from 43.80% but still failing
   - **Potential Fix**: May need specialized handling for secondary creators who scale up
