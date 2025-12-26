#!/usr/bin/env python3
"""
Combine individual plasticity score files into a single comprehensive dataset.

This script addresses the data pipeline issue where individual season plasticity
files exist but are not combined into the expected plasticity_scores.csv file
that the Streamlit app data loader expects.
"""

import pandas as pd
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def combine_plasticity_scores():
    """Combine all individual plasticity score files into one comprehensive dataset."""

    results_dir = Path("results")
    combined_file = results_dir / "plasticity_scores.csv"

    # Find all plasticity score files
    plasticity_files = list(results_dir.glob("plasticity_scores_*.csv"))
    plasticity_files.sort()  # Sort by season for consistency

    if not plasticity_files:
        logger.error("No individual plasticity score files found")
        return

    logger.info(f"Found {len(plasticity_files)} plasticity score files: {[f.name for f in plasticity_files]}")

    # Combine all files
    combined_data = []

    for file_path in plasticity_files:
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} records from {file_path.name}")

            # Validate required columns exist
            required_cols = ['PLAYER_ID', 'SEASON', 'RESILIENCE_SCORE']
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                logger.warning(f"Missing columns in {file_path.name}: {missing_cols}")
                continue

            # Ensure RESILIENCE_SCORE is not empty
            if df['RESILIENCE_SCORE'].isna().all():
                logger.warning(f"All RESILIENCE_SCORE values are NaN in {file_path.name}")
                continue

            combined_data.append(df)

        except Exception as e:
            logger.error(f"Error loading {file_path.name}: {e}")
            continue

    if not combined_data:
        logger.error("No valid plasticity data found to combine")
        return

    # Concatenate all dataframes
    final_df = pd.concat(combined_data, ignore_index=True)

    # Remove any duplicate records (same player-season)
    original_count = len(final_df)
    final_df = final_df.drop_duplicates(subset=['PLAYER_ID', 'SEASON'], keep='last')
    duplicate_count = original_count - len(final_df)

    if duplicate_count > 0:
        logger.info(f"Removed {duplicate_count} duplicate records")

    # Sort by season and player for consistency
    final_df = final_df.sort_values(['SEASON', 'PLAYER_ID'])

    # Save combined file
    final_df.to_csv(combined_file, index=False)

    logger.info(f"✅ Successfully combined {len(final_df)} plasticity records from {len(plasticity_files)} seasons")
    logger.info(f"Combined file saved to {combined_file}")
    logger.info(f"Sample RESILIENCE_SCORE values: {final_df['RESILIENCE_SCORE'].dropna().head().tolist()}")

if __name__ == "__main__":
    combine_plasticity_scores()
