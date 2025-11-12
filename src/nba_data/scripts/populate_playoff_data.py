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
                "GP", "GS", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS",  # Basic counts
                "FGPCT", "FG3PCT", "FTPCT"  # Basic percentages
            ],
            "player_playoff_advanced_stats": [
                "TSPCT", "USGPCT", "ORTG", "DRTG", "NRTG",  # Advanced metrics
                "TRBPCT", "ASTPCT", "PIE"  # Advanced percentages
            ],
            "player_playoff_tracking_stats": [
                "DRIVES", "DRIVE_FGM"  # Tracking metrics (will expand as needed)
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

            # Advanced stats mappings
            "TSPCT": "TS_PCT",
            "USGPCT": "USG_PCT",
            "ORTG": "OFF_RATING",
            "DRTG": "DEF_RATING",
            "NRTG": "NET_RATING",
            "TRBPCT": "REB_PCT",
            "ASTPCT": "AST_PCT",
            "PIE": "PIE",

            # Tracking stats mappings
            "DRIVES": "DRIVES",
            "DRIVE_FGM": "DRIVE_FGM"
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

            # Advanced stats mappings
            "TSPCT": "true_shooting_percentage",
            "USGPCT": "usage_percentage",
            "ORTG": "offensive_rating",
            "DRTG": "defensive_rating",
            "NRTG": "net_rating",
            "TRBPCT": "rebound_percentage",
            "ASTPCT": "assist_percentage",
            "PIE": "pie",

            # Tracking stats mappings
            "DRIVES": "drives",
            "DRIVE_FGM": "drive_field_goals_made"
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
