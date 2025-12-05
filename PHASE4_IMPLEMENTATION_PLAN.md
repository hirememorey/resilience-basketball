# Phase 4 Implementation Plan: Multi-Season Trajectory & Gates-to-Features

**Date**: December 2025  
**Status**: ✅ **IMPLEMENTATION COMPLETE** | Phase 4.1 Refinements Complete ✅  
**Priority**: High - Addresses Core Model Limitations

## ✅ Implementation Status

**Phase 4 Core Implementation**: ✅ **COMPLETE**
- ✅ Trajectory features generator created (`generate_trajectory_features.py`)
- ✅ Gate features generator created (`generate_gate_features.py`)
- ✅ Both integrated into training pipeline
- ✅ Model retrained with 65 features (up from 38)
- ✅ Model accuracy: 63.89% (improved from 62.22%)

**Phase 4.1 Gate Refinements**: ✅ **COMPLETE**
- ✅ Conditional Abdication Tax (Smart Deference exemption)
- ✅ Flash Multiplier exemption for Bag Check Gate

**Remaining Work**: See `NEXT_STEPS.md` for Phase 4.2 priorities (Poole tax, Bridges exemption, threshold adjustments)

## Executive Summary

Phase 4 addresses two critical limitations identified in feedback:

1. **Multi-Season Trajectory Features**: Currently, the model treats Jalen Brunson (Age 22) and Jalen Brunson (Age 24) as independent entities. We need to capture **rate of improvement** (trajectory) and use **Bayesian priors** (previous season performance).

2. **Convert Gates to Features**: The model relies on 7 hard gates (if/else statements) that cap star-level at 30%. These should be converted to **soft features** that the model learns, not hard rules.

**Expected Impact**:
- Trajectory features: Capture "alpha" in rate of improvement, not just current ability
- Gates-to-features: More elegant model, potentially better generalization
- Combined: Addresses the "Sloan Winner" gap by moving from heuristic patches to learned patterns

---

## Part 1: Multi-Season Trajectory Features

### The Problem

**Current State**: Model treats each player-season as independent. Jalen Brunson (2020-21) and Jalen Brunson (2022-23) are evaluated separately with no connection.

**The Gap**: 
- **Noise**: A 22-year-old role player might have a "bad" Creation Vector because they're learning, not because they lack talent
- **Trend Invisibility**: Player A (0.4 → 0.5 → 0.6) vs. Player B (0.8 → 0.7 → 0.6) are ranked identically in Year 3, but Player A is a Latent Star
- **Missing Context**: A high Flash Multiplier at Age 21 is worth 10x more than at Age 28

### The Solution

**Keep player-seasons as rows**, but enrich with:
1. **Trajectory Features**: Year-over-year (YoY) deltas for key stress vectors
2. **Bayesian Priors**: Previous season values as features (let model learn how to weight them)
3. **Age Interactions**: Age × trajectory interactions (young players improving = stronger signal)

### Implementation Steps

#### Step 1.1: Create Trajectory Feature Generator Script

**File**: `src/nba_data/scripts/generate_trajectory_features.py`

**Purpose**: Calculate YoY deltas and previous season priors for all player-seasons.

**Key Features to Calculate**:

**Trajectory Features (YoY Deltas)**:
- `CREATION_VOLUME_RATIO_YOY_DELTA`: Change from previous season
- `CREATION_TAX_YOY_DELTA`: Change in creation efficiency
- `LEVERAGE_USG_DELTA_YOY_DELTA`: Change in clutch usage scaling
- `LEVERAGE_TS_DELTA_YOY_DELTA`: Change in clutch efficiency
- `RS_PRESSURE_RESILIENCE_YOY_DELTA`: Change in pressure shot efficiency
- `RS_PRESSURE_APPETITE_YOY_DELTA`: Change in pressure shot willingness
- `RS_RIM_APPETITE_YOY_DELTA`: Change in rim attack frequency
- `EFG_ISO_WEIGHTED_YOY_DELTA`: Change in isolation efficiency

