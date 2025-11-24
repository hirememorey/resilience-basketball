#!/usr/bin/env python3
"""
Minimal Player Data Population

Populates the players table with basic records needed for JOINs to work.
Extracts player_ids from existing tracking stats and creates minimal records.
"""

import sys
from pathlib import Path
import logging
import sqlite3
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/populate_minimal_players.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MinimalPlayerPopulator:
    """Populates minimal player data for JOIN operations."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)

    def populate_minimal_players(self) -> dict:
        """
        Populate players table with minimal records.

        Returns:
            Dictionary with operation results
        """
        results = {
            "players_found": 0,
            "players_inserted": 0,
            "errors": []
        }

        logger.info("Starting minimal player data population")

        # Get unique player_ids from tracking stats
        with sqlite3.connect(self.db_path) as conn:
            # Find all unique player_ids in the tracking stats
            query = """
            SELECT DISTINCT player_id
            FROM player_tracking_stats
            UNION
            SELECT DISTINCT player_id
            FROM player_advanced_stats
            UNION
            SELECT DISTINCT player_id
            FROM player_season_stats
            ORDER BY player_id
            """

            df_players = pd.read_sql(query, conn)
            results["players_found"] = len(df_players)

            logger.info(f"Found {len(df_players)} unique players in existing data")

            # Check which players are already in the players table
            existing_query = "SELECT player_id FROM players"
            existing_df = pd.read_sql(existing_query, conn)
            existing_ids = set(existing_df['player_id'].tolist())

            # Filter to players not already in the table
            new_players = df_players[~df_players['player_id'].isin(existing_ids)]
            results["players_to_insert"] = len(new_players)

            logger.info(f"{len(existing_df)} players already exist, {len(new_players)} new players to add")

            # Insert new players
            cursor = conn.cursor()
            inserted = 0

            for _, row in new_players.iterrows():
                player_id = row['player_id']

                try:
                    # Insert minimal player record
                    # We'll use placeholder values for most fields since we don't have the full data
                    cursor.execute("""
                        INSERT INTO players (
                            player_id, player_name, first_name, last_name,
                            position, team_id, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (
                        player_id,
                        f"Player {player_id}",  # Placeholder name
                        f"Player",              # Placeholder first name
                        f"{player_id}",         # Placeholder last name
                        "Unknown",              # Placeholder position
                        None                    # No team_id for now
                    ))

                    inserted += 1

                except Exception as e:
                    logger.error(f"Error inserting player {player_id}: {e}")
                    results["errors"].append(f"Player {player_id}: {e}")

            conn.commit()
            results["players_inserted"] = inserted

        logger.info(f"Successfully inserted {inserted} minimal player records")
        return results

    def verify_population(self) -> dict:
        """
        Verify that the players table has been populated.

        Returns:
            Dictionary with verification results
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Count total players
            cursor.execute("SELECT COUNT(*) FROM players")
            total_players = cursor.fetchone()[0]

            # Count players with tracking stats
            cursor.execute("""
                SELECT COUNT(DISTINCT pts.player_id)
                FROM player_tracking_stats pts
                JOIN players p ON pts.player_id = p.player_id
            """)
            players_with_tracking = cursor.fetchone()[0]

            # Sample a few records
            cursor.execute("SELECT player_id, player_name FROM players LIMIT 5")
            sample = cursor.fetchall()

        return {
            "total_players": total_players,
            "players_with_tracking": players_with_tracking,
            "sample_records": sample
        }


def main():
    """Main execution function."""
    populator = MinimalPlayerPopulator()

    # Populate minimal players
    results = populator.populate_minimal_players()

    print("\n=== Minimal Player Population Results ===")
    print(f"Players found in data: {results['players_found']}")
    print(f"Players already existed: {results.get('players_found', 0) - results.get('players_to_insert', 0)}")
    print(f"Players inserted: {results['players_inserted']}")

    if results['errors']:
        print(f"Errors: {len(results['errors'])}")
        for error in results['errors'][:3]:  # Show first 3 errors
            print(f"  - {error}")
        if len(results['errors']) > 3:
            print(f"  ... and {len(results['errors']) - 3} more")

    # Verify
    verification = populator.verify_population()

    print("\n=== Verification ===")
    print(f"Total players in table: {verification['total_players']}")
    print(f"Players with tracking data: {verification['players_with_tracking']}")
    print(f"Sample records: {verification['sample_records']}")

    if results['players_inserted'] > 0:
        print("\n✅ Minimal player population complete!")
    else:
        print("\n⚠️ No new players were inserted - they may already exist.")


if __name__ == "__main__":
    main()
