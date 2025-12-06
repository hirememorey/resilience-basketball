"""
Train Predictive Model with RFE-Selected Top 10 Features.

This script:
1. Loads the RFE-selected top 10 features
2. Trains an XGBoost model with only those features
3. Compares performance with the full 65-feature model
4. Saves the simplified model
"""

import pandas as pd
import numpy as np
import logging
import sys
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import ast

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/train_rfe_model.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class RFEModelTrainer:
    def __init__(self):
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.models_dir = Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    def load_rfe_features(self, n_features=10):
        """Load RFE-selected features from comparison CSV."""
        rfe_path = self.results_dir / "rfe_feature_count_comparison.csv"
        if not rfe_path.exists():
            raise FileNotFoundError(f"RFE results not found at {rfe_path}")
        
        df_rfe = pd.read_csv(rfe_path)
        row = df_rfe[df_rfe['n_features'] == n_features]
        
        if row.empty:
            raise ValueError(f"No RFE results found for {n_features} features")
        
        # Parse the features list from string
        features_str = row.iloc[0]['features']
        features = ast.literal_eval(features_str)
        
        logger.info(f"Loaded {len(features)} RFE-selected features:")
        for i, feat in enumerate(features, 1):
            logger.info(f"  {i}. {feat}")
        
        return features
    
    def load_and_merge_data(self):
        """Load features and labels, merge them into a training set (same as train_predictive_model.py)."""
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
        
        # Pressure Features
        pressure_path = self.results_dir / "pressure_features.csv"
        if pressure_path.exists():
            df_pressure = pd.read_csv(pressure_path)
            logger.info(f"Loaded Pressure Features: {len(df_pressure)} rows.")
        else:
            df_pressure = pd.DataFrame()
            logger.warning("No pressure features file found.")

        # Physicality Features
        physicality_path = self.results_dir / "physicality_features.csv"
        if physicality_path.exists():
            df_physicality = pd.read_csv(physicality_path)
            logger.info(f"Loaded Physicality Features: {len(df_physicality)} rows.")
        else:
            df_physicality = pd.DataFrame()
            logger.warning("No physicality features file found.")
        
        # Rim Pressure Features
        rim_path = self.results_dir / "rim_pressure_features.csv"
        if rim_path.exists():
            df_rim = pd.read_csv(rim_path)
            logger.info(f"Loaded Rim Pressure Features: {len(df_rim)} rows.")
        else:
            df_rim = pd.DataFrame()
            logger.warning("No rim pressure features file found.")
        
        # Trajectory Features
        trajectory_path = self.results_dir / "trajectory_features.csv"
        if trajectory_path.exists():
            df_trajectory = pd.read_csv(trajectory_path)
            logger.info(f"Loaded Trajectory Features: {len(df_trajectory)} rows.")
        else:
            df_trajectory = pd.DataFrame()
            logger.warning("No trajectory features file found.")
        
        # Gate Features
        gate_path = self.results_dir / "gate_features.csv"
        if gate_path.exists():
            df_gate = pd.read_csv(gate_path)
            logger.info(f"Loaded Gate Features: {len(df_gate)} rows.")
        else:
            df_gate = pd.DataFrame()
            logger.warning("No gate features file found.")
        
        # Merge
        df_targets.columns = [c.upper() for c in df_targets.columns]
        
        df_merged = pd.merge(
            df_features,
            df_targets[['PLAYER_NAME', 'SEASON', 'ARCHETYPE', 'RESILIENCE_QUOTIENT', 'DOMINANCE_SCORE']],
            on=['PLAYER_NAME', 'SEASON'],
            how='inner'
        )

        # Merge with pressure features
        if not df_pressure.empty:
            df_merged = pd.merge(
                df_merged,
                df_pressure,
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_pressure')
            )
            cols_to_drop = [c for c in df_merged.columns if '_pressure' in c]
            df_merged = df_merged.drop(columns=cols_to_drop)
            
        # Merge with physicality features
        if not df_physicality.empty:
            df_merged = pd.merge(
                df_merged,
                df_physicality,
                on=['PLAYER_NAME', 'SEASON'],
                how='left',
                suffixes=('', '_phys')
            )
            cols_to_drop = [c for c in df_merged.columns if '_phys' in c]
            df_merged = df_merged.drop(columns=cols_to_drop)
            
        # Merge with rim pressure features
        if not df_rim.empty:
            df_merged = pd.merge(
                df_merged,
                df_rim,
                on=['PLAYER_NAME', 'SEASON'],
                how='left',
                suffixes=('', '_rim')
            )
            cols_to_drop = [c for c in df_merged.columns if '_rim' in c]
            df_merged = df_merged.drop(columns=cols_to_drop)
            
        # Merge with trajectory features
        if not df_trajectory.empty:
            df_merged = pd.merge(
                df_merged,
                df_trajectory,
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_traj')
            )
            cols_to_drop = [c for c in df_merged.columns if '_traj' in c]
            df_merged = df_merged.drop(columns=cols_to_drop)
            
        # Merge with gate features
        if not df_gate.empty:
            df_merged = pd.merge(
                df_merged,
                df_gate,
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_gate')
            )
            cols_to_drop = [c for c in df_merged.columns if '_gate' in c]
            df_merged = df_merged.drop(columns=cols_to_drop)
        
        # Merge with previous playoff features
        prev_po_path = self.results_dir / "previous_playoff_features.csv"
        if prev_po_path.exists():
            df_prev_po = pd.read_csv(prev_po_path)
            logger.info(f"Loaded Previous Playoff Features: {len(df_prev_po)} rows.")
            
            df_merged = pd.merge(
                df_merged,
                df_prev_po,
                on=['PLAYER_ID', 'PLAYER_NAME', 'SEASON'],
                how='left',
                suffixes=('', '_prev_po')
            )
            cols_to_drop = [c for c in df_merged.columns if '_prev_po' in c]
            df_merged = df_merged.drop(columns=cols_to_drop)
        else:
            logger.warning("No previous playoff features file found.")
        
        logger.info(f"Merged Dataset Size: {len(df_merged)} player-seasons.")
        
        return df_merged

    def prepare_features(self, df, rfe_features):
        """Prepare feature set using only RFE-selected features."""
        # Add Usage-Aware Features (if USG_PCT is in RFE features, create interactions)
        if 'USG_PCT' in df.columns and 'USG_PCT' in rfe_features:
            df['USG_PCT'] = pd.to_numeric(df['USG_PCT'], errors='coerce')
            usg_median = df['USG_PCT'].median()
            df['USG_PCT'] = df['USG_PCT'].fillna(usg_median)
            
            # Create interaction terms if they're in RFE features
            interaction_terms = [
                ('USG_PCT', 'CREATION_VOLUME_RATIO'),
                ('USG_PCT', 'LEVERAGE_USG_DELTA'),
                ('USG_PCT', 'RS_PRESSURE_APPETITE'),
                ('USG_PCT', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE'),
                ('USG_PCT', 'EFG_ISO_WEIGHTED')
            ]
            
            for feat1, feat2 in interaction_terms:
                interaction_name = f'{feat1}_X_{feat2}'
                if interaction_name in rfe_features:
                    if feat1 in df.columns and feat2 in df.columns:
                        df[interaction_name] = (df[feat1].fillna(0) * df[feat2].fillna(0))
        
        # Filter to only RFE-selected features
        existing_features = [f for f in rfe_features if f in df.columns]
        missing_features = [f for f in rfe_features if f not in df.columns]
        
        if missing_features:
            logger.warning(f"Missing RFE features (will be ignored): {missing_features}")
        
        logger.info(f"Using {len(existing_features)} RFE-selected features (out of {len(rfe_features)} requested)")
        
        X = df[existing_features].copy()
        
        # Handle NaN values (same logic as train_predictive_model.py)
        for col in X.columns:
            if X[col].isna().sum() > 0:
                if 'CLOCK' in col:
                    X[col] = X[col].fillna(0)
                elif '_YOY_DELTA' in col:
                    X[col] = X[col].fillna(0)
                elif col.startswith('PREV_'):
                    median_val = X[col].median()
                    X[col] = X[col].fillna(median_val)
                elif 'AGE_X_' in col and '_YOY_DELTA' in col:
                    X[col] = X[col].fillna(0)
                elif col in ['DATA_COMPLETENESS_SCORE', 'SAMPLE_SIZE_CONFIDENCE', 'LEVERAGE_DATA_CONFIDENCE']:
                    X[col] = X[col].fillna(0)
                elif col in ['ABDICATION_RISK', 'PHYSICALITY_FLOOR', 'SELF_CREATED_FREQ', 'NEGATIVE_SIGNAL_COUNT']:
                    X[col] = X[col].fillna(0)
                else:
                    median_val = X[col].median()
                    X[col] = X[col].fillna(median_val)
        
        return X, existing_features

    def train(self, n_features=10):
        """Train the XGBoost Model with RFE-selected features."""
        logger.info("=" * 80)
        logger.info(f"Training Model with RFE-Selected Top {n_features} Features")
        logger.info("=" * 80)
        
        # Load RFE-selected features
        rfe_features = self.load_rfe_features(n_features=n_features)
        
        # Load and merge data
        df = self.load_and_merge_data()
        
        # Prepare features
        X, feature_names = self.prepare_features(df, rfe_features)
        y = df['ARCHETYPE']
        
        # Encode Labels
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # DATA LEAKAGE FIX: Temporal Train/Test Split (not random)
        # Train on earlier seasons (2015-2020), test on later seasons (2021-2024)
        logger.info("Performing temporal train/test split...")
        
        # Create season year for sorting
        def parse_season_year(season_str):
            try:
                if isinstance(season_str, str):
                    year_part = season_str.split('-')[0]
                    return int(year_part)
                return 0
            except:
                return 0
        
        df['_SEASON_YEAR'] = df['SEASON'].apply(parse_season_year)
        
        # Split at 2020-21 season (train on 2015-2020, test on 2021-2024)
        split_year = 2020
        train_mask = df['_SEASON_YEAR'] <= split_year
        test_mask = df['_SEASON_YEAR'] > split_year
        
        # Get indices for train/test split
        train_indices = df[train_mask].index
        test_indices = df[test_mask].index
        
        # Split X and y using indices
        X_train = X.loc[train_indices]
        X_test = X.loc[test_indices]
        y_train = y_encoded[train_indices]
        y_test = y_encoded[test_indices]
        
        train_seasons = df.loc[train_mask, 'SEASON'].unique()
        test_seasons = df.loc[test_mask, 'SEASON'].unique()
        logger.info(f"Training seasons: {sorted(train_seasons)} ({len(X_train)} samples)")
        logger.info(f"Testing seasons: {sorted(test_seasons)} ({len(X_test)} samples)")
        logger.info(f"Feature count: {len(feature_names)} (reduced from 65)")
        
        # Initialize XGBoost
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
        logger.info("Training model...")
        model.fit(X_train, y_train)
        
        # Save Model
        model_path = self.models_dir / f"resilience_xgb_rfe_{n_features}.pkl"
        encoder_path = self.models_dir / f"archetype_encoder_rfe_{n_features}.pkl"
        joblib.dump(model, model_path)
        joblib.dump(le, encoder_path)
        logger.info(f"Saved model to {model_path}")
        
        # Evaluation
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Model Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        logger.info(f"{'='*80}")
        logger.info("\nClassification Report:\n" + classification_report(y_test, y_pred, target_names=le.classes_))
        
        # Feature Importance
        importance = pd.DataFrame({
            'Feature': feature_names,
            'Importance': model.feature_importances_
        }).sort_values(by='Importance', ascending=False)
        
        logger.info("\nFeature Importance:\n" + str(importance))
        
        # Visualization: Feature Importance
        plt.figure(figsize=(10, max(6, len(feature_names) * 0.3)))
        sns.barplot(data=importance, x='Importance', y='Feature', hue='Feature', legend=False)
        plt.title(f"Feature Importance: RFE-Selected Top {n_features} Features", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.results_dir / f"feature_importance_rfe_{n_features}.png", dpi=300, bbox_inches='tight')
        logger.info(f"Saved feature importance plot to {self.results_dir / f'feature_importance_rfe_{n_features}.png'}")
        
        # Visualization: Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=le.classes_, yticklabels=le.classes_)
        plt.title(f"Confusion Matrix: RFE-Selected Top {n_features} Features", fontsize=14, fontweight='bold')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.tight_layout()
        plt.savefig(self.results_dir / f"confusion_matrix_rfe_{n_features}.png", dpi=300)
        logger.info(f"Saved confusion matrix to {self.results_dir / f'confusion_matrix_rfe_{n_features}.png'}")
        
        # Save results summary
        results_summary = {
            'n_features': n_features,
            'accuracy': accuracy,
            'features': feature_names,
            'feature_importance': importance.to_dict('records')
        }
        
        import json
        with open(self.results_dir / f"rfe_model_results_{n_features}.json", 'w') as f:
            json.dump(results_summary, f, indent=2)
        
        logger.info(f"\n{'='*80}")
        logger.info("Training Complete!")
        logger.info(f"{'='*80}")
        
        return model, le, accuracy, importance

if __name__ == "__main__":
    trainer = RFEModelTrainer()
    
    # Train with top 10 features
    model, le, accuracy, importance = trainer.train(n_features=10)
    
    logger.info(f"\n✅ Model trained with 10 features")
    logger.info(f"✅ Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"✅ Model saved to: models/resilience_xgb_rfe_10.pkl")

