"""
Test Conditional Predictions on Known Cases

This script validates that the usage-aware model correctly predicts:
1. Known breakouts at low usage (should predict low star-level)
2. Known breakouts at high usage (should predict high star-level)
3. Known Kings at different usage levels
4. Known non-stars (should have low star-level at all usage levels)
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from predict_conditional_archetype import ConditionalArchetypePredictor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_known_cases():
    """Test conditional predictions on known cases."""
    predictor = ConditionalArchetypePredictor()
    
    test_cases = [
        # Known Breakouts - Test at low usage (pre-breakout) and high usage (post-breakout)
        {
            'name': 'Jalen Brunson',
            'season': '2020-21',
            'category': 'Known Breakout',
            'actual_usage': 0.196,
            'breakout_usage': 0.266,
            'expected_low_usage': 'Victim or Sniper',
            'expected_high_usage': 'King or Bulldozer',
            'test_usage_levels': [0.15, 0.20, 0.25, 0.28, 0.32]
        },
        {
            'name': 'Tyrese Haliburton',
            'season': '2020-21',
            'category': 'Known Breakout',
            'actual_usage': 0.175,
            'breakout_usage': 0.239,
            'expected_low_usage': 'Sniper or Victim',
            'expected_high_usage': 'King or Bulldozer',
            'test_usage_levels': [0.15, 0.20, 0.25, 0.28, 0.32]
        },
        {
            'name': 'Tyrese Maxey',
            'season': '2020-21',
            'category': 'Known Breakout',
            'actual_usage': 0.222,
            'breakout_usage': 0.273,
            'expected_low_usage': 'Sniper or Victim',
            'expected_high_usage': 'King or Bulldozer',
            'test_usage_levels': [0.15, 0.20, 0.25, 0.28, 0.32]
        },
        # Known Kings - Should have high star-level at all usage levels
        {
            'name': 'Nikola Jokić',
            'season': '2022-23',
            'category': 'Known King',
            'actual_usage': 0.263,
            'expected_high_usage': 'King or Bulldozer',
            'test_usage_levels': [0.20, 0.25, 0.30, 0.35]
        },
        {
            'name': 'Giannis Antetokounmpo',
            'season': '2020-21',
            'category': 'Known King',
            'actual_usage': 0.320,
            'expected_high_usage': 'King or Bulldozer',
            'test_usage_levels': [0.20, 0.25, 0.30, 0.35]
        },
        # Known Non-Stars - Should have low star-level at all usage levels
        {
            'name': 'Ben Simmons',
            'season': '2020-21',
            'category': 'Known Non-Star',
            'actual_usage': 0.200,
            'expected_all_usage': 'Victim or Sniper',
            'test_usage_levels': [0.15, 0.20, 0.25, 0.30]
        },
        {
            'name': 'T.J. McConnell',
            'season': '2020-21',
            'category': 'Known Non-Star',
            'actual_usage': 0.149,
            'expected_all_usage': 'Victim or Sniper',
            'test_usage_levels': [0.15, 0.20, 0.25, 0.30]
        }
    ]
    
    results = []
    
    for case in test_cases:
        logger.info(f"\n{'='*80}")
        logger.info(f"Testing: {case['name']} ({case['season']}) - {case['category']}")
        logger.info(f"{'='*80}")
        
        player_data = predictor.get_player_data(case['name'], case['season'])
        if player_data is None:
            logger.warning(f"  No data found - skipping")
            continue
        
        actual_usage = case.get('actual_usage', None)
        if actual_usage:
            logger.info(f"  Actual Usage: {actual_usage*100:.1f}%")
        
        # Test at multiple usage levels
        usage_levels = case['test_usage_levels']
        predictions_df = predictor.predict_at_multiple_usage_levels(player_data, usage_levels)
        
        logger.info(f"\n  Predictions at Different Usage Levels:")
        for _, row in predictions_df.iterrows():
            logger.info(f"    {row['usage_level_pct']:.1f}% usage: {row['predicted_archetype']} "
                       f"(Star-Level: {row['star_level_potential']:.2%})")
        
        # Store results
        for _, row in predictions_df.iterrows():
            results.append({
                'player_name': case['name'],
                'season': case['season'],
                'category': case['category'],
                'actual_usage': actual_usage * 100 if actual_usage else None,
                'test_usage': row['usage_level_pct'],
                'predicted_archetype': row['predicted_archetype'],
                'star_level_potential': row['star_level_potential'],
                'king_prob': row['king_prob'],
                'bulldozer_prob': row['bulldozer_prob'],
                'sniper_prob': row['sniper_prob'],
                'victim_prob': row['victim_prob']
            })
        
        # Validate expectations
        logger.info(f"\n  Validation:")
        
        if case['category'] == 'Known Breakout':
            # At low usage, should predict low star-level
            low_usage_pred = predictions_df[predictions_df['usage_level_pct'] <= case['actual_usage']*100]
            if len(low_usage_pred) > 0:
                avg_star_low = low_usage_pred['star_level_potential'].mean()
                logger.info(f"    At low usage (≤{case['actual_usage']*100:.1f}%): Avg Star-Level = {avg_star_low:.2%}")
                if avg_star_low < 0.30:
                    logger.info(f"    ✅ PASS: Low star-level at low usage (expected)")
                else:
                    logger.warning(f"    ⚠️  WARNING: Higher than expected star-level at low usage")
            
            # At high usage (breakout level), should predict high star-level
            breakout_usage = case.get('breakout_usage', None)
            if breakout_usage:
                high_usage_pred = predictions_df[predictions_df['usage_level_pct'] >= breakout_usage*100]
                if len(high_usage_pred) > 0:
                    avg_star_high = high_usage_pred['star_level_potential'].mean()
                    logger.info(f"    At high usage (≥{breakout_usage*100:.1f}%): Avg Star-Level = {avg_star_high:.2%}")
                    if avg_star_high > 0.50:
                        logger.info(f"    ✅ PASS: High star-level at high usage (expected)")
                    else:
                        logger.warning(f"    ⚠️  WARNING: Lower than expected star-level at high usage")
        
        elif case['category'] == 'Known King':
            # Should have high star-level at all usage levels
            avg_star = predictions_df['star_level_potential'].mean()
            logger.info(f"    Avg Star-Level across all usage levels: {avg_star:.2%}")
            if avg_star > 0.70:
                logger.info(f"    ✅ PASS: High star-level at all usage levels (expected)")
            else:
                logger.warning(f"    ⚠️  WARNING: Lower than expected star-level")
        
        elif case['category'] == 'Known Non-Star':
            # Should have low star-level at all usage levels
            avg_star = predictions_df['star_level_potential'].mean()
            logger.info(f"    Avg Star-Level across all usage levels: {avg_star:.2%}")
            if avg_star < 0.20:
                logger.info(f"    ✅ PASS: Low star-level at all usage levels (expected)")
            else:
                logger.warning(f"    ⚠️  WARNING: Higher than expected star-level")
    
    # Save results
    df_results = pd.DataFrame(results)
    output_path = Path("results") / "conditional_predictions_validation.csv"
    df_results.to_csv(output_path, index=False)
    logger.info(f"\n{'='*80}")
    logger.info(f"Results saved to {output_path}")
    logger.info(f"{'='*80}")
    
    # Summary statistics
    logger.info(f"\nSummary Statistics:")
    logger.info(f"  Total test cases: {len(test_cases)}")
    logger.info(f"  Total predictions: {len(df_results)}")
    
    # Check if predictions change with usage
    logger.info(f"\nPrediction Variability (do predictions change with usage?):")
    for player in df_results['player_name'].unique():
        player_data = df_results[df_results['player_name'] == player]
        unique_archetypes = player_data['predicted_archetype'].nunique()
        star_range = player_data['star_level_potential'].max() - player_data['star_level_potential'].min()
        logger.info(f"  {player}: {unique_archetypes} unique archetypes, star-level range: {star_range:.2%}")
        if star_range > 0.10:
            logger.info(f"    ✅ Predictions change with usage (range: {star_range:.2%})")
        else:
            logger.warning(f"    ⚠️  Predictions don't change much with usage (range: {star_range:.2%})")
    
    return df_results


if __name__ == "__main__":
    results = test_known_cases()

