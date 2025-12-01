
import pandas as pd
import numpy as np
import os
import glob
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.nba_data.api.nba_stats_client import NBAStatsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_minutes_data(season):
    """
    Fetch minutes played for all players in RS and Playoffs.
    Returns dict: {(player_id, season_type): minutes}
    """
    client = NBAStatsClient()
    minutes_map = {}
    
    try:
        # Regular Season
        rs_data = client.get_league_player_base_stats(season=season, season_type="Regular Season")
        if rs_data and 'resultSets' in rs_data:
            headers = rs_data['resultSets'][0]['headers']
            rows = rs_data['resultSets'][0]['rowSet']
            df = pd.DataFrame(rows, columns=headers)
            for _, row in df.iterrows():
                minutes_map[(row['PLAYER_ID'], 'Regular Season')] = row['MIN']
                
        # Playoffs
        po_data = client.get_league_player_base_stats(season=season, season_type="Playoffs")
        if po_data and 'resultSets' in po_data:
            headers = po_data['resultSets'][0]['headers']
            rows = po_data['resultSets'][0]['rowSet']
            df = pd.DataFrame(rows, columns=headers)
            for _, row in df.iterrows():
                minutes_map[(row['PLAYER_ID'], 'Playoffs')] = row['MIN']
                
    except Exception as e:
        logger.error(f"Failed to fetch minutes data: {e}")
        
    return minutes_map


def categorize_zone(zone_basic):
    """Map detailed zones to simplified analysis zones."""
    if 'Restricted Area' in zone_basic: return 'Restricted Area'
    if 'In The Paint' in zone_basic: return 'Paint (Non-RA)'
    if 'Mid-Range' in zone_basic: return 'Mid-Range'
    if 'Corner 3' in zone_basic: return 'Corner 3'
    if 'Above the Break' in zone_basic: return 'Above Break 3'
    return 'Other'

def load_shot_quality_data(season):
    """
    Load shot quality data and calculate Tight Shot Percentage.
    Returns a dict: {(player_id, season_type): tight_shot_pct}
    """
    sq_path = Path(f"data/shot_quality/shot_quality_{season}.csv")
    if not sq_path.exists():
        logger.warning(f"Shot quality data not found for {season}")
        return {}
        
    df = pd.read_csv(sq_path)
    
    # Calculate totals per player per season_type
    # SHOT_QUALITY column has values like 'VeryTight', 'Tight', etc.
    # We want (VeryTight + Tight) / Total
    
    quality_map = {}
    
    players = df['PLAYER_ID'].unique()
    for pid in players:
        p_df = df[df['PLAYER_ID'] == pid]
        
        for stype in ['Regular Season', 'Playoffs']:
            subset = p_df[p_df['SEASON_TYPE'] == stype]
            if subset.empty:
                continue
                
            total_shots = subset['FGA'].sum()
            if total_shots == 0:
                continue
                
            tight_shots = subset[subset['SHOT_QUALITY'].isin(['VeryTight', 'Tight'])]['FGA'].sum()
            
            tight_pct = tight_shots / total_shots
            quality_map[(pid, stype)] = tight_pct
            
    return quality_map

def calculate_league_averages(df_season):
    """
    Calculate league average shooting stats per zone for Regular Season.
    Returns a dict: {zone: {'makes': int, 'attempts': int, 'pct': float}}
    """
    # Filter for Regular Season
    rs_df = df_season[df_season['SEASON_TYPE'] == 'Regular Season'].copy()
    
    # Group by SimpleZone
    # Note: SimpleZone must be added before calling this, or we add it here.
    # We'll assume SimpleZone column exists or add it.
    if 'SimpleZone' not in rs_df.columns:
        rs_df['SimpleZone'] = rs_df['SHOT_ZONE_BASIC'].apply(categorize_zone)
        
    stats = rs_df.groupby('SimpleZone').agg({
        'SHOT_MADE_FLAG': ['sum', 'count']
    })
    
    # Flatten columns
    stats.columns = ['makes', 'attempts']
    stats['pct'] = stats['makes'] / stats['attempts']
    
    return stats.to_dict('index')

