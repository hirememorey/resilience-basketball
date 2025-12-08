"""
Test script to verify USG_PCT and AGE population fix.

This script tests that fetch_player_metadata() correctly fetches USG_PCT and AGE
from the advanced_stats endpoint (not base_stats).

Usage:
    python test_usg_age_fix.py [--season SEASON]
    
Example:
    python test_usg_age_fix.py --season 2024-25
"""

import sys
import argparse
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from src.nba_data.scripts.evaluate_plasticity_potential import StressVectorEngine
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_fetch_player_metadata(season: str = "2024-25"):
    """
    Test that fetch_player_metadata() correctly populates USG_PCT and AGE.
    
    Args:
        season: Season to test (default: 2024-25)
    
    Returns:
        dict: Test results with pass/fail status and details
    """
    logger.info("=" * 80)
    logger.info(f"Testing USG_PCT/AGE Fix for Season: {season}")
    logger.info("=" * 80)
    
    results = {
        "season": season,
        "passed": False,
        "tests": {},
        "errors": []
    }
    
    try:
        # Initialize engine
        engine = StressVectorEngine()
        
        # Test 1: Fetch metadata
        logger.info("\n[Test 1] Fetching player metadata...")
        df_metadata = engine.fetch_player_metadata(season)
        
        if df_metadata.empty:
            results["errors"].append("fetch_player_metadata() returned empty DataFrame")
            results["tests"]["fetch_metadata"] = False
            return results
        
        results["tests"]["fetch_metadata"] = True
        logger.info(f"✅ Successfully fetched metadata for {len(df_metadata)} players")
        
        # Test 2: Verify required columns exist
        logger.info("\n[Test 2] Verifying required columns...")
        required_cols = ['PLAYER_ID', 'PLAYER_NAME', 'USG_PCT', 'AGE']
        missing_cols = [col for col in required_cols if col not in df_metadata.columns]
        
        if missing_cols:
            results["errors"].append(f"Missing required columns: {missing_cols}")
            results["tests"]["required_columns"] = False
            logger.error(f"❌ Missing columns: {missing_cols}")
            logger.error(f"Available columns: {list(df_metadata.columns)}")
        else:
            results["tests"]["required_columns"] = True
            logger.info(f"✅ All required columns present: {required_cols}")
        
        # Test 3: Check USG_PCT coverage
        logger.info("\n[Test 3] Checking USG_PCT coverage...")
        usg_coverage = df_metadata['USG_PCT'].notna().sum()
        usg_total = len(df_metadata)
        usg_pct = (usg_coverage / usg_total * 100) if usg_total > 0 else 0
        
        results["tests"]["usg_coverage"] = {
            "coverage": usg_coverage,
            "total": usg_total,
            "percentage": usg_pct
        }
        
        if usg_pct < 90:
            results["errors"].append(f"USG_PCT coverage too low: {usg_pct:.1f}% (expected ≥90%)")
            results["tests"]["usg_coverage"]["passed"] = False
            logger.warning(f"⚠️  USG_PCT coverage: {usg_coverage}/{usg_total} ({usg_pct:.1f}%)")
        else:
            results["tests"]["usg_coverage"]["passed"] = True
            logger.info(f"✅ USG_PCT coverage: {usg_coverage}/{usg_total} ({usg_pct:.1f}%)")
        
        # Test 4: Check AGE coverage
        logger.info("\n[Test 4] Checking AGE coverage...")
        age_coverage = df_metadata['AGE'].notna().sum()
        age_total = len(df_metadata)
        age_pct = (age_coverage / age_total * 100) if age_total > 0 else 0
        
        results["tests"]["age_coverage"] = {
            "coverage": age_coverage,
            "total": age_total,
            "percentage": age_pct
        }
        
        if age_pct < 90:
            results["errors"].append(f"AGE coverage too low: {age_pct:.1f}% (expected ≥90%)")
            results["tests"]["age_coverage"]["passed"] = False
            logger.warning(f"⚠️  AGE coverage: {age_coverage}/{age_total} ({age_pct:.1f}%)")
        else:
            results["tests"]["age_coverage"]["passed"] = True
            logger.info(f"✅ AGE coverage: {age_coverage}/{age_total} ({age_pct:.1f}%)")
        
        # Test 5: Verify USG_PCT format (should be percentage, not decimal)
        logger.info("\n[Test 5] Verifying USG_PCT format...")
        usg_values = df_metadata['USG_PCT'].dropna()
        
        if len(usg_values) > 0:
            max_usg = usg_values.max()
            min_usg = usg_values.min()
            median_usg = usg_values.median()
            
            results["tests"]["usg_format"] = {
                "max": float(max_usg),
                "min": float(min_usg),
                "median": float(median_usg)
            }
            
            # USG_PCT should be in percentage format (typically 15-40 range)
            # If it's in decimal format, values would be 0.15-0.40
            if max_usg < 1.0:
                results["errors"].append(f"USG_PCT appears to be in decimal format (max={max_usg:.3f}), expected percentage format")
                results["tests"]["usg_format"]["passed"] = False
                logger.warning(f"⚠️  USG_PCT appears to be decimal format (max={max_usg:.3f})")
            elif max_usg > 50:
                results["errors"].append(f"USG_PCT values seem too high (max={max_usg:.1f}), may be incorrectly scaled")
                results["tests"]["usg_format"]["passed"] = False
                logger.warning(f"⚠️  USG_PCT values seem too high (max={max_usg:.1f})")
            else:
                results["tests"]["usg_format"]["passed"] = True
                logger.info(f"✅ USG_PCT format correct: range [{min_usg:.1f}, {max_usg:.1f}], median={median_usg:.1f}")
        else:
            results["errors"].append("No USG_PCT values to verify format")
            results["tests"]["usg_format"]["passed"] = False
        
        # Test 6: Verify AGE format (should be reasonable values)
        logger.info("\n[Test 6] Verifying AGE format...")
        age_values = df_metadata['AGE'].dropna()
        
        if len(age_values) > 0:
            max_age = age_values.max()
            min_age = age_values.min()
            median_age = age_values.median()
            
            results["tests"]["age_format"] = {
                "max": float(max_age),
                "min": float(min_age),
                "median": float(median_age)
            }
            
            # AGE should be reasonable (typically 18-45 for NBA players)
            if min_age < 18 or max_age > 50:
                results["errors"].append(f"AGE values seem unreasonable: min={min_age}, max={max_age}")
                results["tests"]["age_format"]["passed"] = False
                logger.warning(f"⚠️  AGE values seem unreasonable: min={min_age}, max={max_age}")
            else:
                results["tests"]["age_format"]["passed"] = True
                logger.info(f"✅ AGE format correct: range [{min_age:.0f}, {max_age:.0f}], median={median_age:.0f}")
        else:
            results["errors"].append("No AGE values to verify format")
            results["tests"]["age_format"]["passed"] = False
        
        # Test 7: Sample data validation
        logger.info("\n[Test 7] Sampling data for validation...")
        sample_size = min(10, len(df_metadata))
        sample_df = df_metadata.head(sample_size)
        
        # Check for known players (if available)
        sample_players = sample_df[['PLAYER_NAME', 'USG_PCT', 'AGE']].copy()
        sample_players = sample_players[sample_players['USG_PCT'].notna() & sample_players['AGE'].notna()]
        
        results["tests"]["sample_data"] = {
            "sample_size": len(sample_players),
            "players": sample_players.to_dict('records')[:5]  # First 5 for display
        }
        
        if len(sample_players) > 0:
            logger.info(f"✅ Sample data available for {len(sample_players)} players")
            logger.info("\nSample players:")
            for idx, row in sample_players.head(5).iterrows():
                logger.info(f"  - {row['PLAYER_NAME']}: USG_PCT={row['USG_PCT']:.1f}%, AGE={row['AGE']:.0f}")
            results["tests"]["sample_data"]["passed"] = True
        else:
            results["errors"].append("No sample players with both USG_PCT and AGE")
            results["tests"]["sample_data"]["passed"] = False
        
        # Test 8: Verify no duplicate PLAYER_IDs
        logger.info("\n[Test 8] Checking for duplicate PLAYER_IDs...")
        duplicates = df_metadata['PLAYER_ID'].duplicated().sum()
        
        if duplicates > 0:
            results["errors"].append(f"Found {duplicates} duplicate PLAYER_IDs")
            results["tests"]["no_duplicates"] = False
            logger.warning(f"⚠️  Found {duplicates} duplicate PLAYER_IDs")
        else:
            results["tests"]["no_duplicates"] = True
            logger.info(f"✅ No duplicate PLAYER_IDs found")
        
        # Overall result
        all_tests_passed = all(
            test.get("passed", False) if isinstance(test, dict) else test
            for test in results["tests"].values()
        )
        
        results["passed"] = all_tests_passed and len(results["errors"]) == 0
        
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}", exc_info=True)
        results["errors"].append(f"Exception: {str(e)}")
        results["passed"] = False
    
    return results


