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

    def run(self):
        seasons = [
            "2015-16", "2016-17", "2017-18", "2018-19", "2019-20",
            "2020-21", "2021-22", "2022-23", "2023-24"
        ]
        
        for season in seasons:
            try:
                self.calculate_stats_for_season(season)
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

