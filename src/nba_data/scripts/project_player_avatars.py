"""
Universal Projection Engine (Avatar Generator).

This script implements the "Projector" phase of the Telescope pipeline.
It transforms current player features into "Star Load Avatars" (projected to 28% Usage).

Logic:
1. Calculates percentile rank of player within their current usage bucket.
2. Projects player to target usage bucket, preserving their PERCENTILE RANK.
   (Previous logic used absolute offset, which broke physics for low-volume players like Gobert).
3. Re-calculates interaction terms based on projected values.

Output:
    data/projected_telescope_dataset.csv: The training data for the Telescope Model.
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Constants
STAR_USAGE_TARGET = 0.28
USAGE_BIN_SIZE = 0.05
SCALABLE_FEATURES = [
    'CREATION_VOLUME_RATIO',
    'LEVERAGE_USG_DELTA',
    'RS_PRESSURE_APPETITE',  # If present
    'RS_RIM_APPETITE'        # If present
]

def load_data():
    """Load the Crucible dataset (RS features)."""
    path = Path("data/crucible_dataset_full.csv")
    if not path.exists():
        path = Path("data/training_dataset.csv")
    
    if not path.exists():
        logger.error("No input dataset found.")
        sys.exit(1)
        
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} records from {path.name}")

    # Normalize USG_PCT
    if 'USG_PCT' in df.columns and df['USG_PCT'].notna().any() and df['USG_PCT'].mean() > 1.0:
        logger.info("Detected USG_PCT as 0-100 scale. Converting to 0-1.")
        df['USG_PCT'] = df['USG_PCT'] / 100.0
    
    if 'USG_PCT' not in df.columns and 'usg_pct_vs_top10' in df.columns:
        logger.info("Found 'usg_pct_vs_top10' instead of 'USG_PCT'. Using it as the primary usage column.")
        df.rename(columns={'usg_pct_vs_top10': 'USG_PCT'}, inplace=True)
    
    return df

def get_bucket_percentiles(df: pd.DataFrame, feature: str) -> dict:
    """
    Calculate full percentile distributions for each usage bin.
    Returns: {bin_midpoint: Series_of_values}
    """
    distribution = {}
    
    # Create bins
    df['USG_BIN'] = (df['USG_PCT'] // USAGE_BIN_SIZE) * USAGE_BIN_SIZE
    
    grouped = df.groupby('USG_BIN')
    for bin_val, group in grouped:
        if feature in group.columns:
            distribution[bin_val] = group[feature].sort_values().values
            
    return distribution

def project_value_by_percentile(value: float, source_dist: np.array, target_dist: np.array) -> float:
    """
    Project a value from source distribution to target distribution preserving percentile rank.
    """
    if len(source_dist) < 5 or len(target_dist) < 5:
        # Not enough data for robust percentile mapping, fallback to identity or simple scaling
        # If target mean > source mean, scale up? No, dangerous. Keep as is.
        return value
        
    # 1. Find percentile of current value in source distribution
    # Using searchsorted to find rank
    rank = np.searchsorted(source_dist, value)
    percentile = rank / len(source_dist)
    
    # 2. Map to value at same percentile in target distribution
    target_idx = int(percentile * len(target_dist))
    target_idx = min(target_idx, len(target_dist) - 1)
    
    return target_dist[target_idx]

def project_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Project features for all players to STAR_USAGE_TARGET using Percentile Preservation.
    """
    df_projected = df.copy()
    
    # Only project players below target usage
    mask_to_project = df['USG_PCT'] < STAR_USAGE_TARGET
    
    # Identify target bin
    target_bin = (STAR_USAGE_TARGET // USAGE_BIN_SIZE) * USAGE_BIN_SIZE
    
    # For each scalable feature
    for feature in SCALABLE_FEATURES:
        if feature not in df.columns:
            continue
            
        logger.info(f"Projecting {feature} via Percentile Preservation...")
        
        # Build distributions
        distributions = get_bucket_percentiles(df, feature)
        
        # Check if target bin exists
        # If STAR_USAGE_TARGET is high (0.28), ensure we have data there.
        # If not, find closest high-usage bin.
        if target_bin not in distributions:
            available_bins = sorted(distributions.keys())
            if not available_bins:
                continue
            # Pick highest available bin to simulate "Star Load"
            effective_target_bin = max(available_bins) 
        else:
            effective_target_bin = target_bin
            
        target_dist = distributions[effective_target_bin]
        
        # Apply projection row by row (slow but correct)
        # Vectorizing this is hard due to varying source distributions
        
        new_values = []
        indices = df[mask_to_project].index
        
        for idx in indices:
            current_usg = df.loc[idx, 'USG_PCT']
            current_val = df.loc[idx, feature]
            
            current_bin = (current_usg // USAGE_BIN_SIZE) * USAGE_BIN_SIZE
            
            if current_bin in distributions:
                source_dist = distributions[current_bin]
                projected_val = project_value_by_percentile(current_val, source_dist, target_dist)
            else:
                # If current bin has no data (unlikely), keep value
                projected_val = current_val
                
            new_values.append(projected_val)
            
        df_projected.loc[mask_to_project, feature] = new_values
        
    # Update Usage
    df_projected.loc[mask_to_project, 'USG_PCT'] = STAR_USAGE_TARGET
    
    return df_projected

def recalculate_interactions(df: pd.DataFrame) -> pd.DataFrame:
    """Recalculate interaction terms involving Usage."""
    interactions = [
        ('USG_PCT_X_CREATION_VOLUME_RATIO', 'USG_PCT', 'CREATION_VOLUME_RATIO'),
        ('USG_PCT_X_LEVERAGE_USG_DELTA', 'USG_PCT', 'LEVERAGE_USG_DELTA'),
        ('USG_PCT_X_RS_PRESSURE_APPETITE', 'USG_PCT', 'RS_PRESSURE_APPETITE'),
        ('USG_PCT_X_EFG_ISO_WEIGHTED', 'USG_PCT', 'EFG_ISO_WEIGHTED'),
        ('USG_PCT_X_RS_LATE_CLOCK_PRESSURE_RESILIENCE', 'USG_PCT', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE')
    ]
    
    for col_name, f1, f2 in interactions:
        if f1 in df.columns and f2 in df.columns:
            df[col_name] = df[f1] * df[f2]
            
    return df

def main():
    df = load_data()
    
    available_scalable = [f for f in SCALABLE_FEATURES if f in df.columns]
    logger.info(f"Scalable features found: {available_scalable}")
    
    # Project with Percentile Preservation
    df_projected = project_features(df)
    
    # Recalculate Interactions
    df_projected = recalculate_interactions(df_projected)
    
    # Save
    output_path = Path("data/projected_telescope_dataset.csv")
    df_projected.to_csv(output_path, index=False)
    logger.info(f"Saved projected avatars to {output_path}")
    
    # Validation Log
    logger.info("Validation:")
    
    cases = ["Jalen Brunson", "Rudy Gobert"]
    for case in cases:
        player_rows = df[df['PLAYER_NAME'].str.contains(case, na=False)]
        if not player_rows.empty:
            proj_rows = df_projected[df_projected['PLAYER_NAME'].str.contains(case, na=False)]
            for idx in player_rows.index:
                name = player_rows.loc[idx, 'PLAYER_NAME']
                season = player_rows.loc[idx, 'SEASON']
                old_usg = player_rows.loc[idx, 'USG_PCT']
                old_vol = player_rows.loc[idx, 'CREATION_VOLUME_RATIO'] if 'CREATION_VOLUME_RATIO' in player_rows.columns else 0
                
                new_usg = proj_rows.loc[idx, 'USG_PCT']
                new_vol = proj_rows.loc[idx, 'CREATION_VOLUME_RATIO'] if 'CREATION_VOLUME_RATIO' in proj_rows.columns else 0
                
                logger.info(f"  {name} ({season}): USG {old_usg:.2f} -> {new_usg:.2f} | VOL {old_vol:.2f} -> {new_vol:.2f}")

if __name__ == "__main__":
    main()
