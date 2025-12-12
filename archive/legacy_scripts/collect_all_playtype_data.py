#!/usr/bin/env python3
"""
Collect Playtype Data for All Players

This script ensures ISO_FREQUENCY and PNR_HANDLER_FREQUENCY are collected
for ALL players in the predictive dataset, not just qualified players.

First Principles Approach:
- The Bag Check Gate requires SELF_CREATED_FREQ = ISO_FREQUENCY + PNR_HANDLER_FREQUENCY
- Missing this data causes incorrect gate application (e.g., Mikal Bridges)
- We need to collect playtype data for ALL players, not just those with MIN >= 20.0
"""

import sys
import argparse
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.nba_data.scripts.populate_playtype_data import PlaytypeDataPopulator
import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/collect_all_playtype_data.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_all_seasons():
    """Get all seasons from 2015-16 to 2024-25."""
    seasons = []
    for year in range(2015, 2025):
        seasons.append(f"{year}-{str(year+1)[-2:]}")
    return seasons


def collect_playtype_for_season(season: str, populator: PlaytypeDataPopulator, force_refresh: bool = False):
    """Collect playtype data for a single season."""
    try:
        logger.info(f"Collecting playtype data for {season}...")
        results = populator.populate_season_playtype_data(
            season_year=season,
            season_type="Regular Season",
            force_refresh=force_refresh
        )
        
        logger.info(f"✅ {season}: {results['records_inserted']} inserted, {results['records_updated']} updated")
        return {
            'season': season,
            'success': True,
            'records_inserted': results['records_inserted'],
            'records_updated': results['records_updated'],
            'errors': len(results['errors'])
        }
    except Exception as e:
        logger.error(f"❌ Failed to collect {season}: {e}")
        return {
            'season': season,
            'success': False,
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(description='Collect playtype data for all players across all seasons')
    parser.add_argument('--seasons', nargs='+', 
                       default=None,
                       help='Specific seasons to collect (default: all 2015-2024)')
    parser.add_argument('--force-refresh', action='store_true',
                       help='Force refresh of cached data')
    parser.add_argument('--workers', type=int, default=2,
                       help='Number of parallel workers (default: 2)')
    
    args = parser.parse_args()
    
    # Get seasons to process
    if args.seasons:
        seasons = args.seasons
    else:
        seasons = get_all_seasons()
    
    logger.info(f"🚀 Starting playtype data collection for {len(seasons)} seasons")
    logger.info(f"   Seasons: {', '.join(seasons)}")
    logger.info(f"   Workers: {args.workers}")
    logger.info(f"   Force refresh: {args.force_refresh}")
    logger.info()
    
    populator = PlaytypeDataPopulator()
    
    # Collect data for all seasons
    results = []
    
    if args.workers > 1:
        # Parallel collection
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(collect_playtype_for_season, season, populator, args.force_refresh): season
                for season in seasons
            }
            
            for future in tqdm(as_completed(futures), total=len(seasons), desc="Collecting playtype data"):
                result = future.result()
                results.append(result)
    else:
        # Sequential collection
        for season in tqdm(seasons, desc="Collecting playtype data"):
            result = collect_playtype_for_season(season, populator, args.force_refresh)
            results.append(result)
    
    # Summary
    logger.info()
    logger.info("=" * 80)
    logger.info("COLLECTION SUMMARY")
    logger.info("=" * 80)
    
    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    total_inserted = sum(r.get('records_inserted', 0) for r in successful)
    total_updated = sum(r.get('records_updated', 0) for r in successful)
    total_errors = sum(r.get('errors', 0) for r in successful)
    
    logger.info(f"✅ Successful: {len(successful)}/{len(seasons)} seasons")
    logger.info(f"❌ Failed: {len(failed)}/{len(seasons)} seasons")
    logger.info(f"📊 Total records inserted: {total_inserted:,}")
    logger.info(f"📊 Total records updated: {total_updated:,}")
    logger.info(f"⚠️  Total errors: {total_errors:,}")
    
    if failed:
        logger.info()
        logger.info("Failed seasons:")
        for r in failed:
            logger.info(f"  - {r['season']}: {r.get('error', 'Unknown error')}")
    
    logger.info()
    logger.info("=" * 80)
    logger.info("NEXT STEPS")
    logger.info("=" * 80)
    logger.info()
    logger.info("1. Verify data collection:")
    logger.info("   python src/nba_data/scripts/populate_playtype_data.py --validate-only")
    logger.info()
    logger.info("2. Re-run feature generation to merge playtype data:")
    logger.info("   python src/nba_data/scripts/evaluate_plasticity_potential.py --seasons 2015-16 2016-17 ...")
    logger.info()
    logger.info("3. Verify coverage in predictive_dataset.csv:")
    logger.info("   python analyze_data_completeness.py")
    logger.info()


if __name__ == '__main__':
    main()

