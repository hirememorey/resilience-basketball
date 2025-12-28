"""
Component 2: Pressure Appetite Score (Weight: 25%)

Question: When the game matters, do you WANT the ball?

Physics Principle:
True stars don't just maintain under pressure - they SEEK responsibility.
The key insight from KEY_INSIGHTS.md #79:
- Deltas lose baseline information
- A player going 40%→35% usage is different than 15%→10%
- We need ABSOLUTE clutch usage, not just the delta

Sub-Metrics:
- Clutch Usage Absolute (50%): What is the actual clutch usage?
- Relative Usage Change (30%): Does usage go up or down in clutch?
- Playoff Appetite (20%): Does usage increase in playoffs?

Validation Cases:
- Ben Simmons: ~20 (usage DROPS under pressure)
- Luka Dončić: ~95 (usage INCREASES under pressure)
- James Harden: ~85 (historically clutch, go-to scorer)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


# Weights for sub-metrics
WEIGHTS = {
    'clutch_usage_absolute': 0.50,
    'relative_usage_change': 0.30,
    'playoff_appetite': 0.20
}


def calculate_pressure_appetite_score(player_data: pd.Series) -> float:
    """
    Calculate Pressure Appetite Score (0-100).
    
    Args:
        player_data: Series containing player features for a season
        
    Returns:
        Score from 0-100 where:
        - 0-20: Hiding under pressure (Simmons)
        - 20-40: Role player in clutch
        - 40-60: Maintains responsibility
        - 60-80: Steps up under pressure
        - 80-100: Demands the ball in clutch (Luka, Harden)
    """
    
    # Sub-metric 1: Clutch Usage Absolute (50%)
    clutch_score = _calculate_clutch_absolute_score(player_data)
    
    # Sub-metric 2: Relative Usage Change (30%)
    appetite_score = _calculate_relative_change_score(player_data)
    
    # Sub-metric 3: Playoff Appetite (20%)
    playoff_score = _calculate_playoff_appetite_score(player_data)
    
    # Weighted combination
    final_score = (
        WEIGHTS['clutch_usage_absolute'] * clutch_score +
        WEIGHTS['relative_usage_change'] * appetite_score +
        WEIGHTS['playoff_appetite'] * playoff_score
    )
    
    return round(np.clip(final_score, 0, 100), 2)


def _calculate_clutch_absolute_score(data: pd.Series) -> float:
    """
    Calculate score based on ABSOLUTE clutch usage.
    
    This directly answers: "Does this player want the ball in crunch time?"
    
    Key Insight (Insight #79):
    - Simmons at 14.8% clutch usage = role player behavior
    - Luka at 27.6% clutch usage = go-to option behavior
    - The ABSOLUTE number matters, not just the change
    
    Benchmarks:
    - Role player: <15% clutch usage
    - Secondary option: 15-22% clutch usage
    - Primary option: 22-30% clutch usage
    - Elite closer: 30%+ clutch usage
    """
    # Primary feature: CLUTCH_USG_ABSOLUTE (already calculated)
    clutch_usg = data.get('CLUTCH_USG_ABSOLUTE', data.get('clutch_usg_absolute', None))
    
    if clutch_usg is None:
        # Fallback: calculate from base usage + delta
        base_usg = data.get('USG_PCT', data.get('usg_pct', 0.20))
        delta = data.get('LEVERAGE_USG_DELTA', data.get('leverage_usg_delta', 0))
        clutch_usg = base_usg + delta
    
    # Scale: 12% = 0, 32%+ = 100
    # This maps role player (12%) to 0 and elite closer (32%) to 100
    score = (clutch_usg - 0.12) / 0.20 * 100
    return np.clip(score, 0, 100)


def _calculate_relative_change_score(data: pd.Series) -> float:
    """
    Calculate score based on PROPORTIONAL usage change.
    
    Key Insight (Insight #79):
    - A 7% drop from 35% is different than 7% from 21%
    - Simmons: -31% relative drop (hiding)
    - Luka: +5% relative increase (stepping up)
    
    Positive change = stepping UP under pressure (good)
    Negative change = hiding under pressure (bad - the Simmons pattern)
    """
    # Primary feature: RELATIVE_USAGE_DROP
    relative_drop = data.get('RELATIVE_USAGE_DROP', data.get('relative_usage_drop', None))
    
    if relative_drop is None:
        # Calculate from raw values
        base_usg = data.get('USG_PCT', data.get('usg_pct', 0.20))
        delta = data.get('LEVERAGE_USG_DELTA', data.get('leverage_usg_delta', 0))
        
        if base_usg > 0.05:
            relative_drop = delta / base_usg
        else:
            relative_drop = 0
    
    # Map: -30% relative drop = 0, 0% = 50, +20% relative increase = 100
    # Simmons (-31%) → 0
    # Stable player (0%) → 50  
    # Luka (+5%) → 62.5
    score = 50 + (relative_drop * 166.67)  # Scale so -0.30 = 0, +0.30 = 100
    return np.clip(score, 0, 100)


def _calculate_playoff_appetite_score(data: pd.Series) -> float:
    """
    Calculate score based on playoff usage vs regular season.
    
    Players who embrace playoff pressure have higher usage in playoffs.
    This is a longer-term version of the clutch metric.
    """
    # Playoff usage (may not be available for all players)
    playoff_usg = data.get('PLAYOFF_USG_PCT', None)
    rs_usg = data.get('USG_PCT', data.get('usg_pct', 0.20))
    
    if playoff_usg is None:
        # No playoff data - use neutral score
        # Don't penalize players who haven't been in playoffs
        return 50.0
    
    if rs_usg > 0.05:
        playoff_bump = (playoff_usg - rs_usg) / rs_usg
    else:
        playoff_bump = 0
    
    # Map: -15% relative drop = 25, 0% = 50, +15% increase = 75
    score = 50 + (playoff_bump * 166.67)
    return np.clip(score, 0, 100)


def get_required_features() -> List[str]:
    """Return list of features required for this component."""
    return [
        # Primary features (should exist)
        'CLUTCH_USG_ABSOLUTE',
        'RELATIVE_USAGE_DROP',
        'LEVERAGE_USG_DELTA',
        'USG_PCT',
        # Optional features
        'PLAYOFF_USG_PCT',          # May not exist for all players
    ]


def get_missing_features(df: pd.DataFrame) -> List[str]:
    """Check which required features are missing from dataset."""
    required = get_required_features()
    missing = [f for f in required if f not in df.columns and f.lower() not in df.columns]
    return missing


# Validation test cases from SPECIFICATION.md
VALIDATION_CASES = {
    'Ben Simmons': {
        'expected_score': 20,
        'tolerance': 15,
        'reason': 'Usage DROPS massively under pressure (abdication)'
    },
    'Luka Dončić': {
        'expected_score': 95,
        'tolerance': 10,
        'reason': 'Usage INCREASES under pressure, demands the ball'
    },
    'James Harden': {
        'expected_score': 85,
        'tolerance': 10,
        'reason': 'Historically clutch, go-to scorer in Houston years'
    },
    'Karl-Anthony Towns': {
        'expected_score': 45,
        'tolerance': 20,
        'reason': 'Takes shots but efficiency drops (chokes, not abdicates)'
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
        
        score = calculate_pressure_appetite_score(player_data)
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
    
    # Test case 1: Ben Simmons pattern (hiding)
    simmons_data = pd.Series({
        'USG_PCT': 0.214,
        'LEVERAGE_USG_DELTA': -0.066,  # -6.6% absolute drop
        'CLUTCH_USG_ABSOLUTE': 0.148,  # Only 14.8% clutch usage
        'RELATIVE_USAGE_DROP': -0.31,  # -31% relative drop
    })
    
    # Test case 2: Luka pattern (stepping up)
    luka_data = pd.Series({
        'USG_PCT': 0.355,
        'LEVERAGE_USG_DELTA': -0.079,  # Small absolute drop
        'CLUTCH_USG_ABSOLUTE': 0.276,  # Still 27.6% clutch usage!
        'RELATIVE_USAGE_DROP': -0.22,  # Only -22% relative
    })
    
    simmons_score = calculate_pressure_appetite_score(simmons_data)
    luka_score = calculate_pressure_appetite_score(luka_data)
    
    print(f"Simmons Score: {simmons_score} (expected ~20)")
    print(f"Luka Score: {luka_score} (expected ~80+)")
    print(f"Gap: {luka_score - simmons_score} (should be large)")

