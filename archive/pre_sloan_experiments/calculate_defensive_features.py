"""
Calculate Defensive Stress Vector Features.


Playoff resilience is two-way. Players who are defensive liabilities get "hunted"
in the playoffs (The "Trae Young Rule"). This script calculates features to
quantify defensive liability and physical survivability.

Features Generated:

DEF_LIABILITY: Player DefRtg - Team DefRtg (Positive = Worse than team)

SIZE_RATING: Composite of Height and Weight (Proxy for switchability/targetability)

DEF_ACTIVITY: Composite of STL%, BLK%, DREB%
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path

Add project root to path

sys.path.append(str(Path(file).resolve().parent.parent.parent.parent))

from src.nba_data.api.nba_stats_client import NBAStatsClient
from src.nba_data.constants import TEAMS

Setup Logging

logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler("logs/defensive_features.log"),
logging.StreamHandler(sys.stdout)
]
)
logger = logging.getLogger(name)

class DefensiveFeatureGenerator:
def init(self):
self.client = NBAStatsClient()
self.data_dir = Path("data")
self.results_dir = Path("results")
self.results_dir.mkdir(parents=True, exist_ok=True)

code
Code
download
content_copy
expand_less
def load_team_defense(self, season: str) -> pd.DataFrame:
    """Load team defensive ratings from defensive context files."""
    file_path = self.data_dir / f"defensive_context_{season}.csv"
    if not file_path.exists():
        logger.warning(f"Defensive context file not found for {season}")
        return pd.DataFrame()
    
    df = pd.read_csv(file_path)
    # Ensure we have TEAM_ID and DEF_RATING
    if 'TEAM_ID' in df.columns and 'DEF_RATING' in df.columns:
        return df[['TEAM_ID', 'DEF_RATING']].rename(columns={'DEF_RATING': 'TEAM_DEF_RATING'})
    return pd.DataFrame()

def fetch_player_defense(self, season: str) -> pd.DataFrame:
    """Fetch player defensive stats and physicals."""
    logger.info(f"Fetching player defense stats for {season}...")
    
    try:
        # 1. Advanced Stats for DefRtg, PIE (as proxy for overall impact), etc.
        adv_response = self.client.get_league_player_advanced_stats(season=season)
        
        headers = adv_response['resultSets'][0]['headers']
        rows = adv_response['resultSets'][0]['rowSet']
        df_adv = pd.DataFrame(rows, columns=headers)
        
        # Select relevant columns
        # DEF_RATING in player stats is "Team's DefRtg when player is on court" (usually) 
        # or individual DRtg depending on API version. 
        # NBA.com 'Advanced' endpoint usually gives individual DRtg estimate or On-Court.
        cols_adv = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'DEF_RATING', 'MIN', 'USG_PCT']
        df_adv = df_adv[[c for c in cols_adv if c in df_adv.columns]]

        # 2. Defense/Misc Stats for STL, BLK, DREB (Activity)
        # Actually, let's use Base stats for counting stats if needed, or Advanced has percentages
        # Advanced has DREB_PCT. It does NOT usually have STL% or BLK% in standard view, 
        # but let's check what we usually get.
        # Usually we get AST_PCT, AST_TO, AST_RATIO, OREB_PCT, DREB_PCT, REB_PCT, TM_TOV_PCT, EFG_PCT, TS_PCT, USG_PCT, PACE, PIE
        # We lack STL% and BLK% in standard 'Advanced' call. 
        # We can approximate activity using Base stats per MIN if needed, or make a separate call for 'Defense' measure type.
        
        # For simplicity and speed, let's use 'Base' to calculate per-minute activity
        base_response = self.client.get_league_player_base_stats(season=season)
        base_headers = base_response['resultSets'][0]['headers']
        base_rows = base_response['resultSets'][0]['rowSet']
        df_base = pd.DataFrame(base_rows, columns=base_headers)
        
        # Merge Base columns: STL, BLK, DREB, MIN (to calc rates)
        df_base = df_base[['PLAYER_ID', 'STL', 'BLK', 'DREB', 'MIN', 'GP']]
        
        # 3. Metadata for Height/Weight
        # This is hard to fetch batch per season.
        # We often rely on `commonplayerinfo` which is per player.
        # Alternatively, `leaguedashplayerbiostats` gives height/weight for everyone.
        bio_response = self.client._make_request("leaguedashplayerbiostats", {
            "LeagueID": "00", "Season": season, "SeasonType": "Regular Season", "PerMode": "PerGame"
        })
        bio_headers = bio_response['resultSets'][0]['headers']
        bio_rows = bio_response['resultSets'][0]['rowSet']
        df_bio = pd.DataFrame(bio_rows, columns=bio_headers)
        
        # Columns: PLAYER_ID, PLAYER_HEIGHT, PLAYER_WEIGHT
        # Height format is usually "6-7". Need to parse.
        
        # Merge everything
        df_merged = pd.merge(df_adv, df_base, on='PLAYER_ID', how='inner')
        df_merged = pd.merge(df_merged, df_bio[['PLAYER_ID', 'PLAYER_HEIGHT', 'PLAYER_WEIGHT']], on='PLAYER_ID', how='left')
        
        return df_merged

    except Exception as e:
        logger.error(f"Error fetching player defense for {season}: {e}")
        return pd.DataFrame()

def parse_height(self, height_str):
    """Convert '6-7' to inches."""
    if pd.isna(height_str): return None
    try:
        if '-' in str(height_str):
            feet, inches = str(height_str).split('-')
            return int(feet) * 12 + int(inches)
        return None
    except:
        return None

def calculate_features(self, df_players: pd.DataFrame, df_teams: pd.DataFrame) -> pd.DataFrame:
    """Calculate derived defensive features."""
    
    # Merge player and team data
    df = pd.merge(df_players, df_teams, on='TEAM_ID', how='left')
    
    # 1. Defensive Liability (Player DRtg - Team DRtg)
    # Note: In NBA stats, Lower DRtg is better.
    # If Player DRtg (115) > Team DRtg (110), they are worse than team average.
    # Positive Diff = Liability.
    df['DEF_LIABILITY'] = df['DEF_RATING'] - df['TEAM_DEF_RATING']
    
    # 2. Size Rating
    # Parse height
    df['HEIGHT_INCHES'] = df['PLAYER_HEIGHT'].apply(self.parse_height)
    df['WEIGHT_LBS'] = pd.to_numeric(df['PLAYER_WEIGHT'], errors='coerce')
    
    # Normalize Size (Simple proxy: Height + Weight/10)
    # This gives a rough "physical presence" score.
    # Small guard: 74 + 190/10 = 93
    # Wing: 79 + 220/10 = 101
    # Big: 84 + 260/10 = 110
    # We can Z-score this later, but raw is fine for now.
    df['SIZE_RATING'] = df['HEIGHT_INCHES'] + (df['WEIGHT_LBS'] / 10.0)
    
    # 3. Defensive Activity
    # Stocks per 36 or similar.
    # Let's do (STL + BLK) per 36 minutes
    df['MIN_TOTAL'] = df['MIN'] * df['GP']
    # Avoid div by zero
    df['DEF_ACTIVITY'] = np.where(
        df['MIN_TOTAL'] > 0,
        ((df['STL'] + df['BLK']) / df['MIN_TOTAL']) * 36,
        0
    )
    
    return df[['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'DEF_LIABILITY', 'SIZE_RATING', 'DEF_ACTIVITY']]

def run(self, seasons: list):
    all_features = []
    
    for season in seasons:
        logger.info(f"Processing Defensive Features for {season}...")
        
        df_teams = self.load_team_defense(season)
        if df_teams.empty:
            logger.warning(f"Skipping {season} (missing team data)")
            continue
            
        df_players = self.fetch_player_defense(season)
        if df_players.empty:
            logger.warning(f"Skipping {season} (missing player data)")
            continue
            
        df_players['SEASON'] = season
        
        features = self.calculate_features(df_players, df_teams)
        all_features.append(features)
        
    if not all_features:
        logger.error("No features generated.")
        return
        
    final_df = pd.concat(all_features, ignore_index=True)
    
    output_path = self.results_dir / "defensive_features.csv"
    final_df.to_csv(output_path, index=False)
    logger.info(f"✅ Saved defensive features to {output_path}")
    logger.info(f"Generated {len(final_df)} rows")

if name == "main":
# Run for all relevant seasons
seasons = [
'2015-16', '2016-17', '2017-18', '2018-19', '2019-20',
'2020-21', '2021-22', '2022-23', '2023-24', '2024-25'
]

code
Code
download
content_copy
expand_less
generator = DefensiveFeatureGenerator()
generator.run(seasons)