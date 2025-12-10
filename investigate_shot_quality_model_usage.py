"""
Investigate why SHOT_QUALITY_GENERATION_DELTA isn't catching false positives.

The feature IS in the model (rank #3, 8.96% importance), but false positives persist.
This script investigates:
1. How the model is using the feature
2. Feature values for false positives vs true positives
3. Model predictions vs feature values
4. Why the model isn't learning to use it effectively
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging
import json
import joblib

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor
from test_latent_star_cases import get_test_cases

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_model_info():
    """Load model and feature information."""
    model_path = Path("models/resilience_xgb_rfe_10.pkl")
    metadata_path = Path("results/rfe_model_results_10.json")
    
    model = joblib.load(model_path)
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    feature_names = list(model.feature_names_in_) if hasattr(model, 'feature_names_in_') else metadata['features']
    
    # Get feature importance
    feature_importance = {}
    for feat_info in metadata['feature_importance']:
        feature_importance[feat_info['Feature']] = feat_info['Importance']
    
    return model, feature_names, feature_importance, metadata


def analyze_feature_usage():
    """Analyze how SHOT_QUALITY_GENERATION_DELTA is being used."""
    
    logger.info("=" * 100)
    logger.info("INVESTIGATING SHOT_QUALITY_GENERATION_DELTA MODEL USAGE")
    logger.info("=" * 100)
    
    # Load model info
    model, feature_names, feature_importance, metadata = load_model_info()
    
    logger.info(f"\nModel Features ({len(feature_names)}):")
    for i, feat in enumerate(feature_names, 1):
        importance = feature_importance.get(feat, 0)
        logger.info(f"  {i}. {feat} ({importance:.2%} importance)")
    
    sq_delta_idx = feature_names.index('SHOT_QUALITY_GENERATION_DELTA') if 'SHOT_QUALITY_GENERATION_DELTA' in feature_names else None
    
    if sq_delta_idx is None:
        logger.error("SHOT_QUALITY_GENERATION_DELTA not found in model features!")
        return
    
    logger.info(f"\nSHOT_QUALITY_GENERATION_DELTA is feature #{sq_delta_idx + 1} with {feature_importance.get('SHOT_QUALITY_GENERATION_DELTA', 0):.2%} importance")
    
    # Load test cases
    predictor = ConditionalArchetypePredictor()
    test_cases = get_test_cases()
    
    # Analyze false positives
    logger.info("\n" + "=" * 100)
    logger.info("ANALYZING FALSE POSITIVES")
    logger.info("=" * 100)
    
    fp_cases = [tc for tc in test_cases if 'False Positive' in tc.category]
    
    results = []
    
    for test_case in fp_cases:
        player_data = predictor.get_player_data(test_case.name, test_case.season)
        
        if player_data is None:
            continue
        
        # Get feature value
        sq_delta = player_data.get('SHOT_QUALITY_GENERATION_DELTA', np.nan)
        
        # Get prediction
        prediction = predictor.predict_archetype_at_usage(
            player_data,
            test_case.test_usage,
            apply_phase3_fixes=True,
            apply_hard_gates=True
        )
        
        star_level = prediction.get('star_level_potential', 0)
        archetype = prediction.get('predicted_archetype', 'Unknown')
        
        # Get feature vector to see actual value used
        features, _ = predictor.prepare_features(
            player_data,
            test_case.test_usage,
            apply_phase3_fixes=True,
            apply_hard_gates=True
        )
        
        sq_delta_in_features = features[0][sq_delta_idx] if len(features[0]) > sq_delta_idx else np.nan
        
        results.append({
            'player_name': test_case.name,
            'season': test_case.season,
            'sq_delta_raw': sq_delta,
            'sq_delta_in_features': sq_delta_in_features,
            'star_level': star_level,
            'archetype': archetype,
            'expected': 'Low'
        })
        
        logger.info(f"\n{test_case.name} ({test_case.season}):")
        logger.info(f"  SHOT_QUALITY_GENERATION_DELTA (raw): {sq_delta:.4f}")
        logger.info(f"  SHOT_QUALITY_GENERATION_DELTA (in features): {sq_delta_in_features:.4f}")
        logger.info(f"  Star Level: {star_level:.2%}")
        logger.info(f"  Archetype: {archetype}")
    
    # Analyze true positives for comparison
    logger.info("\n" + "=" * 100)
    logger.info("ANALYZING TRUE POSITIVES (FOR COMPARISON)")
    logger.info("=" * 100)
    
    tp_cases = [tc for tc in test_cases if 'True Positive' in tc.category]
    
    for test_case in tp_cases:
        player_data = predictor.get_player_data(test_case.name, test_case.season)
        
        if player_data is None:
            continue
        
        sq_delta = player_data.get('SHOT_QUALITY_GENERATION_DELTA', np.nan)
        
        prediction = predictor.predict_archetype_at_usage(
            player_data,
            test_case.test_usage,
            apply_phase3_fixes=True,
            apply_hard_gates=True
        )
        
        star_level = prediction.get('star_level_potential', 0)
        archetype = prediction.get('predicted_archetype', 'Unknown')
        
        features, _ = predictor.prepare_features(
            player_data,
            test_case.test_usage,
            apply_phase3_fixes=True,
            apply_hard_gates=True
        )
        
        sq_delta_in_features = features[0][sq_delta_idx] if len(features[0]) > sq_delta_idx else np.nan
        
        results.append({
            'player_name': test_case.name,
            'season': test_case.season,
            'sq_delta_raw': sq_delta,
            'sq_delta_in_features': sq_delta_in_features,
            'star_level': star_level,
            'archetype': archetype,
            'expected': 'High'
        })
        
        logger.info(f"\n{test_case.name} ({test_case.season}):")
        logger.info(f"  SHOT_QUALITY_GENERATION_DELTA (raw): {sq_delta:.4f}")
        logger.info(f"  SHOT_QUALITY_GENERATION_DELTA (in features): {sq_delta_in_features:.4f}")
        logger.info(f"  Star Level: {star_level:.2%}")
        logger.info(f"  Archetype: {archetype}")
    
    # Summary statistics
    df_results = pd.DataFrame(results)
    df_fp = df_results[df_results['expected'] == 'Low']
    df_tp = df_results[df_results['expected'] == 'High']
    
    logger.info("\n" + "=" * 100)
    logger.info("SUMMARY STATISTICS")
    logger.info("=" * 100)
    
    logger.info(f"\nFalse Positives ({len(df_fp)}):")
    logger.info(f"  Mean SQ_DELTA (raw): {df_fp['sq_delta_raw'].mean():.4f}")
    logger.info(f"  Mean SQ_DELTA (in features): {df_fp['sq_delta_in_features'].mean():.4f}")
    logger.info(f"  Mean Star Level: {df_fp['star_level'].mean():.2%}")
    
    logger.info(f"\nTrue Positives ({len(df_tp)}):")
    logger.info(f"  Mean SQ_DELTA (raw): {df_tp['sq_delta_raw'].mean():.4f}")
    logger.info(f"  Mean SQ_DELTA (in features): {df_tp['sq_delta_in_features'].mean():.4f}")
    logger.info(f"  Mean Star Level: {df_tp['star_level'].mean():.2%}")
    
    # Check if feature values are being transformed
    logger.info("\n" + "=" * 100)
    logger.info("FEATURE TRANSFORMATION CHECK")
    logger.info("=" * 100)
    
    raw_vs_features = df_results[['sq_delta_raw', 'sq_delta_in_features']].dropna()
    if len(raw_vs_features) > 0:
        differences = raw_vs_features['sq_delta_raw'] - raw_vs_features['sq_delta_in_features']
        logger.info(f"Mean difference (raw - in_features): {differences.mean():.6f}")
        logger.info(f"Max difference: {differences.abs().max():.6f}")
        
        if differences.abs().max() > 0.0001:
            logger.warning("⚠️ Feature values are being transformed between raw and feature vector!")
        else:
            logger.info("✅ Feature values are passed through unchanged")
    
    # Save results
    output_path = Path("results/shot_quality_model_usage_analysis.csv")
    df_results.to_csv(output_path, index=False)
    logger.info(f"\n✅ Results saved to: {output_path}")
    
    # Generate insights
    logger.info("\n" + "=" * 100)
    logger.info("KEY INSIGHTS")
    logger.info("=" * 100)
    
    # Check if model is using the feature correctly
    if df_fp['sq_delta_in_features'].mean() < df_tp['sq_delta_in_features'].mean():
        logger.info("✅ Feature distinguishes categories (FP mean < TP mean)")
    else:
        logger.warning("⚠️ Feature does NOT distinguish categories (FP mean >= TP mean)")
    
    # Check if false positives with negative values are being caught
    fp_negative = df_fp[df_fp['sq_delta_in_features'] < 0]
    fp_negative_high_star = fp_negative[fp_negative['star_level'] > 0.70]
    
    logger.info(f"\nFalse Positives with negative SQ_DELTA: {len(fp_negative)}/{len(df_fp)}")
    logger.info(f"  Of those, {len(fp_negative_high_star)} still have star_level > 70%")
    
    if len(fp_negative_high_star) > 0:
        logger.warning(f"⚠️ Model is NOT using negative SQ_DELTA to penalize these cases:")
        for _, row in fp_negative_high_star.iterrows():
            logger.warning(f"  - {row['player_name']} ({row['season']}): SQ_DELTA={row['sq_delta_in_features']:.4f}, Star Level={row['star_level']:.2%}")


if __name__ == "__main__":
    analyze_feature_usage()






