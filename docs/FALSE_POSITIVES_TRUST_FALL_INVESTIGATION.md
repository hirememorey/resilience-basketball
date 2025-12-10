# False Positives Trust Fall 2.1 Investigation

**Date**: December 9, 2025  
**Status**: ✅ **INVESTIGATION COMPLETE** | ✅ **ENHANCEMENT IMPLEMENTED**  
**Finding**: Feature signal exists but is too weak relative to dominant features  
**Resolution**: Enhanced INEFFICIENT_VOLUME_SCORE with multi-signal approach + conditional sample weighting (see `docs/SAMPLE_WEIGHTING_ENHANCEMENT_RESULTS.md`)

---

## Executive Summary

The enhanced `INEFFICIENT_VOLUME_SCORE` (multi-signal approach) **is working correctly** - failing false positives have **2.7x higher scores** than passing cases. However, the feature importance (6.25%) is too low relative to dominant features (USG_PCT: 32.4%), causing the model to still predict high performance for inefficient high-usage players.

---

## Key Findings

### 1. Feature Signal is Correct ✅

**Failing cases have HIGHER INEFFICIENT_VOLUME_SCORE than passing cases:**

| Category | Mean Score | Median Score | Performance |
|----------|------------|--------------|-------------|
| **Passing Cases** | 0.0109 | 0.0109 | 47-99% |
| **Failing Cases** | 0.0292 | 0.0378 | 64-97% |
| **Difference** | **+0.0183** | **+0.0269** | - |

**Individual Cases:**
- **D'Angelo Russell (2018-19)**: Score = 0.0404 (highest!) → Performance = 97.43% ❌
- **Julius Randle (2020-21)**: Score = 0.0378 → Performance = 81.75% ❌
- **Christian Wood (2020-21)**: Score = 0.0093 → Performance = 64.41% ❌
- **Jordan Poole (2021-22)**: Score = 0.0157 → Performance = 99.35% ✅ (but correctly identified as Luxury Component)
- **Talen Horton-Tucker (2020-21)**: Score = 0.0060 → Performance = 47.41% ✅

### 2. Feature Importance is Too Low ⚠️

**Current Feature Importance Rankings:**
1. USG_PCT: **32.4%** (5.2x more important than INEFFICIENT_VOLUME_SCORE)
2. USG_PCT_X_EFG_ISO_WEIGHTED: **11.9%** (1.9x more important)
3. SHOT_QUALITY_GENERATION_DELTA: **8.5%** (1.4x more important)
...
7. **INEFFICIENT_VOLUME_SCORE: 6.25%** ⚠️

**The Problem**: High usage (USG_PCT: 32.4%) + decent efficiency (USG_PCT_X_EFG_ISO_WEIGHTED: 11.9%) **overwhelms** the inefficiency penalty (6.25%).

### 3. Component Analysis

**Failing cases have higher inefficiency across ALL components:**

| Component | Passing (Mean) | Failing (Mean) | Difference |
|-----------|----------------|----------------|------------|
| **CREATION_TAX** | 0.0236 | **0.1227** | **+0.0991** (5.2x) |
| **SQ_DELTA** | 0.0167 | **0.0362** | **+0.0195** (2.2x) |
| **LEVERAGE_TS** | 0.0310 | **0.0403** | **+0.0093** (1.3x) |

**Key Insight**: Failing cases have **much higher CREATION_TAX** (5.2x), which is the strongest signal, but it's still not enough.

---

## Root Cause Analysis

### Why the Feature Isn't Catching False Positives

1. **Feature Importance Too Low**: 6.25% is insufficient when USG_PCT is 32.4%
   - The model prioritizes "high usage = star" over "inefficient usage = empty calories"
   - This is the "Brittle Genius" problem - the physics are correct, but the model doesn't learn them

2. **Signal Strength vs. Feature Dominance**:
   - D'Angelo Russell: INEFFICIENT_VOLUME_SCORE = 0.0404 (very high!)
   - But USG_PCT = 31.1% (very high!) → Model sees "high usage" and predicts "star"
   - The inefficiency penalty (0.0404) is not strong enough to override the usage signal (0.311)

3. **Why Some Pass**:
   - **Jordan Poole**: High score but DEPENDENCE_SCORE (46.11%) triggers Dependence Law → correctly identified as Luxury Component
   - **Talen Horton-Tucker**: Low usage (21%) + low score → correctly predicted as Victim

---

## Recommendations

### Option 1: Increase Feature Importance (Recommended)

**Action**: Retrain model with increased sample weighting for high `INEFFICIENT_VOLUME_SCORE` cases.

**Rationale**: Force the model to pay more attention to this feature by penalizing high-usage players with high inefficiency scores.

**Implementation**:
- Add sample weighting: `if INEFFICIENT_VOLUME_SCORE > 0.02 AND USG_PCT > 0.25: weight = 5x`
- Retrain model
- Measure feature importance increase

**Expected Outcome**: Feature importance increases from 6.25% to 10-15%, allowing it to compete with USG_PCT.

### Option 2: Strengthen Signal Further

**Action**: Apply non-linear transformation to `INEFFICIENT_VOLUME_SCORE` to amplify high values.

