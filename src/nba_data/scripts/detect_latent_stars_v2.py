"""
Phase 2: Latent Star Detection (Use Case B)

This script identifies "sleeping giants" - players with high skills but low opportunity.
Based on post-mortem insights:
- Age < 26 is the PRIMARY filter (veterans have no latent potential)
- Usage < 25% to identify players with low opportunity
- Rank by star-level potential at 25% usage (not current performance)
- Don't over-engineer quality filters - age is the simple solution
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent))
from predict_conditional_archetype import ConditionalArchetypePredictor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LatentStarDetectorV2:
    """Detect latent stars using usage-aware conditional predictions."""
    
    def __init__(self):
        self.predictor = ConditionalArchetypePredictor()
        self.results_dir = Path("results")
    
    def detect_latent_stars(
        self,
        season: str = None,
        age_max: int = 25,
        usage_max: float = 0.25,
        target_usage: float = 0.25,
        min_star_potential: float = 0.50
    ) -> pd.DataFrame:
        """
        Detect latent stars - players with high skills but low opportunity.
        
        Args:
            season: Season to analyze (e.g., "2020-21"). If None, uses all seasons.
            age_max: Maximum age (default: 25, as veterans have no latent potential)
            usage_max: Maximum current usage (default: 0.25 = 25%)
            target_usage: Usage level to predict at (default: 0.25 = 25%)
            min_star_potential: Minimum star-level potential to include (default: 0.50 = 50%)
        
        Returns:
            DataFrame with latent star candidates ranked by star-level potential
        """
        logger.info("="*80)
        logger.info("LATENT STAR DETECTION (Use Case B)")
        logger.info("="*80)
        logger.info(f"Filters: Age < {age_max+1}, Usage < {usage_max*100:.0f}%")
        logger.info(f"Target Usage: {target_usage*100:.0f}%")
        logger.info(f"Min Star Potential: {min_star_potential*100:.0f}%")
        
        # Load feature data
        df_features = self.predictor.df_features.copy()
        
        # Filter by season if specified
        if season:
            df_features = df_features[df_features['SEASON'] == season]
            logger.info(f"Filtered to season: {season}")
        
        # PRIMARY FILTER: Age < 26 (veterans have no latent potential)
        if 'AGE' in df_features.columns:
            df_features = df_features[df_features['AGE'] < (age_max + 1)]
            logger.info(f"After age filter (<{age_max+1}): {len(df_features)} players")
        else:
            logger.warning("AGE column not found - cannot apply age filter")
        
        # SECONDARY FILTER: Usage < 25% (identify players with low opportunity)
        if 'USG_PCT' in df_features.columns:
            df_features = df_features[df_features['USG_PCT'] < usage_max]
            logger.info(f"After usage filter (<{usage_max*100:.0f}%): {len(df_features)} players")
        else:
            logger.warning("USG_PCT column not found - cannot apply usage filter")
        
        if len(df_features) == 0:
            logger.warning("No players match the filters")
            return pd.DataFrame()
        
        # Predict star-level potential at target usage for each candidate
        logger.info(f"\nPredicting star-level potential at {target_usage*100:.0f}% usage...")
        results = []
        
        for idx, row in df_features.iterrows():
            try:
                pred = self.predictor.predict_archetype_at_usage(row, target_usage)
                
                results.append({
                    'PLAYER_ID': row.get('PLAYER_ID', ''),
                    'PLAYER_NAME': row.get('PLAYER_NAME', ''),
                    'SEASON': row.get('SEASON', ''),
                    'AGE': row.get('AGE', None),
                    'RS_USG_PCT': row.get('USG_PCT', None),
                    'TARGET_USAGE': target_usage * 100,
                    'PREDICTED_ARCHETYPE_AT_TARGET': pred['predicted_archetype'],
                    'STAR_LEVEL_POTENTIAL': pred['star_level_potential'],
                    'KING_PROB': pred['probabilities'].get('King', 0),
                    'BULLDOZER_PROB': pred['probabilities'].get('Bulldozer', 0),
                    'SNIPER_PROB': pred['probabilities'].get('Sniper', 0),
                    'VICTIM_PROB': pred['probabilities'].get('Victim', 0),
                    'CONFIDENCE_FLAGS': ', '.join(pred['confidence_flags']) if pred['confidence_flags'] else 'None',
                    # Include key stress vectors for analysis
                    'CREATION_VOLUME_RATIO': row.get('CREATION_VOLUME_RATIO', None),
                    'LEVERAGE_USG_DELTA': row.get('LEVERAGE_USG_DELTA', None),
                    'LEVERAGE_TS_DELTA': row.get('LEVERAGE_TS_DELTA', None),
                    'RS_PRESSURE_APPETITE': row.get('RS_PRESSURE_APPETITE', None),
                    'RS_LATE_CLOCK_PRESSURE_RESILIENCE': row.get('RS_LATE_CLOCK_PRESSURE_RESILIENCE', None)
                })
            except Exception as e:
                logger.warning(f"Error predicting for {row.get('PLAYER_NAME', 'Unknown')}: {e}")
                continue
        
        df_results = pd.DataFrame(results)
        
        if len(df_results) == 0:
            logger.warning("No predictions generated")
            return pd.DataFrame()
        
        # Filter by minimum star potential
        df_results = df_results[df_results['STAR_LEVEL_POTENTIAL'] >= min_star_potential]
        logger.info(f"After min star potential filter (≥{min_star_potential*100:.0f}%): {len(df_results)} candidates")
        
        # Rank by star-level potential (descending)
        df_results = df_results.sort_values('STAR_LEVEL_POTENTIAL', ascending=False).reset_index(drop=True)
        df_results['RANK'] = range(1, len(df_results) + 1)
        
        logger.info(f"\nTop 10 Latent Star Candidates:")
        for idx, row in df_results.head(10).iterrows():
            logger.info(f"  {row['RANK']}. {row['PLAYER_NAME']} ({row['SEASON']}) - "
                       f"Age: {row['AGE']:.1f}, RS Usage: {row['RS_USG_PCT']*100:.1f}%, "
                       f"Star Potential at {row['TARGET_USAGE']:.0f}%: {row['STAR_LEVEL_POTENTIAL']:.2%}")
        
        return df_results
    
    def detect_latent_stars_multi_season(
        self,
        seasons: list = None,
        age_max: int = 25,
        usage_max: float = 0.25,
        target_usage: float = 0.25,
        min_star_potential: float = 0.50
    ) -> pd.DataFrame:
        """
        Detect latent stars across multiple seasons.
        
        Args:
            seasons: List of seasons to analyze (e.g., ["2020-21", "2021-22"])
            age_max: Maximum age (default: 25)
            usage_max: Maximum current usage (default: 0.25)
            target_usage: Usage level to predict at (default: 0.25)
            min_star_potential: Minimum star-level potential (default: 0.50)
        
        Returns:
            DataFrame with latent star candidates across all seasons
        """
        if seasons is None:
            # Get all available seasons
            df_features = self.predictor.df_features
            seasons = sorted(df_features['SEASON'].unique())
            logger.info(f"No seasons specified - analyzing all available seasons: {seasons}")
        
        all_results = []
        
        for season in seasons:
            logger.info(f"\nAnalyzing season: {season}")
            season_results = self.detect_latent_stars(
                season=season,
                age_max=age_max,
                usage_max=usage_max,
                target_usage=target_usage,
                min_star_potential=min_star_potential
            )
            
            if len(season_results) > 0:
                all_results.append(season_results)
        
        if len(all_results) == 0:
            logger.warning("No latent stars found across any season")
            return pd.DataFrame()
        
        # Combine results
        df_all = pd.concat(all_results, ignore_index=True)
        
        # Re-rank across all seasons
        df_all = df_all.sort_values('STAR_LEVEL_POTENTIAL', ascending=False).reset_index(drop=True)
        df_all['RANK'] = range(1, len(df_all) + 1)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Total Latent Star Candidates: {len(df_all)}")
        logger.info(f"{'='*80}")
        
        return df_all


if __name__ == "__main__":
    detector = LatentStarDetectorV2()
    
    # Example: Detect latent stars in 2020-21 season (Brunson test)
    logger.info("\n=== Example: 2020-21 Season (Brunson Test) ===")
    results_2021 = detector.detect_latent_stars(
        season="2020-21",
        age_max=25,
        usage_max=0.25,
        target_usage=0.25,
        min_star_potential=0.50
    )
    
    if len(results_2021) > 0:
        # Save results
        output_path = Path("results") / "latent_stars_v2_2020_21.csv"
        results_2021.to_csv(output_path, index=False)
        logger.info(f"\nResults saved to {output_path}")
        
        # Check if known breakouts are identified
        known_breakouts = ['Jalen Brunson', 'Tyrese Haliburton', 'Tyrese Maxey']
        logger.info(f"\nKnown Breakouts Check:")
        for breakout in known_breakouts:
            if breakout in results_2021['PLAYER_NAME'].values:
                row = results_2021[results_2021['PLAYER_NAME'] == breakout].iloc[0]
                logger.info(f"  ✅ {breakout}: Rank {row['RANK']}, Star Potential: {row['STAR_LEVEL_POTENTIAL']:.2%}")
            else:
                logger.warning(f"  ⚠️  {breakout}: Not identified (may be below threshold)")














