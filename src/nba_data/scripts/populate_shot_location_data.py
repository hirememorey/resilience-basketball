"""
Script to populate player shot location data from the NBA API with parallel processing.

This script fetches detailed shot chart data for each player for every season
and stores it in the player_shot_locations table in the database.

Features:
- Parallel processing with configurable workers
- Thread-safe database connections
- Checkpoint/resume functionality
- Retry logic with exponential backoff
- Progress monitoring
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import sqlite3
import pandas as pd
from tqdm import tqdm
import time
import json
import random
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.api.nba_stats_client import NBAStatsClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ProcessingStats:
    """Tracks processing statistics."""
    total_combinations: int = 0
    processed_combinations: int = 0
    successful_combinations: int = 0
    failed_combinations: int = 0
    total_shots: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ProcessingConfig:
    """Configuration for shot location processing."""
    max_workers: int = 4  # Parallel threads
    batch_size: int = 50  # Player-season combinations per batch
    retry_attempts: int = 3  # Retry failed requests
    retry_delay: float = 3.0  # Base delay between retries
    rate_limit_delay: float = 1.5  # Delay between API calls
    progress_save_interval: int = 5  # Save progress every N batches
    checkpoint_file: str = "data/cache/shot_location_checkpoint.json"
    target_seasons: Optional[List[str]] = None  # Process only specific seasons if provided

class ShotLocationPopulator:
    """Populates player shot location data with parallel processing."""

    def __init__(self, db_path: str = "data/nba_stats.db", config: Optional[ProcessingConfig] = None):
        """Initialize with database path and configuration."""
        self.db_path = Path(db_path)
        self.schema = None  # Will be initialized when needed
        self.config = config or ProcessingConfig()

        # Thread-safe statistics
        self.stats = ProcessingStats()
        self.stats_lock = threading.Lock()

        # Thread-safe database connections (one per thread)
        self.db_connections = {}

        # Load checkpoint if exists
        self.checkpoint_data = self._load_checkpoint()

    def populate_shot_locations_parallel(self, max_combinations: Optional[int] = None) -> ProcessingStats:
        """
        Fetch and store shot location data for all players and seasons using parallel processing.

        Args:
            max_combinations: Maximum player-season combinations to process

        Returns:
            Processing statistics
        """
        self.stats.start_time = datetime.now()
        logger.info(f"🚀 Starting parallel shot location data population with {self.config.max_workers} workers")
        if self.config.target_seasons:
            logger.info(f"🎯 Targeting specific seasons: {', '.join(self.config.target_seasons)}")

        try:
            # Get combinations to process
            combinations = self._get_combinations_to_process(max_combinations)

            if not combinations:
                logger.info("No combinations to process")
                return self.stats

            self.stats.total_combinations = len(combinations)
            logger.info(f"📋 Processing {len(combinations)} player-season combinations")

            # Process combinations in parallel batches
            self._process_combinations_parallel(combinations)

            # Final statistics
            self.stats.end_time = datetime.now()
            self._log_final_stats()

            # Save final checkpoint
            self._save_checkpoint()

            return self.stats

        except Exception as e:
            logger.error(f"Parallel processing failed: {e}")
            raise

    def _get_combinations_to_process(self, max_combinations: Optional[int] = None) -> List[Tuple[int, str]]:
        """Get list of (player_id, season) combinations to process."""
        if self.checkpoint_data and 'combinations' in self.checkpoint_data and self.checkpoint_data['combinations']:
            # Resume from checkpoint
            combinations = self.checkpoint_data['combinations']
            logger.info(f"📚 Resumed from checkpoint: {len(combinations)} combinations")
        else:
            # Discover new combinations
            logger.info("🔍 Discovering player-season combinations...")

            conn = sqlite3.connect(self.db_path)
            query = "SELECT DISTINCT player_id, season FROM player_season_stats"
            
            # Add season filter if target_seasons is set
            if self.config.target_seasons:
                placeholders = ','.join(['?'] * len(self.config.target_seasons))
                query += f" WHERE season IN ({placeholders})"
                params = tuple(self.config.target_seasons)
            else:
                params = ()
            
            query += " ORDER BY player_id, season"
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()

            combinations = list(zip(df['player_id'], df['season']))
            logger.info(f"🎯 Discovered {len(combinations)} player-season combinations")

        # First filter out processed combinations, then apply max_combinations limit
        combinations = self._filter_processed_combinations(combinations)

        if max_combinations and len(combinations) > max_combinations:
            combinations = combinations[:max_combinations]

        return combinations

    def _filter_processed_combinations(self, combinations: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
        """Filter out combinations that have already been processed."""
        unprocessed = []
        
        conn = sqlite3.connect(self.db_path)
        # Using a set for faster lookups of processed combinations
        processed_query = """
            SELECT DISTINCT player_id, season 
            FROM player_shot_locations 
            WHERE season_type IN ('Regular Season', 'Playoffs')
            GROUP BY player_id, season
            HAVING COUNT(DISTINCT season_type) >= 1
        """
        processed_df = pd.read_sql_query(processed_query, conn)
        processed_set = set(zip(processed_df['player_id'], processed_df['season']))
        conn.close()

        for combo in combinations:
            if combo not in processed_set:
                unprocessed.append(combo)

        skipped = len(combinations) - len(unprocessed)
        if skipped > 0:
            logger.info(f"⏭️  Skipped {skipped} already processed combinations")

        return unprocessed

    def _process_combinations_parallel(self, combinations: List[Tuple[int, str]]) -> None:
        """Process combinations using parallel workers."""
        # Process in batches to avoid overwhelming the system
        for i in range(0, len(combinations), self.config.batch_size):
            batch = combinations[i:i + self.config.batch_size]
            batch_num = i // self.config.batch_size + 1
            total_batches = (len(combinations) + self.config.batch_size - 1) // self.config.batch_size

            logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} combinations)")

            # Process batch with parallel workers
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                # Submit all combinations in batch
                future_to_combo = {
                    executor.submit(self._process_single_combination_thread_safe, player_id, season): (player_id, season)
                    for player_id, season in batch
                }

                # Collect results as they complete
                for future in as_completed(future_to_combo):
                    combo = future_to_combo[future]
                    try:
                        result = future.result()
                        self._update_stats_from_result(result)
                    except Exception as e:
                        self._record_error(combo, str(e))

            # Periodic checkpoint save
            if batch_num % self.config.progress_save_interval == 0:
                self._save_checkpoint()

            # Brief pause between batches
            if batch_num < total_batches:
                time.sleep(0.5)

    def _process_single_combination_thread_safe(self, player_id: int, season: str) -> Dict[str, Any]:
        """
        Process a single player-season combination in a thread-safe manner.
        Each thread gets its own database connection and API client.
        """
        thread_id = threading.current_thread().ident

        # Get thread-specific database connection
        if thread_id not in self.db_connections:
            self.db_connections[thread_id] = sqlite3.connect(self.db_path)

        conn = self.db_connections[thread_id]

        # Get thread-specific API client
        client = NBAStatsClient()

        total_shots = 0
        success_count = 0

        try:
            for season_type in ["Regular Season", "Playoffs"]:
                # Rate limiting
                time.sleep(self.config.rate_limit_delay * random.uniform(0.8, 1.2))

                # Fetch shot data with retries
                shot_data = self._fetch_shot_data_with_retries(client, player_id, season, season_type)

                if not shot_data:
                    continue

                # Process and store the data
                shots_processed = self._store_shot_data_thread_safe(conn, shot_data, season, season_type)
                total_shots += shots_processed
                success_count += 1

            return {
                'player_id': player_id,
                'season': season,
                'success': success_count > 0,
                'shots_processed': total_shots,
                'season_types_processed': success_count
            }

        except Exception as e:
            return {
                'player_id': player_id,
                'season': season,
                'success': False,
                'error': str(e),
                'shots_processed': total_shots
            }

    def _fetch_shot_data_with_retries(self, client: NBAStatsClient, player_id: int, season: str, season_type: str) -> Optional[Dict[str, Any]]:
        """Fetch shot data with retry logic."""
        for attempt in range(self.config.retry_attempts):
            try:
                shot_data = client.get_player_shot_chart(player_id=player_id, season=season, season_type=season_type)

                if shot_data and shot_data.get('resultSets') and shot_data['resultSets'][0].get('rowSet'):
                    return shot_data
                else:
                    return None  # No data available

            except Exception as e:
                if attempt < self.config.retry_attempts - 1:
                    delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Attempt {attempt + 1} failed for player {player_id}, {season} {season_type}: {e}. Retrying in {delay:.1f}s")
                    time.sleep(delay)
                else:
                    logger.error(f"All attempts failed for player {player_id}, {season} {season_type}: {e}")
                    raise

        return None

    def _store_shot_data_thread_safe(self, conn: sqlite3.Connection, shot_data: Dict[str, Any], season: str, season_type: str) -> int:
        """Store shot data using thread-specific connection."""
        headers = shot_data['resultSets'][0]['headers']
        rows = shot_data['resultSets'][0]['rowSet']

        if not rows:
            return 0

        df = pd.DataFrame(rows, columns=headers)

        # Prepare data for insertion
        df['season'] = season
        df['season_type'] = season_type

        # Ensure column names match the database schema
        column_mapping = {
            'GAME_ID': 'game_id',
            'PLAYER_ID': 'player_id',
            'TEAM_ID': 'team_id',
            'PERIOD': 'period',
            'MINUTES_REMAINING': 'minutes_remaining',
            'SECONDS_REMAINING': 'seconds_remaining',
            'EVENT_TYPE': 'event_type',
            'ACTION_TYPE': 'action_type',
            'SHOT_TYPE': 'shot_type',
            'SHOT_ZONE_BASIC': 'shot_zone_basic',
            'SHOT_ZONE_AREA': 'shot_zone_area',
            'SHOT_ZONE_RANGE': 'shot_zone_range',
            'SHOT_DISTANCE': 'shot_distance',
            'LOC_X': 'loc_x',
            'LOC_Y': 'loc_y',
            'SHOT_ATTEMPTED_FLAG': 'shot_attempted_flag',
            'SHOT_MADE_FLAG': 'shot_made_flag',
        }
        df = df.rename(columns=column_mapping)

        # Select only the columns that exist in our table
        db_columns = [
            'game_id', 'player_id', 'team_id', 'season', 'season_type', 'period',
            'minutes_remaining', 'seconds_remaining', 'event_type', 'action_type',
            'shot_type', 'shot_zone_basic', 'shot_zone_area', 'shot_zone_range',
            'shot_distance', 'loc_x', 'loc_y', 'shot_attempted_flag', 'shot_made_flag'
        ]

        df_to_insert = df[db_columns]

        # Insert data into the database
        df_to_insert.to_sql('player_shot_locations', conn, if_exists='append', index=False)

        return len(df_to_insert)

    def _update_stats_from_result(self, result: Dict[str, Any]) -> None:
        """Update statistics from processing result."""
        with self.stats_lock:
            self.stats.processed_combinations += 1

            if result.get('success', False):
                self.stats.successful_combinations += 1
                self.stats.total_shots += result.get('shots_processed', 0)
            else:
                self.stats.failed_combinations += 1

    def _record_error(self, combo: Tuple[int, str], error: str) -> None:
        """Record processing error."""
        with self.stats_lock:
            self.stats.errors.append({
                'player_id': combo[0],
                'season': combo[1],
                'error': error,
                'timestamp': datetime.now().isoformat()
            })
            self.stats.failed_combinations += 1

    def _log_final_stats(self) -> None:
        """Log final processing statistics."""
        duration = self.stats.end_time - self.stats.start_time
        success_rate = (self.stats.successful_combinations / self.stats.total_combinations * 100) if self.stats.total_combinations > 0 else 0

        logger.info("=" * 60)
        logger.info("🎯 SHOT LOCATION PROCESSING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"📊 Total combinations: {self.stats.total_combinations}")
        logger.info(f"✅ Successful: {self.stats.successful_combinations}")
        logger.info(f"❌ Failed: {self.stats.failed_combinations}")
        logger.info(f"🎯 Success rate: {success_rate:.1f}%")
        logger.info(f"🏀 Total shots processed: {self.stats.total_shots:,}")
        logger.info(f"⏱️  Total time: {duration}")
        logger.info(f"⚡ Average time per combination: {duration / self.stats.total_combinations if self.stats.total_combinations > 0 else 0}")

        if self.stats.errors:
            logger.warning(f"⚠️  {len(self.stats.errors)} errors occurred. Check logs for details.")

    def _load_checkpoint(self) -> Dict[str, Any]:
        """Load processing checkpoint if it exists."""
        checkpoint_path = Path(self.config.checkpoint_file)
        if checkpoint_path.exists():
            try:
                with open(checkpoint_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
        return {}

    def _save_checkpoint(self) -> None:
        """Save current processing state for resume capability."""
        checkpoint_path = Path(self.config.checkpoint_file)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'processed_combinations': self.stats.processed_combinations,
            'successful_combinations': self.stats.successful_combinations,
            'total_shots': self.stats.total_shots,
            'errors': self.stats.errors[-10:] if len(self.stats.errors) > 10 else self.stats.errors,  # Keep last 10 errors
        }

        try:
            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    # Legacy method for backward compatibility
    def populate_shot_locations(self):
        """Legacy sequential processing method."""
        logger.warning("⚠️  Using legacy sequential processing. Consider using populate_shot_locations_parallel() for better performance.")
        return self.populate_shot_locations_parallel()

def main():
    """Main execution function with command-line arguments."""
    import argparse

    parser = argparse.ArgumentParser(description="Populate NBA player shot location data")
    parser.add_argument("--sequential", action="store_true",
                       help="Use sequential processing instead of parallel (default: False)")
    parser.add_argument("--workers", type=int, default=4,
                       help="Number of parallel workers (default: 4)")
    parser.add_argument("--batch-size", type=int, default=50,
                       help="Batch size for processing (default: 50)")
    parser.add_argument("--max-combinations", type=int,
                       help="Maximum number of player-season combinations to process")
    parser.add_argument("--rate-limit", type=float, default=1.5,
                       help="Rate limit delay between API calls in seconds (default: 1.5)")
    parser.add_argument("--seasons", type=str, nargs="+",
                       help="Specific seasons to process (e.g., '2015-16' '2016-17')")

    args = parser.parse_args()

    # Create configuration
    config = ProcessingConfig(
        max_workers=args.workers,
        batch_size=args.batch_size,
        rate_limit_delay=args.rate_limit,
        target_seasons=args.seasons
    )

    # Create populator
    populator = ShotLocationPopulator(config=config)

    # Choose processing method
    if args.sequential:
        logger.info("🐌 Using sequential processing")
        stats = populator.populate_shot_locations()
    else:
        logger.info(f"🚀 Using parallel processing with {args.workers} workers")
        stats = populator.populate_shot_locations_parallel(max_combinations=args.max_combinations)

    # Log results
    logger.info("✅ Processing complete!")
    return stats

if __name__ == "__main__":
    main()
