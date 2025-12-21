# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-20 22:44:07

## Executive Summary

- **Total Test Cases**: 42
- **Data Found**: 42
- **Passed**: 18
- **Failed**: 24
- **Pass Rate**: 42.9%

## Results by Category

### True Positive
- **Total**: 17
- **Passed**: 0
- **Failed**: 17
- **Pass Rate**: 0.0%

### False Positive
- **Total**: 5
- **Passed**: 2
- **Failed**: 3
- **Pass Rate**: 40.0%

### Not Franchise Cornerstone
- **Total**: 2
- **Passed**: 1
- **Failed**: 1
- **Pass Rate**: 50.0%

### True Negative
- **Total**: 17
- **Passed**: 14
- **Failed**: 3
- **Pass Rate**: 82.4%

### System Player
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Performance | Dependence | Risk Category | Pass |
|------|--------|--------|----------|----------|-----------|-------------|------------|---------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 55.00% | 30.73% | Depth | ❌ FAIL |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Victim (Fragile Role) | 7.75% | 51.17% | Depth | ❌ FAIL |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 55.00% | 44.99% | Depth | ❌ FAIL |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 55.00% | 39.25% | Depth | ❌ FAIL |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 55.00% | 21.36% | Depth | ❌ FAIL |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | Victim (Fragile Role) | 4.34% | 28.02% | Depth | ❌ FAIL |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 55.00% | 42.50% | Depth | ❌ FAIL |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 55.00% | 64.46% | Depth | ❌ FAIL |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 55.00% | 41.05% | Depth | ❌ FAIL |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 55.00% | 28.21% | Depth | ❌ FAIL |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Victim (Fragile Role) | 5.72% | 34.94% | Depth | ❌ FAIL |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 55.00% | 26.39% | Depth | ❌ FAIL |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Victim (Fragile Role) | 4.82% | 61.62% | Depth | ❌ FAIL |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 55.00% | 17.51% | Depth | ❌ FAIL |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Victim (Fragile Role) | 36.33% | 81.24% | Luxury Component | ❌ FAIL |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Victim (Fragile Role) | 5.83% | 14.57% | Depth | ❌ FAIL |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 55.00% | 41.90% | Depth | ❌ FAIL |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Bulldozer (Fragile Star) | 55.00% | 17.18% | Depth | ❌ FAIL |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 62.19% | Depth | ✅ PASS |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Bulldozer (Fragile Star) | 55.00% | 68.07% | Luxury Component | ❌ FAIL |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 41.23% | Depth | ✅ PASS |
| 22 | DeMar DeRozan | 2015-16 | Not Franchise Cornerstone | Bulldozer (High) [Depth] | Victim (Fragile Role) | 36.00% | 15.75% | Depth | ✅ PASS |
| 23 | DeMar DeRozan | 2016-17 | Not Franchise Cornerstone | Bulldozer (High) [Depth] | Bulldozer (Fragile Star) | 80.51% | 1.70% | Franchise Cornerstone | ❌ FAIL |
| 24 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Bulldozer (Fragile Star) | 55.00% | 19.02% | Depth | ❌ FAIL |
| 25 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 6.89% | Depth | ✅ PASS |
| 26 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Bulldozer (Fragile Star) | 55.00% | 1.78% | Depth | ❌ FAIL |
| 27 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 0.00% | 73.29% | Avoid | ✅ PASS |
| 28 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | Victim (Fragile Role) | 5.28% | 8.16% | Depth | ❌ FAIL |
| 29 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 55.00% | 58.18% | Depth | ❌ FAIL |
| 30 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 56.46% | Depth | ✅ PASS |
| 31 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 62.67% | Depth | ✅ PASS |
| 32 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 60.41% | Depth | ✅ PASS |
| 33 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 25.28% | Depth | ✅ PASS |
| 34 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 64.15% | Depth | ✅ PASS |
| 35 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 23.66% | Depth | ✅ PASS |
| 36 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 60.65% | Depth | ✅ PASS |
| 37 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 61.29% | Depth | ✅ PASS |
| 38 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 28.88% | Depth | ✅ PASS |
| 39 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 1.66% | 71.15% | Avoid | ✅ PASS |
| 40 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 17.02% | Depth | ✅ PASS |
| 41 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 34.30% | Depth | ✅ PASS |
| 42 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 60.00% | Depth | ✅ PASS |

## Notes

### Failed Tests

**Shai Gilgeous-Alexander (2018-19)**: Expected high performance (≥65%), got 55.00%

**Victor Oladipo (2016-17)**: Expected high performance (≥65%), got 7.75%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Jalen Brunson (2020-21)**: Expected high performance (≥65%), got 55.00%

**Tyrese Maxey (2021-22)**: Expected high performance (≥65%), got 55.00%

**Pascal Siakam (2018-19)**: Expected high performance (≥65%), got 55.00%

**Jayson Tatum (2017-18)**: Expected high performance (≥65%), got 4.34%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Mikal Bridges (2021-22)**: Expected high performance (≥65%), got 55.00%

**Desmond Bane (2021-22)**: Expected high performance (≥65%), got 55.00%

**Nikola Jokić (2015-16)**: Expected high performance (≥65%), got 55.00%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 55.00%

**Nikola Jokić (2016-17)**: Expected high performance (≥65%), got 55.00%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 55.00%

**Nikola Jokić (2017-18)**: Expected high performance (≥65%), got 5.72%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 5.72%

**Nikola Jokić (2018-19)**: Expected high performance (≥65%), got 55.00%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 55.00%

**Anthony Davis (2015-16)**: Expected high performance (≥65%), got 4.82%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 4.82%

**Anthony Davis (2016-17)**: Expected high performance (≥65%), got 55.00%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 55.00%

**Joel Embiid (2016-17)**: Expected high performance (≥65%), got 36.33%; Expected risk category 'Franchise Cornerstone', got 'Luxury Component'; Risk category matches but performance doesn't: 36.33%

**Joel Embiid (2017-18)**: Expected high performance (≥65%), got 5.83%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 5.83%

**Jordan Poole (2021-22)**: Expected low performance (<55%), got 55.00%; Expected risk category 'Luxury Component', got 'Depth'; Risk category matches but performance doesn't: 55.00%

**Talen Horton-Tucker (2020-21)**: Expected low performance (<55%), got 55.00%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**D'Angelo Russell (2018-19)**: Expected low performance (<55%), got 55.00%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**DeMar DeRozan (2016-17)**: Expected risk category 'Depth', got 'Franchise Cornerstone'

**Ben Simmons (2017-18)**: Expected low performance (<55%), got 55.00%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Ben Simmons (2020-21)**: Expected low performance (<55%), got 55.00%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Domantas Sabonis (2021-22)**: Expected risk category 'Luxury Component', got 'Depth'

**Tyrese Haliburton (2021-22)**: Expected high performance (≥65%), got 55.00%; Expected risk category 'Franchise Cornerstone', got 'Depth'; Risk category matches but performance doesn't: 55.00%

