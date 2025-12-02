"""
Collect Shot Quality Data with Shot Clock Ranges.

This script collects shot quality aggregates broken down by:
- Defender Distance (0-2, 2-4 feet for "tight" defense)
- Shot Clock Range (Late: 7-4, 4-0 vs Early: 22-18, 18-15)

This enables us to distinguish:
- Late Clock Pressure (bailout shots) - valuable
- Early Clock Pressure (bad shot selection) - indicates low IQ
"""

import sys
import os
import argparse
import pandas as pd
import logging
from pathlib import Path
import time
from functools import reduce
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.nba_data.api.shot_dashboard_client import ShotDashboardClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/shot_quality_clock_collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Defender distances we care about (tight defense)
TIGHT_DEFENSE_RANGES = [
    "0-2 Feet - Very Tight",
    "2-4 Feet - Tight"
]

# Shot clock ranges
LATE_CLOCK_RANGES = [
    "7-4 Late",
    "4-0 Very Late"
]

EARLY_CLOCK_RANGES = [
    "22-18 Very Early",
    "18-15 Early"
]

def fetch_shot_quality_with_clock(season, season_type, def_dist, shot_clock):
    """Fetch shot quality data for a specific defender distance and shot clock range.
    
    Creates its own client instance to avoid shared state issues in parallel execution.
    """
    # Create a fresh client for each task to avoid shared state issues
    client = ShotDashboardClient(rate_limit_delay=0.6)  # Reduced delay since we're parallelizing
    
    try:
        response = client.get_player_shot_dashboard_stats(
            season_year=season,
            season_type=season_type,
            close_def_dist_range=def_dist,
            shot_clock_range=shot_clock,
            dribble_range="",  # All dribbles
            shot_dist_range="",  # All shot distances
            per_mode="PerGame"
        )
        
        if response and 'resultSets' in response and response['resultSets']:
            rs = response['resultSets'][0]
            df = pd.DataFrame(rs['rowSet'], columns=rs['headers'])
            
            # Select key columns and process
            cols_to_keep = ['PLAYER_ID', 'PLAYER_NAME', 'PLAYER_LAST_TEAM_ID', 'GP', 'FGA', 'EFG_PCT']
            if all(col in df.columns for col in cols_to_keep):
                df_subset = df[cols_to_keep].copy()
                
                # Create labels
                def_label = "0_2" if "0-2" in def_dist else "2_4"
                clock_label = "LATE" if shot_clock in LATE_CLOCK_RANGES else "EARLY"
                
                # Rename columns with labels
                rename_map = {
                    'PLAYER_LAST_TEAM_ID': 'TEAM_ID',
                    'FGA': f'FGA_{def_label}_{clock_label}',
                    'EFG_PCT': f'EFG_{def_label}_{clock_label}'
                }
                df_subset = df_subset.rename(columns=rename_map)
                
                return df_subset, def_dist, shot_clock
    except Exception as e:
        logger.error(f"Error fetching {season} {season_type} {def_dist} {shot_clock}: {e}")
    
    return pd.DataFrame(), def_dist, shot_clock

def process_season(season, max_workers=8):
    """Collect shot quality data with shot clock for a full season (RS + PO) using parallel fetching."""
    combined_data = []
    
    for season_type in ["Regular Season", "Playoffs"]:
        type_label = "RS" if season_type == "Regular Season" else "PO"
        logger.info(f"Processing {season} {season_type}...")
        
        # Create tasks for all combinations
        tasks = []
        for def_dist in TIGHT_DEFENSE_RANGES:
            for shot_clock in LATE_CLOCK_RANGES + EARLY_CLOCK_RANGES:
                tasks.append((season, season_type, def_dist, shot_clock))
        
        total_combinations = len(tasks)
        logger.info(f"  Fetching {total_combinations} combinations in parallel (max_workers={max_workers})...")
        
        season_data = []
        
        # Use ThreadPoolExecutor to fetch all combinations in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(fetch_shot_quality_with_clock, *task): task 
                for task in tasks
            }
            
            # Process completed tasks with progress bar
            for future in tqdm(as_completed(future_to_task), total=total_combinations, 
                             desc=f"{season} {type_label}"):
                task = future_to_task[future]
                def_dist, shot_clock = task[2], task[3]
                
                try:
                    df, _, _ = future.result()
                    if not df.empty:
                        season_data.append(df)
                    else:
                        logger.warning(f"  No data for {def_dist} | {shot_clock}")
                except Exception as e:
                    logger.error(f"  Error processing {def_dist} | {shot_clock}: {e}")
        
        # Merge all combinations for this season_type
        if not season_data:
            logger.warning(f"  No data collected for {season} {season_type}")
            continue
        
        # Base columns for merging
        base_cols = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'GP']
        
        # Prepare each dataframe with only base cols + its unique FGA/EFG columns
        dfs_to_merge = []
        for df in season_data:
            # Get unique FGA/EFG columns from this dataframe
            unique_cols = [c for c in df.columns if c.startswith('FGA_') or c.startswith('EFG_')]
            # Select only base cols + unique cols
            df_subset = df[base_cols + unique_cols].copy()
            dfs_to_merge.append(df_subset)
        
        # Merge all dataframes using reduce
        def merge_func(left, right):
            return pd.merge(left, right, on=base_cols, how='outer', suffixes=('', '_DROP'))
        
        if len(dfs_to_merge) == 1:
            base_df = dfs_to_merge[0]
        else:
            base_df = reduce(merge_func, dfs_to_merge)
        
        # Remove any _DROP columns (shouldn't happen, but just in case)
        drop_cols = [c for c in base_df.columns if c.endswith('_DROP')]
        if drop_cols:
            base_df = base_df.drop(columns=drop_cols)
        
        # Add metadata
        base_df['SEASON'] = season
        base_df['SEASON_TYPE'] = type_label
        
        combined_data.append(base_df)
        
        logger.info(f"  ✅ Completed {season_type} ({len(base_df)} players)")
    
    if combined_data:
        return pd.concat(combined_data, ignore_index=True)
    return pd.DataFrame()

def main():
    parser = argparse.ArgumentParser(description='Collect Shot Quality Data with Shot Clock')
    parser.add_argument('--seasons', nargs='+', help='Seasons to collect (e.g. 2023-24)', required=True)
    parser.add_argument('--workers', type=int, default=8, help='Number of parallel workers (default: 8)')
    args = parser.parse_args()
    
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    logger.info(f"Starting clock data collection for {len(args.seasons)} season(s) with {args.workers} workers...")
    
    for season in args.seasons:
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting collection for {season}...")
        logger.info(f"{'='*60}")
        
        df = process_season(season, max_workers=args.workers)
        
        if not df.empty:
            output_path = f"data/shot_quality_clock_{season}.csv"
            df.to_csv(output_path, index=False)
            logger.info(f"✅ Saved shot quality clock data to {output_path} ({len(df)} rows)")
        else:
            logger.error(f"❌ Failed to collect data for {season}")

if __name__ == "__main__":
    main()

