import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from nba_data.api.nba_stats_client import NBAStatsClient

def debug_luka():
    client = NBAStatsClient()
    season = "2019-20"
    
    print(f"Fetching {season} RS stats...")
    
    # Fetch Base
    base = client.get_league_player_base_stats(season=season, season_type="Regular Season")
    headers = base['resultSets'][0]['headers']
    rows = base['resultSets'][0]['rowSet']
    df_base = pd.DataFrame(rows, columns=headers)
    
    print(f"Total players found: {len(df_base)}")
    print("First 5 players:", df_base['PLAYER_NAME'].head().tolist())
    
    luka = df_base[df_base['PLAYER_NAME'].str.contains("Luka", case=False)]
    if luka.empty:
        print("❌ 'Luka' NOT found in Base stats")
    else:
        print("✅ 'Luka' FOUND in Base stats")
        print(luka[['PLAYER_NAME', 'GP', 'MIN']].to_string())
        
    # Fetch Advanced
    adv = client.get_league_player_advanced_stats(season=season, season_type="Regular Season")
    headers_adv = adv['resultSets'][0]['headers']
    rows_adv = adv['resultSets'][0]['rowSet']
    df_adv = pd.DataFrame(rows_adv, columns=headers_adv)
    
    luka_adv = df_adv[df_adv['PLAYER_NAME'].str.contains("Doncic", case=False)]
    if luka_adv.empty:
        print("❌ Luka NOT found in Advanced stats")
    else:
        print("✅ Luka FOUND in Advanced stats")
        
    # Test Merge
    if not luka.empty and not luka_adv.empty:
        merge_cols = ['PLAYER_ID', 'TEAM_ID']
        try:
            merged = pd.merge(df_base, df_adv, on=merge_cols, how='inner', suffixes=('', '_adv'))
            luka_merged = merged[merged['PLAYER_NAME'].str.contains("Doncic", case=False)]
            if luka_merged.empty:
                print("❌ Luka lost during MERGE")
            else:
                print("✅ Luka survived MERGE")
                
            # Test Filter
            luka_merged['GP'] = pd.to_numeric(luka_merged['GP'])
            luka_merged['MIN'] = pd.to_numeric(luka_merged['MIN'])
            
            qualified = luka_merged[
                (luka_merged['GP'] >= 50) & 
                (luka_merged['MIN'] >= 20.0)
            ]
            
            if qualified.empty:
                print("❌ Luka filtered out by QUALIFICATION (GP >= 50, MIN >= 20)")
                print(f"GP: {luka_merged['GP'].values[0]}, MIN: {luka_merged['MIN'].values[0]}")
            else:
                print("✅ Luka qualified")
                
        except Exception as e:
            print(f"Merge failed: {e}")

if __name__ == "__main__":
    debug_luka()
