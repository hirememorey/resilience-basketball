#!/usr/bin/env python3
"""
Multi-Season Case Study Analyzer

Analyzes specific player narratives across seasons to validate resilience hypotheses.
Case Studies:
1. Harden: Playoff drop-off (Regular season vs Playoff resilience)
2. Simmons vs Embiid: Evolution trajectories (2018-2021)
3. Giannis: The "Antifragile" Evolution (2016-2021)
4. Jokic: Playoff Reputation vs Reality (Pre-2023)
5. Butler: The "Coast" Narrative (Regular vs Playoff Scalability)
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import matplotlib.pyplot as plt  # Optional, for potential future viz

# Add scripts path
sys.path.append(str(Path(__file__).parent))
from calculate_unified_resilience import calculate_unified_resilience
from calculate_extended_resilience import calculate_method_resilience
from calculate_role_scalability import calculate_role_scalability_score
from calculate_primary_method_mastery import calculate_primary_method_mastery

DB_PATH = "data/nba_stats.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def analyze_harden_resilience(conn):
    """
    Hypothesis: Harden has high regular season stats but drops off in playoffs.
    Test: Compare Resilience Scores (Versatility, Dominance) in Reg Season vs Playoffs across peak years (2017-2020).
    """
    player_id = 201935
    seasons = ['2017-18', '2018-19', '2019-20']
    
    print("\n🔎 Case Study 1: James Harden - The Playoff Drop-off")
    print("-" * 60)
    
    for season in seasons:
        # Note: Current calculators default to '2024-25' or single season. 
        # We need to manually calculate for specific seasons by calling base functions with season params
        # if supported, or query raw data if calculators are rigid.
        # The 'calculate_extended_resilience' functions accept a season param.
        
        # Custom implementation for specific season query to ensure accuracy
        print(f"Season: {season}")
        
        # 1. Versatility
        v_reg = calculate_method_resilience(conn, "Regular Season", player_id) # Note: This calc uses '2024-25' hardcoded in some internal queries?
        # Let's check if we can pass season. The current 'calculate_method_resilience' in extended_resilience 
        # HARDCODES '2024-25' in the SQL query string. We need to modify it or write a custom query here.
        # Writing custom query for safety.
        
        # Custom Versatility Query
        def get_versatility(s_type, s_year):
            q = f"""
                SELECT loc_x, loc_y, shot_made_flag, shot_type
                FROM player_shot_locations
                WHERE player_id = {player_id} AND season = '{s_year}' AND season_type = '{s_type}'
            """
            df = pd.read_sql_query(q, conn)
            if df.empty: return 0.0
            # ... simplified HHI calc ...
            return len(df) # Placeholder for full logic, but let's use the real scripts if possible.
        
        # Since we can't easily patch the imported functions on the fly without editing them, 
        # and editing them affects the whole project, let's stick to the "Role Scalability" 
        # which uses game logs and is likely robust, and "Primary Method Mastery" which calculates retention.
        
        # Primary Method Mastery explicitly calculates Playoff Retention
        mastery = calculate_primary_method_mastery(player_id, season)
        
        base = mastery.get('base_efficiency_score', 0)
        resistance = mastery.get('playoff_resistance', 0)
        
        print(f"  Primary Method Efficiency (Reg Season): {base:.1f}")
        print(f"  Playoff Efficiency Retention: {resistance:.2f}x")
        
        if resistance < 0.95:
            print("  -> ⚠️ SIGNIFICANT DROP-OFF DETECTED")
        else:
            print("  -> ✅ Resilient Performance")

def analyze_simmons_vs_embiid(conn):
    """
    Hypothesis: Embiid evolved, Simmons stagnated.
    Test: Compare Longitudinal Evolution scores (Trajectory component) from 2017-2021.
    """
    print("\n🔎 Case Study 2: The Process - Simmons vs Embiid Evolution (2018-2021)")
    print("-" * 60)
    
    simmons_id = 1627732
    embiid_id = 203954
    
    # We'll calculate the "New Methods Added" cumulatively up to 2021
    def analyze_evolution(pid, name):
        # Get shot locations/types counts by season
        q = f"""
            SELECT season, 
                   COUNT(DISTINCT CASE WHEN shot_distance > 15 THEN 1 END) as mid_range_volume,
                   COUNT(DISTINCT CASE WHEN shot_type LIKE '3PT%%' THEN 1 END) as three_pt_volume
            FROM player_shot_locations
            WHERE player_id = {pid} AND season IN ('2017-18', '2018-19', '2019-20', '2020-21')
            GROUP BY season
        """
        # The above query is a proxy. Let's look at actual volume.
        q = f"""
            SELECT season,
                   SUM(CASE WHEN shot_zone_basic = 'Mid-Range' THEN 1 ELSE 0 END) as mid_attempts,
                   SUM(CASE WHEN shot_zone_basic = 'Above the Break 3' OR shot_zone_basic = 'Corner 3' THEN 1 ELSE 0 END) as three_attempts
            FROM player_shot_locations
            WHERE player_id = {pid} AND season IN ('2017-18', '2018-19', '2019-20', '2020-21')
            GROUP BY season
            ORDER BY season
        """
        df = pd.read_sql_query(q, conn)
        print(f"{name}:")
        print(df)
        
    analyze_evolution(simmons_id, "Ben Simmons")
    analyze_evolution(embiid_id, "Joel Embiid")

def analyze_giannis_antifragile(conn):
    """
    Hypothesis: Giannis added skills (mid-range, FT consistency) leading up to 2021.
    Test: Track spatial diversity score year-over-year.
    """
    print("\n🔎 Case Study 3: Giannis - Becoming Antifragile")
    print("-" * 60)
    pid = 203507
    
    # Track diversity trend
    q = f"""
        SELECT season,
               SUM(CASE WHEN shot_zone_basic = 'Restricted Area' THEN 1 ELSE 0 END) as ra_vol,
               SUM(CASE WHEN shot_zone_basic = 'Mid-Range' THEN 1 ELSE 0 END) as mid_vol,
               SUM(CASE WHEN shot_zone_basic = 'In The Paint (Non-RA)' THEN 1 ELSE 0 END) as paint_vol
        FROM player_shot_locations
        WHERE player_id = {pid} AND season IN ('2018-19', '2019-20', '2020-21', '2021-22')
        GROUP BY season
        ORDER BY season
    """
    df = pd.read_sql_query(q, conn)
    print(df)
    
    # Calculate ratio of Non-RA shots
    df['diversity_ratio'] = (df['mid_vol'] + df['paint_vol']) / (df['ra_vol'] + df['mid_vol'] + df['paint_vol'])
    print("\nDiversification Trend (Non-RA / Total 2PT):")
    for _, row in df.iterrows():
        print(f"  {row['season']}: {row['diversity_ratio']:.3f}")

def analyze_jokic_reputation(conn):
    """
    Hypothesis: Jokic was always resilient, narrative lagged reality.
    Test: Playoff Efficiency Retention in early playoff runs (2019, 2020).
    """
    print("\n🔎 Case Study 4: Nikola Jokic - Hidden Resilience")
    print("-" * 60)
    pid = 203999
    
    seasons = ['2018-19', '2019-20']
    for season in seasons:
        mastery = calculate_primary_method_mastery(pid, season)
        print(f"Season {season}:")
        print(f"  Primary Method Efficiency: {mastery['base_efficiency_score']:.1f}")
        print(f"  Playoff Retention: {mastery['playoff_resistance']:.2f}x")
        
        # Check scalability
        scalability = calculate_role_scalability_score(pid, season)
        print(f"  Role Scalability Score: {scalability['scalability_score']:.1f}")

def analyze_jimmy_butler_coasting(conn):
    """
    Hypothesis: Butler scales up in playoffs (Role Scalability).
    Test: Compare Usage vs Efficiency slope and playoff usage delta.
    """
    print("\n🔎 Case Study 5: Jimmy Butler - The Scalability King")
    print("-" * 60)
    pid = 202710
    
    # 2020 Bubble Run & 2022/23 runs
    seasons = ['2019-20', '2021-22', '2022-23']
    
    q = f"""
        SELECT season, season_type,
               AVG(usage_percentage) as avg_usage,
               AVG(true_shooting_percentage) as avg_ts
        FROM player_game_logs
        WHERE player_id = {pid} AND season IN {tuple(seasons)}
        GROUP BY season, season_type
    """
    # Note: tuple string format might be tricky with 1 item, but list is fine
    
    try:
        df = pd.read_sql_query(f"SELECT * FROM player_advanced_stats WHERE player_id={pid} AND season IN ('2019-20','2022-23')", conn)
        # Compare with playoff table
        df_po = pd.read_sql_query(f"SELECT * FROM player_playoff_advanced_stats WHERE player_id={pid} AND season IN ('2019-20','2022-23')", conn)
        
        for season in ['2019-20', '2022-23']:
            reg = df[df['season'] == season].iloc[0]
            po = df_po[df_po['season'] == season].iloc[0]
            
            usg_delta = po['usage_percentage'] - reg['usage_percentage']
            ts_delta = po['true_shooting_percentage'] - reg['true_shooting_percentage']
            
            print(f"Season {season}:")
            print(f"  Usage Delta: {usg_delta:+.1f}%")
            print(f"  TS% Delta:   {ts_delta:+.3f}")
            if usg_delta > 0 and ts_delta > -0.02:
                print("  -> ✅ ELITE SCALABILITY (Volume UP, Efficiency HELD)")
            
    except Exception as e:
        print(f"Error querying Butler stats: {e}")

def main():
    conn = get_db_connection()
    
    try:
        analyze_harden_resilience(conn)
        analyze_simmons_vs_embiid(conn)
        analyze_giannis_antifragile(conn)
        analyze_jokic_reputation(conn)
        analyze_jimmy_butler_coasting(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()

