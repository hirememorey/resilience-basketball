# SHOT_QUALITY_GENERATION_DELTA Gate Validation Report

**Date**: 2025-12-09 09:45:10

## Executive Summary

This report validates the proposed SHOT_QUALITY_GENERATION_DELTA gate against all test cases.

## Step 1: Metric Status

- **Exists in dataset**: True
- **Coverage**: 5312 (100.0%)
- **Exists in model**: False

## Step 2: Statistical Comparison

| Category | Count | Mean | Median | Std | Min | Max | Missing |
|----------|-------|------|--------|-----|-----|-----|----------|
| True Positive | 9 | 0.0293 | 0.0496 | 0.0761 | -0.0713 | 0.1319 | 0 |
| False Positive | 5 | -0.0096 | -0.0333 | 0.0576 | -0.0718 | 0.0762 | 0 |
| True Negative | 17 | -0.0142 | -0.0162 | 0.0837 | -0.1574 | 0.1280 | 0 |

## Step 3: Proposed Threshold Validation (-0.02)

**Proposed Threshold**: -0.02

**True Positives**:
- Total: 9
- Below threshold: 4 (44.4%)
- **False Negative Rate**: 44.44%

**False Positives**:
- Total: 5
- Below threshold: 3 (60.0%)
- **FP Catch Rate**: 60.00%

⚠️ **WARNING**: Proposed threshold would break more than 20% of true positives!

## Step 4: Optimal Threshold

**Optimal Threshold**: -0.0674
- **False Negative Rate**: 11.11%
- **FP Catch Rate**: 20.00%

## Step 5: Position Dependency Check

**Position Dependent**: False
**Reason**: Correlation with rim pressure: -0.107

## Recommendations

1. **Proposed threshold breaks too many true positives** - Do not implement gate with -0.02 threshold
2. **Consider using optimal threshold** (-0.0674) instead
