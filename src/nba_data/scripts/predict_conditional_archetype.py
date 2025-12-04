"""
Phase 2: Conditional Prediction Function (Enhanced with Phase 3.5 & 3.6 Fixes)

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
        
        return df_features
    
    def _calculate_feature_distributions(self):
        """Calculate feature distributions for Phase 3.5 & 3.6 fixes."""
        # Phase 3.5 Fix #1: Use RS_RIM_APPETITE (absolute volume) instead of RIM_PRESSURE_RESILIENCE (ratio)
        # Calculate bottom 20th percentile for RS_RIM_APPETITE (Fragility Gate)
        if 'RS_RIM_APPETITE' in self.df_features.columns:
            rim_appetite = self.df_features['RS_RIM_APPETITE'].dropna()
            if len(rim_appetite) > 0:
                self.rim_appetite_bottom_20th = rim_appetite.quantile(0.20)
                logger.info(f"RS_RIM_APPETITE bottom 20th percentile: {self.rim_appetite_bottom_20th:.4f}")
            else:
                self.rim_appetite_bottom_20th = None
        else:
            self.rim_appetite_bottom_20th = None
        
        # Phase 3.6 Fix #1: Flash Multiplier - Calculate percentiles for flash detection
        if 'CREATION_VOLUME_RATIO' in self.df_features.columns:
            creation_vol = self.df_features['CREATION_VOLUME_RATIO'].dropna()
            if len(creation_vol) > 0:
                self.creation_vol_25th = creation_vol.quantile(0.25)
                logger.info(f"CREATION_VOLUME_RATIO 25th percentile: {self.creation_vol_25th:.4f}")
            else:
                self.creation_vol_25th = None
        else:
            self.creation_vol_25th = None
        
        if 'CREATION_TAX' in self.df_features.columns:
            creation_tax = self.df_features['CREATION_TAX'].dropna()
            if len(creation_tax) > 0:
                self.creation_tax_80th = creation_tax.quantile(0.80)
                logger.info(f"CREATION_TAX 80th percentile: {self.creation_tax_80th:.4f}")
            else:
                self.creation_tax_80th = None
        else:
            self.creation_tax_80th = None
        
        if 'EFG_ISO_WEIGHTED' in self.df_features.columns:
            efg_iso = self.df_features['EFG_ISO_WEIGHTED'].dropna()
            if len(efg_iso) > 0:
                self.efg_iso_80th = efg_iso.quantile(0.80)
                logger.info(f"EFG_ISO_WEIGHTED 80th percentile: {self.efg_iso_80th:.4f}")
            else:
                self.efg_iso_80th = None
        else:
            self.efg_iso_80th = None
        
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
        
        # Phase 3.6 Fix #2: Playoff Translation Tax - Calculate league average open shot frequency
        # Try to calculate from shot quality data if available
        self.league_avg_open_freq = None
        # Check for RS_OPEN_SHOT_FREQUENCY (from pressure features) or OPEN_SHOT_FREQUENCY
        open_freq_col = None
        if 'RS_OPEN_SHOT_FREQUENCY' in self.df_features.columns:
            open_freq_col = 'RS_OPEN_SHOT_FREQUENCY'
        elif 'OPEN_SHOT_FREQUENCY' in self.df_features.columns:
            open_freq_col = 'OPEN_SHOT_FREQUENCY'
        
        if open_freq_col:
            open_freq = self.df_features[open_freq_col].dropna()
            if len(open_freq) > 0:
                self.league_avg_open_freq = open_freq.median()
                logger.info(f"League average {open_freq_col}: {self.league_avg_open_freq:.4f}")
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
            
            # Phase 3.6 Fix #1: Flash Multiplier - Detect elite efficiency on low volume
            # If player has elite efficiency on low volume, project to star-level volume (not scalar)
            creation_vol = player_data.get('CREATION_VOLUME_RATIO', 0)
            creation_tax = player_data.get('CREATION_TAX', 0)
            efg_iso = player_data.get('EFG_ISO_WEIGHTED', 0)
            
            # Check if "Flash of Brilliance" (low volume + elite efficiency)
            is_low_volume = False
            is_elite_efficiency = False
            
            if (self.creation_vol_25th is not None and 
                pd.notna(creation_vol) and creation_vol < self.creation_vol_25th):
                is_low_volume = True
            
            if (self.creation_tax_80th is not None and pd.notna(creation_tax) and creation_tax > self.creation_tax_80th):
                is_elite_efficiency = True
            elif (self.efg_iso_80th is not None and pd.notna(efg_iso) and efg_iso > self.efg_iso_80th):
                is_elite_efficiency = True
            
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
        
        # Phase 3.6 Fix #2: Playoff Translation Tax - Calculate tax based on open shot frequency
        playoff_tax = 0.0
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
            
            # Calculate playoff tax if we have open shot frequency
            if pd.notna(open_shot_freq) and self.league_avg_open_freq is not None:
                if open_shot_freq > self.league_avg_open_freq:
                    excess_open = open_shot_freq - self.league_avg_open_freq
                    # For every 1% above average, deduct 0.5% from EFG
                    playoff_tax = excess_open * 0.5
                    logger.debug(f"Playoff Translation Tax: {open_shot_freq:.4f} vs {self.league_avg_open_freq:.4f} = {playoff_tax:.4f}")
            elif pd.notna(open_shot_freq):
                # If we have player's open shot freq but no league average, calculate on-the-fly
                # This is a fallback - ideally league average should be pre-calculated
                open_freq_col = None
                if 'RS_OPEN_SHOT_FREQUENCY' in self.df_features.columns:
                    open_freq_col = 'RS_OPEN_SHOT_FREQUENCY'
                elif 'OPEN_SHOT_FREQUENCY' in self.df_features.columns:
                    open_freq_col = 'OPEN_SHOT_FREQUENCY'
                
                if open_freq_col:
                    league_avg = self.df_features[open_freq_col].dropna().median()
                    if pd.notna(league_avg) and open_shot_freq > league_avg:
                        excess_open = open_shot_freq - league_avg
                        playoff_tax = excess_open * 0.5
        
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
                        # Fill with 0 for clock features, median for others
                        if 'CLOCK' in feature_name:
                            val = 0.0
                        elif feature_name in self.df_features.columns:
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
                        elif feature_name in ['RS_PRESSURE_RESILIENCE', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE', 
                                             'RS_EARLY_CLOCK_PRESSURE_RESILIENCE', 'CREATION_TAX', 'EFG_ISO_WEIGHTED',
                                             'EFG_PCT_0_DRIBBLE']:
                            # Efficiency features: keep as-is, but apply context penalty and playoff tax if applicable
                            if context_penalty > 0:
                                val = max(0.0, val - context_penalty)
                            # Phase 3.6 Fix #2: Apply playoff translation tax to efficiency features
                            if playoff_tax > 0:
                                val = max(0.0, val - playoff_tax)
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
            'playoff_tax': playoff_tax,
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
        bag_check_gate_applied = False
        self_created_freq = None
        if apply_phase3_fixes:
            # Calculate self-created frequency (ISO + PNR Handler)
            iso_freq = player_data.get('ISO_FREQUENCY', None)
            pnr_freq = player_data.get('PNR_HANDLER_FREQUENCY', None)
            
            # Try alternative column names if primary ones don't exist
            if pd.isna(iso_freq) or iso_freq is None:
                # Try to calculate from playtype data if available
                # For now, we'll use CREATION_VOLUME_RATIO as a proxy if playtype data isn't available
                # This is a fallback - ideally we'd have explicit ISO_FREQUENCY and PNR_HANDLER_FREQUENCY
                creation_vol_ratio = player_data.get('CREATION_VOLUME_RATIO', 0)
                if pd.notna(creation_vol_ratio):
                    # Use CREATION_VOLUME_RATIO as proxy for self-created frequency
                    # If it's very low (< 0.10), likely low self-creation
                    self_created_freq = creation_vol_ratio
                else:
                    self_created_freq = 0.0
            else:
                # Use explicit playtype data if available
                if pd.isna(pnr_freq) or pnr_freq is None:
                    pnr_freq = 0.0
                self_created_freq = (iso_freq if pd.notna(iso_freq) else 0.0) + (pnr_freq if pd.notna(pnr_freq) else 0.0)
            
            # Gate threshold: 10% self-created frequency
            if pd.notna(self_created_freq) and self_created_freq < 0.10:
                # Cap at Bulldozer (cannot be King)
                if pred_archetype == 'King (Resilient Star)':
                    bag_check_gate_applied = True
                    # Redistribute: King → Bulldozer
                    king_prob = prob_dict.get('King', 0)
                    prob_dict['Bulldozer'] = prob_dict.get('Bulldozer', 0) + king_prob
                    prob_dict['King'] = 0.0
                    # Update predicted archetype
                    pred_archetype = 'Bulldozer (Fragile Star)'
                    # Recalculate star-level (should stay same since King + Bulldozer = star-level)
                    star_level_potential = prob_dict.get('King', 0) + prob_dict.get('Bulldozer', 0)
                    logger.debug(f"Bag Check Gate applied: Self-created freq {self_created_freq:.4f} < 0.10, capped at Bulldozer")
        
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
        if phase3_metadata.get('playoff_tax', 0) > 0:
            phase3_flags.append(f"Playoff Translation Tax applied: {phase3_metadata['playoff_tax']:.4f}")
        if fragility_gate_applied and rim_appetite is not None:
            phase3_flags.append(f"Fragility gate applied (RS_RIM_APPETITE: {rim_appetite:.4f})")
        if bag_check_gate_applied and self_created_freq is not None:
            phase3_flags.append(f"Bag Check Gate applied (Self-created freq: {self_created_freq:.4f})")
        
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

