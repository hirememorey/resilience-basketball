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
                "GP", "GS", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS",  # Basic counts
                "FGPCT", "FG3PCT", "FTPCT"  # Basic percentages
            ],
            "player_advanced_stats": [
                "TSPCT", "USGPCT", "ORTG", "DRTG", "NRTG",  # Advanced metrics
                "TRBPCT", "ASTPCT", "PIE"  # Advanced percentages
            ],
            "player_tracking_stats": [
                "DRIVES", "DRIVE_FGM"  # Tracking metrics
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
                "GS": "games_started",
                "MIN": "minutes_played",
                "PTS": "points",
                "REB": "total_rebounds",
                "AST": "assists",
                "STL": "steals",
                "BLK": "blocks",
                "TOV": "turnovers",
                "PF": "personal_fouls",
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
                "PIE": "pie"
            },
            "player_tracking_stats": {
                "DRIVES": "drives",
                "DRIVE_FGM": "drive_field_goals_made"
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
