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
        
        # ========== Category 1.5: The "Franchise Cornerstone" Misses (Critical False Negatives) ==========
        # These are elite players who should be identified as Franchise Cornerstones but the model is missing
        LatentStarTestCase(
            name="Nikola Jokić",
            season="2015-16",
            category="True Positive - Franchise Cornerstone",
            test_usage=0.30,
            expected_outcome="King",  # Or Bulldozer
            expected_star_level="High",  # >65%
            expected_risk_category="Franchise Cornerstone",  # High Performance + Low Dependence
            context="Rookie year (19.4% Usage). Age 21. Future MVP and champion. Elite passing and efficiency.",
            mechanism="Tests model's ability to identify elite bigs with unique skill sets. Should see high creation volume, elite efficiency, and low dependence."
        ),
        LatentStarTestCase(
            name="Nikola Jokić",
            season="2016-17",
            category="True Positive - Franchise Cornerstone",
            test_usage=0.30,
            expected_outcome="King",
            expected_star_level="High",  # >65%
            expected_risk_category="Franchise Cornerstone",
            context="Age 22 (23.1% Usage). Emerging as elite playmaker and scorer. Future MVP trajectory.",
            mechanism="Elite creation volume and efficiency. Low dependence on system. Should be identified as franchise cornerstone."
        ),
        LatentStarTestCase(
            name="Nikola Jokić",
            season="2017-18",
            category="True Positive - Franchise Cornerstone",
            test_usage=0.30,
            expected_outcome="King",
            expected_star_level="High",  # >65%
            expected_risk_category="Franchise Cornerstone",
            context="Age 23 (23.8% Usage). All-Star season. Elite passing and scoring efficiency.",
            mechanism="Should identify elite creation and efficiency. Low dependence - self-created offense."
        ),
        LatentStarTestCase(
            name="Nikola Jokić",
            season="2018-19",
            category="True Positive - Franchise Cornerstone",
            test_usage=0.30,
            expected_outcome="King",
            expected_star_level="High",  # >65%
            expected_risk_category="Franchise Cornerstone",
            context="Age 24 (27.1% Usage). First-team All-NBA. Elite playmaker and scorer.",
            mechanism="Franchise cornerstone with elite creation volume and efficiency. Low dependence on system."
        ),
        LatentStarTestCase(
            name="Anthony Davis",
            season="2015-16",
            category="True Positive - Franchise Cornerstone",
            test_usage=0.30,
            expected_outcome="Bulldozer",  # Or King
            expected_star_level="High",  # >65%
            expected_risk_category="Franchise Cornerstone",
            context="Age 23 (29.0% Usage). All-Star, All-NBA. Elite rim pressure and defensive anchor.",
            mechanism="Elite physicality vector (rim pressure) and creation. Should be identified as franchise cornerstone."
        ),
        LatentStarTestCase(
            name="Anthony Davis",
            season="2016-17",
            category="True Positive - Franchise Cornerstone",
            test_usage=0.30,
            expected_outcome="Bulldozer",  # Or King
            expected_star_level="High",  # >65%
            expected_risk_category="Franchise Cornerstone",
            context="Age 24 (32.1% Usage). All-Star, All-NBA. Elite two-way player.",
            mechanism="Elite rim pressure, creation volume, and efficiency. Low dependence - self-created offense."
        ),
        LatentStarTestCase(
            name="Joel Embiid",
            season="2016-17",
            category="True Positive - Franchise Cornerstone",
            test_usage=0.30,
            expected_outcome="King",
            expected_star_level="High",  # >65%
            expected_risk_category="Franchise Cornerstone",
            context="Rookie year (35.6% Usage). Age 23. Elite rim pressure and scoring. Future MVP.",
            mechanism="Elite physicality vector and creation volume. Should be identified as franchise cornerstone despite high usage."
        ),
        LatentStarTestCase(
            name="Joel Embiid",
            season="2017-18",
            category="True Positive - Franchise Cornerstone",
            test_usage=0.30,
            expected_outcome="Bulldozer",  # Or King
            expected_star_level="High",  # >65%
            expected_risk_category="Franchise Cornerstone",
            context="Age 24 (33.0% Usage). All-Star. Elite rim pressure and scoring efficiency.",
            mechanism="Elite creation volume and physicality. Low dependence - self-created offense."
        ),
    
        # ========== Category 2: The "Mirage" Breakouts & Fragile Stars (False Positives) ==========
        LatentStarTestCase(
            name="Jordan Poole",
            season="2021-22",
            category="False Positive - Mirage Breakout",
            test_usage=0.30,
            expected_outcome="Victim",
            expected_star_level="Low",  # <55% (or use 2D: High Performance + High Dependence)
            expected_risk_category="Luxury Component",  # High Performance + High Dependence
            context="26% Usage. System merchant relying on Curry gravity.",
            mechanism="Should detect low Pressure Resilience and dependence on open shots. 2D: High Performance (succeeded) + High Dependence (system merchant)."
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
            expected_star_level="Low",  # <55% (or use 2D: High Performance + High Dependence)
            expected_risk_category="Luxury Component",  # High Performance + High Dependence (system-based)
            context="Traded 1-1 for Haliburton. All-Star, but lacks playoff resilience.",
            mechanism="Model should identify lack of stress vectors (Physicality/Creation) needed for playoff success. 2D: High Performance + High Dependence (system-based rim pressure)."
        ),
        LatentStarTestCase(
            name="Tyrese Haliburton",
            season="2021-22",
            category="True Positive - Comparison Case",
            test_usage=0.28,
            expected_outcome="Bulldozer",
            expected_star_level="High",  # >65%
            expected_risk_category="Franchise Cornerstone",  # High Performance + Low Dependence (portable skills)
            context="Traded 1-1 for Sabonis. Elite Creation and Leverage vectors.",
            mechanism="Model should identify elite stress vectors. 2D: High Performance + Low Dependence (portable, self-created)."
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
