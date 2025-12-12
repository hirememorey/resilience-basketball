#!/usr/bin/env python3
"""
Validation script for possession-level data.

Validates the quality and completeness of possession-level analytics data.
"""

import sys
from pathlib import Path
import sqlite3
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.nba_data.db.schema import NBADatabaseSchema


class PossessionDataValidator:
    """Validates possession-level data quality and completeness."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.schema = NBADatabaseSchema(db_path)

    def run_full_validation(self) -> Dict[str, Any]:
        """Run comprehensive possession data validation."""
        print("🔍 Validating Possession-Level Data...")
        print("=" * 50)

        results = {
            "possession_tables_exist": self._check_possession_tables(),
            "possession_data_completeness": self._check_possession_completeness(),
            "possession_data_quality": self._check_possession_quality(),
            "possession_analytics_ready": False
        }

        # Determine overall validation status
        results["possession_analytics_ready"] = self._assess_possession_readiness(results)

        self._print_possession_report(results)
        return results

    def _check_possession_tables(self) -> Dict[str, Any]:
        """Check that possession tables exist and have proper structure."""
        status = {"tables_exist": False, "tables_populated": False}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if possession tables exist
                required_tables = ['possessions', 'possession_lineups', 'possession_events', 'possession_matchups']
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = {row[0] for row in cursor.fetchall()}

                status["tables_exist"] = all(table in existing_tables for table in required_tables)
                status["existing_tables"] = [t for t in required_tables if t in existing_tables]
                status["missing_tables"] = [t for t in required_tables if t not in existing_tables]

                # Check if tables have data
                populated_tables = []
                for table in required_tables:
                    if table in existing_tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        if count > 0:
                            populated_tables.append(f"{table} ({count} rows)")

                status["tables_populated"] = len(populated_tables) > 0
                status["populated_tables"] = populated_tables

        except Exception as e:
            status["error"] = str(e)

        return status

    def _check_possession_completeness(self) -> Dict[str, Any]:
        """Check possession data completeness."""
        completeness = {
            "possessions_count": 0,
            "events_count": 0,
            "lineups_count": 0,
            "matchups_count": 0,
            "games_with_possessions": 0,
            "avg_events_per_possession": 0.0
        }

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Count records in each table
                cursor.execute("SELECT COUNT(*) FROM possessions")
                completeness["possessions_count"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM possession_events")
                completeness["events_count"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM possession_lineups")
                completeness["lineups_count"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM possession_matchups")
                completeness["matchups_count"] = cursor.fetchone()[0]

                # Count games with possession data
                cursor.execute("SELECT COUNT(DISTINCT game_id) FROM possessions")
                completeness["games_with_possessions"] = cursor.fetchone()[0]

                # Calculate average events per possession
                if completeness["possessions_count"] > 0:
                    completeness["avg_events_per_possession"] = (
                        completeness["events_count"] / completeness["possessions_count"]
                    )

        except Exception as e:
            completeness["error"] = str(e)

        return completeness

    def _check_possession_quality(self) -> Dict[str, Any]:
        """Check possession data quality."""
        quality = {
            "valid_possession_durations": False,
            "valid_event_sequences": False,
            "valid_team_assignments": False,
            "data_integrity_score": 0.0
        }

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check possession durations are reasonable (0-30 seconds)
                cursor.execute("""
                    SELECT COUNT(*) FROM possessions
                    WHERE duration_seconds BETWEEN 0 AND 30
                """)
                valid_durations = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM possessions")
                total_possessions = cursor.fetchone()[0]

                quality["valid_possession_durations"] = (
                    valid_durations == total_possessions if total_possessions > 0 else True
                )

                # Check event sequences are valid
                cursor.execute("""
                    SELECT COUNT(DISTINCT possession_id) FROM possession_events
                    WHERE event_number >= 0
                """)
                valid_sequences = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(DISTINCT possession_id) FROM possession_events")
                total_event_possessions = cursor.fetchone()[0]

                quality["valid_event_sequences"] = (
                    valid_sequences == total_event_possessions if total_event_possessions > 0 else True
                )

                # Calculate data integrity score
                checks_passed = sum([
                    quality["valid_possession_durations"],
                    quality["valid_event_sequences"],
                    True  # Placeholder for team assignments check
                ])

                quality["data_integrity_score"] = (checks_passed / 3) * 100

        except Exception as e:
            quality["error"] = str(e)

        return quality

    def _assess_possession_readiness(self, results: Dict[str, Any]) -> bool:
        """Assess if possession data is ready for resilience analysis."""
        # Check table existence
        if not results["possession_tables_exist"]["tables_exist"]:
            return False

        # Check basic data presence
        completeness = results["possession_data_completeness"]
        if completeness["possessions_count"] == 0:
            return False

        # Check data quality
        quality = results["possession_data_quality"]
        if quality["data_integrity_score"] < 80.0:
            return False

        return True

    def _print_possession_report(self, results: Dict[str, Any]):
        """Print possession validation report."""
        print("\n📊 Possession Data Validation Report")
        print("=" * 40)

        # Tables status
        tables = results["possession_tables_exist"]
        if tables["tables_exist"]:
            print("✅ Possession tables: EXIST")
            print(f"   Tables: {', '.join(tables['existing_tables'])}")
            if tables["tables_populated"]:
                print(f"   Populated: {', '.join(tables['populated_tables'])}")
            else:
                print("   Status: Tables exist but are empty")
        else:
            print("❌ Possession tables: MISSING")
            print(f"   Missing: {', '.join(tables['missing_tables'])}")

        # Data completeness
        comp = results["possession_data_completeness"]
        print("\n📈 Data Completeness:")
        print(f"   Possessions: {comp['possessions_count']}")
        print(f"   Events: {comp['events_count']}")
        print(f"   Lineups: {comp['lineups_count']}")
        print(f"   Matchups: {comp['matchups_count']}")
        print(f"   Games covered: {comp['games_with_possessions']}")
        print(f"   Avg events/possession: {comp['avg_events_per_possession']:.1f}")

        # Data quality
        qual = results["possession_data_quality"]
        print("\n🎯 Data Quality:")
        print(f"   Valid durations: {'✅' if qual['valid_possession_durations'] else '❌'}")
        print(f"   Valid sequences: {'✅' if qual['valid_event_sequences'] else '❌'}")
        print(f"   Integrity score: {qual['data_integrity_score']:.1f}%")

        # Overall assessment
        if results["possession_analytics_ready"]:
            print("\n🎉 Overall Assessment: ✅ POSSESSION ANALYTICS READY")
            print("   Data is ready for playoff resilience modeling!")
        else:
            print("\n❌ Overall Assessment: POSSESSION ANALYTICS NOT READY")
            print("   Additional data collection and validation needed.")


def main():
    """Main execution function."""
    validator = PossessionDataValidator()
    results = validator.run_full_validation()


if __name__ == "__main__":
    main()
