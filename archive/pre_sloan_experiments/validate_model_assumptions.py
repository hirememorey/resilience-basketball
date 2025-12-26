#!/usr/bin/env python3
"""
Validate Model Assumptions for Expanded Dataset

Checks for systematic biases and statistical validity in the resilience model.
"""

import pandas as pd
import numpy as np
from scipy import stats
import sys
from pathlib import Path

def load_results():
    """Load resilience scores."""
    return pd.read_csv('results/resilience_scores_all.csv')

def check_residual_normality(df):
    """Test if residuals are normally distributed."""
    residuals_ts = df['actual_ts_pct'] - df['expected_ts_pct']
    residuals_ppg = df['actual_ppg_per75'] - df['expected_ppg_per75']
    residuals_ast = df['actual_ast_pct'] - df['expected_ast_pct']

    # Shapiro-Wilk test
    stat_ts, p_ts = stats.shapiro(residuals_ts)
    stat_ppg, p_ppg = stats.shapiro(residuals_ppg)
    stat_ast, p_ast = stats.shapiro(residuals_ast)

    print("\n📊 Residual Normality Tests (Shapiro-Wilk)")
    print(f"  TS%: p-value = {p_ts:.4f} {'✅ Normal' if p_ts > 0.05 else '⚠️ Non-normal'}")
    print(f"  PPG: p-value = {p_ppg:.4f} {'✅ Normal' if p_ppg > 0.05 else '⚠️ Non-normal'}")
    print(f"  AST%: p-value = {p_ast:.4f} {'✅ Normal' if p_ast > 0.05 else '⚠️ Non-normal'}")

def check_systematic_bias(df):
    """Check for systematic biases by regular season TS% quartiles."""
    # Group by regular season TS% quartiles
    df['rs_ts_quartile'] = pd.qcut(df['rs_ts_pct'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])

    bias_check = df.groupby('rs_ts_quartile')['composite_resilience_score'].mean()

    print("\n🔍 Systematic Bias Check")
    print("  Average resilience score by regular season TS% quartile:")
    print(bias_check)

    # Ideally, scores should be near 0 for all quartiles
    if (bias_check.abs() < 0.3).all():
        print("  ✅ No systematic bias detected")
    else:
        print("  ⚠️ Potential bias - investigate further")

def check_season_distribution(df):
    """Check distribution of data across seasons."""
    season_counts = df['SEASON'].value_counts().sort_index()
    print("\n📅 Data Distribution by Season:")
    print(season_counts)
    print(f"  Total seasons: {len(season_counts)}")
    print(f"  Total samples: {len(df)}")

def main():
    df = load_results()
    print(f"Loaded {len(df)} resilience score records")
    print(f"Columns: {list(df.columns)}")

    check_season_distribution(df)
    # Note: Residual analysis requires expected vs actual columns which may not be in this simplified output

if __name__ == "__main__":
    main()
