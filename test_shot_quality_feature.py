"""
Test Shot Quality Generation Delta Feature Impact on Sample Weighting

This script:
1. Retrains the model with SHOT_QUALITY_GENERATION_DELTA included
2. Tests different sample weighting levels (1x, 3x, 5x)
3. Compares results to see if the new feature reduces reliance on sample weighting
"""

import pandas as pd
import numpy as np
import logging
import sys
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from sklearn.feature_selection import RFE

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/test_shot_quality_feature.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def load_data():
    """Load predictive dataset and targets."""
    results_dir = Path("results")
    
    # Load features
    feature_path = results_dir / "predictive_dataset.csv"
    df_features = pd.read_csv(feature_path)
    logger.info(f"Loaded features: {len(df_features)} rows, {len(df_features.columns)} columns")
    
    # Check if SHOT_QUALITY_GENERATION_DELTA is present
    if 'SHOT_QUALITY_GENERATION_DELTA' in df_features.columns:
        coverage = df_features['SHOT_QUALITY_GENERATION_DELTA'].notna().sum()
        logger.info(f"SHOT_QUALITY_GENERATION_DELTA coverage: {coverage} / {len(df_features)} ({coverage/len(df_features)*100:.1f}%)")
    else:
        logger.warning("SHOT_QUALITY_GENERATION_DELTA not found in dataset!")
    
    # Load targets
    target_path = results_dir / "resilience_archetypes.csv"
    df_targets = pd.read_csv(target_path)
    df_targets.columns = [c.upper() for c in df_targets.columns]
    
    # Merge
    df = pd.merge(
        df_features,
        df_targets[['PLAYER_NAME', 'SEASON', 'ARCHETYPE']],
        on=['PLAYER_NAME', 'SEASON'],
        how='inner'
    )
    
    logger.info(f"Merged dataset: {len(df)} rows")
    return df

def prepare_features(df):
    """Prepare features for training (same logic as train_rfe_model.py)."""
    # Get RFE-selected features (top 10)
    results_dir = Path("results")
    rfe_path = results_dir / "rfe_feature_count_comparison.csv"
    
    if rfe_path.exists():
        df_rfe = pd.read_csv(rfe_path)
        row = df_rfe[df_rfe['n_features'] == 10]
        if not row.empty:
            import ast
            features_str = row.iloc[0]['features']
            rfe_features = ast.literal_eval(features_str)
            logger.info(f"Loaded {len(rfe_features)} RFE-selected features")
        else:
            rfe_features = None
    else:
        rfe_features = None
    
    # Core features (always include)
    core_features = [
        'USG_PCT',
        'CREATION_VOLUME_RATIO',
        'CREATION_TAX',
        'EFG_ISO_WEIGHTED',
        'LEVERAGE_USG_DELTA',
        'LEVERAGE_TS_DELTA',
        'RS_PRESSURE_APPETITE',
        'RS_PRESSURE_RESILIENCE',
        'RS_RIM_APPETITE',
        'CLUTCH_MIN_TOTAL',
    ]
    
    # Add SHOT_QUALITY_GENERATION_DELTA
    if 'SHOT_QUALITY_GENERATION_DELTA' in df.columns:
        core_features.append('SHOT_QUALITY_GENERATION_DELTA')
        logger.info("Added SHOT_QUALITY_GENERATION_DELTA to feature set")
    
    # Usage interaction terms
    interaction_features = [
        'USG_PCT_X_EFG_ISO_WEIGHTED',
        'USG_PCT_X_CREATION_VOLUME_RATIO',
        'USG_PCT_X_RS_PRESSURE_APPETITE',
        'USG_PCT_X_LEVERAGE_USG_DELTA',
        'USG_PCT_X_RS_LATE_CLOCK_PRESSURE_RESILIENCE',
    ]
    
    # Gate features
    gate_features = [
        'ABDICATION_RISK',
        'RIM_PRESSURE_DEFICIT',
        'INEFFICIENT_VOLUME_SCORE',
    ]
    
    # Trajectory features
    trajectory_features = [
        'CREATION_TAX_YOY_DELTA',
        'AGE_X_RS_PRESSURE_RESILIENCE_YOY_DELTA',
    ]
    
    # Combine all features
    all_features = core_features + interaction_features + gate_features + trajectory_features
    
    # Filter to features that exist in dataframe
    available_features = [f for f in all_features if f in df.columns]
    missing_features = [f for f in all_features if f not in df.columns]
    
    if missing_features:
        logger.warning(f"Missing features: {missing_features}")
    
    logger.info(f"Using {len(available_features)} features for training")
    
    return available_features

