"""
Test Universal Projection Implementation on Known Cases

Tests Brunson and Maxey at different usage levels to validate that
features are being projected correctly (not just USG_PCT).
"""

import pandas as pd
import sys
from pathlib import Path
import logging

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_universal_projection():
    """Test universal projection on Brunson and Maxey at different usage levels."""
    
    predictor = ConditionalArchetypePredictor(use_rfe_model=True)
    
    test_cases = [
        {
            'name': 'Jalen Brunson',
            'season': '2020-21',
            'actual_usage': 0.196,
            'test_usage_levels': [0.20, 0.25, 0.30, 0.32, 0.35],
            'expected_at_30': 'High (>70%)',
            'context': 'Backup to Luka Dončić. Should show high star-level when projected to 30%+ usage.'
        },
        {
            'name': 'Tyrese Maxey',
            'season': '2021-22',
            'actual_usage': 0.199,
            'test_usage_levels': [0.20, 0.25, 0.28, 0.30, 0.32],
            'expected_at_30': 'High (>70%)',
            'context': 'Elite Creation Vector and Leverage Vector even at lower usage.'
        }
    ]
    
    print("=" * 80)
    print("UNIVERSAL PROJECTION VALIDATION TEST")
    print("=" * 80)
    print()
    
    for case in test_cases:
        player_name = case['name']
        season = case['season']
        actual_usage = case['actual_usage']
        
        print(f"\n{'=' * 80}")
        print(f"Testing: {player_name} ({season})")
        print(f"Actual Usage: {actual_usage * 100:.1f}%")
        print(f"Context: {case['context']}")
        print(f"{'=' * 80}\n")
        
        # Get player data
        player_data = predictor.get_player_data(player_name, season)
        if player_data is None:
            print(f"❌ No data found for {player_name} {season}")
            continue
        
        # Get current feature values
        current_creation_vol = player_data.get('CREATION_VOLUME_RATIO', None)
        current_leverage_usg = player_data.get('LEVERAGE_USG_DELTA', None)
        current_pressure_app = player_data.get('RS_PRESSURE_APPETITE', None)
        
        print(f"Current Feature Values:")
        print(f"  CREATION_VOLUME_RATIO: {current_creation_vol:.4f}" if pd.notna(current_creation_vol) else "  CREATION_VOLUME_RATIO: N/A")
        print(f"  LEVERAGE_USG_DELTA: {current_leverage_usg:.4f}" if pd.notna(current_leverage_usg) else "  LEVERAGE_USG_DELTA: N/A")
        print(f"  RS_PRESSURE_APPETITE: {current_pressure_app:.4f}" if pd.notna(current_pressure_app) else "  RS_PRESSURE_APPETITE: N/A")
        print()
        
        # Test at different usage levels
        results = []
        for test_usage in case['test_usage_levels']:
            pred = predictor.predict_archetype_at_usage(player_data, test_usage)
            
            # Get projected feature values (by preparing features and inspecting)
            features, metadata = predictor.prepare_features(player_data, test_usage)
            
            # Extract projected values from metadata or calculate
            projection_factor = test_usage / actual_usage if actual_usage > 0 else 1.0
            
            # Check if empirical projection was used
            target_bucket = predictor._get_usage_bucket(test_usage)
            if target_bucket:
                bucket_stats = predictor.usage_buckets[target_bucket]['stats']
                empirical_creation_vol = bucket_stats.get('median_creation_vol', None)
            else:
                empirical_creation_vol = None
            
            results.append({
                'usage': test_usage,
                'archetype': pred['predicted_archetype'],
                'star_level': pred['star_level_potential'],
                'projection_factor': projection_factor,
                'empirical_bucket': target_bucket,
                'empirical_median_creation_vol': empirical_creation_vol
            })
            
            print(f"Usage: {test_usage * 100:.1f}%")
            print(f"  Predicted: {pred['predicted_archetype']}")
            print(f"  Star-Level: {pred['star_level_potential'] * 100:.2f}%")
            print(f"  Projection Factor: {projection_factor:.2f}x")
            if target_bucket:
                print(f"  Empirical Bucket: {target_bucket}")
                if empirical_creation_vol:
                    print(f"  Bucket Median CREATION_VOLUME_RATIO: {empirical_creation_vol:.4f}")
            print()
        
        # Summary
        print(f"\nSummary for {player_name}:")
        print(f"  Expected at 30% usage: {case['expected_at_30']}")
        pred_30 = next((r for r in results if abs(r['usage'] - 0.30) < 0.01), None)
        if pred_30:
            star_level_30 = pred_30['star_level'] * 100
            if star_level_30 >= 70:
                print(f"  ✅ PASS: {star_level_30:.2f}% at 30% usage")
            else:
                print(f"  ❌ FAIL: {star_level_30:.2f}% at 30% usage (expected ≥70%)")
        print()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_universal_projection()

