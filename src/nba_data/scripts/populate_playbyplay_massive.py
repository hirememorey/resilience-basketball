"""
Massive-scale play-by-play data population for NBA resilience analysis.

Processes hundreds to thousands of games with parallel processing, robust error handling,
progress monitoring, and resumption capabilities.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import sqlite3
import time
import json
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from dataclasses import dataclass, field

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.api.possession_fetcher import create_possession_fetcher
from nba_data.api.game_discovery import discover_nba_games
from nba_data.db.schema import NBADatabaseSchema

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ProcessingStats:
    """Tracks processing statistics."""
    total_games: int = 0
    processed_games: int = 0
    successful_games: int = 0
    failed_games: int = 0
    skipped_games: int = 0
    total_possessions: int = 0
    total_events: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ProcessingConfig:
    """Configuration for massive data processing."""
    max_workers: int = 4  # Parallel threads
    batch_size: int = 25  # Games per batch
    retry_attempts: int = 3  # Retry failed games
    retry_delay: float = 5.0  # Delay between retries
    rate_limit_delay: float = 2.0  # Delay between API calls
    progress_save_interval: int = 10  # Save progress every N games
    checkpoint_file: str = "data/cache/processing_checkpoint.json"


class MassivePlayByPlayProcessor:
    """
    Processes massive amounts of play-by-play data with parallel processing
    and robust error handling.
    """

    def __init__(self, db_path: str = "data/nba_stats.db", config: Optional[ProcessingConfig] = None):
        """Initialize the massive processor."""
        self.db_path = Path(db_path)
        self.schema = NBADatabaseSchema(db_path)
        self.fetcher = create_possession_fetcher()
        self.config = config or ProcessingConfig()

        # Thread-safe statistics
        self.stats = ProcessingStats()
        self.stats_lock = threading.Lock()

        # Thread-safe database connections (one per thread)
        self.db_connections = {}

        # Load checkpoint if exists
        self.checkpoint_data = self._load_checkpoint()

    def process_season_games(self, season: str = "2023-24", season_type: str = "regular",
                           game_ids: Optional[List[str]] = None, max_games: Optional[int] = None) -> ProcessingStats:
        """
        Process play-by-play data for a season with massive scaling.

        Args:
            season: Season to process (e.g., '2023-24')
            season_type: 'regular' or 'playoffs'
            game_ids: Specific game IDs to process, or None to auto-discover
            max_games: Maximum games to process

        Returns:
            Processing statistics
        """
        self.stats.start_time = datetime.now()
        logger.info(f"🚀 Starting massive play-by-play processing for {season} {season_type}")

        try:
            # Get games to process
            if game_ids is None:
                game_ids = self._get_games_to_process(season, season_type, max_games)

            if not game_ids:
                logger.warning("No games to process")
                return self.stats

            # Filter out already processed games
            game_ids = self._filter_processed_games(game_ids)

            if not game_ids:
                logger.info("All games already processed")
                return self.stats

            self.stats.total_games = len(game_ids)
            logger.info(f"📋 Processing {len(game_ids)} games with {self.config.max_workers} workers")

            # Process games in parallel batches
            self._process_games_parallel(game_ids)

            # Final statistics
            self.stats.end_time = datetime.now()
            self._log_final_stats()

            # Save final checkpoint
            self._save_checkpoint()

            return self.stats

        except Exception as e:
            logger.error(f"Massive processing failed: {e}")
            raise

    def _get_games_to_process(self, season: str, season_type: str, max_games: int = None) -> List[str]:
        """Get list of games to process."""
        if self.checkpoint_data and 'game_ids' in self.checkpoint_data and self.checkpoint_data['game_ids']:
            # Resume from checkpoint
            game_ids = self.checkpoint_data['game_ids']
            logger.info(f"📚 Resumed from checkpoint: {len(game_ids)} games")
        else:
            # Discover new games
            logger.info(f"🔍 Discovering {season_type} games for {season}...")
            discovered = discover_nba_games([season], [season_type], max_games)

            key = f"{season}_{season_type}"
            game_ids = discovered.get(key, [])
            logger.info(f"🎯 Discovered {len(game_ids)} games")

        # Apply max_games limit
        if max_games and len(game_ids) > max_games:
            game_ids = game_ids[:max_games]

        return game_ids

    def _filter_processed_games(self, game_ids: List[str]) -> List[str]:
        """Filter out games that have already been processed."""
        unprocessed = []

        for game_id in game_ids:
            if not self._game_has_possession_data(game_id):
                unprocessed.append(game_id)

        skipped = len(game_ids) - len(unprocessed)
        if skipped > 0:
            logger.info(f"⏭️  Skipped {skipped} already processed games")

        return unprocessed

    def _process_games_parallel(self, game_ids: List[str]) -> None:
        """Process games using parallel workers."""
        # Process in batches to avoid overwhelming the system
        for i in range(0, len(game_ids), self.config.batch_size):
            batch = game_ids[i:i + self.config.batch_size]
            batch_num = i // self.config.batch_size + 1
            total_batches = (len(game_ids) + self.config.batch_size - 1) // self.config.batch_size

            logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} games)")

            # Process batch with parallel workers
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                # Submit all games in batch
                future_to_game = {
                    executor.submit(self._process_single_game_thread_safe, game_id): game_id
                    for game_id in batch
                }

                # Collect results as they complete
                for future in as_completed(future_to_game):
                    game_id = future_to_game[future]
                    try:
                        result = future.result()
                        self._update_stats_from_result(result)
                    except Exception as e:
                        self._record_error(game_id, str(e))

            # Periodic checkpoint save
            if batch_num % self.config.progress_save_interval == 0:
                self._save_checkpoint()

            # Brief pause between batches
            if batch_num < total_batches:
                time.sleep(1.0)

    def _process_single_game_thread_safe(self, game_id: str) -> Dict[str, Any]:
        """
        Process a single game in a thread-safe manner.
        Each thread gets its own database connection.
        """
        thread_id = threading.current_thread().ident

        # Get thread-specific database connection
        if thread_id not in self.db_connections:
            self.db_connections[thread_id] = sqlite3.connect(self.db_path)

        conn = self.db_connections[thread_id]

        try:
            # Rate limiting
            time.sleep(self.config.rate_limit_delay * random.uniform(0.8, 1.2))

            # Fetch possession data with retries
            possessions = self._fetch_with_retries(game_id)

            if not possessions:
                return {
                    'game_id': game_id,
                    'success': False,
                    'error': 'No possession data found'
                }

            # Store in database
            counts = self._store_possessions_thread_safe(conn, possessions)

            return {
                'game_id': game_id,
                'success': True,
                'possessions': counts['possessions'],
                'events': counts['events'],
                'lineups': counts['lineups'],
                'matchups': counts['matchups']
            }

        except Exception as e:
            return {
                'game_id': game_id,
                'success': False,
                'error': str(e)
            }

    def _fetch_with_retries(self, game_id: str) -> Optional[List[Any]]:
        """Fetch possession data with retry logic."""
        for attempt in range(self.config.retry_attempts):
            try:
                possessions = self.fetcher.fetch_game_possessions(game_id)
                return possessions
            except Exception as e:
                if attempt < self.config.retry_attempts - 1:
                    delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Attempt {attempt + 1} failed for {game_id}: {e}. Retrying in {delay:.1f}s")
                    time.sleep(delay)
                else:
                    logger.error(f"All attempts failed for {game_id}: {e}")
                    raise

        return None

    def _store_possessions_thread_safe(self, conn: sqlite3.Connection, possessions: List[Any]) -> Dict[str, int]:
        """Store possession data using thread-specific connection."""
        cursor = conn.cursor()

        try:
            possessions_count = 0
            events_count = 0
            lineups_count = 0
            matchups_count = 0

            for possession in possessions:
                # Insert possession
                possession_data = (
                    possession.possession_id,
                    possession.game_id,
                    possession.period,
                    possession.clock_time_start,
                    possession.clock_time_end,
                    possession.home_team_id,
                    possession.away_team_id,
                    possession.offensive_team_id,
                    possession.defensive_team_id,
                    possession.possession_start,
                    possession.possession_end,
                    possession.duration_seconds,
                    possession.points_scored,
                    possession.expected_points,
                    possession.possession_type,
                    possession.start_reason,
                    possession.end_reason
                )

                cursor.execute("""
                    INSERT OR REPLACE INTO possessions
                    (possession_id, game_id, period, clock_time_start, clock_time_end,
                     home_team_id, away_team_id, offensive_team_id, defensive_team_id,
                     possession_start, possession_end, duration_seconds, points_scored,
                     expected_points, possession_type, start_reason, end_reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, possession_data)

                possessions_count += 1

                # Insert possession events
                for event in possession.events:
                    event_data = (
                        event.event_id,
                        event.possession_id,
                        event.event_number,
                        event.clock_time,
                        event.elapsed_seconds,
                        event.player_id,
                        event.team_id,
                        event.opponent_team_id,
                        event.event_type,
                        event.event_subtype,
                        event.shot_type,
                        event.shot_distance,
                        event.shot_result,
                        event.points_scored,
                        event.assist_player_id,
                        event.block_player_id,
                        event.steal_player_id,
                        event.turnover_type,
                        event.foul_type,
                        event.rebound_type,
                        event.location_x,
                        event.location_y,
                        event.defender_player_id,
                        event.touches_before_action,
                        event.dribbles_before_action
                    )

                    cursor.execute("""
                        INSERT OR REPLACE INTO possession_events
                        (event_id, possession_id, event_number, clock_time, elapsed_seconds,
                         player_id, team_id, opponent_team_id, event_type, event_subtype,
                         shot_type, shot_distance, shot_result, points_scored, assist_player_id,
                         block_player_id, steal_player_id, turnover_type, foul_type, rebound_type,
                         location_x, location_y, defender_player_id, touches_before_action,
                         dribbles_before_action)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, event_data)

                    events_count += 1

                # Insert lineups (if available)
                for lineup in possession.lineups or []:
                    lineup_data = (
                        possession.possession_id,
                        lineup.get("player_id"),
                        lineup.get("team_id"),
                        lineup.get("position")
                    )

                    cursor.execute("""
                        INSERT OR REPLACE INTO possession_lineups
                        (possession_id, player_id, team_id, position)
                        VALUES (?, ?, ?, ?)
                    """, lineup_data)

                    lineups_count += 1

                # Insert matchups (if available)
                for matchup in possession.matchups or []:
                    matchup_data = (
                        possession.possession_id,
                        matchup.get("offensive_player_id"),
                        matchup.get("defensive_player_id"),
                        matchup.get("matchup_start_time"),
                        matchup.get("matchup_end_time"),
                        matchup.get("duration_seconds"),
                        matchup.get("switches_during_matchup")
                    )

                    cursor.execute("""
                        INSERT OR REPLACE INTO possession_matchups
                        (possession_id, offensive_player_id, defensive_player_id,
                         matchup_start_time, matchup_end_time, duration_seconds,
                         switches_during_matchup)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, matchup_data)

                    matchups_count += 1

            conn.commit()

            return {
                "possessions": possessions_count,
                "events": events_count,
                "lineups": lineups_count,
                "matchups": matchups_count
            }

        finally:
            cursor.close()

    def _update_stats_from_result(self, result: Dict[str, Any]) -> None:
        """Update statistics from a processing result."""
        with self.stats_lock:
            self.stats.processed_games += 1

            if result['success']:
                self.stats.successful_games += 1
                self.stats.total_possessions += result.get('possessions', 0)
                self.stats.total_events += result.get('events', 0)
            else:
                self.stats.failed_games += 1
                self._record_error(result['game_id'], result.get('error', 'Unknown error'))

    def _record_error(self, game_id: str, error: str) -> None:
        """Record an error in the statistics."""
        error_record = {
            'game_id': game_id,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }
        self.stats.errors.append(error_record)

    def _game_has_possession_data(self, game_id: str) -> bool:
        """Check if a game already has possession data."""
        cursor = self.schema.conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM possessions WHERE game_id = ?", (game_id,))
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            cursor.close()

    def _load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Load processing checkpoint if it exists."""
        checkpoint_file = Path(self.config.checkpoint_file)
        if checkpoint_file.exists():
            try:
                with open(checkpoint_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load checkpoint: {e}")
        return None

    def _save_checkpoint(self) -> None:
        """Save current processing state."""
        checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': {
                'total_games': self.stats.total_games,
                'processed_games': self.stats.processed_games,
                'successful_games': self.stats.successful_games,
                'failed_games': self.stats.failed_games,
                'total_possessions': self.stats.total_possessions,
                'total_events': self.stats.total_events,
            },
            'game_ids': getattr(self, '_current_game_ids', None)
        }

        with open(self.config.checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

    def _log_final_stats(self) -> None:
        """Log final processing statistics."""
        duration = self.stats.end_time - self.stats.start_time
        success_rate = (self.stats.successful_games / self.stats.processed_games * 100) if self.stats.processed_games > 0 else 0

        logger.info("🎉 Massive processing complete!")
        logger.info(f"⏱️  Duration: {duration}")
        logger.info(f"🎯 Success Rate: {success_rate:.1f}%")
        logger.info(f"🏀 Games: {self.stats.successful_games}/{self.stats.processed_games}")
        logger.info(f"🏈 Possessions: {self.stats.total_possessions:,}")
        logger.info(f"⚡ Events: {self.stats.total_events:,}")

        if self.stats.errors:
            logger.warning(f"❌ Errors: {len(self.stats.errors)}")
            # Log first few errors
            for error in self.stats.errors[:3]:
                logger.warning(f"   {error['game_id']}: {error['error']}")


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Massive-scale play-by-play data processing")
    parser.add_argument("--season", default="2023-24", help="Season to process")
    parser.add_argument("--season-type", default="regular", choices=["regular", "playoffs"], help="Season type")
    parser.add_argument("--max-games", type=int, help="Maximum games to process")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
    parser.add_argument("--batch-size", type=int, default=25, help="Games per batch")
    parser.add_argument("--db-path", default="data/nba_stats.db", help="Database path")

    args = parser.parse_args()

    # Configure processing
    config = ProcessingConfig(
        max_workers=args.workers,
        batch_size=args.batch_size
    )

    # Run massive processing
    processor = MassivePlayByPlayProcessor(args.db_path, config)
    stats = processor.process_season_games(args.season, args.season_type, max_games=args.max_games)

    # Print summary
    print("\n🎯 Massive Play-by-Play Processing Complete")
    print("=" * 50)
    print(f"Season: {args.season} {args.season_type}")
    print(f"Games Processed: {stats.processed_games}")
    print(f"Games Successful: {stats.successful_games}")
    print(f"Total Possessions: {stats.total_possessions:,}")
    print(f"Total Events: {stats.total_events:,}")

    if stats.errors:
        print(f"\n❌ Errors ({len(stats.errors)}):")
        for error in stats.errors[:5]:
            print(f"  - {error['game_id']}: {error['error']}")
        if len(stats.errors) > 5:
            print(f"  ... and {len(stats.errors) - 5} more errors")


if __name__ == "__main__":
    main()
