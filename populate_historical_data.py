"""
Script to populate historical data from NBA API into our database.

This script orchestrates the population of:
1. Player Season Stats (Regular Season & Playoffs)
2. Player Advanced Stats
3. Player Tracking Stats
4. Team Data
5. Game Data (derived from possessions)

It handles the full historical range (2015-16 to 2024-25).
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import populators
from src.nba_data.scripts.populate_player_data import PlayerDataPopulator
from src.nba_data.scripts.populate_teams_data import TeamsDataPopulator
from src.nba_data.scripts.populate_games_data import GamesDataPopulator
from src.nba_data.db.schema import NBADatabaseSchema

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/historical_population.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def populate_season(season: str, season_types: List[str] = None):
    """Populate data for a single season."""
    if season_types is None:
        season_types = ["Regular Season", "Playoffs"]
        
    logger.info(f"🚀 Starting population for {season}...")
    
    populator = PlayerDataPopulator()
    
    for season_type in season_types:
        try:
            logger.info(f"Populating {season_type} data...")
            populator.populate_all_player_data(season, season_type)
        except Exception as e:
            logger.error(f"Failed to populate {season} {season_type}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Populate historical NBA data")
    parser.add_argument("--seasons", nargs="+", help="Specific seasons to populate (e.g., 2023-24 2024-25)")
    parser.add_argument("--season-types", nargs="+", choices=["Regular Season", "Playoffs"], 
                      help="Season types to populate (default: both)")
    parser.add_argument("--skip-teams", action="store_true", help="Skip team data population")
    
    args = parser.parse_args()
    
    # Default seasons if none provided
    seasons = args.seasons if args.seasons else [
        "2024-25", "2023-24", "2022-23", "2021-22", "2020-21",
        "2019-20", "2018-19", "2017-18", "2016-17", "2015-16"
    ]
    
    # Initialize DB
    schema = NBADatabaseSchema()
    schema.create_all_tables()
    
    # 1. Populate Player Data (Season by Season)
    for season in seasons:
        populate_season(season, args.season_types)

        # Populate Games Data for the season
        try:
            logger.info(f"Populating Games data for {season}...")
            games_populator = GamesDataPopulator()
            for season_type in (args.season_types if args.season_types else ["Regular Season", "Playoffs"]):
                games_populator.populate_games_for_season(season, season_type)
        except Exception as e:
            logger.error(f"Failed to populate games for {season}: {e}")
        
    # 2. Populate Team Data (Derived from players)
    if not args.skip_teams:
        logger.info("Populating team data...")
        teams_populator = TeamsDataPopulator()
        teams_populator.populate_teams_data()
        
    logger.info("🎉 Historical population complete!")

if __name__ == "__main__":
    main()

