"""
Phase 0: Data Understanding & Diagnosis
Analyze data distributions, missing data patterns, and test case groupings
before implementing Phase 3 fixes.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase3DataAnalyzer:
    def __init__(self):
        self.results_dir = Path("results")
        self.data_dir = Path("data")
        
    def load_all_data(self):
        """Load all relevant datasets."""
        logger.info("Loading datasets...")
        
        # Base features
        df_features = pd.read_csv(self.results_dir / "predictive_dataset.csv")
        logger.info(f"Loaded {len(df_features)} player-seasons from predictive_dataset.csv")
        
        # Pressure features
        df_pressure = pd.read_csv(self.results_dir / "pressure_features.csv")
        logger.info(f"Loaded {len(df_pressure)} player-seasons from pressure_features.csv")
        
        # Test case results
        df_test = pd.read_csv(self.results_dir / "latent_star_test_cases_results.csv")
        logger.info(f"Loaded {len(df_test)} test cases")
        
        # Merge pressure features
        df_merged = df_features.merge(
            df_pressure,
            on=['PLAYER_ID', 'SEASON'],
            how='left',
            suffixes=('', '_pressure')
        )
        # Drop duplicate columns from merge
        cols_to_drop = [c for c in df_merged.columns if '_pressure' in c]
        df_merged = df_merged.drop(columns=cols_to_drop)
        
        logger.info(f"After merge: {len(df_merged)} player-seasons")
        logger.info(f"Missing pressure data: {df_merged['RS_PRESSURE_APPETITE'].isna().sum()} players")
        
        return df_merged, df_test
    
    def analyze_feature_distributions(self, df):
        """Analyze distributions of key features for Phase 3 fixes."""
        logger.info("\n" + "="*80)
        logger.info("FEATURE DISTRIBUTION ANALYSIS")
        logger.info("="*80)
        
        features_to_analyze = [
            'RS_PRESSURE_APPETITE',
            'RS_PRESSURE_RESILIENCE',
            'RS_LATE_CLOCK_PRESSURE_APPETITE',
            'RS_EARLY_CLOCK_PRESSURE_APPETITE',
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE',
            'RS_EARLY_CLOCK_PRESSURE_RESILIENCE',
            'RIM_PRESSURE_RESILIENCE',
            'CREATION_VOLUME_RATIO',
            'CREATION_TAX',
            'EFG_ISO_WEIGHTED',
            'LEVERAGE_USG_DELTA',
            'USG_PCT',
        ]
        
        results = {}
        
        for feature in features_to_analyze:
            if feature not in df.columns:
                logger.warning(f"Feature {feature} not found in dataset")
                continue
                
            logger.info(f"\n{feature}:")
            logger.info("-" * 60)
            
            # Basic stats
            non_null = df[feature].dropna()
            if len(non_null) == 0:
                logger.warning(f"  All values are missing!")
                continue
                
            stats = {
                'count': len(non_null),
                'missing': df[feature].isna().sum(),
                'missing_pct': (df[feature].isna().sum() / len(df)) * 100,
                'mean': non_null.mean(),
                'median': non_null.median(),
                'std': non_null.std(),
                'min': non_null.min(),
                'max': non_null.max(),
            }
            
            # Percentiles
            percentiles = [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
            percentile_values = non_null.quantile(percentiles)
            
            logger.info(f"  Count: {stats['count']:,}")
            logger.info(f"  Missing: {stats['missing']:,} ({stats['missing_pct']:.1f}%)")
            logger.info(f"  Mean: {stats['mean']:.4f}")
            logger.info(f"  Median: {stats['median']:.4f}")
            logger.info(f"  Std: {stats['std']:.4f}")
            logger.info(f"  Range: [{stats['min']:.4f}, {stats['max']:.4f}]")
            logger.info(f"  Percentiles:")
            for p, v in zip(percentiles, percentile_values):
                logger.info(f"    {p*100:2.0f}th: {v:.4f}")
            
            # Special analysis for context adjustment (if we calculate it)
            if feature == 'RS_PRESSURE_APPETITE':
                # Check if low values correlate with low usage (role constraint)
                low_usage = df[df['USG_PCT'] < 0.20]
                if len(low_usage) > 0 and feature in low_usage.columns:
                    low_usage_median = low_usage[feature].median()
                    logger.info(f"  Median for players with USG < 20%: {low_usage_median:.4f}")
            
            results[feature] = {
                'stats': stats,
                'percentiles': dict(zip(percentiles, percentile_values))
            }
        
        return results
    
    def analyze_missing_data(self, df):
        """Investigate root causes of missing data."""
        logger.info("\n" + "="*80)
        logger.info("MISSING DATA ANALYSIS")
        logger.info("="*80)
        
        # Key pressure features
        pressure_features = [
            'RS_PRESSURE_APPETITE',
            'RS_PRESSURE_RESILIENCE',
            'RS_LATE_CLOCK_PRESSURE_APPETITE',
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE',
            'RIM_PRESSURE_RESILIENCE',
        ]
        
        # Check missing patterns
        logger.info("\nMissing data patterns:")
        for feature in pressure_features:
            if feature not in df.columns:
                continue
            missing = df[feature].isna().sum()
            missing_pct = (missing / len(df)) * 100
            logger.info(f"  {feature}: {missing:,} ({missing_pct:.1f}%)")
        
        # Check if missing correlates with other factors
        logger.info("\nInvestigating missing data root causes...")
        
        # Check if missing pressure data correlates with no playoff data
        # (This would indicate systematic bias - only playoff players have PO features)
        if 'PO_PRESSURE_APPETITE' in df.columns:
            has_po_data = df['PO_PRESSURE_APPETITE'].notna()
            missing_rs = df['RS_PRESSURE_APPETITE'].isna()
            
            logger.info(f"\nPlayers with PO pressure data: {has_po_data.sum():,}")
            logger.info(f"Players missing RS pressure data: {missing_rs.sum():,}")
            
            # Check overlap
            missing_rs_with_po = (missing_rs & has_po_data).sum()
            logger.info(f"Missing RS but have PO: {missing_rs_with_po:,} (indicates data collection issue)")
        
        # Check if missing data correlates with usage (role players might have less data)
        if 'USG_PCT' in df.columns:
            missing_pressure = df['RS_PRESSURE_APPETITE'].isna()
            if missing_pressure.sum() > 0:
                missing_usage = df[missing_pressure]['USG_PCT'].describe()
                has_usage = df[~missing_pressure]['USG_PCT'].describe()
                
                logger.info(f"\nUsage distribution for players with missing pressure data:")
                logger.info(f"  Mean: {missing_usage['mean']:.3f}")
                logger.info(f"  Median: {missing_usage['50%']:.3f}")
                logger.info(f"\nUsage distribution for players with pressure data:")
                logger.info(f"  Mean: {has_usage['mean']:.3f}")
                logger.info(f"  Median: {has_usage['50%']:.3f}")
        
        return {
            'missing_counts': {f: df[f].isna().sum() for f in pressure_features if f in df.columns},
            'total_players': len(df)
        }
    
    def group_test_cases_by_failure_mode(self, df_test):
        """Group test cases by failure mode pattern."""
        logger.info("\n" + "="*80)
        logger.info("TEST CASE GROUPING BY FAILURE MODE")
        logger.info("="*80)
        
        # Group by category
        grouped = df_test.groupby('category').agg({
            'player_name': list,
            'overall_pass': ['sum', 'count'],
            'star_level_potential': ['mean', 'min', 'max']
        }).reset_index()
        
        grouped.columns = ['category', 'players', 'passed', 'total', 'avg_star_level', 'min_star_level', 'max_star_level']
        grouped['pass_rate'] = (grouped['passed'] / grouped['total'] * 100).round(1)
        
        logger.info("\nFailure mode patterns:")
        for _, row in grouped.iterrows():
            logger.info(f"\n{row['category']}:")
            logger.info(f"  Players: {', '.join(row['players'])}")
            logger.info(f"  Pass rate: {row['passed']}/{row['total']} ({row['pass_rate']}%)")
            logger.info(f"  Star level range: {row['min_star_level']:.1f}% - {row['max_star_level']:.1f}% (avg: {row['avg_star_level']:.1f}%)")
        
        # Identify specific failure modes
        failed = df_test[~df_test['overall_pass']]
        logger.info(f"\n\nFailed test cases ({len(failed)}/{len(df_test)}):")
        for _, row in failed.iterrows():
            logger.info(f"  {row['player_name']} ({row['season']}): {row['category']}")
            logger.info(f"    Expected: {row['expected_outcome']} (star-level {row['expected_star_level']})")
            logger.info(f"    Got: {row['predicted_archetype']} ({row['star_level_potential']:.1f}%)")
            if pd.notna(row['notes']):
                logger.info(f"    Notes: {row['notes']}")
        
        return grouped
    
    def analyze_role_constraint_pattern(self, df, df_test):
        """Analyze the role constraint pattern (Oladipo, Markkanen, Bane, Bridges)."""
        logger.info("\n" + "="*80)
        logger.info("ROLE CONSTRAINT PATTERN ANALYSIS")
        logger.info("="*80)
        
        role_constraint_cases = ['Victor Oladipo', 'Lauri Markkanen', 'Desmond Bane', 'Mikal Bridges']
        role_constraint_data = df_test[df_test['player_name'].isin(role_constraint_cases)]
        
        logger.info(f"\nRole-constrained players: {', '.join(role_constraint_cases)}")
        
        # Get their feature values
        for _, test_case in role_constraint_data.iterrows():
            player = test_case['player_name']
            season = test_case['season']
            
            # Handle case-insensitive matching
            player_data = df[
                (df['PLAYER_NAME'].str.upper() == player.upper()) & 
                (df['SEASON'] == season)
            ]
            if len(player_data) == 0:
                logger.warning(f"  {player} ({season}): Not found in dataset")
                continue
            
            row = player_data.iloc[0]
            logger.info(f"\n{player} ({season}):")
            logger.info(f"  Current USG: {row.get('USG_PCT', 'N/A'):.1%}" if pd.notna(row.get('USG_PCT')) else f"  Current USG: N/A")
            logger.info(f"  CREATION_VOLUME_RATIO: {row.get('CREATION_VOLUME_RATIO', 'N/A'):.3f}" if pd.notna(row.get('CREATION_VOLUME_RATIO')) else f"  CREATION_VOLUME_RATIO: N/A")
            logger.info(f"  CREATION_TAX: {row.get('CREATION_TAX', 'N/A'):.3f}" if pd.notna(row.get('CREATION_TAX')) else f"  CREATION_TAX: N/A")
            logger.info(f"  EFG_ISO_WEIGHTED: {row.get('EFG_ISO_WEIGHTED', 'N/A'):.3f}" if pd.notna(row.get('EFG_ISO_WEIGHTED')) else f"  EFG_ISO_WEIGHTED: N/A")
            logger.info(f"  RS_PRESSURE_APPETITE: {row.get('RS_PRESSURE_APPETITE', 'N/A'):.3f}" if pd.notna(row.get('RS_PRESSURE_APPETITE')) else f"  RS_PRESSURE_APPETITE: N/A")
            logger.info(f"  Predicted star-level: {test_case['star_level_potential']:.1f}%")
            logger.info(f"  Expected: {test_case['expected_star_level']}")
    
    def calculate_context_adjustment(self, df):
        """Calculate context adjustment if not already present."""
        logger.info("\n" + "="*80)
        logger.info("CONTEXT ADJUSTMENT ANALYSIS")
        logger.info("="*80)
        
        # Check if context adjustment already exists
        if 'RS_CONTEXT_ADJUSTMENT' in df.columns:
            logger.info("RS_CONTEXT_ADJUSTMENT already exists in dataset")
            non_null = df['RS_CONTEXT_ADJUSTMENT'].dropna()
            if len(non_null) > 0:
                logger.info(f"  Count: {len(non_null):,}")
                logger.info(f"  Mean: {non_null.mean():.4f}")
                logger.info(f"  Median: {non_null.median():.4f}")
                logger.info(f"  Percentiles:")
                for p in [0.1, 0.25, 0.5, 0.75, 0.9]:
                    logger.info(f"    {p*100:2.0f}th: {non_null.quantile(p):.4f}")
        else:
            logger.info("RS_CONTEXT_ADJUSTMENT not found - will need to calculate")
            logger.info("  This requires shot quality data (defender distance)")
            logger.info("  Expected median: ~-0.0135 (most players perform worse than expected)")
            logger.info("  Top 10-15% threshold: ~0.05 (significant outperformance)")
    
    def generate_summary_report(self, df, df_test, feature_stats, missing_data_info, test_grouping):
        """Generate a summary report."""
        logger.info("\n" + "="*80)
        logger.info("SUMMARY REPORT")
        logger.info("="*80)
        
        logger.info(f"\nDataset Overview:")
        logger.info(f"  Total player-seasons: {len(df):,}")
        logger.info(f"  Test cases: {len(df_test)}")
        logger.info(f"  Pass rate: {df_test['overall_pass'].sum()}/{len(df_test)} ({df_test['overall_pass'].mean()*100:.1f}%)")
        
        logger.info(f"\nMissing Data:")
        for feature, count in missing_data_info['missing_counts'].items():
            pct = (count / missing_data_info['total_players']) * 100
            logger.info(f"  {feature}: {count:,} ({pct:.1f}%)")
        
        logger.info(f"\nKey Insights:")
        logger.info(f"  1. Feature distributions analyzed - check percentiles above")
        logger.info(f"  2. Missing data patterns identified - investigate root causes")
        logger.info(f"  3. Test cases grouped by failure mode - fix patterns, not cases")
        logger.info(f"  4. Role constraint pattern identified - need usage-dependent weighting")
        
        # Save summary to file
        summary_path = self.results_dir / "phase3_data_analysis_summary.txt"
        with open(summary_path, 'w') as f:
            f.write("Phase 3 Data Analysis Summary\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total player-seasons: {len(df):,}\n")
            f.write(f"Test cases: {len(df_test)}\n")
            f.write(f"Pass rate: {df_test['overall_pass'].sum()}/{len(df_test)} ({df_test['overall_pass'].mean()*100:.1f}%)\n\n")
            f.write("Missing Data:\n")
            for feature, count in missing_data_info['missing_counts'].items():
                pct = (count / missing_data_info['total_players']) * 100
                f.write(f"  {feature}: {count:,} ({pct:.1f}%)\n")
        
        logger.info(f"\nSummary saved to: {summary_path}")

def main():
    analyzer = Phase3DataAnalyzer()
    
    # Load data
    df, df_test = analyzer.load_all_data()
    
    # Analyze feature distributions
    feature_stats = analyzer.analyze_feature_distributions(df)
    
    # Analyze missing data
    missing_data_info = analyzer.analyze_missing_data(df)
    
    # Group test cases
    test_grouping = analyzer.group_test_cases_by_failure_mode(df_test)
    
    # Analyze role constraint pattern
    analyzer.analyze_role_constraint_pattern(df, df_test)
    
    # Check context adjustment
    analyzer.calculate_context_adjustment(df)
    
    # Generate summary
    analyzer.generate_summary_report(df, df_test, feature_stats, missing_data_info, test_grouping)
    
    logger.info("\n" + "="*80)
    logger.info("Phase 0 Data Analysis Complete")
    logger.info("="*80)
    logger.info("\nNext steps:")
    logger.info("  1. Review feature distributions to understand 'normal' values")
    logger.info("  2. Investigate missing data root causes")
    logger.info("  3. Design fixes based on failure mode patterns")
    logger.info("  4. Implement fixes with pattern-based validation")

if __name__ == "__main__":
    main()

