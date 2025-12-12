"""
Data Loading Utilities for NBA Resilience Streamlit App

Handles cached loading of model, features, and archetypes data.
"""

import pandas as pd
import joblib
import streamlit as st
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


@st.cache_data
def load_predictive_dataset() -> pd.DataFrame:
    """
    Load predictive dataset with stress vectors.

    Returns:
        DataFrame with player features and metadata
    """
    try:
        df = pd.read_csv('results/predictive_dataset.csv')
        logger.info(f"Loaded predictive dataset: {len(df)} players")
        return df
    except FileNotFoundError:
        st.error("❌ Predictive dataset not found. Please run feature generation first.")
        st.stop()


@st.cache_data
def load_resilience_archetypes() -> pd.DataFrame:
    """
    Load resilience archetypes with performance and dependence scores.

    Returns:
        DataFrame with archetype predictions and scores
    """
    try:
        df = pd.read_csv('results/resilience_archetypes.csv')
        logger.info(f"Loaded archetypes: {len(df)} predictions")
        return df
    except FileNotFoundError:
        st.error("❌ Archetypes data not found. Please run predictions first.")
        st.stop()


@st.cache_data
def load_trained_model() -> Tuple[object, object]:
    """
    Load trained XGBoost model and label encoder.

    Returns:
        Tuple of (model, encoder)
    """
    try:
        model = joblib.load('models/resilience_xgb_rfe_10.pkl')
        encoder = joblib.load('models/archetype_encoder_rfe_10.pkl')
        logger.info("Loaded trained model and encoder")
        return model, encoder
    except FileNotFoundError:
        st.error("❌ Model files not found. Please train the model first.")
        st.stop()


@st.cache_data
def create_master_dataframe() -> pd.DataFrame:
    """
    Create master dataframe by merging features, stress vectors, and comprehensive 2D risk matrix results.

    Merges predictive features with pressure, physicality, plasticity, and 2D risk matrix data.

    Returns:
        Merged dataframe with all data needed for the app
    """
    df_features = load_predictive_dataset()

    # Merge additional stress vector features
    df_master = merge_stress_vector_features(df_features)

    # Try to load comprehensive 2D risk matrix results first (preferred)
    try:
        df_2d_results = pd.read_csv('results/2d_risk_matrix_all_players.csv')
        logger.info(f"Loaded comprehensive 2D risk matrix results: {len(df_2d_results)} records")

        # Merge on available keys
        merge_keys = ['PLAYER_NAME', 'SEASON', 'PLAYER_ID']
        df_master = pd.merge(
            df_master,
            df_2d_results,
            on=merge_keys,
            how='left'  # Left join to keep all features even if no 2D results
        )

        # Handle duplicate columns - prioritize 2D results over original features
        duplicate_columns = ['DEPENDENCE_SCORE', 'ASSISTED_FGM_PCT', 'OPEN_SHOT_FREQUENCY', 'SELF_CREATED_USAGE_RATIO']
        for col in duplicate_columns:
            if f'{col}_y' in df_master.columns:
                # Use the 2D result (suffix _y), fallback to original (suffix _x)
                df_master[col] = df_master[f'{col}_y'].fillna(df_master.get(f'{col}_x'))
                df_master = df_master.drop([f'{col}_x', f'{col}_y'], axis=1)

        logger.info(f"Merged with comprehensive 2D results: {len(df_master)} records")

    except FileNotFoundError:
        # Fallback to original limited 2D results
        logger.warning("Comprehensive 2D results not found, trying limited results")
        try:
            df_2d_results = pd.read_csv('results/2d_risk_matrix_test_results.csv')
            logger.info(f"Loaded limited 2D risk matrix results: {len(df_2d_results)} records")

            # Rename columns to match expected format
            df_2d_results = df_2d_results.rename(columns={
                'player': 'PLAYER_NAME',
                'season': 'SEASON',
                'performance_score': 'PERFORMANCE_SCORE',
                'dependence_score': 'DEPENDENCE_SCORE',
                'risk_category': 'RISK_CATEGORY'
            })

            # Select only the columns we need from 2D results
            columns_to_keep = ['PLAYER_NAME', 'SEASON', 'PERFORMANCE_SCORE', 'DEPENDENCE_SCORE', 'RISK_CATEGORY']
            df_2d_clean = df_2d_results[columns_to_keep].copy()

            # Merge on available keys
            merge_keys = ['PLAYER_NAME', 'SEASON']
            df_master = pd.merge(
                df_master,
                df_2d_clean,
                on=merge_keys,
                how='left'  # Left join to keep all features even if no 2D results
            )

            logger.info(f"Merged with limited 2D results: {len(df_master)} records")

        except FileNotFoundError:
            # Final fallback - no 2D data available
            logger.warning("No 2D risk matrix results found")
            # Add placeholder columns for missing 2D metrics
            df_master['PERFORMANCE_SCORE'] = None
            df_master['DEPENDENCE_SCORE'] = None
            df_master['RISK_CATEGORY'] = None

            logger.warning("No 2D risk matrix data available - run generate_2d_data_for_all.py")

    # Add computed columns for easier access
    df_master['DISPLAY_NAME'] = df_master.apply(
        lambda row: f"{row['PLAYER_NAME']} ({row['SEASON']})",
        axis=1
    )

    # Ensure USG_PCT is in decimal format
    df_master['USG_PCT'] = df_master['USG_PCT'].apply(
        lambda x: x / 100.0 if x > 1.0 else x
    )

    logger.info(f"Created master dataframe: {len(df_master)} records")
    return df_master


