# Jordan Poole Case Study: First Principles Analysis

**Date**: December 2025  
**Purpose**: Deep dive into Poole's data to identify why the Playoff Translation Tax isn't strong enough and find stronger proxies for "Difficulty of Life"

---

## Executive Summary

**The Problem**: Poole is predicted at 95.50% star-level (expected <55%). The Playoff Volume Tax triggers (his open shot frequency is 28.14% vs. 25% threshold), but a 50% volume reduction isn't sufficient.

**Root Cause**: The tax only addresses ONE of Poole's six fundamental holes. We need a **composite "Difficulty of Life" penalty** that captures all system merchant signals.

---

## Poole's Data Profile (2021-22)

### Key Metrics

| Metric | Value | Percentile (vs Stars) | Interpretation |
|--------|-------|----------------------|----------------|
| **USG_PCT** | 25.2% | - | High usage |
| **CREATION_VOLUME_RATIO** | 0.4806 (48.1%) | 48.6th | Moderate creation volume |
| **CREATION_TAX** | -0.0472 | 72.3rd | **NEGATIVE** - Efficiency drops when creating |
| **EFG_ISO_WEIGHTED** | 0.5368 (53.7%) | 89.6th | Good isolation efficiency |
| **LEVERAGE_USG_DELTA** | -0.0010 | 40.5th | Doesn't scale up in clutch |
| **LEVERAGE_TS_DELTA** | -0.0620 | 26.0th | **NEGATIVE** - Efficiency drops in clutch |
| **RS_PRESSURE_APPETITE** | 0.3891 (38.9%) | 17.9th | **LOW** - Avoids tight shots |
| **RS_PRESSURE_RESILIENCE** | 0.4230 (42.3%) | 41.6th | Mediocre on tight shots |
| **RS_LATE_CLOCK_PRESSURE_RESILIENCE** | 0.3018 (30.2%) | - | **POOR** - Late clock bailouts fail |
| **RS_OPEN_SHOT_FREQUENCY** | 0.2814 (28.14%) | 80.9th | **HIGH** - Relies on open shots |

---

## The Six Holes: First Principles Analysis

### 🔴 Hole #1: Creation Efficiency Collapse

**The Data**:
- **CREATION_VOLUME_RATIO**: 0.4806 (48.6th percentile) - Creates shots
- **CREATION_TAX**: -0.0472 (72.3rd percentile) - **EFFICIENCY DROPS when creating**

**The Physics**:
- Stars maintain or improve efficiency when creating (positive or neutral CREATION_TAX)
- Poole's efficiency **drops** when he creates (-0.047) = He's creating against easier defenses
- This is the opposite of what true stars do

**The Proxy**: **CREATION_TAX < 0** = Creating against easier defenses = System Merchant signal

---

### 🔴 Hole #2: Leverage Abdication

**The Data**:
- **LEVERAGE_USG_DELTA**: -0.0010 (40.5th percentile) - Doesn't scale up
- **LEVERAGE_TS_DELTA**: -0.0620 (26.0th percentile) - **EFFICIENCY DROPS in clutch**

**The Physics**:
- Stars scale up usage in clutch (positive LEVERAGE_USG_DELTA) and maintain efficiency
- Poole doesn't scale up AND efficiency drops = Abdication pattern
- This is the "Simmons Paradox" - passivity in high-leverage moments

**The Proxy**: **LEVERAGE_USG_DELTA < 0 AND LEVERAGE_TS_DELTA < 0** = Abdication = System Merchant signal

---

### 🔴 Hole #3: Pressure Resilience Failure

**The Data**:
- **RS_PRESSURE_APPETITE**: 0.3891 (17.9th percentile) - **LOW** - Avoids tight shots
- **RS_PRESSURE_RESILIENCE**: 0.4230 (41.6th percentile) - Mediocre on tight shots
- **RS_LATE_CLOCK_PRESSURE_RESILIENCE**: 0.3018 (30.2%) - **POOR** - Late clock bailouts fail

**The Physics**:
- Stars have higher pressure appetite (face tight defense) and maintain efficiency
- Poole avoids tight shots (17.9th percentile) and is mediocre when he does take them
- Late clock resilience is particularly poor (30.2%) = Can't create bailout shots

**The Proxy**: **RS_PRESSURE_APPETITE < 40th percentile AND RS_PRESSURE_RESILIENCE < 50th percentile** = System Merchant signal

---

### 🔴 Hole #4: Open Shot Dependency (Current Tax Target)

**The Data**:
- **RS_OPEN_SHOT_FREQUENCY**: 0.2814 (28.14%) - 80.9th percentile
- **Threshold**: 0.2660 (75th percentile for stars)
- **Margin**: 0.0154 above threshold (only 1.54 percentage points)

