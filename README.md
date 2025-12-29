# NBA Playoff Resilience Engine

A system for identifying NBA players who will become franchise cornerstones **before** consensus recognition, by measuring their ability to create offense when the defense knows it's coming.

## The Core Question

> **"Does this player need the right situation, or IS he the situation?"**

This distinguishes between:
- **Creators**: Players who can manufacture efficient offense when defenses scheme for them. They ARE the situation.
- **Converters**: Players who can only cash in opportunities created by the system. They NEED the situation.

## Current Status: Phase 2 - Creation Independence Index (CII)

**All 5 CII components implemented with 7/7 critical validation cases passing.**

### The Five Components

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| Self-Created Shot Score | 30% | Can you get a shot without a play? |
| Pressure Appetite Score | 25% | Do you WANT the ball in clutch? |
| Shot Difficulty Embrace | 20% | Do you take hard shots or hide? |
| Defensive Survival Score | 15% | Do you maintain against schemes? |
| Force Multiplication Score | 10% | Do you create through physicality? |

### The Archetypes (Classification Target)

| Archetype | CII Range | Definition | Examples |
|-----------|-----------|------------|----------|
| **Franchise Engine** | 80+ | Can be #1 on a championship team | Harden, Luka, Jokić, Tatum, SGA |
| **Strong Creator** | 70-80 | High creation, optimal as #2 | Haliburton, Jaylen Brown, prime Kyrie |
| **Luxury Amplifier** | 55-70 | Excellent, needs an Engine | Middleton, Bosh |
| **Fragile Star** | 40-55 | Looks like Engine, fatal flaws | Pre-collapse Simmons, KAT |
| **Role Player** | <40 | Solid contributor, not a star | Tyus Jones, Sabonis |

### Key Validation Results

| Player (Season) | CII | Archetype | Status |
|-----------------|-----|-----------|--------|
| James Harden (2018-19) | 87 | Franchise Engine | ✅ |
| Nikola Jokić (2022-23) | 83 | Franchise Engine | ✅ |
| Ben Simmons (2019-20) | 31 | Role Player | ✅ |
| Domantas Sabonis (2022-23) | 24 | Role Player | ✅ |

**Key Insight**: Jokić and Sabonis look similar on paper (elite efficiency, high touch production), but CII correctly separates them by 58 points because Jokić **steps up** under pressure (`leverage_usg_delta = +0.043`) while Sabonis **hides** (`leverage_usg_delta = -0.058`).

## Quick Start

```bash
# Calculate CII for all players
python -c "
from src.nba_data.phase2_creation_independence.index.composite import batch_calculate_cii
import pandas as pd
df = pd.read_csv('results/predictive_dataset_with_friction.csv')
cii_results = batch_calculate_cii(df)
print(cii_results.sort_values('cii', ascending=False).head(20))
"
```

## Project Structure

```
src/nba_data/
├── phase2_creation_independence/  # Active CII implementation
│   ├── SPECIFICATION.md           # Full CII specification
│   ├── index/                     # Component calculators
│   │   ├── composite.py           # Main CII calculator
│   │   ├── self_created.py        # Component 1
│   │   ├── pressure_appetite.py   # Component 2
│   │   ├── difficulty_embrace.py  # Component 3
│   │   ├── defensive_survival.py  # Component 4
│   │   └── force_multiplication.py# Component 5
│   └── ground_truth/              # Expert labels
├── scripts/                       # Data collection & feature engineering
└── phase1_helio_archive/          # Archived Phase 1 (historical reference)
```

## Documentation

| Document | Purpose |
|----------|---------|
| `ACTIVE_CONTEXT.md` | Current project state and priorities |
| `IMPLEMENTATION_GUIDE.md` | Technical implementation details |
| `KEY_INSIGHTS.md` | 80+ hard-won lessons |
| `LUKA_SIMMONS_PARADOX.md` | Theoretical foundation |
| `phase2_creation_independence/SPECIFICATION.md` | CII specification |

## Data Pipeline

The data pipeline collects from the NBA Stats API and generates features:

```bash
# Regenerate core dataset
python src/nba_data/scripts/evaluate_plasticity_potential.py
```

Key outputs:
- `results/predictive_dataset_with_friction.csv` - Core features
- `results/cii_results.csv` - CII scores by player-season

## Next Steps

1. Expand ground truth labels to 60+ player-seasons
2. Train archetype classifier
3. Apply to current season to identify latent stars
