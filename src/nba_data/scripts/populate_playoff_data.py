"""
Script to populate playoff player data from NBA API into our database.

This script fetches playoff player statistics from the NBA API and loads them into
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


class PlayoffDataPopulator:
    """Populates playoff player data from NBA API into database."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.schema = NBADatabaseSchema(db_path)
        self.fetcher = create_data_fetcher()

    def populate_all_playoff_data(self, season: str = "2024-25") -> Dict[str, Any]:
        """
        Populate all playoff player data for a given season.

        Args:
            season: Season to populate data for

        Returns:
            Summary of population results
        """
        logger.info(f"Starting playoff data population for season {season}")

        results = {
            "season": season,
            "metrics_populated": 0,
            "players_affected": 0,
            "errors": []
        }

        # Define which metrics go to which playoff tables
        table_mappings = {
            "player_playoff_stats": [
                "GP", "GS", "MIN", "FGM", "FGA", "FG3M", "FG3A", "FTM", "FTA", "OREB", "DREB",  # Shot and rebound stats
                "PTS", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS",  # Basic counts
                "FGPCT", "FG3PCT", "FTPCT"  # Basic percentages
            ],
            "player_playoff_advanced_stats": [
                # Basic game info
                "AGE", "GP", "W", "L", "W_PCT", "MIN",
                # Advanced metrics
                "TS_PCT", "USG_PCT", "OFF_RATING", "DEF_RATING", "NET_RATING",
                # Percentage stats
                "REB_PCT", "AST_PCT", "AST_TO", "AST_RATIO", "OREB_PCT", "DREB_PCT", "TM_TOV_PCT", "EFG_PCT", "PACE", "PIE"
            ],
            "player_playoff_tracking_stats": [
                # Drive metrics
                "DRIVES", "DRIVE_FGM", "DRIVE_FGA", "DRIVE_FG_PCT", "DRIVE_FTM", "DRIVE_FTA",
                "DRIVE_FT_PCT", "DRIVE_PTS", "DRIVE_PTS_PCT", "DRIVE_PASSES", "DRIVE_PASSES_PCT",
                "DRIVE_AST", "DRIVE_AST_PCT", "DRIVE_TOV", "DRIVE_TOV_PCT", "DRIVE_PF", "DRIVE_PF_PCT",

                # Catch and shoot metrics
                "CATCH_SHOOT_FGM", "CATCH_SHOOT_FGA", "CATCH_SHOOT_FG_PCT", "CATCH_SHOOT_PTS",
                "CATCH_SHOOT_FG3M", "CATCH_SHOOT_FG3A", "CATCH_SHOOT_FG3_PCT", "CATCH_SHOOT_EFG_PCT",

                # Pull up shot metrics
                "PULL_UP_FGM", "PULL_UP_FGA", "PULL_UP_FG_PCT", "PULL_UP_PTS",
                "PULL_UP_FG3M", "PULL_UP_FG3A", "PULL_UP_FG3_PCT", "PULL_UP_EFG_PCT",

                # Paint touch metrics
                "PAINT_TOUCHES", "PAINT_TOUCH_FGM", "PAINT_TOUCH_FGA", "PAINT_TOUCH_FG_PCT",
                "PAINT_TOUCH_FTM", "PAINT_TOUCH_FTA", "PAINT_TOUCH_FT_PCT", "PAINT_TOUCH_PTS",
                "PAINT_TOUCH_PTS_PCT", "PAINT_TOUCH_PASSES", "PAINT_TOUCH_PASSES_PCT",
                "PAINT_TOUCH_AST", "PAINT_TOUCH_AST_PCT", "PAINT_TOUCH_TOV", "PAINT_TOUCH_TOV_PCT",
                "PAINT_TOUCH_FOULS", "PAINT_TOUCH_FOULS_PCT",

                # Post touch metrics
                "POST_TOUCHES", "POST_TOUCH_FGM", "POST_TOUCH_FGA", "POST_TOUCH_FG_PCT",
                "POST_TOUCH_FTM", "POST_TOUCH_FTA", "POST_TOUCH_FT_PCT", "POST_TOUCH_PTS",
                "POST_TOUCH_PTS_PCT", "POST_TOUCH_PASSES", "POST_TOUCH_PASSES_PCT",
                "POST_TOUCH_AST", "POST_TOUCH_AST_PCT", "POST_TOUCH_TOV", "POST_TOUCH_TOV_PCT",
                "POST_TOUCH_FOULS", "POST_TOUCH_FOULS_PCT",

                # Elbow touch metrics
                "ELBOW_TOUCHES", "ELBOW_TOUCH_FGM", "ELBOW_TOUCH_FGA", "ELBOW_TOUCH_FG_PCT",
                "ELBOW_TOUCH_FTM", "ELBOW_TOUCH_FTA", "ELBOW_TOUCH_FT_PCT", "ELBOW_TOUCH_PTS",
                "ELBOW_TOUCH_PASSES", "ELBOW_TOUCH_AST", "ELBOW_TOUCH_AST_PCT",
                "ELBOW_TOUCH_TOV", "ELBOW_TOUCH_TOV_PCT", "ELBOW_TOUCH_FOULS",
                "ELBOW_TOUCH_PASSES_PCT", "ELBOW_TOUCH_FOULS_PCT", "ELBOW_TOUCH_PTS_PCT",

                # Efficiency metrics
                "EFF_PTS", "EFF_DRIVE_PTS", "EFF_DRIVE_FG_PCT", "EFF_CATCH_SHOOT_PTS",
                "EFF_CATCH_SHOOT_FG_PCT", "EFF_PULL_UP_PTS", "EFF_PULL_UP_FG_PCT",
                "EFF_PAINT_TOUCH_PTS", "EFF_PAINT_TOUCH_FG_PCT", "EFF_POST_TOUCH_PTS",
                "EFF_POST_TOUCH_FG_PCT", "EFF_ELBOW_TOUCH_PTS", "EFF_ELBOW_TOUCH_FG_PCT",
                "EFF_EFG_PCT"
            ]
        }

        # Fetch all available playoff metrics
        logger.info("Fetching all available playoff metrics from NBA API...")
        all_metric_data = self.fetcher.fetch_all_available_playoff_metrics(season)

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
            cursor = self.schema.conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_playoff_stats WHERE season = ?", (season,))
            results["players_affected"] = cursor.fetchone()[0]
            cursor.close()
        except Exception as e:
            logger.warning(f"Could not count affected players: {e}")

        logger.info(f"Playoff data population complete for {season}")
        logger.info(f"Results: {results['players_affected']} players, {results['metrics_populated']} metrics")

        return results

    def _populate_table(self, table_name: str, metric_names: List[str], all_data: Dict[str, Dict], season: str) -> int:
        """
        Populate a specific table with metric data.

        Args:
            table_name: Name of the table to populate
            metric_names: List of metric names to populate
            all_data: Dictionary containing all fetched data
            season: Season string

        Returns:
            Number of metrics successfully populated
        """
        populated_count = 0

        # Get the data for this table
        table_data = all_data.get(table_name, {})
        if not table_data:
            logger.warning(f"No data found for table {table_name}")
            return 0

        # Process each metric for this table
        for metric_name in metric_names:
            if metric_name in table_data:
                metric_data = table_data[metric_name]
                try:
                    # Insert/update the metric data
                    inserted_count = self._insert_metric_data(table_name, metric_name, metric_data, season)
                    populated_count += inserted_count
                    logger.debug(f"  ✓ {metric_name}: {inserted_count} records")

                except Exception as e:
                    logger.error(f"  ✗ Failed to populate {metric_name}: {str(e)}")
            else:
                logger.warning(f"  ⚠ {metric_name} not found in API response for {table_name}")

        return populated_count

    def _insert_metric_data(self, table_name: str, metric_name: str, metric_data: List[Dict], season: str) -> int:
        """
        Insert metric data into the database.

        Args:
            table_name: Target table name
            metric_name: Name of the metric
            metric_data: List of metric data records
            season: Season string

        Returns:
            Number of records inserted/updated
        """
        if not metric_data:
            return 0

        cursor = self.schema.conn.cursor()
        inserted_count = 0

        try:
            for record in metric_data:
                try:
                    player_id = record.get("PLAYER_ID")
                    team_id = record.get("TEAM_ID", 0)
                    # For playoff data, map metric name to API column name
                    api_column = self._get_api_column_name(metric_name)
                    value = record.get(api_column)

                    if player_id is None:
                        logger.warning(f"No PLAYER_ID in record: {record}")
                        continue

                    # Build dynamic column name mapping
                    column_mapping = self._get_column_mapping(table_name, metric_name)

                    # Insert or update the record
                    self._upsert_player_stat(cursor, table_name, player_id, team_id, season, column_mapping, value)
                    inserted_count += 1

                except Exception as e:
                    logger.error(f"Failed to insert {metric_name} for player {record.get('PLAYER_ID')}: {str(e)}")

            self.schema.conn.commit()

        finally:
            cursor.close()

        return inserted_count

    def _get_api_column_name(self, metric_name: str) -> str:
        """
        Get the API column name for a given metric name.

        Args:
            metric_name: Internal metric name

        Returns:
            API column name
        """
        # Define mappings from internal metric names to API column names
        api_mappings = {
            # Basic stats mappings
            "GP": "GP",
            "GS": "GS",
            "MIN": "MIN",
            "FGM": "FGM",
            "FGA": "FGA",
            "FG3M": "FG3M",
            "FG3A": "FG3A",
            "FTM": "FTM",
            "FTA": "FTA",
            "OREB": "OREB",
            "DREB": "DREB",
            "PTS": "PTS",
            "REB": "REB",
            "AST": "AST",
            "STL": "STL",
            "BLK": "BLK",
            "TOV": "TOV",
            "PF": "PF",
            "PLUS_MINUS": "PLUS_MINUS",
            "FGPCT": "FG_PCT",
            "FG3PCT": "FG3_PCT",
            "FTPCT": "FT_PCT",

            # Advanced stats mappings - comprehensive coverage
            "AGE": "AGE",
            "GP": "GP",  # Also used for advanced stats
            "W": "W",
            "L": "L",
            "W_PCT": "W_PCT",
            "MIN": "MIN",  # Also used for advanced stats
            "TS_PCT": "TS_PCT",
            "USG_PCT": "USG_PCT",
            "OFF_RATING": "OFF_RATING",
            "DEF_RATING": "DEF_RATING",
            "NET_RATING": "NET_RATING",
            "REB_PCT": "REB_PCT",
            "AST_PCT": "AST_PCT",
            "AST_TO": "AST_TO",
            "AST_RATIO": "AST_RATIO",
            "OREB_PCT": "OREB_PCT",
            "DREB_PCT": "DREB_PCT",
            "TM_TOV_PCT": "TM_TOV_PCT",
            "EFG_PCT": "EFG_PCT",
            "PACE": "PACE",
            "PIE": "PIE",

            # Tracking stats mappings - comprehensive coverage to match API
            # Drive metrics
            "DRIVES": "DRIVES",
            "DRIVE_FGM": "DRIVE_FGM",
            "DRIVE_FGA": "DRIVE_FGA",
            "DRIVE_FG_PCT": "DRIVE_FG_PCT",
            "DRIVE_FTM": "DRIVE_FTM",
            "DRIVE_FTA": "DRIVE_FTA",
            "DRIVE_FT_PCT": "DRIVE_FT_PCT",
            "DRIVE_PTS": "DRIVE_PTS",
            "DRIVE_PTS_PCT": "DRIVE_PTS_PCT",
            "DRIVE_PASSES": "DRIVE_PASSES",
            "DRIVE_PASSES_PCT": "DRIVE_PASSES_PCT",
            "DRIVE_AST": "DRIVE_AST",
            "DRIVE_AST_PCT": "DRIVE_AST_PCT",
            "DRIVE_TOV": "DRIVE_TOV",
            "DRIVE_TOV_PCT": "DRIVE_TOV_PCT",
            "DRIVE_PF": "DRIVE_PF",
            "DRIVE_PF_PCT": "DRIVE_PF_PCT",

            # Catch and shoot metrics
            "CATCH_SHOOT_FGM": "CATCH_SHOOT_FGM",
            "CATCH_SHOOT_FGA": "CATCH_SHOOT_FGA",
            "CATCH_SHOOT_FG_PCT": "CATCH_SHOOT_FG_PCT",
            "CATCH_SHOOT_PTS": "CATCH_SHOOT_PTS",
            "CATCH_SHOOT_FG3M": "CATCH_SHOOT_FG3M",
            "CATCH_SHOOT_FG3A": "CATCH_SHOOT_FG3A",
            "CATCH_SHOOT_FG3_PCT": "CATCH_SHOOT_FG3_PCT",
            "CATCH_SHOOT_EFG_PCT": "CATCH_SHOOT_EFG_PCT",

            # Pull up shot metrics
            "PULL_UP_FGM": "PULL_UP_FGM",
            "PULL_UP_FGA": "PULL_UP_FGA",
            "PULL_UP_FG_PCT": "PULL_UP_FG_PCT",
            "PULL_UP_PTS": "PULL_UP_PTS",
            "PULL_UP_FG3M": "PULL_UP_FG3M",
            "PULL_UP_FG3A": "PULL_UP_FG3A",
            "PULL_UP_FG3_PCT": "PULL_UP_FG3_PCT",
            "PULL_UP_EFG_PCT": "PULL_UP_EFG_PCT",

            # Paint touch metrics
            "PAINT_TOUCHES": "PAINT_TOUCHES",
            "PAINT_TOUCH_FGM": "PAINT_TOUCH_FGM",
            "PAINT_TOUCH_FGA": "PAINT_TOUCH_FGA",
            "PAINT_TOUCH_FG_PCT": "PAINT_TOUCH_FG_PCT",
            "PAINT_TOUCH_FTM": "PAINT_TOUCH_FTM",
            "PAINT_TOUCH_FTA": "PAINT_TOUCH_FTA",
            "PAINT_TOUCH_FT_PCT": "PAINT_TOUCH_FT_PCT",
            "PAINT_TOUCH_PTS": "PAINT_TOUCH_PTS",
            "PAINT_TOUCH_PTS_PCT": "PAINT_TOUCH_PTS_PCT",
            "PAINT_TOUCH_PASSES": "PAINT_TOUCH_PASSES",
            "PAINT_TOUCH_PASSES_PCT": "PAINT_TOUCH_PASSES_PCT",
            "PAINT_TOUCH_AST": "PAINT_TOUCH_AST",
            "PAINT_TOUCH_AST_PCT": "PAINT_TOUCH_AST_PCT",
            "PAINT_TOUCH_TOV": "PAINT_TOUCH_TOV",
            "PAINT_TOUCH_TOV_PCT": "PAINT_TOUCH_TOV_PCT",
            "PAINT_TOUCH_FOULS": "PAINT_TOUCH_FOULS",
            "PAINT_TOUCH_FOULS_PCT": "PAINT_TOUCH_FOULS_PCT",

            # Post touch metrics
            "POST_TOUCHES": "POST_TOUCHES",
            "POST_TOUCH_FGM": "POST_TOUCH_FGM",
            "POST_TOUCH_FGA": "POST_TOUCH_FGA",
            "POST_TOUCH_FG_PCT": "POST_TOUCH_FG_PCT",
            "POST_TOUCH_FTM": "POST_TOUCH_FTM",
            "POST_TOUCH_FTA": "POST_TOUCH_FTA",
            "POST_TOUCH_FT_PCT": "POST_TOUCH_FT_PCT",
            "POST_TOUCH_PTS": "POST_TOUCH_PTS",
            "POST_TOUCH_PTS_PCT": "POST_TOUCH_PTS_PCT",
            "POST_TOUCH_PASSES": "POST_TOUCH_PASSES",
            "POST_TOUCH_PASSES_PCT": "POST_TOUCH_PASSES_PCT",
            "POST_TOUCH_AST": "POST_TOUCH_AST",
            "POST_TOUCH_AST_PCT": "POST_TOUCH_AST_PCT",
            "POST_TOUCH_TOV": "POST_TOUCH_TOV",
            "POST_TOUCH_TOV_PCT": "POST_TOUCH_TOV_PCT",
            "POST_TOUCH_FOULS": "POST_TOUCH_FOULS",
            "POST_TOUCH_FOULS_PCT": "POST_TOUCH_FOULS_PCT",

            # Elbow touch metrics
            "ELBOW_TOUCHES": "ELBOW_TOUCHES",
            "ELBOW_TOUCH_FGM": "ELBOW_TOUCH_FGM",
            "ELBOW_TOUCH_FGA": "ELBOW_TOUCH_FGA",
            "ELBOW_TOUCH_FG_PCT": "ELBOW_TOUCH_FG_PCT",
            "ELBOW_TOUCH_FTM": "ELBOW_TOUCH_FTM",
            "ELBOW_TOUCH_FTA": "ELBOW_TOUCH_FTA",
            "ELBOW_TOUCH_FT_PCT": "ELBOW_TOUCH_FT_PCT",
            "ELBOW_TOUCH_PTS": "ELBOW_TOUCH_PTS",
            "ELBOW_TOUCH_PASSES": "ELBOW_TOUCH_PASSES",
            "ELBOW_TOUCH_AST": "ELBOW_TOUCH_AST",
            "ELBOW_TOUCH_AST_PCT": "ELBOW_TOUCH_AST_PCT",
            "ELBOW_TOUCH_TOV": "ELBOW_TOUCH_TOV",
            "ELBOW_TOUCH_TOV_PCT": "ELBOW_TOUCH_TOV_PCT",
            "ELBOW_TOUCH_FOULS": "ELBOW_TOUCH_FOULS",
            "ELBOW_TOUCH_PASSES_PCT": "ELBOW_TOUCH_PASSES_PCT",
            "ELBOW_TOUCH_FOULS_PCT": "ELBOW_TOUCH_FOULS_PCT",
            "ELBOW_TOUCH_PTS_PCT": "ELBOW_TOUCH_PTS_PCT",

            # Efficiency metrics
            "EFF_PTS": "POINTS",
            "EFF_DRIVE_PTS": "DRIVE_PTS",
            "EFF_DRIVE_FG_PCT": "DRIVE_FG_PCT",
            "EFF_CATCH_SHOOT_PTS": "CATCH_SHOOT_PTS",
            "EFF_CATCH_SHOOT_FG_PCT": "CATCH_SHOOT_FG_PCT",
            "EFF_PULL_UP_PTS": "PULL_UP_PTS",
            "EFF_PULL_UP_FG_PCT": "PULL_UP_FG_PCT",
            "EFF_PAINT_TOUCH_PTS": "PAINT_TOUCH_PTS",
            "EFF_PAINT_TOUCH_FG_PCT": "PAINT_TOUCH_FG_PCT",
            "EFF_POST_TOUCH_PTS": "POST_TOUCH_PTS",
            "EFF_POST_TOUCH_FG_PCT": "POST_TOUCH_FG_PCT",
            "EFF_ELBOW_TOUCH_PTS": "ELBOW_TOUCH_PTS",
            "EFF_ELBOW_TOUCH_FG_PCT": "ELBOW_TOUCH_FG_PCT",
            "EFF_EFG_PCT": "EFF_FG_PCT"
        }

        return api_mappings.get(metric_name, metric_name)

    def _get_column_mapping(self, table_name: str, metric_name: str) -> str:
        """
        Get the database column name for a given metric.

        Args:
            table_name: Table name
            metric_name: API metric name

        Returns:
            Database column name
        """
        # Define mappings from API metric names to database column names
        column_mappings = {
            # Basic stats mappings
            "GP": "games_played",
            "GS": "games_started",
            "MIN": "minutes_played",
            "FGM": "field_goals_made",
            "FGA": "field_goals_attempted",
            "FG3M": "three_pointers_made",
            "FG3A": "three_pointers_attempted",
            "FTM": "free_throws_made",
            "FTA": "free_throws_attempted",
            "OREB": "offensive_rebounds",
            "DREB": "defensive_rebounds",
            "PTS": "points",
            "REB": "total_rebounds",
            "AST": "assists",
            "STL": "steals",
            "BLK": "blocks",
            "TOV": "turnovers",
            "PF": "personal_fouls",
            "PLUS_MINUS": "plus_minus",
            "FGPCT": "field_goal_percentage",
            "FG3PCT": "three_point_percentage",
            "FTPCT": "free_throw_percentage",

            # Advanced stats mappings - comprehensive coverage
            "AGE": "age",
            "GP": "games_played",  # Also used for advanced stats
            "W": "wins",
            "L": "losses",
            "W_PCT": "win_percentage",
            "MIN": "minutes_played",  # Also used for advanced stats
            "TS_PCT": "true_shooting_percentage",
            "USG_PCT": "usage_percentage",
            "OFF_RATING": "offensive_rating",
            "DEF_RATING": "defensive_rating",
            "NET_RATING": "net_rating",
            "REB_PCT": "rebound_percentage",
            "AST_PCT": "assist_percentage",
            "AST_TO": "assist_to_turnover_ratio",
            "AST_RATIO": "assist_ratio",
            "OREB_PCT": "offensive_rebound_percentage",
            "DREB_PCT": "defensive_rebound_percentage",
            "TM_TOV_PCT": "turnover_percentage",
            "EFG_PCT": "effective_field_goal_percentage",
            "PACE": "pace",
            "PIE": "pie",

            # Tracking stats mappings - comprehensive coverage to match regular season
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

            # Paint touch metrics
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

            # Post touch metrics
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

            # Elbow touch metrics
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
            "EFF_EFG_PCT": "efficiency_effective_field_goal_percentage"
        }

        return column_mappings.get(metric_name, metric_name.lower())

    def _upsert_player_stat(self, cursor, table_name: str, player_id: int, team_id: int,
                          season: str, column_name: str, value: Any) -> None:
        """
        Insert or update a player stat record.

        Args:
            cursor: Database cursor
            table_name: Target table name
            player_id: Player ID
            team_id: Team ID
            season: Season string
            column_name: Column name to update
            value: Value to set
        """
        # First, try to insert a new record
        columns = ["player_id", "season", "team_id", column_name]
        placeholders = ["?", "?", "?", "?"]
        values = [player_id, season, team_id, value]

        # Add additional required columns for playoff stats
        if "advanced" in table_name:
            columns.extend(["age", "games_played", "wins", "losses", "win_percentage", "minutes_played"])
            placeholders.extend(["?", "?", "?", "?", "?", "?"])
            # These will be populated by the base stats, so use NULL for now
            values.extend([None, None, None, None, None, None])

        insert_sql = f"""
            INSERT OR IGNORE INTO {table_name}
            ({", ".join(columns)})
            VALUES ({", ".join(placeholders)})
        """

        cursor.execute(insert_sql, values)

        # Then update the specific column
        update_sql = f"""
            UPDATE {table_name}
            SET {column_name} = ?, updated_at = CURRENT_TIMESTAMP
            WHERE player_id = ? AND season = ? AND team_id = ?
        """

        cursor.execute(update_sql, [value, player_id, season, team_id])


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Populate playoff player data from NBA API")
    parser.add_argument("--season", default="2024-25", help="Season to populate")
    parser.add_argument("--db-path", default="data/nba_stats.db", help="Database path")

    args = parser.parse_args()

    populator = PlayoffDataPopulator(args.db_path)
    results = populator.populate_all_playoff_data(args.season)

    print("\n📊 Playoff Data Population Results:")
    print(f"✅ Season: {results['season']}")
    print(f"✅ Players affected: {results['players_affected']}")
    print(f"✅ Metrics populated: {results['metrics_populated']}")
    print(f"❌ Errors: {len(results['errors'])}")

    if results['errors']:
        print("\nFirst few errors:")
        for error in results['errors'][:3]:
            print(f"  - {error}")

    # Exit with appropriate code
    return 0 if len(results['errors']) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
