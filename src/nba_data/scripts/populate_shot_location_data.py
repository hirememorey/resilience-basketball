"""
Script to populate player shot location data from the NBA API.

This script fetches detailed shot chart data for each player for every season
and stores it in the player_shot_locations table in the database.
"""

import sys
from pathlib import Path
import logging
import sqlite3
import pandas as pd
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.api.nba_stats_client import NBAStatsClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ShotLocationPopulator:
    """Populates player shot location data."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.client = NBAStatsClient()

    def populate_shot_locations(self):
        """Fetch and store shot location data for all players and seasons."""
        logger.info("Starting player shot location data population...")

        conn = sqlite3.connect(self.db_path)
        
        # Get all player IDs and all seasons from the player_season_stats table
        players_seasons_df = pd.read_sql_query("SELECT DISTINCT player_id, season FROM player_season_stats", conn)
        
        if players_seasons_df.empty:
            logger.warning("No players or seasons found. Run player data population first.")
            conn.close()
            return

        logger.info(f"Found {len(players_seasons_df)} unique player-season combinations to process.")

        for _, row in tqdm(players_seasons_df.iterrows(), total=len(players_seasons_df), desc="Populating Shot Data"):
            player_id = row['player_id']
            season = row['season']

            for season_type in ["Regular Season", "Playoffs"]:
                try:
                    shot_data = self.client.get_player_shot_chart(player_id=player_id, season=season, season_type=season_type)
                    
                    if not shot_data or not shot_data.get('resultSets'):
                        logger.info(f"No shot data found for player {player_id} in {season} {season_type}.")
                        continue

                    headers = shot_data['resultSets'][0]['headers']
                    rows = shot_data['resultSets'][0]['rowSet']
                    
                    if not rows:
                        continue
                        
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
                    
                    logger.info(f"Inserted {len(df_to_insert)} shot records for player {player_id} in {season} {season_type}.")

                except Exception as e:
                    logger.error(f"Failed to process shot data for player {player_id}, season {season}, type {season_type}: {e}")

        conn.close()
        logger.info("Player shot location data population complete.")

def main():
    """Main execution function."""
    populator = ShotLocationPopulator()
    populator.populate_shot_locations()

if __name__ == "__main__":
    main()
