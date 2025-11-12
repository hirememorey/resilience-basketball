"""
Script to calculate and populate resilience scores for all players.

This script computes statistical resilience metrics based on player season data
and stores them in the database for analysis.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
import sqlite3
import pandas as pd
import numpy as np
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ResilienceCalculator:
    """Calculates and populates resilience scores for players."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)

    def calculate_resilience_scores(self) -> Dict[str, Any]:
        """Calculate and store resilience scores for all players."""
        results = {
            "players_processed": 0,
            "scores_calculated": 0,
            "errors": []
        }

        logger.info("Starting resilience score calculation...")

        # Get player season data
        query = '''
        SELECT
            pss.player_id,
            pss.season,
            pss.team_id,
            pss.points, pss.assists, pss.total_rebounds, pss.steals, pss.blocks,
            pss.field_goals_attempted, pss.three_pointers_attempted, pss.free_throws_attempted,
            pas.usage_percentage, pas.effective_field_goal_percentage,
            pas.true_shooting_percentage, pas.net_rating
        FROM player_season_stats pss
        LEFT JOIN player_advanced_stats pas ON pss.player_id = pas.player_id
            AND pss.season = pas.season
            AND pss.team_id = pas.team_id
        WHERE pss.games_played >= 30
        '''

        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            logger.warning("No player data found for resilience calculation")
            return results

        logger.info(f"Loaded {len(df)} player-season records for analysis")

        # Clean and prepare data
        production_cols = ['points', 'assists', 'total_rebounds', 'steals', 'blocks']
        shot_cols = ['field_goals_attempted', 'three_pointers_attempted', 'free_throws_attempted']

        # Convert to numeric and fill NaN
        for col in production_cols + shot_cols + ['effective_field_goal_percentage', 'true_shooting_percentage', 'usage_percentage', 'net_rating']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Calculate production diversification
        logger.info("Calculating production diversification...")
        for col in production_cols:
            max_val = df[col].max()
            if max_val > 0:
                df[f'{col}_normalized'] = df[col] / max_val
            else:
                df[f'{col}_normalized'] = 0.0

        df['production_concentration'] = df[[f'{col}_normalized' for col in production_cols]].max(axis=1)
        df['production_diversification'] = 1 - df['production_concentration']

        # Calculate shot diversification
        logger.info("Calculating shot diversification...")
        total_shots = df[shot_cols].sum(axis=1)
        for col in shot_cols:
            df[f'{col}_pct'] = df[col] / total_shots.where(total_shots > 0, 1)

        df['shot_concentration'] = df[[f'{col}_pct' for col in shot_cols]].max(axis=1)
        df['shot_diversification'] = 1 - df['shot_concentration']

        # Calculate efficiency stability (variance across metrics)
        logger.info("Calculating efficiency stability...")
        efficiency_cols = ['effective_field_goal_percentage', 'true_shooting_percentage']
        df['efficiency_stability'] = df[efficiency_cols].std(axis=1, skipna=True).fillna(0)

        # Calculate composite resilience score
        logger.info("Calculating composite resilience scores...")
        # Normalize efficiency stability (lower is better, so invert)
        max_stability = df['efficiency_stability'].max()
        if max_stability > 0:
            df['efficiency_stability_normalized'] = 1 - (df['efficiency_stability'] / max_stability)
        else:
            df['efficiency_stability_normalized'] = 1.0

        # Combine diversification metrics with efficiency
        df['resilience_score'] = (
            df['production_diversification'] * 0.4 +
            df['shot_diversification'] * 0.4 +
            df['efficiency_stability_normalized'] * 0.2
        )

        # Calculate percentiles for ranking
        df['resilience_percentile'] = df['resilience_score'].rank(pct=True)

        # Store results in database
        logger.info("Storing resilience scores in database...")
        conn = sqlite3.connect(self.db_path)

        for _, row in tqdm(df.iterrows(), total=len(df), desc="Storing resilience scores"):
            try:
                conn.execute('''
                    UPDATE player_season_stats
                    SET
                        production_diversification = ?,
                        production_concentration = ?,
                        shot_diversification = ?,
                        shot_concentration = ?,
                        efficiency_stability = ?,
                        resilience_score = ?,
                        resilience_percentile = ?
                    WHERE player_id = ? AND season = ? AND team_id = ?
                ''', (
                    row['production_diversification'],
                    row['production_concentration'],
                    row['shot_diversification'],
                    row['shot_concentration'],
                    row['efficiency_stability'],
                    row['resilience_score'],
                    row['resilience_percentile'],
                    row['player_id'],
                    row['season'],
                    row['team_id']
                ))

                results["scores_calculated"] += 1

            except Exception as e:
                error_msg = f"Failed to update player {row['player_id']}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

            results["players_processed"] += 1

        conn.commit()
        conn.close()

        logger.info(f"Resilience calculation complete: {results['scores_calculated']}/{results['players_processed']} players updated")
        return results


def main():
    """Main execution function."""
    calculator = ResilienceCalculator()
    results = calculator.calculate_resilience_scores()

    print("\n📊 Resilience Score Calculation Results:")
    print(f"✅ Players processed: {results['players_processed']}")
    print(f"✅ Scores calculated: {results['scores_calculated']}")
    print(f"❌ Errors: {len(results['errors'])}")

    if results['errors']:
        print("\nFirst few errors:")
        for error in results['errors'][:3]:
            print(f"  - {error}")

    # Show top resilient players
    if results['scores_calculated'] > 0:
        import sqlite3
        conn = sqlite3.connect("data/nba_stats.db")
        cursor = conn.cursor()

        cursor.execute('''
            SELECT p.player_name, pss.resilience_score, pss.resilience_percentile
            FROM player_season_stats pss
            JOIN players p ON pss.player_id = p.player_id
            WHERE pss.resilience_score > 0
            ORDER BY pss.resilience_score DESC
            LIMIT 5
        ''')

        top_players = cursor.fetchall()
        conn.close()

        if top_players:
            print("\n🏆 Top 5 Most Resilient Players:")
            for i, (name, score, percentile) in enumerate(top_players, 1):
                print(f"  {i}. {name}: {score:.3f} (Top {percentile:.1%})")


if __name__ == "__main__":
    main()
