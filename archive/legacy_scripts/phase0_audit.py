"""
Phase 0: Map the Problem Space
Step 0.1: Load and Understand Full Test Suite
Step 0.2: Audit Feature Values for Problem Cases
Step 0.3: Categorize False Positives by Failure Mode
Step 0.4: Understand Prediction Return Structure
Step 0.5: Map Feature Pipeline Dependencies
"""

import sys
import pandas as pd
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from test_latent_star_cases import get_test_cases
from src.nba_data.scripts.predict_conditional_archetype import ConditionalArchetypePredictor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def step_0_1_understand_test_suite():
    """Step 0.1: Load and Understand Full Test Suite"""
    logger.info("=" * 80)
    logger.info("Step 0.1: Understanding Full Test Suite")
    logger.info("=" * 80)
    
    test_cases = get_test_cases()
    
    print(f"\nTotal cases: {len(test_cases)}")
    print(f"\nCategories:")
    categories = set(tc.category for tc in test_cases)
    for cat in sorted(categories):
        count = sum(1 for tc in test_cases if tc.category == cat)
        print(f"  - {cat}: {count} cases")
    
    # Identify false positives
    false_positives = [tc for tc in test_cases if 'False Positive' in tc.category]
    true_negatives = [tc for tc in test_cases if 'True Negative' in tc.category]
    
    print(f"\nFalse Positives: {len(false_positives)}")
    for fp in false_positives:
        print(f"  - {fp.name} ({fp.season}): Expected <55%, Category: {fp.category}")
    
    print(f"\nTrue Negatives: {len(true_negatives)}")
    for tn in true_negatives[:10]:  # Show first 10
        print(f"  - {tn.name} ({tn.season}): Expected <55%, Category: {tn.category}")
    
    return test_cases, false_positives, true_negatives

def step_0_2_audit_feature_values(false_positives, true_negatives):
    """Step 0.2: Audit Feature Values for Problem Cases"""
    logger.info("=" * 80)
    logger.info("Step 0.2: Auditing Feature Values for Problem Cases")
    logger.info("=" * 80)
    
    predictor = ConditionalArchetypePredictor()
    
    # Problem cases from external feedback + test suite
    problem_cases = [
        ('Jordan Poole', '2021-22'),
        ('D\'Angelo Russell', '2018-19'),
        ('Julius Randle', '2020-21'),
        ('Elfrid Payton', '2018-19'),
        ('Kris Dunn', '2017-18'),
        ('Willy Hernangomez', '2016-17'),
        ('Christian Wood', '2020-21'),
        ('Talen Horton-Tucker', '2020-21'),
    ]
    
    # Add all false positives and true negatives
    for tc in false_positives + true_negatives:
        if (tc.name, tc.season) not in problem_cases:
            problem_cases.append((tc.name, tc.season))
    
    audit_results = []
    
    for name, season in problem_cases:
        logger.info(f"Auditing {name} ({season})...")
        try:
            player_data = predictor.get_player_data(name, season)
            
            if player_data is not None:
                audit_results.append({
                    'name': name,
                    'season': season,
                    'EFG_ISO_WEIGHTED': player_data.get('EFG_ISO_WEIGHTED', None),
                    'CREATION_TAX': player_data.get('CREATION_TAX', None),
                    'CREATION_VOLUME_RATIO': player_data.get('CREATION_VOLUME_RATIO', None),
                    'RS_RIM_APPETITE': player_data.get('RS_RIM_APPETITE', None),
                    'DEPENDENCE_SCORE': player_data.get('DEPENDENCE_SCORE', None),
                    'INEFFICIENT_VOLUME_SCORE': player_data.get('INEFFICIENT_VOLUME_SCORE', None),
                    'USG_PCT': player_data.get('USG_PCT', None),
                    'LEVERAGE_USG_DELTA': player_data.get('LEVERAGE_USG_DELTA', None),
                    'LEVERAGE_TS_DELTA': player_data.get('LEVERAGE_TS_DELTA', None),
                    'SHOT_QUALITY_GENERATION_DELTA': player_data.get('SHOT_QUALITY_GENERATION_DELTA', None),
                })
            else:
                logger.warning(f"  Could not find data for {name} ({season})")
                audit_results.append({
                    'name': name,
                    'season': season,
                    'EFG_ISO_WEIGHTED': None,
                    'CREATION_TAX': None,
                    'CREATION_VOLUME_RATIO': None,
                    'RS_RIM_APPETITE': None,
                    'DEPENDENCE_SCORE': None,
                    'INEFFICIENT_VOLUME_SCORE': None,
                    'USG_PCT': None,
                    'LEVERAGE_USG_DELTA': None,
                    'LEVERAGE_TS_DELTA': None,
                    'SHOT_QUALITY_GENERATION_DELTA': None,
                })
        except Exception as e:
            logger.error(f"  Error auditing {name} ({season}): {e}")
            audit_results.append({
                'name': name,
                'season': season,
                'error': str(e),
            })
    
    # Save audit results
    audit_df = pd.DataFrame(audit_results)
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    audit_path = results_dir / "phase4_5_feature_audit.csv"
    audit_df.to_csv(audit_path, index=False)
    logger.info(f"\nSaved audit results to {audit_path}")
    
    # Print summary statistics
    print("\n" + "=" * 80)
    print("Feature Audit Summary")
    print("=" * 80)
    
    numeric_cols = ['EFG_ISO_WEIGHTED', 'CREATION_TAX', 'CREATION_VOLUME_RATIO', 
                    'RS_RIM_APPETITE', 'DEPENDENCE_SCORE', 'INEFFICIENT_VOLUME_SCORE', 'USG_PCT']
    
    for col in numeric_cols:
        if col in audit_df.columns:
            values = audit_df[col].dropna()
            if len(values) > 0:
                print(f"\n{col}:")
                print(f"  Count: {len(values)}/{len(audit_df)}")
                print(f"  Mean: {values.mean():.4f}")
                print(f"  Median: {values.median():.4f}")
                print(f"  Min: {values.min():.4f}")
                print(f"  Max: {values.max():.4f}")
                
                # Test thresholds
                if col == 'EFG_ISO_WEIGHTED':
                    for threshold in [0.40, 0.42, 0.45, 0.48]:
                        below = (values < threshold).sum()
                        print(f"  Below {threshold}: {below}/{len(values)} ({below/len(values)*100:.1f}%)")
                elif col == 'INEFFICIENT_VOLUME_SCORE':
                    for threshold in [0.010, 0.015, 0.020]:
                        above = (values > threshold).sum()
                        print(f"  Above {threshold}: {above}/{len(values)} ({above/len(values)*100:.1f}%)")
                elif col == 'RS_RIM_APPETITE':
                    threshold = 0.1746  # Bottom 20th percentile
                    below = (values < threshold).sum()
                    print(f"  Below {threshold} (20th percentile): {below}/{len(values)} ({below/len(values)*100:.1f}%)")
                elif col == 'DEPENDENCE_SCORE':
                    for threshold in [0.45, 0.60]:
                        above = (values > threshold).sum()
                        print(f"  Above {threshold}: {above}/{len(values)} ({above/len(values)*100:.1f}%)")
    
    return audit_df

