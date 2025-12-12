"""
Validation Script: SHOT_QUALITY_GENERATION_DELTA Gate

This script validates the proposed SHOT_QUALITY_GENERATION_DELTA gate against
all test cases BEFORE implementing any fixes. Following the lessons learned
from the false positive investigation.

Key Questions:
1. Does SHOT_QUALITY_GENERATION_DELTA actually distinguish TPs from FPs?
2. How many TPs would the -0.02 threshold break?
3. Is ISO eFG position-dependent?
4. Is the metric already in the model? If so, why isn't it working?
5. What's the optimal threshold (if any) that catches FPs without breaking TPs?

Date: December 2025
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor
from test_latent_star_cases import get_test_cases, LatentStarTestCase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_feature_for_all_test_cases(
    feature_name: str,
    predictor: ConditionalArchetypePredictor
) -> pd.DataFrame:
    """
    Extract feature values for all test cases.
    
    Returns DataFrame with columns:
    - player_name, season, category, feature_value, data_found
    """
    test_cases = get_test_cases()
    results = []
    
    for test_case in test_cases:
        player_data = predictor.get_player_data(test_case.name, test_case.season)
        
        if player_data is None:
            results.append({
                'player_name': test_case.name,
                'season': test_case.season,
                'category': test_case.category,
                'feature_value': np.nan,
                'data_found': False
            })
            continue
        
        feature_value = player_data.get(feature_name, np.nan)
        
        results.append({
            'player_name': test_case.name,
            'season': test_case.season,
            'category': test_case.category,
            'feature_value': feature_value,
            'data_found': True
        })
    
    return pd.DataFrame(results)


def categorize_test_cases(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorize test cases into True Positive, False Positive, True Negative.
    
    Categories:
    - True Positive: "True Positive" in category
    - False Positive: "False Positive" in category
    - True Negative: "True Negative" in category
    """
    df['test_category'] = 'Unknown'
    df.loc[df['category'].str.contains('True Positive', case=False, na=False), 'test_category'] = 'True Positive'
    df.loc[df['category'].str.contains('False Positive', case=False, na=False), 'test_category'] = 'False Positive'
    df.loc[df['category'].str.contains('True Negative', case=False, na=False), 'test_category'] = 'True Negative'
    
    return df


def statistical_comparison(df: pd.DataFrame, feature_name: str) -> Dict:
    """
    Compare feature distributions across test categories.
    
    Returns dictionary with statistics for each category.
    """
    stats = {}
    
    for category in ['True Positive', 'False Positive', 'True Negative']:
        df_cat = df[df['test_category'] == category]
        df_cat_valid = df_cat[df_cat['data_found'] & df_cat['feature_value'].notna()]
        
        if len(df_cat_valid) == 0:
            stats[category] = {
                'count': 0,
                'mean': np.nan,
                'median': np.nan,
                'std': np.nan,
                'min': np.nan,
                'max': np.nan,
                'missing': len(df_cat)
            }
        else:
            stats[category] = {
                'count': len(df_cat_valid),
                'mean': df_cat_valid['feature_value'].mean(),
                'median': df_cat_valid['feature_value'].median(),
                'std': df_cat_valid['feature_value'].std(),
                'min': df_cat_valid['feature_value'].min(),
                'max': df_cat_valid['feature_value'].max(),
                'missing': len(df_cat) - len(df_cat_valid)
            }
    
    return stats


