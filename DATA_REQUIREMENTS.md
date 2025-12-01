# Data Requirements Specification

## Overview

This document specifies the exact data sources for the regression-based playoff resilience model. It reflects the final, working implementation after discovering and correcting for inconsistencies in the NBA Stats API.

## Data Collection Strategy: Merge "Base" and "Advanced"

A key lesson learned is that no single `MeasureType` provides all required columns. The standard practice for this project is to **fetch both "Base" and "Advanced" stats** for a given endpoint and merge them.
- **Base:** Provides foundational stats like `PTS`, `FGM`, `FGA`, `FTM`, `FTA`, `MIN`.
- **Advanced:** Provides rate stats like `TS%`, `AST%`, `USG%`, and possession counts (`POSS`).

---

## Data Collection Phases

### Phase 1: Regular Season Player Stats

#### Endpoint
`stats.nba.com/stats/leaguedashplayerstats`

#### Parameters
- `SeasonType`: Regular Season
- `PerMode`: `PerGame` for Base, `PerGame` for Advanced (we will calculate pace-adjusted stats manually).
- **`MeasureType`: `Base` and `Advanced` (two separate calls).**

#### Required Fields (Post-Merge)
| Field             | Source     | Description             |
|-------------------|------------|-------------------------|
| `PLAYER_ID`       | Both       | Unique identifier       |
| `PLAYER_NAME`     | Both       | Display name            |
| `TEAM_ABBREVIATION` | Base       | Team abbreviation       |
| `GP`              | Base       | Games Played (Filter ≥50) |
| `MIN`             | Base       | Minutes (Filter ≥20)    |
| `PTS`             | Base       | Points                  |
| `TS_PCT`          | Advanced   | True Shooting %         |
| `AST_PCT`         | Advanced   | Assist Percentage       |
| `USG_PCT`         | Advanced   | Usage Rate              |

#### Storage Format
`data/regular_season_{season}.csv` (Contains the merged and filtered data)

---

### Phase 2: Opponent Defensive Metrics

#### Endpoint
`stats.nba.com/stats/leaguedashteamstats`

#### Parameters & Method
Requires two separate API calls per season, which are then merged.
1.  **`MeasureType`: `Advanced`**
    -   **Purpose:** To get `DEF_RATING`.
2.  **`MeasureType`: `Opponent`**
    -   **Purpose:** To get opponent shooting stats (`OPP_FGM`, `OPP_FGA`, etc.) needed to manually calculate `OPP_EFG_PCT` and `OPP_FTA_RATE`.

#### Required Fields & Calculations
| Field             | Source                | Description                             |
|-------------------|-----------------------|-----------------------------------------|
| `TEAM_ID`         | Both                  | Unique identifier                       |
| `DEF_RATING`      | Advanced              | Points allowed per 100 possessions      |
| `OPP_EFG_PCT`     | **Calculated**        | `(OPP_FGM + 0.5 * OPP_FG3M) / OPP_FGA`    |
| `OPP_FTA_RATE`    | **Calculated**        | `OPP_FTA / OPP_FGA`                     |

---

### Phase 3: Playoff Player Game Logs

#### ⚠️ Deprecated Endpoint: `playbyplayv2`
The `playbyplayv2` endpoint, originally planned for this phase, was found to be **unreliable and is no longer used**. It frequently returns empty data.

#### Primary Endpoint
`stats.nba.com/stats/playergamelogs`

#### Parameters & Method
Requires two separate API calls **per player, per season**, which are then merged.
1.  **`MeasureType`: `Base`**
    -   **Purpose:** Provides per-game totals like `PTS`, `MIN`, `FGA`, `FTA`, `MATCHUP`.
2.  **`MeasureType`: `Advanced`**
    -   **Purpose:** Provides per-game rate stats like `TS_PCT`, `AST_PCT`, `USG_PCT`, and `POSS`.

#### Required Fields (Post-Merge)
| Field             | Source   | Description                         |
|-------------------|----------|-------------------------------------|
| `PLAYER_ID`       | Both     | Unique identifier                   |
| `GAME_ID`         | Both     | Unique game identifier              |
| `MATCHUP`         | Base     | e.g., "DEN vs. LAL" (used to find opponent) |
| All "Base" stats  | Base     | `PTS`, `MIN`, `FGA`, `FTA`, etc.    |
| All "Advanced" stats| Advanced | `POSS`, `USG_PCT`, `AST_PCT`, etc.|

#### Storage Format
`data/playoff_logs_{season}.csv`

---

### Phase 4: Playoff Series Information

#### Endpoint
`stats.nba.com/stats/playoffpicture` or manual data entry

