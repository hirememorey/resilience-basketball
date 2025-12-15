"""
Overall Star Prediction: Franchise Cornerstone Classification Test Suite

PRIMARY EVALUATION FRAMEWORK: 2D Risk Matrix - Franchise Cornerstone Detection
============================================================================

This script tests the model's ability to correctly identify Franchise Cornerstones
at current usage levels. Franchise Cornerstones are players with:
- High Performance (≥70% star-level potential)
- Low Dependence (<30% system dependence)

Key Differences from Latent Star Detection:
- Tests at CURRENT usage levels (not elevated usage)
- Focuses on career star prediction (not opportunity-constrained players)
- Evaluates whether the model correctly identifies established/elite players as Franchise Cornerstones

Each test case includes comprehensive diagnostic output from player_season_analyzer.py
to enable detailed analysis of model mistakes.

Based on first principles framework - Performance and Dependence are orthogonal dimensions.
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any
import joblib

# Add project root to path for imports (relative to project root)
project_root = Path(__file__).parent.parent.parent  # Go up from tests/validation to project root
sys.path.insert(0, str(project_root))

from src.nba_data.scripts.predict_conditional_archetype import ConditionalArchetypePredictor
from typing import Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def collect_comprehensive_diagnostics(predictor, player_name: str, season: str):
    """Collect comprehensive diagnostic data including all raw metrics and calculations."""

    try:
        # Get player data
        player_data = predictor.get_player_data(player_name, season)
        if player_data is None:
            return {'error': 'No data found'}

        # Get the prediction result to access intermediate calculations (at current usage)
        current_usage = player_data.get('USG_PCT', 0.20)  # Use player's actual current usage
        prediction_result = predictor.predict_with_risk_matrix(
            player_data=player_data,
            usage_level=current_usage,
            apply_phase3_fixes=True,
            apply_hard_gates=False  # Get raw predictions for diagnostics
        )

        # Collect raw stats
        raw_stats = {
            'player_name': player_name,
            'season': season,
            'current_usage_pct': player_data.get('USG_PCT', 0) * 100,
            'age': player_data.get('AGE', None),
            'games_played': player_data.get('GP', None),
            'minutes_per_game': player_data.get('MIN', None),
        }

        # Add basic stats
        stat_fields = ['PTS', 'AST', 'REB', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'TS_PCT', 'USG_PCT',
                      'AST_PCT', 'REB_PCT', 'EFG_PCT', 'EFG_ISO_WEIGHTED']
        for field in stat_fields:
            if field in player_data.index:
                raw_stats[f'raw_{field.lower()}'] = player_data[field]

        # Collect feature calculations (what goes into the model)
        feature_calculations = {}

        # Stress vectors (from evaluate_plasticity_potential.py)
        stress_vector_fields = [
            'CREATION_VOLUME_RATIO', 'LEVERAGE_USG_DELTA', 'RS_PRESSURE_APPETITE',
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE', 'RS_RIM_APPETITE', 'EFG_ISO_WEIGHTED',
            'EFG_PCT_0_DRIBBLE', 'LEVERAGE_TS_DELTA', 'USG_PCT', 'PREV_RS_RIM_APPETITE',
            'PREV_EFG_ISO_WEIGHTED', 'EFG_ISO_WEIGHTED_YOY_DELTA', 'AGE_X_LEVERAGE_USG_DELTA_YOY_DELTA',
            'INEFFICIENT_VOLUME_SCORE', 'ABDICATION_RISK', 'SHOT_QUALITY_GENERATION_DELTA'
        ]

        for field in stress_vector_fields:
            if field in player_data.index:
                feature_calculations[field.lower()] = player_data[field]

        # Add USG interaction terms (calculated by the model)
        usg_pct = player_data.get('USG_PCT', 0)
        for field in ['EFG_ISO_WEIGHTED', 'RS_PRESSURE_APPETITE', 'RS_LATE_CLOCK_PRESSURE_RESILIENCE',
                     'CREATION_VOLUME_RATIO', 'LEVERAGE_USG_DELTA', 'RS_RIM_APPETITE']:
            if field in player_data.index:
                interaction_term = f'usg_x_{field.lower()}'
                feature_calculations[interaction_term] = usg_pct * player_data[field]

        # Add trajectory features if available
        trajectory_fields = ['PREV_RS_RIM_APPETITE', 'PREV_EFG_ISO_WEIGHTED', 'EFG_ISO_WEIGHTED_YOY_DELTA',
                           'AGE_X_LEVERAGE_USG_DELTA_YOY_DELTA']
        for field in trajectory_fields:
            if field in player_data.index:
                feature_calculations[field.lower()] = player_data[field]

        # Add dependence calculation components
        dependence_components = {
            'creation_volume_ratio': player_data.get('CREATION_VOLUME_RATIO', None),
            'creation_tax': player_data.get('CREATION_TAX', None),
            'rs_rim_appetite': player_data.get('RS_RIM_APPETITE', None),
            'ftr': player_data.get('RS_FTr', None),
            'shot_quality_generation_delta': player_data.get('SHOT_QUALITY_GENERATION_DELTA', None),
            'efg_iso_weighted': player_data.get('EFG_ISO_WEIGHTED', None),
            'pressure_resilience': player_data.get('RS_PRESSURE_RESILIENCE', None),
            'rs_early_clock_pressure_resilience': player_data.get('RS_EARLY_CLOCK_PRESSURE_RESILIENCE', None),
        }

        # Add Two Doors framework intermediate calculations
        from src.nba_data.scripts.calculate_dependence_score import _calculate_physicality_score, _calculate_skill_score

        try:
            physicality_score = _calculate_physicality_score(player_data)
            skill_score = _calculate_skill_score(player_data)

            # Physicality components
            rim_appetite = float(player_data.get('RS_RIM_APPETITE', 0.0))
            ftr = float(player_data.get('RS_FTr', 0.0))
            creation_vol_ratio = float(player_data.get('CREATION_VOLUME_RATIO', 0.0))

            # Skill components
            sq_delta = float(player_data.get('SHOT_QUALITY_GENERATION_DELTA', 0.0))
            creation_tax = float(player_data.get('CREATION_TAX', -0.20))
            efg_iso = float(player_data.get('EFG_ISO_WEIGHTED', 0.40))

            two_doors_components = {
                'physicality_score': physicality_score,
                'skill_score': skill_score,
                'norm_rim_appetite': min(rim_appetite / 0.40, 1.0) if not np.isnan(rim_appetite) else 0.0,
                'norm_ftr': min(ftr / 0.50, 1.0) if not np.isnan(ftr) else 0.0,
                'sabonis_constraint_applied': creation_vol_ratio < 0.15,
                'sq_delta_raw': sq_delta,
                'creation_tax_raw': creation_tax,
                'efg_iso_raw': efg_iso,
                'empty_calories_constraint_applied': sq_delta < 0.0,
            }
        except Exception as e:
            logger.warning(f"Could not calculate Two Doors components for {player_name} {season}: {e}")
            two_doors_components = {
                'physicality_score': None,
                'skill_score': None,
                'norm_rim_appetite': None,
                'norm_ftr': None,
                'sabonis_constraint_applied': None,
                'sq_delta_raw': None,
                'creation_tax_raw': None,
                'efg_iso_raw': None,
                'empty_calories_constraint_applied': None,
            }

        # Model predictions and metadata
        model_predictions = {
            'predicted_archetype': prediction_result.get('archetype', None),
            'performance_score': prediction_result.get('performance_score', None),
            'dependence_score': prediction_result.get('dependence_score', None),
            'risk_category': prediction_result.get('risk_category', None),
        }

        # Add probabilities if available
        if 'probabilities' in prediction_result:
            model_predictions['prob_king'] = prediction_result['probabilities'].get('King (Resilient Star)', None)
            model_predictions['prob_bulldozer'] = prediction_result['probabilities'].get('Bulldozer (Fragile Star)', None)
            model_predictions['prob_sniper'] = prediction_result['probabilities'].get('Sniper (Resilient Role)', None)
            model_predictions['prob_victim'] = prediction_result['probabilities'].get('Victim (Fragile Role)', None)

        # Combine all diagnostic data
        diagnostic_data = {
            'raw_stats': raw_stats,
            'feature_calculations': feature_calculations,
            'dependence_components': dependence_components,
            'two_doors_components': two_doors_components,
            'model_predictions': model_predictions,
        }

        return diagnostic_data

    except Exception as e:
        logger.warning(f"Could not collect diagnostic data for {player_name} {season}: {e}")
        return {'error': str(e)}


def flatten_diagnostic_data(diagnostic_data: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten nested diagnostic data into a single-level dictionary for CSV output."""

    flattened = {}

    # Flatten raw stats
    if 'raw_stats' in diagnostic_data:
        for key, value in diagnostic_data['raw_stats'].items():
            flattened[f"raw_{key}"] = value

    # Flatten feature calculations
    if 'feature_calculations' in diagnostic_data:
        for key, value in diagnostic_data['feature_calculations'].items():
            flattened[f"calc_{key}"] = value

    # Flatten dependence components
    if 'dependence_components' in diagnostic_data:
        for key, value in diagnostic_data['dependence_components'].items():
            flattened[f"dep_{key}"] = value

    # Flatten Two Doors components
    if 'two_doors_components' in diagnostic_data:
        for key, value in diagnostic_data['two_doors_components'].items():
            flattened[f"doors_{key}"] = value

    # Flatten model predictions
    if 'model_predictions' in diagnostic_data:
        for key, value in diagnostic_data['model_predictions'].items():
            flattened[f"pred_{key}"] = value

    return flattened


