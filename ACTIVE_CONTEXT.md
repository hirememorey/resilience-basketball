# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 11, 2025
**Status**: 🔄 Stalled at 52.5% trust-fall after multiple iterations (brake, feature interactions, class weighting, data regeneration). "Fool's Gold" remains unsolved; next step likely requires a different modeling approach (beyond penalty tweaks).

---

## Project Goal

Identify players who consistently perform better than expected in the playoffs and explain *why* using mechanistic insights. The model predicts playoff archetypes (King, Bulldozer, Sniper, Victim) from regular season stress vectors with usage-aware conditional predictions.

---

## Current Phase: Plateau after Phoenix Iterations

**Model Status**: XGBoost classifier (15 features) with ground-truth data, floor/clutch interactions, single brake (clutch-floor), fixed performance cut (0.74–0.78). Recent attempts: stronger brake, usage-weighted TS expectation interaction, rescaled clutch-floor interaction, class weighting (Victim 1.5), deeper model. RFE 20-feature trial also tested. No pass-rate gain.

**Key Achievement**: Project Phoenix successfully established ground-truth pipeline and implemented context-aware features. RFE selected TS_PCT_VS_USAGE_BAND_EXPECTATION as top feature, validating "efficiency vs. expectation" as critical missing signal. Identified "Fool's Gold" problem where high-usage, low-efficiency players are over-predicted due to clutch metrics.

**Project Phoenix Achievements**:
- ✅ **Ground-Truth Audit**: NBA API provides reliable "0 Dribble" data for all seasons (2015-2025)
- ✅ **Phoenix Pipeline**: Robust fetch_zero_dribble_stats() function integrated into core feature engineering
- ✅ **Context-Aware Features**: SPECIALIST_EFFICIENCY_SCORE and VERSATILITY_THREAT_SCORE implemented
- ✅ **RFE Selection**: TS_PCT_VS_USAGE_BAND_EXPECTATION selected as 4th most important feature (8.6% importance)
- ✅ **Model Improvement**: Accuracy improved from 46.77% to 48.62% (+1.85 percentage points)
- 📊 **Trust Fall Performance**: 50.0% pass rate (20/40 cases) without gates

---

## Scoreboard (Current Metrics)

### Model Performance
- **Accuracy**: ~49% (latest 15-feature model; 20-feature RFE variant similar)
- **True Predictive Power**: RS-only features, temporal split

### Test Suite Performance (latent_star_cases, gates ON)
- **Overall Pass Rate**: `52.5%` (21/40) — unchanged across recent iterations
  - **True Positives**: `47.1%` (8/17)
  - **False Positives**: `40.0%` (2/5)
  - **True Negatives**: `58.8%` (10/17)
  - **System Players**: `100.0%` (1/1)

### Project Phoenix Impact
- **Ground-Truth Data**: "0 Dribble" shooting data confirmed available for all seasons
- **Features Selected by RFE**: TS_PCT_VS_USAGE_BAND_EXPECTATION (Rank #4, 8.6% importance)
- **Context-Aware Architecture**: Specialist/Versatility dyad implemented, RFE prioritized efficiency vs. expectation
- **Critical Finding**: "Fool's Gold" problem identified - high-usage, low-efficiency players over-predicted due to clutch metrics
- **Next Challenge**: Solve "Fool's Gold" problem to achieve 70%+ trust fall performance

---

## Next Developer: Start Here

**Current State**: Plateau at 52.5% trust-fall despite multiple iterations (brake strength up to 4.0; clutch-floor + usage×TS expectation interactions; rescaled clutch-floor feature; class weighting; deeper model; RFE 20-feature variant). Data pipelines refreshed (shot quality, shot charts, rim pressure, gate features, dependence scores recomputed). "Fool's Gold" persists.

**Key Attempts (all failed to lift pass rate):**
- Single brake tuning (floor gap 0.02, multipliers 2.5 → 4.0) and rescaled clutch-floor feature.
- Added USG_PCT_X_TS_PCT_VS_USAGE_BAND_EXPECTATION; rescaled CLUTCH_X_TS_FLOOR_GAP; usage-weighted TS gap monotone-negative.
- Class-weighting Victim (1.5x) + deeper XGB (200 trees, depth 5, lr 0.08).
- RFE 20-feature model: no improvement.
- Data regeneration: shot quality/clock, shot charts (lower concurrency), rim pressure, dependence, gate features; predictive_dataset rebuilt.

**Remaining Issues:**
- False positives remain (40% in suite); overall pass stuck at 52.5%.
- Penalty/weight tweaks and feature interactions no longer move metrics; likely need different modeling approach (e.g., alternate model family, calibrated stacking, or rethinking loss/targets).

**Where to Focus Next:**
- Consider a different architecture rather than further penalty tweaks.
- Revisit class-weight vs. sample-penalty strategy holistically (maybe simplify to class weights only, or new model).
- Use `diagnose_failures.py` on remaining FPs (Jordan Poole 21-22, Julius Randle 20-21) with fresh data to see dominant signals; check SHAP to ensure efficiency/floor signals surface.

**Artifacts:**
- Latest models: `models/resilience_xgb_rfe_phoenix.pkl` (15 features, brake 4.0, class weight Victim 1.5), `models/resilience_xgb_rfe_20.pkl` (20-feature RFE variant).
- Latest suite results: `results/latent_star_test_cases_report.md` (pass 52.5%).
