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

## 🚀 Phase 5: The "Stylistic Stress Test" Predictive Model (Sloan Readiness)

**The Problem:** We now have perfect *labels* (King, Bulldozer, Victim, Sniper). We need to *predict* them using only Regular Season data.

**The Sloan Standard:** To be a paper, we need **Prescriptive Utility**. We must answer: *"How do we identify a 'King' BEFORE the playoffs?"*

---

### Critical Lessons from V1 (The Post-Mortem)
Our initial attempt to solve this by simply filtering RS data for games against "Top-5 Defenses" failed (correlation of 0.08). The post-mortem revealed critical insights that now guide our V2 approach:

1.  **The "Different Sport" Fallacy:** RS "Stress" is not the same as Playoff "Stress." Playoff pressure is about *schematic removal*, not just better opponents. We cannot simply filter game logs; we must find proxies for the *stylistic shift* that occurs in the postseason.
2.  **The "Identifier Hell" Fix:** The NBA API uses inconsistent team IDs. A canonical `teams.py` or `constants.py` file with hardcoded ID-to-Abbreviation maps is the first step to prevent hours of debugging.
3.  **The "Metric Drift" Reality:** "Plasticity" is a vector, not a scalar. A player changing their shot chart (displacement) is only meaningful in context. For a star, it can be adaptation (good); for a role player, it can mean being forced from their spots (bad).

---

### The V2 Plan: The "Stylistic Stress Test" Pipeline
**The Hypothesis:** A player's resilience is visible in RS situations that mimic the three core stylistic shifts of the playoffs: **1) Increased Self-Creation**, **2) Higher Leverage**, and **3) Schematic Pressure**.

#### Step 1: Feature Engineering (The "Stress Vectors")
**Objective:** Create features that measure a player's performance under these specific stylistic pressures. This will be done in a new script: `src/nba_data/scripts/evaluate_plasticity_potential.py`.

*   **Vector 1: The "Isolation" Vector (Self-Creation)**
    *   **Theory:** Assisted looks disappear in the playoffs. We need to measure a player's ability to create their own shot.
    *   **Source:** `ShotDashboardClient` (Dribble Ranges).
    *   **Metric:** `Creation_Tax` = (Efficiency on 3+ Dribbles) / (Efficiency on 0 Dribbles).

*   **Vector 2: The "Clutch" Vector (Leverage)**
    *   **Theory:** Clutch minutes (last 5 mins, score +/- 5) are the best proxy for playoff intensity.
    *   **Source:** `leaguedashplayerclutch` endpoint (needs to be added to `NBAStatsClient`).
    *   **Metric:** `Leverage_Delta` = (Clutch Usage - Season Usage) and (Clutch TS% - Season TS%).

*   **Vector 3: The "Quality of Competition" Vector**
    *   **Theory:** A simplified, more robust version of the original "Stress Test."
    *   **Source:** Regular Season Game Logs.
    *   **Metric:** `QoC_Ratio` = (Performance vs. Top 10 Defenses) / (Performance vs. Bottom 10 Defenses).

#### Step 2: Modeling (Non-Linearity is Key)
**Objective:** Train a model that can understand the complex, non-linear interactions between these features.

*   **Methodology:** An **XGBoost Classifier**. A linear model will fail because the "Stress Vectors" have different meanings for different archetypes.
*   **Target:** The `archetype` column from `results/resilience_archetypes.csv`.

---

## Implementation Guide for New Developer

### 1. Review the Current State
The current "Truth" of the project is in the Archetypes.
1.  Check `results/resilience_archetypes.csv`.
2.  Visualize with `results/resilience_archetypes_plot.png`.
3.  Understand the logic in `src/nba_data/scripts/calculate_simple_resilience.py`.

### 2. Your Mission: Build the Predictive Engine (V2)
Your goal is to predict the archetypes using the "Stylistic Stress Test" approach.
1.  **Infrastructure:** Create `src/nba_data/constants.py` and hardcode the Team ID/Abbreviation maps.
2.  **API Expansion:** Add the `get_league_player_clutch_stats` endpoint to `src/nba_data/api/nba_stats_client.py`.
3.  **Feature Engineering:** Create `src/nba_data/scripts/evaluate_plasticity_potential.py`. This script will fetch all the necessary data (Game Logs, Shot Dashboards, Clutch Stats) and engineer the "Stress Vector" features.
4.  **Prediction:** Train an XGBoost classifier to predict `ARCHETYPE` using the features created in the previous step.
5.  **Validation:** Correlate your predictions with the actual Playoff Archetypes to validate the model.

### 3. Key Files for This Phase
*   `src/nba_data/scripts/calculate_simple_resilience.py`: The engine that generates your **target labels**.
*   `LUKA_SIMMONS_PARADOX.md`: The bible for *why* we use the current labels.
*   `src/nba_data/api/nba_stats_client.py`: The client you will need to extend.
