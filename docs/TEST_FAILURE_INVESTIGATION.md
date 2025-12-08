# First Principles Investigation: Test Case Failures

**Date**: December 8, 2025  
**Status**: Deep Dive Analysis  
**Goal**: Identify root causes of 8 failing test cases using first principles reasoning

---

## Executive Summary

**Current State**: 75.0% pass rate (24/32 cases)  
**Remaining Failures**: 8 cases across 3 categories:
- **True Positives Under-Predicted**: 2 cases (Bane, Haliburton)
- **True Negatives Over-Predicted**: 5 cases (KAT x2, Fultz x2, Randle)
- **Risk Category Mismatch**: 1 case (Sabonis)

**Root Cause Hypothesis**: Two orthogonal failure modes:
1. **Gate Logic Too Aggressive**: Gates capping true positives at 30% (Haliburton, Sabonis)
2. **Model Over-Confidence**: Model predicting "King" for players with fatal flaws (KAT, Fultz)

---

## Failure Mode 1: Gate Logic Capping True Positives

### Case 1: Tyrese Haliburton (2021-22)
**Expected**: ≥65% performance, "Franchise Cornerstone"  
**Actual**: 30.00% performance, "Moderate Performance, Low Dependence"  
**Root Cause**: Gate capping at 30%

**First Principles Analysis**:
- **What the model sees**: 43.06% King probability + 15.61% Bulldozer = 58.67% raw star-level
- **What gates see**: Some gate is capping at 30% before risk matrix calculation
- **The Physics**: Haliburton is a true star with elite creation and leverage vectors. The gate is incorrectly identifying a flaw that doesn't exist.

**Investigation Needed**:
1. Check which gate is triggering (no gate log message in output)
2. Verify data completeness for Haliburton
3. Check if sample size gate is triggering (low usage = 18.4%)
4. Check if leverage data penalty is triggering

**Hypothesis**: Sample Size Gate or Leverage Data Penalty is triggering because Haliburton had low usage (18.4%) in 2021-22, leading to insufficient clutch minutes or pressure shots.

### Case 2: Domantas Sabonis (2021-22)
**Expected**: "Luxury Component" risk category  
**Actual**: 30.00% performance, "Moderate Performance, High Dependence"  
**Root Cause**: Bag Check Gate capping at 30%

**First Principles Analysis**:
- **What the model sees**: 61.21% raw star-level (28.71% King + 32.50% Bulldozer)
- **What gates see**: Bag Check Gate: Self-created freq 0.069 < 0.10 → cap at 30%
- **The Physics**: Sabonis is a hub player (system-based creation via DHOs, cuts). The Bag Check Gate correctly identifies lack of self-creation, but the risk category assignment is wrong.

**Investigation Needed**:
1. Bag Check Gate is working as designed (correctly capping at 30%)
2. Risk category logic needs refinement: "Luxury Component" = High Performance + High Dependence
3. Current logic: 30% performance = "Moderate Performance" (threshold issue)

**Hypothesis**: Risk category thresholds are too strict. 30% performance with 60.37% dependence should map to "Luxury Component" (high dependence = system merchant), not "Moderate Performance".

### Case 3: Desmond Bane (2021-22)
**Expected**: ≥65% performance, "Bulldozer"  
**Actual**: 48.96% performance, "Victim"  
**Root Cause**: Model under-prediction (no gate capping)

**First Principles Analysis**:
- **What the model sees**: 25.54% King + 23.42% Bulldozer = 48.96% star-level
- **What gates see**: No gate capping (performance is 48.96%, not 30%)
- **The Physics**: Bane is a secondary creator who can scale up. Model is not recognizing elite creation vector at low volume.

**Investigation Needed**:
1. Check if Flash Multiplier is triggering (should detect elite efficiency on low volume)
2. Check creation tax and isolation efficiency
3. Check if model is penalizing secondary creator role too heavily

**Hypothesis**: Flash Multiplier conditions not met, or model is under-weighting secondary creator profiles. Bane's 22.6% usage may be below the threshold for Flash Multiplier detection.

---

## Failure Mode 2: Model Over-Predicting False Positives

### Case 4: Karl-Anthony Towns (2018-19)
**Expected**: <55% performance, "Victim"  
**Actual**: 78.30% performance, "King"  
**Root Cause**: Model over-confidence

