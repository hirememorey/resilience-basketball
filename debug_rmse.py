#!/usr/bin/env python3
"""
Debug script to understand why Z-scores are extreme
"""

import pandas as pd
import numpy as np

# Read the results
df = pd.read_csv('resilience_scores_all.csv')

print("=== Z-Score Analysis ===")
print(f"Z_EFF range: {df.Z_EFF.min():.2f} to {df.Z_EFF.max():.2f}")
print(f"Z_VOL range: {df.Z_VOL.min():.2f} to {df.Z_VOL.max():.2f}")
print(f"Z_CRE range: {df.Z_CRE.min():.2f} to {df.Z_CRE.max():.2f}")

# Calculate what RMSE would need to be to get these Z-scores
print("\n=== RMSE Reverse Engineering ===")
print("Z = (actual - expected) / RMSE")
print("So: RMSE = (actual - expected) / Z")

# Take a sample extreme case
extreme = df.iloc[0]  # First row with Z_EFF = -0.27
print(f"\nSample case: {extreme.PLAYER_NAME}")
print(f"RS_TS: {extreme.RS_TS:.3f}")
print(f"PO_TS: {extreme.PO_TS:.3f}")
print(f"EXP_TS: {extreme.EXP_TS:.3f}")
print(f"Z_EFF: {extreme.Z_EFF:.3f}")

# Calculate what RMSE would produce this Z-score
actual_minus_expected = extreme.PO_TS - extreme.EXP_TS
required_rmse = abs(actual_minus_expected / extreme.Z_EFF)
print(f"Required RMSE for Z={extreme.Z_EFF:.3f}: {required_rmse:.6f}")

print("\n=== Problem Diagnosis ===")
print("The RMSE values are too small (< 0.01), making Z-scores explode.")
print("This happens when models overfit - they fit training data perfectly")
print("but fail on new data, leading to tiny RMSE values.")

print("\n=== Solution ===")
print("1. Add regularization to prevent overfitting")
print("2. Use cross-validation to get realistic RMSE estimates")
print("3. Cap extreme Z-scores (e.g., at ±3.0)")
print("4. Investigate data quality issues (PO_TS = 0.0, 1.5)")
