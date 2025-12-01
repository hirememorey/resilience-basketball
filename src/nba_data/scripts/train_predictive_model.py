import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_squared_error, r2_score
import argparse
import logging
from pathlib import Path
import pickle
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Train Predictive Resilience Model')
    parser.add_argument('--input', default='data/predictive_model_training_data.csv', help='Input training data')
    parser.add_argument('--model_out', default='models/predictive_resilience_model.json', help='Output model path')
    args = parser.parse_args()
    
    # 1. Load Data
    if not Path(args.input).exists():
        logger.error(f"Missing input file: {args.input}")
        return
        
    df = pd.read_csv(args.input)
    logger.info(f"Loaded {len(df)} training samples")
    
    # 2. Define Features and Target
    features = [
        'rs_ts_pct', 'rs_ppg_per75', 'rs_ast_pct', 'rs_usg_pct',  # Baseline
        'opp_def_context_score',                                  # Scenario Context
        'consistency_gmsc_std',                                   # Consistency
        'ts_pct_vs_top10', 'ppg_per75_vs_top10', 
        'ast_pct_vs_top10', 'usg_pct_vs_top10'                    # Vs Top 10
    ]
    
    target = 'RESILIENCE_SCORE'
    
    X = df[features].fillna(0) # Basic fillna, ideally investigate missingness
    y = df[target]
    
    # 3. Train/Test Split
    # Since we only have 2023-24 data populated with features right now, 
    # we will use a standard random split. 
    # In production, we would split by Season (Train on < 2024, Test on 2024).
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Train Model (XGBoost Regressor)
    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        random_state=42,
        n_jobs=-1
    )
    
    logger.info("Training XGBoost model...")
    model.fit(X_train, y_train)
    
    # 5. Evaluate
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    logger.info(f"Model Evaluation:")
    logger.info(f"  RMSE: {rmse:.4f}")
    logger.info(f"  R2:   {r2:.4f}")
    
    # 6. Feature Importance
    importance = model.get_booster().get_score(importance_type='gain')
    importance_df = pd.DataFrame([
        {'Feature': k, 'Importance': v} 
        for k, v in importance.items()
    ]).sort_values('Importance', ascending=False)
    
    logger.info("\nTop Predictors of Resilience:")
    logger.info(importance_df.to_string(index=False))
    
    # 7. Save Model
    model.save_model(args.model_out)
    logger.info(f"✅ Saved model to {args.model_out}")

    # Save feature names for inference
    with open('models/predictive_features.json', 'w') as f:
        json.dump(features, f)

if __name__ == "__main__":
    main()

