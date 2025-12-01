# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Current Status:**
*   ✅ **Descriptive Engine:** Fully functional. Calculates "Resilience Scores" for historical playoffs based on performance vs. expectation (accounting for defensive context).
*   ✅ **Predictive Engine:** Fully functional. Predicts future resilience with positive R² using "Performance vs. Top-10 Defenses" and "Consistency" metrics.
*   ✅ **Mechanistic Engine (The Sloan Breakthrough):** **CONFIRMED.** We have identified the mechanism of resilience: **Counter-Punch Efficiency**.
    *   Resilience Correlation: **+0.381 (P < 0.0001)**.
    *   Key Insight: Resilient players are those who maintain efficiency in the *new* zones that playoff defenses force them into.
*   🔄 **Dual-Grade Archetypes (Phase 5b):** We have pivoted to a "Dual-Grade" system that separates **Adaptability** (Efficiency) from **Dominance** (Volume) to correctly classify outliers like Luka Dončić and Ben Simmons. See `LUKA_SIMMONS_PARADOX_UPDATE.md`.

---

## Quick Start for New Developers

### 1. Understand the Vision
*   **`README.md`**: You're here! High-level overview.
*   **`IMPLEMENTATION_PLAN.md`**: **CRITICAL.** Read this to understand the "Plasticity Potential" model and your specific next steps (The "Stress Test").

### 2. Set Up Environment
```bash
# Install dependencies
pip install pandas numpy scikit-learn scipy tenacity requests xgboost tqdm tabulate

# Create required directories
mkdir -p data/cache models results logs
```

### 3. Run the Full Pipeline
This pipeline collects data, generates features, calculates plasticity, and outputs the leaderboard.

```bash
# 1. Collect Shot Charts (Historical & Current)
# Note: This uses parallel workers to respect rate limits while collecting fast.
python src/nba_data/scripts/collect_shot_charts.py --seasons 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 --workers 4

# 2. Calculate Plasticity Metrics (Zone Displacement, Counter-Punch Efficiency)
python src/nba_data/scripts/calculate_shot_plasticity.py

# 3. Generate Correlation Report & Leaderboard
python src/nba_data/scripts/analyze_plasticity_correlation.py
```

**Output:** Check `results/plasticity_scores.csv` and the terminal output for the "Plasticity Leaderboard".

---

## The "Sloan Path" (Phase 5)

We are aiming for a paper worthy of the **MIT Sloan Sports Analytics Conference**.

**Core Finding:** Resilience is "Plasticity"—the ability to adapt efficiency to a forced change in shot diet.
*   **The "Tank" (Jokic):** Displaced from Rim $\to$ Dominates Short Mid-Range.
*   **The "Crumble" (Gobert):** Displaced from Rim $\to$ Efficiency Collapses.

**Next Step:** Proving we can predict this using *Regular Season* data by simulating playoff stress (isolating performance vs. Top-5 Defenses).

See **`IMPLEMENTATION_PLAN.md`** for the detailed roadmap.

---

## Project Structure

```
├── IMPLEMENTATION_PLAN.md          # **START HERE** - The Roadmap
├── src/
│   └── nba_data/
│       ├── api/                    # NBA Stats API client
│       └── scripts/
│           ├── collect_shot_charts.py          # Parallel data collection
│           ├── calculate_shot_plasticity.py    # The Plasticity Engine
│           └── analyze_plasticity_correlation.py # The Validation Engine
├── data/                           # Data storage
│   ├── shot_charts_*.csv           # Raw X,Y shot data
│   └── rs_game_logs_*.csv          # Granular RS data
├── results/                        # Final Scores
│   ├── resilience_scores_all.csv   # Historical Resilience Scores
│   └── plasticity_scores.csv       # The Mechanic Metrics
```

---

## Key Principles

1.  **First Principles Thinking:** Don't just measure *what* happened. Ask *why* it happened given the context.
2.  **Mechanism over Correlation:** We proved that resilience isn't random; it's a specific skill (hitting shots in secondary zones).
3.  **Simplicity in Execution:** We use simple, robust metrics (Efficiency Delta) rather than black-box neural networks.

---

## Support
*   **Technical questions:** Review `src/nba_data/api/nba_stats_client.py` to see how we handle rate limits.
*   **Conceptual questions:** Review `IMPLEMENTATION_PLAN.md`.
