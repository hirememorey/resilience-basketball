# NBA Playoff Resilience Engine (V5 - The "Factory" Model)

This project has evolved from a series of exploratory scripts into a robust, reproducible **"Data Factory"** for simulating NBA player performance under playoff conditions.

Its primary goal is to move beyond simple predictions and create a **"Universal Avatar" Simulation Engine** that projects how a player's efficiency scales with increased usage and defensive pressure.

## Core Architecture: The Factory Pipeline

The system is designed as a linear, one-click pipeline. A new developer can regenerate the entire project's data artifacts and visualizations by running a single command.

```bash
python src/nba_data/scripts/evaluate_plasticity_potential.py && streamlit run src/nba_data/scripts/visualize_risk_matrix.py
```

This command executes the two primary stages of the factory:

### 1. The Engine: `evaluate_plasticity_potential.py`
This script is the heart of the factory. It ingests raw data from the NBA Stats API and performs all necessary feature engineering to produce the core `predictive_dataset.csv`. Key outputs include:
-   `SHOT_QUALITY_GENERATION_DELTA`: A measure of a player's ability to create high-quality shots.
-   `HELIO_POTENTIAL_SCORE`: A non-linear feature capturing a player's potential to be a heliocentric engine.
-   `FRICTION_COEFFICIENTS`: Empirically derived values that model how efficiency degrades with usage.

### 2. The Visualization: `visualize_risk_matrix.py`
This script launches a Streamlit web application that displays the final "2D Risk Matrix," the primary deliverable for analysis. It plots players on two axes:
-   **Resilience (X-Axis)**: Modeled by `HELIO_POTENTIAL_SCORE`.
-   **Scalability (Y-Axis)**: A projection of the player's `TS%` at a standardized 28% usage rate, calculated via the Universal Projection Engine.

## Data Integrity

To combat entropy and ensure reproducibility, the pipeline now enforces a strict data schema using Pydantic models, defined in `src/nba_data/core/models.py`. The `evaluate_plasticity_potential.py` script validates its final output against the `PlayerSeason` model, ensuring that no "broken" data is saved.

## Key Principles & Theory

For a deeper understanding of the "First Principles" that guide this project, please review the following core documents:

-   `LUKA_SIMMONS_PARADOX.md`: The theoretical foundation for why this model exists.
-   `KEY_INSIGHTS.md`: A list of hard-won lessons and insights gained during the exploratory phase.
