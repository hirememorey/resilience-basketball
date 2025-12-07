"""
Test All Players Age 25 and Under

This script runs predictions for all players who had a season at age 25 or under,
allowing exploration of model behavior outside of test cases.
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging
from typing import Optional

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Run predictions for all players age 25 and under."""
    
    logger.info("="*80)
    logger.info("TESTING ALL PLAYERS AGE 25 AND UNDER")
    logger.info("="*80)
    
    # Initialize predictor
    logger.info("Loading model and data...")
    predictor = ConditionalArchetypePredictor()
    
    # Load feature dataset
    df_features = predictor.df_features.copy()
    logger.info(f"Loaded {len(df_features)} total player-seasons")
    
    # Filter for age <= 25
    if 'AGE' not in df_features.columns:
        logger.error("AGE column not found in dataset. Cannot filter by age.")
        return
    
    df_young = df_features[df_features['AGE'] <= 25].copy()
    logger.info(f"Filtered to age <= 25: {len(df_young)} player-seasons")
    
    if len(df_young) == 0:
        logger.warning("No players found with age <= 25")
        return
    
    # Get unique players
    unique_players = df_young[['PLAYER_ID', 'PLAYER_NAME']].drop_duplicates()
    logger.info(f"Found {len(unique_players)} unique players")
    
    # Run predictions
    logger.info("\nRunning predictions...")
    results = []
    
    for idx, row in df_young.iterrows():
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
            }
            
            results.append(result)
            
            # Progress logging
            if len(results) % 100 == 0:
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
    df_results = df_results.sort_values('AT_25_USG_STAR_LEVEL', ascending=False)
    
    # Save results
    output_path = Path("results/all_young_players_predictions.csv")
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


