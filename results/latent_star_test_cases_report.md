# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-21 21:14:21

## Executive Summary

- **Total Test Cases**: 48
- **Data Found**: 48
- **Passed**: 26
- **Failed**: 22
- **Pass Rate**: 54.2%

## Results by Category

### True Positive
- **Total**: 19
- **Passed**: 9
- **Failed**: 10
- **Pass Rate**: 47.4%

### False Positive
- **Total**: 8
- **Passed**: 2
- **Failed**: 6
- **Pass Rate**: 25.0%

### Not Franchise Cornerstone
- **Total**: 2
- **Passed**: 1
- **Failed**: 1
- **Pass Rate**: 50.0%

### True Negative
- **Total**: 17
- **Passed**: 13
- **Failed**: 4
- **Pass Rate**: 76.5%

### System Player
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

### System Hub
- **Total**: 1
- **Passed**: 0
- **Failed**: 1
- **Pass Rate**: 0.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Performance | Dependence | Risk Category | Pass |
|------|--------|--------|----------|----------|-----------|-------------|------------|---------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 78.87% | 30.73% | Franchise Cornerstone | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Victim (Fragile Role) | 6.83% | 51.17% | Depth | ❌ FAIL |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 95.00% | 44.99% | Franchise Cornerstone | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 83.72% | 39.25% | Franchise Cornerstone | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 77.25% | 21.36% | Franchise Cornerstone | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | Victim (Fragile Role) | 22.23% | 28.02% | Depth | ❌ FAIL |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 78.82% | 42.50% | Franchise Cornerstone | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 79.09% | 64.46% | Franchise Cornerstone | ✅ PASS |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 69.18% | 41.05% | Depth | ❌ FAIL |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 66.62% | 28.21% | Depth | ❌ FAIL |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 58.71% | 34.94% | Depth | ❌ FAIL |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 71.11% | 26.39% | Franchise Cornerstone | ✅ PASS |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Victim (Fragile Role) | 6.38% | 61.62% | Depth | ❌ FAIL |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 60.23% | 17.51% | Depth | ❌ FAIL |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Victim (Fragile Role) | 18.86% | 81.24% | Avoid | ❌ FAIL |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Victim (Fragile Role) | 6.34% | 14.57% | Depth | ❌ FAIL |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 86.27% | 41.90% | Franchise Cornerstone | ❌ FAIL |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Bulldozer (Fragile Star) | 91.60% | 17.18% | Franchise Cornerstone | ❌ FAIL |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 62.19% | Depth | ✅ PASS |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Bulldozer (Fragile Star) | 67.69% | 68.07% | Luxury Component | ❌ FAIL |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 41.23% | Depth | ✅ PASS |
| 22 | DeMar DeRozan | 2015-16 | Not Franchise Cornerstone | Bulldozer (High) [Depth] | Bulldozer (Fragile Star) | 64.43% | 15.75% | Depth | ✅ PASS |
| 23 | DeMar DeRozan | 2016-17 | Not Franchise Cornerstone | Bulldozer (High) [Depth] | Bulldozer (Fragile Star) | 80.76% | 1.70% | Franchise Cornerstone | ❌ FAIL |
| 24 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Bulldozer (Fragile Star) | 75.32% | 19.02% | Franchise Cornerstone | ❌ FAIL |
| 25 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 6.89% | Depth | ✅ PASS |
| 26 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Bulldozer (Fragile Star) | 94.88% | 1.78% | Franchise Cornerstone | ❌ FAIL |
| 27 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 0.00% | 73.29% | Avoid | ✅ PASS |
| 28 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 57.34% | 8.16% | Depth | ❌ FAIL |
| 29 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 80.43% | 58.18% | Franchise Cornerstone | ✅ PASS |
| 30 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 56.46% | Depth | ✅ PASS |
| 31 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 62.67% | Depth | ✅ PASS |
| 32 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 60.41% | Depth | ✅ PASS |
| 33 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 25.28% | Depth | ✅ PASS |
| 34 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 64.15% | Depth | ✅ PASS |
| 35 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 23.66% | Depth | ✅ PASS |
| 36 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 60.65% | Depth | ✅ PASS |
| 37 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 61.29% | Depth | ✅ PASS |
| 38 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 28.88% | Depth | ✅ PASS |
| 39 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 3.09% | 71.15% | Avoid | ✅ PASS |
| 40 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 17.02% | Depth | ✅ PASS |
| 41 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 34.30% | Depth | ✅ PASS |
| 42 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | Bulldozer (Fragile Star) | 58.27% | 60.00% | Depth | ❌ FAIL |
| 43 | Jamal Murray | 2019-20 | True Positive - Latent Star (Riser) | Bulldozer (High) | Bulldozer (Fragile Star) | 58.29% | 53.60% | Depth | ❌ FAIL |
| 44 | Rudy Gobert | 2020-21 | False Positive - System Specialist | Sniper (Low) [Luxury Component] | Victim (Fragile Role) | 40.08% | 50.00% | Depth | ❌ FAIL |
| 45 | Isaiah Thomas | 2016-17 | True Positive - Outlier | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 92.78% | 11.44% | Franchise Cornerstone | ✅ PASS |
| 46 | Zach LaVine | 2020-21 | False Positive - Empty Calories | Bulldozer (Medium) [Luxury Component] | Bulldozer (Fragile Star) | 92.62% | 33.90% | Franchise Cornerstone | ❌ FAIL |
| 47 | Fred VanVleet | 2021-22 | False Positive - Inefficient Volume | Victim (Low) [Avoid] | Bulldozer (Fragile Star) | 72.59% | 63.73% | Franchise Cornerstone | ❌ FAIL |
| 48 | Draymond Green | 2015-16 | System Hub - Unique Archetype | Sniper (Low) [Luxury Component] | Bulldozer (Fragile Star) | 58.16% | 11.29% | Depth | ❌ FAIL |

