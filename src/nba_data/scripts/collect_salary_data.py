"""
Collect Historical NBA Salary Data

Sources: Basketball Reference (primary), HoopsHype (fallback)
Method: Season-level table scraping (1 request per season)
Output: data/salaries.csv

This script fetches historical salary data to enable "Alpha Score" calculation
(Value - Price). It normalizes names to match the NBA Stats API conventions.

Note: HoopsHype URLs for historical seasons may return 404. Basketball Reference
is more reliable for historical data.
"""

import pandas as pd
import requests
import logging
import time
import re
from pathlib import Path
from typing import Optional, Dict, List
from io import StringIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/salary_collection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = Path("data")
RESULTS_DIR = Path("results")
OUTPUT_FILE = DATA_DIR / "salaries.csv"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


class SalaryCollector:
    def __init__(self):
        self.seasons = [
            "2015-16", "2016-17", "2017-18", "2018-19", "2019-20",
            "2020-21", "2021-22", "2022-23", "2023-24", "2024-25"
        ]
        DATA_DIR.mkdir(exist_ok=True)
        RESULTS_DIR.mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
    
    def get_basketball_reference_url(self, season: str) -> str:
        """Convert '2015-16' to Basketball Reference URL."""
        # Basketball Reference uses format: /contracts/players.html?y1=2016
        # The year is the END year of the season
        start_year = int(season.split('-')[0])
        end_year = start_year + 1
        return f"https://www.basketball-reference.com/contracts/players.html?y1={end_year}"
    
    def get_hoopshype_url(self, season: str) -> str:
        """Convert '2015-16' to HoopsHype URL (may not work for historical data)."""
        start_year = season.split('-')[0]
        end_year = int(start_year) + 1
        return f"https://hoopshype.com/salaries/players/{start_year}-{end_year}/"
    
    def clean_salary(self, salary_str: str) -> float:
        """Convert '$12,345,678' to 12.345678 (millions)."""
        if pd.isna(salary_str):
            return 0.0
        try:
            clean_str = str(salary_str).replace('$', '').replace(',', '').strip()
            return float(clean_str) / 1_000_000
        except ValueError:
            return 0.0
    
    def normalize_name(self, name: str) -> str:
        """
        Normalize player name for matching.
        - Removes periods (C.J. -> CJ)
        - Removes special characters (Dončić -> Doncic)
        - Handles encoding issues
        - Removes common suffixes (Jr., Sr., II, III, IV)
        - Lowercase
        - Strips whitespace
        """
        if pd.isna(name):
            return ""
        name = str(name)
        
        # Handle encoding issues (fix corrupted unicode)
        try:
            # Try to fix common encoding issues
            if '\\x' in repr(name) or 'Ä' in name:
                name = name.encode('latin-1').decode('utf-8', errors='ignore')
        except:
            pass
        
        # Remove periods
        name = name.replace('.', '')
        
        # Remove common suffixes (Jr., Sr., II, III, IV, etc.)
        suffixes = ['jr', 'sr', 'ii', 'iii', 'iv', 'v']
        name_parts = name.split()
        if len(name_parts) > 0:
            last_part = name_parts[-1].lower().rstrip(',')
            if last_part in suffixes:
                name = ' '.join(name_parts[:-1])
        
        # Remove special characters (accents) and normalize unicode
        import unicodedata
        name = unicodedata.normalize('NFKD', name)
        name = name.encode('ascii', 'ignore').decode('ascii')
        
        # Remove hyphens and apostrophes for matching (keep in original)
        name = name.replace('-', ' ').replace("'", '').replace("'", '')
        
        # Lowercase and strip
        name = name.lower().strip()
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        return name
    
    def fetch_season_salaries(self, season: str) -> pd.DataFrame:
        """Fetch salary data for a single season. Tries Basketball Reference first, then HoopsHype."""
        # Try Basketball Reference first (more reliable for historical data)
        br_url = self.get_basketball_reference_url(season)
        logger.info(f"Fetching {season} from Basketball Reference: {br_url}...")
        
        try:
            response = requests.get(br_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            # Parse tables
            tables = pd.read_html(StringIO(response.text))
            if tables:
                # Basketball Reference contract table is usually the first table
                df = tables[0]
                
                # BR table structure: Player, Team, Salary (in millions already)
                # Find player and salary columns
                df.columns = [str(c).lower() for c in df.columns]
                player_col = next((c for c in df.columns if 'player' in c), None)
                salary_col = next((c for c in df.columns if 'salary' in c or '$' in str(df[c].iloc[0] if len(df) > 0 else '')), None)
                
                if player_col and salary_col:
                    df_clean = pd.DataFrame()
                    df_clean['PLAYER_NAME'] = df[player_col]
                    # BR already has salaries in millions, but may have $ and commas
                    df_clean['SALARY_MILLIONS'] = df[salary_col].apply(self.clean_salary)
                    df_clean['SEASON'] = season
                    df_clean = df_clean[df_clean['SALARY_MILLIONS'] > 0]
                    
                    logger.info(f"  ✅ Parsed {len(df_clean)} salaries from Basketball Reference for {season}")
                    return df_clean
        except Exception as e:
            logger.debug(f"  Basketball Reference failed: {e}")
        
        # Fallback to HoopsHype
        start_year = season.split('-')[0]
        end_year = int(start_year) + 1
        url_patterns = [
            f"https://hoopshype.com/salaries/players/{start_year}-{end_year}/",
            f"https://hoopshype.com/salaries/players/{season}/",
        ]
        
        for url in url_patterns:
            logger.info(f"  Trying HoopsHype fallback: {url}...")
            try:
                response = requests.get(url, headers=HEADERS, timeout=30)
                if response.status_code == 200:
                    tables = pd.read_html(StringIO(response.text))
                    if tables:
                        df = tables[0]
                        df.columns = [str(c).lower() for c in df.columns]
                        player_col = next((c for c in df.columns if 'player' in c), None)
                        salary_col = next((c for c in df.columns if 'salary' in c and 'adjustment' not in c and 'inflation' not in c), None)
                        
                        if not salary_col and len(df.columns) >= 3:
                            salary_col = df.columns[2]
                        
                        if player_col and salary_col:
                            df_clean = pd.DataFrame()
                            df_clean['PLAYER_NAME'] = df[player_col]
                            df_clean['SALARY_MILLIONS'] = df[salary_col].apply(self.clean_salary)
                            df_clean['SEASON'] = season
                            df_clean = df_clean[df_clean['SALARY_MILLIONS'] > 0]
                            
                            logger.info(f"  ✅ Parsed {len(df_clean)} salaries from HoopsHype for {season}")
                            return df_clean
            except Exception as e:
                logger.debug(f"  HoopsHype pattern failed: {e}")
                continue
        
        logger.error(f"  ❌ Could not fetch salary data for {season} from any source")
        return pd.DataFrame()
    
    def collect_all(self):
        """Run collection for all seasons."""
        all_salaries = []
        
        for season in self.seasons:
            df = self.fetch_season_salaries(season)
            if not df.empty:
                all_salaries.append(df)
            # Be polite
            time.sleep(2)
        
        if not all_salaries:
            logger.error("No salary data collected.")
            return
        
        final_df = pd.concat(all_salaries, ignore_index=True)
        
        # Save Raw
        final_df.to_csv(OUTPUT_FILE, index=False)
        logger.info(f"✅ Saved raw salary data to {OUTPUT_FILE} ({len(final_df)} rows)")
        
        self.validate_coverage(final_df)
    
    def validate_coverage(self, salary_df: pd.DataFrame):
        """Check how well we match against our predictive dataset."""
        pred_path = RESULTS_DIR / "predictive_dataset.csv"
        if not pred_path.exists():
            logger.warning("Predictive dataset not found. Skipping coverage check.")
            return
        
        pred_df = pd.read_csv(pred_path)
        
        # Create normalized names
        pred_df['NORM_NAME'] = pred_df['PLAYER_NAME'].apply(self.normalize_name)
        salary_df['NORM_NAME'] = salary_df['PLAYER_NAME'].apply(self.normalize_name)
        
        # Create matching keys (name + season)
        pred_df['MATCH_KEY'] = pred_df['NORM_NAME'] + "_" + pred_df['SEASON']
        salary_df['MATCH_KEY'] = salary_df['NORM_NAME'] + "_" + salary_df['SEASON']
        
        # Check exact matches
        matched = pred_df[pred_df['MATCH_KEY'].isin(salary_df['MATCH_KEY'])]
        exact_match_rate = len(matched) / len(pred_df) * 100
        
        # Try fuzzy matching for unmatched players (match by name only, ignore season)
        unmatched_pred = pred_df[~pred_df['MATCH_KEY'].isin(salary_df['MATCH_KEY'])].copy()
        if len(unmatched_pred) > 0:
            # Create a lookup of normalized names in salary data
            salary_names = set(salary_df['NORM_NAME'].unique())
            fuzzy_matched = unmatched_pred[unmatched_pred['NORM_NAME'].isin(salary_names)]
            fuzzy_match_count = len(fuzzy_matched)
        else:
            fuzzy_match_count = 0
        
        total_match_rate = (len(matched) + fuzzy_match_count) / len(pred_df) * 100
        
        logger.info("=" * 60)
        logger.info(f"COVERAGE REPORT")
        logger.info("=" * 60)
        logger.info(f"Predictive Dataset Rows: {len(pred_df)}")
        logger.info(f"Salary Database Rows: {len(salary_df)}")
        logger.info(f"Exact Matches (Name + Season): {len(matched)} ({exact_match_rate:.1f}%)")
        logger.info(f"Fuzzy Matches (Name Only): {fuzzy_match_count} additional")
        logger.info(f"Total Potential Matches: {len(matched) + fuzzy_match_count} ({total_match_rate:.1f}%)")
        
        if exact_match_rate < 80:
            logger.warning("⚠️  Exact match rate is low. Some players may need manual matching.")
            
            # Show sample mismatches
            unmatched = pred_df[~pred_df['MATCH_KEY'].isin(salary_df['MATCH_KEY'])].head(10)
            logger.info("\nSample Unmatched Players (showing normalized names):")
            for _, row in unmatched.iterrows():
                logger.info(f"  - {row['PLAYER_NAME']} -> '{row['NORM_NAME']}' ({row['SEASON']})")
                
                # Show closest match in salary data
                salary_matches = salary_df[salary_df['NORM_NAME'].str.contains(row['NORM_NAME'].split()[-1] if len(row['NORM_NAME'].split()) > 0 else '', case=False, na=False)]
                if len(salary_matches) > 0:
                    logger.info(f"    Possible match: {salary_matches.iloc[0]['PLAYER_NAME']} -> '{salary_matches.iloc[0]['NORM_NAME']}'")


if __name__ == "__main__":
    collector = SalaryCollector()
    collector.collect_all()

