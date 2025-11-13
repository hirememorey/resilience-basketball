"""
Script to populate player data from NBA API into our database.

This script fetches player statistics from the NBA API and loads them into
our local database for playoff resilience analysis.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.api import create_data_fetcher
from nba_data.db.schema import NBADatabaseSchema

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PlayerDataPopulator:
    """Populates player data from NBA API into database."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.schema = NBADatabaseSchema(db_path)
        self.fetcher = create_data_fetcher()

    def populate_all_player_data(self, season: str = "2024-25") -> Dict[str, Any]:
        """
        Populate all player data for a given season.

        Args:
            season: Season to populate data for

        Returns:
            Summary of population results
        """
        logger.info(f"Starting player data population for season {season}")

        results = {
            "season": season,
            "metrics_populated": 0,
            "players_affected": 0,
            "errors": []
        }

        # Define which metrics go to which tables
        table_mappings = {
            "player_season_stats": [
                "GP", "MIN", "FGM", "FGA", "FG3M", "FG3A", "FTM", "FTA", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TOV", "PF", "PTS", "PLUS_MINUS",  # Basic counts
                "FGPCT", "FG3PCT", "FTPCT"  # Basic percentages
            ],
            "player_advanced_stats": [
                "TSPCT", "USGPCT", "ORTG", "DRTG", "NRTG",  # Advanced metrics
                "TRBPCT", "ASTPCT", "PIE",  # Advanced percentages
                "AGE", "GP_ADV", "WINS", "LOSSES", "WIN_PCT", "MIN_ADV",  # Additional metrics
                "AST_TO", "AST_RATIO", "OREB_PCT", "DREB_PCT", "TOV_PCT", "EFG_PCT", "PACE_ADV"  # More advanced metrics
            ],
            "player_tracking_stats": [
                # Touches
                "TOUCHES",
                # Drive metrics (17 total)
                "DRIVES", "DRIVE_FGM", "DRIVE_FGA", "DRIVE_FG_PCT", "DRIVE_FTM", "DRIVE_FTA", "DRIVE_FT_PCT",
                "DRIVE_PTS", "DRIVE_PTS_PCT", "DRIVE_PASSES", "DRIVE_PASSES_PCT", "DRIVE_AST", "DRIVE_AST_PCT",
                "DRIVE_TOV", "DRIVE_TOV_PCT", "DRIVE_PF", "DRIVE_PF_PCT",
                # Catch and shoot metrics (8 total)
                "CATCH_SHOOT_FGM", "CATCH_SHOOT_FGA", "CATCH_SHOOT_FG_PCT", "CATCH_SHOOT_PTS",
                "CATCH_SHOOT_FG3M", "CATCH_SHOOT_FG3A", "CATCH_SHOOT_FG3_PCT", "CATCH_SHOOT_EFG_PCT",
                # Pull up metrics (8 total)
                "PULL_UP_FGM", "PULL_UP_FGA", "PULL_UP_FG_PCT", "PULL_UP_PTS",
                "PULL_UP_FG3M", "PULL_UP_FG3A", "PULL_UP_FG3_PCT", "PULL_UP_EFG_PCT",
                # Paint touch metrics (18 total)
                "PAINT_TOUCHES", "PAINT_TOUCH_FGM", "PAINT_TOUCH_FGA", "PAINT_TOUCH_FG_PCT", "PAINT_TOUCH_FTM", "PAINT_TOUCH_FTA", "PAINT_TOUCH_FT_PCT",
                "PAINT_TOUCH_PTS", "PAINT_TOUCH_PTS_PCT", "PAINT_TOUCH_PASSES", "PAINT_TOUCH_PASSES_PCT", "PAINT_TOUCH_AST", "PAINT_TOUCH_AST_PCT",
                "PAINT_TOUCH_TOV", "PAINT_TOUCH_TOV_PCT", "PAINT_TOUCH_FOULS", "PAINT_TOUCH_FOULS_PCT",
                # Post touch metrics (18 total)
                "POST_TOUCHES", "POST_TOUCH_FGM", "POST_TOUCH_FGA", "POST_TOUCH_FG_PCT", "POST_TOUCH_FTM", "POST_TOUCH_FTA", "POST_TOUCH_FT_PCT",
                "POST_TOUCH_PTS", "POST_TOUCH_PTS_PCT", "POST_TOUCH_PASSES", "POST_TOUCH_PASSES_PCT", "POST_TOUCH_AST", "POST_TOUCH_AST_PCT",
                "POST_TOUCH_TOV", "POST_TOUCH_TOV_PCT", "POST_TOUCH_FOULS", "POST_TOUCH_FOULS_PCT",
                # Elbow touch metrics (18 total)
                "ELBOW_TOUCHES", "ELBOW_TOUCH_FGM", "ELBOW_TOUCH_FGA", "ELBOW_TOUCH_FG_PCT", "ELBOW_TOUCH_FTM", "ELBOW_TOUCH_FTA", "ELBOW_TOUCH_FT_PCT",
                "ELBOW_TOUCH_PTS", "ELBOW_TOUCH_PASSES", "ELBOW_TOUCH_AST", "ELBOW_TOUCH_AST_PCT", "ELBOW_TOUCH_TOV", "ELBOW_TOUCH_TOV_PCT",
                "ELBOW_TOUCH_FOULS", "ELBOW_TOUCH_PASSES_PCT", "ELBOW_TOUCH_FOULS_PCT", "ELBOW_TOUCH_PTS_PCT",
                # Efficiency metrics
                "EFF_PTS", "EFF_DRIVE_PTS", "EFF_DRIVE_FG_PCT", "EFF_CATCH_SHOOT_PTS",
                "EFF_CATCH_SHOOT_FG_PCT", "EFF_PULL_UP_PTS", "EFF_PULL_UP_FG_PCT",
                "EFF_PAINT_TOUCH_PTS", "EFF_PAINT_TOUCH_FG_PCT", "EFF_POST_TOUCH_PTS",
                "EFF_POST_TOUCH_FG_PCT", "EFF_ELBOW_TOUCH_PTS", "EFF_ELBOW_TOUCH_FG_PCT",
                "EFF_FG_PCT",
                # Speed and Distance metrics
                "DIST_FEET", "DIST_MILES", "DIST_MILES_OFF", "DIST_MILES_DEF",
                "AVG_SPEED", "AVG_SPEED_OFF", "AVG_SPEED_DEF",
                # Passing metrics
                "PASSES_MADE", "PASSES_RECEIVED", "FT_AST", "SECONDARY_AST",
                "POTENTIAL_AST", "AST_POINTS_CREATED", "AST_ADJ", "AST_TO_PASS_PCT",
                "AST_TO_PASS_PCT_ADJ",
                # Rebounding metrics
                "OREB_CONTEST", "OREB_UNCONTEST", "OREB_CONTEST_PCT", "OREB_CHANCES",
                "OREB_CHANCE_PCT", "OREB_CHANCE_DEFER", "OREB_CHANCE_PCT_ADJ", "AVG_OREB_DIST",
                "DREB_CONTEST", "DREB_UNCONTEST", "DREB_CONTEST_PCT", "DREB_CHANCES",
                "DREB_CHANCE_PCT", "DREB_CHANCE_DEFER", "DREB_CHANCE_PCT_ADJ", "AVG_DREB_DIST",
                "REB_CONTEST", "REB_UNCONTEST", "REB_CONTEST_PCT", "REB_CHANCES",
                "REB_CHANCE_PCT", "REB_CHANCE_DEFER", "REB_CHANCE_PCT_ADJ", "AVG_REB_DIST"
            ]
        }

        # Fetch all available metrics
        logger.info("Fetching all available metrics from NBA API...")
        all_metric_data = self.fetcher.fetch_all_available_metrics(season)

        # Process each table
        for table_name, metric_names in table_mappings.items():
            logger.info(f"Populating {table_name}...")

            try:
                populated_count = self._populate_table(table_name, metric_names, all_metric_data, season)
                results["metrics_populated"] += populated_count
                logger.info(f"✅ {table_name}: {populated_count} metrics populated")

            except Exception as e:
                error_msg = f"Failed to populate {table_name}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        # Calculate unique players affected
        try:
            with self.schema.conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_season_stats WHERE season = ?", (season,))
                results["players_affected"] = cursor.fetchone()[0]
        except Exception as e:
            logger.warning(f"Could not count affected players: {e}")

        logger.info(f"Player data population complete for {season}")
        logger.info(f"Results: {results['players_affected']} players, {results['metrics_populated']} metrics")

        return results

    def _populate_table(self, table_name: str, metric_names: List[str], all_data: Dict[str, Dict], season: str) -> int:
        """
        Populate a specific table with metric data.

        Args:
            table_name: Name of the table to populate
            metric_names: List of metric names to include
            all_data: All fetched metric data
            season: Season being processed

        Returns:
            Number of metrics successfully populated
        """
        populated_count = 0

        # Filter to only metrics we have data for and want for this table
        relevant_metrics = {name: all_data.get(name, {}) for name in metric_names if name in all_data}

        if not relevant_metrics:
            logger.warning(f"No relevant metrics found for {table_name}")
            return 0

        # Get all unique player IDs across all metrics
        all_player_ids = set()
        for metric_data in relevant_metrics.values():
            all_player_ids.update(metric_data.keys())

        logger.info(f"Processing {len(all_player_ids)} players for {table_name}")

        # Process each player
        cursor = self.schema.conn.cursor()
        for player_id in all_player_ids:
            try:
                # Build the record for this player
                record = self._build_player_record(player_id, relevant_metrics, season, table_name)

                if record:
                    # Insert or replace the record
                    self._insert_player_record(cursor, table_name, record)
                    populated_count += 1

            except Exception as e:
                logger.warning(f"Failed to process player {player_id} for {table_name}: {e}")
                continue

        self.schema.conn.commit()
        return populated_count

    def _build_player_record(self, player_id: int, metrics_data: Dict[str, Dict], season: str, table_name: str) -> Dict[str, Any]:
        """
        Build a database record for a player.

        Args:
            player_id: Player ID
            metrics_data: Metric data for all players
            season: Season
            table_name: Target table name

        Returns:
            Database record as dictionary
        """
        record = {
            "player_id": player_id,
            "season": season
        }

        # Add team_id (we'll need to get this from somewhere - for now use placeholder)
        # In a full implementation, we'd need to fetch player info to get team_id
        record["team_id"] = 1610612760  # Default to OKC for now

        # Map metric names to database column names
        column_mappings = {
            "player_season_stats": {
                "FGPCT": "field_goal_percentage",
                "FG3PCT": "three_point_percentage",
                "FTPCT": "free_throw_percentage",
                "GP": "games_played",
                "MIN": "minutes_played",
                "FGM": "field_goals_made",
                "FGA": "field_goals_attempted",
                "FG3M": "three_pointers_made",
                "FG3A": "three_pointers_attempted",
                "FTM": "free_throws_made",
                "FTA": "free_throws_attempted",
                "OREB": "offensive_rebounds",
                "DREB": "defensive_rebounds",
                "REB": "total_rebounds",
                "AST": "assists",
                "STL": "steals",
                "BLK": "blocks",
                "TOV": "turnovers",
                "PF": "personal_fouls",
                "PTS": "points",
                "PLUS_MINUS": "plus_minus"
            },
            "player_advanced_stats": {
                "TSPCT": "true_shooting_percentage",
                "USGPCT": "usage_percentage",
                "ORTG": "offensive_rating",
                "DRTG": "defensive_rating",
                "NRTG": "net_rating",
                "TRBPCT": "rebound_percentage",
                "ASTPCT": "assist_percentage",
                "PIE": "pie",
                "AGE": "age",
                "GP_ADV": "games_played",
                "WINS": "wins",
                "LOSSES": "losses",
                "WIN_PCT": "win_percentage",
                "MIN_ADV": "minutes_played",
                "AST_TO": "assist_to_turnover_ratio",
                "AST_RATIO": "assist_ratio",
                "OREB_PCT": "offensive_rebound_percentage",
                "DREB_PCT": "defensive_rebound_percentage",
                "TOV_PCT": "turnover_percentage",
                "EFG_PCT": "effective_field_goal_percentage",
                "PACE_ADV": "pace"
            },
            "player_tracking_stats": {
                # Drive metrics
                "DRIVES": "drives",
                "DRIVE_FGM": "drive_field_goals_made",
                "DRIVE_FGA": "drive_field_goals_attempted",
                "DRIVE_FG_PCT": "drive_field_goal_percentage",
                "DRIVE_FTM": "drive_free_throws_made",
                "DRIVE_FTA": "drive_free_throws_attempted",
                "DRIVE_FT_PCT": "drive_free_throw_percentage",
                "DRIVE_PTS": "drive_points",
                "DRIVE_PTS_PCT": "drive_points_percentage",
                "DRIVE_PASSES": "drive_passes",
                "DRIVE_PASSES_PCT": "drive_passes_percentage",
                "DRIVE_AST": "drive_assists",
                "DRIVE_AST_PCT": "drive_assists_percentage",
                "DRIVE_TOV": "drive_turnovers",
                "DRIVE_TOV_PCT": "drive_turnovers_percentage",
                "DRIVE_PF": "drive_personal_fouls",
                "DRIVE_PF_PCT": "drive_personal_fouls_percentage",

                # Catch and shoot metrics
                "CATCH_SHOOT_FGM": "catch_shoot_field_goals_made",
                "CATCH_SHOOT_FGA": "catch_shoot_field_goals_attempted",
                "CATCH_SHOOT_FG_PCT": "catch_shoot_field_goal_percentage",
                "CATCH_SHOOT_PTS": "catch_shoot_points",
                "CATCH_SHOOT_FG3M": "catch_shoot_three_pointers_made",
                "CATCH_SHOOT_FG3A": "catch_shoot_three_pointers_attempted",
                "CATCH_SHOOT_FG3_PCT": "catch_shoot_three_point_percentage",
                "CATCH_SHOOT_EFG_PCT": "catch_shoot_effective_field_goal_percentage",

                # Pull up shot metrics
                "PULL_UP_FGM": "pull_up_field_goals_made",
                "PULL_UP_FGA": "pull_up_field_goals_attempted",
                "PULL_UP_FG_PCT": "pull_up_field_goal_percentage",
                "PULL_UP_PTS": "pull_up_points",
                "PULL_UP_FG3M": "pull_up_three_pointers_made",
                "PULL_UP_FG3A": "pull_up_three_pointers_attempted",
                "PULL_UP_FG3_PCT": "pull_up_three_point_percentage",
                "PULL_UP_EFG_PCT": "pull_up_effective_field_goal_percentage",

                # Touch metrics - Paint
                "TOUCHES": "touches",
                "PAINT_TOUCHES": "paint_touches",
                "PAINT_TOUCH_FGM": "paint_touch_field_goals_made",
                "PAINT_TOUCH_FGA": "paint_touch_field_goals_attempted",
                "PAINT_TOUCH_FG_PCT": "paint_touch_field_goal_percentage",
                "PAINT_TOUCH_FTM": "paint_touch_free_throws_made",
                "PAINT_TOUCH_FTA": "paint_touch_free_throws_attempted",
                "PAINT_TOUCH_FT_PCT": "paint_touch_free_throw_percentage",
                "PAINT_TOUCH_PTS": "paint_touch_points",
                "PAINT_TOUCH_PTS_PCT": "paint_touch_points_percentage",
                "PAINT_TOUCH_PASSES": "paint_touch_passes",
                "PAINT_TOUCH_PASSES_PCT": "paint_touch_passes_percentage",
                "PAINT_TOUCH_AST": "paint_touch_assists",
                "PAINT_TOUCH_AST_PCT": "paint_touch_assists_percentage",
                "PAINT_TOUCH_TOV": "paint_touch_turnovers",
                "PAINT_TOUCH_TOV_PCT": "paint_touch_turnovers_percentage",
                "PAINT_TOUCH_FOULS": "paint_touch_fouls",
                "PAINT_TOUCH_FOULS_PCT": "paint_touch_fouls_percentage",

                # Touch metrics - Post
                "POST_TOUCHES": "post_touches",
                "POST_TOUCH_FGM": "post_touch_field_goals_made",
                "POST_TOUCH_FGA": "post_touch_field_goals_attempted",
                "POST_TOUCH_FG_PCT": "post_touch_field_goal_percentage",
                "POST_TOUCH_FTM": "post_touch_free_throws_made",
                "POST_TOUCH_FTA": "post_touch_free_throws_attempted",
                "POST_TOUCH_FT_PCT": "post_touch_free_throw_percentage",
                "POST_TOUCH_PTS": "post_touch_points",
                "POST_TOUCH_PTS_PCT": "post_touch_points_percentage",
                "POST_TOUCH_PASSES": "post_touch_passes",
                "POST_TOUCH_PASSES_PCT": "post_touch_passes_percentage",
                "POST_TOUCH_AST": "post_touch_assists",
                "POST_TOUCH_AST_PCT": "post_touch_assists_percentage",
                "POST_TOUCH_TOV": "post_touch_turnovers",
                "POST_TOUCH_TOV_PCT": "post_touch_turnovers_percentage",
                "POST_TOUCH_FOULS": "post_touch_fouls",
                "POST_TOUCH_FOULS_PCT": "post_touch_fouls_percentage",

                # Touch metrics - Elbow
                "ELBOW_TOUCHES": "elbow_touches",
                "ELBOW_TOUCH_FGM": "elbow_touch_field_goals_made",
                "ELBOW_TOUCH_FGA": "elbow_touch_field_goals_attempted",
                "ELBOW_TOUCH_FG_PCT": "elbow_touch_field_goal_percentage",
                "ELBOW_TOUCH_FTM": "elbow_touch_free_throws_made",
                "ELBOW_TOUCH_FTA": "elbow_touch_free_throws_attempted",
                "ELBOW_TOUCH_FT_PCT": "elbow_touch_free_throw_percentage",
                "ELBOW_TOUCH_PTS": "elbow_touch_points",
                "ELBOW_TOUCH_PASSES": "elbow_touch_passes",
                "ELBOW_TOUCH_AST": "elbow_touch_assists",
                "ELBOW_TOUCH_AST_PCT": "elbow_touch_assists_percentage",
                "ELBOW_TOUCH_TOV": "elbow_touch_turnovers",
                "ELBOW_TOUCH_TOV_PCT": "elbow_touch_turnovers_percentage",
                "ELBOW_TOUCH_FOULS": "elbow_touch_fouls",
                "ELBOW_TOUCH_PASSES_PCT": "elbow_touch_passes_percentage",
                "ELBOW_TOUCH_FOULS_PCT": "elbow_touch_fouls_percentage",
                "ELBOW_TOUCH_PTS_PCT": "elbow_touch_points_percentage",

                # Efficiency metrics
                "EFF_PTS": "efficiency_points",
                "EFF_DRIVE_PTS": "efficiency_drive_points",
                "EFF_DRIVE_FG_PCT": "efficiency_drive_field_goal_percentage",
                "EFF_CATCH_SHOOT_PTS": "efficiency_catch_shoot_points",
                "EFF_CATCH_SHOOT_FG_PCT": "efficiency_catch_shoot_field_goal_percentage",
                "EFF_PULL_UP_PTS": "efficiency_pull_up_points",
                "EFF_PULL_UP_FG_PCT": "efficiency_pull_up_field_goal_percentage",
                "EFF_PAINT_TOUCH_PTS": "efficiency_paint_touch_points",
                "EFF_PAINT_TOUCH_FG_PCT": "efficiency_paint_touch_field_goal_percentage",
                "EFF_POST_TOUCH_PTS": "efficiency_post_touch_points",
                "EFF_POST_TOUCH_FG_PCT": "efficiency_post_touch_field_goal_percentage",
                "EFF_ELBOW_TOUCH_PTS": "efficiency_elbow_touch_points",
                "EFF_ELBOW_TOUCH_FG_PCT": "efficiency_elbow_touch_field_goal_percentage",
                "EFF_FG_PCT": "efficiency_effective_field_goal_percentage",
                # Speed and Distance metrics
                "DIST_FEET": "dist_feet",
                "DIST_MILES": "dist_miles",
                "DIST_MILES_OFF": "dist_miles_off",
                "DIST_MILES_DEF": "dist_miles_def",
                "AVG_SPEED": "avg_speed",
                "AVG_SPEED_OFF": "avg_speed_off",
                "AVG_SPEED_DEF": "avg_speed_def",
                # Passing metrics
                "PASSES_MADE": "passes_made",
                "PASSES_RECEIVED": "passes_received",
                "FT_AST": "ft_ast",
                "SECONDARY_AST": "secondary_ast",
                "POTENTIAL_AST": "potential_ast",
                "AST_POINTS_CREATED": "ast_points_created",
                "AST_ADJ": "ast_adj",
                "AST_TO_PASS_PCT": "ast_to_pass_pct",
                "AST_TO_PASS_PCT_ADJ": "ast_to_pass_pct_adj",
                # Rebounding metrics
                "OREB_CONTEST": "oreb_contest",
                "OREB_UNCONTEST": "oreb_uncontest",
                "OREB_CONTEST_PCT": "oreb_contest_pct",
                "OREB_CHANCES": "oreb_chances",
                "OREB_CHANCE_PCT": "oreb_chance_pct",
                "OREB_CHANCE_DEFER": "oreb_chance_defer",
                "OREB_CHANCE_PCT_ADJ": "oreb_chance_pct_adj",
                "AVG_OREB_DIST": "avg_oreb_dist",
                "DREB_CONTEST": "dreb_contest",
                "DREB_UNCONTEST": "dreb_uncontest",
                "DREB_CONTEST_PCT": "dreb_contest_pct",
                "DREB_CHANCES": "dreb_chances",
                "DREB_CHANCE_PCT": "dreb_chance_pct",
                "DREB_CHANCE_DEFER": "dreb_chance_defer",
                "DREB_CHANCE_PCT_ADJ": "dreb_chance_pct_adj",
                "AVG_DREB_DIST": "avg_dreb_dist",
                "REB_CONTEST": "reb_contest",
                "REB_UNCONTEST": "reb_uncontest",
                "REB_CONTEST_PCT": "reb_contest_pct",
                "REB_CHANCES": "reb_chances",
                "REB_CHANCE_PCT": "reb_chance_pct",
                "REB_CHANCE_DEFER": "reb_chance_defer",
                "REB_CHANCE_PCT_ADJ": "reb_chance_pct_adj",
                "AVG_REB_DIST": "avg_reb_dist"
            }
        }

        # Add metric values to record
        for metric_name, column_name in column_mappings.get(table_name, {}).items():
            if metric_name in metrics_data and player_id in metrics_data[metric_name]:
                record[column_name] = metrics_data[metric_name][player_id]

        return record

    def _insert_player_record(self, cursor, table_name: str, record: Dict[str, Any]):
        """Insert a player record into the database."""
        # Remove None values for cleaner inserts
        clean_record = {k: v for k, v in record.items() if v is not None}

        columns = list(clean_record.keys())
        values = list(clean_record.values())
        placeholders = ",".join(["?" for _ in values])

        sql = f"""
        INSERT OR REPLACE INTO {table_name}
        ({",".join(columns)})
        VALUES ({placeholders})
        """

        cursor.execute(sql, values)

    def get_population_summary(self) -> Dict[str, Any]:
        """Get a summary of the current database population."""
        summary = {}

        table_queries = {
            "players": "SELECT COUNT(*) FROM players",
            "player_season_stats": "SELECT COUNT(DISTINCT player_id) FROM player_season_stats",
            "player_advanced_stats": "SELECT COUNT(DISTINCT player_id) FROM player_advanced_stats",
            "player_tracking_stats": "SELECT COUNT(DISTINCT player_id) FROM player_tracking_stats",
            "seasons": "SELECT DISTINCT season FROM player_season_stats ORDER BY season"
        }

        try:
            cursor = self.schema.conn.cursor()
            for table, query in table_queries.items():
                    try:
                        cursor.execute(query)
                        result = cursor.fetchone()
                        if table == "seasons":
                            summary[table] = [row[0] for row in cursor.fetchall()]
                        else:
                            summary[table] = result[0] if result else 0
                    except Exception as e:
                        logger.warning(f"Could not query {table}: {e}")
                        summary[table] = 0
        except Exception as e:
            logger.error(f"Could not get population summary: {e}")

        return summary


