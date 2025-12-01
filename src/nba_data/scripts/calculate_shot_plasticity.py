
import pandas as pd
import numpy as np
import os
import glob
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def categorize_zone(zone_basic):
    """Map detailed zones to simplified analysis zones."""
    if 'Restricted Area' in zone_basic: return 'Restricted Area'
    if 'In The Paint' in zone_basic: return 'Paint (Non-RA)'
    if 'Mid-Range' in zone_basic: return 'Mid-Range'
    if 'Corner 3' in zone_basic: return 'Corner 3'
    if 'Above the Break' in zone_basic: return 'Above Break 3'
    return 'Other'

def calculate_plasticity_metrics(df_season):
    """
    Calculate plasticity metrics for all players in a season dataframe.
    """
    results = []
    
    # Add simplified zone
    df_season['SimpleZone'] = df_season['SHOT_ZONE_BASIC'].apply(categorize_zone)
    
    # Filter out 'Other' (Backcourt shots etc usually noise)
    df_season = df_season[df_season['SimpleZone'] != 'Other']
    
    players = df_season['PLAYER_ID'].unique()
    
    for pid in players:
        player_shots = df_season[df_season['PLAYER_ID'] == pid]
        player_name = player_shots['PLAYER_NAME'].iloc[0] if 'PLAYER_NAME' in player_shots.columns else f"Player {pid}"
        season = player_shots['SEASON'].iloc[0]
        
        rs_shots = player_shots[player_shots['SEASON_TYPE'] == 'Regular Season']
        po_shots = player_shots[player_shots['SEASON_TYPE'] == 'Playoffs']
        
        # Minimum sample size filter
        if len(rs_shots) < 50 or len(po_shots) < 20:
            continue
            
        # --- Metric 1: Zone Displacement (Hellinger-ish) ---
        # Calculate zone frequencies
        rs_dist = rs_shots['SimpleZone'].value_counts(normalize=True)
        po_dist = po_shots['SimpleZone'].value_counts(normalize=True)
        
        # Align indexes
        all_zones = ['Restricted Area', 'Paint (Non-RA)', 'Mid-Range', 'Corner 3', 'Above Break 3']
        rs_vec = rs_dist.reindex(all_zones, fill_value=0)
        po_vec = po_dist.reindex(all_zones, fill_value=0)
        
        # Simple Displacement: Sum of absolute differences / 2 (scales 0 to 1)
        # 0 = Identical distribution, 1 = Completely different
        displacement_score = (rs_vec - po_vec).abs().sum() / 2
        
        # --- Metric 2: Counter-Punch Efficiency ---
        # Did they make shots in the zones they moved TO?
        
        # Identify zones where volume INCREASED
        volume_delta = po_vec - rs_vec
        increased_zones = volume_delta[volume_delta > 0].index.tolist()
        
        if not increased_zones:
            counter_punch_efficiency = 0 # Should rarely happen unless distribution is identical
        else:
            # Calculate efficiency in those zones
            rs_makes = rs_shots[rs_shots['SimpleZone'].isin(increased_zones)]['SHOT_MADE_FLAG'].mean()
            po_makes = po_shots[po_shots['SimpleZone'].isin(increased_zones)]['SHOT_MADE_FLAG'].mean()
            
            # Handle NaN (if they never took shots in that zone in RS)
            if pd.isna(rs_makes): rs_makes = 0.0
            if pd.isna(po_makes): po_makes = 0.0
            
            counter_punch_efficiency = po_makes - rs_makes

        # --- Metric 3: Compression Score ---
        # Did their shot diet get squeezed?
        # Measure: Change in standard deviation of Shot Distance
        # Negative = Compressed (less variety), Positive = Expanded
        
        rs_std = rs_shots['SHOT_DISTANCE'].std()
        po_std = po_shots['SHOT_DISTANCE'].std()
        
        if pd.isna(rs_std) or pd.isna(po_std):
            compression_score = 0
        else:
            compression_score = po_std - rs_std

        # --- Metric 4: Rim Deterrence ---
        # Specifically measuring how much they were forced away from the rim
        rim_delta = volume_delta.get('Restricted Area', 0)
        
        results.append({
            'PLAYER_ID': pid,
            'PLAYER_NAME': player_name,
            'SEASON': season,
            'ZONE_DISPLACEMENT': round(displacement_score, 4),
            'COUNTER_PUNCH_EFF': round(counter_punch_efficiency, 4),
            'COMPRESSION_SCORE': round(compression_score, 4),
            'RIM_DETERRENCE': round(rim_delta, 4),
            'RS_SHOTS': len(rs_shots),
            'PO_SHOTS': len(po_shots)
        })
        
    return pd.DataFrame(results)

def main():
    data_dir = Path("data")
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    # Find all shot chart files
    files = list(data_dir.glob("shot_charts_*.csv"))
    if not files:
        logger.error("No shot chart files found in data/")
        return

    all_results = []
    
    for f in files:
        logger.info(f"Processing {f.name}...")
        try:
            df = pd.read_csv(f)
            if df.empty:
                continue
                
            season_results = calculate_plasticity_metrics(df)
            all_results.append(season_results)
            logger.info(f"Processed {len(season_results)} players for {f.name}")
            
        except Exception as e:
            logger.error(f"Error processing {f.name}: {e}")
            
    if all_results:
        final_df = pd.concat(all_results, ignore_index=True)
        
        # Merge with Resilience Scores if available for context
        res_path = Path("results/resilience_scores_all.csv")
        if res_path.exists():
            res_df = pd.read_csv(res_path)
            # Merge only relevant columns
            final_df = pd.merge(
                final_df, 
                res_df[['PLAYER_ID', 'SEASON', 'RESILIENCE_SCORE']], 
                on=['PLAYER_ID', 'SEASON'],
                how='left'
            )
            
        output_path = output_dir / "plasticity_scores.csv"
        final_df.to_csv(output_path, index=False)
        logger.info(f"✅ Saved plasticity metrics for {len(final_df)} player-seasons to {output_path}")
    else:
        logger.warning("No results generated.")

if __name__ == "__main__":
    main()

