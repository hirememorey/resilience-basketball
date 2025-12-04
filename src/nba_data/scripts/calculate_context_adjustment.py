"""
Phase 3.5 Fix #3: Calculate Context Adjustment

This script calculates RS_CONTEXT_ADJUSTMENT = ACTUAL_EFG - EXPECTED_EFG
where EXPECTED_EFG is based on shot openness distribution.

The principle: Stats are downstream of Context. A 60% TS% as a #3 option 
facing single coverage is worth less than a 56% TS% as a #1 option facing blitzes.

This metric identifies "System Merchants" - players who outperform expected 
eFG% due to wide-open shots (e.g., Poole benefiting from Curry gravity).
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_shot_quality_data(season: str) -> Optional[pd.DataFrame]:
    """Load shot quality aggregates for a season."""
    data_dir = Path("data")
    file_path = data_dir / f"shot_quality_aggregates_{season}.csv"
    
    if not file_path.exists():
        logger.warning(f"Shot quality data not found for {season}: {file_path}")
        return None
    
    df = pd.read_csv(file_path)
    logger.info(f"Loaded {len(df)} records for {season}")
    return df


def calculate_expected_efg(df: pd.DataFrame) -> pd.Series:
    """
    Calculate expected eFG% based on shot openness distribution.
    
    Formula: Weighted average of eFG% by shot quality category,
    weighted by the frequency of shots in each category.
    
    Expected eFG% = Σ (EFG_category × FREQ_category) for all categories
    """
    # Shot quality categories (from most open to most tight)
    categories = ['6_PLUS', '4_6', '2_4', '0_2']
    
    expected_efg = pd.Series(index=df.index, dtype=float)
    
    for idx in df.index:
        row = df.iloc[idx]
        total_freq = 0.0
        weighted_efg = 0.0
        
        for category in categories:
            freq_col = f'FREQ_{category}'
            efg_col = f'EFG_{category}'
            
            if freq_col in row.index and efg_col in row.index:
                freq = row[freq_col]
                efg = row[efg_col]
                
                if pd.notna(freq) and pd.notna(efg) and freq > 0:
                    total_freq += freq
                    weighted_efg += efg * freq
        
        if total_freq > 0:
            expected_efg[idx] = weighted_efg / total_freq
        else:
            expected_efg[idx] = np.nan
    
    return expected_efg


def calculate_context_adjustment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate RS_CONTEXT_ADJUSTMENT = ACTUAL_EFG - EXPECTED_EFG
    
    Positive values indicate outperforming expected (context-dependent efficiency).
    Negative values indicate underperforming expected (facing tougher defense).
    """
    # Filter to Regular Season only (handle both 'RS' and 'Regular Season' formats)
    rs_df = df[df['SEASON_TYPE'].isin(['RS', 'Regular Season'])].copy()
    
    if rs_df.empty:
        logger.warning("No Regular Season data found")
        return pd.DataFrame()
    
    # Calculate expected eFG% based on shot distribution
    logger.info("Calculating expected eFG% based on shot openness distribution...")
    rs_df['EXPECTED_EFG'] = calculate_expected_efg(rs_df)
    
    # Get actual eFG% - we need to calculate overall eFG% from shot quality data
    # Overall eFG% = weighted average of eFG% by category
    logger.info("Calculating actual eFG% from shot quality data...")
    rs_df['ACTUAL_EFG'] = calculate_actual_efg(rs_df)
    
    # Calculate context adjustment
    rs_df['RS_CONTEXT_ADJUSTMENT'] = rs_df['ACTUAL_EFG'] - rs_df['EXPECTED_EFG']
    
    # Select key columns for output
    output_cols = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'ACTUAL_EFG', 
                   'EXPECTED_EFG', 'RS_CONTEXT_ADJUSTMENT']
    
    result_df = rs_df[output_cols].copy()
    
    logger.info(f"Calculated context adjustment for {len(result_df)} player-seasons")
    logger.info(f"Context adjustment range: {result_df['RS_CONTEXT_ADJUSTMENT'].min():.4f} to {result_df['RS_CONTEXT_ADJUSTMENT'].max():.4f}")
    logger.info(f"Mean context adjustment: {result_df['RS_CONTEXT_ADJUSTMENT'].mean():.4f}")
    
    return result_df


