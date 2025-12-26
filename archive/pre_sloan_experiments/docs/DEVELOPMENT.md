# Development Guide

This guide explains how to contribute to the NBA Playoff Resilience Engine.

## Development Philosophy

**First Principles Thinking:** Reason from fundamental basketball physics, not patterns. A 46.77% accuracy model with mechanistic insights is more valuable than a 70% black box.

**Scientific Rigor:** Use temporal splits, no data leakage, validate on known cases. Document failures and learnings.

## Quick Start for Contributors

```bash
# 1. Set up environment
./scripts/setup.sh

# 2. Run tests to ensure everything works
python scripts/validate.py

# 3. Make your changes
# 4. Run tests again
python scripts/validate.py

# 5. Debug any issues
python scripts/debug.py --diagnostic
```

## Project Structure

```
resilience_basketball/
├── docs/                    # 📚 Documentation (contribute here first!)
├── scripts/                 # 🚀 Entry points (add new workflows here)
├── src/                     # 🔧 Core code (modular packages)
│   ├── data/               # 📊 Data layer
│   ├── features/           # 🔬 Feature engineering
│   ├── model/              # 🤖 Model layer
│   └── utils/              # 🛠️ Shared utilities
├── tests/                   # ✅ Test suites (add tests here)
├── config/                  # ⚙️ Configuration
├── data/                    # 📊 Datasets
├── models/                  # 🤖 Model registry
└── results/                 # 📈 Outputs
```

## Development Workflow

### 1. Choose Your Task
- **Bug Fix:** Start with reproduction case
- **New Feature:** Write test case first
- **Model Improvement:** Run baseline validation first

### 2. Understand the Codebase
```bash
# Read the key docs first
cat docs/ARCHITECTURE.md
cat docs/README.md

# Run a diagnostic to see system state
python scripts/debug.py --diagnostic
```

### 3. Make Changes
- **Follow the boy'scout rule:** Leave code better than you found it
- **Add tests:** Every feature needs validation
- **Update docs:** If behavior changes, docs must change

### 4. Validate Changes
```bash
# Run all tests
python scripts/validate.py

# Check specific functionality
python scripts/predict.py --player "Test Player" --season "2023-24"

# Debug issues
python scripts/debug.py --player "Problem Player" --season "2023-24"
```

## Coding Standards

### Python Style
```python
# ✅ Good: Descriptive names, clear structure
def calculate_resilience_quotient(playoff_stats, regular_season_stats):
    """Calculate RQ using first principles: Efficiency × Volume."""
    efficiency_ratio = playoff_stats['efg_pct'] / regular_season_stats['efg_pct']
    volume_ratio = playoff_stats['usg_pct'] / regular_season_stats['usg_pct']
    return efficiency_ratio * volume_ratio

# ❌ Bad: Magic numbers, unclear intent
def calc_rq(po, rs):
    return (po['efg'] / rs['efg']) * (po['usg'] / rs['usg'])
```

### Naming Conventions
- **Functions:** `verb_noun()` (calculate_resilience, predict_archetype)
- **Classes:** `NounClass` (ConditionalArchetypePredictor)
- **Files:** `snake_case.py` (resilience_calculator.py)
- **Constants:** `UPPER_CASE` (MAX_USAGE_THRESHOLD = 0.35)

### Documentation Standards
```python
def predict_archetype(player_data, usage_level=None, confidence_threshold=0.5):
    """
    Predict playoff archetype for a player.

    Uses XGBoost model to predict which of 4 archetypes (King, Bulldozer,
    Sniper, Victim) a player will exhibit in playoffs.

    Args:
        player_data (dict): Player season data with stress vectors
        usage_level (float, optional): Usage % to predict at. If None, uses current usage
        confidence_threshold (float): Minimum confidence to return prediction

    Returns:
        ArchetypePrediction: Named tuple with archetype, confidence, and features

    Raises:
        ValueError: If required features missing
        ModelLoadError: If model files not found

    Example:
        >>> result = predict_archetype(player_data, usage_level=0.25)
        >>> print(f"{result.archetype} ({result.confidence:.1%})")
        King (87.3%)
    """
```

## Testing Strategy

### Test Types
- **Unit Tests** (`tests/unit/`): Test individual functions
- **Integration Tests** (`tests/integration/`): Test data pipelines
- **Validation Tests** (`tests/validation/`): Test business logic against known cases

