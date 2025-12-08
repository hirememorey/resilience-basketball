"""
Phase 4: Multi-Season Trajectory Features Generator

This script calculates Year-over-Year (YoY) deltas and previous season priors
for key stress vectors to capture the "alpha" in rate of improvement.

Key Features Generated:
1. YoY Deltas: Change from previous season for key stress vectors
2. Bayesian Priors: Previous season values as features
3. Age-Trajectory Interactions: Age × trajectory interactions (young players improving = stronger signal)

Implementation based on PHASE4_IMPLEMENTATION_PLAN.md
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path
from typing import List, Optional

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/trajectory_features.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Key stress vectors to calculate trajectories for
KEY_STRESS_VECTORS = [
    'CREATION_VOLUME_RATIO',
    'CREATION_TAX',
    'LEVERAGE_USG_DELTA',
    'LEVERAGE_TS_DELTA',
    'RS_PRESSURE_RESILIENCE',
    'RS_PRESSURE_APPETITE',
    'RS_RIM_APPETITE',
    'EFG_ISO_WEIGHTED',
    'RS_LATE_CLOCK_PRESSURE_RESILIENCE',  # V4.2 feature
]


class TrajectoryFeatureGenerator:
    """Generate trajectory features (YoY deltas and priors) for stress vectors."""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self) -> pd.DataFrame:
        """Load predictive dataset with all features."""
        logger.info("Loading predictive dataset...")
        
        df = pd.read_csv(self.results_dir / "predictive_dataset.csv")
        
        # Merge with pressure features if available
        pressure_path = self.results_dir / "pressure_features.csv"
        if pressure_path.exists():
            df_pressure = pd.read_csv(pressure_path)
            df = pd.merge(
                df,
                df_pressure,
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_pressure')
            )
            cols_to_drop = [c for c in df.columns if '_pressure' in c]
            df = df.drop(columns=cols_to_drop)
            logger.info(f"Merged with pressure features: {len(df)} rows")
        
        # Merge with physicality features if available
        physicality_path = self.results_dir / "physicality_features.csv"
        if physicality_path.exists():
            df_physicality = pd.read_csv(physicality_path)
            df = pd.merge(
                df,
                df_physicality,
                on=['PLAYER_NAME', 'SEASON'],
                how='left',
                suffixes=('', '_phys')
            )
            cols_to_drop = [c for c in df.columns if '_phys' in c]
            df = df.drop(columns=cols_to_drop)
            logger.info(f"Merged with physicality features: {len(df)} rows")
        
        # Merge with rim pressure features if available
        rim_path = self.results_dir / "rim_pressure_features.csv"
        if rim_path.exists():
            df_rim = pd.read_csv(rim_path)
            df = pd.merge(
                df,
                df_rim,
                on=['PLAYER_NAME', 'SEASON'],
                how='left',
                suffixes=('', '_rim')
            )
            cols_to_drop = [c for c in df.columns if '_rim' in c]
            df = df.drop(columns=cols_to_drop)
            logger.info(f"Merged with rim pressure features: {len(df)} rows")
        
        logger.info(f"Total dataset size: {len(df)} player-seasons")
        return df
    
    def parse_season(self, season: str) -> int:
        """Parse season string (e.g., '2015-16') to year (2015)."""
        if pd.isna(season):
            return None
        try:
            # Handle formats like "2015-16" or "2015-2016"
            year_str = str(season).split('-')[0]
            return int(year_str)
        except (ValueError, AttributeError):
            return None
    
    def calculate_trajectory_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate YoY deltas and previous season priors for all player-seasons.
        
        Args:
            df: DataFrame with columns PLAYER_ID, SEASON, and stress vector features
            
        Returns:
            DataFrame with trajectory features added
        """
        logger.info("Calculating trajectory features...")
        
        # Sort by player and season (chronological)
        df = df.copy()
        
        # Add year column for sorting
        df['YEAR'] = df['SEASON'].apply(self.parse_season)
        df = df.sort_values(['PLAYER_ID', 'YEAR']).copy()
        
        # Initialize trajectory feature columns
        trajectory_features = {}
        prior_features = {}
        age_interaction_features = {}
        
        # For each player, calculate YoY deltas
        players_processed = 0
        players_with_trajectory = 0
        
        for player_id in df['PLAYER_ID'].unique():
            player_df = df[df['PLAYER_ID'] == player_id].copy()
            
            if len(player_df) < 2:
                # Need at least 2 seasons for trajectory
                players_processed += 1
                continue
            
            players_processed += 1
            
            # Calculate YoY deltas for each season (starting from second season)
            for idx in range(1, len(player_df)):
                current_season = player_df.iloc[idx]
                prev_season = player_df.iloc[idx - 1]
                
                season_key = (player_id, current_season['SEASON'])
                
                # Initialize dictionaries for this season
                if season_key not in trajectory_features:
                    trajectory_features[season_key] = {}
                    prior_features[season_key] = {}
                
                # Calculate deltas for key features
                for feature in KEY_STRESS_VECTORS:
                    if feature not in df.columns:
                        continue
                    
                    current_val = current_season[feature]
                    prev_val = prev_season[feature]
                    
                    # Calculate YoY delta
                    if pd.notna(current_val) and pd.notna(prev_val):
                        delta = current_val - prev_val
                        trajectory_features[season_key][f'{feature}_YOY_DELTA'] = delta
                        prior_features[season_key][f'PREV_{feature}'] = prev_val
                    else:
                        # Missing data - set to NaN (will be filled later)
                        trajectory_features[season_key][f'{feature}_YOY_DELTA'] = np.nan
                        prior_features[season_key][f'PREV_{feature}'] = np.nan
                
                # Calculate age-trajectory interactions
                age = current_season.get('AGE', None)
                if pd.notna(age):
                    for feature in KEY_STRESS_VECTORS:
                        if feature not in df.columns:
                            continue
                        
                        delta_key = f'{feature}_YOY_DELTA'
                        if delta_key in trajectory_features[season_key]:
                            delta_val = trajectory_features[season_key][delta_key]
                            if pd.notna(delta_val):
                                age_interaction_key = f'AGE_X_{feature}_YOY_DELTA'
                                age_interaction_features[season_key] = age_interaction_features.get(season_key, {})
                                age_interaction_features[season_key][age_interaction_key] = age * delta_val
            
            players_with_trajectory += 1
        
        logger.info(f"Processed {players_processed} players, {players_with_trajectory} with trajectory data")
        
        # Convert to DataFrames
        trajectory_df = pd.DataFrame([
            {'PLAYER_ID': pid, 'SEASON': season, **features}
            for (pid, season), features in trajectory_features.items()
        ])
        
        prior_df = pd.DataFrame([
            {'PLAYER_ID': pid, 'SEASON': season, **features}
            for (pid, season), features in prior_features.items()
        ])
        
        age_interaction_df = pd.DataFrame([
            {'PLAYER_ID': pid, 'SEASON': season, **features}
            for (pid, season), features in age_interaction_features.items()
        ])
        
        # Merge back into original dataframe
        logger.info(f"Generated {len(trajectory_df)} trajectory feature rows")
        logger.info(f"Generated {len(prior_df)} prior feature rows")
        logger.info(f"Generated {len(age_interaction_df)} age-interaction feature rows")
        
        # Merge trajectory features
        df = pd.merge(
            df,
            trajectory_df,
            on=['PLAYER_ID', 'SEASON'],
            how='left'
        )
        
        # Merge prior features
        df = pd.merge(
            df,
            prior_df,
            on=['PLAYER_ID', 'SEASON'],
            how='left'
        )
        
        # Merge age-interaction features
        if not age_interaction_df.empty:
            df = pd.merge(
                df,
                age_interaction_df,
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )
        
        # Drop temporary YEAR column
        df = df.drop(columns=['YEAR'], errors='ignore')
        
        # Log coverage statistics
        trajectory_cols = [c for c in df.columns if '_YOY_DELTA' in c]
        prior_cols = [c for c in df.columns if c.startswith('PREV_')]
        age_interaction_cols = [c for c in df.columns if 'AGE_X_' in c and '_YOY_DELTA' in c]
        
        logger.info(f"\nTrajectory Feature Coverage:")
        for col in trajectory_cols[:5]:  # Show first 5
            coverage = df[col].notna().sum() / len(df) * 100
            logger.info(f"  {col}: {coverage:.1f}% coverage ({df[col].notna().sum()}/{len(df)})")
        
        logger.info(f"\nPrior Feature Coverage:")
        for col in prior_cols[:5]:  # Show first 5
            coverage = df[col].notna().sum() / len(df) * 100
            logger.info(f"  {col}: {coverage:.1f}% coverage ({df[col].notna().sum()}/{len(df)})")
        
        if age_interaction_cols:
            logger.info(f"\nAge-Interaction Feature Coverage:")
            for col in age_interaction_cols[:5]:  # Show first 5
                coverage = df[col].notna().sum() / len(df) * 100
                logger.info(f"  {col}: {coverage:.1f}% coverage ({df[col].notna().sum()}/{len(df)})")
        
        return df
    
    def save_trajectory_features(self, df: pd.DataFrame):
        """Save trajectory features to CSV."""
        output_path = self.results_dir / "trajectory_features.csv"
        
        # Extract only trajectory-related columns
        trajectory_cols = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON']
        trajectory_cols += [c for c in df.columns if '_YOY_DELTA' in c]
        trajectory_cols += [c for c in df.columns if c.startswith('PREV_')]
        trajectory_cols += [c for c in df.columns if 'AGE_X_' in c and '_YOY_DELTA' in c]
        
        # Filter to columns that exist
        trajectory_cols = [c for c in trajectory_cols if c in df.columns]
        
        df_trajectory = df[trajectory_cols].copy()
        df_trajectory.to_csv(output_path, index=False)
        logger.info(f"Saved trajectory features to {output_path}")
        logger.info(f"Total trajectory features: {len(trajectory_cols) - 3} (excluding ID columns)")
    
    def run(self):
        """Main execution function."""
        logger.info("=" * 60)
        logger.info("Phase 4: Trajectory Features Generation")
        logger.info("=" * 60)
        
        # Load data
        df = self.load_data()
        
        # Calculate trajectory features
        df_with_trajectory = self.calculate_trajectory_features(df)
        
        # Save trajectory features
        self.save_trajectory_features(df_with_trajectory)
        
        logger.info("=" * 60)
        logger.info("Trajectory features generation complete!")
        logger.info("=" * 60)


if __name__ == "__main__":
    generator = TrajectoryFeatureGenerator()
    generator.run()






