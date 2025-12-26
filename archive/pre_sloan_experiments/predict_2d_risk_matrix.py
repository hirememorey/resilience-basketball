"""
2D Risk Matrix Generator.

This script synthesizes the Two-Clock System:
1. The Crucible (Current Viability): Probability of NOT being a Liability.
2. The Telescope (Future Potential): Predicted Peak Future PIE (on Projected Avatar).

It generates the final classification:
- Franchise Cornerstone (High Viability, High Potential)
- Latent Star (Low Viability, High Potential)
- Win-Now Piece (High Viability, Low Potential)
- Ghost/Avoid (Low Viability, Low Potential)

Output:
    results/risk_matrix_analysis.csv
"""

import pandas as pd
import numpy as np
import joblib
import logging
import sys
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def load_data():
    """Load both raw RS data and Projected Avatars."""
    # Raw Data (for Crucible)
    raw_path = Path("data/crucible_dataset_full.csv")
    if not raw_path.exists():
        logger.error(f"{raw_path.name} not found. Run build_crucible_dataset.py first.")
        raw_path = Path("data/training_dataset.csv")
    df_raw = pd.read_csv(raw_path)
    
    if 'USG_PCT' not in df_raw.columns and 'usg_pct_vs_top10' in df_raw.columns:
        logger.info("Renaming 'usg_pct_vs_top10' to 'USG_PCT' in raw data.")
        df_raw.rename(columns={'usg_pct_vs_top10': 'USG_PCT'}, inplace=True)
        
    # Projected Data (for Telescope)
    proj_path = Path("data/projected_telescope_dataset.csv")
    if not proj_path.exists():
        logger.error("Projected dataset not found. Run project_player_avatars.py first.")
        sys.exit(1)
    df_proj = pd.read_csv(proj_path)
    
    return df_raw, df_proj

