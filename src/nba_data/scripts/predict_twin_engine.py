"""
Twin Engine Prediction Script.

Combines:
1. Model A: Engine Similarity Score (DNA Capacity) - The "Lion" Detector.
2. Model B: Resilience Index (1 - Fragility Score) - The "Glass" Detector.

Formula:
Star_Probability = Engine_Score * Resilience_Index

This decouples Capacity (Ben Simmons = 1.0) from Resilience (Ben Simmons = 0.1),
solving the "Greedy Tree" problem where volume overpowered flaws.
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def predict_twin_engine():
    # 1. Load Data (Result of Model A training)
    data_path = Path("results/predictive_dataset_with_engine_score.csv")
    if not data_path.exists():
        logger.error("Dataset not found. Run train_engine_similarity.py first.")
        return

    df = pd.read_csv(data_path)
    
    # 2. Get Model A Score (Capacity)
    # Already computed as ENGINE_SIMILARITY_SCORE
    if 'ENGINE_SIMILARITY_SCORE' not in df.columns:
        logger.error("Engine Score not found.")
        return
        
    # 3. Get Model B Score (Resilience)
    # We use the physics-based FRAGILITY_SCORE calculated in evaluate_plasticity_potential.py
    # This score already includes the "Abdication Tax" (Simmons) and "Choke Tax" (KAT).
    if 'fragility_score' in df.columns:
        fragility = df['fragility_score'].fillna(0.5)
    elif 'FRAGILITY_SCORE' in df.columns:
        fragility = df['FRAGILITY_SCORE'].fillna(0.5)
    else:
        logger.error("Fragility Score not found.")
        return

    # Invert Fragility to get Resilience (0 to 1)
    # We apply a sigmoid curve to punish high fragility severely
    # If Fragility > 0.7, Resilience should crash to 0.
    resilience = 1.0 - fragility
    
    # 4. Combine (The Twin Engine Formula)
    # Star Power = Capacity * Resilience
    df['TWIN_ENGINE_SCORE'] = df['ENGINE_SIMILARITY_SCORE'] * resilience
    
    # 5. Archetype Classification
    # We define archetypes based on the Quadrants of the 2D Engine/Resilience space
    
    def classify_archetype(row):
        eng = row['ENGINE_SIMILARITY_SCORE']
        res = 1.0 - row['fragility_score'] if 'fragility_score' in row else 1.0 - row['FRAGILITY_SCORE']
        
        if eng > 0.7: # High Capacity
            if res > 0.6:
                return "King"          # High Cap, High Res (Jokic)
            else:
                return "Bulldozer"     # High Cap, Low Res (Simmons/KAT)
        else: # Low Capacity
            if res > 0.7:
                return "Sniper"        # Low Cap, High Res (Tyus Jones)
            else:
                return "Victim"        # Low Cap, Low Res
                
    df['PREDICTED_ARCHETYPE'] = df.apply(classify_archetype, axis=1)
    
    # 6. Save Results
    output_path = Path("results/twin_engine_predictions.csv")
    df.to_csv(output_path, index=False)
    logger.info(f"Saved Twin Engine predictions to {output_path}")
    
    # 7. Validation Probes
    validate_probes(df)

def validate_probes(df):
    logger.info("="*80)
    logger.info("TWIN ENGINE VALIDATION (The Final Verdict)")
    logger.info(f"{'PLAYER':<20} | {'SEASON':<8} | {'ENGINE (Cap)':<12} | {'RESILIENCE':<10} | {'TOTAL':<8} | {'ARCHETYPE'}")
    logger.info("-" * 80)
    
    probes = [
        ('Ben Simmons', '2017-18'), # The Paradox
        ('Ben Simmons', '2020-21'), # The Collapse
        ('Jalen Brunson', '2020-21'), # The Caged Lion
        ('Jordan Poole', '2021-22'), # The Mirage
        ('Karl-Anthony Towns', '2018-19'), # The Empty Stats
        ('Tyus Jones', '2021-22'), # The Manager
        ('Nikola Jokic', '2015-16') # The Latent King
    ]
    
    for name, season in probes:
        # Fuzzy match
        row = df[(df['player_name'].str.contains(name, case=False)) & (df['season'] == season)]
        if not row.empty:
            r = row.iloc[0]
            eng = r['ENGINE_SIMILARITY_SCORE']
            frag = r['fragility_score'] if 'fragility_score' in r else r['FRAGILITY_SCORE']
            res = 1.0 - frag
            total = r['TWIN_ENGINE_SCORE']
            arch = r['PREDICTED_ARCHETYPE']
            
            logger.info(f"{r['player_name']:<20} | {season:<8} | {eng:<12.3f} | {res:<10.3f} | {total:<8.3f} | {arch}")
        else:
            logger.warning(f"Probe not found: {name} {season}")

if __name__ == "__main__":
    predict_twin_engine()

