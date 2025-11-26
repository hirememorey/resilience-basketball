#!/usr/bin/env python3
"""
Validate Measurement Assumptions: What Are We Actually Measuring?

This script questions our fundamental assumptions:
1. Does TS% delta actually measure playoff overperformance/underperformance?
2. Does production delta actually measure playoff overperformance/underperformance?
3. What is a "good" baseline to compare against?
4. How do we validate these measurements without using playoff outcomes?

Key Insight: We can't use playoff outcomes to validate because outcomes don't reveal
who over/underperformed. We need to validate the measurements themselves.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from src.nba_data.api.nba_stats_client import NBAStatsClient
from calculate_resilience_external import ExternalResilienceCalculator


class MeasurementValidator:
    """Validates what we're actually measuring with TS% and Production ratios."""
    
    def __init__(self):
        self.calculator = ExternalResilienceCalculator()
        self.client = NBAStatsClient()
    
    def get_player_season_data(self, player_name: str, season: str) -> Optional[Dict]:
        """Get comprehensive data for a player in a season."""
        # Get advanced stats (TS%, usage, etc.)
        rs_advanced = self.calculator.get_season_data(season, "Regular Season")
        po_advanced = self.calculator.get_season_data(season, "Playoffs")
        
        if rs_advanced.empty or po_advanced.empty:
            return None
        
        rs_player = rs_advanced[rs_advanced['PLAYER_NAME'] == player_name]
        po_player = po_advanced[po_advanced['PLAYER_NAME'] == player_name]
        
        if rs_player.empty or po_player.empty:
            return None
        
        rs_adv = rs_player.iloc[0]
        po_adv = po_player.iloc[0]
        
        # Get base stats (PTS, AST, REB)
        try:
            rs_base = self.client.get_league_player_base_stats(season=season, season_type="Regular Season")
            po_base = self.client.get_league_player_playoff_base_stats(season=season)
            
            if not rs_base.get('resultSets') or not po_base.get('resultSets'):
                return None
            
            rs_base_df = pd.DataFrame(rs_base['resultSets'][0]['rowSet'], 
                                     columns=rs_base['resultSets'][0]['headers'])
            po_base_df = pd.DataFrame(po_base['resultSets'][0]['rowSet'],
                                     columns=po_base['resultSets'][0]['headers'])
            
            rs_base_player = rs_base_df[rs_base_df['PLAYER_NAME'] == player_name]
            po_base_player = po_base_df[po_base_df['PLAYER_NAME'] == player_name]
            
            if rs_base_player.empty or po_base_player.empty:
                return None
            
            rs_b = rs_base_player.iloc[0]
            po_b = po_base_player.iloc[0]
            
            # Calculate production
            rs_production = (rs_b.get('PTS', 0) or 0) + 1.5 * (rs_b.get('AST', 0) or 0) + 0.5 * (rs_b.get('REB', 0) or 0)
            po_production = (po_b.get('PTS', 0) or 0) + 1.5 * (po_b.get('AST', 0) or 0) + 0.5 * (po_b.get('REB', 0) or 0)
            
            return {
                'player_name': player_name,
                'season': season,
                
                # Regular season
                'rs_ts_pct': rs_adv['TS_PCT'],
                'rs_usage_pct': rs_adv['USG_PCT'],
                'rs_minutes': rs_adv['MIN'],
                'rs_production': rs_production,
                'rs_games': rs_adv.get('GP', 0),
                
                # Playoffs
                'po_ts_pct': po_adv['TS_PCT'],
                'po_usage_pct': po_adv.get('USG_PCT', 0),
                'po_minutes': po_adv['MIN'],
                'po_production': po_production,
                'po_games': po_adv.get('GP', 0),
                
                # Ratios
                'ts_ratio': po_adv['TS_PCT'] / rs_adv['TS_PCT'] if rs_adv['TS_PCT'] > 0 else None,
                'production_ratio': po_production / rs_production if rs_production > 0 else None,
                'usage_ratio': (po_adv.get('USG_PCT', 0) / rs_adv['USG_PCT']) if rs_adv['USG_PCT'] > 0 else None,
            }
        except Exception as e:
            return None
    
    def analyze_baseline_questions(self, df: pd.DataFrame) -> Dict:
        """Analyze fundamental questions about our baseline."""
        results = {}
        
        # Question 1: Is regular season average a good baseline?
        # Hypothesis: Regular season includes easy games, playoffs don't
        # Test: Compare regular season performance vs "hard games" (if we can identify them)
        
        # For now, we can look at variance in regular season
        # High variance might indicate inconsistent baseline
        
        # Question 2: Does usage change affect our ratios?
        # If usage increases in playoffs, TS% might decline but production might increase
        # This could explain some of our Type 1 failures
        
        df_with_usage = df[df['usage_ratio'].notna()].copy()
        
        # Correlation: Usage change vs TS% change
        usage_ts_corr = df_with_usage['usage_ratio'].corr(df_with_usage['ts_ratio'])
        
        # Correlation: Usage change vs Production change
        usage_prod_corr = df_with_usage['usage_ratio'].corr(df_with_usage['production_ratio'])
        
        results['usage_analysis'] = {
            'usage_ts_correlation': usage_ts_corr,
            'usage_prod_correlation': usage_prod_corr,
            'cases_with_usage_data': len(df_with_usage),
        }
        
        # Question 3: Are we measuring "overperformance" or just "different context"?
        # If TS% declines but production increases, is that overperformance or just role change?
        
        # Question 4: What does "baseline" actually mean?
        # Regular season average? Recent form? Career average? Opponent-adjusted?
        
        return results
    
    def analyze_what_ratios_measure(self, df: pd.DataFrame) -> Dict:
        """Analyze what TS% and Production ratios actually measure."""
        results = {}
        
        # TS% Ratio Analysis
        # What does TS% ratio < 1.0 actually mean?
        # - Player is less efficient in playoffs
        # - But is this "underperformance" or "harder context"?
        
        ts_fragile = df[df['ts_ratio'] < 0.95]
        ts_resilient = df[df['ts_ratio'] > 1.05]
        
        results['ts_analysis'] = {
            'fragile_count': len(ts_fragile),
            'fragile_mean_usage_change': ts_fragile['usage_ratio'].mean() if 'usage_ratio' in ts_fragile.columns else None,
            'resilient_count': len(ts_resilient),
            'resilient_mean_usage_change': ts_resilient['usage_ratio'].mean() if 'usage_ratio' in ts_resilient.columns else None,
        }
        
        # Production Ratio Analysis
        # What does Production ratio > 1.0 actually mean?
        # - Player produces more in playoffs
        # - But is this "overperformance" or "more opportunity"?
        
        prod_fragile = df[df['production_ratio'] < 0.95]
        prod_resilient = df[df['production_ratio'] > 1.05]
        
        results['production_analysis'] = {
            'fragile_count': len(prod_fragile),
            'fragile_mean_usage_change': prod_fragile['usage_ratio'].mean() if 'usage_ratio' in prod_fragile.columns else None,
            'resilient_count': len(prod_resilient),
            'resilient_mean_usage_change': prod_resilient['usage_ratio'].mean() if 'usage_ratio' in prod_resilient.columns else None,
        }
        
        # Key Question: Are we measuring performance or opportunity?
        # If usage increases, production might increase even if performance doesn't
        
        return results
    
    def identify_baseline_issues(self, df: pd.DataFrame) -> Dict:
        """Identify potential issues with using regular season as baseline."""
        issues = []
        
        # Issue 1: Regular season includes easy games
        # Playoffs don't have easy games
        # This might make TS% decline inevitable for some players
        
        # Issue 2: Regular season includes garbage time
        # Playoffs have less garbage time
        # This might affect production
        
        # Issue 3: Regular season has schedule variance
        # Some teams play easier schedules
        # Playoffs are more uniform (all good teams)
        
        # Issue 4: Role changes
        # Players might have different roles in playoffs
        # Usage changes might explain ratio changes
        
        # For now, we can test: Do usage changes explain ratio changes?
        df_with_usage = df[df['usage_ratio'].notna()].copy()
        
        if len(df_with_usage) > 0:
            # If usage increases, does TS% decline? (expected: yes, harder shots)
            usage_increase = df_with_usage[df_with_usage['usage_ratio'] > 1.1]
            if len(usage_increase) > 0:
                mean_ts_change = (usage_increase['ts_ratio'] - 1.0).mean()
                issues.append({
                    'issue': 'Usage increase effect on TS%',
                    'description': f'When usage increases >10%, mean TS% change: {mean_ts_change:.3f}',
                    'cases': len(usage_increase),
                })
            
            # If usage increases, does production increase? (expected: yes, more opportunity)
            if len(usage_increase) > 0:
                mean_prod_change = (usage_increase['production_ratio'] - 1.0).mean()
                issues.append({
                    'issue': 'Usage increase effect on Production',
                    'description': f'When usage increases >10%, mean Production change: {mean_prod_change:.3f}',
                    'cases': len(usage_increase),
                })
        
        return {
            'issues': issues,
            'total_cases_analyzed': len(df_with_usage),
        }
    
    def generate_validation_report(self, df: pd.DataFrame, baseline_analysis: Dict, 
                                   ratio_analysis: Dict, baseline_issues: Dict,
                                   output_path: str = "data/measurement_validation_report.md"):
        """Generate comprehensive validation report."""
        Path("data").mkdir(exist_ok=True)
        
        report = []
        report.append("# Measurement Validation Report: What Are We Actually Measuring?")
        report.append("")
        report.append(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total Cases**: {len(df)}")
        report.append("")
        
        report.append("## Fundamental Questions")
        report.append("")
        report.append("### Question 1: Does TS% delta measure overperformance/underperformance?")
        report.append("")
        report.append("**What we're measuring**: `Playoff TS% ÷ Regular Season TS%`")
        report.append("")
        report.append("**What we're assuming**:")
        report.append("- Regular season TS% is a valid baseline")
        report.append("- TS% decline = underperformance")
        report.append("- TS% increase = overperformance")
        report.append("")
        report.append("**Potential issues**:")
        report.append("- Regular season includes easy games, playoffs don't")
        report.append("- Regular season includes garbage time, playoffs don't")
        report.append("- Usage changes might explain TS% changes (harder shots at higher usage)")
        report.append("- Opponent quality is different (playoffs = better defenses)")
        report.append("")
        
        report.append("### Question 2: Does Production delta measure overperformance/underperformance?")
        report.append("")
        report.append("**What we're measuring**: `Playoff Production ÷ Regular Season Production`")
        report.append("")
        report.append("**What we're assuming**:")
        report.append("- Regular season production is a valid baseline")
        report.append("- Production increase = overperformance")
        report.append("- Production decline = underperformance")
        report.append("")
        report.append("**Potential issues**:")
        report.append("- Usage changes might explain production changes (more opportunity)")
        report.append("- Role changes might explain production changes")
        report.append("- Minutes changes might explain production changes")
        report.append("- We might be measuring opportunity, not performance")
        report.append("")
        
        report.append("### Question 3: What is a 'good' baseline?")
        report.append("")
        report.append("**Current baseline**: Regular season average")
        report.append("")
        report.append("**Alternatives to consider**:")
        report.append("- Recent form (last 20 games of regular season)")
        report.append("- Opponent-adjusted regular season (only games vs playoff teams)")
        report.append("- Career playoff average (for players with playoff history)")
        report.append("- Context-adjusted (accounting for usage, role, minutes)")
        report.append("")
        
        # Usage analysis
        if 'usage_analysis' in baseline_analysis:
            usage_analysis = baseline_analysis['usage_analysis']
            report.append("## Usage Change Analysis")
            report.append("")
            report.append(f"**Usage vs TS% Correlation**: {usage_analysis['usage_ts_correlation']:.3f}")
            report.append(f"**Usage vs Production Correlation**: {usage_analysis['usage_prod_correlation']:.3f}")
            report.append("")
            report.append("**Interpretation**:")
            if abs(usage_analysis['usage_ts_correlation']) > 0.3:
                report.append("- Usage changes significantly affect TS% ratios")
                report.append("- This suggests TS% changes might be due to role/opportunity, not just performance")
            if abs(usage_analysis['usage_prod_correlation']) > 0.3:
                report.append("- Usage changes significantly affect Production ratios")
                report.append("- This suggests Production changes might be due to opportunity, not just performance")
            report.append("")
        
        # Baseline issues
        if baseline_issues.get('issues'):
            report.append("## Baseline Issues Identified")
            report.append("")
            for issue in baseline_issues['issues']:
                report.append(f"### {issue['issue']}")
                report.append(f"- **Description**: {issue['description']}")
                report.append(f"- **Cases**: {issue['cases']}")
                report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        report.append("### Option 1: Validate Current Approach")
        report.append("- Test if TS% and Production ratios correlate with meaningful outcomes")
        report.append("- Test if usage changes explain ratio changes")
        report.append("- If usage explains most variance, we might be measuring opportunity, not performance")
        report.append("")
        
        report.append("### Option 2: Improve Baseline")
        report.append("- Use recent form instead of full regular season")
        report.append("- Use opponent-adjusted baseline (only games vs playoff teams)")
        report.append("- Account for usage/role changes in the ratio")
        report.append("")
        
        report.append("### Option 3: Redefine What We're Measuring")
        report.append("- Instead of 'overperformance', measure 'maintenance despite context change'")
        report.append("- Instead of 'underperformance', measure 'decline in favorable context'")
        report.append("- Accept that we're measuring context adaptation, not pure performance")
        report.append("")
        
        # Write report
        report_text = "\n".join(report)
        with open(output_path, 'w') as f:
            f.write(report_text)
        
        print(f"\n📄 Report saved to {output_path}")
        return output_path


def main():
    """Main validation function."""
    print("=" * 70)
    print("MEASUREMENT VALIDATION: What Are We Actually Measuring?")
    print("=" * 70)
    print()
    print("This script questions our fundamental assumptions:")
    print("1. Does TS% delta measure overperformance/underperformance?")
    print("2. Does production delta measure overperformance/underperformance?")
    print("3. What is a 'good' baseline to compare against?")
    print()
    
    validator = MeasurementValidator()
    
    # Load validation data (we already have this)
    validation_file = "data/problem_validation_data.csv"
    if not Path(validation_file).exists():
        print(f"❌ Validation data not found: {validation_file}")
        print("   Run validate_problem_exists.py first")
        return
    
    df = pd.read_csv(validation_file)
    print(f"✅ Loaded {len(df)} cases from validation data")
    
    # We need to add usage ratio data
    print("\n📊 Collecting usage data for analysis...")
    print("   (This may take a few minutes)")
    
    enhanced_data = []
    for idx, row in df.iterrows():
        if (idx + 1) % 50 == 0:
            print(f"   Progress: {idx + 1}/{len(df)} ({100*(idx+1)/len(df):.1f}%)")
        
        player_data = validator.get_player_season_data(row['player_name'], row['season'])
        if player_data:
            enhanced_data.append(player_data)
    
    if not enhanced_data:
        print("❌ Could not collect enhanced data")
        return
    
    enhanced_df = pd.DataFrame(enhanced_data)
    print(f"✅ Collected data for {len(enhanced_df)} cases")
    
    # Save enhanced data
    enhanced_file = "data/measurement_validation_data.csv"
    enhanced_df.to_csv(enhanced_file, index=False)
    print(f"💾 Enhanced data saved to {enhanced_file}")
    
    # Analyze
    print("\n📊 Analyzing measurement assumptions...")
    baseline_analysis = validator.analyze_baseline_questions(enhanced_df)
    ratio_analysis = validator.analyze_what_ratios_measure(enhanced_df)
    baseline_issues = validator.identify_baseline_issues(enhanced_df)
    
    # Generate report
    report_path = validator.generate_validation_report(
        enhanced_df, baseline_analysis, ratio_analysis, baseline_issues
    )
    
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)
    print(f"📄 Full report: {report_path}")
    print()
    print("Key questions to consider:")
    print("1. Are we measuring performance or opportunity?")
    print("2. Is regular season average a good baseline?")
    print("3. Do usage/role changes explain our ratios?")
    print()


if __name__ == "__main__":
    main()

