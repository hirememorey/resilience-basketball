"""
Composite Creation Independence Index (CII) Calculator

Combines all five components into a single score.

The CII measures a player's ability to create offense when the defense knows it's coming.
This is the difference between "IS the situation" vs "NEEDS the situation."

Formula:
    CII = 0.30 × Self_Created_Shot_Score
        + 0.25 × Pressure_Appetite_Score
        + 0.20 × Shot_Difficulty_Score
        + 0.15 × Defensive_Survival_Score
        + 0.10 × Force_Score

Each component is normalized to 0-100 scale.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

# Import component calculators
from .self_created import calculate_self_created_score
from .pressure_appetite import calculate_pressure_appetite_score
from .difficulty_embrace import calculate_difficulty_embrace_score
from .defensive_survival import calculate_defensive_survival_score
from .force_multiplication import calculate_force_multiplication_score

logger = logging.getLogger(__name__)

# Component weights (from SPECIFICATION.md)
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
        player_data: Series containing player features for a single season
        component_scores: Optional pre-calculated component scores (for testing)
        
    Returns:
        Dictionary containing:
        - 'cii': The composite Creation Independence Index (0-100)
        - 'components': Individual component scores
        - 'archetype': Predicted archetype based on CII
        - 'confidence': Confidence level based on data completeness
    """
    
    # If component scores not provided, calculate them
    if component_scores is None:
        component_scores = {
            'self_created': calculate_self_created_score(player_data),
            'pressure_appetite': calculate_pressure_appetite_score(player_data),
            'difficulty_embrace': calculate_difficulty_embrace_score(player_data),
            'defensive_survival': calculate_defensive_survival_score(player_data),
            'force_multiplication': calculate_force_multiplication_score(player_data)
        }
    
    # Calculate weighted CII
    cii = sum(
        component_scores[component] * weight 
        for component, weight in WEIGHTS.items()
    )
    
    # Clamp to valid range
    cii = np.clip(cii, 0, 100)
    
    # Determine archetype
    archetype = _determine_archetype(cii)
    
    # Calculate confidence based on data completeness
    confidence = _calculate_confidence(player_data)
    
    return {
        'cii': round(cii, 2),
        'components': component_scores,
        'archetype': archetype,
        'confidence': confidence
    }


def _calculate_confidence(data: pd.Series) -> str:
    """
    Calculate confidence level based on data completeness.
    
    Returns:
        'High', 'Medium', or 'Low' confidence
    """
    # Key features that should be present for high confidence
    high_confidence_features = [
        'CLUTCH_USG_ABSOLUTE',
        'RELATIVE_USAGE_DROP', 
        'creation_volume_ratio',
        'FRAGILITY_SCORE',
        'time_of_poss'
    ]
    
    present = sum(1 for f in high_confidence_features 
                  if f in data.index or f.lower() in data.index)
    
    if present >= 4:
        return 'High'
    elif present >= 2:
        return 'Medium'
    else:
        return 'Low'


def _determine_archetype(cii: float) -> str:
    """
    Map CII score to archetype.
    
    Thresholds from SPECIFICATION.md:
    
    | CII Range | Archetype         | Description                           |
    |-----------|-------------------|---------------------------------------|
    | 80+       | Franchise Engine  | Can be #1 on a championship team     |
    | 70-80     | Strong Creator    | High creation, optimal as #2         |
    | 55-70     | Luxury Amplifier  | Excellent, needs an Engine           |
    | 40-55     | Fragile Star      | Looks like Engine, fatal flaws       |
    | <40       | Role Player       | Solid contributor, not a star        |
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
        df: DataFrame with player features (one row per player-season)
        
    Returns:
        DataFrame with CII scores and archetypes added:
        - player_name, season, cii, archetype, confidence
        - cii_self_created, cii_pressure_appetite, etc.
    """
    logger.info(f"Calculating CII for {len(df)} player-seasons...")
    
    results = []
    
    for idx, row in df.iterrows():
        try:
            cii_result = calculate_cii(row)
            results.append({
                'player_name': row.get('player_name', row.get('PLAYER_NAME', '')),
                'season': row.get('season', row.get('SEASON', '')),
                'cii': cii_result['cii'],
                'archetype': cii_result['archetype'],
                'confidence': cii_result['confidence'],
                **{f'cii_{k}': v for k, v in cii_result['components'].items()}
            })
        except Exception as e:
            logger.warning(f"Error calculating CII for index {idx}: {e}")
            results.append({
                'player_name': row.get('player_name', row.get('PLAYER_NAME', '')),
                'season': row.get('season', row.get('SEASON', '')),
                'cii': np.nan,
                'archetype': 'Error',
                'confidence': 'Low'
            })
    
    result_df = pd.DataFrame(results)
    
    # Log summary statistics
    if not result_df.empty:
        valid_scores = result_df['cii'].dropna()
        logger.info(f"  -> CII calculated. Mean: {valid_scores.mean():.2f}, Median: {valid_scores.median():.2f}")
        logger.info(f"  -> Archetype distribution:")
        for archetype, count in result_df['archetype'].value_counts().items():
            logger.info(f"      {archetype}: {count}")
    
    return result_df


