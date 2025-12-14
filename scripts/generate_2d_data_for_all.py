#!/usr/bin/env python3
"""
Generate 2D Risk Matrix Data for All Players

This script generates performance scores, dependence scores, and risk categories
for all players in the dataset, enabling full 2D risk matrix analysis in the app.

Process:
1. Load all player data from predictive_dataset.csv
2. For each player, predict performance score using the ML model
3. Calculate dependence score using the dependence formula
4. Determine risk category based on the 2D matrix thresholds
5. Save comprehensive 2D data for all players
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from tqdm import tqdm
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import required modules
from src.nba_data.scripts.predict_conditional_archetype import ConditionalArchetypePredictor
from src.nba_data.scripts.calculate_dependence_score import calculate_dependence_score
from src.nba_data.utils.projection_utils import (
    calculate_empirical_usage_buckets,
    calculate_feature_percentiles
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_all_player_data() -> pd.DataFrame:
    """Load all player data from the predictive dataset."""
    try:
        df = pd.read_csv('results/predictive_dataset.csv')
        logger.info(f"Loaded {len(df)} players from predictive dataset")

        # Filter out players with insufficient data
        df = df.dropna(subset=['USG_PCT'])  # Must have usage data
        logger.info(f"After filtering: {len(df)} players with usage data")

        return df
    except FileNotFoundError:
        logger.error("❌ predictive_dataset.csv not found. Run feature generation first.")
        sys.exit(1)


def predict_performance_for_all(df_players: pd.DataFrame) -> pd.DataFrame:
    """
    Predict performance scores for all players using the ML model.

    This uses the ConditionalArchetypePredictor to get star-level potential
    at each player's current usage level.
    """
    logger.info("Initializing performance predictor...")
    predictor = ConditionalArchetypePredictor(use_rfe_model=True)

    # Load projection data
    usage_buckets = calculate_empirical_usage_buckets(df_players)
    percentiles = calculate_feature_percentiles(df_players)

    results = []

    logger.info(f"Predicting performance for {len(df_players)} players...")

    for idx, row in tqdm(df_players.iterrows(), total=len(df_players), desc="Performance Prediction"):
        player_name = row['PLAYER_NAME']
        season = row['SEASON']

        try:
            # Predict at current usage level
            current_usage = row.get('USG_PCT', 0.20)
            if current_usage > 1.0:  # Convert percentage if needed
                current_usage = current_usage / 100.0

            # Create a copy of row data and normalize USG_PCT
            player_data = row.copy()
            player_data['USG_PCT'] = current_usage

            # Get prediction result
            prediction = predictor.predict_archetype_at_usage(
                player_data=player_data,
                usage_level=current_usage,
                apply_phase3_fixes=True,
                apply_hard_gates=True  # Apply Alpha Threshold and other physics gates
            )

            result = {
                'PLAYER_NAME': player_name,
                'SEASON': season,
                'PLAYER_ID': row.get('PLAYER_ID'),
                'PERFORMANCE_SCORE': prediction['star_level_potential'],
                'PREDICTED_ARCHETYPE': prediction['predicted_archetype'],
                'CURRENT_USAGE': current_usage,
                'prediction_success': True
            }

            results.append(result)

        except Exception as e:
            logger.warning(f"Failed to predict for {player_name} ({season}): {e}")
            results.append({
                'PLAYER_NAME': player_name,
                'SEASON': season,
                'PLAYER_ID': row.get('PLAYER_ID'),
                'PERFORMANCE_SCORE': None,
                'PREDICTED_ARCHETYPE': None,
                'CURRENT_USAGE': row.get('USG_PCT', 0),
                'prediction_success': False,
                'error': str(e)
            })

    df_results = pd.DataFrame(results)
    success_rate = df_results['prediction_success'].mean() * 100
    logger.info(f"Performance prediction success rate: {success_rate:.1f}%")
    return df_results


def calculate_dependence_for_all(df_players: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate dependence scores for all players.

    Uses the new calculate_dependence_score logic (Two Doors).
    """
    results = []

    logger.info(f"Calculating dependence scores for {len(df_players)} players...")

    for idx, row in tqdm(df_players.iterrows(), total=len(df_players), desc="Dependence Calculation"):
        player_name = row['PLAYER_NAME']
        season = row['SEASON']

        try:
            # Use the robust Two Doors calculation
            result = calculate_dependence_score(row)
            
            dependence_score = result['dependence_score']
            assisted_fgm_pct = result['assisted_fgm_pct']
            open_shot_freq = result['open_shot_frequency']
            self_created_ratio = result['self_created_usage_ratio']
            physicality_score = result['physicality_score']
            skill_score = result['skill_score']

            res_dict = {
                'PLAYER_NAME': player_name,
                'SEASON': season,
                'PLAYER_ID': row.get('PLAYER_ID'),
                'DEPENDENCE_SCORE': dependence_score,
                'PHYSICALITY_SCORE': physicality_score,
                'SKILL_SCORE': skill_score,
                'ASSISTED_FGM_PCT': assisted_fgm_pct,
                'OPEN_SHOT_FREQUENCY': open_shot_freq,
                'SELF_CREATED_USAGE_RATIO': self_created_ratio,
                'dependence_success': dependence_score is not None
            }

            results.append(res_dict)

        except Exception as e:
            logger.warning(f"Failed to calculate dependence for {player_name} ({season}): {e}")
            results.append({
                'PLAYER_NAME': player_name,
                'SEASON': season,
                'PLAYER_ID': row.get('PLAYER_ID'),
                'DEPENDENCE_SCORE': None,
                'PHYSICALITY_SCORE': None,
                'SKILL_SCORE': None,
                'ASSISTED_FGM_PCT': None,
                'OPEN_SHOT_FREQUENCY': None,
                'SELF_CREATED_USAGE_RATIO': None,
                'dependence_success': False,
                'error': str(e)
            })

    df_results = pd.DataFrame(results)
    success_rate = df_results['dependence_success'].mean() * 100
    logger.info(f"Dependence calculation success rate: {success_rate:.1f}%")
    return df_results


