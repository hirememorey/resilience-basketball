"""
Calculate System Dependence Score for 2D Risk Matrix

This script calculates the Dependence Score (Y-axis) for the 2D Risk Matrix.
The Dependence Score measures how portable/system-dependent a player's production is.

Formula:
DEPENDENCE_SCORE = (
    ASSISTED_FGM_PCT * 0.40 +           # 40% weight - shots created by others
    OPEN_SHOT_FREQUENCY * 0.35 +         # 35% weight - wide open shots (system/gravity)
    (1 - SELF_CREATED_USAGE_RATIO) * 0.25  # 25% weight - can't create own offense
)

All components are calculated from objective regular season data (no hindsight bias).
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_dependence_score(player_data: pd.Series) -> dict:
    """
    Calculate System Dependence Score for a single player-season.
    
    Args:
        player_data: Player's stress vector data (Series) with tracking stats
        
    Returns:
        Dictionary with:
        - dependence_score: Overall dependence score (0-1, higher = more dependent)
        - assisted_fgm_pct: Percentage of FGM that are assisted (0-1)
        - open_shot_frequency: Percentage of FGA that are wide open (0-1)
        - self_created_usage_ratio: Percentage of offense that is self-created (0-1)
        - components: Breakdown of each component's contribution
    """
    # Component 1: Assisted FGM Percentage
    # Proxy: catch_shoot_field_goals_made / total_field_goals_made
    # Catch-and-shoot shots are typically assisted
    assisted_fgm_pct = None
    
    # Try to get from tracking stats
    catch_shoot_fgm = player_data.get('catch_shoot_field_goals_made', None)
    total_fgm = player_data.get('field_goals_made', None)
    
    # If not in player_data, try alternative column names
    if pd.isna(catch_shoot_fgm) or catch_shoot_fgm is None:
        # Try RS-prefixed version
        catch_shoot_fgm = player_data.get('RS_CATCH_SHOOT_FGM', None)
    
    if pd.isna(total_fgm) or total_fgm is None:
        # Try FGM from different sources
        total_fgm = player_data.get('FGM', None)
        if pd.isna(total_fgm) or total_fgm is None:
            total_fgm = player_data.get('RS_FGM', None)
    
    if pd.notna(catch_shoot_fgm) and pd.notna(total_fgm) and total_fgm > 0:
        assisted_fgm_pct = catch_shoot_fgm / total_fgm
        # Cap at 1.0 (can't have more assisted than total)
        assisted_fgm_pct = min(assisted_fgm_pct, 1.0)
    else:
        # Fallback: Use pull-up + drive as proxy for unassisted
        # If we have pull_up and drive FGM, we can estimate
        pull_up_fgm = player_data.get('pull_up_field_goals_made', None)
        drive_fgm = player_data.get('drive_field_goals_made', None)
        
        if pd.notna(pull_up_fgm) and pd.notna(drive_fgm) and pd.notna(total_fgm) and total_fgm > 0:
            # Unassisted = pull_up + drive (self-created)
            unassisted_fgm = (pull_up_fgm if pd.notna(pull_up_fgm) else 0) + (drive_fgm if pd.notna(drive_fgm) else 0)
            assisted_fgm_pct = 1.0 - (unassisted_fgm / total_fgm)
            assisted_fgm_pct = max(0.0, min(assisted_fgm_pct, 1.0))  # Cap between 0 and 1
        else:
            # Last resort: Use CREATION_VOLUME_RATIO as inverse proxy
            # Higher creation volume = lower assisted rate
            creation_vol_ratio = player_data.get('CREATION_VOLUME_RATIO', None)
            if pd.notna(creation_vol_ratio):
                # Inverse relationship: if creation_vol_ratio is 0.5, assume 50% unassisted
                # So assisted = 1 - creation_vol_ratio (rough proxy)
                assisted_fgm_pct = 1.0 - min(creation_vol_ratio, 1.0)
            else:
                assisted_fgm_pct = None
    
    # Component 2: Open Shot Frequency
    # Already calculated in pressure features: RS_OPEN_SHOT_FREQUENCY
    open_shot_frequency = None
    
    if 'RS_OPEN_SHOT_FREQUENCY' in player_data.index:
        open_shot_frequency = player_data['RS_OPEN_SHOT_FREQUENCY']
    elif 'OPEN_SHOT_FREQUENCY' in player_data.index:
        open_shot_frequency = player_data['OPEN_SHOT_FREQUENCY']
    elif 'FGA_6_PLUS' in player_data.index and 'TOTAL_FGA' in player_data.index:
        # Calculate from shot quality data
        fga_6_plus = player_data.get('FGA_6_PLUS', 0)
        total_fga = player_data.get('TOTAL_FGA', 0)
        if pd.notna(fga_6_plus) and pd.notna(total_fga) and total_fga > 0:
            open_shot_frequency = fga_6_plus / total_fga
    elif 'RS_TOTAL_TRACKED_FGA_PER_GAME' in player_data.index:
        # Try to get from tracked FGA data
        fga_6_plus = player_data.get('FGA_6_PLUS', 0)
        total_tracked = player_data.get('RS_TOTAL_TRACKED_FGA_PER_GAME', 0)
        if pd.notna(fga_6_plus) and pd.notna(total_tracked) and total_tracked > 0:
            open_shot_frequency = fga_6_plus / total_tracked
    
    # Component 3: Self-Created Usage Ratio
    # Use same logic as predict_conditional_archetype.py (Bag Check Gate)
    self_created_usage_ratio = None
    
    # Try explicit ISO/PNR data first
    iso_freq = player_data.get('ISO_FREQUENCY', None)
    pnr_freq = player_data.get('PNR_HANDLER_FREQUENCY', None)
    
    if pd.notna(iso_freq) and pd.notna(pnr_freq):
        # Use explicit playtype data
        self_created_usage_ratio = (iso_freq if pd.notna(iso_freq) else 0.0) + (pnr_freq if pd.notna(pnr_freq) else 0.0)
    elif 'CREATION_VOLUME_RATIO' in player_data.index:
        # Use CREATION_VOLUME_RATIO as proxy (same logic as Bag Check Gate)
        creation_vol_ratio = player_data.get('CREATION_VOLUME_RATIO', None)
        efg_iso = player_data.get('EFG_ISO_WEIGHTED', None)
        
        if pd.notna(creation_vol_ratio):
            # Phase 3.8 Fix: Better heuristic for system-based creation
            # High creation volume (>0.15) without ISO/PNR data = likely system-based (hub player)
            if creation_vol_ratio > 0.15:
                # Conservative estimate: assume only 35% is self-created (system-based assumption)
                self_created_usage_ratio = creation_vol_ratio * 0.35
            else:
                # Moderate creation volume - use 60% estimate
                self_created_usage_ratio = creation_vol_ratio * 0.60
    elif 'SELF_CREATED_FREQ' in player_data.index:
        # Use pre-calculated gate feature ONLY if it's > 0 (not a placeholder)
        # Gate features set SELF_CREATED_FREQ to 0.0 when ISO/PNR data is missing
        # So if it's 0.0, we should use CREATION_VOLUME_RATIO proxy instead
        self_created_freq = player_data['SELF_CREATED_FREQ']
        if pd.notna(self_created_freq) and self_created_freq > 0:
            # Has actual data (not placeholder)
            self_created_usage_ratio = self_created_freq
        # If it's 0.0, we'll leave it as None and handle in the fallback below
    
    # Calculate Dependence Score
    # Handle missing components gracefully
    components = {}
    dependence_score = None
    
    # PHASE 3 FINAL FIXES: Use pd.notna() instead of is not None for pandas compatibility
    # This ensures NaN values are properly handled
    if pd.notna(assisted_fgm_pct) and pd.notna(open_shot_frequency) and pd.notna(self_created_usage_ratio):
        # All components available - calculate full score
        components['assisted'] = assisted_fgm_pct * 0.40
        components['open_shot'] = open_shot_frequency * 0.35
        components['low_self_creation'] = (1.0 - self_created_usage_ratio) * 0.25
        
        dependence_score = components['assisted'] + components['open_shot'] + components['low_self_creation']
        # Cap at 1.0
        dependence_score = min(dependence_score, 1.0)
    # PHASE 3 FINAL FIXES: Changed rim pressure override from separate if to elif
    # This ensures the 2-component fallback only executes if full calculation didn't happen
    elif pd.notna(assisted_fgm_pct) and pd.notna(open_shot_frequency):
        # Missing self-creation - use 2 components with adjusted weights
        components['assisted'] = assisted_fgm_pct * 0.50  # Adjusted weight
        components['open_shot'] = open_shot_frequency * 0.50  # Adjusted weight
        components['low_self_creation'] = None
        
        dependence_score = components['assisted'] + components['open_shot']
    
    # FRANCHISE CORNERSTONE FIX: Rim Pressure Override (applies AFTER calculation)
    # Players with high rim appetite generate their own offense via positioning and physicality,
    # even if the box score says "Assisted". Rim pressure = self-created offense.
    # PHASE 3 FINAL FIXES: Increased threshold from 0.20 to 0.25 to avoid catching guards
    # (e.g., Jordan Poole with 0.201 RS_RIM_APPETITE shouldn't get this benefit)
    # Apply rim pressure override AFTER calculating dependence_score
    if dependence_score is not None:
        rim_appetite = player_data.get('RS_RIM_APPETITE', None)
        if pd.notna(rim_appetite) and rim_appetite > 0.25:
            # Cap dependence score at 0.40 (rim pressure reduces dependence but doesn't eliminate it)
            # This allows "Franchise Cornerstone" classification (High Performance + Low Dependence)
            original_score = dependence_score
            dependence_score = min(dependence_score, 0.40)
            if original_score != dependence_score:
                logger.debug(f"Rim Pressure Override: Dependence score capped from {original_score:.3f} to {dependence_score:.3f} (RS_RIM_APPETITE={rim_appetite:.3f} > 0.25)")
    elif pd.notna(open_shot_frequency) and pd.notna(self_created_usage_ratio):
        # Missing assisted - use 2 components with adjusted weights
        components['assisted'] = None
        components['open_shot'] = open_shot_frequency * 0.50  # Adjusted weight
        components['low_self_creation'] = (1.0 - self_created_usage_ratio) * 0.50  # Adjusted weight
        
        dependence_score = components['open_shot'] + components['low_self_creation']
    elif pd.notna(open_shot_frequency):
        # Only open shot frequency available - use as single component
        components['assisted'] = None
        components['open_shot'] = open_shot_frequency
        components['low_self_creation'] = None
        
        dependence_score = open_shot_frequency
    else:
        # Insufficient data - return None
        components['assisted'] = None
        components['open_shot'] = None
        components['low_self_creation'] = None
        dependence_score = None
    
    return {
        'dependence_score': dependence_score,
        'assisted_fgm_pct': assisted_fgm_pct,
        'open_shot_frequency': open_shot_frequency,
        'self_created_usage_ratio': self_created_usage_ratio,
        'components': components
    }


def calculate_dependence_scores_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Dependence Scores for all player-seasons in a DataFrame.
    
    Args:
        df: DataFrame with player-season data (must have PLAYER_ID, SEASON columns)
        
    Returns:
        DataFrame with dependence scores added
    """
    df = df.copy()
    
    results = []
    for idx, row in df.iterrows():
        result = calculate_dependence_score(row)
        results.append({
            'PLAYER_ID': row.get('PLAYER_ID', None),
            'PLAYER_NAME': row.get('PLAYER_NAME', None),
            'SEASON': row.get('SEASON', None),
            'DEPENDENCE_SCORE': result['dependence_score'],
            'ASSISTED_FGM_PCT': result['assisted_fgm_pct'],
            'OPEN_SHOT_FREQUENCY': result['open_shot_frequency'],
            'SELF_CREATED_USAGE_RATIO': result['self_created_usage_ratio']
        })
    
    df_dependence = pd.DataFrame(results)
    
    # Drop existing dependence score columns if they exist (they may be NaN from previous failed attempts)
    cols_to_drop = ['DEPENDENCE_SCORE', 'ASSISTED_FGM_PCT', 'OPEN_SHOT_FREQUENCY', 'SELF_CREATED_USAGE_RATIO']
    for col in cols_to_drop:
        if col in df.columns:
            df = df.drop(columns=[col])
    
    # Merge back into original dataframe
    merge_cols = ['PLAYER_ID', 'SEASON']
    if 'PLAYER_NAME' in df.columns and 'PLAYER_NAME' in df_dependence.columns:
        merge_cols.append('PLAYER_NAME')
    
    df = pd.merge(df, df_dependence, on=merge_cols, how='left')
    
    logger.info(f"Calculated dependence scores for {df_dependence['DEPENDENCE_SCORE'].notna().sum()}/{len(df_dependence)} player-seasons")
    
    return df


