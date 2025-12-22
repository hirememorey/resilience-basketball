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
            # If RFE results don't exist, we might need to rely on a default list or fail
            # For now, let's assume we can proceed if we force our critical features
            logger.warning(f"RFE results not found at {rfe_path}. Using empty base list.")
            features = []
        else:
            df_rfe = pd.read_csv(rfe_path)
            row = df_rfe[df_rfe['n_features'] == n_features]
            
            if row.empty:
                # Fallback to nearest feature count or defaults
                logger.warning(f"No RFE results found for {n_features} features. Using best available.")
                if not df_rfe.empty:
                    features_str = df_rfe.iloc[0]['features']
                    features = ast.literal_eval(features_str)
                else:
                    features = []
            else:
                # Parse the features list from string
                features_str = row.iloc[0]['features']
                features = ast.literal_eval(features_str)
        
        # [NEW] FORCE INCLUSION: The "Physics-Based Truth Tellers" (Dec 21, 2025)
        # These features are direct simulations of playoff reality, not proxies.
        # We force their inclusion because they represent our core causal hypothesis.
        # CRITICAL: Added friction coefficients to the list of features to include
        critical_features = [
            'PROJECTED_PLAYOFF_OUTPUT', # The "Remainder" after applying playoff friction.
            'PROJECTED_PLAYOFF_PPS',    # The projected efficiency component of the Remainder.
            'FRICTION_COEFF_ISO',       # The friction coefficient for isolation
            'FRICTION_COEFF_0_DRIBBLE', # The friction coefficient for off-ball
            'SHOT_QUALITY_GENERATION_DELTA', # Existing critical feature - keep.
            'HELIO_ABOVE_REPLACEMENT_VALUE' # NEW (Dec 2025): Rewards inefficient stars less than efficient ones, but rewards VOLUME.
        ]
        
        for feat in critical_features:
            if feat not in features:
                features.append(feat)
                logger.info(f"Force-included critical feature: {feat}")

        # De-duplicate in case RFE already found them
        features = sorted(list(set(features)))
        
        logger.info(f"Loaded {len(features)} RFE-selected features (including Critical Features):")
        for i, feat in enumerate(features, 1):
            logger.info(f"  {i}. {feat}")
        
        return features
    
    def load_and_merge_data(self):
        """Load features and labels, merge them into a training set (same as train_predictive_model.py)."""
        # [NEW] Physics-Based Features (Dec 21, 2025)
        # We are moving from a collection of proxy CSVs to a single, unified source of truth.
        feature_path = self.results_dir / "predictive_dataset_with_friction.csv"
        if not feature_path.exists():
            # Fallback to the old file if the new one doesn't exist yet (for CI/CD or partial runs)
            old_feature_path = self.results_dir / "predictive_dataset.csv"
            logger.warning(f"Unified features file with friction not found at {feature_path}.")
            if old_feature_path.exists():
                logger.warning(f"Falling back to {old_feature_path}. Friction features will be missing.")
                feature_path = old_feature_path
            else:
                raise FileNotFoundError(f"No features file found. Please run 'evaluate_plasticity_potential.py' first.")
                
        df_features = pd.read_csv(feature_path)
        logger.info(f"Loaded Unified Features from {feature_path}: {len(df_features)} rows.")
        
        # Targets
        target_path = self.results_dir / "resilience_archetypes.csv"
        if not target_path.exists():
            raise FileNotFoundError(f"Target labels not found at {target_path}")
        df_targets = pd.read_csv(target_path)
        
        # Merge targets into the unified feature set
        df_targets.columns = [c.upper() for c in df_targets.columns]
        
        df_merged = pd.merge(
            df_features,
            df_targets[['PLAYER_NAME', 'SEASON', 'ARCHETYPE', 'RESILIENCE_QUOTIENT', 'DOMINANCE_SCORE', 'PO_MINUTES_TOTAL']],
            on=['PLAYER_NAME', 'SEASON'],
            how='inner'
        )
        
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
                elif col == 'PROJECTED_USAGE_PPS' or col == 'PROJECTED_PLAYOFF_OUTPUT' or col == 'PROJECTED_PLAYOFF_PPS':
                    # PROJECTED_USAGE_PPS and variants are critical features, 0 is a safe floor (meaning no contribution)
                    X[col] = X[col].fillna(0)
                else:
                    median_val = X[col].median()
                    X[col] = X[col].fillna(median_val)
        
        return X, existing_features

    def _calculate_synthetic_crucible_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculates the Synthetic Crucible Score for players without playoff experience.
        This score is a composite of performance in high-stress regular season contexts.
        
        De-Risking Strategies:
        1. Bayesian Shrinkage: Small sample metrics are shrunk towards a neutral baseline.
        2. Role Player Bias Mitigation: Score is scaled by creation volume.
        """
        logger.info("  Calculating Synthetic Crucible Score (v2)...")
        
        # Component 1: Hostility (Performance vs. Top Defenses)
        # ELITE_WEAK_TS_DELTA is ideal: Perf vs Top 10 Defenses - Perf vs Bottom 10
        hostility_proxy = df.get('ELITE_WEAK_TS_DELTA', 0).fillna(0)
        
        # Component 2: Friction (Late Clock Efficiency)
        friction_proxy = df.get('RS_LATE_CLOCK_PRESSURE_RESILIENCE', 0).fillna(0)
        
        # Component 3: Stakes (Clutch Experience)
        stakes_proxy = df.get('CLUTCH_MIN_TOTAL', 0).fillna(0)
        
        # --- Normalization (0 to 1 scale) ---
        def robust_normalize(series):
            min_val = series.quantile(0.05)
            max_val = series.quantile(0.95)
            if (max_val - min_val) == 0: return pd.Series(0.5, index=series.index)
            return ((series - min_val) / (max_val - min_val)).clip(0, 1)

        norm_hostility = robust_normalize(hostility_proxy)
        norm_friction = robust_normalize(friction_proxy)
        norm_stakes = robust_normalize(stakes_proxy)
        
        # --- De-Risking: Bayesian Shrinkage on Friction ---
        # We can't trust late-clock eFG% on a tiny sample.
        # We'll use RS_LATE_CLOCK_PRESSURE_APPETITE as a proxy for shot volume.
        late_clock_attempts_proxy = df.get('RS_LATE_CLOCK_PRESSURE_APPETITE', 0).fillna(0) * df.get('TOTAL_FGA', 100).fillna(100)
        
        k = 20  # The "skepticism constant" or "burden of proof" (20 shots)
        
        friction_confidence = (late_clock_attempts_proxy / (late_clock_attempts_proxy + k)).fillna(0)
        
        # Shrink towards the 50th percentile (0.5, since it's normalized)
        weighted_friction = (norm_friction * friction_confidence) + (0.5 * (1 - friction_confidence))
        logger.info(f"    - Applied Bayesian Shrinkage to friction proxy (avg confidence: {friction_confidence.mean():.2f})")

        # --- Composite Score Calculation (Weighted Average) ---
        # Hostility (40%), Friction (40%), Stakes (20%)
        weights = {'hostility': 0.4, 'friction': 0.4, 'stakes': 0.2}
        
        synthetic_raw = (
            norm_hostility * weights['hostility'] +
            weighted_friction * weights['friction'] +
            norm_stakes * weights['stakes']
        )
        
        # --- De-Risking: Role Player Bias Mitigation ---
        # Scale the score by creation volume. We want engines, not passengers.
        # Use sqrt to dampen the effect of extreme creation volume.
        creation_volume = df.get('CREATION_VOLUME_RATIO', 0.5).fillna(0.5)
        responsibility_scalar = np.sqrt(creation_volume.clip(0.1, 1.0)) # Clip to avoid penalizing rookies too much
        
        final_score = (synthetic_raw * responsibility_scalar).fillna(0)
        logger.info(f"    - Final Synthetic Score (avg: {final_score.mean():.3f}) scaled by Creation Volume")
        
        return final_score

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
        logger.info("Calculating Crucible Weights for asymmetric loss...")

        #
        # Phase 5: Crucible-Weighted Training (Dec 21, 2025)
        # Principle: "Resilience is only observable under Load."
        # Weight samples based on the hostility of the environment (Crucible Factor).
        #
        
        # 1. Get required data from the training set dataframe
        df_train = df.loc[train_indices].copy()
        
        # 2. Calculate individual weight components
        
        # Component 1: Playoff Experience (IsPlayoff * 2.0)
        # Use po_minutes_total > 0 as a reliable indicator of playoff participation
        is_playoff = df_train.get('PO_MINUTES_TOTAL', 0) > 0
        playoff_weight = is_playoff.astype(float) * 2.0
        
        # Component 2: Opponent Quality (OpponentDCS_Normalized * 1.5)
        # Normalize opponent defensive context score (DCS) from 0 to 1
        opp_dcs = df_train.get('MEAN_OPPONENT_DCS', pd.Series(df['MEAN_OPPONENT_DCS'].median(), index=df_train.index))
        opp_dcs_min = df['MEAN_OPPONENT_DCS'].min()
        opp_dcs_max = df['MEAN_OPPONENT_DCS'].max()
        
        # De-Risking: Handle division by zero if all values are the same
        if (opp_dcs_max - opp_dcs_min) > 0:
            opp_dcs_normalized = (opp_dcs - opp_dcs_min) / (opp_dcs_max - opp_dcs_min)
        else:
            opp_dcs_normalized = pd.Series(0.5, index=df_train.index) # Neutral weight if no variance
            
        opponent_quality_weight = opp_dcs_normalized.fillna(0.5) * 1.5 # Fill NaNs with median
        
        # Component 3: Clutch Minutes (IsClutch * 0.5)
        # Define "Clutch" as having played > 0 clutch minutes
        is_clutch = df_train.get('CLUTCH_MIN_TOTAL', 0) > 0
        clutch_weight = is_clutch.astype(float) * 0.5
        
        # De-Risking Strategy 1: The "Rookie Blindspot" (Synthetic Crucible V2)
        # For players with no playoff data, we must construct a "Proxy Stress" score.
        # This replaces the simple binary flag with a continuous gradient.
        has_no_playoff_data = ~is_playoff
        
        synthetic_crucible_score = self._calculate_synthetic_crucible_score(df_train)
        
        # The score modulates the boost. A score of 0.5 results in a 1.5x weight.
        # We multiply by 2.0 to give it a similar impact range as the playoff boost.
        synthetic_crucible_weight = (has_no_playoff_data * synthetic_crucible_score * 2.0)
        
        # 3. Calculate Final Crucible Weight
        # Weight = Base (1.0) + Playoff + Opponent Quality + Clutch + Synthetic Crucible
        base_weight = 1.0
        crucible_weights = base_weight + playoff_weight + opponent_quality_weight + clutch_weight + synthetic_crucible_weight
        
        # De-Risking Strategy 2: The "Variance Trap" (Weight Clipping)
        # Cap the maximum sample weight to prevent outliers from dominating.
        max_weight_clip = 4.0
        crucible_weights = crucible_weights.clip(upper=max_weight_clip)
        
        # De-Risking Strategy 3: The "Base Load" Guarantee
        # Ensure the minimum weight is not zero, so all samples contribute something.
        min_weight_floor = 0.5
        crucible_weights = crucible_weights.clip(lower=min_weight_floor)
        
        # De-Risking Strategy 4: The "Clutch Merchant" Trap (Efficiency Gating)
        # Only apply clutch weight boost if the player's clutch performance was efficient.
        # LEVERAGE_TS_DELTA > 0 is a good proxy for efficient clutch performance.
        leverage_ts_delta = df_train.get('LEVERAGE_TS_DELTA', 0)
        is_efficient_clutch = leverage_ts_delta > 0
        
        # Remove the clutch weight for inefficient clutch players
        crucible_weights.loc[is_clutch & ~is_efficient_clutch] -= 0.5
        
        sample_weights = crucible_weights
        
        logger.info(f"  Crucible Weights Calculated:")
        logger.info(f"    - Mean Weight: {sample_weights.mean():.2f}")
        logger.info(f"    - Max Weight (Clipped): {sample_weights.max():.2f}")
        logger.info(f"    - Min Weight (Floored): {sample_weights.min():.2f}")
        logger.info(f"    - Players with Playoff Boost: {is_playoff.sum()}")
        logger.info(f"    - Players with Synthetic Crucible Boost: {synthetic_crucible_weight.sum()}")
        logger.info(f"    - Players with Efficient Clutch Boost: {(is_clutch & is_efficient_clutch).sum()}")
        
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
        logger.info("Training model with Crucible sample weighting...")
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
    
    # Train with top 10 features (will actually be ~16 with force-included features)
    model, le, accuracy, importance = trainer.train(n_features=15)
    
    logger.info(f"\n✅ Model trained with features")
    logger.info(f"✅ Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"✅ Model saved to: models/resilience_xgb_rfe_15.pkl")
