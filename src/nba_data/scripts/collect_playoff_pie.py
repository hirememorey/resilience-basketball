"""
Collect Playoff PIE (Player Impact Estimate) data for all seasons.

This script fetches playoff advanced stats which includes PIE and aggregates
it at the player-season level for use in component analysis.
"""

import pandas as pd
import logging
import sys
from pathlib import Path
from typing import List

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.nba_data.api.nba_stats_client import NBAStatsClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/playoff_pie_collection.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def collect_playoff_pie(seasons: List[str]) -> pd.DataFrame:
    """Collect playoff PIE data for given seasons."""
    client = NBAStatsClient()
    all_data = []
    
    for season in seasons:
        logger.info(f"Fetching playoff PIE data for {season}...")
        try:
            response = client.get_league_player_playoff_advanced_stats(season=season)
            
            if not response or 'resultSets' not in response or not response['resultSets']:
                logger.warning(f"No data returned for {season}")
                continue
            
            df = pd.DataFrame(
                response['resultSets'][0]['rowSet'],
                columns=response['resultSets'][0]['headers']
            )
            
            if df.empty:
                logger.warning(f"Empty dataframe for {season}")
                continue
            
            # Select relevant columns
            cols_to_keep = ['PLAYER_ID', 'PLAYER_NAME', 'SEASON_ID', 'TEAM_ABBREVIATION']
            
            # Check which columns exist
            available_cols = [c for c in cols_to_keep if c in df.columns]
            
            # Add PIE and other useful metrics
            metric_cols = ['PIE', 'NET_RATING', 'OFF_RATING', 'DEF_RATING', 
                          'TS_PCT', 'USG_PCT', 'GP', 'MIN']
            available_cols.extend([c for c in metric_cols if c in df.columns])
            
            df_season = df[available_cols].copy()
            df_season['SEASON'] = season
            
            all_data.append(df_season)
            logger.info(f"  -> Collected {len(df_season)} players for {season}")
            
        except Exception as e:
            logger.error(f"Error fetching {season}: {e}")
            continue
    
    if not all_data:
        logger.error("No data collected!")
        return pd.DataFrame()
    
    # Combine all seasons
    df_all = pd.concat(all_data, ignore_index=True)
    logger.info(f"Total players collected: {len(df_all)}")
    
    return df_all


def aggregate_by_player_season(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate playoff stats by player-season (handles players who switched teams)."""
    logger.info("Aggregating by player-season...")
    
    # Group by player and season, taking weighted averages where appropriate
    agg_dict = {
        'PIE': 'mean',  # Average PIE across series
        'NET_RATING': 'mean',
        'OFF_RATING': 'mean',
        'DEF_RATING': 'mean',
        'TS_PCT': 'mean',
        'USG_PCT': 'mean',
        'GP': 'sum',  # Total games played
        'MIN': 'sum',  # Total minutes
        'PLAYER_NAME': 'first',  # Keep name
        'TEAM_ABBREVIATION': lambda x: ', '.join(x.unique())  # List teams
    }
    
    # Only aggregate columns that exist
    existing_agg = {k: v for k, v in agg_dict.items() if k in df.columns}
    
    df_agg = df.groupby(['PLAYER_ID', 'SEASON']).agg(existing_agg).reset_index()
    
    logger.info(f"Aggregated to {len(df_agg)} player-seasons")
    
    return df_agg


def main():
    """Main execution."""
    seasons = [
        "2015-16", "2016-17", "2017-18", "2018-19", "2019-20",
        "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"
    ]
    
    # Collect data
    df = collect_playoff_pie(seasons)
    
    if df.empty:
        logger.error("No data collected. Exiting.")
        return
    
    # Aggregate by player-season
    df_agg = aggregate_by_player_season(df)
    
    # Save
    output_path = Path("data/playoff_pie_data.csv")
    df_agg.to_csv(output_path, index=False)
    logger.info(f"Saved playoff PIE data to {output_path}")
    
    # Print summary
    logger.info("=" * 60)
    logger.info("Collection Summary")
    logger.info("=" * 60)
    logger.info(f"Total player-seasons: {len(df_agg)}")
    if 'PIE' in df_agg.columns:
        logger.info(f"PIE coverage: {df_agg['PIE'].notna().sum()} / {len(df_agg)} ({100 * df_agg['PIE'].notna().sum() / len(df_agg):.1f}%)")
        logger.info(f"PIE range: {df_agg['PIE'].min():.3f} to {df_agg['PIE'].max():.3f}")


if __name__ == "__main__":
    main()

