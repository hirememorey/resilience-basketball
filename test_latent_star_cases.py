"""
Critical Case Studies for Latent Star Detection

This script tests the model on critical case studies that probe different
failure modes and validate the model's ability to distinguish:
- Good breakouts (should predict high star-level = Bulldozer)
- Mediocre breakouts (should predict low star-level = Victim)
- System players (should predict Sniper at high usage)
- Context-dependent players (should account for teammate gravity)
- Max contract mistakes (players paid like stars but not playoff stars)
- Comparison cases (similar caliber players with different playoff outcomes)

Based on first principles framework and user insights that breakouts typically
become "Bulldozer" (not "King") when scaled up.
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
        self.expected_star_level = expected_star_level  # "High" (>70%), "Medium" (30-70%), "Low" (<30%)
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
            expected_outcome="Bulldozer",  # Good breakout, not King
            expected_star_level="High",  # >70%
            context="Rookie year. 18.3% Usage. Role player behind Lou Williams and Danilo Gallinari.",
            mechanism="Should see elite Driving/Physicality Vector (Rim Pressure) even at low volume. Tests if model overvalues shooting range and undervalues rim pressure."
        ),
        LatentStarTestCase(
            name="Victor Oladipo",
            season="2016-17",
            category="True Positive - Latent Star",
            test_usage=0.30,
            expected_outcome="Bulldozer",  # Good breakout, not King
            expected_star_level="High",  # >70%
            context="Russell Westbrook's MVP usage-hole year. Oladipo was relegated to a spot-up shooter (21% Usage).",
            mechanism="Did he maintain Creation Vector efficiency on the few self-created shots? Tests if model can see Creation Vector through role constraints."
        ),
        LatentStarTestCase(
            name="Jalen Brunson",
            season="2020-21",
            category="True Positive - Latent Star",
            test_usage=0.32,
            expected_outcome="Bulldozer",  # Already validated
            expected_star_level="High",  # >70% (already validated at 94.02%)
            context="19.6% Usage. Backup to Luka Dončić.",
            mechanism="Gold Standard validation. High Creation Efficiency + High Leverage Resilience should trigger high star-level even at low usage."
        ),
        
        # ========== Category 2: The "Mirage" Breakouts (False Positives) ==========
        LatentStarTestCase(
            name="Jordan Poole",
            season="2021-22",
            category="False Positive - Mirage Breakout",
            test_usage=0.30,
            expected_outcome="Victim",  # Efficiency collapses at scale
            expected_star_level="Low",  # <30%
            context="26% Usage, 60% TS. Looked like the next Curry.",
            mechanism="Should detect low Pressure Resilience. Poole likely took many 'Open' shots (Stephen Curry gravity) and few 'Late Clock/High Pressure' shots."
        ),
        LatentStarTestCase(
            name="Talen Horton-Tucker",
            season="2020-21",
            category="False Positive - Mirage Breakout",
            test_usage=0.25,
            expected_outcome="Victim",  # Can't maintain efficiency
            expected_star_level="Low",  # <30%
            context="18% Usage. The 'Baby LeBron' hype. Elite rim pressure numbers on low volume.",
            mechanism="Should see that while Physicality Vector was high, Creation Efficiency was actually poor. Should predict 'Bulldozer' (Empty Calories) at best."
        ),
        
        # ========== Category 3: The "System Players" (The Ceiling Test) ==========
        LatentStarTestCase(
            name="Tyus Jones",
            season="2021-22",
            category="System Player - Ceiling Test",
            test_usage=0.25,
            expected_outcome="Sniper",  # Good role player, not scalable
            expected_star_level="Low",  # <30%
            context="The 'God of Assist-to-Turnover Ratio.' Elite efficiency metrics.",
            mechanism="Should predict 'Sniper' or 'Victim' at high usage. If it predicts 'King' just because he doesn't turn the ball over, model is overweighting Plasticity and underweighting Creation/Physicality."
        ),
        
        # ========== Category 4: The "Usage Shock" Test (The outlier) ==========
        LatentStarTestCase(
            name="Mikal Bridges",
            season="2021-22",
            category="Usage Shock - Hardest Test",
            test_usage=0.28,
            expected_outcome="Bulldozer",  # Border with King
            expected_star_level="High",  # >70%
            context="Elite 3-and-D (15% Usage). Later became Primary Option (27% Usage).",
            mechanism="Hardest test. Can the model see a '3-and-D' player and correctly identify that he has the Creation Vector chops to scale up, even if he didn't use them in Phoenix?"
        ),
        
        # ========== Additional Tests ==========
        LatentStarTestCase(
            name="Lauri Markkanen",
            season="2021-22",
            category="True Positive - Wrong Role",
            test_usage=0.26,
            expected_outcome="Bulldozer",  # Good breakout, not King
            expected_star_level="High",  # >70%
            context="Played as a 'Tower' Small Forward alongside Mobley/Allen. 19.4% Usage, primarily a spot-up threat.",
            mechanism="Did the model see the Creation Vector (ability to shoot off the dribble/drive) hidden inside a 'Catch-and-Shoot' role?"
        ),
        LatentStarTestCase(
            name="Christian Wood",
            season="2020-21",
            category="False Positive - Empty Calories",
            test_usage=0.26,
            expected_outcome="Victim",  # Garbage time efficiency
            expected_star_level="Low",  # <30%
            context="Put up massive stats (21 PPG, 26% Usage) on a tanking team. TS% was elite (59%).",
            mechanism="Tests the Leverage Vector (Clutch) and Pressure Vector. Wood likely excelled in 'Low Leverage' moments but crumbled in 'High Leverage' moments."
        ),
        LatentStarTestCase(
            name="Jamal Murray",
            season="2018-19",
            category="True Positive - Playoff Riser",
            test_usage=0.30,
            expected_outcome="Bulldozer",  # Or King if Leverage Vector is strong
            expected_star_level="High",  # >70%
            context="A solid but inconsistent RS player (18 PPG, 53% TS). Never an All-Star.",
            mechanism="Ultimate test of 'Resilience.' Murray's RS efficiency is often average. His Clutch efficiency is elite. Tests if model values Leverage Vector over Consistency."
        ),
        LatentStarTestCase(
            name="D'Angelo Russell",
            season="2018-19",
            category="False Positive - Fool's Gold",
            test_usage=0.31,
            expected_outcome="Victim",  # Physicality fragility
            expected_star_level="Low",  # <30%
            context="An All-Star season. Led team to playoffs. Usage 31%.",
            mechanism="Tests if model detects Physicality fragility. Russell relies on tough mid-range jumpers and floaters. Has extremely low Rim Pressure Resilience."
        ),
        LatentStarTestCase(
            name="Desmond Bane",
            season="2021-22",
            category="True Positive - Secondary Creator",
            test_usage=0.27,
            expected_outcome="Bulldozer",  # Good breakout, not King
            expected_star_level="High",  # >70%
            context="Elite shooter (43% 3PT), moderate usage (22%). Viewed as a 'Klay Thompson' type.",
            mechanism="Can the model distinguish a 'Shooter' from a 'Scorer'? Should see his Creation Vector (drives per game, pull-up efficiency) and predict that his efficiency is robust enough to scale."
        ),
        LatentStarTestCase(
            name="Tobias Harris",
            season="2016-17",
            category="False Positive - Max Contract Mistake",
            test_usage=0.28,
            expected_outcome="Victim",  # Not a true star despite max contract
            expected_star_level="Low",  # <30%
            context="Received a max contract but was not a true playoff star. High usage (25-28%) but efficiency and impact don't scale to playoff success.",
            mechanism="Tests if model can identify players who get paid like stars but don't have the Creation/Leverage/Physicality vectors to succeed in playoffs. Should detect lack of self-creation ability or physicality floor."
        ),
        LatentStarTestCase(
            name="Domantas Sabonis",
            season="2021-22",
            category="False Positive - Comparison Case",
            test_usage=0.28,
            expected_outcome="Victim",  # Not a playoff star
            expected_star_level="Low",  # <30%
            context="Traded 1-1 for Tyrese Haliburton in February 2022. Time has shown Haliburton is a true playoff star while Sabonis has not been. Both were All-Stars, but Sabonis lacks playoff resilience.",
            mechanism="Critical comparison test. Both players were similar caliber (All-Stars), but model should identify that Sabonis lacks the stress vectors (likely Physicality or Creation) needed for playoff success. Tests if model can distinguish regular season production from playoff capability."
        ),
        LatentStarTestCase(
            name="Tyrese Haliburton",
            season="2021-22",
            category="True Positive - Comparison Case",
            test_usage=0.28,
            expected_outcome="Bulldozer",  # True playoff star
            expected_star_level="High",  # >70%
            context="Traded 1-1 for Domantas Sabonis in February 2022. Time has shown Haliburton is a true playoff star while Sabonis has not been. Both were All-Stars, but Haliburton has elite Creation and Leverage vectors.",
            mechanism="Critical comparison test. Model should identify that Haliburton has the stress vectors (Creation, Leverage, Pressure) needed for playoff success. Should show higher star-level than Sabonis despite similar regular season production."
        ),
        LatentStarTestCase(
            name="Tyrese Maxey",
            season="2021-22",
            category="True Positive - Latent Star",
            test_usage=0.28,
            expected_outcome="Bulldozer",  # True star
            expected_star_level="High",  # >70%
            context="22.2% Usage in 2021-22. Broke out to 27.3% usage in 2023-24. Elite Creation Vector and Leverage Vector even at lower usage.",
            mechanism="Should identify high Creation efficiency and positive Leverage USG Delta. Tests if model can see star potential through role constraints. Maxey maintained elite efficiency on self-created shots even at lower usage."
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
        'Bulldozer': ['Bulldozer (Fragile Star)', 'Bulldozer'],
        'Victim': ['Victim (Fragile Role)', 'Victim'],
        'Sniper': ['Sniper (Resilient Role)', 'Sniper'],
        'King': ['King (Resilient Star)', 'King']
    }
    
    if expected_outcome in archetype_variations:
        result['archetype_match'] = predicted_archetype in archetype_variations[expected_outcome]
    else:
        result['archetype_match'] = expected_outcome in predicted_archetype
    
    # Check star-level match
    if expected_star_level:
        if expected_star_level == "High":
            result['star_level_match'] = star_level_potential >= 0.70
            if not result['star_level_match']:
                result['notes'].append(f"Expected high star-level (≥70%), got {star_level_potential:.2%}")
        elif expected_star_level == "Medium":
            result['star_level_match'] = 0.30 <= star_level_potential < 0.70
            if not result['star_level_match']:
                result['notes'].append(f"Expected medium star-level (30-70%), got {star_level_potential:.2%}")
        elif expected_star_level == "Low":
            result['star_level_match'] = star_level_potential < 0.30
            if not result['star_level_match']:
                result['notes'].append(f"Expected low star-level (<30%), got {star_level_potential:.2%}")
    
    # Overall pass if both match (or if star-level is the primary signal)
    if expected_star_level:
        # For these tests, star-level is more important than exact archetype
        result['overall_pass'] = result['star_level_match']
        if not result['archetype_match']:
            result['notes'].append(f"Archetype mismatch: expected {expected_outcome}, got {predicted_archetype}")
    else:
        result['overall_pass'] = result['archetype_match']
    
    return result


def run_test_suite():
    """Run all test cases and generate comprehensive report."""
    
    logger.info("=" * 100)
    logger.info("CRITICAL CASE STUDIES FOR LATENT STAR DETECTION")
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
        prediction = predictor.predict_archetype_at_usage(player_data, test_case.test_usage)
        
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
    generate_markdown_report(df_results, summary_stats, output_path.parent / "latent_star_test_cases_report.md")
    
    return df_results, summary_stats


def generate_markdown_report(df_results: pd.DataFrame, summary_stats: Dict, output_path: Path):
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
    results, stats = run_test_suite()

