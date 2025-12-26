"""
Universal Projection Utilities

Shared utilities for projecting player features at different usage levels.
Extracted from predict_conditional_archetype.py to avoid code duplication.

This module provides the "Universal Projection" logic that scales features together
using empirical distributions rather than linear scaling.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_empirical_usage_buckets(df_features: pd.DataFrame) -> Dict:
    """
    Calculate empirical bucket medians for universal projection.

    Features must scale together using empirical distributions, not linear scaling.
    This captures the non-linear relationships between usage and creation volume.

    Args:
        df_features: DataFrame with player features including USG_PCT and CREATION_VOLUME_RATIO

    Returns:
        Dict with bucket definitions and medians
    """
    # Define usage buckets (percentage ranges)
    buckets = {
        '20-25%': {'min': 0.20, 'max': 0.25, 'median_creation_vol': None},
        '25-30%': {'min': 0.25, 'max': 0.30, 'median_creation_vol': None},
        '30-35%': {'min': 0.30, 'max': 0.35, 'median_creation_vol': None}
    }

    # Calculate median creation volume for each usage bucket
    for bucket_name, bucket_info in buckets.items():
        bucket_data = df_features[
            (df_features['USG_PCT'] >= bucket_info['min']) &
            (df_features['USG_PCT'] < bucket_info['max']) &
            (df_features['CREATION_VOLUME_RATIO'].notna())
        ]

        if len(bucket_data) > 0:
            bucket_info['median_creation_vol'] = bucket_data['CREATION_VOLUME_RATIO'].median()
            logger.debug(f"{bucket_name}: {len(bucket_data)} players, median creation vol: {bucket_info['median_creation_vol']:.4f}")
        else:
            logger.warning(f"No data for {bucket_name} bucket")

    return buckets


def calculate_feature_percentiles(df_features: pd.DataFrame) -> Dict:
    """
    Calculate percentiles needed for flash multiplier and gate logic.

    Args:
        df_features: DataFrame with player features

    Returns:
        Dict with calculated percentiles
    """
    percentiles = {}

    # Creation volume percentiles for flash detection
    if 'CREATION_VOLUME_RATIO' in df_features.columns:
        percentiles['creation_vol_25th'] = df_features['CREATION_VOLUME_RATIO'].quantile(0.25)
        percentiles['creation_vol_median'] = df_features['CREATION_VOLUME_RATIO'].median()

    # Efficiency percentiles for flash detection
    if 'CREATION_TAX' in df_features.columns:
        percentiles['creation_tax_80th'] = df_features['CREATION_TAX'].quantile(0.80)

    if 'EFG_ISO_WEIGHTED' in df_features.columns:
        percentiles['efg_iso_80th'] = df_features['EFG_ISO_WEIGHTED'].quantile(0.80)

    if 'RS_PRESSURE_RESILIENCE' in df_features.columns:
        percentiles['pressure_resilience_80th'] = df_features['RS_PRESSURE_RESILIENCE'].quantile(0.80)

    # Star-level medians (players with high usage)
    star_players = df_features[df_features['USG_PCT'] > 0.25]
    if len(star_players) > 0 and 'CREATION_VOLUME_RATIO' in star_players.columns:
        percentiles['star_median_creation_vol'] = star_players['CREATION_VOLUME_RATIO'].median()
    else:
        percentiles['star_median_creation_vol'] = None

    return percentiles


def detect_flash_multiplier(
    player_data: pd.Series,
    percentiles: Dict,
    target_usage: float,
    current_usage: float
) -> Tuple[float, bool]:
    """
    Detect "Flash Multiplier" - elite efficiency on low volume.

    If a player shows elite efficiency on low volume, project to star-level volume
    instead of linear scaling. This captures "flashes of brilliance."

    Args:
        player_data: Player's feature data
        percentiles: Pre-calculated percentiles
        target_usage: Target usage level
        current_usage: Current usage level

    Returns:
        Tuple of (projection_factor, flash_applied)
    """
    if target_usage <= current_usage:
        return 1.0, False

    creation_vol = player_data.get('CREATION_VOLUME_RATIO', 0)
    creation_tax = player_data.get('CREATION_TAX', 0)
    efg_iso = player_data.get('EFG_ISO_WEIGHTED', 0)
    pressure_resilience = player_data.get('RS_PRESSURE_RESILIENCE', 0)

    # Check if "Flash of Brilliance" (low volume + elite efficiency)
    is_low_volume = False
    is_elite_efficiency = False

    if (percentiles.get('creation_vol_25th') is not None and
        pd.notna(creation_vol) and creation_vol < percentiles['creation_vol_25th']):
        is_low_volume = True

    # Expanded flash definition - ISO efficiency OR Pressure Resilience
    if (percentiles.get('creation_tax_80th') is not None and
        pd.notna(creation_tax) and creation_tax > percentiles['creation_tax_80th']):
        is_elite_efficiency = True
    elif (percentiles.get('efg_iso_80th') is not None and
          pd.notna(efg_iso) and efg_iso > percentiles['efg_iso_80th']):
        is_elite_efficiency = True
    elif (percentiles.get('pressure_resilience_80th') is not None and
          pd.notna(pressure_resilience) and pressure_resilience > percentiles['pressure_resilience_80th']):
        is_elite_efficiency = True

    if (is_low_volume and is_elite_efficiency and
        percentiles.get('star_median_creation_vol') is not None):

        # Project to star-level volume instead of scalar projection
        projection_factor = percentiles['star_median_creation_vol'] / max(creation_vol, 0.001)
        logger.debug(f"Flash Multiplier applied: {creation_vol:.4f} → {percentiles['star_median_creation_vol']:.4f}")
        return projection_factor, True

    return 1.0, False


def project_stress_vectors_for_usage(
    player_data: pd.Series,
    target_usage: float,
    usage_buckets: Dict,
    percentiles: Dict
) -> pd.Series:
    """
    Project stress vectors for different usage level using universal projection.

    Features must scale together using empirical distributions, not independently.

    Args:
        player_data: Player's original feature data
        target_usage: Target usage level (decimal)
        usage_buckets: Empirical bucket definitions
        percentiles: Pre-calculated percentiles

    Returns:
        Projected feature vector
    """
    projected_data = player_data.copy()

    # Update usage
    projected_data['USG_PCT'] = target_usage

    current_usage = player_data.get('USG_PCT', target_usage)

    # Apply flash multiplier if applicable
    projection_factor, flash_applied = detect_flash_multiplier(
        player_data, percentiles, target_usage, current_usage
    )

    # If projecting upward, use empirical bucket median instead of linear scaling
    if target_usage > current_usage:
        # Find appropriate bucket
        target_bucket = None
        for bucket_name, bucket_info in usage_buckets.items():
            if bucket_info['min'] <= target_usage < bucket_info['max']:
                target_bucket = bucket_name
                break

        if target_bucket and usage_buckets[target_bucket]['median_creation_vol'] is not None:
            # Use empirical bucket median (non-linear scaling)
            projected_data['CREATION_VOLUME_RATIO'] = usage_buckets[target_bucket]['median_creation_vol']
            logger.debug(f"Universal Projection: {current_usage:.1%} → {target_usage:.1%}, "
                        f"Creation Vol: {player_data.get('CREATION_VOLUME_RATIO', 0):.4f} → "
                        f"{projected_data['CREATION_VOLUME_RATIO']:.4f} (empirical)")
        else:
            # Fallback to flash-adjusted linear scaling
            projected_data['CREATION_VOLUME_RATIO'] = player_data.get('CREATION_VOLUME_RATIO', 0) * projection_factor

    # Store flash multiplier flag for downstream logic
    projected_data['_FLASH_MULTIPLIER_ACTIVE'] = flash_applied

    # Recalculate derived non-linear features for the new usage level
    # This ensures the projection is physically consistent with the Telescope Model v2.1
    if 'SHOT_QUALITY_GENERATION_DELTA' in projected_data.index:
        # HELIO_POTENTIAL_SCORE = SHOT_QUALITY_GENERATION_DELTA * (USG_PCT^1.5)
        # Ensure USG_PCT is decimal for the exponent
        usg_val = projected_data['USG_PCT']
        if usg_val > 1.0:
            usg_val /= 100.0
            
        projected_data['HELIO_POTENTIAL_SCORE'] = projected_data['SHOT_QUALITY_GENERATION_DELTA'] * (usg_val ** 1.5)
        
        # Also update SHOT_QUALITY_GENERATION_DELTA_X_USG interaction term if it exists
        projected_data['SHOT_QUALITY_GENERATION_DELTA_X_USG'] = projected_data['SHOT_QUALITY_GENERATION_DELTA'] * usg_val

    return projected_data


def prepare_features_for_prediction(
    projected_data: pd.Series,
    feature_names: list,
    model
) -> np.ndarray:
    """
    Prepare feature vector for model prediction.

    Args:
        projected_data: Projected player data
        feature_names: Expected feature names
        model: Trained model (for feature validation)

    Returns:
        Feature array ready for prediction
    """
    features = []

    for feature_name in feature_names:
        if feature_name in projected_data.index:
            value = projected_data[feature_name]
            if pd.notna(value):
                features.append(value)
            else:
                # Use median imputation for missing values
                features.append(0.0)  # Conservative imputation
        else:
            # Feature not available
            features.append(0.0)

    return np.array(features).reshape(1, -1)
