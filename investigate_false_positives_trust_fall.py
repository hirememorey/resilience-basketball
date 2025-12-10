"""
Investigate False Positives in Trust Fall 2.1

This script analyzes why false positives still fail without gates, focusing on:
1. Feature values for failing false positives
2. INEFFICIENT_VOLUME_SCORE values (enhanced multi-signal)
3. Why the model isn't learning the pattern
4. Comparison with passing false positives
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# False Positive cases from Trust Fall 2.1 results
FALSE_POSITIVE_CASES = [
    ("Jordan Poole", "2021-22", 0.30, True),  # PASSES
    ("Talen Horton-Tucker", "2020-21", 0.25, True),  # PASSES
    ("Christian Wood", "2020-21", 0.26, False),  # FAILS
    ("D'Angelo Russell", "2018-19", 0.31, False),  # FAILS
    ("Julius Randle", "2020-21", 0.30, False),  # FAILS
]

def analyze_false_positive(predictor, player_name, season, test_usage, passes):
    """Analyze a single false positive case."""
    logger.info("=" * 80)
    logger.info(f"Analyzing: {player_name} ({season}) - {'PASSES' if passes else 'FAILS'}")
    logger.info("=" * 80)
    
    # Get player data
    player_data = predictor.get_player_data(player_name, season)
    if player_data is None:
        logger.warning(f"  No data found for {player_name} ({season})")
        return None
    
    # Get feature values
    features = {
        'USG_PCT': player_data.get('USG_PCT', np.nan),
        'CREATION_VOLUME_RATIO': player_data.get('CREATION_VOLUME_RATIO', np.nan),
        'CREATION_TAX': player_data.get('CREATION_TAX', np.nan),
        'SHOT_QUALITY_GENERATION_DELTA': player_data.get('SHOT_QUALITY_GENERATION_DELTA', np.nan),
        'LEVERAGE_TS_DELTA': player_data.get('LEVERAGE_TS_DELTA', np.nan),
        'EFG_ISO_WEIGHTED': player_data.get('EFG_ISO_WEIGHTED', np.nan),
    }
    
    # Calculate enhanced INEFFICIENT_VOLUME_SCORE manually
    creation_vol = features['CREATION_VOLUME_RATIO'] if pd.notna(features['CREATION_VOLUME_RATIO']) else 0.0
    creation_tax = features['CREATION_TAX'] if pd.notna(features['CREATION_TAX']) else 0.0
    sq_delta = features['SHOT_QUALITY_GENERATION_DELTA'] if pd.notna(features['SHOT_QUALITY_GENERATION_DELTA']) else 0.0
    leverage_ts = features['LEVERAGE_TS_DELTA'] if pd.notna(features['LEVERAGE_TS_DELTA']) else 0.0
    usg_pct = test_usage
    
    # Normalize USG_PCT if needed
    if usg_pct > 1.0:
        usg_pct = usg_pct / 100.0
    
    # Multi-signal inefficiency
    negative_tax_magnitude = max(0, -creation_tax) if pd.notna(creation_tax) else 0.0
    negative_sq_magnitude = max(0, -sq_delta) if pd.notna(sq_delta) else 0.0
    negative_leverage_magnitude = max(0, -leverage_ts) if pd.notna(leverage_ts) else 0.0
    
    combined_inefficiency = negative_tax_magnitude + negative_sq_magnitude + negative_leverage_magnitude
    base_score = creation_vol * combined_inefficiency
    inefficient_volume_score = usg_pct * base_score
    
    # Get prediction without gates
    result = predictor.predict_with_risk_matrix(
        player_data,
        test_usage,
        apply_phase3_fixes=True,
        apply_hard_gates=False
    )
    
    # Get model probabilities
    feature_vector, metadata = predictor.prepare_features(
        player_data,
        test_usage,
        apply_phase3_fixes=True,
        apply_hard_gates=False
    )
    
    # Get INEFFICIENT_VOLUME_SCORE from risk features
    risk_features = predictor._calculate_risk_features(player_data, test_usage)
    model_inefficient_score = risk_features.get('INEFFICIENT_VOLUME_SCORE', 0.0)
    
    logger.info(f"\nFeature Values:")
    logger.info(f"  USG_PCT: {features['USG_PCT']:.3f}")
    logger.info(f"  CREATION_VOLUME_RATIO: {creation_vol:.3f}")
    logger.info(f"  CREATION_TAX: {creation_tax:.4f} (negative magnitude: {negative_tax_magnitude:.4f})")
    logger.info(f"  SHOT_QUALITY_GENERATION_DELTA: {sq_delta:.4f} (negative magnitude: {negative_sq_magnitude:.4f})")
    logger.info(f"  LEVERAGE_TS_DELTA: {leverage_ts:.4f} (negative magnitude: {negative_leverage_magnitude:.4f})")
    logger.info(f"  EFG_ISO_WEIGHTED: {features['EFG_ISO_WEIGHTED']:.4f}")
    
    logger.info(f"\nINEFFICIENT_VOLUME_SCORE Calculation:")
    logger.info(f"  Combined Inefficiency: {combined_inefficiency:.4f}")
    logger.info(f"    - CREATION_TAX component: {negative_tax_magnitude:.4f}")
    logger.info(f"    - SQ_DELTA component: {negative_sq_magnitude:.4f}")
    logger.info(f"    - LEVERAGE_TS component: {negative_leverage_magnitude:.4f}")
    logger.info(f"  Base Score (Volume × Combined): {base_score:.4f}")
    logger.info(f"  Final Score (Usage × Base): {inefficient_volume_score:.4f}")
    logger.info(f"  Model's INEFFICIENT_VOLUME_SCORE: {model_inefficient_score:.4f}")
    
    logger.info(f"\nPrediction (No Gates):")
    logger.info(f"  Performance Score: {result['performance_score']:.2%}")
    logger.info(f"  Predicted Archetype: {result['archetype']}")
    logger.info(f"  Risk Category: {result['risk_category']}")
    
    # Get model feature importance for INEFFICIENT_VOLUME_SCORE
    if hasattr(predictor.model, 'feature_importances_'):
        feature_names = predictor.model.feature_names_in_
        if 'INEFFICIENT_VOLUME_SCORE' in feature_names:
            idx = list(feature_names).index('INEFFICIENT_VOLUME_SCORE')
            importance = predictor.model.feature_importances_[idx]
            logger.info(f"\nModel Feature Importance:")
            logger.info(f"  INEFFICIENT_VOLUME_SCORE importance: {importance:.4f} ({importance*100:.2f}%)")
    
    return {
        'player_name': player_name,
        'season': season,
        'passes': passes,
        'performance_score': result['performance_score'],
        'inefficient_volume_score': inefficient_volume_score,
        'model_inefficient_score': model_inefficient_score,
        'combined_inefficiency': combined_inefficiency,
        'negative_tax_magnitude': negative_tax_magnitude,
        'negative_sq_magnitude': negative_sq_magnitude,
        'negative_leverage_magnitude': negative_leverage_magnitude,
        'creation_vol': creation_vol,
        'usg_pct': usg_pct,
        'features': features,
    }

def main():
    """Main analysis function."""
    logger.info("=" * 80)
    logger.info("False Positive Trust Fall 2.1 Investigation")
    logger.info("=" * 80)
    
    # Initialize predictor
    predictor = ConditionalArchetypePredictor()
    
    results = []
    for player_name, season, test_usage, passes in FALSE_POSITIVE_CASES:
        result = analyze_false_positive(predictor, player_name, season, test_usage, passes)
        if result:
            results.append(result)
    
    # Compare passing vs failing cases
    logger.info("\n" + "=" * 80)
    logger.info("COMPARISON: Passing vs Failing False Positives")
    logger.info("=" * 80)
    
    passing = [r for r in results if r['passes']]
    failing = [r for r in results if not r['passes']]
    
    logger.info(f"\nPassing Cases ({len(passing)}):")
    for r in passing:
        logger.info(f"  {r['player_name']} ({r['season']}): Score={r['inefficient_volume_score']:.4f}, Performance={r['performance_score']:.2%}")
    
    logger.info(f"\nFailing Cases ({len(failing)}):")
    for r in failing:
        logger.info(f"  {r['player_name']} ({r['season']}): Score={r['inefficient_volume_score']:.4f}, Performance={r['performance_score']:.2%}")
    
    # Statistical comparison
    if passing and failing:
        passing_scores = [r['inefficient_volume_score'] for r in passing]
        failing_scores = [r['inefficient_volume_score'] for r in failing]
        
        logger.info(f"\nStatistical Comparison:")
        logger.info(f"  Passing Cases - Mean Score: {np.mean(passing_scores):.4f}, Median: {np.median(passing_scores):.4f}")
        logger.info(f"  Failing Cases - Mean Score: {np.mean(failing_scores):.4f}, Median: {np.median(failing_scores):.4f}")
        logger.info(f"  Difference: {np.mean(failing_scores) - np.mean(passing_scores):.4f}")
        
        # Component analysis
        logger.info(f"\nComponent Analysis:")
        for component in ['negative_tax_magnitude', 'negative_sq_magnitude', 'negative_leverage_magnitude']:
            passing_vals = [r[component] for r in passing]
            failing_vals = [r[component] for r in failing]
            logger.info(f"  {component}:")
            logger.info(f"    Passing: {np.mean(passing_vals):.4f} (mean), {np.median(passing_vals):.4f} (median)")
            logger.info(f"    Failing: {np.mean(failing_vals):.4f} (mean), {np.median(failing_vals):.4f} (median)")
    
    # Save results
    df_results = pd.DataFrame(results)
    output_path = Path("results") / "false_positives_trust_fall_analysis.csv"
    df_results.to_csv(output_path, index=False)
    logger.info(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    main()
