#!/usr/bin/env python3
"""
Multi-Season Analysis Script

This script generates classification reports for ALL seasons in the dataset,
allowing you to review how well the 2D classification system performs across
different time periods.

Usage:
    python scripts/analyze_all_seasons.py

Output:
    - Individual season reports in results/season_reports/
    - Summary comparison report in results/multi_season_summary.md
    - CSV files for each season's classifications

Date: December 29, 2025
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src' / 'nba_data' / 'scripts'))

from src.nba_data.phase2_creation_independence.index.classify_2d import (
    batch_classify_2d,
    diagnose_2d_classification,
    calculate_career_leverage,
    has_real_creation_tools
)
from src.nba_data.phase2_creation_independence.index.composite import calculate_cii
from src.nba_data.phase2_creation_independence.index.trajectory import calculate_tii

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'logs' / 'multi_season_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_dataset():
    """Load the full dataset."""
    results_path = project_root / 'results' / 'predictive_dataset_with_friction.csv'
    
    if not results_path.exists():
        logger.error(f"Dataset not found at {results_path}")
        return None
        
    df = pd.read_csv(results_path)
    logger.info(f"Loaded dataset with {len(df)} total player-seasons")
    
    return df


def analyze_season(df_full, season, output_dir):
    """
    Analyze a single season and generate a detailed report.
    
    Returns:
        Dictionary with season statistics
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"ANALYZING SEASON: {season}")
    logger.info(f"{'='*80}")
    
    # Filter to this season
    df_season = df_full[df_full['season'] == season].copy()
    
    if len(df_season) == 0:
        logger.warning(f"No data found for season {season}")
        return None
    
    # Run classification
    logger.info(f"Classifying {len(df_season)} players...")
    results = batch_classify_2d(df_full)
    results_season = results[results['season'] == season].copy()
    
    # Calculate statistics
    stats = {
        'season': season,
        'total_players': len(results_season),
        'archetype_counts': results_season['archetype_2d'].value_counts().to_dict(),
        'archetype_percentages': (results_season['archetype_2d'].value_counts() / len(results_season) * 100).to_dict(),
        'avg_cii': results_season['cii'].mean(),
        'avg_tii': results_season['tii'].mean(),
        'top_engines': [],
        'top_latent': [],
        'top_fragile': [],
        'notable_cases': []
    }
    
    # Top Franchise Engines
    franchise = results_season[results_season['archetype_2d'] == 'Franchise Engine'].sort_values('cii', ascending=False)
    if len(franchise) > 0:
        stats['top_engines'] = franchise.head(10)[['player_name', 'cii', 'tii', 'career_leverage_mean']].to_dict('records')
    
    # Top Latent Engines
    latent = results_season[results_season['archetype_2d'] == 'Latent Engine'].sort_values('tii', ascending=False)
    if len(latent) > 0:
        stats['top_latent'] = latent.head(10)[['player_name', 'cii', 'tii', 'career_leverage_mean']].to_dict('records')
    
    # Top Fragile Stars (most dangerous)
    fragile = results_season[results_season['archetype_2d'] == 'Fragile Star'].sort_values('cii', ascending=False)
    if len(fragile) > 0:
        stats['top_fragile'] = fragile.head(10)[['player_name', 'cii', 'tii', 'career_leverage_mean', 'has_creation_tools']].to_dict('records')
    
    # Generate report file
    report_path = output_dir / f"report_{season.replace('-', '_')}.md"
    generate_season_report(stats, results_season, df_season, report_path)
    
    # Save CSV
    csv_path = output_dir / f"classification_{season.replace('-', '_')}.csv"
    results_season.to_csv(csv_path, index=False)
    logger.info(f"Saved results to {csv_path}")
    
    return stats


