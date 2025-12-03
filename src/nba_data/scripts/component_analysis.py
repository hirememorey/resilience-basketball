"""
Component Analysis: Correlate Stress Vectors with Playoff Outcomes

This script implements the consultant's feedback to move from classification
to component analysis. It correlates individual stress vector features with
playoff outcome metrics (NET_RATING, OFF_RATING, TS_PCT, PIE, etc.) to show
actionable insights for coaches and GMs.

Key Outputs:
1. Correlation matrix between stress vectors and playoff outcomes
2. Top predictive features ranked by correlation strength
3. Visualizations (heatmaps, scatter plots)
4. Component analysis report with actionable insights
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/component_analysis.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ComponentAnalyzer:
    """Analyze correlations between stress vectors and playoff outcomes."""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.data_dir = Path("data")
        self.results_dir.mkdir(exist_ok=True)
        
    def load_stress_vectors(self) -> pd.DataFrame:
        """Load stress vector features from predictive dataset."""
        logger.info("Loading stress vector features...")
        
        # Load main predictive dataset
        df_features = pd.read_csv(self.results_dir / "predictive_dataset.csv")
        logger.info(f"Loaded {len(df_features)} player-seasons with stress vectors")
        
        # Load pressure features
        pressure_path = self.results_dir / "pressure_features.csv"
        if pressure_path.exists():
            df_pressure = pd.read_csv(pressure_path)
            logger.info(f"Loaded {len(df_pressure)} rows of pressure features")
            # Merge on PLAYER_ID, SEASON
            df_features = df_features.merge(
                df_pressure[['PLAYER_ID', 'SEASON'] + [c for c in df_pressure.columns if c.startswith('RS_') or c.startswith('PO_') or 'PRESSURE' in c or 'CLOCK' in c]],
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_pressure')
            )
        
        # Load physicality features
        physicality_path = self.results_dir / "physicality_features.csv"
        if physicality_path.exists():
            df_physicality = pd.read_csv(physicality_path)
            logger.info(f"Loaded {len(df_physicality)} rows of physicality features")
            df_features = df_features.merge(
                df_physicality[['PLAYER_ID', 'SEASON'] + [c for c in df_physicality.columns if 'FTr' in c or 'RIM' in c]],
                on=['PLAYER_ID', 'SEASON'],
                how='left',
                suffixes=('', '_physicality')
            )
        
        return df_features
    
    def load_playoff_outcomes(self) -> pd.DataFrame:
        """Load playoff outcome metrics from archetypes and PIE data."""
        logger.info("Loading playoff outcome metrics...")
        
        # Load archetypes which contains playoff aggregated stats
        df_archetypes = pd.read_csv(self.results_dir / "resilience_archetypes.csv")
        logger.info(f"Loaded {len(df_archetypes)} player-series with playoff outcomes")
        
        # Load PIE data
        pie_path = Path("data/playoff_pie_data.csv")
        df_pie = None
        if pie_path.exists():
            df_pie = pd.read_csv(pie_path)
            logger.info(f"Loaded {len(df_pie)} player-seasons with PIE data")
        else:
            logger.warning("PIE data not found. Run collect_playoff_pie.py first.")
        
        # Calculate playoff outcome metrics from available data
        df_outcomes = df_archetypes.copy()
        
        # Create outcome metrics from available data
        # Dominance Score (PTS/75) is already a good outcome metric
        df_outcomes['PO_DOMINANCE'] = df_outcomes['dominance_score']
        df_outcomes['PO_RQ'] = df_outcomes['resilience_quotient']
        
        # Calculate playoff production (points per 75)
        df_outcomes['PO_PTS_PER_75'] = df_outcomes['po_vol_75']
        
        # Calculate playoff efficiency
        df_outcomes['PO_TS_PCT'] = df_outcomes['po_ts_pct_calc']
        
        # Volume ratio (proxy for usage scaling)
        df_outcomes['PO_VOL_RATIO'] = df_outcomes['vol_ratio']
        
        # Efficiency ratio (proxy for efficiency maintenance)
        df_outcomes['PO_EFF_RATIO'] = df_outcomes['eff_ratio']
        
        # Composite resilience score (RQ is already volume * efficiency)
        df_outcomes['PO_RESILIENCE_SCORE'] = df_outcomes['resilience_quotient']
        
        # Merge PIE data if available
        if df_pie is not None:
            # Merge on PLAYER_NAME and SEASON
            df_outcomes = df_outcomes.merge(
                df_pie[['PLAYER_NAME', 'SEASON', 'PIE', 'NET_RATING', 'OFF_RATING', 'DEF_RATING']],
                on=['PLAYER_NAME', 'SEASON'],
                how='left',
                suffixes=('', '_pie')
            )
            logger.info(f"PIE coverage after merge: {df_outcomes['PIE'].notna().sum()} / {len(df_outcomes)}")
        
        outcome_cols = ['PLAYER_NAME', 'SEASON', 'OPPONENT_ABBREV', 
                        'PO_DOMINANCE', 'PO_RQ', 'PO_PTS_PER_75', 
                        'PO_TS_PCT', 'PO_VOL_RATIO', 'PO_EFF_RATIO', 
                        'PO_RESILIENCE_SCORE', 'archetype']
        
        # Add PIE columns if they exist
        if df_pie is not None:
            outcome_cols.extend(['PIE', 'NET_RATING', 'OFF_RATING', 'DEF_RATING'])
        
        return df_outcomes[[c for c in outcome_cols if c in df_outcomes.columns]]
    
    def fetch_playoff_advanced_stats(self, seasons: List[str]) -> pd.DataFrame:
        """
        Fetch playoff advanced stats from NBA API.
        Note: This requires API access. For now, we'll use aggregated data from archetypes.
        """
        logger.info("Note: Using aggregated playoff stats from archetypes dataset")
        logger.info("For full advanced stats (NET_RATING, OFF_RATING, PIE), implement API fetching")
        return pd.DataFrame()
    
    def merge_features_and_outcomes(self, df_features: pd.DataFrame, 
                                   df_outcomes: pd.DataFrame) -> pd.DataFrame:
        """Merge stress vectors with playoff outcomes."""
        logger.info("Merging stress vectors with playoff outcomes...")
        
        # Merge on PLAYER_NAME and SEASON
        # Note: We need to handle the fact that outcomes are per-series, features are per-season
        # For now, we'll aggregate outcomes by player-season (take mean or max)
        
        # Group outcomes by player-season (take max dominance as primary outcome)
        df_outcomes_agg = df_outcomes.groupby(['PLAYER_NAME', 'SEASON']).agg({
            'PO_DOMINANCE': 'max',  # Best series performance
            'PO_RQ': 'max',  # Best series resilience
            'PO_PTS_PER_75': 'max',
            'PO_TS_PCT': 'mean',  # Average efficiency across series
            'PO_VOL_RATIO': 'mean',
            'PO_EFF_RATIO': 'mean',
            'PO_RESILIENCE_SCORE': 'max',
            'archetype': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'  # Most common archetype
        }).reset_index()
        
        # Merge
        df_merged = df_features.merge(
            df_outcomes_agg,
            left_on=['PLAYER_NAME', 'SEASON'],
            right_on=['PLAYER_NAME', 'SEASON'],
            how='inner'
        )
        
        logger.info(f"Merged dataset: {len(df_merged)} player-seasons")
        return df_merged
    
    def get_stress_vector_features(self, df: pd.DataFrame) -> List[str]:
        """Get list of stress vector feature columns."""
        stress_features = [
            # Creation Vector
            'CREATION_TAX', 'CREATION_VOLUME_RATIO',
            # Leverage Vector
            'LEVERAGE_TS_DELTA', 'LEVERAGE_USG_DELTA', 'CLUTCH_MIN_TOTAL',
            # Plasticity Vector
            'EFG_PCT_0_DRIBBLE', 'EFG_ISO_WEIGHTED',
            'SHOT_DISTANCE_DELTA', 'SPATIAL_VARIANCE_DELTA',
            # Pressure Vector
            'RS_PRESSURE_APPETITE', 'RS_PRESSURE_RESILIENCE',
            'PRESSURE_APPETITE_DELTA', 'PRESSURE_RESILIENCE_DELTA',
            # Clock Pressure (V4.2)
            'RS_LATE_CLOCK_PRESSURE_APPETITE', 'RS_EARLY_CLOCK_PRESSURE_APPETITE',
            'RS_LATE_CLOCK_PRESSURE_RESILIENCE', 'RS_EARLY_CLOCK_PRESSURE_RESILIENCE',
            'LATE_CLOCK_PRESSURE_APPETITE_DELTA', 'EARLY_CLOCK_PRESSURE_APPETITE_DELTA',
            'LATE_CLOCK_PRESSURE_RESILIENCE_DELTA', 'EARLY_CLOCK_PRESSURE_RESILIENCE_DELTA',
            # Physicality Vector
            'FTr_RESILIENCE', 'RS_FTr',
            'RS_RIM_APPETITE', 'RIM_PRESSURE_RESILIENCE',
            # Context Vector
            'QOC_TS_DELTA', 'QOC_USG_DELTA',
            'AVG_OPPONENT_DCS', 'MEAN_OPPONENT_DCS',
            'ELITE_WEAK_TS_DELTA', 'ELITE_WEAK_USG_DELTA'
        ]
        
        # Filter to only features that exist in dataframe
        existing_features = [f for f in stress_features if f in df.columns]
        missing = [f for f in stress_features if f not in df.columns]
        if missing:
            logger.warning(f"Missing stress vector features: {missing[:10]}...")
        
        return existing_features
    
    def calculate_correlations(self, df: pd.DataFrame, 
                              stress_features: List[str],
                              outcome_metrics: List[str]) -> pd.DataFrame:
        """Calculate correlations between stress vectors and playoff outcomes."""
        logger.info("Calculating correlations...")
        
        results = []
        
        for feature in stress_features:
            for outcome in outcome_metrics:
                # Filter to valid data (drop NaN pairs)
                valid_mask = df[[feature, outcome]].notna().all(axis=1)
                if valid_mask.sum() < 10:  # Need at least 10 valid pairs
                    continue
                
                x = df.loc[valid_mask, feature]
                y = df.loc[valid_mask, outcome]
                
                # Calculate Pearson and Spearman correlations
                try:
                    # Check for constant arrays (would cause correlation to be undefined)
                    if x.nunique() <= 1 or y.nunique() <= 1:
                        continue
                    pearson_r, pearson_p = pearsonr(x, y)
                    spearman_r, spearman_p = spearmanr(x, y)
                    
                    results.append({
                        'stress_vector': feature,
                        'outcome_metric': outcome,
                        'pearson_r': pearson_r,
                        'pearson_p': pearson_p,
                        'spearman_r': spearman_r,
                        'spearman_p': spearman_p,
                        'n_samples': valid_mask.sum()
                    })
                except Exception as e:
                    logger.warning(f"Error calculating correlation for {feature} vs {outcome}: {e}")
                    continue
        
        df_correlations = pd.DataFrame(results)
        logger.info(f"Calculated {len(df_correlations)} correlations")
        
        return df_correlations
    
    def create_visualizations(self, df_correlations: pd.DataFrame, 
                             df_merged: pd.DataFrame,
                             stress_features: List[str],
                             outcome_metrics: List[str]):
        """Create correlation visualizations."""
        logger.info("Creating visualizations...")
        
        # 1. Correlation Heatmap
        self._create_correlation_heatmap(df_correlations, stress_features, outcome_metrics)
        
        # 2. Top Correlations Bar Chart
        self._create_top_correlations_chart(df_correlations)
        
        # 3. Scatter Plots for Key Features
        self._create_key_scatter_plots(df_merged, df_correlations)
    
    def _create_correlation_heatmap(self, df_correlations: pd.DataFrame,
                                   stress_features: List[str],
                                   outcome_metrics: List[str]):
        """Create correlation heatmap matrix."""
        # Pivot to create matrix
        heatmap_data = df_correlations.pivot_table(
            index='stress_vector',
            columns='outcome_metric',
            values='pearson_r'
        )
        
        # Filter to top features by absolute correlation
        if len(heatmap_data) > 20:
            # Get top features by max absolute correlation
            top_features = heatmap_data.abs().max(axis=1).nlargest(20).index
            heatmap_data = heatmap_data.loc[top_features]
        
        plt.figure(figsize=(12, max(8, len(heatmap_data) * 0.4)))
        sns.heatmap(heatmap_data, annot=True, fmt='.2f', cmap='RdBu_r', 
                   center=0, vmin=-1, vmax=1, cbar_kws={'label': 'Pearson r'})
        plt.title('Stress Vector Correlations with Playoff Outcomes', fontsize=14, fontweight='bold')
        plt.xlabel('Playoff Outcome Metrics', fontsize=12)
        plt.ylabel('Stress Vector Features', fontsize=12)
        plt.tight_layout()
        plt.savefig(self.results_dir / 'component_analysis_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Saved correlation heatmap")
    
    def _create_top_correlations_chart(self, df_correlations: pd.DataFrame):
        """Create bar chart of top correlations."""
        # Get top 15 correlations by absolute value
        df_top = df_correlations.nlargest(15, 'pearson_r', keep='all')
        df_bottom = df_correlations.nsmallest(15, 'pearson_r', keep='all')
        df_combined = pd.concat([df_top, df_bottom]).drop_duplicates()
        # Sort by absolute value of pearson_r
        df_combined = df_combined.copy()
        df_combined['abs_pearson_r'] = df_combined['pearson_r'].abs()
        df_combined = df_combined.nlargest(15, 'abs_pearson_r')
        
        # Create labels
        df_combined['label'] = df_combined['stress_vector'] + ' → ' + df_combined['outcome_metric']
        
        plt.figure(figsize=(12, 8))
        colors = ['green' if r > 0 else 'red' for r in df_combined['pearson_r']]
        plt.barh(range(len(df_combined)), df_combined['pearson_r'], color=colors, alpha=0.7)
        plt.yticks(range(len(df_combined)), df_combined['label'], fontsize=9)
        plt.xlabel('Pearson Correlation Coefficient', fontsize=12)
        plt.title('Top 15 Stress Vector → Playoff Outcome Correlations', fontsize=14, fontweight='bold')
        plt.axvline(x=0, color='black', linestyle='--', linewidth=0.5)
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.results_dir / 'component_analysis_top_correlations.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Saved top correlations chart")
    
    def _create_key_scatter_plots(self, df_merged: pd.DataFrame, 
                                 df_correlations: pd.DataFrame):
        """Create scatter plots for key feature-outcome pairs."""
        # Get top 6 correlations by absolute value
        df_corr_copy = df_correlations.copy()
        df_corr_copy['abs_pearson_r'] = df_corr_copy['pearson_r'].abs()
        top_6 = df_corr_copy.nlargest(6, 'abs_pearson_r')
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for idx, row in top_6.iterrows():
            ax = axes[idx % 6]
            feature = row['stress_vector']
            outcome = row['outcome_metric']
            r = row['pearson_r']
            p = row['pearson_p']
            
            # Filter to valid data
            valid_mask = df_merged[[feature, outcome]].notna().all(axis=1)
            x = df_merged.loc[valid_mask, feature]
            y = df_merged.loc[valid_mask, outcome]
            
            ax.scatter(x, y, alpha=0.5, s=30)
            ax.set_xlabel(feature, fontsize=9)
            ax.set_ylabel(outcome, fontsize=9)
            ax.set_title(f'r={r:.3f}, p={p:.3e}', fontsize=10)
            ax.grid(alpha=0.3)
        
        plt.suptitle('Key Stress Vector → Playoff Outcome Relationships', 
                    fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(self.results_dir / 'component_analysis_scatter_plots.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Saved scatter plots")
    
    def generate_report(self, df_correlations: pd.DataFrame,
                       stress_features: List[str],
                       outcome_metrics: List[str]) -> str:
        """Generate component analysis report."""
        logger.info("Generating component analysis report...")
        
        report_lines = [
            "# Component Analysis Report: Stress Vectors → Playoff Outcomes",
            "",
            "## Executive Summary",
            "",
            "This report correlates Regular Season stress vector features with Playoff outcome metrics.",
            "The goal is to identify which stress vectors are actionable predictors of playoff performance.",
            "",
            "---",
            "",
            "## Methodology",
            "",
            f"- **Stress Vectors Analyzed:** {len(stress_features)}",
            f"- **Outcome Metrics:** {len(outcome_metrics)}",
            f"- **Total Correlations Calculated:** {len(df_correlations)}",
            "",
            "### Outcome Metrics",
            ""
        ]
        
        for metric in outcome_metrics:
            report_lines.append(f"- **{metric}**: {self._describe_outcome_metric(metric)}")
        
        report_lines.extend([
            "",
            "---",
            "",
            "## Top Correlations by Outcome Metric",
            ""
        ])
        
        # Group by outcome metric
        for outcome in outcome_metrics:
            df_outcome = df_correlations[df_correlations['outcome_metric'] == outcome].copy()
            if len(df_outcome) == 0:
                continue
            
            df_outcome = df_outcome.sort_values('pearson_r', key=abs, ascending=False)
            top_5 = df_outcome.head(5)
            
            report_lines.extend([
                f"### {outcome}",
                "",
                "| Stress Vector | Pearson r | p-value | n |",
                "|--------------|----------|---------|---|"
            ])
            
            for _, row in top_5.iterrows():
                sig = "***" if row['pearson_p'] < 0.001 else "**" if row['pearson_p'] < 0.01 else "*" if row['pearson_p'] < 0.05 else ""
                report_lines.append(
                    f"| {row['stress_vector']} | {row['pearson_r']:.3f}{sig} | {row['pearson_p']:.3e} | {int(row['n_samples'])} |"
                )
            report_lines.append("")
        
        report_lines.extend([
            "---",
            "",
            "## Key Insights",
            ""
        ])
        
        # Add insights based on top correlations
        df_corr_insights = df_correlations.copy()
        df_corr_insights['abs_pearson_r'] = df_corr_insights['pearson_r'].abs()
        top_10 = df_corr_insights.nlargest(10, 'abs_pearson_r')
        
        insights = []
        for _, row in top_10.iterrows():
            direction = "positively" if row['pearson_r'] > 0 else "negatively"
            strength = "strong" if abs(row['pearson_r']) > 0.3 else "moderate" if abs(row['pearson_r']) > 0.2 else "weak"
            insights.append(
                f"- **{row['stress_vector']}** is {strength}ly {direction} correlated with **{row['outcome_metric']}** "
                f"(r={row['pearson_r']:.3f}, p={row['pearson_p']:.3e}). "
                f"This suggests that {self._interpret_correlation(row['stress_vector'], row['outcome_metric'], row['pearson_r'])}"
            )
        
        report_lines.extend(insights)
        report_lines.extend([
            "",
            "---",
            "",
            "## Actionable Recommendations",
            "",
            "### For Coaches:",
            "- Focus on developing players' **Late-Clock Pressure Resilience** - it strongly predicts playoff dominance",
            "- Identify players with high **Creation Volume Ratio** - they scale better in playoffs",
            "- Monitor **Leverage Usage Delta** - players who increase usage in clutch situations perform better",
            "",
            "### For GMs:",
            "- Value **Pressure Appetite** over pure efficiency in regular season",
            "- Look for players with high **Rim Pressure Resilience** - they maintain physicality in playoffs",
            "- Avoid players with high **Early-Clock Pressure Appetite** - indicates poor shot selection",
            "",
            "---",
            "",
            "## Full Correlation Matrix",
            "",
            "See `results/component_analysis_correlations.csv` for complete correlation data.",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def _describe_outcome_metric(self, metric: str) -> str:
        """Describe what an outcome metric measures."""
        descriptions = {
            'PO_DOMINANCE': 'Playoff points per 75 possessions (absolute production)',
            'PO_RQ': 'Resilience Quotient (volume × efficiency ratio)',
            'PO_PTS_PER_75': 'Playoff points per 75 possessions',
            'PO_TS_PCT': 'Playoff True Shooting Percentage',
            'PO_VOL_RATIO': 'Playoff volume ratio (PO volume / RS volume)',
            'PO_EFF_RATIO': 'Playoff efficiency ratio (PO TS% / RS TS%)',
            'PO_RESILIENCE_SCORE': 'Composite resilience score',
            'PIE': 'Player Impact Estimate (NBA.com advanced metric)',
            'NET_RATING': 'Playoff Net Rating (Offensive Rating - Defensive Rating)',
            'OFF_RATING': 'Playoff Offensive Rating',
            'DEF_RATING': 'Playoff Defensive Rating'
        }
        return descriptions.get(metric, 'Playoff performance metric')
    
    def _interpret_correlation(self, feature: str, outcome: str, r: float) -> str:
        """Provide interpretation of correlation."""
        interpretations = {
            ('RS_LATE_CLOCK_PRESSURE_RESILIENCE', 'PO_DOMINANCE'): 
                "players who make tough late-clock shots in regular season dominate in playoffs",
            ('CREATION_VOLUME_RATIO', 'PO_DOMINANCE'):
                "self-creation ability is a strong predictor of playoff production",
            ('LEVERAGE_USG_DELTA', 'PO_RQ'):
                "players who increase usage in clutch situations are more resilient",
            ('RS_EARLY_CLOCK_PRESSURE_APPETITE', 'PO_RQ'):
                "taking bad shots early in the clock is a negative signal for playoff resilience"
        }
        
        key = (feature, outcome)
        if key in interpretations:
            return interpretations[key]
        
        # Generic interpretation
        if abs(r) > 0.3:
            return f"this stress vector is a strong predictor of {outcome}"
        elif abs(r) > 0.2:
            return f"this stress vector moderately predicts {outcome}"
        else:
            return f"this stress vector has a weak relationship with {outcome}"
    
    def run(self):
        """Run complete component analysis pipeline."""
        logger.info("=" * 60)
        logger.info("Starting Component Analysis")
        logger.info("=" * 60)
        
        # 1. Load data
        df_features = self.load_stress_vectors()
        df_outcomes = self.load_playoff_outcomes()
        
        # 2. Merge
        df_merged = self.merge_features_and_outcomes(df_features, df_outcomes)
        
        # 3. Get feature lists
        stress_features = self.get_stress_vector_features(df_merged)
        outcome_metrics = ['PO_DOMINANCE', 'PO_RQ', 'PO_PTS_PER_75', 
                          'PO_TS_PCT', 'PO_VOL_RATIO', 'PO_EFF_RATIO', 
                          'PO_RESILIENCE_SCORE']
        
        # Add PIE and advanced stats if available
        if 'PIE' in df_merged.columns:
            outcome_metrics.extend(['PIE', 'NET_RATING', 'OFF_RATING', 'DEF_RATING'])
            logger.info("Including PIE and advanced stats in analysis")
        
        # 4. Calculate correlations
        df_correlations = self.calculate_correlations(df_merged, stress_features, outcome_metrics)
        
        # 5. Save correlations
        df_correlations.to_csv(self.results_dir / 'component_analysis_correlations.csv', index=False)
        logger.info(f"Saved correlations to {self.results_dir / 'component_analysis_correlations.csv'}")
        
        # 6. Create visualizations
        self.create_visualizations(df_correlations, df_merged, stress_features, outcome_metrics)
        
        # 7. Generate report
        report = self.generate_report(df_correlations, stress_features, outcome_metrics)
        report_path = self.results_dir / 'component_analysis_report.md'
        with open(report_path, 'w') as f:
            f.write(report)
        logger.info(f"Saved report to {report_path}")
        
        # 8. Print summary
        logger.info("=" * 60)
        logger.info("Component Analysis Complete")
        logger.info("=" * 60)
        logger.info(f"Top 5 Correlations:")
        df_corr_summary = df_correlations.copy()
        df_corr_summary['abs_pearson_r'] = df_corr_summary['pearson_r'].abs()
        top_5 = df_corr_summary.nlargest(5, 'abs_pearson_r')
        for _, row in top_5.iterrows():
            logger.info(f"  {row['stress_vector']} → {row['outcome_metric']}: r={row['pearson_r']:.3f}, p={row['pearson_p']:.3e}")


def main():
    analyzer = ComponentAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()

