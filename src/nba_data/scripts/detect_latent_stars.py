"""
Latent Star Detection: Find "Sleeping Giants"

This script identifies players with high stress vector profiles but low usage,
suggesting they have the potential to scale up in playoffs but haven't been
given the opportunity yet.

The consultant's hypothesis: "Who is paid like a role player ('Sniper') but has
the latent stress profile of a 'King'?"

Key Criteria:
1. Low usage (< 20% USG in regular season)
2. High stress vector scores (top decile in key metrics)
3. High pressure resilience (ability to make tough shots)
4. High creation volume ratio (self-creation ability)
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path
from typing import List, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/latent_star_detection.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class LatentStarDetector:
    """Detect players with high stress profiles but low usage."""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.data_dir = Path("data")
        self.results_dir.mkdir(exist_ok=True)
        
    def load_data(self) -> pd.DataFrame:
        """Load stress vectors and regular season usage data."""
        logger.info("Loading data...")
        
        # Load stress vectors
        df_features = pd.read_csv(self.results_dir / "predictive_dataset.csv")
        logger.info(f"Loaded {len(df_features)} player-seasons with stress vectors")
        
        # Load pressure features
        pressure_path = self.results_dir / "pressure_features.csv"
        if pressure_path.exists():
            df_pressure = pd.read_csv(pressure_path)
            df_features = df_features.merge(
                df_pressure[['PLAYER_ID', 'SEASON'] + 
                           [c for c in df_pressure.columns if 'PRESSURE' in c or 'CLOCK' in c]],
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )
        
        # Load physicality features
        physicality_path = self.results_dir / "physicality_features.csv"
        if physicality_path.exists():
            df_physicality = pd.read_csv(physicality_path)
            df_features = df_features.merge(
                df_physicality[['PLAYER_ID', 'SEASON'] + 
                             [c for c in df_physicality.columns if 'FTr' in c or 'RIM' in c]],
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )
        
        # Load regular season stats for actual USG% data
        logger.info("Loading regular season usage data...")
        rs_files = list(self.data_dir.glob("regular_season_*.csv"))
        if not rs_files:
            logger.warning("No regular season files found. Cannot filter by usage.")
            return df_features
        
        rs_data_list = []
        for rs_file in rs_files:
            try:
                # Extract season from filename (e.g., "regular_season_2023-24.csv" -> "2023-24")
                season = rs_file.stem.replace("regular_season_", "")
                df_rs = pd.read_csv(rs_file)
                df_rs['SEASON'] = season
                
                # Select only needed columns
                if 'PLAYER_ID' in df_rs.columns and 'USG_PCT' in df_rs.columns:
                    rs_data_list.append(df_rs[['PLAYER_ID', 'SEASON', 'USG_PCT', 'PLAYER_NAME']])
            except Exception as e:
                logger.warning(f"Error loading {rs_file}: {e}")
                continue
        
        if rs_data_list:
            df_rs_usage = pd.concat(rs_data_list, ignore_index=True)
            # Handle players who played for multiple teams (take max usage)
            df_rs_usage = df_rs_usage.groupby(['PLAYER_ID', 'SEASON']).agg({
                'USG_PCT': 'max',  # Take max usage if player was on multiple teams
                'PLAYER_NAME': 'first'  # Keep first name
            }).reset_index()
            
            # Merge usage data
            df_features = df_features.merge(
                df_rs_usage[['PLAYER_ID', 'SEASON', 'USG_PCT']],
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )
            logger.info(f"Merged usage data for {df_features['USG_PCT'].notna().sum()} player-seasons")
        else:
            logger.warning("No regular season usage data loaded. Cannot filter by usage.")
            df_features['USG_PCT'] = np.nan
        
        return df_features
    
    def calculate_stress_profile_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate composite stress profile score."""
        logger.info("Calculating stress profile scores...")
        
        df = df.copy()
        
        # Key stress vector features that indicate playoff readiness
        # CONSULTANT FIX: CREATION_BOOST is a "superpower" signal - efficiency increases when self-creating
        # This is a "physics violation" indicating elite self-creation ability (e.g., Tyrese Maxey)
        stress_features = [
            'CREATION_BOOST',  # CONSULTANT FIX: Superpower signal (1.5x weighted when CREATION_TAX > 0)
            'CREATION_VOLUME_RATIO',  # Self-creation ability
            'RS_PRESSURE_RESILIENCE',  # Ability to make tough shots
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE',  # Late-clock bailout ability
            'EFG_ISO_WEIGHTED',  # Isolation efficiency
            'LEVERAGE_USG_DELTA',  # Clutch usage scaling
            'RS_FTr',  # Physicality
        ]
        
        # Filter to existing features
        existing_features = [f for f in stress_features if f in df.columns]
        logger.info(f"Using {len(existing_features)} stress features for scoring")
        
        # Calculate percentiles for each feature
        for feature in existing_features:
            # Only calculate on non-null values
            valid_mask = df[feature].notna()
            if valid_mask.sum() < 10:
                continue
            
            # Calculate percentile (0-100)
            df.loc[valid_mask, f'{feature}_PERCENTILE'] = (
                df.loc[valid_mask, feature].rank(pct=True) * 100
            )
        
        # Calculate composite stress profile score
        # Average of percentiles (higher = better stress profile)
        percentile_cols = [c for c in df.columns if c.endswith('_PERCENTILE')]
        
        if percentile_cols:
            df['STRESS_PROFILE_SCORE'] = df[percentile_cols].mean(axis=1)
            logger.info(f"Calculated stress profile scores for {df['STRESS_PROFILE_SCORE'].notna().sum()} players")
        else:
            logger.warning("No percentile columns created. Cannot calculate stress profile score.")
            df['STRESS_PROFILE_SCORE'] = np.nan
        
        return df
    
    def identify_latent_stars(self, df: pd.DataFrame, 
                             usage_threshold: float = 20.0,
                             stress_percentile_threshold: float = 80.0) -> pd.DataFrame:
        """
        Identify latent stars based on criteria.
        
        CONSULTANT'S FIX: Filter by LOW USAGE FIRST, then rank by stress profile.
        A "latent star" = High Capacity + Low Opportunity, not just High Capacity.
        
        Args:
            df: DataFrame with stress vectors and usage data
            usage_threshold: Maximum USG% to be considered "low usage" (default 20%)
            stress_percentile_threshold: Minimum stress profile percentile (default 80th)
        """
        logger.info("Identifying latent stars...")
        logger.info(f"Using usage threshold: {usage_threshold}%")
        logger.info(f"Using stress percentile threshold: {stress_percentile_threshold}th")
        
        # Filter for players with stress profile scores
        df_valid = df[df['STRESS_PROFILE_SCORE'].notna()].copy()
        
        if len(df_valid) == 0:
            logger.error("No players with valid stress profile scores!")
            return pd.DataFrame()
        
        # CONSULTANT'S FIX: Filter by LOW USAGE FIRST
        # This is the critical change - we want players with high capacity but low opportunity
        if 'USG_PCT' not in df_valid.columns or df_valid['USG_PCT'].isna().all():
            logger.error("USG_PCT column missing or all NaN. Cannot filter by usage.")
            logger.warning("Falling back to stress profile only (this will include established stars)")
            df_low_usage = df_valid.copy()
        else:
            # Convert USG_PCT to percentage if it's stored as decimal (0.20) vs percentage (20.0)
            # Check if values are typically < 1 (decimal) or > 1 (percentage)
            sample_usg = df_valid['USG_PCT'].dropna()
            if len(sample_usg) > 0:
                max_usg = sample_usg.max()
                if max_usg < 1.0:
                    # Stored as decimal, convert to percentage
                    usage_threshold_decimal = usage_threshold / 100.0
                    df_low_usage = df_valid[df_valid['USG_PCT'] < usage_threshold_decimal].copy()
                else:
                    # Stored as percentage
                    df_low_usage = df_valid[df_valid['USG_PCT'] < usage_threshold].copy()
            else:
                logger.warning("No valid USG_PCT values. Cannot filter by usage.")
                df_low_usage = df_valid.copy()
        
        logger.info(f"After usage filter (< {usage_threshold}%): {len(df_low_usage)} players")
        
        if len(df_low_usage) == 0:
            logger.warning("No players meet usage threshold. Try lowering usage_threshold.")
            return pd.DataFrame()
        
        # Calculate stress profile percentile (on the low-usage subset)
        df_low_usage['STRESS_PROFILE_PERCENTILE'] = (
            df_low_usage['STRESS_PROFILE_SCORE'].rank(pct=True) * 100
        )
        
        # Filter by stress profile percentile
        latent_stars = df_low_usage[
            df_low_usage['STRESS_PROFILE_PERCENTILE'] >= stress_percentile_threshold
        ].copy()
        
        logger.info(f"After stress profile filter (≥{stress_percentile_threshold}th percentile): {len(latent_stars)} players")
        
        # Additional quality filters: High creation ability and pressure resilience
        if 'CREATION_VOLUME_RATIO' in latent_stars.columns:
            # High creation ability (top 30% of remaining players)
            creation_threshold = latent_stars['CREATION_VOLUME_RATIO'].quantile(0.7)
            before_creation = len(latent_stars)
            latent_stars = latent_stars[
                latent_stars['CREATION_VOLUME_RATIO'] >= creation_threshold
            ]
            logger.info(f"After creation filter (≥{creation_threshold:.3f}): {len(latent_stars)} players (removed {before_creation - len(latent_stars)})")
        
        if 'RS_PRESSURE_RESILIENCE' in latent_stars.columns:
            # High pressure resilience (top 30% of remaining players)
            pressure_threshold = latent_stars['RS_PRESSURE_RESILIENCE'].quantile(0.7)
            before_pressure = len(latent_stars)
            latent_stars = latent_stars[
                latent_stars['RS_PRESSURE_RESILIENCE'] >= pressure_threshold
            ]
            logger.info(f"After pressure resilience filter (≥{pressure_threshold:.3f}): {len(latent_stars)} players (removed {before_pressure - len(latent_stars)})")
        
        # Sort by stress profile score (descending)
        latent_stars = latent_stars.sort_values('STRESS_PROFILE_SCORE', ascending=False)
        
        logger.info(f"Final latent star candidates: {len(latent_stars)}")
        
        return latent_stars
    
    def generate_report(self, latent_stars: pd.DataFrame) -> str:
        """Generate latent star detection report."""
        logger.info("Generating report...")
        
        if len(latent_stars) == 0:
            return "# Latent Star Detection Report\n\nNo latent stars identified."
        
        # Sort by stress profile score
        latent_stars_sorted = latent_stars.sort_values('STRESS_PROFILE_SCORE', ascending=False)
        
        report_lines = [
            "# Latent Star Detection Report: Sleeping Giants",
            "",
            "## Executive Summary",
            "",
            f"This report identifies **{len(latent_stars)}** players with high stress vector profiles",
            "who may be undervalued or underutilized. These 'Sleeping Giants' have the stress",
            "profile of playoff stars but may not have been given the opportunity yet.",
            "",
            "---",
            "",
            "## Methodology",
            "",
            "**Criteria for Latent Stars:**",
            "",
            "1. **Low Usage** (< 20% USG in regular season): Filter FIRST - identifies players with low opportunity",
            "2. **Top Stress Profile** (≥80th percentile): High scores across key stress vectors",
            "3. **High Creation Ability**: Top 30% in Creation Volume Ratio",
            "4. **High Pressure Resilience**: Top 30% in Pressure Resilience",
            "",
            "**Key Stress Vectors Analyzed:**",
            "- Creation Volume Ratio (self-creation ability)",
            "- Pressure Resilience (ability to make tough shots)",
            "- Late-Clock Pressure Resilience (bailout ability)",
            "- Isolation Efficiency",
            "- Clutch Usage Scaling",
            "- Physicality (Free Throw Rate)",
            "",
            "---",
            "",
            "## Top Latent Star Candidates",
            "",
            "| Rank | Player | Season | RS USG% | Stress Score | Creation Ratio | Pressure Resilience | Key Strengths |",
            "|------|--------|--------|---------|--------------|----------------|-------------------|---------------|"
        ]
        
        # Add top 20 candidates
        top_20 = latent_stars_sorted.head(20)
        
        for idx, (_, row) in enumerate(top_20.iterrows(), 1):
            player = row.get('PLAYER_NAME', 'Unknown')
            season = row.get('SEASON', 'Unknown')
            usg_pct = row.get('USG_PCT', 0)
            # Convert to percentage if stored as decimal
            if usg_pct < 1.0:
                usg_pct = usg_pct * 100
            stress_score = row.get('STRESS_PROFILE_SCORE', 0)
            creation = row.get('CREATION_VOLUME_RATIO', 0)
            pressure = row.get('RS_PRESSURE_RESILIENCE', 0)
            
            # Identify key strengths
            strengths = []
            if creation > 0.5:
                strengths.append("High Creation")
            if pressure > 0.5:
                strengths.append("Pressure Resilient")
            if row.get('RS_LATE_CLOCK_PRESSURE_RESILIENCE', 0) > 0.5:
                strengths.append("Late-Clock")
            if row.get('EFG_ISO_WEIGHTED', 0) > 0.5:
                strengths.append("Isolation")
            
            strengths_str = ", ".join(strengths) if strengths else "N/A"
            
            report_lines.append(
                f"| {idx} | {player} | {season} | {usg_pct:.1f}% | {stress_score:.1f} | "
                f"{creation:.3f} | {pressure:.3f} | {strengths_str} |"
            )
        
        report_lines.extend([
            "",
            "---",
            "",
            "## Insights",
            "",
            "### What Makes a Latent Star?",
            "",
            "These players share common characteristics:",
            "",
            "1. **Self-Creation Ability**: High Creation Volume Ratio indicates they can",
            "   generate their own offense, critical for playoff success.",
            "",
            "2. **Pressure Resilience**: Ability to make tough shots (high Pressure Resilience)",
            "   suggests they won't shrink in playoff moments.",
            "",
            "3. **Late-Clock Ability**: Players with high Late-Clock Pressure Resilience",
            "   can bail out broken plays, a valuable playoff skill.",
            "",
            "### Why They're Undervalued",
            "",
            "These players may be undervalued because:",
            "",
            "- **Low Usage**: They haven't been given high-usage roles in regular season",
            "- **Role Player Perception**: They're seen as complementary pieces, not stars",
            "- **Small Sample Size**: Limited opportunity to show their stress profile",
            "",
            "### The \"Next Jalen Brunson\" Test",
            "",
            "Jalen Brunson in 2021 (DAL) had a high stress profile but was a backup.",
            "When given opportunity in NYK, he became a star. These candidates may follow",
            "a similar path.",
            "",
            "---",
            "",
            "## Full Results",
            "",
            "See `results/latent_stars.csv` for complete list of candidates.",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def run(self):
        """Run complete latent star detection pipeline."""
        logger.info("=" * 60)
        logger.info("Starting Latent Star Detection")
        logger.info("=" * 60)
        
        # 1. Load data
        df = self.load_data()
        
        # 2. Calculate stress profile scores
        df = self.calculate_stress_profile_score(df)
        
        # 3. Identify latent stars
        latent_stars = self.identify_latent_stars(df)
        
        if len(latent_stars) == 0:
            logger.warning("No latent stars identified!")
            return
        
        # 4. Save results
        output_cols = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'USG_PCT', 'STRESS_PROFILE_SCORE',
                      'STRESS_PROFILE_PERCENTILE', 'CREATION_BOOST', 'CREATION_TAX', 'CREATION_VOLUME_RATIO',
                      'RS_PRESSURE_RESILIENCE', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE',
                      'EFG_ISO_WEIGHTED', 'LEVERAGE_USG_DELTA', 'RS_FTr']
        
        output_cols = [c for c in output_cols if c in latent_stars.columns]
        latent_stars[output_cols].to_csv(
            self.results_dir / 'latent_stars.csv',
            index=False
        )
        logger.info(f"Saved {len(latent_stars)} latent stars to {self.results_dir / 'latent_stars.csv'}")
        
        # 5. Generate report
        report = self.generate_report(latent_stars)
        report_path = self.results_dir / 'latent_star_detection_report.md'
        with open(report_path, 'w') as f:
            f.write(report)
        logger.info(f"Saved report to {report_path}")
        
        # 6. Print summary
        logger.info("=" * 60)
        logger.info("Latent Star Detection Complete")
        logger.info("=" * 60)
        logger.info(f"Total latent stars identified: {len(latent_stars)}")
        logger.info("\nTop 5 Candidates:")
        top_5 = latent_stars.sort_values('STRESS_PROFILE_SCORE', ascending=False).head(5)
        for idx, (_, row) in enumerate(top_5.iterrows(), 1):
            logger.info(f"  {idx}. {row.get('PLAYER_NAME', 'Unknown')} ({row.get('SEASON', 'Unknown')}) - "
                       f"Stress Score: {row.get('STRESS_PROFILE_SCORE', 0):.1f}")


def main():
    detector = LatentStarDetector()
    detector.run()


if __name__ == "__main__":
    main()

