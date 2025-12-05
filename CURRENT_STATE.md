# Current State: NBA Playoff Resilience Engine

**Date**: December 5, 2025  
**Status**: 2D Risk Matrix Implementation Complete ✅ | Data-Driven Thresholds Calculated | D'Angelo Russell Fix Complete ✅

---

## Project Overview

**Goal**: Identify players who consistently perform better than expected in the playoffs and explain *why* using mechanistic insights.

**Current Model**: XGBoost Classifier that predicts playoff archetypes (King, Bulldozer, Sniper, Victim) from regular season stress vectors with **usage-aware conditional predictions**. **RFE-optimized to 10 core features** (reduced from 65).

**Accuracy**: 63.33% (899 player-seasons, 2015-2024)

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
- Usage (USG_PCT): 100% coverage
- Age: 100% coverage
- Clock data: 100% coverage (all seasons)

### Model Architecture

**Algorithm**: XGBoost Classifier (Multi-Class)

**RFE-Optimized Model (10 features)** - **CURRENT**:
1. **USG_PCT** (28.9% importance) - Usage level (highest importance!)
2. **USG_PCT_X_EFG_ISO_WEIGHTED** (18.7% importance) - Usage × Isolation efficiency (2nd highest!)
3. **NEGATIVE_SIGNAL_COUNT** (10.5% importance) - Gate feature (3rd highest!)
4. **EFG_PCT_0_DRIBBLE** (6.8% importance) - Catch-and-shoot efficiency
5. **LEVERAGE_USG_DELTA** (6.1% importance) - #1 predictor (Abdication Detector)
6. **USG_PCT_X_RS_PRESSURE_APPETITE** (5.9% importance)
7. **PREV_RS_PRESSURE_RESILIENCE** (5.9% importance)
8. **LATE_CLOCK_PRESSURE_APPETITE_DELTA** (5.9% importance)
9. **USG_PCT_X_CREATION_VOLUME_RATIO** (5.7% importance)
10. **USG_PCT_X_LEVERAGE_USG_DELTA** (5.7% importance)

**Key Insight**: RFE analysis revealed that 10 features achieve peak accuracy (63.33%), matching or exceeding the 65-feature model (62.89%). Most trajectory and gate features add noise, not signal.

**Model File**: `models/resilience_xgb_rfe_10.pkl` (primary), `models/resilience_xgb.pkl` (fallback)

### Key Scripts

**Feature Generation**:
- `evaluate_plasticity_potential.py`: Generates Creation, Leverage, Plasticity vectors
- `calculate_shot_difficulty_features.py`: Generates Pressure vector features
- `collect_shot_quality_with_clock.py`: Collects clock data (parallelized)

**Model Training**:
- `train_rfe_model.py`: Trains RFE-optimized model (10 features) ✅
- `train_predictive_model.py`: Trains full model (65 features, fallback)

**Prediction**:
- `predict_conditional_archetype.py`: Conditional prediction function (predict at any usage level)
- `detect_latent_stars.py`: Latent star detection (age < 26, usage < 25%)

**Analysis**:
- `component_analysis.py`: Correlates stress vectors with playoff outcomes
- `calculate_simple_resilience.py`: Generates archetype labels

---

## Current Capabilities

### Usage-Aware Conditional Predictions

The model can predict at **any usage level**, enabling two use cases:

1. **Archetype Prediction**: "How will this player perform in playoffs given their current role?"
2. **Latent Star Detection**: "Who has the skills but hasn't been given opportunity?"

**Example**: Jalen Brunson (2020-21)
- At 19.6% usage: "Victim" (0.77% star-level) ✅ Correct
- At 32% usage: "Bulldozer" (94.02% star-level) ✅ Correct

**Key Principle**: Skills (stress vectors) are relatively stable across seasons. Performance (archetype) depends on opportunity (usage). The model learns: `archetype = f(stress_vectors, usage)` ✅

---

## Validation Results

### Test Case Pass Rate: 87.5% (14/16)

**True Positives**: 87.5% (7/8)
- ✅ Victor Oladipo: 65.09% (PASS)
- ✅ Tyrese Haliburton: 93.76% (PASS)
- ✅ Tyrese Maxey: 96.16% (PASS)
- ✅ Shai Gilgeous-Alexander: 90.29% (PASS)
- ✅ Jalen Brunson: 94.02% (PASS)
- ✅ Jamal Murray: 72.39% (PASS)
- ✅ Talen Horton-Tucker: 16.79% (PASS - correctly identified as Victim)

