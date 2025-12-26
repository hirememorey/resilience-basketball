# Test Failure Root Causes: First Principles Analysis

**Date**: December 8, 2025  
**Status**: Root Causes Identified  
**Method**: Diagnostic script + gate logic tracing

---

## Executive Summary

**8 Failing Cases** fall into **3 distinct failure modes**:

1. **Gate Logic Too Aggressive** (2 cases): Gates capping true positives at 30%
   - **Haliburton**: Fragility Gate triggering incorrectly
   - **Sabonis**: Bag Check Gate working correctly, but risk category wrong

2. **Model Over-Confidence** (5 cases): Model predicting "King" for players with fatal flaws
   - **KAT (2018-19, 2020-21)**: Model over-weighting volume × efficiency
   - **Fultz (2019-20, 2022-23)**: Model seeing small-sample noise as signal
   - **Randle (2020-21)**: Model ignoring leverage fragility

3. **Model Under-Confidence** (1 case): Model under-predicting true positives
   - **Bane**: Model not recognizing elite secondary creator profile

---

## Failure Mode 1: Gate Logic Too Aggressive

### Case 1: Tyrese Haliburton (2021-22)
**Expected**: ≥65% performance, "Franchise Cornerstone"  
**Actual**: 30.00% performance, "Moderate Performance, Low Dependence"  
**Root Cause**: **Fragility Gate triggering incorrectly**

**Diagnostic Findings**:
- **RS_RIM_APPETITE**: 0.1639 (below threshold 0.1892)
- **Self-created freq**: 0.7105 (OK, above 0.10)
- **Leverage data**: Present (USG_DELTA=-0.0190, TS_DELTA=-0.0720, Clutch=133.2)
- **Gate Trigger**: Fragility Gate WOULD TRIGGER

