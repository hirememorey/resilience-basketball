"""
Calculate Data-Driven Dependence Score Thresholds

Calculate 33rd and 66th percentiles of Dependence Score for star-level players
(Usage > 25%) to determine "Low", "Moderate", and "High" dependence thresholds.
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))

from predict_conditional_archetype import ConditionalArchetypePredictor
from calculate_dependence_score import calculate_dependence_score

def calculate_dependence_thresholds():
    """Calculate data-driven thresholds for Dependence Score."""
    
    predictor = ConditionalArchetypePredictor()
    
    # Load full dataset
    df = predictor.df_features.copy()
    
    # Filter to star-level players (Usage > 25%)
    star_players = df[df['USG_PCT'] > 0.25].copy()
    
    print("=" * 80)
    print("Dependence Score Threshold Calculation")
    print("=" * 80)
    print()
    print(f"Total player-seasons: {len(df)}")
    print(f"Star-level players (USG_PCT > 25%): {len(star_players)}")
    print()
    
    # Calculate dependence scores for all star players
    print("Calculating dependence scores for star-level players...")
    dependence_scores = []
    
    for idx, row in star_players.iterrows():
        result = calculate_dependence_score(row)
        if result['dependence_score'] is not None:
            dependence_scores.append({
                'PLAYER_NAME': row.get('PLAYER_NAME', 'Unknown'),
                'SEASON': row.get('SEASON', 'Unknown'),
                'USG_PCT': row.get('USG_PCT', None),
                'DEPENDENCE_SCORE': result['dependence_score'],
                'ASSISTED_FGM_PCT': result['assisted_fgm_pct'],
                'OPEN_SHOT_FREQUENCY': result['open_shot_frequency'],
                'SELF_CREATED_USAGE_RATIO': result['self_created_usage_ratio']
            })
    
    df_dependence = pd.DataFrame(dependence_scores)
    
    print(f"Dependence scores calculated: {len(df_dependence)}/{len(star_players)} ({len(df_dependence)/len(star_players)*100:.1f}%)")
    print()
    
    if len(df_dependence) == 0:
        print("❌ No dependence scores calculated. Cannot determine thresholds.")
        return None
    
    # Calculate percentiles
    dependence_scores_array = df_dependence['DEPENDENCE_SCORE'].dropna()
    
    print("=" * 80)
    print("Dependence Score Distribution (Star-Level Players, USG_PCT > 25%)")
    print("=" * 80)
    print()
    print(f"Total with dependence scores: {len(dependence_scores_array)}")
    print(f"Mean: {dependence_scores_array.mean():.4f}")
    print(f"Median: {dependence_scores_array.median():.4f}")
    print(f"Std Dev: {dependence_scores_array.std():.4f}")
    print()
    print("Percentiles:")
    print(f"  10th: {dependence_scores_array.quantile(0.10):.4f}")
    print(f"  25th: {dependence_scores_array.quantile(0.25):.4f}")
    print(f"  33rd: {dependence_scores_array.quantile(0.33):.4f} ← Low/Moderate threshold")
    print(f"  50th (Median): {dependence_scores_array.quantile(0.50):.4f}")
    print(f"  66th: {dependence_scores_array.quantile(0.66):.4f} ← Moderate/High threshold")
    print(f"  75th: {dependence_scores_array.quantile(0.75):.4f}")
    print(f"  90th: {dependence_scores_array.quantile(0.90):.4f}")
    print()
    
    # Data-driven thresholds
    low_threshold = dependence_scores_array.quantile(0.33)
    high_threshold = dependence_scores_array.quantile(0.66)
    
    print("=" * 80)
    print("Data-Driven Thresholds")
    print("=" * 80)
    print()
    print(f"Low Dependence: < {low_threshold:.4f} (Bottom 33%)")
    print(f"Moderate Dependence: {low_threshold:.4f} - {high_threshold:.4f} (33rd-66th percentile)")
    print(f"High Dependence: ≥ {high_threshold:.4f} (Top 33%)")
    print()
    
    # Categorize players
    df_dependence['DEPENDENCE_CATEGORY'] = pd.cut(
        df_dependence['DEPENDENCE_SCORE'],
        bins=[0, low_threshold, high_threshold, 1.0],
        labels=['Low', 'Moderate', 'High'],
        include_lowest=True
    )
    
    print("Distribution by Category:")
    print(df_dependence['DEPENDENCE_CATEGORY'].value_counts().sort_index())
    print()
    
    # Show examples
    print("=" * 80)
    print("Example Players by Category")
    print("=" * 80)
    print()
    
    for category in ['Low', 'Moderate', 'High']:
        category_players = df_dependence[df_dependence['DEPENDENCE_CATEGORY'] == category].sort_values('DEPENDENCE_SCORE')
        print(f"\n{category} Dependence (n={len(category_players)}):")
        if category == 'Low':
            # Show top 5 (lowest dependence)
            examples = category_players.head(5)
        elif category == 'High':
            # Show top 5 (highest dependence)
            examples = category_players.tail(5)
        else:
            # Show middle examples
            examples = category_players.iloc[len(category_players)//2-2:len(category_players)//2+3]
        
        for _, player in examples.iterrows():
            print(f"  {player['PLAYER_NAME']} ({player['SEASON']}): {player['DEPENDENCE_SCORE']:.3f} "
                  f"(Assisted: {player['ASSISTED_FGM_PCT']:.1%} if not None else 'N/A', "
                  f"Open: {player['OPEN_SHOT_FREQUENCY']:.1%} if not None else 'N/A', "
                  f"Self-Created: {player['SELF_CREATED_USAGE_RATIO']:.1%} if not None else 'N/A')")
    
    # Save results
    output_path = Path("results") / "dependence_score_thresholds.csv"
    df_dependence.to_csv(output_path, index=False)
    print(f"\nResults saved to: {output_path}")
    
    # Save threshold values
    thresholds_path = Path("results") / "dependence_thresholds.json"
    import json
    thresholds = {
        'low_threshold': float(low_threshold),
        'high_threshold': float(high_threshold),
        'percentile_33': float(dependence_scores_array.quantile(0.33)),
        'percentile_66': float(dependence_scores_array.quantile(0.66)),
        'mean': float(dependence_scores_array.mean()),
        'median': float(dependence_scores_array.median()),
        'std': float(dependence_scores_array.std()),
        'n_star_players': len(df_dependence),
        'n_total_players': len(df)
    }
    with open(thresholds_path, 'w') as f:
        json.dump(thresholds, f, indent=2)
    print(f"Thresholds saved to: {thresholds_path}")
    
    return thresholds

if __name__ == "__main__":
    thresholds = calculate_dependence_thresholds()
    if thresholds:
        print("\n" + "=" * 80)
        print("Recommended Thresholds for 2D Risk Matrix")
        print("=" * 80)
        print(f"\nLow Dependence: < {thresholds['low_threshold']:.4f}")
        print(f"High Dependence: ≥ {thresholds['high_threshold']:.4f}")
        print(f"\nThese thresholds should replace the fixed 0.30/0.70 values.")

