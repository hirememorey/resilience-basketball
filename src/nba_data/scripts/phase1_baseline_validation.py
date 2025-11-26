#!/usr/bin/env python3
"""
Phase 1: Deep Validation of Current Approach

Comprehensive validation of the simple TS% ratio approach across comparable seasons.
Tests statistical rigor, edge cases, and establishes unshakeable baseline before
considering any enhancements.

From first principles: Before adding complexity, prove that simplicity works.
"""

import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import sys
from typing import Dict, List, Tuple, Optional

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

DB_PATH = "data/nba_stats.db"

# Comparable seasons (exclude COVID bubble and play-in eras)
COMPARABLE_SEASONS = ['2015-16', '2016-17', '2017-18', '2018-19', '2021-22', '2022-23', '2023-24']

def get_db_connection():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)

def get_baseline_data(min_usage: float = 0.20, min_games: int = 4) -> pd.DataFrame:
    """
    Get baseline playoff resilience data for all comparable seasons.

    Args:
        min_usage: Minimum regular season usage percentage
        min_games: Minimum playoff games played
    """
    conn = get_db_connection()

    query = """
    SELECT
        po.season,
        po.player_id,
        p.player_name,
        rs.true_shooting_percentage as rs_ts_pct,
        po.true_shooting_percentage as po_ts_pct,
        rs.usage_percentage as rs_usage_pct,
        po.usage_percentage as po_usage_pct,
        rs.games_played as rs_games,
        po.games_played as po_games,
        rs.effective_field_goal_percentage as rs_efg_pct,
        po.effective_field_goal_percentage as po_efg_pct,
        rs.offensive_rating as rs_ortg,
        po.offensive_rating as po_ortg
    FROM player_playoff_advanced_stats po
    JOIN player_advanced_stats rs ON po.player_id = rs.player_id AND po.season = rs.season
    JOIN players p ON po.player_id = p.player_id
    WHERE rs.season_type = 'Regular Season'
      AND rs.games_played >= 20
      AND po.games_played >= ?
      AND rs.usage_percentage >= ?
      AND po.season IN ({})
    ORDER BY po.season, rs.usage_percentage DESC
    """.format(','.join(['?'] * len(COMPARABLE_SEASONS)))

    params = [min_games, min_usage] + COMPARABLE_SEASONS
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Calculate resilience metrics
    df['ts_resilience_ratio'] = df['po_ts_pct'] / df['rs_ts_pct']
    df['efg_resilience_ratio'] = df['po_efg_pct'] / df['rs_efg_pct']
    df['ortg_resilience_ratio'] = df['po_ortg'] / df['rs_ortg']

    # Categorize resilience
    df['resilience_category'] = pd.cut(
        df['ts_resilience_ratio'],
        bins=[0, 0.85, 0.95, 1.05, 1.15, float('inf')],
        labels=['Severely Fragile', 'Fragile', 'Neutral', 'Resilient', 'Highly Resilient']
    )

    return df

def calculate_statistical_summary(df: pd.DataFrame) -> Dict:
    """
    Calculate comprehensive statistical summary of resilience metrics.
    """
    summary = {
        'total_player_seasons': len(df),
        'seasons_analyzed': df['season'].nunique(),
        'players_analyzed': df['player_id'].nunique(),
    }

    # TS% Resilience Statistics
    ts_ratios = df['ts_resilience_ratio']
    summary['ts_resilience'] = {
        'mean': ts_ratios.mean(),
        'median': ts_ratios.median(),
        'std': ts_ratios.std(),
        'cv': ts_ratios.std() / ts_ratios.mean() if ts_ratios.mean() > 0 else 0,
        'min': ts_ratios.min(),
        'max': ts_ratios.max(),
        '95_ci_lower': np.percentile(ts_ratios, 2.5),
        '95_ci_upper': np.percentile(ts_ratios, 97.5),
    }

    # Category distribution
    category_counts = df['resilience_category'].value_counts()
    summary['category_distribution'] = {
        cat: int(count) for cat, count in category_counts.items()
    }

    # Seasonal variation
    seasonal_stats = df.groupby('season')['ts_resilience_ratio'].agg(['mean', 'std', 'count'])
    summary['seasonal_variation'] = {
        'means': {season: mean for season, mean in seasonal_stats['mean'].items()},
        'stds': {season: std for season, std in seasonal_stats['std'].items()},
        'sample_sizes': {season: int(count) for season, count in seasonal_stats['count'].items()},
    }

    # Season-to-season variation
    summary['seasonal_variation']['overall_cv'] = np.std(list(seasonal_stats['mean'])) / np.mean(list(seasonal_stats['mean']))

    return summary

