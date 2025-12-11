"""
Validate the EMPTY_CALORIES_SCORE plan against test cases.

Key Questions:
1. Does EMPTY_CALORIES_SCORE distinguish FPs from TPs?
2. Does the safety valve gate (USG_PCT > 0.25 AND SQ_DELTA < -0.05) break any TPs?
3. Is this feature different from existing INEFFICIENT_VOLUME_SCORE?
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor
from test_latent_star_cases import get_test_cases

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_empty_calories_score(usg_pct, sq_delta):
    """Calculate EMPTY_CALORIES_SCORE = USG_PCT * max(0, -SHOT_QUALITY_GENERATION_DELTA)"""
    if pd.isna(usg_pct) or pd.isna(sq_delta):
        return np.nan
    return usg_pct * max(0, -sq_delta)


def validate_plan():
    """Validate the EMPTY_CALORIES_SCORE plan."""
    
    logger.info("=" * 100)
    logger.info("VALIDATING EMPTY_CALORIES_SCORE PLAN")
    logger.info("=" * 100)
    
    predictor = ConditionalArchetypePredictor()
    test_cases = get_test_cases()
    
    results = []
    
    for test_case in test_cases:
        player_data = predictor.get_player_data(test_case.name, test_case.season)
        
        if player_data is None:
            continue
        
        usg_pct = player_data.get('USG_PCT', np.nan)
        sq_delta = player_data.get('SHOT_QUALITY_GENERATION_DELTA', np.nan)
        
        # Normalize USG_PCT if needed
        if pd.notna(usg_pct) and usg_pct > 1.0:
            usg_pct = usg_pct / 100.0
        
        # Calculate EMPTY_CALORIES_SCORE
        empty_calories_score = calculate_empty_calories_score(usg_pct, sq_delta)
        
        # Check if safety valve gate would trigger
        safety_valve_triggered = False
        if pd.notna(usg_pct) and pd.notna(sq_delta):
            safety_valve_triggered = (usg_pct > 0.25) and (sq_delta < -0.05)
        
        # Categorize
        category = 'Unknown'
        if 'True Positive' in test_case.category:
            category = 'True Positive'
        elif 'False Positive' in test_case.category:
            category = 'False Positive'
        elif 'True Negative' in test_case.category:
            category = 'True Negative'
        
        results.append({
            'player_name': test_case.name,
            'season': test_case.season,
            'category': category,
            'usg_pct': usg_pct,
            'sq_delta': sq_delta,
            'empty_calories_score': empty_calories_score,
            'safety_valve_triggered': safety_valve_triggered
        })
    
    df = pd.DataFrame(results)
    
    # Statistical comparison
    logger.info("\n" + "=" * 100)
    logger.info("STATISTICAL COMPARISON")
    logger.info("=" * 100)
    
    for cat in ['True Positive', 'False Positive', 'True Negative']:
        df_cat = df[df['category'] == cat]
        df_valid = df_cat[df_cat['empty_calories_score'].notna()]
        
        if len(df_valid) > 0:
            logger.info(f"\n{cat} ({len(df_valid)} cases):")
            logger.info(f"  Mean EMPTY_CALORIES_SCORE: {df_valid['empty_calories_score'].mean():.6f}")
            logger.info(f"  Median: {df_valid['empty_calories_score'].median():.6f}")
            logger.info(f"  Range: [{df_valid['empty_calories_score'].min():.6f}, {df_valid['empty_calories_score'].max():.6f}]")
    
    # Safety valve gate validation
    logger.info("\n" + "=" * 100)
    logger.info("SAFETY VALVE GATE VALIDATION")
    logger.info("=" * 100)
    
    logger.info("\nTrue Positives that would trigger gate:")
    tp_triggered = df[(df['category'] == 'True Positive') & (df['safety_valve_triggered'] == True)]
    if len(tp_triggered) > 0:
        for _, row in tp_triggered.iterrows():
            logger.warning(f"  ❌ {row['player_name']} ({row['season']}): USG={row['usg_pct']:.3f}, SQ_DELTA={row['sq_delta']:.4f}")
    else:
        logger.info("  ✅ None - Gate would NOT break any true positives")
    
    logger.info("\nFalse Positives that would trigger gate:")
    fp_triggered = df[(df['category'] == 'False Positive') & (df['safety_valve_triggered'] == True)]
    if len(fp_triggered) > 0:
        for _, row in fp_triggered.iterrows():
            logger.info(f"  ✅ {row['player_name']} ({row['season']}): USG={row['usg_pct']:.3f}, SQ_DELTA={row['sq_delta']:.4f}")
    else:
        logger.warning("  ⚠️ None - Gate would NOT catch any false positives")
    
    # Check if feature distinguishes categories
    logger.info("\n" + "=" * 100)
    logger.info("FEATURE DISCRIMINATION CHECK")
    logger.info("=" * 100)
    
    df_fp = df[df['category'] == 'False Positive']
    df_tp = df[df['category'] == 'True Positive']
    
    fp_mean = df_fp['empty_calories_score'].mean()
    tp_mean = df_tp['empty_calories_score'].mean()
    
    if fp_mean > tp_mean:
        logger.info(f"✅ Feature distinguishes categories: FP mean ({fp_mean:.6f}) > TP mean ({tp_mean:.6f})")
    else:
        logger.warning(f"⚠️ Feature does NOT distinguish: FP mean ({fp_mean:.6f}) <= TP mean ({tp_mean:.6f})")
    
    # Save results
    output_path = Path("results/empty_calories_plan_validation.csv")
    df.to_csv(output_path, index=False)
    logger.info(f"\n✅ Results saved to: {output_path}")
    
    return df


if __name__ == "__main__":
    validate_plan()







