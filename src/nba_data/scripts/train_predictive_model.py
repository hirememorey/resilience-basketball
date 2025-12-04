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

        # Pressure Features (New V2)
        pressure_path = self.results_dir / "pressure_features.csv"
        if pressure_path.exists():
            df_pressure = pd.read_csv(pressure_path)
            logger.info(f"Loaded Pressure Features: {len(df_pressure)} rows.")
        else:
            df_pressure = pd.DataFrame()
            logger.warning("No pressure features file found.")

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

        # Merge with pressure features if they exist
        if not df_pressure.empty:
            df_merged = pd.merge(
                df_merged,
                df_pressure,
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_pressure') # Avoid collisions if names match
            )
            # Drop duplicate columns if any (like PLAYER_NAME_pressure)
            cols_to_drop = [c for c in df_merged.columns if '_pressure' in c]
            df_merged = df_merged.drop(columns=cols_to_drop)
            
        # Physicality Features (New V3/V4)
        physicality_path = self.results_dir / "physicality_features.csv"
        if physicality_path.exists():
            df_physicality = pd.read_csv(physicality_path)
            logger.info(f"Loaded Physicality Features: {len(df_physicality)} rows.")
            
            df_merged = pd.merge(
                df_merged,
                df_physicality,
                on=['PLAYER_NAME', 'SEASON'], # Physicality uses PLAYER_NAME/SEASON as keys or PLAYER_ID?
                how='left',
                suffixes=('', '_phys')
            )
            # Note: Physicality script uses PLAYER_ID, PLAYER_NAME, SEASON. 
            # If 'PLAYER_ID' is in df_merged (it is), better to use that + SEASON
            # But let's check if df_merged has PLAYER_ID consistently. Yes.
            
            # Drop duplicate columns
            cols_to_drop = [c for c in df_merged.columns if '_phys' in c]
            df_merged = df_merged.drop(columns=cols_to_drop)
        else:
            logger.warning("No physicality features file found.")

        # Rim Pressure Features (New V4.1)
        rim_path = self.results_dir / "rim_pressure_features.csv"
        if rim_path.exists():
            df_rim = pd.read_csv(rim_path)
            logger.info(f"Loaded Rim Pressure Features: {len(df_rim)} rows.")
            
            df_merged = pd.merge(
                df_merged,
                df_rim,
                on=['PLAYER_NAME', 'SEASON'],
                how='left',
                suffixes=('', '_rim')
            )
            
            # Drop duplicate columns
            cols_to_drop = [c for c in df_merged.columns if '_rim' in c]
            df_merged = df_merged.drop(columns=cols_to_drop)
        else:
            logger.warning("No rim pressure features file found.")
        
        logger.info(f"Merged Dataset Size: {len(df_merged)} player-seasons.")
        
        # Drop missing values (some players might be missing leverage data)
        # We filled NaNs in feature generation, but let's be safe.
        # Actually, XGBoost handles NaNs, but let's see.
        
        return df_merged

    def train(self):
        """Train the XGBoost Model."""
        df = self.load_and_merge_data()
        
        # PHASE 2: Add Usage-Aware Features
        # Add USG_PCT as explicit feature and create interaction terms
        if 'USG_PCT' in df.columns:
            logger.info("Adding usage-aware features (USG_PCT + interaction terms)...")
            
            # Ensure USG_PCT is numeric and fill NaN with median
            df['USG_PCT'] = pd.to_numeric(df['USG_PCT'], errors='coerce')
            usg_median = df['USG_PCT'].median()
            df['USG_PCT'] = df['USG_PCT'].fillna(usg_median)
            logger.info(f"USG_PCT coverage: {df['USG_PCT'].notna().sum()}/{len(df)} ({df['USG_PCT'].notna().sum()/len(df)*100:.1f}%)")
            
            # Create interaction terms with top stress vectors
            # Based on feature importance: CREATION_VOLUME_RATIO (6.2%), LEVERAGE_USG_DELTA (9.2%), 
            # RS_PRESSURE_APPETITE (4.5%), RS_LATE_CLOCK_PRESSURE_RESILIENCE (4.8%), EFG_ISO_WEIGHTED (4.1%)
            interaction_terms = [
                ('USG_PCT', 'CREATION_VOLUME_RATIO'),
                ('USG_PCT', 'LEVERAGE_USG_DELTA'),
                ('USG_PCT', 'RS_PRESSURE_APPETITE'),
                ('USG_PCT', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE'),
                ('USG_PCT', 'EFG_ISO_WEIGHTED')
            ]
            
            for feat1, feat2 in interaction_terms:
                if feat1 in df.columns and feat2 in df.columns:
                    interaction_name = f'{feat1}_X_{feat2}'
                    # Fill NaN with 0 for interaction terms (if either feature is missing, interaction is 0)
                    df[interaction_name] = (df[feat1].fillna(0) * df[feat2].fillna(0))
                    logger.info(f"Created interaction term: {interaction_name}")
                else:
                    logger.warning(f"Could not create interaction {feat1} * {feat2} - missing features")
        else:
            logger.warning("USG_PCT not found in dataset. Usage-aware features will not be added.")
        
        # Define Features and Target
        features = [
            'CREATION_TAX', 'CREATION_VOLUME_RATIO',
            'LEVERAGE_TS_DELTA', 'LEVERAGE_USG_DELTA',
            'CLUTCH_MIN_TOTAL', 
            'EFG_PCT_0_DRIBBLE', 'EFG_ISO_WEIGHTED',
            # Context Features (Quality of Competition)
            'QOC_TS_DELTA', 'QOC_USG_DELTA',
            # NEW: Opponent Defensive Context Features
            'AVG_OPPONENT_DCS', 'MEAN_OPPONENT_DCS',
            'ELITE_WEAK_TS_DELTA', 'ELITE_WEAK_USG_DELTA',
            # New Plasticity Features
            'SHOT_DISTANCE_DELTA',
            'SPATIAL_VARIANCE_DELTA',
            'PO_EFG_BEYOND_RS_MEDIAN',
            # New Shot Difficulty Features (V2)
            'RS_PRESSURE_APPETITE',
            'RS_PRESSURE_RESILIENCE',
            'PRESSURE_APPETITE_DELTA',
            'PRESSURE_RESILIENCE_DELTA',
            # NEW: Late vs Early Clock Pressure Features (V4.2)
            'RS_LATE_CLOCK_PRESSURE_APPETITE',
            'RS_EARLY_CLOCK_PRESSURE_APPETITE',
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE',
            'RS_EARLY_CLOCK_PRESSURE_RESILIENCE',
            'LATE_CLOCK_PRESSURE_APPETITE_DELTA',
            'EARLY_CLOCK_PRESSURE_APPETITE_DELTA',
            'LATE_CLOCK_PRESSURE_RESILIENCE_DELTA',
            'EARLY_CLOCK_PRESSURE_RESILIENCE_DELTA',
            # New Physicality Features
            'FTr_RESILIENCE',
            'RS_FTr',
            # New Rim Pressure Features
            'RS_RIM_APPETITE',
            'RIM_PRESSURE_RESILIENCE'
        ]
        
        # PHASE 2: Conditionally add Usage-Aware Features
        if 'USG_PCT' in df.columns:
            features.append('USG_PCT')
            # Add interaction terms if they were created
            interaction_feature_names = [
                'USG_PCT_X_CREATION_VOLUME_RATIO',
                'USG_PCT_X_LEVERAGE_USG_DELTA',
                'USG_PCT_X_RS_PRESSURE_APPETITE',
                'USG_PCT_X_RS_LATE_CLOCK_PRESSURE_RESILIENCE',
                'USG_PCT_X_EFG_ISO_WEIGHTED'
            ]
            for interaction_feat in interaction_feature_names:
                if interaction_feat in df.columns:
                    features.append(interaction_feat)
        
        target = 'ARCHETYPE'
        
        # Filter out features that don't exist in the dataframe
        existing_features = [f for f in features if f in df.columns]
        missing_features = [f for f in features if f not in df.columns]
        if missing_features:
            logger.warning(f"Missing expected features, they will be ignored: {missing_features}")
        
        logger.info(f"Total features: {len(existing_features)} (including {len([f for f in existing_features if 'USG_PCT' in f])} usage-aware features)")
        
        X = df[existing_features].copy()
        y = df[target]
        
        # Handle NaN values in features
        # For clock features with low coverage, fill NaN with 0 (no clock pressure data = neutral signal)
        # For other features, fill with median
        for col in X.columns:
            if X[col].isna().sum() > 0:
                if 'CLOCK' in col:
                    # Clock features: fill NaN with 0 (neutral signal when no data)
                    X[col] = X[col].fillna(0)
                    logger.info(f"Filled {X[col].isna().sum()} NaN values in {col} with 0")
                else:
                    # Other features: fill with median
                    median_val = X[col].median()
                    X[col] = X[col].fillna(median_val)
                    logger.info(f"Filled {X[col].isna().sum()} NaN values in {col} with median ({median_val:.4f})")
        
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
