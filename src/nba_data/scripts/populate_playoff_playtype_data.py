#!/usr/bin/env python3
"""
Script to populate player playoff playtype statistics from NBA Synergy API.

This script fetches detailed playoff play type breakdowns (Isolation, Pick & Roll, etc.)
for all players in the specified playoff season.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
import sqlite3
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.api.synergy_playtypes_client import SynergyPlaytypesClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PlayoffPlaytypeDataPopulator:
    """Populates player playoff playtype statistics into the database."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.client = SynergyPlaytypesClient()

    def populate_playoff_playtype_data(
        self,
        season_year: str = "2024-25",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Populate playoff playtype data for a season.

        Args:
            season_year: Season in format "2024-25"
            force_refresh: Whether to force refresh cached data

        Returns:
            Dictionary with operation results
        """
        return self._populate_season_playtype_data(
            season_year=season_year,
            season_type="Playoffs",
            force_refresh=force_refresh
        )

    def _populate_season_playtype_data(
        self,
        season_year: str,
        season_type: str,
        force_refresh: bool
    ) -> Dict[str, Any]:
        """
        Internal method to populate playtype data for any season type.
        """
        results = {
            "play_types_processed": 0,
            "records_inserted": 0,
            "records_updated": 0,
            "errors": [],
            "season_year": season_year,
            "season_type": season_type
        }

        logger.info(f"Starting playoff playtype data population for {season_year}")

        # Get data for all play types
        logger.info("Fetching playoff data for all play types...")
        all_playtype_data = self.client.get_all_playtype_stats_for_season(
            season_year=season_year,
            season_type=season_type
        )

        # Process each play type
        for play_type, response_data in all_playtype_data.items():
            try:
                logger.info(f"Processing playoff {play_type} play type...")

                # Parse the response
                records = self.client.parse_playtype_response(response_data)

                if not records:
                    logger.warning(f"No playoff records found for {play_type}")
                    continue

                # Store records in database
                playtype_results = self._store_playtype_records(records, season_type)
                results["records_inserted"] += playtype_results["inserted"]
                results["records_updated"] += playtype_results["updated"]

                if playtype_results["errors"]:
                    results["errors"].extend(playtype_results["errors"])

                results["play_types_processed"] += 1
                logger.info(f"Completed playoff {play_type}: {len(records)} records")

            except Exception as e:
                error_msg = f"Failed to process playoff {play_type}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        logger.info(f"Playoff playtype data population complete: {results['records_inserted']} inserted, {results['records_updated']} updated")
        return results

    def _store_playtype_records(self, records: List[Dict[str, Any]], season_type: str) -> Dict[str, Any]:
        """Store playtype records in the database."""
        results = {"inserted": 0, "updated": 0, "errors": []}

        table_name = "player_playoff_playtype_stats"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for record in records:
                try:
                    # Extract season from season_id or use default
                    season = self.client.extract_season_from_season_id(record.get('season_id', ''))

                    # Prepare data for insertion
                    data = (
                        record['player_id'],
                        season,
                        record['team_id'],
                        record['play_type'],
                        record['type_grouping'],
                        record.get('percentile'),
                        record.get('games_played'),
                        record.get('possession_percentage'),
                        record.get('points_per_possession'),
                        record.get('field_goal_percentage'),
                        record.get('free_throw_possession_percentage'),
                        record.get('turnover_possession_percentage'),
                        record.get('shot_foul_possession_percentage'),
                        record.get('plus_one_possession_percentage'),
                        record.get('score_possession_percentage'),
                        record.get('effective_field_goal_percentage'),
                        record.get('possessions'),
                        record.get('points'),
                        record.get('field_goals_made'),
                        record.get('field_goals_attempted'),
                        record.get('field_goals_missed')
                    )

                    # Insert or replace record
                    cursor.execute(f'''
                        INSERT OR REPLACE INTO {table_name} (
                            player_id, season, team_id, play_type, type_grouping,
                            percentile, games_played, possession_percentage, points_per_possession,
                            field_goal_percentage, free_throw_possession_percentage,
                            turnover_possession_percentage, shot_foul_possession_percentage,
                            plus_one_possession_percentage, score_possession_percentage,
                            effective_field_goal_percentage, possessions, points,
                            field_goals_made, field_goals_attempted, field_goals_missed
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', data)

                    # Check if this was an insert or update
                    if cursor.rowcount > 0:
                        results["inserted"] += 1
                    else:
                        results["updated"] += 1

                except Exception as e:
                    error_msg = f"Failed to store playoff record for player {record.get('player_id', 'unknown')}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

            conn.commit()

        return results

    def validate_playoff_playtype_data(self) -> Dict[str, Any]:
        """Validate the quality of stored playoff playtype data."""
        return self._validate_playtype_data("Playoffs")

    def _validate_playtype_data(self, season_type: str) -> Dict[str, Any]:
        """Internal validation method."""
        validation_results = {
            "total_records": 0,
            "unique_players": 0,
            "unique_play_types": 0,
            "play_type_distribution": {},
            "data_quality_checks": {}
        }

        table_name = "player_playoff_playtype_stats"

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Basic counts
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                validation_results["total_records"] = cursor.fetchone()[0]

                cursor.execute(f"SELECT COUNT(DISTINCT player_id) FROM {table_name}")
                validation_results["unique_players"] = cursor.fetchone()[0]

                cursor.execute(f"SELECT COUNT(DISTINCT play_type) FROM {table_name}")
                validation_results["unique_play_types"] = cursor.fetchone()[0]

                # Play type distribution
                cursor.execute(f"SELECT play_type, COUNT(*) FROM {table_name} GROUP BY play_type")
                validation_results["play_type_distribution"] = {row[0]: row[1] for row in cursor.fetchall()}

                # Data quality checks
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE percentile IS NULL")
                validation_results["data_quality_checks"]["null_percentiles"] = cursor.fetchone()[0]

                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE points_per_possession < 0 OR points_per_possession > 3")
                validation_results["data_quality_checks"]["invalid_ppp"] = cursor.fetchone()[0]

                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE field_goal_percentage < 0 OR field_goal_percentage > 1")
                validation_results["data_quality_checks"]["invalid_fg_pct"] = cursor.fetchone()[0]

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            validation_results["error"] = str(e)

        return validation_results


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description='Populate NBA player playoff playtype statistics')
    parser.add_argument('--season', default='2024-25', help='Season year (e.g., 2024-25)')
    parser.add_argument('--force-refresh', action='store_true', help='Force refresh of cached data')
    parser.add_argument('--validate-only', action='store_true', help='Only run validation, do not populate')

    args = parser.parse_args()

    populator = PlayoffPlaytypeDataPopulator()

    if args.validate_only:
        print("🔍 Validating existing playoff playtype data...")
        validation = populator.validate_playoff_playtype_data()
        print("Validation Results:")
        print(f"  Total Records: {validation['total_records']}")
        print(f"  Unique Players: {validation['unique_players']}")
        print(f"  Unique Play Types: {validation['unique_play_types']}")
        print(f"  Play Type Distribution: {validation['play_type_distribution']}")
        print(f"  Data Quality: {validation['data_quality_checks']}")
        return

    print(f"🏀 Populating {args.season} playoff playtype data...")

    results = populator.populate_playoff_playtype_data(
        season_year=args.season,
        force_refresh=args.force_refresh
    )

    print("\n📊 Playoff Population Results:")
    print(f"✅ Play Types Processed: {results['play_types_processed']}")
    print(f"✅ Records Inserted: {results['records_inserted']}")
    print(f"✅ Records Updated: {results['records_updated']}")
    print(f"❌ Errors: {len(results['errors'])}")

    if results['errors']:
        print("\nFirst few errors:")
        for error in results['errors'][:3]:
            print(f"  - {error}")

    # Run validation
    print("\n🔍 Running validation...")
    validation = populator.validate_playoff_playtype_data()
    print("Validation Results:")
    print(f"  Total Records: {validation['total_records']}")
    print(f"  Unique Players: {validation['unique_players']}")
    print(f"  Play Types: {validation['unique_play_types']}")
    print(f"  Records per Play Type: {validation['play_type_distribution']}")

    print("\n✅ Playoff playtype data population complete!")


if __name__ == "__main__":
    main()
