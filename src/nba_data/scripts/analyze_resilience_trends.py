#!/usr/bin/env python3
"""
Pre-Mortem Analysis Script

Purpose:
To detect potential failures in our resilience model by analyzing historical trends.
We want to ensure our "snapshot" analysis isn't missing critical career arcs.

Core Analysis:
1. Calculate Unified Resilience Score for EVERY season in the database (2015-2025)
2. Visualize the trajectory of resilience scores over time
3. Detect "False Positives" (Players who scored high but failed in playoffs)
4. Detect "False Negatives" (Players who scored low but succeeded)
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
from typing import Dict, List

# Add the scripts directory to path
sys.path.append(str(Path(__file__).parent))
from calculate_unified_resilience import calculate_unified_resilience, get_player_name

DB_PATH = "data/nba_stats.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def get_available_seasons(conn):
    """Get all available seasons from the database."""
    query = "SELECT DISTINCT season FROM player_season_stats ORDER BY season"
    return pd.read_sql_query(query, conn)['season'].tolist()

def calculate_multi_season_resilience(player_id: int) -> pd.DataFrame:
    """
    Calculate Unified Resilience Score for a player across ALL available seasons.
    """
    conn = get_db_connection()
    seasons = get_available_seasons(conn)
    conn.close()

    results = []

    print(f"\nAnalyzing Career Arc for Player {player_id}...")

    for season in seasons:
        try:
            # Note: calculate_unified_resilience currently defaults to 2024-25
            # We need to update it to accept a 'season' parameter to make this true multi-season.
            # For now, we will assume the underlying functions handle the season parameter if passed,
            # but looking at calculate_unified_resilience.py, it takes a 'season' arg!
            
            res = calculate_unified_resilience(player_id, season=season)
            
            results.append({
                'season': season,
                'unified_score': res['Unified_Score'],
                'versatility': res['Pathway_Scores']['Versatility'],
                'specialization': res['Pathway_Scores']['Specialization'],
                'scalability': res['Pathway_Scores']['Scalability'],
                'dominance': res['Pathway_Scores']['Dominance'],
                'evolution': res['Pathway_Scores']['Evolution'],
                'primary_archetype': res['Primary_Archetype']
            })
            print(f"  {season}: {res['Unified_Score']:.1f} ({res['Primary_Archetype']})")
            
        except Exception as e:
            # Some seasons might be missing data for a player (e.g. before they were drafted)
            # print(f"  Skipping {season}: {str(e)}")
            pass

    return pd.DataFrame(results)

def analyze_archetype_trends():
    """Run multi-season analysis for key archetypes."""
    archetypes = {
        203507: "Giannis Antetokounmpo",
        201935: "James Harden",
        2544: "LeBron James",
        203999: "Nikola Jokic",
        1629029: "Luka Doncic",
        201142: "Kevin Durant"
    }

    all_trends = {}

    for pid, name in archetypes.items():
        print(f"Processing {name}...")
        df = calculate_multi_season_resilience(pid)
        if not df.empty:
            all_trends[name] = df
            
            # Save individual player trend to CSV
            filename = f"data/trend_{name.replace(' ', '_').lower()}.csv"
            df.to_csv(filename, index=False)
            print(f"Saved trend data to {filename}")

    return all_trends

def main():
    print("🚀 Pre-Mortem Analysis: Multi-Season Resilience Trends")
    print("=====================================================")
    
    analyze_archetype_trends()

if __name__ == "__main__":
    main()

