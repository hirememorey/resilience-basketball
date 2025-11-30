import sys
import os
import argparse
import pandas as pd
import logging
from pathlib import Path
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.nba_data.api.nba_stats_client import NBAStatsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_team_defense_stats(client, season, season_type="Regular Season"):
    """
    Fetch and merge team defensive stats.
    Requires two API calls:
    1. MeasureType='Advanced' for DEF_RATING
    2. MeasureType='Opponent' for OPP_EFG_PCT and OPP_FTA_RATE
    """
    logger.info(f"Fetching defensive stats for {season} ({season_type})...")
    
    try:
        # 1. Fetch Advanced Stats (for DEF_RATING)
        logger.info("Fetching Advanced stats...")
        adv_response = client._make_request("leaguedashteamstats", {
            "MeasureType": "Advanced",
            "PerMode": "PerGame",
            "PlusMinus": "N",
            "PaceAdjust": "N",
            "Rank": "N",
            "LeagueID": "00",
            "Season": season,
            "SeasonType": season_type,
            "Outcome": "",
            "Location": "",
            "Month": "0",
            "SeasonSegment": "",
            "DateFrom": "",
            "DateTo": "",
            "OpponentTeamID": "0",
            "VsConference": "",
            "VsDivision": "",
            "TeamID": "0",
            "Conference": "",
            "Division": "",
            "GameSegment": "",
            "Period": "0",
            "ShotClockRange": "",
            "LastNGames": "0",
            "GameScope": "",
            "PlayerExperience": "",
            "PlayerPosition": "",
            "StarterBench": "",
            "DraftYear": "",
            "DraftPick": "",
            "College": "",
            "Country": "",
            "Height": "",
            "Weight": "",
            "TwoWay": "0",
            "ISTRound": "",
            "PORound": "0",
        })
        
        adv_df = pd.DataFrame(
            adv_response['resultSets'][0]['rowSet'],
            columns=adv_response['resultSets'][0]['headers']
        )
        
        # 2. Fetch Opponent Stats (for OPP_EFG_PCT, OPP_FTA_RATE)
        logger.info("Fetching Opponent stats...")
        opp_response = client._make_request("leaguedashteamstats", {
            "MeasureType": "Opponent",
            "PerMode": "PerGame",
            "PlusMinus": "N",
            "PaceAdjust": "N",
            "Rank": "N",
            "LeagueID": "00",
            "Season": season,
            "SeasonType": season_type,
            "Outcome": "",
            "Location": "",
            "Month": "0",
            "SeasonSegment": "",
            "DateFrom": "",
            "DateTo": "",
            "OpponentTeamID": "0",
            "VsConference": "",
            "VsDivision": "",
            "TeamID": "0",
            "Conference": "",
            "Division": "",
            "GameSegment": "",
            "Period": "0",
            "ShotClockRange": "",
            "LastNGames": "0",
            "GameScope": "",
            "PlayerExperience": "",
            "PlayerPosition": "",
            "StarterBench": "",
            "DraftYear": "",
            "DraftPick": "",
            "College": "",
            "Country": "",
            "Height": "",
            "Weight": "",
            "TwoWay": "0",
            "ISTRound": "",
            "PORound": "0",
        })
        
        opp_df = pd.DataFrame(
            opp_response['resultSets'][0]['rowSet'],
            columns=opp_response['resultSets'][0]['headers']
        )
        
        # Calculate derived metrics if missing
        if 'OPP_EFG_PCT' not in opp_df.columns:
            # eFG% = (FGM + 0.5 * 3PM) / FGA
            opp_df['OPP_EFG_PCT'] = (opp_df['OPP_FGM'] + 0.5 * opp_df['OPP_FG3M']) / opp_df['OPP_FGA']
            
        if 'OPP_FTA_RATE' not in opp_df.columns:
            # FTR = FTA / FGA
            opp_df['OPP_FTA_RATE'] = opp_df['OPP_FTA'] / opp_df['OPP_FGA']
        
        # Merge datasets
        merged_df = pd.merge(
            adv_df[['TEAM_ID', 'TEAM_NAME', 'DEF_RATING']],
            opp_df[['TEAM_ID', 'OPP_EFG_PCT', 'OPP_FTA_RATE']],
            on='TEAM_ID',
            how='inner'
        )
        
        return merged_df
        
    except Exception as e:
        logger.error(f"Error fetching defensive stats for {season}: {e}")
        return pd.DataFrame()

def calculate_defensive_context_score(row):
    """
    Calculate composite defensive context score (0-100).
    
    Formula:
    - DR score = 100 * (130 - def_rating) / 40
    - eFG score = 100 * (0.60 - opp_efg) / 0.20
    - FTR score = 100 * (0.35 - opp_ft_rate) / 0.20
    - DCS = 0.60 * DR + 0.25 * eFG + 0.15 * FTR
    """
    # Extract metrics
    dr = row['DEF_RATING']
    efg = row['OPP_EFG_PCT']
    ftr = row['OPP_FTA_RATE']
    
    # Normalize components
    dr_score = 100 * (130 - dr) / 40
    efg_score = 100 * (0.60 - efg) / 0.20
    ftr_score = 100 * (0.35 - ftr) / 0.20
    
    # Weighted composite
    dcs = (0.60 * dr_score) + (0.25 * efg_score) + (0.15 * ftr_score)
    
    # Clamp to 0-100
    return max(0, min(100, dcs))

def main():
    parser = argparse.ArgumentParser(description='Collect Defensive Context Stats')
    parser.add_argument('--seasons', nargs='+', help='Seasons to collect (e.g. 2023-24)', required=True)
    args = parser.parse_args()
    
    client = NBAStatsClient()
    Path("data").mkdir(exist_ok=True)
    
    for season in args.seasons:
        logger.info(f"Processing {season}...")
        
        # Fetch Regular Season Defense
        rs_df = fetch_team_defense_stats(client, season, "Regular Season")
        if not rs_df.empty:
            # Calculate DCS
            rs_df['def_context_score'] = rs_df.apply(calculate_defensive_context_score, axis=1)
            
            # Save
            output_path = f"data/defensive_context_{season}.csv"
            rs_df.to_csv(output_path, index=False)
            logger.info(f"Saved {len(rs_df)} teams to {output_path}")
        else:
            logger.warning(f"No data saved for {season}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()

