"""
Analyze Model Misses: Why did the model rate these players so highly?

This script investigates specific cases where the model predicted "King (Resilient Star)"
at 25% usage, but the players didn't pan out as stars.

Key Questions:
1. What stress vectors drove the high predictions?
2. Should gates have caught them?
3. What patterns do these misses share?
4. Are there systematic model limitations?
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor

# Cases to investigate
CASES_TO_INVESTIGATE = [
    ("Willy Hernangomez", "2016-17", 18),
    ("Elfrid Payton", "2018-19", 59),
    ("Markelle Fultz", "2022-23", 60),
    ("Devonte' Graham", "2019-20", 65),
    ("Kris Dunn", "2017-18", 69),
    ("Dejounte Murray", "2021-22", 77),
    ("Dennis Schröder", "2017-18", 133),
    ("Dion Waiters", "2016-17", 137),
    ("Kawhi Leonard", "2015-16", 166),  # Special case - labeled "Luxury Component"
    ("Jayson Tatum", "2018-19", 365),  # Special case - labeled "Avoid" but later seasons correct
]

def load_data():
    """Load the expanded predictions dataset."""
    df = pd.read_csv("results/expanded_predictions.csv")
    return df

def analyze_case(df, player_name, season, rank):
    """Analyze a specific case in detail."""
    case = df[(df['PLAYER_NAME'] == player_name) & (df['SEASON'] == season)].iloc[0]
    
    print(f"\n{'='*80}")
    print(f"CASE: {player_name} ({season}) - Rank #{rank}")
    print(f"{'='*80}")
    
    # Basic info
    print(f"\nBasic Info:")
    print(f"  Age: {case['AGE']:.0f}")
    print(f"  RS Usage: {case['RS_USG_PCT']*100:.1f}%")
    print(f"  Current Archetype: {case['CURRENT_ARCHETYPE']}")
    print(f"  Current Star Level: {case['CURRENT_STAR_LEVEL']*100:.2f}%")
    print(f"  AT 25% Usage Archetype: {case['AT_25_USG_ARCHETYPE']}")
    print(f"  AT 25% Usage Star Level: {case['AT_25_USG_STAR_LEVEL']*100:.2f}%")
    print(f"  Performance Score: {case['PERFORMANCE_SCORE']*100:.2f}%" if pd.notna(case.get('PERFORMANCE_SCORE')) else "  Performance Score: N/A")
    print(f"  Dependence Score: {case['DEPENDENCE_SCORE']*100:.2f}%" if pd.notna(case.get('DEPENDENCE_SCORE')) else "  Dependence Score: N/A")
    print(f"  Risk Category: {case['RISK_CATEGORY']}")
    
    # Stress vectors
    print(f"\nStress Vectors:")
    print(f"  CREATION_VOLUME_RATIO: {case['CREATION_VOLUME_RATIO']:.4f}" if pd.notna(case.get('CREATION_VOLUME_RATIO')) else "  CREATION_VOLUME_RATIO: N/A")
    print(f"  CREATION_TAX: {case['CREATION_TAX']:.4f}" if pd.notna(case.get('CREATION_TAX')) else "  CREATION_TAX: N/A")
    print(f"  LEVERAGE_USG_DELTA: {case['LEVERAGE_USG_DELTA']:.4f}" if pd.notna(case.get('LEVERAGE_USG_DELTA')) else "  LEVERAGE_USG_DELTA: N/A")
    print(f"  LEVERAGE_TS_DELTA: {case['LEVERAGE_TS_DELTA']:.4f}" if pd.notna(case.get('LEVERAGE_TS_DELTA')) else "  LEVERAGE_TS_DELTA: N/A")
    print(f"  RS_PRESSURE_APPETITE: {case['RS_PRESSURE_APPETITE']:.4f}" if pd.notna(case.get('RS_PRESSURE_APPETITE')) else "  RS_PRESSURE_APPETITE: N/A")
    print(f"  RS_PRESSURE_RESILIENCE: {case['RS_PRESSURE_RESILIENCE']:.4f}" if pd.notna(case.get('RS_PRESSURE_RESILIENCE')) else "  RS_PRESSURE_RESILIENCE: N/A")
    print(f"  RS_RIM_APPETITE: {case['RS_RIM_APPETITE']:.4f}" if pd.notna(case.get('RS_RIM_APPETITE')) else "  RS_RIM_APPETITE: N/A")
    print(f"  EFG_ISO_WEIGHTED: {case['EFG_ISO_WEIGHTED']:.4f}" if pd.notna(case.get('EFG_ISO_WEIGHTED')) else "  EFG_ISO_WEIGHTED: N/A")
    print(f"  EFG_PCT_0_DRIBBLE: {case['EFG_PCT_0_DRIBBLE']:.4f}" if pd.notna(case.get('EFG_PCT_0_DRIBBLE')) else "  EFG_PCT_0_DRIBBLE: N/A")
    
    # Gate analysis
    print(f"\nGate Analysis:")
    
    # Check for negative signals
    leverage_usg = case.get('LEVERAGE_USG_DELTA')
    leverage_ts = case.get('LEVERAGE_TS_DELTA')
    creation_tax = case.get('CREATION_TAX')
    
    negative_signals = []
    if pd.notna(leverage_usg) and leverage_usg < -0.05:
        negative_signals.append(f"Abdication (LEVERAGE_USG_DELTA={leverage_usg:.3f})")
    if pd.notna(leverage_ts) and leverage_ts < -0.15:
        negative_signals.append(f"Leverage TS Collapse (LEVERAGE_TS_DELTA={leverage_ts:.3f})")
    if pd.notna(creation_tax) and creation_tax < -0.20:
        negative_signals.append(f"Creation Tax (CREATION_TAX={creation_tax:.3f})")
    
    if negative_signals:
        print(f"  ⚠️  Negative Signals: {', '.join(negative_signals)}")
    else:
        print(f"  ✅ No major negative signals")
    
    # Check rim pressure
    rim_appetite = case.get('RS_RIM_APPETITE')
    if pd.notna(rim_appetite):
        # Bottom 20th percentile threshold is ~0.1746
        if rim_appetite < 0.1746:
            print(f"  ⚠️  Low Rim Pressure (RS_RIM_APPETITE={rim_appetite:.4f} < 0.1746) - Fragility Gate should apply")
        else:
            print(f"  ✅ Adequate Rim Pressure (RS_RIM_APPETITE={rim_appetite:.4f})")
    else:
        print(f"  ⚠️  Missing Rim Pressure Data")
    
    # Check creation volume
    creation_vol = case.get('CREATION_VOLUME_RATIO')
    if pd.notna(creation_vol):
        if creation_vol > 0.60:
            print(f"  ✅ High Creation Volume (CREATION_VOLUME_RATIO={creation_vol:.4f} > 0.60) - Volume Exemption")
        elif creation_vol < 0.15:
            print(f"  ⚠️  Low Creation Volume (CREATION_VOLUME_RATIO={creation_vol:.4f} < 0.15) - Role Player Signal")
        else:
            print(f"  ⚠️  Moderate Creation Volume (CREATION_VOLUME_RATIO={creation_vol:.4f}) - Gray Area")
    else:
        print(f"  ⚠️  Missing Creation Volume Data")
    
    # Check data completeness
    critical_features = ['CREATION_VOLUME_RATIO', 'CREATION_TAX', 'LEVERAGE_USG_DELTA', 
                        'LEVERAGE_TS_DELTA', 'RS_PRESSURE_APPETITE', 'RS_PRESSURE_RESILIENCE']
    present_count = sum(1 for feat in critical_features if pd.notna(case.get(feat)))
    completeness = present_count / len(critical_features)
    
    if completeness < 0.67:
        print(f"  ⚠️  Low Data Completeness ({present_count}/{len(critical_features)} = {completeness:.1%} < 67%) - Data Completeness Gate should apply")
    else:
        print(f"  ✅ Adequate Data Completeness ({present_count}/{len(critical_features)} = {completeness:.1%})")
    
    # Pattern analysis
    print(f"\nPattern Analysis:")
    
    # High creation volume but negative creation tax?
    if pd.notna(creation_vol) and pd.notna(creation_tax):
        if creation_vol > 0.60 and creation_tax < -0.10:
            print(f"  ⚠️  PATTERN: High Volume + Negative Tax = 'Empty Calories' Creator")
            print(f"      (Volume={creation_vol:.3f}, Tax={creation_tax:.3f})")
        elif creation_vol > 0.60 and creation_tax >= -0.05:
            print(f"  ✅ PATTERN: High Volume + Efficient Creation = True Creator")
    
    # Positive leverage but negative creation?
    if pd.notna(leverage_usg) and pd.notna(creation_tax):
        if leverage_usg > 0.05 and creation_tax < -0.10:
            print(f"  ⚠️  PATTERN: Scales in Clutch but Inefficient Creation = 'Volume Scorer'")
    
    # High pressure resilience but low rim pressure?
    pressure_resilience = case.get('RS_PRESSURE_RESILIENCE')
    if pd.notna(pressure_resilience) and pd.notna(rim_appetite):
        if pressure_resilience > 0.50 and rim_appetite < 0.20:
            print(f"  ⚠️  PATTERN: Good Jump Shooter but No Rim Pressure = 'Fragile'")
    
    return case

def compare_to_successful_cases(df):
    """Compare misses to successful predictions."""
    print(f"\n{'='*80}")
    print("COMPARISON: Misses vs. Successful Cases")
    print(f"{'='*80}")
    
    # Get successful cases (known stars)
    successful = df[
        (df['PLAYER_NAME'].isin(['Shai Gilgeous-Alexander', 'Jalen Brunson', 'Tyrese Haliburton', 
                                 'Tyrese Maxey', 'Pascal Siakam'])) &
        (df['AT_25_USG_STAR_LEVEL'] > 0.90)
    ]
    
    # Get misses
    misses = df[df['PLAYER_NAME'].isin([c[0] for c in CASES_TO_INVESTIGATE])]
    
    print(f"\nSuccessful Cases (n={len(successful)}):")
    for col in ['CREATION_VOLUME_RATIO', 'CREATION_TAX', 'LEVERAGE_USG_DELTA', 
                'LEVERAGE_TS_DELTA', 'RS_RIM_APPETITE']:
        if col in successful.columns:
            mean_val = successful[col].mean()
            print(f"  {col}: {mean_val:.4f}")
    
    print(f"\nMisses (n={len(misses)}):")
    for col in ['CREATION_VOLUME_RATIO', 'CREATION_TAX', 'LEVERAGE_USG_DELTA', 
                'LEVERAGE_TS_DELTA', 'RS_RIM_APPETITE']:
        if col in misses.columns:
            mean_val = misses[col].mean()
            print(f"  {col}: {mean_val:.4f}")

def main():
    """Run the analysis."""
    print("="*80)
    print("MODEL MISSES ANALYSIS")
    print("="*80)
    
    # Load data
    df = load_data()
    print(f"\nLoaded {len(df)} player-seasons")
    
    # Analyze each case
    cases_data = []
    for player_name, season, rank in CASES_TO_INVESTIGATE:
        try:
            case = analyze_case(df, player_name, season, rank)
            cases_data.append(case)
        except Exception as e:
            print(f"\n❌ Error analyzing {player_name} {season}: {e}")
            continue
    
    # Compare to successful cases
    compare_to_successful_cases(df)
    
    # Summary patterns
    print(f"\n{'='*80}")
    print("SUMMARY PATTERNS")
    print(f"{'='*80}")
    
    if cases_data:
        df_cases = pd.DataFrame(cases_data)
        
        print(f"\nCommon Patterns in Misses:")
        
        # High creation volume?
        high_creation = df_cases['CREATION_VOLUME_RATIO'].apply(lambda x: x > 0.60 if pd.notna(x) else False).sum()
        print(f"  - High Creation Volume (>0.60): {high_creation}/{len(df_cases)} ({high_creation/len(df_cases)*100:.1f}%)")
        
        # Negative creation tax?
        neg_tax = df_cases['CREATION_TAX'].apply(lambda x: x < -0.10 if pd.notna(x) else False).sum()
        print(f"  - Negative Creation Tax (<-0.10): {neg_tax}/{len(df_cases)} ({neg_tax/len(df_cases)*100:.1f}%)")
        
        # Low rim pressure?
        low_rim = df_cases['RS_RIM_APPETITE'].apply(lambda x: x < 0.20 if pd.notna(x) else False).sum()
        print(f"  - Low Rim Pressure (<0.20): {low_rim}/{len(df_cases)} ({low_rim/len(df_cases)*100:.1f}%)")
        
        # Positive leverage?
        pos_leverage = df_cases['LEVERAGE_USG_DELTA'].apply(lambda x: x > 0.05 if pd.notna(x) else False).sum()
        print(f"  - Positive Leverage USG (>0.05): {pos_leverage}/{len(df_cases)} ({pos_leverage/len(df_cases)*100:.1f}%)")
    
    print(f"\n{'='*80}")
    print("Analysis complete!")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()

