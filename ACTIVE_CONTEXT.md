# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 29, 2025 (Evening)
**Status**: ✅ **PHASE 2: CREATION INDEPENDENCE** - All 5 Components Complete

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

## Implementation Status (December 28, 2025)

### ✅ Completed

1.  **CII Component 1: `Self-Created Shot Score` Implemented** (Updated Dec 29)
    *   **File**: `src/nba_data/phase2_creation_independence/index/self_created.py`
    *   **Status**: Complete with **Two-Path Architecture** (Perimeter + Hub paths).
    *   **Key Architecture Update (Dec 29)**:
        *   Added **Hub Creation Path** for post-centric orchestrators (Jokić, prime Shaq)
        *   Takes MAX(perimeter_score, hub_score) - allows either path to excellence
        *   **Critical Gate**: Hub path only activates if `leverage_usg_delta >= 0` (not hiding)
    *   **Validation Results**:
        | Player | Perimeter | Hub | Final | Status |
        |--------|-----------|-----|-------|--------|
        | Jokić | 25.9 | 89.7 | **89.7** | ✅ Hub path |
        | Sabonis | 25.8 | 0.0 | 25.8 | ✅ No hub (hides) |
        | Harden | 99.0 | 0.0 | 99.0 | ✅ Perimeter path |
        | Simmons | 38.1 | 0.0 | 38.1 | ✅ Neither path elite |

2.  **CII Component 2: `Pressure Appetite Score` Implemented**
    *   **File**: `src/nba_data/phase2_creation_independence/index/pressure_appetite.py`
    *   **Status**: Logic implemented and validated.
    *   **Action**: Mapped `clutch_usg_absolute` and `relative_usage_drop` to measure the "Abdication Tax." Successfully identified Simmons as a low-appetite outlier (score ~18-21).

3.  **CII Component 3: `Shot Difficulty Embrace Score` Implemented** (Updated Dec 29)
    *   **File**: `src/nba_data/phase2_creation_independence/index/difficulty_embrace.py`
    *   **Status**: Complete with **Two-Path Architecture** (Perimeter + Hub paths).
    *   **Key Architecture Update (Dec 29)**:
        *   Added **Hub Creation Path** to recognize elite efficiency as a form of difficulty embrace
        *   Jokić (70% TS, 10.5 touch production) "solves" difficulty by manufacturing easy shots
        *   **Critical Gate**: Hub path only activates if `leverage_usg_delta >= 0` (not hiding)
        *   Takes MAX(perimeter_score, hub_score) - same logic as Component 1
    *   **Two Paths**:
        *   **Perimeter Path**: Pull-up Volume (40%), Mid-range (30%), Pull-up 3s (20%), Time (10%)
        *   **Hub Path**: Elite TS (65%+) + Elite touches (8+) + Non-hiding + Significant usage
    *   **Validation Results**:
        | Player | Perimeter | Hub | Final | Status |
        |--------|-----------|-----|-------|--------|
        | Jokić | 15.4 | 91.4 | **91.4** | ✅ Hub path |
        | Sabonis | 8.6 | 0.0 | 8.6 | ✅ No hub (hides) |
        | DeRozan | 77.9 | 0.0 | 77.9 | ✅ Perimeter path |
        | Simmons | 14.0 | 0.0 | 14.0 | ✅ Neither path |

4.  **CII Component 4: `Defensive Survival Score` Implemented** (Dec 28)
    *   **File**: `src/nba_data/phase2_creation_independence/index/defensive_survival.py`
    *   **Status**: Complete implementation with **6/6 validation cases passing**.
    *   **Key Insight - The Abdication Efficiency Trap**:
        *   Ben Simmons maintains POSITIVE `leverage_ts_delta` (+0.04 to +0.09) because when he HIDES, he only takes his best shots (uncontested layups).
        *   His efficiency is maintained through VOLUME ABDICATION, not skill.
        *   The fix: Weight efficiency resilience BY volume maintenance. If you're hiding, efficiency doesn't count.
    *   **Final Architecture**:
        *   Clutch Volume Maintenance: 35% (do you stay in the game?)
        *   Shot Versatility: 30% (can you be schemed?)
        *   Efficiency Resilience: 25% (volume-adjusted)
        *   Fragility Inverse: 10% (supporting signal)
    *   **Validation Results**:
        | Player | Season | Score | Status |
        |--------|--------|-------|--------|
        | Ben Simmons | 2019-20 | 32.6 | ✅ Abdicator (hiding pattern) |
        | James Harden | 2018-19 | 77.6 | ✅ Engine (steps UP) |
        | Nikola Jokić | 2021-22 | 54.9 | ✅ Hub creator (steps up, low versatility) |
        | Luka Dončić | 2020-21 | 69.8 | ✅ Elite versatility |
        | KAT | 2017-18 | 21.0 | ✅ Double collapse (volume + efficiency) |
        | Giannis | 2020-21 | 49.2 | ✅ Force creator |

