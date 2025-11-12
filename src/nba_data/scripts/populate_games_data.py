"""
Script to populate games data from existing possession records.

This script extracts game information from the possessions table and populates the games table.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
import sqlite3

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.db.schema import NBADatabaseSchema

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GamesDataPopulator:
    """Populates games data from possession records."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.schema = NBADatabaseSchema(db_path)

    def populate_games_data(self) -> Dict[str, Any]:
        """
        Populate games data from possession records.

        Returns:
            Summary of population results
        """
        logger.info("Starting games data population from possessions")

        results = {
            "games_processed": 0,
            "games_inserted": 0,
            "errors": []
        }

        conn = sqlite3.connect(self.db_path)

        try:
            # Get unique games from possessions table
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT
                    game_id,
                    home_team_id,
                    away_team_id,
                    MIN(created_at) as first_possession_time
                FROM possessions
                GROUP BY game_id, home_team_id, away_team_id
                ORDER BY game_id
            """)

            games_data = cursor.fetchall()
            logger.info(f"Found {len(games_data)} unique games in possessions table")

            for game_data in games_data:
                game_id, home_team_id, away_team_id, first_possession_time = game_data

                try:
                    # Derive season and season_type from game_id
                    season, season_type = self._derive_season_info(game_id)

                    game_record = {
                        "game_id": game_id,
                        "game_date": None,  # Not available in possessions data
                        "home_team_id": home_team_id,
                        "away_team_id": away_team_id,
                        "home_team_score": None,  # Not available in possessions data
                        "away_team_score": None,  # Not available in possessions data
                        "season": season,
                        "season_type": season_type
                    }

                    self._insert_game_data(game_record)
                    results["games_inserted"] += 1
                    results["games_processed"] += 1

                    if results["games_processed"] % 100 == 0:
                        logger.info(f"Processed {results['games_processed']} games...")

                except Exception as e:
                    logger.error(f"Error processing game {game_id}: {e}")
                    results["errors"].append(f"game_id {game_id}: {str(e)}")
                    results["games_processed"] += 1

        finally:
            conn.close()

        logger.info(f"Games population complete: {results['games_inserted']} inserted, {len(results['errors'])} errors")
        return results

    def _derive_season_info(self, game_id: str) -> tuple[str, str]:
        """Derive season and season_type from game_id.

        NBA game_ids follow format: {season_type}{season}{game_number}
        - season_type: 0= preseason, 1=regular, 2=playoffs, 4=allstar, 5=playin
        - season: last 2 digits of starting year (e.g., 23 for 2023-24)
        - game_number: sequential game number
        """
        if not game_id or len(game_id) < 10:
            return "2024-25", "Regular Season"

        season_type_code = game_id[0]
        season_code = game_id[1:3]

        # Map season type
        season_type_map = {
            "0": "Pre Season",
            "1": "Regular Season",
            "2": "Playoffs",
            "4": "All-Star",
            "5": "Play-In"
        }
        season_type = season_type_map.get(season_type_code, "Regular Season")

        # Convert season code to full season string
        try:
            start_year = 2000 + int(season_code)
            end_year = start_year + 1
            season = f"{start_year}-{str(end_year)[-2:]}"
        except (ValueError, IndexError):
            season = "2024-25"

        return season, season_type

    def _insert_game_data(self, game_data: Dict[str, Any]) -> None:
        """Insert game data into database."""
        conn = sqlite3.connect(self.db_path)

        try:
            cursor = conn.cursor()

            # Check if game already exists
            cursor.execute("SELECT COUNT(*) FROM games WHERE game_id = ?", (game_data["game_id"],))
            exists = cursor.fetchone()[0] > 0

            if exists:
                # Update existing record
                cursor.execute("""
                    UPDATE games SET
                        game_date = ?,
                        home_team_id = ?,
                        away_team_id = ?,
                        home_team_score = ?,
                        away_team_score = ?,
                        season = ?,
                        season_type = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE game_id = ?
                """, (
                    game_data["game_date"],
                    game_data["home_team_id"],
                    game_data["away_team_id"],
                    game_data["home_team_score"],
                    game_data["away_team_score"],
                    game_data["season"],
                    game_data["season_type"],
                    game_data["game_id"]
                ))
                logger.debug(f"Updated existing game: {game_data['game_id']}")
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO games (
                        game_id, game_date, home_team_id, away_team_id,
                        home_team_score, away_team_score, season, season_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    game_data["game_id"],
                    game_data["game_date"],
                    game_data["home_team_id"],
                    game_data["away_team_id"],
                    game_data["home_team_score"],
                    game_data["away_team_score"],
                    game_data["season"],
                    game_data["season_type"]
                ))
                logger.debug(f"Inserted new game: {game_data['game_id']}")

            conn.commit()

        except Exception as e:
            logger.error(f"Error inserting game data: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()


def main():
    """Main execution function."""
    populator = GamesDataPopulator()
    results = populator.populate_games_data()

    print("\n🎯 Games Data Population Complete")
    print("=" * 40)
    print(f"Games processed: {results['games_processed']}")
    print(f"Games inserted: {results['games_inserted']}")
    print(f"Errors: {len(results['errors'])}")

    if results['errors']:
        print("\n❌ Errors encountered:")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(results['errors']) > 5:
            print(f"  ... and {len(results['errors']) - 5} more")

    return results


if __name__ == "__main__":
    main()