def get_crucible_score(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Run the Crucible Model to get Viability Score."""
    # Load Crucible Model
    model_path = Path("models/resilience_xgb_rfe_15.pkl")
    if not model_path.exists():
        model_path = Path("models/resilience_xgb.pkl")
    
    if not model_path.exists():
        logger.error("Crucible model not found.")
        sys.exit(1)
        
    model = joblib.load(model_path)
    
    # Get features expected by model
    # We need to be careful about feature alignment
    if hasattr(model, 'feature_names_in_'):
        features = list(model.feature_names_in_)
    else:
        # Fallback to RFE features if available
        try:
            with open("results/rfe_model_results_10.json", 'r') as f:
                features = json.load(f)['features']
        except:
            # Fallback to known list
            features = [
                'LEVERAGE_USG_DELTA', 'EFG_PCT_0_DRIBBLE', 'LATE_CLOCK_PRESSURE_APPETITE_DELTA',
                'USG_PCT', 'USG_PCT_X_CREATION_VOLUME_RATIO', 'USG_PCT_X_LEVERAGE_USG_DELTA',
                'USG_PCT_X_RS_PRESSURE_APPETITE', 'USG_PCT_X_EFG_ISO_WEIGHTED',
                'PREV_RS_PRESSURE_RESILIENCE', 'NEGATIVE_SIGNAL_COUNT'
            ]
    
    # Ensure features exist (fill 0 for missing)
    X = df_raw.copy()
    for f in features:
        if f not in X.columns:
            X[f] = 0
            
    # Predict Probabilities
    probs = model.predict_proba(X[features])
    
    # We need to know which class is which.
    # Load encoder
    encoder_path = Path("models/archetype_encoder_rfe_15.pkl")
    if not encoder_path.exists():
        encoder_path = Path("models/archetype_encoder.pkl")
    
    if encoder_path.exists():
        encoder = joblib.load(encoder_path)
        classes = encoder.classes_
        logger.info(f"Crucible Classes: {classes}")
        
        # Define "Viable" classes: King, Bulldozer, Sniper, Hub, Connector
        # Define "Liability" classes: Liability, Victim
        # Let's map "Liability" index
        # A simpler heuristic: Viability = 1 - Prob(Liability/Victim)
        
        # Find indices
        liability_indices = [i for i, c in enumerate(classes) if 'Liability' in c or 'Victim' in c]
        
        # Sum probabilities of being a liability
        liability_probs = np.sum(probs[:, liability_indices], axis=1)
        viability_scores = 1.0 - liability_probs
    else:
        logger.warning("No encoder found. Cannot map probabilities. Using raw max prob?")
        # Fallback if no encoder: Assume class 0 is bad? Too risky.
        # Let's assume the model orders classes.
        # But for now, if encoder fails, we can't generate specific scores.
        # Assuming encoder exists as trained by existing pipeline.
        viability_scores = np.zeros(len(df_raw))

    df_raw['CRUCIBLE_SCORE'] = viability_scores
    return df_raw[['PLAYER_ID', 'SEASON', 'CRUCIBLE_SCORE']]

def get_telescope_score(df_proj: pd.DataFrame) -> pd.DataFrame:
    """Run the Telescope Model on Projected Avatars."""
    model_path = Path("models/telescope_model.pkl")
    model = joblib.load(model_path)
    
    # Load feature list
    feature_path = Path("models/telescope_features.json")
    if feature_path.exists():
        with open(feature_path, 'r') as f:
            features = json.load(f)
    else:
        # Fallback
        features = [
             'CREATION_TAX', 'CREATION_VOLUME_RATIO', 'LEVERAGE_USG_DELTA', 
             'LEVERAGE_TS_DELTA', 'EFG_ISO_WEIGHTED', 'USG_PCT', 
             'DEPENDENCE_SCORE', 'AGE', 
             'USG_PCT_X_CREATION_VOLUME_RATIO', 'USG_PCT_X_LEVERAGE_USG_DELTA'
        ]
        
    X = df_proj.copy()
    for f in features:
        if f not in X.columns:
            X[f] = 0
            
    preds = model.predict(X[features])
    df_proj['TELESCOPE_SCORE'] = preds
    return df_proj[['PLAYER_ID', 'SEASON', 'TELESCOPE_SCORE']]

def main():
    logger.info("Generating 2D Risk Matrix...")
    
    df_raw, df_proj = load_data()
    
    # 1. Get Crucible Scores
    logger.info("Running Crucible Engine...")
    df_crucible = get_crucible_score(df_raw)
    
    # 2. Get Telescope Scores
    logger.info("Running Telescope Engine...")
    df_telescope = get_telescope_score(df_proj)
    
    # 3. Merge
    df_final = pd.merge(df_raw[['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'AGE', 'USG_PCT']], 
                       df_crucible, on=['PLAYER_ID', 'SEASON'])
    df_final = pd.merge(df_final, df_telescope, on=['PLAYER_ID', 'SEASON'])
    
    # 4. Categorize
    # Calculate medians for thresholds
    c_median = df_final['CRUCIBLE_SCORE'].median()
    t_median = df_final['TELESCOPE_SCORE'].median()
    
    logger.info(f"Thresholds -> Viability: {c_median:.4f}, Potential: {t_median:.4f}")
    
    def classify(row):
        high_c = row['CRUCIBLE_SCORE'] >= c_median
        high_t = row['TELESCOPE_SCORE'] >= t_median
        
        if high_c and high_t:
            return "Franchise Cornerstone"
        elif not high_c and high_t:
            return "Latent Star"
        elif high_c and not high_t:
            return "Win-Now Piece"
        else:
            return "Ghost/Avoid"
            
    df_final['RISK_CATEGORY'] = df_final.apply(classify, axis=1)
    
    # 5. Save
    output_path = Path("results/risk_matrix_analysis.csv")
    output_path.parent.mkdir(exist_ok=True)
    df_final.to_csv(output_path, index=False)
    
    # 6. Report on Key Cases
    logger.info("\nKey Case Analysis:")
    cases = ["Brunson", "Poole", "Wiseman", "Jokic", "Maxey", "Haliburton"]
    
    for case in cases:
        matches = df_final[df_final['PLAYER_NAME'].str.contains(case, case=False, na=False)]
        if not matches.empty:
            logger.info(f"\n--- {case} ---")
            for _, row in matches.iterrows():
                logger.info(f"{row['PLAYER_NAME']} ({row['SEASON']}): "
                            f"Viability={row['CRUCIBLE_SCORE']:.2f}, "
                            f"Potential={row['TELESCOPE_SCORE']:.2f} "
                            f"-> {row['RISK_CATEGORY']}")

if __name__ == "__main__":
    main()

