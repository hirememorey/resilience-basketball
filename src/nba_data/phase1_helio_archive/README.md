# Phase 1 Archive: HELIO Potential Model

**Archived**: December 27, 2025

## What This Contains

This directory contains the original approach to latent star detection, which attempted to predict `FUTURE_PEAK_HELIO` (future playoff PIE) using XGBoost regression.

### Files

| File | Purpose |
|------|---------|
| `train_telescope_model.py` | Trained XGBoost regressor on projected avatars |
| `validate_telescope_resilience.py` | Validation against 35 test cases |
| `train_crucible_model.py` | Earlier version of the training pipeline |
| `train_rfe_model.py` | Recursive Feature Elimination model |
| `detect_latent_stars.py` | v1 detection logic |
| `detect_latent_stars_v2.py` | v2 detection logic |

## Why It Was Archived

### The Fundamental Problem

The approach predicted **outcomes** (playoff PIE), not **process** (creation independence).

This led to:
1. **Ground Truth Trap**: Ben Simmons had decent playoff PIE pre-2021, so the model learned he was "good"
2. **Context Contamination**: Players who looked good due to teammates/system were labeled as stars
3. **Wrong Question**: "How good will they be?" instead of "Can they create when schemed?"

### Key Learnings

1. **Features were valuable**: `clutch_usg_absolute`, `creation_volume_ratio`, `abdication_interaction` all had signal
2. **Target was wrong**: `FUTURE_PEAK_HELIO` rewarded converters who got lucky with context
3. **Abdication penalty helped but was a patch**: We could catch Simmons by penalizing his target, but this was fixing symptoms, not causes

### Final Validation Results

- **Pass Rate**: 60% (21/35)
- **Simmons**: Finally caught all 3 seasons after abdication penalty
- **But**: Required manual target adjustment, which is a "patch" not a "learn"

## The Pivot

Phase 2 shifts from:
- **Regression** (predict future PIE) → **Classification** (predict archetype)
- **Outcomes** (what happened) → **Process** (can they create?)
- **HELIO Index** → **Creation Independence Index**

See `/src/nba_data/phase2_creation_independence/` for the new approach.

## Data Assets Preserved

The data collection scripts remain active in `/src/nba_data/scripts/`. These are still valuable:
- Playtype data
- Tracking data  
- Shot quality
- Clutch splits
- Defensive context

The raw features we engineered (`evaluate_plasticity_potential.py`) are also preserved.

