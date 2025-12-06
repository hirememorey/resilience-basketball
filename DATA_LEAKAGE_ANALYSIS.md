# Data Leakage Analysis: Temporal and Future Data Risks

**Date**: December 2025  
**Status**: ⚠️ **CRITICAL ISSUES IDENTIFIED**

---

## Executive Summary

**Yes, there are significant risks of data leakage in your model.** The model uses **playoff data in features** to predict playoff outcomes, which creates a circular dependency. Additionally, the train/test split is **random rather than temporal**, which could allow future data to inform past predictions.

---

## Critical Issue #1: Playoff Data in Features (Data Leakage)

### The Problem

Several features use **playoff data** to predict playoff archetypes. This is data leakage because you cannot know playoff performance before predicting it.

### Features That Use Playoff Data

#### 1. **Delta Features** (Playoff - Regular Season)
These features calculate the **change** from regular season to playoffs:

- `PRESSURE_APPETITE_DELTA` = `PO_PRESSURE_APPETITE - RS_PRESSURE_APPETITE`
- `PRESSURE_RESILIENCE_DELTA` = `PO_PRESSURE_RESILIENCE - RS_PRESSURE_RESILIENCE`
- `LATE_CLOCK_PRESSURE_APPETITE_DELTA` = `PO_LATE_CLOCK_PRESSURE_APPETITE - RS_LATE_CLOCK_PRESSURE_APPETITE`
- `EARLY_CLOCK_PRESSURE_APPETITE_DELTA` = `PO_EARLY_CLOCK_PRESSURE_APPETITE - RS_EARLY_CLOCK_PRESSURE_APPETITE`
- `LATE_CLOCK_PRESSURE_RESILIENCE_DELTA` = `PO_LATE_CLOCK_PRESSURE_RESILIENCE - RS_LATE_CLOCK_PRESSURE_RESILIENCE`
- `EARLY_CLOCK_PRESSURE_RESILIENCE_DELTA` = `PO_EARLY_CLOCK_PRESSURE_RESILIENCE - RS_EARLY_CLOCK_PRESSURE_RESILIENCE`

**Location**: `src/nba_data/scripts/calculate_shot_difficulty_features.py` (lines 194-195, 219-223)

#### 2. **Resilience Ratio Features** (Playoff / Regular Season)
These features calculate the **ratio** of playoff to regular season performance:

- `RIM_PRESSURE_RESILIENCE` = `PO_RIM_APPETITE / RS_RIM_APPETITE`
- `FTr_RESILIENCE` = `PO_FTr / RS_FTr`

**Location**: 
- `src/nba_data/scripts/calculate_rim_pressure.py` (line 104)
- `src/nba_data/scripts/calculate_physicality_features.py` (line 121)

#### 3. **Playoff-Only Features**
- `PO_EFG_BEYOND_RS_MEDIAN` - Uses playoff EFG% directly

**Location**: `src/nba_data/scripts/train_predictive_model.py` (line 259)

### Why This Is Data Leakage

**The Goal**: Predict playoff archetypes from **regular season data only**.

**The Reality**: Features include playoff performance, creating a circular dependency:
1. Model uses playoff data in features
2. Model predicts playoff archetypes (which are based on playoff performance)
3. Model appears accurate because it's using the answer to predict the answer

**Example**: 
- If `RIM_PRESSURE_RESILIENCE = 1.2`, this means the player increased rim pressure in playoffs
- But you can't know this **before** the playoffs happen
- Using this feature means you're using future information

### Impact on Model Performance

The model's **63.33% accuracy** may be inflated because:
- Features contain information about playoff outcomes
- The model is learning patterns that include playoff data
- In production, these features won't be available (you can't know playoff performance before predicting it)

---

## Critical Issue #2: Random Train/Test Split (Temporal Leakage)

### The Problem

The train/test split uses **random sampling** instead of **temporal splitting**:

```python
# Current Implementation (WRONG for time series)
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)
```

**Location**: 
- `src/nba_data/scripts/train_predictive_model.py` (line 394)
- `src/nba_data/scripts/train_rfe_model.py` (line 277)

### Why This Is Temporal Leakage

**The Scenario**:
- Training set might include 2023-24 data
- Test set might include 2015-16 data
- Model learns patterns from future seasons to predict past seasons

**The Problem**:
- NBA playstyles evolve over time (pace, 3-point shooting, etc.)
- Features calculated in 2023 might use different methodologies than 2015
- Model might learn "future" patterns that don't apply to past seasons

### What Should Happen

**Temporal Split**: Train on earlier seasons, test on later seasons:
- Train: 2015-2020 (5 seasons)
- Test: 2021-2024 (4 seasons)

Or use **walk-forward validation**:
- Train on 2015-2018, test on 2019
- Train on 2015-2019, test on 2020
- Train on 2015-2020, test on 2021
- etc.

---

## Issue #3: Trajectory Features (Potentially OK)

### The Feature

**YoY Delta Features**: `CREATION_VOLUME_RATIO_YOY_DELTA`, `LEVERAGE_USG_DELTA_YOY_DELTA`, etc.

**How They're Calculated**:
```python
# From generate_trajectory_features.py
for idx in range(1, len(player_df)):
    current_season = player_df.iloc[idx]
    prev_season = player_df.iloc[idx - 1]
    delta = current_season[feature] - prev_season[feature]
```

### Analysis

**✅ This is OK** because:
- Uses **previous season** data (past) to predict **current season** (future)
- No future data is used
- This is legitimate feature engineering

**⚠️ But be careful**:
- If you're predicting 2020-21 playoffs, you can use 2019-20 regular season data
- But you **cannot** use 2020-21 regular season data if you're predicting 2020-21 playoffs (that's the same season)

**Current Implementation**: Appears correct - uses previous season only.

---

## Issue #4: Label Generation (This is OK)

### The Labels

**Archetype Labels** are generated from playoff performance:
- `resilience_quotient` = `(PO_vol / RS_vol) * (PO_eff / RS_eff)`
- `dominance_score` = `PO_PTS per 75 possessions`

**Location**: `src/nba_data/scripts/calculate_simple_resilience.py`

### Analysis

**✅ This is OK** because:
- Labels are the **ground truth** (what actually happened)
- You're trying to **predict** these labels from regular season features
- Using playoff data for labels is correct - you want to predict what happened

**The Problem**: Not with labels, but with **features** that also use playoff data.

---

## Recommended Fixes

### Fix #1: Remove Playoff Data from Features

**Remove these features**:
- `PRESSURE_APPETITE_DELTA`
- `PRESSURE_RESILIENCE_DELTA`
- `LATE_CLOCK_PRESSURE_APPETITE_DELTA`
- `EARLY_CLOCK_PRESSURE_APPETITE_DELTA`
- `LATE_CLOCK_PRESSURE_RESILIENCE_DELTA`
- `EARLY_CLOCK_PRESSURE_RESILIENCE_DELTA`
- `RIM_PRESSURE_RESILIENCE`
- `FTr_RESILIENCE`
- `PO_EFG_BEYOND_RS_MEDIAN`

**Keep these features** (they only use regular season data):
- `RS_PRESSURE_APPETITE` ✅
- `RS_PRESSURE_RESILIENCE` ✅
- `RS_LATE_CLOCK_PRESSURE_APPETITE` ✅
- `RS_RIM_APPETITE` ✅
- `RS_FTr` ✅

**Rationale**: You can only use **regular season** data to predict playoffs. The model should learn patterns from RS features alone.

### Fix #2: Implement Temporal Train/Test Split

**Replace random split with temporal split**:

```python
# NEW: Temporal Split
# Sort by season
df = df.sort_values('SEASON')

# Split at 80% point (2015-2020 train, 2021-2024 test)
split_season = '2020-21'
train_mask = df['SEASON'] <= split_season
test_mask = df['SEASON'] > split_season

X_train = X[train_mask]
X_test = X[test_mask]
y_train = y_encoded[train_mask]
y_test = y_encoded[test_mask]
```

**Or use walk-forward validation** for more robust evaluation.

### Fix #3: Validate on True Future Data

**Test on 2024-25 season** (or most recent season not in training):
- Train on 2015-2023
- Test on 2024
- This is the true test of predictive power

---

## Impact Assessment

### Current Model Performance (May Be Inflated)

- **Reported Accuracy**: 63.33%
- **True Accuracy** (after fixes): Likely 50-55% (estimate)
- **Reason**: Removing playoff features will reduce signal, but increase validity

### What You'll Lose

- Delta features provide strong signal (they directly measure playoff change)
- But they're not available in production (can't know playoffs before they happen)

### What You'll Gain

- **Valid predictions**: Model can actually be used in production
- **True predictive power**: Measures ability to predict from RS data alone
- **Scientific rigor**: Model learns patterns that generalize, not memorize

---

## Validation Strategy

### Step 1: Remove Playoff Features
1. Remove all `*_DELTA` features that use playoff data
2. Remove all `*_RESILIENCE` ratio features
3. Keep only `RS_*` features

### Step 2: Retrain Model
1. Retrain with RS-only features
2. Use temporal split (train on 2015-2020, test on 2021-2024)
3. Measure true accuracy

### Step 3: Compare Performance
- **Before**: 63.33% accuracy (with leakage)
- **After**: True accuracy (without leakage)
- **Gap**: Measures how much leakage was inflating performance

### Step 4: Feature Engineering
- If accuracy drops significantly, engineer new RS-only features
- Example: `RS_PRESSURE_APPETITE` might predict `PRESSURE_RESILIENCE_DELTA`
- But you must learn this from **historical data**, not current season

---

## Key Principles

1. **Features must be available at prediction time**
   - If predicting 2024-25 playoffs, you can only use 2024-25 regular season data
   - Cannot use 2024-25 playoff data (doesn't exist yet)

2. **Temporal order matters**
   - Train on past, test on future
   - Never use future data to predict past

3. **Labels can use future data**
   - Labels are ground truth (what happened)
   - But features cannot use future data

4. **Trajectory features are OK**
   - Using previous season data is legitimate
   - But must be careful about same-season leakage

---

## Files to Modify

1. **`src/nba_data/scripts/train_predictive_model.py`**
   - Remove playoff features from feature list
   - Implement temporal split

2. **`src/nba_data/scripts/train_rfe_model.py`**
   - Remove playoff features from RFE selection
   - Implement temporal split

3. **`src/nba_data/scripts/calculate_shot_difficulty_features.py`**
   - Document that delta features are for analysis only, not prediction
   - Or remove them from feature generation

4. **`src/nba_data/scripts/calculate_rim_pressure.py`**
   - Document that `RIM_PRESSURE_RESILIENCE` is for analysis only
   - Keep `RS_RIM_APPETITE` for prediction

---

## Conclusion

**Yes, your model has data leakage.** The most critical issues are:

1. **Playoff data in features** (delta and resilience features)
2. **Random train/test split** (should be temporal)

**Recommended Action**: 
1. Remove all playoff-based features
2. Implement temporal train/test split
3. Retrain and measure true accuracy
4. Accept that accuracy may drop (but validity will increase)

**The Good News**: Your model architecture is sound. The issue is feature selection, not model design. Fixing this will make your model production-ready and scientifically valid.

---

**Status**: ⚠️ **REQUIRES IMMEDIATE ATTENTION**

**Next Steps**: 
1. Review this analysis
2. Decide which features to remove
3. Implement temporal split
4. Retrain and validate