def merge_stress_vector_features(df_base: pd.DataFrame) -> pd.DataFrame:
    """
    Merge additional stress vector features (pressure, physicality, plasticity) into the base dataframe.

    Args:
        df_base: Base dataframe with predictive features

    Returns:
        DataFrame with additional stress vector features merged in
    """
    df_master = df_base.copy()

    # Merge pressure features
    try:
        df_pressure = pd.read_csv('results/pressure_features.csv')
        pressure_cols_to_keep = [
            'PLAYER_ID', 'PLAYER_NAME', 'SEASON',
            'RS_PRESSURE_RESILIENCE',  # For radar chart "Pressure"
            'RS_PRESSURE_APPETITE',    # Additional pressure data
        ]
        df_pressure_clean = df_pressure[pressure_cols_to_keep].copy()

        merge_keys = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON']
        df_master = pd.merge(df_master, df_pressure_clean, on=merge_keys, how='left')
        logger.info(f"Merged pressure features: {df_pressure_clean['RS_PRESSURE_RESILIENCE'].notna().sum()} players with pressure data")

    except FileNotFoundError:
        logger.warning("Pressure features file not found - pressure radar chart will show defaults")
    except Exception as e:
        logger.warning(f"Error merging pressure features: {e}")

    # Merge physicality features (for rim appetite)
    try:
        df_physicality = pd.read_csv('results/physicality_features.csv')
        # Look for rim-related features
        rim_cols = [col for col in df_physicality.columns if 'rim' in col.lower() or 'fta' in col.lower() or 'fgm' in col.lower()]
        if rim_cols:
            physicality_cols_to_keep = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON'] + rim_cols[:3]  # Take first 3 rim-related cols
            df_physicality_clean = df_physicality[physicality_cols_to_keep].copy()

            merge_keys = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON']
            df_master = pd.merge(df_master, df_physicality_clean, on=merge_keys, how='left')
            logger.info(f"Merged physicality features: {len(physicality_cols_to_keep)-3} physicality metrics")

    except FileNotFoundError:
        logger.warning("Physicality features file not found - physicality radar chart will show defaults")
    except Exception as e:
        logger.warning(f"Error merging physicality features: {e}")

    # Merge plasticity features
    try:
        df_plasticity = pd.read_csv('results/plasticity_scores.csv')
        plasticity_cols_to_keep = [
            'PLAYER_ID', 'PLAYER_NAME', 'SEASON',
            'RESILIENCE_SCORE',      # For radar chart "Plasticity"
            'PRODUCTION_RESILIENCE', # Additional plasticity data
            'ADJ_COUNTER_PUNCH'
        ]
        df_plasticity_clean = df_plasticity[plasticity_cols_to_keep].copy()

        merge_keys = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON']
        df_master = pd.merge(df_master, df_plasticity_clean, on=merge_keys, how='left')
        logger.info(f"Merged plasticity features: {df_plasticity_clean['RESILIENCE_SCORE'].notna().sum()} players with plasticity data")

    except FileNotFoundError:
        logger.warning("Plasticity features file not found - plasticity radar chart will show defaults")
    except Exception as e:
        logger.warning(f"Error merging plasticity features: {e}")

    # Add derived physicality feature if rim data is missing
    if 'RS_RIM_APPETITE' not in df_master.columns:
        # Try multiple approaches to derive rim appetite

        # Approach 1: Use physicality features if available
        if any(col.startswith('RS_F') for col in df_master.columns):
            # Look for rim-related features in physicality data
            rim_features = [col for col in df_master.columns if 'rim' in col.lower() or ('fga' in col.lower() and 'rs' in col.lower())]
            if rim_features:
                # Use the first rim-related feature as a proxy
                proxy_col = rim_features[0]
                df_master['RS_RIM_APPETITE'] = df_master[proxy_col].fillna(0.5)  # Default to median
                logger.info(f"Using {proxy_col} as RS_RIM_APPETITE proxy")

        # Approach 2: Simple derivation from usage and existing features
        if 'RS_RIM_APPETITE' not in df_master.columns:
            # Use USG_PCT as a rough proxy - higher usage often correlates with rim appetite
            df_master['RS_RIM_APPETITE'] = df_master['USG_PCT'].fillna(0.5)
            logger.info("Derived RS_RIM_APPETITE from USG_PCT as fallback")

    return df_master


