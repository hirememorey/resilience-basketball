#!/usr/bin/env python3
"""
Extended Playoff Resilience Calculator - Phase 1 Integration

Combines Method Resilience (versatility) with Dominance Score (SQAV) for comprehensive
multi-pathway playoff resilience analysis.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Dict

# Add the scripts directory to path so we can import the dominance calculator
sys.path.append(str(Path(__file__).parent))
from calculate_dominance_score import calculate_player_sqav

DB_PATH = "data/nba_stats.db"
PLAYER_ID = 201935  # James Harden

def get_db_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def define_court_zones(df: pd.DataFrame) -> pd.Series:
    """Categorizes shots into predefined court zones based on x, y coordinates."""
    x, y = df['loc_x'], df['loc_y']
    is_ra = (x.abs() <= 4) & (y <= 4.25)
    is_paint = (x.abs() <= 8) & (y <= 19) & ~is_ra
    is_mid_range = (
        ((x.abs() > 8) & (y <= 19)) |
        ((x.abs() <= 22) & (y > 19)) |
        (df['shot_type'] == '2PT Field Goal') & ~is_ra & ~is_paint
    )
    is_corner_3 = (x.abs() > 22) & (y <= 7.8)
    is_above_break_3 = (df['shot_type'] == '3PT Field Goal') & ~is_corner_3

    conditions = [
        is_ra, is_paint, is_mid_range,
        (is_corner_3) & (x < 0), (is_corner_3) & (x >= 0),
        is_above_break_3
    ]
    choices = [
        'Restricted Area', 'In The Paint (Non-RA)', 'Mid-Range',
        'Left Corner 3', 'Right Corner 3', 'Above the Break 3'
    ]
    return pd.Series(np.select(conditions, choices, default='Other'), index=df.index)

def calculate_hhi(series: pd.Series) -> float:
    """Calculates the Herfindahl-Hirschman Index (HHI) for a given series."""
    proportions = series / series.sum()
    return (proportions ** 2).sum()

def calculate_diversity_score(series: pd.Series) -> float:
    """Converts HHI into a diversity score from 0 to 100."""
    if series.sum() == 0:
        return 0
    return (1 - calculate_hhi(series)) * 100

def calculate_spatial_diversity(conn: sqlite3.Connection, season_type: str) -> float:
    """Calculate spatial diversity using shot location data."""
    st_query = season_type
    query = f"""
        SELECT loc_x, loc_y, shot_made_flag, shot_type
        FROM player_shot_locations
        WHERE player_id = {PLAYER_ID} AND season = '2024-25' AND season_type = '{st_query}'
    """
    df = pd.read_sql_query(query, conn)
    if df.empty: return 0

    df['zone'] = define_court_zones(df)
    zone_attempts = df['zone'].value_counts()
    zone_makes_df = df[df['shot_made_flag'] == 1]
    zone_makes = zone_makes_df['zone'].value_counts()
    three_pm = zone_makes_df[zone_makes_df['shot_type'] == '3PT Field Goal']['zone'].value_counts()

    stats = pd.DataFrame({'attempts': zone_attempts, 'makes': zone_makes, '3pm': three_pm}).fillna(0)
    stats['efg'] = (stats['makes'] + 0.5 * stats['3pm']) / stats['attempts']

    # Simple efficiency weighting for now (can be enhanced with league averages)
    stats['weighted_volume'] = stats['attempts'] * stats['efg'].fillna(0.4)
    return calculate_diversity_score(stats['weighted_volume'])

def calculate_play_type_diversity(conn: sqlite3.Connection, season_type: str) -> float:
    """Calculate play-type diversity using synergy stats."""
    table = "player_playtype_stats" if season_type == "Regular Season" else "player_playoff_playtype_stats"
    query = f"""
        SELECT play_type, possessions, points_per_possession
        FROM {table}
        WHERE player_id = {PLAYER_ID} AND season = '2024-25'
    """
    df = pd.read_sql_query(query, conn)
    if df.empty: return 0

    # Weight by efficiency (can be enhanced with league averages)
    df['weighted_volume'] = df['possessions'] * df['points_per_possession'].fillna(0.9)
    return calculate_diversity_score(df.set_index('play_type')['weighted_volume'])

def calculate_creation_diversity(conn: sqlite3.Connection, season_type: str) -> float:
    """Calculate creation method diversity using tracking stats."""
    table = "player_tracking_stats" if season_type == "Regular Season" else "player_playoff_tracking_stats"
    query = f"SELECT * FROM {table} WHERE player_id = {PLAYER_ID} AND season = '2024-25'"
    df = pd.read_sql_query(query, conn)
    if df.empty: return 0

    df = df.iloc[0]

    # Extract creation metrics
    cs_attempts = df['catch_shoot_field_goals_attempted']
    cs_efg = df['catch_shoot_effective_field_goal_percentage']

    pu_attempts = df['pull_up_field_goals_attempted']
    pu_efg = df['pull_up_effective_field_goal_percentage']

    drives = df['drives']
    drive_pts = df['drive_points']
    drive_ppd = (drive_pts / drives) if drives else 0

    creation_data = pd.DataFrame([
        {'type': 'Catch & Shoot', 'volume': cs_attempts, 'efficiency': cs_efg},
        {'type': 'Pull-Up', 'volume': pu_attempts, 'efficiency': pu_efg},
        {'type': 'Drives', 'volume': drives, 'efficiency': drive_ppd}
    ]).set_index('type')

    creation_data['weighted_volume'] = creation_data['volume'] * creation_data['efficiency'].fillna(0.4)
    return calculate_diversity_score(creation_data['weighted_volume'])

def calculate_method_resilience(conn: sqlite3.Connection, season_type: str) -> float:
    """Calculate overall method resilience (versatility score)."""
    spatial = calculate_spatial_diversity(conn, season_type)
    play_type = calculate_play_type_diversity(conn, season_type)
    creation = calculate_creation_diversity(conn, season_type)

    weights = {'spatial': 0.4, 'play_type': 0.4, 'creation': 0.2}
    return (spatial * weights['spatial'] +
            play_type * weights['play_type'] +
            creation * weights['creation'])

def calculate_extended_resilience(player_id: int, season: str = "2024-25") -> Dict[str, float]:
    """
    Calculate extended playoff resilience combining multiple pathways.

    Returns comprehensive resilience metrics including:
    - Method Resilience (versatility)
    - Dominance Score (SQAV)
    - Overall Extended Resilience Score
    """
    global PLAYER_ID
    PLAYER_ID = player_id  # Update global for helper functions

    conn = get_db_connection()

    results = {}

    for season_type in ["Regular Season", "Playoffs"]:
        # Calculate Method Resilience (versatility)
        method_resilience = calculate_method_resilience(conn, season_type)

        # Calculate Dominance Score (SQAV)
        dominance_score = calculate_player_sqav(player_id, season, season_type)

        # Combined Extended Resilience Score (Phase 1: equal weighting)
        extended_score = (method_resilience * 0.6) + (dominance_score * 0.4)

        results[season_type] = {
            'Method_Resilience': method_resilience,
            'Dominance_Score': dominance_score,
            'Extended_Resilience': extended_score
        }

    conn.close()

    # Calculate resilience deltas
    results['Resilience_Delta'] = {
        'Method_Resilience_Delta': (results['Playoffs']['Method_Resilience'] -
                                   results['Regular Season']['Method_Resilience']),
        'Dominance_Delta': (results['Playoffs']['Dominance_Score'] -
                           results['Regular Season']['Dominance_Score']),
        'Extended_Resilience_Delta': (results['Playoffs']['Extended_Resilience'] -
                                     results['Regular Season']['Extended_Resilience'])
    }

    return results

def get_player_name(player_id: int) -> str:
    """Get player name for display purposes."""
    conn = get_db_connection()
    query = f"SELECT player_name FROM players WHERE player_id = {player_id}"
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result.iloc[0]['player_name'] if not result.empty else f"Player {player_id}"

def main():
    """Main function demonstrating extended resilience calculator."""

    # Test on archetype players
    archetype_players = {
        201935: "James Harden",  # Should excel in dominance
        2544: "LeBron James",    # Should excel in versatility + dominance
        1629029: "Luka Dončić", # Should excel in versatility
        203076: "Anthony Davis"  # Should excel in dominance
    }

    print("🚀 Extended Playoff Resilience Calculator - Phase 1 Integration")
    print("=" * 70)

    for player_id, expected_profile in archetype_players.items():
        player_name = get_player_name(player_id)
        print(f"\n{player_name} ({expected_profile})")
        print("-" * 50)

        try:
            results = calculate_extended_resilience(player_id)

            for season_type, metrics in results.items():
                if season_type != 'Resilience_Delta':
                    print(f"{season_type}:")
                    for metric, value in metrics.items():
                        print(f"{metric}: {value:.2f}")
                    print()

            # Show deltas
            print("Resilience Deltas (Playoffs - Regular Season):")
            for metric, delta in results['Resilience_Delta'].items():
                print(f"{metric}: {delta:+.2f}")

        except Exception as e:
            print(f"Error calculating for {player_name}: {e}")

    print("\n" + "=" * 70)
    print("Phase 1 Complete: Multi-pathway resilience analysis operational!")
    print("Next: Phase 2 (Primary Method Mastery) and Phase 3 (Role Scalability)")

if __name__ == "__main__":
    main()
