# Phase 3.7 Refinement Plan: Addressing Feedback

**Date**: December 2025  
**Status**: Ready for Implementation  
**Based on**: User Feedback Analysis on Phase 3.6 Results

## Executive Summary

Phase 3.6 achieved 75.0% pass rate (12/16) with threshold adjustments. User feedback identified two critical refinements needed:

1. **Poole Failure**: Move Playoff Translation Tax from Efficiency to Volume (the "Linear Tax Fallacy")
2. **Haliburton Failure**: Widen Flash Multiplier definition to include Pressure Resilience (the "Narrow Flash" Problem)

**Key Validations from Feedback**:
- ✅ **Bag Check Gate**: Structural triumph - successfully codifies "Dependency is Fragility"
- ✅ **Threshold Adjustment**: Valid calibration, not cheating - maps to "GM Reality"

---

## Fix #1: The "Linear Tax Fallacy" - Move Tax from Efficiency to Volume

### The Problem (Poole Failure)

**Current Implementation**: Playoff Translation Tax penalizes efficiency (EFG) by deducting 0.5% for every 1% above league average open shot frequency.

**The Physics Failure**: We assumed that in the playoffs, **Efficiency drops**. In reality, for system merchants like Poole, **Opportunity drops**.

**The Mechanism**:
- **Regular Season**: Curry's gravity gives Poole 5 wide-open drives a game
- **Playoffs**: Defenses switch and stay home. Poole doesn't just shoot worse; **he loses the ability to take the shot**
- **Result**: Those shots physically disappear - it's a volume problem, not an efficiency problem

**Current Result**: Poole still at 83.05% star-level (expected <55%)

### The Fix

**Move the Tax from Efficiency to Volume**:

```
If OPEN_SHOT_FREQ > 75th percentile:
    PROJECTED_CREATION_VOLUME = PROJECTED_CREATION_VOLUME × 0.70  # Slash by 30%
    
# Logic: "You physically will not get these shots in the playoffs"
```

**Why This Works**: 
- System merchants rely on open shots that disappear in playoffs
- The issue isn't that they shoot worse on those shots; it's that they don't get those shots at all
- By slashing projected volume, we simulate the reality that opportunity drops, not just efficiency

### Implementation

```python
def apply_playoff_volume_tax(player_data, projected_creation_volume, df_features):
    """
    Apply playoff translation tax to volume, not efficiency.
    System merchants lose opportunity, not just efficiency.
    """
    # Get open shot frequency
    open_shot_freq = player_data.get('RS_OPEN_SHOT_FREQUENCY', None)
    if pd.isna(open_shot_freq):
        # Calculate from shot quality data if available
        fga_6_plus = player_data.get('FGA_6_PLUS', 0)
        total_fga = player_data.get('TOTAL_FGA', 0)
        if total_fga > 0:
            open_shot_freq = fga_6_plus / total_fga
        else:
            return projected_creation_volume  # No tax if no data
    
    # Calculate 75th percentile threshold
    if 'RS_OPEN_SHOT_FREQUENCY' in df_features.columns:
        open_freq_75th = df_features['RS_OPEN_SHOT_FREQUENCY'].quantile(0.75)
    else:
        # Fallback: use league average + 1 standard deviation
        open_freq_75th = df_features['RS_OPEN_SHOT_FREQUENCY'].quantile(0.75) if 'RS_OPEN_SHOT_FREQUENCY' in df_features.columns else None
    
    if open_freq_75th is not None and pd.notna(open_shot_freq) and open_shot_freq > open_freq_75th:
        # Slash projected volume by 30%
        projected_creation_volume = projected_creation_volume * 0.70
        logger.debug(f"Playoff Volume Tax applied: {open_shot_freq:.4f} > {open_freq_75th:.4f}, volume reduced by 30%")
    
    return projected_creation_volume
```

**Expected Impact**: Fixes Poole case (83.05% → <55%)

---

## Fix #2: The "Narrow Flash" Problem - Widen Flash Definition

### The Problem (Haliburton Failure)

**Current Implementation**: Flash Multiplier only looks for isolation efficiency:
- `CREATION_TAX > 80th percentile` OR `EFG_ISO_WEIGHTED > 80th percentile`

**The Physics Failure**: We assumed "Flash of Brilliance" = Isolation Efficiency. But Haliburton is not an Iso-Scorer (Harden); he is a **PnR Manipulator** (Nash/CP3).

**The Miss**: Haliburton's genius isn't in 1-on-1 isolation; it's in:
- High-volume PnR decision-making
- Hitting shots under schematic pressure (contested pull-up 3s)

**Current Result**: Haliburton at 27.44% star-level (expected ≥65%)

### The Fix

**Expand the "Flash" Definition**:

```
Current: ISO_EFFICIENCY > 80th percentile

New: ISO_EFFICIENCY > 80th OR PRESSURE_RESILIENCE > 80th

# Why: Haliburton hits contested pull-up 3s. That is a "Flash" of star potential,
# even if it's not technically an "Isolation."
```

