# Missing Data Root Cause Analysis

## Executive Summary

Using first principles, we've identified why data is missing and discovered a **critical selection bias** that filters out the exact players we're trying to identify as "latent stars."

---

## Missing Data Patterns (2020-21 Season)

| Feature | Missing % | Root Cause | Type |
|---------|-----------|------------|------|
| **USG_PCT** | 66.6% (357/536) | **Selection Bias** - MIN >= 20.0 filter | ❌ **Systematic Exclusion** |
| **LEVERAGE_USG_DELTA** | 45.3% (243/536) | Requires CLUTCH_MIN_TOTAL >= 15 | ✅ Legitimate (No Clutch Minutes) |
| **RS_PRESSURE_RESILIENCE** | 76.7% (411/536) | Requires shot quality data (defender distance) | ✅ Legitimate (Insufficient Sample) |
| **RS_FTr** | 84.7% (454/536) | Requires free throw attempts | ✅ Legitimate (Insufficient Sample) |

---

## Critical Finding: USG_PCT Selection Bias

### The Problem

**Regular Season File Filter** (`collect_regular_season_stats.py`, line 73-86):
```python
def filter_qualified_players(df):
    """Filter for qualified players (GP >= 50, MIN >= 20)."""
    qualified = df[
        (df['GP'] >= 50) & 
        (df['MIN'] >= 20.0)  # ← THIS IS THE PROBLEM
    ].copy()
```

### Case Study: Tyrese Maxey (2020-21)

- **GP**: 61 ✅ (meets >= 50 requirement)
- **MIN**: 15.3 ❌ (fails >= 20.0 requirement)
- **Result**: Excluded from `regular_season_2020-21.csv`
- **Impact**: Cannot calculate USG_PCT, filtered out before stress profile calculation

### First Principles Analysis

**The Filter's Purpose**: Exclude low-minute players who don't have meaningful sample sizes.

**The Unintended Consequence**: Also excludes **rookies and role players who haven't been given opportunity yet** - exactly the players we're trying to identify as "latent stars."

**The Selection Bias**: 
- We want to find: "High Capacity + Low Opportunity"
- We're filtering out: Players with low opportunity (MIN < 20.0)
- **This is a logic inversion** - we're excluding the target population!

### The Consultant's Insight Validated

> "Absence of evidence is not evidence of absence."

Maxey has:
- ✅ Positive CREATION_BOOST (0.0504) - elite self-creation ability
- ✅ High CREATION_VOLUME_RATIO (0.746) - can create own shots
- ✅ Complete pressure data (RS_PRESSURE_RESILIENCE = 0.531)
- ❌ Missing USG_PCT (excluded by MIN filter)

**He's being penalized for not having opportunity, not for lacking ability.**

---

## Other Missing Data: Legitimate vs. Problematic

### Legitimate Missing Data (Cannot Be Measured)

1. **LEVERAGE_USG_DELTA** (45.3% missing)
   - **Requirement**: CLUTCH_MIN_TOTAL >= 15
   - **Reason**: Player didn't play in clutch situations
   - **Solution**: Use alternative signals (e.g., Isolation EFG as proxy)

2. **RS_PRESSURE_RESILIENCE** (76.7% missing)
   - **Requirement**: Shot quality data (defender distance)
   - **Reason**: Insufficient shot attempts or data not collected
   - **Solution**: Use alternative signals (e.g., Isolation EFG as proxy)

3. **RS_FTr** (84.7% missing)
   - **Requirement**: Free throw attempts
   - **Reason**: Insufficient FTA or data not collected
   - **Solution**: Use alternative signals (e.g., Rim Appetite as proxy)

### Problematic Missing Data (Systematic Exclusion)

1. **USG_PCT** (66.6% missing)
   - **Requirement**: MIN >= 20.0 in regular season file
   - **Reason**: Selection bias - filtering out low-opportunity players
   - **Solution**: **Remove MIN filter OR use alternative source for USG_PCT**

---

## Root Cause Summary

### Why Data is Missing

1. **USG_PCT**: **Selection bias** - MIN >= 20.0 filter excludes low-opportunity players
2. **LEVERAGE_USG_DELTA**: **Legitimate** - requires clutch minutes (CLUTCH_MIN_TOTAL >= 15)
3. **RS_PRESSURE_RESILIENCE**: **Legitimate** - requires shot quality data (defender distance)
4. **RS_FTr**: **Legitimate** - requires free throw attempts

### The Fundamental Issue

**We're filtering out the target population before we can evaluate them.**

The regular season file's MIN >= 20.0 filter is designed to exclude low-minute players, but it's also excluding:
- Rookies (like Maxey in 2020-21)
- Role players who haven't been given opportunity
- Players who are exactly what we're trying to find: "High Capacity + Low Opportunity"

---

## Recommended Solutions

### 1. Fix USG_PCT Selection Bias (CRITICAL)

**Option A: Remove MIN Filter from Regular Season File**
- Pro: Captures all players, including low-opportunity ones
- Con: Includes very low-minute players with noisy stats
- **Recommendation**: Remove MIN filter, keep GP >= 50 (or lower to GP >= 20)

**Option B: Use Alternative Source for USG_PCT**
- Fetch USG_PCT directly from API for all players in predictive_dataset
- Don't rely on filtered regular_season file
- **Recommendation**: This is the better approach - keeps qualification filters separate from usage data

**Option C: Lower MIN Threshold**
- Change MIN >= 20.0 to MIN >= 10.0 or MIN >= 15.0
- Pro: Captures more low-opportunity players
- Con: Still excludes some (Maxey had 15.3 MIN)
- **Recommendation**: Not ideal - still has selection bias

### 2. Handle Legitimate Missing Data (Signal Confidence)

**For LEVERAGE_USG_DELTA, RS_PRESSURE_RESILIENCE, RS_FTr:**
- Implement "Signal Confidence" metric
- Weight features by data availability
- Use alternative signals when primary signals are missing:
  - **LEVERAGE_USG_DELTA missing** → Use Isolation EFG as proxy
  - **RS_PRESSURE_RESILIENCE missing** → Use Isolation EFG as proxy
  - **RS_FTr missing** → Use Rim Appetite as proxy

---

## Implementation Priority

1. **IMMEDIATE**: Fix USG_PCT selection bias (Option B - fetch directly from API)
2. **HIGH**: Implement Signal Confidence metric for legitimate missing data
3. **MEDIUM**: Add alternative signal proxies for missing features

---

## Key Insight

**The consultant was right**: "Absence of evidence is not evidence of absence."

Maxey is a perfect example:
- He has elite signals (positive CREATION_BOOST, high creation volume)
- He's missing USG_PCT because he was excluded by the MIN filter
- He's being penalized for not having opportunity, not for lacking ability

**The fix**: Don't filter out players before evaluating them. Use alternative sources for USG_PCT and implement Signal Confidence for legitimate missing data.

