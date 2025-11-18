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

# Add the scripts directory to path so we can import calculators
sys.path.append(str(Path(__file__).parent))
from calculate_dominance_score import calculate_player_sqav
from calculate_primary_method_mastery import calculate_primary_method_mastery
from calculate_role_scalability import calculate_role_scalability_score

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

    Phase 1-3 Integration: Method Resilience, Dominance Score, Primary Method Mastery, and Role Scalability

    Returns comprehensive resilience metrics including:
    - Method Resilience (versatility)
    - Dominance Score (SQAV)
    - Primary Method Mastery (specialization)
    - Role Scalability (usage adaptability)
    - Overall Extended Resilience Score
    """
    global PLAYER_ID
    PLAYER_ID = player_id  # Update global for helper functions

    conn = get_db_connection()

    results = {}

    # Calculate Primary Method Mastery (works across both seasons)
    mastery_data = calculate_primary_method_mastery(player_id, season)

    for season_type in ["Regular Season", "Playoffs"]:
        # Calculate Method Resilience (versatility)
        method_resilience = calculate_method_resilience(conn, season_type)

        # Calculate Dominance Score (SQAV)
        dominance_score = calculate_player_sqav(player_id, season, season_type)

        # Calculate Role Scalability (only meaningful for playoffs, but calculate for both for consistency)
        scalability_data = calculate_role_scalability_score(player_id, season)

        # Combined Extended Resilience Score (Phase 1-3: four pathways)
        # Method Resilience (30%), Dominance Score (25%), Primary Method Mastery (20%), Role Scalability (25%)
        extended_score = (method_resilience * 0.3) + (dominance_score * 0.25) + (mastery_data['primary_method_mastery'] * 0.2) + (scalability_data['scalability_score'] * 0.25)

        results[season_type] = {
            'Method_Resilience': method_resilience,
            'Dominance_Score': dominance_score,
            'Primary_Method_Mastery': mastery_data['primary_method_mastery'],
            'Role_Scalability': scalability_data['scalability_score'],
            'Extended_Resilience': extended_score
        }

    conn.close()

    # Calculate resilience deltas
    results['Resilience_Delta'] = {
        'Method_Resilience_Delta': (results['Playoffs']['Method_Resilience'] -
                                   results['Regular Season']['Method_Resilience']),
        'Dominance_Delta': (results['Playoffs']['Dominance_Score'] -
                           results['Regular Season']['Dominance_Score']),
        'Primary_Method_Mastery_Delta': 0.0,  # Mastery is calculated consistently
        'Role_Scalability_Delta': 0.0,  # Scalability is calculated consistently across seasons
        'Extended_Resilience_Delta': (results['Playoffs']['Extended_Resilience'] -
                                     results['Regular Season']['Extended_Resilience'])
    }

    # Add pathway details
    results['Pathway_Details'] = {
        'Primary_Method_Mastery_Base': mastery_data['base_efficiency_score'],
        'Primary_Method_Mastery_Resistance': mastery_data['playoff_resistance'],
        'Primary_Methods': mastery_data['primary_methods']
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
        201935: "James Harden",      # Should excel in versatility + dominance
        2544: "LeBron James",        # Should excel in versatility + mastery
        1629029: "Luka Dončić",     # Should excel in versatility
        203076: "Anthony Davis",    # Should excel in dominance + mastery
        2397: "Shaq",              # Should excel in primary method mastery
        2207: "Dirk Nowitzki"      # Should excel in primary method mastery
    }

    print("🚀 Extended Playoff Resilience Calculator - Phase 1-3 Integration")
    print("Four Pathways: Versatility + Dominance + Primary Method Mastery + Role Scalability")
    print("=" * 70)

    for player_id, expected_profile in archetype_players.items():
        player_name = get_player_name(player_id)
        print(f"\n{player_name} ({expected_profile})")
        print("-" * 50)

        try:
            results = calculate_extended_resilience(player_id)

            for season_type, metrics in results.items():
                if season_type not in ['Resilience_Delta', 'Pathway_Details']:
                    print(f"{season_type}:")
                    for metric, value in metrics.items():
                        if metric in ['Method_Resilience', 'Dominance_Score', 'Primary_Method_Mastery', 'Role_Scalability']:
                            print(f"  {metric}: {value:.1f}")
                        else:
                            print(f"  {metric}: {value:.2f}")
                    print()

            # Show pathway details
            if 'Pathway_Details' in results:
                details = results['Pathway_Details']
                print("Primary Method Mastery Details:")
                print(".2f")
                print(".2f")
                primary_methods = details['Primary_Methods']
                if 'spatial' in primary_methods and 'primary_zone' in primary_methods['spatial']:
                    print(f"  Primary Zone: {primary_methods['spatial']['primary_zone']}")
                if 'play_type' in primary_methods and 'primary_playtype' in primary_methods['play_type']:
                    print(f"  Primary Play Type: {primary_methods['play_type']['primary_playtype']}")
                if 'creation' in primary_methods and 'primary_creation' in primary_methods['creation']:
                    print(f"  Primary Creation: {primary_methods['creation']['primary_creation']}")
                print()

            # Show deltas
            print("Resilience Deltas (Playoffs - Regular Season):")
            for metric, delta in results['Resilience_Delta'].items():
                if 'Primary_Method_Mastery_Delta' not in metric or delta != 0.0:  # Only show meaningful deltas
                    print(f"  {metric}: {delta:+.2f}")

        except Exception as e:
            print(f"Error calculating for {player_name}: {e}")

    print("\n" + "=" * 70)
    print("✅ Phase 1-3 Complete: Four-Pathway Resilience Operational!")
    print("Versatility + Dominance + Primary Method Mastery + Role Scalability integrated")
    print("Next: Phase 4 (Longitudinal Evolution) and Phase 5 (Unified Framework)")

if __name__ == "__main__":
    main()
