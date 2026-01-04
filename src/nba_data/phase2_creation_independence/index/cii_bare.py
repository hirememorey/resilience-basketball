"""
Bare CII Calculator - No Gates Version

This calculates CII using the multi-path architecture but with
ZERO gates, adjustments, or corrections.

Purpose: Establish what the pure architecture produces before any tuning.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd
from .paths.combined import MultiPathCombiner

# =============================================================================
# BARE COMPONENT CALCULATORS (No Gates)
# =============================================================================

def calculate_pressure_appetite_bare(player_data: dict) -> float:
    """Bare C2 calculation."""
    # Weights
    w_clutch = 0.50
    w_relative = 0.30
    w_playoff = 0.20
    
    # 1. Clutch Usage Absolute
    clutch_usg = player_data.get('clutch_usg_absolute', 0.15)
    if clutch_usg > 1.0: clutch_usg /= 100.0
    clutch_score = np.clip((clutch_usg - 0.10) / 0.30 * 100, 0, 100)
    
    # 2. Relative Usage Change (leverage_usg_delta)
    rel_change = player_data.get('leverage_usg_delta', 0)
    rel_score = np.clip(50 + (rel_change * 200), 0, 100)
    
    # 3. Playoff Elevation
    rs_usg = player_data.get('usg_pct', 0.20)
    po_usg = player_data.get('playoff_usg_pct', rs_usg)
    if rs_usg > 1.0: rs_usg /= 100.0
    if po_usg > 1.0: po_usg /= 100.0
    
    if rs_usg > 0.05:
        po_bump = (po_usg - rs_usg) / rs_usg
    else:
        po_bump = 0
    po_score = np.clip(50 + (po_bump * 150), 0, 100)
    
    return round(clutch_score * w_clutch + rel_score * w_relative + po_score * w_playoff, 1)

def calculate_difficulty_embrace_bare(player_data: dict) -> float:
    """Bare C3 calculation (Perimeter path only to avoid hub gates)."""
    # Weights
    w_pullup = 0.40
    w_midrange = 0.30
    w_pullup3 = 0.20
    w_time = 0.10
    
    # 1. Pull-up Volume
    pullup_fga = player_data.get('pull_up_fga', 0)
    pullup_score = np.clip((pullup_fga / 10.0) * 100, 0, 100)
    
    # 2. Mid-Range %
    mid_pct = player_data.get('pct_pts_2pt_mr', 0)
    mid_score = np.clip((mid_pct / 0.30) * 100, 0, 100)
    
    # 3. Pull-up 3
    pullup3 = player_data.get('pull_up_fg3a', 0)
    pullup3_score = np.clip((pullup3 / 7.0) * 100, 0, 100)
    
    # 4. Time of Possession
    top = player_data.get('time_of_poss', 3.0)
    top_score = np.clip((top - 2.0) / 5.0 * 100, 0, 100)
    
    return round(pullup_score * w_pullup + mid_score * w_midrange + pullup3_score * w_pullup3 + top_score * w_time, 1)

def calculate_defensive_survival_bare(player_data: dict) -> float:
    """Bare C4 calculation (No volume-adjusted efficiency penalty)."""
    # Weights
    w_vol = 0.35
    w_vers = 0.30
    w_eff = 0.25
    w_frag = 0.10
    
    # 1. Volume Maintenance
    usg_delta = player_data.get('leverage_usg_delta', 0)
    vol_score = np.clip((usg_delta + 0.15) / 0.30 * 100, 0, 100)
    
    # 2. Versatility (simplified)
    pullup_fga = player_data.get('pull_up_fga', 0)
    vers_score = np.clip((pullup_fga / 8.0) * 100, 0, 100)
    
    # 3. Efficiency Resilience (BARE: No multiplier)
    ts_delta = player_data.get('leverage_ts_delta', 0)
    eff_score = np.clip((ts_delta + 0.15) / 0.25 * 100, 0, 100)
    
    # 4. Fragility Inverse
    frag = player_data.get('fragility_score', 0.5)
    if frag > 1.0: frag /= 100.0
    frag_score = (1.0 - frag) * 100
    
    return round(vol_score * w_vol + vers_score * w_vers + eff_score * w_eff + frag_score * w_frag, 1)

def calculate_force_multiplication_bare(player_data: dict) -> float:
    """Bare C5 calculation."""
    # Weights
    w_tools = 0.25
    w_vol = 0.30
    w_agency = 0.25
    w_touch = 0.20
    
    # 1. Tools
    phys = player_data.get('physicality_score', 0.5)
    if phys > 1.0: phys /= 100.0
    tools_score = np.clip((phys - 0.30) / 0.70 * 100, 0, 100)
    
    # 2. Volume
    usg = player_data.get('usg_pct', 0.18)
    if usg > 1.0: usg /= 100.0
    vol_score = np.clip((usg - 0.15) / 0.20 * 100, 0, 100)
    
    # 3. Agency
    clutch_usg = player_data.get('clutch_usg_absolute', usg)
    if clutch_usg > 1.0: clutch_usg /= 100.0
    agency_score = np.clip((clutch_usg - 0.12) / 0.23 * 100, 0, 100)
    
    # 4. Touch
    tp = player_data.get('weighted_touch_production', 2.0)
    touch_score = np.clip((tp - 0.5) / 5.5 * 100, 0, 100)
    
    return round(tools_score * w_tools + vol_score * w_vol + agency_score * w_agency + touch_score * w_touch, 1)


# =============================================================================
# MAIN BARE CALCULATOR
# =============================================================================

class BareCIICalculator:
    """
    CII Calculator with no gates or adjustments.
    
    Component Weights:
    - Self-Created (C1): 30%
    - Pressure Appetite (C2): 25%
    - Difficulty Embrace (C3): 20%
    - Defensive Survival (C4): 15%
    - Force Multiplication (C5): 10%
    """
    
    WEIGHTS = {
        'self_created': 0.30,
        'pressure_appetite': 0.25,
        'difficulty_embrace': 0.20,
        'defensive_survival': 0.15,
        'force_multiplication': 0.10,
    }
    
    def __init__(self):
        self.path_combiner = MultiPathCombiner()
    
    def calculate(self, player_data: dict) -> Dict:
        """
        Calculate bare CII score.
        
        Returns:
            Dictionary with complete breakdown
        """
        # Component 1: Self-Created (Multi-Path)
        c1_result = self.path_combiner.calculate(player_data)
        c1_score = c1_result['final_score']
        
        # Component 2: Pressure Appetite (bare version)
        c2_score = calculate_pressure_appetite_bare(player_data)
        
        # Component 3: Difficulty Embrace (bare version)
        c3_score = calculate_difficulty_embrace_bare(player_data)
        
        # Component 4: Defensive Survival (bare version)
        c4_score = calculate_defensive_survival_bare(player_data)
        
        # Component 5: Force Multiplication (bare version)
        c5_score = calculate_force_multiplication_bare(player_data)
        
        # Weighted combination
        cii_total = (
            c1_score * self.WEIGHTS['self_created'] +
            c2_score * self.WEIGHTS['pressure_appetite'] +
            c3_score * self.WEIGHTS['difficulty_embrace'] +
            c4_score * self.WEIGHTS['defensive_survival'] +
            c5_score * self.WEIGHTS['force_multiplication']
        )
        
        return {
            'cii_total': round(cii_total, 1),
            'component_scores': {
                'self_created': c1_score,
                'pressure_appetite': c2_score,
                'difficulty_embrace': c3_score,
                'defensive_survival': c4_score,
                'force_multiplication': c5_score,
            },
            'self_created_breakdown': c1_result,
            'weights': self.WEIGHTS,
            'gates_applied': [],  # Explicitly empty - no gates
        }

