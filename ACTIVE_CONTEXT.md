# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 8, 2025  
**Status**: Phase 4.2 Complete ✅ | Model Retrained ✅ | 5x Sample Weighting ✅

---

## Project Goal

Identify players who consistently perform better than expected in the playoffs and explain *why* using mechanistic insights. The model predicts playoff archetypes (King, Bulldozer, Sniper, Victim) from regular season stress vectors with usage-aware conditional predictions.

---

## Current Phase: Production-Ready Model

**Model Status**: RFE-optimized XGBoost Classifier with 10 core features, continuous gradients, and 5x sample weighting for asymmetric loss. All data leakage removed, temporal train/test split implemented, 2D Risk Matrix integrated.

**Key Achievement**: Model achieves **46.77% accuracy** with **true predictive power** (RS-only features, temporal split). This represents genuine predictive capability, not inflated accuracy from data leakage.

---

## Scoreboard (Current Metrics)

### Model Performance
- **Accuracy**: 46.77% (RFE model, 10 features, 5x sample weighting)
- **True Predictive Power**: RS-only features, temporal split (2015-2020 train, 2021-2024 test)
- **Dataset**: 5,312 player-seasons (2015-2024), 899 in train/test split

### Test Suite Performance (32 cases)
- **Overall Pass Rate (With Gates)**: 75.0% (24/32) ✅
  - **True Positives**: 77.8% (7/9) ✅
  - **False Positives**: 80.0% (4/5) ✅ - **Major improvement** from 40.0% (+40.0 pp)
  - **True Negatives**: 70.6% (12/17) ✅ - **Major improvement** from 41.2% (+29.4 pp)
- **Pass Rate (Trust Fall 2.0 - Gates Disabled)**: 56.2% (18/32)
  - Model identifies stars well (88.9% True Positives) but struggles with false positives (40.0% False Positives)

### Data Coverage
- **USG_PCT**: 100% ✅ (Fixed Dec 8, 2025)
- **AGE**: 100% ✅ (Fixed Dec 8, 2025)
- **Playtype Data**: 79.3% (4,210/5,312) ✅ (Fixed Dec 8, 2025)
- **Rim Pressure**: 95.9% (1,773/1,849) ✅ (Fixed Dec 5, 2025)

---

## Active Pipeline

### Data Ingestion
- `src/nba_data/scripts/collect_regular_season_stats.py`
- `src/nba_data/scripts/collect_playoff_logs.py`
- `src/nba_data/scripts/collect_shot_charts.py` (with predictive dataset support)
- `src/nba_data/scripts/collect_shot_quality_with_clock.py`

### Feature Engineering
- `src/nba_data/scripts/calculate_simple_resilience.py` (Target Generation)
- `src/nba_data/scripts/evaluate_plasticity_potential.py` (Creation, Leverage, Context, Playtype)
- `src/nba_data/scripts/calculate_rim_pressure.py` (Physicality)
- `src/nba_data/scripts/calculate_shot_difficulty_features.py` (Pressure)
- `src/nba_data/scripts/calculate_dependence_score.py` (2D Risk Y-Axis)
- `src/nba_data/scripts/generate_trajectory_features.py` (Priors/Trajectory)
- `src/nba_data/scripts/generate_gate_features.py` (Soft Gates)
- `src/nba_data/scripts/generate_previous_playoff_features.py` (Past PO Performance)

### Modeling & Inference
- `src/nba_data/scripts/train_rfe_model.py` (Primary Trainer - 10 features)
- `src/nba_data/scripts/predict_conditional_archetype.py` (Core Inference Engine)
- `src/nba_data/scripts/detect_latent_stars_v2.py` (Latent Star Detection)
- `run_expanded_predictions.py` (Batch Inference)

### Validation
- `test_latent_star_cases.py` (32 critical cases - uses 2D Risk Matrix)
- `test_2d_risk_matrix.py` (Risk Matrix Suite)
- `analyze_model_misses.py` (Miss Analysis)

---

## Current Model Architecture

### Top 10 Features (RFE-Optimized)
1. **USG_PCT** (41.26%) - Usage level
2. **USG_PCT_X_EFG_ISO_WEIGHTED** (8.85%) - Usage × Isolation efficiency
3. **CREATION_TAX** (8.54%) - Creation efficiency drop-off
4. **USG_PCT_X_RS_LATE_CLOCK_PRESSURE_RESILIENCE** (7.16%) - Usage × Late clock resilience
5. **ABDICATION_RISK** (6.71%) - Continuous gradient (negative leverage signal)
6. **RS_LATE_CLOCK_PRESSURE_APPETITE** (6.33%) - Late clock pressure willingness
7. **CLUTCH_MIN_TOTAL** (5.39%) - Clutch minutes
8. **QOC_USG_DELTA** (5.28%) - Quality of competition usage delta
9. **CREATION_TAX_YOY_DELTA** (5.26%) - Year-over-year change in creation tax
10. **AGE_X_RS_PRESSURE_RESILIENCE_YOY_DELTA** (5.21%) - Age × Pressure resilience trajectory

**Key Insight**: Usage-aware features dominate (USG_PCT: 41.26% importance). All features are RS-only or trajectory-based.

