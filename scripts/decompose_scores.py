"""
Decompose CII scores to understand contribution of each component and path.
Run this BEFORE any refactoring to establish baseline.
"""

import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from src.nba_data.phase2_creation_independence.index.self_created import (
    calculate_self_created_score,
    _calculate_perimeter_path_score,
    _calculate_hub_creation_score
)
from src.nba_data.phase2_creation_independence.index.pressure_appetite import calculate_pressure_appetite_score
from src.nba_data.phase2_creation_independence.index.difficulty_embrace import calculate_difficulty_embrace_score
from src.nba_data.phase2_creation_independence.index.defensive_survival import calculate_defensive_survival_score
from src.nba_data.phase2_creation_independence.index.force_multiplication import calculate_force_multiplication_score
from src.nba_data.phase2_creation_independence.index.composite import calculate_cii

def decompose_player_score(player_name: str, season: str, df: pd.DataFrame) -> dict:
    """
    Return complete decomposition of how a player's CII was calculated.
    """
    # Normalize inputs
    player_lower = player_name.lower()
    
    # Filter dataframe
    mask = (df['player_name'].str.lower().str.contains(player_lower, na=False)) & (df['season'] == season)
    player_rows = df[mask]
    
    if player_rows.empty:
        print(f"WARNING: Could not find {player_name} ({season})")
        return None
        
    player_data = player_rows.iloc[0]
    
    # Calculate components
    self_created = calculate_self_created_score(player_data)
    pressure = calculate_pressure_appetite_score(player_data)
    difficulty = calculate_difficulty_embrace_score(player_data)
    defense = calculate_defensive_survival_score(player_data)
    force = calculate_force_multiplication_score(player_data)
    
    # Calculate CII
    cii_result = calculate_cii(player_data)
    
    # Decompose Self-Created (Component 1)
    perimeter_path = _calculate_perimeter_path_score(player_data)
    hub_path = _calculate_hub_creation_score(player_data)
    
    max_path = "Perimeter" if perimeter_path >= hub_path else "Hub"
    
    # Note: Current implementation doesn't have Gravity/Drive-Kick separated yet, 
    # nor multi-modal bonus explicitly returned, so we fill with current state values.
    # The current implementation DOES take MAX(Perimeter, Hub).
    
    return {
        'player': player_name,
        'season': season,
        'cii_total': cii_result['cii'],
        'component_1_self_created': {
            'final_score': self_created,
            'iso_path': perimeter_path, # Current perimeter path is mostly ISO/Pull-up
            'drive_kick_path': 0.0, # Not implemented yet
            'post_hub_path': hub_path,
            'gravity_path': 0.0, # Not implemented yet
            'max_path': max_path,
            'multi_modal_bonus': 0.0, # Not implemented yet
        },
        'component_2_pressure': pressure,
        'component_3_difficulty': difficulty,
        'component_4_defense': defense,
        'component_5_force': force,
        'gates_applied': [], # Not tracking gates in detail for baseline yet
        'classification': cii_result['archetype'],
    }

def run_decomposition_suite():
    """Run decomposition on all validation players."""
    
    # Load dataset
    data_path = project_root / 'results' / 'predictive_dataset_with_friction.csv'
    if not data_path.exists():
        print(f"Error: Dataset not found at {data_path}")
        return

    print(f"Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    # Normalize columns
    df.columns = [c.lower() for c in df.columns]
    
    validation_players = [
        ("LeBron James", "2015-16"),
        ("Stephen Curry", "2016-17"),
        ("Giannis Antetokounmpo", "2020-21"),
        ("Kevin Durant", "2018-19"),
        ("Nikola Jokić", "2022-23"),
        ("Kawhi Leonard", "2018-19"),
        ("Ben Simmons", "2020-21"),
        ("James Harden", "2018-19"),
        ("Trae Young", "2019-20"),
        ("Zach LaVine", "2021-22"),
    ]
    
    results = []
    for player, season in validation_players:
        decomp = decompose_player_score(player, season, df)
        if decomp:
            results.append(decomp)
            
            # Print detailed breakdown
            print(f"\n{'='*60}")
            print(f"PLAYER: {player} ({season})")
            print(f"{'='*60}")
            print(f"CII TOTAL: {decomp['cii_total']:.1f}")
            print(f"\nCOMPONENT 1 (Self-Created) - Weight: 30%")
            print(f"  ISO Path:       {decomp['component_1_self_created']['iso_path']:.1f}")
            print(f"  Drive-Kick:     {decomp['component_1_self_created']['drive_kick_path']:.1f}")
            print(f"  Post Hub:       {decomp['component_1_self_created']['post_hub_path']:.1f}")
            print(f"  Gravity:        {decomp['component_1_self_created']['gravity_path']:.1f}")
            print(f"  MAX PATH:       {decomp['component_1_self_created']['max_path']}")
            print(f"  Multi-Modal:    +{decomp['component_1_self_created']['multi_modal_bonus']:.1f}")
            print(f"  FINAL:          {decomp['component_1_self_created']['final_score']:.1f}")
            print(f"\nCOMPONENT 2 (Pressure):    {decomp['component_2_pressure']:.1f}")
            print(f"COMPONENT 3 (Difficulty):  {decomp['component_3_difficulty']:.1f}")
            print(f"COMPONENT 4 (Defense):     {decomp['component_4_defense']:.1f}")
            print(f"COMPONENT 5 (Force):       {decomp['component_5_force']:.1f}")
            print(f"\nCLASSIFICATION: {decomp['classification']}")
    
    # Save to CSV
    # Flatten the dictionary for CSV
    flat_results = []
    for r in results:
        flat = {
            'player': r['player'],
            'season': r['season'],
            'cii_total': r['cii_total'],
            'c1_final': r['component_1_self_created']['final_score'],
            'c1_iso': r['component_1_self_created']['iso_path'],
            'c1_hub': r['component_1_self_created']['post_hub_path'],
            'c2_pressure': r['component_2_pressure'],
            'c3_difficulty': r['component_3_difficulty'],
            'c4_defense': r['component_4_defense'],
            'c5_force': r['component_5_force'],
            'classification': r['classification']
        }
        flat_results.append(flat)
        
    pd.DataFrame(flat_results).to_csv('results/decomposition_baseline.csv', index=False)
    print(f"\nSaved baseline results to results/decomposition_baseline.csv")
    
if __name__ == "__main__":
    run_decomposition_suite()

