
import pandas as pd
import numpy as np
import logging
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_all_shot_quality_data():
    """Load and combine all shot quality aggregate files."""
    data_dir = Path("data")
    all_files = list(data_dir.glob("shot_quality_aggregates_*.csv"))
    
    if not all_files:
        logger.error("No shot quality aggregate files found!")
        return pd.DataFrame()
        
    dfs = []
    for f in all_files:
        df = pd.read_csv(f)
        dfs.append(df)
        
    return pd.concat(dfs, ignore_index=True)

def load_all_shot_quality_clock_data():
    """Load and combine all shot quality clock files."""
    data_dir = Path("data")
    all_files = list(data_dir.glob("shot_quality_clock_*.csv"))
    
    if not all_files:
        logger.warning("No shot quality clock files found!")
        return pd.DataFrame()
        
    dfs = []
    for f in all_files:
        df = pd.read_csv(f)
        dfs.append(df)
        
    return pd.concat(dfs, ignore_index=True)

def calculate_clock_features(df_clock):
    """Calculate Late vs Early Clock Pressure features."""
    if df_clock.empty:
        return pd.DataFrame()
    
    # Ensure numeric columns
    clock_cols = [
        'FGA_0_2_LATE', 'FGA_0_2_EARLY', 'FGA_2_4_LATE', 'FGA_2_4_EARLY',
        'EFG_0_2_LATE', 'EFG_0_2_EARLY', 'EFG_2_4_LATE', 'EFG_2_4_EARLY',
        'GP'
    ]
    
    for col in clock_cols:
        if col in df_clock.columns:
            df_clock[col] = pd.to_numeric(df_clock[col], errors='coerce').fillna(0)
    
    # Calculate total tight FGA (0-2 + 2-4) for late and early clock
    df_clock['TIGHT_FGA_LATE'] = df_clock['FGA_0_2_LATE'] + df_clock['FGA_2_4_LATE']
    df_clock['TIGHT_FGA_EARLY'] = df_clock['FGA_0_2_EARLY'] + df_clock['FGA_2_4_EARLY']
    df_clock['TIGHT_FGA_TOTAL'] = df_clock['TIGHT_FGA_LATE'] + df_clock['TIGHT_FGA_EARLY']
    
    # Late Clock Pressure Appetite: % of tight shots taken in late clock
    df_clock['LATE_CLOCK_PRESSURE_APPETITE'] = np.where(
        df_clock['TIGHT_FGA_TOTAL'] > 0,
        df_clock['TIGHT_FGA_LATE'] / df_clock['TIGHT_FGA_TOTAL'],
        0
    )
    
    # Early Clock Pressure Appetite: % of tight shots taken in early clock
    df_clock['EARLY_CLOCK_PRESSURE_APPETITE'] = np.where(
        df_clock['TIGHT_FGA_TOTAL'] > 0,
        df_clock['TIGHT_FGA_EARLY'] / df_clock['TIGHT_FGA_TOTAL'],
        0
    )
    
    # Late Clock Pressure Resilience: Weighted eFG% on tight shots in late clock
    df_clock['LATE_CLOCK_PRESSURE_RESILIENCE'] = np.where(
        df_clock['TIGHT_FGA_LATE'] > 0,
        ((df_clock['EFG_0_2_LATE'] * df_clock['FGA_0_2_LATE']) + 
         (df_clock['EFG_2_4_LATE'] * df_clock['FGA_2_4_LATE'])) / df_clock['TIGHT_FGA_LATE'],
        0
    )
    
    # Early Clock Pressure Resilience: Weighted eFG% on tight shots in early clock
    df_clock['EARLY_CLOCK_PRESSURE_RESILIENCE'] = np.where(
        df_clock['TIGHT_FGA_EARLY'] > 0,
        ((df_clock['EFG_0_2_EARLY'] * df_clock['FGA_0_2_EARLY']) + 
         (df_clock['EFG_2_4_EARLY'] * df_clock['FGA_2_4_EARLY'])) / df_clock['TIGHT_FGA_EARLY'],
        0
    )
    
    return df_clock

