"""
Train Predictive Model for Playoff Resilience Archetypes.

This script:
1. Loads the feature set (Stress Vectors) from results/predictive_dataset.csv
2. Loads the target labels (Archetypes) from results/resilience_archetypes.csv
3. Trains an XGBoost Classifier to predict Archetypes from RS data.
4. Evaluates performance and saves the model.
"""

import pandas as pd
import numpy as np
import logging
import sys
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/train_model.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ResiliencePredictor:
    def __init__(self):
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.models_dir = Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    def load_and_merge_data(self):
        """Load features and labels, merge them into a training set."""
        logger.info("Loading datasets...")
        
        # Features
        feature_path = self.results_dir / "predictive_dataset.csv"
        if not feature_path.exists():
            raise FileNotFoundError(f"Features file not found at {feature_path}")
        df_features = pd.read_csv(feature_path)
        
        # Targets
        target_path = self.results_dir / "resilience_archetypes.csv"
        if not target_path.exists():
            raise FileNotFoundError(f"Target labels not found at {target_path}")
        df_targets = pd.read_csv(target_path)
        
        # Plasticity Features (New)
        # We'll need to combine plasticity scores from all seasons
        plasticity_files = self.results_dir.glob("plasticity_scores_*.csv")
        df_plasticity_list = [pd.read_csv(f) for f in plasticity_files]
        
        if not df_plasticity_list:
            logger.warning("No plasticity score files found. Proceeding without them.")
            df_plasticity = pd.DataFrame()
        else:
            df_plasticity = pd.concat(df_plasticity_list, ignore_index=True)

        # Merge
        # Note: Target CSV likely has 'PLAYER_ID' and 'SEASON'
        # Let's inspect columns if needed, but standardizing on ID/SEASON is key.
        
        # Check for column case sensitivity
        df_targets.columns = [c.upper() for c in df_targets.columns]
        
        # Target columns are: RESILIENCE_QUOTIENT, DOMINANCE_SCORE, ARCHETYPE
        
        # Merge base features with targets
        df_merged = pd.merge(
            df_features,
            df_targets[['PLAYER_NAME', 'SEASON', 'ARCHETYPE', 'RESILIENCE_QUOTIENT', 'DOMINANCE_SCORE']],
            on=['PLAYER_NAME', 'SEASON'],
            how='inner'
        )

        # Merge with plasticity features if they exist
        if not df_plasticity.empty:
            df_merged = pd.merge(
                df_merged,
                df_plasticity,
                on=['PLAYER_ID', 'SEASON'],
                how='left'
        )
        
        logger.info(f"Merged Dataset Size: {len(df_merged)} player-seasons.")
        
        # Drop missing values (some players might be missing leverage data)
        # We filled NaNs in feature generation, but let's be safe.
        # Actually, XGBoost handles NaNs, but let's see.
        
        return df_merged

    def train(self):
        """Train the XGBoost Model."""
        df = self.load_and_merge_data()
        
        # Define Features and Target
        features = [
            'CREATION_TAX', 'CREATION_VOLUME_RATIO',
            'LEVERAGE_TS_DELTA', 'LEVERAGE_USG_DELTA',
            'CLUTCH_MIN_TOTAL', 
            'EFG_PCT_0_DRIBBLE', 'EFG_ISO_WEIGHTED',
            # New Plasticity Features
            'SHOT_DISTANCE_DELTA',
            'SPATIAL_VARIANCE_DELTA',
            'PO_EFG_BEYOND_RS_MEDIAN'
        ]
        target = 'ARCHETYPE'
        
        # Filter out features that don't exist in the dataframe
        existing_features = [f for f in features if f in df.columns]
        missing_features = [f for f in features if f not in df.columns]
        if missing_features:
            logger.warning(f"Missing expected features, they will be ignored: {missing_features}")
        
        X = df[existing_features]
        y = df[target]
        
        # Encode Labels
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # Train/Test Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        logger.info(f"Training on {len(X_train)} samples, Testing on {len(X_test)} samples.")
        
        # Initialize XGBoost
        # Using a simplified classifier for interpretability
        model = xgb.XGBClassifier(
            objective='multi:softprob',
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric='mlogloss',
            random_state=42
        )
        
        # Train
        model.fit(X_train, y_train)
        
        # Save Model
        joblib.dump(model, self.models_dir / "resilience_xgb.pkl")
        joblib.dump(le, self.models_dir / "archetype_encoder.pkl")
        
        # Evaluation
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Model Accuracy: {accuracy:.4f}")
        logger.info("\nClassification Report:\n" + classification_report(y_test, y_pred, target_names=le.classes_))
        
        # Feature Importance
        importance = pd.DataFrame({
            'Feature': existing_features,
            'Importance': model.feature_importances_
        }).sort_values(by='Importance', ascending=False)
        
        logger.info("\nFeature Importance:\n" + str(importance))
        
        # Visualization: Feature Importance
        plt.figure(figsize=(10, 6))
        sns.barplot(data=importance, x='Importance', y='Feature', hue='Feature', legend=False)
        plt.title("Predictive Feature Importance (Stress Vectors)")
        plt.tight_layout()
        plt.savefig(self.results_dir / "feature_importance.png")
        
        # Visualization: Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=le.classes_, yticklabels=le.classes_)
        plt.title("Confusion Matrix")
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.tight_layout()
        plt.savefig(self.results_dir / "confusion_matrix.png")

if __name__ == "__main__":
    predictor = ResiliencePredictor()
    predictor.train()
