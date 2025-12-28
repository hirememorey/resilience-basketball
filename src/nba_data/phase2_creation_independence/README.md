# Phase 2: Creation Independence Index

**Status**: Foundation Complete  
**Date**: December 27, 2025

## Mission

Build a latent star detection model that identifies franchise cornerstones BEFORE consensus recognition, by measuring their ability to create offense when the defense knows it's coming.

## The Core Insight

Phase 1 asked: **"How good will this player be?"** (predicting future playoff PIE)

Phase 2 asks: **"Can this player create when schemed?"** (measuring creation independence)

The difference:
- **Simmons** looked good in Phase 1 because his raw playoff PIE was decent (propped up by Embiid + shooters)
- **Simmons** fails Phase 2 because he has zero self-created shots and hides under pressure

## Directory Structure

```
/phase2_creation_independence/
  /index/                    # CII calculation modules
    - self_created.py        # Component 1: Self-Created Shot Score
    - pressure_appetite.py   # Component 2: Pressure Appetite Score
    - difficulty_embrace.py  # Component 3: Shot Difficulty Score
    - defensive_survival.py  # Component 4: Defensive Attention Survival
    - force_multiplication.py # Component 5: Force Score
    - composite.py           # Combined CII calculation
    
  /classification/           # Archetype prediction
    - train_classifier.py    # Train archetype classifier
    - validate.py            # Validation against ground truth
    - predict.py             # Predict archetype for new players
    
  /ground_truth/             # Curated labels
    - player_labels.csv      # Expert-labeled player archetypes
    
  SPECIFICATION.md           # Detailed spec for CII
  README.md                  # This file
```

## Archetypes

| Archetype | Definition | CII Range |
|-----------|------------|-----------|
| **Franchise Engine** | Can be #1 on a championship team | 80+ |
| **Strong Creator** | High creation, optimal as #2 | 70-80 |
| **Luxury Amplifier** | Excellent, needs an Engine | 55-70 |
| **Fragile Star** | Looks like Engine, fatal flaws | 40-55 |
| **Role Player** | Solid contributor, not a star | <40 |

## Key Test Cases

| Player | Expected | Why |
|--------|----------|-----|
| Harden (OKC) | Engine | Elite ISO, stepback, FTr even as 6th man |
| Simmons | Fragile Star | Zero self-created jumpers, hides in clutch |
| Haliburton | Strong Creator | Elite PnR creation, portable skills |
| Sabonis | Amplifier | Needs plays run for him, can't self-create |
| KAT | Fragile Star | Has skills but can't impose them |
| Luka | Engine | Maximum creation independence |
| SGA | Engine | Elite self-creation, high force |

## What's Preserved from Phase 1

### Data Assets (Still Active)
- All data collection scripts in `/scripts/`
- Raw CSV files in `/data/` and `/results/`
- Feature engineering in `evaluate_plasticity_potential.py`

### Features (Reusable)
- `clutch_usg_absolute` → feeds Pressure Appetite Score
- `relative_usage_drop` → feeds Pressure Appetite Score
- `abdication_interaction` → useful signal
- `creation_volume_ratio` → feeds Self-Created Score
- `time_of_poss` → context for creation
- Free throw rate → feeds Force Score

### Learnings (Documented)
- See `KEY_INSIGHTS.md` for 40+ lessons
- See `phase1_helio_archive/README.md` for why Phase 1 was archived

## Next Steps

1. [ ] Implement each CII component function
2. [ ] Calculate CII for all players in ground truth
3. [ ] Validate CII ranking against labels
4. [ ] Train archetype classifier
5. [ ] Test on blind validation set
6. [ ] Deploy for current season predictions

## Success Criteria

1. **Simmons correctly identified** as Fragile Star in all pre-collapse seasons
2. **Harden at OKC correctly identified** as Engine despite 6th man role  
3. **Haliburton ranked above Sabonis** before the trade
4. **Early-career engines** (Tatum, SGA, Luka) correctly identified
5. **KAT correctly identified** as Fragile Star despite elite raw stats

## Principles

1. **Creation over Outcomes**: Measure the process, not the result
2. **Portable over Contextual**: Skills that work anywhere beat system fit
3. **Pressure Appetite**: Who wants the ball when it matters?
4. **Self-Sufficiency**: "Give him the ball and get out of the way"