def train_and_evaluate(df, sample_weight_multiplier=5.0, n_features=10):
    """Train model with specified sample weighting and evaluate."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Training with {sample_weight_multiplier}x sample weighting")
    logger.info(f"{'='*80}")
    
    # Prepare features
    feature_names = prepare_features(df)
    
    # Prepare data
    X = df[feature_names].copy()
    y = df['ARCHETYPE'].copy()
    
    # Handle missing values
    X = X.fillna(X.median())
    
    # Temporal split (2015-2020 train, 2021-2024 test)
    train_mask = df['SEASON'].isin(['2015-16', '2016-17', '2017-18', '2018-19', '2019-20', '2020-21'])
    test_mask = df['SEASON'].isin(['2021-22', '2022-23', '2023-24', '2024-25'])
    
    X_train = X[train_mask]
    X_test = X[test_mask]
    y_train = y[train_mask]
    y_test = y[test_mask]
    
    logger.info(f"Train: {len(X_train)} samples ({sorted(df[train_mask]['SEASON'].unique())})")
    logger.info(f"Test: {len(X_test)} samples ({sorted(df[test_mask]['SEASON'].unique())})")
    
    # Encode labels
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    y_test_encoded = le.transform(y_test)
    
    # Calculate sample weights
    is_victim = (y_train == 'Victim (Fragile Role)').astype(int)
    usg_pct = df.loc[train_mask, 'USG_PCT'].fillna(0.0)
    if usg_pct.max() > 1.0:
        usg_pct = usg_pct / 100.0
    is_high_usage = (usg_pct > 0.25).astype(int)
    
    penalty_multiplier = sample_weight_multiplier - 1.0  # e.g., 5x = 1.0 + 4.0
    sample_weights = 1.0 + (is_victim * is_high_usage * penalty_multiplier)
    
    logger.info(f"Sample weighting: {sample_weight_multiplier}x (penalty_multiplier={penalty_multiplier})")
    logger.info(f"High-usage victims receiving penalty: {(is_victim * is_high_usage).sum()}")
    logger.info(f"Weighted samples: {(sample_weights > 1.0).sum()}")
    
    # Run RFE if needed
    if len(feature_names) > n_features:
        logger.info(f"Running RFE to select top {n_features} features...")
        base_estimator = xgb.XGBClassifier(
            objective='multi:softprob',
            n_estimators=50,
            max_depth=3,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric='mlogloss',
            random_state=42
        )
        
        rfe = RFE(estimator=base_estimator, n_features_to_select=n_features, step=1)
        rfe.fit(X_train, y_train_encoded, sample_weight=sample_weights.values)
        
        selected_features = [feature_names[i] for i in range(len(feature_names)) if rfe.support_[i]]
        logger.info(f"RFE selected {len(selected_features)} features:")
        for i, feat in enumerate(selected_features, 1):
            logger.info(f"  {i}. {feat}")
        
        X_train = X_train[selected_features]
        X_test = X_test[selected_features]
        feature_names = selected_features
    else:
        logger.info(f"Using all {len(feature_names)} features (no RFE needed)")
    
    # Train model
    model = xgb.XGBClassifier(
        objective='multi:softprob',
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric='mlogloss',
        random_state=42
    )
    
    model.fit(X_train, y_train_encoded, sample_weight=sample_weights.values)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test_encoded, y_pred)
    
    # Feature importance
    importance = pd.DataFrame({
        'Feature': feature_names,
        'Importance': model.feature_importances_
    }).sort_values(by='Importance', ascending=False)
    
    logger.info(f"\nModel Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info("\nTop 10 Features by Importance:")
    for i, row in importance.head(10).iterrows():
        logger.info(f"  {row['Feature']}: {row['Importance']:.4f} ({row['Importance']*100:.2f}%)")
    
    # Check if SHOT_QUALITY_GENERATION_DELTA is in top features
    if 'SHOT_QUALITY_GENERATION_DELTA' in importance['Feature'].values:
        sq_rank = importance[importance['Feature'] == 'SHOT_QUALITY_GENERATION_DELTA'].index[0] + 1
        sq_importance = importance[importance['Feature'] == 'SHOT_QUALITY_GENERATION_DELTA']['Importance'].iloc[0]
        logger.info(f"\n✅ SHOT_QUALITY_GENERATION_DELTA: Rank #{sq_rank}, Importance: {sq_importance:.4f} ({sq_importance*100:.2f}%)")
    else:
        logger.info("\n⚠️ SHOT_QUALITY_GENERATION_DELTA not in top features")
    
    # Confusion matrix for false positives
    cm = confusion_matrix(y_test_encoded, y_pred, labels=le.transform(le.classes_))
    class_names = le.classes_
    
    # Count false positives (predicting Victim as King/Bulldozer)
    victim_idx = list(class_names).index('Victim (Fragile Role)')
    king_idx = list(class_names).index('King (Resilient Star)')
    bulldozer_idx = list(class_names).index('Bulldozer (Fragile Star)')
    
    false_positives = cm[victim_idx, king_idx] + cm[victim_idx, bulldozer_idx]
    total_victims = cm[victim_idx, :].sum()
    fp_rate = false_positives / total_victims if total_victims > 0 else 0
    
    logger.info(f"\nFalse Positive Rate: {false_positives} / {total_victims} = {fp_rate:.2%}")
    
    return {
        'accuracy': accuracy,
        'false_positive_rate': fp_rate,
        'false_positives': false_positives,
        'total_victims': total_victims,
        'feature_importance': importance,
        'shot_quality_rank': sq_rank if 'SHOT_QUALITY_GENERATION_DELTA' in importance['Feature'].values else None,
        'shot_quality_importance': sq_importance if 'SHOT_QUALITY_GENERATION_DELTA' in importance['Feature'].values else None,
    }

def main():
    """Main execution."""
    logger.info("Testing Shot Quality Generation Delta Feature Impact")
    logger.info("="*80)
    
    # Load data
    df = load_data()
    
    # Test different sample weighting levels
    results = {}
    
    for weight_mult in [1.0, 3.0, 5.0]:
        result = train_and_evaluate(df, sample_weight_multiplier=weight_mult, n_features=10)
        results[weight_mult] = result
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("SUMMARY: Sample Weighting Impact with SHOT_QUALITY_GENERATION_DELTA")
    logger.info("="*80)
    
    summary_df = pd.DataFrame({
        'Sample Weight': [f'{w}x' for w in results.keys()],
        'Accuracy': [r['accuracy'] for r in results.values()],
        'False Positive Rate': [r['false_positive_rate'] for r in results.values()],
        'False Positives': [r['false_positives'] for r in results.values()],
        'SQ Delta Rank': [r['shot_quality_rank'] if r['shot_quality_rank'] else 'N/A' for r in results.values()],
        'SQ Delta Importance': [f"{r['shot_quality_importance']*100:.2f}%" if r['shot_quality_importance'] else 'N/A' for r in results.values()],
    })
    
    logger.info("\n" + summary_df.to_string(index=False))
    
    # Analysis
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS")
    logger.info("="*80)
    
    acc_1x = results[1.0]['accuracy']
    acc_3x = results[3.0]['accuracy']
    acc_5x = results[5.0]['accuracy']
    
    fp_1x = results[1.0]['false_positive_rate']
    fp_3x = results[3.0]['false_positive_rate']
    fp_5x = results[5.0]['false_positive_rate']
    
    logger.info(f"\nAccuracy:")
    logger.info(f"  1x: {acc_1x:.4f} ({acc_1x*100:.2f}%)")
    logger.info(f"  3x: {acc_3x:.4f} ({acc_3x*100:.2f}%) - Change: {acc_3x-acc_1x:+.4f} ({+(acc_3x-acc_1x)*100:+.2f} pp)")
    logger.info(f"  5x: {acc_5x:.4f} ({acc_5x*100:.2f}%) - Change: {acc_5x-acc_1x:+.4f} ({+(acc_5x-acc_1x)*100:+.2f} pp)")
    
    logger.info(f"\nFalse Positive Rate:")
    logger.info(f"  1x: {fp_1x:.2%}")
    logger.info(f"  3x: {fp_3x:.2%} - Change: {fp_3x-fp_1x:+.2%}")
    logger.info(f"  5x: {fp_5x:.2%} - Change: {fp_5x-fp_1x:+.2%}")
    
    # Check if feature is selected
    if all(r['shot_quality_rank'] for r in results.values()):
        logger.info(f"\n✅ SHOT_QUALITY_GENERATION_DELTA is selected by RFE in all configurations")
        logger.info(f"   Average rank: {np.mean([r['shot_quality_rank'] for r in results.values()]):.1f}")
        logger.info(f"   Average importance: {np.mean([r['shot_quality_importance'] for r in results.values()])*100:.2f}%")
    else:
        logger.info(f"\n⚠️ SHOT_QUALITY_GENERATION_DELTA not consistently selected")
    
    # Conclusion
    logger.info("\n" + "="*80)
    logger.info("CONCLUSION")
    logger.info("="*80)
    
    if fp_3x < fp_1x * 1.1:  # 3x reduces FP rate by at least 10% vs 1x
        logger.info("✅ 3x sample weighting significantly reduces false positives")
        if fp_5x < fp_3x * 1.1:  # 5x doesn't help much more than 3x
            logger.info("⚠️ 5x sample weighting provides minimal additional benefit over 3x")
            logger.info("   → Consider reducing to 3x if SHOT_QUALITY_GENERATION_DELTA is selected")
        else:
            logger.info("✅ 5x sample weighting provides additional benefit")
    else:
        logger.info("⚠️ Sample weighting has limited impact on false positives")
        logger.info("   → May need additional features or different approach")

if __name__ == "__main__":
    main()

