# Failure Categorization Summary

**Date**: January 3, 2026  
**Baseline Pass Rate**: 5/12 (41.7%)  
**Total Failures**: 7

---

## Category 1: Path Formula Issues (Weights/Thresholds)

**Count**: 4 players  
**Players**: LeBron James, Stephen Curry, Giannis Antetokounmpo, Kevin Durant

### LeBron James (2015-16)
- **Issue**: Drive-Kick path scoring 59.3 (expected 85+)
- **Root Cause**: Formula not correctly translating drive volume and outcomes into score
- **Fix Strategy**: Review `drive_kick.py` sub-component calculations and thresholds

### Stephen Curry (2016-17)
- **Issue**: Gravity path scoring 60.1 (expected 85+)
- **Root Cause**: Formula not capturing true gravity impact; also missing `screen_ast` data
- **Fix Strategy**: Review `gravity.py` weights/thresholds AND fix data collection

### Giannis Antetokounmpo (2020-21)
- **Issue**: Drive-Kick path scoring 62.8 (expected 85+); also Gravity incorrectly identified as primary mode
- **Root Cause**: Drive-Kick under-scoring AND Gravity over-scoring (flawed movement proxy)
- **Fix Strategy**: Fix both `drive_kick.py` and `gravity.py` formulas

### Kevin Durant (2018-19)
- **Issue**: ISO path scoring 72.9 (just below 75.0 elite threshold)
- **Root Cause**: Minor calibration issue; architecture is correct
- **Fix Strategy**: Fine-tune ISO path thresholds or weights

---

## Category 2: Missing Data (Field Not Captured)

**Count**: 2 players  
**Players**: Ja Morant, Donovan Mitchell

### Ja Morant (2021-22)
- **Issue**: Drive-Kick path returning 0.0 due to missing tracking data
- **Root Cause**: `drives_per_game`, `drive_pts`, `drive_ast` not in dataset for this season
- **Fix Strategy**: Investigate data collection/merge pipeline for 2021-22 tracking data

### Donovan Mitchell (2021-22)
- **Issue**: Same missing Drive-Kick data, but less critical since ISO is his true engine
- **Root Cause**: Same data collection issue as Ja Morant
- **Fix Strategy**: Same as Ja Morant (data pipeline fix)

---

## Category 3: Component Architecture Issue

**Count**: 1 player  
**Player**: Nikola Jokić

### Nikola Jokić (2022-23)
- **Issue**: C3 (Difficulty Embrace) scoring 46.1, dragging CII down despite elite C1 (87.1)
- **Root Cause**: `calculate_difficulty_embrace_bare` does not include Hub path logic (unlike C1)
- **Fix Strategy**: Refactor C3 to include `MAX(Perimeter, Hub)` logic, matching C1 architecture

---

## Category 4: Threshold/Weight Calibration

**Count**: 1 player (overlap with Category 1)  
**Player**: Donovan Mitchell

### Donovan Mitchell (2021-22)
- **Issue**: Elite C1 (78.0) and C2 (90.0) but CII (69.2) just below 74.0 threshold
- **Root Cause**: Component weights or CII threshold may be too strict for players with elite C1+C2 but "good" C3-C5
- **Fix Strategy**: Review component weights or consider if 74.0 threshold is appropriate

---

## Summary Statistics

| Category | Count | Priority | Fix Complexity |
|----------|-------|----------|----------------|
| Path Formula Issues | 4 | High | Medium-High |
| Missing Data | 2 | Medium | Low (data pipeline) |
| Component Architecture | 1 | Critical | Medium |
| Threshold Calibration | 1 | Low | Low |

---

## Recommended Fix Order

1. **Phase 3.1: Fix Component Architecture** (Jokić C3 issue)
   - **Why First**: This is a fundamental architectural flaw that affects all hub creators
   - **Impact**: Will fix Jokić and potentially other hub players

2. **Phase 3.2: Fix Drive-Kick Path Formula** (LeBron, Giannis)
   - **Why Second**: Affects 2 critical validation cases
   - **Impact**: Will fix LeBron and Giannis (primary failures)

3. **Phase 3.3: Fix Gravity Path Formula** (Curry, Giannis)
   - **Why Third**: Affects Curry and corrects Giannis misclassification
   - **Impact**: Will fix Curry and prevent Gravity path from incorrectly scoring force players

4. **Phase 3.4: Fine-Tune ISO Path** (Durant)
   - **Why Fourth**: Minor calibration issue
   - **Impact**: Will fix Durant (narrow miss)

5. **Phase 3.5: Investigate Data Collection** (Ja Morant, Mitchell)
   - **Why Last**: Data pipeline issue, not model issue
   - **Impact**: Will enable proper Drive-Kick scoring for these players

6. **Phase 3.6: Review Thresholds/Weights** (Mitchell borderline case)
   - **Why Last**: May not need fixing if other fixes resolve it
   - **Impact**: Addresses borderline classification cases

---

## Next Steps

Proceed to **Phase 3: Principled Adjustments** following the recommended fix order above. Each fix must:
1. Have theoretical justification (not "this makes Player X pass")
2. Be tested on ALL validation players (not just the failure case)
3. Be documented with impact analysis before implementation

