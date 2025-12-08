# Current State: NBA Playoff Resilience Engine

Date: December 8, 2025

Status: Data Leakage Fixes Complete ✅ | Previous Playoff Features Integrated ✅ | Temporal Train/Test Split Implemented ✅ | 2D Risk Matrix Complete ✅ | Universal Projection Implemented ✅ | Feature Distribution Alignment Complete ✅ | USG_PCT Normalization Complete ✅ | Inefficiency Gate Implemented ✅ | Playtype Data Merge Complete ✅ | USG_PCT/AGE Population Bug Fixed ✅ | Phase 4.2: Continuous Gradients & Sample Weighting Complete ✅ | Phase 1: Dependence Score Upstream ✅ | Phase 2: Portable Features ✅ | Phase 4: 5x Sample Weighting ✅ | Model Retrained ✅

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

**Current Model:** XGBoost Classifier that predicts playoff archetypes (King, Bulldozer, Sniper, Victim) from regular season stress vectors with usage-aware conditional predictions. RFE-optimized to 10 core features with continuous gradient risk features and sample weighting for asymmetric loss.

**Accuracy:** 46.77% (RFE model, 10 features with 5x sample weighting) - True predictive power using only Regular Season data with temporal train/test split (899 player-seasons, 2015-2024, retrained December 8, 2025 with portable features and 5x penalty for high-usage victims)

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
5. ABDICATION_RISK (6.71% importance) - Continuous gradient (negative leverage signal)
6. RS_LATE_CLOCK_PRESSURE_APPETITE (6.33% importance) - Late clock pressure willingness
7. CLUTCH_MIN_TOTAL (5.39% importance) - Clutch minutes
8. QOC_USG_DELTA (5.28% importance) - Quality of competition usage delta
9. CREATION_TAX_YOY_DELTA (5.26% importance) - Year-over-year change in creation tax
10. AGE_X_RS_PRESSURE_RESILIENCE_YOY_DELTA (5.21% importance) - Age × Pressure resilience trajectory

**New Risk Features (Phase 4.2):**
- `RIM_PRESSURE_DEFICIT`: Continuous gradient (0-1) measuring rim pressure shortfall
- `ABDICATION_MAGNITUDE`: Continuous gradient (0-1) with Smart Deference logic
- `INEFFICIENT_VOLUME_SCORE`: Volume × Flaw interaction (creation_vol × negative_tax)
- `SYSTEM_DEPENDENCE_SCORE`: Volume × Dependence interaction (usg × system_dependence)
- `EMPTY_CALORIES_RISK`: Volume × Rim Pressure Deficit interaction

**Key Insight:** All features are RS-only or trajectory-based. Usage-aware features dominate (USG_PCT: 30.5% importance). Model retrained December 8, 2025 with portable features, continuous gradients, interaction terms, and 5x sample weighting for high-usage victims.

**Gates & Constraints (Phase 4.2 - Trust Fall 2.0):**
- **Hard Gates**: **DISABLED BY DEFAULT** - Model now learns from continuous gradient features
- **Continuous Gradients**: Binary gates converted to continuous features (0-1 scale)
  - `RIM_PRESSURE_DEFICIT`: Measures rim pressure shortfall (replaces Fragility Gate)
  - `ABDICATION_MAGNITUDE`: Measures abdication with Smart Deference exemption (replaces Negative Signal Gate)
  - `INEFFICIENT_VOLUME_SCORE`: Volume × Flaw interaction (replaces Inefficiency Gate logic)
- **Interaction Terms**: Explicit Volume × Flaw features teach model complex relationships
  - `SYSTEM_DEPENDENCE_SCORE`: `USG_PCT × (assisted_pct + open_shot_freq)`
  - `EMPTY_CALORIES_RISK`: `USG_PCT × RIM_PRESSURE_DEFICIT`
- **Sample Weighting**: Asymmetric loss - 5x weight for high-usage victims (penalizes false positives) - **Increased from 3x on December 8, 2025**
- **Trust Fall 2.0**: Gates disabled by default (`apply_hard_gates=False`) - model must learn patterns

**Model File:** `models/resilience_xgb_rfe_10.pkl` (primary), `models/resilience_xgb.pkl` (fallback)

### Validation Results

**Test Case Pass Rate (With Gates):** **75.0%** (24/32) - Updated December 8, 2025 after 5x sample weighting implementation ✅
- **True Positives**: 77.8% (7/9) ✅ - Model correctly identifies latent stars
- **False Positives**: 80.0% (4/5) ✅ - **Significant improvement** from 40.0% (+40.0 pp)
- **True Negatives**: 70.6% (12/17) ✅ - **Significant improvement** from 41.2% (+29.4 pp)

**Test Case Pass Rate (Trust Fall 2.0 - Gates Disabled):** **56.2%** (18/32) - December 8, 2025 ✅
- **True Positives**: 88.9% (8/9) ✅ - Model correctly identifies latent stars
- **False Positives**: 40.0% (2/5) ⚠️ - Model over-predicts stars (KAT, Russell, Randle, Fultz)
- **True Negatives**: 41.2% (7/17) ⚠️ - Model struggles to penalize high-usage players with flaws

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

