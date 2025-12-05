"""
Test 2D Risk Matrix Implementation

Validates both Performance (X-axis) and Dependence (Y-axis) dimensions
on known test cases from the Trust Fall experiment.
"""

import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))

from predict_conditional_archetype import ConditionalArchetypePredictor


def test_2d_risk_matrix():
    """Test 2D Risk Matrix on known cases."""
    
    predictor = ConditionalArchetypePredictor()
    
    # Test cases from Trust Fall experiment
    # Expected results based on 2D_RISK_MATRIX_IMPLEMENTATION.md
    test_cases = [
        {
            'player': 'Jordan Poole',
            'season': '2021-22',
            'expected_performance': 'High',  # He succeeded (17 PPG, 62.7% TS)
            'expected_dependence': 'High',   # System merchant
            'expected_category': 'Luxury Component'
        },
        {
            'player': 'Luka Dončić',
            'season': '2023-24',
            'expected_performance': 'High',  # Elite player
            'expected_dependence': 'Low',    # Portable, self-created
            'expected_category': 'Franchise Cornerstone'
        },
        {
            'player': 'Domantas Sabonis',
            'season': '2021-22',
            'expected_performance': 'High',  # High production
            'expected_dependence': 'High',   # System-based rim pressure
            'expected_category': 'Luxury Component'
        },
        {
            'player': 'Jalen Brunson',
            'season': '2020-21',
            'expected_performance': 'Low',   # At 19.6% usage: Victim
            'expected_dependence': 'Low',    # Skills are portable
            'expected_category': 'Depth'  # Or "Latent Star" if projected at higher usage
        },
        {
            'player': 'Tyrese Haliburton',
            'season': '2021-22',
            'expected_performance': 'High',  # Latent star
            'expected_dependence': 'Low',    # Portable skills
            'expected_category': 'Franchise Cornerstone'
        }
    ]
    
    results = []
    
    print("=" * 80)
    print("2D Risk Matrix Test Results")
    print("=" * 80)
    print()
    
    for test_case in test_cases:
        player_name = test_case['player']
        season = test_case['season']
        
        player_data = predictor.get_player_data(player_name, season)
        
        if player_data is None:
            print(f"❌ {player_name} ({season}): Data not found")
            results.append({
                'player': player_name,
                'season': season,
                'status': 'DATA_NOT_FOUND'
            })
            continue
        
        # Get current usage for prediction
        current_usage = player_data.get('USG_PCT', 0.25)
        if pd.isna(current_usage):
            current_usage = 0.25
        
        # Predict with 2D Risk Matrix
        result = predictor.predict_with_risk_matrix(
            player_data,
            current_usage,
            apply_phase3_fixes=True,
            apply_hard_gates=True
        )
        
        performance_score = result['performance_score']
        dependence_score = result['dependence_score']
        risk_category = result['risk_category']
        
        # Load data-driven thresholds
        import json
        thresholds_path = Path("results") / "dependence_thresholds.json"
        if thresholds_path.exists():
            with open(thresholds_path, 'r') as f:
                thresholds = json.load(f)
                low_dep_threshold = thresholds.get('low_threshold', 0.3570)
                high_dep_threshold = thresholds.get('high_threshold', 0.4482)
        else:
            # Fallback
            low_dep_threshold = 0.3570
            high_dep_threshold = 0.4482
        
        # Validate expectations
        performance_match = False
        dependence_match = False
        category_match = False
        
        if test_case['expected_performance'] == 'High':
            performance_match = performance_score >= 0.70
        elif test_case['expected_performance'] == 'Low':
            performance_match = performance_score < 0.30
        else:
            performance_match = True  # Moderate - no specific expectation
        
        if dependence_score is not None:
            if test_case['expected_dependence'] == 'High':
                dependence_match = dependence_score >= high_dep_threshold  # ≥ 0.4482
            elif test_case['expected_dependence'] == 'Low':
                dependence_match = dependence_score < low_dep_threshold  # < 0.3570
            else:
                dependence_match = True  # Moderate - no specific expectation
        else:
            dependence_match = False  # Missing data
        
        category_match = test_case['expected_category'] in risk_category
        
        # Print results
        status = "✅" if (performance_match and dependence_match and category_match) else "⚠️"
        
        print(f"{status} {player_name} ({season})")
        print(f"   Performance Score: {performance_score:.2%} (Expected: {test_case['expected_performance']})")
        if dependence_score is not None:
            print(f"   Dependence Score: {dependence_score:.2%} (Expected: {test_case['expected_dependence']})")
        else:
            print(f"   Dependence Score: N/A (Missing data)")
        print(f"   Risk Category: {risk_category}")
        print(f"   Expected Category: {test_case['expected_category']}")
        
        # Show component breakdown if available
        if 'dependence_details' in result.get('metadata', {}):
            dep_details = result['metadata']['dependence_details']
            if dep_details.get('assisted_fgm_pct') is not None:
                print(f"   Assisted FGM %: {dep_details['assisted_fgm_pct']:.2%}")
            if dep_details.get('open_shot_frequency') is not None:
                print(f"   Open Shot Frequency: {dep_details['open_shot_frequency']:.2%}")
            if dep_details.get('self_created_usage_ratio') is not None:
                print(f"   Self-Created Usage Ratio: {dep_details['self_created_usage_ratio']:.2%}")
        
        print()
        
        results.append({
            'player': player_name,
            'season': season,
            'performance_score': performance_score,
            'dependence_score': dependence_score,
            'risk_category': risk_category,
            'expected_category': test_case['expected_category'],
            'performance_match': performance_match,
            'dependence_match': dependence_match,
            'category_match': category_match,
            'status': 'PASS' if (performance_match and dependence_match and category_match) else 'FAIL'
        })
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    
    df_results = pd.DataFrame(results)
    
    if len(df_results) > 0:
        total = len(df_results)
        passed = len(df_results[df_results['status'] == 'PASS'])
        data_found = len(df_results[df_results['status'] != 'DATA_NOT_FOUND'])
        
        print(f"Total Test Cases: {total}")
        print(f"Data Found: {data_found}")
        print(f"Passed: {passed}/{data_found} ({passed/data_found*100:.1f}%)" if data_found > 0 else "Passed: N/A")
        print()
        
        # Performance dimension
        perf_match = df_results['performance_match'].sum()
        print(f"Performance Match: {perf_match}/{data_found} ({perf_match/data_found*100:.1f}%)" if data_found > 0 else "Performance Match: N/A")
        
        # Dependence dimension
        dep_match = df_results['dependence_match'].sum()
        dep_available = df_results['dependence_score'].notna().sum()
        print(f"Dependence Match: {dep_match}/{dep_available} ({dep_match/dep_available*100:.1f}%)" if dep_available > 0 else "Dependence Match: N/A")
        print(f"Dependence Data Available: {dep_available}/{data_found}")
        
        # Category match
        cat_match = df_results['category_match'].sum()
        print(f"Category Match: {cat_match}/{data_found} ({cat_match/data_found*100:.1f}%)" if data_found > 0 else "Category Match: N/A")
        
        # Save results
        output_path = Path("results") / "2d_risk_matrix_test_results.csv"
        df_results.to_csv(output_path, index=False)
        print(f"\nResults saved to: {output_path}")
    
    return results


if __name__ == "__main__":
    test_2d_risk_matrix()

