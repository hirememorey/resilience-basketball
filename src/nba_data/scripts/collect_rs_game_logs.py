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
        logging.FileHandler("logs/rs_logs_collection.log"),
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

def fetch_player_rs_logs(client, player_id, season):
    """Fetch and merge Base and Advanced regular season game logs for a player."""
    try:
        # 1. Fetch Base Logs
        resp_base = client.get_player_game_logs(
            player_id=player_id,
            season=season,
            season_type="Regular Season",
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

        # 2. Fetch Advanced Logs
        resp_adv = client.get_player_game_logs(
            player_id=player_id,
            season=season,
            season_type="Regular Season",
            measure_type="Advanced"
        )
        
        if not resp_adv or 'resultSets' not in resp_adv or not resp_adv['resultSets']:
            # Fallback to base only if advanced fails
            return df_base
            
        df_adv = pd.DataFrame(
            resp_adv['resultSets'][0]['rowSet'],
            columns=resp_adv['resultSets'][0]['headers']
        )
        
        if df_adv.empty:
            return df_base

        # 3. Merge
        merge_cols = ['GAME_ID', 'PLAYER_ID', 'SEASON_YEAR']
        cols_to_add = [c for c in df_adv.columns if c not in df_base.columns and c not in merge_cols]
        
        merged = pd.merge(
            df_base,
            df_adv[merge_cols + cols_to_add],
            on=merge_cols,
            how='inner'
        )
        
        # Ensure PLAYER_ID is correct
        merged['PLAYER_ID'] = player_id
        
        return merged
        
    except Exception as e:
        logger.error(f"Error fetching logs for player {player_id}: {e}")
        return pd.DataFrame()

def process_player(args):
    """Wrapper for threaded execution."""
    client, player_id, season = args
    return fetch_player_rs_logs(client, player_id, season)

def main():
    parser = argparse.ArgumentParser(description='Collect Regular Season Game Logs')
    parser.add_argument('--seasons', nargs='+', help='Seasons to collect (e.g. 2023-24)', required=True)
    parser.add_argument('--workers', type=int, default=5, help='Number of parallel workers')
    args = parser.parse_args()
    
    # Create a client for the main thread (or shared if thread-safe enough)
    # Note: requests.Session is not strictly thread-safe, but usually fine if read-only.
    # However, the NBAStatsClient has state (rate limiting). 
    # For robustness with the stateful client, we'll use a separate client per worker 
    # or just use one client and rely on its internal locking if it had it. 
    # Given the simple client, passing a new client or a shared one might be tricky with the state.
    # BEST APPROACH: Use one client, but set the min_interval very low, and let the API return 429s 
    # which the client handles with retries. 
    # OR: Just sequential with very low interval.
    
    # Let's try sequential with optimized interval first as it's safer for this specific client implementation.
    # The user asked to speed it up "without messing up rate limit".
    # Parallel requests often trigger 429s.
    # Sequential with 0.6s interval = ~100 requests/min. 
    # 209 players * 2 requests (Base+Adv) = 418 requests.
    # 418 * 0.6s = 250s = 4 mins.
    # To go faster, we need parallel.
    
    # We will use ThreadPool but create a new client for each thread to avoid state corruption,
    # knowing that the IP-level rate limit is shared.
    
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    for season in args.seasons:
        logger.info(f"Processing {season}...")
        
        player_ids = load_qualified_players(season)
        if not player_ids:
            logger.warning(f"Skipping {season} due to missing player list")
            continue
            
        logger.info(f"Found {len(player_ids)} qualified players for {season}")
        
        all_logs = []
        
        # We'll use a ThreadPoolExecutor
        # We need to be careful about rate limits.
        # We'll create a simple function that instantiates its own client to avoid shared state issues
        
        def fetch_task(pid):
            # Create a fresh client for each task to avoid shared state issues
            # Set a low internal interval because the global rate limit is the bottleneck
            local_client = NBAStatsClient()
            local_client.min_request_interval = 0.5 
            return fetch_player_rs_logs(local_client, pid, season)

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            # Use tqdm for progress bar
            results = list(tqdm(executor.map(fetch_task, player_ids), total=len(player_ids), desc=f"Fetching {season}"))
            
            for res in results:
                if not res.empty:
                    all_logs.append(res)
        
        if all_logs:
            final_df = pd.concat(all_logs, ignore_index=True)
            output_path = f"data/rs_game_logs_{season}.csv"
            final_df.to_csv(output_path, index=False)
            logger.info(f"✅ Saved {len(final_df)} game logs to {output_path}")
        else:
            logger.warning(f"No logs collected for {season}")

if __name__ == "__main__":
    main()








