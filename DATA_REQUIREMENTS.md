# Data Requirements Specification

## Overview

This document specifies the data needed for the resilience model. The pipeline uses a **Merge Strategy** where multiple API endpoints are fetched and joined to construct complete player profiles.

## Data Collection Phases

### Phase 1: Regular Season Player Stats

#### Endpoints
1.  `leaguedashplayerstats` (MeasureType='Base') -> PTS, GP, MIN
2.  `leaguedashplayerstats` (MeasureType='Advanced') -> TS%, AST%, USG%

#### Merging Strategy
- Fetch both endpoints for the season.
- Join on `PLAYER_ID`.
- Filter for `GP >= 50` and `MIN >= 20.0`.

#### Required Fields
| Field | Source | Description |
|-------|--------|-------------|
| Player ID | Both | Unique identifier |
| TS% | Advanced | True Shooting % |
| Points | Base | Total Points (calculate per 75) |
| AST% | Advanced | Assist percentage |
| Usage% | Advanced | Usage rate |

#### Storage Format
`data/regular_season_{season}.csv`

---

### Phase 2: Opponent Defensive Metrics

#### Endpoints
1.  `leaguedashteamstats` (MeasureType='Advanced') -> DEF_RATING
2.  `leaguedashteamstats` (MeasureType='Opponent') -> OPP_FGM, OPP_FGA, OPP_FTA

#### Calculation Strategy
- `DEF_RATING`: Direct from Advanced stats.
- `OPP_EFG_PCT`: Calculated from Opponent stats: `(FGM + 0.5 * 3PM) / FGA`
- `OPP_FTA_RATE`: Calculated from Opponent stats: `FTA / FGA`

#### Composite Defensive Context Score (DCS)
```python
dcs = 0.60 * scaled_dr + 0.25 * scaled_efg + 0.15 * scaled_ftr
```

#### Storage Format
`data/defensive_context_{season}.csv`

---

### Phase 3: Playoff Data (Game Logs)

**Note:** Replaces `playbyplayv2` due to API instability.

#### Endpoints
1.  `playergamelogs` (MeasureType='Base') -> PTS, MIN, FGM, FGA, FTA
2.  `playergamelogs` (MeasureType='Advanced') -> POSS, USG%, AST%

#### Collection Strategy
1.  Fetch list of playoff players from `leaguedashplayerstats`.
2.  For each player, fetch Base and Advanced logs.
3.  Merge on `GAME_ID`.

#### Aggregation (Assembly Phase)
- Parse `MATCHUP` to determine Opponent (e.g., "DEN vs. LAL" -> Opponent is LAL).
- Group by `PLAYER_ID` and `OPPONENT`.
- Sum counting stats (PTS, FGA, etc.).
- Calculate weighted averages for rates (AST%, USG%).
- Recalculate TS% from summed attempts.

#### Storage Format
`data/playoff_logs_{season}.csv`

---

## Training Dataset Schema

The final `training_dataset.csv` contains one row per Player-Series:

| Column | Description | Source |
|--------|-------------|--------|
| `PLAYER_ID` | Player ID | RS/PO |
| `SEASON` | Season Year | RS/PO |
| `OPPONENT_ABBREV`| Opponent Team | PO Logs |
| `rs_ts_pct` | Regular Season TS% | RS |
| `rs_ppg_per75` | RS Points per 75 Poss | RS |
| `rs_ast_pct` | RS Assist % | RS |
| `opp_def_context_score` | Opponent Defense Score | Def Context |
| `po_ts_pct` | Playoff Series TS% | PO Logs |
| `po_ppg_per75` | PO Series Points per 75 | PO Logs |
| `po_ast_pct` | PO Series Assist % | PO Logs |

---

## API Notes

- **Rate Limiting:** The client handles 429 errors with exponential backoff.
- **Caching:** All API responses are cached in `data/cache/`.
- **Parallelism:** Data collection can be run in parallel for different seasons to speed up the process.
