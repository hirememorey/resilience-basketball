# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-05 11:25:15

## Executive Summary

- **Total Test Cases**: 16
- **Data Found**: 16
- **Passed**: 13
- **Failed**: 3
- **Pass Rate**: 81.2%

## Results by Category

### True Positive
- **Total**: 8
- **Passed**: 7
- **Failed**: 1
- **Pass Rate**: 87.5%

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
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 97.58% | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 75.25% | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 99.20% | ✅ PASS |
| 4 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) | King (Resilient Star) | 52.84% | ✅ PASS |
| 5 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 6 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | Usage Shock - Hardest Test | Bulldozer (High) | Victim (Fragile Role) | 30.00% | ❌ FAIL |
| 8 | Lauri Markkanen | 2021-22 | True Positive - Wrong Role | Bulldozer (High) | King (Resilient Star) | 71.79% | ✅ PASS |
| 9 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 10 | Jamal Murray | 2018-19 | True Positive - Playoff Riser | Bulldozer (High) | King (Resilient Star) | 97.65% | ✅ PASS |
| 11 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | King (Resilient Star) | 99.00% | ❌ FAIL |
| 12 | Desmond Bane | 2021-22 | True Positive - Secondary Creator | Bulldozer (High) | Victim (Fragile Role) | 26.05% | ❌ FAIL |
| 13 | Tobias Harris | 2016-17 | False Positive - Max Contract Mistake | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 14 | Domantas Sabonis | 2021-22 | False Positive - Comparison Case | Victim (Low) | Victim (Fragile Role) | 30.00% | ✅ PASS |
| 15 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) | Bulldozer (Fragile Star) | 93.76% | ✅ PASS |
| 16 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 96.16% | ✅ PASS |

## Notes

### Failed Tests

**Mikal Bridges (2021-22)**: Expected high star-level (≥65%), got 30.00%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**D'Angelo Russell (2018-19)**: Expected low star-level (<55%), got 99.00%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Desmond Bane (2021-22)**: Expected high star-level (≥65%), got 26.05%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

