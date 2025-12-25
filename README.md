# NBA Playoff Resilience Engine

**Goal:** To build a predictive system that can accurately distinguish between immediate playoff contributors, future stars, and "fool's gold" players.

**Current Status:** ✅ **TELESCOPE MODEL v1 TRAINED**. HELIO_LOAD_INDEX targets generated and Telescope model trained (R² = 0.11). Next priority: Implement SHOT_QUALITY_GENERATION_DELTA feature to break R² ceiling.

---

## Quick Start

### 1. Understand the Project
- **`ACTIVE_CONTEXT.md`** - **START HERE** - Current project state, metrics, and next priorities. This file explains the "Two-Clock" (Crucible/Telescope) architecture.
- **`LUKA_SIMMONS_PARADOX.md`** - Theoretical foundation (why we built this).
- **`KEY_INSIGHTS.md`** - Critical lessons learned during the project.

### 2. Set Up Environment
```bash
pip install -r requirements.txt
mkdir -p data/cache models results logs
```

### 3. Run the Pipeline
The pipeline is now a two-stage process, reflecting our "Two-Clock" architecture.

**Stage 1: The Crucible (Current Viability)**
```bash
# 1. Build the Crucible Dataset (Maps RS Physics to Playoff Impact)
python src/nba_data/scripts/build_crucible_dataset.py

# 2. Train the Crucible Model
python src/nba_data/scripts/train_crucible_model.py

# 3. Apply the model to all players to get their "Viability Score"
python src/nba_data/scripts/detect_ghost_risk.py
```

**Stage 2: The Telescope (Future Potential) - *Phase 4 Implementation***

```bash
# 1. Generate HELIO targets (predicting peak future playoff scalability)
python src/nba_data/scripts/generate_helio_targets.py

# 2. Train the Telescope model
python src/nba_data/scripts/train_telescope_model.py

# 3. Evaluate performance and plan feature enhancements
# Current: R² = 0.11, USG_PCT strongest driver
# Next: Add SHOT_QUALITY_GENERATION_DELTA to distinguish "System Merchants" from "Scalable Engines"
```

### 4. Run Validation Tests
```bash
# Run the test suite for the Crucible model
python tests/validation/test_crucible_model.py
```

### 5. Launch Interactive App (Future)
The Streamlit app will be updated to synthesize the outputs of both the Crucible and Telescope models into a unified 2D Risk Matrix.

---

## Current Model: The Crucible Engine

**Algorithm:** XGBoost Regressor
**Target:** `PIE_TARGET` (Player Impact Estimate) - an objective measure of playoff performance.
**R2 Score:** **0.4715** - Indicates a strong relationship between our physics-based features and actual playoff impact.
**Test Suite Performance:**
- **Overall Pass Rate:** 41.67%
- **Key Success**: Excels at identifying "Mirage Breakouts" and "Inefficient Volume" players without the need for manual gates.
- **Area for Improvement**: Struggles to identify latent stars and rookies, which is the explicit job of the upcoming "Telescope" model.

---

## Key Files

### Core Scripts
- `src/nba_data/scripts/build_crucible_dataset.py`
- `src/nba_data/scripts/train_crucible_model.py`
- `src/nba_data/scripts/detect_ghost_risk.py`

### Test Scripts
- `tests/validation/test_crucible_model.py`

### Data Files
- `data/crucible_dataset.csv`: The training set for the Crucible model.
- `results/physics_adjusted_impact.csv`: The output of the Crucible model for all players.

### Model Files
- `models/crucible_impact_model.pkl`: **CURRENT MODEL**

---

## Documentation
- **`ACTIVE_CONTEXT.md`** - **START HERE** - Explains the "Two-Clock" architecture.
- **`KEY_INSIGHTS.md`** - Hard-won lessons.
- **`LUKA_SIMMONS_PARADOX.md`** - Theoretical foundation.
- `results/physics_model_validation_report.md`: Detailed report on the Crucible model's performance.
- `results/crucible_model_test_report.csv`: Raw output of the test suite.
