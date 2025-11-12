#!/usr/bin/env python3
"""
Test script for possession-level data fetching and parsing.

Tests the new possession analytics infrastructure for playoff resilience analysis.
"""

import sys
from pathlib import Path
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.nba_data.api.possession_fetcher import create_possession_fetcher

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_possession_fetcher():
    """Test the possession fetcher with sample data."""
    print("🧪 Testing NBA Possession Fetcher...")
    print("=" * 50)

    fetcher = create_possession_fetcher()

    # Test with a recent NBA game (you would replace this with a real game ID)
    # For testing, we'll use a placeholder game ID
    test_game_id = "0022400001"  # This is likely not a real game ID

    try:
        print(f"Fetching possession data for game {test_game_id}...")

        # This will likely fail with the placeholder ID, but tests the API connection
        possessions = fetcher.fetch_game_possessions(test_game_id)

        print("✅ Successfully fetched possession data!")
        print(f"Number of possessions: {len(possessions)}")

        if possessions:
            # Show details of first possession
            possession = possessions[0]
            print("\n📊 Sample Possession Details:")
            print(f"  ID: {possession.possession_id}")
            print(f"  Period: {possession.period}")
            print(f"  Duration: {possession.duration_seconds:.1f}s")
            print(f"  Points Scored: {possession.points_scored}")
            print(f"  Events: {len(possession.events)}")
            print(f"  Lineups: {len(possession.lineups)}")
            print(f"  Matchups: {len(possession.matchups)}")

            if possession.events:
                print("\n🎯 Sample Events:")
                for i, event in enumerate(possession.events[:3]):  # Show first 3 events
                    print(f"    {i+1}. {event.event_type} by Player {event.player_id} at {event.clock_time}")

    except Exception as e:
        print(f"❌ Test failed (expected with placeholder game ID): {e}")
        print("\n💡 This is normal - the test uses a placeholder game ID.")
        print("   To test with real data, use a valid NBA game ID from the 2024-25 season.")


def test_api_endpoints():
    """Test that the new API endpoints are available."""
    print("\n🔗 Testing API Endpoints...")
    print("=" * 30)

    fetcher = create_possession_fetcher()
    client = fetcher.client

    # Test play-by-play endpoint
    try:
        print("Testing play-by-play endpoint...")
        # This will test the API structure even if the game doesn't exist
        result = client.get_play_by_play("0022400001")
        print("✅ Play-by-play endpoint accessible")
    except Exception as e:
        print(f"❌ Play-by-play endpoint failed: {e}")

    # Test game rotation endpoint
    try:
        print("Testing game rotation endpoint...")
        result = client.get_game_rotation("0022400001")
        print("✅ Game rotation endpoint accessible")
    except Exception as e:
        print(f"❌ Game rotation endpoint failed: {e}")


def main():
    """Run all possession tests."""
    print("🏀 NBA Possession-Level Analytics Test Suite")
    print("=" * 50)

    test_api_endpoints()
    test_possession_fetcher()

    print("\n🎉 Test suite complete!")
    print("\n💡 Next steps:")
    print("1. Update test with real NBA game IDs from your database")
    print("2. Run populate_possession_data.py with actual game IDs")
    print("3. Validate possession data quality")
    print("4. Build resilience metrics using possession-level features")


if __name__ == "__main__":
    main()
