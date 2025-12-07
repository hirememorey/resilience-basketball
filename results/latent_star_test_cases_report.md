# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-07 18:47:12

## Executive Summary

- **Total Test Cases**: 32
- **Data Found**: 32
- **Passed**: 26
- **Failed**: 6
- **Pass Rate**: 81.2%

## Results by Category

### True Positive
- **Total**: 9
- **Passed**: 8
- **Failed**: 1
- **Pass Rate**: 88.9%

### False Positive
- **Total**: 5
- **Passed**: 3
- **Failed**: 2
- **Pass Rate**: 60.0%

### True Negative
- **Total**: 17
- **Passed**: 14
- **Failed**: 3
- **Pass Rate**: 82.4%

### System Player
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Star-Level | Pass |
|------|--------|--------|----------|----------|-----------|------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 99.16% | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 94.71% | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 99.50% | ✅ PASS |
| 4 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 84.12% | ✅ PASS |
| 5 | Pascal Siakam | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 94.47% | ✅ PASS |
| 6 | Jayson Tatum | 2017-18 | True Positive - Rookie Sensation | Bulldozer (High) | King (Resilient Star) | 84.97% | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | True Positive - Usage Shock | Bulldozer (High) | Bulldozer (Fragile Star) | 99.55% | ✅ PASS |
| 8 | Desmond Bane | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 83.09% | ✅ PASS |
| 9 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) | King (Resilient Star) | 87.62% | ❌ FAIL |
| 10 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 11 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 12 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 13 | Julius Randle | 2020-21 | False Positive - Empty Calories | Victim (Low) | King (Resilient Star) | 61.33% | ❌ FAIL |
| 14 | Ben Simmons | 2017-18 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 45.85% | ✅ PASS |
| 15 | Ben Simmons | 2018-19 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 16 | Ben Simmons | 2020-21 | True Negative - Fragile Star | Victim (Low) | Victim (Fragile Role) | 23.98% | ✅ PASS |
| 17 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 18 | Domantas Sabonis | 2021-22 | True Negative - Comparison Case | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 19 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) | Victim (Fragile Role) | 30.00% | ❌ FAIL |
| 20 | Karl-Anthony Towns | 2015-16 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 21 | Karl-Anthony Towns | 2016-17 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 22 | Karl-Anthony Towns | 2017-18 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 23 | Karl-Anthony Towns | 2018-19 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 24 | Karl-Anthony Towns | 2019-20 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 25 | Karl-Anthony Towns | 2020-21 | True Negative - Empty Stats Star | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 26 | Markelle Fultz | 2017-18 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 27 | Markelle Fultz | 2018-19 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 28 | Markelle Fultz | 2019-20 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 73.04% | ❌ FAIL |
| 29 | Markelle Fultz | 2020-21 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 30 | Markelle Fultz | 2021-22 | True Negative - Draft Bust | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 31 | Markelle Fultz | 2022-23 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 74.87% | ❌ FAIL |
| 32 | Markelle Fultz | 2023-24 | True Negative - Draft Bust | Victim (Low) | King (Resilient Star) | 66.08% | ❌ FAIL |

## Notes

### Failed Tests

**Jordan Poole (2021-22)**: Expected low star-level (<55%), got 87.62%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Julius Randle (2020-21)**: Expected low star-level (<55%), got 61.33%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Tyrese Haliburton (2021-22)**: Expected high star-level (≥65%), got 30.00%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Markelle Fultz (2019-20)**: Expected low star-level (<55%), got 73.04%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2022-23)**: Expected low star-level (<55%), got 74.87%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Markelle Fultz (2023-24)**: Expected low star-level (<55%), got 66.08%; Archetype mismatch: expected Victim, got King (Resilient Star)

