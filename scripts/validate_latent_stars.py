import pandas as pd
import joblib
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Test Cases Definition ---
# Canonical Latent Stars
LATENT_STAR_CASES = [
    {"PLAYER_NAME": "Shai Gilgeous-Alexander", "SEASON": "2018-19"},
    {"PLAYER_NAME": "Jalen Brunson", "SEASON": "2020-21"},
    {"PLAYER_NAME": "Tyrese Maxey", "SEASON": "2021-22"},
]

# Control Group
CONTROL_CASES = [
    # Established Superstar (should have a high score, but maybe not peak potential)
    {"PLAYER_NAME": "LeBron James", "SEASON": "2018-19"},
    # Premier Role Player (should have a very low score)
    {"PLAYER_NAME": "P.J. Tucker", "SEASON": "2018-19"},
    # "Fool's Gold" / System Merchant Example
    {"PLAYER_NAME": "D'Angelo Russell", "SEASON": "2021-22"},
    # The "Jordan Poole Paradox" - High Volume/Efficiency but Low Scalability
    {"PLAYER_NAME": "Jordan Poole", "SEASON": "2021-22"}
]

ALL_CASES = LATENT_STAR_CASES + CONTROL_CASES

def load_model_and_data():
    """Loads the trained model, feature list, and predictive dataset."""
    model_path = Path("models/telescope_model.pkl")
    features_path = Path("models/telescope_features.json")
    data_path = Path("results/predictive_dataset.csv")
    targets_path = Path("results/training_targets_helio.csv")

    if not all([model_path.exists(), features_path.exists(), data_path.exists(), targets_path.exists()]):
        logger.error("Missing required files (model, features, data, or targets). Exiting.")
        return None, None, None, None

    model = joblib.load(model_path)
    with open(features_path, 'r') as f:
        features = json.load(f)
    
    df_data = pd.read_csv(data_path)
    df_targets = pd.read_csv(targets_path)

    # Merge in the actual target for comparison
    df_targets_slim = df_targets[['PLAYER_ID', 'SEASON_YEAR', 'FUTURE_PEAK_HELIO']]
    df_data['SEASON_YEAR'] = df_data['SEASON'].apply(lambda x: int(x.split('-')[0]) + 1)
    df_data['PLAYER_ID'] = df_data['PLAYER_ID'].astype(str)
    df_targets_slim['PLAYER_ID'] = df_targets_slim['PLAYER_ID'].astype(str)
    df_merged = pd.merge(df_data, df_targets_slim, on=['PLAYER_ID', 'SEASON_YEAR'], how='left')

    return model, features, df_merged

def evaluate_latent_stars():
    """Evaluates the model's performance on the defined latent star test suite."""
    model, features, df = load_model_and_data()
    if model is None:
        return

    test_data = []
    found_types = []
    
    for case in LATENT_STAR_CASES:
        player_data = df[(df['PLAYER_NAME'] == case['PLAYER_NAME']) & (df['SEASON'] == case['SEASON'])]
        if not player_data.empty:
            test_data.append(player_data.iloc[0])
            found_types.append('Latent Star')
        else:
            logger.warning(f"Could not find data for {case['PLAYER_NAME']} in {case['SEASON']}")

    for case in CONTROL_CASES:
        player_data = df[(df['PLAYER_NAME'] == case['PLAYER_NAME']) & (df['SEASON'] == case['SEASON'])]
        if not player_data.empty:
            test_data.append(player_data.iloc[0])
            # Assign control type based on name for simplicity in validation
            if case['PLAYER_NAME'] == "LeBron James":
                found_types.append('Superstar')
            elif case['PLAYER_NAME'] == "P.J. Tucker":
                found_types.append('Role Player')
            else:
                found_types.append("Fool's Gold")
        else:
            logger.warning(f"Could not find data for {case['PLAYER_NAME']} in {case['SEASON']}")

    if not test_data:
        logger.error("No test cases found in the dataset.")
        return

    df_test = pd.DataFrame(test_data)

    # Ensure all required features are present, fill missing with 0 for prediction
    for feature in features:
        if feature not in df_test.columns:
            logger.warning(f"Feature '{feature}' not found in test data. Calculating if possible.")
            if feature == 'HELIO_POTENTIAL_SCORE':
                df_test['HELIO_POTENTIAL_SCORE'] = df_test['SHOT_QUALITY_GENERATION_DELTA'] * (df_test['USG_PCT'] ** 1.5)
            else:
                df_test[feature] = 0
            
    X_test = df_test[features]
    
    # Check for NaN values in prediction features and fill with mean
    for col in X_test.columns:
        if X_test[col].isnull().any():
            mean_val = X_test[col].mean() if not X_test[col].isnull().all() else 0
            X_test[col] = X_test[col].fillna(mean_val)
            logger.warning(f"NaNs found in '{col}'. Filled with value: {mean_val:.4f}")


    predictions = model.predict(X_test)

    # Create report
    report_df = pd.DataFrame({
        'PLAYER_NAME': df_test['PLAYER_NAME'],
        'SEASON': df_test['SEASON'],
        'PLAYER_TYPE': found_types,
        'PREDICTED_PEAK_HELIO': predictions,
        'ACTUAL_PEAK_HELIO': df_test['FUTURE_PEAK_HELIO'],
        'SHOT_QUALITY_DELTA': df_test.get('SHOT_QUALITY_GENERATION_DELTA', 0)
    })

    logger.info("\\n" + "="*80)
    logger.info("Latent Star Test Suite Evaluation (Telescope Model v2)")
    logger.info("="*80)
    logger.info("Target: FUTURE_PEAK_HELIO (Higher is better)")
    logger.info("-" * 80)
    
    # Format for better readability
    report_df['PREDICTED_PEAK_HELIO'] = report_df['PREDICTED_PEAK_HELIO'].map('{:,.3f}'.format)
    report_df['ACTUAL_PEAK_HELIO'] = report_df['ACTUAL_PEAK_HELIO'].map('{:,.3f}'.format)
    if 'SHOT_QUALITY_DELTA' in report_df.columns and pd.api.types.is_numeric_dtype(report_df['SHOT_QUALITY_DELTA']):
        report_df['SHOT_QUALITY_DELTA'] = report_df['SHOT_QUALITY_DELTA'].map('{:,.3f}'.format)
        
    print(report_df.to_string(index=False))
    logger.info("="*80)

if __name__ == "__main__":
    evaluate_latent_stars()

