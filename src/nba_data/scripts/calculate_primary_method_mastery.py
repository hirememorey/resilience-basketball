#!/usr/bin/env python3
"""
Phase 2: Primary Method Mastery Implementation

Measures elite specialization pathway - how efficient is a player's primary offensive method,
and is it strong enough to remain effective even when schemed against?

This addresses the "Shaq problem" where players achieve playoff success through elite mastery
in one primary method rather than broad diversification.
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

def identify_primary_method(player_id: int, season: str = "2024-25", season_type: str = "Regular Season") -> Dict[str, any]:
    """
    Identify player's primary offensive method across three dimensions:
    1. Spatial zones (Restricted Area, Paint, Mid-Range, Corner 3, Above Break 3)
    2. Play types (Isolation, Pick & Roll, Transition, etc.)
    3. Creation methods (Catch & Shoot, Pull-Up, Drives)

    Returns primary method info with weighted volume and efficiency.
    """
    conn = get_db_connection()

    # Get spatial diversity data
    spatial_query = f"""
        SELECT loc_x, loc_y, shot_made_flag, shot_type
        FROM player_shot_locations
        WHERE player_id = {player_id} AND season = '{season}' AND season_type = '{season_type}'
    """
    spatial_df = pd.read_sql_query(spatial_query, conn)
    spatial_zones = {}

    if not spatial_df.empty:
        # Define court zones
        x, y = spatial_df['loc_x'], spatial_df['loc_y']
        is_ra = (x.abs() <= 4) & (y <= 4.25)
        is_paint = (x.abs() <= 8) & (y <= 19) & ~is_ra
        is_mid_range = (
            ((x.abs() > 8) & (y <= 19)) |
            ((x.abs() <= 22) & (y > 19)) |
            (spatial_df['shot_type'] == '2PT Field Goal') & ~is_ra & ~is_paint
        )
        is_corner_3 = (x.abs() > 22) & (y <= 7.8)
        is_above_break_3 = (spatial_df['shot_type'] == '3PT Field Goal') & ~is_corner_3

        conditions = [is_ra, is_paint, is_mid_range, is_corner_3 & (x < 0), is_corner_3 & (x >= 0), is_above_break_3]
        choices = ['Restricted Area', 'In The Paint (Non-RA)', 'Mid-Range', 'Left Corner 3', 'Right Corner 3', 'Above the Break 3']

        spatial_df['zone'] = pd.Series(np.select(conditions, choices, default='Other'), index=spatial_df.index)

        # Calculate efficiency by zone
        zone_stats = spatial_df.groupby('zone').agg({
            'shot_made_flag': ['count', 'sum']
        }).reset_index()
        zone_stats.columns = ['zone', 'attempts', 'makes']

        # Calculate 3PM for eFG
        three_pointers = spatial_df[spatial_df['shot_type'] == '3PT Field Goal'].groupby('zone')['shot_made_flag'].sum()
        zone_stats = zone_stats.set_index('zone')
        zone_stats['3pm'] = three_pointers
        zone_stats['3pm'] = zone_stats['3pm'].fillna(0)
        zone_stats['efg'] = (zone_stats['makes'] + 0.5 * zone_stats['3pm']) / zone_stats['attempts']

        # Weight by efficiency for primary zone identification
        zone_stats['weighted_volume'] = zone_stats['attempts'] * zone_stats['efg'].fillna(0.4)
        primary_zone = zone_stats['weighted_volume'].idxmax()
        spatial_zones = {
            'primary_zone': primary_zone,
            'zone_attempts': zone_stats.loc[primary_zone, 'attempts'],
            'zone_efg': zone_stats.loc[primary_zone, 'efg']
        }

    # Get play type diversity data
    table = "player_playtype_stats" if season_type == "Regular Season" else "player_playoff_playtype_stats"
    playtype_query = f"""
        SELECT play_type, possessions, points_per_possession
        FROM {table}
        WHERE player_id = {player_id} AND season = '{season}'
    """
    playtype_df = pd.read_sql_query(playtype_query, conn)

    play_types = {}
    if not playtype_df.empty:
        # Weight by efficiency for primary play type
        playtype_df['weighted_volume'] = playtype_df['possessions'] * playtype_df['points_per_possession'].fillna(0.9)
        primary_playtype = playtype_df.loc[playtype_df['weighted_volume'].idxmax(), 'play_type']
        primary_ptp = playtype_df.loc[playtype_df['weighted_volume'].idxmax(), 'points_per_possession']
        play_types = {
            'primary_playtype': primary_playtype,
            'playtype_possessions': playtype_df['possessions'].max(),
            'playtype_ppp': primary_ptp
        }

    # Get creation method diversity data
    tracking_table = "player_tracking_stats" if season_type == "Regular Season" else "player_playoff_tracking_stats"
    tracking_query = f"SELECT * FROM {tracking_table} WHERE player_id = {player_id} AND season = '{season}'"
    tracking_df = pd.read_sql_query(tracking_query, conn)

    creation_methods = {}
    if not tracking_df.empty:
        tracking_df = tracking_df.iloc[0]

        # Extract creation metrics
        cs_attempts = tracking_df['catch_shoot_field_goals_attempted']
        cs_efg = tracking_df['catch_shoot_effective_field_goal_percentage']

        pu_attempts = tracking_df['pull_up_field_goals_attempted']
        pu_efg = tracking_df['pull_up_effective_field_goal_percentage']

        drives = tracking_df['drives']
        drive_pts = tracking_df['drive_points']
        drive_ppd = (drive_pts / drives) if drives else 0

        creation_data = pd.DataFrame([
            {'method': 'Catch & Shoot', 'volume': cs_attempts, 'efficiency': cs_efg},
            {'method': 'Pull-Up', 'volume': pu_attempts, 'efficiency': pu_efg},
            {'method': 'Drives', 'volume': drives, 'efficiency': drive_ppd}
        ])

        # Weight by efficiency for primary creation method
        creation_data['weighted_volume'] = creation_data['volume'] * creation_data['efficiency'].fillna(0.4)
        primary_creation = creation_data.loc[creation_data['weighted_volume'].idxmax(), 'method']
        primary_eff = creation_data.loc[creation_data['weighted_volume'].idxmax(), 'efficiency']

        creation_methods = {
            'primary_creation': primary_creation,
            'creation_attempts': creation_data['volume'].max(),
            'creation_efficiency': primary_eff
        }

    conn.close()

    return {
        'spatial': spatial_zones,
        'play_type': play_types,
        'creation': creation_methods
    }

def calculate_absolute_efficiency(primary_methods: Dict, season: str = "2024-25", season_type: str = "Regular Season") -> float:
    """
    Measure absolute efficiency of primary method vs historical benchmarks and league averages.

    Returns percentile rank (0-100) among all players in that method.
    """
    conn = get_db_connection()

    # Calculate percentile rank for primary method efficiency
    percentile_score = 0.0

    # Spatial zone efficiency percentile
    if 'primary_zone' in primary_methods.get('spatial', {}):
        zone = primary_methods['spatial']['primary_zone']
        player_efg = primary_methods['spatial']['zone_efg']

        # Get all players' efficiency in this zone
        spatial_query = f"""
            SELECT DISTINCT p.player_id, p.player_name,
                   COUNT(CASE WHEN shot_made_flag = 1 THEN 1 END) as makes,
                   COUNT(*) as attempts,
                   COUNT(CASE WHEN shot_type = '3PT Field Goal' AND shot_made_flag = 1 THEN 1 END) as threepm
            FROM player_shot_locations psl
            JOIN players p ON p.player_id = psl.player_id
            WHERE psl.season = '{season}' AND psl.season_type = '{season_type}'
            GROUP BY p.player_id, p.player_name, psl.loc_x, psl.loc_y, psl.shot_type
            HAVING attempts >= 10
        """

        # Simplified approach: use league average as benchmark for now
        # In full implementation, would calculate percentiles across all players
        league_avg_efg = 0.45  # Approximate league average eFG
        zone_multiplier = {
            'Restricted Area': 1.2,  # Easier shots
            'In The Paint (Non-RA)': 1.1,
            'Mid-Range': 0.9,
            'Above the Break 3': 0.7,
            'Left Corner 3': 0.8,
            'Right Corner 3': 0.8
        }

        expected_efg = league_avg_efg * zone_multiplier.get(zone, 1.0)
        zone_percentile = min(100, max(0, (player_efg / expected_efg) * 50))  # Rough percentile calculation
        percentile_score += zone_percentile * 0.4

    # Play type efficiency percentile
    if 'primary_playtype' in primary_methods.get('play_type', {}):
        playtype = primary_methods['play_type']['primary_playtype']
        player_ppp = primary_methods['play_type']['playtype_ppp']

        # League average PPP by play type (approximate benchmarks)
        ppp_benchmarks = {
            'Isolation': 0.85,
            'Pick & Roll Ball Handler': 0.90,
            'Pick & Roll Roll Man': 1.15,
            'Post-Up': 0.95,
            'Spot Up': 1.05,
            'Off Screen': 0.95,
            'Hand Off': 0.90,
            'Cut': 1.25,
            'Transition': 1.10,
            'Miscellaneous': 0.90
        }

        benchmark_ppp = ppp_benchmarks.get(playtype, 0.90)
        playtype_percentile = min(100, max(0, (player_ppp / benchmark_ppp) * 50))
        percentile_score += playtype_percentile * 0.4

    # Creation method efficiency percentile
    if 'primary_creation' in primary_methods.get('creation', {}):
        creation = primary_methods['creation']['primary_creation']
        player_eff = primary_methods['creation']['creation_efficiency']

        # Efficiency benchmarks by creation method
        eff_benchmarks = {
            'Catch & Shoot': 0.55,  # eFG%
            'Pull-Up': 0.45,
            'Drives': 0.75  # Points per drive
        }

        benchmark_eff = eff_benchmarks.get(creation, 0.50)
        creation_percentile = min(100, max(0, (player_eff / benchmark_eff) * 50))
        percentile_score += creation_percentile * 0.2

    conn.close()
    return percentile_score

def measure_playoff_resistance(player_id: int, primary_methods: Dict, season: str = "2024-25") -> float:
    """
    Measure how well primary method efficiency holds up in playoffs vs regular season.

    Returns efficiency retention ratio (0-1.5, where >1 means playoff improvement).
    """
    # Get regular season efficiency
    reg_season_eff = calculate_absolute_efficiency(primary_methods, season, "Regular Season")

    # Get playoff efficiency
    playoff_eff = calculate_absolute_efficiency(primary_methods, season, "Playoffs")

    if reg_season_eff > 0:
        retention_ratio = playoff_eff / reg_season_eff
        # Cap at 1.5 (significant improvement) and floor at 0.3 (severe decline)
        return max(0.3, min(1.5, retention_ratio))

    return 1.0  # Neutral if no regular season efficiency

def calculate_primary_method_mastery(player_id: int, season: str = "2024-25") -> Dict[str, float]:
    """
    Calculate Primary Method Mastery score - elite specialization pathway.

    Combines absolute efficiency (base score) with playoff resistance (multiplier).
    """
    # Step 1: Identify primary method
    primary_methods = identify_primary_method(player_id, season, "Regular Season")

    # Step 2: Measure absolute efficiency (percentile rank)
    base_score = calculate_absolute_efficiency(primary_methods, season, "Regular Season")

    # Step 3: Measure playoff resistance
    playoff_resistance = measure_playoff_resistance(player_id, primary_methods, season)

    # Step 4: Calculate mastery score
    mastery_score = base_score * playoff_resistance

    # Clamp to 0-100 range
    mastery_score = max(0, min(100, mastery_score))

    return {
        'primary_method_mastery': mastery_score,
        'base_efficiency_score': base_score,
        'playoff_resistance': playoff_resistance,
        'primary_methods': primary_methods
    }

def get_player_name(player_id: int) -> str:
    """Get player name for display purposes."""
    conn = get_db_connection()
    query = f"SELECT player_name FROM players WHERE player_id = {player_id}"
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result.iloc[0]['player_name'] if not result.empty else f"Player {player_id}"

def calculate_primary_method_mastery_batch(player_ids: list, season: str = "2024-25") -> pd.DataFrame:
    """
    Calculate primary method mastery scores for multiple players.
    """
    results = []

    for player_id in player_ids:
        try:
            mastery_data = calculate_primary_method_mastery(player_id, season)
            player_name = get_player_name(player_id)

            result = {
                'player_id': player_id,
                'player_name': player_name,
                'primary_method_mastery': round(mastery_data['primary_method_mastery'], 2),
                'base_efficiency_score': round(mastery_data['base_efficiency_score'], 2),
                'playoff_resistance': round(mastery_data['playoff_resistance'], 2),
            }

            # Add primary method details
            primary_methods = mastery_data['primary_methods']
            if 'spatial' in primary_methods and 'primary_zone' in primary_methods['spatial']:
                result['primary_zone'] = primary_methods['spatial']['primary_zone']
            if 'play_type' in primary_methods and 'primary_playtype' in primary_methods['play_type']:
                result['primary_playtype'] = primary_methods['play_type']['primary_playtype']
            if 'creation' in primary_methods and 'primary_creation' in primary_methods['creation']:
                result['primary_creation'] = primary_methods['creation']['primary_creation']

            results.append(result)
            print(f"✓ {player_name}: Mastery {mastery_data['primary_method_mastery']:.2f}")

        except Exception as e:
            print(f"✗ Error calculating for player {player_id}: {e}")

    return pd.DataFrame(results)

def main():
    """Main function for Phase 2 Primary Method Mastery implementation."""

    # Test on archetype players
    archetype_players = {
        201935: "James Harden",      # Should be high versatility, moderate mastery
        2544: "LeBron James",        # Should be high versatility + mastery
        1629029: "Luka Dončić",     # Should be high versatility, moderate mastery
        203076: "Anthony Davis",    # Should be high mastery (post/dominance)
        2397: "Shaq",              # Should be VERY high mastery (post specialist)
        2207: "Dirk Nowitzki",     # Should be high mastery (corner 3 specialist)
    }

    print("🚀 Phase 2: Primary Method Mastery Implementation")
    print("=" * 60)

    # Calculate primary method mastery for archetype players
    print("\nCalculating primary method mastery scores...")
    player_ids = list(archetype_players.keys())
    results = calculate_primary_method_mastery_batch(player_ids)

    print("\nResults:")
    print("=" * 60)
    for _, row in results.iterrows():
        print(f"{row['player_name']} (ID: {row['player_id']}):")
        print(".2f")
        print(".2f")
        print(".2f")
        if 'primary_zone' in row and pd.notna(row['primary_zone']):
            print(f"  Primary Zone: {row['primary_zone']}")
        if 'primary_playtype' in row and pd.notna(row['primary_playtype']):
            print(f"  Primary Play Type: {row['primary_playtype']}")
        if 'primary_creation' in row and pd.notna(row['primary_creation']):
            print(f"  Primary Creation: {row['primary_creation']}")
        print()

    # Save results
    results.to_csv("data/primary_method_mastery_phase2.csv", index=False)
    print("Results saved to data/primary_method_mastery_phase2.csv")

if __name__ == "__main__":
    main()






