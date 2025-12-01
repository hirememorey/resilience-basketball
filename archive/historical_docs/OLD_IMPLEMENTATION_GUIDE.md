# Implementation Guide: Step-by-Step

## Prerequisites

### Required Python Packages
```bash
pip install pandas numpy scikit-learn scipy tenacity requests
```

### Existing Infrastructure
- API client: `src/nba_data/api/nba_stats_client.py` (already built)
- Caching: Built-in with tenacity retries
- Error handling: Rate limiting implemented

---

## Step 1: Data Collection
The data collection process is divided into three scripts. They can be run in parallel for different seasons to speed up collection.

### 1.1 Regular Season Stats (`collect_regular_season_stats.py`)
**Purpose:** Fetches player stats for the regular season.
**Method:**
1.  Makes two API calls to `leaguedashplayerstats` for each season:
    - `MeasureType="Base"`: To get raw totals like `PTS`, `MIN`, `GP`.
    - `MeasureType="Advanced"`: To get rate stats like `TS%`, `AST%`, `USG%`.
2.  Merges the two dataframes.
3.  Filters for qualified players (`GP >= 50`, `MIN >= 20`).
4.  Saves the result to `data/regular_season_{season}.csv`.

**Run:**
```bash
python src/nba_data/scripts/collect_regular_season_stats.py --seasons 2018-19 2019-20 ...
```

---

### 1.2 Defensive Context (`collect_defensive_context.py`)
**Purpose:** Fetches team-level defensive statistics to calculate the `Defensive Context Score (DCS)`.
**Method:**
1.  Makes two API calls to `leaguedashteamstats` for each season:
    - `MeasureType="Advanced"`: To get `DEF_RATING`.
    - `MeasureType="Opponent"`: To get opponent shooting stats (`OPP_FGM`, `OPP_FGA`, etc.).
2.  **Manually calculates `OPP_EFG_PCT` and `OPP_FTA_RATE`**, as these are not directly available.
3.  Merges the dataframes.
4.  Calculates the composite `def_context_score` for each team.
5.  Saves the result to `data/defensive_context_{season}.csv`.

**Run:**
```bash
python src/nba_data/scripts/collect_defensive_context.py --seasons 2018-19 2019-20 ...
```

---

### 1.3 Playoff Game Logs (`collect_playoff_logs.py`)
**Purpose:** Fetches per-game stats for every player in the playoffs. This script is the most robust and replaces the original, unreliable play-by-play approach.
**Method:**
1.  Fetches a list of all players who participated in the playoffs for a given season.
2.  For **each player**, it makes two API calls to `playergamelogs`:
    - `MeasureType="Base"`: For `PTS`, `MIN`, `MATCHUP`, etc.
    - `MeasureType="Advanced"`: For `POSS`, `USG%`, `AST%`, etc.
3.  Merges the Base and Advanced game logs for each player.
4.  Aggregates all player game logs for the season and saves them to `data/playoff_logs_{season}.csv`.

**Run:**
```bash
# This is the longest-running script.
# It can be run in parallel for each season to speed up collection.
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2018-19 &
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2019-20 &
# ... etc.
```
**Note:** The original concept of a "garbage time filter" based on play-by-play data has been deprecated. Noise is now handled by filtering on total minutes played in a series (see Step 1.4).

---

### 1.4 Training Data Assembler (`assemble_training_data.py`)
**Purpose:** Combines all collected data into a single, model-ready dataset where each row represents one player's performance in a single playoff series.
**Method:**
1.  Loads all `regular_season_*.csv`, `defensive_context_*.csv`, and `playoff_logs_*.csv` files.
2.  Creates a mapping of team abbreviations to team IDs from the regular season data.
3.  **Aggregates the playoff game logs:**
    - Parses the opponent's abbreviation from the `MATCHUP` string (e.g., "LAL" from "DEN vs. LAL").
    - Groups each player's games by opponent to create series-level stats.
    - Recalculates `po_ts_pct` and `po_ppg_per75` from summed totals to ensure accuracy.
    - Calculates a weighted average for `po_ast_pct` and `po_usg_pct` based on minutes played.
4.  Merges the aggregated series data with the corresponding regular season stats.
5.  Merges the result with the defensive context data for each series opponent.
6.  Saves the final clean dataset to `data/training_dataset.csv`.

**Run:**
```bash
python src/nba_data/scripts/assemble_training_data.py
```

**Expected Output:**
- `data/training_dataset.csv` (~1000 rows for 6 seasons)

---

## Step 2: Model Training (`train_resilience_models.py`)
**Purpose:** Trains the regression models and filters out small sample sizes.
**Method:**
1.  Loads `data/training_dataset.csv`.
2.  **Applies a critical filter:** `df = df[df['po_minutes_total'] >= 50]`. This removes noise from players with insignificant minutes.
3.  Prepares the feature matrix for three separate models (TS%, PPG per 75, AST%).
4.  Trains a `LinearRegression` model for each target variable.
5.  Saves the trained models (`.pkl`) and metadata (RMSE scores) to the `models/` directory.

**Run:**
```bash
python src/nba_data/scripts/train_resilience_models.py
```

---

