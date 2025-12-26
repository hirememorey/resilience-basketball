# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-10 21:45:47

## Executive Summary

- **Total Test Cases**: 40
- **Data Found**: 40
- **Passed**: 20
- **Failed**: 20
- **Pass Rate**: 50.0%

## Results by Category

### True Positive
- **Total**: 17
- **Passed**: 9
- **Failed**: 8
- **Pass Rate**: 52.9%

### False Positive
- **Total**: 5
- **Passed**: 1
- **Failed**: 4
- **Pass Rate**: 20.0%

### True Negative
- **Total**: 17
- **Passed**: 10
- **Failed**: 7
- **Pass Rate**: 58.8%

### System Player
- **Total**: 1
- **Passed**: 0
- **Failed**: 1
- **Pass Rate**: 0.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Performance | Dependence | Risk Category | Pass |
|------|--------|--------|----------|----------|-----------|-------------|------------|---------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 96.91% | 27.56% | Franchise Cornerstone | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 95.77% | 44.72% | Franchise Cornerstone | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 98.77% | 31.31% | Franchise Cornerstone | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 95.95% | 30.53% | Franchise Cornerstone | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 92.34% | 49.12% | Franchise Cornerstone | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | Bulldozer (Fragile Star) | 85.04% | 46.34% | Franchise Cornerstone | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 99.01% | 62.61% | Luxury Component | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 68.10% | 52.06% | Luxury Component | ✅ PASS |
| 9 | Nikola Jokić | 2015-16 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Victim (Fragile Role) | 13.77% | 64.09% | Avoid | ❌ FAIL |
| 10 | Nikola Jokić | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Victim (Fragile Role) | 26.21% | 61.33% | Avoid | ❌ FAIL |
| 11 | Nikola Jokić | 2017-18 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | King (Resilient Star) | 96.26% | 60.60% | Luxury Component | ❌ FAIL |
| 12 | Nikola Jokić | 2018-19 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Victim (Fragile Role) | 22.63% | 56.58% | Avoid | ❌ FAIL |
| 13 | Anthony Davis | 2015-16 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 96.40% | 62.47% | Luxury Component | ❌ FAIL |
| 14 | Anthony Davis | 2016-17 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 95.40% | 59.64% | Luxury Component | ❌ FAIL |
| 15 | Joel Embiid | 2016-17 | True Positive - Franchise Cornerstone | King (High) [Franchise Cornerstone] | Bulldozer (Fragile Star) | 96.03% | 64.37% | Luxury Component | ❌ FAIL |
| 16 | Joel Embiid | 2017-18 | True Positive - Franchise Cornerstone | Bulldozer (High) [Franchise Cornerstone] | King (Resilient Star) | 94.22% | 60.09% | Luxury Component | ❌ FAIL |
| 17 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 94.87% | 46.20% | Franchise Cornerstone | ❌ FAIL |
| 18 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | King (Resilient Star) | 81.78% | N/A | High Performance (Dependence Unknown) | ❌ FAIL |
| 19 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 50.40% | 61.94% | Avoid | ✅ PASS |
| 20 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Bulldozer (Fragile Star) | 95.47% | 22.61% | Franchise Cornerstone | ❌ FAIL |
| 21 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | Bulldozer (Fragile Star) | 87.70% | 38.30% | Franchise Cornerstone | ❌ FAIL |
| 22 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 12.42% | 24.88% | Depth Piece | ✅ PASS |
| 23 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 36.31% | 35.72% | Depth Piece | ✅ PASS |
| 24 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | King (Resilient Star) | 53.40% | 36.07% | Depth Piece | ✅ PASS |
| 25 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | King (Resilient Star) | 68.56% | 34.63% | Franchise Cornerstone | ❌ FAIL |
| 26 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | King (Resilient Star) | 82.27% | 60.94% | Luxury Component | ✅ PASS |
| 27 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | King (Resilient Star) | 84.96% | 28.74% | Franchise Cornerstone | ✅ PASS |
| 28 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 91.66% | 67.19% | Luxury Component | ❌ FAIL |
| 29 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 74.50% | 64.35% | Luxury Component | ❌ FAIL |
| 30 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 84.81% | 66.28% | Luxury Component | ❌ FAIL |
| 31 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 77.30% | 64.60% | Luxury Component | ❌ FAIL |
| 32 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 69.61% | 64.20% | Luxury Component | ❌ FAIL |
| 33 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 50.33% | 61.38% | Avoid | ✅ PASS |
| 34 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 33.83% | N/A | Low Performance (Dependence Unknown) | ✅ PASS |
| 35 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 22.07% | 28.74% | Depth Piece | ✅ PASS |
| 36 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 37.28% | 27.85% | Depth Piece | ✅ PASS |
| 37 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 42.19% | 17.06% | Depth Piece | ✅ PASS |
| 38 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 41.48% | 17.39% | Depth Piece | ✅ PASS |
| 39 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 67.12% | 28.71% | Franchise Cornerstone | ❌ FAIL |
| 40 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 66.70% | 28.73% | Franchise Cornerstone | ❌ FAIL |

## Notes

### Failed Tests

**Nikola Jokić (2015-16)**: Expected high performance (≥65%), got 13.77%; Expected risk category 'Franchise Cornerstone', got 'Avoid'; Risk category matches but performance doesn't: 13.77%

**Nikola Jokić (2016-17)**: Expected high performance (≥65%), got 26.21%; Expected risk category 'Franchise Cornerstone', got 'Avoid'; Risk category matches but performance doesn't: 26.21%

**Nikola Jokić (2017-18)**: Expected risk category 'Franchise Cornerstone', got 'Luxury Component'

**Nikola Jokić (2018-19)**: Expected high performance (≥65%), got 22.63%; Expected risk category 'Franchise Cornerstone', got 'Avoid'; Risk category matches but performance doesn't: 22.63%

**Anthony Davis (2015-16)**: Expected risk category 'Franchise Cornerstone', got 'Luxury Component'

**Anthony Davis (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Luxury Component'

**Joel Embiid (2016-17)**: Expected risk category 'Franchise Cornerstone', got 'Luxury Component'

**Joel Embiid (2017-18)**: Expected risk category 'Franchise Cornerstone', got 'Luxury Component'

**Jordan Poole (2021-22)**: Expected low performance (<55%), got 94.87%; Expected risk category 'Luxury Component', got 'Franchise Cornerstone'; Risk category matches but performance doesn't: 94.87%

**Talen Horton-Tucker (2020-21)**: Expected low performance (<55%), got 81.78%; Archetype mismatch: expected Victim, got King (Resilient Star)

**D'Angelo Russell (2018-19)**: Expected low performance (<55%), got 95.47%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Julius Randle (2020-21)**: Expected low performance (<55%), got 87.70%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Tyus Jones (2021-22)**: Expected low performance (<55%), got 68.56%; Archetype mismatch: expected Sniper, got King (Resilient Star)

**Karl-Anthony Towns (2015-16)**: Expected low performance (<55%), got 91.66%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Karl-Anthony Towns (2016-17)**: Expected low performance (<55%), got 74.50%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Karl-Anthony Towns (2017-18)**: Expected low performance (<55%), got 84.81%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Karl-Anthony Towns (2018-19)**: Expected low performance (<55%), got 77.30%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Karl-Anthony Towns (2019-20)**: Expected low performance (<55%), got 69.61%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2022-23)**: Expected low performance (<55%), got 67.12%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2023-24)**: Expected low performance (<55%), got 66.70%; Archetype mismatch: expected Victim, got King (Resilient Star)

