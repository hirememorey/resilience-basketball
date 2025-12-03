# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Current Status & Key Insight (V4.2 - Complete)**

The project has successfully developed a complete "Stylistic Stress Test" system to predict and explain playoff resilience.

- **`V4.2 Predictive Model`**: An XGBoost Classifier that achieves **59.4% accuracy** in predicting a player's Playoff Archetype (King, Bulldozer, Sniper, Victim) based on five Regular Season "Stress Vectors":
    1.  **Creation Vector**: Measures efficiency drop-off when forced to create own shot.
    2.  **Leverage Vector**: Measures how efficiency and usage scale in clutch situations.
    3.  **Pressure Vector (V4.2 Refined)**: Measures willingness to take tight shots with **Clock Distinction** (late-clock bailouts vs. early-clock bad shots).
    4.  **Physicality Vector**: **Rim Pressure Resilience** - maintains rim attack volume in playoffs.
    5.  **Plasticity Vector**: Spatial and temporal shot distribution changes.

- **`Complete Dataset`**: **10 seasons (2015-2024)** with 5,312 player-season records and full historical context data.
- **`Clock Data Coverage`**: **100% coverage** across all seasons (2015-16 through 2024-25) with optimized parallel collection.

## Next Developer Mission: Implement Phase 2 - Ranking Formula & Features

The predictive engine and component analysis are production-ready. Phase 0 (Problem Domain Understanding) and Phase 1 (Data Pipeline Fix) are complete. The current focus is Phase 2: implementing the ranking formula and features to better identify undervalued players.

### Current State

**✅ Phase 0 Complete (Problem Domain Understanding):**
- All 14 test cases validated (100% coverage)
- Key findings documented: USG% filter too strict, Leverage TS Delta is strongest signal
- See `results/phase0_key_findings.md` for complete analysis

**✅ Phase 1 Complete (Data Pipeline Fix):**
- USG_PCT: 100% coverage (5,312 / 5,312) - fetched directly from API
- AGE: 100% coverage (5,312 / 5,312) - fetched directly from API
- CREATION_BOOST: 100% coverage, correctly calculated
- No dependency on filtered files
- See `results/phase1_completion_summary.md` for details

**🎯 Phase 2 Ready (Ranking Formula & Features):**
- **⚠️ CRITICAL**: Read previous developer's learnings and consultant's Proxy Fallacy warning in `LATENT_STAR_REFINEMENT_PLAN.md`
- Validate ranking formula on test cases BEFORE building pipeline
- Understand data distribution (actual ranges, not theoretical)
- Implement Confidence Score system (addresses Proxy Fallacy)
- Implement Scalability Coefficient
- Implement ranking formula with piecewise normalization
- Update filter thresholds (raise USG% to 25%, test age < 26)
- Systematic threshold testing

### ⚠️ CRITICAL: Read This First

**Before implementing Phase 2, read `LATENT_STAR_REFINEMENT_PLAN.md`.**

The plan includes:
- Phase 0 findings summary (what we learned from test cases)
- Phase 1 completion summary (data pipeline fixes)
- Complete Phase 2 implementation plan with specific formulas and validation criteria
- Previous developer's critical insights (don't average away strongest signal)

**Key Principle**: Understand the problem before implementing the solution. Missing data often has a systematic cause (selection bias), not a technical one (NaN handling).

### How to Work on Latent Star Detection (Phase 2)

**✅ Phase 0 & 1 Complete**: Problem domain understanding and data pipeline fixes are done.

1.  **Read the Refinement Plan**:
    *   **`LATENT_STAR_REFINEMENT_PLAN.md`**: Complete implementation plan with Phase 0 findings and Phase 2 tasks
    *   **`results/phase0_key_findings.md`**: Key insights from test case validation
    *   **`results/phase1_completion_summary.md`**: Data pipeline fix summary
    *   **`BRUNSON_TEST_ANALYSIS.md`**: First principles analysis of why certain players were identified
    *   **`MAXEY_ANALYSIS.md`**: False negative case study revealing system weaknesses

