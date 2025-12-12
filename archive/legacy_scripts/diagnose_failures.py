"""
Diagnostic script to inspect feature values for failing test cases:
1. Julius Randle (2020-21)
2. Domantas Sabonis (2021-22)
3. Tyrese Haliburton (2021-22)
4. Markelle Fultz (2019-20, 2022-23, 2023-24)
"""


import pandas as pd
import sys
from pathlib import Path

Add scripts directory to path

sys.path.insert(0, str(Path(file).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor

def diagnose():
predictor = ConditionalArchetypePredictor()

code
Code
download
content_copy
expand_less
cases = [
    ("Julius Randle", "2020-21"),
    ("Domantas Sabonis", "2021-22"),
    ("Tyrese Haliburton", "2021-22"),
    ("Markelle Fultz", "2019-20"),
    ("Markelle Fultz", "2022-23"),
    ("Markelle Fultz", "2023-24")
]

print(f"{'Player':<20} {'Season':<8} {'USG':<6} {'VolRatio':<8} {'SelfCrFreq':<10} {'IsoEff':<8} {'RimApp':<8} {'AbdRisk':<8} {'Pred'}")
print("-" * 100)

for player, season in cases:
    data = predictor.get_player_data(player, season)
    if data is None:
        print(f"{player:<20} {season:<8} NOT FOUND")
        continue
        
    # Run prediction to see what happens
    pred = predictor.predict_archetype_at_usage(data, data.get('USG_PCT', 0.25))
    
    # Extract features
    usg = data.get('USG_PCT', 0)
    vol_ratio = data.get('CREATION_VOLUME_RATIO', 0)
    
    # Self Created Freq (for Bag Check)
    iso = data.get('ISO_FREQUENCY', 0)
    pnr = data.get('PNR_HANDLER_FREQUENCY', 0)
    self_created = iso + pnr
    # Also check existing SELF_CREATED_FREQ if present
    if 'SELF_CREATED_FREQ' in data:
        self_created_feat = data['SELF_CREATED_FREQ']
    else:
        self_created_feat = 0
        
    iso_eff = data.get('EFG_ISO_WEIGHTED', 0)
    rim_app = data.get('RS_RIM_APPETITE', 0)
    abd_risk = data.get('ABDICATION_RISK', 0) # Derived from LEVERAGE_USG_DELTA
    
    star_level = pred['star_level_potential']
    archetype = pred['predicted_archetype']
    
    print(f"{player:<20} {season:<8} {usg:<6.3f} {vol_ratio:<8.3f} {self_created:<10.3f} {iso_eff:<8.3f} {rim_app:<8.3f} {abd_risk:<8.3f} {star_level:.2f} ({archetype})")
    
    # Check specific gates
    if self_created < 0.10:
         print(f"  -> Fails Bag Check (<0.10). Proxy would be: {vol_ratio * 0.35:.3f}")
    
    if rim_app < 0.1746: # approx threshold
         print(f"  -> Fails Fragility (<0.1746)")

if name == "main":
diagnose()