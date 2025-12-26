# Overall Star Prediction: Franchise Cornerstone Classification Test Report

**Date**: 2025-12-21 15:19:23

## Executive Summary

**Primary Focus**: Testing the model's ability to correctly identify Franchise Cornerstones at current usage levels.

**Framework**: 2D Risk Matrix - Franchise Cornerstones require High Performance (≥70%) + Low Dependence (<30%).

- **Total Test Cases**: 35
- **Data Found**: 34
- **Correct Classifications**: 19
- **Incorrect Classifications**: 15
- **Accuracy**: 55.9%

## Results by Category

### Confirmed Franchise Cornerstone
- **Total**: 17
- **Correct**: 10
- **Incorrect**: 7
- **Accuracy**: 58.8%

### Borderline Franchise Cornerstone
- **Total**: 2
- **Correct**: 2
- **Incorrect**: 0
- **Accuracy**: 100.0%

### Not Franchise Cornerstone
- **Total**: 12
- **Correct**: 4
- **Incorrect**: 8
- **Accuracy**: 33.3%

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
| 1 | Nikola Jokić | 2023-24 | Confirmed Franchise Cornerstone | Yes | Yes | 89.53% | 29.32% | Franchise Cornerstone | ✅ Correct |
| 2 | Luka Dončić | 2023-24 | Confirmed Franchise Cornerstone | Yes | Yes | 95.00% | 3.06% | Franchise Cornerstone | ✅ Correct |
| 3 | Giannis Antetokounmpo | 2023-24 | Confirmed Franchise Cornerstone | Yes | Yes | 95.00% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 4 | Joel Embiid | 2023-24 | Confirmed Franchise Cornerstone | Yes | No | 62.79% | 68.08% | Luxury Component | ❌ Incorrect |
| 5 | Joel Embiid | 2018-19 | Confirmed Franchise Cornerstone | Yes | No | 60.33% | 0.30% | Depth | ❌ Incorrect |
| 6 | Shai Gilgeous-Alexander | 2023-24 | Borderline Franchise Cornerstone | Yes | Yes | 95.00% | 16.94% | Franchise Cornerstone | ✅ Correct |
| 7 | Tyrese Maxey | 2023-24 | Borderline Franchise Cornerstone | Yes | Yes | 72.21% | 40.45% | Franchise Cornerstone | ✅ Correct |
| 8 | Jordan Poole | 2023-24 | Not Franchise Cornerstone | No | No | 2.03% | 57.57% | Depth | ✅ Correct |
| 9 | Jordan Poole | 2021-22 | Not Franchise Cornerstone | No | Yes | 86.27% | 41.90% | Franchise Cornerstone | ❌ Incorrect |
| 10 | Domantas Sabonis | 2023-24 | Not Franchise Cornerstone | No | Yes | 78.99% | 12.92% | Franchise Cornerstone | ❌ Incorrect |
| 11 | Julius Randle | 2023-24 | Not Franchise Cornerstone | No | No | 60.59% | 68.06% | Luxury Component | ✅ Correct |
| 12 | DeMar DeRozan | 2015-16 | Not Franchise Cornerstone | No | No | 56.42% | 15.75% | Depth | ✅ Correct |
| 13 | DeMar DeRozan | 2016-17 | Not Franchise Cornerstone | No | Yes | 80.03% | 1.70% | Franchise Cornerstone | ❌ Incorrect |
| 14 | Karl-Anthony Towns | 2021-22 | Not Franchise Cornerstone | No | Yes | 76.61% | 16.09% | Franchise Cornerstone | ❌ Incorrect |
| 15 | Karl-Anthony Towns | 2022-23 | Not Franchise Cornerstone | No | No | 2.20% | 74.53% | Avoid | ✅ Correct |
| 16 | Karl-Anthony Towns | 2023-24 | Not Franchise Cornerstone | No | Yes | 87.61% | 29.80% | Franchise Cornerstone | ❌ Incorrect |
| 17 | Ben Simmons | 2018-19 | Not Franchise Cornerstone | No | Yes | 86.01% | 6.89% | Franchise Cornerstone | ❌ Incorrect |
| 18 | Ben Simmons | 2020-21 | Not Franchise Cornerstone | No | Yes | 94.88% | 1.78% | Franchise Cornerstone | ❌ Incorrect |
| 19 | Aaron Gordon | 2023-24 | Role Player - Depth | No | No | 1.29% | 14.69% | Depth | ✅ Correct |
| 20 | Brook Lopez | 2023-24 | Role Player - Depth | No | No | 0.63% | 74.74% | Avoid | ✅ Correct |
| 21 | Chris Paul | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 79.56% | 50.94% | Franchise Cornerstone | ❌ Incorrect |
| 22 | Chris Paul | 2016-17 | Confirmed Franchise Cornerstone | Yes | No | 95.00% | 51.46% | Franchise Cornerstone | ❌ Incorrect |
| 23 | Chris Paul | 2017-18 | Confirmed Franchise Cornerstone | Yes | Yes | 95.00% | 42.52% | Franchise Cornerstone | ✅ Correct |
| 24 | Jimmy Butler III | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 1.90% | 10.57% | Depth | ❌ Incorrect |
| 25 | James Harden | 2015-16 | Confirmed Franchise Cornerstone | Yes | Yes | 70.37% | 11.80% | Franchise Cornerstone | ✅ Correct |
| 26 | Eric Bledsoe | 2015-16 | Not Franchise Cornerstone | No | Yes | 87.54% | 0.00% | Franchise Cornerstone | ❌ Incorrect |
| 27 | James Harden | 2015-16 | Confirmed Franchise Cornerstone | Yes | Yes | 70.37% | 11.80% | Franchise Cornerstone | ✅ Correct |
| 28 | John Wall | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 11.48% | 38.53% | Depth | ❌ Incorrect |
| 29 | LeBron James | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 65.06% | 18.06% | Depth | ❌ Incorrect |
| 30 | Kawhi Leonard | 2015-16 | Confirmed Franchise Cornerstone | Yes | Yes | 87.73% | 40.97% | Franchise Cornerstone | ✅ Correct |
| 31 | Giannis Antetokounmpo | 2024-25 | Confirmed Franchise Cornerstone | Yes | Yes | 95.00% | 0.00% | Franchise Cornerstone | ✅ Correct |
| 32 | Donovan Mitchell | 2024-25 | Confirmed Franchise Cornerstone | Yes | Yes | 82.28% | 48.08% | Franchise Cornerstone | ✅ Correct |
| 33 | LeBron James | 2024-25 | Confirmed Franchise Cornerstone | Yes | Yes | 78.34% | 38.45% | Franchise Cornerstone | ✅ Correct |
| 34 | Cade Cunningham | 2024-25 | Emerging Franchise Cornerstone | Yes | Yes | 73.52% | 44.44% | Franchise Cornerstone | ✅ Correct |
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

