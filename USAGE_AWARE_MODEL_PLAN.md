# Usage-Aware Conditional Prediction Model: Implementation Plan

**Status**: 🎯 **Ready for Implementation**  
**Date**: December 2025  
**Priority**: High - Core Model Enhancement

## Executive Summary

The current model predicts playoff archetypes based on regular season stress vectors, but it has a critical limitation: **it predicts performance at the current usage level, not at different usage levels**. This prevents it from answering both questions we need:

1. **Question 1 (Archetype Prediction)**: "How will this player perform in playoffs given their current role?"
2. **Question 2 (Latent Star Detection)**: "Who has the skills but hasn't been given opportunity?"

**The Solution**: Make the model **usage-aware** by treating usage as an explicit feature with interactions, allowing it to predict performance at different usage levels.

---

## 1. The Problem

### Current Model Limitation

**What it does:**
- Takes stress vectors (skills) as input
- Predicts archetype (performance) as output
- **Implicitly assumes usage is fixed** at the player's current level

**What it can't do:**
- Predict what performance would be at a different usage level
- Answer "If this player had 25% usage instead of 19.6%, would they be a King?"

### The Brunson Example

**Jalen Brunson (2020-21):**
- **Current Usage**: 19.6%
- **Stress Vectors**: High creation ratio (0.692), positive leverage USG delta (0.029)
- **Model Prediction**: "Victim" (correct for 19.6% usage)
- **Actual Performance at 19.6%**: Low production, low impact (backup role)

**Jalen Brunson (2022-23):**
- **Current Usage**: 26.6%
- **Stress Vectors**: Similar skills (creation ratio 0.862, leverage USG delta 0.047)
- **Actual Performance**: "King" (high production, high efficiency)
- **Model Prediction**: Would be "King" (correct for 26.6% usage)

**The Insight**: Skills are relatively stable across seasons. Performance depends on opportunity (usage). The model needs to learn: `archetype = f(stress_vectors, usage)`

---

## 2. What We Know (Theoretical Foundation)

### The Stress Vectors (Skills)

These measure a player's **capacity**, not their current performance:

1. **Creation Vector**: Self-creation ability (efficiency on 3+ dribble shots)
2. **Leverage Vector**: Clutch performance (usage and efficiency in high-pressure moments)
3. **Pressure Vector**: Willingness to take tight shots (late-clock vs. early-clock distinction)
4. **Physicality Vector**: Rim pressure resilience (maintaining rim attack volume)
5. **Plasticity Vector**: Spatial and temporal shot distribution adaptability

**Key Insight**: These are relatively stable across seasons. A player's creation ratio doesn't change dramatically year-to-year.

### The Archetype System (Performance)

Performance is classified into four archetypes based on two axes:

1. **Resilience Quotient (RQ)**: Adaptability (volume × efficiency ratio)
2. **Dominance Score**: Absolute value (points per 75 possessions)

**The Four Archetypes:**
- **King**: High RQ, High Dominance (elite production maintained)
- **Bulldozer**: Low RQ, High Dominance (high production, inefficient)
- **Sniper**: High RQ, Low Dominance (efficient, low volume)
- **Victim**: Low RQ, Low Dominance (low production, low efficiency)

**Key Insight**: Performance depends on both skills AND opportunity. A player with King-level skills at 19.6% usage might be a "Victim" (low production), but at 26.6% usage they become a "King" (high production).

### Current Model State

- **Algorithm**: XGBoost Classifier
- **Features**: 32 stress vector features
- **Accuracy**: 59.4%
- **Training Data**: 899 player-seasons (2015-2024)
- **Limitation**: Usage is not an explicit feature, so model can't predict at different usage levels

---

## 3. What Exists (Current State)

### Data Pipeline

**Key Files:**
- `results/predictive_dataset.csv`: Stress vectors for 5,312 player-seasons
- `results/resilience_archetypes.csv`: Playoff archetypes (labels)
- `models/resilience_xgb.pkl`: Trained XGBoost model
- `src/nba_data/scripts/train_predictive_model.py`: Model training script

**Data Available:**
- Stress vectors: 100% coverage
- Usage (USG_PCT): 100% coverage (added in Phase 1)
- Age: 100% coverage (added in Phase 1)
- Playoff archetypes: Available for 899 player-seasons

### Model Architecture

**Current Features (32 total):**
- Creation: CREATION_TAX, CREATION_VOLUME_RATIO
- Leverage: LEVERAGE_TS_DELTA, LEVERAGE_USG_DELTA, CLUTCH_MIN_TOTAL
- Pressure: RS_PRESSURE_APPETITE, RS_PRESSURE_RESILIENCE, clock features
- Physicality: RS_FTr, FTr_RESILIENCE, RIM_PRESSURE_RESILIENCE
- Plasticity: SHOT_DISTANCE_DELTA, SPATIAL_VARIANCE_DELTA
- Context: QOC_TS_DELTA, opponent defensive context

**Missing**: Usage as explicit feature with interactions

### Known Limitations

1. **No usage interaction**: Model can't predict performance at different usage levels
2. **Implicit usage assumption**: Model assumes usage is fixed at current level
3. **Can't answer latent star question**: Can't predict "what if this player had more opportunity?"

---

## 4. What to Build (Implementation Plan)

### Goal

Create a **usage-aware conditional prediction model** that can answer:
- "What would this player's archetype be at their current usage?" (Question 1)
- "What would this player's archetype be at 25% usage?" (Question 2)

### Architecture

