# Troubleshooting Guide

Common issues and their solutions when working with the NBA Playoff Resilience Engine.

## Quick Diagnostic

Run this first when you encounter any issue:

```bash
# Get system diagnostic information
python scripts/debug.py --diagnostic

# Check if basic prediction works
python scripts/predict.py --player "Luka Dončić" --season "2023-24"

# Run validation suite
python scripts/validate.py
```

## Data Collection Issues

### API Rate Limiting
**Symptoms:** Requests fail with 429 errors, timeouts, or "Too Many Requests"

**Solutions:**
```bash
# Check current API status
python scripts/debug.py --api-status

# Run data collection with reduced concurrency
./scripts/collect_data.sh --workers 2

# Wait and retry (NBA API resets every 60 seconds)
sleep 60
python scripts/collect_data.sh
```

**Prevention:**
- Use default worker count (8) for normal operation
- Reduce to 2-4 workers during peak hours
- Built-in exponential backoff handles transient issues

### Missing Data
**Symptoms:** Features show NaN values, incomplete datasets

**Root Causes & Solutions:**

1. **Player not in dataset:**
   ```bash
   # Check if player exists
   python scripts/debug.py --player "Player Name" --season "2023-24"
   ```

2. **API data gaps:**
   - NBA API occasionally missing recent games
   - Solution: Wait 24-48 hours, re-run collection

3. **Season not available:**
   - Data only goes back to 2015-16
   - Some seasons have incomplete playoff data

### Data Quality Issues
**Symptoms:** Unreasonable values (eFG% > 1.0, negative percentages)

**Solutions:**
```bash
# Validate data integrity
python scripts/debug.py --data-integrity

# Re-collect specific problematic data
python scripts/collect_data.sh --season "2023-24" --overwrite
```

## Model Issues

### Model Not Found
**Symptoms:** "Model file not found" errors

**Solutions:**
```bash
# Check model registry
ls -la models/
ls -la models/production/

# Retrain model if missing
./scripts/train_model.sh

# Check model metadata
python scripts/debug.py --model-info
```

### Poor Model Performance
**Symptoms:** Low accuracy, unexpected predictions

**Diagnostic Steps:**
```bash
# Run full validation suite
python scripts/validate.py

# Check feature importance
python scripts/debug.py --feature-importance

# Analyze specific player
python scripts/debug.py --player "Jordan Poole" --season "2021-22" --detailed
```

**Common Causes:**
- **Data leakage:** Model trained on future data
- **Feature drift:** Training data distribution changed
- **Overfitting:** Too many features for available data

### Memory Issues
**Symptoms:** Out of memory errors during training

**Solutions:**
- Reduce XGBoost tree depth: `max_depth: 4` in config
- Decrease training data size
- Use smaller batch sizes for feature engineering
- Close other memory-intensive applications

## Prediction Issues

### Unexpected Archetype Predictions
**Symptoms:** Player predicted as different archetype than expected

**Debug Steps:**
```bash
# Get detailed prediction breakdown
python scripts/debug.py --player "Player Name" --season "2023-24" --detailed

# Check stress vector values
python scripts/debug.py --player "Player Name" --season "2023-24" --features

# Compare to similar players
python scripts/debug.py --player "Player Name" --season "2023-24" --similar
```

**Common Causes:**
- **Usage level:** Predictions change dramatically with usage
- **Missing data:** Critical features (leverage, creation) missing
- **Context dependence:** Player benefits from specific system

### Confidence Scores Too Low
**Symptoms:** All predictions have <30% confidence

**Causes:**
- Missing critical features (leverage data most important)
- Insufficient sample size (<50 possessions)
- Data quality issues

## Environment Issues

### Import Errors
**Symptoms:** `ModuleNotFoundError`, `ImportError`

**Solutions:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Path Issues
**Symptoms:** File not found errors for data/models/results

**Solutions:**
```bash
# Check directory structure
ls -la

# Run from project root
cd /path/to/resilience_basketball
python scripts/predict.py ...

# Fix relative imports if running scripts directly
PYTHONPATH=/path/to/resilience_basketball python scripts/predict.py
```

## Validation Issues

### Test Suite Failures
**Symptoms:** `python scripts/validate.py` shows failing tests

**Diagnostic:**
```bash
# Get detailed failure report
python scripts/debug.py --validation-report

# Focus on specific failing case
python scripts/debug.py --player "Failing Player" --season "2023-24" --validation
```

**Common Causes:**
- Model changes broke existing expectations
- Data collection issues affected feature values
- Configuration changes altered thresholds

### Performance Regression
**Symptoms:** Test pass rate decreased after changes

**Investigation:**
```bash
# Compare before/after
python scripts/debug.py --performance-comparison

# Check what changed
git log --oneline -10
git diff HEAD~1
```

## Development Issues

### Code Changes Not Taking Effect
**Symptoms:** Modified code doesn't change behavior

**Solutions:**
- **Python cache:** Remove `__pycache__/` directories
- **Jupyter cache:** Restart kernel if using notebooks
- **Model cache:** Retrain model after feature changes
- **Import cache:** Restart Python interpreter

### IDE Issues
**Symptoms:** Linting errors, import resolution failures

**Solutions:**
```bash
# Update Python path in IDE settings
# Project root: /path/to/resilience_basketball

# Install development dependencies
pip install -r requirements-dev.txt  # if exists

# Configure IDE for project structure
# - Source roots: src/
# - Test roots: tests/
```

## Performance Optimization

### Slow Data Collection
**Symptoms:** Data collection takes >30 minutes

**Solutions:**
```bash
# Use more workers (if API allows)
./scripts/collect_data.sh --workers 12

# Collect only recent seasons
./scripts/collect_data.sh --seasons "2022-23 2023-24"

# Use cached data when possible
./scripts/collect_data.sh --use-cache
```

### Slow Model Training
**Symptoms:** Training takes >10 minutes

**Solutions:**
- Reduce XGBoost parameters in config
- Use fewer features (RFE model is faster)
- Train on subset of data for experimentation
- Use GPU if available

## Advanced Diagnostics

### Deep Model Analysis
```bash
# Feature importance and correlations
python scripts/debug.py --model-analysis

# SHAP values for specific prediction
python scripts/debug.py --player "Player" --season "2023-24" --shap

# Cross-validation results
python scripts/debug.py --cv-analysis
```

### Data Pipeline Audit
```bash
# Check data completeness
python scripts/debug.py --data-completeness

# Validate feature distributions
python scripts/debug.py --feature-distributions

# Check for data drift
python scripts/debug.py --data-drift
```

### System Health Check
```bash
# Full system diagnostic
python scripts/debug.py --full-diagnostic

# Performance benchmark
python scripts/debug.py --benchmark

# Dependency check
python scripts/debug.py --dependencies
```

## Getting Help

If these solutions don't work:

1. **Check recent changes:** `git log --oneline -5`
2. **Run full diagnostic:** `python scripts/debug.py --full-diagnostic`
3. **Check the docs:** `cat docs/ARCHITECTURE.md`
4. **Open an issue:** Include the full diagnostic output

## Prevention Best Practices

- **Run tests before committing:** `python scripts/validate.py`
- **Check diagnostics regularly:** `python scripts/debug.py --diagnostic`
- **Monitor performance:** Keep baseline metrics in version control
- **Document changes:** Update docs when behavior changes
- **Use version control:** Branch for experimental changes

Remember: Most issues stem from **data quality** or **environment setup**. Start with diagnostics, not code changes.
