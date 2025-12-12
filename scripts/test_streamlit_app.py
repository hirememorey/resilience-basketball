#!/usr/bin/env python3
"""
Test script for the NBA Resilience Streamlit App

Validates that all components can be imported and basic functionality works.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        # Test projection utils
        from src.nba_data.utils.projection_utils import (
            calculate_empirical_usage_buckets,
            calculate_feature_percentiles,
            project_stress_vectors_for_usage
        )
        print("✅ Projection utils imported successfully")

        # Test data loaders
        from src.streamlit_app.utils.data_loaders import create_master_dataframe
        print("✅ Data loaders imported successfully")

        # Test visualization components
        from src.streamlit_app.components.risk_matrix_plot import create_risk_matrix_plot
        from src.streamlit_app.components.stress_vectors_radar import create_stress_vectors_radar
        print("✅ Visualization components imported successfully")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_data_availability():
    """Test that required data files exist."""
    print("Testing data availability...")

    required_files = [
        'results/predictive_dataset.csv',
        'results/resilience_archetypes.csv',
        'models/resilience_xgb_rfe_10.pkl',
        'models/archetype_encoder_rfe_10.pkl'
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\nTo generate missing data:")
        print("1. Run feature generation: python src/nba_data/scripts/evaluate_plasticity_potential.py")
        print("2. Run archetype calculation: python src/nba_data/scripts/calculate_simple_resilience.py")
        print("3. Train model: python src/nba_data/scripts/train_rfe_model.py")
        return False
    else:
        print("✅ All required data files found")
        return True


def test_basic_functionality():
    """Test basic functionality without full data loading."""
    print("Testing basic functionality...")

    try:
        # Test projection utils with dummy data
        import pandas as pd
        from src.nba_data.utils.projection_utils import calculate_empirical_usage_buckets

        # Create dummy dataframe
        dummy_df = pd.DataFrame({
            'USG_PCT': [0.15, 0.22, 0.28, 0.35],
            'CREATION_VOLUME_RATIO': [0.1, 0.3, 0.5, 0.7]
        })

        buckets = calculate_empirical_usage_buckets(dummy_df)
        assert '20-25%' in buckets
        assert '25-30%' in buckets
        print("✅ Projection utilities work correctly")

        return True

    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing NBA Resilience Streamlit App")
    print("=" * 50)

    tests = [
        ("Import Test", test_imports),
        ("Data Availability Test", test_data_availability),
        ("Basic Functionality Test", test_basic_functionality)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append(result)

    print("\n" + "=" * 50)
    print("📊 Test Results:")

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("\n🚀 Ready to run the app:")
        print("python scripts/run_streamlit_app.py")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\nPlease fix the failed tests before running the app.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
