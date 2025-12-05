# Phase 4.2 Multi-Signal Tax Implementation Plan

**Date**: December 2025  
**Status**: 🎯 Ready for Implementation  
**Based on**: First Principles Analysis + Developer Lessons Learned

---

## Executive Summary

**Goal**: Implement Multi-Signal Tax to fix Jordan Poole case (95.50% → <55%)

**Key Insight from Lessons**: The "Hydra" problem - system merchants have fake volume AND fake efficiency. We must tax both, and we must tax base features BEFORE calculating interaction terms.

**Test Usage Level**: 30% (not 25%) - this is what the test suite uses for Poole

---

## Step-by-Step Implementation Plan

### Phase 0: Pre-Implementation Discovery (15 minutes)

**Before writing ANY code**, understand the model architecture:

#### 0.1: Inspect RFE Model Features

**Action**: Load the model and identify:
- Which features are **base features** (e.g., `CREATION_VOLUME_RATIO`, `EFG_ISO_WEIGHTED`)
- Which features are **interaction terms** (e.g., `USG_PCT_X_CREATION_VOLUME_RATIO`, `USG_PCT_X_EFG_ISO_WEIGHTED`)
- Feature importance ranking (from RFE analysis)

**Expected Findings**:
- Top 10 RFE features:
  1. `USG_PCT` (28.9% importance)
  2. `USG_PCT_X_EFG_ISO_WEIGHTED` (18.7% importance) ← **THE LEAK**
  3. `NEGATIVE_SIGNAL_COUNT` (10.5% importance)
  4. `EFG_PCT_0_DRIBBLE` (6.8% importance)
  5. `LEVERAGE_USG_DELTA` (6.1% importance)
  6. `USG_PCT_X_RS_PRESSURE_APPETITE` (5.9% importance)
  7. `PREV_RS_PRESSURE_RESILIENCE` (5.9% importance)
  8. `LATE_CLOCK_PRESSURE_APPETITE_DELTA` (5.9% importance)
  9. `USG_PCT_X_CREATION_VOLUME_RATIO` (5.7% importance) ← What we initially thought
  10. `USG_PCT_X_LEVERAGE_USG_DELTA` (5.7% importance)

**Key Insight**: `USG_PCT_X_EFG_ISO_WEIGHTED` (18.7%) is the leak, not `USG_PCT_X_CREATION_VOLUME_RATIO` (5.7%)

#### 0.2: Identify Base Features That Need Taxing

**Action**: Map interaction terms to their base features:

- `USG_PCT_X_CREATION_VOLUME_RATIO` → Base: `CREATION_VOLUME_RATIO`
- `USG_PCT_X_EFG_ISO_WEIGHTED` → Base: `EFG_ISO_WEIGHTED` ← **CRITICAL LEAK**
- `USG_PCT_X_LEVERAGE_USG_DELTA` → Base: `LEVERAGE_USG_DELTA`
- `USG_PCT_X_RS_PRESSURE_APPETITE` → Base: `RS_PRESSURE_APPETITE`

**Key Insight**: We must tax `EFG_ISO_WEIGHTED` (the base), not just `CREATION_VOLUME_RATIO`

#### 0.3: Understand Current Tax Implementation

**Action**: Review current code in `prepare_features()`:
- Where is the current tax applied? (Line ~615: only to `CREATION_VOLUME_RATIO`)
- When is it applied? (After projection, before interaction calculation)
- What's the tax rate? (50% reduction)

**Key Insight**: Current tax only addresses volume, not efficiency. The efficiency leak (`EFG_ISO_WEIGHTED`) is untouched.

---

### Phase 1: Design the Multi-Signal Tax System (20 minutes)

#### 1.1: Define System Merchant Signals

**From First Principles Analysis**, system merchants show:

