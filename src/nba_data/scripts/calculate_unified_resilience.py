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

Uses pre-calculated CSVs for batch metrics (Friction, Crucible) to ensure consistency.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Dict, List, Optional

# Add the scripts directory to path
sys.path.append(str(Path(__file__).parent))
from calculate_dominance_score import calculate_player_sqav
from calculate_longitudinal_evolution import calculate_longitudinal_evolution
from calculate_extended_resilience import calculate_method_resilience

DB_PATH = "data/nba_stats.db"

class UnifiedCalculator:
    def __init__(self, season="2023-24"):
        self.season = season
        self.friction_map = self._load_friction_map()
        self.crucible_map = self._load_crucible_map()
        
    def _load_friction_map(self) -> Dict[int, float]:
        """Load Friction Resilience Scores from CSV."""
        path = f"data/friction_resilience_{self.season}.csv"
        try:
            df = pd.read_csv(path)
            # Ensure column exists
            if 'friction_resilience_score' not in df.columns:
                return {}
            return dict(zip(df['player_id'], df['friction_resilience_score']))
        except FileNotFoundError:
            print(f"⚠️ Warning: Friction file {path} not found. Run calculate_friction.py first.")
            return {}

    def _load_crucible_map(self) -> Dict[int, float]:
        """Load Crucible Resilience Scores from CSV."""
        path = f"data/crucible_resilience_{self.season}.csv"
        try:
            df = pd.read_csv(path)
            if 'crucible_resilience_score' not in df.columns:
                return {}
            return dict(zip(df['player_id'], df['crucible_resilience_score']))
        except FileNotFoundError:
            print(f"⚠️ Warning: Crucible file {path} not found. Run calculate_crucible_baseline.py first.")
            return {}

    def get_db_connection(self):
        return sqlite3.connect(DB_PATH)

    def calculate_score(self, player_id: int) -> Dict:
        """
        Calculate the Unified Extended Resilience Score for a player.
        """
        conn = self.get_db_connection()
        
        # 1. Fetch Component Scores
        # -------------------------
        
        # A. Friction Score (Pre-calculated)
        # Default to 50 (Average) if missing
        friction_score = self.friction_map.get(player_id, 50.0)
        
        # B. Crucible Score (Pre-calculated)
        crucible_score = self.crucible_map.get(player_id, 50.0)
        
        # C. Evolution (Multi-Season / Macro-Evolution)
        try:
            # Calculates based on full career history
            evo_data = calculate_longitudinal_evolution(player_id)
            evolution_score = evo_data.get('Adaptability_Score', 50.0)
        except:
            evolution_score = 50.0
            
        # D. Dominance (SQAV)
        # This script returns 0-100
        try:
            dominance_score = calculate_player_sqav(player_id, self.season, "Regular Season")
        except:
            dominance_score = 50.0
            
        # E. Versatility (Method Resilience)
        try:
            versatility_score = calculate_method_resilience(conn, "Regular Season", player_id)
        except:
            versatility_score = 50.0
            
        conn.close()
        
        # 2. Weighting Logic (The "Unified" Model)
        # ----------------------------------------
        
        scores = {
            'Friction': friction_score,
            'Crucible': crucible_score,
            'Evolution': evolution_score,
            'Dominance': dominance_score,
            'Versatility': versatility_score
        }
        
        # Equal weights for now, or based on philosophy?
        # Philosophy: Friction and Crucible are the hardest tests.
        # Let's use the Dynamic Peak-Bias Weighting from previous version.
        
        sorted_pathways = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        weights_config = [0.30, 0.25, 0.20, 0.15, 0.10] # Top strength matters most
        
        weighted_sum = 0.0
        final_weights = {}
        
        for idx, (pathway, score) in enumerate(sorted_pathways):
            weight = weights_config[idx]
            final_weights[pathway] = weight
            weighted_sum += score * weight
            
        return {
            'Player_ID': player_id,
            'Unified_Score': weighted_sum,
            'Pathway_Scores': scores,
            'Primary_Archetype': sorted_pathways[0][0],
            'Secondary_Archetype': sorted_pathways[1][0]
        }

def main():
    """Test the Unified Framework."""
    calc = UnifiedCalculator(season="2023-24")
    
    # Test Archetypes
    # Note: Player IDs must match 2023-24 roster
    archetypes = {
        203507: "Giannis Antetokounmpo",
        201935: "James Harden",
        2544: "LeBron James",
        203999: "Nikola Jokic",
        1629029: "Luka Doncic",
        1628378: "Desmond Bane" 
    }
    
    print(f"🚀 Unified Playoff Resilience Framework (2023-24)")
    print("===============================================")
    print(f"{'Player':<25} {'Score':<6} {'Archetype':<30}")
    print("-" * 70)
    
    for pid, name in archetypes.items():
        try:
            res = calc.calculate_score(pid)
            print(f"{name:<25} {res['Unified_Score']:<6.1f} {res['Primary_Archetype']} + {res['Secondary_Archetype']}")
            
            # Debug details
            # print(res['Pathway_Scores'])
        except Exception as e:
            print(f"{name:<25} ERROR: {e}")

if __name__ == "__main__":
    main()

