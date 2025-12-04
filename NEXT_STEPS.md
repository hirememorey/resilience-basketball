# Next Steps: Phase 3.7 Follow-Up

**Date**: December 4, 2025  
**Status**: Phase 3.7 Implementation Complete | Follow-Up Items Identified

---

## What Was Completed

✅ **Phase 3.7 Fix #1**: Playoff Translation Tax moved from efficiency to volume  
✅ **Phase 3.7 Fix #2**: Flash Multiplier widened to include Pressure Resilience  
✅ **Data Completeness Fix**: Changed INNER JOIN to LEFT JOIN, added 3,253 RS-only players

**Current Pass Rate**: 62.5% (10/16) - decreased from 75.0% due to threshold shifts

---

## Critical Issues to Address

### 1. Sabonis Regression (Priority: High)

**Problem**: Sabonis jumped from 22.80% to 80.22% - Bag Check Gate not working

**Root Cause**: `ISO_FREQUENCY` and `PNR_HANDLER_FREQUENCY` are missing (N/A). Code falls back to `CREATION_VOLUME_RATIO` as proxy, but Sabonis's `CREATION_VOLUME_RATIO` (0.217) is above 0.10 threshold, so gate doesn't apply.

**Issue**: `CREATION_VOLUME_RATIO` is not a good proxy for self-created frequency. Sabonis has high creation volume but it's system-based (DHOs, cuts), not self-created.

**Fix Needed**: Improve Bag Check Gate logic when ISO/PNR data is missing:
- Option A: Use a different proxy (e.g., check if player has high creation volume but low isolation efficiency)
- Option B: Flag missing data and apply conservative gate
- Option C: Collect ISO/PNR data for all players

**Files to Modify**: `src/nba_data/scripts/predict_conditional_archetype.py` - Bag Check Gate section (lines 518-558)

---

### 2. Poole Case - Threshold Adjustment (Priority: Medium)

**Problem**: Poole still at 84.23% (expected <55%). Playoff Volume Tax not triggering.

**Root Cause**: Poole's open shot frequency (0.2814) is at 66th percentile, below 75th percentile threshold (0.3234).

**Fix Options**:
- Lower threshold to 70th percentile
- Use a different metric to identify system merchants
- Increase tax multiplier for borderline cases

**Files to Modify**: `src/nba_data/scripts/predict_conditional_archetype.py` - Playoff Volume Tax section

---

### 3. Haliburton Case - Alternative Signals (Priority: Medium)

**Problem**: Haliburton improved from 27.44% to 49.23% but still below 65% threshold.

**Root Cause**: 
- Pressure resilience (0.409) below 80th percentile (0.538)
- Not low volume (CREATION_VOLUME_RATIO = 0.737, above 25th percentile)
- Flash Multiplier doesn't apply (designed for "low volume + elite efficiency" cases)

**Fix Options**:
- Lower pressure resilience threshold (80th → 75th or 70th percentile)
- Investigate alternative signals for Haliburton's profile
- Consider that Haliburton may not fit the "Flash Multiplier" pattern (he's high volume, not low volume)

**Files to Review**: `src/nba_data/scripts/predict_conditional_archetype.py` - Flash Multiplier section

---

### 4. Threshold Recalibration (Priority: Low)

**Consideration**: Current thresholds (65%/55%) were calibrated on incomplete dataset (1,220 players). Now we have full dataset (4,473 players). Thresholds shifted, causing some cases to fail.

**Question**: Should we recalibrate thresholds based on full dataset, or accept that some cases will fail with more accurate thresholds?

**Action**: Review failing cases and determine if threshold adjustment is needed or if failures are legitimate.

---

## Recommended Action Order

1. **Investigate Sabonis Bag Check Gate** (High Priority)
   - This is a regression that needs immediate attention
   - Fix will likely improve pass rate

2. **Test threshold adjustments** (Medium Priority)
   - Lower Playoff Volume Tax threshold to 70th percentile (test Poole)
   - Lower Pressure Resilience threshold to 75th percentile (test Haliburton)
   - Run validation suite after each change

3. **Re-evaluate failing cases** (Medium Priority)
   - Determine if failures are legitimate or threshold issues
   - Consider if model needs retraining with full dataset

---

## Key Files for Next Developer

**Start Here**:
- `CURRENT_STATE.md` - Complete current state with Phase 3.7 results
- `results/phase3_7_data_fix_impact.md` - Impact analysis
- `results/haliburton_pressure_investigation.md` - Data completeness investigation

**Code to Modify**:
- `src/nba_data/scripts/predict_conditional_archetype.py` - Bag Check Gate, Playoff Volume Tax, Flash Multiplier

**Test Suite**:
- `test_latent_star_cases.py` - Run after each fix to validate improvements

---

## Data Files

**Updated**:
- `results/pressure_features.csv` - Now includes 4,473 rows (up from 1,220)
- `results/latent_star_test_cases_results.csv` - Latest test results
- `results/latent_star_test_cases_report.md` - Latest test report

---

**Status**: Ready for next developer to continue with follow-up fixes.