def validate_threshold(
    df: pd.DataFrame,
    feature_name: str,
    threshold: float,
    direction: str = 'below'
) -> Dict:
    """
    Validate a threshold against test cases.
    
    Args:
        df: DataFrame with test cases and feature values
        feature_name: Name of feature
        threshold: Threshold value to test
        direction: 'below' (feature < threshold) or 'above' (feature > threshold)
    
    Returns:
        Dictionary with false positive/negative rates
    """
    results = {}
    
    for category in ['True Positive', 'False Positive', 'True Negative']:
        df_cat = df[df['test_category'] == category]
        df_cat_valid = df_cat[df_cat['data_found'] & df_cat['feature_value'].notna()]
        
        if len(df_cat_valid) == 0:
            results[category] = {
                'total': 0,
                'below_threshold': 0,
                'above_threshold': 0,
                'pct_below': np.nan,
                'pct_above': np.nan
            }
            continue
        
        if direction == 'below':
            below_count = (df_cat_valid['feature_value'] < threshold).sum()
            above_count = len(df_cat_valid) - below_count
        else:
            above_count = (df_cat_valid['feature_value'] > threshold).sum()
            below_count = len(df_cat_valid) - above_count
        
        results[category] = {
            'total': len(df_cat_valid),
            'below_threshold': below_count,
            'above_threshold': above_count,
            'pct_below': below_count / len(df_cat_valid) * 100,
            'pct_above': above_count / len(df_cat_valid) * 100
        }
    
    # Calculate false negative rate (TPs that would be caught by threshold)
    if results['True Positive']['total'] > 0:
        if direction == 'below':
            false_negative_rate = results['True Positive']['below_threshold'] / results['True Positive']['total']
        else:
            false_negative_rate = results['True Positive']['above_threshold'] / results['True Positive']['total']
    else:
        false_negative_rate = np.nan
    
    # Calculate false positive catch rate (FPs that would be caught by threshold)
    if results['False Positive']['total'] > 0:
        if direction == 'below':
            fp_catch_rate = results['False Positive']['below_threshold'] / results['False Positive']['total']
        else:
            fp_catch_rate = results['False Positive']['above_threshold'] / results['False Positive']['total']
    else:
        fp_catch_rate = np.nan
    
    results['false_negative_rate'] = false_negative_rate
    results['fp_catch_rate'] = fp_catch_rate
    
    return results


def find_optimal_threshold(
    df: pd.DataFrame,
    feature_name: str,
    direction: str = 'below',
    max_false_negative_rate: float = 0.20
) -> Dict:
    """
    Find optimal threshold that maximizes FP catch rate while keeping FN rate < max_false_negative_rate.
    
    Args:
        df: DataFrame with test cases and feature values
        feature_name: Name of feature
        direction: 'below' (feature < threshold) or 'above' (feature > threshold)
        max_false_negative_rate: Maximum acceptable false negative rate
    
    Returns:
        Dictionary with optimal threshold and statistics
    """
    # Get all valid feature values
    df_valid = df[df['data_found'] & df['feature_value'].notna()].copy()
    
    if len(df_valid) == 0:
        return {'optimal_threshold': np.nan, 'fn_rate': np.nan, 'fp_catch_rate': np.nan}
    
    # Test thresholds from min to max in 0.01 steps
    min_val = df_valid['feature_value'].min()
    max_val = df_valid['feature_value'].max()
    
    thresholds = np.arange(min_val, max_val + 0.01, 0.01)
    
    best_threshold = None
    best_fp_catch_rate = 0
    best_fn_rate = 1.0
    
    for threshold in thresholds:
        results = validate_threshold(df, feature_name, threshold, direction)
        
        fn_rate = results.get('false_negative_rate', 1.0)
        fp_catch_rate = results.get('fp_catch_rate', 0.0)
        
        # Check if this threshold meets FN rate constraint and has better FP catch rate
        if not np.isnan(fn_rate) and not np.isnan(fp_catch_rate):
            if fn_rate <= max_false_negative_rate:
                if fp_catch_rate > best_fp_catch_rate:
                    best_threshold = threshold
                    best_fp_catch_rate = fp_catch_rate
                    best_fn_rate = fn_rate
    
    return {
        'optimal_threshold': best_threshold,
        'fn_rate': best_fn_rate,
        'fp_catch_rate': best_fp_catch_rate
    }


