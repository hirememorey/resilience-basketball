
import pandas as pd
import numpy as np
from pathlib import Path

def debug_jokic():
    file_path = Path("results/predictive_dataset_with_friction.csv")
    df = pd.read_csv(file_path)
    
    # Filter for Jokic
    # Name might be "Nikola Jokić" or "Nikola Jokic"
    jokic_df = df[df['PLAYER_NAME'].str.contains("Jokic|Jokić")]
    
    # Calculate components
    # Calculate seasonal averages for replacement level
    seasonal_stats = df.groupby('SEASON')['TS_PCT'].mean().reset_index()
    seasonal_stats.rename(columns={'TS_PCT': 'LEAGUE_AVG_TS'}, inplace=True)
    jokic_df = jokic_df.merge(seasonal_stats, on='SEASON', how='left')
    
    jokic_df['REPLACEMENT_LEVEL_TS'] = jokic_df['LEAGUE_AVG_TS'] - 0.04
    
    jokic_df['CREATION_VOLUME_RATIO'] = jokic_df['CREATION_VOLUME_RATIO'].fillna(0)
    
    jokic_df['HELIO_INDEX'] = (
        (jokic_df['USG_PCT'] * 100) * 
        (jokic_df['TS_PCT'] - jokic_df['REPLACEMENT_LEVEL_TS']) * 
        jokic_df['CREATION_VOLUME_RATIO']
    )
    
    cols = ['PLAYER_NAME', 'SEASON', 'HELIO_INDEX', 'USG_PCT', 'TS_PCT', 'CREATION_VOLUME_RATIO', 'FGA_0_DRIBBLE', 'FGA_3_DRIBBLE', 'FGA_7_DRIBBLE']
    print(jokic_df[cols].sort_values('SEASON').to_string(index=False))

if __name__ == "__main__":
    debug_jokic()

