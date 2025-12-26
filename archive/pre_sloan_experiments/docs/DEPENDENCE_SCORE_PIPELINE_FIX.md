# DEPENDENCE_SCORE Data Pipeline Fix

**Date**: December 10, 2025  
**Status**: ✅ **FIXED**

---

## Problem

DEPENDENCE_SCORE coverage was 0% (0/5,312 rows, 0/3,067 training rows). This was a **critical data pipeline bug** that prevented the model from learning about "System Merchants."

**Root Cause**: The `calculate_dependence_scores_batch()` function requires `RS_OPEN_SHOT_FREQUENCY` from pressure features, but pressure features were not merged into `final_df` before calculating dependence scores in `evaluate_plasticity_potential.py`.

---

## Solution

### 1. Merge Pressure Features Before Calculation

**File**: `src/nba_data/scripts/evaluate_plasticity_potential.py`

**Change**: Added code to load and merge pressure features (specifically `RS_OPEN_SHOT_FREQUENCY`) before calling `calculate_dependence_scores_batch()`.

```python
# PHASE 1 FIX: Merge pressure features before calculating Dependence Scores
logger.info("Loading pressure features for Dependence Score calculation...")
pressure_path = self.results_dir / "pressure_features.csv"
if pressure_path.exists():
    df_pressure = pd.read_csv(pressure_path)
    # Merge pressure features (need RS_OPEN_SHOT_FREQUENCY for dependence calculation)
    final_df = pd.merge(
        final_df,
        df_pressure[['PLAYER_ID', 'SEASON', 'RS_OPEN_SHOT_FREQUENCY']],
        on=['PLAYER_ID', 'SEASON'],
        how='left'
    )
```

### 2. Fix Merge Column Conflicts

**File**: `src/nba_data/scripts/calculate_dependence_score.py`

**Change**: Drop existing NaN columns before merging to avoid duplicate column suffixes (`_x`, `_y`).

```python
# Drop existing dependence score columns if they exist (they may be NaN from previous failed attempts)
cols_to_drop = ['DEPENDENCE_SCORE', 'ASSISTED_FGM_PCT', 'OPEN_SHOT_FREQUENCY', 'SELF_CREATED_USAGE_RATIO']
for col in cols_to_drop:
    if col in df.columns:
        df = df.drop(columns=[col])
```

### 3. Clean Up Exception Handler

**File**: `src/nba_data/scripts/evaluate_plasticity_potential.py`

**Change**: Drop existing NaN columns before calculation, not after exception.

```python
# Drop any existing NaN columns from previous failed attempts (they'll be recalculated)
cols_to_drop = ['DEPENDENCE_SCORE', 'ASSISTED_FGM_PCT', 'OPEN_SHOT_FREQUENCY', 'SELF_CREATED_USAGE_RATIO']
for col in cols_to_drop:
    if col in final_df.columns:
        final_df = final_df.drop(columns=[col])
```

---

## Test Results

**Before Fix**: 0% coverage (0/5,312 rows)

**After Fix** (tested on 100 rows):
- DEPENDENCE_SCORE: 96/100 (96% coverage)
- ASSISTED_FGM_PCT: 100/100 (100% coverage - using fallbacks)
- OPEN_SHOT_FREQUENCY: 96/100 (96% coverage - matches RS_OPEN_SHOT_FREQUENCY)
- SELF_CREATED_USAGE_RATIO: 100/100 (100% coverage - using ISO/PNR or CREATION_VOLUME_RATIO fallbacks)

**Sample Results**:
- Klay Thompson (2015-16): DEPENDENCE_SCORE=0.616 (high dependence - system player)
- Anthony Davis (2015-16): DEPENDENCE_SCORE=0.614 (high dependence - rim finisher)
- Al Horford (2015-16): DEPENDENCE_SCORE=0.758 (very high dependence - system player)

---

## Why Coverage Isn't 100%

The 96% coverage for DEPENDENCE_SCORE and OPEN_SHOT_FREQUENCY is due to:
1. **Missing pressure features**: Some player-seasons don't have pressure features (4,473/5,312 = 84% coverage in pressure_features.csv)
2. **Missing RS_OPEN_SHOT_FREQUENCY**: Required for dependence calculation

The 100% coverage for ASSISTED_FGM_PCT and SELF_CREATED_USAGE_RATIO is because:
1. **ASSISTED_FGM_PCT**: Has multiple fallbacks (catch-shoot → pull-up+drive → CREATION_VOLUME_RATIO)
2. **SELF_CREATED_USAGE_RATIO**: Has fallbacks (ISO/PNR → CREATION_VOLUME_RATIO)

---

## Next Steps

1. ✅ **Fix implemented** - Code changes complete
2. ⏳ **Regenerate predictive_dataset.csv** - Run `evaluate_plasticity_potential.py` to regenerate with populated dependence scores
3. ⏳ **Verify coverage** - Check that DEPENDENCE_SCORE is populated for all training data (2015-2020)
4. ⏳ **Retrain model** - Model can now learn about System Merchants if DEPENDENCE_SCORE is in feature set

---

## Impact

This fix enables:
1. **Model can learn about System Merchants** - DEPENDENCE_SCORE is now available as a training feature
2. **Portable Features can work** - PORTABLE_USG_PCT requires DEPENDENCE_SCORE
3. **System Merchant Gate can use data-driven thresholds** - No longer need to calculate at inference time

**Critical for Project Sloan**: This was the #1 blocker identified in the feedback - "DEPENDENCE_SCORE is missing for key players during the feature generation phase."
