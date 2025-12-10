"""
NBA Synergy Play Types API Client

Fetches play type statistics from the NBA Stats API synergy playtypes endpoint.
This provides detailed breakdown of player performance by play type (Isolation, Pick & Roll, etc.)
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import requests
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from nba_data.api.nba_stats_client import NBAStatsClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SynergyPlaytypesClient:
    """Client for fetching NBA synergy play type statistics."""

    # Common NBA play types from synergy data
    # Note: API uses specific names - "PutBack" is actually "OffRebound", "PostUp" is "Postup"
    # Note: "SpotUp" is not a valid playtype name in the API (returns 400 error)
    PLAY_TYPES = [
        'Isolation',
        'Transition',
        'PRBallHandler',  # Pick & Roll Ball Handler
        'PRRollMan',      # Pick & Roll Roll Man
        'Postup',         # Post Up (correct API name, not "PostUp")
        # 'SpotUp',       # REMOVED: Not a valid playtype name (returns 400 error)
        'Handoff',
        'Cut',
        'OffScreen',
        'OffRebound',     # Put Back (correct API name, not "PutBack")
        'Misc'
    ]

    def __init__(self, rate_limit_delay: float = 1.0):
        """Initialize the synergy playtypes client."""
        self.rate_limit_delay = rate_limit_delay
        self.base_client = NBAStatsClient()

    def get_player_playtype_stats(
        self,
        season_year: str = "2024-25",
        season_type: str = "Regular Season",
        play_type: str = "Isolation",
        per_mode: str = "PerGame",
        type_grouping: str = "offensive"
    ) -> Dict[str, Any]:
        """
        Fetch player play type statistics for a specific play type.

        Args:
            season_year: Season in format "2024-25"
            season_type: "Regular Season" or "Playoffs"
            play_type: One of the PLAY_TYPES constants
            per_mode: "PerGame" or "Totals"
            type_grouping: "offensive" or "defensive"

        Returns:
            Dictionary containing API response data
        """
        if play_type not in self.PLAY_TYPES:
            raise ValueError(f"Invalid play_type: {play_type}. Must be one of {self.PLAY_TYPES}")

        # Create cache key
        cache_key = f"synergy_playtypes_{season_year}_{season_type}_{play_type}_{per_mode}_{type_grouping}"
        cache_path = self.base_client._get_cache_path("synergyplaytypes", {
            'SeasonYear': season_year,
            'SeasonType': season_type,
            'PlayType': play_type,
            'PerMode': per_mode,
            'TypeGrouping': type_grouping
        })

        # Check cache first
        cached_data = self.base_client._read_from_cache(cache_path)
        if cached_data:
            logger.info(f"Loaded cached data for {play_type} play type")
            return cached_data

        # Make API request using direct requests since NBAStatsClient doesn't have generic method
        url = "https://stats.nba.com/stats/synergyplaytypes"

        params = {
            'LeagueID': '00',
            'SeasonYear': season_year,
            'SeasonType': season_type,
            'PlayerOrTeam': 'P',  # Player data
            'PlayType': play_type,
            'PerMode': per_mode,
            'TypeGrouping': type_grouping
        }

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://www.nba.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.nba.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }

        logger.info(f"Fetching synergy playtypes data for {play_type} ({season_year} {season_type})")

        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            # Handle 400/404 errors gracefully (some playtypes may not be valid or available)
            if response.status_code in [400, 404]:
                logger.warning(f"Playtype {play_type} returned {response.status_code} for {season_year} {season_type} - May be invalid playtype name or not available for this season")
                return {'resultSets': []}
            
            response.raise_for_status()

            data = response.json()

            # Validate response structure
            if 'resultSets' not in data or not data['resultSets']:
                logger.warning(f"No resultSets found in response for {play_type}")
                return {'resultSets': []}

            # Cache the successful response
            self.base_client._write_to_cache(cache_path, data)

            # Rate limiting
            time.sleep(self.rate_limit_delay)

            return data

        except requests.HTTPError as e:
            # Other HTTP errors (500, etc.) - log as error
            logger.error(f"Request failed for {play_type}: {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"Request failed for {play_type}: {e}")
            raise
        except ValueError as e:
            logger.error(f"JSON parsing failed for {play_type}: {e}")
            raise

    def get_all_playtype_stats_for_season(
        self,
        season_year: str = "2024-25",
        season_type: str = "Regular Season",
        per_mode: str = "PerGame",
        type_grouping: str = "offensive"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch play type statistics for all play types in a season.

        Returns:
            Dictionary with play_type as key and API response as value
        """
        results = {}

        for play_type in self.PLAY_TYPES:
            try:
                logger.info(f"Fetching data for play type: {play_type}")
                data = self.get_player_playtype_stats(
                    season_year=season_year,
                    season_type=season_type,
                    play_type=play_type,
                    per_mode=per_mode,
                    type_grouping=type_grouping
                )
                results[play_type] = data

            except Exception as e:
                logger.error(f"Failed to fetch data for {play_type}: {e}")
                results[play_type] = {'error': str(e), 'resultSets': []}

        return results

    def parse_playtype_response(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the API response into a list of player playtype records.

        Args:
            response_data: Raw API response dictionary

        Returns:
            List of dictionaries with standardized field names
        """
        if not response_data.get('resultSets'):
            return []

        result_set = response_data['resultSets'][0]
        headers = result_set.get('headers', [])
        rows = result_set.get('rowSet', [])

        parsed_data = []

        for row in rows:
            if len(row) != len(headers):
                logger.warning(f"Row length {len(row)} doesn't match headers length {len(headers)}")
                continue

            record = dict(zip(headers, row))

            # Convert to our standardized format
            parsed_record = {
                'season_id': record.get('SEASON_ID'),
                'player_id': record.get('PLAYER_ID'),
                'player_name': record.get('PLAYER_NAME'),
                'team_id': record.get('TEAM_ID'),
                'team_abbreviation': record.get('TEAM_ABBREVIATION'),
                'team_name': record.get('TEAM_NAME'),
                'play_type': record.get('PLAY_TYPE'),
                'type_grouping': record.get('TYPE_GROUPING'),
                'percentile': record.get('PERCENTILE'),
                'games_played': record.get('GP'),
                'possession_percentage': record.get('POSS_PCT'),
                'points_per_possession': record.get('PPP'),
                'field_goal_percentage': record.get('FG_PCT'),
                'free_throw_possession_percentage': record.get('FT_POSS_PCT'),
                'turnover_possession_percentage': record.get('TOV_POSS_PCT'),
                'shot_foul_possession_percentage': record.get('SF_POSS_PCT'),
                'plus_one_possession_percentage': record.get('PLUSONE_POSS_PCT'),
                'score_possession_percentage': record.get('SCORE_POSS_PCT'),
                'effective_field_goal_percentage': record.get('EFG_PCT'),
                'possessions': record.get('POSS'),
                'points': record.get('PTS'),
                'field_goals_made': record.get('FGM'),
                'field_goals_attempted': record.get('FGA'),
                'field_goals_missed': record.get('FGMX')
            }

            parsed_data.append(parsed_record)

        return parsed_data

    def extract_season_from_season_id(self, season_id: str) -> str:
        """
        Extract season string from season_id.

        Args:
            season_id: Season ID like "22024"

        Returns:
            Season string like "2024-25"
        """
        if not season_id or len(season_id) < 5:
            return "2024-25"  # Default fallback

        # Season ID format: "2" + "2024" = "22024" for 2024-25 season
        year = season_id[1:5]
        next_year = str(int(year) + 1)[-2:]  # Get last 2 digits
        return f"{year}-{next_year}"


# Example usage and testing
if __name__ == "__main__":
    client = SynergyPlaytypesClient()

    # Test single play type
    print("Testing single play type fetch...")
    try:
        data = client.get_player_playtype_stats(play_type="Isolation")
        parsed = client.parse_playtype_response(data)
        print(f"Found {len(parsed)} records for Isolation play type")

        if parsed:
            print("Sample record:")
            print(parsed[0])

    except Exception as e:
        print(f"Test failed: {e}")

    # Test all play types (commented out to avoid rate limiting)
    # print("\nTesting all play types...")
    # all_data = client.get_all_playtype_stats_for_season()
    # for play_type, data in all_data.items():
    #     parsed = client.parse_playtype_response(data)
    #     print(f"{play_type}: {len(parsed)} records")