def calculate_actual_efg(df: pd.DataFrame) -> pd.Series:
    """
    Calculate actual eFG% from shot quality data.
    
    This is a weighted average of eFG% by category, weighted by FGA in each category.
    """
    categories = ['6_PLUS', '4_6', '2_4', '0_2']
    
    actual_efg = pd.Series(index=df.index, dtype=float)
    
    for idx in df.index:
        row = df.iloc[idx]
        total_fga = 0.0
        weighted_efg = 0.0
        
        for category in categories:
            fga_col = f'FGA_{category}'
            efg_col = f'EFG_{category}'
            
            if fga_col in row.index and efg_col in row.index:
                fga = row[fga_col]
                efg = row[efg_col]
                
                if pd.notna(fga) and pd.notna(efg) and fga > 0:
                    total_fga += fga
                    weighted_efg += efg * fga
        
        if total_fga > 0:
            actual_efg[idx] = weighted_efg / total_fga
        else:
            actual_efg[idx] = np.nan
    
    return actual_efg


def merge_with_predictive_dataset(context_df: pd.DataFrame) -> pd.DataFrame:
    """Merge context adjustment with predictive dataset."""
    results_dir = Path("results")
    predictive_path = results_dir / "predictive_dataset.csv"
    
    if not predictive_path.exists():
        logger.warning(f"Predictive dataset not found: {predictive_path}")
        return context_df
    
    predictive_df = pd.read_csv(predictive_path)
    logger.info(f"Loaded predictive dataset: {len(predictive_df)} records")
    
    # Merge on PLAYER_ID and SEASON
    merged_df = pd.merge(
        predictive_df,
        context_df[['PLAYER_ID', 'SEASON', 'RS_CONTEXT_ADJUSTMENT']],
        on=['PLAYER_ID', 'SEASON'],
        how='left'
    )
    
    if 'RS_CONTEXT_ADJUSTMENT' in merged_df.columns:
        logger.info(f"Merged context adjustment: {merged_df['RS_CONTEXT_ADJUSTMENT'].notna().sum()} / {len(merged_df)} records have context adjustment")
    else:
        logger.warning("RS_CONTEXT_ADJUSTMENT column not found after merge - check merge keys")
    
    # Save updated predictive dataset
    merged_df.to_csv(predictive_path, index=False)
    logger.info(f"Updated predictive dataset saved to {predictive_path}")
    
    return merged_df


def process_all_seasons(seasons: list) -> pd.DataFrame:
    """Process all seasons and combine results."""
    all_results = []
    
    for season in seasons:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {season}")
        logger.info(f"{'='*60}")
        
        df = load_shot_quality_data(season)
        if df is None or df.empty:
            continue
        
        context_df = calculate_context_adjustment(df)
        if not context_df.empty:
            all_results.append(context_df)
    
    if not all_results:
        logger.error("No results to combine")
        return pd.DataFrame()
    
    combined_df = pd.concat(all_results, ignore_index=True)
    logger.info(f"\nCombined results: {len(combined_df)} player-seasons")
    
    return combined_df


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Calculate RS_CONTEXT_ADJUSTMENT")
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
    context_df = process_all_seasons(args.seasons)
    
    if context_df.empty:
        logger.error("No context adjustment data calculated")
        return
    
    # Save to results directory
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    output_path = results_dir / "context_adjustment.csv"
    context_df.to_csv(output_path, index=False)
    logger.info(f"\nContext adjustment saved to {output_path}")
    
    # Merge with predictive dataset if requested
    if args.merge:
        logger.info("\nMerging with predictive dataset...")
        merge_with_predictive_dataset(context_df)
    
    # Print summary statistics
    logger.info("\n" + "="*60)
    logger.info("SUMMARY STATISTICS")
    logger.info("="*60)
    logger.info(f"Total player-seasons: {len(context_df)}")
    logger.info(f"Mean context adjustment: {context_df['RS_CONTEXT_ADJUSTMENT'].mean():.4f}")
    logger.info(f"Std context adjustment: {context_df['RS_CONTEXT_ADJUSTMENT'].std():.4f}")
    logger.info(f"Top 10% threshold (>90th percentile): {context_df['RS_CONTEXT_ADJUSTMENT'].quantile(0.90):.4f}")
    logger.info(f"Top 15% threshold (>85th percentile): {context_df['RS_CONTEXT_ADJUSTMENT'].quantile(0.85):.4f}")
    
    # Show top system merchants
    logger.info("\nTop 10 System Merchants (Highest Context Adjustment):")
    top_merchants = context_df.nlargest(10, 'RS_CONTEXT_ADJUSTMENT')[
        ['PLAYER_NAME', 'SEASON', 'ACTUAL_EFG', 'EXPECTED_EFG', 'RS_CONTEXT_ADJUSTMENT']
    ]
    logger.info("\n" + top_merchants.to_string(index=False))


if __name__ == "__main__":
    main()

