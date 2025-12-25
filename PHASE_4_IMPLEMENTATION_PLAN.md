# Implementation Plan: The "Helio-Target" Pivot

## The Core Problem
The Telescope Model is structurally sound (it doesn't hallucinate skills), but teleologically confused. It optimizes for **General Utility** (PIE) rather than **Heliocentric Scalability**.
- **Symptom**: It correctly identifies Brunson (Latent Star), but incorrectly flags Rudy Gobert (High Utility, Low Scalability) as a "Latent Star."
- **Root Cause**: The target variable (`Playoff_PIE`) rewards rebounding and defense equally with creation.
- **Goal**: Change the target to train a "Heliocentric Engine" detector, not a "Good Basketball Player" detector.

---

## Phase 1: Engineer the "Helio-Target" (Ground Truth)

**Objective**: Create a target variable that mathematically defines "Star" as "High-Volume, Efficient Creation."

### 1. Define the Metric
Replace `PIE` with `HELIO_INDEX`.
**Formula**: 
```python
HELIO_INDEX = (USG_PCT * 100) * (TS_PCT - REPLACEMENT_LEVEL_TS) * CREATION_VOLUME_RATIO
```
- **USG_PCT**: Captures Engine Capacity.
- **TS_PCT - 0.54**: Captures Efficiency Value-Add. (If inefficient, score becomes negative).
- **CREATION_VOLUME_RATIO**: Captures Self-Reliance (filters out Capela/Gobert).

### 2. Implement the Target Script
**File**: `src/nba_data/scripts/generate_helio_targets.py`
- **Input**: `playoff_pie_data.csv` (for efficiency/usage) + `predictive_dataset_with_friction.csv` (for creation volume).
- **Logic**: 
    - Calculate `HELIO_INDEX` for every playoff run.
    - For each player-season (N), Target = `MAX(HELIO_INDEX)` over years N+1 to N+3.
    - **Crucial**: Keep the "Washout Imputation" (Set Target = 0 for players who disappear).

### 3. De-Risking the "DeRozan Trap"
DeRozan has high usage and creation volume. To ensure he doesn't break the metric:
- Use **Playoff Efficiency** in the target calculation, not Regular Season.
- This ensures the target reflects the *reality* of his value drop (Leverage Decay).

---

## Phase 2: Refine the "Universal Projector" (Input Physics)

**Objective**: Ensure the inputs (what the model sees) contain the signals necessary to predict the new target.

### 1. Add "Anti-DeRozan" Features
The model needs signals that correlate with "Playoff Efficiency Drop."
- **Add**: `SHOT_DISTRIBUTION_RIM_FREQ`, `SHOT_DISTRIBUTION_3P_FREQ`.
- **Add**: `MID_RANGE_RELIANCE` (Ratio of Mid-Range FGA / Total FGA).
- **Why**: The model needs to learn that "High Mid-Range Reliance" + "High Volume" = "Negative Helio-Target" (Playoff Inefficiency).

### 2. Verify Percentile Preservation
**File**: `src/nba_data/scripts/project_player_avatars.py`
- **Audit**: Ensure the `project_value_by_percentile` function is robust for edge cases (0 volume).
- **Action**: Add unit tests for extreme archetypes (Gobert, DeRozan, Curry).

---

## Phase 3: Train & Synthesize

**Objective**: Retrain the Telescope on the new target and integrate.

### 1. Retrain Telescope
**File**: `src/nba_data/scripts/train_telescope_model.py`
- **Change**: Switch target column from `TELESCOPE_TARGET` (PIE) to `HELIO_TARGET`.
- **Validation**: Check Feature Importance. `CREATION_VOLUME` and `LEVERAGE_DELTA` should rise; `REB_PCT` (if included) should vanish.

### 2. Update Risk Matrix Logic
**File**: `src/nba_data/scripts/predict_2d_risk_matrix.py`
- **Thresholds**: The new target will have a different scale/distribution.
- **Action**: Recalculate `Franchise Cornerstone` threshold. It shouldn't be the median. It should be the **Top 15th Percentile** of the `HELIO_TARGET`. Stars are rare; the threshold must reflect that.

---

## The "Non-Obvious" Checklist (Don't Skip)

1.  **The "Efficiency Floor"**: Ensure `REPLACEMENT_LEVEL_TS` is dynamic by season (league average rises over time). Hardcoding 0.54 will punish 2024 players less than 2016 players.
2.  **The "Sample Size" Trap**: Filter the Ground Truth. Don't calculate `HELIO_INDEX` for a player with 10 playoff minutes. They might have 100% TS and break the scale. Enforce `MIN > 50` for target generation.
3.  **The "Role Player" Zero**: Most players will have a `HELIO_INDEX` near 0 (Low Usage or Low Creation). This is correct. The model should predict "0" for 90% of the league. Don't balance the classes artificially.

## Success Metric (Falsification)
- **Gobert Test**: Must classify as `Win-Now Piece` (High Crucible, Low Telescope).
- **DeRozan Test**: Must classify as `Win-Now Piece` or `Ghost` (High Crucible, Low/Mid Telescope).
- **Brunson Test**: Must classify as `Latent Star` (Low Crucible, High Telescope).

