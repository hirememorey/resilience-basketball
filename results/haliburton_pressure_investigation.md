# Haliburton Pressure Resilience Missing Data Investigation

**Date**: December 4, 2025  
**Issue**: `RS_PRESSURE_RESILIENCE` is missing (NaN) for Tyrese Haliburton (2021-22)  
**Impact**: Flash Multiplier cannot trigger for Haliburton, causing test case failure

---

## Executive Summary

**Root Cause**: Haliburton is completely missing from `pressure_features.csv` because the calculation script uses an **INNER JOIN** between Regular Season (RS) and Playoff (PO) data. Haliburton has RS data but no PO data (his teams didn't make playoffs in 2021-22), so he gets filtered out entirely.

**Solution**: Change the merge from `how='inner'` to `how='left'` in `calculate_shot_difficulty_features.py` to preserve RS data even when PO data is missing.

---

## Investigation Details

### 1. Data Availability Check

**Raw Shot Quality Data** (`data/shot_quality_aggregates_2021-22.csv`):
- ✅ **Haliburton HAS RS data**: 1 row with Regular Season data
  - `FGA_0_2`: 0.58 (per game)
  - `EFG_0_2`: 0.409
  - `GP`: 76 games
- ❌ **Haliburton MISSING PO data**: No playoff rows found

**Pressure Features Output** (`results/pressure_features.csv`):
- ❌ **Haliburton completely missing**: Not in the file at all
- File contains 1,220 player-seasons (only players with BOTH RS and PO data)

### 2. Root Cause Analysis

**File**: `src/nba_data/scripts/calculate_shot_difficulty_features.py`  
**Line**: 187

```python
# Current code (PROBLEM):
merged = pd.merge(rs_df, po_df, on=['PLAYER_ID', 'PLAYER_NAME', 'SEASON'], how='inner')
```

**The Problem**:
- `how='inner'` only keeps players who have data in BOTH RS and PO
- Haliburton was traded from Sacramento to Indiana in February 2022
- Neither team made the playoffs in 2021-22
- Result: Haliburton has RS data but no PO data → gets filtered out completely

**Impact on Features**:
- `RS_PRESSURE_RESILIENCE` only needs RS data (can be calculated from RS alone)
- `PRESSURE_RESILIENCE_DELTA` needs both RS and PO (can be NaN if PO missing)
- Current implementation: If PO missing → entire row removed → RS features also lost

### 3. Data Loss Analysis

**2021-22 Season**:
- Players with RS data: ~400+ (all players who played)
- Players with PO data: ~200+ (only playoff participants)
- Players with BOTH (current INNER JOIN): ~200
- **Players lost (RS only)**: ~200+ players, including Haliburton

**Impact on Model**:
- Many players who didn't make playoffs are missing RS pressure features
- This affects latent star detection (Use Case B) - exactly the use case where we need RS features for players who haven't had playoff opportunity yet

### 4. Why This Matters for Haliburton

**Haliburton's Situation (2021-22)**:
- Age: 22
- Usage: 18.4% (low - role player)
- Team: Traded mid-season, neither team made playoffs
- **This is exactly the "latent star" scenario**: Young player with low usage, no playoff opportunity yet

**Flash Multiplier Logic**:
- Requires `RS_PRESSURE_RESILIENCE > 80th percentile` as alternative flash signal
- But `RS_PRESSURE_RESILIENCE` is NaN because Haliburton is missing from pressure_features.csv
- Result: Flash Multiplier cannot trigger → test case fails

---

## Solution

### Fix: Change INNER JOIN to LEFT JOIN

**File**: `src/nba_data/scripts/calculate_shot_difficulty_features.py`  
**Line**: 187

**Change**:
```python
# OLD (PROBLEM):
merged = pd.merge(rs_df, po_df, on=['PLAYER_ID', 'PLAYER_NAME', 'SEASON'], how='inner')

# NEW (FIX):
merged = pd.merge(rs_df, po_df, on=['PLAYER_ID', 'PLAYER_NAME', 'SEASON'], how='left')
```

**Additional Changes Needed**:

1. **Handle PO columns as NaN when missing**:
   - PO columns will be NaN for players without playoff data (expected)
   - Delta calculations already handle this with `np.where(merged[rs_col].notna() & merged[po_col].notna(), ...)`

2. **Update PO_TOTAL_VOLUME filter**:
   - Current: `filtered_df = final_df[final_df['PO_TOTAL_VOLUME'] >= 30]`
   - New: Only apply filter to players with PO data, or make it optional
   - Option A: `filtered_df = final_df[(final_df['PO_TOTAL_VOLUME'] >= 30) | final_df['PO_TOTAL_VOLUME'].isna()]`
   - Option B: Separate filter - keep all RS data, only filter PO data for players who have it

3. **Update delta calculations** (already handled):
   - Line 191-192: Already uses subtraction which will result in NaN if PO is NaN
   - Clock deltas (lines 221-224): Already uses `np.where` with `notna()` checks

### Expected Impact

**After Fix**:
- ✅ Haliburton will have `RS_PRESSURE_RESILIENCE` calculated from RS data
- ✅ `PRESSURE_RESILIENCE_DELTA` will be NaN (expected - no PO data)
- ✅ Flash Multiplier can now trigger if `RS_PRESSURE_RESILIENCE > 80th percentile`
- ✅ ~200+ additional players will have RS pressure features available

**Data Quality**:
- RS features: Available for all players with RS shot quality data
- PO features: Available only for players who made playoffs (expected)
- Delta features: NaN for players without PO data (expected and handled)

---

## Verification Steps

1. **Apply the fix** (change `how='inner'` to `how='left'`)
2. **Re-run** `calculate_shot_difficulty_features.py`
3. **Verify**:
   - Haliburton appears in `pressure_features.csv`
   - `RS_PRESSURE_RESILIENCE` is calculated (not NaN)
   - `PRESSURE_RESILIENCE_DELTA` is NaN (expected - no PO data)
   - Total rows in file increases (~200+ more players)
4. **Re-test** Flash Multiplier on Haliburton case

---

## Related Issues

This same issue likely affects:
- Other players who didn't make playoffs in their test seasons
- Players traded mid-season to non-playoff teams
- Young players with low usage (exactly the latent star detection use case)

**Recommendation**: Apply this fix as it's a fundamental data completeness issue that affects the core use case (latent star detection).

---

## Files to Modify

1. **`src/nba_data/scripts/calculate_shot_difficulty_features.py`**:
   - Line 187: Change `how='inner'` to `how='left'`
   - Line 255: Update PO_TOTAL_VOLUME filter to handle NaN

2. **Re-run data pipeline**:
   ```bash
   python src/nba_data/scripts/calculate_shot_difficulty_features.py
   ```

3. **Re-test**:
   ```bash
   python test_latent_star_cases.py
   ```

---

**Status**: Root cause identified. Fix ready for implementation.