### Joel Embiid (2023-24)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 62.79%
- **Dependence**: 68.08%
- **Risk Category**: Luxury Component
- **Notes**: Performance too low (62.79% < 70%); Dependence too high (68.08% >= 30%); False Negative: Should be Franchise Cornerstone

### Joel Embiid (2018-19)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 60.33%
- **Dependence**: 0.30%
- **Risk Category**: Depth
- **Notes**: Performance too low (60.33% < 70%); False Negative: Should be Franchise Cornerstone

### Jordan Poole (2021-22)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 86.27%
- **Dependence**: 41.90%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### Domantas Sabonis (2023-24)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 78.99%
- **Dependence**: 12.92%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### DeMar DeRozan (2016-17)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 80.03%
- **Dependence**: 1.70%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### Karl-Anthony Towns (2021-22)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 76.61%
- **Dependence**: 16.09%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### Karl-Anthony Towns (2023-24)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 87.61%
- **Dependence**: 29.80%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### Ben Simmons (2018-19)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 86.01%
- **Dependence**: 6.89%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### Ben Simmons (2020-21)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 94.88%
- **Dependence**: 1.78%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### Chris Paul (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 79.56%
- **Dependence**: 50.94%
- **Risk Category**: Franchise Cornerstone
- **Notes**: Dependence too high (50.94% >= 30%); False Negative: Should be Franchise Cornerstone

### Chris Paul (2016-17)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 95.00%
- **Dependence**: 51.46%
- **Risk Category**: Franchise Cornerstone
- **Notes**: Dependence too high (51.46% >= 30%); False Negative: Should be Franchise Cornerstone

### Jimmy Butler III (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 1.90%
- **Dependence**: 10.57%
- **Risk Category**: Depth
- **Notes**: Performance too low (1.90% < 70%); False Negative: Should be Franchise Cornerstone

### Eric Bledsoe (2015-16)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 87.54%
- **Dependence**: 0.00%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### John Wall (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 11.48%
- **Dependence**: 38.53%
- **Risk Category**: Depth
- **Notes**: Performance too low (11.48% < 70%); Dependence too high (38.53% >= 30%); False Negative: Should be Franchise Cornerstone

### LeBron James (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 65.06%
- **Dependence**: 18.06%
- **Risk Category**: Depth
- **Notes**: Performance too low (65.06% < 70%); False Negative: Should be Franchise Cornerstone

## Missing Data

- **Kevin Porter Jr (2024-25)**: No data found in dataset

