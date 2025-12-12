#!/usr/bin/env python3
"""
Setup script for the NBA Resilience Streamlit App

Ensures all required data and dependencies are available before running the app.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def check_data_files():
    """Check if required data files exist."""
    required_files = [
        'results/predictive_dataset.csv',
        'results/resilience_archetypes.csv',
        'models/resilience_xgb_rfe_10.pkl',
        'models/archetype_encoder_rfe_10.pkl'
    ]

    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)

    return missing

def main():
    """Main setup function."""
    print("🚀 Setting up NBA Resilience Streamlit App")
    print("=" * 50)

    # Check if data files exist
    missing_files = check_data_files()
    if missing_files:
        print("📊 Missing data files. Generating required data...")

        # Generate predictive features
        if not run_command(
            "python src/nba_data/scripts/evaluate_plasticity_potential.py",
            "Generate predictive features"
        ):
            return False

        # Calculate archetypes
        if not run_command(
            "python src/nba_data/scripts/calculate_simple_resilience.py",
            "Calculate resilience archetypes"
        ):
            return False

        # Train model
        if not run_command(
            "python src/nba_data/scripts/train_rfe_model.py",
            "Train RFE model"
        ):
            return False

    else:
        print("✅ All required data files found")

    # Install app dependencies
    print("\n📦 Installing Streamlit app dependencies...")
    if not run_command(
        "pip install -r src/streamlit_app/requirements.txt",
        "Install app dependencies"
    ):
        return False

    # Run tests
    print("\n🧪 Running validation tests...")
    if not run_command(
        "python scripts/test_streamlit_app.py",
        "Run app validation tests"
    ):
        return False

    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("\n🚀 To run the app:")
    print("python scripts/run_streamlit_app.py")
    print("\n📖 For more options:")
    print("python scripts/run_streamlit_app.py --help")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
