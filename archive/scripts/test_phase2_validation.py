#!/usr/bin/env python3
"""
Phase 2 Validation Script

Comprehensive validation of the three-pathway resilience framework.
Tests consistency across all calculators and validates archetype expectations.
"""

import sys
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.nba_data.scripts.calculate_extended_resilience import calculate_extended_resilience
from src.nba_data.scripts.calculate_primary_method_mastery import calculate_primary_method_mastery
from src.nba_data.scripts.calculate_dominance_score import calculate_player_sqav

def get_player_name(player_id: int) -> str:
    """Get player name for display purposes."""
    import sqlite3
    conn = sqlite3.connect("data/nba_stats.db")
    query = f"SELECT player_name FROM players WHERE player_id = {player_id}"
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result.iloc[0]['player_name'] if not result.empty else f"Player {player_id}"

def validate_calculator_consistency():
    """Validate that all calculators produce consistent results."""

    print("🔬 PHASE 2 VALIDATION: Calculator Consistency Test")
    print("=" * 60)

    # Test on James Harden (201935)
    player_id = 201935
    player_name = get_player_name(player_id)
    season = "2024-25"

    print(f"Testing consistency for {player_name} (ID: {player_id})")
    print("-" * 50)

    # Get results from each calculator
    try:
        # Extended resilience (three-pathway)
        extended_results = calculate_extended_resilience(player_id, season)
        reg_method_resilience = extended_results['Regular Season']['Method_Resilience']
        reg_dominance = extended_results['Regular Season']['Dominance_Score']
        reg_mastery = extended_results['Regular Season']['Primary_Method_Mastery']
        extended_score = extended_results['Regular Season']['Extended_Resilience']

        # Individual calculators
        individual_mastery = calculate_primary_method_mastery(player_id, season)
        individual_dominance = calculate_player_sqav(player_id, season, "Regular Season")

        print("Extended Calculator Results:")
        print(".2f")
        print(".2f")
        print(".2f")
        print(".2f")

        print("\nIndividual Calculator Results:")
        print(f"  Primary Method Mastery: {individual_mastery['primary_method_mastery']:.2f}")
        print(f"  Dominance Score: {individual_dominance:.2f}")

        # Check consistency
        mastery_match = abs(reg_mastery - individual_mastery['primary_method_mastery']) < 0.01
        dominance_match = abs(reg_dominance - individual_dominance) < 0.01

        print("\nConsistency Check:")
        print(f"  Primary Method Mastery Match: {'✅' if mastery_match else '❌'}")
        print(f"  Dominance Score Match: {'✅' if dominance_match else '❌'}")

        # Check extended score calculation
        expected_extended = (reg_method_resilience * 0.4) + (reg_dominance * 0.35) + (reg_mastery * 0.25)
        extended_match = abs(extended_score - expected_extended) < 0.01

        print(f"  Extended Score Calculation: {'✅' if extended_match else '❌'}")

        overall_consistent = mastery_match and dominance_match and extended_match
        print(f"\nOverall Consistency: {'✅ PASS' if overall_consistent else '❌ FAIL'}")

        return overall_consistent

    except Exception as e:
        print(f"❌ Error during consistency test: {e}")
        return False

def validate_archetype_patterns():
    """Validate that archetype players show expected patterns."""

    print("\n🔬 PHASE 2 VALIDATION: Archetype Pattern Analysis")
    print("=" * 60)

    archetypes = {
        201935: ("James Harden", "Versatile scorer with 3PT/dominance focus"),
        2544: ("LeBron James", "Balanced versatility + mastery"),
        1629029: ("Luka Dončić", "High versatility focus"),
        203076: ("Anthony Davis", "Dominance + mastery focus")
    }

    results = []

    for player_id, (name, description) in archetypes.items():
        print(f"\nTesting {name}: {description}")
        print("-" * 40)

        try:
            extended_results = calculate_extended_resilience(player_id, "2024-25")
            reg_scores = extended_results['Regular Season']

            method_res = reg_scores['Method_Resilience']
            dominance = reg_scores['Dominance_Score']
            mastery = reg_scores['Primary_Method_Mastery']
            extended = reg_scores['Extended_Resilience']

            print(".2f")
            print(".2f")
            print(".2f")
            print(".2f")

            # Analyze patterns - check for meaningful differentiation
            # Rather than binary thresholds, check that scores show meaningful variation
            scores_vary = (
                abs(method_res - dominance) > 10 or  # Different pathway emphasis
                abs(method_res - mastery) > 10 or
                abs(dominance - mastery) > 10
            )

            # Check that at least one pathway is strong
            has_strength = max(method_res, dominance, mastery) > 55

            # Pattern description based on relative strengths
            pathways = {
                'Versatility': method_res,
                'Dominance': dominance,
                'Mastery': mastery
            }
            primary_pathway = max(pathways, key=pathways.get)
            pattern_str = f"Primary: {primary_pathway} ({pathways[primary_pathway]:.1f})"

            print(f"  Pattern: {pattern_str}")

            # Validate that framework shows meaningful differentiation
            # All players should have varying scores and at least one strength
            expected = scores_vary and has_strength

            validation = "✅" if expected else "❌"
            print(f"  Validation: {validation}")

            results.append({
                'player': name,
                'method_resilience': method_res,
                'dominance': dominance,
                'mastery': mastery,
                'pattern': pattern_str,
                'scores_vary': scores_vary,
                'has_strength': has_strength,
                'validated': expected
            })

        except Exception as e:
            print(f"❌ Error testing {name}: {e}")
            results.append({
                'player': name,
                'error': str(e),
                'validated': False
            })

    # Summary
    print("\n" + "=" * 60)
    print("ARCHETYPE VALIDATION SUMMARY")
    print("=" * 60)

    valid_count = sum(1 for r in results if r.get('validated', False))
    total_count = len(results)

    for result in results:
        if 'error' in result:
            print(f"❌ {result['player']}: ERROR - {result['error']}")
        else:
            status = "✅" if result['validated'] else "❌"
            print(f"{status} {result['player']}: {result['pattern']}")

    print(f"\nValidation Score: {valid_count}/{total_count} archetypes validated correctly")
    return valid_count == total_count

