# Current State: NBA Playoff Resilience Engine

Date: December 6, 2025

Status: Data Leakage Fixes Complete ✅ | Previous Playoff Features Integrated ✅ | Temporal Train/Test Split Implemented ✅ | 2D Risk Matrix Complete ✅ | Alpha Engine Implementation Complete ✅

## 🏗️ Project Structure & Cleanup

We are currently consolidating the codebase. Obsolete frameworks (Linear Regression, Complex 5-Pathway) are being archived to focus on the Active XGBoost Pipeline.

### Active Pipeline Components

These are the core files driving the current 55.01% accuracy model:

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
- `src/nba_data/scripts/calculate_dependence_score.py` (2D Risk Y-Axis, Alpha Engine)
- `src/nba_data/scripts/generate_trajectory_features.py` (Priors/Trajectory)
- `src/nba_data/scripts/generate_gate_features.py` (Soft Gates)
- `src/nba_data/scripts/generate_previous_playoff_features.py` (Past PO Performance)

**Alpha Engine (Value - Price):**
- `src/nba_data/scripts/collect_salary_data.py` (Salary data collection)
- `src/nba_data/scripts/calculate_alpha_scores.py` (Alpha calculation)

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

**Accuracy:** 55.01% (RFE model, 11 features with DEPENDENCE_SCORE) / 51.69% (Full model, 60 features) - True predictive power using only Regular Season data with temporal train/test split (899 player-seasons, 2015-2024, retrained December 6, 2025)

## What Exists (Current State)

### Data Pipeline

**Complete Dataset:** 10 seasons (2015-2024), 5,312 player-season records

**Key Data Files:**
- `results/predictive_dataset.csv`: Stress vectors (5,312 player-seasons)
- `results/resilience_archetypes.csv`: Playoff archetypes (labels)
- `results/pressure_features.csv`: Pressure vector features
- `data/playoff_pie_data.csv`: Playoff advanced stats
- `data/salaries.csv`: Historical salary data (4,680 player-seasons, 2015-2025) ⭐ NEW
- `results/alpha_scores.csv`: Alpha scores (Value - Price) for 885 player-seasons ⭐ NEW

**Data Coverage:**
- Stress vectors: 100% coverage
- Usage (USG_PCT): 100% coverage
- Age: 100% coverage
- Clock data: 100% coverage (all seasons)
- Rim pressure data: 95.9% coverage (1,773/1,849 in expanded predictions) - Fixed December 5, 2025 ✅

### Model Architecture

**Algorithm:** XGBoost Classifier (Multi-Class)

**RFE-Optimized Model (11 features) - CURRENT:**
1. USG_PCT (45.27% importance) - Usage level (highest importance!)
2. USG_PCT_X_EFG_ISO_WEIGHTED (8.32% importance) - Usage × Isolation efficiency
3. EFG_PCT_0_DRIBBLE (7.33% importance) - Catch-and-shoot efficiency
4. CREATION_TAX (6.47% importance) - Creation efficiency drop-off
5. **DEPENDENCE_SCORE (5.92% importance)** - System dependence (Alpha Engine) ⭐ NEW
6. EFG_ISO_WEIGHTED_YOY_DELTA (5.16% importance) - Year-over-year change in isolation efficiency
7. LEVERAGE_USG_DELTA (4.73% importance) - Clutch usage scaling
8. PREV_LEVERAGE_TS_DELTA (4.61% importance) - Previous season leverage efficiency
9. USG_PCT_X_CREATION_VOLUME_RATIO (4.51% importance) - Usage × Creation volume
10. RS_LATE_CLOCK_PRESSURE_APPETITE (3.92% importance) - Late clock pressure appetite
11. PREV_RS_RIM_APPETITE (3.76% importance) - Previous season rim pressure

**Key Insights:**
- All features are RS-only or trajectory-based (previous season). No playoff features made it into the top 11.
- Usage-aware features dominate (65.9% combined importance).
- **DEPENDENCE_SCORE** is now a mandatory feature (5.92% importance) - enables Alpha Engine to identify system merchants.

**Model File:** `models/resilience_xgb_rfe_10.pkl` (primary), `models/resilience_xgb.pkl` (fallback)

### Validation Results

