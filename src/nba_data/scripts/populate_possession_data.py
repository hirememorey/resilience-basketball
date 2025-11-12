"""
Script to populate possession-level data from NBA play-by-play API.

This script fetches play-by-play data and parses it into granular possession-level
analytics for playoff resilience analysis.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
import sqlite3

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.api.possession_fetcher import create_possession_fetcher
from nba_data.db.schema import NBADatabaseSchema

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PossessionDataPopulator:
    """Populates possession-level data from NBA play-by-play API."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.schema = NBADatabaseSchema(db_path)
        self.fetcher = create_possession_fetcher()

    def populate_game_possessions(self, game_ids: List[str]) -> Dict[str, Any]:
        """
        Populate possession data for multiple games.

        Args:
            game_ids: List of NBA game IDs (format: 0022400001)

        Returns:
            Summary of population results
        """
        results = {
            "games_processed": 0,
            "total_possessions": 0,
            "total_events": 0,
            "total_lineups": 0,
            "total_matchups": 0,
            "errors": []
        }

        for game_id in game_ids:
            try:
                logger.info(f"Processing game {game_id}")
                game_results = self._populate_single_game(game_id)

                results["games_processed"] += 1
                results["total_possessions"] += game_results["possessions"]
                results["total_events"] += game_results["events"]
                results["total_lineups"] += game_results["lineups"]
                results["total_matchups"] += game_results["matchups"]

                logger.info(f"✅ Game {game_id}: {game_results['possessions']} possessions, {game_results['events']} events")

            except Exception as e:
                error_msg = f"Failed to process game {game_id}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        logger.info(f"Possession data population complete: {results['games_processed']} games processed")
        return results

    def _populate_single_game(self, game_id: str) -> Dict[str, int]:
        """
        Populate possession data for a single game.

        Args:
            game_id: NBA game ID

        Returns:
            Counts of inserted records
        """
        # Fetch possession data
        possessions = self.fetcher.fetch_game_possessions(game_id)

        results = {"possessions": 0, "events": 0, "lineups": 0, "matchups": 0}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for possession in possessions:
                try:
                    # Insert possession
                    self._insert_possession(cursor, possession)
                    results["possessions"] += 1

                    # Insert events
                    for event in possession.events:
                        self._insert_possession_event(cursor, event)
                        results["events"] += 1

                    # Insert lineups (if available)
                    for lineup in possession.lineups:
                        self._insert_possession_lineup(cursor, possession.possession_id, lineup)
                        results["lineups"] += 1

                    # Insert matchups (if available)
                    for matchup in possession.matchups:
                        self._insert_possession_matchup(cursor, possession.possession_id, matchup)
                        results["matchups"] += 1

                except Exception as e:
                    logger.warning(f"Failed to insert possession {possession.possession_id}: {e}")
                    continue

            conn.commit()

        return results

    def _insert_possession(self, cursor: sqlite3.Cursor, possession: Any) -> None:
        """Insert a possession record."""
        cursor.execute("""
            INSERT INTO possessions (
                possession_id, game_id, period, clock_time_start, clock_time_end,
                home_team_id, away_team_id, offensive_team_id, defensive_team_id,
                possession_start, possession_end, duration_seconds, points_scored,
                expected_points, possession_type, start_reason, end_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            possession.possession_id, possession.game_id, possession.period,
            possession.clock_time_start, possession.clock_time_end,
            possession.home_team_id, possession.away_team_id,
            possession.offensive_team_id, possession.defensive_team_id,
            possession.possession_start, possession.possession_end,
            possession.duration_seconds, possession.points_scored,
            possession.expected_points, possession.possession_type,
            possession.start_reason, possession.end_reason
        ))

    def _insert_possession_event(self, cursor: sqlite3.Cursor, event: Any) -> None:
        """Insert a possession event record."""
        cursor.execute("""
            INSERT INTO possession_events (
                event_id, possession_id, event_number, clock_time, elapsed_seconds,
                player_id, team_id, opponent_team_id, event_type, event_subtype,
                shot_type, shot_distance, shot_result, points_scored,
                assist_player_id, block_player_id, steal_player_id,
                turnover_type, foul_type, rebound_type,
                location_x, location_y, defender_player_id,
                touches_before_action, dribbles_before_action
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_id, event.possession_id, event.event_number,
            event.clock_time, event.elapsed_seconds, event.player_id,
            event.team_id, event.opponent_team_id, event.event_type,
            event.event_subtype, event.shot_type, event.shot_distance,
            event.shot_result, event.points_scored, event.assist_player_id,
            event.block_player_id, event.steal_player_id, event.turnover_type,
            event.foul_type, event.rebound_type, event.location_x,
            event.location_y, event.defender_player_id,
            event.touches_before_action, event.dribbles_before_action
        ))

    def _insert_possession_lineup(self, cursor: sqlite3.Cursor, possession_id: str, lineup: Dict) -> None:
        """Insert a possession lineup record."""
        cursor.execute("""
            INSERT INTO possession_lineups (
                possession_id, player_id, team_id, position
            ) VALUES (?, ?, ?, ?)
        """, (
            possession_id, lineup["player_id"], lineup["team_id"], lineup.get("position")
        ))

    def _insert_possession_matchup(self, cursor: sqlite3.Cursor, possession_id: str, matchup: Dict) -> None:
        """Insert a possession matchup record."""
        cursor.execute("""
            INSERT INTO possession_matchups (
                possession_id, offensive_player_id, defensive_player_id,
                matchup_start_time, matchup_end_time, duration_seconds,
                switches_during_matchup
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            possession_id, matchup["offensive_player_id"], matchup["defensive_player_id"],
            matchup.get("matchup_start_time"), matchup.get("matchup_end_time"),
            matchup.get("duration_seconds", 0), matchup.get("switches_during_matchup", 0)
        ))


def main():
    """Main execution function."""
    # Example game IDs for testing (2024-25 season games)
    # You would typically get these from the games table in your database
    test_game_ids = [
        "0022400001",  # Example game ID format
        # Add more game IDs as needed
    ]

    populator = PossessionDataPopulator()
    results = populator.populate_game_possessions(test_game_ids)

    print("\n🎯 Possession Data Population Results:")
    print(f"Games Processed: {results['games_processed']}")
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


if __name__ == "__main__":
    main()
