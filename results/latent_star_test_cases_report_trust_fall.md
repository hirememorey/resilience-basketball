# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-09 23:18:30

## Executive Summary

- **Total Test Cases**: 40
- **Data Found**: 40
- **Passed**: 27
- **Failed**: 13
- **Pass Rate**: 67.5%

## Results by Category

### True Positive
- **Total**: 17
- **Passed**: 17
- **Failed**: 0
- **Pass Rate**: 100.0%

### False Positive
- **Total**: 5
- **Passed**: 3
- **Failed**: 2
- **Pass Rate**: 60.0%

### True Negative
- **Total**: 17
- **Passed**: 6
- **Failed**: 11
- **Pass Rate**: 35.3%

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
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 97.48% | 51.90% | Luxury Component | ✅ PASS |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 99.48% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 99.54% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 99.19% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 94.59% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 98.54% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 99.51% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 98.97% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 99.09% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 99.56% | 46.11% | Luxury Component | ✅ PASS |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 36.03% | N/A | Moderate Performance (Dependence Unknown) | ✅ PASS |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 53.47% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | King (Resilient Star) | 97.96% | 22.14% | Franchise Cornerstone | ❌ FAIL |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | King (Resilient Star) | 97.37% | 35.02% | Franchise Cornerstone | ❌ FAIL |
| 22 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | King (Resilient Star) | 55.19% | 22.68% | Moderate Performance, Low Dependence | ❌ FAIL |
| 23 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | King (Resilient Star) | 68.28% | 33.87% | Moderate Performance, Low Dependence | ❌ FAIL |
| 24 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 44.64% | 34.30% | Moderate Performance, Low Dependence | ✅ PASS |
| 25 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 42.77% | 34.63% | Moderate Performance, Low Dependence | ✅ PASS |
| 26 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 84.20% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 27 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | King (Resilient Star) | 93.62% | 28.55% | Franchise Cornerstone | ✅ PASS |
| 28 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 95.90% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 29 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 56.89% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 30 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 63.05% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 31 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 48.96% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 32 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 84.17% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 33 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 49.52% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 34 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 47.03% | N/A | Moderate Performance (Dependence Unknown) | ✅ PASS |
| 35 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 26.31% | 27.88% | Depth | ✅ PASS |
| 36 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 74.41% | 27.19% | Franchise Cornerstone | ❌ FAIL |
| 37 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 34.41% | 17.06% | Moderate Performance, Low Dependence | ✅ PASS |
| 38 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 83.70% | 15.77% | Franchise Cornerstone | ❌ FAIL |
| 39 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 71.78% | 27.25% | Franchise Cornerstone | ❌ FAIL |
| 40 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 73.07% | 26.60% | Franchise Cornerstone | ❌ FAIL |

## Notes

### Failed Tests

**D'Angelo Russell (2018-19)**: Expected low performance (<55%), got 97.96%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Julius Randle (2020-21)**: Expected low performance (<55%), got 97.37%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Ben Simmons (2017-18)**: Expected low performance (<55%), got 55.19%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Ben Simmons (2018-19)**: Expected low performance (<55%), got 68.28%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Domantas Sabonis (2021-22)**: Expected low performance (<55%), got 84.20%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone (Moderate Dependence)'; Risk category matches but performance doesn't: 84.20%

**Karl-Anthony Towns (2015-16)**: Expected low performance (<55%), got 95.90%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Karl-Anthony Towns (2016-17)**: Expected low performance (<55%), got 56.89%

**Karl-Anthony Towns (2017-18)**: Expected low performance (<55%), got 63.05%

**Karl-Anthony Towns (2019-20)**: Expected low performance (<55%), got 84.17%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Markelle Fultz (2019-20)**: Expected low performance (<55%), got 74.41%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2021-22)**: Expected low performance (<55%), got 83.70%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2022-23)**: Expected low performance (<55%), got 71.78%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2023-24)**: Expected low performance (<55%), got 73.07%; Archetype mismatch: expected Victim, got King (Resilient Star)

