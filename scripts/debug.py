#!/usr/bin/env python3
"""
NBA Playoff Resilience Engine - Debug and Diagnostic Script
Comprehensive debugging tools for troubleshooting issues.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import argparse
import json
import pandas as pd

# Package is now installed via setup.py, so imports should work directly

try:
    from src.utils.logging import setup_logger
except ImportError:
    # Fallback if package not installed
    import logging
    def setup_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        return logger

logger = setup_logger(__name__)


def run_system_diagnostic() -> Dict[str, Any]:
    """Run comprehensive system diagnostic."""
    logger.info("Running system diagnostic...")

    # Import pandas for timestamp
    import pandas as pd

    diagnostic = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "system_info": {},
        "data_status": {},
        "model_status": {},
        "environment": {},
        "issues": []
    }

    # System info
    diagnostic["system_info"] = {
        "python_version": sys.version,
        "platform": sys.platform,
        "working_directory": os.getcwd()
    }

    # Environment check
    diagnostic["environment"] = {
        "has_venv": sys.prefix != sys.base_prefix,
        "venv_path": sys.prefix if sys.prefix != sys.base_prefix else None,
        "python_path": sys.path[:3]  # First 3 entries
    }

    # Data status
    data_paths = {
        "predictive_dataset": "data/processed/predictive_dataset.csv",
        "raw_nba_api": "data/raw/nba_api/",
        "shot_charts": "data/raw/shot_charts/",
        "results_dir": "results/",
        "models_dir": "models/"
    }

    for name, path in data_paths.items():
        full_path = Path(path)
        diagnostic["data_status"][name] = {
            "exists": full_path.exists(),
            "is_file": full_path.is_file() if full_path.exists() else False,
            "size": full_path.stat().st_size if full_path.exists() else 0
        }

        # Check if data files have content
        if full_path.is_file():
            try:
                if name == "predictive_dataset":
                    df = pd.read_csv(full_path)
                    diagnostic["data_status"][name]["rows"] = len(df)
                    diagnostic["data_status"][name]["columns"] = len(df.columns)
                elif full_path.is_dir():
                    files = list(full_path.glob("*"))
                    diagnostic["data_status"][name]["file_count"] = len(files)
            except Exception as e:
                diagnostic["data_status"][name]["error"] = str(e)

    # Model status
    model_paths = [
        "models/production/resilience_xgb_rfe_10.pkl",
        "models/production/archetype_encoder_rfe_10.pkl",
        "models/resilience_xgb_rfe_10.pkl",  # Legacy location
        "models/archetype_encoder_rfe_10.pkl"
    ]

    diagnostic["model_status"] = {}
    for model_path in model_paths:
        path = Path(model_path)
        diagnostic["model_status"][model_path] = {
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else 0
        }

    # Check for common issues
    issues = []

    # Data issues
    if not Path("data/processed/predictive_dataset.csv").exists():
        issues.append("No predictive dataset found - run data collection first")

    # Model issues
    has_production_model = any(
        Path(p).exists() for p in [
            "models/production/resilience_xgb_rfe_10.pkl",
            "models/resilience_xgb_rfe_10.pkl"
        ]
    )
    if not has_production_model:
        issues.append("No trained model found - run model training first")

    # Environment issues
    if sys.prefix == sys.base_prefix:
        issues.append("Not running in virtual environment - consider using venv")

    # Import issues
    try:
        import pandas as pd
        import numpy as np
        import xgboost as xgb
        import sklearn
        diagnostic["imports"] = {
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "xgboost": xgb.__version__,
            "sklearn": sklearn.__version__
        }
    except ImportError as e:
        issues.append(f"Missing dependency: {e}")
        diagnostic["imports"] = {"error": str(e)}

    diagnostic["issues"] = issues
    diagnostic["status"] = "healthy" if len(issues) == 0 else "issues_found"

    return diagnostic


def analyze_player_prediction(
    player_name: str,
    season: str,
    usage_level: Optional[float] = None,
    detailed: bool = False
) -> Dict[str, Any]:
    """Analyze prediction for a specific player."""
    logger.info(f"Analyzing prediction for {player_name} ({season})")

    analysis = {
        "player_name": player_name,
        "season": season,
        "usage_level": usage_level,
        "data_found": False,
        "prediction_success": False,
        "issues": []
    }

    try:
        # Get player data
        from src.data.client import get_player_data
        player_data = get_player_data(player_name, season)

        if not player_data:
            analysis["issues"].append("Player data not found")
            return analysis

        analysis["data_found"] = True
        analysis["data_completeness"] = len(player_data)

        # Basic data validation
        required_fields = ['usg_pct', 'efg_pct', 'ts_pct']
        missing_fields = [f for f in required_fields if f not in player_data or pd.isna(player_data[f])]

        if missing_fields:
            analysis["issues"].append(f"Missing required fields: {missing_fields}")

        # Make prediction
        from src.model.predictor import predict_with_risk_matrix
        prediction = predict_with_risk_matrix(player_data, usage_level)

        analysis["prediction_success"] = True
        analysis["prediction"] = prediction

        if detailed:
            # Add feature analysis
            analysis["feature_analysis"] = analyze_prediction_features(player_data, prediction)

            # Add similar players
            analysis["similar_players"] = find_similar_players(player_data, season)

    except Exception as e:
        analysis["issues"].append(f"Analysis failed: {str(e)}")
        logger.error(f"Player analysis failed: {e}")

    return analysis


def analyze_prediction_features(player_data: dict, prediction: dict) -> Dict[str, Any]:
    """Analyze which features drove the prediction."""
    analysis = {}

    try:
        # Load model to get feature importance
        import joblib
        model_path = "models/production/resilience_xgb_rfe_10.pkl"
        if not Path(model_path).exists():
            model_path = "models/resilience_xgb_rfe_10.pkl"

        if Path(model_path).exists():
            model = joblib.load(model_path)

            # Get feature importance
            if hasattr(model, 'feature_importances_'):
                # Load feature names (this would need to be stored during training)
                analysis["feature_importance"] = {
                    f"feature_{i}": imp for i, imp in enumerate(model.feature_importances_)
                }

        # Analyze key stress vectors
        stress_vectors = {
            "creation_tax": player_data.get("creation_tax"),
            "leverage_usg_delta": player_data.get("leverage_usg_delta"),
            "leverage_ts_delta": player_data.get("leverage_ts_delta"),
            "rim_pressure_resilience": player_data.get("rim_pressure_resilience"),
            "pressure_resilience": player_data.get("pressure_resilience")
        }

        analysis["stress_vectors"] = stress_vectors

        # Flag concerning values
        concerning_flags = []
        if stress_vectors.get("creation_tax", 0) > 0.2:
            concerning_flags.append("High creation tax (inefficient creator)")
        if stress_vectors.get("leverage_usg_delta", 0) < -0.05:
            concerning_flags.append("Negative leverage USG delta (abdication)")
        if stress_vectors.get("rim_pressure_resilience", 1) < 0.8:
            concerning_flags.append("Low rim pressure resilience")

        analysis["concerning_flags"] = concerning_flags

    except Exception as e:
        analysis["error"] = str(e)

    return analysis


def find_similar_players(player_data: dict, season: str, n_similar: int = 3) -> List[Dict[str, Any]]:
    """Find players with similar profiles."""
    similar = []

    try:
        # Load dataset
        dataset_path = "data/processed/predictive_dataset.csv"
        if not Path(dataset_path).exists():
            return similar

        df = pd.read_csv(dataset_path)

        # Filter to same season and similar usage
        usage = player_data.get("usg_pct", 0)
        season_data = df[df["season"] == season]
        similar_usage = season_data[
            (season_data["usg_pct"] >= usage * 0.8) &
            (season_data["usg_pct"] <= usage * 1.2)
        ]

        # Sort by similarity (simple euclidean distance on key stats)
        key_stats = ["efg_pct", "ts_pct", "usg_pct"]
        player_stats = [player_data.get(stat, 0) for stat in key_stats]

        def similarity_score(row):
            row_stats = [row[stat] for stat in key_stats]
            return sum((a - b) ** 2 for a, b in zip(player_stats, row_stats)) ** 0.5

        similar_usage = similar_usage.copy()
        similar_usage["similarity"] = similar_usage.apply(similarity_score, axis=1)
        similar_usage = similar_usage.sort_values("similarity").head(n_similar)

        for _, row in similar_usage.iterrows():
            similar.append({
                "player_name": row["player_name"],
                "similarity_score": row["similarity"],
                "usg_pct": row["usg_pct"],
                "efg_pct": row["efg_pct"]
            })

    except Exception as e:
        logger.warning(f"Similar players analysis failed: {e}")

    return similar


def analyze_model_performance() -> Dict[str, Any]:
    """Analyze current model performance."""
    analysis = {}

    try:
        # Load test results
        results_dir = Path("results")
        latest_results = None
        latest_time = None

        for results_file in results_dir.glob("**/validation_results.json"):
            mtime = results_file.stat().st_mtime
            if latest_time is None or mtime > latest_time:
                latest_time = mtime
                latest_results = results_file

        if latest_results:
            with open(latest_results) as f:
                analysis["validation_results"] = json.load(f)

        # Load experiment results
        exp_dir = results_dir / "experiments"
        if exp_dir.exists():
            experiments = []
            for exp_dir in exp_dir.glob("*"):
                if exp_dir.is_dir():
                    summary_file = exp_dir / "experiment_summary.json"
                    if summary_file.exists():
                        with open(summary_file) as f:
                            exp_data = json.load(f)
                            experiments.append(exp_data)

            analysis["recent_experiments"] = experiments[-5:]  # Last 5 experiments

    except Exception as e:
        analysis["error"] = str(e)

    return analysis


def analyze_data_completeness() -> Dict[str, Any]:
    """Analyze data completeness and quality."""
    analysis = {}

    try:
        from src.utils.validation import validate_data_completeness
        analysis = validate_data_completeness()

    except Exception as e:
        analysis["error"] = str(e)

    return analysis


def main():
    parser = argparse.ArgumentParser(
        description="NBA Playoff Resilience Engine - Debug & Diagnostics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # System diagnostic
  python scripts/debug.py --diagnostic

  # Analyze specific player
  python scripts/debug.py --player "Luka Dončić" --season "2023-24"

  # Detailed player analysis
  python scripts/debug.py --player "Jordan Poole" --season "2021-22" --detailed

  # Model performance analysis
  python scripts/debug.py --model-analysis

  # Data completeness check
  python scripts/debug.py --data-completeness

  # Find similar players
  python scripts/debug.py --player "Jalen Brunson" --season "2022-23" --similar
        """
    )

    # Analysis types
    parser.add_argument(
        "--diagnostic",
        action="store_true",
        help="Run full system diagnostic"
    )

    parser.add_argument(
        "--player",
        help="Player name for analysis"
    )

    parser.add_argument(
        "--season",
        help="Season for player analysis (required with --player)"
    )

    parser.add_argument(
        "--usage",
        type=float,
        help="Usage level for prediction analysis"
    )

    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed analysis"
    )

    parser.add_argument(
        "--model-analysis",
        action="store_true",
        help="Analyze model performance"
    )

    parser.add_argument(
        "--data-completeness",
        action="store_true",
        help="Analyze data completeness"
    )

    parser.add_argument(
        "--similar",
        action="store_true",
        help="Find similar players (requires --player and --season)"
    )

    parser.add_argument(
        "--output",
        help="Output file for results (JSON format)"
    )

    args = parser.parse_args()

    try:
        results = {}

        # Run diagnostic
        if args.diagnostic:
            results["system_diagnostic"] = run_system_diagnostic()

        # Player analysis
        if args.player and args.season:
            results["player_analysis"] = analyze_player_prediction(
                args.player, args.season, args.usage, args.detailed
            )

        # Model analysis
        if args.model_analysis:
            results["model_analysis"] = analyze_model_performance()

        # Data completeness
        if args.data_completeness:
            results["data_completeness"] = analyze_data_completeness()

        # Output results
        if results:
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                print(f"Results saved to: {args.output}")
            else:
                # Pretty print to console
                print(json.dumps(results, indent=2, default=str))
        else:
            parser.print_help()

    except Exception as e:
        logger.error(f"Debug command failed: {e}")
        if args.detailed:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
