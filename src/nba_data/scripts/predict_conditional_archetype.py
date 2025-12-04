"""
Phase 2: Conditional Prediction Function

This script provides a function to predict archetype at different usage levels.
This enables answering both questions:
1. "What would this player's archetype be at their current usage?" (Use Case A)
2. "What would this player's archetype be at 25% usage?" (Use Case B - Latent Star Detection)
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
    
    def prepare_features(self, player_data: pd.Series, usage_level: float) -> np.ndarray:
        """
        Prepare feature vector for prediction at specified usage level.
        
        Args:
            player_data: Player's stress vector data (Series)
            usage_level: Usage percentage as decimal (e.g., 0.25 for 25%)
        
        Returns:
            Feature array ready for model prediction
        """
        features = []
        missing_features = []
        
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
        
        return np.array(features).reshape(1, -1)
    
    def predict_archetype_at_usage(
        self, 
        player_data: pd.Series, 
        usage_level: float
    ) -> Dict:
        """
        Predict archetype at specified usage level.
        
        Args:
            player_data: Player's stress vector data (Series)
            usage_level: Usage percentage as decimal (e.g., 0.25 for 25%)
        
        Returns:
            Dictionary with:
            - predicted_archetype: Predicted archetype class
            - probabilities: Dict of probabilities for each archetype
            - star_level_potential: Combined King + Bulldozer probability
            - confidence_flags: List of missing data flags
        """
        # Prepare features
        features = self.prepare_features(player_data, usage_level)
        
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
        
        # Check for missing data (confidence flags)
        confidence_flags = []
        key_features = ['LEVERAGE_TS_DELTA', 'LEVERAGE_USG_DELTA', 'CREATION_VOLUME_RATIO', 
                       'RS_PRESSURE_APPETITE', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE']
        for feat in key_features:
            if feat in player_data.index and pd.isna(player_data[feat]):
                confidence_flags.append(f"Missing {feat}")
        
        return {
            'predicted_archetype': pred_archetype,
            'probabilities': prob_dict,
            'star_level_potential': star_level_potential,
            'confidence_flags': confidence_flags
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

