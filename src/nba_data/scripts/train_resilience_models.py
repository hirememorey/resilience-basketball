import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def prepare_features(df, target_metric):
    """Prepare features and target for modeling."""
    rs_metric_col = f'rs_{target_metric}'
    po_metric_col = f'po_{target_metric}'
    
    # Create interaction term
    df[f'{rs_metric_col}_x_dcs'] = df[rs_metric_col] * df['opp_def_context_score']
    
    # Feature matrix
    X = df[[
        rs_metric_col,
        'opp_def_context_score',
        'rs_usg_pct',
        f'{rs_metric_col}_x_dcs'
    ]].fillna(0)
    
    # Target
    y = df[po_metric_col].fillna(0)
    
    return X, y

def train_model(X, y, model_name):
    """Train linear regression model."""
    # For very small datasets (Skewer test), don't split or split minimally
    if len(X) < 10:
        logger.warning("Dataset too small for split. Training on full set.")
        X_train, X_test, y_train, y_test = X, X, y, y
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    logger.info(f"{model_name} - R2: {r2:.3f}, RMSE: {rmse:.4f}")
    
    # Save model
    with open(f'models/{model_name}_model.pkl', 'wb') as f:
        pickle.dump(model, f)
        
    return rmse

def main():
    df = pd.read_csv('data/training_dataset.csv')
    logger.info(f"Training on {len(df)} samples...")
    
    metadata = {}
    
    # TS%
    X, y = prepare_features(df, 'ts_pct')
    metadata['ts_pct_rmse'] = train_model(X, y, 'ts_pct')
    
    # PPG
    X, y = prepare_features(df, 'ppg_per75')
    metadata['ppg_per75_rmse'] = train_model(X, y, 'ppg_per75')
    
    # AST%
    X, y = prepare_features(df, 'ast_pct')
    metadata['ast_pct_rmse'] = train_model(X, y, 'ast_pct')
    
    with open('models/model_metadata.pkl', 'wb') as f:
        pickle.dump(metadata, f)
        
    logger.info("✅ Models trained and saved.")

if __name__ == "__main__":
    main()