def determine_risk_categories(df_combined: pd.DataFrame) -> pd.DataFrame:
    """
    Determine risk categories based on performance and dependence scores.

    Uses data-driven thresholds calculated from the distribution.
    """
    # Initialize RISK_CATEGORY column
    df_combined['RISK_CATEGORY'] = None

    # Drop rows with missing scores
    df_valid = df_combined.dropna(subset=['PERFORMANCE_SCORE', 'DEPENDENCE_SCORE']).copy()

    if len(df_valid) == 0:
        logger.warning("No valid performance/dependence score pairs found")
        return df_combined

    # Calculate thresholds from the data distribution
    # High performance: Top 25% of performance scores
    # Use same thresholds as main predictor for consistency
    # High performance: >= 70% (elite level)
    perf_threshold = 0.70

    # High dependence: 33rd percentile as the new threshold for low dependence
    # Recalibrate based on new Two Doors distribution
    if len(df_valid) > 0:
        dep_percentiles = df_valid['DEPENDENCE_SCORE'].quantile([0.33, 0.50, 0.66]).to_dict()
        logger.info(f"Dependence Score Distribution:")
        logger.info(f"  33rd Percentile (Low Dep Cutoff): {dep_percentiles[0.33]:.3f}")
        logger.info(f"  50th Percentile (Median):        {dep_percentiles[0.50]:.3f}")
        logger.info(f"  66th Percentile (High Dep):      {dep_percentiles[0.66]:.3f}")
        
        dep_threshold = dep_percentiles[0.33]
        # Round to nearest 0.005 for cleaner threshold
        dep_threshold = round(dep_threshold * 200) / 200
    else:
        dep_threshold = 0.40 # Fallback

    logger.info(f"Performance threshold (fixed): {perf_threshold:.1f}")
    logger.info(f"Dependence threshold (Dynamic 33rd Percentile): {dep_threshold:.3f}")
    def categorize_risk(row):
        perf = row['PERFORMANCE_SCORE']
        dep = row['DEPENDENCE_SCORE']

        if perf >= perf_threshold and dep < dep_threshold:
            return 'Franchise Cornerstone'
        elif perf >= perf_threshold and dep >= dep_threshold:
            return 'Luxury Component'
        elif perf < perf_threshold and dep < dep_threshold:
            return 'Depth'
        else:  # perf < perf_threshold and dep >= dep_threshold
            return 'Avoid'

    # Apply categorization
    df_combined['RISK_CATEGORY'] = None
    valid_mask = df_combined['PERFORMANCE_SCORE'].notna() & df_combined['DEPENDENCE_SCORE'].notna()
    df_combined.loc[valid_mask, 'RISK_CATEGORY'] = df_combined.loc[valid_mask].apply(categorize_risk, axis=1)

    # Add more descriptive categories for the UI
    def get_detailed_category(row):
        if pd.isna(row['RISK_CATEGORY']):
            return 'Analysis Pending'

        perf = row['PERFORMANCE_SCORE']
        dep = row['DEPENDENCE_SCORE']

        if row['RISK_CATEGORY'] == 'Franchise Cornerstone':
            return 'Franchise Cornerstone'
        elif row['RISK_CATEGORY'] == 'Luxury Component':
            return f'Luxury Component (High Performance {perf:.1%}, High Dependence {dep:.1%})'
        elif row['RISK_CATEGORY'] == 'Depth':
            return f'Depth (Low Performance {perf:.1%}, Low Dependence {dep:.1%})'
        elif row['RISK_CATEGORY'] == 'Avoid':
            return f'Avoid (Low Performance {perf:.1%}, High Dependence {dep:.1%})'
        else:
            return row['RISK_CATEGORY']

    df_combined['RISK_CATEGORY_DETAILED'] = df_combined.apply(get_detailed_category, axis=1)

    return df_combined


