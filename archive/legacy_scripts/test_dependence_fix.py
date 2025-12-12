"""
Test Dependence Score Fix
Check current predictions for system-dependent cases
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.nba_data.scripts.predict_conditional_archetype import ConditionalArchetypePredictor
import pandas as pd

# System-dependent cases from audit
system_dependent_cases = [
    ('Jordan Poole', '2021-22', 0.462),  # DEPENDENCE_SCORE
    ('Willy Hernangomez', '2016-17', 0.664),
    ('Christian Wood', '2020-21', 0.619),
    ('Domantas Sabonis', '2021-22', 0.609),
    ('Karl-Anthony Towns', '2015-16', 0.672),
    ('Karl-Anthony Towns', '2016-17', 0.643),
    ('Karl-Anthony Towns', '2017-18', 0.663),
    ('Karl-Anthony Towns', '2018-19', 0.646),
    ('Karl-Anthony Towns', '2019-20', 0.642),
    ('Karl-Anthony Towns', '2020-21', 0.614),
]

predictor = ConditionalArchetypePredictor()

print("=" * 80)
print("Current Predictions for System-Dependent Cases")
print("=" * 80)
print(f"{'Player':<25} {'Season':<12} {'DEP':<6} {'Star%':<8} {'Archetype':<25} {'Gate Applied':<15}")
print("-" * 80)

results = []

for name, season, dep_score in system_dependent_cases:
    try:
        player_data = predictor.get_player_data(name, season)
        if player_data is None:
            print(f"{name:<25} {season:<12} {dep_score:.3f} {'N/A':<8} {'NOT FOUND':<25}")
            continue
        
        # Test at 25% usage (standard test usage)
        result = predictor.predict_archetype_at_usage(
            player_data,
            usage_level=0.25,
            apply_phase3_fixes=True,
            apply_hard_gates=True
        )
        
        star_level = result['star_level_potential']
        archetype = result['predicted_archetype']
        
        # Check if System Merchant Gate was applied
        gate_applied = "System Merchant" in str(result.get('phase3_flags', []))
        
        # Check phase3_metadata for gate info
        metadata = result.get('phase3_metadata', {})
        flags = result.get('phase3_flags', [])
        
        system_merchant_gate = any('SYSTEM MERCHANT' in flag.upper() for flag in flags)
        
        print(f"{name:<25} {season:<12} {dep_score:.3f} {star_level*100:>6.1f}% {archetype:<25} {'YES' if system_merchant_gate else 'NO':<15}")
        
        results.append({
            'name': name,
            'season': season,
            'dependence_score': dep_score,
            'star_level': star_level,
            'archetype': archetype,
            'gate_applied': system_merchant_gate,
            'flags': flags,
        })
    except Exception as e:
        print(f"{name:<25} {season:<12} {dep_score:.3f} {'ERROR':<8} {str(e)[:25]:<25}")

print("\n" + "=" * 80)
print("Summary")
print("=" * 80)

df = pd.DataFrame(results)
if len(df) > 0:
    print(f"Total cases tested: {len(df)}")
    print(f"Cases with gate applied: {df['gate_applied'].sum()}")
    print(f"Cases above 0.45 threshold: {(df['dependence_score'] > 0.45).sum()}")
    print(f"Cases above 0.60 threshold: {(df['dependence_score'] > 0.60).sum()}")
    print(f"\nAverage star-level: {df['star_level'].mean():.1%}")
    print(f"Cases still above 55%: {(df['star_level'] > 0.55).sum()}")
    print(f"Cases still above 65%: {(df['star_level'] > 0.65).sum()}")
    
    print("\nCases that should be caught but aren't:")
    failed = df[(df['dependence_score'] > 0.45) & (df['star_level'] > 0.55) & (~df['gate_applied'])]
    for _, row in failed.iterrows():
        print(f"  - {row['name']} ({row['season']}): DEP={row['dependence_score']:.3f}, Star={row['star_level']:.1%}")

