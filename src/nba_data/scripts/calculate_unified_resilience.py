#!/usr/bin/env python3
"""
Unified Playoff Resilience Calculator - Phase 5 Integration

Combines all five resilience pathways into a single "Extended Playoff Resilience Score":
1. Versatility Resilience (Method Diversity)
2. Specialization (Primary Method Mastery)
3. Role Scalability (Usage Adaptability)
4. Dominance Resilience (Shot Quality-Adjusted Value)
5. Longitudinal Evolution (Career Adaptability)

Uses dynamic archetype-based weighting to generate a final predictive score.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Dict, List

# Add the scripts directory to path
sys.path.append(str(Path(__file__).parent))
from calculate_dominance_score import calculate_player_sqav
from calculate_primary_method_mastery import calculate_primary_method_mastery
from calculate_role_scalability import calculate_role_scalability_score
from calculate_longitudinal_evolution import calculate_longitudinal_evolution
from calculate_extended_resilience import calculate_method_resilience

DB_PATH = "data/nba_stats.db"

def get_db_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def normalize_score(score: float, min_val: float = 0, max_val: float = 100) -> float:
    """Normalize score to 0-100 range."""
    return max(min((score - min_val) / (max_val - min_val) * 100, 100), 0)

def calculate_unified_resilience(player_id: int, season: str = "2024-25") -> Dict:
    """
    Calculate the Unified Extended Resilience Score.
    
    Returns:
        Dict containing individual pathway scores, weights used, and final unified score.
    """
    conn = get_db_connection()
    
    # 1. Calculate Raw Scores for All 5 Pathways
    # ------------------------------------------
    
    # Pathway 1: Versatility (Method Resilience)
    # Uses regular season for baseline capability
    raw_versatility = calculate_method_resilience(conn, "Regular Season", player_id)
    
    # Pathway 2: Specialization (Primary Method Mastery)
    mastery_data = calculate_primary_method_mastery(player_id, season)
    raw_mastery = mastery_data.get('primary_method_mastery', 0.0)
    
    # Pathway 3: Scalability (Role Scalability)
    scalability_data = calculate_role_scalability_score(player_id, season)
    raw_scalability = scalability_data.get('scalability_score', 0.0)
    
    # Pathway 4: Dominance (SQAV)
    # SQAV is often small (e.g. +0.15), need to normalize to 0-100 scale roughly
    # Assuming calculate_player_sqav returns a normalized 0-100 score based on previous files
    raw_dominance = calculate_player_sqav(player_id, season, "Regular Season")
    
    # Pathway 5: Evolution (Longitudinal Adaptability)
    evolution_data = calculate_longitudinal_evolution(player_id)
    raw_evolution = evolution_data.get('Adaptability_Score', 0.0)
    
    conn.close()
    
    # 2. Dynamic Weighting (Archetype Identification)
    # -----------------------------------------------
    
    scores = {
        'Versatility': raw_versatility,
        'Specialization': raw_mastery,
        'Scalability': raw_scalability,
        'Dominance': raw_dominance,
        'Evolution': raw_evolution
    }
    
    # Sort pathways by strength (descending)
    sorted_pathways = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Assign weights based on rank (Peak-Bias Weighting)
    # We reward the player's strengths while maintaining a holistic view.
    # Rank 1: 35% (Primary Archetype)
    # Rank 2: 25% (Secondary Strength)
    # Rank 3: 20%
    # Rank 4: 10%
    # Rank 5: 10%
    
    weights_config = [0.35, 0.25, 0.20, 0.10, 0.10]
    
    final_weights = {}
    weighted_sum = 0.0
    
    primary_archetype = sorted_pathways[0][0]
    secondary_archetype = sorted_pathways[1][0]
    
    for idx, (pathway, score) in enumerate(sorted_pathways):
        weight = weights_config[idx]
        final_weights[pathway] = weight
        weighted_sum += score * weight
        
    unified_score = weighted_sum
    
    return {
        'Player_ID': player_id,
        'Unified_Score': unified_score,
        'Primary_Archetype': primary_archetype,
        'Secondary_Archetype': secondary_archetype,
        'Pathway_Scores': scores,
        'Pathway_Weights': final_weights
    }

def get_player_name(player_id: int) -> str:
    """Get player name for display purposes."""
    conn = get_db_connection()
    try:
        query = f"SELECT player_name FROM players WHERE player_id = {player_id}"
        result = pd.read_sql_query(query, conn)
        return result.iloc[0]['player_name'] if not result.empty else f"Player {player_id}"
    finally:
        conn.close()

def main():
    """Test the Unified Framework."""
    
    # Test Archetypes
    archetypes = {
        203507: "Giannis Antetokounmpo", # Evolution + Dominance
        201935: "James Harden",          # Dominance + Versatility
        2544: "LeBron James",            # Scalability + Versatility + Evolution
        203999: "Nikola Jokic",          # Versatility + Mastery
        203076: "Anthony Davis",         # Mastery + Dominance
        1629029: "Luka Doncic",          # Versatility + Scalability
        201142: "Kevin Durant"           # Mastery + Dominance
    }
    
    print("🚀 Unified Playoff Resilience Framework (Phase 5)")
    print("===============================================")
    print(f"{'Player':<25} {'Score':<6} {'Archetype (Primary + Secondary)':<40}")
    print("-" * 75)
    
    results_list = []
    
    for pid, name in archetypes.items():
        try:
            res = calculate_unified_resilience(pid)
            score = res['Unified_Score']
            p_arch = res['Primary_Archetype']
            s_arch = res['Secondary_Archetype']
            
            print(f"{name:<25} {score:<6.1f} {p_arch} + {s_arch}")
            
            # Print detailed breakdown for debugging
            # print(f"   Breakdown: {res['Pathway_Scores']}")
            # print(f"   Weights:   {res['Pathway_Weights']}")
            
            results_list.append({
                'name': name,
                'score': score,
                'primary': p_arch,
                'secondary': s_arch,
                'details': res
            })
            
        except Exception as e:
            print(f"{name:<25} ERROR  {str(e)}")
            import traceback
            traceback.print_exc()

    print("\nDetailed Pathway Analysis:")
    print("=" * 75)
    for r in results_list:
        print(f"\n{r['name']} (Score: {r['score']:.1f})")
        scores = r['details']['Pathway_Scores']
        weights = r['details']['Pathway_Weights']
        
        # Sort by weight to show primary drivers first
        sorted_pathways = sorted(scores.keys(), key=lambda k: weights[k], reverse=True)
        
        for p in sorted_pathways:
            print(f"  {p:<15}: {scores[p]:5.1f} (Weight: {weights[p]*100:.0f}%)")

if __name__ == "__main__":
    main()