def main():
    """Main entry point for player data population."""
    import argparse

    parser = argparse.ArgumentParser(description="Populate NBA player data")
    parser.add_argument("--season", default="2024-25", help="Season to populate")
    parser.add_argument("--db-path", default="data/nba_stats.db", help="Database path")

    args = parser.parse_args()

    # Initialize populator
    populator = PlayerDataPopulator(args.db_path)

    # Verify schema exists
    if not populator.schema.verify_schema():
        logger.error("Database schema not properly initialized. Run schema.py first.")
        return 1

    # Populate data
    try:
        results = populator.populate_all_player_data(args.season)

        print("\n🎉 Player Data Population Complete!")
        print("=" * 50)
        print(f"Season: {results['season']}")
        print(f"Players affected: {results['players_affected']}")
        print(f"Metrics populated: {results['metrics_populated']}")

        if results['errors']:
            print(f"Errors encountered: {len(results['errors'])}")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")

        # Show database summary
        summary = populator.get_population_summary()
        print("\nDatabase Summary:")
        print(f"  Total players: {summary.get('players', 0)}")
        print(f"  Players with season stats: {summary.get('player_season_stats', 0)}")
        print(f"  Players with advanced stats: {summary.get('player_advanced_stats', 0)}")
        print(f"  Players with tracking stats: {summary.get('player_tracking_stats', 0)}")
        print(f"  Seasons: {summary.get('seasons', [])}")

        return 0

    except Exception as e:
        logger.error(f"Population failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