def calculate_features(df):
    """Calculate Pressure Appetite and Resilience features."""
    # Ensure we have numeric columns
    numeric_cols = [
        'FGA_0_2', 'FGA_2_4', 'FGA_4_6', 'FGA_6_PLUS',
        'EFG_0_2', 'EFG_2_4', 'EFG_4_6', 'EFG_6_PLUS',
        'GP'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # Total FGA captured in this tracking data (Per Game)
    df['TOTAL_TRACKED_FGA_PER_GAME'] = df['FGA_0_2'] + df['FGA_2_4'] + df['FGA_4_6'] + df['FGA_6_PLUS']
    
    # Total Volume (Total Shots over Season/Series)
    df['TOTAL_VOLUME'] = df['TOTAL_TRACKED_FGA_PER_GAME'] * df['GP']
    
    # Avoid division by zero
    df = df[df['TOTAL_TRACKED_FGA_PER_GAME'] > 0].copy()
    
    # 1. PRESSURE APPETITE: % of shots taken with defender < 4 feet
    df['PRESSURE_APPETITE'] = (df['FGA_0_2'] + df['FGA_2_4']) / df['TOTAL_TRACKED_FGA_PER_GAME']
    
    # 2. PRESSURE RESILIENCE: eFG% on shots with defender < 2 feet (Very Tight)
    # We focus on the most extreme pressure.
    df['PRESSURE_RESILIENCE'] = df['EFG_0_2']
    
    # Also calculate "Tight" resilience (0-4 feet) for robustness
    total_tight_fga = df['FGA_0_2'] + df['FGA_2_4']
    # Weighted average eFG
    weighted_tight_efg = ((df['EFG_0_2'] * df['FGA_0_2']) + (df['EFG_2_4'] * df['FGA_2_4'])) / total_tight_fga
    df['PRESSURE_RESILIENCE_BROAD'] = weighted_tight_efg.fillna(0)
    
    return df

def pivot_and_calculate_deltas(df, df_clock=None):
    """Pivot RS and PO data and calculate deltas."""
    # We need to pivot so we have one row per player-season
    
    # Separate RS and PO
    rs_df = df[df['SEASON_TYPE'] == 'RS'].copy()
    po_df = df[df['SEASON_TYPE'] == 'PO'].copy()
    
    # Add prefixes
    feature_cols = ['PRESSURE_APPETITE', 'PRESSURE_RESILIENCE', 'PRESSURE_RESILIENCE_BROAD', 'TOTAL_VOLUME', 'GP']
    
    rs_df = rs_df[['PLAYER_ID', 'PLAYER_NAME', 'SEASON'] + feature_cols]
    po_df = po_df[['PLAYER_ID', 'PLAYER_NAME', 'SEASON'] + feature_cols]
    
    rs_df = rs_df.rename(columns={c: f'RS_{c}' for c in feature_cols})
    po_df = po_df.rename(columns={c: f'PO_{c}' for c in feature_cols})
    
    # Merge
    merged = pd.merge(rs_df, po_df, on=['PLAYER_ID', 'PLAYER_NAME', 'SEASON'], how='inner')
    logger.info(f"Merged RS and PO data: {len(merged)} rows")
    
    # Calculate Deltas
    merged['PRESSURE_APPETITE_DELTA'] = merged['PO_PRESSURE_APPETITE'] - merged['RS_PRESSURE_APPETITE']
    merged['PRESSURE_RESILIENCE_DELTA'] = merged['PO_PRESSURE_RESILIENCE'] - merged['RS_PRESSURE_RESILIENCE']
    
    # Add clock features if available
    if df_clock is not None and not df_clock.empty:
        # Separate RS and PO for clock data
        rs_clock = df_clock[df_clock['SEASON_TYPE'] == 'RS'].copy()
        po_clock = df_clock[df_clock['SEASON_TYPE'] == 'PO'].copy()
        
        clock_feature_cols = [
            'LATE_CLOCK_PRESSURE_APPETITE', 'EARLY_CLOCK_PRESSURE_APPETITE',
            'LATE_CLOCK_PRESSURE_RESILIENCE', 'EARLY_CLOCK_PRESSURE_RESILIENCE'
        ]
        
        if not rs_clock.empty:
            rs_clock_subset = rs_clock[['PLAYER_ID', 'PLAYER_NAME', 'SEASON'] + clock_feature_cols]
            rs_clock_subset = rs_clock_subset.rename(columns={c: f'RS_{c}' for c in clock_feature_cols})
            merged = pd.merge(merged, rs_clock_subset, on=['PLAYER_ID', 'PLAYER_NAME', 'SEASON'], how='left')
        
        if not po_clock.empty:
            po_clock_subset = po_clock[['PLAYER_ID', 'PLAYER_NAME', 'SEASON'] + clock_feature_cols]
            po_clock_subset = po_clock_subset.rename(columns={c: f'PO_{c}' for c in clock_feature_cols})
            merged = pd.merge(merged, po_clock_subset, on=['PLAYER_ID', 'PLAYER_NAME', 'SEASON'], how='left')
        
        # Calculate clock deltas
        for feat in clock_feature_cols:
            rs_col = f'RS_{feat}'
            po_col = f'PO_{feat}'
            if rs_col in merged.columns and po_col in merged.columns:
                merged[f'{feat}_DELTA'] = merged[po_col] - merged[rs_col]
        
        logger.info(f"Added clock features: {len([c for c in merged.columns if 'CLOCK' in c])} columns")
    
    return merged

def main():
    logger.info("Loading shot quality data...")
    raw_df = load_all_shot_quality_data()
    
    if raw_df.empty:
        return
        
    logger.info(f"Loaded {len(raw_df)} rows. Calculating features...")
    feat_df = calculate_features(raw_df)
    
    # Load and calculate clock features
    logger.info("Loading shot quality clock data...")
    raw_clock_df = load_all_shot_quality_clock_data()
    clock_feat_df = None
    if not raw_clock_df.empty:
        logger.info(f"Loaded {len(raw_clock_df)} clock rows. Calculating clock features...")
        clock_feat_df = calculate_clock_features(raw_clock_df)
        logger.info(f"Calculated clock features for {len(clock_feat_df)} rows")
    
    logger.info("Pivoting and calculating deltas...")
    final_df = pivot_and_calculate_deltas(feat_df, clock_feat_df)
    
    # Filter for meaningful sample size in playoffs
    # e.g., at least 30 total tracked shots in playoffs
    filtered_df = final_df[final_df['PO_TOTAL_VOLUME'] >= 30].copy()
    logger.info(f"Filtered for PO volume >= 30: {len(filtered_df)} rows (dropped {len(final_df) - len(filtered_df)})")
    
    output_path = Path("results/pressure_features.csv")
    output_path.parent.mkdir(exist_ok=True)
    
    filtered_df.to_csv(output_path, index=False)
    logger.info(f"✅ Saved {len(filtered_df)} player-seasons to {output_path}")
    
    # Print top 5 Pressure Appetite
    print("\nTop 5 Pressure Appetite (RS):")
    print(filtered_df.sort_values('RS_PRESSURE_APPETITE', ascending=False)[['PLAYER_NAME', 'SEASON', 'RS_PRESSURE_APPETITE']].head())

    # Print top 5 Pressure Resilience
    print("\nTop 5 Pressure Resilience (RS):")
    print(filtered_df.sort_values('RS_PRESSURE_RESILIENCE', ascending=False)[['PLAYER_NAME', 'SEASON', 'RS_PRESSURE_RESILIENCE']].head())

if __name__ == "__main__":
    main()
