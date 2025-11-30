# Data Requirements Specification

## Overview

This document specifies the exact data needed for the regression-based playoff resilience model.

## Data Collection Phases

### Phase 1: Regular Season Player Stats

#### Endpoint
`stats.nba.com/stats/leaguedashplayerstats`

#### Parameters
- `Season`: 2018-19, 2019-20, 2020-21, 2021-22, 2022-23, 2023-24, 2024-25
- `SeasonType`: Regular Season
- `PerMode`: Per100Possessions (for pace adjustment)

#### Required Fields
| Field | NBA API Name | Description | Usage |
|-------|--------------|-------------|-------|
| Player ID | PLAYER_ID | Unique identifier | Join key |
| Player Name | PLAYER_NAME | Display name | Output |
| Team | TEAM_ABBREVIATION | Team abbreviation | Context |
| Games Played | GP | Games in season | Filter (≥50) |
| Minutes per Game | MIN | Average minutes | Filter (≥20) |
| TS% | TS_PCT | True Shooting % | Model input |
| Points per 75 | PTS (converted) | Pace-adjusted scoring | Model input |
| AST% | AST_PCT | Assist percentage | Model input |
| Usage% | USG_PCT | Usage rate | Model input |

#### Filtering
```python
# Apply these filters
df = df[
    (df['GP'] >= 50) &
    (df['MIN'] >= 20.0)
]
```

#### Storage Format
`data/regular_season_{season}.csv`

---

### Phase 2: Opponent Defensive Metrics

#### Endpoint
`stats.nba.com/stats/leaguedashteamstats`

#### Parameters
- `Season`: Same as Phase 1
- `SeasonType`: Both Regular Season AND Playoffs
- `MeasureType`: Defense

#### Required Fields
| Field | NBA API Name | Description | Usage |
|-------|--------------|-------------|-------|
| Team ID | TEAM_ID | Unique identifier | Join key |
| Team Name | TEAM_NAME | Display name | Output |
| Season Type | SEASON_TYPE | Regular/Playoff | Dynamic weighting |
| Defensive Rating | DEF_RATING | Pts allowed per 100 | Primary context |
| Opponent eFG% | OPP_EFG_PCT | eFG% allowed | Secondary context |
| Opponent FT Rate | OPP_FTA_RATE | FTA/FGA allowed | Secondary context |
| Games Played | GP | Sample size | Weighting factor |

#### Composite Defensive Context Score (DCS)
```python
# Normalize each component to 0-100 scale
def calculate_dcs(def_rating, opp_efg, opp_ft_rate):
    # Lower defensive rating = better defense
    # Lower opponent shooting = better defense
    
    # Scale defensive rating (league avg ~110)
    dr_score = 100 * (130 - def_rating) / 40
    
    # Scale opponent eFG% (league avg ~0.52)
    efg_score = 100 * (0.60 - opp_efg) / 0.20
    
    # Scale opponent FT rate (league avg ~0.25)
    ftr_score = 100 * (0.35 - opp_ft_rate) / 0.20
    
    # Weighted composite (60% DRTG, 25% eFG, 15% FTR)
    dcs = 0.60 * dr_score + 0.25 * efg_score + 0.15 * ftr_score
    
    # Clamp to 0-100
    return max(0, min(100, dcs))
```

#### Dynamic Playoff Adjustment
```python
# Use playoff-specific if sample is large enough
if playoff_games >= 10:
    dcs = calculate_dcs(playoff_def_rating, playoff_opp_efg, playoff_opp_ft_rate)
else:
    # Use regular season metrics
    dcs = calculate_dcs(regular_season_def_rating, regular_season_opp_efg, regular_season_opp_ft_rate)
```

#### Storage Format
`data/defensive_context_{season}.csv`

---

### Phase 3: Playoff Play-by-Play Data

#### Endpoint
`stats.nba.com/stats/playbyplayv2`

#### Parameters
- `GameID`: All playoff games from target seasons
- Must be called per game (API limitation)

#### Required Fields
| Field | NBA API Name | Description | Usage |
|-------|--------------|-------------|-------|
| Game ID | GAME_ID | Unique game identifier | Join key |
| Event Type | EVENTMSGTYPE | Type of play | Filtering |
| Period | PERIOD | Quarter/OT | Garbage time filter |
| Time Remaining | PCTIMESTRING | Clock time | Garbage time filter |
| Score Margin | SCOREMARGIN | Point differential | Garbage time filter |
| Player ID | PLAYER1_ID | Acting player | Attribution |

#### Garbage Time Filter
```python
def is_garbage_time(period, time_remaining, score_margin):
    """
    Remove plays that occur when:
    - Period is 4th quarter or overtime (period >= 4)
    - Score differential >= 15 points
    - Time remaining <= 5 minutes
    """
    if period < 4:
        return False
    
    # Parse time remaining (format: "MM:SS")
    minutes, seconds = map(int, time_remaining.split(':'))
    total_seconds = minutes * 60 + seconds
    
    # Garbage time conditions
    if total_seconds <= 300 and abs(score_margin) >= 15:
        return True
    
    return False

# Apply filter
df['is_garbage'] = df.apply(
    lambda row: is_garbage_time(row['PERIOD'], row['PCTIMESTRING'], row['SCOREMARGIN']),
    axis=1
)
df_clean = df[~df['is_garbage']]
```

#### Aggregation to Player-Game Stats
After filtering, aggregate to player-game level:
```python
player_game_stats = df_clean.groupby(['GAME_ID', 'PLAYER_ID']).agg({
    'FGM': 'sum',
    'FGA': 'sum',
    'FG3M': 'sum',
    'FTM': 'sum',
    'FTA': 'sum',
    'PTS': 'sum',
    'AST': 'sum',
    'REB': 'sum',
    # ... other stats
})
```

#### Storage Format
`data/playoff_playbyplay_{season}_clean.csv`

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

| Column | Type | Description |
|--------|------|-------------|
| player_id | int | Unique player identifier |
| player_name | str | Player display name |
| season | str | NBA season (e.g., "2023-24") |
| series_round | int | Playoff round (1-4) |
| opponent_team | str | Opponent team abbreviation |
| rs_ts_pct | float | Regular season TS% |
| rs_ppg_per75 | float | Regular season points per 75 |
| rs_ast_pct | float | Regular season AST% |
| rs_usg_pct | float | Regular season usage% |
| opp_def_context_score | float | Opponent defensive context (0-100) |
| po_ts_pct | float | Playoff TS% (target) |
| po_ppg_per75 | float | Playoff points per 75 (target) |
| po_ast_pct | float | Playoff AST% (target) |
| po_games_played | int | Sample size |
| po_minutes_total | float | Total playoff minutes |

### Data Quality Checks

Before training, validate:
```python
# Check for missing values
assert training_data.isnull().sum().sum() == 0, "Missing values found"

# Check value ranges
assert (training_data['rs_ts_pct'] >= 0).all() and (training_data['rs_ts_pct'] <= 1.0).all()
assert (training_data['po_ts_pct'] >= 0).all() and (training_data['po_ts_pct'] <= 1.0).all()
assert (training_data['opp_def_context_score'] >= 0).all() and (training_data['opp_def_context_score'] <= 100).all()

# Check minimum samples
assert (training_data['po_games_played'] >= 4).all(), "Players with <4 playoff games found"

# Check for outliers
from scipy import stats
z_scores = np.abs(stats.zscore(training_data[['rs_ts_pct', 'po_ts_pct']]))
assert (z_scores < 5).all().all(), "Extreme outliers detected (>5 SD)"
```

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
