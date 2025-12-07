#!/usr/bin/env python3
"""
Analyze historical playoff resilience for specific players using external API data.
From first principles: Does one season's fragility invalidate the metric?
"""

import sys
from pathlib import Path
from typing import Dict, List
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))

from src.nba_data.api.nba_stats_client import NBAStatsClient

class PlayerHistoryAnalyzer:
    """Analyze historical playoff performance for specific players."""

    def __init__(self):
        self.client = NBAStatsClient()

    def get_player_resilience_across_seasons(self, player_names: List[str], seasons: List[str]) -> pd.DataFrame:
        """Get resilience metrics for players across multiple seasons."""

        results = []

        for season in seasons:
            print(f"📊 Analyzing {season}...")

            # Get both datasets
            rs_data = self.client.get_league_player_advanced_stats(season=season)
            po_data = self.client.get_league_player_playoff_advanced_stats(season=season)

            if not (rs_data.get('resultSets') and po_data.get('resultSets')):
                print(f"❌ Missing data for {season}")
                continue

            rs_df = pd.DataFrame(rs_data['resultSets'][0]['rowSet'],
                               columns=rs_data['resultSets'][0]['headers'])
            po_df = pd.DataFrame(po_data['resultSets'][0]['rowSet'],
                               columns=po_data['resultSets'][0]['headers'])

            # Filter for meaningful minutes
            rs_df = rs_df[rs_df['MIN'] >= 10].copy()
            po_df = po_df[po_df['MIN'] >= 10].copy()

            for player_name in player_names:
                # Check if player exists in both datasets
                rs_player = rs_df[rs_df['PLAYER_NAME'] == player_name]
                po_player = po_df[po_df['PLAYER_NAME'] == player_name]

                if rs_player.empty or po_player.empty:
                    continue

                rs_stats = rs_player.iloc[0]
                po_stats = po_player.iloc[0]

                # Only include if meaningful playoff minutes (≥15 MPG)
                if po_stats['MIN'] < 15:
                    continue

                # Calculate resilience metrics
                ts_resilience = po_stats['TS_PCT'] / rs_stats['TS_PCT']

                results.append({
                    'player_name': player_name,
                    'season': season,
                    'rs_ts_pct': rs_stats['TS_PCT'],
                    'po_ts_pct': po_stats['TS_PCT'],
                    'rs_usage_pct': rs_stats['USG_PCT'],
                    'po_usage_pct': po_stats.get('USG_PCT', 0),
                    'ts_resilience_ratio': ts_resilience,
                    'rs_minutes': rs_stats['MIN'],
                    'po_minutes': po_stats['MIN'],
                    'po_games': po_stats['GP']
                })

        return pd.DataFrame(results)

def main():
    """Analyze Jamal Murray and Kawhi Leonard's historical playoff resilience."""

    print("🏀 HISTORICAL PLAYOFF RESILIENCE ANALYSIS")
    print("=" * 50)
    print("From first principles: Does one fragile season invalidate the metric?")
    print()

    analyzer = PlayerHistoryAnalyzer()

    # Focus on the players mentioned
    players = ['Jamal Murray', 'Kawhi Leonard']

    # Seasons where these players had notable playoff runs
    seasons = ['2023-24', '2022-23', '2021-22', '2020-21', '2019-20']

    df = analyzer.get_player_resilience_across_seasons(players, seasons)

    if df.empty:
        print("❌ No historical data found")
        return

    print(f"📊 Found {len(df)} player-season combinations")
    print()

    # Analyze each player
    for player in players:
        player_data = df[df['player_name'] == player].copy()
        if player_data.empty:
            continue

        print(f"🎯 {player.upper()} HISTORICAL ANALYSIS")
        print("-" * 40)

        # Calculate stats
        avg_resilience = player_data['ts_resilience_ratio'].mean()
        min_resilience = player_data['ts_resilience_ratio'].min()
        max_resilience = player_data['ts_resilience_ratio'].max()
        std_resilience = player_data['ts_resilience_ratio'].std()

        print(".3f")
        print(".3f")
        print(".3f")
        print(".3f")
        print()

        # Show year-by-year breakdown
        print("Year-by-Year Resilience:")
        for _, row in player_data.iterrows():
            resilience = row['ts_resilience_ratio']
            category = "Resilient" if resilience > 1.0 else "Neutral" if resilience > 0.95 else "Fragile"
            print(".3f")

        # Key insights
        print("\n🔍 KEY INSIGHTS:")

        # Check for 2023-24 fragility
        fragile_2024 = player_data[player_data['season'] == '2023-24']
        if not fragile_2024.empty:
            fragile_ratio = fragile_2024.iloc[0]['ts_resilience_ratio']
            print(".3f")

        # Check consistency
        if len(player_data) > 1:
            consistent = std_resilience < 0.15  # Low variance
            print(f"  • Consistency: {'HIGH' if consistent else 'LOW'} (Std Dev: {std_resilience:.3f})")

        # Historical excellence context
        if player == 'Jamal Murray':
            print("  • 2021 Playoff MVP with strong historical performance")
        elif player == 'Kawhi Leonard':
            print("  • 2x Finals MVP, consistently elite playoff performer")

        print()

    # Philosophical analysis
    print("🧠 FIRST PRINCIPLES ANALYSIS")
    print("=" * 30)
    print("Does one fragile season invalidate the TS% delta metric?")
    print()

    print("ARGUMENTS FOR:")
    print("• Single season could be statistical noise or injury/recovery effects")
    print("• External factors (matchups, injuries, team context) affect performance")
    print("• Murray/Leonard have proven track records of playoff excellence")
    print()

    print("ARGUMENTS AGAINST:")
    print("• Even elite players have vulnerable seasons (Kobe's 2006 playoffs)")
    print("• TS% delta might identify specific vulnerabilities under pressure")
    print("• One fragile season doesn't erase historical excellence, but highlights risk")
    print()

    print("BALANCED VIEW:")
    print("• TS% delta identifies relative performance, not absolute skill")
    print("• One season shows vulnerability, but multiple seasons show pattern")
    print("• Elite players can be fragile, but fragility doesn't make them non-elite")
    print("• The metric remains valid for identifying risk, not destiny")

if __name__ == "__main__":
    main()