**Bayesian Prior Features (Previous Season Values)**:
- `PREV_CREATION_VOLUME_RATIO`: Previous season's value
- `PREV_CREATION_TAX`: Previous season's value
- `PREV_LEVERAGE_USG_DELTA`: Previous season's value
- `PREV_LEVERAGE_TS_DELTA`: Previous season's value
- `PREV_RS_PRESSURE_RESILIENCE`: Previous season's value
- `PREV_RS_PRESSURE_APPETITE`: Previous season's value
- `PREV_RS_RIM_APPETITE`: Previous season's value
- `PREV_EFG_ISO_WEIGHTED`: Previous season's value

**Age-Trajectory Interactions**:
- `AGE_X_CREATION_VOLUME_RATIO_YOY_DELTA`: Age × trajectory interaction
- `AGE_X_LEVERAGE_USG_DELTA_YOY_DELTA`: Age × trajectory interaction
- `AGE_X_RS_PRESSURE_RESILIENCE_YOY_DELTA`: Age × trajectory interaction

**Implementation Logic**:

```python
def calculate_trajectory_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate YoY deltas and previous season priors for all player-seasons.
    
    Args:
        df: DataFrame with columns PLAYER_ID, SEASON, and stress vector features
        
    Returns:
        DataFrame with trajectory features added
    """
    # Sort by player and season (chronological)
    df = df.sort_values(['PLAYER_ID', 'SEASON']).copy()
    
    # For each player, calculate YoY deltas
    trajectory_features = []
    prior_features = []
    
    for player_id in df['PLAYER_ID'].unique():
        player_df = df[df['PLAYER_ID'] == player_id].copy()
        
        if len(player_df) < 2:
            # Need at least 2 seasons for trajectory
            continue
        
        # Calculate YoY deltas
        for idx in range(1, len(player_df)):
            current_season = player_df.iloc[idx]
            prev_season = player_df.iloc[idx - 1]
            
            # Calculate deltas for key features
            for feature in KEY_STRESS_VECTORS:
                current_val = current_season[feature]
                prev_val = prev_season[feature]
                
                if pd.notna(current_val) and pd.notna(prev_val):
                    delta = current_val - prev_val
                    trajectory_features.append({
                        'PLAYER_ID': player_id,
                        'SEASON': current_season['SEASON'],
                        f'{feature}_YOY_DELTA': delta,
                        f'PREV_{feature}': prev_val
                    })
    
    # Merge back into original dataframe
    trajectory_df = pd.DataFrame(trajectory_features)
    df = pd.merge(df, trajectory_df, on=['PLAYER_ID', 'SEASON'], how='left')
    
    return df
```

**Key Stress Vectors** (features to calculate trajectories for):
```python
KEY_STRESS_VECTORS = [
    'CREATION_VOLUME_RATIO',
    'CREATION_TAX',
    'LEVERAGE_USG_DELTA',
    'LEVERAGE_TS_DELTA',
    'RS_PRESSURE_RESILIENCE',
    'RS_PRESSURE_APPETITE',
    'RS_RIM_APPETITE',
    'EFG_ISO_WEIGHTED',
    'RS_LATE_CLOCK_PRESSURE_RESILIENCE',  # V4.2 feature
]
```

**Edge Cases to Handle**:
- **First Season**: No previous season → set trajectory features to NaN (expected)
- **Missing Previous Season**: If player has gap (e.g., injury), use most recent available season
- **Rookie Season**: No trajectory data (expected) - model will learn to handle this
- **Team Changes**: Keep trajectory (skills are player-level, not team-level)

#### Step 1.2: Integrate Trajectory Features into Training Pipeline

**File**: `src/nba_data/scripts/train_predictive_model.py`

**Changes**:
1. Load trajectory features before training
2. Add trajectory features to feature list
3. Handle NaN values (first seasons, rookies) appropriately