**The Physics**:
- Current tax triggers (28.14% > 25% threshold)
- But the margin is small (1.54 pp) - tax may not be strong enough
- **The real issue**: This is only ONE signal. We need to combine with other signals.

**The Proxy**: **RS_OPEN_SHOT_FREQUENCY > 75th percentile** = System Merchant signal (already implemented)

---

### 🔴 Hole #5: Context Dependency Pattern

**The Data**:
- **CREATION_VOLUME_RATIO**: 0.4806 (High - creates shots)
- **RS_OPEN_SHOT_FREQUENCY**: 0.2814 (High - gets open shots)
- **CREATION_TAX**: -0.0472 (Negative - efficiency drops when creating)

**The Physics**:
- **Pattern**: High creation volume + High open shots + Negative creation tax
- This means: "Creates shots but relies on open looks" = System Merchant
- The contradiction: If you're creating shots, you shouldn't be getting open looks. Unless... you're benefiting from someone else's gravity (Curry).

**The Proxy**: **Context Dependency Score** = `(OPEN_SHOT_FREQ - median) + (CREATION_VOL - median) - (CREATION_TAX - median)`
- Positive score = System Merchant pattern

**Poole's Score**: 0.0170 (Positive = System Merchant confirmed)

---

### 🔴 Hole #6: Low Difficulty of Life

**The Data**:
- **Difficulty of Life Proxy**: 0.5007 (41.4th percentile)
- **Components**: Creation volume (0.5) + Pressure appetite (0.3) + Inverse open shots (0.2)

**The Physics**:
- True stars face high defensive attention (high pressure appetite relative to creation volume)
- Poole has low pressure appetite (17.9th percentile) despite creating shots (48.6th percentile)
- This means: He's creating against **bent defenses** (thanks to Curry), not tight defenses

**The Proxy**: **Difficulty of Life** = `CREATION_VOL * 0.5 + PRESSURE_APP * 0.3 + (1 - OPEN_FREQ) * 0.2`
- Lower score = Easier life = System Merchant

**Poole's Score**: 41.4th percentile (Low = Easier life = System Merchant confirmed)

---

## Why the Current Tax Isn't Strong Enough

### Current Implementation

1. **Tax Trigger**: `RS_OPEN_SHOT_FREQUENCY > 75th percentile (0.2500)`
   - Poole: 0.2814 (triggers ✅)
   - Margin: 0.0154 above threshold (small margin)

2. **Tax Application**: 50% reduction to `CREATION_VOLUME_RATIO`
   - Original: 0.4806
   - After tax: 0.2403
   - **Problem**: This only addresses ONE hole (open shot dependency)

### Why It Fails

1. **Single-Signal Tax**: Only penalizes open shot frequency, ignores 5 other holes
2. **Small Margin**: Poole is only 1.54 pp above threshold - tax may not be aggressive enough
3. **Volume-Only Penalty**: Doesn't address efficiency issues (CREATION_TAX, LEVERAGE_TS_DELTA)
4. **Missing Composite Signal**: Doesn't capture the "Difficulty of Life" pattern

---

## First Principles Solution: Composite "Difficulty of Life" Penalty

### The Core Insight

**"Difficulty of Life" = Defensive Attention Received**

We need to weight efficiency by defensive attention. If we don't have tracking data for "double teams," we must use a **stronger composite proxy**.

### Proposed Composite Proxy

**Difficulty of Life Score** = Weighted combination of:

1. **Creation Volume** (0.3 weight): High = Creates shots
2. **Pressure Appetite** (0.3 weight): High = Faces tight defense
3. **Inverse Open Shot Frequency** (0.2 weight): High = Fewer open looks
4. **Creation Tax** (0.2 weight): Positive = Maintains efficiency when creating

**Formula**:
```python
difficulty_of_life = (
    CREATION_VOLUME_RATIO * 0.3 +
    RS_PRESSURE_APPETITE * 0.3 +
    (1 - RS_OPEN_SHOT_FREQUENCY) * 0.2 +
    max(0, CREATION_TAX + 0.1) * 0.2  # Normalize CREATION_TAX (shift by +0.1 to make negative = 0)
)
```

**System Merchant Penalty** = `(STAR_MEDIAN_DIFFICULTY - player_difficulty) / STAR_MEDIAN_DIFFICULTY`

- If player's difficulty < star median → Penalty (easier life = system merchant)
- Penalty scales with how much easier their life is

### Alternative: Multi-Signal Tax

Instead of a single tax, apply **multiple penalties** based on multiple signals:

