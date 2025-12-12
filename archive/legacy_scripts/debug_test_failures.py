"""
Diagnostic script to investigate specific test case failures.
Focuses on: Jordan Poole, Lauri Markkanen, Tyrese Haliburton.
"""


import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging

Add scripts directory to path

sys.path.insert(0, str(Path(file).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(name)

def debug_failures():
predictor = ConditionalArchetypePredictor(use_rfe_model=True)

code
Code
download
content_copy
expand_less
# Cases to investigate
cases = [
    # Case 1: Tyrese Haliburton - Capped at 30% (Likely Gate Issue)
    {
        "name": "Tyrese Haliburton",
        "season": "2021-22",
        "target_usage": 0.28,
        "expected": "High Star Level",
        "issue": "Currently capped at 30%"
    },
    # Case 2: Lauri Markkanen - Just missed threshold
    {
        "name": "Lauri Markkanen",
        "season": "2021-22",
        "target_usage": 0.26,
        "expected": "High Star Level",
        "issue": "64.16% (Need >= 65%)"
    },
    # Case 3: Jordan Poole - False Positive
    {
        "name": "Jordan Poole",
        "season": "2021-22",
        "target_usage": 0.30,
        "expected": "Low Star Level (or High Dependence)",
        "issue": "87.62% (Too High)"
    }
]

print("="*80)
print("DEEP DIVE DIAGNOSTICS")
print("="*80)

for case in cases:
    print(f"\nAnalyzing {case['name']} ({case['season']})")
    print(f"Target Usage: {case['target_usage']}")
    print("-" * 40)
    
    player_data = predictor.get_player_data(case['name'], case['season'])
    
    if player_data is None:
        print("❌ Data not found")
        continue
        
    # 1. Inspect Raw Features
    print("RAW FEATURES:")
    cols = [
        'USG_PCT', 'CREATION_VOLUME_RATIO', 'CREATION_TAX', 
        'RS_RIM_APPETITE', 'EFG_ISO_WEIGHTED', 'LEVERAGE_USG_DELTA',
        'RS_PRESSURE_APPETITE', 'SELF_CREATED_FREQ', 'ISO_FREQUENCY', 'PNR_HANDLER_FREQUENCY'
    ]
    for c in cols:
        val = player_data.get(c, 'N/A')
        print(f"  {c}: {val}")
        
    # 2. Check Gate Thresholds vs Values
    print("\nGATE LOGIC CHECK:")
    
    # Fragility Gate
    rim_appetite = player_data.get('RS_RIM_APPETITE', 0)
    fragility_threshold = 0.1746
    print(f"  Fragility Check: {rim_appetite} < {fragility_threshold}? {'YES (Triggered)' if rim_appetite < fragility_threshold else 'NO'}")
    
    # Creator Exemption Logic
    # Current logic: creation_vol > 0.60 AND usg_pct > 0.25 AND (tax > -0.05 OR rim > 0.1746)
    creation_vol = player_data.get('CREATION_VOLUME_RATIO', 0)
    usg_pct = player_data.get('USG_PCT', 0)
    creation_tax = player_data.get('CREATION_TAX', 0)
    
    is_high_vol = creation_vol > 0.60
    is_high_usg = usg_pct > 0.25
    is_efficient = creation_tax >= -0.05
    has_rim = rim_appetite >= 0.1746
    
    print(f"  Creator Exemption Check:")
    print(f"    - High Vol (>0.60): {is_high_vol} ({creation_vol:.3f})")
    print(f"    - High Usg (>0.25): {is_high_usg} ({usg_pct:.3f})")
    print(f"    - Efficient (>-0.05): {is_efficient} ({creation_tax:.3f})")
    print(f"    - Has Rim: {has_rim}")
    print(f"    -> EXEMPTION STATUS: {'GRANTED' if is_high_vol and is_high_usg and (is_efficient or has_rim) else 'DENIED'}")
    
    # Bag Check Gate
    self_created = player_data.get('SELF_CREATED_FREQ', 0)
    if pd.isna(self_created) or self_created == 0:
        # Proxy check
        if creation_vol > 0.15:
            proxy = creation_vol * 0.35
        else:
            proxy = creation_vol * 0.60
        print(f"  Bag Check Check (Proxy): {proxy:.3f} < 0.10? {'YES (Triggered)' if proxy < 0.10 else 'NO'}")
    else:
        print(f"  Bag Check Check (Actual): {self_created:.3f} < 0.10? {'YES (Triggered)' if self_created < 0.10 else 'NO'}")

    # 3. Run Prediction with Debugging
    print("\nPREDICTION RESULT:")
    pred = predictor.predict_archetype_at_usage(player_data, case['target_usage'])
    print(f"  Star Level: {pred['star_level_potential']:.4f}")
    print(f"  Archetype: {pred['predicted_archetype']}")
    print(f"  Flags: {pred['confidence_flags']}")
    
    # 4. Universal Projection Check
    print("\nPROJECTION CHECK:")
    # Manually verify projection logic
    if case['target_usage'] > usg_pct:
        # Check bucket
        buckets = predictor.usage_buckets
        target_bucket = None
        for bucket_name, data in buckets.items():
            if data['min'] <= case['target_usage'] < data['max']:
                target_bucket = data
                break
        
        if target_bucket:
            median_creation = target_bucket['stats']['median_creation_vol']
            print(f"  Target Bucket Median Creation: {median_creation:.3f}")
            
            # Logic: if current > current_bucket_median, keep offset?
            # Actually universal projection takes the median of the target bucket if we are projecting up significantly
            # Let's see what the predictor did. We can't see inside easily without modifying code, 
            # but we can infer from the result if it's high.
        else:
            print("  No target bucket found")

if name == "main":
debug_failures()