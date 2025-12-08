# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-08 13:10:11

## Executive Summary

- **Total Test Cases**: 32
- **Data Found**: 32
- **Passed**: 29
- **Failed**: 3
- **Pass Rate**: 90.6%

## Results by Category

### True Positive
- **Total**: 9
- **Passed**: 7
- **Failed**: 2
- **Pass Rate**: 77.8%

### False Positive
- **Total**: 5
- **Passed**: 4
- **Failed**: 1
- **Pass Rate**: 80.0%

### True Negative
- **Total**: 17
- **Passed**: 17
- **Failed**: 0
- **Pass Rate**: 100.0%

### System Player
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Performance | Dependence | Risk Category | Pass |
|------|--------|--------|----------|----------|-----------|-------------|------------|---------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 95.66% | 27.10% | Franchise Cornerstone | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 96.87% | 44.50% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 99.28% | 31.31% | Franchise Cornerstone | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 91.12% | 30.53% | Franchise Cornerstone | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 75.61% | 47.63% | Luxury Component | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | Bulldozer (Fragile Star) | 69.37% | 45.60% | Luxury Component | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 98.91% | 62.36% | Luxury Component | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Victim (Fragile Role) | 48.10% | 51.90% | Luxury Component | ❌ FAIL |
| 9 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | King (Resilient Star) | 89.06% | 46.11% | Luxury Component | ✅ PASS |
| 10 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 30.00% | N/A | Moderate Performance, Moderate Dependence | ✅ PASS |
| 11 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 61.21% | Avoid | ✅ PASS |
| 12 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | King (Resilient Star) | 96.77% | 22.14% | Franchise Cornerstone | ❌ FAIL |
| 13 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 35.02% | Depth | ✅ PASS |
| 14 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 50.72% | 22.68% | Moderate Performance, Low Dependence | ✅ PASS |
| 15 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 33.87% | Moderate Performance, Low Dependence | ✅ PASS |
| 16 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 49.89% | 34.30% | Moderate Performance, Low Dependence | ✅ PASS |
| 17 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 0.00% | 34.63% | Depth | ✅ PASS |
| 18 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | Victim (Fragile Role) | 30.00% | 60.37% | Luxury Component | ✅ PASS |
| 19 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | King (Resilient Star) | 58.66% | 28.55% | Moderate Performance, Low Dependence | ❌ FAIL |
| 20 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 66.09% | Luxury Component | ✅ PASS |
| 21 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 62.40% | Avoid | ✅ PASS |
| 22 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 65.31% | Avoid | ✅ PASS |
| 23 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 61.97% | Avoid | ✅ PASS |
| 24 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 62.95% | Avoid | ✅ PASS |
| 25 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 59.27% | Avoid | ✅ PASS |
| 26 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | N/A | Moderate Performance, Moderate Dependence | ✅ PASS |
| 27 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 27.88% | Depth | ✅ PASS |
| 28 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 27.19% | Depth | ✅ PASS |
| 29 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 17.06% | Moderate Performance, Low Dependence | ✅ PASS |
| 30 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 15.77% | Moderate Performance, Low Dependence | ✅ PASS |
| 31 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 0.00% | 27.25% | Depth | ✅ PASS |
| 32 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 34.16% | 26.60% | Moderate Performance, Low Dependence | ✅ PASS |

## Notes

### Failed Tests

**Desmond Bane (2021-22)**: Expected high performance (≥65%), got 48.10%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**D'Angelo Russell (2018-19)**: Expected low performance (<55%), got 96.77%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Tyrese Haliburton (2021-22)**: Expected high performance (≥65%), got 58.66%; Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Low Dependence'; Risk category matches but performance doesn't: 58.66%

