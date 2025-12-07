#!/bin/bash

# Create archive directory structure for scripts if it doesn't exist
mkdir -p archive/scripts/legacy_v1_linear
mkdir -p archive/scripts/legacy_v2_complex
mkdir -p archive/scripts/legacy_validation

echo "📦 Archiving Legacy V1 (Linear Regression) Scripts..."
mv src/nba_data/scripts/train_resilience_models.py archive/scripts/legacy_v1_linear/ 2>/dev/null
mv src/nba_data/scripts/calculate_resilience_scores.py archive/scripts/legacy_v1_linear/ 2>/dev/null

echo "📦 Archiving Legacy V2 (Complex 5-Pathway) Scripts..."
# Note: Some of these may already be in archive/complex_framework/
mv src/nba_data/scripts/calculate_friction.py archive/scripts/legacy_v2_complex/ 2>/dev/null
mv src/nba_data/scripts/calculate_crucible_baseline.py archive/scripts/legacy_v2_complex/ 2>/dev/null
mv src/nba_data/scripts/calculate_role_scalability.py archive/scripts/legacy_v2_complex/ 2>/dev/null
mv src/nba_data/scripts/calculate_primary_method_mastery.py archive/scripts/legacy_v2_complex/ 2>/dev/null
mv src/nba_data/scripts/calculate_longitudinal_evolution.py archive/scripts/legacy_v2_complex/ 2>/dev/null
mv src/nba_data/scripts/calculate_extended_resilience.py archive/scripts/legacy_v2_complex/ 2>/dev/null
mv src/nba_data/scripts/calculate_unified_resilience.py archive/scripts/legacy_v2_complex/ 2>/dev/null
mv src/nba_data/scripts/calculate_dominance_score.py archive/scripts/legacy_v2_complex/ 2>/dev/null
mv src/nba_data/scripts/proof_of_concept_archetypes.py archive/scripts/legacy_v2_complex/ 2>/dev/null

echo "📦 Archiving Legacy Validation & Analysis Scripts..."
mv src/nba_data/scripts/validate_face_validity.py archive/scripts/legacy_validation/ 2>/dev/null
mv src/nba_data/scripts/validate_resilience_prediction.py archive/scripts/legacy_validation/ 2>/dev/null
mv src/nba_data/scripts/phase1_baseline_validation.py archive/scripts/legacy_validation/ 2>/dev/null
mv src/nba_data/scripts/validate_measurement_assumptions.py archive/scripts/legacy_validation/ 2>/dev/null
mv src/nba_data/scripts/validate_problem_exists.py archive/scripts/legacy_validation/ 2>/dev/null
mv src/nba_data/scripts/validate_test_cases.py archive/scripts/legacy_validation/ 2>/dev/null
mv src/nba_data/scripts/test_phase2_validation.py archive/scripts/legacy_validation/ 2>/dev/null
mv src/nba_data/scripts/simple_external_test.py archive/scripts/legacy_validation/ 2>/dev/null
mv src/nba_data/scripts/analyze_shai_pattern.py archive/scripts/legacy_validation/ 2>/dev/null
mv src/nba_data/scripts/analyze_usage_ts_relationship.py archive/scripts/legacy_validation/ 2>/dev/null
mv src/nba_data/scripts/analyze_player_history.py archive/scripts/legacy_validation/ 2>/dev/null
mv src/nba_data/scripts/refine_composite_interpretation.py archive/scripts/legacy_validation/ 2>/dev/null
mv src/nba_data/scripts/calculate_composite_resilience.py archive/scripts/legacy_validation/ 2>/dev/null

echo "✅ Cleanup Complete. Active pipeline files remain in src/nba_data/scripts/."
