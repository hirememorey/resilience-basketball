"""
Create Revision 3 Features: Conceptually Pure, Real Data Only

Based on first-principles analysis, previous features failed because:
1. Imputed TS% was redundant (linear combination of existing features)
2. OFF_BALL_SCORING_ADVANTAGE mixed opposing concepts

Revision 3 uses only 100% coverage real data with single clean concepts:

1. TRUE_EFG_VS_EXPECTED = EFG_ISO_WEIGHTED - LEAGUE_AVG_EFG_AT_USAGE_BAND
   - Measures: Efficiency relative to usage-based peers
   - Pure concept: "How efficient are you for your role?"

2. SYSTEM_EFFICIENCY_SCORE = EFG_ISO_WEIGHTED × ASSISTED_FGM_PCT
   - Measures: How much of your efficiency comes from system assistance
   - Pure concept: "System-enabled scoring efficiency"

Usage: python create_revision3_features.py
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
        logging.FileHandler("logs/revision3_features.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class Revision3FeatureCreator:
    """Create conceptually pure features using real data only."""

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
        """Calculate league averages for EFG by usage band."""
        logger.info("Calculating league averages for EFG by usage band...")

        # Create usage bands
        usage_bins = [0, 15, 20, 25, 30, 35, 100]
        usage_labels = ['0-15%', '15-20%', '20-25%', '25-30%', '30-35%', '35%+']

        # Calculate league average EFG_ISO_WEIGHTED by season and usage band
        self.df['USAGE_BAND'] = pd.cut(self.df['USG_PCT'], bins=usage_bins, labels=usage_labels, right=False)

        league_avg_efg = self.df.groupby(['SEASON', 'USAGE_BAND'])['EFG_ISO_WEIGHTED'].mean().reset_index()
        league_avg_efg = league_avg_efg.rename(columns={'EFG_ISO_WEIGHTED': 'LEAGUE_AVG_EFG_AT_USAGE'})

        self.league_avg_efg = league_avg_efg
        logger.info(f"Calculated league averages for {len(league_avg_efg)} season-band combinations")

        # Show some stats
        logger.info("Sample league averages by usage band:")
        sample = league_avg_efg.head(10)
        for _, row in sample.iterrows():
            logger.info(".3f")

    def create_revision3_features(self):
        """Create the two Revision 3 features."""
        logger.info("Creating Revision 3 features...")

        df = self.df.copy()

        # Merge league averages
        df = pd.merge(df, self.league_avg_efg, on=['SEASON', 'USAGE_BAND'], how='left')

        # Feature 1: TRUE_EFG_VS_EXPECTED
        # EFG_ISO_WEIGHTED - LEAGUE_AVG_EFG_AT_USAGE
        df['TRUE_EFG_VS_EXPECTED'] = df['EFG_ISO_WEIGHTED'] - df['LEAGUE_AVG_EFG_AT_USAGE']

        # Feature 2: SYSTEM_EFFICIENCY_SCORE
        # EFG_ISO_WEIGHTED × ASSISTED_FGM_PCT
        df['SYSTEM_EFFICIENCY_SCORE'] = df['EFG_ISO_WEIGHTED'] * df['ASSISTED_FGM_PCT']

        # Log feature statistics
        logger.info("TRUE_EFG_VS_EXPECTED statistics:")
        logger.info(".4f")
        logger.info(".4f")
        logger.info(".4f")
        logger.info(".4f")
        logger.info(f"  Valid values: {df['TRUE_EFG_VS_EXPECTED'].notna().sum()}")

        logger.info("SYSTEM_EFFICIENCY_SCORE statistics:")
        logger.info(".4f")
        logger.info(".4f")
        logger.info(".4f")
        logger.info(".4f")
        logger.info(f"  Valid values: {df['SYSTEM_EFFICIENCY_SCORE'].notna().sum()}")

        # Quality checks - look at players with extreme values
        logger.info("\nTop 5 players by TRUE_EFG_VS_EXPECTED (efficient for usage):")
        top_eff = df.nlargest(5, 'TRUE_EFG_VS_EXPECTED')[['PLAYER_NAME', 'SEASON', 'TRUE_EFG_VS_EXPECTED', 'EFG_ISO_WEIGHTED', 'USG_PCT', 'USAGE_BAND']]
        for _, player in top_eff.iterrows():
            logger.info(".4f")

        logger.info("\nTop 5 players by SYSTEM_EFFICIENCY_SCORE (system-enabled efficiency):")
        top_system = df.nlargest(5, 'SYSTEM_EFFICIENCY_SCORE')[['PLAYER_NAME', 'SEASON', 'SYSTEM_EFFICIENCY_SCORE', 'EFG_ISO_WEIGHTED', 'ASSISTED_FGM_PCT']]
        for _, player in top_system.iterrows():
            logger.info(".4f")

        logger.info("\nBottom 5 players by TRUE_EFG_VS_EXPECTED (inefficient for usage):")
        bottom_eff = df.nsmallest(5, 'TRUE_EFG_VS_EXPECTED')[['PLAYER_NAME', 'SEASON', 'TRUE_EFG_VS_EXPECTED', 'EFG_ISO_WEIGHTED', 'USG_PCT', 'USAGE_BAND']]
        for _, player in bottom_eff.iterrows():
            logger.info(".4f")

        self.df_updated = df

    def update_predictive_dataset(self):
        """Update the predictive dataset with Revision 3 features."""
        logger.info("Updating predictive dataset with Revision 3 features...")

        # Save updated dataset
        output_path = self.results_dir / "predictive_dataset.csv"
        self.df_updated.to_csv(output_path, index=False)
        logger.info(f"Updated predictive dataset saved to {output_path}")

        # Also save analysis version
        analysis_path = self.results_dir / "predictive_dataset_with_revision3.csv"
        self.df_updated.to_csv(analysis_path, index=False)
        logger.info(f"Analysis version saved to {analysis_path}")

    def run(self):
        """Run the complete Revision 3 feature creation pipeline."""
        logger.info("Starting Revision 3 feature creation...")

        self.load_data()
        self.calculate_league_averages()
        self.create_revision3_features()
        self.update_predictive_dataset()

        logger.info("✅ Revision 3 features created successfully!")
        logger.info("Features: TRUE_EFG_VS_EXPECTED, SYSTEM_EFFICIENCY_SCORE")


def main():
    try:
        creator = Revision3FeatureCreator()
        creator.run()
    except Exception as e:
        logger.error(f"Error creating Revision 3 features: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()