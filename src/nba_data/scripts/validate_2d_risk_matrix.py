"""
Validate 2D Risk Matrix (Telescope + Crucible).

This script validates the newly generated "Two-Clock" system against the
canonical "Latent Star" test suite.

It does NOT run inference. It validates the artifacts produced by
`predict_2d_risk_matrix.py` against the ground truth expectations.

Output:
    results/2d_risk_matrix_test_results.csv
    results/2d_risk_matrix_test_report.md
"""

import pandas as pd
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

# Import Test Cases
try:
    from tests.validation.test_latent_star_cases import get_test_cases, LatentStarTestCase
except ImportError:
    # Fallback if import fails (e.g. structure issues), define minimal class/cases locally
    # But ideally this works.
    pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def load_predictions():
    """Load the final 2D Risk Matrix predictions."""
    path = Path("results/risk_matrix_analysis.csv")
    if not path.exists():
        logger.error(f"Predictions not found at {path}. Run predict_2d_risk_matrix.py first.")
        sys.exit(1)
    df = pd.read_csv(path)
    # create lookup key
    df['LOOKUP_KEY'] = df['PLAYER_NAME'] + "_" + df['SEASON']
    return df

def evaluate_case(test_case, df_preds: pd.DataFrame) -> Dict:
    """Evaluate a single test case."""
    key = f"{test_case.name}_{test_case.season}"
    match = df_preds[df_preds['LOOKUP_KEY'] == key]
    
    result = {
        'test_name': test_case.name,
        'season': test_case.season,
        'category': test_case.category,
        'expected_risk': test_case.expected_risk_category,
        'actual_risk': None,
        'crucible': None,
        'telescope': None,
        'pass': False,
        'note': ""
    }
    
    if match.empty:
        result['note'] = "Player/Season not found in dataset"
        return result
        
    row = match.iloc[0]
    result['actual_risk'] = row['RISK_CATEGORY']
    result['crucible'] = row['CRUCIBLE_SCORE']
    result['telescope'] = row['TELESCOPE_SCORE']
    
    # Validation Logic
    # 1. Direct Category Match
    if test_case.expected_risk_category:
        # Flexible matching for "Latent Star" vs "Franchise Cornerstone" overlap
        # Sometimes a Latent Star is so good they are a Franchise Cornerstone.
        # And Franchise Cornerstones are effectively Latent Stars that arrived.
        
        expected = test_case.expected_risk_category
        actual = row['RISK_CATEGORY']
        
        if expected == actual:
            result['pass'] = True
        elif expected == "Latent Star" and actual == "Franchise Cornerstone":
            result['pass'] = True
            result['note'] = "Exceeded expectations (Franchise Cornerstone)"
        elif expected == "Franchise Cornerstone" and actual == "Latent Star":
            # This is technically a miss on "Viability" (Crucible too low), but correct on Potential.
            # Let's count as Partial/Fail but note it.
            result['pass'] = False
            result['note'] = "Crucible score too low (Viability)"
        elif expected in ["Luxury Component", "Win-Now Piece"] and actual in ["Luxury Component", "Win-Now Piece"]:
             # These terms are somewhat fluid in the old test suite vs new matrix
             # Old "Luxury Component" meant High Performance + High Dependence.
             # New "Win-Now Piece" means High Crucible (Viable) + Low Telescope (Capped).
             # Old "Luxury" mapped to "High Risk" dependence.
             # Let's be strict for now.
             result['pass'] = False
        else:
            result['pass'] = False
            
    else:
        # Backward compatibility for old test cases without risk category
        # Use expected_outcome/star_level proxies
        result['note'] = "No expected risk category defined"
        
    return result

def generate_report(results: List[Dict]):
    """Generate Markdown report."""
    passed = sum(1 for r in results if r['pass'])
    total = len(results)
    found = sum(1 for r in results if r['actual_risk'] is not None)
    
    md = [
        "# 2D Risk Matrix Validation Report",
        f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d')}",
        "",
        "## Summary",
        f"- **Total Cases**: {total}",
        f"- **Data Found**: {found}",
        f"- **Passed**: {passed}",
        f"- **Pass Rate**: {passed/found*100:.1f}%" if found > 0 else "- **Pass Rate**: N/A",
        "",
        "## Detailed Results",
        "| Player | Season | Type | Expected | Actual | Crucible (Viability) | Telescope (Potential) | Pass |",
        "|---|---|---|---|---|---|---|---|"
    ]
    
    for r in results:
        status = "✅" if r['pass'] else "❌"
        if r['actual_risk'] is None:
            status = "⚠️ No Data"
            
        c_score = f"{r['crucible']:.2f}" if r['crucible'] is not None else "-"
        t_score = f"{r['telescope']:.2f}" if r['telescope'] is not None else "-"
        
        md.append(f"| {r['test_name']} | {r['season']} | {r['category']} | {r['expected_risk']} | {r['actual_risk']} | {c_score} | {t_score} | {status} |")
        
    output_path = Path("results/2d_risk_matrix_test_report.md")
    with open(output_path, 'w') as f:
        f.write("\n".join(md))
    
    # Also save CSV
    pd.DataFrame(results).to_csv("results/2d_risk_matrix_test_results.csv", index=False)
    logger.info(f"Report saved to {output_path}")

def main():
    logger.info("Starting Validation...")
    
    # 1. Load Data
    df_preds = load_predictions()
    logger.info(f"Loaded {len(df_preds)} predictions.")
    
    # 2. Get Test Cases
    try:
        from tests.validation.test_latent_star_cases import get_test_cases
        cases = get_test_cases()
        logger.info(f"Loaded {len(cases)} test cases.")
    except ImportError:
        logger.error("Could not import test cases. Check path.")
        return

    # 3. Evaluate
    results = []
    for case in cases:
        # Only evaluate cases that have an expected_risk_category
        if case.expected_risk_category:
            res = evaluate_case(case, df_preds)
            results.append(res)
            
            log_icon = "✅" if res['pass'] else "❌"
            if res['actual_risk'] is None: log_icon = "⚠️"
            
            logger.info(f"{log_icon} {case.name} ({case.season}): Exp '{case.expected_risk_category}' vs Act '{res['actual_risk']}'")
            
    # 4. Report
    generate_report(results)

if __name__ == "__main__":
    main()

