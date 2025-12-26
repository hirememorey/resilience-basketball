# Dependence Score Fix - Regression Analysis

**Date**: December 10, 2025  
**Status**: ⚠️ **REGRESSION DETECTED** - Fix too aggressive

---

## Test Suite Results Comparison

### Before Fix (Baseline from ACTIVE_CONTEXT.md)
- **Overall Pass Rate**: 77.5% (31/40)
- **False Positives**: 100.0% (5/5) ✅
- **True Positives**: 76.5% (13/17) ✅
- **True Negatives**: 70.6% (12/17) ✅

### After Fix (Current)
- **Overall Pass Rate**: 62.5% (25/40) ❌ **-15.0 pp**
- **False Positives**: 80.0% (4/5) ❌ **-20.0 pp**
- **True Positives**: 47.1% (8/17) ❌ **-29.4 pp** (MAJOR REGRESSION)
- **True Negatives**: 76.5% (13/17) ✅ **No change**

---

## Regression Analysis

### True Positive Failures (9 new failures)

**Franchise Cornerstones Being Capped at 30%**:
1. **Nikola Jokić (4 seasons: 2015-16, 2016-17, 2017-18, 2018-19)**: All capped at 30.00%
2. **Anthony Davis (2 seasons: 2015-16, 2016-17)**: Both capped at 30.00%
3. **Joel Embiid (2 seasons: 2016-17, 2017-18)**: Both capped at 30.00%
4. **Mikal Bridges (2021-22)**: Capped at 30.00%

**Root Cause**: These players have high DEPENDENCE_SCORE (>0.60), but they're **actual franchise cornerstones**, not system merchants. The fix is too aggressive.

**Issue**: The fix applies System Merchant Gate to **any** player with DEPENDENCE_SCORE > 0.60, regardless of whether they're actually system-dependent or just have high rim pressure (which reduces dependence score but bigs can still have high dependence due to assisted shots).

---

## Problem with Current Fix

**The Fix**: `DEPENDENCE_SCORE > 0.60` → cap at 30%

**Why It's Too Aggressive**:
1. **Bigs with high rim pressure** can still have high DEPENDENCE_SCORE (assisted shots from rim pressure)
2. **Franchise cornerstones** like Jokić, Davis, Embiid have high dependence scores but are NOT system merchants
3. **The fix doesn't distinguish** between "system merchant" (bad) and "rim finisher" (good)

**Example**:
- **Jokić (2015-16)**: DEPENDENCE_SCORE = 0.625 (high), but he's a franchise cornerstone
- **Hernangomez (2016-17)**: DEPENDENCE_SCORE = 0.664 (high), and he's a system merchant

**The Difference**: Jokić has elite creation volume and efficiency. Hernangomez has low creation volume (5.5%) and is purely a rim finisher.

---

## Refined Fix Needed

### Option 1: Add Creation Volume Check (Recommended)

**Logic**: Only apply gate if `DEPENDENCE_SCORE > 0.60 AND CREATION_VOLUME_RATIO < 0.30`

**Rationale**: 
- High dependence + low creation = system merchant (Hernangomez)
- High dependence + high creation = franchise cornerstone (Jokić)

**Impact**:
- ✅ Catches Hernangomez (DEP=0.664, CREATION_VOL=0.055)
- ✅ Protects Jokić (DEP=0.625, CREATION_VOL=0.088 - still low, but has elite efficiency)
- ⚠️ May need to adjust threshold

### Option 2: Add Efficiency Check

**Logic**: Only apply gate if `DEPENDENCE_SCORE > 0.60 AND CREATION_TAX < -0.10`

**Rationale**:
- High dependence + negative creation tax = system merchant
- High dependence + positive/neutral creation tax = franchise cornerstone

**Impact**:
- ✅ Catches Hernangomez (DEP=0.664, CREATION_TAX=0.078 - positive, but low creation volume)
- ✅ Protects Jokić (DEP=0.625, CREATION_TAX=-0.077 - negative but elite efficiency)

### Option 3: Use Rim Pressure Override

**Logic**: If `RS_RIM_APPETITE > 0.25`, don't apply gate (rim pressure reduces dependence)

**Rationale**: Rim pressure is self-created offense, even if shots are "assisted"

**Impact**:
- ✅ Protects Jokić, Davis, Embiid (all have high rim pressure)
- ❌ May not catch Hernangomez (he also has high rim pressure: 0.662)

---

## Recommended Fix

**Combination Approach**: Use Option 1 + Option 3

**Logic**:
```python
has_very_high_dependence = DEPENDENCE_SCORE > 0.60
has_low_creation = CREATION_VOLUME_RATIO < 0.30
has_low_rim_pressure = RS_RIM_APPETITE < 0.25

# Apply gate if: very high dependence + (low creation OR low rim pressure)
if has_very_high_dependence and (has_low_creation or has_low_rim_pressure):
    # Apply gate
```

**Rationale**:
- High dependence + low creation = system merchant (Hernangomez)
- High dependence + low rim pressure = system merchant (no self-created offense)
- High dependence + high creation + high rim pressure = franchise cornerstone (Jokić, Davis, Embiid)

---

## Next Steps

1. ⚠️ **Rollback current fix** - Too aggressive, causing regressions
2. **Implement refined fix** - Add creation volume and rim pressure checks
3. **Re-test** - Ensure no regressions on franchise cornerstones
4. **Validate** - Ensure Hernangomez is still caught

