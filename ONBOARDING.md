# Onboarding Guide for New Developers

**Date**: December 4, 2025  
**Purpose**: Get a new developer up to speed quickly with all context needed to continue development.

---

## 🎯 Current State (TL;DR)

**What We Have**:
- ✅ **RFE-Optimized Model**: 10 features, 63.33% accuracy, 81.2% test case pass rate
- ✅ **Usage-Aware Predictions**: Can predict at any usage level
- ✅ **Complete Dataset**: 10 seasons (2015-2024), 5,312 player-seasons

**What's Next**:
- ⏭️ Fix 3 remaining edge cases (Poole, Bridges, Markkanen)
- ⏭️ Target: 87.5-93.8% pass rate (currently 81.2%)

---

## 📚 Essential Reading (In Order)

### 1. Start Here
- **`README.md`** - Project overview and quick start
- **`CURRENT_STATE.md`** - Detailed current state (updated with RFE model)
- **`NEXT_STEPS.md`** - What to work on next

### 2. Core Understanding
- **`LUKA_SIMMONS_PARADOX.md`** - Theoretical foundation (CRITICAL)
- **`extended_resilience_framework.md`** - Stress vectors explained
- **`KEY_INSIGHTS.md`** - Hard-won lessons (33+ principles)

### 3. Recent Work
- **`results/rfe_analysis_summary.md`** - RFE analysis results
- **`results/rfe_model_comparison.md`** - RFE vs. full model comparison
- **`results/latent_star_test_cases_report.md`** - Latest validation results

---

## 🔑 Key Concepts

### The Model

**Current Model**: `models/resilience_xgb_rfe_10.pkl`
- **10 features** (reduced from 65 via RFE)
- **63.33% accuracy** (improved from 62.89%)
- **81.2% test case pass rate** (13/16)

**Top 10 Features**:
1. `USG_PCT` (28.9% importance) - Usage level
2. `USG_PCT_X_EFG_ISO_WEIGHTED` (18.7% importance) - Usage × Isolation
3. `NEGATIVE_SIGNAL_COUNT` (10.5% importance) - Gate feature
4. `EFG_PCT_0_DRIBBLE` (6.8% importance) - Catch-and-shoot
5. `LEVERAGE_USG_DELTA` (6.1% importance) - #1 predictor
6. `USG_PCT_X_RS_PRESSURE_APPETITE` (5.9% importance)
7. `PREV_RS_PRESSURE_RESILIENCE` (5.9% importance)
8. `LATE_CLOCK_PRESSURE_APPETITE_DELTA` (5.9% importance)
9. `USG_PCT_X_CREATION_VOLUME_RATIO` (5.7% importance)
10. `USG_PCT_X_LEVERAGE_USG_DELTA` (5.7% importance)

### The Archetype System

Four archetypes based on two axes:
- **Resilience Quotient (RQ)**: Adaptability (volume × efficiency ratio)
- **Dominance Score**: Absolute value (points per 75 possessions)

| Archetype | RQ | Dominance | Example |
|-----------|----|-----------|---------|
| **King** | High | High | Jokić, Giannis |
| **Bulldozer** | Low | High | Luka, LeBron |
| **Sniper** | High | Low | Aaron Gordon |
| **Victim** | Low | Low | Ben Simmons |

### Usage-Aware Conditional Predictions

The model can predict at **any usage level**:
- "What would this player be at 19.6% usage?" → Victim
- "What would this player be at 32% usage?" → Bulldozer

This enables **latent star detection**: Identify players with high skills but low opportunity.

---

## 🛠️ Key Files

### Prediction Scripts (Updated to Use RFE Model)
- `src/nba_data/scripts/predict_conditional_archetype.py` - Main prediction function
- `src/nba_data/scripts/detect_latent_stars.py` - Latent star detection
- `src/nba_data/scripts/validate_model_behavior.py` - Model validation

### Training Scripts
- `src/nba_data/scripts/train_rfe_model.py` - Train RFE-optimized model (10 features)
- `src/nba_data/scripts/train_predictive_model.py` - Train full model (65 features)

### Test Scripts
- `test_latent_star_cases.py` - Validation test suite (16 critical cases)
- `test_rfe_model.py` - RFE model validation

