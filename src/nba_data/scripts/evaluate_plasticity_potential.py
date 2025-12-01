
import sys
import os
import pandas as pd
import numpy as np
import logging
from pathlib import Path
import argparse

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.nba_data.api.nba_stats_client import NBAStatsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
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

def get_defensive_rankings(season):
    """
    Fetch team defensive ratings and return Top 5 (Stress) and Bottom 10 (Comfort) teams.
    Returns: (set(stress_ids), set(comfort_ids), id_to_name_map)
    """
    client = NBAStatsClient()
    logger.info(f"Fetching defensive rankings for {season}...")
    
    data = client.get_league_team_stats(season=season, measure_type="Advanced")
    
    if not data or 'resultSets' not in data:
        logger.error("Failed to fetch team stats")
        return set(), set(), {}
        
    headers = data['resultSets'][0]['headers']
    rows = data['resultSets'][0]['rowSet']
    df = pd.DataFrame(rows, columns=headers)
    
    # Sort by DEF_RATING (Ascending = Better Defense)
    df = df.sort_values('DEF_RATING', ascending=True)
    
    # Top 5 Defenses (Lowest Rating)
    stress_teams = df.head(5)
    # Bottom 10 Defenses (Highest Rating)
    comfort_teams = df.tail(10)
    
    logger.info(f"Top 5 Defenses (Stress): {stress_teams['TEAM_NAME'].tolist()}")
    logger.info(f"Bottom 10 Defenses (Comfort): {comfort_teams['TEAM_NAME'].tolist()}")
    
    return (
        set(stress_teams['TEAM_ID'].values),
        set(comfort_teams['TEAM_ID'].values),
        dict(zip(df['TEAM_ID'], df['TEAM_NAME']))
    )

def build_abbrev_map(df_shots):
    """
    Build a map of Team Name/ID to Abbreviation using the shot chart data.
    """
    # TEAM_ID corresponds to TEAM_NAME. 
    # HTM/VTM correspond to abbreviations.
    # We need to link ID -> Abbrev.
    
    # Filter where TEAM_NAME matches HTM (Home games) - Wait, HTM is Abbrev, TEAM_NAME is Full.
    # We can't directly match "Atlanta Hawks" to "ATL" without a common key or logic.
    # BUT, we know for a given game (GAME_ID), there are two teams.
    # The shot chart has TEAM_ID.
    # If we look at a game, we can deduce the abbreviation.
    
    # Actually, there is a simpler way:
    # In the shot chart, for a specific TEAM_ID, look at games where they are Home (vs someone).
    # This is tricky because we don't know if they are Home or Away from the row alone easily
    # without checking HTM/VTM columns.
    # However, for every row: 
    # IF (HTM == VTM) -> Data error (impossible).
    # The columns are HTM and VTM. 
    # One of them is the player's team.
    
    # Let's blindly try to map:
    # For each TEAM_ID, find the abbreviation that appears in HTM or VTM most frequently? No.
    
    # Better approach:
    # We have TEAM_ID and TEAM_NAME from the API.
    # We can construct a static map for the 30 active teams to be safe.
    # Using a static map avoids logic errors with dynamic inference.
    
    # NBA Team ID to Abbrev Map (Standard IDs)
    # IDs from 1610612737 to 1610612766
    static_map = {
        1610612737: 'ATL', 1610612738: 'BOS', 1610612739: 'CLE', 1610612740: 'NOP',
        1610612741: 'CHI', 1610612742: 'DAL', 1610612743: 'DEN', 1610612744: 'GSW',
        1610612745: 'HOU', 1610612746: 'LAC', 1610612747: 'LAL', 1610612748: 'MIA',
        1610612749: 'MIL', 1610612750: 'MIN', 1610612751: 'BKN', 1610612752: 'NYK',
        1610612753: 'ORL', 1610612754: 'IND', 1610612755: 'PHI', 1610612756: 'PHX',
        1610612757: 'POR', 1610612758: 'SAC', 1610612759: 'SAS', 1610612760: 'OKC',
        1610612761: 'TOR', 1610612762: 'UTA', 1610612763: 'MEM', 1610612764: 'WAS',
        1610612765: 'DET', 1610612766: 'CHA'
    }
    return static_map

