# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-04 11:25:40

## Executive Summary

- **Total Test Cases**: 14
- **Data Found**: 14
- **Passed**: 6
- **Failed**: 8
- **Pass Rate**: 42.9%

## Results by Category

### True Positive
- **Total**: 6
- **Passed**: 2
- **Failed**: 4
- **Pass Rate**: 33.3%

### False Positive
- **Total**: 6
- **Passed**: 3
- **Failed**: 3
- **Pass Rate**: 50.0%

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
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 94.03% | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Victim (Fragile Role) | 30.24% | ❌ FAIL |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 38.06% | ❌ FAIL |
| 4 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) | Bulldozer (Fragile Star) | 49.82% | ❌ FAIL |
| 5 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 20.96% | ✅ PASS |
| 6 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 6.88% | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | Usage Shock - Hardest Test | Bulldozer (High) | Victim (Fragile Role) | 16.81% | ❌ FAIL |
| 8 | Lauri Markkanen | 2021-22 | True Positive - Wrong Role | Bulldozer (High) | Victim (Fragile Role) | 5.10% | ❌ FAIL |
| 9 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 9.10% | ✅ PASS |
| 10 | Jamal Murray | 2018-19 | True Positive - Playoff Riser | Bulldozer (High) | Bulldozer (Fragile Star) | 73.36% | ✅ PASS |
| 11 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Bulldozer (Fragile Star) | 78.38% | ❌ FAIL |
| 12 | Desmond Bane | 2021-22 | True Positive - Secondary Creator | Bulldozer (High) | Victim (Fragile Role) | 17.67% | ❌ FAIL |
| 13 | Tobias Harris | 2016-17 | False Positive - Max Contract Mistake | Victim (Low) | Bulldozer (Fragile Star) | 32.95% | ❌ FAIL |
| 14 | Tobias Harris | 2017-18 | False Positive - Max Contract Mistake | Victim (Low) | Victim (Fragile Role) | 25.12% | ✅ PASS |

## Notes

### Failed Tests

**Victor Oladipo (2016-17)**: Expected high star-level (≥70%), got 30.24%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Jalen Brunson (2020-21)**: Expected high star-level (≥70%), got 38.06%

**Jordan Poole (2021-22)**: Expected low star-level (<30%), got 49.82%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Mikal Bridges (2021-22)**: Expected high star-level (≥70%), got 16.81%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Lauri Markkanen (2021-22)**: Expected high star-level (≥70%), got 5.10%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**D'Angelo Russell (2018-19)**: Expected low star-level (<30%), got 78.38%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Desmond Bane (2021-22)**: Expected high star-level (≥70%), got 17.67%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Tobias Harris (2016-17)**: Expected low star-level (<30%), got 32.95%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

