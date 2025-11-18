#!/usr/bin/env python3
"""
Populate Player Game Logs

This script fetches and populates player game logs for all players across multiple seasons.
This granular data is essential for calculating Role Scalability (efficiency slopes) and
validating resilience metrics with larger sample sizes.
"""

import sqlite3
import time
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
from tqdm import tqdm
import pandas as pd
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.nba_data.api.nba_stats_client import NBAStatsClient
from src.nba_data.db.schema import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/populate_game_logs.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = "data/nba_stats.db"
SEASONS = [
    "2015-16", "2016-17", "2017-18", "2018-19", "2019-20",
    "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"
]

# Thread-local storage for database connections and clients
thread_local = threading.local()

def get_db_connection():
    """Get a thread-local database connection."""
    if not hasattr(thread_local, "conn"):
        thread_local.conn = sqlite3.connect(DB_PATH)
    return thread_local.conn

def get_client():
    """Get a thread-local API client."""
    if not hasattr(thread_local, "client"):
        thread_local.client = NBAStatsClient()
    return thread_local.client

def get_active_players_for_season(conn: sqlite3.Connection, season: str) -> List[int]:
    """Get list of player IDs active in a specific season."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT player_id FROM player_season_stats WHERE season = ?", 
        (season,)
    )
    return [row[0] for row in cursor.fetchall()]

def process_game_logs(logs: List[Dict[str, Any]], season: str, season_type: str) -> List[Tuple]:
    """Process raw game logs into database tuples."""
    processed_logs = []
    
    for log in logs:
        try:
            # Extract basic stats
            processed_logs.append((
                log.get('PLAYER_ID'),
                log.get('GAME_ID'),
                season,
                season_type,
                log.get('GAME_DATE'),
                log.get('TEAM_ID'),
                log.get('MATCHUP'),
                log.get('WL'),
                
                # Stats
                log.get('MIN'),
                log.get('PTS'),
                log.get('FGM'),
                log.get('FGA'),
                log.get('FG_PCT'),
                log.get('FG3M'),
                log.get('FG3A'),
                log.get('FG3_PCT'),
                log.get('FTM'),
                log.get('FTA'),
                log.get('FT_PCT'),
                log.get('OREB'),
                log.get('DREB'),
                log.get('REB'),
                log.get('AST'),
                log.get('STL'),
                log.get('BLK'),
                log.get('TOV'),
                log.get('PF'),
                log.get('PLUS_MINUS')
            ))
        except Exception as e:
            logger.error(f"Error processing log for game {log.get('GAME_ID')}: {e}")
            continue
            
    return processed_logs

def save_game_logs(conn: sqlite3.Connection, logs: List[Tuple]):
    """Save processed game logs to the database."""
    cursor = conn.cursor()
    
    cursor.executemany("""
        INSERT OR REPLACE INTO player_game_logs (
            player_id, game_id, season, season_type, game_date, team_id, matchup, outcome,
            minutes_played, points, field_goals_made, field_goals_attempted, field_goal_percentage,
            three_pointers_made, three_pointers_attempted, three_point_percentage,
            free_throws_made, free_throws_attempted, free_throw_percentage,
            offensive_rebounds, defensive_rebounds, total_rebounds,
            assists, steals, blocks, turnovers, personal_fouls, plus_minus
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, logs)
    
    conn.commit()

def process_player_logs(player_id: int, season: str) -> int:
    """Process game logs for a single player (Worker function)."""
    client = get_client()
    conn = get_db_connection()
    processed_count = 0
    
    try:
        # Fetch Regular Season logs
        data = client.get_player_game_logs(
            player_id=player_id, 
            season=season,
            season_type="Regular Season"
        )
        
        if data and 'resultSets' in data:
            # Parse result sets
            headers = data['resultSets'][0]['headers']
            rows = data['resultSets'][0]['rowSet']
            
            # Convert to list of dicts
            logs = [dict(zip(headers, row)) for row in rows]
            
            if logs:
                processed = process_game_logs(logs, season, "Regular Season")
                save_game_logs(conn, processed)
                processed_count += len(processed)
        
        # Fetch Playoff logs
        playoff_data = client.get_player_game_logs(
            player_id=player_id,
            season=season,
            season_type="Playoffs"
        )
        
        if playoff_data and 'resultSets' in playoff_data:
            headers = playoff_data['resultSets'][0]['headers']
            rows = playoff_data['resultSets'][0]['rowSet']
            
            logs = [dict(zip(headers, row)) for row in rows]
            
            if logs:
                processed = process_game_logs(logs, season, "Playoffs")
                save_game_logs(conn, processed)
                processed_count += len(processed)
                
    except Exception as e:
        logger.error(f"Error fetching logs for player {player_id} in {season}: {e}")
        
    return processed_count

def main():
    parser = argparse.ArgumentParser(description='Populate player game logs')
    parser.add_argument('--season', type=str, help='Specific season to populate (e.g., 2023-24)')
    parser.add_argument('--historical', action='store_true', help='Populate all historical seasons')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers')
    args = parser.parse_args()

    # Initialize database schema if needed
    # init_database() # Assuming schema is already active or controlled elsewhere
    
    # Main connection for getting player list
    main_conn = sqlite3.connect(DB_PATH)
    
    # Determine seasons to process
    if args.season:
        seasons_to_process = [args.season]
    elif args.historical:
        seasons_to_process = SEASONS
    else:
        seasons_to_process = ["2024-25"]  # Default to current season

    total_processed = 0
    
    for season in seasons_to_process:
        logger.info(f"Processing game logs for season {season}...")
        
        # Get active players for this season
        player_ids = get_active_players_for_season(main_conn, season)
        logger.info(f"Found {len(player_ids)} active players in {season}")
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            # Create futures for all players
            futures = {
                executor.submit(process_player_logs, pid, season): pid 
                for pid in player_ids
            }
            
            # Monitor progress
            with tqdm(total=len(player_ids), desc=f"Fetching logs for {season}") as pbar:
                for future in as_completed(futures):
                    try:
                        count = future.result()
                        total_processed += count
                    except Exception as e:
                        logger.error(f"Worker failed: {e}")
                    finally:
                        pbar.update(1)
                
    print(f"\n✅ Successfully populated {total_processed} game logs across {len(seasons_to_process)} seasons.")
    main_conn.close()

if __name__ == "__main__":
    main()

