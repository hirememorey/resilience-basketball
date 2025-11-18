"""
NBA Shot Dashboard API Client

Fetches player shot statistics filtered by closest defender distance ranges.
This provides crucial data for analyzing how players perform under different defensive pressure levels.
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


class ShotDashboardClient:
    """Client for fetching NBA shot dashboard statistics with closest defender distance filtering."""

    # Closest defender distance ranges available in NBA Stats API
    DEFENDER_DISTANCE_RANGES = [
        '0-2 Feet - Very Tight',
        '2-4 Feet - Tight',
        '4-6 Feet - Open',
        '6+ Feet - Wide Open'
    ]

    # Shot distance ranges for filtering
    SHOT_DISTANCE_RANGES = [
        '>=0.0',
        '>=6.0',
        '>=10.0',
        '>=16.0',
        '>=22.0'
    ]

    # Shot clock ranges for filtering (seconds remaining)
    # NBA Stats API uses descriptive labels for shot clock ranges
    SHOT_CLOCK_RANGES = [
        '22-18 Very Early',      # Still early (most time)
        '18-15 Early',           # Early mid
        '15-7 Average',          # Average time
        '7-4 Late',              # Late shot clock
        '4-0 Very Late'          # Very late/rushed shots
    ]

    # Dribble ranges for filtering (number of dribbles before shot)
    DRIBBLE_RANGES = [
        '0 Dribbles',      # Catch & Shoot
        '1 Dribble',
        '2 Dribbles',
        '3-6 Dribbles',    # Moderate creation
        '7+ Dribbles'      # Extensive creation
    ]

    def __init__(self, rate_limit_delay: float = 1.0):
        """Initialize the shot dashboard client."""
        self.rate_limit_delay = rate_limit_delay
        self.base_client = NBAStatsClient()

    def get_player_shot_dashboard_stats(
        self,
        season_year: str = "2024-25",
        season_type: str = "Regular Season",
        close_def_dist_range: str = "",
        shot_clock_range: str = "",
        dribble_range: str = "",
        shot_dist_range: str = "",
        per_mode: str = "PerGame"
    ) -> Dict[str, Any]:
        """
        Fetch player shot dashboard statistics with various filtering options.

        Args:
            season_year: Season in format "2024-25"
            season_type: "Regular Season" or "Playoffs"
            close_def_dist_range: Defender distance range from DEFENDER_DISTANCE_RANGES (optional)
            shot_clock_range: Shot clock range from SHOT_CLOCK_RANGES (optional)
            dribble_range: Dribble range from DRIBBLE_RANGES (optional)
            shot_dist_range: Shot distance range filter (optional)
            per_mode: "PerGame" or "Totals"

        Returns:
            Dictionary containing API response data
        """
        if close_def_dist_range and close_def_dist_range not in self.DEFENDER_DISTANCE_RANGES:
            raise ValueError(f"Invalid close_def_dist_range: {close_def_dist_range}. Must be one of {self.DEFENDER_DISTANCE_RANGES}")

        if shot_clock_range and shot_clock_range not in self.SHOT_CLOCK_RANGES:
            raise ValueError(f"Invalid shot_clock_range: {shot_clock_range}. Must be one of {self.SHOT_CLOCK_RANGES}")

        if dribble_range and dribble_range not in self.DRIBBLE_RANGES:
            raise ValueError(f"Invalid dribble_range: {dribble_range}. Must be one of {self.DRIBBLE_RANGES}")

        # Create cache key
        cache_key = f"shot_dashboard_{season_year}_{season_type}_{close_def_dist_range}_{shot_clock_range}_{dribble_range}_{shot_dist_range}_{per_mode}".replace(' ', '_').replace('>=', 'gte').replace('-', '_')
        cache_path = self.base_client._get_cache_path("shotdashboard", {
            'Season': season_year,
            'SeasonType': season_type,
            'CloseDefDistRange': close_def_dist_range,
            'ShotClockRange': shot_clock_range,
            'DribbleRange': dribble_range,
            'ShotDistRange': shot_dist_range,
            'PerMode': per_mode
        })

        # Check cache first
        cached_data = self.base_client._read_from_cache(cache_path)
        if cached_data:
            filter_desc = []
            if close_def_dist_range:
                filter_desc.append(f"{close_def_dist_range} defense")
            if shot_clock_range:
                filter_desc.append(f"{shot_clock_range} shot clock")
            if dribble_range:
                filter_desc.append(f"{dribble_range}")
            if shot_dist_range:
                filter_desc.append(f"{shot_dist_range} shot distance")
            filter_str = ", ".join(filter_desc) if filter_desc else "all shots"
            logger.info(f"Loaded cached data for {filter_str}")
            return cached_data

        # Make API request
        url = "https://stats.nba.com/stats/leaguedashplayerptshot"

        params = {
            'LeagueID': '00',
            'Season': season_year,
            'SeasonType': season_type,
            'PerMode': per_mode,
            'CloseDefDistRange': close_def_dist_range,
            'ShotClockRange': shot_clock_range,
            'DribbleRange': dribble_range,
            'ShotDistRange': shot_dist_range,
            'PlayerOrTeam': 'Player',  # Get individual player data
            'LastNGames': '0',
            'Month': '0',
            'OpponentTeamID': '0',
            'Period': '0',
            'TeamID': '0',
            'VsConference': '',
            'VsDivision': '',
            'Location': '',
            'Outcome': '',
            'PORound': '0',
            'SeasonSegment': '',
            'DateFrom': '',
            'DateTo': '',
            'GameSegment': '',
            'GameScope': '',
            'PlayerExperience': '',
            'PlayerPosition': '',
            'StarterBench': '',
            'DraftYear': '',
            'DraftPick': '',
            'College': '',
            'Country': '',
            'Height': '',
            'Weight': '',
            'TouchTimeRange': '',
            'GeneralRange': ''
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

        filter_desc = []
        if close_def_dist_range:
            filter_desc.append(f"{close_def_dist_range} defense")
        if shot_clock_range:
            filter_desc.append(f"{shot_clock_range} shot clock")
        if dribble_range:
            filter_desc.append(f"{dribble_range}")
        if shot_dist_range:
            filter_desc.append(f"{shot_dist_range} shot distance")
        filter_str = ", ".join(filter_desc) if filter_desc else "all shots"
        logger.info(f"Fetching shot dashboard data for {filter_str} ({season_year} {season_type})")

        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Validate response structure
            if 'resultSets' not in data or not data['resultSets']:
                logger.warning(f"No resultSets found in response for {close_def_dist_range}")
                return {'resultSets': []}

            # Cache the successful response
            self.base_client._write_to_cache(cache_path, data)

            # Rate limiting
            time.sleep(self.rate_limit_delay)

            return data

        except requests.RequestException as e:
            logger.error(f"Request failed for {close_def_dist_range}: {e}")
            raise
        except ValueError as e:
            logger.error(f"JSON parsing failed for {close_def_dist_range}: {e}")
            raise

    def get_all_defender_distances_for_season(
        self,
        season_year: str = "2024-25",
        season_type: str = "Regular Season",
        shot_dist_range: str = ">=10.0",
        per_mode: str = "PerGame"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch shot dashboard statistics for all defender distance ranges in a season.

        Returns:
            Dictionary with defender_distance as key and API response as value
        """
        results = {}

        for def_dist_range in self.DEFENDER_DISTANCE_RANGES:
            try:
                logger.info(f"Fetching data for defender distance: {def_dist_range}")
                data = self.get_player_shot_dashboard_stats(
                    season_year=season_year,
                    season_type=season_type,
                    close_def_dist_range=def_dist_range,
                    shot_dist_range=shot_dist_range,
                    per_mode=per_mode
                )
                results[def_dist_range] = data

            except Exception as e:
                logger.error(f"Failed to fetch data for {def_dist_range}: {e}")
                results[def_dist_range] = {'error': str(e), 'resultSets': []}

        return results

    def get_all_shot_clock_ranges_for_season(
        self,
        season_year: str = "2024-25",
        season_type: str = "Regular Season",
        shot_dist_range: str = ">=10.0",
        per_mode: str = "PerGame"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch shot dashboard statistics for all shot clock ranges in a season.

        Returns:
            Dictionary with shot_clock_range as key and API response as value
        """
        results = {}

        for shot_clock_range in self.SHOT_CLOCK_RANGES:
            try:
                logger.info(f"Fetching data for shot clock range: {shot_clock_range}")
                data = self.get_player_shot_dashboard_stats(
                    season_year=season_year,
                    season_type=season_type,
                    shot_clock_range=shot_clock_range,
                    shot_dist_range=shot_dist_range,
                    per_mode=per_mode
                )
                results[shot_clock_range] = data

            except Exception as e:
                logger.error(f"Failed to fetch data for {shot_clock_range}: {e}")
                results[shot_clock_range] = {'error': str(e), 'resultSets': []}

        return results

    def get_all_dribble_ranges_for_season(
        self,
        season_year: str = "2024-25",
        season_type: str = "Regular Season",
        shot_dist_range: str = ">=10.0",
        per_mode: str = "PerGame"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch shot dashboard statistics for all dribble ranges in a season.

        Returns:
            Dictionary with dribble_range as key and API response as value
        """
        results = {}

        for dribble_range in self.DRIBBLE_RANGES:
            try:
                logger.info(f"Fetching data for dribble range: {dribble_range}")
                data = self.get_player_shot_dashboard_stats(
                    season_year=season_year,
                    season_type=season_type,
                    dribble_range=dribble_range,
                    shot_dist_range=shot_dist_range,
                    per_mode=per_mode
                )
                results[dribble_range] = data

            except Exception as e:
                logger.error(f"Failed to fetch data for {dribble_range}: {e}")
                results[dribble_range] = {'error': str(e), 'resultSets': []}

        return results

    def get_all_shot_dashboard_combinations(
        self,
        season_year: str = "2024-25",
        season_type: str = "Regular Season",
        shot_dist_range: str = ">=10.0",
        per_mode: str = "PerGame"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch shot dashboard statistics for all combinations of defender distance and shot clock ranges.

        Returns:
            Dictionary with combination key and API response as value
        """
        results = {}

        for def_dist_range in self.DEFENDER_DISTANCE_RANGES:
            for shot_clock_range in self.SHOT_CLOCK_RANGES:
                combo_key = f"{def_dist_range}_{shot_clock_range}"
                try:
                    logger.info(f"Fetching data for {combo_key}")
                    data = self.get_player_shot_dashboard_stats(
                        season_year=season_year,
                        season_type=season_type,
                        close_def_dist_range=def_dist_range,
                        shot_clock_range=shot_clock_range,
                        shot_dist_range=shot_dist_range,
                        per_mode=per_mode
                    )
                    results[combo_key] = data

                except Exception as e:
                    logger.error(f"Failed to fetch data for {combo_key}: {e}")
                    results[combo_key] = {'error': str(e), 'resultSets': []}

        return results

    def parse_shot_dashboard_response(self, response_data: Dict[str, Any], close_def_dist_range: str = "", shot_clock_range: str = "", dribble_range: str = "", season: str = "2024-25") -> List[Dict[str, Any]]:
        """
        Parse the API response into a list of player shot dashboard records.

        Args:
            response_data: Raw API response dictionary
            close_def_dist_range: Defender distance range filter used
            shot_clock_range: Shot clock range filter used
            dribble_range: Dribble range filter used
            season: Season year (e.g., "2024-25")

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
                'season': season,
                'player_id': record.get('PLAYER_ID'),
                'player_name': record.get('PLAYER_NAME'),
                'team_id': record.get('PLAYER_LAST_TEAM_ID'),
                'team_abbreviation': record.get('PLAYER_LAST_TEAM_ABBREVIATION'),
                'team_name': None,  # Not provided in this API
                'age': record.get('AGE'),
                'gp': record.get('GP'),
                'g': record.get('G'),
                'fga_frequency': record.get('FGA_FREQUENCY'),
                'fgm': record.get('FGM'),
                'fga': record.get('FGA'),
                'fg_pct': record.get('FG_PCT'),
                'efg_pct': record.get('EFG_PCT'),
                'fg2a_frequency': record.get('FG2A_FREQUENCY'),
                'fg2m': record.get('FG2M'),
                'fg2a': record.get('FG2A'),
                'fg2_pct': record.get('FG2_PCT'),
                'fg3a_frequency': record.get('FG3A_FREQUENCY'),
                'fg3m': record.get('FG3M'),
                'fg3a': record.get('FG3A'),
                'fg3_pct': record.get('FG3_PCT'),
                'shot_dist_range': '>=10.0',  # From API parameters
                'close_def_dist_range': close_def_dist_range,
                'shot_clock_range': shot_clock_range,
                'dribble_range': dribble_range
            }

            parsed_data.append(parsed_record)

        return parsed_data


# Example usage and testing
if __name__ == "__main__":
    client = ShotDashboardClient()

    # Test single dribble range
    print("Testing single dribble range fetch...")
    try:
        data = client.get_player_shot_dashboard_stats(dribble_range="0 Dribbles")
        parsed = client.parse_shot_dashboard_response(data, dribble_range="0 Dribbles")
        print(f"Found {len(parsed)} records for 0 Dribbles (Catch & Shoot)")

        if parsed:
            print("Sample record:")
            print(parsed[0])

    except Exception as e:
        print(f"Test failed: {e}")

    # Test all defender distances (commented out to avoid rate limiting)
    # print("\nTesting all defender distances...")
    # all_data = client.get_all_defender_distances_for_season()
    # for def_dist, data in all_data.items():
    #     parsed = client.parse_shot_dashboard_response(data, def_dist)
    #     print(f"{def_dist}: {len(parsed)} records")