**First Principles Analysis**:
- **What the model sees**: 75.87% King + 2.43% Bulldozer = 78.30% star-level
- **What gates see**: No gate capping (performance is 78.30%)
- **The Physics**: KAT has elite regular season stats but lacks playoff resilience. Model is seeing high volume + decent efficiency and predicting "King", ignoring fatal flaws.

**Investigation Needed**:
1. Check what features are driving the "King" prediction
2. Check if leverage data shows abdication (LEVERAGE_USG_DELTA)
3. Check if rim pressure resilience is being captured
4. Check if creation tax is positive (efficiency drop-off)

**Hypothesis**: Model is over-weighting volume × efficiency interaction (USG_PCT × EFG_ISO_WEIGHTED) and under-weighting leverage resilience. KAT's regular season stats look elite, but playoff performance reveals fragility.

### Case 5: Karl-Anthony Towns (2020-21)
**Expected**: <55% performance, "Victim"  
**Actual**: 61.30% performance, "King"  
**Root Cause**: Model over-confidence (less severe than 2018-19)

**First Principles Analysis**:
- **What the model sees**: 48.72% King + 12.57% Bulldozer = 61.30% star-level
- **What gates see**: No gate capping
- **The Physics**: Same pattern as 2018-19, but model is slightly less confident (61.30% vs 78.30%).

**Investigation Needed**: Same as Case 4.

### Case 6: Markelle Fultz (2019-20)
**Expected**: <55% performance, "Victim"  
**Actual**: 79.20% performance, "King"  
**Root Cause**: Model over-confidence (most severe)

**First Principles Analysis**:
- **What the model sees**: 77.85% King + 1.35% Bulldozer = 79.20% star-level
- **What gates see**: No gate capping
- **The Physics**: Fultz has fatal flaws (shooting, creation) but model is predicting "King". This is the most concerning failure - model is completely wrong.

**Investigation Needed**:
1. Check if creation tax is being calculated correctly (should be negative)
2. Check if isolation efficiency is being captured
3. Check if sample size is too small (21.0% usage, limited minutes)
4. Check if model is seeing small-sample noise as signal

**Hypothesis**: Small sample size (21.0% usage, limited minutes) is creating noise. Model is seeing random efficiency spikes as signal. Inefficiency Gate should catch this (EFG_ISO_WEIGHTED < 25th percentile), but it's not triggering.

### Case 7: Markelle Fultz (2022-23)
**Expected**: <55% performance, "Victim"  
**Actual**: 89.22% performance, "King"  
**Root Cause**: Model over-confidence (most severe)

**First Principles Analysis**:
- **What the model sees**: Model predicting 89.22% King probability
- **What gates see**: No gate capping
- **The Physics**: Same as 2019-20, but even more severe. Model is completely wrong.

**Investigation Needed**: Same as Case 6.

### Case 8: Julius Randle (2020-21)
**Expected**: <55% performance, "Victim"  
**Actual**: 61.13% performance, "King"  
**Root Cause**: Model over-confidence (close to threshold)

**First Principles Analysis**:
- **What the model sees**: 48.72% King + 12.57% Bulldozer = 61.30% star-level (wait, this matches KAT 2020-21 exactly?)
- **What gates see**: No gate capping
- **The Physics**: Randle had All-NBA regular season but playoff collapse. Model is seeing high volume + decent efficiency and predicting "King", ignoring playoff fragility.

**Investigation Needed**:
1. Check if leverage data shows abdication
2. Check if pressure resilience is being captured
3. Check if creation tax is positive (efficiency drop-off)

**Hypothesis**: Model is over-weighting regular season volume × efficiency and under-weighting leverage resilience. Randle's regular season stats look elite, but playoff performance reveals fragility.

---

## Root Cause Analysis: First Principles

### Principle 1: Filter First, Then Rank
**Current Issue**: Gates are filtering true positives (Haliburton, Sabonis) before the model can rank them.

**The Physics**:
- **Haliburton**: Elite creation + leverage vectors → should be ranked high, not filtered
- **Sabonis**: System-based creation → correctly filtered, but risk category wrong

**The Fix**:
- **Haliburton**: Gate logic needs refinement. Low usage (18.4%) doesn't mean insufficient data if player has elite efficiency.
- **Sabonis**: Risk category thresholds need refinement. 30% performance + 60% dependence = "Luxury Component", not "Moderate Performance".

