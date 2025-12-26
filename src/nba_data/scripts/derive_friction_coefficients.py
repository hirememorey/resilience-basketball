"""
Derive Friction Coefficients for Universal Projection Engine

This script empirically derives the "friction coefficients" that govern how a 
player's efficiency changes as their usage increases. This is a critical first 
step before building the Universal Avatar simulation engine.

Methodology (First Principles):
1.  The "Law of Friction": All else equal, an increase in usage (more difficult 
    shots, more defensive attention) leads to a decrease in efficiency.
2.  Hypothesis: The magnitude of this efficiency loss is inversely proportional 
    to a player's creation ability. Players who generate high-quality shots 
    for themselves and others should be more resilient to increased volume.
3.  Metric for Creation Ability: SHOT_QUALITY_GENERATION_DELTA.
4.  Procedure:
    a. Load historical player data from 'predictive_dataset.csv'.
    b. For each player, find consecutive seasons (year N and year N+1).
    c. Calculate the change in usage (delta_usg) and the change in efficiency 
       (delta_ts).
    d. Group players by their SHOT_QUALITY_GENERATION_DELTA in year N.
    e. Analyze the relationship between delta_usg and delta_ts for each group. 
       This relationship defines the friction coefficient for that archetype.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[3]))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/derive_friction.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_data() -> pd.DataFrame:
    """Load the predictive dataset."""
    results_dir = Path("results")
    predictive_path = results_dir / "predictive_dataset.csv"
    
    if not predictive_path.exists():
        logger.error(f"Predictive dataset not found: {predictive_path}")
        raise FileNotFoundError
        
    df = pd.read_csv(predictive_path)
    logger.info(f"Loaded {len(df)} records from {predictive_path}")
    return df


def calculate_yoy_deltas(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate year-over-year deltas for usage and efficiency."""
    
    # Ensure data is sorted by player and season
    df = df.sort_values(by=['PLAYER_ID', 'SEASON']).copy()
    
    # Identify key columns
    usage_col = 'USG_PCT'
    efficiency_col = 'TS_PCT'
    sq_delta_col = 'SHOT_QUALITY_GENERATION_DELTA'
    
    # Check if necessary columns exist
    required_cols = [usage_col, efficiency_col, sq_delta_col, 'PLAYER_ID', 'SEASON', 'RS_TOTAL_VOLUME']
    for col in required_cols:
        if col not in df.columns:
            logger.error(f"Required column '{col}' not in DataFrame.")
            raise ValueError(f"Missing required column: {col}")

    # Calculate year-over-year changes
    df['PREV_SEASON'] = df.groupby('PLAYER_ID')['SEASON'].shift(1)
    df['PREV_USG_PCT'] = df.groupby('PLAYER_ID')[usage_col].shift(1)
    df['PREV_TS_PCT'] = df.groupby('PLAYER_ID')[efficiency_col].shift(1)
    df['PREV_SQ_DELTA'] = df.groupby('PLAYER_ID')[sq_delta_col].shift(1)
    df['PREV_VOLUME'] = df.groupby('PLAYER_ID')['RS_TOTAL_VOLUME'].shift(1)
    
    # Drop rows without a previous season to compare to
    deltas_df = df.dropna(
        subset=['PREV_SEASON', 'PREV_USG_PCT', 'PREV_TS_PCT', 'PREV_SQ_DELTA', 'PREV_VOLUME']
    ).copy()
    
    # Filter for significant playing time in both seasons
    min_volume = 500 # Corresponds roughly to 500 possessions, a reasonable threshold for a role player
    deltas_df = deltas_df[
        (deltas_df['RS_TOTAL_VOLUME'] >= min_volume) &
        (deltas_df['PREV_VOLUME'] >= min_volume)
    ]

    # Calculate deltas
    deltas_df['DELTA_USG'] = deltas_df[usage_col] - deltas_df['PREV_USG_PCT']
    deltas_df['DELTA_TS'] = deltas_df[efficiency_col] - deltas_df['PREV_TS_PCT']
    
    logger.info(f"Calculated deltas for {len(deltas_df)} player-seasons with >{min_volume} volume in consecutive years.")
    
    return deltas_df


def analyze_friction_by_archetype(deltas_df: pd.DataFrame):
    """Analyze the relationship between usage and efficiency changes by SQ_DELTA."""
    
    # Filter out rows with missing SQ_DELTA
    analysis_df = deltas_df.dropna(subset=['PREV_SQ_DELTA']).copy()

    # Define archetypes based on previous season's SHOT_QUALITY_GENERATION_DELTA
    quantiles = analysis_df['PREV_SQ_DELTA'].quantile([0.1, 0.9]).to_dict()
    low_sq_threshold = quantiles[0.1]
    high_sq_threshold = quantiles[0.9]

    logger.info(f"SQ_DELTA Quantiles: Low (10th %ile) = {low_sq_threshold:.4f}, High (90th %ile) = {high_sq_threshold:.4f}")

    analysis_df['ARCHETYPE'] = np.select(
        [
            analysis_df['PREV_SQ_DELTA'] >= high_sq_threshold,
            analysis_df['PREV_SQ_DELTA'] <= low_sq_threshold
        ],
        [
            'High SQ Delta (Creators)',
            'Low SQ Delta (Finishers)'
        ],
        default='Mid SQ Delta'
    )
    
    # Focus on players with significant usage increase
    usage_increase_df = analysis_df[analysis_df['DELTA_USG'] > 0.02].copy()
    logger.info(f"Analyzing {len(usage_increase_df)} instances of significant usage increase (>2%).")
    
    # Calculate average friction for each archetype
    friction_results = usage_increase_df.groupby('ARCHETYPE').agg(
        avg_delta_usg=('DELTA_USG', 'mean'),
        avg_delta_ts=('DELTA_TS', 'mean'),
        sample_size=('PLAYER_ID', 'count')
    ).reset_index()
    
    # Friction Coefficient = Average change in TS% per 1% increase in USG%
    friction_results['FRICTION_COEFFICIENT'] = (friction_results['avg_delta_ts'] / (friction_results['avg_delta_usg'] * 100))
    
    logger.info("\n" + "="*80)
    logger.info("EMPIRICAL FRICTION COEFFICIENT RESULTS")
    logger.info("="*80)
    logger.info("Analyzes players who increased usage by >2% year-over-year.")
    logger.info("Friction Coefficient = Change in True Shooting % for each 1% increase in Usage %.")
    logger.info("\n" + friction_results.to_string(index=False))
    
    # Save results
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    output_path = results_dir / "friction_coefficient_analysis.csv"
    friction_results.to_csv(output_path, index=False)
    logger.info(f"\nAnalysis saved to {output_path}")


def main():
    """Main execution function."""
    try:
        logger.info("Starting Friction Coefficient Derivation...")
        player_data = load_data()
        deltas_df = calculate_yoy_deltas(player_data)
        analyze_friction_by_archetype(deltas_df)
        logger.info("Friction coefficient derivation complete.")
        
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

