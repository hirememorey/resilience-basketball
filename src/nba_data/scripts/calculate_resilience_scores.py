import sqlite3
import pandas as pd
import numpy as np
from typing import Dict

DB_PATH = "data/nba_stats.db"
PLAYER_ID = 201935  # James Harden
SEASON = "2024-25"

def get_db_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def fetch_league_averages(conn: sqlite3.Connection) -> pd.DataFrame:
    """Fetches all league average benchmarks from the database."""
    return pd.read_sql_query("SELECT * FROM league_averages", conn)

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

def calculate_spatial_diversity(conn: sqlite3.Connection, averages: pd.DataFrame, season_type: str) -> float:
    st_query = season_type
    query = f"""
        SELECT loc_x, loc_y, shot_made_flag, shot_type
        FROM player_shot_locations
        WHERE player_id = {PLAYER_ID} AND season = '{SEASON}' AND season_type = '{st_query}'
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
    
    avg_efg = averages[(averages['season_type'] == season_type) & (averages['metric_type'] == 'spatial')].set_index('metric_name')['value']
    stats['efg_vs_avg'] = stats['efg'] / avg_efg
    stats['weighted_volume'] = stats['attempts'] * stats['efg_vs_avg'].fillna(1)
    
    return calculate_diversity_score(stats['weighted_volume'])

def calculate_play_type_diversity(conn: sqlite3.Connection, averages: pd.DataFrame, season_type: str) -> float:
    table = "player_playtype_stats" if season_type == "Regular Season" else "player_playoff_playtype_stats"
    query = f"""
        SELECT play_type, possessions, points_per_possession
        FROM {table}
        WHERE player_id = {PLAYER_ID} AND season = '{SEASON}'
    """
    df = pd.read_sql_query(query, conn)
    if df.empty: return 0

    avg_ppp = averages[(averages['season_type'] == season_type) & (averages['metric_type'] == 'play_type')].set_index('metric_name')['value']
    df['ppp_vs_avg'] = df['points_per_possession'] / avg_ppp.loc[df['play_type']].values
    df['weighted_volume'] = df['possessions'] * df['ppp_vs_avg'].fillna(1)

    return calculate_diversity_score(df.set_index('play_type')['weighted_volume'])

def calculate_creation_diversity(conn: sqlite3.Connection, averages: pd.DataFrame, season_type: str) -> float:
    table = "player_tracking_stats" if season_type == "Regular Season" else "player_playoff_tracking_stats"
    query = f"SELECT * FROM {table} WHERE player_id = {PLAYER_ID} AND season = '{SEASON}'"
    df = pd.read_sql_query(query, conn).iloc[0]

    # Catch & Shoot
    cs_attempts = df['catch_shoot_field_goals_attempted']
    cs_efg = df['catch_shoot_effective_field_goal_percentage']
    
    # Pull-Up
    pu_attempts = df['pull_up_field_goals_attempted']
    pu_efg = df['pull_up_effective_field_goal_percentage']

    # Drives
    drives = df['drives']
    drive_pts = df['drive_points']
    drive_ppd = (drive_pts / drives) if drives else 0

    creation_data = pd.DataFrame([
        {'type': 'Catch & Shoot', 'volume': cs_attempts, 'efficiency': cs_efg},
        {'type': 'Pull-Up', 'volume': pu_attempts, 'efficiency': pu_efg},
        {'type': 'Drives', 'volume': drives, 'efficiency': drive_ppd}
    ]).set_index('type')

    avg_creation = averages[(averages['season_type'] == season_type) & (averages['metric_type'] == 'creation')].set_index('metric_name')['value']
    creation_data['eff_vs_avg'] = creation_data['efficiency'] / avg_creation
    creation_data['weighted_volume'] = creation_data['volume'] * creation_data['eff_vs_avg'].fillna(1)
    
    return calculate_diversity_score(creation_data['weighted_volume'])

def main():
    conn = get_db_connection()
    league_averages = fetch_league_averages(conn)
    
    report = {}
    weights = {'spatial': 0.4, 'play_type': 0.4, 'creation': 0.2}

    for st in ["Regular Season", "Playoffs"]:
        spatial = calculate_spatial_diversity(conn, league_averages, st)
        play_type = calculate_play_type_diversity(conn, league_averages, st)
        creation = calculate_creation_diversity(conn, league_averages, st)
        
        score = (spatial * weights['spatial'] + 
                 play_type * weights['play_type'] + 
                 creation * weights['creation'])
        
        report[st] = {
            'Spatial Diversity': spatial,
            'Play-Type Diversity': play_type,
            'Creation Diversity': creation,
            'Overall Score': score
        }

    print("James Harden - 2024-25 Method Resilience Score Report")
    print("="*60)
    for season_type, data in report.items():
        print(f"\n{season_type}:")
        for key, value in data.items():
            print(f"  - {key}: {value:.2f}")
    
    delta = report['Playoffs']['Overall Score'] - report['Regular Season']['Overall Score']
    print("\n" + "="*60)
    print(f"RESILIENCE DELTA: {delta:+.2f}")
    print("="*60)

    conn.close()

if __name__ == "__main__":
    main()
