import pandas as pd
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Assemble Predictive Model Training Data')
    parser.add_argument('--output', default='data/predictive_model_training_data.csv', help='Output path')
    args = parser.parse_args()
    
    # 1. Load Base Training Data (Context + Baselines)
    base_path = Path('data/training_dataset.csv')
    if not base_path.exists():
        logger.error("Missing data/training_dataset.csv")
        return
    
    base_df = pd.read_csv(base_path)
    logger.info(f"Loaded base data: {len(base_df)} rows")
    
    # 2. Load Targets (Resilience Scores)
    target_path = Path('results/resilience_scores_all.csv')
    if not target_path.exists():
        logger.error("Missing results/resilience_scores_all.csv")
        return
        
    target_df = pd.read_csv(target_path)
    logger.info(f"Loaded targets: {len(target_df)} rows")
    
    # Merge Targets into Base
    # Join keys: PLAYER_ID, SEASON, OPPONENT_ABBREV (Target file has OPPONENT, Base has OPPONENT_ABBREV)
    
    # Rename target opponent col to match base
    target_df = target_df.rename(columns={'OPPONENT': 'OPPONENT_ABBREV'})
    
    # Check if PLAYER_ID exists in target_df (I just added it)
    if 'PLAYER_ID' not in target_df.columns:
        logger.error("PLAYER_ID missing in resilience_scores_all.csv. Please regenerate scores.")
        return

    # We only need the score from target_df, other cols are in base
    target_subset = target_df[['PLAYER_ID', 'SEASON', 'OPPONENT_ABBREV', 'RESILIENCE_SCORE']]
    
    merged_df = pd.merge(
        base_df,
        target_subset,
        on=['PLAYER_ID', 'SEASON', 'OPPONENT_ABBREV'],
        how='inner'
    )
    logger.info(f"Merged targets: {len(merged_df)} rows")
    
    # 3. Load Predictive Features
    # These are split by season files: data/predictive_features_{season}.csv
    # We need to find all available feature files and concat them
    feature_files = list(Path('data').glob('predictive_features_*.csv'))
    
    if not feature_files:
        logger.error("No predictive feature files found in data/")
        return
        
    features_list = []
    for f in feature_files:
        df = pd.read_csv(f)
        # Extract season from filename if not in df (it is in df)
        features_list.append(df)
        
    features_df = pd.concat(features_list, ignore_index=True)
    logger.info(f"Loaded predictive features: {len(features_df)} rows from {len(feature_files)} files")
    
    # 4. Merge Predictive Features
    # Join keys: PLAYER_ID, SEASON
    
    final_df = pd.merge(
        merged_df,
        features_df,
        on=['PLAYER_ID', 'SEASON'],
        how='inner'
    )
    
    logger.info(f"Final dataset size: {len(final_df)} rows")
    
    # 5. Save
    final_df.to_csv(args.output, index=False)
    logger.info(f"✅ Saved training data to {args.output}")
    
    # Preview
    logger.info("Columns: " + ", ".join(final_df.columns))
    logger.info(f"Sample:\n{final_df.head(3)}")

if __name__ == "__main__":
    main()

