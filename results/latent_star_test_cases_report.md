# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-07 22:52:37

## Executive Summary

- **Total Test Cases**: 32
- **Data Found**: 32
- **Passed**: 26
- **Failed**: 6
- **Pass Rate**: 81.2%

## Results by Category

### True Positive
- **Total**: 9
- **Passed**: 8
- **Failed**: 1
- **Pass Rate**: 88.9%

### False Positive
- **Total**: 5
- **Passed**: 4
- **Failed**: 1
- **Pass Rate**: 80.0%

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

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Performance | Dependence | Risk Category | Pass |
|------|--------|--------|----------|----------|-----------|-------------|------------|---------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 99.16% | 35.83% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 94.71% | 52.44% | Luxury Component | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 99.50% | 39.31% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 84.12% | 30.53% | Franchise Cornerstone | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 94.47% | 50.01% | Luxury Component | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | King (Resilient Star) | 84.97% | 50.52% | Luxury Component | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 99.55% | 62.36% | Luxury Component | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 83.09% | 51.90% | Luxury Component | ✅ PASS |
| 9 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | King (Resilient Star) | 87.62% | 46.11% | Luxury Component | ✅ PASS |
| 10 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 30.00% | N/A | Moderate Performance, Moderate Dependence | ✅ PASS |
| 11 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 30.00% | 63.55% | Moderate Performance, High Dependence | ✅ PASS |
| 12 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Victim (Fragile Role) | 30.00% | 34.11% | Moderate Performance, Low Dependence | ✅ PASS |
| 13 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | King (Resilient Star) | 61.33% | 43.64% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 14 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 45.85% | 29.47% | Moderate Performance, Low Dependence | ✅ PASS |
| 15 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 34.73% | Moderate Performance, Low Dependence | ✅ PASS |
| 16 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 23.98% | 36.50% | Depth (Moderate Dependence) | ✅ PASS |
| 17 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 30.00% | 34.63% | Moderate Performance, Low Dependence | ✅ PASS |
| 18 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | Victim (Fragile Role) | 30.00% | 60.37% | Moderate Performance, High Dependence | ❌ FAIL |
| 19 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | Victim (Fragile Role) | 30.00% | 28.55% | Moderate Performance, Low Dependence | ❌ FAIL |
| 20 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 67.93% | Moderate Performance, High Dependence | ✅ PASS |
| 21 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 64.91% | Moderate Performance, High Dependence | ✅ PASS |
| 22 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 65.95% | Moderate Performance, High Dependence | ✅ PASS |
| 23 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 65.91% | Moderate Performance, High Dependence | ✅ PASS |
| 24 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 65.13% | Moderate Performance, High Dependence | ✅ PASS |
| 25 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 63.71% | Moderate Performance, High Dependence | ✅ PASS |
| 26 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | N/A | Moderate Performance, Moderate Dependence | ✅ PASS |
| 27 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 32.90% | Moderate Performance, Low Dependence | ✅ PASS |
| 28 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 73.04% | 35.34% | Franchise Cornerstone | ❌ FAIL |
| 29 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 27.61% | Moderate Performance, Low Dependence | ✅ PASS |
| 30 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 15.77% | Moderate Performance, Low Dependence | ✅ PASS |
| 31 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 74.87% | 33.75% | Franchise Cornerstone | ❌ FAIL |
| 32 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 66.08% | 30.95% | Moderate Performance, Low Dependence | ❌ FAIL |

## Notes

### Failed Tests

**Julius Randle (2020-21)**: Expected low performance (<55%), got 61.33%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Domantas Sabonis (2021-22)**: Expected risk category 'Luxury Component', got 'Moderate Performance, High Dependence'

**Tyrese Haliburton (2021-22)**: Expected high performance (≥65%), got 30.00%; Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Low Dependence'; Risk category matches but performance doesn't: 30.00%

**Markelle Fultz (2019-20)**: Expected low performance (<55%), got 73.04%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2022-23)**: Expected low performance (<55%), got 74.87%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2023-24)**: Expected low performance (<55%), got 66.08%; Archetype mismatch: expected Victim, got King (Resilient Star)

