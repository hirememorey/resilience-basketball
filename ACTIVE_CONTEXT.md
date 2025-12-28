# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 27, 2025
**Status**: 🔄 **PHASE 2: CREATION INDEPENDENCE** - "The Right Question"

---

## The Pivot

We discovered that Phase 1 was asking the **wrong question**:

- **Phase 1 asked**: "How good will this player be?" (predicting future playoff PIE)
- **Phase 2 asks**: "Can this player create when schemed?" (measuring creation independence)

### Why Phase 1 Failed

The fundamental issue was the **Ground Truth Trap**:
- Ben Simmons had decent playoff PIE (pre-2021) because of Embiid + shooters
- The model learned Simmons was "good" because his outcomes were good
- But his **process** (zero self-created shots, hiding under pressure) was fragile
- We could patch this with abdication penalties, but patches aren't learning

### The Creation Independence Insight

The key differentiator between true stars and fragile ones is **creation independence**:
- **Harden at OKC**: Give him the ball and get out of the way. He IS the situation.
- **Simmons**: Needs shooters, Embiid doubles, transition. He needs the situation.

This leads to our new question: **"Does this player need the right situation, or IS he the situation?"**

---

## Phase 2: Creation Independence Index (CII)

### Location
`/src/nba_data/phase2_creation_independence/`

### Components

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| Self-Created Shot Score | 30% | Can you get a shot without a play? |
| Pressure Appetite Score | 25% | Do you WANT the ball in clutch? |
| Shot Difficulty Embrace | 20% | Do you take hard shots or hide? |
| Defensive Survival Score | 15% | Do you maintain against schemes? |
| Force Multiplication Score | 10% | Do you create through physicality? |

### Archetypes (Classification Target)

| Archetype | CII Range | Definition |
|-----------|-----------|------------|
| Franchise Engine | 80+ | Can be #1 on a championship team |
| Strong Creator | 70-80 | High creation, optimal as #2 |
| Luxury Amplifier | 55-70 | Excellent, needs an Engine |
| Fragile Star | 40-55 | Looks like Engine, fatal flaws |
| Role Player | <40 | Solid contributor, not a star |

### Ground Truth
Curated labels in `/ground_truth/player_labels.csv` - 40+ player-seasons with expert archetypes.

---

## Phase 1 Archive

Phase 1 work preserved in `/src/nba_data/phase1_helio_archive/`:
- `train_telescope_model.py` - XGBoost regressor
- `validate_telescope_resilience.py` - 35 test cases
- Achieved 60% pass rate with abdication penalty
- See `/phase1_helio_archive/README.md` for details

### Key Phase 1 Learnings
1. **Features were valuable**: `clutch_usg_absolute`, `abdication_interaction` have signal
2. **Target was wrong**: `FUTURE_PEAK_HELIO` rewarded converters, not creators
3. **Patches don't scale**: Abdication penalty worked but violated "learn don't patch"
4. **Wrong question**: Outcomes ≠ Process, need to measure creation directly

---

## Current Pipeline (Preserved)

### Data Collection (Still Active)
- `/src/nba_data/scripts/` - All collection scripts unchanged
- Playtype, tracking, shot quality, clutch splits, defensive context

### Feature Engineering (Still Active)
- `evaluate_plasticity_potential.py` - Generates features
- Output: `results/predictive_dataset_with_friction.csv`
- Key features: `clutch_usg_absolute`, `relative_usage_drop`, `abdication_interaction`

---

## Implementation Status (December 27, 2025)

### ✅ Completed

1. **Implementation Guide Created**: `IMPLEMENTATION_GUIDE.md`
   - Comprehensive technical documentation from first principles
   - Covers theory, architecture, data pipeline, and step-by-step tasks
   - Includes code patterns, validation approach, and troubleshooting

2. **CII Component Skeletons Implemented**:
   - `index/self_created.py` - Self-Created Shot Score (30%)
   - `index/pressure_appetite.py` - Pressure Appetite Score (25%)
   - `index/difficulty_embrace.py` - Shot Difficulty Embrace (20%)
   - `index/defensive_survival.py` - Defensive Survival Score (15%)
   - `index/force_multiplication.py` - Force Multiplication Score (10%)
   - `index/composite.py` - Updated with proper imports and validation

3. **Each Component Includes**:
   - Full docstrings explaining physics principle
   - Sub-metric breakdown with weights
   - Calculation logic using existing + placeholder features
   - Validation cases from SPECIFICATION.md
   - Self-test capability

---

## Next Steps

### Priority 1: Data Collection (Required for full CII)
- [ ] Collect `UNASSISTED_FG_PCT` from tracking data
- [ ] Collect `CONTESTED_SHOT_RATE` from `CloseDefDistRange`
- [ ] Collect `MIDRANGE_FGA_PER_GAME` from shot charts
- [ ] Collect `PULLUP_3PT_RATE` from shooting splits
- [ ] Collect `PLAYOFF_TS_PCT` and `PLAYOFF_USG_PCT`

### Priority 2: Integration Testing
- [ ] Run `batch_calculate_cii()` on existing dataset
- [ ] Verify Simmons < Harden ordering
- [ ] Verify Haliburton > Sabonis ordering
- [ ] Check all validation cases pass

### Priority 3: Classifier Training
- [ ] Expand ground truth labels to 60+ player-seasons
- [ ] Implement `train_classifier.py`
- [ ] Achieve 100% critical case pass rate

### Priority 4: Deployment
- [ ] Apply to current season data
- [ ] Identify latent stars

---

## Key Decision: Creator vs. Converter

The central question for any player:

> **Creators** can manufacture efficient offense against engaged defenses.
> **Converters** can only cash in opportunities that the system creates.

| | High Efficiency | Low Efficiency |
|---|---|---|
| **High Creation** | FRANCHISE ENGINE | Struggling Star |
| **Low Creation** | LUXURY AMPLIFIER | Role Player |

Ben Simmons is in the bottom-left: efficient but dependent. The model must identify this.

---

## Files to Reference

| File | Purpose |
|------|---------|
| **`IMPLEMENTATION_GUIDE.md`** | **NEW: Complete technical guide for developers** |
| `phase2_creation_independence/SPECIFICATION.md` | Detailed CII spec |
| `phase2_creation_independence/index/composite.py` | Main CII calculator |
| `phase2_creation_independence/index/self_created.py` | Component 1 implementation |
| `phase2_creation_independence/index/pressure_appetite.py` | Component 2 implementation |
| `phase2_creation_independence/index/difficulty_embrace.py` | Component 3 implementation |
| `phase2_creation_independence/index/defensive_survival.py` | Component 4 implementation |
| `phase2_creation_independence/index/force_multiplication.py` | Component 5 implementation |
| `phase2_creation_independence/ground_truth/player_labels.csv` | Expert labels |
| `KEY_INSIGHTS.md` | 80+ learnings from Phase 1 |
| `LUKA_SIMMONS_PARADOX.md` | Theoretical foundation |

---

## Quick Start for New Developers

```bash
# 1. Read the implementation guide
cat IMPLEMENTATION_GUIDE.md

# 2. Test CII calculation
python -c "from src.nba_data.phase2_creation_independence.index import batch_calculate_cii; print('OK')"

# 3. Run component tests
python src/nba_data/phase2_creation_independence/index/self_created.py
python src/nba_data/phase2_creation_independence/index/pressure_appetite.py
```