## Step 3: Generate Resilience Scores (`calculate_resilience_scores.py`)
**Purpose:** Uses the trained models to score every player-series in the dataset.
**Method:**
1.  Loads the trained models from the `models/` directory.
2.  Loads the `data/training_dataset.csv`.
3.  **Applies the same >50 minute filter** to ensure scores are only generated for meaningful performances.
4.  For each player-series, it:
    - Predicts the "expected" performance for TS%, PPG, and AST%.
    - Calculates the residual (Actual - Expected).
    - Standardizes the residual into a Z-score using the model's RMSE.
    - Combines the three Z-scores into a final `RESILIENCE_SCORE`.
5.  Saves all scores to `results/resilience_scores_all.csv`.

**Run:**
```bash
python src/nba_data/scripts/calculate_resilience_scores.py
```

---

## Step 4: Validation (`validate_face_validity.py`)
**Purpose:** Checks the model's output against known, historic playoff performances to ensure it aligns with reality.
**Method:**
1.  Loads the `results/resilience_scores_all.csv`.
2.  Defines a list of test cases (e.g., Kawhi Leonard in 2018-19, Trae Young in 2021-22).
3.  Averages the player's resilience score across all series in that season.
4.  Compares the actual score to the expected outcome (e.g., expects Kawhi's score to be strongly positive).
5.  Prints a pass/fail summary.

**Run:**
```bash
python src/nba_data/scripts/validate_face_validity.py
```

---

## Step 5: Generate Final Report (`generate_report.py`)
**Purpose:** Creates a human-readable summary of the results.
**Method:**
1.  Loads the `results/resilience_scores_all.csv`.
2.  Generates a Markdown file with the Top 10 and Bottom 10 performers.
3.  Saves the report to `results/resilience_report.md`.

**Run:**
```bash
python src/nba_data/scripts/generate_report.py
```

---

## Full Pipeline Execution
The entire process can be run sequentially with the following commands after setting up the environment.

```bash
# 1. Collect data (can be parallelized)
python src/nba_data/scripts/collect_regular_season_stats.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24
python src/nba_data/scripts/collect_defensive_context.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24

# 2. Analyze
python src/nba_data/scripts/assemble_training_data.py
python src/nba_data/scripts/train_resilience_models.py
python src/nba_data/scripts/calculate_resilience_scores.py
python src/nba_data/scripts/validate_face_validity.py
python src/nba_data/scripts/generate_report.py
```

---

## Testing Strategy

### Unit Tests
Create `tests/test_data_pipeline.py`:
```python
import pytest
import pandas as pd

def test_garbage_time_filter():
    """Test garbage time logic."""
    from src.nba_data.scripts.collect_playoff_playbyplay import is_garbage_time
    
    # Should be garbage time
    assert is_garbage_time(4, "04:30", 20) == True
    assert is_garbage_time(5, "02:00", 18) == True
    
    # Should NOT be garbage time
    assert is_garbage_time(4, "06:00", 20) == False
    assert is_garbage_time(4, "04:30", 10) == False
    assert is_garbage_time(3, "00:30", 25) == False

def test_defensive_context_score():
    """Test DCS calculation."""
    from src.nba_data.scripts.collect_defensive_context import calculate_defensive_context_score
    
    # League average defense
    dcs = calculate_defensive_context_score(110.0, 0.52, 0.25)
    assert 45 <= dcs <= 55  # Should be near 50
    
    # Elite defense
    dcs = calculate_defensive_context_score(105.0, 0.48, 0.22)
    assert dcs > 60
    
    # Weak defense
    dcs = calculate_defensive_context_score(115.0, 0.56, 0.28)
    assert dcs < 40

# Run tests
pytest tests/test_data_pipeline.py
```

---

## Troubleshooting

### Issue: API Rate Limiting
**Solution:** Increase sleep time between requests, use caching aggressively.

### Issue: Missing Playoff Data
**Solution:** Some players/teams may not have data. Skip and log warnings.

### Issue: Model R² < 0.3
**Solution:** Check for data quality issues, verify feature engineering, consider adding features.

### Issue: Face Validity Fails
**Solution:** Investigate known cases, check if expected performance is reasonable.

---

## Next Steps After Implementation

1. **Run on 2024-25 season** (current season)
2. **Generate rankings** for all playoff performers
3. **Validate predictions** by comparing to actual outcomes
4. **Iterate** based on results

---

## Quick Start Summary

```bash
# 1. Collect data
python src/nba_data/scripts/collect_regular_season_stats.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24
python src/nba_data/scripts/collect_defensive_context.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24

# 2. Analyze
python src/nba_data/scripts/assemble_training_data.py
python src/nba_data/scripts/train_resilience_models.py
python src/nba_data/scripts/calculate_resilience_scores.py
python src/nba_data/scripts/validate_face_validity.py
python src/nba_data/scripts/generate_report.py
```

---

**Estimated Time:**
- Data collection: 4-6 hours (mostly API wait time)
- Model training: 5-10 minutes
- Scoring: 1-2 minutes
- Validation: 5-10 minutes
- **Total:** 4-7 hours (mostly unattended)

---

**Next:** Review `IMPLEMENTATION_PLAN.md` for conceptual overview, or start implementing data collection scripts.
