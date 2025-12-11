# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-11 11:54:09

## Executive Summary

- **Total Test Cases**: 40
- **Data Found**: 40
- **Passed**: 20
- **Failed**: 20
- **Pass Rate**: 50.0%

## Results by Category

### True Positive
- **Total**: 17
- **Passed**: 8
- **Failed**: 9
- **Pass Rate**: 47.1%

### False Positive
- **Total**: 5
- **Passed**: 2
- **Failed**: 3
- **Pass Rate**: 40.0%

### True Negative
- **Total**: 17
- **Passed**: 9
- **Failed**: 8
- **Pass Rate**: 52.9%

### System Player
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Performance | Dependence | Risk Category | Pass |
|------|--------|--------|----------|----------|-----------|-------------|------------|---------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 99.62% | 41.85% | Luxury Component | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 99.21% | 49.02% | Luxury Component | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 99.82% | 35.21% | Depth Piece | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 89.46% | 33.64% | Depth Piece | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 90.62% | 54.66% | Luxury Component | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | Bulldozer (Fragile Star) | 91.61% | 42.19% | Luxury Component | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 99.72% | 51.63% | Luxury Component | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 88.83% | 58.32% | Luxury Component | ✅ PASS |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Victim (Fragile Role) | 0.00% | 65.77% | Avoid | ❌ FAIL |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 71.28% | 61.94% | Avoid | ❌ FAIL |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 99.43% | 56.94% | Luxury Component | ❌ FAIL |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 68.62% | 48.83% | Avoid | ❌ FAIL |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Victim (Fragile Role) | 0.00% | 51.66% | Avoid | ❌ FAIL |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 97.36% | 43.33% | Luxury Component | ❌ FAIL |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 99.58% | 54.24% | Luxury Component | ❌ FAIL |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Victim (Fragile Role) | 0.00% | 52.87% | Avoid | ❌ FAIL |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | King (Resilient Star) | 98.16% | 39.23% | Depth Piece | ❌ FAIL |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | King (Resilient Star) | 64.03% | 49.55% | Avoid | ❌ FAIL |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 34.35% | 57.61% | Avoid | ✅ PASS |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Victim (Fragile Role) | 0.00% | 23.57% | Depth Piece | ✅ PASS |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | King (Resilient Star) | 71.13% | 32.55% | Depth Piece | ❌ FAIL |
| 22 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 46.10% | 23.15% | Depth Piece | ✅ PASS |
| 23 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 15.37% | 38.64% | Depth Piece | ✅ PASS |
| 24 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | King (Resilient Star) | 64.46% | 34.61% | Depth Piece | ❌ FAIL |
| 25 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 0.00% | 47.71% | Avoid | ✅ PASS |
| 26 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | Victim (Fragile Role) | 0.00% | 63.57% | Avoid | ❌ FAIL |
| 27 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | Victim (Fragile Role) | 0.00% | 35.43% | Depth Piece | ❌ FAIL |
| 28 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 93.80% | 63.82% | Luxury Component | ❌ FAIL |
| 29 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 64.09% | Avoid | ✅ PASS |
| 30 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 0.00% | 66.90% | Avoid | ✅ PASS |
| 31 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 94.92% | 55.74% | Luxury Component | ❌ FAIL |
| 32 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 76.67% | 60.26% | Avoid | ❌ FAIL |
| 33 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 89.17% | 57.89% | Luxury Component | ❌ FAIL |
| 34 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 28.68% | 52.01% | Avoid | ✅ PASS |
| 35 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 11.12% | 38.04% | Depth Piece | ✅ PASS |
| 36 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 55.31% | 43.38% | Avoid | ❌ FAIL |
| 37 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 20.11% | 30.03% | Depth Piece | ✅ PASS |
| 38 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 49.46% | 36.35% | Depth Piece | ✅ PASS |
| 39 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 96.22% | 34.12% | Depth Piece | ❌ FAIL |
| 40 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 5.96% | 29.57% | Depth Piece | ✅ PASS |

## Notes

### Failed Tests

**Nikola Jokić (2015-16)**: Expected high performance (≥65%), got 0.00%; Expected risk category 'Franchise Cornerstone', got 'Avoid'; Risk category matches but performance doesn't: 0.00%

**Nikola Jokić (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Avoid'

**Nikola Jokić (2017-18)**: Expected risk category 'Franchise Cornerstone', got 'Luxury Component'

**Nikola Jokić (2018-19)**: Expected risk category 'Franchise Cornerstone', got 'Avoid'

**Anthony Davis (2015-16)**: Expected high performance (≥65%), got 0.00%; Expected risk category 'Franchise Cornerstone', got 'Avoid'; Risk category matches but performance doesn't: 0.00%

**Anthony Davis (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Luxury Component'

**Joel Embiid (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Luxury Component'

**Joel Embiid (2017-18)**: Expected high performance (≥65%), got 0.00%; Expected risk category 'Franchise Cornerstone', got 'Avoid'; Risk category matches but performance doesn't: 0.00%

**Jordan Poole (2021-22)**: Expected low performance (<55%), got 98.16%; Expected risk category 'Luxury Component', got 'Depth Piece'; Risk category matches but performance doesn't: 98.16%

**Talen Horton-Tucker (2020-21)**: Expected low performance (<55%), got 64.03%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Julius Randle (2020-21)**: Expected low performance (<55%), got 71.13%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Ben Simmons (2020-21)**: Expected low performance (<55%), got 64.46%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Domantas Sabonis (2021-22)**: Expected risk category 'Luxury Component', got 'Avoid'

**Tyrese Haliburton (2021-22)**: Expected high performance (≥65%), got 0.00%; Expected risk category 'Franchise Cornerstone', got 'Depth Piece'; Risk category matches but performance doesn't: 0.00%

**Karl-Anthony Towns (2015-16)**: Expected low performance (<55%), got 93.80%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Karl-Anthony Towns (2018-19)**: Expected low performance (<55%), got 94.92%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Karl-Anthony Towns (2019-20)**: Expected low performance (<55%), got 76.67%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Karl-Anthony Towns (2020-21)**: Expected low performance (<55%), got 89.17%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2019-20)**: Expected low performance (<55%), got 55.31%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2022-23)**: Expected low performance (<55%), got 96.22%; Archetype mismatch: expected Victim, got King (Resilient Star)

