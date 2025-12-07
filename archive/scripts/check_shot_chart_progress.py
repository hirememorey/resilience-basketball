#!/usr/bin/env python3
"""
Quick script to check progress of shot chart collection.
"""
import pandas as pd
from pathlib import Path

print("="*80)
print("SHOT CHART COLLECTION PROGRESS")
print("="*80)
print()

# Check existing shot chart files
shot_files = list(Path('data').glob('shot_charts_*.csv'))
seasons = sorted([f.stem.replace('shot_charts_', '') for f in shot_files])

if not seasons:
    print("❌ No shot chart files found yet")
    print("   Collection may still be in progress...")
else:
    print(f"✅ Found {len(seasons)} seasons with shot chart data:")
    print()
    
    total_players = 0
    total_shots = 0
    
    for season in seasons:
        file_path = Path(f'data/shot_charts_{season}.csv')
        if file_path.exists():
            df = pd.read_csv(file_path, low_memory=False)
            players = df['PLAYER_ID'].nunique() if 'PLAYER_ID' in df.columns else 0
            shots = len(df)
            total_players += players
            total_shots += shots
            
            # Check if it has both RS and PO
            rs_shots = 0
            po_shots = 0
            if 'SEASON_TYPE' in df.columns:
                rs_shots = (df['SEASON_TYPE'] == 'Regular Season').sum()
                po_shots = (df['SEASON_TYPE'] == 'Playoffs').sum()
            
            print(f"  {season}:")
            print(f"    Players: {players}")
            print(f"    Shots: {shots:,} (RS: {rs_shots:,}, PO: {po_shots:,})")
    
    print()
    print(f"Total: {total_players} unique players, {total_shots:,} total shots")
    print()
    
    # Compare with expected
    pred = pd.read_csv('results/predictive_dataset.csv')
    expected_seasons = sorted(pred['SEASON'].unique().tolist())
    
    print("Expected seasons:", len(expected_seasons))
    print("Collected seasons:", len(seasons))
    
    missing = set(expected_seasons) - set(seasons)
    if missing:
        print(f"⚠️  Missing seasons: {sorted(missing)}")
    else:
        print("✅ All seasons collected!")

print()
print("="*80)
print("To check live progress, run: tail -f logs/shot_chart_collection.log")
print("="*80)


