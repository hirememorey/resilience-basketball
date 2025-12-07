# Salary Data Collection Strategy

**Goal**: Efficiently collect historical salary data for 2015-2025 to calculate Alpha Scores.

## The "First Principles" Efficiency Approach

Instead of scraping individual player pages (N=5000+ requests), we scrape season-level lists (N=10 requests).

## Source Selection

We use **Basketball Reference** as the primary source (with HoopsHype as fallback) for these reasons:

1. **Reliable Historical Data**: Basketball Reference maintains consistent URLs for all historical seasons
2. **Clean HTML Tables**: Easily parsable by Pandas without complex DOM traversal
3. **Complete Coverage**: All NBA players with salary data for each season

**Note**: HoopsHype URLs for historical seasons may return 404, so Basketball Reference is used as the primary source.

## Data Pipeline

1. **Iterate Seasons**: 2015-16 to 2024-25.
2. **Fetch**: GET request to HoopsHype.
3. **Parse**: Extract the main salary table.
4. **Clean**:
   - Convert `"$25,000,000"` → `25.0` (Millions)
   - Normalize names (strip ".", lower case comparison)
5. **Merge**: Join with `predictive_dataset.csv` on normalized names.

## Handling Name Mismatches

NBA API and HoopsHype often spell names differently (e.g., "CJ McCollum" vs "C.J. McCollum").

The script includes a `normalize_name` function to maximize match rates.

## Usage

```bash
# Collect salary data
python src/nba_data/scripts/collect_salary_data.py

# Calculate Alpha scores
python src/nba_data/scripts/calculate_alpha_scores.py --salary data/salaries.csv
```

## Output

- **File**: `data/salaries.csv`
- **Columns**: `PLAYER_NAME`, `SEASON`, `SALARY_MILLIONS`
- **Coverage**: All NBA players with salary data for seasons 2015-16 through 2024-25
