# Overall Star Prediction: Franchise Cornerstone Classification Test Report

**Date**: 2025-12-14 23:02:35

## Executive Summary

**Primary Focus**: Testing the model's ability to correctly identify Franchise Cornerstones at current usage levels.

**Framework**: 2D Risk Matrix - Franchise Cornerstones require High Performance (≥70%) + Low Dependence (<30%).

- **Total Test Cases**: 35
- **Data Found**: 34
- **Correct Classifications**: 25
- **Incorrect Classifications**: 9
- **Accuracy**: 73.5%

## Results by Category

### Confirmed Franchise Cornerstone
- **Total**: 17
- **Correct**: 14
- **Incorrect**: 3
- **Accuracy**: 82.4%

### Borderline Franchise Cornerstone
- **Total**: 2
- **Correct**: 2
- **Incorrect**: 0
- **Accuracy**: 100.0%

### Not Franchise Cornerstone
- **Total**: 12
- **Correct**: 6
- **Incorrect**: 6
- **Accuracy**: 50.0%

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
| 1 | Nikola Jokić | 2023-24 | Confirmed Franchise Cornerstone | Yes | Yes | 91.47% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 2 | Luka Dončić | 2023-24 | Confirmed Franchise Cornerstone | Yes | Yes | 98.32% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 3 | Giannis Antetokounmpo | 2023-24 | Confirmed Franchise Cornerstone | Yes | Yes | 98.64% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 4 | Joel Embiid | 2023-24 | Confirmed Franchise Cornerstone | Yes | Yes | 98.07% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 5 | Joel Embiid | 2018-19 | Confirmed Franchise Cornerstone | Yes | No | 14.52% | 0.30% | Depth | ❌ Incorrect |
| 6 | Shai Gilgeous-Alexander | 2023-24 | Borderline Franchise Cornerstone | Yes | Yes | 99.02% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 7 | Tyrese Maxey | 2023-24 | Borderline Franchise Cornerstone | Yes | Yes | 75.72% | 11.97% | Franchise Cornerstone | ✅ Correct |
| 8 | Jordan Poole | 2023-24 | Not Franchise Cornerstone | No | No | 18.33% | 57.57% | Depth | ✅ Correct |
| 9 | Jordan Poole | 2021-22 | Not Franchise Cornerstone | No | Yes | 84.05% | 0.00% | Franchise Cornerstone | ❌ Incorrect |
| 10 | Domantas Sabonis | 2023-24 | Not Franchise Cornerstone | No | No | 14.06% | 0.00% | Depth | ✅ Correct |
| 11 | Julius Randle | 2023-24 | Not Franchise Cornerstone | No | Yes | 88.46% | 49.86% | Franchise Cornerstone | ❌ Incorrect |
| 12 | DeMar DeRozan | 2015-16 | Not Franchise Cornerstone | No | No | 46.18% | 15.75% | Depth | ✅ Correct |
| 13 | DeMar DeRozan | 2016-17 | Not Franchise Cornerstone | No | Yes | 99.50% | 2.21% | Franchise Cornerstone | ❌ Incorrect |
| 14 | Karl-Anthony Towns | 2021-22 | Not Franchise Cornerstone | No | Yes | 88.32% | 0.00% | Franchise Cornerstone | ❌ Incorrect |
| 15 | Karl-Anthony Towns | 2022-23 | Not Franchise Cornerstone | No | No | 51.53% | 61.93% | Depth | ✅ Correct |
| 16 | Karl-Anthony Towns | 2023-24 | Not Franchise Cornerstone | No | Yes | 94.01% | 0.00% | Franchise Cornerstone | ❌ Incorrect |
| 17 | Ben Simmons | 2018-19 | Not Franchise Cornerstone | No | No | 7.53% | 0.00% | Depth | ✅ Correct |
| 18 | Ben Simmons | 2020-21 | Not Franchise Cornerstone | No | No | 5.81% | 0.00% | Depth | ✅ Correct |
| 19 | Aaron Gordon | 2023-24 | Role Player - Depth | No | No | 2.43% | 13.37% | Depth | ✅ Correct |
| 20 | Brook Lopez | 2023-24 | Role Player - Depth | No | No | 0.42% | 58.06% | Depth | ✅ Correct |
| 21 | Chris Paul | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 66.64% | 0.00% | Depth | ❌ Incorrect |
| 22 | Chris Paul | 2016-17 | Confirmed Franchise Cornerstone | Yes | Yes | 92.45% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 23 | Chris Paul | 2017-18 | Confirmed Franchise Cornerstone | Yes | Yes | 72.73% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 24 | Jimmy Butler III | 2015-16 | Confirmed Franchise Cornerstone | Yes | Yes | 71.93% | 10.57% | Franchise Cornerstone | ✅ Correct |
| 25 | James Harden | 2015-16 | Confirmed Franchise Cornerstone | Yes | Yes | 99.53% | 3.70% | Franchise Cornerstone | ✅ Correct |
| 26 | Eric Bledsoe | 2015-16 | Not Franchise Cornerstone | No | Yes | 93.36% | 0.00% | Franchise Cornerstone | ❌ Incorrect |
| 27 | James Harden | 2015-16 | Confirmed Franchise Cornerstone | Yes | Yes | 99.53% | 3.70% | Franchise Cornerstone | ✅ Correct |
| 28 | John Wall | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 49.07% | 38.53% | Depth | ❌ Incorrect |
| 29 | LeBron James | 2015-16 | Confirmed Franchise Cornerstone | Yes | Yes | 99.16% | 0.25% | Franchise Cornerstone | ✅ Correct |
| 30 | Kawhi Leonard | 2015-16 | Confirmed Franchise Cornerstone | Yes | Yes | 79.84% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 31 | Giannis Antetokounmpo | 2024-25 | Confirmed Franchise Cornerstone | Yes | Yes | 99.12% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 32 | Donovan Mitchell | 2024-25 | Confirmed Franchise Cornerstone | Yes | Yes | 96.87% | 4.08% | Franchise Cornerstone | ✅ Correct |
| 33 | LeBron James | 2024-25 | Confirmed Franchise Cornerstone | Yes | Yes | 93.47% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 34 | Cade Cunningham | 2024-25 | Emerging Franchise Cornerstone | Yes | Yes | 99.28% | 43.62% | Franchise Cornerstone | ✅ Correct |
| 35 | Kevin Porter Jr | 2024-25 | Not Franchise Cornerstone | No | N/A | N/A | N/A | N/A | ❌ No Data |

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

