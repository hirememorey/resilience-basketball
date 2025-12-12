import pandas as pd
import numpy as np
from pathlib import Path

def audit_false_positives():
    print("Starting Diagnostic Audit of False Positive Cases...")
    
    # Define target cases
    targets = [
        {'name': "D'Angelo Russell", 'season': '2018-19'},
        {'name': "Jordan Poole", 'season': '2021-22'},
        {'name': "Julius Randle", 'season': '2020-21'},
        {'name': "Christian Wood", 'season': '2020-21'},
        {'name': "Karl-Anthony Towns", 'season': '2021-22'},
        {'name': "Elfrid Payton", 'season': '2018-19'},
        {'name': "Kris Dunn", 'season': '2017-18'},
        # Add a True Positive for reference
        {'name': "Jalen Brunson", 'season': '2020-21'} 
    ]
    
    # Load Data
    results_dir = Path("results")
    predictive_path = results_dir / "predictive_dataset_clean.csv"
    gate_path = results_dir / "gate_features.csv"
    
    if not predictive_path.exists():
        print(f"Error: {predictive_path} not found.")
        return

    df_pred = pd.read_csv(predictive_path)
    
    if gate_path.exists():
        df_gate = pd.read_csv(gate_path)
        # Merge, avoiding duplicate columns
        cols_to_use = df_gate.columns.difference(df_pred.columns).tolist()
        cols_to_use.extend(['PLAYER_NAME', 'SEASON'])
        df = pd.merge(df_pred, df_gate[cols_to_use], on=['PLAYER_NAME', 'SEASON'], how='left')
    else:
        print("Warning: gate_features.csv not found. Using only predictive dataset.")
        df = df_pred

    # Normalize columns if needed
    if 'USG_PCT' in df.columns and df['USG_PCT'].max() > 1.0:
        df['USG_PCT'] = df['USG_PCT'] / 100.0

    # Define columns to audit
    audit_cols = [
        'PLAYER_NAME', 'SEASON',
        # Low Floor
        'EFG_ISO_WEIGHTED', 'CREATION_TAX', 'QUALITY_ADJUSTED_RESILIENCE',
        # Flaws
        'RS_RIM_APPETITE', 'RIM_PRESSURE_DEFICIT', 'SYSTEM_DEPENDENCE_SCORE',
        # Stat Stuffer
        'USG_PCT', 'CREATION_VOLUME_RATIO', 'INEFFICIENT_VOLUME_SCORE', 
        # Context
        'LEVERAGE_USG_DELTA', 'LEVERAGE_TS_DELTA'
    ]
    
    # Check which columns exist
    existing_cols = [c for c in audit_cols if c in df.columns]
    
    # Filter for targets
    audit_data = []
    for target in targets:
        row = df[(df['PLAYER_NAME'] == target['name']) & (df['SEASON'] == target['season'])]
        if not row.empty:
            audit_data.append(row[existing_cols].iloc[0])
        else:
            print(f"Warning: {target['name']} ({target['season']}) not found in dataset.")

    if not audit_data:
        print("No target players found.")
        return

    audit_df = pd.DataFrame(audit_data)
    
    # Print formatted output
    print("\n=== AUDIT RESULTS ===")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    # Section 1: Low Floor Audit
    print("\n--- 1. Low Floor Audit (Threshold: EFG < 0.45) ---")
    cols = ['PLAYER_NAME', 'SEASON', 'EFG_ISO_WEIGHTED', 'CREATION_TAX', 'QUALITY_ADJUSTED_RESILIENCE']
    print(audit_df[[c for c in cols if c in audit_df.columns]].to_string(index=False))

    # Section 2: Flaw Scaling Audit
    print("\n--- 2. Flaw Scaling Audit (Threshold: Rim < 0.20) ---")
    cols = ['PLAYER_NAME', 'SEASON', 'USG_PCT', 'RS_RIM_APPETITE', 'RIM_PRESSURE_DEFICIT', 'SYSTEM_DEPENDENCE_SCORE']
    print(audit_df[[c for c in cols if c in audit_df.columns]].to_string(index=False))

    # Section 3: Stat Stuffer Audit
    print("\n--- 3. Stat Stuffer Audit (High Inefficiency) ---")
    cols = ['PLAYER_NAME', 'SEASON', 'USG_PCT', 'CREATION_VOLUME_RATIO', 'INEFFICIENT_VOLUME_SCORE']
    print(audit_df[[c for c in cols if c in audit_df.columns]].to_string(index=False))
    
    # Calculate Percentiles for Context
    print("\n=== DATASET PERCENTILES ===")
    
    if 'EFG_ISO_WEIGHTED' in df.columns:
        p25_efg = df['EFG_ISO_WEIGHTED'].quantile(0.25)
        print(f"EFG_ISO_WEIGHTED 25th Percentile: {p25_efg:.4f}")
    
    if 'RS_RIM_APPETITE' in df.columns:
        p20_rim = df['RS_RIM_APPETITE'].quantile(0.20)
        print(f"RS_RIM_APPETITE 20th Percentile: {p20_rim:.4f}")
        
    if 'INEFFICIENT_VOLUME_SCORE' in df.columns:
        p75_ineff = df['INEFFICIENT_VOLUME_SCORE'].quantile(0.75)
        p90_ineff = df['INEFFICIENT_VOLUME_SCORE'].quantile(0.90)
        print(f"INEFFICIENT_VOLUME_SCORE 75th Percentile: {p75_ineff:.4f}")
        print(f"INEFFICIENT_VOLUME_SCORE 90th Percentile: {p90_ineff:.4f}")

if __name__ == "__main__":
    audit_false_positives()
