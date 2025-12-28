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
    'age',
    'usg_pct',
    'ts_pct',
    'shot_quality_generation_delta',
    'creation_volume_ratio',
    'helio_potential_score',
    'subsidy_index',
    'projected_playoff_pps',
    'projected_playoff_output',
    'helio_above_replacement_value',
    'avg_opponent_dcs',
    'fragility_score',
    'physicality_score',
    # NEW (Dec 2025): Clutch Behavior Encoding - "Learn, Don't Patch"
    'clutch_usg_absolute',      # The absolute clutch usage floor
    'relative_usage_drop',       # Proportional drop (not absolute)
    'abdication_interaction',    # Usage × Efficiency delta interaction
]

def load_and_merge_data():
    """Load projected features and telescope targets, merge them."""
    # 1. Load Features (Projected Avatars)
    features_path = Path("results/predictive_dataset_with_friction.csv")
    if not features_path.exists():
        logger.error(f"Features not found at {features_path}")
        sys.exit(1)
    
    df_features = pd.read_csv(features_path)
    
    # Ensure all features are present (even as 0) to avoid XGBoost errors
    for feature in FEATURES:
        if feature not in df_features.columns:
            logger.warning(f"Feature '{feature}' missing from dataset. Filling with 0.0.")
            df_features[feature] = 0.0
            
    # 2. Load Targets
    targets_path = Path("results/training_targets_helio.csv")
    if not targets_path.exists():
        logger.error(f"Targets not found at {targets_path}")
        sys.exit(1)
    df_targets = pd.read_csv(targets_path)
    df_targets_slim = df_targets[['PLAYER_ID', 'SEASON_YEAR', 'FUTURE_PEAK_HELIO']]
    
    # 3. Merge
    # Standardize season format for merging (e.g. "2023-24" -> 2024)
    df_features['SEASON_YEAR'] = df_features['season'].apply(lambda x: int(x.split('-')[0]) + 1)
    
    # Ensure correct dtypes for merging
    df_features['player_id'] = df_features['player_id'].astype(str)
    df_targets_slim['PLAYER_ID'] = df_targets_slim['PLAYER_ID'].astype(str)
    
    merged = pd.merge(
        df_features, 
        df_targets_slim, 
        left_on=['player_id', 'SEASON_YEAR'],
        right_on=['PLAYER_ID', 'SEASON_YEAR'],
        how='inner'
    )
    logger.info(f"Merged dataset size: {len(merged)} rows")
    
    # ========== TARGET REFINEMENT: Abdication-Signature-Adjusted HELIO ==========
    # The "Ground Truth Trap" fix: penalize players who achieved their PIE by HIDING.
    # 
    # Key insight: Not all usage drops are bad. The problem is:
    #   - Usage drops AND Efficiency rises = HIDING (only taking easy shots)
    #   - Usage drops AND Efficiency drops = FORCED (taking harder shots under pressure)
    #
    # V3: Targeted penalty for the "Abdication Signature" only
    # abdication_interaction = leverage_usg_delta × leverage_ts_delta
    #   - NEGATIVE = hiding (usage down, efficiency up)
    #   - POSITIVE = forced or stepping up
    
    relative_drop = merged['relative_usage_drop'].fillna(0)
    abdication = merged['abdication_interaction'].fillna(0)
    
    # Calculate penalty factor:
    # - For abdication signature (negative interaction): apply penalty
    # - For forced/stepping up (positive interaction): no penalty or bonus
    
    def calculate_retention_factor(row):
        drop = row['relative_usage_drop'] if pd.notna(row['relative_usage_drop']) else 0
        abd = row['abdication_interaction'] if pd.notna(row['abdication_interaction']) else 0
        
        # Only penalize if BOTH conditions are met:
        # 1. Usage dropped significantly (< -0.10)
        # 2. Abdication signature is present (negative interaction, meaning TS went UP)
        
        if drop < -0.10 and abd < 0:
            # Abdication penalty: the more negative the interaction, the harsher
            # Scale: abd of -0.01 → 10% penalty, abd of -0.05 → 50% penalty
            # V4: More aggressive scaling (1000 instead of 500)
            penalty_magnitude = min(abs(abd) * 1000, 0.6)  # Cap at 60% penalty
            return 1.0 - penalty_magnitude
        elif drop > 0.05:
            # Player stepped UP in clutch - give a bonus
            return min(1.0 + drop, 1.3)
        else:
            # Neutral - no adjustment
            return 1.0
    
    volume_retention_factor = merged.apply(calculate_retention_factor, axis=1)
    
    # Apply the adjustment
    original_mean = merged['FUTURE_PEAK_HELIO'].mean()
    merged['FUTURE_PEAK_HELIO_ADJUSTED'] = merged['FUTURE_PEAK_HELIO'] * volume_retention_factor
    adjusted_mean = merged['FUTURE_PEAK_HELIO_ADJUSTED'].mean()
    
    logger.info("="*60)
    logger.info("TARGET REFINEMENT: Volume-Retention Adjustment Applied")
    logger.info("="*60)
    logger.info(f"  Original target mean: {original_mean:.4f}")
    logger.info(f"  Adjusted target mean: {adjusted_mean:.4f}")
    logger.info(f"  Volume retention factor range: [{volume_retention_factor.min():.3f}, {volume_retention_factor.max():.3f}]")
    
    # Show impact on key players for validation
    key_players = ['Ben Simmons', 'Nikola Jokić', 'Luka Dončić']
    for player in key_players:
        player_data = merged[merged['player_name'].str.contains(player, case=False, na=False)]
        if not player_data.empty:
            row = player_data.iloc[0]
            logger.info(f"  {player}: {row['FUTURE_PEAK_HELIO']:.2f} → {row['FUTURE_PEAK_HELIO_ADJUSTED']:.2f} (factor: {volume_retention_factor[player_data.index[0]]:.3f})")
    
    return merged

def train_telescope_model():
    df = load_and_merge_data()
    
    # Filter for Growth Cohort
    original_size = len(df)
    df_growth = df[df['age'] <= GROWTH_COHORT_AGE_LIMIT].copy()
    logger.info(f"Filtered for Growth Cohort (Age <= {GROWTH_COHORT_AGE_LIMIT}): {len(df_growth)}/{original_size} rows")
    
    # Final check for features
    available_features = [f for f in FEATURES if f in df_growth.columns]
    
    logger.info(f"Training with {len(available_features)} features: {available_features}")
    
    X = df_growth[available_features]
    # Use the Volume-Retention-Adjusted target to penalize abdicators
    y = df_growth['FUTURE_PEAK_HELIO_ADJUSTED']

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

