
import sys
from pathlib import Path
import logging

# Add project root to sys.path
sys.path.append(str(Path.cwd()))

from src.nba_data.scripts.predict_conditional_archetype import ConditionalArchetypePredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_loading():
    predictor = ConditionalArchetypePredictor()
    
    # Check Shai
    player = "Shai Gilgeous-Alexander"
    season = "2018-19"
    
    logger.info(f"Attempting to fetch {player} {season}...")
    data = predictor.get_player_data(player, season)
    
    if data is not None:
        logger.info("✅ Data found!")
        print(data[['PLAYER_NAME', 'SEASON', 'USG_PCT', 'FRAGILITY_SCORE']])
    else:
        logger.error("❌ Data NOT found.")
        
        # Debug: Check if player exists at all
        matches = predictor.df_features[predictor.df_features['PLAYER_NAME'].str.contains("Shai")]
        if not matches.empty:
            logger.info(f"Found partial matches for 'Shai':\n{matches[['PLAYER_NAME', 'SEASON']].head()}")
        else:
            logger.info("No matches for 'Shai' in loaded dataframe.")

if __name__ == "__main__":
    test_data_loading()

