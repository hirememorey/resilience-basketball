
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
        logging.FileHandler("logs/phase2_collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_phase2_data(client, season):
    """Fetch specific data required for Phase 2 CII components."""
    logger.info(f"Fetching Phase 2 data for {season}...")
    
    try:
        # 1. Scoring Stats (Unassisted %, Mid-Range % Points)
        logger.info("Fetching Scoring stats...")
        scoring_data = client.get_league_player_scoring_stats(season=season)
        df_scoring = pd.DataFrame(
            scoring_data['resultSets'][0]['rowSet'],
            columns=scoring_data['resultSets'][0]['headers']
        )
        
        # Keep only relevant columns
        scoring_cols = ['PLAYER_ID', 'PLAYER_NAME', 'PCT_UAST_FGM', 'PCT_PTS_2PT_MR']
        # Check if columns exist
        available_scoring_cols = [c for c in scoring_cols if c in df_scoring.columns]
        df_scoring = df_scoring[available_scoring_cols]
        
        # 2. Pull-Up Stats (Tracking)
        logger.info("Fetching Pull-Up stats...")
        pullup_data = client.get_league_player_tracking_stats(
            season=season, 
            pt_measure_type="PullUpShot"
        )
        df_pullup = pd.DataFrame(
            pullup_data['resultSets'][0]['rowSet'],
            columns=pullup_data['resultSets'][0]['headers']
        )
        
        # Keep relevant columns
        pullup_cols = ['PLAYER_ID', 'PULL_UP_FGA', 'PULL_UP_FG3A', 'PULL_UP_FG3M']
        available_pullup_cols = [c for c in pullup_cols if c in df_pullup.columns]
        df_pullup = df_pullup[available_pullup_cols]
        
        # 3. Merge
        logger.info("Merging datasets...")
        if not df_scoring.empty and not df_pullup.empty:
            merged = pd.merge(
                df_scoring,
                df_pullup,
                on='PLAYER_ID',
                how='outer'
            )
            
            # Fill NaNs
            # If player exists in one but not other, likely 0 volume in the missing one
            merged = merged.fillna(0)
            
            # Add Season
            merged['SEASON'] = season
            
            return merged
        else:
            logger.warning("One of the datasets is empty.")
            return pd.concat([df_scoring, df_pullup], axis=1).fillna(0) # Fallback

    except Exception as e:
        logger.error(f"Error fetching Phase 2 data for {season}: {e}")
        return pd.DataFrame()

def main():
    parser = argparse.ArgumentParser(description='Collect Phase 2 Stats')
    parser.add_argument('--seasons', nargs='+', help='Seasons to collect (e.g. 2023-24)', required=True)
    args = parser.parse_args()
    
    client = NBAStatsClient()
    
    Path("data/phase2").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    for season in args.seasons:
        logger.info(f"Processing {season}...")
        
        df = fetch_phase2_data(client, season)
        
        if not df.empty:
            output_path = f"data/phase2/phase2_stats_{season}.csv"
            df.to_csv(output_path, index=False)
            logger.info(f"Saved {len(df)} rows to {output_path}")
            
            # Validation peek
            harden = df[df['PLAYER_NAME'].str.contains('Harden', case=False, na=False)]
            if not harden.empty:
                logger.info(f"Validation (Harden): {harden.iloc[0].to_dict()}")
        else:
            logger.warning(f"No data saved for {season}")
            
        time.sleep(1)

if __name__ == "__main__":
    main()