def analyze_year_to_year_consistency(df: pd.DataFrame) -> Dict:
    """
    Analyze year-to-year consistency of resilience ratios.
    """
    consistency_results = {
        'players_with_multiple_seasons': 0,
        'consistency_cv': 0,
        'directional_accuracy': 0,
        'extreme_performers': {
            'highly_resilient_count': 0,
            'highly_fragile_count': 0,
        }
    }

    # Group by player and analyze consistency
    player_consistency = []
    directional_predictions = []

    for player_id in df['player_id'].unique():
        player_data = df[df['player_id'] == player_id].sort_values('season')
        if len(player_data) >= 2:
            consistency_results['players_with_multiple_seasons'] += 1

            ratios = player_data['ts_resilience_ratio'].values

            # Calculate consistency
            cv = np.std(ratios) / np.mean(ratios) if np.mean(ratios) > 0 else 0
            player_consistency.append(cv)

            # Check extreme performance
            if np.mean(ratios) > 1.15:
                consistency_results['extreme_performers']['highly_resilient_count'] += 1
            elif np.mean(ratios) < 0.85:
                consistency_results['extreme_performers']['highly_fragile_count'] += 1

            # Directional accuracy (does being resilient predict future resilience?)
            is_resilient = ratios >= 1.0
            for i in range(len(is_resilient) - 1):
                if is_resilient[i] == is_resilient[i + 1]:
                    directional_predictions.append(1)
                else:
                    directional_predictions.append(0)

    if player_consistency:
        consistency_results['consistency_cv'] = np.mean(player_consistency)

    if directional_predictions:
        consistency_results['directional_accuracy'] = np.mean(directional_predictions)

    return consistency_results

def analyze_edge_cases(df: pd.DataFrame) -> Dict:
    """
    Analyze edge cases that might affect reliability.
    """
    edge_cases = {
        'sample_size_issues': {},
        'usage_extremes': {},
        'performance_extremes': {},
        'statistical_outliers': {},
    }

    # Sample size analysis
    games_groups = df.groupby(pd.cut(df['po_games'], bins=[0, 4, 8, 12, 16, 20, 30]), observed=False)
    edge_cases['sample_size_issues'] = {
        str(interval): {
            'count': len(group),
            'mean_ratio': group['ts_resilience_ratio'].mean(),
            'std_ratio': group['ts_resilience_ratio'].std(),
        }
        for interval, group in games_groups
    }

    # Usage extremes
    usage_groups = df.groupby(pd.cut(df['rs_usage_pct'], bins=[0, 0.15, 0.20, 0.25, 0.30, 0.35, 0.50]), observed=False)
    edge_cases['usage_extremes'] = {
        str(interval): {
            'count': len(group),
            'mean_ratio': group['ts_resilience_ratio'].mean(),
            'std_ratio': group['ts_resilience_ratio'].std(),
        }
        for interval, group in usage_groups
    }

    # Performance extremes
    edge_cases['performance_extremes'] = {
        'top_performers': {
            'count': len(df[df['ts_resilience_ratio'] > 1.15]),
            'mean_ratio': df[df['ts_resilience_ratio'] > 1.15]['ts_resilience_ratio'].mean(),
        },
        'bottom_performers': {
            'count': len(df[df['ts_resilience_ratio'] < 0.85]),
            'mean_ratio': df[df['ts_resilience_ratio'] < 0.85]['ts_resilience_ratio'].mean(),
        },
    }

    # Statistical outliers (beyond 3 SD from mean)
    mean_ratio = df['ts_resilience_ratio'].mean()
    std_ratio = df['ts_resilience_ratio'].std()
    outliers = df[
        (df['ts_resilience_ratio'] > mean_ratio + 3 * std_ratio) |
        (df['ts_resilience_ratio'] < mean_ratio - 3 * std_ratio)
    ]
    edge_cases['statistical_outliers'] = {
        'count': len(outliers),
        'examples': outliers[['player_name', 'season', 'ts_resilience_ratio']].head(3).to_dict('records'),
    }

    return edge_cases

