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
from pathlib import Path
from typing import Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConditionalArchetypePredictor:
    """Predict archetype at different usage levels using usage-aware model."""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.models_dir = Path("models")
        
        # Load model and encoder
        self.model = joblib.load(self.models_dir / "resilience_xgb.pkl")
        self.encoder = joblib.load(self.models_dir / "archetype_encoder.pkl")
        
        # Load feature data to get feature names and defaults
        self.df_features = self._load_features()
        
        # Get feature names from model
        if hasattr(self.model, 'feature_names_in_'):
            self.feature_names = list(self.model.feature_names_in_)
        else:
            # Fallback: use expected features
            self.feature_names = self._get_expected_features()
        
        # Calculate feature distributions for Phase 3 fixes
        self._calculate_feature_distributions()
        
        logger.info(f"Model expects {len(self.feature_names)} features")
    
    def _load_features(self) -> pd.DataFrame:
        """Load feature dataset for reference."""
        df_features = pd.read_csv(self.results_dir / "predictive_dataset.csv")
        
        # Merge with other feature files (same as training script)
        pressure_path = self.results_dir / "pressure_features.csv"
        if pressure_path.exists():
            df_pressure = pd.read_csv(pressure_path)
            df_features = pd.merge(
                df_features,
                df_pressure,
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_pressure')
            )
            cols_to_drop = [c for c in df_features.columns if '_pressure' in c]
            df_features = df_features.drop(columns=cols_to_drop)
        
        physicality_path = self.results_dir / "physicality_features.csv"
        if physicality_path.exists():
            df_physicality = pd.read_csv(physicality_path)
            df_features = pd.merge(
                df_features,
                df_physicality,
                on=['PLAYER_NAME', 'SEASON'],
                how='left',
                suffixes=('', '_phys')
            )
            cols_to_drop = [c for c in df_features.columns if '_phys' in c]
            df_features = df_features.drop(columns=cols_to_drop)
        
        rim_path = self.results_dir / "rim_pressure_features.csv"
        if rim_path.exists():
            df_rim = pd.read_csv(rim_path)
            df_features = pd.merge(
                df_features,
                df_rim,
                on=['PLAYER_NAME', 'SEASON'],
                how='left',
                suffixes=('', '_rim')
            )
            cols_to_drop = [c for c in df_features.columns if '_rim' in c]
            df_features = df_features.drop(columns=cols_to_drop)
        
        # PHASE 4: Load Trajectory Features
        trajectory_path = self.results_dir / "trajectory_features.csv"
        if trajectory_path.exists():
            df_trajectory = pd.read_csv(trajectory_path)
            df_features = pd.merge(
                df_features,
                df_trajectory,
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_traj')
            )
            cols_to_drop = [c for c in df_features.columns if '_traj' in c]
            df_features = df_features.drop(columns=cols_to_drop)
            logger.info(f"Loaded trajectory features: {len(df_trajectory)} rows")
        
        # PHASE 4: Load Gate Features
        gate_path = self.results_dir / "gate_features.csv"
        if gate_path.exists():
            df_gate = pd.read_csv(gate_path)
            df_features = pd.merge(
                df_features,
                df_gate,
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_gate')
            )
            cols_to_drop = [c for c in df_features.columns if '_gate' in c]
            df_features = df_features.drop(columns=cols_to_drop)
            logger.info(f"Loaded gate features: {len(df_gate)} rows")
        
        return df_features
    
    def _get_qualified_players(self, min_fga: int = 200, min_pressure_shots: int = 50) -> pd.DataFrame:
        """
        Filter players by volume thresholds to avoid small sample noise.
        
        Phase 3.8 Fix: Reference Class Principle - Calculate percentiles only on 
        rotation players (qualified by volume), not entire dataset including bench players.
        
        Args:
            min_fga: Minimum field goal attempts (default: 200)
            min_pressure_shots: Minimum pressure shots for pressure-related metrics (default: 50)
        
        Returns:
            DataFrame filtered to qualified players
        """
        qualified = self.df_features.copy()
        
        # Filter by FGA if available (from pressure features or other sources)
        if 'RS_TOTAL_VOLUME' in qualified.columns:
            # RS_TOTAL_VOLUME is total tracked shots - use as proxy for FGA
            qualified = qualified[qualified['RS_TOTAL_VOLUME'] >= min_pressure_shots]
        elif 'TOTAL_FGA' in qualified.columns:
            qualified = qualified[qualified['TOTAL_FGA'] >= min_fga]
        
        # Also filter by usage if available (rotation players typically have USG_PCT > 10%)
        if 'USG_PCT' in qualified.columns:
            qualified = qualified[qualified['USG_PCT'] >= 0.10]
        
        logger.info(f"Qualified players: {len(qualified)} / {len(self.df_features)} (filtered by volume thresholds)")
        return qualified
    
    def _calculate_feature_distributions(self):
        """Calculate feature distributions for Phase 3.5 & 3.6 fixes."""
        # Phase 3.8 Fix: Use qualified players (rotation players) for percentile calculations
        # This avoids small sample noise from bench players
        qualified_players = self._get_qualified_players()
        
        # Phase 3.5 Fix #1: Use RS_RIM_APPETITE (absolute volume) instead of RIM_PRESSURE_RESILIENCE (ratio)
        # Calculate bottom 20th percentile for RS_RIM_APPETITE (Fragility Gate)
        if 'RS_RIM_APPETITE' in qualified_players.columns:
            rim_appetite = qualified_players['RS_RIM_APPETITE'].dropna()
            if len(rim_appetite) > 0:
                self.rim_appetite_bottom_20th = rim_appetite.quantile(0.20)
                logger.info(f"RS_RIM_APPETITE bottom 20th percentile (qualified): {self.rim_appetite_bottom_20th:.4f}")
            else:
                self.rim_appetite_bottom_20th = None
        else:
            self.rim_appetite_bottom_20th = None
        
        # Phase 3.6 Fix #1: Flash Multiplier - Calculate percentiles for flash detection
        # Phase 3.8 Fix: Use qualified players to avoid small sample noise
        if 'CREATION_VOLUME_RATIO' in qualified_players.columns:
            creation_vol = qualified_players['CREATION_VOLUME_RATIO'].dropna()
            if len(creation_vol) > 0:
                self.creation_vol_25th = creation_vol.quantile(0.25)
                logger.info(f"CREATION_VOLUME_RATIO 25th percentile (qualified): {self.creation_vol_25th:.4f}")
            else:
                self.creation_vol_25th = None
        else:
            self.creation_vol_25th = None
        
        if 'CREATION_TAX' in qualified_players.columns:
            creation_tax = qualified_players['CREATION_TAX'].dropna()
            if len(creation_tax) > 0:
                self.creation_tax_80th = creation_tax.quantile(0.80)
                logger.info(f"CREATION_TAX 80th percentile (qualified): {self.creation_tax_80th:.4f}")
            else:
                self.creation_tax_80th = None
        else:
            self.creation_tax_80th = None
        
        if 'EFG_ISO_WEIGHTED' in qualified_players.columns:
            efg_iso = qualified_players['EFG_ISO_WEIGHTED'].dropna()
            if len(efg_iso) > 0:
                self.efg_iso_80th = efg_iso.quantile(0.80)
                logger.info(f"EFG_ISO_WEIGHTED 80th percentile (qualified): {self.efg_iso_80th:.4f}")
            else:
                self.efg_iso_80th = None
        else:
            self.efg_iso_80th = None
        
        # Phase 3.7 Fix #2: Flash Multiplier - Add RS_PRESSURE_RESILIENCE as alternative flash signal
        # Phase 3.8 Fix: Filter by pressure shot volume for pressure resilience percentile
        if 'RS_PRESSURE_RESILIENCE' in qualified_players.columns:
            # For pressure resilience, filter by minimum pressure shots (RS_TOTAL_VOLUME)
            if 'RS_TOTAL_VOLUME' in qualified_players.columns:
                pressure_qualified = qualified_players[
                    (qualified_players['RS_TOTAL_VOLUME'] >= 50) & 
                    (qualified_players['RS_PRESSURE_RESILIENCE'].notna())
                ]
            else:
                pressure_qualified = qualified_players[qualified_players['RS_PRESSURE_RESILIENCE'].notna()]
            
            pressure_resilience = pressure_qualified['RS_PRESSURE_RESILIENCE'].dropna()
            if len(pressure_resilience) > 0:
                self.pressure_resilience_80th = pressure_resilience.quantile(0.80)
                logger.info(f"RS_PRESSURE_RESILIENCE 80th percentile (qualified, min 50 pressure shots): {self.pressure_resilience_80th:.4f}")
            else:
                self.pressure_resilience_80th = None
        else:
            self.pressure_resilience_80th = None
        
        # Calculate star-level median CREATION_VOLUME_RATIO (for Flash Multiplier projection)
        if 'CREATION_VOLUME_RATIO' in self.df_features.columns and 'ARCHETYPE' in self.df_features.columns:
            star_archetypes = ['King (Resilient Star)', 'Bulldozer (Fragile Star)']
            star_players = self.df_features[self.df_features['ARCHETYPE'].isin(star_archetypes)]
            if len(star_players) > 0:
                star_creation_vol = star_players['CREATION_VOLUME_RATIO'].dropna()
                if len(star_creation_vol) > 0:
                    self.star_median_creation_vol = star_creation_vol.median()
                    logger.info(f"Star-level median CREATION_VOLUME_RATIO: {self.star_median_creation_vol:.4f}")
                else:
                    self.star_median_creation_vol = None
            else:
                self.star_median_creation_vol = None
        else:
            self.star_median_creation_vol = None
        
        # Phase 3.6 Fix #2 & Phase 3.7 Fix #1: Playoff Translation Tax - Calculate STAR average and 75th percentile
        # Phase 3.8 Fix: Use STAR_AVG_OPEN_FREQ (Usage > 20%) instead of LEAGUE_AVG
        # Phase 3.8.1 Fix: Use STARS (USG > 20%) for 75th percentile threshold, not qualified players
        # This ensures Poole is compared to other stars, not bench players who take more open shots
        self.star_avg_open_freq = None
        self.open_freq_75th = None
        # Check for RS_OPEN_SHOT_FREQUENCY (from pressure features) or OPEN_SHOT_FREQUENCY
        open_freq_col = None
        if 'RS_OPEN_SHOT_FREQUENCY' in self.df_features.columns:
            open_freq_col = 'RS_OPEN_SHOT_FREQUENCY'
        elif 'OPEN_SHOT_FREQUENCY' in self.df_features.columns:
            open_freq_col = 'OPEN_SHOT_FREQUENCY'
        
        if open_freq_col:
            # Phase 3.8 Fix: Filter to stars (Usage > 20%) for both average and 75th percentile
            if 'USG_PCT' in self.df_features.columns:
                star_players = self.df_features[self.df_features['USG_PCT'] > 0.20]
                star_open_freq = star_players[open_freq_col].dropna()
                if len(star_open_freq) > 0:
                    self.star_avg_open_freq = star_open_freq.median()
                    # Phase 3.8.1: Use stars for 75th percentile threshold (not qualified players)
                    self.open_freq_75th = star_open_freq.quantile(0.75)
                    logger.info(f"STAR average {open_freq_col} (Usage > 20%): {self.star_avg_open_freq:.4f}")
                    logger.info(f"{open_freq_col} 75th percentile (STARS, USG > 20%): {self.open_freq_75th:.4f}")
            
            # Fallback: if star data not available, use qualified players
            if self.open_freq_75th is None:
                open_freq = qualified_players[open_freq_col].dropna()
                if len(open_freq) > 0:
                    self.open_freq_75th = open_freq.quantile(0.75)
                    logger.info(f"Fallback: {open_freq_col} 75th percentile (qualified): {self.open_freq_75th:.4f}")
                if self.star_avg_open_freq is None and len(open_freq) > 0:
                    self.star_avg_open_freq = open_freq.median()
                    logger.info(f"Fallback: Using qualified players median {open_freq_col}: {self.star_avg_open_freq:.4f}")
        # If not in features, we'll calculate it on-the-fly from shot quality data if available
    
    def _get_expected_features(self) -> list:
        """Get expected feature names (fallback if model doesn't have feature_names_in_)."""
        return [
            'CREATION_TAX', 'CREATION_VOLUME_RATIO',
            'LEVERAGE_TS_DELTA', 'LEVERAGE_USG_DELTA',
            'CLUTCH_MIN_TOTAL', 
            'EFG_PCT_0_DRIBBLE', 'EFG_ISO_WEIGHTED',
            'QOC_TS_DELTA', 'QOC_USG_DELTA',
            'AVG_OPPONENT_DCS', 'MEAN_OPPONENT_DCS',
            'ELITE_WEAK_TS_DELTA', 'ELITE_WEAK_USG_DELTA',
            'SHOT_DISTANCE_DELTA',
            'SPATIAL_VARIANCE_DELTA',
            'PO_EFG_BEYOND_RS_MEDIAN',
            'RS_PRESSURE_APPETITE',
            'RS_PRESSURE_RESILIENCE',
            'PRESSURE_APPETITE_DELTA',
            'PRESSURE_RESILIENCE_DELTA',
            'RS_LATE_CLOCK_PRESSURE_APPETITE',
            'RS_EARLY_CLOCK_PRESSURE_APPETITE',
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE',
            'RS_EARLY_CLOCK_PRESSURE_RESILIENCE',
            'LATE_CLOCK_PRESSURE_APPETITE_DELTA',
            'EARLY_CLOCK_PRESSURE_APPETITE_DELTA',
            'LATE_CLOCK_PRESSURE_RESILIENCE_DELTA',
            'EARLY_CLOCK_PRESSURE_RESILIENCE_DELTA',
            'FTr_RESILIENCE',
            'RS_FTr',
            'RS_RIM_APPETITE',
            'RIM_PRESSURE_RESILIENCE',
            'USG_PCT',
            'USG_PCT_X_CREATION_VOLUME_RATIO',
            'USG_PCT_X_LEVERAGE_USG_DELTA',
            'USG_PCT_X_RS_PRESSURE_APPETITE',
            'USG_PCT_X_RS_LATE_CLOCK_PRESSURE_RESILIENCE',
            'USG_PCT_X_EFG_ISO_WEIGHTED'
        ]
    
    def get_player_data(self, player_name: str, season: str) -> Optional[pd.Series]:
        """Get player's stress vector data for a given season."""
        player_data = self.df_features[
            (self.df_features['PLAYER_NAME'] == player_name) & 
            (self.df_features['SEASON'] == season)
        ]
        
        if len(player_data) == 0:
            logger.warning(f"No data found for {player_name} {season}")
            return None
        
        return player_data.iloc[0]
    
    def prepare_features(
        self, 
        player_data: pd.Series, 
        usage_level: float,
        apply_phase3_fixes: bool = True
    ) -> Tuple[np.ndarray, Dict]:
        """
        Prepare feature vector for prediction at specified usage level.
        
        Phase 3.5 Fixes Applied:
        - Fix #2: Projected Volume Features (simulate usage scaling instead of linear scaling)
        - Fix #2 (Context): Context-Adjusted Efficiency (usage-scaled penalty)
        
        Phase 3.6 Fixes Applied:
        - Fix #1: Flash Multiplier - Detect elite efficiency on low volume → project to star-level volume
        - Fix #2: Playoff Translation Tax - Heavily penalize open shot reliance
        
        Args:
            player_data: Player's stress vector data (Series)
            usage_level: Usage percentage as decimal (e.g., 0.25 for 25%)
            apply_phase3_fixes: Whether to apply Phase 3.5 & 3.6 fixes (default: True)
        
        Returns:
            Feature array ready for model prediction
        """
        features = []
        missing_features = []
        
        # Get current usage for projection calculation
        current_usage = player_data.get('USG_PCT', usage_level)
        if pd.isna(current_usage):
            current_usage = usage_level
        
        # Phase 3.5 Fix #2: Calculate projection factor for volume features
        # Principle: Tree models make decisions based on splits. Simulate the result, don't just weight the input.
        projection_factor = 1.0
        use_projection = False
        flash_multiplier_applied = False
        if apply_phase3_fixes and usage_level > current_usage:
            projection_factor = usage_level / current_usage
            use_projection = True
            
            # Phase 3.6 Fix #1 & Phase 3.7 Fix #2: Flash Multiplier - Detect elite efficiency on low volume
            # Phase 3.7: Expanded to include Pressure Resilience as alternative flash signal
            # If player has elite efficiency on low volume, project to star-level volume (not scalar)
            creation_vol = player_data.get('CREATION_VOLUME_RATIO', 0)
            creation_tax = player_data.get('CREATION_TAX', 0)
            efg_iso = player_data.get('EFG_ISO_WEIGHTED', 0)
            pressure_resilience = player_data.get('RS_PRESSURE_RESILIENCE', 0)
            
            # Check if "Flash of Brilliance" (low volume + elite efficiency)
            is_low_volume = False
            is_elite_efficiency = False
            
            if (self.creation_vol_25th is not None and 
                pd.notna(creation_vol) and creation_vol < self.creation_vol_25th):
                is_low_volume = True
            
            # Phase 3.7 Fix #2: Expanded flash definition - ISO efficiency OR Pressure Resilience
            if (self.creation_tax_80th is not None and pd.notna(creation_tax) and creation_tax > self.creation_tax_80th):
                is_elite_efficiency = True
            elif (self.efg_iso_80th is not None and pd.notna(efg_iso) and efg_iso > self.efg_iso_80th):
                is_elite_efficiency = True
            elif (self.pressure_resilience_80th is not None and pd.notna(pressure_resilience) and 
                  pressure_resilience > self.pressure_resilience_80th):
                is_elite_efficiency = True  # NEW: Pressure Resilience as flash signal
            
            if is_low_volume and is_elite_efficiency and self.star_median_creation_vol is not None:
                # Project to star-level volume instead of scalar projection
                projection_factor = self.star_median_creation_vol / max(creation_vol, 0.001)  # Avoid division by zero
                flash_multiplier_applied = True
                logger.debug(f"Flash Multiplier applied: {creation_vol:.4f} → {self.star_median_creation_vol:.4f}")
        
        # Phase 3 Fix #2 (Context): Calculate context adjustment (if available)
        context_adjustment = 0.0
        context_penalty = 0.0
        if apply_phase3_fixes and 'RS_CONTEXT_ADJUSTMENT' in player_data.index:
            context_adjustment = player_data['RS_CONTEXT_ADJUSTMENT']
            if pd.notna(context_adjustment) and context_adjustment > 0:
                # Usage-scaled penalty: stronger at low usage, weaker at high usage
                # At 20% usage: full penalty, at 30%+ usage: minimal penalty
                if usage_level <= 0.20:
                    penalty_scale = 1.0
                elif usage_level >= 0.30:
                    penalty_scale = 0.1  # Minimal penalty at high usage
                else:
                    # Linear interpolation between 20% and 30%
                    penalty_scale = 1.0 - ((usage_level - 0.20) / (0.30 - 0.20)) * 0.9
                
                # Apply penalty to efficiency features
                # Penalize if context adjustment > 0.05 (top 10-15% as per analysis)
                if context_adjustment > 0.05:
                    context_penalty = context_adjustment * penalty_scale * 0.5  # 50% of adjustment as penalty
        
        # Phase 3.7 Fix #1: Playoff Translation Tax - Moved from efficiency to volume
        # Phase 3.6 Fix #2 (OLD): Was applied to efficiency features
        # Phase 3.7 Fix #1 (NEW): Apply to volume instead - system merchants lose opportunity, not just efficiency
        playoff_volume_tax_applied = False
        open_shot_freq = None
        if apply_phase3_fixes:
            # Try to get open shot frequency from player data (check RS_OPEN_SHOT_FREQUENCY first)
            if 'RS_OPEN_SHOT_FREQUENCY' in player_data.index:
                open_shot_freq = player_data['RS_OPEN_SHOT_FREQUENCY']
            elif 'OPEN_SHOT_FREQUENCY' in player_data.index:
                open_shot_freq = player_data['OPEN_SHOT_FREQUENCY']
            elif 'FGA_6_PLUS' in player_data.index and 'TOTAL_FGA' in player_data.index:
                # Calculate from shot quality data if available
                fga_6_plus = player_data.get('FGA_6_PLUS', 0)
                total_fga = player_data.get('TOTAL_FGA', 0)
                if pd.notna(fga_6_plus) and pd.notna(total_fga) and total_fga > 0:
                    open_shot_freq = fga_6_plus / total_fga
            elif 'RS_TOTAL_TRACKED_FGA_PER_GAME' in player_data.index:
                # Try to get from tracked FGA data
                fga_6_plus = player_data.get('FGA_6_PLUS', 0)
                total_tracked = player_data.get('RS_TOTAL_TRACKED_FGA_PER_GAME', 0)
                if pd.notna(fga_6_plus) and pd.notna(total_tracked) and total_tracked > 0:
                    open_shot_freq = fga_6_plus / total_tracked
            
            # Phase 3.7 Fix #1: Check if open shot frequency > 75th percentile (volume tax threshold)
            if pd.notna(open_shot_freq) and self.open_freq_75th is not None:
                if open_shot_freq > self.open_freq_75th:
                    playoff_volume_tax_applied = True
                    logger.debug(f"Playoff Volume Tax applied: {open_shot_freq:.4f} > {self.open_freq_75th:.4f} (75th percentile)")
            elif pd.notna(open_shot_freq):
                # Fallback: calculate 75th percentile on-the-fly if not pre-calculated
                open_freq_col = None
                if 'RS_OPEN_SHOT_FREQUENCY' in self.df_features.columns:
                    open_freq_col = 'RS_OPEN_SHOT_FREQUENCY'
                elif 'OPEN_SHOT_FREQUENCY' in self.df_features.columns:
                    open_freq_col = 'OPEN_SHOT_FREQUENCY'
                
                if open_freq_col:
                    open_freq_75th = self.df_features[open_freq_col].dropna().quantile(0.75)
                    if pd.notna(open_freq_75th) and open_shot_freq > open_freq_75th:
                        playoff_volume_tax_applied = True
                        logger.debug(f"Playoff Volume Tax applied (on-the-fly): {open_shot_freq:.4f} > {open_freq_75th:.4f}")
        
        for feature_name in self.feature_names:
            if feature_name == 'USG_PCT':
                # Use the specified usage level
                features.append(usage_level)
            elif feature_name.startswith('USG_PCT_X_'):
                # Calculate interaction term: USG_PCT * base_feature
                base_feature = feature_name.replace('USG_PCT_X_', '')
                if base_feature in player_data.index:
                    base_value = player_data[base_feature]
                    if pd.isna(base_value):
                        # If base feature is missing, set interaction to 0
                        features.append(0.0)
                    else:
                        features.append(usage_level * base_value)
                else:
                    # Base feature missing, set interaction to 0
                    features.append(0.0)
                    missing_features.append(feature_name)
            else:
                # Regular feature - use player's actual value
                if feature_name in player_data.index:
                    val = player_data[feature_name]
                    # Handle NaN
                    if pd.isna(val):
                        # PHASE 4: Special handling for trajectory and gate features
                        if '_YOY_DELTA' in feature_name:
                            # Trajectory features (YoY deltas): fill NaN with 0 (no change = neutral signal for first seasons)
                            val = 0.0
                        elif feature_name.startswith('PREV_'):
                            # Prior features: fill NaN with median (no prior = use population average)
                            if feature_name in self.df_features.columns:
                                val = self.df_features[feature_name].median()
                            else:
                                val = 0.0
                        elif 'AGE_X_' in feature_name and '_YOY_DELTA' in feature_name:
                            # Age-trajectory interactions: fill NaN with 0 (calculated after filling trajectory)
                            val = 0.0
                        elif feature_name in ['DATA_COMPLETENESS_SCORE', 'SAMPLE_SIZE_CONFIDENCE', 'LEVERAGE_DATA_CONFIDENCE']:
                            # Gate confidence features: fill NaN with 0 (no data = no confidence)
                            val = 0.0
                        elif feature_name in ['ABDICATION_RISK', 'PHYSICALITY_FLOOR', 'SELF_CREATED_FREQ', 'NEGATIVE_SIGNAL_COUNT']:
                            # Gate risk/count features: fill NaN with 0 (no risk = 0, no signals = 0)
                            val = 0.0
                        elif 'CLOCK' in feature_name:
                            # Clock features: fill NaN with 0 (neutral signal when no data)
                            val = 0.0
                        elif feature_name in self.df_features.columns:
                            # Other features: fill with median
                            val = self.df_features[feature_name].median()
                        else:
                            val = 0.0
                    
                    # Phase 3.5 Fix #2: Apply projected volume features instead of linear scaling
                    # Volume-based features: project to simulate usage scaling
                    # Efficiency features: keep as-is (they don't scale with usage)
                    if apply_phase3_fixes and use_projection:
                        # Volume-based features that should be projected
                        volume_features = [
                            'CREATION_VOLUME_RATIO',
                            'LEVERAGE_USG_DELTA',  # Usage delta scales with usage
                            'RS_PRESSURE_APPETITE',  # Pressure appetite scales with usage
                            'RS_LATE_CLOCK_PRESSURE_APPETITE',
                            'RS_EARLY_CLOCK_PRESSURE_APPETITE'
                        ]
                        
                        if feature_name in volume_features:
                            # Project volume feature: simulate what it would be at higher usage
                            val = val * projection_factor
                            
                            # Phase 3.7 Fix #1: Apply playoff volume tax to CREATION_VOLUME_RATIO
                            # System merchants lose opportunity, not just efficiency
                            if feature_name == 'CREATION_VOLUME_RATIO' and playoff_volume_tax_applied:
                                # Phase 3.8.1 Fix: Slash projected volume by 50% (multiply by 0.50) - increased from 30%
                                # System merchants lose opportunity more dramatically in playoffs
                                original_val = val
                                val = val * 0.50
                                logger.debug(f"Playoff Volume Tax: CREATION_VOLUME_RATIO reduced by 50% (from {original_val:.4f} to {val:.4f})")
                        elif feature_name in ['RS_PRESSURE_RESILIENCE', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE', 
                                             'RS_EARLY_CLOCK_PRESSURE_RESILIENCE', 'CREATION_TAX', 'EFG_ISO_WEIGHTED',
                                             'EFG_PCT_0_DRIBBLE']:
                            # Efficiency features: keep as-is, but apply context penalty if applicable
                            # Phase 3.7 Fix #1: Removed playoff tax from efficiency (moved to volume)
                            if context_penalty > 0:
                                val = max(0.0, val - context_penalty)
                        # All other features: use as-is
                    
                    features.append(val)
                else:
                    # Feature missing from player data
                    if 'CLOCK' in feature_name:
                        features.append(0.0)
                    elif feature_name in self.df_features.columns:
                        features.append(self.df_features[feature_name].median())
                    else:
                        features.append(0.0)
                    missing_features.append(feature_name)
        
        if missing_features:
            logger.debug(f"Missing features filled with defaults: {missing_features[:5]}...")
        
        # Return features and phase3 metadata
        phase3_metadata = {
            'projection_factor': projection_factor if use_projection else 1.0,
            'use_projection': use_projection,
            'flash_multiplier_applied': flash_multiplier_applied,
            'context_penalty': context_penalty,
            'context_adjustment': context_adjustment if 'RS_CONTEXT_ADJUSTMENT' in player_data.index else None,
            'playoff_volume_tax_applied': playoff_volume_tax_applied,  # Phase 3.7: Moved from efficiency to volume
            'open_shot_freq': open_shot_freq
        }
        
        return np.array(features).reshape(1, -1), phase3_metadata
    
    def predict_archetype_at_usage(
        self, 
        player_data: pd.Series, 
        usage_level: float,
        apply_phase3_fixes: bool = True
    ) -> Dict:
        """
        Predict archetype at specified usage level.
        
        Args:
            player_data: Player's stress vector data (Series)
            usage_level: Usage percentage as decimal (e.g., 0.25 for 25%)
            apply_phase3_fixes: Whether to apply Phase 3 fixes (default: True)
        
        Returns:
            Dictionary with:
            - predicted_archetype: Predicted archetype class
            - probabilities: Dict of probabilities for each archetype
            - star_level_potential: Combined King + Bulldozer probability
            - confidence_flags: List of missing data flags
        """
        # Prepare features
        features, phase3_metadata = self.prepare_features(player_data, usage_level, apply_phase3_fixes)
        
        # Store flash_multiplier_applied in player_data for use in gates
        flash_multiplier_applied = phase3_metadata.get('flash_multiplier_applied', False)
        player_data['_FLASH_MULTIPLIER_ACTIVE'] = flash_multiplier_applied
        
        # Predict
        probs = self.model.predict_proba(features)[0]
        pred_class = self.model.predict(features)[0]
        pred_archetype = self.encoder.inverse_transform([pred_class])[0]
        
        # Get probabilities for each archetype
        prob_dict = {}
        archetype_short_names = {
            'King (Resilient Star)': 'King',
            'Bulldozer (Fragile Star)': 'Bulldozer',
            'Sniper (Resilient Role)': 'Sniper',
            'Victim (Fragile Role)': 'Victim'
        }
        
        for i, archetype in enumerate(self.encoder.classes_):
            short_name = archetype_short_names.get(archetype, archetype)
            prob_dict[short_name] = probs[i]
            prob_dict[archetype] = probs[i]  # Keep full name too
        
        # Calculate star-level potential (King + Bulldozer)
        star_level_potential = prob_dict.get('King', 0) + prob_dict.get('Bulldozer', 0)
        
        # Phase 3.5 Fix #1: Fragility Gate - Use RS_RIM_APPETITE (absolute volume) instead of ratio
        # Cap star-level if RS_RIM_APPETITE is bottom 20th percentile
        # Principle: Ratios measure change, not state. Use absolute metrics for floors.
        fragility_gate_applied = False
        rim_appetite = None
        if apply_phase3_fixes and 'RS_RIM_APPETITE' in player_data.index:
            rim_appetite = player_data['RS_RIM_APPETITE']
            if pd.notna(rim_appetite) and self.rim_appetite_bottom_20th is not None:
                if rim_appetite <= self.rim_appetite_bottom_20th:
                    # Hard gate: Cap at 30% (Sniper ceiling)
                    star_level_potential = min(star_level_potential, 0.30)
                    fragility_gate_applied = True
                    # Also cap archetype probabilities - can't be King or Bulldozer
                    if star_level_potential <= 0.30:
                        # Redistribute: Victim gets remainder, Sniper gets capped amount
                        prob_dict['Sniper'] = min(prob_dict.get('Sniper', 0), 0.30)
                        prob_dict['Victim'] = 1.0 - prob_dict['Sniper']
                        prob_dict['King'] = 0.0
                        prob_dict['Bulldozer'] = 0.0
                        # Update predicted archetype if needed
                        if pred_archetype in ['King (Resilient Star)', 'Bulldozer (Fragile Star)']:
                            pred_archetype = 'Sniper (Resilient Role)' if prob_dict['Sniper'] > prob_dict['Victim'] else 'Victim (Fragile Role)'
        
        # Phase 3.6 Fix #3: Bag Check Gate - Cap players lacking self-created volume at Bulldozer (cannot be King)
        # Principle: Self-created volume is required for primary initiators (Kings)
        # Phase 3.8 Fix: Improved proxy logic when ISO/PNR data is missing
        bag_check_gate_applied = False
        self_created_freq = None
        bag_check_reason = None
        
        # Initialize new gate flags
        leverage_data_penalty_applied = False
        negative_signal_gate_applied = False
        data_completeness_gate_applied = False
        sample_size_gate_applied = False
        if apply_phase3_fixes:
            # Calculate self-created frequency (ISO + PNR Handler)
            iso_freq = player_data.get('ISO_FREQUENCY', None)
            pnr_freq = player_data.get('PNR_HANDLER_FREQUENCY', None)
            
            # Try alternative column names if primary ones don't exist
            if pd.isna(iso_freq) or iso_freq is None:
                # Phase 3.8 Fix: Better proxy when ISO/PNR data is missing
                # Check if player has high creation volume but low isolation efficiency
                # This indicates system-based creation (like Sabonis), not self-creation
                creation_vol_ratio = player_data.get('CREATION_VOLUME_RATIO', 0)
                efg_iso = player_data.get('EFG_ISO_WEIGHTED', None)
                
                if pd.notna(creation_vol_ratio) and pd.notna(efg_iso):
                    # Phase 3.8 Fix: Better heuristic for system-based creation
                    # Sabonis pattern: High CREATION_VOLUME_RATIO (0.217) but this is system-based (DHOs, cuts)
                    # Key insight: Even if ISO efficiency is decent, high creation volume without explicit ISO/PNR data
                    # suggests system-based creation (hub players like Sabonis)
                    if 'EFG_ISO_WEIGHTED' in self.df_features.columns:
                        iso_median = self.df_features['EFG_ISO_WEIGHTED'].median()
                        # More aggressive: If creation volume is high but we don't have explicit ISO/PNR data,
                        # assume it's system-based (conservative estimate)
                        # For players with high creation volume (>0.15) but missing ISO/PNR data, assume 30-40% is self-created
                        if creation_vol_ratio > 0.15:
                            # High creation volume without ISO/PNR data = likely system-based (hub player)
                            self_created_freq = creation_vol_ratio * 0.35  # Assume only 35% is self-created
                            bag_check_reason = f"Proxy: CREATION_VOLUME_RATIO={creation_vol_ratio:.3f} (high, missing ISO/PNR) → estimated {self_created_freq:.3f} (system-based assumption)"
                        elif pd.notna(iso_median) and efg_iso < iso_median:
                            # Low ISO efficiency = likely system-based
                            self_created_freq = creation_vol_ratio * 0.5  # Assume 50% is self-created
                            bag_check_reason = f"Proxy: CREATION_VOLUME_RATIO={creation_vol_ratio:.3f}, EFG_ISO below median → estimated {self_created_freq:.3f}"
                        else:
                            # Moderate creation volume, decent ISO - use conservative estimate
                            self_created_freq = creation_vol_ratio * 0.6
                            bag_check_reason = f"Proxy: CREATION_VOLUME_RATIO={creation_vol_ratio:.3f} → estimated {self_created_freq:.3f}"
                    else:
                        # Fallback: use conservative estimate
                        if creation_vol_ratio > 0.15:
                            self_created_freq = creation_vol_ratio * 0.35
                        else:
                            self_created_freq = creation_vol_ratio * 0.6
                        bag_check_reason = f"Proxy: CREATION_VOLUME_RATIO={creation_vol_ratio:.3f} → estimated {self_created_freq:.3f} (no ISO efficiency data)"
                elif pd.notna(creation_vol_ratio):
                    # Only creation vol available - use conservative estimate
                    if creation_vol_ratio > 0.15:
                        self_created_freq = creation_vol_ratio * 0.35
                    else:
                        self_created_freq = creation_vol_ratio * 0.6
                    bag_check_reason = f"Proxy: CREATION_VOLUME_RATIO={creation_vol_ratio:.3f} → estimated {self_created_freq:.3f} (no ISO efficiency data)"
                else:
                    self_created_freq = 0.0
                    bag_check_reason = "No ISO/PNR or creation data available - assuming 0% self-created"
            else:
                # Use explicit playtype data if available
                if pd.isna(pnr_freq) or pnr_freq is None:
                    pnr_freq = 0.0
                self_created_freq = (iso_freq if pd.notna(iso_freq) else 0.0) + (pnr_freq if pd.notna(pnr_freq) else 0.0)
                bag_check_reason = f"Explicit: ISO={iso_freq:.3f}, PNR={pnr_freq:.3f}"
            
            # Gate threshold: 10% self-created frequency (absolute threshold)
            # PHASE 4.1 FIX: Bag Check Gate with Flash Multiplier Exemption
            # If Flash Multiplier conditions are met (low volume + elite efficiency), low volume = role constraint, not skill deficit
            # Phase 3.8 Fix: Cap star-level potential regardless of archetype if self_created freq < 10%
            
            # Check Flash Multiplier conditions directly (don't rely on flag which may not be set if star_median_creation_vol is None)
            flash_multiplier_conditions_met = False
            creation_vol = player_data.get('CREATION_VOLUME_RATIO', 0)
            creation_tax = player_data.get('CREATION_TAX', 0)
            efg_iso = player_data.get('EFG_ISO_WEIGHTED', 0)
            pressure_resilience = player_data.get('RS_PRESSURE_RESILIENCE', 0)
            
            # Check if low volume
            is_low_volume = (self.creation_vol_25th is not None and 
                            pd.notna(creation_vol) and creation_vol < self.creation_vol_25th)
            
            # Check if elite efficiency (any of the three signals)
            is_elite_efficiency = False
            if (self.creation_tax_80th is not None and pd.notna(creation_tax) and creation_tax > self.creation_tax_80th):
                is_elite_efficiency = True
            elif (self.efg_iso_80th is not None and pd.notna(efg_iso) and efg_iso > self.efg_iso_80th):
                is_elite_efficiency = True
            elif (self.pressure_resilience_80th is not None and pd.notna(pressure_resilience) and 
                  pressure_resilience > self.pressure_resilience_80th):
                is_elite_efficiency = True
            
            flash_multiplier_conditions_met = is_low_volume and is_elite_efficiency
            
            if pd.notna(self_created_freq) and self_created_freq < 0.10:
                # PHASE 4.1: Exempt if Flash Multiplier conditions are met (showing elite skills despite low volume)
                if flash_multiplier_conditions_met:
                    logger.info(f"Bag Check Gate EXEMPTED: Self-created freq {self_created_freq:.4f} < 0.10 BUT Flash Multiplier conditions met (low volume={creation_vol:.4f} + elite efficiency) = role constraint, not skill deficit")
                else:
                    bag_check_gate_applied = True
                    # Cap star-level at 30% (Sniper ceiling) - cannot be a true star without self-creation
                    original_star_level = star_level_potential
                    star_level_potential = min(star_level_potential, 0.30)
                    
                    # If predicted as King, redistribute to Bulldozer
                    if pred_archetype == 'King (Resilient Star)':
                        king_prob = prob_dict.get('King', 0)
                        prob_dict['Bulldozer'] = prob_dict.get('Bulldozer', 0) + king_prob
                        prob_dict['King'] = 0.0
                        pred_archetype = 'Bulldozer (Fragile Star)'
                    
                    # If star-level was capped, redistribute probabilities
                    if star_level_potential <= 0.30:
                        # Cap at Sniper/Victim level
                        prob_dict['Sniper'] = min(prob_dict.get('Sniper', 0), 0.30)
                        prob_dict['Victim'] = 1.0 - prob_dict['Sniper']
                        prob_dict['King'] = 0.0
                        prob_dict['Bulldozer'] = 0.0
                        # Update predicted archetype if needed
                        if original_star_level > 0.30:
                            pred_archetype = 'Sniper (Resilient Role)' if prob_dict['Sniper'] > prob_dict['Victim'] else 'Victim (Fragile Role)'
                    
                    logger.info(f"Bag Check Gate applied: Self-created freq {self_created_freq:.4f} < 0.10, star-level capped from {original_star_level:.2%} to {star_level_potential:.2%}. Reason: {bag_check_reason}")
        
        # Fix #2: Missing Leverage Data Penalty (Priority: High)
        # LEVERAGE_USG_DELTA is the #1 predictor - missing it is a critical gap
        leverage_data_penalty_applied = False
        if apply_phase3_fixes:
            leverage_usg = player_data.get('LEVERAGE_USG_DELTA', None)
            leverage_ts = player_data.get('LEVERAGE_TS_DELTA', None)
            clutch_min = player_data.get('CLUTCH_MIN_TOTAL', 0)
            
            # Check if missing leverage data or insufficient clutch minutes
            missing_leverage = pd.isna(leverage_usg) or pd.isna(leverage_ts)
            insufficient_clutch = pd.isna(clutch_min) or clutch_min < 15
            
            if missing_leverage or insufficient_clutch:
                original_star_level = star_level_potential
                # Cap at 30% (Sniper ceiling) - can't be a star without leverage data
                star_level_potential = min(star_level_potential, 0.30)
                leverage_data_penalty_applied = True
                
                # Redistribute probabilities if capped
                if star_level_potential <= 0.30:
                    prob_dict['Sniper'] = min(prob_dict.get('Sniper', 0), 0.30)
                    prob_dict['Victim'] = 1.0 - prob_dict['Sniper']
                    prob_dict['King'] = 0.0
                    prob_dict['Bulldozer'] = 0.0
                    # Update predicted archetype if needed
                    if original_star_level > 0.30:
                        pred_archetype = 'Sniper (Resilient Role)' if prob_dict['Sniper'] > prob_dict['Victim'] else 'Victim (Fragile Role)'
                
                reason = []
                if missing_leverage:
                    reason.append("missing leverage data")
                if insufficient_clutch:
                    reason.append(f"insufficient clutch minutes ({clutch_min if pd.notna(clutch_min) else 'NaN'} < 15)")
                logger.info(f"Leverage Data Penalty applied: {', '.join(reason)}, star-level capped from {original_star_level:.2%} to {star_level_potential:.2%}")
        
        # Fix #3: Negative Signal Gate (Priority: High)
        # Penalize players with multiple negative signals, especially negative LEVERAGE_USG_DELTA (Abdication Tax)
        negative_signal_gate_applied = False
        if apply_phase3_fixes:
            creation_tax = player_data.get('CREATION_TAX', 0)
            leverage_usg_delta = player_data.get('LEVERAGE_USG_DELTA', 0)
            leverage_ts_delta = player_data.get('LEVERAGE_TS_DELTA', 0)
            
            negative_signals = []
            
            # Negative creation tax (inefficient)
            if pd.notna(creation_tax) and creation_tax < -0.10:
                negative_signals.append(f"CREATION_TAX={creation_tax:.3f}")
            
            # Negative leverage USG delta (doesn't scale up - "Abdication Tax")
            # PHASE 4.1 FIX: Conditional Abdication Tax - Distinguish "Panic Abdication" (Simmons) from "Smart Deference" (Oladipo)
            # If LEVERAGE_TS_DELTA > 0.05 (elite efficiency), the usage drop is smart, not cowardly
            # Logic: Only penalize if BOTH usage drops AND efficiency doesn't spike
            if pd.notna(leverage_usg_delta) and leverage_usg_delta < -0.05:
                # Check if efficiency spikes (Smart Deference) or stays flat/drops (Panic Abdication)
                efficiency_spikes = pd.notna(leverage_ts_delta) and leverage_ts_delta > 0.05
                
                if not efficiency_spikes:
                    # Panic Abdication: Usage drops AND efficiency doesn't spike → Penalize
                    original_star_level = star_level_potential
                    # Hard filter: Cap at 30% (Sniper ceiling)
                    star_level_potential = min(star_level_potential, 0.30)
                    negative_signal_gate_applied = True
                    
                    # Redistribute probabilities if capped
                    if star_level_potential <= 0.30:
                        prob_dict['Sniper'] = min(prob_dict.get('Sniper', 0), 0.30)
                        prob_dict['Victim'] = 1.0 - prob_dict['Sniper']
                        prob_dict['King'] = 0.0
                        prob_dict['Bulldozer'] = 0.0
                        # Update predicted archetype if needed
                        if original_star_level > 0.30:
                            pred_archetype = 'Sniper (Resilient Role)' if prob_dict['Sniper'] > prob_dict['Victim'] else 'Victim (Fragile Role)'
                    
                    logger.info(f"Abdication Tax detected: LEVERAGE_USG_DELTA={leverage_usg_delta:.3f} < -0.05 AND LEVERAGE_TS_DELTA={leverage_ts_delta:.3f} <= 0.05 (Panic Abdication), star-level capped from {original_star_level:.2%} to {star_level_potential:.2%}")
                else:
                    # Smart Deference: Usage drops BUT efficiency spikes → Exempt
                    logger.info(f"Smart Deference detected: LEVERAGE_USG_DELTA={leverage_usg_delta:.3f} < -0.05 BUT LEVERAGE_TS_DELTA={leverage_ts_delta:.3f} > 0.05 (efficiency spikes) → Abdication Tax EXEMPTED")
            
            # Negative leverage TS delta (declines in clutch)
            if pd.notna(leverage_ts_delta) and leverage_ts_delta < -0.15:
                negative_signals.append(f"LEVERAGE_TS_DELTA={leverage_ts_delta:.3f}")
            
            # If 2+ negative signals (excluding leverage USG delta which is already handled above), cap at 30%
            if len(negative_signals) >= 2:
                original_star_level = star_level_potential
                star_level_potential = min(star_level_potential, 0.30)
                negative_signal_gate_applied = True
                
                # Redistribute probabilities if capped
                if star_level_potential <= 0.30:
                    prob_dict['Sniper'] = min(prob_dict.get('Sniper', 0), 0.30)
                    prob_dict['Victim'] = 1.0 - prob_dict['Sniper']
                    prob_dict['King'] = 0.0
                    prob_dict['Bulldozer'] = 0.0
                    # Update predicted archetype if needed
                    if original_star_level > 0.30:
                        pred_archetype = 'Sniper (Resilient Role)' if prob_dict['Sniper'] > prob_dict['Victim'] else 'Victim (Fragile Role)'
                
                logger.info(f"Multiple negative signals detected ({len(negative_signals)}): {', '.join(negative_signals)}, star-level capped from {original_star_level:.2%} to {star_level_potential:.2%}")
        
        # Fix #4: Data Completeness Gate (Priority: Medium)
        # Require at least 4 of 6 critical features present (67% completeness)
        data_completeness_gate_applied = False
        if apply_phase3_fixes:
            critical_features = [
                'CREATION_VOLUME_RATIO',
                'CREATION_TAX',
                'LEVERAGE_USG_DELTA',
                'LEVERAGE_TS_DELTA',
                'RS_PRESSURE_APPETITE',
                'RS_PRESSURE_RESILIENCE',
            ]
            
            present_features = sum(1 for f in critical_features if pd.notna(player_data.get(f, None)))
            completeness = present_features / len(critical_features) if len(critical_features) > 0 else 0.0
            
            # Require at least 4 of 6 critical features (67% completeness)
            if completeness < 0.67:
                original_star_level = star_level_potential
                # Cap at 30% (Sniper ceiling) - insufficient data for reliable prediction
                star_level_potential = min(star_level_potential, 0.30)
                data_completeness_gate_applied = True
                
                # Redistribute probabilities if capped
                if star_level_potential <= 0.30:
                    prob_dict['Sniper'] = min(prob_dict.get('Sniper', 0), 0.30)
                    prob_dict['Victim'] = 1.0 - prob_dict['Sniper']
                    prob_dict['King'] = 0.0
                    prob_dict['Bulldozer'] = 0.0
                    # Update predicted archetype if needed
                    if original_star_level > 0.30:
                        pred_archetype = 'Sniper (Resilient Role)' if prob_dict['Sniper'] > prob_dict['Victim'] else 'Victim (Fragile Role)'
                
                missing_features = [f for f in critical_features if pd.isna(player_data.get(f, None))]
                logger.info(f"Data Completeness Gate applied: {present_features}/{len(critical_features)} features present ({completeness:.1%} < 67%), star-level capped from {original_star_level:.2%} to {star_level_potential:.2%}. Missing: {', '.join(missing_features)}")
        
        # Fix #1: Minimum Sample Size Gate (Priority: High)
        # Check for minimum sample sizes to avoid small sample size noise
        sample_size_gate_applied = False
        if apply_phase3_fixes:
            # Check pressure shots (need minimum 50 for reliable pressure resilience)
            pressure_shots = player_data.get('RS_TOTAL_VOLUME', 0)
            insufficient_pressure = pd.isna(pressure_shots) or pressure_shots < 50
            
            # Check clutch minutes (need minimum 15 for reliable leverage data)
            clutch_min = player_data.get('CLUTCH_MIN_TOTAL', 0)
            insufficient_clutch = pd.isna(clutch_min) or clutch_min < 15
            
            # For creation metrics, we can't check ISO_FGA directly (not in dataset),
            # but we can check if CREATION_TAX is suspiciously perfect (1.0) or near-perfect (>0.8)
            # with low usage, which suggests tiny sample size
            creation_tax = player_data.get('CREATION_TAX', None)
            creation_vol_ratio = player_data.get('CREATION_VOLUME_RATIO', None)
            usage = player_data.get('USG_PCT', None)
            
            suspicious_creation = False
            if pd.notna(creation_tax) and pd.notna(usage):
                # If CREATION_TAX is perfect (1.0) or near-perfect (>0.8) with low usage (<20%),
                # it's likely small sample size noise
                if creation_tax >= 0.8 and usage < 0.20:
                    suspicious_creation = True
            
            if insufficient_pressure or insufficient_clutch or suspicious_creation:
                original_star_level = star_level_potential
                # Cap at 30% (Sniper ceiling) - insufficient sample size for reliable metrics
                star_level_potential = min(star_level_potential, 0.30)
                sample_size_gate_applied = True
                
                # Redistribute probabilities if capped
                if star_level_potential <= 0.30:
                    prob_dict['Sniper'] = min(prob_dict.get('Sniper', 0), 0.30)
                    prob_dict['Victim'] = 1.0 - prob_dict['Sniper']
                    prob_dict['King'] = 0.0
                    prob_dict['Bulldozer'] = 0.0
                    # Update predicted archetype if needed
                    if original_star_level > 0.30:
                        pred_archetype = 'Sniper (Resilient Role)' if prob_dict['Sniper'] > prob_dict['Victim'] else 'Victim (Fragile Role)'
                
                reasons = []
                if insufficient_pressure:
                    reasons.append(f"insufficient pressure shots ({pressure_shots if pd.notna(pressure_shots) else 'NaN'} < 50)")
                if insufficient_clutch:
                    reasons.append(f"insufficient clutch minutes ({clutch_min if pd.notna(clutch_min) else 'NaN'} < 15)")
                if suspicious_creation:
                    reasons.append(f"suspicious creation efficiency (CREATION_TAX={creation_tax:.3f} with usage={usage*100:.1f}% - likely small sample)")
                logger.info(f"Sample Size Gate applied: {', '.join(reasons)}, star-level capped from {original_star_level:.2%} to {star_level_potential:.2%}")
        
        # Check for missing data (confidence flags)
        confidence_flags = []
        key_features = ['LEVERAGE_TS_DELTA', 'LEVERAGE_USG_DELTA', 'CREATION_VOLUME_RATIO', 
                       'RS_PRESSURE_APPETITE', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE']
        for feat in key_features:
            if feat in player_data.index and pd.isna(player_data[feat]):
                confidence_flags.append(f"Missing {feat}")
        
        # Add Phase 3.5 & 3.6 fix flags
        phase3_flags = []
        if phase3_metadata['use_projection']:
            if phase3_metadata.get('flash_multiplier_applied', False):
                phase3_flags.append(f"Flash Multiplier applied (projection: {phase3_metadata['projection_factor']:.2f}x)")
            else:
                phase3_flags.append(f"Volume projection applied (factor: {phase3_metadata['projection_factor']:.2f}x)")
        if phase3_metadata['context_penalty'] > 0:
            phase3_flags.append(f"Context penalty applied: {phase3_metadata['context_penalty']:.4f}")
        if phase3_metadata.get('playoff_volume_tax_applied', False):
            phase3_flags.append(f"Playoff Volume Tax applied: CREATION_VOLUME_RATIO reduced by 50%")
        if fragility_gate_applied and rim_appetite is not None:
            phase3_flags.append(f"Fragility gate applied (RS_RIM_APPETITE: {rim_appetite:.4f})")
        if bag_check_gate_applied and self_created_freq is not None:
            phase3_flags.append(f"Bag Check Gate applied (Self-created freq: {self_created_freq:.4f})")
        if leverage_data_penalty_applied:
            phase3_flags.append("Leverage Data Penalty applied (missing leverage data or insufficient clutch minutes)")
        if negative_signal_gate_applied:
            phase3_flags.append("Negative Signal Gate applied (Abdication Tax or multiple negative signals)")
        if data_completeness_gate_applied:
            phase3_flags.append("Data Completeness Gate applied (insufficient critical features)")
        if sample_size_gate_applied:
            phase3_flags.append("Sample Size Gate applied (insufficient sample size for reliable metrics)")
        
        return {
            'predicted_archetype': pred_archetype,
            'probabilities': prob_dict,
            'star_level_potential': star_level_potential,
            'confidence_flags': confidence_flags,
            'phase3_flags': phase3_flags
        }
    
    def predict_at_multiple_usage_levels(
        self,
        player_data: pd.Series,
        usage_levels: list
    ) -> pd.DataFrame:
        """
        Predict archetype at multiple usage levels.
        
        Args:
            player_data: Player's stress vector data (Series)
            usage_levels: List of usage percentages as decimals
        
        Returns:
            DataFrame with predictions at each usage level
        """
        results = []
        
        for usage in usage_levels:
            pred = self.predict_archetype_at_usage(player_data, usage)
            results.append({
                'usage_level': usage,
                'usage_level_pct': usage * 100,  # For display
                'predicted_archetype': pred['predicted_archetype'],
                'king_prob': pred['probabilities'].get('King', 0),
                'bulldozer_prob': pred['probabilities'].get('Bulldozer', 0),
                'sniper_prob': pred['probabilities'].get('Sniper', 0),
                'victim_prob': pred['probabilities'].get('Victim', 0),
                'star_level_potential': pred['star_level_potential'],
                'confidence_flags': ', '.join(pred['confidence_flags']) if pred['confidence_flags'] else 'None'
            })
        
        return pd.DataFrame(results)


if __name__ == "__main__":
    # Example usage
    predictor = ConditionalArchetypePredictor()
    
    # Test on Brunson 2020-21
    player_data = predictor.get_player_data("Jalen Brunson", "2020-21")
    if player_data is not None:
        print("\n=== Jalen Brunson (2020-21) Predictions ===")
        usage_levels = [0.15, 0.20, 0.25, 0.28, 0.32]
        results = predictor.predict_at_multiple_usage_levels(player_data, usage_levels)
        print(results.to_string(index=False))
        
        # Test at specific usage level
        print("\n=== Prediction at 25% Usage ===")
        pred_25 = predictor.predict_archetype_at_usage(player_data, 0.25)
        print(f"Predicted Archetype: {pred_25['predicted_archetype']}")
        print(f"Star-Level Potential: {pred_25['star_level_potential']:.2%}")
        print(f"Probabilities: {pred_25['probabilities']}")

