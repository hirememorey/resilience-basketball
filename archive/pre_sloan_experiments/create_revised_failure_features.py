"""
Create Revised Failure Autopsy Features (Phase 2.1)

Based on first-principles analysis, we identified that the original features
CRAFTY_SCORER_INDEX and INEFFICIENT_VOLUME_MERCHANT were flawed because they
conflated orthogonal concepts.

This script implements the revised features:

1. OFF_BALL_VALUE_OVER_REPLACEMENT: (EFG_PCT_0_DRIBBLE - LEAGUE_AVG_0_DRIBBLE_EFG) * FGA_0_DRIBBLE
   - Pure signal of off-ball shooting value above league average, weighted by volume

2. EFFICIENCY_SCORE_VS_EXPECTED: (PLAYER_TS - LEAGUE_AVG_TS_AT_USAGE_BAND) × USG_PCT
   - Compares player's TS% to league average for their usage level, weighted by usage

Usage: python create_revised_failure_features.py
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/revised_failure_features.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RevisedFailureFeatureGenerator:
    """Create surgically designed features from failure autopsy."""

    def __init__(self):
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self):
        """Load predictive dataset and regular season data."""
        logger.info("Loading predictive dataset...")

        # Load predictive dataset
        predictive_path = self.results_dir / "predictive_dataset.csv"
        if not predictive_path.exists():
            raise FileNotFoundError(f"Predictive dataset not found at {predictive_path}")

        self.df_predictive = pd.read_csv(predictive_path)
        logger.info(f"Loaded {len(self.df_predictive)} player-seasons from predictive dataset")

        # Load regular season data to get TS_PCT and FGA_0_DRIBBLE
        # We need to merge data from multiple seasons
        rs_files = [
            "regular_season_2015-16.csv",
            "regular_season_2016-17.csv",
            "regular_season_2017-18.csv",
            "regular_season_2018-19.csv",
            "regular_season_2019-20.csv",
            "regular_season_2020-21.csv",
            "regular_season_2021-22.csv",
            "regular_season_2022-23.csv",
            "regular_season_2023-24.csv"
        ]

        rs_dfs = []
        for rs_file in rs_files:
            rs_path = self.data_dir / rs_file
            if rs_path.exists():
                df_rs = pd.read_csv(rs_path)
                # Select only needed columns
                df_rs = df_rs[['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'TS_PCT', 'USG_PCT', 'FGA']]
                # Convert season from filename
                season = rs_file.replace('regular_season_', '').replace('.csv', '')
                df_rs['SEASON'] = season
                rs_dfs.append(df_rs)
                logger.info(f"Loaded {len(df_rs)} players from {season}")
            else:
                logger.warning(f"Regular season file not found: {rs_file}")

        if not rs_dfs:
            raise FileNotFoundError("No regular season files found")

        self.df_rs = pd.concat(rs_dfs, ignore_index=True)
        logger.info(f"Combined regular season data: {len(self.df_rs)} total records")

        # Load 0-dribble shot data (FGA_0_DRIBBLE)
        # This comes from shot quality aggregates
        shot_files = [
            "shot_quality_aggregates_2015-16.csv",
            "shot_quality_aggregates_2016-17.csv",
            "shot_quality_aggregates_2017-18.csv",
            "shot_quality_aggregates_2018-19.csv",
            "shot_quality_aggregates_2019-20.csv",
            "shot_quality_aggregates_2020-21.csv",
            "shot_quality_aggregates_2021-22.csv",
            "shot_quality_aggregates_2022-23.csv",
            "shot_quality_aggregates_2023-24.csv"
        ]

        shot_dfs = []
        for shot_file in shot_files:
            shot_path = self.data_dir / shot_file
            if shot_path.exists():
                df_shot = pd.read_csv(shot_path)
                # Convert season from filename
                season = shot_file.replace('shot_quality_aggregates_', '').replace('.csv', '')
                df_shot['SEASON'] = season
                shot_dfs.append(df_shot)
                logger.info(f"Loaded shot data for {season}")
            else:
                logger.warning(f"Shot quality file not found: {shot_file}")

        if shot_dfs:
            self.df_shots = pd.concat(shot_dfs, ignore_index=True)
            logger.info(f"Combined shot quality data: {len(self.df_shots)} total records")
        else:
            logger.warning("No shot quality data found - FGA_0_DRIBBLE will be unavailable")
            self.df_shots = None

    def calculate_league_averages(self):
        """Calculate league averages by usage band for TS% and 0-dribble EFG."""
        logger.info("Calculating league averages by usage band...")

        # Create usage bands (similar to the original approach)
        usage_bins = [0, 15, 20, 25, 30, 35, 100]  # USG_PCT bands
        usage_labels = ['0-15%', '15-20%', '20-25%', '25-30%', '30-35%', '35%+']

        self.df_rs['USAGE_BAND'] = pd.cut(self.df_rs['USG_PCT'] * 100, bins=usage_bins, labels=usage_labels, right=False)

        # Calculate league average TS% by usage band and season
        ts_averages = self.df_rs.groupby(['SEASON', 'USAGE_BAND'])['TS_PCT'].mean().reset_index()
        ts_averages = ts_averages.rename(columns={'TS_PCT': 'LEAGUE_AVG_TS_AT_USAGE'})
        self.ts_averages = ts_averages
        logger.info(f"Calculated TS% averages for {len(ts_averages)} season-band combinations")

        # Calculate league average 0-dribble EFG by season
        if self.df_shots is not None and 'EFG_PCT_0_DRIBBLE' in self.df_shots.columns:
            efg_0dribble_averages = self.df_shots.groupby('SEASON')['EFG_PCT_0_DRIBBLE'].mean().reset_index()
            efg_0dribble_averages = efg_0dribble_averages.rename(columns={'EFG_PCT_0_DRIBBLE': 'LEAGUE_AVG_0_DRIBBLE_EFG'})
            self.efg_0dribble_averages = efg_0dribble_averages
            logger.info(f"Calculated 0-dribble EFG averages for {len(efg_0dribble_averages)} seasons")
        else:
            logger.warning("EFG_PCT_0_DRIBBLE not found in shot data - will use fallback")
            self.efg_0dribble_averages = None

    def merge_additional_data(self):
        """Merge TS_PCT and shot data into predictive dataset."""
        logger.info("Merging additional data into predictive dataset...")

        # Merge TS_PCT and USG_PCT from regular season data
        rs_merge_cols = ['PLAYER_ID', 'SEASON', 'TS_PCT', 'USG_PCT']
        df_merged = pd.merge(
            self.df_predictive,
            self.df_rs[rs_merge_cols],
            on=['PLAYER_ID', 'SEASON'],
            how='left',
            suffixes=('', '_rs')  # Suffix for regular season columns
        )
        logger.info(f"Merged TS_PCT data: {df_merged['TS_PCT'].notna().sum()} players have TS_PCT")

        # Merge 0-dribble shot data if available
        if self.df_shots is not None:
            shot_merge_cols = ['PLAYER_ID', 'SEASON', 'EFG_PCT_0_DRIBBLE', 'FGA_0_DRIBBLE']
            if all(col in self.df_shots.columns for col in shot_merge_cols):
                df_merged = pd.merge(
                    df_merged,
                    self.df_shots[shot_merge_cols],
                    on=['PLAYER_ID', 'SEASON'],
                    how='left'
                )
                logger.info(f"Merged shot data: {df_merged['EFG_PCT_0_DRIBBLE'].notna().sum()} players have 0-dribble EFG")
            else:
                logger.warning("Required shot columns not found")
                df_merged['EFG_PCT_0_DRIBBLE'] = np.nan
                df_merged['FGA_0_DRIBBLE'] = np.nan

        self.df_enhanced = df_merged
        logger.info(f"Enhanced dataset columns: {list(df_merged.columns[:20])}...")
        logger.info(f"TS_PCT columns: {[col for col in df_merged.columns if 'TS_PCT' in col]}")
        logger.info(f"USG_PCT columns: {[col for col in df_merged.columns if 'USG_PCT' in col]}")

    def create_revised_features(self):
        """Create the two revised features."""
        logger.info("Creating revised features...")

        df = self.df_enhanced.copy()

        # Create usage bands for TS% comparison
        # USG_PCT is already in percentage form (0-100), no need to multiply by 100
        logger.info(f"USG_PCT sample: {df['USG_PCT'].head()}")

        usage_bins = [0, 15, 20, 25, 30, 35, 100]
        usage_labels = ['0-15%', '15-20%', '20-25%', '25-30%', '30-35%', '35%+']
        df['USAGE_BAND'] = pd.cut(df['USG_PCT'], bins=usage_bins, labels=usage_labels, right=False)
        logger.info(f"USAGE_BAND created. Null count: {df['USAGE_BAND'].isna().sum()}")
        logger.info(f"USAGE_BAND distribution: {df['USAGE_BAND'].value_counts(dropna=False)}")

        # Merge league averages
        logger.info(f"Before merge: df has {len(df)} rows, ts_averages has {len(self.ts_averages)} rows")
        logger.info(f"USAGE_BAND unique values: {df['USAGE_BAND'].unique() if 'USAGE_BAND' in df.columns else 'Not created yet'}")
        logger.info(f"ts_averages columns: {self.ts_averages.columns.tolist()}")
        logger.info(f"ts_averages sample: {self.ts_averages.head()}")
        df = pd.merge(df, self.ts_averages, on=['SEASON', 'USAGE_BAND'], how='left')
        logger.info(f"After merge columns: {[col for col in df.columns if 'LEAGUE_AVG' in col or 'USAGE' in col]}")
        if 'LEAGUE_AVG_TS_AT_USAGE' in df.columns:
            logger.info(f"After merge: LEAGUE_AVG_TS_AT_USAGE null count: {df['LEAGUE_AVG_TS_AT_USAGE'].isna().sum()}")
        else:
            logger.error("LEAGUE_AVG_TS_AT_USAGE column not found after merge")
            logger.info(f"df columns: {df.columns.tolist()}")
            return

        if self.efg_0dribble_averages is not None:
            df = pd.merge(df, self.efg_0dribble_averages, on='SEASON', how='left')
        else:
            # Fallback: use a reasonable league average
            df['LEAGUE_AVG_0_DRIBBLE_EFG'] = 0.55  # Conservative estimate

        # Feature 1: OFF_BALL_VALUE_OVER_REPLACEMENT
        # (EFG_PCT_0_DRIBBLE - LEAGUE_AVG_0_DRIBBLE_EFG) * FGA_0_DRIBBLE
        df['OFF_BALL_VALUE_OVER_REPLACEMENT'] = (
            (df['EFG_PCT_0_DRIBBLE'] - df['LEAGUE_AVG_0_DRIBBLE_EFG']) *
            df['FGA_0_DRIBBLE'].fillna(0)
        )

        # Feature 2: EFFICIENCY_SCORE_VS_EXPECTED
        # (PLAYER_TS - LEAGUE_AVG_TS_AT_USAGE_BAND) × USG_PCT
        # Use the most recent merge result (with _y suffix)
        df['EFFICIENCY_SCORE_VS_EXPECTED'] = (
            (df['TS_PCT'] - df['LEAGUE_AVG_TS_AT_USAGE_y']) *
            df['USG_PCT']  # Use original USG_PCT from predictive dataset
        )

        # Log feature statistics
        logger.info("OFF_BALL_VALUE_OVER_REPLACEMENT statistics:")
        logger.info(f"  Mean: {df['OFF_BALL_VALUE_OVER_REPLACEMENT'].mean():.4f}")
        logger.info(f"  Std: {df['OFF_BALL_VALUE_OVER_REPLACEMENT'].std():.4f}")
        logger.info(f"  Min: {df['OFF_BALL_VALUE_OVER_REPLACEMENT'].min():.4f}")
        logger.info(f"  Max: {df['OFF_BALL_VALUE_OVER_REPLACEMENT'].max():.4f}")
        logger.info(f"  Valid values: {df['OFF_BALL_VALUE_OVER_REPLACEMENT'].notna().sum()}")

        logger.info("EFFICIENCY_SCORE_VS_EXPECTED statistics:")
        logger.info(f"  Mean: {df['EFFICIENCY_SCORE_VS_EXPECTED'].mean():.4f}")
        logger.info(f"  Std: {df['EFFICIENCY_SCORE_VS_EXPECTED'].std():.4f}")
        logger.info(f"  Min: {df['EFFICIENCY_SCORE_VS_EXPECTED'].min():.4f}")
        logger.info(f"  Max: {df['EFFICIENCY_SCORE_VS_EXPECTED'].max():.4f}")
        logger.info(f"  Valid values: {df['EFFICIENCY_SCORE_VS_EXPECTED'].notna().sum()}")

        self.df_final = df

    def save_enhanced_dataset(self):
        """Save the enhanced dataset with new features."""
        output_path = self.results_dir / "predictive_dataset_revised_features.csv"
        self.df_final.to_csv(output_path, index=False)
        logger.info(f"Saved enhanced dataset with revised features to {output_path}")

        # Also update the main predictive_dataset.csv for downstream scripts
        main_output_path = self.results_dir / "predictive_dataset.csv"
        self.df_final.to_csv(main_output_path, index=False)
        logger.info(f"Updated main predictive dataset at {main_output_path}")

    def run(self):
        """Run the complete feature creation pipeline."""
        logger.info("Starting revised failure feature creation...")

        self.load_data()
        self.calculate_league_averages()
        self.merge_additional_data()
        self.create_revised_features()
        self.save_enhanced_dataset()

        logger.info("✅ Revised failure features created successfully!")
        logger.info(f"Added features: OFF_BALL_VALUE_OVER_REPLACEMENT, EFFICIENCY_SCORE_VS_EXPECTED")


def main():
    try:
        generator = RevisedFailureFeatureGenerator()
        generator.run()
    except Exception as e:
        logger.error(f"Error creating revised features: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()