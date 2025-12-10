"""
Audit False Positive Cases

This script performs a deep dive analysis of false positive test cases to understand:
1. Which gates are applying (or not applying)
2. Which exemptions are being used
3. What feature values are driving predictions
4. Why the model is predicting high performance
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
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# False Positive cases from test results
FALSE_POSITIVE_CASES = [
    ("Jordan Poole", "2021-22", 0.30, "Expected <55%, got 98.79%"),
    ("Christian Wood", "2020-21", 0.26, "Expected <55%, got 72.81%"),
    ("D'Angelo Russell", "2018-19", 0.31, "Expected <55%, got 96.57%"),
    ("Julius Randle", "2020-21", 0.30, "Expected <55%, got 88.05%"),
]

def audit_case(predictor, player_name, season, test_usage):
    """Perform comprehensive audit of a single false positive case."""
    
    logger.info("=" * 100)
    logger.info(f"AUDITING: {player_name} ({season})")
    logger.info("=" * 100)
    
    # Get player data
    player_data = predictor.get_player_data(player_name, season)
    if player_data is None:
        logger.error("  ❌ NO DATA FOUND")
        return None
    
    logger.info(f"\n  Actual Usage: {player_data.get('USG_PCT', 'N/A')*100:.1f}%")
    logger.info(f"  Test Usage: {test_usage*100:.1f}%")
    logger.info(f"  Age: {player_data.get('AGE', 'N/A')}")
    
    # ========================================================================
    # SECTION 1: CRITICAL FEATURES ANALYSIS
    # ========================================================================
    logger.info("\n" + "=" * 100)
    logger.info("SECTION 1: CRITICAL FEATURES")
    logger.info("=" * 100)
    
    critical_features = {
        'Usage & Volume': [
            'USG_PCT', 'CREATION_VOLUME_RATIO', 'CREATION_TAX',
            'SHOT_QUALITY_GENERATION_DELTA', 'INEFFICIENT_VOLUME_SCORE'
        ],
        'Leverage (Clutch)': [
            'LEVERAGE_USG_DELTA', 'LEVERAGE_TS_DELTA', 'CLUTCH_MIN_TOTAL'
        ],
        'Physicality (Rim Pressure)': [
            'RS_RIM_APPETITE', 'RS_RIM_PCT'
        ],
        'Creation (ISO/PNR)': [
            'ISO_FREQUENCY', 'PNR_HANDLER_FREQUENCY', 'SELF_CREATED_FREQ',
            'EFG_ISO_WEIGHTED'
        ],
        'Playmaking': [
            'AST_PCT', 'CREATION_VOLUME_RATIO'
        ],
        'Pressure Resilience': [
            'RS_PRESSURE_APPETITE', 'RS_PRESSURE_RESILIENCE',
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE'
        ],
        'Dependence': [
            'DEPENDENCE_SCORE'
        ]
    }
    
    feature_values = {}
    for category, features in critical_features.items():
        logger.info(f"\n  {category}:")
        for feat in features:
            val = player_data.get(feat, None)
            if pd.notna(val):
                feature_values[feat] = val
                logger.info(f"    {feat}: {val:.4f}")
            else:
                feature_values[feat] = None
                logger.info(f"    {feat}: MISSING")
    
    # ========================================================================
    # SECTION 2: GATE ANALYSIS
    # ========================================================================
    logger.info("\n" + "=" * 100)
    logger.info("SECTION 2: GATE ANALYSIS")
    logger.info("=" * 100)
    
    # Run prediction with gates enabled to see which gates apply
    prediction_with_gates = predictor.predict_archetype_at_usage(
        player_data,
        test_usage,
        apply_phase3_fixes=True,
        apply_hard_gates=True
    )
    
    confidence_flags = prediction_with_gates.get('confidence_flags', [])
    star_level_with_gates = prediction_with_gates.get('star_level_potential', 0)
    
    logger.info(f"\n  Star Level (With Gates): {star_level_with_gates:.2%}")
    logger.info(f"  Predicted Archetype: {prediction_with_gates.get('predicted_archetype', 'N/A')}")
    logger.info(f"  Confidence Flags: {confidence_flags if confidence_flags else 'None'}")
    
    # Check each gate condition manually
    logger.info("\n  Gate Conditions Check:")
    
    # Tier 1: Fatal Flaw Gates
    logger.info("\n  TIER 1: FATAL FLAW GATES")
    
    # 1. Clutch Fragility Gate
    leverage_ts_delta = player_data.get('LEVERAGE_TS_DELTA', None)
    if pd.notna(leverage_ts_delta):
        would_trigger = leverage_ts_delta < -0.10
        logger.info(f"    Clutch Fragility: LEVERAGE_TS_DELTA={leverage_ts_delta:.4f} {'< -0.10' if would_trigger else '>= -0.10'} → {'WOULD TRIGGER' if would_trigger else 'OK'}")
    else:
        logger.info(f"    Clutch Fragility: LEVERAGE_TS_DELTA MISSING")
    
    # 2. Abdication Gate
    leverage_usg_delta = player_data.get('LEVERAGE_USG_DELTA', None)
    leverage_ts_delta = player_data.get('LEVERAGE_TS_DELTA', None)
    rs_usg_pct = player_data.get('USG_PCT', None)
    
    if pd.notna(leverage_usg_delta):
        has_high_usage_immunity = False
        if pd.notna(rs_usg_pct) and rs_usg_pct > 0.30:
            if leverage_usg_delta > -0.10:
                has_high_usage_immunity = True
        
        if not has_high_usage_immunity:
            efficiency_spikes = pd.notna(leverage_ts_delta) and leverage_ts_delta > 0.05
            would_trigger = leverage_usg_delta < -0.05 and not efficiency_spikes
            leverage_ts_str = f"{leverage_ts_delta:.4f}" if pd.notna(leverage_ts_delta) else "N/A"
            logger.info(f"    Abdication: LEVERAGE_USG_DELTA={leverage_usg_delta:.4f}, LEVERAGE_TS_DELTA={leverage_ts_str}")
            logger.info(f"      → {'WOULD TRIGGER' if would_trigger else 'OK (Smart Deference)' if efficiency_spikes else 'OK'}")
        else:
            logger.info(f"    Abdication: EXEMPTED (High-Usage Immunity: RS_USG_PCT={rs_usg_pct:.1%} > 30%)")
    else:
        logger.info(f"    Abdication: LEVERAGE_USG_DELTA MISSING")
    
    # 3. Creation Fragility Gate
    creation_tax = player_data.get('CREATION_TAX', None)
    creation_vol_ratio = player_data.get('CREATION_VOLUME_RATIO', None)
    rim_appetite = player_data.get('RS_RIM_APPETITE', None)
    age = player_data.get('AGE', None)
    
    if pd.notna(creation_tax):
        has_elite_creator_exemption = False
        if pd.notna(creation_vol_ratio):
            has_elite_creation_volume = creation_vol_ratio > 0.65
            if has_elite_creation_volume:
                has_elite_creator_exemption = True
        
        if creation_tax < -0.10:
            has_elite_creator_exemption = True
        
        has_elite_rim_force = pd.notna(rim_appetite) and rim_appetite > 0.20
        
        is_young_player = pd.notna(age) and age < 22
        leverage_ts_delta = player_data.get('LEVERAGE_TS_DELTA', None)
        leverage_usg_delta = player_data.get('LEVERAGE_USG_DELTA', None)
        has_positive_leverage = (pd.notna(leverage_ts_delta) and leverage_ts_delta > 0) or (pd.notna(leverage_usg_delta) and leverage_usg_delta > 0)
        young_player_exempt = is_young_player and has_positive_leverage
        
        would_trigger = creation_tax < -0.15 and not has_elite_creator_exemption and not has_elite_rim_force and not young_player_exempt
        
        logger.info(f"    Creation Fragility: CREATION_TAX={creation_tax:.4f}")
        creation_vol_str = f"{creation_vol_ratio:.4f}" if pd.notna(creation_vol_ratio) else "N/A"
        logger.info(f"      Elite Creator Exemption: {has_elite_creator_exemption} (Volume={creation_vol_str} > 0.65 OR Tax < -0.10)")
        rim_appetite_str = f"{rim_appetite:.4f}" if pd.notna(rim_appetite) else "N/A"
        age_str = f"{age:.0f}" if pd.notna(age) else "N/A"
        logger.info(f"      Elite Rim Force Exemption: {has_elite_rim_force} (RS_RIM_APPETITE={rim_appetite_str} > 0.20)")
        logger.info(f"      Young Player Exemption: {young_player_exempt} (AGE={age_str} < 22)")
        logger.info(f"      → {'WOULD TRIGGER' if would_trigger else 'EXEMPTED'}")
    else:
        logger.info(f"    Creation Fragility: CREATION_TAX MISSING")
    
    # Tier 2: Data Quality Gates
    logger.info("\n  TIER 2: DATA QUALITY GATES")
    
    # Leverage Data Penalty
    leverage_usg = player_data.get('LEVERAGE_USG_DELTA', None)
    leverage_ts = player_data.get('LEVERAGE_TS_DELTA', None)
    clutch_min = player_data.get('CLUTCH_MIN_TOTAL', 0)
    
    missing_leverage = pd.isna(leverage_usg) or pd.isna(leverage_ts)
    insufficient_clutch = pd.isna(clutch_min) or clutch_min < 15
    
    if missing_leverage or insufficient_clutch:
        logger.info(f"    Leverage Data Penalty: {'WOULD TRIGGER' if missing_leverage or insufficient_clutch else 'OK'}")
        if missing_leverage:
            logger.info(f"      Missing leverage data: USG={pd.isna(leverage_usg)}, TS={pd.isna(leverage_ts)}")
        if insufficient_clutch:
            clutch_min_str = f"{clutch_min:.0f}" if pd.notna(clutch_min) else "N/A"
            logger.info(f"      Insufficient clutch minutes: {clutch_min_str} < 15")
    else:
        logger.info(f"    Leverage Data Penalty: OK")
    
    # Tier 3: Contextual Gates
    logger.info("\n  TIER 3: CONTEXTUAL GATES")
    
    # Replacement Level Creator Gate
    usage = player_data.get('USG_PCT', None)
    sq_gen_delta = player_data.get('SHOT_QUALITY_GENERATION_DELTA', None)
    
    if pd.notna(usage) and pd.notna(sq_gen_delta):
        would_trigger = usage > 0.25 and sq_gen_delta < -0.05
        
        # Check exemptions
        rim_appetite = player_data.get('RS_RIM_APPETITE', None)
        ast_pct = player_data.get('AST_PCT', None)
        creation_vol_ratio = player_data.get('CREATION_VOLUME_RATIO', None)
        
        has_elite_rim_force = pd.notna(rim_appetite) and rim_appetite > 0.20
        has_elite_playmaker = (pd.notna(ast_pct) and ast_pct > 0.30) or (pd.notna(creation_vol_ratio) and creation_vol_ratio > 0.50)
        has_elite_volume_creator = pd.notna(creation_vol_ratio) and creation_vol_ratio > 0.65
        
        has_exemption = has_elite_rim_force or has_elite_playmaker or has_elite_volume_creator
        
        logger.info(f"    Replacement Level Creator: USG_PCT={usage:.1%} > 25% AND SQ_DELTA={sq_gen_delta:.4f} < -0.05")
        logger.info(f"      → {'WOULD TRIGGER' if would_trigger and not has_exemption else 'EXEMPTED' if has_exemption else 'OK'}")
        if has_exemption:
            exemption_reasons = []
            if has_elite_rim_force:
                exemption_reasons.append(f"Elite Rim Force (RS_RIM_APPETITE={rim_appetite:.4f} > 0.20)")
            if has_elite_playmaker:
                ast_pct_str = f"{ast_pct:.4f}" if pd.notna(ast_pct) else "N/A"
                creation_vol_str = f"{creation_vol_ratio:.4f}" if pd.notna(creation_vol_ratio) else "N/A"
                exemption_reasons.append(f"Elite Playmaker (AST_PCT={ast_pct_str} > 0.30 OR CREATION_VOLUME_RATIO={creation_vol_str} > 0.50)")
            if has_elite_volume_creator:
                exemption_reasons.append(f"Elite Volume Creator (CREATION_VOLUME_RATIO={creation_vol_ratio:.4f} > 0.65)")
            logger.info(f"        Exemption Reasons: {', '.join(exemption_reasons)}")
    else:
        logger.info(f"    Replacement Level Creator: MISSING DATA (USG_PCT={usage is not None}, SQ_DELTA={sq_gen_delta is not None})")
    
    # Bag Check Gate
    iso_freq = player_data.get('ISO_FREQUENCY', None)
    pnr_freq = player_data.get('PNR_HANDLER_FREQUENCY', None)
    
    if pd.notna(iso_freq) or pd.notna(pnr_freq):
        self_created_freq = (iso_freq if pd.notna(iso_freq) else 0.0) + (pnr_freq if pd.notna(pnr_freq) else 0.0)
    else:
        # Use proxy
        creation_vol_ratio = player_data.get('CREATION_VOLUME_RATIO', 0)
        if pd.notna(creation_vol_ratio) and creation_vol_ratio > 0.15:
            self_created_freq = creation_vol_ratio * 0.35
        else:
            self_created_freq = creation_vol_ratio * 0.6 if pd.notna(creation_vol_ratio) else 0.0
    
    if pd.notna(self_created_freq):
        would_trigger = self_created_freq < 0.10
        
        # Check exemptions
        ast_pct = player_data.get('AST_PCT', None)
        creation_vol_ratio = player_data.get('CREATION_VOLUME_RATIO', None)
        rim_appetite = player_data.get('RS_RIM_APPETITE', None)
        
        has_elite_playmaker = (pd.notna(ast_pct) and ast_pct > 0.30) or (pd.notna(creation_vol_ratio) and creation_vol_ratio > 0.50)
        has_elite_rim_force = pd.notna(rim_appetite) and rim_appetite > 0.20
        
        has_exemption = has_elite_playmaker or has_elite_rim_force
        
        logger.info(f"    Bag Check: SELF_CREATED_FREQ={self_created_freq:.4f} < 0.10")
        logger.info(f"      → {'WOULD TRIGGER' if would_trigger and not has_exemption else 'EXEMPTED' if has_exemption else 'OK'}")
        if has_exemption:
            exemption_reasons = []
            if has_elite_playmaker:
                ast_pct_str = f"{ast_pct:.4f}" if pd.notna(ast_pct) else "N/A"
                creation_vol_str = f"{creation_vol_ratio:.4f}" if pd.notna(creation_vol_ratio) else "N/A"
                exemption_reasons.append(f"Elite Playmaker (AST_PCT={ast_pct_str} > 0.30 OR CREATION_VOLUME_RATIO={creation_vol_str} > 0.50)")
            if has_elite_rim_force:
                exemption_reasons.append(f"Elite Rim Force (RS_RIM_APPETITE={rim_appetite:.4f} > 0.20)")
            logger.info(f"        Exemption Reasons: {', '.join(exemption_reasons)}")
    else:
        logger.info(f"    Bag Check: SELF_CREATED_FREQ MISSING")
    
    # ========================================================================
    # SECTION 3: MODEL PREDICTION ANALYSIS
    # ========================================================================
    logger.info("\n" + "=" * 100)
    logger.info("SECTION 3: MODEL PREDICTION ANALYSIS")
    logger.info("=" * 100)
    
    # Get raw model prediction (without gates)
    prediction_no_gates = predictor.predict_archetype_at_usage(
        player_data,
        test_usage,
        apply_phase3_fixes=True,
        apply_hard_gates=False
    )
    
    star_level_no_gates = prediction_no_gates.get('star_level_potential', 0)
    probs_no_gates = prediction_no_gates.get('probabilities', {})
    
    logger.info(f"\n  Model Prediction (No Gates):")
    logger.info(f"    Star Level: {star_level_no_gates:.2%}")
    logger.info(f"    King: {probs_no_gates.get('King', 0):.2%}")
    logger.info(f"    Bulldozer: {probs_no_gates.get('Bulldozer', 0):.2%}")
    logger.info(f"    Sniper: {probs_no_gates.get('Sniper', 0):.2%}")
    logger.info(f"    Victim: {probs_no_gates.get('Victim', 0):.2%}")
    
    logger.info(f"\n  Model Prediction (With Gates):")
    logger.info(f"    Star Level: {star_level_with_gates:.2%}")
    probs_with_gates = prediction_with_gates.get('probabilities', {})
    logger.info(f"    King: {probs_with_gates.get('King', 0):.2%}")
    logger.info(f"    Bulldozer: {probs_with_gates.get('Bulldozer', 0):.2%}")
    logger.info(f"    Sniper: {probs_with_gates.get('Sniper', 0):.2%}")
    logger.info(f"    Victim: {probs_with_gates.get('Victim', 0):.2%}")
    
    gate_impact = star_level_no_gates - star_level_with_gates
    logger.info(f"\n  Gate Impact: {gate_impact:+.2%} ({star_level_no_gates:.2%} → {star_level_with_gates:.2%})")
    
    # ========================================================================
    # SECTION 4: ROOT CAUSE ANALYSIS
    # ========================================================================
    logger.info("\n" + "=" * 100)
    logger.info("SECTION 4: ROOT CAUSE ANALYSIS")
    logger.info("=" * 100)
    
    logger.info("\n  Why is this player passing as a False Positive?")
    
    # Check if gates are applying
    if gate_impact < 0.01:
        logger.info("    ❌ GATES NOT APPLYING: Gates have minimal impact (<1%)")
        logger.info("      → Need to investigate why gates aren't triggering")
    else:
        logger.info(f"    ⚠️  GATES APPLYING: Gates reduce star level by {gate_impact:.2%}, but still above 55%")
        logger.info("      → Gates are working but may need to be more aggressive")
    
    # Check if model is over-confident
    if star_level_no_gates > 0.80:
        logger.info(f"    ❌ MODEL OVER-CONFIDENCE: Model predicts {star_level_no_gates:.2%} star level without gates")
        logger.info("      → Model may be over-weighting certain features")
    
    # Check for missing critical data
    missing_critical = []
    if pd.isna(leverage_usg) or pd.isna(leverage_ts):
        missing_critical.append("Leverage data")
    if pd.isna(creation_tax):
        missing_critical.append("Creation tax")
    if pd.isna(rim_appetite):
        missing_critical.append("Rim appetite")
    
    if missing_critical:
        logger.info(f"    ⚠️  MISSING CRITICAL DATA: {', '.join(missing_critical)}")
        logger.info("      → Missing data may prevent gates from applying")
    
    # Check for exemptions that may be too broad
    exemption_count = 0
    if has_elite_creator_exemption:
        exemption_count += 1
    if has_elite_rim_force:
        exemption_count += 1
    if has_elite_playmaker:
        exemption_count += 1
    if has_high_usage_immunity:
        exemption_count += 1
    
    if exemption_count > 0:
        logger.info(f"    ⚠️  EXEMPTIONS APPLYING: {exemption_count} exemption(s) preventing gates from triggering")
        logger.info("      → Exemptions may be too broad for this player profile")
    
    return {
        'player_name': player_name,
        'season': season,
        'star_level_no_gates': star_level_no_gates,
        'star_level_with_gates': star_level_with_gates,
        'gate_impact': gate_impact,
        'confidence_flags': confidence_flags,
        'feature_values': feature_values
    }

def main():
    """Run audit on all false positive cases."""
    
    logger.info("=" * 100)
    logger.info("FALSE POSITIVE AUDIT")
    logger.info("=" * 100)
    
    predictor = ConditionalArchetypePredictor()
    
    results = []
    for player_name, season, test_usage, description in FALSE_POSITIVE_CASES:
        try:
            result = audit_case(predictor, player_name, season, test_usage)
            if result:
                results.append(result)
        except Exception as e:
            logger.error(f"Error auditing {player_name} ({season}): {e}", exc_info=True)
    
    # Summary
    logger.info("\n" + "=" * 100)
    logger.info("SUMMARY")
    logger.info("=" * 100)
    
    for result in results:
        logger.info(f"\n{result['player_name']} ({result['season']}):")
        logger.info(f"  Star Level (No Gates): {result['star_level_no_gates']:.2%}")
        logger.info(f"  Star Level (With Gates): {result['star_level_with_gates']:.2%}")
        logger.info(f"  Gate Impact: {result['gate_impact']:+.2%}")
        logger.info(f"  Confidence Flags: {result['confidence_flags'] if result['confidence_flags'] else 'None'}")

if __name__ == "__main__":
    main()