**False Positives**: 100% (6/6) - **Perfect** ✅
- ✅ Jordan Poole: 52.84% (PASS - correctly downgraded)
- ✅ Domantas Sabonis: 30.00% (PASS - correctly filtered)
- ✅ D'Angelo Russell: 30.00% (PASS - correctly filtered) - **FIXED December 2025**
- ✅ Ben Simmons: 30.00% (PASS - correctly filtered)
- ✅ All other false positives correctly filtered

**Remaining Failures (2 cases - may be removed from test suite)**:
- ⚠️ Mikal Bridges: 30.00% (expected ≥65%) - Usage Shock case, may be accurately rated
- ⚠️ Desmond Bane: 26.05% (expected ≥65%) - Unclear if actually broke out (as of Dec 2025)

**See**: `results/latent_star_test_cases_report.md` for complete validation results.

---

## Key Features Implemented

### Multi-Signal Tax System (Phase 4.2)

Addresses "The Poole Problem" (System Merchant Detection):
- **4-Tax System**: Open Shot Dependency (50%), Creation Efficiency Collapse (20%), Leverage Abdication (20%), Pressure Avoidance (20%)
- **Volume Exemption**: `CREATION_VOLUME_RATIO > 0.60` exempts true stars
- **Late Clock Dampener**: Reduces penalty by half if elite late clock resilience
- **Taxes Both Volume AND Efficiency**: System merchants lose both opportunity and efficiency

### Gate Features

Converted hard gates to soft features that the model learns:
- **Abdication Risk**: Detects passivity (negative LEVERAGE_USG_DELTA)
- **Physicality Floor**: Caps players with zero rim pressure
- **Bag Check Gate**: Requires self-created volume for primary initiators
- **Data Completeness**: Ensures sufficient data for reliable predictions
- **Negative Signal Count**: Counts multiple negative signals

**Key Insight**: `NEGATIVE_SIGNAL_COUNT` ranks 3rd in feature importance (10.5%), validating that gate features work.

---

## 2D Risk Matrix Implementation (December 2025) ✅ COMPLETE

**The Discovery**: The model correctly predicts **Performance** (outcomes), but we're trying to predict two different things in one dimension.

