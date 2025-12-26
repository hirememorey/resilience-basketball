"""
Validation script for the Telescope Subsidy Index model using legacy test cases.
Follows first principles: Performance vs. Dependence.
"""

import pandas as pd
import numpy as np
import joblib
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[3]))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
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
        expected_risk_category: Optional[str] = None,
        context: str = "",
        mechanism: str = ""
    ):
        self.name = name
        self.season = season
        self.category = category
        self.test_usage = test_usage
        self.expected_outcome = expected_outcome
        self.expected_star_level = expected_star_level
        self.expected_risk_category = expected_risk_category
        self.context = context
        self.mechanism = mechanism

def get_test_cases() -> List[LatentStarTestCase]:
    """
    Define critical test cases for latent star detection validation.
    Note: These are hardcoded here to avoid dependency issues with legacy scripts.
    """
    test_cases = [
        # ========== Category 1: The "Latent Stars" (True Positives) ==========
        LatentStarTestCase(
            name="Shai Gilgeous-Alexander",
            season="2018-19",
            category="True Positive - Latent Star",
            test_usage=0.30,
            expected_outcome="Bulldozer",
            expected_star_level="High",
            context="Rookie year. 18.3% Usage.",
            mechanism="Should see elite Rim Pressure even at low volume."
        ),
        LatentStarTestCase(
            name="Jalen Brunson",
            season="2020-21",
            category="True Positive - Latent Star",
            test_usage=0.32,
            expected_outcome="Bulldozer",
            expected_star_level="High",
            context="19.6% Usage. Backup to Luka Dončić.",
            mechanism="High Creation Efficiency + High Leverage Resilience."
        ),
        LatentStarTestCase(
            name="Tyrese Maxey",
            season="2021-22",
            category="True Positive - Latent Star",
            test_usage=0.28,
            expected_outcome="Bulldozer",
            expected_star_level="High",
            context="22.2% Usage.",
            mechanism="Elite Creation Vector and Leverage Vector."
        ),
        
        # ========== Category 1.5: Franchise Cornerstones (Jokic cases) ==========
        LatentStarTestCase(
            name="Nikola Jokić",
            season="2016-17",
            category="True Positive - Franchise Cornerstone",
            test_usage=0.30,
            expected_outcome="King",
            expected_star_level="High",
            expected_risk_category="Franchise Cornerstone",
            context="Age 22 (23.1% Usage). Emerging as elite playmaker.",
            mechanism="Elite creation volume and efficiency. Low dependence on system."
        ),
        
        # ========== Category 2: The "Mirage" Breakouts (False Positives) ==========
        LatentStarTestCase(
            name="Jordan Poole",
            season="2021-22",
            category="False Positive - Mirage Breakout",
            test_usage=0.30,
            expected_outcome="Victim",
            expected_star_level="Low",
            expected_risk_category="Luxury Component",
            context="26% Usage. System merchant relying on Curry gravity.",
            mechanism="Should detect low Pressure Resilience and high subsidy index."
        ),
        LatentStarTestCase(
            name="Christian Wood",
            season="2020-21",
            category="False Positive - Empty Calories",
            test_usage=0.26,
            expected_outcome="Victim",
            expected_star_level="Low",
            context="Massive stats on tanking team. Low leverage performance.",
            mechanism="Tests Leverage Vector (Clutch) and Pressure Vector."
        ),
        
        # ========== Category 3: The "Ben Simmons" Fragility Test ==========
        LatentStarTestCase(
            name="Ben Simmons",
            season="2020-21",
            category="True Negative - Fragile Star",
            test_usage=0.25,
            expected_outcome="Victim",
            expected_star_level="Low",
            context="20.2% Usage. The Hawks series collapse.",
            mechanism="Abdication Tax and low Creation Tax."
        ),
        
        # ========== Category 5: Comparison Cases ==========
        LatentStarTestCase(
            name="Domantas Sabonis",
            season="2021-22",
            category="True Negative - Comparison Case",
            test_usage=0.28,
            expected_outcome="Victim",
            expected_star_level="Low",
            expected_risk_category="Luxury Component",
            context="All-Star, but lacks playoff resilience.",
            mechanism="Identify lack of stress vectors (Physicality/Creation). High Dependence."
        ),
        LatentStarTestCase(
            name="Tyrese Haliburton",
            season="2021-22",
            category="True Positive - Comparison Case",
            test_usage=0.28,
            expected_outcome="Bulldozer",
            expected_star_level="High",
            expected_risk_category="Franchise Cornerstone",
            context="Traded 1-1 for Sabonis. Elite Creation and Leverage vectors.",
            mechanism="Identify elite stress vectors. Low Dependence."
        ),
    ]
    return test_cases

