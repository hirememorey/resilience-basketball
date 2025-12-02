
import sys
import os
import argparse
import pandas as pd
import logging
from pathlib import Path
import time
from tenacity import retry, stop_after_attempt, wait_fixed

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.nba_data.api.nba_stats_client import NBAStatsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/shot_quality_collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DISTANCES = {
    "0-2 Feet - Very Tight": "0_2",
    "2-4 Feet - Tight": "2_4",
    "4-6 Feet - Open": "4_6",
    "6+ Feet - Wide Open": "6_PLUS"
}

def fetch_distance_data(client, season, season_type, distance_param):
    """Fetch data for a specific distance range."""
    try:
        resp = client.get_league_player_shooting_stats(
            season=season,
            season_type=season_type,
            close_def_dist=distance_param
        )
        
        if resp and 'resultSets' in resp and resp['resultSets']:
            rs = resp['resultSets'][0]
            df = pd.DataFrame(rs['rowSet'], columns=rs['headers'])
            return df
    except Exception as e:
        logger.error(f"Error fetching {season} {season_type} {distance_param}: {e}")
    return pd.DataFrame()

def process_season(season):
    """Collect and pivot data for a full season (RS + PO)."""
    client = NBAStatsClient()
    # Increase min interval slightly for safety
    client.min_request_interval = 1.0
    
    combined_data = []
    
    for season_type in ["Regular Season", "Playoffs"]:
        type_label = "RS" if season_type == "Regular Season" else "PO"
        logger.info(f"Processing {season} {season_type}...")
        
        # We need a base list of players to merge onto. 
        # We'll merge everything on PLAYER_ID.
        season_type_dfs = {}
        
        for dist_param, dist_label in DISTANCES.items():
            logger.info(f"  Fetching {dist_label} ({dist_param})...")
            df = fetch_distance_data(client, season, season_type, dist_param)
            
            if df.empty:
                logger.warning(f"  No data for {dist_label}")
                continue
                
            # Select key columns and rename
            # We want: FGA_FREQUENCY, EFG_PCT, FGA, GP
            cols_to_keep = ['PLAYER_ID', 'PLAYER_NAME', 'PLAYER_LAST_TEAM_ID', 'GP', 'FGA_FREQUENCY', 'EFG_PCT', 'FGA']
            df_subset = df[cols_to_keep].copy()
            
            # Rename value columns with distance suffix
            rename_map = {
                'PLAYER_LAST_TEAM_ID': 'TEAM_ID',
                'FGA_FREQUENCY': f'FREQ_{dist_label}',
                'EFG_PCT': f'EFG_{dist_label}',
                'FGA': f'FGA_{dist_label}'
            }
            df_subset = df_subset.rename(columns=rename_map)
            
            season_type_dfs[dist_label] = df_subset
            
        # Merge all distances for this season_type
        if not season_type_dfs:
            continue
            
        # Start with the first dataframe
        base_df = list(season_type_dfs.values())[0][['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'GP']]
        
        # Outer join all distance dataframes
        merged_df = base_df
        for label, df in season_type_dfs.items():
            merged_df = pd.merge(merged_df, df, on=['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'GP'], how='outer')
            
        # Add metadata
        merged_df['SEASON'] = season
        merged_df['SEASON_TYPE'] = type_label
        
        combined_data.append(merged_df)
        
    if combined_data:
        return pd.concat(combined_data, ignore_index=True)
    return pd.DataFrame()

def main():
    parser = argparse.ArgumentParser(description='Collect Shot Quality Aggregates')
    parser.add_argument('--seasons', nargs='+', help='Seasons to collect (e.g. 2023-24)', required=True)
    args = parser.parse_args()
    
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    for season in args.seasons:
        logger.info(f"Starting collection for {season}...")
        df = process_season(season)
        
        if not df.empty:
            output_path = f"data/shot_quality_aggregates_{season}.csv"
            df.to_csv(output_path, index=False)
            logger.info(f"✅ Saved shot quality data to {output_path}")
        else:
            logger.error(f"❌ Failed to collect data for {season}")

if __name__ == "__main__":
    main()

