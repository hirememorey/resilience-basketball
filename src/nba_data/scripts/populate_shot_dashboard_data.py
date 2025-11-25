
#!/usr/bin/env python3
"""
Script to populate player shot dashboard statistics from NBA Stats API.

This script fetches shot statistics using INTERSECTIONAL filters to capture true shot quality context.
It fetches:
1. Defender Distance x Shot Clock Range (For Shot Quality/Dominance)
2. Defender Distance x Dribble Range (For Self-Creation/Isolation)
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.api.shot_dashboard_client import ShotDashboardClient

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/populate_shot_dashboard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SEASONS = [
    "2015-16", "2016-17", "2017-18", "2018-19", "2019-20",
    "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"
]

class ShotDashboardDataPopulator:
    """Populates player shot dashboard statistics into the database."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = ShotDashboardClient()
        return self._client

    def populate_season_shot_dashboard_data(
        self,
        season_year: str = "2024-25",
        season_type: str = "Regular Season",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Populate shot dashboard data for an entire season using combinatorial fetching.
        """
        results = {
            "combinations_processed": 0,
            "records_inserted": 0,
            "records_updated": 0,
            "errors": [],
            "season_year": season_year,
            "season_type": season_type
        }

        logger.info(f"Starting COMBINATORIAL shot dashboard population for {season_year} {season_type}")

        # Determine table name based on season type
        table_name = "player_shot_dashboard_stats" if season_type == "Regular Season" else "player_playoff_shot_dashboard_stats"
        
        # Check if season_type column exists in schema for the target table
        has_season_type = True
        if table_name == "player_playoff_shot_dashboard_stats":
            # Verify schema based on the actual database state
            has_season_type = False
            
        # --- BATCH 1: Defender Distance x Shot Clock (Shot Quality Context) ---
        # This matrix tells us how players perform against tight defense at different clock times.
        logger.info("--- Processing Batch 1: Defender Distance x Shot Clock ---")
        
        for def_dist in self.client.DEFENDER_DISTANCE_RANGES:
            for shot_clock in self.client.SHOT_CLOCK_RANGES:
                try:
                    logger.info(f"Fetching: {def_dist} | {shot_clock}")
                    
                    # Fetch Data
                    response_data = self.client.get_player_shot_dashboard_stats(
                        season_year=season_year,
                        season_type=season_type,
                        close_def_dist_range=def_dist,
                        shot_clock_range=shot_clock,
                        dribble_range="", # Explicitly empty
                        shot_dist_range=">=10.0" # Standardize to shots outside 10ft (Jump Shots mostly) or keep default
                        # Note: Keeping >=10.0 from original script logic, but maybe we want all shots?
                        # The original script hardcoded >=10.0 in the parser. Let's stick to that for consistency with "Shot Quality"
                        # unless we want rim finishes.
                        # Decision: Pass >=10.0 to match the parser's hardcoded value.
                    )

                    # Parse Data
                    records = self.client.parse_shot_dashboard_response(
                        response_data, 
                        close_def_dist_range=def_dist,
                        shot_clock_range=shot_clock,
                        dribble_range="", # IMPORTANT: Must pass empty string to match DB schema expectation
                        season=season_year
                    )

                    if not records:
                        logger.warning(f"No records for {def_dist} | {shot_clock}")
                        continue

                    # Insert Data
                    inserted, updated = self._insert_shot_dashboard_records(
                        records, table_name, season_year, season_type
                    )

                    results["records_inserted"] += inserted
                    results["records_updated"] += updated
                    results["combinations_processed"] += 1

                except Exception as e:
                    error_msg = f"Failed Batch 1 ({def_dist}|{shot_clock}): {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)


        # --- BATCH 2: Defender Distance x Dribbles (Self-Creation Context) ---
        # This matrix tells us how players perform against tight defense when self-creating vs spot-up.
        logger.info("--- Processing Batch 2: Defender Distance x Dribbles ---")

        for def_dist in self.client.DEFENDER_DISTANCE_RANGES:
            for dribble in self.client.DRIBBLE_RANGES:
                try:
                    logger.info(f"Fetching: {def_dist} | {dribble}")
                    
                    # Fetch Data
                    response_data = self.client.get_player_shot_dashboard_stats(
                        season_year=season_year,
                        season_type=season_type,
                        close_def_dist_range=def_dist,
                        shot_clock_range="", # Explicitly empty
                        dribble_range=dribble,
                        shot_dist_range=">=10.0"
                    )

                    # Parse Data
                    records = self.client.parse_shot_dashboard_response(
                        response_data, 
                        close_def_dist_range=def_dist,
                        shot_clock_range="", # Empty
                        dribble_range=dribble,
                        season=season_year
                    )

                    if not records:
                        logger.warning(f"No records for {def_dist} | {dribble}")
                        continue

                    # Insert Data
                    inserted, updated = self._insert_shot_dashboard_records(
                        records, table_name, season_year, season_type
                    )

                    results["records_inserted"] += inserted
                    results["records_updated"] += updated
                    results["combinations_processed"] += 1

                except Exception as e:
                    error_msg = f"Failed Batch 2 ({def_dist}|{dribble}): {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

        logger.info(f"Completed {season_year} {season_type}. Processed {results['combinations_processed']} combinations.")
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
        """
        inserted = 0
        updated = 0

        logger.info(f"Inserting into table: {table_name}")
        
        # Determine if we should include season_type in the query
        # Based on schema verification, player_playoff_shot_dashboard_stats DOES NOT have season_type
        include_season_type = True
        if table_name == "player_playoff_shot_dashboard_stats":
            include_season_type = False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for record in records:
                try:
                    # Ensure we handle None values for keys that might be missing
                    # The schema expects TEXT NOT NULL, so we must use empty strings for missing ranges
                    
                    if include_season_type:
                        # Prepare the record data WITH season_type
                        record_data = (
                            record.get('player_id'),
                            record.get('season'),
                            season_type, # Explicitly pass season_type
                            record.get('team_id'),
                            record.get('close_def_dist_range', ''),
                            record.get('shot_clock_range', ''),
                            record.get('dribble_range', ''),
                            record.get('shot_dist_range', ''),
                            
                            # Metadata
                            record.get('player_name'),
                            record.get('team_abbreviation'),
                            record.get('team_name'),
                            record.get('age'),
                            
                            # Stats
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

                        # Insert SQL (Matches schema column order)
                        insert_sql = f"""
                            INSERT INTO {table_name} (
                                player_id, season, season_type, team_id, 
                                close_def_dist_range, shot_clock_range, dribble_range, shot_dist_range,
                                player_name, team_abbreviation, team_name, age, 
                                gp, g,
                                fga_frequency, fgm, fga, fg_pct, efg_pct,
                                fg2a_frequency, fg2m, fg2a, fg2_pct,
                                fg3a_frequency, fg3m, fg3a, fg3_pct
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """

                        try:
                            cursor.execute(insert_sql, record_data)
                            inserted += 1
                        except sqlite3.IntegrityError:
                            # Update logic (if record exists)
                            update_sql = f"""
                                UPDATE {table_name} SET
                                    player_name = ?, team_abbreviation = ?, team_name = ?, age = ?,
                                    gp = ?, g = ?, fga_frequency = ?, fgm = ?, fga = ?, fg_pct = ?, efg_pct = ?,
                                    fg2a_frequency = ?, fg2m = ?, fg2a = ?, fg2_pct = ?,
                                    fg3a_frequency = ?, fg3m = ?, fg3a = ?, fg3_pct = ?,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE player_id = ? AND season = ? AND season_type = ? AND team_id = ? 
                                AND close_def_dist_range = ? AND shot_clock_range = ? AND dribble_range = ? AND shot_dist_range = ?
                            """
                            
                            # Data for update: Stats first, then WHERE clause params
                            stats_data = record_data[8:]
                            pk_data = record_data[0:8]
                            
                            cursor.execute(update_sql, stats_data + pk_data)
                            updated += 1
                    else:
                        # Prepare the record data WITHOUT season_type
                        record_data = (
                            record.get('player_id'),
                            record.get('season'),
                            # NO SEASON_TYPE HERE
                            record.get('team_id'),
                            record.get('close_def_dist_range', ''),
                            record.get('shot_clock_range', ''),
                            record.get('dribble_range', ''),
                            record.get('shot_dist_range', ''),
                            
                            # Metadata
                            record.get('player_name'),
                            record.get('team_abbreviation'),
                            record.get('team_name'),
                            record.get('age'),
                            
                            # Stats
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

                        # Insert SQL (Matches schema column order - no season_type)
                        insert_sql = f"""
                            INSERT INTO {table_name} (
                                player_id, season, team_id, 
                                close_def_dist_range, shot_clock_range, dribble_range, shot_dist_range,
                                player_name, team_abbreviation, team_name, age, 
                                gp, g,
                                fga_frequency, fgm, fga, fg_pct, efg_pct,
                                fg2a_frequency, fg2m, fg2a, fg2_pct,
                                fg3a_frequency, fg3m, fg3a, fg3_pct
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """

                        try:
                            cursor.execute(insert_sql, record_data)
                            inserted += 1
                        except sqlite3.IntegrityError:
                            # Update logic (if record exists)
                            update_sql = f"""
                                UPDATE {table_name} SET
                                    player_name = ?, team_abbreviation = ?, team_name = ?, age = ?,
                                    gp = ?, g = ?, fga_frequency = ?, fgm = ?, fga = ?, fg_pct = ?, efg_pct = ?,
                                    fg2a_frequency = ?, fg2m = ?, fg2a = ?, fg2_pct = ?,
                                    fg3a_frequency = ?, fg3m = ?, fg3a = ?, fg3_pct = ?,
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE player_id = ? AND season = ? AND team_id = ? 
                                AND close_def_dist_range = ? AND shot_clock_range = ? AND dribble_range = ? AND shot_dist_range = ?
                            """
                            
                            # Data for update: Stats first, then WHERE clause params
                            # Slice indices adjusted for missing season_type
                            # record_data indices:
                            # 0: player_id
                            # 1: season
                            # 2: team_id
                            # 3-6: ranges
                            # 7-25: stats
                            
                            stats_data = record_data[7:]
                            pk_data = record_data[0:7]
                            
                            cursor.execute(update_sql, stats_data + pk_data)
                            updated += 1

                except Exception as e:
                    logger.error(f"Error processing record for player {record.get('player_id')}: {e}")
                    continue

            conn.commit()

        return inserted, updated

def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description='Populate shot dashboard data from NBA Stats API')
    parser.add_argument('--season', default='2024-25', help='Season year (default: 2024-25)')
    parser.add_argument('--season-type', choices=['Regular Season', 'Playoffs'], default='Regular Season',
                        help='Season type (default: Regular Season)')
    parser.add_argument('--db-path', default='data/nba_stats.db', help='Database path (default: data/nba_stats.db)')
    parser.add_argument('--historical', action='store_true', help='Populate all historical seasons')
    parser.add_argument('--workers', type=int, default=1, help='Number of parallel workers for historical processing')

    args = parser.parse_args()

    if args.historical:
        print(f"=== Starting Historical Population ({len(SEASONS)} seasons) ===")
        print(f"Workers: {args.workers}")
        
        def process_season(season):
            # New instance per thread
            populator = ShotDashboardDataPopulator(db_path=args.db_path)
            logger.info(f"Processing season {season}...")
            try:
                # Regular Season
                populator.populate_season_shot_dashboard_data(
                    season_year=season,
                    season_type="Regular Season"
                )
                # Playoffs
                populator.populate_season_shot_dashboard_data(
                    season_year=season,
                    season_type="Playoffs"
                )
                return season, True
            except Exception as e:
                logger.error(f"Error processing season {season}: {e}")
                return season, False

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(process_season, season): season for season in SEASONS}
            for future in as_completed(futures):
                season, success = future.result()
                status = "✅" if success else "❌"
                print(f"{status} Processed {season}")
                
    else:
        # Single Season
        populator = ShotDashboardDataPopulator(db_path=args.db_path)
        populator.populate_season_shot_dashboard_data(
            season_year=args.season,
            season_type=args.season_type
        )

if __name__ == "__main__":
    main()