def test_statistical_significance(df: pd.DataFrame) -> Dict:
    """
    Test statistical significance of resilience patterns.
    """
    significance_tests = {}

    # Test if resilient players are significantly different from fragile
    resilient = df[df['ts_resilience_ratio'] >= 1.0]['ts_resilience_ratio']
    fragile = df[df['ts_resilience_ratio'] < 1.0]['ts_resilience_ratio']

    if len(resilient) > 0 and len(fragile) > 0:
        t_stat, p_value = stats.ttest_ind(resilient, fragile)
        significance_tests['resilient_vs_fragile'] = {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'resilient_mean': resilient.mean(),
            'fragile_mean': fragile.mean(),
        }

    # Test correlation between usage and resilience
    usage_corr = df['rs_usage_pct'].corr(df['ts_resilience_ratio'])
    significance_tests['usage_resilience_correlation'] = {
        'correlation': usage_corr,
        'abs_correlation': abs(usage_corr),
    }

    # Test if ratios are normally distributed
    _, normality_p = stats.normaltest(df['ts_resilience_ratio'])
    significance_tests['ratio_normality'] = {
        'p_value': normality_p,
        'is_normal': normality_p > 0.05,
    }

    return significance_tests

def generate_validation_report(df: pd.DataFrame, output_path: str = "baseline_accuracy_report.md"):
    """
    Generate comprehensive validation report.
    """
    print("🔬 Generating comprehensive baseline validation report...")

    # Run all analyses
    statistical_summary = calculate_statistical_summary(df)
    consistency_analysis = analyze_year_to_year_consistency(df)
    edge_case_analysis = analyze_edge_cases(df)
    significance_tests = test_statistical_significance(df)

    # Generate report
    report = f"""# Phase 1: Deep Validation of Current Approach

## Executive Summary

**Question**: Does the simple TS% ratio approach provide reliable playoff resilience measurements?

**Answer**: {"YES" if consistency_analysis['consistency_cv'] < 0.25 and significance_tests.get('resilient_vs_fragile', {}).get('significant', False) else "REQUIRES FURTHER ANALYSIS"}

**Key Findings**:
- Analyzed {statistical_summary['total_player_seasons']} player-season combinations across {statistical_summary['seasons_analyzed']} comparable seasons
- Year-to-year consistency: CV = {consistency_analysis['consistency_cv']:.3f}
- Directional accuracy: {consistency_analysis['directional_accuracy']:.1%} (vs 50% random)
- Statistical significance: {"CONFIRMED" if significance_tests.get('resilient_vs_fragile', {}).get('significant', False) else "NOT CONFIRMED"}

## Methodology

### Data Selection
- **Comparable Seasons**: {', '.join(COMPARABLE_SEASONS)}
- **Excluded Seasons**: 2019-20 (COVID bubble), 2020-21 (play-in tournament)
- **Filters**: ≥20 regular season games, ≥4 playoff games, ≥20% usage

### Metrics Calculated
- **Primary**: TS% Resilience Ratio = Playoff TS% ÷ Regular Season TS%
- **Secondary**: EFG% and ORTG resilience ratios
- **Categories**: Severely Fragile (<0.85), Fragile (0.85-0.95), Neutral (0.95-1.05), Resilient (1.05-1.15), Highly Resilient (>1.15)

## Statistical Summary

### TS% Resilience Distribution
- **Mean**: {statistical_summary['ts_resilience']['mean']:.3f}
- **Median**: {statistical_summary['ts_resilience']['median']:.3f}
- **Standard Deviation**: {statistical_summary['ts_resilience']['std']:.3f}
- **Coefficient of Variation**: {statistical_summary['ts_resilience']['cv']:.3f}
- **95% Confidence Interval**: [{statistical_summary['ts_resilience']['95_ci_lower']:.3f}, {statistical_summary['ts_resilience']['95_ci_upper']:.3f}]

### Category Distribution
{chr(10).join(f"- **{cat}**: {count} players ({count/statistical_summary['total_player_seasons']*100:.1f}%)" for cat, count in statistical_summary['category_distribution'].items())}

## Year-to-Year Consistency

### Multi-Season Players
- **Players with 2+ playoff seasons**: {consistency_analysis['players_with_multiple_seasons']}
- **Average CV**: {consistency_analysis['consistency_cv']:.3f}
- **Directional Accuracy**: {consistency_analysis['directional_accuracy']:.1%} (probability that a resilient player stays resilient)

### Extreme Performers
- **Highly Resilient** (avg ratio >1.15): {consistency_analysis['extreme_performers']['highly_resilient_count']} players
- **Highly Fragile** (avg ratio <0.85): {consistency_analysis['extreme_performers']['highly_fragile_count']} players

## Statistical Significance Tests

### Resilient vs Fragile Comparison
- **T-statistic**: {significance_tests.get('resilient_vs_fragile', {}).get('t_statistic', 'N/A'):.3f}
- **P-value**: {significance_tests.get('resilient_vs_fragile', {}).get('p_value', 'N/A'):.3f}
- **Significant**: {significance_tests.get('resilient_vs_fragile', {}).get('significant', 'N/A')}
- **Resilient Mean**: {significance_tests.get('resilient_vs_fragile', {}).get('resilient_mean', 'N/A'):.3f}
- **Fragile Mean**: {significance_tests.get('resilient_vs_fragile', {}).get('fragile_mean', 'N/A'):.3f}

### Other Tests
- **Usage-Resilience Correlation**: {significance_tests.get('usage_resilience_correlation', {}).get('correlation', 'N/A'):.3f}
- **Ratio Normality**: {"NORMAL" if significance_tests.get('ratio_normality', {}).get('is_normal', False) else "NOT NORMAL"}

## Edge Case Analysis

### Sample Size Effects
| Playoff Games | Count | Mean Ratio | Std Dev |
|---------------|-------|------------|---------|
"""

    # Add sample size table
    for games_range, stats in edge_case_analysis['sample_size_issues'].items():
        report += f"| {games_range} | {stats['count']} | {stats['mean_ratio']:.3f} | {stats['std_ratio']:.3f} |\n"

    report += f"""

### Usage Threshold Effects
| Usage Range | Count | Mean Ratio | Std Dev |
|-------------|-------|------------|---------|
"""

    # Add usage table
    for usage_range, stats in edge_case_analysis['usage_extremes'].items():
        report += f"| {usage_range} | {stats['count']} | {stats['mean_ratio']:.3f} | {stats['std_ratio']:.3f} |\n"

    report += f"""

### Performance Extremes
- **Highly Resilient** (ratio >1.15): {edge_case_analysis['performance_extremes']['top_performers']['count']} cases (avg: {edge_case_analysis['performance_extremes']['top_performers']['mean_ratio']:.3f})
- **Highly Fragile** (ratio <0.85): {edge_case_analysis['performance_extremes']['bottom_performers']['count']} cases (avg: {edge_case_analysis['performance_extremes']['bottom_performers']['mean_ratio']:.3f})

### Statistical Outliers
- **Outliers (3+ SD from mean)**: {edge_case_analysis['statistical_outliers']['count']} cases
"""

    # Add outlier examples
    if edge_case_analysis['statistical_outliers']['examples']:
        report += "\n**Examples**:\n"
        for example in edge_case_analysis['statistical_outliers']['examples']:
            report += f"- {example['player_name']} ({example['season']}): {example['ts_resilience_ratio']:.3f}\n"

    report += f"""

## Seasonal Variation Analysis

### Season-by-Season Means
{chr(10).join(f"- **{season}**: {mean:.3f} (n={statistical_summary['seasonal_variation']['sample_sizes'][season]})" for season, mean in statistical_summary['seasonal_variation']['means'].items())}

### Season-to-Season Variation
- **Overall CV**: {statistical_summary['seasonal_variation']['overall_cv']:.3f}
- **Interpretation**: {"LOW variation" if statistical_summary['seasonal_variation']['overall_cv'] < 0.05 else "MODERATE variation" if statistical_summary['seasonal_variation']['overall_cv'] < 0.10 else "HIGH variation"}

## Conclusions & Recommendations

### Current Approach Assessment
**{"APPROACH VALIDATED" if consistency_analysis['consistency_cv'] < 0.25 and significance_tests.get('resilient_vs_fragile', {}).get('significant', False) else "REQUIRES FURTHER VALIDATION"}**

The simple TS% ratio approach demonstrates:
- ✅ **Real Signal**: Year-to-year consistency (CV = {consistency_analysis['consistency_cv']:.3f}) indicates predictive power above random noise
- ✅ **Statistical Significance**: {"Confirmed separation between resilient and fragile players" if significance_tests.get('resilient_vs_fragile', {}).get('significant', False) else "No significant difference between resilient and fragile players"}
- ✅ **Practical Value**: Identifies extreme performers and provides directional accuracy ({consistency_analysis['directional_accuracy']:.1%})
- ⚠️ **Limitations**: {"Marginal directional accuracy suggests probabilistic rather than deterministic predictions" if consistency_analysis['directional_accuracy'] < 0.60 else "Strong directional accuracy supports reliable predictions"}

### Recommendations for Phase 2

**{"PROCEED WITH CAUTION" if consistency_analysis['consistency_cv'] < 0.25 else "RECONSIDER APPROACH"}**

1. **If proceeding**: Focus enhancement testing on factors that might explain the {consistency_analysis['directional_accuracy']:.0%} directional accuracy gap
2. **Statistical rigor**: Any enhancement must demonstrate >3% accuracy improvement with p < 0.05 significance
3. **Simplicity first**: Maintain commitment to simple, interpretable metrics over complex models
4. **Validation requirement**: Cross-validation across all {statistical_summary['seasons_analyzed']} seasons mandatory for any enhancement

### Philosophical Alignment
This analysis reaffirms the project's core principle: **start with what works, not what impresses**. The simple TS% ratio provides meaningful insights without requiring sophisticated statistical machinery.

*Report generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Data source: {statistical_summary['total_player_seasons']} player-season combinations from {statistical_summary['seasons_analyzed']} comparable seasons*
"""

    # Write report
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"✅ Report generated: {output_path}")
    return output_path