## ✅ Completed: Phase 4.2 - Continuous Gradients & Sample Weighting (December 8, 2025)

**Status**: ✅ **COMPLETE**

**The Problem**: Hard gates (binary if/else statements) were brittle post-hoc patches. Model couldn't learn nuanced patterns from binary signals.

**The Solution**: Convert hard gates to continuous gradients and add explicit Volume × Flaw interaction terms:
1. **Continuous Gradients**: Binary gates → continuous features (0-1 scale)
   - `RIM_PRESSURE_DEFICIT`: `(threshold - rim_appetite) / threshold` (measures magnitude of flaw)
   - `ABDICATION_MAGNITUDE`: `max(0, -LEVERAGE_USG_DELTA)` with Smart Deference exemption
   - `INEFFICIENT_VOLUME_SCORE`: `creation_vol × negative_tax_magnitude` (Volume × Flaw)
2. **Explicit Interaction Terms**: Teach model that high usage amplifies flaws
   - `SYSTEM_DEPENDENCE_SCORE`: `USG_PCT × (assisted_pct + open_shot_freq)`
   - `EMPTY_CALORIES_RISK`: `USG_PCT × RIM_PRESSURE_DEFICIT`
3. **Asymmetric Loss (Sample Weighting)**: 5x weight for high-usage victims (penalizes false positives) - **Increased from 3x on December 8, 2025**

**Results**:
- ✅ **Model Retrained**: December 8, 2025 with portable features and 5x sample weighting
- ✅ **RFE Feature Selection**: `INEFFICIENT_VOLUME_SCORE` included in top 15 features (rank #13)
- ✅ **Test Suite Performance**: 75.0% pass rate (24/32) with gates enabled
  - **True Positives**: 77.8% (7/9) ✅ - Model correctly identifies latent stars
  - **False Positives**: 80.0% (4/5) ✅ - **Major improvement** from 40.0% (+40.0 pp)
  - **True Negatives**: 70.6% (12/17) ✅ - **Major improvement** from 41.2% (+29.4 pp)
- ✅ **Key Finding**: 5x sample weighting significantly improved false positive detection. Jordan Poole, Christian Wood, and D'Angelo Russell now pass. KAT: 4/6 seasons pass (was 0/6).

**Key Principle**: **Learn, Don't Patch**. Continuous gradients and interaction terms teach the model complex relationships. Sample weighting addresses asymmetric cost of false positives.

**See**: `KEY_INSIGHTS.md` (Insight #45: Continuous Gradients & Volume × Flaw Interactions) for complete details.

## Next Priority: Investigate Remaining Test Failures

**Status:** 🟡 MEDIUM PRIORITY (Down from HIGH - 5x penalty improved results significantly)

**Remaining Failures (8 cases):**

1. **Desmond Bane (2021-22)**: 48.96% (expected ≥65%)
   - **Root Cause**: True positive case - under-predicted
   - **Category**: True Positive
   - **Next Steps**: Investigate why model under-predicts Bane - may need gate logic adjustment

2. **Julius Randle (2020-21)**: 61.13% (expected <55%)
   - **Root Cause**: False positive case - All-NBA regular season but playoff collapse
   - **Category**: False Positive
   - **Note**: Close to threshold (61.13% vs 55%), improved from previous failures
   - **Next Steps**: Evaluate if this is acceptable or needs refinement

3. **Domantas Sabonis (2021-22)**: Risk category mismatch
   - **Root Cause**: Expected "Luxury Component", got "Moderate Performance, High Dependence"
   - **Category**: True Negative
   - **Note**: Gates capping at 30% - may need gate logic adjustment
   - **Next Steps**: Check gate logic for risk category assignment

4. **Tyrese Haliburton (2021-22)**: 30.00% (expected ≥65%)
   - **Root Cause**: True positive case - gates capping at 30%
   - **Category**: True Positive
   - **Next Steps**: Check data completeness and gate logic - gates are too aggressive

5. **Karl-Anthony Towns (2018-19)**: 78.30% (expected <55%)
   - **Root Cause**: True negative case - model overvaluing KAT
   - **Category**: True Negative
   - **Note**: Improved - 4/6 KAT seasons now pass (was 0/6)
   - **Next Steps**: Investigate remaining 2 seasons

6. **Karl-Anthony Towns (2020-21)**: 61.30% (expected <55%)
   - **Root Cause**: True negative case - model overvaluing KAT
   - **Category**: True Negative
   - **Note**: Close to threshold, improved from previous failures
   - **Next Steps**: Evaluate if acceptable

7. **Markelle Fultz (2019-20)**: 79.20% (expected <55%)
   - **Root Cause**: True negative case - model overvaluing Fultz
   - **Category**: True Negative
   - **Note**: 4/7 Fultz seasons now pass (improved)
   - **Next Steps**: Investigate remaining seasons

8. **Markelle Fultz (2022-23)**: 89.22% (expected <55%)
   - **Root Cause**: True negative case - model overvaluing Fultz
   - **Category**: True Negative
   - **Note**: Similar pattern to 2019-20
   - **Next Steps**: Investigate what features are driving high predictions
