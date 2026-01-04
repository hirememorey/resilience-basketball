"""
Run validation with bare (no gates) CII calculator.
Document what the pure architecture produces.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from src.nba_data.phase2_creation_independence.index.cii_bare import BareCIICalculator

def get_player_data(player_name: str, season: str, df: pd.DataFrame) -> dict:
    """Helper to get player data from dataframe."""
    player_lower = player_name.lower().replace('ć', '.').replace('ö', '.')
    mask = (df['player_name'].str.lower().str.contains(player_lower, na=False)) & (df['season'] == season)
    rows = df[mask]
    if rows.empty:
        return None
    return rows.iloc[0].to_dict()

def run_bare_validation():
    """Run all validation players through bare CII."""
    
    calculator = BareCIICalculator()
    data_path = project_root / 'results' / 'tracking_data_merged.csv'
    
    if not data_path.exists():
        print(f"Error: Dataset not found at {data_path}")
        return

    print(f"Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    # Normalize columns
    df.columns = [c.lower() for c in df.columns]
    
    validation_players = [
        # Sanity checks (should be Engines)
        ("LeBron James", "2015-16", "Franchise Engine"),
        ("Stephen Curry", "2016-17", "Franchise Engine"),
        ("Giannis Antetokounmpo", "2020-21", "Franchise Engine"),
        ("Kevin Durant", "2018-19", "Franchise Engine"),
        ("Nikola Jokić", "2022-23", "Franchise Engine"),
        ("Kawhi Leonard", "2018-19", "Franchise Engine"),
        # Sanity checks (should be Fragile/Low)
        ("Ben Simmons", "2020-21", "Fragile Star"),
        # Discriminant pairs
        ("Trae Young", "2019-20", "Franchise Engine"),
        ("Ja Morant", "2021-22", "Franchise Engine"),
        ("Jordan Poole", "2021-22", "Fragile Star"),
        ("Zach LaVine", "2021-22", "Strong Creator"),
        ("Donovan Mitchell", "2021-22", "Franchise Engine"),
    ]
    
    results = []
    
    for player, season, expected in validation_players:
        player_data = get_player_data(player, season, df)
        if player_data is None:
            print(f"SKIPPING: {player} ({season}) - not found")
            continue
            
        result = calculator.calculate(player_data)
        
        # Determine classification based on CII
        cii = result['cii_total']
        if cii >= 74:
            classification = "Franchise Engine"
        elif cii >= 60:
            classification = "Strong Creator"
        elif cii >= 45:
            classification = "Developing/Amplifier"
        else:
            classification = "Fragile/Role"
        
        correct = classification == expected or (expected == "Fragile Star" and cii < 50)
        
        results.append({
            'player': player,
            'season': season,
            'expected': expected,
            'cii': cii,
            'classification': classification,
            'correct': correct,
            'c1_self_created': result['component_scores']['self_created'],
            'c1_primary_mode': result['self_created_breakdown']['primary_mode'],
            'c1_iso': result['self_created_breakdown']['path_scores']['iso'],
            'c1_drive_kick': result['self_created_breakdown']['path_scores']['drive_kick'],
            'c1_post_hub': result['self_created_breakdown']['path_scores']['post_hub'],
            'c1_gravity': result['self_created_breakdown']['path_scores']['gravity'],
            'c2_pressure': result['component_scores']['pressure_appetite'],
            'c3_difficulty': result['component_scores']['difficulty_embrace'],
            'c4_defense': result['component_scores']['defensive_survival'],
            'c5_force': result['component_scores']['force_multiplication'],
        })
        
        print(f"\n{'='*60}")
        print(f"{player} ({season})")
        print(f"{'='*60}")
        print(f"CII: {cii:.1f} | Expected: {expected} | Got: {classification} | {'✅' if correct else '❌'}")
        print(f"\nPath Scores:")
        print(f"  ISO:        {result['self_created_breakdown']['path_scores']['iso']:.1f}")
        print(f"  Drive-Kick: {result['self_created_breakdown']['path_scores']['drive_kick']:.1f}")
        print(f"  Post Hub:   {result['self_created_breakdown']['path_scores']['post_hub']:.1f}")
        print(f"  Gravity:    {result['self_created_breakdown']['path_scores']['gravity']:.1f}")
        print(f"  PRIMARY:    {result['self_created_breakdown']['primary_mode']}")
    
    # Summary
    results_df = pd.DataFrame(results)
    results_df.to_csv('results/bare_validation_results.csv', index=False)
    
    passed = results_df['correct'].sum()
    total = len(results_df)
    print(f"\n{'='*60}")
    print(f"BARE VALIDATION SUMMARY: {passed}/{total} correct ({100*passed/total:.1f}%)")
    print(f"{'='*60}")
    
    # Failure analysis
    failures = results_df[~results_df['correct']]
    if len(failures) > 0:
        print("\nFAILURES TO INVESTIGATE:")
        for _, row in failures.iterrows():
            print(f"\n{row['player']} ({row['season']})")
            print(f"  Expected: {row['expected']}, Got: {row['classification']} (CII: {row['cii']:.1f})")
            print(f"  Primary mode: {row['c1_primary_mode']}")
            print(f"  Path scores: ISO={row['c1_iso']:.1f}, DK={row['c1_drive_kick']:.1f}, Hub={row['c1_post_hub']:.1f}, Grav={row['c1_gravity']:.1f}")

if __name__ == "__main__":
    run_bare_validation()

