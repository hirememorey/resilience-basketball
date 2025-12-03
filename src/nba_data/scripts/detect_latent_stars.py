"""
Latent Star Detection: Find "Sleeping Giants"

This script identifies players with high stress vector profiles but low usage,
suggesting they have the potential to scale up in playoffs but haven't been
given the opportunity yet.

The consultant's hypothesis: "Who is paid like a role player ('Sniper') but has
the latent stress profile of a 'King'?"

Key Principles (UPDATED):
1. Filter FIRST (Reference Class) - Define candidate pool (Age < 25, USG < 25%) before ranking
2. Use Stress Vector Composite - Use validated stress vectors with model feature importance weights
3. Normalize within Candidate Pool - All normalization/ranking relative to filtered subset, not entire league
4. Confidence Scores - Flag missing data, no proxies (correlation = 0.0047 invalidates Isolation EFG proxy)

Key Criteria:
1. Age < 25 years old (latent stars must be young)
2. Low usage (< 25% USG in regular season)
3. High stress vector composite score (weighted by model feature importance)
4. High confidence (complete data preferred, but flag low confidence instead of excluding)
"""

import pandas as pd
import numpy as np
import logging
import sys
import joblib
from pathlib import Path
from typing import List, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/latent_star_detection.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class LatentStarDetector:
    """Detect players with high stress profiles but low usage."""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.data_dir = Path("data")
        self.models_dir = Path("models")
        self.results_dir.mkdir(exist_ok=True)
        
        # Load trained model and label encoder
        self.model = None
        self.label_encoder = None
        self.model_features = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained XGBoost model and label encoder."""
        model_path = self.models_dir / "resilience_xgb.pkl"
        encoder_path = self.models_dir / "archetype_encoder.pkl"
        
        if not model_path.exists() or not encoder_path.exists():
            logger.warning("Model files not found. Archetype prediction will be skipped.")
            logger.warning(f"Expected: {model_path} and {encoder_path}")
            return
        
        try:
            self.model = joblib.load(model_path)
            self.label_encoder = joblib.load(encoder_path)
            
            # Get feature names from model (if available)
            if hasattr(self.model, 'feature_names_in_'):
                self.model_features = list(self.model.feature_names_in_)
            else:
                # Fallback: try to get from predictive_features.json if it exists
                import json
                features_path = self.models_dir / "predictive_features.json"
                if features_path.exists():
                    with open(features_path, 'r') as f:
                        self.model_features = json.load(f)
                else:
                    logger.warning("Could not determine model feature names. Will use all available features.")
            
            logger.info(f"Loaded model with {len(self.model_features) if self.model_features else 'unknown'} features")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.warning("Archetype prediction will be skipped.")
    
    def predict_archetypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict archetypes for candidates using the trained model.
        
        Returns DataFrame with PREDICTED_ARCHETYPE and PREDICTED_KING_PROBABILITY columns.
        """
        if self.model is None or self.label_encoder is None:
            logger.warning("Model not loaded. Skipping archetype prediction.")
            df['PREDICTED_ARCHETYPE'] = 'Unknown'
            df['PREDICTED_KING_PROBABILITY'] = 0.0
            return df
        
        df = df.copy()
        
        # Get features that model expects
        if self.model_features:
            # Ensure all model features exist in dataframe (add missing ones with default values)
            for feature in self.model_features:
                if feature not in df.columns:
                    # Add missing feature with default value (0 for clock features, median for others)
                    if 'CLOCK' in feature or 'DELTA' in feature:
                        df[feature] = 0.0
                    else:
                        # Try to infer default from similar features
                        df[feature] = 0.0
                    logger.debug(f"Added missing feature {feature} with default value 0.0")
            
            X = df[self.model_features].copy()
        else:
            # Use all numeric features (fallback)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            # Exclude non-feature columns
            exclude_cols = ['PLAYER_ID', 'AGE', 'USG_PCT', 'SEASON']
            feature_cols = [c for c in numeric_cols if c not in exclude_cols]
            X = df[feature_cols].copy()
            logger.info(f"Using {len(feature_cols)} numeric features for prediction")
        
        # Handle NaN values same way as training (fill with median or 0 for clock features)
        for col in X.columns:
            if X[col].isna().sum() > 0:
                if 'CLOCK' in col:
                    X[col] = X[col].fillna(0)
                else:
                    median_val = X[col].median()
                    X[col] = X[col].fillna(median_val)
        
        try:
            # Predict archetypes
            y_pred = self.model.predict(X)
            y_proba = self.model.predict_proba(X)
            
            # Decode predictions
            df['PREDICTED_ARCHETYPE'] = self.label_encoder.inverse_transform(y_pred)
            
            # Get probability of being "King" (first class in label encoder)
            king_class_idx = list(self.label_encoder.classes_).index('King') if 'King' in self.label_encoder.classes_ else 0
            df['PREDICTED_KING_PROBABILITY'] = y_proba[:, king_class_idx]
            
            logger.info(f"Predicted archetypes for {len(df)} candidates")
            logger.info(f"Archetype distribution: {df['PREDICTED_ARCHETYPE'].value_counts().to_dict()}")
            
        except Exception as e:
            logger.error(f"Error predicting archetypes: {e}")
            df['PREDICTED_ARCHETYPE'] = 'Unknown'
            df['PREDICTED_KING_PROBABILITY'] = 0.0
        
        return df
        
    def load_data(self) -> pd.DataFrame:
        """Load stress vectors and regular season usage data."""
        logger.info("Loading data...")
        
        # Load stress vectors (should already have USG_PCT, AGE, CREATION_BOOST from Phase 1)
        df_features = pd.read_csv(self.results_dir / "predictive_dataset.csv")
        logger.info(f"Loaded {len(df_features)} player-seasons with stress vectors")
        
        # Verify critical columns exist
        required_cols = ['PLAYER_ID', 'SEASON', 'USG_PCT', 'AGE']
        missing_cols = [c for c in required_cols if c not in df_features.columns]
        if missing_cols:
            logger.warning(f"Missing required columns: {missing_cols}. These should be in predictive_dataset.csv from Phase 1.")
        
        # Load pressure features
        pressure_path = self.results_dir / "pressure_features.csv"
        if pressure_path.exists():
            df_pressure = pd.read_csv(pressure_path)
            df_features = df_features.merge(
                df_pressure[['PLAYER_ID', 'SEASON'] + 
                           [c for c in df_pressure.columns if 'PRESSURE' in c or 'CLOCK' in c]],
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )
        
        # Load physicality features
        physicality_path = self.results_dir / "physicality_features.csv"
        if physicality_path.exists():
            df_physicality = pd.read_csv(physicality_path)
            df_features = df_features.merge(
                df_physicality[['PLAYER_ID', 'SEASON'] + 
                             [c for c in df_physicality.columns if 'FTr' in c or 'RIM' in c]],
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )
        
        # USG_PCT and AGE should already be in predictive_dataset.csv from Phase 1
        # Only merge from regular season files if they're missing
        if 'USG_PCT' not in df_features.columns:
            logger.warning("USG_PCT not in predictive_dataset.csv. Attempting to load from regular season files...")
            rs_files = list(self.data_dir.glob("regular_season_*.csv"))
            if rs_files:
                rs_data_list = []
                for rs_file in rs_files:
                    try:
                        season = rs_file.stem.replace("regular_season_", "")
                        df_rs = pd.read_csv(rs_file)
                        df_rs['SEASON'] = season
                        if 'PLAYER_ID' in df_rs.columns and 'USG_PCT' in df_rs.columns:
                            rs_data_list.append(df_rs[['PLAYER_ID', 'SEASON', 'USG_PCT']])
                    except Exception as e:
                        logger.warning(f"Error loading {rs_file}: {e}")
                        continue
                
                if rs_data_list:
                    df_rs_usage = pd.concat(rs_data_list, ignore_index=True)
                    df_rs_usage = df_rs_usage.groupby(['PLAYER_ID', 'SEASON']).agg({'USG_PCT': 'max'}).reset_index()
                    df_features = df_features.merge(df_rs_usage, on=['PLAYER_ID', 'SEASON'], how='left')
                    logger.info(f"Merged usage data for {df_features['USG_PCT'].notna().sum()} player-seasons")
                else:
                    logger.error("Could not load USG_PCT from regular season files.")
                    df_features['USG_PCT'] = np.nan
            else:
                logger.error("No regular season files found and USG_PCT not in dataset.")
                df_features['USG_PCT'] = np.nan
        else:
            logger.info(f"USG_PCT already in dataset: {df_features['USG_PCT'].notna().sum()} / {len(df_features)} values")
        
        # Same for AGE
        if 'AGE' not in df_features.columns:
            logger.warning("AGE not in predictive_dataset.csv. This should have been added in Phase 1.")
            df_features['AGE'] = np.nan
        else:
            logger.info(f"AGE already in dataset: {df_features['AGE'].notna().sum()} / {len(df_features)} values")
        
        return df_features
    
    def get_stress_vector_weights(self) -> Dict[str, float]:
        """
        Get stress vector feature importance weights from validated model.
        These weights come from the XGBoost model that achieves 59.4% accuracy.
        """
        # Feature importance weights from model (validated, from predictive_model_report.md)
        # These are the actual weights learned by the model, not arbitrary
        weights = {
            'LEVERAGE_USG_DELTA': 0.092,  # #1 Predictor - Abdication Detector
            'CREATION_VOLUME_RATIO': 0.062,  # Self-creation ability
            'RS_PRESSURE_APPETITE': 0.045,  # Dominance signal
            'EFG_ISO_WEIGHTED': 0.041,  # Isolation efficiency
            'RS_FTr': 0.039,  # Physicality
            'RS_EARLY_CLOCK_PRESSURE_APPETITE': 0.038,  # Early-clock bad shots (negative signal)
            'LATE_CLOCK_PRESSURE_RESILIENCE_DELTA': 0.036,  # Late-clock bailout ability change
            'RS_PRESSURE_RESILIENCE': 0.035,  # Pressure resilience
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE': 0.032,  # Late-clock bailout ability
            'LEVERAGE_TS_DELTA': 0.030,  # Clutch efficiency (if available)
            'CLUTCH_MIN_TOTAL': 0.025,  # Clutch minutes (trust signal)
            'CREATION_TAX': 0.020,  # Creation efficiency cost
            'RS_RIM_PRESSURE_RESILIENCE': 0.018,  # Rim pressure resilience
            'EFG_PCT_0_DRIBBLE': 0.015,  # Catch-and-shoot efficiency
            # Add other stress vector features with lower weights
        }
        return weights
    
    def calculate_stress_composite(self, df: pd.DataFrame, reference_pool: pd.DataFrame = None) -> pd.DataFrame:
        """
        Calculate stress vector composite score using model feature importance weights.
        
        CRITICAL: Normalize within reference pool (candidate pool), not entire league.
        This implements the "Reference Class" principle.
        
        Args:
            df: DataFrame with stress vectors
            reference_pool: Pool to normalize against (if None, uses df itself)
        """
        logger.info("Calculating stress vector composite scores...")
        
        if reference_pool is None:
            reference_pool = df
        
        df = df.copy()
        weights = self.get_stress_vector_weights()
        
        # Filter to existing features
        existing_features = [f for f in weights.keys() if f in df.columns]
        logger.info(f"Using {len(existing_features)} stress vector features for composite scoring")
        
        # Initialize composite score
        df['STRESS_COMPOSITE'] = 0.0
        df['SIGNAL_CONFIDENCE'] = 0.0
        
        # Calculate composite for each feature
        for feature in existing_features:
            weight = weights[feature]
            
            # Check data availability
            has_data = df[feature].notna()
            df.loc[has_data, 'SIGNAL_CONFIDENCE'] += weight * 0.5  # Data available = confidence boost
            
            if has_data.sum() < 10:
                logger.debug(f"Skipping {feature}: insufficient data ({has_data.sum()} valid values)")
                continue
            
            # Normalize within reference pool (percentile-based, more robust)
            # CRITICAL: Normalize relative to reference pool, not entire df
            reference_values = reference_pool[feature].dropna()
            if len(reference_values) < 10:
                logger.debug(f"Skipping {feature}: insufficient reference data")
                continue
            
            # Calculate percentile rank within reference pool
            # CRITICAL: Rank df values relative to reference_pool distribution
            # This implements the "Reference Class" principle
            reference_series = reference_pool[feature].dropna()
            if len(reference_series) > 0:
                # For each value in df, calculate its percentile rank in reference_pool
                df_values = df.loc[has_data, feature]
                # Use numpy searchsorted to find percentile rank
                sorted_ref = np.sort(reference_series.values)
                percentile_ranks = np.searchsorted(sorted_ref, df_values, side='right') / len(sorted_ref) * 100
                df.loc[has_data, f'{feature}_NORMALIZED'] = percentile_ranks
            else:
                df.loc[has_data, f'{feature}_NORMALIZED'] = 50.0  # Default to median if no reference
            
            # Add weighted normalized value to composite
            df.loc[has_data, 'STRESS_COMPOSITE'] += (
                df.loc[has_data, f'{feature}_NORMALIZED'] * weight
            )
        
        # Normalize confidence score (0-1 scale)
        max_confidence = sum(weights.values()) * 0.5  # Max if all features available
        df['SIGNAL_CONFIDENCE'] = df['SIGNAL_CONFIDENCE'] / max_confidence if max_confidence > 0 else 0.0
        df['SIGNAL_CONFIDENCE'] = df['SIGNAL_CONFIDENCE'].clip(0.0, 1.0)
        
        logger.info(f"Calculated stress composite scores for {df['STRESS_COMPOSITE'].notna().sum()} players")
        logger.info(f"Average confidence: {df['SIGNAL_CONFIDENCE'].mean():.3f}")
        
        return df
    
    def identify_latent_stars(self, df: pd.DataFrame, 
                             age_threshold: float = 25.0,
                             usage_threshold: float = 25.0,
                             min_confidence: float = 0.3,
                             leverage_usg_delta_threshold: float = -0.05) -> pd.DataFrame:
        """
        Identify latent stars using filter-first architecture and stress vector composite.
        
        CRITICAL: Filter FIRST (Reference Class), then normalize and rank within candidate pool.
        This implements the "Reference Class" principle - value is relative to the cohort.
        
        Args:
            df: DataFrame with stress vectors, usage data, and age
            age_threshold: Maximum age to be considered "latent star" (default 25.0)
            usage_threshold: Maximum USG% to be considered "low usage" (default 25%)
            min_confidence: Minimum signal confidence to include (default 0.3)
        """
        logger.info("Identifying latent stars using filter-first architecture...")
        logger.info(f"Age threshold: < {age_threshold} years")
        logger.info(f"Usage threshold: < {usage_threshold}%")
        logger.info(f"Minimum confidence: ≥ {min_confidence}")
        logger.info(f"LEVERAGE_USG_DELTA threshold: ≥ {leverage_usg_delta_threshold} (Abdication Detector)")
        
        # STEP 1: FILTER FIRST - Define the candidate pool (Reference Class)
        # This is the critical change - we stop asking "Is Brunson better than LeBron?"
        # and start asking "Is Brunson better than other 24-year-old bench guards?"
        
        df_candidate = df.copy()
        
        # Filter by age FIRST
        if 'AGE' not in df_candidate.columns or df_candidate['AGE'].isna().all():
            logger.warning("AGE column missing or all NaN. Cannot filter by age.")
        else:
            before_age = len(df_candidate)
            df_candidate = df_candidate[df_candidate['AGE'] < age_threshold].copy()
            logger.info(f"After age filter (< {age_threshold}): {len(df_candidate)} players (removed {before_age - len(df_candidate)})")
        
        # Filter by usage
        if 'USG_PCT' not in df_candidate.columns or df_candidate['USG_PCT'].isna().all():
            logger.error("USG_PCT column missing or all NaN. Cannot filter by usage.")
            return pd.DataFrame()
        else:
            # Convert USG_PCT to percentage if needed
            sample_usg = df_candidate['USG_PCT'].dropna()
            if len(sample_usg) > 0:
                max_usg = sample_usg.max()
                if max_usg < 1.0:
                    usage_threshold_decimal = usage_threshold / 100.0
                    before_usage = len(df_candidate)
                    df_candidate = df_candidate[df_candidate['USG_PCT'] < usage_threshold_decimal].copy()
                    logger.info(f"After usage filter (< {usage_threshold}%): {len(df_candidate)} players (removed {before_usage - len(df_candidate)})")
                else:
                    before_usage = len(df_candidate)
                    df_candidate = df_candidate[df_candidate['USG_PCT'] < usage_threshold].copy()
                    logger.info(f"After usage filter (< {usage_threshold}%): {len(df_candidate)} players (removed {before_usage - len(df_candidate)})")
            else:
                logger.warning("No valid USG_PCT values. Cannot filter by usage.")
                return pd.DataFrame()
        
        if len(df_candidate) == 0:
            logger.warning("No players meet age and usage criteria. Try adjusting thresholds.")
            return pd.DataFrame()
        
        # STEP 2: Filter by LEVERAGE_USG_DELTA (Abdication Detector)
        # CRITICAL: Players with negative LEVERAGE_USG_DELTA don't scale up in clutch
        # This is the #1 predictor (9.2% importance) and catches the "Simmons Paradox"
        if 'LEVERAGE_USG_DELTA' in df_candidate.columns:
            before_leverage = len(df_candidate)
            df_candidate = df_candidate[
                df_candidate['LEVERAGE_USG_DELTA'].notna() & 
                (df_candidate['LEVERAGE_USG_DELTA'] >= leverage_usg_delta_threshold)
            ].copy()
            logger.info(f"After LEVERAGE_USG_DELTA filter (≥ {leverage_usg_delta_threshold}): {len(df_candidate)} players (removed {before_leverage - len(df_candidate)})")
            
            if len(df_candidate) == 0:
                logger.warning("No players meet LEVERAGE_USG_DELTA threshold.")
                return pd.DataFrame()
        else:
            logger.warning("LEVERAGE_USG_DELTA not in dataset. Cannot filter by Abdication Detector.")
        
        # STEP 3: Predict archetypes using trained model
        # This captures the interaction of all stress vectors, not just individual ones
        df_candidate = self.predict_archetypes(df_candidate)
        
        # Filter for King or Bulldozer predictions only
        # These are players who will actually perform in playoffs (not just have skills)
        before_archetype = len(df_candidate)
        # Check actual archetype format (may include parentheses)
        unique_archetypes = df_candidate['PREDICTED_ARCHETYPE'].unique()
        logger.info(f"Unique predicted archetypes: {unique_archetypes}")
        
        # Match archetypes that contain "King" or "Bulldozer" (case-insensitive)
        valid_archetypes = df_candidate[
            df_candidate['PREDICTED_ARCHETYPE'].str.contains('King|Bulldozer', case=False, na=False)
        ]['PREDICTED_ARCHETYPE'].unique().tolist()
        
        if not valid_archetypes:
            # Fallback: try exact matches
            valid_archetypes = ['King (Resilient Star)', 'Bulldozer (Fragile Star)', 'King', 'Bulldozer']
            valid_archetypes = [a for a in valid_archetypes if a in unique_archetypes]
        
        logger.info(f"Valid archetypes for filtering: {valid_archetypes}")
        df_candidate = df_candidate[df_candidate['PREDICTED_ARCHETYPE'].isin(valid_archetypes)].copy()
        logger.info(f"After archetype filter (King/Bulldozer only): {len(df_candidate)} players (removed {before_archetype - len(df_candidate)})")
        
        if len(df_candidate) == 0:
            logger.warning("No players predicted as King or Bulldozer.")
            return pd.DataFrame()
        
        # STEP 4: Calculate stress vector composite WITHIN candidate pool
        # CRITICAL: Normalize relative to candidate pool, not entire league
        df_candidate = self.calculate_stress_composite(df_candidate, reference_pool=df_candidate)
        
        # Filter by minimum confidence
        before_confidence = len(df_candidate)
        df_candidate = df_candidate[df_candidate['SIGNAL_CONFIDENCE'] >= min_confidence].copy()
        logger.info(f"After confidence filter (≥ {min_confidence}): {len(df_candidate)} players (removed {before_confidence - len(df_candidate)})")
        
        if len(df_candidate) == 0:
            logger.warning("No players meet confidence threshold.")
            return pd.DataFrame()
        
        # STEP 5: Rank within candidate pool (Z-scores relative to peers)
        # Calculate Z-score relative to candidate pool distribution
        mean_composite = df_candidate['STRESS_COMPOSITE'].mean()
        std_composite = df_candidate['STRESS_COMPOSITE'].std()
        
        if std_composite > 0:
            df_candidate['Z_SCORE'] = (df_candidate['STRESS_COMPOSITE'] - mean_composite) / std_composite
        else:
            df_candidate['Z_SCORE'] = 0.0
        
        # Sort by Z-score (descending) - highest relative to candidate pool peers
        latent_stars = df_candidate.sort_values('Z_SCORE', ascending=False).copy()
        
        logger.info(f"Final latent star candidates: {len(latent_stars)}")
        logger.info(f"Top candidate Z-score: {latent_stars['Z_SCORE'].iloc[0]:.2f}")
        
        return latent_stars
    
    def generate_report(self, latent_stars: pd.DataFrame) -> str:
        """Generate latent star detection report."""
        logger.info("Generating report...")
        
        if len(latent_stars) == 0:
            return "# Latent Star Detection Report\n\nNo latent stars identified."
        
        # Sort by Z-score (already sorted, but ensure it's correct)
        latent_stars_sorted = latent_stars.sort_values('Z_SCORE', ascending=False)
        
        report_lines = [
            "# Latent Star Detection Report: Sleeping Giants",
            "",
            "## Executive Summary",
            "",
            f"This report identifies **{len(latent_stars)}** players with high stress vector profiles",
            "who may be undervalued or underutilized. These 'Sleeping Giants' have the stress",
            "profile of playoff stars but may not have been given the opportunity yet.",
            "",
            "---",
            "",
            "## Methodology (Phase 2 - Updated)",
            "",
            "**Criteria for Latent Stars:**",
            "",
            "1. **Age < 25 years old**: Filter FIRST - latent stars must be young",
            "2. **Low Usage (< 25% USG)**: Identifies players with low opportunity",
            "3. **LEVERAGE_USG_DELTA ≥ -0.05**: Abdication Detector - must scale up in clutch (filters out passivity)",
            "4. **Predicted Archetype (King/Bulldozer)**: Model predicts actual playoff performance, not just skills",
            "5. **Primary Score Ranking**: Ranked by Stress Vector Composite (weighted by model feature importance)",
            "6. **Confidence Score**: Flags data quality (missing data = lower confidence, no proxies)",
            "",
            "**Key Principles:**",
            "- **Filter FIRST (Reference Class)**: Define candidate pool before ranking",
            "- **Normalize within Candidate Pool**: All ranking relative to filtered subset, not entire league",
            "- **Use Validated Stress Vectors**: Model feature importance weights (not arbitrary)",
            "- **No Proxies**: Flag missing data with confidence scores (correlation = 0.0047 invalidates Isolation EFG proxy)",
            "",
            "**Key Stress Vectors Analyzed (from validated model):**",
            "- LEVERAGE_USG_DELTA (9.2%): Clutch usage scaling (Abdication Detector)",
            "- CREATION_VOLUME_RATIO (6.2%): Self-creation ability",
            "- RS_PRESSURE_APPETITE (4.5%): Dominance signal",
            "- EFG_ISO_WEIGHTED (4.1%): Isolation efficiency",
            "- RS_LATE_CLOCK_PRESSURE_RESILIENCE (4.8%): Late-clock bailout ability",
            "- Plus 10+ other validated stress vector features",
            "",
            "---",
            "",
            "## Top Latent Star Candidates",
            "",
            "| Rank | Player | Season | Age | RS USG% | Z-Score | Predicted Archetype | King Prob | Key Strengths |",
            "|------|--------|--------|-----|---------|---------|---------------------|-----------|---------------|"
        ]
        
        # Add top 20 candidates
        top_20 = latent_stars_sorted.head(20)
        
        for idx, (_, row) in enumerate(top_20.iterrows(), 1):
            player = row.get('PLAYER_NAME', 'Unknown')
            season = row.get('SEASON', 'Unknown')
            age = row.get('AGE', 0)
            usg_pct = row.get('USG_PCT', 0)
            # Convert to percentage if stored as decimal
            if usg_pct < 1.0:
                usg_pct = usg_pct * 100
            z_score = row.get('Z_SCORE', 0)
            predicted_archetype = row.get('PREDICTED_ARCHETYPE', 'Unknown')
            king_prob = row.get('PREDICTED_KING_PROBABILITY', 0.0)
            
            # Identify key strengths
            strengths = []
            if row.get('CREATION_VOLUME_RATIO', 0) > 0.5:
                strengths.append("High Creation")
            if row.get('RS_PRESSURE_RESILIENCE', 0) > 0.5:
                strengths.append("Pressure Resilient")
            if row.get('RS_LATE_CLOCK_PRESSURE_RESILIENCE', 0) > 0.5:
                strengths.append("Late-Clock")
            if row.get('LEVERAGE_USG_DELTA', 0) > 0:
                strengths.append("Clutch Scaling")
            if row.get('CREATION_BOOST', 1.0) > 1.0:
                strengths.append("Positive Creation Tax")
            
            strengths_str = ", ".join(strengths) if strengths else "N/A"
            
            report_lines.append(
                f"| {idx} | {player} | {season} | {age:.1f} | {usg_pct:.1f}% | "
                f"{z_score:.2f} | {predicted_archetype} | {king_prob:.2f} | {strengths_str} |"
            )
        
        report_lines.extend([
            "",
            "---",
            "",
            "## Insights",
            "",
            "### What Makes a Latent Star?",
            "",
            "These players share common characteristics:",
            "",
            "1. **Self-Creation Ability**: High Creation Volume Ratio indicates they can",
            "   generate their own offense, critical for playoff success.",
            "",
            "2. **Pressure Resilience**: Ability to make tough shots (high Pressure Resilience)",
            "   suggests they won't shrink in playoff moments.",
            "",
            "3. **Late-Clock Ability**: Players with high Late-Clock Pressure Resilience",
            "   can bail out broken plays, a valuable playoff skill.",
            "",
            "### Why They're Undervalued",
            "",
            "These players may be undervalued because:",
            "",
            "- **Low Usage**: They haven't been given high-usage roles in regular season",
            "- **Role Player Perception**: They're seen as complementary pieces, not stars",
            "- **Small Sample Size**: Limited opportunity to show their stress profile",
            "",
            "### The \"Next Jalen Brunson\" Test",
            "",
            "Jalen Brunson in 2021 (DAL) had a high stress profile but was a backup.",
            "When given opportunity in NYK, he became a star. These candidates may follow",
            "a similar path.",
            "",
            "---",
            "",
            "## Full Results",
            "",
            "See `results/latent_stars.csv` for complete list of candidates.",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def run(self):
        """Run complete latent star detection pipeline."""
        logger.info("=" * 60)
        logger.info("Starting Latent Star Detection")
        logger.info("=" * 60)
        
        # 1. Load data
        df = self.load_data()
        
        # 2. Identify latent stars (filter-first architecture with stress vector composite)
        latent_stars = self.identify_latent_stars(df, age_threshold=25.0, usage_threshold=25.0)
        
        if len(latent_stars) == 0:
            logger.warning("No latent stars identified!")
            return
        
        # 4. Save results
        output_cols = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'AGE', 'USG_PCT', 
                      'STRESS_COMPOSITE', 'Z_SCORE', 'SIGNAL_CONFIDENCE',
                      'PREDICTED_ARCHETYPE', 'PREDICTED_KING_PROBABILITY',
                      'CREATION_VOLUME_RATIO', 'LEVERAGE_USG_DELTA',
                      'RS_PRESSURE_RESILIENCE', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE',
                      'EFG_ISO_WEIGHTED', 'RS_FTr', 'CREATION_BOOST']
        
        output_cols = [c for c in output_cols if c in latent_stars.columns]
        latent_stars[output_cols].to_csv(
            self.results_dir / 'latent_stars.csv',
            index=False
        )
        logger.info(f"Saved {len(latent_stars)} latent stars to {self.results_dir / 'latent_stars.csv'}")
        
        # 5. Generate report
        report = self.generate_report(latent_stars)
        report_path = self.results_dir / 'latent_star_detection_report.md'
        with open(report_path, 'w') as f:
            f.write(report)
        logger.info(f"Saved report to {report_path}")
        
        # 6. Print summary
        logger.info("=" * 60)
        logger.info("Latent Star Detection Complete")
        logger.info("=" * 60)
        logger.info(f"Total latent stars identified: {len(latent_stars)}")
        logger.info("\nTop 5 Candidates:")
        top_5 = latent_stars.head(5)
        for idx, (_, row) in enumerate(top_5.iterrows(), 1):
            logger.info(f"  {idx}. {row.get('PLAYER_NAME', 'Unknown')} ({row.get('SEASON', 'Unknown')}) - "
                       f"Z-Score: {row.get('Z_SCORE', 0):.2f}, Archetype: {row.get('PREDICTED_ARCHETYPE', 'Unknown')}, "
                       f"King Prob: {row.get('PREDICTED_KING_PROBABILITY', 0):.2f}")


def main():
    detector = LatentStarDetector()
    detector.run()


if __name__ == "__main__":
    main()

