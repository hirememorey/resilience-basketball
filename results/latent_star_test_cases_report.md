# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-04 20:28:45

## Executive Summary

- **Total Test Cases**: 16
- **Data Found**: 16
- **Passed**: 10
- **Failed**: 6
- **Pass Rate**: 62.5%

## Results by Category

### True Positive
- **Total**: 8
- **Passed**: 4
- **Failed**: 4
- **Pass Rate**: 50.0%

### False Positive
- **Total**: 6
- **Passed**: 5
- **Failed**: 1
- **Pass Rate**: 83.3%

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
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 91.86% | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 58.14% | ❌ FAIL |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 96.69% | ✅ PASS |
| 4 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) | Bulldozer (Fragile Star) | 90.24% | ❌ FAIL |
| 5 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 26.28% | ✅ PASS |
| 6 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 7.57% | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | Usage Shock - Hardest Test | Bulldozer (High) | Victim (Fragile Role) | 30.00% | ❌ FAIL |
| 8 | Lauri Markkanen | 2021-22 | True Positive - Wrong Role | Bulldozer (High) | Victim (Fragile Role) | 15.52% | ❌ FAIL |
| 9 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 10 | Jamal Murray | 2018-19 | True Positive - Playoff Riser | Bulldozer (High) | Bulldozer (Fragile Star) | 79.30% | ✅ PASS |
| 11 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 12 | Desmond Bane | 2021-22 | True Positive - Secondary Creator | Bulldozer (High) | Bulldozer (Fragile Star) | 86.40% | ✅ PASS |
| 13 | Tobias Harris | 2016-17 | False Positive - Max Contract Mistake | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 14 | Domantas Sabonis | 2021-22 | False Positive - Comparison Case | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 15 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) | Victim (Fragile Role) | 32.01% | ❌ FAIL |
| 16 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Victim (Fragile Role) | 55.67% | ❌ FAIL |

## Notes

### Failed Tests

**Victor Oladipo (2016-17)**: Expected high star-level (≥65%), got 58.14%

**Jordan Poole (2021-22)**: Expected low star-level (<55%), got 90.24%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Mikal Bridges (2021-22)**: Expected high star-level (≥65%), got 30.00%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Lauri Markkanen (2021-22)**: Expected high star-level (≥65%), got 15.52%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Tyrese Haliburton (2021-22)**: Expected high star-level (≥65%), got 32.01%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Tyrese Maxey (2021-22)**: Expected high star-level (≥65%), got 55.67%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