### Principle 2: No Proxies
**Current Issue**: Model is using volume × efficiency as proxy for resilience, ignoring leverage data.

**The Physics**:
- **KAT, Fultz, Randle**: High volume + decent efficiency → model predicts "King"
- **Reality**: Leverage data (LEVERAGE_USG_DELTA, LEVERAGE_TS_DELTA) should reveal fragility

**The Fix**:
- Model needs to weight leverage features more heavily
- Gates need to check leverage data before allowing "King" prediction

### Principle 3: Resilience = Efficiency × Volume
**Current Issue**: Model is seeing efficiency × volume and predicting resilience, ignoring the "Abdication Tax".

**The Physics**:
- **KAT, Randle**: High volume in regular season → model assumes resilience
- **Reality**: Playoff volume drops (LEVERAGE_USG_DELTA < -0.05) → "Abdication Tax" should trigger

**The Fix**:
- Negative Signal Gate should catch this, but it's not triggering for KAT/Randle
- Check if High-Usage Immunity is incorrectly exempting these players

### Principle 4: Learn, Don't Patch
**Current Issue**: Gates are patching model failures, but model itself is making wrong predictions.

**The Physics**:
- **Fultz**: Model predicting "King" when it should predict "Victim"
- **Gates**: Not catching this (no gate capping)

**The Fix**:
- Model needs better training on false positives (KAT, Fultz, Randle patterns)
- Sample weighting (5x) may not be strong enough
- Consider increasing to 10x or adding explicit false positive examples

### Principle 5: Two-Dimensional Evaluation
**Current Issue**: Risk category thresholds are too strict.

**The Physics**:
- **Sabonis**: 30% performance + 60% dependence → should be "Luxury Component"
- **Current Logic**: 30% < threshold → "Moderate Performance"

**The Fix**:
- Risk category thresholds need refinement
- "Luxury Component" should allow 30% performance if dependence is high (>50%)

---

## Investigation Plan

### Phase 1: Gate Logic Investigation
1. **Trace gate logic for Haliburton**:
   - Check which gate is triggering (add logging)
   - Verify data completeness
   - Check sample size thresholds
   - Check leverage data availability

2. **Trace gate logic for Sabonis**:
   - Bag Check Gate is working (correctly capping)
   - Fix risk category thresholds
   - Allow "Luxury Component" for 30% performance + high dependence

3. **Trace gate logic for Bane**:
   - Check Flash Multiplier conditions
   - Check creation tax and isolation efficiency
   - Check if model is penalizing secondary creator role

### Phase 2: Model Over-Confidence Investigation
1. **Trace model predictions for KAT, Fultz, Randle**:
   - Check feature importance for these cases
   - Check if leverage data is present and being used
   - Check if Negative Signal Gate should trigger
   - Check if High-Usage Immunity is incorrectly exempting

2. **Check training data**:
   - Verify KAT, Fultz, Randle are in training set with correct labels
   - Check if sample weighting is working (5x penalty)
   - Consider increasing to 10x or adding explicit false positive examples

3. **Check feature engineering**:
   - Verify leverage features are being calculated correctly
   - Check if creation tax is capturing efficiency drop-off
   - Check if pressure resilience is being captured

### Phase 3: Risk Category Refinement
1. **Fix risk category thresholds**:
   - Allow "Luxury Component" for 30% performance + high dependence (>50%)
   - Refine "Franchise Cornerstone" threshold (currently too strict)

2. **Test risk category logic**:
   - Run test suite with refined thresholds
   - Verify Sabonis maps to "Luxury Component"

---

## Next Steps

1. **Immediate**: Add detailed logging to gate logic to identify which gates are triggering
2. **Short-term**: Fix risk category thresholds for Sabonis case
3. **Medium-term**: Investigate model over-confidence for KAT, Fultz, Randle
4. **Long-term**: Consider increasing sample weighting or adding explicit false positive examples

---

## Key Insights

1. **Gate Logic**: Too aggressive for true positives (Haliburton), but working for system players (Sabonis)
2. **Model Over-Confidence**: Model is over-weighting volume × efficiency and under-weighting leverage resilience
3. **Risk Category Thresholds**: Too strict - need refinement for edge cases
4. **Sample Weighting**: 5x may not be strong enough - consider 10x or explicit false positive examples

---

**Status**: Investigation in progress. Awaiting detailed gate logging and model prediction traces.