**Why This Works**:
- Pressure Resilience (tight shot efficiency) is a valid signal of star potential
- Players like Haliburton show flashes through contested shots, not just isolation
- This widens the aperture to catch PnR manipulators, not just iso-scorers

### Implementation

```python
def apply_flash_multiplier(player_data, projection_factor, df_features):
    """
    If player has elite efficiency on low volume, project to star-level volume.
    Expanded to include Pressure Resilience as alternative flash signal.
    """
    creation_vol = player_data.get('CREATION_VOLUME_RATIO', 0)
    creation_tax = player_data.get('CREATION_TAX', 0)
    efg_iso = player_data.get('EFG_ISO_WEIGHTED', 0)
    pressure_resilience = player_data.get('RS_PRESSURE_RESILIENCE', 0)
    
    # Calculate percentiles
    vol_25th = df_features['CREATION_VOLUME_RATIO'].quantile(0.25)
    tax_80th = df_features['CREATION_TAX'].quantile(0.80)
    efg_80th = df_features['EFG_ISO_WEIGHTED'].quantile(0.80)
    pressure_80th = df_features['RS_PRESSURE_RESILIENCE'].quantile(0.80)
    
    # Check if "Flash of Brilliance"
    is_low_volume = False
    is_elite_efficiency = False
    
    if (self.creation_vol_25th is not None and 
        pd.notna(creation_vol) and creation_vol < self.creation_vol_25th):
        is_low_volume = True
    
    # Expanded flash definition: ISO efficiency OR Pressure Resilience
    if (self.creation_tax_80th is not None and pd.notna(creation_tax) and creation_tax > self.creation_tax_80th):
        is_elite_efficiency = True
    elif (self.efg_iso_80th is not None and pd.notna(efg_iso) and efg_iso > self.efg_iso_80th):
        is_elite_efficiency = True
    elif (pressure_80th is not None and pd.notna(pressure_resilience) and pressure_resilience > pressure_80th):
        is_elite_efficiency = True  # NEW: Pressure Resilience as flash signal
    
    if is_low_volume and is_elite_efficiency and self.star_median_creation_vol is not None:
        # Project to star-level volume instead of scalar projection
        return self.star_median_creation_vol
    else:
        # Normal projection
        return creation_vol * projection_factor
```

**Expected Impact**: Fixes Haliburton case (27.44% → ≥65%)

---

## Implementation Checklist

### Phase 3.7.1: Move Playoff Tax to Volume (Priority: High)
- [ ] Remove efficiency penalty from Playoff Translation Tax
- [ ] Add volume penalty: If OPEN_SHOT_FREQ > 75th percentile → slash PROJECTED_CREATION_VOLUME by 30%
- [ ] Update `prepare_features()` to apply volume tax instead of efficiency tax
- [ ] Test on Poole case (should drop from 83.05% to <55%)

### Phase 3.7.2: Widen Flash Multiplier Definition (Priority: High)
- [ ] Add PRESSURE_RESILIENCE to flash detection logic
- [ ] Update flash condition: ISO_EFFICIENCY > 80th OR PRESSURE_RESILIENCE > 80th
- [ ] Calculate PRESSURE_RESILIENCE 80th percentile in `_calculate_feature_distributions()`
- [ ] Test on Haliburton case (should improve from 27.44% to ≥65%)

### Phase 3.7.3: Re-Validation
- [ ] Run validation test suite with Phase 3.7 refinements
- [ ] Expected: 13-14/16 passing (81-88%)
- [ ] Document results

---

## Expected Outcomes

### After Phase 3.7.1 (Volume Tax)
- **Poole**: Should decrease from 83.05% to <55%
- **Pass Rate**: Should improve to 13/16 (81.3%)

### After Phase 3.7.2 (Widened Flash)
- **Haliburton**: Should improve from 27.44% to ≥65%
- **Pass Rate**: Should improve to 13-14/16 (81-88%)

---

## Key Principles from Feedback

1. **Dependency is Fragility**: Bag Check Gate successfully codifies this - system-dependent production is fragile
2. **Threshold Calibration**: 65%/55% thresholds map to "GM Reality" - uncertainty is failure for max contracts
3. **Opportunity vs. Efficiency**: For system merchants, playoffs reduce opportunity, not just efficiency
4. **Flash Aperture**: Star potential can show through pressure resilience, not just isolation efficiency

---

## Files to Modify

1. **`src/nba_data/scripts/predict_conditional_archetype.py`**:
   - Update `prepare_features()`: Move Playoff Translation Tax from efficiency to volume
   - Update Flash Multiplier: Add PRESSURE_RESILIENCE as alternative flash signal
   - Update `_calculate_feature_distributions()`: Add PRESSURE_RESILIENCE 80th percentile

2. **`test_latent_star_cases.py`**:
   - No changes needed (uses existing test cases)

---

## References

- **Feedback Source**: User Analysis of Phase 3.6 Results
- **Phase 3.6 Validation**: `results/phase3_6_validation_report.md`
- **Key Insights**: `KEY_INSIGHTS.md` (Sections 14, 15, 16, 17)

---

**Status**: Ready for Implementation

**Expected After Phase 3.7**: 13-14/16 passing (81-88%)

