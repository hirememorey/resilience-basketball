# Extended Playoff Resilience Framework

## 🚨 Project Pivot: Addressing Critical Feedback & New Philosophy

**This project has undergone a critical philosophical pivot.** Initial analysis focused on measuring resilience as an *intrinsic player trait*. Based on critical feedback, we now understand this is flawed. The model's original failure modes stemmed from the gap between *what* happened and *why* it happened.

**New Philosophy: Resilience is a Conditional Probability.** A player's resilience is not a static score; it is a dependent variable contingent on specific constraints like defensive schemes, offensive systems, teammate gravity, and resource consumption (i.e., time of possession).

Our new mandate is to measure **Process Independence** over raw production.

### The Five Failure Modes We Must Now Address:
This new approach is a direct response to five identified blind spots in the original model:

1.  **The Defensive Scheme Blind Spot (Context Vacuum):** The old model rewarded "versatility" without understanding dependencies. A player scoring in three ways that all rely on a single action (e.g., a kick-out from a primary ball-handler) is not versatile, but fragile. **The Fix: We must measure "Creation Independence" by factoring in `% Assisted` data.**
2.  **The "Heliocentric" Illusion (System vs. Skill):** The old model conflated a player's skill with their coaching system. It couldn't distinguish between "cannot do it" and "is not asked to do it" (e.g., Jalen Brunson in Dallas vs. New York). **The Fix: We will normalize for "Opportunity Density" by measuring `Points Per Touch-Second` to identify latent scalability.**
3.  **The "League Average" Denominator Flaw:** The old model's "Dominance" score (SQAV) compared players against a regular-season baseline, which is statistically incongruent with playoff intensity. **The Fix: We must create a "Crucible Baseline" by comparing performance against only Top-10 rated defenses.**
4.  **The "Portfolio Theory" Problem (Actionability Gap):** The old model treated players as independent variables, ignoring that high-usage, high-resilience players cannibalize each other's resources. **The Fix: We will introduce a "Resource Cost" (e.g., High/Low Friction) to each resilience score.**
5.  **The "Lagging Indicator" of Evolution:** The old model's "Neuroplasticity" metric was too slow, confirming evolution only after a player was already on a max contract. **The Fix: We will detect "Micro-Evolution" by tracking changes in *attempt rates* within a single season.**

---
## Data Integrity Post-Mortem: A Warning for New Developers

The most significant roadblock in the initial implementation was not complex logic, but **silent data corruption.** A series of shortcuts during initial data population created latent integrity issues that made all downstream analysis unreliable.

**Before writing any new analysis, understand these core lessons:**

1.  **Your Schema is Your Constitution:** The original `player_season_stats` table was missing a `season_type` column in its primary key, causing "Regular Season" and "Playoffs" data to collide. This has been fixed. **Instruction:** Rigorously define uniqueness constraints for any new table. The database should physically prevent you from making data-quality errors.
2.  **Never Trust, Always Verify:** The initial population scripts ran without crashing but were silently inserting incorrect data. **Instruction:** For every population script, a corresponding validation script (like the new `validate_integrity.py`) is mandatory. It must perform presence, sanity, and joinability checks.
3.  **Eliminate "Magic Numbers":** The entire data foundation was corrupted by a placeholder `team_id` (`1610612760`). This has been fixed by fetching the real `team_id` from the API. **Instruction:** There is no such thing as a temporary placeholder for a foreign key. A `NULL` value is honest; a fake value is a lie that your code will treat as fact.

---
## 1. The Goal (The "Why")

The ultimate goal is to build a predictive model that moves beyond traditional box score stats to identify the factors that make an NBA player's performance resilient to postseason pressure. We aim to create a quantifiable "Playoff Resilience Score" that can help basketball decision-makers make more informed, championship-focused investments.

## 2. The Core Problem

Regular-season performance is an imperfect predictor of postseason success. The game changes—defensive intensity increases, rotations shorten, and opponents exploit specific weaknesses. This project addresses the critical gap in understanding the *leading indicators* of playoff adaptability. We are not just asking "who succeeded," but "why did they succeed, and can we predict it in advance?"

## 3. Core Hypotheses

1.  **Method Resilience Predicts Playoff Success:** A player who demonstrates a measurable diversification of their *scoring methods* is more likely to maintain performance. A diverse skillset is harder to neutralize.
2.  **Method Over-Specialization Creates Fragility:** Players who rely on a narrow set of offensive actions are more susceptible to targeted defensive schemes.
3.  **Adaptability is a Measurable Skill:** The "rate of change" in a player's statistical profile over time is a variable we can test as a predictor of future success under pressure.
4.  **The "Neuroplasticity Coefficient" Predicts Future Resilience:** Future resilience is predicted by the **rate of new method acquisition**, not by age or athleticism. Draft for "learning rate."

## 4. The Five-Pathway Framework (As Originally Conceived)

*This section outlines the original five pathways. Note that the "Project Pivot" described above requires us to refine how these are calculated.*

