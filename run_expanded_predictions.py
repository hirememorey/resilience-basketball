"""
Run Model on Expanded Dataset: All Young Players (Age <= 25, Minimum Minutes)

This script runs the resilience model on all player-seasons from the past 10 years
where players were 25 or younger and had at least a minimum threshold of minutes played.

It generates comprehensive predictions including:
- Archetype predictions at current usage
- Archetype predictions at 25% usage (latent star detection)
- 2D Risk Matrix predictions (Performance + Dependence)
- Full stress vector profiles
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging
from typing import Optional, Dict
import argparse
from tqdm import tqdm

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_minutes_data(seasons: list) -> pd.DataFrame:
    """
    Fetch minutes played data from NBA API for all seasons.
    
    Args:
        seasons: List of season strings (e.g., ['2015-16', '2016-17'])
        
    Returns:
        DataFrame with PLAYER_ID, SEASON, MIN (total minutes), GP (games played)
    """
    try:
        from src.nba_data.api.nba_stats_client import NBAStatsClient
        
        client = NBAStatsClient()
        all_data = []
        
        logger.info(f"Fetching minutes data for {len(seasons)} seasons...")
        
        for season in tqdm(seasons, desc="Fetching minutes"):
            try:
                # Fetch base stats which includes MIN and GP
                response = client.get_league_player_base_stats(
                    season=season,
                    season_type="Regular Season",
                    per_mode="Totals"
                )
                
                if response.get('resultSets') and response['resultSets'][0].get('rowSet'):
                    headers = response['resultSets'][0]['headers']
                    rows = response['resultSets'][0]['rowSet']
                    df_season = pd.DataFrame(rows, columns=headers)
                    df_season['SEASON'] = season
                    
                    # Select relevant columns
                    cols_to_keep = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'MIN', 'GP']
                    cols_to_keep = [c for c in cols_to_keep if c in df_season.columns]
                    df_season = df_season[cols_to_keep].copy()
                    
                    # Convert MIN to numeric (might be string)
                    if 'MIN' in df_season.columns:
                        df_season['MIN'] = pd.to_numeric(df_season['MIN'], errors='coerce')
                    if 'GP' in df_season.columns:
                        df_season['GP'] = pd.to_numeric(df_season['GP'], errors='coerce')
                    
                    all_data.append(df_season)
                    
            except Exception as e:
                logger.warning(f"Error fetching minutes for {season}: {e}")
                continue
        
        if len(all_data) == 0:
            logger.warning("No minutes data fetched. Will use usage-based proxy.")
            return pd.DataFrame()
        
        df_minutes = pd.concat(all_data, ignore_index=True)
        logger.info(f"Fetched minutes data for {len(df_minutes)} player-seasons")
        return df_minutes
        
    except Exception as e:
        logger.warning(f"Error initializing API client: {e}")
        logger.info("Will use usage-based proxy for minutes filtering")
        return pd.DataFrame()


def filter_by_minutes(
    df: pd.DataFrame,
    df_minutes: Optional[pd.DataFrame],
    min_minutes: int = 500
) -> pd.DataFrame:
    """
    Filter dataset by minimum minutes played.
    
    Args:
        df: Main dataset with player-seasons
        df_minutes: DataFrame with minutes data (PLAYER_ID, SEASON, MIN)
        min_minutes: Minimum total minutes required
        
    Returns:
        Filtered DataFrame
    """
    if df_minutes is None or df_minutes.empty:
        # Fallback: Use usage-based proxy
        # Players with meaningful usage (>= 15%) likely have meaningful minutes
        logger.info(f"No minutes data available. Using usage-based proxy (USG_PCT >= 0.15)")
        if 'USG_PCT' in df.columns:
            df_filtered = df[df['USG_PCT'] >= 0.15].copy()
            logger.info(f"Filtered to {len(df_filtered)} player-seasons with USG_PCT >= 15%")
            return df_filtered
        else:
            logger.warning("No USG_PCT column found. Cannot filter by usage proxy.")
            return df
    
    # Merge minutes data
    df_merged = pd.merge(
        df,
        df_minutes[['PLAYER_ID', 'SEASON', 'MIN', 'GP']],
        on=['PLAYER_ID', 'SEASON'],
        how='left'
    )
    
    # Filter by minimum minutes
    df_filtered = df_merged[
        (df_merged['MIN'].notna()) & 
        (df_merged['MIN'] >= min_minutes)
    ].copy()
    
    logger.info(f"Filtered to {len(df_filtered)} player-seasons with MIN >= {min_minutes}")
    
    return df_filtered


def main():
    """Run predictions on expanded dataset."""
    
    parser = argparse.ArgumentParser(description='Run model on expanded dataset')
    parser.add_argument('--min-minutes', type=int, default=500,
                       help='Minimum total minutes played (default: 500)')
    parser.add_argument('--max-age', type=int, default=25,
                       help='Maximum age (default: 25)')
    parser.add_argument('--fetch-minutes', action='store_true',
                       help='Fetch minutes data from API (slower but more accurate)')
    parser.add_argument('--output', type=str, default='results/expanded_predictions.csv',
                       help='Output file path')
    parser.add_argument('--no-2d', dest='include_2d', action='store_false',
                       help='Disable 2D Risk Matrix predictions (default: enabled)')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Batch size for progress logging (default: 100)')
    
    args = parser.parse_args()
    
    # Default include_2d to True if not explicitly disabled
    if not hasattr(args, 'include_2d'):
        args.include_2d = True
    
    logger.info("="*80)
    logger.info("EXPANDED DATASET PREDICTIONS")
    logger.info("="*80)
    logger.info(f"Filters: Age <= {args.max_age}, Minutes >= {args.min_minutes}")
    logger.info(f"2D Risk Matrix: {'Enabled' if args.include_2d else 'Disabled'}")
    logger.info("="*80)
    
    # Initialize predictor
    logger.info("\nLoading model and data...")
    predictor = ConditionalArchetypePredictor()
    
    # Load feature dataset
    df_features = predictor.df_features.copy()
    logger.info(f"Loaded {len(df_features)} total player-seasons")
    
    # Filter for age <= max_age
    if 'AGE' not in df_features.columns:
        logger.error("AGE column not found in dataset. Cannot filter by age.")
        return
    
    df_young = df_features[df_features['AGE'] <= args.max_age].copy()
    logger.info(f"Filtered to age <= {args.max_age}: {len(df_young)} player-seasons")
    
    if len(df_young) == 0:
        logger.warning("No players found with age <= {args.max_age}")
        return
    
    # Get unique seasons
    seasons = sorted(df_young['SEASON'].unique().tolist())
    logger.info(f"Seasons in dataset: {seasons}")
    
    # Fetch minutes data if requested
    df_minutes = None
    if args.fetch_minutes:
        df_minutes = fetch_minutes_data(seasons)
    
    # Filter by minutes
    df_filtered = filter_by_minutes(df_young, df_minutes, args.min_minutes)
    
    if len(df_filtered) == 0:
        logger.warning("No players found after filtering by minutes")
        return
    
    logger.info(f"\nFinal dataset: {len(df_filtered)} player-seasons")
    
    # Run predictions
    logger.info("\nRunning predictions...")
    results = []
    
    for idx, row in tqdm(df_filtered.iterrows(), total=len(df_filtered), desc="Predicting"):
        try:
            player_name = row.get('PLAYER_NAME', 'Unknown')
            season = row.get('SEASON', 'Unknown')
            age = row.get('AGE', None)
            current_usage = row.get('USG_PCT', None)
            
            # Skip if missing critical data
            if pd.isna(current_usage) or current_usage <= 0:
                continue
            
            # Predict at current usage
            pred_current = predictor.predict_archetype_at_usage(row, current_usage)
            
            # Predict at 25% usage (standard latent star test)
            pred_25 = predictor.predict_archetype_at_usage(row, 0.25)
            
            # Predict at 30% usage (high usage test)
            pred_30 = predictor.predict_archetype_at_usage(row, 0.30)
            
            # Build result dictionary
            result = {
                'PLAYER_ID': row.get('PLAYER_ID', ''),
                'PLAYER_NAME': player_name,
                'SEASON': season,
                'AGE': age,
                'RS_USG_PCT': current_usage,
                
                # Current usage predictions
                'CURRENT_ARCHETYPE': pred_current['predicted_archetype'],
                'CURRENT_STAR_LEVEL': pred_current['star_level_potential'],
                'CURRENT_KING_PROB': pred_current['probabilities'].get('King (Resilient Star)', 0),
                'CURRENT_BULLDOZER_PROB': pred_current['probabilities'].get('Bulldozer (Fragile Star)', 0),
                'CURRENT_SNIPER_PROB': pred_current['probabilities'].get('Sniper (Resilient Role)', 0),
                'CURRENT_VICTIM_PROB': pred_current['probabilities'].get('Victim (Fragile Role)', 0),
                
                # 25% usage predictions
                'AT_25_USG_ARCHETYPE': pred_25['predicted_archetype'],
                'AT_25_USG_STAR_LEVEL': pred_25['star_level_potential'],
                'AT_25_USG_KING_PROB': pred_25['probabilities'].get('King (Resilient Star)', 0),
                'AT_25_USG_BULLDOZER_PROB': pred_25['probabilities'].get('Bulldozer (Fragile Star)', 0),
                'AT_25_USG_SNIPER_PROB': pred_25['probabilities'].get('Sniper (Resilient Role)', 0),
                'AT_25_USG_VICTIM_PROB': pred_25['probabilities'].get('Victim (Fragile Role)', 0),
                
                # 30% usage predictions
                'AT_30_USG_ARCHETYPE': pred_30['predicted_archetype'],
                'AT_30_USG_STAR_LEVEL': pred_30['star_level_potential'],
                'AT_30_USG_KING_PROB': pred_30['probabilities'].get('King (Resilient Star)', 0),
                'AT_30_USG_BULLDOZER_PROB': pred_30['probabilities'].get('Bulldozer (Fragile Star)', 0),
                'AT_30_USG_SNIPER_PROB': pred_30['probabilities'].get('Sniper (Resilient Role)', 0),
                'AT_30_USG_VICTIM_PROB': pred_30['probabilities'].get('Victim (Fragile Role)', 0),
                
                # Key stress vectors for analysis
                'CREATION_VOLUME_RATIO': row.get('CREATION_VOLUME_RATIO', None),
                'CREATION_TAX': row.get('CREATION_TAX', None),
                'LEVERAGE_USG_DELTA': row.get('LEVERAGE_USG_DELTA', None),
                'LEVERAGE_TS_DELTA': row.get('LEVERAGE_TS_DELTA', None),
                'RS_PRESSURE_APPETITE': row.get('RS_PRESSURE_APPETITE', None),
                'RS_PRESSURE_RESILIENCE': row.get('RS_PRESSURE_RESILIENCE', None),
                'RIM_PRESSURE_RESILIENCE': row.get('RIM_PRESSURE_RESILIENCE', None),
                'RS_RIM_APPETITE': row.get('RS_RIM_APPETITE', None),
                'EFG_ISO_WEIGHTED': row.get('EFG_ISO_WEIGHTED', None),
                'EFG_PCT_0_DRIBBLE': row.get('EFG_PCT_0_DRIBBLE', None),
            }
            
            # Add minutes data if available
            if 'MIN' in row.index and pd.notna(row['MIN']):
                result['MINUTES'] = row['MIN']
            if 'GP' in row.index and pd.notna(row['GP']):
                result['GAMES_PLAYED'] = row['GP']
            
            # Add 2D Risk Matrix predictions if requested
            if args.include_2d:
                try:
                    risk_pred = predictor.predict_with_risk_matrix(row, current_usage)
                    result['PERFORMANCE_SCORE'] = risk_pred.get('performance_score', None)
                    result['DEPENDENCE_SCORE'] = risk_pred.get('dependence_score', None)
                    result['RISK_CATEGORY'] = risk_pred.get('risk_category', None)
                    
                    # Add dependence components
                    dep_details = risk_pred.get('dependence_details', {})
                    if dep_details:
                        result['ASSISTED_FGM_PCT'] = dep_details.get('assisted_fgm_pct', None)
                        result['OPEN_SHOT_FREQUENCY'] = dep_details.get('open_shot_frequency', None)
                        result['SELF_CREATED_USAGE_RATIO'] = dep_details.get('self_created_usage_ratio', None)
                except Exception as e:
                    logger.debug(f"Error calculating 2D risk matrix for {player_name} {season}: {e}")
                    result['PERFORMANCE_SCORE'] = None
                    result['DEPENDENCE_SCORE'] = None
                    result['RISK_CATEGORY'] = None
            
            results.append(result)
            
            # Progress logging
            if len(results) % args.batch_size == 0:
                logger.info(f"Processed {len(results)} player-seasons...")
                
        except Exception as e:
            logger.warning(f"Error processing {row.get('PLAYER_NAME', 'Unknown')} {row.get('SEASON', 'Unknown')}: {e}")
            continue
    
    # Create results DataFrame
    df_results = pd.DataFrame(results)
    
    if len(df_results) == 0:
        logger.warning("No results generated")
        return
    
    # Sort by star-level potential at 25% usage (descending)
    df_results = df_results.sort_values('AT_25_USG_STAR_LEVEL', ascending=False).reset_index(drop=True)
    df_results['RANK'] = range(1, len(df_results) + 1)
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_results.to_csv(output_path, index=False)
    logger.info(f"\nResults saved to: {output_path}")
    logger.info(f"Total player-seasons analyzed: {len(df_results)}")
    
    # Print summary statistics
    logger.info("\n" + "="*80)
    logger.info("SUMMARY STATISTICS")
    logger.info("="*80)
    
    logger.info(f"\nAge Distribution:")
    logger.info(df_results['AGE'].describe())
    
    logger.info(f"\nCurrent Usage Distribution:")
    logger.info(df_results['RS_USG_PCT'].describe())
    
    logger.info(f"\nStar-Level Potential at 25% Usage:")
    logger.info(df_results['AT_25_USG_STAR_LEVEL'].describe())
    
    if args.include_2d and 'PERFORMANCE_SCORE' in df_results.columns:
        logger.info(f"\nPerformance Score Distribution:")
        logger.info(df_results['PERFORMANCE_SCORE'].describe())
        
        logger.info(f"\nDependence Score Distribution:")
        logger.info(df_results['DEPENDENCE_SCORE'].describe())
        
        logger.info(f"\nRisk Category Distribution:")
        logger.info(df_results['RISK_CATEGORY'].value_counts())
    
    logger.info(f"\nTop 20 Players by Star-Level Potential at 25% Usage:")
    top_20 = df_results.head(20)[['PLAYER_NAME', 'SEASON', 'AGE', 'RS_USG_PCT', 
                                    'AT_25_USG_ARCHETYPE', 'AT_25_USG_STAR_LEVEL']]
    for idx, row in top_20.iterrows():
        logger.info(f"  {row['PLAYER_NAME']} ({row['SEASON']}) - Age {row['AGE']:.0f}, "
                   f"RS Usage {row['RS_USG_PCT']*100:.1f}% → {row['AT_25_USG_ARCHETYPE']} "
                   f"({row['AT_25_USG_STAR_LEVEL']:.2%})")
    
    logger.info(f"\nArchetype Distribution at Current Usage:")
    logger.info(df_results['CURRENT_ARCHETYPE'].value_counts())
    
    logger.info(f"\nArchetype Distribution at 25% Usage:")
    logger.info(df_results['AT_25_USG_ARCHETYPE'].value_counts())
    
    logger.info(f"\nArchetype Distribution at 30% Usage:")
    logger.info(df_results['AT_30_USG_ARCHETYPE'].value_counts())
    
    logger.info("\n" + "="*80)
    logger.info("Analysis complete!")
    logger.info("="*80)


if __name__ == "__main__":
    main()

