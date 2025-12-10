"""
Test HoopsHype GraphQL API for salary data collection.

Tests the new API implementation on a single season to verify:
1. API connectivity and response format
2. Data extraction
3. Match rate improvements
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nba_data.scripts.collect_salary_data import SalaryCollector
import pandas as pd

def test_single_season(season: str = "2024-25"):
    """Test salary collection on a single season."""
    print(f"\n{'='*60}")
    print(f"Testing HoopsHype API for season: {season}")
    print(f"{'='*60}\n")
    
    collector = SalaryCollector()
    
    # Test API fetch
    print("1. Testing API fetch...")
    df_api = collector.fetch_hoopshype_api_salaries(season)
    
    if df_api.empty:
        print("   ❌ API returned empty results")
        return
    
    print(f"   ✅ API returned {len(df_api)} contracts")
    print(f"   Sample columns: {df_api.columns.tolist()}")
    
    # Show sample data
    print("\n2. Sample data:")
    print(df_api.head(10)[['SOURCE_PLAYER_NAME', 'HOOPSHYPE_PLAYER_ID', 'SALARY_MILLIONS', 'SOURCE']].to_string())
    
    # Check for player IDs
    has_ids = df_api['HOOPSHYPE_PLAYER_ID'].notna().sum()
    print(f"\n3. Player ID coverage: {has_ids}/{len(df_api)} ({has_ids/len(df_api)*100:.1f}%)")
    
    # Test matching
    print("\n4. Testing name matching...")
    df_matched = collector.fetch_season_salaries(season)
    
    if not df_matched.empty:
        matched_count = (df_matched['PLAYER_NAME'] != df_matched['SOURCE_PLAYER_NAME']).sum()
        match_rate = matched_count / len(df_matched) * 100
        print(f"   ✅ Matched {matched_count}/{len(df_matched)} names ({match_rate:.1f}%)")
        
        # Show some matched examples
        print("\n5. Sample matched names:")
        matched_examples = df_matched[df_matched['PLAYER_NAME'] != df_matched['SOURCE_PLAYER_NAME']].head(5)
        for _, row in matched_examples.iterrows():
            print(f"   '{row['SOURCE_PLAYER_NAME']}' -> '{row['PLAYER_NAME']}'")
        
        # Show unmatched examples
        print("\n6. Sample unmatched names:")
        unmatched_examples = df_matched[df_matched['PLAYER_NAME'] == df_matched['SOURCE_PLAYER_NAME']].head(5)
        for _, row in unmatched_examples.iterrows():
            print(f"   '{row['SOURCE_PLAYER_NAME']}' (no match found)")
    
    # Compare with old method (if we want)
    print("\n7. Testing HTML fallback...")
    df_html = collector.fetch_hoopshype_salaries(season)
    if not df_html.empty:
        print(f"   ✅ HTML method returned {len(df_html)} contracts")
        print(f"   API method: {len(df_api)} contracts")
        print(f"   HTML method: {len(df_html)} contracts")
        if len(df_api) > 0:
            coverage_diff = ((len(df_api) - len(df_html)) / len(df_html)) * 100
            print(f"   Coverage difference: {coverage_diff:+.1f}%")
    
    print(f"\n{'='*60}")
    print("Test complete!")
    print(f"{'='*60}\n")
    
    return df_matched

if __name__ == "__main__":
    # Test on most recent season
    test_season = "2024-25"
    if len(sys.argv) > 1:
        test_season = sys.argv[1]
    
    result = test_single_season(test_season)
    
    if result is not None and not result.empty:
        print(f"\n✅ Test successful! Collected {len(result)} salary records for {test_season}")
        print(f"   Saved sample to: test_salary_output.csv")
        result.to_csv("test_salary_output.csv", index=False)
    else:
        print("\n❌ Test failed or returned no data")