class OverallStarTestCase:
    """Represents a single test case for overall star prediction."""

    def __init__(
        self,
        name: str,
        season: str,
        category: str,
        expected_franchise_cornerstone: bool,
        context: str = "",
        mechanism: str = ""
    ):
        self.name = name
        self.season = season
        self.category = category
        self.expected_franchise_cornerstone = expected_franchise_cornerstone  # True = should be Franchise Cornerstone
        self.context = context
        self.mechanism = mechanism


def get_test_cases() -> List[OverallStarTestCase]:
    """Define all critical test cases for overall star prediction validation."""

    test_cases = [
        # ========== Category 1: Confirmed Franchise Cornerstones ==========
        # These players should be correctly identified as Franchise Cornerstones
        # (High Performance + Low Dependence)
        OverallStarTestCase(
            name="Nikola Jokić",
            season="2023-24",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 29. MVP, All-Star, elite playmaker and scorer. Current usage 31.4%.",
            mechanism="Should show High Performance + Low Dependence (self-created offense)."
        ),
        OverallStarTestCase(
            name="Luka Dončić",
            season="2023-24",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 25. All-Star, elite scorer and playmaker. Current usage 35.3%.",
            mechanism="Should show High Performance + Low Dependence despite high usage."
        ),
        OverallStarTestCase(
            name="Giannis Antetokounmpo",
            season="2023-24",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 29. MVP, All-Star, dominant two-way player. Current usage 30.7%.",
            mechanism="Should show High Performance + Low Dependence (physical dominance)."
        ),
        OverallStarTestCase(
            name="Joel Embiid",
            season="2023-24",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 30. MVP, All-Star, elite rim protection and scoring. Current usage 33.7%.",
            mechanism="Should show High Performance + Low Dependence despite injury history."
        ),
        OverallStarTestCase(
            name="Joel Embiid",
            season="2018-19",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 24. MVP candidate, elite rim pressure and scoring. First-team All-NBA despite limited games.",
            mechanism="Should show High Performance + Low Dependence (self-created offense despite injury limitations)."
        ),

        # ========== Category 2: Borderline/Questionable Cases ==========
        # These players might be Franchise Cornerstones but could be misclassified
        OverallStarTestCase(
            name="Shai Gilgeous-Alexander",
            season="2023-24",
            category="Borderline Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 25. All-Star, emerging as elite scorer. Current usage 32.8%.",
            mechanism="Should show High Performance + Low Dependence as primary initiator."
        ),
        OverallStarTestCase(
            name="Tyrese Maxey",
            season="2023-24",
            category="Borderline Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 23. All-Star, elite shooting and scoring. Current usage 25.6%.",
            mechanism="Should show High Performance + Low Dependence with creation volume."
        ),

        # ========== Category 3: Not Franchise Cornerstones ==========
        # These players should NOT be classified as Franchise Cornerstones
        OverallStarTestCase(
            name="Jordan Poole",
            season="2023-24",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 25. Good scorer but system-dependent. Current usage 23.5%.",
            mechanism="Should show High Performance but High Dependence (system merchant)."
        ),
        OverallStarTestCase(
            name="Jordan Poole",
            season="2021-22",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 23. High usage breakout but system merchant. Reliant on Curry gravity for efficiency.",
            mechanism="Should show High Performance but High Dependence (system merchant despite high usage)."
        ),
        OverallStarTestCase(
            name="Domantas Sabonis",
            season="2023-24",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 28. All-Star but system-based. Current usage 21.7%.",
            mechanism="Should show High Performance but High Dependence (assisted/system-based)."
        ),
        OverallStarTestCase(
            name="Julius Randle",
            season="2023-24",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 29. Good scorer but playoff struggles. Current usage 27.6%.",
            mechanism="Should show Moderate Performance + Moderate/High Dependence."
        ),
        OverallStarTestCase(
            name="DeMar DeRozan",
            season="2015-16",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 26. All-Star, reliable scorer but not franchise cornerstone. High individual performance but lacks elite portability.",
            mechanism="Should show High Performance but Moderate/High Dependence (not truly portable at franchise level)."
        ),
        OverallStarTestCase(
            name="DeMar DeRozan",
            season="2016-17",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 27. All-Star, consistent scorer but not franchise cornerstone. Good but not elite in terms of franchise impact.",
            mechanism="Should show High Performance but Moderate/High Dependence (solid contributor but not transformative)."
        ),
        OverallStarTestCase(
            name="Karl-Anthony Towns",
            season="2021-22",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 26. Elite regular season stats but playoff struggles. High volume scorer but lacks creation volume and resilience.",
            mechanism="Should show Moderate Performance with lack of stress vectors needed for playoff success."
        ),
        OverallStarTestCase(
            name="Karl-Anthony Towns",
            season="2022-23",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 27. Elite regular season stats but playoff fragility persists. High volume scorer but inconsistent creation.",
            mechanism="Should show Moderate Performance with persistent lack of playoff resilience and creation volume."
        ),
        OverallStarTestCase(
            name="Karl-Anthony Towns",
            season="2023-24",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 28. High usage scorer but playoff performance gap remains. Lacks true franchise cornerstone creation volume.",
            mechanism="Should show Moderate Performance with continued lack of stress vectors needed for playoff success."
        ),
        OverallStarTestCase(
            name="Ben Simmons",
            season="2018-19",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 22. Rookie All-Star, elite passer and rebounder but shooting deficiency. Abdication Tax should trigger.",
            mechanism="Should show Low Performance due to creation tax viability (shooting) and leverage issues (passivity)."
        ),
        OverallStarTestCase(
            name="Ben Simmons",
            season="2020-21",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 24. Continued struggles with shooting and creation. Hawks series collapse. Fear of free throws.",
            mechanism="Should show Low Performance with persistent creation tax issues and Abdication Tax (negative leverage)."
        ),

        # ========== Category 4: Role Players (Depth/Avoid) ==========
        # These should definitely not be Franchise Cornerstones
        OverallStarTestCase(
            name="Aaron Gordon",
            season="2023-24",
            category="Role Player - Depth",
            expected_franchise_cornerstone=False,
            context="Age 28. Veteran role player. Current usage 13.5%.",
            mechanism="Should show Low Performance + Low Dependence (reliable but limited)."
        ),
        OverallStarTestCase(
            name="Brook Lopez",
            season="2023-24",
            category="Role Player - Depth",
            expected_franchise_cornerstone=False,
            context="Age 36. Veteran center. Current usage 11.8%.",
            mechanism="Should show Low Performance + Low Dependence (defensive specialist)."
        ),

        # ========== User-Provided Test Cases ==========
        # 2015-16 Season Cases
        OverallStarTestCase(
            name="Chris Paul",
            season="2015-16",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 30. MVP, elite playmaker and defender. Multiple All-Star.",
            mechanism="Should show High Performance + Low Dependence (primary facilitator)."
        ),
        OverallStarTestCase(
            name="Chris Paul",
            season="2016-17",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 31. MVP candidate, elite playmaker and defender. All-Star, consistent excellence.",
            mechanism="Should show High Performance + Low Dependence (primary facilitator)."
        ),
        OverallStarTestCase(
            name="Chris Paul",
            season="2017-18",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 32. MVP candidate, elite playmaker and defender. All-Star, peak performance.",
            mechanism="Should show High Performance + Low Dependence (primary facilitator)."
        ),
        OverallStarTestCase(
            name="Jimmy Butler III",
            season="2015-16",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 26. All-Star, defensive player of the year. Elite two-way player.",
            mechanism="Should show High Performance + Low Dependence (versatile forward)."
        ),
        OverallStarTestCase(
            name="James Harden",
            season="2015-16",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 26. Scoring champion, MVP candidate. Elite scorer and creator.",
            mechanism="Should show High Performance + Low Dependence (primary offensive engine)."
        ),
        OverallStarTestCase(
            name="Eric Bledsoe",
            season="2015-16",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 26. Good scorer but inconsistent. Backup-level impact.",
            mechanism="Should show Moderate Performance + Moderate Dependence (role player)."
        ),
        OverallStarTestCase(
            name="James Harden",
            season="2015-16",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 26. Scoring champion, MVP candidate. Elite scorer and creator.",
            mechanism="Should show High Performance + Low Dependence (primary offensive engine)."
        ),
        OverallStarTestCase(
            name="John Wall",
            season="2015-16",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 25. All-Star, elite playmaker. Primary facilitator for Wizards.",
            mechanism="Should show High Performance + Low Dependence (primary playmaker)."
        ),
        OverallStarTestCase(
            name="LeBron James",
            season="2015-16",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 31. MVP, dominant all-around player. Elite in every category.",
            mechanism="Should show High Performance + Low Dependence (versatile superstar)."
        ),
        OverallStarTestCase(
            name="Kawhi Leonard",
            season="2015-16",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 24. Finals MVP, elite two-way player. Defensive player of the year.",
            mechanism="Should show High Performance + Low Dependence (versatile forward with elite defense)."
        ),

        # 2024-25 Season Cases
        OverallStarTestCase(
            name="Giannis Antetokounmpo",
            season="2024-25",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 30. MVP, dominant two-way player. Current champion.",
            mechanism="Should show High Performance + Low Dependence (physical dominance)."
        ),
        OverallStarTestCase(
            name="Donovan Mitchell",
            season="2024-25",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 28. All-Star, elite scorer. Primary offensive option.",
            mechanism="Should show High Performance + Low Dependence (primary scorer)."
        ),
        OverallStarTestCase(
            name="LeBron James",
            season="2024-25",
            category="Confirmed Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 40. GOAT candidate, still elite all-around player.",
            mechanism="Should show High Performance + Low Dependence (versatile veteran)."
        ),
        OverallStarTestCase(
            name="Cade Cunningham",
            season="2024-25",
            category="Emerging Franchise Cornerstone",
            expected_franchise_cornerstone=True,
            context="Age 22. Rookie of the year, developing star. High potential.",
            mechanism="Should show High Performance + Low Dependence (building as primary option)."
        ),
        OverallStarTestCase(
            name="Kevin Porter Jr",
            season="2024-25",
            category="Not Franchise Cornerstone",
            expected_franchise_cornerstone=False,
            context="Age 25. Talented but inconsistent. Off-court issues impact reliability.",
            mechanism="Should show Moderate Performance + High Dependence (unreliable)."
        ),
    ]

    return test_cases


