"""
Train the Resilience Model (Model B - The Glass Detector).

First Principles:
- Resilience = Efficiency Retention under Stress.
- Target: Playoff TS% / Regular Season TS% (The "Translation Ratio").
- Features: Mechanics, Aggression, Force, Experience. (NO RAW VOLUME).

Architecture:
1. Filter Training Set to players with meaningful Playoff sample (>100 mins).
2. Train Regressor (Gradient Boosting) to predict Translation Ratio.
3. Apply to all players to get "Predicted Resilience".
"""

import pandas as pd
import numpy as np
import joblib
import logging
import sys
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class ResilienceTrainer:
    def __init__(self):
        self.data_dir = Path("results")
        self.models_dir = Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Features that define "Toughness" (Orthogonal to Capacity)
        self.features = [
            'ts_pct',                  # Base Efficiency
            'scoring_aggression',      # Do you attack?
            'rim_pressure_rate',       # Do you get to the rim?
            'physicality_score',       # FTr + Rim Appetite
            'shot_quality_generation_delta', # IQ
            'avg_opponent_dcs',        # Did you face tough defenses?
            'leverage_ts_delta',       # Clutch performance (proxy for stress)
            'fragility_score'          # The rule-based prior (Abdication Tax)
        ]

    def load_data(self):
        # 1. Load Features
        feature_path = self.data_dir / "predictive_dataset_with_friction.csv"
        df_feat = pd.read_csv(feature_path)
        
        # 2. Load Targets (Playoff Data)
        # We need actual Playoff TS% to calculate the target.
        # We'll use resilience_archetypes.csv which has PO stats
        target_path = self.data_dir / "resilience_archetypes.csv"
        if not target_path.exists():
            raise FileNotFoundError("Resilience archetypes not found. Cannot train.")
            
        df_target = pd.read_csv(target_path)
        # Normalize column names
        df_target.columns = [c.lower() for c in df_target.columns]
        
        # Rename specific columns if needed
        if 'po_ts_pct_calc' in df_target.columns:
            df_target = df_target.rename(columns={'po_ts_pct_calc': 'po_ts_pct'})
            
        # Merge on NAME and SEASON because ID is missing in target
        # Ensure name match is robust (lowercase strip)
        df_feat['merge_name'] = df_feat['player_name'].str.lower().str.strip()
        df_feat['merge_season'] = df_feat['season'].astype(str)
        
        df_target['merge_name'] = df_target['player_name'].str.lower().str.strip()
        df_target['merge_season'] = df_target['season'].astype(str)
        
        # Merge
        df = pd.merge(df_feat, df_target[['merge_name', 'merge_season', 'po_ts_pct', 'po_minutes_total']], 
                     on=['merge_name', 'merge_season'], how='left')
                     
        # Drop temp columns
        df = df.drop(columns=['merge_name', 'merge_season'])
        
        # Calculate Target: Translation Ratio
        # Avoid division by zero
        df['base_ts'] = df['ts_pct'].replace(0, np.nan)
        df['translation_ratio'] = df['po_ts_pct'] / df['base_ts']
        
        # Clip outliers (some players have 1.5x translation due to small sample)
        df['translation_ratio'] = df['translation_ratio'].clip(0.5, 1.3)
        
        return df

    def train(self):
        df = self.load_data()
        
        # 1. Filter Training Set (The Crucible)
        # Only train on players who actually faced the fire.
        
        # FEATURE ENGINEERING: Jump Shot Rate
        # Proxy for spacing/gravity.
        # If Scoring Aggression (Total) ~= Rim Pressure (Rim), then Jump Shot Rate ~= 0.
        # Simmons: 2.5 (Agg) - 2.0 (Rim) = 0.5 (Low Jumps)
        # Brunson: 3.0 (Agg) - 1.0 (Rim) = 2.0 (High Jumps)
        df['jump_shot_rate'] = (df['scoring_aggression'] - df['rim_pressure_rate']).clip(lower=0)
        
        # Add to features
        self.features.append('jump_shot_rate')
        
        mask_train = (df['po_minutes_total'] > 100) & (df['translation_ratio'].notna())
        train_df = df[mask_train].copy()
        
        logger.info(f"Training Resilience Model on {len(train_df)} playoff veterans.")
        
        # Handle Missing Features in Training Set
        X = train_df[self.features].fillna(0)
        y = train_df['translation_ratio']
        
        # 2. Train Model
        # Monotonic Constraints: 
        # fragility_score should negatively impact resilience (-1)
        # leverage_ts_delta should positively impact resilience (+1)
        
        # Map feature names to indices for monotonic constraints if using XGBoost, 
        # but sklearn GBR supports it too.
        # Let's keep it simple first.
        
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=3,
            random_state=42
        )
        
        model.fit(X, y)
        
        # 3. Predict on EVERYONE
        # Even rookies who never made playoffs
        X_all = df[self.features].fillna(0)
        df['PREDICTED_TRANSLATION'] = model.predict(X_all)
        
        # 4. Save
        joblib.dump(model, self.models_dir / "resilience_model_b.pkl")
        df.to_csv(self.data_dir / "predictive_dataset_with_resilience.csv", index=False)
        
        # 5. Validation Logic
        self.validate(model, X, y)
        self.probe_simmons(df)
        
        return df

    def validate(self, model, X, y):
        score = model.score(X, y)
        logger.info(f"Model R2 on Training Data: {score:.3f}")
        
        # Feature Importance
        imp = pd.Series(model.feature_importances_, index=self.features).sort_values(ascending=False)
        logger.info("Feature Importance:")
        logger.info(imp)

    def probe_simmons(self, df):
        logger.info("="*60)
        logger.info("RESILIENCE PROBES")
        logger.info("="*60)
        
        probes = [
            ('Ben Simmons', '2017-18'),
            ('Ben Simmons', '2020-21'), # The Collapse
            ('Jalen Brunson', '2020-21'),
            ('Giannis Antetokounmpo', '2020-21'),
            ('Jordan Poole', '2021-22')
        ]
        
        for name, season in probes:
            row = df[(df['player_name'] == name) & (df['season'] == season)]
            if not row.empty:
                trans = row.iloc[0]['PREDICTED_TRANSLATION']
                logger.info(f"{name} ({season}): Predicted Translation {trans:.3f}")
                logger.info(f"   - Fragility: {row.iloc[0].get('fragility_score', 'N/A')}")
                logger.info(f"   - Aggression: {row.iloc[0].get('scoring_aggression', 'N/A')}")
            else:
                logger.warning(f"Probe not found: {name} {season}")

if __name__ == "__main__":
    trainer = ResilienceTrainer()
    trainer.train()