**Feature List Update**:
```python
features = [
    # ... existing features ...
    
    # NEW: Trajectory Features (YoY Deltas)
    'CREATION_VOLUME_RATIO_YOY_DELTA',
    'CREATION_TAX_YOY_DELTA',
    'LEVERAGE_USG_DELTA_YOY_DELTA',
    'LEVERAGE_TS_DELTA_YOY_DELTA',
    'RS_PRESSURE_RESILIENCE_YOY_DELTA',
    'RS_PRESSURE_APPETITE_YOY_DELTA',
    'RS_RIM_APPETITE_YOY_DELTA',
    'EFG_ISO_WEIGHTED_YOY_DELTA',
    'RS_LATE_CLOCK_PRESSURE_RESILIENCE_YOY_DELTA',
    
    # NEW: Bayesian Prior Features (Previous Season Values)
    'PREV_CREATION_VOLUME_RATIO',
    'PREV_CREATION_TAX',
    'PREV_LEVERAGE_USG_DELTA',
    'PREV_LEVERAGE_TS_DELTA',
    'PREV_RS_PRESSURE_RESILIENCE',
    'PREV_RS_PRESSURE_APPETITE',
    'PREV_RS_RIM_APPETITE',
    'PREV_EFG_ISO_WEIGHTED',
    
    # NEW: Age-Trajectory Interactions
    'AGE_X_CREATION_VOLUME_RATIO_YOY_DELTA',
    'AGE_X_LEVERAGE_USG_DELTA_YOY_DELTA',
    'AGE_X_RS_PRESSURE_RESILIENCE_YOY_DELTA',
]
```

**NaN Handling**:
- **Trajectory Features**: Fill NaN with 0 (no change = neutral signal for first seasons)
- **Prior Features**: Fill NaN with median (no prior = use population average)
- **Age Interactions**: Calculate after filling NaN (AGE × trajectory)

#### Step 1.3: Update Conditional Prediction Function

**File**: `src/nba_data/scripts/predict_conditional_archetype.py`

**Changes**:
1. Load trajectory features when initializing predictor
2. Calculate trajectory features for new predictions (if previous season data available)
3. Handle missing trajectory data gracefully (confidence flags)

**Implementation**:
```python
def prepare_features_with_trajectory(
    self, 
    player_data: pd.Series, 
    usage_level: float,
    prev_season_data: Optional[pd.Series] = None
) -> Tuple[np.ndarray, Dict]:
    """
    Prepare features including trajectory features if previous season available.
    """
    # ... existing feature preparation ...
    
    # Add trajectory features if previous season available
    if prev_season_data is not None:
        # Calculate YoY deltas
        for feature in KEY_STRESS_VECTORS:
            current_val = player_data.get(feature, None)
            prev_val = prev_season_data.get(feature, None)
            
            if pd.notna(current_val) and pd.notna(prev_val):
                delta = current_val - prev_val
                features_dict[f'{feature}_YOY_DELTA'] = delta
                features_dict[f'PREV_{feature}'] = prev_val
            else:
                features_dict[f'{feature}_YOY_DELTA'] = 0.0  # No change
                features_dict[f'PREV_{feature}'] = np.nan  # Missing prior
    
    # Calculate age-trajectory interactions
    age = player_data.get('AGE', None)
    if pd.notna(age):
        for feature in KEY_STRESS_VECTORS:
            if f'{feature}_YOY_DELTA' in features_dict:
                features_dict[f'AGE_X_{feature}_YOY_DELTA'] = age * features_dict[f'{feature}_YOY_DELTA']
    
    # ... rest of feature preparation ...
```

### Validation Strategy

**Test Cases**:
1. **Jalen Brunson (2020-21 → 2022-23)**: Should show positive trajectory → higher star-level prediction
2. **Tyrese Maxey (2020-21 → 2023-24)**: Should show steep improvement trajectory
3. **Victor Oladipo (2016-17)**: Should benefit from trajectory context (improving vs. declining)

**Success Criteria**:
- Trajectory features show non-zero feature importance (model is using them)
- Players with positive trajectories (0.4 → 0.5 → 0.6) rank higher than declining players (0.8 → 0.7 → 0.6) in Year 3
- Young players (Age < 25) with positive trajectories show higher star-level potential
- Model accuracy improves or maintains (≥ 62.22%)

