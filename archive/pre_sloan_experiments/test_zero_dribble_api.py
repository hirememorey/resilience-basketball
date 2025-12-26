
import sys
import os
import json
import logging
import time

# Add the parent directory of 'api' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.nba_stats_client import NBAStatsClient, EmptyResponseError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def audit_zero_dribble_data_availability():
    """
    Tests the availability of '0 Dribble' shooting stats from the NBA Stats API
    across a range of seasons to ensure historical data integrity.
    """
    logging.info("Starting historical audit for '0 Dribble' data availability...")
    
    client = NBAStatsClient()
    seasons_to_audit = [f"{year}-{str(year+1)[-2:]}" for year in range(2015, 2025)]
    
    all_seasons_successful = True
    
    for season in seasons_to_audit:
        logging.info(f"--- Auditing Season: {season} ---")
        try:
            data = client.get_league_player_shooting_stats(
                season=season,
                season_type="Regular Season",
                dribble_range="0 Dribbles"
            )
            
            if not data or 'resultSets' not in data or not data['resultSets']:
                raise EmptyResponseError("API returned a response with no result sets.")
                
            result_set = data['resultSets'][0]
            rows = result_set.get('rowSet')
            
            if not rows:
                logging.warning(f"Season {season}: SUCCESS (Endpoint Valid), but returned 0 players.")
            else:
                logging.info(f"✅ Season {season}: SUCCESS, returned {len(rows)} players.")
            
        except Exception as e:
            logging.error(f"❌ Season {season}: FAILED. Error: {e}", exc_info=True)
            all_seasons_successful = False
        
        # Respectful delay to avoid hammering the API
        time.sleep(2)

    print("\n--- AUDIT COMPLETE ---")
    if all_seasons_successful:
        print("✅ Success: The '0 Dribble' data endpoint is reliable for all audited seasons (2015-2025).")
        print("We can proceed with Path A.")
    else:
        print("❌ Failure: One or more seasons failed to return data.")
        print("Review the logs above. We may need to pivot to Contingency B for the failed seasons.")

if __name__ == "__main__":
    audit_zero_dribble_data_availability()
