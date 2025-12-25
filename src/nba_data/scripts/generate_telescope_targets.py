"""
Generate Telescope Targets (Time-Shifted Future Impact).

This script generates the target variable for the Telescope Model:
MAX(Playoff_PIE) over the next 3 seasons (t+1, t+2, t+3).

It addresses Survivorship Bias by explicitly imputing a replacement-level value
for players who wash out of the league or fail to make the playoffs in the future window.

Output:
    data/telescope_targets.csv: Contains PLAYER_ID, SEASON, TELESCOPE_TARGET
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
REPLACEMENT_LEVEL_PIE = 0.05  # Imputed value for washouts/non-playoff players
FUTURE_WINDOW_YEARS = 3
MIN_FUTURE_SEASONS_REQUIRED = 1  # If they play in 0 future seasons, we impute. If 1+, we take max.

def load_data():
    """Load necessary datasets."""
    # 1. Load Playoff PIE (The "Ground Truth" Outcomes)
    pie_path = Path("data/playoff_pie_data.csv")
    if not pie_path.exists():
        logger.error(f"Playoff PIE data not found at {pie_path}")
        sys.exit(1)
    
    df_pie = pd.read_csv(pie_path)
    logger.info(f"Loaded {len(df_pie)} playoff PIE records.")
    
    # 2. Load Regular Season Data (The "Universe" of Players)
    # We need this to know who existed in Season N so we can find their future.
    # We'll use the crucible_dataset.csv as it contains the processed RS features.
    rs_path = Path("data/crucible_dataset_full.csv")
    if not rs_path.exists():
        logger.error(f"{rs_path.name} not found. Run build_crucible_dataset.py first.")
        # Fallback to training_dataset.csv if crucible doesn't exist
        rs_path = Path("data/training_dataset.csv")
    
    if not rs_path.exists():
        logger.error("No Regular Season dataset found (checked crucible_dataset.csv and training_dataset.csv)")
        sys.exit(1)
        
    df_rs = pd.read_csv(rs_path)
    logger.info(f"Loaded {len(df_rs)} regular season records from {rs_path.name}.")
    
    return df_pie, df_rs

def get_next_seasons(current_season: str, n: int = 3) -> List[str]:
    """Return list of next n season strings (e.g., '2015-16' -> ['2016-17', ...])."""
    try:
        start_year = int(current_season.split('-')[0])
        next_seasons = []
        for i in range(1, n + 1):
            next_start = start_year + i
            next_end = (next_start + 1) % 100
            next_seasons.append(f"{next_start}-{next_end:02d}")
        return next_seasons
    except Exception as e:
        logger.warning(f"Error parsing season {current_season}: {e}")
        return []

def calculate_telescope_target(df_rs: pd.DataFrame, df_pie: pd.DataFrame) -> pd.DataFrame:
    """
    For each player-season in RS data, calculate MAX(Playoff_PIE) in next 3 years.
    Impute REPLACEMENT_LEVEL_PIE for missing future data.
    """
    logger.info("Calculating Telescope Targets...")
    
    # Create lookup dictionary for PIE: {(PLAYER_ID, SEASON): PIE}
    pie_lookup = df_pie.set_index(['PLAYER_ID', 'SEASON'])['PIE'].to_dict()
    
    targets = []
    
    # Get unique player-seasons from RS data
    # We only care about rows that actually exist in our training set
    player_seasons = df_rs[['PLAYER_ID', 'PLAYER_NAME', 'SEASON']].drop_duplicates()
    
    total = len(player_seasons)
    
    for idx, row in player_seasons.iterrows():
        player_id = row['PLAYER_ID']
        current_season = row['SEASON']
        
        # Determine future seasons
        future_seasons = get_next_seasons(current_season, FUTURE_WINDOW_YEARS)
        
        future_pies = []
        for season in future_seasons:
            key = (player_id, season)
            if key in pie_lookup:
                future_pies.append(pie_lookup[key])
        
        # LOGIC:
        # If we found at least one future playoff run -> Take the MAX PIE.
        # If we found NO future playoff runs -> Impute REPLACEMENT_LEVEL_PIE (Survivorship Logic).
        # Note: This imputes 0.05 for both "Missed Playoffs" and "Out of League".
        # This is intentional: The Telescope predicts impact. No impact = low score.
        
        if future_pies:
            target_value = max(future_pies)
            is_imputed = False
        else:
            target_value = REPLACEMENT_LEVEL_PIE
            is_imputed = True
            
        targets.append({
            'PLAYER_ID': player_id,
            'PLAYER_NAME': row['PLAYER_NAME'],
            'SEASON': current_season,
            'TELESCOPE_TARGET': target_value,
            'IS_IMPUTED': is_imputed,
            'FUTURE_SEASONS_FOUND': len(future_pies)
        })
        
        if idx % 1000 == 0:
            logger.info(f"Processed {idx}/{total} records...")

    df_targets = pd.DataFrame(targets)
    return df_targets

def main():
    logger.info("Starting Telescope Target Generation...")
    
    df_pie, df_rs = load_data()
    
    df_targets = calculate_telescope_target(df_rs, df_pie)
    
    output_path = Path("data/telescope_targets.csv")
    df_targets.to_csv(output_path, index=False)
    
    logger.info("="*50)
    logger.info(f"Successfully saved targets to {output_path}")
    logger.info(f"Total Records: {len(df_targets)}")
    logger.info(f"Imputed Records (No Future Playoffs): {df_targets['IS_IMPUTED'].sum()} ({df_targets['IS_IMPUTED'].mean()*100:.1f}%)")
    logger.info(f"Average Target Value: {df_targets['TELESCOPE_TARGET'].mean():.4f}")
    logger.info("="*50)

if __name__ == "__main__":
    main()