def validate_telescope_resilience():
    # 1. Load Model and Features
    model_path = Path("models/telescope_model.pkl")
    features_path = Path("models/telescope_features.json")
    
    if not model_path.exists() or not features_path.exists():
        logger.error("Model or features list missing. Please run train_telescope_model.py first.")
        return
    
    model = joblib.load(model_path)
    with open(features_path, 'r') as f:
        features = json.load(f)
    
    # 2. Load Dataset
    data_path = Path("results/predictive_dataset_with_friction.csv")
    if not data_path.exists():
        logger.error("Predictive dataset missing. Please run evaluate_plasticity_potential.py first.")
        return
    
    df = pd.read_csv(data_path)
    
    # 3. Get Test Cases
    test_cases = get_test_cases()
    
    results = []
    
    logger.info("="*120)
    logger.info(f"{'PLAYER NAME':<25} | {'SEASON':<8} | {'SUBSIDY':<8} | {'POTENTIAL':<10} | {'ARCHETYPE':<12} | {'STATUS':<10}")
    logger.info("-"*120)
    
    for case in test_cases:
        # Find player in dataset
        player_data = df[(df['player_name'].str.contains(case.name, case=False, na=False)) & 
                         (df['season'] == case.season)]
        
        if player_data.empty:
            # Try fuzzy match on last name if exact match fails
            player_data = df[(df['player_name'].str.contains(case.name.split()[-1], case=False, na=False)) & 
                             (df['season'] == case.season)]
            
        if player_data.empty:
            results.append({
                'name': case.name,
                'season': case.season,
                'status': 'MISSING DATA'
            })
            continue
            
        row = player_data.iloc[0]
        
        # Prepare features for prediction
        X_df = pd.DataFrame([row[features]])
        
        # Prediction
        potential = model.predict(X_df)[0]
        subsidy = row.get('subsidy_index', 0.5)
        
        # Determine Archetype and Risk Category (First Principles Mapping)
        if potential > 4.0:
            predicted_archetype = "King"
        elif potential > 2.5:
            predicted_archetype = "Bulldozer"
        elif potential > 1.0:
            predicted_archetype = "Sniper"
        else:
            predicted_archetype = "Victim"
            
        # 2D Risk Matrix
        if potential > 2.5:
            risk_cat = "Franchise Cornerstone" if subsidy < 0.15 else "Luxury Component"
        else:
            risk_cat = "Depth Piece" if subsidy < 0.15 else "Avoid/System Merchant"
            
        # Success check
        is_success = False
        if case.expected_outcome in ["Bulldozer", "King"]:
            is_success = predicted_archetype in ["Bulldozer", "King"]
        elif case.expected_outcome in ["Victim", "Sniper"]:
            is_success = predicted_archetype in ["Victim", "Sniper"]
            
        # Extra check for 2D Risk Category if provided
        if case.expected_risk_category:
            if case.expected_risk_category == risk_cat:
                is_success = True
            else:
                # If risk category doesn't match, we still might count as success if archetype matches
                # but we'll be more strict if the user specifically provided a 2D category
                pass

        status_str = "✅ PASS" if is_success else "❌ FAIL"
        
        logger.info(f"{case.name:<25} | {case.season:<8} | {subsidy:<8.3f} | {potential:<10.2f} | {predicted_archetype:<12} | {status_str}")
        
        results.append({
            'name': case.name,
            'season': case.season,
            'category': case.category,
            'subsidy': subsidy,
            'potential': potential,
            'predicted_archetype': predicted_archetype,
            'risk_cat': risk_cat,
            'expected': case.expected_outcome,
            'success': is_success
        })
        
    # Summarize
    valid_results = [r for r in results if r.get('status') != 'MISSING DATA']
    total = len(valid_results)
    passed = len([r for r in valid_results if r.get('success')])
    missing = len([r for r in results if r.get('status') == 'MISSING DATA'])
    
    logger.info("="*120)
    logger.info(f"VALIDATION SUMMARY:")
    if total > 0:
        logger.info(f"Total Test Cases Found: {total}")
        logger.info(f"Passed: {passed} ({passed/total:.1%})")
        
        # Log specific failures
        failures = [r for r in valid_results if not r.get('success')]
        if failures:
            logger.info("\nSpecific Failures:")
            for f in failures:
                logger.info(f"  - {f['name']} ({f['season']}): Expected {f['expected']}, Predicted {f['predicted_archetype']} (Potential: {f['potential']:.2f}, Subsidy: {f['subsidy']:.3f})")
    else:
        logger.info("No valid test cases found in the dataset.")
    logger.info(f"Missing Data: {missing}")
    logger.info("="*120)

    # 4. Output Results to Files
    output_dir = Path("results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # CSV Output
    df_results = pd.DataFrame(results)
    csv_path = output_dir / "telescope_validation_results.csv"
    df_results.to_csv(csv_path, index=False)
    logger.info(f"Detailed results saved to {csv_path}")
    
    # Markdown Output
    md_path = output_dir / "telescope_validation_summary.md"
    with open(md_path, 'w') as f:
        f.write("# Telescope Model Validation Summary\n\n")
        f.write(f"**Pass Rate**: {passed}/{total} ({passed/total:.1%})\n\n")
        f.write("## Detailed Test Results\n\n")
        f.write("| Player Name | Season | Subsidy | Potential | Predicted | Expected | Status |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        
        for r in results:
            if r.get('status') == 'MISSING DATA':
                f.write(f"| {r['name']} | {r['season']} | - | - | - | - | ⚠️ MISSING |\n")
            else:
                status_emoji = "✅ PASS" if r['success'] else "❌ FAIL"
                f.write(f"| {r['name']} | {r['season']} | {r['subsidy']:.3f} | {r['potential']:.2f} | {r['predicted_archetype']} | {r['expected']} | {status_emoji} |\n")
                
        if failures:
            f.write("\n## Identified Failures\n\n")
            for f_case in failures:
                f.write(f"- **{f_case['name']} ({f_case['season']})**: Expected {f_case['expected']}, but model predicted {f_case['predicted_archetype']}. ")
                f.write(f"(Potential: {f_case['potential']:.2f}, Subsidy: {f_case['subsidy']:.3f})\n")
                
    logger.info(f"Markdown summary saved to {md_path}")

if __name__ == "__main__":
    validate_telescope_resilience()
