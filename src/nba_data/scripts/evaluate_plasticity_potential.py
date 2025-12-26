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
from concurrent.futures import ThreadPoolExecutor
import argparse

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[3]))

# Add script directory to path for local imports
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from src.nba_data.api.nba_stats_client import create_nba_stats_client
from src.nba_data.api.synergy_playtypes_client import SynergyPlaytypesClient
from src.nba_data.constants import ID_TO_ABBREV, get_team_abbrev, ABBREV_TO_ID
from calculate_dependence_score import calculate_dependence_scores_batch
from src.nba_data.core.models import PlayerSeason
from pydantic import ValidationError


def validate_with_pydantic(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the DataFrame against the PlayerSeason Pydantic model.
    Logs errors for rows that fail validation.

    Args:
        df: The final DataFrame to validate.

    Returns:
        A DataFrame containing only the valid rows.
    """
    logger.info("Validating final dataset against PlayerSeason schema...")
    
    df_to_validate = df.copy()
    
    # The Pydantic model requires 'minutes', but the dataframe uses various metrics.
    # We will use 'RS_TOTAL_VOLUME' as the canonical measure for minutes played.
    if 'RS_TOTAL_VOLUME' in df_to_validate.columns:
        df_to_validate.rename(columns={'RS_TOTAL_VOLUME': 'minutes'}, inplace=True)
    elif 'minutes' not in df_to_validate.columns:
        logger.warning("No 'minutes' or 'RS_TOTAL_VOLUME' column found for validation. Using 0.0 as default.")
        df_to_validate['minutes'] = 0.0

    # Ensure USG_PCT is present for validation
    if 'USG_PCT' not in df_to_validate.columns:
        logger.warning("No 'USG_PCT' column found for validation. Using 0.0 as default.")
        df_to_validate['USG_PCT'] = 0.0
        
    # Ensure TS_PCT is present for validation
    if 'TS_PCT' not in df_to_validate.columns:
        logger.warning("No 'TS_PCT' column found for validation. Using 0.0 as default.")
        df_to_validate['TS_PCT'] = 0.0
        
    # Ensure PLAYER_NAME is present for validation
    if 'PLAYER_NAME' not in df_to_validate.columns:
        logger.warning("No 'PLAYER_NAME' column found for validation. Using 'Unknown' as default.")
        df_to_validate['PLAYER_NAME'] = 'Unknown'


    validated_records = []
    error_count = 0
    total_rows = len(df_to_validate)
    
    for index, row in df_to_validate.iterrows():
        try:
            # Pydantic can validate directly from a dict
            validated_model = PlayerSeason.model_validate(row.to_dict())
            validated_records.append(validated_model.model_dump())
        except ValidationError:
            error_count += 1
            # Skip logging individual errors to prevent spam
            pass

    if error_count > 0:
        logger.warning(f"Validation failed for {error_count} out of {total_rows} rows ({error_count/total_rows:.1%}). These rows will be dropped.")
    
    if not validated_records:
        logger.error("No records passed validation. Returning an empty DataFrame.")
        return pd.DataFrame()

    validated_df = pd.DataFrame(validated_records)
    logger.info(f"Validation complete. {len(validated_df)} / {total_rows} rows passed.")
    
    # Revert column name if we changed it
    if 'minutes' in validated_df.columns and 'RS_TOTAL_VOLUME' in df.columns:
        validated_df.rename(columns={'minutes': 'RS_TOTAL_VOLUME'}, inplace=True)

    return validated_df


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
        self.playtype_client = SynergyPlaytypesClient()
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_zero_dribble_stats(self, season: str, season_type: str = "Regular Season") -> pd.DataFrame:
        """
        Fetches and processes shooting statistics for '0 Dribble' attempts for a given season.

        This function is a dedicated pipeline for acquiring the ground-truth data for
        off-ball scoring value, as defined in Project Phoenix. It includes robust error
        handling and returns a clean DataFrame.

        Args:
            season (str): The season to fetch data for (e.g., "2023-24").
            season_type (str): "Regular Season" or "Playoffs"

        Returns:
            pd.DataFrame: A DataFrame containing zero-dribble shooting stats with columns
                          [PLAYER_ID, PLAYER_NAME, EFG_PCT_0_DRIBBLE, FGA_0_DRIBBLE].
                          Returns an empty DataFrame if the API call fails or returns no data.
        """
        logger.info(f"  - Executing Phoenix Pipeline: Fetching 0 Dribble ground truth for {season} ({season_type})...")
        try:
            zero_dribbles_data = self.client.get_league_player_shooting_stats(
                season=season, 
                dribble_range="0 Dribbles",
                season_type=season_type
            )
            
            if not zero_dribbles_data or 'resultSets' not in zero_dribbles_data or not zero_dribbles_data['resultSets']:
                logger.warning(f"    -> No result sets found for 0 Dribble data in {season} ({season_type}).")
                return pd.DataFrame()

            result_set = zero_dribbles_data['resultSets'][0]
            headers = result_set.get('headers')
            rows = result_set.get('rowSet')

            if not headers or not rows:
                logger.warning(f"    -> API call for 0 Dribbles in {season} ({season_type}) was successful but returned no player data.")
                return pd.DataFrame()

            df_zero = pd.DataFrame(rows, columns=headers)
            
            # Select and rename columns for clarity and consistency
            df_zero = df_zero[['PLAYER_ID', 'PLAYER_NAME', 'EFG_PCT', 'FGA']]
            df_zero = df_zero.rename(columns={
                'EFG_PCT': 'EFG_PCT_0_DRIBBLE',
                'FGA': 'FGA_0_DRIBBLE'
            })

            
            
            logger.info(f"    -> Success: Fetched {len(df_zero)} rows for 0 Dribble stats.")

            # Calibrated MINIMUM VOLUME THRESHOLD (Lowered for inclusivity of Latent Stars)
            initial_count = len(df_zero)
            df_zero = df_zero[df_zero['FGA_0_DRIBBLE'] > 1.5].copy()
            logger.info(f"    -> Filtered {initial_count - len(df_zero)} players below 1.5 FGA_0_DRIBBLE threshold.")

            return df_zero

        except Exception as e:
            logger.error(f"    -> ❌ Critical error in fetch_zero_dribble_stats for {season} ({season_type}): {e}", exc_info=True)
            return pd.DataFrame()
        
    def fetch_creation_metrics(self, season, season_type="Regular Season"):
        """
        Vector 1: Self-Creation (The 'Creation Tax')
        Fetches shooting stats by Dribble Range.
        """
        logger.info(f"Fetching Creation Metrics for {season} ({season_type})...")
        
        try:
            # 1. Zero Dribbles (Dependent) - Using the new robust pipeline
            df_zero = self.fetch_zero_dribble_stats(season, season_type=season_type)
            if df_zero.empty and season_type == "Regular Season":
                logger.error(f"Could not fetch essential 0-dribble data for {season}. Aborting creation metrics.")
                return pd.DataFrame()
            elif df_zero.empty:
                 logger.warning(f"No 0-dribble data for {season} ({season_type}).")

            
            # 2. 3-6 Dribbles (Self-Created/Iso)
            logger.info(f"  - Fetching 3-6 Dribbles for {season} ({season_type})...")
            iso_dribbles = self.client.get_league_player_shooting_stats(
                season=season, 
                dribble_range="3-6 Dribbles",
                season_type=season_type
            )
            
            if iso_dribbles and 'resultSets' in iso_dribbles and iso_dribbles['resultSets']:
                 df_iso = pd.DataFrame(iso_dribbles['resultSets'][0]['rowSet'], 
                                      columns=iso_dribbles['resultSets'][0]['headers'])
                 df_iso = df_iso[['PLAYER_ID', 'EFG_PCT', 'FGA']]
                 df_iso = df_iso.rename(columns={
                    'EFG_PCT': 'EFG_PCT_3_DRIBBLE',
                    'FGA': 'FGA_3_DRIBBLE'
                 })
            else:
                 df_iso = pd.DataFrame(columns=['PLAYER_ID', 'EFG_PCT_3_DRIBBLE', 'FGA_3_DRIBBLE'])

            logger.info(f"    -> Got {len(df_iso)} rows.")
            
            # 3. 7+ Dribbles (Deep Iso)
            logger.info(f"  - Fetching 7+ Dribbles for {season} ({season_type})...")
            deep_iso = self.client.get_league_player_shooting_stats(
                season=season, 
                dribble_range="7+ Dribbles",
                season_type=season_type
            )
            
            if deep_iso and 'resultSets' in deep_iso and deep_iso['resultSets']:
                df_deep = pd.DataFrame(deep_iso['resultSets'][0]['rowSet'], 
                                       columns=deep_iso['resultSets'][0]['headers'])
                df_deep = df_deep[['PLAYER_ID', 'EFG_PCT', 'FGA']]
                df_deep = df_deep.rename(columns={
                    'EFG_PCT': 'EFG_PCT_7_DRIBBLE',
                    'FGA': 'FGA_7_DRIBBLE'
                })
            else:
                 df_deep = pd.DataFrame(columns=['PLAYER_ID', 'EFG_PCT_7_DRIBBLE', 'FGA_7_DRIBBLE'])

            logger.info(f"    -> Got {len(df_deep)} rows.")
            
            # Merge
            logger.info("  - Merging creation datasets...")
            if not df_zero.empty:
                 df_creation = df_zero
            else:
                 # If no zero dribble data, start with ISO data if available, or empty
                 if not df_iso.empty:
                      df_creation = df_iso[['PLAYER_ID']].drop_duplicates()
                 else:
                      return pd.DataFrame() # No data at all

            if not df_iso.empty:
                 df_creation = pd.merge(df_creation, df_iso, on='PLAYER_ID', how='outer')
            if not df_deep.empty:
                 df_creation = pd.merge(df_creation, df_deep, on='PLAYER_ID', how='outer')
                        
            # Fill NaNs with 0 (some players never take 7+ dribbles)
            df_creation = df_creation.fillna(0)
            
            # Feature Engineering: Creation Tax
            # How much efficiency do you lose when you have to dribble?
            
            # Weighted average of 3+ dribbles
            df_creation['FGA_ISO_TOTAL'] = df_creation['FGA_3_DRIBBLE'] + df_creation['FGA_7_DRIBBLE']
            
            # Avoid division by zero
            df_creation['EFG_ISO_WEIGHTED'] = np.where(
                df_creation['FGA_ISO_TOTAL'] > 0.5, # Calibrated MINIMUM VOLUME THRESHOLD (Lowered for inclusivity)
                ((df_creation['EFG_PCT_3_DRIBBLE'] * df_creation['FGA_3_DRIBBLE']) + 
                 (df_creation['EFG_PCT_7_DRIBBLE'] * df_creation['FGA_7_DRIBBLE'])) / df_creation['FGA_ISO_TOTAL'],
                0 # Set to 0 for unqualified players
            )
            
            df_creation['CREATION_TAX'] = df_creation['EFG_ISO_WEIGHTED'] - df_creation['EFG_PCT_0_DRIBBLE']
            
            # Feature: Creation Volume Ratio
            df_creation['TOTAL_FGA_TRACKED'] = df_creation['FGA_0_DRIBBLE'] + df_creation['FGA_ISO_TOTAL']
            
            df_creation['CREATION_VOLUME_RATIO'] = np.where(
                df_creation['TOTAL_FGA_TRACKED'] > 0,
                df_creation['FGA_ISO_TOTAL'] / df_creation['TOTAL_FGA_TRACKED'],
                0
            )
            
            # PHASE 1: CREATION_BOOST - Positive creation tax is a superpower
            # If efficiency increases when creating (positive tax), weight by 1.5x
            df_creation['CREATION_BOOST'] = np.where(
                df_creation['CREATION_TAX'] > 0,
                1.5,
                1.0
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

    def _calculate_fragility_score(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Calculating FRAGILITY_SCORE (v3)...")

        def robust_normalize(series):
            min_val = series.quantile(0.05)
            max_val = series.quantile(0.95)
            if (max_val - min_val) == 0: return pd.Series(0.5, index=series.index)
            return ((series - min_val) / (max_val - min_val)).clip(0, 1)
        # 1. Calculate base Physicality Score
        norm_ftr = robust_normalize(df.get('RS_FTr', pd.Series(0, index=df.index)))
        norm_rim_appetite = robust_normalize(df.get('RS_RIM_APPETITE', pd.Series(0, index=df.index)))
        physicality_score = (0.6 * norm_ftr + 0.4 * norm_rim_appetite).fillna(0.5)
        # 2. De-Risking: "The Curry Paradox" (Sniper Exception)
        qualified_mask = df.get('TOTAL_FGA_TRACKED', pd.Series(0, index=df.index)) > 200 # Use existing volume metric
        qualified_players = df[qualified_mask]
        efg_95th = qualified_players['EFG_ISO_WEIGHTED'].quantile(0.95)
        sq_delta_95th = qualified_players['SHOT_QUALITY_GENERATION_DELTA'].quantile(0.95)
        is_elite_shooter = (df['EFG_ISO_WEIGHTED'] > efg_95th) | (df['SHOT_QUALITY_GENERATION_DELTA'] > sq_delta_95th)
        physicality_score.loc[is_elite_shooter] = 1.0 # Immune to penalty
        # 3. De-Risking: "The Grifter Trap" (Trae Young Rule)
        ftr_80th = qualified_players['RS_FTr'].quantile(0.80)
        rim_appetite_40th = qualified_players['RS_RIM_APPETITE'].quantile(0.40)
        is_grifter = (df['RS_FTr'] > ftr_80th) & (df['RS_RIM_APPETITE'] < rim_appetite_40th)
        physicality_score.loc[is_grifter] = physicality_score.loc[is_grifter].clip(upper=0.5)
        # 4. Calculate Final Fragility Score
        norm_open_shot_freq = robust_normalize(df.get('RS_OPEN_SHOT_FREQUENCY', pd.Series(0, index=df.index)))
        norm_sq_delta = robust_normalize(df.get('SHOT_QUALITY_GENERATION_DELTA', pd.Series(0, index=df.index)))
        df['FRAGILITY_SCORE'] = (
            ((1.0 - physicality_score) * 0.50) +
            (norm_open_shot_freq * 0.30) +
            ((1.0 - norm_sq_delta) * 0.20)
        ).fillna(0.5)
        logger.info(f"  -> FRAGILITY_SCORE calculated. Average: {df['FRAGILITY_SCORE'].mean():.3f}")
        return df

    def calculate_context_metrics(self, season):
        """
        Vector 3: Context (Quality of Competition)
        """
        # Placeholder for now until we confirm RS logs strategy
        return pd.DataFrame()
    
    def fetch_player_metadata(self, season):
        """
        Fetch USG_PCT, TS_PCT, and AGE for all players in a season.
        This ensures we have complete metadata without dependency on filtered files.
        
        Returns:
            DataFrame with columns: PLAYER_ID, PLAYER_NAME, USG_PCT, TS_PCT, AGE
        """
        logger.info(f"Fetching player metadata (USG_PCT, TS_PCT, AGE) for {season}...")
        
        try:
            # Fetch Advanced stats for USG_PCT, TS_PCT and AGE
            advanced_stats = self.client.get_league_player_advanced_stats(season=season, season_type="Regular Season")
            df_advanced = pd.DataFrame(
                advanced_stats['resultSets'][0]['rowSet'],
                columns=advanced_stats['resultSets'][0]['headers']
            )
            
            # Verify required columns exist
            required_cols = ['PLAYER_ID', 'PLAYER_NAME', 'USG_PCT', 'TS_PCT', 'AGE', 'MIN']
            missing_cols = [col for col in required_cols if col not in df_advanced.columns]
            if missing_cols:
                logger.error(f"❌ Missing required columns in advanced_stats response: {missing_cols}")
                logger.error(f"Available columns: {list(df_advanced.columns)}")
                return pd.DataFrame()
            
            # Select only needed columns
            df_metadata = df_advanced[required_cols].copy()
            
            # Rename MIN to RS_TOTAL_VOLUME for consistency
            df_metadata.rename(columns={'MIN': 'RS_TOTAL_VOLUME'}, inplace=True)
            
            # Handle USG_PCT: API might return as decimal (0.20) or percentage (20.0)
            if len(df_metadata) > 0:
                sample_usg = df_metadata['USG_PCT'].dropna()
                if len(sample_usg) > 0:
                    max_usg = sample_usg.max()
                    if max_usg > 1.0:
                        # Stored as percentage, convert to decimal for consistency
                        df_metadata['USG_PCT'] = df_metadata['USG_PCT'] / 100.0
            
            logger.info(f"  ✅ Fetched metadata for {len(df_metadata)} players")
            logger.info(f"  - USG_PCT coverage: {df_metadata['USG_PCT'].notna().sum()} / {len(df_metadata)}")
            logger.info(f"  - TS_PCT coverage: {df_metadata['TS_PCT'].notna().sum()} / {len(df_metadata)}")
            logger.info(f"  - AGE coverage: {df_metadata['AGE'].notna().sum()} / {len(df_metadata)}")
            logger.info(f"  - RS_TOTAL_VOLUME (MIN) coverage: {df_metadata['RS_TOTAL_VOLUME'].notna().sum()} / {len(df_metadata)}")
            
            return df_metadata
            
        except Exception as e:
            logger.error(f"❌ Error fetching player metadata for {season}: {e}", exc_info=True)
            return pd.DataFrame()

    def fetch_playtype_metrics(self, season, season_type="Regular Season"):
        """
        Fetch playtype data (ISO_FREQUENCY, PNR_HANDLER_FREQUENCY) from NBA Synergy API.
        
        Returns:
            DataFrame with columns: PLAYER_ID, ISO_FREQUENCY, ISO_PPP, ISO_EFG_PCT, ...
        """
        logger.info(f"Fetching Playtype Metrics for {season} ({season_type})...")
        
        try:
            # Fetch all playtype data for the season
            all_playtype_data = self.playtype_client.get_all_playtype_stats_for_season(
                season_year=season,
                season_type=season_type
            )
            
            if not all_playtype_data:
                logger.warning(f"No playtype data returned for {season} ({season_type})")
                return pd.DataFrame()
            
            # Parse all playtype responses
            all_records = []
            for play_type, response_data in all_playtype_data.items():
                if 'error' in response_data:
                    logger.warning(f"Error fetching {play_type} for {season} ({season_type}): {response_data['error']}")
                    continue
                
                try:
                    records = self.playtype_client.parse_playtype_response(response_data)
                    all_records.extend(records)
                except Exception as e:
                    logger.warning(f"Error parsing {play_type} for {season} ({season_type}): {e}")
                    continue
            
            if not all_records:
                logger.warning(f"No playtype records parsed for {season} ({season_type})")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df_playtype = pd.DataFrame(all_records)
            
            # Define aggregation functions for efficiency metrics
            # We need to handle multi-team players by weighting efficiency by volume
            def weighted_avg(x, val_col, weight_col):
                try:
                    return np.average(x[val_col], weights=x[weight_col])
                except ZeroDivisionError:
                    return 0.0
                except Exception:
                    return 0.0

            # 1. Group by Player and PlayType to aggregate across teams
            # We need to calculate: Total FGA, Total POSS, Weighted PPP, Weighted EFG
            
            # First, sum the volumes
            df_grouped_vol = df_playtype.groupby(['player_id', 'play_type'])[['field_goals_attempted', 'possessions']].sum().reset_index()
            
            # Then calculate weighted efficiencies
            # This is tricky with groupby.apply, so we'll iterate or use a custom aggregation
            
            # Simplify: Just iterate through unique player/playtype combos? No, that's slow.
            # Use apply.
            
            df_grouped_eff = df_playtype.groupby(['player_id', 'play_type']).apply(
                lambda x: pd.Series({
                    'PPP': weighted_avg(x, 'points_per_possession', 'possessions'),
                    'EFG_PCT': weighted_avg(x, 'effective_field_goal_percentage', 'field_goals_attempted')
                })
            ).reset_index()
            
            # Merge volume and efficiency
            df_playtype_grouped = pd.merge(df_grouped_vol, df_grouped_eff, on=['player_id', 'play_type'])
            
            # Calculate total FGA across all play types for each player (for Frequency calc)
            df_total = df_playtype_grouped.groupby('player_id')['field_goals_attempted'].sum().reset_index()
            df_total.columns = ['PLAYER_ID', 'TOTAL_FGA_PLAYTYPE']
            
            # Helper to extract playtype stats
            def extract_playtype_stats(pt_name, prefix):
                df_pt = df_playtype_grouped[df_playtype_grouped['play_type'] == pt_name].copy()
                if not df_pt.empty:
                    df_pt = df_pt[['player_id', 'field_goals_attempted', 'possessions', 'PPP', 'EFG_PCT']].copy()
                    df_pt.columns = ['PLAYER_ID', f'{prefix}_FGA', f'{prefix}_POSS', f'{prefix}_PPP', f'{prefix}_EFG_PCT']
                else:
                    df_pt = pd.DataFrame(columns=['PLAYER_ID', f'{prefix}_FGA', f'{prefix}_POSS', f'{prefix}_PPP', f'{prefix}_EFG_PCT'])
                return df_pt

            # Extract Isolation
            df_iso = extract_playtype_stats('Isolation', 'ISO')
            
            # Extract PnR Handler
            df_pnr = extract_playtype_stats('PRBallHandler', 'PNR_HANDLER')
            
            # Extract PostUp
            df_post = extract_playtype_stats('Postup', 'POST')
            
            # Extract SpotUp (often resilient)
            # df_spot = extract_playtype_stats('SpotUp', 'SPOT') # API doesn't support SpotUp? checked earlier code, said removed.
            # Let's check 'SpotUp' again? The comment in client said "SpotUp is not a valid playtype name". 
            # We'll skip for now.

            # Merge all
            df_result = df_total.copy()
            
            for df_part in [df_iso, df_pnr, df_post]:
                if not df_part.empty:
                    df_result = pd.merge(df_result, df_part, on='PLAYER_ID', how='left')
            
            # Fill NaNs
            cols_to_fill = [c for c in df_result.columns if c != 'PLAYER_ID']
            df_result[cols_to_fill] = df_result[cols_to_fill].fillna(0.0)
            
            # Calculate frequencies
            df_result['ISO_FREQUENCY'] = np.where(
                df_result['TOTAL_FGA_PLAYTYPE'] > 0,
                df_result['ISO_FGA'] / df_result['TOTAL_FGA_PLAYTYPE'],
                0.0
            )
            
            df_result['PNR_HANDLER_FREQUENCY'] = np.where(
                df_result['TOTAL_FGA_PLAYTYPE'] > 0,
                df_result['PNR_HANDLER_FGA'] / df_result['TOTAL_FGA_PLAYTYPE'],
                0.0
            )
            
            df_result['POST_TOUCH_FREQUENCY'] = np.where(
                df_result['TOTAL_FGA_PLAYTYPE'] > 0,
                df_result['POST_FGA'] / df_result['TOTAL_FGA_PLAYTYPE'],
                0.0
            )
            
            # Select columns to return
            # We want Frequency AND Efficiency (PPP, EFG)
            cols_to_return = ['PLAYER_ID', 
                              'ISO_FREQUENCY', 'ISO_PPP', 'ISO_EFG_PCT',
                              'PNR_HANDLER_FREQUENCY', 'PNR_HANDLER_PPP', 'PNR_HANDLER_EFG_PCT',
                              'POST_TOUCH_FREQUENCY', 'POST_PPP', 'POST_EFG_PCT']
            
            # Ensure all exist
            for col in cols_to_return:
                if col not in df_result.columns:
                    df_result[col] = 0.0
                    
            df_result = df_result[cols_to_return].copy()
            
            logger.info(f"  ✅ Processed Playtype Metrics for {len(df_result)} players ({season_type})")
            return df_result
            
        except Exception as e:
            logger.error(f"❌ Error fetching playtype metrics for {season} ({season_type}): {e}", exc_info=True)
            return pd.DataFrame()

    def calculate_projected_playoff_output(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates PROJECTED_PLAYOFF_PPS and PROJECTED_PLAYOFF_OUTPUT.
        
        This is the core of the "Physics Simulation". It projects a player's
        regular season shot diet onto the playoff environment using calculated
        friction coefficients.
        
        Args:
            df (pd.DataFrame): DataFrame containing merged RS data and friction coefficients.
            
        Returns:
            pd.DataFrame: DataFrame with the new projected features.
        """
        logger.info("Calculating Projected Playoff Output features...")
        
        # Define shot types, their RS efficiency metric, RS volume metric, and friction coefficient
        shot_components = {
            'iso_dribbles': {
                'efficiency': 'EFG_ISO_WEIGHTED',
                'volume': 'FGA_ISO_TOTAL',
                'friction': 'FRICTION_COEFF_ISO'
            },
            'zero_dribbles': {
                'efficiency': 'EFG_PCT_0_DRIBBLE',
                'volume': 'FGA_0_DRIBBLE',
                'friction': 'FRICTION_COEFF_0_DRIBBLE'
            },
            'playtype_iso': {
                'efficiency': 'ISO_PPP_RS',
                'volume': 'ISO_FGA_RS',
                'friction': 'FRICTION_COEFF_PLAYTYPE_ISO'
            },
            'playtype_pnr': {
                'efficiency': 'PNR_HANDLER_PPP_RS',
                'volume': 'PNR_HANDLER_FGA_RS',
                'friction': 'FRICTION_COEFF_PNR_HANDLER'
            },
            'playtype_post': {
                'efficiency': 'POST_PPP_RS',
                'volume': 'POST_FGA_RS',
                'friction': 'FRICTION_COEFF_POST'
            }
        }
        
        # Calculate total FGA from all tracked components for weighting
        df['TOTAL_PROJECTED_FGA'] = 0
        for comp in shot_components.values():
            if comp['volume'] in df.columns:
                df['TOTAL_PROJECTED_FGA'] += df[comp['volume']].fillna(0)
        
        # Calculate projected PPS for each component
        df['PROJECTED_PLAYOFF_PPS'] = 0
        
        for name, comp in shot_components.items():
            # Ensure all required columns exist
            if all(c in df.columns for c in [comp['efficiency'], comp['volume'], comp['friction']]):
                
                # Shot weight = volume of this shot type / total volume
                shot_weight = (df[comp['volume']].fillna(0) / df['TOTAL_PROJECTED_FGA']).fillna(0)
                
                # Projected efficiency for this component = RS_efficiency * friction
                projected_comp_pps = df[comp['efficiency']].fillna(0) * df[comp['friction']].fillna(1.0)
                
                # Add the weighted component PPS to the total
                df['PROJECTED_PLAYOFF_PPS'] += shot_weight * projected_comp_pps
                
        # Handle cases where total FGA is zero to avoid NaN
        df['PROJECTED_PLAYOFF_PPS'] = df['PROJECTED_PLAYOFF_PPS'].fillna(0.0)
        
        # The "Unit Scaling" Trap Fix: Centralized Normalization
        # Ensure USG_PCT is 0-1 before creating the interaction term
        if 'USG_PCT' in df.columns:
            # First, ensure USG_PCT is numeric
            df['USG_PCT'] = pd.to_numeric(df['USG_PCT'], errors='coerce').fillna(df['USG_PCT'].median())
            
            # Now, normalize if it's in percentage format
            if df['USG_PCT'].max() > 1.0:
                logger.info(f"Normalizing USG_PCT from percentage to decimal format (max was {df['USG_PCT'].max():.1f})")
                df['USG_PCT'] /= 100.0
        else:
            df['USG_PCT'] = 0.0 # Default if missing
            
        # Final Feature: PROJECTED_PLAYOFF_OUTPUT (The "Remainder")
        # This is our primary First Principles feature.
        df['PROJECTED_PLAYOFF_OUTPUT'] = df['PROJECTED_PLAYOFF_PPS'] * df['USG_PCT']

        # NEW FEATURE (Dec 2025): HELIO_ABOVE_REPLACEMENT_VALUE
        # Solves the "Luka Paradox" without breaking the "DeRozan Filter".
        # Formula: (Max(0, USG - 0.30)^2) * (PPS - 0.90)
        # 1. Isolates Extreme Usage (>30%)
        # 2. Scales non-linearly (squared) to reward true Heliocentric outliers
        # 3. Penalizes inefficient volume (Westbrook Trap) by checking against replacement floor (0.90)
        
        # Calculate usage excess (only count usage above 30%)
        usage_excess = (df['USG_PCT'] - 0.30).clip(lower=0)
        
        # Calculate efficiency delta (relative to replacement level floor of 0.90 PPS)
        efficiency_delta = df['PROJECTED_PLAYOFF_PPS'] - 0.90
        
        # Calculate the feature
        df['HELIO_ABOVE_REPLACEMENT_VALUE'] = (usage_excess ** 2) * efficiency_delta
        
        logger.info(f"Successfully calculated PROJECTED_PLAYOFF_OUTPUT. Mean: {df['PROJECTED_PLAYOFF_OUTPUT'].mean():.4f}")
        
        return df

    def run(self, seasons=['2021-22', '2022-23', '2023-24'], max_workers=1):
        
        all_seasons_data = []
        
        def process_single_season(season):
            logger.info(f"=== Processing {season} ===")
            
            try:
                # 1. Fetch Base Metadata (The new "Source of Truth" for a season)
                logger.info(f"--- Fetching Base Player Metadata for {season} ---")
                df_season = self.fetch_player_metadata(season)
                if df_season.empty:
                    logger.warning(f"Skipping {season} due to missing base metadata.")
                    return None

                # 2. Fetch Regular Season Features
                logger.info(f"--- Fetching Regular Season data for {season} ---")
                df_creation_rs = self.fetch_creation_metrics(season, season_type="Regular Season")
                df_playtype_rs = self.fetch_playtype_metrics(season, season_type="Regular Season")
                
                # 3. Fetch Playoff Data for Friction Calculation
                logger.info(f"--- Fetching Playoff data for {season} ---")
                df_creation_po = self.fetch_creation_metrics(season, season_type="Playoffs")
                df_playtype_po = self.fetch_playtype_metrics(season, season_type="Playoffs")
                
                # 4. Calculate Friction Coefficients
                logger.info(f"--- Calculating Friction Coefficients for {season} ---")
                
                # Merge Creation Metrics
                df_creation_merged = pd.merge(
                    df_creation_rs.add_suffix('_RS'),
                    df_creation_po.add_suffix('_PO'),
                    left_on='PLAYER_ID_RS', right_on='PLAYER_ID_PO',
                    how='inner' # Inner join: must have both RS and PO data
                )
                if not df_creation_merged.empty:
                    df_creation_merged = df_creation_merged.drop(columns=['PLAYER_ID_PO', 'PLAYER_NAME_PO'])
                    df_creation_merged = df_creation_merged.rename(columns={'PLAYER_ID_RS': 'PLAYER_ID', 'PLAYER_NAME_RS': 'PLAYER_NAME'})

                # Merge Playtype Metrics
                df_playtype_merged = pd.merge(
                    df_playtype_rs.add_suffix('_RS'),
                    df_playtype_po.add_suffix('_PO'),
                    left_on='PLAYER_ID_RS', right_on='PLAYER_ID_PO',
                    how='inner'
                )
                if not df_playtype_merged.empty:
                    df_playtype_merged = df_playtype_merged.drop(columns=['PLAYER_ID_PO'])
                    df_playtype_merged = df_playtype_merged.rename(columns={'PLAYER_ID_RS': 'PLAYER_ID'})

                # Combine all friction data
                if not df_creation_merged.empty and not df_playtype_merged.empty:
                    df_friction = pd.merge(df_creation_merged, df_playtype_merged, on='PLAYER_ID', how='outer')
                elif not df_creation_merged.empty:
                    df_friction = df_creation_merged
                elif not df_playtype_merged.empty:
                    df_friction = df_playtype_merged
                else:
                    df_friction = pd.DataFrame()
                
                friction_cols = []
                if not df_friction.empty:
                    # Dribble-based friction
                    if 'EFG_ISO_WEIGHTED_PO' in df_friction.columns and 'EFG_ISO_WEIGHTED_RS' in df_friction.columns:
                        df_friction['FRICTION_COEFF_ISO'] = df_friction['EFG_ISO_WEIGHTED_PO'] / df_friction['EFG_ISO_WEIGHTED_RS']
                        friction_cols.append('FRICTION_COEFF_ISO')
                    if 'EFG_PCT_0_DRIBBLE_PO' in df_friction.columns and 'EFG_PCT_0_DRIBBLE_RS' in df_friction.columns:
                        df_friction['FRICTION_COEFF_0_DRIBBLE'] = df_friction['EFG_PCT_0_DRIBBLE_PO'] / df_friction['EFG_PCT_0_DRIBBLE_RS']
                        friction_cols.append('FRICTION_COEFF_0_DRIBBLE')
                    
                    # Playtype-based friction (using PPP)
                    if 'ISO_PPP_PO' in df_friction.columns and 'ISO_PPP_RS' in df_friction.columns:
                        df_friction['FRICTION_COEFF_PLAYTYPE_ISO'] = df_friction['ISO_PPP_PO'] / df_friction['ISO_PPP_RS']
                        friction_cols.append('FRICTION_COEFF_PLAYTYPE_ISO')
                    if 'PNR_HANDLER_PPP_PO' in df_friction.columns and 'PNR_HANDLER_PPP_RS' in df_friction.columns:
                        df_friction['FRICTION_COEFF_PNR_HANDLER'] = df_friction['PNR_HANDLER_PPP_PO'] / df_friction['PNR_HANDLER_PPP_RS']
                        friction_cols.append('FRICTION_COEFF_PNR_HANDLER')
                    if 'POST_PPP_PO' in df_friction.columns and 'POST_PPP_RS' in df_friction.columns:
                        df_friction['FRICTION_COEFF_POST'] = df_friction['POST_PPP_PO'] / df_friction['POST_PPP_RS']
                        friction_cols.append('FRICTION_COEFF_POST')
                    
                    if friction_cols:
                        df_friction[friction_cols] = df_friction[friction_cols].replace([np.inf, -np.inf], np.nan).fillna(1.0)
                    
                    logger.info(f"Calculated friction for {len(df_friction)} players in {season}.")
                
                # 5. Fetch other RS-based metrics (Leverage, Context, etc.)
                df_leverage = self.fetch_leverage_metrics(season)
                df_context = self.fetch_context_metrics(season)
                
                # 6. Combine all data for the season using LEFT joins from metadata
                logger.info(f"--- Merging all feature sets for {season} ---")

                # Merge creation data
                if not df_creation_rs.empty:
                    df_season = pd.merge(df_season, df_creation_rs.drop(columns=['PLAYER_NAME']), on='PLAYER_ID', how='left')

                # Merge friction coefficients
                if not df_friction.empty:
                    df_season = pd.merge(df_season, df_friction[['PLAYER_ID'] + friction_cols], on='PLAYER_ID', how='left')
                    for col in friction_cols:
                         if col in df_season.columns:
                              df_season[col] = df_season[col].fillna(1.0)
                else:
                    for col in ['FRICTION_COEFF_ISO', 'FRICTION_COEFF_0_DRIBBLE', 'FRICTION_COEFF_PLAYTYPE_ISO', 'FRICTION_COEFF_PNR_HANDLER', 'FRICTION_COEFF_POST']:
                        df_season[col] = 1.0

                # Merge other datasets
                if not df_leverage.empty:
                    df_season = pd.merge(df_season, df_leverage, on='PLAYER_ID', how='left')
                if not df_context.empty:
                    df_season = pd.merge(df_season, df_context, on='PLAYER_ID', how='left')
                if not df_playtype_rs.empty:
                     df_season = pd.merge(df_season, df_playtype_rs.add_suffix('_RS'), left_on='PLAYER_ID', right_on='PLAYER_ID_RS', how='left')
                     if 'PLAYER_ID_RS' in df_season.columns:
                          df_season = df_season.drop(columns=['PLAYER_ID_RS'])

                # 7. Engineer the Projected Playoff Output Feature
                df_season = self.calculate_projected_playoff_output(df_season)
                
                df_season['SEASON'] = season
                return df_season
                
            except Exception as e:
                logger.error(f"Failed to process {season}: {e}", exc_info=True)
                return None

        # Process seasons in parallel
        logger.info(f"Processing {len(seasons)} seasons with {max_workers} workers...")
        if max_workers > 1:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(process_single_season, seasons))
        else:
            results = [process_single_season(s) for s in seasons]
            
        all_seasons_data = [r for r in results if r is not None]
        
        # Combine all
        if not all_seasons_data:
            logger.error("No data generated.")
            return
            
        final_df = pd.concat(all_seasons_data, ignore_index=True)

        pressure_path = self.results_dir / "pressure_features.csv"
        if pressure_path.exists():
            df_pressure = pd.read_csv(pressure_path)
            # Drop PLAYER_NAME if it exists to avoid merge conflicts
            if 'PLAYER_NAME' in df_pressure.columns:
                df_pressure = df_pressure.drop(columns=['PLAYER_NAME'])
            final_df = pd.merge(
                final_df,
                df_pressure,
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )

        physicality_path = self.results_dir / "physicality_features.csv"
        if physicality_path.exists():
            df_physicality = pd.read_csv(physicality_path)
            # Drop PLAYER_NAME if it exists to avoid merge conflicts
            if 'PLAYER_NAME' in df_physicality.columns:
                df_physicality = df_physicality.drop(columns=['PLAYER_NAME'])
            final_df = pd.merge(
                final_df,
                df_physicality,
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )
        
        rim_pressure_path = self.results_dir / "rim_pressure_features.csv"
        if rim_pressure_path.exists():
            df_rim_pressure = pd.read_csv(rim_pressure_path)
            # Drop PLAYER_NAME if it exists to avoid merge conflicts
            if 'PLAYER_NAME' in df_rim_pressure.columns:
                df_rim_pressure = df_rim_pressure.drop(columns=['PLAYER_NAME'])
            final_df = pd.merge(
                final_df,
                df_rim_pressure,
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )

        
        # --- Final Feature Engineering & Cleanup ---
        # (This will be where we do the final PROJECTED_PLAYOFF_OUTPUT calculation)
        
        # NEW FEATURES (Dec 2025): Latent Star Index and Inefficient Volume Score
        # These are critical for the Projected Dependence logic.
        
        # 1. INEFFICIENT_VOLUME_SCORE
        # Principle: Efficiency must survive Volume.
        # Measures volume that comes at the cost of extreme inefficiency.
        final_df['INEFFICIENT_VOLUME_SCORE'] = (
            final_df['CREATION_VOLUME_RATIO'].fillna(0) * 
            (-final_df['CREATION_TAX'].fillna(0)).clip(lower=0)
        )
        
        # 2. latent_score (Capacity Engine)
        # Principle: Ability precedes Responsibility.
        # Measures elite efficiency on low-to-moderate volume.
        baseline_eff = 0.44
        efficiency_delta = (final_df['EFG_ISO_WEIGHTED'].fillna(0) - baseline_eff).clip(lower=-0.1) # Soft floor
        volume_scalar = np.sqrt(final_df['CREATION_VOLUME_RATIO'].fillna(0)) * 10
        final_df['latent_score'] = efficiency_delta * volume_scalar
        
        # 3. Merging SHOT_QUALITY_GENERATION_DELTA (Source of Truth)
        # This is a prerequisite for dependence calculation.
        sq_path = Path("results/shot_quality_generation_delta.csv")
        if sq_path.exists():
            logger.info(f"Merging SHOT_QUALITY_GENERATION_DELTA from {sq_path}...")
            sq_df = pd.read_csv(sq_path)
            # Ensure types match for merging
            sq_df['PLAYER_ID'] = sq_df['PLAYER_ID'].astype(int)
            final_df['PLAYER_ID'] = final_df['PLAYER_ID'].astype(int)
            
            # Merge on ID and Season
            final_df = pd.merge(
                final_df, 
                sq_df[['PLAYER_ID', 'SEASON', 'SHOT_QUALITY_GENERATION_DELTA']], 
                on=['PLAYER_ID', 'SEASON'], 
                how='left'
            )
            # Fill missing with 0 (conservative)
            final_df['SHOT_QUALITY_GENERATION_DELTA'] = final_df['SHOT_QUALITY_GENERATION_DELTA'].fillna(0.0)

            # 4. HELIO_POTENTIAL_SCORE (Phase 4 Non-Linearity Feature)
            # Formula: SHOT_QUALITY_GENERATION_DELTA * (USG_PCT^1.5)
            # This rewards high creation quality at extreme usage exponentially.
            if 'USG_PCT' in final_df.columns:
                # Ensure USG_PCT is in decimal format for the exponent
                usg_decimal = final_df['USG_PCT']
                if usg_decimal.max() > 1.0:
                    usg_decimal = usg_decimal / 100.0
                
                final_df['HELIO_POTENTIAL_SCORE'] = final_df['SHOT_QUALITY_GENERATION_DELTA'] * (usg_decimal ** 1.5)
                logger.info(f"Calculated HELIO_POTENTIAL_SCORE. Mean: {final_df['HELIO_POTENTIAL_SCORE'].mean():.4f}")

                # 5. SHOT_QUALITY_GENERATION_DELTA_X_USG (Interaction Term)
                final_df['SHOT_QUALITY_GENERATION_DELTA_X_USG'] = final_df['SHOT_QUALITY_GENERATION_DELTA'] * usg_decimal
                logger.info(f"Calculated SHOT_QUALITY_GENERATION_DELTA_X_USG. Mean: {final_df['SHOT_QUALITY_GENERATION_DELTA_X_USG'].mean():.4f}")

        else:
            logger.warning(f"SHOT_QUALITY_GENERATION_DELTA file not found at {sq_path}. Using 0.0 default.")
            if 'SHOT_QUALITY_GENERATION_DELTA' not in final_df.columns:
                final_df['SHOT_QUALITY_GENERATION_DELTA'] = 0.0
            if 'HELIO_POTENTIAL_SCORE' not in final_df.columns:
                final_df['HELIO_POTENTIAL_SCORE'] = 0.0
            if 'SHOT_QUALITY_GENERATION_DELTA_X_USG' not in final_df.columns:
                final_df['SHOT_QUALITY_GENERATION_DELTA_X_USG'] = 0.0

        # 4. Calculate Dependence Scores (Projected)
        # This will now use the new logic in calculate_dependence_score.py
        logger.info("Calculating Projected Dependence Scores...")
        final_df = calculate_dependence_scores_batch(final_df)
        
        # INSERT THIS CALL
        final_df = self._calculate_fragility_score(final_df)
        
        # PHASE 5 REFACTOR: Validate the final dataset against the Pydantic schema
        final_df = validate_with_pydantic(final_df)
        
        # For now, just save what we have
        output_path = self.results_dir / "predictive_dataset_with_friction.csv"
        final_df.to_csv(output_path, index=False)
        logger.info(f"Successfully saved Predictive Dataset with Friction to {output_path}")
        logger.info(f"Total Rows: {len(final_df)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature Engineering for Stylistic Stress Test")
    parser.add_argument('--workers', type=int, default=1, help='Number of parallel workers (default: 1)')
    parser.add_argument('--seasons', nargs='+', help='Seasons to process (e.g., 2023-24)')
    args = parser.parse_args()

    engine = StressVectorEngine()
    
    # Seasons to process
    if args.seasons:
        seasons_to_process = args.seasons
    else:
        # Default seasons
        seasons_to_process = [
            '2015-16', '2016-17', '2017-18', '2018-19',
            '2019-20', '2020-21', '2021-22', '2022-23', '2023-24', '2024-25'
        ]
        
    engine.run(seasons=seasons_to_process, max_workers=args.workers)
