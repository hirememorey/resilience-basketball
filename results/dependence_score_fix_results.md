# Dependence Score Fix Results

**Date**: December 10, 2025  
**Status**: ✅ Implemented and Validated  
**Fix**: Lower usage threshold for high-dependence players

---

## Problem

**Willy Hernangomez (2016-17)**:
- DEPENDENCE_SCORE: 0.664 (very high)
- USG_PCT: 19.9% (< 25% threshold)
- Star-level: 72.4% ❌ (should be <55%)
- **Issue**: System Merchant Gate didn't apply because usage was too low

---

## Root Cause

**The Problem**: System Merchant Gate required `USG_PCT > 0.25 AND DEPENDENCE_SCORE > 0.45`, but some system-dependent players have lower usage.

**Additional Issue**: Gate was recalculating DEPENDENCE_SCORE on-the-fly (returning 0.4) instead of using stored value (0.664).

---

## Fix Implemented

### Fix 1: Lower Usage Threshold for High Dependence

**Change**: Apply System Merchant Gate to very high-dependence players even at lower usage

**Logic**:
```python
# Before: USG_PCT > 0.25 AND DEPENDENCE_SCORE > 0.45
# After: (USG_PCT > 0.25 AND DEPENDENCE_SCORE > 0.45) OR (DEPENDENCE_SCORE > 0.60)
```

**Rationale**:
- DEPENDENCE_SCORE > 0.60 is already used in Dependence Law (very high dependence)
- High dependence is a flaw regardless of usage
- Catches Hernangomez (DEP=0.664) even at 19.9% usage

### Fix 2: Use Stored DEPENDENCE_SCORE

**Change**: Use stored DEPENDENCE_SCORE from player_data if available, instead of recalculating

**Rationale**:
- On-the-fly calculation may be missing data (returns 0.4 instead of stored 0.664)
- Stored value is more reliable (calculated during feature generation)

---

## Results

### Before Fix

| Player | Season | DEP | USG | Star% | Gate Applied |
|--------|--------|-----|-----|-------|--------------|
| Willy Hernangomez | 2016-17 | 0.664 | 19.9% | 72.4% | ❌ NO |

### After Fix

| Player | Season | DEP | USG | Star% | Gate Applied |
|--------|--------|-----|-----|-------|--------------|
| Willy Hernangomez | 2016-17 | 0.664 | 19.9% | 30.0% | ✅ YES |

**Gate Message**: "System Merchant Gate applied: DEPENDENCE_SCORE=0.664 > 0.60 (very high dependence = system merchant, regardless of usage), star-level capped from 72.37% to 30.00%"

---

## Impact on All System-Dependent Cases

**Total Cases**: 10 system-dependent cases (DEPENDENCE_SCORE > 0.45)

**Cases Above 0.60**: 9 cases (very high dependence)

**Expected Impact**:
- All 9 cases with DEP > 0.60 should now be caught by System Merchant Gate
- 1 case (Jordan Poole, DEP=0.462) already caught by existing gate (USG > 25%)

---

## Validation

✅ **Hernangomez**: Fixed (72.4% → 30.0%)  
✅ **Gate Logic**: Correctly applies to very high-dependence players  
✅ **Stored Value**: Uses stored DEPENDENCE_SCORE instead of recalculating  

---

## Files Modified

1. `src/nba_data/scripts/predict_conditional_archetype.py`:
   - Modified System Merchant Gate condition (line ~2027)
   - Added logic to use stored DEPENDENCE_SCORE (line ~2015)
   - Updated logging to distinguish between usage-based and dependence-based triggers

---

## Next Steps

1. ✅ Fix implemented
2. ✅ Validated on Hernangomez case
3. ⏳ Test on all system-dependent cases
4. ⏳ Run full test suite to ensure no regressions
5. ⏳ Document in implementation summary

