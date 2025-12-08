# Current State: NBA Playoff Resilience Engine

Date: December 8, 2025

Status: Data Leakage Fixes Complete ✅ | Previous Playoff Features Integrated ✅ | Temporal Train/Test Split Implemented ✅ | 2D Risk Matrix Complete ✅ | Universal Projection Implemented ✅ | Feature Distribution Alignment Complete ✅ | USG_PCT Normalization Complete ✅ | Inefficiency Gate Implemented ✅ | Playtype Data Merge Complete ✅ | USG_PCT/AGE Population Bug Fixed ✅ | Model Retrained ✅

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
- `src/nba_data/scripts/evaluate_plasticity_potential.py` (Creation, Leverage, Context, **Playtype**) - Updated Dec 8, 2025 ✅
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
- `test_latent_star_cases.py` (Critical Case Suite - **Now uses 2D Risk Matrix for all cases**)
- `test_2d_risk_matrix.py` (Risk Matrix Suite)
- `analyze_model_misses.py` (Miss Analysis)

## Project Overview

**Goal:** Identify players who consistently perform better than expected in the playoffs and explain why using mechanistic insights.

**Current Model:** XGBoost Classifier that predicts playoff archetypes (King, Bulldozer, Sniper, Victim) from regular season stress vectors with usage-aware conditional predictions. RFE-optimized to 10 core features (reduced from 65).

**Accuracy:** 53.85% (RFE model, 10 features) - True predictive power using only Regular Season data with temporal train/test split (899 player-seasons, 2015-2024, retrained December 8, 2025 with fixed USG_PCT/AGE data)

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
- Usage (USG_PCT): **100% coverage** - Fixed December 8, 2025 ✅ (was incorrectly fetched from base_stats, now from advanced_stats)
- Age: **100% coverage** - Fixed December 8, 2025 ✅ (fetched from advanced_stats endpoint)
- Playtype data (ISO_FREQUENCY, PNR_HANDLER_FREQUENCY): **79.3% coverage** (4,210/5,312) - Fixed December 8, 2025 ✅
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

**Key Insight:** All features are RS-only or trajectory-based. Usage-aware features dominate (57.27% combined importance). Model retrained December 8, 2025 with fixed USG_PCT/AGE data and feature distribution alignment fixes.

**Gates & Constraints:**
- **Fragility Gate**: Caps players with low rim pressure (RS_RIM_APPETITE < bottom 20th percentile) at 30% star-level
- **Bag Check Gate**: Caps players lacking self-created volume (SELF_CREATED_FREQ < 10%) at 30% star-level
- **Inefficiency Gate**: Caps players with uniformly low/mediocre isolation efficiency at 40% star-level (fixes "Low-Floor Illusion")
  - Condition 1: EFG_ISO_WEIGHTED < 25th percentile (uniformly bad)
  - Condition 2: EFG_ISO_WEIGHTED < median AND CREATION_TAX near 0.00 (uniformly mediocre)
- **Leverage Data Penalty**: Caps players missing critical leverage data at 30% star-level
- **Negative Signal Gate**: Caps players with negative leverage signals (abdication) at 30% star-level
- **Data Completeness Gate**: Caps players with <67% critical features at 30% star-level
- **Sample Size Gate**: Caps players with insufficient sample sizes at 30% star-level

**Model File:** `models/resilience_xgb_rfe_10.pkl` (primary), `models/resilience_xgb.pkl` (fallback)

### Validation Results

**Test Case Pass Rate:** **65.6%** (21/32) - Updated December 8, 2025 after model retraining with fixed USG_PCT/AGE data ✅

**Test Suite Enhancement (December 7, 2025):**
- Test suite now uses `predict_with_risk_matrix()` for all test cases
- Provides both Performance Score (1D) and Risk Category (2D) for richer evaluation
- Key insight: Using existing 2D framework is simpler than forcing 2D insights into 1D model
- Jordan Poole correctly identified as "Luxury Component" (High Performance + High Dependence) ✅

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
- ❌ Tyrese Haliburton (2021-22): 30.00% (FAIL - expected ≥65%, got 30.00% - gates capping)

**False Positives:** **60.0%** (3/5) ⚠️
- ✅ Talen Horton-Tucker (2020-21): 30.00% (PASS)
- ✅ D'Angelo Russell (2018-19): 30.00% (PASS)
- ❌ Jordan Poole (2021-22): 87.62% (FAIL - expected <55%, got 87.62% - risk category correct: "Luxury Component")
- ❌ Christian Wood (2020-21): 81.69% (FAIL - expected <55%, got 81.69%)
- ❌ Julius Randle (2020-21): 61.33% (FAIL - expected <55%, got 61.33%)

**True Negatives:** **52.9%** (9/17) ⚠️
- ✅ Ben Simmons (3 seasons: 2017-18, 2018-19, 2020-21): All passed
- ✅ Domantas Sabonis (2021-22): 30.00% (PASS - risk category mismatch: expected "Luxury Component", got "Moderate Performance, High Dependence" due to gate capping)
- ✅ Karl-Anthony Towns (2015-16, 2017-18): 2 seasons passed
- ✅ Markelle Fultz (2017-18, 2018-19, 2020-21, 2021-22): 4 seasons passed
  - **2017-18**: Inefficiency Gate applied (EFG_ISO=0.3596 < floor=0.4042) → capped at 40% ✅
  - **2018-19**: Inefficiency Gate applied (below median + near-zero CREATION_TAX) → capped at 40% ✅
