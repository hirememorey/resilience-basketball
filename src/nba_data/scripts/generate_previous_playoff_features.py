"""
Generate Previous Playoff Performance Features.

This script calculates previous season playoff stats as features for predicting
future playoff performance. This is legitimate (past → future) and not data leakage.

Key Features Generated:
1. Previous Playoff Stats: Previous season's playoff performance metrics
2. Playoff Experience Flag: Binary flag indicating if player has playoff experience
3. Previous Playoff Archetype: Previous season's playoff archetype (if available)

Implementation based on trajectory features pattern but for playoff stats.
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path
from typing import List, Optional

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/previous_playoff_features.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Playoff features to calculate previous season values for
PREVIOUS_PLAYOFF_FEATURES = [
    'PO_RIM_APPETITE',  # From rim_pressure_features.csv
    'PO_PRESSURE_RESILIENCE',  # From pressure_features.csv
    'PO_PRESSURE_APPETITE',  # From pressure_features.csv
    'PO_FTr',  # From physicality_features.csv
    'PO_LATE_CLOCK_PRESSURE_RESILIENCE',  # From pressure_features.csv (if available)
    'PO_EARLY_CLOCK_PRESSURE_RESILIENCE',  # From pressure_features.csv (if available)
]


class PreviousPlayoffFeatureGenerator:
    """Generate previous playoff performance features."""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_season(self, season: str) -> Optional[int]:
        """Parse season string (e.g., '2015-16') to year (2015)."""
        if pd.isna(season):
            return None
        try:
            year_str = str(season).split('-')[0]
            return int(year_str)
        except (ValueError, AttributeError):
            return None
    
    def load_playoff_features(self) -> pd.DataFrame:
        """Load all playoff features from various sources."""
        logger.info("Loading playoff features from various sources...")
        
        all_features = []
        
        # 1. Rim Pressure Features (contains PO_RIM_APPETITE)
        rim_path = self.results_dir / "rim_pressure_features.csv"
        if rim_path.exists():
            df_rim = pd.read_csv(rim_path)
            logger.info(f"Loaded rim pressure features: {len(df_rim)} rows")
            # Keep only PO features and identifiers
            rim_cols = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'PO_RIM_APPETITE']
            rim_cols = [c for c in rim_cols if c in df_rim.columns]
            if rim_cols:
                all_features.append(df_rim[rim_cols])
        
        # 2. Pressure Features (contains PO_PRESSURE_RESILIENCE, PO_PRESSURE_APPETITE)
        pressure_path = self.results_dir / "pressure_features.csv"
        if pressure_path.exists():
            df_pressure = pd.read_csv(pressure_path)
            logger.info(f"Loaded pressure features: {len(df_pressure)} rows")
            # Keep only PO features and identifiers
            pressure_cols = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 
                            'PO_PRESSURE_RESILIENCE', 'PO_PRESSURE_APPETITE']
            pressure_cols = [c for c in pressure_cols if c in df_pressure.columns]
            if pressure_cols:
                all_features.append(df_pressure[pressure_cols])
        
        # 3. Physicality Features (contains PO_FTr)
        physicality_path = self.results_dir / "physicality_features.csv"
        if physicality_path.exists():
            df_phys = pd.read_csv(physicality_path)
            logger.info(f"Loaded physicality features: {len(df_phys)} rows")
            # Keep only PO features and identifiers
            phys_cols = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'PO_FTr']
            phys_cols = [c for c in phys_cols if c in df_phys.columns]
            if phys_cols:
                all_features.append(df_phys[phys_cols])
        
        # 4. Clock Features (if available in pressure_features)
        # These might be in pressure_features.csv already
        
        # Merge all features
        if not all_features:
            logger.warning("No playoff features found!")
            return pd.DataFrame()
        
        # Start with first dataframe
        df_merged = all_features[0].copy()
        
        # Merge others
        for df in all_features[1:]:
            df_merged = pd.merge(
                df_merged,
                df,
                on=['PLAYER_ID', 'PLAYER_NAME', 'SEASON'],
                how='outer',
                suffixes=('', '_dup')
            )
            # Drop duplicate columns
            dup_cols = [c for c in df_merged.columns if c.endswith('_dup')]
            df_merged = df_merged.drop(columns=dup_cols)
        
        logger.info(f"Merged playoff features: {len(df_merged)} rows")
        return df_merged
    
    def load_archetypes(self) -> pd.DataFrame:
        """Load playoff archetypes for previous season archetype feature."""
        archetype_path = self.results_dir / "resilience_archetypes.csv"
        if not archetype_path.exists():
            logger.warning("Archetypes file not found")
            return pd.DataFrame()
        
        df_arch = pd.read_csv(archetype_path)
        logger.info(f"Loaded archetypes: {len(df_arch)} rows")
        
        # Keep only what we need
        return df_arch[['PLAYER_NAME', 'SEASON', 'archetype']].copy()
    
    def calculate_previous_playoff_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate previous season playoff features for all player-seasons.
        
        Args:
            df: DataFrame with playoff features (PO_* columns)
            
        Returns:
            DataFrame with previous playoff features added
        """
        logger.info("Calculating previous playoff features...")
        
        # Sort by player and season (chronological)
        df = df.sort_values(['PLAYER_ID', 'SEASON']).copy()
        
        # Initialize result dictionaries
        prev_features = {}
        playoff_experience = {}
        
        players_processed = 0
        players_with_prev_po = 0
        
        for player_id in df['PLAYER_ID'].unique():
            player_df = df[df['PLAYER_ID'] == player_id].copy()
            player_df = player_df.sort_values('SEASON')
            
            players_processed += 1
            
            # Track playoff experience
            has_playoff_exp = False
            
            # Calculate previous playoff features for each season (starting from second season)
            for idx in range(len(player_df)):
                current_season = player_df.iloc[idx]
                season_key = (player_id, current_season['SEASON'])
                
                # Initialize for this season
                if season_key not in prev_features:
                    prev_features[season_key] = {}
                    playoff_experience[season_key] = False
                
                # Look for previous season with playoff data
                prev_po_data = None
                for prev_idx in range(idx - 1, -1, -1):
                    prev_season = player_df.iloc[prev_idx]
                    # Check if previous season has any playoff data
                    po_cols = [c for c in prev_season.index if c.startswith('PO_')]
                    if po_cols and any(pd.notna(prev_season.get(c)) for c in po_cols):
                        prev_po_data = prev_season
                        has_playoff_exp = True
                        players_with_prev_po += 1
                        break
                
                if prev_po_data is not None:
                    # Copy previous playoff features
                    for feature in PREVIOUS_PLAYOFF_FEATURES:
                        if feature in prev_po_data.index:
                            prev_val = prev_po_data[feature]
                            if pd.notna(prev_val):
                                prev_features[season_key][f'PREV_{feature}'] = prev_val
                                playoff_experience[season_key] = True
                
                # Set playoff experience flag
                playoff_experience[season_key] = has_playoff_exp
        
        logger.info(f"Processed {players_processed} players")
        logger.info(f"Found previous playoff data for {players_with_prev_po} player-seasons")
        
        # Convert to DataFrame
        prev_df_list = []
        for (player_id, season), features in prev_features.items():
            # Get player name from original df
            player_rows = df[(df['PLAYER_ID'] == player_id) & (df['SEASON'] == season)]
            player_name = player_rows['PLAYER_NAME'].iloc[0] if not player_rows.empty else None
            
            prev_df_list.append({
                'PLAYER_ID': player_id,
                'PLAYER_NAME': player_name,
                'SEASON': season,
                **features,
                'HAS_PLAYOFF_EXPERIENCE': playoff_experience.get((player_id, season), False)
            })
        
        prev_df = pd.DataFrame(prev_df_list)
        
        return prev_df
    
    def add_previous_archetype(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add previous season's playoff archetype as a feature."""
        logger.info("Adding previous playoff archetype...")
        
        df_arch = self.load_archetypes()
        if df_arch.empty:
            return df
        
        # Create archetype encoding (for model compatibility)
        archetype_map = {
            'King (Resilient Star)': 3,
            'Bulldozer (Fragile Star)': 2,
            'Sniper (Resilient Role)': 1,
            'Victim (Fragile Role)': 0
        }
        
        df_arch['ARCHETYPE_ENCODED'] = df_arch['archetype'].map(archetype_map).fillna(-1)
        
        # For each player-season, find previous season archetype
        prev_archetypes = {}
        
        for player_id in df['PLAYER_ID'].unique():
            player_df = df[df['PLAYER_ID'] == player_id].sort_values('SEASON')
            if player_df.empty or 'PLAYER_NAME' not in player_df.columns:
                continue
            player_names = player_df['PLAYER_NAME'].unique()
            player_arch = df_arch[df_arch['PLAYER_NAME'].isin(player_names)].sort_values('SEASON')
            
            for idx, row in player_df.iterrows():
                current_season = row['SEASON']
                season_key = (player_id, current_season)
                
                # Find previous season archetype
                prev_arch = None
                for prev_idx in range(len(player_df) - 1, -1, -1):
                    if player_df.iloc[prev_idx]['SEASON'] < current_season:
                        prev_season = player_df.iloc[prev_idx]['SEASON']
                        prev_arch_row = player_arch[player_arch['SEASON'] == prev_season]
                        if not prev_arch_row.empty:
                            prev_arch = prev_arch_row.iloc[0]['ARCHETYPE_ENCODED']
                            break
                
                if prev_arch is not None:
                    prev_archetypes[season_key] = prev_arch
        
        # Add to dataframe
        df['PREV_PO_ARCHETYPE'] = df.apply(
            lambda row: prev_archetypes.get((row['PLAYER_ID'], row['SEASON']), -1),
            axis=1
        )
        
        logger.info(f"Added previous archetype for {len([v for v in prev_archetypes.values() if v >= 0])} player-seasons")
        
        return df
    
    def generate(self) -> pd.DataFrame:
        """Generate all previous playoff features."""
        logger.info("=" * 80)
        logger.info("Generating Previous Playoff Features")
        logger.info("=" * 80)
        
        # Load playoff features
        df_po = self.load_playoff_features()
        if df_po.empty:
            logger.error("No playoff features found. Cannot generate previous playoff features.")
            return pd.DataFrame()
        
        # Calculate previous playoff features
        df_prev = self.calculate_previous_playoff_features(df_po)
        
        # Add previous archetype
        df_prev = self.add_previous_archetype(df_prev)
        
        # Save results
        output_path = self.results_dir / "previous_playoff_features.csv"
        df_prev.to_csv(output_path, index=False)
        logger.info(f"Saved previous playoff features to {output_path}")
        logger.info(f"Total rows: {len(df_prev)}")
        logger.info(f"Features generated: {len([c for c in df_prev.columns if c.startswith('PREV_PO_') or c == 'HAS_PLAYOFF_EXPERIENCE'])}")
        
        return df_prev


def main():
    generator = PreviousPlayoffFeatureGenerator()
    generator.generate()
    logger.info("✅ Previous playoff features generation complete!")


if __name__ == "__main__":
    main()

