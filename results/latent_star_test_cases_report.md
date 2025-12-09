# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-09 11:27:22

## Executive Summary

- **Total Test Cases**: 40
- **Data Found**: 40
- **Passed**: 31
- **Failed**: 9
- **Pass Rate**: 77.5%

## Results by Category

### True Positive
- **Total**: 17
- **Passed**: 17
- **Failed**: 0
- **Pass Rate**: 100.0%

### False Positive
- **Total**: 5
- **Passed**: 1
- **Failed**: 4
- **Pass Rate**: 20.0%

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
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 96.04% | 27.10% | Franchise Cornerstone | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 95.06% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 99.52% | 31.31% | Franchise Cornerstone | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 93.81% | 30.53% | Franchise Cornerstone | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 76.76% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | King (Resilient Star) | 70.13% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 99.48% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 86.76% | 42.29% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 97.45% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 98.82% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 96.67% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 90.83% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 96.56% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 98.55% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 96.13% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 94.36% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 98.79% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 30.00% | N/A | Moderate Performance, Moderate Dependence | ✅ PASS |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Bulldozer (Fragile Star) | 72.81% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | King (Resilient Star) | 96.57% | 20.64% | Franchise Cornerstone | ❌ FAIL |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | King (Resilient Star) | 88.05% | 35.02% | Franchise Cornerstone | ❌ FAIL |
| 22 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | King (Resilient Star) | 54.63% | 22.68% | Moderate Performance, Low Dependence | ✅ PASS |
| 23 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 33.87% | Moderate Performance, Low Dependence | ✅ PASS |
| 24 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 46.88% | 34.30% | Moderate Performance, Low Dependence | ✅ PASS |
| 25 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 0.00% | 32.41% | Depth | ✅ PASS |
| 26 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 74.52% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 27 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | King (Resilient Star) | 79.68% | 28.57% | Franchise Cornerstone | ✅ PASS |
| 28 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | 40.00% | Moderate Performance, Moderate Dependence | ✅ PASS |
| 29 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 72.95% | 40.00% | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 30 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 31 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 32 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 40.00% | Depth (Moderate Dependence) | ✅ PASS |
| 33 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 59.68% | 40.00% | Moderate Performance, Moderate Dependence | ❌ FAIL |
| 34 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | N/A | Moderate Performance, Moderate Dependence | ✅ PASS |
| 35 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 26.08% | 27.88% | Depth | ✅ PASS |
| 36 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 47.98% | 27.19% | Moderate Performance, Low Dependence | ✅ PASS |
| 37 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 17.06% | Moderate Performance, Low Dependence | ✅ PASS |
| 38 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | 15.77% | Moderate Performance, Low Dependence | ✅ PASS |
| 39 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 62.74% | 27.25% | Moderate Performance, Low Dependence | ❌ FAIL |
| 40 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 78.84% | 26.60% | Franchise Cornerstone | ❌ FAIL |

## Notes

### Failed Tests

**Jordan Poole (2021-22)**: Expected low performance (<55%), got 98.79%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone (Moderate Dependence)'; Risk category matches but performance doesn't: 98.79%

**Christian Wood (2020-21)**: Expected low performance (<55%), got 72.81%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**D'Angelo Russell (2018-19)**: Expected low performance (<55%), got 96.57%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Julius Randle (2020-21)**: Expected low performance (<55%), got 88.05%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Domantas Sabonis (2021-22)**: Expected low performance (<55%), got 74.52%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone (Moderate Dependence)'; Risk category matches but performance doesn't: 74.52%

**Karl-Anthony Towns (2016-17)**: Expected low performance (<55%), got 72.95%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Karl-Anthony Towns (2020-21)**: Expected low performance (<55%), got 59.68%

**Markelle Fultz (2022-23)**: Expected low performance (<55%), got 62.74%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2023-24)**: Expected low performance (<55%), got 78.84%; Archetype mismatch: expected Victim, got King (Resilient Star)