def determine_opponent(row, id_to_abbrev):
    """
    Determine the opponent team ID (or Abbrev) for a shot row.
    """
    player_team_id = row['TEAM_ID']
    player_team_abbrev = id_to_abbrev.get(player_team_id)
    
    if not player_team_abbrev:
        return None
        
    htm = row['HTM']
    vtm = row['VTM']
    
    if htm == player_team_abbrev:
        return vtm # Opponent is Visiting Team
    elif vtm == player_team_abbrev:
        return htm # Opponent is Home Team
    else:
        # Fallback/Edge case: Player might have been traded or abbreviation mismatch
        # Assume opponent is the one that isn't the mapped abbreviation
        # But if neither match, we can't know.
        return None

def calculate_stress_plasticity(df, stress_abbrevs, comfort_abbrevs, id_to_abbrev):
    """
    Calculate plasticity metrics comparing Comfort (Baseline) vs Stress (Test).
    """
    # 1. Identify Opponent for every shot
    # We'll create a new column 'OPP_ABBREV'
    
    # Optimization: Vectorize if possible, but apply is safer for logic
    # Using a map for team_id -> abbrev
    
    # Create Opponent Column
    # If HTM == TeamAbbrev, Opp = VTM, else HTM
    df['TeamAbbrev'] = df['TEAM_ID'].map(id_to_abbrev)
    
    # Vectorized condition
    df['OPP_ABBREV'] = np.where(
        df['HTM'] == df['TeamAbbrev'], 
        df['VTM'], 
        df['HTM']
    )
    
    # Handle cases where TeamAbbrev was NaN or neither matched (should be rare)
    # Filter out unknown opponents
    df = df.dropna(subset=['OPP_ABBREV'])
    
    # 2. Split into Contexts
    comfort_shots = df[df['OPP_ABBREV'].isin(comfort_abbrevs)]
    stress_shots = df[df['OPP_ABBREV'].isin(stress_abbrevs)]
    
    # 3. Process per player
    results = []
    players = df['PLAYER_ID'].unique()
    
    for pid in players:
        p_comfort = comfort_shots[comfort_shots['PLAYER_ID'] == pid].copy()
        p_stress = stress_shots[stress_shots['PLAYER_ID'] == pid].copy()
        
        # Minimum sample size
        # Need significant shots to stabilize the signal
        if len(p_comfort) < 30 or len(p_stress) < 30:
            continue
            
        player_name = p_comfort['PLAYER_NAME'].iloc[0]
        
        # Add simplified zone
        p_comfort['SimpleZone'] = p_comfort['SHOT_ZONE_BASIC'].apply(categorize_zone)
        p_stress['SimpleZone'] = p_stress['SHOT_ZONE_BASIC'].apply(categorize_zone)
        
        # Filter Other
        p_comfort = p_comfort[p_comfort['SimpleZone'] != 'Other']
        p_stress = p_stress[p_stress['SimpleZone'] != 'Other']
        
        # --- Metric Calculation (Reused Logic) ---
        
        # Distributions
        c_dist = p_comfort['SimpleZone'].value_counts(normalize=True)
        s_dist = p_stress['SimpleZone'].value_counts(normalize=True)
        
        all_zones = ['Restricted Area', 'Paint (Non-RA)', 'Mid-Range', 'Corner 3', 'Above Break 3']
        c_vec = c_dist.reindex(all_zones, fill_value=0)
        s_vec = s_dist.reindex(all_zones, fill_value=0)
        
        # Metric 1: Zone Displacement
        displacement_score = (c_vec - s_vec).abs().sum() / 2
        
        # Metric 2: Stress Counter-Punch Efficiency
        # Efficiency in zones where volume INCREASED under stress
        volume_delta = s_vec - c_vec
        increased_zones = volume_delta[volume_delta > 0].index.tolist()
        
        if not increased_zones:
            cp_eff = 0.0
        else:
            c_makes = p_comfort[p_comfort['SimpleZone'].isin(increased_zones)]['SHOT_MADE_FLAG'].mean()
            s_makes = p_stress[p_stress['SimpleZone'].isin(increased_zones)]['SHOT_MADE_FLAG'].mean()
            
            if pd.isna(c_makes): c_makes = 0.0
            if pd.isna(s_makes): s_makes = 0.0
            
            cp_eff = s_makes - c_makes
            
        results.append({
            'PLAYER_ID': pid,
            'PLAYER_NAME': player_name,
            'RS_STRESS_DISPLACEMENT': round(displacement_score, 4),
            'RS_STRESS_COUNTER_PUNCH': round(cp_eff, 4),
            'COMFORT_SHOTS': len(p_comfort),
            'STRESS_SHOTS': len(p_stress)
        })
        
    return pd.DataFrame(results)

