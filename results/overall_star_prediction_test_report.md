# Overall Star Prediction: Franchise Cornerstone Classification Test Report

**Date**: 2025-12-20 16:00:52

## Executive Summary

**Primary Focus**: Testing the model's ability to correctly identify Franchise Cornerstones at current usage levels.

**Framework**: 2D Risk Matrix - Franchise Cornerstones require High Performance (≥70%) + Low Dependence (<30%).

- **Total Test Cases**: 35
- **Data Found**: 34
- **Correct Classifications**: 14
- **Incorrect Classifications**: 20
- **Accuracy**: 41.2%

## Results by Category

### Confirmed Franchise Cornerstone
- **Total**: 17
- **Correct**: 1
- **Incorrect**: 16
- **Accuracy**: 5.9%

### Borderline Franchise Cornerstone
- **Total**: 2
- **Correct**: 0
- **Incorrect**: 2
- **Accuracy**: 0.0%

### Not Franchise Cornerstone
- **Total**: 12
- **Correct**: 11
- **Incorrect**: 1
- **Accuracy**: 91.7%

### Role Player
- **Total**: 2
- **Correct**: 2
- **Incorrect**: 0
- **Accuracy**: 100.0%

### Emerging Franchise Cornerstone
- **Total**: 1
- **Correct**: 0
- **Incorrect**: 1
- **Accuracy**: 0.0%

## Detailed Results

