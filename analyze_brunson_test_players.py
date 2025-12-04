"""
First Principles Analysis: Why Did the System Pick These 6 Players?

This script analyzes the stress vector profiles of the 6 players identified
in the Brunson Test to understand:
1. What they have in common (why they were all flagged)
2. What distinguishes the breakouts (Brunson, Haliburton) from non-breakouts
3. What patterns we can use to refine the detection criteria
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Load data
results_dir = Path("results")
data_dir = Path("data")

print("=" * 80)
print("First Principles Analysis: Brunson Test Players (2020-21)")
print("=" * 80)

# Load stress vectors
df_features = pd.read_csv(results_dir / "predictive_dataset.csv")
df_pressure = pd.read_csv(results_dir / "pressure_features.csv")

# Merge
df = df_features.merge(
    df_pressure,
    on=['PLAYER_ID', 'SEASON'],
    how='left',
    suffixes=('', '_p')
)

# Load usage data
rs_files = list(data_dir.glob("regular_season_*.csv"))
rs_data = []
for f in rs_files:
    try:
        df_rs = pd.read_csv(f)
        season = f.stem.replace("regular_season_", "")
        df_rs['SEASON'] = season
        if 'PLAYER_ID' in df_rs.columns and 'USG_PCT' in df_rs.columns:
            # Handle multiple teams - take max usage
            df_rs_grouped = df_rs.groupby('PLAYER_ID').agg({
                'USG_PCT': 'max',
                'PLAYER_NAME': 'first'
            }).reset_index()
            df_rs_grouped['SEASON'] = season
            rs_data.append(df_rs_grouped[['PLAYER_ID', 'SEASON', 'USG_PCT', 'PLAYER_NAME']])
    except Exception as e:
        pass

if rs_data:
    df_usage = pd.concat(rs_data, ignore_index=True)
    df = df.merge(df_usage, on=['PLAYER_ID', 'SEASON'], how='left', suffixes=('', '_u'))

# Filter for our 6 players in 2020-21
players_2021 = {
    1628973: 'Jalen Brunson',
    204456: 'T.J. McConnell',
    1628407: 'Dwayne Bacon',
    202709: 'Cory Joseph',
    1630169: 'Tyrese Haliburton',
    1626153: 'Delon Wright'
}

df_2021 = df[(df['SEASON'] == '2020-21') & (df['PLAYER_ID'].isin(players_2021.keys()))].copy()

# Map player IDs to names for clarity
player_map = {pid: name for pid, name in players_2021.items()}
df_2021['PLAYER_NAME'] = df_2021['PLAYER_ID'].map(player_map)

# Classify as breakout vs non-breakout
breakouts = [1628973, 1630169]  # Brunson, Haliburton
df_2021['BREAKOUT'] = df_2021['PLAYER_ID'].isin(breakouts)

# Key stress vector features to analyze
key_features = {
    'Usage': 'USG_PCT',
    'Creation Volume Ratio': 'CREATION_VOLUME_RATIO',
    'Creation Tax': 'CREATION_TAX',
    'Pressure Resilience': 'RS_PRESSURE_RESILIENCE',
    'Pressure Appetite': 'RS_PRESSURE_APPETITE',
    'Late Clock Resilience': 'RS_LATE_CLOCK_PRESSURE_RESILIENCE',
    'Late Clock Appetite': 'RS_LATE_CLOCK_PRESSURE_APPETITE',
    'Isolation EFG': 'EFG_ISO_WEIGHTED',
    'Leverage USG Delta': 'LEVERAGE_USG_DELTA',
    'Leverage TS Delta': 'LEVERAGE_TS_DELTA',
    'Clutch Minutes': 'CLUTCH_MIN_TOTAL',
    'Free Throw Rate': 'RS_FTr',
}

# Filter to available features
available_features = {k: v for k, v in key_features.items() if v in df_2021.columns}

print("\n" + "=" * 80)
print("STRESS VECTOR PROFILES")
print("=" * 80)

# Display profiles
display_cols = ['PLAYER_NAME', 'BREAKOUT'] + list(available_features.values())
df_display = df_2021[display_cols].copy()

# Rename columns for display
df_display = df_display.rename(columns={v: k for k, v in available_features.items()})
df_display = df_display.rename(columns={'PLAYER_NAME': 'Player', 'BREAKOUT': 'Broke Out'})

# Sort: breakouts first, then by creation volume ratio
df_display = df_display.sort_values(['Broke Out', 'Creation Volume Ratio'], ascending=[False, False])

print("\n" + df_display.to_string(index=False))

# Statistical comparison
print("\n" + "=" * 80)
print("STATISTICAL COMPARISON: BREAKOUTS vs NON-BREAKOUTS")
print("=" * 80)

df_breakouts = df_2021[df_2021['BREAKOUT'] == True]
df_non_breakouts = df_2021[df_2021['BREAKOUT'] == False]

print(f"\nBreakouts (n={len(df_breakouts)}): {', '.join(df_breakouts['PLAYER_NAME'].values)}")
print(f"Non-Breakouts (n={len(df_non_breakouts)}): {', '.join(df_non_breakouts['PLAYER_NAME'].values)}")

print("\nMean Values by Group:")
print("-" * 80)

comparison_data = []
for feature_name, feature_col in available_features.items():
    if feature_col in df_2021.columns:
        breakout_mean = df_breakouts[feature_col].mean() if len(df_breakouts) > 0 else np.nan
        non_breakout_mean = df_non_breakouts[feature_col].mean() if len(df_non_breakouts) > 0 else np.nan
        diff = breakout_mean - non_breakout_mean
        
        comparison_data.append({
            'Feature': feature_name,
            'Breakouts': breakout_mean,
            'Non-Breakouts': non_breakout_mean,
            'Difference': diff
        })

df_comparison = pd.DataFrame(comparison_data)
df_comparison = df_comparison.sort_values('Difference', key=abs, ascending=False)
print(df_comparison.to_string(index=False))

# First principles insights
print("\n" + "=" * 80)
print("FIRST PRINCIPLES INSIGHTS")
print("=" * 80)

print("\n1. WHAT THEY HAVE IN COMMON (Why all 6 were flagged):")
print("-" * 80)
print("   All 6 players share:")
print("   - Low usage (<20% USG) - filtered first")
print("   - High stress profile scores (≥80th percentile)")
print("   - High creation volume ratio (top 30%)")
print("   - High pressure resilience (top 30%)")

print("\n2. WHAT DISTINGUISHES BREAKOUTS FROM NON-BREAKOUTS:")
print("-" * 80)

# Check each feature for meaningful differences
for feature_name, feature_col in available_features.items():
    if feature_col in df_2021.columns:
        breakout_vals = df_breakouts[feature_col].dropna()
        non_breakout_vals = df_non_breakouts[feature_col].dropna()
        
        if len(breakout_vals) > 0 and len(non_breakout_vals) > 0:
            breakout_mean = breakout_vals.mean()
            non_breakout_mean = non_breakout_vals.mean()
            diff_pct = ((breakout_mean - non_breakout_mean) / abs(non_breakout_mean) * 100) if non_breakout_mean != 0 else 0
            
            # Flag significant differences (>20% relative difference)
            if abs(diff_pct) > 20:
                direction = "higher" if diff_pct > 0 else "lower"
                print(f"   - {feature_name}: Breakouts have {abs(diff_pct):.1f}% {direction} values")
                print(f"     (Breakouts: {breakout_mean:.3f}, Non-Breakouts: {non_breakout_mean:.3f})")

print("\n3. KEY HYPOTHESES TO TEST:")
print("-" * 80)
print("   Based on first principles, breakouts might differ in:")
print("   - Age/Experience: Younger players more likely to break out")
print("   - Team Context: Players on teams with star usage might be capped")
print("   - Creation Efficiency: Not just volume, but efficiency on created shots")
print("   - Clutch Volume: More clutch minutes = more proven in high-leverage")
print("   - Late-Clock Ability: The 'Grenade Vector' - bailout ability")

print("\n" + "=" * 80)
print("INDIVIDUAL PLAYER ANALYSIS")
print("=" * 80)

for _, row in df_2021.iterrows():
    player = row['PLAYER_NAME']
    is_breakout = row['BREAKOUT']
    status = "✅ BROKEOUT" if is_breakout else "❌ NO BREAKOUT"
    
    print(f"\n{player} ({status}):")
    print(f"  USG%: {row.get('USG_PCT', 0):.1f}%")
    print(f"  Creation Volume Ratio: {row.get('CREATION_VOLUME_RATIO', 0):.3f}")
    print(f"  Pressure Resilience: {row.get('RS_PRESSURE_RESILIENCE', 0):.3f}")
    print(f"  Late Clock Resilience: {row.get('RS_LATE_CLOCK_PRESSURE_RESILIENCE', 0):.3f}")
    print(f"  Isolation EFG: {row.get('EFG_ISO_WEIGHTED', 0):.3f}")
    print(f"  Clutch Minutes: {row.get('CLUTCH_MIN_TOTAL', 0):.1f}")

print("\n" + "=" * 80)


