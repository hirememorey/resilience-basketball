"""
Creation Independence Index (CII) Component Calculators

This package contains the five components of the CII:
1. Self-Created Shot Score (30%) - Can you get a shot without a play?
2. Pressure Appetite Score (25%) - Do you WANT the ball in clutch?
3. Shot Difficulty Embrace (20%) - Do you take hard shots or hide?
4. Defensive Survival Score (15%) - Do you maintain against schemes?
5. Force Multiplication Score (10%) - Do you create through physicality?

Usage:
    from src.nba_data.phase2_creation_independence.index import (
        calculate_cii,
        batch_calculate_cii,
        validate_cii
    )
    
    # Calculate CII for a single player-season
    result = calculate_cii(player_data)
    print(f"CII: {result['cii']}, Archetype: {result['archetype']}")
    
    # Calculate CII for entire dataset
    cii_df = batch_calculate_cii(feature_df)
"""

from .composite import (
    calculate_cii,
    batch_calculate_cii,
    validate_cii,
    WEIGHTS
)

from .self_created import (
    calculate_self_created_score,
    VALIDATION_CASES as SELF_CREATED_VALIDATION
)

from .pressure_appetite import (
    calculate_pressure_appetite_score,
    VALIDATION_CASES as PRESSURE_VALIDATION
)

from .difficulty_embrace import (
    calculate_difficulty_embrace_score,
    VALIDATION_CASES as DIFFICULTY_VALIDATION
)

from .defensive_survival import (
    calculate_defensive_survival_score,
    VALIDATION_CASES as DEFENSE_VALIDATION
)

from .force_multiplication import (
    calculate_force_multiplication_score,
    VALIDATION_CASES as FORCE_VALIDATION
)

__all__ = [
    # Main functions
    'calculate_cii',
    'batch_calculate_cii',
    'validate_cii',
    'WEIGHTS',
    # Component calculators
    'calculate_self_created_score',
    'calculate_pressure_appetite_score', 
    'calculate_difficulty_embrace_score',
    'calculate_defensive_survival_score',
    'calculate_force_multiplication_score',
    # Validation cases
    'SELF_CREATED_VALIDATION',
    'PRESSURE_VALIDATION',
    'DIFFICULTY_VALIDATION',
    'DEFENSE_VALIDATION',
    'FORCE_VALIDATION',
]
