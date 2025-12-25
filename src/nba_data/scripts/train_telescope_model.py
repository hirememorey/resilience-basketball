"""
Train Telescope Model (Future Potential Engine).

This script trains the Telescope Model to predict Peak Future Playoff PIE (3-year horizon).
It uses the "Projected Avatars" (Universal Projection) as input.

Key constraints:
1. Trains ONLY on the "Growth Cohort" (Age <= 26).
2. Uses only portable, physics-based features.
3. Target is time-shifted (MAX future PIE).

Output:
    models/telescope_model.pkl: The trained model.
    results/telescope_evaluation.txt: Performance metrics.
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import logging
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Constants
GROWTH_COHORT_AGE_LIMIT = 26
FEATURES = [
    'CREATION_TAX',
    'CREATION_VOLUME_RATIO',
    'LEVERAGE_USG_DELTA',
    'LEVERAGE_TS_DELTA',
    'RS_PRESSURE_APPETITE', # If available
    'EFG_ISO_WEIGHTED',
    'USG_PCT',
    'DEPENDENCE_SCORE',
    'AGE',
    # Interaction terms
    'USG_PCT_X_CREATION_VOLUME_RATIO',
    'USG_PCT_X_LEVERAGE_USG_DELTA'
]

def load_and_merge_data():
    """Load projected features and telescope targets, merge them."""
    # 1. Load Features (Projected Avatars)
    features_path = Path("data/projected_telescope_dataset.csv")
    if not features_path.exists():
        logger.error(f"Features not found at {features_path}")
        sys.exit(1)
    df_features = pd.read_csv(features_path)
    
    # 2. Load Targets
    targets_path = Path("results/training_targets_helio.csv")
    if not targets_path.exists():
        logger.error(f"Targets not found at {targets_path}")
        sys.exit(1)
    df_targets = pd.read_csv(targets_path)
    df_targets_slim = df_targets[['PLAYER_ID', 'SEASON_YEAR', 'FUTURE_PEAK_HELIO']]
    
    # 3. Merge
    # Standardize season format for merging
    df_features['SEASON_YEAR'] = df_features['SEASON'].apply(lambda x: int(x.split('-')[0]) + 1)
    
    # Ensure correct dtypes for merging
    df_features['PLAYER_ID'] = df_features['PLAYER_ID'].astype(str)
    df_targets_slim['PLAYER_ID'] = df_targets_slim['PLAYER_ID'].astype(str)
    
    merged = pd.merge(df_features, df_targets_slim, on=['PLAYER_ID', 'SEASON_YEAR'], how='inner')
    logger.info(f"Merged dataset size: {len(merged)} rows")
    
    return merged

def train_telescope_model():
    df = load_and_merge_data()
    
    if 'USG_PCT' not in df.columns and 'usg_pct_vs_top10' in df.columns:
        logger.info("Renaming 'usg_pct_vs_top10' to 'USG_PCT' for model training.")
        df.rename(columns={'usg_pct_vs_top10': 'USG_PCT'}, inplace=True)
        
    # Filter for Growth Cohort
    original_size = len(df)
    df_growth = df[df['AGE'] <= GROWTH_COHORT_AGE_LIMIT].copy()
    logger.info(f"Filtered for Growth Cohort (Age <= {GROWTH_COHORT_AGE_LIMIT}): {len(df_growth)}/{original_size} rows")
    
    # Validate Features exist
    available_features = [f for f in FEATURES if f in df_growth.columns]
    missing_features = [f for f in FEATURES if f not in df_growth.columns]
    if missing_features:
        logger.warning(f"Missing features: {missing_features}")
    
    logger.info(f"Training with {len(available_features)} features: {available_features}")
    
    X = df_growth[available_features]
    y = df_growth['FUTURE_PEAK_HELIO']
    
    # Train/Test Split (Random is okay for now, but Temporal is better. 
    # Given small dataset, let's just do random to get a working prototype).
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # XGBoost Regressor
    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=100,
        max_depth=4,
        learning_rate=0.05,
        n_jobs=-1,
        random_state=42
    )
    
    logger.info("Training XGBoost model...")
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, preds)
    
    logger.info("="*40)
    logger.info("Telescope Model Evaluation")
    logger.info("="*40)
    logger.info(f"RMSE: {rmse:.4f}")
    logger.info(f"R2 Score: {r2:.4f}")
    logger.info(f"Target Mean: {y.mean():.4f}")
    logger.info(f"Target Std: {y.std():.4f}")
    
    # Feature Importance
    importance = pd.DataFrame({
        'Feature': available_features,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    logger.info("\nTop 5 Drivers of Future Potential:")
    logger.info(importance.head(5))
    
    # Save Model
    output_dir = Path("models")
    output_dir.mkdir(exist_ok=True)
    model_path = output_dir / "telescope_model.pkl"
    joblib.dump(model, model_path)
    logger.info(f"\nSaved model to {model_path}")
    
    # Save Feature List (for inference)
    import json
    with open(output_dir / "telescope_features.json", 'w') as f:
        json.dump(available_features, f)

if __name__ == "__main__":
    train_telescope_model()

