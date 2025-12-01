
import sys
import os
import argparse
import pandas as pd
import logging
from pathlib import Path
import time
import concurrent.futures
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.nba_data.api.nba_stats_client import NBAStatsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/shot_chart_collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_target_players(season):
    """
    Load the list of target players for a given season.
    We use results/resilience_scores_all.csv as the source of truth
    for players who actually played significant playoff minutes.
    """
    source_path = Path("results/resilience_scores_all.csv")
    if not source_path.exists():
        logger.error(f"Source file {source_path} not found!")
        return []
    
    df = pd.read_csv(source_path)
    
    # Filter for the specific season
    # The CSV has 'SEASON' column like '2023-24'
    season_players = df[df['SEASON'] == season][['PLAYER_ID', 'PLAYER_NAME']].drop_duplicates()
    
    targets = []
    for _, row in season_players.iterrows():
        targets.append({
            'id': row['PLAYER_ID'],
            'name': row['PLAYER_NAME'],
            'season': season
        })
        
    return targets

def fetch_shot_charts(client, player_id, season):
    """
    Fetch both Regular Season and Playoff shot charts.
    Returns a combined DataFrame with a 'SEASON_TYPE' column.
    """
    dfs = []
    
    for season_type in ["Regular Season", "Playoffs"]:
        try:
            data = client.get_player_shot_chart(
                player_id=player_id, 
                season=season, 
                season_type=season_type
            )
            
            # Check for valid response structure
            if data and 'resultSets' in data and len(data['resultSets']) > 0:
                headers = data['resultSets'][0]['headers']
                rows = data['resultSets'][0]['rowSet']
                
                if rows:
                    df = pd.DataFrame(rows, columns=headers)
                    df['SEASON_TYPE'] = season_type
                    df['PLAYER_ID'] = player_id
                    df['SEASON'] = season
                    dfs.append(df)
                    
        except Exception as e:
            # Log but don't crash - we want to continue with other players
            logger.warning(f"Failed to fetch {season_type} for {player_id}: {e}")
            
    if not dfs:
        return pd.DataFrame()
        
    return pd.concat(dfs, ignore_index=True)

def process_player_task(args):
    """
    Worker function to fetch data for a single player.
    Instantiates its own client to ensure thread safety.
    """
    player_target = args
    player_id = player_target['id']
    season = player_target['season']
    
    # Create a fresh client for this thread
    client = NBAStatsClient()
    # Set a conservative interval since we are running in parallel
    client.min_request_interval = 0.6 
    
    return fetch_shot_charts(client, player_id, season)

def main():
    parser = argparse.ArgumentParser(description='Collect Shot Chart Data')
    parser.add_argument('--seasons', nargs='+', help='Seasons to collect (e.g. 2023-24)', required=True)
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers')
    args = parser.parse_args()
    
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    for season in args.seasons:
        logger.info(f"Starting collection for {season}...")
        
        targets = get_target_players(season)
        if not targets:
            logger.warning(f"No target players found for {season}. Skipping.")
            continue
            
        logger.info(f"Found {len(targets)} players to process for {season}")
        
        all_shots = []
        
        # Parallel Execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            # Map returns results in order of input
            results = list(tqdm(
                executor.map(process_player_task, targets), 
                total=len(targets), 
                desc=f"Fetching {season} Shot Charts"
            ))
            
            for res in results:
                if not res.empty:
                    all_shots.append(res)
        
        # Save Results
        if all_shots:
            final_df = pd.concat(all_shots, ignore_index=True)
            output_path = f"data/shot_charts_{season}.csv"
            final_df.to_csv(output_path, index=False)
            logger.info(f"✅ Success! Saved {len(final_df)} shots to {output_path}")
        else:
            logger.warning(f"⚠️  No shot data collected for {season}")

if __name__ == "__main__":
    main()

