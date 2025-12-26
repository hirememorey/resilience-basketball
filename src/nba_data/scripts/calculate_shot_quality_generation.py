"""
Calculate Shot Quality Generation Delta Feature

This script implements the "Shot Quality Generation Delta" feature recommended
to replace sample weighting with organic features that explain WHY players fail.

The Feature: SHOT_QUALITY_GENERATION_DELTA
Logic: Does the player generate higher quality shots (for themselves and teammates) 
than the average replacement player would in that exact possession state?

Why: "Empty Calories" players create shots, but they create predictable shots that 
are easily schemed against in a 7-game series. True Kings create high-value shots 
(rim pressure, open corner 3s for others).

Implementation:
1. Self-Created Shot Quality: Compare player's isolation efficiency to league average
2. Assisted Shot Quality: Compare quality of shots player creates for teammates 
   (via catch-and-shoot opportunities) to league average
3. Delta: Actual shot quality generated - Expected shot quality for replacement player
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Optional, Dict
import sys

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[3]))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/shot_quality_generation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_shot_quality_data(season: str) -> Optional[pd.DataFrame]:
    """Load shot quality aggregates for a season and pivot to wide format."""
    data_dir = Path("data/shot_quality")
    file_path = data_dir / f"shot_quality_{season}.csv"
    
    # Fallback to old location
    if not file_path.exists():
        old_path = Path("data") / f"shot_quality_aggregates_{season}.csv"
        if old_path.exists():
            file_path = old_path
        else:
            logger.warning(f"Shot quality data not found for {season}: {file_path}")
            return None
    
    df = pd.read_csv(file_path)
    
    # Check if it's already in wide format (old aggregates file)
    if 'EFG_0_2' in df.columns:
        logger.info(f"Loaded {len(df)} records for {season} (already wide format)")
        return df
        
    # Pivot from long to wide if loaded from new collection script
    if 'SHOT_QUALITY' in df.columns and 'EFG_PCT' in df.columns:
        logger.info(f"Pivoting {len(df)} records from long to wide format...")
        
        # Mapping for column suffixes
        quality_map = {
            "VeryTight": "0_2",
            "Tight": "2_4",
            "Open": "4_6",
            "WideOpen": "6_PLUS"
        }
        
        pivoted_dfs = []
        base_cols = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'SEASON_TYPE']
        
        # Get base player list (unique players)
        # Note: PLAYER_ID alone might not be unique if player played multiple teams? 
        # But aggregate data usually merges. The collection script output raw totals per player.
        # It's safest to distinct on PLAYER_ID and SEASON_TYPE
        players = df[base_cols].drop_duplicates(subset=['PLAYER_ID', 'SEASON_TYPE'])
        
        for q_label, suffix in quality_map.items():
            # Filter for this quality
            subset = df[df['SHOT_QUALITY'] == q_label].copy()
            if subset.empty:
                continue
                
            # Rename columns
            subset = subset.rename(columns={
                'EFG_PCT': f'EFG_{suffix}',
                'FGA': f'FGA_{suffix}'
            })
            
            # Keep only ID and the new value columns
            cols_to_keep = ['PLAYER_ID', 'SEASON_TYPE'] + [f'EFG_{suffix}', f'FGA_{suffix}']
            subset = subset[cols_to_keep]
            
            pivoted_dfs.append(subset)
            
        if not pivoted_dfs:
            return None
            
        # Merge all back to players
        result = players.copy()
        for sub in pivoted_dfs:
            result = pd.merge(result, sub, on=['PLAYER_ID', 'SEASON_TYPE'], how='left')
            
        logger.info(f"Pivoted to {len(result)} wide records")
        return result

    logger.info(f"Loaded {len(df)} records for {season}")
    return df


def load_predictive_features(season: str) -> Optional[pd.DataFrame]:
    """Load predictive features for a season (contains creation metrics)."""
    # Try main predictive dataset first (Source of Truth)
    main_dataset_path = Path("results/predictive_dataset.csv")
    if main_dataset_path.exists():
        df_all = pd.read_csv(main_dataset_path)
        df_season = df_all[df_all['SEASON'] == season].copy()
        if not df_season.empty:
            logger.info(f"Loaded {len(df_season)} predictive feature records for {season} from main dataset")
            return df_season

    data_dir = Path("data")
    file_path = data_dir / f"predictive_features_{season}.csv"
    
    if file_path.exists():
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} predictive feature records for {season} from data dir")
        return df
        
    logger.warning(f"Predictive features not found for {season}")
    return None


def calculate_league_average_shot_quality(
    shot_quality_df: pd.DataFrame,
    predictive_df: Optional[pd.DataFrame] = None,
    season: Optional[str] = None
) -> Dict[str, float]:
    """
    Calculate league average shot quality by context.
    
    Uses EFG_ISO_WEIGHTED from predictive dataset if available (more accurate),
    otherwise falls back to shot quality data.
    
    Contexts:
    - "self_created": Isolation shots (3+ dribbles) - EFG_ISO_WEIGHTED
    - "assisted": Catch-and-shoot shots (0 dribbles) - EFG_PCT_0_DRIBBLE
    - "overall": Overall shot quality
    """
    league_averages = {}
    
    # 1. Self-Created Shot Quality (Isolation)
    # Prefer EFG_ISO_WEIGHTED from predictive dataset (more accurate)
    if predictive_df is not None and season is not None:
        season_predictive = predictive_df[predictive_df['SEASON'] == season].copy()
        if 'EFG_ISO_WEIGHTED' in season_predictive.columns:
            # Filter to players with sufficient isolation volume
            valid_iso = season_predictive[
                (season_predictive['EFG_ISO_WEIGHTED'].notna()) &
                (season_predictive.get('CREATION_VOLUME_RATIO', 0) > 0.1)  # At least 10% creation
            ]
            if len(valid_iso) > 0:
                league_averages['self_created'] = valid_iso['EFG_ISO_WEIGHTED'].mean()
                logger.info(f"League average self-created shot quality (EFG_ISO_WEIGHTED): {league_averages['self_created']:.4f}")
    
    # Fallback: Calculate from shot quality data (tight defense as proxy)
    if 'self_created' not in league_averages:
        rs_df = shot_quality_df[shot_quality_df['SEASON_TYPE'].isin(['RS', 'Regular Season'])].copy()
        if not rs_df.empty:
            tight_defense_cols = ['EFG_0_2', 'EFG_2_4', 'FGA_0_2', 'FGA_2_4']
            if all(col in rs_df.columns for col in tight_defense_cols):
                rs_df['TIGHT_FGA'] = rs_df['FGA_0_2'].fillna(0) + rs_df['FGA_2_4'].fillna(0)
                rs_df['TIGHT_EFG_WEIGHTED'] = np.where(
                    rs_df['TIGHT_FGA'] > 50,  # Minimum volume
                    ((rs_df['EFG_0_2'].fillna(0) * rs_df['FGA_0_2'].fillna(0)) + 
                     (rs_df['EFG_2_4'].fillna(0) * rs_df['FGA_2_4'].fillna(0))) / rs_df['TIGHT_FGA'],
                    np.nan
                )
                valid_tight = rs_df[rs_df['TIGHT_EFG_WEIGHTED'].notna()]
                if len(valid_tight) > 0:
                    league_averages['self_created'] = valid_tight['TIGHT_EFG_WEIGHTED'].mean()
                    logger.info(f"League average self-created shot quality (tight defense fallback): {league_averages['self_created']:.4f}")
    
    # 2. Assisted Shot Quality (Catch-and-Shoot)
    # Prefer EFG_PCT_0_DRIBBLE from predictive dataset
    if predictive_df is not None and season is not None:
        season_predictive = predictive_df[predictive_df['SEASON'] == season].copy()
        if 'EFG_PCT_0_DRIBBLE' in season_predictive.columns:
            valid_catch = season_predictive[season_predictive['EFG_PCT_0_DRIBBLE'].notna()]
            if len(valid_catch) > 0:
                league_averages['assisted'] = valid_catch['EFG_PCT_0_DRIBBLE'].mean()
                logger.info(f"League average assisted shot quality (EFG_PCT_0_DRIBBLE): {league_averages['assisted']:.4f}")
    
    # Fallback: Use wide open shots (6+ feet) as proxy
    if 'assisted' not in league_averages:
        rs_df = shot_quality_df[shot_quality_df['SEASON_TYPE'].isin(['RS', 'Regular Season'])].copy()
        if not rs_df.empty and 'EFG_6_PLUS' in rs_df.columns and 'FGA_6_PLUS' in rs_df.columns:
            valid_open = rs_df[(rs_df['FGA_6_PLUS'].fillna(0) > 50) & rs_df['EFG_6_PLUS'].notna()]
            if len(valid_open) > 0:
                total_fga = valid_open['FGA_6_PLUS'].sum()
                if total_fga > 0:
                    league_averages['assisted'] = (valid_open['EFG_6_PLUS'] * valid_open['FGA_6_PLUS']).sum() / total_fga
                    logger.info(f"League average assisted shot quality (wide open fallback): {league_averages['assisted']:.4f}")
    
    # 3. Overall shot quality (weighted average across all contexts)
    # This is the baseline for "replacement player"
    rs_df = shot_quality_df[shot_quality_df['SEASON_TYPE'].isin(['RS', 'Regular Season'])].copy()
    if not rs_df.empty:
        categories = ['6_PLUS', '4_6', '2_4', '0_2']
        efg_cols = [f'EFG_{cat}' for cat in categories]
        fga_cols = [f'FGA_{cat}' for cat in categories]
        
        if all(col in rs_df.columns for col in efg_cols + fga_cols):
            rs_df['TOTAL_FGA'] = sum(rs_df[f'FGA_{cat}'].fillna(0) for cat in categories)
            rs_df['WEIGHTED_EFG'] = np.nan
            
            for idx in rs_df.index:
                row = rs_df.loc[idx]
                total_fga = row['TOTAL_FGA']
                if total_fga > 10:  # Minimum volume
                    weighted_sum = sum(
                        row[f'EFG_{cat}'] * row[f'FGA_{cat}'] 
                        for cat in categories 
                        if pd.notna(row[f'EFG_{cat}']) and pd.notna(row[f'FGA_{cat}'])
                    )
                    rs_df.loc[idx, 'WEIGHTED_EFG'] = weighted_sum / total_fga
            
            valid_overall = rs_df[rs_df['WEIGHTED_EFG'].notna()]
            if len(valid_overall) > 0:
                league_averages['overall'] = valid_overall['WEIGHTED_EFG'].mean()
                logger.info(f"League average overall shot quality: {league_averages['overall']:.4f}")
    
    return league_averages


def calculate_player_shot_quality_generated(
    player_data: pd.Series,
    shot_quality_data: pd.DataFrame,
    league_averages: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate shot quality generated by player (self + assisted).
    
    Prefers EFG_ISO_WEIGHTED and EFG_PCT_0_DRIBBLE from player_data if available,
    otherwise falls back to shot quality data.
    
    Returns:
    - self_created_quality: Player's isolation shot quality
    - assisted_quality: Quality of shots player creates for teammates
    - overall_quality: Weighted average of self + assisted
    """
    results = {}
    
    # 1. Self-Created Shot Quality
    # Prefer EFG_ISO_WEIGHTED from player_data (more accurate)
    if 'EFG_ISO_WEIGHTED' in player_data.index and pd.notna(player_data['EFG_ISO_WEIGHTED']):
        results['self_created_quality'] = player_data['EFG_ISO_WEIGHTED']
    else:
        # Fallback: Use tight defense from shot quality data
        player_id = player_data.get('PLAYER_ID')
        season = player_data.get('SEASON')
        
        if pd.notna(player_id) and pd.notna(season):
            player_sq = shot_quality_data[
                (shot_quality_data['PLAYER_ID'] == player_id) & 
                (shot_quality_data['SEASON'] == season) &
                (shot_quality_data['SEASON_TYPE'].isin(['RS', 'Regular Season']))
            ]
            
            if not player_sq.empty:
                player_sq = player_sq.iloc[0]
                if all(col in player_sq.index for col in ['EFG_0_2', 'EFG_2_4', 'FGA_0_2', 'FGA_2_4']):
                    tight_fga = (player_sq.get('FGA_0_2', 0) or 0) + (player_sq.get('FGA_2_4', 0) or 0)
                    if tight_fga > 25: # MINIMUM VOLUME THRESHOLD
                        tight_efg = (
                            (player_sq.get('EFG_0_2', 0) or 0) * (player_sq.get('FGA_0_2', 0) or 0) +
                            (player_sq.get('EFG_2_4', 0) or 0) * (player_sq.get('FGA_2_4', 0) or 0)
                        ) / tight_fga
                        results['self_created_quality'] = tight_efg
                    else:
                        results['self_created_quality'] = np.nan
                else:
                    results['self_created_quality'] = np.nan
            else:
                results['self_created_quality'] = np.nan
        else:
            results['self_created_quality'] = np.nan
    
    # 2. Assisted Shot Quality
    # Prefer EFG_PCT_0_DRIBBLE from player_data (catch-and-shoot)
    if 'EFG_PCT_0_DRIBBLE' in player_data.index and pd.notna(player_data['EFG_PCT_0_DRIBBLE']):
        results['assisted_quality'] = player_data['EFG_PCT_0_DRIBBLE']
    else:
        # Fallback: Use wide open shots from shot quality data
        player_id = player_data.get('PLAYER_ID')
        season = player_data.get('SEASON')
        
        if pd.notna(player_id) and pd.notna(season):
            player_sq = shot_quality_data[
                (shot_quality_data['PLAYER_ID'] == player_id) & 
                (shot_quality_data['SEASON'] == season) &
                (shot_quality_data['SEASON_TYPE'].isin(['RS', 'Regular Season']))
            ]
            
            if not player_sq.empty:
                player_sq = player_sq.iloc[0]
                if 'EFG_6_PLUS' in player_sq.index and 'FGA_6_PLUS' in player_sq.index:
                    open_fga = player_sq.get('FGA_6_PLUS', 0) or 0
                    if open_fga > 25: # MINIMUM VOLUME THRESHOLD
                        results['assisted_quality'] = player_sq.get('EFG_6_PLUS', 0) or 0
                    else:
                        results['assisted_quality'] = np.nan
                else:
                    results['assisted_quality'] = np.nan
            else:
                results['assisted_quality'] = np.nan
        else:
            results['assisted_quality'] = np.nan
    
    # 3. Overall Shot Quality (weighted average)
    # Calculate from shot quality data if available
    player_id = player_data.get('PLAYER_ID')
    season = player_data.get('SEASON')
    
    if pd.notna(player_id) and pd.notna(season):
        player_sq = shot_quality_data[
            (shot_quality_data['PLAYER_ID'] == player_id) & 
            (shot_quality_data['SEASON'] == season) &
            (shot_quality_data['SEASON_TYPE'].isin(['RS', 'Regular Season']))
        ]
        
        if not player_sq.empty:
            player_sq = player_sq.iloc[0]
            categories = ['6_PLUS', '4_6', '2_4', '0_2']
            efg_cols = [f'EFG_{cat}' for cat in categories]
            fga_cols = [f'FGA_{cat}' for cat in categories]
            
            if all(col in player_sq.index for col in efg_cols + fga_cols):
                total_fga = sum(player_sq.get(f'FGA_{cat}', 0) or 0 for cat in categories)
                if total_fga > 100:  # Minimum volume
                    weighted_sum = sum(
                        (player_sq.get(f'EFG_{cat}', 0) or 0) * (player_sq.get(f'FGA_{cat}', 0) or 0)
                        for cat in categories
                    )
                    results['overall_quality'] = weighted_sum / total_fga
                else:
                    results['overall_quality'] = np.nan
            else:
                results['overall_quality'] = np.nan
        else:
            results['overall_quality'] = np.nan
    else:
        results['overall_quality'] = np.nan
    
    return results


