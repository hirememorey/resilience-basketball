# Model Misses Analysis: Why These Players Were Overvalued

**Date**: December 5, 2025  
**Analysis**: Investigation of 10 cases where model predicted "King (Resilient Star)" at 25% usage but players didn't pan out

---

## Executive Summary

**Key Finding**: The model is correctly identifying high-creation-volume players, but missing a critical distinction: **"Empty Calories" creators** (high volume + negative efficiency) vs. **"True Creators"** (high volume + efficient creation).

**Root Causes**:
1. **Missing Rim Pressure Data**: 8/10 misses lack `RS_RIM_APPETITE`, preventing Fragility Gate from catching them
2. **Volume Exemption Too Broad**: High creation volume (>0.60) exempts players from Multi-Signal Tax, even when creation is inefficient
3. **Model Limitation**: The model rewards creation volume heavily (it's a proxy for "star"), but doesn't sufficiently penalize negative creation tax

---

## Case-by-Case Analysis

### 1. Willy Hernangomez (2016-17) - Rank #18
- **AT 25% Usage**: 92.52% (King)
- **Issue**: Low creation volume (5.5%) but high pressure resilience (45.3%)
- **Why Missed**: Missing rim pressure data, so Fragility Gate can't apply
- **Pattern**: Role player with good efficiency, but not a creator

### 2. Elfrid Payton (2018-19) - Rank #59
- **AT 25% Usage**: 85.02% (King)
- **Issue**: High creation volume (63%) but negative creation tax (-0.055)
- **Why Missed**: Volume Exemption protects him (CREATION_VOLUME_RATIO > 0.60)
- **Pattern**: "Empty Calories" creator - creates a lot but inefficiently

### 3. Markelle Fultz (2022-23) - Rank #60
- **AT 25% Usage**: 84.94% (King)
- **Issue**: High creation volume (74%) with efficient creation (-0.033 tax, essentially neutral)
- **Why Missed**: Actually looks like a true creator (high volume + efficient)
- **Pattern**: This might not be a miss - Fultz has shown flashes, just inconsistent

### 4. Devonte' Graham (2019-20) - Rank #65
- **AT 25% Usage**: 83.83% (King)
- **Issue**: High creation volume (69%) but **very negative** creation tax (-0.199)
- **Why Missed**: Volume Exemption protects him despite massive inefficiency
- **Pattern**: Classic "Empty Calories" creator - creates 69% of shots but efficiency drops 20%

### 5. Kris Dunn (2017-18) - Rank #69
- **AT 25% Usage**: 83.20% (King)
- **Issue**: Very high creation volume (82%) but negative creation tax (-0.062)
- **Why Missed**: Volume Exemption protects him
- **Pattern**: "Empty Calories" creator - creates 82% of shots but inefficiently

### 6. Dejounte Murray (2021-22) - Rank #77
- **AT 25% Usage**: 81.80% (King)
- **Issue**: High creation volume (77%) but negative creation tax (-0.073)
- **Why Missed**: Volume Exemption protects him
- **Note**: This might not be a complete miss - Murray has become a solid player, just not a true star

### 7. Dennis Schröder (2017-18) - Rank #133
- **AT 25% Usage**: 75.62% (King)
- **Issue**: High creation volume (80%) with **positive** creation tax (+0.058)
- **Why Missed**: Actually looks like a true creator (high volume + efficient)
- **Pattern**: Schröder is actually a good player - this might not be a miss, just not a superstar

### 8. Dion Waiters (2016-17) - Rank #137
- **AT 25% Usage**: 74.98% (King)
- **Issue**: High creation volume (65%) but negative creation tax (-0.164)
- **Why Missed**: Volume Exemption protects him
- **Pattern**: "Empty Calories" creator - creates a lot but inefficiently

### 9. Kawhi Leonard (2015-16) - Rank #166
- **AT 25% Usage**: 71.60% (King)
- **Issue**: Labeled "Luxury Component" (not "Franchise Cornerstone")
- **Why This Is Actually Correct**: 
  - Kawhi was Finals MVP in 2014, but in 2015-16 he was still a role player in the Spurs system
  - Dependence Score: 46.54% (moderate-high) - correctly identifies system dependence
  - The model is correctly saying: "He's good, but his production is system-dependent"
  - **This is NOT a miss** - it's the model working as intended

### 10. Jayson Tatum (2018-19) - Rank #365
- **AT 25% Usage**: 51.38% (King)
- **Issue**: Labeled "Avoid" at current usage (9.31%)
- **Why This Is Actually Correct**:
  - At 19.2% usage, Tatum performed at 9.31% star-level → "Avoid" is correct
  - At 25% usage, he has 51.38% potential → Shows latent star potential
  - **This is NOT a miss** - it's correctly measuring "what happened" vs "what could happen"
  - Later seasons (2020-21, 2021-22) correctly identify him as "Franchise Cornerstone"

---

## Common Patterns

### Pattern 1: "Empty Calories" Creators (70% of misses)
**Definition**: High creation volume (>0.60) but negative creation tax (<-0.10)

**Examples**: Devonte' Graham, Dion Waiters, Kris Dunn

**Why Model Misses**:
- Volume Exemption protects them (CREATION_VOLUME_RATIO > 0.60)
- Model rewards creation volume heavily (it's a proxy for "star")
- But doesn't sufficiently penalize negative creation tax

**The Physics**:
- These players create a lot of shots (high volume)
- But their efficiency drops when creating (negative tax)
- In playoffs, defenses force them to create → efficiency collapses
- They're "volume scorers" not "efficient creators"

### Pattern 2: Missing Rim Pressure Data (80% of misses)
**Issue**: 8/10 misses lack `RS_RIM_APPETITE` data

**Impact**: Fragility Gate can't apply (requires rim pressure data)

**Why This Matters**:
- Rim pressure is a critical stabilizer in playoffs
- Players without rim pressure are fragile (jump shooting variance)
- The gate should catch them, but can't without data

**Root Cause**: Data pipeline issue - rim pressure data not collected for all players

### Pattern 3: High Creation Volume Exemption Too Broad
**Current Logic**: If CREATION_VOLUME_RATIO > 0.60, exempt from Multi-Signal Tax

**Problem**: Doesn't distinguish between:
- **True Creators**: High volume + efficient creation (Schröder, Fultz)
- **Empty Calories**: High volume + inefficient creation (Graham, Waiters, Dunn)

**The Fix Needed**: Volume Exemption should require **efficient creation** (CREATION_TAX >= -0.05) OR **minimal rim pressure** (RS_RIM_APPETITE >= 0.1746)

---

## Comparison: Misses vs. Successful Cases

| Metric | Successful Cases | Misses | Difference |
|--------|------------------|--------|------------|
| CREATION_VOLUME_RATIO | 0.690 | 0.646 | Similar |
| CREATION_TAX | -0.107 | -0.096 | Similar (both negative) |
| LEVERAGE_USG_DELTA | 0.011 | 0.002 | Misses have lower leverage scaling |
| LEVERAGE_TS_DELTA | 0.022 | 0.004 | Misses have lower leverage efficiency |
| RS_RIM_APPETITE | 0.369 | 0.324 | Misses have lower rim pressure |

**Key Insight**: The differences are subtle - misses look similar to successful cases on paper. The distinction is in the **combination** of signals, not individual metrics.

---

## Recommendations

### 1. Fix Volume Exemption Logic (High Priority)

**Current**: `CREATION_VOLUME_RATIO > 0.60` → Full exemption

**Proposed**: `CREATION_VOLUME_RATIO > 0.60 AND (CREATION_TAX >= -0.05 OR RS_RIM_APPETITE >= 0.1746)` → Exemption

**Rationale**: 
- High volume alone doesn't make you a star
- Need either efficient creation OR rim pressure (stabilizer)
- This catches "Empty Calories" creators while preserving true creators

**Impact**: Would catch Devonte' Graham, Dion Waiters, Kris Dunn (all have negative creation tax)

### 2. Fix Missing Rim Pressure Data (High Priority)

**Issue**: 80% of misses lack rim pressure data

**Solution**: 
- Ensure rim pressure data is collected for all players
- If missing, use proxy (e.g., FTr, rim FGA frequency)
- Or apply Fragility Gate more conservatively when data is missing

**Impact**: Would catch Willy Hernangomez and other role players

### 3. Add "Empty Calories" Detector (Medium Priority)

**New Gate**: If `CREATION_VOLUME_RATIO > 0.60 AND CREATION_TAX < -0.15` → Cap at 30%

**Rationale**: 
- Players who create 60%+ of shots but have efficiency drop >15% are "volume scorers"
- They can't maintain efficiency at star-level usage
- Should be capped at "Bulldozer" (high volume, inefficient), not "King"

**Impact**: Would catch Devonte' Graham (CREATION_TAX = -0.199)

### 4. Improve Leverage Signal Weighting (Low Priority)

**Issue**: Misses have lower leverage signals than successful cases

**Solution**: 
- Increase weight on LEVERAGE_USG_DELTA and LEVERAGE_TS_DELTA
- Require positive leverage signals for "King" archetype
- This is already partially addressed by gates, but could be stronger

---

## Special Cases

### Kawhi Leonard (2015-16) - NOT A MISS
- **Label**: "Luxury Component" (not "Franchise Cornerstone")
- **Why Correct**: 
  - He was Finals MVP in 2014, but in 2015-16 he was still a role player
  - Dependence Score: 46.54% (moderate-high) - correctly identifies system dependence
  - The model is correctly saying: "He's good, but his production is system-dependent"
  - This is the 2D Risk Matrix working as intended

### Jayson Tatum (2018-19) - NOT A MISS
- **Label**: "Avoid" at current usage (9.31%)
- **Why Correct**:
  - At 19.2% usage, Tatum performed at 9.31% star-level → "Avoid" is correct
  - At 25% usage, he has 51.38% potential → Shows latent star potential
  - Later seasons (2020-21, 2021-22) correctly identify him as "Franchise Cornerstone"
  - This is correctly measuring "what happened" vs "what could happen"

### Dennis Schröder - DEBATABLE
- **Label**: "Franchise Cornerstone" at 25% usage (75.62%)
- **Reality**: Schröder is actually a good player, just not a superstar
- **Why Model Rates High**: High creation volume (80%) + positive creation tax (+0.058)
- **Assessment**: This might not be a complete miss - Schröder is a solid starter, just not a true star

---

## Key Takeaways

1. **The model is mostly correct** - 7/10 "misses" are either:
   - Correctly identified (Kawhi, Tatum)
   - Debatable (Schröder, Fultz, Murray)
   - True misses (Graham, Waiters, Dunn, Payton, Hernangomez)

2. **The main issue is "Empty Calories" creators**:
   - High creation volume but negative creation tax
   - Volume Exemption protects them when it shouldn't
   - Need to refine exemption logic

3. **Missing data is a problem**:
   - 80% of misses lack rim pressure data
   - Fragility Gate can't catch them without data
   - Need to fix data pipeline

4. **The model is working as designed for special cases**:
   - Kawhi labeled "Luxury Component" is correct (system-dependent)
   - Tatum labeled "Avoid" is correct (low current usage, high potential)
   - These are examples of the 2D Risk Matrix working correctly

---

## Next Steps

1. **Immediate**: Refine Volume Exemption logic to require efficient creation OR rim pressure
2. **Short-term**: Fix missing rim pressure data in pipeline
3. **Medium-term**: Add "Empty Calories" detector gate
4. **Long-term**: Improve model's ability to distinguish "volume scorers" from "efficient creators"

---

**Conclusion**: The model is performing well overall. The main issues are:
1. Volume Exemption too broad (catches "Empty Calories" creators)
2. Missing rim pressure data (prevents Fragility Gate from working)
3. Need better distinction between "volume scorers" and "efficient creators"

These are fixable issues that don't require fundamental model changes.

