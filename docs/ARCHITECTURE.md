# System Architecture

This document explains how the NBA Playoff Resilience Engine works from the ground up.

## Overview

The system follows a classic ML pipeline: **Data → Features → Model → Prediction → Validation**

```
Raw Data → Feature Engineering → Model Training → Inference → Validation
     ↓             ↓                    ↓            ↓          ↓
 NBA API → 5 Stress Vectors → XGBoost Classifier → Archetypes → Test Suite
```

## Data Pipeline

### 1. Data Collection (`src/data/`)
Collects data from multiple NBA APIs and sources:

- **NBA Stats API**: Player stats, game logs, advanced metrics
- **NBA Shot Charts**: Spatial shooting data, shot quality analysis
- **Play-by-Play Data**: Possession-level game data
- **Defensive Context**: Opponent quality, pace, scheme analysis

**Key Principle:** Ground-truth data only. No proxies for critical signals.

### 2. Feature Engineering (`src/features/`)

Transforms raw data into **5 Stress Vectors** that measure resilience under pressure:

#### Creation Vector
- **What:** Efficiency drop-off when forced to create own shot
- **Key Metric:** `CREATION_TAX` - FG% on 3+ dribble shots vs. catch-and-shoot
- **Why:** Self-creation ability is the strongest predictor of playoff success

#### Leverage Vector
- **What:** How efficiency and usage scale in clutch situations
- **Key Metrics:** `LEVERAGE_TS_DELTA`, `LEVERAGE_USG_DELTA`
- **Why:** Clutch performance reveals true character (Abdication Tax)

#### Pressure Vector
- **What:** Willingness to take tight shots with **clock distinction**
- **Key Distinction:**
  - **Late Clock Pressure (7-4s, 4-0s):** Valuable (bailout ability)
  - **Early Clock Pressure (22-18s, 18-15s):** Negative (bad shot selection)
- **Why:** Late clock = resilience, early clock = poor decision-making

#### Physicality Vector
- **What:** Rim pressure resilience (maintains rim attack volume)
- **Key Metric:** `RIM_PRESSURE_RESILIENCE` (ratio) + `RS_RIM_APPETITE` (absolute)
- **Why:** "The Whistle Disappears in May" - jump shooting variance kills in playoffs

#### Plasticity Vector
- **What:** Spatial and temporal shot distribution adaptability
- **Key Metrics:** Shot chart analysis, zone adaptability
- **Why:** Playoff defenses force spatial adaptation

### 3. Model Training (`src/model/`)

#### Algorithm: XGBoost Classifier (Multi-Class)
- **Why XGBoost:** Handles feature interactions, robust to outliers, interpretable
- **Multi-Class:** Predicts 4 archetypes (King, Bulldozer, Sniper, Victim)

#### Key Innovations

**Usage-Aware Features**
```
archetype = f(stress_vectors, usage)
```
- Model learns how performance changes with opportunity
- Enables "What if?" scenarios (20% → 30% usage projections)

**Universal Projection**
- Features scale together using empirical distributions
- Solves "Static Avatar Fallacy" (features must scale as usage changes)

**Sample Weighting**
- Asymmetric loss: False positives cost more than false negatives
- Penalizes predicting "Victim" as "King" (dangerous high-usage busts)

### 4. Inference Engine (`src/model/`)

#### Core Prediction Function
```python
predict_archetype(player_data, usage_level=None) → ArchetypePrediction
```

**Two Use Cases:**

1. **Current Role Evaluation:** "How will this player perform given their current usage?"
2. **Latent Star Detection:** "What archetype would this player be at star usage levels?"

#### 2D Risk Matrix Output
Returns both dimensions:
- **Performance Score:** What outcomes will they achieve?
- **Dependence Score:** Is their production portable?

### 5. Validation Framework (`tests/validation/`)

#### Test Suite Structure
- **32 Critical Cases:** Historical players with known outcomes
- **Hybrid Evaluation:** 2D for modern cases, 1D compatibility for legacy
- **Pass Rate:** 87.5% (35/40) - Major breakthrough

#### Validation Principles
- **Temporal Splits:** Train on past, test on future (no data leakage)
- **Mechanistic Explanations:** Explain *why* predictions work
- **First Principles:** Ground predictions in basketball physics

## Key Design Principles

### 1. First Principles Thinking
Don't measure *what* happened. Isolate the *stylistic shifts* that explain *why*.

### 2. Resilience = Efficiency × Volume
The "Abdication Tax" is real. Passivity is failure. Volume maintenance is as important as efficiency.

### 3. Self-Creation is King
The strongest predictor of playoff success is generating your own offense. A player who can't create is limited.

### 4. Dominance is Rigid
Some players (Shaq, Giannis) succeed not by adapting, but by imposing their will regardless of context.

### 5. Filter First, Then Rank
Value is relative to the reference class. Always filter the candidate pool before normalizing.

### 6. No Proxies
Use ground-truth data. Flag missing data with confidence scores, don't impute.

### 7. Learn, Don't Patch
Model should learn patterns from features, not rely on hard-coded rules.

## System Components

### Configuration System (`config/`)
- Environment-specific settings (dev/prod)
- API credentials, model parameters
- Feature engineering hyperparameters

### Model Registry (`models/`)
- Versioned model storage
- Production/staging/archive separation
- Metadata tracking (accuracy, features, training date)

### Data Organization (`data/`)
- **Raw:** Never modify (source of truth)
- **Interim:** Intermediate processing results
- **Processed:** Final datasets ready for training
- **External:** Third-party datasets

### Results Organization (`results/`)
- **Experiments:** Model training runs
- **Reports:** Analysis and validation results
- **Predictions:** Model outputs
- **Diagnostics:** Debug information

## Error Handling & Resilience

### Rate Limiting
- NBA API has strict limits - built-in exponential backoff
- Parallel processing with worker pools
- Graceful degradation on API failures

### Data Quality
- Comprehensive validation at each pipeline stage
- Missing data handling with confidence scores
- Outlier detection and filtering

### Model Robustness
- Feature importance monitoring
- Performance drift detection
- Fallback to simpler models if needed

## Performance Characteristics

- **Training Time:** ~5 minutes on modern hardware
- **Prediction Time:** <1 second per player
- **Memory Usage:** ~2GB during training
- **Data Volume:** 5,312 player-seasons (2015-2025)
- **Feature Count:** 15 (RFE-optimized from 65+)

## Scaling Considerations

### Horizontal Scaling
- Data collection: Parallel API calls with worker pools
- Feature engineering: Embarrassingly parallel per player
- Model training: Single node (XGBoost scales vertically)

### Vertical Scaling
- Memory: Feature engineering is memory-intensive
- CPU: API rate limits are the bottleneck
- Storage: CSV-based, easily scales to cloud storage

## Monitoring & Observability

### Key Metrics to Monitor
- Model accuracy on validation set
- Feature importance stability
- Data collection success rates
- API rate limit usage

### Logging Strategy
- Structured logging with context
- Separate logs for data, model, and application events
- Error aggregation and alerting

This architecture enables reliable, explainable predictions while maintaining scientific rigor and operational resilience.
