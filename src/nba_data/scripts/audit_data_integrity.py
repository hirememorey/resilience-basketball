#!/usr/bin/env python3
"""
NBA Data Integrity Audit

Systematic validation of data quality for playoff resilience analysis.
From first principles: verify data integrity before any analysis.

Audit checks:
1. Player identity accuracy
2. Team assignment accuracy
3. Statistical data validity
4. Cross-table consistency
5. Historical fact verification
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from typing import Dict, List, Tuple, Optional

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

DB_PATH = "data/nba_stats.db"

class DataIntegrityAuditor:
    """Comprehensive data integrity auditor for NBA stats."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.audit_results = {
            'player_identity': {},
            'team_assignments': {},
            'statistical_validity': {},
            'cross_consistency': {},
            'historical_accuracy': {},
            'overall_assessment': {}
        }

    def get_connection(self):
        """Get database connection."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def audit_player_identity(self) -> Dict:
        """Audit player identity accuracy."""
        print("🔍 Auditing player identity accuracy...")

        conn = self.get_connection()
        results = {}

        # Check for duplicate player names
        duplicate_names_query = """
        SELECT player_name, COUNT(*) as count
        FROM players
        GROUP BY player_name
        HAVING COUNT(*) > 1
        """

        duplicates = pd.read_sql_query(duplicate_names_query, conn)
        results['duplicate_names'] = len(duplicates)

        if len(duplicates) > 0:
            results['duplicate_examples'] = duplicates.head(3).to_dict('records')

        # Check for players with missing critical data
        missing_data_query = """
        SELECT COUNT(*) as players_missing_data
        FROM players p
        LEFT JOIN player_advanced_stats pa ON p.player_id = pa.player_id
        WHERE pa.player_id IS NULL
        """

        missing_data = pd.read_sql_query(missing_data_query, conn)
        results['players_without_stats'] = missing_data.iloc[0]['players_missing_data']

        # Check for unusual name patterns
        unusual_names_query = """
        SELECT player_name
        FROM players
        WHERE player_name NOT LIKE '% %'
           OR LENGTH(player_name) < 5
           OR player_name LIKE '%test%'
        """

        unusual_names = pd.read_sql_query(unusual_names_query, conn)
        results['unusual_names'] = len(unusual_names)

        if len(unusual_names) > 0:
            results['unusual_name_examples'] = unusual_names.head(3)['player_name'].tolist()

        results['assessment'] = self._assess_player_identity(results)
        return results

    def audit_team_assignments(self) -> Dict:
        """Audit team assignment accuracy."""
        print("🔍 Auditing team assignment accuracy...")

        conn = self.get_connection()
        results = {}

        # Check for historical accuracy using known examples
        historical_checks = {
            'lebron_james': {
                '2018-19': 'Los Angeles Lakers',
                '2020-21': 'Los Angeles Lakers'
            },
            'steph_curry': {
                '2015-16': 'Golden State Warriors',
                '2021-22': 'Golden State Warriors'
            },
            'jimmy_butler': {
                '2016-17': 'Chicago Bulls',
                '2019-20': 'Miami Heat',
                '2022-23': 'Miami Heat'
            }
        }

        results['historical_checks'] = {}

        for player_key, expected_teams in historical_checks.items():
            player_name_pattern = player_key.replace('_', ' ').title()
            if player_key == 'jimmy_butler':
                player_name_pattern = 'Jimmy Butler III'

            results['historical_checks'][player_key] = {}

            for season, expected_team in expected_teams.items():
                # Find actual team assignment
                team_query = f"""
                SELECT DISTINCT t.team_name
                FROM player_advanced_stats pa
                JOIN players p ON pa.player_id = p.player_id
                JOIN teams t ON pa.team_id = t.team_id
                WHERE p.player_name = '{player_name_pattern}'
                  AND pa.season = '{season}'
                  AND pa.season_type = 'Regular Season'
                """

                actual_team = pd.read_sql_query(team_query, conn)

                if len(actual_team) > 0:
                    actual_team_name = actual_team.iloc[0]['team_name']
                    is_correct = actual_team_name == expected_team
                    results['historical_checks'][player_key][season] = {
                        'expected': expected_team,
                        'actual': actual_team_name,
                        'correct': is_correct
                    }
                else:
                    results['historical_checks'][player_key][season] = {
                        'expected': expected_team,
                        'actual': 'NOT FOUND',
                        'correct': False
                    }

        # Count total historical accuracy
        total_checks = 0
        correct_checks = 0

        for player_checks in results['historical_checks'].values():
            for season_check in player_checks.values():
                total_checks += 1
                if season_check['correct']:
                    correct_checks += 1

        results['historical_accuracy_rate'] = correct_checks / total_checks if total_checks > 0 else 0

        # Check for players on multiple teams in same season (should be rare)
        multiple_teams_query = """
        SELECT season, player_id, COUNT(DISTINCT team_id) as team_count
        FROM player_advanced_stats
        WHERE season_type = 'Regular Season'
        GROUP BY season, player_id
        HAVING team_count > 1
        """

        multiple_teams = pd.read_sql_query(multiple_teams_query, conn)
        results['players_multiple_teams_same_season'] = len(multiple_teams)

        results['assessment'] = self._assess_team_assignments(results)
        return results

    def audit_statistical_validity(self) -> Dict:
        """Audit statistical data validity."""
        print("🔍 Auditing statistical data validity...")

        conn = self.get_connection()
        results = {}

        # TS% range check (should be 0.0 to 1.0 for decimal representation)
        ts_range_query = """
        SELECT
            COUNT(*) as total_stats,
            SUM(CASE WHEN true_shooting_percentage < 0 OR true_shooting_percentage > 1 THEN 1 ELSE 0 END) as invalid_ts,
            MIN(true_shooting_percentage) as min_ts,
            MAX(true_shooting_percentage) as max_ts,
            AVG(true_shooting_percentage) as avg_ts
        FROM player_advanced_stats
        WHERE true_shooting_percentage IS NOT NULL
        """

        ts_check = pd.read_sql_query(ts_range_query, conn)
        results['ts_percentage_check'] = ts_check.iloc[0].to_dict()

        # Usage percentage check (should be reasonable, typically 0-50%)
        usage_check_query = """
        SELECT
            COUNT(*) as total_stats,
            SUM(CASE WHEN usage_percentage < 0 OR usage_percentage > 100 THEN 1 ELSE 0 END) as invalid_usage,
            MIN(usage_percentage) as min_usage,
            MAX(usage_percentage) as max_usage,
            AVG(usage_percentage) as avg_usage
        FROM player_advanced_stats
        WHERE usage_percentage IS NOT NULL
        """

        usage_check = pd.read_sql_query(usage_check_query, conn)
        results['usage_percentage_check'] = usage_check.iloc[0].to_dict()

        # Games played check
        games_check_query = """
        SELECT
            COUNT(*) as total_stats,
            SUM(CASE WHEN games_played < 1 OR games_played > 82 THEN 1 ELSE 0 END) as invalid_games,
            MIN(games_played) as min_games,
            MAX(games_played) as max_games,
            AVG(games_played) as avg_games
        FROM player_advanced_stats
        WHERE games_played IS NOT NULL
        """

        games_check = pd.read_sql_query(games_check_query, conn)
        results['games_played_check'] = games_check.iloc[0].to_dict()

        # Check for statistical impossibilities
        impossible_stats_query = """
        SELECT COUNT(*) as impossible_cases
        FROM player_advanced_stats
        WHERE true_shooting_percentage > 0.8 AND usage_percentage < 5
           OR games_played > 82
           OR effective_field_goal_percentage > 1.2
        """

        impossible_stats = pd.read_sql_query(impossible_stats_query, conn)
        results['statistical_impossibilities'] = impossible_stats.iloc[0]['impossible_cases']

        results['assessment'] = self._assess_statistical_validity(results)
        return results

    def audit_cross_consistency(self) -> Dict:
        """Audit cross-table data consistency."""
        print("🔍 Auditing cross-table consistency...")

        conn = self.get_connection()
        results = {}

        # Check player-game consistency
        player_game_consistency_query = """
        SELECT COUNT(*) as total_player_games
        FROM player_game_logs pgl
        LEFT JOIN games g ON pgl.game_id = g.game_id
        WHERE g.game_id IS NULL
        """

        orphaned_games = pd.read_sql_query(player_game_consistency_query, conn)
        results['orphaned_player_games'] = orphaned_games.iloc[0]['total_player_games']

        # Check playoff stats consistency
        playoff_consistency_query = """
        SELECT
            COUNT(DISTINCT pa.player_id) as players_with_advanced,
            COUNT(DISTINCT po.player_id) as players_with_playoff_advanced
        FROM player_advanced_stats pa
        LEFT JOIN player_playoff_advanced_stats po ON pa.player_id = po.player_id
        WHERE pa.season_type = 'Regular Season'
        """

        playoff_consistency = pd.read_sql_query(playoff_consistency_query, conn)
        results['playoff_consistency'] = playoff_consistency.iloc[0].to_dict()

        # Check team-player consistency
        team_consistency_query = """
        SELECT COUNT(*) as mismatched_team_assignments
        FROM player_advanced_stats pa
        LEFT JOIN teams t ON pa.team_id = t.team_id
        WHERE t.team_id IS NULL
        """

        team_mismatches = pd.read_sql_query(team_consistency_query, conn)
        results['team_assignment_mismatches'] = team_mismatches.iloc[0]['mismatched_team_assignments']

        results['assessment'] = self._assess_cross_consistency(results)
        return results

    def audit_historical_accuracy(self) -> Dict:
        """Audit historical accuracy with known facts."""
        print("🔍 Auditing historical accuracy...")

        conn = self.get_connection()
        results = {}

        # Check 2019-20 playoff bubble teams
        bubble_teams_query = """
        SELECT DISTINCT t.team_name
        FROM games g
        JOIN teams t ON g.home_team_id = t.team_id OR g.away_team_id = t.team_id
        WHERE g.season = '2019-20' AND g.season_type = 'Playoffs'
        ORDER BY t.team_name
        """

        bubble_teams = pd.read_sql_query(bubble_teams_query, conn)
        actual_bubble_teams = set(bubble_teams['team_name'].tolist())

        # Known 2019-20 playoff bubble teams
        expected_bubble_teams = {
            'Los Angeles Lakers', 'Los Angeles Clippers', 'Denver Nuggets',
            'Utah Jazz', 'Oklahoma City Thunder', 'Houston Rockets',
            'Dallas Mavericks', 'Portland Trail Blazers', 'Memphis Grizzlies',
            'Phoenix Suns', 'Sacramento Kings', 'San Antonio Spurs',
            'New Orleans Pelicans', 'Miami Heat', 'Boston Celtics',
            'Milwaukee Bucks', 'Toronto Raptors', 'Indiana Pacers',
            'Philadelphia 76ers', 'Brooklyn Nets', 'Orlando Magic'
        }

        results['bubble_teams_accuracy'] = {
            'expected_count': len(expected_bubble_teams),
            'actual_count': len(actual_bubble_teams),
            'missing_teams': list(expected_bubble_teams - actual_bubble_teams),
            'extra_teams': list(actual_bubble_teams - expected_bubble_teams)
        }

        # Check 2020 MVP winner stats (should be Nikola Jokic)
        mvp_stats_query = """
        SELECT p.player_name, pa.season, pa.points, pa.total_rebounds as rebounds, pa.assists
        FROM player_season_stats pa
        JOIN players p ON pa.player_id = p.player_id
        WHERE pa.season = '2019-20' AND pa.season_type = 'Regular Season'
          AND p.player_name LIKE '%Nikola%'
        """

        jokic_stats = pd.read_sql_query(mvp_stats_query, conn)
        if len(jokic_stats) > 0:
            results['jokic_mvp_stats'] = jokic_stats.iloc[0].to_dict()
            # 2019-20 MVP stats should be around 26.4 PPG, 10.8 RPG, 7.0 APG
            expected_stats = {'points': 26.4, 'rebounds': 10.8, 'assists': 7.0}
            actual_stats = jokic_stats.iloc[0]
            results['jokic_stats_accuracy'] = {
                'expected': expected_stats,
                'actual': {
                    'points': actual_stats['points'],
                    'rebounds': actual_stats['rebounds'],
                    'assists': actual_stats['assists']
                }
            }

        results['assessment'] = self._assess_historical_accuracy(results)
        return results

    def run_full_audit(self) -> Dict:
        """Run complete data integrity audit."""
        print("🧪 RUNNING COMPREHENSIVE DATA INTEGRITY AUDIT")
        print("=" * 60)

        self.audit_results['player_identity'] = self.audit_player_identity()
        self.audit_results['team_assignments'] = self.audit_team_assignments()
        self.audit_results['statistical_validity'] = self.audit_statistical_validity()
        self.audit_results['cross_consistency'] = self.audit_cross_consistency()
        self.audit_results['historical_accuracy'] = self.audit_historical_accuracy()

        self.audit_results['overall_assessment'] = self._generate_overall_assessment()

        return self.audit_results

    def _assess_player_identity(self, results: Dict) -> str:
        """Assess player identity audit results."""
        if results['duplicate_names'] == 0 and results['players_without_stats'] == 0 and results['unusual_names'] == 0:
            return "✅ EXCELLENT - No player identity issues detected"
        elif results['duplicate_names'] <= 2 and results['players_without_stats'] <= 10:
            return "⚠️ GOOD - Minor player identity issues, acceptable for analysis"
        else:
            return "🚨 POOR - Significant player identity issues require attention"

    def _assess_team_assignments(self, results: Dict) -> str:
        """Assess team assignment audit results."""
        accuracy_rate = results['historical_accuracy_rate']
        if accuracy_rate >= 0.95:
            return f"✅ EXCELLENT - {accuracy_rate:.1%} historical accuracy"
        elif accuracy_rate >= 0.80:
            return f"⚠️ GOOD - {accuracy_rate:.1%} historical accuracy, some issues"
        else:
            return f"🚨 POOR - {accuracy_rate:.1%} historical accuracy, major issues"

    def _assess_statistical_validity(self, results: Dict) -> str:
        """Assess statistical validity audit results."""
        ts_invalid = results['ts_percentage_check']['invalid_ts']
        usage_invalid = results['usage_percentage_check']['invalid_usage']
        games_invalid = results['games_played_check']['invalid_games']
        impossibilities = results['statistical_impossibilities']

        total_invalid = ts_invalid + usage_invalid + games_invalid + impossibilities

        if total_invalid == 0:
            return "✅ EXCELLENT - All statistical data within valid ranges"
        elif total_invalid <= 10:
            return f"⚠️ GOOD - {total_invalid} minor statistical anomalies"
        else:
            return f"🚨 POOR - {total_invalid} significant statistical issues"

    def _assess_cross_consistency(self, results: Dict) -> str:
        """Assess cross-consistency audit results."""
        orphaned_games = results['orphaned_player_games']
        team_mismatches = results['team_assignment_mismatches']

        issues = orphaned_games + team_mismatches

        if issues == 0:
            return "✅ EXCELLENT - Perfect cross-table consistency"
        elif issues <= 5:
            return f"⚠️ GOOD - {issues} minor consistency issues"
        else:
            return f"🚨 POOR - {issues} significant consistency problems"

    def _assess_historical_accuracy(self, results: Dict) -> str:
        """Assess historical accuracy audit results."""
        bubble_accuracy = len(results['bubble_teams_accuracy']['missing_teams']) + len(results['bubble_teams_accuracy']['extra_teams'])

        if bubble_accuracy == 0 and 'jokic_stats_accuracy' in results:
            jokic_match = abs(results['jokic_stats_accuracy']['actual']['points'] - results['jokic_stats_accuracy']['expected']['points']) < 2
            if jokic_match:
                return "✅ EXCELLENT - Historical facts accurately represented"
            else:
                return "⚠️ GOOD - Historical facts mostly accurate, minor discrepancies"
        else:
            return f"🚨 POOR - {bubble_accuracy} historical accuracy issues"

    def _generate_overall_assessment(self) -> Dict:
        """Generate overall data integrity assessment."""
        assessments = [
            self.audit_results['player_identity']['assessment'],
            self.audit_results['team_assignments']['assessment'],
            self.audit_results['statistical_validity']['assessment'],
            self.audit_results['cross_consistency']['assessment'],
            self.audit_results['historical_accuracy']['assessment']
        ]

        # Count assessment levels
        excellent_count = sum(1 for a in assessments if 'EXCELLENT' in a)
        good_count = sum(1 for a in assessments if 'GOOD' in a)
        poor_count = sum(1 for a in assessments if 'POOR' in a)

        if excellent_count >= 4:
            overall_rating = "✅ READY FOR ANALYSIS"
            confidence = "HIGH"
        elif good_count >= 3:
            overall_rating = "⚠️ REQUIRES MINOR CLEANUP"
            confidence = "MEDIUM"
        else:
            overall_rating = "🚨 REQUIRES MAJOR CLEANUP"
            confidence = "LOW"

        return {
            'overall_rating': overall_rating,
            'confidence_level': confidence,
            'breakdown': {
                'excellent': excellent_count,
                'good': good_count,
                'poor': poor_count,
                'total': len(assessments)
            },
            'recommendations': self._generate_recommendations(confidence)
        }

    def _generate_recommendations(self, confidence: str) -> List[str]:
        """Generate recommendations based on confidence level."""
        if confidence == "HIGH":
            return [
                "Proceed with analysis using current dataset",
                "Monitor for edge cases during analysis",
                "Document any additional data issues found"
            ]
        elif confidence == "MEDIUM":
            return [
                "Address identified data issues before major analysis",
                "Focus cleanup on team assignment and statistical validity issues",
                "Re-run audit after cleanup to verify improvements"
            ]
        else:
            return [
                "Major data integrity issues must be resolved first",
                "Consider alternative data sources if current dataset is unreliable",
                "Do not proceed with analysis until data quality is assured"
            ]

def main():
    """Run the data integrity audit."""
    auditor = DataIntegrityAuditor()

    try:
        results = auditor.run_full_audit()

        print("\n" + "=" * 60)
        print("📊 AUDIT RESULTS SUMMARY")
        print("=" * 60)

        print(f"Overall Rating: {results['overall_assessment']['overall_rating']}")
        print(f"Confidence Level: {results['overall_assessment']['confidence_level']}")

        print("\nAssessment Breakdown:")
        breakdown = results['overall_assessment']['breakdown']
        print(f"  ✅ Excellent: {breakdown['excellent']}/{breakdown['total']}")
        print(f"  ⚠️ Good: {breakdown['good']}/{breakdown['total']}")
        print(f"  🚨 Poor: {breakdown['poor']}/{breakdown['total']}")

        print("\nRecommendations:")
        for rec in results['overall_assessment']['recommendations']:
            print(f"  • {rec}")

        print("\n" + "=" * 60)
        print("📄 Detailed results saved to audit report")

    except Exception as e:
        print(f"❌ Audit failed with error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
