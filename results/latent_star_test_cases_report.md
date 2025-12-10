# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-10 14:45:00

## Executive Summary

- **Total Test Cases**: 40
- **Data Found**: 40
- **Passed**: 28
- **Failed**: 12
- **Pass Rate**: 70.0%

## Results by Category

### True Positive
- **Total**: 17
- **Passed**: 10
- **Failed**: 7
- **Pass Rate**: 58.8%

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
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 58.55% | 27.56% | Moderate Performance, Low Dependence | ❌ FAIL |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 93.42% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 89.37% | 31.31% | Franchise Cornerstone | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 99.10% | 30.53% | Franchise Cornerstone | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 85.52% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | King (Resilient Star) | 93.72% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Victim (Fragile Role) | 36.20% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 63.77% | 52.06% | Luxury Component | ❌ FAIL |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 89.90% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 66.20% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 85.95% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 84.90% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 40.00% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Victim (Fragile Role) | 30.00% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 40.00% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 86.97% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Victim (Fragile Role) | 30.00% | 46.20% | Luxury Component | ✅ PASS |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 20.15% | N/A | Low Performance (Dependence Unknown) | ✅ PASS |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 30.00% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Bulldozer (Fragile Star) | 99.15% | 22.61% | Franchise Cornerstone | ❌ FAIL |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 30.00% | 38.30% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 22 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 52.54% | 24.88% | Moderate Performance, Low Dependence | ✅ PASS |
| 23 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 35.72% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 24 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 39.83% | 36.07% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 25 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 47.54% | 34.63% | Moderate Performance, Low Dependence | ✅ PASS |
| 26 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | Victim (Fragile Role) | 54.16% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 27 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 93.77% | 28.74% | Franchise Cornerstone | ✅ PASS |
| 28 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 29 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 30 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 31 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 32 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 33 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 88.54% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 34 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | N/A | Moderate Performance (Dependence Unknown) | ✅ PASS |
| 35 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 28.74% | Moderate Performance, Low Dependence | ✅ PASS |
| 36 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 51.01% | 27.85% | Moderate Performance, Low Dependence | ✅ PASS |
| 37 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 17.06% | Moderate Performance, Low Dependence | ✅ PASS |
| 38 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 17.39% | Moderate Performance, Low Dependence | ✅ PASS |
| 39 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 75.65% | 28.71% | Franchise Cornerstone | ❌ FAIL |
| 40 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 86.91% | 28.73% | Franchise Cornerstone | ❌ FAIL |

## Notes

### Failed Tests

**Shai Gilgeous-Alexander (2018-19)**: Expected high performance (≥65%), got 58.55%

**Mikal Bridges (2021-22)**: Expected high performance (≥65%), got 36.20%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Desmond Bane (2021-22)**: Expected high performance (≥65%), got 63.77%

**Nikola Jokić (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Moderate Dependence'

**Anthony Davis (2015-16)**: Expected high performance (≥65%), got 40.00%; Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Moderate Dependence'; Risk category matches but performance doesn't: 40.00%

**Anthony Davis (2016-17)**: Expected high performance (≥65%), got 30.00%; Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Moderate Dependence'; Risk category matches but performance doesn't: 30.00%

**Joel Embiid (2016-17)**: Expected high performance (≥65%), got 40.00%; Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Moderate Dependence'; Risk category matches but performance doesn't: 40.00%

**D'Angelo Russell (2018-19)**: Expected low performance (<55%), got 99.15%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Domantas Sabonis (2021-22)**: Expected risk category 'Luxury Component', got 'Moderate Performance, Moderate Dependence'

**Karl-Anthony Towns (2020-21)**: Expected low performance (<55%), got 88.54%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Markelle Fultz (2022-23)**: Expected low performance (<55%), got 75.65%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2023-24)**: Expected low performance (<55%), got 86.91%; Archetype mismatch: expected Victim, got King (Resilient Star)

