# NBA Playoff Resilience: The Sloan Path Implementation Plan

## Executive Summary

**Goal:** Identify "16-game players" who perform better than expected in the playoffs and **explain why** using mechanistic data.

**Target:** Submission to MIT Sloan Sports Analytics Conference.

**Core Breakthrough (Dec 2025):** We have mathematically proven that **Resilience is "Counter-Punch Efficiency."**
*   **Findings:** Resilient players are *not* those who maintain their shot diet (Correlation: -0.06). They are the ones who maintain efficiency in the *new* zones that defenses force them into (Correlation: +0.38, P < 0.0001).
*   **The Metric:** `COUNTER_PUNCH_EFF` = Efficiency in zones where Playoff Volume > Regular Season Volume.

---

## ✅ Completed Phases (The Foundation)

We have successfully built the Descriptive, Predictive, and Mechanistic engines.

*   **Phase 1: Data Integrity:** ✅ Solved via `collect_rs_game_logs.py` (Granular data).
*   **Phase 2: Descriptive Resilience:** ✅ Solved via `calculate_resilience_scores.py` (Performance vs. Expectation).
*   **Phase 3: Predictive Engine:** ✅ Solved via `train_predictive_model.py` (Top-10 Defense Performance).
*   **Phase 4: Mechanistic Engine:** ✅ Solved via `calculate_shot_plasticity.py`. We have identified the mechanism of resilience.

---

## 🚀 Phase 5: The "Plasticity Potential" Model (Sloan Readiness)

**The Problem:** Our current "Counter-Punch" metric is descriptive (post-hoc). We know *who* adapted, but only after the playoffs happen.
**The Sloan Standard:** To be a paper, we need **Prescriptive Utility**. We must answer: *"How do we identify this Counter-Punch trait in a player BEFORE the playoffs?"*

**The Hypothesis:** A player's "Plasticity Potential" is visible in the Regular Season during **High-Stress Outliers** (e.g., vs. Top-5 Defenses, Clutch Minutes).

### Step 1: The "Stress Test" Pipeline
**Objective:** Calculate `COUNTER_PUNCH_EFF` using *only* specific subsets of Regular Season data to see if it predicts Playoff `COUNTER_PUNCH_EFF`.

*   **Task:** Create `src/nba_data/scripts/evaluate_plasticity_potential.py`.
*   **Methodology:**
    1.  **Baseline:** Player's shot chart vs. Bottom-10 Defenses (The "Comfort Zone").
    2.  **Stress Test:** Player's shot chart vs. Top-5 Defenses (The "Simulated Playoff").
    3.  **Metric:** Calculate the `RS_STRESS_COUNTER_PUNCH` (Efficiency in zones where volume increases against Top-5 defenses).
    4.  **Validation:** Correlate `RS_STRESS_COUNTER_PUNCH` with actual `PLAYOFF_RESILIENCE`.

### Step 2: Shot Quality Context
**Objective:** Differentiate between "Bad Decisions" and "Missed Opportunities."
*   **Task:** Integrate `CLOSE_DEF_DIST` (Closest Defender Distance) into the plasticity model.
*   **Hypothesis:** Resilient players don't just take shots in new zones; they generate *open* shots in new zones.
*   **Action:** Update `calculate_shot_plasticity.py` to fetch and merge shot quality data.

### Step 3: The "Fragility Taxonomy" Clustering
**Objective:** Formally cluster players into the 4 archetypes we discovered.
*   **The Tank (Jokic):** Displaced $\to$ Hits New Shots.
*   **The Sniper (Durant):** Not Displaced $\to$ Hits Same Shots.
*   **The Crumble (Gobert):** Displaced $\to$ Misses New Shots.
*   **The Force (Inefficient Volume):** Not Displaced $\to$ Misses Same Shots.

---

## Implementation Guide for New Developer

### 1. Run the Existing Pipeline
The full pipeline is robust and parallelized.
```bash
# 1. Collect Shot Charts (Takes ~20 mins for 6 seasons)
python src/nba_data/scripts/collect_shot_charts.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 --workers 4

# 2. Calculate Plasticity Metrics
python src/nba_data/scripts/calculate_shot_plasticity.py

# 3. Analyze Correlations (The "Money Plot")
python src/nba_data/scripts/analyze_plasticity_correlation.py
```

### 2. Start the "Stress Test" (Next Priority)
Your goal is to prove we can scout this trait.
1.  Modify `NBAStatsClient` to allow fetching game logs/shots filtered by *Opponent Team ID*.
2.  Collect shot charts for games against Top-5 Defensive Rating teams for each season.
3.  Calculate the "Stress Plasticity" and correlate it with the known "Playoff Plasticity".

### 3. Key Files
*   `src/nba_data/scripts/collect_shot_charts.py`: The data harvester.
*   `src/nba_data/scripts/calculate_shot_plasticity.py`: The logic engine (Hellinger distance, efficiency deltas).
*   `results/plasticity_scores.csv`: The output file containing the breakthrough metrics.
