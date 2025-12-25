import pandas as pd
import numpy as np
import joblib
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[3]))

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GhostRiskDetector:
    def __init__(self):
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.models_dir = Path("models")
        
        # Features used by the Crucible model
        self.features = [
            'CREATION_TAX', 
            'CREATION_VOLUME_RATIO', 
            'LEVERAGE_TS_DELTA', 
            'LEVERAGE_USG_DELTA',
            'DEPENDENCE_SCORE', 
            'SHOT_QUALITY_GENERATION_DELTA',
            'EFG_PCT_0_DRIBBLE', 
            'EFG_ISO_WEIGHTED',
            'USG_PCT',
            'AGE'
        ]
        
        # Load the Crucible model
        model_path = self.models_dir / "crucible_impact_model.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"Missing model: {model_path}")
        self.model = joblib.load(model_path)

    def detect(self, input_path="results/predictive_dataset.csv"):
        """
        Applies the Crucible model to all players to predict 'Physics-Adjusted Playoff Impact'.
        """
        if not Path(input_path).exists():
            logger.error(f"Missing {input_path}")
            return
            
        df = pd.read_csv(input_path)
        logger.info(f"Loaded {len(df)} players from {input_path}.")
        
        # 1. Prepare Features
        # Ensure all features exist
        for f in self.features:
            if f not in df.columns:
                df[f] = 0.0
                
        X = df[self.features].fillna(0)
        
        # 2. Predict Playoff Impact
        df['PREDICTED_PLAYOFF_IMPACT'] = self.model.predict(X)
        
        # 3. Join with actual Playoff outcomes (if available) to identify historical ghosts
        crucible_path = self.data_dir / "crucible_dataset.csv"
        if crucible_path.exists():
            crucible_df = pd.read_csv(crucible_path)
            # We want to identify historical ghosts to validate
            ghost_check = pd.merge(
                df,
                crucible_df[['PLAYER_ID', 'SEASON', 'PIE_TARGET']],
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )
            ghost_check['GHOST_GAP'] = ghost_check['PREDICTED_PLAYOFF_IMPACT'] - ghost_check['PIE_TARGET']
            df = ghost_check
        
        # 4. Define Ghost Risk
        # A player is a "Ghost Risk" if they have high RS stats (USG_PCT, etc.) 
        # but the physics-adjusted predicted impact is significantly lower than their RS production would suggest.
        # Let's normalize PIE to a 0-1 scale similar to RS stats if possible, or just use raw PIE.
        # Average PIE for a "Star" is around 0.15+.
        
        # For now, let's just save the predictions.
        output_path = self.results_dir / "physics_adjusted_impact.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"✅ Saved Physics-Adjusted Impact to {output_path}")
        
        # Preview top "Physics Stars" vs "RS Stars"
        logger.info("Top Physics-Adjusted Stars (2023-24):")
        top_physics = df[df['SEASON'] == '2023-24'].sort_values('PREDICTED_PLAYOFF_IMPACT', ascending=False).head(10)
        logger.info(top_physics[['PLAYER_NAME', 'PREDICTED_PLAYOFF_IMPACT', 'USG_PCT']])
        
        return df

if __name__ == "__main__":
    detector = GhostRiskDetector()
    detector.detect()