| Test | Player | Season | Category | Expected FC | Predicted FC | Performance | Dependence | Risk Category | Correct |
|------|--------|--------|----------|-------------|---------------|-------------|------------|---------------|---------|
| 1 | Nikola Jokić | 2023-24 | Confirmed Franchise Cornerstone | Yes | No | 29.96% | 29.32% | Depth | ❌ Incorrect |
| 2 | Luka Dončić | 2023-24 | Confirmed Franchise Cornerstone | Yes | No | 35.44% | 3.06% | Depth | ❌ Incorrect |
| 3 | Giannis Antetokounmpo | 2023-24 | Confirmed Franchise Cornerstone | Yes | No | 13.07% | 0.00% | Depth | ❌ Incorrect |
| 4 | Joel Embiid | 2023-24 | Confirmed Franchise Cornerstone | Yes | No | 54.98% | 68.08% | Luxury Component | ❌ Incorrect |
| 5 | Joel Embiid | 2018-19 | Confirmed Franchise Cornerstone | Yes | No | 5.98% | 0.30% | Depth | ❌ Incorrect |
| 6 | Shai Gilgeous-Alexander | 2023-24 | Borderline Franchise Cornerstone | Yes | No | 28.23% | 16.94% | Depth | ❌ Incorrect |
| 7 | Tyrese Maxey | 2023-24 | Borderline Franchise Cornerstone | Yes | No | 7.67% | 40.45% | Depth | ❌ Incorrect |
| 8 | Jordan Poole | 2023-24 | Not Franchise Cornerstone | No | No | 3.77% | 57.57% | Depth | ✅ Correct |
| 9 | Jordan Poole | 2021-22 | Not Franchise Cornerstone | No | No | 2.90% | 41.90% | Depth | ✅ Correct |
| 10 | Domantas Sabonis | 2023-24 | Not Franchise Cornerstone | No | No | 4.14% | 12.92% | Depth | ✅ Correct |
| 11 | Julius Randle | 2023-24 | Not Franchise Cornerstone | No | No | 5.95% | 68.06% | Avoid | ✅ Correct |
| 12 | DeMar DeRozan | 2015-16 | Not Franchise Cornerstone | No | No | 13.18% | 15.75% | Depth | ✅ Correct |
| 13 | DeMar DeRozan | 2016-17 | Not Franchise Cornerstone | No | Yes | 92.28% | 1.70% | Franchise Cornerstone | ❌ Incorrect |
| 14 | Karl-Anthony Towns | 2021-22 | Not Franchise Cornerstone | No | No | 2.94% | 16.09% | Depth | ✅ Correct |
| 15 | Karl-Anthony Towns | 2022-23 | Not Franchise Cornerstone | No | No | 8.01% | 74.53% | Avoid | ✅ Correct |
| 16 | Karl-Anthony Towns | 2023-24 | Not Franchise Cornerstone | No | No | 3.85% | 29.80% | Depth | ✅ Correct |
| 17 | Ben Simmons | 2018-19 | Not Franchise Cornerstone | No | No | 6.67% | 6.89% | Depth | ✅ Correct |
| 18 | Ben Simmons | 2020-21 | Not Franchise Cornerstone | No | No | 3.90% | 1.78% | Depth | ✅ Correct |
| 19 | Aaron Gordon | 2023-24 | Role Player - Depth | No | No | 1.78% | 14.69% | Depth | ✅ Correct |
| 20 | Brook Lopez | 2023-24 | Role Player - Depth | No | No | 1.19% | 74.74% | Avoid | ✅ Correct |
| 21 | Chris Paul | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 3.05% | 50.94% | Depth | ❌ Incorrect |
| 22 | Chris Paul | 2016-17 | Confirmed Franchise Cornerstone | Yes | No | 9.50% | 51.46% | Depth | ❌ Incorrect |
| 23 | Chris Paul | 2017-18 | Confirmed Franchise Cornerstone | Yes | No | 5.54% | 42.52% | Depth | ❌ Incorrect |
| 24 | Jimmy Butler III | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 2.98% | 10.57% | Depth | ❌ Incorrect |
| 25 | James Harden | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 54.81% | 11.80% | Depth | ❌ Incorrect |
| 26 | Eric Bledsoe | 2015-16 | Not Franchise Cornerstone | No | No | 5.07% | 0.00% | Depth | ✅ Correct |
| 27 | James Harden | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 54.81% | 11.80% | Depth | ❌ Incorrect |
| 28 | John Wall | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 7.92% | 38.53% | Depth | ❌ Incorrect |
| 29 | LeBron James | 2015-16 | Confirmed Franchise Cornerstone | Yes | Yes | 72.36% | 18.06% | Franchise Cornerstone | ✅ Correct |
| 30 | Kawhi Leonard | 2015-16 | Confirmed Franchise Cornerstone | Yes | No | 6.25% | 40.97% | Depth | ❌ Incorrect |
| 31 | Giannis Antetokounmpo | 2024-25 | Confirmed Franchise Cornerstone | Yes | No | 51.08% | 0.00% | Depth | ❌ Incorrect |
| 32 | Donovan Mitchell | 2024-25 | Confirmed Franchise Cornerstone | Yes | No | 52.50% | 48.08% | Depth | ❌ Incorrect |
| 33 | LeBron James | 2024-25 | Confirmed Franchise Cornerstone | Yes | No | 9.46% | 38.45% | Depth | ❌ Incorrect |
| 34 | Cade Cunningham | 2024-25 | Emerging Franchise Cornerstone | Yes | No | 31.43% | 44.44% | Depth | ❌ Incorrect |
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

### Nikola Jokić (2023-24)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 29.96%
- **Dependence**: 29.32%
- **Risk Category**: Depth
- **Notes**: Performance too low (29.96% < 70%); False Negative: Should be Franchise Cornerstone

### Luka Dončić (2023-24)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 35.44%
- **Dependence**: 3.06%
- **Risk Category**: Depth
- **Notes**: Performance too low (35.44% < 70%); False Negative: Should be Franchise Cornerstone

### Giannis Antetokounmpo (2023-24)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 13.07%
- **Dependence**: 0.00%
- **Risk Category**: Depth
- **Notes**: Performance too low (13.07% < 70%); False Negative: Should be Franchise Cornerstone

### Joel Embiid (2023-24)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 54.98%
- **Dependence**: 68.08%
- **Risk Category**: Luxury Component
- **Notes**: Performance too low (54.98% < 70%); Dependence too high (68.08% >= 30%); False Negative: Should be Franchise Cornerstone

### Joel Embiid (2018-19)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 5.98%
- **Dependence**: 0.30%
- **Risk Category**: Depth
- **Notes**: Performance too low (5.98% < 70%); False Negative: Should be Franchise Cornerstone