def generate_season_report(stats, results_season, df_season, report_path):
    """Generate a markdown report for a single season."""
    
    with open(report_path, 'w') as f:
        f.write(f"# NBA Creation Independence Analysis: {stats['season']}\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%B %d, %Y')}\n\n")
        f.write("---\n\n")
        
        # Summary Statistics
        f.write("## Summary Statistics\n\n")
        f.write(f"- **Total Players Classified**: {stats['total_players']}\n")
        f.write(f"- **Average CII**: {stats['avg_cii']:.1f}\n")
        f.write(f"- **Average TII**: {stats['avg_tii']:.1f}\n\n")
        
        # Archetype Distribution
        f.write("## Archetype Distribution\n\n")
        f.write("| Archetype | Count | Percentage |\n")
        f.write("|-----------|-------|------------|\n")
        for archetype in sorted(stats['archetype_counts'].keys()):
            count = stats['archetype_counts'][archetype]
            pct = stats['archetype_percentages'][archetype]
            f.write(f"| {archetype} | {count} | {pct:.1f}% |\n")
        f.write("\n")
        
        # Top Franchise Engines
        if len(stats['top_engines']) > 0:
            f.write("## Top Franchise Engines\n\n")
            f.write("| Player | CII | TII | Career Leverage |\n")
            f.write("|--------|-----|-----|-----------------|\n")
            for player in stats['top_engines']:
                f.write(f"| {player['player_name']} | {player['cii']:.1f} | {player['tii']:.1f} | {player['career_leverage_mean']:+.3f} |\n")
            f.write("\n")
        
        # Top Latent Engines
        if len(stats['top_latent']) > 0:
            f.write("## Top Latent Engines\n\n")
            f.write("| Player | CII | TII | Career Leverage |\n")
            f.write("|--------|-----|-----|-----------------|\n")
            for player in stats['top_latent']:
                f.write(f"| {player['player_name']} | {player['cii']:.1f} | {player['tii']:.1f} | {player['career_leverage_mean']:+.3f} |\n")
            f.write("\n")
        
        # Top Fragile Stars
        if len(stats['top_fragile']) > 0:
            f.write("## Top Fragile Stars (High Risk)\n\n")
            f.write("| Player | CII | TII | Career Leverage | Has Tools |\n")
            f.write("|--------|-----|-----|-----------------|-----------|\n")
            for player in stats['top_fragile']:
                tools = "Yes" if player['has_creation_tools'] else "**No**"
                f.write(f"| {player['player_name']} | {player['cii']:.1f} | {player['tii']:.1f} | {player['career_leverage_mean']:+.3f} | {tools} |\n")
            f.write("\n")
        
        # Validation Cases (if applicable)
        f.write("## Validation Cases\n\n")
        
        # Check for known validation cases
        validation_players = {
            'James Harden': 'Franchise Engine',
            'Nikola Jokić': 'Franchise Engine',
            'Luka Dončić': 'Franchise Engine',
            'Jalen Brunson': 'Latent Engine',
            'Ben Simmons': 'Fragile Star',
            'Karl-Anthony Towns': 'Fragile Star',
            'Julius Randle': 'Luxury Amplifier'
        }
        
        f.write("| Player | Expected | Actual | Status |\n")
        f.write("|--------|----------|--------|--------|\n")
        
        for player_name, expected in validation_players.items():
            player_results = results_season[results_season['player_name'].str.contains(player_name, case=False, na=False)]
            if len(player_results) > 0:
                actual = player_results.iloc[0]['archetype_2d']
                status = "✅" if actual == expected else "⚠️"
                f.write(f"| {player_name} | {expected} | {actual} | {status} |\n")
        
        f.write("\n")
        
        # Notable Patterns
        f.write("## Notable Patterns\n\n")
        
        # Count of players with positive vs negative leverage
        positive_leverage = results_season[results_season['career_leverage_mean'] >= 0.01]
        negative_leverage = results_season[results_season['career_leverage_mean'] < -0.02]
        mixed_leverage = results_season[
            (results_season['career_leverage_mean'] >= -0.02) & 
            (results_season['career_leverage_mean'] < 0.01)
        ]
        
        f.write(f"- **Players with Positive Leverage** (Steps Up): {len(positive_leverage)} ({len(positive_leverage)/len(results_season)*100:.1f}%)\n")
        f.write(f"- **Players with Negative Leverage** (Hides): {len(negative_leverage)} ({len(negative_leverage)/len(results_season)*100:.1f}%)\n")
        f.write(f"- **Players with Mixed Leverage**: {len(mixed_leverage)} ({len(mixed_leverage)/len(results_season)*100:.1f}%)\n")
        f.write("\n")
        
        # Players with creation tools
        with_tools = results_season[results_season['has_creation_tools'] == True]
        without_tools = results_season[results_season['has_creation_tools'] == False]
        f.write(f"- **Players with Creation Tools**: {len(with_tools)} ({len(with_tools)/len(results_season)*100:.1f}%)\n")
        f.write(f"- **Players without Creation Tools**: {len(without_tools)} ({len(without_tools)/len(results_season)*100:.1f}%)\n")
        f.write("\n")


