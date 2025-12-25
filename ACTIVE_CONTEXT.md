# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 24, 2025
**Status**: 🔬 **HELIO PIVOT VALIDATED** - Original HELIO_INDEX falsified via simulation. New HELIO_LOAD_INDEX formula (Offensive_Load^1.3 × Efficiency_Delta) correctly ranks Jokić #1 while Gobert scores near zero. Ready for implementation.

---

## Project Goal

To build a predictive system that can accurately distinguish between immediate playoff contributors, future stars, and "fool's gold" players by modeling the orthogonal physics of **Viability** and **Scalability**.

---

## Core Architecture: The "Two-Clock" System

### 1. The Crucible (The "Camera" - Viability Engine)
- **Status**: ✅ Implemented & Validated
- **Purpose**: Answers the question: *"If you drop this player into a playoff series **today**, will they survive?"*
- **Target Variable**: `Current_Season_Playoff_PIE`
- **Output**: `CRUCIBLE_SCORE` (1 - Probability of Liability)

### 2. The Telescope (The "Projection" - Potential Engine)
- **Status**: 🔬 **TARGET FORMULA VALIDATED** - HELIO_LOAD_INDEX correctly identifies heliocentric engines (Jokić #1, Gobert near zero)
- **Purpose**: Answers the question: *"What is this player's **peak scalability** over the next 3 seasons?"*
- **Target Variable**: `FUTURE_PEAK_HELIO_LOAD_INDEX` - MAX(HELIO_LOAD_INDEX) over next 3 playoff runs, 0 for washouts
- **Formula**: `(OFFENSIVE_LOAD^1.3) × EFFICIENCY_DELTA` where `OFFENSIVE_LOAD = USG_PCT + (AST_PCT × 0.75)`
- **Methodology**:
    1. **Future Peak Logic**: Target is peak scalability in playoff runs N+1 to N+3.
    2. **Washout Imputation**: Players with <100 playoff minutes in 3-year window get Target = 0.
    3. **Non-Linear Load Scaling**: Exponent 1.3 separates true engines from hyper-efficient role players.
- **Features**: Current physics-based features (CREATION_TAX, LEVERAGE_TS_DELTA, etc.)
- **Output**: `TELESCOPE_SCORE` (Predicted Future HELIO_LOAD_INDEX)

---

## The 2D Risk Matrix

The system now categorizes players based on the intersection of the two clocks:

| Category | Crucible Score | Telescope Score | Interpretation | Example Result |
| :--- | :--- | :--- | :--- | :--- |
| **Franchise Cornerstone** | High | High | Great Now, Great Later | **Nikola Jokić (2018-19)** |
| **Latent Star** | Low | High | Bad Now, Great Later | *Jalen Brunson (Early Career)* |
| **Win-Now Piece** | High | Low | Great Now, Capped Later | *Veteran Role Player* |
| **Ghost/Avoid** | Low | Low | Bad Now, Bad Later | **Jordan Poole (2021-22)** |

---

## Validation Results: Physics Compliance Achieved

**Test Suite Results**: System demonstrates **physics compliance** (no skill hallucination) but **teleological confusion** (wrong optimization target).

### ✅ **HELIO Formula Validation (Target Pivot Success)**
- **Nikola Jokić (2024-25 Peak)**: **#1 Overall** ✓ (Correctly identifies heliocentric engine)
- **James Harden (2017-18 Peak)**: **#4 Overall** ✓ (Elite load + efficiency maintained)
- **Tyrese Haliburton (2023-24 Peak)**: **#11 Overall** ✓ (Rises into elite tier)
- **Rudy Gobert (2021-22 Peak)**: **#96 Overall** ✓ (Near zero - correctly penalized for low load)
- **DeMar DeRozan (2019-20 Peak)**: **#20 Overall** ✓ (No longer artificially inflated)

### 🔍 **Falsification Process Completed**
Original HELIO_INDEX `(USG × TS × Creation_Ratio)` was **falsified** via simulation:
- **Jokić ranked #67** (failed the engine test)
- **Gobert ranked #31** (failed the role player test)
- **New HELIO_LOAD_INDEX** passes all validation checks

---

## Next Developer: Start Here

**Current State**: HELIO_LOAD_INDEX formula validated via simulation. Ready to implement the target generation pipeline.

**Highest Leverage Action**: Execute the **HELIO_LOAD_INDEX Target Generation**
- **Why**: Transform the Telescope from predicting "Good Players" to predicting "Scalable Engines."
- **How**: Create `src/nba_data/scripts/generate_helio_targets.py` implementing the Future Peak logic with 3-year lookahead window.
- **Impact**: Will correctly identify heliocentric engines while penalizing utility-focused role players.

**Implementation Plan**: See `PHASE_4_HELIO_IMPLEMENTATION_PLAN.md` for detailed steps.

**Secondary Priorities** (After HELIO Pivot):
1.  **Dataset Expansion**: Process additional seasons for larger training set.
2.  **Dashboard Integration**: Visualize 2D Risk Matrix in Streamlit app.
3.  **Model Refinement**: Tune thresholds and interaction terms.

**Key Scripts**:
- `scripts/evaluate_helio_target.py` (Original HELIO_INDEX simulation - falsified)
- `scripts/evaluate_helio_load.py` (HELIO_LOAD_INDEX simulation - validated)
- `src/nba_data/scripts/evaluate_plasticity_potential.py` (Physics Engine)
- `src/nba_data/scripts/build_crucible_dataset.py` (Dataset Synthesis)
- `src/nba_data/scripts/generate_telescope_targets.py` (Target Generation)
- `src/nba_data/scripts/project_player_avatars.py` (Universal Projection)
- `src/nba_data/scripts/train_telescope_model.py` (Model Training)
- `src/nba_data/scripts/predict_2d_risk_matrix.py` (Synthesis)
- `src/nba_data/scripts/validate_2d_risk_matrix.py` (Validation)

**Simulation Results**:
- `results/helio_index_simulation.csv` (Original formula - falsified)
- `results/helio_load_simulation.csv` (New formula - validated)</content>
<parameter name="file_path">ACTIVE_CONTEXT.md