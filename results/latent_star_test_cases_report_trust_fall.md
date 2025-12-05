# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-05 10:59:46

## Executive Summary

- **Total Test Cases**: 16
- **Data Found**: 16
- **Passed**: 9
- **Failed**: 7
- **Pass Rate**: 56.2%

## Results by Category

### True Positive
- **Total**: 8
- **Passed**: 8
- **Failed**: 0
- **Pass Rate**: 100.0%

### False Positive
- **Total**: 6
- **Passed**: 0
- **Failed**: 6
- **Pass Rate**: 0.0%

### System Player
- **Total**: 1
- **Passed**: 0
- **Failed**: 1
- **Pass Rate**: 0.0%

### Usage Shock
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Star-Level | Pass |
|------|--------|--------|----------|----------|-----------|------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 97.58% | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 75.25% | ✅ PASS |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 99.20% | ✅ PASS |
| 4 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) | Bulldozer (Fragile Star) | 97.00% | ❌ FAIL |
| 5 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | King (Resilient Star) | 89.62% | ❌ FAIL |
| 6 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | King (Resilient Star) | 55.36% | ❌ FAIL |
| 7 | Mikal Bridges | 2021-22 | Usage Shock - Hardest Test | Bulldozer (High) | Bulldozer (Fragile Star) | 98.18% | ✅ PASS |
| 8 | Lauri Markkanen | 2021-22 | True Positive - Wrong Role | Bulldozer (High) | King (Resilient Star) | 71.79% | ✅ PASS |
| 9 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Bulldozer (Fragile Star) | 76.37% | ❌ FAIL |
| 10 | Jamal Murray | 2018-19 | True Positive - Playoff Riser | Bulldozer (High) | King (Resilient Star) | 97.65% | ✅ PASS |
| 11 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | King (Resilient Star) | 99.00% | ❌ FAIL |
| 12 | Desmond Bane | 2021-22 | True Positive - Secondary Creator | Bulldozer (High) | Bulldozer (Fragile Star) | 90.64% | ✅ PASS |
| 13 | Tobias Harris | 2016-17 | False Positive - Max Contract Mistake | Victim (Low) | Bulldozer (Fragile Star) | 67.59% | ❌ FAIL |
| 14 | Domantas Sabonis | 2021-22 | False Positive - Comparison Case | Victim (Low) | Bulldozer (Fragile Star) | 93.58% | ❌ FAIL |
| 15 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) | Bulldozer (Fragile Star) | 93.76% | ✅ PASS |
| 16 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 96.16% | ✅ PASS |

## Notes

### Failed Tests

**Jordan Poole (2021-22)**: Expected low star-level (<55%), got 97.00%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Talen Horton-Tucker (2020-21)**: Expected low star-level (<55%), got 89.62%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Tyus Jones (2021-22)**: Expected low star-level (<55%), got 55.36%; Archetype mismatch: expected Sniper, got King (Resilient Star)

**Christian Wood (2020-21)**: Expected low star-level (<55%), got 76.37%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**D'Angelo Russell (2018-19)**: Expected low star-level (<55%), got 99.00%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Tobias Harris (2016-17)**: Expected low star-level (<55%), got 67.59%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Domantas Sabonis (2021-22)**: Expected low star-level (<55%), got 93.58%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

