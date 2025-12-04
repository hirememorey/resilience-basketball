"""
Phase 0: Model Behavior Discovery

This script tests the current model on 20-30 known cases to understand:
1. Does it ever predict "King"? (Expected: rarely, too conservative)
2. What does it predict for known Kings? (Expected: "Bulldozer" at high usage)
3. What does it predict for known non-stars? (Expected: "Victim" or "Sniper")
4. How do predictions change with usage level?

This validation happens BEFORE any model modifications.
"""

import pandas as pd
import numpy as np
import joblib
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelBehaviorValidator:
    def __init__(self):
        self.results_dir = Path("results")
        self.models_dir = Path("models")
        
        # Load model and encoder
        self.model = joblib.load(self.models_dir / "resilience_xgb.pkl")
        self.encoder = joblib.load(self.models_dir / "archetype_encoder.pkl")
        
        # Load and merge all feature files (same as training script)
        self.df_features = self.load_and_merge_features()
        self.df_archetypes = pd.read_csv(self.results_dir / "resilience_archetypes.csv")
        
        # Get feature names from model (XGBoost stores feature names)
        if hasattr(self.model, 'feature_names_in_'):
            self.feature_names = list(self.model.feature_names_in_)
        else:
            # Fallback: use expected features from training script
            self.feature_names = [
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
                'RIM_PRESSURE_RESILIENCE'
            ]
        
        logger.info(f"Model expects {len(self.feature_names)} features")
    
    def load_and_merge_features(self) -> pd.DataFrame:
        """Load and merge all feature files (same as training script)."""
        # Base features
        df_features = pd.read_csv(self.results_dir / "predictive_dataset.csv")
        
        # Plasticity Features
        plasticity_files = list(self.results_dir.glob("plasticity_scores_*.csv"))
        if plasticity_files:
            df_plasticity_list = [pd.read_csv(f) for f in plasticity_files]
            df_plasticity = pd.concat(df_plasticity_list, ignore_index=True)
            df_features = pd.merge(
                df_features,
                df_plasticity,
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )
        
        # Pressure Features
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
        
        # Physicality Features
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
        
        # Rim Pressure Features
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
        
    def get_test_cases(self) -> List[Dict]:
        """Define 20-30 known test cases across different categories."""
        return [
            # Known Kings (elite production maintained)
            {"name": "Nikola Jokić", "season": "2022-23", "category": "Known King", "actual_archetype": "King"},
            {"name": "Nikola Jokić", "season": "2023-24", "category": "Known King", "actual_archetype": "King"},
            {"name": "Giannis Antetokounmpo", "season": "2020-21", "category": "Known King", "actual_archetype": "King"},
            {"name": "LeBron James", "season": "2019-20", "category": "Known King", "actual_archetype": "King"},
            
            # Known Bulldogs (high volume, lower efficiency)
            {"name": "Luka Dončić", "season": "2023-24", "category": "Known Bulldozer", "actual_archetype": "Bulldozer"},
            {"name": "James Harden", "season": "2018-19", "category": "Known Bulldozer", "actual_archetype": "Bulldozer"},
            
            # Known Breakouts (players who broke out after low usage)
            {"name": "Jalen Brunson", "season": "2020-21", "category": "Known Breakout", "actual_archetype": "Victim", "breakout_season": "2022-23", "breakout_usage": 26.6},
            {"name": "Jalen Brunson", "season": "2022-23", "category": "Known Breakout", "actual_archetype": "King", "breakout_usage": 26.6},
            {"name": "Tyrese Haliburton", "season": "2020-21", "category": "Known Breakout", "actual_archetype": "Victim", "breakout_season": "2021-22", "breakout_usage": 23.9},
            {"name": "Tyrese Maxey", "season": "2020-21", "category": "Known Breakout", "actual_archetype": "Victim", "breakout_season": "2023-24", "breakout_usage": 27.3},
            
            # Known Non-Stars (role players who never broke out)
            {"name": "Ben Simmons", "season": "2020-21", "category": "Known Non-Star", "actual_archetype": "Victim"},
            {"name": "T.J. McConnell", "season": "2020-21", "category": "Known Non-Star", "actual_archetype": "Victim"},
            {"name": "Cory Joseph", "season": "2020-21", "category": "Known Non-Star", "actual_archetype": "Victim"},
            
            # Known Snipers (efficient role players)
            {"name": "Aaron Gordon", "season": "2018-19", "category": "Known Sniper", "actual_archetype": "Sniper"},
            {"name": "Brook Lopez", "season": "2020-21", "category": "Known Sniper", "actual_archetype": "Sniper"},
        ]
    
    def get_player_data(self, player_name: str, season: str) -> pd.Series:
        """Get player's stress vector data for a given season."""
        player_data = self.df_features[
            (self.df_features['PLAYER_NAME'] == player_name) & 
            (self.df_features['SEASON'] == season)
        ]
        
        if len(player_data) == 0:
            logger.warning(f"No data found for {player_name} {season}")
            return None
        
        return player_data.iloc[0]
    
    def prepare_features(self, player_data: pd.Series, usage_level: float = None) -> np.ndarray:
        """Prepare feature vector for prediction. If usage_level provided, use it instead of actual USG_PCT."""
        features = []
        
        for feature_name in self.feature_names:
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
                        val = 0.0  # Default if feature doesn't exist
                features.append(val)
            else:
                # Feature missing from player data
                if 'CLOCK' in feature_name:
                    features.append(0.0)
                elif feature_name in self.df_features.columns:
                    features.append(self.df_features[feature_name].median())
                else:
                    features.append(0.0)  # Default if feature doesn't exist
        
        return np.array(features).reshape(1, -1)
    
    def predict_at_usage(self, player_data: pd.Series, usage_levels: List[float]) -> List[Dict]:
        """Predict archetype at different usage levels."""
        results = []
        
        for usage in usage_levels:
            # Note: Current model doesn't use USG_PCT, so predictions won't change
            # This is just to test current behavior
            features = self.prepare_features(player_data, usage_level=usage)
            
            # Predict
            probs = self.model.predict_proba(features)[0]
            pred_class = self.model.predict(features)[0]
            pred_archetype = self.encoder.inverse_transform([pred_class])[0]
            
            # Get probabilities for each archetype
            # Map full names to short names for easier interpretation
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
                # Also keep full name for reference
                prob_dict[archetype] = probs[i]
            
            results.append({
                'usage_level': usage,
                'predicted_archetype': pred_archetype,
                'probabilities': prob_dict,
                'star_level_potential': prob_dict.get('King', 0) + prob_dict.get('Bulldozer', 0)
            })
        
        return results
    
    def validate_model_behavior(self):
        """Run validation tests on all test cases."""
        logger.info("=" * 80)
        logger.info("PHASE 0: MODEL BEHAVIOR DISCOVERY")
        logger.info("=" * 80)
        
        test_cases = self.get_test_cases()
        results = []
        
        # Test usage levels
        usage_levels = [15.0, 18.0, 22.0, 25.0, 28.0, 32.0]
        
        for case in test_cases:
            player_name = case['name']
            season = case['season']
            category = case['category']
            
            logger.info(f"\nTesting: {player_name} ({season}) - {category}")
            
            # Get player data
            player_data = self.get_player_data(player_name, season)
            if player_data is None:
                continue
            
            # Get actual usage (stored as decimal, e.g., 0.30 = 30%)
            actual_usage = player_data.get('USG_PCT', None)
            if pd.isna(actual_usage):
                logger.warning(f"  No USG_PCT data for {player_name} {season}")
                continue
            
            # Convert to percentage for display
            actual_usage_pct = actual_usage * 100 if actual_usage < 1.0 else actual_usage
            logger.info(f"  Actual Usage: {actual_usage_pct:.1f}%")
            
            # Predict at different usage levels
            predictions = self.predict_at_usage(player_data, usage_levels)
            
            # Store results
            for pred in predictions:
                results.append({
                    'player_name': player_name,
                    'season': season,
                    'category': category,
                    'actual_archetype': case.get('actual_archetype', 'Unknown'),
                    'actual_usage': actual_usage_pct,
                    'test_usage': pred['usage_level'],
                    'predicted_archetype': pred['predicted_archetype'],
                    'king_prob': pred['probabilities'].get('King', 0),
                    'bulldozer_prob': pred['probabilities'].get('Bulldozer', 0),
                    'sniper_prob': pred['probabilities'].get('Sniper', 0),
                    'victim_prob': pred['probabilities'].get('Victim', 0),
                    'star_level_potential': pred['star_level_potential']
                })
        
        # Save results
        df_results = pd.DataFrame(results)
        output_path = self.results_dir / "model_behavior_validation.csv"
        df_results.to_csv(output_path, index=False)
        logger.info(f"\nResults saved to {output_path}")
        
        # Analyze patterns
        self.analyze_patterns(df_results)
        
        return df_results
    
    def analyze_patterns(self, df_results: pd.DataFrame):
        """Analyze patterns in model behavior."""
        logger.info("\n" + "=" * 80)
        logger.info("MODEL BEHAVIOR PATTERNS")
        logger.info("=" * 80)
        
        # Pattern 1: Does it ever predict "King"?
        king_predictions = df_results[df_results['predicted_archetype'] == 'King']
        logger.info(f"\n1. King Predictions: {len(king_predictions)} out of {len(df_results)} ({len(king_predictions)/len(df_results)*100:.1f}%)")
        if len(king_predictions) > 0:
            logger.info("   Examples:")
            for _, row in king_predictions.head(5).iterrows():
                logger.info(f"     {row['player_name']} ({row['season']}) at {row['test_usage']:.1f}% usage")
        
        # Pattern 2: What does it predict for known Kings?
        known_kings = df_results[df_results['category'] == 'Known King']
        logger.info(f"\n2. Known Kings Predictions:")
        for player in known_kings['player_name'].unique():
            player_data = known_kings[known_kings['player_name'] == player]
            logger.info(f"   {player}:")
            for _, row in player_data.iterrows():
                logger.info(f"     At {row['test_usage']:.1f}% usage: {row['predicted_archetype']} "
                          f"(King: {row['king_prob']:.2%}, Bulldozer: {row['bulldozer_prob']:.2%}, "
                          f"Star-Level: {row['star_level_potential']:.2%})")
        
        # Pattern 3: What does it predict for known breakouts at low vs high usage?
        known_breakouts = df_results[df_results['category'] == 'Known Breakout']
        logger.info(f"\n3. Known Breakouts Predictions:")
        for player in known_breakouts['player_name'].unique():
            player_data = known_breakouts[known_breakouts['player_name'] == player].sort_values('test_usage')
            logger.info(f"   {player}:")
            for _, row in player_data.iterrows():
                logger.info(f"     At {row['test_usage']:.1f}% usage: {row['predicted_archetype']} "
                          f"(Star-Level: {row['star_level_potential']:.2%})")
        
        # Pattern 4: What does it predict for known non-stars?
        known_non_stars = df_results[df_results['category'] == 'Known Non-Star']
        logger.info(f"\n4. Known Non-Stars Predictions:")
        for player in known_non_stars['player_name'].unique():
            player_data = known_non_stars[known_non_stars['player_name'] == player]
            logger.info(f"   {player}:")
            for _, row in player_data.head(3).iterrows():
                logger.info(f"     At {row['test_usage']:.1f}% usage: {row['predicted_archetype']} "
                          f"(Star-Level: {row['star_level_potential']:.2%})")
        
        # Pattern 5: Star-Level Potential distribution
        logger.info(f"\n5. Star-Level Potential Distribution:")
        logger.info(f"   Mean: {df_results['star_level_potential'].mean():.2%}")
        logger.info(f"   Median: {df_results['star_level_potential'].median():.2%}")
        logger.info(f"   Max: {df_results['star_level_potential'].max():.2%}")
        logger.info(f"   Min: {df_results['star_level_potential'].min():.2%}")
        
        # Pattern 6: Does prediction change with usage? (Current model shouldn't, but let's verify)
        logger.info(f"\n6. Prediction Consistency Across Usage Levels:")
        for player in df_results['player_name'].unique():
            player_data = df_results[df_results['player_name'] == player].sort_values('test_usage')
            unique_predictions = player_data['predicted_archetype'].unique()
            if len(unique_predictions) > 1:
                logger.info(f"   {player}: Predictions vary: {unique_predictions}")
            else:
                logger.debug(f"   {player}: Consistent prediction: {unique_predictions[0]}")


if __name__ == "__main__":
    validator = ModelBehaviorValidator()
    results = validator.validate_model_behavior()

