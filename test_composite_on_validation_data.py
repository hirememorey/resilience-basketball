#!/usr/bin/env python3
"""
Test Composite Metric on Validation Dataset

This script tests whether the composite metric fixes Type 1 failures identified
in the problem validation. It calculates composite scores for all cases in the
validation dataset and compares composite vs TS% performance.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from calculate_composite_resilience import CompositeResilienceCalculator


class CompositeValidator:
    """Tests composite metric on validation dataset."""
    
    def __init__(self):
        self.calculator = CompositeResilienceCalculator()
    
    def load_validation_data(self, filepath: str = "data/problem_validation_data.csv") -> pd.DataFrame:
        """Load the validation dataset."""
        if not Path(filepath).exists():
            raise FileNotFoundError(f"Validation data not found: {filepath}")
        
        df = pd.read_csv(filepath)
        print(f"✅ Loaded {len(df)} cases from validation dataset")
        return df
    
    def calculate_composite_for_cases(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate composite scores for all cases in the dataset."""
        print("\n📊 Calculating composite scores for all cases...")
        print("   (Using existing TS% and Production ratios from validation data)")
        
        # The validation data already has both ts_resilience_ratio and production_ratio
        # Composite is simply: (TS% Ratio + Production Ratio) / 2
        df = df.copy()
        
        # Calculate composite resilience
        # Composite is simply: (TS% Ratio + Production Ratio) / 2
        df['composite_resilience'] = (df['ts_resilience_ratio'] + df['production_ratio']) / 2
        
        print(f"✅ Calculated composite scores for {len(df)} cases")
        return df
    
    def categorize_composite(self, composite_score: float) -> str:
        """Categorize composite resilience score."""
        if pd.isna(composite_score):
            return 'Unknown'
        elif composite_score < 0.85:
            return 'Severely Fragile'
        elif composite_score < 0.95:
            return 'Fragile'
        elif composite_score <= 1.05:
            return 'Neutral'
        elif composite_score <= 1.15:
            return 'Resilient'
        else:
            return 'Highly Resilient'
    
    def analyze_composite_fixes(self, df: pd.DataFrame) -> Dict:
        """Analyze whether composite metric fixes Type 1 failures."""
        # Filter to cases with valid composite scores
        valid_df = df[df['composite_resilience'].notna()].copy()
        
        # Add composite categories
        valid_df['composite_category'] = valid_df['composite_resilience'].apply(self.categorize_composite)
        
        # Identify Type 1 failures (TS% says fragile, Production says resilient)
        type1_failures = valid_df[valid_df['type1_failure'] == True].copy()
        
        # Check if composite correctly identifies these as resilient
        # Composite should be >1.0 (resilient) for Type 1 failures
        type1_fixed = type1_failures[type1_failures['composite_resilience'] > 1.0]
        type1_still_fragile = type1_failures[type1_failures['composite_resilience'] <= 1.0]
        
        # Also check if composite creates new false positives
        # Cases where TS% and Production agree, but composite disagrees
        non_type1 = valid_df[valid_df['type1_failure'] == False].copy()
        # Cases where TS% says fragile and Production says fragile, but composite says resilient
        false_positives = non_type1[
            (non_type1['ts_resilience_ratio'] < 0.95) & 
            (non_type1['production_ratio'] < 0.95) &
            (non_type1['composite_resilience'] > 1.0)
        ]
        
        # Cases where TS% says resilient and Production says resilient, but composite says fragile
        false_negatives = non_type1[
            (non_type1['ts_resilience_ratio'] > 1.05) & 
            (non_type1['production_ratio'] > 1.05) &
            (non_type1['composite_resilience'] < 1.0)
        ]
        
        return {
            'total_cases': len(valid_df),
            'type1_failures_total': len(type1_failures),
            'type1_fixed': len(type1_fixed),
            'type1_fix_rate': len(type1_fixed) / len(type1_failures) * 100 if len(type1_failures) > 0 else 0,
            'type1_still_fragile': len(type1_still_fragile),
            'false_positives': len(false_positives),
            'false_negatives': len(false_negatives),
            'type1_fixed_df': type1_fixed,
            'type1_still_fragile_df': type1_still_fragile,
            'false_positives_df': false_positives,
            'false_negatives_df': false_negatives,
        }
    
    def compare_classifications(self, df: pd.DataFrame) -> Dict:
        """Compare TS% vs Composite classifications."""
        valid_df = df[df['composite_resilience'].notna()].copy()
        
        # Add categories
        valid_df['ts_category'] = valid_df['ts_resilience_ratio'].apply(lambda x: 
            'Fragile' if x < 0.95 else ('Resilient' if x > 1.05 else 'Neutral'))
        valid_df['composite_category'] = valid_df['composite_resilience'].apply(lambda x:
            'Fragile' if x < 0.95 else ('Resilient' if x > 1.05 else 'Neutral'))
        
        # Agreement analysis
        agreement = valid_df[valid_df['ts_category'] == valid_df['composite_category']]
        disagreement = valid_df[valid_df['ts_category'] != valid_df['composite_category']]
        
        # Correlation
        correlation = valid_df['ts_resilience_ratio'].corr(valid_df['composite_resilience'])
        
        return {
            'total_cases': len(valid_df),
            'agreement_count': len(agreement),
            'agreement_percentage': len(agreement) / len(valid_df) * 100,
            'disagreement_count': len(disagreement),
            'disagreement_percentage': len(disagreement) / len(valid_df) * 100,
            'correlation': correlation,
            'disagreement_df': disagreement,
        }
    
    def generate_report(self, df: pd.DataFrame, fixes: Dict, comparison: Dict, 
                       output_path: str = "data/composite_validation_report.md"):
        """Generate comprehensive comparison report."""
        Path("data").mkdir(exist_ok=True)
        
        report = []
        report.append("# Composite Metric Validation Report")
        report.append("")
        report.append(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total Cases**: {len(df)}")
        report.append("")
        
        report.append("## Executive Summary")
        report.append("")
        report.append(f"- **Type 1 Failures Identified**: {fixes['type1_failures_total']} cases")
        report.append(f"- **Type 1 Failures Fixed by Composite**: {fixes['type1_fixed']} cases ({fixes['type1_fix_rate']:.1f}%)")
        report.append(f"- **Type 1 Failures Still Fragile**: {fixes['type1_still_fragile']} cases")
        report.append(f"- **False Positives Created**: {fixes['false_positives']} cases")
        report.append(f"- **False Negatives Created**: {fixes['false_negatives']} cases")
        report.append(f"- **TS% vs Composite Agreement**: {comparison['agreement_percentage']:.1f}%")
        report.append(f"- **TS% vs Composite Correlation**: {comparison['correlation']:.3f}")
        report.append("")
        
        # Assessment
        report.append("## Assessment")
        report.append("")
        if fixes['type1_fix_rate'] >= 80 and fixes['false_positives'] < 5:
            report.append("**✅ COMPOSITE VALIDATES**: Composite metric successfully fixes most Type 1 failures with minimal false positives.")
            report.append("")
            report.append("**Recommendation**: Proceed with composite metric. It addresses the identified problem effectively.")
        elif fixes['type1_fix_rate'] >= 50:
            report.append("**⚠️ PARTIAL SUCCESS**: Composite metric fixes some Type 1 failures but not all.")
            report.append("")
            report.append("**Recommendation**: Consider refining the composite formula or accepting partial improvement.")
        else:
            report.append("**❌ COMPOSITE FAILS**: Composite metric does not effectively fix Type 1 failures.")
            report.append("")
            report.append("**Recommendation**: Archive composite approach. The problem may not be solvable with this method.")
        report.append("")
        
        # Type 1 fixes analysis
        report.append("## Type 1 Failure Fixes")
        report.append("")
        report.append(f"**Total Type 1 Failures**: {fixes['type1_failures_total']}")
        report.append(f"**Fixed by Composite**: {fixes['type1_fixed']} ({fixes['type1_fix_rate']:.1f}%)")
        report.append(f"**Still Fragile**: {fixes['type1_still_fragile']}")
        report.append("")
        
        if not fixes['type1_fixed_df'].empty:
            report.append("**Cases Fixed by Composite (Top 10):**")
            report.append("")
            report.append("| Player | Season | TS% Ratio | Production Ratio | Composite | Fixed? |")
            report.append("|--------|--------|-----------|------------------|-----------|--------|")
            top_fixed = fixes['type1_fixed_df'].nlargest(10, 'composite_resilience')
            for _, row in top_fixed.iterrows():
                report.append(f"| {row['player_name']} | {row['season']} | {row['ts_resilience_ratio']:.3f} | {row['production_ratio']:.3f} | {row['composite_resilience']:.3f} | ✅ |")
            report.append("")
        
        if not fixes['type1_still_fragile_df'].empty:
            report.append("**Cases Still Fragile (Top 10):**")
            report.append("")
            report.append("| Player | Season | TS% Ratio | Production Ratio | Composite | Fixed? |")
            report.append("|--------|--------|-----------|------------------|-----------|--------|")
            top_still_fragile = fixes['type1_still_fragile_df'].nsmallest(10, 'composite_resilience')
            for _, row in top_still_fragile.iterrows():
                report.append(f"| {row['player_name']} | {row['season']} | {row['ts_resilience_ratio']:.3f} | {row['production_ratio']:.3f} | {row['composite_resilience']:.3f} | ❌ |")
            report.append("")
        
        # False positives/negatives
        if fixes['false_positives'] > 0:
            report.append("## False Positives")
            report.append("")
            report.append(f"**Count**: {fixes['false_positives']} cases where TS% and Production both say fragile, but Composite says resilient")
            report.append("")
            if not fixes['false_positives_df'].empty:
                report.append("| Player | Season | TS% Ratio | Production Ratio | Composite |")
                report.append("|--------|--------|-----------|------------------|-----------|")
                for _, row in fixes['false_positives_df'].head(10).iterrows():
                    report.append(f"| {row['player_name']} | {row['season']} | {row['ts_resilience_ratio']:.3f} | {row['production_ratio']:.3f} | {row['composite_resilience']:.3f} |")
                report.append("")
        
        if fixes['false_negatives'] > 0:
            report.append("## False Negatives")
            report.append("")
            report.append(f"**Count**: {fixes['false_negatives']} cases where TS% and Production both say resilient, but Composite says fragile")
            report.append("")
        
        # Classification comparison
        report.append("## Classification Comparison")
        report.append("")
        report.append(f"**Agreement**: {comparison['agreement_count']} cases ({comparison['agreement_percentage']:.1f}%)")
        report.append(f"**Disagreement**: {comparison['disagreement_count']} cases ({comparison['disagreement_percentage']:.1f}%)")
        report.append(f"**Correlation**: {comparison['correlation']:.3f}")
        report.append("")
        
        if not comparison['disagreement_df'].empty:
            report.append("**Top Disagreements (TS% vs Composite):**")
            report.append("")
            report.append("| Player | Season | TS% Category | Composite Category | TS% Ratio | Composite |")
            report.append("|--------|--------|--------------|-------------------|-----------|-----------|")
            top_disagreements = comparison['disagreement_df'].head(15)
            for _, row in top_disagreements.iterrows():
                report.append(f"| {row['player_name']} | {row['season']} | {row['ts_category']} | {row['composite_category']} | {row['ts_resilience_ratio']:.3f} | {row['composite_resilience']:.3f} |")
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
    print("COMPOSITE METRIC VALIDATION")
    print("=" * 70)
    print()
    print("Testing whether composite metric fixes Type 1 failures...")
    print()
    
    validator = CompositeValidator()
    
    # Load validation data
    try:
        df = validator.load_validation_data()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Run validate_problem_exists.py first to generate validation data.")
        return
    
    # Calculate composite scores
    df_with_composite = validator.calculate_composite_for_cases(df)
    
    # Save results
    output_file = "data/composite_validation_data.csv"
    df_with_composite.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to {output_file}")
    
    # Analyze fixes
    print("\n📊 Analyzing composite fixes...")
    fixes = validator.analyze_composite_fixes(df_with_composite)
    comparison = validator.compare_classifications(df_with_composite)
    
    # Generate report
    report_path = validator.generate_report(df_with_composite, fixes, comparison)
    
    # Print summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Type 1 Failures: {fixes['type1_failures_total']}")
    print(f"Fixed by Composite: {fixes['type1_fixed']} ({fixes['type1_fix_rate']:.1f}%)")
    print(f"Still Fragile: {fixes['type1_still_fragile']}")
    print(f"False Positives: {fixes['false_positives']}")
    print(f"TS% vs Composite Agreement: {comparison['agreement_percentage']:.1f}%")
    print()
    
    if fixes['type1_fix_rate'] >= 80:
        print("✅ COMPOSITE VALIDATES: Successfully fixes most Type 1 failures")
    elif fixes['type1_fix_rate'] >= 50:
        print("⚠️ PARTIAL SUCCESS: Fixes some but not all Type 1 failures")
    else:
        print("❌ COMPOSITE FAILS: Does not effectively fix Type 1 failures")
    print()
    print(f"📄 Full report: {report_path}")


if __name__ == "__main__":
    main()