def calculate_plasticity_metrics(df_season):
    """
    Calculate plasticity metrics for all players in a season dataframe.
    """
    results = []
    
    # Load Shot Quality Context
    season_str = df_season['SEASON'].iloc[0]
    quality_map = load_shot_quality_data(season_str)
    
    # Load Minutes Context
    minutes_map = fetch_minutes_data(season_str)
    logger.info(f"Loaded minutes for {len(minutes_map)} player-season-types.")
    
    # Debug first entry
    if minutes_map:
        first_key = list(minutes_map.keys())[0]
        logger.info(f"Sample Minutes Key: {first_key}, Value: {minutes_map[first_key]}")

    
    # Add simplified zone
    df_season['SimpleZone'] = df_season['SHOT_ZONE_BASIC'].apply(categorize_zone)
    
    # Calculate League Averages (Bayesian Prior)
    league_stats = calculate_league_averages(df_season)
    
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
        
        # --- Metric 2: Counter-Punch Efficiency (Bayesian Adjusted) ---
        # Did they make shots in the zones they moved TO?
        
        # Identify zones where volume INCREASED
        volume_delta = po_vec - rs_vec
        increased_zones = volume_delta[volume_delta > 0].index.tolist()
        
        if not increased_zones:
            counter_punch_efficiency = 0 
            bayes_counter_punch = 0
        else:
            # We need to calculate the aggregate makes/attempts for the player in these zones
            # to do the Bayesian update properly.
            
            # Filter shots in increased zones
            p_rs_zone_shots = rs_shots[rs_shots['SimpleZone'].isin(increased_zones)]
            p_po_zone_shots = po_shots[po_shots['SimpleZone'].isin(increased_zones)]
            
            # Raw Stats
            rs_makes = p_rs_zone_shots['SHOT_MADE_FLAG'].sum()
            rs_attempts = len(p_rs_zone_shots)
            rs_pct = rs_makes / rs_attempts if rs_attempts > 0 else 0.0
            
            po_makes = p_po_zone_shots['SHOT_MADE_FLAG'].sum()
            po_attempts = len(p_po_zone_shots)
            po_pct = po_makes / po_attempts if po_attempts > 0 else 0.0
            
            # Bayesian Baseline Calculation
            # Expected = (PlayerMakes + K * LeagueAvgPct) / (PlayerAttempts + K)
            # We need the League Avg Pct for these specific zones (Weighted average)
            
            # Calculate League Avg for this specific mix of zones
            l_makes = 0
            l_attempts = 0
            for z in increased_zones:
                stats = league_stats.get(z, {'makes': 0, 'attempts': 0})
                l_makes += stats['makes']
                l_attempts += stats['attempts']
            
            l_avg_pct = l_makes / l_attempts if l_attempts > 0 else 0.40 # Default to 40% if missing
            
            # K factor (Damping) - 25 shots is a reasonable prior strength
            K = 25
            
            expected_baseline = (rs_makes + (K * l_avg_pct)) / (rs_attempts + K)
            
            # Metrics
            counter_punch_efficiency = po_pct - rs_pct
            bayes_counter_punch = po_pct - expected_baseline

            # --- Metric 2c: Production Resilience (Per Minute) ---
            # Did they produce MORE makes per minute in the new zones?
            rs_min = minutes_map.get((pid, 'Regular Season'), 0.0)
            po_min = minutes_map.get((pid, 'Playoffs'), 0.0)
            
            # Debug log for first player to diagnose 0.0 issue
            if pid == players[0]:
                logger.info(f"Debug Minutes for {pid} ({player_name}): RS={rs_min}, PO={po_min}")
            
            # Thresholds for MPG (Minutes Per Game)
            if rs_min > 10 and po_min > 5:
                rs_games_count = rs_shots['GAME_ID'].nunique()
                po_games_count = po_shots['GAME_ID'].nunique()
                
                if rs_games_count > 0 and po_games_count > 0:
                    rs_makes_pg = rs_makes / rs_games_count
                    po_makes_pg = po_makes / po_games_count
                    
                    rs_mpm = rs_makes_pg / rs_min
                    po_mpm = po_makes_pg / po_min
                    
                    # Per 36 Adjustment
                    production_resilience = (po_mpm - rs_mpm) * 36
                else:
                    production_resilience = 0.0
            else:
                production_resilience = 0.0

        # --- Metric 2b: Shot Quality Adjustment ---
        rs_tight_pct = quality_map.get((pid, 'Regular Season'), 0.0)
        po_tight_pct = quality_map.get((pid, 'Playoffs'), 0.0)
        sq_delta = po_tight_pct - rs_tight_pct
        adj_factor = 0.75 
        
        # Apply to Bayesian score as well
        adj_counter_punch = bayes_counter_punch + (sq_delta * adj_factor)

        # --- Metric 3: Compression Score ---
        rs_std = rs_shots['SHOT_DISTANCE'].std()
        po_std = po_shots['SHOT_DISTANCE'].std()
        
        if pd.isna(rs_std) or pd.isna(po_std):
            compression_score = 0
        else:
            compression_score = po_std - rs_std
            
        # --- Metric 4: Rim Deterrence ---
        rim_delta = volume_delta.get('Restricted Area', 0)
        
        results.append({
            'PLAYER_ID': pid,
            'PLAYER_NAME': player_name,
            'SEASON': season,
            'ZONE_DISPLACEMENT': round(displacement_score, 4),
            'RAW_COUNTER_PUNCH': round(counter_punch_efficiency, 4),
            'COUNTER_PUNCH_EFF': round(bayes_counter_punch, 4), # Replaces old metric as primary
            'ADJ_COUNTER_PUNCH': round(adj_counter_punch, 4),
            'PRODUCTION_RESILIENCE': round(production_resilience, 4),
            'SQ_DELTA': round(sq_delta, 4),
            'COMPRESSION_SCORE': round(compression_score, 4),
            'RIM_DETERRENCE': round(rim_delta, 4),
            'RS_SHOTS': len(rs_shots),
            'PO_SHOTS': len(po_shots)
        })
        
    return pd.DataFrame(results)
        
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