2.  **Implement Phase 2 (Ranking Formula & Features)**:
    *   Implement Scalability Coefficient calculation
    *   Implement ranking formula (Leverage TS Delta weighted 3x + Scalability + CREATION_BOOST)
    *   Update filter thresholds (raise USG% to 25%, test age < 26)
    *   Implement Signal Confidence metric
    *   Systematic threshold testing

3.  **Key Files to Modify**:
    *   `src/nba_data/scripts/detect_latent_stars.py` - Implement ranking formula, Scalability Coefficient, Signal Confidence
    *   `src/nba_data/scripts/brunson_test.py` - Update validation criteria

4.  **Run the Analysis**:
    ```bash
    # Run latent star detection (after Phase 2 implementation)
    python src/nba_data/scripts/detect_latent_stars.py
    
    # Run Brunson Test for validation
    python src/nba_data/scripts/brunson_test.py --detection-season 2020-21 --subsequent-seasons 2021-22 2022-23 2023-24
    
    # Validate Phase 2 implementation
    python validate_test_cases.py  # Re-run to verify improvements
    ```

## Quick Start for New Developers

### 1. Understand the Vision & Current State
*   **`LUKA_SIMMONS_PARADOX.md`**: **CRITICAL.** Understands the core *descriptive* problem we solved.
*   **`IMPLEMENTATION_PLAN.md`**: The roadmap, now completed through Phase 8, with Phase 9 in progress.
*   **`LATENT_STAR_REFINEMENT_PLAN.md`**: **START HERE** - Complete implementation plan for latent star detection refinement with consultant feedback.
*   **`BRUNSON_TEST_ANALYSIS.md`**: First principles analysis of why certain players were identified.
*   **`MAXEY_ANALYSIS.md`**: False negative case study revealing system weaknesses.
*   **`CONSULTANT_FIXES_IMPLEMENTED.md`**: Summary of initial consultant feedback implementation (partial).

### 2. Set Up Environment
```bash
# Install dependencies
pip install pandas numpy scikit-learn scipy tenacity requests xgboost tqdm tabulate seaborn matplotlib joblib

# Create required directories
mkdir -p data/cache models results logs
```

### 3. Run the Full Pipeline
This generates the two key artifacts: the *labels* (Archetypes) and the *features* (Stress Vectors), then trains the model.

```bash
# 1. Generate Historical Archetypes (The Labels)
python src/nba_data/scripts/calculate_simple_resilience.py

# 2. Generate Predictive Features (The Stress Vectors)
python src/nba_data/scripts/evaluate_plasticity_potential.py
python src/nba_data/scripts/calculate_physicality_features.py # NEW V4

# 3. Generate Pressure Features
python src/nba_data/scripts/collect_shot_quality_aggregates.py --seasons 2015-16 2016-17 2017-18 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 2024-25
# 3a. Generate Pressure Features with Shot Clock (V4.2 - Required for full accuracy)
python src/nba_data/scripts/collect_shot_quality_with_clock.py --seasons 2015-16 2016-17 2017-18 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24 2024-25 --workers 8
python src/nba_data/scripts/calculate_shot_difficulty_features.py

# 4. Train the Predictive Model
python src/nba_data/scripts/train_predictive_model.py
```

**Key Outputs:**
*   `results/resilience_archetypes.csv`: The descriptive labels.
*   `results/predictive_dataset.csv`: The predictive features.
*   `results/pressure_features.csv`: The pressure vector features.
*   `models/resilience_xgb.pkl`: The trained XGBoost model.
*   `results/feature_importance.png`: Explains *why* the model works.

### 4. Run Component Analysis & Latent Star Detection

