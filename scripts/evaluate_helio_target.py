
import pandas as pd
import numpy as np
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def calculate_helio_index_test():
    # Load the dataset
    file_path = Path("results/predictive_dataset_with_friction.csv")
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return

    df = pd.read_csv(file_path)
    
    # Filter for last 10 years (approx 2014-2024)
    # Seasons are likely strings like "2015-16"
    # Let's see unique seasons
    seasons = sorted(df['SEASON'].unique())
    logger.info(f"Seasons available: {seasons}")
    
    # Filter for relevant seasons if needed
    # Filter out garbage time players (Sample Size Trap)
    # The dataset has 'CLUTCH_MIN_TOTAL' but maybe not total minutes?
    # It has 'MIN_vs_top10', 'MIN_vs_elite' etc.
    # Let's look at the columns again from the csv read.
    # 'CLUTCH_MPG', 'CLUTCH_GP'. 
    # 'RS_GP', 'RS_TOTAL_VOLUME'. 'RS_TOTAL_VOLUME' usually means FGA?
    # 'TOTAL_PROJECTED_FGA'.
    
    # We need a minutes filter. 
    # The file has 'MIN_vs_weak' etc which implies there is a MIN column somewhere?
    # Let's check the columns printed in the first read if I can see them.
    # I saw 'CLUTCH_MIN_TOTAL'. 
    # Wait, 'RS_GP' is there.
    # Let's use RS_GP > 20 as a basic filter.
    if 'RS_GP' in df.columns:
        df = df[df['RS_GP'] >= 20]
    elif 'GP' in df.columns:
        df = df[df['GP'] >= 20]
    
    # Also filter out rows with 'PLAYER_NAME' == '0'
    df = df[df['PLAYER_NAME'] != '0']
    
    # 1. Calculate Replacement Level TS per Season
    # We'll define replacement level as the median or mean TS% of the league that season
    # Or maybe 10th percentile? 
    # The plan says "TS_PCT - 0.54" as an example but says "Ensure REPLACEMENT_LEVEL_TS is dynamic".
    # Usually replacement level is below average. Let's use League Average for now to punish inefficiency strictly, 
    # or maybe 0.9 * League Average? 
    # The plan says "Captures Efficiency Value-Add. (If inefficient, score becomes negative)."
    # If we use Average, then average players get 0. That seems intended ("Role Player Zero").
    
    seasonal_stats = df.groupby('SEASON')['TS_PCT'].mean().reset_index()
    seasonal_stats.rename(columns={'TS_PCT': 'LEAGUE_AVG_TS'}, inplace=True)
    
    df = df.merge(seasonal_stats, on='SEASON', how='left')
    
    # Calculate Helio Index
    # HELIO_INDEX = (USG_PCT * 100) * (TS_PCT - LEAGUE_AVG_TS) * CREATION_VOLUME_RATIO
    
    # Note: USG_PCT in the file might be 0.xx or xx.x.
    # In the head output: "0.114" -> 11.4%. 
    # So USG_PCT * 100 makes sense.
    
    # Creation Volume Ratio might be missing (NaN). Fill with 0.
    df['CREATION_VOLUME_RATIO'] = df['CREATION_VOLUME_RATIO'].fillna(0)
    
    # Calculate components
    df['USAGE_COMPONENT'] = df['USG_PCT'] * 100
    df['EFFICIENCY_COMPONENT'] = df['TS_PCT'] - df['LEAGUE_AVG_TS']
    # If we want to use a specific replacement level (e.g. -4% rTS), we could do LEAGUE_AVG_TS - 0.04
    # But let's stick to "Value Over Average" for now as it's a cleaner signal for "Star"
    # Stars usually have above average efficiency. 
    # Wait, the plan says "TS_PCT - 0.54". In 2024, avg TS is ~58%. 
    # So 54% is -4%. 
    # Let's use Replacement = League Avg - 0.04
    
    df['REPLACEMENT_LEVEL_TS'] = df['LEAGUE_AVG_TS'] - 0.04
    df['EFFICIENCY_VAL_ADD'] = df['TS_PCT'] - df['REPLACEMENT_LEVEL_TS']
    
    df['HELIO_INDEX'] = (
        df['USAGE_COMPONENT'] * 
        df['EFFICIENCY_VAL_ADD'] * 
        df['CREATION_VOLUME_RATIO']
    )
    
    # ALSO calculate the PROPOSED REFINED METRIC from the thought process
    # REAL_HELIO_LOAD = (USG_PCT + (ASSIST_PCT / factor)) -> We don't have ASSIST_PCT easily available here?
    # Let's check columns.
    
    # If we don't have AST_PCT, we can't fully implement the refined one. 
    # But let's check the columns in the dataframe again.
    # The head output didn't show AST_PCT.
    # It has 'PLAYER_NAME', 'EFG_PCT_0_DRIBBLE', ... 'USG_PCT', 'TS_PCT' ...
    
    # Let's just output the Standard Helio Index results first.
    
    # Group by Player and find their Peak Helio Index
    player_peaks = df.groupby(['PLAYER_ID', 'PLAYER_NAME'])['HELIO_INDEX'].max().sort_values(ascending=False).reset_index()
    
    # Add the season they peaked
    # merge back
    peak_seasons = df.loc[df.groupby(['PLAYER_ID', 'PLAYER_NAME'])['HELIO_INDEX'].idxmax()]
    peak_seasons = peak_seasons[['PLAYER_NAME', 'SEASON', 'HELIO_INDEX', 'USG_PCT', 'TS_PCT', 'LEAGUE_AVG_TS', 'CREATION_VOLUME_RATIO']]
    
    peak_seasons = peak_seasons.sort_values('HELIO_INDEX', ascending=False)
    
    print("\n=== TOP 50 PLAYERS BY PEAK HELIO INDEX (Last 10 Years) ===")
    print(peak_seasons.head(50).to_string(index=False))
    
    # Also Check specific players mentioned in the critique
    print("\n=== CRITIQUE CHECK ===")
    check_players = ["Rudy Gobert", "Klay Thompson", "Tyrese Haliburton", "Steve Nash", "James Harden", "Stephen Curry", "Nikola Jokic", "Russell Westbrook", "DeMar DeRozan"]
    
    # Filter for these players
    # We need to handle exact name matches
    # Add Nikola Jokic specifically if not in top 50
    check_players = ["Rudy Gobert", "Klay Thompson", "Tyrese Haliburton", "Steve Nash", "James Harden", "Stephen Curry", "Nikola Jokic", "Russell Westbrook", "DeMar DeRozan"]
    
    # Filter for these players
    mask = peak_seasons['PLAYER_NAME'].isin(check_players)
    print(peak_seasons[mask].to_string(index=False))
    
    # Check Jokic Rank (Handle accent if needed)
    jokic_mask = peak_seasons['PLAYER_NAME'].str.contains("Jokic|Jokić", case=False, regex=True)
    if jokic_mask.any():
        jokic_row = peak_seasons[jokic_mask].iloc[0]
        # Find rank in the sorted dataframe
        jokic_name = jokic_row['PLAYER_NAME']
        # The index in peak_seasons is not the rank because we sorted it but didn't reset index properly or use range
        # Let's reset index to get rank
        peak_seasons_ranked = peak_seasons.reset_index(drop=True)
        jokic_rank = peak_seasons_ranked[peak_seasons_ranked['PLAYER_NAME'] == jokic_name].index[0]
        
        print(f"\nNikola Jokic Rank: #{jokic_rank + 1}")
        print(f"Nikola Jokic Data:\n{jokic_row}")
    else:
        print("\nNikola Jokic not found in dataset")

    # Save to CSV for user
    peak_seasons.head(100).to_csv("results/helio_index_simulation.csv", index=False)
    print("\nSaved top 100 to results/helio_index_simulation.csv")

if __name__ == "__main__":
    calculate_helio_index_test()

