
import pandas as pd
import time
import sys
import logging
from tabulate import tabulate
from src.nba_data.api.nba_stats_client import NBAStatsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_shot_chart_df(client, player_id, season, season_type):
    """Fetch shot chart and return as DataFrame."""
    try:
        data = client.get_player_shot_chart(player_id=player_id, season=season, season_type=season_type)
        headers = data['resultSets'][0]['headers']
        rows = data['resultSets'][0]['rowSet']
        return pd.DataFrame(rows, columns=headers)
    except Exception as e:
        logger.error(f"Error fetching {season_type} data for player {player_id}: {e}")
        return pd.DataFrame()

def analyze_plasticity(df_rs, df_po, player_name, season):
    """Analyze and print plasticity metrics."""
    if df_rs.empty or df_po.empty:
        print(f"\n⚠️  Missing data for {player_name} ({season})")
        return

    print(f"\n{'='*60}")
    print(f"🏀 {player_name.upper()} - {season}")
    print(f"{'='*60}")

    # 1. Shot Zone Distribution
    # Using 'SHOT_ZONE_BASIC'
    zones = ['Restricted Area', 'In The Paint (Non-RA)', 'Mid-Range', 'Left Corner 3', 'Right Corner 3', 'Above the Break 3', 'Backcourt']
    
    # Map zones to simpler categories
    def map_zone(zone):
        if 'Corner 3' in zone: return 'Corner 3'
        if 'Backcourt' in zone: return 'Backcourt'
        return zone

    df_rs['SimpleZone'] = df_rs['SHOT_ZONE_BASIC'].apply(map_zone)
    df_po['SimpleZone'] = df_po['SHOT_ZONE_BASIC'].apply(map_zone)
    
    # Calculate distribution
    rs_dist = df_rs['SimpleZone'].value_counts(normalize=True) * 100
    po_dist = df_po['SimpleZone'].value_counts(normalize=True) * 100
    
    # Merge for comparison
    dist_df = pd.DataFrame({
        'RS %': rs_dist,
        'PO %': po_dist
    }).fillna(0)
    
    dist_df['Delta'] = dist_df['PO %'] - dist_df['RS %']
    dist_df = dist_df.sort_values('RS %', ascending=False)

    print(f"\n📊 SHOT DIET (Distribution by Zone)")
    print(tabulate(dist_df.round(1), headers='keys', tablefmt='simple'))

    # 2. Average Shot Distance
    rs_dist_avg = df_rs['SHOT_DISTANCE'].mean()
    po_dist_avg = df_po['SHOT_DISTANCE'].mean()
    
    print(f"\n📏 SHOT DISTANCE")
    print(f"RS: {rs_dist_avg:.1f} ft  |  PO: {po_dist_avg:.1f} ft  |  Delta: {po_dist_avg - rs_dist_avg:+.1f} ft")

    # 3. Shot Efficiency by Zone (Make/Miss)
    # SHOT_MADE_FLAG is 1 for make, 0 for miss
    rs_eff = df_rs.groupby('SimpleZone')['SHOT_MADE_FLAG'].mean() * 100
    po_eff = df_po.groupby('SimpleZone')['SHOT_MADE_FLAG'].mean() * 100
    
    eff_df = pd.DataFrame({
        'RS FG%': rs_eff,
        'PO FG%': po_eff
    }).fillna(0)
    
    eff_df['Delta'] = eff_df['PO FG%'] - eff_df['RS FG%']
    # Only show zones with meaningful volume (>1% of shots) in either
    relevant_zones = dist_df[(dist_df['RS %'] > 1) | (dist_df['PO %'] > 1)].index
    eff_df = eff_df.loc[relevant_zones].sort_values('RS FG%', ascending=False)

    print(f"\n🎯 EFFICIENCY (FG% by Zone)")
    print(tabulate(eff_df.round(1), headers='keys', tablefmt='simple'))

def main():
    client = NBAStatsClient()
    
    # Archetypes to test
    targets = [
        {
            "name": "Karl-Anthony Towns (2023 - Disappointment)",
            "id": 1626157,
            "season": "2022-23"
        },
        {
            "name": "Karl-Anthony Towns (2024 - Redemption?)",
            "id": 1626157,
            "season": "2023-24"
        },
        {
            "name": "Ben Simmons (The Collapse)",
            "id": 1627732,
            "season": "2020-21"
        },
        {
            "name": "Luka Doncic (The Helico)",
            "id": 1629029,
            "season": "2023-24"
        }
    ]

    for target in targets:
        logger.info(f"Fetching data for {target['name']}...")
        df_rs = get_shot_chart_df(client, target['id'], target['season'], "Regular Season")
        df_po = get_shot_chart_df(client, target['id'], target['season'], "Playoffs")
        
        analyze_plasticity(df_rs, df_po, target['name'], target['season'])
        
        # Be nice to the API
        time.sleep(1)

if __name__ == "__main__":
    main()

