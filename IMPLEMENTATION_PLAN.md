# NBA Playoff Resilience: The Sloan Path Implementation Plan

## Executive Summary

**Goal:** Identify "16-game players" who perform better than expected in the playoffs and **explain why** using mechanistic data (Shot Diet Plasticity).

**Target:** Submission to MIT Sloan Sports Analytics Conference.

---

## ✅ Completed Phases (The Foundation)

We have successfully built the Descriptive and Predictive engines. **Do not re-invent these.**

*   **Phase 1: Data Integrity:** ✅ Solved via `collect_rs_game_logs.py` (Granular data).
*   **Phase 2: Descriptive Resilience:** ✅ Solved via `calculate_resilience_scores.py`. We have ground-truth scores based on performance vs. expectation.
*   **Phase 3: Predictive Engine:** ✅ Solved via `train_predictive_model.py`. We can predict resilience with positive R² using "Performance vs. Top-10 Defenses".

---

## 🚀 Phase 4: The Sloan Path (Shot Diet Plasticity)

**The Problem:** Our predictive model knows *who* is resilient (e.g., players with high usage vs. Top-10 defenses), but it doesn't explain *how* they adapt.
**The Hypothesis:** Resilience is the ability to fundamentally change your shot profile in response to playoff defenses (e.g., "taking what the defense gives you" but actually making it).

### Step 1: Collect Shot Chart Data
**Objective:** Get X,Y coordinates for every shot taken by relevant players in both RS and PO.
*   **Source:** `shotchartdetail` endpoint (Already in `NBAStatsClient`).
*   **Task:** Create `src/nba_data/scripts/collect_shot_charts.py`.
*   **Scope:** Same 6 seasons (2018-24).
*   **Storage:** `data/shot_charts_{season}.csv`.

### Step 2: Feature Engineering (The "Plasticity" Metrics)
**Objective:** Quantify the difference between a player's RS and PO shot profile.
*   **Task:** Create `src/nba_data/scripts/calculate_shot_plasticity.py`.
*   **Key Metrics to Prototype:**
    1.  **Shot Distance Shift:** `Avg_Shot_Dist_PO` - `Avg_Shot_Dist_RS`. (Do they get pushed out?)
    2.  **Zone Migration:** Change in % of shots at Rim, Mid-Range, Corner 3, Above Break 3.
    3.  **Self-Creation Delta:** Change in `% Unassisted` (if available in shot chart, otherwise merge with logs).
    4.  **Hellinger Distance:** (Advanced) A statistical measure of the divergence between two 2D spatial distributions (RS Heatmap vs. PO Heatmap).

### Step 3: Correlation Analysis
**Objective:** Prove that "Plasticity" correlates with "Resilience."
*   **Task:** Merge `plasticity_features` with `resilience_scores_all.csv`.
*   **Hypothesis Check:**
    *   Do high-resilience players have *higher* plasticity (adaptability)?
    *   Or do they have *lower* plasticity (imposing their will)?
    *   *Note:* It likely varies by archetype (Bigs vs. Guards).

### Step 4: The "Fragility Taxonomy"
**Objective:** Cluster non-resilient players into failure modes.
*   **Analysis:** Using the new metrics, identify:
    1.  **The Shrinker:** Volume drops, locations stay same.
    2.  **The Pushed-Out:** Volume stays same, shot distance increases significantly (forced into bad shots).
    3.  **The Bricklayer:** Volume/Locations same, Efficiency drops (just missing open shots?).

---

## Implementation Guide for New Developer

1.  **Start with Data:** Run `collect_shot_charts.py` (you need to write this).
    *   *Tip:* Use the `NBAStatsClient.get_player_shot_chart` method.
    *   *Tip:* Re-use the `ThreadPool` pattern from `collect_rs_game_logs.py` to speed it up.

2.  **Build the Metric:** Start simple. Just calculate **"Change in % of shots taken from Mid-Range."**
    *   If Resilient players take *more* mid-range shots in playoffs (counter-intuitive to Moreyball), that is a Sloan-worthy finding.

3.  **Validate:** Check this metric against **Kawhi Leonard (2019)**. He is the prototype of "Mid-Range Resilience."

---

## Success Criteria for Phase 4

*   [ ] Shot chart data collected for 2018-24.
*   [ ] "Shot Plasticity" metrics calculated for all qualified players.
*   [ ] Correlation analysis showing relationship between Plasticity and Resilience.
*   [ ] A clear narrative: "Resilient players adapt by [doing X], while Fragile players fail by [doing Y]."