1. **Open Shot Dependency** (Tax #1): `RS_OPEN_SHOT_FREQUENCY > 75th percentile`
2. **Creation Efficiency Collapse** (Tax #2): `CREATION_TAX < 0` (efficiency drops when creating)
3. **Leverage Abdication** (Tax #3): `LEVERAGE_USG_DELTA < 0 AND LEVERAGE_TS_DELTA < 0`
4. **Pressure Avoidance** (Tax #4): `RS_PRESSURE_APPETITE < 40th percentile`

**Tax Rates**:
- Tax #1 (Open Shot): 50% reduction (current)
- Tax #2 (Creation Efficiency): 20% additional reduction
- Tax #3 (Leverage Abdication): 20% additional reduction
- Tax #4 (Pressure Avoidance): 20% additional reduction

**Maximum Penalty**: 50% × 80% × 80% × 80% = **74.4% reduction** (for all 4 signals)

#### 1.2: Define Exemption Logic

**Principle**: True stars have at least ONE positive signal. System merchants have ALL negative signals.

**Exemption Conditions** (if ANY is true, exempt from all taxes):
- `LEVERAGE_USG_DELTA > 0` (scales up in clutch) OR
- `LEVERAGE_TS_DELTA > 0` (maintains efficiency in clutch) OR
- `CREATION_TAX > 0` (maintains efficiency when creating)

**Key Insight**: Jokić has negative CREATION_TAX but positive LEVERAGE_USG_DELTA → Exempt

#### 1.3: Identify Features to Tax

**Volume Features** (taxed with volume penalty):
- `CREATION_VOLUME_RATIO` (base for `USG_PCT_X_CREATION_VOLUME_RATIO`)
- `RS_PRESSURE_APPETITE` (base for `USG_PCT_X_RS_PRESSURE_APPETITE`)
- `LEVERAGE_USG_DELTA` (base for `USG_PCT_X_LEVERAGE_USG_DELTA`)

**Efficiency Features** (taxed with same penalty - THE FIX):
- `EFG_ISO_WEIGHTED` (base for `USG_PCT_X_EFG_ISO_WEIGHTED`) ← **CRITICAL LEAK**
- `CREATION_TAX` (if negative, already penalized, but may need additional tax)
- `RS_PRESSURE_RESILIENCE` (if pressure appetite is low)

**Key Insight**: Efficiency is just as fake as volume for system merchants. Tax both.

---

### Phase 2: Implementation Architecture (30 minutes)

#### 2.1: Tax Calculation Order

**Critical Order** (must be exact):
1. **Check Exemption** → If exempt, skip all taxes
2. **Calculate Tax Penalty** → Based on system merchant signals
3. **Tax Base Features** → Apply penalty to base features (volume AND efficiency)
4. **Apply Projection** → Project volume features to target usage
5. **Calculate Interactions** → Use taxed base features in interaction terms

**Key Principle**: Tax → Project → Interaction (not Project → Tax → Interaction)

#### 2.2: Tax Calculation Logic

**Pseudocode**:
```python
# Step 1: Check exemption
has_positive_leverage = (LEVERAGE_USG_DELTA > 0) or (LEVERAGE_TS_DELTA > 0)
has_positive_creation = CREATION_TAX > 0
is_exempt = has_positive_leverage or has_positive_creation

if is_exempt:
    volume_penalty = 1.0  # No tax
    efficiency_penalty = 1.0  # No tax
else:
    # Step 2: Calculate tax penalty
    volume_penalty = 1.0
    efficiency_penalty = 1.0
    
    # Tax #1: Open Shot Dependency
    if open_shot_freq > open_freq_75th:
        volume_penalty *= 0.50  # 50% reduction
        efficiency_penalty *= 0.50  # 50% reduction (THE FIX)
    
    # Tax #2: Creation Efficiency Collapse
    if CREATION_TAX < 0:
        volume_penalty *= 0.80  # Additional 20% reduction
        efficiency_penalty *= 0.80  # Additional 20% reduction
    
    # Tax #3: Leverage Abdication
    if LEVERAGE_USG_DELTA < 0 and LEVERAGE_TS_DELTA < 0:
        volume_penalty *= 0.80  # Additional 20% reduction
        efficiency_penalty *= 0.80  # Additional 20% reduction
    
    # Tax #4: Pressure Avoidance
    if RS_PRESSURE_APPETITE < pressure_app_40th:
        volume_penalty *= 0.80  # Additional 20% reduction
        efficiency_penalty *= 0.80  # Additional 20% reduction
```

#### 2.3: Feature Application Logic

**Where to Apply Taxes** (in `prepare_features()` method):

**Before Projection** (tax base features first):
```python
# Get base feature values
creation_vol_base = player_data.get('CREATION_VOLUME_RATIO', 0)
efg_iso_base = player_data.get('EFG_ISO_WEIGHTED', 0)
pressure_app_base = player_data.get('RS_PRESSURE_APPETITE', 0)
leverage_usg_base = player_data.get('LEVERAGE_USG_DELTA', 0)

# Apply taxes to base features
taxed_creation_vol = creation_vol_base * volume_penalty
taxed_efg_iso = efg_iso_base * efficiency_penalty  # ← THE FIX
taxed_pressure_app = pressure_app_base * volume_penalty
taxed_leverage_usg = leverage_usg_base * volume_penalty
```

**After Projection** (project taxed volume features):
```python
# Project volume features (if usage > current usage)
if use_projection:
    projected_creation_vol = taxed_creation_vol * projection_factor
    projected_pressure_app = taxed_pressure_app * projection_factor
    projected_leverage_usg = taxed_leverage_usg * projection_factor
else:
    projected_creation_vol = taxed_creation_vol
    projected_pressure_app = taxed_pressure_app
    projected_leverage_usg = taxed_leverage_usg
```

**In Interaction Calculation** (use taxed/projected values):
```python
# When calculating interaction terms
if feature_name == 'USG_PCT_X_CREATION_VOLUME_RATIO':
    features.append(usage_level * projected_creation_vol)  # Use taxed + projected
    
elif feature_name == 'USG_PCT_X_EFG_ISO_WEIGHTED':
    features.append(usage_level * taxed_efg_iso)  # Use taxed efficiency ← THE FIX
    
elif feature_name == 'USG_PCT_X_RS_PRESSURE_APPETITE':
    features.append(usage_level * projected_pressure_app)  # Use taxed + projected
    
elif feature_name == 'USG_PCT_X_LEVERAGE_USG_DELTA':
    features.append(usage_level * projected_leverage_usg)  # Use taxed + projected
```

---

### Phase 3: Implementation Details (45 minutes)

#### 3.1: Location in Code

**File**: `src/nba_data/scripts/predict_conditional_archetype.py`

**Method**: `prepare_features()` (starts at line 407)

**Insertion Point**: After calculating `playoff_volume_tax_applied` (line ~542), before the feature loop (line 544)

#### 3.2: Calculate Percentile Thresholds

**Add to `_calculate_feature_distributions()` method** (around line 320):

```python
# Calculate 40th percentile for pressure appetite (Tax #4 threshold)
if 'RS_PRESSURE_APPETITE' in self.df_features.columns:
    if 'USG_PCT' in self.df_features.columns:
        star_players = self.df_features[self.df_features['USG_PCT'] > 0.20]
        star_pressure_app = star_players['RS_PRESSURE_APPETITE'].dropna()
        if len(star_pressure_app) > 0:
            self.pressure_app_40th = star_pressure_app.quantile(0.40)
            logger.info(f"RS_PRESSURE_APPETITE 40th percentile (STARS, USG > 20%): {self.pressure_app_40th:.4f}")
```

#### 3.3: Multi-Signal Tax Calculation

**Insert before feature loop** (after line 542):

```python
# ========== PHASE 4.2: Multi-Signal Tax System ==========
# Calculate system merchant tax penalty based on multiple signals

# Step 1: Check exemption (true stars have positive signals)
leverage_usg_delta = player_data.get('LEVERAGE_USG_DELTA', 0)
leverage_ts_delta = player_data.get('LEVERAGE_TS_DELTA', 0)
creation_tax = player_data.get('CREATION_TAX', 0)

has_positive_leverage = (
    (pd.notna(leverage_usg_delta) and leverage_usg_delta > 0) or
    (pd.notna(leverage_ts_delta) and leverage_ts_delta > 0)
)
has_positive_creation = pd.notna(creation_tax) and creation_tax > 0
is_exempt = has_positive_leverage or has_positive_creation

# Step 2: Calculate tax penalty (if not exempt)
volume_penalty = 1.0
efficiency_penalty = 1.0
tax_applied_flags = []

if not is_exempt and apply_phase3_fixes:
    # Tax #1: Open Shot Dependency
    if playoff_volume_tax_applied:  # Already calculated above
        volume_penalty *= 0.50
        efficiency_penalty *= 0.50  # ← THE FIX: Tax efficiency too
        tax_applied_flags.append("Open Shot Tax")
    
    # Tax #2: Creation Efficiency Collapse
    if pd.notna(creation_tax) and creation_tax < 0:
        volume_penalty *= 0.80
        efficiency_penalty *= 0.80
        tax_applied_flags.append("Creation Efficiency Tax")
    
    # Tax #3: Leverage Abdication
    if (pd.notna(leverage_usg_delta) and leverage_usg_delta < 0 and
        pd.notna(leverage_ts_delta) and leverage_ts_delta < 0):
        volume_penalty *= 0.80
        efficiency_penalty *= 0.80
        tax_applied_flags.append("Leverage Abdication Tax")
    
    # Tax #4: Pressure Avoidance
    pressure_appetite = player_data.get('RS_PRESSURE_APPETITE', None)
    if (pd.notna(pressure_appetite) and 
        self.pressure_app_40th is not None and 
        pressure_appetite < self.pressure_app_40th):
        volume_penalty *= 0.80
        efficiency_penalty *= 0.80
        tax_applied_flags.append("Pressure Avoidance Tax")
    
    if tax_applied_flags:
        logger.debug(f"Multi-Signal Tax applied: {tax_applied_flags}, "
                    f"Volume Penalty: {volume_penalty:.4f}, Efficiency Penalty: {efficiency_penalty:.4f}")
else:
    if is_exempt:
        logger.debug("Player exempt from Multi-Signal Tax (has positive signals)")

# Store penalties for use in feature loop
multi_signal_volume_penalty = volume_penalty
multi_signal_efficiency_penalty = efficiency_penalty
# ========== END PHASE 4.2 ==========
```

#### 3.4: Apply Taxes in Feature Loop

**Modify feature loop** (starting at line 544):

**For Base Features** (before projection):
```python
# Get base feature values (before projection)
if feature_name == 'CREATION_VOLUME_RATIO':
    val = player_data.get('CREATION_VOLUME_RATIO', 0)
    if pd.isna(val):
        val = 0.0
    # Apply multi-signal tax BEFORE projection
    val = val * multi_signal_volume_penalty
    # Store for later use in interaction calculation
    taxed_creation_vol = val
    
elif feature_name == 'EFG_ISO_WEIGHTED':
    val = player_data.get('EFG_ISO_WEIGHTED', 0)
    if pd.isna(val):
        val = 0.0
    # Apply multi-signal tax (THE FIX)
    val = val * multi_signal_efficiency_penalty
    # Store for later use in interaction calculation
    taxed_efg_iso = val
    
elif feature_name == 'RS_PRESSURE_APPETITE':
    val = player_data.get('RS_PRESSURE_APPETITE', 0)
    if pd.isna(val):
        val = 0.0
    # Apply multi-signal tax BEFORE projection
    val = val * multi_signal_volume_penalty
    # Store for later use in interaction calculation
    taxed_pressure_app = val
    
elif feature_name == 'LEVERAGE_USG_DELTA':
    val = player_data.get('LEVERAGE_USG_DELTA', 0)
    if pd.isna(val):
        val = 0.0
    # Apply multi-signal tax BEFORE projection
    val = val * multi_signal_volume_penalty
    # Store for later use in interaction calculation
    taxed_leverage_usg = val
```

**For Interaction Terms** (use taxed values):
```python
elif feature_name.startswith('USG_PCT_X_'):
    base_feature = feature_name.replace('USG_PCT_X_', '')
    
    # Use pre-taxed values for interactions
    if base_feature == 'CREATION_VOLUME_RATIO':
        # Use taxed + projected value
        if use_projection:
            base_value = taxed_creation_vol * projection_factor
        else:
            base_value = taxed_creation_vol
        features.append(usage_level * base_value)
        
    elif base_feature == 'EFG_ISO_WEIGHTED':
        # Use taxed efficiency value (THE FIX)
        base_value = taxed_efg_iso
        features.append(usage_level * base_value)
        
    elif base_feature == 'RS_PRESSURE_APPETITE':
        # Use taxed + projected value
        if use_projection:
            base_value = taxed_pressure_app * projection_factor
        else:
            base_value = taxed_pressure_app
        features.append(usage_level * base_value)
        
    elif base_feature == 'LEVERAGE_USG_DELTA':
        # Use taxed + projected value
        if use_projection:
            base_value = taxed_leverage_usg * projection_factor
        else:
            base_value = taxed_leverage_usg
        features.append(usage_level * base_value)
        
    else:
        # Fallback: use original logic for other interactions
        if base_feature in player_data.index:
            base_value = player_data[base_feature]
            if pd.isna(base_value):
                features.append(0.0)
            else:
                features.append(usage_level * base_value)
        else:
            features.append(0.0)
```

---

### Phase 4: Testing Strategy (30 minutes)

#### 4.1: Test on True Stars FIRST

**Before testing on Poole**, verify we don't break true stars:

```python
# Test on known true stars
true_stars = [
    ("Nikola Jokić", "2022-23", 0.30),
    ("Giannis Antetokounmpo", "2020-21", 0.30),
    ("LeBron James", "2019-20", 0.30)
]

for name, season, usage in true_stars:
    player_data = predictor.get_player_data(name, season)
    if player_data is not None:
        pred = predictor.predict_archetype_at_usage(player_data, usage)
        star_level = pred['star_level_potential']
        assert star_level > 0.50, f"{name} incorrectly penalized! Star-level: {star_level:.2%}"
        print(f"✅ {name} ({season}): {star_level:.2%} (exempted correctly)")
```

**Expected**: All true stars should be exempt (have positive signals) and maintain high star-level

#### 4.2: Test on Poole at Correct Usage Level

**Critical**: Test at 30% usage (not 25%) - this is what the test suite uses:

```python
# Test Poole at 30% usage (test suite usage level)
poole_data = predictor.get_player_data("Jordan Poole", "2021-22")
if poole_data is not None:
    pred = predictor.predict_archetype_at_usage(poole_data, 0.30)  # ← 30%, not 25%!
    star_level = pred['star_level_potential']
    print(f"Poole (2021-22) at 30% usage: {star_level:.2%}")
    print(f"Expected: <55%")
    print(f"Tax flags: {pred.get('phase3_metadata', {}).get('tax_applied_flags', [])}")
    
    assert star_level < 0.55, f"Poole still too high! Star-level: {star_level:.2%}"
```

**Expected**: Poole should be <55% star-level with all 4 taxes applied

#### 4.3: Test on Other System Merchants

**Test on other false positives**:
- Sabonis (2021-22) - Should be filtered
- Other system merchants from test suite

#### 4.4: Run Full Test Suite

**Run the complete test suite**:
```bash
python test_latent_star_cases.py
```

**Expected**: Pass rate should improve from 81.2% (13/16) to 87.5-93.8% (14-15/16)

---

### Phase 5: Debugging Checklist

**When the tax isn't working**, check in order:

1. ✅ **Is the tax being calculated?** 
   - Check `tax_applied_flags` in metadata
   - Check `volume_penalty < 1.0` and `efficiency_penalty < 1.0`

2. ✅ **Is the exemption logic working?**
   - Check if true stars are exempted (should have positive signals)
   - Check if Poole is NOT exempted (should have all negative signals)

3. ✅ **Are taxes applied to base features?**
   - Check if `taxed_creation_vol`, `taxed_efg_iso` are calculated
   - Check if they're different from original values

4. ✅ **Are taxed values used in interactions?**
   - Check if `USG_PCT_X_EFG_ISO_WEIGHTED` uses `taxed_efg_iso`
   - Check if interaction values are lower than expected

5. ✅ **Is the test usage level correct?**
   - Check test suite: Poole uses 30% usage, not 25%
   - Test at the same usage level as test suite

6. ✅ **Are there other high-importance features?**
   - Check feature importance: `USG_PCT_X_EFG_ISO_WEIGHTED` (18.7%) is the leak
   - Make sure we're taxing the right features

7. ✅ **Is the order correct?**
   - Tax → Project → Interaction (not Project → Tax → Interaction)
   - Check that taxes are applied before projection

---

## Expected Outcomes

### Poole Prediction

**Before**:
- Star-Level: 95.50% (expected <55%)
- Tax Applied: 50% volume reduction only
- Result: Still too high

**After**:
- Star-Level: Expected <55% ✅
- Tax Applied: 74.4% reduction (all 4 signals)
- Volume Penalty: 0.256 (50% × 80% × 80% × 80%)
- Efficiency Penalty: 0.256 (same)
- `CREATION_VOLUME_RATIO`: 0.4806 → 0.1230
- `EFG_ISO_WEIGHTED`: 0.5368 → 0.1374 ← **THE FIX**
- `USG_PCT_X_EFG_ISO_WEIGHTED`: 0.30 × 0.1374 = 0.0412 (vs. 0.161 before)

### Test Suite Results

**Before**: 81.2% pass rate (13/16)
**After**: Expected 87.5-93.8% pass rate (14-15/16)

**Key Wins**:
- ✅ Poole: 95.50% → <55% (PASS)
- ✅ True stars: Maintain high star-level (exempted correctly)
- ✅ Other system merchants: Filtered correctly

---

## Key Principles

1. **Tax Base Features, Not Interactions**: Interactions are calculated from taxed bases
2. **Tax Efficiency AND Volume**: System merchants have fake efficiency too (the "Hydra" problem)
3. **Exemption Logic is Critical**: True stars have positive signals somewhere
4. **Test on True Stars FIRST**: Don't break what works
5. **Test at Test Suite Usage Levels**: Match test conditions exactly
6. **Feature Importance Shows Leaks**: Highest importance features are the leaks
7. **Order Matters**: Tax → Project → Interaction (not Project → Tax → Interaction)

---

## Implementation Checklist

- [ ] Phase 0: Pre-Implementation Discovery
  - [ ] Inspect RFE model features and importance
  - [ ] Identify base features vs. interaction terms
  - [ ] Understand current tax implementation

- [ ] Phase 1: Design Multi-Signal Tax System
  - [ ] Define system merchant signals
  - [ ] Define exemption logic
  - [ ] Identify features to tax (volume AND efficiency)

- [ ] Phase 2: Implementation Architecture
  - [ ] Design tax calculation order
  - [ ] Design feature application logic
  - [ ] Plan code insertion points

- [ ] Phase 3: Implementation
  - [ ] Add percentile threshold calculation
  - [ ] Add multi-signal tax calculation
  - [ ] Modify feature loop to apply taxes
  - [ ] Modify interaction calculation to use taxed values

- [ ] Phase 4: Testing
  - [ ] Test on true stars FIRST
  - [ ] Test on Poole at 30% usage
  - [ ] Test on other system merchants
  - [ ] Run full test suite

- [ ] Phase 5: Validation
  - [ ] Verify Poole <55% star-level
  - [ ] Verify true stars maintain high star-level
  - [ ] Verify test suite pass rate improved

---

**Status**: Ready for implementation. Follow this plan step-by-step to avoid the pitfalls identified in lessons learned.

