"""
Recursive Feature Elimination (RFE) for Feature Selection.

This script:
1. Loads the full feature set (same as train_predictive_model.py)
2. Runs RFE to identify top 10-15 features
3. Compares accuracy with reduced feature sets
4. Reports which features are most important
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
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_selection import RFE, RFECV
import xgboost as xgb

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/rfe_feature_selection.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class RFEFeatureSelector:
    def __init__(self):
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.models_dir = Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
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
        
        # Merge with previous playoff features (after df_merged is created)
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

    def prepare_features(self, df):
        """
        Prepare feature set (same logic as train_predictive_model.py).
        
        CRITICAL: Apply transformations in the correct order to match prediction pipeline:
        1. Flash Multiplier (transforms CREATION_VOLUME_RATIO)
        2. Multi-Signal Tax System (transforms CREATION_VOLUME_RATIO, EFG_ISO_WEIGHTED, etc.)
        3. Create interaction terms from TRANSFORMED values
        """
        df = df.copy()  # Work on copy to avoid modifying original
        
        # ========== STEP 1: Flash Multiplier (Phase 3.6 Fix #1) ==========
        # Apply Flash Multiplier FIRST - transforms CREATION_VOLUME_RATIO
        if 'CREATION_VOLUME_RATIO' in df.columns and 'CREATION_TAX' in df.columns and 'EFG_ISO_WEIGHTED' in df.columns:
            # Phase 3.8 Fix: Use qualified players (rotation players) for percentile calculations
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
        volume_penalty = pd.Series([1.0] * len(df))
        efficiency_penalty = pd.Series([1.0] * len(df))
        
        # Tax #1: Open Shot Dependency (50% reduction)
        if 'RS_OPEN_SHOT_FREQUENCY' in df.columns:
            # Phase 3.8 Fix #2: Use STAR average (USG > 20%) for threshold
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
        if 'CREATION_VOLUME_RATIO' in df.columns:
            df['CREATION_VOLUME_RATIO'] = df['CREATION_VOLUME_RATIO'] * volume_penalty
        if 'EFG_ISO_WEIGHTED' in df.columns:
            df['EFG_ISO_WEIGHTED'] = df['EFG_ISO_WEIGHTED'] * efficiency_penalty
        if 'EFG_PCT_0_DRIBBLE' in df.columns:
            df['EFG_PCT_0_DRIBBLE'] = df['EFG_PCT_0_DRIBBLE'] * efficiency_penalty
        if 'RS_PRESSURE_APPETITE' in df.columns:
            df['RS_PRESSURE_APPETITE'] = df['RS_PRESSURE_APPETITE'] * volume_penalty
        if 'LEVERAGE_USG_DELTA' in df.columns:
            df['LEVERAGE_USG_DELTA'] = df['LEVERAGE_USG_DELTA'] * volume_penalty
        
        logger.info(f"Applied Multi-Signal Tax System to base features")
        
        # ========== STEP 3: Create Interaction Terms from TRANSFORMED Values ==========
        # CRITICAL: Interaction terms must use transformed values, not raw values
        if 'USG_PCT' in df.columns:
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
                if feat1 in df.columns and feat2 in df.columns:
                    interaction_name = f'{feat1}_X_{feat2}'
                    # Use transformed values (already in df)
                    df[interaction_name] = (df[feat1].fillna(0) * df[feat2].fillna(0))
                    logger.debug(f"Created interaction term {interaction_name} from transformed values")
        
        # Define all possible features (same as train_predictive_model.py)
        # DATA LEAKAGE FIX: Removed all playoff-based features (DELTA, RESILIENCE ratios, PO_*)
        # Only using Regular Season (RS_*) features that are available at prediction time
        features = [
            'CREATION_TAX', 'CREATION_VOLUME_RATIO',
            'LEVERAGE_TS_DELTA', 'LEVERAGE_USG_DELTA',  # Clutch data is RS-only
            'CLUTCH_MIN_TOTAL', 
            'EFG_PCT_0_DRIBBLE', 'EFG_ISO_WEIGHTED',
            'QOC_TS_DELTA', 'QOC_USG_DELTA',  # RS-only
            'AVG_OPPONENT_DCS', 'MEAN_OPPONENT_DCS',
            'ELITE_WEAK_TS_DELTA', 'ELITE_WEAK_USG_DELTA',  # RS-only
            # REMOVED: 'SHOT_DISTANCE_DELTA', 'SPATIAL_VARIANCE_DELTA' (use PO data)
            # REMOVED: 'PO_EFG_BEYOND_RS_MEDIAN' (playoff feature)
            'RS_PRESSURE_APPETITE',
            'RS_PRESSURE_RESILIENCE',
            # REMOVED: 'PRESSURE_APPETITE_DELTA', 'PRESSURE_RESILIENCE_DELTA' (playoff features)
            'RS_LATE_CLOCK_PRESSURE_APPETITE',
            'RS_EARLY_CLOCK_PRESSURE_APPETITE',
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE',
            'RS_EARLY_CLOCK_PRESSURE_RESILIENCE',
            # REMOVED: All *_DELTA clock features (playoff features)
            'RS_FTr',
            # REMOVED: 'FTr_RESILIENCE' (playoff feature)
            'RS_RIM_APPETITE',
            # REMOVED: 'RIM_PRESSURE_RESILIENCE' (playoff feature)
        ]
        
        # Add Usage-Aware Features
        if 'USG_PCT' in df.columns:
            features.append('USG_PCT')
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
        
        # Add Trajectory Features
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
        
        for feat in trajectory_yoy_features + trajectory_prior_features + trajectory_age_interaction_features:
            if feat in df.columns:
                features.append(feat)
        
        # Add Gate Features (Continuous Gradients + Legacy)
        gate_features = [
            # New continuous gradient features (Phase 4.2)
            'RIM_PRESSURE_DEFICIT',
            'ABDICATION_MAGNITUDE',
            'INEFFICIENT_VOLUME_SCORE',
            'SYSTEM_DEPENDENCE_SCORE',
            'EMPTY_CALORIES_RISK',
            # Legacy features (for backward compatibility)
            'ABDICATION_RISK',
            'PHYSICALITY_FLOOR',
            'SELF_CREATED_FREQ',
            'DATA_COMPLETENESS_SCORE',
            'SAMPLE_SIZE_CONFIDENCE',
            'LEVERAGE_DATA_CONFIDENCE',
            'NEGATIVE_SIGNAL_COUNT',
        ]
        
        for feat in gate_features:
            if feat in df.columns:
                features.append(feat)
        
        # Add Previous Playoff Features (Legitimate past → future)
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
        
        for feat in prev_po_features:
            if feat in df.columns:
                features.append(feat)
        
        # Filter to existing features
        existing_features = [f for f in features if f in df.columns]
        missing_features = [f for f in features if f not in df.columns]
        if missing_features:
            logger.warning(f"Missing expected features: {len(missing_features)} features")
        
        logger.info(f"Total features available: {len(existing_features)}")
        
        X = df[existing_features].copy()
        
        # Handle NaN values (same logic as train_predictive_model.py)
        for col in X.columns:
            if X[col].isna().sum() > 0:
                if 'CLOCK' in col:
                    X[col] = X[col].fillna(0)
                elif '_YOY_DELTA' in col:
                    X[col] = X[col].fillna(0)
                elif col.startswith('PREV_'):
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
                    X[col] = X[col].fillna(0)
                elif col in ['DATA_COMPLETENESS_SCORE', 'SAMPLE_SIZE_CONFIDENCE', 'LEVERAGE_DATA_CONFIDENCE']:
                    X[col] = X[col].fillna(0)
                elif col in ['ABDICATION_RISK', 'ABDICATION_MAGNITUDE', 'PHYSICALITY_FLOOR', 'SELF_CREATED_FREQ', 
                             'NEGATIVE_SIGNAL_COUNT', 'RIM_PRESSURE_DEFICIT', 'INEFFICIENT_VOLUME_SCORE',
                             'SYSTEM_DEPENDENCE_SCORE', 'EMPTY_CALORIES_RISK']:
                    X[col] = X[col].fillna(0)
                else:
                    median_val = X[col].median()
                    X[col] = X[col].fillna(median_val)
        
        return X, existing_features

    def run_rfe(self, n_features=15):
        """Run Recursive Feature Elimination to identify top N features."""
        logger.info("=" * 80)
        logger.info(f"Running RFE with {n_features} features")
        logger.info("=" * 80)
        
        # Load and prepare data
        df = self.load_and_merge_data()
        X, feature_names = self.prepare_features(df)
        y = df['ARCHETYPE']
        
        # Encode labels
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
        
        # Initialize base estimator
        base_estimator = xgb.XGBClassifier(
            objective='multi:softprob',
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric='mlogloss',
            random_state=42
        )
        
        # Run RFE
        logger.info(f"Running RFE to select top {n_features} features...")
        rfe = RFE(
            estimator=base_estimator,
            n_features_to_select=n_features,
            step=1,
            verbose=1
        )
        
        rfe.fit(X_train, y_train)
        
        # Get selected features
        selected_features = [feature_names[i] for i in range(len(feature_names)) if rfe.support_[i]]
        selected_indices = [i for i in range(len(feature_names)) if rfe.support_[i]]
        
        logger.info(f"\nSelected {len(selected_features)} features:")
        for i, feat in enumerate(selected_features, 1):
            logger.info(f"  {i}. {feat}")
        
        # Train model with selected features
        X_train_selected = X_train.iloc[:, selected_indices]
        X_test_selected = X_test.iloc[:, selected_indices]
        
        model = xgb.XGBClassifier(
            objective='multi:softprob',
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric='mlogloss',
            random_state=42
        )
        
        model.fit(X_train_selected, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_selected)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"\nModel Accuracy with {n_features} features: {accuracy:.4f}")
        logger.info("\nClassification Report:\n" + classification_report(y_test, y_pred, target_names=le.classes_))
        
        # Feature rankings
        feature_ranking = pd.DataFrame({
            'Feature': feature_names,
            'Rank': rfe.ranking_,
            'Selected': rfe.support_
        }).sort_values('Rank')
        
        return {
            'n_features': n_features,
            'selected_features': selected_features,
            'accuracy': accuracy,
            'feature_ranking': feature_ranking,
            'model': model,
            'label_encoder': le
        }

    def compare_feature_counts(self, feature_counts=[5, 10, 15, 20, 25, 30, 40, 50]):
        """Compare accuracy across different feature counts."""
        logger.info("=" * 80)
        logger.info("Comparing Accuracy Across Different Feature Counts")
        logger.info("=" * 80)
        
        results = []
        
        for n_features in feature_counts:
            try:
                result = self.run_rfe(n_features=n_features)
                results.append({
                    'n_features': n_features,
                    'accuracy': result['accuracy'],
                    'features': result['selected_features']
                })
                logger.info(f"\n{n_features} features: {result['accuracy']:.4f} accuracy")
            except Exception as e:
                logger.error(f"Error with {n_features} features: {e}")
                continue
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame(results)
        
        # Save results
        comparison_df.to_csv(self.results_dir / "rfe_feature_count_comparison.csv", index=False)
        
        # Visualize
        plt.figure(figsize=(10, 6))
        plt.plot(comparison_df['n_features'], comparison_df['accuracy'], marker='o', linewidth=2, markersize=8)
        plt.xlabel('Number of Features', fontsize=12)
        plt.ylabel('Accuracy', fontsize=12)
        plt.title('RFE: Accuracy vs. Number of Features', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.results_dir / "rfe_accuracy_vs_features.png", dpi=300)
        logger.info(f"\nSaved visualization to {self.results_dir / 'rfe_accuracy_vs_features.png'}")
        
        # Find optimal feature count (where accuracy plateaus)
        if len(comparison_df) > 1:
            accuracies = comparison_df['accuracy'].values
            feature_counts = comparison_df['n_features'].values
            
            # Find where improvement < 0.5% per additional feature
            improvements = np.diff(accuracies)
            plateau_idx = None
            for i, improvement in enumerate(improvements):
                if improvement < 0.005:  # Less than 0.5% improvement
                    plateau_idx = i
                    break
            
            if plateau_idx is not None:
                optimal_n = feature_counts[plateau_idx + 1]
                logger.info(f"\n🎯 Optimal feature count: {optimal_n} (accuracy plateaus after this)")
            else:
                optimal_n = feature_counts[-1]
                logger.info(f"\n⚠️ Accuracy still improving. Last tested: {optimal_n} features")
        
        return comparison_df, results

    def run_detailed_rfe(self, n_features=15):
        """Run detailed RFE analysis with feature importance."""
        logger.info("=" * 80)
        logger.info(f"Running Detailed RFE Analysis ({n_features} features)")
        logger.info("=" * 80)
        
        result = self.run_rfe(n_features=n_features)
        
        # Save selected features
        selected_df = pd.DataFrame({
            'Feature': result['selected_features'],
            'Rank': range(1, len(result['selected_features']) + 1)
        })
        selected_df.to_csv(self.results_dir / f"rfe_top_{n_features}_features.csv", index=False)
        
        # Save full ranking
        result['feature_ranking'].to_csv(self.results_dir / f"rfe_full_ranking.csv", index=False)
        
        # Visualize feature importance from final model
        model = result['model']
        feature_importance = pd.DataFrame({
            'Feature': result['selected_features'],
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        plt.figure(figsize=(10, max(8, len(result['selected_features']) * 0.3)))
        sns.barplot(data=feature_importance, x='Importance', y='Feature', palette='viridis')
        plt.title(f'Feature Importance: Top {n_features} Features (RFE Selected)', fontsize=14, fontweight='bold')
        plt.xlabel('Importance', fontsize=12)
        plt.tight_layout()
        plt.savefig(self.results_dir / f"rfe_top_{n_features}_importance.png", dpi=300, bbox_inches='tight')
        
        logger.info(f"\n✅ Saved results:")
        logger.info(f"  - Selected features: {self.results_dir / f'rfe_top_{n_features}_features.csv'}")
        logger.info(f"  - Full ranking: {self.results_dir / f'rfe_full_ranking.csv'}")
        logger.info(f"  - Importance plot: {self.results_dir / f'rfe_top_{n_features}_importance.png'}")
        
        return result

if __name__ == "__main__":
    selector = RFEFeatureSelector()
    
    # Step 1: Compare different feature counts
    logger.info("\n" + "=" * 80)
    logger.info("STEP 1: Comparing Feature Counts")
    logger.info("=" * 80)
    comparison_df, all_results = selector.compare_feature_counts(feature_counts=[5, 10, 15, 20, 25, 30, 40, 50])
    
    # Step 2: Detailed analysis with top 15 features
    logger.info("\n" + "=" * 80)
    logger.info("STEP 2: Detailed Analysis (Top 15 Features)")
    logger.info("=" * 80)
    detailed_result = selector.run_detailed_rfe(n_features=15)
    
    logger.info("\n" + "=" * 80)
    logger.info("RFE Analysis Complete!")
    logger.info("=" * 80)

