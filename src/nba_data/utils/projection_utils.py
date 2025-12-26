"""
Universal Projection Engine for the "Universal Avatar"

This utility implements the core logic for projecting a player's efficiency 
at different usage levels, incorporating the empirically derived "friction 
coefficients".

Core Principles:
1.  Law of Friction: Efficiency degrades as usage and defensive attention increase.
2.  Resilience Buffer: A player's ability to create high-quality shots 
    (SHOT_QUALITY_GENERATION_DELTA) acts as a buffer against this friction.
3.  Friction Tiers: We apply different friction coefficients based on a player's 
    creator archetype (SQ_DELTA quantiles).
"""

import pandas as pd
import numpy as np
from typing import Dict, Union

# Empirically derived friction coefficients from 'derive_friction_coefficients.py'
# Represents the change in TS% for each 1% increase in USG%.
# Note: These are simplified for this initial implementation. A more robust
# version would use a continuous function or more granular tiers.
FRICTION_COEFFICIENTS = {
    'High SQ Delta (Creators)': -0.007133,
    'Low SQ Delta (Finishers)': 0.007870, # Note: Positive coefficient suggests selection bias, we'll treat as near-zero friction.
    'Mid SQ Delta': 0.000340
}

# Thresholds for defining archetypes based on SHOT_QUALITY_GENERATION_DELTA
# Derived from the 10th and 90th percentiles in the historical analysis.
SQ_DELTA_THRESHOLDS = {
    'low': 0.0635,
    'high': 0.1685
}


def get_player_archetype(shot_quality_generation_delta: float) -> str:
    """
    Categorizes a player into a creator archetype based on their SQ_DELTA.

    Args:
        shot_quality_generation_delta: The player's score.

    Returns:
        The corresponding archetype name.
    """
    if shot_quality_generation_delta >= SQ_DELTA_THRESHOLDS['high']:
        return 'High SQ Delta (Creators)'
    elif shot_quality_generation_delta <= SQ_DELTA_THRESHOLDS['low']:
        return 'Low SQ Delta (Finishers)'
    else:
        return 'Mid SQ Delta'


def project_efficiency(
    base_usg: float,
    base_ts: float,
    shot_quality_generation_delta: float,
    target_usg: float
) -> Dict[str, Union[str, float]]:
    """
    Projects a player's True Shooting % (TS%) at a new target Usage % (USG%).

    Args:
        base_usg: The player's current USG% (e.g., 0.25 for 25%).
        base_ts: The player's current TS% (e.g., 0.60 for 60%).
        shot_quality_generation_delta: The player's creation score.
        target_usg: The target USG% to project to.

    Returns:
        A dictionary containing the projected TS%, the archetype used, and the
        friction coefficient applied.
    """
    if pd.isna(base_usg) or pd.isna(base_ts) or pd.isna(shot_quality_generation_delta):
        return {
            "projected_ts": np.nan,
            "archetype": "Unknown",
            "friction_coefficient": np.nan,
            "delta_usg": np.nan,
            "delta_ts_raw": np.nan
        }

    # 1. Determine the player's creator archetype
    archetype = get_player_archetype(shot_quality_generation_delta)

    # 2. Get the corresponding friction coefficient
    friction_coeff = FRICTION_COEFFICIENTS[archetype]
    
    # Special Handling for "Finishers" where a positive coefficient was found.
    # This is likely selection bias. For projection, it's safer to assume 
    # their efficiency stays flat rather than magically increasing. We'll cap
    # the friction at 0 (no penalty), which is a conservative assumption.
    if archetype == 'Low SQ Delta (Finishers)' and friction_coeff > 0:
        friction_coeff = 0.0

    # 3. Calculate the change in usage
    # The coefficient is per 1% change, so we multiply by 100.
    delta_usg_points = (target_usg - base_usg) * 100

    # 4. Calculate the expected change in True Shooting
    # This is the "Friction Tax"
    delta_ts_raw = friction_coeff * delta_usg_points

    # 5. Apply the tax to the base efficiency
    projected_ts = base_ts + (delta_ts_raw / 100) # Convert back to percentage points

    return {
        "projected_ts": projected_ts,
        "archetype": archetype,
        "friction_coefficient": friction_coeff,
        "delta_usg": target_usg - base_usg,
        "delta_ts_raw": delta_ts_raw
    }

# Example Usage (for demonstration and testing)
if __name__ == '__main__':
    print("--- Universal Projection Engine: Example Cases ---")

    # Case 1: Jalen Brunson (High SQ Delta Creator)
    # Simulating his jump from role player to primary engine in NY.
    brunson_base = {
        'name': 'Jalen Brunson (Pre-NY)',
        'usg': 0.22,
        'ts': 0.58,
        'sq_delta': 0.201 # High creator value from ACTIVE_CONTEXT
    }
    brunson_target_usg = 0.30 # Star-level usage
    
    brunson_projection = project_efficiency(
        brunson_base['usg'],
        brunson_base['ts'],
        brunson_base['sq_delta'],
        brunson_target_usg
    )
    
    print(f"\nProjecting: {brunson_base['name']}")
    print(f"  Base Stats: {brunson_base['usg']*100:.1f}% USG, {brunson_base['ts']*100:.1f}% TS")
    print(f"  Target USG: {brunson_target_usg*100:.1f}%")
    print(f"  Archetype: {brunson_projection['archetype']}")
    print(f"  Friction Coefficient: {brunson_projection['friction_coefficient']:.5f}")
    print(f"  Result -> Projected TS: {brunson_projection['projected_ts']*100:.1f}%")
    
    
    # Case 2: Jordan Poole (Low SQ Delta Finisher)
    # Simulating his transition from beneficiary in GSW to primary in WAS.
    poole_base = {
        'name': 'Jordan Poole (GSW)',
        'usg': 0.27,
        'ts': 0.59,
        'sq_delta': 0.142 # Lower creator value from ACTIVE_CONTEXT
    }
    poole_target_usg = 0.32 # High usage
    
    poole_projection = project_efficiency(
        poole_base['usg'],
        poole_base['ts'],
        poole_base['sq_delta'],
        poole_target_usg
    )

    print(f"\nProjecting: {poole_base['name']}")
    print(f"  Base Stats: {poole_base['usg']*100:.1f}% USG, {poole_base['ts']*100:.1f}% TS")
    print(f"  Target USG: {poole_target_usg*100:.1f}%")
    print(f"  Archetype: {poole_projection['archetype']}")
    print(f"  Friction Coefficient: {poole_projection['friction_coefficient']:.5f}")
    print(f"  Result -> Projected TS: {poole_projection['projected_ts']*100:.1f}%")

    # Note: Poole's SQ Delta (0.142) puts him in the "Mid" category based on our
    # historical quantiles. His real-world collapse was more severe than this
    # model predicts, suggesting a non-linear friction effect or other factors
    # (like the "Schematic Cliff") are at play, which is a key insight for V2.
    # For now, this linear model is the correct first implementation step.
