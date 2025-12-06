# Latent Star Detection: Critical Case Studies Test Report

**Date**: 2025-12-05 12:32:10

## Executive Summary

- **Total Test Cases**: 16
- **Data Found**: 16
- **Passed**: 8
- **Failed**: 8
- **Pass Rate**: 50.0%

## Results by Category

### True Positive
- **Total**: 8
- **Passed**: 6
- **Failed**: 2
- **Pass Rate**: 75.0%

### False Positive
- **Total**: 6
- **Passed**: 0
- **Failed**: 6
- **Pass Rate**: 0.0%

### System Player
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

### Usage Shock
- **Total**: 1
- **Passed**: 1
- **Failed**: 0
- **Pass Rate**: 100.0%

## Detailed Results

| Test | Player | Season | Category | Expected | Predicted | Star-Level | Pass |
|------|--------|--------|----------|----------|-----------|------------|------|
| 1 | Shai Gilgeous-Alexander | 2018-19 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 96.43% | ✅ PASS |
| 2 | Victor Oladipo | 2016-17 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 60.74% | ❌ FAIL |
| 3 | Jalen Brunson | 2020-21 | True Positive - Latent Star | Bulldozer (High) | King (Resilient Star) | 99.33% | ✅ PASS |
| 4 | Jordan Poole | 2021-22 | False Positive - Mirage Breakout | Victim (Low) | King (Resilient Star) | 96.66% | ❌ FAIL |
| 5 | Talen Horton-Tucker | 2020-21 | False Positive - Mirage Breakout | Victim (Low) | Bulldozer (Fragile Star) | 95.50% | ❌ FAIL |
| 6 | Tyus Jones | 2021-22 | System Player - Ceiling Test | Sniper (Low) | Victim (Fragile Role) | 44.70% | ✅ PASS |
| 7 | Mikal Bridges | 2021-22 | Usage Shock - Hardest Test | Bulldozer (High) | Bulldozer (Fragile Star) | 96.74% | ✅ PASS |
| 8 | Lauri Markkanen | 2021-22 | True Positive - Wrong Role | Bulldozer (High) | Victim (Fragile Role) | 56.05% | ❌ FAIL |
| 9 | Christian Wood | 2020-21 | False Positive - Empty Calories | Victim (Low) | Bulldozer (Fragile Star) | 80.14% | ❌ FAIL |
| 10 | Jamal Murray | 2018-19 | True Positive - Playoff Riser | Bulldozer (High) | King (Resilient Star) | 95.94% | ✅ PASS |
| 11 | D'Angelo Russell | 2018-19 | False Positive - Fool's Gold | Victim (Low) | King (Resilient Star) | 97.88% | ❌ FAIL |
| 12 | Desmond Bane | 2021-22 | True Positive - Secondary Creator | Bulldozer (High) | Bulldozer (Fragile Star) | 89.76% | ✅ PASS |
| 13 | Tobias Harris | 2016-17 | False Positive - Max Contract Mistake | Victim (Low) | Bulldozer (Fragile Star) | 83.14% | ❌ FAIL |
| 14 | Domantas Sabonis | 2021-22 | False Positive - Comparison Case | Victim (Low) | Bulldozer (Fragile Star) | 93.32% | ❌ FAIL |
| 15 | Tyrese Haliburton | 2021-22 | True Positive - Comparison Case | Bulldozer (High) | King (Resilient Star) | 92.85% | ✅ PASS |
| 16 | Tyrese Maxey | 2021-22 | True Positive - Latent Star | Bulldozer (High) | Bulldozer (Fragile Star) | 95.59% | ✅ PASS |

## Notes

### Failed Tests

**Victor Oladipo (2016-17)**: Expected high star-level (≥65%), got 60.74%

**Jordan Poole (2021-22)**: Expected low star-level (<55%), got 96.66%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Talen Horton-Tucker (2020-21)**: Expected low star-level (<55%), got 95.50%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Lauri Markkanen (2021-22)**: Expected high star-level (≥65%), got 56.05%; Archetype mismatch: expected Bulldozer, got Victim (Fragile Role)

**Christian Wood (2020-21)**: Expected low star-level (<55%), got 80.14%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**D'Angelo Russell (2018-19)**: Expected low star-level (<55%), got 97.88%; Archetype mismatch: expected Victim, got King (Resilient Star)

**Tobias Harris (2016-17)**: Expected low star-level (<55%), got 83.14%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

**Domantas Sabonis (2021-22)**: Expected low star-level (<55%), got 93.32%; Archetype mismatch: expected Victim, got Bulldozer (Fragile Star)