---

## Part 2: Convert Gates to Features

### The Problem

**Current State**: 7 hard gates cap `star_level_potential` at 0.30:
1. Fragility Gate (RS_RIM_APPETITE < threshold)
2. Bag Check Gate (SELF_CREATED_FREQ < 10%)
3. Missing Leverage Data Penalty
4. Negative Signal Gate (Abdication Tax: LEVERAGE_USG_DELTA < -0.05)
5. Data Completeness Gate (< 67% critical features)
6. Minimum Sample Size Gate
7. (Additional gates from Phase 3.9)

**The Gap**: These are post-hoc patches. A robust ML model should learn these patterns from features, not hard rules.

### The Solution

**Convert hard gates to soft features** that the model learns:
1. **Risk Features**: Negative signals as continuous features (not binary gates)
2. **Confidence Features**: Data completeness and sample size as confidence scores
3. **Constraint Features**: Physics-of-basketball constraints as features (not hard caps)

### Implementation Steps

#### Step 2.1: Identify Gate Logic to Convert

**Gates to Convert**:

1. **Abdication Tax Gate** → `ABDICATION_RISK` feature
   - Current: `if LEVERAGE_USG_DELTA < -0.05: cap at 30%`
   - New: `ABDICATION_RISK = max(0, -LEVERAGE_USG_DELTA)` (continuous risk score)

2. **Fragility Gate** → `PHYSICALITY_FLOOR` feature
   - Current: `if RS_RIM_APPETITE < bottom_20th: cap at 30%`
   - New: `PHYSICALITY_FLOOR = RS_RIM_APPETITE` (let model learn threshold)

3. **Bag Check Gate** → `SELF_CREATED_FREQ` feature (already calculated)
   - Current: `if SELF_CREATED_FREQ < 10%: cap at 30%`
   - New: Use `SELF_CREATED_FREQ` as feature (let model learn threshold)

4. **Data Completeness Gate** → `DATA_COMPLETENESS_SCORE` feature
   - Current: `if completeness < 67%: cap at 30%`
   - New: `DATA_COMPLETENESS_SCORE = present_features / total_features` (0.0 to 1.0)

5. **Sample Size Gate** → `SAMPLE_SIZE_CONFIDENCE` feature
   - Current: `if pressure_shots < 50 or clutch_min < 15: cap at 30%`
   - New: `SAMPLE_SIZE_CONFIDENCE = min(1.0, pressure_shots/50, clutch_min/15)` (0.0 to 1.0)

6. **Missing Leverage Data** → `LEVERAGE_DATA_CONFIDENCE` feature
   - Current: `if missing leverage data: cap at 30%`
   - New: `LEVERAGE_DATA_CONFIDENCE = 1.0 if present else 0.0` (let model learn importance)

7. **Multiple Negative Signals** → `NEGATIVE_SIGNAL_COUNT` feature
   - Current: `if 2+ negative signals: cap at 30%`
   - New: `NEGATIVE_SIGNAL_COUNT = count(negative_signals)` (let model learn threshold)

#### Step 2.2: Create Gate-to-Feature Converter Script

**File**: `src/nba_data/scripts/generate_gate_features.py`

**Purpose**: Calculate soft features from gate logic (before training).

**Implementation**:

