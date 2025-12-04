# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-04 10:21:27

## Executive Summary

- **Total Test Cases**: 12
- **Data Found**: 12
- **Passed**: 6
- **Failed**: 6
- **Pass Rate**: 50.0%

## Results by Category

### True Positive
- **Total**: 6
- **Passed**: 3
- **Failed**: 3
- **Pass Rate**: 50.0%

### False Positive
- **Total**: 4
- **Passed**: 2
- **Failed**: 2
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
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 95.82% | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 59.47% | ❌ FAIL |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 95.77% | ✅ PASS |
| 4 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) | Bulldozer (Fragile Star) | 88.14% | ❌ FAIL |
| 5 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 16.79% | ✅ PASS |
| 6 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 6.88% | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | Usage Shock - Hardest Test | Bulldozer (High) | Bulldozer (Fragile Star) | 54.70% | ❌ FAIL |
| 8 | Lauri Markkanen | 2021-22 | True Positive - Wrong Role | Bulldozer (High) | Victim (Fragile Role) | 34.13% | ❌ FAIL |
| 9 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 28.35% | ✅ PASS |
| 10 | Jamal Murray | 2018-19 | True Positive - Playoff Riser | Bulldozer (High) | Bulldozer (Fragile Star) | 81.03% | ✅ PASS |
| 11 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Bulldozer (Fragile Star) | 86.25% | ❌ FAIL |
| 12 | Desmond Bane | 2021-22 | True Positive - Secondary Creator | Bulldozer (High) | Bulldozer (Fragile Star) | 64.67% | ❌ FAIL |

## Notes

### Failed Tests

**Victor Oladipo (2016-17)**: Expected high star-level (≥70%), got 59.47%

**Jordan Poole (2021-22)**: Expected low star-level (<30%), got 88.14%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Mikal Bridges (2021-22)**: Expected high star-level (≥70%), got 54.70%

**Lauri Markkanen (2021-22)**: Expected high star-level (≥70%), got 34.13%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**D'Angelo Russell (2018-19)**: Expected low star-level (<30%), got 86.25%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Desmond Bane (2021-22)**: Expected high star-level (≥70%), got 64.67%

