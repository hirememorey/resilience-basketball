# Key Insights: Hard-Won Lessons

**Purpose**: Condensed reference of critical lessons learned during development. Use this as a quick reference when implementing new features.

---

## 1. The Reference Class Principle

**The Problem**: Ranking players against the entire league creates false comparisons.

**The Insight**: Value is relative to the cohort, not absolute. You can't calculate a percentile until you've defined the population.

**The Fix**: Filter FIRST, then normalize and rank within the filtered subset.

**Example**:
- ❌ **Wrong**: "Is Jalen Brunson better than LeBron James?" (No - wrong reference class)
- ✅ **Right**: "Is Jalen Brunson better than other 24-year-old bench guards?" (Yes - correct reference class)

**Implementation**:
```python
# WRONG: Rank all players, then filter
df_ranked = rank_all_players(df)
df_filtered = df_ranked[df_ranked['AGE'] < 25]

# RIGHT: Filter first, then rank within subset
df_candidate = df[df['AGE'] < 25]
df_ranked = rank_within_pool(df_candidate, reference_pool=df_candidate)
```

---

## 2. The Proxy Fallacy

**The Problem**: Using Isolation EFG as a proxy for Leverage TS Delta assumes "talented = resilient."

**The Insight**: Correlation = 0.0047. Being good at isolation has zero statistical relationship with maintaining efficiency in the clutch.

**The Fix**: Don't use proxies. Flag missing data with confidence scores instead of imputing.

**Example**:
- ❌ **Wrong**: "Maxey is good at ISO (0.509), so he's probably good in clutch" → Use ISO EFG as proxy
- ✅ **Right**: "Maxey has missing clutch data" → Flag as "High Potential / Low Confidence"

**Implementation**:
```python
# WRONG: Impute missing Leverage TS Delta with Isolation EFG
df['LEVERAGE_TS_DELTA'] = df['LEVERAGE_TS_DELTA'].fillna(df['EFG_ISO_WEIGHTED'])

# RIGHT: Flag missing data with confidence score
df['SIGNAL_CONFIDENCE'] = calculate_confidence(df)  # Lower if Leverage TS Delta missing
```

---

## 3. Missing Data = Selection Bias

**The Problem**: Missing data is often treated as random noise, but it's usually systematic.

**The Insight**: Missing data often indicates selection bias (filters that exclude target population), not technical issues (NaN handling).

**The Fix**: Find the root cause of missing data. Fix the pipeline, not the symptom.

**Example**:
- **Problem**: 66.6% of players missing USG_PCT
- **Root Cause**: USG_PCT was merged from `regular_season_*.csv` which has MIN >= 20.0 filter
- **Fix**: Fetch USG_PCT directly from API during feature generation (no filter dependency)

**Implementation**:
```python
# WRONG: Handle missing data with imputation
df['USG_PCT'] = df['USG_PCT'].fillna(df['USG_PCT'].median())

# RIGHT: Fix the root cause (data pipeline)
# Fetch USG_PCT directly from API, not from filtered files
```

---

## 4. Normalize Within Cohort, Not Entire League

**The Problem**: Normalizing against the entire league penalizes players in the candidate pool.

**The Insight**: Z-scores and percentiles are only meaningful relative to the reference class.

**The Fix**: Normalize within the candidate pool (filtered subset), not the entire dataset.

**Example**:
- ❌ **Wrong**: Calculate Z-score relative to all 5,312 player-seasons
- ✅ **Right**: Calculate Z-score relative to 567 candidates (age < 25, USG < 25%)

**Implementation**:
```python
# WRONG: Normalize against entire dataset
df['Z_SCORE'] = (df['STRESS_COMPOSITE'] - df['STRESS_COMPOSITE'].mean()) / df['STRESS_COMPOSITE'].std()

# RIGHT: Normalize within candidate pool
candidate_pool = df[(df['AGE'] < 25) & (df['USG_PCT'] < 25)]
df['Z_SCORE'] = (df['STRESS_COMPOSITE'] - candidate_pool['STRESS_COMPOSITE'].mean()) / candidate_pool['STRESS_COMPOSITE'].std()
```

---

## 5. Filter-First Architecture

**The Problem**: Calculating scores before filtering creates incorrect rankings.

**The Insight**: The distribution changes completely when you remove veterans. Normalization parameters must be calculated on the filtered pool.

**The Fix**: Filter FIRST, then normalize, then rank.

**Implementation Order**:
1. **Define the Universe**: Filter (Age < 25, USG < 25%)
2. **Normalize the Universe**: Calculate percentiles/Z-scores within filtered subset
3. **Rank the Universe**: Sort by normalized scores

