# False Positive Analysis: Small Sample Size Noise

**Date**: December 4, 2025  
**Issue**: Players with no business being ranked highly are appearing at the top of predictions

## Problematic Players

1. **Thanasis Antetokounmpo (2015-16)** - Ranked #2 (83.75%)
2. **KZ Okpala (2019-20)** - Ranked #3 (77.60%)
3. **Trevon Scott (2021-22)** - Ranked #5 (77.50%)
4. **Isaiah Mobley (2022-23)** - Ranked #7 (74.45%)
5. **Jahlil Okafor (multiple seasons)** - Ranked #11-14 (63-67%)
6. **Ben Simmons (2018-19)** - Ranked #13 (63.55%) - "Simmons Paradox" case

## Root Causes

### 1. Small Sample Size Noise (Critical)

**Problem**: Players with tiny sample sizes are getting perfect or near-perfect efficiency scores.

**Examples**:
- **KZ Okpala (2019-20)**: CREATION_TAX = 1.0 (100%), CREATION_VOLUME_RATIO = 0.667 (67%)
  - Usage: 10.2% (very low)
  - Likely: 1-2 isolation shots made = perfect efficiency
  - Missing leverage data (no clutch minutes)
  
- **Trevon Scott (2021-22)**: CREATION_TAX = 1.0 (100%), CREATION_VOLUME_RATIO = 0.5 (50%)
  - Usage: 20.7%
  - Likely: Tiny sample size creating perfect score
  
- **Thanasis Antetokounmpo (2015-16)**: CREATION_TAX = 0.5 (50%), CREATION_VOLUME_RATIO = 0.333 (33%)
  - Usage: 28.6% (but likely very few games/minutes)
  - RS_PRESSURE_RESILIENCE = 1.0 (100% - perfect!)
  - Missing leverage data

**Fix Required**: Add minimum sample size thresholds for creation metrics:
- Minimum isolation attempts (e.g., 20-30 attempts)
- Minimum 3+ dribble shots (e.g., 15-20 attempts)
- Flag players with insufficient sample sizes

### 2. Missing Leverage Data Not Penalized

**Problem**: Many false positives have missing LEVERAGE_USG_DELTA and LEVERAGE_TS_DELTA, but this isn't being penalized.

**Examples**:
- Thanasis: Missing leverage data
- KZ Okpala: Missing leverage data
- Trevon Scott: Missing leverage data
- Isaiah Mobley: Missing leverage data

**Current Behavior**: Missing leverage data is filled with NaN, but model may treat it as neutral.