1.  **Versatility Resilience (The "Swiss Army Knife")**
    *   **Concept:** Harder to guard if you can score from everywhere.
    *   **Metric:** **Diversity Score** (Inverse HHI).
    *   **Archetype:** **Luka Doncic**.

2.  **Specialization Mastery (The "Shaq")**
    *   **Concept:** If you are elite at one thing, you don't need to be versatile.
    *   **Metric:** **Primary Method Mastery**.
    *   **Archetype:** **Kevin Durant**.

3.  **Role Scalability (The "Jimmy Butler")**
    *   **Concept:** Can you maintain efficiency when your usage spikes?
    *   **Metric:** **Efficiency Slope** (Correlation between Usage & Efficiency).
    *   **Archetype:** **Nikola Jokic**.

4.  **Dominance Resilience (The "Harden/Kobe")**
    *   **Concept:** Can you make bad shots (high contest, low clock)?
    *   **Metric:** **SQAV (Shot Quality-Adjusted Value)**.
    *   **Archetype:** **James Harden**.

5.  **Longitudinal Evolution (The "Giannis")**
    *   **Concept:** "Neuroplasticity" or Learning Rate. Does the player add new skills over time?
    *   **Metric:** **Adaptability Score**.
    *   **Archetype:** **Giannis Antetokounmpo**.

---
## 5. Technical Implementation & Current Status

### Data Foundation & Recent Fixes
- **Scope:** 10 full seasons (2015-16 to 2024-25).
- **Architecture:** Local SQLite (`nba_stats.db`).
- **CRITICAL FIX (Nov 2025):** The data integrity has been overhauled.
    - The schema for core stats tables (`player_season_stats`, `player_advanced_stats`, `player_tracking_stats`) has been **updated to include `season_type` in the primary key.**
    - The data population scripts have been **fixed and executed.**
    - The database is now **fully populated with clean data for all seasons from 2015-16 to 2024-25,** for both Regular Season and Playoffs.

### Core Scripts
- **`calculate_unified_resilience.py`**: The main engine (aggregates the 5 pathways). **NOTE: This script needs to be updated to reflect the new philosophical pivot.**
- **Population Scripts:** Reside in `src/nba_data/scripts/` and are used to fetch data from the API.
- **Validation Script:** `src/nba_data/scripts/validate_integrity.py` **must be run** after any data population to ensure data health.

### Next Steps (The New Roadmap)
1.  **✅ Repopulate Historical Data:** Run the fixed population scripts for all seasons from 2015-16 to 2023-24 for both "Regular Season" and "Playoffs".
2.  **Implement Team Ratings Ingestion:** Create a script to populate team-level defensive ratings for each season. This is required for the "Crucible Baseline".
3.  **Refactor Resilience Calculations:** Update the analysis scripts (`calculate_...`) to implement the new logic:
    - `Dependency-Weighted Versatility Score`
    - `Friction Score` (Points per Touch-Second)
    - `Crucible-Adjusted Dominance Score`
4.  **Visualize:** Generate career arc charts for the new, more robust metrics.

---
### Implementation Progress
- **✅ Friction Score Data Pipeline:** The necessary possession metrics (`AVG_SEC_PER_TOUCH`, `AVG_DRIB_PER_TOUCH`, `PTS_PER_TOUCH`, `TIME_OF_POSS`, `FRONT_CT_TOUCHES`) have been successfully integrated and verified.
- **✅ Historical Data Backfill:** The database now contains 10 seasons of player and game data.
- **✅ Team Ratings:** Team defensive ratings data is available in `team_season_stats` table.
- **✅ Friction Score Resilience:**
  - **Complete & Validated:** `calculate_friction.py` now correctly measures the delta between Regular Season and Playoff efficiency.
  - **Data Integrity Fix:** Fixed a critical bug where Playoff tracking data was identical to Regular Season data due to an API client error.
  - **Results:** successfully identified "Resilient" high-usage players (e.g., Damian Lillard -7.26 Delta) vs. "Fragile" players (e.g., Anthony Edwards +5.15 Delta) for the 2023-24 season.
- **🔄 Logic Bridge Progress:**
  - **✅ Friction Score Calculation:** **COMPLETE & VERIFIED**.
  - **🔄 Crucible Baseline:** Started implementation, data foundation ready.
  - **⏳ Dominance Score:** Shot dashboard data fixed with combinatorial approach (13K+ rows), ready for calculation.
  - **⏳ Unified Resilience:** Integration of all metrics pending.

### Key Fixes Implemented
- **Tracking Data Integrity:** Discovered and fixed a silent failure where `NBAStatsClient` was hardcoding `SeasonType="Regular Season"`, causing Playoff data to be corrupted. All 2023-24 tracking data has been repopulated and verified.
- **Shot Dashboard Data Integrity:** Fixed the "fragmented rows" issue by implementing combinatorial API fetching instead of independent loops. This provides true intersectional data for shot quality analysis.
- **Player Metadata:** Minimal player table populated (1,437 players) to enable JOIN operations for analysis scripts.
- **Data Verification:** All foundational data tables are populated and verified to work together.
