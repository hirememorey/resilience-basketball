#!/usr/bin/env python3
"""
First Principles Data Completeness Analysis

Analyzes the predictive dataset to identify missing metrics and data gaps.
"""

import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def analyze_data_completeness():
    """Analyze data completeness across all features."""
    
    print("=" * 80)
    print("DATA COMPLETENESS ANALYSIS - First Principles Deep Dive")
    print("=" * 80)
    print()
    
    # Load predictive dataset
    df = pd.read_csv('results/predictive_dataset.csv')
    total_rows = len(df)
    
    print(f"Total player-seasons: {total_rows:,}")
    print()
    
    # Get all columns except identifiers
    id_cols = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON']
    feature_cols = [c for c in df.columns if c not in id_cols]
    
    print(f"Total feature columns: {len(feature_cols)}")
    print()
    
    # Analyze coverage
    print("=" * 80)
    print("COVERAGE ANALYSIS BY FEATURE")
    print("=" * 80)
    print()
    
    coverage_data = []
    for col in sorted(feature_cols):
        missing = df[col].isna().sum()
        coverage_pct = (1 - missing / total_rows) * 100
        coverage_data.append({
            'feature': col,
            'coverage_pct': coverage_pct,
            'missing_count': missing,
            'present_count': total_rows - missing
        })
    
    coverage_df = pd.DataFrame(coverage_data)
    
    # Critical features (from KEY_INSIGHTS.md and code analysis)
    critical_features = [
        'LEVERAGE_TS_DELTA', 'LEVERAGE_USG_DELTA',  # #1 predictor
        'CREATION_VOLUME_RATIO', 'CREATION_TAX',  # Creation vector
        'RS_PRESSURE_APPETITE', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE',  # Pressure vector
        'RS_RIM_APPETITE',  # Physicality vector
        'ISO_FREQUENCY', 'PNR_HANDLER_FREQUENCY',  # Self-creation (Bag Check Gate)
        'EFG_ISO_WEIGHTED', 'EFG_PCT_0_DRIBBLE',  # Efficiency metrics
        'USG_PCT', 'AGE',  # Metadata
    ]
    
    print("CRITICAL FEATURES (< 95% coverage):")
    print("-" * 80)
    critical_missing = []
    for feat in critical_features:
        if feat in coverage_df['feature'].values:
            row = coverage_df[coverage_df['feature'] == feat].iloc[0]
            if row['coverage_pct'] < 95:
                print(f"  ❌ {feat:40s} {row['coverage_pct']:6.1f}% ({row['missing_count']:,} missing)")
                critical_missing.append(feat)
            else:
                print(f"  ✅ {feat:40s} {row['coverage_pct']:6.1f}%")
        else:
            print(f"  ⚠️  {feat:40s} NOT FOUND IN DATASET")
            critical_missing.append(feat)
    
    print()
    print("ALL FEATURES WITH < 95% COVERAGE:")
    print("-" * 80)
    low_coverage = coverage_df[coverage_df['coverage_pct'] < 95].sort_values('coverage_pct')
    for _, row in low_coverage.iterrows():
        status = "❌ CRITICAL" if row['feature'] in critical_features else "⚠️  LOW"
        print(f"  {status} {row['feature']:40s} {row['coverage_pct']:6.1f}% ({row['missing_count']:,} missing)")
    
    print()
    print("=" * 80)
    print("MISSING DATA ROOT CAUSE ANALYSIS")
    print("=" * 80)
    print()
    
    # Analyze ISO_FREQUENCY and PNR_HANDLER_FREQUENCY specifically
    if 'ISO_FREQUENCY' in df.columns:
        iso_coverage = df['ISO_FREQUENCY'].notna().sum() / total_rows * 100
        print(f"ISO_FREQUENCY Coverage: {iso_coverage:.1f}%")
        print(f"  Missing: {df['ISO_FREQUENCY'].isna().sum():,} player-seasons")
        print(f"  Present: {df['ISO_FREQUENCY'].notna().sum():,} player-seasons")
        
        # Check if missing data correlates with specific seasons
        if df['ISO_FREQUENCY'].isna().sum() > 0:
            missing_by_season = df[df['ISO_FREQUENCY'].isna()].groupby('SEASON').size()
            print(f"  Missing by season:")
            for season, count in missing_by_season.items():
                print(f"    {season}: {count:,} missing")
    
    print()
    if 'PNR_HANDLER_FREQUENCY' in df.columns:
        pnr_coverage = df['PNR_HANDLER_FREQUENCY'].notna().sum() / total_rows * 100
        print(f"PNR_HANDLER_FREQUENCY Coverage: {pnr_coverage:.1f}%")
        print(f"  Missing: {df['PNR_HANDLER_FREQUENCY'].isna().sum():,} player-seasons")
        print(f"  Present: {df['PNR_HANDLER_FREQUENCY'].notna().sum():,} player-seasons")
    
    print()
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    print("1. CRITICAL: Collect ISO_FREQUENCY and PNR_HANDLER_FREQUENCY for all players")
    print("   - These are used for SELF_CREATED_FREQ (Bag Check Gate)")
    print("   - Current coverage: 8.6% (CRITICAL GAP)")
    print("   - Action: Run populate_playtype_data.py for all seasons 2015-2024")
    print()
    
    print("2. Verify data collection pipeline:")
    print("   - Check if populate_playtype_data.py collects for ALL players or just qualified players")
    print("   - Ensure evaluate_plasticity_potential.py merges playtype data correctly")
    print()
    
    print("3. Other potential missing metrics to investigate:")
    for feat in critical_missing:
        if feat not in ['ISO_FREQUENCY', 'PNR_HANDLER_FREQUENCY']:
            print(f"   - {feat}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Total features analyzed: {len(feature_cols)}")
    print(f"Features with < 95% coverage: {len(low_coverage)}")
    print(f"Critical features missing: {len([f for f in critical_missing if f in df.columns])}")
    print()
    
    # Save detailed report
    output_path = Path('results/data_completeness_analysis.csv')
    coverage_df.to_csv(output_path, index=False)
    print(f"Detailed coverage report saved to: {output_path}")
    
    return coverage_df

if __name__ == '__main__':
    analyze_data_completeness()

