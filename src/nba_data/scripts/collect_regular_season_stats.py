import sys
import os
import argparse
import pandas as pd
import logging
from pathlib import Path
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.nba_data.api.nba_stats_client import NBAStatsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_regular_season_stats(client, season):
    """Fetch regular season stats for a given season (Base + Advanced)."""
    logger.info(f"Fetching regular season stats for {season}...")
    
    try:
        # 1. Fetch Base (for PTS, GP, MIN)
        logger.info("Fetching Base stats...")
        base_response = client.get_league_player_base_stats(
            season=season,
            season_type="Regular Season"
        )
        
        df_base = pd.DataFrame(
            base_response['resultSets'][0]['rowSet'],
            columns=base_response['resultSets'][0]['headers']
        )
        
        # 2. Fetch Advanced (for TS%, AST%, USG%)
        logger.info("Fetching Advanced stats...")
        adv_response = client.get_league_player_advanced_stats(
            season=season,
            season_type="Regular Season"
        )
        
        df_adv = pd.DataFrame(
            adv_response['resultSets'][0]['rowSet'],
            columns=adv_response['resultSets'][0]['headers']
        )
        
        # 3. Merge
        merge_cols = ['PLAYER_ID', 'TEAM_ID']
        # Filter cols to add
        cols_to_add = [c for c in df_adv.columns if c not in df_base.columns and c not in merge_cols]
        
        merged = pd.merge(
            df_base,
            df_adv[merge_cols + cols_to_add],
            on=merge_cols,
            how='inner'
        )
        
        logger.info(f"Successfully fetched and merged {len(merged)} players for {season}")
        return merged
        
    except Exception as e:
        logger.error(f"Error fetching stats for {season}: {e}")
        return pd.DataFrame()

def filter_qualified_players(df):
    """Filter for qualified players (GP >= 50, MIN >= 20)."""
    if df.empty:
        return df
        
    # Ensure numeric columns are numeric
    df['GP'] = pd.to_numeric(df['GP'])
    df['MIN'] = pd.to_numeric(df['MIN'])
    
    # Apply filters
    qualified = df[
        (df['GP'] >= 50) & 
        (df['MIN'] >= 20.0)
    ].copy()
    
    logger.info(f"Filtered to {len(qualified)} qualified players")
    return qualified

def main():
    parser = argparse.ArgumentParser(description='Collect Regular Season Stats')
    parser.add_argument('--seasons', nargs='+', help='Seasons to collect (e.g. 2023-24)', required=True)
    args = parser.parse_args()
    
    client = NBAStatsClient()
    
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    for season in args.seasons:
        logger.info(f"Processing {season}...")
        
        df = fetch_regular_season_stats(client, season)
        
        if not df.empty:
            qualified_df = filter_qualified_players(df)
            
            output_path = f"data/regular_season_{season}.csv"
            qualified_df.to_csv(output_path, index=False)
            logger.info(f"Saved {len(qualified_df)} rows to {output_path}")
        else:
            logger.warning(f"No data saved for {season}")
            
        # Polite delay between seasons
        time.sleep(2)

if __name__ == "__main__":
    main()