**Fix Required**: 
- Penalize missing leverage data (it's a critical signal - LEVERAGE_USG_DELTA is #1 predictor)
- Require minimum clutch minutes (currently 15 minutes threshold exists, but may not be enforced in predictions)
- Add "data completeness gate" that caps star-level for players with missing critical features

### 3. Pressure Appetite Overvaluation

**Problem**: High pressure appetite alone is driving predictions, even when other signals are negative.

**Example - Jahlil Okafor (2019-20)**:
- RS_PRESSURE_APPETITE: 0.822 (82% - very high)
- CREATION_TAX: -0.204 (negative - inefficient)
- LEVERAGE_TS_DELTA: -0.387 (negative - declines in clutch)
- LEVERAGE_USG_DELTA: -0.059 (negative - doesn't scale up)

**Fix Required**: 
- Pressure appetite alone shouldn't be enough
- Need to check for negative signals in other vectors
- Add "negative signal gate" that penalizes players with multiple negative signals

### 4. Ben Simmons - The "Simmons Paradox" Case

**Problem**: Ben Simmons (2018-19) is ranked #13 (63.55%) despite being the exact "Simmons Paradox" case.

**His Profile**:
- CREATION_VOLUME_RATIO: 0.650 (65% - high)
- CREATION_TAX: -0.147 (negative - inefficient)
- LEVERAGE_USG_DELTA: -0.067 (negative - doesn't scale up in clutch)
- LEVERAGE_TS_DELTA: 0.007 (essentially neutral)
- RS_PRESSURE_APPETITE: 0.788 (79% - high)
- RS_RIM_APPETITE: 0.660 (66% - high)

**Why He's Ranked High**: 
- High creation volume + high pressure appetite + high rim appetite
- Model is seeing "volume" and "pressure appetite" as positive signals
- But missing that he's inefficient (negative creation tax) and doesn't scale up (negative leverage USG delta)

**Fix Required**: 
- Negative LEVERAGE_USG_DELTA should be a hard filter (as per KEY_INSIGHTS.md #10: "The Abdication Detector")
- Players with negative leverage USG delta should be capped at low star-level
- This is the exact "Simmons Paradox" - passivity is failure

## Recommended Fixes

### Fix #1: Minimum Sample Size Gate (Priority: High)

Add minimum sample size requirements for creation metrics:

```python
# In predict_conditional_archetype.py
def check_minimum_sample_sizes(player_data):
    """
    Check if player has sufficient sample sizes for reliable metrics.
    Returns: (passed, reasons)
    """
    failures = []
    
    # Check creation volume (need minimum isolation attempts)
    # If CREATION_VOLUME_RATIO is high but based on <20 attempts, flag as unreliable
    iso_attempts = player_data.get('ISO_FGA', 0)  # Need to add this to dataset
    if iso_attempts < 20:
        failures.append(f"Insufficient isolation attempts ({iso_attempts} < 20)")
    
    # Check pressure resilience (already has 50 shot threshold in qualified players)
    # But need to check individual player's sample size
    pressure_shots = player_data.get('RS_TOTAL_VOLUME', 0)
    if pressure_shots < 50:
        failures.append(f"Insufficient pressure shots ({pressure_shots} < 50)")
    
    # Check leverage data (need minimum clutch minutes)
    clutch_min = player_data.get('CLUTCH_MIN_TOTAL', 0)
    if clutch_min < 15:
        failures.append(f"Insufficient clutch minutes ({clutch_min} < 15)")
    
    passed = len(failures) == 0
    return passed, failures
```

**Action**: Cap star-level at 30% (Sniper ceiling) if minimum sample sizes not met.

### Fix #2: Missing Leverage Data Penalty (Priority: High)

Penalize players with missing leverage data:

```python
# In predict_conditional_archetype.py
def apply_leverage_data_penalty(player_data, star_level_potential):
    """
    Penalize players with missing leverage data.
    LEVERAGE_USG_DELTA is the #1 predictor - missing it is a critical gap.
    """
    leverage_usg = player_data.get('LEVERAGE_USG_DELTA', None)
    leverage_ts = player_data.get('LEVERAGE_TS_DELTA', None)
    clutch_min = player_data.get('CLUTCH_MIN_TOTAL', 0)
    
    # If missing leverage data or insufficient clutch minutes, penalize
    if pd.isna(leverage_usg) or pd.isna(leverage_ts) or clutch_min < 15:
        # Cap at 30% (Sniper ceiling) - can't be a star without leverage data
        star_level_potential = min(star_level_potential, 0.30)
        logger.debug(f"Leverage data penalty applied: missing or insufficient clutch minutes")
    
    return star_level_potential
```

### Fix #3: Negative Signal Gate (Priority: High)

Add gate for players with multiple negative signals:

```python
# In predict_conditional_archetype.py
def apply_negative_signal_gate(player_data, star_level_potential):
    """
    Penalize players with multiple negative signals.
    """
    creation_tax = player_data.get('CREATION_TAX', 0)
    leverage_usg_delta = player_data.get('LEVERAGE_USG_DELTA', 0)
    leverage_ts_delta = player_data.get('LEVERAGE_TS_DELTA', 0)
    
    negative_signals = 0
    
    # Negative creation tax (inefficient)
    if pd.notna(creation_tax) and creation_tax < -0.10:
        negative_signals += 1
    
    # Negative leverage USG delta (doesn't scale up - "Abdication Tax")
    if pd.notna(leverage_usg_delta) and leverage_usg_delta < -0.05:
        negative_signals += 1
        # This is the "Simmons Paradox" - hard filter
        star_level_potential = min(star_level_potential, 0.30)
        logger.debug(f"Abdication Tax detected: LEVERAGE_USG_DELTA = {leverage_usg_delta}")
    
    # Negative leverage TS delta (declines in clutch)
    if pd.notna(leverage_ts_delta) and leverage_ts_delta < -0.15:
        negative_signals += 1
    
    # If 2+ negative signals, cap at 30%
    if negative_signals >= 2:
        star_level_potential = min(star_level_potential, 0.30)
        logger.debug(f"Multiple negative signals detected ({negative_signals}), capping at 30%")
    
    return star_level_potential
```

### Fix #4: Data Completeness Gate (Priority: Medium)

Add overall data completeness check:

```python
# In predict_conditional_archetype.py
def check_data_completeness(player_data):
    """
    Check if player has sufficient data completeness for reliable prediction.
    """
    critical_features = [
        'CREATION_VOLUME_RATIO',
        'CREATION_TAX',
        'LEVERAGE_USG_DELTA',
        'LEVERAGE_TS_DELTA',
        'RS_PRESSURE_APPETITE',
        'RS_PRESSURE_RESILIENCE',
    ]
    
    present_features = sum(1 for f in critical_features if pd.notna(player_data.get(f, None)))
    completeness = present_features / len(critical_features)
    
    # Require at least 4 of 6 critical features (67% completeness)
    if completeness < 0.67:
        return False, completeness
    
    return True, completeness
```

## Implementation Priority

1. **Fix #2 (Missing Leverage Data Penalty)** - Highest priority
   - LEVERAGE_USG_DELTA is #1 predictor
   - Missing it should be a hard filter
   - Will catch most false positives

2. **Fix #3 (Negative Signal Gate)** - High priority
   - Will catch Ben Simmons case
   - Enforces "Abdication Tax" principle

3. **Fix #1 (Minimum Sample Size Gate)** - High priority
   - Will catch small sample size noise
   - Need to add ISO_FGA to dataset first

4. **Fix #4 (Data Completeness Gate)** - Medium priority
   - Overall quality check
   - Can be added after other fixes

## Expected Impact

After implementing these fixes:
- **Thanasis, KZ Okpala, Trevon Scott**: Should be filtered by minimum sample size or missing leverage data
- **Jahlil Okafor**: Should be filtered by negative signal gate (negative creation tax + negative leverage delta)
- **Ben Simmons**: Should be filtered by negative leverage USG delta (Abdication Tax)
- **Isaiah Mobley**: Should be filtered by missing leverage data

**Expected Pass Rate**: Should improve from current false positives to correctly identifying only legitimate latent stars.

