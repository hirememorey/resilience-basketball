# Recommended File Structure

Date: December 6, 2025

Philosophy: Organize by function (Ingest -> Transform -> Train -> Predict -> Validate).

## Active Pipeline Structure

The project should eventually migrate to this structure. Currently, most scripts reside in `src/nba_data/scripts/`.

```
project_root/
├── archive/                      # Deprecated frameworks (Linear Reg, Complex 5-Pathway)
├── data/                         # Raw CSVs, SQLite DB (nba_stats.db)
├── models/                       # Serialized models (.pkl) and encoders
├── results/                      # Analysis outputs, CSVs, reports
├── logs/                         # Execution logs
│
├── scripts/                      # Top-level Entry Points
│   ├── run_pipeline.py           # Orchestrator
│   ├── run_predictions.py        # Run inference (Expanded dataset)
│   ├── run_validation.py         # Run test suites
│   └── update_data.py            # Trigger data collection
│
├── src/
│   └── nba_data/
│       ├── api/                  # External Data Interface
│       │   ├── nba_stats_client.py
│       │   └── ...
│       │
│       ├── db/                   # Database Interface
│       │   └── schema.py
│       │
│       ├── ingestion/            # Data Collection (Raw -> DB/CSV)
│       │   ├── collect_regular_season_stats.py
│       │   ├── collect_playoff_logs.py
│       │   ├── collect_shot_charts.py
│       │   ├── collect_shot_quality_aggregates.py
│       │   ├── collect_shot_quality_with_clock.py
│       │   └── collect_defensive_context.py
│       │
│       ├── features/             # Feature Engineering (Raw -> Stress Vectors)
│       │   ├── calculate_simple_resilience.py      # Target Generation (Labels)
│       │   ├── evaluate_plasticity_potential.py    # Creation/Leverage/Context Vectors
│       │   ├── calculate_rim_pressure.py           # Physicality Vector
│       │   ├── calculate_shot_difficulty_features.py # Pressure Vector
│       │   ├── calculate_dependence_score.py       # Dependence Score (2D Y-Axis)
│       │   ├── generate_trajectory_features.py     # Trajectory/Priors
│       │   └── generate_gate_features.py           # Gates (Soft Features)
│       │
│       ├── training/             # Model Training
│       │   ├── train_rfe_model.py                  # Primary (10 features)
│       │   ├── train_predictive_model.py           # Full model (Fallback)
│       │   └── rfe_feature_selection.py            # Feature Selection Logic
│       │
│       ├── inference/            # Prediction Logic
│       │   ├── predict_conditional_archetype.py    # Core Prediction Engine
│       │   └── detect_latent_stars_v2.py           # Latent Star Detection Logic
│       │
│       ├── validation/           # Test Suites & Quality Checks
│       │   ├── test_latent_star_cases.py           # Critical Case Studies
│       │   ├── test_2d_risk_matrix.py              # Risk Matrix Validation
│       │   └── analyze_model_misses.py             # Diagnostic Tools
│       │
│       └── analysis/             # Insights & Correlation
│           └── component_analysis.py               # Stress Vector Correlation
```

## Legacy/Obsolete Files (To Archive)

The following files represent previous iterations and should be moved to `archive/`:

**Linear Regression Model (V1):** `train_resilience_models.py`, `calculate_resilience_scores.py`

**Complex Framework (5-Pathway):** `calculate_friction.py`, `calculate_crucible_baseline.py`, `calculate_role_scalability.py`, `calculate_primary_method_mastery.py`, `calculate_longitudinal_evolution.py`, `calculate_extended_resilience.py`, `calculate_unified_resilience.py`

**Old Validation/Analysis:** `validate_face_validity.py`, `validate_resilience_prediction.py`, `phase1_baseline_validation.py`, `simple_external_test.py`, `validate_measurement_assumptions.py`, `validate_problem_exists.py`, `analyze_shai_pattern.py`
