# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-10 17:48:02

## Executive Summary

- **Total Test Cases**: 40
- **Data Found**: 40
- **Passed**: 18
- **Failed**: 22
- **Pass Rate**: 45.0%

## Results by Category

### True Positive
- **Total**: 17
- **Passed**: 11
- **Failed**: 6
- **Pass Rate**: 64.7%

### False Positive
- **Total**: 5
- **Passed**: 1
- **Failed**: 4
- **Pass Rate**: 20.0%

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
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 98.27% | 27.56% | Franchise Cornerstone | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 98.00% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 99.29% | 31.31% | Franchise Cornerstone | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 78.75% | 30.53% | Franchise Cornerstone | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 91.94% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | King (Resilient Star) | 85.20% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | King (Resilient Star) | 68.27% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Victim (Fragile Role) | 47.78% | 52.06% | Luxury Component | ❌ FAIL |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 97.90% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 67.06% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 65.02% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 61.33% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 97.79% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Victim (Fragile Role) | 44.95% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 97.18% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 53.59% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | King (Resilient Star) | 96.39% | 46.20% | Luxury Component | ✅ PASS |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | King (Resilient Star) | 79.25% | N/A | High Performance (Dependence Unknown) | ❌ FAIL |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | King (Resilient Star) | 56.84% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | King (Resilient Star) | 98.39% | 22.61% | Franchise Cornerstone | ❌ FAIL |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | King (Resilient Star) | 97.03% | 38.30% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 22 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 49.57% | 24.88% | Moderate Performance, Low Dependence | ✅ PASS |
| 23 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | King (Resilient Star) | 51.29% | 35.72% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 24 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | King (Resilient Star) | 60.85% | 36.07% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 25 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 27.60% | 34.63% | Depth | ✅ PASS |
| 26 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | King (Resilient Star) | 68.32% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 27 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | King (Resilient Star) | 94.99% | 28.74% | Franchise Cornerstone | ✅ PASS |
| 28 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 94.66% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 29 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 61.38% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 30 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 49.38% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 31 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 49.87% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 32 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 62.52% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 33 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 83.10% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 34 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 53.87% | N/A | Moderate Performance (Dependence Unknown) | ✅ PASS |
| 35 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 57.56% | 28.74% | Moderate Performance, Low Dependence | ❌ FAIL |
| 36 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 68.99% | 27.85% | Moderate Performance, Low Dependence | ❌ FAIL |
| 37 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 62.20% | 17.06% | Moderate Performance, Low Dependence | ❌ FAIL |
| 38 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 75.55% | 17.39% | Franchise Cornerstone | ❌ FAIL |
| 39 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 86.13% | 28.71% | Franchise Cornerstone | ❌ FAIL |
| 40 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 79.13% | 28.73% | Franchise Cornerstone | ❌ FAIL |

## Notes

### Failed Tests

**Desmond Bane (2021-22)**: Expected high performance (≥65%), got 47.78%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Nikola Jokić (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Moderate Dependence'

**Nikola Jokić (2017-18)**: Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Moderate Dependence'

**Nikola Jokić (2018-19)**: Expected high performance (≥65%), got 61.33%; Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Moderate Dependence'; Risk category matches but performance doesn't: 61.33%

**Anthony Davis (2016-17)**: Expected high performance (≥65%), got 44.95%; Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Moderate Dependence'; Risk category matches but performance doesn't: 44.95%

**Joel Embiid (2017-18)**: Expected high performance (≥65%), got 53.59%; Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Moderate Dependence'; Risk category matches but performance doesn't: 53.59%

**Talen Horton-Tucker (2020-21)**: Expected low performance (<55%), got 79.25%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Christian Wood (2020-21)**: Expected low performance (<55%), got 56.84%; Archetype mismatch: expected Victim, got King (Resilient Star)

**D'Angelo Russell (2018-19)**: Expected low performance (<55%), got 98.39%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Julius Randle (2020-21)**: Expected low performance (<55%), got 97.03%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Ben Simmons (2020-21)**: Expected low performance (<55%), got 60.85%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Domantas Sabonis (2021-22)**: Expected low performance (<55%), got 68.32%; Expected risk category 'Luxury Component', got 'Moderate Performance, Moderate Dependence'; Risk category matches but performance doesn't: 68.32%

**Karl-Anthony Towns (2015-16)**: Expected low performance (<55%), got 94.66%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Karl-Anthony Towns (2016-17)**: Expected low performance (<55%), got 61.38%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Karl-Anthony Towns (2019-20)**: Expected low performance (<55%), got 62.52%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Karl-Anthony Towns (2020-21)**: Expected low performance (<55%), got 83.10%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2018-19)**: Expected low performance (<55%), got 57.56%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2019-20)**: Expected low performance (<55%), got 68.99%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2020-21)**: Expected low performance (<55%), got 62.20%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2021-22)**: Expected low performance (<55%), got 75.55%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2022-23)**: Expected low performance (<55%), got 86.13%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2023-24)**: Expected low performance (<55%), got 79.13%; Archetype mismatch: expected Victim, got King (Resilient Star)

