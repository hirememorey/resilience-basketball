# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-14 23:02:32

## Executive Summary

- **Total Test Cases**: 42
- **Data Found**: 42
- **Passed**: 29
- **Failed**: 13
- **Pass Rate**: 69.0%

## Results by Category

### True Positive
- **Total**: 17
- **Passed**: 8
- **Failed**: 9
- **Pass Rate**: 47.1%

### False Positive
- **Total**: 5
- **Passed**: 4
- **Failed**: 1
- **Pass Rate**: 80.0%

### Not Franchise Cornerstone
- **Total**: 2
- **Passed**: 0
- **Failed**: 2
- **Pass Rate**: 0.0%

### True Negative
- **Total**: 17
- **Passed**: 16
- **Failed**: 1
- **Pass Rate**: 94.1%

### System Player
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Performance | Dependence | Risk Category | Pass |
|------|--------|--------|----------|----------|-----------|-------------|------------|---------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 0.00% | 0.34% | Depth | ❌ FAIL |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 92.46% | 51.17% | Franchise Cornerstone | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 0.00% | 0.00% | Depth | ❌ FAIL |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 0.00% | 0.00% | Depth | ❌ FAIL |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 83.46% | 0.00% | Franchise Cornerstone | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | Bulldozer (Fragile Star) | 50.00% | 17.27% | Depth | ❌ FAIL |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Victim (Fragile Role) | 30.00% | 0.00% | Depth | ❌ FAIL |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 0.00% | 0.00% | Depth | ❌ FAIL |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 95.11% | 0.00% | Franchise Cornerstone | ✅ PASS |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 87.59% | 0.00% | Franchise Cornerstone | ✅ PASS |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 91.36% | 10.16% | Franchise Cornerstone | ✅ PASS |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 93.48% | 26.39% | Franchise Cornerstone | ✅ PASS |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 67.24% | 57.70% | Depth | ❌ FAIL |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 67.58% | 17.51% | Depth | ❌ FAIL |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 85.13% | 78.94% | Luxury Component | ❌ FAIL |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 89.34% | 14.57% | Franchise Cornerstone | ✅ PASS |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 98.14% | 0.00% | Franchise Cornerstone | ❌ FAIL |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 41.64% | 28.00% | Depth | ✅ PASS |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 0.00% | Depth | ✅ PASS |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | King (Resilient Star) | 0.00% | 40.12% | Depth | ✅ PASS |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 41.23% | Depth | ✅ PASS |
| 22 | DeMar DeRozan | 2015-16 | Not Franchise Cornerstone | Bulldozer (High) [Depth] | Bulldozer (Fragile Star) | 94.64% | 15.75% | Franchise Cornerstone | ❌ FAIL |
| 23 | DeMar DeRozan | 2016-17 | Not Franchise Cornerstone | Bulldozer (High) [Depth] | Bulldozer (Fragile Star) | 98.82% | 2.21% | Franchise Cornerstone | ❌ FAIL |
| 24 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 7.67% | Depth | ✅ PASS |
| 25 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 0.00% | Depth | ✅ PASS |
| 26 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 0.00% | Depth | ✅ PASS |
| 27 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 0.00% | 62.28% | Depth | ✅ PASS |
| 28 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | King (Resilient Star) | 81.96% | 0.00% | Franchise Cornerstone | ❌ FAIL |
| 29 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | King (Resilient Star) | 91.79% | 0.00% | Franchise Cornerstone | ✅ PASS |
| 30 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 0.00% | Depth | ✅ PASS |
| 31 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 0.00% | Depth | ✅ PASS |
| 32 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 6.96% | Depth | ✅ PASS |
| 33 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 0.00% | Depth | ✅ PASS |
| 34 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 0.09% | Depth | ✅ PASS |
| 35 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 20.34% | Depth | ✅ PASS |
| 36 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 60.65% | Depth | ✅ PASS |
| 37 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 61.29% | Depth | ✅ PASS |
| 38 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 35.33% | Depth | ✅ PASS |
| 39 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 20.15% | 71.15% | Avoid | ✅ PASS |
| 40 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 36.69% | Depth | ✅ PASS |
| 41 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 34.61% | Depth | ✅ PASS |
| 42 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 0.00% | 60.00% | Depth | ✅ PASS |

## Notes

### Failed Tests

**Shai Gilgeous-Alexander (2018-19)**: Expected high performance (≥65%), got 0.00%

**Jalen Brunson (2020-21)**: Expected high performance (≥65%), got 0.00%

**Tyrese Maxey (2021-22)**: Expected high performance (≥65%), got 0.00%

**Jayson Tatum (2017-18)**: Expected high performance (≥65%), got 50.00%

**Mikal Bridges (2021-22)**: Expected high performance (≥65%), got 30.00%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Desmond Bane (2021-22)**: Expected high performance (≥65%), got 0.00%

**Anthony Davis (2015-16)**: Expected risk category 'Franchise Cornerstone', got 'Depth'

**Anthony Davis (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Depth'

**Joel Embiid (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Luxury Component'

**Jordan Poole (2021-22)**: Expected low performance (<55%), got 98.14%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone'; Risk category matches but performance doesn't: 98.14%

**DeMar DeRozan (2015-16)**: Expected risk category 'Depth', got 'Franchise Cornerstone'

**DeMar DeRozan (2016-17)**: Expected risk category 'Depth', got 'Franchise Cornerstone'

**Domantas Sabonis (2021-22)**: Expected low performance (<55%), got 81.96%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone'; Risk category matches but performance doesn't: 81.96%