def calculate_shot_quality_generation_delta(
    player_data: pd.Series,
    shot_quality_data: pd.DataFrame,
    league_averages: Dict[str, float],
    predictive_features: Optional[pd.DataFrame] = None
) -> float:
    """
    Calculate SHOT_QUALITY_GENERATION_DELTA.
    
    Formula: Actual Shot Quality Generated - Expected Shot Quality (Replacement Player)
    
    For now, we use a simplified version:
    - Self-created delta: Player's isolation quality - League average isolation quality
    - Weighted by creation volume ratio
    
    Future enhancement: Include assisted shot quality and playtype context
    """
    player_qualities = calculate_player_shot_quality_generated(
        player_data, shot_quality_data, league_averages
    )
    
    if not player_qualities:
        return np.nan
    
    # Get creation volume ratio (how much of their offense is self-created)
    creation_vol_ratio = player_data.get('CREATION_VOLUME_RATIO', 0.5)  # Default to 50% if missing
    
    if pd.isna(creation_vol_ratio):
        creation_vol_ratio = 0.5
    
    # Calculate delta for self-created shots
    self_created_delta = np.nan
    if 'self_created_quality' in player_qualities and 'self_created' in league_averages:
        player_self_quality = player_qualities['self_created_quality']
        league_self_quality = league_averages['self_created']
        
        if pd.notna(player_self_quality) and pd.notna(league_self_quality):
            self_created_delta = player_self_quality - league_self_quality
    
    # Calculate delta for assisted shots
    assisted_delta = np.nan
    if 'assisted_quality' in player_qualities and 'assisted' in league_averages:
        player_assisted_quality = player_qualities['assisted_quality']
        league_assisted_quality = league_averages['assisted']
        
        if pd.notna(player_assisted_quality) and pd.notna(league_assisted_quality):
            assisted_delta = player_assisted_quality - league_assisted_quality
    
    # Weighted delta: More weight on self-created if player creates more
    # This captures the "Empty Calories" problem: players who create a lot but create low-quality shots
    if pd.notna(self_created_delta) and pd.notna(assisted_delta):
        # Weight by creation volume: high creators' self-created quality matters more
        weighted_delta = (self_created_delta * creation_vol_ratio) + (assisted_delta * (1 - creation_vol_ratio))
    elif pd.notna(self_created_delta):
        # Only self-created available
        weighted_delta = self_created_delta * creation_vol_ratio
    elif pd.notna(assisted_delta):
        # Only assisted available
        weighted_delta = assisted_delta * (1 - creation_vol_ratio)
    else:
        # Fallback: Use overall quality delta
        if 'overall_quality' in player_qualities and 'overall' in league_averages:
            player_overall = player_qualities['overall_quality']
            league_overall = league_averages['overall']
            if pd.notna(player_overall) and pd.notna(league_overall):
                weighted_delta = player_overall - league_overall
            else:
                weighted_delta = np.nan
        else:
            weighted_delta = np.nan
    
    return weighted_delta


