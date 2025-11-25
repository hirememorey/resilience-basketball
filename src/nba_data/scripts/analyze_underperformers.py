#!/usr/bin/env python3
"""
Analyze Playoff Underperformers (2015-16 to 2024-25)
Identifies high-usage players who saw significant efficiency drops in the playoffs.
"""

import sqlite3
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for potential imports
sys.path.append(str(Path(__file__).parent.parent))

DB_PATH = "data/nba_stats.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def analyze_underperformers():
    conn = get_db_connection()
    
    # 1. Get Regular Season Data (High Usage/Volume Players)
    # We use Top 40 by Usage Rate as a proxy for "All-Star Caliber" primary options
    # Filter: Min 40 games, Min 20% Usage
    query_rs = """
    SELECT 
        p.player_name,
        rs.player_id,
        rs.season,
        rs.true_shooting_percentage as rs_ts,
        rs.effective_field_goal_percentage as rs_efg,
        rs.usage_percentage as rs_usg,
        rs.offensive_rating as rs_ortg,
        rs.games_played as rs_gp
    FROM player_advanced_stats rs
    JOIN players p ON rs.player_id = p.player_id
    WHERE rs.games_played >= 40 
      AND rs.usage_percentage >= 0.20
      AND rs.minutes_played >= 20
    """
    
    df_rs = pd.read_sql_query(query_rs, conn)
    
    # 2. Get Playoff Data
    # Filter: Min 4 games (at least one short series)
    query_po = """
    SELECT 
        player_id,
        season,
        true_shooting_percentage as po_ts,
        effective_field_goal_percentage as po_efg,
        usage_percentage as po_usg,
        offensive_rating as po_ortg,
        games_played as po_gp
    FROM player_playoff_advanced_stats
    WHERE games_played >= 4
    """
    
    df_po = pd.read_sql_query(query_po, conn)
    
    conn.close()
    
    # 3. Merge Data
    merged = pd.merge(df_rs, df_po, on=['player_id', 'season'], how='inner')
    
    # 4. Calculate Deltas
    merged['ts_diff'] = merged['po_ts'] - merged['rs_ts']
    merged['efg_diff'] = merged['po_efg'] - merged['rs_efg']
    merged['usg_diff'] = merged['po_usg'] - merged['rs_usg']
    merged['ortg_diff'] = merged['po_ortg'] - merged['rs_ortg']
    
    # 5. Filter for Significant Underperformance
    # Criteria: 
    # - TS% drop > 5% (e.g., 60% -> 55%)
    # - ORTG drop > 5 points
    # - Must have been a high-impact player (Usage > 25% in RS)
    
    underperformers = merged[
        (merged['rs_usg'] >= 0.25) & 
        (merged['ts_diff'] < -0.04) # 4% drop in TS is significant
    ].copy()
    
    # Sort by TS Difference (biggest drop first)
    underperformers = underperformers.sort_values('ts_diff', ascending=True)
    
    # Add a "Severity" score (TS Drop * Usage) to find high-profile failures
    underperformers['severity'] = underperformers['ts_diff'] * underperformers['rs_usg'] * 100
    
    # Top 30 Underperformers by Severity
    top_fails = underperformers.sort_values('severity', ascending=True).head(40)
    
    print("🚨 TOP 40 PLAYOFF UNDERPERFORMERS (Efficiency Drop vs Regular Season) 🚨")
    print("=" * 100)
    print(f"{'Player':<25} {'Season':<10} {'RS TS%':<8} {'PO TS%':<8} {'Diff':<8} {'RS Usg':<8} {'Severity':<8}")
    print("-" * 100)
    
    for _, row in top_fails.iterrows():
        print(f"{row['player_name']:<25} {row['season']:<10} {row['rs_ts']:.3f}    {row['po_ts']:.3f}    {row['ts_diff']:+.3f}    {row['rs_usg']:.1%}     {row['severity']:.1f}")

    # Also check for "Volume Scorers who disappeared" (Usage Drop)
    print("\n📉 NOTABLE USAGE DROPS (Disappearing Acts)")
    print("=" * 100)
    usage_drops = merged[
        (merged['rs_usg'] >= 0.25) & 
        (merged['usg_diff'] < -0.05) # 5% usage drop
    ].sort_values('usg_diff', ascending=True).head(15)
    
    for _, row in usage_drops.iterrows():
        print(f"{row['player_name']:<25} {row['season']:<10} {row['rs_usg']:.1%}    {row['po_usg']:.1%}    {row['usg_diff']:+.1%}")

if __name__ == "__main__":
    analyze_underperformers()







