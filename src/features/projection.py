"""
Universal Projection module for NBA Playoff Resilience Engine.
Projects player features to different usage levels using empirical distributions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def project_features_to_usage(
    player_data: Dict,
    target_usage: float,
    current_usage: float,
    usage_buckets: Optional[Dict] = None
) -> Dict:
    """
    Project player features to different usage level.

    Uses empirical distributions to scale features together,
    solving the "Static Avatar Fallacy".

    Args:
        player_data: Current player data
        target_usage: Target usage % (0.0-1.0)
        current_usage: Current usage % (0.0-1.0)
        usage_buckets: Custom usage buckets (optional)

    Returns:
        Projected feature values at target usage
    """
    if usage_buckets is None:
        # Default empirical buckets based on historical data
        usage_buckets = {
            '15-20%': {'creation_volume_ratio': 0.25, 'leverage_usg_delta': -0.02},
            '20-25%': {'creation_volume_ratio': 0.42, 'leverage_usg_delta': 0.01},
            '25-30%': {'creation_volume_ratio': 0.61, 'leverage_usg_delta': 0.03},
            '30-35%': {'creation_volume_ratio': 0.70, 'leverage_usg_delta': 0.05}
        }

    # Determine source and target buckets
    source_bucket = _get_usage_bucket(current_usage)
    target_bucket = _get_usage_bucket(target_usage)

    if source_bucket == target_bucket:
        # No projection needed
        return player_data.copy()

    # Get empirical values for target bucket
    target_values = usage_buckets.get(target_bucket, {})

    # Project features
    projected_data = player_data.copy()
    projected_data['usg_pct'] = target_usage

    # Scale creation volume ratio
    if 'creation_volume_ratio' in player_data and target_bucket in usage_buckets:
        projected_data['creation_volume_ratio'] = target_values['creation_volume_ratio']

    # Adjust leverage deltas
    if 'leverage_usg_delta' in player_data:
        # Higher usage generally means more stable or positive leverage
        usage_factor = (target_usage - current_usage) * 0.1
        projected_data['leverage_usg_delta'] = player_data['leverage_usg_delta'] + usage_factor

    logger.info(f"Projected {player_data.get('player_name', 'Unknown')} from {current_usage:.1%} to {target_usage:.1%} usage")

    return projected_data


def _get_usage_bucket(usage_pct: float) -> str:
    """Get usage bucket for a given usage percentage."""
    usage_pct = usage_pct * 100  # Convert to percentage

    if usage_pct < 20:
        return '15-20%'
    elif usage_pct < 25:
        return '20-25%'
    elif usage_pct < 30:
        return '25-30%'
    elif usage_pct < 35:
        return '30-35%'
    else:
        return '35%+'