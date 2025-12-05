# Model Behavior Rules: Phase 0 Discovery

**Date:** December 2025  
**Status:** ✅ Complete

## Key Findings

### 1. Model DOES Predict "King" (Contrary to Previous Assumption)

**Finding:** The model DOES predict "King (Resilient Star)" for known Kings:
- Nikola Jokić (2022-23): 66.3% King probability, 70.3% star-level potential
- Giannis Antetokounmpo (2020-21): 55.0% King probability, 57.2% star-level potential  
- LeBron James (2019-20): 73.6% King probability, 75.8% star-level potential

**Implication:** The model is NOT overly conservative about "King" predictions. Previous developer's observation may have been context-specific or after modifications.

**Action:** Focus on "Star-Level Potential" (King + Bulldozer) as the primary metric, but "King" predictions are valid and meaningful.

---

### 2. Predictions Don't Change with Usage (Expected - USG_PCT Not a Feature Yet)

**Finding:** All predictions are identical across usage levels (15%, 18%, 22%, 25%, 28%, 32%).

**Example:**
- Jokić (2022-23): 66.3% King probability at ALL usage levels
- Brunson (2020-21): 16.3% star-level potential at ALL usage levels

**Implication:** Current model doesn't use USG_PCT, so predictions are independent of usage level. This confirms the need for usage-aware model.

**Action:** Add USG_PCT as explicit feature with interaction terms (Phase 2).

---

### 3. Known Kings Have High Star-Level Potential

**Finding:** All known Kings show high star-level potential (King + Bulldozer probability):
- LeBron James (2019-20): 75.8% star-level potential
- Nikola Jokić (2022-23): 70.3% star-level potential
- Giannis Antetokounmpo (2020-21): 57.2% star-level potential

**Implication:** Model correctly identifies star-level players.

**Action:** Use star-level potential as primary ranking metric.

---

### 4. Known Breakouts Show Varying Potential

**Finding:** Breakout players show different star-level potential before vs. after breakout:
- Jalen Brunson (2020-21): 16.3% star-level potential (pre-breakout)
- Jalen Brunson (2022-23): 70.7% star-level potential (post-breakout)
- Tyrese Haliburton (2020-21): 0.6% star-level potential (pre-breakout)
- Tyrese Maxey (2020-21): 2.1% star-level potential (pre-breakout)

**Implication:** Model may be missing some breakouts at low usage. Need quality filters to identify players with high skills but low opportunity.

**Action:** Build quality filters (Phase 1) to identify latent stars before breakout.

---

### 5. Known Non-Stars Have Low Star-Level Potential

**Finding:** Non-star players show very low star-level potential:
- Ben Simmons (2020-21): 1.4% star-level potential
- T.J. McConnell (2020-21): 0.4% star-level potential
- Cory Joseph (2020-21): 0.5% star-level potential

**Implication:** Model correctly filters out non-stars.

**Action:** Use quality filters to ensure top-ranked players have positive signals (Phase 1).

---

### 6. Star-Level Potential Distribution

**Finding:** 
- Mean: 29.4%
- Median: 16.3%
- Max: 75.8% (LeBron James)
- Min: 0.4% (T.J. McConnell)

**Implication:** Distribution is right-skewed. Most players have low star-level potential, but stars have very high potential.

**Action:** Use percentiles for thresholds (top 10%, top 5%) rather than absolute probabilities.

---

## Model Behavior Rules

### Rule 1: Star-Level Potential is Primary Metric
- Use "Star-Level Potential" = King Probability + Bulldozer Probability
- Focus on identifying star-level players, not just "King"
- Percentile-based thresholds (top 10%, top 5%) are more meaningful than absolute probabilities

### Rule 2: Predictions Are Currently Usage-Independent
- Current model doesn't use USG_PCT
- Predictions don't change with usage level
- Need usage-aware model to predict at different usage levels (Phase 2)

### Rule 3: Model Correctly Identifies Stars
- Known Kings have high star-level potential (57-76%)
- Known non-stars have low star-level potential (<2%)
- Model is working correctly for established players

### Rule 4: Some Breakouts Are Missed at Low Usage
- Pre-breakout players (Brunson, Haliburton, Maxey) show low star-level potential
- Need quality filters to identify players with high skills but low opportunity
- Quality filters should check base signal strength independent of usage

---

## Next Steps

1. **Phase 1:** Build quality filters to identify latent stars
2. **Phase 2:** Add USG_PCT as explicit feature with interaction terms
3. **Phase 3:** Create conditional prediction function
4. **Phase 4:** Build star potential ranking with quality filters

---

**Status:** Model behavior documented. Ready for Phase 1 (Quality Filters).