```python
def calculate_gate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert hard gate logic to soft features.
    
    Args:
        df: DataFrame with stress vector features
        
    Returns:
        DataFrame with gate features added
    """
    df = df.copy()
    
    # 1. Abdication Risk (from Negative Signal Gate)
    df['ABDICATION_RISK'] = df['LEVERAGE_USG_DELTA'].apply(
        lambda x: max(0, -x) if pd.notna(x) else 0.0
    )
    
    # 2. Physicality Floor (from Fragility Gate)
    # Already have RS_RIM_APPETITE - use as-is
    df['PHYSICALITY_FLOOR'] = df['RS_RIM_APPETITE'].fillna(0.0)
    
    # 3. Self-Created Frequency (from Bag Check Gate)
    # Calculate if not already present
    if 'SELF_CREATED_FREQ' not in df.columns:
        iso_freq = df.get('ISO_FREQUENCY', 0).fillna(0)
        pnr_freq = df.get('PNR_HANDLER_FREQUENCY', 0).fillna(0)
        df['SELF_CREATED_FREQ'] = iso_freq + pnr_freq
        # If missing, use proxy (already calculated in predict_conditional_archetype.py)
        # This should match the proxy logic
    
    # 4. Data Completeness Score
    critical_features = [
        'CREATION_VOLUME_RATIO',
        'CREATION_TAX',
        'LEVERAGE_USG_DELTA',
        'LEVERAGE_TS_DELTA',
        'RS_PRESSURE_APPETITE',
        'RS_PRESSURE_RESILIENCE',
    ]
    present_count = df[critical_features].notna().sum(axis=1)
    df['DATA_COMPLETENESS_SCORE'] = present_count / len(critical_features)
    
    # 5. Sample Size Confidence
    pressure_shots = df.get('RS_TOTAL_VOLUME', 0).fillna(0)
    clutch_min = df.get('CLUTCH_MIN_TOTAL', 0).fillna(0)
    
    pressure_confidence = (pressure_shots / 50).clip(0, 1.0)
    clutch_confidence = (clutch_min / 15).clip(0, 1.0)
    df['SAMPLE_SIZE_CONFIDENCE'] = (pressure_confidence * clutch_confidence) ** 0.5  # Geometric mean
    
    # 6. Leverage Data Confidence
    leverage_usg = df.get('LEVERAGE_USG_DELTA', None)
    leverage_ts = df.get('LEVERAGE_TS_DELTA', None)
    df['LEVERAGE_DATA_CONFIDENCE'] = (
        (leverage_usg.notna() | leverage_ts.notna()).astype(float)
    )
    
    # 7. Negative Signal Count
    negative_signals = 0
    if 'CREATION_TAX' in df.columns:
        negative_signals += (df['CREATION_TAX'] < -0.10).astype(int)
    if 'LEVERAGE_TS_DELTA' in df.columns:
        negative_signals += (df['LEVERAGE_TS_DELTA'] < -0.15).astype(int)
    df['NEGATIVE_SIGNAL_COUNT'] = negative_signals
    
    return df
```

#### Step 2.3: Update Training Pipeline

**File**: `src/nba_data/scripts/train_predictive_model.py`

**Changes**:
1. Load gate features before training
2. Add gate features to feature list
3. Remove hard gate logic from training (gates only apply in prediction for backward compatibility during transition)

**Feature List Update**:
```python
features = [
    # ... existing features ...
    # ... trajectory features ...
    
    # NEW: Gate Features (Soft Features)
    'ABDICATION_RISK',
    'PHYSICALITY_FLOOR',
    'SELF_CREATED_FREQ',
    'DATA_COMPLETENESS_SCORE',
    'SAMPLE_SIZE_CONFIDENCE',
    'LEVERAGE_DATA_CONFIDENCE',
    'NEGATIVE_SIGNAL_COUNT',
]
```

#### Step 2.4: Update Conditional Prediction Function (Gradual Migration)

**File**: `src/nba_data/scripts/predict_conditional_archetype.py`

**Strategy**: **Gradual Migration** - Keep gates as fallback, but prioritize model-learned features.

**Implementation**:
```python
def predict_archetype_at_usage(
    self, 
    player_data: pd.Series, 
    usage_level: float,
    use_gate_features: bool = True,  # NEW: Toggle gate features
    apply_hard_gates: bool = False,   # NEW: Toggle hard gates (default False)
) -> Dict:
    """
    Predict archetype with option to use gate features or hard gates.
    """
    # Calculate gate features
    if use_gate_features:
        gate_features = self._calculate_gate_features(player_data)
        # Add to feature preparation
        for feat_name, feat_value in gate_features.items():
            player_data[feat_name] = feat_value
    
    # ... existing prediction logic ...
    
    # Apply hard gates only if explicitly requested (for backward compatibility)
    if apply_hard_gates:
        # ... existing gate logic ...
        pass
    else:
        # Model should learn from gate features - no hard caps
        pass
```

