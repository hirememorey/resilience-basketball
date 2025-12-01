# Data Requirements Specification

## Overview

This document specifies the data sources for the **Playoff Resilience Engine** and the **Sloan Path (Shot Plasticity)** analysis.

---

## Part 1: Resilience & Predictive Engine (Existing)

### 1. Regular Season Game Logs
*   **Source:** `playergamelogs` (Base & Advanced merged)
*   **Purpose:** Feature engineering (Consistency, Performance vs Top 10)
*   **File:** `data/rs_game_logs_{season}.csv`

### 2. Defensive Context
*   **Source:** `leaguedashteamstats` (Advanced & Opponent merged)
*   **Purpose:** Identifying Top-10 Defenses and calculating Expected Performance.
*   **File:** `data/defensive_context_{season}.csv`

### 3. Playoff Logs
*   **Source:** `playergamelogs` (Playoffs)
*   **Purpose:** Calculating ground-truth Resilience Scores.
*   **File:** `data/playoff_logs_{season}.csv`

---

## Part 2: The Sloan Path (New Requirements)

### 4. Shot Charts (Spatial Data)
**Critical for determining "Shot Diet Plasticity"**

#### Endpoint
`stats.nba.com/stats/shotchartdetail`

#### Parameters
*   `PlayerID`: (Loop through all qualified players)
*   `Season`: e.g., "2023-24"
*   `SeasonType`: Fetch **both** "Regular Season" and "Playoffs" separately.
*   `ContextMeasure`: "FGA"

#### Required Fields
| Field | Description | Usage |
|-------|-------------|-------|
| `LOC_X` | X Coordinate (-250 to 250) | Spatial analysis |
| `LOC_Y` | Y Coordinate (-50 to 900) | Spatial analysis |
| `SHOT_ZONE_BASIC` | e.g., "Mid-Range", "Restricted Area" | Zone migration analysis |
| `SHOT_DISTANCE` | Distance in feet | "Pushed Out" metric |
| `SHOT_TYPE` | "2PT Field Goal" vs "3PT Field Goal" | Shot profile |
| `ACTION_TYPE` | e.g., "Jump Shot", "Driving Layup" | Shot type analysis |

#### Storage Format
`data/shot_charts_{season}.csv`
*   *Note:* You may want to store RS and PO in the same file with a `SEASON_TYPE` column, or separate files. Single file with a flag is usually easier for analysis.

---

## Data Caching Strategy

*   **API Rate Limiting:** The `NBAStatsClient` handles this. Do not bypass it.
*   **Volume:** Shot chart data is large. 
    *   Regular Season: ~200k shots per season.
    *   Playoffs: ~15k shots per season.
    *   **Total:** ~1.5M rows for 6 seasons.
    *   **Strategy:** Use `ThreadPoolExecutor` (as in `collect_rs_game_logs.py`) but be mindful of the sheer number of rows when loading into memory. Use `dask` or process player-by-player if pandas memory usage becomes an issue.
