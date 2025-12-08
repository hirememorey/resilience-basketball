# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-08 15:48:57

## Executive Summary

- **Total Test Cases**: 32
- **Data Found**: 32
- **Passed**: 29
- **Failed**: 3
- **Pass Rate**: 90.6%

## Results by Category

### True Positive
- **Total**: 9
- **Passed**: 9
- **Failed**: 0
- **Pass Rate**: 100.0%

### False Positive
- **Total**: 5
- **Passed**: 4
- **Failed**: 1
- **Pass Rate**: 80.0%

### True Negative
- **Total**: 17
- **Passed**: 15
- **Failed**: 2
- **Pass Rate**: 88.2%

### System Player
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Performance | Dependence | Risk Category | Pass |
|------|--------|--------|----------|----------|-----------|-------------|------------|---------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 97.52% | 27.10% | Franchise Cornerstone | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 92.19% | 44.50% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 99.67% | 31.31% | Franchise Cornerstone | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 93.92% | 30.53% | Franchise Cornerstone | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 72.19% | 47.63% | Luxury Component | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | King (Resilient Star) | 82.60% | 45.60% | Luxury Component | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 99.58% | 62.36% | Luxury Component | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 89.35% | 51.90% | Luxury Component | ✅ PASS |
| 9 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 98.20% | 46.11% | Luxury Component | ✅ PASS |
| 10 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 30.00% | N/A | Moderate Performance, Moderate Dependence | ✅ PASS |
| 11 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 61.21% | Avoid | ✅ PASS |
| 12 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | King (Resilient Star) | 95.66% | 22.14% | Franchise Cornerstone | ❌ FAIL |
| 13 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 0.00% | 35.02% | Depth | ✅ PASS |
| 14 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | King (Resilient Star) | 60.27% | 22.68% | Moderate Performance, Low Dependence | ❌ FAIL |
| 15 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 33.87% | Moderate Performance, Low Dependence | ✅ PASS |
| 16 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 43.73% | 34.30% | Moderate Performance, Low Dependence | ✅ PASS |
| 17 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 0.00% | 34.63% | Depth | ✅ PASS |
| 18 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | Victim (Fragile Role) | 30.00% | 60.37% | Luxury Component | ✅ PASS |
| 19 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 92.92% | 28.55% | Franchise Cornerstone | ✅ PASS |
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
| 32 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 73.57% | 26.60% | Franchise Cornerstone | ❌ FAIL |

## Notes

### Failed Tests

**D'Angelo Russell (2018-19)**: Expected low performance (<55%), got 95.66%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Ben Simmons (2017-18)**: Expected low performance (<55%), got 60.27%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2023-24)**: Expected low performance (<55%), got 73.57%; Archetype mismatch: expected Victim, got King (Resilient Star)

