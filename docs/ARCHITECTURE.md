# System Architecture

This document explains how the NBA Playoff Resilience Engine works from the ground up. The system has evolved from a single-model architecture to a "Two-Clock" system that separates **Current Viability** from **Future Potential**.

## Overview

The system follows a **Two-Clock Architecture**: **Data → Features → Dual Models → Synthesis → Validation**

```
Raw Data → Feature Engineering → Crucible + Telescope → 2D Risk Matrix → Validation
     ↓             ↓                    ↓            ↓          ↓
 NBA API → Physics Features → Viability + Potential → Risk Categories → Test Suite
```

## Core Architectural Shift

### The "Two-Clock" Problem

Our previous single-model approach failed because it tried to optimize for two contradictory goals with one loss function:
- **Current Viability**: "Will this player survive playoff pressure **today**?"
- **Future Potential**: "How much will this player grow over the next 3 seasons?"

### The Solution: Dual-Engine Architecture

We now maintain **two separate models**, each optimized for one clock:

1. **The Crucible (Viability Engine)**: Evaluates current playoff readiness.
2. **The Telescope (Potential Engine)**: Projects future growth trajectory.

## Data Pipeline

### 1. Data Collection (`src/data/`)
Collects data from multiple NBA APIs and sources:

- **NBA Stats API**: Player stats, game logs, advanced metrics
- **NBA Shot Charts**: Spatial shooting data, shot quality analysis
- **Play-by-Play Data**: Possession-level game data
- **Defensive Context**: Opponent quality, pace, scheme analysis

**Key Principle:** Ground-truth data only. No proxies for critical signals.

### 2. Feature Engineering (`src/features/`)

Transforms raw data into **Physics Features** that capture basketball first principles:

#### Core Physics Features
- **`CREATION_TAX`**: Efficiency penalty when forced to create own shot
- **`DEPENDENCE_SCORE`**: How much help a player needs (Two Doors: Physicality + Skill)
- **`SHOT_QUALITY_GENERATION_DELTA`**: Ability to generate easy shots for the offense
- **`LEVERAGE_TS_DELTA`**: Performance under clutch pressure
- **`USG_PCT`**: Usage level (sets the floor/ceiling for impact)

**Key Innovation:** These features are **causal**, not just correlational. They reflect the actual physics of basketball success.

### 3. Model Training (`src/model/`)

#### The Crucible Engine
**Algorithm:** XGBoost Regressor
**Target Variable:** `PIE_TARGET` (Player Impact Estimate - objective playoff performance)
**Purpose:** Predicts immediate playoff viability
**Training Data:** `crucible_dataset.csv` (RS physics features mapped to actual playoff outcomes)

#### The Telescope Engine (Planned)
**Algorithm:** XGBoost Regressor
**Target Variable:** `MAX(PIE_TARGET)` over next 3 seasons
**Purpose:** Projects future potential
**Training Data:** Time-shifted dataset with explicit failure imputation

### 4. Inference Engine (`src/model/`)

#### Synthesis Function
```python
def synthesize_risk_categories(crucible_score, telescope_score):
    """
    Combines Viability and Potential into final risk categories.
    """
    if crucible_score > 0.14 and telescope_score > 0.14:
        return "Franchise Cornerstone"
    elif crucible_score > 0.14 and telescope_score <= 0.14:
        return "Win-Now Veteran"
    elif crucible_score <= 0.14 and telescope_score > 0.14:
        return "Latent Star"
    else:
        return "Avoid/Ghost"
```

### 5. Validation Framework (`tests/validation/`)

#### Test Suite Structure
- **48 Critical Cases:** Historical players with known outcomes
- **Dual Evaluation:** Tests both Crucible and Telescope components
- **Pass Rate:** 41.67% (Crucible Engine) - Foundation is solid, Telescope will address remaining gaps

## Key Design Principles

### 1. First Principles Thinking
Don't measure *what* happened. Isolate the *stylistic shifts* that explain *why*.

### 2. Separate Viability from Potential
**Current Viability** and **Future Scalability** are chemically different properties. They require separate models.

### 3. Input Sanitation Over Output Gates
Filter "fair weather" noise at the input stage (Crucible Dataset) rather than building elaborate post-hoc gates.

### 4. Objective Targets Over Subjective Labels
Train on `PIE_TARGET` (league-standard impact measure) rather than subjective archetypes like "King" or "Bulldozer".

### 5. Explicit Failure Imputation
For the Telescope to learn properly, it must see "0" outcomes for players who wash out of the league.

## System Components

### Configuration System (`config/`)
- Environment-specific settings (dev/prod)
- API credentials, model parameters
- Feature engineering hyperparameters

### Model Registry (`models/`)
- Versioned model storage: `crucible_impact_model.pkl`
- Production/staging/archive separation
- Metadata tracking (R2 score, features, training date)

### Data Organization (`data/`)
- **Raw:** Never modify (source of truth)
- **Interim:** Intermediate processing results
- **Processed:** Final datasets: `crucible_dataset.csv`
- **External:** Third-party datasets

### Results Organization (`results/`)
- **Experiments:** Model training runs
- **Reports:** `physics_model_validation_report.md`, `crucible_model_test_report.csv`
- **Predictions:** `physics_adjusted_impact.csv`
- **Diagnostics:** Debug information

## Performance Characteristics

- **Crucible Training Time:** ~5 seconds
- **Crucible Prediction Time:** <1 second per player
- **Data Volume:** 619 player-seasons (Crucible cohort: >200 playoff minutes)
- **Feature Count:** 10 physics-based features
- **R2 Score:** **0.4715** (Strong predictive power for cross-context sports prediction)

## Next Development Phase

The **Telescope Engine** is the immediate priority. It will:
1. Engineer a time-shifted target variable (`MAX(PIE_TARGET)` over `SEASON+1` to `SEASON+3`)
2. Explicitly impute failure outcomes for washed-out players
3. Train on the "Growth Cohort" (Age < 26) to focus on developmental potential
4. Synthesize with the Crucible to produce final 2D Risk Matrix categories

This dual-engine approach addresses the core limitation of our previous systems: the impossibility of optimizing one model for two opposing goals.