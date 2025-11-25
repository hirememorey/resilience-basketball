#!/usr/bin/env python3
"""
Calculate Friction Score & Resilience for NBA Players

The Friction Score measures how efficiently a player converts ball touches into points,
accounting for the time they spend with the ball.

New "Resilience" Logic:
1. Calculates Friction for BOTH Regular Season and Playoffs.
2. Measures the DELTA (Playoff Friction - Regular Season Friction).
3. Contextualizes by Usage Rate to separate Primary Creators from Finishers.
4. Filters by ESTIMATED TOTAL TOUCHES (Touches Per Game * Games Played) to ensure sample size.

Formula: friction_score = avg_sec_per_touch / pts_per_touch
- Lower is better (more efficient).
- Resilience = Ability to MAINTAIN or LOWER friction in Playoffs.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import sqlite3
import pandas as pd
import numpy as np

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
    """Calculates Friction Scores and Resilience Deltas."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        self.db_path = Path(db_path)

    def get_season_data(
        self,
        season: str,
        season_type: str,
        min_total_touches: int = 1000
    ) -> pd.DataFrame:
        """Fetch tracking data for a specific season/type."""
        
        # We join with player_season_stats to get games_played for total volume calculation
        query = """
        SELECT
            pts.player_id,
            pts.season,
            pts.season_type,
            pts.team_id,
            pts.minutes_played,
            pts.touches as touches_per_game,
            pts.avg_sec_per_touch,
            pts.pts_per_touch,
            pts.time_of_poss,
            
            pss.games_played,
            
            p.player_name,
            t.team_abbreviation,
            pa.usage_percentage
        FROM player_tracking_stats pts
        JOIN players p ON pts.player_id = p.player_id
        JOIN teams t ON pts.team_id = t.team_id
        JOIN player_season_stats pss ON (
            pts.player_id = pss.player_id
            AND pts.season = pss.season
            AND pts.season_type = pss.season_type
            AND pts.team_id = pss.team_id
        )
        LEFT JOIN player_advanced_stats pa ON (
            pts.player_id = pa.player_id
            AND pts.season = pa.season
            AND pts.season_type = pa.season_type
            AND pts.team_id = pa.team_id
        )
        WHERE pts.season = ?
        AND pts.season_type = ?
        AND pts.avg_sec_per_touch > 0
        AND pts.pts_per_touch > 0
        """

        with sqlite3.connect(self.db_path) as conn:
            try:
                df = pd.read_sql(query, conn, params=[season, season_type])
            except Exception as e:
                logger.error(f"Error querying data: {e}")
                return pd.DataFrame()
        
        if df.empty:
            return df

        # Calculate estimated total touches
        df['total_touches'] = df['touches_per_game'] * df['games_played']
        
        # Filter by volume
        df_filtered = df[df['total_touches'] >= min_total_touches].copy()
        
        logger.info(f"Fetched {len(df_filtered)} rows for {season} {season_type} (Min Touches: {min_total_touches})")
        return df_filtered

    def calculate_resilience(
        self,
        season: str = "2023-24",
        min_touches_reg: int = 1000,
        min_touches_playoff: int = 100
    ) -> pd.DataFrame:
        """
        Calculate Friction Resilience (Delta between Reg Season and Playoffs).
        """
        logger.info(f"Calculating Friction Resilience for {season}...")

        # 1. Get Regular Season Data
        df_reg = self.get_season_data(season, "Regular Season", min_touches_reg)
        if df_reg.empty:
            logger.warning("No Regular Season data found.")
            return pd.DataFrame()

        # 2. Get Playoff Data
        df_playoff = self.get_season_data(season, "Playoffs", min_touches_playoff)
        if df_playoff.empty:
            logger.warning("No Playoff data found.")
            # Return just regular season data if no playoffs found?
            # No, we need resilience (delta), so return empty or just reg season scores.
            return pd.DataFrame()

        # 3. Calculate Base Friction Score (Sec per Touch / Pts per Touch)
        # Lower = Better
        df_reg['friction_score'] = df_reg['avg_sec_per_touch'] / df_reg['pts_per_touch']
        df_playoff['friction_score'] = df_playoff['avg_sec_per_touch'] / df_playoff['pts_per_touch']

        # 4. Merge
        # We merge on player_id. We keep suffixes.
        df_merged = pd.merge(
            df_reg,
            df_playoff[['player_id', 'friction_score', 'touches_per_game', 'usage_percentage', 'pts_per_touch', 'avg_sec_per_touch', 'time_of_poss']],
            on='player_id',
            suffixes=('_reg', '_playoff'),
            how='inner'
        )

        # 5. Calculate Delta
        # Friction Delta = Playoff Friction - Regular Season Friction
        # Positive Delta = Got Worse (More Friction)
        # Negative Delta = Got Better (Less Friction)
        df_merged['friction_delta'] = df_merged['friction_score_playoff'] - df_merged['friction_score_reg']

        # 6. Define Usage Tiers (based on Regular Season) - Updated "Engine" vs "Finisher" Logic
        def get_tier(row):
            usage = row['usage_percentage_reg']
            time_poss = row['time_of_poss'] # Need to ensure this column is in the merged DF or fetch it
            
            if pd.isna(usage): return "Unknown"
            
            # High Usage Tiers
            if usage >= 0.30:
                return "Heliocentric Engine" if time_poss > 6.0 else "Elite Finisher"
            
            if usage >= 0.24:
                return "Primary Creator" if time_poss > 4.0 else "Secondary Scorer"
                
            if usage >= 0.18:
                return "Connector"
                
            return "Role Player"

        # Ensure 'time_of_poss' is available in merged df (it comes from pts.time_of_poss in query)
        # In get_season_data, we select pts.time_of_poss. 
        # In merged df, it will be time_of_poss_reg and time_of_poss_playoff.
        
        df_merged['usage_tier'] = df_merged.apply(
            lambda x: get_tier({'usage_percentage_reg': x['usage_percentage_reg'], 'time_of_poss': x.get('time_of_poss_reg', 0)}), 
            axis=1
        )

        # 7. Normalize to 0-100 Score (Percentile Rank)
        # Logic: Lower Delta is BETTER.
        # - Negative Delta (got better) -> High Score (closer to 100)
        # - Positive Delta (got worse) -> Low Score (closer to 0)
        
        # Rank 'friction_delta' ascending (Lowest/Best is rank 1)
        # pct=True gives 0.0 to 1.0
        # We want the lowest delta to be 1.0 (100), so we invert or just rank descending?
        # Let's use rank(ascending=True). Smallest delta (e.g. -5) gets rank 1 (0.0 percentile).
        # Wait, if we use ascending=False:
        # Largest delta (+5, bad) gets rank 1.
        # Smallest delta (-5, good) gets rank N.
        # So percentile of ascending=False would give high score to good players.
        
        df_merged['friction_resilience_score'] = df_merged['friction_delta'].rank(ascending=False, pct=True) * 100
        
        # 8. Sort and Rank
        df_merged = df_merged.sort_values('friction_resilience_score', ascending=False) # Highest score first

        logger.info(f"Calculated resilience for {len(df_merged)} players who played in both Reg Season & Playoffs.")
        return df_merged

    def get_resilience_dict(self, season: str = "2023-24") -> Dict[int, float]:
        """Get a dictionary of {player_id: friction_resilience_score} directly."""
        df = self.calculate_resilience(season)
        if df.empty:
            return {}
        return dict(zip(df['player_id'], df['friction_resilience_score']))

    def save_results(self, df: pd.DataFrame, season: str):
        if df.empty: return
        filename = f"data/friction_resilience_{season}.csv"
        df.to_csv(filename, index=False)
        logger.info(f"Saved results to {filename}")

