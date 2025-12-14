#!/usr/bin/env python3
"""
NBA Playoff Resilience Engine - Validation Script
Run comprehensive validation tests and generate reports.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse
import json
from datetime import datetime

# Package is installed via setup.py, so imports should work directly
try:
    from src.utils.logging import setup_logger
    from src.model.evaluation import evaluate_model_performance
    import joblib
except ImportError:
    # Fallback if package not installed
    import logging
    def setup_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        return logger
    def evaluate_model_performance(*args, **kwargs):
        return {"error": "Package not properly installed. Run: pip install -e ."}
    # Mock joblib for fallback
    class joblib:
        @staticmethod
        def load(*args, **kwargs):
            raise ImportError("Package not properly installed. Run: pip install -e .")

logger = setup_logger(__name__)


def run_latent_star_test_cases() -> Dict[str, Any]:
    """Run the 32 critical latent star test cases."""
    logger.info("Running latent star test cases...")

    test_cases = [
        # Franchise Cornerstones (High Performance + Low Dependence)
        {"player": "Nikola Jokić", "season": "2023-24", "expected": "Franchise Cornerstone"},
        {"player": "Giannis Antetokounmpo", "season": "2022-23", "expected": "Franchise Cornerstone"},
        {"player": "Luka Dončić", "season": "2023-24", "expected": "Franchise Cornerstone"},

        # Luxury Components (High Performance + High Dependence)
        {"player": "Jordan Poole", "season": "2021-22", "expected": "Luxury Component"},
        {"player": "Domantas Sabonis", "season": "2021-22", "expected": "Luxury Component"},
        {"player": "Kevin Durant", "season": "2016-17", "expected": "Luxury Component"},

        # Bulldogs (High Performance + High Dependence, but different context)
        {"player": "LeBron James", "season": "2014-15", "expected": "Franchise Cornerstone"},
        {"player": "Russell Westbrook", "season": "2016-17", "expected": "Luxury Component"},

        # Sniper cases (Low Performance + Low Dependence)
        {"player": "Aaron Gordon", "season": "2022-23", "expected": "Depth Piece"},
        {"player": "Brook Lopez", "season": "2020-21", "expected": "Depth Piece"},

        # Victim cases (Low Performance + High Dependence)
        {"player": "Ben Simmons", "season": "2020-21", "expected": "Avoid"},
        {"player": "D'Angelo Russell", "season": "2018-19", "expected": "Avoid"},
        {"player": "Tony Wroten", "season": "2014-15", "expected": "Avoid"},

        # Edge cases and latent star detection
        {"player": "Jalen Brunson", "season": "2022-23", "expected": "Franchise Cornerstone"},
        {"player": "Tyrese Haliburton", "season": "2021-22", "expected": "Franchise Cornerstone"},
        {"player": "Victor Oladipo", "season": "2017-18", "expected": "Franchise Cornerstone"},
        {"player": "DeMar DeRozan", "season": "2015-16", "expected": "Depth Piece"},
        {"player": "Kyrie Irving", "season": "2015-16", "expected": "Franchise Cornerstone"},
        {"player": "Isaiah Thomas", "season": "2016-17", "expected": "Luxury Component"},
        {"player": "Jimmy Butler", "season": "2014-15", "expected": "Franchise Cornerstone"},
        {"player": "Klay Thompson", "season": "2018-19", "expected": "Luxury Component"},
        {"player": "Kevin Love", "season": "2016-17", "expected": "Depth Piece"},
        {"player": "Andre Iguodala", "season": "2014-15", "expected": "Depth Piece"},
        {"player": "Kyle Lowry", "season": "2015-16", "expected": "Luxury Component"},
        {"player": "Kawhi Leonard", "season": "2013-14", "expected": "Franchise Cornerstone"},
        {"player": "Pau Gasol", "season": "2015-16", "expected": "Depth Piece"},
        {"player": "Rajon Rondo", "season": "2013-14", "expected": "Depth Piece"},
        {"player": "Tony Parker", "season": "2013-14", "expected": "Depth Piece"},
        {"player": "Boris Diaw", "season": "2013-14", "expected": "Depth Piece"},
        {"player": "Danny Green", "season": "2013-14", "expected": "Depth Piece"},
        {"player": "Manu Ginóbili", "season": "2013-14", "expected": "Depth Piece"},
        {"player": "Tim Duncan", "season": "2014-15", "expected": "Franchise Cornerstone"},
        {"player": "Shaq", "season": "2001-02", "expected": "Franchise Cornerstone"},
        {"player": "Dirk Nowitzki", "season": "2010-11", "expected": "Franchise Cornerstone"},
    ]

    results = []
    passed = 0
    total = len(test_cases)

    for i, case in enumerate(test_cases, 1):
        logger.info(f"Testing {i}/{total}: {case['player']} ({case['season']})")

        try:
            from src.model.predictor import predict_with_risk_matrix
            from src.data.client import get_player_data

            # Get player data
            player_data = get_player_data(case['player'], case['season'])
            if not player_data:
                result = {
                    "player": case['player'],
                    "season": case['season'],
                    "expected": case['expected'],
                    "actual": "NO_DATA",
                    "passed": False,
                    "error": "Player data not found"
                }
            else:
                # Make prediction
                prediction = predict_with_risk_matrix(player_data)

                # Check if prediction matches expectation
                actual = prediction['risk_category']
                expected = case['expected']
                passed_case = actual == expected

                result = {
                    "player": case['player'],
                    "season": case['season'],
                    "expected": expected,
                    "actual": actual,
                    "passed": passed_case,
                    "performance_score": prediction.get('performance_score'),
                    "dependence_score": prediction.get('dependence_score'),
                    "confidence": prediction.get('confidence')
                }

                if passed_case:
                    passed += 1

            results.append(result)

        except Exception as e:
            logger.warning(f"Failed to test {case['player']} ({case['season']}): {e}")
            results.append({
                "player": case['player'],
                "season": case['season'],
                "expected": case['expected'],
                "actual": "ERROR",
                "passed": False,
                "error": str(e)
            })

    return {
        "test_name": "latent_star_test_cases",
        "total_cases": total,
        "passed_cases": passed,
        "pass_rate": passed / total if total > 0 else 0,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


def run_model_performance_validation() -> Dict[str, Any]:
    """Run model performance validation on held-out test set."""
    logger.info("Running model performance validation...")

    try:
        # Load model
        model_path = "models/production/resilience_xgb_rfe_10.pkl"
        encoder_path = "models/production/archetype_encoder_rfe_10.pkl"

        if not (Path(model_path).exists() and Path(encoder_path).exists()):
            # Try alternative model locations
            model_path = "models/resilience_xgb_rfe_10.pkl"
            encoder_path = "models/archetype_encoder_rfe_10.pkl"

        if not (Path(model_path).exists() and Path(encoder_path).exists()):
            raise FileNotFoundError("No trained model found in production/ or root models/")

        model = joblib.load(model_path)
        encoder = joblib.load(encoder_path)

        # Load test data
        from src.data.storage import prepare_training_data
        X_train, X_test, y_train, y_test, feature_names = prepare_training_data()

        # Evaluate
        results = evaluate_model_performance(model, encoder, X_test, y_test)

        return {
            "test_name": "model_performance",
            "accuracy": results.get("accuracy", 0),
            "f1_score": results.get("f1_score", 0),
            "precision": results.get("precision", 0),
            "recall": results.get("recall", 0),
            "test_samples": len(X_test),
            "model_path": model_path,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Model performance validation failed: {e}")
        return {
            "test_name": "model_performance",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def run_data_quality_validation() -> Dict[str, Any]:
    """Run data quality and completeness validation."""
    logger.info("Running data quality validation...")

    try:
        from src.utils.validation import validate_data_completeness

        results = validate_data_completeness()

        return {
            "test_name": "data_quality",
            "overall_completeness": results.get("overall_completeness", 0),
            "total_players": results.get("total_players", 0),
            "total_seasons": results.get("total_seasons", 0),
            "missing_data_breakdown": results.get("missing_data_breakdown", {}),
            "data_quality_score": results.get("data_quality_score", 0),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Data quality validation failed: {e}")
        return {
            "test_name": "data_quality",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def generate_validation_report(results: List[Dict[str, Any]], output_file: Optional[str] = None) -> str:
    """Generate a comprehensive validation report."""
    report = {
        "validation_report": {
            "timestamp": datetime.now().isoformat(),
            "tests_run": len(results),
            "summary": {}
        },
        "test_results": results
    }

    # Calculate summary
    latent_star_results = None
    model_perf_results = None
    data_quality_results = None

    for result in results:
        if result.get("test_name") == "latent_star_test_cases":
            latent_star_results = result
        elif result.get("test_name") == "model_performance":
            model_perf_results = result
        elif result.get("test_name") == "data_quality":
            data_quality_results = result

    # Overall assessment
    overall_score = 0
    issues = []

    if latent_star_results:
        ls_pass_rate = latent_star_results.get("pass_rate", 0)
        overall_score += ls_pass_rate * 0.5  # 50% weight
        if ls_pass_rate < 0.75:
            issues.append(f"Low latent star test pass rate: {ls_pass_rate:.1%}")

    if model_perf_results and "accuracy" in model_perf_results:
        accuracy = model_perf_results["accuracy"]
        overall_score += accuracy * 0.3  # 30% weight
        if accuracy < 0.45:
            issues.append(f"Low model accuracy: {accuracy:.1%}")

    if data_quality_results and "overall_completeness" in data_quality_results:
        completeness = data_quality_results["overall_completeness"]
        overall_score += completeness * 0.2  # 20% weight
        if completeness < 0.8:
            issues.append(f"Low data completeness: {completeness:.1%}")

    report["validation_report"]["summary"] = {
        "overall_score": overall_score,
        "issues": issues,
        "recommendations": []
    }

    # Generate recommendations
    if overall_score < 0.7:
        report["validation_report"]["summary"]["recommendations"].append(
            "Overall system health is concerning. Consider retraining model or collecting more data."
        )

    if latent_star_results and latent_star_results.get("pass_rate", 0) < 0.8:
        report["validation_report"]["summary"]["recommendations"].append(
            "Review failing latent star test cases for model improvements."
        )

    if model_perf_results and model_perf_results.get("accuracy", 1) < 0.5:
        report["validation_report"]["summary"]["recommendations"].append(
            "Model accuracy is low. Consider feature engineering or hyperparameter tuning."
        )

    # Save report
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return f"Report saved to: {output_path}"

    return json.dumps(report, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser(
        description="NBA Playoff Resilience Engine - Validation Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--tests",
        nargs="*",
        choices=["latent_star", "model_performance", "data_quality", "all"],
        default=["all"],
        help="Tests to run (default: all)"
    )

    parser.add_argument(
        "--output",
        help="Output file for detailed results (JSON format)"
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate human-readable report"
    )

    args = parser.parse_args()

    # Determine which tests to run
    if "all" in args.tests:
        tests_to_run = ["latent_star", "model_performance", "data_quality"]
    else:
        tests_to_run = args.tests

    logger.info(f"Running validation tests: {tests_to_run}")

    results = []

    # Run selected tests
    if "latent_star" in tests_to_run:
        results.append(run_latent_star_test_cases())

    if "model_performance" in tests_to_run:
        results.append(run_model_performance_validation())

    if "data_quality" in tests_to_run:
        results.append(run_data_quality_validation())

    # Generate output
    if args.output or args.report:
        report_json = generate_validation_report(results, args.output)

        if args.report:
            # Generate human-readable report
            report = json.loads(report_json)["validation_report"]

            print("\n" + "="*60)
            print("🏀 NBA PLAYOFF RESILIENCE ENGINE - VALIDATION REPORT")
            print("="*60)
            print(f"Timestamp: {report['timestamp']}")
            print(f"Tests Run: {report['tests_run']}")
            print()

            summary = report.get("summary", {})
            overall_score = summary.get("overall_score", 0)

            print(f"🎯 Overall Score: {overall_score:.1%}")

            if overall_score >= 0.9:
                print("✅ EXCELLENT: System performing well")
            elif overall_score >= 0.75:
                print("✅ GOOD: System performing adequately")
            elif overall_score >= 0.6:
                print("⚠️  CONCERNING: System needs attention")
            else:
                print("❌ CRITICAL: System needs immediate fixes")

            # Test results summary
            for result in results:
                test_name = result.get("test_name", "unknown")
                if test_name == "latent_star_test_cases":
                    pass_rate = result.get("pass_rate", 0)
                    print(f"\n📊 Latent Star Tests: {pass_rate:.1%} ({result.get('passed_cases', 0)}/{result.get('total_cases', 0)})")
                elif test_name == "model_performance" and "accuracy" in result:
                    accuracy = result.get("accuracy", 0)
                    print(f"🤖 Model Accuracy: {accuracy:.1%}")
                elif test_name == "data_quality" and "overall_completeness" in result:
                    completeness = result.get("overall_completeness", 0)
                    print(f"📊 Data Completeness: {completeness:.1%}")

            # Issues and recommendations
            issues = summary.get("issues", [])
            if issues:
                print(f"\n⚠️  Issues Found ({len(issues)}):")
                for issue in issues:
                    print(f"   • {issue}")

            recommendations = summary.get("recommendations", [])
            if recommendations:
                print(f"\n💡 Recommendations ({len(recommendations)}):")
                for rec in recommendations:
                    print(f"   • {rec}")

            if args.output:
                print(f"\n📄 Detailed results saved to: {args.output}")

    else:
        # Just print summary
        print("\n🏀 Validation Results:")

        for result in results:
            test_name = result.get("test_name", "unknown")

            if test_name == "latent_star_test_cases":
                pass_rate = result.get("pass_rate", 0)
                print(f"📊 Latent Star Tests: {pass_rate:.1%} ({result.get('passed_cases', 0)}/{result.get('total_cases', 0)})")

            elif test_name == "model_performance" and "accuracy" in result:
                accuracy = result.get("accuracy", 0)
                print(f"🤖 Model Accuracy: {accuracy:.1%}")

            elif test_name == "data_quality" and "overall_completeness" in result:
                completeness = result.get("overall_completeness", 0)
                print(f"📊 Data Completeness: {completeness:.1%}")

            elif "error" in result:
                print(f"❌ {test_name}: Failed - {result['error']}")


if __name__ == "__main__":
    main()
