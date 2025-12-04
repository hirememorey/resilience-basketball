#!/usr/bin/env python3
"""
Analyze Usage-TS% Relationship: Does TS% Drop When Usage Increases?

This script tests the hypothesis that when usage increases, TS% typically drops.
If true, maintaining TS% at higher usage is valuable (scalability).

Key Questions:
1. When usage increases, does TS% typically drop?
2. What's the relationship between usage change and TS% change?
3. Are players who maintain TS% at higher usage actually scalable?
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))


def analyze_usage_ts_relationship(df: pd.DataFrame) -> dict:
    """Analyze the relationship between usage changes and TS% changes."""
    results = {}
    
    # Filter to cases with valid usage data
    valid_df = df[df['usage_ratio'].notna() & df['ts_ratio'].notna()].copy()
    
    results['total_cases'] = len(valid_df)
    
    # Calculate TS% change (difference from 1.0)
    valid_df['ts_change'] = valid_df['ts_ratio'] - 1.0
    valid_df['usage_change'] = valid_df['usage_ratio'] - 1.0
    
    # Correlation
    correlation = valid_df['usage_change'].corr(valid_df['ts_change'])
    results['correlation'] = correlation
    
    # Group by usage change categories
    def categorize_usage_change(change):
        if change < -0.1:  # >10% decrease
            return 'Large Decrease (>10%)'
        elif change < -0.05:  # 5-10% decrease
            return 'Moderate Decrease (5-10%)'
        elif change < 0.05:  # -5% to +5% (stable)
            return 'Stable (-5% to +5%)'
        elif change < 0.1:  # 5-10% increase
            return 'Moderate Increase (5-10%)'
        else:  # >10% increase
            return 'Large Increase (>10%)'
    
    valid_df['usage_category'] = valid_df['usage_change'].apply(categorize_usage_change)
    
    # Analyze TS% change by usage category
    usage_analysis = []
    for category in valid_df['usage_category'].unique():
        category_df = valid_df[valid_df['usage_category'] == category]
        usage_analysis.append({
            'usage_category': category,
            'count': len(category_df),
            'mean_ts_change': category_df['ts_change'].mean(),
            'mean_ts_ratio': category_df['ts_ratio'].mean(),
            'median_ts_change': category_df['ts_change'].median(),
            'std_ts_change': category_df['ts_change'].std(),
            'pct_ts_decline': (category_df['ts_change'] < 0).sum() / len(category_df) * 100,
        })
    
    results['usage_category_analysis'] = pd.DataFrame(usage_analysis)
    
    # Focus on usage increases
    usage_increase = valid_df[valid_df['usage_change'] > 0.05]  # >5% increase
    usage_decrease = valid_df[valid_df['usage_change'] < -0.05]  # >5% decrease
    usage_stable = valid_df[abs(valid_df['usage_change']) <= 0.05]  # Stable
    
    results['usage_increase_analysis'] = {
        'count': len(usage_increase),
        'mean_ts_change': usage_increase['ts_change'].mean(),
        'mean_ts_ratio': usage_increase['ts_ratio'].mean(),
        'pct_ts_decline': (usage_increase['ts_change'] < 0).sum() / len(usage_increase) * 100,
        'pct_ts_maintain_or_improve': (usage_increase['ts_change'] >= 0).sum() / len(usage_increase) * 100,
    }
    
    results['usage_decrease_analysis'] = {
        'count': len(usage_decrease),
        'mean_ts_change': usage_decrease['ts_change'].mean(),
        'mean_ts_ratio': usage_decrease['ts_ratio'].mean(),
        'pct_ts_decline': (usage_decrease['ts_change'] < 0).sum() / len(usage_decrease) * 100,
    }
    
    results['usage_stable_analysis'] = {
        'count': len(usage_stable),
        'mean_ts_change': usage_stable['ts_change'].mean(),
        'mean_ts_ratio': usage_stable['ts_ratio'].mean(),
        'pct_ts_decline': (usage_stable['ts_change'] < 0).sum() / len(usage_stable) * 100,
    }
    
    # Statistical test: Does TS% drop more when usage increases?
    if len(usage_increase) > 0 and len(usage_stable) > 0:
        t_stat, p_value = stats.ttest_ind(usage_increase['ts_change'], usage_stable['ts_change'])
        results['statistical_test'] = {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'interpretation': 'Usage increase causes TS% decline' if p_value < 0.05 and usage_increase['ts_change'].mean() < usage_stable['ts_change'].mean() else 'No significant difference',
        }
    
    # Identify scalable players (usage increases, TS% maintains/improves)
    scalable = valid_df[
        (valid_df['usage_change'] > 0.05) &  # Usage increases >5%
        (valid_df['ts_change'] >= -0.02)  # TS% declines <2% (essentially maintains)
    ]
    
    results['scalable_players'] = {
        'count': len(scalable),
        'percentage': len(scalable) / len(valid_df) * 100,
        'mean_usage_increase': scalable['usage_change'].mean() * 100,
        'mean_ts_change': scalable['ts_change'].mean() * 100,
        'mean_production_ratio': scalable['production_ratio'].mean(),
        'players': scalable[['player_name', 'season', 'usage_change', 'ts_change', 'production_ratio']].to_dict('records'),
    }
    
    # Compare scalable players to Type 1 failures
    # Type 1 failures: TS% says fragile, Production says resilient
    type1_failures = valid_df[
        (valid_df['ts_ratio'] < 0.95) & 
        (valid_df['production_ratio'] > 1.05)
    ]
    
    # Are Type 1 failures actually scalable?
    type1_scalable = type1_failures[
        (type1_failures['usage_change'] > 0.05) &
        (type1_failures['ts_change'] >= -0.05)  # TS% decline <5%
    ]
    
    results['type1_scalability'] = {
        'type1_total': len(type1_failures),
        'type1_scalable_count': len(type1_scalable),
        'type1_scalable_percentage': len(type1_scalable) / len(type1_failures) * 100 if len(type1_failures) > 0 else 0,
        'mean_usage_increase': type1_scalable['usage_change'].mean() * 100 if len(type1_scalable) > 0 else None,
        'mean_ts_change': type1_scalable['ts_change'].mean() * 100 if len(type1_scalable) > 0 else None,
    }
    
    return results


def generate_report(results: dict, output_path: str = "data/usage_ts_relationship_report.md"):
    """Generate comprehensive report."""
    Path("data").mkdir(exist_ok=True)
    
    report = []
    report.append("# Usage-TS% Relationship Analysis")
    report.append("")
    report.append("## Key Question: Does TS% Drop When Usage Increases?")
    report.append("")
    report.append(f"**Total Cases Analyzed**: {results['total_cases']}")
    report.append(f"**Correlation (Usage Change vs TS% Change)**: {results['correlation']:.3f}")
    report.append("")
    
    # Main finding
    if results['usage_increase_analysis']['pct_ts_decline'] > 50:
        report.append("### ✅ HYPOTHESIS VALIDATED")
        report.append("")
        report.append(f"When usage increases, **{results['usage_increase_analysis']['pct_ts_decline']:.1f}%** of players see TS% decline.")
        report.append("")
        report.append("**Implication**: Maintaining TS% at higher usage is valuable (scalability).")
    else:
        report.append("### ❌ HYPOTHESIS NOT VALIDATED")
        report.append("")
        report.append(f"When usage increases, only {results['usage_increase_analysis']['pct_ts_decline']:.1f}% of players see TS% decline.")
        report.append("")
        report.append("**Implication**: Usage increase may not cause TS% decline.")
    report.append("")
    
    # Usage category analysis
    report.append("## TS% Change by Usage Category")
    report.append("")
    report.append("| Usage Change | Cases | Mean TS% Change | Mean TS% Ratio | % TS% Decline |")
    report.append("|--------------|-------|-----------------|----------------|----------------|")
    for _, row in results['usage_category_analysis'].iterrows():
        report.append(f"| {row['usage_category']} | {int(row['count'])} | {row['mean_ts_change']:.3f} | {row['mean_ts_ratio']:.3f} | {row['pct_ts_decline']:.1f}% |")
    report.append("")
    
    # Usage increase analysis
    report.append("## Usage Increase Analysis")
    report.append("")
    inc = results['usage_increase_analysis']
    report.append(f"- **Cases with Usage Increase (>5%)**: {inc['count']}")
    report.append(f"- **Mean TS% Change**: {inc['mean_ts_change']:.3f} ({inc['mean_ts_change']*100:.1f}%)")
    report.append(f"- **Mean TS% Ratio**: {inc['mean_ts_ratio']:.3f}")
    report.append(f"- **% with TS% Decline**: {inc['pct_ts_decline']:.1f}%")
    report.append(f"- **% with TS% Maintain/Improve**: {inc['pct_ts_maintain_or_improve']:.1f}%")
    report.append("")
    
    # Statistical test
    if 'statistical_test' in results:
        test = results['statistical_test']
        report.append("## Statistical Test")
        report.append("")
        report.append(f"- **T-statistic**: {test['t_statistic']:.3f}")
        report.append(f"- **P-value**: {test['p_value']:.4f}")
        report.append(f"- **Significant**: {'Yes' if test['significant'] else 'No'}")
        report.append(f"- **Interpretation**: {test['interpretation']}")
        report.append("")
    
    # Scalable players
    scalable = results['scalable_players']
    report.append("## Scalable Players (Usage Increases, TS% Maintains)")
    report.append("")
    report.append(f"- **Count**: {scalable['count']} ({scalable['percentage']:.1f}% of total)")
    report.append(f"- **Mean Usage Increase**: {scalable['mean_usage_increase']:.1f}%")
    report.append(f"- **Mean TS% Change**: {scalable['mean_ts_change']:.1f}%")
    report.append(f"- **Mean Production Ratio**: {scalable['mean_production_ratio']:.3f}")
    report.append("")
    
    if scalable['count'] > 0:
        report.append("**Top 10 Scalable Players:**")
        report.append("")
        report.append("| Player | Season | Usage Change | TS% Change | Production Ratio |")
        report.append("|--------|--------|--------------|------------|-----------------|")
        top_scalable = sorted(scalable['players'], key=lambda x: x['usage_change'], reverse=True)[:10]
        for player in top_scalable:
            report.append(f"| {player['player_name']} | {player['season']} | {player['usage_change']*100:.1f}% | {player['ts_change']*100:.1f}% | {player['production_ratio']:.3f} |")
        report.append("")
    
    # Type 1 failures and scalability
    type1 = results['type1_scalability']
    report.append("## Type 1 Failures: Are They Scalable?")
    report.append("")
    report.append(f"- **Total Type 1 Failures**: {type1['type1_total']}")
    report.append(f"- **Scalable Type 1 Failures**: {type1['type1_scalable_count']} ({type1['type1_scalable_percentage']:.1f}%)")
    if type1['type1_scalable_count'] > 0:
        report.append(f"- **Mean Usage Increase**: {type1['mean_usage_increase']:.1f}%")
        report.append(f"- **Mean TS% Change**: {type1['mean_ts_change']:.1f}%")
    report.append("")
    
    if type1['type1_scalable_percentage'] > 50:
        report.append("**✅ INSIGHT**: Most Type 1 failures are actually scalable players!")
        report.append("")
        report.append("This validates that production ratio measures scalability, not just opportunity.")
    else:
        report.append("**⚠️ MIXED**: Some Type 1 failures are scalable, but not all.")
    report.append("")
    
    # Conclusions
    report.append("## Conclusions")
    report.append("")
    if results['usage_increase_analysis']['pct_ts_decline'] > 50:
        report.append("1. **Usage increase typically causes TS% decline** - Maintaining TS% at higher usage is valuable")
        report.append("2. **Production ratio may measure scalability** - Ability to maintain/elevate production at higher usage")
        report.append("3. **Composite metric captures two skills**:")
        report.append("   - TS% ratio: Efficiency maintenance in harder context")
        report.append("   - Production ratio: Scalability (maintaining production despite usage increase)")
    else:
        report.append("1. **Usage increase does not typically cause TS% decline** - Need to reconsider hypothesis")
    report.append("")
    
    # Write report
    report_text = "\n".join(report)
    with open(output_path, 'w') as f:
        f.write(report_text)
    
    print(f"\n📄 Report saved to {output_path}")
    return output_path


def main():
    """Main analysis function."""
    print("=" * 70)
    print("USAGE-TS% RELATIONSHIP ANALYSIS")
    print("=" * 70)
    print()
    print("Testing hypothesis: Does TS% drop when usage increases?")
    print()
    
    # Load measurement validation data
    data_file = "data/measurement_validation_data.csv"
    if not Path(data_file).exists():
        print(f"❌ Data file not found: {data_file}")
        print("   Run validate_measurement_assumptions.py first")
        return
    
    df = pd.read_csv(data_file)
    print(f"✅ Loaded {len(df)} cases")
    
    # Analyze
    print("\n📊 Analyzing usage-TS% relationship...")
    results = analyze_usage_ts_relationship(df)
    
    # Generate report
    report_path = generate_report(results)
    
    # Print summary
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"Total cases: {results['total_cases']}")
    print(f"Correlation (Usage vs TS%): {results['correlation']:.3f}")
    print()
    
    inc = results['usage_increase_analysis']
    print(f"When usage increases (>5%):")
    print(f"  - Cases: {inc['count']}")
    print(f"  - Mean TS% change: {inc['mean_ts_change']*100:.1f}%")
    print(f"  - % with TS% decline: {inc['pct_ts_decline']:.1f}%")
    print()
    
    scalable = results['scalable_players']
    print(f"Scalable players (usage ↑, TS% maintains):")
    print(f"  - Count: {scalable['count']} ({scalable['percentage']:.1f}%)")
    print(f"  - Mean production ratio: {scalable['mean_production_ratio']:.3f}")
    print()
    
    type1 = results['type1_scalability']
    print(f"Type 1 failures that are scalable:")
    print(f"  - {type1['type1_scalable_count']}/{type1['type1_total']} ({type1['type1_scalable_percentage']:.1f}%)")
    print()
    
    if inc['pct_ts_decline'] > 50:
        print("✅ HYPOTHESIS VALIDATED: TS% typically drops when usage increases")
        print("   → Maintaining TS% at higher usage is valuable (scalability)")
    else:
        print("❌ HYPOTHESIS NOT VALIDATED: TS% does not typically drop")
    print()
    print(f"📄 Full report: {report_path}")


if __name__ == "__main__":
    main()




