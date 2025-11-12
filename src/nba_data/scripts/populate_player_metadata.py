"""
Script to populate player metadata from NBA API.

This script fetches player information (names, physical attributes, etc.)
for all players in our database and stores it in the players table.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
import sqlite3
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.api.nba_stats_client import NBAStatsClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PlayerMetadataPopulator:
    """Populates player metadata from NBA API into database."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.client = NBAStatsClient()

    def get_player_ids_to_populate(self) -> List[int]:
        """Get all unique player IDs that need metadata."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get player IDs from season stats that don't exist in players table
            cursor.execute('''
                SELECT DISTINCT pss.player_id
                FROM player_season_stats pss
                LEFT JOIN players p ON pss.player_id = p.player_id
                WHERE p.player_id IS NULL
            ''')

            player_ids = [row[0] for row in cursor.fetchall()]
            logger.info(f"Found {len(player_ids)} players needing metadata")
            return player_ids

    def fetch_player_info(self, player_id: int) -> Dict[str, Any]:
        """Fetch player information from NBA API."""
        try:
            data = self.client.get_common_player_info(player_id)

            if 'resultSets' in data and data['resultSets']:
                headers = data['resultSets'][0]['headers']
                rows = data['resultSets'][0]['rowSet']

                if rows:
                    # Convert to dictionary
                    player_data = dict(zip(headers, rows[0]))

                    # Extract relevant fields
                    return {
                        'player_id': int(player_data.get('PERSON_ID', player_id)),
                        'player_name': player_data.get('DISPLAY_FIRST_LAST', ''),
                        'first_name': player_data.get('DISPLAY_FIRST_LAST', '').split(' ')[0] if player_data.get('DISPLAY_FIRST_LAST') else '',
                        'last_name': ' '.join(player_data.get('DISPLAY_FIRST_LAST', '').split(' ')[1:]) if player_data.get('DISPLAY_FIRST_LAST') else '',
                        'birth_date': player_data.get('BIRTHDATE', ''),
                        'country': player_data.get('COUNTRY', ''),
                        'height': player_data.get('HEIGHT', ''),
                        'weight': int(player_data.get('WEIGHT', 0)) if player_data.get('WEIGHT') else None,
                        'jersey_number': player_data.get('JERSEY', ''),
                        'position': player_data.get('POSITION', ''),
                        'team_id': int(player_data.get('TEAM_ID', 0)) if player_data.get('TEAM_ID') else None,
                        'wingspan': None,  # Not available in this endpoint
                        'draft_year': player_data.get('DRAFT_YEAR', ''),
                    }

            logger.warning(f"No data returned for player {player_id}")
            return None

        except Exception as e:
            logger.error(f"Failed to fetch player info for {player_id}: {e}")
            return None

    def populate_player_metadata(self) -> Dict[str, Any]:
        """Populate metadata for all players needing it."""
        results = {
            "players_processed": 0,
            "players_populated": 0,
            "errors": []
        }

        player_ids = self.get_player_ids_to_populate()

        if not player_ids:
            logger.info("No players need metadata population")
            return results

        logger.info(f"Starting metadata population for {len(player_ids)} players")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            batch_size = 10  # Process in smaller batches
            for i in range(0, len(player_ids), batch_size):
                batch = player_ids[i:i+batch_size]

                for player_id in batch:
                    results["players_processed"] += 1

                    # Fetch player info
                    player_info = self.fetch_player_info(player_id)

                    if player_info:
                        try:
                            # Insert player data
                            cursor.execute('''
                                INSERT OR REPLACE INTO players (
                                    player_id, player_name, first_name, last_name,
                                    birth_date, country, height, weight, jersey_number,
                                    position, team_id, draft_year
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                player_info['player_id'],
                                player_info['player_name'],
                                player_info['first_name'],
                                player_info['last_name'],
                                player_info['birth_date'],
                                player_info['country'],
                                player_info['height'],
                                player_info['weight'],
                                player_info['jersey_number'],
                                player_info['position'],
                                player_info['team_id'],
                                player_info['draft_year']
                            ))

                            results["players_populated"] += 1

                        except Exception as e:
                            error_msg = f"Failed to insert player {player_id}: {e}"
                            logger.error(error_msg)
                            results["errors"].append(error_msg)
                    else:
                        error_msg = f"No data available for player {player_id}"
                        logger.warning(error_msg)
                        results["errors"].append(error_msg)

                # Commit after each batch
                try:
                    conn.commit()
                    logger.info(f"Committed batch {i//batch_size + 1}/{(len(player_ids)-1)//batch_size + 1} ({results['players_populated']}/{results['players_processed']} players)")
                except Exception as e:
                    logger.error(f"Failed to commit batch: {e}")
                    results["errors"].append(f"Commit failed for batch {i//batch_size + 1}: {e}")

                # Small delay between batches to be respectful to the API
                import time
                time.sleep(1)

        logger.info(f"Metadata population complete: {results['players_populated']}/{results['players_processed']} players populated")
        return results


def main():
    """Main execution function."""
    populator = PlayerMetadataPopulator()
    results = populator.populate_player_metadata()

    print("\n📊 Player Metadata Population Results:")
    print(f"✅ Players processed: {results['players_processed']}")
    print(f"✅ Players populated: {results['players_populated']}")
    print(f"❌ Errors: {len(results['errors'])}")

    if results['errors']:
        print("\nFirst few errors:")
        for error in results['errors'][:5]:
            print(f"  - {error}")

    # Verify final state
    with sqlite3.connect("data/nba_stats.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM players")
        final_count = cursor.fetchone()[0]

        print(f"\n🎯 Final database state: {final_count} players with metadata")


if __name__ == "__main__":
    main()