def step_0_3_categorize_false_positives(audit_df):
    """Step 0.3: Categorize False Positives by Failure Mode"""
    logger.info("=" * 80)
    logger.info("Step 0.3: Categorizing False Positives by Failure Mode")
    logger.info("=" * 80)
    
    categorized = {
        'low_efficiency': [],  # EFG_ISO_WEIGHTED < 0.45 → Quality floor should fix
        'system_dependent': [],  # DEPENDENCE_SCORE > 0.45 → Dependence score should fix
        'empty_calories': [],  # High INEFFICIENT_VOLUME_SCORE → INEFFICIENT_VOLUME_SCORE should fix
        'low_rim_pressure': [],  # RS_RIM_APPETITE < threshold → Exponential flaw scaling should fix
        'multiple_issues': [],  # Multiple problems
        'unknown': [],  # Need investigation
    }
    
    for _, row in audit_df.iterrows():
        name = row['name']
        efg = row.get('EFG_ISO_WEIGHTED')
        dep = row.get('DEPENDENCE_SCORE')
        ineff = row.get('INEFFICIENT_VOLUME_SCORE')
        rim = row.get('RS_RIM_APPETITE')
        creation_tax = row.get('CREATION_TAX')
        
        issues = []
        
        # Check each failure mode
        if pd.notna(efg) and efg < 0.45:
            issues.append('low_efficiency')
        
        if pd.notna(dep) and dep > 0.45:
            issues.append('system_dependent')
        
        if pd.notna(ineff) and ineff > 0.015:
            issues.append('empty_calories')
        
        if pd.notna(rim) and rim < 0.1746:  # Bottom 20th percentile
            issues.append('low_rim_pressure')
        
        # Categorize
        if len(issues) == 0:
            categorized['unknown'].append(name)
        elif len(issues) == 1:
            categorized[issues[0]].append(name)
        else:
            categorized['multiple_issues'].append((name, issues))
    
    print("\nCategorized False Positives:")
    for category, cases in categorized.items():
        if cases:
            print(f"\n{category}: {len(cases)} cases")
            for case in cases:
                if isinstance(case, tuple):
                    print(f"  - {case[0]}: {', '.join(case[1])}")
                else:
                    print(f"  - {case}")
    
    return categorized

