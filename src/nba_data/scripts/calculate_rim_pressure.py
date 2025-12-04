import pandas as pd
import logging
from pathlib import Path
import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_shot_data(seasons):
    """Load shot chart data for requested seasons."""
    all_shots = []
    
    for season in seasons:
        path = Path(f"data/shot_charts_{season}.csv")
        if path.exists():
            try:
                df = pd.read_csv(path)
                # Ensure SEASON column exists or derive it
                if 'SEASON' not in df.columns:
                    df['SEASON'] = season
                all_shots.append(df)
                logger.info(f"Loaded {len(df)} shots for {season}")
            except Exception as e:
                logger.error(f"Error loading {path}: {e}")
        else:
            logger.warning(f"Missing {path}")
            
    return pd.concat(all_shots, ignore_index=True) if all_shots else pd.DataFrame()

def calculate_features(df):
    """Calculate Rim Pressure features."""
    if df.empty:
        logger.warning("Empty dataframe")
        return pd.DataFrame()

    # Filter for RS and PO
    rs_shots = df[df['SEASON_TYPE'] == 'Regular Season'].copy()
    po_shots = df[df['SEASON_TYPE'] == 'Playoffs'].copy()
    
    if rs_shots.empty:
        logger.warning("No Regular Season shots found")
        return pd.DataFrame()

    # --- Process Regular Season ---
    # Group by Player-Season
    rs_agg = rs_shots.groupby(['PLAYER_ID', 'PLAYER_NAME', 'SEASON']).apply(
        lambda x: pd.Series({
            'RS_FGA': len(x),
            'RS_RIM_FGA': len(x[x['SHOT_ZONE_BASIC'] == 'Restricted Area']),
            'RS_RIM_FGM': len(x[(x['SHOT_ZONE_BASIC'] == 'Restricted Area') & (x['SHOT_MADE_FLAG'] == 1)])
        })
    ).reset_index()
    
    rs_agg['RS_RIM_APPETITE'] = rs_agg['RS_RIM_FGA'] / rs_agg['RS_FGA']
    rs_agg['RS_RIM_PCT'] = rs_agg['RS_RIM_FGM'] / rs_agg['RS_RIM_FGA'] # Rim Finishing
    rs_agg = rs_agg.fillna(0)

    # --- Process Playoffs ---
    if po_shots.empty:
        logger.warning("No Playoff shots found")
        # Return just RS features if no PO data (though unlikely for our target players)
        return rs_agg

    po_agg = po_shots.groupby(['PLAYER_ID', 'PLAYER_NAME', 'SEASON']).apply(
        lambda x: pd.Series({
            'PO_FGA': len(x),
            'PO_RIM_FGA': len(x[x['SHOT_ZONE_BASIC'] == 'Restricted Area']),
            'PO_RIM_FGM': len(x[(x['SHOT_ZONE_BASIC'] == 'Restricted Area') & (x['SHOT_MADE_FLAG'] == 1)])
        })
    ).reset_index()
    
    po_agg['PO_RIM_APPETITE'] = po_agg['PO_RIM_FGA'] / po_agg['PO_FGA']
    po_agg['PO_RIM_PCT'] = po_agg['PO_RIM_FGM'] / po_agg['PO_RIM_FGA']
    po_agg = po_agg.fillna(0)
    
    # --- Merge ---
    merged = pd.merge(
        rs_agg,
        po_agg,
        on=['PLAYER_ID', 'PLAYER_NAME', 'SEASON'],
        how='inner'
    )
    
    # --- Calculate Resilience ---
    # Rim Pressure Resilience = PO Appetite / RS Appetite
    merged['RIM_PRESSURE_RESILIENCE'] = merged['PO_RIM_APPETITE'] / merged['RS_RIM_APPETITE']
    
    # Handle division by zero (if RS appetite is 0)
    merged.loc[merged['RS_RIM_APPETITE'] == 0, 'RIM_PRESSURE_RESILIENCE'] = 0
    
    return merged

def main():
    # Determine available seasons from file system
    files = list(Path('data').glob('shot_charts_*.csv'))
    seasons = [f.stem.replace('shot_charts_', '') for f in files]
    
    if not seasons:
        logger.error("No shot chart data found in data/")
        return

    logger.info(f"Found shot charts for seasons: {seasons}")
    
    shots_df = load_shot_data(seasons)
    
    logger.info("Calculating Rim Pressure Features...")
    features_df = calculate_features(shots_df)
    
    if features_df.empty:
        logger.warning("No features calculated.")
        return

    # Filter for sample size
    # Minimum RS FGA and PO FGA to avoid noise
    min_rs_fga = 100
    min_po_fga = 30
    
    filtered_df = features_df[
        (features_df['RS_FGA'] >= min_rs_fga) & 
        (features_df['PO_FGA'] >= min_po_fga)
    ].copy()
    
    logger.info(f"Filtered dataset from {len(features_df)} to {len(filtered_df)} rows (Min RS FGA: {min_rs_fga}, Min PO FGA: {min_po_fga})")
    
    output_path = Path("results/rim_pressure_features.csv")
    output_path.parent.mkdir(exist_ok=True)
    
    filtered_df.to_csv(output_path, index=False)
    logger.info(f"✅ Saved rim pressure features to {output_path}")
    
    # Top 5 Resilient
    print("\nTop 5 Rim Pressure Resilience:")
    print(filtered_df.sort_values('RIM_PRESSURE_RESILIENCE', ascending=False)[['PLAYER_NAME', 'SEASON', 'RIM_PRESSURE_RESILIENCE', 'RS_RIM_APPETITE', 'PO_RIM_APPETITE']].head(10))
    
    # Bottom 5
    print("\nBottom 5 Rim Pressure Resilience:")
    print(filtered_df.sort_values('RIM_PRESSURE_RESILIENCE', ascending=True)[['PLAYER_NAME', 'SEASON', 'RIM_PRESSURE_RESILIENCE', 'RS_RIM_APPETITE', 'PO_RIM_APPETITE']].head(10))

if __name__ == "__main__":
    main()


