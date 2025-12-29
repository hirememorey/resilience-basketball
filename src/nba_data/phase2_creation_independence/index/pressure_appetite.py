"""
Component 2: Pressure Appetite Score (Weight: 25%)

Question: When the game matters, do you WANT the ball?

Physics Principle:
True Engines expand their volume under pressure (Luka, Jordan).
Fragile Stars shrink their volume to avoid failure (Simmons, KAT).
This measures the "Abdication Tax" - efficiency maintained by passing the grenade is a failure of resilience.

Sub-Metrics:
- Clutch Usage Absolute (50%): Actual usage in clutch moments.
- Relative Usage Change (30%): (Clutch USG - Base USG). Do you step up or hide?
- Playoff Elevation (20%): Does your usage hold up in the playoffs?

Validation Cases:
- Ben Simmons: ~20 (Usage drops significantly under pressure)
- Luka Dončić: ~95 (Usage increases, demands the ball)
- James Harden: ~85 (Historically high volume, though efficiency may vary)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Weights for sub-metrics
WEIGHTS = {
    'clutch_usage_absolute': 0.50,
    'relative_usage_change': 0.30,
    'playoff_elevation': 0.20
}

def calculate_pressure_appetite_score(player_data: pd.Series) -> float:
    """
    Calculate Pressure Appetite Score (0-100).
    
    Args:
        player_data: Series containing player features for a season
        
    Returns:
        Score from 0-100 where:
        - 0-30: Shrinks under pressure (Role players, Fragile Stars)
        - 30-60: Maintains role (Standard starters)
        - 60-80: Steps up (Strong Creators)
        - 80-100: Demands the ball (Franchise Engines)
    """
    
    # Sub-metric 1: Clutch Usage Absolute (50%)
    clutch_score = _calculate_clutch_usage_score(player_data)
    
    # Sub-metric 2: Relative Usage Change (30%)
    appetite_score = _calculate_relative_appetite_score(player_data)
    
    # Sub-metric 3: Playoff Elevation (20%)
    playoff_score = _calculate_playoff_elevation_score(player_data)
    
    # Weighted combination
    final_score = (
        WEIGHTS['clutch_usage_absolute'] * clutch_score +
        WEIGHTS['relative_usage_change'] * appetite_score +
        WEIGHTS['playoff_elevation'] * playoff_score
    )
    
    return round(np.clip(final_score, 0, 100), 2)


def _calculate_clutch_usage_score(data: pd.Series) -> float:
    """
    Calculate score based on absolute usage in clutch time.
    
    This answers: "Does this player want the ball in crunch time?"
    
    Benchmarks:
    - Role Player: <15%
    - Star: 25-30%
    - Engine: 35%+
    """
    # Try different case variations
    clutch_usg = data.get('clutch_usg_absolute', data.get('CLUTCH_USG_ABSOLUTE', 0.15))
    
    # Handle percentage vs decimal
    if clutch_usg > 1.0:
        clutch_usg = clutch_usg / 100.0
        
    # Scale: 
    # 10% -> 0 score
    # 40% -> 100 score
    score = (clutch_usg - 0.10) / 0.30 * 100
    return np.clip(score, 0, 100)


def _calculate_relative_appetite_score(data: pd.Series) -> float:
    """
    Calculate score based on how usage changes from base to clutch.
    
    Positive = stepping UP under pressure (good)
    Negative = hiding under pressure (bad - the Simmons pattern)
    
    Benchmarks:
    - Hiding: -25% drop (Simmons) -> Score 0
    - Stable: 0% change -> Score 50
    - Elevation: +25% rise (Luka) -> Score 100
    """
    # Try different case variations
    # relative_usage_drop might be named leverage_usg_delta in some versions
    relative_change = data.get('relative_usage_drop', 
                         data.get('RELATIVE_USAGE_DROP', 
                           data.get('leverage_usg_delta', 
                             data.get('LEVERAGE_USG_DELTA', 0))))
    
    # Map: -0.25 (hiding) = 0, 0 (stable) = 50, +0.25 (stepping up) = 100
    # Slope = (100 - 50) / 0.25 = 200
    score = 50 + (relative_change * 200)
    
    return np.clip(score, 0, 100)


def _calculate_playoff_elevation_score(data: pd.Series) -> float:
    """
    Calculate score based on usage retention/elevation in playoffs.
    
    Players who embrace pressure often scale volume in playoffs.
    
    Benchmarks:
    - Drop: -10% or worse -> Score 35 (or lower)
    - Stable: 0% -> Score 50
    - Rise: +10% -> Score 65+
    """
    playoff_usg = data.get('playoff_usg_pct', data.get('PLAYOFF_USG_PCT', None))
    rs_usg = data.get('usg_pct', data.get('USG_PCT', 0.20))
    
    # Handle percentage vs decimal
    if rs_usg > 1.0: rs_usg /= 100.0
    if playoff_usg is not None and playoff_usg > 1.0: playoff_usg /= 100.0
    
    # If no playoff data, default to neutral/base usage
    if playoff_usg is None or pd.isna(playoff_usg) or playoff_usg == 0:
        playoff_usg = rs_usg
        
    if rs_usg > 0.05:
        playoff_bump = (playoff_usg - rs_usg) / rs_usg
    else:
        playoff_bump = 0
        
    # Scale:
    # -0.20 (-20% drop) -> 20
    # 0.00 (flat) -> 50
    # +0.20 (+20% rise) -> 80
    score = 50 + (playoff_bump * 150)
    
    return np.clip(score, 0, 100)


def get_required_features() -> List[str]:
    """Return list of features required for this component."""
    return [
        'clutch_usg_absolute',
        'relative_usage_drop', # Or leverage_usg_delta
        'playoff_usg_pct',
        'usg_pct'
    ]


def get_missing_features(df: pd.DataFrame) -> List[str]:
    """Check which required features are missing from dataset."""
    required = get_required_features()
    # Check lowercase versions since we often normalize
    cols = [c.lower() for c in df.columns]
    missing = [f for f in required if f.lower() not in cols]
    return missing


def diagnose_pressure_appetite(player_data: pd.Series):
    """Prints a detailed breakdown of the pressure appetite score for a player."""
    player_name = player_data.get('player_name', 'Unknown')
    season = player_data.get('season', 'N/A')
    print(f"\n--- Diagnosing Pressure Appetite: {player_name} ({season}) ---")

    # 1. Clutch Usage Absolute
    clutch_usg = player_data.get('clutch_usg_absolute', player_data.get('CLUTCH_USG_ABSOLUTE', 0))
    clutch_score = _calculate_clutch_usage_score(player_data)
    print(f"  Clutch Usage (W: 50%): {clutch_score:.1f}")
    print(f"    - Value: {clutch_usg:.3f}")

    # 2. Relative Change
    relative_change = player_data.get('relative_usage_drop', 
                                    player_data.get('RELATIVE_USAGE_DROP', 
                                      player_data.get('leverage_usg_delta', 
                                        player_data.get('LEVERAGE_USG_DELTA', 0))))
    appetite_score = _calculate_relative_appetite_score(player_data)
    print(f"  Relative Change (W: 30%): {appetite_score:.1f}")
    print(f"    - Value: {relative_change:.3f}")

    # 3. Playoff Elevation
    playoff_usg = player_data.get('playoff_usg_pct', player_data.get('PLAYOFF_USG_PCT', 0))
    rs_usg = player_data.get('usg_pct', player_data.get('USG_PCT', 0))
    playoff_score = _calculate_playoff_elevation_score(player_data)
    print(f"  Playoff Elevation (W: 20%): {playoff_score:.1f}")
    print(f"    - RS Usage: {rs_usg:.3f}")
    print(f"    - PO Usage: {playoff_usg:.3f}")

    final_score = calculate_pressure_appetite_score(player_data)
    print(f"  ---------------------------------")
    print(f"  Final Pressure Appetite Score: {final_score:.2f}")


VALIDATION_CASES: Dict[str, Dict] = {
    'Ben Simmons': {'expected_score': 20, 'tolerance': 15},  # Usage DROPS under pressure
    'Luka Dončić': {'expected_score': 95, 'tolerance': 10},  # Usage INCREASES under pressure
    'James Harden': {'expected_score': 85, 'tolerance': 10}, # Historically clutch
}


if __name__ == '__main__':
    from pathlib import Path
    
    dataset_path = Path(__file__).parents[4] / 'results' / 'predictive_dataset_with_friction.csv'
    
    if not dataset_path.exists():
        print("Dataset not found. Cannot run diagnosis.")
    else:
        print(f"Loading dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)
        # Normalize column names to lower case for consistency
        df.columns = [c.lower() for c in df.columns]

        # Critical Validation Cases
        players_to_diagnose = {
            'Ben Simmons': ['2018-19', '2020-21'], # The Abdicator
            'Luka Dončić': ['2020-21', '2023-24'], # The Engine
            'James Harden': ['2018-19', '2019-20'], # The System
            'Trae Young': ['2020-21'], # High volume creator
            'Rudy Gobert': ['2020-21'], # Converter (should be low)
        }

        for player_name, seasons in players_to_diagnose.items():
            for season in seasons:
                # Fuzzy match for player name
                player_mask = df['player_name'].str.lower().str.contains(player_name.lower())
                season_mask = df['season'] == season
                
                player_data = df[player_mask & season_mask]
                
                if not player_data.empty:
                    # Take the first match (sometimes multiple rows if traded, take max G or similar if needed, 
                    # but usually unique per team-season in this dataset)
                    # Ideally we want the row with most minutes or aggregated.
                    # For now just take the first one found.
                    diagnose_pressure_appetite(player_data.iloc[0])
                else:
                    print(f"\n--- Could not find data for {player_name} in {season} ---")