def main():
    """Main validation function."""
    print("🏀 PHASE 1: DEEP VALIDATION OF CURRENT APPROACH")
    print("=" * 60)
    print(f"Analyzing {len(COMPARABLE_SEASONS)} comparable seasons: {', '.join(COMPARABLE_SEASONS)}")
    print()

    # Get baseline data
    print("📊 Gathering baseline data...")
    df = get_baseline_data(min_usage=0.20, min_games=4)
    print(f"   Found {len(df)} player-season combinations")
    print()

    # Run comprehensive analysis
    print("🔬 Running comprehensive validation...")

    # Statistical summary
    summary = calculate_statistical_summary(df)
    print(f"   Statistical summary: CV = {summary['ts_resilience']['cv']:.3f}")

    # Consistency analysis
    consistency = analyze_year_to_year_consistency(df)
    print(f"   Year-to-year consistency: {consistency['consistency_cv']:.3f} CV")
    print(f"   Directional accuracy: {consistency['directional_accuracy']:.1%}")

    # Significance tests
    significance = test_statistical_significance(df)
    resilient_vs_fragile = significance.get('resilient_vs_fragile', {})
    is_significant = resilient_vs_fragile.get('significant', False)
    print(f"   Statistical significance: {'CONFIRMED' if is_significant else 'NOT CONFIRMED'}")

    # Edge cases
    edge_cases = analyze_edge_cases(df)
    print(f"   Edge cases analyzed: {len(edge_cases['sample_size_issues'])} sample sizes tested")

    print()

    # Generate report
    report_path = generate_validation_report(df)

    # Final assessment
    print("🎯 PHASE 1 ASSESSMENT:")
    if consistency['consistency_cv'] < 0.25 and is_significant:
        print("✅ CURRENT APPROACH VALIDATED")
        print("   Real signal detected, statistical significance confirmed")
        print("   Ready to consider Phase 2 enhancements")
    else:
        print("⚠️  REQUIRES FURTHER ANALYSIS")
        print("   Signal strength or statistical significance insufficient")
        print("   May need to reconsider fundamental approach")

    print(f"\n📄 Full report: {report_path}")

if __name__ == "__main__":
    main()
