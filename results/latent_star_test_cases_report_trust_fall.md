# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-08 09:56:59

## Executive Summary

- **Total Test Cases**: 32
- **Data Found**: 32
- **Passed**: 18
- **Failed**: 14
- **Pass Rate**: 56.2%

## Results by Category

### True Positive
- **Total**: 9
- **Passed**: 8
- **Failed**: 1
- **Pass Rate**: 88.9%

### False Positive
- **Total**: 5
- **Passed**: 2
- **Failed**: 3
- **Pass Rate**: 40.0%

### True Negative
- **Total**: 17
- **Passed**: 7
- **Failed**: 10
- **Pass Rate**: 41.2%

### System Player
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Performance | Dependence | Risk Category | Pass |
|------|--------|--------|----------|----------|-----------|-------------|------------|---------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 96.90% | 27.10% | Franchise Cornerstone | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 96.00% | 44.50% | Franchise Cornerstone (Moderate Dependence) | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 99.13% | 31.31% | Franchise Cornerstone | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 89.61% | 30.53% | Franchise Cornerstone | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 75.36% | 47.63% | Luxury Component | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | King (Resilient Star) | 79.33% | 45.60% | Luxury Component | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 98.86% | 62.36% | Luxury Component | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 78.15% | 51.90% | Luxury Component | ✅ PASS |
| 9 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) [Luxury Component] | Bulldozer (Fragile Star) | 98.32% | 46.11% | Luxury Component | ✅ PASS |
| 10 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | King (Resilient Star) | 95.26% | N/A | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 11 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 26.00% | 61.21% | Avoid | ✅ PASS |
| 12 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | King (Resilient Star) | 97.02% | 22.14% | Franchise Cornerstone | ❌ FAIL |
| 13 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | King (Resilient Star) | 73.66% | 35.02% | Franchise Cornerstone | ❌ FAIL |
| 14 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 44.08% | 22.68% | Moderate Performance, Low Dependence | ✅ PASS |
| 15 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 17.88% | 33.87% | Depth | ✅ PASS |
| 16 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 42.13% | 34.30% | Moderate Performance, Low Dependence | ✅ PASS |
| 17 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 31.26% | 34.63% | Moderate Performance, Low Dependence | ✅ PASS |
| 18 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) [Luxury Component] | King (Resilient Star) | 72.34% | 60.37% | Luxury Component | ✅ PASS |
| 19 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) [Franchise Cornerstone] | King (Resilient Star) | 66.45% | 28.55% | Moderate Performance, Low Dependence | ❌ FAIL |
| 20 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 86.03% | 66.09% | Luxury Component | ❌ FAIL |
| 21 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 64.81% | 62.40% | Moderate Performance, High Dependence | ❌ FAIL |
| 22 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Bulldozer (Fragile Star) | 64.10% | 65.31% | Moderate Performance, High Dependence | ❌ FAIL |
| 23 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 86.51% | 61.97% | Luxury Component | ❌ FAIL |
| 24 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 55.39% | 62.95% | Moderate Performance, High Dependence | ❌ FAIL |
| 25 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | King (Resilient Star) | 57.55% | 59.27% | Moderate Performance, High Dependence | ❌ FAIL |
| 26 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 84.62% | N/A | Franchise Cornerstone (Moderate Dependence) | ❌ FAIL |
| 27 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 51.28% | 27.88% | Moderate Performance, Low Dependence | ✅ PASS |
| 28 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 48.22% | 27.19% | Moderate Performance, Low Dependence | ✅ PASS |
| 29 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 49.77% | 17.06% | Moderate Performance, Low Dependence | ✅ PASS |
| 30 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 63.37% | 15.77% | Moderate Performance, Low Dependence | ❌ FAIL |
| 31 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 79.54% | 27.25% | Franchise Cornerstone | ❌ FAIL |
| 32 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 62.49% | 26.60% | Moderate Performance, Low Dependence | ❌ FAIL |

## Notes

### Failed Tests

**Talen Horton-Tucker (2020-21)**: Expected low performance (<55%), got 95.26%; Archetype mismatch: expected Victim, got King (Resilient Star)

**D'Angelo Russell (2018-19)**: Expected low performance (<55%), got 97.02%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Julius Randle (2020-21)**: Expected low performance (<55%), got 73.66%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Tyrese Haliburton (2021-22)**: Expected risk category 'Franchise Cornerstone', got 'Moderate Performance, Low Dependence'

**Karl-Anthony Towns (2015-16)**: Expected low performance (<55%), got 86.03%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Karl-Anthony Towns (2016-17)**: Expected low performance (<55%), got 64.81%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Karl-Anthony Towns (2017-18)**: Expected low performance (<55%), got 64.10%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Karl-Anthony Towns (2018-19)**: Expected low performance (<55%), got 86.51%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Karl-Anthony Towns (2019-20)**: Expected low performance (<55%), got 55.39%

**Karl-Anthony Towns (2020-21)**: Expected low performance (<55%), got 57.55%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2017-18)**: Expected low performance (<55%), got 84.62%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2021-22)**: Expected low performance (<55%), got 63.37%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2022-23)**: Expected low performance (<55%), got 79.54%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2023-24)**: Expected low performance (<55%), got 62.49%; Archetype mismatch: expected Victim, got King (Resilient Star)

