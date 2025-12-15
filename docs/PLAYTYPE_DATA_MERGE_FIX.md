# Playtype Data Merge Fix: Resolving Bag Check Gate Issue

**Date**: December 2025  
**Status**: ✅ **IMPLEMENTED**  
**Priority**: High - Fixes Mikal Bridges and other "Usage Shock" test failures

---

## Problem Statement

The Bag Check Gate was incorrectly capping latent stars like Mikal Bridges (2021-22) at 30% star-level because:

1. **Missing Data Source**: Synergy playtype data (`ISO_FREQUENCY`, `PNR_HANDLER_FREQUENCY`) was not being merged into `predictive_dataset.csv`
2. **Conservative Proxy**: When playtype data was missing, the system used a conservative proxy:
   - `SELF_CREATED_FREQ = CREATION_VOLUME_RATIO * 0.35` (for high volume > 0.15)
   - `SELF_CREATED_FREQ = CREATION_VOLUME_RATIO * 0.6` (for low volume ≤ 0.15)
3. **Impact on Low-Usage Players**: For players like Bridges with low creation volume (0.20):
   - `0.20 * 0.35 = 0.07` (7%)
   - 7% < 10% threshold → Bag Check Gate applies → Capped at 30%

**Root Cause**: The `populate_playtype_data.py` script stores data in the database, but `evaluate_plasticity_potential.py` never loads it into the predictive dataset.

---

## Solution

### Implementation

Added `fetch_playtype_metrics()` method to `StressVectorEngine` class that:

1. **Queries Database**: Loads playtype data from `player_playtype_stats` table
2. **Handles Multi-Team Players**: Sums FGA across teams for players who were traded
3. **Calculates Frequencies**:
   - `ISO_FREQUENCY = (Isolation FGA) / (Total FGA from all play types)`
   - `PNR_HANDLER_FREQUENCY = (PRBallHandler FGA) / (Total FGA from all play types)`
4. **Merges into Dataset**: Adds `ISO_FREQUENCY` and `PNR_HANDLER_FREQUENCY` columns to `predictive_dataset.csv`

### Code Changes

**File**: `src/nba_data/scripts/evaluate_plasticity_potential.py`

1. **Added imports**: `sqlite3` for database access
2. **Added database path**: `self.db_path = self.data_dir / "nba_stats.db"`
3. **New method**: `fetch_playtype_metrics(season)` - Loads and calculates playtype frequencies
4. **Updated `run()` method**: Calls `fetch_playtype_metrics()` and merges results
5. **Updated column list**: Added `ISO_FREQUENCY` and `PNR_HANDLER_FREQUENCY` to `cols_to_keep`

---

## Expected Impact

### Before Fix
- **Mikal Bridges (2021-22)**: 30.00% star-level (capped by Bag Check Gate)
  - Proxy: `0.20 * 0.35 = 0.07` (7%) < 10% threshold
  - Model prediction before gates: 93.43% (correct!)

### After Fix
- **Mikal Bridges (2021-22)**: Should show ≥65% star-level
  - Explicit playtype data: `ISO_FREQUENCY + PNR_HANDLER_FREQUENCY` > 10%
  - Bag Check Gate no longer applies
  - Model prediction (93.43%) is preserved

### Other Affected Cases
- **Tyrese Haliburton (2021-22)**: May also benefit if missing playtype data was the issue
- **Desmond Bane (2021-22)**: May benefit if secondary creator pattern is captured in playtype data

---

## Data Requirements

### Prerequisites
1. **Database must exist**: `data/nba_stats.db`
2. **Playtype data must be populated**: Run `populate_playtype_data.py` for all seasons
3. **Data must be for Regular Season**: The query filters for `season_type = 'Regular Season'`

### Data Coverage
- The fix gracefully handles missing data:
  - If database doesn't exist: Logs warning, continues without playtype data
  - If no playtype data for season: Logs warning, fills with NaN
  - If player has no ISO/PNR plays: Sets frequency to 0.0 (expected for role players)

---

## Validation Steps

1. **Regenerate Predictive Dataset**:
   ```bash
   python src/nba_data/scripts/evaluate_plasticity_potential.py
   ```

2. **Verify Playtype Data is Present**:
   ```python
   import pandas as pd
   df = pd.read_csv('results/predictive_dataset.csv')
   print(f"ISO_FREQUENCY coverage: {df['ISO_FREQUENCY'].notna().sum()} / {len(df)}")
   print(f"PNR_HANDLER_FREQUENCY coverage: {df['PNR_HANDLER_FREQUENCY'].notna().sum()} / {len(df)}")
   ```

3. **Test Mikal Bridges Case**:
   ```bash
   python test_latent_star_cases.py
   ```
   - Expected: Mikal Bridges should now pass (≥65% star-level)

4. **Check Bag Check Gate Logic**:
   - Verify that `predict_conditional_archetype.py` uses explicit playtype data when available
   - Verify that proxy logic is only used as fallback

---

## Key Principles Applied

1. **Fix Root Cause, Not Symptom**: Instead of adjusting the proxy multiplier, we fixed the missing data source
2. **Graceful Degradation**: System continues to work if playtype data is missing (falls back to proxy)
3. **Data Completeness**: Explicit data > Proxy estimates (first principles)

---

## Related Files

- `src/nba_data/scripts/evaluate_plasticity_potential.py` - Main implementation
- `src/nba_data/scripts/populate_playtype_data.py` - Data collection script
- `src/nba_data/scripts/predict_conditional_archetype.py` - Uses playtype data in Bag Check Gate
- `src/nba_data/db/schema.py` - Database schema for `player_playtype_stats` table

---

## Next Steps

1. ✅ **Implementation Complete** - Code changes merged
2. ⏳ **Regenerate Dataset** - Run `evaluate_plasticity_potential.py` to create new dataset with playtype data
3. ⏳ **Validate Fix** - Run test suite to verify Mikal Bridges case passes
4. ⏳ **Update Documentation** - Update `CURRENT_STATE.md` and `NEXT_STEPS.md` with fix status

---

**Status**: ✅ **IMPLEMENTATION COMPLETE**  
**Next Action**: Regenerate `predictive_dataset.csv` and validate fix