def generate_summary_report(all_stats, output_path):
    """Generate a summary report comparing all seasons."""
    
    with open(output_path, 'w') as f:
        f.write("# Multi-Season Classification Summary\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%B %d, %Y')}\n\n")
        f.write("This report compares the 2D classification system across all seasons in the dataset.\n\n")
        f.write("---\n\n")
        
        # Overall Statistics Table
        f.write("## Overall Statistics by Season\n\n")
        f.write("| Season | Players | Avg CII | Avg TII | Engines | Latent | Fragile |\n")
        f.write("|--------|---------|---------|---------|---------|--------|---------|\n")
        
        for stats in sorted(all_stats, key=lambda x: x['season']):
            engines = stats['archetype_counts'].get('Franchise Engine', 0)
            latent = stats['archetype_counts'].get('Latent Engine', 0)
            fragile = stats['archetype_counts'].get('Fragile Star', 0)
            
            f.write(f"| {stats['season']} | {stats['total_players']} | {stats['avg_cii']:.1f} | {stats['avg_tii']:.1f} | {engines} | {latent} | {fragile} |\n")
        
        f.write("\n")
        
        # Archetype Distribution Over Time
        f.write("## Archetype Distribution Over Time\n\n")
        
        # Get all unique archetypes
        all_archetypes = set()
        for stats in all_stats:
            all_archetypes.update(stats['archetype_counts'].keys())
        
        for archetype in sorted(all_archetypes):
            f.write(f"### {archetype}\n\n")
            f.write("| Season | Count | Percentage |\n")
            f.write("|--------|-------|------------|\n")
            
            for stats in sorted(all_stats, key=lambda x: x['season']):
                count = stats['archetype_counts'].get(archetype, 0)
                pct = stats['archetype_percentages'].get(archetype, 0)
                f.write(f"| {stats['season']} | {count} | {pct:.1f}% |\n")
            
            f.write("\n")
        
        # Top Players Across All Seasons
        f.write("## Top Franchise Engines (All Seasons)\n\n")
        f.write("| Season | Player | CII | TII |\n")
        f.write("|--------|--------|-----|-----|\n")
        
        for stats in sorted(all_stats, key=lambda x: x['season']):
            for player in stats['top_engines'][:3]:  # Top 3 per season
                f.write(f"| {stats['season']} | {player['player_name']} | {player['cii']:.1f} | {player['tii']:.1f} |\n")
        
        f.write("\n")
        
        # Validation Case Tracking
        f.write("## Validation Case Tracking\n\n")
        f.write("Tracking known validation cases across seasons:\n\n")
        
        validation_tracking = defaultdict(list)
        
        for stats in sorted(all_stats, key=lambda x: x['season']):
            # We'd need to load the actual results to check validation cases
            # For now, just note that individual season reports contain this
            pass
        
        f.write("See individual season reports for detailed validation case tracking.\n\n")
        
        # Trends Analysis
        f.write("## Trends Analysis\n\n")
        
        # Calculate trends
        seasons_sorted = sorted([s['season'] for s in all_stats])
        avg_cii_trend = [s['avg_cii'] for s in sorted(all_stats, key=lambda x: x['season'])]
        avg_tii_trend = [s['avg_tii'] for s in sorted(all_stats, key=lambda x: x['season'])]
        
        f.write(f"- **Average CII Trend**: {avg_cii_trend[0]:.1f} → {avg_cii_trend[-1]:.1f} ({avg_cii_trend[-1] - avg_cii_trend[0]:+.1f})\n")
        f.write(f"- **Average TII Trend**: {avg_tii_trend[0]:.1f} → {avg_tii_trend[-1]:.1f} ({avg_tii_trend[-1] - avg_tii_trend[0]:+.1f})\n")
        f.write("\n")
        
        # Engine Count Trend
        engine_counts = [s['archetype_counts'].get('Franchise Engine', 0) for s in sorted(all_stats, key=lambda x: x['season'])]
        f.write(f"- **Franchise Engine Count**: {engine_counts[0]} → {engine_counts[-1]} ({engine_counts[-1] - engine_counts[0]:+d})\n")
        
        latent_counts = [s['archetype_counts'].get('Latent Engine', 0) for s in sorted(all_stats, key=lambda x: x['season'])]
        f.write(f"- **Latent Engine Count**: {latent_counts[0]} → {latent_counts[-1]} ({latent_counts[-1] - latent_counts[0]:+d})\n")
        
        fragile_counts = [s['archetype_counts'].get('Fragile Star', 0) for s in sorted(all_stats, key=lambda x: x['season'])]
        f.write(f"- **Fragile Star Count**: {fragile_counts[0]} → {fragile_counts[-1]} ({fragile_counts[-1] - fragile_counts[0]:+d})\n")
        f.write("\n")


def main():
    """Main analysis pipeline."""
    logger.info("=" * 80)
    logger.info("MULTI-SEASON CLASSIFICATION ANALYSIS")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 80)
    
    # Load dataset
    df_full = load_dataset()
    if df_full is None:
        logger.error("Failed to load dataset. Exiting.")
        return
    
    # Get all unique seasons
    seasons = sorted(df_full['season'].unique())
    logger.info(f"Found {len(seasons)} seasons to analyze: {seasons}")
    
    # Create output directory
    output_dir = project_root / 'results' / 'season_reports'
    output_dir.mkdir(exist_ok=True)
    
    # Analyze each season
    all_stats = []
    for season in seasons:
        stats = analyze_season(df_full, season, output_dir)
        if stats:
            all_stats.append(stats)
    
    # Generate summary report
    summary_path = project_root / 'results' / 'multi_season_summary.md'
    generate_summary_report(all_stats, summary_path)
    logger.info(f"\nGenerated summary report: {summary_path}")
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("ANALYSIS COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Analyzed {len(all_stats)} seasons")
    logger.info(f"Individual reports: {output_dir}")
    logger.info(f"Summary report: {summary_path}")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()


