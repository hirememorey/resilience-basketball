import sqlite3
import pandas as pd
from typing import Dict, Tuple

DB_PATH = "data/nba_stats.db"

def get_db_connection():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def define_court_zones(df: pd.DataFrame) -> pd.Series:
    """
    Categorizes shots into predefined court zones based on x, y coordinates.
    """
    x, y = df['loc_x'], df['loc_y']

    # Restricted Area
    is_ra = (x.abs() <= 4) & (y <= 4.25)

    # In The Paint (Non-RA)
    is_paint = (x.abs() <= 8) & (y <= 19) & ~is_ra

    # Mid-Range
    is_mid_range = (
        ((x.abs() > 8) & (y <= 19)) |
        ((x.abs() <= 22) & (y > 19)) |
        (df['shot_type'] == '2PT Field Goal') & ~is_ra & ~is_paint
    )

    # Corner 3s
    is_corner_3 = (x.abs() > 22) & (y <= 7.8)

    # Above the Break 3
    is_above_break_3 = (df['shot_type'] == '3PT Field Goal') & ~is_corner_3

    conditions = [
        is_ra,
        is_paint,
        is_mid_range,
        (is_corner_3) & (x < 0),
        (is_corner_3) & (x >= 0),
        is_above_break_3
    ]
    choices = [
        'Restricted Area',
        'In The Paint (Non-RA)',
        'Mid-Range',
        'Left Corner 3',
        'Right Corner 3',
        'Above the Break 3'
    ]
    return pd.Series(pd.NA, index=df.index).fillna(pd.Series(np.select(conditions, choices, default='Other'), index=df.index))

def calculate_spatial_averages(conn: sqlite3.Connection, season: str, season_type: str) -> Dict[str, float]:
    """
    Calculates the league-average eFG% for each defined court zone.
    """
    query = f"""
        SELECT loc_x, loc_y, shot_made_flag, shot_type
        FROM player_shot_locations
        WHERE season = '{season}' AND season_type = '{season_type.replace(" ", "")}'
    """
    df = pd.read_sql_query(query, conn)
    df['zone'] = define_court_zones(df)

    # Calculate points from each shot
    df['points'] = 0
    df.loc[df['shot_made_flag'] == 1, 'points'] = df['shot_type'].apply(lambda x: 3 if '3PT' in x else 2)
    
    # Calculate eFG% = (FGM + 0.5 * 3PM) / FGA
    three_pointers_made = df[(df['shot_made_flag'] == 1) & (df['shot_type'] == '3PT Field Goal')].groupby('zone').size()
    field_goals_made = df[df['shot_made_flag'] == 1].groupby('zone').size()
    field_goals_attempted = df.groupby('zone').size()

    zone_stats = pd.DataFrame({
        'FGM': field_goals_made,
        'FGA': field_goals_attempted,
        '3PM': three_pointers_made
    }).fillna(0)

    zone_stats['eFG%'] = (zone_stats['FGM'] + 0.5 * zone_stats['3PM']) / zone_stats['FGA']
    
    return zone_stats['eFG%'].to_dict()

def calculate_play_type_averages(conn: sqlite3.Connection, season: str, season_type: str) -> Dict[str, float]:
    """
    Calculates the league-average Points Per Possession (PPP) for each play type.
    """
    table_name = "player_playtype_stats" if season_type == "Regular Season" else "player_playoff_playtype_stats"
    query = f"""
        SELECT play_type, SUM(possessions) as total_possessions, SUM(points) as total_points
        FROM {table_name}
        WHERE season = '{season}'
        GROUP BY play_type
    """
    df = pd.read_sql_query(query, conn)
    df['ppp'] = df['total_points'] / df['total_possessions']
    return df.set_index('play_type')['ppp'].to_dict()

def calculate_creation_averages(conn: sqlite3.Connection, season: str, season_type: str) -> Dict[str, float]:
    """
    Calculates league-average efficiency for different shot creation types.
    """
    table_name = "player_tracking_stats" if season_type == "Regular Season" else "player_playoff_tracking_stats"
    query = f"SELECT * FROM {table_name} WHERE season = '{season}'"
    df = pd.read_sql_query(query, conn)

    averages = {}
    
    # Catch & Shoot eFG%
    total_cs_fga = df['catch_shoot_field_goals_attempted'].sum()
    total_cs_fgm = df['catch_shoot_field_goals_made'].sum()
    total_cs_3pm = df['catch_shoot_three_pointers_made'].sum()
    averages['Catch & Shoot'] = (total_cs_fgm + 0.5 * total_cs_3pm) / total_cs_fga if total_cs_fga else 0

    # Pull Up eFG%
    total_pu_fga = df['pull_up_field_goals_attempted'].sum()
    total_pu_fgm = df['pull_up_field_goals_made'].sum()
    total_pu_3pm = df['pull_up_three_pointers_made'].sum()
    averages['Pull-Up'] = (total_pu_fgm + 0.5 * total_pu_3pm) / total_pu_fga if total_pu_fga else 0

    # Drives Points per Drive
    total_drives = df['drives'].sum()
    total_drive_points = df['drive_points'].sum()
    averages['Drives'] = total_drive_points / total_drives if total_drives else 0
    
    return averages

def store_averages(conn: sqlite3.Connection, season: str, season_type: str, averages: Dict[str, Dict[str, float]]):
    """
    Stores the calculated league averages in the database.
    """
    cursor = conn.cursor()
    for metric_type, values in averages.items():
        for metric_name, value in values.items():
            cursor.execute("""
                INSERT OR REPLACE INTO league_averages 
                (season, season_type, metric_type, metric_name, value)
                VALUES (?, ?, ?, ?, ?)
            """, (season, season_type, metric_type, metric_name, value))
    conn.commit()
    print(f"✅ Stored league averages for {season} {season_type}")

def main():
    """Main function to calculate and store all league averages."""
    season = "2024-25"
    conn = get_db_connection()

    for season_type in ["Regular Season", "Playoffs"]:
        print(f"\nCalculating league averages for {season} {season_type}...")
        
        spatial = calculate_spatial_averages(conn, season, season_type)
        play_type = calculate_play_type_averages(conn, season, season_type)
        creation = calculate_creation_averages(conn, season, season_type)

        all_averages = {
            'spatial': spatial,
            'play_type': play_type,
            'creation': creation
        }
        
        store_averages(conn, season, season_type, all_averages)

    conn.close()

if __name__ == "__main__":
    import numpy as np
    main()
