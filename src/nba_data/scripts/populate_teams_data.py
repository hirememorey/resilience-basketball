"""
Script to populate teams data into our database.

This script inserts known NBA team information into the teams table.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
import sqlite3

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.db.schema import NBADatabaseSchema

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# NBA Teams data - known constants for 2024-25 season
NBA_TEAMS = [
    {"team_id": 1610612737, "team_name": "Atlanta Hawks", "team_abbreviation": "ATL", "team_code": "hawks", "team_city": "Atlanta", "team_conference": "East", "team_division": "Southeast"},
    {"team_id": 1610612738, "team_name": "Boston Celtics", "team_abbreviation": "BOS", "team_code": "celtics", "team_city": "Boston", "team_conference": "East", "team_division": "Atlantic"},
    {"team_id": 1610612739, "team_name": "Cleveland Cavaliers", "team_abbreviation": "CLE", "team_code": "cavaliers", "team_city": "Cleveland", "team_conference": "East", "team_division": "Central"},
    {"team_id": 1610612740, "team_name": "New Orleans Pelicans", "team_abbreviation": "NOP", "team_code": "pelicans", "team_city": "New Orleans", "team_conference": "West", "team_division": "Southwest"},
    {"team_id": 1610612741, "team_name": "Chicago Bulls", "team_abbreviation": "CHI", "team_code": "bulls", "team_city": "Chicago", "team_conference": "East", "team_division": "Central"},
    {"team_id": 1610612742, "team_name": "Dallas Mavericks", "team_abbreviation": "DAL", "team_code": "mavericks", "team_city": "Dallas", "team_conference": "West", "team_division": "Southwest"},
    {"team_id": 1610612743, "team_name": "Denver Nuggets", "team_abbreviation": "DEN", "team_code": "nuggets", "team_city": "Denver", "team_conference": "West", "team_division": "Northwest"},
    {"team_id": 1610612744, "team_name": "Golden State Warriors", "team_abbreviation": "GSW", "team_code": "warriors", "team_city": "Golden State", "team_conference": "West", "team_division": "Pacific"},
    {"team_id": 1610612745, "team_name": "Houston Rockets", "team_abbreviation": "HOU", "team_code": "rockets", "team_city": "Houston", "team_conference": "West", "team_division": "Southwest"},
    {"team_id": 1610612746, "team_name": "Los Angeles Clippers", "team_abbreviation": "LAC", "team_code": "clippers", "team_city": "Los Angeles", "team_conference": "West", "team_division": "Pacific"},
    {"team_id": 1610612747, "team_name": "Los Angeles Lakers", "team_abbreviation": "LAL", "team_code": "lakers", "team_city": "Los Angeles", "team_conference": "West", "team_division": "Pacific"},
    {"team_id": 1610612748, "team_name": "Miami Heat", "team_abbreviation": "MIA", "team_code": "heat", "team_city": "Miami", "team_conference": "East", "team_division": "Southeast"},
    {"team_id": 1610612749, "team_name": "Milwaukee Bucks", "team_abbreviation": "MIL", "team_code": "bucks", "team_city": "Milwaukee", "team_conference": "East", "team_division": "Central"},
    {"team_id": 1610612750, "team_name": "Minnesota Timberwolves", "team_abbreviation": "MIN", "team_code": "timberwolves", "team_city": "Minnesota", "team_conference": "West", "team_division": "Northwest"},
    {"team_id": 1610612751, "team_name": "Brooklyn Nets", "team_abbreviation": "BKN", "team_code": "nets", "team_city": "Brooklyn", "team_conference": "East", "team_division": "Atlantic"},
    {"team_id": 1610612752, "team_name": "New York Knicks", "team_abbreviation": "NYK", "team_code": "knicks", "team_city": "New York", "team_conference": "East", "team_division": "Atlantic"},
    {"team_id": 1610612753, "team_name": "Orlando Magic", "team_abbreviation": "ORL", "team_code": "magic", "team_city": "Orlando", "team_conference": "East", "team_division": "Southeast"},
    {"team_id": 1610612754, "team_name": "Philadelphia 76ers", "team_abbreviation": "PHI", "team_code": "76ers", "team_city": "Philadelphia", "team_conference": "East", "team_division": "Atlantic"},
    {"team_id": 1610612755, "team_name": "Phoenix Suns", "team_abbreviation": "PHX", "team_code": "suns", "team_city": "Phoenix", "team_conference": "West", "team_division": "Pacific"},
    {"team_id": 1610612756, "team_name": "Portland Trail Blazers", "team_abbreviation": "POR", "team_code": "blazers", "team_city": "Portland", "team_conference": "West", "team_division": "Northwest"},
    {"team_id": 1610612757, "team_name": "Sacramento Kings", "team_abbreviation": "SAC", "team_code": "kings", "team_city": "Sacramento", "team_conference": "West", "team_division": "Pacific"},
    {"team_id": 1610612758, "team_name": "San Antonio Spurs", "team_abbreviation": "SAS", "team_code": "spurs", "team_city": "San Antonio", "team_conference": "West", "team_division": "Southwest"},
    {"team_id": 1610612759, "team_name": "Toronto Raptors", "team_abbreviation": "TOR", "team_code": "raptors", "team_city": "Toronto", "team_conference": "East", "team_division": "Atlantic"},
    {"team_id": 1610612760, "team_name": "Oklahoma City Thunder", "team_abbreviation": "OKC", "team_code": "thunder", "team_city": "Oklahoma City", "team_conference": "West", "team_division": "Northwest"},
    {"team_id": 1610612761, "team_name": "Washington Wizards", "team_abbreviation": "WAS", "team_code": "wizards", "team_city": "Washington", "team_conference": "East", "team_division": "Southeast"},
    {"team_id": 1610612762, "team_name": "Utah Jazz", "team_abbreviation": "UTA", "team_code": "jazz", "team_city": "Utah", "team_conference": "West", "team_division": "Northwest"},
    {"team_id": 1610612763, "team_name": "Memphis Grizzlies", "team_abbreviation": "MEM", "team_code": "grizzlies", "team_city": "Memphis", "team_conference": "West", "team_division": "Southwest"},
    {"team_id": 1610612764, "team_name": "Detroit Pistons", "team_abbreviation": "DET", "team_code": "pistons", "team_city": "Detroit", "team_conference": "East", "team_division": "Central"},
    {"team_id": 1610612765, "team_name": "Charlotte Hornets", "team_abbreviation": "CHA", "team_code": "hornets", "team_city": "Charlotte", "team_conference": "East", "team_division": "Southeast"},
    {"team_id": 1610612766, "team_name": "Indiana Pacers", "team_abbreviation": "IND", "team_code": "pacers", "team_city": "Indiana", "team_conference": "East", "team_division": "Central"},
]


class TeamsDataPopulator:
    """Populates teams data into database."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.schema = NBADatabaseSchema(db_path)

    def populate_teams_data(self) -> Dict[str, Any]:
        """
        Populate teams data for all teams in our database.

        Returns:
            Summary of population results
        """
        logger.info("Starting teams data population")

        results = {
            "teams_processed": 0,
            "teams_inserted": 0,
            "errors": []
        }

        # Get unique team_ids from players table to only insert teams we actually have players for
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT DISTINCT team_id FROM players WHERE team_id IS NOT NULL ORDER BY team_id')
            existing_team_ids = set(row[0] for row in cursor.fetchall())

            logger.info(f"Found {len(existing_team_ids)} unique team_ids in players table")

            # Filter NBA_TEAMS to only include teams we have players for
            # teams_to_insert = [team for team in NBA_TEAMS if team["team_id"] in existing_team_ids]
            # FORCE INSERT ALL TEAMS - We need them even if no players are currently linked
            teams_to_insert = NBA_TEAMS

            logger.info(f"Will insert {len(teams_to_insert)} teams")

            for team_data in teams_to_insert:
                try:
                    self._insert_team_data(team_data)
                    results["teams_inserted"] += 1
                    results["teams_processed"] += 1
                    logger.info(f"✅ Inserted team: {team_data['team_name']}")

                except Exception as e:
                    logger.error(f"Error inserting team {team_data['team_id']}: {e}")
                    results["errors"].append(f"team_id {team_data['team_id']}: {str(e)}")
                    results["teams_processed"] += 1

        finally:
            conn.close()

        logger.info(f"Teams population complete: {results['teams_inserted']} inserted, {len(results['errors'])} errors")
        return results

    def _insert_team_data(self, team_data: Dict[str, Any]) -> None:
        """Insert team data into database."""
        conn = sqlite3.connect(self.db_path)

        try:
            cursor = conn.cursor()

            # Check if team already exists
            cursor.execute("SELECT COUNT(*) FROM teams WHERE team_id = ?", (team_data["team_id"],))
            exists = cursor.fetchone()[0] > 0

            if exists:
                # Update existing record
                cursor.execute("""
                    UPDATE teams SET
                        team_name = ?,
                        team_abbreviation = ?,
                        team_code = ?,
                        team_city = ?,
                        team_conference = ?,
                        team_division = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE team_id = ?
                """, (
                    team_data["team_name"],
                    team_data["team_abbreviation"],
                    team_data["team_code"],
                    team_data["team_city"],
                    team_data["team_conference"],
                    team_data["team_division"],
                    team_data["team_id"]
                ))
                logger.info(f"Updated existing team: {team_data['team_name']}")
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO teams (
                        team_id, team_name, team_abbreviation, team_code,
                        team_city, team_conference, team_division
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    team_data["team_id"],
                    team_data["team_name"],
                    team_data["team_abbreviation"],
                    team_data["team_code"],
                    team_data["team_city"],
                    team_data["team_conference"],
                    team_data["team_division"]
                ))
                logger.info(f"Inserted new team: {team_data['team_name']}")

            conn.commit()

        except Exception as e:
            logger.error(f"Error inserting team data: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()


def main():
    """Main execution function."""
    populator = TeamsDataPopulator()
    results = populator.populate_teams_data()

    print("\n🎯 Teams Data Population Complete")
    print("=" * 40)
    print(f"Teams processed: {results['teams_processed']}")
    print(f"Teams inserted: {results['teams_inserted']}")
    print(f"Errors: {len(results['errors'])}")

    if results['errors']:
        print("\n❌ Errors encountered:")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(results['errors']) > 5:
            print(f"  ... and {len(results['errors']) - 5} more")

    return results


if __name__ == "__main__":
    main()
