# Changelog

All notable changes to the NBA Playoff Resilience Engine will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **HELIO_LOAD_INDEX Target Generation**: Complete implementation of Telescope model target pipeline
  - Created `generate_helio_targets.py` script implementing 3-year lookahead window logic
  - Implemented `HELIO_LOAD_INDEX = (OFFENSIVE_LOAD^1.3) × EFFICIENCY_DELTA` with replacement level baseline
  - Generated `training_targets_helio.csv` with FUTURE_PEAK_HELIO targets for all regular season rows
  - **Key Discovery**: League average baseline created "Negative Inversion Trap"; replaced with replacement level (League Avg - 5.0)
- **Telescope Model v1**: Initial training on HELIO targets with physics-based features
  - R² = 0.11 baseline established with USG_PCT (21% importance) as strongest driver
  - Features: CREATION_VOLUME_RATIO, LEVERAGE_USG_DELTA, RS_PRESSURE_APPETITE, AGE
  - Validated that model correctly values high-usage stars above washouts
- **HELIO_LOAD_INDEX Target Formula**: Validated new target variable for Telescope model pivot
  - Implemented `HELIO_LOAD_INDEX = (OFFENSIVE_LOAD^1.3) × EFFICIENCY_DELTA` where `OFFENSIVE_LOAD = USG_PCT + (AST_PCT × 0.75)`
  - Created simulation scripts: `evaluate_helio_target.py` (original formula) and `evaluate_helio_load.py` (validated formula)
  - **Key Validation**: Nikola Jokić ranks #1, Rudy Gobert near zero - correctly identifies heliocentric engines
  - **PHASE_4_HELIO_IMPLEMENTATION_PLAN.md**: Complete implementation roadmap for target generation pipeline
- **DeRozan Problem SOLVED**: Physics-based playoff friction simulation implemented
  - Added PROJECTED_PLAYOFF_OUTPUT and friction coefficients (FRICTION_COEFF_ISO, FRICTION_COEFF_0_DRIBBLE)
  - Force-included physics-based features in RFE model despite statistical selection
  - Parallel processing (6 workers) for faster data collection
  - Centralized USG_PCT normalization to prevent unit scaling traps
- **Complete Data Pipeline Restoration**: Fixed critical SHOT_QUALITY_GENERATION_DELTA data gap
  - Collected raw shot quality data for all 10 seasons (2015-2025) using 6 parallel workers
  - Calculated SHOT_QUALITY_GENERATION_DELTA for all 5,312 player-seasons
  - Added historical star test cases (Harden, Wall, LeBron James 2015-16) to overall star prediction tests
- **Streamlit App Bug Fix**: Resolved duplicate element key preventing proper app loading
- **Project restructure**: Complete reorganization for developer experience
  - New modular `src/` structure (`data/`, `features/`, `model/`, `utils/`)
  - Clear entry points in `scripts/` directory
  - Consolidated documentation in `docs/`
  - Environment-specific configuration in `config/`
  - Comprehensive test organization in `tests/`

