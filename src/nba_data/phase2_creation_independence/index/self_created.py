"""
Component 1: Self-Created Shot Score (Weight: 30%)

Question: Can you generate a quality shot without a play being run?

Physics Principle:
A player who can create their own shot is not dependent on the system.
This is the difference between "IS the situation" vs "NEEDS the situation."

Sub-Metrics:
- Unassisted FG% (25%): What % of made shots are unassisted?
- ISO + Pull-up Volume (30%): How often does the player create?
- Self-Created Efficiency (30%): How efficient are self-created shots?
- Creation Tools (15%): Does the player have stepback, fadeaway, etc.?

Validation Cases:
- Ben Simmons: ~5 (near zero self-created jumpers)
- James Harden: ~95 (elite stepback, any shot anytime)
- Luka Dončić: ~95 (maximum creation)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


# Weights for sub-metrics
WEIGHTS = {
    'unassisted_rate': 0.25,
    'creation_volume': 0.30,
    'self_created_efficiency': 0.30,
    'creation_tools': 0.15
}


def calculate_self_created_score(player_data: pd.Series) -> float:
    """
    Calculate Self-Created Shot Score (0-100).
    
    Args:
        player_data: Series containing player features for a season
        
    Returns:
        Score from 0-100 where:
        - 0-20: No self-creation (Simmons)
        - 20-50: Limited creation (role players)
        - 50-70: Moderate creation (secondary creators)
        - 70-90: High creation (primary options)
        - 90-100: Elite creation (Harden, Luka)
    """
    
    # Sub-metric 1: Unassisted FG Rate (25%)
    unassisted_score = _calculate_unassisted_score(player_data)
    
    # Sub-metric 2: ISO + Pull-up Volume (30%)
    volume_score = _calculate_creation_volume_score(player_data)
    
    # Sub-metric 3: Self-Created Efficiency (30%)
    efficiency_score = _calculate_self_created_efficiency_score(player_data)
    
    # Sub-metric 4: Creation Tools Availability (15%)
    tools_score = _calculate_creation_tools_score(player_data)
    
    # Weighted combination
    final_score = (
        WEIGHTS['unassisted_rate'] * unassisted_score +
        WEIGHTS['creation_volume'] * volume_score +
        WEIGHTS['self_created_efficiency'] * efficiency_score +
        WEIGHTS['creation_tools'] * tools_score
    )
    
    return round(np.clip(final_score, 0, 100), 2)


def _calculate_unassisted_score(data: pd.Series) -> float:
    """
    Calculate score based on unassisted field goal rate.
    
    Higher unassisted rate = more self-created scoring.
    
    Benchmarks:
    - Simmons: ~35% (mostly assisted on dunks)
    - Average: ~50%
    - Harden: ~65% (creates most of his own)
    """
    # TODO: Collect UNASSISTED_FG_PCT from tracking data
    # For now, use creation_volume_ratio as proxy
    unassisted_rate = data.get('UNASSISTED_FG_PCT', None)
    
    if unassisted_rate is None:
        # Fallback: estimate from creation_volume_ratio
        cvr = data.get('creation_volume_ratio', 
                       data.get('CREATION_VOLUME_RATIO', 0.5))
        unassisted_rate = 0.35 + (cvr * 0.35)  # Scale 0.35-0.70
    
    # Scale: 35% = 0, 65%+ = 100
    score = (unassisted_rate - 0.35) / 0.30 * 100
    return np.clip(score, 0, 100)


def _calculate_creation_volume_score(data: pd.Series) -> float:
    """
    Calculate score based on ISO and pull-up volume.
    
    Measures how often the player is asked/chooses to create.
    
    Benchmarks:
    - Role player: <2 possessions/game
    - Average starter: 2-4 possessions/game
    - Primary creator: 4-8 possessions/game
    - Elite heliocentric: 8+ possessions/game
    """
    # ISO possessions
    iso_poss = data.get('ISO_POSS_RS', data.get('ISO_POSS', 0))
    
    # Pull-up attempts (3-6 and 7+ dribble shots)
    fga_3_dribble = data.get('FGA_3_DRIBBLE', 0)
    fga_7_dribble = data.get('FGA_7_DRIBBLE', 0)
    
    # Total creation volume per game (approximate)
    total_creation = iso_poss + fga_3_dribble + fga_7_dribble
    
    # Scale: 2 = 0, 8+ = 100
    score = (total_creation - 2.0) / 6.0 * 100
    return np.clip(score, 0, 100)


def _calculate_self_created_efficiency_score(data: pd.Series) -> float:
    """
    Calculate score based on efficiency on self-created shots.
    
    Measures ability to score EFFICIENTLY when creating.
    
    Benchmarks:
    - Poor: <40% EFG on ISO
    - Average: 40-45% EFG
    - Good: 45-50% EFG
    - Elite: 50%+ EFG (Harden stepback range)
    """
    efg_iso = data.get('EFG_ISO_WEIGHTED', data.get('ISO_EFG_PCT', 0.45))
    
    # Scale: 40% = 0, 55%+ = 100
    score = (efg_iso - 0.40) / 0.15 * 100
    return np.clip(score, 0, 100)


def _calculate_creation_tools_score(data: pd.Series) -> float:
    """
    Calculate score based on availability of creation tools.
    
    Does the player have stepback, fadeaway, floater, etc.?
    
    Proxy: Use deep ISO (7+ dribbles) as indicator.
    Players with tools can operate in deep ISO situations.
    """
    fga_7_dribble = data.get('FGA_7_DRIBBLE', 0)
    fga_iso_total = data.get('FGA_ISO_TOTAL', 1)
    
    if fga_iso_total < 0.5:
        return 0  # No creation at all
    
    # What % of creation is deep ISO?
    deep_ratio = fga_7_dribble / max(fga_iso_total, 1)
    
    # Also factor in time of possession (longer = more tools used)
    time_of_poss = data.get('time_of_poss', 3.0)
    time_factor = min(time_of_poss / 6.0, 1.0)  # 6+ seconds = full credit
    
    # Combined score
    score = (deep_ratio * 100 * 0.6) + (time_factor * 100 * 0.4)
    return np.clip(score, 0, 100)


def get_required_features() -> List[str]:
    """Return list of features required for this component."""
    return [
        # Primary features
        'UNASSISTED_FG_PCT',        # Needs collection from tracking
        'ISO_POSS_RS',              # From playtype data
        'FGA_3_DRIBBLE',            # From shooting stats
        'FGA_7_DRIBBLE',            # From shooting stats
        'FGA_ISO_TOTAL',            # Calculated
        'EFG_ISO_WEIGHTED',         # Calculated
        # Fallback features
        'creation_volume_ratio',    # Existing feature
        'time_of_poss',             # From tracking data
    ]


def get_missing_features(df: pd.DataFrame) -> List[str]:
    """Check which required features are missing from dataset."""
    required = get_required_features()
    missing = [f for f in required if f not in df.columns]
    return missing


# Validation test cases from SPECIFICATION.md
VALIDATION_CASES = {
    'Ben Simmons': {
        'expected_score': 5,
        'tolerance': 10,
        'reason': 'Near zero self-created jumpers in career'
    },
    'James Harden': {
        'expected_score': 95,
        'tolerance': 10,
        'reason': 'Elite stepback, can get any shot anytime'
    },
    'Luka Dončić': {
        'expected_score': 95,
        'tolerance': 10,
        'reason': 'Maximum creation, holds ball 6+ seconds'
    },
    'Khris Middleton': {
        'expected_score': 70,
        'tolerance': 15,
        'reason': 'Good mid-range creation, not elite volume'
    },
}


def validate_component(df: pd.DataFrame) -> Dict[str, dict]:
    """
    Validate component against known test cases.
    
    Returns:
        Dict mapping player names to pass/fail results
    """
    results = {}
    
    for player, case in VALIDATION_CASES.items():
        player_mask = df['player_name'].str.lower().str.contains(player.lower())
        
        if not player_mask.any():
            results[player] = {
                'status': 'SKIP',
                'reason': 'Player not in dataset'
            }
            continue
        
        # Get most recent season
        player_df = df[player_mask].sort_values('season', ascending=False)
        player_data = player_df.iloc[0]
        
        score = calculate_self_created_score(player_data)
        expected = case['expected_score']
        tolerance = case['tolerance']
        
        if abs(score - expected) <= tolerance:
            results[player] = {
                'status': 'PASS',
                'score': score,
                'expected': expected
            }
        else:
            results[player] = {
                'status': 'FAIL',
                'score': score,
                'expected': expected,
                'delta': score - expected
            }
    
    return results


if __name__ == '__main__':
    # Quick test with synthetic data
    test_data = pd.Series({
        'creation_volume_ratio': 0.6,
        'ISO_POSS_RS': 5.0,
        'FGA_3_DRIBBLE': 3.0,
        'FGA_7_DRIBBLE': 2.0,
        'FGA_ISO_TOTAL': 5.0,
        'EFG_ISO_WEIGHTED': 0.48,
        'time_of_poss': 5.5
    })
    
    score = calculate_self_created_score(test_data)
    print(f"Test Score: {score}")
    print(f"Expected range: 60-80 for solid creator")

