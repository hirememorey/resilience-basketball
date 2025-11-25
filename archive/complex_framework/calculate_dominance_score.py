#!/usr/bin/env python3
"""
Phase 1: Dominance Score (SQAV) Implementation

Calculates Shot Quality-Adjusted Value for NBA players using comprehensive shot context data.
This addresses the "Harden problem" by measuring true shot-making dominance under contest.
"""

import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from pathlib import Path

DB_PATH = "data/nba_stats.db"

def get_db_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def calculate_league_baselines(season: str = "2024-25", season_type: str = "Regular Season") -> pd.DataFrame:
    """
    Calculate league-average eFG% baselines for defender distance contexts.

    Based on data structure analysis, defender distance data is available as separate records.
    This provides the most relevant context for measuring shot-making under contest.

    Returns DataFrame with columns:
    - close_def_dist_range
    - league_avg_efg
    - total_attempts (for statistical reliability)
    """
    conn = get_db_connection()

    # Focus on defender distance data (most relevant for contest/dominance)
    query = f"""
        SELECT
            close_def_dist_range,
            SUM(fgm + 0.5 * fg3m) as total_points,
            SUM(fga) as total_attempts,
            SUM(fgm + 0.5 * fg3m) / NULLIF(SUM(fga), 0) as league_avg_efg
        FROM player_shot_dashboard_stats
        WHERE season = '{season}'
          AND close_def_dist_range != ''
          AND fga > 0
        GROUP BY close_def_dist_range
        HAVING total_attempts >= 50  -- Minimum sample size for reliability
        ORDER BY close_def_dist_range
    """

    baselines = pd.read_sql_query(query, conn)
    conn.close()

    print(f"✅ Calculated {len(baselines)} league baseline contexts (defender distance)")
    print(f"   Total attempts across all contexts: {baselines['total_attempts'].sum():,}")

    return baselines

def calculate_player_sqav(player_id: int, season: str = "2024-25",
                        season_type: str = "Regular Season") -> float:
    """
    Calculate Shot Quality-Adjusted Value (SQAV) for a single player.

    Phase 1 Implementation: Focus on defender distance as primary contest indicator.
    SQAV = Σ (eFG_vs_Expected × Attempts × Difficulty_Multiplier)
    """
    conn = get_db_connection()

    # Get player's defender distance shot data
    player_query = f"""
        SELECT
            close_def_dist_range,
            fgm, fga, fg3m, fg3a,
            efg_pct as player_efg
        FROM player_shot_dashboard_stats
        WHERE player_id = {player_id}
          AND season = '{season}'
          AND close_def_dist_range != ''
          AND fga > 0
    """

    player_data = pd.read_sql_query(player_query, conn)
    conn.close()

    if player_data.empty:
        return 0.0

    # Get league baselines for defender distance
    baselines = calculate_league_baselines(season, season_type)
    baselines_dict = baselines.set_index('close_def_dist_range')['league_avg_efg'].to_dict()

    # Calculate SQAV for each defender distance context
    sqav_components = []

    for _, row in player_data.iterrows():
        defender_dist = row['close_def_dist_range']

        if defender_dist in baselines_dict:
            league_avg = baselines_dict[defender_dist]
            player_efg = row['player_efg']
            attempts = row['fga']

            # eFG% above expected (handle null/zero cases)
            if pd.isna(player_efg) or player_efg == 0:
                continue

            efg_above_expected = player_efg - league_avg

            # Difficulty multiplier based on defender distance
            difficulty_multiplier = get_difficulty_multiplier(defender_dist)

            # SQAV contribution for this context
            context_sqav = efg_above_expected * attempts * difficulty_multiplier
            sqav_components.append(context_sqav)

    # Aggregate to final SQAV score
    if sqav_components:
        total_sqav = sum(sqav_components)
        # Normalize to 0-100 scale using sigmoid-like transformation
        # This maps the raw SQAV score to an intuitive 0-100 scale
        normalized_sqav = 1 / (1 + np.exp(-total_sqav / 100)) * 100
        return max(0, min(100, normalized_sqav))  # Clamp to 0-100

    return 0.0

def get_difficulty_multiplier(defender_distance: str) -> float:
    """
    Assign difficulty multipliers based on defender distance.
    Higher multipliers for tougher shots (closer defenders).
    """
    multipliers = {
        '0-2 Feet - Very Tight': 1.5,
        '2-4 Feet - Tight': 1.3,
        '4-6 Feet - Open': 1.1,
        '6+ Feet - Wide Open': 1.0
    }
    return multipliers.get(defender_distance, 1.0)

def get_player_name(player_id: int) -> str:
    """Get player name for display purposes."""
    conn = get_db_connection()
    query = f"SELECT player_name FROM players WHERE player_id = {player_id}"
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result.iloc[0]['player_name'] if not result.empty else f"Player {player_id}"

def calculate_dominance_scores_batch(player_ids: list, season: str = "2024-25") -> pd.DataFrame:
    """
    Calculate dominance scores for multiple players.
    Returns DataFrame with player_id, name, and dominance_score.
    """
    results = []

    for player_id in player_ids:
        try:
            dominance_score = calculate_player_sqav(player_id, season)
            player_name = get_player_name(player_id)
            results.append({
                'player_id': player_id,
                'player_name': player_name,
                'dominance_score': round(dominance_score, 2)
            })
            print(f"✓ {player_name}: {dominance_score:.2f}")
        except Exception as e:
            print(f"✗ Error calculating for player {player_id}: {e}")

    return pd.DataFrame(results)

def main():
    """Main function for Phase 1 Dominance Score implementation."""

    # Test on archetype players
    archetype_players = {
        201935: "James Harden",  # Should score high on dominance
        2544: "LeBron James",    # Should score high on versatility/dominance
        1629029: "Luka Doncic", # Should score high on versatility
        203076: "Anthony Davis"  # Should score high on dominance
    }

    print("🚀 Phase 1: Dominance Score (SQAV) Implementation")
    print("=" * 60)

    # Calculate league baselines first
    print("\nCalculating league baselines...")
    baselines = calculate_league_baselines()
    print(f"   Contexts available: {len(baselines)}")
    print("   Sample baselines:")
    print(baselines.head())

    # Calculate dominance scores for archetype players
    print("\nCalculating dominance scores for archetype players...")
    player_ids = list(archetype_players.keys())
    results = calculate_dominance_scores_batch(player_ids)

    print("\nResults:")
    print("=" * 60)
    for _, row in results.iterrows():
        print(".2f")

    # Save results
    results.to_csv("data/dominance_scores_phase1.csv", index=False)
    print("\nResults saved to data/dominance_scores_phase1.csv")
if __name__ == "__main__":
    main()
