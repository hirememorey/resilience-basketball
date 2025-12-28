"""
Component 3: Shot Difficulty Embrace Score (Weight: 20%)

Question: Are you willing to take HARD shots, or only easy ones?

Physics Principle:
Creators must be willing to take difficult shots when the defense denies easy ones.
Players who only take layups and dunks (Simmons) are exposed when those are taken away.
Players who embrace mid-range, pull-ups, and contested shots have more options.

Sub-Metrics:
- Contested Shot Rate (35%): % of shots with defender < 4 feet
- Mid-Range Volume (25%): Mid-range FGA per game
- Pull-up 3PT Rate (25%): Pull-up 3s / Total 3s
- Average Shot Difficulty (15%): Composite from time of possession

Validation Cases:
- Ben Simmons: ~10 (only takes layups/dunks, never difficult shots)
- Jayson Tatum: ~85 (takes tough fadeaways routinely)
- Khris Middleton: ~80 (elite mid-range game)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


# Weights for sub-metrics
WEIGHTS = {
    'contested_rate': 0.35,
    'midrange_volume': 0.25,
    'pullup_3pt_rate': 0.25,
    'shot_difficulty': 0.15
}


def calculate_difficulty_embrace_score(player_data: pd.Series) -> float:
    """
    Calculate Shot Difficulty Embrace Score (0-100).
    
    Args:
        player_data: Series containing player features for a season
        
    Returns:
        Score from 0-100 where:
        - 0-20: Only takes easy shots (Simmons)
        - 20-40: Limited shot difficulty
        - 40-60: Average shot difficulty
        - 60-80: Embraces difficult shots
        - 80-100: Takes the hardest shots (Tatum, DeRozan)
    """
    
    # Sub-metric 1: Contested Shot Rate (35%)
    contested_score = _calculate_contested_score(player_data)
    
    # Sub-metric 2: Mid-Range Volume (25%)
    midrange_score = _calculate_midrange_score(player_data)
    
    # Sub-metric 3: Pull-up 3PT Rate (25%)
    pullup_score = _calculate_pullup_3pt_score(player_data)
    
    # Sub-metric 4: Time-based difficulty proxy (15%)
    difficulty_score = _calculate_time_difficulty_score(player_data)
    
    # Weighted combination
    final_score = (
        WEIGHTS['contested_rate'] * contested_score +
        WEIGHTS['midrange_volume'] * midrange_score +
        WEIGHTS['pullup_3pt_rate'] * pullup_score +
        WEIGHTS['shot_difficulty'] * difficulty_score
    )
    
    return round(np.clip(final_score, 0, 100), 2)


def _calculate_contested_score(data: pd.Series) -> float:
    """
    Calculate score based on contested shot rate.
    
    Shots with defender 0-4 feet are considered "contested."
    Higher contested rate = willingness to take difficult shots.
    
    Benchmarks:
    - Easy shot hunters: <40% contested
    - Average: 50% contested
    - Difficulty embracers: 65%+ contested
    """
    # Primary: CONTESTED_SHOT_RATE (needs collection)
    contested_rate = data.get('CONTESTED_SHOT_RATE', None)
    
    if contested_rate is None:
        # Fallback: use inverse of open shot frequency
        open_freq = data.get('RS_OPEN_SHOT_FREQUENCY', 0.50)
        contested_rate = 1.0 - open_freq
    
    # Scale: 35% = 0, 70%+ = 100
    score = (contested_rate - 0.35) / 0.35 * 100
    return np.clip(score, 0, 100)


def _calculate_midrange_score(data: pd.Series) -> float:
    """
    Calculate score based on mid-range volume.
    
    Mid-range shots are analytically "inefficient" but demonstrate
    shot creation ability. Elite mid-range scorers have more options
    when the paint and 3pt line are taken away.
    
    Benchmarks:
    - Modern efficiency player: <1 mid-range per game
    - Average: 2-3 per game
    - Mid-range specialist: 5+ per game (DeRozan, Kawhi)
    """
    # Primary: MIDRANGE_FGA_PER_GAME (needs calculation from shot charts)
    midrange_fga = data.get('MIDRANGE_FGA_PER_GAME', None)
    
    if midrange_fga is None:
        # Fallback: use creation volume as proxy
        # Players who create tend to have more mid-range
        cvr = data.get('creation_volume_ratio', 
                       data.get('CREATION_VOLUME_RATIO', 0.4))
        # Higher CVR suggests more self-created shots, often mid-range
        midrange_fga = cvr * 6.0  # Scale to reasonable range
    
    # Scale: 0.5 = 0, 5+ = 100
    score = (midrange_fga - 0.5) / 4.5 * 100
    return np.clip(score, 0, 100)


def _calculate_pullup_3pt_score(data: pd.Series) -> float:
    """
    Calculate score based on pull-up 3PT rate.
    
    Pull-up 3s are harder than catch-and-shoot 3s.
    Higher pull-up rate indicates shot creation ability.
    
    Benchmarks:
    - Catch-and-shoot specialist: <20% pull-up
    - Average: 30-40% pull-up
    - Pull-up specialist: 60%+ pull-up (Curry, Lillard, Tatum)
    """
    # Primary: PULLUP_3PT_RATE (needs calculation)
    pullup_rate = data.get('PULLUP_3PT_RATE', None)
    
    if pullup_rate is None:
        # Fallback: use 3+ dribble volume vs 0-dribble volume
        fga_3_dribble = data.get('FGA_3_DRIBBLE', 0) + data.get('FGA_7_DRIBBLE', 0)
        fga_0_dribble = data.get('FGA_0_DRIBBLE', 1)
        
        total = fga_3_dribble + fga_0_dribble
        if total > 0:
            pullup_rate = fga_3_dribble / total
        else:
            pullup_rate = 0.30  # Default
    
    # Scale: 15% = 0, 60%+ = 100
    score = (pullup_rate - 0.15) / 0.45 * 100
    return np.clip(score, 0, 100)


def _calculate_time_difficulty_score(data: pd.Series) -> float:
    """
    Calculate score based on time of possession.
    
    Longer possessions → harder shots (defense is set, more dribbles).
    This is a good proxy for overall shot difficulty.
    
    Benchmarks:
    - Catch-and-shoot: <2 seconds
    - Average: 3-4 seconds
    - ISO player: 5-6 seconds
    - Elite creator: 6+ seconds (Harden, Luka)
    """
    time_of_poss = data.get('time_of_poss', 3.0)
    
    # Scale: 2 sec = 0, 7+ sec = 100
    score = (time_of_poss - 2.0) / 5.0 * 100
    return np.clip(score, 0, 100)


def get_required_features() -> List[str]:
    """Return list of features required for this component."""
    return [
        # Primary features (need collection)
        'CONTESTED_SHOT_RATE',      # From CloseDefDistRange
        'MIDRANGE_FGA_PER_GAME',    # From shot charts
        'PULLUP_3PT_RATE',          # From shooting splits
        # Fallback features (should exist)
        'RS_OPEN_SHOT_FREQUENCY',
        'FGA_3_DRIBBLE',
        'FGA_7_DRIBBLE',
        'FGA_0_DRIBBLE',
        'creation_volume_ratio',
        'time_of_poss',
    ]


def get_missing_features(df: pd.DataFrame) -> List[str]:
    """Check which required features are missing from dataset."""
    required = get_required_features()
    missing = [f for f in required if f not in df.columns and f.lower() not in df.columns]
    return missing


# Validation test cases from SPECIFICATION.md
VALIDATION_CASES = {
    'Ben Simmons': {
        'expected_score': 10,
        'tolerance': 10,
        'reason': 'Only takes layups/dunks, never embraces difficulty'
    },
    'Jayson Tatum': {
        'expected_score': 85,
        'tolerance': 10,
        'reason': 'Takes tough fadeaways, step-backs, contested shots'
    },
    'Khris Middleton': {
        'expected_score': 80,
        'tolerance': 10,
        'reason': 'Elite mid-range game, difficult shot maker'
    },
    'DeMar DeRozan': {
        'expected_score': 90,
        'tolerance': 10,
        'reason': 'Mid-range master, embraces the hardest shots'
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
        
        score = calculate_difficulty_embrace_score(player_data)
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
    
    # Test case 1: Ben Simmons pattern (easy shots only)
    simmons_data = pd.Series({
        'RS_OPEN_SHOT_FREQUENCY': 0.70,  # Mostly open (easy) shots
        'creation_volume_ratio': 0.15,    # Very low creation
        'FGA_3_DRIBBLE': 0.1,
        'FGA_7_DRIBBLE': 0.0,
        'FGA_0_DRIBBLE': 5.0,
        'time_of_poss': 2.0,  # Very short time
    })
    
    # Test case 2: Tatum pattern (embraces difficulty)
    tatum_data = pd.Series({
        'RS_OPEN_SHOT_FREQUENCY': 0.40,  # Takes contested shots
        'creation_volume_ratio': 0.55,
        'FGA_3_DRIBBLE': 3.0,
        'FGA_7_DRIBBLE': 1.5,
        'FGA_0_DRIBBLE': 2.5,
        'time_of_poss': 5.5,  # Longer possessions
    })
    
    simmons_score = calculate_difficulty_embrace_score(simmons_data)
    tatum_score = calculate_difficulty_embrace_score(tatum_data)
    
    print(f"Simmons Score: {simmons_score} (expected ~10)")
    print(f"Tatum Score: {tatum_score} (expected ~85)")
    print(f"Gap: {tatum_score - simmons_score} (should be large)")