def print_summary(results: dict):
    """Print test summary."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    logger.info(f"\nSeason: {results['season']}")
    logger.info(f"Overall Status: {'✅ PASSED' if results['passed'] else '❌ FAILED'}")
    
    logger.info("\nTest Results:")
    for test_name, test_result in results["tests"].items():
        if isinstance(test_result, dict):
            passed = test_result.get("passed", False)
            status = "✅" if passed else "❌"
            logger.info(f"  {status} {test_name}")
            if "coverage" in test_result:
                logger.info(f"     Coverage: {test_result['coverage']}/{test_result['total']} ({test_result['percentage']:.1f}%)")
        else:
            status = "✅" if test_result else "❌"
            logger.info(f"  {status} {test_name}")
    
    if results["errors"]:
        logger.info(f"\n❌ Errors ({len(results['errors'])}):")
        for error in results["errors"]:
            logger.info(f"  - {error}")
    else:
        logger.info("\n✅ No errors")
    
    logger.info("\n" + "=" * 80)


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description="Test USG_PCT/AGE population fix")
    parser.add_argument(
        "--season",
        type=str,
        default="2024-25",
        help="Season to test (default: 2024-25)"
    )
    
    args = parser.parse_args()
    
    # Run tests
    results = test_fetch_player_metadata(args.season)
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if results["passed"] else 1)


if __name__ == "__main__":
    main()

