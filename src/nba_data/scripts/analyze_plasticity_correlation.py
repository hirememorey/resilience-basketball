
import pandas as pd
import numpy as np
import logging
from tabulate import tabulate
from scipy.stats import pearsonr
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

def analyze_correlations():
    """
    Analyze relationship between Plasticity Metrics and Resilience.
    """
    plasticity_path = Path("results/plasticity_scores.csv")
    resilience_path = Path("results/resilience_scores_all.csv")
    
    if not plasticity_path.exists():
        logger.error("Plasticity scores not found. Run calculate_shot_plasticity.py first.")
        return

    df_plast = pd.read_csv(plasticity_path)
    
    if resilience_path.exists():
        df_res = pd.read_csv(resilience_path)
        # Merge if not already merged in the previous step
        if 'RESILIENCE_SCORE' not in df_plast.columns:
            df_plast = pd.merge(
                df_plast, 
                df_res[['PLAYER_ID', 'SEASON', 'RESILIENCE_SCORE']], 
                on=['PLAYER_ID', 'SEASON'],
                how='inner'
            )
    
    if 'RESILIENCE_SCORE' not in df_plast.columns:
        logger.error("No resilience scores available for correlation.")
        return

    print("\n" + "="*60)
    print("🔗 PLASTICITY vs. RESILIENCE CORRELATION ANALYSIS")
    print("="*60)
    
    metrics = ['ZONE_DISPLACEMENT', 'COUNTER_PUNCH_EFF', 'COMPRESSION_SCORE', 'RIM_DETERRENCE']
    
    correlations = []
    for metric in metrics:
        # remove NaNs
        valid_data = df_plast.dropna(subset=[metric, 'RESILIENCE_SCORE'])
        if len(valid_data) < 10:
            continue
            
        r, p_value = pearsonr(valid_data[metric], valid_data['RESILIENCE_SCORE'])
        correlations.append({
            'Metric': metric,
            'Correlation (r)': r,
            'P-Value': p_value,
            'Significance': '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else ''
        })
        
    corr_df = pd.DataFrame(correlations).sort_values('Correlation (r)', ascending=False)
    print(tabulate(corr_df, headers='keys', tablefmt='simple', floatfmt=".4f"))
    
    print("\n" + "-"*60)
    print("🏆 PLASTICITY LEADERS (Top 10 Adaptable Players)")
    print("-"*60)
    
    # Create a Composite Plasticity Score for ranking
    # Weight Counter-Punch efficiency heavily as it's the success metric
    df_plast['PLASTICITY_INDEX'] = (
        (df_plast['ZONE_DISPLACEMENT'] * 0.5) + 
        (df_plast['COUNTER_PUNCH_EFF'] * 100 * 1.0) # Scale up percentage
    )
    
    top_plasticity = df_plast.sort_values('PLASTICITY_INDEX', ascending=False).head(10)
    print(tabulate(top_plasticity[['PLAYER_NAME', 'SEASON', 'ZONE_DISPLACEMENT', 'COUNTER_PUNCH_EFF', 'PLASTICITY_INDEX', 'RESILIENCE_SCORE']], 
                   headers='keys', tablefmt='simple', floatfmt=".3f"))

    print("\n" + "-"*60)
    print("🧱 THE RIGID LIST (Bottom 10 Plasticity)")
    print("-"*60)
    
    bottom_plasticity = df_plast.sort_values('PLASTICITY_INDEX', ascending=True).head(10)
    print(tabulate(bottom_plasticity[['PLAYER_NAME', 'SEASON', 'ZONE_DISPLACEMENT', 'COUNTER_PUNCH_EFF', 'PLASTICITY_INDEX', 'RESILIENCE_SCORE']], 
                   headers='keys', tablefmt='simple', floatfmt=".3f"))

if __name__ == "__main__":
    analyze_correlations()