### Writing Tests
```python
# tests/unit/test_features.py
import pytest
from src.features.resilience import calculate_resilience_quotient

def test_calculate_resilience_quotient():
    """Test RQ calculation with known values."""
    playoff_stats = {'efg_pct': 0.500, 'usg_pct': 0.280}
    rs_stats = {'efg_pct': 0.550, 'usg_pct': 0.250}

    rq = calculate_resilience_quotient(playoff_stats, rs_stats)

    # Expected: (0.500/0.550) * (0.280/0.250) = 0.909 * 1.12 = 1.018
    assert abs(rq - 1.018) < 0.001

def test_rq_with_passivity_penalty():
    """Test that passivity reduces RQ."""
    playoff_stats = {'efg_pct': 0.500, 'usg_pct': 0.200}  # Usage dropped
    rs_stats = {'efg_pct': 0.550, 'usg_pct': 0.250}

    rq = calculate_resilience_quotient(playoff_stats, rs_stats)

    # Should be < 1.0 due to volume decrease (Abdication Tax)
    assert rq < 1.0
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/unit/test_features.py

# Run with coverage
python -m pytest --cov=src --cov-report=html tests/
```

## Feature Development Process

### 1. Define the Problem
Start with a specific question:
- "Why does the model misclassify X player?"
- "How can we better measure Y concept?"
- "What missing signal would improve Z prediction?"

### 2. Research First Principles
Ground your solution in basketball physics:
- **Creation:** Can they generate their own shot?
- **Leverage:** Do they scale up in pressure?
- **Physicality:** Can they attack the rim?
- **Adaptation:** Do they adjust to defensive schemes?

### 3. Implement Incrementally
```python
# 1. Add the feature calculation
def calculate_new_feature(player_data):
    """Calculate new feature based on first principles."""
    # Implementation here

# 2. Add tests for the feature
def test_calculate_new_feature():
    # Test cases here

# 3. Integrate into pipeline
# Update feature engineering scripts

# 4. Retrain model
# Run scripts/train_model.sh

# 5. Validate improvement
# Run scripts/validate.py
```

### 4. Validate Against Known Cases
Every feature must be tested against historical examples:
- **Luka Dončić (2023-24):** Should be Bulldozer (volume carrier)
- **Ben Simmons (2020-21):** Should be Victim (passivity)
- **Jordan Poole (2021-22):** Should be Luxury Component (system dependent)

## Common Pitfalls to Avoid

### ❌ Don't: Use Proxies
```python
# Wrong: Use ISO EFG as proxy for clutch performance
leverage_ts_delta = df['efg_iso_weighted']  # Correlation = 0.0047
```
```python
# Right: Flag missing data with confidence
signal_confidence = 0.3 if leverage_ts_delta.isna() else 1.0
```

### ❌ Don't: Average Away Strong Signals
```python
# Wrong: Equal weighting dilutes strong predictors
composite = (creation + leverage + pressure + physicality + plasticity) / 5
```
```python
# Right: Use model feature importance weights
composite = (
    leverage * 0.092 +  # Strongest signal
    creation * 0.062 +
    # ... other features with validated weights
)
```

### ❌ Don't: Build Without Validation
```python
# Wrong: Build full pipeline, then test
def build_complex_feature():
    # 200 lines of code
    results = run_pipeline()
    if results['accuracy'] < 0.5:
        # Oops, start over
```
```python
# Right: Test formulas on known cases first
def test_feature_formula():
    test_cases = load_known_cases()
    for case in test_cases:
        score = calculate_feature(case)
        assert score_matches_expected(score, case)
    # Formula validated, now build pipeline
```

## Performance Guidelines

### Code Performance
- **Data Processing:** Use vectorized pandas operations
- **API Calls:** Respect rate limits, use exponential backoff
- **Memory:** Process data in chunks for large datasets
- **Caching:** Cache expensive computations

### Model Performance
- **Accuracy Target:** 45-50% (temporal validation, true predictive power)
- **Feature Count:** Keep under 20 (Pareto principle)
- **Training Time:** Under 10 minutes
- **Inference Time:** Under 1 second

## Deployment Checklist

Before submitting a PR:

- [ ] **Tests Pass:** `python scripts/validate.py`
- [ ] **Code Style:** Follows PEP 8, descriptive names
- [ ] **Documentation:** Updated docs/README.md and relevant docs
- [ ] **Type Hints:** Added where helpful
- [ ] **Error Handling:** Graceful failure with clear messages
- [ ] **Performance:** No significant regression
- [ ] **Security:** No secrets committed

## Getting Help

- **Conceptual Questions:** Read `docs/ARCHITECTURE.md`
- **Code Issues:** Run `python scripts/debug.py --diagnostic`
- **API Problems:** Check `src/data/client.py` rate limiting
- **Model Issues:** Run `python scripts/debug.py --model-analysis`

Remember: This project values **mechanistic insights** over raw accuracy. Explain *why* your changes work, not just that they improve metrics.
