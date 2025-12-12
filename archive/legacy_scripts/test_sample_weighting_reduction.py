"""
Test if SHOT_QUALITY_GENERATION_DELTA allows reducing sample weighting from 5x to 3x or lower.

This script:
1. Retrains the model with SHOT_QUALITY_GENERATION_DELTA included in feature set
2. Tests different sample weighting levels (1x, 2x, 3x, 4x, 5x)
3. Compares false positive rates to see if lower weighting is sufficient
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
import ast

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/test_sample_weighting_reduction.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def load_data():
    """Load and merge all datasets (same as train_rfe_model.py)."""
    results_dir = Path("results")
    data_dir = Path("data")
    
    # Load features
    feature_path = results_dir / "predictive_dataset.csv"
    df_features = pd.read_csv(feature_path)
    logger.info(f"Loaded features: {len(df_features)} rows")
    
    # Check SHOT_QUALITY_GENERATION_DELTA
    if 'SHOT_QUALITY_GENERATION_DELTA' in df_features.columns:
        coverage = df_features['SHOT_QUALITY_GENERATION_DELTA'].notna().sum()
        logger.info(f"SHOT_QUALITY_GENERATION_DELTA: {coverage} / {len(df_features)} ({coverage/len(df_features)*100:.1f}%)")
    else:
        logger.warning("SHOT_QUALITY_GENERATION_DELTA not found!")
    
    # Load targets
    target_path = results_dir / "resilience_archetypes.csv"
    df_targets = pd.read_csv(target_path)
    df_targets.columns = [c.upper() for c in df_targets.columns]
    
    # Merge with additional feature files (same as train_rfe_model.py)
    pressure_path = results_dir / "pressure_features.csv"
    if pressure_path.exists():
        df_pressure = pd.read_csv(pressure_path)
        df_features = pd.merge(df_features, df_pressure, on=['PLAYER_ID', 'SEASON'], how='left', suffixes=('', '_pressure'))
        cols_to_drop = [c for c in df_features.columns if '_pressure' in c]
        df_features = df_features.drop(columns=cols_to_drop)
    
    physicality_path = results_dir / "physicality_features.csv"
    if physicality_path.exists():
        df_physicality = pd.read_csv(physicality_path)
        df_features = pd.merge(df_features, df_physicality, on=['PLAYER_NAME', 'SEASON'], how='left', suffixes=('', '_phys'))
        cols_to_drop = [c for c in df_features.columns if '_phys' in c]
        df_features = df_features.drop(columns=cols_to_drop)
    
    rim_path = results_dir / "rim_pressure_features.csv"
    if rim_path.exists():
        df_rim = pd.read_csv(rim_path)
        df_features = pd.merge(df_features, df_rim, on=['PLAYER_ID', 'SEASON'], how='left', suffixes=('', '_rim'))
        cols_to_drop = [c for c in df_features.columns if '_rim' in c]
        df_features = df_features.drop(columns=cols_to_drop)
    
    trajectory_path = results_dir / "trajectory_features.csv"
    if trajectory_path.exists():
        df_trajectory = pd.read_csv(trajectory_path)
        df_features = pd.merge(df_features, df_trajectory, on=['PLAYER_ID', 'SEASON'], how='left')
    
    gate_path = results_dir / "gate_features.csv"
    if gate_path.exists():
        df_gate = pd.read_csv(gate_path)
        df_features = pd.merge(df_features, df_gate, on=['PLAYER_ID', 'SEASON'], how='left')
    
    prev_po_path = results_dir / "previous_playoff_features.csv"
    if prev_po_path.exists():
        df_prev_po = pd.read_csv(prev_po_path)
        df_features = pd.merge(df_features, df_prev_po, on=['PLAYER_ID', 'SEASON'], how='left', suffixes=('', '_prev_po'))
        cols_to_drop = [c for c in df_features.columns if '_prev_po' in c]
        df_features = df_features.drop(columns=cols_to_drop)
    
    # Merge with targets
    df = pd.merge(
        df_features,
        df_targets[['PLAYER_NAME', 'SEASON', 'ARCHETYPE', 'RESILIENCE_QUOTIENT', 'DOMINANCE_SCORE']],
        on=['PLAYER_NAME', 'SEASON'],
        how='inner'
    )
    
    logger.info(f"Final merged dataset: {len(df)} rows")
    return df

def prepare_features_with_shot_quality(df):
    """Prepare features including SHOT_QUALITY_GENERATION_DELTA."""
    # Get current RFE top 10 features
    results_dir = Path("results")
    rfe_path = results_dir / "rfe_feature_count_comparison.csv"
    
    if rfe_path.exists():
        df_rfe = pd.read_csv(rfe_path)
        row = df_rfe[df_rfe['n_features'] == 10]
        if not row.empty:
            features_str = row.iloc[0]['features']
            rfe_features = ast.literal_eval(features_str)
            logger.info(f"Loaded {len(rfe_features)} RFE-selected features")
        else:
            rfe_features = None
    else:
        rfe_features = None
    
    # Start with RFE features if available
    if rfe_features:
        features = rfe_features.copy()
    else:
        # Fallback: use core features
        features = [
            'USG_PCT',
            'CREATION_TAX',
            'CREATION_VOLUME_RATIO',
            'EFG_ISO_WEIGHTED',
            'LEVERAGE_USG_DELTA',
            'LEVERAGE_TS_DELTA',
            'CLUTCH_MIN_TOTAL',
            'QOC_USG_DELTA',
            'ABDICATION_RISK',
            'USG_PCT_X_EFG_ISO_WEIGHTED',
            'USG_PCT_X_RS_LATE_CLOCK_PRESSURE_RESILIENCE',
        ]
    
    # Add SHOT_QUALITY_GENERATION_DELTA if not already included
    if 'SHOT_QUALITY_GENERATION_DELTA' not in features and 'SHOT_QUALITY_GENERATION_DELTA' in df.columns:
        features.append('SHOT_QUALITY_GENERATION_DELTA')
        logger.info("Added SHOT_QUALITY_GENERATION_DELTA to feature set")
    
    # Filter to features that exist
    available_features = [f for f in features if f in df.columns]
    missing = [f for f in features if f not in df.columns]
    
    if missing:
        logger.warning(f"Missing features: {missing}")
    
    logger.info(f"Using {len(available_features)} features")
    return available_features

def train_and_evaluate(df, sample_weight_multiplier=5.0):
    """Train model with specified sample weighting."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Training with {sample_weight_multiplier}x sample weighting")
    logger.info(f"{'='*80}")
    
    # Prepare features
    feature_names = prepare_features_with_shot_quality(df)
    
    # Prepare data
    X = df[feature_names].copy()
    y = df['ARCHETYPE'].copy()
    
    # Handle missing values
    for col in X.columns:
        if X[col].isna().sum() > 0:
            if 'CLOCK' in col or '_YOY_DELTA' in col or 'AGE_X_' in col:
                X[col] = X[col].fillna(0)
            elif col.startswith('PREV_'):
                if col == 'PREV_PO_ARCHETYPE':
                    X[col] = X[col].fillna(-1)
                else:
                    X[col] = X[col].fillna(X[col].median())
            elif col in ['DATA_COMPLETENESS_SCORE', 'SAMPLE_SIZE_CONFIDENCE', 'LEVERAGE_DATA_CONFIDENCE']:
                X[col] = X[col].fillna(0)
            elif col in ['ABDICATION_RISK', 'RIM_PRESSURE_DEFICIT', 'INEFFICIENT_VOLUME_SCORE']:
                X[col] = X[col].fillna(0)
            else:
                X[col] = X[col].fillna(X[col].median())
    
    # Temporal split
    train_mask = df['SEASON'].isin(['2015-16', '2016-17', '2017-18', '2018-19', '2019-20', '2020-21'])
    test_mask = df['SEASON'].isin(['2021-22', '2022-23', '2023-24', '2024-25'])
    
    X_train = X[train_mask]
    X_test = X[test_mask]
    y_train = y[train_mask]
    y_test = y[test_mask]
    
    logger.info(f"Train: {len(X_train)} samples")
    logger.info(f"Test: {len(X_test)} samples")
    
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
    
    penalty_multiplier = sample_weight_multiplier - 1.0
    sample_weights = 1.0 + (is_victim * is_high_usage * penalty_multiplier)
    
    logger.info(f"Sample weighting: {sample_weight_multiplier}x")
    logger.info(f"High-usage victims: {(is_victim * is_high_usage).sum()}")
    
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
    
    # Check SHOT_QUALITY_GENERATION_DELTA
    sq_rank = None
    sq_importance = None
    if 'SHOT_QUALITY_GENERATION_DELTA' in importance['Feature'].values:
        sq_rank = importance[importance['Feature'] == 'SHOT_QUALITY_GENERATION_DELTA'].index[0] + 1
        sq_importance = importance[importance['Feature'] == 'SHOT_QUALITY_GENERATION_DELTA']['Importance'].iloc[0]
        logger.info(f"✅ SHOT_QUALITY_GENERATION_DELTA: Rank #{sq_rank}, Importance: {sq_importance:.4f} ({sq_importance*100:.2f}%)")
    
    # Confusion matrix for false positives
    cm = confusion_matrix(y_test_encoded, y_pred, labels=le.transform(le.classes_))
    class_names = le.classes_
    
    victim_idx = list(class_names).index('Victim (Fragile Role)')
    king_idx = list(class_names).index('King (Resilient Star)')
    bulldozer_idx = list(class_names).index('Bulldozer (Fragile Star)')
    
    false_positives = cm[victim_idx, king_idx] + cm[victim_idx, bulldozer_idx]
    total_victims = cm[victim_idx, :].sum()
    fp_rate = false_positives / total_victims if total_victims > 0 else 0
    
    # True positives (predicting King/Bulldozer correctly)
    true_positives = cm[king_idx, king_idx] + cm[bulldozer_idx, bulldozer_idx]
    total_stars = cm[king_idx, :].sum() + cm[bulldozer_idx, :].sum()
    tp_rate = true_positives / total_stars if total_stars > 0 else 0
    
    logger.info(f"Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"False Positive Rate: {fp_rate:.2%} ({false_positives}/{total_victims})")
    logger.info(f"True Positive Rate: {tp_rate:.2%} ({true_positives}/{total_stars})")
    
    return {
        'accuracy': accuracy,
        'false_positive_rate': fp_rate,
        'true_positive_rate': tp_rate,
        'false_positives': false_positives,
        'total_victims': total_victims,
        'true_positives': true_positives,
        'total_stars': total_stars,
        'shot_quality_rank': sq_rank,
        'shot_quality_importance': sq_importance,
    }

def main():
    """Main execution."""
    logger.info("Testing Sample Weighting Reduction with SHOT_QUALITY_GENERATION_DELTA")
    logger.info("="*80)
    
    # Load data
    df = load_data()
    
    # Test different sample weighting levels
    results = {}
    for weight_mult in [1.0, 2.0, 3.0, 4.0, 5.0]:
        result = train_and_evaluate(df, sample_weight_multiplier=weight_mult)
        results[weight_mult] = result
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("SUMMARY: Sample Weighting Impact with SHOT_QUALITY_GENERATION_DELTA")
    logger.info("="*80)
    
    summary_data = []
    for weight, result in results.items():
        summary_data.append({
            'Weight': f'{weight}x',
            'Accuracy': f"{result['accuracy']:.2%}",
            'FP Rate': f"{result['false_positive_rate']:.2%}",
            'TP Rate': f"{result['true_positive_rate']:.2%}",
            'FP Count': f"{result['false_positives']}/{result['total_victims']}",
            'SQ Rank': result['shot_quality_rank'] if result['shot_quality_rank'] else 'N/A',
            'SQ Importance': f"{result['shot_quality_importance']*100:.2f}%" if result['shot_quality_importance'] else 'N/A',
        })
    
    summary_df = pd.DataFrame(summary_data)
    logger.info("\n" + summary_df.to_string(index=False))
    
    # Analysis
    logger.info("\n" + "="*80)
    logger.info("ANALYSIS")
    logger.info("="*80)
    
    baseline_5x = results[5.0]
    baseline_fp = baseline_5x['false_positive_rate']
    baseline_tp = baseline_5x['true_positive_rate']
    baseline_acc = baseline_5x['accuracy']
    
    logger.info(f"\nBaseline (5x):")
    logger.info(f"  Accuracy: {baseline_acc:.2%}")
    logger.info(f"  FP Rate: {baseline_fp:.2%}")
    logger.info(f"  TP Rate: {baseline_tp:.2%}")
    
    # Find optimal weighting (lowest FP rate while maintaining TP rate)
    for weight in [3.0, 2.0, 1.0]:
        result = results[weight]
        fp_diff = result['false_positive_rate'] - baseline_fp
        tp_diff = result['true_positive_rate'] - baseline_tp
        acc_diff = result['accuracy'] - baseline_acc
        
        logger.info(f"\n{weight}x vs 5x:")
        logger.info(f"  FP Rate: {result['false_positive_rate']:.2%} ({fp_diff:+.2%})")
        logger.info(f"  TP Rate: {result['true_positive_rate']:.2%} ({tp_diff:+.2%})")
        logger.info(f"  Accuracy: {result['accuracy']:.2%} ({acc_diff:+.2%})")
        
        # Check if acceptable
        if fp_diff <= 0.05 and tp_diff >= -0.05:  # FP within 5pp, TP within 5pp
            logger.info(f"  ✅ {weight}x is acceptable (within 5pp of 5x baseline)")
        else:
            logger.info(f"  ⚠️ {weight}x may not be sufficient")
    
    # Conclusion
    logger.info("\n" + "="*80)
    logger.info("CONCLUSION")
    logger.info("="*80)
    
    # Check if 3x is sufficient
    result_3x = results[3.0]
    if (result_3x['false_positive_rate'] <= baseline_fp + 0.05 and 
        result_3x['true_positive_rate'] >= baseline_tp - 0.05):
        logger.info("✅ 3x sample weighting is sufficient with SHOT_QUALITY_GENERATION_DELTA")
        logger.info("   → Can reduce from 5x to 3x without significant performance loss")
    else:
        logger.info("⚠️ 3x sample weighting may not be sufficient")
        logger.info("   → May need to keep 5x or further refine SHOT_QUALITY_GENERATION_DELTA")
    
    # Check if feature is being used
    if all(r['shot_quality_rank'] for r in results.values()):
        avg_rank = np.mean([r['shot_quality_rank'] for r in results.values()])
        avg_importance = np.mean([r['shot_quality_importance'] for r in results.values()])
        logger.info(f"\n✅ SHOT_QUALITY_GENERATION_DELTA is consistently selected")
        logger.info(f"   Average rank: {avg_rank:.1f}")
        logger.info(f"   Average importance: {avg_importance*100:.2f}%")
    else:
        logger.info("\n⚠️ SHOT_QUALITY_GENERATION_DELTA not consistently selected")
        logger.info("   → May need to force include or improve feature calculation")

if __name__ == "__main__":
    main()

