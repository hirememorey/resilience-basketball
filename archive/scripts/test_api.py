#!/usr/bin/env python3
"""
Test script for NBA data API functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nba_data.api import create_data_fetcher, create_nba_stats_client

def test_api_client():
    """Test the basic API client."""
    print("Testing NBA Stats API Client...")
    print("=" * 50)

    client = create_nba_stats_client()

    try:
        print("Fetching basic player stats...")
        data = client.get_league_player_base_stats()
        player_count = len(data.get('resultSets', [{}])[0].get('rowSet', []))
        print(f"✅ Successfully fetched data for {player_count} players")

        print("Fetching advanced player stats...")
        data = client.get_league_player_advanced_stats()
        player_count = len(data.get('resultSets', [{}])[0].get('rowSet', []))
        print(f"✅ Successfully fetched advanced data for {player_count} players")

    except Exception as e:
        print(f"❌ API client test failed: {e}")

def test_data_fetcher():
    """Test the data fetcher functionality."""
    print("\nTesting NBA Data Fetcher...")
    print("=" * 50)

    try:
        fetcher = create_data_fetcher()

        print(f"Available metrics: {len(fetcher.get_available_metrics())}")
        print(f"Missing metrics: {len(fetcher.get_missing_metrics())}")

        # Test fetching a few key metrics
        test_metrics = ["FTPCT", "TSPCT", "FGPCT", "USGPCT"]

        for metric in test_metrics:
            print(f"\nTesting fetch for {metric}...")
            data = fetcher.fetch_metric_data(metric)
            if data:
                print(f"✅ Successfully fetched data for {len(data)} players")
                # Show a sample
                if data:
                    sample_player = list(data.keys())[0]
                    print(f"   Sample: Player {sample_player} = {data[sample_player]}")
            else:
                print("❌ Failed to fetch data")

    except Exception as e:
        print(f"❌ Data fetcher test failed: {e}")

def main():
    """Run all tests."""
    test_api_client()
    test_data_fetcher()
    print("\n🎉 API testing complete!")

if __name__ == "__main__":
    main()
