#!/usr/bin/env python3
"""
NBA Playoff Resilience Calculator - External API Version

Uses clean, validated data from NBA Stats API instead of corrupted local database.
From first principles: Simple TS% ratio approach with authoritative data source.

Resilience Score = Playoff TS% ÷ Regular Season TS%
- > 1.0: Improved in playoffs (resilient)
- = 1.0: Maintained efficiency (neutral)
- < 1.0: Declined in playoffs (fragile)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from src.nba_data.api.nba_stats_client import NBAStatsClient

class ExternalResilienceCalculator:
    """Calculates playoff resilience using external NBA API data."""

    def __init__(self):
        self.client = NBAStatsClient()

    def get_season_data(self, season: str, season_type: str = "Regular Season") -> pd.DataFrame:
        """Fetch player advanced stats for a season from NBA API."""
        print(f"📡 Fetching {season_type.lower()} data for {season}...")

        try:
            if season_type == "Regular Season":
                response = self.client.get_league_player_advanced_stats(season=season)
            else:  # Playoffs
                response = self.client.get_league_player_playoff_advanced_stats(season=season)

            if not response.get('resultSets') or not response['resultSets'][0].get('rowSet'):
                print(f"❌ No data received for {season} {season_type}")
                return pd.DataFrame()

            headers = response['resultSets'][0]['headers']
            rows = response['resultSets'][0]['rowSet']
            df = pd.DataFrame(rows, columns=headers)

            # Filter for meaningful minutes (similar to original approach)
            # MIN is minutes per game, so filter for players with decent playing time
            df = df[df['MIN'] >= 10].copy()  # At least 10 minutes per game on average

            print(f"✅ Retrieved {len(df)} players with sufficient minutes")
            return df

        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return pd.DataFrame()

    def calculate_player_resilience(self, player_name: str, season: str) -> Optional[Dict]:
        """Calculate resilience for a specific player in a season."""

        # Get regular season data
        rs_data = self.get_season_data(season, "Regular Season")
        if rs_data.empty:
            return None

        # Get playoff data
        po_data = self.get_season_data(season, "Playoffs")
        if po_data.empty:
            return None

        # Find player in both datasets
        rs_player = rs_data[rs_data['PLAYER_NAME'] == player_name]
        po_player = po_data[po_data['PLAYER_NAME'] == player_name]

        if rs_player.empty or po_player.empty:
            return None

        rs_stats = rs_player.iloc[0]
        po_stats = po_player.iloc[0]

        # Calculate resilience metrics
        ts_resilience = po_stats['TS_PCT'] / rs_stats['TS_PCT']
        ortg_resilience = po_stats.get('OFF_RATING', po_stats.get('ORTG', 100)) / rs_stats.get('OFF_RATING', rs_stats.get('ORTG', 100))
        efg_resilience = po_stats['EFG_PCT'] / rs_stats['EFG_PCT']

        # Weighted resilience (higher usage = more important)
        usage_weight = rs_stats['USG_PCT']

        return {
            'player_name': player_name,
            'season': season,

            # Raw metrics
            'rs_ts_pct': rs_stats['TS_PCT'],
            'po_ts_pct': po_stats['TS_PCT'],
            'rs_usage_pct': rs_stats['USG_PCT'],
            'po_usage_pct': po_stats.get('USG_PCT', 0),

            # Resilience ratios
            'ts_resilience_ratio': ts_resilience,
            'ortg_resilience_ratio': ortg_resilience,
            'efg_resilience_ratio': efg_resilience,

            # Weighted scores
            'weighted_ts_resilience': ts_resilience * usage_weight,

            # Sample sizes
            'rs_minutes': rs_stats['MIN'],
            'po_minutes': po_stats['MIN']
        }

    def calculate_season_resilience(self, season: str = "2023-24", min_usage: float = 0.20) -> pd.DataFrame:
        """Calculate resilience scores for all qualified players in a season."""

        print(f"\n🏀 Calculating resilience for {season}")
        print("=" * 50)

        # Get both datasets
        rs_data = self.get_season_data(season, "Regular Season")
        po_data = self.get_season_data(season, "Playoffs")

        if rs_data.empty or po_data.empty:
            print("❌ Missing required data")
            return pd.DataFrame()

        # Find players who appear in both regular season and playoffs
        rs_players = set(rs_data['PLAYER_NAME'])
        po_players = set(po_data['PLAYER_NAME'])
        qualified_players = rs_players.intersection(po_players)

        # Filter by usage and playoff minutes
        qualified_data = []
        for player_name in qualified_players:
            rs_player = rs_data[rs_data['PLAYER_NAME'] == player_name].iloc[0]
            po_player = po_data[po_data['PLAYER_NAME'] == player_name].iloc[0]

            # Apply filters: high usage in regular season, meaningful playoff time
            # MIN is minutes per game, so 15+ minutes per playoff game is meaningful
            if (rs_player['USG_PCT'] >= min_usage and
                po_player['MIN'] >= 15):  # At least 15 minutes per playoff game

                resilience = self.calculate_player_resilience(player_name, season)
                if resilience:
                    qualified_data.append(resilience)

        if not qualified_data:
            print("❌ No qualified players found")
            return pd.DataFrame()

        df = pd.DataFrame(qualified_data)

        # Add resilience categories
        df['resilience_category'] = pd.cut(
            df['ts_resilience_ratio'],
            bins=[0, 0.85, 0.95, 1.05, 1.15, float('inf')],
            labels=['Severely Fragile', 'Fragile', 'Neutral', 'Resilient', 'Highly Resilient']
        )

        # Sort by weighted resilience (most important players first)
        df = df.sort_values('weighted_ts_resilience', ascending=False)

        print(f"✅ Analyzed {len(df)} qualified players")
        return df

def main():
    """Main function to demonstrate external API resilience calculation."""

    print("🏀 NBA PLAYOFF RESILIENCE CALCULATOR - EXTERNAL API VERSION")
    print("=" * 70)
    print("Using clean, validated data from NBA Stats API")
    print("No corrupted local database required!")
    print()

    calculator = ExternalResilienceCalculator()

    # Calculate resilience for recent season
    season = "2023-24"
    df = calculator.calculate_season_resilience(season, min_usage=0.20)

    if df.empty:
        print("❌ Could not calculate resilience - check API connectivity")
        return

    print(f"\n📊 {season} RESILIENCE ANALYSIS")
    print(f"Found {len(df)} qualified players\n")

    # Show top resilient players
    print("✅ MOST RESILIENT PLAYERS:")
    top_resilient = df.head(10)
    for _, row in top_resilient.iterrows():
        print(".3f")

    print("\n❌ MOST FRAGILE PLAYERS:")
    bottom_fragile = df[df['ts_resilience_ratio'] < 0.9].tail(10)
    for _, row in bottom_fragile.iterrows():
        print(".3f")

    # Identify major underperformers
    print(f"\n🚨 MAJOR UNDERPERFORMERS ({season}):")
    underperformers = df[
        (df['ts_resilience_ratio'] < 0.90) &  # >10% TS% drop
        (df['rs_usage_pct'] >= 0.25)
    ].copy()

    if not underperformers.empty:
        underperformers['severity_score'] = (
            (1 - underperformers['ts_resilience_ratio']) *
            underperformers['rs_usage_pct'] * 100
        )
        underperformers = underperformers.sort_values('severity_score', ascending=False)

        for _, row in underperformers.head(10).iterrows():
            print(".1f")
    else:
        print("No major underperformers found")

    # Save results
    output_file = f"data/resilience_external_{season.replace('-', '_')}.csv"
    df.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to {output_file}")

    # Summary stats
    print(f"\n📈 SUMMARY STATISTICS:")
    print(".3f")
    print(".3f")
    print(".3f")

    category_counts = df['resilience_category'].value_counts()
    print(f"\nResilience Categories:")
    for category, count in category_counts.items():
        print(f"  {category}: {count} players ({count/len(df)*100:.1f}%)")

if __name__ == "__main__":
    main()