if __name__ == "__main__":
    # Test on sample data
    from predict_conditional_archetype import ConditionalArchetypePredictor
    
    predictor = ConditionalArchetypePredictor()
    
    # Test on known cases
    test_cases = [
        ("Jordan Poole", "2021-22"),  # Expected: High dependence
        ("Luka Dončić", "2023-24"),   # Expected: Low dependence
        ("Domantas Sabonis", "2021-22")  # Expected: High dependence
    ]
    
    print("\n=== Dependence Score Test Cases ===\n")
    
    for player_name, season in test_cases:
        player_data = predictor.get_player_data(player_name, season)
        if player_data is not None:
            result = calculate_dependence_score(player_data)
            print(f"{player_name} ({season}):")
            print(f"  Dependence Score: {result['dependence_score']:.3f}" if result['dependence_score'] is not None else "  Dependence Score: N/A")
            print(f"  Assisted FGM %: {result['assisted_fgm_pct']:.3f}" if result['assisted_fgm_pct'] is not None else "  Assisted FGM %: N/A")
            print(f"  Open Shot Frequency: {result['open_shot_frequency']:.3f}" if result['open_shot_frequency'] is not None else "  Open Shot Frequency: N/A")
            print(f"  Self-Created Usage Ratio: {result['self_created_usage_ratio']:.3f}" if result['self_created_usage_ratio'] is not None else "  Self-Created Usage Ratio: N/A")
            print(f"  Components: {result['components']}")
            print()
        else:
            print(f"{player_name} ({season}): Data not found\n")

