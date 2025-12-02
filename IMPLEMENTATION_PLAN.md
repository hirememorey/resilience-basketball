# NBA Playoff Resilience: The Sloan Path Implementation Plan

## Executive Summary

**Goal:** Identify "16-game players" who perform better than expected in the playoffs and **explain why** using mechanistic data.

**Target:** Submission to MIT Sloan Sports Analytics Conference.

**Core Breakthrough (Dec 2025):** We have solved the **Luka/Simmons Paradox** by establishing the **Dual-Grade Archetype System**. Resilience is defined as the interaction between **Adaptability** (Resilience Quotient) and **Dominance** (Absolute Value).

---

## ✅ Completed Phases (The Foundation)

We have successfully built the Descriptive, Predictive, and Mechanistic engines.

*   **Phase 1: Data Integrity:** ✅ Solved. Full historical dataset (2015-2024) collected and verified.
*   **Phase 2: Descriptive Resilience:** ✅ Solved. The "Dual-Grade" system correctly classifies historical outliers.
*   **Phase 3: Predictive Engine:** ✅ Initial "Plasticity" model showed promise; now needs retraining on the new Archetype labels.
*   **Phase 4: The Paradox Fix:** ✅ Solved. `LUKA_SIMMONS_PARADOX.md` details the resolution.

---

## 🚀 Phase 5: The "Plasticity Potential" Model (Sloan Readiness)

**The Problem:** We now have perfect *labels* (King, Bulldozer, Victim, Sniper). We need to *predict* them.

**The Sloan Standard:** To be a paper, we need **Prescriptive Utility**. We must answer: *"How do we identify a 'King' BEFORE the playoffs?"*

**The Hypothesis:** A player's "Plasticity Potential" is visible in the Regular Season during **High-Stress Outliers** (e.g., vs. Top-5 Defenses, Clutch Minutes).

### Step 1: The "Stress Test" Pipeline (NEXT PRIORITY)
**Objective:** Calculate `RS_STRESS_METRICS` using *only* specific subsets of Regular Season data.

*   **Task:** Create `src/nba_data/scripts/evaluate_plasticity_potential.py`.
*   **Methodology:**
    1.  **Baseline:** Player's performance vs. Bottom-10 Defenses (The "Comfort Zone").
    2.  **Stress Test:** Player's performance vs. Top-5 Defenses (The "Simulated Playoff").
    3.  **Metric:** Calculate the drop-off in Volume and Efficiency under stress.
    4.  **Validation:** Correlate `RS_STRESS_DROP_OFF` with actual `RESILIENCE_QUOTIENT` and `ARCHETYPE`.

### Step 2: Addressing Critical Failure Modes (Luka & Simmons)
**Status: COMPLETED (Dec 2025).**
We successfully resolved the paradoxes using the Dual-Grade system.
*   **See:** `LUKA_SIMMONS_PARADOX.md`
*   **Code:** `src/nba_data/scripts/calculate_simple_resilience.py`

### Step 3: The "Fragility Taxonomy" Clustering
**Status: COMPLETED (Dec 2025).**

We formally clustered players into 4 archetypes:
*   **King (Resilient Star):** High RQ, High Dominance.
*   **Bulldozer (Fragile Star):** Low RQ, High Dominance.
*   **Sniper (Resilient Role):** High RQ, Low Dominance.
*   **Victim (Fragile Role):** Low RQ, Low Dominance.

**See:** `results/resilience_archetypes.csv`

---

## Implementation Guide for New Developer

### 1. Review the Current State
The current "Truth" of the project is in the Archetypes.
1.  Check `results/resilience_archetypes.csv`.
2.  Visualize with `results/resilience_archetypes_plot.png`.
3.  Understand the logic in `src/nba_data/scripts/calculate_simple_resilience.py`.

### 2. Start the "Stress Test" (Your Mission)
Your goal is to predict these archetypes.
1.  **Feature Engineering:** Use `NBAStatsClient` to fetch RS Game Logs.
2.  **Filtering:** Filter for games against Top-5 Defensive Rating teams.
3.  **Calculation:** Calculate `RS_Stress_Vol_Ratio` and `RS_Stress_Eff_Ratio`.
4.  **Prediction:** Train a classifier (XGBoost/RandomForest) to predict `ARCHETYPE` using these RS Stress features.

### 3. Key Files
*   `src/nba_data/scripts/calculate_simple_resilience.py`: The engine that generates the target labels.
*   `LUKA_SIMMONS_PARADOX.md`: The bible for why we use this metric.
*   `src/nba_data/scripts/collect_regular_season_stats.py`: The data harvester.
