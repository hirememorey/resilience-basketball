#!/usr/bin/env python3
"""
Unified Playoff Resilience Calculator - Phase 5 Integration
Refactored to implement the "Project Pivot" Logic (Friction, Crucible, Micro-Evolution).

Combines 5 Pathways:
1. Friction Resilience (Process Independence)
2. Crucible Resilience (Top-10 Defense Performance)
3. Micro-Evolution (Within-Season Adaptability)
4. Dominance (SQAV)
5. Versatility (Method Diversity)

Uses direct class-based calculators and Z-Score normalization for consistent aggregation.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Dict, List, Optional
import logging

# Add the scripts directory to path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent.parent)) # Add src root for utils

from calculate_dominance_score import calculate_player_sqav
from calculate_longitudinal_evolution import calculate_longitudinal_evolution
from calculate_extended_resilience import calculate_method_resilience
from calculate_friction import FrictionCalculator
from calculate_crucible_baseline import CrucibleCalculator
from nba_data.utils.normalization import standardize_metric

DB_PATH = "data/nba_stats.db"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedCalculator:
    def __init__(self, season="2023-24"):
        self.season = season
        self.friction_calc = FrictionCalculator(DB_PATH)
        self.crucible_calc = CrucibleCalculator(DB_PATH)
        
        # Cache for batch calculations
        self._friction_cache = None
        self._crucible_cache = None
        
    def _get_friction_scores(self) -> Dict[int, float]:
        """Get Friction scores directly from calculator."""
        if self._friction_cache is None:
            logger.info("Calculating batch Friction scores...")
            self._friction_cache = self.friction_calc.get_resilience_dict(self.season)
        return self._friction_cache

    def _get_crucible_scores(self) -> Dict[int, float]:
        """Get Crucible scores directly from calculator."""
        if self._crucible_cache is None:
            logger.info("Calculating batch Crucible scores...")
            self._crucible_cache = self.crucible_calc.get_resilience_dict(self.season)
        return self._crucible_cache

    def get_db_connection(self):
        return sqlite3.connect(DB_PATH)

    def calculate_batch_scores(self, player_ids: List[int]) -> pd.DataFrame:
        """
        Calculate Unified Scores for a list of players using Z-Score normalization.
        """
        conn = self.get_db_connection()
        
        # 1. Gather Raw Data for All Players
        # ----------------------------------
        raw_data = []
        friction_map = self._get_friction_scores()
        crucible_map = self._get_crucible_scores()
        
        logger.info(f"Processing {len(player_ids)} players...")
        
        for pid in player_ids:
            # A. Friction
            friction = friction_map.get(pid, None)
            
            # B. Crucible
            crucible = crucible_map.get(pid, None)
            
            # C. Evolution (Expensive - could optimize batching later)
            try:
                evo_data = calculate_longitudinal_evolution(pid)
                evolution = evo_data.get('Adaptability_Score', 0.0)
            except:
                evolution = 0.0
                
            # D. Dominance
            try:
                dominance = calculate_player_sqav(pid, self.season, "Regular Season")
            except:
                dominance = 0.0
                
            # E. Versatility
            try:
                versatility = calculate_method_resilience(conn, "Regular Season", pid)
            except:
                versatility = 0.0
                
            raw_data.append({
                'player_id': pid,
                'friction': friction,
                'crucible': crucible,
                'evolution': evolution,
                'dominance': dominance,
                'versatility': versatility
            })
            
        conn.close()
        
        df = pd.DataFrame(raw_data)
        
        # 2. Z-Score Normalization (Vectorized)
        # -------------------------------------
        # We only normalize if we have valid data.
        # Missing friction/crucible means player didn't qualify (e.g. missed playoffs).
        
        pathways = ['friction', 'crucible', 'evolution', 'dominance', 'versatility']
        
        # Create Normalized Columns (0-100 scale)
        for p in pathways:
            # Filter out None/NaN for calculation stats
            valid_mask = df[p].notna() & (df[p] != 0)
            
            if valid_mask.sum() > 1:
                mean = df.loc[valid_mask, p].mean()
                std = df.loc[valid_mask, p].std()
                
                if std == 0:
                    df[f'{p}_norm'] = 50.0
                else:
                    # Z-Score -> Normalize to Mean=50, Std=15, Cap 0-100
                    z = (df.loc[valid_mask, p] - mean) / std
                    df.loc[valid_mask, f'{p}_norm'] = (z * 15 + 50).clip(0, 100)
                    
                # Fill missing with low score (penalty for not qualifying)
                df.loc[~valid_mask, f'{p}_norm'] = 25.0
            else:
                df[f'{p}_norm'] = 50.0 # Fallback
                
        # 3. Peak-Bias Weighting
        # ----------------------
        def calculate_weighted_score(row):
            scores = {
                'Friction': row['friction_norm'],
                'Crucible': row['crucible_norm'],
                'Evolution': row['evolution_norm'],
                'Dominance': row['dominance_norm'],
                'Versatility': row['versatility_norm']
            }
            
            # Sort by score (Dynamic weighting)
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            weights = [0.30, 0.25, 0.20, 0.15, 0.10]
            
            weighted_sum = 0.0
            for i, (name, score) in enumerate(sorted_scores):
                weighted_sum += score * weights[i]
                
            return pd.Series({
                'unified_score': weighted_sum,
                'primary_archetype': sorted_scores[0][0],
                'secondary_archetype': sorted_scores[1][0]
            })

        scores_df = df.apply(calculate_weighted_score, axis=1)
        final_df = pd.concat([df['player_id'], scores_df, df[[f'{p}_norm' for p in pathways]]], axis=1)
        
        return final_df.sort_values('unified_score', ascending=False)

def get_player_name(conn, player_id):
    cur = conn.cursor()
    cur.execute("SELECT player_name FROM players WHERE player_id = ?", (player_id,))
    res = cur.fetchone()
    return res[0] if res else str(player_id)

def main():
    """Test the Unified Framework with Batch Normalization."""
    calc = UnifiedCalculator(season="2023-24")
    
    # Test with a mix of stars and role players for distribution check
    test_ids = [
        203507, # Giannis
        201935, # Harden
        2544,   # LeBron
        203999, # Jokic
        1629029, # Luka
        1628378, # Bane (Role/Star bridge)
        1630162, # Anthony Edwards
        1628973, # Jalen Brunson
        1627750, # Jamal Murray
        201142, # Durant
        201939, # Curry
        1628369, # Tatum
    ]
    
    print(f"🚀 Unified Resilience Framework (2023-24) - Z-Score Normalized")
    print("===========================================================")
    
    results = calc.calculate_batch_scores(test_ids)
    
    conn = calc.get_db_connection()
    
    print(f"{'Player':<20} {'Score':<6} {'Primary Archetype':<20} {'Fric':<5} {'Cruc':<5} {'Evo':<5} {'Dom':<5} {'Vers':<5}")
    print("-" * 90)
    
    for _, row in results.iterrows():
        name = get_player_name(conn, row['player_id'])
        print(f"{name:<20} {row['unified_score']:<6.1f} {row['primary_archetype']:<20} "
              f"{row['friction_norm']:<5.0f} {row['crucible_norm']:<5.0f} {row['evolution_norm']:<5.0f} "
              f"{row['dominance_norm']:<5.0f} {row['versatility_norm']:<5.0f}")
              
    conn.close()

if __name__ == "__main__":
    main()

