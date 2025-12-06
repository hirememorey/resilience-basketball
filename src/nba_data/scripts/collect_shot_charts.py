
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

def load_qualified_players(season):
    """Load qualified players from existing regular_season CSV."""
    path = Path(f"data/regular_season_{season}.csv")
    if not path.exists():
        logger.error(f"Regular season data not found for {season} at {path}")
        return []
    
    df = pd.read_csv(path)
    if 'PLAYER_ID' not in df.columns:
        logger.error(f"PLAYER_ID column missing in {path}")
        return []
        
    return df['PLAYER_ID'].unique().tolist()

def load_all_players_from_predictive_dataset(season):
    """Load all players from predictive_dataset.csv for a given season.
    
    This includes players who don't meet the GP >= 50 / MIN >= 20.0 filter
    used in regular_season files, which is important for collecting shot charts
    for young players and role players who may not have qualified stats.
    """
    path = Path("results/predictive_dataset.csv")
    if not path.exists():
        logger.warning(f"predictive_dataset.csv not found at {path}, falling back to regular_season")
        return load_qualified_players(season)
    
    df = pd.read_csv(path)
    if 'PLAYER_ID' not in df.columns or 'SEASON' not in df.columns:
        logger.warning(f"Required columns missing in {path}, falling back to regular_season")
        return load_qualified_players(season)
    
    # Filter for the specific season
    season_df = df[df['SEASON'] == season].copy()
    if season_df.empty:
        logger.warning(f"No players found for {season} in predictive_dataset.csv, falling back to regular_season")
        return load_qualified_players(season)
    
    player_ids = season_df['PLAYER_ID'].unique().tolist()
    logger.info(f"Loaded {len(player_ids)} players from predictive_dataset.csv for {season}")
    return player_ids

def fetch_shot_chart(client, player_id, season):
    """Fetches both RS and Playoff shot charts for a player."""
    all_charts = []
    for season_type in ["Regular Season", "Playoffs"]:
        try:
            resp = client.get_player_shot_chart(player_id=player_id, season=season, season_type=season_type)
            if resp and 'resultSets' in resp and resp['resultSets']:
                df = pd.DataFrame(
                    resp['resultSets'][0]['rowSet'],
                    columns=resp['resultSets'][0]['headers']
                )
                if not df.empty:
                    df['SEASON_TYPE'] = season_type
                    all_charts.append(df)
        except Exception as e:
            logger.error(f"Error fetching shot chart for Player {player_id}, Season {season}, Type {season_type}: {e}")
            
    if all_charts:
        return pd.concat(all_charts, ignore_index=True)
    return pd.DataFrame()
        
def fetch_task(args):
    player_id, season = args
    # Create a fresh client for each task to avoid shared state issues
    local_client = NBAStatsClient()
    local_client.min_request_interval = 0.6 # Be conservative with this endpoint
    return fetch_shot_chart(local_client, player_id, season)

def main():
    parser = argparse.ArgumentParser(description='Collect Shot Chart Data')
    parser.add_argument('--seasons', nargs='+', help='Seasons to collect (e.g. 2023-24)', required=True)
    parser.add_argument('--workers', type=int, default=5, help='Number of parallel workers')
    parser.add_argument('--pilot', action='store_true', help='Run in pilot mode for a small subset of players.')
    parser.add_argument('--use-predictive-dataset', action='store_true', 
                       help='Use predictive_dataset.csv instead of regular_season files (includes more players)')
    args = parser.parse_args()
    
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # Pilot player IDs
    pilot_player_ids = [203999, 201939, 203507, 1629029] # Jokic, Curry, Giannis, Luka
    
    for season in args.seasons:
        logger.info(f"Processing Shot Charts for {season}...")
        
        if args.pilot:
            player_ids = pilot_player_ids
            logger.info(f"PILOT MODE: Using {len(player_ids)} specific players.")
        elif args.use_predictive_dataset:
            player_ids = load_all_players_from_predictive_dataset(season)
            logger.info(f"Using predictive_dataset.csv: {len(player_ids)} players for {season}")
        else:
            player_ids = load_qualified_players(season)
            logger.info(f"Using regular_season files: {len(player_ids)} qualified players for {season}")

        if not player_ids:
            logger.warning(f"Skipping {season} due to missing player list")
            continue
            
        logger.info(f"Found {len(player_ids)} qualified players for {season}")
        
        tasks = [(pid, season) for pid in player_ids]
        all_shot_charts = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            results = list(tqdm(executor.map(fetch_task, tasks), total=len(tasks), desc=f"Fetching {season} Shot Charts"))
            
            for res in results:
                if not res.empty:
                    all_shot_charts.append(res)
        
        if all_shot_charts:
            final_df = pd.concat(all_shot_charts, ignore_index=True)
            output_path = f"data/shot_charts_{season}.csv"
            final_df.to_csv(output_path, index=False)
            logger.info(f"✅ Saved {len(final_df)} shots to {output_path}")
        else:
            logger.warning(f"No shot charts collected for {season}")

if __name__ == "__main__":
    main()

