# Phase 0 Summary: Problem Space Mapping

**Date**: December 10, 2025  
**Status**: ✅ Complete  
**Purpose**: Map the problem space before implementing fixes

---

## Step 0.1: Test Suite Structure

**Total Cases**: 40 test cases

**Categories**:
- **True Positives**: 16 cases (40%)
  - Latent Star: 6 cases
  - Franchise Cornerstone: 8 cases
  - Rookie Sensation: 1 case
  - Usage Shock: 1 case
- **False Positives**: 5 cases (12.5%)
  - Mirage Breakout: 2 cases (Poole, Horton-Tucker)
  - Empty Calories: 2 cases (Wood, Randle)
  - Fool's Gold: 1 case (Russell)
- **True Negatives**: 17 cases (42.5%)
  - Empty Stats Star: 6 cases (KAT seasons)
  - Draft Bust: 7 cases (Fultz seasons)
  - Fragile Star: 3 cases (Simmons seasons)
  - Comparison Case: 1 case (Sabonis)

**Key Insight**: We have 22 problem cases (5 false positives + 17 true negatives) that should be predicted <55% star-level.

---

## Step 0.2: Feature Audit Results

### EFG_ISO_WEIGHTED (Quality Floor)

**Distribution**:
- Mean: 0.4846
- Median: 0.4849
- Min: 0.3596 (Markelle Fultz)
- Max: 0.6456

**Threshold Analysis**:
- Below 0.40: 1/25 (4.0%) - Only Fultz
- Below 0.42: 2/25 (8.0%) - Fultz + 1 other
- Below 0.45: 6/25 (24.0%) - **6 cases would be penalized**
- Below 0.48: 9/25 (36.0%) - 9 cases would be penalized

**Key Finding**: 
- **24% of problem cases** have EFG_ISO_WEIGHTED < 0.45
- Quality floor fix (threshold 0.45) would apply to **6 cases**
- **Current 25th percentile threshold**: 0.4042 (from qualified players)

**Recommendation**: Use **0.42 threshold** (catches 8% of cases) OR **percentile-based** (25th percentile = 0.4042)

---

### CREATION_TAX (Creation Efficiency)

**Distribution**:
- Mean: -0.2159 (negative = inefficient)
- Median: -0.1305
- Min: -0.8074 (very inefficient)
- Max: 0.0805 (slightly efficient)

**Key Finding**: 
- **All problem cases have negative CREATION_TAX** (mean = -0.22)
- This confirms they are inefficient creators
- Quality floor should penalize these cases

---

### RS_RIM_APPETITE (Rim Pressure)

**Distribution**:
- Mean: 0.4037
- Median: 0.3816
- Min: 0.1589
- Max: 0.6624
- **Bottom 20th percentile threshold**: 0.1746 (from qualified players)
- **Current bottom 20th percentile**: 0.1892 (from qualified players in model)

