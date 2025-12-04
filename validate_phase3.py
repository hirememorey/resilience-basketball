"""
Phase 3 Validation Testing

This script validates that Phase 3 fixes improve model performance on critical test cases.
It runs the test suite with different Phase 3 configurations:
1. Baseline (all fixes disabled)
2. Fix #1 only (Usage-Dependent Weighting)
3. Fix #2 only (Context-Adjusted Efficiency)
4. Fix #3 only (Fragility Gate)
5. All fixes together

Based on PHASE3_VALIDATION_PLAN.md
"""

import pandas as pd
import sys
from pathlib import Path
import logging
from typing import Dict, List
from datetime import datetime

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))
from predict_conditional_archetype import ConditionalArchetypePredictor
from test_latent_star_cases import get_test_cases, evaluate_prediction, LatentStarTestCase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Phase3Validator:
    """Validates Phase 3 fixes on test cases."""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.predictor = ConditionalArchetypePredictor()
        self.test_cases = get_test_cases()
        
    def run_test_configuration(
        self,
        config_name: str,
        apply_fix1: bool = False,
        apply_fix2: bool = False,
        apply_fix3: bool = False
    ) -> pd.DataFrame:
        """
        Run test suite with specific Phase 3 fix configuration.
        
        Args:
            config_name: Name of configuration (e.g., "Baseline", "Fix #1 Only")
            apply_fix1: Apply Usage-Dependent Feature Weighting
            apply_fix2: Apply Context-Adjusted Efficiency
            apply_fix3: Apply Fragility Gate
        
        Returns:
            DataFrame with test results
        """
        logger.info(f"\n{'='*100}")
        logger.info(f"Running Configuration: {config_name}")
        logger.info(f"  Fix #1 (Usage-Dependent Weighting): {apply_fix1}")
        logger.info(f"  Fix #2 (Context Adjustment): {apply_fix2}")
        logger.info(f"  Fix #3 (Fragility Gate): {apply_fix3}")
        logger.info(f"{'='*100}\n")
        
        # Note: All fixes are applied together in the current implementation
        # We'll need to modify the code to support individual toggles
        # For now, we'll use apply_phase3_fixes to control all fixes
        apply_phase3_fixes = apply_fix1 or apply_fix2 or apply_fix3
        
        results = []
        
        for i, test_case in enumerate(self.test_cases, 1):
            logger.info(f"Test {i}/{len(self.test_cases)}: {test_case.name} ({test_case.season})")
            
            # Get player data
            player_data = self.predictor.get_player_data(test_case.name, test_case.season)
            
            if player_data is None:
                logger.warning(f"  ❌ NO DATA FOUND - Skipping")
                results.append({
                    'test_number': i,
                    'player_name': test_case.name,
                    'season': test_case.season,
                    'category': test_case.category,
                    'config': config_name,
                    'data_found': False,
                    'predicted_archetype': None,
                    'star_level_potential': None,
                    'overall_pass': False,
                    'notes': 'No data found'
                })
                continue
            
            # Predict at test usage level
            # Note: Current implementation applies all fixes together
            # We'll need to modify prepare_features to support individual toggles
            prediction = self.predictor.predict_archetype_at_usage(
                player_data, 
                test_case.test_usage,
                apply_phase3_fixes=apply_phase3_fixes
            )
            
            predicted_archetype = prediction['predicted_archetype']
            star_level_potential = prediction['star_level_potential']
            
            # Evaluate prediction
            evaluation = evaluate_prediction(
                predicted_archetype,
                star_level_potential,
                test_case.expected_outcome,
                test_case.expected_star_level
            )
            
            # Store results
            results.append({
                'test_number': i,
                'player_name': test_case.name,
                'season': test_case.season,
                'category': test_case.category,
                'config': config_name,
                'test_usage_pct': test_case.test_usage * 100,
                'expected_outcome': test_case.expected_outcome,
                'expected_star_level': test_case.expected_star_level,
                'data_found': True,
                'predicted_archetype': predicted_archetype,
                'star_level_potential': star_level_potential,
                'king_prob': prediction['probabilities'].get('King', 0),
                'bulldozer_prob': prediction['probabilities'].get('Bulldozer', 0),
                'sniper_prob': prediction['probabilities'].get('Sniper', 0),
                'victim_prob': prediction['probabilities'].get('Victim', 0),
                'archetype_match': evaluation['archetype_match'],
                'star_level_match': evaluation['star_level_match'],
                'overall_pass': evaluation['overall_pass'],
                'notes': '; '.join(evaluation['notes']) if evaluation['notes'] else 'None',
                'phase3_flags': ', '.join(prediction.get('phase3_flags', [])) if prediction.get('phase3_flags') else 'None'
            })
            
            status = "✅ PASS" if evaluation['overall_pass'] else "❌ FAIL"
            logger.info(f"  {status} - Star-Level: {star_level_potential:.2%}, Archetype: {predicted_archetype}")
        
        return pd.DataFrame(results)
    
    def run_all_configurations(self) -> Dict[str, pd.DataFrame]:
        """Run all test configurations."""
        results = {}
        
        # 1. Baseline (all fixes disabled)
        results['baseline'] = self.run_test_configuration(
            "Baseline",
            apply_fix1=False,
            apply_fix2=False,
            apply_fix3=False
        )
        
        # 2. All fixes together (current implementation)
        results['all_fixes'] = self.run_test_configuration(
            "All Fixes",
            apply_fix1=True,
            apply_fix2=True,
            apply_fix3=True
        )
        
        return results
    
    def compare_configurations(self, results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Compare results across configurations."""
        comparison = []
        
        # Get baseline results
        baseline = results['baseline']
        all_fixes = results['all_fixes']
        
        # For each test case, compare baseline vs all fixes
        for test_num in range(1, len(self.test_cases) + 1):
            baseline_row = baseline[baseline['test_number'] == test_num].iloc[0]
            fixes_row = all_fixes[all_fixes['test_number'] == test_num].iloc[0]
            
            if not baseline_row['data_found'] or not fixes_row['data_found']:
                continue
            
            comparison.append({
                'test_number': test_num,
                'player_name': baseline_row['player_name'],
                'season': baseline_row['season'],
                'category': baseline_row['category'],
                'baseline_star_level': baseline_row['star_level_potential'],
                'baseline_archetype': baseline_row['predicted_archetype'],
                'baseline_pass': baseline_row['overall_pass'],
                'all_fixes_star_level': fixes_row['star_level_potential'],
                'all_fixes_archetype': fixes_row['predicted_archetype'],
                'all_fixes_pass': fixes_row['overall_pass'],
                'star_level_delta': fixes_row['star_level_potential'] - baseline_row['star_level_potential'],
                'improved': fixes_row['overall_pass'] and not baseline_row['overall_pass'],
                'regressed': baseline_row['overall_pass'] and not fixes_row['overall_pass'],
                'baseline_notes': baseline_row['notes'],
                'all_fixes_notes': fixes_row['notes']
            })
        
        return pd.DataFrame(comparison)
    
    def generate_summary_report(self, results: Dict[str, pd.DataFrame], comparison: pd.DataFrame):
        """Generate summary report."""
        baseline = results['baseline']
        all_fixes = results['all_fixes']
        
        baseline_passed = baseline[baseline['data_found']]['overall_pass'].sum()
        baseline_total = baseline[baseline['data_found']].shape[0]
        baseline_rate = baseline_passed / baseline_total * 100 if baseline_total > 0 else 0
        
        fixes_passed = all_fixes[all_fixes['data_found']]['overall_pass'].sum()
        fixes_total = all_fixes[all_fixes['data_found']].shape[0]
        fixes_rate = fixes_passed / fixes_total * 100 if fixes_total > 0 else 0
        
        improved = comparison['improved'].sum()
        regressed = comparison['regressed'].sum()
        
        logger.info(f"\n{'='*100}")
        logger.info("PHASE 3 VALIDATION SUMMARY")
        logger.info(f"{'='*100}")
        logger.info(f"\nBaseline (No Fixes):")
        logger.info(f"  Passed: {baseline_passed}/{baseline_total} ({baseline_rate:.1f}%)")
        logger.info(f"\nAll Fixes:")
        logger.info(f"  Passed: {fixes_passed}/{fixes_total} ({fixes_rate:.1f}%)")
        logger.info(f"\nImprovement:")
        logger.info(f"  Improved: {improved} cases")
        logger.info(f"  Regressed: {regressed} cases")
        logger.info(f"  Net Change: {fixes_passed - baseline_passed} cases")
        
        # Save detailed comparison
        output_path = self.results_dir / "phase3_validation_comparison.csv"
        comparison.to_csv(output_path, index=False)
        logger.info(f"\nDetailed comparison saved to: {output_path}")
        
        # Generate markdown report
        self._generate_markdown_report(baseline, all_fixes, comparison, baseline_rate, fixes_rate, improved, regressed)
    
    def _generate_markdown_report(
        self,
        baseline: pd.DataFrame,
        all_fixes: pd.DataFrame,
        comparison: pd.DataFrame,
        baseline_rate: float,
        fixes_rate: float,
        improved: int,
        regressed: int
    ):
        """Generate markdown validation report."""
        output_path = self.results_dir / "phase3_validation_report.md"
        
        with open(output_path, 'w') as f:
            f.write("# Phase 3 Validation Report\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write(f"- **Baseline Pass Rate**: {baseline_rate:.1f}%\n")
            f.write(f"- **All Fixes Pass Rate**: {fixes_rate:.1f}%\n")
            f.write(f"- **Improvement**: {fixes_rate - baseline_rate:.1f} percentage points\n")
            f.write(f"- **Cases Improved**: {improved}\n")
            f.write(f"- **Cases Regressed**: {regressed}\n\n")
            
            f.write("## Results by Configuration\n\n")
            f.write("### Baseline (No Fixes)\n\n")
            f.write(f"- **Passed**: {baseline[baseline['data_found']]['overall_pass'].sum()}/{baseline[baseline['data_found']].shape[0]}\n")
            f.write(f"- **Pass Rate**: {baseline_rate:.1f}%\n\n")
            
            f.write("### All Fixes\n\n")
            f.write(f"- **Passed**: {all_fixes[all_fixes['data_found']]['overall_pass'].sum()}/{all_fixes[all_fixes['data_found']].shape[0]}\n")
            f.write(f"- **Pass Rate**: {fixes_rate:.1f}%\n\n")
            
            f.write("## Detailed Comparison\n\n")
            f.write("| Test | Player | Season | Category | Baseline | All Fixes | Delta | Status |\n")
            f.write("|------|--------|--------|----------|----------|-----------|-------|--------|\n")
            
            for _, row in comparison.iterrows():
                baseline_status = "✅" if row['baseline_pass'] else "❌"
                fixes_status = "✅" if row['all_fixes_pass'] else "❌"
                delta_str = f"{row['star_level_delta']:+.2%}"
                
                if row['improved']:
                    status = "🔼 Improved"
                elif row['regressed']:
                    status = "🔽 Regressed"
                else:
                    status = "➡️ No Change"
                
                f.write(f"| {row['test_number']} | {row['player_name']} | {row['season']} | {row['category']} | "
                       f"{baseline_status} {row['baseline_star_level']:.1%} | {fixes_status} {row['all_fixes_star_level']:.1%} | "
                       f"{delta_str} | {status} |\n")
            
            f.write("\n## Improved Cases\n\n")
            improved_cases = comparison[comparison['improved']]
            if len(improved_cases) > 0:
                for _, row in improved_cases.iterrows():
                    f.write(f"- **{row['player_name']} ({row['season']})**: {row['baseline_star_level']:.1%} → {row['all_fixes_star_level']:.1%}\n")
            else:
                f.write("No cases improved.\n")
            
            f.write("\n## Regressed Cases\n\n")
            regressed_cases = comparison[comparison['regressed']]
            if len(regressed_cases) > 0:
                for _, row in regressed_cases.iterrows():
                    f.write(f"- **{row['player_name']} ({row['season']})**: {row['baseline_star_level']:.1%} → {row['all_fixes_star_level']:.1%}\n")
            else:
                f.write("No cases regressed.\n")
        
        logger.info(f"Markdown report saved to: {output_path}")


def main():
    """Run Phase 3 validation."""
    logger.info("=" * 100)
    logger.info("PHASE 3 VALIDATION TESTING")
    logger.info("=" * 100)
    
    validator = Phase3Validator()
    
    # Run all configurations
    results = validator.run_all_configurations()
    
    # Compare configurations
    comparison = validator.compare_configurations(results)
    
    # Generate summary report
    validator.generate_summary_report(results, comparison)
    
    logger.info("\n✅ Phase 3 validation complete!")


if __name__ == "__main__":
    main()

