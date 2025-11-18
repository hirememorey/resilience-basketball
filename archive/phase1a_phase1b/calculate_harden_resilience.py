import sqlite3
import pandas as pd
import numpy as np

PLAYER_ID = 201935
SEASON = '2024-25'
DB_PATH = 'data/nba_stats.db'

def calculate_hhi(proportions):
    """Calculates the Herfindahl-Hirschman Index (HHI)."""
    return sum(p**2 for p in proportions)

def calculate_diversity_score(proportions):
    """Converts HHI to a diversity score."""
    if not proportions:
        return 0
    hhi = calculate_hhi(proportions)
    return (1 - hhi) * 100

def get_creation_diversity(db_path, player_id, season, season_type='regular'):
    table_name = 'player_tracking_stats' if season_type == 'regular' else 'player_playoff_tracking_stats'
    
    conn = sqlite3.connect(db_path)
    
    # Get player data
    player_query = f"""
    SELECT
        catch_shoot_field_goals_attempted,
        pull_up_field_goals_attempted,
        drive_field_goals_attempted,
        catch_shoot_effective_field_goal_percentage AS catch_shoot_efg,
        pull_up_effective_field_goal_percentage AS pull_up_efg,
        drive_field_goal_percentage AS drive_fga -- Note: This is FG%, not eFG%. We'll adjust if needed.
    FROM {table_name}
    WHERE player_id = ? AND season = ?
    """
    player_df = pd.read_sql_query(player_query, conn, params=(player_id, season))
    
    if player_df.empty:
        print(f"No {season_type} season creation data found for player_id {player_id}")
        return None, None
        
    player_stats = player_df.iloc[0]

    # Get league averages
    league_query = f"""
    SELECT
        AVG(catch_shoot_effective_field_goal_percentage) AS avg_catch_shoot_efg,
        AVG(pull_up_effective_field_goal_percentage) AS avg_pull_up_efg,
        AVG(drive_field_goal_percentage) AS avg_drive_fga
    FROM {table_name}
    WHERE season = ? AND minutes_played > 100 -- Filter for players with significant minutes
    """
    league_avg_df = pd.read_sql_query(league_query, conn, params=(season,))
    league_avgs = league_avg_df.iloc[0]

    conn.close()

    creation_attempts = {
        'Catch & Shoot': player_stats['catch_shoot_field_goals_attempted'],
        'Pull-Up': player_stats['pull_up_field_goals_attempted'],
        'Drive': player_stats['drive_field_goals_attempted']
    }
    
    total_attempts = sum(creation_attempts.values())
    
    if total_attempts == 0:
        return 0, creation_attempts

    # Volume Distribution
    volume_proportions = {k: v / total_attempts for k, v in creation_attempts.items()}

    # Efficiency Weights
    player_efficiencies = {
        'Catch & Shoot': player_stats['catch_shoot_efg'],
        'Pull-Up': player_stats['pull_up_efg'],
        'Drive': player_stats['drive_fga']
    }
    
    league_avg_efficiencies = {
        'Catch & Shoot': league_avgs['avg_catch_shoot_efg'],
        'Pull-Up': league_avgs['avg_pull_up_efg'],
        'Drive': league_avgs['avg_drive_fga']
    }
    
    efficiency_weights = {
        k: player_efficiencies[k] / league_avg_efficiencies[k] if league_avg_efficiencies[k] > 0 else 0
        for k in creation_attempts.keys()
    }
    
    # Weighted Proportions
    weighted_values = {k: volume_proportions[k] * efficiency_weights[k] for k in creation_attempts.keys()}
    total_weighted_value = sum(weighted_values.values())
    
    if total_weighted_value == 0:
        return 0, creation_attempts

    final_proportions = [v / total_weighted_value for v in weighted_values.values()]
    
    diversity_score = calculate_diversity_score(final_proportions)
    
    return diversity_score, creation_attempts

# --- Main Execution ---
if __name__ == "__main__":
    reg_season_creation_score, reg_season_creation_attempts = get_creation_diversity(DB_PATH, PLAYER_ID, SEASON, 'regular')
    
    if reg_season_creation_score is not None:
        print("--- James Harden 2024-25 Regular Season ---")
        print("\nCreation Diversity Pillar:")
        print(f"  Attempts:")
        for k, v in reg_season_creation_attempts.items():
            print(f"    {k}: {v or 0:.0f}")
        print(f"\n  Creation Diversity Score: {reg_season_creation_score:.2f}")

    playoff_creation_score, playoff_creation_attempts = get_creation_diversity(DB_PATH, PLAYER_ID, SEASON, 'playoff')
    if playoff_creation_score is not None:
        print("\n--- James Harden 2024-25 Playoffs ---")
        print("\nCreation Diversity Pillar:")
        print(f"  Attempts:")
        for k, v in playoff_creation_attempts.items():
            print(f"    {k}: {v or 0:.0f}")
        print(f"\n  Playoff Creation Diversity Score: {playoff_creation_score:.2f}")

        if reg_season_creation_score is not None:
            delta = playoff_creation_score - reg_season_creation_score
            print(f"\n--- Resilience Analysis ---")
            print(f"Creation Resilience Delta: {delta:.2f}")


