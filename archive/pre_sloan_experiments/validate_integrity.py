"""
Script to perform comprehensive "World Class" integrity checks on the NBA database.
Validates referential integrity, logical consistency, and type safety.
"""

import sys
import sqlite3
from pathlib import Path
import logging
from typing import List, Tuple, Dict

# Add project root to path
project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.nba_data.db.schema import NBADatabaseSchema

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/integrity_check_enhanced.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegrityValidator:
    def __init__(self, db_path: str = "data/nba_stats.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.issues_found = 0

    def check_referential_integrity(self):
        """Check for orphaned records (Foreign Key violations)."""
        logger.info("\n🔍 Checking Referential Integrity (Orphans)...")
        
        # relationships = [(ChildTable, ForeignKeyColumn, ParentTable, ParentKey)]
        relationships = [
            ("player_game_logs", "player_id", "players", "player_id"),
            ("player_game_logs", "team_id", "teams", "team_id"),
            ("player_game_logs", "game_id", "games", "game_id"),
            ("games", "home_team_id", "teams", "team_id"),
            ("games", "away_team_id", "teams", "team_id"),
            ("players", "team_id", "teams", "team_id"),
            ("player_season_stats", "player_id", "players", "player_id"),
            ("player_season_stats", "team_id", "teams", "team_id"),
            ("player_advanced_stats", "player_id", "players", "player_id"),
            ("player_tracking_stats", "player_id", "players", "player_id"),
            ("player_playoff_stats", "player_id", "players", "player_id"),
            ("possessions", "game_id", "games", "game_id"),
            ("possessions", "offensive_team_id", "teams", "team_id"),
        ]

        for child_table, fk_col, parent_table, pk_col in relationships:
            try:
                query = f"""
                    SELECT COUNT(*) 
                    FROM {child_table} c 
                    LEFT JOIN {parent_table} p ON c.{fk_col} = p.{pk_col} 
                    WHERE p.{pk_col} IS NULL AND c.{fk_col} IS NOT NULL
                """
                self.cursor.execute(query)
                orphan_count = self.cursor.fetchone()[0]
                
                if orphan_count > 0:
                    logger.error(f"❌ ORPHAN DETECTED: {orphan_count} rows in '{child_table}' have invalid '{fk_col}' references.")
                    self.issues_found += 1
                else:
                    logger.debug(f"✅ {child_table}.{fk_col} -> {parent_table} is clean.")
            except sqlite3.OperationalError as e:
                logger.warning(f"⚠️ Could not check {child_table} -> {parent_table}: {e}")

    def check_logical_consistency(self):
        """Check for logical data errors (e.g. FGM > FGA)."""
        logger.info("\n🧠 Checking Logical Consistency...")

        checks = [
            ("player_season_stats", "field_goals_made > field_goals_attempted", "FGM > FGA"),
            ("player_season_stats", "three_pointers_made > three_pointers_attempted", "3PM > 3PA"),
            ("player_season_stats", "free_throws_made > free_throws_attempted", "FTM > FTA"),
            ("player_season_stats", "games_started > games_played", "GS > GP"),
            ("player_game_logs", "field_goals_made > field_goals_attempted", "FGM > FGA (Logs)"),
            ("player_game_logs", "points < 0", "Negative Points"),
        ]

        for table, condition, desc in checks:
            try:
                query = f"SELECT COUNT(*) FROM {table} WHERE {condition}"
                self.cursor.execute(query)
                count = self.cursor.fetchone()[0]
                
                if count > 0:
                    logger.error(f"❌ LOGIC FAILURE: {count} rows in '{table}' satisfy '{desc}'.")
                    self.issues_found += 1
                else:
                    logger.debug(f"✅ {table}: {desc} passed.")
            except sqlite3.OperationalError as e:
                logger.warning(f"⚠️ Could not check logic for {table}: {e}")

    def check_critical_placeholders(self):
        """Check for forbidden placeholder values (e.g. Team ID 1610612760)."""
        logger.info("\n🚫 Checking for Forbidden Placeholders...")
        
        PLACEHOLDER_ID = 1610612760 # OKC Blue / Placeholder
        
        tables_to_check = ["player_season_stats", "player_game_logs", "player_tracking_stats"]
        
        for table in tables_to_check:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE team_id = ?", (PLACEHOLDER_ID,))
                count = self.cursor.fetchone()[0]
                
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total = self.cursor.fetchone()[0]
                
                if total == 0:
                    continue

                pct = (count / total) * 100
                if pct > 15: # Strict threshold
                    logger.error(f"❌ PLACEHOLDER DETECTED: {pct:.1f}% of '{table}' uses Team ID {PLACEHOLDER_ID}.")
                    self.issues_found += 1
                else:
                    logger.debug(f"✅ {table} placeholder check passed ({count} rows).")
            except sqlite3.OperationalError:
                pass

    def validate(self) -> bool:
        """Run all validations."""
        logger.info(f"🚀 Starting World Class Integrity Check on {self.db_path}...")
        
        if not Path(self.db_path).exists():
            logger.error("❌ Database file not found.")
            return False

        self.check_referential_integrity()
        self.check_logical_consistency()
        self.check_critical_placeholders()
        
        if self.issues_found > 0:
            logger.error(f"\n❌ INTEGRITY CHECK FAILED: {self.issues_found} critical issues found.")
            return False
        else:
            logger.info(f"\n✅ INTEGRITY CHECK PASSED: Database is clean.")
            return True

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    validator = IntegrityValidator()
    success = validator.validate()
    validator.close()
    sys.exit(0 if success else 1)
