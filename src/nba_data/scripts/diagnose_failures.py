"""
Failure Autopsy Diagnostic Script

This script analyzes individual player failures to identify missing physics in the model.
For a given PLAYER_NAME and SEASON, it provides:
1. Feature profile comparison vs similar players
2. Prediction vs expectation analysis
3. Identification of features causing misclassification
4. Recommendations for new features

Usage: python diagnose_failures.py "Desmond Bane" "2021-22"
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
import joblib

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[3]))

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/failure_diagnosis.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FailureDiagnostician:
    def __init__(self):
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.models_dir = Path("models")

        # Load trained model and data
        self.load_model_and_data()

    def load_model_and_data(self):
        """Load the trained model, feature data, and test results."""
        logger.info("Loading model and data for diagnosis...")

        # Load model
        model_path = self.models_dir / "resilience_xgb_rfe_phoenix.pkl"
        if not model_path.exists():
            model_path = self.models_dir / "resilience_xgb_rfe_10.pkl"
            
        if model_path.exists():
            try:
                model_data = joblib.load(model_path)
                if isinstance(model_data, dict) and 'model' in model_data:
                    self.model = model_data['model']
                    logger.info(f"Loaded model bundle from {model_path}")
                else:
                    self.model = model_data
                    logger.info(f"Loaded legacy model object from {model_path}")
            except Exception as e:
                raise ValueError(f"Error loading model from {model_path}: {e}")
        else:
            raise FileNotFoundError(f"Model not found at {model_path}")

        # Load feature data
        feature_path = self.results_dir / "predictive_dataset.csv"
        if feature_path.exists():
            self.df_features = pd.read_csv(feature_path)
            logger.info(f"Loaded {len(self.df_features)} player-seasons from features")
        else:
            raise FileNotFoundError(f"Features not found at {feature_path}")

        # Load gate features
        gate_path = self.results_dir / "gate_features.csv"
        if gate_path.exists():
            self.df_gates = pd.read_csv(gate_path)
            logger.info(f"Loaded {len(self.df_gates)} player-seasons from gates")
        else:
            logger.warning("Gate features not found - some analysis will be limited")

        # Load test results
        test_path = self.results_dir / "latent_star_test_cases_report.md"
        if test_path.exists():
            self.test_results = self.parse_test_results(test_path)
            logger.info(f"Loaded test results for {len(self.test_results)} cases")
        else:
            logger.warning("Test results not found")

    def parse_test_results(self, test_path):
        """Parse the test results markdown file."""
        results = []
        with open(test_path, 'r') as f:
            lines = f.readlines()

        # Find the detailed results table
        in_table = False
        headers = []
        for line in lines:
            line = line.strip()
            if line.startswith('| Test | Player | Season | Category | Expected | Predicted'):
                in_table = True
                headers = [col.strip() for col in line.split('|')[1:-1]]
                continue
            elif in_table and line.startswith('|------'):
                continue
            elif in_table and line.startswith('| ') and not line.startswith('|---'):
                cols = [col.strip() for col in line.split('|')[1:-1]]
                if len(cols) >= len(headers):
                    result = dict(zip(headers, cols))
                    results.append(result)

        return results

    def diagnose_player(self, player_name, season):
        """Diagnose a specific player's failure."""
        logger.info(f"\n{'='*80}")
        logger.info(f"DIAGNOSING: {player_name} ({season})")
        logger.info(f"{'='*80}")

        # Find the player in test results
        test_case = None
        for result in self.test_results:
            if result.get('Player') == player_name and result.get('Season') == season:
                test_case = result
                break

        if not test_case:
            logger.error(f"No test case found for {player_name} {season}")
            return

        logger.info(f"Test Case: {test_case}")
        expected = test_case.get('Expected', 'Unknown')
        predicted = test_case.get('Predicted', 'Unknown')
        passed = test_case.get('Pass', 'Unknown')

        logger.info(f"Expected: {expected}")
        logger.info(f"Predicted: {predicted}")
        logger.info(f"Status: {'✅ PASS' if 'PASS' in str(passed) else '❌ FAIL'}")

        # Get player's feature data
        player_data = self.get_player_feature_data(player_name, season)
        if player_data.empty:
            logger.error(f"No feature data found for {player_name} {season}")
            return

        # Show feature profile
        self.analyze_feature_profile(player_data, expected, predicted)

        # Compare to similar players
        self.compare_to_similar_players(player_data, expected, predicted)

        # Analyze feature contributions
        self.analyze_feature_contributions(player_data)

        # Recommendations
        self.generate_recommendations(player_data, expected, predicted)

    def get_player_feature_data(self, player_name, season):
        """Get all feature data for a player-season."""
        # Debug: Check columns
        logger.info(f"Features columns: {list(self.df_features.columns[:5])}...")
        if hasattr(self, 'df_gates') and not self.df_gates.empty:
            logger.info(f"Gates columns: {list(self.df_gates.columns[:5])}...")

        # Merge features and gates
        df_merged = self.df_features.copy()
        if hasattr(self, 'df_gates') and not self.df_gates.empty:
            df_merged = pd.merge(
                df_merged,
                self.df_gates,
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_gate')
            )
            # Drop duplicate columns, keep the original
            duplicate_cols = [col for col in df_merged.columns if col.endswith('_gate')]
            for col in duplicate_cols:
                if col.replace('_gate', '') in df_merged.columns:
                    df_merged = df_merged.drop(columns=[col])

        logger.info(f"Merged columns: {list(df_merged.columns[:10])}...")

        # Find the player
        logger.info(f"Looking for {player_name} in {season}")
        logger.info(f"Sample players: {df_merged['PLAYER_NAME'].head().tolist()}")

        mask = (df_merged['PLAYER_NAME'] == player_name) & (df_merged['SEASON'] == season)
        player_data = df_merged[mask]

        logger.info(f"Found {len(player_data)} matching rows")

        return player_data

    def analyze_feature_profile(self, player_data, expected, predicted):
        """Analyze the player's feature profile."""
        logger.info(f"\n📊 FEATURE PROFILE ANALYSIS")
        logger.info(f"{'-'*50}")

        # Key features to analyze
        key_features = [
            'CREATION_TAX', 'CREATION_VOLUME_RATIO', 'SKILL_MATURITY_INDEX',
            'LEVERAGE_TS_DELTA', 'LEVERAGE_USG_DELTA', 'CLUTCH_FAILURE_RISK',
            'EFG_PCT_0_DRIBBLE', 'EFG_ISO_WEIGHTED', 'INEFFICIENT_CREATION_SCORE',
            'USG_PCT', 'AGE', 'PHYSICAL_DOMINANCE_RATIO',
            'RS_RIM_APPETITE', 'RS_PRESSURE_APPETITE', 'RS_PRESSURE_RESILIENCE',
            'DEPENDENCE_SCORE', 'INEFFICIENT_VOLUME_SCORE'
        ]

        for feature in key_features:
            if feature in player_data.columns:
                value = player_data[feature].iloc[0]
                if pd.notna(value):
                    # Get league percentiles for context
                    league_values = self.df_features[feature].dropna() if feature in self.df_features.columns else None
                    if league_values is not None and len(league_values) > 0:
                        percentile = (league_values <= value).mean() * 100
                        logger.info(f"{feature:30}: {value:8.3f} ({percentile:5.1f}th percentile)")
                    else:
                        logger.info(f"{feature:30}: {value:8.3f}")
                else:
                    logger.info(f"{feature:30}: NaN")

    def compare_to_similar_players(self, player_data, expected, predicted):
        """Compare to similar players that the model gets right."""
        logger.info(f"\n🔍 SIMILAR PLAYER COMPARISON")
        logger.info(f"{'-'*50}")

        # Find similar players based on key features
        player_row = player_data.iloc[0]

        # Get players with similar profiles
        comparison_features = ['CREATION_TAX', 'CREATION_VOLUME_RATIO', 'USG_PCT', 'AGE']

        # Filter to players with similar key stats
        similar_mask = pd.Series(True, index=self.df_features.index)

        for feature in comparison_features:
            if feature in player_data.columns and feature in self.df_features.columns:
                player_val = player_row[feature]
                if pd.notna(player_val):
                    # Find players within 20% of the value
                    feature_values = self.df_features[feature]
                    tolerance = abs(player_val) * 0.20 if player_val != 0 else 0.1
                    similar_mask &= (feature_values >= player_val - tolerance) & (feature_values <= player_val + tolerance)

        similar_players = self.df_features[similar_mask & (self.df_features['PLAYER_NAME'] != player_row['PLAYER_NAME'])]

        logger.info(f"Found {len(similar_players)} players with similar profiles")

        if len(similar_players) > 0:
            # Show top 5 most similar
            logger.info(f"\nTop 5 Similar Players:")
            logger.info(f"{'Player':20} {'Season':10} {'Creation Tax':12} {'Volume':8} {'USG':6}")
            logger.info(f"{'-'*20} {'-'*10} {'-'*12} {'-'*8} {'-'*6}")

            for _, row in similar_players.head(5).iterrows():
                logger.info(f"{row['PLAYER_NAME'][:19]:20} {row['SEASON']:10} {row['CREATION_TAX']:8.3f} {row['CREATION_VOLUME_RATIO']:8.3f} {row['USG_PCT']:6.2f}")

    def analyze_feature_contributions(self, player_data):
        """Analyze which features contribute most to the prediction."""
        logger.info(f"\n🎯 FEATURE CONTRIBUTION ANALYSIS")
        logger.info(f"{'-'*50}")

        if not hasattr(self.model, 'feature_importances_'):
            logger.warning("Model doesn't have feature importances")
            return

        # Get feature names (should match training)
        feature_names = [
            'CLUTCH_MIN_TOTAL', 'USG_PCT', 'USG_PCT_X_EFG_ISO_WEIGHTED',
            'PREV_CREATION_VOLUME_RATIO', 'PREV_EFG_ISO_WEIGHTED',
            'AGE_X_LEVERAGE_USG_DELTA_YOY_DELTA', 'SKILL_MATURITY_INDEX',
            'PHYSICAL_DOMINANCE_RATIO', 'ABDICATION_RISK', 'SELF_CREATED_FREQ'
        ]

        # Get feature values for this player
        player_values = []
        for feature in feature_names:
            if feature in player_data.columns:
                value = player_data[feature].iloc[0]
                player_values.append(value if pd.notna(value) else 0)
            else:
                player_values.append(0)

        # Calculate contributions (feature_importance * feature_value)
        contributions = []
        for i, (name, importance, value) in enumerate(zip(feature_names, self.model.feature_importances_, player_values)):
            contribution = importance * abs(value)  # Magnitude of contribution
            contributions.append((name, contribution, value))

        # Sort by contribution
        contributions.sort(key=lambda x: x[1], reverse=True)

        logger.info("Top Contributing Features:")
        for name, contrib, value in contributions[:10]:
            logger.info(f"{name:35}: {contrib:.4f} (value: {value:.3f})")

    def generate_recommendations(self, player_data, expected, predicted):
        """Generate recommendations for new features or fixes."""
        logger.info(f"\n💡 RECOMMENDATIONS")
        logger.info(f"{'-'*50}")

        player_row = player_data.iloc[0]

        # Analyze what went wrong
        issues = []

        # Check if dependence score is the issue
        if 'DEPENDENCE_SCORE' in player_data.columns:
            dep_score = player_row['DEPENDENCE_SCORE']
            if pd.notna(dep_score) and dep_score > 0.5:
                issues.append("High dependence score may be overriding strong individual skills")

        # Check creation efficiency vs volume
        if 'CREATION_TAX' in player_data.columns and 'CREATION_VOLUME_RATIO' in player_data.columns:
            tax = player_row['CREATION_TAX']
            volume = player_row['CREATION_VOLUME_RATIO']
            if pd.notna(tax) and pd.notna(volume):
                if tax > 0 and volume > 0.6:  # High volume, positive tax
                    issues.append("High-volume creator with positive tax - model may be missing 'efficient volume' signal")

        # Check age/maturity
        if 'AGE' in player_data.columns and 'SKILL_MATURITY_INDEX' in player_data.columns:
            age = player_row['AGE']
            maturity = player_row['SKILL_MATURITY_INDEX']
            if pd.notna(age) and pd.notna(maturity):
                if age < 25 and maturity < 0:
                    issues.append("Young player with negative maturity index - may need age-adjusted thresholds")

        # Check physical vs skill profile
        if 'PHYSICAL_DOMINANCE_RATIO' in player_data.columns and 'CREATION_TAX' in player_data.columns:
            phys_ratio = player_row['PHYSICAL_DOMINANCE_RATIO']
            skill_tax = player_row['CREATION_TAX']
            if pd.notna(phys_ratio) and pd.notna(skill_tax):
                if phys_ratio > 1.0 and skill_tax > 0:
                    issues.append("Physical player with good creation skills - may need 'athletic creator' feature")

        if issues:
            logger.info("Identified Issues:")
            for i, issue in enumerate(issues, 1):
                logger.info(f"{i}. {issue}")
        else:
            logger.info("No obvious issues identified - may need deeper feature analysis")

        logger.info(f"\nSuggested Next Steps:")
        logger.info("1. Compare this player's raw playoff data vs prediction")
        logger.info("2. Check if similar players have different feature profiles")
        logger.info("3. Consider creating interaction features for identified issues")

def main():
    if len(sys.argv) != 3:
        print("Usage: python diagnose_failures.py 'Player Name' 'Season'")
        print("Example: python diagnose_failures.py 'Desmond Bane' '2021-22'")
        return

    player_name = sys.argv[1]
    season = sys.argv[2]

    try:
        diagnostician = FailureDiagnostician()
        diagnostician.diagnose_player(player_name, season)
    except Exception as e:
        logger.error(f"Error diagnosing {player_name} {season}: {e}", exc_info=True)

if __name__ == "__main__":
    main()