#!/usr/bin/env python3
"""
Extended Playoff Resilience Calculator - Phase 4: Longitudinal Evolution
Implementation of the "Evolver" pathway (Giannis Antetokounmpo archetype).

Core Principles:
1. Skill Acquisition: Counting new reliable methods added per season
2. Trajectory Analysis: Measuring efficiency slopes of newly added skills
3. Adaptability Score: Composite metric of acquisition * retention
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Dict, List, Tuple

# Add the scripts directory to path so we can import common helpers
sys.path.append(str(Path(__file__).parent))

DB_PATH = "data/nba_stats.db"

def get_db_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def get_method_portfolio(conn, player_id: int) -> pd.DataFrame:
    """
    Retrieve a player's method portfolio across all available seasons.
    Combines spatial zones, play types, and creation methods.
    """
    # 1. Get Spatial Data (Shot Locations)
    query_spatial = f"""
        SELECT 
            season,
            loc_x, 
            loc_y, 
            shot_made_flag
        FROM player_shot_locations
        WHERE player_id = {player_id} AND season_type = 'Regular Season'
    """
    df_spatial = pd.read_sql_query(query_spatial, conn)
    
    # Process spatial zones if data exists
    spatial_methods = []
    if not df_spatial.empty:
        # Vectorized zone definition (simplified for speed)
        df_spatial['zone'] = 'Other'
        x, y = df_spatial['loc_x'], df_spatial['loc_y']
        
        # Restricted Area
        mask_ra = (x.abs() <= 4) & (y <= 4.25)
        df_spatial.loc[mask_ra, 'zone'] = 'Restricted Area'
        
        # Paint (Non-RA)
        mask_paint = (x.abs() <= 8) & (y <= 19) & ~mask_ra
        df_spatial.loc[mask_paint, 'zone'] = 'Paint (Non-RA)'
        
        # Mid-Range
        mask_mid = ((x.abs() > 8) & (y <= 19)) | ((x.abs() <= 22) & (y > 19))
        df_spatial.loc[mask_mid, 'zone'] = 'Mid-Range'
        
        # Corner 3
        mask_c3 = (x.abs() > 22) & (y <= 7.8)
        df_spatial.loc[mask_c3, 'zone'] = 'Corner 3'
        
        # Above Break 3
        mask_ab3 = (y > 7.8) & (x.abs() > 8) & ~mask_mid & ~mask_c3
        df_spatial.loc[mask_ab3, 'zone'] = 'Above Break 3'
        
        # Aggregate per season
        spatial_agg = df_spatial.groupby(['season', 'zone']).agg(
            volume=('shot_made_flag', 'count'),
            makes=('shot_made_flag', 'sum')
        ).reset_index()
        spatial_agg['efficiency'] = spatial_agg['makes'] / spatial_agg['volume']
        spatial_agg['method_type'] = 'Spatial'
        spatial_agg.rename(columns={'zone': 'method_name'}, inplace=True)
        spatial_methods = [spatial_agg]

    # 2. Get Play Type Data
    query_playtype = f"""
        SELECT season, play_type as method_name, possessions as volume, points_per_possession
        FROM player_playtype_stats
        WHERE player_id = {player_id}
    """
    df_playtype = pd.read_sql_query(query_playtype, conn)
    if not df_playtype.empty:
        df_playtype['efficiency'] = df_playtype['points_per_possession'] # PPP is efficiency
        df_playtype['method_type'] = 'PlayType'
    
    # 3. Get Tracking Data (Creation)
    query_tracking = f"""
        SELECT season, 
               drives, drive_points,
               catch_shoot_field_goals_attempted, catch_shoot_effective_field_goal_percentage,
               pull_up_field_goals_attempted, pull_up_effective_field_goal_percentage
        FROM player_tracking_stats
        WHERE player_id = {player_id}
    """
    df_tracking = pd.read_sql_query(query_tracking, conn)
    creation_methods = []
    
    if not df_tracking.empty:
        # Drives
        drives = df_tracking[['season', 'drives', 'drive_points']].copy()
        drives.columns = ['season', 'volume', 'points']
        drives['efficiency'] = drives['points'] / drives['volume'].replace(0, 1) # PPD
        drives['method_name'] = 'Drives'
        drives['method_type'] = 'Creation'
        creation_methods.append(drives[['season', 'method_name', 'method_type', 'volume', 'efficiency']])
        
        # Catch & Shoot
        cs = df_tracking[['season', 'catch_shoot_field_goals_attempted', 'catch_shoot_effective_field_goal_percentage']].copy()
        cs.columns = ['season', 'volume', 'efficiency']
        cs['method_name'] = 'Catch & Shoot'
        cs['method_type'] = 'Creation'
        creation_methods.append(cs)
        
        # Pull Ups
        pu = df_tracking[['season', 'pull_up_field_goals_attempted', 'pull_up_effective_field_goal_percentage']].copy()
        pu.columns = ['season', 'volume', 'efficiency']
        pu['method_name'] = 'Pull Up'
        pu['method_type'] = 'Creation'
        creation_methods.append(pu)

    # Combine all dataframes
    dfs_to_concat = spatial_methods + [df_playtype] + creation_methods
    # Filter out empty DFs
    dfs_to_concat = [d for d in dfs_to_concat if not d.empty]
    
    if not dfs_to_concat:
        return pd.DataFrame()
        
    full_portfolio = pd.concat(dfs_to_concat, ignore_index=True)
    return full_portfolio

def calculate_skill_acquisition(portfolio: pd.DataFrame) -> float:
    """
    Calculate the rate of NEW skill acquisition per season.
    A 'skill' is defined as a method with volume > threshold.
    """
    if portfolio.empty:
        return 0.0
        
    # Define volume thresholds per type (Total volume per season, not per game)
    # Raw data shows Giannis has ~250-550 mid-range shots/season.
    # PlayTypes (e.g. Isolation) are ~3-5 possessions PER GAME. 
    # We need to handle per-game vs total volume differences.
    
    # Currently, spatial data is TOTAL shots (250+).
    # PlayType data is POSSESSIONS PER GAME (2.7, 3.6, etc).
    # Tracking data (Drives) is DRIVES PER GAME (8.8, 10.9).
    
    THRESHOLDS = {
        'Spatial': 150,    # Total shots per season
        'PlayType': 1.5,   # Possessions per game
        'Creation': 3.0    # Attempts/Drives per game
    }
    
    # Filter for "Qualified" skills
    portfolio['qualified'] = portfolio.apply(
        lambda row: row['volume'] >= THRESHOLDS.get(row['method_type'], 50), axis=1
    )
    
    qualified_skills = portfolio[portfolio['qualified']].copy()
    
    # Identify first season for each method
    method_start = qualified_skills.groupby(['method_type', 'method_name'])['season'].min().reset_index()
    method_start.columns = ['method_type', 'method_name', 'start_season']
    
    # Count new skills per season (excluding rookie year/first data year)
    seasons = sorted(portfolio['season'].unique())
    if len(seasons) < 2:
        return 0.0 # Need at least 2 seasons to measure evolution
        
    first_season = seasons[0]
    
    # We only care about skills added AFTER the first season
    new_skills = method_start[method_start['start_season'] > first_season]
    
    total_new_skills = len(new_skills)
    num_eligible_seasons = len(seasons) - 1
    
    # Metric: New Qualified Skills per Season
    acquisition_rate = total_new_skills / num_eligible_seasons
    
    # Normalize to 0-100 (approx 1 new skill per season is elite)
    score = min(acquisition_rate * 100, 100)
    
    return score


def calculate_efficiency_trajectory(portfolio: pd.DataFrame) -> float:
    """
    Calculate the trajectory (slope) of efficiency for NEWLY acquired skills.
    This rewards players who not only add skills but improve them over time.
    """
    if portfolio.empty:
        return 0.0
        
    # Define volume thresholds per type (Total volume per season, not per game)
    THRESHOLDS = {
        'Spatial': 150,    # Total shots per season
        'PlayType': 1.5,   # Possessions per game
        'Creation': 3.0    # Attempts/Drives per game
    }
    
    # 1. Identify "New Skills" (Skills that appeared after season 1)
    seasons = sorted(portfolio['season'].unique())
    if len(seasons) < 2:
        return 0.0
        
    first_season = seasons[0]
    
    # Determine start season for every method
    portfolio['qualified'] = portfolio.apply(
        lambda row: row['volume'] >= THRESHOLDS.get(row['method_type'], 50), axis=1
    )
    # Filter to only qualified seasons for start-date purposes, but keep all data for trend analysis
    qualified_rows = portfolio[portfolio['qualified']]
    
    if qualified_rows.empty:
        return 0.0

    method_start = qualified_rows.groupby(['method_type', 'method_name'])['season'].min().reset_index()
    method_start.columns = ['method_type', 'method_name', 'start_season']
    
    # Filter for methods that started AFTER the first season (New Skills)
    new_methods = method_start[method_start['start_season'] > first_season]
    
    if new_methods.empty:
        return 0.0 # No new skills to analyze
        
    # 2. Calculate Efficiency Slope for each new skill
    slopes = []
    
    for _, method in new_methods.iterrows():
        # Get all history for this method (even pre-qualification if it exists)
        history = portfolio[
            (portfolio['method_type'] == method['method_type']) & 
            (portfolio['method_name'] == method['method_name'])
        ].copy()
        
        if len(history) < 2:
            continue # Need at least 2 data points for a slope
            
        # Map seasons to integers for regression (0, 1, 2...)
        season_map = {s: i for i, s in enumerate(sorted(history['season'].unique()))}
        x = history['season'].map(season_map).values
        y = history['efficiency'].fillna(0).values
        
        # Simple linear regression slope
        if len(x) > 1:
            slope, _ = np.polyfit(x, y, 1)
            # Weight the slope by the average volume of the skill? 
            # For now, raw efficiency improvement is the signal.
            slopes.append(slope)
            
    if not slopes:
        return 0.0
        
    # Average slope of all new skills
    avg_slope = np.mean(slopes)
    
    # Normalize: A slope of +0.05 (5% efficiency boost per year) is elite
    # A slope of 0 is stagnant. Negative is regression.
    # Sigmoid normalization centered at 0
    # 0.05 -> ~100 score? 
    # Let's use linear scaling for simplicity first: 
    # Score = avg_slope * 1000 (so 0.01 -> 10, 0.05 -> 50) + 50 baseline?
    
    # Let's scale it such that 0.05 (5% improvement) = 100
    score = max(min(avg_slope * 2000, 100), -100) 
    
    # Clip negative scores to 0 for the final metric? 
    # No, regression should penalize adaptability.
    
    return score

def calculate_longitudinal_evolution(player_id: int) -> Dict[str, float]:
    conn = get_db_connection()
    
    # 1. Get raw portfolio
    portfolio = get_method_portfolio(conn, player_id)
    
    if portfolio.empty:
        conn.close()
        return {'Skill_Acquisition_Score': 0, 'Efficiency_Trajectory_Score': 0, 'Adaptability_Score': 0}

    # 2. Calculate Acquisition Score
    acquisition_score = calculate_skill_acquisition(portfolio)
    
    # 3. Calculate Efficiency Trajectory
    trajectory_score = calculate_efficiency_trajectory(portfolio)
    
    conn.close()
    
    # 4. Composite Adaptability Score
    # 60% Weight to Acquisition (Can you learn?)
    # 40% Weight to Trajectory (Do you get better?)
    # If trajectory is negative, it hurts the score.
    
    # Ensure non-negative final score
    trajectory_component = max(trajectory_score, 0) 
    
    adaptability = (acquisition_score * 0.6) + (trajectory_component * 0.4)

    return {
        'Skill_Acquisition_Score': acquisition_score,
        'Efficiency_Trajectory_Score': trajectory_score,
        'Adaptability_Score': adaptability
    }

def main():
    """Test the Longitudinal Evolution calculator."""
    # Test candidates known for evolution vs stagnation
    test_players = {
        203507: "Giannis Antetokounmpo", # The Archetype (High Evolution)
        201935: "James Harden",          # Moderate Evolution (Role shifts)
        203076: "Anthony Davis",         # Stagnant/Specialized
        1629029: "Luka Doncic"           # Young/High Baseline
    }
    
    print("🚀 Longitudinal Evolution Calculator (Phase 4)")
    print("============================================")
    
    for pid, name in test_players.items():
        print(f"\nAnalyzing {name}...")
        try:
            result = calculate_longitudinal_evolution(pid)
            print(f"  Skill Acquisition: {result['Skill_Acquisition_Score']:.1f}")
            print(f"  Efficiency Trajectory: {result['Efficiency_Trajectory_Score']:.1f}")
            print(f"  Adaptability Score: {result['Adaptability_Score']:.1f}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    main()

