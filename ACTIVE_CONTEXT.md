# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 10, 2025  
**Status**: False Positive Reduction Complete (80% Pass Rate) | "Two Doors to Stardom" architecture defined for next phase.

---

## Project Goal

Identify players who consistently perform better than expected in the playoffs and explain *why* using mechanistic insights. The model predicts playoff archetypes (King, Bulldozer, Sniper, Victim) from regular season stress vectors with usage-aware conditional predictions.

---

## Current Phase: False Positive Hardening & Architectural Refinement

**Model Status**: RFE-optimized XGBoost Classifier with 10 core features, continuous gradients, and aggressive sample weighting (`13x` for high-usage, inefficient victims). Feature engineering now includes a calibrated Quality Floor and quadratically-scaled Inefficiency Score.

**Key Achievement**: Model has been successfully hardened against False Positives. The test suite pass rate for this category has improved from `20%` to `80%`, correctly identifying "Fool's Gold" players like D'Angelo Russell and Jordan Poole. This was achieved through a data-driven, incremental process of auditing failure modes and implementing targeted fixes.

**The New Challenge**: The aggressive penalties required to filter false positives have inadvertently lowered the True Positive pass rate from `100%` to `58.8%`. The next phase will focus on re-capturing these true stars without re-introducing the false positive vulnerability.

---

## Scoreboard (Current Metrics)

### Model Performance
- **Accuracy**: `48.92%` (RFE model, 10 features, `13x` sample weighting, retrained Dec 10, 2025)
- **True Predictive Power**: RS-only features, temporal split (2015-2021 train, 2022-2024 test)

### Test Suite Performance (40 cases)
- **Overall Pass Rate (With Gates)**: `70.0%` (28/40)
  - **True Positives**: `58.8%` (10/17) ⚠️ - **REGRESSION, PRIMARY TARGET FOR NEXT PHASE.**
  - **False Positives**: `80.0%` (4/5) ✅ - **SUCCESS, PRIMARY GOAL OF PREVIOUS PHASE MET.**
  - **True Negatives**: `76.5%` (13/17) ✅ - Stable and effective.

---

## Next Developer: Start Here

**The Problem**: We have two competing goals: correctly identify true stars (high TP rate) and correctly reject non-stars (high FP pass rate). Our recent work to improve FP detection has made our filter too strict, causing us to miss some true stars.

**The Solution - "Two Doors to Stardom"**: From first principles, we've recognized that there is more than one valid "path" to NBA stardom. A single, universal filter is too blunt an instrument. The next developer will implement a new architecture that allows for parallel validation paths.

**Key Documents to Read**:
1.  **`docs/TWO_DOORS_TO_STARDOM.md`**: **START HERE**. This is the full design document for the next phase. It outlines the first principles, the proposed architecture ("Polished Diamond" vs. "Uncut Gem" paths), and a detailed implementation plan.
2.  **`docs/FEEDBACK_EVALUATION_FIRST_PRINCIPLES.md`**: This document provides the context for the most recent set of changes, including the audit that led to the successful False Positive reduction.
3.  **`KEY_INSIGHTS.md`**: Review the newly added **Insight #51: The "Two Doors to Stardom" Principle**.
4.  **`ACTIVE_CONTEXT.md`**: This file.

**Your Task**: Implement the "Two Doors to Stardom" model as outlined in the design document. Your goal is to raise the True Positive pass rate back above 80% while keeping the False Positive pass rate at its current low level.