### Changed
- **Model Performance**: Major accuracy jump from 46.77% to 58.15% (+24% improvement) with physics-based features
- **PROJECTED_PLAYOFF_OUTPUT**: Now rank #2 (14.48% importance) in RFE model
- **Friction Coefficients**: FRICTION_COEFF_ISO (#4, 8.19% importance), FRICTION_COEFF_0_DRIBBLE (#5, 7.49% importance)
- **Test Suite Performance**: Latent Star Detection: 71.9% pass rate (23/32), Overall Star Prediction: 53.3% accuracy (18/34)
- **SHOT_QUALITY_GENERATION_DELTA**: Now rank #4 (5.9% importance) in RFE model for organic tank commander detection
- **Test Suite Coverage**: Expanded to 23 test cases with 81.8% accuracy on Franchise Cornerstone classification
- **Documentation consolidation**: Reduced from 35+ scattered files to 6 comprehensive docs
- **Model registry**: Organized models by lifecycle (production/staging/archive)
- **Data organization**: Clear separation of raw/interim/processed/external data

## [2.0.0] - 2025-01-01

### Added
- **2D Risk Matrix**: Primary evaluation framework separating Performance vs. Dependence
- **Hybrid evaluation**: 2D for modern cases, 1D compatibility maintained
- **Ground-truth data acquisition**: "0 Dribble" shooting data for all seasons
- **Project Phoenix**: Systematic elimination of proxies in critical signals
- **Universal Projection**: Features scale together using empirical distributions
- **Tiered gate execution**: Fatal flaws → Data quality → Contextual gates

### Changed
- **Test suite pass rate**: 52.5% → 87.5% (35/40 cases)
- **Model accuracy**: Improved temporal validation through better features
- **Jordan Poole classification**: Correctly identified as Luxury Component
- **Sample weighting**: Asymmetric loss for false positive penalty

### Fixed
- **Ground Truth Trap**: Model training no longer biased by outcome-based labels
- **Static Avatar Fallacy**: Features now project together, not independently
- **Low-Floor Illusion**: Absolute efficiency floors prevent false "King" predictions
- **Empty Calories Creator**: Volume exemption refined to require efficient creation

## [1.5.0] - 2024-08-15

### Added
- **Multi-signal tax system**: Compound penalties for system merchants
- **Volume exemption**: High creators (60%+ volume) exempt from certain penalties
- **Trust Fall experiment**: Model validation without hard gates
- **RFE optimization**: 10-feature model achieves same accuracy as 65 features

### Changed
- **Feature count**: Reduced from 65 to 10 (85% reduction, same accuracy)
- **Usage-aware features**: 5 of 10 features are usage-related (65.9% importance)
- **Pass rate improvement**: 43.8% → 75.0% with threshold adjustments

## [1.4.0] - 2024-06-01

### Added
- **Usage-aware conditional predictions**: Predict archetypes at any usage level
- **Latent star detection**: Identify high-skill players lacking opportunity
- **Flash Multiplier**: Elite efficiency on low volume → star-level projection
- **Playoff Translation Tax**: Penalize open shot reliance (system merchants)
- **Bag Check Gate**: Require self-created volume for primary initiators

### Changed
- **Model architecture**: Now predicts f(stress_vectors, usage)
- **Validation examples**: Brunson at 30% usage correctly predicts "Bulldozer"
- **Feature engineering**: Clock distinction in pressure vectors

## [1.3.0] - 2024-03-15

### Added
- **Five Stress Vectors**: Creation, Leverage, Pressure, Physicality, Plasticity
- **Abdication Tax**: LEVERAGE_USG_DELTA < -0.05 indicates passivity
- **Data completeness gates**: Require 67% of critical features
- **Minimum sample size gates**: Prevent noise from tiny samples
- **Negative signal gates**: Multiple red flags compound

### Changed
- **Resilience definition**: Efficiency × Volume (not efficiency alone)
- **Simmons Paradox resolution**: Passivity penalty correctly identifies collapse
- **Luka Paradox resolution**: Volume maintenance rewards carrying the load

## [1.2.0] - 2024-01-01

### Added
- **Dual-Grade Archetype System**: RQ (Resilience) × Dominance (Absolute Value)
- **Four archetypes**: King (Elite), Bulldozer (Efficient Volume), Sniper (Efficient Role), Victim (Collapse)
- **Historical validation**: 9-year dataset (2015-2024) confirms system accuracy
- **Mechanistic insights**: Explain *why* predictions work using basketball physics

### Changed
- **From single scalar to two dimensions**: Separated adaptability from absolute value
- **Validation approach**: Known historical cases instead of cross-validation only

## [1.1.0] - 2023-10-01

### Added
- **XGBoost implementation**: Replaced linear regression with tree-based model
- **Feature importance weighting**: No longer average away strongest signals
- **Temporal validation**: Train on past seasons, test on future seasons
- **Rate limiting**: Proper NBA API handling with exponential backoff

### Fixed
- **Data leakage**: Separated training and validation temporally
- **Feature scaling**: Proper normalization within reference classes

## [1.0.0] - 2023-07-01

### Added
- **Initial Plasticity Model**: Shot zone adaptation as resilience proxy
- **NBA Stats API integration**: Automated data collection
- **Linear regression baseline**: Initial predictive modeling
- **Basic validation**: Face validity testing on known cases

### Known Issues
- Luka Paradox: Efficiency-focused model missed volume maintenance
- Simmons Paradox: No penalty for passivity and abdication
- Ground Truth Trap: Training labels biased by outcomes

---

## Version Numbering

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes, architectural rewrites
- **MINOR**: New features, significant improvements
- **PATCH**: Bug fixes, minor improvements

## Release Frequency

- **Major releases**: When fundamental architecture changes
- **Minor releases**: When new capabilities are added (3-6 month cadence)
- **Patches**: As needed for critical fixes

## Validation Metrics

Each release includes validation against the 32-case test suite:

- **Pass Rate**: Percentage of cases with correct predictions
- **2D Cases**: Explicit Performance vs. Dependence expectations
- **1D Cases**: Legacy archetype compatibility
- **False Positives**: Incorrect "star" predictions (most costly)
- **False Negatives**: Missed latent stars (less costly)

## Contributing to Changelog

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security-related changes

All changes must be validated against the test suite before release.