def process_season(season: str) -> pd.DataFrame:
    """Process a single season and calculate shot quality generation delta."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing {season}")
    logger.info(f"{'='*60}")
    
    # Load data
    shot_quality_df = load_shot_quality_data(season)
    if shot_quality_df is None or shot_quality_df.empty:
        logger.warning(f"No shot quality data for {season}")
        return pd.DataFrame()
    
    predictive_features_df = load_predictive_features(season)
    
    # Calculate league averages (use predictive dataset for better accuracy)
    logger.info("Calculating league average shot quality...")
    league_averages = calculate_league_average_shot_quality(
        shot_quality_df,
        predictive_features_df,
        season
    )
    
    if not league_averages:
        logger.warning(f"Could not calculate league averages for {season}")
        return pd.DataFrame()
    
    # Load predictive dataset to get player list
    results_dir = Path("results")
    predictive_dataset_path = results_dir / "predictive_dataset.csv"
    
    if not predictive_dataset_path.exists():
        logger.warning(f"Predictive dataset not found: {predictive_dataset_path}")
        return pd.DataFrame()
    
    predictive_df = pd.read_csv(predictive_dataset_path)
    season_df = predictive_df[predictive_df['SEASON'] == season].copy()
    
    if season_df.empty:
        logger.warning(f"No players found for {season} in predictive dataset")
        return pd.DataFrame()
    
    logger.info(f"Calculating shot quality generation delta for {len(season_df)} players...")
    
    # Calculate delta for each player
    deltas = []
    for idx, player_row in season_df.iterrows():
        delta = calculate_shot_quality_generation_delta(
            player_row,
            shot_quality_df,
            league_averages,
            predictive_features_df
        )
        deltas.append(delta)
    
    season_df['SHOT_QUALITY_GENERATION_DELTA'] = deltas
    
    # Select output columns
    output_cols = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'SHOT_QUALITY_GENERATION_DELTA']
    result_df = season_df[output_cols].copy()
    
    # Filter to valid deltas
    result_df = result_df[result_df['SHOT_QUALITY_GENERATION_DELTA'].notna()].copy()
    
    logger.info(f"Calculated delta for {len(result_df)} players")
    logger.info(f"Delta range: {result_df['SHOT_QUALITY_GENERATION_DELTA'].min():.4f} to {result_df['SHOT_QUALITY_GENERATION_DELTA'].max():.4f}")
    logger.info(f"Mean delta: {result_df['SHOT_QUALITY_GENERATION_DELTA'].mean():.4f}")
    
    return result_df


def merge_with_predictive_dataset(delta_df: pd.DataFrame) -> pd.DataFrame:
    """Merge shot quality generation delta with predictive dataset."""
    results_dir = Path("results")
    predictive_path = results_dir / "predictive_dataset.csv"
    
    if not predictive_path.exists():
        logger.warning(f"Predictive dataset not found: {predictive_path}")
        return delta_df
    
    predictive_df = pd.read_csv(predictive_path)
    logger.info(f"Loaded predictive dataset: {len(predictive_df)} records")
    
    # Merge on PLAYER_ID and SEASON
    # If column already exists in predictive_df, drop it first to avoid collision
    if 'SHOT_QUALITY_GENERATION_DELTA' in predictive_df.columns:
        logger.info("SHOT_QUALITY_GENERATION_DELTA already exists in predictive dataset. Overwriting...")
        predictive_df = predictive_df.drop(columns=['SHOT_QUALITY_GENERATION_DELTA'])

    merged_df = pd.merge(
        predictive_df,
        delta_df[['PLAYER_ID', 'SEASON', 'SHOT_QUALITY_GENERATION_DELTA']],
        on=['PLAYER_ID', 'SEASON'],
        how='left'
    )
    
    if 'SHOT_QUALITY_GENERATION_DELTA' in merged_df.columns:
        coverage = merged_df['SHOT_QUALITY_GENERATION_DELTA'].notna().sum()
        logger.info(f"Merged shot quality generation delta: {coverage} / {len(merged_df)} records have delta ({coverage/len(merged_df)*100:.1f}%)")
    else:
        logger.warning("SHOT_QUALITY_GENERATION_DELTA column not found after merge")
    
    # Save updated predictive dataset
    merged_df.to_csv(predictive_path, index=False)
    logger.info(f"Updated predictive dataset saved to {predictive_path}")
    
    return merged_df


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Calculate Shot Quality Generation Delta")
    parser.add_argument(
        '--seasons',
        nargs='+',
        default=['2015-16', '2016-17', '2017-18', '2018-19', '2019-20', 
                 '2020-21', '2021-22', '2022-23', '2023-24', '2024-25'],
        help='Seasons to process'
    )
    parser.add_argument(
        '--merge',
        action='store_true',
        help='Merge with predictive dataset after calculation'
    )
    
    args = parser.parse_args()
    
    # Process all seasons
    all_results = []
    for season in args.seasons:
        result_df = process_season(season)
        if not result_df.empty:
            all_results.append(result_df)
    
    if not all_results:
        logger.error("No results calculated")
        return
    
    combined_df = pd.concat(all_results, ignore_index=True)
    logger.info(f"\nCombined results: {len(combined_df)} player-seasons")
    
    # Save to results directory
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    output_path = results_dir / "shot_quality_generation_delta.csv"
    combined_df.to_csv(output_path, index=False)
    logger.info(f"\nShot quality generation delta saved to {output_path}")
    
    # Merge with predictive dataset if requested
    if args.merge:
        logger.info("\nMerging with predictive dataset...")
        merge_with_predictive_dataset(combined_df)
    
    # Print summary statistics
    logger.info("\n" + "="*60)
    logger.info("SUMMARY STATISTICS")
    logger.info("="*60)
    logger.info(f"Total player-seasons: {len(combined_df)}")
    logger.info(f"Mean delta: {combined_df['SHOT_QUALITY_GENERATION_DELTA'].mean():.4f}")
    logger.info(f"Std delta: {combined_df['SHOT_QUALITY_GENERATION_DELTA'].std():.4f}")
    logger.info(f"Top 10% threshold (>90th percentile): {combined_df['SHOT_QUALITY_GENERATION_DELTA'].quantile(0.90):.4f}")
    logger.info(f"Bottom 10% threshold (<10th percentile): {combined_df['SHOT_QUALITY_GENERATION_DELTA'].quantile(0.10):.4f}")
    
    # Show top and bottom players
    logger.info("\nTop 10 Shot Quality Generators (Highest Delta):")
    top_generators = combined_df.nlargest(10, 'SHOT_QUALITY_GENERATION_DELTA')[
        ['PLAYER_NAME', 'SEASON', 'SHOT_QUALITY_GENERATION_DELTA']
    ]
    logger.info("\n" + top_generators.to_string(index=False))
    
    logger.info("\nBottom 10 Shot Quality Generators (Lowest Delta - 'Empty Calories'):")
    bottom_generators = combined_df.nsmallest(10, 'SHOT_QUALITY_GENERATION_DELTA')[
        ['PLAYER_NAME', 'SEASON', 'SHOT_QUALITY_GENERATION_DELTA']
    ]
    logger.info("\n" + bottom_generators.to_string(index=False))


if __name__ == "__main__":
    main()