**Migration Path**:
1. **Phase 4.1**: Add gate features, keep hard gates as fallback
2. **Phase 4.2**: Train model with gate features, compare performance
3. **Phase 4.3**: If gate features perform well, remove hard gates
4. **Phase 4.4**: If gate features don't capture patterns, refine features

### Validation Strategy

**Test Cases**:
1. **Ben Simmons**: Should have high `ABDICATION_RISK` → model predicts low star-level
2. **D'Angelo Russell**: Should have low `PHYSICALITY_FLOOR` → model predicts low star-level
3. **Domantas Sabonis**: Should have low `SELF_CREATED_FREQ` → model predicts low star-level
4. **Thanasis**: Should have low `DATA_COMPLETENESS_SCORE` and `SAMPLE_SIZE_CONFIDENCE` → model predicts low star-level

**Success Criteria**:
- Gate features show non-zero feature importance (model is using them)
- Model accuracy maintains or improves (≥ 62.22%)
- Hard gates become unnecessary (model learns patterns from features)
- Test cases that were fixed by gates are still correctly predicted by model

---

## Implementation Checklist

### Phase 4.1: Trajectory Features (Priority: High)

- [ ] **Step 1.1**: Create `generate_trajectory_features.py` script
  - [ ] Calculate YoY deltas for key stress vectors
  - [ ] Calculate previous season priors
  - [ ] Handle edge cases (first seasons, rookies, gaps)
  - [ ] Test on sample data (Brunson, Maxey, Oladipo)

- [ ] **Step 1.2**: Integrate trajectory features into training pipeline
  - [ ] Update `train_predictive_model.py` to load trajectory features
  - [ ] Add trajectory features to feature list
  - [ ] Handle NaN values appropriately
  - [ ] Retrain model with trajectory features

- [ ] **Step 1.3**: Update conditional prediction function
  - [ ] Add trajectory feature calculation to `predict_conditional_archetype.py`
  - [ ] Handle missing previous season data gracefully
  - [ ] Test on known cases (Brunson, Maxey)

- [ ] **Validation**: Run test suite with trajectory features
  - [ ] Verify trajectory features have non-zero importance
  - [ ] Verify players with positive trajectories rank higher
  - [ ] Verify model accuracy maintains or improves

### Phase 4.2: Gates to Features (Priority: Medium)

- [ ] **Step 2.1**: Identify gate logic to convert
  - [ ] Document all 7 gates and their logic
  - [ ] Map each gate to a soft feature

- [ ] **Step 2.2**: Create `generate_gate_features.py` script
  - [ ] Implement gate feature calculations
  - [ ] Test on sample data (Simmons, Russell, Sabonis, Thanasis)

- [ ] **Step 2.3**: Update training pipeline
  - [ ] Update `train_predictive_model.py` to load gate features
  - [ ] Add gate features to feature list
  - [ ] Retrain model with gate features

- [ ] **Step 2.4**: Update conditional prediction function (gradual migration)
  - [ ] Add `use_gate_features` parameter
  - [ ] Add `apply_hard_gates` parameter (default False)
  - [ ] Test with gate features only (no hard gates)

- [ ] **Validation**: Run test suite with gate features
  - [ ] Verify gate features have non-zero importance
  - [ ] Verify model learns patterns (no hard gates needed)
  - [ ] Verify model accuracy maintains or improves
  - [ ] Compare: gate features vs. hard gates performance

### Phase 4.3: Combined Validation

- [ ] **Full Integration**: Train model with both trajectory and gate features
- [ ] **Test Suite**: Run full validation on 16 test cases
- [ ] **Performance Comparison**:
  - Baseline (current): 68.8% pass rate
  - With trajectory: Expected 75-80% pass rate
  - With gate features: Expected 70-75% pass rate
  - Combined: Expected 80-85% pass rate