def check_position_dependency(
    df: pd.DataFrame,
    feature_name: str,
    predictor: ConditionalArchetypePredictor
) -> Dict:
    """
    Check if feature is position-dependent.
    
    Attempts to infer position from player data (if available).
    For now, we'll check if there's a correlation with other position-related features.
    """
    # Try to get position data if available
    # For now, we'll use a simple heuristic: check if feature correlates with rim pressure
    # (bigs typically have higher rim pressure)
    
    df_valid = df[df['data_found']].copy()
    
    if len(df_valid) == 0:
        return {'position_dependent': False, 'reason': 'No data available'}
    
    # Try to extract rim pressure data as proxy for position
    rim_pressure_values = []
    feature_values = []
    
    for _, row in df_valid.iterrows():
        player_data = predictor.get_player_data(row['player_name'], row['season'])
        if player_data is not None:
            rim_pressure = player_data.get('RS_RIM_APPETITE', np.nan)
            feature_val = row['feature_value']
            
            if pd.notna(rim_pressure) and pd.notna(feature_val):
                rim_pressure_values.append(rim_pressure)
                feature_values.append(feature_val)
    
    if len(rim_pressure_values) < 5:
        return {'position_dependent': False, 'reason': 'Insufficient data for correlation check'}
    
    # Calculate correlation
    correlation = np.corrcoef(rim_pressure_values, feature_values)[0, 1]
    
    # If correlation > 0.3 or < -0.3, might be position-dependent
    is_position_dependent = abs(correlation) > 0.3
    
    return {
        'position_dependent': is_position_dependent,
        'correlation_with_rim_pressure': correlation,
        'reason': f'Correlation with rim pressure: {correlation:.3f}'
    }


def check_if_metric_exists_in_model() -> Dict:
    """
    Check if SHOT_QUALITY_GENERATION_DELTA already exists in the model.
    
    Returns dictionary with information about the metric's current status.
    """
    # Check if feature exists in predictive dataset
    predictive_path = Path("results/predictive_dataset.csv")
    
    if not predictive_path.exists():
        return {
            'exists_in_dataset': False,
            'coverage': 0,
            'exists_in_model': False,
            'feature_importance': None
        }
    
    df = pd.read_csv(predictive_path)
    
    exists_in_dataset = 'SHOT_QUALITY_GENERATION_DELTA' in df.columns
    
    if exists_in_dataset:
        coverage = df['SHOT_QUALITY_GENERATION_DELTA'].notna().sum()
        coverage_pct = coverage / len(df) * 100
    else:
        coverage = 0
        coverage_pct = 0
    
    # Check model metadata for feature importance
    model_metadata_path = Path("results/rfe_model_results_10.json")
    feature_importance = None
    
    if model_metadata_path.exists():
        import json
        with open(model_metadata_path, 'r') as f:
            metadata = json.load(f)
        
        if 'feature_importance' in metadata:
            for feat_info in metadata['feature_importance']:
                if 'SHOT_QUALITY_GENERATION_DELTA' in feat_info.get('feature', ''):
                    feature_importance = feat_info.get('importance', None)
                    break
    
    return {
        'exists_in_dataset': exists_in_dataset,
        'coverage': coverage,
        'coverage_pct': coverage_pct,
        'exists_in_model': feature_importance is not None,
        'feature_importance': feature_importance
    }


