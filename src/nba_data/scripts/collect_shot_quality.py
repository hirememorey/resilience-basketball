
import sys
import os
import pandas as pd
import logging
from pathlib import Path
import argparse
import time
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.nba_data.api.nba_stats_client import NBAStatsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/shot_quality_collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_shot_quality_data(client, season, season_type):
    """
    Fetch aggregated shot quality data for the entire league.
    We need to make 4 calls per season/type:
    1. Very Tight (0-2 ft)
    2. Tight (2-4 ft)
    3. Open (4-6 ft)
    4. Wide Open (6+ ft)
    """
    
    quality_ranges = [
        ("0-2 Feet - Very Tight", "VeryTight"),
        ("2-4 Feet - Tight", "Tight"),
        ("4-6 Feet - Open", "Open"),
        ("6+ Feet - Wide Open", "WideOpen")
    ]
    
    dfs = []
    
    for q_range, q_label in quality_ranges:
        try:
            logger.info(f"Fetching {q_label} shots for {season} {season_type}...")
            
            # The client method 'get_league_player_playoff_shot_stats' maps to 'leaguedashplayerptshot'.
            # We can reuse it but need to pass the 'CloseDefDistRange' param.
            # I'll use the generic _make_request to be flexible or add a dedicated method if needed.
            # Actually, let's use the client properly. I'll update the client to support generic params if needed
            # or just use the existing method and pass the CloseDefDistRange in the kwargs if supported?
            # The current method hardcodes params. I should update the client first to be more flexible
            # or just use the method I added and modify it to accept the range.
            
            # Checking client... I added get_league_player_playoff_shot_stats but it hardcodes params.
            # I will fix the client in a separate step, but for now I'll simulate the call structure.
            
            endpoint = "leaguedashplayerptshot"
            params = {
                "CloseDefDistRange": q_range,
                "College": "",
                "Conference": "",
                "Country": "",
                "DateFrom": "",
                "DateTo": "",
                "Division": "",
                "DraftPick": "",
                "DraftYear": "",
                "DribbleRange": "",
                "GameScope": "",
                "GameSegment": "",
                "GeneralRange": "Overall",
                "Height": "",
                "ISTRound": "",
                "LastNGames": "0",
                "LeagueID": "00",
                "Location": "",
                "Month": "0",
                "OpponentTeamID": "0",
                "Outcome": "",
                "PORound": "0",
                "PaceAdjust": "N",
                "PerMode": "Totals", # We want raw totals to aggregate
                "Period": "0",
                "PlayerExperience": "",
                "PlayerPosition": "",
                "PlusMinus": "N",
                "Rank": "N",
                "Season": season,
                "SeasonSegment": "",
                "SeasonType": season_type,
                "ShotClockRange": "",
                "ShotDistRange": "",
                "StarterBench": "",
                "TeamID": "0",
                "TouchTimeRange": "",
                "VsConference": "",
                "VsDivision": "",
                "Weight": ""
            }
            
            data = client._make_request(endpoint, params)
            
            if data and 'resultSets' in data:
                headers = data['resultSets'][0]['headers']
                rows = data['resultSets'][0]['rowSet']
                df = pd.DataFrame(rows, columns=headers)
                df['SHOT_QUALITY'] = q_label
                df['SEASON_TYPE'] = season_type
                df['SEASON'] = season
                dfs.append(df)
            
            time.sleep(1) # Be nice to the API
            
        except Exception as e:
            logger.error(f"Failed to fetch {q_label}: {e}")
            
    if not dfs:
        return pd.DataFrame()
        
    return pd.concat(dfs, ignore_index=True)

def main():
    parser = argparse.ArgumentParser(description='Collect Shot Quality Data')
    parser.add_argument('--seasons', nargs='+', help='Seasons to collect (e.g. 2023-24)', required=True)
    args = parser.parse_args()
    
    Path("data/shot_quality").mkdir(parents=True, exist_ok=True)
    
    client = NBAStatsClient()
    
    for season in args.seasons:
        logger.info(f"Processing {season}...")
        
        # RS
        rs_df = fetch_shot_quality_data(client, season, "Regular Season")
        # Playoffs
        po_df = fetch_shot_quality_data(client, season, "Playoffs")
        
        full_df = pd.concat([rs_df, po_df], ignore_index=True)
        
        if not full_df.empty:
            output_path = f"data/shot_quality/shot_quality_{season}.csv"
            full_df.to_csv(output_path, index=False)
            logger.info(f"Saved {len(full_df)} records to {output_path}")
        else:
            logger.warning(f"No data found for {season}")

if __name__ == "__main__":
    main()












