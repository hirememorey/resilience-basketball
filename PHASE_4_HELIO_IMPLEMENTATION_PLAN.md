# Implementation Plan: The "Future-Peak" Helio Target

## The Core Objective
We are pivoting the Telescope Model from predicting "General Utility" (PIE) to predicting **Heliocentric Scalability**. The target variable is the single most critical component of this pivot.

If we train the model to predict regular season stats, we build a calculator. If we train it to predict **future playoff scalability**, we build a Telescope.

## Phase 1: Engineer the Ground Truth (Target Generation) ✅ COMPLETED

**File**: `src/nba_data/scripts/generate_helio_targets.py`

### 1. The Metric: `HELIO_LOAD_INDEX`
Implement the formula validated by simulation, with one crucial adjustment for non-linearity to de-risk "Role Player Inflation".

```python
# Formula
# 1. Load: Measures responsibility (Scoring + Playmaking)
OFFENSIVE_LOAD = USG_PCT + (AST_PCT * 0.75)

# 2. Efficiency: Measures value-add per possession (includes TOV penalty)
# CRITICAL INSIGHT: Using league average baseline created "Negative Inversion Trap"
# High-usage stars struggling slightly below average were penalized more than washouts
EFFICIENCY_DELTA = OFF_RATING - (LEAGUE_AVG_OFF_RATING - 5.0)  # Replacement Level Baseline

# 3. Target: Reward high-load efficiency non-linearly
# Exponent 1.3 ensures high-load stars separate from hyper-efficient low-usage role players
HELIO_LOAD_INDEX = (OFFENSIVE_LOAD ** 1.3) * EFFICIENCY_DELTA
```

### 2. The Horizon: "Future Peak" Logic
The target for Player X in Year N is **not** their stats in Year N. It is their **Peak Scalability** in the near future.

*   **Window**: Next 3 Playoff Runs (Years N+1, N+2, N+3).
*   **Aggregation**: `MAX(HELIO_LOAD_INDEX)` over that window.
*   **The Washout Signal**: If a player plays < 100 playoff minutes total in that 3-year window, their Target = 0.
    *   *Why*: If you don't play, you aren't scalable. The model must learn to predict "disappearance."

### 3. De-Risking Filters (The "Sample Size" Trap)
*   **Input Filter**: Only calculate `HELIO_LOAD_INDEX` for playoff runs with `MIN > 100` or `GP > 4`.
*   *Why*: Prevents a 5-minute "garbage time god" performance from becoming the ground truth label for a star.

---

## Phase 2: Input Feature Alignment (The "Antidote") ✅ COMPLETED

**File**: `src/nba_data/scripts/train_telescope_model.py` (and feature engineering scripts)

**Status**: Telescope Model v2.1 trained. `HELIO_POTENTIAL_SCORE` is now a primary driver, and structural repairs have stabilized the prediction magnitude.

### 1. The "Empty Calories" Antidote ✅ COMPLETED
*   **Feature**: `SHOT_QUALITY_GENERATION_DELTA` (Self-Created Quality vs. Teammate-Created Quality).
*   **Result**: This single feature addition more than doubled the model's R-squared, proving its high leverage.
*   **Stabilization**: Calibrated volume thresholds (>1.5 FGA for assisted, >0.5 FGA for ISO) eliminated fringe player noise.

### 2. The "Physicality" Antidote ✅ COMPLETED
*   **Feature**: `FREE_THROW_RATE_RESILIENCE` (Playoff FTr / Regular Season FTr).
*   **Status**: Implemented in base dataset.

### 3. The "Non-Linearity" Antidote ✅ COMPLETED
*   **Feature**: `HELIO_POTENTIAL_SCORE = SHOT_QUALITY_GENERATION_DELTA * (USG_PCT^1.5)`
*   **Result**: This is now the #1 driver of future stardom predictions. It has corrected the "magnitude collapse" where the model under-predicted superstar peaks.

---

## Phase 3: The "Jokic-Gobert" Validation Suite ✅ COMPLETED

**File**: `scripts/validate_latent_stars.py`

**Status**: Latent Star Test Suite evaluation completed with **High Fidelity**. The model now identifies both the direction and the magnitude of stardom.

### Findings:
*   **Jalen Brunson ('21)**: Predicted 7.30 (Actual Peak 7.73). Success.
*   **Tyrese Maxey ('22)**: Predicted 5.53 (Actual Peak 5.35). Success.
*   **LeBron James ('19)**: Predicted 5.80. High baseline maintained.
*   **D'Angelo Russell ('22)**: Predicted 1.74. Correctly identified as "Fool's Gold" compared to latent stars.

---

## Checklist for the Next Developer

1.  [x] **Create `generate_helio_targets.py`**:
    *   Implemented "Revealed Capacity" logic (Drops censored data/lottery years).
2.  [x] **Run the Validation Suite**:
    *   Verified "Magnitude Matching" for Brunson/Maxey.
3.  [x] **Retrain Telescope Model**:
    *   Confirmed `HELIO_POTENTIAL_SCORE` is the #1 feature.
4.  [x] **Implement the "Empty Calories" Antidote**:
    *   Engineered stable `SHOT_QUALITY_GENERATION_DELTA`.
5.  [x] **Backfill Data**:
    *   Reran full pipeline to eliminate historical `nan` values.

## Final Findings: Phase 4 Summary

We have successfully moved from a "Regular Season Calculator" to a "Playoff Telescope." The model no longer just predicts *what* happened; it identifies the **mechanistic capacity** for stardom before it is fully revealed in outcomes.

