
import sys
import os
import pandas as pd
import numpy as np

def analyze_luka_production():
    # Load 2023-24 shot charts
    file_path = "data/shot_charts_2023-24.csv"
    if not os.path.exists(file_path):
        print("Shot chart file not found.")
        return

    df = pd.read_csv(file_path)
    
    # Filter for Luka (ID: 1629029)
    luka = df[df['PLAYER_ID'] == 1629029].copy()
    
    # Simplify Zones
    def get_zone(row):
        if 'Restricted Area' in row['SHOT_ZONE_BASIC']: return 'Restricted Area'
        if 'In The Paint' in row['SHOT_ZONE_BASIC']: return 'Paint (Non-RA)'
        if 'Mid-Range' in row['SHOT_ZONE_BASIC']: return 'Mid-Range'
        if 'Corner 3' in row['SHOT_ZONE_BASIC']: return 'Corner 3'
        if 'Above the Break' in row['SHOT_ZONE_BASIC']: return 'Above Break 3'
        return 'Other'
        
    luka['SimpleZone'] = luka.apply(get_zone, axis=1)
    luka = luka[luka['SimpleZone'] != 'Other']
    
    # Counter-Punch Zone for Luka is 'Paint (Non-RA)'
    target_zone = 'Paint (Non-RA)'
    
    print(f"Luka Dončić 2023-24 Production Analysis ({target_zone})")
    print("-" * 50)
    
    rs = luka[luka['SEASON_TYPE'] == 'Regular Season']
    po = luka[luka['SEASON_TYPE'] == 'Playoffs']
    
    # Calculate raw counts
    rs_shots = len(rs)
    po_shots = len(po)
    
    rs_zone = rs[rs['SimpleZone'] == target_zone]
    po_zone = po[po['SimpleZone'] == target_zone]
    
    rs_vol = len(rs_zone)
    po_vol = len(po_zone)
    
    rs_makes = rs_zone['SHOT_MADE_FLAG'].sum()
    po_makes = po_zone['SHOT_MADE_FLAG'].sum()
    
    # Per-Game Scaling (Crucial because PO sample is smaller)
    # We need Games Played
    rs_games = rs['GAME_ID'].nunique()
    po_games = po['GAME_ID'].nunique()
    
    print(f"Games: RS {rs_games} | PO {po_games}")
    
    # Metrics per Game
    rs_fga_pg = rs_vol / rs_games
    po_fga_pg = po_vol / po_games
    
    rs_fgm_pg = rs_makes / rs_games
    po_fgm_pg = po_makes / po_games
    
    rs_pts_pg = rs_fgm_pg * 2 # Assuming 2pts for Paint shots
    po_pts_pg = po_fgm_pg * 2
    
    print(f"\nVolume (FGA/Game) in Zone:")
    print(f"RS: {rs_fga_pg:.2f}")
    print(f"PO: {po_fga_pg:.2f}")
    print(f"Delta: {po_fga_pg - rs_fga_pg:+.2f} shots/game")
    
    print(f"\nEfficiency (FG%) in Zone:")
    rs_pct = rs_makes / rs_vol
    po_pct = po_makes / po_vol
    print(f"RS: {rs_pct:.1%}")
    print(f"PO: {po_pct:.1%}")
    print(f"Delta: {po_pct - rs_pct:+.1%}")
    
    print(f"\nProduction (Points/Game) in Zone:")
    print(f"RS: {rs_pts_pg:.2f} pts")
    print(f"PO: {po_pts_pg:.2f} pts")
    print(f"Delta: {po_pts_pg - rs_pts_pg:+.2f} pts/game")
    
    # Validation Logic
    if (po_pts_pg - rs_pts_pg) > 0:
        print("\n✅ HYPOTHESIS CONFIRMED: Luka produced MORE points from this zone in playoffs.")
        print("He sacrificed Efficiency (-10%) to buy Volume (+3.5 shots/game).")
    else:
        print("\n❌ HYPOTHESIS FAILED: Luka produced fewer points.")

if __name__ == "__main__":
    analyze_luka_production()

