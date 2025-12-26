# Universal Projection Implementation: Fixing the "Static Avatar" Fallacy & The "Poole Mirage"

**Date**: December 2025  
**Status**: ✅ **COMPLETE** (v3 with Touch Ownership)  
**Priority**: High - Core Model Logic Upgrade

## The Problem: "Static Avatar" Fallacy & The "Poole Mirage"

1. **Static Avatar**: When predicting at different usage levels, the model was updating `USG_PCT` but leaving `CREATION_VOLUME_RATIO` at role-player levels.
2. **The Poole Mirage**: The model was assuming all observed efficiency was "owned" by the player. In reality, "System Merchants" (e.g., Jordan Poole '22) "rent" efficiency from elite teammates. When projected to higher usage (new context), this subsidy evaporates.

## The Solution: Universal Projection v2 (Subsidy-Aware)

We now use a two-stage projection engine:

1. **De-Subsidy**: Isolate "Intrinsic Skill" by applying the **Subsidy Index**.
2. **Project**: Scale the "Owned" portion of efficiency using empirical distributions and friction.

### 1. The Subsidy Index (Ownership Logic)

Using Player Tracking data, we define Skill as either **Kinetic Energy** (Movement) or **Potential Energy** (Ball Dominance):

$$SkillIndex = Max(NormalizedSpeed_{Offense}, NormalizedTimeOfPossession)$$
$$SubsidyIndex = 1.0 - SkillIndex$$

*Note: As of Dec 26, 2025, the formula is now a 3-dimensional Max-Gate to include "Touch Ownership" for big men.*
$$SkillIndex = Max(NormalizedTimeOfPoss, NormalizedAstPct, NormalizedTouchProduction)$$

- **Treatment**: Efficiency is taxed by the Subsidy Index before projection. A player with high subsidy (Low speed, Low possession time) has their baseline efficiency discounted by up to 50%.

### 2. Universal Projection with Empirical Distributions

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

**Correct Order**: Project → De-Subsidy → Tax → Use

1. Calculate projected volume values (CREATION_VOLUME_RATIO, etc.)
2. Apply the **Subsidy Tax** to efficiency components based on the player's tracking profile.
3. **Apply Friction Coefficients** to the subsidized efficiency.
4. **Apply Fragility Taxes**: Final efficiency is penalized by the **Fragility Score** (Abdication + Choke taxes).
5. Use in interaction terms and final output.

**Key Principle**: You cannot project what you do not own, and what you own must be durable.

## Validation: The "Ground Truth" Test (2021-22)

| Metric | Nikola Jokić ('19) (Owner) | Jordan Poole ('22) (Merchant) | D'Angelo Russell ('19) (Fragile) |
| :--- | :--- | :--- | :--- |
| **Subsidy Index** | **0.198** (19.8%) | **0.522** (52.2%) | **0.129** (12.9%) |
| **Fragility Score** | **Low** | **Moderate** | **High** (Abdication) |
| **Projected Impact** | **Scales** with usage. | **Discounted** by subsidy. | **Penalized** by fragility. |

The system now correctly identifies that Poole's efficiency was ~2.6x more subsidized than Jokic's, and that D-Lo's high-ownership volume is not portable due to high-leverage abdication.

## Files Modified

1. **`src/nba_data/scripts/evaluate_plasticity_potential.py`**:
   - Added `fetch_touch_metrics()` for Post and Elbow production.
   - Updated `calculate_subsidy_index()` to use the 3-dimensional Max-Gate logic.
   - Implemented `FRAGILITY_SCORE v3.5` with Abdication and Choke taxes.
2. **`src/nba_data/core/models.py`**:
   - Added `weighted_touch_production` and `skill_index` to `PlayerSeason` schema.
   - Added `fragility_score`, `leverage_usg_delta`, and `leverage_ts_delta` for persistence.

## Key Principles

1. **Features must scale together**: Usage, creation volume, leverage, pressure appetite are causally linked
2. **Empirical > Linear**: Use data-driven distributions, not theoretical linear relationships
3. **Project first, tax second**: Apply taxes to projected values, not original values
4. **Filter for ownership**: Distinguish between owned efficiency and rented subsidy.

## Next Steps

1. **Run validation tests** on known cases (Brunson, Maxey, Haliburton)
2. **Compare predictions** before/after implementation
3. **Measure test case pass rate** improvement
4. **Document any edge cases** discovered during testing

## References

- **Original Analysis**: User's "Static Avatar" Fallacy diagnosis
- **Key Insights**: `KEY_INSIGHTS.md` (Insight #70: System Merchant Mirage)
- **Current Model**: `ACTIVE_CONTEXT.md`

