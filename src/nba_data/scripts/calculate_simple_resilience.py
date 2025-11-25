#!/usr/bin/env python3
"""
Simple Playoff Resilience Calculator

From first principles: Playoff resilience is about maintaining shooting efficiency
when the games matter most. This calculator uses the simplest, most direct approach:

Resilience Score = Playoff TS% / Regular Season TS%

- > 1.0: Improved in playoffs (resilient)
- = 1.0: Maintained efficiency (neutral)
- < 1.0: Declined in playoffs (fragile)

Weighted by regular season usage to focus on players who actually matter.
"""

import sqlite3
import pandas as pd
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

DB_PATH = "data/nba_stats.db"

def get_db_connection():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)

def calculate_player_resilience(player_id: int, season: str) -> Optional[Dict]:
    """
    Calculate simple resilience score for a player in a given season.

    Returns:
        dict with resilience metrics, or None if insufficient data
    """
    conn = get_db_connection()

    # Get regular season advanced stats
    rs_query = """
        SELECT
            p.player_name,
            rs.true_shooting_percentage as rs_ts_pct,
            rs.usage_percentage as rs_usage_pct,
            rs.games_played as rs_games,
            rs.offensive_rating as rs_ortg,
            rs.effective_field_goal_percentage as rs_efg_pct
        FROM player_advanced_stats rs
        JOIN players p ON rs.player_id = p.player_id
        WHERE rs.player_id = ? AND rs.season = ? AND rs.season_type = 'Regular Season'
        AND rs.games_played >= 20  -- Minimum games for reliability
    """

    # Get playoff advanced stats
    po_query = """
        SELECT
            true_shooting_percentage as po_ts_pct,
            usage_percentage as po_usage_pct,
            games_played as po_games,
            offensive_rating as po_ortg,
            effective_field_goal_percentage as po_efg_pct
        FROM player_playoff_advanced_stats
        WHERE player_id = ? AND season = ?
        AND games_played >= 4  -- At least one short playoff series
    """

    try:
        # Get regular season data
        rs_df = pd.read_sql_query(rs_query, conn, params=(player_id, season))

        if rs_df.empty:
            return None  # No regular season data

        rs_data = rs_df.iloc[0]

        # Get playoff data
        po_df = pd.read_sql_query(po_query, conn, params=(player_id, season))

        if po_df.empty:
            return None  # No playoff data

        po_data = po_df.iloc[0]

        # Calculate resilience metrics
        ts_resilience = po_data['po_ts_pct'] / rs_data['rs_ts_pct']
        ortg_resilience = po_data['po_ortg'] / rs_data['rs_ortg']
        efg_resilience = po_data['po_efg_pct'] / rs_data['rs_efg_pct']

        # Weighted resilience (higher usage = more important)
        usage_weight = rs_data['rs_usage_pct']
        weighted_ts_resilience = ts_resilience * usage_weight

        return {
            'player_id': player_id,
            'player_name': rs_data['player_name'],
            'season': season,

            # Raw metrics
            'rs_ts_pct': rs_data['rs_ts_pct'],
            'po_ts_pct': po_data['po_ts_pct'],
            'rs_usage_pct': rs_data['rs_usage_pct'],
            'po_usage_pct': po_data['po_usage_pct'],

            # Resilience ratios
            'ts_resilience_ratio': ts_resilience,
            'ortg_resilience_ratio': ortg_resilience,
            'efg_resilience_ratio': efg_resilience,

            # Weighted scores
            'weighted_ts_resilience': weighted_ts_resilience,

            # Sample sizes
            'rs_games': rs_data['rs_games'],
            'po_games': po_data['po_games']
        }

    except Exception as e:
        print(f"Error calculating resilience for player {player_id}: {e}")
        return None
    finally:
        conn.close()

def calculate_season_resilience(season: str = "2023-24", min_usage: float = 0.20) -> pd.DataFrame:
    """
    Calculate resilience scores for all qualified players in a season.

    Args:
        season: Season to analyze (e.g., "2023-24")
        min_usage: Minimum regular season usage % to include
    """
    conn = get_db_connection()

    # Get all players with sufficient regular season and playoff data
    query = """
        SELECT DISTINCT
            rs.player_id,
            p.player_name
        FROM player_advanced_stats rs
        JOIN player_playoff_advanced_stats po ON rs.player_id = po.player_id AND rs.season = po.season
        JOIN players p ON rs.player_id = p.player_id
        WHERE rs.season = ?
          AND rs.season_type = 'Regular Season'
          AND rs.games_played >= 20
          AND rs.usage_percentage >= ?
          AND po.games_played >= 4
        ORDER BY rs.usage_percentage DESC
    """

    players_df = pd.read_sql_query(query, conn, params=(season, min_usage))
    conn.close()

    print(f"Calculating resilience for {len(players_df)} players in {season} (min usage: {min_usage:.1%})")

    results = []
    for _, row in players_df.iterrows():
        resilience = calculate_player_resilience(row['player_id'], season)
        if resilience:
            results.append(resilience)

    df = pd.DataFrame(results)

    # Add resilience categories
    df['resilience_category'] = pd.cut(
        df['ts_resilience_ratio'],
        bins=[0, 0.85, 0.95, 1.05, 1.15, float('inf')],
        labels=['Severely Fragile', 'Fragile', 'Neutral', 'Resilient', 'Highly Resilient']
    )

    # Sort by weighted resilience (most important players first)
    df = df.sort_values('weighted_ts_resilience', ascending=False)

    return df

def identify_underperformers(season: str = "2023-24", min_usage: float = 0.25) -> pd.DataFrame:
    """
    Identify players who significantly underperformed in playoffs.

    Focus on high-usage players with meaningful TS% drops.
    """
    df = calculate_season_resilience(season, min_usage)

    # Filter for significant underperformance
    underperformers = df[
        (df['ts_resilience_ratio'] < 0.90) &  # >10% TS% drop
        (df['rs_usage_pct'] >= min_usage)
    ].copy()

    # Calculate severity score
    underperformers['severity_score'] = (
        (1 - underperformers['ts_resilience_ratio']) *
        underperformers['rs_usage_pct'] * 100
    )

    # Sort by severity
    underperformers = underperformers.sort_values('severity_score', ascending=False)

    return underperformers

def main():
    """Main function to demonstrate simple resilience calculation."""

    print("🏀 Simple Playoff Resilience Calculator")
    print("=" * 50)

    # Calculate resilience for recent season
    season = "2023-24"
    df = calculate_season_resilience(season, min_usage=0.20)

    print(f"\n📊 {season} Resilience Analysis")
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
    underperformers = identify_underperformers(season, min_usage=0.25)

    for _, row in underperformers.head(10).iterrows():
        print(".1f")

    # Save results
    df.to_csv(f"data/simple_resilience_{season.replace('-', '_')}.csv", index=False)
    print(f"\n💾 Results saved to data/simple_resilience_{season.replace('-', '_')}.csv")

if __name__ == "__main__":
    main()
