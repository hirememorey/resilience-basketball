"""
Diagnostic script to trace failing test cases and identify root causes.

This script runs the test suite with detailed logging to identify:
1. Which gates are triggering
2. What features are driving predictions
3. Why risk categories are mismatched
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/diagnose_failures.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Failing cases to investigate
FAILING_CASES = [
    ("Desmond Bane", "2021-22", "True Positive - Under-predicted"),
    ("Tyrese Haliburton", "2021-22", "True Positive - Gate capping"),
    ("Domantas Sabonis", "2021-22", "True Negative - Risk category mismatch"),
    ("Karl-Anthony Towns", "2018-19", "True Negative - Over-predicted"),
    ("Karl-Anthony Towns", "2020-21", "True Negative - Over-predicted"),
    ("Markelle Fultz", "2019-20", "True Negative - Over-predicted"),
    ("Markelle Fultz", "2022-23", "True Negative - Over-predicted"),
    ("Julius Randle", "2020-21", "False Positive - Over-predicted"),
]

def diagnose_case(predictor, player_name, season, test_usage=0.28):
    """Diagnose a single failing case with detailed logging."""
    
    logger.info("=" * 100)
    logger.info(f"DIAGNOSING: {player_name} ({season})")
    logger.info("=" * 100)
    
    # Get player data
    player_data = predictor.get_player_data(player_name, season)
    if player_data is None:
        logger.error(f"  ❌ NO DATA FOUND")
        return None
    
    logger.info(f"\n  Actual Usage: {player_data.get('USG_PCT', 'N/A')*100:.1f}%")
    logger.info(f"  Test Usage: {test_usage*100:.1f}%")
    
    # Check critical features
    logger.info(f"\n  Critical Features:")
    critical_features = [
        'CREATION_VOLUME_RATIO', 'CREATION_TAX', 'EFG_ISO_WEIGHTED',
        'LEVERAGE_USG_DELTA', 'LEVERAGE_TS_DELTA', 'CLUTCH_MIN_TOTAL',
        'RS_PRESSURE_APPETITE', 'RS_PRESSURE_RESILIENCE', 'RS_RIM_APPETITE',
        'ISO_FREQUENCY', 'PNR_HANDLER_FREQUENCY', 'USG_PCT', 'AGE'
    ]
    
    for feat in critical_features:
        val = player_data.get(feat, None)
        if pd.notna(val):
            logger.info(f"    {feat}: {val:.4f}")
        else:
            logger.info(f"    {feat}: MISSING")
    
    # Check gate conditions
    logger.info(f"\n  Gate Conditions:")
    
    # 1. Fragility Gate
    rim_appetite = player_data.get('RS_RIM_APPETITE', None)
    if pd.notna(rim_appetite):
        rim_threshold = predictor.rim_appetite_bottom_20th
        if rim_threshold is not None:
            below_threshold = rim_appetite <= rim_threshold
            logger.info(f"    Fragility Gate: RS_RIM_APPETITE={rim_appetite:.4f} {'<=' if below_threshold else '>'} {rim_threshold:.4f} → {'WOULD TRIGGER' if below_threshold else 'OK'}")
        else:
            logger.info(f"    Fragility Gate: RS_RIM_APPETITE={rim_appetite:.4f} (threshold not calculated)")
    else:
        logger.info(f"    Fragility Gate: RS_RIM_APPETITE MISSING")
    
    # 2. Bag Check Gate
    iso_freq = player_data.get('ISO_FREQUENCY', None)
    pnr_freq = player_data.get('PNR_HANDLER_FREQUENCY', None)
    if pd.notna(iso_freq) and pd.notna(pnr_freq):
        self_created_freq = iso_freq + pnr_freq
        logger.info(f"    Bag Check Gate: Self-created freq={self_created_freq:.4f} {'<' if self_created_freq < 0.10 else '>='} 0.10 → {'WOULD TRIGGER' if self_created_freq < 0.10 else 'OK'}")
    else:
        logger.info(f"    Bag Check Gate: ISO/PNR data missing, using proxy")
        creation_vol = player_data.get('CREATION_VOLUME_RATIO', 0)
        if pd.notna(creation_vol):
            estimated = creation_vol * 0.35 if creation_vol > 0.15 else creation_vol * 0.6
            logger.info(f"    Bag Check Gate: Proxy estimate={estimated:.4f} (from CREATION_VOLUME_RATIO={creation_vol:.4f})")
    
    # 3. Leverage Data Penalty
    leverage_usg = player_data.get('LEVERAGE_USG_DELTA', None)
    leverage_ts = player_data.get('LEVERAGE_TS_DELTA', None)
    clutch_min = player_data.get('CLUTCH_MIN_TOTAL', 0)
    missing_leverage = pd.isna(leverage_usg) or pd.isna(leverage_ts)
    insufficient_clutch = pd.isna(clutch_min) or clutch_min < 15
    if missing_leverage or insufficient_clutch:
        logger.info(f"    Leverage Data Penalty: {'WOULD TRIGGER'}")
        if missing_leverage:
            logger.info(f"      - Missing leverage data: USG_DELTA={leverage_usg}, TS_DELTA={leverage_ts}")
        if insufficient_clutch:
            logger.info(f"      - Insufficient clutch minutes: {clutch_min if pd.notna(clutch_min) else 'NaN'} < 15")
    else:
        logger.info(f"    Leverage Data Penalty: OK (USG_DELTA={leverage_usg:.4f}, TS_DELTA={leverage_ts:.4f}, Clutch={clutch_min:.1f})")
    
    # 4. Negative Signal Gate (Abdication Tax)
    if pd.notna(leverage_usg) and leverage_usg < -0.05:
        rs_usg = player_data.get('USG_PCT', None)
        has_immunity = pd.notna(rs_usg) and rs_usg > 0.30 and leverage_usg > -0.10
        if has_immunity:
            logger.info(f"    Abdication Tax: EXEMPTED (High-Usage Immunity: RS_USG={rs_usg:.1%} > 30%, Delta={leverage_usg:.4f} > -0.10)")
        else:
            efficiency_spikes = pd.notna(leverage_ts) and leverage_ts > 0.05
            if efficiency_spikes:
                logger.info(f"    Abdication Tax: EXEMPTED (Smart Deference: TS_DELTA={leverage_ts:.4f} > 0.05)")
            else:
                logger.info(f"    Abdication Tax: WOULD TRIGGER (Panic Abdication: USG_DELTA={leverage_usg:.4f} < -0.05, TS_DELTA={leverage_ts:.4f if pd.notna(leverage_ts) else 'NaN'})")
    else:
        usg_str = f"{leverage_usg:.4f}" if pd.notna(leverage_usg) else "NaN"
        logger.info(f"    Abdication Tax: OK (USG_DELTA={usg_str})")
    
    # 5. Data Completeness Gate
    critical_features_gate = [
        'CREATION_VOLUME_RATIO', 'CREATION_TAX', 'LEVERAGE_USG_DELTA',
        'LEVERAGE_TS_DELTA', 'RS_PRESSURE_APPETITE', 'RS_PRESSURE_RESILIENCE'
    ]
    present = sum(1 for f in critical_features_gate if pd.notna(player_data.get(f, None)))
    completeness = present / len(critical_features_gate)
    if completeness < 0.67:
        logger.info(f"    Data Completeness Gate: WOULD TRIGGER ({present}/{len(critical_features_gate)} features = {completeness:.1%} < 67%)")
    else:
        logger.info(f"    Data Completeness Gate: OK ({present}/{len(critical_features_gate)} features = {completeness:.1%})")
    
    # 6. Sample Size Gate
    pressure_shots = player_data.get('RS_TOTAL_VOLUME', 0)
    insufficient_pressure = pd.isna(pressure_shots) or pressure_shots < 50
    insufficient_clutch = pd.isna(clutch_min) or clutch_min < 15
    creation_tax = player_data.get('CREATION_TAX', None)
    usage = player_data.get('USG_PCT', None)
    suspicious_creation = pd.notna(creation_tax) and pd.notna(usage) and creation_tax >= 0.8 and usage < 0.20
    
    if insufficient_pressure or insufficient_clutch or suspicious_creation:
        logger.info(f"    Sample Size Gate: WOULD TRIGGER")
        if insufficient_pressure:
            logger.info(f"      - Insufficient pressure shots: {pressure_shots if pd.notna(pressure_shots) else 'NaN'} < 50")
        if insufficient_clutch:
            logger.info(f"      - Insufficient clutch minutes: {clutch_min if pd.notna(clutch_min) else 'NaN'} < 15")
        if suspicious_creation:
            logger.info(f"      - Suspicious creation: CREATION_TAX={creation_tax:.3f} >= 0.8 with usage={usage:.1%} < 20%")
    else:
        logger.info(f"    Sample Size Gate: OK")
    
    # 7. Inefficiency Gate
    efg_iso = player_data.get('EFG_ISO_WEIGHTED', None)
    if pd.notna(efg_iso):
        efg_floor = predictor.efg_iso_floor
        efg_median = predictor.efg_iso_median
        if efg_floor is not None:
            below_floor = efg_iso < efg_floor
            uniformly_mediocre = False
            if pd.notna(creation_tax) and efg_median is not None:
                near_zero_tax = abs(creation_tax) <= 0.05
                below_median = efg_iso < efg_median
                uniformly_mediocre = near_zero_tax and below_median
            if below_floor or uniformly_mediocre:
                logger.info(f"    Inefficiency Gate: WOULD TRIGGER (EFG_ISO={efg_iso:.4f}, {'below floor' if below_floor else 'uniformly mediocre'})")
            else:
                logger.info(f"    Inefficiency Gate: OK (EFG_ISO={efg_iso:.4f})")
    
    # Run prediction with gates enabled
    logger.info(f"\n  Prediction (Gates Enabled):")
    result_gates = predictor.predict_with_risk_matrix(
        player_data,
        test_usage,
        apply_phase3_fixes=True,
        apply_hard_gates=True
    )
    
    logger.info(f"    Performance Score: {result_gates['performance_score']:.2%}")
    logger.info(f"    Dependence Score: {result_gates.get('dependence_score', 'N/A')}")
    logger.info(f"    Risk Category: {result_gates['risk_category']}")
    logger.info(f"    Archetype: {result_gates['archetype']}")
    
    # Check phase3 flags
    if 'phase3_flags' in result_gates.get('metadata', {}):
        flags = result_gates['metadata']['phase3_flags']
        if flags:
            logger.info(f"    Phase 3 Flags: {', '.join(flags)}")
    
    # Run prediction without gates (Trust Fall)
    logger.info(f"\n  Prediction (Gates Disabled - Trust Fall):")
    result_no_gates = predictor.predict_with_risk_matrix(
        player_data,
        test_usage,
        apply_phase3_fixes=True,
        apply_hard_gates=False
    )
    
    logger.info(f"    Performance Score: {result_no_gates['performance_score']:.2%}")
    logger.info(f"    Dependence Score: {result_no_gates.get('dependence_score', 'N/A')}")
    logger.info(f"    Risk Category: {result_no_gates['risk_category']}")
    logger.info(f"    Archetype: {result_no_gates['archetype']}")
    
    # Compare
    logger.info(f"\n  Comparison:")
    logger.info(f"    Gates Enabled:  {result_gates['performance_score']:.2%} → {result_gates['risk_category']}")
    logger.info(f"    Gates Disabled: {result_no_gates['performance_score']:.2%} → {result_no_gates['risk_category']}")
    logger.info(f"    Difference: {result_no_gates['performance_score'] - result_gates['performance_score']:.2%}")
    
    return {
        'player_name': player_name,
        'season': season,
        'gates_enabled': result_gates,
        'gates_disabled': result_no_gates,
        'player_data': player_data
    }

def main():
    """Run diagnostics on all failing cases."""
    
    logger.info("=" * 100)
    logger.info("TEST FAILURE DIAGNOSTICS")
    logger.info("=" * 100)
    
    predictor = ConditionalArchetypePredictor()
    
    results = []
    for player_name, season, description in FAILING_CASES:
        try:
            result = diagnose_case(predictor, player_name, season)
            if result:
                results.append(result)
        except Exception as e:
            logger.error(f"Error diagnosing {player_name} ({season}): {e}", exc_info=True)
    
    # Summary
    logger.info("\n" + "=" * 100)
    logger.info("SUMMARY")
    logger.info("=" * 100)
    
    for result in results:
        gates = result['gates_enabled']
        no_gates = result['gates_disabled']
        diff = no_gates['performance_score'] - gates['performance_score']
        
        logger.info(f"\n{result['player_name']} ({result['season']}):")
        logger.info(f"  Gates: {gates['performance_score']:.2%} → {gates['risk_category']}")
        logger.info(f"  No Gates: {no_gates['performance_score']:.2%} → {no_gates['risk_category']}")
        logger.info(f"  Gate Impact: {diff:+.2%}")

if __name__ == "__main__":
    main()

