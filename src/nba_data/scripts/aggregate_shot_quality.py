#!/usr/bin/env python3
"""
Aggregate Shot Quality Data

Transform raw shot quality data by defense distance range into aggregated format
expected by calculate_shot_quality_generation.py.

Input: data/shot_quality/shot_quality_{season}.csv (raw by distance range)
Output: data/shot_quality_aggregates_{season}.csv (aggregated by player)
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def aggregate_season_shot_quality(season: str) -> Optional[pd.DataFrame]:
    """
    Aggregate shot quality data for a season from raw format to expected format.
    """
    input_path = Path("data/shot_quality") / f"shot_quality_{season}.csv"
    output_path = Path("data") / f"shot_quality_aggregates_{season}.csv"

    if not input_path.exists():
        logger.warning(f"Input file not found: {input_path}")
        return None

    logger.info(f"Loading raw shot quality data for {season}...")
    df = pd.read_csv(input_path)
    logger.info(f"Loaded {len(df)} raw records")

    # Filter to regular season only (exclude playoffs for now)
    rs_df = df[df['SEASON_TYPE'].isin(['RS', 'Regular Season'])].copy()
    logger.info(f"Filtered to {len(rs_df)} regular season records")

    if rs_df.empty:
        logger.warning(f"No regular season data for {season}")
        return None

    # Map shot quality ranges to expected column names
    range_mapping = {
        'VeryTight': '0_2',    # 0-2 feet
        'Tight': '2_4',        # 2-4 feet
        'Open': '4_6',         # 4-6 feet
        'WideOpen': '6_PLUS'   # 6+ feet
    }

    # Pivot the data: one row per player with columns for each distance range
    aggregated_data = []

    # Group by player
    for (player_id, season_type), player_group in rs_df.groupby(['PLAYER_ID', 'SEASON_TYPE']):
        player_data = {
            'PLAYER_ID': player_id,
            'PLAYER_NAME': player_group['PLAYER_NAME'].iloc[0],
            'SEASON': season,
            'SEASON_TYPE': season_type,
            'AGE': player_group['AGE'].iloc[0],
            'GP': player_group['GP'].iloc[0],
            'G': player_group['G'].iloc[0]
        }

        # Initialize columns for each distance range
        for range_name in range_mapping.values():
            player_data[f'EFG_{range_name}'] = None
            player_data[f'FGA_{range_name}'] = 0
            player_data[f'FGM_{range_name}'] = 0

        # Fill in data for each shot quality range
        for _, row in player_group.iterrows():
            shot_quality = row['SHOT_QUALITY']
            if shot_quality in range_mapping:
                range_key = range_mapping[shot_quality]
                player_data[f'EFG_{range_key}'] = row['EFG_PCT']
                player_data[f'FGA_{range_key}'] = row['FGA']
                player_data[f'FGM_{range_key}'] = row['FGM']

        aggregated_data.append(player_data)

    # Create aggregated dataframe
    agg_df = pd.DataFrame(aggregated_data)

    # Calculate total FGA and overall EFG for validation
    range_cols = list(range_mapping.values())
    agg_df['TOTAL_FGA'] = agg_df[[f'FGA_{col}' for col in range_cols]].sum(axis=1)
    agg_df['TOTAL_FGM'] = agg_df[[f'FGM_{col}' for col in range_cols]].sum(axis=1)

    # Calculate overall weighted EFG
    def calculate_weighted_efg(row):
        total_weighted = 0
        total_fga = 0
        for col in range_cols:
            efg = row.get(f'EFG_{col}')
            fga = row.get(f'FGA_{col}', 0)
            if pd.notna(efg) and fga > 0:
                total_weighted += efg * fga
                total_fga += fga
        return total_weighted / total_fga if total_fga > 0 else None

    agg_df['OVERALL_EFG'] = agg_df.apply(calculate_weighted_efg, axis=1)

    # Filter to players with meaningful volume
    agg_df = agg_df[agg_df['TOTAL_FGA'] >= 50].copy()
    logger.info(f"Filtered to {len(agg_df)} players with >=50 FGA")

    # Save aggregated data
    agg_df.to_csv(output_path, index=False)
    logger.info(f"Saved aggregated data to {output_path}")

    # Log some statistics
    logger.info(f"EFG ranges: {agg_df['OVERALL_EFG'].min():.3f} - {agg_df['OVERALL_EFG'].max():.3f}")
    logger.info(f"Top players by volume: {agg_df.nlargest(5, 'TOTAL_FGA')[['PLAYER_NAME', 'TOTAL_FGA', 'OVERALL_EFG']].to_string(index=False)}")

    return agg_df

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Aggregate Shot Quality Data")
    parser.add_argument(
        '--seasons',
        nargs='+',
        default=['2015-16', '2016-17', '2017-18', '2018-19', '2019-20',
                 '2020-21', '2021-22', '2022-23', '2023-24', '2024-25'],
        help='Seasons to aggregate'
    )

    args = parser.parse_args()

    for season in args.seasons:
        logger.info(f"\n{'='*60}")
        logger.info(f"Aggregating shot quality for {season}")
        logger.info(f"{'='*60}")

        result = aggregate_season_shot_quality(season)
        if result is None:
            logger.error(f"Failed to aggregate {season}")

    logger.info("\n✅ Shot quality aggregation complete!")

if __name__ == "__main__":
    main()