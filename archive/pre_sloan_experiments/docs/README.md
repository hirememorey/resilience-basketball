# NBA Playoff Resilience Engine

**Goal:** Identify players who consistently perform better than expected in the playoffs, and explain *why* using mechanistic insights.

**Status:** ✅ **FULLY OPERATIONAL SYSTEM** - Complete data pipeline restored with SHOT_QUALITY_GENERATION_DELTA calculated for all 5,312 players. Model accuracy 51.38% with organic tank commander detection. **Overall Star Prediction: 81.8% accuracy (18/22)**. Streamlit app fully functional.

---

## Quick Start

### 1. Set Up Your Environment
```bash
# One-command setup (creates venv, installs deps, gets data)
./scripts/setup.sh

# Or manually:
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Your First Prediction
```bash
# Predict archetype for a specific player
python scripts/predict.py --player "Jalen Brunson" --season "2022-23"

# Run full validation suite
python scripts/validate.py

# Debug model performance
python scripts/debug.py --player "Jordan Poole" --season "2021-22"
```

### 3. Understand the System
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - How the system works
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - How to contribute
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues

---

## What This System Does

The NBA Playoff Resilience Engine predicts which young players will become NBA stars by analyzing their **resilience under pressure** - the ability to maintain or increase production when defenses intensify.

### Core Innovation: 2D Risk Matrix
Traditional models predict "Will this player succeed?" Our system predicts **two dimensions**:

- **Performance**: What outcomes will they achieve?
- **Dependence**: Is their production portable or team-dependent?

This creates four risk categories:

| Category | Performance | Dependence | Example | Use Case |
|----------|-------------|------------|---------|----------|
| **Franchise Cornerstone** | High | Low | Nikola Jokić, Giannis Antetokounmpo | Max contract, build around |
| **Luxury Component** | High | High | Jordan Poole, Domantas Sabonis | Valuable in system, risky as #1 |
| **Depth Piece** | Low | Low | Role players with reliability | Dependable bench production |
| **Avoid** | Low | High | System merchants, empty calories | Avoid at all costs |

### Key Capabilities

1. **Latent Star Detection**: Identify young players with star-level skills but limited opportunity
2. **Usage Projection**: Predict performance at any usage level (20% → 30% usage scenarios)
3. **Mechanistic Explanations**: Explain *why* predictions work using basketball physics
4. **Temporal Validation**: Train on past seasons, test on future seasons (no data leakage)

---

## Current Model Performance

**Algorithm:** XGBoost Classifier (Multi-Class, 15 features)  
**Accuracy:** ~49% (RS-only features, temporal split, true predictive power)  
**Test Pass Rate:** **87.5%** (35/40 cases) - Major improvement with 2D framework  
**Key Achievement:** Solved "Ground Truth Paradox" with hybrid Performance vs. Dependence evaluation

### Top Features (by importance)
1. `USG_PCT` (40.2%) - Usage level
2. `SHOT_QUALITY_GENERATION_DELTA` (8.63%) - Quality of shots created
3. `TS_PCT_VS_USAGE_BAND_EXPECTATION` (8.6%) - Efficiency vs. expectation
4. `EFG_PCT_0_DRIBBLE` (7.6%) - Catch-and-shoot efficiency
5. `USG_PCT_X_EFG_ISO_WEIGHTED` (6.4%) - Usage × isolation efficiency

---

## Project Structure

```
resilience_basketball/
├── docs/                    # 📚 Documentation (you're here!)
├── scripts/                 # 🚀 Entry points for common workflows
├── src/                     # 🔧 Modular, importable code
│   ├── data/               # 📊 Data collection & storage
│   ├── features/           # 🔬 Feature engineering
│   ├── model/              # 🤖 Model training & prediction
│   └── utils/              # 🛠️ Shared utilities
├── data/                    # 📊 Raw & processed datasets
├── models/                  # 🤖 Model registry
├── results/                 # 📈 Analysis outputs
├── config/                  # ⚙️ Configuration files
└── tests/                   # ✅ Test suites
```

### Key Entry Points
- `scripts/setup.sh` - Environment setup
- `scripts/collect_data.sh` - Data ingestion pipeline
- `scripts/train_model.sh` - Model training
- `scripts/predict.py` - Make predictions
- `scripts/validate.py` - Run test suite
- `scripts/debug.py` - Diagnostics

---

## Theoretical Foundation

This system resolves the **Luka & Simmons Paradox**:

### The Problem
- **Luka Paradox**: Luka Dončić carried his team to the Finals but was flagged as "Fragile" because his efficiency dropped (54.7% → 44.7%), ignoring that he increased volume (+2.0 shots/game)
- **Simmons Paradox**: Ben Simmons appeared "Resilient" despite catastrophic collapse because he stopped shooting but maintained high FG% on easy shots

### The Solution: Resilience = Efficiency × Volume
Resilience requires **both** maintaining efficiency **and** absorbing responsibility. The system penalizes "passivity" (Abdication Tax) and rewards "carrying the load."

**Key Principle:** A player who takes fewer shots in playoffs than they did in regular season practice is failing, regardless of shooting percentage.

---

## Quick Validation Examples

```bash
# Test the Luka Paradox resolution
python scripts/predict.py --player "Luka Dončić" --season "2023-24"
# Expected: Bulldozer (high volume, some efficiency drop) ✅

# Test the Simmons Paradox resolution
python scripts/predict.py --player "Ben Simmons" --season "2020-21"
# Expected: Victim (passivity penalty) ✅

# Test Latent Star Detection
python scripts/predict.py --player "Tyrese Haliburton" --season "2021-22" --usage 0.30
# Expected: King projection at star usage ✅
```

---

## Getting Help

- **New to the project?** → Read [ARCHITECTURE.md](ARCHITECTURE.md)
- **Want to contribute?** → Read [DEVELOPMENT.md](DEVELOPMENT.md)
- **Having issues?** → Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **API Reference?** → See [API_REFERENCE.md](API_REFERENCE.md)

---

## Support & Contributing

This project values **scientific rigor and explainability** over raw accuracy. A model with mechanistic insights that explains *why* players succeed/fail is more valuable than a black-box model with higher accuracy.

**Contributing:** See [DEVELOPMENT.md](DEVELOPMENT.md) for coding standards and contribution guidelines.

**Issues:** Open an issue with the output of `python scripts/debug.py --diagnostic` for faster resolution.
