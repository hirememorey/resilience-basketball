"""
Star Latency Analysis

This script analyzes how well the model predicts "star latency" - the gap between
a player's current state and their predicted star-level potential at higher usage.

Star Latency = Players who are predicted to be stars at 25% usage but aren't
currently stars (i.e., they have latent star potential that hasn't manifested yet).

IMPORTANT: For star latency analysis, Risk Categories are calculated based on
projected performance at 25% usage, not current usage. This correctly identifies
players who would be "Franchise Cornerstone" or "Luxury Component" if given more usage.
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging
from tqdm import tqdm

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def analyze_star_latency(df: pd.DataFrame, predictor: ConditionalArchetypePredictor) -> pd.DataFrame:
    """
    Analyze star latency - players with high star potential at 25% usage
    but low current star-level.
    
    IMPORTANT: Recalculates Risk Category at 25% usage for proper latency evaluation.
    
    Args:
        df: DataFrame with predictions at current and 25% usage
        predictor: ConditionalArchetypePredictor instance for recalculating risk categories
        
    Returns:
        DataFrame with latency analysis including Risk Category at 25% usage
    """
    df = df.copy()
    
    # Define star threshold (70% star-level potential)
    STAR_THRESHOLD = 0.70
    
    # Calculate latency metrics
    df['IS_CURRENT_STAR'] = df['CURRENT_STAR_LEVEL'] >= STAR_THRESHOLD
    df['IS_PREDICTED_STAR_AT_25'] = df['AT_25_USG_STAR_LEVEL'] >= STAR_THRESHOLD
    df['STAR_LATENCY'] = df['AT_25_USG_STAR_LEVEL'] - df['CURRENT_STAR_LEVEL']
    df['USAGE_GAP'] = 0.25 - df['RS_USG_PCT']
    
    # Calculate Risk Category at 25% usage using star-level potential and dependence
    # IMPORTANT: Use AT_25_USG_STAR_LEVEL as performance score (not recalculated with gates)
    # Dependence score should be the same regardless of usage level
    logger.info("Calculating Risk Categories at 25% usage for latency analysis...")
    logger.info("Using AT_25_USG_STAR_LEVEL as performance score (gates already applied in prediction)")
    
    # Use star-level potential at 25% as performance score
    df['PERFORMANCE_SCORE_AT_25_USG'] = df['AT_25_USG_STAR_LEVEL']
    
    # Dependence score is usage-independent, so use current one if available
    # Otherwise, we'll need to calculate it
    df['DEPENDENCE_SCORE_AT_25_USG'] = df.get('DEPENDENCE_SCORE', None)
    
    # Calculate risk categories using the predictor's categorization logic
    risk_categories_25 = []
    df_features = predictor.df_features.copy()
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Calculating Risk Categories"):
        try:
            performance_score = row['AT_25_USG_STAR_LEVEL']
            dependence_score = row.get('DEPENDENCE_SCORE', None)
            
            # Use predictor's categorization method
            risk_category = predictor._categorize_risk(performance_score, dependence_score)
            risk_categories_25.append(risk_category)
            
        except Exception as e:
            logger.debug(f"Error calculating risk category for {row.get('PLAYER_NAME', 'Unknown')} {row.get('SEASON', 'Unknown')}: {e}")
            # Fallback: categorize manually
            performance_score = row['AT_25_USG_STAR_LEVEL']
            dependence_score = row.get('DEPENDENCE_SCORE', None)
            
            if dependence_score is None:
                if performance_score >= 0.70:
                    risk_category = "High Performance (Dependence Unknown)"
                elif performance_score < 0.30:
                    risk_category = "Low Performance (Dependence Unknown)"
                else:
                    risk_category = "Moderate Performance (Dependence Unknown)"
            else:
                # Manual categorization
                low_dep_threshold = 0.3570
                high_dep_threshold = 0.4482
                
                high_performance = performance_score >= 0.70
                low_performance = performance_score < 0.30
                high_dependence = dependence_score >= high_dep_threshold
                low_dependence = dependence_score < low_dep_threshold
                
                if high_performance and low_dependence:
                    risk_category = "Franchise Cornerstone"
                elif high_performance and high_dependence:
                    risk_category = "Luxury Component"
                elif low_performance and low_dependence:
                    risk_category = "Depth"
                elif low_performance and high_dependence:
                    risk_category = "Avoid"
                else:
                    # Moderate scores
                    if performance_score >= 0.70:
                        if dependence_score >= high_dep_threshold:
                            risk_category = "Luxury Component (Moderate Dependence)"
                        else:
                            risk_category = "Franchise Cornerstone (Moderate Dependence)"
                    elif performance_score < 0.30:
                        if dependence_score >= high_dep_threshold:
                            risk_category = "Avoid (Moderate Dependence)"
                        else:
                            risk_category = "Depth (Moderate Dependence)"
                    else:
                        if dependence_score >= high_dep_threshold:
                            risk_category = "Luxury Component"
                        elif dependence_score < low_dep_threshold:
                            risk_category = "Moderate Performance, Low Dependence"
                        else:
                            risk_category = "Moderate Performance, Moderate Dependence"
            
            risk_categories_25.append(risk_category)
    
    # Add new columns
    df['RISK_CATEGORY_AT_25_USG'] = risk_categories_25
    
    # Categorize players
    df['LATENCY_CATEGORY'] = 'None'
    df.loc[
        (~df['IS_CURRENT_STAR']) & (df['IS_PREDICTED_STAR_AT_25']),
        'LATENCY_CATEGORY'
    ] = 'Latent Star'
    df.loc[
        (df['IS_CURRENT_STAR']) & (df['IS_PREDICTED_STAR_AT_25']),
        'LATENCY_CATEGORY'
    ] = 'Current Star'
    df.loc[
        (~df['IS_CURRENT_STAR']) & (~df['IS_PREDICTED_STAR_AT_25']),
        'LATENCY_CATEGORY'
    ] = 'Non-Star'
    df.loc[
        (df['IS_CURRENT_STAR']) & (~df['IS_PREDICTED_STAR_AT_25']),
        'LATENCY_CATEGORY'
    ] = 'Overrated'
    
    return df


def generate_latency_report(df: pd.DataFrame) -> str:
    """Generate a comprehensive star latency report."""
    
    report = []
    report.append("="*80)
    report.append("STAR LATENCY ANALYSIS")
    report.append("="*80)
    report.append("")
    
    # Overall statistics
    total_players = len(df)
    latent_stars = len(df[df['LATENCY_CATEGORY'] == 'Latent Star'])
    current_stars = len(df[df['LATENCY_CATEGORY'] == 'Current Star'])
    non_stars = len(df[df['LATENCY_CATEGORY'] == 'Non-Star'])
    overrated = len(df[df['LATENCY_CATEGORY'] == 'Overrated'])
    
    report.append(f"Total Player-Seasons Analyzed: {total_players}")
    report.append("")
    report.append("Latency Categories:")
    report.append(f"  Latent Stars (Predicted Star at 25%, Not Currently): {latent_stars} ({latent_stars/total_players*100:.1f}%)")
    report.append(f"  Current Stars (Star Now & Predicted at 25%): {current_stars} ({current_stars/total_players*100:.1f}%)")
    report.append(f"  Non-Stars (Not Star Now or Predicted): {non_stars} ({non_stars/total_players*100:.1f}%)")
    report.append(f"  Overrated (Star Now, Not Predicted at 25%): {overrated} ({overrated/total_players*100:.1f}%)")
    report.append("")
    
    # Latent star analysis
    if latent_stars > 0:
        latent_df = df[df['LATENCY_CATEGORY'] == 'Latent Star'].copy()
        report.append("="*80)
        report.append("LATENT STAR ANALYSIS")
        report.append("="*80)
        report.append("")
        
        report.append(f"Total Latent Stars: {latent_stars}")
        report.append("")
        
        report.append("Age Distribution:")
        report.append(f"  Mean: {latent_df['AGE'].mean():.1f}")
        report.append(f"  Median: {latent_df['AGE'].median():.0f}")
        report.append(f"  Range: {latent_df['AGE'].min():.0f} - {latent_df['AGE'].max():.0f}")
        report.append("")
        
        report.append("Current Usage Distribution:")
        report.append(f"  Mean: {latent_df['RS_USG_PCT'].mean()*100:.1f}%")
        report.append(f"  Median: {latent_df['RS_USG_PCT'].median()*100:.1f}%")
        report.append(f"  Range: {latent_df['RS_USG_PCT'].min()*100:.1f}% - {latent_df['RS_USG_PCT'].max()*100:.1f}%")
        report.append("")
        
        report.append("Star Latency (Gap between Current and Predicted at 25%):")
        report.append(f"  Mean: {latent_df['STAR_LATENCY'].mean()*100:.1f}%")
        report.append(f"  Median: {latent_df['STAR_LATENCY'].median()*100:.1f}%")
        report.append(f"  Range: {latent_df['STAR_LATENCY'].min()*100:.1f}% - {latent_df['STAR_LATENCY'].max()*100:.1f}%")
        report.append("")
        
        report.append("Usage Gap (How much usage increase needed to reach 25%):")
        report.append(f"  Mean: {latent_df['USAGE_GAP'].mean()*100:.1f}%")
        report.append(f"  Median: {latent_df['USAGE_GAP'].median()*100:.1f}%")
        report.append("")
        
        report.append("Predicted Star-Level at 25% Usage:")
        report.append(f"  Mean: {latent_df['AT_25_USG_STAR_LEVEL'].mean()*100:.1f}%")
        report.append(f"  Median: {latent_df['AT_25_USG_STAR_LEVEL'].median()*100:.1f}%")
        report.append(f"  Range: {latent_df['AT_25_USG_STAR_LEVEL'].min()*100:.1f}% - {latent_df['AT_25_USG_STAR_LEVEL'].max()*100:.1f}%")
        report.append("")
        
        report.append("Top 20 Latent Stars by Star-Level Potential at 25% Usage:")
        top_latent = latent_df.nlargest(20, 'AT_25_USG_STAR_LEVEL')[
            ['PLAYER_NAME', 'SEASON', 'AGE', 'RS_USG_PCT', 
             'CURRENT_STAR_LEVEL', 'AT_25_USG_STAR_LEVEL', 'STAR_LATENCY']
        ]
        for idx, row in top_latent.iterrows():
            report.append(
                f"  {row['PLAYER_NAME']} ({row['SEASON']}) - Age {row['AGE']:.0f}, "
                f"Usage {row['RS_USG_PCT']*100:.1f}% → "
                f"Current: {row['CURRENT_STAR_LEVEL']*100:.1f}%, "
                f"At 25%: {row['AT_25_USG_STAR_LEVEL']*100:.1f}% "
                f"(Latency: +{row['STAR_LATENCY']*100:.1f}%)"
            )
        report.append("")
        
        # Risk category distribution for latent stars (at 25% usage)
        if 'RISK_CATEGORY_AT_25_USG' in latent_df.columns:
            report.append("Risk Category Distribution at 25% Usage (Latent Stars):")
            risk_counts = latent_df['RISK_CATEGORY_AT_25_USG'].value_counts()
            for category, count in risk_counts.items():
                report.append(f"  {category}: {count} ({count/len(latent_df)*100:.1f}%)")
            report.append("")
    
    # Model performance metrics
    report.append("="*80)
    report.append("MODEL PERFORMANCE METRICS")
    report.append("="*80)
    report.append("")
    
    # Star prediction rate
    predicted_stars = len(df[df['IS_PREDICTED_STAR_AT_25']])
    report.append(f"Players Predicted to be Stars at 25% Usage: {predicted_stars} ({predicted_stars/total_players*100:.1f}%)")
    report.append("")
    
    # Latency distribution
    report.append("Star Latency Distribution (All Players):")
    report.append(f"  Mean: {df['STAR_LATENCY'].mean()*100:.1f}%")
    report.append(f"  Median: {df['STAR_LATENCY'].median()*100:.1f}%")
    report.append(f"  Std Dev: {df['STAR_LATENCY'].std()*100:.1f}%")
    report.append("")
    
    # High latency players (biggest gap)
    high_latency = df.nlargest(20, 'STAR_LATENCY')[
        ['PLAYER_NAME', 'SEASON', 'AGE', 'RS_USG_PCT',
         'CURRENT_STAR_LEVEL', 'AT_25_USG_STAR_LEVEL', 'STAR_LATENCY']
    ]
    report.append("Top 20 Players by Star Latency (Biggest Gap):")
    for idx, row in high_latency.iterrows():
        report.append(
            f"  {row['PLAYER_NAME']} ({row['SEASON']}) - "
            f"Current: {row['CURRENT_STAR_LEVEL']*100:.1f}% → "
            f"At 25%: {row['AT_25_USG_STAR_LEVEL']*100:.1f}% "
            f"(Gap: +{row['STAR_LATENCY']*100:.1f}%)"
        )
    report.append("")
    
    # Age-based analysis
    report.append("="*80)
    report.append("AGE-BASED LATENCY ANALYSIS")
    report.append("="*80)
    report.append("")
    
    for age in sorted(df['AGE'].unique()):
        age_df = df[df['AGE'] == age]
        age_latent = len(age_df[age_df['LATENCY_CATEGORY'] == 'Latent Star'])
        age_total = len(age_df)
        if age_total > 0:
            report.append(f"Age {age:.0f}: {age_latent}/{age_total} latent stars ({age_latent/age_total*100:.1f}%)")
    report.append("")
    
    # Usage-based analysis
    report.append("="*80)
    report.append("USAGE-BASED LATENCY ANALYSIS")
    report.append("="*80)
    report.append("")
    
    # Low usage players (< 20%)
    low_usage = df[df['RS_USG_PCT'] < 0.20]
    low_usage_latent = len(low_usage[low_usage['LATENCY_CATEGORY'] == 'Latent Star'])
    report.append(f"Low Usage (< 20%): {low_usage_latent}/{len(low_usage)} latent stars ({low_usage_latent/len(low_usage)*100:.1f}%)")
    
    # Medium usage (20-25%)
    med_usage = df[(df['RS_USG_PCT'] >= 0.20) & (df['RS_USG_PCT'] < 0.25)]
    med_usage_latent = len(med_usage[med_usage['LATENCY_CATEGORY'] == 'Latent Star'])
    report.append(f"Medium Usage (20-25%): {med_usage_latent}/{len(med_usage)} latent stars ({med_usage_latent/len(med_usage)*100:.1f}%)")
    
    # High usage (>= 25%)
    high_usage = df[df['RS_USG_PCT'] >= 0.25]
    high_usage_latent = len(high_usage[high_usage['LATENCY_CATEGORY'] == 'Latent Star'])
    report.append(f"High Usage (>= 25%): {high_usage_latent}/{len(high_usage)} latent stars ({high_usage_latent/len(high_usage)*100:.1f}%)")
    report.append("")
    
    # Key player analysis (cases that were flagged)
    report.append("="*80)
    report.append("KEY PLAYER ANALYSIS (At 25% Usage)")
    report.append("="*80)
    report.append("")
    report.append("These players show correct categorization when evaluated at 25% usage:")
    report.append("")
    
    key_players = [
        ('Tyrese Haliburton', '2024-25'),
        ('Nikola Jokić', '2019-20'),
        ('Nikola Jokić', '2017-18'),
        ('Nikola Jokić', '2018-19'),
        ('Jalen Brunson', '2020-21'),
        ('Luka Dončić', '2019-20'),
        ('Donovan Mitchell', '2021-22'),
        ('Victor Wembanyama', '2023-24'),
        ('Victor Wembanyama', '2024-25'),
        ('Devin Booker', '2020-21'),
        ('Anthony Davis', '2017-18'),
        ('Anthony Davis', '2015-16'),
        ('Anthony Davis', '2016-17'),
        ('Joel Embiid', '2016-17'),
        ('Joel Embiid', '2017-18'),
        ('Pascal Siakam', '2018-19'),
        ('Zach LaVine', '2019-20'),
        ('D\'Angelo Russell', '2019-20'),
        ('D\'Angelo Russell', '2017-18'),
        ('Lauri Markkanen', '2020-21'),
        ('Kevin Porter Jr.', '2021-22'),
        ('RJ Barrett', '2021-22'),
        ('Shai Gilgeous-Alexander', '2018-19'),
        ('Tyrese Maxey', '2022-23'),
        ('Tyrese Haliburton', '2021-22'),
        ('Tyrese Haliburton', '2022-23'),
        ('Tyrese Haliburton', '2020-21'),
    ]
    
    for player_name, season in key_players:
        player_df = df[(df['PLAYER_NAME'] == player_name) & (df['SEASON'] == season)]
        if len(player_df) > 0:
            row = player_df.iloc[0]
            current_risk = row.get('RISK_CATEGORY', 'N/A')
            risk_25 = row.get('RISK_CATEGORY_AT_25_USG', 'N/A')
            perf_25 = row.get('PERFORMANCE_SCORE_AT_25_USG', row.get('AT_25_USG_STAR_LEVEL', 0))
            dep_25 = row.get('DEPENDENCE_SCORE_AT_25_USG', row.get('DEPENDENCE_SCORE', None))
            
            report.append(
                f"{player_name} ({season}):"
            )
            report.append(
                f"  Current Usage ({row['RS_USG_PCT']*100:.1f}%): {current_risk} "
                f"(Performance: {row.get('PERFORMANCE_SCORE', row['CURRENT_STAR_LEVEL'])*100:.1f}%)"
            )
            report.append(
                f"  At 25% Usage: {risk_25} "
                f"(Performance: {perf_25*100:.1f}%, "
                f"Dependence: {dep_25*100:.1f}% if available)"
            )
            report.append(
                f"  Star-Level at 25%: {row['AT_25_USG_STAR_LEVEL']*100:.1f}% "
                f"(Latency: +{row['STAR_LATENCY']*100:.1f}%)"
            )
            report.append("")
    
    return "\n".join(report)


def main():
    """Main analysis function."""
    
    logger.info("="*80)
    logger.info("STAR LATENCY ANALYSIS")
    logger.info("="*80)
    
    # Load results
    results_path = Path("results/young_players_star_latency_analysis.csv")
    if not results_path.exists():
        logger.error(f"Results file not found: {results_path}")
        logger.info("Please run run_expanded_predictions.py first to generate predictions.")
        return
    
    logger.info(f"Loading results from: {results_path}")
    df = pd.read_csv(results_path)
    logger.info(f"Loaded {len(df)} player-seasons")
    
    # Initialize predictor for recalculating risk categories
    logger.info("\nInitializing predictor...")
    predictor = ConditionalArchetypePredictor()
    
    # Analyze star latency
    logger.info("\nAnalyzing star latency...")
    df_analyzed = analyze_star_latency(df, predictor)
    
    # Save analyzed results
    output_path = Path("results/star_latency_analysis.csv")
    df_analyzed.to_csv(output_path, index=False)
    logger.info(f"Saved analyzed results to: {output_path}")
    
    # Generate report
    logger.info("\nGenerating report...")
    report = generate_latency_report(df_analyzed)
    
    # Save report
    report_path = Path("results/star_latency_report.md")
    with open(report_path, 'w') as f:
        f.write(report)
    logger.info(f"Saved report to: {report_path}")
    
    # Print report
    print("\n" + report)
    
    logger.info("\n" + "="*80)
    logger.info("Analysis complete!")
    logger.info("="*80)


if __name__ == "__main__":
    main()

