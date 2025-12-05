"""
Test script to verify RFE model works with updated prediction scripts.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "nba_data" / "scripts"))

from predict_conditional_archetype import ConditionalArchetypePredictor
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rfe_model():
    """Test that RFE model works with prediction script."""
    logger.info("=" * 80)
    logger.info("Testing RFE Model with Prediction Script")
    logger.info("=" * 80)
    
    # Initialize predictor with RFE model
    try:
        predictor = ConditionalArchetypePredictor(use_rfe_model=True)
        logger.info("✅ RFE model loaded successfully")
        logger.info(f"✅ Model expects {len(predictor.feature_names)} features")
        logger.info(f"✅ Features: {predictor.feature_names}")
    except Exception as e:
        logger.error(f"❌ Failed to load RFE model: {e}")
        return False
    
    # Test with a known player (Brunson 2020-21)
    try:
        player_data = predictor.get_player_data("Jalen Brunson", "2020-21")
        if player_data is None:
            logger.warning("Could not find test player data")
            return False
        
        logger.info(f"✅ Loaded player data for Jalen Brunson (2020-21)")
        
        # Test prediction at different usage levels
        usage_levels = [0.196, 0.25, 0.32]
        
        for usage in usage_levels:
            result = predictor.predict_archetype_at_usage(player_data, usage)
            logger.info(f"✅ Prediction at {usage*100:.1f}% usage: {result['predicted_archetype']} ({result['star_level_potential']*100:.2f}% star-level)")
        
        logger.info("=" * 80)
        logger.info("✅ All tests passed!")
        logger.info("=" * 80)
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rfe_model()
    sys.exit(0 if success else 1)

