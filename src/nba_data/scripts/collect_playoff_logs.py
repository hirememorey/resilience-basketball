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

def get_playoff_players(client, season):
    """Get list of all players who played in playoffs for the season."""
    logger.info(f"Fetching list of playoff players for {season}...")
    try:
        response = client.get_league_player_playoff_base_stats(season=season)
        
        headers = response['resultSets'][0]['headers']
        data = response['resultSets'][0]['rowSet']
        
        df = pd.DataFrame(data, columns=headers)
        return df['PLAYER_ID'].unique().tolist()
        
    except Exception as e:
        logger.error(f"Error fetching playoff player list: {e}")
        return []

def fetch_player_playoff_logs(client, player_id, season):
    """Fetch and merge Base and Advanced playoff game logs for a player."""
    try:
        # 1. Fetch Base Logs (PTS, REB, AST, MIN, FGM, etc.)
        resp_base = client.get_player_game_logs(
            player_id=player_id,
            season=season,
            season_type="Playoffs",
            measure_type="Base"
        )
        
        if not resp_base or 'resultSets' not in resp_base or not resp_base['resultSets']:
            return pd.DataFrame()
            
        df_base = pd.DataFrame(
            resp_base['resultSets'][0]['rowSet'],
            columns=resp_base['resultSets'][0]['headers']
        )
        
        if df_base.empty:
            return pd.DataFrame()

        # 2. Fetch Advanced Logs (POSS, USG%, AST%, TS%)
        resp_adv = client.get_player_game_logs(
            player_id=player_id,
            season=season,
            season_type="Playoffs",
            measure_type="Advanced"
        )
        
        if not resp_adv or 'resultSets' not in resp_adv or not resp_adv['resultSets']:
            # Fallback: return base only (will miss advanced metrics)
            logger.warning(f"No advanced logs for {player_id}")
            return df_base
            
        df_adv = pd.DataFrame(
            resp_adv['resultSets'][0]['rowSet'],
            columns=resp_adv['resultSets'][0]['headers']
        )
        
        if df_adv.empty:
            return df_base

        # 3. Merge
        # Common columns to merge on
        merge_cols = ['GAME_ID', 'PLAYER_ID', 'SEASON_YEAR']
        
        # Identify columns to add from Advanced (avoid duplicates)
        cols_to_add = [c for c in df_adv.columns if c not in df_base.columns and c not in merge_cols]
        
        # Merge
        # We use inner join to ensure data alignment
        merged = pd.merge(
            df_base,
            df_adv[merge_cols + cols_to_add],
            on=merge_cols,
            how='inner'
        )
        
        return merged
        
    except Exception as e:
        logger.error(f"Error fetching logs for player {player_id}: {e}")
        return pd.DataFrame()

def main():
    parser = argparse.ArgumentParser(description='Collect Playoff Game Logs')
    parser.add_argument('--seasons', nargs='+', help='Seasons to collect (e.g. 2023-24)', required=True)
    parser.add_argument('--player_id', type=int, help='Optional: Collect for single player only', required=False)
    args = parser.parse_args()
    
    client = NBAStatsClient()
    Path("data").mkdir(exist_ok=True)
    
    for season in args.seasons:
        logger.info(f"Processing {season}...")
        
        # Determine players to fetch
        if args.player_id:
            player_ids = [args.player_id]
            logger.info(f"Collecting for single player: {args.player_id}")
        else:
            player_ids = get_playoff_players(client, season)
            logger.info(f"Found {len(player_ids)} playoff players")
        
        all_logs = []
        
        for i, player_id in enumerate(player_ids):
            logs = fetch_player_playoff_logs(client, player_id, season)
            
            if not logs.empty:
                all_logs.append(logs)
            
            # Log progress every 10 players
            if (i + 1) % 10 == 0:
                logger.info(f"Processed {i + 1}/{len(player_ids)} players")
                
                # Incremental Save
                if all_logs:
                    temp_df = pd.concat(all_logs, ignore_index=True)
                    output_path = f"data/playoff_logs_{season}.csv"
                    temp_df.to_csv(output_path, index=False)
                    logger.info(f"Incremental save: {len(temp_df)} rows")
                
            time.sleep(0.6) # Respect rate limits
            
        if all_logs:
            final_df = pd.concat(all_logs, ignore_index=True)
            output_path = f"data/playoff_logs_{season}.csv"
            final_df.to_csv(output_path, index=False)
            logger.info(f"Saved {len(final_df)} game logs to {output_path}")
        else:
            logger.warning(f"No logs collected for {season}")

if __name__ == "__main__":
    main()
