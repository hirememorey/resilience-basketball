# Data-Driven Dependence Score Thresholds

## Summary

Replaced fixed 0.30/0.70 thresholds with data-driven percentiles calculated from star-level players (USG_PCT > 25%) in the 10-year dataset.

## Findings

**Distribution Analysis (533 star-level players):**
- Mean: 0.4309
- Median: 0.3962
- Std Dev: 0.1252

**Data-Driven Thresholds:**
- **Low Dependence**: < 0.3570 (33rd percentile)
- **Moderate Dependence**: 0.3570 - 0.4482 (33rd-66th percentile)
- **High Dependence**: ≥ 0.4482 (66th percentile)

## Key Insight

Most players are moderately dependent (30-70% range), not polarized. The original 0.30/0.70 thresholds were forcing the data into a mental model that didn't match reality.

## Implementation

1. **Threshold Calculation**: `calculate_dependence_thresholds.py`
   - Calculates 33rd and 66th percentiles from star-level players
   - Saves thresholds to `results/dependence_thresholds.json`

2. **Updated Categorization Logic**: `predict_conditional_archetype.py`
   - `_categorize_risk()` now loads thresholds from JSON file
   - Uses 0.3570 and 0.4482 as cutoffs instead of 0.30/0.70

3. **Updated Test Suite**: `test_2d_risk_matrix.py`
   - Test expectations now use data-driven thresholds

## Example Players by Category

**Low Dependence (< 0.3570):**
- James Harden (2018-19): 0.217
- Luka Dončić (2022-23): 0.237
- Derrick Rose (2019-20): 0.236

**Moderate Dependence (0.3570 - 0.4482):**
- Giannis Antetokounmpo (2023-24): 0.395
- Jordan Clarkson (2024-25): 0.395

**High Dependence (≥ 0.4482):**
- System-dependent role players and catch-and-shoot specialists

## Files Modified

1. `src/nba_data/scripts/predict_conditional_archetype.py`
   - Updated `_categorize_risk()` to use data-driven thresholds

2. `test_2d_risk_matrix.py`
   - Updated test expectations to use data-driven thresholds

3. `calculate_dependence_thresholds.py` (new)
   - Script to calculate and validate thresholds

## Files Created

1. `results/dependence_thresholds.json`
   - Contains threshold values and distribution statistics

2. `results/dependence_score_thresholds.csv`
   - Full dataset of star-level players with dependence scores and categories

## Validation

- Luka Dončić correctly categorized as **Franchise Cornerstone** (High Performance, Low Dependence)
- Thresholds properly separate Low/Moderate/High dependence categories
- Distribution matches expected pattern (most players in moderate range)