- ❌ Karl-Anthony Towns (2016-17, 2018-19, 2019-20, 2020-21): 4 seasons failing (model overvaluing)
- ❌ Markelle Fultz (2019-20, 2022-23, 2023-24): 3 seasons failing (model overvaluing)

**System Player:** **100.0%** (1/1) ✅
- ✅ Tyus Jones (2021-22): 30.00% (PASS)

**Remaining Failures (11 cases):**
- ❌ Jordan Poole (2021-22): 87.62% (expected <55%) - False positive, but risk category correct ("Luxury Component")
- ❌ Christian Wood (2020-21): 81.69% (expected <55%) - False positive case
- ❌ Julius Randle (2020-21): 61.33% (expected <55%) - False positive case, close to threshold
- ❌ Tyrese Haliburton (2021-22): 30.00% (expected ≥65%) - True positive case, gates capping (needs gate logic fix)
- ❌ Domantas Sabonis (2021-22): Risk category mismatch - expected "Luxury Component", got "Moderate Performance, High Dependence" (gates capping performance)
- ❌ Karl-Anthony Towns (2016-17, 2018-19, 2019-20, 2020-21): 4 seasons failing - True negative cases (model overvaluing)
- ❌ Markelle Fultz (2019-20, 2022-23, 2023-24): 3 seasons failing - True negative cases (model overvaluing)
  - **Note**: Inefficiency Gate fixes "Low-Floor Illusion" for uniformly inefficient players (2017-18, 2018-19 now pass)
  - **Remaining Issue**: In later seasons, Fultz's isolation efficiency improved (above median), so gate doesn't apply. Model still overvalues due to other factors (high creation volume, rim pressure).

**Key Insight (December 8, 2025)**: Risk categories are correctly assigned based on Performance and Dependence scores. Failures are due to:
1. Gate capping preventing correct risk categorization (Sabonis, Haliburton)
2. Model false positives (KAT, Fultz later seasons, Wood, Randle, Poole)

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

## ✅ Completed: Inefficiency Gate Implementation (December 7, 2025)

**Status**: ✅ **COMPLETE**

**The Problem**: "Low-Floor Illusion" - Model falsely identified players like Markelle Fultz as "King" (Resilient Star) despite uniformly low efficiency. When a player is equally bad at catch-and-shoot (45% eFG) and self-creation (45% eFG), `CREATION_TAX = 0.00` looks like "resilience" (no drop) but is actually uniform mediocrity.

**The Solution**: Absolute Efficiency Floor Gate with two conditions:
1. **Condition 1**: `EFG_ISO_WEIGHTED < 25th percentile` (uniformly bad)
2. **Condition 2**: `EFG_ISO_WEIGHTED < median AND CREATION_TAX near 0.00` (uniformly mediocre)

**Implementation**:
- Calculates 25th percentile and median of `EFG_ISO_WEIGHTED` from qualified players (data-driven threshold)
- Caps star-level at 40% (allows for "Bulldozer" - inefficient volume scorer)
- Forces downgrade from "King" to "Bulldozer" or "Victim"
- Applies BEFORE other gates (hard physics constraint)

**Results**:
- ✅ **Markelle Fultz (2017-18)**: Now passes (Inefficiency Gate applied - EFG_ISO=0.3596 < floor=0.4042) → capped at 40%
- ✅ **Markelle Fultz (2018-19)**: Now passes (Inefficiency Gate applied - below median + near-zero CREATION_TAX) → capped at 40%
- ⚠️ **Markelle Fultz (2019-20, 2022-23, 2023-24)**: Still failing - Gate doesn't apply (EFG_ISO above median in these seasons)
  - **Note**: In later seasons, Fultz's isolation efficiency improved (0.48-0.52), so gate correctly doesn't apply. Model still overvalues due to other factors (high creation volume, rim pressure).

**Key Principle**: **Absolute metrics for floors, relative metrics for change**. CREATION_TAX measures change (resilience), but EFG_ISO_WEIGHTED measures absolute quality (star-level requirement). Uniformly inefficient ≠ resilient.

**See**: `KEY_INSIGHTS.md` (Insight #44: The "Low-Floor Illusion") for complete details.

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
   - **Note**: Inefficiency Gate does not apply (EFG_ISO_WEIGHTED=0.4826 above median=0.4594). Isolation efficiency improved in later seasons, but model still overvalues.
   - **Next Steps**: Investigate other factors driving high predictions (high creation volume, rim pressure, etc.)

5. **Markelle Fultz (2022-23)**: 74.87% (expected <55%)
   - **Root Cause**: True negative case - model overvaluing Fultz
   - **Category**: True Negative
   - **Note**: Inefficiency Gate does not apply (EFG_ISO_WEIGHTED=0.5186 above median). Similar to 2019-20.
   - **Next Steps**: Same as above - investigate other factors

6. **Markelle Fultz (2023-24)**: 66.08% (expected <55%)
   - **Root Cause**: True negative case - model overvaluing Fultz
   - **Category**: True Negative
   - **Note**: Inefficiency Gate does not apply (EFG_ISO_WEIGHTED=0.4634 above median). Pattern suggests model responding to high creation volume/rim pressure despite lack of star-level efficiency.
   - **Next Steps**: Investigate what features are driving high predictions for Fultz in these specific seasons
