"""
Composite Creation Independence Index (CII) Calculator

Combines all five components into a single score.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional

# Component weights
WEIGHTS = {
    'self_created': 0.30,
    'pressure_appetite': 0.25,
    'difficulty_embrace': 0.20,
    'defensive_survival': 0.15,
    'force_multiplication': 0.10
}

def calculate_cii(
    player_data: pd.Series,
    component_scores: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Calculate the Creation Independence Index for a player.
    
    Args:
        player_data: Series containing player features
        component_scores: Optional pre-calculated component scores
        
    Returns:
        Dictionary containing:
        - 'cii': The composite Creation Independence Index (0-100)
        - 'components': Individual component scores
        - 'archetype': Predicted archetype based on CII
    """
    
    # If component scores not provided, calculate them
    if component_scores is None:
        component_scores = {
            'self_created': _calculate_self_created_score(player_data),
            'pressure_appetite': _calculate_pressure_appetite_score(player_data),
            'difficulty_embrace': _calculate_difficulty_embrace_score(player_data),
            'defensive_survival': _calculate_defensive_survival_score(player_data),
            'force_multiplication': _calculate_force_score(player_data)
        }
    
    # Calculate weighted CII
    cii = sum(
        component_scores[component] * weight 
        for component, weight in WEIGHTS.items()
    )
    
    # Determine archetype
    archetype = _determine_archetype(cii)
    
    return {
        'cii': round(cii, 2),
        'components': component_scores,
        'archetype': archetype
    }


def _calculate_self_created_score(data: pd.Series) -> float:
    """
    Component 1: Self-Created Shot Score
    
    Measures ability to generate quality shots without plays being run.
    
    TODO: Implement with actual data
    - % of FGA unassisted
    - ISO + Pull-up volume and efficiency
    - Stepback/fadeaway availability
    """
    # Placeholder - use creation_volume_ratio as proxy
    cvr = data.get('creation_volume_ratio', 0.5)
    return min(cvr * 100, 100)


def _calculate_pressure_appetite_score(data: pd.Series) -> float:
    """
    Component 2: Pressure Appetite Score
    
    Measures willingness to take responsibility in high-leverage situations.
    
    Uses existing features:
    - clutch_usg_absolute
    - relative_usage_drop
    """
    clutch_usg = data.get('clutch_usg_absolute', 0.2)
    rel_drop = data.get('relative_usage_drop', 0)
    
    # Higher clutch usage = better (0-40% range → 0-100 scale)
    clutch_score = min(clutch_usg / 0.35 * 100, 100)
    
    # Positive relative change (stepping UP) = bonus
    # Negative relative change (hiding) = penalty
    appetite_modifier = 50 + (rel_drop * 100)  # -0.5 to +0.5 → 0 to 100
    appetite_modifier = np.clip(appetite_modifier, 0, 100)
    
    return (clutch_score * 0.6) + (appetite_modifier * 0.4)


def _calculate_difficulty_embrace_score(data: pd.Series) -> float:
    """
    Component 3: Shot Difficulty Embrace Score
    
    Measures willingness to take hard shots (not just layups/dunks).
    
    TODO: Implement with actual data
    - % of shots contested
    - Mid-range volume
    - Pull-up 3PT rate
    """
    # Placeholder - use time_of_poss as proxy (longer possessions = harder shots)
    top = data.get('time_of_poss', 3.0)
    return min(top / 8.0 * 100, 100)


def _calculate_defensive_survival_score(data: pd.Series) -> float:
    """
    Component 4: Defensive Attention Survival Score
    
    Measures ability to maintain production against elite defenses.
    
    TODO: Implement with actual data
    - Efficiency vs Top 10 defenses
    - Playoff vs RS efficiency
    """
    # Placeholder - use fragility_score inverted
    fragility = data.get('fragility_score', 0.5)
    return (1 - fragility) * 100


def _calculate_force_score(data: pd.Series) -> float:
    """
    Component 5: Force Multiplication Score
    
    Measures ability to create through physicality and pressure.
    
    Uses existing features:
    - physicality_score
    - Free throw rate (from underlying data)
    """
    physicality = data.get('physicality_score', 0.5)
    return physicality * 100


def _determine_archetype(cii: float) -> str:
    """
    Map CII score to archetype.
    
    | CII Range | Archetype |
    |-----------|-----------|
    | 80+       | Franchise Engine |
    | 70-80     | Strong Creator |
    | 55-70     | Luxury Amplifier |
    | 40-55     | Fragile Star |
    | <40       | Role Player |
    """
    if cii >= 80:
        return "Franchise Engine"
    elif cii >= 70:
        return "Strong Creator"
    elif cii >= 55:
        return "Luxury Amplifier"
    elif cii >= 40:
        return "Fragile Star"
    else:
        return "Role Player"


def batch_calculate_cii(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate CII for all players in a DataFrame.
    
    Args:
        df: DataFrame with player features
        
    Returns:
        DataFrame with CII scores and archetypes added
    """
    results = []
    
    for idx, row in df.iterrows():
        cii_result = calculate_cii(row)
        results.append({
            'player_name': row.get('player_name', ''),
            'season': row.get('season', ''),
            'cii': cii_result['cii'],
            'archetype': cii_result['archetype'],
            **{f'cii_{k}': v for k, v in cii_result['components'].items()}
        })
    
    return pd.DataFrame(results)

