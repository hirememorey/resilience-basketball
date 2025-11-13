"""NBA Stats API client for making direct HTTP requests."""

import time
import random
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib
import json
import os
from pathlib import Path

# Add tenacity for advanced retry logic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

logger = logging.getLogger(__name__)

CACHE_DIR = Path("data/cache")
CACHE_EXPIRATION = timedelta(days=1)


class EmptyResponseError(Exception):
    """Raised when API returns 200 OK but with empty data."""
    pass


class UpstreamDataMissingError(Exception):
    """Raised when required upstream data is missing."""
    pass


class NBAStatsClient:
    """Client for making requests to the NBA Stats API."""

    def __init__(self):
        """Initialize the NBA Stats API client."""
        self.base_url = "https://stats.nba.com/stats"
        self.session = requests.Session()

        # Configure retry strategy with exponential backoff and jitter
        retry_strategy = Retry(
            total=10,  # Increased number of retries
            backoff_factor=2,  # Increased backoff factor
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            respect_retry_after_header=True
        )

        # Create an adapter with the retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Set default headers to match working curl request
        self.session.headers.update({
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://www.nba.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.nba.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        })

        # Rate limiting parameters
        self.requests_per_minute = 100
        self.request_interval = 60.0 / self.requests_per_minute
        self.last_request_time = 0.0
        self.min_request_interval = 5.0  # Minimum time between requests in seconds

        # Adaptive rate limiting state
        self.consecutive_failures = 0
        self.consecutive_rate_limits = 0
        self.last_successful_request = time.time()
        self.adaptive_mode = False

        # Global timeout for all requests
        self.timeout = 60  # Sensible default timeout

        # Ensure cache directory exists
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, endpoint: str, params: Optional[Dict]) -> Path:
        """Generate a unique file path for caching based on endpoint and params."""
        hasher = hashlib.md5()
        # Use a consistent representation of params for hashing
        if params:
            encoded_params = json.dumps(params, sort_keys=True).encode('utf-8')
            hasher.update(encoded_params)

        # Include endpoint in the hash to avoid collisions for same params on different endpoints
        hasher.update(endpoint.encode('utf-8'))

        return CACHE_DIR / f"{hasher.hexdigest()}.json"

    def _read_from_cache(self, cache_path: Path) -> Optional[Dict]:
        """Read data from cache if it exists and is not expired."""
        if cache_path.exists():
            modified_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
            if datetime.now() - modified_time < CACHE_EXPIRATION:
                logger.info(f"Cache hit. Reading from {cache_path}")
                with open(cache_path, 'r') as f:
                    return json.load(f)
        logger.info(f"Cache miss for {cache_path}")
        return None

    def _write_to_cache(self, cache_path: Path, data: Dict):
        """Write data to the cache."""
        logger.info(f"Writing to cache: {cache_path}")
        with open(cache_path, 'w') as f:
            json.dump(data, f)

    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits by waiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        # Adaptive rate limiting based on recent failures
        if self.adaptive_mode:
            adaptive_interval = self.min_request_interval * (2 ** min(self.consecutive_failures, 3))
            min_interval = max(adaptive_interval, self.min_request_interval)
        else:
            min_interval = self.min_request_interval

        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            logger.debug(f"Adaptive rate limiting: waiting {sleep_time:.1f}s (consecutive failures: {self.consecutive_failures})")
            time.sleep(sleep_time)

        # Add a random jitter to the request interval
        jitter = random.uniform(0.5, 1.5)
        time.sleep(jitter)

        self.last_request_time = time.time()

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Handle rate limiting by waiting for the specified time."""
        if response.status_code == 429:  # Too Many Requests
            retry_after = int(response.headers.get("Retry-After", 30))
            self.consecutive_rate_limits += 1
            self.consecutive_failures += 1

            # Enable adaptive mode after multiple rate limits
            if self.consecutive_rate_limits >= 3:
                self.adaptive_mode = True
                logger.warning(f"Multiple rate limits detected ({self.consecutive_rate_limits}). Enabling adaptive mode.")

            logging.warning(f"Rate limited (429). Waiting {retry_after} seconds...")
            time.sleep(retry_after)
        elif response.status_code >= 500:  # Server errors
            self.consecutive_failures += 1
            if self.consecutive_failures >= 5:
                self.adaptive_mode = True
                logger.warning(f"Multiple server errors detected ({self.consecutive_failures}). Enabling adaptive mode.")
        else:
            # Reset counters on successful request
            self.consecutive_failures = 0
            self.consecutive_rate_limits = 0
            self.adaptive_mode = False
            self.last_successful_request = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the NBA Stats API with caching and rate limiting."""
        # Check cache first
        cache_path = self._get_cache_path(endpoint, params)
        cached_data = self._read_from_cache(cache_path)
        if cached_data:
            return cached_data

        # Rate limiting
        self._wait_for_rate_limit()

        # Make the request
        url = f"{self.base_url}/{endpoint}"
        logger.info(f"Making request to {url}")

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Cache the response
            self._write_to_cache(cache_path, data)

            # Reset failure counters on success
            self._update_request_success()

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            self._handle_rate_limit(response if 'response' in locals() else None)
            raise

    def _update_request_success(self):
        """Update state after a successful request."""
        self.consecutive_failures = 0
        self.consecutive_rate_limits = 0
        self.adaptive_mode = False

    # Core API methods
    def get_league_player_base_stats(self, season: str = "2024-25", season_type: str = "Regular Season") -> Dict[str, Any]:
        """Get basic player statistics."""
        endpoint = "leaguedashplayerstats"
        params = {
            "College": "",
            "Conference": "",
            "Country": "",
            "DateFrom": "",
            "DateTo": "",
            "Division": "",
            "DraftPick": "",
            "DraftYear": "",
            "GameScope": "",
            "GameSegment": "",
            "Height": "",
            "LastNGames": "0",
            "LeagueID": "00",
            "Location": "",
            "MeasureType": "Base",
            "Month": "0",
            "OpponentTeamID": "0",
            "Outcome": "",
            "PORound": "0",
            "PaceAdjust": "N",
            "PerMode": "PerGame",
            "Period": "0",
            "PlayerExperience": "",
            "PlayerPosition": "",
            "PlusMinus": "N",
            "Rank": "N",
            "Season": season,
            "SeasonSegment": "",
            "SeasonType": season_type,
            "ShotClockRange": "",
            "StarterBench": "",
            "TeamID": "0",
            "TwoWay": "0",
            "VsConference": "",
            "VsDivision": "",
            "Weight": ""
        }
        return self._make_request(endpoint, params)

    def get_league_player_advanced_stats(self, season: str = "2024-25", season_type: str = "Regular Season") -> Dict[str, Any]:
        """Get advanced player statistics."""
        endpoint = "leaguedashplayerstats"
        params = {
            "College": "",
            "Conference": "",
            "Country": "",
            "DateFrom": "",
            "DateTo": "",
            "Division": "",
            "DraftPick": "",
            "DraftYear": "",
            "GameScope": "",
            "GameSegment": "",
            "Height": "",
            "LastNGames": "0",
            "LeagueID": "00",
            "Location": "",
            "MeasureType": "Advanced",
            "Month": "0",
            "OpponentTeamID": "0",
            "Outcome": "",
            "PORound": "0",
            "PaceAdjust": "N",
            "PerMode": "PerGame",
            "Period": "0",
            "PlayerExperience": "",
            "PlayerPosition": "",
            "PlusMinus": "N",
            "Rank": "N",
            "Season": season,
            "SeasonSegment": "",
            "SeasonType": season_type,
            "ShotClockRange": "",
            "StarterBench": "",
            "TeamID": "0",
            "TwoWay": "0",
            "VsConference": "",
            "VsDivision": "",
            "Weight": ""
        }
        return self._make_request(endpoint, params)

    def get_league_player_tracking_stats(self, season: str = "2024-25", pt_measure_type: str = "Drives") -> Dict[str, Any]:
        """Get player tracking statistics."""
        endpoint = "leaguedashptstats"
        params = {
            "College": "",
            "Conference": "",
            "Country": "",
            "DateFrom": "",
            "DateTo": "",
            "Division": "",
            "DraftPick": "",
            "DraftYear": "",
            "GameScope": "",
            "GameSegment": "",
            "Height": "",
            "LastNGames": "0",
            "LeagueID": "00",
            "Location": "",
            "Month": "0",
            "OpponentTeamID": "0",
            "Outcome": "",
            "PORound": "0",
            "PaceAdjust": "N",
            "PerMode": "PerGame",
            "Period": "0",
            "PlayerExperience": "",
            "PlayerOrTeam": "Player",  # CRITICAL: This gets individual player data, not team aggregates
            "PlayerPosition": "",
            "PlusMinus": "N",
            "PtMeasureType": pt_measure_type,
            "Rank": "N",
            "Season": season,
            "SeasonSegment": "",
            "SeasonType": "Regular Season",
            "ShotClockRange": "",
            "StarterBench": "",
            "TeamID": "0",
            "TwoWay": "0",
            "VsConference": "",
            "VsDivision": "",
            "Weight": ""
        }
        return self._make_request(endpoint, params)

    def get_common_player_info(self, player_id: int) -> Dict[str, Any]:
        """Get basic player information."""
        endpoint = "commonplayerinfo"
        params = {
            "LeagueID": "00",
            "PlayerID": str(player_id)
        }
        return self._make_request(endpoint, params)

    def get_league_hustle_stats(self, season: str = "2024-25") -> Dict[str, Any]:
        """Get player hustle statistics."""
        endpoint = "leaguehustlestatsplayer"
        params = {
            "College": "",
            "Conference": "",
            "Country": "",
            "DateFrom": "",
            "DateTo": "",
            "Division": "",
            "DraftPick": "",
            "DraftYear": "",
            "GameScope": "",
            "GameSegment": "",
            "Height": "",
            "LastNGames": "0",
            "LeagueID": "00",
            "Location": "",
            "Month": "0",
            "OpponentTeamID": "0",
            "Outcome": "",
            "PORound": "0",
            "PaceAdjust": "N",
            "PerMode": "PerGame",
            "Period": "0",
            "PlayerExperience": "",
            "PlayerPosition": "",
            "PlusMinus": "N",
            "Rank": "N",
            "Season": season,
            "SeasonSegment": "",
            "SeasonType": "Regular Season",
            "ShotClockRange": "",
            "StarterBench": "",
            "TeamID": "0",
            "TwoWay": "0",
            "VsConference": "",
            "VsDivision": "",
            "Weight": ""
        }
        return self._make_request(endpoint, params)

    # Playoff stats methods
    def get_league_player_playoff_base_stats(self, season: str = "2024-25") -> Dict[str, Any]:
        """Get basic player playoff statistics."""
        endpoint = "leaguedashplayerstats"
        params = {
            "College": "",
            "Conference": "",
            "Country": "",
            "DateFrom": "",
            "DateTo": "",
            "Division": "",
            "DraftPick": "",
            "DraftYear": "",
            "GameScope": "",
            "GameSegment": "",
            "Height": "",
            "LastNGames": "0",
            "LeagueID": "00",
            "Location": "",
            "MeasureType": "Base",
            "Month": "0",
            "OpponentTeamID": "0",
            "Outcome": "",
            "PORound": "0",
            "PaceAdjust": "N",
            "PerMode": "PerGame",
            "Period": "0",
            "PlayerExperience": "",
            "PlayerPosition": "",
            "PlusMinus": "N",
            "Rank": "N",
            "Season": season,
            "SeasonSegment": "",
            "SeasonType": "Playoffs",
            "ShotClockRange": "",
            "StarterBench": "",
            "TeamID": "0",
            "TwoWay": "0",
            "VsConference": "",
            "VsDivision": "",
            "Weight": ""
        }
        return self._make_request(endpoint, params)

    def get_league_player_playoff_advanced_stats(self, season: str = "2024-25") -> Dict[str, Any]:
        """Get advanced player playoff statistics."""
        endpoint = "leaguedashplayerstats"
        params = {
            "College": "",
            "Conference": "",
            "Country": "",
            "DateFrom": "",
            "DateTo": "",
            "Division": "",
            "DraftPick": "",
            "DraftYear": "",
            "GameScope": "",
            "GameSegment": "",
            "Height": "",
            "LastNGames": "0",
            "LeagueID": "00",
            "Location": "",
            "MeasureType": "Advanced",
            "Month": "0",
            "OpponentTeamID": "0",
            "Outcome": "",
            "PORound": "0",
            "PaceAdjust": "N",
            "PerMode": "PerGame",
            "Period": "0",
            "PlayerExperience": "",
            "PlayerPosition": "",
            "PlusMinus": "N",
            "Rank": "N",
            "Season": season,
            "SeasonSegment": "",
            "SeasonType": "Playoffs",
            "ShotClockRange": "",
            "StarterBench": "",
            "TeamID": "0",
            "TwoWay": "0",
            "VsConference": "",
            "VsDivision": "",
            "Weight": ""
        }
        return self._make_request(endpoint, params)

    def get_league_player_playoff_tracking_stats(self, season: str = "2024-25", pt_measure_type: str = "Drives") -> Dict[str, Any]:
        """Get player playoff tracking statistics."""
        endpoint = "leaguedashptstats"
        params = {
            "College": "",
            "Conference": "",
            "Country": "",
            "DateFrom": "",
            "DateTo": "",
            "Division": "",
            "DraftPick": "",
            "DraftYear": "",
            "GameScope": "",
            "GameSegment": "",
            "Height": "",
            "LastNGames": "0",
            "LeagueID": "00",
            "Location": "",
            "Month": "0",
            "OpponentTeamID": "0",
            "Outcome": "",
            "PORound": "0",
            "PaceAdjust": "N",
            "PerMode": "PerGame",
            "Period": "0",
            "PlayerExperience": "",
            "PlayerOrTeam": "Player",  # CRITICAL: This gets individual player data, not team aggregates
            "PlayerPosition": "",
            "PlusMinus": "N",
            "PtMeasureType": pt_measure_type,
            "Rank": "N",
            "Season": season,
            "SeasonSegment": "",
            "SeasonType": "Playoffs",
            "ShotClockRange": "",
            "StarterBench": "",
            "TeamID": "0",
            "TwoWay": "0",
            "VsConference": "",
            "VsDivision": "",
            "Weight": ""
        }
        return self._make_request(endpoint, params)

    def get_league_player_playoff_shot_stats(self, season: str = "2024-25") -> Dict[str, Any]:
        """Get player playoff shot statistics (from the cURL example provided)."""
        endpoint = "leaguedashplayerptshot"
        params = {
            "CloseDefDistRange": "",
            "College": "",
            "Conference": "",
            "Country": "",
            "DateFrom": "",
            "DateTo": "",
            "Division": "",
            "DraftPick": "",
            "DraftYear": "",
            "DribbleRange": "",
            "GameScope": "",
            "GameSegment": "",
            "GeneralRange": "Overall",
            "Height": "",
            "ISTRound": "",
            "LastNGames": "0",
            "LeagueID": "00",
            "Location": "",
            "Month": "0",
            "OpponentTeamID": "0",
            "Outcome": "",
            "PORound": "0",
            "PaceAdjust": "N",
            "PerMode": "PerGame",
            "Period": "0",
            "PlayerExperience": "",
            "PlayerPosition": "",
            "PlusMinus": "N",
            "Rank": "N",
            "Season": season,
            "SeasonSegment": "",
            "SeasonType": "Playoffs",
            "ShotClockRange": "",
            "ShotDistRange": "",
            "StarterBench": "",
            "TeamID": "0",
            "TouchTimeRange": "",
            "VsConference": "",
            "VsDivision": "",
            "Weight": ""
        }
        return self._make_request(endpoint, params)

    def get_player_shot_chart(self, player_id: int, season: str, season_type: str = "Regular Season") -> Dict[str, Any]:
        """Get shot chart data for a specific player and season."""
        endpoint = "shotchartdetail"
        params = {
            "PlayerID": player_id,
            "Season": season,
            "SeasonType": season_type,
            "TeamID": 0,
            "GameID": "",
            "Outcome": "",
            "Location": "",
            "Month": 0,
            "SeasonSegment": "",
            "DateFrom": "",
            "DateTo": "",
            "OpponentTeamID": 0,
            "VsConference": "",
            "VsDivision": "",
            "PlayerPosition": "",
            "GameSegment": "",
            "Period": 0,
            "LastNGames": 0,
            "ContextMeasure": "FGA",
            "RookieYear": ""
        }
        return self._make_request(endpoint, params)

    def get_play_by_play(self, game_id: str, start_period: int = 1, end_period: int = 10) -> Dict[str, Any]:
        """Get play-by-play data for a specific game."""
        endpoint = "playbyplayv2"
        params = {
            "GameID": game_id,
            "StartPeriod": str(start_period),
            "EndPeriod": str(end_period)
        }
        return self._make_request(endpoint, params)

    def get_game_rotation(self, game_id: str) -> Dict[str, Any]:
        """Get player rotation data (who was on court when) for a specific game."""
        endpoint = "gamerotation"
        params = {
            "GameID": game_id,
            "LeagueID": "00"
        }
        return self._make_request(endpoint, params)


# Convenience functions
def create_nba_stats_client() -> NBAStatsClient:
    """Create a new NBAStatsClient instance."""
    return NBAStatsClient()


if __name__ == "__main__":
    # Test the client
    client = create_nba_stats_client()

    print("Testing NBA Stats API client...")

    try:
        # Test basic stats
        print("Fetching basic player stats...")
        data = client.get_league_player_base_stats()
        print(f"✅ Successfully fetched data for {len(data.get('resultSets', [{}])[0].get('rowSet', []))} players")

        # Test advanced stats
        print("Fetching advanced player stats...")
        data = client.get_league_player_advanced_stats()
        print(f"✅ Successfully fetched advanced data for {len(data.get('resultSets', [{}])[0].get('rowSet', []))} players")

        # Test shot chart data for a specific player
        print("Fetching shot chart data for LeBron James...")
        # Note: Using a known player ID for a stable test case
        data = client.get_player_shot_chart(player_id=2544, season="2023-24")
        print(f"✅ Successfully fetched {len(data.get('resultSets', [{}])[0].get('rowSet', []))} shots for LeBron James")

    except Exception as e:
        print(f"❌ Error testing API client: {e}")