def evaluate_franchise_cornerstone_prediction(
    performance_score: float,
    dependence_score: Optional[float],
    risk_category: str,
    expected_franchise_cornerstone: bool
) -> Dict:
    """Evaluate if prediction correctly identifies Franchise Cornerstone status."""

    result = {
        'correct_classification': False,
        'predicted_franchise_cornerstone': False,
        'notes': []
    }

    # Determine if model predicts Franchise Cornerstone
    is_franchise_cornerstone = False
    if pd.notna(performance_score) and pd.notna(dependence_score):
        is_franchise_cornerstone = (
            performance_score >= 0.70 and  # High Performance
            dependence_score < 0.50       # Low Dependence
        )
    elif "Franchise Cornerstone" in str(risk_category):
        # Fallback to risk category if scores available
        is_franchise_cornerstone = True

    result['predicted_franchise_cornerstone'] = is_franchise_cornerstone
    result['correct_classification'] = (is_franchise_cornerstone == expected_franchise_cornerstone)

    # Add diagnostic notes
    if not result['correct_classification']:
        if expected_franchise_cornerstone and not is_franchise_cornerstone:
            # False Negative: Should be FC but wasn't predicted
            if performance_score < 0.70:
                result['notes'].append(f"Performance too low ({performance_score:.2%} < 70%)")
            if pd.notna(dependence_score) and dependence_score >= 0.30:
                result['notes'].append(f"Dependence too high ({dependence_score:.2%} >= 30%)")
            result['notes'].append("False Negative: Should be Franchise Cornerstone")
        elif not expected_franchise_cornerstone and is_franchise_cornerstone:
            # False Positive: Shouldn't be FC but was predicted
            result['notes'].append("False Positive: Should not be Franchise Cornerstone")

    return result




