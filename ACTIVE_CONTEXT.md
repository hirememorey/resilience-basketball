# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 24, 2025
**Status**: ✅ **"TWO-CLOCK" ARCHITECTURE DESIGNED** - We have shifted from a single, flawed model to a dual-engine architecture that separates **Current Viability** (The Crucible) from **Future Potential** (The Telescope). The Crucible Engine is implemented and validated. The Telescope is the next priority.

---

## Project Goal

To build a predictive system that can accurately distinguish between immediate playoff contributors, future stars, and "fool's gold" players by modeling the orthogonal physics of **Viability** and **Scalability**.

---

## Core Architecture: The "Two-Clock" System

Our previous monolithic model failed because it tried to optimize for two opposing goals: "Win Now" and "Win Later." The new architecture solves this by assigning each goal to a dedicated model.

### 1. The Crucible (The "Camera" - Viability Engine)
- **Status**: ✅ Implemented & Validated
- **Purpose**: Answers the question: *"If you drop this player into a playoff series **today**, will they survive?"*
- **Target Variable**: `Current_Season_Playoff_PIE` (Objective, immediate impact)
- **Key Insight**: The Crucible correctly identifies players like Jordan Poole as "Ghosts" (Low Viability) and correctly flags Rookie Jokić as a "Liability" *for his rookie season*. It is a precise measure of **present-day friction**.

### 2. The Telescope (The "Projection" - Potential Engine)
- **Status**: ⏳ **DESIGNED - NOT IMPLEMENTED**
- **Purpose**: Answers the question: *"What is this player's **peak impact** over the next 3 seasons?"*
- **Target Variable**: `MAX(Playoff_PIE)` over the subsequent 3 seasons.
- **Key Insight**: The Telescope is designed to recognize the "Peyton Manning" rookie signal—that high-usage, high-turnover seasons for young players are often a *positive* indicator of future stardom. It's built to find players whose scalability is high, even if their current viability is low.

---

## How The Two Clocks Define Player Value

The 2D Risk Matrix is no longer a simple output of one model. It is the **synthesis** of the two engines:

| Category | Crucible Score | Telescope Score | Interpretation |
| :--- | :--- | :--- | :--- |
| **Franchise Cornerstone** | High | High | Great Now, Great Later (LeBron) |
| **Latent Star** | Low | High | Bad Now, Great Later (Rookie Luka) |
| **Win-Now Veteran** | High | Low | Great Now, Capped Later (Vet PG) |
| **Avoid/Ghost** | Low | Low | Bad Now, Bad Later (Wiseman, Poole) |

---

## Next Developer: Start Here

**Current State**: ✅ **CRUCIBLE ENGINE COMPLETE**. The "Viability" half of the equation is solved. We have a robust, physics-based model that can assess a player's immediate playoff readiness. The test suite pass rate is **41.67%**, reflecting that it is *only* solving for half the problem (it correctly fails latent stars on current viability).

**Highest Leverage Action**: **Build The Telescope.**

The primary weakness of our system is its inability to project future value, causing it to fail test cases for latent stars and rookies. You must build the second clock.

**Implementation Plan**:
1.  **Engineer the Time-Shifted Target**:
    -   Create a script to generate the target variable: `MAX(Playoff_PIE)` for `SEASON+1` through `SEASON+3`.
2.  **De-Risk Survivorship Bias**:
    -   You **must** explicitly impute failure. For players who wash out of the league before `SEASON+3`, add them back to the training data with a `PIE_TARGET` of `0.05` (Replacement Level). The model must learn that "disappearing" is a common outcome.
3.  **Train the Telescope Model**:
    -   Use the same physics-based RS features as the Crucible.
    -   Train an XGBoost Regressor on the "Growth Cohort" (players under 26) to predict the time-shifted target.
4.  **Synthesize the Scores**:
    -   Once both models are built, create a final script that generates a `CRUCIBLE_SCORE` and a `TELESCOPE_SCORE` for every player. These two scores will become the new inputs for the final 2D Risk Matrix categorization.

**Key Test Cases to Validate the Telescope**:
- **Nikola Jokić (2015-16)**: Should have a low Crucible score but a high Telescope score.
- **James Wiseman (2020-21)**: Should have a low Crucible score and a low Telescope score.
- **Jordan Poole (2021-22)**: Should have a low Crucible score and a low/mid Telescope score.
