#!/usr/bin/env python3
"""
Phase 3: Role Scalability Implementation

Measures a player's ability to maintain efficiency when usage increases in the playoffs.
This addresses the "Butler problem" where players excel under expanded roles.

Key Components:
- Usage tier segmentation (low/medium/high/very high)
- Efficiency slope analysis across usage rates
- Playoff usage change measurement
- Role scalability score calculation
"""

import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List
from pathlib import Path
from sklearn.linear_model import LinearRegression

DB_PATH = "data/nba_stats.db"

def get_db_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def define_usage_tiers() -> Dict[str, Tuple[float, float]]:
    """
    Define usage rate tiers for scalability analysis.

    Returns:
        Dict mapping tier names to (min_usage, max_usage) tuples.
        Very High tier has no upper bound.
    """
    return {
        'Low': (0.0, 0.20),
        'Medium': (0.20, 0.25),
        'High': (0.25, 0.30),
        'Very High': (0.30, 1.0)  # No upper bound
    }

def calculate_player_usage_efficiency(player_id: int, season: str = "2024-25") -> Dict[str, float]:
    """
    Calculate player's usage rate and efficiency for regular season and playoffs.

    Since we don't have game-by-game data, we use season-aggregated metrics
    to assess scalability through usage changes between regular season and playoffs.

    Returns dict with usage rates and efficiency metrics for both seasons.
    """
    conn = get_db_connection()

    # Get regular season usage and efficiency
    reg_query = f"""
        SELECT
            usage_percentage,
            true_shooting_percentage as ts_pct,
            offensive_rating as ortg,
            effective_field_goal_percentage as efg_pct
        FROM player_advanced_stats
        WHERE player_id = {player_id}
          AND season = '{season}'
    """

    # Get playoff usage and efficiency
    playoff_query = f"""
        SELECT
            usage_percentage,
            true_shooting_percentage as ts_pct,
            offensive_rating as ortg,
            effective_field_goal_percentage as efg_pct
        FROM player_playoff_advanced_stats
        WHERE player_id = {player_id}
          AND season = '{season}'
    """

    reg_data = pd.read_sql_query(reg_query, conn)
    playoff_data = pd.read_sql_query(playoff_query, conn)
    conn.close()

    result = {
        'regular_season': {},
        'playoffs': {}
    }

    # Extract regular season data
    if not reg_data.empty:
        row = reg_data.iloc[0]
        result['regular_season'] = {
            'usage_pct': row['usage_percentage'] or 0,
            'ts_pct': row['ts_pct'] or 0,
            'ortg': row['ortg'] or 0,
            'efg_pct': row['efg_pct'] or 0
        }
    else:
        result['regular_season'] = {k: 0 for k in ['usage_pct', 'ts_pct', 'ortg', 'efg_pct']}

    # Extract playoff data
    if not playoff_data.empty:
        row = playoff_data.iloc[0]
        result['playoffs'] = {
            'usage_pct': row['usage_percentage'] or 0,
            'ts_pct': row['ts_pct'] or 0,
            'ortg': row['ortg'] or 0,
            'efg_pct': row['efg_pct'] or 0
        }
    else:
        result['playoffs'] = {k: 0 for k in ['usage_pct', 'ts_pct', 'ortg', 'efg_pct']}

    return result

