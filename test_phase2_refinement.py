"""
Test Phase 2 Refinement: Replacement Level Creator Gate

This script tests the refined gate logic on:
1. False Positives (should now be caught)
2. True Positives (should still pass)
"""

import pandas as pd
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor

# Test cases
FALSE_POSITIVE_CASES = [
    ("D'Angelo Russell", "2018-19", 0.31, "Should be caught by gate (removed exemptions)"),
    ("Julius Randle", "2020-21", 0.30, "Should be caught by gate (refined rim force exemption)"),
]

TRUE_POSITIVE_CASES = [
    ("Nikola Jokić", "2018-19", 0.30, "Should still pass (refined rim force exemption)"),
    ("Anthony Davis", "2016-17", 0.30, "Should still pass (refined rim force exemption)"),
    ("Joel Embiid", "2016-17", 0.30, "Should still pass (refined rim force exemption)"),
]

def test_case(predictor, player_name, season, test_usage, expected_outcome):
    """Test a single case."""
    print(f"\n{'='*80}")
    print(f"Testing: {player_name} ({season})")
    print(f"Expected: {expected_outcome}")
    print(f"{'='*80}")
    
    # Get player data
    player_data = predictor.get_player_data(player_name, season)
    if player_data is None:
        print(f"  ❌ NO DATA FOUND")
        return None
    
    # Check key features
    usage = player_data.get('USG_PCT', None)
    sq_delta = player_data.get('SHOT_QUALITY_GENERATION_DELTA', None)
    rim_appetite = player_data.get('RS_RIM_APPETITE', None)
    rim_pct = player_data.get('RS_RIM_PCT', None)
    leverage_ts_delta = player_data.get('LEVERAGE_TS_DELTA', None)
    creation_tax = player_data.get('CREATION_TAX', None)
    ast_pct = player_data.get('AST_PCT', None)
    creation_vol_ratio = player_data.get('CREATION_VOLUME_RATIO', None)
    
    print(f"\n  Key Features:")
    print(f"    USG_PCT: {usage:.1%}" if pd.notna(usage) else "    USG_PCT: MISSING")
    print(f"    SHOT_QUALITY_GENERATION_DELTA: {sq_delta:.4f}" if pd.notna(sq_delta) else "    SHOT_QUALITY_GENERATION_DELTA: MISSING")
    print(f"    RS_RIM_APPETITE: {rim_appetite:.4f}" if pd.notna(rim_appetite) else "    RS_RIM_APPETITE: MISSING")
    print(f"    RS_RIM_PCT: {rim_pct:.1%}" if pd.notna(rim_pct) else "    RS_RIM_PCT: MISSING")
    print(f"    LEVERAGE_TS_DELTA: {leverage_ts_delta:.4f}" if pd.notna(leverage_ts_delta) else "    LEVERAGE_TS_DELTA: MISSING")
    print(f"    CREATION_TAX: {creation_tax:.4f}" if pd.notna(creation_tax) else "    CREATION_TAX: MISSING")
    print(f"    AST_PCT: {ast_pct:.1%}" if pd.notna(ast_pct) else "    AST_PCT: MISSING")
    print(f"    CREATION_VOLUME_RATIO: {creation_vol_ratio:.4f}" if pd.notna(creation_vol_ratio) else "    CREATION_VOLUME_RATIO: MISSING")
    
    # Check gate conditions
    print(f"\n  Gate Conditions:")
    has_high_usage = pd.notna(usage) and usage > 0.25
    has_negative_sq_delta = pd.notna(sq_delta) and sq_delta < -0.05
    
    print(f"    High Usage (>25%): {has_high_usage}")
    print(f"    Negative SQ_DELTA (<-0.05): {has_negative_sq_delta}")
    
    # Check refined Elite Rim Force exemption
    is_elite_rim_force = False
    if pd.notna(rim_appetite) and rim_appetite > 0.20:
        has_efficient_rim_finishing = pd.notna(rim_pct) and rim_pct > 0.60
        has_positive_leverage = pd.notna(leverage_ts_delta) and leverage_ts_delta > 0
        has_positive_creation = pd.notna(creation_tax) and creation_tax > -0.10
        has_positive_signal = has_positive_leverage or has_positive_creation
        
        is_elite_rim_force = has_efficient_rim_finishing and has_positive_signal
        
        print(f"    Elite Rim Force Exemption:")
        print(f"      RS_RIM_APPETITE > 0.20: {rim_appetite > 0.20 if pd.notna(rim_appetite) else False}")
        print(f"      RS_RIM_PCT > 60%: {has_efficient_rim_finishing}")
        print(f"      Positive Signal: {has_positive_signal} (Leverage: {has_positive_leverage}, Creation: {has_positive_creation})")
        print(f"      → EXEMPTED: {is_elite_rim_force}")
    
    # Check if gate would trigger
    gate_would_trigger = has_high_usage and has_negative_sq_delta and not is_elite_rim_force
    print(f"\n    Gate Would Trigger: {gate_would_trigger}")
    
    # Run prediction
    result = predictor.predict_archetype_at_usage(
        player_data,
        test_usage,
        apply_phase3_fixes=True,
        apply_hard_gates=True
    )
    
    star_level = result.get('star_level_potential', 0)
    archetype = result.get('predicted_archetype', 'Unknown')
    confidence_flags = result.get('confidence_flags', [])
    
    print(f"\n  Prediction Results:")
    print(f"    Star Level: {star_level:.2%}")
    print(f"    Archetype: {archetype}")
    if confidence_flags:
        print(f"    Flags: {', '.join(confidence_flags)}")
    
    # Evaluate
    if "False Positive" in expected_outcome or "Should be caught" in expected_outcome:
        # Should be caught (star level < 55%)
        passed = star_level < 0.55
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n  Result: {status}")
        if not passed:
            print(f"    Expected star level < 55%, got {star_level:.2%}")
    else:
        # Should still pass (star level >= 65%)
        passed = star_level >= 0.65
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n  Result: {status}")
        if not passed:
            print(f"    Expected star level >= 65%, got {star_level:.2%}")
    
    return {
        'player_name': player_name,
        'season': season,
        'star_level': star_level,
        'gate_would_trigger': gate_would_trigger,
        'is_elite_rim_force': is_elite_rim_force,
        'passed': passed
    }

