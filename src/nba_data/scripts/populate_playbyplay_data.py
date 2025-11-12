"""
Script to populate play-by-play data from NBA API for multiple games.

This script fetches play-by-play data and parses it into possession-level
analytics for playoff resilience analysis. Scales beyond single game processing.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
import sqlite3
from datetime import datetime, timedelta
import random
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.api.possession_fetcher import create_possession_fetcher
from nba_data.db.schema import NBADatabaseSchema

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PlayByPlayDataPopulator:
    """Populates play-by-play data from NBA API for multiple games."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.schema = NBADatabaseSchema(db_path)
        self.fetcher = create_possession_fetcher()

    def populate_season_playbyplay(self, season: str = "2023-24", season_type: str = "Regular Season",
                                  max_games: int = None, batch_size: int = 10) -> Dict[str, Any]:
        """
        Populate play-by-play data for an entire season.

        Args:
            season: Season to process (format: "2023-24")
            season_type: "Regular Season" or "Playoffs"
            max_games: Maximum number of games to process (None for all)
            batch_size: Number of games to process in each batch

        Returns:
            Summary of population results
        """
        logger.info(f"Starting play-by-play data population for {season} {season_type}")

        results = {
            "season": season,
            "season_type": season_type,
            "games_processed": 0,
            "games_successful": 0,
            "total_possessions": 0,
            "total_events": 0,
            "total_lineups": 0,
            "total_matchups": 0,
            "errors": [],
            "skipped_games": []
        }

        # Get list of games to process
        game_ids = self._get_game_ids_for_season(season, season_type, max_games)

        if not game_ids:
            logger.warning(f"No games found for {season} {season_type}")
            return results

        logger.info(f"Found {len(game_ids)} games to process")

        # Process games in batches
        for i in range(0, len(game_ids), batch_size):
            batch = game_ids[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(game_ids) + batch_size - 1)//batch_size} ({len(batch)} games)")

            batch_results = self._process_batch(batch)

            results["games_processed"] += batch_results["games_processed"]
            results["games_successful"] += batch_results["games_successful"]
            results["total_possessions"] += batch_results["total_possessions"]
            results["total_events"] += batch_results["total_events"]
            results["total_lineups"] += batch_results["total_lineups"]
            results["total_matchups"] += batch_results["total_matchups"]
            results["errors"].extend(batch_results["errors"])
            results["skipped_games"].extend(batch_results["skipped_games"])

            # Add delay between batches to be respectful to the API
            if i + batch_size < len(game_ids):
                delay = random.uniform(5, 15)
                logger.info(f"Waiting {delay:.1f}s before next batch...")
                time.sleep(delay)

        logger.info(f"Play-by-play data population complete for {season} {season_type}")
        logger.info(f"Results: {results['games_successful']}/{results['games_processed']} games successful")
        logger.info(f"Total: {results['total_possessions']} possessions, {results['total_events']} events")

        return results

    def _get_game_ids_for_season(self, season: str, season_type: str, max_games: int = None) -> List[str]:
        """
        Get list of game IDs for a season.

        For now, we'll use a curated list of games that we know have play-by-play data.
        In the future, this could query the NBA API for game schedules.
        """
        # Known games with available play-by-play data
        # Using 2023 season games as examples
        known_games = [
            # 2023-24 Regular Season sample
            "0022300001", "0022300002", "0022300003", "0022300004", "0022300005",
            "0022300010", "0022300015", "0022300020", "0022300025", "0022300030",
            "0022300035", "0022300040", "0022300045", "0022300050",
            # Add more as discovered
        ]

        # For playoffs, use different game IDs
        if season_type == "Playoffs":
            # 2023 Playoffs (example - would need to be updated for current playoffs)
            playoff_games = [
                "0042300101", "0042300102", "0042300103", "0042300104", "0042300105",
                "0042300201", "0042300202", "0042300203", "0042300204",
                "0042300301", "0042300302", "0042300303", "0042300304",
                "0042300401", "0042300402", "0042300403", "0042300404",
                # Add more playoff games as they become available
            ]
            known_games = playoff_games

        # Filter by max_games if specified
        if max_games:
            known_games = known_games[:max_games]

        return known_games

    def _process_batch(self, game_ids: List[str]) -> Dict[str, Any]:
        """
        Process a batch of games.

        Args:
            game_ids: List of game IDs to process

        Returns:
            Batch processing results
        """
        batch_results = {
            "games_processed": 0,
            "games_successful": 0,
            "total_possessions": 0,
            "total_events": 0,
            "total_lineups": 0,
            "total_matchups": 0,
            "errors": [],
            "skipped_games": []
        }

        for game_id in game_ids:
            batch_results["games_processed"] += 1

            try:
                # Check if game already has possession data
                if self._game_has_possession_data(game_id):
                    logger.info(f"⏭️  Game {game_id}: Already has possession data, skipping")
                    batch_results["skipped_games"].append(game_id)
                    continue

                # Process the game
                game_results = self._populate_single_game(game_id)

                batch_results["games_successful"] += 1
                batch_results["total_possessions"] += game_results["possessions"]
                batch_results["total_events"] += game_results["events"]
                batch_results["total_lineups"] += game_results["lineups"]
                batch_results["total_matchups"] += game_results["matchups"]

                logger.info(f"✅ Game {game_id}: {game_results['possessions']} possessions, {game_results['events']} events")

            except Exception as e:
                error_msg = f"Failed to process game {game_id}: {str(e)}"
                logger.error(error_msg)
                batch_results["errors"].append(error_msg)

        return batch_results

    def _game_has_possession_data(self, game_id: str) -> bool:
        """
        Check if a game already has possession data.

        Args:
            game_id: Game ID to check

        Returns:
            True if game has possession data
        """
        try:
            cursor = self.schema.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM possessions WHERE game_id = ?", (game_id,))
            count = cursor.fetchone()[0]
            cursor.close()
            return count > 0
        except Exception:
            return False

    def _populate_single_game(self, game_id: str) -> Dict[str, int]:
        """
        Populate possession data for a single game.

        Args:
            game_id: NBA game ID

        Returns:
            Counts of inserted records
        """
        try:
            # Fetch possession data
            possessions = self.fetcher.fetch_game_possessions(game_id)

            if not possessions:
                logger.warning(f"No possession data found for game {game_id}")
                return {"possessions": 0, "events": 0, "lineups": 0, "matchups": 0}

            # Store in database
            return self._store_possessions(possessions)

        except Exception as e:
            logger.error(f"Error processing game {game_id}: {str(e)}")
            raise

    def _store_possessions(self, possessions: List[Any]) -> Dict[str, int]:
        """
        Store possession data in the database.

        Args:
            possessions: List of possession objects

        Returns:
            Counts of stored records
        """
        cursor = self.schema.conn.cursor()

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

            self.schema.conn.commit()

            return {
                "possessions": possessions_count,
                "events": events_count,
                "lineups": lineups_count,
                "matchups": matchups_count
            }

        finally:
            cursor.close()


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Populate play-by-play data from NBA API")
    parser.add_argument("--season", default="2023-24", help="Season to process")
    parser.add_argument("--season-type", default="Regular Season", choices=["Regular Season", "Playoffs"],
                       help="Season type to process")
    parser.add_argument("--max-games", type=int, default=None, help="Maximum number of games to process")
    parser.add_argument("--batch-size", type=int, default=5, help="Games to process per batch")
    parser.add_argument("--db-path", default="data/nba_stats.db", help="Database path")

    args = parser.parse_args()

    populator = PlayByPlayDataPopulator(args.db_path)
    results = populator.populate_season_playbyplay(
        season=args.season,
        season_type=args.season_type,
        max_games=args.max_games,
        batch_size=args.batch_size
    )

    print("\n🎯 Play-by-Play Data Population Results:")
    print("=" * 50)
    print(f"Season: {results['season']} {results['season_type']}")
    print(f"Games Processed: {results['games_processed']}")
    print(f"Games Successful: {results['games_successful']}")
    print(f"Games Skipped: {len(results['skipped_games'])}")
    print(f"Total Possessions: {results['total_possessions']}")
    print(f"Total Events: {results['total_events']}")
    print(f"Total Lineups: {results['total_lineups']}")
    print(f"Total Matchups: {results['total_matchups']}")

    if results['errors']:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(results['errors']) > 5:
            print(f"  ... and {len(results['errors']) - 5} more errors")

    if results['skipped_games']:
        print(f"\n⏭️  Skipped Games ({len(results['skipped_games'])}):")
        for game_id in results['skipped_games'][:10]:  # Show first 10
            print(f"  - {game_id}")
        if len(results['skipped_games']) > 10:
            print(f"  ... and {len(results['skipped_games']) - 10} more games")


if __name__ == "__main__":
    main()