### Shai Gilgeous-Alexander (2023-24)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 28.23%
- **Dependence**: 16.94%
- **Risk Category**: Depth
- **Notes**: Performance too low (28.23% < 70%); False Negative: Should be Franchise Cornerstone

### Tyrese Maxey (2023-24)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 7.67%
- **Dependence**: 40.45%
- **Risk Category**: Depth
- **Notes**: Performance too low (7.67% < 70%); Dependence too high (40.45% >= 30%); False Negative: Should be Franchise Cornerstone

### DeMar DeRozan (2016-17)
- **Expected**: Not Franchise Cornerstone
- **Predicted**: Franchise Cornerstone
- **Performance**: 92.28%
- **Dependence**: 1.70%
- **Risk Category**: Franchise Cornerstone
- **Notes**: False Positive: Should not be Franchise Cornerstone

### Chris Paul (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 3.05%
- **Dependence**: 50.94%
- **Risk Category**: Depth
- **Notes**: Performance too low (3.05% < 70%); Dependence too high (50.94% >= 30%); False Negative: Should be Franchise Cornerstone

### Chris Paul (2016-17)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 9.50%
- **Dependence**: 51.46%
- **Risk Category**: Depth
- **Notes**: Performance too low (9.50% < 70%); Dependence too high (51.46% >= 30%); False Negative: Should be Franchise Cornerstone

### Chris Paul (2017-18)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 5.54%
- **Dependence**: 42.52%
- **Risk Category**: Depth
- **Notes**: Performance too low (5.54% < 70%); Dependence too high (42.52% >= 30%); False Negative: Should be Franchise Cornerstone

### Jimmy Butler III (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 2.98%
- **Dependence**: 10.57%
- **Risk Category**: Depth
- **Notes**: Performance too low (2.98% < 70%); False Negative: Should be Franchise Cornerstone

### James Harden (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 54.81%
- **Dependence**: 11.80%
- **Risk Category**: Depth
- **Notes**: Performance too low (54.81% < 70%); False Negative: Should be Franchise Cornerstone

### James Harden (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 54.81%
- **Dependence**: 11.80%
- **Risk Category**: Depth
- **Notes**: Performance too low (54.81% < 70%); False Negative: Should be Franchise Cornerstone

### John Wall (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 7.92%
- **Dependence**: 38.53%
- **Risk Category**: Depth
- **Notes**: Performance too low (7.92% < 70%); Dependence too high (38.53% >= 30%); False Negative: Should be Franchise Cornerstone

### Kawhi Leonard (2015-16)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 6.25%
- **Dependence**: 40.97%
- **Risk Category**: Depth
- **Notes**: Performance too low (6.25% < 70%); Dependence too high (40.97% >= 30%); False Negative: Should be Franchise Cornerstone

### Giannis Antetokounmpo (2024-25)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 51.08%
- **Dependence**: 0.00%
- **Risk Category**: Depth
- **Notes**: Performance too low (51.08% < 70%); False Negative: Should be Franchise Cornerstone

### Donovan Mitchell (2024-25)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 52.50%
- **Dependence**: 48.08%
- **Risk Category**: Depth
- **Notes**: Performance too low (52.50% < 70%); Dependence too high (48.08% >= 30%); False Negative: Should be Franchise Cornerstone

### LeBron James (2024-25)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 9.46%
- **Dependence**: 38.45%
- **Risk Category**: Depth
- **Notes**: Performance too low (9.46% < 70%); Dependence too high (38.45% >= 30%); False Negative: Should be Franchise Cornerstone

### Cade Cunningham (2024-25)
- **Expected**: Franchise Cornerstone
- **Predicted**: Not Franchise Cornerstone
- **Performance**: 31.43%
- **Dependence**: 44.44%
- **Risk Category**: Depth
- **Notes**: Performance too low (31.43% < 70%); Dependence too high (44.44% >= 30%); False Negative: Should be Franchise Cornerstone

## Missing Data

- **Kevin Porter Jr (2024-25)**: No data found in dataset

