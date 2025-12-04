# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-04 13:52:46

## Executive Summary

- **Total Test Cases**: 16
- **Data Found**: 16
- **Passed**: 7
- **Failed**: 9
- **Pass Rate**: 43.8%

## Results by Category

### True Positive
- **Total**: 8
- **Passed**: 4
- **Failed**: 4
- **Pass Rate**: 50.0%

### False Positive
- **Total**: 6
- **Passed**: 2
- **Failed**: 4
- **Pass Rate**: 33.3%

### System Player
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

### Usage Shock
- **Total**: 1
- **Passed**: 0
- **Failed**: 1
- **Pass Rate**: 0.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Star-Level | Pass |
|------|--------|--------|----------|----------|-----------|------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 89.17% | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 68.08% | ❌ FAIL |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 94.17% | ✅ PASS |
| 4 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) | Bulldozer (Fragile Star) | 84.23% | ❌ FAIL |
| 5 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 19.71% | ✅ PASS |
| 6 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 8.75% | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | Usage Shock - Hardest Test | Bulldozer (High) | Bulldozer (Fragile Star) | 61.71% | ❌ FAIL |
| 8 | Lauri Markkanen | 2021-22 | True Positive - Wrong Role | Bulldozer (High) | Victim (Fragile Role) | 15.31% | ❌ FAIL |
| 9 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 26.70% | ✅ PASS |
| 10 | Jamal Murray | 2018-19 | True Positive - Playoff Riser | Bulldozer (High) | Bulldozer (Fragile Star) | 76.78% | ✅ PASS |
| 11 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Victim (Fragile Role) | 30.00% | ❌ FAIL |
| 12 | Desmond Bane | 2021-22 | True Positive - Secondary Creator | Bulldozer (High) | Bulldozer (Fragile Star) | 65.58% | ❌ FAIL |
| 13 | Tobias Harris | 2016-17 | False Positive - Max Contract Mistake | Victim (Low) | Bulldozer (Fragile Star) | 57.75% | ❌ FAIL |
| 14 | Domantas Sabonis | 2021-22 | False Positive - Comparison Case | Victim (Low) | Bulldozer (Fragile Star) | 78.87% | ❌ FAIL |
| 15 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) | Victim (Fragile Role) | 46.40% | ❌ FAIL |
| 16 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 75.50% | ✅ PASS |

## Notes

### Failed Tests

**Victor Oladipo (2016-17)**: Expected high star-level (≥70%), got 68.08%

**Jordan Poole (2021-22)**: Expected low star-level (<30%), got 84.23%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Mikal Bridges (2021-22)**: Expected high star-level (≥70%), got 61.71%

**Lauri Markkanen (2021-22)**: Expected high star-level (≥70%), got 15.31%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**D'Angelo Russell (2018-19)**: Expected low star-level (<30%), got 30.00%

**Desmond Bane (2021-22)**: Expected high star-level (≥70%), got 65.58%

**Tobias Harris (2016-17)**: Expected low star-level (<30%), got 57.75%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Domantas Sabonis (2021-22)**: Expected low star-level (<30%), got 78.87%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Tyrese Haliburton (2021-22)**: Expected high star-level (≥70%), got 46.40%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