### Model Features (Phase 4.2)
- **Continuous Gradients**: Binary gates converted to continuous features (RIM_PRESSURE_DEFICIT, ABDICATION_MAGNITUDE, INEFFICIENT_VOLUME_SCORE)
- **Volume × Flaw Interactions**: Explicit interaction terms (SYSTEM_DEPENDENCE_SCORE, EMPTY_CALORIES_RISK)
- **Sample Weighting**: 5x weight for high-usage victims (penalizes false positives)
- **Hard Gates**: **DISABLED BY DEFAULT** (`apply_hard_gates=False`) - model learns from continuous gradients

**Model File**: `models/resilience_xgb_rfe_10.pkl` (primary)

---

## Immediate Next Steps (Top 3 Priorities)

### 1. Investigate Remaining Test Failures (8 cases) 🟡 MEDIUM PRIORITY

**Status**: 5x sample weighting improved results significantly (75.0% pass rate), but 8 failures remain.

**Remaining Failures**:
- **Desmond Bane (2021-22)**: 48.96% (expected ≥65%) - True positive, under-predicted
- **Julius Randle (2020-21)**: 61.13% (expected <55%) - False positive, close to threshold
- **Domantas Sabonis (2021-22)**: Risk category mismatch - Gates capping at 30%
- **Tyrese Haliburton (2021-22)**: 30.00% (expected ≥65%) - True positive, gates capping
- **KAT (2018-19, 2020-21)**: 2 seasons over-predicted (True negatives)
- **Markelle Fultz (2019-20, 2022-23)**: 2 seasons over-predicted (True negatives)

**Root Causes**:
1. Gate capping preventing correct risk categorization (Sabonis, Haliburton)
2. Model false positives (KAT, Fultz later seasons)

**Next Actions**:
- Check gate logic for Sabonis/Haliburton (gates too aggressive)
- Investigate why model overvalues KAT/Fultz in later seasons
- Consider increasing sample weight penalty to 10x if needed

### 2. Evaluate Test Suite Refinement

**Status**: 2 test cases may be removed from test suite.

**Cases**:
- **Mikal Bridges** (30.00%, expected ≥65%) - Usage Shock case, may be accurately rated
- **Desmond Bane** (26.05%, expected ≥65%) - Unclear if actually broke out (as of Dec 2025)

**Action**: Evaluate if these are legitimate model predictions or actual failures. If accurately rated, remove from test suite.

### 3. Monitor Model Performance

**Status**: Model is production-ready but needs ongoing validation.

**Actions**:
- Run test suite after any code changes
- Monitor false positive rate (currently 80.0% pass rate)
- Track model accuracy on new seasons as they become available

---

## Key Completed Work (Recent)

### ✅ Phase 4.2: Continuous Gradients & Sample Weighting (Dec 8, 2025)
- Converted binary gates to continuous gradients
- Added Volume × Flaw interaction terms
- Implemented 5x sample weighting for high-usage victims
- **Result**: False positive detection improved from 40.0% to 80.0% (+40.0 pp)

### ✅ 2D Risk Matrix Integration (Dec 7, 2025)
- Test suite now uses `predict_with_risk_matrix()` for all cases
- Provides both Performance Score (1D) and Risk Category (2D)
- **Result**: Jordan Poole correctly identified as "Luxury Component"

### ✅ Universal Projection Implementation (Dec 7, 2025)
- Features now scale together using empirical distributions
- **Result**: Test suite pass rate improved from 68.8% to 81.2% (+12.4 pp)

### ✅ Data Completeness Fixes (Dec 8, 2025)
- USG_PCT and AGE: 0% → 100% coverage
- Playtype data: 8.6% → 79.3% coverage
- **Result**: Model can now make valid predictions

---

## Key Files Reference

### Core Documentation
- **`.cursorrules`** - System instructions (always loaded)
- **`KEY_INSIGHTS.md`** - 48 hard-won lessons (reference on demand)
- **`LUKA_SIMMONS_PARADOX.md`** - Theoretical foundation (reference for gate logic)

### Model Files
- **`models/resilience_xgb_rfe_10.pkl`** - Current model (10 features)
- **`results/rfe_model_results_10.json`** - Model results and feature list

### Data Files
- **`results/predictive_dataset.csv`** - Stress vectors (5,312 player-seasons)
- **`results/resilience_archetypes.csv`** - Playoff archetypes (labels)
- **`results/pressure_features.csv`** - Pressure vector features

### Test Suite
- **`test_latent_star_cases.py`** - 32 critical test cases
- **`results/latent_star_test_cases_report.md`** - Latest test results

---

## Key Principles (Quick Reference)

1. **Filter First, Then Rank** - Value is relative to the cohort, not absolute
2. **No Proxies** - Flag missing data with confidence scores
3. **Resilience = Efficiency × Volume** - The "Abdication Tax" is real
4. **Learn, Don't Patch** - Continuous gradients > hard gates
5. **Two-Dimensional Evaluation** - Performance vs. Dependence are orthogonal
6. **Features Must Scale Together** - Universal Projection with empirical distributions

**See**: `.cursorrules` for complete principles and `KEY_INSIGHTS.md` for detailed explanations.

---

**Note**: This file should be updated after major changes to reflect current state. For detailed historical context, see `CURRENT_STATE.md` and `NEXT_STEPS.md` (archived after consolidation).

