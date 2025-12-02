# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Current Status:**
*   ✅ **Data Foundation:** Complete historical dataset (2015-2024) with Regular Season, Playoff Logs, and Defensive Context.
*   ✅ **The Paradox Solved:** We have successfully addressed the "Luka Dončić Paradox" (False Negative) and "Ben Simmons Paradox" (False Positive) using the **Dual-Grade Archetype System**.
*   ✅ **Dual-Grade System:** Players are now evaluated on two axes:
    1.  **Resilience Quotient (RQ):** Adaptability (Volume × Efficiency retention).
    2.  **Dominance Score:** Absolute Value (Playoff PTS/75).
*   ✅ **Historical Validation:** The model correctly classifies historical outliers (Jokić as "King", Simmons as "Victim", Harden as "Bulldozer").

---

## Quick Start for New Developers

### 1. Understand the Vision
*   **`LUKA_SIMMONS_PARADOX.md`**: **CRITICAL.** Read this to understand the core problem we solved and the logic behind the current "Dual-Grade" model.
*   **`IMPLEMENTATION_PLAN.md`**: The roadmap for the "Plasticity Potential" predictive model (The Sloan Paper goal).

### 2. Set Up Environment
```bash
# Install dependencies
pip install pandas numpy scikit-learn scipy tenacity requests xgboost tqdm tabulate seaborn matplotlib

# Create required directories
mkdir -p data/cache models results logs
```

### 3. Run the Resilience Engine
This pipeline collects data, builds the dataset, and calculates the Archetypes.

```bash
# 1. Collect Data (if needed)
# Note: The repository should contain the CSVs in data/. If not:
python src/nba_data/scripts/collect_regular_season_stats.py --seasons 2015-16 ... 2023-24
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2015-16 ... 2023-24 --workers 4

# 2. Assemble Training Data
python src/nba_data/scripts/assemble_training_data.py

# 3. Calculate Archetypes & Generate Plot
python src/nba_data/scripts/calculate_simple_resilience.py
```

**Output:**
*   **`results/resilience_archetypes.csv`**: The master file with RQ, Dominance, and Archetypes for every player-series (2015-2024).
*   **`results/resilience_archetypes_plot.png`**: The scatter plot visualization.

---

## The "Sloan Path" (Phase 5)

We are aiming for a paper worthy of the **MIT Sloan Sports Analytics Conference**.

**Core Finding:** Resilience is not just about "making shots"—it's about the trade-off between **Adaptability** and **Dominance**.
*   **The King:** Maintains Efficiency AND Volume (Jokić).
*   **The Bulldozer:** Sacrifices Efficiency to maintain Volume (Luka).
*   **The Victim:** Sacrifices Volume to maintain Efficiency (Simmons).

**Next Step:** Proving we can predict these Archetypes using *Regular Season* data by simulating playoff *stylistic shifts* (isolating performance in clutch, self-created, and high-pressure situations).

See **`IMPLEMENTATION_PLAN.md`** for the detailed roadmap.

---

## Project Structure

```
├── LUKA_SIMMONS_PARADOX.md         # The Theoretical Foundation (Problem & Solution)
├── IMPLEMENTATION_PLAN.md          # The Roadmap
├── src/
│   └── nba_data/
│       ├── api/                    # NBA Stats API client
│       └── scripts/
│           ├── collect_*.py                    # Data collection scripts
│           ├── assemble_training_data.py       # Data merger
│           └── calculate_simple_resilience.py  # The Dual-Grade Engine (Current Production)
├── data/                           # Data storage
│   ├── regular_season_*.csv        # RS Stats
│   ├── playoff_logs_*.csv          # Playoff Game Logs
│   └── training_dataset.csv        # The assembled master dataset
├── results/                        # Final Scores
│   ├── resilience_archetypes.csv   # The Archetype Classifications
│   └── resilience_archetypes_plot.png
```

---

## Key Principles

1.  **First Principles Thinking:** Don't just measure *what* happened. Ask *why* it happened given the context.
2.  **Resilience = Efficiency × Volume:** You cannot measure resilience without accounting for the "Abdication Tax" (Passivity).
3.  **Absolute Dominance:** In the playoffs, absolute production matters more than relative improvement.

---

## Support
*   **Technical questions:** Review `src/nba_data/api/nba_stats_client.py` to see how we handle rate limits.
*   **Conceptual questions:** Review `LUKA_SIMMONS_PARADOX.md`.
