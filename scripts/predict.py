#!/usr/bin/env python3
"""
NBA Playoff Resilience Engine - Prediction Script
Make archetype predictions for players using the trained model.
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import argparse
import json

# Package is installed via setup.py, so imports should work directly
try:
    from src.model.predictor import predict_archetype, predict_with_risk_matrix
    from src.data.client import get_player_data
    from src.utils.logging import setup_logger
except ImportError:
    # Fallback if package not installed
    import logging
    def setup_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        return logger
    # Mock functions for fallback
    def predict_archetype(*args, **kwargs):
        raise ImportError("Package not properly installed. Run: pip install -e .")
    def predict_with_risk_matrix(*args, **kwargs):
        raise ImportError("Package not properly installed. Run: pip install -e .")
    def get_player_data(*args, **kwargs):
        raise ImportError("Package not properly installed. Run: pip install -e .")

logger = setup_logger(__name__)


def format_prediction(result: Dict[str, Any], detailed: bool = False) -> str:
    """Format prediction result for display."""
    output = []

    if 'risk_category' in result:
        # 2D Risk Matrix result
        output.append(f"🎯 Risk Category: {result['risk_category']}")
        output.append(f"📈 Performance Score: {result['performance_score']:.1f}/100")
        output.append(f"🔗 Dependence Score: {result['dependence_score']:.1f}/100")
        output.append(f"🎪 Confidence: {result['confidence']:.1f}/100")

        if detailed and 'reasoning' in result:
            output.append("\n📋 Reasoning:")
            for key, value in result['reasoning'].items():
                output.append(f"   {key}: {value}")
    else:
        # 1D Archetype result
        output.append(f"🎯 Archetype: {result['archetype']}")
        output.append(f"🎪 Confidence: {result['confidence']:.1%}")

        if detailed:
            output.append(f"🔗 Dependence Score: {result.get('dependence_score', 'N/A')}")

            if 'features' in result:
                output.append("\n📊 Key Features:")
                # Show top 5 features by importance (would need model metadata)
                features = result['features']
                for key, value in list(features.items())[:5]:
                    output.append(f"   {key}: {value:.3f}")

    return "\n".join(output)


def predict_single_player(
    player_name: str,
    season: str,
    usage_level: Optional[float] = None,
    use_2d: bool = True,
    detailed: bool = False
) -> Dict[str, Any]:
    """Predict for a single player."""
    logger.info(f"Predicting for {player_name} ({season})")

    try:
        # Get player data
        player_data = get_player_data(player_name, season)
        if not player_data:
            raise ValueError(f"Player '{player_name}' not found for season {season}")

        logger.info(f"Found player data: {len(player_data)} features")

        # Make prediction
        if use_2d:
            result = predict_with_risk_matrix(player_data, usage_level)
        else:
            result = predict_archetype(player_data, usage_level)

        # Add metadata
        result['player_name'] = player_name
        result['season'] = season
        result['usage_level'] = usage_level

        return result

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise


def predict_batch(
    input_file: str,
    output_file: str,
    usage_level: Optional[float] = None,
    use_2d: bool = True
) -> None:
    """Predict for multiple players from CSV."""
    import pandas as pd

    logger.info(f"Batch prediction: {input_file} -> {output_file}")

    # Read input
    df = pd.read_csv(input_file)
    required_cols = ['player_name', 'season']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Input CSV must have columns: {required_cols}")

    results = []

    # Process each player
    for _, row in df.iterrows():
        player_name = row['player_name']
        season = row['season']

        try:
            result = predict_single_player(
                player_name=player_name,
                season=season,
                usage_level=usage_level,
                use_2d=use_2d,
                detailed=False
            )
            results.append(result)

        except Exception as e:
            logger.warning(f"Failed to predict for {player_name} ({season}): {e}")
            results.append({
                'player_name': player_name,
                'season': season,
                'error': str(e)
            })

    # Save results
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_file, index=False)

    logger.info(f"Batch prediction complete: {len(results)} predictions saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="NBA Playoff Resilience Engine - Make Predictions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single player prediction
  python scripts/predict.py --player "Luka Dončić" --season "2023-24"

  # Predict at specific usage level
  python scripts/predict.py --player "Jalen Brunson" --season "2022-23" --usage 0.30

  # Batch prediction from CSV
  python scripts/predict.py --input players.csv --output predictions.csv

  # Detailed output with feature breakdown
  python scripts/predict.py --player "Jordan Poole" --season "2021-22" --detailed

  # Use 1D archetype prediction instead of 2D risk matrix
  python scripts/predict.py --player "Nikola Jokić" --season "2023-24" --1d
        """
    )

    # Player selection
    player_group = parser.add_mutually_exclusive_group(required=True)
    player_group.add_argument(
        '--player',
        help='Player name (e.g., "Luka Dončić")'
    )
    player_group.add_argument(
        '--input',
        help='Input CSV file with player_name and season columns'
    )

    # Prediction options
    parser.add_argument(
        '--season',
        required='--player' in sys.argv,
        help='Season (e.g., "2023-24")'
    )
    parser.add_argument(
        '--usage',
        type=float,
        help='Usage level to predict at (0.0-1.0, e.g., 0.25 for 25%% usage)'
    )
    parser.add_argument(
        '--1d',
        action='store_true',
        help='Use 1D archetype prediction instead of 2D risk matrix'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed output with feature breakdown'
    )

    # Output options
    parser.add_argument(
        '--output',
        help='Output file for batch predictions (CSV format)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format (for single predictions)'
    )

    args = parser.parse_args()

    try:
        # Single player prediction
        if args.player:
            result = predict_single_player(
                player_name=args.player,
                season=args.season,
                usage_level=args.usage,
                use_2d=not args.d1,
                detailed=args.detailed
            )

            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                print(f"\n🏀 {args.player} ({args.season})")
                print("=" * 50)
                print(format_prediction(result, args.detailed))

        # Batch prediction
        elif args.input:
            if not args.output:
                parser.error("--output is required for batch predictions")

            predict_batch(
                input_file=args.input,
                output_file=args.output,
                usage_level=args.usage,
                use_2d=not args.d1
            )

            print(f"\n✅ Batch prediction complete!")
            print(f"📄 Results saved to: {args.output}")

    except Exception as e:
        logger.error(f"Command failed: {e}")
        if args.detailed:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
