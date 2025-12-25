# Telescope Model Implementation Report

## Summary
The "Telescope" (Future Potential Engine) has been implemented with **physics compliance** (no skill hallucination) but requires target variable refinement. The system achieves mechanical soundness but optimizes for the wrong goal.

## Key Outcomes

### 1. The Separation of Concerns
The system now distinctively separates "Viability" (Current Floor) from "Scalability" (Future Ceiling).
- **Crucible**: Measures friction, turnovers, and defensive liability.
- **Telescope**: Measures creation volume, age-adjusted efficiency, and leverage scaling.

### 2. Physics Compliance Achieved
**Critical Bug Fixed**: Initial implementation hallucinated skills during projection (e.g., turning Rudy Gobert into a creation machine). Fixed with **percentile preservation** logic that maintains relative rank within usage buckets.

### 3. Current Validation State
The system demonstrates **meaningful predictive validity** but with target misalignment:

| Player (Season) | Crucible Score (Viability) | Telescope Score (Potential) | Categorization | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Jalen Brunson (2021-22)** | **Low** | **High** | **Latent Star** | ✅ **PASS** |
| **Jordan Poole (2021-22)** | **Low** | **Low** | **Ghost/Avoid** | ✅ **PASS** |
| **Rudy Gobert (2015-16)** | **High** | **High** | **Latent Star** | ❌ **FAIL** (PIE target) |
| **DeRozan (2015-16)** | **High** | **High** | **Latent Star** | ❌ **FAIL** (PIE target) |

**Interpretation:**
- **Brunson/Poole**: Correctly identified ✓ (Physics compliance working)
- **Gobert/DeRozan**: False positives due to PIE target rewarding utility (rebounding/defense) over scalability

## Implementation Details

### 1. Time-Shifted Ground Truth
- **Script**: `src/nba_data/scripts/generate_telescope_targets.py`
- **Logic**: Target is `MAX(Playoff_PIE)` over `t+1`, `t+2`, `t+3`.
- **Survivorship**: Implemented explicit imputation (0.05 PIE) for players who wash out, preventing survivorship bias.
- **Issue**: PIE is a "utility metric" that rewards rebounding/defense equally with creation.

### 2. Universal Projection Engine (Fixed)
- **Script**: `src/nba_data/scripts/project_player_avatars.py`
- **Logic**: Uses **percentile preservation** (not linear scaling) to prevent skill hallucination.
- **Fix**: Corrected `USG_PCT` scaling and implemented rank-preserving projection that maintains relative skill levels.

### 3. Telescope Model
- **Script**: `src/nba_data/scripts/train_telescope_model.py`
- **Type**: XGBoost Regressor.
- **Training Data**: Restricted to "Growth Cohort" (Age <= 26, 923 players).
- **Features**: 11 physics-based features (Creation Volume, Leverage Delta, etc.).

### 4. 2D Risk Matrix Synthesis
- **Script**: `src/nba_data/scripts/predict_2d_risk_matrix.py`
- **Output**: `results/risk_matrix_analysis.csv`
- **Method**: Cross-references Viability (1 - Liability Probability) with Potential (Predicted Future PIE).

## Next Steps (Highest Leverage)
1. **HELIO_INDEX Target Pivot**: Replace PIE target with `HELIO_INDEX = Usage × (Efficiency - Replacement) × Creation_Volume` to train a "Scalability Detector" instead of "Utility Detector."
2. **Expand Dataset**: Process additional seasons for larger training sample.
3. **Dashboard Integration**: Visualize 2D Risk Matrix in Streamlit app.

See `PHASE_4_IMPLEMENTATION_PLAN.md` for detailed HELIO_INDEX implementation steps.

