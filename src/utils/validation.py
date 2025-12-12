"""
Data validation utilities for NBA Playoff Resilience Engine.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


def validate_player_data(player_data: Dict) -> Dict[str, Any]:
    """
    Validate player data completeness and quality.

    Args:
        player_data: Player season data dictionary

    Returns:
        Validation results with completeness score and issues
    """
    validation = {
        'is_valid': True,
        'completeness_score': 0.0,
        'issues': [],
        'missing_fields': [],
        'data_quality_checks': {}
    }

    if not player_data:
        validation['is_valid'] = False
        validation['issues'].append('Player data is empty')
        return validation

    # Required fields for basic functionality
    required_fields = ['player_id', 'season', 'usg_pct', 'efg_pct']
    present_fields = [f for f in required_fields if f in player_data and pd.notna(player_data[f])]

    validation['completeness_score'] = len(present_fields) / len(required_fields)
    validation['missing_fields'] = [f for f in required_fields if f not in present_fields]

    if validation['missing_fields']:
        validation['issues'].append(f"Missing required fields: {validation['missing_fields']}")

    # Data quality checks
    if 'usg_pct' in player_data:
        usg = player_data['usg_pct']
        if not (0 <= usg <= 1):
            validation['issues'].append(f"Invalid usage percentage: {usg}")
            validation['data_quality_checks']['usg_range'] = False
        else:
            validation['data_quality_checks']['usg_range'] = True

    if 'efg_pct' in player_data:
        efg = player_data['efg_pct']
        if not (0 <= efg <= 1):
            validation['issues'].append(f"Invalid eFG percentage: {efg}")
            validation['data_quality_checks']['efg_range'] = False
        else:
            validation['data_quality_checks']['efg_range'] = True

    # Overall validity
    validation['is_valid'] = len(validation['issues']) == 0

    return validation


def validate_data_completeness() -> Dict[str, Any]:
    """
    Validate overall dataset completeness and quality.

    Returns:
        Dataset validation results
    """
    validation = {
        'overall_completeness': 0.0,
        'total_players': 0,
        'total_seasons': 0,
        'data_files_status': {},
        'quality_metrics': {}
    }

    # Check key data files
    data_files = {
        'predictive_dataset': 'data/processed/predictive_dataset.csv',
        'raw_player_data': 'data/raw/nba_api/',
        'shot_charts': 'data/raw/shot_charts/'
    }

    for name, path in data_files.items():
        from pathlib import Path
        p = Path(path)
        validation['data_files_status'][name] = {
            'exists': p.exists(),
            'path': str(p)
        }

        if p.is_file():
            try:
                # Try to read first few lines to check format
                if name == 'predictive_dataset':
                    df = pd.read_csv(p, nrows=5)
                    validation['data_files_status'][name]['rows'] = len(df) if len(df) > 0 else 'unknown'
                    validation['data_files_status'][name]['columns'] = len(df.columns)
            except Exception as e:
                validation['data_files_status'][name]['error'] = str(e)

    # Calculate overall completeness
    existing_files = sum(1 for status in validation['data_files_status'].values() if status['exists'])
    validation['overall_completeness'] = existing_files / len(data_files)

    return validation


def validate_model_inputs(X: pd.DataFrame, feature_names: List[str]) -> Dict[str, Any]:
    """
    Validate model input data.

    Args:
        X: Feature matrix
        feature_names: Expected feature names

    Returns:
        Validation results
    """
    validation = {
        'is_valid': True,
        'issues': [],
        'shape': X.shape,
        'feature_check': {}
    }

    # Check shape
    if X.shape[0] == 0:
        validation['issues'].append("No samples in feature matrix")
        validation['is_valid'] = False

    if X.shape[1] == 0:
        validation['issues'].append("No features in feature matrix")
        validation['is_valid'] = False

    # Check for NaN values
    nan_counts = X.isnull().sum()
    total_nans = nan_counts.sum()

    if total_nans > 0:
        validation['issues'].append(f"Found {total_nans} NaN values in feature matrix")
        validation['nan_summary'] = nan_counts[nan_counts > 0].to_dict()

    # Check feature names
    actual_features = list(X.columns)
    missing_features = [f for f in feature_names if f not in actual_features]
    extra_features = [f for f in actual_features if f not in feature_names]

    if missing_features:
        validation['issues'].append(f"Missing expected features: {missing_features}")

    if extra_features:
        validation['issues'].append(f"Unexpected features: {extra_features}")

    validation['feature_check'] = {
        'expected_features': len(feature_names),
        'actual_features': len(actual_features),
        'missing_features': missing_features,
        'extra_features': extra_features
    }

    validation['is_valid'] = len(validation['issues']) == 0

    return validation
