# Dependence Score Fix Plan

**Date**: December 10, 2025  
**Status**: Planning  
**Priority**: High (affects 43.5% of problem cases - 10 cases)

---

## Problem Analysis

### Current State

**System Merchant Gate**:
- Condition: `USG_PCT > 0.25 AND DEPENDENCE_SCORE > 0.45`
- Action: Cap at 30%
- Status: ✅ Working for high-usage cases (Jordan Poole)

**Dependence Law** (2D Risk Matrix):
- Condition: `DEPENDENCE_SCORE > 0.60`
- Action: Cap risk category at "Luxury Component"
- Status: ✅ Working

### Failure Cases

1. **Willy Hernangomez (2016-17)**: 
   - DEP=0.664 (very high)
   - USG_PCT=19.9% (< 25% threshold)
   - Star-level: 72.4% ❌
   - **Issue**: System Merchant Gate doesn't apply because usage is too low

2. **Other cases**: Most are already passing (<55%), but gates aren't being detected properly

---

## Root Cause

**The Problem**: System Merchant Gate requires `USG_PCT > 0.25`, but some system-dependent players have lower usage (e.g., Hernangomez at 19.9%).

**First Principles**: 
- **High dependence is a flaw regardless of usage level**
- A player with DEPENDENCE_SCORE > 0.60 is system-dependent even at low usage
- The current gate only catches high-usage system merchants

---

## Proposed Fixes

### Fix 1: Lower Usage Threshold for High Dependence (Recommended)

**Change**: Apply System Merchant Gate to high-dependence players even at lower usage

**Logic**:
```python
# Current: USG_PCT > 0.25 AND DEPENDENCE_SCORE > 0.45
# New: (USG_PCT > 0.25 AND DEPENDENCE_SCORE > 0.45) OR (DEPENDENCE_SCORE > 0.60)
```

**Rationale**:
- DEPENDENCE_SCORE > 0.60 is already used in Dependence Law (very high dependence)
- High dependence is a flaw regardless of usage
- Catches Hernangomez (DEP=0.664) even at 19.9% usage

**Impact**:
- Catches: Hernangomez (DEP=0.664, USG=19.9%)
- Protects: Low-usage, low-dependence players (not affected)

---

### Fix 2: Strengthen Dependence Law Penalty

**Change**: Make Dependence Law more aggressive

**Current**: `DEPENDENCE_SCORE > 0.60` → cap risk category at "Luxury Component"

**Proposed**: `DEPENDENCE_SCORE > 0.60` → cap star-level at 30% (not just risk category)

**Rationale**:
- Dependence Law currently only affects risk category, not star-level
- High dependence (0.60+) should directly cap performance prediction
- Aligns with System Merchant Gate logic

**Impact**:
- Catches: All cases with DEP > 0.60 (9 cases from audit)
- More aggressive than Fix 1

---

### Fix 3: Add Sample Weighting for High Dependence

**Change**: Increase sample weight for high-dependence cases during training

**Logic**:
```python
# Add to train_rfe_model.py
if 'DEPENDENCE_SCORE' in df.columns:
    dep_scores = df.loc[train_indices, 'DEPENDENCE_SCORE'].fillna(0.0)
    is_high_dependence = dep_scores > 0.60
    sample_weights[is_high_dependence] *= 3.0  # 3x weight
```

**Rationale**:
- Helps model learn to penalize high-dependence players
- Complements gate logic
- More robust (model learns pattern, not just gate enforces it)

**Impact**:
- Affects model training (not just inference)
- Helps model learn the pattern

---

## Recommended Implementation

### Phase 1: Fix 1 - Lower Usage Threshold (Immediate)

**Priority**: High - Catches Hernangomez case

**Implementation**:
1. Modify System Merchant Gate condition in `predict_conditional_archetype.py`
2. Change from: `USG_PCT > 0.25 AND DEPENDENCE_SCORE > 0.45`
3. To: `(USG_PCT > 0.25 AND DEPENDENCE_SCORE > 0.45) OR (DEPENDENCE_SCORE > 0.60)`

**Validation**:
- Test on Hernangomez: Should be capped at 30%
- Test on other cases: Should not break existing behavior

---

### Phase 2: Fix 2 - Strengthen Dependence Law (If Needed)

**Priority**: Medium - More aggressive penalty

**Implementation**:
1. Modify Dependence Law in `predict_conditional_archetype.py`
2. Add star-level cap: `DEPENDENCE_SCORE > 0.60` → cap at 30%

**Validation**:
- Test on all cases with DEP > 0.60
- Ensure risk category logic still works

---

### Phase 3: Fix 3 - Sample Weighting (Optional)

**Priority**: Low - Helps model learn, but gates already catch cases

**Implementation**:
1. Add sample weighting in `train_rfe_model.py`
2. Retrain model
3. Validate on test cases

---

## Expected Impact

**Current**: 1/10 system-dependent cases still failing (Hernangomez)

**After Fix 1**: 0/10 cases failing ✅

**After Fix 2**: 0/10 cases failing ✅ (more aggressive)

**After Fix 3**: Model learns pattern better (complementary to gates)

---

## Implementation Steps

1. **Test current behavior** on Hernangomez case
2. **Implement Fix 1** (lower usage threshold)
3. **Validate** on all system-dependent cases
4. **If needed**, implement Fix 2 (strengthen Dependence Law)
5. **Document** changes and results