def main():
    """Run comprehensive validation of SHOT_QUALITY_GENERATION_DELTA gate."""
    
    logger.info("=" * 100)
    logger.info("SHOT_QUALITY_GENERATION_DELTA GATE VALIDATION")
    logger.info("=" * 100)
    
    predictor = ConditionalArchetypePredictor()
    
    # Step 1: Check if metric already exists
    logger.info("\n" + "=" * 100)
    logger.info("STEP 1: Check if Metric Already Exists")
    logger.info("=" * 100)
    
    metric_status = check_if_metric_exists_in_model()
    logger.info(f"Exists in dataset: {metric_status['exists_in_dataset']}")
    logger.info(f"Coverage: {metric_status['coverage']} ({metric_status['coverage_pct']:.1f}%)")
    logger.info(f"Exists in model: {metric_status['exists_in_model']}")
    if metric_status['feature_importance']:
        logger.info(f"Feature importance: {metric_status['feature_importance']:.2%}")
    
    # Step 2: Extract feature values for all test cases
    logger.info("\n" + "=" * 100)
    logger.info("STEP 2: Extract Feature Values for All Test Cases")
    logger.info("=" * 100)
    
    df_features = extract_feature_for_all_test_cases('SHOT_QUALITY_GENERATION_DELTA', predictor)
    df_features = categorize_test_cases(df_features)
    
    logger.info(f"Total test cases: {len(df_features)}")
    logger.info(f"Data found: {df_features['data_found'].sum()}")
    logger.info(f"Feature values available: {df_features[df_features['data_found']]['feature_value'].notna().sum()}")
    
    # Also extract related features for context
    logger.info("\nExtracting related features for context...")
    df_creation_vol = extract_feature_for_all_test_cases('CREATION_VOLUME_RATIO', predictor)
    df_creation_tax = extract_feature_for_all_test_cases('CREATION_TAX', predictor)
    df_efg_iso = extract_feature_for_all_test_cases('EFG_ISO_WEIGHTED', predictor)
    df_usg = extract_feature_for_all_test_cases('USG_PCT', predictor)
    
    # Merge related features
    df_features = df_features.merge(
        df_creation_vol[['player_name', 'season', 'feature_value']].rename(columns={'feature_value': 'CREATION_VOLUME_RATIO'}),
        on=['player_name', 'season'],
        how='left'
    )
    df_features = df_features.merge(
        df_creation_tax[['player_name', 'season', 'feature_value']].rename(columns={'feature_value': 'CREATION_TAX'}),
        on=['player_name', 'season'],
        how='left'
    )
    df_features = df_features.merge(
        df_efg_iso[['player_name', 'season', 'feature_value']].rename(columns={'feature_value': 'EFG_ISO_WEIGHTED'}),
        on=['player_name', 'season'],
        how='left'
    )
    df_features = df_features.merge(
        df_usg[['player_name', 'season', 'feature_value']].rename(columns={'feature_value': 'USG_PCT'}),
        on=['player_name', 'season'],
        how='left'
    )
    
    # Step 3: Statistical comparison
    logger.info("\n" + "=" * 100)
    logger.info("STEP 3: Statistical Comparison Across Categories")
    logger.info("=" * 100)
    
    stats = statistical_comparison(df_features, 'SHOT_QUALITY_GENERATION_DELTA')
    
    for category, category_stats in stats.items():
        logger.info(f"\n{category}:")
        logger.info(f"  Count: {category_stats['count']}")
        if category_stats['count'] > 0:
            logger.info(f"  Mean: {category_stats['mean']:.4f}")
            logger.info(f"  Median: {category_stats['median']:.4f}")
            logger.info(f"  Std: {category_stats['std']:.4f}")
            logger.info(f"  Range: [{category_stats['min']:.4f}, {category_stats['max']:.4f}]")
        logger.info(f"  Missing: {category_stats['missing']}")
    
    # Step 4: Validate proposed threshold (-0.02)
    logger.info("\n" + "=" * 100)
    logger.info("STEP 4: Validate Proposed Threshold (-0.02)")
    logger.info("=" * 100)
    
    proposed_threshold = -0.02
    threshold_results = validate_threshold(df_features, 'SHOT_QUALITY_GENERATION_DELTA', proposed_threshold, 'below')
    
    logger.info(f"\nProposed threshold: {proposed_threshold}")
    logger.info(f"\nTrue Positives:")
    logger.info(f"  Total: {threshold_results['True Positive']['total']}")
    logger.info(f"  Below threshold: {threshold_results['True Positive']['below_threshold']} ({threshold_results['True Positive']['pct_below']:.1f}%)")
    logger.info(f"  False Negative Rate: {threshold_results['false_negative_rate']:.2%}")
    
    logger.info(f"\nFalse Positives:")
    logger.info(f"  Total: {threshold_results['False Positive']['total']}")
    logger.info(f"  Below threshold: {threshold_results['False Positive']['below_threshold']} ({threshold_results['False Positive']['pct_below']:.1f}%)")
    logger.info(f"  FP Catch Rate: {threshold_results['fp_catch_rate']:.2%}")
    
    if threshold_results['false_negative_rate'] > 0.20:
        logger.warning(f"⚠️ WARNING: Proposed threshold would break {threshold_results['false_negative_rate']:.1%} of true positives!")
    
    # Step 5: Find optimal threshold
    logger.info("\n" + "=" * 100)
    logger.info("STEP 5: Find Optimal Threshold")
    logger.info("=" * 100)
    
    optimal = find_optimal_threshold(df_features, 'SHOT_QUALITY_GENERATION_DELTA', 'below', max_false_negative_rate=0.20)
    
    if optimal['optimal_threshold'] is not None:
        logger.info(f"Optimal threshold: {optimal['optimal_threshold']:.4f}")
        logger.info(f"False Negative Rate: {optimal['fn_rate']:.2%}")
        logger.info(f"FP Catch Rate: {optimal['fp_catch_rate']:.2%}")
    else:
        logger.warning("⚠️ No optimal threshold found that meets constraints!")
    
    # Step 6: Check position dependency
    logger.info("\n" + "=" * 100)
    logger.info("STEP 6: Check Position Dependency")
    logger.info("=" * 100)
    
    position_check = check_position_dependency(df_features, 'SHOT_QUALITY_GENERATION_DELTA', predictor)
    logger.info(f"Position dependent: {position_check['position_dependent']}")
    logger.info(f"Reason: {position_check['reason']}")
    
    # Step 7: Detailed analysis of test cases
    logger.info("\n" + "=" * 100)
    logger.info("STEP 7: Detailed Analysis of Test Cases")
    logger.info("=" * 100)
    
    # Show cases that would be affected by proposed threshold
    df_valid = df_features[df_features['data_found'] & df_features['feature_value'].notna()].copy()
    
    logger.info("\nTrue Positives that would be caught by threshold (< -0.02):")
    tp_below = df_valid[
        (df_valid['test_category'] == 'True Positive') & 
        (df_valid['feature_value'] < proposed_threshold)
    ]
    if len(tp_below) > 0:
        for _, row in tp_below.iterrows():
            logger.info(f"  {row['player_name']} ({row['season']}): {row['feature_value']:.4f}")
    else:
        logger.info("  None")
    
    logger.info("\nFalse Positives that would be caught by threshold (< -0.02):")
    fp_below = df_valid[
        (df_valid['test_category'] == 'False Positive') & 
        (df_valid['feature_value'] < proposed_threshold)
    ]
    if len(fp_below) > 0:
        for _, row in fp_below.iterrows():
            logger.info(f"  {row['player_name']} ({row['season']}): {row['feature_value']:.4f}")
    else:
        logger.info("  None")
    
    # Save detailed results
    output_path = Path("results/shot_quality_generation_delta_validation.csv")
    df_features.to_csv(output_path, index=False)
    logger.info(f"\n✅ Detailed results saved to: {output_path}")
    
    # Generate summary report
    report_path = Path("results/shot_quality_generation_delta_validation_report.md")
    generate_report(
        report_path,
        metric_status,
        stats,
        threshold_results,
        optimal,
        position_check,
        df_features
    )
    logger.info(f"✅ Validation report saved to: {report_path}")


