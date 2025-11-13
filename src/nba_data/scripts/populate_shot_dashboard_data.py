#!/usr/bin/env python3
"""
Script to populate player shot dashboard statistics from NBA Stats API.

This script fetches shot statistics filtered by closest defender distance ranges
for all players in the specified season.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
import sqlite3
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.api.shot_dashboard_client import ShotDashboardClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ShotDashboardDataPopulator:
    """Populates player shot dashboard statistics into the database."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.client = ShotDashboardClient()

    def populate_season_shot_dashboard_data(
        self,
        season_year: str = "2024-25",
        season_type: str = "Regular Season",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Populate shot dashboard data for an entire season.

        Args:
            season_year: Season in format "2024-25"
            season_type: "Regular Season" or "Playoffs"
            force_refresh: Whether to force refresh cached data

        Returns:
            Dictionary with operation results
        """
        results = {
            "defender_distances_processed": 0,
            "shot_clock_ranges_processed": 0,
            "dribble_ranges_processed": 0,
            "records_inserted": 0,
            "records_updated": 0,
            "errors": [],
            "season_year": season_year,
            "season_type": season_type
        }

        logger.info(f"Starting shot dashboard data population for {season_year} {season_type}")

        # Determine table name based on season type
        table_name = "player_shot_dashboard_stats" if season_type == "Regular Season" else "player_playoff_shot_dashboard_stats"

        # Get data for all defender distance ranges
        logger.info("Fetching data for all defender distance ranges...")
        all_defender_data = self.client.get_all_defender_distances_for_season(
            season_year=season_year,
            season_type=season_type
        )

        # Process each defender distance range
        for def_dist_range, response_data in all_defender_data.items():
            try:
                logger.info(f"Processing {def_dist_range} defender distance...")

                # Parse the response
                records = self.client.parse_shot_dashboard_response(response_data, close_def_dist_range=def_dist_range)

                if not records:
                    logger.warning(f"No records found for {def_dist_range}")
                    continue

                # Insert/update records in database
                inserted, updated = self._insert_shot_dashboard_records(
                    records, table_name, season_year, season_type
                )

                results["records_inserted"] += inserted
                results["records_updated"] += updated
                results["defender_distances_processed"] += 1

                logger.info(f"Processed {len(records)} records for {def_dist_range}")

            except Exception as e:
                error_msg = f"Failed to process {def_dist_range}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        # Get data for all shot clock ranges
        logger.info("Fetching data for all shot clock ranges...")
        all_shot_clock_data = self.client.get_all_shot_clock_ranges_for_season(
            season_year=season_year,
            season_type=season_type
        )

        # Process each shot clock range
        for shot_clock_range, response_data in all_shot_clock_data.items():
            try:
                logger.info(f"Processing {shot_clock_range} shot clock range...")

                # Parse the response
                records = self.client.parse_shot_dashboard_response(response_data, shot_clock_range=shot_clock_range)

                if not records:
                    logger.warning(f"No records found for {shot_clock_range}")
                    continue

                # Insert/update records in database
                inserted, updated = self._insert_shot_dashboard_records(
                    records, table_name, season_year, season_type
                )

                results["records_inserted"] += inserted
                results["records_updated"] += updated
                results["shot_clock_ranges_processed"] = results.get("shot_clock_ranges_processed", 0) + 1

                logger.info(f"Processed {len(records)} records for {shot_clock_range}")

            except Exception as e:
                error_msg = f"Failed to process {shot_clock_range}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        # Get data for all dribble ranges
        logger.info("Fetching data for all dribble ranges...")
        all_dribble_data = self.client.get_all_dribble_ranges_for_season(
            season_year=season_year,
            season_type=season_type
        )

        # Process each dribble range
        for dribble_range, response_data in all_dribble_data.items():
            try:
                logger.info(f"Processing {dribble_range} dribble range...")

                # Parse the response
                records = self.client.parse_shot_dashboard_response(response_data, dribble_range=dribble_range)

                if not records:
                    logger.warning(f"No records found for {dribble_range}")
                    continue

                # Insert/update records in database
                inserted, updated = self._insert_shot_dashboard_records(
                    records, table_name, season_year, season_type
                )

                results["records_inserted"] += inserted
                results["records_updated"] += updated
                results["dribble_ranges_processed"] = results.get("dribble_ranges_processed", 0) + 1

                logger.info(f"Processed {len(records)} records for {dribble_range}")

            except Exception as e:
                error_msg = f"Failed to process {dribble_range}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        logger.info(f"Shot dashboard data population completed for {season_year} {season_type}")
        logger.info(f"Processed {results['defender_distances_processed']} defender distance ranges")
        logger.info(f"Processed {results.get('shot_clock_ranges_processed', 0)} shot clock ranges")
        logger.info(f"Processed {results.get('dribble_ranges_processed', 0)} dribble ranges")
        logger.info(f"Inserted {results['records_inserted']} records, updated {results['records_updated']} records")

        return results

    def _insert_shot_dashboard_records(
        self,
        records: List[Dict[str, Any]],
        table_name: str,
        season_year: str,
        season_type: str
    ) -> tuple[int, int]:
        """
        Insert or update shot dashboard records in the database.

        Args:
            records: List of parsed shot dashboard records
            table_name: Target table name
            season_year: Season year
            season_type: Season type

        Returns:
            Tuple of (records_inserted, records_updated)
        """
        inserted = 0
        updated = 0

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for record in records:
                try:
                    # Prepare the record data
                    record_data = (
                        record.get('player_id'),
                        record.get('season'),
                        record.get('team_id'),
                        record.get('close_def_dist_range'),
                        record.get('shot_clock_range'),
                        record.get('dribble_range'),
                        record.get('shot_dist_range'),
                        record.get('player_name'),
                        record.get('team_abbreviation'),
                        record.get('team_name'),
                        record.get('age'),
                        record.get('gp'),
                        record.get('g'),
                        record.get('fga_frequency'),
                        record.get('fgm'),
                        record.get('fga'),
                        record.get('fg_pct'),
                        record.get('efg_pct'),
                        record.get('fg2a_frequency'),
                        record.get('fg2m'),
                        record.get('fg2a'),
                        record.get('fg2_pct'),
                        record.get('fg3a_frequency'),
                        record.get('fg3m'),
                        record.get('fg3a'),
                        record.get('fg3_pct')
                    )

                    # Try to insert first (will fail if record exists due to PRIMARY KEY constraint)
                    insert_sql = f"""
                        INSERT INTO {table_name} (
                            player_id, season, team_id, close_def_dist_range, shot_clock_range, dribble_range, shot_dist_range,
                            player_name, team_abbreviation, team_name, age, gp, g,
                            fga_frequency, fgm, fga, fg_pct, efg_pct,
                            fg2a_frequency, fg2m, fg2a, fg2_pct,
                            fg3a_frequency, fg3m, fg3a, fg3_pct
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """

                    try:
                        cursor.execute(insert_sql, record_data)
                        inserted += 1
                    except sqlite3.IntegrityError:
                        # Record exists, update instead
                        update_sql = f"""
                            UPDATE {table_name} SET
                                player_name = ?, team_abbreviation = ?, team_name = ?, age = ?,
                                gp = ?, g = ?, fga_frequency = ?, fgm = ?, fga = ?, fg_pct = ?, efg_pct = ?,
                                fg2a_frequency = ?, fg2m = ?, fg2a = ?, fg2_pct = ?,
                                fg3a_frequency = ?, fg3m = ?, fg3a = ?, fg3_pct = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE player_id = ? AND season = ? AND team_id = ? AND close_def_dist_range = ? AND shot_clock_range = ? AND dribble_range = ? AND shot_dist_range = ?
                        """

                        update_data = record_data[7:] + record_data[:7]  # Move WHERE clause values to end
                        cursor.execute(update_sql, update_data)
                        updated += 1

                except Exception as e:
                    logger.error(f"Error processing record for player {record.get('player_id')}: {e}")
                    continue

            conn.commit()

        return inserted, updated

    def get_shot_dashboard_stats_summary(
        self,
        season_year: str = "2024-25",
        season_type: str = "Regular Season"
    ) -> Dict[str, Any]:
        """
        Get a summary of shot dashboard data in the database.

        Args:
            season_year: Season year
            season_type: Season type

        Returns:
            Dictionary with data summary
        """
        table_name = "player_shot_dashboard_stats" if season_type == "Regular Season" else "player_playoff_shot_dashboard_stats"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Count total records
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE season = ?", (season_year,))
            total_records = cursor.fetchone()[0]

            # Count unique players
            cursor.execute(f"SELECT COUNT(DISTINCT player_id) FROM {table_name} WHERE season = ?", (season_year,))
            unique_players = cursor.fetchone()[0]

            # Count by defender distance range
            cursor.execute(f"""
                SELECT close_def_dist_range, COUNT(*) as count
                FROM {table_name}
                WHERE season = ?
                GROUP BY close_def_dist_range
                ORDER BY count DESC
            """, (season_year,))
            defender_distance_breakdown = cursor.fetchall()

            # Count by shot clock range
            cursor.execute(f"""
                SELECT shot_clock_range, COUNT(*) as count
                FROM {table_name}
                WHERE season = ? AND shot_clock_range != ''
                GROUP BY shot_clock_range
                ORDER BY count DESC
            """, (season_year,))
            shot_clock_breakdown = cursor.fetchall()

            # Count by dribble range
            cursor.execute(f"""
                SELECT dribble_range, COUNT(*) as count
                FROM {table_name}
                WHERE season = ? AND dribble_range != ''
                GROUP BY dribble_range
                ORDER BY count DESC
            """, (season_year,))
            dribble_breakdown = cursor.fetchall()

            # Count by shot distance range
            cursor.execute(f"""
                SELECT shot_dist_range, COUNT(*) as count
                FROM {table_name}
                WHERE season = ?
                GROUP BY shot_dist_range
                ORDER BY count DESC
            """, (season_year,))
            shot_distance_breakdown = cursor.fetchall()

        return {
            "season_year": season_year,
            "season_type": season_type,
            "total_records": total_records,
            "unique_players": unique_players,
            "defender_distance_breakdown": defender_distance_breakdown,
            "shot_clock_breakdown": shot_clock_breakdown,
            "dribble_breakdown": dribble_breakdown,
            "shot_distance_breakdown": shot_distance_breakdown
        }


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description='Populate shot dashboard data from NBA Stats API')
    parser.add_argument('--season', default='2024-25', help='Season year (default: 2024-25)')
    parser.add_argument('--season-type', choices=['Regular Season', 'Playoffs'], default='Regular Season',
                        help='Season type (default: Regular Season)')
    parser.add_argument('--db-path', default='data/nba_stats.db', help='Database path (default: data/nba_stats.db)')
    parser.add_argument('--force-refresh', action='store_true', help='Force refresh cached API data')
    parser.add_argument('--summary-only', action='store_true', help='Only show summary, do not populate data')

    args = parser.parse_args()

    populator = ShotDashboardDataPopulator(db_path=args.db_path)

    if args.summary_only:
        # Show summary only
        summary = populator.get_shot_dashboard_stats_summary(
            season_year=args.season,
            season_type=args.season_type
        )

        print(f"\n=== Shot Dashboard Data Summary ===")
        print(f"Season: {summary['season_year']} {summary['season_type']}")
        print(f"Total Records: {summary['total_records']:,}")
        print(f"Unique Players: {summary['unique_players']:,}")

        print(f"\nBy Defender Distance:")
        for dist_range, count in summary['defender_distance_breakdown']:
            print(f"  {dist_range}: {count:,}")

        if summary['shot_clock_breakdown']:
            print(f"\nBy Shot Clock Range:")
            for clock_range, count in summary['shot_clock_breakdown']:
                print(f"  {clock_range}: {count:,}")

        if summary['dribble_breakdown']:
            print(f"\nBy Dribble Range:")
            for dribble_range, count in summary['dribble_breakdown']:
                print(f"  {dribble_range}: {count:,}")

        print(f"\nBy Shot Distance:")
        for shot_range, count in summary['shot_distance_breakdown']:
            print(f"  {shot_range}: {count:,}")

    else:
        # Populate data
        results = populator.populate_season_shot_dashboard_data(
            season_year=args.season,
            season_type=args.season_type,
            force_refresh=args.force_refresh
        )

        print("\n=== Population Results ===")
        print(f"Season: {results['season_year']} {results['season_type']}")
        print(f"Defender Distance Ranges Processed: {results['defender_distances_processed']}")
        print(f"Shot Clock Ranges Processed: {results['shot_clock_ranges_processed']}")
        print(f"Dribble Ranges Processed: {results['dribble_ranges_processed']}")
        print(f"Records Inserted: {results['records_inserted']:,}")
        print(f"Records Updated: {results['records_updated']:,}")

        if results['errors']:
            print(f"\nErrors ({len(results['errors'])}):")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(results['errors']) > 5:
                print(f"  ... and {len(results['errors']) - 5} more")


if __name__ == "__main__":
    main()
