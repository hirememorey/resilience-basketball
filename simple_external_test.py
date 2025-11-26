#!/usr/bin/env python3
"""
Simple External Data Test: Can NBA APIs provide reliable playoff data?

From first principles: Before investing weeks in remediation, test if external
APIs can give us clean playoff data for resilience analysis.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))

from src.nba_data.api.nba_stats_client import NBAStatsClient

def assess_external_data_viability():
    """Simple assessment: Can external APIs provide usable playoff data?"""

    print("🔍 SIMPLE EXTERNAL DATA VIABILITY TEST")
    print("=" * 50)

    client = NBAStatsClient()

    try:
        # Test 1: Can we fetch playoff data?
        print("\n1️⃣  CAN WE FETCH PLAYOFF DATA?")
        playoff_data = client.get_league_player_playoff_advanced_stats(season="2023-24")

        if not playoff_data.get('resultSets') or not playoff_data['resultSets'][0].get('rowSet'):
            print("❌ Cannot fetch playoff data from NBA API")
            return False

        df = pd.DataFrame(playoff_data['resultSets'][0]['rowSet'],
                         columns=playoff_data['resultSets'][0]['headers'])

        print(f"✅ Successfully fetched data for {len(df)} playoff players")

        # Test 2: Is data complete?
        print("\n2️⃣  IS DATA COMPLETE?")
        completeness = df.notna().mean().mean()
        print(".1%")

        if completeness < 0.95:
            print("❌ Data has significant missing values")
            return False
        print("✅ Data is highly complete")

        # Test 3: Are stats in valid ranges?
        print("\n3️⃣  ARE STATS IN VALID RANGES?")
        ts_range = df['TS_PCT'].describe()
        usg_range = df['USG_PCT'].describe()

        ts_valid = (ts_range['min'] >= 0) and (ts_range['max'] <= 1.5)  # Reasonable TS% range
        usg_valid = (usg_range['min'] >= 0) and (usg_range['max'] <= 1.0)  # Usage as decimal

        print(".3f")
        print(".3f")

        if ts_valid and usg_valid:
            print("✅ Stats are in valid ranges")
        else:
            print("❌ Stats have invalid ranges")
            return False

        # Test 4: Do we have key playoff teams?
        print("\n4️⃣  DO WE HAVE KEY PLAYOFF TEAMS?")
        teams_present = set(df['TEAM_ABBREVIATION'].unique())
        expected_teams = {'DEN', 'DAL', 'MIA', 'BOS', 'LAL', 'PHX'}  # 2023-24 playoff teams

        teams_found = len(teams_present.intersection(expected_teams))
        print(f"Expected playoff teams: {expected_teams}")
        print(f"Teams found in data: {sorted(teams_present)}")
        print(f"Key teams present: {teams_found}/{len(expected_teams)}")

        if teams_found >= 4:  # At least half the expected teams
            print("✅ Sufficient playoff teams represented")
        else:
            print("❌ Insufficient playoff teams")
            return False

        # Test 5: Can we find star players?
        print("\n5️⃣  CAN WE FIND STAR PLAYERS?")
        star_players = ['Nikola Jokić', 'Luka Dončić', 'Bam Adebayo', 'Aaron Gordon']
        players_found = 0

        for player in star_players:
            if df['PLAYER_NAME'].str.contains(player, case=False, na=False).any():
                players_found += 1
                player_data = df[df['PLAYER_NAME'].str.contains(player, case=False, na=False)].iloc[0]
                print(f"  ✅ {player}: {player_data['GP']} games, TS%={player_data['TS_PCT']:.3f}")

        print(f"Star players found: {players_found}/{len(star_players)}")

        if players_found >= 3:  # At least 3 of 4 star players
            print("✅ Sufficient star players found")
        else:
            print("❌ Insufficient star players")
            return False

        # Test 6: Resilience calculation feasibility
        print("\n6️⃣  CAN WE CALCULATE RESILIENCE?")
        # For resilience analysis, we need both regular season and playoff data
        # Let's check if we can get regular season data too

        regular_data = client.get_league_player_advanced_stats(season="2023-24",
                                                             season_type="Regular Season")

        if regular_data.get('resultSets') and regular_data['resultSets'][0].get('rowSet'):
            reg_df = pd.DataFrame(regular_data['resultSets'][0]['rowSet'],
                                columns=regular_data['resultSets'][0]['headers'])
            print(f"✅ Regular season data: {len(reg_df)} players")

            # Check if we can match playoff players to regular season
            playoff_names = set(df['PLAYER_NAME'])
            regular_names = set(reg_df['PLAYER_NAME'])
            overlap = len(playoff_names.intersection(regular_names))

            print(f"Players in both datasets: {overlap}")
            if overlap >= 150:  # Most playoff players should have regular season data
                print("✅ Can match playoff and regular season data for resilience calculation")
            else:
                print("❌ Insufficient overlap for resilience calculation")
                return False
        else:
            print("❌ Cannot fetch regular season data")
            return False

        # Final assessment
        print("\n🏆 FINAL ASSESSMENT")
        print("✅ External NBA APIs can provide reliable playoff data")
        print("✅ Data is complete, valid, and suitable for resilience analysis")
        print("✅ Recommendation: Use external APIs instead of fixing corrupted local data")

        return True

    except Exception as e:
        print(f"❌ Error testing external data: {e}")
        return False

if __name__ == "__main__":
    success = assess_external_data_viability()

    if success:
        print("\n🚀 NEXT STEPS:")
        print("1. ✅ External data is viable - pivot to API-based approach")
        print("2. Build data pipeline using NBA Stats API")
        print("3. Implement caching and error handling")
        print("4. Cancel complex remediation plan")
        print("5. Resume resilience analysis with clean data")
    else:
        print("\n🔧 NEXT STEPS:")
        print("1. ❌ External data insufficient")
        print("2. Proceed with targeted local data remediation")
        print("3. Focus remediation on specific analysis needs")
