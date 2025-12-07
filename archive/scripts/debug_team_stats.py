
import sys
import os
sys.path.append(os.getcwd())
from src.nba_data.api.nba_stats_client import NBAStatsClient
import pandas as pd

def debug_team_stats():
    client = NBAStatsClient()
    print("Fetching Team Stats...")
    # Fetch Advanced stats to get Defensive Rating (DEF_RATING)
    data = client.get_league_team_stats(season="2023-24", measure_type="Advanced")
    
    if data and 'resultSets' in data:
        headers = data['resultSets'][0]['headers']
        rows = data['resultSets'][0]['rowSet']
        df = pd.DataFrame(rows, columns=headers)
        print("Columns:", df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df[['TEAM_ID', 'TEAM_NAME', 'DEF_RATING']].head())
        
        # Check for abbreviation
        if 'TEAM_ABBREVIATION' in df.columns:
            print("\nFound TEAM_ABBREVIATION!")
        else:
            print("\nTEAM_ABBREVIATION not found in Advanced stats.")

    print("\nFetching Base Stats...")
    data_base = client.get_league_team_stats(season="2023-24", measure_type="Base")
    if data_base and 'resultSets' in data_base:
        headers = data_base['resultSets'][0]['headers']
        rows = data_base['resultSets'][0]['rowSet']
        df_base = pd.DataFrame(rows, columns=headers)
        if 'TEAM_ABBREVIATION' in df_base.columns:
             print("Found TEAM_ABBREVIATION in Base stats!")
             print(df_base[['TEAM_ID', 'TEAM_ABBREVIATION']].head())

            
    else:
        print("No data returned.")

if __name__ == "__main__":
    debug_team_stats()

