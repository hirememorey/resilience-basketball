# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-24 21:25:52

## Executive Summary

- **Total Test Cases**: 48
- **Data Found**: 48
- **Passed**: 29
- **Failed**: 19
- **Pass Rate**: 60.4%

## Results by Category

### True Positive
- **Total**: 19
- **Passed**: 12
- **Failed**: 7
- **Pass Rate**: 63.2%

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
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 78.87% | 23.91% | Franchise Cornerstone | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Victim (Fragile Role) | 13.27% | 51.17% | Depth | ❌ FAIL |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 95.00% | 33.79% | Franchise Cornerstone | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 83.72% | 39.25% | Franchise Cornerstone | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 77.25% | 14.30% | Franchise Cornerstone | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | Bulldozer (Fragile Star) | 50.00% | 28.02% | Depth | ❌ FAIL |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 78.82% | 26.13% | Franchise Cornerstone | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 79.09% | 55.32% | Franchise Cornerstone | ✅ PASS |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 69.18% | 26.97% | Depth | ❌ FAIL |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 66.62% | 16.67% | Depth | ❌ FAIL |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 58.71% | 26.84% | Depth | ❌ FAIL |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 77.48% | 15.18% | Franchise Cornerstone | ✅ PASS |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | King (Resilient Star) | 57.32% | 61.62% | Depth | ❌ FAIL |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | King (Resilient Star) | 95.96% | 8.57% | Franchise Cornerstone | ✅ PASS |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 96.87% | 81.24% | Luxury Component | ❌ FAIL |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 98.98% | 10.99% | Franchise Cornerstone | ✅ PASS |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 86.27% | 26.59% | Franchise Cornerstone | ❌ FAIL |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Bulldozer (Fragile Star) | 91.60% | 0.72% | Franchise Cornerstone | ❌ FAIL |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 53.51% | Depth | ✅ PASS |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Bulldozer (Fragile Star) | 67.69% | 65.00% | Luxury Component | ❌ FAIL |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 39.72% | Depth | ✅ PASS |
| 22 | DeMar DeRozan | 2015-16 | Not Franchise Cornerstone | Bulldozer (High) [Depth] | Victim (Fragile Role) | 58.68% | 11.38% | Depth | ✅ PASS |
| 23 | DeMar DeRozan | 2016-17 | Not Franchise Cornerstone | Bulldozer (High) [Depth] | Bulldozer (Fragile Star) | 98.26% | 0.00% | Franchise Cornerstone | ❌ FAIL |
| 24 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Bulldozer (Fragile Star) | 69.61% | 19.02% | Depth | ❌ FAIL |
| 25 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 6.02% | Depth | ✅ PASS |
| 26 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Bulldozer (Fragile Star) | 94.88% | 0.00% | Franchise Cornerstone | ❌ FAIL |
| 27 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Sniper (Resilient Role) | 0.00% | 73.29% | Avoid | ✅ PASS |
| 28 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 57.34% | 0.85% | Depth | ❌ FAIL |
| 29 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 80.43% | 58.18% | Franchise Cornerstone | ✅ PASS |
| 30 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 46.04% | Depth | ✅ PASS |
| 31 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 54.26% | Depth | ✅ PASS |
| 32 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 60.41% | Depth | ✅ PASS |
| 33 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 12.58% | Depth | ✅ PASS |
| 34 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 56.26% | Depth | ✅ PASS |
| 35 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 23.66% | Depth | ✅ PASS |
| 36 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 60.65% | Depth | ✅ PASS |
| 37 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Sniper (Resilient Role) | 0.00% | 61.29% | Depth | ✅ PASS |
| 38 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 19.92% | Depth | ✅ PASS |
| 39 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 71.15% | Luxury Component | ✅ PASS |
| 40 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 2.60% | Depth | ✅ PASS |
| 41 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 21.27% | Depth | ✅ PASS |
| 42 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 66.04% | 57.13% | Depth | ❌ FAIL |
| 43 | Jamal Murray | 2019-20 | True Positive - Latent Star (Riser) | Bulldozer (High) | King (Resilient Star) | 87.05% | 51.97% | Franchise Cornerstone | ✅ PASS |
| 44 | Rudy Gobert | 2020-21 | False Positive - System Specialist | Sniper (Low) [Luxury Component] | Sniper (Resilient Role) | 2.44% | 50.00% | Depth | ❌ FAIL |
| 45 | Isaiah Thomas | 2016-17 | True Positive - Outlier | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 99.51% | 1.50% | Franchise Cornerstone | ✅ PASS |
| 46 | Zach LaVine | 2020-21 | False Positive - Empty Calories | Bulldozer (Medium) [Luxury Component] | King (Resilient Star) | 97.35% | 33.90% | Franchise Cornerstone | ❌ FAIL |
| 47 | Fred VanVleet | 2021-22 | False Positive - Inefficient Volume | Victim (Low) [Avoid] | Bulldozer (Fragile Star) | 72.59% | 61.01% | Franchise Cornerstone | ❌ FAIL |
| 48 | Draymond Green | 2015-16 | System Hub - Unique Archetype | Sniper (Low) [Luxury Component] | Victim (Fragile Role) | 26.90% | 9.47% | Depth | ❌ FAIL |

## Notes

### Failed Tests

**Victor Oladipo (2016-17)**: Expected high performance (≥65%), got 13.27%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Jayson Tatum (2017-18)**: Expected high performance (≥65%), got 50.00%

**Nikola Jokić (2015-16)**: Expected risk category 'Franchise Cornerstone', got 'Depth'

**Nikola Jokić (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Depth'

**Nikola Jokić (2017-18)**: Expected high performance (≥65%), got 58.71%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 58.71%

**Anthony Davis (2015-16)**: Expected high performance (≥65%), got 57.32%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 57.32%

**Joel Embiid (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Luxury Component'

**Jordan Poole (2021-22)**: Expected low performance (<55%), got 86.27%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone'; Risk category matches but performance doesn't: 86.27%

**Talen Horton-Tucker (2020-21)**: Expected low performance (<55%), got 91.60%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**D'Angelo Russell (2018-19)**: Expected low performance (<55%), got 67.69%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**DeMar DeRozan (2016-17)**: Expected risk category 'Depth', got 'Franchise Cornerstone'

**Ben Simmons (2017-18)**: Expected low performance (<55%), got 69.61%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Ben Simmons (2020-21)**: Expected low performance (<55%), got 94.88%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Domantas Sabonis (2021-22)**: Expected low performance (<55%), got 57.34%; Expected risk category 'Luxury Component', got 'Depth'; Risk category matches but performance doesn't: 57.34%

**Markelle Fultz (2023-24)**: Expected low performance (<55%), got 66.04%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Rudy Gobert (2020-21)**: Expected risk category 'Luxury Component', got 'Depth'

**Zach LaVine (2020-21)**: Expected medium performance (30-70%), got 97.35%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone'; Risk category matches but performance doesn't: 97.35%

**Fred VanVleet (2021-22)**: Expected low performance (<55%), got 72.59%; Expected risk category 'Avoid', got 'Franchise Cornerstone'; Risk category matches but performance doesn't: 72.59%

**Draymond Green (2015-16)**: Expected risk category 'Luxury Component', got 'Depth'

