#!/usr/bin/env python3
"""
Problem Validation Script: Does TS% Systematically Miss Production Elevation?

This script validates whether the problem actually exists:
1. Calculates TS% ratio and Production ratio for all qualified players across multiple seasons
2. Identifies cases where TS% says "fragile" but Production says "resilient" (Type 1 failures)
3. Tests if certain players consistently show this pattern (the "Butler test")
4. Quantifies the problem scope to determine if it's worth solving

Hypothesis: Certain players (like Jimmy Butler) consistently elevate production 
despite TS% decline, and TS% ratio alone fails to identify them.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from collections import defaultdict

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from src.nba_data.api.nba_stats_client import NBAStatsClient
from calculate_resilience_external import ExternalResilienceCalculator


class ProblemValidator(ExternalResilienceCalculator):
    """Validates whether TS% systematically misses production elevation."""
    
    def __init__(self):
        super().__init__()
        self.client = NBAStatsClient()
    
    def calculate_production_ratio(self, player_name: str, season: str) -> Optional[float]:
        """Calculate absolute production ratio for a player."""
        try:
            # Get base stats for regular season
            rs_base = self.client.get_league_player_base_stats(season=season, season_type="Regular Season")
            if not rs_base.get('resultSets') or not rs_base['resultSets'][0].get('rowSet'):
                return None
            
            rs_headers = rs_base['resultSets'][0]['headers']
            rs_rows = rs_base['resultSets'][0]['rowSet']
            rs_df = pd.DataFrame(rs_rows, columns=rs_headers)
            rs_player = rs_df[rs_df['PLAYER_NAME'] == player_name]
            
            # Get base stats for playoffs
            po_base = self.client.get_league_player_playoff_base_stats(season=season)
            if not po_base.get('resultSets') or not po_base['resultSets'][0].get('rowSet'):
                return None
            
            po_headers = po_base['resultSets'][0]['headers']
            po_rows = po_base['resultSets'][0]['rowSet']
            po_df = pd.DataFrame(po_rows, columns=po_headers)
            po_player = po_df[po_df['PLAYER_NAME'] == player_name]
            
            if rs_player.empty or po_player.empty:
                return None
            
            rs_stats = rs_player.iloc[0]
            po_stats = po_player.iloc[0]
            
            # Calculate weighted production: PTS + 1.5×AST + 0.5×REB (per game)
            rs_pts = rs_stats.get('PTS', 0) or 0
            rs_ast = rs_stats.get('AST', 0) or 0
            rs_reb = rs_stats.get('REB', 0) or 0
            po_pts = po_stats.get('PTS', 0) or 0
            po_ast = po_stats.get('AST', 0) or 0
            po_reb = po_stats.get('REB', 0) or 0
            
            rs_production = rs_pts + 1.5 * rs_ast + 0.5 * rs_reb
            po_production = po_pts + 1.5 * po_ast + 0.5 * po_reb
            
            if rs_production > 0:
                return po_production / rs_production
            return None
            
        except Exception as e:
            return None
    
    def calculate_player_metrics(self, player_name: str, season: str) -> Optional[Dict]:
        """Calculate both TS% ratio and Production ratio for a player."""
        # Get TS% resilience
        ts_resilience = self.calculate_player_resilience(player_name, season)
        if not ts_resilience:
            return None
        
        # Get production ratio
        production_ratio = self.calculate_production_ratio(player_name, season)
        if production_ratio is None:
            return None
        
        ts_ratio = ts_resilience['ts_resilience_ratio']
        
        # Calculate disagreement score
        disagreement = abs(ts_ratio - production_ratio)
        
        # Categorize TS% resilience
        if ts_ratio < 0.85:
            ts_category = 'Severely Fragile'
        elif ts_ratio < 0.95:
            ts_category = 'Fragile'
        elif ts_ratio <= 1.05:
            ts_category = 'Neutral'
        elif ts_ratio <= 1.15:
            ts_category = 'Resilient'
        else:
            ts_category = 'Highly Resilient'
        
        # Categorize production resilience
        if production_ratio < 0.85:
            prod_category = 'Severely Fragile'
        elif production_ratio < 0.95:
            prod_category = 'Fragile'
        elif production_ratio <= 1.05:
            prod_category = 'Neutral'
        elif production_ratio <= 1.15:
            prod_category = 'Resilient'
        else:
            prod_category = 'Highly Resilient'
        
        # Identify failure types
        type1_failure = (ts_ratio < 0.95 and production_ratio > 1.05)  # TS% says fragile, Production says resilient
        type2_failure = (ts_ratio > 1.05 and production_ratio < 0.95)  # TS% says resilient, Production says fragile
        
        result = ts_resilience.copy()
        result.update({
            'production_ratio': production_ratio,
            'disagreement_score': disagreement,
            'ts_category': ts_category,
            'production_category': prod_category,
            'type1_failure': type1_failure,
            'type2_failure': type2_failure,
        })
        
        return result
    
    def analyze_season(self, season: str, min_usage: float = 0.20) -> pd.DataFrame:
        """Analyze all qualified players in a season."""
        print(f"\n📊 Analyzing {season}...")
        
        # Get both datasets
        rs_data = self.get_season_data(season, "Regular Season")
        po_data = self.get_season_data(season, "Playoffs")
        
        if rs_data.empty or po_data.empty:
            print(f"❌ Missing data for {season}")
            return pd.DataFrame()
        
        # Find qualified players
        rs_players = set(rs_data['PLAYER_NAME'])
        po_players = set(po_data['PLAYER_NAME'])
        qualified_players = rs_players.intersection(po_players)
        
        # Calculate metrics for each player
        results = []
        for player_name in qualified_players:
            rs_player = rs_data[rs_data['PLAYER_NAME'] == player_name]
            po_player = po_data[po_data['PLAYER_NAME'] == player_name]
            
            if rs_player.empty or po_player.empty:
                continue
            
            rs_stats = rs_player.iloc[0]
            po_stats = po_player.iloc[0]
            
            # Apply filters
            if (rs_stats['USG_PCT'] >= min_usage and po_stats['MIN'] >= 15):
                metrics = self.calculate_player_metrics(player_name, season)
                if metrics:
                    results.append(metrics)
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        print(f"✅ Analyzed {len(df)} players for {season}")
        return df
    
    def analyze_multiple_seasons(self, seasons: List[str], min_usage: float = 0.20) -> pd.DataFrame:
        """Analyze multiple seasons and combine results."""
        all_results = []
        
        for season in seasons:
            season_df = self.analyze_season(season, min_usage)
            if not season_df.empty:
                all_results.append(season_df)
        
        if not all_results:
            return pd.DataFrame()
        
        combined_df = pd.concat(all_results, ignore_index=True)
        return combined_df
    
    def identify_failures(self, df: pd.DataFrame) -> Dict:
        """Identify and categorize failure cases."""
        total_cases = len(df)
        
        type1_failures = df[df['type1_failure'] == True]
        type2_failures = df[df['type2_failure'] == True]
        
        # High-impact failures (high usage players)
        high_usage_df = df[df['rs_usage_pct'] >= 0.25]
        high_usage_type1 = high_usage_df[high_usage_df['type1_failure'] == True]
        
        return {
            'total_cases': total_cases,
            'type1_count': len(type1_failures),
            'type1_percentage': len(type1_failures) / total_cases * 100 if total_cases > 0 else 0,
            'type2_count': len(type2_failures),
            'type2_percentage': len(type2_failures) / total_cases * 100 if total_cases > 0 else 0,
            'high_usage_total': len(high_usage_df),
            'high_usage_type1_count': len(high_usage_type1),
            'high_usage_type1_percentage': len(high_usage_type1) / len(high_usage_df) * 100 if len(high_usage_df) > 0 else 0,
            'type1_failures_df': type1_failures,
            'type2_failures_df': type2_failures,
        }
    
    def analyze_consistency(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze which players consistently show Type 1 failures."""
        # Group by player
        player_groups = df.groupby('player_name')
        
        consistency_results = []
        for player_name, group in player_groups:
            seasons = len(group)
            if seasons < 2:  # Need at least 2 seasons
                continue
            
            type1_count = group['type1_failure'].sum()
            consistency_score = type1_count / seasons
            
            avg_ts_ratio = group['ts_resilience_ratio'].mean()
            avg_prod_ratio = group['production_ratio'].mean()
            avg_disagreement = group['disagreement_score'].mean()
            
            consistency_results.append({
                'player_name': player_name,
                'seasons': seasons,
                'type1_failures': type1_count,
                'consistency_score': consistency_score,
                'avg_ts_ratio': avg_ts_ratio,
                'avg_prod_ratio': avg_prod_ratio,
                'avg_disagreement': avg_disagreement,
                'is_consistent_overperformer': consistency_score >= 0.5,  # ≥50% of seasons show Type 1 failure
            })
        
        consistency_df = pd.DataFrame(consistency_results)
        return consistency_df.sort_values('consistency_score', ascending=False)
    
    def validate_known_cases(self, df: pd.DataFrame) -> Dict:
        """Validate against known test cases."""
        results = {}
        
        # Jimmy Butler - should show Type 1 failure in multiple seasons
        butler_cases = df[df['player_name'].str.contains('Butler', case=False, na=False)]
        if not butler_cases.empty:
            butler_type1 = butler_cases[butler_cases['type1_failure'] == True]
            results['butler'] = {
                'total_seasons': len(butler_cases),
                'type1_failures': len(butler_type1),
                'seasons': butler_cases[['season', 'ts_resilience_ratio', 'production_ratio', 'type1_failure']].to_dict('records'),
            }
        
        # Jamal Murray - should show agreement (not failure)
        murray_cases = df[df['player_name'].str.contains('Murray', case=False, na=False)]
        if not murray_cases.empty:
            murray_type1 = murray_cases[murray_cases['type1_failure'] == True]
            results['murray'] = {
                'total_seasons': len(murray_cases),
                'type1_failures': len(murray_type1),
                'seasons': murray_cases[['season', 'ts_resilience_ratio', 'production_ratio', 'type1_failure']].to_dict('records'),
            }
        
        return results
    
    def generate_report(self, df: pd.DataFrame, output_path: str = "data/problem_validation_report.md"):
        """Generate comprehensive validation report."""
        Path("data").mkdir(exist_ok=True)
        
        # Calculate statistics
        failures = self.identify_failures(df)
        consistency_df = self.analyze_consistency(df)
        known_cases = self.validate_known_cases(df)
        
        # Correlation analysis
        correlation = df['ts_resilience_ratio'].corr(df['production_ratio'])
        
        # Consistent overperformers
        consistent_overperformers = consistency_df[consistency_df['is_consistent_overperformer'] == True]
        
        # Generate report
        report = []
        report.append("# Problem Validation Report: Does TS% Systematically Miss Production Elevation?")
        report.append("")
        report.append(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total Cases Analyzed**: {len(df)}")
        report.append("")
        
        report.append("## Executive Summary")
        report.append("")
        report.append(f"- **Type 1 Failures**: {failures['type1_count']} cases ({failures['type1_percentage']:.1f}% of total)")
        report.append(f"- **High-Usage Type 1 Failures**: {failures['high_usage_type1_count']} cases ({failures['high_usage_type1_percentage']:.1f}% of high-usage players)")
        report.append(f"- **Consistent Overperformers**: {len(consistent_overperformers)} players show Type 1 failure in ≥50% of seasons")
        report.append(f"- **TS% vs Production Correlation**: {correlation:.3f}")
        report.append("")
        
        # Problem scope assessment
        report.append("## Problem Scope Assessment")
        report.append("")
        if failures['type1_percentage'] < 5:
            report.append("**Assessment**: Problem is too small (<5% of cases). TS% ratio is sufficient.")
        elif failures['type1_percentage'] < 10:
            report.append("**Assessment**: Problem is marginal (5-10% of cases). May not be worth solving.")
        else:
            report.append(f"**Assessment**: Problem is significant (>{failures['type1_percentage']:.1f}% of cases). Worth solving.")
        report.append("")
        
        if correlation > 0.9:
            report.append("**Correlation Analysis**: TS% and Production are highly correlated (>0.9). They may be measuring the same thing.")
        elif correlation < 0.7:
            report.append("**Correlation Analysis**: TS% and Production show significant disagreement (<0.7). They are measuring different aspects of resilience.")
        else:
            report.append("**Correlation Analysis**: TS% and Production show moderate correlation (0.7-0.9). Some disagreement exists.")
        report.append("")
        
        # Failure analysis
        report.append("## Failure Analysis")
        report.append("")
        report.append(f"### Type 1 Failures (TS% says Fragile, Production says Resilient)")
        report.append(f"- **Count**: {failures['type1_count']} cases")
        report.append(f"- **Percentage**: {failures['type1_percentage']:.1f}% of total")
        report.append(f"- **High-Usage Cases**: {failures['high_usage_type1_count']} ({failures['high_usage_type1_percentage']:.1f}%)")
        report.append("")
        
        if not failures['type1_failures_df'].empty:
            report.append("**Top 10 Type 1 Failures (by disagreement score):**")
            top_failures = failures['type1_failures_df'].nlargest(10, 'disagreement_score')
            report.append("")
            report.append("| Player | Season | TS% Ratio | Production Ratio | Disagreement |")
            report.append("|--------|--------|-----------|-------------------|--------------|")
            for _, row in top_failures.iterrows():
                report.append(f"| {row['player_name']} | {row['season']} | {row['ts_resilience_ratio']:.3f} | {row['production_ratio']:.3f} | {row['disagreement_score']:.3f} |")
            report.append("")
        
        report.append(f"### Type 2 Failures (TS% says Resilient, Production says Fragile)")
        report.append(f"- **Count**: {failures['type2_count']} cases")
        report.append(f"- **Percentage**: {failures['type2_percentage']:.1f}% of total")
        report.append("")
        
        # Consistency analysis
        report.append("## Consistency Analysis: The 'Butler Test'")
        report.append("")
        report.append(f"**Players with 2+ seasons analyzed**: {len(consistency_df)}")
        report.append(f"**Consistent overperformers (≥50% Type 1 failures)**: {len(consistent_overperformers)}")
        report.append("")
        
        if not consistent_overperformers.empty:
            report.append("**Consistent Overperformers:**")
            report.append("")
            report.append("| Player | Seasons | Type 1 Failures | Consistency Score | Avg TS% | Avg Production |")
            report.append("|--------|---------|-----------------|-------------------|---------|----------------|")
            for _, row in consistent_overperformers.head(10).iterrows():
                report.append(f"| {row['player_name']} | {int(row['seasons'])} | {int(row['type1_failures'])} | {row['consistency_score']:.2f} | {row['avg_ts_ratio']:.3f} | {row['avg_prod_ratio']:.3f} |")
            report.append("")
        
        # Known cases validation
        report.append("## Known Cases Validation")
        report.append("")
        if 'butler' in known_cases:
            butler = known_cases['butler']
            report.append(f"### Jimmy Butler")
            report.append(f"- **Seasons analyzed**: {butler['total_seasons']}")
            report.append(f"- **Type 1 failures**: {butler['type1_failures']}")
            report.append(f"- **Expected**: Should show Type 1 failure in multiple seasons")
            report.append(f"- **Result**: {'✅ PASS' if butler['type1_failures'] >= 2 else '❌ FAIL'}")
            report.append("")
            for season_data in butler['seasons']:
                report.append(f"  - {season_data['season']}: TS% {season_data['ts_resilience_ratio']:.3f}, Production {season_data['production_ratio']:.3f}, Type 1: {season_data['type1_failure']}")
            report.append("")
        
        if 'murray' in known_cases:
            murray = known_cases['murray']
            report.append(f"### Jamal Murray")
            report.append(f"- **Seasons analyzed**: {murray['total_seasons']}")
            report.append(f"- **Type 1 failures**: {murray['type1_failures']}")
            report.append(f"- **Expected**: Should show agreement (not Type 1 failure)")
            report.append(f"- **Result**: {'✅ PASS' if murray['type1_failures'] == 0 else '⚠️ PARTIAL'}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        if failures['type1_percentage'] >= 10 and len(consistent_overperformers) >= 3:
            report.append("**✅ PROBLEM VALIDATED**: The problem exists and is significant enough to solve.")
            report.append("")
            report.append("**Next Steps**:")
            report.append("1. Proceed with composite metric validation")
            report.append("2. Test if composite metric fixes Type 1 failures")
            report.append("3. Compare composite accuracy vs TS% baseline")
        elif failures['type1_percentage'] >= 5:
            report.append("**⚠️ MARGINAL PROBLEM**: The problem exists but may not be worth solving.")
            report.append("")
            report.append("**Next Steps**:")
            report.append("1. Consider if 5-10% failure rate justifies complexity")
            report.append("2. Focus on high-usage players if they show higher failure rate")
        else:
            report.append("**❌ PROBLEM NOT VALIDATED**: The problem is too small to justify solving.")
            report.append("")
            report.append("**Next Steps**:")
            report.append("1. Archive composite approach")
            report.append("2. Accept TS% ratio as sufficient")
            report.append("3. Focus on understanding TS% limitations rather than fixing them")
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
    print("PROBLEM VALIDATION: Does TS% Systematically Miss Production Elevation?")
    print("=" * 70)
    print()
    print("This script will:")
    print("1. Calculate TS% ratio and Production ratio for all qualified players")
    print("2. Identify cases where TS% says 'fragile' but Production says 'resilient'")
    print("3. Test if certain players consistently show this pattern")
    print("4. Quantify the problem scope")
    print()
    
    validator = ProblemValidator()
    
    # Seasons to analyze (excluding bubble and play-in)
    seasons = [
        "2015-16", "2016-17", "2017-18", "2018-19",
        "2021-22", "2022-23", "2023-24"
    ]
    
    print(f"📅 Analyzing {len(seasons)} seasons...")
    print("   (Excluding 2019-20 bubble and 2020-21 play-in)")
    print()
    
    # Analyze all seasons
    df = validator.analyze_multiple_seasons(seasons, min_usage=0.20)
    
    if df.empty:
        print("❌ No data collected. Check API connectivity.")
        return
    
    print(f"\n✅ Collected data for {len(df)} player-season combinations")
    
    # Save raw data
    output_file = "data/problem_validation_data.csv"
    df.to_csv(output_file, index=False)
    print(f"💾 Raw data saved to {output_file}")
    
    # Generate report
    report_path = validator.generate_report(df)
    
    # Print summary
    failures = validator.identify_failures(df)
    consistency_df = validator.analyze_consistency(df)
    consistent_overperformers = consistency_df[consistency_df['is_consistent_overperformer'] == True]
    correlation = df['ts_resilience_ratio'].corr(df['production_ratio'])
    
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total cases analyzed: {len(df)}")
    print(f"Type 1 failures: {failures['type1_count']} ({failures['type1_percentage']:.1f}%)")
    print(f"High-usage Type 1 failures: {failures['high_usage_type1_count']} ({failures['high_usage_type1_percentage']:.1f}%)")
    print(f"Consistent overperformers: {len(consistent_overperformers)} players")
    print(f"TS% vs Production correlation: {correlation:.3f}")
    print()
    
    if failures['type1_percentage'] >= 10:
        print("✅ PROBLEM VALIDATED: Significant enough to solve")
    elif failures['type1_percentage'] >= 5:
        print("⚠️ MARGINAL PROBLEM: May not be worth solving")
    else:
        print("❌ PROBLEM NOT VALIDATED: Too small to justify solution")
    print()
    print(f"📄 Full report: {report_path}")


if __name__ == "__main__":
    main()




