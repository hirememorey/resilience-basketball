# NBA Playoff Resilience Engine

A system for identifying NBA players who will become franchise cornerstones **before** consensus recognition, by measuring their ability to create offense when the defense knows it's coming.

## The Core Question

> **"Does this player need the right situation, or IS he the situation?"**

This distinguishes between:
- **Creators**: Players who can manufacture efficient offense when defenses scheme for them. They ARE the situation.
- **Converters**: Players who can only cash in opportunities created by the system. They NEED the situation.

## Current Status: Phase 2d - Multi-Path Creation Framework

**Refinement In Progress**: We are refactoring the **Self-Created Shot Score** (30% of CII) to move beyond ISO-centric measurement.

**The "Polymath" Shift**: Previous versions under-valued "Drive-and-Kick" engines (LeBron) and "Gravity" engines (Curry) because they generated advantage through rim pressure or off-ball movement rather than isolation pull-ups. The new system evaluates **four distinct creation pathways**:

1.  **ISO Creator** (Harden, Luka) - 1v1 separation.
2.  **Drive-and-Kick Engine** (LeBron, Giannis) - Rim pressure and collapse.
3.  **Post Hub** (Jokić, Embiid) - Structural advantage and passing.
4.  **Gravity Engine** (Curry, Klay) - Spacing and distortion.

**Score Calculation**: `Max(Path_A, Path_B, Path_C, Path_D) + Multi-Modal Bonus`

---

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
| **Franchise Engine** | Can be #1 on a championship team | Harden, Luka, Jokić, SGA, LeBron, Curry |
| **Latent Engine** | Has skills, needs opportunity → **THE ALPHA** | Brunson 2020-21, Harden at OKC |
| **Luxury Amplifier** | Negative leverage + has tools = thrives as #2 | Randle, Jaylen Brown, Klay |
| **Fragile Star** | High usage (>22%) + low CII + no tools = fundamental gaps | Simmons, Sabonis, KAT, Jordan Poole |
| **Role Player** | Solid contributor, not a star | Tyus Jones, 3-and-D players, Derrick White |

### Key Validation Results

| Player (Season) | Classification | Status |
|-----------------|----------------|--------|
| James Harden (2018-19) | Franchise Engine | ✅ (ISO Path) |
| Nikola Jokić (2022-23) | Franchise Engine | ✅ (Post Hub Path) |
| LeBron James (2015-16) | Franchise Engine | ✅ (Drive-and-Kick Path) |
| Stephen Curry (2016-17) | Franchise Engine | ✅ (Gravity Path) |
| Jalen Brunson (2020-21) | **Latent Engine** | ✅ Detected BEFORE breakout |
| Ben Simmons (2019-20) | Fragile Star | ✅ Fails all paths |

---

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
│   ├── index/                     # Component calculators
│   │   ├── composite.py           # CII calculator
│   │   ├── classify_2d.py         # 2D classification engine
│   │   ├── self_created.py        # CII Component 1 (Multi-Path)
│   │   ├── path_iso.py            # Path A
│   │   ├── path_drive_kick.py     # Path B
│   │   ├── path_post_hub.py       # Path C
│   │   ├── path_gravity.py        # Path D
│   │   └── ...                    # Components 2-5
│   └── ground_truth/              # Expert labels
├── scripts/                       # Data collection & feature engineering
└── phase1_helio_archive/          # Archived Phase 1 (historical reference)
```

## Documentation

| Document | Purpose |
|----------|---------|
| `ACTIVE_CONTEXT.md` | Current project state and priorities |
| `implementation_plan_multipath.md` | **Active Blueprint for Phase 2d** |
| `KEY_INSIGHTS.md` | 80+ hard-won lessons |
| `LUKA_SIMMONS_PARADOX.md` | Theoretical foundation |
