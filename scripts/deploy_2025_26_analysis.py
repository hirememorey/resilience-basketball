#!/usr/bin/env python3
"""
2025-26 Season Deployment Script (Updated)

This script deploys the CII/TII 2D classification system using historical data
to identify players who are:
1. Franchise Engines - Players who CAN be #1 on a championship team
2. Latent Engines - Undervalued players with untapped creation potential
3. Fragile Stars - Players who look like stars but have fatal creation flaws

Key Insight: We use 2024-25 season data (most recent complete season) plus career
patterns to identify players. The classification is based on PROCESS, not outcomes,
so recent regular season data is sufficient for identifying creation independence.

Usage:
    python scripts/deploy_2025_26_analysis.py

Date: December 29, 2025
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from datetime import datetime

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
        logging.FileHandler(project_root / 'logs' / 'deployment_2025_26.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_existing_data():
    """
    Load the existing dataset with all seasons through 2024-25.
    """
    logger.info("=" * 70)
    logger.info("STEP 1: LOADING EXISTING DATASET")
    logger.info("=" * 70)
    
    results_path = project_root / 'results' / 'predictive_dataset_with_friction.csv'
    
    if not results_path.exists():
        logger.error(f"Dataset not found at {results_path}")
        return None
        
    df = pd.read_csv(results_path)
    logger.info(f"Loaded dataset with {len(df)} total player-seasons")
    
    # Show season distribution
    season_counts = df['season'].value_counts().sort_index()
    logger.info("Season distribution:")
    for season, count in season_counts.items():
        logger.info(f"  {season}: {count} players")
    
    # Get most recent season
    most_recent = df['season'].max()
    df_recent = df[df['season'] == most_recent].copy()
    logger.info(f"\nMost recent season ({most_recent}): {len(df_recent)} players")
    
    return df, df_recent, most_recent


def run_2d_classification(df_full, df_recent_season):
    """
    Apply 2D classification (CII × TII) to identify archetypes.
    Uses the full dataset for career context but focuses on most recent season.
    """
    logger.info("=" * 70)
    logger.info("STEP 2: RUNNING 2D CLASSIFICATION")
    logger.info("=" * 70)
    
    # Classify all player-seasons
    results = batch_classify_2d(df_full)
    
    return results


def identify_key_players(results_df, df_full, focus_season):
    """
    Identify and report on key player categories for the focus season.
    """
    logger.info("=" * 70)
    logger.info("STEP 3: IDENTIFYING KEY PLAYERS")
    logger.info("=" * 70)
    
    # Filter to focus season
    results_season = results_df[results_df['season'] == focus_season].copy()
    
    # Category breakdowns
    franchise_engines = results_season[results_season['archetype_2d'] == 'Franchise Engine'].copy()
    latent_engines = results_season[results_season['archetype_2d'] == 'Latent Engine'].copy()
    strong_creators = results_season[results_season['archetype_2d'] == 'Strong Creator'].copy()
    fragile_stars = results_season[results_season['archetype_2d'] == 'Fragile Star'].copy()
    luxury_amplifiers = results_season[results_season['archetype_2d'] == 'Luxury Amplifier'].copy()
    developing = results_season[results_season['archetype_2d'].str.contains('Developing', na=False)].copy()
    
    # Print summary
    print("\n" + "=" * 80)
    print("NBA CREATION INDEPENDENCE ANALYSIS")
    print(f"Based on: {focus_season} season data + career patterns")
    print(f"Analysis Date: {datetime.now().strftime('%B %d, %Y')}")
    print("=" * 80)
    
    print(f"\n📊 ARCHETYPE DISTRIBUTION ({focus_season})")
    print("-" * 40)
    for archetype, count in results_season['archetype_2d'].value_counts().items():
        pct = count / len(results_season) * 100
        print(f"  {archetype}: {count} ({pct:.1f}%)")
    
    # === FRANCHISE ENGINES ===
    print("\n" + "=" * 80)
    print("🚀 FRANCHISE ENGINES (CII ≥ 74)")
    print("   Players who CAN be #1 on a championship team")
    print("=" * 80)
    
    if len(franchise_engines) > 0:
        franchise_engines = franchise_engines.sort_values('cii', ascending=False)
        for _, row in franchise_engines.head(25).iterrows():
            # Get age from full dataset
            player_mask = (df_full['player_name'].str.lower() == row['player_name'].lower()) & \
                         (df_full['season'] == focus_season)
            age = df_full.loc[player_mask, 'age'].values[0] if player_mask.any() else 'N/A'
            usg = df_full.loc[player_mask, 'usg_pct'].values[0] * 100 if player_mask.any() else 0
            
            print(f"\n  {row['player_name']} (Age: {age:.0f}, USG: {usg:.1f}%)")
            print(f"    CII: {row['cii']:.1f} | TII: {row['tii']:.1f}")
            print(f"    Career Pattern: {row['career_pattern']} ({row['career_positive_seasons']:.0f}+/{row['career_negative_seasons']:.0f}-)")
    else:
        print("  No Franchise Engines identified")
    
    # === LATENT ENGINES ===
    print("\n" + "=" * 80)
    print("⭐ LATENT ENGINES (Medium CII + High TII + Positive Leverage)")
    print("   THE ALPHA: Undervalued players with untapped creation potential")
    print("   These players could be Franchise Engines with more opportunity")
    print("=" * 80)
    
    if len(latent_engines) > 0:
        # Sort by TII to show highest potential first
        latent_engines = latent_engines.sort_values('tii', ascending=False)
        
        for _, row in latent_engines.head(25).iterrows():
            # Get age and usage from full dataset
            player_mask = (df_full['player_name'].str.lower() == row['player_name'].lower()) & \
                         (df_full['season'] == focus_season)
            age = df_full.loc[player_mask, 'age'].values[0] if player_mask.any() else 'N/A'
            usg = df_full.loc[player_mask, 'usg_pct'].values[0] * 100 if player_mask.any() else 0
            
            print(f"\n  {row['player_name']} (Age: {age:.0f}, USG: {usg:.1f}%)")
            print(f"    CII: {row['cii']:.1f} | TII: {row['tii']:.1f}")
            print(f"    Career Leverage: {row['career_leverage_mean']:+.3f} ({row['career_positive_seasons']:.0f}+/{row['career_negative_seasons']:.0f}-)")
            print(f"    Creation Tools: {'YES ✓' if row['has_creation_tools'] else 'NO ✗'}")
    else:
        print("  No Latent Engines identified in current season")
    
    # === FRAGILE STARS ===
    print("\n" + "=" * 80)
    print("⚠️  FRAGILE STARS (High status + Low CII + Fatal flaws)")
    print("   Players who LOOK like stars but have fundamental creation gaps")
    print("   CAUTION: These players may collapse in playoff settings")
    print("=" * 80)
    
    if len(fragile_stars) > 0:
        fragile_stars = fragile_stars.sort_values('cii', ascending=False)
        for _, row in fragile_stars.head(20).iterrows():
            player_mask = (df_full['player_name'].str.lower() == row['player_name'].lower()) & \
                         (df_full['season'] == focus_season)
            age = df_full.loc[player_mask, 'age'].values[0] if player_mask.any() else 'N/A'
            usg = df_full.loc[player_mask, 'usg_pct'].values[0] * 100 if player_mask.any() else 0
            
            print(f"\n  {row['player_name']} (Age: {age:.0f}, USG: {usg:.1f}%)")
            print(f"    CII: {row['cii']:.1f} | TII: {row['tii']:.1f}")
            print(f"    Career Pattern: {row['career_pattern']}")
            print(f"    Creation Tools: {'YES' if row['has_creation_tools'] else 'NO ← FATAL'}")
            print(f"    Reasoning: {row['reasoning'][:80]}...")
    else:
        print("  No Fragile Stars identified")
    
    # === LUXURY AMPLIFIERS ===
    print("\n" + "=" * 80)
    print("💎 LUXURY AMPLIFIERS")
    print("   Excellent players who thrive as #2 alongside an Engine")
    print("=" * 80)
    
    if len(luxury_amplifiers) > 0:
        luxury_amplifiers = luxury_amplifiers.sort_values('cii', ascending=False)
        for _, row in luxury_amplifiers.head(15).iterrows():
            print(f"\n  {row['player_name']}")
            print(f"    CII: {row['cii']:.1f} | TII: {row['tii']:.1f}")
    else:
        print("  No Luxury Amplifiers identified")
    
    # === STRONG CREATORS ===
    print("\n" + "=" * 80)
    print("💪 STRONG CREATORS")
    print("   High creation ability, can be primary option on good teams")
    print("=" * 80)
    
    if len(strong_creators) > 0:
        for _, row in strong_creators.head(15).iterrows():
            print(f"\n  {row['player_name']}")
            print(f"    CII: {row['cii']:.1f} | TII: {row['tii']:.1f}")
    else:
        print("  No Strong Creators identified")
    
    # === DEVELOPING PLAYERS ===
    print("\n" + "=" * 80)
    print("🌱 DEVELOPING PLAYERS (High TII, Lower CII)")
    print("   Young players with creation potential not yet fully realized")
    print("=" * 80)
    
    if len(developing) > 0:
        developing = developing.sort_values('tii', ascending=False)
        for _, row in developing.head(15).iterrows():
            player_mask = (df_full['player_name'].str.lower() == row['player_name'].lower()) & \
                         (df_full['season'] == focus_season)
            age = df_full.loc[player_mask, 'age'].values[0] if player_mask.any() else 'N/A'
            
            if pd.notna(age) and age <= 24:  # Focus on young players
                print(f"\n  {row['player_name']} (Age: {age:.0f})")
                print(f"    CII: {row['cii']:.1f} | TII: {row['tii']:.1f}")
                print(f"    Archetype: {row['archetype_2d']}")
    else:
        print("  No Developing Players identified")
    
    return {
        'franchise_engines': franchise_engines,
        'latent_engines': latent_engines,
        'strong_creators': strong_creators,
        'fragile_stars': fragile_stars,
        'luxury_amplifiers': luxury_amplifiers,
        'developing': developing
    }


def generate_rookie_contract_alpha(results_df, df_full, focus_season):
    """
    Identify Latent Engines on rookie contracts - the ultimate alpha.
    """
    print("\n" + "=" * 80)
    print("💰 ALPHA ALERT: LATENT ENGINES UNDER 26")
    print("   Players with high TII who could become Franchise Engines")
    print("   Historical examples: Brunson (2020-21), Harden at OKC, SGA")
    print("=" * 80)
    
    results_season = results_df[results_df['season'] == focus_season].copy()
    latent_engines = results_season[results_season['archetype_2d'] == 'Latent Engine'].copy()
    
    if len(latent_engines) == 0:
        print("  No Latent Engines identified")
        return
    
    # Get age data
    for idx, row in latent_engines.iterrows():
        player_mask = (df_full['player_name'].str.lower() == row['player_name'].lower()) & \
                     (df_full['season'] == focus_season)
        if player_mask.any():
            latent_engines.loc[idx, 'age'] = df_full.loc[player_mask, 'age'].values[0]
            latent_engines.loc[idx, 'usg'] = df_full.loc[player_mask, 'usg_pct'].values[0]
    
    # Filter to young players (under 26)
    young_latent = latent_engines[latent_engines['age'] <= 26].sort_values('tii', ascending=False)
    
    if len(young_latent) > 0:
        print(f"\n  🔥 Found {len(young_latent)} young Latent Engines (age ≤ 26):")
        print("  " + "-" * 60)
        for _, row in young_latent.iterrows():
            print(f"\n  ⭐ {row['player_name']} (Age: {row['age']:.0f}, Current USG: {row['usg']*100:.1f}%)")
            print(f"     CII: {row['cii']:.1f} | TII: {row['tii']:.1f}")
            print(f"     Career Leverage: {row['career_leverage_mean']:+.3f} ({row['career_pattern']})")
            print(f"     → POTENTIAL: If given 28%+ usage, could become Franchise Engine")
    else:
        print("  No young (≤26) Latent Engines found")
    
    # Also show players with high TII regardless of current archetype
    print("\n" + "-" * 60)
    print("  Players with ELITE TII (≥75) under age 26:")
    
    high_tii = results_season[results_season['tii'] >= 75].copy()
    for idx, row in high_tii.iterrows():
        player_mask = (df_full['player_name'].str.lower() == row['player_name'].lower()) & \
                     (df_full['season'] == focus_season)
        if player_mask.any():
            high_tii.loc[idx, 'age'] = df_full.loc[player_mask, 'age'].values[0]
    
    young_high_tii = high_tii[high_tii['age'] <= 26].sort_values('tii', ascending=False)
    
    if len(young_high_tii) > 0:
        for _, row in young_high_tii.head(10).iterrows():
            status = "✓" if row['archetype_2d'] in ['Franchise Engine', 'Latent Engine'] else ""
            print(f"  {row['player_name']} (Age: {row['age']:.0f}): TII {row['tii']:.1f} - {row['archetype_2d']} {status}")


def deep_dive_key_players(results_df, df_full, focus_season):
    """
    Provide detailed breakdowns for the most interesting players.
    """
    print("\n" + "=" * 80)
    print("🔍 DEEP DIVE: DETAILED PLAYER BREAKDOWNS")
    print("=" * 80)
    
    results_season = results_df[results_df['season'] == focus_season].copy()
    
    # Pick interesting cases for deep dive
    interesting_cases = [
        # Top Franchise Engines
        ('Highest CII', results_season.nlargest(3, 'cii')),
        # Top Latent Engines  
        ('Top Latent Engines', results_season[results_season['archetype_2d'] == 'Latent Engine'].nlargest(3, 'tii')),
        # Top Fragile Stars (most dangerous false positives)
        ('Top Fragile Stars', results_season[results_season['archetype_2d'] == 'Fragile Star'].nlargest(3, 'cii')),
    ]
    
    for label, subset in interesting_cases:
        if len(subset) > 0:
            print(f"\n{label}:")
            print("-" * 50)
            for _, row in subset.iterrows():
                player_mask = (df_full['player_name'].str.lower() == row['player_name'].lower()) & \
                             (df_full['season'] == focus_season)
                if player_mask.any():
                    player_data = df_full[player_mask].iloc[0]
                    
                    print(f"\n  {row['player_name']} ({row['archetype_2d']})")
                    print(f"    CII: {row['cii']:.1f} | TII: {row['tii']:.1f}")
                    print(f"    Age: {player_data['age']:.0f} | USG: {player_data['usg_pct']*100:.1f}% | TS: {player_data['ts_pct']*100:.1f}%")
                    print(f"    Career Leverage: {row['career_leverage_mean']:+.3f}")
                    
                    # Show CII components if available
                    if 'cii_components' in row and row['cii_components']:
                        comps = row['cii_components']
                        print(f"    CII Components:")
                        for comp_name, comp_val in comps.items():
                            print(f"      - {comp_name}: {comp_val:.1f}")


def save_results(results_df, categories, focus_season):
    """Save classification results to CSV."""
    # Save full classification results
    output_path = project_root / 'results' / f'classification_2d_{focus_season.replace("-", "_")}.csv'
    
    # Filter to focus season for the main output
    results_season = results_df[results_df['season'] == focus_season].copy()
    results_season.to_csv(output_path, index=False)
    logger.info(f"Saved 2D classification results to {output_path}")
    
    # Save Latent Engines specifically
    if len(categories['latent_engines']) > 0:
        latent_path = project_root / 'results' / f'latent_engines_{focus_season.replace("-", "_")}.csv'
        categories['latent_engines'].to_csv(latent_path, index=False)
        logger.info(f"Saved Latent Engines to {latent_path}")
    
    # Save Franchise Engines
    if len(categories['franchise_engines']) > 0:
        engine_path = project_root / 'results' / f'franchise_engines_{focus_season.replace("-", "_")}.csv'
        categories['franchise_engines'].to_csv(engine_path, index=False)
        logger.info(f"Saved Franchise Engines to {engine_path}")
    
    # Save Fragile Stars (important for avoiding bad contracts)
    if len(categories['fragile_stars']) > 0:
        fragile_path = project_root / 'results' / f'fragile_stars_{focus_season.replace("-", "_")}.csv'
        categories['fragile_stars'].to_csv(fragile_path, index=False)
        logger.info(f"Saved Fragile Stars to {fragile_path}")


def main():
    """Main deployment pipeline."""
    logger.info("=" * 80)
    logger.info("DEPLOYING CII/TII 2D CLASSIFICATION SYSTEM")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 80)
    
    # Step 1: Load existing data
    result = load_existing_data()
    if result is None:
        logger.error("Failed to load data. Exiting.")
        return
    
    df_full, df_recent, focus_season = result
    
    # Step 2: Run 2D classification
    results = run_2d_classification(df_full, df_recent)
    
    # Step 3: Identify key players
    categories = identify_key_players(results, df_full, focus_season)
    
    # Step 4: Look for alpha (young Latent Engines)
    generate_rookie_contract_alpha(results, df_full, focus_season)
    
    # Step 5: Deep dive on interesting players
    deep_dive_key_players(results, df_full, focus_season)
    
    # Step 6: Save results
    save_results(results, categories, focus_season)
    
    print("\n" + "=" * 80)
    print("DEPLOYMENT COMPLETE")
    print("=" * 80)
    print(f"Analysis based on: {focus_season} season")
    print(f"Total players classified: {len(results[results['season'] == focus_season])}")
    print(f"Results saved to: results/classification_2d_{focus_season.replace('-', '_')}.csv")
    print("=" * 80)


if __name__ == '__main__':
    main()