1. **Open Shot Tax** (current): 50% volume reduction if `OPEN_FREQ > 75th percentile`
2. **Creation Efficiency Tax**: Additional 20% volume reduction if `CREATION_TAX < 0`
3. **Leverage Abdication Tax**: Additional 20% volume reduction if `LEVERAGE_USG_DELTA < 0 AND LEVERAGE_TS_DELTA < 0`
4. **Pressure Avoidance Tax**: Additional 20% volume reduction if `PRESSURE_APPETITE < 40th percentile`

**Total Maximum Penalty**: 50% + 20% + 20% + 20% = **90% volume reduction** for extreme system merchants

### Poole's Penalty Calculation

**Current (Single Tax)**:
- Open Shot Tax: 50% reduction → `CREATION_VOLUME_RATIO: 0.4806 → 0.2403`

**Proposed (Multi-Signal Tax)**:
- Open Shot Tax: 50% reduction → `0.4806 → 0.2403`
- Creation Efficiency Tax: 20% reduction → `0.2403 → 0.1922` (CREATION_TAX = -0.047 < 0)
- Leverage Abdication Tax: 20% reduction → `0.1922 → 0.1538` (LEVERAGE_USG_DELTA < 0 AND LEVERAGE_TS_DELTA < 0)
- Pressure Avoidance Tax: 20% reduction → `0.1538 → 0.1230` (PRESSURE_APPETITE = 17.9th percentile < 40th)

**Total Penalty**: 74.4% reduction (vs. current 50%)
**Final CREATION_VOLUME_RATIO**: 0.1230 (vs. current 0.2403)

---

## Recommended Implementation

### Option 1: Multi-Signal Tax (Recommended)

**Advantages**:
- Addresses all 6 holes, not just one
- Penalty scales with number of system merchant signals
- More interpretable (each tax has clear meaning)

**Implementation**:
```python
# Apply multiple taxes based on system merchant signals
volume_penalty = 1.0

# Tax 1: Open Shot Dependency
if open_shot_freq > open_freq_75th:
    volume_penalty *= 0.50  # 50% reduction

# Tax 2: Creation Efficiency Collapse
if creation_tax < 0:
    volume_penalty *= 0.80  # Additional 20% reduction

# Tax 3: Leverage Abdication
if leverage_usg_delta < 0 and leverage_ts_delta < 0:
    volume_penalty *= 0.80  # Additional 20% reduction

# Tax 4: Pressure Avoidance
if pressure_appetite < pressure_app_40th:
    volume_penalty *= 0.80  # Additional 20% reduction

# Apply to CREATION_VOLUME_RATIO
projected_creation_vol = projected_creation_vol * volume_penalty
```

### Option 2: Composite Difficulty of Life Penalty

**Advantages**:
- Single unified metric
- More elegant (one calculation)
- Captures all signals in one score

**Implementation**:
```python
# Calculate Difficulty of Life Score
difficulty_of_life = (
    creation_vol_ratio * 0.3 +
    pressure_appetite * 0.3 +
    (1 - open_shot_freq) * 0.2 +
    max(0, creation_tax + 0.1) * 0.2
)

# Calculate penalty based on deviation from star median
star_median_difficulty = calculate_star_median_difficulty()
if difficulty_of_life < star_median_difficulty:
    penalty_factor = difficulty_of_life / star_median_difficulty
    # Penalize: easier life = more penalty
    volume_penalty = penalty_factor ** 2  # Square to make penalty more aggressive
else:
    volume_penalty = 1.0  # No penalty if harder life than stars

# Apply to CREATION_VOLUME_RATIO
projected_creation_vol = projected_creation_vol * volume_penalty
```

---

## Expected Impact

### Current Prediction
- **Poole Star-Level**: 95.50% (expected <55%)
- **Tax Applied**: 50% volume reduction
- **Result**: Still too high

### With Multi-Signal Tax
- **Poole Star-Level**: Expected <55% ✅
- **Tax Applied**: 74.4% volume reduction (4 signals)
- **CREATION_VOLUME_RATIO**: 0.1230 (vs. current 0.2403)
- **Result**: Should drop below 55% threshold

---

## Validation Strategy

1. **Test on Poole**: Verify star-level drops to <55%
2. **Test on Other System Merchants**: Sabonis, other false positives
3. **Test on True Stars**: Ensure Jokić, Giannis, LeBron aren't penalized
4. **Test on Latent Stars**: Ensure Oladipo, Haliburton, Maxey aren't penalized

---

## Key Principles

1. **Multiple Signals > Single Signal**: System merchants show multiple red flags, not just one
2. **Composite Metrics > Individual Metrics**: "Difficulty of Life" captures the pattern better than individual features
3. **Penalty Scaling**: More system merchant signals = stronger penalty
4. **First Principles**: Weight efficiency by defensive attention received (even if we don't have direct tracking data)

---

**Status**: Ready for implementation. Multi-Signal Tax recommended for immediate fix.

