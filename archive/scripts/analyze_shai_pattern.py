#!/usr/bin/env python3
"""
Simple Analysis: How many "Shai-like" cases exist?

Shai's Pattern:
- High regular season TS% (0.637 - elite)
- "Declined" in playoffs (0.574 - still good, but lower)
- Marked as "Fragile" (composite 0.923)
- But clearly a great playoff performer (won championship)

Question: Is Shai an exception or a pattern?

We'll look for players with:
1. High regular season TS% (≥0.60 - elite level)
2. TS% declined in playoffs (ratio <0.95)
3. But playoff TS% still good (≥0.55)
4. Marked as "Fragile" by composite
5. But likely good playoff performers
"""

import pandas as pd

def analyze_shai_pattern():
    # Load 2024-25 data
    df = pd.read_csv('data/composite_resilience_2024_25.csv')
    
    print("=" * 70)
    print("SHAI PATTERN ANALYSIS")
    print("=" * 70)
    print("\nShai's Pattern:")
    print("- Regular Season TS%: 0.637 (elite)")
    print("- Playoff TS%: 0.574 (good, but declined)")
    print("- TS% Ratio: 0.901 (fragile)")
    print("- Production Ratio: 0.944 (fragile)")
    print("- Composite: 0.923 (fragile)")
    print("- Reality: Won championship (clearly great playoff performer)")
    print()
    
    # Define "Shai-like" pattern
    # 1. High regular season TS% (≥0.60 - elite)
    # 2. TS% declined (ratio <0.95)
    # 3. But playoff TS% still good (≥0.55)
    # 4. Marked as fragile (composite <0.95)
    
    shai_like = df[
        (df['rs_ts_pct'] >= 0.60) &  # Elite regular season TS%
        (df['ts_resilience_ratio'] < 0.95) &  # TS% declined
        (df['po_ts_pct'] >= 0.55) &  # But playoff TS% still good
        (df['composite_resilience'] < 0.95)  # Marked as fragile
    ].copy()
    
    print(f"Players with 'Shai-like' pattern: {len(shai_like)}")
    print(f"Total qualified players: {len(df)}")
    print(f"Percentage: {len(shai_like)/len(df)*100:.1f}%")
    print()
    
    if len(shai_like) > 0:
        print("=" * 70)
        print("SHAI-LIKE PLAYERS (High RS TS%, Declined but Still Good)")
        print("=" * 70)
        print()
        
        # Sort by regular season TS% (highest first)
        shai_like = shai_like.sort_values('rs_ts_pct', ascending=False)
        
        for idx, (_, row) in enumerate(shai_like.iterrows(), 1):
            print(f"{idx:2d}. {row['player_name']:30s} | "
                  f"RS TS%: {row['rs_ts_pct']:.3f} → "
                  f"PO TS%: {row['po_ts_pct']:.3f} | "
                  f"TS% Ratio: {row['ts_resilience_ratio']:.3f} | "
                  f"Composite: {row['composite_resilience']:.3f} | "
                  f"Category: {row['composite_category']}")
        
        print()
        print("=" * 70)
        print("ANALYSIS")
        print("=" * 70)
        print()
        
        # Calculate averages
        avg_rs_ts = shai_like['rs_ts_pct'].mean()
        avg_po_ts = shai_like['po_ts_pct'].mean()
        avg_ts_ratio = shai_like['ts_resilience_ratio'].mean()
        avg_composite = shai_like['composite_resilience'].mean()
        
        print(f"Average Regular Season TS%: {avg_rs_ts:.3f}")
        print(f"Average Playoff TS%: {avg_po_ts:.3f}")
        print(f"Average TS% Ratio: {avg_ts_ratio:.3f}")
        print(f"Average Composite: {avg_composite:.3f}")
        print()
        
        # Compare to Shai
        shai_data = df[df['player_name'] == 'Shai Gilgeous-Alexander'].iloc[0]
        print("Shai's Numbers:")
        print(f"  Regular Season TS%: {shai_data['rs_ts_pct']:.3f}")
        print(f"  Playoff TS%: {shai_data['po_ts_pct']:.3f}")
        print(f"  TS% Ratio: {shai_data['ts_resilience_ratio']:.3f}")
        print(f"  Composite: {shai_data['composite_resilience']:.3f}")
        print()
        
        # Check if pattern is common
        if len(shai_like) >= 5:
            print("✅ PATTERN: Shai is NOT an exception - this pattern is COMMON")
            print(f"   {len(shai_like)} players show the same pattern")
            print("   The metric systematically penalizes elite regular season performers")
        elif len(shai_like) >= 2:
            print("⚠️  PATTERN: Shai is RARE but not unique")
            print(f"   {len(shai_like)} players show the same pattern")
            print("   May need adjustment for elite regular season performers")
        else:
            print("❌ EXCEPTION: Shai is unique")
            print("   Only 1 player shows this pattern")
            print("   May be a data issue or unique case")
    
    # Also check: How many elite regular season players are marked as fragile?
    print()
    print("=" * 70)
    print("BROADER PATTERN: Elite Regular Season Players")
    print("=" * 70)
    print()
    
    elite_rs = df[df['rs_ts_pct'] >= 0.60].copy()
    elite_fragile = elite_rs[elite_rs['composite_resilience'] < 0.95]
    
    print(f"Players with RS TS% ≥ 0.60: {len(elite_rs)}")
    print(f"  Marked as Fragile (composite <0.95): {len(elite_fragile)}")
    print(f"  Percentage: {len(elite_fragile)/len(elite_rs)*100:.1f}%")
    print()
    
    if len(elite_fragile) > 0:
        print("Elite Regular Season Players Marked as Fragile:")
        elite_fragile_sorted = elite_fragile.sort_values('rs_ts_pct', ascending=False)
        for idx, (_, row) in enumerate(elite_fragile_sorted.iterrows(), 1):
            print(f"{idx:2d}. {row['player_name']:30s} | "
                  f"RS TS%: {row['rs_ts_pct']:.3f} | "
                  f"PO TS%: {row['po_ts_pct']:.3f} | "
                  f"Composite: {row['composite_resilience']:.3f}")
    
    # Check: What about players with very high regular season TS%?
    print()
    print("=" * 70)
    print("VERY HIGH REGULAR SEASON TS% (≥0.63)")
    print("=" * 70)
    print()
    
    very_high_rs = df[df['rs_ts_pct'] >= 0.63].copy()
    very_high_fragile = very_high_rs[very_high_rs['composite_resilience'] < 0.95]
    
    print(f"Players with RS TS% ≥ 0.63: {len(very_high_rs)}")
    print(f"  Marked as Fragile: {len(very_high_fragile)}")
    print(f"  Percentage: {len(very_high_fragile)/len(very_high_rs)*100:.1f}%")
    print()
    
    if len(very_high_rs) > 0:
        for idx, (_, row) in enumerate(very_high_rs.sort_values('rs_ts_pct', ascending=False).iterrows(), 1):
            marker = " ⚠️" if row['composite_resilience'] < 0.95 else ""
            print(f"{idx:2d}. {row['player_name']:30s} | "
                  f"RS TS%: {row['rs_ts_pct']:.3f} | "
                  f"PO TS%: {row['po_ts_pct']:.3f} | "
                  f"Composite: {row['composite_resilience']:.3f}{marker}")

if __name__ == "__main__":
    analyze_shai_pattern()