---

## 6. Skills vs. Performance

**The Problem**: Stress vectors measure skills (capacity), but archetypes measure performance (actual results).

**The Insight**: Skills are relatively stable across seasons. Performance depends on opportunity (usage).

**The Fix**: Make model usage-aware. Predict performance at different usage levels, not just current usage.

**Example**:
- Brunson 2020-21: Skills (creation ratio 0.692) are high, but performance is "Victim" at 19.6% usage
- Brunson 2022-23: Same skills (creation ratio 0.862), but performance is "King" at 26.6% usage
- **Model should predict**: "Victim" at 19.6% usage, "King" at 26.6% usage

**Implementation**:
```python
# Model should learn: archetype = f(stress_vectors, usage)
# Not just: archetype = f(stress_vectors)
```

---

## 7. Don't Average Away the Strongest Signal

**The Problem**: Weighting all features equally dilutes the strongest predictor.

**The Insight**: LEVERAGE_USG_DELTA is the #1 predictor (9.2% importance). Don't average it with weaker signals.

**The Fix**: Use model feature importance weights, not arbitrary averaging.

**Implementation**:
```python
# WRONG: Average all stress vectors equally
composite = (creation + leverage + pressure + physicality + plasticity) / 5

# RIGHT: Weight by model feature importance
composite = (
    leverage * 0.092 +  # Strongest signal
    creation * 0.062 +
    pressure * 0.045 +
    # ... other features with validated weights
)
```

---

## 8. Validation-First Approach

**The Problem**: Building the full pipeline before validating the formula leads to wasted time.

**The Insight**: Test formulas on known cases BEFORE building the pipeline.

**The Fix**: Create test scripts that validate formulas on test cases first.

**Implementation**:
```python
# WRONG: Build full pipeline, then test
def build_pipeline():
    # ... 500 lines of code ...
    results = run_pipeline()
    if results['brunson_rank'] > 500:
        # Oops, formula is wrong, rebuild everything

# RIGHT: Test formula first, then build pipeline
def test_formula():
    test_cases = load_test_cases()
    for case in test_cases:
        score = calculate_score(case)
        assert score > threshold, f"{case} failed"
    # Formula validated, now build pipeline
```

---

## 9. Understand Data Distribution Before Normalizing

**The Problem**: Assuming theoretical ranges (e.g., -0.4 to +0.2) when actual data clusters around 0.

**The Insight**: Most values are between -0.15 and +0.10, not theoretical extremes. Design normalization around actual distribution.

**The Fix**: Check percentiles and median before designing normalization.

**Implementation**:
```python
# WRONG: Assume theoretical range
normalized = (value - (-0.4)) / (0.2 - (-0.4))  # Assumes -0.4 to +0.2

# RIGHT: Use actual distribution
actual_min = df['LEVERAGE_TS_DELTA'].quantile(0.01)
actual_max = df['LEVERAGE_TS_DELTA'].quantile(0.99)
normalized = (value - actual_min) / (actual_max - actual_min)
```

---

## 10. The Abdication Detector

**The Problem**: Players who don't scale up in clutch situations (negative LEVERAGE_USG_DELTA) are still ranked high.

**The Insight**: LEVERAGE_USG_DELTA is the #1 predictor (9.2% importance). Negative values indicate passivity, not resilience.

**The Fix**: Use LEVERAGE_USG_DELTA as a filter (must be ≥ -0.05) to catch the "Simmons Paradox."

**Example**:
- Ben Simmons: Negative LEVERAGE_USG_DELTA (-0.034, -0.067) → Doesn't scale up in clutch
- **Filter**: LEVERAGE_USG_DELTA ≥ -0.05 → Correctly filters out Simmons

---

## Quick Reference Checklist

When implementing new features, ask:

- [ ] Am I filtering first, then normalizing?
- [ ] Am I normalizing within the candidate pool, not entire league?
- [ ] Am I using proxies? (Don't - use confidence scores instead)
- [ ] Is missing data systematic? (Fix root cause, not symptom)
- [ ] Am I using validated feature importance weights?
- [ ] Have I validated the formula on test cases before building?
- [ ] Do I understand the actual data distribution?
- [ ] Am I accounting for usage as a variable (not fixed)?

---

**See Also**:
- `USAGE_AWARE_MODEL_PLAN.md` - Implementation plan
- `LUKA_SIMMONS_PARADOX.md` - Theoretical foundation
- `extended_resilience_framework.md` - Stress vectors explained

