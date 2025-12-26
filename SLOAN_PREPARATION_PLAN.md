# Sloan Sports Analytics Conference: Preparation Plan

## Primary Objective: From "Predictive Model" to "Simulation Engine"

To succeed at Sloan, we must evolve beyond descriptive accuracy ("*who* is a good player") and deliver prescriptive utility ("*how* a player's value changes with context").

The goal is to present a **"Universal Avatar" Simulation Engine**. This engine will take our core metrics (`HELIO_POTENTIAL_SCORE`, `CRUCIBLE_SCORE`) and project a player's performance into different offensive roles and defensive environments, providing a dynamic understanding of their scalability.

---

## 1. The Highest Leverage Action: "Universal Avatar" Integration

**Action**: Implement the **Universal Projection Integration** engine (`src/nba_data/utils/projection_utils.py`). The focus is to transform our static scores into a dynamic simulation tool.

**Why (First Principles Analysis):**
- **Principle**: `Value = Capacity × Context`.
- **Current State**: We have excellent metrics for **Capacity** (Telescope/Helio Score) and **Viability** (Crucible Score).
- **The Gap**: We currently treat these as static labels. The "Universal Avatar" will allow us to simulate how a player's efficiency and impact change as their context (usage, defensive attention) changes.
- **The Payoff**: This transforms the project from a "Classification Task" into a "Simulation Engine," which is the key differentiator for a Sloan-level presentation.

---

## 2. De-Risking the Implementation: Key Failure Modes & Mitigations

### A. Failure Mode: The "Linear Extrapolation" Fallacy
- **The Trap**: Assuming a player's efficiency scales linearly as their usage increases. This violates the **Law of Friction**.
- **De-Risking Plan**: Enforce **"Friction Curves"** in the projection engine. The `SHOT_QUALITY_GENERATION_DELTA` must dictate the friction coefficient.
    - **High `SQ_DELTA` (e.g., Jalen Brunson)**: Apply **Low Friction**. Efficiency is resilient as usage rises.
    - **Low `SQ_DELTA` (e.g., Jordan Poole)**: Apply **High Friction**. Efficiency drops steeply as usage rises.

### B. Failure Mode: The "Context Vacuum"
- **The Trap**: Projecting a player's resilience against a "league average" defense, which doesn't exist in the playoffs.
- **De-Risking Plan**: Implement a **"Stress Test" Toggle**. The projection should not be a single number but a *range of outcomes*.
    - **Implementation**: Visualize the projection as: *"Projected Output vs. Pistons"* (high) vs. *"Projected Output vs. Celtics"* (low), using our `vs_top10` and `vs_elite_defense` context metrics.

### C. Failure Mode: "Metric Soup" (The Presentation Killer)
- **The Trap**: Presenting a table of raw scores, which is complex and lacks a clear takeaway.
- **De-Risking Plan**: Create the **"2D Risk Matrix" Visualization**. This is the "money slide" for the presentation.
    - **Implementation**: Use Streamlit to plot players on a 2D plane defined by two axes: **Scalability (Y-Axis)** and **Resilience (X-Axis)**. This will map every player to one of four clear archetypes:
        1.  **Helio-Engine** (High Scale, High Resilience)
        2.  **Floor-Raiser** (High Scale, Low Resilience)
        3.  **Ceiling-Raiser** (Low Scale, High Resilience)
        4.  **Empty Calories** (Low Scale, Low Resilience)

---

## 3. Checklist for Next Developer

1.  [ ] **Implement Projection Engine**:
    -   **File**: `src/nba_data/utils/projection_utils.py`.
    -   **Core Logic**: Ensure `SHOT_QUALITY_GENERATION_DELTA` dynamically adjusts the friction curve for player projections.

2.  [ ] **Verify the "Stress Test"**:
    -   **Action**: Run both a "Low SQ_DELTA" player (Jordan Poole) and a "High SQ_DELTA" player (Jalen Brunson) through the *new projection engine*.
    -   **Expected Outcome**: The visualization should clearly show Poole's efficiency collapsing under high usage, while Brunson's remains stable.

3.  [ ] **Build the "2D Risk Matrix" Visualization**:
    -   **Tool**: Streamlit.
    -   **Goal**: Create the final 4-quadrant chart that maps players to the Sloan-ready archetypes. This is the primary deliverable.

## Historical Context: Phase 4 Summary (Completed Work)

- **Telescope Model Calibrated**: The model can now accurately predict `FUTURE_PEAK_HELIO`, with `HELIO_POTENTIAL_SCORE` as its primary driver.
- **Magnitude Matching Verified**: Correctly predicts the superstar peaks of Jalen Brunson and Tyrese Maxey.
- **"Mirage Breakout" Filter Validated**: Successfully distinguishes "Empty Calories" players like Jordan Poole and DeMar DeRozan from true stars.
- **Data Integrity Hardened**: The feature engineering pipeline is now robust and the single source of truth for the validation suite.
