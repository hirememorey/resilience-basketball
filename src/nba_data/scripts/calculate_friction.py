#!/usr/bin/env python3
"""
Calculate Friction Score for NBA Players

The Friction Score measures how efficiently a player converts ball touches into points,
accounting for the time they spend with the ball. Lower friction = more efficient scoring.

Formula: friction_score = avg_sec_per_touch / pts_per_touch
- Higher values indicate more "friction" (inefficiency)
- Lower values indicate smoother, more efficient scoring

This is part of the "Process Independence" metric in the new resilience framework.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import sqlite3
import pandas as pd
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/calculate_friction.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FrictionCalculator:
    """Calculates Friction Scores for NBA players based on tracking data."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)

    def calculate_friction_scores(
        self,
        season_year: str = "2023-24",
        season_type: str = "Regular Season",
        min_touches: int = 50  # Minimum touches to be included
    ) -> pd.DataFrame:
        """
        Calculate friction scores for all qualified players.

        Args:
            season_year: Season in format "2023-24"
            season_type: "Regular Season" or "Playoffs"
            min_touches: Minimum touches required for calculation

        Returns:
            DataFrame with friction scores and related metrics
        """
        logger.info(f"Calculating friction scores for {season_year} {season_type}")

        # Query tracking data
        query = """
        SELECT
            pts.player_id,
            pts.season,
            pts.season_type,
            pts.team_id,
            pts.minutes_played,
            pts.touches,
            pts.avg_sec_per_touch,
            pts.pts_per_touch,
            pts.time_of_poss,

            -- Player info for context
            p.player_name,
            t.team_abbreviation,

            -- Usage rate for context (from advanced stats)
            pa.usage_percentage

        FROM player_tracking_stats pts
        JOIN players p ON pts.player_id = p.player_id
        JOIN teams t ON pts.team_id = t.team_id
        LEFT JOIN player_advanced_stats pa ON (
            pts.player_id = pa.player_id
            AND pts.season = pa.season
            AND pts.season_type = pa.season_type
            AND pts.team_id = pa.team_id
        )
        WHERE pts.season = ?
        AND pts.season_type = ?
        AND pts.touches >= ?
        AND pts.avg_sec_per_touch > 0  -- Avoid division by zero
        AND pts.pts_per_touch > 0      -- Avoid infinite friction
        ORDER BY pts.touches DESC
        """

        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql(query, conn, params=[season_year, season_type, min_touches])

        logger.info(f"Query returned {len(df)} rows")

        if df.empty:
            logger.warning(f"No players found with minimum {min_touches} touches")
            logger.info(f"Query executed: season={season_year}, season_type={season_type}, min_touches={min_touches}")
            return pd.DataFrame()

        logger.info(f"Found {len(df)} players with sufficient tracking data")

        # Calculate friction score
        # friction_score = time_per_touch / points_per_touch
        # Higher = more friction (less efficient)
        df['friction_score'] = df['avg_sec_per_touch'] / df['pts_per_touch']

        # Calculate additional efficiency metrics
        df['touch_efficiency'] = df['pts_per_touch'] / df['avg_sec_per_touch']  # Inverse of friction
        df['possession_efficiency'] = df['pts_per_touch'] * (df['touches'] / df['time_of_poss'])

        # Calculate percentiles for ranking
        df['friction_percentile'] = df['friction_score'].rank(pct=True, ascending=False)  # Lower friction = higher percentile
        df['touch_efficiency_percentile'] = df['touch_efficiency'].rank(pct=True)

        # Sort by friction score (ascending = most efficient)
        df = df.sort_values('friction_score')

        logger.info(f"Friction scores calculated for {len(df)} players")
        logger.info(".2f")
        logger.info(".2f")

        return df

    def save_friction_scores(
        self,
        df: pd.DataFrame,
        output_path: Optional[str] = None
    ) -> None:
        """
        Save friction scores to CSV and optionally to database.

        Args:
            df: DataFrame with friction scores
            output_path: Path to save CSV (optional)
        """
        if df.empty:
            logger.warning("No data to save")
            return

        # Default output path
        if output_path is None:
            output_path = f"data/friction_scores_{df['season'].iloc[0].replace('-', '_')}_{df['season_type'].iloc[0].replace(' ', '_').lower()}.csv"

        # Save to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Saved friction scores to {output_path}")

        # Could also save to database table if needed
        # self._save_to_database(df)

    def get_top_efficient_players(
        self,
        df: pd.DataFrame,
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        Get the most efficient players (lowest friction).

        Args:
            df: DataFrame with friction scores
            top_n: Number of top players to return

        Returns:
            DataFrame with top efficient players
        """
        if df.empty:
            return pd.DataFrame()

        return df.head(top_n)[[
            'player_name', 'team_abbreviation', 'touches', 'friction_score',
            'touch_efficiency', 'avg_sec_per_touch', 'pts_per_touch',
            'usage_percentage', 'friction_percentile'
        ]]

    def analyze_friction_by_position(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Analyze friction scores by player position.

        Args:
            df: DataFrame with friction scores

        Returns:
            DataFrame with position analysis
        """
        # This would require joining with player position data
        # For now, return basic stats
        return df.groupby('team_abbreviation').agg({
            'friction_score': ['mean', 'std', 'count'],
            'touch_efficiency': 'mean'
        }).round(3)


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description='Calculate Friction Scores for NBA players')
    parser.add_argument('--season', default='2023-24', help='Season year (default: 2023-24)')
    parser.add_argument('--season-type', choices=['Regular Season', 'Playoffs'], default='Regular Season',
                        help='Season type (default: Regular Season)')
    parser.add_argument('--min-touches', type=int, default=50, help='Minimum touches required (default: 50)')
    parser.add_argument('--output', help='Output CSV path')
    parser.add_argument('--top-n', type=int, default=20, help='Show top N most efficient players')

    args = parser.parse_args()

    calculator = FrictionCalculator()

    # Calculate friction scores
    df = calculator.calculate_friction_scores(
        season_year=args.season,
        season_type=args.season_type,
        min_touches=args.min_touches
    )

    if df.empty:
        print("No data available for the specified parameters")
        return

    # Save results
    calculator.save_friction_scores(df, args.output)

    # Show top players
    top_players = calculator.get_top_efficient_players(df, args.top_n)

    print(f"\n=== Top {args.top_n} Most Efficient Players ({args.season} {args.season_type}) ===")
    print(f"Minimum touches: {args.min_touches}")
    print(top_players.to_string(index=False))

    # Show summary stats
    print("\n=== Friction Score Summary ===")
    print(".3f")
    print(".3f")
    print(f"Players analyzed: {len(df)}")


if __name__ == "__main__":
    main()