## Notes

### Failed Tests

**Victor Oladipo (2016-17)**: Expected high performance (≥65%), got 6.83%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Jayson Tatum (2017-18)**: Expected high performance (≥65%), got 22.23%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Nikola Jokić (2015-16)**: Expected risk category 'Franchise Cornerstone', got 'Depth'

**Nikola Jokić (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Depth'

**Nikola Jokić (2017-18)**: Expected high performance (≥65%), got 58.71%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 58.71%

**Anthony Davis (2015-16)**: Expected high performance (≥65%), got 6.38%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 6.38%

**Anthony Davis (2016-17)**: Expected high performance (≥65%), got 60.23%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 60.23%

**Joel Embiid (2016-17)**: Expected high performance (≥65%), got 18.86%; Expected risk category 'Franchise Cornerstone', got 'Avoid'; Risk category matches but performance doesn't: 18.86%

**Joel Embiid (2017-18)**: Expected high performance (≥65%), got 6.34%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 6.34%

**Jordan Poole (2021-22)**: Expected low performance (<55%), got 86.27%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone'; Risk category matches but performance doesn't: 86.27%

**Talen Horton-Tucker (2020-21)**: Expected low performance (<55%), got 91.60%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**D'Angelo Russell (2018-19)**: Expected low performance (<55%), got 67.69%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**DeMar DeRozan (2016-17)**: Expected risk category 'Depth', got 'Franchise Cornerstone'

**Ben Simmons (2017-18)**: Expected low performance (<55%), got 75.32%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Ben Simmons (2020-21)**: Expected low performance (<55%), got 94.88%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Domantas Sabonis (2021-22)**: Expected low performance (<55%), got 57.34%; Expected risk category 'Luxury Component', got 'Depth'; Risk category matches but performance doesn't: 57.34%

**Markelle Fultz (2023-24)**: Expected low performance (<55%), got 58.27%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Jamal Murray (2019-20)**: Expected high performance (≥65%), got 58.29%

**Rudy Gobert (2020-21)**: Expected risk category 'Luxury Component', got 'Depth'

**Zach LaVine (2020-21)**: Expected medium performance (30-70%), got 92.62%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone'; Risk category matches but performance doesn't: 92.62%

**Fred VanVleet (2021-22)**: Expected low performance (<55%), got 72.59%; Expected risk category 'Avoid', got 'Franchise Cornerstone'; Risk category matches but performance doesn't: 72.59%

**Draymond Green (2015-16)**: Expected low performance (<55%), got 58.16%; Expected risk category 'Luxury Component', got 'Depth'; Risk category matches but performance doesn't: 58.16%