def main():
    """Generate 2D risk matrix data for all players."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate 2D Risk Matrix Data")
    parser.add_argument('--test', action='store_true', help='Run on first 10 players only for testing')
    parser.add_argument('--sample', type=int, help='Run on first N players only')
    args = parser.parse_args()

    if args.test:
        logger.info("🧪 TEST MODE: Processing first 10 players only")
    elif args.sample:
        logger.info(f"📊 SAMPLE MODE: Processing first {args.sample} players only")

    logger.info("🏀 Generating 2D Risk Matrix Data for Players")
    logger.info("=" * 60)

    # Load all player data
    df_players = load_all_player_data()
    if len(df_players) == 0:
        logger.error("No player data found")
        sys.exit(1)

    # Apply sampling if requested
    if args.test:
        df_players = df_players.head(10)
    elif args.sample:
        df_players = df_players.head(args.sample)

    logger.info(f"Processing {len(df_players)} players")

    # Step 1: Predict performance scores
    logger.info("\n📊 Step 1: Predicting Performance Scores")
    df_performance = predict_performance_for_all(df_players)

    # Step 2: Calculate dependence scores
    logger.info("\n🔗 Step 2: Calculating Dependence Scores")
    df_dependence = calculate_dependence_for_all(df_players)

    # Step 3: Combine results
    logger.info("\n🔄 Step 3: Combining Results")
    df_combined = pd.merge(
        df_performance,
        df_dependence,
        on=['PLAYER_NAME', 'SEASON', 'PLAYER_ID'],
        how='outer'
    )

    # Step 4: Determine risk categories
    logger.info("\n📈 Step 4: Determining Risk Categories")
    df_final = determine_risk_categories(df_combined)

    # Step 5: Save comprehensive results
    if args.test:
        output_file = 'results/2d_risk_matrix_test_sample.csv'
    else:
        output_file = 'results/2d_risk_matrix_all_players.csv'

    df_final.to_csv(output_file, index=False)

    # Generate summary statistics
    total_players = len(df_final)
    valid_predictions = df_final['PERFORMANCE_SCORE'].notna().sum()
    valid_dependence = df_final['DEPENDENCE_SCORE'].notna().sum()
    complete_2d = df_final['RISK_CATEGORY'].notna().sum()

    logger.info("\n" + "=" * 60)
    logger.info("✅ 2D Risk Matrix Generation Complete!")
    logger.info(f"📄 Results saved to: {output_file}")
    logger.info(f"👥 Total players processed: {total_players}")
    logger.info(f"🎯 Players with performance scores: {valid_predictions} ({valid_predictions/total_players*100:.1f}%)")
    logger.info(f"🔗 Players with dependence scores: {valid_dependence} ({valid_dependence/total_players*100:.1f}%)")
    logger.info(f"📊 Players with complete 2D analysis: {complete_2d} ({complete_2d/total_players*100:.1f}%)")

    # Show risk category distribution
    if complete_2d > 0:
        category_counts = df_final['RISK_CATEGORY'].value_counts()
        logger.info("\n📈 Risk Category Distribution:")
        for category, count in category_counts.items():
            percentage = count / complete_2d * 100
            logger.info(f"{category:<25} {count:>6} ({percentage:>5.1f}%)")

    if args.test:
        logger.info("\n🧪 Test mode complete! Run without --test to process all players.")
    else:
        logger.info("\n🚀 The Streamlit app now has 2D data for all players!")
        logger.info("   Run: python scripts/run_streamlit_app.py")


if __name__ == "__main__":
    main()
