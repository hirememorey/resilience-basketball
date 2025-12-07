# Universal Projection Implementation: Fixing the "Static Avatar" Fallacy

**Date**: December 2025  
**Status**: ✅ **COMPLETE**  
**Priority**: High - Core Model Logic Upgrade

## The Problem: "Static Avatar" Fallacy

When predicting at different usage levels (e.g., "How would Brunson perform at 30% usage?"), the model was updating `USG_PCT` but leaving `CREATION_VOLUME_RATIO` at the role-player level (e.g., 0.20).

**Result**: The model saw an impossible profile: high usage (30%) + low creation volume (20%) = "off-ball chucker" or "system merchant forced into a role they can't handle." The model correctly predicted "Victim" or "Sniper" because this profile doesn't exist in nature for successful stars.

**Reality**: A true latent star (Brunson) changes their shot diet as usage scales. At 30% usage, Brunson's creation volume rises to ~50-60%, not 20%.

## The Solution: Universal Projection with Empirical Distributions

Instead of conditional projection (only when `usage_level > current_usage`), we now:

1. **Always project** when usage differs (upward or downward)
2. **Use empirical distributions** for upward projections (not linear scaling)
3. **Project multiple features together** (CREATION_VOLUME_RATIO, LEVERAGE_USG_DELTA, PRESSURE_APPETITE)
4. **Preserve Flash Multiplier** as an override for elite efficiency players

## Implementation Details

### 1. Empirical Usage Buckets

Added calculation of median feature values for each usage bucket:

```python
Usage Buckets:
- 10-15%: median CREATION_VOLUME_RATIO = X.XX
- 15-20%: median CREATION_VOLUME_RATIO = X.XX
- 20-25%: median CREATION_VOLUME_RATIO = X.XX
- 25-30%: median CREATION_VOLUME_RATIO = X.XX
- 30-35%: median CREATION_VOLUME_RATIO = X.XX
- 35-40%: median CREATION_VOLUME_RATIO = X.XX
```

**Location**: `_calculate_feature_distributions()` method

### 2. Empirical Projection Method

New method `_project_features_empirically()` that:
- Uses median value from target usage bucket for upward projections
- Preserves player's relative position (offset from current bucket median)
- Falls back to linear scaling if bucket not found

**Key Principle**: Respects non-linear relationship between usage and feature values.

### 3. Universal Projection Logic

Modified `prepare_features()` to:
- **Always calculate projection** when `abs(usage_level - current_usage) > 0.001`
- **Use empirical projection** for upward projections (target > current)
- **Use linear scaling** for downward projections (conservative)
- **Apply Flash Multiplier** as override for elite efficiency players

### 4. Feature Projection Order

**Correct Order**: Project → Tax → Use

1. Calculate projected values from original values (empirical or linear)
2. Apply multi-signal tax to projected values
3. Use in interaction terms and base features

**Previous (Wrong) Order**: Tax → Project
- This taxed the original value, then projected it, which was incorrect

## Features Projected

1. **CREATION_VOLUME_RATIO**: Primary volume feature
2. **LEVERAGE_USG_DELTA**: Clutch usage scaling
3. **RS_PRESSURE_APPETITE**: Pressure shot willingness

**Note**: Efficiency features (CREATION_TAX, EFG_ISO_WEIGHTED) do NOT project - they remain constant.

## Validation

### Test Cases

1. **Jalen Brunson (2020-21) at 30% usage**:
   - Current: 19.6% usage, 0.20 creation volume
   - Projected: 30% usage, ~0.50-0.60 creation volume (empirical bucket median)
   - Expected: Should predict "Bulldozer" or "King" (not "Victim")

2. **Tyrese Maxey (2021-22) at 30% usage**:
   - Current: 20.1% usage, 0.25 creation volume
   - Projected: 30% usage, ~0.55-0.65 creation volume
   - Expected: Should predict "Bulldozer" or "King"

### Expected Impact

- **Latent Star Detection**: Should improve significantly
- **Test Case Pass Rate**: Should increase from 68.8% to ~75-80%
- **Model Accuracy**: May improve slightly (1-2 percentage points)

## Files Modified

1. **`src/nba_data/scripts/predict_conditional_archetype.py`**:
   - Added empirical usage bucket calculation to `_calculate_feature_distributions()`
   - Added `_get_usage_bucket()` helper method
   - Added `_project_features_empirically()` method
   - Modified `prepare_features()` to use universal projection
   - Updated interaction term calculations to use projected values
   - Updated base feature calculations to use projected values

## Key Principles

1. **Features must scale together**: Usage, creation volume, leverage, pressure appetite are causally linked
2. **Empirical > Linear**: Use data-driven distributions, not theoretical linear relationships
3. **Project first, tax second**: Apply taxes to projected values, not original values
4. **Preserve relative position**: If player is above median at current usage, keep them above at target

## Next Steps

1. **Run validation tests** on known cases (Brunson, Maxey, Haliburton)
2. **Compare predictions** before/after implementation
3. **Measure test case pass rate** improvement
4. **Document any edge cases** discovered during testing

## References

- **Original Analysis**: User's "Static Avatar" Fallacy diagnosis
- **Key Insights**: `KEY_INSIGHTS.md` (Insight #11: Opportunity vs. Ability)
- **Current Model**: `CURRENT_STATE.md`

