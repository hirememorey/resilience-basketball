# Phase 3 Validation Plan

**Date**: December 2025  
**Status**: Ready for Validation Testing  
**Goal**: Validate that Phase 3 fixes improve model performance on critical test cases

---

## Overview

Phase 3 fixes have been implemented in `predict_conditional_archetype.py`. This document outlines the validation strategy to measure improvement and ensure fixes work as expected.

**Current State**: 6/14 test cases passing (42.9%)  
**Expected After Phase 3**: 10-11/14 test cases passing (71-79%)

---

## Test Suite

**File**: `test_latent_star_cases.py` (or equivalent test script)  
**Test Cases**: 14 critical case studies grouped by failure mode

### Failure Mode Patterns

1. **Role Constraint** (4 cases - all currently failing):
   - Victor Oladipo (2016-17)
   - Lauri Markkanen (2021-22)
   - Desmond Bane (2021-22)
   - Mikal Bridges (2021-22)

2. **Context Dependency** (1 case - currently failing):
   - Jordan Poole (2021-22)

3. **Physicality/Fragility** (1 case - currently failing):
   - D'Angelo Russell (2018-19)

4. **True Positives** (3 cases - 1 passing, 2 failing):
   - Shai Gilgeous-Alexander (2018-19) - ✅ Passing
   - Jalen Brunson (2020-21) - ❌ Failing
   - Jamal Murray (2018-19) - ✅ Passing

5. **False Positives** (2 cases - 1 passing, 1 failing):
   - Talen Horton-Tucker (2020-21) - ✅ Passing
   - Tobias Harris (2016-17) - ❌ Failing

6. **System Player** (1 case - passing):
   - Tyus Jones (2021-22) - ✅ Passing

---

## Validation Strategy

### Step 1: Run Baseline Test Suite

**Action**: Run test suite with Phase 3 fixes **disabled** to establish baseline.

```python
# In test script, set apply_phase3_fixes=False
predictor = ConditionalArchetypePredictor()
result = predictor.predict_archetype_at_usage(
    player_data, 
    usage_level=0.30,
    apply_phase3_fixes=False  # Baseline
)
```

**Expected**: 6/14 passing (42.9%) - matches current state

**Output**: Baseline results CSV with predictions for all 14 cases

---

### Step 2: Test Each Fix Independently

#### Test Fix #1 Only (Usage-Dependent Weighting)

**Action**: Enable only Fix #1, disable Fix #2 and Fix #3.

**Expected Improvements**:
- Oladipo: Star-level should increase (from ~30% to ≥70%)
- Markkanen: Star-level should increase (from ~5% to ≥70%)
- Bane: Star-level should increase (from ~18% to ≥70%)
- Bridges: Star-level should increase (from ~17% to ≥70%)

**Validation**:
- Check that ALL 4 role-constrained players improve
- Measure improvement magnitude (should be significant)
- Check for regressions in other cases

**Output**: Fix #1 results CSV

---

#### Test Fix #2 Only (Context-Adjusted Efficiency)

**Action**: Enable only Fix #2, disable Fix #1 and Fix #3.

**Note**: Requires `RS_CONTEXT_ADJUSTMENT` to be calculated first. If not available, skip this test or calculate it.

**Expected Improvements**:
- Poole: Star-level should decrease (from ~50% to <30%)

**Validation**:
- Check that Poole's star-level decreases appropriately
- Check for regressions in other cases

**Output**: Fix #2 results CSV (or note if context adjustment not available)

---

#### Test Fix #3 Only (Fragility Gate)

**Action**: Enable only Fix #3, disable Fix #1 and Fix #2.

**Expected Improvements**:
- Russell: Star-level should decrease (from ~78% to <30%)

**Validation**:
- Check that Russell's star-level is capped at 30%
- Check that archetype changes to Sniper or Victim (not King/Bulldozer)
- Check for regressions in other cases

**Output**: Fix #3 results CSV

---

### Step 3: Test All Fixes Together

**Action**: Enable all three fixes.

**Expected Improvements**:
- Role Constraint pattern: 4/4 cases should improve
- Context Dependency: 1/1 case should improve (if context adjustment available)
- Physicality: 1/1 case should improve
- Overall: 10-11/14 passing (71-79%)

**Validation**:
- Measure improvement by pattern (not just individual cases)
- Check for regressions in passing cases
- Validate that fixes work together (no negative interactions)

**Output**: Combined results CSV

---

### Step 4: Pattern-Based Validation

**Action**: Analyze results by failure mode pattern, not just individual cases.

