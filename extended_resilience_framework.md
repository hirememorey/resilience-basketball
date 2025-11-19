# Extended Playoff Resilience Framework

## Current State: Phase 5 Complete - Unified Framework Operational ✅

### Project Overview
This project analyzes NBA player performance to identify factors that predict playoff resilience—the ability to maintain or exceed regular-season production in the postseason. We have a complete data pipeline with comprehensive player statistics, shot location data, game logs, and both regular-season and playoff metrics across 10 seasons (2015-16 through 2024-25).

### The "Extended Playoff Resilience Score"
We have successfully implemented a **Five-Pathway Resilience Framework** that measures multiple dimensions of playoff adaptability. The core thesis is that resilience is not one-dimensional; players can survive the playoffs through different "survival strategies."

#### The 5 Pathways (Fully Operational)

1.  **Versatility Resilience (The "Swiss Army Knife")**
    *   **Concept:** Harder to guard if you can score from everywhere.
    *   **Metric:** **Diversity Score** (Inverse HHI).
    *   **Archetype:** **Luka Doncic**. High scores across spatial zones and play types.

2.  **Specialization Mastery (The "Shaq")**
    *   **Concept:** If you are elite at one thing (3 standard deviations above mean), you don't need to be versatile.
    *   **Metric:** **Primary Method Mastery**.
    *   **Archetype:** **Kevin Durant**. Elite efficiency in specific zones (mid-range) that translates to playoffs.

3.  **Role Scalability (The "Jimmy Butler")**
    *   **Concept:** Can you maintain efficiency when your usage spikes?
    *   **Metric:** **Efficiency Slope** (Correlation between Usage & Efficiency).
    *   **Archetype:** **Nikola Jokic**. Gets *more* efficient as he shoulders more load.

4.  **Dominance Resilience (The "Harden/Kobe")**
    *   **Concept:** Can you make bad shots (high contest, low clock)?
    *   **Metric:** **SQAV (Shot Quality-Adjusted Value)**.
    *   **Archetype:** **James Harden**. High ability to hit difficult shots, though often fragile if this is the *only* pathway.

5.  **Longitudinal Evolution (The "Giannis")**
    *   **Concept:** "Neuroplasticity" or Learning Rate. Does the player add new skills over time?
    *   **Metric:** **Adaptability Score**. Counts new "qualified methods" added year-over-year.
    *   **Archetype:** **Giannis Antetokounmpo**. Started raw, added driving, then passing, then mid-range.

---

## Trend Analysis Findings (Pre-Mortem)

We performed a longitudinal analysis (2015-2025) to validate the model. The results confirm that **resilience is a trajectory, not a snapshot.**

| Player | Trend Insight |
| :--- | :--- |
| **Nikola Jokic** | **The Ascendant.** Consistent rise from Versatility (62.7) to elite Scalability (69.8). The model identifies him as the most resilient player in the dataset due to elite scores in 3 pathways. |
| **James Harden** | **The Fragility Curve.** Peaked in 2018 (61.1 - MVP Season) but steadily declined to 55.6 by 2022. His low **Evolution Score (18.4)** successfully predicted his stagnation. |
| **Kevin Durant** | **The Specialist Shift.** Transformed from a Versatile wing in Golden State (56.3) to a pure Specialist in Phoenix (60.1). |
| **Luka Doncic** | **The Early Peak?** Peaked in 2021 (67.8) but has regressed to 57.9 in 2025. Suggests he is becoming more static/predictable despite high volume. |

---

## Technical Implementation Details

### Data Foundation
- **Scope:** 10 full seasons (2015-16 to 2024-25).
- **Granularity:**
    - 272,276 Game Logs.
    - 889,927 Shot Locations (X/Y coordinates).
    - Comprehensive Tracking Data (Drives, Touches, Catch & Shoot).
- **Architecture:** Local SQLite (`nba_stats.db`) with "Historical Processing Mode" for reproducibility.

### Core Scripts
- **`calculate_unified_resilience.py`**: The main engine. Aggregates all 5 pathways and applies dynamic weighting based on the player's primary archetype.
- **`calculate_longitudinal_evolution.py`**: Implements the "Neuroplasticity" logic (counting new skills).
- **`analyze_resilience_trends.py`**: Runs the multi-season analysis to generate career arcs.

### Next Steps
1.  **Refine Dominance Normalization:** The SQAV scores are currently compressed (~50). We need to adjust the sigmoid scaling to differentiate elite shot-makers (KD/Kyrie) more clearly.
2.  **Visualization:** Generate line charts for the trend data to visualize career arcs.
3.  **Final Report:** Publish the findings as a research paper/blog post.