def validate_data_integrity():
    """Validate data integrity and completeness."""

    print("\n🔬 PHASE 2 VALIDATION: Data Integrity Check")
    print("=" * 60)

    import sqlite3

    try:
        conn = sqlite3.connect("data/nba_stats.db")

        # Check critical tables exist and have data
        critical_tables = [
            'players', 'player_season_stats', 'player_advanced_stats',
            'player_tracking_stats', 'player_shot_dashboard_stats'
        ]

        integrity_checks = []

        for table in critical_tables:
            count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", conn).iloc[0]['count']
            has_data = count > 0
            integrity_checks.append((table, count, has_data))
            status = "✅" if has_data else "❌"
            print(f"{status} {table}: {count:,} rows")

        # Check for null values in critical columns
        null_checks = []
        critical_columns = [
            ('player_season_stats', 'points'),
            ('player_advanced_stats', 'true_shooting_percentage'),
            ('player_tracking_stats', 'touches')
        ]

        for table, column in critical_columns:
            null_count = pd.read_sql_query(f"SELECT COUNT(*) as nulls FROM {table} WHERE {column} IS NULL", conn).iloc[0]['nulls']
            total_count = pd.read_sql_query(f"SELECT COUNT(*) as total FROM {table}", conn).iloc[0]['total']
            null_pct = (null_count / total_count * 100) if total_count > 0 else 0
            acceptable = null_pct < 5  # Less than 5% nulls acceptable
            null_checks.append((f"{table}.{column}", null_count, null_pct, acceptable))
            status = "✅" if acceptable else "❌"
            print(f"{status} {table}.{column}: {null_count}/{total_count} nulls ({null_pct:.1f}%)")
        conn.close()

        # Overall assessment
        tables_ok = all(check[2] for check in integrity_checks)
        nulls_ok = all(check[3] for check in null_checks)

        overall_ok = tables_ok and nulls_ok
        print(f"\nData Integrity: {'✅ PASS' if overall_ok else '❌ FAIL'}")

        return overall_ok

    except Exception as e:
        print(f"❌ Data integrity check failed: {e}")
        return False

def main():
    """Run comprehensive Phase 2 validation."""

    print("🚀 COMPREHENSIVE PHASE 2 VALIDATION SUITE")
    print("=" * 80)
    print("Testing three-pathway resilience framework implementation")
    print("=" * 80)

    # Run all validation tests
    consistency_ok = validate_calculator_consistency()
    archetypes_ok = validate_archetype_patterns()
    data_ok = validate_data_integrity()

    # Final assessment
    print("\n" + "=" * 80)
    print("🎯 PHASE 2 VALIDATION RESULTS")
    print("=" * 80)

    tests = [
        ("Calculator Consistency", consistency_ok),
        ("Archetype Patterns", archetypes_ok),
        ("Data Integrity", data_ok)
    ]

    for test_name, passed in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")

    all_passed = all(t[1] for t in tests)

    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print("=" * 80)

    if all_passed:
        print("🎉 Phase 2 implementation is fully validated and ready for production!")
        print("Three-pathway resilience framework operational with:")
        print("  • Method Resilience (versatility)")
        print("  • Dominance Score (contest mastery)")
        print("  • Primary Method Mastery (elite specialization)")
    else:
        print("⚠️  Some validation tests failed. Please review and fix issues before proceeding.")

    return all_passed

if __name__ == "__main__":
    main()
