"""
Calculate Crucible Baseline Statistics.

This script implements the "Crucible Baseline" logic:
1. Identify Top 10 Defensive Teams (by Def Rtg) for each season.
2. Aggregate player stats ONLY from games played against these "Crucible" teams.
3. Calculate efficiency and volume metrics for this subset.
4. Store in `player_crucible_stats` table.

This provides a more accurate baseline for Playoff resilience than raw Regular Season averages.
"""

import sys
import sqlite3
import pandas as pd
import logging
from pathlib import Path
from typing import List, Tuple, Dict

# Add project root to path
project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.nba_data.db.schema import init_database

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/calculate_crucible_baseline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CrucibleCalculator:
    def __init__(self, db_path: str = "data/nba_stats.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def get_crucible_teams(self, season: str, limit: int = 10) -> List[int]:
        """
        Identify the Top N Defensive Teams for a given season.
        Returns a list of team_ids.
        """
        query = """
            SELECT team_id, defensive_rating
            FROM team_season_stats
            WHERE season = ? 
            AND season_type = 'Regular Season'
            ORDER BY defensive_rating ASC
            LIMIT ?
        """
        self.cursor.execute(query, (season, limit))
        results = self.cursor.fetchall()
        
        crucible_teams = [row['team_id'] for row in results]
        
        # Log the teams for verification
        logger.info(f"🛡️  Crucible Teams for {season} (Top {limit} Defenses): {crucible_teams}")
        return crucible_teams

    def calculate_stats_for_season(self, season: str):
        """
        Calculate and store Crucible stats for all players in a season.
        """
        logger.info(f"Analyzing Crucible Performance for {season}...")
        
        # 1. Get Crucible Teams
        crucible_ids = self.get_crucible_teams(season)
        if not crucible_ids:
            logger.warning(f"⚠️  No crucible teams found for {season}. Skipping.")
            return

        placeholders = ','.join(['?'] * len(crucible_ids))
        
        # 2. Aggregation Query
        # We join player_game_logs with games to find the opponent.
        # Logic: If player.team_id == home_team_id, opponent is away_team_id.
        query = f"""
            SELECT 
                l.player_id,
                l.season,
                l.team_id,
                COUNT(DISTINCT l.game_id) as games_played,
                SUM(l.minutes_played) as minutes_played,
                SUM(l.points) as points,
                SUM(l.field_goals_made) as fgm,
                SUM(l.field_goals_attempted) as fga,
                SUM(l.three_pointers_made) as fg3m,
                SUM(l.three_pointers_attempted) as fg3a,
                SUM(l.free_throws_made) as ftm,
                SUM(l.free_throws_attempted) as fta,
                SUM(l.assists) as assists,
                SUM(l.turnovers) as turnovers
            FROM player_game_logs l
            JOIN games g ON l.game_id = g.game_id
            WHERE l.season = ?
              AND l.season_type = 'Regular Season'
              AND (
                  (l.team_id = g.home_team_id AND g.away_team_id IN ({placeholders}))
                  OR 
                  (l.team_id = g.away_team_id AND g.home_team_id IN ({placeholders}))
              )
            GROUP BY l.player_id, l.season, l.team_id
        """
        
        # Params: season, then crucible_ids twice (once for each OR condition)
        params = [season] + crucible_ids + crucible_ids
        
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        
        logger.info(f"  Found {len(rows)} players with games against Crucible teams.")
        
        # 3. Calculate Derived Metrics & Insert
        records_to_insert = []
        
        for row in rows:
            pts = row['points'] or 0
            fga = row['fga'] or 0
            fgm = row['fgm'] or 0
            fta = row['fta'] or 0
            fg3m = row['fg3m'] or 0
            tov = row['turnovers'] or 0
            ast = row['assists'] or 0
            mins = row['minutes_played'] or 0
            
            # TS% = PTS / (2 * (FGA + 0.44 * FTA))
            ts_denom = 2 * (fga + 0.44 * fta)
            ts_pct = (pts / ts_denom) if ts_denom > 0 else 0.0
            
            # eFG% = (FGM + 0.5 * 3PM) / FGA
            efg_pct = ((fgm + 0.5 * fg3m) / fga) if fga > 0 else 0.0
            
            # Ast/TO
            ast_to_ratio = (ast / tov) if tov > 0 else (ast if ast > 0 else 0.0)
            
            # Usage Estimate (Simple usage: (FGA + 0.44*FTA + TOV) / MIN) - optional, simplified here
            # For now we just store the basics.
            usage_est = 0.0 # Placeholder if we want complex usage calc
            
            records_to_insert.append((
                row['player_id'],
                row['season'],
                row['team_id'],
                row['games_played'],
                mins,
                pts,
                fgm,
                fga,
                fg3m,
                row['fg3a'],
                row['ftm'],
                fta,
                ts_pct,
                efg_pct,
                usage_est,
                ast,
                tov,
                ast_to_ratio
            ))
            
        # 4. Batch Insert
        insert_query = """
            INSERT OR REPLACE INTO player_crucible_stats (
                player_id, season, team_id, games_played, minutes_played,
                points, field_goals_made, field_goals_attempted,
                three_pointers_made, three_pointers_attempted,
                free_throws_made, free_throws_attempted,
                true_shooting_percentage, effective_field_goal_percentage, usage_percentage,
                assists, turnovers, assist_to_turnover_ratio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.cursor.executemany(insert_query, records_to_insert)
        self.conn.commit()
        logger.info(f"✅ Inserted {len(records_to_insert)} Crucible records for {season}.")

    def calculate_resilience_score(self, season: str) -> pd.DataFrame:
        """
        Calculate Crucible Resilience Score (Delta vs Regular Season).
        
        Metrics:
        1. TS% Delta (Efficiency maintenance)
        2. PPG/36 Delta (Volume maintenance)
        """
        logger.info(f"Calculating Crucible Resilience Score for {season}...")
        
        # 1. Fetch Crucible Stats
        query_crucible = """
            SELECT 
                player_id,
                games_played as gp_crucible,
                minutes_played as min_crucible,
                points as pts_crucible,
                true_shooting_percentage as ts_crucible
            FROM player_crucible_stats
            WHERE season = ?
        """
        
        # 2. Fetch Regular Season Stats
        query_regular = """
            SELECT 
                player_id,
                games_played as gp_reg,
                minutes_played as min_reg,
                points as pts_reg,
                (points / (2.0 * (field_goals_attempted + 0.44 * free_throws_attempted))) as ts_reg
            FROM player_season_stats
            WHERE season = ? AND season_type = 'Regular Season'
        """
        
        import pandas as pd
        
        try:
            df_crucible = pd.read_sql(query_crucible, self.conn, params=[season])
            df_reg = pd.read_sql(query_regular, self.conn, params=[season])
        except Exception as e:
            logger.error(f"Error fetching data for resilience calc: {e}")
            return pd.DataFrame()
            
        if df_crucible.empty or df_reg.empty:
            logger.warning("Missing data for resilience calculation.")
            return pd.DataFrame()

        # 3. Merge
        df = pd.merge(df_crucible, df_reg, on='player_id', how='inner')
        
        # 4. Filter for significant sample size
        # e.g., > 100 mins in Crucible games to be meaningful
        df = df[df['min_crucible'] > 100].copy()
        
        # 5. Calculate Per 36 Metrics
        df['pts36_crucible'] = (df['pts_crucible'] / df['min_crucible']) * 36
        df['pts36_reg'] = (df['pts_reg'] / df['min_reg']) * 36
        
        # 6. Calculate Deltas
        df['ts_delta'] = df['ts_crucible'] - df['ts_reg']
        df['pts36_delta'] = df['pts36_crucible'] - df['pts36_reg']
        
        # 7. Calculate Resilience Score (Percentile of TS Delta)
        # Primary driver: Efficiency Maintenance.
        # Higher Delta (Positive) is better.
        df['crucible_resilience_score'] = df['ts_delta'].rank(pct=True) * 100
        
        # 8. Get Player Names for display
        names_query = "SELECT player_id, player_name FROM players"
        df_names = pd.read_sql(names_query, self.conn)
        df = pd.merge(df, df_names, on='player_id', how='left')
        
        # Sort by score
        df = df.sort_values('crucible_resilience_score', ascending=False)
        
        # Save output
        output_file = f"data/crucible_resilience_{season}.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"✅ Saved Crucible Resilience scores to {output_file}")
        
        return df

    def get_resilience_dict(self, season: str = "2023-24") -> Dict[int, float]:
        """Get a dictionary of {player_id: crucible_resilience_score} directly."""
        df = self.calculate_resilience_score(season)
        if df.empty:
            return {}
        return dict(zip(df['player_id'], df['crucible_resilience_score']))

    def run(self):
        seasons = [
            "2015-16", "2016-17", "2017-18", "2018-19", "2019-20",
            "2020-21", "2021-22", "2022-23", "2023-24"
        ]
        
        for season in seasons:
            try:
                self.calculate_stats_for_season(season)
                # Run resilience score calc for the season
                self.calculate_resilience_score(season)
            except Exception as e:
                logger.error(f"❌ Error processing {season}: {e}", exc_info=True)
                
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    # Ensure schema is up to date
    init_database()
    
    calculator = CrucibleCalculator()
    calculator.run()
    calculator.close()


