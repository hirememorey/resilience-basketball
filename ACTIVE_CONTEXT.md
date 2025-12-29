# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 29, 2025 (Morning)
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

## Implementation Status (December 28, 2025)

### ✅ Completed

1.  **CII Component 1: `Self-Created Shot Score` Implemented**
    *   **File**: `src/nba_data/phase2_creation_independence/index/self_created.py`
    *   **Status**: Logic implemented, validated against key players, and pushed to repo.
    *   **Action**: Mapped theoretical metrics to concrete data columns (`pct_uast_fgm`, `pull_up_fga`, etc.).

2.  **CII Component 2: `Pressure Appetite Score` Implemented**
    *   **File**: `src/nba_data/phase2_creation_independence/index/pressure_appetite.py`
    *   **Status**: Logic implemented and validated.
    *   **Action**: Mapped `clutch_usg_absolute` and `relative_usage_drop` to measure the "Abdication Tax." Successfully identified Simmons as a low-appetite outlier (score ~18-21).

3.  **CII Component 3: `Shot Difficulty Embrace Score` Implemented**
    *   **File**: `src/nba_data/phase2_creation_independence/index/difficulty_embrace.py`
    *   **Status**: Complete rewrite with **7/7 validation cases passing**.
    *   **Key Learnings**:
        *   **The Contested Shot Rate Trap**: Simmons (0.76) and Gobert (0.85) have the HIGHEST contested shot rates because they only take layups/dunks in traffic. Naive use of this metric would score them as "difficulty embracers."
        *   **The Fix**: Replaced `contested_shot_rate` with jump shot metrics (`pull_up_fga`, `pct_pts_2pt_mr`, `pull_up_fg3a`) as primary signals.
        *   **Giannis/Shaq Consideration**: Force creators get credit through Components 1 and 5, not Component 3. This keeps the component focused on "shot difficulty" specifically.
    *   **Final Architecture**:
        *   Pull-up Volume: 40% (the key differentiator)
        *   Mid-range %: 30%
        *   Pull-up 3 Volume: 20%
        *   Time of Possession: 10%
    *   **Validation Results**:
        | Player | Score | Status |
        |--------|-------|--------|
        | Rudy Gobert | 0.2 | ✅ Pure finisher |
        | Zion Williamson | 10.1 | ✅ Force creator (C1/C5) |
        | Ben Simmons | 24.3 | ✅ Minimal jumpers |
        | Giannis | 36.9 | ✅ Hybrid |
        | Tatum | 51.9 | ✅ Perimeter creator |
        | Middleton | 64.7 | ✅ Elite mid-range |
        | DeRozan | 77.8 | ✅ Maximum mid-range |

4.  **CII Component 4: `Defensive Survival Score` Implemented** ✨ NEW (Dec 28)
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

### Priority 1: Component Calculation (High)
- [x] ~~Implement `calculate_self_created_score` using `pct_uast_fgm` and `pull_up_fga`.~~ **(DONE)**
- [x] ~~Implement `calculate_pressure_appetite_score`.~~ **(DONE)**
- [x] ~~Implement `calculate_difficulty_embrace_score`.~~ **(DONE)**
- [x] ~~Overhaul validation test suite~~ **(DONE - Dec 29 morning)**
- [x] ~~Implement `calculate_defensive_survival_score`.~~ **(DONE - Dec 28 evening)**
- [ ] Implement `calculate_force_multiplication_score`.
- [ ] Run `batch_calculate_cii()` on integrated dataset.

### Priority 2: Validation & Refinement
- [ ] Verify Simmons < Harden ordering in calculated CII.
- [ ] Verify Haliburton > Sabonis ordering.
- [ ] Check all critical validation cases from `SPECIFICATION.md` using **peak seasons**.

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
