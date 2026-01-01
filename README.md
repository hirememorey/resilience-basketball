# NBA Playoff Resilience Engine

A system for identifying NBA players who will become franchise cornerstones **before** consensus recognition, by measuring their ability to create offense when the defense knows it's coming.

## The Core Question

> **"Does this player need the right situation, or IS he the situation?"**

This distinguishes between:
- **Creators**: Players who can manufacture efficient offense when defenses scheme for them. They ARE the situation.
- **Converters**: Players who can only cash in opportunities created by the system. They NEED the situation.

## Current Status: Refining Phase 2c - Creation Viability

**Refinement In Progress**: We are implementing "Viability-Dampened Volume" to correct the "Mudiay Anomaly" (where inefficient chuckers were rewarded for raw creation volume).
- **Previous Logic**: High Volume = High Score.
- **New Logic**: High Volume is only valuable if it is **Viable** (more efficient than the team's alternative options).

**Phase 2 Complete**: 2D Classification System (CII × TII)
- **All CII/TII components implemented.**
- **Phase 2b refinements (Age & Usage Gates) implemented.**

The system now combines:
1. **CII (Creation Independence Index)** - Current creation ability
2. **TII (Trajectory Independence Index)** - Scaling potential
3. **Career Leverage Pattern** - Consistent stepping up vs hiding
4. **Creation Tools Check** - Real self-creation ability
5. **Age Gates** - Prevents veterans from being labeled "Developing" or "Latent"
6. **Usage Gates** - Protects elite role players from "Fragile Star" misclassification

### The 2D Classification Grid

```
                       TII (Scaling Potential)
                  Low (<50)    Med (50-70)    High (>70)
             ┌─────────────┬─────────────┬─────────────┐
  High (74+) │  Franchise  │  Franchise  │  Franchise  │
             │   Engine    │   Engine    │   Engine    │
CII          ├─────────────┼─────────────┼─────────────┤
(Current)    │   Luxury    │   Strong    │   LATENT    │
  Med (45-74)│  Amplifier  │  Creator    │   ENGINE    │ ← The Alpha
             ├─────────────┼─────────────┼─────────────┤
             │    Role     │ Developing  │ Developing  │
  Low (<45)  │   Player    │  Prospect   │   Star      │
             └─────────────┴─────────────┴─────────────┘
```

### Key Archetypes

| Archetype | Definition | Examples |
|-----------|------------|----------|
| **Franchise Engine** | Can be #1 on a championship team | Harden, Luka, Jokić, SGA |
| **Latent Engine** | Has skills, needs opportunity → **THE ALPHA** | Brunson 2020-21, Harden at OKC |
| **Luxury Amplifier** | Negative leverage + has tools = thrives as #2 | Randle, Jaylen Brown, Klay |
| **Fragile Star** | High usage (>22%) + low CII + no tools = fundamental gaps | Simmons, Sabonis, KAT, Jordan Poole |
| **Role Player** | Solid contributor, not a star | Tyus Jones, 3-and-D players, Derrick White |

### Key Validation Results

| Player (Season) | Classification | Status |
|-----------------|----------------|--------|
| James Harden (2018-19) | Franchise Engine | ✅ |
| Nikola Jokić (2022-23) | Franchise Engine | ✅ |
| Jalen Brunson (2020-21) | **Latent Engine** | ✅ Detected BEFORE breakout |
| Julius Randle (2020-21) | Luxury Amplifier | ✅ Thrives as #2, not #1 |
| Ben Simmons (2019-20) | Fragile Star | ✅ |
| Karl-Anthony Towns (2019-20) | Fragile Star | ✅ |

**Key Breakthroughs**:
1. **Career Leverage Pattern**: Randle's career leverage pattern (-0.023 mean, 8 negative seasons) revealed his 2020-21 was an outlier. True Engines like Harden (+0.053), Brunson (+0.040), and SGA (+0.033) show consistent positive leverage throughout their careers.
2. **Usage Gates (Phase 2b)**: Fragile Star classification now requires high usage (>22%) to protect elite role players like Derrick White from false positives. A role player who hides is just a role player; a STAR who hides is Fragile.
3. **Creation Viability (Phase 2c - In Progress)**: Dampening creation volume for inefficient players (Mudiay Correction) using "Creation Premium" logic (Player TS vs Taxed Teammate TS).

## Quick Start

```bash
# Run 2D classification on all players
python -c "
from src.nba_data.phase2_creation_independence.index.classify_2d import batch_classify_2d
import pandas as pd
df = pd.read_csv('results/predictive_dataset_with_friction.csv')
results = batch_classify_2d(df)
print(results[['player_name', 'season', 'cii', 'tii', 'archetype_2d']].sort_values('cii', ascending=False).head(20))
"

# Diagnose a specific player
python -c "
from src.nba_data.phase2_creation_independence.index.classify_2d import diagnose_2d_classification
import pandas as pd
df = pd.read_csv('results/predictive_dataset_with_friction.csv')
diagnose_2d_classification('Jalen Brunson', '2020-21', df)
"
```

## Project Structure

```
src/nba_data/
├── phase2_creation_independence/  # Active implementation
│   ├── SPECIFICATION.md           # CII specification
│   ├── TII_SPECIFICATION.md       # TII specification
│   ├── index/                     # Component calculators
│   │   ├── composite.py           # CII calculator
│   │   ├── trajectory.py          # TII calculator
│   │   ├── classify_2d.py         # 2D classification engine ← NEW
│   │   ├── self_created.py        # CII Component 1
│   │   ├── pressure_appetite.py   # CII Component 2
│   │   ├── difficulty_embrace.py  # CII Component 3
│   │   ├── defensive_survival.py  # CII Component 4
│   │   └── force_multiplication.py# CII Component 5
│   └── ground_truth/              # Expert labels
│       ├── player_labels.csv      # 1D labels
│       └── player_labels_2d.csv   # 2D labels
├── scripts/                       # Data collection & feature engineering
└── phase1_helio_archive/          # Archived Phase 1 (historical reference)
```

## Key Outputs

| File | Description |
|------|-------------|
| `results/predictive_dataset_with_friction.csv` | Core features (2673 player-seasons) |
| `results/classification_2d_results.csv` | Full 2D classification results |

## Documentation

| Document | Purpose |
|----------|---------|
| `ACTIVE_CONTEXT.md` | Current project state and priorities |
| `IMPLEMENTATION_GUIDE.md` | Technical implementation details |
| `KEY_INSIGHTS.md` | 80+ hard-won lessons |
| `LUKA_SIMMONS_PARADOX.md` | Theoretical foundation |

## Next Steps

1. ✅ **Deployed to 2024-25 season** - Results in `results/classification_2d_2024_25.csv`
2. **Implement Creation Viability** - Fix Mudiay/Curry anomalies by weighting volume by relative efficiency.
3. Build Streamlit dashboard for interactive 2D grid visualization
4. Monitor "Latent Engine" list (Garland, Cunningham, Simons) during 2025-26 season
5. Track "Fragile Stars" (Poole, Kuzma) for playoff validation
