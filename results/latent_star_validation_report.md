# Latent Star Detection: Comprehensive Validation Report

**Date:** December 2025
**Total Test Cases:** 19

---

## Executive Summary

- **True Positives:** 2 (breakouts correctly identified)
- **True Negatives:** 8 (non-breakouts correctly excluded)
- **False Positives:** 2 (non-breakouts incorrectly identified)
- **False Negatives:** 7 (breakouts incorrectly missed)

- **Breakout Recall:** 22.2% (2/9 breakouts identified)
- **Non-Breakout Precision:** 75.0% (8/8 non-breakouts excluded)

---

## False Positives (Non-Breakouts Identified)

These players were identified as latent stars but did NOT break out:

| Player | Season | Age | Star Potential | Reason |
|--------|--------|-----|----------------|--------|
| T.J. McConnell | 2015-16 | 24.0 | 51.8% | Young but didn't break out |
| Dwayne Bacon | 2019-20 | 24.0 | 51.2% | Young but didn't break out |

---

## False Negatives (Breakouts Missed)

These players broke out but were NOT identified as latent stars:

| Player | Season | Age | Reason Not Found |
|--------|--------|-----|------------------|
| Tyrese Haliburton | 2020-21 | 21.0 | Failed star potential threshold or quality filters |
| Tyrese Maxey | 2020-21 | 20.0 | Failed star potential threshold or quality filters |
| Pascal Siakam | 2017-18 | 24.0 | Failed star potential threshold or quality filters |
| Pascal Siakam | 2018-19 | 25.0 | Failed star potential threshold or quality filters |
| Anthony Edwards | 2020-21 | 19.0 | USG 26.4% ≥ 25% (high usage) |
| Devin Booker | 2015-16 | 19.0 | Failed star potential threshold or quality filters |
| Donovan Mitchell | 2017-18 | 21.0 | USG 28.3% ≥ 25% (high usage) |

---

## True Positives (Breakouts Correctly Identified)

| Player | Season | Age | Star Potential | Archetype | Confidence |
|--------|--------|-----|----------------|-----------|------------|
| Jalen Brunson | 2020-21 | 24.0 | 68.1% | King (Resilient Star) | Low |
| Shai Gilgeous-Alexander | 2018-19 | 20.0 | 51.9% | Victim (Fragile Role) | Low |

---

## Key Insights

### Age Filter Effectiveness

✅ **Age filter working correctly:** No veterans (≥26) identified as latent stars

### Missing Breakouts Analysis

**7 breakouts were missed:**
- Failed star potential threshold or quality filters: 5 cases
- USG 26.4% ≥ 25% (high usage): 1 cases
- USG 28.3% ≥ 25% (high usage): 1 cases

---

## Full Results

See `results/latent_star_validation_results.csv` for complete validation data.
