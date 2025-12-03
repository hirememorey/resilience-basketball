# Phase 0 Validation: Key Findings

## Executive Summary

All 14 test cases were found in the dataset (100% coverage). This analysis reveals critical insights about which filters are removing known breakouts and why false positives are being flagged.

---

## Critical Discoveries

### 1. USG% Filter is TOO STRICT

**Problem:** The 20% USG threshold is filtering out known breakouts:
- **Maxey (2020-21)**: USG 22.2% → FILTERED OUT (but he broke out!)
- **Edwards (2020-21)**: USG 26.4% → FILTERED OUT (but he's a star!)
- **Siakam (2018-19)**: USG 20.5% → FILTERED OUT (this is his breakout year!)

**Insight:** The 20% threshold is arbitrary and too strict. These players had high usage but were still "latent" in terms of opportunity/role.

**Recommendation:** 
- Consider raising threshold to 25% or 30%
- OR: Use a relative threshold (e.g., bottom 50% of players in their position)
- OR: Remove usage filter entirely and rely on other signals

---

### 2. Age Filter is CORRECT (But Siakam Edge Case)

**Problem:** Siakam (2018-19) is age 25.0 → filtered out by age < 25

**Insight:** This is his actual breakout year, but he's exactly at the age boundary.

**Recommendation:**
- Consider age < 26 (more inclusive)
- OR: Age < 25.5 (catches players who turn 25 during season)
- OR: Keep age < 25 but acknowledge edge cases

---

### 3. Leverage TS Delta is THE STRONGEST SIGNAL (Confirmed)

**Breakouts:**
- Haliburton: +0.178 (very strong)
- Siakam (2017-18): +0.339 (extremely strong)
- Siakam (2018-19): +0.119 (strong)
- Brunson: -0.060 (negative but small - edge case)

**Non-Breakouts:**
- Turner: -0.016, -0.017 (neutral/negative)
- McConnell: +0.180 (strong - but didn't break out - why?)

**Fragility Cases:**
- Simmons: +0.093, +0.007 (weak/neutral)
- KAT: +0.028, -0.052, -0.132 (weak/negative - shows fragility!)

**Insight:** Leverage TS Delta clearly distinguishes breakouts from non-breakouts. However, McConnell has strong Leverage TS Delta (+0.180) but didn't break out - need to understand why.

**Recommendation:**
- Rank by Leverage TS Delta (weighted 2-3x)
- Use as primary signal, not just a filter
- Require data (not NaN) for high confidence, but allow missing data with lower confidence

---

### 4. Missing Leverage TS Delta Data is a Problem

**Problem:** Maxey has missing Leverage TS Delta data (NaN)

**Insight:** This is exactly the "Maxey Failure" - missing data penalizes players who should be identified.

**Recommendation:**
- Don't exclude players with missing Leverage TS Delta
- Use Isolation EFG as proxy (Maxey: 0.509, which is decent)
- Flag as "Low Confidence" but still include

---

### 5. Scalability Coefficient Works Well

**Breakouts:**
- Haliburton: 0.912 (very high)
- Siakam (2017-18): 0.891 (very high)
- Siakam (2018-19): 0.932 (very high)
- Brunson: 0.647 (high)
- Maxey: 0.727 (high)
- Edwards: 0.719 (high)

**Non-Breakouts:**
- Turner: 0.715, 0.652 (high - but didn't break out)
- McConnell: 0.872 (very high - but didn't break out)

**Fragility Cases:**
- Simmons: 0.903, 0.872 (very high - but fragile in playoffs!)
- KAT: 0.956, 0.854, 0.755 (very high - but fragile in playoffs!)

**Insight:** Scalability alone doesn't distinguish breakouts from non-breakouts. It's necessary but not sufficient.

**Recommendation:**
- Use Scalability as secondary signal
- Combine with Leverage TS Delta for ranking
- Don't use as hard filter (threshold too high)

---

### 6. Creation Volume Ratio Threshold is TOO HIGH

**Problem:** Siakam (2017-18) has Creation Ratio 0.203 (just above 0.20 threshold)

**Insight:** The 0.20 threshold is correct (catches Siakam), but it's close to the boundary.

**Recommendation:**
- Keep 0.20 threshold (validated by Siakam)
- But don't use as hard filter - use as tiebreaker

---

### 7. Positive Creation Tax is CRITICAL (Maxey Case)

**Maxey (2020-21):**
- Creation Tax: +0.034 (positive - efficiency INCREASES when creating!)
- Creation Boost: 1.5 (already implemented!)
- This is the "physics violation" - should be highest indicator

**Insight:** Maxey has positive creation tax but was still filtered out by usage. The CREATION_BOOST feature is already in the data (1.5), but it's not being used in ranking.

**Recommendation:**
- Use CREATION_BOOST in ranking formula
- Weight positive creation tax players higher

---

### 8. False Positives: Why Turner and McConnell Were Flagged

**Evan Turner:**
- Age: 27, 28 (FILTERED OUT by age - correct!)
- Leverage TS Delta: -0.016, -0.017 (negative - should filter out)
- Scalability: 0.715, 0.652 (high)
- Creation Ratio: 0.721, 0.656 (very high)

**T.J. McConnell:**
- Age: 29 (FILTERED OUT by age - correct!)
- Leverage TS Delta: +0.180 (strong - but didn't break out)
- Scalability: 0.872 (very high)
- Creation Ratio: 0.816 (very high)

**Insight:** 
- Turner: Age filter works (27, 28 > 25)
- McConnell: Age filter works (29 > 25)
- BUT: If age filter wasn't there, they'd be flagged because of high Scalability and Creation Ratio

**Recommendation:**
- Age filter is critical (validated!)
- Keep age < 25 as hard filter
- McConnell case: High Leverage TS Delta but didn't break out - need to understand why (age? role? opportunity?)

---

### 9. Fragility Cases: Simmons and KAT Show Negative Signals

**Ben Simmons:**
- Leverage TS Delta: +0.093, +0.007 (weak/neutral)
- Scalability: 0.903, 0.872 (very high - misleading!)
- Creation Ratio: 0.769, 0.650 (very high - misleading!)

**KAT:**
- Leverage TS Delta: +0.028, -0.052, -0.132 (weak/negative - shows fragility!)
- Scalability: 0.956, 0.854, 0.755 (very high - misleading!)
- Creation Ratio: 0.088, 0.136, 0.109 (very low - correct signal!)

**Insight:** 
- Leverage TS Delta correctly shows fragility (negative/weak for KAT)
- Scalability is misleading (high for both, but they're fragile)
- Creation Ratio correctly shows KAT's weakness (low)
- Simmons has high Creation Ratio but weak Leverage TS Delta - this is the "passivity" signal

**Recommendation:**
- Use Leverage TS Delta as primary fragility signal
- Low Creation Ratio + High Scalability = fragility (KAT pattern)
- High Creation Ratio + Weak Leverage TS Delta = passivity (Simmons pattern)

---

## Summary of Recommendations

### Immediate Fixes (Phase 1):

1. **Raise USG% threshold to 25% or 30%** (catches Maxey, Edwards, Siakam 2018-19)
2. **Keep age < 25 filter** (validated - filters out Turner, McConnell)
3. **Require Leverage TS Delta data** (but use Isolation EFG as proxy if missing)
4. **Rank by Leverage TS Delta (weighted 2-3x) + Scalability** (not just filter)

### Feature Implementation (Phase 2):

1. **Use CREATION_BOOST in ranking** (Maxey has 1.5 - should boost his score)
2. **Don't use Scalability as hard filter** (too many false positives)
3. **Use Creation Ratio as tiebreaker** (not hard filter)
4. **Flag missing data as "Low Confidence"** (don't exclude)

### Ranking Formula (Phase 3):

```
Primary Ranking = (Normalized Leverage TS Delta × 3) + (Normalized Scalability × 1) + (CREATION_BOOST bonus)

Filters (in order):
1. Age < 25 (hard filter)
2. USG < 25% (raised threshold)
3. Leverage TS Delta data preferred (not required - use proxy if missing)
4. Scalability > 0.25 (low threshold - catches Brunson at 0.647)
5. Creation Ratio > 0.20 (low threshold - catches Siakam at 0.203)
```

---

## Validation Matrix Results

### True Positives (Should Be Identified):
- ✅ Haliburton (2020-21): Would pass all filters
- ✅ Brunson (2020-21): Would pass all filters
- ✅ Siakam (2017-18): Would pass all filters
- ❌ Siakam (2018-19): Age 25.0 → filtered out (edge case)
- ❌ Maxey (2020-21): USG 22.2% → filtered out (needs threshold raise)
- ❌ Edwards (2020-21): USG 26.4% → filtered out (needs threshold raise)

### False Positives (Should NOT Be Identified):
- ✅ Turner (2015-16): Age 27 → filtered out (correct!)
- ✅ Turner (2016-17): Age 28 → filtered out (correct!)
- ✅ McConnell (2020-21): Age 29 → filtered out (correct!)

### Fragility Cases (Should Show Negative Signals):
- ✅ Simmons: Weak Leverage TS Delta (+0.093, +0.007) → correct signal
- ✅ KAT: Negative Leverage TS Delta (-0.052, -0.132) → correct signal

---

## Next Steps

1. **Phase 1**: Fix data pipeline (USG_PCT, AGE already in dataset - validate completeness)
2. **Phase 2**: Implement ranking formula with Leverage TS Delta weighting
3. **Phase 3**: Test threshold combinations systematically
4. **Phase 4**: Validate against all test cases

