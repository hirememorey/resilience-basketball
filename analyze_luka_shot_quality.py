
import sys
import os
import pandas as pd
import numpy as np

def analyze_luka_quality():
    # Load 2023-24 shot charts
    file_path = "data/shot_charts_2023-24.csv"
    if not os.path.exists(file_path):
        print("Shot chart file not found.")
        return

    df = pd.read_csv(file_path)
    
    # Filter for Luka (ID: 1629029)
    luka = df[df['PLAYER_ID'] == 1629029].copy()
    
    print(f"Luka Dončić 2023-24 Shot Analysis")
    print("-" * 30)
    
    # Group by Season Type
    # Note: The current shot_charts_2023-24.csv MIGHT NOT have shot quality columns (Close Def Dist)
    # The API client fetches `shotchartdetail` which DOES NOT include `CloseDefDistRange`.
    # We need to check the columns.
    print("Columns available:", luka.columns.tolist())
    
    # If shot quality is missing, we can't check it yet. 
    # The `shotchartdetail` endpoint gives X,Y, Zone, etc.
    # The `leaguedashplayerptshot` endpoint gives Shot Quality aggregates, but not per-shot.
    
    # Check if we can infer difficulty from Zone/Action Type?
    # Or just volume/efficiency for now to confirm the efficiency drop.
    
    stats = luka.groupby('SEASON_TYPE').agg({
        'SHOT_MADE_FLAG': ['count', 'mean'],
        'SHOT_DISTANCE': 'mean'
    })
    print(stats)
    
    # Check "Counter Punch" Zones (where volume increased)
    # 1. Calculate distributions
    def get_zone(row):
        if 'Restricted Area' in row['SHOT_ZONE_BASIC']: return 'Restricted Area'
        if 'In The Paint' in row['SHOT_ZONE_BASIC']: return 'Paint (Non-RA)'
        if 'Mid-Range' in row['SHOT_ZONE_BASIC']: return 'Mid-Range'
        if 'Corner 3' in row['SHOT_ZONE_BASIC']: return 'Corner 3'
        if 'Above the Break' in row['SHOT_ZONE_BASIC']: return 'Above Break 3'
        return 'Other'
        
    luka['SimpleZone'] = luka.apply(get_zone, axis=1)
    
    rs = luka[luka['SEASON_TYPE'] == 'Regular Season']
    po = luka[luka['SEASON_TYPE'] == 'Playoffs']
    
    rs_dist = rs['SimpleZone'].value_counts(normalize=True)
    po_dist = po['SimpleZone'].value_counts(normalize=True)
    
    print("\nZone Distribution Delta (Playoffs - RS):")
    delta = po_dist - rs_dist
    print(delta)
    
    # Identify zones with increased volume
    increased = delta[delta > 0].index.tolist()
    print(f"\nCounter-Punch Zones (Increased Volume): {increased}")
    
    # Check efficiency in those zones
    print("\nEfficiency in Counter-Punch Zones:")
    for zone in increased:
        rs_eff = rs[rs['SimpleZone'] == zone]['SHOT_MADE_FLAG'].mean()
        po_eff = po[po['SimpleZone'] == zone]['SHOT_MADE_FLAG'].mean()
        print(f"{zone}: RS {rs_eff:.3f} -> PO {po_eff:.3f} (Delta: {po_eff - rs_eff:.3f})")

if __name__ == "__main__":
    analyze_luka_quality()