### Data Files
- `results/predictive_dataset.csv` - Stress vectors (5,312 player-seasons)
- `results/resilience_archetypes.csv` - Playoff archetypes (labels)
- `results/pressure_features.csv` - Pressure vector features
- `results/trajectory_features.csv` - Trajectory features (36 features)
- `results/gate_features.csv` - Gate features (7 features)

### Model Files
- `models/resilience_xgb_rfe_10.pkl` - **CURRENT MODEL** (10 features)
- `models/resilience_xgb.pkl` - Full model (65 features, fallback)

---

## 🎯 What to Work On Next

### Priority 1: Fix Remaining Edge Cases (3 cases)

1. **Jordan Poole** (95.50%, expected <55%)
   - Problem: Playoff Volume Tax not strong enough
   - Fix: Increase tax rate to 70-80% reduction
   - File: `src/nba_data/scripts/predict_conditional_archetype.py`

2. **Mikal Bridges** (30.00%, expected ≥65%)
   - Problem: Doesn't meet Flash Multiplier (not low volume)
   - Fix: Add Leverage Vector Exemption or Pressure Resilience Exemption
   - File: `src/nba_data/scripts/predict_conditional_archetype.py`

3. **Lauri Markkanen** (60.37%, expected ≥65%)
   - Problem: Very close to threshold (only 4.63% away)
   - Fix: Consider threshold adjustment OR investigate model prediction
   - File: `test_latent_star_cases.py` (thresholds) or model investigation

### Priority 2: Validation

After each fix:
1. Run `test_latent_star_cases.py` to validate improvements
2. Check pass rate (target: 87.5-93.8%)
3. Review `results/latent_star_test_cases_report.md`

---

## 🧪 Testing

### Run Validation Test Suite
```bash
python test_latent_star_cases.py
```

**Expected Results**:
- Current: 81.2% pass rate (13/16)
- Target: 87.5-93.8% pass rate (14-15/16)

### Test RFE Model
```bash
python test_rfe_model.py
```

**Expected**: All tests pass, predictions work at different usage levels

---

## 📊 Recent Results

### RFE Model Validation (Latest)
- **Pass Rate**: 81.2% (13/16)
- **True Positives**: 87.5% (7/8)
- **False Positives**: 83.3% (5/6)

### Key Wins
- ✅ Victor Oladipo: 65.09% (PASS) - Previously failing
- ✅ Tyrese Haliburton: 70.66% (PASS) - Previously failing
- ✅ Tyrese Maxey: 89.60% (PASS) - Previously failing
- ✅ Domantas Sabonis: 30.00% (PASS) - Correctly filtered

### Remaining Failures
- ❌ Jordan Poole: 95.50% (expected <55%)
- ❌ Mikal Bridges: 30.00% (expected ≥65%)
- ❌ Lauri Markkanen: 60.37% (expected ≥65%)

---

## 💡 Key Insights for New Developers

1. **Feature Bloat is Real**: RFE analysis proved that 10 features > 65 features
2. **Usage-Aware is Core**: 5 of 10 features are usage-related (65.9% importance)
3. **Gates Work**: `NEGATIVE_SIGNAL_COUNT` ranks 3rd (10.5% importance)
4. **Trajectory Features Mostly Noise**: Only 1 of 36 made top 10
5. **The Feedback Was Right**: Simplification improved both accuracy and pass rate

**See `KEY_INSIGHTS.md` for complete list of 34+ hard-won lessons.**

---

## 🚀 Quick Start

1. **Understand the Vision**: Read `LUKA_SIMMONS_PARADOX.md`
2. **Check Current State**: Read `CURRENT_STATE.md`
3. **See What's Next**: Read `NEXT_STEPS.md`
4. **Run Tests**: `python test_latent_star_cases.py`
5. **Make Changes**: Follow priorities in `NEXT_STEPS.md`

---

## 📝 Important Notes

- **All prediction scripts use RFE model by default** (falls back to full model if not found)
- **Model file**: `models/resilience_xgb_rfe_10.pkl` (not `resilience_xgb.pkl`)
- **Test cases**: 16 critical cases in `test_latent_star_cases.py`
- **Documentation**: Always update `CURRENT_STATE.md` and `NEXT_STEPS.md` after changes

---

**Status**: Ready for next developer to continue with Phase 4.2 edge case fixes.