def step_0_4_understand_prediction_structure():
    """Step 0.4: Understand Prediction Return Structure"""
    logger.info("=" * 80)
    logger.info("Step 0.4: Understanding Prediction Return Structure")
    logger.info("=" * 80)
    
    predictor = ConditionalArchetypePredictor()
    
    # Test with a known case
    test_cases = get_test_cases()
    test_case = test_cases[0]  # Use first test case
    
    logger.info(f"Testing with {test_case.name} ({test_case.season})...")
    
    player_data = predictor.get_player_data(test_case.name, test_case.season)
    
    if player_data is not None:
        result = predictor.predict_archetype_at_usage(
            player_data,
            usage_level=test_case.test_usage,
            apply_phase3_fixes=True,
            apply_hard_gates=True
        )
        
        print("\nPrediction Return Structure:")
        print(f"Keys: {list(result.keys())}")
        print("\nFull result structure:")
        for key, value in result.items():
            if isinstance(value, dict):
                print(f"  {key}: dict with keys {list(value.keys())}")
            elif isinstance(value, (list, tuple)):
                print(f"  {key}: {type(value).__name__} of length {len(value)}")
            else:
                print(f"  {key}: {type(value).__name__} = {value}")
        
        return result
    else:
        logger.warning(f"Could not find data for {test_case.name} ({test_case.season})")
        return None

def step_0_5_map_pipeline_dependencies():
    """Step 0.5: Map Feature Pipeline Dependencies"""
    logger.info("=" * 80)
    logger.info("Step 0.5: Mapping Feature Pipeline Dependencies")
    logger.info("=" * 80)
    
    pipeline = {
        'evaluate_plasticity_potential.py': {
            'inputs': ['training_dataset.csv', 'shot_quality_data'],
            'outputs': ['predictive_features_*.csv'],
            'generates': ['CREATION_TAX', 'CREATION_VOLUME_RATIO', 'LEVERAGE_*', 'DEPENDENCE_SCORE'],
        },
        'calculate_shot_difficulty_features.py': {
            'inputs': ['shot_quality_with_clock.csv'],
            'outputs': ['pressure_features.csv'],
            'generates': ['RS_PRESSURE_*', 'RS_OPEN_SHOT_FREQUENCY'],
        },
        'assemble_predictive_dataset.py': {
            'inputs': ['predictive_features_*.csv', 'pressure_features.csv', 'training_dataset.csv'],
            'outputs': ['predictive_dataset.csv'],
            'generates': ['Combined feature dataset'],
        },
        'generate_gate_features.py': {
            'inputs': ['predictive_dataset.csv'],
            'outputs': ['gate_features.csv'],
            'generates': ['QUALITY_ADJUSTED_RESILIENCE', 'INEFFICIENT_VOLUME_SCORE', 'RIM_PRESSURE_DEFICIT'],
        },
        'train_rfe_model.py': {
            'inputs': ['predictive_dataset.csv', 'gate_features.csv', 'previous_playoff_features.csv'],
            'outputs': ['models/resilience_xgb_rfe_10.pkl'],
            'generates': ['Trained model'],
        },
    }
    
    print("\nPipeline Order and Dependencies:")
    print("=" * 80)
    
    for i, (script, deps) in enumerate(pipeline.items(), 1):
        print(f"\n{i}. {script}")
        print(f"   Inputs: {', '.join(deps['inputs'])}")
        print(f"   Outputs: {', '.join(deps['outputs'])}")
        print(f"   Generates: {', '.join(deps['generates'][:3])}...")
    
    # Check if files exist
    print("\n" + "=" * 80)
    print("Pipeline File Status:")
    print("=" * 80)
    
    results_dir = Path("results")
    models_dir = Path("models")
    
    required_files = {
        'predictive_dataset.csv': results_dir / 'predictive_dataset.csv',
        'gate_features.csv': results_dir / 'gate_features.csv',
        'pressure_features.csv': results_dir / 'pressure_features.csv',
        'resilience_xgb_rfe_10.pkl': models_dir / 'resilience_xgb_rfe_10.pkl',
    }
    
    for name, path in required_files.items():
        exists = path.exists()
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"  {name}: {status}")
        if exists:
            size = path.stat().st_size / 1024  # KB
            mtime = pd.Timestamp.fromtimestamp(path.stat().st_mtime)
            print(f"    Size: {size:.1f} KB, Modified: {mtime}")
    
    return pipeline

def main():
    """Run all Phase 0 steps"""
    logger.info("Starting Phase 0: Map the Problem Space")
    
    # Step 0.1: Understand test suite
    test_cases, false_positives, true_negatives = step_0_1_understand_test_suite()
    
    # Step 0.2: Audit feature values
    audit_df = step_0_2_audit_feature_values(false_positives, true_negatives)
    
    # Step 0.3: Categorize false positives
    categorized = step_0_3_categorize_false_positives(audit_df)
    
    # Step 0.4: Understand prediction structure
    prediction_structure = step_0_4_understand_prediction_structure()
    
    # Step 0.5: Map pipeline dependencies
    pipeline = step_0_5_map_pipeline_dependencies()
    
    logger.info("\n" + "=" * 80)
    logger.info("Phase 0 Complete!")
    logger.info("=" * 80)
    logger.info(f"Audit results saved to: results/phase4_5_feature_audit.csv")
    logger.info(f"Total problem cases audited: {len(audit_df)}")
    logger.info(f"Categories identified: {len([k for k, v in categorized.items() if v])}")

if __name__ == "__main__":
    main()