def generate_report(
    output_path: Path,
    metric_status: Dict,
    stats: Dict,
    threshold_results: Dict,
    optimal: Dict,
    position_check: Dict,
    df_features: pd.DataFrame
):
    """Generate markdown validation report."""
    
    with open(output_path, 'w') as f:
        f.write("# SHOT_QUALITY_GENERATION_DELTA Gate Validation Report\n\n")
        f.write(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Executive Summary\n\n")
        f.write("This report validates the proposed SHOT_QUALITY_GENERATION_DELTA gate against all test cases.\n\n")
        
        f.write("## Step 1: Metric Status\n\n")
        f.write(f"- **Exists in dataset**: {metric_status['exists_in_dataset']}\n")
        f.write(f"- **Coverage**: {metric_status['coverage']} ({metric_status['coverage_pct']:.1f}%)\n")
        f.write(f"- **Exists in model**: {metric_status['exists_in_model']}\n")
        if metric_status['feature_importance']:
            f.write(f"- **Feature importance**: {metric_status['feature_importance']:.2%}\n")
        f.write("\n")
        
        f.write("## Step 2: Statistical Comparison\n\n")
        f.write("| Category | Count | Mean | Median | Std | Min | Max | Missing |\n")
        f.write("|----------|-------|------|--------|-----|-----|-----|----------|\n")
        
        for category, category_stats in stats.items():
            if category_stats['count'] > 0:
                f.write(f"| {category} | {category_stats['count']} | "
                       f"{category_stats['mean']:.4f} | {category_stats['median']:.4f} | "
                       f"{category_stats['std']:.4f} | {category_stats['min']:.4f} | "
                       f"{category_stats['max']:.4f} | {category_stats['missing']} |\n")
            else:
                f.write(f"| {category} | 0 | N/A | N/A | N/A | N/A | N/A | {category_stats['missing']} |\n")
        
        f.write("\n## Step 3: Proposed Threshold Validation (-0.02)\n\n")
        f.write(f"**Proposed Threshold**: -0.02\n\n")
        f.write(f"**True Positives**:\n")
        f.write(f"- Total: {threshold_results['True Positive']['total']}\n")
        f.write(f"- Below threshold: {threshold_results['True Positive']['below_threshold']} ({threshold_results['True Positive']['pct_below']:.1f}%)\n")
        f.write(f"- **False Negative Rate**: {threshold_results['false_negative_rate']:.2%}\n\n")
        
        f.write(f"**False Positives**:\n")
        f.write(f"- Total: {threshold_results['False Positive']['total']}\n")
        f.write(f"- Below threshold: {threshold_results['False Positive']['below_threshold']} ({threshold_results['False Positive']['pct_below']:.1f}%)\n")
        f.write(f"- **FP Catch Rate**: {threshold_results['fp_catch_rate']:.2%}\n\n")
        
        if threshold_results['false_negative_rate'] > 0.20:
            f.write("⚠️ **WARNING**: Proposed threshold would break more than 20% of true positives!\n\n")
        
        f.write("## Step 4: Optimal Threshold\n\n")
        if optimal['optimal_threshold'] is not None:
            f.write(f"**Optimal Threshold**: {optimal['optimal_threshold']:.4f}\n")
            f.write(f"- **False Negative Rate**: {optimal['fn_rate']:.2%}\n")
            f.write(f"- **FP Catch Rate**: {optimal['fp_catch_rate']:.2%}\n\n")
        else:
            f.write("⚠️ **No optimal threshold found** that meets constraints (FN rate < 20%)\n\n")
        
        f.write("## Step 5: Position Dependency Check\n\n")
        f.write(f"**Position Dependent**: {position_check['position_dependent']}\n")
        f.write(f"**Reason**: {position_check['reason']}\n\n")
        
        f.write("## Recommendations\n\n")
        
        # Generate recommendations based on findings
        if not metric_status['exists_in_dataset']:
            f.write("1. **Metric not found in dataset** - Need to calculate SHOT_QUALITY_GENERATION_DELTA first\n")
        elif threshold_results['false_negative_rate'] > 0.20:
            f.write("1. **Proposed threshold breaks too many true positives** - Do not implement gate with -0.02 threshold\n")
            if optimal['optimal_threshold'] is not None:
                f.write(f"2. **Consider using optimal threshold** ({optimal['optimal_threshold']:.4f}) instead\n")
            else:
                f.write("2. **No viable threshold found** - Gate may not be effective for this metric\n")
        elif threshold_results['fp_catch_rate'] < 0.50:
            f.write("1. **Gate would catch less than 50% of false positives** - May not be effective\n")
        else:
            f.write("1. **Gate appears viable** - Consider implementing with validated threshold\n")
        
        if position_check['position_dependent']:
            f.write("2. **Metric is position-dependent** - Consider position-relative thresholds\n")


if __name__ == "__main__":
    main()

