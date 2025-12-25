"""
Build Crucible Dataset (Full).

This script aggregates all seasonal predictive feature files into a single,
comprehensive dataset for running the full Telescope pipeline.

It scans for `predictive_features_*.csv` files in the `data/` directory.

Output:
    data/crucible_dataset_full.csv
"""

import pandas as pd
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def build_full_dataset():
    """
    Synthesize a full dataset by merging regular season stats with 
    engineered predictive features for each season.
    """
    data_dir = Path("data")
    
    # 1. Aggregate Regular Season Data (the base)
    reg_season_files = sorted(list(data_dir.glob("regular_season_*.csv")))
    if not reg_season_files:
        logger.error("No 'regular_season_*.csv' files found.")
        return

    all_reg_dfs = []
    for file in reg_season_files:
        df = pd.read_csv(file)
        if 'SEASON' not in df.columns:
            season_str = file.stem.split('_')[-1]
            df['SEASON'] = season_str
        all_reg_dfs.append(df)
    
    df_base = pd.concat(all_reg_dfs, ignore_index=True)
    logger.info(f"Aggregated {len(df_base)} records from {len(reg_season_files)} regular season files.")

    # 2. Load Physics Features Data (from evaluate_plasticity_potential.py)
    physics_path = Path("results/predictive_dataset_with_friction.csv")
    if not physics_path.exists():
        logger.warning(f"Physics features file not found at {physics_path}. Output will lack physics features.")
        df_features = pd.DataFrame()
    else:
        df_features = pd.read_csv(physics_path)
        logger.info(f"Loaded physics features: {len(df_features)} records with {len(df_features.columns)} columns.")
        # Verify physics features are present
        physics_cols = [c for c in df_features.columns if any(term in c for term in ['CREATION', 'LEVERAGE', 'PRESSURE', 'EFG_ISO', 'DEPENDENCE'])]
        logger.info(f"Physics features detected: {len(physics_cols)} columns")

    # 3. Merge them
    # Ensure keys are the same type for merging
    df_base['PLAYER_ID'] = df_base['PLAYER_ID'].astype(str)
    df_base['SEASON'] = df_base['SEASON'].astype(str)
    
    if not df_features.empty:
        df_features['PLAYER_ID'] = df_features['PLAYER_ID'].astype(str)
        df_features['SEASON'] = df_features['SEASON'].astype(str)
        
        # For the physics features file, we want ALL columns, not just the base ones
        # So we prioritize the physics features over the base ones if there's a conflict
        df_full = pd.merge(df_base, df_features, on=['PLAYER_ID', 'SEASON'], how='left', suffixes=('_base', '_physics'))

        # Drop the base versions of columns that we want the physics versions of
        cols_to_drop = []
        for col in df_full.columns:
            if col.endswith('_base'):
                physics_version = col.replace('_base', '_physics')
                if physics_version in df_full.columns:
                    cols_to_drop.append(col)
                    # Rename the physics version to remove the suffix
                    df_full.rename(columns={physics_version: col.replace('_base', '')}, inplace=True)

        if cols_to_drop:
            df_full.drop(columns=cols_to_drop, inplace=True)

        # Handle remaining _physics suffixes
        physics_cols = [c for c in df_full.columns if c.endswith('_physics')]
        for col in physics_cols:
            clean_name = col.replace('_physics', '')
            df_full.rename(columns={col: clean_name}, inplace=True)

        logger.info(f"Merged dataset size: {len(df_full)}")
        logger.info(f"Physics features preserved: {len([c for c in df_full.columns if 'CREATION' in c or 'LEVERAGE' in c])}")
    else:
        df_full = df_base

    # Handle column name inconsistencies (e.g., usg_pct)
    if 'usg_pct_vs_top10' in df_full.columns and 'USG_PCT' not in df_full.columns:
        df_full.rename(columns={'usg_pct_vs_top10': 'USG_PCT'}, inplace=True)
        logger.info("Renamed 'usg_pct_vs_top10' to 'USG_PCT'.")
    
    # Save to new file
    output_path = data_dir / "crucible_dataset_full.csv"
    df_full.to_csv(output_path, index=False)
    
    logger.info("="*50)
    logger.info(f"Successfully synthesized {len(df_full)} records.")
    logger.info(f"Saved full dataset to {output_path}")
    logger.info(f"Seasons covered: {sorted(df_full['SEASON'].unique())}")
    logger.info("="*50)

if __name__ == "__main__":
    build_full_dataset()
