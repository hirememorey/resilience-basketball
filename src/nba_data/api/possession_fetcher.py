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
            # Get play-by-play data
            pbp_data = self.client.get_play_by_play(game_id)

            # Get rotation data for lineups
            rotation_data = self.client.get_game_rotation(game_id)

            # Parse into possessions
            possessions = self._parse_possessions_from_pbp(pbp_data, rotation_data)

            logger.info(f"Successfully parsed {len(possessions)} possessions for game {game_id}")
            return possessions

        except Exception as e:
            logger.error(f"Failed to fetch possessions for game {game_id}: {e}")
            raise

    def _parse_possessions_from_pbp(self, pbp_data: Dict, rotation_data: Dict) -> List[Possession]:
        """
        Parse play-by-play data into possession sequences.

        This is the core logic that transforms raw play-by-play events
        into meaningful possession units for resilience analysis.
        """
        possessions = []

        # Extract game metadata - handle different response formats
        game_id = None
        if "parameters" in pbp_data and "GameID" in pbp_data["parameters"]:
            game_id = pbp_data["parameters"]["GameID"]
        elif isinstance(pbp_data, dict) and "GameID" in pbp_data:
            game_id = pbp_data["GameID"]

        if not game_id:
            logger.warning("Could not extract game_id from PBP data")
            return possessions

        home_team_id = None
        away_team_id = None

        # Get events from play-by-play data
        events = []
        if "resultSets" in pbp_data and len(pbp_data["resultSets"]) > 0:
            events = pbp_data["resultSets"][0].get("rowSet", [])

        if events:
            # Find team IDs from events
            for event in events:
                if len(event) >= 7:  # Ensure we have enough fields
                    if event[6] and home_team_id is None:  # PLAYER1_TEAM_ID
                        home_team_id = event[6]
                    if event[9] and away_team_id is None:  # PLAYER2_TEAM_ID
                        away_team_id = event[9]

            # If we can't determine teams from events, try to parse from game_id
            if not home_team_id or not away_team_id:
                home_team_id, away_team_id = self._get_team_ids_from_game_id(game_id)

        # Parse events into possessions
        current_possession = None
        event_sequence = 0

        for event in events:
            if len(event) < 10:
                continue

            event_num = event[0]
            period = event[3]
            clock_time = event[5]
            elapsed_seconds = self._clock_to_seconds(clock_time)
            event_type_id = event[1]
            event_description = event[6] if len(event) > 6 else ""
            player1_id = event[12] if len(event) > 12 else None
            player1_team_id = event[7] if len(event) > 7 else None
            player2_id = event[13] if len(event) > 13 else None
            player2_team_id = event[10] if len(event) > 10 else None

            # Determine event type
            event_type = self.event_type_map.get(event_type_id, "unknown")

            # Check if this starts a new possession
            if self._is_possession_start(event_type, event_description):
                # Save previous possession if exists
                if current_possession:
                    self._finalize_possession(current_possession)
                    possessions.append(current_possession)

                # Start new possession
                current_possession = self._create_new_possession(
                    game_id, period, clock_time, elapsed_seconds,
                    home_team_id, away_team_id, event_type, event_description
                )
                event_sequence = 0

            # Add event to current possession
            if current_possession:
                possession_event = self._parse_event_to_possession_event(
                    current_possession.possession_id, event, event_sequence,
                    elapsed_seconds
                )
                if possession_event:
                    current_possession.events.append(possession_event)
                    event_sequence += 1

        # Add final possession
        if current_possession:
            self._finalize_possession(current_possession)
            possessions.append(current_possession)

        return possessions

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
