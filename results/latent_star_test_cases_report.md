# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-09 23:18:31

## Executive Summary

- **Total Test Cases**: 40
- **Data Found**: 40
- **Passed**: 34
- **Failed**: 6
- **Pass Rate**: 85.0%

## Results by Category

### True Positive
- **Total**: 17
- **Passed**: 16
- **Failed**: 1
- **Pass Rate**: 94.1%

### False Positive
- **Total**: 5
- **Passed**: 5
- **Failed**: 0
- **Pass Rate**: 100.0%

### True Negative
- **Total**: 17
- **Passed**: 12
- **Failed**: 5
- **Pass Rate**: 70.6%

### System Player
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Performance | Dependence | Risk Category | Pass |
|------|--------|--------|----------|----------|-----------|-------------|------------|---------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 98.11% | 27.10% | Franchise Cornerstone | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 97.75% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 99.65% | 31.31% | Franchise Cornerstone | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 97.79% | 30.53% | Franchise Cornerstone | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 86.11% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | King (Resilient Star) | 71.10% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 99.70% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 88.42% | 51.90% | Luxury Component | ✅ PASS |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 98.06% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 99.49% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 98.96% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 94.59% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 98.54% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Victim (Fragile Role) | 30.00% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 98.97% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 99.09% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Victim (Fragile Role) | 30.00% | 46.11% | Luxury Component | ✅ PASS |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 30.00% | N/A | Moderate Performance (Dependence Unknown) | ✅ PASS |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 30.00% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Victim (Fragile Role) | 30.00% | 22.14% | Moderate Performance, Low Dependence | ✅ PASS |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 30.00% | 35.02% | Moderate Performance, Low Dependence | ✅ PASS |
| 22 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | King (Resilient Star) | 55.19% | 22.68% | Moderate Performance, Low Dependence | ❌ FAIL |
| 23 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 33.87% | Moderate Performance, Low Dependence | ✅ PASS |
| 24 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 44.64% | 34.30% | Moderate Performance, Low Dependence | ✅ PASS |
| 25 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 42.77% | 34.63% | Moderate Performance, Low Dependence | ✅ PASS |
| 26 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 73.64% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 27 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | King (Resilient Star) | 93.62% | 28.55% | Franchise Cornerstone | ✅ PASS |
| 28 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 29 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 30 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 31 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 32 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 33 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 49.52% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 34 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | N/A | Moderate Performance (Dependence Unknown) | ✅ PASS |
| 35 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 26.31% | 27.88% | Depth | ✅ PASS |
| 36 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 74.41% | 27.19% | Franchise Cornerstone | ❌ FAIL |
| 37 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 17.06% | Moderate Performance, Low Dependence | ✅ PASS |
| 38 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 15.77% | Moderate Performance, Low Dependence | ✅ PASS |
| 39 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 71.78% | 27.25% | Franchise Cornerstone | ❌ FAIL |
| 40 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 73.07% | 26.60% | Franchise Cornerstone | ❌ FAIL |

## Notes

### Failed Tests

**Anthony Davis (2016-17)**: Expected high performance (≥65%), got 30.00%; Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Moderate Dependence'; Risk category matches but performance doesn't: 30.00%

**Ben Simmons (2017-18)**: Expected low performance (<55%), got 55.19%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Domantas Sabonis (2021-22)**: Expected low performance (<55%), got 73.64%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone (Moderate Dependence)'; Risk category matches but performance doesn't: 73.64%

**Markelle Fultz (2019-20)**: Expected low performance (<55%), got 74.41%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2022-23)**: Expected low performance (<55%), got 71.78%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2023-24)**: Expected low performance (<55%), got 73.07%; Archetype mismatch: expected Victim, got King (Resilient Star)

