# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-12 10:33:18

## Executive Summary

- **Total Test Cases**: 40
- **Data Found**: 40
- **Passed**: 35
- **Failed**: 5
- **Pass Rate**: 87.5%

## Results by Category

### True Positive
- **Total**: 17
- **Passed**: 13
- **Failed**: 4
- **Pass Rate**: 76.5%

### False Positive
- **Total**: 5
- **Passed**: 5
- **Failed**: 0
- **Pass Rate**: 100.0%

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
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 0.00% | 27.10% | Depth | ❌ FAIL |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 92.19% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 0.00% | 31.31% | Depth | ❌ FAIL |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 0.00% | 30.53% | Depth | ❌ FAIL |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 72.19% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | King (Resilient Star) | 82.60% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 99.58% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 0.00% | 51.90% | Avoid | ❌ FAIL |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 99.40% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 99.37% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 98.60% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 90.07% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 94.16% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 98.61% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 97.09% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 95.48% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 99.37% | 46.11% | Luxury Component | ✅ PASS |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 30.00% | N/A | Moderate Performance (Dependence Unknown) | ✅ PASS |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | King (Resilient Star) | 0.00% | 22.14% | Depth | ✅ PASS |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 35.02% | Depth | ✅ PASS |
| 22 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | King (Resilient Star) | 0.00% | 22.68% | Depth | ✅ PASS |
| 23 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 33.87% | Depth | ✅ PASS |
| 24 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 34.30% | Depth | ✅ PASS |
| 25 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 0.00% | 34.63% | Depth | ✅ PASS |
| 26 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | King (Resilient Star) | 78.06% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 27 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 92.92% | 28.55% | Franchise Cornerstone | ✅ PASS |
| 28 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 29 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 30 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 31 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 32 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 33 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 34 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | N/A | Low Performance (Dependence Unknown) | ✅ PASS |
| 35 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 27.88% | Depth | ✅ PASS |
| 36 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 27.19% | Depth | ✅ PASS |
| 37 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 17.06% | Moderate Performance, Low Dependence | ✅ PASS |
| 38 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 15.77% | Moderate Performance, Low Dependence | ✅ PASS |
| 39 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 27.25% | Depth | ✅ PASS |
| 40 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 0.00% | 26.60% | Depth | ✅ PASS |

## Notes

### Failed Tests

**Shai Gilgeous-Alexander (2018-19)**: Expected high performance (≥65%), got 0.00%

**Jalen Brunson (2020-21)**: Expected high performance (≥65%), got 0.00%

**Tyrese Maxey (2021-22)**: Expected high performance (≥65%), got 0.00%

**Desmond Bane (2021-22)**: Expected high performance (≥65%), got 0.00%

**Domantas Sabonis (2021-22)**: Expected low performance (<55%), got 78.06%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone (Moderate Dependence)'; Risk category matches but performance doesn't: 78.06%

