"""
Script to validate database integrity and identify data population issues.
"""

import sys
import sqlite3
from pathlib import Path
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.db.schema import NBADatabaseSchema

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def validate_integrity(db_path: str = "data/nba_stats.db"):
    """Run integrity checks on the database."""
    logger.info(f"🔍 Validating database integrity for {db_path}...")
    
    if not Path(db_path).exists():
        logger.error(f"❌ Database file not found: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    issues_found = 0
    
    # Check 1: Team ID Diversity
    logger.info("\n--- Check 1: Team ID Diversity ---")
    try:
        cursor.execute("SELECT COUNT(DISTINCT team_id) FROM player_season_stats")
        team_count = cursor.fetchone()[0]
        logger.info(f"Unique Team IDs in player_season_stats: {team_count}")
        
        if team_count <= 1:
            logger.error("❌ CRITICAL: Lack of Team ID diversity. Data likely corrupted with placeholders.")
            issues_found += 1
        else:
            logger.info("✅ Team ID diversity looks plausible.")
            
    except Exception as e:
        logger.error(f"Check failed: {e}")

    # Check 2: Placeholder Team ID Usage
    logger.info("\n--- Check 2: Placeholder Usage ---")
    PLACEHOLDER_ID = 1610612760  # OKC
    try:
        cursor.execute(f"SELECT COUNT(*) FROM player_season_stats WHERE team_id = {PLACEHOLDER_ID}")
        okc_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM player_season_stats")
        total_count = cursor.fetchone()[0]
        
        if total_count > 0:
            pct_okc = (okc_count / total_count) * 100
            logger.info(f"Rows with Team ID {PLACEHOLDER_ID} (OKC): {okc_count}/{total_count} ({pct_okc:.1f}%)")
            
            if pct_okc > 10: # Allow some legitimate OKC players, but not 100%
                logger.error("❌ CRITICAL: Suspiciously high number of players on OKC. Placeholder data detected.")
                issues_found += 1
        else:
            logger.warning("⚠️ Table player_season_stats is empty.")
            
    except Exception as e:
        logger.error(f"Check failed: {e}")

    # Check 3: Primary Key Collisions (Simulated)
    # Since the current PK is (player_id, season, team_id), we check if we have multiple entries 
    # for the same player-season that might be distinct if season_type was included
    logger.info("\n--- Check 3: Potential Season Type Collisions ---")
    try:
        # We can't easily check for collisions if they've already overwritten each other.
        # Instead, we check if we have any data that explicitly looks like playoffs in the season stats
        # or if the counts match what we expect.
        
        cursor.execute("SELECT COUNT(*) FROM player_playoff_stats")
        playoff_count = cursor.fetchone()[0]
        logger.info(f"Rows in player_playoff_stats: {playoff_count}")
        
        if playoff_count == 0:
             logger.warning("⚠️ player_playoff_stats is empty. Playoff data might be missing or misrouted.")
             
    except Exception as e:
        logger.error(f"Check failed: {e}")

    conn.close()
    
    if issues_found > 0:
        logger.error(f"\n❌ Validation Failed: {issues_found} critical issues detected.")
        return False
    else:
        logger.info("\n✅ Validation Passed: No critical integrity issues found.")
        return True

if __name__ == "__main__":
    validate_integrity()