**Option 1: Usage as Explicit Feature (Recommended)**
```python
# Add usage as feature with interactions
features = [
    ...existing_stress_vectors...,
    'USG_PCT',  # Explicit usage feature
    'USG_PCT * CREATION_VOLUME_RATIO',  # Interaction terms
    'USG_PCT * LEVERAGE_USG_DELTA',
    # ... other interactions
]
```

**Option 2: Conditional Prediction Function**
```python
def predict_archetype_at_usage(stress_vectors, usage_level):
    # Model trained with usage as feature
    # Can predict at any usage level
    return model.predict(stress_vectors, usage_level)
```

### Implementation Steps

#### Step 1: Add Usage as Explicit Feature (1-2 days)

**What to do:**
1. Modify `train_predictive_model.py` to include `USG_PCT` as a feature
2. Add interaction terms: `USG_PCT * CREATION_VOLUME_RATIO`, `USG_PCT * LEVERAGE_USG_DELTA`, etc.
3. Retrain model with usage-aware features

**Validation:**
- Model accuracy should remain similar or improve
- Feature importance should show usage interactions matter

#### Step 2: Test Conditional Predictions (1 day)

**What to do:**
1. For known cases (Brunson, Haliburton, etc.), predict archetype at:
   - Current usage level
   - Higher usage level (e.g., 25%)
2. Compare predictions to actual performance when usage changed

**Validation:**
- Brunson at 19.6% usage: Should predict "Victim" or "Sniper"
- Brunson at 26.6% usage: Should predict "King"
- If predictions match actual performance, model is working

#### Step 3: Create Conditional Prediction Function (1 day)

**What to do:**
1. Create `predict_archetype_at_usage()` function
2. Takes stress vectors and usage level as input
3. Returns predicted archetype and probabilities

**Validation:**
- Function works for any usage level
- Predictions are consistent (same stress vectors + different usage = different archetypes)

#### Step 4: Validate on Test Cases (1-2 days)

**What to do:**
1. Test on players whose usage changed significantly:
   - Brunson: 19.6% → 26.6%
   - Haliburton: 17.5% → 23.9%
   - Maxey: 19.9% → 27.3%
2. Check if predictions at higher usage match actual performance

**Success Criteria:**
- Model correctly predicts performance at different usage levels
- Predictions at higher usage match actual breakout performance
- Model can answer both questions (current performance + potential performance)

---

## 5. How to Validate (Test Cases)

### Known Cases

**Jalen Brunson:**
- 2020-21: 19.6% usage, predicted "Victim" (correct for that usage)
- 2022-23: 26.6% usage, actual "King"
- **Test**: Predict archetype at 26.6% usage using 2020-21 stress vectors → Should predict "King"

**Tyrese Haliburton:**
- 2020-21: 17.5% usage
- 2021-22: 23.9% usage (breakout)
- **Test**: Predict archetype at 23.9% usage using 2020-21 stress vectors → Should predict "King" or "Bulldozer"

**Tyrese Maxey:**
- 2020-21: 19.9% usage
- 2023-24: 27.3% usage (breakout)
- **Test**: Predict archetype at 27.3% usage using 2020-21 stress vectors → Should predict "King" or "Bulldozer"

### Success Criteria

1. **Accuracy maintained**: Model accuracy should remain ≥ 59.4% (ideally improve)
2. **Conditional predictions work**: Predictions at different usage levels match actual performance
3. **Both questions answered**: Can predict current performance AND potential performance
4. **Latent stars identified**: Players with high skills but low usage are correctly predicted as "King" at higher usage

---

## 6. Key Insights (Hard-Won Lessons)

See `KEY_INSIGHTS.md` for detailed lessons learned. Key principles:

1. **Filter-first architecture**: Define candidate pool before ranking
2. **No proxies**: Missing data = selection bias, not random noise
3. **Normalize within cohort**: All ranking relative to filtered subset
4. **Reference class principle**: Value is relative to the cohort, not absolute

---

## 7. Files to Modify

1. **`src/nba_data/scripts/train_predictive_model.py`**:
   - Add `USG_PCT` as explicit feature
   - Add interaction terms (usage × stress vectors)
   - Retrain model

2. **`src/nba_data/scripts/detect_latent_stars.py`** (if resuming):
   - Use conditional prediction function
   - Predict at higher usage levels for latent star detection

3. **New file**: `src/nba_data/scripts/predict_conditional_archetype.py`:
   - Conditional prediction function
   - Validation script for test cases

---

## 8. Expected Outcomes

### Model Improvements

- **Usage-aware predictions**: Can predict at any usage level
- **Both questions answered**: Current performance + potential performance
- **Latent star detection**: Can identify players with high skills but low opportunity

### Validation Results

- **Brunson test**: Predicts "King" at 26.6% usage using 2020-21 stress vectors
- **Haliburton test**: Predicts "King" or "Bulldozer" at 23.9% usage
- **Maxey test**: Predicts "King" or "Bulldozer" at 27.3% usage

---

## 9. Next Steps After Implementation

1. **Validate on more test cases**: Expand beyond known breakouts
2. **Improve model accuracy**: If usage-aware model improves accuracy, great. If not, investigate why.
3. **Resume latent star detection**: Use conditional predictions to identify latent stars
4. **Sloan paper preparation**: Document usage-aware conditional prediction as key innovation

---

## 10. References

- **Theoretical Foundation**: `LUKA_SIMMONS_PARADOX.md`
- **Stress Vectors**: `extended_resilience_framework.md`
- **Current Model**: `results/predictive_model_report.md`
- **Key Insights**: `KEY_INSIGHTS.md`
- **Data Requirements**: `DATA_REQUIREMENTS.md`

---

**Status**: Ready for implementation. Start with Step 1 (add usage as explicit feature) and validate incrementally.