def calculate_scalability_from_usage_change(usage_efficiency_data: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Calculate scalability based on usage changes between regular season and playoffs.

    This simplified approach assesses how well players maintain efficiency when their
    usage rate changes from regular season to playoffs.

    Returns dict with scalability metrics.
    """
    reg = usage_efficiency_data['regular_season']
    playoff = usage_efficiency_data['playoffs']

    # Calculate usage change
    usage_change = playoff['usage_pct'] - reg['usage_pct']
    if reg['usage_pct'] > 0:
        usage_change_pct = (usage_change / reg['usage_pct'] * 100)
    elif playoff['usage_pct'] > 0:
        usage_change_pct = 100.0  # Went from 0 to some usage
    else:
        usage_change_pct = 0.0  # Both are 0

    # Calculate efficiency change (handle NaN values)
    ts_change = (playoff['ts_pct'] - reg['ts_pct']) if (not np.isnan(playoff['ts_pct']) and not np.isnan(reg['ts_pct'])) else 0.0
    ortg_change = (playoff['ortg'] - reg['ortg']) if (not np.isnan(playoff['ortg']) and not np.isnan(reg['ortg'])) else 0.0

    # Scalability assessment
    scalability_score = 50.0  # Start with neutral score

    if usage_change > 0.02:  # Usage increased significantly (>2 percentage points)
        # Player shouldered more responsibility - how did efficiency hold up?
        if ts_change >= -2:  # Maintained or improved TS%
            scalability_score += 20
        elif ts_change >= -5:  # Minor decline
            scalability_score += 10
        else:  # Significant decline
            scalability_score -= 10

        if ortg_change >= -2:  # Maintained offensive rating
            scalability_score += 15
        elif ortg_change >= -5:
            scalability_score += 5
        else:
            scalability_score -= 15

    elif usage_change < -0.02:  # Usage decreased significantly
        # Less responsibility - efficiency should improve or stay same
        if ts_change > 1:  # Improved with less usage
            scalability_score += 25
        elif ts_change > -1:  # Maintained efficiency
            scalability_score += 15
        else:  # Declined with less usage (concerning)
            scalability_score -= 10

    else:  # Usage stayed similar
        # Consistency is valuable but doesn't demonstrate scalability
        scalability_score += 5

    # Clamp to 0-100 range
    scalability_score = max(0, min(100, scalability_score))

    return {
        'scalability_score': scalability_score,
        'usage_change': usage_change,
        'usage_change_pct': usage_change_pct,
        'ts_change': ts_change,
        'ortg_change': ortg_change,
        'regular_usage': reg['usage_pct'],
        'playoff_usage': playoff['usage_pct'],
        'regular_ts': reg['ts_pct'],
        'playoff_ts': playoff['ts_pct']
    }

def calculate_role_scalability_score(player_id: int, season: str = "2024-25") -> Dict[str, any]:
    """
    Calculate comprehensive role scalability score for a player.

    This simplified implementation uses season-aggregated data to assess how well
    players maintain efficiency when their usage changes from regular season to playoffs.

    Returns dict with scalability metrics and final score.
    """
    # Get usage and efficiency data for both seasons
    usage_efficiency_data = calculate_player_usage_efficiency(player_id, season)

    # Check if we have valid data
    if (usage_efficiency_data['regular_season']['usage_pct'] == 0 and
        usage_efficiency_data['playoffs']['usage_pct'] == 0):
        return {
            'scalability_score': 0.0,
            'usage_change': 0.0,
            'usage_change_pct': 0.0,
            'ts_change': 0.0,
            'ortg_change': 0.0,
            'regular_usage': 0.0,
            'playoff_usage': 0.0,
            'regular_ts': 0.0,
            'playoff_ts': 0.0,
            'data_quality': 'insufficient_data'
        }

    # Calculate scalability from usage changes
    scalability_metrics = calculate_scalability_from_usage_change(usage_efficiency_data)

    return {
        'scalability_score': scalability_metrics['scalability_score'],
        'usage_change': scalability_metrics['usage_change'],
        'usage_change_pct': scalability_metrics['usage_change_pct'],
        'ts_change': scalability_metrics['ts_change'],
        'ortg_change': scalability_metrics['ortg_change'],
        'regular_usage': scalability_metrics['regular_usage'],
        'playoff_usage': scalability_metrics['playoff_usage'],
        'regular_ts': scalability_metrics['regular_ts'],
        'playoff_ts': scalability_metrics['playoff_ts'],
        'data_quality': 'good' if scalability_metrics['regular_usage'] > 0 else 'limited'
    }


def get_player_name(player_id: int) -> str:
    """Get player name for display purposes."""
    conn = get_db_connection()
    query = f"SELECT player_name FROM players WHERE player_id = {player_id}"
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result.iloc[0]['player_name'] if not result.empty else f"Player {player_id}"

def calculate_scalability_scores_batch(player_ids: List[int], season: str = "2024-25") -> pd.DataFrame:
    """
    Calculate role scalability scores for multiple players.

    Returns DataFrame with player_id, name, and scalability metrics.
    """
    results = []

    for player_id in player_ids:
        try:
            scalability_data = calculate_role_scalability_score(player_id, season)
            player_name = get_player_name(player_id)

            results.append({
                'player_id': player_id,
                'player_name': player_name,
                'scalability_score': round(scalability_data['scalability_score'], 2),
                'usage_change': round(scalability_data['usage_change'], 3),
                'usage_change_pct': round(scalability_data['usage_change_pct'], 1),
                'ts_change': round(scalability_data['ts_change'], 1),
                'ortg_change': round(scalability_data['ortg_change'], 1),
                'regular_usage': round(scalability_data['regular_usage'], 3),
                'playoff_usage': round(scalability_data['playoff_usage'], 3),
                'regular_ts': round(scalability_data['regular_ts'], 1),
                'playoff_ts': round(scalability_data['playoff_ts'], 1),
                'data_quality': scalability_data['data_quality']
            })

            print(f"✓ {player_name}: Scalability {scalability_data['scalability_score']:.1f}, Usage Δ {scalability_data['usage_change_pct']:+.1f}%")

        except Exception as e:
            print(f"✗ Error calculating for player {player_id}: {e}")

    return pd.DataFrame(results)

def main():
    """Main function for Phase 3 Role Scalability implementation."""

    # Test on archetype players - focusing on those expected to show different scalability patterns
    archetype_players = {
        202710: "Jimmy Butler",    # Should score high on scalability (maintains efficiency at high usage)
        201935: "James Harden",    # Should score moderate (versatile but usage dependent)
        2544: "LeBron James",      # Should score high (maintains efficiency across usage ranges)
        1629029: "Luka Dončić",   # Should score moderate (high usage star)
        203076: "Anthony Davis",   # Should show different scalability patterns
        2397: "Shaq",            # Should score lower (post-dependent, less scalable)
        2207: "Dirk Nowitzki"    # Should score moderate (stretch four role changes)
    }

    print("🚀 Phase 3: Role Scalability Implementation")
    print("Measuring efficiency maintenance when usage increases")
    print("=" * 70)

    print("\nCalculating role scalability scores for archetype players...")
    player_ids = list(archetype_players.keys())
    results = calculate_scalability_scores_batch(player_ids)

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    for _, row in results.iterrows():
        print(f"\n{row['player_name']} ({archetype_players.get(row['player_id'], 'Unknown')}):")
        print(f"  Scalability Score: {row['scalability_score']:.1f}/100")
        print(f"  Usage Change: {row['regular_usage']:.1%} → {row['playoff_usage']:.1%} ({row['usage_change_pct']:+.1f}%)")
        print(f"  TS% Change: {row['regular_ts']:.1f}% → {row['playoff_ts']:.1f}% ({row['ts_change']:+.1f})")
        print(f"  ORTG Change: {row['ortg_change']:+.1f}")
        print(f"  Data Quality: {row['data_quality']}")

    # Save results
    results.to_csv("data/role_scalability_scores_phase3.csv", index=False)
    print(f"\nResults saved to data/role_scalability_scores_phase3.csv")

    print("\n" + "=" * 70)
    print("✅ Phase 3 Complete: Role Scalability Operational!")
    print("Next: Phase 4 (Longitudinal Evolution) and Phase 5 (Unified Framework)")
    print("=" * 70)

if __name__ == "__main__":
    main()
