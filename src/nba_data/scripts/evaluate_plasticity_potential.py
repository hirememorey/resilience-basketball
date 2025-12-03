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
from src.nba_data.constants import ID_TO_ABBREV, get_team_abbrev, ABBREV_TO_ID

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
            
            # CONSULTANT FIX: CREATION_BOOST - Superpower signal
            # If efficiency increases when self-creating (positive tax), this is a "physics violation"
            # indicating elite self-creation ability. Weight it 1.5x as a superpower indicator.
            df_creation['CREATION_BOOST'] = np.where(
                df_creation['CREATION_TAX'] > 0,
                df_creation['CREATION_TAX'] * 1.5,  # 1.5x weight for positive creation tax
                0  # No boost for negative or zero tax
            )
            
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

    def fetch_context_metrics(self, season):
        """
        Vector 3: Context (Quality of Competition)
        Calculates player performance against Top 10 vs Bottom 10 defenses.
        ENHANCED: Adds opponent defensive context score (DCS) features.
        """
        logger.info(f"Fetching Context Metrics for {season}...")
        try:
            # 1. Load Defensive Context
            def_context_path = self.data_dir / f"defensive_context_{season}.csv"
            if not def_context_path.exists():
                logger.warning(f"  - Defensive context file not found at {def_context_path}, skipping.")
                return pd.DataFrame()
            
            df_def = pd.read_csv(def_context_path)
            # Rank by DEF_RATING (lower is better)
            df_def['DEF_RANK'] = df_def['DEF_RATING'].rank(method='first', ascending=True)
            
            # Create DCS map for quick lookup
            dcs_map = dict(zip(df_def['TEAM_ID'], df_def['def_context_score']))
            
            top_10_defenses = df_def[df_def['DEF_RANK'] <= 10]['TEAM_ID'].tolist()
            bottom_10_defenses = df_def[df_def['DEF_RANK'] > 20]['TEAM_ID'].tolist()
            
            # Elite defenses (DCS > 70) and weak defenses (DCS < 40)
            elite_defenses = df_def[df_def['def_context_score'] > 70]['TEAM_ID'].tolist()
            weak_defenses = df_def[df_def['def_context_score'] < 40]['TEAM_ID'].tolist()

            # 2. Load Regular Season Game Logs
            game_logs_path = self.data_dir / f"rs_game_logs_{season}.csv"
            if not game_logs_path.exists():
                logger.warning(f"  - RS Game Logs not found at {game_logs_path}, skipping.")
                return pd.DataFrame()
                
            df_logs = pd.read_csv(game_logs_path, dtype={'GAME_ID': str, 'PLAYER_ID': int, 'TEAM_ID': int})

            # Get opponent team ID
            def get_opponent_team_abbrev(row):
                matchup = row['MATCHUP']
                teams = matchup.replace('@', 'vs.').split(' vs. ')
                # Find the abbreviation that is NOT the player's team's abbreviation
                player_team_abbrev = row['TEAM_ABBREVIATION']
                opponent_abbrev = teams[0] if teams[0] != player_team_abbrev else teams[1]
                return opponent_abbrev

            df_logs['OPPONENT_TEAM_ABBREV'] = df_logs.apply(get_opponent_team_abbrev, axis=1)
            df_logs['OPPONENT_TEAM_ID'] = df_logs['OPPONENT_TEAM_ABBREV'].map(ABBREV_TO_ID)

            # Drop rows where opponent ID could not be mapped (just in case)
            df_logs.dropna(subset=['OPPONENT_TEAM_ID'], inplace=True)
            df_logs['OPPONENT_TEAM_ID'] = df_logs['OPPONENT_TEAM_ID'].astype(int)
            
            # Add opponent DCS to each game log
            df_logs['OPPONENT_DCS'] = df_logs['OPPONENT_TEAM_ID'].map(dcs_map)

            # 3. Split by Opponent Quality
            df_vs_top10 = df_logs[df_logs['OPPONENT_TEAM_ID'].isin(top_10_defenses)]
            df_vs_bottom10 = df_logs[df_logs['OPPONENT_TEAM_ID'].isin(bottom_10_defenses)]
            df_vs_elite = df_logs[df_logs['OPPONENT_TEAM_ID'].isin(elite_defenses)]
            df_vs_weak = df_logs[df_logs['OPPONENT_TEAM_ID'].isin(weak_defenses)]

            # 4. Aggregate Player Stats
            def aggregate_player_stats(df, suffix):
                if df.empty:
                    return pd.DataFrame()
                
                player_agg = df.groupby('PLAYER_ID').agg(
                    FGA=('FGA', 'sum'),
                    FGM=('FGM', 'sum'),
                    FG3A=('FG3A', 'sum'),
                    FG3M=('FG3M', 'sum'),
                    FTA=('FTA', 'sum'),
                    FTM=('FTM', 'sum'),
                    USG_PCT=('USG_PCT', 'mean'), # Note: API has a typo USU_PCT corrected to USG_PCT
                    MIN=('MIN', 'sum')
                ).reset_index()

                # Calculate TS%
                player_agg[f'TS_PCT_{suffix}'] = np.where(
                    player_agg['FGA'] + 0.44 * player_agg['FTA'] > 0,
                    (player_agg['FGM'] + 0.5 * player_agg['FG3M']) / (2 * (player_agg['FGA'] + 0.44 * player_agg['FTA'])),
                    0
                )
                player_agg = player_agg.rename(columns={'USG_PCT': f'USG_PCT_{suffix}', 'MIN': f'MIN_{suffix}'})
                return player_agg[['PLAYER_ID', f'TS_PCT_{suffix}', f'USG_PCT_{suffix}', f'MIN_{suffix}']]

            agg_top10 = aggregate_player_stats(df_vs_top10, 'vs_top10')
            agg_bottom10 = aggregate_player_stats(df_vs_bottom10, 'vs_bottom10')
            agg_elite = aggregate_player_stats(df_vs_elite, 'vs_elite')
            agg_weak = aggregate_player_stats(df_vs_weak, 'vs_weak')

            # 5. Calculate average opponent DCS faced (weighted by minutes)
            # Handle case where df_logs might be empty or have no valid DCS values
            if len(df_logs) > 0 and df_logs['OPPONENT_DCS'].notna().any():
                opp_dcs_weighted = df_logs.groupby('PLAYER_ID').apply(
                    lambda x: np.average(x['OPPONENT_DCS'], weights=x['MIN']) if x['OPPONENT_DCS'].notna().any() else np.nan,
                    include_groups=False
                ).reset_index()
                opp_dcs_weighted.columns = ['PLAYER_ID', 'AVG_OPPONENT_DCS']
                
                # Also calculate simple average
                opp_dcs_simple = df_logs.groupby('PLAYER_ID')['OPPONENT_DCS'].mean().reset_index()
                opp_dcs_simple.columns = ['PLAYER_ID', 'MEAN_OPPONENT_DCS']
            else:
                opp_dcs_weighted = pd.DataFrame(columns=['PLAYER_ID', 'AVG_OPPONENT_DCS'])
                opp_dcs_simple = pd.DataFrame(columns=['PLAYER_ID', 'MEAN_OPPONENT_DCS'])

            # 6. Merge all context features - start with top10/bottom10 which should always exist
            if not agg_top10.empty and not agg_bottom10.empty:
                df_context = pd.merge(agg_top10, agg_bottom10, on='PLAYER_ID', how='outer')
            elif not agg_top10.empty:
                df_context = agg_top10.copy()
            elif not agg_bottom10.empty:
                df_context = agg_bottom10.copy()
            else:
                # If both are empty, we can't create context features
                logger.warning(f"  - No top10/bottom10 data for {season}, skipping context metrics.")
                return pd.DataFrame()
            
            # Merge elite/weak stats if they exist
            if not agg_elite.empty:
                df_context = pd.merge(df_context, agg_elite, on='PLAYER_ID', how='outer')
            if not agg_weak.empty:
                df_context = pd.merge(df_context, agg_weak, on='PLAYER_ID', how='outer')
            if not opp_dcs_weighted.empty:
                df_context = pd.merge(df_context, opp_dcs_weighted, on='PLAYER_ID', how='outer')
            if not opp_dcs_simple.empty:
                df_context = pd.merge(df_context, opp_dcs_simple, on='PLAYER_ID', how='outer')
            
            # Filter for meaningful sample size (at least 50 minutes vs top 10 and bottom 10)
            df_context = df_context[
                (df_context['MIN_vs_top10'].fillna(0) >= 50) & 
                (df_context['MIN_vs_bottom10'].fillna(0) >= 50)
            ]

            # 7. Create Features
            # Existing QOC features
            df_context['QOC_TS_DELTA'] = df_context['TS_PCT_vs_top10'].fillna(0) - df_context['TS_PCT_vs_bottom10'].fillna(0)
            df_context['QOC_USG_DELTA'] = df_context['USG_PCT_vs_top10'].fillna(0) - df_context['USG_PCT_vs_bottom10'].fillna(0)
            
            # NEW: Elite vs Weak defense features (only if columns exist)
            if 'TS_PCT_vs_elite' in df_context.columns and 'TS_PCT_vs_weak' in df_context.columns:
                df_context['ELITE_WEAK_TS_DELTA'] = (
                    df_context['TS_PCT_vs_elite'].fillna(0) - df_context['TS_PCT_vs_weak'].fillna(0)
                )
            else:
                df_context['ELITE_WEAK_TS_DELTA'] = 0
                
            if 'USG_PCT_vs_elite' in df_context.columns and 'USG_PCT_vs_weak' in df_context.columns:
                df_context['ELITE_WEAK_USG_DELTA'] = (
                    df_context['USG_PCT_vs_elite'].fillna(0) - df_context['USG_PCT_vs_weak'].fillna(0)
                )
            else:
                df_context['ELITE_WEAK_USG_DELTA'] = 0
            
            # Fill NaN values for players who didn't face elite/weak defenses
            if 'TS_PCT_vs_elite' in df_context.columns:
                df_context['TS_PCT_vs_elite'] = df_context['TS_PCT_vs_elite'].fillna(0)
            if 'TS_PCT_vs_weak' in df_context.columns:
                df_context['TS_PCT_vs_weak'] = df_context['TS_PCT_vs_weak'].fillna(0)
            if 'USG_PCT_vs_elite' in df_context.columns:
                df_context['USG_PCT_vs_elite'] = df_context['USG_PCT_vs_elite'].fillna(0)
            if 'USG_PCT_vs_weak' in df_context.columns:
                df_context['USG_PCT_vs_weak'] = df_context['USG_PCT_vs_weak'].fillna(0)
            if 'MIN_vs_elite' in df_context.columns:
                df_context['MIN_vs_elite'] = df_context['MIN_vs_elite'].fillna(0)
            if 'MIN_vs_weak' in df_context.columns:
                df_context['MIN_vs_weak'] = df_context['MIN_vs_weak'].fillna(0)
            
            logger.info(f"✅ Processed Context Metrics for {len(df_context)} players.")
            logger.info(f"  - Added AVG_OPPONENT_DCS (weighted by minutes)")
            logger.info(f"  - Added ELITE_WEAK_TS_DELTA and ELITE_WEAK_USG_DELTA")
            return df_context

        except Exception as e:
            logger.error(f"❌ Error in Context Metrics: {e}", exc_info=True)
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

                # 3. Context
                df_context = self.fetch_context_metrics(season)
                
                # Merge Vectors
                df_season = df_creation
                if not df_leverage.empty:
                    df_season = pd.merge(df_season, df_leverage, on='PLAYER_ID', how='left')
                else:
                    logger.warning(f"No leverage data for {season}, filling with NaNs")
                    df_season['LEVERAGE_TS_DELTA'] = np.nan
                    df_season['LEVERAGE_USG_DELTA'] = np.nan
                    df_season['CLUTCH_MIN_TOTAL'] = 0

                if not df_context.empty:
                    df_season = pd.merge(df_season, df_context, on='PLAYER_ID', how='left')
                else:
                    logger.warning(f"No context data for {season}, filling with NaNs")
                    df_season['QOC_TS_DELTA'] = np.nan
                    df_season['QOC_USG_DELTA'] = np.nan
                    df_season['AVG_OPPONENT_DCS'] = np.nan
                    df_season['MEAN_OPPONENT_DCS'] = np.nan
                    df_season['ELITE_WEAK_TS_DELTA'] = np.nan
                    df_season['ELITE_WEAK_USG_DELTA'] = np.nan
                
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
                        'CREATION_TAX', 'CREATION_BOOST', 'CREATION_VOLUME_RATIO',
                        'LEVERAGE_TS_DELTA', 'LEVERAGE_USG_DELTA', 'CLUTCH_MIN_TOTAL',
                        'QOC_TS_DELTA', 'QOC_USG_DELTA',
                        'AVG_OPPONENT_DCS', 'MEAN_OPPONENT_DCS',
                        'ELITE_WEAK_TS_DELTA', 'ELITE_WEAK_USG_DELTA',
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
    # Expanding window to capture enough historical data for training (2015-2025)
    all_seasons = [
        '2015-16', '2016-17', '2017-18', '2018-19',
        '2019-20', '2020-21', '2021-22', '2022-23', '2023-24', '2024-25'
    ]
    engine.run(seasons=all_seasons)
