import pandas as pd
import numpy as np
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[3]))

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CrucibleTestEngine:
    def __init__(self):
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.tests_dir = Path("tests/validation")
        
        self.test_cases_path = self.results_dir / "latent_star_test_cases_results.csv"
        self.predictions_path = self.results_dir / "physics_adjusted_impact.csv"
        self.player_id_map_path = self.results_dir / "predictive_dataset.csv"  # To get PLAYER_ID

    def define_success_criteria(self, row):
        """
        Defines pass/fail criteria for each test case based on predicted impact.
        """
        category = row.get('category', '')
        predicted_impact = row.get('PREDICTED_PLAYOFF_IMPACT', 0)
        
        # Star Impact Thresholds
        STAR_IMPACT_THRESHOLD = 0.14
        ROLE_PLAYER_THRESHOLD = 0.12
        GHOST_THRESHOLD = 0.13

        if 'True Positive' in category:
            # Expected to be a star. Pass if prediction is high.
            return predicted_impact >= STAR_IMPACT_THRESHOLD
            
        elif 'False Positive' in category:
            # Expected to be a "Ghost". Pass if prediction is low.
            return predicted_impact < GHOST_THRESHOLD
            
        elif 'True Negative' in category:
            # Expected to be a non-star. Pass if prediction is low.
            return predicted_impact < ROLE_PLAYER_THRESHOLD
            
        return False

    def run_tests(self, output_path="results/crucible_model_test_report.csv"):
        """
        Runs the test suite for the Crucible model.
        """
        if not self.test_cases_path.exists():
            logger.error(f"Missing test cases file: {self.test_cases_path}")
            return
            
        if not self.predictions_path.exists():
            logger.error(f"Missing predictions file: {self.predictions_path}")
            return
            
        if not self.player_id_map_path.exists():
            logger.error(f"Missing player ID map file: {self.player_id_map_path}")
            return

        test_cases_df = pd.read_csv(self.test_cases_path)
        predictions_df = pd.read_csv(self.predictions_path)
        player_id_df = pd.read_csv(self.player_id_map_path)[['PLAYER_NAME', 'PLAYER_ID', 'SEASON']].drop_duplicates()
        
        # Rename for consistency
        test_cases_df = test_cases_df.rename(columns={'player_name': 'PLAYER_NAME', 'season': 'SEASON'})
        
        # Get PLAYER_ID for test cases
        test_cases_with_id = pd.merge(
            test_cases_df,
            player_id_df,
            on=['PLAYER_NAME', 'SEASON'],
            how='left'
        )
        
        # Merge test cases with predictions
        merged_df = pd.merge(
            test_cases_with_id,
            predictions_df[['PLAYER_ID', 'SEASON', 'PREDICTED_PLAYOFF_IMPACT', 'USG_PCT']],
            on=['PLAYER_ID', 'SEASON'],
            how='left'
        )
        
        # Apply success criteria
        merged_df['TEST_PASSED'] = merged_df.apply(self.define_success_criteria, axis=1)
        
        # Calculate pass rate
        pass_rate = merged_df['TEST_PASSED'].mean()
        logger.info(f"Overall Test Suite Pass Rate: {pass_rate:.2%}")
        
        # Breakdown by case type
        pass_rate_by_type = merged_df.groupby('category')['TEST_PASSED'].mean()
        logger.info(f"Pass Rate by Case Type:\n{pass_rate_by_type}")
        
        # Save detailed report
        merged_df.to_csv(output_path, index=False)
        logger.info(f"✅ Saved test report to {output_path}")

        return merged_df

if __name__ == "__main__":
    tester = CrucibleTestEngine()
    tester.run_tests()