def main():
    """Run tests."""
    print("="*80)
    print("PHASE 2 REFINEMENT TEST")
    print("="*80)
    
    predictor = ConditionalArchetypePredictor()
    
    print("\n" + "="*80)
    print("FALSE POSITIVE CASES (Should be caught)")
    print("="*80)
    
    false_positive_results = []
    for player_name, season, test_usage, expected in FALSE_POSITIVE_CASES:
        result = test_case(predictor, player_name, season, test_usage, expected)
        if result:
            false_positive_results.append(result)
    
    print("\n" + "="*80)
    print("TRUE POSITIVE CASES (Should still pass)")
    print("="*80)
    
    true_positive_results = []
    for player_name, season, test_usage, expected in TRUE_POSITIVE_CASES:
        result = test_case(predictor, player_name, season, test_usage, expected)
        if result:
            true_positive_results.append(result)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    print(f"\nFalse Positives: {sum(1 for r in false_positive_results if r['passed'])}/{len(false_positive_results)} passed")
    for r in false_positive_results:
        print(f"  {r['player_name']} ({r['season']}): {r['star_level']:.2%} {'✅' if r['passed'] else '❌'}")
    
    print(f"\nTrue Positives: {sum(1 for r in true_positive_results if r['passed'])}/{len(true_positive_results)} passed")
    for r in true_positive_results:
        print(f"  {r['player_name']} ({r['season']}): {r['star_level']:.2%} {'✅' if r['passed'] else '❌'}")

if __name__ == "__main__":
    main()