def main():
    parser = argparse.ArgumentParser(description='Evaluate Plasticity Potential (Stress Test)')
    parser.add_argument('--season', type=str, default='2023-24', help='Season to analyze')
    args = parser.parse_args()
    
    season = args.season
    shot_file = Path(f"data/shot_charts_{season}.csv")
    
    if not shot_file.exists():
        logger.error(f"Shot chart file not found: {shot_file}")
        logger.info("Please run collect_shot_charts.py first.")
        return

    # 1. Get Defensive Rankings
    stress_ids, comfort_ids, id_to_name = get_defensive_rankings(season)
    if not stress_ids:
        return
        
    # 2. Build Abbrev Maps
    id_to_abbrev = build_abbrev_map(None) # Using static map
    
    # Convert ID sets to Abbrev sets for filtering
    stress_abbrevs = {id_to_abbrev[tid] for tid in stress_ids if tid in id_to_abbrev}
    comfort_abbrevs = {id_to_abbrev[tid] for tid in comfort_ids if tid in id_to_abbrev}
    
    logger.info(f"Stress Team Abbrevs: {stress_abbrevs}")
    logger.info(f"Comfort Team Abbrevs: {comfort_abbrevs}")
    
    # 3. Load Shots
    logger.info(f"Loading shots from {shot_file}...")
    df = pd.read_csv(shot_file)
    
    # Filter for Regular Season only (we are simulating playoffs using RS data)
    df = df[df['SEASON_TYPE'] == 'Regular Season'].copy()
    logger.info(f"Loaded {len(df)} regular season shots.")
    
    # 4. Calculate Metrics
    logger.info("Calculating stress plasticity metrics...")
    results_df = calculate_stress_plasticity(df, stress_abbrevs, comfort_abbrevs, id_to_abbrev)
    
    if results_df.empty:
        logger.warning("No players met the sample size criteria.")
        return
        
    results_df['SEASON'] = season
    
    # 5. Validate against actual Playoff Resilience
    res_path = Path("results/plasticity_scores.csv") 
    # Note: We want to correlate with the MECHANISTIC score (Counter Punch), not just the raw outcome.
    # But the Plan says correlate with "Playoff Resilience". Let's try both if available.
    
    if res_path.exists():
        logger.info("Correlating with actual Playoff Plasticity...")
        po_df = pd.read_csv(res_path)
        
        # Merge
        merged = pd.merge(
            results_df,
            po_df[['PLAYER_ID', 'SEASON', 'COUNTER_PUNCH_EFF', 'ZONE_DISPLACEMENT']],
            on=['PLAYER_ID', 'SEASON'],
            suffixes=('_STRESS', '_PLAYOFF')
        )
        
        if not merged.empty:
            corr_cp = merged['RS_STRESS_COUNTER_PUNCH'].corr(merged['COUNTER_PUNCH_EFF'])
            logger.info(f"🎯 CORRELATION (Stress CP vs Playoff CP): {corr_cp:.4f}")
            
            # Save validation results
            merged.to_csv(f"results/rs_stress_test_metrics.csv", index=False)
            logger.info(f"Saved detailed metrics to results/rs_stress_test_metrics.csv")
        else:
            logger.warning("No overlapping players found between Stress Test and Playoff results.")
    else:
        logger.warning("results/plasticity_scores.csv not found. Cannot validate yet.")
        # Save just the stress scores
        results_df.to_csv(f"results/rs_stress_test_metrics.csv", index=False)

if __name__ == "__main__":
    main()

