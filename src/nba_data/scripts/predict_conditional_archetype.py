"""
Phase 2: Conditional Prediction Function (Enhanced with Phase 3.5, 3.6, 3.7 & 3.8 Fixes)

This script provides a function to predict archetype at different usage levels.
This enables answering both questions:
1. "What would this player's archetype be at their current usage?" (Use Case A)
2. "What would this player's archetype be at 25% usage?" (Use Case B - Latent Star Detection)

Phase 3.5 Enhancements (First Principles Fixes):
- Fix #1: Fragility Gate - Use RS_RIM_APPETITE (absolute volume) instead of RIM_PRESSURE_RESILIENCE (ratio)
- Fix #2: Projected Volume Features - Simulate usage scaling instead of linear scaling
- Fix #3: Context-Adjusted Efficiency - Usage-scaled system merchant penalty (requires RS_CONTEXT_ADJUSTMENT data)

Phase 3.6 Enhancements (First Principles Physics Fixes):
- Fix #1: Flash Multiplier - Detect elite efficiency on low volume → project to star-level volume
- Fix #2: Playoff Translation Tax - Heavily penalize open shot reliance (simulate playoff defense)
- Fix #3: Bag Check Gate - Cap players lacking self-created volume at Bulldozer (cannot be King)

Phase 3.7 Enhancements (Refinements Based on User Feedback):
- Fix #1: Linear Tax Fallacy - Move Playoff Translation Tax from efficiency to volume (system merchants lose opportunity, not just efficiency)
- Fix #2: Narrow Flash Problem - Widen Flash Multiplier to include Pressure Resilience (not just isolation efficiency)

Phase 3.8 Enhancements (Reference Class Calibration Fixes):
- Fix #1: Qualified Percentiles - Filter by volume (FGA > 200 or pressure shots > 50) before calculating percentiles to avoid small sample noise
- Fix #2: STAR Average for Tax - Use STAR_AVG_OPEN_FREQ (Usage > 20%) instead of LEAGUE_AVG for Playoff Translation Tax comparison
- Fix #3: Improved Bag Check Proxy - Better heuristic when ISO/PNR data is missing (check high creation vol + low ISO efficiency pattern)
"""