**Validation Criteria**:

1. **Role Constraint Pattern**:
   - All 4 cases should show improvement
   - Average star-level should increase significantly
   - At least 3/4 should pass (≥70% star-level)

2. **Context Dependency Pattern**:
   - Poole should show improvement (if context adjustment available)
   - Star-level should decrease to <30%

3. **Physicality Pattern**:
   - Russell should show improvement
   - Star-level should be capped at 30%

4. **No Regressions**:
   - Passing cases should still pass
   - No new failures introduced

---

## Key Files

1. **`src/nba_data/scripts/predict_conditional_archetype.py`**:
   - Enhanced with Phase 3 fixes
   - `prepare_features()`: Implements Fix #1 and Fix #2
   - `predict_archetype_at_usage()`: Implements Fix #3

2. **`test_latent_star_cases.py`** (or equivalent):
   - Test suite with 14 critical cases
   - Should be modified to test with/without Phase 3 fixes

3. **`analyze_phase3_data.py`**:
   - Data analysis script
   - Can be used to understand feature distributions

4. **`results/phase3_implementation_summary.md`**:
   - Complete implementation details
   - Expected impacts and thresholds

---

## Prerequisites

### Required Data

1. **Test Case Data**: All 14 test cases should be in dataset
   - Verify with `analyze_phase3_data.py`

2. **Context Adjustment** (for Fix #2):
   - `RS_CONTEXT_ADJUSTMENT` needs to be calculated
   - Currently not in dataset - needs implementation
   - Can skip Fix #2 validation if not available

3. **Rim Pressure Data** (for Fix #3):
   - `RIM_PRESSURE_RESILIENCE` should be in dataset
   - Threshold already calculated: 0.7555 (bottom 20th percentile)

### Required Scripts

1. Test suite script (or create one based on `test_latent_star_cases.py`)
2. Results comparison script (to compare baseline vs. fixes)

---

## Success Criteria

### Minimum Success (Must Achieve)

- **Role Constraint Pattern**: At least 3/4 cases improve significantly
- **Physicality Pattern**: Russell case improves (star-level <30%)
- **No Regressions**: Passing cases still pass
- **Overall**: At least 8/14 passing (57%)

### Target Success (Expected)

- **Role Constraint Pattern**: All 4/4 cases improve, at least 3/4 pass
- **Context Dependency Pattern**: Poole improves (if context adjustment available)
- **Physicality Pattern**: Russell improves
- **Overall**: 10-11/14 passing (71-79%)

### Ideal Success (Stretch Goal)

- **All Patterns**: All cases in each pattern improve
- **Overall**: 12-13/14 passing (86-93%)

---

## Validation Results

**Status**: ✅ **VALIDATION COMPLETE** (December 2025)

**Results**: 6/14 passed (42.9%) - Same as baseline. No improvement.

**Key Findings**:
1. **Fix #1 Failed**: Linear scaling doesn't cross tree model decision boundaries
2. **Fix #2 Cannot Be Applied**: Missing `RS_CONTEXT_ADJUSTMENT` data
3. **Fix #3 Failed**: Used ratio metric instead of absolute volume metric

**Detailed Results**: See `results/phase3_validation_report.md` and `results/phase3_validation_analysis.md`

## Next Steps: Phase 3.5 Implementation

**Status**: 🎯 **READY FOR IMPLEMENTATION** (December 2025)

Based on first principles analysis, Phase 3.5 addresses the fundamental flaws identified in validation.

**See**: `PHASE3_5_IMPLEMENTATION_PLAN.md` for complete implementation plan.

**Key Fixes**:
1. Switch fragility gate to `RS_RIM_APPETITE` (absolute volume) instead of `RIM_PRESSURE_RESILIENCE` (ratio)
2. Implement projected volume features instead of linear scaling
3. Calculate `RS_CONTEXT_ADJUSTMENT` data before re-validation

**Expected After Phase 3.5**: 10-11/14 passed (71-79%)

---

## Notes

- **Pattern-Based Validation**: Focus on improving failure mode patterns, not just individual cases
- **Context Adjustment**: Fix #2 requires data calculation - may need to implement first
- **Missing Data**: Some test cases (Markkanen, Bane) have missing pressure data - may need Fix #4 first
- **Gradual Scaling**: Fix #1 uses gradual scaling (not binary) - validate that scaling works correctly

---

**See Also**:
- `results/phase3_implementation_summary.md` - Implementation details
- `CURRENT_STATE.md` - Current project state
- `KEY_INSIGHTS.md` - Hard-won lessons