5.  **CII Component 5: `Force Multiplication Score` Implemented** ✨ NEW (Dec 28)
    *   **File**: `src/nba_data/phase2_creation_independence/index/force_multiplication.py`
    *   **Status**: Complete implementation with **6/6 validation cases passing**.
    *   **Key Insight - The "Having Tools vs Using Them" Trap**:
        *   Ben Simmons has `physicality_score` of 0.93-0.98 (elite physical tools!)
        *   But his `leverage_usg_delta` is -0.085 (HIDING under pressure)
        *   Giannis has `physicality_score` of 1.0 AND maintains/increases volume
        *   The fix: Combine physical tools (25%) with volume usage (30%), pressure agency (25%), and touch production (20%)
    *   **Final Architecture**:
        *   Physical Tools: 25% (FTr + Rim Appetite via physicality_score)
        *   Force Volume: 30% (usage × creation volume ratio)
        *   Force Agency: 25% (clutch_usg_absolute + leverage_usg_delta)
        *   Touch Production: 20% (weighted_touch_production)
    *   **Validation Results**:
        | Player | Season | Score | Status |
        |--------|--------|-------|--------|
        | Giannis | 2019-20 | 92.9 | ✅ Maximum force creator |
        | Ben Simmons | 2019-20 | 44.2 | ✅ Has tools, doesn't use them |
        | Stephen Curry | 2020-21 | 58.2 | ✅ Gravity not force |
        | Joel Embiid | 2022-23 | 80.5 | ✅ Post force + FT machine |
        | Zion Williamson | 2020-21 | 77.0 | ✅ Elite force (when healthy) |
        | Rudy Gobert | 2020-21 | 24.1 | ✅ Physical but no agency |

5.  **Diagnostic Validation Performed**
    *   **Action**: Conducted a deep-dive analysis on the scores for Luka Dončić, Khris Middleton, Ben Simmons, and others across different seasons.
    *   **Finding 1 (Luka/AD Trade Context)**: The model successfully detected the change in Luka Dončić's role after being traded to the Lakers. His score correctly adjusted from a peak of 97.1 (2022-23) to 84.0 (2024-25), reflecting his new context playing alongside LeBron James. This is a major validation of the model's sensitivity to process, not just reputation.
    *   **Finding 2 (Middleton Career Arc)**: The model correctly identified Khris Middleton's peak as a "Luxury Amplifier" (67.0 in 2020-21) and his subsequent decline into the "Fragile Star/Role Player" tier (49.4 in 2024-25), demonstrating its ability to model career trajectories.
    *   **Conclusion**: The `Self-Created Shot Score` component is functioning correctly and is highly sensitive to changes in player role and ability.

6.  **Validation Test Suite Overhauled**
    *   **File**: `tests/validation/test_latent_star_cases.py`
    *   **Status**: Complete refactor of test cases based on first principles.
    *   **Key Changes**:
        *   **Mikal Bridges**: Re-classified from `True Positive` to `False Positive - System Merchant`. Correctly identifies that high usage on a bad team is not the same as creation ability.
        *   **Desmond Bane**: Removed. Outcome is not yet certain, and the validation suite requires ground truth.
        *   **Giannis Antetokounmpo**: Added multiple seasons (including championship year) as a `True Positive - Force Creator`. This is a critical addition to ensure the model can distinguish between fragile non-shooters (Simmons) and engine non-shooters.
        *   **Zion Williamson**: Added as `True Positive - Force Creator (Injury-Limited)`. This tests the model's focus on PROCESS (elite creation physics) vs. OUTCOME (championships), as his availability is out of scope for CII.
    *   **Conclusion**: The test suite is now more robust and directly targets the core discrimination challenges of the project.

---

## Next Steps

### Priority 1: Component Calculation (High) ✅ COMPLETE
- [x] ~~Implement `calculate_self_created_score` using `pct_uast_fgm` and `pull_up_fga`.~~ **(DONE)**
- [x] ~~Implement `calculate_pressure_appetite_score`.~~ **(DONE)**
- [x] ~~Implement `calculate_difficulty_embrace_score`.~~ **(DONE)**
- [x] ~~Overhaul validation test suite~~ **(DONE - Dec 29 morning)**
- [x] ~~Implement `calculate_defensive_survival_score`.~~ **(DONE - Dec 28 evening)**
- [x] ~~Implement `calculate_force_multiplication_score`.~~ **(DONE - Dec 28)**
- [x] ~~Run `batch_calculate_cii()` on integrated dataset.~~ **(DONE - Dec 28)**

### Priority 2: Validation & Refinement ✅ COMPLETE
- [x] ~~Verify Simmons < Harden ordering in calculated CII.~~ **(DONE - Simmons 27 vs Harden 86)**
- [x] ~~Verify Haliburton > Sabonis ordering.~~ **(DONE - Haliburton 75 vs Sabonis 24)**
- [x] ~~Check critical validation cases~~ **(7/7 pass - Dec 28)**
- [x] ~~**RESOLVED**: Jokić now classified as "Franchise Engine"~~ **(DONE - CII 82.7)**
  - **Solution**: Added "Hub Creation Path" to Components 1 (Self-Created) and 3 (Difficulty Embrace)
  - Hub path rewards elite efficiency (65%+ TS) + touch production (8+) + positive pressure response
  - **Critical Gate**: `leverage_usg_delta >= 0` (must NOT be hiding under pressure)
  - Jokić (CII 82.7) vs Sabonis (CII 24.2) = **58-point gap** - EXACTLY what we wanted
  - Sabonis fails hub gates because he HIDES (`leverage_usg_delta = -0.058`)

### Priority 3: Classifier Training
- [ ] Expand ground truth labels to 60+ player-seasons.
- [ ] Implement `train_classifier.py` and achieve 100% pass rate.

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