import pandas as pd
import numpy as np
import joblib
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Tuple, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConditionalArchetypePredictor:
    """Predict archetype at different usage levels using usage-aware model."""
    
    def __init__(self, use_rfe_model: bool = True):
        """
        Initialize predictor with RFE-simplified model or full model.
        
        Args:
            use_rfe_model: If True, use RFE-selected 10-feature model (default: True)
        """
        self.results_dir = Path("results")
        self.models_dir = Path("models")
        self.data_dir = Path("data")
        self.db_path = self.data_dir / "nba_stats.db"
        self.use_rfe_model = use_rfe_model
        self.dep_model = None
        self.dep_thresholds = {}
        self.performance_thresholds = {}
        
        # Load model and encoder
        if use_rfe_model:
            # Prefer Phoenix (15-feature) bundle when available to ensure selected_features are present
            phoenix_path = self.models_dir / "resilience_xgb_rfe_phoenix.pkl"
            model_path = phoenix_path if phoenix_path.exists() else self.models_dir / "resilience_xgb_rfe_10.pkl"
            
            if not model_path.exists():
                logger.warning(f"RFE model not found at {model_path}, falling back to full model")
                model_path = self.models_dir / "resilience_xgb.pkl"
                self.use_rfe_model = False

            try:
                # Load model, encoder, and selected features from single pkl
                model_data = joblib.load(model_path)
                
                if isinstance(model_data, dict) and 'model' in model_data:
                    self.model = model_data.get('model')
                    self.dep_model = model_data.get('dependence_model')
                    self.dep_thresholds = model_data.get('dependence_thresholds', {})
                    self.performance_thresholds = model_data.get('performance_thresholds', {})
                    self.label_encoder = model_data.get('label_encoder')
                    self.selected_features = model_data.get('selected_features')
                    logger.info(f"Successfully loaded RFE model bundle from {model_path}")
                else:
                    # Legacy: File is just the model object
                    self.model = model_data
                    self.dep_model = None
                    self.dep_thresholds = {}
                    # Try to load separate encoder file
                    encoder_path = self.models_dir / "archetype_encoder_rfe_10.pkl"
                    if encoder_path.exists():
                        self.label_encoder = joblib.load(encoder_path)
                    else:
                        logger.warning(f"Label encoder not found at {encoder_path}")
                        self.label_encoder = None
                    self.selected_features = None # Will need to infer or use default
                    logger.info(f"Successfully loaded legacy RFE model from {model_path}")

                if self.selected_features:
                    logger.info(f"Model configured with {len(self.selected_features)} features.")
                else:
                    logger.error("Loaded model bundle is missing selected_features; predictions will fail without them.")
                    raise ValueError("selected_features not found in model bundle")
            except Exception as e:
                logger.error(f"Error loading RFE model from {model_path}: {e}")
                raise

        else:
            model_path = self.models_dir / "resilience_xgb.pkl"

            if not model_path.exists():
                logger.error(f"Full model not found at {model_path}. Run train_predictive_model.py first.")
                raise FileNotFoundError(f"Full model not found at {model_path}")

            self.model = joblib.load(model_path)
            self.dep_model = None
            self.dep_thresholds = {}
            # Full model might not have encoder/features bundled, handle this gracefully
            self.label_encoder = None
            self.selected_features = None
            logger.info(f"Successfully loaded full model from {model_path}")

        # Load all datasets
        self.df_features = self.load_dataset("predictive_dataset.csv", "features")
        self.df_pressure = self.load_dataset("pressure_features.csv", "pressure")
        self.df_physicality = self.load_dataset("physicality_features.csv", "physicality")
        self.df_rim = self.load_dataset("rim_pressure_features.csv", "rim pressure")
        self.df_trajectory = self.load_dataset("trajectory_features.csv", "trajectory")
        self.df_gate = self.load_dataset("gate_features.csv", "gate")
        self.df_prev_po = self.load_dataset("previous_playoff_features.csv", "previous playoff")

        self.full_dataset = self.merge_all_data()
        
        # Calculate feature distributions for Phase 3 fixes
        self._calculate_feature_distributions()
        
        # PHASE 3 FINAL FIXES: Add DEPENDENCE_SCORE diagnostic check
        self._check_dependence_score_coverage()
        
        if self.selected_features:
            logger.info(f"Model expects {len(self.selected_features)} features")
        else:
            logger.info("Model loaded without explicit feature list (Legacy mode)")

    def load_dataset(self, filename: str, name: str) -> Optional[pd.DataFrame]:
        """Load a dataset from the results directory."""
        path = self.results_dir / filename
        if path.exists():
            logger.info(f"Loading {name} data from {path}...")
            return pd.read_csv(path)
        logger.warning(f"{name} data not found at {path}.")
        return None

    def merge_all_data(self) -> pd.DataFrame:
        """Merge all loaded dataframes into a single comprehensive dataframe."""
        if self.df_features is None:
            raise ValueError("Base features (predictive_dataset.csv) are required.")

        df = self.df_features.copy()
        
        # List of dataframes to merge
        datasets_to_merge = [
            (self.df_pressure, ['PLAYER_ID', 'SEASON']),
            (self.df_physicality, ['PLAYER_NAME', 'SEASON']),
            (self.df_rim, ['PLAYER_NAME', 'SEASON']),
            (self.df_trajectory, ['PLAYER_ID', 'SEASON']),
            (self.df_gate, ['PLAYER_ID', 'SEASON']),
            (self.df_prev_po, ['PLAYER_ID', 'PLAYER_NAME', 'SEASON'])
        ]
        
        for dataset, on_cols in datasets_to_merge:
            if dataset is not None:
                # Ensure merge keys exist in both dataframes
                valid_on_cols = [col for col in on_cols if col in df.columns and col in dataset.columns]
                if not valid_on_cols:
                    logger.warning(f"Skipping merge for a dataset due to missing key columns: {on_cols}")
                    continue

                # To handle potential duplicate columns (e.g., PLAYER_NAME)
                dataset_cols = valid_on_cols + [col for col in dataset.columns if col not in df.columns]
                
                df = pd.merge(df, dataset[dataset_cols], on=valid_on_cols, how='left')

        # DATA COMPLETENESS FIX: Normalize USG_PCT from percentage to decimal format (if it exists)
        if 'USG_PCT' in df.columns and df['USG_PCT'].max() > 1.0:
            df['USG_PCT'] = df['USG_PCT'] / 100.0
            logger.info("Normalized USG_PCT from percentage to decimal format in feature dataset")

        return df
    
    def get_player_data(self, player_name: str, season: str) -> Optional[Dict]:
        """Get a single row of player data for prediction."""
        
        # Find player in the merged dataset
        player_data = self.full_dataset[
            (self.full_dataset['PLAYER_NAME'].str.lower() == player_name.lower()) &
            (self.full_dataset['SEASON'] == season)
        ]
        
        if player_data.empty:
            return None
        
        return player_data.iloc[0].to_dict()

    def _calculate_feature_distributions(self):
        """Calculate and store key feature distributions needed for Phase 3 fixes."""
        logger.info("Calculating feature distributions for dynamic adjustments...")
        
        # Phase 3.8 Fix: Filter to qualified players for percentile calculations
        # This avoids small sample size players from skewing the distribution
        qualified_mask = (
            (self.full_dataset.get('RS_TOTAL_VOLUME', 0) >= 50) | 
            (self.full_dataset.get('TOTAL_FGA', 0) >= 200)
        ) & (self.full_dataset.get('USG_PCT', 0) >= 0.10)
        
        qualified_df = self.full_dataset[qualified_mask]
        logger.info(f"Qualified players: {len(qualified_df)} / {len(self.full_dataset)} (filtered by volume thresholds)")
        
        # Store distributions in a dictionary for easy access
        self.dist = {}
        
        # RS_RIM_APPETITE (for Fragility Gate)
        if 'RS_RIM_APPETITE' in qualified_df.columns:
            self.dist['rim_appetite_20th'] = qualified_df['RS_RIM_APPETITE'].quantile(0.20)
            logger.info(f"RS_RIM_APPETITE bottom 20th percentile (qualified): {self.dist['rim_appetite_20th']:.4f}")
        
        # CREATION_VOLUME_RATIO (for Flash Multiplier)
        if 'CREATION_VOLUME_RATIO' in qualified_df.columns:
            self.dist['creation_vol_25th'] = qualified_df['CREATION_VOLUME_RATIO'].quantile(0.25)
            logger.info(f"CREATION_VOLUME_RATIO 25th percentile (qualified): {self.dist['creation_vol_25th']:.4f}")
            
        # CREATION_TAX and EFG_ISO_WEIGHTED (for Flash Multiplier and Bag Check)
        if 'CREATION_TAX' in qualified_df.columns:
            self.dist['creation_tax_80th'] = qualified_df['CREATION_TAX'].quantile(0.80)
            logger.info(f"CREATION_TAX 80th percentile (qualified): {self.dist['creation_tax_80th']:.4f}")
        
        if 'EFG_ISO_WEIGHTED' in qualified_df.columns:
            self.dist['efg_iso_80th'] = qualified_df['EFG_ISO_WEIGHTED'].quantile(0.80)
            self.dist['efg_iso_25th'] = qualified_df['EFG_ISO_WEIGHTED'].quantile(0.25)
            self.dist['efg_iso_50th'] = qualified_df['EFG_ISO_WEIGHTED'].median()
            logger.info(f"EFG_ISO_WEIGHTED 80th percentile (qualified): {self.dist['efg_iso_80th']:.4f}")
            logger.info(f"EFG_ISO_WEIGHTED 25th percentile (inefficiency floor): {self.dist['efg_iso_25th']:.4f}")
            logger.info(f"EFG_ISO_WEIGHTED 50th percentile (median): {self.dist['efg_iso_50th']:.4f}")
            
        # RS_PRESSURE_RESILIENCE (for Flash Multiplier - Phase 3.7 Fix #2)
        if 'RS_PRESSURE_RESILIENCE' in qualified_df.columns:
            # Additional filter for pressure data to ensure meaningful sample
            pressure_qualified_df = qualified_df[qualified_df.get('RS_TOTAL_VOLUME', 0) >= 50]
            if len(pressure_qualified_df) > 0:
                self.dist['pressure_resilience_80th'] = pressure_qualified_df['RS_PRESSURE_RESILIENCE'].quantile(0.80)
                logger.info(f"RS_PRESSURE_RESILIENCE 80th percentile (qualified, min 50 pressure shots): {self.dist['pressure_resilience_80th']:.4f}")

        # EMPTY_CALORIES_RISK threshold (for Bag Check - Phase 3.8 Fix #3)
        # Using a fallback since SHOT_QUALITY_GENERATION_DELTA is not yet integrated
        try:
            self.dist['empty_calories_threshold'] = qualified_df['SHOT_QUALITY_GENERATION_DELTA'].quantile(0.25)
        except (KeyError, AttributeError):
            self.dist['empty_calories_threshold'] = -0.05
            logger.warning(f"Missing SQ_DELTA or USG_PCT columns, using fallback threshold: {self.dist['empty_calories_threshold']:.4f}")

        # RS_OPEN_SHOT_FREQUENCY (for Playoff Translation Tax - Phase 3.8 Fix #2)
        if 'RS_OPEN_SHOT_FREQUENCY' in self.full_dataset.columns:
            star_df = self.full_dataset[self.full_dataset.get('USG_PCT', 0) > 0.20]
            if not star_df.empty:
                self.dist['star_open_shot_freq_mean'] = star_df['RS_OPEN_SHOT_FREQUENCY'].mean()
                self.dist['star_open_shot_freq_75th'] = star_df['RS_OPEN_SHOT_FREQUENCY'].quantile(0.75)
                logger.info(f"STAR average RS_OPEN_SHOT_FREQUENCY (Usage > 20%): {self.dist['star_open_shot_freq_mean']:.4f}")
                logger.info(f"RS_OPEN_SHOT_FREQUENCY 75th percentile (STARS, USG > 20%): {self.dist['star_open_shot_freq_75th']:.4f}")
        
        # RS_PRESSURE_APPETITE (for Playoff Translation Tax)
        if 'RS_PRESSURE_APPETITE' in self.full_dataset.columns:
            star_df = self.full_dataset[self.full_dataset.get('USG_PCT', 0) > 0.20]
            if not star_df.empty:
                self.dist['star_pressure_appetite_40th'] = star_df['RS_PRESSURE_APPETITE'].quantile(0.40)
                logger.info(f"RS_PRESSURE_APPETITE 40th percentile (STARS, USG > 20%): {self.dist['star_pressure_appetite_40th']:.4f}")

        # TWO DOORS TO STARDOM: Creator-only percentiles (USG >= 20%) for routing
        creator_df = self.full_dataset[self.full_dataset.get('USG_PCT', 0) >= 0.20]
        if not creator_df.empty:
            if 'RS_RIM_APPETITE' in creator_df.columns:
                self.dist['rim_appetite_60th'] = creator_df['RS_RIM_APPETITE'].quantile(0.60)
                self.dist['rim_appetite_70th'] = creator_df['RS_RIM_APPETITE'].quantile(0.70)
                self.dist['rim_appetite_80th'] = creator_df['RS_RIM_APPETITE'].quantile(0.80)
                logger.info(f"Calculated RS_RIM_APPETITE 60/70/80 percentiles for Router (creators): {self.dist['rim_appetite_60th']:.4f} / {self.dist['rim_appetite_70th']:.4f} / {self.dist['rim_appetite_80th']:.4f}")
            if 'CREATION_TAX' in creator_df.columns:
                self.dist['creation_tax_75th'] = creator_df['CREATION_TAX'].quantile(0.75)
                logger.info(f"Calculated CREATION_TAX 75th percentile for Router (creators): {self.dist['creation_tax_75th']:.4f}")
            if 'EFG_ISO_WEIGHTED' in creator_df.columns:
                self.dist['efg_iso_35th'] = creator_df['EFG_ISO_WEIGHTED'].quantile(0.35)
                self.dist['efg_iso_15th'] = creator_df['EFG_ISO_WEIGHTED'].quantile(0.15)
                logger.info(f"Calculated EFG_ISO 35th/15th percentiles for path gates: {self.dist['efg_iso_35th']:.4f} / {self.dist['efg_iso_15th']:.4f}")

    def _determine_validation_path(self, player_data: pd.Series) -> str:
        """
        Route player through Physicality or Skill path using creator percentiles.
        """
        rim_threshold = self.dist.get('rim_appetite_60th', 0.28)  # fallback ~60th creators
        tax_threshold = self.dist.get('creation_tax_75th', -0.05)  # fallback ~75th creators

        rim_appetite = player_data.get('RS_RIM_APPETITE', 0)
        creation_tax = player_data.get('CREATION_TAX', 0)

        if pd.notna(rim_appetite) and rim_appetite > rim_threshold:
            logger.info(f"  Validation Path: PHYSICALITY (rim {rim_appetite:.4f} > {rim_threshold:.4f})")
            return "Physicality"

        if pd.notna(creation_tax) and creation_tax > tax_threshold:
            logger.info(f"  Validation Path: SKILL (creation_tax {creation_tax:.4f} > {tax_threshold:.4f})")
            return "Skill"

        logger.info("  Validation Path: DEFAULT")
        return "Default"

    def _apply_path_specific_gates(self, player_data: pd.Series, final_probs: Dict, path: str) -> Tuple[Dict, List[str]]:
        """
        Apply gates specific to the routed path.
        """
        flags: List[str] = []

        if path == "Physicality":
            # Relaxed inefficiency floor for uncut gems
            efg_iso = player_data.get('EFG_ISO_WEIGHTED', 0)
            relaxed_floor = self.dist.get('efg_iso_15th', 0.35)
            if pd.notna(efg_iso) and efg_iso < relaxed_floor:
                king_prob = final_probs.pop('King (Resilient Star)', 0)
                if king_prob:
                    final_probs['Bulldozer (Fragile Star)'] = final_probs.get('Bulldozer (Fragile Star)', 0) + king_prob
                    flags.append(f"PHYSICALITY GATE: Inefficiency (EFG {efg_iso:.3f} < {relaxed_floor:.3f}) -> King->Bulldozer")

            # Stricter passivity for uncut gems, with tightly scoped exemptions
            leverage_usg_delta = player_data.get('LEVERAGE_USG_DELTA', 0)
            rim_appetite = player_data.get('RS_RIM_APPETITE', 0)
            efg_iso = player_data.get('EFG_ISO_WEIGHTED', 0)
            leverage_ts_delta = player_data.get('LEVERAGE_TS_DELTA', 0)
            age = player_data.get('AGE', 99)
            dep_score = player_data.get('DEPENDENCE_SCORE', 0.5)

            rim_60 = self.dist.get('rim_appetite_60th', 0.28)
            rim_70 = self.dist.get('rim_appetite_70th', 0.32)
            efg_35 = self.dist.get('efg_iso_35th', 0.45)

            strong_rim = pd.notna(rim_appetite) and rim_appetite > rim_70
            good_efg = pd.notna(efg_iso) and efg_iso > efg_35
            young = pd.notna(age) and age < 23
            low_dep = pd.notna(dep_score) and dep_score < 0.35
            positive_leverage_ts = pd.notna(leverage_ts_delta) and leverage_ts_delta > 0

            strict_passivity_threshold = -0.02
            # Relax only when rim is strong, leverage TS is positive, and the player is either young, low-dep, or also has solid efficiency.
            if strong_rim and positive_leverage_ts and (young or low_dep or good_efg):
                strict_passivity_threshold = -0.08

            if pd.notna(leverage_usg_delta) and leverage_usg_delta < strict_passivity_threshold:
                star_prob = final_probs.pop('King (Resilient Star)', 0) + final_probs.pop('Bulldozer (Fragile Star)', 0)
                if star_prob > 0:
                    sniper = final_probs.get('Sniper (Resilient Role)', 0)
                    victim = final_probs.get('Victim (Fragile Role)', 0)
                    total = sniper + victim
                    if total > 0:
                        final_probs['Sniper (Resilient Role)'] = sniper + star_prob * (sniper / total)
                        final_probs['Victim (Fragile Role)'] = victim + star_prob * (victim / total)
                    else:
                        final_probs['Victim (Fragile Role)'] = star_prob
                    flags.append(f"PHYSICALITY GATE: Passivity (Leverage USG Delta {leverage_usg_delta:.3f} < {strict_passivity_threshold}) -> Star->Sniper/Victim")

        elif path == "Skill":
            # Stricter inefficiency floor for polished diamonds
            efg_iso = player_data.get('EFG_ISO_WEIGHTED', 0)
            strict_floor = self.dist.get('efg_iso_35th', 0.45)
            if pd.notna(efg_iso) and efg_iso < strict_floor:
                king_prob = final_probs.pop('King (Resilient Star)', 0)
                if king_prob:
                    final_probs['Bulldozer (Fragile Star)'] = final_probs.get('Bulldozer (Fragile Star)', 0) + king_prob
                    flags.append(f"SKILL GATE: Inefficiency (EFG {efg_iso:.3f} < {strict_floor:.3f}) -> King->Bulldozer")

        else:
            # Default fragility gate (legacy)
            is_fragile = player_data.get('RS_RIM_APPETITE', 1.0) < self.dist.get('rim_appetite_20th', 0.20)
            if is_fragile and ('King (Resilient Star)' in final_probs or 'Bulldozer (Fragile Star)' in final_probs):
                logger.info("  FRAGILITY GATE TRIGGERED: Capping at Sniper/Victim (low rim appetite)")
                star_prob = final_probs.pop('King (Resilient Star)', 0) + final_probs.pop('Bulldozer (Fragile Star)', 0)
                sniper = final_probs.get('Sniper (Resilient Role)', 0)
                victim = final_probs.get('Victim (Fragile Role)', 0)
                total = sniper + victim
                if total > 0:
                    final_probs['Sniper (Resilient Role)'] = sniper + star_prob * (sniper / total)
                    final_probs['Victim (Fragile Role)'] = victim + star_prob * (victim / total)
                else:
                    final_probs['Victim (Fragile Role)'] = star_prob / 2
                    final_probs['Sniper (Resilient Role)'] = star_prob / 2
                flags.append("FRAGILITY GATE: Capped at Sniper/Victim")

        # Re-normalize probabilities if they drift
        total_prob = sum(final_probs.values())
        if total_prob > 0 and abs(total_prob - 1.0) > 0.001:
            final_probs = {k: v / total_prob for k, v in final_probs.items()}

        return final_probs, flags
            
    def _check_dependence_score_coverage(self):
        """Check for DEPENDENCE_SCORE coverage in the loaded dataset."""
        if 'DEPENDENCE_SCORE' in self.full_dataset.columns:
            total_rows = len(self.full_dataset)
            valid_scores = self.full_dataset['DEPENDENCE_SCORE'].notna().sum()
            coverage = valid_scores / total_rows * 100
            logger.info(f"DEPENDENCE_SCORE diagnostic: {valid_scores}/{total_rows} ({coverage:.1f}%) successful calculations")
        else:
            logger.warning("DEPENDENCE_SCORE column not found in dataset. 2D Risk Matrix will be disabled.")
    
    def _apply_flash_multiplier(self, player_data: pd.Series, projected_features: pd.Series) -> pd.Series:
        """
        Phase 3.6, Fix #1 & 3.7, Fix #2: Flash Multiplier
        - If a player has elite efficiency signals (Creation Tax, Iso EFG, Pressure Resilience) on low volume,
        - Project their CREATION_VOLUME_RATIO to the median of star players.
        - This simulates a usage shock for hyper-efficient role players.
        """
        
        # Check if necessary features are available
        required_features = ['CREATION_VOLUME_RATIO', 'CREATION_TAX', 'EFG_ISO_WEIGHTED']
        if not all(feat in player_data and pd.notna(player_data[feat]) for feat in required_features):
            return projected_features

        # Determine if the player is a "low volume" creator
        is_low_volume = player_data['CREATION_VOLUME_RATIO'] < self.dist.get('creation_vol_25th', 0.25)
        
        # Determine if the player has "elite" efficiency signals
        is_elite_efficiency = (
            (player_data['CREATION_TAX'] > self.dist.get('creation_tax_80th', 0.05)) or
            (player_data['EFG_ISO_WEIGHTED'] > self.dist.get('efg_iso_80th', 0.52))
        )
        
        # Phase 3.7, Fix #2: Widen to include Pressure Resilience
        if 'RS_PRESSURE_RESILIENCE' in player_data and pd.notna(player_data['RS_PRESSURE_RESILIENCE']):
            is_elite_efficiency |= (player_data['RS_PRESSURE_RESILIENCE'] > self.dist.get('pressure_resilience_80th', 0.55))

        if is_low_volume and is_elite_efficiency:
            # Find the median CREATION_VOLUME_RATIO of star players (Kings/Bulldozers)
            # This is not available here, so we'll use a reasonable fallback (e.g., 65%)
            star_median_vol = 0.65
            logger.info(f"  FLASH MULTIPLIER TRIGGERED: Projecting CREATION_VOLUME_RATIO to {star_median_vol:.2f} (was {player_data['CREATION_VOLUME_RATIO']:.2f})")
            projected_features['CREATION_VOLUME_RATIO'] = star_median_vol
            
        return projected_features

    def _apply_playoff_translation_tax(self, player_data: pd.Series, projected_features: pd.Series) -> pd.Series:
        """
        Phase 3.6, Fix #2 & 3.7, Fix #1: Playoff Translation Tax
        - Simulates the tightening of defenses in the playoffs where open shots are less available.
        - Penalizes players who are overly reliant on open shots.
        - Tax is applied to VOLUME features (OPPORTUNITY), not just efficiency.
        """

        # Step 1: Check exemption (true stars have positive signals or high volume)
        is_exempt = (
            (player_data.get('LEVERAGE_USG_DELTA', 0) > 0) or
            (player_data.get('LEVERAGE_TS_DELTA', 0) > 0) or
            (player_data.get('CREATION_TAX', 0) > 0) or
            (player_data.get('CREATION_VOLUME_RATIO', 0) > 0.60)
        )
        
        if is_exempt:
            return projected_features # No tax for exempt players
        
        # Step 2: Calculate tax penalties for non-exempt players
        volume_penalty = 1.0
        efficiency_penalty = 1.0 # Phase 3.7, Fix #1: We primarily tax volume now

        # Tax #1: Open Shot Dependency (50% volume reduction)
        if 'RS_OPEN_SHOT_FREQUENCY' in player_data:
            open_freq_threshold = self.dist.get('star_open_shot_freq_75th', 0.25)
            if player_data['RS_OPEN_SHOT_FREQUENCY'] > open_freq_threshold:
                volume_penalty *= 0.50
                efficiency_penalty *= 0.50 # Keep a smaller efficiency tax
                logger.info(f"  PLAYOFF TAX (Open Shot): Applied 50% volume penalty")

        # Tax #2: Creation Efficiency Collapse (20% volume reduction)
        if player_data.get('CREATION_TAX', 0) < 0:
            volume_penalty *= 0.80
            efficiency_penalty *= 0.80

        # Tax #3: Leverage Abdication (20% volume reduction)
        if player_data.get('LEVERAGE_USG_DELTA', 0) < 0 and player_data.get('LEVERAGE_TS_DELTA', 0) < 0:
            volume_penalty *= 0.80
            efficiency_penalty *= 0.80
            
        # Tax #4: Pressure Avoidance (20% volume reduction)
        if 'RS_PRESSURE_APPETITE' in player_data:
            pressure_appetite_threshold = self.dist.get('star_pressure_appetite_40th', 0.45)
            if player_data['RS_PRESSURE_APPETITE'] < pressure_appetite_threshold:
                volume_penalty *= 0.80

        # Step 3: Apply penalties to projected features
        # Phase 3.7, Fix #1: Tax is now primarily on VOLUME features
        projected_features['CREATION_VOLUME_RATIO'] *= volume_penalty
        projected_features['RS_PRESSURE_APPETITE'] *= volume_penalty
        projected_features['LEVERAGE_USG_DELTA'] *= volume_penalty
        
        # Apply smaller tax to efficiency features
        projected_features['EFG_ISO_WEIGHTED'] *= efficiency_penalty
        projected_features['EFG_PCT_0_DRIBBLE'] *= efficiency_penalty
        
        return projected_features

    def _apply_bag_check_gate(self, player_data: pd.Series, projected_probs: Dict) -> Tuple[Dict, List[str]]:
        """
        Phase 3.6, Fix #3 & 3.8, Fix #3: Bag Check Gate
        - A player cannot be a "King" (franchise cornerstone) if they lack a foundational creation "bag".
        - This prevents over-projection of efficient role players into primary creator roles.
        """
        flags = []

        # Heuristic 1: Low self-created volume (primary check)
        low_creation_volume = player_data.get('CREATION_VOLUME_RATIO', 0) < self.dist.get('creation_vol_25th', 0.25)
        
        # Heuristic 2: Inefficient on self-created shots (secondary check)
        inefficient_creation = player_data.get('EFG_ISO_WEIGHTED', 0) < self.dist.get('efg_iso_25th', 0.40)
        
        # Heuristic 3: Empty calories (high usage but doesn't improve team offense - Phase 3.8, Fix #3)
        is_empty_calories = player_data.get('EMPTY_CALORIES_RISK', 0) > 0.5 # Using new gate feature
        
        # Heuristic 4: Missing ISO/PNR playtype data (proxy check - Phase 3.8, Fix #3)
        missing_playtype_data = (
            pd.isna(player_data.get('ISO_FREQUENCY')) or
            pd.isna(player_data.get('PNR_HANDLER_FREQUENCY'))
        )
        
        # Check for the "high volume, low efficiency" pattern if data is missing
        if missing_playtype_data:
            # If a player has high creation volume but very poor efficiency, it's a red flag
            if player_data.get('CREATION_VOLUME_RATIO', 0) > 0.50 and inefficient_creation:
                low_creation_volume = True # Treat as effectively low self-creation skill
                flags.append("BAG CHECK: High Volume, Low Efficiency (Proxy for Missing Playtype)")
        
        # Gate Condition: Player must have at least one of these to be a King
        # - Decent self-created volume
        # - Not be wildly inefficient
        # - Not be an "empty calories" scorer
        
        if (low_creation_volume and inefficient_creation) or is_empty_calories:
            if 'King (Resilient Star)' in projected_probs and projected_probs['King (Resilient Star)'] > 0:
                logger.info(f"  BAG CHECK GATE TRIGGERED: Capping at Bulldozer (Low Creation and/or Empty Calories)")
                
                # Re-distribute King probability to Bulldozer
                king_prob = projected_probs.pop('King (Resilient Star)')
                if 'Bulldozer (Fragile Star)' not in projected_probs:
                    projected_probs['Bulldozer (Fragile Star)'] = 0
                projected_probs['Bulldozer (Fragile Star)'] += king_prob
                
                # Re-normalize probabilities
                total_prob = sum(projected_probs.values())
                if total_prob > 0:
                    projected_probs = {k: v / total_prob for k, v in projected_probs.items()}
                
                flags.append("BAG CHECK: Capped at Bulldozer")
        
        return projected_probs, flags
        
    def _project_volume_features(self, player_data: Dict, target_usage: float) -> pd.Series:
        """
        Phase 3.5, Fix #2: Project volume-based features to a target usage level.
        - Uses empirical distributions where possible (e.g., from DB).
        - Falls back to linear scaling for features without clear distributions.
        """
        
        projected = pd.Series(player_data)
        current_usage = player_data.get('USG_PCT', target_usage)
        
        if current_usage == 0: return projected # Avoid division by zero
        
        scaling_factor = target_usage / current_usage

        # Features to scale
        volume_features = [
            'CREATION_VOLUME_RATIO',
            'RS_PRESSURE_APPETITE',
            'RS_LATE_CLOCK_PRESSURE_APPETITE',
            'RS_EARLY_CLOCK_PRESSURE_APPETITE',
            'RS_RIM_APPETITE'
        ]

        for feat in volume_features:
            if feat in projected and pd.notna(projected[feat]):
                projected[feat] *= scaling_factor
        
        return projected

    def _apply_context_adjustment(self, player_data: pd.Series, projected_features: pd.Series) -> pd.Series:
        """
        Phase 3.5, Fix #3: Apply context-adjusted efficiency.
        - Penalizes players who are system merchants (high dependence, high context adjustment).
        """
        
        # Check for required data
        if 'DEPENDENCE_SCORE' not in player_data or 'RS_CONTEXT_ADJUSTMENT' not in player_data:
            return projected_features
            
        dependence = player_data['DEPENDENCE_SCORE']
        context_adj = player_data['RS_CONTEXT_ADJUSTMENT']
        
        # System Merchant profile: High dependence AND high context adjustment
        if dependence > 0.75 and context_adj > 0.05:
            penalty = 1.0 - (context_adj * dependence) # Max penalty of ~25%
            logger.info(f"  CONTEXT ADJUSTMENT: Applying {penalty:.2f}x efficiency penalty (System Merchant)")
            
            efficiency_features = ['EFG_ISO_WEIGHTED', 'EFG_PCT_0_DRIBBLE', 'LEVERAGE_TS_DELTA']
            for feat in efficiency_features:
                if feat in projected_features:
                    projected_features[feat] *= penalty
                    
        return projected_features

    def prepare_features_for_prediction(
        self, 
        player_data: Dict, 
        target_usage: float,
        apply_phase3_fixes: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Prepare a single row of features for prediction, applying Phase 3 dynamic adjustments.
        """
        
        # Convert dict to Series for easier manipulation
        player_series = pd.Series(player_data)
        
        # --- PHASE 3 DYNAMIC ADJUSTMENTS ---
        if apply_phase3_fixes:
            # Step 1: Project volume features to target usage
            projected_features = self._project_volume_features(player_data, target_usage)
            
            # Step 2: Apply Flash Multiplier (modifies projected CREATION_VOLUME_RATIO)
            projected_features = self._apply_flash_multiplier(player_series, projected_features)
            
            # Step 3: Apply Playoff Translation Tax (modifies multiple projected features)
            projected_features = self._apply_playoff_translation_tax(player_series, projected_features)
            
            # Step 4: Apply Context Adjustment (modifies projected efficiency)
            projected_features = self._apply_context_adjustment(player_series, projected_features)
            
            # Update the player_series with the dynamically adjusted features
            player_series.update(projected_features)
        
        # --- FEATURE ENGINEERING (Interaction Terms, etc.) ---
        # This part must mirror the logic in `train_predictive_model.py`'s `prepare_features`
        
        # Ensure USG_PCT is at the target level for interaction term calculation
        player_series['USG_PCT'] = target_usage
        
        # Create interaction terms
        interaction_terms = [
            ('USG_PCT', 'CREATION_VOLUME_RATIO'),
            ('USG_PCT', 'LEVERAGE_USG_DELTA'),
            ('USG_PCT', 'RS_PRESSURE_APPETITE'),
            ('USG_PCT', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE'),
            ('USG_PCT', 'EFG_ISO_WEIGHTED')
        ]
        
        for feat1, feat2 in interaction_terms:
            if feat1 in player_series and feat2 in player_series:
                interaction_name = f'{feat1}_X_{feat2}'
                player_series[interaction_name] = player_series[feat1] * player_series[feat2]

        # Additional interactions used in training (inefficiency and floor emphasis)
        if 'USG_PCT' in player_series and 'INEFFICIENT_VOLUME_SCORE' in player_series:
            player_series['USG_PCT_X_INEFFICIENT_VOLUME_SCORE'] = player_series['USG_PCT'] * player_series['INEFFICIENT_VOLUME_SCORE']

        if 'USG_PCT' in player_series and 'TS_FLOOR_GAP' in player_series:
            player_series['USG_PCT_X_TS_FLOOR_GAP'] = player_series['USG_PCT'] * player_series['TS_FLOOR_GAP']

        # Clutch-floor interaction (mirrors training): normalized clutch minutes × floor gap
        if 'CLUTCH_MIN_TOTAL' in player_series and 'TS_FLOOR_GAP' in player_series:
            clutch_norm = player_series['CLUTCH_MIN_TOTAL'] / 60.0  # tighter scale to amplify signal
            player_series['CLUTCH_X_TS_FLOOR_GAP'] = clutch_norm * player_series['TS_FLOOR_GAP']

        # Usage-weighted TS expectation gap
        if 'USG_PCT' in player_series and 'TS_PCT_VS_USAGE_BAND_EXPECTATION' in player_series:
            player_series['USG_PCT_X_TS_PCT_VS_USAGE_BAND_EXPECTATION'] = (
                player_series['USG_PCT'] * player_series['TS_PCT_VS_USAGE_BAND_EXPECTATION']
            )

        if 'DEPENDENCE_SCORE' in player_series and 'INEFFICIENT_VOLUME_SCORE' in player_series:
            dep_score_clipped = float(np.clip(player_series['DEPENDENCE_SCORE'], 0.0, 1.0))
            ineff_val = float(player_series['INEFFICIENT_VOLUME_SCORE']) if pd.notna(player_series['INEFFICIENT_VOLUME_SCORE']) else 0.0
            player_series['DEPENDENCE_SCORE_X_INEFFICIENT_VOLUME_SCORE'] = dep_score_clipped * ineff_val
            player_series['INVERSE_DEPENDENCE_X_INEFFICIENT_VOLUME_SCORE'] = (1.0 - dep_score_clipped) * ineff_val

        # --- FINAL PREPARATION ---
        # Select the features the model was trained on
        if not self.selected_features:
            logger.error("No selected features found. Model was likely loaded incorrectly.")
            return None
        
        # Ensure all required features are present, fill NaNs with a safe default (0)
        features_df = pd.DataFrame([player_series])
        for col in self.selected_features:
            if col not in features_df.columns:
                features_df[col] = 0 # Add missing columns with a default value
        
        # Fill any existing NaNs in the selected feature columns
        final_features = features_df[self.selected_features].fillna(0)

        return final_features

    def predict_archetype_at_usage(
        self, 
        player_data: Dict, 
        target_usage: float, 
        apply_phase3_fixes: bool = True,
        apply_hard_gates: bool = False
    ) -> Dict:
        """
        Predict a player's archetype at a specified usage level.
        
        Args:
            player_data: A dictionary containing all features for a player-season.
            target_usage: The usage level (as a decimal, e.g., 0.25) to predict for.
            apply_phase3_fixes: Whether to apply dynamic adjustments (Flash Multiplier, etc.).
            apply_hard_gates: Whether to apply hard-coded gates post-prediction.
            
        Returns:
            A dictionary with the predicted archetype, probabilities, and confidence flags.
        """
        
        # Prepare the feature vector for the model
        features = self.prepare_features_for_prediction(player_data, target_usage, apply_phase3_fixes)
        
        if features is None:
            return {
                'archetype': 'Error',
                'probabilities': {},
                'confidence_flags': ['Feature preparation failed']
            }
        
        # Get model prediction (probabilities)
        try:
            probs = self.model.predict_proba(features)[0]
            prob_dict = {self.label_encoder.classes_[i]: prob for i, prob in enumerate(probs)}
        except Exception as e:
            logger.error(f"Error during model prediction: {e}", exc_info=True)
            logger.error(f"Features passed to model: \n{features.to_dict(orient='records')[0]}")
            return {'archetype': 'Error', 'probabilities': {}, 'confidence_flags': ['Model prediction failed']}

        # --- POST-PREDICTION GATES & ADJUSTMENTS ---
        final_probs = prob_dict.copy()
        confidence_flags = []
        
        if apply_hard_gates:
            # Determine path first for gate ordering
            validation_path = self._determine_validation_path(pd.Series(player_data))

            # Gate 1: Bag Check Gate (caps at Bulldozer) — skip for Physicality path (big/uncut gems)
            if validation_path != "Physicality":
                final_probs, bag_check_flags = self._apply_bag_check_gate(pd.Series(player_data), final_probs)
                confidence_flags.extend(bag_check_flags)
            
            # Gate 2: Path-Specific Gates
            final_probs, path_flags = self._apply_path_specific_gates(pd.Series(player_data), final_probs, validation_path)
            confidence_flags.extend(path_flags)

        # Determine final archetype from potentially modified probabilities
        predicted_archetype = max(final_probs, key=final_probs.get)

        # Add other confidence flags
        if player_data.get('SAMPLE_SIZE_CONFIDENCE', 1.0) < 0.5:
            confidence_flags.append("Low Sample Size")
        if player_data.get('LEVERAGE_DATA_CONFIDENCE', 1.0) < 0.5:
            confidence_flags.append("Low Clutch Data")
        
        return {
            'archetype': predicted_archetype,
            'probabilities': final_probs,
            'confidence_flags': confidence_flags,
            'raw_probabilities': prob_dict # For debugging
        }

    def predict_with_risk_matrix(
        self, 
        player_data: Dict, 
        target_usage: float, 
        apply_phase3_fixes: bool = True,
        apply_hard_gates: bool = False
    ) -> Dict:
        """
        Predicts player archetype and maps it to the 2D Risk Matrix.
        
        The 2D Risk Matrix evaluates players on two axes:
        1. Performance (Y-axis): The projected star-level outcome (King/Bulldozer vs Sniper/Victim).
        2. Dependence (X-axis): The player's reliance on a specific system or teammates.
        
        Returns a dictionary with the final risk category and supporting metrics.
        """
        
        # Step 1: Get the 1D performance prediction
        performance_result = self.predict_archetype_at_usage(
            player_data, 
            target_usage, 
            apply_phase3_fixes=apply_phase3_fixes,
            apply_hard_gates=apply_hard_gates
        )
        
        # Step 2: Calculate the Performance Score (Y-axis)
        # This is the combined probability of being a star-level player.
        probs = performance_result.get('probabilities', {})
        performance_score = probs.get('King (Resilient Star)', 0) + probs.get('Bulldozer (Fragile Star)', 0)
        
        # Step 3: Get the Dependence Score (X-axis) via model prediction if available
        dependence_score = None
        if hasattr(self, 'dep_model') and self.dep_model is not None:
            try:
                dep_pred = float(self.dep_model.predict(self.prepare_features_for_prediction(player_data, target_usage, apply_phase3_fixes))[0])
                dependence_score = dep_pred
            except Exception as e:
                logger.warning(f"Dependence prediction failed; falling back to player_data: {e}")
                dependence_score = player_data.get('DEPENDENCE_SCORE')
        else:
            dependence_score = player_data.get('DEPENDENCE_SCORE')

        # Step 4: Determine Risk Category based on calibrated thresholds
        thresholds = self.dep_thresholds if hasattr(self, 'dep_thresholds') else {}
        low_cut = thresholds.get('low', 0.40)
        high_cut = thresholds.get('high', 0.55)
        performance_cut = (self.performance_thresholds or {}).get('cut', 0.76)

        risk_category = "Unknown"
        if dependence_score is not None and pd.notna(dependence_score):
            if performance_score >= performance_cut and dependence_score < low_cut:
                risk_category = "Franchise Cornerstone"
            elif performance_score >= performance_cut and dependence_score >= high_cut:
                risk_category = "Luxury Component"
            elif performance_score < performance_cut and dependence_score < low_cut:
                risk_category = "Depth Piece"
            elif performance_score < performance_cut and dependence_score >= high_cut:
                risk_category = "Avoid"
            else:
                risk_category = "Depth Piece"
        else:
            # Fallback for players without dependence score
            if performance_score >= performance_cut:
                risk_category = "High Performance (Dependence Unknown)"
            else:
                risk_category = "Low Performance (Dependence Unknown)"
        
        return {
            'archetype': performance_result.get('archetype', 'Error'),
            'performance_score': performance_score,
            'dependence_score': dependence_score,
            'risk_category': risk_category,
            'probabilities': performance_result.get('probabilities', {}),
            'confidence_flags': performance_result.get('confidence_flags', [])
        }
        
    def _get_player_id_from_db(self, player_name: str) -> Optional[int]:
        """Get player ID from the database."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT PLAYER_ID FROM players WHERE PLAYER_NAME = ?", (player_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()

if __name__ == '__main__':
    # Example usage
    predictor = ConditionalArchetypePredictor(use_rfe_model=True)
    
    # Use Case A: Current Usage
    player_name = "Jalen Brunson"
    season = "2023-24"
    player_data = predictor.get_player_data(player_name, season)
    
    if player_data:
        current_usage = player_data.get('USG_PCT', 0.25)
        logger.info(f"\n--- Predicting {player_name} ({season}) at current usage ({current_usage:.2%}) ---")
        prediction = predictor.predict_with_risk_matrix(player_data, current_usage)
        logger.info(f"  Risk Category: {prediction['risk_category']}")
        logger.info(f"  Performance Score: {prediction['performance_score']:.2%}")
        logger.info(f"  Dependence Score: {prediction['dependence_score']:.2%}" if prediction['dependence_score'] is not None else "  Dependence Score: N/A")
    else:
        logger.warning(f"No data found for {player_name} in {season}")
        
    # Use Case B: Latent Star Detection (fixed high usage)
    player_name_latent = "Jalen Brunson"
    season_latent = "2020-21"
    target_usage_latent = 0.32
    player_data_latent = predictor.get_player_data(player_name_latent, season_latent)
    
    if player_data_latent:
        logger.info(f"\n--- Predicting {player_name_latent} ({season_latent}) at {target_usage_latent:.1%} usage (Latent Star Test) ---")
        prediction_latent = predictor.predict_with_risk_matrix(player_data_latent, target_usage_latent)
        logger.info(f"  Risk Category: {prediction_latent['risk_category']}")
        logger.info(f"  Performance Score: {prediction_latent['performance_score']:.2%}")
        logger.info(f"  Dependence Score: {prediction_latent['dependence_score']:.2%}" if prediction_latent['dependence_score'] is not None else "  Dependence Score: N/A")
    else:
        logger.warning(f"No data found for {player_name_latent} in {season_latent}")
