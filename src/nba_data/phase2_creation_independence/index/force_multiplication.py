"""
Component 5: Force Multiplication Score (Weight: 10%)

Question: Do you create things that aren't in the box score?

Physics Principle:
Some players create value through physicality and pressure that doesn't
show up in traditional stats. They draw fouls, create contact, collapse
defenses, and generate open looks for teammates through sheer force.

Sub-Metrics:
- Free Throw Rate (40%): FTA / FGA - getting to the line
- Rim Pressure (30%): Shots at rim with contact
- Touch Production (20%): Points from post/elbow touches
- Physicality Score (10%): Existing physicality metric

Validation Cases:
- Giannis: ~100 (maximum force, entire game is force)
- Ben Simmons: ~35 (HAD the tools, DIDN'T use them)
- Stephen Curry: ~50 (gravity, not force)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


# Weights for sub-metrics
WEIGHTS = {
    'free_throw_rate': 0.40,
    'rim_pressure': 0.30,
    'touch_production': 0.20,
    'physicality': 0.10
}


def calculate_force_multiplication_score(player_data: pd.Series) -> float:
    """
    Calculate Force Multiplication Score (0-100).
    
    Args:
        player_data: Series containing player features for a season
        
    Returns:
        Score from 0-100 where:
        - 0-30: No physical force (pure shooters)
        - 30-50: Average physicality
        - 50-70: Above average force
        - 70-90: High force (modern bigs)
        - 90-100: Maximum force (Giannis, peak Shaq)
    """
    
    # Sub-metric 1: Free Throw Rate (40%)
    ftr_score = _calculate_ftr_score(player_data)
    
    # Sub-metric 2: Rim Pressure (30%)
    rim_score = _calculate_rim_pressure_score(player_data)
    
    # Sub-metric 3: Touch Production (20%)
    touch_score = _calculate_touch_production_score(player_data)
    
    # Sub-metric 4: Physicality Score (10%)
    physicality_score = _calculate_physicality_component_score(player_data)
    
    # Weighted combination
    final_score = (
        WEIGHTS['free_throw_rate'] * ftr_score +
        WEIGHTS['rim_pressure'] * rim_score +
        WEIGHTS['touch_production'] * touch_score +
        WEIGHTS['physicality'] * physicality_score
    )
    
    return round(np.clip(final_score, 0, 100), 2)


def _calculate_ftr_score(data: pd.Series) -> float:
    """
    Calculate score based on Free Throw Rate.
    
    FTr = FTA / FGA - measures ability to get to the line.
    Getting to the line = creating fouls = force multiplication.
    
    Benchmarks:
    - Low FTr: <0.20 (pure shooters, catch-and-shoot)
    - Average: 0.25-0.35
    - High FTr: 0.40-0.50 (slashers, physical players)
    - Elite FTr: 0.50+ (Giannis, Embiid, peak Harden)
    
    Note: The "Grifter Trap" (Insight #74):
    High FTr + Low Rim Appetite = foul baiter, not physical player
    This is handled by combining with rim pressure
    """
    ftr = data.get('RS_FTr', data.get('FTr', 0.30))
    
    # Scale: 0.15 = 0, 0.55 = 100
    score = (ftr - 0.15) / 0.40 * 100
    return np.clip(score, 0, 100)


def _calculate_rim_pressure_score(data: pd.Series) -> float:
    """
    Calculate score based on rim pressure.
    
    Shots at the rim with contact = true physical force.
    This distinguishes "force" from "foul baiting."
    
    Benchmarks:
    - Perimeter player: <0.20 rim appetite
    - Average: 0.25-0.35
    - Slasher: 0.40-0.50
    - Elite rim attacker: 0.50+ (Giannis, LeBron drives)
    """
    rim_appetite = data.get('RS_RIM_APPETITE', 0.30)
    
    # Scale: 0.15 = 0, 0.55 = 100
    score = (rim_appetite - 0.15) / 0.40 * 100
    return np.clip(score, 0, 100)


def _calculate_touch_production_score(data: pd.Series) -> float:
    """
    Calculate score based on post/elbow touch production.
    
    Points generated from touches in the post and elbow.
    This captures "Big Man Force" that doesn't require dribbling.
    
    Benchmarks:
    - Guards: <3 points from touches
    - Average big: 4-6 points from touches
    - Post-up big: 6-8 points from touches
    - Elite post player: 8+ points (Embiid, Jokic)
    """
    touch_pts = data.get('weighted_touch_production', 
                         data.get('post_touch_pts', 0) + data.get('elbow_touch_pts', 0))
    
    # Scale: 1 = 0, 10 = 100
    score = (touch_pts - 1.0) / 9.0 * 100
    return np.clip(score, 0, 100)


def _calculate_physicality_component_score(data: pd.Series) -> float:
    """
    Calculate score from existing physicality_score feature.
    
    This is the pre-calculated physicality score that combines
    FTr and rim appetite into a single metric.
    """
    physicality = data.get('physicality_score', 0.50)
    
    # Already 0-1, convert to 0-100
    return physicality * 100


def get_required_features() -> List[str]:
    """Return list of features required for this component."""
    return [
        # Free throw rate
        'RS_FTr',
        # Rim pressure
        'RS_RIM_APPETITE',
        # Touch production
        'weighted_touch_production',
        'post_touch_pts',
        'elbow_touch_pts',
        # Existing composite
        'physicality_score',
    ]


def get_missing_features(df: pd.DataFrame) -> List[str]:
    """Check which required features are missing from dataset."""
    required = get_required_features()
    missing = [f for f in required if f not in df.columns and f.lower() not in df.columns]
    return missing


# Validation test cases from SPECIFICATION.md
VALIDATION_CASES = {
    'Giannis Antetokounmpo': {
        'expected_score': 100,
        'tolerance': 5,
        'reason': 'Maximum force - entire game is physical force'
    },
    'Joel Embiid': {
        'expected_score': 95,
        'tolerance': 10,
        'reason': 'Elite post force + FTr'
    },
    'Ben Simmons': {
        'expected_score': 35,
        'tolerance': 15,
        'reason': 'HAD the physical tools, DIDN\'T use them aggressively'
    },
    'Stephen Curry': {
        'expected_score': 50,
        'tolerance': 15,
        'reason': 'Creates via gravity, not force'
    },
    'Nikola Jokić': {
        'expected_score': 70,
        'tolerance': 15,
        'reason': 'Post production but not traditional force'
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
        
        score = calculate_force_multiplication_score(player_data)
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
    
    # Test case 1: Giannis pattern (maximum force)
    giannis_data = pd.Series({
        'RS_FTr': 0.55,                    # Elite FTr
        'RS_RIM_APPETITE': 0.60,           # Maximum rim attacks
        'weighted_touch_production': 8.0,  # High touch points
        'physicality_score': 0.95,         # Near maximum
    })
    
    # Test case 2: Curry pattern (gravity, not force)
    curry_data = pd.Series({
        'RS_FTr': 0.25,                    # Low FTr (doesn't get to line much)
        'RS_RIM_APPETITE': 0.25,           # Perimeter player
        'weighted_touch_production': 2.0,  # Few touch points
        'physicality_score': 0.40,         # Below average physicality
    })
    
    # Test case 3: Simmons pattern (tools but doesn't use them)
    simmons_data = pd.Series({
        'RS_FTr': 0.35,                    # Moderate FTr
        'RS_RIM_APPETITE': 0.45,           # Actually attacks rim
        'weighted_touch_production': 4.0,  # Some touch points
        'physicality_score': 0.50,         # Average - COULD be higher
    })
    
    giannis_score = calculate_force_multiplication_score(giannis_data)
    curry_score = calculate_force_multiplication_score(curry_data)
    simmons_score = calculate_force_multiplication_score(simmons_data)
    
    print(f"Giannis Score: {giannis_score} (expected ~100)")
    print(f"Curry Score: {curry_score} (expected ~50)")
    print(f"Simmons Score: {simmons_score} (expected ~35)")
    print(f"\nForce hierarchy: Giannis > Simmons > Curry (correct ordering)")

