"""
Brunson Test: Historical Validation Framework

This script implements the consultant's "Brunson Test" to validate that the
latent star detection system can identify players BEFORE they break out.

The Test:
1. Train model on data up to a cutoff year (e.g., 2020)
2. Run latent star detection on a specific season (e.g., 2021)
3. Validate if identified players saw usage/value spikes in subsequent seasons

Example: If the model flagged Jalen Brunson in 2021 (DAL) before his breakout
in NYK, that's alpha. If it flagged LeBron, that's noise.
"""

import pandas as pd
import numpy as np
import logging
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import using relative import since we're in the same package
from src.nba_data.scripts.detect_latent_stars import LatentStarDetector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/brunson_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BrunsonTestValidator:
    """Validate latent star detection through historical backtesting."""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.data_dir = Path("data")
        self.results_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
    def load_regular_season_usage(self, seasons: List[str]) -> pd.DataFrame:
        """Load regular season usage data for multiple seasons."""
        logger.info(f"Loading regular season usage data for {len(seasons)} seasons...")
        
        rs_data_list = []
        for season in seasons:
            rs_path = self.data_dir / f"regular_season_{season}.csv"
            if not rs_path.exists():
                logger.warning(f"Missing {rs_path}")
                continue
            
            try:
                df_rs = pd.read_csv(rs_path)
                df_rs['SEASON'] = season
                
                if 'PLAYER_ID' in df_rs.columns and 'USG_PCT' in df_rs.columns:
                    # Handle players on multiple teams (take max usage)
                    df_rs_grouped = df_rs.groupby('PLAYER_ID').agg({
                        'USG_PCT': 'max',
                        'PLAYER_NAME': 'first'
                    }).reset_index()
                    df_rs_grouped['SEASON'] = season
                    rs_data_list.append(df_rs_grouped[['PLAYER_ID', 'SEASON', 'USG_PCT', 'PLAYER_NAME']])
            except Exception as e:
                logger.warning(f"Error loading {rs_path}: {e}")
                continue
        
        if rs_data_list:
            df_usage = pd.concat(rs_data_list, ignore_index=True)
            logger.info(f"Loaded usage data for {len(df_usage)} player-seasons")
            return df_usage
        else:
            logger.error("No usage data loaded!")
            return pd.DataFrame()
    
    def identify_latent_stars_for_season(self, season: str, 
                                         usage_threshold: float = 20.0) -> pd.DataFrame:
        """
        Run latent star detection for a specific season.
        
        Note: This uses the current model, but in a full backtest, we would
        train a model only on data up to the previous season.
        """
        logger.info(f"Identifying latent stars for {season}...")
        
        # Load predictive dataset for this season
        df_features = pd.read_csv(self.results_dir / "predictive_dataset.csv")
        df_season = df_features[df_features['SEASON'] == season].copy()
        
        if len(df_season) == 0:
            logger.warning(f"No data found for season {season}")
            return pd.DataFrame()
        
        # Load usage data
        df_usage = self.load_regular_season_usage([season])
        if not df_usage.empty:
            df_season = df_season.merge(
                df_usage[['PLAYER_ID', 'SEASON', 'USG_PCT']],
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )
        
        # Calculate stress profile scores
        detector = LatentStarDetector()
        df_season = detector.calculate_stress_profile_score(df_season)
        
        # Identify latent stars
        latent_stars = detector.identify_latent_stars(
            df_season,
            usage_threshold=usage_threshold,
            stress_percentile_threshold=80.0
        )
        
        logger.info(f"Identified {len(latent_stars)} latent stars for {season}")
        return latent_stars
    
    def validate_breakout(self, player_id: int, player_name: str, 
                        detection_season: str, 
                        subsequent_seasons: List[str],
                        usage_spike_threshold: float = 5.0) -> Dict:
        """
        Check if a player broke out in subsequent seasons.
        
        Args:
            player_id: Player ID
            player_name: Player name
            detection_season: Season when player was flagged (e.g., "2020-21")
            subsequent_seasons: Seasons to check for breakout (e.g., ["2021-22", "2022-23"])
            usage_spike_threshold: Minimum USG% increase to count as breakout (default 5%)
        
        Returns:
            Dict with breakout validation results
        """
        # Load usage data for detection season and subsequent seasons
        all_seasons = [detection_season] + subsequent_seasons
        df_usage = self.load_regular_season_usage(all_seasons)
        
        if df_usage.empty:
            return {
                'player_id': player_id,
                'player_name': player_name,
                'detection_season': detection_season,
                'breakout_detected': False,
                'reason': 'No usage data available'
            }
        
        # Get player's usage in detection season
        df_detection = df_usage[
            (df_usage['PLAYER_ID'] == player_id) & 
            (df_usage['SEASON'] == detection_season)
        ]
        
        if df_detection.empty:
            return {
                'player_id': player_id,
                'player_name': player_name,
                'detection_season': detection_season,
                'breakout_detected': False,
                'reason': f'No usage data for {detection_season}'
            }
        
        detection_usg = df_detection['USG_PCT'].iloc[0]
        # Convert to percentage if stored as decimal
        if detection_usg < 1.0:
            detection_usg = detection_usg * 100
        
        # Check subsequent seasons for breakout
        breakout_seasons = []
        max_usg = detection_usg
        
        for season in subsequent_seasons:
            df_subsequent = df_usage[
                (df_usage['PLAYER_ID'] == player_id) & 
                (df_usage['SEASON'] == season)
            ]
            
            if not df_subsequent.empty:
                subsequent_usg = df_subsequent['USG_PCT'].iloc[0]
                # Convert to percentage if stored as decimal
                if subsequent_usg < 1.0:
                    subsequent_usg = subsequent_usg * 100
                
                usg_increase = subsequent_usg - detection_usg
                max_usg = max(max_usg, subsequent_usg)
                
                if usg_increase >= usage_spike_threshold:
                    breakout_seasons.append({
                        'season': season,
                        'usg_pct': subsequent_usg,
                        'increase': usg_increase
                    })
        
        breakout_detected = len(breakout_seasons) > 0
        
        return {
            'player_id': player_id,
            'player_name': player_name,
            'detection_season': detection_season,
            'detection_usg_pct': detection_usg,
            'max_subsequent_usg_pct': max_usg,
            'breakout_detected': breakout_detected,
            'breakout_seasons': breakout_seasons,
            'max_usg_increase': max_usg - detection_usg if breakout_detected else 0
        }
    
    def run_brunson_test(self, detection_season: str,
                         subsequent_seasons: List[str],
                         usage_threshold: float = 20.0,
                         usage_spike_threshold: float = 5.0) -> pd.DataFrame:
        """
        Run the complete Brunson Test.
        
        Args:
            detection_season: Season to run latent star detection (e.g., "2020-21")
            subsequent_seasons: Seasons to check for breakout (e.g., ["2021-22", "2022-23", "2023-24"])
            usage_threshold: Maximum USG% for latent star detection (default 20%)
            usage_spike_threshold: Minimum USG% increase to count as breakout (default 5%)
        
        Returns:
            DataFrame with validation results
        """
        logger.info("=" * 60)
        logger.info("Running Brunson Test")
        logger.info("=" * 60)
        logger.info(f"Detection Season: {detection_season}")
        logger.info(f"Subsequent Seasons: {subsequent_seasons}")
        logger.info(f"Usage Threshold: {usage_threshold}%")
        logger.info(f"Breakout Threshold: {usage_spike_threshold}% increase")
        
        # Step 1: Identify latent stars for detection season
        latent_stars = self.identify_latent_stars_for_season(
            detection_season,
            usage_threshold=usage_threshold
        )
        
        if len(latent_stars) == 0:
            logger.warning("No latent stars identified. Cannot run validation.")
            return pd.DataFrame()
        
        logger.info(f"\nIdentified {len(latent_stars)} latent star candidates:")
        for idx, (_, row) in enumerate(latent_stars.head(10).iterrows(), 1):
            logger.info(f"  {idx}. {row.get('PLAYER_NAME', 'Unknown')} "
                       f"(USG: {row.get('USG_PCT', 0):.1f}%)")
        
        # Step 2: Validate breakout for each identified player
        logger.info("\nValidating breakouts...")
        validation_results = []
        
        for _, row in latent_stars.iterrows():
            player_id = row['PLAYER_ID']
            player_name = row.get('PLAYER_NAME', 'Unknown')
            
            result = self.validate_breakout(
                player_id=player_id,
                player_name=player_name,
                detection_season=detection_season,
                subsequent_seasons=subsequent_seasons,
                usage_spike_threshold=usage_spike_threshold
            )
            
            # Add stress profile info
            result['stress_profile_score'] = row.get('STRESS_PROFILE_SCORE', 0)
            result['creation_volume_ratio'] = row.get('CREATION_VOLUME_RATIO', 0)
            result['pressure_resilience'] = row.get('RS_PRESSURE_RESILIENCE', 0)
            
            validation_results.append(result)
        
        df_results = pd.DataFrame(validation_results)
        
        # Calculate summary statistics
        total_identified = len(df_results)
        breakouts = df_results['breakout_detected'].sum()
        breakout_rate = (breakouts / total_identified * 100) if total_identified > 0 else 0
        
        logger.info("\n" + "=" * 60)
        logger.info("Brunson Test Results")
        logger.info("=" * 60)
        logger.info(f"Total Identified: {total_identified}")
        logger.info(f"Breakouts Detected: {breakouts}")
        logger.info(f"Breakout Rate: {breakout_rate:.1f}%")
        
        # Show top breakouts
        if breakouts > 0:
            logger.info("\nTop Breakouts:")
            df_breakouts = df_results[df_results['breakout_detected']].sort_values(
                'max_usg_increase', ascending=False
            )
            for idx, (_, row) in enumerate(df_breakouts.head(10).iterrows(), 1):
                logger.info(f"  {idx}. {row['player_name']}: "
                           f"{row['detection_usg_pct']:.1f}% → {row['max_subsequent_usg_pct']:.1f}% "
                           f"(+{row['max_usg_increase']:.1f}%)")
        
        # Save results
        output_path = self.results_dir / f"brunson_test_{detection_season.replace('-', '_')}.csv"
        df_results.to_csv(output_path, index=False)
        logger.info(f"\nSaved results to {output_path}")
        
        # Generate report
        report = self.generate_report(df_results, detection_season, subsequent_seasons)
        report_path = self.results_dir / f"brunson_test_{detection_season.replace('-', '_')}_report.md"
        with open(report_path, 'w') as f:
            f.write(report)
        logger.info(f"Saved report to {report_path}")
        
        return df_results
    
    def generate_report(self, df_results: pd.DataFrame, 
                       detection_season: str,
                       subsequent_seasons: List[str]) -> str:
        """Generate markdown report of Brunson Test results."""
        total = len(df_results)
        breakouts = df_results['breakout_detected'].sum()
        breakout_rate = (breakouts / total * 100) if total > 0 else 0
        
        report_lines = [
            "# Brunson Test: Historical Validation Report",
            "",
            f"**Detection Season:** {detection_season}",
            f"**Subsequent Seasons Checked:** {', '.join(subsequent_seasons)}",
            "",
            "## Executive Summary",
            "",
            f"- **Total Latent Stars Identified:** {total}",
            f"- **Breakouts Detected:** {breakouts}",
            f"- **Breakout Rate:** {breakout_rate:.1f}%",
            "",
            "---",
            "",
            "## Methodology",
            "",
            "The Brunson Test validates that the latent star detection system can identify",
            "players **before** they break out. The test:",
            "",
            "1. Identifies latent stars in a given season (players with high stress profiles but low usage)",
            "2. Checks if those players saw significant usage/value spikes in subsequent seasons",
            "3. Calculates the breakout rate to measure predictive value",
            "",
            "**Breakout Definition:** USG% increase of ≥5% in any subsequent season",
            "",
            "---",
            "",
            "## Results",
            ""
        ]
        
        if breakouts > 0:
            report_lines.extend([
                "### Successful Breakouts",
                "",
                "| Player | Detection USG% | Max Subsequent USG% | Increase | Breakout Season(s) |",
                "|--------|----------------|---------------------|----------|-------------------|"
            ])
            
            df_breakouts = df_results[df_results['breakout_detected']].sort_values(
                'max_usg_increase', ascending=False
            )
            
            for _, row in df_breakouts.iterrows():
                breakout_seasons_str = ", ".join([
                    f"{b['season']} (+{b['increase']:.1f}%)" 
                    for b in row['breakout_seasons']
                ])
                report_lines.append(
                    f"| {row['player_name']} | {row['detection_usg_pct']:.1f}% | "
                    f"{row['max_subsequent_usg_pct']:.1f}% | +{row['max_usg_increase']:.1f}% | "
                    f"{breakout_seasons_str} |"
                )
        else:
            report_lines.append("**No breakouts detected.**")
        
        report_lines.extend([
            "",
            "---",
            "",
            "## Interpretation",
            "",
            f"A breakout rate of {breakout_rate:.1f}% indicates:",
            "",
            "- **>30%**: Strong predictive value (model identifies real latent stars)",
            "- **15-30%**: Moderate predictive value (some false positives)",
            "- **<15%**: Weak predictive value (mostly noise, not signal)",
            "",
            "---",
            "",
            "## Full Results",
            "",
            f"See `results/brunson_test_{detection_season.replace('-', '_')}.csv` for complete data.",
            ""
        ])
        
        return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description='Run Brunson Test for historical validation')
    parser.add_argument('--detection-season', type=str, default='2020-21',
                       help='Season to run latent star detection (e.g., 2020-21)')
    parser.add_argument('--subsequent-seasons', nargs='+', 
                       default=['2021-22', '2022-23', '2023-24'],
                       help='Seasons to check for breakout')
    parser.add_argument('--usage-threshold', type=float, default=20.0,
                       help='Maximum USG% for latent star detection (default: 20.0)')
    parser.add_argument('--usage-spike-threshold', type=float, default=5.0,
                       help='Minimum USG% increase to count as breakout (default: 5.0)')
    
    args = parser.parse_args()
    
    validator = BrunsonTestValidator()
    results = validator.run_brunson_test(
        detection_season=args.detection_season,
        subsequent_seasons=args.subsequent_seasons,
        usage_threshold=args.usage_threshold,
        usage_spike_threshold=args.usage_spike_threshold
    )
    
    if not results.empty:
        print("\n✅ Brunson Test Complete!")
        print(f"Breakout Rate: {(results['breakout_detected'].sum() / len(results) * 100):.1f}%")
    else:
        print("\n⚠️  No results generated. Check logs for details.")


if __name__ == "__main__":
    main()

