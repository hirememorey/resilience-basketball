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

        # Previous Playoff Features (New - Legitimate past → future)
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
            # Drop duplicate columns
            cols_to_drop = [c for c in df_merged.columns if '_prev_po' in c]
            df_merged = df_merged.drop(columns=cols_to_drop)
        else:
            logger.warning("No previous playoff features file found.")
        
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
        
        # PHASE 4: Trajectory Features (New)
        trajectory_path = self.results_dir / "trajectory_features.csv"
        if trajectory_path.exists():
            df_trajectory = pd.read_csv(trajectory_path)
            logger.info(f"Loaded Trajectory Features: {len(df_trajectory)} rows.")
            
            df_merged = pd.merge(
                df_merged,
                df_trajectory,
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_traj')
            )
            
            # Drop duplicate columns
            cols_to_drop = [c for c in df_merged.columns if '_traj' in c]
            df_merged = df_merged.drop(columns=cols_to_drop)
        else:
            logger.warning("No trajectory features file found. Run generate_trajectory_features.py first.")
        
        # PHASE 4: Gate Features (New)
        gate_path = self.results_dir / "gate_features.csv"
        if gate_path.exists():
            df_gate = pd.read_csv(gate_path)
            logger.info(f"Loaded Gate Features: {len(df_gate)} rows.")
            
            df_merged = pd.merge(
                df_merged,
                df_gate,
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_gate')
            )
            
            # Drop duplicate columns
            cols_to_drop = [c for c in df_merged.columns if '_gate' in c]
            df_merged = df_merged.drop(columns=cols_to_drop)
        else:
            logger.warning("No gate features file found. Run generate_gate_features.py first.")
        
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
        # DATA LEAKAGE FIX: Removed all playoff-based features (DELTA, RESILIENCE ratios, PO_*)
        # Only using Regular Season (RS_*) features that are available at prediction time
        features = [
            'CREATION_TAX', 'CREATION_VOLUME_RATIO',
            'LEVERAGE_TS_DELTA', 'LEVERAGE_USG_DELTA',  # Clutch data is RS-only
            'CLUTCH_MIN_TOTAL', 
            'EFG_PCT_0_DRIBBLE', 'EFG_ISO_WEIGHTED',
            # Context Features (Quality of Competition) - RS-only
            'QOC_TS_DELTA', 'QOC_USG_DELTA',
            # NEW: Opponent Defensive Context Features - RS-only
            'AVG_OPPONENT_DCS', 'MEAN_OPPONENT_DCS',
            'ELITE_WEAK_TS_DELTA', 'ELITE_WEAK_USG_DELTA',
            # New Plasticity Features - REMOVED: SHOT_DISTANCE_DELTA, SPATIAL_VARIANCE_DELTA (use PO data)
            # REMOVED: 'PO_EFG_BEYOND_RS_MEDIAN' (playoff feature)
            # New Shot Difficulty Features (V2) - RS-only
            'RS_PRESSURE_APPETITE',
            'RS_PRESSURE_RESILIENCE',
            # REMOVED: 'PRESSURE_APPETITE_DELTA', 'PRESSURE_RESILIENCE_DELTA' (playoff features)
            # NEW: Late vs Early Clock Pressure Features (V4.2) - RS-only
            'RS_LATE_CLOCK_PRESSURE_APPETITE',
            'RS_EARLY_CLOCK_PRESSURE_APPETITE',
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE',
            'RS_EARLY_CLOCK_PRESSURE_RESILIENCE',
            # REMOVED: All *_DELTA clock features (playoff features)
            # New Physicality Features - RS-only
            'RS_FTr',
            # REMOVED: 'FTr_RESILIENCE' (playoff feature)
            # New Rim Pressure Features - RS-only
            'RS_RIM_APPETITE',
            # REMOVED: 'RIM_PRESSURE_RESILIENCE' (playoff feature)
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
        
        # PHASE 4: Add Trajectory Features (YoY Deltas and Priors)
        trajectory_yoy_features = [
            'CREATION_VOLUME_RATIO_YOY_DELTA',
            'CREATION_TAX_YOY_DELTA',
            'LEVERAGE_USG_DELTA_YOY_DELTA',
            'LEVERAGE_TS_DELTA_YOY_DELTA',
            'RS_PRESSURE_RESILIENCE_YOY_DELTA',
            'RS_PRESSURE_APPETITE_YOY_DELTA',
            'RS_RIM_APPETITE_YOY_DELTA',
            'EFG_ISO_WEIGHTED_YOY_DELTA',
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE_YOY_DELTA',
        ]
        
        trajectory_prior_features = [
            'PREV_CREATION_VOLUME_RATIO',
            'PREV_CREATION_TAX',
            'PREV_LEVERAGE_USG_DELTA',
            'PREV_LEVERAGE_TS_DELTA',
            'PREV_RS_PRESSURE_RESILIENCE',
            'PREV_RS_PRESSURE_APPETITE',
            'PREV_RS_RIM_APPETITE',
            'PREV_EFG_ISO_WEIGHTED',
        ]
        
        trajectory_age_interaction_features = [
            'AGE_X_CREATION_VOLUME_RATIO_YOY_DELTA',
            'AGE_X_LEVERAGE_USG_DELTA_YOY_DELTA',
            'AGE_X_RS_PRESSURE_RESILIENCE_YOY_DELTA',
        ]
        
        # Add trajectory features that exist in dataframe
        for feat in trajectory_yoy_features + trajectory_prior_features + trajectory_age_interaction_features:
            if feat in df.columns:
                features.append(feat)
        
        # PHASE 4: Add Gate Features (Soft Features)
        gate_features = [
            'ABDICATION_RISK',
            'PHYSICALITY_FLOOR',
            'SELF_CREATED_FREQ',
            'DATA_COMPLETENESS_SCORE',
            'SAMPLE_SIZE_CONFIDENCE',
            'LEVERAGE_DATA_CONFIDENCE',
            'NEGATIVE_SIGNAL_COUNT',
        ]
        
        # Add gate features that exist in dataframe
        for feat in gate_features:
            if feat in df.columns:
                features.append(feat)
        
        # NEW: Add Previous Playoff Features (Legitimate past → future)
        prev_po_features = [
            'PREV_PO_RIM_APPETITE',
            'PREV_PO_PRESSURE_RESILIENCE',
            'PREV_PO_PRESSURE_APPETITE',
            'PREV_PO_FTr',
            'PREV_PO_LATE_CLOCK_PRESSURE_RESILIENCE',
            'PREV_PO_EARLY_CLOCK_PRESSURE_RESILIENCE',
            'PREV_PO_ARCHETYPE',
            'HAS_PLAYOFF_EXPERIENCE',
        ]
        
        # Add previous playoff features that exist in dataframe
        for feat in prev_po_features:
            if feat in df.columns:
                features.append(feat)
                logger.info(f"Added previous playoff feature: {feat}")
        
        target = 'ARCHETYPE'
        
        # Filter out features that don't exist in the dataframe
        existing_features = [f for f in features if f in df.columns]
        missing_features = [f for f in features if f not in df.columns]
        if missing_features:
            logger.warning(f"Missing expected features, they will be ignored: {missing_features}")
        
        logger.info(f"Total features: {len(existing_features)} (including {len([f for f in existing_features if 'USG_PCT' in f])} usage-aware features)")
        
        # Store season information for temporal split (before feature preparation may drop rows)
        # Create a season year for sorting (e.g., "2020-21" -> 2020)
        def parse_season_year(season_str):
            try:
                if isinstance(season_str, str):
                    year_part = season_str.split('-')[0]
                    return int(year_part)
                return 0
            except:
                return 0
        
        df['_SEASON_YEAR'] = df['SEASON'].apply(parse_season_year)
        
        X = df[existing_features].copy()
        y = df[target]
        
        # Handle NaN values in features
        # PHASE 4: Special handling for trajectory and gate features
        for col in X.columns:
            if X[col].isna().sum() > 0:
                if 'CLOCK' in col:
                    # Clock features: fill NaN with 0 (neutral signal when no data)
                    X[col] = X[col].fillna(0)
                elif '_YOY_DELTA' in col:
                    # Trajectory features (YoY deltas): fill NaN with 0 (no change = neutral signal for first seasons)
                    X[col] = X[col].fillna(0)
                elif col.startswith('PREV_'):
                    # Prior features: fill NaN with median (no prior = use population average)
                    # Exception: PREV_PO_ARCHETYPE should be -1 (no previous archetype)
                    if col == 'PREV_PO_ARCHETYPE':
                        X[col] = X[col].fillna(-1)
                    else:
                        median_val = X[col].median()
                        X[col] = X[col].fillna(median_val)
                elif col == 'HAS_PLAYOFF_EXPERIENCE':
                    # Binary flag: fill NaN with False (no experience)
                    X[col] = X[col].fillna(False).astype(int)
                elif 'AGE_X_' in col and '_YOY_DELTA' in col:
                    # Age-trajectory interactions: fill NaN with 0 (calculated after filling trajectory)
                    X[col] = X[col].fillna(0)
                elif col in ['DATA_COMPLETENESS_SCORE', 'SAMPLE_SIZE_CONFIDENCE', 'LEVERAGE_DATA_CONFIDENCE']:
                    # Gate confidence features: fill NaN with 0 (no data = no confidence)
                    X[col] = X[col].fillna(0)
                elif col in ['ABDICATION_RISK', 'PHYSICALITY_FLOOR', 'SELF_CREATED_FREQ', 'NEGATIVE_SIGNAL_COUNT']:
                    # Gate risk/count features: fill NaN with 0 (no risk = 0, no signals = 0)
                    X[col] = X[col].fillna(0)
                else:
                    # Other features: fill with median
                    median_val = X[col].median()
                    X[col] = X[col].fillna(median_val)
        
        # Encode Labels
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # DATA LEAKAGE FIX: Temporal Train/Test Split (not random)
        # Train on earlier seasons (2015-2020), test on later seasons (2021-2024)
        # This prevents future data from informing past predictions
        logger.info("Performing temporal train/test split...")
        
        # Split at 2020-21 season (train on 2015-2020, test on 2021-2024)
        split_year = 2020
        train_mask = df['_SEASON_YEAR'] <= split_year
        test_mask = df['_SEASON_YEAR'] > split_year
        
        # Get indices for train/test split (X is a DataFrame, use loc)
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
