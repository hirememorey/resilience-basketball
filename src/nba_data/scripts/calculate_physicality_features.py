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

def load_data(seasons):
    """Load RS and PO data for requested seasons."""
    rs_data = []
    po_data = []
    
    for season in seasons:
        # Load Regular Season
        rs_path = Path(f"data/regular_season_{season}.csv")
        if rs_path.exists():
            df = pd.read_csv(rs_path)
            df['SEASON'] = season
            rs_data.append(df)
        else:
            logger.warning(f"Missing {rs_path}")
            
        # Load Playoff Logs
        po_path = Path(f"data/playoff_logs_{season}.csv")
        if po_path.exists():
            df = pd.read_csv(po_path)
            df['SEASON'] = season
            po_data.append(df)
        else:
            logger.warning(f"Missing {po_path}")
            
    return (
        pd.concat(rs_data, ignore_index=True) if rs_data else pd.DataFrame(),
        pd.concat(po_data, ignore_index=True) if po_data else pd.DataFrame()
    )

def calculate_features(rs_df, po_df):
    """Calculate Physicality (FTr) features."""
    if rs_df.empty or po_df.empty:
        logger.warning("Empty RS or PO dataframe")
        return pd.DataFrame()

    # --- Process Regular Season ---
    # Calculate FTr = FTA / FGA
    # Ensure numeric
    cols_to_numeric_rs = ['FTA', 'FGA', 'GP']
    for col in cols_to_numeric_rs:
        if col in rs_df.columns:
            rs_df[col] = pd.to_numeric(rs_df[col], errors='coerce').fillna(0)

    rs_df['RS_FTr'] = rs_df['FTA'] / rs_df['FGA']
    # Handle division by zero or NaN
    rs_df['RS_FTr'] = rs_df['RS_FTr'].fillna(0)
    # Cap infinite values if any FGA is 0
    rs_df.loc[rs_df['FGA'] == 0, 'RS_FTr'] = 0
    
    # Calculate Total FGA for filtering
    if 'GP' in rs_df.columns:
        rs_df['RS_FGA_TOTAL'] = rs_df['FGA'] * rs_df['GP']
    else:
        rs_df['RS_FGA_TOTAL'] = rs_df['FGA'] # Fallback if GP missing, though unlikely
    
    rs_features = rs_df[['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'RS_FTr', 'FTA', 'FGA', 'RS_FGA_TOTAL']].rename(columns={'FTA': 'RS_FTA', 'FGA': 'RS_FGA'})

    # --- Process Playoffs ---
    # po_df contains game logs. We need to aggregate by Player-Season.
    # Ensure numeric
    cols_to_numeric = ['FTA', 'FGA']
    for col in cols_to_numeric:
        po_df[col] = pd.to_numeric(po_df[col], errors='coerce').fillna(0)
        
    po_agg = po_df.groupby(['PLAYER_ID', 'PLAYER_NAME', 'SEASON']).agg({
        'FTA': 'sum',
        'FGA': 'sum',
        'GAME_ID': 'count' 
    }).reset_index()
    
    po_agg = po_agg.rename(columns={'FTA': 'PO_FTA', 'FGA': 'PO_FGA', 'GAME_ID': 'PO_GP'})
    
    po_agg['PO_FTr'] = po_agg['PO_FTA'] / po_agg['PO_FGA']
    po_agg['PO_FTr'] = po_agg['PO_FTr'].fillna(0)
    po_agg.loc[po_agg['PO_FGA'] == 0, 'PO_FTr'] = 0
    
    # --- Merge ---
    merged = pd.merge(
        rs_features,
        po_agg,
        on=['PLAYER_ID', 'PLAYER_NAME', 'SEASON'],
        how='inner'
    )
    
    # --- Calculate Resilience ---
    # FTr Resilience = PO FTr / RS FTr
    # Or maybe Delta? IMPLEMENTATION_PLAN says "Playoff FTr / RS FTr"
    
    merged['FTr_RESILIENCE'] = merged['PO_FTr'] / merged['RS_FTr']
    
    # Handle cases where RS_FTr is 0
    merged.loc[merged['RS_FTr'] == 0, 'FTr_RESILIENCE'] = 0 
    
    # Add FTr Delta as well, just in case
    merged['FTr_DELTA'] = merged['PO_FTr'] - merged['RS_FTr']
    
    return merged

def main():
    # Determine available seasons from file system
    files = list(Path('data').glob('regular_season_*.csv'))
    seasons = [f.stem.replace('regular_season_', '') for f in files]
    
    if not seasons:
        logger.error("No data found in data/")
        return

    logger.info(f"Found data for seasons: {seasons}")
    
    rs_df, po_df = load_data(seasons)
    
    logger.info("Calculating Physicality Features...")
    features_df = calculate_features(rs_df, po_df)
    
    if features_df.empty:
        logger.warning("No features calculated.")
        return

    # Filter for sample size
    # Minimum RS FGA (Total) and PO FGA (Total) to avoid noise
    min_rs_fga_total = 100
    min_po_fga_total = 30
    
    filtered_df = features_df[
        (features_df['RS_FGA_TOTAL'] >= min_rs_fga_total) & 
        (features_df['PO_FGA'] >= min_po_fga_total)
    ].copy()
    
    logger.info(f"Filtered dataset from {len(features_df)} to {len(filtered_df)} rows (Min RS Total FGA: {min_rs_fga_total}, Min PO Total FGA: {min_po_fga_total})")
    
    output_path = Path("results/physicality_features.csv")
    output_path.parent.mkdir(exist_ok=True)
    
    filtered_df.to_csv(output_path, index=False)
    logger.info(f"✅ Saved physicality features to {output_path}")
    
    # Top 5 Resilient
    print("\nTop 5 FTr Resilience:")
    print(filtered_df.sort_values('FTr_RESILIENCE', ascending=False)[['PLAYER_NAME', 'SEASON', 'FTr_RESILIENCE', 'RS_FTr', 'PO_FTr']].head())
    
    # Bottom 5
    print("\nBottom 5 FTr Resilience:")
    print(filtered_df.sort_values('FTr_RESILIENCE', ascending=True)[['PLAYER_NAME', 'SEASON', 'FTr_RESILIENCE', 'RS_FTr', 'PO_FTr']].head())

if __name__ == "__main__":
    main()

