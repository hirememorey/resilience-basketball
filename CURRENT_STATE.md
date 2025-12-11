# Current State: NBA Playoff Resilience Engine

Date: December 11, 2025

Status: Temporal Split ✅ | Dual-Model Bundle (Performance + Dependence) ✅ | Universal Projection ✅ | Feature Alignment/USG Normalization ✅ | Gates Disabled by Default ✅ | Single Brake (clutch-floor) ✅ | Latest Pass Rate 52.5% (TP 47.1%, FP 40.0%, TN 58.8%) 🔄 Plateau

## 🏗️ Project Structure & Cleanup

We are currently consolidating the codebase. Obsolete frameworks (Linear Regression, Complex 5-Pathway) are being archived to focus on the Active XGBoost Pipeline.

### Latest Update (Dec 11, 2025) — Plateau at 52.5% (gates on)
- Data refreshed: shot quality/clock, shot charts (rerun with lower concurrency), rim pressure, dependence, gate features; predictive_dataset rebuilt.
- Model: 15-feature XGB, single brake (clutch-floor) at 0.02 / 4.0, fixed performance cut 0.74–0.78, floor/clutch interactions added (CLUTCH_X_TS_FLOOR_GAP, USG_PCT_X_TS_PCT_VS_USAGE_BAND_EXPECTATION), class weighting Victim 1.5, deeper config (200 trees, depth 5). RFE 20-feature variant also trained (`models/resilience_xgb_rfe_20.pkl`).
- Validation (latent_star_cases, gates on): 52.5% pass (TP 47.1%, FP 40.0%, TN 58.8%, System 100%). No improvement across iterations; penalties/feature tweaks stalled.
- Remaining FPs: Jordan Poole 21-22, Julius Randle 20-21 (others resolved). SHAP shows clutch/floor signals not dominating star classes.
- Next: consider model-architecture change (e.g., different loss/model family or pure class weighting without layered penalties) rather than further penalty tuning.

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

### Model Architecture (Dec 11, 2025)

- File: `models/resilience_xgb_rfe_phoenix.pkl` (15 features), single brake (clutch-floor weight 4.0), class weight Victim 1.5; performance cut calibrated to 0.78 (creators 60th pct, clipped 0.74–0.78); monotone constraints on floor/clutch interactions.
- File: `models/resilience_xgb_rfe_20.pkl` (20-feature RFE variant) similar performance.
- Dependence regressor: MSE ~0.006, R2 ~0.79; calibrated creator cuts low=0.2879, high=0.3945.

### Current Validation Snapshot (latent_star_cases, Dec 10 dual-model, gates off)
- Pass rate: 55.0% (22/40)
- True Positives: 6/17 (35.3%)
- False Positives: 3/5 (60.0%)
- True Negatives: 12/17 (70.6%)
- System Player: 1/1 (100%)
- Observations: Poole/Fultz still high performance; dependence moves them to Luxury (not Cornerstone). Cornerstone bigs sometimes downgraded to Luxury when dependence is high. Performance cut is still fixed at 0.65 (needs calibration).

### Next Steps (for new developer)
- Calibrate performance score on validation creators (USG≥0.20) and set data-driven high/low cuts instead of fixed 0.65.
- Strengthen dependence signals if needed: add explicit USG×DEPENDENCE_SCORE and context/open-shot reliance features to training (feature, not gate).
- Keep inference gate-free; adjust only calibrated cuts or features, not post-hoc gates.

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

## ✅ Completed: Phase 4.4 - Gate Logic Refinement (December 8, 2025)

**Status**: ✅ **COMPLETE**

**The Problem**: 8 test failures remained after Phase 4.2. First principles analysis identified three distinct failure modes:
1. **Definition Mismatch (False Negatives)**: System incorrectly defining "Resilience" strictly as Rim Pressure (Haliburton) or "Performance" as Independence (Sabonis)
2. **Constraint Failures (False Positives)**: System failing to enforce "Physics Constraints" on players who collapse in high-leverage moments (KAT, Randle) or rewards noise in low-sample data (Fultz)
3. **Relative vs. Absolute (Under-prediction)**: System penalizing elite players for relative dips even when absolute performance remains elite (Bane)

**The Solution**: Surgical refinement of gate logic with context-aware exemptions:
1. **Elite Creator Exemption**: Lowered threshold to 0.65, added OR-based logic (creation volume OR elite efficiency)
2. **Clutch Fragility Gate**: Cap at 30% if LEVERAGE_TS_DELTA < -0.10 (catastrophic clutch collapse)
3. **Creation Fragility Gate**: Cap at 30% if CREATION_TAX < -0.15, with young player exemption (AGE < 22 with positive leverage)
4. **Compound Fragility Gate**: Cap at 30% if CREATION_TAX < -0.10 AND LEVERAGE_TS_DELTA < -0.05, with elite creator exemption
5. **Low-Usage Noise Gate**: Cap at 30% if USG_PCT < 22% AND abs(CREATION_TAX) < 0.05 (ambiguous signal = noise)
6. **Volume Creator Inefficiency Gate**: Cap at 30% if CREATION_VOLUME_RATIO > 0.70 AND CREATION_TAX < -0.08 AND LEVERAGE_TS_DELTA <= 0
7. **Risk Category Threshold Fix**: Allow "Luxury Component" for Performance ≥ 30% AND Dependence ≥ 50%

**Results**:
- ✅ **Test Suite Pass Rate**: 75.0% → **90.6%** (+15.6 pp)
- ✅ **True Negatives**: 70.6% → **100.0%** (17/17) - **Perfect**
- ✅ **False Positives**: 80.0% (maintained)
- ✅ **True Positives**: 77.8% (maintained)
- ✅ **Key Fixes**: Randle, KAT (all seasons), Fultz (all seasons), Sabonis, Tatum, Maxey all now pass

**Key Principle**: **Logic Over Weights**. Hard-code the "Physics of the Game" into gates (e.g., "If you don't go to the rim, you MUST be an elite creator to survive"). Context-aware exemptions prevent over-correction.

**See**: `docs/IMPLEMENTATION_SUMMARY.md` for complete details.

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

**Status:** 🟡 LOW PRIORITY (Down from MEDIUM - Phase 4.4 gate refinement achieved 90.6% pass rate)

**Remaining Failures (3 cases):**

1. **Desmond Bane (2021-22)**: 48.10% (expected ≥65%)
   - **Root Cause**: Model under-prediction (Elite Efficiency Override implemented but insufficient)
   - **Category**: True Positive
   - **Next Steps**: Investigate model under-prediction - may require model retraining or feature adjustment

2. **D'Angelo Russell (2018-19)**: 96.77% (expected <55%)
   - **Root Cause**: Volume Creator Inefficiency Gate not catching (positive leverage exemption)
   - **Category**: False Positive
   - **Next Steps**: Consider adjusting Volume Creator Inefficiency Gate exemption thresholds

3. **Tyrese Haliburton (2021-22)**: 58.66% (expected ≥65%)
   - **Root Cause**: Model under-prediction (improved from 30% to 58.66% with Elite Creator Exemption)
   - **Category**: True Positive
   - **Next Steps**: Investigate model under-prediction - may require model retraining or feature adjustment
