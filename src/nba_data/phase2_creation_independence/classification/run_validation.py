"""
Validation script for the Creation Independence Index (CII).

This script runs the batch CII calculation on the full feature dataset
and performs validation checks against key players and archetypes.
"""
import pandas as pd
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure the script can find the src module
import sys
sys.path.append(str(Path(__file__).resolve().parents[4]))

from src.nba_data.phase2_creation_independence.index.composite import batch_calculate_cii, validate_cii

def main():
    """Main validation function."""
    
    # Define paths
    project_root = Path(__file__).resolve().parents[4]
    feature_dataset_path = project_root / 'results' / 'predictive_dataset_with_friction.csv'
    output_path = project_root / 'results' / 'cii_results.csv'
    
    logging.info(f"Loading feature dataset from: {feature_dataset_path}")
    if not feature_dataset_path.exists():
        logging.error(f"Feature dataset not found at {feature_dataset_path}")
        logging.error("Please run the feature engineering pipeline first (e.g., evaluate_plasticity_potential.py)")
        return

    df = pd.read_csv(feature_dataset_path)
    logging.info(f"Loaded {len(df)} player-seasons.")
    
    # Run batch CII calculation
    cii_results = batch_calculate_cii(df)
    
    if cii_results.empty:
        logging.error("CII calculation returned an empty DataFrame. Aborting.")
        return
        
    logging.info(f"Saving CII results to: {output_path}")
    cii_results.to_csv(output_path, index=False)
    
    # --- Validation Checks ---
    logging.info("\n--- KERNEL OF TRUTH VALIDATION ---")
    
    # 1. Simmons vs. Harden Ordering
    logging.info("\n1. Verifying Simmons < Harden ordering (Peak Seasons)...")
    try:
        simmons_peak = cii_results[
            (cii_results['player_name'].str.contains("Ben Simmons", case=False)) &
            (cii_results['season'] == '2018-19')
        ].iloc[0]
        
        harden_peak = cii_results[
            (cii_results['player_name'].str.contains("James Harden", case=False)) &
            (cii_results['season'] == '2018-19')
        ].iloc[0]
        
        simmons_score = simmons_peak['cii']
        harden_score = harden_peak['cii']
        
        if simmons_score < harden_score:
            logging.info(f"  ✅ PASS: Simmons ({simmons_score}) < Harden ({harden_score})")
        else:
            logging.error(f"  ❌ FAIL: Simmons ({simmons_score}) >= Harden ({harden_score})")
            
        logging.info("\nSimmons 2018-19 Breakdown:")
        logging.info(simmons_peak)
        logging.info("\nHarden 2018-19 Breakdown:")
        logging.info(harden_peak)

    except IndexError:
        logging.warning("  ⚠️ SKIP: Could not find peak Simmons or Harden season in the dataset.")
        
    # 2. Haliburton vs. Sabonis Ordering
    logging.info("\n2. Verifying Haliburton > Sabonis ordering (Trade Season)...")
    try:
        hali_2022 = cii_results[
            (cii_results['player_name'].str.contains("Tyrese Haliburton", case=False)) &
            (cii_results['season'] == '2021-22')
        ].iloc[0]
        
        sabonis_2022 = cii_results[
            (cii_results['player_name'].str.contains("Domantas Sabonis", case=False)) &
            (cii_results['season'] == '2021-22')
        ].iloc[0]
        
        hali_score = hali_2022['cii']
        sabonis_score = sabonis_2022['cii']
        
        if hali_score > sabonis_score:
            logging.info(f"  ✅ PASS: Haliburton ({hali_score}) > Sabonis ({sabonis_score})")
        else:
            logging.error(f"  ❌ FAIL: Haliburton ({hali_score}) <= Sabonis ({sabonis_score})")
            
    except IndexError:
        logging.warning("  ⚠️ SKIP: Could not find Haliburton or Sabonis 2021-22 season.")
        
    # 3. Run all critical validation cases from composite.py
    logging.info("\n3. Running all critical validation cases...")
    validation_results = validate_cii(df)
    for player, result in validation_results.items():
        if result['status'] == 'PASS':
            logging.info(f"  ✅ PASS: {player} -> {result['archetype']} ({result['cii']})")
        elif result['status'] == 'FAIL':
            logging.error(f"  ❌ FAIL: {player} -> {result['archetype']} ({result['cii']}). Expected: {result['expected']}")
        else:
            logging.warning(f"  ⚠️ SKIP: {player} -> {result['reason']}")

    logging.info("\nValidation complete. Check logs for details.")

if __name__ == "__main__":
    main()