**Threshold Analysis**:
- Below 0.1746: 1/25 (4.0%) - Only 1 case (D'Angelo Russell)

**Key Finding**: 
- **Only 4% of problem cases** have low rim pressure (< 0.1746)
- Exponential flaw scaling would apply to **1 case** (Russell)
- Most problem cases have decent rim pressure (mean = 0.40)

**Recommendation**: Exponential flaw scaling may have **limited impact** - only affects 1 case directly

---

### DEPENDENCE_SCORE (System Dependence)

**Distribution**:
- Mean: 0.4301
- Median: 0.3607
- Min: 0.1706
- Max: 0.6719
- Coverage: 23/25 (92%)

**Threshold Analysis**:
- Above 0.45: 10/23 (43.5%) - **10 cases are system-dependent**
- Above 0.60: 9/23 (39.1%) - **9 cases are highly system-dependent**

**Key Finding**: 
- **43.5% of problem cases** are system-dependent (DEPENDENCE_SCORE > 0.45)
- This is the **largest category** of failure modes
- Dependence score fix would apply to **10 cases**

**Recommendation**: **Dependence score fix is highest priority** - affects most cases

---

### INEFFICIENT_VOLUME_SCORE (Stat-Stuffer Penalty)

**Distribution**:
- Mean: 0.0294
- Median: 0.0116
- Min: 0.0000
- Max: 0.1481

**Threshold Analysis**:
- Above 0.010: 13/25 (52.0%) - **13 cases have high inefficient volume**
- Above 0.015: 10/25 (40.0%) - **10 cases above current threshold**
- Above 0.020: 10/25 (40.0%) - **10 cases above higher threshold**

**Key Finding**: 
- **40% of problem cases** have INEFFICIENT_VOLUME_SCORE > 0.015
- Current sample weighting (5x) applies to **10 cases**
- Stat-stuffer penalty fix would strengthen penalty for these cases

**Recommendation**: **Stat-stuffer penalty fix is medium priority** - affects 40% of cases

---

## Step 0.3: Categorized False Positives

### By Failure Mode:

1. **System Dependent** (8 cases - 32%)
   - Jordan Poole, Willy Hernangomez, Christian Wood, Domantas Sabonis, KAT (4 seasons)
   - **Fix**: Dependence score should catch these

2. **Empty Calories** (3 cases - 12%)
   - Julius Randle, Ben Simmons (2 seasons)
   - **Fix**: INEFFICIENT_VOLUME_SCORE should catch these

3. **Multiple Issues** (7 cases - 28%)
   - D'Angelo Russell: empty_calories + low_rim_pressure
   - Kris Dunn: low_efficiency + empty_calories
   - KAT (2 seasons): low_efficiency + system_dependent + empty_calories
   - Markelle Fultz (3 seasons): low_efficiency + empty_calories
   - **Fix**: Multiple fixes needed

4. **Unknown** (7 cases - 28%)
   - Elfrid Payton, Talen Horton-Tucker, Ben Simmons (1 season), Markelle Fultz (4 seasons)
   - **Fix**: Need investigation

**Key Insight**: 
- **Different problems need different solutions**
- **System dependence is the largest category** (32%)
- **Multiple issues** require multiple fixes (28%)

---

## Step 0.4: Prediction Return Structure

**Return Keys**:
- `predicted_archetype`: str (e.g., "Bulldozer (Fragile Star)")
- `probabilities`: dict (probabilities for each archetype)
- `star_level_potential`: float (King + Bulldozer probability)
- `confidence_flags`: list (missing data flags)
- `phase3_flags`: list (gate/tax flags)
- `phase3_metadata`: dict (projection, tax, exemption info)

**Key Finding**: 
- Use `result['star_level_potential']` for validation
- Use `result['predicted_archetype']` for archetype
- Use `result['phase3_metadata']` for debugging

---

## Step 0.5: Pipeline Dependencies

**Pipeline Order**:
1. `evaluate_plasticity_potential.py` → `predictive_features_*.csv`
2. `calculate_shot_difficulty_features.py` → `pressure_features.csv`
3. `assemble_predictive_dataset.py` → `predictive_dataset.csv`
4. `generate_gate_features.py` → `gate_features.csv`
5. `train_rfe_model.py` → `models/resilience_xgb_rfe_10.pkl`

**File Status**: ✅ All required files exist and are up-to-date

---

## Key Insights for Implementation

### Priority 1: Dependence Score Fix (Highest Impact)
- **Affects**: 10 cases (43.5% of problem cases)
- **Category**: System-dependent players
- **Fix**: Strengthen DEPENDENCE_SCORE penalty or gate

### Priority 2: Quality Floor Fix (Medium Impact)
- **Affects**: 6 cases (24% of problem cases)
- **Category**: Low-efficiency players
- **Fix**: Integrate quality floor into CREATION_TAX calculation
- **Threshold**: Use 0.42 (catches 8%) OR percentile-based (25th = 0.4042)

### Priority 3: Stat-Stuffer Penalty (Medium Impact)
- **Affects**: 10 cases (40% of problem cases)
- **Category**: Empty-calories players
- **Fix**: Increase sample weighting from 5x → 10x OR increase feature exponent

### Priority 4: Exponential Flaw Scaling (Low Impact)
- **Affects**: 1 case (4% of problem cases)
- **Category**: Low rim pressure (D'Angelo Russell)
- **Fix**: Apply square root degradation to flaw features
- **Note**: Limited impact, but still worth implementing for completeness

---

## Recommendations

1. **Start with Dependence Score Fix** - Highest impact (43.5% of cases)
2. **Then Quality Floor Fix** - Medium impact (24% of cases)
3. **Then Stat-Stuffer Penalty** - Medium impact (40% of cases)
4. **Finally Exponential Flaw Scaling** - Low impact (4% of cases) but still valuable

5. **Use Percentile-Based Thresholds** - More robust than fixed values
6. **Test Incrementally** - One fix at a time, validate, document
7. **Protect True Positives** - Ensure fixes don't hurt Brunson, Maxey, etc.

---

## Next Steps

1. **Phase 1**: Implement Quality Floor Fix (integrate into CREATION_TAX)
2. **Phase 2**: Implement Exponential Flaw Scaling (for completeness)
3. **Phase 3**: Strengthen Stat-Stuffer Penalty (increase sample weighting)
4. **Phase 4**: Full validation on test suite

**Note**: Dependence Score Fix is already partially implemented (DEPENDENCE_SCORE exists, but may need strengthening). Consider investigating current implementation before adding new fixes.

