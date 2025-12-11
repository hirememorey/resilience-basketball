"""
Create Alternative Off-Ball Feature

Since EFG_PCT_0_DRIBBLE and FGA_0_DRIBBLE are not available in our data sources,
this script creates an alternative feature that captures off-ball scoring value using
available data.

Original Concept: OFF_BALL_VALUE_OVER_REPLACEMENT = (EFG_PCT_0_DRIBBLE - LEAGUE_AVG_0_DRIBBLE_EFG) * FGA_0_DRIBBLE

Alternative Approach: Use ASSISTED_FGM_PCT and efficiency measures to estimate off-ball value.

New Feature: OFF_BALL_SCORING_ADVANTAGE = (ASSISTED_FGM_PCT - LEAGUE_AVG_ASSISTED_PCT) * EFG_ISO_WEIGHTED

This captures players who:
1. Get a high percentage of their points from assisted (off-ball) shots
2. Are efficient overall (can convert those opportunities)

Usage: python create_alternative_off_ball_feature.py
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
        logging.FileHandler("logs/alternative_off_ball_feature.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AlternativeOffBallFeatureCreator:
    """Create alternative off-ball scoring feature using available data."""

    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self):
        """Load predictive dataset."""
        logger.info("Loading predictive dataset...")

        dataset_path = self.results_dir / "predictive_dataset.csv"
        if not dataset_path.exists():
            raise FileNotFoundError(f"Predictive dataset not found at {dataset_path}")

        self.df = pd.read_csv(dataset_path)
        logger.info(f"Loaded {len(self.df)} player-seasons")

    def calculate_league_averages(self):
        """Calculate league averages for assisted percentage by season."""
        logger.info("Calculating league averages for assisted percentage...")

        # Calculate league average ASSISTED_FGM_PCT by season
        league_avg_assisted = self.df.groupby('SEASON')['ASSISTED_FGM_PCT'].mean().reset_index()
        league_avg_assisted = league_avg_assisted.rename(columns={'ASSISTED_FGM_PCT': 'LEAGUE_AVG_ASSISTED_PCT'})

        self.league_avg_assisted = league_avg_assisted
        logger.info(f"Calculated league averages for {len(league_avg_assisted)} seasons")

        # Show some stats
        logger.info("League average assisted % by season (sample):")
        sample = league_avg_assisted.head(5)
        for _, row in sample.iterrows():
            logger.info(f"  {row['SEASON']}: {row['LEAGUE_AVG_ASSISTED_PCT']:.3f}")

    def create_alternative_feature(self):
        """Create the alternative off-ball scoring advantage feature."""
        logger.info("Creating alternative off-ball scoring advantage feature...")

        df = self.df.copy()

        # Merge league averages
        df = pd.merge(df, self.league_avg_assisted, on='SEASON', how='left')

        # Calculate OFF_BALL_SCORING_ADVANTAGE
        # = (ASSISTED_FGM_PCT - LEAGUE_AVG_ASSISTED_PCT) * EFG_ISO_WEIGHTED
        df['OFF_BALL_SCORING_ADVANTAGE'] = (
            (df['ASSISTED_FGM_PCT'] - df['LEAGUE_AVG_ASSISTED_PCT']) *
            df['EFG_ISO_WEIGHTED']
        )

        # Alternative version weighted by usage (since catch-and-shoot players might not carry high usage)
        df['OFF_BALL_SCORING_ADVANTAGE_WEIGHTED'] = (
            (df['ASSISTED_FGM_PCT'] - df['LEAGUE_AVG_ASSISTED_PCT']) *
            df['EFG_ISO_WEIGHTED'] *
            (1 + df['USG_PCT'])  # Bonus for moderate usage
        )

        # Log feature statistics
        logger.info("OFF_BALL_SCORING_ADVANTAGE statistics:")
        logger.info(f"  Mean: {df['OFF_BALL_SCORING_ADVANTAGE'].mean():.4f}")
        logger.info(f"  Std: {df['OFF_BALL_SCORING_ADVANTAGE'].std():.4f}")
        logger.info(f"  Min: {df['OFF_BALL_SCORING_ADVANTAGE'].min():.4f}")
        logger.info(f"  Max: {df['OFF_BALL_SCORING_ADVANTAGE'].max():.4f}")
        logger.info(f"  Valid values: {df['OFF_BALL_SCORING_ADVANTAGE'].notna().sum()}")

        logger.info("OFF_BALL_SCORING_ADVANTAGE_WEIGHTED statistics:")
        logger.info(f"  Mean: {df['OFF_BALL_SCORING_ADVANTAGE_WEIGHTED'].mean():.4f}")
        logger.info(f"  Std: {df['OFF_BALL_SCORING_ADVANTAGE_WEIGHTED'].std():.4f}")
        logger.info(f"  Min: {df['OFF_BALL_SCORING_ADVANTAGE_WEIGHTED'].min():.4f}")
        logger.info(f"  Max: {df['OFF_BALL_SCORING_ADVANTAGE_WEIGHTED'].max():.4f}")

        # Quality check: look at players with high off-ball advantage
        logger.info("\nTop 5 players by OFF_BALL_SCORING_ADVANTAGE (sample):")
        top_players = df.nlargest(5, 'OFF_BALL_SCORING_ADVANTAGE')[['PLAYER_NAME', 'SEASON', 'OFF_BALL_SCORING_ADVANTAGE', 'ASSISTED_FGM_PCT', 'EFG_ISO_WEIGHTED']]
        for _, player in top_players.iterrows():
            logger.info(f"  {player['PLAYER_NAME'][:20]:20} {player['SEASON']} {player['OFF_BALL_SCORING_ADVANTAGE']:.4f} (Assisted: {player['ASSISTED_FGM_PCT']:.3f}, EFG: {player['EFG_ISO_WEIGHTED']:.3f})")

        self.df_updated = df

    def update_predictive_dataset(self):
        """Update the predictive dataset with the new off-ball feature."""
        logger.info("Updating predictive dataset with alternative off-ball feature...")

        # Save updated dataset
        output_path = self.results_dir / "predictive_dataset.csv"
        self.df_updated.to_csv(output_path, index=False)
        logger.info(f"Updated predictive dataset saved to {output_path}")

        # Also save analysis version
        analysis_path = self.results_dir / "predictive_dataset_with_off_ball_feature.csv"
        self.df_updated.to_csv(analysis_path, index=False)
        logger.info(f"Analysis version saved to {analysis_path}")

    def run(self):
        """Run the complete alternative off-ball feature creation pipeline."""
        logger.info("Starting alternative off-ball feature creation...")

        self.load_data()
        self.calculate_league_averages()
        self.create_alternative_feature()
        self.update_predictive_dataset()

        logger.info("✅ Alternative off-ball feature created successfully!")


def main():
    try:
        creator = AlternativeOffBallFeatureCreator()
        creator.run()
    except Exception as e:
        logger.error(f"Error creating alternative off-ball feature: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()