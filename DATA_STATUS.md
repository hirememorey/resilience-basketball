# Database Status Report

**Last Updated:** November 20, 2025  
**Purpose:** Quick reference for new developers to understand current database state.

## 🚨 High-Level Status: PENDING HISTORICAL REPOPULATION

The database schema and population logic have been **completely overhauled** to fix critical integrity issues. As a result, almost all historical data was wiped.

-   ✅ **Schema:** Corrected and up-to-date. Primary Keys now correctly use `(player_id, season, season_type, team_id)`.
-   ✅ **Data Population Logic:** Fixed. Scripts now use real `team_id`s.
-   ✅ **2024-25 Regular Season:** Repopulated with clean, validated data.
-   ⚠️ **Historical Data (2015-2024):** **PENDING.** Needs to be repopulated using the new `populate_historical_data.py` script.
-   ⚠️ **Playoff Data:** **PENDING.** Needs to be populated for all seasons.

## Data Integrity

**This is the most critical takeaway from recent work.** Do not trust any data without verification.

1.  **The `team_id` Fix:** The root cause of all previous corruption was a placeholder `team_id`. This is resolved. The population scripts now fetch and use the correct `team_id` for each player's season stint.
2.  **The Schema Fix:** The core stats tables now have a composite primary key that includes `season_type`. This prevents Regular Season and Playoff data from colliding.
3.  **Validation is Mandatory:** After running any population script, you **must** run `python src/nba_data/scripts/validate_integrity.py` to check for placeholder data, key collisions, and other silent failures.

## Table-by-Table Status (Post-Rebuild)

### Core Player Data
| Table | Records (Approx.) | Status | Notes |
|-------|---------|--------|----------|
| `player_season_stats` | 569 | ✅ Populated for 2024-25 RS | Historical data pending |
| `player_advanced_stats` | 569 | ✅ Populated for 2024-25 RS | Historical data pending |
| `player_tracking_stats` | 569 | ✅ Populated for 2024-25 RS | Historical data pending |
| `player_playtype_stats` | ~4,300 | ⚠️ PENDING | Requires population |
| `player_shot_locations` | 0 | ⚠️ PENDING | Requires full historical population |

### Playoff Data
All playoff tables (`player_playoff_*`) are currently empty and pending population.

### Game Logs & Shot Dashboards
All game-level data (`player_game_logs`, `player_shot_dashboard_stats`) are currently empty and pending population.

## Next Steps for New Developers

1.  **Run Historical Population:** Use `populate_historical_data.py` to fill the database. This will take time.
    ```bash
    python src/nba_data/scripts/populate_historical_data.py --seasons 2023-24 2022-23
    ```
2.  **Validate Continuously:** After each major population run, use the `validate_integrity.py` script.
3.  **Begin Analysis Refactor:** Once you have a sufficient dataset, start implementing the new metrics described in `extended_resilience_framework.md`.