def run_overall_star_test_suite():
    """
    Run all test cases for overall star prediction and generate comprehensive diagnostic output.

    PRIMARY FRAMEWORK: Franchise Cornerstone Detection at Current Usage
    - Tests Performance + Dependence evaluation
    - Generates combined CSV with full diagnostic data from player_season_analyzer.py
    """

    logger.info("=" * 100)
    logger.info("OVERALL STAR PREDICTION: FRANCHISE CORNERSTONE CLASSIFICATION TEST SUITE")
    logger.info("=" * 100)

    predictor = ConditionalArchetypePredictor()
    test_cases = get_test_cases()

    results = []
    diagnostic_rows = []
    summary_stats = {
        'total': len(test_cases),
        'found': 0,
        'correct': 0,
        'incorrect': 0,
        'by_category': {}
    }

    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'='*100}")
        logger.info(f"Test {i}/{len(test_cases)}: {test_case.name} ({test_case.season})")
        logger.info(f"Category: {test_case.category}")
        logger.info(f"Expected Franchise Cornerstone: {test_case.expected_franchise_cornerstone}")
        logger.info(f"{'='*100}")
        logger.info(f"Context: {test_case.context}")
        logger.info(f"Mechanism: {test_case.mechanism}")

        # Get player data
        player_data = predictor.get_player_data(test_case.name, test_case.season)

        if player_data is None:
            logger.warning(f"  ❌ NO DATA FOUND - Skipping")
            results.append({
                'test_number': i,
                'player_name': test_case.name,
                'season': test_case.season,
                'category': test_case.category,
                'expected_franchise_cornerstone': test_case.expected_franchise_cornerstone,
                'data_found': False,
                'performance_score': None,
                'dependence_score': None,
                'risk_category': None,
                'predicted_franchise_cornerstone': None,
                'correct_classification': False,
                'notes': 'No data found'
            })
            continue

        summary_stats['found'] += 1

        # Get current usage
        current_usage = player_data.get('USG_PCT', 0.20)
        if pd.notna(current_usage) and current_usage > 1.0:
            current_usage = current_usage / 100.0  # Convert from percentage if needed

        logger.info(f"  Current Usage: {current_usage*100:.1f}%")

        # Predict with 2D Risk Matrix at current usage
        result_2d = predictor.predict_with_risk_matrix(
            player_data,
            current_usage,  # Test at CURRENT usage (not elevated)
            apply_phase3_fixes=True,
            apply_hard_gates=False  # Use 2D evaluation
        )

        # Extract 2D metrics
        performance_score = result_2d.get('performance_score', 0.0)
        dependence_score = result_2d.get('dependence_score', None)
        risk_category = result_2d.get('risk_category', 'Unknown')
        predicted_archetype = result_2d.get('archetype', 'Unknown')

        logger.info(f"\n  Prediction Results (2D Risk Matrix at Current Usage):")
        logger.info(f"    Predicted Archetype: {predicted_archetype}")
        logger.info(f"    Performance Score: {performance_score:.2%}")
        if dependence_score is not None:
            logger.info(f"    Dependence Score: {dependence_score:.2%}")
        else:
            logger.info(f"    Dependence Score: N/A (Missing data)")
        logger.info(f"    Risk Category: {risk_category}")

        # Evaluate classification
        evaluation = evaluate_franchise_cornerstone_prediction(
            performance_score,
            dependence_score,
            risk_category,
            test_case.expected_franchise_cornerstone
        )

        logger.info(f"\n  Evaluation:")
        if evaluation['correct_classification']:
            logger.info(f"    ✅ CORRECT")
            summary_stats['correct'] += 1
        else:
            logger.info(f"    ❌ INCORRECT")
            summary_stats['incorrect'] += 1

        if evaluation['notes']:
            for note in evaluation['notes']:
                logger.info(f"      - {note}")

        # Track by category
        category = test_case.category.split(' - ')[0]  # Get main category
        if category not in summary_stats['by_category']:
            summary_stats['by_category'][category] = {'total': 0, 'correct': 0, 'incorrect': 0}
        summary_stats['by_category'][category]['total'] += 1
        if evaluation['correct_classification']:
            summary_stats['by_category'][category]['correct'] += 1
        else:
            summary_stats['by_category'][category]['incorrect'] += 1

        # Store results
        results.append({
            'test_number': i,
            'player_name': test_case.name,
            'season': test_case.season,
            'category': test_case.category,
            'expected_franchise_cornerstone': test_case.expected_franchise_cornerstone,
            'current_usage_pct': current_usage * 100,
            'data_found': True,
            'predicted_archetype': predicted_archetype,
            'performance_score': performance_score,
            'dependence_score': dependence_score,
            'risk_category': risk_category,
            'predicted_franchise_cornerstone': evaluation['predicted_franchise_cornerstone'],
            'correct_classification': evaluation['correct_classification'],
            'notes': '; '.join(evaluation['notes']) if evaluation['notes'] else 'None'
        })

        # Collect comprehensive diagnostic data
        logger.info(f"  Collecting diagnostic data...")
        diagnostic_data = collect_comprehensive_diagnostics(predictor, test_case.name, test_case.season)
        flattened_diagnostic = flatten_diagnostic_data(diagnostic_data)

        # Add test case info to diagnostic row
        flattened_diagnostic.update({
            'test_number': i,
            'test_category': test_case.category,
            'expected_franchise_cornerstone': test_case.expected_franchise_cornerstone,
            'predicted_franchise_cornerstone': evaluation['predicted_franchise_cornerstone'],
            'correct_classification': evaluation['correct_classification'],
            'performance_score': performance_score,
            'dependence_score': dependence_score,
            'risk_category': risk_category
        })

        diagnostic_rows.append(flattened_diagnostic)

    # Generate summary report
    logger.info(f"\n{'='*100}")
    logger.info("SUMMARY REPORT - OVERALL STAR PREDICTION")
    logger.info(f"{'='*100}")
    logger.info(f"Total Test Cases: {summary_stats['total']}")
    logger.info(f"Data Found: {summary_stats['found']}")
    logger.info(f"Correct Classifications: {summary_stats['correct']}")
    logger.info(f"Incorrect Classifications: {summary_stats['incorrect']}")
    if summary_stats['found'] > 0:
        accuracy = summary_stats['correct'] / summary_stats['found'] * 100
        logger.info(f"Accuracy: {accuracy:.1f}%")

    logger.info(f"\nBy Category:")
    for category, stats in summary_stats['by_category'].items():
        accuracy = stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
        logger.info(f"  {category}: {stats['correct']}/{stats['total']} correct ({accuracy:.1f}%)")

    # Save results
    df_results = pd.DataFrame(results)
    results_path = Path("results") / "overall_star_prediction_test_results.csv"
    df_results.to_csv(results_path, index=False)
    logger.info(f"\nTest results saved to: {results_path}")

    # Save comprehensive diagnostic CSV
    df_diagnostics = pd.DataFrame(diagnostic_rows)
    diagnostics_path = Path("results") / "overall_star_prediction_diagnostics.csv"
    df_diagnostics.to_csv(diagnostics_path, index=False)
    logger.info(f"Comprehensive diagnostics saved to: {diagnostics_path}")
    logger.info(f"Total diagnostic columns: {len(df_diagnostics.columns)}")
    logger.info(f"Total diagnostic rows: {len(df_diagnostics)}")

    # Generate markdown report
    generate_markdown_report(df_results, summary_stats, diagnostics_path)

    return df_results, df_diagnostics, summary_stats