@st.cache_data
def get_season_options(df_master: pd.DataFrame) -> list:
    """
    Get sorted list of available seasons.

    Args:
        df_master: Master dataframe

    Returns:
        Sorted list of seasons
    """
    seasons = sorted(df_master['SEASON'].unique(), reverse=True)
    return seasons


@st.cache_data
def get_players_for_season(df_master: pd.DataFrame, season: str) -> pd.DataFrame:
    """
    Get players for a specific season.

    Args:
        df_master: Master dataframe
        season: Season string (e.g., '2021-22')

    Returns:
        Filtered dataframe for the season
    """
    return df_master[df_master['SEASON'] == season].copy()


def get_player_data(df_master: pd.DataFrame, player_name: str, season: str) -> Optional[pd.Series]:
    """
    Get data for a specific player in a specific season.

    Args:
        df_master: Master dataframe
        player_name: Player name
        season: Season string

    Returns:
        Player data series or None if not found
    """
    mask = (df_master['PLAYER_NAME'] == player_name) & (df_master['SEASON'] == season)
    matches = df_master[mask]

    if len(matches) == 0:
        return None
    elif len(matches) > 1:
        logger.warning(f"Multiple matches for {player_name} in {season}, using first")
        return matches.iloc[0]
    else:
        return matches.iloc[0]


@st.cache_data
def prepare_radar_chart_data(df_season: pd.DataFrame, player_data: pd.Series) -> Tuple[list, list]:
    """
    Prepare data for stress vectors radar chart.

    Converts raw features to percentiles for comparability.

    Args:
        df_season: All players in the season
        player_data: Selected player's data

    Returns:
        Tuple of (categories, percentiles)
    """
    categories = ['Creation', 'Leverage', 'Pressure', 'Physicality', 'Plasticity']
    percentiles = []

    # Define feature mappings (inverted where higher values are worse)
    feature_mapping = {
        'Creation': ('CREATION_TAX', True),  # Invert: higher tax = worse
        'Leverage': ('LEVERAGE_TS_DELTA', False),  # Don't invert: positive = better
        'Pressure': ('RS_PRESSURE_RESILIENCE', False),  # Don't invert: higher resilience = better
        'Physicality': ('RS_RIM_APPETITE', False),  # Don't invert: higher rim appetite = better
        'Plasticity': ('RESILIENCE_SCORE', False)  # Don't invert: higher resilience = better
    }

    for category, (feature_name, invert) in feature_mapping.items():
        if feature_name in df_season.columns and feature_name in player_data.index:
            player_value = player_data[feature_name]
            season_values = df_season[feature_name].dropna()

            if len(season_values) > 0 and pd.notna(player_value):
                # Calculate percentile rank
                percentile = (season_values <= player_value).mean() * 100

                # For inverted features (higher = worse), flip the percentile
                if invert:
                    percentile = 100 - percentile

                percentiles.append(percentile)
            else:
                percentiles.append(50.0)  # Default to median
        else:
            percentiles.append(50.0)  # Default to median

    return categories, percentiles