### Joel Embiid (2018-19)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 14.52%
- **Dependence**: 0.30%
- **Risk Category**: Depth
- **Notes**: Performance too low (14.52% < 70%); False Negative: Should be Franchise Cornerstone

### Jordan Poole (2021-22)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 84.05%
- **Dependence**: 0.00%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### Julius Randle (2023-24)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 88.46%
- **Dependence**: 49.86%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### DeMar DeRozan (2016-17)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 99.50%
- **Dependence**: 2.21%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### Karl-Anthony Towns (2021-22)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 88.32%
- **Dependence**: 0.00%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### Karl-Anthony Towns (2023-24)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 94.01%
- **Dependence**: 0.00%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### Chris Paul (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 66.64%
- **Dependence**: 0.00%
- **Risk Category**: Depth
- **Notes**: Performance too low (66.64% < 70%); False Negative: Should be Franchise Cornerstone

### Eric Bledsoe (2015-16)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 93.36%
- **Dependence**: 0.00%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### John Wall (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 49.07%
- **Dependence**: 38.53%
- **Risk Category**: Depth
- **Notes**: Performance too low (49.07% < 70%); Dependence too high (38.53% >= 30%); False Negative: Should be Franchise Cornerstone

## Missing Data

- **Kevin Porter Jr (2024-25)**: No data found in dataset