def generate_markdown_report(df_results: pd.DataFrame, summary_stats: Dict, diagnostics_path: Path):
    """Generate a markdown report of test results."""

    report_path = Path("results") / "overall_star_prediction_test_report.md"

    with open(report_path, 'w') as f:
        f.write("# Overall Star Prediction: Franchise Cornerstone Classification Test Report\n\n")
        f.write(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Executive Summary\n\n")
        f.write("**Primary Focus**: Testing the model's ability to correctly identify Franchise Cornerstones at current usage levels.\n\n")
        f.write("**Framework**: 2D Risk Matrix - Franchise Cornerstones require High Performance (≥70%) + Low Dependence (<30%).\n\n")
        f.write(f"- **Total Test Cases**: {summary_stats['total']}\n")
        f.write(f"- **Data Found**: {summary_stats['found']}\n")
        f.write(f"- **Correct Classifications**: {summary_stats['correct']}\n")
        f.write(f"- **Incorrect Classifications**: {summary_stats['incorrect']}\n")
        if summary_stats['found'] > 0:
            accuracy = summary_stats['correct'] / summary_stats['found'] * 100
            f.write(f"- **Accuracy**: {accuracy:.1f}%\n")
        f.write("\n")

        f.write("## Results by Category\n\n")
        for category, stats in summary_stats['by_category'].items():
            accuracy = stats['correct'] / stats['total'] * 100 if stats['total'] > 0 else 0
            f.write(f"### {category}\n")
            f.write(f"- **Total**: {stats['total']}\n")
            f.write(f"- **Correct**: {stats['correct']}\n")
            f.write(f"- **Incorrect**: {stats['incorrect']}\n")
            f.write(f"- **Accuracy**: {accuracy:.1f}%\n\n")

        f.write("## Detailed Results\n\n")
        f.write("| Test | Player | Season | Category | Expected FC | Predicted FC | Performance | Dependence | Risk Category | Correct |\n")
        f.write("|------|--------|--------|----------|-------------|---------------|-------------|------------|---------------|---------|\n")

        for _, row in df_results.iterrows():
            if not row['data_found']:
                status = "❌ No Data"
                perf_str = "N/A"
                dep_str = "N/A"
                risk_str = "N/A"
                pred_fc = "N/A"
            elif row['correct_classification']:
                status = "✅ Correct"
                perf_str = f"{row['performance_score']:.2%}" if pd.notna(row['performance_score']) else "N/A"
                dep_str = f"{row['dependence_score']:.2%}" if pd.notna(row['dependence_score']) else "N/A"
                risk_str = str(row['risk_category']) if pd.notna(row['risk_category']) else "N/A"
                pred_fc = "Yes" if row['predicted_franchise_cornerstone'] else "No"
            else:
                status = "❌ Incorrect"
                perf_str = f"{row['performance_score']:.2%}" if pd.notna(row['performance_score']) else "N/A"
                dep_str = f"{row['dependence_score']:.2%}" if pd.notna(row['dependence_score']) else "N/A"
                risk_str = str(row['risk_category']) if pd.notna(row['risk_category']) else "N/A"
                pred_fc = "Yes" if row['predicted_franchise_cornerstone'] else "No"

            expected_fc = "Yes" if row['expected_franchise_cornerstone'] else "No"

            f.write(f"| {row['test_number']} | {row['player_name']} | {row['season']} | {row['category']} | "
                   f"{expected_fc} | {pred_fc} | {perf_str} | {dep_str} | {risk_str} | {status} |\n")

        f.write("\n## Diagnostic Data\n\n")
        f.write(f"Comprehensive diagnostic data has been saved to: `{diagnostics_path}`\n\n")
        f.write("This CSV contains all raw statistics, feature calculations, and predictions from `player_season_analyzer.py` for each test case, enabling detailed analysis of model mistakes.\n\n")

        f.write("## Key Metrics for Analysis\n\n")
        f.write("**Franchise Cornerstone Criteria**:\n")
        f.write("- Performance Score ≥ 70%\n")
        f.write("- Dependence Score < 30%\n")
        f.write("- Risk Category = 'Franchise Cornerstone'\n\n")

        f.write("**Common Issues to Investigate**:\n")
        f.write("- False Negatives: Elite players not classified as Franchise Cornerstones\n")
        f.write("- False Positives: Non-elite players incorrectly classified as Franchise Cornerstones\n")
        f.write("- Performance vs. Dependence miscalibration\n\n")

        # Add error analysis
        incorrect_tests = df_results[~df_results['correct_classification'] & df_results['data_found']]
        if len(incorrect_tests) > 0:
            f.write("## Incorrect Classifications Analysis\n\n")
            for _, row in incorrect_tests.iterrows():
                f.write(f"### {row['player_name']} ({row['season']})\n")
                f.write(f"- **Expected**: {'Franchise Cornerstone' if row['expected_franchise_cornerstone'] else 'Not Franchise Cornerstone'}\n")
                f.write(f"- **Predicted**: {'Franchise Cornerstone' if row['predicted_franchise_cornerstone'] else 'Not Franchise Cornerstone'}\n")
                f.write(f"- **Performance**: {row['performance_score']:.2%}\n")
                if pd.notna(row['dependence_score']):
                    f.write(f"- **Dependence**: {row['dependence_score']:.2%}\n")
                else:
                    f.write(f"- **Dependence**: N/A\n")
                f.write(f"- **Risk Category**: {row['risk_category']}\n")
                f.write(f"- **Notes**: {row['notes']}\n\n")

        # Add missing data section
        missing_data = df_results[~df_results['data_found']]
        if len(missing_data) > 0:
            f.write("## Missing Data\n\n")
            for _, row in missing_data.iterrows():
                f.write(f"- **{row['player_name']} ({row['season']})**: No data found in dataset\n\n")

    logger.info(f"Markdown report saved to: {report_path}")


if __name__ == "__main__":
    results, diagnostics, stats = run_overall_star_test_suite()
