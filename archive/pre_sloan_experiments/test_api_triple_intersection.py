
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.api.shot_dashboard_client import ShotDashboardClient

logging.basicConfig(level=logging.INFO)

def test_triple_intersection():
    client = ShotDashboardClient()
    
    # Try to fetch: Tight Defense + Late Clock + 7+ Dribbles
    def_dist = '0-2 Feet - Very Tight'
    shot_clock = '4-0 Very Late'
    dribbles = '7+ Dribbles'
    
    print(f"Testing fetch for: {def_dist} AND {shot_clock} AND {dribbles}")
    
    try:
        data = client.get_player_shot_dashboard_stats(
            season_year='2023-24',
            close_def_dist_range=def_dist,
            shot_clock_range=shot_clock,
            dribble_range=dribbles
        )
        
        result_sets = data.get('resultSets', [])
        if not result_sets:
            print("❌ API returned no resultSets")
            return
            
        row_set = result_sets[0].get('rowSet', [])
        print(f"✅ Success! Received {len(row_set)} rows.")
        if len(row_set) > 0:
            headers = result_sets[0].get('headers')
            sample = dict(zip(headers, row_set[0]))
            print(f"Sample Player: {sample.get('PLAYER_NAME')}")
            print(f"FG%: {sample.get('FG_PCT')}")
            print(f"FGA: {sample.get('FGA')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_triple_intersection()

