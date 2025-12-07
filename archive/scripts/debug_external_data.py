#!/usr/bin/env python3
"""
Debug: Check actual player names in external NBA Stats API data
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))

from src.nba_data.api.nba_stats_client import NBAStatsClient

def debug_player_names():
    """Check what player names look like in external data."""

    client = NBAStatsClient()

    try:
        playoff_data = client.get_league_player_playoff_advanced_stats(season="2023-24")

        if not playoff_data.get('resultSets') or not playoff_data['resultSets'][0].get('rowSet'):
            print("No data received")
            return

        headers = playoff_data['resultSets'][0]['headers']
        rows = playoff_data['resultSets'][0]['rowSet']
        df = pd.DataFrame(rows, columns=headers)

        print(f"Total players: {len(df)}")
        print("\nFirst 10 player names:")
        for i, row in df.head(10).iterrows():
            print(f"  {row['PLAYER_NAME']}")

        # Look for players containing key names
        search_terms = ['Jokić', 'Dončić', 'Butler', 'Curry', 'Giannis', 'Antetokounmpo']
        print(f"\nSearching for key players:")

        for term in search_terms:
            matches = df[df['PLAYER_NAME'].str.contains(term, case=False, na=False)]
            if not matches.empty:
                print(f"  {term}: Found {len(matches)} matches")
                for _, player in matches.iterrows():
                    print(f"    - {player['PLAYER_NAME']} ({player.get('TEAM_ABBREVIATION', 'N/A')}) - TS%: {player.get('TS_PCT', 'N/A')}, GP: {player.get('GP', 'N/A')}")
            else:
                print(f"  {term}: No matches found")

        # Check for Miami Heat and Golden State players (teams that made playoffs)
        print(f"\nMiami Heat players:")
        heat_players = df[df['TEAM_ABBREVIATION'] == 'MIA']
        for _, player in heat_players.iterrows():
            print(f"  - {player['PLAYER_NAME']} - TS%: {player.get('TS_PCT', 'N/A')}, GP: {player.get('GP', 'N/A')}")

        print(f"\nGolden State Warriors players:")
        warriors_players = df[df['TEAM_ABBREVIATION'] == 'GSW']
        if warriors_players.empty:
            print("  No GSW players found in playoffs")
        else:
            for _, player in warriors_players.iterrows():
                print(f"  - {player['PLAYER_NAME']} - TS%: {player.get('TS_PCT', 'N/A')}, GP: {player.get('GP', 'N/A')}")

        # Show teams represented
        print(f"\nTeams represented: {sorted(df['TEAM_ABBREVIATION'].unique())}")

        # Show available columns
        print(f"\nAvailable columns in playoff data:")
        print(f"  {list(df.columns)}")

        # Show some stats for first few players
        print(f"\nSample stats for first 5 players:")
        for i, row in df.head(5).iterrows():
            print(f"  {row['PLAYER_NAME']}: TS%={row.get('TS_PCT', 'N/A')}, GP={row.get('GP', 'N/A')}, USG%={row.get('USG_PCT', 'N/A')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_player_names()
