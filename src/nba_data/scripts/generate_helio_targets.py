"""
generate_helio_targets.py

Phase 4: Telescope Model Target Generation
- Implements the "Future-Peak" Helio Target logic.
- Creates the ground truth label for predicting heliocentric scalability.
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/generate_helio_targets.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HelioTargetGenerator:
    def __init__(self, data_dir='data', results_dir='results'):
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.seasons = self._get_available_seasons()

    def _get_available_seasons(self):
        """Finds available seasons from playoff log files."""
        files = self.data_dir.glob("playoff_logs_*.csv")
        seasons = sorted([f.stem.split('_')[-1] for f in files])
        logger.info(f"Found seasons: {seasons}")
        return seasons

    def load_data(self):
        """Loads all regular season and playoff data."""
        rs_dfs = []
        po_dfs = []
        for season in self.seasons:
            year = int(season.split('-')[0]) + 1
            
            rs_file = self.data_dir / f"regular_season_{season}.csv"
            po_file = self.data_dir / f"playoff_logs_{season}.csv"
            
            if rs_file.exists():
                df = pd.read_csv(rs_file)
                df['SEASON_YEAR'] = year
                rs_dfs.append(df)
            if po_file.exists():
                df = pd.read_csv(po_file)
                df['SEASON_YEAR'] = year
                po_dfs.append(df)
                
        df_rs = pd.concat(rs_dfs, ignore_index=True)
        df_po = pd.concat(po_dfs, ignore_index=True)
        
        logger.info(f"Loaded {len(df_rs)} total regular season rows.")
        logger.info(f"Loaded {len(df_po)} total playoff rows.")
        return df_rs, df_po

    def calculate_helio_load_index(self, df_po: pd.DataFrame, df_rs: pd.DataFrame) -> pd.DataFrame:
        """Calculates HELIO_LOAD_INDEX for playoff data."""
        logger.info("Calculating HELIO_LOAD_INDEX for all playoff runs...")

        # Aggregate playoff data to season level
        df_po_agg = df_po.groupby(['PLAYER_ID', 'SEASON_YEAR']).agg({
            'MIN': 'sum',
            'USG_PCT': 'mean',
            'AST_PCT': 'mean',
            'OFF_RATING': 'mean',
        }).reset_index()
        
        # Get games played from regular season data
        df_rs_gp = df_rs[['PLAYER_ID', 'SEASON_YEAR', 'GP']]
        df_po_agg = pd.merge(df_po_agg, df_rs_gp, on=['PLAYER_ID', 'SEASON_YEAR'], how='left')

        # De-Risking Filter: Ensure sufficient sample size
        df_filtered = df_po_agg[df_po_agg['MIN'] > 100].copy()
        
        # 1. Calculate League Average Offensive Rating for each season
        league_avg_off_rating = df_filtered.groupby('SEASON_YEAR')['OFF_RATING'].mean().rename('LEAGUE_AVG_OFF_RATING')
        df_filtered = pd.merge(df_filtered, league_avg_off_rating, on='SEASON_YEAR', how='left')
        
        # 2. Calculate Offensive Load
        df_filtered['OFFENSIVE_LOAD'] = df_filtered['USG_PCT'] + (df_filtered['AST_PCT'] * 0.75)
        
        # 3. Calculate Efficiency Delta (with Replacement Level Adjustment)
        replacement_level_offset = 5.0
        df_filtered['EFFICIENCY_DELTA'] = df_filtered['OFF_RATING'] - (df_filtered['LEAGUE_AVG_OFF_RATING'] - replacement_level_offset)
        
        # 4. Calculate Final Index
        df_filtered['HELIO_LOAD_INDEX'] = (df_filtered['OFFENSIVE_LOAD'] ** 1.3) * df_filtered['EFFICIENCY_DELTA']
        
        logger.info("HELIO_LOAD_INDEX calculation complete.")
        # Need player name for logging
        df_final = pd.merge(df_filtered, df_rs[['PLAYER_ID', 'SEASON_YEAR', 'PLAYER_NAME']].drop_duplicates(), on=['PLAYER_ID', 'SEASON_YEAR'])
        logger.info(f"Top 5 performers:\n{df_final.sort_values('HELIO_LOAD_INDEX', ascending=False).head(5)[['PLAYER_NAME', 'SEASON_YEAR', 'HELIO_LOAD_INDEX']]}")
        
        return df_final[['PLAYER_ID', 'SEASON_YEAR', 'HELIO_LOAD_INDEX', 'GP', 'MIN']]

    def generate_future_peak_target(self, df_rs: pd.DataFrame, df_helio: pd.DataFrame) -> pd.DataFrame:
        """Applies the 3-year lookahead window to generate the training target."""
        logger.info("Generating 'Future Peak' target with 3-year lookahead...")
        
        df_rs['FUTURE_PEAK_HELIO'] = np.nan
        
        # Sort for easier processing
        df_helio_sorted = df_helio.sort_values(by=['PLAYER_ID', 'SEASON_YEAR'])
        
        # Group by player to perform lookahead calculations
        player_groups = df_helio_sorted.groupby('PLAYER_ID')
        
        all_targets = []

        for player_id, group in player_groups:
            player_targets = []
            seasons = group['SEASON_YEAR'].values
            helio_scores = group['HELIO_LOAD_INDEX'].values
            minutes = group['MIN'].values

            for i, season in enumerate(seasons):
                # Window: Years N+1, N+2, N+3
                window_mask = (seasons > season) & (seasons <= season + 3)
                
                if np.any(window_mask):
                    future_scores = helio_scores[window_mask]
                    future_minutes = minutes[window_mask]
                    
                    # The Washout Signal (revealed capacity is zero if they played but failed to stick)
                    if np.sum(future_minutes) < 100:
                        peak_helio = 0.0
                    else:
                        peak_helio = np.max(future_scores)
                else:
                    # No data in window: This is NOT a zero, it is UNKNOWN (Censored data)
                    peak_helio = np.nan
                
                player_targets.append({'PLAYER_ID': player_id, 'SEASON_YEAR': season, 'FUTURE_PEAK_HELIO': peak_helio})

            if player_targets:
                all_targets.extend(player_targets)
        
        if not all_targets:
             logger.warning("No targets were generated. Check data.")
             return df_rs

        df_targets = pd.DataFrame(all_targets)
        
        # Merge targets back into the regular season dataframe
        # We merge on previous season to align target correctly
        df_targets['TARGET_SEASON_YEAR'] = df_targets['SEASON_YEAR'] -1
        
        df_rs = pd.merge(
            df_rs,
            df_targets[['PLAYER_ID', 'TARGET_SEASON_YEAR', 'FUTURE_PEAK_HELIO']],
            left_on=['PLAYER_ID', 'SEASON_YEAR'],
            right_on=['PLAYER_ID', 'TARGET_SEASON_YEAR'],
            how='left'
        )
        
        # The merge creates FUTURE_PEAK_HELIO_y if FUTURE_PEAK_HELIO already exists.
        # We need to coalesce these columns.
        if 'FUTURE_PEAK_HELIO_y' in df_rs.columns:
            df_rs['FUTURE_PEAK_HELIO'] = df_rs['FUTURE_PEAK_HELIO_y'].combine_first(df_rs['FUTURE_PEAK_HELIO_x'])
            df_rs = df_rs.drop(columns=['FUTURE_PEAK_HELIO_x', 'FUTURE_PEAK_HELIO_y'])

        # Drop rows where target is NaN (the Booker/Fox/SGA Trap fix)
        # We only train on "Revealed Outcomes"
        initial_len = len(df_rs)
        df_rs = df_rs.dropna(subset=['FUTURE_PEAK_HELIO'])
        logger.info(f"Dropped {initial_len - len(df_rs)} rows with no playoff outcome (Censored Data).")

        if 'TARGET_SEASON_YEAR' in df_rs.columns:
            df_rs = df_rs.drop(columns=['TARGET_SEASON_YEAR'])

        logger.info("'Future Peak' target generation complete.")
        return df_rs

    def run(self):
        """Execute the full target generation pipeline."""
        logger.info("Starting HELIO target generation pipeline...")
        
        df_rs, df_po = self.load_data()
        df_helio = self.calculate_helio_load_index(df_po, df_rs)
        df_final = self.generate_future_peak_target(df_rs, df_helio)
        
        output_path = self.results_dir / "training_targets_helio.csv"
        df_final.to_csv(output_path, index=False)
        
        logger.info(f"Successfully saved Helio targets to {output_path}")
        logger.info(f"Final dataset shape: {df_final.shape}")
        logger.info(f"Non-zero targets: {(df_final['FUTURE_PEAK_HELIO'] > 0).sum()}")

if __name__ == "__main__":
    generator = HelioTargetGenerator()
    generator.run()


