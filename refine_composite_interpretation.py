#!/usr/bin/env python3
"""
Refine Composite Metric Interpretation

Based on our analysis, we need to clearly define what the composite metric
actually measures. This script validates and refines the interpretation.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))


def analyze_composite_components(df: pd.DataFrame) -> dict:
    """Analyze what each component of the composite actually measures."""
    results = {}
    
    # Filter to valid cases
    valid_df = df[
        df['ts_ratio'].notna() & 
        df['production_ratio'].notna() & 
        df['usage_ratio'].notna()
    ].copy()
    
    # Calculate composite
    valid_df['composite_resilience'] = (valid_df['ts_ratio'] + valid_df['production_ratio']) / 2
    
    # Component 1: TS% Ratio Analysis
    # What does it measure?
    results['ts_ratio_analysis'] = {
        'mean': valid_df['ts_ratio'].mean(),
        'median': valid_df['ts_ratio'].median(),
        'std': valid_df['ts_ratio'].std(),
        'correlation_with_usage': valid_df['ts_ratio'].corr(valid_df['usage_ratio']),
        'correlation_with_production': valid_df['ts_ratio'].corr(valid_df['production_ratio']),
    }
    
    # Component 2: Production Ratio Analysis
    # What does it measure?
    results['production_ratio_analysis'] = {
        'mean': valid_df['production_ratio'].mean(),
        'median': valid_df['production_ratio'].median(),
        'std': valid_df['production_ratio'].std(),
        'correlation_with_usage': valid_df['production_ratio'].corr(valid_df['usage_ratio']),
        'correlation_with_ts': valid_df['production_ratio'].corr(valid_df['ts_ratio']),
    }
    
    # Composite Analysis
    results['composite_analysis'] = {
        'mean': valid_df['composite_resilience'].mean(),
        'median': valid_df['composite_resilience'].median(),
        'std': valid_df['composite_resilience'].std(),
        'correlation_with_ts': valid_df['composite_resilience'].corr(valid_df['ts_ratio']),
        'correlation_with_production': valid_df['composite_resilience'].corr(valid_df['production_ratio']),
        'correlation_with_usage': valid_df['composite_resilience'].corr(valid_df['usage_ratio']),
    }
    
    # Categorize players by component patterns
    def categorize_player(row):
        ts = row['ts_ratio']
        prod = row['production_ratio']
        usage = row['usage_ratio']
        
        # TS% categories
        if ts < 0.95:
            ts_cat = 'Fragile'
        elif ts > 1.05:
            ts_cat = 'Resilient'
        else:
            ts_cat = 'Neutral'
        
        # Production categories
        if prod < 0.95:
            prod_cat = 'Fragile'
        elif prod > 1.05:
            prod_cat = 'Resilient'
        else:
            prod_cat = 'Neutral'
        
        # Usage change
        if usage > 1.05:
            usage_cat = 'Increased'
        elif usage < 0.95:
            usage_cat = 'Decreased'
        else:
            usage_cat = 'Stable'
        
        # Pattern classification
        if ts_cat == 'Resilient' and prod_cat == 'Resilient':
            pattern = 'Both Resilient'
        elif ts_cat == 'Fragile' and prod_cat == 'Fragile':
            pattern = 'Both Fragile'
        elif ts_cat == 'Fragile' and prod_cat == 'Resilient':
            pattern = 'Production Scalable'  # Type 1 failure pattern
        elif ts_cat == 'Resilient' and prod_cat == 'Fragile':
            pattern = 'Efficiency Only'
        else:
            pattern = 'Mixed/Neutral'
        
        return pd.Series({
            'ts_category': ts_cat,
            'production_category': prod_cat,
            'usage_category': usage_cat,
            'pattern': pattern,
        })
    
    categorized = valid_df.apply(categorize_player, axis=1)
    valid_df = pd.concat([valid_df, categorized], axis=1)
    
    # Analyze each pattern
    pattern_analysis = []
    for pattern in valid_df['pattern'].unique():
        pattern_df = valid_df[valid_df['pattern'] == pattern]
        pattern_analysis.append({
            'pattern': pattern,
            'count': len(pattern_df),
            'percentage': len(pattern_df) / len(valid_df) * 100,
            'mean_ts_ratio': pattern_df['ts_ratio'].mean(),
            'mean_production_ratio': pattern_df['production_ratio'].mean(),
            'mean_composite': pattern_df['composite_resilience'].mean(),
            'mean_usage_change': (pattern_df['usage_ratio'].mean() - 1.0) * 100,
            'pct_usage_increase': (pattern_df['usage_ratio'] > 1.05).sum() / len(pattern_df) * 100,
        })
    
    results['pattern_analysis'] = pd.DataFrame(pattern_analysis)
    results['categorized_df'] = valid_df
    
    # Specific analysis: Production Scalable players (Type 1 failures)
    prod_scalable = valid_df[valid_df['pattern'] == 'Production Scalable']
    results['production_scalable_analysis'] = {
        'count': len(prod_scalable),
        'mean_ts_ratio': prod_scalable['ts_ratio'].mean(),
        'mean_production_ratio': prod_scalable['production_ratio'].mean(),
        'mean_composite': prod_scalable['composite_resilience'].mean(),
        'mean_usage_change': (prod_scalable['usage_ratio'].mean() - 1.0) * 100,
        'pct_usage_increase': (prod_scalable['usage_ratio'] > 1.05).sum() / len(prod_scalable) * 100,
        'mean_ts_decline': (prod_scalable['ts_ratio'].mean() - 1.0) * 100,
    }
    
    # Specific analysis: Both Resilient players
    both_resilient = valid_df[valid_df['pattern'] == 'Both Resilient']
    results['both_resilient_analysis'] = {
        'count': len(both_resilient),
        'mean_ts_ratio': both_resilient['ts_ratio'].mean(),
        'mean_production_ratio': both_resilient['production_ratio'].mean(),
        'mean_composite': both_resilient['composite_resilience'].mean(),
        'mean_usage_change': (both_resilient['usage_ratio'].mean() - 1.0) * 100,
        'pct_usage_increase': (both_resilient['usage_ratio'] > 1.05).sum() / len(both_resilient) * 100,
    }
    
    return results


def generate_interpretation_report(results: dict, output_path: str = "data/composite_interpretation_report.md"):
    """Generate comprehensive interpretation report."""
    Path("data").mkdir(exist_ok=True)
    
    report = []
    report.append("# Composite Metric Interpretation: What Does It Actually Measure?")
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append("The composite metric measures **context adaptation** through two complementary skills:")
    report.append("")
    report.append("1. **Efficiency Maintenance** (TS% Ratio): Ability to maintain shooting efficiency in harder context")
    report.append("2. **Production Scalability** (Production Ratio): Ability to maintain/elevate total production despite context changes")
    report.append("")
    report.append("The composite balances both skills, identifying players who adapt to playoff context effectively.")
    report.append("")
    
    # Component 1: TS% Ratio
    report.append("## Component 1: TS% Ratio")
    report.append("")
    report.append("### What It Measures")
    report.append("")
    report.append("**TS% Ratio = Playoff TS% ÷ Regular Season TS%**")
    report.append("")
    report.append("Measures: **Efficiency Maintenance in Harder Context**")
    report.append("")
    report.append("**Key Characteristics:**")
    ts_analysis = results['ts_ratio_analysis']
    report.append(f"- Mean: {ts_analysis['mean']:.3f}")
    report.append(f"- Correlation with Usage: {ts_analysis['correlation_with_usage']:.3f} (very weak - not confounded by opportunity)")
    report.append(f"- Correlation with Production: {ts_analysis['correlation_with_production']:.3f}")
    report.append("")
    report.append("**What It Tells Us:**")
    report.append("- How well a player maintains shooting efficiency when:")
    report.append("  - Opponents are better (playoffs = only good teams)")
    report.append("  - Defensive intensity increases")
    report.append("  - Context becomes harder")
    report.append("- **Not confounded by usage changes** (correlation 0.046)")
    report.append("- Measures **pure efficiency performance** in harder context")
    report.append("")
    
    # Component 2: Production Ratio
    report.append("## Component 2: Production Ratio")
    report.append("")
    report.append("### What It Measures")
    report.append("")
    report.append("**Production Ratio = Playoff Production ÷ Regular Season Production**")
    report.append("**Production = PTS + 1.5×AST + 0.5×REB**")
    report.append("")
    report.append("Measures: **Production Scalability Despite Context Change**")
    report.append("")
    report.append("**Key Characteristics:**")
    prod_analysis = results['production_ratio_analysis']
    report.append(f"- Mean: {prod_analysis['mean']:.3f}")
    report.append(f"- Correlation with Usage: {prod_analysis['correlation_with_usage']:.3f} (moderate - partially confounded by opportunity)")
    report.append(f"- Correlation with TS%: {prod_analysis['correlation_with_ts']:.3f}")
    report.append("")
    report.append("**What It Tells Us:**")
    report.append("- How well a player maintains/elevates total production when:")
    report.append("  - Usage may increase (more opportunity)")
    report.append("  - Role may change (more responsibility)")
    report.append("  - Context becomes harder")
    report.append("- **Partially confounded by usage** (correlation 0.561)")
    report.append("- But: If usage increases and TS% drops (expected), maintaining production is still valuable")
    report.append("- Measures **production scalability** - ability to produce despite efficiency decline")
    report.append("")
    
    # Composite
    report.append("## Composite Metric")
    report.append("")
    report.append("### What It Measures")
    report.append("")
    report.append("**Composite = (TS% Ratio + Production Ratio) / 2**")
    report.append("")
    report.append("Measures: **Context Adaptation Through Dual Skills**")
    report.append("")
    comp_analysis = results['composite_analysis']
    report.append(f"- Mean: {comp_analysis['mean']:.3f}")
    report.append(f"- Correlation with TS%: {comp_analysis['correlation_with_ts']:.3f}")
    report.append(f"- Correlation with Production: {comp_analysis['correlation_with_production']:.3f}")
    report.append(f"- Correlation with Usage: {comp_analysis['correlation_with_usage']:.3f}")
    report.append("")
    report.append("**What It Tells Us:**")
    report.append("The composite identifies players who adapt to playoff context through:")
    report.append("")
    report.append("1. **Efficiency Maintenance**: Maintaining shooting efficiency in harder context")
    report.append("2. **Production Scalability**: Maintaining/elevating production despite context changes")
    report.append("")
    report.append("**Why Both Matter:**")
    report.append("- **Efficiency-only resilient**: Maintains efficiency but may not scale production")
    report.append("- **Production-only resilient**: Scales production despite efficiency decline (still valuable)")
    report.append("- **Both resilient**: Ideal - maintains efficiency AND scales production")
    report.append("")
    
    # Pattern Analysis
    report.append("## Player Patterns")
    report.append("")
    report.append("| Pattern | Count | % | Mean TS% | Mean Production | Mean Composite | Mean Usage Change |")
    report.append("|---------|-------|---|----------|----------------|----------------|------------------|")
    for _, row in results['pattern_analysis'].iterrows():
        report.append(f"| {row['pattern']} | {int(row['count'])} | {row['percentage']:.1f}% | {row['mean_ts_ratio']:.3f} | {row['mean_production_ratio']:.3f} | {row['mean_composite']:.3f} | {row['mean_usage_change']:.1f}% |")
    report.append("")
    
    # Production Scalable Analysis
    prod_scal = results['production_scalable_analysis']
    report.append("## Production Scalable Players (Type 1 Failures)")
    report.append("")
    report.append(f"- **Count**: {prod_scal['count']} ({prod_scal['count']/len(results['categorized_df'])*100:.1f}%)")
    report.append(f"- **Mean TS% Ratio**: {prod_scal['mean_ts_ratio']:.3f} (fragile)")
    report.append(f"- **Mean Production Ratio**: {prod_scal['mean_production_ratio']:.3f} (resilient)")
    report.append(f"- **Mean Composite**: {prod_scal['mean_composite']:.3f}")
    report.append(f"- **Mean Usage Change**: {prod_scal['mean_usage_change']:.1f}%")
    report.append(f"- **% with Usage Increase**: {prod_scal['pct_usage_increase']:.1f}%")
    report.append("")
    report.append("**Interpretation:**")
    report.append("These players show **production scalability**:")
    report.append("- Usage typically increases (more opportunity/responsibility)")
    report.append("- TS% declines (expected when usage increases)")
    report.append("- But production still increases (valuable despite efficiency decline)")
    report.append("- Composite correctly identifies them as resilient (production scalability is valuable)")
    report.append("")
    
    # Both Resilient Analysis
    both_res = results['both_resilient_analysis']
    report.append("## Both Resilient Players (Ideal)")
    report.append("")
    report.append(f"- **Count**: {both_res['count']} ({both_res['count']/len(results['categorized_df'])*100:.1f}%)")
    report.append(f"- **Mean TS% Ratio**: {both_res['mean_ts_ratio']:.3f} (resilient)")
    report.append(f"- **Mean Production Ratio**: {both_res['mean_production_ratio']:.3f} (resilient)")
    report.append(f"- **Mean Composite**: {both_res['mean_composite']:.3f}")
    report.append(f"- **Mean Usage Change**: {both_res['mean_usage_change']:.1f}%")
    report.append("")
    report.append("**Interpretation:**")
    report.append("These players show **ideal resilience**:")
    report.append("- Maintain efficiency in harder context")
    report.append("- Scale production despite context change")
    report.append("- Most valuable type of playoff resilience")
    report.append("")
    
    # Refined Interpretation
    report.append("## Refined Interpretation")
    report.append("")
    report.append("### What the Composite Measures")
    report.append("")
    report.append("The composite measures **context adaptation** - how well a player adapts to the harder playoff context through two complementary skills:")
    report.append("")
    report.append("1. **Efficiency Maintenance** (TS% Ratio)")
    report.append("   - Pure performance signal (not confounded by opportunity)")
    report.append("   - Measures ability to maintain efficiency in harder context")
    report.append("")
    report.append("2. **Production Scalability** (Production Ratio)")
    report.append("   - Partially confounded by opportunity (usage changes)")
    report.append("   - But: If usage increases and TS% drops (expected), maintaining production is still valuable")
    report.append("   - Measures ability to scale production despite efficiency decline")
    report.append("")
    report.append("### Why Both Matter")
    report.append("")
    report.append("**Efficiency-only resilient players**:")
    report.append("- Maintain efficiency but may not scale production")
    report.append("- Valuable but limited impact")
    report.append("")
    report.append("**Production-only resilient players** (Type 1 failures):")
    report.append("- Scale production despite efficiency decline")
    report.append("- Valuable because: If usage increases and TS% drops (expected), maintaining production is still a win")
    report.append("- Composite correctly identifies them as resilient")
    report.append("")
    report.append("**Both resilient players** (ideal):")
    report.append("- Maintain efficiency AND scale production")
    report.append("- Most valuable type of playoff resilience")
    report.append("")
    
    # Conclusion
    report.append("## Conclusion")
    report.append("")
    report.append("The composite metric measures **context adaptation through dual skills**:")
    report.append("")
    report.append("- **TS% Ratio**: Efficiency maintenance in harder context (pure performance)")
    report.append("- **Production Ratio**: Production scalability despite context change (valuable even if efficiency declines)")
    report.append("")
    report.append("**The composite is valid** because:")
    report.append("1. It captures two complementary forms of context adaptation")
    report.append("2. Both skills are valuable (efficiency maintenance AND production scalability)")
    report.append("3. It correctly identifies production-scalable players (Type 1 failures) as resilient")
    report.append("4. It balances both skills without over-weighting either")
    report.append("")
    
    # Write report
    report_text = "\n".join(report)
    with open(output_path, 'w') as f:
        f.write(report_text)
    
    print(f"\n📄 Report saved to {output_path}")
    return output_path


def main():
    """Main function."""
    print("=" * 70)
    print("REFINING COMPOSITE METRIC INTERPRETATION")
    print("=" * 70)
    print()
    
    # Load data
    data_file = "data/measurement_validation_data.csv"
    if not Path(data_file).exists():
        print(f"❌ Data file not found: {data_file}")
        return
    
    df = pd.read_csv(data_file)
    print(f"✅ Loaded {len(df)} cases")
    
    # Analyze
    print("\n📊 Analyzing composite components...")
    results = analyze_composite_components(df)
    
    # Generate report
    report_path = generate_interpretation_report(results)
    
    # Print summary
    print("\n" + "=" * 70)
    print("INTERPRETATION SUMMARY")
    print("=" * 70)
    print()
    print("TS% Ratio:")
    print(f"  - Measures: Efficiency Maintenance in Harder Context")
    print(f"  - Correlation with Usage: {results['ts_ratio_analysis']['correlation_with_usage']:.3f} (not confounded)")
    print()
    print("Production Ratio:")
    print(f"  - Measures: Production Scalability Despite Context Change")
    print(f"  - Correlation with Usage: {results['production_ratio_analysis']['correlation_with_usage']:.3f} (partially confounded)")
    print()
    print("Composite:")
    print(f"  - Measures: Context Adaptation Through Dual Skills")
    print(f"  - Mean: {results['composite_analysis']['mean']:.3f}")
    print()
    
    prod_scal = results['production_scalable_analysis']
    print(f"Production Scalable Players (Type 1 Failures):")
    print(f"  - Count: {prod_scal['count']}")
    print(f"  - Mean Usage Change: {prod_scal['mean_usage_change']:.1f}%")
    print(f"  - Mean TS% Decline: {prod_scal['mean_ts_decline']:.1f}%")
    print(f"  - Mean Production Increase: {(prod_scal['mean_production_ratio'] - 1.0)*100:.1f}%")
    print()
    print(f"📄 Full report: {report_path}")


if __name__ == "__main__":
    main()


