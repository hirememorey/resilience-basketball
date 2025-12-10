"""
Phase 4.2: Gate-to-Feature Converter with Continuous Gradients

This script converts hard gate logic to soft features with continuous gradients
that the model can learn. Instead of binary pass/fail gates, we create continuous
risk scores that preserve information about the magnitude of flaws.

Key Innovation: "Risk Amplification"
- Convert binary gates to continuous gradients (distance from threshold)
- Add explicit "Volume × Flaw" interaction terms
- Preserve variance (don't cap, let model learn the penalty)

New Features:
1. RIM_PRESSURE_DEFICIT: Normalized distance below rim pressure threshold (0.0 = safe, 1.0 = zero rim pressure)
2. ABDICATION_MAGNITUDE: Normalized magnitude of negative leverage delta (with Smart Deference exemption)
3. INEFFICIENT_VOLUME_SCORE: Interaction of Usage × Volume × Negative Creation Tax (enhanced Dec 9-10, 2025)
4. SYSTEM_DEPENDENCE_SCORE: Interaction of Usage × (Assisted% + Open Shot%)
5. EMPTY_CALORIES_RISK: USG_PCT × RIM_PRESSURE_DEFICIT (high usage + no rim pressure = disaster)

Implementation based on feedback: "Internalizing Constraints (Moving from Gates to Gradients)"
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/gate_features.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class GateFeatureGenerator:
    """Convert hard gate logic to soft features with continuous gradients."""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Critical features for data completeness calculation
        self.critical_features = [
            'CREATION_VOLUME_RATIO',
            'CREATION_TAX',
            'LEVERAGE_USG_DELTA',
            'LEVERAGE_TS_DELTA',
            'RS_PRESSURE_APPETITE',
            'RS_PRESSURE_RESILIENCE',
        ]
        
        # Rim pressure threshold (bottom 20th percentile from qualified players)
        # This should be calculated from actual data, but using known value for now
        self.rim_pressure_threshold = 0.1746  # Bottom 20th percentile
        
    def _calculate_assisted_fgm_pct(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate ASSISTED_FGM_PCT using same logic as calculate_dependence_score.py.
        
        Tries multiple methods:
        1. catch_shoot_field_goals_made / total_field_goals_made
        2. (pull_up + drive) as proxy for unassisted
        3. CREATION_VOLUME_RATIO as inverse proxy (last resort)
        """
        assisted_pct = pd.Series([None] * len(df), index=df.index)
        
        # Method 1: Try catch-shoot data (if available)
        catch_shoot_cols = ['catch_shoot_field_goals_made', 'RS_CATCH_SHOOT_FGM', 'CATCH_SHOOT_FGM']
        total_fgm_cols = ['field_goals_made', 'FGM', 'RS_FGM', 'TOTAL_FGM']
        
        catch_shoot_col = None
        total_fgm_col = None
        
        for col in catch_shoot_cols:
            if col in df.columns:
                catch_shoot_col = col
                break
        
        for col in total_fgm_cols:
            if col in df.columns:
                total_fgm_col = col
                break
        
        if catch_shoot_col and total_fgm_col:
            catch_shoot = df[catch_shoot_col].fillna(0.0)
            total_fgm = df[total_fgm_col].fillna(0.0)
            mask = total_fgm > 0
            assisted_pct.loc[mask] = (catch_shoot.loc[mask] / total_fgm.loc[mask]).clip(0, 1.0)
            logger.info(f"  Method 1 (catch-shoot): Calculated for {(assisted_pct.notna()).sum()} player-seasons")
        
        # Method 2: Use pull-up + drive as proxy for unassisted
        if assisted_pct.isna().any():
            pull_up_cols = ['pull_up_field_goals_made', 'RS_PULL_UP_FGM', 'PULL_UP_FGM']
            drive_cols = ['drive_field_goals_made', 'RS_DRIVE_FGM', 'DRIVE_FGM']
            
            pull_up_col = None
            drive_col = None
            
            for col in pull_up_cols:
                if col in df.columns:
                    pull_up_col = col
                    break
            
            for col in drive_cols:
                if col in df.columns:
                    drive_col = col
                    break
            
            if pull_up_col and drive_col and total_fgm_col:
                pull_up = df[pull_up_col].fillna(0.0)
                drive = df[drive_col].fillna(0.0)
                total_fgm = df[total_fgm_col].fillna(0.0)
                
                mask = (assisted_pct.isna()) & (total_fgm > 0)
                unassisted = (pull_up.loc[mask] + drive.loc[mask])
                assisted_pct.loc[mask] = (1.0 - (unassisted / total_fgm.loc[mask])).clip(0, 1.0)
                logger.info(f"  Method 2 (pull-up + drive): Calculated for {(assisted_pct.notna() & mask).sum()} additional player-seasons")
        
        # Method 3: Use CREATION_VOLUME_RATIO as inverse proxy (last resort)
        if assisted_pct.isna().any() and 'CREATION_VOLUME_RATIO' in df.columns:
            creation_vol = df['CREATION_VOLUME_RATIO'].fillna(0.0)
            mask = assisted_pct.isna()
            # Inverse relationship: if creation_vol_ratio is 0.5, assume 50% unassisted
            # So assisted = 1 - creation_vol_ratio (rough proxy)
            assisted_pct.loc[mask] = (1.0 - creation_vol.loc[mask].clip(0, 1.0))
            logger.info(f"  Method 3 (CREATION_VOLUME_RATIO proxy): Calculated for {(assisted_pct.notna() & mask).sum()} additional player-seasons")
        
        # Fill any remaining NaN with 0.0
        assisted_pct = assisted_pct.fillna(0.0)
        
        return assisted_pct
    
    def load_data(self) -> pd.DataFrame:
        """Load predictive dataset with all features."""
        logger.info("Loading predictive dataset...")
        
        df = pd.read_csv(self.results_dir / "predictive_dataset.csv")
        
        # Merge with pressure features if available
        pressure_path = self.results_dir / "pressure_features.csv"
        if pressure_path.exists():
            df_pressure = pd.read_csv(pressure_path)
            df = pd.merge(
                df,
                df_pressure,
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_pressure')
            )
            cols_to_drop = [c for c in df.columns if '_pressure' in c]
            df = df.drop(columns=cols_to_drop)
            logger.info(f"Merged with pressure features: {len(df)} rows")
        
        # Merge with physicality features if available
        physicality_path = self.results_dir / "physicality_features.csv"
        if physicality_path.exists():
            df_physicality = pd.read_csv(physicality_path)
            df = pd.merge(
                df,
                df_physicality,
                on=['PLAYER_NAME', 'SEASON'],
                how='left',
                suffixes=('', '_phys')
            )
            cols_to_drop = [c for c in df.columns if '_phys' in c]
            df = df.drop(columns=cols_to_drop)
            logger.info(f"Merged with physicality features: {len(df)} rows")
        
        # Merge with rim pressure features if available
        rim_path = self.results_dir / "rim_pressure_features.csv"
        if rim_path.exists():
            df_rim = pd.read_csv(rim_path)
            df = pd.merge(
                df,
                df_rim,
                on=['PLAYER_NAME', 'SEASON'],
                how='left',
                suffixes=('', '_rim')
            )
            cols_to_drop = [c for c in df.columns if '_rim' in c]
            df = df.drop(columns=cols_to_drop)
            logger.info(f"Merged with rim pressure features: {len(df)} rows")
        
        logger.info(f"Total dataset size: {len(df)} player-seasons")
        return df
    
    def calculate_gate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert hard gate logic to soft features with continuous gradients.
        
        Args:
            df: DataFrame with stress vector features
            
        Returns:
            DataFrame with gate features added
        """
        logger.info("Calculating gate features with continuous gradients...")
        
        df = df.copy()
        
        # ========== CONTINUOUS GRADIENT FEATURES ==========
        
        # 1. RIM_PRESSURE_DEFICIT: Normalized distance below threshold
        # Formula: max(0, threshold - RS_RIM_APPETITE) / threshold
        # Result: 0.0 (safe) to 1.0 (zero rim pressure)
        if 'RS_RIM_APPETITE' in df.columns:
            rim_appetite = df['RS_RIM_APPETITE'].fillna(0.0)
            df['RIM_PRESSURE_DEFICIT'] = (
                np.maximum(0, self.rim_pressure_threshold - rim_appetite) / self.rim_pressure_threshold
            ).clip(0, 1.0)
            logger.info(f"RIM_PRESSURE_DEFICIT: {df['RIM_PRESSURE_DEFICIT'].notna().sum()}/{len(df)} values")
            logger.info(f"  Mean deficit: {df['RIM_PRESSURE_DEFICIT'].mean():.3f}")
            logger.info(f"  Players with deficit > 0.5: {(df['RIM_PRESSURE_DEFICIT'] > 0.5).sum()}")
        else:
            df['RIM_PRESSURE_DEFICIT'] = 0.0
            logger.warning("RS_RIM_APPETITE not found - RIM_PRESSURE_DEFICIT set to 0.0")
        
        # 2. ABDICATION_MAGNITUDE: Normalized magnitude of negative leverage delta
        # Formula: max(0, -LEVERAGE_USG_DELTA) / 0.10 (normalize to 0-1 scale)
        # BUT: Apply Smart Deference exemption (if LEVERAGE_TS_DELTA > 0.05, it's smart play, not abdication)
        if 'LEVERAGE_USG_DELTA' in df.columns and 'LEVERAGE_TS_DELTA' in df.columns:
            leverage_usg = df['LEVERAGE_USG_DELTA'].fillna(0.0)
            leverage_ts = df['LEVERAGE_TS_DELTA'].fillna(0.0)
            
            # Calculate raw abdication magnitude
            raw_abdication = np.maximum(0, -leverage_usg) / 0.10  # Normalize to 0-1 scale
            
            # Smart Deference exemption: If TS delta is positive (>0.05), it's smart play, not abdication
            smart_deference_mask = leverage_ts > 0.05
            df['ABDICATION_MAGNITUDE'] = np.where(smart_deference_mask, 0.0, raw_abdication).clip(0, 1.0)
            
            logger.info(f"ABDICATION_MAGNITUDE: {df['ABDICATION_MAGNITUDE'].notna().sum()}/{len(df)} values")
            logger.info(f"  Mean magnitude: {df['ABDICATION_MAGNITUDE'].mean():.3f}")
            logger.info(f"  Players with magnitude > 0.5: {(df['ABDICATION_MAGNITUDE'] > 0.5).sum()}")
            logger.info(f"  Smart Deference exemptions: {smart_deference_mask.sum()}")
        else:
            df['ABDICATION_MAGNITUDE'] = 0.0
            logger.warning("LEVERAGE_USG_DELTA or LEVERAGE_TS_DELTA not found - ABDICATION_MAGNITUDE set to 0.0")
        
        # Keep old ABDICATION_RISK for backward compatibility (but prefer ABDICATION_MAGNITUDE)
        if 'LEVERAGE_USG_DELTA' in df.columns:
            df['ABDICATION_RISK'] = df['LEVERAGE_USG_DELTA'].apply(
                lambda x: max(0, -x) if pd.notna(x) else 0.0
            )
        else:
            df['ABDICATION_RISK'] = 0.0
        
        # 3. INEFFICIENT_VOLUME_SCORE: Multi-Signal Inefficiency Penalty
        # Formula: USG_PCT × CREATION_VOLUME_RATIO × combined_inefficiency
        #   where combined_inefficiency = max(0, -CREATION_TAX) + max(0, -SHOT_QUALITY_GENERATION_DELTA) + max(0, -LEVERAGE_TS_DELTA)
        # Result: High usage + high volume + multiple inefficiency signals generates huge penalty
        # Enhancement (Dec 9, 2025): Added USG_PCT to strengthen signal - penalizes inefficiency scaled by usage level
        # Enhancement (Dec 9, 2025): Multi-signal approach - combines self-relative (CREATION_TAX), league-relative (SQ_DELTA), and clutch (LEVERAGE_TS_DELTA) inefficiency
        if 'CREATION_VOLUME_RATIO' in df.columns and 'CREATION_TAX' in df.columns:
            creation_vol = df['CREATION_VOLUME_RATIO'].fillna(0.0)
            creation_tax = df['CREATION_TAX'].fillna(0.0)
            
            # Multi-signal inefficiency: Combine multiple inefficiency signals
            # 1. CREATION_TAX: Self-relative inefficiency (how much efficiency drops when creating)
            negative_tax_magnitude = np.maximum(0, -creation_tax)
            
            # 2. SHOT_QUALITY_GENERATION_DELTA: League-relative inefficiency (how much worse than replacement)
            sq_delta = df.get('SHOT_QUALITY_GENERATION_DELTA', pd.Series([0.0] * len(df)))
            if isinstance(sq_delta, pd.Series):
                sq_delta = sq_delta.fillna(0.0)
            else:
                sq_delta = pd.Series([0.0] * len(df))
            negative_sq_magnitude = np.maximum(0, -sq_delta)
            
            # 3. LEVERAGE_TS_DELTA: Clutch inefficiency (how much efficiency drops under pressure)
            leverage_ts = df.get('LEVERAGE_TS_DELTA', pd.Series([0.0] * len(df)))
            if isinstance(leverage_ts, pd.Series):
                leverage_ts = leverage_ts.fillna(0.0)
            else:
                leverage_ts = pd.Series([0.0] * len(df))
            negative_leverage_magnitude = np.maximum(0, -leverage_ts)
            
            # Combined inefficiency signal: Sum of all negative inefficiency magnitudes
            # This captures inefficiency across multiple dimensions (self-relative, league-relative, clutch)
            combined_inefficiency = negative_tax_magnitude + negative_sq_magnitude + negative_leverage_magnitude
            
            # Base interaction: Volume × Combined Inefficiency (linear)
            base_score = creation_vol * combined_inefficiency
            
            # Enhancement: Scale by usage level (USG_PCT) if available
            if 'USG_PCT' in df.columns:
                usg_pct = df['USG_PCT'].fillna(0.0)
                # Normalize USG_PCT from percentage (26.0) to decimal (0.26) if needed
                if usg_pct.max() > 1.0:
                    usg_pct = usg_pct / 100.0
                    logger.info(f"Normalized USG_PCT for INEFFICIENT_VOLUME_SCORE calculation")
                
                # Triple interaction: Usage × Volume × Combined Inefficiency
                df['INEFFICIENT_VOLUME_SCORE'] = usg_pct * base_score
            else:
                # Fallback to original formula if USG_PCT not available
                df['INEFFICIENT_VOLUME_SCORE'] = base_score
                logger.warning("USG_PCT not found - using CREATION_VOLUME_RATIO × combined inefficiency only")
            
            logger.info(f"INEFFICIENT_VOLUME_SCORE (multi-signal enhanced): {df['INEFFICIENT_VOLUME_SCORE'].notna().sum()}/{len(df)} values")
            logger.info(f"  Mean score: {df['INEFFICIENT_VOLUME_SCORE'].mean():.3f}")
            logger.info(f"  Players with score > 0.1: {(df['INEFFICIENT_VOLUME_SCORE'] > 0.1).sum()}")
            logger.info(f"  Using multi-signal approach: CREATION_TAX + SHOT_QUALITY_GENERATION_DELTA + LEVERAGE_TS_DELTA")
        else:
            df['INEFFICIENT_VOLUME_SCORE'] = 0.0
            logger.warning("CREATION_VOLUME_RATIO or CREATION_TAX not found - INEFFICIENT_VOLUME_SCORE set to 0.0")
        
        # 4. SYSTEM_DEPENDENCE_SCORE: Interaction of Usage × (Assisted% + Open Shot%)
        # Formula: USG_PCT × (ASSISTED_FGM_PCT + OPEN_SHOT_FREQUENCY)
        # Result: High usage players who rely on system/gravity get penalized
        if 'USG_PCT' in df.columns:
            # CRITICAL: Normalize USG_PCT from percentage (26.0) to decimal (0.26)
            # The dataset stores USG_PCT as percentage, but we need decimal for calculations
            usg_pct = df['USG_PCT'].fillna(0.0)
            if usg_pct.max() > 1.0:
                usg_pct = usg_pct / 100.0
                logger.info(f"Normalized USG_PCT from percentage to decimal format (max was {df['USG_PCT'].max():.1f})")
            
            # Calculate assisted percentage (if available, or calculate on-the-fly)
            if 'ASSISTED_FGM_PCT' in df.columns:
                assisted_pct = df['ASSISTED_FGM_PCT'].fillna(0.0)
            else:
                # Calculate ASSISTED_FGM_PCT on-the-fly using same logic as calculate_dependence_score.py
                logger.info("ASSISTED_FGM_PCT not found - calculating from available data...")
                assisted_pct = self._calculate_assisted_fgm_pct(df)
                # Store it in the dataframe for future use
                df['ASSISTED_FGM_PCT'] = assisted_pct
                logger.info(f"  Calculated ASSISTED_FGM_PCT for {assisted_pct.notna().sum()}/{len(df)} player-seasons")
                logger.info(f"  Mean assisted %: {assisted_pct.mean():.3f}")
            
            # Calculate open shot frequency (if available)
            if 'RS_OPEN_SHOT_FREQUENCY' in df.columns:
                open_shot_freq = df['RS_OPEN_SHOT_FREQUENCY'].fillna(0.0)
            else:
                # Try alternative column names
                open_shot_freq = df.get('OPEN_SHOT_FREQUENCY', pd.Series([0.0] * len(df))).fillna(0.0)
                if open_shot_freq.isna().all():
                    logger.warning("Open shot frequency not found - using 0.0")
                    open_shot_freq = pd.Series([0.0] * len(df))
            
            # System dependence = assisted% + open shot%
            system_dependence = (assisted_pct + open_shot_freq).clip(0, 1.0)
            
            # Interaction: Usage × System Dependence
            df['SYSTEM_DEPENDENCE_SCORE'] = usg_pct * system_dependence
            
            logger.info(f"SYSTEM_DEPENDENCE_SCORE: {df['SYSTEM_DEPENDENCE_SCORE'].notna().sum()}/{len(df)} values")
            logger.info(f"  Mean score: {df['SYSTEM_DEPENDENCE_SCORE'].mean():.3f}")
            logger.info(f"  Players with score > 0.15: {(df['SYSTEM_DEPENDENCE_SCORE'] > 0.15).sum()}")
        else:
            df['SYSTEM_DEPENDENCE_SCORE'] = 0.0
            logger.warning("USG_PCT not found - SYSTEM_DEPENDENCE_SCORE set to 0.0")
        
        # ========== EXPLICIT VOLUME × FLAW INTERACTION TERMS ==========
        
        # 5. EMPTY_CALORIES_RISK: USG_PCT × RIM_PRESSURE_DEFICIT
        # High usage + no rim pressure = disaster (D'Angelo Russell pattern)
        if 'USG_PCT' in df.columns and 'RIM_PRESSURE_DEFICIT' in df.columns:
            # USG_PCT should already be normalized above, but ensure it's decimal format
            usg_pct = df['USG_PCT'].fillna(0.0)
            if usg_pct.max() > 1.0:
                usg_pct = usg_pct / 100.0
            rim_deficit = df['RIM_PRESSURE_DEFICIT']
            
            df['EMPTY_CALORIES_RISK'] = usg_pct * rim_deficit
            
            logger.info(f"EMPTY_CALORIES_RISK: {df['EMPTY_CALORIES_RISK'].notna().sum()}/{len(df)} values")
            logger.info(f"  Mean risk: {df['EMPTY_CALORIES_RISK'].mean():.3f}")
            logger.info(f"  Players with risk > 0.10: {(df['EMPTY_CALORIES_RISK'] > 0.10).sum()}")
        else:
            df['EMPTY_CALORIES_RISK'] = 0.0
            logger.warning("USG_PCT or RIM_PRESSURE_DEFICIT not found - EMPTY_CALORIES_RISK set to 0.0")
        
        # ========== PORTABLE VOLUME FEATURES (Phase 2: Upstream Dependence) ==========
        
        # 6. PORTABLE_USG_PCT: Raw Usage discounted by Dependence Score
        # Formula: USG_PCT * (1 - DEPENDENCE_SCORE)
        # Logic: If a player uses 30% of possessions but has 50% dependence, their portable usage is only 15%
        # This helps the model distinguish "Nutritious Usage" from "Empty Calories"
        if 'USG_PCT' in df.columns:
            # Ensure USG_PCT is in decimal format
            usg_pct = df['USG_PCT'].fillna(0.0)
            if usg_pct.max() > 1.0:
                usg_pct = usg_pct / 100.0
            
            # Get DEPENDENCE_SCORE (from Phase 1 - may be NaN if not calculated yet)
            if 'DEPENDENCE_SCORE' in df.columns:
                dependence_score = df['DEPENDENCE_SCORE'].fillna(0.0).clip(0, 1.0)
                df['PORTABLE_USG_PCT'] = usg_pct * (1.0 - dependence_score)
                
                logger.info(f"PORTABLE_USG_PCT: {df['PORTABLE_USG_PCT'].notna().sum()}/{len(df)} values")
                logger.info(f"  Mean portable usage: {df['PORTABLE_USG_PCT'].mean():.3f}")
                logger.info(f"  Mean raw usage: {usg_pct.mean():.3f}")
                logger.info(f"  Mean dependence: {dependence_score.mean():.3f}")
                logger.info(f"  Coverage: {dependence_score.notna().sum()}/{len(df)} have dependence scores")
            else:
                # If DEPENDENCE_SCORE not available, set portable = raw (no discount)
                df['PORTABLE_USG_PCT'] = usg_pct
                logger.warning("DEPENDENCE_SCORE not found - PORTABLE_USG_PCT = USG_PCT (no discount)")
        else:
            df['PORTABLE_USG_PCT'] = 0.0
            logger.warning("USG_PCT not found - PORTABLE_USG_PCT set to 0.0")
        
        # 7. PORTABLE_CREATION_VOLUME: Creation Volume discounted by negative efficiency tax
        # Formula: CREATION_VOLUME_RATIO * (1 + min(0, CREATION_TAX))
        # Logic: If creation tax is negative (efficiency drops when creating), discount the volume
        # This penalizes "Empty Calories" creators (high volume + negative tax)
        if 'CREATION_VOLUME_RATIO' in df.columns and 'CREATION_TAX' in df.columns:
            creation_vol = df['CREATION_VOLUME_RATIO'].fillna(0.0)
            creation_tax = df['CREATION_TAX'].fillna(0.0)
            
            # Discount factor: 1 + min(0, tax) means:
            # - If tax is positive (0.1): discount = 1.0 (no discount)
            # - If tax is negative (-0.1): discount = 0.9 (10% discount)
            # - If tax is very negative (-0.2): discount = 0.8 (20% discount)
            discount_factor = 1.0 + np.minimum(0, creation_tax)
            df['PORTABLE_CREATION_VOLUME'] = creation_vol * discount_factor.clip(0, 1.0)
            
            logger.info(f"PORTABLE_CREATION_VOLUME: {df['PORTABLE_CREATION_VOLUME'].notna().sum()}/{len(df)} values")
            logger.info(f"  Mean portable creation: {df['PORTABLE_CREATION_VOLUME'].mean():.3f}")
            logger.info(f"  Mean raw creation: {creation_vol.mean():.3f}")
            logger.info(f"  Players with negative tax: {(creation_tax < 0).sum()}")
        else:
            df['PORTABLE_CREATION_VOLUME'] = 0.0
            logger.warning("CREATION_VOLUME_RATIO or CREATION_TAX not found - PORTABLE_CREATION_VOLUME set to 0.0")
        
        # ========== LEGACY FEATURES (for backward compatibility) ==========
        
        # Physicality Floor (keep for backward compatibility, but RIM_PRESSURE_DEFICIT is preferred)
        if 'RS_RIM_APPETITE' in df.columns:
            df['PHYSICALITY_FLOOR'] = df['RS_RIM_APPETITE'].fillna(0.0)
        else:
            df['PHYSICALITY_FLOOR'] = 0.0
        
        # Self-Created Frequency (from Bag Check Gate)
        if 'SELF_CREATED_FREQ' not in df.columns:
            iso_freq = df.get('ISO_FREQUENCY', pd.Series([0.0] * len(df))).fillna(0.0)
            pnr_freq = df.get('PNR_HANDLER_FREQUENCY', pd.Series([0.0] * len(df))).fillna(0.0)
            post_freq = df.get('POST_TOUCH_FREQUENCY', pd.Series([0.0] * len(df))).fillna(0.0)
            df['SELF_CREATED_FREQ'] = iso_freq + pnr_freq + post_freq
            
            if df['SELF_CREATED_FREQ'].isna().all():
                if 'CREATION_VOLUME_RATIO' in df.columns:
                    df['SELF_CREATED_FREQ'] = df['CREATION_VOLUME_RATIO'].fillna(0.0) * 0.35
                else:
                    df['SELF_CREATED_FREQ'] = 0.0
        
        # Data Completeness Score
        present_count = df[self.critical_features].notna().sum(axis=1)
        df['DATA_COMPLETENESS_SCORE'] = present_count / len(self.critical_features)
        
        # Sample Size Confidence
        pressure_shots = df.get('RS_TOTAL_VOLUME', pd.Series([0.0] * len(df))).fillna(0.0)
        clutch_min = df.get('CLUTCH_MIN_TOTAL', pd.Series([0.0] * len(df))).fillna(0.0)
        pressure_confidence = (pressure_shots / 50).clip(0, 1.0)
        clutch_confidence = (clutch_min / 15).clip(0, 1.0)
        df['SAMPLE_SIZE_CONFIDENCE'] = (pressure_confidence * clutch_confidence) ** 0.5
        
        # Leverage Data Confidence
        leverage_usg = df.get('LEVERAGE_USG_DELTA', None)
        leverage_ts = df.get('LEVERAGE_TS_DELTA', None)
        df['LEVERAGE_DATA_CONFIDENCE'] = (
            (leverage_usg.notna() | leverage_ts.notna()).astype(float)
        )
        
        # Negative Signal Count
        negative_signals = 0
        if 'CREATION_TAX' in df.columns:
            negative_signals += (df['CREATION_TAX'] < -0.10).astype(int)
        if 'LEVERAGE_TS_DELTA' in df.columns:
            negative_signals += (df['LEVERAGE_TS_DELTA'] < -0.15).astype(int)
        if 'LEVERAGE_USG_DELTA' in df.columns:
            negative_signals += (df['LEVERAGE_USG_DELTA'] < -0.05).astype(int)
        df['NEGATIVE_SIGNAL_COUNT'] = negative_signals
        
        logger.info("=" * 60)
        logger.info("Gate features calculation complete!")
        logger.info("=" * 60)
        
        return df
    
    def save_gate_features(self, df: pd.DataFrame):
        """Save gate features to CSV."""
        output_path = self.results_dir / "gate_features.csv"
        
        # Extract gate feature columns (new + legacy)
        gate_cols = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON']
        gate_cols += [
            # New continuous gradient features
            'RIM_PRESSURE_DEFICIT',
            'ABDICATION_MAGNITUDE',
            'INEFFICIENT_VOLUME_SCORE',
            'SYSTEM_DEPENDENCE_SCORE',
            'EMPTY_CALORIES_RISK',
            # Portable volume features (Phase 2: Upstream Dependence)
            'PORTABLE_USG_PCT',
            'PORTABLE_CREATION_VOLUME',
            # Calculated intermediate features
            'ASSISTED_FGM_PCT',  # Calculated for SYSTEM_DEPENDENCE_SCORE
            # Legacy features (for backward compatibility)
            'ABDICATION_RISK',
            'PHYSICALITY_FLOOR',
            'SELF_CREATED_FREQ',
            'DATA_COMPLETENESS_SCORE',
            'SAMPLE_SIZE_CONFIDENCE',
            'LEVERAGE_DATA_CONFIDENCE',
            'NEGATIVE_SIGNAL_COUNT',
        ]
        
        # Filter to columns that exist
        gate_cols = [c for c in gate_cols if c in df.columns]
        
        df_gate = df[gate_cols].copy()
        df_gate.to_csv(output_path, index=False)
        logger.info(f"Saved gate features to {output_path}")
        logger.info(f"Total gate features: {len(gate_cols) - 3} (excluding ID columns)")
        logger.info(f"  New continuous gradients: 5")
        logger.info(f"  Portable volume features: 2")
        logger.info(f"  Legacy features: {len(gate_cols) - 10}")
    
    def run(self):
        """Main execution function."""
        logger.info("=" * 60)
        logger.info("Phase 4.2: Gate Features Generation (Continuous Gradients)")
        logger.info("=" * 60)
        
        # Load data
        df = self.load_data()
        
        # Calculate gate features
        df_with_gates = self.calculate_gate_features(df)
        
        # Save gate features
        self.save_gate_features(df_with_gates)
        
        logger.info("=" * 60)
        logger.info("Gate features generation complete!")
        logger.info("=" * 60)


if __name__ == "__main__":
    generator = GateFeatureGenerator()
    generator.run()
