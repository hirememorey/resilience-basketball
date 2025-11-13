#!/usr/bin/env python3
"""
Data validation script for the NBA player data pipeline.

Validates data quality, completeness, and consistency in our database.
"""

import sys
from pathlib import Path
import sqlite3
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.nba_data.db.schema import NBADatabaseSchema


class DataValidator:
    """Validates the quality and completeness of NBA data."""

    def __init__(self, db_path: str = "data/nba_stats.db"):
        """Initialize with database path."""
        self.db_path = Path(db_path)
        self.schema = NBADatabaseSchema(db_path)

    def run_full_validation(self) -> Dict[str, Any]:
        """Run comprehensive data validation."""
        print("🔍 Running comprehensive data validation...")
        print("=" * 60)

        results = {
            "database_status": self._check_database_status(),
            "data_completeness": self._check_data_completeness(),
            "data_quality": self._check_data_quality(),
            "statistical_summary": self._generate_statistical_summary(),
            "validation_passed": False
        }

        # Determine overall validation status
        results["validation_passed"] = self._assess_overall_health(results)

        self._print_validation_report(results)
        return results

    def _check_database_status(self) -> Dict[str, Any]:
        """Check basic database status."""
        status = {"tables_exist": False, "tables_populated": False}

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if core tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                required_tables = ['teams', 'games', 'players', 'player_season_stats',
                                 'player_advanced_stats', 'player_tracking_stats', 'possessions']

                status["tables_exist"] = all(table in tables for table in required_tables)
                status["existing_tables"] = tables

                # Check if tables have data
                populated_tables = []
                for table in required_tables:
                    if table in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        if count > 0:
                            populated_tables.append(f"{table} ({count} rows)")

                status["tables_populated"] = len(populated_tables) > 0
                status["populated_tables"] = populated_tables

        except Exception as e:
            status["error"] = str(e)

        return status

    def _check_data_completeness(self) -> Dict[str, Any]:
        """Check data completeness across tables."""
        completeness = {
            "players_with_season_stats": 0,
            "players_with_advanced_stats": 0,
            "players_with_tracking_stats": 0,
            "players_with_playoff_stats": 0,
            "players_with_playoff_advanced_stats": 0,
            "players_with_playoff_tracking_stats": 0,
            "season_coverage": {},
            "playoff_season_coverage": {},
            "metric_coverage": {}
        }

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Count players by stat type (regular season)
                cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_season_stats")
                completeness["players_with_season_stats"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_advanced_stats")
                completeness["players_with_advanced_stats"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_tracking_stats")
                completeness["players_with_tracking_stats"] = cursor.fetchone()[0]

                # Count players by stat type (playoffs)
                cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_playoff_stats")
                completeness["players_with_playoff_stats"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_playoff_advanced_stats")
                completeness["players_with_playoff_advanced_stats"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_playoff_tracking_stats")
                completeness["players_with_playoff_tracking_stats"] = cursor.fetchone()[0]

                # Playtype stats
                cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_playtype_stats")
                completeness["players_with_playtype_stats"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_playoff_playtype_stats")
                completeness["players_with_playoff_playtype_stats"] = cursor.fetchone()[0]

                # Season coverage
                cursor.execute("SELECT season, COUNT(DISTINCT player_id) FROM player_season_stats GROUP BY season")
                completeness["season_coverage"] = {row[0]: row[1] for row in cursor.fetchall()}

                # Playoff season coverage
                cursor.execute("SELECT season, COUNT(DISTINCT player_id) FROM player_playoff_stats GROUP BY season")
                completeness["playoff_season_coverage"] = {row[0]: row[1] for row in cursor.fetchall()}

                # Metric coverage for season stats
                cursor.execute("SELECT COUNT(*) FROM player_season_stats WHERE field_goal_percentage IS NOT NULL")
                completeness["metric_coverage"]["fg_pct_available"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM player_season_stats WHERE points IS NOT NULL")
                completeness["metric_coverage"]["pts_available"] = cursor.fetchone()[0]

        except Exception as e:
            completeness["error"] = str(e)

        return completeness

    def _check_data_quality(self) -> Dict[str, Any]:
        """Check data quality metrics."""
        quality = {
            "stat_ranges_valid": True,  # Start with True, set to False if issues found
            "negative_values": {},
            "outliers": {},
            "missing_values": {"null_points": 0, "null_usage": 0}
        }

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check for negative values where they shouldn't exist
                negative_checks = [
                    ("points", "player_season_stats"),
                    ("assists", "player_season_stats"),
                    ("rebounds", "player_season_stats"),
                    ("steals", "player_season_stats"),
                    ("blocks", "player_season_stats"),
                    ("usage_percentage", "player_advanced_stats"),
                    ("true_shooting_percentage", "player_advanced_stats")
                ]

                for column, table in negative_checks:
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} < 0")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        quality["negative_values"][f"{table}.{column}"] = count

                # Check percentage ranges (0-1 for most stats, but allow higher for advanced stats)
                cursor.execute("SELECT COUNT(*) FROM player_season_stats WHERE field_goal_percentage > 1.0 OR field_goal_percentage < 0 OR three_point_percentage > 1.0 OR three_point_percentage < 0 OR free_throw_percentage > 1.0 OR free_throw_percentage < 0")
                invalid_pct = cursor.fetchone()[0]
                if invalid_pct > 0:
                    quality["stat_ranges_valid"] = False
                    quality["invalid_percentages"] = invalid_pct
                else:
                    quality["stat_ranges_valid"] = True

                # Check for missing critical values
                cursor.execute("SELECT COUNT(*) FROM player_season_stats WHERE points IS NULL")
                quality["missing_values"]["null_points"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM player_advanced_stats WHERE usage_percentage IS NULL")
                quality["missing_values"]["null_usage"] = cursor.fetchone()[0]

        except Exception as e:
            quality["error"] = str(e)

        return quality

    def _generate_statistical_summary(self) -> Dict[str, Any]:
        """Generate statistical summary of the data."""
        summary = {
            "top_scorers": [],
            "high_usage_players": [],
            "best_shooters": [],
            "season_stats": {}
        }

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Top 5 scorers
                cursor.execute("""
                    SELECT 'Player_' || player_id, points
                    FROM player_season_stats
                    WHERE points IS NOT NULL
                    ORDER BY points DESC
                    LIMIT 5
                """)
                summary["top_scorers"] = cursor.fetchall()

                # Top 5 usage rate players
                cursor.execute("""
                    SELECT 'Player_' || player_id, usage_percentage
                    FROM player_advanced_stats
                    WHERE usage_percentage IS NOT NULL
                    ORDER BY usage_percentage DESC
                    LIMIT 5
                """)
                summary["high_usage_players"] = cursor.fetchall()

                # Best shooters (FG%)
                cursor.execute("""
                    SELECT 'Player_' || player_id, field_goal_percentage
                    FROM player_season_stats
                    WHERE field_goal_percentage IS NOT NULL
                    ORDER BY field_goal_percentage DESC
                    LIMIT 5
                """)
                summary["best_shooters"] = cursor.fetchall()

                # Season summary
                cursor.execute("""
                    SELECT
                        COUNT(DISTINCT player_id) as total_players,
                        AVG(points) as avg_points,
                        AVG(field_goal_percentage) as avg_fg_pct,
                        MAX(points) as max_points
                    FROM player_season_stats
                    WHERE points IS NOT NULL
                """)
                row = cursor.fetchone()
                if row:
                    summary["season_stats"] = {
                        "total_players": row[0],
                        "avg_points": round(row[1], 1) if row[1] else None,
                        "avg_fg_pct": round(row[2], 3) if row[2] else None,
                        "max_points": row[3]
                    }

        except Exception as e:
            summary["error"] = str(e)

        return summary

    def _assess_overall_health(self, results: Dict[str, Any]) -> bool:
        """Assess overall data health."""
        try:
            # Must have tables and data
            if not results["database_status"]["tables_populated"]:
                return False

            # Must have reasonable number of players
            completeness = results["data_completeness"]
            if completeness["players_with_season_stats"] < 100:
                return False

            # Must have valid stat ranges
            if not results["data_quality"]["stat_ranges_valid"]:
                return False

            # Should not have too many negative values
            negative_count = sum(results["data_quality"]["negative_values"].values())
            if negative_count > 10:  # Allow some minor data issues
                return False

            return True

        except:
            return False

    def _print_validation_report(self, results: Dict[str, Any]):
        """Print a comprehensive validation report."""
        print("\n📊 NBA Data Validation Report")
        print("=" * 60)

        # Database Status
        db_status = results["database_status"]
        print(f"✅ Database Status: {'OK' if db_status['tables_exist'] else 'ISSUES'}")
        print(f"   Tables exist: {db_status['tables_exist']}")
        print(f"   Tables populated: {db_status['tables_populated']}")
        if db_status['populated_tables']:
            print(f"   Populated tables: {', '.join(db_status['populated_tables'])}")

        # Data Completeness
        completeness = results["data_completeness"]
        print(f"\n✅ Data Completeness:")

        # Regular Season Data
        print(f"   Regular Season:")
        print(f"     Players with season stats: {completeness['players_with_season_stats']}")
        print(f"     Players with advanced stats: {completeness['players_with_advanced_stats']}")
        print(f"     Players with tracking stats: {completeness['players_with_tracking_stats']}")
        print(f"     Players with playtype stats: {completeness['players_with_playtype_stats']}")

        if completeness['season_coverage']:
            print(f"     Seasons covered: {list(completeness['season_coverage'].keys())}")

        # Playoff Data
        print(f"   Playoffs:")
        print(f"     Players with playoff stats: {completeness['players_with_playoff_stats']}")
        print(f"     Players with playoff advanced stats: {completeness['players_with_playoff_advanced_stats']}")
        print(f"     Players with playoff tracking stats: {completeness['players_with_playoff_tracking_stats']}")
        print(f"     Players with playoff playtype stats: {completeness['players_with_playoff_playtype_stats']}")

        if completeness['playoff_season_coverage']:
            print(f"     Playoff seasons covered: {list(completeness['playoff_season_coverage'].keys())}")

        # Data Quality
        quality = results["data_quality"]
        print(f"\n✅ Data Quality:")
        print(f"   Stat ranges valid: {quality['stat_ranges_valid']}")

        if quality['negative_values']:
            print(f"   ⚠️  Negative values found: {quality['negative_values']}")
        else:
            print("   ✅ No invalid negative values")

        if quality['missing_values']:
            print(f"   ⚠️  Missing values: {quality['missing_values']}")

        # Statistical Summary
        stats = results["statistical_summary"]
        if stats['season_stats']:
            season_stats = stats['season_stats']
            print(f"\n✅ Statistical Summary:")
            print(f"   Total players: {season_stats['total_players']}")
            print(f"   Average points: {season_stats['avg_points']}")
            print(f"   Average FG%: {season_stats['avg_fg_pct']}")
            print(f"   Max points: {season_stats['max_points']}")

        # Overall Assessment
        print(f"\n🎯 Overall Assessment: {'✅ PASSED' if results['validation_passed'] else '❌ FAILED'}")

        if results['validation_passed']:
            print("   Data pipeline is healthy and ready for analysis!")
        else:
            print("   Data quality issues detected. Review report above.")


def main():
    """Main validation entry point."""
    validator = DataValidator()

    try:
        results = validator.run_full_validation()

        # Exit with appropriate code
        return 0 if results["validation_passed"] else 1

    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