**Test Case Pass Rate:** 68.8% (11/16)

**True Positives:** 62.5% (5/8)
- ✅ Victor Oladipo: 65.09% (PASS)
- ✅ Tyrese Haliburton: 93.76% (PASS)
- ✅ Tyrese Maxey: 96.16% (PASS)
- ✅ Shai Gilgeous-Alexander: 90.29% (PASS)
- ✅ Jalen Brunson: 94.02% (PASS)
- ✅ Jamal Murray: 72.39% (PASS)
- ✅ Talen Horton-Tucker: 16.79% (PASS - correctly identified as Victim)

**False Positives:** 83.3% (5/6) - Strong ✅
- ✅ Jordan Poole: 52.84% (PASS - correctly downgraded)
- ✅ Domantas Sabonis: 30.00% (PASS - correctly filtered)
- ✅ D'Angelo Russell: 30.00% (PASS - correctly filtered) - FIXED December 2025
- ✅ Ben Simmons: 30.00% (PASS - correctly filtered)
- ✅ All other false positives correctly filtered

**Remaining Failures (5 cases):**
- ❌ Mikal Bridges: 30.00% (expected ≥65%) - Usage Shock case (hardest test)
- ❌ Desmond Bane: 43.80% (expected ≥65%) - Secondary creator, model underestimates
- ❌ Tyrese Haliburton: 30.00% (expected ≥65%) - Low usage latent star, model misses
- ⚠️ Shai Gilgeous-Alexander: Predicted King instead of Bulldozer (archetype mismatch, but correct star-level)
- ⚠️ Lauri Markkanen: Predicted King instead of Bulldozer (archetype mismatch, but correct star-level)

## 2D Risk Matrix Implementation (December 2025) ✅ COMPLETE

**The Discovery:** The model correctly predicts Performance (outcomes), but we're trying to predict two different things in one dimension.

**The Ground Truth Trap:** Training labels are based on outcomes (Poole = "King" because he succeeded), but we want to predict portability (Poole = "System Merchant" because his production isn't portable).

**The Solution:** 2D Risk Matrix separating Performance (what happened) from Dependence (is it portable?).

**Validation Results:**
- ✅ Luka Dončić: Franchise Cornerstone (96.87% Performance, 26.59% Dependence)
- ✅ Jordan Poole: Luxury Component (58.62% Performance, 51.42% Dependence)

## Alpha Engine Implementation (December 2025) ✅ COMPLETE

**Status**: ✅ **COMPLETE** - December 6, 2025

**What Was Implemented**:
1. **Principle 1: Volume Exemption Fix** - Refined to distinguish "Engines" (Good Volume) from "Black Holes" (Bad Volume)
   - Volume Exemption now requires: `CREATION_VOLUME_RATIO > 0.60 AND (CREATION_TAX >= -0.05 OR RS_RIM_APPETITE >= 0.1746)`
   - Catches "Empty Calories" creators (Waiters, Dunn, Hernangomez) while preserving true creators (Haliburton, Maxey)
   
2. **Principle 3: DEPENDENCE_SCORE Integration** - Added as mandatory feature in XGBoost model
   - DEPENDENCE_SCORE: 5.92% importance (5th most important feature)
   - Model learns to penalize high-dependence players (system merchants) in star-level predictions
   - Coverage: 100% (899/899 player-seasons)
   
3. **Principle 4: Alpha Calculation Framework** - Maps model outputs to salary data
   - Salary data collection: 4,680 player-seasons (2015-2025) from Basketball Reference
   - Alpha scores calculated: 885/1,871 player-seasons (47.3% coverage)
   - Identifies: Undervalued Stars (13), Overvalued Players (149), Rookie Contract Stars (0)

**Key Results**:
- ✅ Model accuracy improved: 53.54% → 55.01% (+1.47 pp) with DEPENDENCE_SCORE
- ✅ Test case pass rate maintained: 68.8% (11/16)
- ✅ Volume Exemption fix validated: D'Angelo Russell correctly filtered (30% star-level)
- ✅ Alpha opportunities identified: 13 undervalued stars (Brunson Zone)

**See**: `ALPHA_ENGINE_IMPLEMENTATION.md` and `ALPHA_ENGINE_VALIDATION_RESULTS.md` for complete details.
