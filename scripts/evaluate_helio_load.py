
import pandas as pd
import numpy as np
import logging
from pathlib import Path
import glob

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def evaluate_helio_load_target():
    """
    Simulates the proposed "Helio-Load" target variable to test its efficacy before implementation.
    This metric aims to fix the flaws in the original "Helio-Index" by:
    1.  Incorporating playmaking (AST_PCT) into the load calculation.
    2.  Using a possession-based efficiency metric (Offensive Rating) that accounts for turnovers.
    """
    # --- 1. Data Loading and Preparation ---
    data_path = Path("data/")
    season_files = glob.glob(str(data_path / "regular_season_*.csv"))
    
    if not season_files:
        logger.error("No regular season data files found in data/")
        return

    df_list = []
    for file in season_files:
        season_str = Path(file).stem.split('_')[-1]
        temp_df = pd.read_csv(file)
        temp_df['SEASON'] = season_str
        df_list.append(temp_df)
    
    df = pd.concat(df_list, ignore_index=True)
    logger.info(f"Loaded data for {df['SEASON'].nunique()} seasons, with {len(df)} player-season records.")

    # --- 2. Data Cleaning and Filtering ---
    # Filter for significant playing time to avoid sample size noise
    df_filtered = df[(df['GP'] >= 20) & (df['MIN'] >= 15)].copy()
    logger.info(f"Filtered down to {len(df_filtered)} significant player-seasons.")

    # --- 3. Feature Engineering ---
    # Calculate league average offensive rating per season for normalization
    seasonal_avg_off_rating = df_filtered.groupby('SEASON')['OFF_RATING'].mean().reset_index()
    seasonal_avg_off_rating.rename(columns={'OFF_RATING': 'LEAGUE_AVG_OFF_RATING'}, inplace=True)
    df_filtered = df_filtered.merge(seasonal_avg_off_rating, on='SEASON', how='left')

    # A. Offensive Load: Combines scoring and playmaking responsibility.
    # The AST_PCT_FACTOR is a tunable parameter. 0.75 is a common public starting point.
    AST_PCT_FACTOR = 0.75
    df_filtered['OFFENSIVE_LOAD'] = df_filtered['USG_PCT'] + (df_filtered['AST_PCT'] * AST_PCT_FACTOR)

    # B. Efficiency Delta: Measures points added per 100 possessions vs. league average.
    # This inherently penalizes turnovers, as they are factored into Offensive Rating.
    df_filtered['EFFICIENCY_DELTA'] = df_filtered['OFF_RATING'] - df_filtered['LEAGUE_AVG_OFF_RATING']

    # C. Helio-Load Index: The final proposed target variable.
    # It rewards players who carry a high offensive load efficiently.
    df_filtered['HELIO_LOAD_INDEX'] = df_filtered['OFFENSIVE_LOAD'] * df_filtered['EFFICIENCY_DELTA']

    # --- 4. Analysis and Ranking ---
    # Find the peak season for each player
    peak_seasons = df_filtered.loc[df_filtered.groupby('PLAYER_ID')['HELIO_LOAD_INDEX'].idxmax()]
    
    # Sort by the peak score to create the final ranking
    final_ranking = peak_seasons.sort_values('HELIO_LOAD_INDEX', ascending=False)

    # --- 5. Reporting ---
    logger.info("\n=== TOP 50 PLAYERS BY PEAK HELIO-LOAD INDEX (Last 10 Years) ===")
    display_cols = ['PLAYER_NAME', 'SEASON', 'HELIO_LOAD_INDEX', 'OFFENSIVE_LOAD', 'EFFICIENCY_DELTA', 'USG_PCT', 'AST_PCT', 'OFF_RATING']
    logger.info(final_ranking[display_cols].head(50).to_string(index=False))

    logger.info("\n=== CRITIQUE CHECK (HELIO-LOAD) ===")
    check_players = [
        "Nikola Jokic", "James Harden", "Russell Westbrook", "Stephen Curry", 
        "Luka Doncic", "Tyrese Haliburton", "DeMar DeRozan", "Rudy Gobert", "Klay Thompson"
    ]
    
    # Use contains for flexible name matching (e.g., Luka Doncic vs Dončić)
    critique_check_df = final_ranking[final_ranking['PLAYER_NAME'].str.contains('|'.join(check_players), case=False, regex=True)]
    logger.info(critique_check_df[display_cols].to_string(index=False))

    # Save results for further review
    output_path = Path("results/helio_load_simulation.csv")
    final_ranking[display_cols].to_csv(output_path, index=False)
    logger.info(f"\nSimulation results saved to {output_path}")


if __name__ == "__main__":
    evaluate_helio_load_target()

