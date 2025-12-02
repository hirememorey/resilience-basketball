# Extended Playoff Resilience Framework

## 🚨 Project Update: The Dual-Grade Evolution (Dec 2025)

**Note:** This document outlines the original "5-Pathway" framework. While the core principles remain valid, the implementation has been streamlined into the **Dual-Grade Archetype System** to solve the "Luka & Simmons Paradox".

**Current Implementation:**
The 5 pathways have been synthesized into two primary axes:
1.  **Adaptability (Resilience Quotient):** Synthesizes *Versatility*, *Role Scalability*, and *Evolution*.
2.  **Dominance (Dominance Score):** Synthesizes *Dominance Resilience* and *Crucible Baseline*.

**See `LUKA_SIMMONS_PARADOX.md` for the current, active framework.**

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

## 4. The Five-Pathway Framework (Theoretical Basis)

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
- **Architecture:** Local SQLite (`nba_stats.db`) and CSV.
- **Status:** Fully populated with clean data for all seasons.

### Core Scripts
- **`calculate_simple_resilience.py`**: **The Main Engine.** Calculates the Dual-Grade Archetypes (RQ + Dominance).
- **`calculate_shot_plasticity.py`**: The original mechanistic engine (Legacy/Research).

### Next Steps
1.  **Visualization:** Generate career arc charts.
2.  **Predictive Modeling:** Use RS "Stress Tests" to predict Playoff Archetypes.
