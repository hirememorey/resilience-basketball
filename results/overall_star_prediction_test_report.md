# Overall Star Prediction: Franchise Cornerstone Classification Test Report

**Date**: 2025-12-13 21:51:03

## Executive Summary

**Primary Focus**: Testing the model's ability to correctly identify Franchise Cornerstones at current usage levels.

**Framework**: 2D Risk Matrix - Franchise Cornerstones require High Performance (≥70%) + Low Dependence (<30%).

- **Total Test Cases**: 20
- **Data Found**: 19
- **Correct Classifications**: 17
- **Incorrect Classifications**: 2
- **Accuracy**: 89.5%

## Results by Category

### Confirmed Franchise Cornerstone
- **Total**: 10
- **Correct**: 8
- **Incorrect**: 2
- **Accuracy**: 80.0%

### Borderline Franchise Cornerstone
- **Total**: 2
- **Correct**: 2
- **Incorrect**: 0
- **Accuracy**: 100.0%

### Not Franchise Cornerstone
- **Total**: 4
- **Correct**: 4
- **Incorrect**: 0
- **Accuracy**: 100.0%

### Role Player
- **Total**: 2
- **Correct**: 2
- **Incorrect**: 0
- **Accuracy**: 100.0%

### Emerging Franchise Cornerstone
- **Total**: 1
- **Correct**: 1
- **Incorrect**: 0
- **Accuracy**: 100.0%

## Detailed Results

| Test | Player | Season | Category | Expected FC | Predicted FC | Performance | Dependence | Risk Category | Correct |
|------|--------|--------|----------|-------------|---------------|-------------|------------|---------------|---------|
| 1 | Nikola Jokić | 2023-24 | Confirmed Franchise Cornerstone | Yes | Yes | 80.51% | 29.32% | Franchise Cornerstone | ✅ Correct |
| 2 | Luka Dončić | 2023-24 | Confirmed Franchise Cornerstone | Yes | Yes | 98.62% | 39.66% | Franchise Cornerstone | ✅ Correct |
| 3 | Giannis Antetokounmpo | 2023-24 | Confirmed Franchise Cornerstone | Yes | Yes | 98.50% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 4 | Joel Embiid | 2023-24 | Confirmed Franchise Cornerstone | Yes | No | 98.45% | 71.09% | Luxury Component | ❌ Incorrect |
| 5 | Shai Gilgeous-Alexander | 2023-24 | Borderline Franchise Cornerstone | Yes | Yes | 99.18% | 16.94% | Franchise Cornerstone | ✅ Correct |
| 6 | Tyrese Maxey | 2023-24 | Borderline Franchise Cornerstone | Yes | Yes | 82.08% | 40.45% | Franchise Cornerstone | ✅ Correct |
| 7 | Jordan Poole | 2023-24 | Not Franchise Cornerstone | No | No | 17.00% | 57.57% | Avoid | ✅ Correct |
| 8 | Domantas Sabonis | 2023-24 | Not Franchise Cornerstone | No | No | 13.39% | 12.92% | Depth | ✅ Correct |
| 9 | Julius Randle | 2023-24 | Not Franchise Cornerstone | No | No | 88.78% | 68.06% | Luxury Component | ✅ Correct |
| 10 | Aaron Gordon | 2023-24 | Role Player - Depth | No | No | 3.46% | 14.69% | Depth | ✅ Correct |
| 11 | Brook Lopez | 2023-24 | Role Player - Depth | No | No | 0.36% | 74.74% | Avoid | ✅ Correct |
| 12 | Chris Paul | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 69.87% | 50.94% | Luxury Component | ❌ Incorrect |
| 13 | Jimmy Butler III | 2015-16 | Confirmed Franchise Cornerstone | Yes | Yes | 74.97% | 10.57% | Franchise Cornerstone | ✅ Correct |
| 14 | James Harden | 2015-16 | Confirmed Franchise Cornerstone | Yes | Yes | 99.27% | 11.80% | Franchise Cornerstone | ✅ Correct |
| 15 | Eric Bledsoe | 2015-16 | Not Franchise Cornerstone | No | No | 92.62% | 65.29% | Luxury Component | ✅ Correct |
| 16 | Giannis Antetokounmpo | 2024-25 | Confirmed Franchise Cornerstone | Yes | Yes | 99.12% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 17 | Donovan Mitchell | 2024-25 | Confirmed Franchise Cornerstone | Yes | Yes | 96.84% | 48.08% | Luxury Component | ✅ Correct |
| 18 | LeBron James | 2024-25 | Confirmed Franchise Cornerstone | Yes | Yes | 94.84% | 38.45% | Franchise Cornerstone | ✅ Correct |
| 19 | Cade Cunningham | 2024-25 | Emerging Franchise Cornerstone | Yes | Yes | 99.12% | 44.44% | Franchise Cornerstone | ✅ Correct |
| 20 | Kevin Porter Jr | 2024-25 | Not Franchise Cornerstone | No | N/A | N/A | N/A | N/A | ❌ No Data |

## Diagnostic Data

Comprehensive diagnostic data has been saved to: `results/overall_star_prediction_diagnostics.csv`

This CSV contains all raw statistics, feature calculations, and predictions from `player_season_analyzer.py` for each test case, enabling detailed analysis of model mistakes.

## Key Metrics for Analysis

**Franchise Cornerstone Criteria**:
- Performance Score ≥ 70%
- Dependence Score < 30%
- Risk Category = 'Franchise Cornerstone'

**Common Issues to Investigate**:
- False Negatives: Elite players not classified as Franchise Cornerstones
- False Positives: Non-elite players incorrectly classified as Franchise Cornerstones
- Performance vs. Dependence miscalibration

## Incorrect Classifications Analysis

### Joel Embiid (2023-24)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 98.45%
- **Dependence**: 71.09%
- **Risk Category**: Luxury Component
- **Notes**: Dependence too high (71.09% >= 30%); False Negative: Should be Franchise Cornerstone

### Chris Paul (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 69.87%
- **Dependence**: 50.94%
- **Risk Category**: Luxury Component
- **Notes**: Performance too low (69.87% < 70%); Dependence too high (50.94% >= 30%); False Negative: Should be Franchise Cornerstone

## Missing Data

- **Kevin Porter Jr (2024-25)**: No data found in dataset

