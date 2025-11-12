"""
NBA Possession-Level Data Fetcher

Fetches and parses play-by-play data to create granular possession-level
analytics for playoff resilience analysis.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib

from .nba_stats_client import NBAStatsClient

logger = logging.getLogger(__name__)

@dataclass
class PossessionEvent:
    """Represents a single event within a possession."""
    event_id: str
    possession_id: str
    event_number: int
    clock_time: str
    elapsed_seconds: float
    player_id: Optional[int]
    team_id: int
    opponent_team_id: int
    event_type: str
    event_subtype: Optional[str] = None
    shot_type: Optional[str] = None
    shot_distance: Optional[int] = None
    shot_result: Optional[str] = None
    points_scored: int = 0
    assist_player_id: Optional[int] = None
    block_player_id: Optional[int] = None
    steal_player_id: Optional[int] = None
    turnover_type: Optional[str] = None
    foul_type: Optional[str] = None
    rebound_type: Optional[str] = None
    location_x: Optional[float] = None
    location_y: Optional[float] = None
    defender_player_id: Optional[int] = None
    touches_before_action: Optional[int] = None
    dribbles_before_action: Optional[int] = None

@dataclass
class Possession:
    """Represents a complete possession with all events."""
    possession_id: str
    game_id: str
    period: int
    clock_time_start: str
    clock_time_end: str
    home_team_id: int
    away_team_id: int
    offensive_team_id: int
    defensive_team_id: int
    possession_start: float
    possession_end: float
    duration_seconds: float
    points_scored: int
    expected_points: Optional[float] = None
    possession_type: str = "offensive"
    start_reason: Optional[str] = None
    end_reason: Optional[str] = None
    events: List[PossessionEvent] = None
    lineups: List[Dict] = None  # List of {player_id, team_id, position}
    matchups: List[Dict] = None  # List of {offensive_player_id, defensive_player_id, ...}

    def __post_init__(self):
        if self.events is None:
            self.events = []
        if self.lineups is None:
            self.lineups = []
        if self.matchups is None:
            self.matchups = []

class PossessionFetcher:
    """
    Fetches and parses NBA play-by-play data into possession-level analytics.

    This enables granular analysis of player decision-making and adaptability
    under pressure - the core of playoff resilience.
    """

    def __init__(self, client: Optional[NBAStatsClient] = None):
        """Initialize the possession fetcher."""
        self.client = client or NBAStatsClient()

        # Event type mappings for parsing
        self.event_type_map = {
            1: "shot", 2: "shot", 3: "free_throw", 4: "rebound", 5: "turnover",
            6: "foul", 7: "violation", 8: "substitution", 9: "timeout", 10: "jump_ball",
            11: "ejection", 12: "start_period", 13: "end_period", 14: "memo",
            15: "tv_timeout", 16: "clock_stoppage", 17: "foul_personal", 18: "foul_technical",
            19: "foul_double", 20: "foul_loose_ball", 21: "foul_offensive"
        }

    def fetch_game_possessions(self, game_id: str) -> List[Possession]:
        """
        Fetch and parse all possessions for a specific game.

        Args:
            game_id: NBA game ID (format: 0022400001)

        Returns:
            List of Possession objects with complete event sequences
        """
        logger.info(f"Fetching possession data for game {game_id}")

        try:
            # Extract season from game_id (format: 002YY00001 where YY is season)
            season_year = 2000 + int(game_id[3:5])  # Convert 2-digit year to 4-digit
            season = f"{season_year}-{season_year + 1}"

            # Get play-by-play data from data.nba.com
            pbp_data = self._get_pbp_from_data_api(game_id, season)

            # Parse into possessions
            possessions = self._parse_possessions_from_pbp(pbp_data)

            logger.info(f"Successfully parsed {len(possessions)} possessions for game {game_id}")
            return possessions

        except Exception as e:
            logger.error(f"Failed to fetch possessions for game {game_id}: {e}")
            raise

    def _get_pbp_from_data_api(self, game_id: str, season: str) -> Dict:
        """
        Fetch play-by-play data from data.nba.com API.

        Args:
            game_id: NBA game ID
            season: Season in format "2023-24"

        Returns:
            Play-by-play data dictionary
        """
        import requests

        url = f"https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/{season[:4]}/scores/pbp/{game_id}_full_pbp.json"

        logger.info(f"Fetching PBP data from: {url}")

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()
        return data

    def _parse_possessions_from_pbp(self, pbp_data: Dict) -> List[Possession]:
        """
        Parse play-by-play data from data.nba.com into possession sequences.

        This is the core logic that transforms raw play-by-play events
        into meaningful possession units for resilience analysis.
        """
        possessions = []

        # Extract game metadata
        game_data = pbp_data.get('g', {})
        game_id = game_data.get('gid')

        if not game_id:
            logger.warning("Could not extract game_id from PBP data")
            return possessions

        # Extract team IDs from play data (they're embedded in individual plays)
        team_ids = self._extract_team_ids_from_plays(game_data.get('pd', []))
        home_team_id = team_ids[0] if len(team_ids) > 0 else 0
        away_team_id = team_ids[1] if len(team_ids) > 1 else 0

        logger.info(f"Parsing possessions for game {game_id} (Home: {home_team_id}, Away: {away_team_id})")

        # Get periods data
        periods_data = game_data.get('pd', [])
        if not periods_data:
            logger.warning("No period data found in PBP response")
            return possessions

        # Process each period
        for period_data in periods_data:
            period_num = period_data.get('p', 0)
            plays = period_data.get('pla', [])

            logger.info(f"Processing period {period_num} with {len(plays)} plays")

            # Parse plays into possessions
            possessions.extend(self._parse_period_plays(game_id, period_num, plays, home_team_id, away_team_id))

        logger.info(f"Total possessions parsed: {len(possessions)}")
        return possessions

    def _extract_team_ids_from_plays(self, periods_data: List[Dict]) -> List[int]:
        """Extract unique team IDs from play data."""
        team_ids = set()

        for period_data in periods_data:
            plays = period_data.get('pla', [])
            for play in plays:
                tid = play.get('tid', 0)
                if tid and tid != 0:  # Skip invalid team IDs
                    team_ids.add(tid)

        return sorted(list(team_ids))  # Return sorted for consistent home/away assignment

    def _parse_period_plays(self, game_id: str, period: int, plays: List[Dict],
                           home_team_id: int, away_team_id: int) -> List[Possession]:
        """
        Parse plays from a single period into possession sequences.
        """
        possessions = []
        current_possession = None
        event_sequence = 0

        for play in plays:
            # Extract play data
            event_num = play.get('evt', 0)
            clock_time = play.get('cl', '00:00')
            elapsed_seconds = self._clock_to_seconds(clock_time)
            description = play.get('de', '')
            event_type_id = play.get('etype', 0)
            player_id = play.get('pid', 0) or None
            team_id = play.get('tid', 0)
            home_score = play.get('hs', 0)
            visitor_score = play.get('vs', 0)
            loc_x = play.get('locX', 0)
            loc_y = play.get('locY', 0)
            assist_player_id = play.get('epid') or None

            # Map event type
            event_type = self._map_event_type(event_type_id)

            # Check if this starts a new possession
            if self._is_possession_start(event_type, description):
                # Save previous possession if exists
                if current_possession:
                    self._finalize_possession(current_possession)
                    possessions.append(current_possession)

                # Start new possession
                current_possession = self._create_new_possession_from_play(
                    game_id, period, clock_time, elapsed_seconds, play, home_team_id, away_team_id
                )
                event_sequence = 0

            # Add event to current possession
            if current_possession:
                possession_event = self._create_possession_event_from_play(
                    current_possession.possession_id, play, event_sequence, elapsed_seconds, home_team_id, away_team_id
                )
                if possession_event:
                    current_possession.events.append(possession_event)
                    event_sequence += 1

        # Add final possession
        if current_possession:
            self._finalize_possession(current_possession)
            possessions.append(current_possession)

        return possessions

    def _map_event_type(self, event_type_id: int) -> str:
        """Map data.nba.com event type IDs to our event types."""
        # Map the data.nba.com event types to our standard types
        event_mapping = {
            1: "shot",      # Made shot
            2: "shot",      # Missed shot
            3: "free_throw", # Free throw
            4: "rebound",   # Rebound
            5: "turnover",  # Turnover
            6: "foul",      # Foul
            7: "violation", # Violation
            8: "substitution", # Substitution
            9: "timeout",   # Timeout
            10: "jump_ball", # Jump ball
            12: "start_period", # Start period
            13: "end_period",   # End period
            18: "foul_technical", # Technical foul
            20: "stoppage"   # Stoppage
        }
        return event_mapping.get(event_type_id, "unknown")

    def _create_new_possession_from_play(self, game_id: str, period: int, clock_time: str,
                                       elapsed_seconds: float, play: Dict,
                                       home_team_id: int, away_team_id: int) -> Possession:
        """Create a new possession object from a play event."""
        possession_id = f"{game_id}_{period}_{elapsed_seconds}"

        # Determine offensive team (simplified logic)
        team_id = play.get('tid', 0)
        offensive_team_id = team_id if team_id else home_team_id
        defensive_team_id = away_team_id if offensive_team_id == home_team_id else home_team_id

        return Possession(
            possession_id=possession_id,
            game_id=game_id,
            period=period,
            clock_time_start=clock_time,
            clock_time_end=clock_time,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            offensive_team_id=offensive_team_id,
            defensive_team_id=defensive_team_id,
            possession_start=elapsed_seconds,
            possession_end=elapsed_seconds,
            duration_seconds=0.0,
            points_scored=0,
            start_reason=play.get('de', ''),
            possession_type="offensive"
        )

    def _create_possession_event_from_play(self, possession_id: str, play: Dict,
                                         event_number: int, elapsed_seconds: float,
                                         home_team_id: int, away_team_id: int) -> Optional[PossessionEvent]:
        """Create a possession event from a play."""
        event_id = f"{possession_id}_{event_number}"
        clock_time = play.get('cl', '00:00')
        description = play.get('de', '')

        # Parse shot details if it's a shot
        event_type_id = play.get('etype', 0)
        points_scored = 0

        if event_type_id in [1, 3]:  # Made shot or free throw
            if 'PTS' in description:
                if '3PT' in description or '3pt' in description:
                    points_scored = 3
                elif 'Free Throw' in description:
                    points_scored = 1
                else:
                    points_scored = 2

        # Determine opponent team
        team_id = play.get('tid', 0)
        opponent_team_id = away_team_id if team_id == home_team_id else home_team_id

        return PossessionEvent(
            event_id=event_id,
            possession_id=possession_id,
            event_number=event_number,
            clock_time=clock_time,
            elapsed_seconds=elapsed_seconds,
            player_id=play.get('pid') or None,
            team_id=team_id,
            opponent_team_id=opponent_team_id,
            event_type=self._map_event_type(event_type_id),
            event_subtype="made" if event_type_id == 1 else "missed" if event_type_id == 2 else None,
            shot_result="made" if event_type_id == 1 else "missed" if event_type_id == 2 else None,
            points_scored=points_scored,
            assist_player_id=play.get('epid') or None,
            location_x=play.get('locX'),
            location_y=play.get('locY')
        )

    def _is_possession_start(self, event_type: str, description: str) -> bool:
        """Determine if an event starts a new possession."""
        possession_starters = [
            "shot", "turnover", "foul", "rebound", "jump_ball",
            "start_period", "timeout"
        ]

        # Check event type
        if event_type in possession_starters:
            return True

        # Check description keywords
        start_keywords = [
            "rebound", "steal", "turnover", "makes", "misses",
            "foul", "jump ball", "start of", "enters the game"
        ]

        description_lower = description.lower()
        return any(keyword in description_lower for keyword in start_keywords)

    def _create_new_possession(self, game_id: str, period: int, clock_time: str,
                             elapsed_seconds: float, home_team_id: int, away_team_id: int,
                             event_type: str, description: str) -> Possession:
        """Create a new possession object."""
        possession_id = f"{game_id}_{period}_{elapsed_seconds}"

        # Determine offensive team based on event
        offensive_team_id = self._determine_offensive_team(home_team_id, away_team_id, description)
        defensive_team_id = away_team_id if offensive_team_id == home_team_id else home_team_id

        return Possession(
            possession_id=possession_id,
            game_id=game_id,
            period=period,
            clock_time_start=clock_time,
            clock_time_end=clock_time,  # Will be updated
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            offensive_team_id=offensive_team_id,
            defensive_team_id=defensive_team_id,
            possession_start=elapsed_seconds,
            possession_end=elapsed_seconds,  # Will be updated
            duration_seconds=0.0,  # Will be calculated
            points_scored=0,
            start_reason=event_type,
            possession_type="offensive"
        )

    def _determine_offensive_team(self, home_team_id: int, away_team_id: int, description: str) -> int:
        """Determine which team has the ball based on event description."""
        # Simple heuristic - can be enhanced with more sophisticated logic
        desc_lower = description.lower()

        # Look for team indicators in description
        if "home" in desc_lower:
            return home_team_id
        elif "away" in desc_lower or "visitor" in desc_lower:
            return away_team_id

        # Default to home team (can be refined)
        return home_team_id

    def _parse_event_to_possession_event(self, possession_id: str, event: List, event_number: int,
                                       elapsed_seconds: float) -> Optional[PossessionEvent]:
        """Parse a raw PBP event into a PossessionEvent object."""
        if len(event) < 15:
            return None

        event_id = f"{possession_id}_{event_number}"
        clock_time = event[5] if len(event) > 5 else "00:00"
        event_type_id = event[1] if len(event) > 1 else 0
        event_type = self.event_type_map.get(event_type_id, "unknown")

        player_id = event[12] if len(event) > 12 and event[12] else None
        team_id = event[7] if len(event) > 7 and event[7] else 0
        opponent_team_id = event[10] if len(event) > 10 and event[10] else 0

        # Parse event-specific details
        event_details = self._parse_event_details(event)

        return PossessionEvent(
            event_id=event_id,
            possession_id=possession_id,
            event_number=event_number,
            clock_time=clock_time,
            elapsed_seconds=elapsed_seconds,
            player_id=player_id,
            team_id=team_id,
            opponent_team_id=opponent_team_id,
            event_type=event_type,
            **event_details
        )

    def _parse_event_details(self, event: List) -> Dict[str, Any]:
        """Parse event-specific details based on event type."""
        details = {}

        if len(event) < 20:
            return details

        event_type_id = event[1]
        description = event[6] if len(event) > 6 else ""

        # Shot events
        if event_type_id in [1, 2]:
            details["event_subtype"] = "made" if "makes" in description.lower() else "missed"
            details["shot_result"] = details["event_subtype"]

            # Parse shot type and distance
            if "3PT" in description:
                details["shot_type"] = "3PT"
            elif "Free Throw" in description:
                details["shot_type"] = "FT"
            else:
                details["shot_type"] = "2PT"

            # Extract points scored
            if "makes" in description.lower():
                details["points_scored"] = 3 if "3PT" in description else 2 if "Free Throw" not in description else 1

        # Rebound events
        elif event_type_id == 4:
            details["event_subtype"] = "offensive" if "offensive" in description.lower() else "defensive"
            details["rebound_type"] = details["event_subtype"]

        # Turnover events
        elif event_type_id == 5:
            details["event_subtype"] = "turnover"
            # Could parse specific turnover types

        return details

    def _finalize_possession(self, possession: Possession) -> None:
        """Finalize a possession by calculating duration and end time."""
        if possession.events:
            # Sort events by time (most recent first for end time)
            sorted_events = sorted(possession.events, key=lambda e: e.elapsed_seconds)

            possession.possession_end = sorted_events[-1].elapsed_seconds
            possession.clock_time_end = sorted_events[-1].clock_time
            possession.duration_seconds = possession.possession_end - possession.possession_start

            # Calculate total points scored in possession
            possession.points_scored = sum(event.points_scored for event in possession.events)

    def _clock_to_seconds(self, clock_time: str) -> float:
        """Convert MM:SS clock time to total seconds elapsed in period."""
        try:
            minutes, seconds = map(int, clock_time.split(':'))
            return minutes * 60 + seconds
        except (ValueError, AttributeError):
            return 0.0

    def _get_team_ids_from_game_id(self, game_id: str) -> Tuple[int, int]:
        """Extract team IDs from game ID format."""
        # NBA game IDs are typically 10 digits: SSSTTHHHH
        # Where SSS = season, TT = game type, HHHH = home team
        # This is a simplified extraction - would need proper team ID mapping
        try:
            # For now, return placeholder team IDs
            # In a production system, you'd have a proper mapping
            home_team_id = 1610612747  # Lakers
            away_team_id = 1610612748  # Warriors
            return home_team_id, away_team_id
        except:
            return 1610612747, 1610612748  # Default fallback

# Convenience function
def create_possession_fetcher(client: Optional[NBAStatsClient] = None) -> PossessionFetcher:
    """Create a new PossessionFetcher instance."""
    return PossessionFetcher(client)