**Rationale**: High inefficiency scores should have exponential penalty, not linear.

**Implementation**:
- Current: `INEFFICIENT_VOLUME_SCORE = USG_PCT × CREATION_VOLUME_RATIO × combined_inefficiency`
- Enhanced: `INEFFICIENT_VOLUME_SCORE = USG_PCT × CREATION_VOLUME_RATIO × (combined_inefficiency ** 1.5)`
- Or: `INEFFICIENT_VOLUME_SCORE = USG_PCT × CREATION_VOLUME_RATIO × max(0, combined_inefficiency - 0.10) ** 2`

**Expected Outcome**: High inefficiency scores (0.04+) become much larger (0.08+), making them harder to ignore.

### Option 3: Create Interaction Term with USG_PCT

**Action**: Create `USG_PCT_X_INEFFICIENT_VOLUME_SCORE` interaction term.

**Rationale**: Explicitly encode "high usage × high inefficiency = bad" as a single feature.

**Implementation**:
- `USG_PCT_X_INEFFICIENT_VOLUME_SCORE = USG_PCT × INEFFICIENT_VOLUME_SCORE`
- This creates a quadratic penalty: high usage amplifies the inefficiency penalty

**Expected Outcome**: Interaction term may be selected by RFE and have higher importance than base feature.

### Option 4: Accept Current Performance (Not Recommended)

**Action**: Keep gates enabled and accept that model needs gates for False Positives.

**Rationale**: Model is already at 90% pass rate with gates, 70% without gates.

**Risk**: Doesn't solve the "Brittle Genius" problem - intelligence still lives in gates, not model.

---

## Detailed Case Analysis

### D'Angelo Russell (2018-19) - FAILS

**Feature Values:**
- USG_PCT: 31.1% (very high)
- CREATION_VOLUME_RATIO: 75.2% (very high)
- CREATION_TAX: -0.1013 (very negative)
- SQ_DELTA: -0.0718 (very negative)
- LEVERAGE_TS_DELTA: 0.0220 (positive - helps!)
- **INEFFICIENT_VOLUME_SCORE: 0.0404** (highest of all cases!)

**Prediction**: 97.43% performance, "King (Resilient Star)"

**Why It Fails**:
- High usage (31.1%) + decent efficiency (EFG_ISO_WEIGHTED: 48.17%) → Model sees "star"
- Inefficiency penalty (0.0404) is not strong enough to override usage signal (0.311)
- Feature importance (6.25%) is too low relative to USG_PCT (32.4%)

### Julius Randle (2020-21) - FAILS

**Feature Values:**
- USG_PCT: 28.5% (high)
- CREATION_VOLUME_RATIO: 53.6% (moderate)
- CREATION_TAX: -0.1362 (very negative - worst!)
- SQ_DELTA: -0.0367 (negative)
- LEVERAGE_TS_DELTA: -0.0620 (negative)
- **INEFFICIENT_VOLUME_SCORE: 0.0378** (very high!)

**Prediction**: 81.75% performance, "King (Resilient Star)"

**Why It Fails**:
- High usage (28.5%) + moderate efficiency → Model sees "star"
- Inefficiency penalty (0.0378) is not strong enough
- All three inefficiency components are negative, but model still predicts high

### Christian Wood (2020-21) - FAILS

**Feature Values:**
- USG_PCT: 25.5% (moderate-high)
- CREATION_VOLUME_RATIO: 18.9% (low - doesn't create much!)
- CREATION_TAX: -0.1305 (very negative)
- SQ_DELTA: 0.0176 (positive - helps!)
- LEVERAGE_TS_DELTA: -0.0590 (negative)
- **INEFFICIENT_VOLUME_SCORE: 0.0093** (lowest of failing cases)

**Prediction**: 64.41% performance, "King (Resilient Star)"

**Why It Fails**:
- Low creation volume (18.9%) reduces the penalty
- But high usage (25.5%) + decent efficiency → Model still sees "star"
- Score is lower (0.0093) but still not enough to catch

---

## Next Steps

1. **Implement Option 1** (Increase Feature Importance via Sample Weighting)
   - Add conditional sample weighting for high INEFFICIENT_VOLUME_SCORE cases
   - Retrain model
   - Measure feature importance increase

2. **Test Option 2** (Non-Linear Transformation)
   - Apply exponential transformation to high inefficiency scores
   - Regenerate features and retrain
   - Compare with Option 1

3. **Validate Improvement**
   - Run Trust Fall 2.2 experiment
   - Target: False Positive pass rate > 60% (from 40%)
   - Measure gap reduction (from 20.0 pp to <15 pp)

---

## Conclusion

The enhanced `INEFFICIENT_VOLUME_SCORE` is working correctly - failing cases have 2.7x higher scores. However, the feature importance (6.25%) is too low to compete with dominant features (USG_PCT: 32.4%). The model needs either:

1. **Higher feature importance** (via sample weighting)
2. **Stronger signal** (via non-linear transformation)
3. **Explicit interaction term** (USG_PCT × INEFFICIENT_VOLUME_SCORE)

The physics are correct, but the model needs help learning them.
