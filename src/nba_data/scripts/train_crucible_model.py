import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
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

class CrucibleModelTrainer:
    def __init__(self):
        self.data_dir = Path("data")
        self.models_dir = Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.features = [
            'CREATION_TAX', 
            'CREATION_VOLUME_RATIO', 
            'LEVERAGE_TS_DELTA', 
            'LEVERAGE_USG_DELTA',
            'DEPENDENCE_SCORE', 
            'SHOT_QUALITY_GENERATION_DELTA',
            'EFG_PCT_0_DRIBBLE', 
            'EFG_ISO_WEIGHTED',
            'USG_PCT',
            'AGE'
        ]
        self.target = 'PIE_TARGET'

    def train(self, input_path="data/crucible_dataset.csv"):
        """
        Trains the physics-to-impact translation model.
        """
        if not Path(input_path).exists():
            logger.error(f"Missing {input_path}")
            return
            
        df = pd.read_csv(input_path)
        logger.info(f"Loaded {len(df)} samples for training.")
        
        # 1. Prepare Features and Target
        # Filter for existing features
        existing_features = [f for f in self.features if f in df.columns]
        missing_features = [f for f in self.features if f not in df.columns]
        if missing_features:
            logger.warning(f"Missing features: {missing_features}")
            
        X = df[existing_features].fillna(0)
        y = df[self.target]
        
        # 2. Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 3. Train XGBoost Regressor
        model = xgb.XGBRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        
        logger.info("Training XGBoost Regressor...")
        model.fit(X_train, y_train)
        
        # 4. Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Model Evaluation: MSE={mse:.4f}, R2={r2:.4f}")
        
        # 5. Feature Importance
        importances = pd.DataFrame({
            'feature': existing_features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info(f"Feature Importances:\n{importances}")
        
        # 6. Save Model
        model_path = self.models_dir / "crucible_impact_model.pkl"
        joblib.dump(model, model_path)
        logger.info(f"✅ Saved model to {model_path}")
        
        # 7. Identify "Ghosts" in the training data
        # Predicted Impact >> Actual Impact
        df['PREDICTED_IMPACT'] = model.predict(X)
        df['IMPACT_GAP'] = df['PREDICTED_IMPACT'] - df[self.target]
        
        ghosts = df[df['IMPACT_GAP'] > df['IMPACT_GAP'].std() * 1.5].sort_values('IMPACT_GAP', ascending=False)
        logger.info(f"Detected {len(ghosts)} 'Ghosts' (Underperformers relative to physics):")
        logger.info(ghosts[['PLAYER_NAME', 'SEASON', 'PREDICTED_IMPACT', self.target, 'IMPACT_GAP']].head(10))
        
        return model

if __name__ == "__main__":
    trainer = CrucibleModelTrainer()
    trainer.train()

