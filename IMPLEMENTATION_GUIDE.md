# NBA Playoff Resilience Engine - Technical Implementation Guide

**Version**: 1.0  
**Date**: December 27, 2025  
**Audience**: New developers joining the project

---

## Table of Contents

1. [Theoretical Foundation](#1-theoretical-foundation)
2. [Architecture Overview](#2-architecture-overview)
3. [Data Pipeline](#3-data-pipeline)
4. [CII Component Implementation](#4-cii-component-implementation)
5. [Classification System](#5-classification-system)
6. [Testing & Validation](#6-testing--validation)
7. [Code Patterns & Conventions](#7-code-patterns--conventions)
8. [Step-by-Step Implementation Tasks](#8-step-by-step-implementation-tasks)
9. [Troubleshooting & Anti-Patterns](#9-troubleshooting--anti-patterns)

---

## 1. Theoretical Foundation

### 1.1 The Core Question

The entire system is designed to answer one question:

> **"Does this player need the right situation, or IS he the situation?"**

This distinguishes between:
- **Creators**: Players who can manufacture efficient offense when defenses know it's coming
- **Converters**: Players who can only cash in opportunities created by the system

### 1.2 The Ground Truth Trap (Why Phase 1 Failed)

Phase 1 tried to predict `FUTURE_PEAK_HELIO` (future playoff PIE). This failed because:

```
Ben Simmons had GOOD playoff PIE (pre-2021) → Model learned he was "good"
Reality: His PROCESS was fragile (zero self-created jumpers, hiding under pressure)
```

**The Insight**: Outcomes are contaminated by context (teammates, schemes). We must model the **process**, not the **outcome**.

### 1.3 The Five Immutable Principles

These principles govern all implementation decisions:

| Principle | Description | Example |
|-----------|-------------|---------|
| **Creators vs. Converters** | The central distinction | Harden IS the situation; Simmons NEEDS the situation |
| **Filter First, Then Rank** | Never rank against entire league | Evaluate "Is this player an Engine?" not "How does he compare to everyone?" |
| **Model the Process** | Measure ability, not results | Measure "Can he create?" not "Did he score?" |
| **No Proxies** | Each metric measures one phenomenon | Don't use ISO EFG as proxy for Leverage TS Delta |
| **Learn, Don't Patch** | Features should capture phenomena | Don't patch targets with manual penalties |

### 1.4 The Archetypes

The classification target is a 5-class archetype system:

| Archetype | CII Range | Definition | Examples |
|-----------|-----------|------------|----------|
| **Franchise Engine** | 80+ | Can be #1 on a championship team | Harden, Luka, Jokić, Tatum, SGA |
| **Strong Creator** | 70-80 | High creation, optimal as #2 | Haliburton, Jaylen Brown, prime Kyrie |
| **Luxury Amplifier** | 55-70 | Excellent, needs an Engine | Sabonis, Middleton, Bosh |
| **Fragile Star** | 40-55 | Looks like Engine, fatal flaws | Simmons, KAT, Randle |
| **Role Player** | <40 | Solid contributor, not a star | Tyus Jones, 3-and-D players |

---

## 2. Architecture Overview

### 2.1 Directory Structure

```
resilience_basketball/
├── src/nba_data/
│   ├── api/                          # NBA Stats API clients
│   │   ├── nba_stats_client.py       # Core HTTP client with caching
│   │   ├── synergy_playtypes_client.py # Playtype data
│   │   └── shot_dashboard_client.py  # Shot quality data
│   │
│   ├── core/
│   │   └── models.py                 # Pydantic schemas (Single Source of Truth)
│   │
│   ├── utils/
│   │   ├── normalization.py          # Z-score and 0-100 scaling
│   │   └── projection_utils.py       # Usage projection utilities
│   │
│   ├── scripts/                      # Data collection & feature engineering
│   │   ├── evaluate_plasticity_potential.py  # Main feature pipeline
│   │   ├── collect_*.py              # Data collection scripts
│   │   └── calculate_*.py            # Feature calculation scripts
│   │
│   ├── phase1_helio_archive/         # Archived Phase 1 (DO NOT MODIFY)
│   │
│   └── phase2_creation_independence/ # ACTIVE DEVELOPMENT
│       ├── SPECIFICATION.md          # CII spec document
│       ├── index/
│       │   ├── __init__.py
│       │   ├── composite.py          # Main CII calculator
│       │   ├── self_created.py       # Component 1 (TO BUILD)
│       │   ├── pressure_appetite.py  # Component 2 (TO BUILD)
│       │   ├── difficulty_embrace.py # Component 3 (TO BUILD)
│       │   ├── defensive_survival.py # Component 4 (TO BUILD)
│       │   └── force_multiplication.py # Component 5 (TO BUILD)
│       ├── classification/
│       │   ├── __init__.py
│       │   ├── train_classifier.py   # Archetype classifier (TO BUILD)
│       │   └── validate.py           # Validation harness (TO BUILD)
│       └── ground_truth/
│           ├── __init__.py
│           └── player_labels.csv     # Expert-curated labels
│
├── data/                             # Raw data & cache
├── results/                          # Outputs & analysis
├── models/                           # Serialized models (.pkl)
└── logs/                             # Execution logs
```

### 2.2 Data Flow Diagram

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│   NBA Stats     │────▶│  Feature         │────▶│  CII Component     │
│   API           │     │  Engineering     │     │  Calculators       │
└─────────────────┘     └──────────────────┘     └────────────────────┘
                                                          │
                        ┌──────────────────┐              │
                        │  Ground Truth    │◀─────────────┘
                        │  Labels          │
                        └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐     ┌────────────────────┐
                        │  Archetype       │────▶│  Latent Star       │
                        │  Classifier      │     │  Detection         │
                        └──────────────────┘     └────────────────────┘
```

### 2.3 Key Files to Understand

| File | Purpose | When to Read |
|------|---------|--------------|
| `ACTIVE_CONTEXT.md` | Current project state | **ALWAYS READ FIRST** |
| `SPECIFICATION.md` | CII component formulas | When implementing components |
| `KEY_INSIGHTS.md` | 80+ learnings from Phase 1 | When debugging failures |
| `LUKA_SIMMONS_PARADOX.md` | Theoretical foundation | Understanding "why" |
| `core/models.py` | Pydantic schemas | Understanding data contracts |
| `composite.py` | Main CII calculator | Entry point for CII |

---

## 3. Data Pipeline

### 3.1 NBA Stats API Client

The `NBAStatsClient` handles all communication with the NBA Stats API:

```python
from src.nba_data.api.nba_stats_client import create_nba_stats_client

client = create_nba_stats_client()

# Fetch player stats
base_stats = client.get_league_player_base_stats(season="2023-24")
advanced_stats = client.get_league_player_advanced_stats(season="2023-24")

# Fetch shooting stats by dribble range (for Self-Created Shot Score)
zero_dribble = client.get_league_player_shooting_stats(
    season="2023-24",
    dribble_range="0 Dribbles"  # Catch-and-shoot
)
iso_dribble = client.get_league_player_shooting_stats(
    season="2023-24",
    dribble_range="3-6 Dribbles"  # Self-created
)

# Fetch clutch stats (for Pressure Appetite Score)
clutch_stats = client.get_league_player_clutch_stats(
    season="2023-24",
    measure_type="Advanced"
)

# Fetch tracking data (for Force Multiplication Score)
tracking = client.get_league_player_tracking_stats(
    season="2023-24",
    pt_measure_type="Possessions"
)
```

**Key Features**:
- **Caching**: Responses are cached to `data/cache/` for 24 hours
- **Rate Limiting**: Adaptive rate limiting to avoid 429 errors
- **Retry Logic**: Automatic retries with exponential backoff

### 3.2 Parsing API Responses

All NBA Stats API responses follow this structure:

```python
{
    "resultSets": [
        {
            "name": "LeagueDashPlayerStats",
            "headers": ["PLAYER_ID", "PLAYER_NAME", "USG_PCT", ...],
            "rowSet": [
                [201566, "LeBron James", 0.318, ...],
                [203507, "Giannis Antetokounmpo", 0.352, ...],
                ...
            ]
        }
    ]
}
```

Standard parsing pattern:

```python
def parse_api_response(response: Dict) -> pd.DataFrame:
    """Convert NBA Stats API response to DataFrame."""
    result_set = response['resultSets'][0]
    headers = result_set['headers']
    rows = result_set['rowSet']
    return pd.DataFrame(rows, columns=headers)
```

### 3.3 Feature Dataset Schema

The main feature dataset (`results/predictive_dataset_with_friction.csv`) contains:

| Column | Description | Source |
|--------|-------------|--------|
| `PLAYER_ID` | NBA Stats player ID | All endpoints |
| `PLAYER_NAME` | Player name | All endpoints |
| `SEASON` | Season string (e.g., "2023-24") | All endpoints |
| `USG_PCT` | Usage percentage (0.0-1.0) | Advanced stats |
| `TS_PCT` | True shooting percentage | Advanced stats |
| `time_of_poss` | Time of possession (seconds/touch) | Tracking |
| `creation_volume_ratio` | Self-created FGA / Total tracked FGA | Shooting stats |
| `LEVERAGE_USG_DELTA` | Clutch usage - Base usage | Clutch stats |
| `LEVERAGE_TS_DELTA` | Clutch TS% - Base TS% | Clutch stats |
| `CLUTCH_USG_ABSOLUTE` | Actual clutch usage | Calculated |
| `subsidy_index` | System dependence (0=Owner, 1=Subsidized) | Calculated |
| `FRAGILITY_SCORE` | Stylistic fragility (0=Robust, 1=Fragile) | Calculated |

---

## 4. CII Component Implementation

The Creation Independence Index is a weighted sum of five components:

```
CII = 0.30 × Self_Created_Shot_Score
    + 0.25 × Pressure_Appetite_Score
    + 0.20 × Shot_Difficulty_Score
    + 0.15 × Defensive_Survival_Score
    + 0.10 × Force_Score
```

Each component should be normalized to 0-100 scale.

### 4.1 Component 1: Self-Created Shot Score (30%)

**Question**: Can you generate a quality shot without a play being run?

**Implementation File**: `src/nba_data/phase2_creation_independence/index/self_created.py`

**Data Sources**:
- `leaguedashplayerptshot` with `DribbleRange` filters
- `synergyplaytypes` for ISO and PnR Handler data

**Sub-Metrics**:

| Metric | Weight | Calculation |
|--------|--------|-------------|
| Unassisted FG% | 25% | % of FGM that are unassisted |
| ISO + Pull-up Volume | 30% | (ISO_FGA + PullUp_FGA) / 100 possessions |
| Self-Created Efficiency | 30% | EFG% on 3-6 and 7+ dribble shots |
| Creation Tools | 15% | Presence of stepback, fadeaway in shot diet |

**Implementation Skeleton**:

```python
# src/nba_data/phase2_creation_independence/index/self_created.py

import pandas as pd
import numpy as np
from typing import Dict

def calculate_self_created_score(player_data: pd.Series) -> float:
    """
    Calculate Self-Created Shot Score (0-100).
    
    This measures the ability to generate quality shots without plays being run.
    
    Sub-metrics:
    1. Unassisted FG% (25%)
    2. ISO + Pull-up Volume (30%)
    3. Self-Created Efficiency (30%)
    4. Creation Tools Availability (15%)
    """
    
    # Sub-metric 1: Unassisted FG%
    # Higher unassisted rate = more self-created scoring
    unassisted_rate = player_data.get('UNASSISTED_FG_PCT', 0.5)
    unassisted_score = min(unassisted_rate / 0.65 * 100, 100)  # 65%+ = elite
    
    # Sub-metric 2: ISO + Pull-up Volume (per 75 possessions)
    iso_poss = player_data.get('ISO_POSS_RS', 0)
    pullup_fga = player_data.get('FGA_3_DRIBBLE', 0) + player_data.get('FGA_7_DRIBBLE', 0)
    total_creation_volume = iso_poss + pullup_fga
    volume_score = min(total_creation_volume / 8.0 * 100, 100)  # 8+ = elite
    
    # Sub-metric 3: Self-Created Efficiency
    efg_self_created = player_data.get('EFG_ISO_WEIGHTED', 0.45)
    efficiency_score = min((efg_self_created - 0.40) / 0.15 * 100, 100)  # 40% floor, 55%+ = elite
    efficiency_score = max(efficiency_score, 0)  # Floor at 0
    
    # Sub-metric 4: Creation Tools (stepback availability)
    # Proxy: Use 7+ dribble volume as indicator of deep creation ability
    deep_creation_ratio = player_data.get('FGA_7_DRIBBLE', 0) / max(player_data.get('FGA_ISO_TOTAL', 1), 1)
    tools_score = min(deep_creation_ratio * 100 * 2, 100)  # 50%+ of ISO being 7+ = elite
    
    # Weighted combination
    final_score = (
        0.25 * unassisted_score +
        0.30 * volume_score +
        0.30 * efficiency_score +
        0.15 * tools_score
    )
    
    return round(final_score, 2)


def get_required_features() -> list:
    """Return list of features required for this component."""
    return [
        'UNASSISTED_FG_PCT',  # Needs collection
        'ISO_POSS_RS',
        'FGA_3_DRIBBLE',
        'FGA_7_DRIBBLE', 
        'FGA_ISO_TOTAL',
        'EFG_ISO_WEIGHTED'
    ]


# Validation cases (from SPECIFICATION.md)
VALIDATION_CASES = {
    'Ben Simmons': {'expected_score': 5, 'tolerance': 10},   # Near zero self-created jumpers
    'James Harden': {'expected_score': 95, 'tolerance': 10}, # Elite stepback available
    'Luka Dončić': {'expected_score': 95, 'tolerance': 10},  # Maximum creation
}
```

### 4.2 Component 2: Pressure Appetite Score (25%)

**Question**: When the game matters, do you WANT the ball?

**Implementation File**: `src/nba_data/phase2_creation_independence/index/pressure_appetite.py`

**Data Sources**:
- `leaguedashplayerclutch` endpoint
- Existing features: `CLUTCH_USG_ABSOLUTE`, `RELATIVE_USAGE_DROP`

**Sub-Metrics**:

| Metric | Weight | Calculation |
|--------|--------|-------------|
| Clutch Usage Absolute | 50% | Actual usage in clutch (not delta) |
| Relative Usage Change | 30% | (Clutch USG - Base USG) / Base USG |
| 4th Quarter vs 1st-3rd | 20% | Usage pattern throughout game |

**Implementation Skeleton**:

```python
# src/nba_data/phase2_creation_independence/index/pressure_appetite.py

import pandas as pd
import numpy as np

def calculate_pressure_appetite_score(player_data: pd.Series) -> float:
    """
    Calculate Pressure Appetite Score (0-100).
    
    This measures willingness to take responsibility in high-leverage situations.
    
    Key Insight (from KEY_INSIGHTS.md #79):
    - Deltas lose baseline information
    - A player going 40%→35% is different than 15%→10%
    - Use ABSOLUTE clutch usage, not just delta
    """
    
    # Sub-metric 1: Clutch Usage Absolute (50%)
    # This directly answers: "Does this player want the ball in crunch time?"
    clutch_usg = player_data.get('CLUTCH_USG_ABSOLUTE', 0.15)
    
    # Scale: 15% = role player, 35%+ = go-to option
    clutch_score = min((clutch_usg - 0.10) / 0.30 * 100, 100)
    clutch_score = max(clutch_score, 0)
    
    # Sub-metric 2: Relative Usage Change (30%)
    # Positive = stepping UP under pressure (good)
    # Negative = hiding under pressure (bad - the Simmons pattern)
    relative_drop = player_data.get('RELATIVE_USAGE_DROP', 0)
    
    # Map: -30% (hiding) = 0, 0% (stable) = 50, +20% (stepping up) = 100
    appetite_score = 50 + (relative_drop * 200)  # -0.25 → 0, 0 → 50, +0.25 → 100
    appetite_score = np.clip(appetite_score, 0, 100)
    
    # Sub-metric 3: Playoff Usage Bump (20%)
    # Players who embrace playoff pressure have higher usage in playoffs
    playoff_usg = player_data.get('PLAYOFF_USG_PCT', player_data.get('USG_PCT', 0.20))
    rs_usg = player_data.get('USG_PCT', 0.20)
    
    if rs_usg > 0.05:
        playoff_bump = (playoff_usg - rs_usg) / rs_usg
    else:
        playoff_bump = 0
        
    playoff_score = 50 + (playoff_bump * 150)  # -10% = 35, 0 = 50, +10% = 65
    playoff_score = np.clip(playoff_score, 0, 100)
    
    # Weighted combination
    final_score = (
        0.50 * clutch_score +
        0.30 * appetite_score +
        0.20 * playoff_score
    )
    
    return round(final_score, 2)


VALIDATION_CASES = {
    'Ben Simmons': {'expected_score': 20, 'tolerance': 15},  # Usage DROPS under pressure
    'Luka Dončić': {'expected_score': 95, 'tolerance': 10},  # Usage INCREASES under pressure
    'James Harden': {'expected_score': 85, 'tolerance': 10}, # Historically clutch
}
```

### 4.3 Component 3: Shot Difficulty Embrace Score (20%)

**Question**: Are you willing to take HARD shots, or only easy ones?

**Implementation File**: `src/nba_data/phase2_creation_independence/index/difficulty_embrace.py`

**Data Sources**:
- `leaguedashplayerptshot` with `CloseDefDistRange` filters
- Shot chart data for mid-range volume

**Sub-Metrics**:

| Metric | Weight | Calculation |
|--------|--------|-------------|
| Contested Shot Rate | 35% | % of shots with defender < 4 feet |
| Mid-Range Volume | 25% | Mid-range FGA per 75 possessions |
| Pull-up 3PT Rate | 25% | Pull-up 3s / Total 3s |
| Average Shot Difficulty | 15% | Composite from defender distance |

**Implementation Skeleton**:

```python
# src/nba_data/phase2_creation_independence/index/difficulty_embrace.py

import pandas as pd
import numpy as np

def calculate_difficulty_embrace_score(player_data: pd.Series) -> float:
    """
    Calculate Shot Difficulty Embrace Score (0-100).
    
    This measures willingness to take HARD shots, not just efficient ones.
    
    Key Insight:
    Ben Simmons only takes layups/dunks - NEVER embraces difficulty.
    Jayson Tatum takes tough fadeaways routinely.
    """
    
    # Sub-metric 1: Contested Shot Rate (35%)
    # Shots with defender 0-4 feet / Total shots
    contested_rate = player_data.get('CONTESTED_SHOT_RATE', 0.50)
    contested_score = min(contested_rate / 0.70 * 100, 100)  # 70%+ contested = elite
    
    # Sub-metric 2: Mid-Range Volume (25%)
    # Mid-range is "harder" than corner 3s or layups
    midrange_fga = player_data.get('MIDRANGE_FGA_PER_GAME', 2.0)
    midrange_score = min(midrange_fga / 5.0 * 100, 100)  # 5+ per game = elite
    
    # Sub-metric 3: Pull-up 3PT Rate (25%)
    # Pull-up 3s are harder than catch-and-shoot
    pullup_3_rate = player_data.get('PULLUP_3PT_RATE', 0.30)
    pullup_score = min(pullup_3_rate / 0.60 * 100, 100)  # 60%+ of 3s being pull-up = elite
    
    # Sub-metric 4: Time of Possession Proxy (15%)
    # Longer possessions → harder shots (more dribbles, defense set)
    time_of_poss = player_data.get('time_of_poss', 3.0)
    time_score = min(time_of_poss / 6.0 * 100, 100)  # 6+ seconds = elite
    
    # Weighted combination
    final_score = (
        0.35 * contested_score +
        0.25 * midrange_score +
        0.25 * pullup_score +
        0.15 * time_score
    )
    
    return round(final_score, 2)


VALIDATION_CASES = {
    'Ben Simmons': {'expected_score': 10, 'tolerance': 10},  # Only layups/dunks
    'Jayson Tatum': {'expected_score': 85, 'tolerance': 10}, # Takes tough fadeaways
    'Khris Middleton': {'expected_score': 80, 'tolerance': 10}, # Elite mid-range
}
```

### 4.4 Component 4: Defensive Survival Score (15%)

**Question**: When defenses scheme for you, do you survive?

**Implementation File**: `src/nba_data/phase2_creation_independence/index/defensive_survival.py`

**Data Sources**:
- Game logs with opponent defensive rating
- Existing features: `QOC_TS_DELTA`, `ELITE_WEAK_TS_DELTA`

**Sub-Metrics**:

| Metric | Weight | Calculation |
|--------|--------|-------------|
| Efficiency vs Top 10 Defenses | 40% | TS% vs elite defenses / TS% vs weak |
| Playoff vs RS Efficiency | 30% | Playoff TS% / RS TS% |
| Elimination Game Performance | 20% | Performance in must-win games |
| Schematic Resilience | 10% | Maintains production across contexts |

**Implementation Skeleton**:

```python
# src/nba_data/phase2_creation_independence/index/defensive_survival.py

import pandas as pd
import numpy as np

def calculate_defensive_survival_score(player_data: pd.Series) -> float:
    """
    Calculate Defensive Attention Survival Score (0-100).
    
    This measures ability to maintain production when defenses scheme.
    
    Key Insight:
    Ben Simmons completely collapses when schemed (Hawks 2021).
    James Harden actually got BETTER - found counters.
    """
    
    # Sub-metric 1: Performance vs Elite Defenses (40%)
    # How much efficiency drops against top defenses
    ts_vs_top = player_data.get('TS_PCT_vs_top10', 0.55)
    ts_vs_bottom = player_data.get('TS_PCT_vs_bottom10', 0.60)
    
    if ts_vs_bottom > 0:
        qoc_ratio = ts_vs_top / ts_vs_bottom
    else:
        qoc_ratio = 1.0
    
    # 1.0 = no drop, 0.85 = 15% drop (bad), 1.10 = actually better (elite)
    qoc_score = (qoc_ratio - 0.75) / 0.35 * 100  # 0.75 = 0, 1.10 = 100
    qoc_score = np.clip(qoc_score, 0, 100)
    
    # Sub-metric 2: Playoff Translation (30%)
    # How well RS performance translates to playoffs
    playoff_ts = player_data.get('PLAYOFF_TS_PCT', player_data.get('TS_PCT', 0.55))
    rs_ts = player_data.get('TS_PCT', 0.55)
    
    if rs_ts > 0:
        playoff_ratio = playoff_ts / rs_ts
    else:
        playoff_ratio = 1.0
        
    playoff_score = (playoff_ratio - 0.80) / 0.30 * 100
    playoff_score = np.clip(playoff_score, 0, 100)
    
    # Sub-metric 3: Inverse of Fragility Score (30%)
    # Already calculated fragility captures abdication + choke patterns
    fragility = player_data.get('FRAGILITY_SCORE', 0.5)
    fragility_inverse_score = (1.0 - fragility) * 100
    
    # Weighted combination
    final_score = (
        0.40 * qoc_score +
        0.30 * playoff_score +
        0.30 * fragility_inverse_score
    )
    
    return round(final_score, 2)


VALIDATION_CASES = {
    'Ben Simmons': {'expected_score': 25, 'tolerance': 15},  # Completely collapses
    'James Harden': {'expected_score': 85, 'tolerance': 10}, # Found counters
    'Nikola Jokić': {'expected_score': 90, 'tolerance': 10}, # Elite playoff performer
}
```

### 4.5 Component 5: Force Multiplication Score (10%)

**Question**: Do you create things that aren't in the box score?

**Implementation File**: `src/nba_data/phase2_creation_independence/index/force_multiplication.py`

**Data Sources**:
- Free throw rate from advanced stats
- Touch/post data from tracking
- Existing features: `physicality_score`, `weighted_touch_production`

**Sub-Metrics**:

| Metric | Weight | Calculation |
|--------|--------|-------------|
| Free Throw Rate | 40% | FTA / FGA (getting to the line) |
| Rim Pressure | 30% | FGA at rim with contact |
| Gravity/Doubles | 20% | (Harder to measure - proxy via assists) |
| And-1 Frequency | 10% | Three-point plays per game |

**Implementation Skeleton**:

```python
# src/nba_data/phase2_creation_independence/index/force_multiplication.py

import pandas as pd
import numpy as np

def calculate_force_multiplication_score(player_data: pd.Series) -> float:
    """
    Calculate Force Multiplication Score (0-100).
    
    This measures ability to create things beyond the box score via physicality.
    
    Key Insight:
    Giannis = Maximum force. His whole game is force multiplication.
    Ben Simmons = HAD the physical tools, DIDN'T use them.
    """
    
    # Sub-metric 1: Free Throw Rate (40%)
    # Getting to the line = creating fouls = force
    ftr = player_data.get('RS_FTr', 0.30)
    ftr_score = min(ftr / 0.50 * 100, 100)  # 50%+ FTr = elite (Giannis/Embiid level)
    
    # Sub-metric 2: Rim Pressure (30%)
    # Shots at rim with contact
    rim_appetite = player_data.get('RS_RIM_APPETITE', 0.30)
    rim_score = min(rim_appetite / 0.50 * 100, 100)
    
    # Sub-metric 3: Post/Elbow Production (20%)
    # Force via post-up and elbow touches
    touch_production = player_data.get('weighted_touch_production', 3.0)
    touch_score = min(touch_production / 8.0 * 100, 100)  # 8+ pts from touches = elite
    
    # Sub-metric 4: Physicality Score (10%)
    # Already calculated composite
    physicality = player_data.get('physicality_score', 0.5)
    physicality_score = physicality * 100
    
    # Weighted combination
    final_score = (
        0.40 * ftr_score +
        0.30 * rim_score +
        0.20 * touch_score +
        0.10 * physicality_score
    )
    
    return round(final_score, 2)


VALIDATION_CASES = {
    'Giannis Antetokounmpo': {'expected_score': 100, 'tolerance': 5},  # Maximum force
    'Ben Simmons': {'expected_score': 35, 'tolerance': 15},            # Had tools, didn't use
    'Stephen Curry': {'expected_score': 50, 'tolerance': 15},          # Gravity, not force
}
```

---

## 5. Classification System

### 5.1 Ground Truth Labels

The ground truth is stored in `phase2_creation_independence/ground_truth/player_labels.csv`:

```csv
player_name,season,archetype,confidence,notes
James Harden,2011-12,Engine,High,"OKC 6th man year. Elite ISO efficiency..."
Ben Simmons,2018-19,Fragile Star,High,"Age 22. All-Star. Usage drops in clutch..."
```

**Label Distribution Guidelines**:
- ~10-15 Franchise Engines
- ~10-15 Strong Creators
- ~10-15 Luxury Amplifiers
- ~10-15 Fragile Stars
- ~5-10 Role Players

### 5.2 Training the Classifier

**Implementation File**: `src/nba_data/phase2_creation_independence/classification/train_classifier.py`

**Approach**:

```python
# src/nba_data/phase2_creation_independence/classification/train_classifier.py

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from pathlib import Path

def load_ground_truth() -> pd.DataFrame:
    """Load expert-curated ground truth labels."""
    path = Path(__file__).parent.parent / 'ground_truth' / 'player_labels.csv'
    df = pd.read_csv(path, comment='#')
    return df

def load_feature_dataset() -> pd.DataFrame:
    """Load the main feature dataset."""
    path = Path(__file__).parents[4] / 'results' / 'predictive_dataset_with_friction.csv'
    return pd.read_csv(path)

def prepare_training_data():
    """Merge ground truth with features."""
    gt = load_ground_truth()
    features = load_feature_dataset()
    
    # Normalize column names
    gt['player_name'] = gt['player_name'].str.lower().str.strip()
    features['player_name'] = features['player_name'].str.lower().str.strip()
    
    # Merge on player_name and season
    merged = pd.merge(
        gt,
        features,
        left_on=['player_name', 'season'],
        right_on=['player_name', 'season'],
        how='inner'
    )
    
    print(f"Matched {len(merged)} / {len(gt)} ground truth labels to features")
    return merged

def train_archetype_classifier():
    """Train and validate archetype classifier."""
    
    data = prepare_training_data()
    
    # Feature columns (CII components + supporting metrics)
    feature_cols = [
        'cii_self_created',
        'cii_pressure_appetite', 
        'cii_difficulty_embrace',
        'cii_defensive_survival',
        'cii_force_multiplication',
        # Supporting features (let model learn weights)
        'USG_PCT',
        'TS_PCT',
        'CLUTCH_USG_ABSOLUTE',
        'RELATIVE_USAGE_DROP',
        'subsidy_index',
        'FRAGILITY_SCORE'
    ]
    
    # Filter to features that exist
    available_features = [c for c in feature_cols if c in data.columns]
    print(f"Using {len(available_features)} features: {available_features}")
    
    X = data[available_features].fillna(0)
    y = data['archetype']
    
    # Encode target
    archetype_order = ['Role Player', 'Fragile Star', 'Luxury Amplifier', 'Strong Creator', 'Franchise Engine']
    y_encoded = pd.Categorical(y, categories=archetype_order, ordered=True).codes
    
    # Train with cross-validation
    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=4,
        random_state=42
    )
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y_encoded, cv=cv, scoring='accuracy')
    
    print(f"Cross-validation accuracy: {scores.mean():.3f} (+/- {scores.std()*2:.3f})")
    
    # Train final model on all data
    model.fit(X, y_encoded)
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': available_features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(importance.to_string())
    
    # Save model
    model_path = Path(__file__).parents[4] / 'models' / 'archetype_classifier.pkl'
    model_path.parent.mkdir(exist_ok=True)
    joblib.dump({
        'model': model,
        'features': available_features,
        'archetype_order': archetype_order
    }, model_path)
    
    print(f"\nModel saved to {model_path}")
    
    return model, importance


if __name__ == '__main__':
    train_archetype_classifier()
```

### 5.3 Validation Harness

The validation must pass specific test cases:

```python
# src/nba_data/phase2_creation_independence/classification/validate.py

CRITICAL_CASES = [
    # Simmons must be Fragile Star in ALL seasons
    {'player': 'Ben Simmons', 'season': '2017-18', 'expected': 'Fragile Star'},
    {'player': 'Ben Simmons', 'season': '2018-19', 'expected': 'Fragile Star'},
    {'player': 'Ben Simmons', 'season': '2019-20', 'expected': 'Fragile Star'},
    {'player': 'Ben Simmons', 'season': '2020-21', 'expected': 'Fragile Star'},
    
    # Harden at OKC must be Engine despite 6th man role
    {'player': 'James Harden', 'season': '2011-12', 'expected': 'Franchise Engine'},
    
    # Haliburton above Sabonis (must rank correctly)
    {'player': 'Tyrese Haliburton', 'season': '2021-22', 'expected': 'Strong Creator'},
    {'player': 'Domantas Sabonis', 'season': '2021-22', 'expected': 'Luxury Amplifier'},
    
    # Early-career stars identified as Engines
    {'player': 'Jayson Tatum', 'season': '2017-18', 'expected': 'Franchise Engine'},
    {'player': 'Luka Dončić', 'season': '2018-19', 'expected': 'Franchise Engine'},
    {'player': 'Shai Gilgeous-Alexander', 'season': '2020-21', 'expected': 'Franchise Engine'},
    
    # KAT identified as Fragile despite elite raw stats
    {'player': 'Karl-Anthony Towns', 'season': '2018-19', 'expected': 'Fragile Star'},
]

def validate_critical_cases(model, X, player_info):
    """Run validation on critical test cases."""
    passed = 0
    failed = 0
    
    for case in CRITICAL_CASES:
        mask = (
            (player_info['player_name'].str.lower() == case['player'].lower()) &
            (player_info['season'] == case['season'])
        )
        
        if not mask.any():
            print(f"⚠️  SKIP: {case['player']} {case['season']} - not in dataset")
            continue
        
        idx = mask.idxmax()
        pred = model.predict(X.loc[[idx]])[0]
        pred_label = archetype_order[pred]
        
        if pred_label == case['expected']:
            print(f"✅ PASS: {case['player']} {case['season']} = {pred_label}")
            passed += 1
        else:
            print(f"❌ FAIL: {case['player']} {case['season']} = {pred_label} (expected {case['expected']})")
            failed += 1
    
    print(f"\nResults: {passed}/{passed+failed} critical cases passed")
    return passed, failed
```

---

## 6. Testing & Validation

### 6.1 Unit Test Structure

Each component should have corresponding tests:

```python
# tests/test_cii_components.py

import pytest
import pandas as pd
from src.nba_data.phase2_creation_independence.index.self_created import (
    calculate_self_created_score,
    VALIDATION_CASES
)

class TestSelfCreatedScore:
    
    def test_simmons_near_zero(self):
        """Ben Simmons should score near zero (no self-created jumpers)."""
        simmons_data = pd.Series({
            'UNASSISTED_FG_PCT': 0.35,  # Low unassisted
            'ISO_POSS_RS': 0.5,         # Almost never ISOs
            'FGA_3_DRIBBLE': 0.2,       # No pull-ups
            'FGA_7_DRIBBLE': 0.1,
            'FGA_ISO_TOTAL': 0.3,
            'EFG_ISO_WEIGHTED': 0.0     # Never takes them
        })
        
        score = calculate_self_created_score(simmons_data)
        assert score < 15, f"Simmons should be <15, got {score}"
    
    def test_harden_elite(self):
        """James Harden should score elite (stepback king)."""
        harden_data = pd.Series({
            'UNASSISTED_FG_PCT': 0.65,
            'ISO_POSS_RS': 8.0,
            'FGA_3_DRIBBLE': 4.0,
            'FGA_7_DRIBBLE': 3.0,
            'FGA_ISO_TOTAL': 7.0,
            'EFG_ISO_WEIGHTED': 0.52
        })
        
        score = calculate_self_created_score(harden_data)
        assert score > 85, f"Harden should be >85, got {score}"
    
    @pytest.mark.parametrize("player,expected,tolerance", [
        (case, vals['expected_score'], vals['tolerance'])
        for case, vals in VALIDATION_CASES.items()
    ])
    def test_validation_cases(self, player, expected, tolerance):
        """Test against documented validation cases."""
        # This would load actual player data
        pass
```

### 6.2 Integration Testing

```python
# tests/test_cii_integration.py

def test_full_cii_pipeline():
    """Test complete CII calculation from raw data to archetype."""
    from src.nba_data.phase2_creation_independence.index.composite import (
        calculate_cii,
        batch_calculate_cii
    )
    
    # Load test data
    df = pd.read_csv('results/predictive_dataset_with_friction.csv')
    
    # Calculate CII for all players
    results = batch_calculate_cii(df)
    
    # Verify expected orderings
    simmons = results[results['player_name'].str.contains('Simmons', case=False)]
    harden = results[results['player_name'].str.contains('Harden', case=False)]
    
    assert simmons['cii'].mean() < harden['cii'].mean(), \
        "Harden should have higher CII than Simmons"
    
    # Verify archetype thresholds
    engines = results[results['archetype'] == 'Franchise Engine']
    assert engines['cii'].min() >= 80, "All Engines should have CII >= 80"
```

### 6.3 Validation Metrics

Track these metrics for model health:

| Metric | Target | Description |
|--------|--------|-------------|
| Critical Case Pass Rate | 100% | All validation cases must pass |
| Cross-Val Accuracy | >75% | 5-fold stratified CV |
| Simmons Detection | 100% | All Simmons seasons = Fragile |
| Harden OKC Detection | 100% | 2011-12 = Engine |
| Hali > Sabonis | 100% | Correct relative ranking |

---

## 7. Code Patterns & Conventions

### 7.1 Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | `snake_case.py` | `self_created.py` |
| Functions | `snake_case` | `calculate_pressure_appetite_score` |
| Classes | `PascalCase` | `StressVectorEngine` |
| Constants | `UPPER_SNAKE_CASE` | `VALIDATION_CASES` |
| Features | `UPPER_SNAKE_CASE` | `CLUTCH_USG_ABSOLUTE` |

### 7.2 Feature Engineering Pattern

```python
def calculate_new_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate [FEATURE_NAME] for all players.
    
    Physics Principle:
    [Explain the underlying basketball physics]
    
    Formula:
    [Show the mathematical formula]
    
    Validation:
    - [Player A] should be [high/low] because [reason]
    - [Player B] should be [high/low] because [reason]
    """
    logger.info(f"Calculating {FEATURE_NAME}...")
    
    # 1. Validate inputs exist
    required_cols = ['col_a', 'col_b']
    for col in required_cols:
        if col not in df.columns:
            logger.warning(f"{col} missing, using default")
            df[col] = DEFAULT_VALUE
    
    # 2. Calculate feature
    df['NEW_FEATURE'] = (
        df['col_a'] * WEIGHT_A +
        df['col_b'] * WEIGHT_B
    )
    
    # 3. Handle edge cases
    df['NEW_FEATURE'] = df['NEW_FEATURE'].fillna(0).clip(0, 1)
    
    # 4. Log statistics
    logger.info(f"  -> {FEATURE_NAME} calculated. Mean: {df['NEW_FEATURE'].mean():.4f}")
    
    return df
```

### 7.3 Normalization Pattern

Always normalize to 0-100 scale for CII components:

```python
from src.nba_data.utils.normalization import standardize_metric

def normalize_component(raw_scores: Dict[int, float]) -> Dict[int, float]:
    """
    Normalize raw component scores to 0-100 scale.
    
    Uses Z-score normalization with fixed anchors (not relative percentiles)
    to ensure consistent interpretation across seasons.
    """
    # Method 1: Fixed anchor normalization (preferred for CII)
    ANCHOR_MIN = 0.0   # Theoretical minimum
    ANCHOR_MAX = 10.0  # Elite threshold
    
    normalized = {
        k: min((v - ANCHOR_MIN) / (ANCHOR_MAX - ANCHOR_MIN) * 100, 100)
        for k, v in raw_scores.items()
    }
    
    return normalized
    
    # Method 2: Z-score normalization (use for relative comparisons)
    # return standardize_metric(raw_scores)
```

### 7.4 Logging Pattern

```python
import logging

logger = logging.getLogger(__name__)

# At start of major operation
logger.info(f"=== Processing {season} ===")

# For sub-steps
logger.info(f"  - Fetching {data_type}...")

# For warnings (non-fatal)
logger.warning(f"  ⚠️  {col} missing, using default")

# For errors (with stack trace)
logger.error(f"  ❌ Critical error: {e}", exc_info=True)

# For success
logger.info(f"  ✅ Successfully processed {n} records")
```

---

## 8. Step-by-Step Implementation Tasks

### Phase 1: Complete CII Components (Priority: HIGH)

#### Task 1.1: Self-Created Shot Score
**File**: `src/nba_data/phase2_creation_independence/index/self_created.py`

1. Create the file with skeleton from Section 4.1
2. Implement data fetching for missing metrics:
   - `UNASSISTED_FG_PCT` from player tracking
   - Pull-up shooting splits
3. Run validation cases
4. Integrate with `composite.py`

**Validation Command**:
```bash
python -c "from src.nba_data.phase2_creation_independence.index.self_created import *; print('OK')"
```

#### Task 1.2: Pressure Appetite Score
✅ **COMPLETE** - Implemented in `src/nba_data/phase2_creation_independence/index/pressure_appetite.py`.

1. Create file with skeleton from Section 4.2
2. Existing features available: `CLUTCH_USG_ABSOLUTE`, `RELATIVE_USAGE_DROP`
3. Add playoff usage comparison (if not available)
4. Validate Simmons << Luka

#### Task 1.3: Shot Difficulty Embrace Score
**File**: `src/nba_data/phase2_creation_independence/index/difficulty_embrace.py`

1. Create file with skeleton from Section 4.3
2. Collect missing data:
   - Defender distance stats from `CloseDefDistRange`
   - Mid-range volume from shot charts
3. Validate Simmons << Tatum

#### Task 1.4: Defensive Survival Score
**File**: `src/nba_data/phase2_creation_independence/index/defensive_survival.py`

1. Create file with skeleton from Section 4.4
2. Existing features: `QOC_TS_DELTA`, `FRAGILITY_SCORE`
3. Add playoff-specific metrics if available
4. Validate using known playoff performers

#### Task 1.5: Force Multiplication Score
**File**: `src/nba_data/phase2_creation_independence/index/force_multiplication.py`

1. Create file with skeleton from Section 4.5
2. Existing features: `RS_FTr`, `physicality_score`
3. Validate Giannis = maximum

### Phase 2: Update Composite Calculator (Priority: HIGH)

#### Task 2.1: Integrate Components
**File**: `src/nba_data/phase2_creation_independence/index/composite.py`

1. Replace placeholder functions with imports
2. Handle missing features gracefully
3. Add confidence scoring for missing data

```python
from .self_created import calculate_self_created_score
from .pressure_appetite import calculate_pressure_appetite_score
from .difficulty_embrace import calculate_difficulty_embrace_score
from .defensive_survival import calculate_defensive_survival_score
from .force_multiplication import calculate_force_multiplication_score

def calculate_cii(player_data: pd.Series) -> Dict:
    # ... implementation
```

### Phase 3: Classification System (Priority: MEDIUM)

#### Task 3.1: Expand Ground Truth
**File**: `phase2_creation_independence/ground_truth/player_labels.csv`

1. Add 20-30 more labeled player-seasons
2. Ensure class balance
3. Include edge cases

#### Task 3.2: Train Classifier
**File**: `phase2_creation_independence/classification/train_classifier.py`

1. Implement using skeleton from Section 5.2
2. Test with cross-validation
3. Analyze feature importance

#### Task 3.3: Validation Harness
**File**: `phase2_creation_independence/classification/validate.py`

1. Implement critical case testing
2. Ensure 100% pass rate on required cases
3. Add regression testing

### Phase 4: Data Collection Gaps (Priority: MEDIUM)

#### Task 4.1: Unassisted FG%
✅ **COMPLETE** - Collected via `MeasureType='Scoring'` in `collect_phase2_data.py`.

#### Task 4.2: Defender Distance
✅ **COMPLETE** - Collected via `leaguedashplayerptshot` and aggregated in `evaluate_plasticity_potential.py`.

#### Task 4.3: Playoff-Specific Stats
Ensure playoff usage and efficiency are captured.

---

## 9. Troubleshooting & Anti-Patterns

### 9.1 Common Mistakes to Avoid

#### ❌ Training on Outcomes
```python
# BAD: Predicting playoff PIE (outcome)
target = df['FUTURE_PEAK_HELIO']

# GOOD: Classifying archetype (process)
target = df['archetype']
```

#### ❌ Using Deltas Without Context
```python
# BAD: Delta alone loses baseline information
df['clutch_change'] = df['LEVERAGE_USG_DELTA']

# GOOD: Include absolute value
df['CLUTCH_USG_ABSOLUTE'] = df['USG_PCT'] + df['LEVERAGE_USG_DELTA']
```

#### ❌ Patching the Target
```python
# BAD: Manual penalty in target
df['target'] = df['helio'] - (df['abdication'] * 0.5)

# GOOD: Let model learn from features
df['FRAGILITY_SCORE'] = calculate_fragility(df)  # Feature, not target modification
```

#### ❌ Hard Gates
```python
# BAD: Binary threshold
if subsidy_index > 0.4:
    projected_volume = 0

# GOOD: Continuous gradient
projected_volume = current_volume * (1.0 - subsidy_index)
```

#### ❌ Ranking Before Filtering
```python
# BAD: Rank everyone, then filter
df['rank'] = df['score'].rank()
engines = df[df['rank'] < 10]

# GOOD: Filter to candidate pool, then rank
candidates = df[df['min_volume'] > threshold]
candidates['rank'] = candidates['score'].rank()
```

### 9.2 Debugging Checklist

When a validation case fails:

1. **Check data availability**
   ```python
   print(df[df['player_name'].str.contains('Simmons')][['season', 'CLUTCH_USG_ABSOLUTE', 'FRAGILITY_SCORE']])
   ```

2. **Verify feature calculations**
   ```python
   # Add logging to component
   logger.info(f"Simmons self_created_score breakdown: {sub_scores}")
   ```

3. **Compare against expectations**
   ```python
   from SPECIFICATION import EXPECTED_SCORES
   print(f"Expected: {EXPECTED_SCORES['Simmons']}, Got: {calculated}")
   ```

4. **Check for NaN contamination**
   ```python
   print(df[feature_cols].isna().sum())
   ```

5. **Review normalization**
   ```python
   print(df['component'].describe())  # Should be 0-100 range
   ```

### 9.3 Performance Optimization

For large batch processing:

```python
# Use vectorized operations instead of iterrows
df['cii'] = (
    0.30 * df['self_created'] +
    0.25 * df['pressure_appetite'] +
    0.20 * df['difficulty'] +
    0.15 * df['defense'] +
    0.10 * df['force']
)

# Cache expensive API calls
# (Already implemented in NBAStatsClient)

# Parallel season processing
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_season, seasons))
```

---

## Appendix A: Quick Reference Card

### CII Formula
```
CII = 0.30×Self + 0.25×Pressure + 0.20×Difficulty + 0.15×Defense + 0.10×Force
```

### Archetype Thresholds
```
Engine: 80+  |  Strong: 70-80  |  Amplifier: 55-70  |  Fragile: 40-55  |  Role: <40
```

### Critical Validation Cases
```
Simmons = Fragile (all seasons)
Harden OKC = Engine
Haliburton > Sabonis
Tatum/Luka/SGA early = Engine
KAT = Fragile
```

### Key Files
```
ACTIVE_CONTEXT.md     → Current state (READ FIRST)
SPECIFICATION.md      → CII formulas
KEY_INSIGHTS.md       → Learnings
composite.py          → Main calculator
player_labels.csv     → Ground truth
```

---

**Document Version**: 1.0  
**Last Updated**: December 27, 2025  
**Maintainer**: NBA Resilience Engine Team

