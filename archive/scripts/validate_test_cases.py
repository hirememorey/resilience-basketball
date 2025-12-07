"""
Phase 0 Validation: Test Case Analysis

This script validates known breakouts, non-breakouts, and fragility cases
to understand what the current system measures and where gaps exist.

Test Cases:
- Known Breakouts: Haliburton (2020-21), Brunson (2020-21), Siakam (2017-18/2018-19), Maxey (2020-21), Edwards (2020-21)
- Known Non-Breakouts: Turner (historical), McConnell (2020-21)
- Fragility Cases: Simmons (2017-18/2018-19), KAT (early career)
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestCaseValidator:
    """Validate test cases against current detection system."""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.data_dir = Path("data")
        
        # Test cases to validate
        self.test_cases = {
            # Known Breakouts (True Positives)
            "Haliburton_2020-21": {"name": "Tyrese Haliburton", "season": "2020-21", "type": "breakout"},
            "Brunson_2020-21": {"name": "Jalen Brunson", "season": "2020-21", "type": "breakout"},
            "Siakam_2017-18": {"name": "Pascal Siakam", "season": "2017-18", "type": "breakout"},
            "Siakam_2018-19": {"name": "Pascal Siakam", "season": "2018-19", "type": "breakout"},
            "Maxey_2020-21": {"name": "Tyrese Maxey", "season": "2020-21", "type": "breakout"},
            "Edwards_2020-21": {"name": "Anthony Edwards", "season": "2020-21", "type": "breakout"},
            
            # Known Non-Breakouts (False Positives)
            "Turner_2015-16": {"name": "Evan Turner", "season": "2015-16", "type": "non_breakout"},
            "Turner_2016-17": {"name": "Evan Turner", "season": "2016-17", "type": "non_breakout"},
            "McConnell_2020-21": {"name": "T.J. McConnell", "season": "2020-21", "type": "non_breakout"},
            
            # Fragility Cases
            "Simmons_2017-18": {"name": "Ben Simmons", "season": "2017-18", "type": "fragility"},
            "Simmons_2018-19": {"name": "Ben Simmons", "season": "2018-19", "type": "fragility"},
            "KAT_2015-16": {"name": "Karl-Anthony Towns", "season": "2015-16", "type": "fragility"},
            "KAT_2016-17": {"name": "Karl-Anthony Towns", "season": "2016-17", "type": "fragility"},
            "KAT_2017-18": {"name": "Karl-Anthony Towns", "season": "2017-18", "type": "fragility"},
        }
    
    def load_data(self) -> pd.DataFrame:
        """Load predictive dataset and merge with usage/age data."""
        logger.info("Loading predictive dataset...")
        df = pd.read_csv(self.results_dir / "predictive_dataset.csv")
        logger.info(f"Loaded {len(df)} player-seasons")
        
        # Load pressure features if available
        pressure_path = self.results_dir / "pressure_features.csv"
        if pressure_path.exists():
            df_pressure = pd.read_csv(pressure_path)
            pressure_cols = [c for c in df_pressure.columns if 'PRESSURE' in c or 'CLOCK' in c]
            df = df.merge(
                df_pressure[['PLAYER_ID', 'SEASON'] + pressure_cols],
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )
            logger.info(f"Merged pressure features: {len(pressure_cols)} columns")
        
        # Load usage data from regular season files
        logger.info("Loading usage data...")
        rs_files = list(self.data_dir.glob("regular_season_*.csv"))
        rs_data_list = []
        for rs_file in rs_files:
            try:
                season = rs_file.stem.replace("regular_season_", "")
                df_rs = pd.read_csv(rs_file)
                df_rs['SEASON'] = season
                if 'PLAYER_ID' in df_rs.columns and 'USG_PCT' in df_rs.columns:
                    rs_data_list.append(df_rs[['PLAYER_ID', 'SEASON', 'USG_PCT', 'PLAYER_NAME']])
            except Exception as e:
                logger.warning(f"Error loading {rs_file}: {e}")
                continue
        
        # Check if USG_PCT already exists in predictive dataset
        if 'USG_PCT' in df.columns:
            logger.info(f"USG_PCT already in dataset: {df['USG_PCT'].notna().sum()} values")
        else:
            # Try to load from regular season files
            if rs_data_list:
                df_rs_usage = pd.concat(rs_data_list, ignore_index=True)
                df_rs_usage = df_rs_usage.groupby(['PLAYER_ID', 'SEASON']).agg({
                    'USG_PCT': 'max',
                    'PLAYER_NAME': 'first'
                }).reset_index()
                
                df = df.merge(
                    df_rs_usage[['PLAYER_ID', 'SEASON', 'USG_PCT']],
                    on=['PLAYER_ID', 'SEASON'],
                    how='left'
                )
                logger.info(f"Merged usage data for {df['USG_PCT'].notna().sum()} player-seasons")
            else:
                logger.warning("No regular season usage data found")
                df['USG_PCT'] = np.nan
        
        return df
    
    def find_test_case(self, df: pd.DataFrame, name: str, season: str) -> Optional[pd.Series]:
        """Find a test case in the dataset."""
        # Try exact match first
        mask = (df['PLAYER_NAME'].str.contains(name, case=False, na=False)) & (df['SEASON'] == season)
        matches = df[mask]
        
        if len(matches) == 0:
            # Try partial name match
            name_parts = name.split()
            if len(name_parts) > 1:
                last_name = name_parts[-1]
                mask = (df['PLAYER_NAME'].str.contains(last_name, case=False, na=False)) & (df['SEASON'] == season)
                matches = df[mask]
        
        if len(matches) == 1:
            return matches.iloc[0]
        elif len(matches) > 1:
            logger.warning(f"Multiple matches for {name} ({season}): {len(matches)}")
            return matches.iloc[0]  # Return first match
        else:
            return None
    
    def calculate_scalability(self, row: pd.Series) -> float:
        """Calculate Scalability Coefficient."""
        iso_efg = row.get('EFG_ISO_WEIGHTED', np.nan)
        leverage_ts_delta = row.get('LEVERAGE_TS_DELTA', np.nan)
        clutch_min = row.get('CLUTCH_MIN_TOTAL', np.nan)
        
        # Normalize ISO EFG (0-1 scale, assuming max ~0.7)
        iso_normalized = iso_efg / 0.7 if not pd.isna(iso_efg) else np.nan
        
        # Normalize Leverage TS Delta (assume range -0.4 to +0.2)
        leverage_normalized = (leverage_ts_delta + 0.4) / 0.6 if not pd.isna(leverage_ts_delta) else np.nan
        
        # Normalize Clutch Minutes (divide by 100)
        clutch_normalized = clutch_min / 100.0 if not pd.isna(clutch_min) else np.nan
        
        # Calculate weighted average
        components = []
        weights = []
        
        if not pd.isna(iso_normalized):
            components.append(iso_normalized)
            weights.append(0.4)
        
        if not pd.isna(leverage_normalized):
            components.append(leverage_normalized)
            weights.append(0.4)
        elif not pd.isna(iso_normalized):
            # Use ISO EFG as proxy if Leverage TS Delta is missing
            components.append(iso_normalized)
            weights.append(0.4)
        
        if not pd.isna(clutch_normalized):
            components.append(clutch_normalized)
            weights.append(0.2)
        
        if len(components) == 0:
            return np.nan
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight == 0:
            return np.nan
        
        weights = [w / total_weight for w in weights]
        return sum(c * w for c, w in zip(components, weights))
    
    def calculate_stress_profile_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate stress profile score using current method."""
        df = df.copy()
        
        stress_features = [
            'CREATION_VOLUME_RATIO',
            'RS_PRESSURE_RESILIENCE',
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE',
            'EFG_ISO_WEIGHTED',
            'LEVERAGE_USG_DELTA',
            'RS_FTr',
        ]
        
        existing_features = [f for f in stress_features if f in df.columns]
        
        # Calculate percentiles
        for feature in existing_features:
            valid_mask = df[feature].notna()
            if valid_mask.sum() < 10:
                continue
            df.loc[valid_mask, f'{feature}_PERCENTILE'] = (
                df.loc[valid_mask, feature].rank(pct=True) * 100
            )
        
        # Average percentiles
        percentile_cols = [c for c in df.columns if c.endswith('_PERCENTILE')]
        if percentile_cols:
            df['STRESS_PROFILE_SCORE'] = df[percentile_cols].mean(axis=1)
        else:
            df['STRESS_PROFILE_SCORE'] = np.nan
        
        return df
    
    def analyze_test_case(self, df: pd.DataFrame, case_id: str, case_info: Dict) -> Dict:
        """Analyze a single test case."""
        name = case_info['name']
        season = case_info['season']
        case_type = case_info['type']
        
        logger.info(f"Analyzing {case_id}: {name} ({season})")
        
        row = self.find_test_case(df, name, season)
        if row is None:
            return {
                'case_id': case_id,
                'name': name,
                'season': season,
                'type': case_type,
                'found': False,
                'error': 'Not found in dataset'
            }
        
        # Calculate Scalability
        scalability = self.calculate_scalability(row)
        
        # Get key metrics
        metrics = {
            'case_id': case_id,
            'name': name,
            'season': season,
            'type': case_type,
            'found': True,
            'player_id': row.get('PLAYER_ID', np.nan),
            'age': row.get('AGE', np.nan),
            'usg_pct': row.get('USG_PCT', np.nan),
            'creation_volume_ratio': row.get('CREATION_VOLUME_RATIO', np.nan),
            'creation_tax': row.get('CREATION_TAX', np.nan),
            'creation_boost': row.get('CREATION_BOOST', 1.0),
            'leverage_ts_delta': row.get('LEVERAGE_TS_DELTA', np.nan),
            'leverage_usg_delta': row.get('LEVERAGE_USG_DELTA', np.nan),
            'clutch_min_total': row.get('CLUTCH_MIN_TOTAL', np.nan),
            'efg_iso_weighted': row.get('EFG_ISO_WEIGHTED', np.nan),
            'rs_pressure_resilience': row.get('RS_PRESSURE_RESILIENCE', np.nan),
            'rs_late_clock_pressure_resilience': row.get('RS_LATE_CLOCK_PRESSURE_RESILIENCE', np.nan),
            'scalability_coefficient': scalability,
            'stress_profile_score': row.get('STRESS_PROFILE_SCORE', np.nan),
        }
        
        # Check which filters would remove them
        # Convert to simple boolean values for DataFrame storage
        age_val = metrics['age']
        usg_val = metrics['usg_pct']
        leverage_val = metrics['leverage_ts_delta']
        creation_val = metrics['creation_volume_ratio']
        pressure_val = metrics['rs_pressure_resilience']
        
        filters = {
            'age_filter': pd.isna(age_val) or age_val >= 25,
            'usage_filter': pd.isna(usg_val) or (usg_val < 1.0 and usg_val >= 0.20) or (usg_val >= 20.0),
            'leverage_data_missing': pd.isna(leverage_val),
            'scalability_low': pd.isna(scalability) or scalability < 0.25,
            'creation_low': pd.isna(creation_val) or creation_val < 0.20,
            'pressure_missing': pd.isna(pressure_val),
        }
        
        # Add filter flags to metrics
        for key, value in filters.items():
            metrics[f'filter_{key}'] = value
        
        return metrics
    
    def run_validation(self):
        """Run validation on all test cases."""
        logger.info("=" * 60)
        logger.info("Phase 0: Test Case Validation")
        logger.info("=" * 60)
        
        # Load data
        df = self.load_data()
        
        # Calculate stress profile scores
        df = self.calculate_stress_profile_score(df)
        
        # Analyze each test case
        results = []
        for case_id, case_info in self.test_cases.items():
            result = self.analyze_test_case(df, case_id, case_info)
            results.append(result)
        
        # Convert to DataFrame
        df_results = pd.DataFrame(results)
        
        # Save results
        output_path = self.results_dir / "phase0_validation_results.csv"
        df_results.to_csv(output_path, index=False)
        logger.info(f"Saved validation results to {output_path}")
        
        # Generate summary report
        self.generate_report(df_results)
        
        return df_results
    
    def generate_report(self, df_results: pd.DataFrame):
        """Generate validation report."""
        report_lines = [
            "# Phase 0 Validation Report: Test Case Analysis",
            "",
            "## Executive Summary",
            "",
            f"This report validates {len(df_results)} test cases against the current detection system.",
            "",
            "---",
            "",
            "## Test Cases Found in Dataset",
            "",
            "| Case ID | Name | Season | Type | Found | Age | USG% | Leverage TS Δ | Scalability | Creation Ratio |",
            "|---------|------|--------|------|-------|-----|------|---------------|-------------|----------------|"
        ]
        
        for _, row in df_results.iterrows():
            if row['found']:
                report_lines.append(
                    f"| {row['case_id']} | {row['name']} | {row['season']} | {row['type']} | ✅ | "
                    f"{row['age']:.1f} | {row['usg_pct']:.1f}% | "
                    f"{row['leverage_ts_delta']:.3f} | {row['scalability_coefficient']:.3f} | "
                    f"{row['creation_volume_ratio']:.3f} |"
                )
            else:
                report_lines.append(
                    f"| {row['case_id']} | {row['name']} | {row['season']} | {row['type']} | ❌ | "
                    f"- | - | - | - | - |"
                )
        
        report_lines.extend([
            "",
            "---",
            "",
            "## Filter Analysis",
            "",
            "### Known Breakouts (Should Be Identified)",
            ""
        ])
        
        breakouts = df_results[df_results['type'] == 'breakout']
        for _, row in breakouts.iterrows():
            if row['found']:
                report_lines.append(f"### {row['name']} ({row['season']})")
                report_lines.append("")
                age_val = row.get('age', np.nan)
                usg_val = row.get('usg_pct', np.nan)
                leverage_val = row.get('leverage_ts_delta', np.nan)
                scalability_val = row.get('scalability_coefficient', np.nan)
                creation_val = row.get('creation_volume_ratio', np.nan)
                pressure_val = row.get('rs_pressure_resilience', np.nan)
                
                age_filter = row.get('filter_age_filter', False)
                usage_filter = row.get('filter_usage_filter', False)
                leverage_missing = row.get('filter_leverage_data_missing', False)
                scalability_low = row.get('filter_scalability_low', False)
                creation_low = row.get('filter_creation_low', False)
                pressure_missing = row.get('filter_pressure_missing', False)
                
                report_lines.append(f"- **Age Filter**: {'❌ REMOVED' if age_filter else '✅ PASS'} (Age: {age_val:.1f})")
                report_lines.append(f"- **Usage Filter**: {'❌ REMOVED' if usage_filter else '✅ PASS'} (USG%: {usg_val:.1f}%)")
                report_lines.append(f"- **Leverage Data**: {'❌ MISSING' if leverage_missing else '✅ AVAILABLE'} (Value: {leverage_val:.3f})")
                report_lines.append(f"- **Scalability**: {'❌ LOW' if scalability_low else '✅ HIGH'} (Value: {scalability_val:.3f})")
                report_lines.append(f"- **Creation Ratio**: {'❌ LOW' if creation_low else '✅ HIGH'} (Value: {creation_val:.3f})")
                report_lines.append(f"- **Pressure Data**: {'❌ MISSING' if pressure_missing else '✅ AVAILABLE'} (Value: {pressure_val:.3f})")
                report_lines.append("")
        
        report_lines.extend([
            "---",
            "",
            "## Key Findings",
            "",
            "### Data Availability",
            ""
        ])
        
        found_count = df_results['found'].sum()
        report_lines.append(f"- **Found in Dataset**: {found_count} / {len(df_results)} ({found_count/len(df_results)*100:.1f}%)")
        
        breakouts_found = breakouts['found'].sum()
        report_lines.append(f"- **Known Breakouts Found**: {breakouts_found} / {len(breakouts)} ({breakouts_found/len(breakouts)*100:.1f}%)")
        
        # Save report
        report_path = self.results_dir / "phase0_validation_report.md"
        with open(report_path, 'w') as f:
            f.write("\n".join(report_lines))
        logger.info(f"Saved validation report to {report_path}")


def main():
    validator = TestCaseValidator()
    results = validator.run_validation()
    return results


if __name__ == "__main__":
    main()