- [ ] **Feature Importance Analysis**: Verify both feature sets contribute
- [ ] **Edge Case Testing**: Test on rookies, first seasons, missing data

---

## Expected Outcomes

### Trajectory Features

**Before**: Jalen Brunson (2020-21) and Jalen Brunson (2022-23) evaluated independently  
**After**: Model sees Brunson's trajectory (improving) → higher star-level prediction

**Before**: Player A (0.4 → 0.5 → 0.6) and Player B (0.8 → 0.7 → 0.6) ranked identically in Year 3  
**After**: Player A ranks higher (positive trajectory) than Player B (declining)

**Before**: High Flash Multiplier at Age 21 treated same as Age 28  
**After**: Age × trajectory interactions capture that young players improving = stronger signal

### Gates to Features

**Before**: 7 hard gates cap star-level at 30% (post-hoc patches)  
**After**: Model learns patterns from soft features (elegant, unified model)

**Before**: "We utilize XGBoost, followed by 6 manual exception rules"  
**After**: "We utilize XGBoost with 38 features including risk and confidence scores"

**Before**: Ben Simmons needs hard gate to catch negative LEVERAGE_USG_DELTA  
**After**: Model learns that high `ABDICATION_RISK` → low star-level

---

## Key Principles

1. **Trajectory > Snapshot**: Rate of improvement matters more than current ability for young players
2. **Learn, Don't Patch**: Model should learn patterns from features, not hard rules
3. **Gradual Migration**: Keep hard gates as fallback during transition, remove once validated
4. **Feature Engineering > Model Complexity**: Better features (trajectory, gates) > more complex models

---

## Files Created/Modified

### New Files ✅ CREATED
- ✅ `src/nba_data/scripts/generate_trajectory_features.py` - Calculate YoY deltas and priors
- ✅ `src/nba_data/scripts/generate_gate_features.py` - Convert gate logic to features
- ✅ `results/trajectory_features.csv` - Generated trajectory features (36 features)
- ✅ `results/gate_features.csv` - Generated gate features (7 features)

### Modified Files ✅ UPDATED
- ✅ `src/nba_data/scripts/train_predictive_model.py` - Added trajectory and gate features
- ✅ `src/nba_data/scripts/predict_conditional_archetype.py` - Support trajectory and gate features, Phase 4.1 refinements
- ✅ `models/resilience_xgb.pkl` - Retrained model with 65 features (63.89% accuracy)

### Documentation ✅ UPDATED
- ✅ `CURRENT_STATE.md` - Updated with Phase 4 and 4.1 status
- ✅ `KEY_INSIGHTS.md` - Added Phase 4.1 insights (Smart Deference, Flash Multiplier exemption, Double-Penalization)
- ✅ `NEXT_STEPS.md` - Updated with Phase 4.2 priorities
- ✅ `README.md` - Updated status to Phase 4 complete
- ✅ `PHASE4_IMPLEMENTATION_PLAN.md` - Marked implementation complete

---

## Success Metrics

1. ✅ **Model Accuracy**: 63.89% (improved from 62.22%) - **ACHIEVED**
2. ⚠️ **Test Case Pass Rate**: 62.5% (same as baseline) - **Gates still active, need Phase 4.2 refinements**
3. ✅ **Feature Importance**: Trajectory and gate features show non-zero importance (`NEGATIVE_SIGNAL_COUNT` is #3 feature) - **ACHIEVED**
4. ⚠️ **Model Elegance**: Hard gates remain active but refined (Phase 4.1) - **PARTIAL** (Phase 4.2 "Trust Fall" experiment pending)
5. ⚠️ **Sloan Readiness**: Moving toward "Sloan Winner" candidate - **IN PROGRESS** (Phase 4.2 refinements needed)

---

**Status**: ✅ **IMPLEMENTATION COMPLETE**  
**Next Step**: See `NEXT_STEPS.md` for Phase 4.2 priorities (Poole tax, Bridges exemption, threshold adjustments)

