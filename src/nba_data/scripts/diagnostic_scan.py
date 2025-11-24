
import sqlite3
import pandas as pd
from pathlib import Path
import sys

# Add src to path to import local modules if needed
sys.path.append(str(Path(__file__).parent.parent.parent))

DB_PATH = "data/nba_stats.db"

def connect_db():
    if not Path(DB_PATH).exists():
        print(f"❌ Database not found at {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def scan_shot_dashboard(conn):
    print("\n--- 1. Diagnostic: Player Shot Dashboard Stats ---")
    table_name = "player_shot_dashboard_stats"
    
    # Check if table exists
    try:
        count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table_name}", conn).iloc[0]['count']
        print(f"Total Rows: {count}")
    except Exception as e:
        print(f"❌ Table {table_name} does not exist or error querying: {e}")
        return

    if count == 0:
        print("❌ Table is EMPTY.")
        return

    # Check for Fragmentation: Are context columns mutually exclusive?
    # We expect a row to represent a specific combination, but the bug report suggests
    # they might be inserted as separate rows where other columns are null/default.
    
    query = """
    SELECT 
        close_def_dist_range, 
        shot_clock_range, 
        dribble_range, 
        shot_dist_range,
        count(*) as freq
    FROM player_shot_dashboard_stats
    GROUP BY close_def_dist_range, shot_clock_range, dribble_range, shot_dist_range
    ORDER BY freq DESC
    LIMIT 10
    """
    print("\nTop 10 Context Combinations:")
    df = pd.read_sql(query, conn)
    print(df)
    
    # Check distinct values for each context column to see if they look valid
    for col in ['close_def_dist_range', 'shot_clock_range', 'dribble_range', 'shot_dist_range']:
        unique_vals = pd.read_sql(f"SELECT DISTINCT {col} FROM {table_name} LIMIT 5", conn)
        print(f"\nSample values for {col}:")
        print(unique_vals[col].tolist())

def scan_friction_data(conn):
    print("\n--- 2. Diagnostic: Friction Score Data (Tracking Stats) ---")
    table_name = "player_tracking_stats"
    
    try:
        count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table_name}", conn).iloc[0]['count']
        print(f"Total Rows: {count}")
    except:
        print(f"❌ Table {table_name} does not exist.")
        return

    if count == 0:
        print("❌ Table is EMPTY.")
        return

    # Check specific columns for Friction Score
    cols = ['avg_sec_per_touch', 'pts_per_touch', 'time_of_poss', 'touches']
    
    # Check for NULLs
    null_counts = pd.read_sql(f"""
        SELECT 
            COUNT(*) - COUNT(avg_sec_per_touch) as missing_sec_per_touch,
            COUNT(*) - COUNT(pts_per_touch) as missing_pts_per_touch,
            COUNT(*) - COUNT(time_of_poss) as missing_time_of_poss,
            COUNT(*) - COUNT(touches) as missing_touches
        FROM {table_name}
    """, conn)
    print("\nMissing Values Count:")
    print(null_counts)

    # Check for Zeros (which might be effectively missing data)
    zero_counts = pd.read_sql(f"""
        SELECT 
            SUM(CASE WHEN avg_sec_per_touch = 0 THEN 1 ELSE 0 END) as zeros_sec_per_touch,
            SUM(CASE WHEN pts_per_touch = 0 THEN 1 ELSE 0 END) as zeros_pts_per_touch,
            SUM(CASE WHEN time_of_poss = 0 THEN 1 ELSE 0 END) as zeros_time_of_poss,
            SUM(CASE WHEN touches = 0 THEN 1 ELSE 0 END) as zeros_touches
        FROM {table_name}
    """, conn)
    print("\nZero Values Count:")
    print(zero_counts)
    
    # Sample Data for a known high-usage player (e.g., Luka Doncic or equivalent if ID known, otherwise random top 5 by touches)
    print("\nSample Data (Top 5 by Touches):")
    sample = pd.read_sql(f"SELECT player_id, season, {', '.join(cols)} FROM {table_name} ORDER BY touches DESC LIMIT 5", conn)
    print(sample)

def scan_team_ratings(conn):
    print("\n--- 3. Diagnostic: Team Defensive Ratings (Crucible Baseline) ---")
    
    # Check if any plausible table exists
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%team%'")
    tables = cursor.fetchall()
    print(f"Existing 'Team' tables: {[t[0] for t in tables]}")
    
    # We know from schema review that team_season_stats is missing, but let's confirm
    if 'team_season_stats' not in [t[0] for t in tables]:
        print("❌ CRITICAL: 'team_season_stats' table MISSING. Cannot calculate Crucible Baseline.")
    else:
        # If it miraculously exists, check for defensive rating
        cols = pd.read_sql("PRAGMA table_info(team_season_stats)", conn)
        if 'def_rtg' in cols['name'].values or 'defensive_rating' in cols['name'].values:
             print("✅ 'team_season_stats' exists and has defensive rating column.")
        else:
             print("⚠️ 'team_season_stats' exists but MIGHT be missing defensive rating.")

if __name__ == "__main__":
    conn = connect_db()
    try:
        scan_shot_dashboard(conn)
        scan_friction_data(conn)
        scan_team_ratings(conn)
    finally:
        conn.close()