```bash
# Collect playoff PIE data (if not already collected)
python src/nba_data/scripts/collect_playoff_pie.py

# Run component analysis
python src/nba_data/scripts/component_analysis.py

# Run latent star detection
python src/nba_data/scripts/detect_latent_stars.py

# Run Brunson Test for historical validation
python src/nba_data/scripts/brunson_test.py --detection-season 2020-21 --subsequent-seasons 2021-22 2022-23 2023-24
```

**Component Analysis Outputs:**
*   `data/playoff_pie_data.csv`: Playoff PIE and advanced stats
*   `results/component_analysis_correlations.csv`: Full correlation matrix
*   `results/component_analysis_report.md`: Detailed analysis with actionable insights
*   `results/component_analysis_heatmap.png`: Correlation visualizations

**Latent Star Detection Outputs:**
*   `results/latent_stars.csv`: Current latent star candidates
*   `results/latent_star_detection_report.md`: Analysis report
*   `results/brunson_test_2020_21.csv`: Historical validation results
*   `results/brunson_test_2020_21_report.md`: Validation report

---

## The "Sloan Path" (Phase 6)

We have achieved the core goal of building a predictive model. The next phase is to refine it and prepare the findings for publication.

**Core Finding Validated:** Playoff resilience is predicted by a player's ability to **create their own offense**, **absorb responsibility in the clutch**, and **force the issue** (Pressure Appetite).

**Current Status:** Model accuracy is **59.4%** with full clock data coverage. The model successfully predicts playoff archetypes using mechanistic stress vectors.

See **`IMPLEMENTATION_PLAN.md`** for the detailed roadmap.

---

## Project Structure

```
├── LUKA_SIMMONS_PARADOX.md         # The Theoretical Foundation
├── IMPLEMENTATION_PLAN.md          # The Roadmap
├── results/
│   ├── predictive_model_report.md  # Performance of our V4.2 Predictive Model
│   ├── resilience_archetypes.csv   # The Labels
│   ├── predictive_dataset.csv      # The Features
│   ├── pressure_features.csv       # The Pressure Features
│   ├── component_analysis_correlations.csv  # Stress Vector → Outcome Correlations
│   ├── component_analysis_report.md  # Component Analysis Report
│   ├── latent_stars.csv            # Latent Star Candidates
│   └── latent_star_detection_report.md  # Latent Star Analysis
├── data/
│   └── playoff_pie_data.csv        # Playoff PIE & Advanced Stats
├── src/
│   └── nba_data/scripts/
│       ├── calculate_simple_resilience.py      # Descriptive Engine (Generates Labels)
│       ├── evaluate_plasticity_potential.py  # Feature Engine (Generates Features)
│       ├── collect_shot_quality_aggregates.py # Data Collection (Pressure Vector)
│       ├── calculate_shot_difficulty_features.py # Feature Engine (Pressure Vector)
│       ├── train_predictive_model.py         # Predictive Engine (Trains Model)
│       ├── collect_playoff_pie.py            # Collect Playoff PIE Data
│       ├── component_analysis.py              # Component Analysis (Stress Vectors → Outcomes)
│       ├── detect_latent_stars.py            # Latent Star Detection (Sleeping Giants)
│       └── brunson_test.py                   # Historical Validation Framework
├── models/
│   └── resilience_xgb.pkl          # The Trained Model
```

---

## Key Principles

1.  **First Principles Thinking:** Don't just measure *what* happened. Isolate the *stylistic shifts* that explain *why*.
2.  **Resilience = Efficiency × Volume:** The "Abdication Tax" is real. Passivity is failure.
3.  **Self-Creation is King:** The strongest predictor of playoff success is the ability to generate your own offense.
4.  **Dominance is Rigid:** Some players (Shaq/Giannis) are resilient not because they adapt, but because they impose their will. We measure this as "Pressure Appetite."

---

## Support
*   **Technical questions:** Review `src/nba_data/api/nba_stats_client.py` to see how we handle rate limits.
*   **Conceptual questions:** Review `LUKA_SIMMONS_PARADOX.md`.
