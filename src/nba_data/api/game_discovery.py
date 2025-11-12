"""
NBA Game Discovery Module

Systematically discovers available NBA games for play-by-play data collection.
Supports both regular season and playoff games across multiple seasons.
"""

import logging
import requests
import time
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import json
import random

logger = logging.getLogger(__name__)


class NBAGameDiscovery:
    """Discovers available NBA games for play-by-play data collection."""

    def __init__(self, cache_dir: str = "data/cache"):
        """Initialize game discovery with caching."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()

        # Set headers to match working requests
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'application/json',
        })

        # Rate limiting
        self.request_delay = 1.0  # seconds between requests

    def discover_all_games(self, seasons: List[str] = None, season_types: List[str] = None,
                          max_games_per_season: int = None) -> Dict[str, List[str]]:
        """
        Discover all available games across specified seasons and types.

        Args:
            seasons: List of seasons (e.g., ['2023-24', '2024-25'])
            season_types: List of season types (['regular', 'playoffs'])
            max_games_per_season: Maximum games to discover per season/type

        Returns:
            Dictionary mapping season_type to list of game IDs
        """
        if seasons is None:
            seasons = ['2023-24', '2024-25']

        if season_types is None:
            season_types = ['regular', 'playoffs']

        discovered_games = {}

        for season in seasons:
            for season_type in season_types:
                logger.info(f"Discovering {season_type} games for {season}...")

                games = self._discover_season_games(season, season_type, max_games_per_season)

                key = f"{season}_{season_type}"
                discovered_games[key] = games

                logger.info(f"Found {len(games)} {season_type} games for {season}")

                # Small delay between season discoveries
                time.sleep(0.5)

        return discovered_games

    def _discover_season_games(self, season: str, season_type: str, max_games: int = None) -> List[str]:
        """
        Discover games for a specific season and type.

        Args:
            season: Season string (e.g., '2023-24')
            season_type: 'regular' or 'playoffs'
            max_games: Maximum games to discover

        Returns:
            List of valid game IDs
        """
        available_games = []

        if season_type == 'regular':
            # Regular season games: 002YYYNZZZ format
            season_prefix = season[:4]  # e.g., '2023'
            season_code = season_prefix[2:]  # e.g., '23'

            # Try game numbers from 0001 to 1300 (NBA has ~1230 regular season games)
            max_attempts = min(max_games, 1300) if max_games else 1300

            for game_num in range(1, max_attempts + 1):
                game_id = f"002{season_code}000{game_num:02d}"
                if self._check_game_exists(game_id):
                    available_games.append(game_id)
                else:
                    # If we hit a gap of 10 missing games, assume we're done with this season
                    if len(available_games) > 0 and game_num > len(available_games) + 10:
                        break

        elif season_type == 'playoffs':
            # Playoff games: 004YYYR0GG format
            season_prefix = season[:4]
            season_code = season_prefix[2:]

            # Try all playoff rounds and games
            for round_num in range(1, 5):  # Rounds 1-4
                for game_num in range(1, 8):  # Games 1-7 per series
                    game_id = f"004{season_code}{round_num}0{game_num:02d}"
                    if self._check_game_exists(game_id):
                        available_games.append(game_id)

        return available_games

    def _check_game_exists(self, game_id: str) -> bool:
        """
        Check if a game exists by attempting to fetch its play-by-play data.

        Args:
            game_id: NBA game ID

        Returns:
            True if game exists and has data
        """
        cache_key = f"game_check_{game_id}"
        cache_file = self.cache_dir / f"{cache_key}.json"

        # Check cache first
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_result = json.load(f)
                return cached_result.get('exists', False)
            except:
                pass  # Cache corrupted, check again

        # Extract season year from game ID (format: 002YY...)
        season_year = 2000 + int(game_id[3:5])  # Convert YY to 20YY

        # Check if game exists via API
        url = f"https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/{season_year}/scores/pbp/{game_id}_full_pbp.json"

        try:
            time.sleep(self.request_delay)  # Rate limiting

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check if we got actual game data
            exists = self._validate_game_data(data)

            # Cache result
            cache_data = {
                'exists': exists,
                'checked_at': datetime.now().isoformat(),
                'game_id': game_id
            }

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)

            return exists

        except requests.exceptions.RequestException:
            # Cache negative result to avoid repeated failed requests
            cache_data = {
                'exists': False,
                'checked_at': datetime.now().isoformat(),
                'game_id': game_id,
                'error': 'request_failed'
            }

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)

            return False

    def _validate_game_data(self, data: Dict) -> bool:
        """
        Validate that the game data contains actual play-by-play information.

        Args:
            data: JSON response from NBA API

        Returns:
            True if data contains valid game information
        """
        try:
            game_data = data.get('g', {})
            if not game_data:
                return False

            # Check for basic game metadata
            game_id = game_data.get('gid')
            if not game_id:
                return False

            # Check for play data
            periods = game_data.get('pd', [])
            if not periods:
                return False

            # Check if at least one period has plays
            total_plays = 0
            for period in periods:
                plays = period.get('pla', [])
                total_plays += len(plays)

            # Must have at least some plays to be considered valid
            return total_plays > 0

        except Exception as e:
            logger.debug(f"Error validating game data: {e}")
            return False

    def get_season_summary(self, discovered_games: Dict[str, List[str]]) -> Dict[str, Dict]:
        """
        Generate summary statistics for discovered games.

        Args:
            discovered_games: Dictionary from discover_all_games()

        Returns:
            Summary statistics
        """
        summary = {}

        for key, games in discovered_games.items():
            season, season_type = key.split('_', 1)

            summary[key] = {
                'season': season,
                'season_type': season_type,
                'total_games': len(games),
                'sample_games': games[:5] if games else []
            }

        return summary

    def save_game_list(self, discovered_games: Dict[str, List[str]], filename: str = None) -> str:
        """
        Save discovered games to a JSON file.

        Args:
            discovered_games: Dictionary from discover_all_games()
            filename: Optional filename, defaults to timestamped name

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"discovered_games_{timestamp}.json"

        filepath = self.cache_dir / filename

        data = {
            'discovery_timestamp': datetime.now().isoformat(),
            'games': discovered_games,
            'summary': self.get_season_summary(discovered_games)
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {sum(len(games) for games in discovered_games.values())} games to {filepath}")
        return str(filepath)


# Convenience functions
def discover_nba_games(seasons: List[str] = None, season_types: List[str] = None,
                      max_games_per_season: int = None) -> Dict[str, List[str]]:
    """
    Convenience function to discover NBA games.

    Args:
        seasons: List of seasons
        season_types: List of season types
        max_games_per_season: Max games per season

    Returns:
        Dictionary of discovered games
    """
    discovery = NBAGameDiscovery()
    return discovery.discover_all_games(seasons, season_types, max_games_per_season)


def load_game_list(filepath: str) -> Dict[str, List[str]]:
    """
    Load previously discovered games from file.

    Args:
        filepath: Path to JSON file

    Returns:
        Dictionary of games
    """
    with open(filepath, 'r') as f:
        data = json.load(f)

    return data['games']


if __name__ == "__main__":
    # Test the discovery system
    import argparse

    parser = argparse.ArgumentParser(description="Discover available NBA games")
    parser.add_argument("--seasons", nargs="+", default=["2023-24"], help="Seasons to discover")
    parser.add_argument("--season-types", nargs="+", default=["regular"], help="Season types")
    parser.add_argument("--max-games", type=int, default=50, help="Max games per season")

    args = parser.parse_args()

    discovery = NBAGameDiscovery()
    games = discovery.discover_all_games(args.seasons, args.season_types, args.max_games)

    # Print summary
    summary = discovery.get_season_summary(games)
    print("\n🎯 Game Discovery Results:")
    print("=" * 40)

    for key, stats in summary.items():
        print(f"{key}: {stats['total_games']} games")
        if stats['sample_games']:
            print(f"  Sample: {', '.join(stats['sample_games'][:3])}")

    # Save results
    filepath = discovery.save_game_list(games)
    print(f"\n📁 Results saved to: {filepath}")
