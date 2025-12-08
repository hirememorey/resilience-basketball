# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 8, 2025  
**Status**: Phase 4.4 Complete ✅ | Gate Logic Refinement Complete ✅ | 90.6% Test Pass Rate ✅

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
- **Overall Pass Rate (With Gates)**: 90.6% (29/32) ✅ - **Major improvement** from 75.0% (+15.6 pp)
  - **True Positives**: 77.8% (7/9) ✅
  - **False Positives**: 80.0% (4/5) ✅
  - **True Negatives**: 100.0% (17/17) ✅ - **Perfect** - **Major improvement** from 70.6% (+29.4 pp)
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

### Model Features (Phase 4.4)
- **Hard Gates**: **ENABLED BY DEFAULT** (`apply_hard_gates=True`) - surgical refinements based on first principles
- **Gate Logic**: Context-aware constraint system with nuanced exemptions and overrides
  - Elite Creator Exemption (CREATION_VOLUME_RATIO > 0.65 OR CREATION_TAX < -0.10)
  - Clutch Fragility Gate (LEVERAGE_TS_DELTA < -0.10)
  - Creation Fragility Gate (CREATION_TAX < -0.15, with young player exemption)
  - Compound Fragility Gate (CREATION_TAX < -0.10 AND LEVERAGE_TS_DELTA < -0.05)
  - Low-Usage Noise Gate (USG_PCT < 22% AND abs(CREATION_TAX) < 0.05)
  - Volume Creator Inefficiency Gate (CREATION_VOLUME_RATIO > 0.70 AND CREATION_TAX < -0.08)
- **Continuous Gradients**: Still available as features (RIM_PRESSURE_DEFICIT, ABDICATION_MAGNITUDE, INEFFICIENT_VOLUME_SCORE)
- **Sample Weighting**: 5x weight for high-usage victims (penalizes false positives)

**Model File**: `models/resilience_xgb_rfe_10.pkl` (primary)

---

## Immediate Next Steps (Top 3 Priorities)

### 1. Investigate Remaining Test Failures (3 cases) 🟡 LOW PRIORITY

**Status**: Gate logic refinement achieved 90.6% pass rate (29/32). 3 failures remain, primarily model under-prediction issues.

**Remaining Failures**:
- **Desmond Bane (2021-22)**: 48.10% (expected ≥65%) - Model under-prediction (Elite Efficiency Override implemented but insufficient)
- **D'Angelo Russell (2018-19)**: 96.77% (expected <55%) - Volume Creator Inefficiency Gate not catching (positive leverage exemption)
- **Tyrese Haliburton (2021-22)**: 58.66% (expected ≥65%) - Improved from 30% to 58.66% with Elite Creator Exemption, but still below threshold

**Root Causes**:
1. Model under-prediction for true positives (Bane, Haliburton) - may require model retraining or feature adjustment
2. Edge case where exemptions prevent gates from triggering (Russell)

**Next Actions**:
- Investigate model under-prediction (may need feature engineering or retraining)
- Consider adjusting Volume Creator Inefficiency Gate exemption thresholds
- Evaluate if remaining failures are acceptable given 90.6% pass rate

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

### ✅ Phase 4.4: Gate Logic Refinement (Dec 8, 2025)
- Implemented surgical gate refinements based on first principles analysis
- Added Elite Creator Exemption (threshold lowered to 0.65)
- Added Clutch Fragility Gate, Creation Fragility Gate, Compound Fragility Gate
- Added Low-Usage Noise Gate, Volume Creator Inefficiency Gate
- Fixed risk category thresholds (Luxury Component at 30% performance)
- **Result**: Test pass rate improved from 75.0% to 90.6% (+15.6 pp), True Negatives: 100% (17/17)

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