#### Required Fields
| Field | Description | Usage |
|-------|-------------|-------|
| Season | NBA season | Join key |
| Round | Playoff round (1-4) | Context |
| Team 1 | First team | Join key |
| Team 2 | Opponent team | Defensive context |
| Winner | Series winner | Validation |

#### Storage Format
`data/playoff_series_{season}.csv`

---

## Data Assembly for Model Training

### Training Dataset Structure

Combine all phases into single training dataset:

```python
# Pseudo-code for data assembly
training_data = []

for season in seasons:
    # Load regular season stats
    regular_season = pd.read_csv(f'data/regular_season_{season}.csv')
    
    # Load defensive context
    defensive_context = pd.read_csv(f'data/defensive_context_{season}.csv')
    
    # Load playoff performance (aggregated from play-by-play)
    playoff_stats = pd.read_csv(f'data/playoff_playbyplay_{season}_clean.csv')
    
    # Load series information
    series_info = pd.read_csv(f'data/playoff_series_{season}.csv')
    
    # Join everything
    merged = regular_season.merge(
        playoff_stats, on=['PLAYER_ID'], suffixes=('_RS', '_PO')
    ).merge(
        series_info, on=['TEAM_ID', 'SEASON']
    ).merge(
        defensive_context, left_on=['OPPONENT_TEAM_ID'], right_on=['TEAM_ID']
    )
    
    training_data.append(merged)

# Combine all seasons
full_training_data = pd.concat(training_data)
```

### Final Training Dataset Schema

| Column                  | Type  | Description                               |
|-------------------------|-------|-------------------------------------------|
| player_id               | int   | Unique player identifier                  |
| player_name             | str   | Player display name                       |
| season                  | str   | NBA season (e.g., "2023-24")              |
| opponent_abbrev         | str   | Opponent team abbreviation                |
| rs_ts_pct               | float | Regular season TS%                        |
| rs_ppg_per75            | float | Regular season points per 75 possessions  |
| rs_ast_pct              | float | Regular season AST%                       |
| rs_usg_pct              | float | Regular season usage%                     |
| opp_def_context_score   | float | Opponent defensive context score (0-100)    |
| po_ts_pct               | float | Playoff TS% (aggregated from logs)        |
| po_ppg_per75            | float | Playoff points per 75 (aggregated)      |
| po_ast_pct              | float | Playoff AST% (weighted average)           |
| po_games_played         | int   | Games played in the series                |
| po_minutes_total        | float | Total minutes played in the series        |

### Data Quality Checks

Before training, the `assemble_training_data.py` script aggregates game logs into player-series and merges them with regular season and defensive data. The `train_resilience_models.py` and `calculate_resilience_scores.py` scripts then apply a crucial filter:

```python
# Filter out any player-series with less than 50 total minutes
df = df[df['po_minutes_total'] >= 50]
```
This step is critical for removing small-sample-size noise from the analysis.

---

## Data Caching Strategy

### API Rate Limiting
- NBA Stats API: ~20 requests per minute
- Implement exponential backoff with retries
- Cache all responses locally

### Caching Implementation
```python
import pickle
from pathlib import Path
import hashlib

def get_cached_or_fetch(endpoint, params, fetch_function):
    """
    Check cache first, fetch if not exists.
    """
    # Create cache key from params
    cache_key = hashlib.md5(str(params).encode()).hexdigest()
    cache_file = Path(f'data/cache/{endpoint}_{cache_key}.pkl')
    
    if cache_file.exists():
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    # Fetch from API
    data = fetch_function(params)
    
    # Save to cache
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)
    
    return data
```

---

## Estimated Data Volumes

### Per Season
- Regular season players: ~450 qualified players
- Playoff players: ~200 players
- Playoff games: ~80-90 games
- Play-by-play rows: ~300k rows (before filtering)

### Total for 5 Seasons
- Training samples: ~800-1000 player-series combinations
- Storage requirement: ~500 MB (with caching)
- API calls: ~400-500 total (with efficient caching)

---

## Data Collection Scripts

### Quick Start
```bash
# Step 1: Collect regular season data
python src/nba_data/scripts/collect_regular_season_stats.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24

# Step 2: Collect defensive metrics
python src/nba_data/scripts/collect_defensive_context.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24

# Step 3: Collect playoff play-by-play (slow, ~2-3 hours)
python src/nba_data/scripts/collect_playoff_playbyplay.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24

# Step 4: Assemble training dataset
python src/nba_data/scripts/assemble_training_data.py --output data/training_dataset.csv
```

---

## Next Steps

1. **Implement:** Data collection scripts (see `IMPLEMENTATION_GUIDE.md`)
2. **Validate:** Run data quality checks on collected data
3. **Train:** Build regression models using training dataset
4. **Score:** Generate resilience scores for target season

---

**Note:** All scripts should use existing infrastructure in `src/nba_data/api/` for API access and caching.
