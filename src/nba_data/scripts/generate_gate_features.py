"""
Phase 4: Gate-to-Feature Converter


This script converts hard gate logic to soft features that the model can learn.
Instead of 7 hard gates (if/else statements) that cap star-level at 30%, we create
soft features that the model learns patterns from.

Gates Converted:

Abdication Tax Gate → ABDICATION_RISK feature

Fragility Gate → PHYSICALITY_FLOOR feature

Bag Check Gate → SELF_CREATED_FREQ feature (already calculated)

Data Completeness Gate → DATA_COMPLETENESS_SCORE feature

Sample Size Gate → SAMPLE_SIZE_CONFIDENCE feature

Missing Leverage Data → LEVERAGE_DATA_CONFIDENCE feature

Multiple Negative Signals → NEGATIVE_SIGNAL_COUNT feature

Implementation based on PHASE4_IMPLEMENTATION_PLAN.md
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path

Setup Logging

logging.basicConfig(
level=logging.INFO,
format='%(asctime)s - %(levelname)s - %(message)s',
handlers=[
logging.FileHandler("logs/gate_features.log"),
logging.StreamHandler(sys.stdout)
]
)
logger = logging.getLogger(name)

class GateFeatureGenerator:
"""Convert hard gate logic to soft features."""

code
Code
download
content_copy
expand_less
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
    Convert hard gate logic to soft features.
    
    Args:
        df: DataFrame with stress vector features
        
    Returns:
        DataFrame with gate features added
    """
    logger.info("Calculating gate features...")
    
    df = df.copy()
    
    # 1. Abdication Risk (from Negative Signal Gate)
    # ABDICATION_RISK = max(0, -LEVERAGE_USG_DELTA)
    # Higher risk = more negative LEVERAGE_USG_DELTA (passivity)
    if 'LEVERAGE_USG_DELTA' in df.columns:
        df['ABDICATION_RISK'] = df['LEVERAGE_USG_DELTA'].apply(
            lambda x: max(0, -x) if pd.notna(x) else 0.0
        )
        logger.info(f"ABDICATION_RISK: {df['ABDICATION_RISK'].notna().sum()}/{len(df)} values")
    else:
        df['ABDICATION_RISK'] = 0.0
        logger.warning("LEVERAGE_USG_DELTA not found - ABDICATION_RISK set to 0.0")
    
    # 2. Physicality Floor (from Fragility Gate)
    # PHYSICALITY_FLOOR = RS_RIM_APPETITE (absolute frequency)
    # Let model learn threshold instead of hard cap
    if 'RS_RIM_APPETITE' in df.columns:
        df['PHYSICALITY_FLOOR'] = df['RS_RIM_APPETITE'].fillna(0.0)
        logger.info(f"PHYSICALITY_FLOOR: {df['PHYSICALITY_FLOOR'].notna().sum()}/{len(df)} values")
    else:
        df['PHYSICALITY_FLOOR'] = 0.0
        logger.warning("RS_RIM_APPETITE not found - PHYSICALITY_FLOOR set to 0.0")
    
    # 3. Self-Created Frequency (from Bag Check Gate)
    # Calculate if not already present
    if 'SELF_CREATED_FREQ' not in df.columns:
        # Try to calculate from ISO and PNR handler frequencies
        iso_freq = df.get('ISO_FREQUENCY', pd.Series([0.0] * len(df)))
        pnr_freq = df.get('PNR_HANDLER_FREQUENCY', pd.Series([0.0] * len(df)))
        post_freq = df.get('POST_TOUCH_FREQUENCY', pd.Series([0.0] * len(df)))
        
        # Fill NaN with 0
        iso_freq = iso_freq.fillna(0.0)
        pnr_freq = pnr_freq.fillna(0.0)
        post_freq = post_freq.fillna(0.0)
        
        # Include Post Frequency
        df['SELF_CREATED_FREQ'] = iso_freq + pnr_freq + post_freq
        
        # If still missing, use CREATION_VOLUME_RATIO as proxy (conservative estimate)
        if df['SELF_CREATED_FREQ'].isna().all():
            logger.warning("SELF_CREATED_FREQ could not be calculated - using CREATION_VOLUME_RATIO as proxy")
            if 'CREATION_VOLUME_RATIO' in df.columns:
                # Conservative estimate: assume 35% of creation volume is self-created
                df['SELF_CREATED_FREQ'] = df['CREATION_VOLUME_RATIO'].fillna(0.0) * 0.35
            else:
                df['SELF_CREATED_FREQ'] = 0.0
        
        logger.info(f"SELF_CREATED_FREQ: {df['SELF_CREATED_FREQ'].notna().sum()}/{len(df)} values")
    else:
        logger.info(f"SELF_CREATED_FREQ already exists: {df['SELF_CREATED_FREQ'].notna().sum()}/{len(df)} values")
    
    # 4. Data Completeness Score
    # DATA_COMPLETENESS_SCORE = present_features / total_features (0.0 to 1.0)
    present_count = df[self.critical_features].notna().sum(axis=1)
    df['DATA_COMPLETENESS_SCORE'] = present_count / len(self.critical_features)
    logger.info(f"DATA_COMPLETENESS_SCORE: {df['DATA_COMPLETENESS_SCORE'].notna().sum()}/{len(df)} values")
    logger.info(f"  Mean completeness: {df['DATA_COMPLETENESS_SCORE'].mean():.2%}")
    
    # 5. Sample Size Confidence
    # SAMPLE_SIZE_CONFIDENCE = min(1.0, pressure_shots/50, clutch_min/15)
    pressure_shots = df.get('RS_TOTAL_VOLUME', pd.Series([0.0] * len(df))).fillna(0.0)
    clutch_min = df.get('CLUTCH_MIN_TOTAL', pd.Series([0.0] * len(df))).fillna(0.0)
    
    pressure_confidence = (pressure_shots / 50).clip(0, 1.0)
    clutch_confidence = (clutch_min / 15).clip(0, 1.0)
    
    # Geometric mean (both need to be high for high confidence)
    df['SAMPLE_SIZE_CONFIDENCE'] = (pressure_confidence * clutch_confidence) ** 0.5
    logger.info(f"SAMPLE_SIZE_CONFIDENCE: {df['SAMPLE_SIZE_CONFIDENCE'].notna().sum()}/{len(df)} values")
    logger.info(f"  Mean confidence: {df['SAMPLE_SIZE_CONFIDENCE'].mean():.2%}")
    
    # 6. Leverage Data Confidence
    # LEVERAGE_DATA_CONFIDENCE = 1.0 if present else 0.0
    leverage_usg = df.get('LEVERAGE_USG_DELTA', None)
    leverage_ts = df.get('LEVERAGE_TS_DELTA', None)
    
    df['LEVERAGE_DATA_CONFIDENCE'] = (
        (leverage_usg.notna() | leverage_ts.notna()).astype(float)
    )
    logger.info(f"LEVERAGE_DATA_CONFIDENCE: {df['LEVERAGE_DATA_CONFIDENCE'].notna().sum()}/{len(df)} values")
    logger.info(f"  Coverage: {df['LEVERAGE_DATA_CONFIDENCE'].mean():.2%}")
    
    # 7. Negative Signal Count
    # NEGATIVE_SIGNAL_COUNT = count(negative_signals)
    negative_signals = 0
    
    # CREATION_TAX < -0.10 (negative creation efficiency)
    if 'CREATION_TAX' in df.columns:
        negative_signals += (df['CREATION_TAX'] < -0.10).astype(int)
    
    # LEVERAGE_TS_DELTA < -0.15 (declining efficiency in clutch)
    if 'LEVERAGE_TS_DELTA' in df.columns:
        negative_signals += (df['LEVERAGE_TS_DELTA'] < -0.15).astype(int)
    
    # LEVERAGE_USG_DELTA < -0.05 (abdication - already captured in ABDICATION_RISK, but count separately)
    if 'LEVERAGE_USG_DELTA' in df.columns:
        negative_signals += (df['LEVERAGE_USG_DELTA'] < -0.05).astype(int)
    
    df['NEGATIVE_SIGNAL_COUNT'] = negative_signals
    logger.info(f"NEGATIVE_SIGNAL_COUNT: {df['NEGATIVE_SIGNAL_COUNT'].notna().sum()}/{len(df)} values")
    logger.info(f"  Mean negative signals: {df['NEGATIVE_SIGNAL_COUNT'].mean():.2f}")
    logger.info(f"  Players with 2+ negative signals: {(df['NEGATIVE_SIGNAL_COUNT'] >= 2).sum()}")
    
    return df

def save_gate_features(self, df: pd.DataFrame):
    """Save gate features to CSV."""
    output_path = self.results_dir / "gate_features.csv"
    
    # Extract only gate feature columns
    gate_cols = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON']
    gate_cols += [
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

def run(self):
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("Phase 4: Gate Features Generation")
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

if name == "main":
generator = GateFeatureGenerator()
generator.run()