"""
Critical Case Studies for Latent Star Detection


This script tests the model on critical case studies that probe different
failure modes and validate the model's ability to distinguish:

Good breakouts (should predict high star-level = Bulldozer/King)

Mediocre breakouts (should predict low star-level = Victim)

System players (should predict Sniper at high usage)

Context-dependent players (should account for teammate gravity)

Max contract mistakes (players paid like stars but not playoff stars)

Comparison cases (similar caliber players with different playoff outcomes)

Based on first principles framework and user insights.
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LatentStarTestCase:
    """Represents a single test case for latent star detection."""
    
    def __init__(
        self,
        name: str,
        season: str,
        category: str,
        test_usage: float,
        expected_outcome: str,
        expected_star_level: Optional[str] = None,
        context: str = "",
        mechanism: str = ""
    ):
        self.name = name
        self.season = season
        self.category = category
        self.test_usage = test_usage  # As decimal (e.g., 0.30 for 30%)
        self.expected_outcome = expected_outcome  # "Bulldozer", "Victim", "Sniper", "King", etc.
        self.expected_star_level = expected_star_level  # "High" (>65%), "Medium" (30-65%), "Low" (<55%)
        self.context = context
        self.mechanism = mechanism

def get_test_cases() -> List[LatentStarTestCase]:
    """Define all critical test cases for latent star detection validation."""
    
    test_cases = [
        # ========== Category 1: The "Latent Stars" (True Positives) ==========
        LatentStarTestCase(
            name="Shai Gilgeous-Alexander",
        season="2018-19",
        category="True Positive - Latent Star",
        test_usage=0.30,
        expected_outcome="Bulldozer",  # Good breakout
        expected_star_level="High",  # >65%
        context="Rookie year. 18.3% Usage. Role player behind Lou Williams and Danilo Gallinari.",
        mechanism="Should see elite Driving/Physicality Vector (Rim Pressure) even at low volume."
    ),
    LatentStarTestCase(
        name="Victor Oladipo",
        season="2016-17",
        category="True Positive - Latent Star",
        test_usage=0.30,
        expected_outcome="Bulldozer",
        expected_star_level="High",  # >65%
        context="Russell Westbrook's MVP usage-hole year. Oladipo was relegated to a spot-up shooter (21% Usage).",
        mechanism="Did he maintain Creation Vector efficiency on the few self-created shots?"
    ),
    LatentStarTestCase(
        name="Jalen Brunson",
        season="2020-21",
        category="True Positive - Latent Star",
        test_usage=0.32,
        expected_outcome="Bulldozer",
        expected_star_level="High",  # >65%
        context="19.6% Usage. Backup to Luka Dončić.",
        mechanism="Gold Standard validation. High Creation Efficiency + High Leverage Resilience."
    ),
    LatentStarTestCase(
        name="Tyrese Maxey",
        season="2021-22",
        category="True Positive - Latent Star",
        test_usage=0.28,
        expected_outcome="Bulldozer",
        expected_star_level="High",  # >65%
        context="22.2% Usage. Broke out to 27.3% in '24.",
        mechanism="Elite Creation Vector and Leverage Vector even at lower usage."
    ),
    LatentStarTestCase(
        name="Pascal Siakam",
        season="2018-19",
        category="True Positive - Latent Star",
        test_usage=0.28,
        expected_outcome="Bulldozer", # Or King
        expected_star_level="High", # >65%
        context="The 'Spin Cycle' breakout year (20.5% Usage). Won MIP and Championship.",
        mechanism="High motor, transition scoring, improving face-up game. Demonstrates scalability of efficiency with volume."
    ),
    LatentStarTestCase(
        name="Jayson Tatum",
        season="2017-18",
        category="True Positive - Rookie Sensation",
        test_usage=0.28,
        expected_outcome="Bulldozer",
        expected_star_level="High", # >65%
        context="Rookie year (19.5% Usage). Exploded in playoffs without Kyrie/Hayward.",
        mechanism="Elite shot creation profile and positional size even at low usage."
    ),
    LatentStarTestCase(
        name="Mikal Bridges",
        season="2021-22",
        category="True Positive - Usage Shock",
        test_usage=0.30,
        expected_outcome="Bulldozer",
        expected_star_level="High", # >65%
        context="Role player in Phoenix (14.2% Usage). Broke out when traded to Brooklyn with higher usage.",
        mechanism="Tests model's ability to see star potential through role constraints. Elite efficiency on low volume."
    ),
    LatentStarTestCase(
        name="Desmond Bane",
        season="2021-22",
        category="True Positive - Latent Star",
        test_usage=0.28,
        expected_outcome="Bulldozer",
        expected_star_level="High", # >65%
        context="22.6% Usage. Elite secondary creator with high shooting efficiency.",
        mechanism="Tests model's ability to identify secondary creators who can scale up. Elite Creation Vector and shooting."
    ),
    
        # ========== Category 2: The "Mirage" Breakouts & Fragile Stars (False Positives) ==========
        LatentStarTestCase(
            name="Jordan Poole",
        season="2021-22",
        category="False Positive - Mirage Breakout",
        test_usage=0.30,
        expected_outcome="Victim",
        expected_star_level="Low",  # <55%
        context="26% Usage. System merchant relying on Curry gravity.",
        mechanism="Should detect low Pressure Resilience and dependence on open shots."
    ),
    LatentStarTestCase(
        name="Talen Horton-Tucker",
        season="2020-21",
        category="False Positive - Mirage Breakout",
        test_usage=0.25,
        expected_outcome="Victim",
        expected_star_level="Low",  # <55%
        context="18% Usage. Elite rim pressure numbers on low volume but poor efficiency.",
        mechanism="Creation Efficiency was actually poor despite high Physicality Vector."
    ),
    LatentStarTestCase(
        name="Christian Wood",
        season="2020-21",
        category="False Positive - Empty Calories",
        test_usage=0.26,
        expected_outcome="Victim",
        expected_star_level="Low",  # <55%
        context="Massive stats on tanking team. Low leverage performance.",
        mechanism="Tests Leverage Vector (Clutch) and Pressure Vector."
    ),
    LatentStarTestCase(
        name="D'Angelo Russell",
        season="2018-19",
        category="False Positive - Fool's Gold",
        test_usage=0.31,
        expected_outcome="Victim",
        expected_star_level="Low",  # <55%
        context="All-Star season (31% Usage). Reliance on mid-range/floaters.",
        mechanism="Tests Physicality fragility (low Rim Pressure Resilience)."
    ),
    LatentStarTestCase(
        name="Julius Randle",
        season="2020-21",
        category="False Positive - Empty Calories",
        test_usage=0.30,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="All-NBA season (29% Usage). Imploded in playoffs (29.8% FG).",
        mechanism="Tests for 'Bulldozer' profile that lacks true resilience traits (tough shot making, leverage stability)."
    ),
    
        # ========== Category 3: The "Ben Simmons" Fragility Test ==========
        LatentStarTestCase(
            name="Ben Simmons",
        season="2017-18",
        category="True Negative - Fragile Star",
        test_usage=0.25,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Rookie year (22.3% Usage). Playoff collapse vs Celtics (1 point game).",
        mechanism="High raw stats but fatal flaws in Creation (shooting) and Leverage (passivity)."
    ),
    LatentStarTestCase(
        name="Ben Simmons",
        season="2018-19",
        category="True Negative - Fragile Star",
        test_usage=0.25,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="22.1% Usage. Continued playoff struggles.",
        mechanism="Persistent lack of creation tax viability."
    ),
    LatentStarTestCase(
        name="Ben Simmons",
        season="2020-21",
        category="True Negative - Fragile Star",
        test_usage=0.25,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="20.2% Usage. The Hawks series collapse. Fear of free throws.",
        mechanism="Abdication Tax should trigger (negative Leverage USG Delta) and low Creation Tax."
    ),
    
        # ========== Category 4: The "System Players" (The Ceiling Test) ==========
        LatentStarTestCase(
            name="Tyus Jones",
        season="2021-22",
        category="System Player - Ceiling Test",
        test_usage=0.25,
        expected_outcome="Sniper", # Or Victim
        expected_star_level="Low",  # <55%
        context="Elite assist-to-turnover ratio role player.",
        mechanism="Should predict 'Sniper' or 'Victim' at high usage. Lacks creation ceiling."
    ),
    
        # ========== Category 5: Comparison Cases ==========
        LatentStarTestCase(
            name="Domantas Sabonis",
        season="2021-22",
        category="True Negative - Comparison Case",
        test_usage=0.28,
        expected_outcome="Victim",
        expected_star_level="Low",  # <55%
        context="Traded 1-1 for Haliburton. All-Star, but lacks playoff resilience.",
        mechanism="Model should identify lack of stress vectors (Physicality/Creation) needed for playoff success."
    ),
    LatentStarTestCase(
        name="Tyrese Haliburton",
        season="2021-22",
        category="True Positive - Comparison Case",
        test_usage=0.28,
        expected_outcome="Bulldozer",
        expected_star_level="High",  # >65%
        context="Traded 1-1 for Sabonis. Elite Creation and Leverage vectors.",
        mechanism="Model should identify elite stress vectors."
    ),
    
        # ========== Category 6: The "Empty Stats" Stars (True Negatives - Regular Season Stars, Playoff Fragile) ==========
        LatentStarTestCase(
            name="Karl-Anthony Towns",
        season="2015-16",
        category="True Negative - Empty Stats Star",
        test_usage=0.28,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Rookie year (25.5% Usage). High volume scorer but lacks playoff resilience.",
        mechanism="Tests model's ability to identify players with high raw stats but low stress vectors (Physicality/Creation/Leverage)."
    ),
    LatentStarTestCase(
        name="Karl-Anthony Towns",
        season="2016-17",
        category="True Negative - Empty Stats Star",
        test_usage=0.28,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Age 21. High usage scorer (28.1%) but playoff struggles.",
        mechanism="Persistent lack of playoff resilience despite elite regular season production."
    ),
    LatentStarTestCase(
        name="Karl-Anthony Towns",
        season="2017-18",
        category="True Negative - Empty Stats Star",
        test_usage=0.28,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Age 22. All-Star but playoff performance doesn't match regular season.",
        mechanism="Model should identify lack of stress vectors needed for playoff success."
    ),
    LatentStarTestCase(
        name="Karl-Anthony Towns",
        season="2018-19",
        category="True Negative - Empty Stats Star",
        test_usage=0.28,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Age 23. High volume scorer but playoff fragility persists.",
        mechanism="Tests consistency - same flaws across multiple seasons."
    ),
    LatentStarTestCase(
        name="Karl-Anthony Towns",
        season="2019-20",
        category="True Negative - Empty Stats Star",
        test_usage=0.28,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Age 24. Elite regular season stats but playoff struggles continue.",
        mechanism="Model should consistently identify lack of playoff resilience."
    ),
    LatentStarTestCase(
        name="Karl-Anthony Towns",
        season="2020-21",
        category="True Negative - Empty Stats Star",
        test_usage=0.28,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Age 25. High usage scorer but playoff performance gap remains.",
        mechanism="Final pre-age-25 season. Tests model's ability to identify persistent patterns."
    ),
    
        # ========== Category 7: The "Draft Bust" Cases (True Negatives - High Draft Picks Who Failed) ==========
        LatentStarTestCase(
            name="Markelle Fultz",
        season="2017-18",
        category="True Negative - Draft Bust",
        test_usage=0.25,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Rookie year (19.5% Usage). #1 overall pick with shooting yips.",
        mechanism="Tests model's ability to identify fatal flaws (shooting, creation) even in high draft picks."
    ),
    LatentStarTestCase(
        name="Markelle Fultz",
        season="2018-19",
        category="True Negative - Draft Bust",
        test_usage=0.25,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Age 20. Continued shooting struggles and injury issues.",
        mechanism="Persistent lack of creation tax viability and shooting ability."
    ),
    LatentStarTestCase(
        name="Markelle Fultz",
        season="2019-20",
        category="True Negative - Draft Bust",
        test_usage=0.25,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Age 21. Traded to Orlando, continued struggles.",
        mechanism="Model should identify lack of star-level potential despite draft position."
    ),
    LatentStarTestCase(
        name="Markelle Fultz",
        season="2020-21",
        category="True Negative - Draft Bust",
        test_usage=0.25,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Age 22. ACL injury, limited playing time.",
        mechanism="Tests model's handling of injury-affected seasons."
    ),
    LatentStarTestCase(
        name="Markelle Fultz",
        season="2021-22",
        category="True Negative - Draft Bust",
        test_usage=0.25,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Age 23. Return from injury, role player production.",
        mechanism="Model should identify lack of star-level potential."
    ),
    LatentStarTestCase(
        name="Markelle Fultz",
        season="2022-23",
        category="True Negative - Draft Bust",
        test_usage=0.25,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Age 24. Solid role player but not star-level.",
        mechanism="Tests consistency - model should maintain low star-level prediction."
    ),
    LatentStarTestCase(
        name="Markelle Fultz",
        season="2023-24",
        category="True Negative - Draft Bust",
        test_usage=0.25,
        expected_outcome="Victim",
        expected_star_level="Low", # <55%
        context="Age 25. Role player, never reached star potential.",
        mechanism="Final age-25 season. Tests model's ability to identify persistent lack of star traits."
    ),
    ]
    
    return test_cases

def evaluate_prediction(
    predicted_archetype: str,
    star_level_potential: float,
    expected_outcome: str,
    expected_star_level: Optional[str]
) -> Dict:
    """Evaluate if prediction matches expectations."""
    
    result = {
        'archetype_match': False,
        'star_level_match': False,
        'overall_pass': False,
        'notes': []
    }

    # Check archetype match (flexible - allow variations)
    archetype_variations = {
        'Bulldozer': ['Bulldozer (Fragile Star)', 'Bulldozer', 'King (Resilient Star)', 'King'], # Allow King for high performers
        'Victim': ['Victim (Fragile Role)', 'Victim'],
        'Sniper': ['Sniper (Resilient Role)', 'Sniper', 'Victim (Fragile Role)', 'Victim'], # Sniper/Victim often overlap at high usage for role players
        'King': ['King (Resilient Star)', 'King', 'Bulldozer (Fragile Star)', 'Bulldozer'] # Allow Bulldozer for Kings (both are stars)
    }

    # Normalize input
    clean_expected = expected_outcome.split(' ')[0]

    if clean_expected in archetype_variations:
        result['archetype_match'] = predicted_archetype in archetype_variations[clean_expected]
    else:
        result['archetype_match'] = clean_expected in predicted_archetype

    # Check star-level match
    # Thresholds:
    # - High: ≥65% 
    # - Low: <55% 
    if expected_star_level:
        if expected_star_level == "High":
            result['star_level_match'] = star_level_potential >= 0.65
            if not result['star_level_match']:
                result['notes'].append(f"Expected high star-level (≥65%), got {star_level_potential:.2%}")
        elif expected_star_level == "Medium":
            result['star_level_match'] = 0.30 <= star_level_potential < 0.70
            if not result['star_level_match']:
                result['notes'].append(f"Expected medium star-level (30-70%), got {star_level_potential:.2%}")
        elif expected_star_level == "Low":
            result['star_level_match'] = star_level_potential < 0.55
            if not result['star_level_match']:
                result['notes'].append(f"Expected low star-level (<55%), got {star_level_potential:.2%}")

    # Overall pass if star-level matches (primary metric)
    if expected_star_level:
        result['overall_pass'] = result['star_level_match']
        if not result['archetype_match']:
            result['notes'].append(f"Archetype mismatch: expected {expected_outcome}, got {predicted_archetype}")
    else:
        result['overall_pass'] = result['archetype_match']
    
    return result

def run_test_suite(apply_hard_gates: bool = True):
    """
    Run all test cases and generate comprehensive report.
    """
    
    gate_status = "ENABLED" if apply_hard_gates else "DISABLED (Trust Fall)"
    logger.info("=" * 100)
    logger.info(f"CRITICAL CASE STUDIES FOR LATENT STAR DETECTION - Gates: {gate_status}")
    logger.info("=" * 100)

    predictor = ConditionalArchetypePredictor()
    test_cases = get_test_cases()

    results = []
    summary_stats = {
        'total': len(test_cases),
        'found': 0,
        'passed': 0,
        'failed': 0,
        'by_category': {}
    }

    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'='*100}")
        logger.info(f"Test {i}/{len(test_cases)}: {test_case.name} ({test_case.season})")
        logger.info(f"Category: {test_case.category}")
        logger.info(f"{'='*100}")
        logger.info(f"Context: {test_case.context}")
        logger.info(f"Mechanism: {test_case.mechanism}")
        logger.info(f"Expected: {test_case.expected_outcome} (Star-Level: {test_case.expected_star_level})")
        logger.info(f"Test Usage: {test_case.test_usage*100:.1f}%")
        
        # Get player data
        player_data = predictor.get_player_data(test_case.name, test_case.season)
        
        if player_data is None:
            logger.warning(f"  ❌ NO DATA FOUND - Skipping")
            results.append({
                'test_number': i,
                'player_name': test_case.name,
                'season': test_case.season,
                'category': test_case.category,
                'test_usage_pct': test_case.test_usage * 100,
                'expected_outcome': test_case.expected_outcome,
                'expected_star_level': test_case.expected_star_level,
                'data_found': False,
                'predicted_archetype': None,
                'star_level_potential': None,
                'king_prob': None,
                'bulldozer_prob': None,
                'sniper_prob': None,
                'victim_prob': None,
                'archetype_match': False,
                'star_level_match': False,
                'overall_pass': False,
                'notes': 'No data found'
            })
            continue
        
        summary_stats['found'] += 1
        
        # Get actual usage if available
        actual_usage = player_data.get('USG_PCT', None)
        if actual_usage and not pd.isna(actual_usage):
            logger.info(f"  Actual Usage: {actual_usage*100:.1f}%")
        
        # Predict at test usage level
        prediction = predictor.predict_archetype_at_usage(player_data, test_case.test_usage, apply_hard_gates=apply_hard_gates)
        
        predicted_archetype = prediction['predicted_archetype']
        star_level_potential = prediction['star_level_potential']
        probs = prediction['probabilities']
        
        logger.info(f"\n  Prediction Results:")
        logger.info(f"    Predicted Archetype: {predicted_archetype}")
        logger.info(f"    Star-Level Potential: {star_level_potential:.2%}")
        logger.info(f"    Probabilities:")
        logger.info(f"      King: {probs.get('King', 0):.2%}")
        logger.info(f"      Bulldozer: {probs.get('Bulldozer', 0):.2%}")
        logger.info(f"      Sniper: {probs.get('Sniper', 0):.2%}")
        logger.info(f"      Victim: {probs.get('Victim', 0):.2%}")
        
        if prediction['confidence_flags']:
            logger.info(f"    Confidence Flags: {', '.join(prediction['confidence_flags'])}")
        
        # Evaluate prediction
        evaluation = evaluate_prediction(
            predicted_archetype,
            star_level_potential,
            test_case.expected_outcome,
            test_case.expected_star_level
        )
        
        logger.info(f"\n  Evaluation:")
        if evaluation['overall_pass']:
            logger.info(f"    ✅ PASS")
            summary_stats['passed'] += 1
        else:
            logger.info(f"    ❌ FAIL")
            summary_stats['failed'] += 1
        
        if evaluation['notes']:
            for note in evaluation['notes']:
                logger.info(f"      - {note}")
        
        # Track by category
        category = test_case.category.split(' - ')[0]  # Get main category
        if category not in summary_stats['by_category']:
            summary_stats['by_category'][category] = {'total': 0, 'passed': 0, 'failed': 0}
        summary_stats['by_category'][category]['total'] += 1
        if evaluation['overall_pass']:
            summary_stats['by_category'][category]['passed'] += 1
        else:
            summary_stats['by_category'][category]['failed'] += 1
        
        # Store results
        results.append({
            'test_number': i,
            'player_name': test_case.name,
            'season': test_case.season,
            'category': test_case.category,
            'test_usage_pct': test_case.test_usage * 100,
            'expected_outcome': test_case.expected_outcome,
            'expected_star_level': test_case.expected_star_level,
            'data_found': True,
            'predicted_archetype': predicted_archetype,
            'star_level_potential': star_level_potential,
            'king_prob': probs.get('King', 0),
            'bulldozer_prob': probs.get('Bulldozer', 0),
            'sniper_prob': probs.get('Sniper', 0),
            'victim_prob': probs.get('Victim', 0),
            'archetype_match': evaluation['archetype_match'],
            'star_level_match': evaluation['star_level_match'],
            'overall_pass': evaluation['overall_pass'],
            'notes': '; '.join(evaluation['notes']) if evaluation['notes'] else 'None',
            'confidence_flags': ', '.join(prediction['confidence_flags']) if prediction['confidence_flags'] else 'None'
        })

    # Generate summary report
    logger.info(f"\n{'='*100}")
    logger.info("SUMMARY REPORT")
    logger.info(f"{'='*100}")
    logger.info(f"Total Test Cases: {summary_stats['total']}")
    logger.info(f"Data Found: {summary_stats['found']}")
    logger.info(f"Passed: {summary_stats['passed']}")
    logger.info(f"Failed: {summary_stats['failed']}")
    logger.info(f"Pass Rate: {summary_stats['passed']/summary_stats['found']*100:.1f}%" if summary_stats['found'] > 0 else "N/A")

    logger.info(f"\nBy Category:")
    for category, stats in summary_stats['by_category'].items():
        pass_rate = stats['passed']/stats['total']*100 if stats['total'] > 0 else 0
        logger.info(f"  {category}: {stats['passed']}/{stats['total']} passed ({pass_rate:.1f}%)")

    # Save detailed results
    df_results = pd.DataFrame(results)
    output_path = Path("results") / "latent_star_test_cases_results.csv"
    df_results.to_csv(output_path, index=False)
    logger.info(f"\nDetailed results saved to: {output_path}")

    # Generate markdown report
    report_filename = "latent_star_test_cases_report_trust_fall.md" if not apply_hard_gates else "latent_star_test_cases_report.md"
    generate_markdown_report(df_results, summary_stats, output_path.parent / report_filename, apply_hard_gates)

    return df_results, summary_stats

def generate_markdown_report(df_results: pd.DataFrame, summary_stats: Dict, output_path: Path, apply_hard_gates: bool = True):
    """Generate a markdown report of test results."""
    
    with open(output_path, 'w') as f:
        f.write("# Latent Star Detection: Critical Case Studies Test Report\n\n")
        f.write(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Test Cases**: {summary_stats['total']}\n")
        f.write(f"- **Data Found**: {summary_stats['found']}\n")
        f.write(f"- **Passed**: {summary_stats['passed']}\n")
        f.write(f"- **Failed**: {summary_stats['failed']}\n")
        if summary_stats['found'] > 0:
            f.write(f"- **Pass Rate**: {summary_stats['passed']/summary_stats['found']*100:.1f}%\n")
        f.write("\n")
        
        f.write("## Results by Category\n\n")
        for category, stats in summary_stats['by_category'].items():
            pass_rate = stats['passed']/stats['total']*100 if stats['total'] > 0 else 0
            f.write(f"### {category}\n")
            f.write(f"- **Total**: {stats['total']}\n")
            f.write(f"- **Passed**: {stats['passed']}\n")
            f.write(f"- **Failed**: {stats['failed']}\n")
            f.write(f"- **Pass Rate**: {pass_rate:.1f}%\n\n")
        
        f.write("## Detailed Results\n\n")
        f.write("| Test | Player | Season | Category | Expected | Predicted | Star-Level | Pass |\n")
        f.write("|------|--------|--------|----------|----------|-----------|------------|------|\n")
        
        for _, row in df_results.iterrows():
            if not row['data_found']:
                status = "❌ No Data"
            elif row['overall_pass']:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            
            f.write(f"| {row['test_number']} | {row['player_name']} | {row['season']} | {row['category']} | "
                   f"{row['expected_outcome']} ({row['expected_star_level']}) | "
                   f"{row['predicted_archetype']} | {row['star_level_potential']:.2%} | {status} |\n")
        
        f.write("\n## Notes\n\n")
        failed_tests = df_results[~df_results['overall_pass'] & df_results['data_found']]
        if len(failed_tests) > 0:
            f.write("### Failed Tests\n\n")
            for _, row in failed_tests.iterrows():
                f.write(f"**{row['player_name']} ({row['season']})**: {row['notes']}\n\n")
        
        missing_data = df_results[~df_results['data_found']]
        if len(missing_data) > 0:
            f.write("### Missing Data\n\n")
            for _, row in missing_data.iterrows():
                f.write(f"- **{row['player_name']} ({row['season']})**: No data found in dataset\n\n")

    logger.info(f"Markdown report saved to: {output_path}")

if __name__ == "__main__":
    import sys
    
    # Check for Trust Fall flag
    apply_hard_gates = True
    if len(sys.argv) > 1 and sys.argv[1] == "--trust-fall":
        apply_hard_gates = False
        logger.info("🔬 TRUST FALL EXPERIMENT: Running with hard gates DISABLED")
    
    results, stats = run_test_suite(apply_hard_gates=apply_hard_gates)