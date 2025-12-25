# Implementation Plan: The "Future-Peak" Helio Target

## The Core Objective
We are pivoting the Telescope Model from predicting "General Utility" (PIE) to predicting **Heliocentric Scalability**. The target variable is the single most critical component of this pivot.

If we train the model to predict regular season stats, we build a calculator. If we train it to predict **future playoff scalability**, we build a Telescope.

## Phase 1: Engineer the Ground Truth (Target Generation)

**File**: `src/nba_data/scripts/generate_helio_targets.py`

### 1. The Metric: `HELIO_LOAD_INDEX`
Implement the formula validated by simulation, with one crucial adjustment for non-linearity to de-risk "Role Player Inflation".

```python
# Formula
# 1. Load: Measures responsibility (Scoring + Playmaking)
OFFENSIVE_LOAD = USG_PCT + (AST_PCT * 0.75)

# 2. Efficiency: Measures value-add per possession (includes TOV penalty)
EFFICIENCY_DELTA = OFF_RATING - LEAGUE_AVG_OFF_RATING

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

## Phase 2: Input Feature Alignment (The "Antidote")

**File**: `src/nba_data/scripts/train_telescope_model.py` (or feature engineering scripts)

The model needs features that explain *why* a player might fail to hit their Helio Target.

### 1. The "Empty Calories" Antidote
*   **Feature**: `SHOT_QUALITY_GENERATION_DELTA` (Self-Created Quality vs. Teammate-Created Quality).
*   *Hypothesis*: Players with high `HELIO_LOAD` but low `GENERATION_DELTA` in the regular season are "System Merchants." They will fail the Playoff Stress Test. The model needs this signal to predict the washout.

### 2. The "Physicality" Antidote
*   **Feature**: `FREE_THROW_RATE_RESILIENCE` (Playoff FTr / Regular Season FTr).
*   *Hypothesis*: Engines who rely on foul-baiting often see their efficiency collapse in the playoffs (Harden Rule). This historical feature helps predict future resilience.

---

## Phase 3: The "Jokic-Gobert" Validation Suite

**File**: `tests/validation/test_helio_alignment.py`

Before training, run this exact test on the **generated target file**:

1.  **The Engine Test**: Ensure `Target(Nikola Jokic 2020)` > `Target(Rudy Gobert 2020)`.
    *   *First Principles*: Value = Load * Efficiency. Jokic carries load; Gobert does not.
2.  **The Merchant Test**: Ensure `Target(Trae Young 2021)` > `Target(D'Angelo Russell 2019)`.
    *   *First Principles*: Both are high usage, but one scales (Trae's playmaking/gravity) and one doesn't (Russell's inefficiency). The target must reflect the *outcome* of their playoff runs.
3.  **The Washout Test**: Ensure `Target(Hassan Whiteside 2016)` is near 0.
    *   *First Principles*: He put up stats but became unplayable. The target must be 0 to teach the model to spot the "Empty Calories" traits.

---

## Checklist for the Next Developer

1.  [ ] **Create `generate_helio_targets.py`**:
    *   Load `regular_season_*.csv` and `playoff_logs_*.csv`.
    *   Compute `HELIO_LOAD_INDEX` for all playoff runs.
    *   Apply the 3-year lookahead window to create the `FUTURE_PEAK_HELIO` column for every regular season row.
    *   Save as `data/training_targets_helio.csv`.

2.  [ ] **Run the Validation Suite**:
    *   Manually inspect the top 20 and bottom 20 targets.
    *   Verify the "Jokic-Gobert" separation.

3.  [ ] **Retrain Telescope Model**:
    *   Swap target variable to `FUTURE_PEAK_HELIO`.
    *   Run feature importance. `OFFENSIVE_LOAD` components (USG, AST) should rise; raw shooting splits should fall.