def validate_cii(df: pd.DataFrame) -> Dict[str, dict]:
    """
    Validate CII calculations against critical test cases.
    
    Returns:
        Dictionary of pass/fail results for each test case
    """
    from .self_created import VALIDATION_CASES as SELF_CASES
    from .pressure_appetite import VALIDATION_CASES as PRESSURE_CASES
    from .difficulty_embrace import VALIDATION_CASES as DIFFICULTY_CASES
    from .defensive_survival import VALIDATION_CASES as DEFENSE_CASES
    from .force_multiplication import VALIDATION_CASES as FORCE_CASES
    
    # Critical CII test cases from SPECIFICATION.md
    CRITICAL_CASES = {
        'Ben Simmons': {'expected_archetype': 'Fragile Star', 'max_cii': 40},
        'James Harden': {'expected_archetype': 'Franchise Engine', 'min_cii': 80},
        'Luka Dončić': {'expected_archetype': 'Franchise Engine', 'min_cii': 85},
        'Tyrese Haliburton': {'expected_archetype': 'Strong Creator', 'min_cii': 70},
        'Domantas Sabonis': {'expected_archetype': 'Luxury Amplifier', 'max_cii': 65},
    }
    
    # Calculate CII for all players
    cii_results = batch_calculate_cii(df)
    
    results = {}
    for player, case in CRITICAL_CASES.items():
        player_mask = cii_results['player_name'].str.lower().str.contains(player.lower())
        
        if not player_mask.any():
            results[player] = {'status': 'SKIP', 'reason': 'Not in dataset'}
            continue
        
        player_df = cii_results[player_mask].sort_values('season', ascending=False)
        player_cii = player_df.iloc[0]
        
        # Check archetype
        archetype_match = player_cii['archetype'] == case['expected_archetype']
        
        # Check CII bounds
        cii_valid = True
        if 'min_cii' in case and player_cii['cii'] < case['min_cii']:
            cii_valid = False
        if 'max_cii' in case and player_cii['cii'] > case['max_cii']:
            cii_valid = False
        
        if archetype_match and cii_valid:
            results[player] = {
                'status': 'PASS',
                'cii': player_cii['cii'],
                'archetype': player_cii['archetype']
            }
        else:
            results[player] = {
                'status': 'FAIL',
                'cii': player_cii['cii'],
                'archetype': player_cii['archetype'],
                'expected': case
            }
    
    # Print summary
    passed = sum(1 for r in results.values() if r['status'] == 'PASS')
    failed = sum(1 for r in results.values() if r['status'] == 'FAIL')
    skipped = sum(1 for r in results.values() if r['status'] == 'SKIP')
    
    logger.info(f"\nValidation Results: {passed} passed, {failed} failed, {skipped} skipped")
    
    return results


if __name__ == '__main__':
    # Quick integration test
    import pandas as pd
    
    # Test with synthetic player data
    test_players = pd.DataFrame([
        {
            'player_name': 'Test Engine',
            'season': '2023-24',
            'creation_volume_ratio': 0.7,
            'CLUTCH_USG_ABSOLUTE': 0.32,
            'RELATIVE_USAGE_DROP': 0.05,
            'time_of_poss': 6.5,
            'FRAGILITY_SCORE': 0.15,
            'physicality_score': 0.70
        },
        {
            'player_name': 'Test Fragile',
            'season': '2023-24',
            'creation_volume_ratio': 0.2,
            'CLUTCH_USG_ABSOLUTE': 0.14,
            'RELATIVE_USAGE_DROP': -0.30,
            'time_of_poss': 2.5,
            'FRAGILITY_SCORE': 0.85,
            'physicality_score': 0.40
        }
    ])
    
    results = batch_calculate_cii(test_players)
    print("\nTest Results:")
    print(results[['player_name', 'cii', 'archetype', 'confidence']])

