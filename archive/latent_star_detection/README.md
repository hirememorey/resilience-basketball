# Latent Star Detection Archive

**Status**: ⏸️ **Paused** - Focus shifted to usage-aware conditional prediction model

**Date Archived**: December 2025

## Contents

This directory contains documentation and results from the latent star detection work, which has been paused to focus on improving the core model's ability to answer both questions:

1. "How will this player perform in playoffs given their current role?"
2. "Who has the skills but hasn't been given opportunity?"

## Key Documents

- **`LATENT_STAR_REFINEMENT_PLAN.md`**: Complete Phase 2 implementation plan with consultant feedback
- **`BRUNSON_TEST_ANALYSIS.md`**: First principles analysis of why certain players were identified
- **`MAXEY_ANALYSIS.md`**: False negative case study revealing system weaknesses
- **`CONSULTANT_FIXES_IMPLEMENTED.md`**: Summary of consultant feedback implementation

## Results Files

- **`phase0_key_findings.md`**: Key insights from test case validation
- **`phase1_completion_summary.md`**: Data pipeline fix summary
- **`brunson_test_2020_21_report.md`**: Historical validation results
- **`latent_star_detection_report.md`**: Analysis report
- **`phase2_*.csv`**: Test case rankings and validation results
- **`brunson_test_2020_21.csv`**: Validation results

## Why This Was Paused

The latent star detection system revealed a fundamental limitation in the model: it predicts performance at the current usage level, not at different usage levels. This prevents it from answering the second question ("Who has the skills but hasn't been given opportunity?").

**The Solution**: Implement a usage-aware conditional prediction model that can predict performance at different usage levels. See `USAGE_AWARE_MODEL_PLAN.md` in the main directory for the implementation plan.

## Key Insights Preserved

The hard-won lessons from this work are preserved in `KEY_INSIGHTS.md` in the main directory. These include:

- Reference class principle (filter-first architecture)
- Proxy fallacy (no proxies, use confidence scores)
- Missing data = selection bias (fix root cause)
- Normalize within cohort (not entire league)
- Skills vs. performance distinction

## Future Work

Once the usage-aware model is implemented, latent star detection can be resumed using conditional predictions:

```python
# Predict archetype at higher usage level
predicted_archetype = model.predict_at_usage(stress_vectors, usage=25.0)
# If predicted "King" at 25% usage but current usage is 19.6%, they're a latent star
```

---

**Note**: This archive preserves the implementation details and analysis for future reference, but the focus has shifted to the foundational model improvement.
















