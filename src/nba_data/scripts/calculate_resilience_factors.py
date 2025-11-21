"""
Calculate Friction and Dependency metrics for the Extended Resilience Framework.

This script implements the "Philosophical Pivot" metrics:
1. Friction Score (Points per Touch-Second) - Measures Opportunity Density
2. Dependency Score (Assisted Rate) - Measures Creation Independence
"""

import sys
import sqlite3
import pandas as pd
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.db.schema import NBADatabaseSchema

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def calculate_resilience_factors(db_path: str = "data/nba_stats.db"):
    """Calculate and display Friction and Dependency scores."""
    
    if not Path(db_path).exists():
        logger.error(f"Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    
    # We need data from Tracking (Touches, Time of Poss) and Advanced (Usage, TS%)
    query = """
    SELECT 
        p.player_name,
        t.team_abbreviation,
        s.season,
        tr.touches,
        tr.time_of_possession, -- Total time of possession in minutes? No, usually it's AVG seconds per touch * Touches or similar. 
                               -- NBA API 'TIME_OF_POSS' is usually total minutes. Let's verify units.
                               -- Actually NBA tracking usually gives 'AVG_SEC_PER_TOUCH' and 'TOUCHES'.
                               -- Let's check what columns we actually have in player_tracking_stats.
                               
        -- We have to assume the columns exist based on population.
        -- The schema has 'touches', 'avg_sec_per_touch' (maybe? let's check schema), 
        -- Wait, looking at schema.py, we have:
        -- 'touches', 'pass', 'dribbles', etc.
        -- We need to verify the exact column names for Time of Possession.
        
        adv.true_shooting_percentage as ts_pct,
        adv.usage_percentage as usg_pct,
        pss.points,
        pss.field_goals_made,
        pss.assists
        
    FROM player_season_stats pss
    JOIN players p ON pss.player_id = p.player_id
    JOIN teams t ON pss.team_id = t.team_id
    JOIN player_advanced_stats adv ON pss.player_id = adv.player_id AND pss.season = adv.season AND pss.team_id = adv.team_id
    LEFT JOIN player_tracking_stats tr ON pss.player_id = tr.player_id AND pss.season = tr.season AND pss.team_id = tr.team_id
    WHERE pss.season = '2024-25' AND pss.games_played > 10 AND pss.minutes_played > 15
    ORDER BY pss.points DESC
    LIMIT 50
    """
    
    # Let's first inspect the tracking table columns to be sure
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(player_tracking_stats)")
    columns = [info[1] for info in cursor.fetchall()]
    
    logger.info(f"Tracking Columns found: {len(columns)}")
    # We are looking for something like 'avg_sec_per_touch' or 'time_of_poss'.
    # Based on schema.py earlier:
    # It has 'touches', 'avg_speed', 'dist_feet', etc. 
    # It DOES NOT seem to have 'avg_sec_per_touch' explicitly listed in the CREATE TABLE provided in the prompt history?
    # Wait, I need to re-read the schema I just created.
    
    # In schema.py: 
    # drive_*, catch_shoot_*, pull_up_*, paint_touch_*, post_touch_*, elbow_touch_*
    # It does NOT have general "Front Court Touches" or "Time of Possession" in the simplified schema?
    # It has 'touches'.
    
    # If we lack 'Time of Possession', we can't calculate Friction exactly as (PTS / Time).
    # We might need to infer it or check if we missed a metric mapping.
    
    # Let's check the 'leaguedashptstats' mappings in data_fetcher.py.
    # It fetches 'Drives', 'CatchShoot', 'PullUp', 'Passing', 'Rebounding'.
    # There is a "Possessions" endpoint in NBA API (leaguedashptstats with PtMeasureType='Possessions') 
    # which gives 'AVG_SEC_PER_TOUCH'.
    # Did we implement that? 
    
    # Looking at data_fetcher.py in previous turn:
    # It fetches 'Drives', 'CatchShoot', 'PullUp', 'Paint', 'Post', 'Elbow', 'Efficiency', 'Speed', 'Passing', 'Rebounding'.
    # It DOES NOT appear to fetch the general 'Possessions' dataset which contains Time of Possession.
    
    # CRITICAL FINDING: We are missing the specific datasource for Friction (Time of Possession).
    # We have 'drives', 'touches' (total), but not the *duration* of those touches globally.
    
    # HOWEVER: We do have 'dribbles' (maybe? 'avg_dribbles'?) 
    # The schema has 'drives', 'pass_made'. 
    
    # Pivot: We can approximate Friction using 'Drives' and 'Pull Up' frequency as a proxy for "Ball Dominance".
    # Or we can add the 'Possessions' tracking call to the fetcher.
    
    # Plan: I will update the Data Fetcher to get 'Possessions' tracking data.
    # But first, let's try to calculate "Dependency" (Assisted Rate).
    # We need %FGM Assisted.
    # Standard box score doesn't give %Assisted for the *player* (it gives it for the team).
    # Actually 'scoring' endpoint gives %Assisted.
    # Or we can use 'catch_shoot_fgm' + 'cut_fgm' (if we had it) vs 'pull_up_fgm'.
    
    # We DO have:
    # - catch_shoot_field_goals_made
    # - pull_up_field_goals_made
    # - drive_field_goals_made (usually unassisted)
    
    # Dependency Proxy = (Catch&Shoot FGM) / (Total FGM)
    # Self-Creation Proxy = (Pull Up FGM + Drive FGM) / (Total FGM)
    
    pass 

if __name__ == "__main__":
    calculate_resilience_factors()

