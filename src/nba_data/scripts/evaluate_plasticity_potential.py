"""
Feature Engineering Script for "Stylistic Stress Test" (V2 Resilience Model).

This script calculates the three "Stress Vectors" for every player-season:
1. Creation Tax (Self-Reliance)
2. Leverage Delta (Clutch Performance)
3. Quality of Competition (Schematic Resilience)

It outputs a CSV ready for the predictive model.
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path
import time

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[3]))

from src.nba_data.api.nba_stats_client import create_nba_stats_client
from src.nba_data.constants import ID_TO_ABBREV, get_team_abbrev

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/stress_vectors.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class StressVectorEngine:
    def __init__(self):
        self.client = create_nba_stats_client()
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_creation_metrics(self, season):
        """
        Vector 1: Self-Creation (The 'Creation Tax')
        Fetches shooting stats by Dribble Range.
        """
        logger.info(f"Fetching Creation Metrics for {season}...")
        
        try:
            # 1. Zero Dribbles (Dependent)
            logger.info(f"  - Fetching 0 Dribbles for {season}...")
            zero_dribbles = self.client.get_league_player_shooting_stats(
                season=season, 
                dribble_range="0 Dribbles"
            )
            df_zero = pd.DataFrame(zero_dribbles['resultSets'][0]['rowSet'], 
                                   columns=zero_dribbles['resultSets'][0]['headers'])
            df_zero = df_zero[['PLAYER_ID', 'PLAYER_NAME', 'FG_PCT', 'FG3_PCT', 'EFG_PCT', 'FGA']]
            df_zero = df_zero.rename(columns={
                'FG_PCT': 'FG_PCT_0_DRIBBLE', 
                'EFG_PCT': 'EFG_PCT_0_DRIBBLE',
                'FGA': 'FGA_0_DRIBBLE'
            })
            logger.info(f"    -> Got {len(df_zero)} rows.")
            
            # 2. 3-6 Dribbles (Self-Created/Iso)
            logger.info(f"  - Fetching 3-6 Dribbles for {season}...")
            iso_dribbles = self.client.get_league_player_shooting_stats(
                season=season, 
                dribble_range="3-6 Dribbles"
            )
            df_iso = pd.DataFrame(iso_dribbles['resultSets'][0]['rowSet'], 
                                  columns=iso_dribbles['resultSets'][0]['headers'])
            df_iso = df_iso[['PLAYER_ID', 'EFG_PCT', 'FGA']]
            df_iso = df_iso.rename(columns={
                'EFG_PCT': 'EFG_PCT_3_DRIBBLE',
                'FGA': 'FGA_3_DRIBBLE'
            })
            logger.info(f"    -> Got {len(df_iso)} rows.")
            
            # 3. 7+ Dribbles (Deep Iso)
            logger.info(f"  - Fetching 7+ Dribbles for {season}...")
            deep_iso = self.client.get_league_player_shooting_stats(
                season=season, 
                dribble_range="7+ Dribbles"
            )
            df_deep = pd.DataFrame(deep_iso['resultSets'][0]['rowSet'], 
                                   columns=deep_iso['resultSets'][0]['headers'])
            df_deep = df_deep[['PLAYER_ID', 'EFG_PCT', 'FGA']]
            df_deep = df_deep.rename(columns={
                'EFG_PCT': 'EFG_PCT_7_DRIBBLE',
                'FGA': 'FGA_7_DRIBBLE'
            })
            logger.info(f"    -> Got {len(df_deep)} rows.")
            
            # Merge
            logger.info("  - Merging creation datasets...")
            df_creation = pd.merge(df_zero, df_iso, on='PLAYER_ID', how='left')
            df_creation = pd.merge(df_creation, df_deep, on='PLAYER_ID', how='left')
            
            # Fill NaNs with 0 (some players never take 7+ dribbles)
            df_creation = df_creation.fillna(0)
            
            # Feature Engineering: Creation Tax
            # How much efficiency do you lose when you have to dribble?
            
            # Weighted average of 3+ dribbles
            df_creation['FGA_ISO_TOTAL'] = df_creation['FGA_3_DRIBBLE'] + df_creation['FGA_7_DRIBBLE']
            
            # Avoid division by zero
            df_creation['EFG_ISO_WEIGHTED'] = np.where(
                df_creation['FGA_ISO_TOTAL'] > 0,
                ((df_creation['EFG_PCT_3_DRIBBLE'] * df_creation['FGA_3_DRIBBLE']) + 
                 (df_creation['EFG_PCT_7_DRIBBLE'] * df_creation['FGA_7_DRIBBLE'])) / df_creation['FGA_ISO_TOTAL'],
                0
            )
            
            df_creation['CREATION_TAX'] = df_creation['EFG_ISO_WEIGHTED'] - df_creation['EFG_PCT_0_DRIBBLE']
            
            # Feature: Creation Volume Ratio
            df_creation['TOTAL_FGA_TRACKED'] = df_creation['FGA_0_DRIBBLE'] + df_creation['FGA_ISO_TOTAL']
            
            df_creation['CREATION_VOLUME_RATIO'] = np.where(
                df_creation['TOTAL_FGA_TRACKED'] > 0,
                df_creation['FGA_ISO_TOTAL'] / df_creation['TOTAL_FGA_TRACKED'],
                0
            )
            
            logger.info(f"✅ Processed Creation Metrics for {len(df_creation)} players.")
            return df_creation
            
        except Exception as e:
            logger.error(f"❌ Error in Creation Metrics: {e}", exc_info=True)
            return pd.DataFrame()

    def fetch_leverage_metrics(self, season):
        """
        Vector 2: Leverage (The 'Clutch Delta')
        Fetches Clutch stats vs Base stats.
        """
        logger.info(f"Fetching Leverage Metrics for {season}...")
        
        try:
            # Base Stats (Full Season)
            logger.info(f"  - Fetching Base Advanced Stats for {season}...")
            base_adv = self.client.get_league_player_advanced_stats(season=season)
            df_base = pd.DataFrame(base_adv['resultSets'][0]['rowSet'], 
                                   columns=base_adv['resultSets'][0]['headers'])
            df_base = df_base[['PLAYER_ID', 'TS_PCT', 'USG_PCT']]
            df_base = df_base.rename(columns={'TS_PCT': 'BASE_TS', 'USG_PCT': 'BASE_USG'})
            
            # Clutch Stats
            logger.info(f"  - Fetching Clutch Stats for {season}...")
            clutch_adv = self.client.get_league_player_clutch_stats(season=season, measure_type="Advanced")
            df_clutch = pd.DataFrame(clutch_adv['resultSets'][0]['rowSet'], 
                                     columns=clutch_adv['resultSets'][0]['headers'])
            
            logger.info(f"    -> Raw Clutch Data: {len(df_clutch)} rows.")
            if not df_clutch.empty:
                logger.info(f"    -> Sample Clutch Row: {df_clutch.iloc[0].to_dict()}")
            
            df_clutch = df_clutch[['PLAYER_ID', 'TS_PCT', 'USG_PCT', 'MIN', 'GP']]
            df_clutch = df_clutch.rename(columns={'TS_PCT': 'CLUTCH_TS', 'USG_PCT': 'CLUTCH_USG', 'MIN': 'CLUTCH_MPG', 'GP': 'CLUTCH_GP'})
            
            # Calculate Total Clutch Minutes (API returns Per Game)
            df_clutch['CLUTCH_MIN_TOTAL'] = df_clutch['CLUTCH_MPG'] * df_clutch['CLUTCH_GP']
            
            # Merge
            df_leverage = pd.merge(df_base, df_clutch, on='PLAYER_ID', how='inner') # Inner join - must have clutch minutes
            
            logger.info(f"    -> Rows after Merge: {len(df_leverage)}")
            
            # Filter Noise: Must have at least 10 Total Clutch Minutes (~2-3 close games)
            df_leverage = df_leverage[df_leverage['CLUTCH_MIN_TOTAL'] >= 15] 
            
            logger.info(f"    -> Rows after Filter (Total Min >= 15): {len(df_leverage)}")
            
            # Feature Engineering
            df_leverage['LEVERAGE_TS_DELTA'] = df_leverage['CLUTCH_TS'] - df_leverage['BASE_TS']
            df_leverage['LEVERAGE_USG_DELTA'] = df_leverage['CLUTCH_USG'] - df_leverage['BASE_USG']
            
            logger.info(f"✅ Processed Leverage Metrics for {len(df_leverage)} players.")
            return df_leverage
            
        except Exception as e:
            logger.error(f"❌ Error in Leverage Metrics: {e}", exc_info=True)
            return pd.DataFrame()

    def calculate_context_metrics(self, season):
        """
        Vector 3: Context (Quality of Competition)
        """
        # Placeholder for now until we confirm RS logs strategy
        return pd.DataFrame()

    def run(self, seasons=['2021-22', '2022-23', '2023-24']):
        
        all_seasons_data = []
        
        for season in seasons:
            logger.info(f"=== Processing {season} ===")
            
            try:
                # 1. Creation
                df_creation = self.fetch_creation_metrics(season)
                if df_creation.empty:
                    logger.warning(f"Skipping {season} due to missing creation data.")
                    continue
                
                # 2. Leverage
                df_leverage = self.fetch_leverage_metrics(season)
                
                # Merge Vectors
                if not df_leverage.empty:
                    df_season = pd.merge(df_creation, df_leverage, on='PLAYER_ID', how='left')
                else:
                    logger.warning(f"No leverage data for {season}, filling with NaNs")
                    df_season = df_creation
                    df_season['LEVERAGE_TS_DELTA'] = np.nan
                    df_season['LEVERAGE_USG_DELTA'] = np.nan
                    df_season['CLUTCH_MIN_TOTAL'] = 0
                
                df_season['SEASON'] = season
                all_seasons_data.append(df_season)
                
                # Be nice to the API
                time.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Failed to process {season}: {e}", exc_info=True)
        
        # Combine all
        if not all_seasons_data:
            logger.error("No data generated.")
            return
            
        final_df = pd.concat(all_seasons_data, ignore_index=True)
        
        # Clean up columns
        cols_to_keep = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 
                        'CREATION_TAX', 'CREATION_VOLUME_RATIO',
                        'LEVERAGE_TS_DELTA', 'LEVERAGE_USG_DELTA', 'CLUTCH_MIN_TOTAL',
                        'EFG_PCT_0_DRIBBLE', 'EFG_ISO_WEIGHTED']
        
        # Only keep columns that actually exist
        existing_cols = [c for c in cols_to_keep if c in final_df.columns]
        final_df = final_df[existing_cols]
                             
        output_path = self.results_dir / "predictive_dataset.csv"
        final_df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved Predictive Dataset to {output_path}")
        logger.info(f"Total Rows: {len(final_df)}")

if __name__ == "__main__":
    engine = StressVectorEngine()
    # Expanding window to capture enough historical data for training
    engine.run(seasons=['2019-20', '2020-21', '2021-22', '2022-23', '2023-24'])
