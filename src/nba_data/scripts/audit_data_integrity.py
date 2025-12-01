import pandas as pd
import numpy as np
import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_file_existence_and_size(path_pattern):
    """Check if files matching pattern exist and are not empty."""
    files = list(Path('data').glob(path_pattern))
    if not files:
        logger.error(f"❌ No files found matching {path_pattern}")
        return False
        
    all_good = True
    for f in files:
        if f.stat().st_size == 0:
            logger.error(f"❌ File {f.name} is empty!")
            all_good = False
        else:
            # Check row count
            try:
                df = pd.read_csv(f)
                if len(df) == 0:
                    logger.error(f"❌ File {f.name} has 0 rows!")
                    all_good = False
                else:
                    logger.info(f"✅ {f.name}: {len(df)} rows")
            except Exception as e:
                logger.error(f"❌ Could not read {f.name}: {e}")
                all_good = False
    return all_good

def check_nulls(df, name, critical_cols):
    """Check for nulls in critical columns."""
    logger.info(f"\nChecking NULLs in {name}...")
    has_issues = False
    for col in critical_cols:
        if col not in df.columns:
            logger.error(f"❌ Critical column '{col}' missing in {name}")
            has_issues = True
            continue
            
        null_count = df[col].isnull().sum()
        if null_count > 0:
            logger.warning(f"⚠️  Column '{col}' has {null_count} NULLs ({null_count/len(df):.1%})")
            # It might be okay, but worth noting
        else:
            logger.info(f"✅ Column '{col}' is clean")
    return not has_issues

def trace_player(player_name, season):
    """Trace a player through the pipeline."""
    logger.info(f"\nTracing {player_name} for {season}...")
    
    # 1. Regular Season
    rs_path = Path(f"data/regular_season_{season}.csv")
    if rs_path.exists():
        rs_df = pd.read_csv(rs_path)
        player_rs = rs_df[rs_df['PLAYER_NAME'] == player_name]
        if not player_rs.empty:
            logger.info(f"✅ Found in Regular Season Stats (ID: {player_rs['PLAYER_ID'].values[0]})")
            player_id = player_rs['PLAYER_ID'].values[0]
        else:
            logger.error(f"❌ {player_name} NOT found in {rs_path}")
            return
    else:
        logger.error(f"❌ Missing {rs_path}")
        return

    # 2. Game Logs
    logs_path = Path(f"data/rs_game_logs_{season}.csv")
    if logs_path.exists():
        logs_df = pd.read_csv(logs_path)
        player_logs = logs_df[logs_df['PLAYER_ID'] == player_id]
        if not player_logs.empty:
            logger.info(f"✅ Found {len(player_logs)} game logs")
        else:
            logger.error(f"❌ No game logs found for ID {player_id}")
    
    # 3. Predictive Features
    feat_path = Path(f"data/predictive_features_{season}.csv")
    if feat_path.exists():
        feat_df = pd.read_csv(feat_path)
        player_feat = feat_df[feat_df['PLAYER_ID'] == player_id]
        if not player_feat.empty:
            logger.info(f"✅ Found in Predictive Features")
            logger.info(f"   - Games vs Top 10: {player_feat['games_vs_top10'].values[0]}")
            logger.info(f"   - Consistency (GmSc Std): {player_feat['consistency_gmsc_std'].values[0]:.2f}")
        else:
            logger.error(f"❌ Not found in Predictive Features")

def check_target_distribution():
    """Check the distribution of the target variable."""
    logger.info("\nChecking Target Variable (RESILIENCE_SCORE)...")
    path = Path("data/predictive_model_training_data.csv")
    if not path.exists():
        logger.error("❌ Training data file missing")
        return
        
    df = pd.read_csv(path)
    target = df['RESILIENCE_SCORE']
    
    mean = target.mean()
    std = target.std()
    min_val = target.min()
    max_val = target.max()
    
    logger.info(f"Distribution Stats: Mean={mean:.3f}, Std={std:.3f}, Min={min_val:.3f}, Max={max_val:.3f}")
    
    if abs(mean) > 0.5:
        logger.warning("⚠️  Mean is drifting from 0.0")
    else:
        logger.info("✅ Mean is approximately centered")
        
    if std < 0.5 or std > 1.5:
        logger.warning("⚠️  Standard Deviation is unexpected (should be ~1.0)")
    else:
        logger.info("✅ Variance looks normal")

def main():
    logger.info("=== STARTING DATA INTEGRITY AUDIT ===")
    
    # 1. File Completeness
    logger.info("\n--- File Completeness Check ---")
    check_file_existence_and_size("regular_season_*.csv")
    check_file_existence_and_size("rs_game_logs_*.csv")
    check_file_existence_and_size("predictive_features_*.csv")
    
    # 2. Training Data Null Check
    logger.info("\n--- Training Data Null Check ---")
    train_path = Path("data/predictive_model_training_data.csv")
    if train_path.exists():
        df = pd.read_csv(train_path)
        crit_cols = [
            'PLAYER_ID', 'SEASON', 'RESILIENCE_SCORE', 'opp_def_context_score',
            'ts_pct_vs_top10', 'consistency_gmsc_std'
        ]
        check_nulls(df, "Training Data", crit_cols)
    
    # 3. Trace LeBron (2019-20 Champion)
    logger.info("\n--- The LeBron Test (2019-20) ---")
    trace_player("LeBron James", "2019-20")
    
    # 4. Target Distribution
    check_target_distribution()
    
    logger.info("\n=== AUDIT COMPLETE ===")

if __name__ == "__main__":
    main()
