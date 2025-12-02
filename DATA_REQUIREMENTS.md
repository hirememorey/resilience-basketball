# Data Requirements Specification

## Overview

This document specifies the data sources for the **Playoff Resilience Engine** and the **Sloan Path (Stress Vectors)** analysis.

---

## Part 1: Resilience & Predictive Engine (Core Data)

### 1. Regular Season Stats
*   **Source:** `leaguedashplayerstats` (Base & Advanced merged)
*   **Purpose:** Baseline player performance for comparison.
*   **File:** `data/regular_season_{season}.csv`

### 2. Playoff Logs
*   **Source:** `playergamelogs` (Playoffs)
*   **Purpose:** Calculating ground-truth Resilience Scores (Archetypes).
*   **File:** `data/playoff_logs_{season}.csv`

---

## Part 2: Stress Vector Data

### 3. Shot Charts (Plasticity Vector)
**Critical for determining "Spatial Rigidity"**

#### Endpoint
`stats.nba.com/stats/shotchartdetail`

#### Required Fields
| Field | Description | Usage |
|-------|-------------|-------|
| `LOC_X` | X Coordinate (-250 to 250) | Spatial analysis |
| `LOC_Y` | Y Coordinate (-50 to 900) | Spatial analysis |
| `SHOT_DISTANCE` | Distance in feet | "Pushed Out" metric |

#### Storage Format
`data/shot_charts_{season}.csv`

---

### 4. Shot Quality Aggregates (Pressure Vector) ✅ NEW
**Critical for determining "Pressure Appetite" and "Pressure Resilience"**

#### Endpoint
`stats.nba.com/stats/leaguedashplayerptshot`

#### Parameters
*   `Season`: e.g., "2023-24"
*   `SeasonType`: "Regular Season" or "Playoffs"
*   `CloseDefDistRange`: One of:
    *   `"0-2 Feet - Very Tight"`
    *   `"2-4 Feet - Tight"`
    *   `"4-6 Feet - Open"`
    *   `"6+ Feet - Wide Open"`

#### Required Fields
| Field | Description | Usage |
|-------|-------------|-------|
| `PLAYER_ID` | Player ID | Join key |
| `GP` | Games Played | Total volume calculation |
| `FGA` | Field Goal Attempts (per game) | Volume |
| `EFG_PCT` | Effective Field Goal % | Efficiency |

#### Storage Format
`data/shot_quality_aggregates_{season}.csv`

**Script:** `src/nba_data/scripts/collect_shot_quality_aggregates.py`

---

### 5. Physicality Data (Physicality Vector) 🎯 NEXT
**For measuring "Force" - the ability to get to the line**

#### Endpoint
`stats.nba.com/stats/leaguedashplayerstats`

#### Required Fields
| Field | Description | Usage |
|-------|-------------|-------|
| `FTA` | Free Throw Attempts | Volume |
| `FGA` | Field Goal Attempts | Denominator for FTr |

#### Derived Metric
*   **`FTr` (Free Throw Rate):** `FTA / FGA`
*   **`FTr_RESILIENCE`:** `Playoff FTr / RS FTr`

---

## Data Caching Strategy

*   **API Rate Limiting:** The `NBAStatsClient` handles this. Do not bypass it.
*   **Caching:** All API responses are cached to `data/cache/` for 24 hours. Delete cache files to force re-fetch.
*   **Volume:** Shot quality aggregates are lightweight (~500 players per call). Shot charts are large (~200k shots per season).

---

## Historical Expansion Status

**✅ COMPLETE** - All seasons collected (2015-16 through 2024-25)

| Season | Shot Quality Aggregates | Clock Data | Status |
|--------|------------------------|------------|--------|
| 2024-25 | ✅ Collected | ✅ Collected | Complete |
| 2023-24 | ✅ Collected | ✅ Collected | Complete |
| 2022-23 | ✅ Collected | ✅ Collected | Complete |
| 2021-22 | ✅ Collected | ✅ Collected | Complete |
| 2020-21 | ✅ Collected | ✅ Collected | Complete |
| 2019-20 | ✅ Collected | ✅ Collected | Complete |
| 2018-19 | ✅ Collected | ✅ Collected | Complete |
| 2017-18 | ✅ Collected | ✅ Collected | Complete |
| 2016-17 | ✅ Collected | ✅ Collected | Complete |
| 2015-16 | ✅ Collected | ✅ Collected | Complete |

**Clock Data Collection (Optimized):**
```bash
# Collect clock data for all seasons (parallelized, ~4-5x faster)
python src/nba_data/scripts/collect_shot_quality_with_clock.py \
  --seasons 2015-16 2016-17 2017-18 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 2024-25 \
  --workers 8
```

**Note:** Clock data collection has been optimized with ThreadPoolExecutor for parallel fetching. The `--workers` parameter controls parallelism (default: 8).
