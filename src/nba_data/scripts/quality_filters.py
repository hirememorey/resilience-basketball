"""
Phase 1: Quality Filters

This module implements quality filters to identify players with positive signals
across key stress vectors. These filters prevent false positives (players with
negative Leverage TS Delta, weak creation ability, etc.) from ranking high.

Key Principles:
1. Filter for quality FIRST, before ranking
2. Missing data = selection bias, not random noise
3. Use data completeness score to handle missing data
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QualityFilters:
    """Quality filters for identifying players with positive stress vector signals."""
    
    # Core quality signals (from feature importance and component analysis)
    KEY_FEATURES = [
        'LEVERAGE_TS_DELTA',           # #1 predictor (9.2% importance)
        'CREATION_VOLUME_RATIO',       # #2 predictor (6.2% importance)
        'LEVERAGE_USG_DELTA',          # Top-5 predictor
        'RS_PRESSURE_APPETITE',        # #3 predictor (4.5% importance)
        'RS_LATE_CLOCK_PRESSURE_RESILIENCE',  # Strong signal (4.8% importance)
        'RS_FTr'                        # Physicality signal (3.9% importance)
    ]
    
    def __init__(self):
        """Initialize quality filters with thresholds."""
        # Quality filter thresholds (based on component analysis and lessons learned)
        # These are designed to catch FALSE POSITIVES, not filter out known stars
        # Key insight: Players with negative Leverage TS Delta shouldn't rank high
        # Thresholds are very lenient - only catch obvious false positives
        self.thresholds = {
            'LEVERAGE_TS_DELTA': -0.15,            # Must not decline too much in clutch (very lenient)
            'CREATION_VOLUME_RATIO': 0.1,          # Minimal creation ability (very lenient)
            'LEVERAGE_USG_DELTA': -0.10,           # Must not be too passive (very lenient)
            'RS_PRESSURE_APPETITE': -1.0,          # No threshold (any value OK)
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE': -1.0,  # No threshold (any value OK)
            'RS_FTr': -1.0                         # No threshold (any value OK)
        }
        
        # Age filter (young players with breakout potential)
        # Note: For latent star detection, use < 26. For established stars, age doesn't matter.
        self.max_age = 26
        
        # Data completeness threshold (must have at least 4 of 6 key features for young players)
        # More lenient for young players who may have missing data
        self.min_completeness = 4 / 6  # 67% completeness (lowered from 83%)
    
    def calculate_data_completeness(self, player_data: pd.Series) -> Tuple[float, int, int]:
        """
        Calculate data completeness score for a player.
        
        Returns:
            (completeness_score, features_present, total_features)
        """
        features_present = 0
        total_features = len(self.KEY_FEATURES)
        
        for feature in self.KEY_FEATURES:
            if feature in player_data.index:
                val = player_data[feature]
                if not pd.isna(val):
                    features_present += 1
        
        completeness_score = features_present / total_features
        
        return completeness_score, features_present, total_features
    
    def check_quality_filter(self, player_data: pd.Series, strict: bool = True) -> Tuple[bool, Dict[str, bool], str]:
        """
        Check if player passes quality filter.
        
        Args:
            player_data: Player's stress vector data
            strict: If True, all quality signals must pass. If False, allow 1 failure.
        
        Returns:
            (passed, signal_results, reason)
        """
        signal_results = {}
        failures = []
        
        # Check each quality signal
        for feature, threshold in self.thresholds.items():
            if feature in player_data.index:
                val = player_data[feature]
                if pd.isna(val):
                    signal_results[feature] = None  # Missing data
                    # Don't add to failures if threshold is -1.0 (no threshold)
                    if threshold >= 0:
                        failures.append(f"{feature} (missing)")
                else:
                    # Skip check if threshold is -1.0 (no threshold)
                    if threshold < -0.5:  # No threshold
                        signal_results[feature] = True  # Always pass
                    else:
                        passed = val > threshold if threshold >= 0 else val >= threshold
                        signal_results[feature] = passed
                        if not passed:
                            failures.append(f"{feature} ({val:.3f} <= {threshold:.3f})")
            else:
                signal_results[feature] = None  # Feature doesn't exist
                # Don't add to failures if threshold is -1.0 (no threshold)
                if threshold >= 0:
                    failures.append(f"{feature} (missing)")
        
        # Check age filter (only for latent star detection, not for established stars)
        # For now, we'll make age optional - it's a filter for latent stars, not quality
        age = player_data.get('AGE', None)
        if pd.isna(age):
            age_passed = None  # Missing age is OK
        else:
            age_passed = age < self.max_age
            # Don't fail quality filter for age - it's a separate filter for latent stars
            # if not age_passed:
            #     failures.append(f"AGE ({age} >= {self.max_age})")
        
        # Check data completeness
        completeness, features_present, total_features = self.calculate_data_completeness(player_data)
        completeness_passed = completeness >= self.min_completeness
        if not completeness_passed:
            failures.append(f"Data Completeness ({features_present}/{total_features} < {self.min_completeness*100:.0f}%)")
        
        # Determine if passed
        if strict:
            # All quality signals must pass (except missing data, which is handled by completeness)
            # Allow missing data for 1 feature, but all present features must pass
            present_features = [f for f in self.KEY_FEATURES if signal_results.get(f) is not None]
            if len(present_features) < self.min_completeness * len(self.KEY_FEATURES):
                passed = False
                reason = f"Too much missing data ({features_present}/{total_features})"
            else:
                # Check all present features pass
                all_present_pass = all(signal_results.get(f, True) for f in present_features)
                age_ok = age_passed if age_passed is not None else True  # Age missing is OK if other signals pass
                passed = all_present_pass and age_ok and completeness_passed
                reason = "Passed" if passed else f"Failed: {', '.join(failures)}"
        else:
            # Allow 1 failure
            failure_count = len([f for f in failures if not f.endswith('(missing)')])
            passed = failure_count <= 1 and completeness_passed
            reason = "Passed" if passed else f"Failed: {', '.join(failures)}"
        
        return passed, signal_results, reason
    
    def filter_dataset(self, df: pd.DataFrame, strict: bool = True) -> pd.DataFrame:
        """
        Filter dataset to only include players who pass quality filter.
        
        Args:
            df: Dataset with player stress vectors
            strict: If True, all quality signals must pass. If False, allow 1 failure.
        
        Returns:
            Filtered dataset with quality filter results added
        """
        logger.info(f"Filtering dataset: {len(df)} players")
        
        results = []
        for idx, row in df.iterrows():
            passed, signal_results, reason = self.check_quality_filter(row, strict=strict)
            completeness, features_present, total_features = self.calculate_data_completeness(row)
            
            results.append({
                'passed_quality_filter': passed,
                'quality_filter_reason': reason,
                'data_completeness': completeness,
                'features_present': features_present,
                'total_features': total_features,
                **{f'{k}_check': v for k, v in signal_results.items()}
            })
        
        # Add results to dataframe
        df_results = pd.DataFrame(results, index=df.index)
        df_filtered = pd.concat([df.reset_index(drop=True), df_results], axis=1)
        
        # Count passed
        passed_count = df_filtered['passed_quality_filter'].sum()
        logger.info(f"Quality filter results: {passed_count}/{len(df)} passed ({passed_count/len(df)*100:.1f}%)")
        
        return df_filtered
    
    def calculate_base_signal_strength(self, player_data: pd.Series) -> float:
        """
        Calculate base signal strength (average of top stress vectors, independent of usage).
        
        This metric ensures high star potential requires both high usage AND strong base signals.
        """
        signals = []
        weights = {
            'LEVERAGE_TS_DELTA': 0.30,              # #1 predictor
            'CREATION_VOLUME_RATIO': 0.25,          # #2 predictor
            'LEVERAGE_USG_DELTA': 0.15,             # Top-5 predictor
            'RS_PRESSURE_APPETITE': 0.15,           # #3 predictor
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE': 0.10,  # Strong signal
            'RS_FTr': 0.05                          # Physicality
        }
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for feature, weight in weights.items():
            if feature in player_data.index:
                val = player_data[feature]
                if not pd.isna(val):
                    # Normalize to 0-1 scale (assuming typical ranges)
                    # For deltas: -0.2 to +0.2 -> 0 to 1
                    # For ratios: 0 to 1 -> 0 to 1
                    if 'DELTA' in feature:
                        normalized = (val + 0.2) / 0.4  # Map -0.2 to +0.2 -> 0 to 1
                    elif 'RATIO' in feature or 'APPETITE' in feature or 'RESILIENCE' in feature:
                        normalized = max(0, min(1, val))  # Clamp to 0-1
                    else:
                        normalized = max(0, min(1, val / 0.5))  # Assume max around 0.5
                    
                    weighted_sum += normalized * weight
                    total_weight += weight
        
        if total_weight > 0:
            base_signal_strength = weighted_sum / total_weight
        else:
            base_signal_strength = 0.0
        
        return base_signal_strength


def validate_filters_on_known_cases(df_features: pd.DataFrame) -> pd.DataFrame:
    """
    Validate quality filters on known test cases.
    
    Args:
        df_features: Dataset with player stress vectors
    
    Returns:
        Validation results
    """
    logger.info("Validating quality filters on known cases...")
    
    filters = QualityFilters()
    
    # Known test cases
    test_cases = [
        {"name": "Nikola Jokić", "season": "2022-23", "category": "Known King"},
        {"name": "Giannis Antetokounmpo", "season": "2020-21", "category": "Known King"},
        {"name": "LeBron James", "season": "2019-20", "category": "Known King"},
        {"name": "Jalen Brunson", "season": "2020-21", "category": "Known Breakout"},
        {"name": "Jalen Brunson", "season": "2022-23", "category": "Known Breakout"},
        {"name": "Tyrese Haliburton", "season": "2020-21", "category": "Known Breakout"},
        {"name": "Tyrese Maxey", "season": "2020-21", "category": "Known Breakout"},
        {"name": "Ben Simmons", "season": "2020-21", "category": "Known Non-Star"},
        {"name": "T.J. McConnell", "season": "2020-21", "category": "Known Non-Star"},
        {"name": "Cory Joseph", "season": "2020-21", "category": "Known Non-Star"},
    ]
    
    results = []
    for case in test_cases:
        player_name = case['name']
        season = case['season']
        category = case['category']
        
        player_data = df_features[
            (df_features['PLAYER_NAME'] == player_name) & 
            (df_features['SEASON'] == season)
        ]
        
        if len(player_data) == 0:
            logger.warning(f"No data found for {player_name} {season}")
            continue
        
        player_data = player_data.iloc[0]
        
        passed, signal_results, reason = filters.check_quality_filter(player_data, strict=True)
        completeness, features_present, total_features = filters.calculate_data_completeness(player_data)
        base_signal_strength = filters.calculate_base_signal_strength(player_data)
        
        results.append({
            'player_name': player_name,
            'season': season,
            'category': category,
            'passed_quality_filter': passed,
            'quality_filter_reason': reason,
            'data_completeness': completeness,
            'features_present': features_present,
            'total_features': total_features,
            'base_signal_strength': base_signal_strength,
            **{f'{k}_value': player_data.get(k, np.nan) for k in filters.KEY_FEATURES}
        })
    
    df_results = pd.DataFrame(results)
    
    logger.info("\nQuality Filter Validation Results:")
    logger.info("=" * 80)
    for _, row in df_results.iterrows():
        status = "✅ PASSED" if row['passed_quality_filter'] else "❌ FAILED"
        logger.info(f"{status} {row['player_name']} ({row['season']}) - {row['category']}")
        logger.info(f"  Reason: {row['quality_filter_reason']}")
        logger.info(f"  Data Completeness: {row['data_completeness']:.1%} ({row['features_present']}/{row['total_features']})")
        logger.info(f"  Base Signal Strength: {row['base_signal_strength']:.3f}")
    
    return df_results


def load_and_merge_all_features(results_dir: Path) -> pd.DataFrame:
    """Load and merge all feature files (same as training script)."""
    # Base features
    df_features = pd.read_csv(results_dir / "predictive_dataset.csv")
    
    # Plasticity Features
    plasticity_files = list(results_dir.glob("plasticity_scores_*.csv"))
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
    pressure_path = results_dir / "pressure_features.csv"
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
    physicality_path = results_dir / "physicality_features.csv"
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
    rim_path = results_dir / "rim_pressure_features.csv"
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


if __name__ == "__main__":
    from pathlib import Path
    
    # Load and merge all features
    results_dir = Path("results")
    df_features = load_and_merge_all_features(results_dir)
    
    # Validate filters
    validation_results = validate_filters_on_known_cases(df_features)
    
    # Save results
    output_path = results_dir / "quality_filter_validation.csv"
    validation_results.to_csv(output_path, index=False)
    logger.info(f"\nValidation results saved to {output_path}")

