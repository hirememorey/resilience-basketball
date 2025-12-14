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
        
    def load_rfe_features(self, n_features=15):
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
        
        # [NEW] FORCE INCLUSION: The "Truth Tellers" (Dec 12, 2025)
        # These features are critical for distinguishing Empty Calories from True Stars
        # INEFFICIENT_VOLUME_SCORE: (CREATION_VOLUME_RATIO * Negative_CREATION_TAX) - massive negative signal for Tank Commanders
        # SHOT_QUALITY_GENERATION_DELTA: Measures if player generates easy shots or just hard shots - exposes Empty Calorie creators
        critical_features = ['INEFFICIENT_VOLUME_SCORE', 'SHOT_QUALITY_GENERATION_DELTA']

        for feat in critical_features:
            if feat not in features:
                # Replace the last (least important) feature to maintain count, or just append
                if len(features) >= n_features:
                    features.pop()
                features.append(feat)
                logger.info(f"Force-included critical feature: {feat}")

        # Legacy: Force include SHOT_QUALITY_GENERATION_DELTA if available (Dec 8, 2025)
        # This feature reduces reliance on sample weighting and should always be included
        if 'SHOT_QUALITY_GENERATION_DELTA' not in features:
            # Remove lowest importance feature if we're at the limit
            if len(features) >= n_features:
                # Keep top n_features-1, add SHOT_QUALITY_GENERATION_DELTA
                features = features[:n_features-1]
            features.append('SHOT_QUALITY_GENERATION_DELTA')
            logger.info(f"Added SHOT_QUALITY_GENERATION_DELTA to feature set (reduces reliance on sample weighting)")
        
        logger.info(f"Loaded {len(features)} RFE-selected features (including SHOT_QUALITY_GENERATION_DELTA):")
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
        """
        Prepare feature set using only RFE-selected features.
        
        CRITICAL: Apply transformations in the correct order to match prediction pipeline:
        1. Flash Multiplier (transforms CREATION_VOLUME_RATIO)
        2. Multi-Signal Tax System (transforms CREATION_VOLUME_RATIO, EFG_ISO_WEIGHTED, etc.)
        3. Create interaction terms from TRANSFORMED values
        4. Filter to RFE features
        5. Handle NaN values
        """
        df = df.copy()  # Work on copy to avoid modifying original
        
        # ========== STEP 1: Flash Multiplier (Phase 3.6 Fix #1) ==========
        # Apply Flash Multiplier FIRST - transforms CREATION_VOLUME_RATIO
        if 'CREATION_VOLUME_RATIO' in df.columns and 'CREATION_TAX' in df.columns and 'EFG_ISO_WEIGHTED' in df.columns:
            # Phase 3.8 Fix: Use qualified players (rotation players) for percentile calculations
            # Filter by volume to avoid small sample noise
            qualified_mask = (
                (df.get('RS_TOTAL_VOLUME', 0) >= 50) | 
                (df.get('TOTAL_FGA', 0) >= 200)
            ) & (df.get('USG_PCT', 0) >= 0.10)
            qualified_df = df[qualified_mask] if qualified_mask.any() else df
            
            # Calculate percentiles on qualified players
            vol_25th = qualified_df['CREATION_VOLUME_RATIO'].quantile(0.25) if len(qualified_df) > 0 else df['CREATION_VOLUME_RATIO'].quantile(0.25)
            tax_80th = qualified_df['CREATION_TAX'].quantile(0.80) if len(qualified_df) > 0 else df['CREATION_TAX'].quantile(0.80)
            efg_80th = qualified_df['EFG_ISO_WEIGHTED'].quantile(0.80) if len(qualified_df) > 0 else df['EFG_ISO_WEIGHTED'].quantile(0.80)
            
            # Phase 3.7 Fix #2: Include RS_PRESSURE_RESILIENCE as alternative flash signal
            pressure_80th = None
            if 'RS_PRESSURE_RESILIENCE' in qualified_df.columns:
                pressure_80th = qualified_df['RS_PRESSURE_RESILIENCE'].quantile(0.80) if len(qualified_df) > 0 else None
            
            # Calculate star median volume from Kings/Bulldozers
            star_mask = df['ARCHETYPE'].isin(['King (Resilient Star)', 'Bulldozer (Fragile Star)'])
            if star_mask.any():
                star_median_vol = df.loc[star_mask, 'CREATION_VOLUME_RATIO'].median()
            else:
                star_median_vol = 0.65  # Fallback
                
            logger.info(f"Applying Flash Multiplier (Star Median Vol: {star_median_vol:.4f})...")
            
            # Vectorized Flash Multiplier
            is_low_vol = df['CREATION_VOLUME_RATIO'] < vol_25th
            is_elite = (df['CREATION_TAX'] > tax_80th) | (df['EFG_ISO_WEIGHTED'] > efg_80th)
            if pressure_80th is not None:
                is_elite |= (df['RS_PRESSURE_RESILIENCE'] > pressure_80th)
                
            flash_mask = is_low_vol & is_elite
            if flash_mask.any():
                df.loc[flash_mask, 'CREATION_VOLUME_RATIO'] = star_median_vol
                logger.info(f"  Applied Flash Multiplier to {flash_mask.sum()} player-seasons")
        
        # ========== STEP 2: Multi-Signal Tax System (Phase 4.2) ==========
        # Apply Multi-Signal Tax System SECOND - transforms base features before interaction terms
        # This matches the prediction pipeline logic exactly
        
        # Step 2.1: Check exemption (true stars have positive signals OR high creation volume)
        leverage_usg_delta = df.get('LEVERAGE_USG_DELTA', pd.Series([0] * len(df)))
        leverage_ts_delta = df.get('LEVERAGE_TS_DELTA', pd.Series([0] * len(df)))
        creation_tax = df.get('CREATION_TAX', pd.Series([0] * len(df)))
        creation_vol_ratio = df.get('CREATION_VOLUME_RATIO', pd.Series([0] * len(df)))
        
        # Exemption #1: Positive leverage signals
        has_positive_leverage = (
            (leverage_usg_delta > 0) | (leverage_ts_delta > 0)
        )
        
        # Exemption #2: Positive creation efficiency
        has_positive_creation = creation_tax > 0
        
        # Exemption #3: High creation volume (>0.60)
        has_high_creation_volume = creation_vol_ratio > 0.60
        
        is_exempt = has_positive_leverage | has_positive_creation | has_high_creation_volume
        
        # Step 2.2: Calculate tax penalties (if not exempt)
        # Initialize penalties (1.0 = no penalty)
        volume_penalty = pd.Series([1.0] * len(df))
        efficiency_penalty = pd.Series([1.0] * len(df))
        
        # Tax #1: Open Shot Dependency (50% reduction)
        if 'RS_OPEN_SHOT_FREQUENCY' in df.columns:
            # Phase 3.8 Fix #2: Use STAR average (USG > 20%) for threshold, not league average
            star_players = df[df.get('USG_PCT', 0) > 0.20] if 'USG_PCT' in df.columns else df
            if len(star_players) > 0:
                open_freq_75th = star_players['RS_OPEN_SHOT_FREQUENCY'].quantile(0.75)
            else:
                open_freq_75th = df['RS_OPEN_SHOT_FREQUENCY'].quantile(0.75)
            
            mask_open_tax = (~is_exempt) & (df['RS_OPEN_SHOT_FREQUENCY'] > open_freq_75th)
            volume_penalty.loc[mask_open_tax] *= 0.50
            efficiency_penalty.loc[mask_open_tax] *= 0.50
            logger.info(f"  Applied Open Shot Tax to {mask_open_tax.sum()} player-seasons")
        
        # Tax #2: Creation Efficiency Collapse (20% additional reduction)
        mask_creation_tax = (~is_exempt) & (creation_tax < 0)
        volume_penalty.loc[mask_creation_tax] *= 0.80
        efficiency_penalty.loc[mask_creation_tax] *= 0.80
        
        # Tax #3: Leverage Abdication (20% additional reduction)
        mask_leverage_tax = (~is_exempt) & (leverage_usg_delta < 0) & (leverage_ts_delta < 0)
        volume_penalty.loc[mask_leverage_tax] *= 0.80
        efficiency_penalty.loc[mask_leverage_tax] *= 0.80
        
        # Tax #4: Pressure Avoidance (20% additional reduction)
        if 'RS_PRESSURE_APPETITE' in df.columns:
            # Use qualified players for 40th percentile
            qualified_mask = (
                (df.get('RS_TOTAL_VOLUME', 0) >= 50) | 
                (df.get('TOTAL_FGA', 0) >= 200)
            ) & (df.get('USG_PCT', 0) >= 0.10)
            qualified_df = df[qualified_mask] if qualified_mask.any() else df
            pressure_app_40th = qualified_df['RS_PRESSURE_APPETITE'].quantile(0.40) if len(qualified_df) > 0 else df['RS_PRESSURE_APPETITE'].quantile(0.40)
            
            mask_pressure_tax = (~is_exempt) & (df['RS_PRESSURE_APPETITE'] < pressure_app_40th)
            volume_penalty.loc[mask_pressure_tax] *= 0.80
            efficiency_penalty.loc[mask_pressure_tax] *= 0.80
        
        # Step 2.3: Apply taxes to base features
        # Tax CREATION_VOLUME_RATIO (volume feature)
        if 'CREATION_VOLUME_RATIO' in df.columns:
            df['CREATION_VOLUME_RATIO'] = df['CREATION_VOLUME_RATIO'] * volume_penalty
        
        # Tax EFG_ISO_WEIGHTED (efficiency feature)
        if 'EFG_ISO_WEIGHTED' in df.columns:
            df['EFG_ISO_WEIGHTED'] = df['EFG_ISO_WEIGHTED'] * efficiency_penalty
        
        # Tax EFG_PCT_0_DRIBBLE (efficiency feature)
        if 'EFG_PCT_0_DRIBBLE' in df.columns:
            df['EFG_PCT_0_DRIBBLE'] = df['EFG_PCT_0_DRIBBLE'] * efficiency_penalty
        
        # Tax RS_PRESSURE_APPETITE (volume feature)
        if 'RS_PRESSURE_APPETITE' in df.columns:
            df['RS_PRESSURE_APPETITE'] = df['RS_PRESSURE_APPETITE'] * volume_penalty
        
        # Tax LEVERAGE_USG_DELTA (volume feature)
        if 'LEVERAGE_USG_DELTA' in df.columns:
            df['LEVERAGE_USG_DELTA'] = df['LEVERAGE_USG_DELTA'] * volume_penalty
        
        logger.info(f"Applied Multi-Signal Tax System to base features")
        
        # ========== STEP 3: Create Interaction Terms from TRANSFORMED Values ==========
        # CRITICAL: Interaction terms must use transformed values, not raw values
        if 'USG_PCT' in df.columns and 'USG_PCT' in rfe_features:
            df['USG_PCT'] = pd.to_numeric(df['USG_PCT'], errors='coerce')
            
            # CRITICAL FIX: Normalize USG_PCT from percentage (26.0) to decimal (0.26)
            # The dataset stores USG_PCT as a percentage, but we need decimal format for consistency
            if df['USG_PCT'].max() > 1.0:
                df['USG_PCT'] = df['USG_PCT'] / 100.0
                logger.info(f"Normalized USG_PCT from percentage to decimal format")
            
            usg_median = df['USG_PCT'].median()
            df['USG_PCT'] = df['USG_PCT'].fillna(usg_median)
            
            # Create interaction terms from TRANSFORMED base features
            interaction_terms = [
                ('USG_PCT', 'CREATION_VOLUME_RATIO'),  # Uses transformed CREATION_VOLUME_RATIO
                ('USG_PCT', 'LEVERAGE_USG_DELTA'),     # Uses transformed LEVERAGE_USG_DELTA
                ('USG_PCT', 'RS_PRESSURE_APPETITE'),   # Uses transformed RS_PRESSURE_APPETITE
                ('USG_PCT', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE'),
                ('USG_PCT', 'EFG_ISO_WEIGHTED')        # Uses transformed EFG_ISO_WEIGHTED
            ]
            
            for feat1, feat2 in interaction_terms:
                interaction_name = f'{feat1}_X_{feat2}'
                if interaction_name in rfe_features:
                    if feat1 in df.columns and feat2 in df.columns:
                        # Use transformed values (already in df)
                        df[interaction_name] = (df[feat1].fillna(0) * df[feat2].fillna(0))
                        logger.debug(f"Created interaction term {interaction_name} from transformed values")
        
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

    def train(self, n_features=15):
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
        
        # Calculate sample weights for asymmetric loss
        # False positives (predicting "Victim" as "King") are much worse than false negatives
        # REDUCED from 5x to 3x (Dec 8, 2025) - SHOT_QUALITY_GENERATION_DELTA feature reduces reliance on sample weighting
        # Weight function: weight = 1.0 + (is_victim_actual * is_high_usage * 2.0)
        # This gives 3x total weight (1.0 base + 2.0 penalty = 3.0) for high-usage victims
        logger.info("Calculating sample weights for asymmetric loss (3x penalty for high-usage victims)...")
        
        # Get actual archetypes for training set
        y_train_archetypes = df.loc[train_indices, 'ARCHETYPE']
        is_victim = (y_train_archetypes == 'Victim (Fragile Role)').astype(int)
        
        # Get usage for training set
        if 'USG_PCT' in df.columns:
            usg_pct = df.loc[train_indices, 'USG_PCT'].fillna(0.0)
            # Normalize USG_PCT if it's in percentage format
            if usg_pct.max() > 1.0:
                usg_pct = usg_pct / 100.0
            is_high_usage = (usg_pct > 0.25).astype(int)  # High usage threshold (25%)
        else:
            is_high_usage = pd.Series([0] * len(y_train_archetypes))
            logger.warning("USG_PCT not found - sample weighting will not account for usage")
        
        # Calculate weights: 1.0 base + penalty for high-usage victims
        # REDUCED from 5x to 3x (Dec 8, 2025) - SHOT_QUALITY_GENERATION_DELTA feature reduces reliance on sample weighting
        # Weight function: weight = 1.0 + (is_victim_actual * is_high_usage * penalty_multiplier)
        # 3x total weight (1.0 base + 2.0 penalty = 3.0) for high-usage victims
        penalty_multiplier = 2.0  # REDUCED from 4.0 (5x) to 2.0 (3x) - Dec 8, 2025
        sample_weights = 1.0 + (is_victim * is_high_usage * penalty_multiplier)
        
        logger.info(f"  Base weight: 1.0")
        logger.info(f"  Penalty multiplier: {penalty_multiplier} (total weight = {1.0 + penalty_multiplier}x for high-usage victims)")
        logger.info(f"  High-usage victims (penalty): {is_victim.sum()} victims, {is_high_usage.sum()} high-usage")
        logger.info(f"  High-usage victims receiving penalty: {(is_victim * is_high_usage).sum()}")
        logger.info(f"  Weighted samples: {(sample_weights > 1.0).sum()} (weight > 1.0)")
        logger.info(f"  Max weight: {sample_weights.max():.2f}")
        logger.info(f"  Mean weight: {sample_weights.mean():.2f}")
        
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
        
        # Train with sample weights
        logger.info("Training model with asymmetric loss (sample weighting)...")
        model.fit(X_train, y_train, sample_weight=sample_weights.values)
        
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
    model, le, accuracy, importance = trainer.train(n_features=15)
    
    logger.info(f"\n✅ Model trained with 10 features")
    logger.info(f"✅ Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"✅ Model saved to: models/resilience_xgb_rfe_10.pkl")