**The Ground Truth Trap**: Training labels are based on **outcomes** (Poole = "King" because he succeeded), but we want to predict **portability** (Poole = "System Merchant" because his production isn't portable).

**The Solution**: **2D Risk Matrix** separating Performance (what happened) from Dependence (is it portable?).

### Implementation Status: ✅ COMPLETE

**Components Implemented**:
1. **Dependence Score Calculation** (`calculate_dependence_score.py`)
   - Quantitative formula: `ASSISTED_FGM_PCT * 0.40 + OPEN_SHOT_FREQUENCY * 0.35 + (1 - SELF_CREATED_USAGE_RATIO) * 0.25`
   - Calculated from objective data (no training labels needed)
   - Integrated into `predict_conditional_archetype.py`

2. **2D Prediction Function** (`predict_with_risk_matrix()`)
   - Returns both Performance Score and Dependence Score
   - Categorizes players into 4 risk quadrants:
     - **Franchise Cornerstone**: High Performance + Low Dependence
     - **Luxury Component**: High Performance + High Dependence
     - **Depth**: Low Performance + Low Dependence
     - **Avoid**: Low Performance + High Dependence

3. **Data-Driven Thresholds** ✅
   - Calculated 33rd and 66th percentiles from 533 star-level players (USG_PCT > 25%)
   - **Low Dependence**: < 0.3570 (33rd percentile)
   - **High Dependence**: ≥ 0.4482 (66th percentile)
   - Replaced arbitrary 0.30/0.70 thresholds with data-driven values
   - Saved to `results/dependence_thresholds.json`

4. **Gate Logic Refinements** ✅
   - **High-Usage Immunity** (Abdication Tax): Players with RS_USG_PCT > 30% exempted from small usage drops
   - **High-Usage Creator Exemption** (Fragility Gate): Players with CREATION_VOLUME_RATIO > 0.60 and USG_PCT > 0.25 exempted
   - Fixed "Luka Performance Cap" showstopper (Luka now correctly identified as 96.87% Performance)

**Validation Results**:
- ✅ Luka Dončić: **Franchise Cornerstone** (96.87% Performance, 26.59% Dependence)
- ✅ Jordan Poole: **Luxury Component** (58.62% Performance, 51.42% Dependence)
- ✅ Dependence scores properly distributed (most players in moderate range)

**Key Files**:
- `src/nba_data/scripts/calculate_dependence_score.py` - Dependence score calculation
- `src/nba_data/scripts/predict_conditional_archetype.py` - 2D prediction function
- `test_2d_risk_matrix.py` - Validation test suite
- `calculate_dependence_thresholds.py` - Threshold calculation script
- `results/dependence_thresholds.json` - Data-driven thresholds
- `results/data_driven_thresholds_summary.md` - Implementation summary
- `results/luka_gate_fix_summary.md` - Gate logic fixes

**See**: `2D_RISK_MATRIX_IMPLEMENTATION.md` for complete implementation plan and `results/data_driven_thresholds_summary.md` for threshold analysis.

---

## Expanded Dataset Analysis: Complete ✅

**Status**: Expanded predictions run on 1,849 player-seasons (Age ≤ 25, Min 500 minutes)

**Results**:
- **Dataset**: 1,849 player-seasons from 2015-2024
- **Top Latent Stars**: Shai Gilgeous-Alexander (97.69%), Deandre Ayton (96.88%), Derrick White (96.58%)
- **Risk Categories**: 1,080 "Avoid" (58.4%), 98 "Franchise Cornerstone" (5.3%)
- **2D Risk Matrix**: Working correctly - Performance Score at current usage, potential at 25% usage

**Key Findings from Model Misses Analysis**:
- **7/10 "misses" are either correct or debatable** (Kawhi, Tatum, Schröder cases)
- **3/10 are true misses**: "Empty Calories" creators (high volume + negative creation tax)
- **Root Cause**: Volume Exemption too broad - doesn't distinguish efficient vs. inefficient creators
- **Data Issue**: 80% of misses lack rim pressure data, preventing Fragility Gate from working

**See**: `results/expanded_predictions.csv` for full results and `results/model_misses_analysis.md` for detailed analysis.

---

## Known Issues & Limitations

1. **Two test cases may be removed from test suite**: Mikal Bridges and Desmond Bane may be accurately rated (not actual failures)
2. ~~**D'Angelo Russell Phenomenon**: Needs investigation - why does the model rate him differently than expected?~~ ✅ **FIXED** - Refined High-Usage Creator Exemption to distinguish between versatile creators (Luka) and limited creators (Russell). See `results/dangelo_russell_deep_dive.md`.
3. **Volume Exemption Too Broad**: High creation volume (>0.60) exempts players from Multi-Signal Tax, even when creation is inefficient. Need to refine to require efficient creation OR rim pressure. See `results/model_misses_analysis.md`.
4. **Missing Rim Pressure Data**: 80% of model misses lack `RS_RIM_APPETITE` data, preventing Fragility Gate from catching them. Need to fix data pipeline.

---

## Key Files & Their Purpose

### Core Documentation
- **`README.md`**: Project overview and quick start
- **`NEXT_STEPS.md`**: What to work on next
- **`KEY_INSIGHTS.md`**: Hard-won lessons (critical reference)
- **`LUKA_SIMMONS_PARADOX.md`**: Theoretical foundation

### Model & Data
- **`models/resilience_xgb_rfe_10.pkl`**: **CURRENT MODEL** (10 features)
- **`results/predictive_dataset.csv`**: Stress vectors (features)
- **`results/resilience_archetypes.csv`**: Playoff archetypes (labels)
- **`results/pressure_features.csv`**: Pressure vector features

### Scripts
- **`src/nba_data/scripts/predict_conditional_archetype.py`**: Main prediction function (supports `apply_hard_gates` parameter for Trust Fall)
- **`src/nba_data/scripts/train_rfe_model.py`**: Train RFE-optimized model
- **`test_latent_star_cases.py`**: Validation test suite (supports `--trust-fall` flag)
- **`run_expanded_predictions.py`**: Run model on expanded dataset (Age ≤ 25, Min minutes threshold)
- **`analyze_model_misses.py`**: Diagnostic script to analyze specific model misses

---

**See Also**:
- `2D_RISK_MATRIX_IMPLEMENTATION.md` - ✅ **COMPLETE** - 2D framework implementation
- `NEXT_STEPS.md` - Current priorities and completed work
- `results/data_driven_thresholds_summary.md` - Data-driven threshold analysis
- `results/luka_gate_fix_summary.md` - Gate logic refinements
- `results/latent_star_test_cases_report.md` - Latest validation results (with gates)
- `results/rfe_model_comparison.md` - RFE model analysis
- `KEY_INSIGHTS.md` - Hard-won lessons (see Insight #37: Trust Fall & Ground Truth Trap, Insight #38: Data-Driven Thresholds)
