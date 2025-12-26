# Shot Chart Collection Fix

**Date**: December 5, 2025  
**Issue**: Missing shot chart data for 1,204 players (65.1% of expanded predictions)

---

## Root Cause

The `collect_shot_charts.py` script only collected shot charts for players in `regular_season_{season}.csv`, which is filtered to players with:
- `GP >= 50` (games played)
- `MIN >= 20.0` (minutes per game)

However, the **expanded predictions** include players with:
- `Age <= 25`
- `Total MIN >= 500` (much lower threshold)

This means many young players and role players who don't meet the `GP >= 50 / MIN >= 20.0` filter were excluded from shot chart collection, even though:
1. The NBA Stats API shot chart endpoint doesn't require any filters
2. Shot chart data is available for all players who played in the NBA
3. These players are in `predictive_dataset.csv` (5,312 players vs. ~200 per season in `regular_season` files)

---

## Solution

Modified `src/nba_data/scripts/collect_shot_charts.py` to:

1. **Added `load_all_players_from_predictive_dataset()` function**:
   - Loads all players from `results/predictive_dataset.csv` for a given season
   - Includes players who don't meet the `GP >= 50 / MIN >= 20.0` filter
   - Falls back to `regular_season` files if `predictive_dataset.csv` is not available

2. **Added `--use-predictive-dataset` flag**:
   - When enabled, uses `predictive_dataset.csv` instead of `regular_season` files
   - Allows collection of shot charts for all players in the expanded predictions

3. **Fixed unreachable code bug**:
   - Removed unreachable `return pd.DataFrame()` statement in `fetch_shot_chart()`

---

## Next Steps

### 1. Re-collect Shot Charts (Required)

Run the shot chart collection script with the new flag for all seasons:

```bash
python src/nba_data/scripts/collect_shot_charts.py \
  --seasons 2015-16 2016-17 2017-18 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 2024-25 \
  --use-predictive-dataset \
  --workers 5
```

**Expected Impact**:
- Current: ~200 players per season (from `regular_season` files)
- New: ~500-600 players per season (from `predictive_dataset.csv`)
- **Total increase**: From ~2,000 to ~5,500 players with shot chart data

### 2. Re-calculate Rim Pressure Features

After collecting shot charts, re-run the rim pressure calculation:

```bash
python src/nba_data/scripts/calculate_rim_pressure.py
```

**Expected Impact**:
- Current: 1,845 players with rim pressure data
- New: ~5,000+ players with rim pressure data
- **Coverage in expanded predictions**: From 34.9% (645/1,849) to ~90%+ (1,600+/1,849)

### 3. Re-train Model (Optional)

If rim pressure data coverage improves significantly, consider re-training the model:

```bash
python src/nba_data/scripts/train_rfe_model.py
```

### 4. Re-run Expanded Predictions (Optional)

After re-calculating rim pressure features, re-run expanded predictions:

```bash
python run_expanded_predictions.py
```

---

## Expected Results

### Before Fix
- **Shot chart files**: ~200 players per season
- **Rim pressure data**: 1,845 players total
- **Coverage in expanded predictions**: 34.9% (645/1,849)
- **Missing players**: 1,204 players without rim pressure data

### After Fix
- **Shot chart files**: ~500-600 players per season
- **Rim pressure data**: ~5,000+ players total
- **Coverage in expanded predictions**: ~90%+ (1,600+/1,849)
- **Missing players**: ~200-300 players (only those truly without shot chart data in API)

---

## Key Players That Will Now Have Rim Pressure Data

Examples of players currently missing rim pressure data who will now be included:

- **Willy Hernangomez (2016-17)**: Currently 92.52% star-level, missing rim pressure
- **Dion Waiters (2016-17)**: Currently 74.98% star-level, missing rim pressure
- **Mikal Bridges (2021-22)**: Currently 30.00% star-level, missing rim pressure (usage shock case)
- **Many young players**: Age <= 25 who don't meet GP >= 50 filter

---

## Notes

1. **API Rate Limiting**: The shot chart endpoint is rate-limited. The script uses 5 workers with 0.6s delay between requests. For ~5,000 players across 10 seasons, this will take several hours.

2. **Data Availability**: Some players may still not have shot chart data if:
   - They didn't play enough minutes to generate shot chart data
   - They were injured/traded mid-season
   - API doesn't have data for them

3. **Backward Compatibility**: The script still works without the `--use-predictive-dataset` flag, using the original `regular_season` files.

---

## Files Modified

- `src/nba_data/scripts/collect_shot_charts.py`:
  - Added `load_all_players_from_predictive_dataset()` function
  - Added `--use-predictive-dataset` flag
  - Fixed unreachable code bug in `fetch_shot_chart()`