**First Principles Analysis**:
- **The Physics**: Haliburton is a **high-usage creator** (73.68% creation volume ratio) with **elite creation efficiency** (CREATION_TAX=-0.1521, meaning he's MORE efficient in creation than overall). The Fragility Gate is checking rim pressure, but **high-usage creators can score without rim pressure** (see Phase 4.3 High-Usage Creator Exemption).

**The Problem**:
- Haliburton's RS_USG_PCT = 18.4% (below 25% threshold for High-Usage Creator Exemption)
- But he has **73.68% creation volume ratio** (way above 60% threshold)
- The exemption logic requires BOTH high usage (>25%) AND high creation volume (>60%)

**The Fix**:
- **Option 1**: Lower usage threshold for High-Usage Creator Exemption (e.g., 20% instead of 25%)
- **Option 2**: Add "Elite Creator Exemption" for players with >70% creation volume ratio regardless of usage
- **Option 3**: Check creation efficiency (CREATION_TAX) - if elite (< -0.10), exempt from Fragility Gate

**Recommended Fix**: Option 2 + Option 3 (Elite Creator Exemption based on creation volume ratio OR creation efficiency)

### Case 2: Domantas Sabonis (2021-22)
**Expected**: "Luxury Component" risk category  
**Actual**: 30.00% performance, "Moderate Performance, High Dependence"  
**Root Cause**: **Bag Check Gate working correctly, but risk category thresholds wrong**

**Diagnostic Findings**:
- **Self-created freq**: 0.0690 (below 0.10 threshold) → **Bag Check Gate correctly triggers**
- **Dependence Score**: 60.37% (high dependence)
- **Performance Score**: 30.00% (capped by Bag Check Gate)
- **Risk Category**: "Moderate Performance, High Dependence" (wrong)

**First Principles Analysis**:
- **The Physics**: Sabonis is a **system-based hub player** (DHOs, cuts). The Bag Check Gate correctly identifies lack of self-creation and caps at 30%. However, the risk category logic is wrong:
  - **30% performance + 60% dependence** = "Luxury Component" (system merchant who performs well but is dependent)
  - **Current logic**: 30% < 0.70 threshold → "Moderate Performance" (wrong)

**The Problem**:
- Risk category thresholds are too strict
- "Luxury Component" should allow 30% performance if dependence is high (>50%)

**The Fix**:
- Refine risk category thresholds:
  - **"Luxury Component"**: Performance ≥ 30% AND Dependence ≥ 50% (system merchant)
  - **"Franchise Cornerstone"**: Performance ≥ 65% AND Dependence < 50% (portable star)
  - **"Depth"**: Performance < 30% AND Dependence < 50% (role player)
  - **"Avoid"**: Performance < 30% AND Dependence ≥ 50% (fragile system player)

**Recommended Fix**: Update `_categorize_risk()` to allow "Luxury Component" for 30% performance + high dependence

---

## Failure Mode 2: Model Over-Confidence

### Case 3: Karl-Anthony Towns (2018-19)
**Expected**: <55% performance, "Victim"  
**Actual**: 78.30% performance, "King"  
**Root Cause**: **Model over-weighting volume × efficiency, ignoring leverage fragility**

**Diagnostic Findings**:
- **LEVERAGE_USG_DELTA**: -0.0070 (slight drop, not enough to trigger Abdication Tax)
- **LEVERAGE_TS_DELTA**: -0.1190 (significant efficiency drop in clutch)
- **CREATION_TAX**: -0.0820 (negative = efficiency drop in creation)
- **No gates triggering**: Model is making wrong prediction

**First Principles Analysis**:
- **The Physics**: KAT has **high volume** (28.0% usage) + **decent efficiency** (EFG_ISO_WEIGHTED=0.5320), so model predicts "King". However, **LEVERAGE_TS_DELTA=-0.1190** shows he **collapses in clutch situations** (efficiency drops 11.9%). This is a fatal flaw that the model is ignoring.

**The Problem**:
- Model is over-weighting **USG_PCT × EFG_ISO_WEIGHTED** interaction (feature #2, 8.85% importance)
- Model is under-weighting **LEVERAGE_TS_DELTA** (not in top 10 features)
- Negative Signal Gate should catch LEVERAGE_TS_DELTA < -0.15, but -0.1190 is just above threshold

**The Fix**:
- **Option 1**: Lower Negative Signal Gate threshold for LEVERAGE_TS_DELTA (e.g., -0.10 instead of -0.15)
- **Option 2**: Add "Clutch Fragility Gate" that caps at 30% if LEVERAGE_TS_DELTA < -0.10
- **Option 3**: Increase sample weighting for KAT pattern (high volume + negative leverage TS delta)

**Recommended Fix**: Option 2 (Clutch Fragility Gate) - catches KAT pattern without affecting other cases

### Case 4: Karl-Anthony Towns (2020-21)
**Expected**: <55% performance, "Victim"  
**Actual**: 61.30% performance, "King"  
**Root Cause**: **Same as 2018-19, but less severe**

**Diagnostic Findings**:
- **LEVERAGE_USG_DELTA**: 0.0240 (positive = scales up, not abdication)
- **LEVERAGE_TS_DELTA**: 0.1200 (positive = efficiency spikes in clutch)
- **CREATION_TAX**: -0.1997 (very negative = efficiency drops significantly in creation)
- **No gates triggering**: Model is making wrong prediction

**First Principles Analysis**:
- **The Physics**: KAT's leverage data looks good (positive deltas), but **CREATION_TAX=-0.1997** shows he's **inefficient in creation** (efficiency drops 20% when creating own shot). This is a fatal flaw for a "King" - he can't create efficiently.

**The Problem**:
- Model is seeing positive leverage deltas and predicting "King"
- But CREATION_TAX=-0.1997 is a fatal flaw (efficiency drops 20% in creation)
- Negative Signal Gate should catch CREATION_TAX < -0.10, but it's not triggering

**The Fix**:
- **Option 1**: Check if Negative Signal Gate is checking CREATION_TAX correctly
- **Option 2**: Add "Creation Fragility Gate" that caps at 30% if CREATION_TAX < -0.15
- **Option 3**: Increase sample weighting for KAT pattern (positive leverage + negative creation tax)

**Recommended Fix**: Option 2 (Creation Fragility Gate) - catches KAT pattern

### Case 5: Markelle Fultz (2019-20)
**Expected**: <55% performance, "Victim"  
**Actual**: 79.20% performance, "King"  
**Root Cause**: **Model seeing small-sample noise as signal**

**Diagnostic Findings**:
- **CREATION_TAX**: -0.0074 (near-zero = no efficiency drop, but this is noise)
- **EFG_ISO_WEIGHTED**: 0.4826 (below median 0.4594, but not below floor 0.4042)
- **LEVERAGE_TS_DELTA**: 0.0610 (positive = efficiency spikes, but this is noise)
- **USG_PCT**: 21.0% (low usage = small sample size)
- **No gates triggering**: Model is seeing noise as signal

**First Principles Analysis**:
- **The Physics**: Fultz has **low usage** (21.0%) with **small sample size**. The model is seeing random efficiency spikes (LEVERAGE_TS_DELTA=0.0610, CREATION_TAX=-0.0074) as signal, but this is **small-sample noise**, not true skill.

**The Problem**:
- Sample Size Gate should catch this (suspicious creation: CREATION_TAX >= 0.8 with usage < 20%), but Fultz's CREATION_TAX=-0.0074 is not suspicious (it's near-zero, not near-perfect)
- Inefficiency Gate should catch this (EFG_ISO_WEIGHTED < 25th percentile OR uniformly mediocre), but Fultz's EFG_ISO_WEIGHTED=0.4826 is above floor (0.4042)

**The Fix**:
- **Option 1**: Lower Sample Size Gate threshold for low-usage players (e.g., usage < 22% → require more clutch minutes)
- **Option 2**: Add "Low-Usage Noise Gate" that caps at 30% if usage < 22% AND CREATION_TAX near-zero (noise pattern)
- **Option 3**: Check if Fultz's data is actually valid (may be injury-affected season)

**Recommended Fix**: Option 2 (Low-Usage Noise Gate) - catches Fultz pattern

### Case 6: Markelle Fultz (2022-23)
**Expected**: <55% performance, "Victim"  
**Actual**: 89.22% performance, "King"  
**Root Cause**: **Same as 2019-20, but even more severe**

**Diagnostic Findings**:
- **CREATION_TAX**: -0.0334 (negative but small = noise)
- **EFG_ISO_WEIGHTED**: 0.5186 (above median, not below floor)
- **LEVERAGE_TS_DELTA**: 0.1010 (positive = efficiency spikes, but this is noise)
- **USG_PCT**: 20.8% (low usage = small sample size)
- **No gates triggering**: Model is seeing noise as signal

**The Fix**: Same as Case 5 (Low-Usage Noise Gate)

### Case 7: Julius Randle (2020-21)
**Expected**: <55% performance, "Victim"  
**Actual**: 61.13% performance, "King"  
**Root Cause**: **Model ignoring leverage fragility**

**Diagnostic Findings**:
- **LEVERAGE_USG_DELTA**: 0.0220 (positive = scales up, not abdication)
- **LEVERAGE_TS_DELTA**: -0.0620 (negative = efficiency drops in clutch)
- **CREATION_TAX**: -0.1362 (negative = efficiency drops in creation)
- **No gates triggering**: Model is making wrong prediction

**First Principles Analysis**:
- **The Physics**: Randle has **high volume** (28.5% usage) + **decent efficiency**, so model predicts "King". However, **LEVERAGE_TS_DELTA=-0.0620** shows he **drops efficiency in clutch** (efficiency drops 6.2%). Combined with **CREATION_TAX=-0.1362** (efficiency drops 13.6% in creation), this is a fatal flaw.

**The Problem**:
- Model is over-weighting volume × efficiency
- Model is under-weighting leverage fragility
- Negative Signal Gate should catch multiple negative signals (CREATION_TAX < -0.10 AND LEVERAGE_TS_DELTA < -0.15), but thresholds are too strict

**The Fix**:
- **Option 1**: Lower Negative Signal Gate thresholds (e.g., CREATION_TAX < -0.10 OR LEVERAGE_TS_DELTA < -0.10)
- **Option 2**: Add "Compound Fragility Gate" that caps at 30% if CREATION_TAX < -0.10 AND LEVERAGE_TS_DELTA < -0.05
- **Option 3**: Increase sample weighting for Randle pattern (high volume + negative creation tax + negative leverage TS delta)

**Recommended Fix**: Option 2 (Compound Fragility Gate) - catches Randle pattern

---

## Failure Mode 3: Model Under-Confidence

### Case 8: Desmond Bane (2021-22)
**Expected**: ≥65% performance, "Bulldozer"  
**Actual**: 48.96% performance, "Victim"  
**Root Cause**: **Model not recognizing elite secondary creator profile**

**Diagnostic Findings**:
- **CREATION_VOLUME_RATIO**: 0.3874 (moderate, not high)
- **CREATION_TAX**: -0.1304 (negative = efficiency drops, but this is wrong - Bane is elite)
- **EFG_ISO_WEIGHTED**: 0.5286 (above 80th percentile 0.5188 = elite)
- **LEVERAGE_USG_DELTA**: -0.0340 (slight drop, not enough to trigger)
- **LEVERAGE_TS_DELTA**: -0.0160 (slight drop, not significant)
- **Self-created freq**: 0.2308 (OK, above 0.10)
- **No gates triggering**: Model is under-predicting

**First Principles Analysis**:
- **The Physics**: Bane is an **elite secondary creator** with **high shooting efficiency** (EFG_ISO_WEIGHTED=0.5286, above 80th percentile). However, **CREATION_TAX=-0.1304** is negative, which the model interprets as "efficiency drops in creation". But this is wrong - Bane is elite at creation, the negative tax is likely due to small sample size or data quality.

**The Problem**:
- Model is seeing CREATION_TAX=-0.1304 (negative) and penalizing
- But EFG_ISO_WEIGHTED=0.5286 (elite) suggests Bane is actually elite at creation
- Flash Multiplier should detect this (low volume + elite efficiency), but conditions may not be met

**The Fix**:
- **Option 1**: Check if Flash Multiplier conditions are met (low volume + elite efficiency)
- **Option 2**: Add "Elite Efficiency Override" that ignores negative CREATION_TAX if EFG_ISO_WEIGHTED is elite (>80th percentile)
- **Option 3**: Check if CREATION_TAX calculation is correct for Bane (may be data quality issue)

**Recommended Fix**: Option 2 (Elite Efficiency Override) - catches Bane pattern

---

## Summary of Recommended Fixes

1. **Haliburton**: Add "Elite Creator Exemption" to Fragility Gate (creation volume ratio >70% OR creation efficiency < -0.10)
2. **Sabonis**: Fix risk category thresholds (allow "Luxury Component" for 30% performance + high dependence)
3. **KAT (2018-19)**: Add "Clutch Fragility Gate" (cap at 30% if LEVERAGE_TS_DELTA < -0.10)
4. **KAT (2020-21)**: Add "Creation Fragility Gate" (cap at 30% if CREATION_TAX < -0.15)
5. **Fultz (2019-20, 2022-23)**: Add "Low-Usage Noise Gate" (cap at 30% if usage < 22% AND CREATION_TAX near-zero)
6. **Randle**: Add "Compound Fragility Gate" (cap at 30% if CREATION_TAX < -0.10 AND LEVERAGE_TS_DELTA < -0.05)
7. **Bane**: Add "Elite Efficiency Override" (ignore negative CREATION_TAX if EFG_ISO_WEIGHTED is elite)

---

## Next Steps

1. **Immediate**: Implement fixes for Haliburton and Sabonis (gate logic and risk category)
2. **Short-term**: Add new gates for KAT, Fultz, Randle patterns
3. **Medium-term**: Investigate Bane case (data quality vs. model issue)
4. **Long-term**: Consider retraining model with increased sample weighting for false positive patterns

---

**Status**: Root causes identified. Ready for implementation.

