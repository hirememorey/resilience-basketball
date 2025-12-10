# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-10 10:49:21

## Executive Summary

- **Total Test Cases**: 40
- **Data Found**: 40
- **Passed**: 24
- **Failed**: 16
- **Pass Rate**: 60.0%

## Results by Category

### True Positive
- **Total**: 17
- **Passed**: 14
- **Failed**: 3
- **Pass Rate**: 82.4%

### False Positive
- **Total**: 5
- **Passed**: 4
- **Failed**: 1
- **Pass Rate**: 80.0%

### True Negative
- **Total**: 17
- **Passed**: 5
- **Failed**: 12
- **Pass Rate**: 29.4%

### System Player
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Performance | Dependence | Risk Category | Pass |
|------|--------|--------|----------|----------|-----------|-------------|------------|---------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 79.71% | 27.56% | Franchise Cornerstone | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Victim (Fragile Role) | 55.51% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 94.68% | 31.31% | Franchise Cornerstone | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 87.53% | 30.53% | Franchise Cornerstone | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 93.93% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | King (Resilient Star) | 76.41% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 91.03% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 97.66% | 52.06% | Luxury Component | ✅ PASS |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 89.96% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 78.15% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 83.09% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 86.28% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 60.03% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 78.75% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 67.10% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 83.63% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 87.37% | 46.20% | Luxury Component | ✅ PASS |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 19.36% | N/A | Low Performance (Dependence Unknown) | ✅ PASS |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 55.45% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Victim (Fragile Role) | 38.66% | 22.61% | Moderate Performance, Low Dependence | ✅ PASS |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 46.93% | 38.30% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 22 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 37.88% | 24.88% | Moderate Performance, Low Dependence | ✅ PASS |
| 23 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | King (Resilient Star) | 69.93% | 35.72% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 24 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 43.10% | 36.07% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 25 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 38.23% | 34.63% | Moderate Performance, Low Dependence | ✅ PASS |
| 26 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 80.72% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 27 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 82.30% | 28.74% | Franchise Cornerstone | ✅ PASS |
| 28 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 96.97% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 29 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 77.09% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 30 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 85.62% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 31 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 84.23% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 32 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 88.71% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 33 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 72.22% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 34 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 21.77% | N/A | Low Performance (Dependence Unknown) | ✅ PASS |
| 35 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 24.70% | 28.74% | Depth | ✅ PASS |
| 36 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 68.62% | 27.85% | Moderate Performance, Low Dependence | ❌ FAIL |
| 37 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 35.35% | 17.06% | Moderate Performance, Low Dependence | ✅ PASS |
| 38 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 86.62% | 17.39% | Franchise Cornerstone | ❌ FAIL |
| 39 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 80.54% | 28.71% | Franchise Cornerstone | ❌ FAIL |
| 40 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 86.42% | 28.73% | Franchise Cornerstone | ❌ FAIL |

## Notes

### Failed Tests

**Victor Oladipo (2016-17)**: Expected high performance (≥65%), got 55.51%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Anthony Davis (2015-16)**: Expected high performance (≥65%), got 60.03%; Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Moderate Dependence'; Risk category matches but performance doesn't: 60.03%

**Joel Embiid (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Moderate Dependence'

**Christian Wood (2020-21)**: Expected low performance (<55%), got 55.45%

**Ben Simmons (2018-19)**: Expected low performance (<55%), got 69.93%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Domantas Sabonis (2021-22)**: Expected low performance (<55%), got 80.72%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone (Moderate Dependence)'; Risk category matches but performance doesn't: 80.72%

**Karl-Anthony Towns (2015-16)**: Expected low performance (<55%), got 96.97%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Karl-Anthony Towns (2016-17)**: Expected low performance (<55%), got 77.09%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Karl-Anthony Towns (2017-18)**: Expected low performance (<55%), got 85.62%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Karl-Anthony Towns (2018-19)**: Expected low performance (<55%), got 84.23%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Karl-Anthony Towns (2019-20)**: Expected low performance (<55%), got 88.71%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Karl-Anthony Towns (2020-21)**: Expected low performance (<55%), got 72.22%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Markelle Fultz (2019-20)**: Expected low performance (<55%), got 68.62%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2021-22)**: Expected low performance (<55%), got 86.62%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2022-23)**: Expected low performance (<55%), got 80.54%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2023-24)**: Expected low performance (<55%), got 86.42%; Archetype mismatch: expected Victim, got King (Resilient Star)