def main():
    calculator = FrictionCalculator()
    
    # Run for 2023-24
    df = calculator.calculate_resilience(season="2023-24")
    
    if not df.empty:
        calculator.save_results(df, "2023-24")
        
        # Display Top Resilient High-Usage Players
        print("\n=== 🏆 Top Resilience (High Usage: >25%) ===")
        high_usage = df[df['usage_percentage_reg'] > 0.25].head(10)
        cols = ['player_name', 'team_abbreviation', 'usage_tier', 'friction_score_reg', 'friction_score_playoff', 'friction_delta', 'friction_resilience_score']
        print(high_usage[cols].to_string(index=False, float_format="%.3f"))

        print("\n=== 📉 Biggest Drop-offs (High Usage) ===")
        high_usage_worst = df[df['usage_percentage_reg'] > 0.25].tail(10)
        print(high_usage_worst[cols].to_string(index=False, float_format="%.3f"))

        print("\n=== 🔍 Metric Context ===")
        print("Friction Score = Seconds per Touch / Points per Touch")
        print("Delta = Playoff - Regular Season")
        print("Resilience Score (0-100) = Percentile Rank of Delta (Higher is Better)")
        print("Negative Delta = RESILIENT (Maintained or Improved efficiency)")
        print("Positive Delta = FRAGILE (Efficiency worsened)")

if __name__ == "__main__":
    main()
