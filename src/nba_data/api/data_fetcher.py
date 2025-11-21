"""
NBA Data Fetcher Module

Provides a unified interface for fetching NBA player data from various
API endpoints, with built-in schema awareness and error handling.
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .nba_stats_client import NBAStatsClient

# Add progress bar support
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Add retry logic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class DataType(Enum):
    """Data types for metrics."""
    COUNT = "count"
    PERCENTAGE = "percentage"
    RATING = "rating"
    TIME = "time"
    STRING = "string"
    CALCULATED = "calculated"
    MISSING = "missing"

@dataclass
class MetricMapping:
    """Represents a metric mapping to its API source."""
    canonical_name: str
    api_source: str
    api_column: str
    endpoint_params: Dict[str, Any]
    data_type: DataType
    required: bool
    notes: str

class DataFetcher:
    """
    Unified data fetcher with schema awareness and error handling.
    """

    def __init__(self, client: Optional[NBAStatsClient] = None):
        """Initialize the data fetcher."""
        self.client = client or NBAStatsClient()
        self.metric_mappings = self._load_metric_mappings()
        self.cache = {}

    def _load_metric_mappings(self) -> Dict[str, MetricMapping]:
        """Load metric mappings for core NBA statistics."""
        # Core metrics that are available and most relevant for playoff resilience
        mappings = {
            # Basic box score stats
            "TEAM_ID": MetricMapping(
                canonical_name="Team ID",
                api_source="leaguedashplayerstats",
                api_column="TEAM_ID",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Team Identifier"
            ),
            "GP": MetricMapping(
                canonical_name="Games Played",
                api_source="leaguedashplayerstats",
                api_column="GP",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Games played"
            ),
            "GS": MetricMapping(
                canonical_name="Games Started",
                api_source="leaguedashplayerstats",
                api_column="GS",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=False,
                notes="Games started"
            ),
            "MIN": MetricMapping(
                canonical_name="Minutes Played",
                api_source="leaguedashplayerstats",
                api_column="MIN",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Minutes played"
            ),
            "PTS": MetricMapping(
                canonical_name="Points",
                api_source="leaguedashplayerstats",
                api_column="PTS",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Total points"
            ),
            "REB": MetricMapping(
                canonical_name="Total Rebounds",
                api_source="leaguedashplayerstats",
                api_column="REB",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Total rebounds"
            ),
            "AST": MetricMapping(
                canonical_name="Assists",
                api_source="leaguedashplayerstats",
                api_column="AST",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Total assists"
            ),
            "STL": MetricMapping(
                canonical_name="Steals",
                api_source="leaguedashplayerstats",
                api_column="STL",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Total steals"
            ),
            "BLK": MetricMapping(
                canonical_name="Blocks",
                api_source="leaguedashplayerstats",
                api_column="BLK",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Total blocks"
            ),
            "TOV": MetricMapping(
                canonical_name="Turnovers",
                api_source="leaguedashplayerstats",
                api_column="TOV",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Total turnovers"
            ),
            "PF": MetricMapping(
                canonical_name="Personal Fouls",
                api_source="leaguedashplayerstats",
                api_column="PF",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Personal fouls"
            ),
            "PLUS_MINUS": MetricMapping(
                canonical_name="Plus Minus",
                api_source="leaguedashplayerstats",
                api_column="PLUS_MINUS",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=False,
                notes="Plus/minus statistic"
            ),

            # Basic shooting and efficiency metrics
            "FTPCT": MetricMapping(
                canonical_name="Free Throw Percentage",
                api_source="leaguedashplayerstats",
                api_column="FT_PCT",
                endpoint_params={"MeasureType": "Base", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.PERCENTAGE,
                required=True,
                notes="Direct mapping from base stats"
            ),
            "TSPCT": MetricMapping(
                canonical_name="True Shooting Percentage",
                api_source="leaguedashplayerstats",
                api_column="TS_PCT",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.PERCENTAGE,
                required=True,
                notes="Direct mapping from advanced stats"
            ),
            "FGPCT": MetricMapping(
                canonical_name="Field Goal Percentage",
                api_source="leaguedashplayerstats",
                api_column="FG_PCT",
                endpoint_params={"MeasureType": "Base", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.PERCENTAGE,
                required=True,
                notes="Direct mapping from base stats"
            ),
            "FG3PCT": MetricMapping(
                canonical_name="Three Point Percentage",
                api_source="leaguedashplayerstats",
                api_column="FG3_PCT",
                endpoint_params={"MeasureType": "Base", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.PERCENTAGE,
                required=True,
                notes="Direct mapping from base stats"
            ),

            # Additional base stats metrics available in the API
            "FGM": MetricMapping(
                canonical_name="Field Goals Made",
                api_source="leaguedashplayerstats",
                api_column="FGM",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Field goals made from base stats"
            ),
            "FGA": MetricMapping(
                canonical_name="Field Goals Attempted",
                api_source="leaguedashplayerstats",
                api_column="FGA",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Field goals attempted from base stats"
            ),
            "FG3M": MetricMapping(
                canonical_name="Three Pointers Made",
                api_source="leaguedashplayerstats",
                api_column="FG3M",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Three pointers made from base stats"
            ),
            "FG3A": MetricMapping(
                canonical_name="Three Pointers Attempted",
                api_source="leaguedashplayerstats",
                api_column="FG3A",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Three pointers attempted from base stats"
            ),
            "FTM": MetricMapping(
                canonical_name="Free Throws Made",
                api_source="leaguedashplayerstats",
                api_column="FTM",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Free throws made from base stats"
            ),
            "FTA": MetricMapping(
                canonical_name="Free Throws Attempted",
                api_source="leaguedashplayerstats",
                api_column="FTA",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Free throws attempted from base stats"
            ),
            "OREB": MetricMapping(
                canonical_name="Offensive Rebounds",
                api_source="leaguedashplayerstats",
                api_column="OREB",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Offensive rebounds from base stats"
            ),
            "DREB": MetricMapping(
                canonical_name="Defensive Rebounds",
                api_source="leaguedashplayerstats",
                api_column="DREB",
                endpoint_params={"MeasureType": "Base", "PerMode": "Totals", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Defensive rebounds from base stats"
            ),

            # Rebounding and playmaking
            "TRBPCT": MetricMapping(
                canonical_name="Total Rebound Percentage",
                api_source="leaguedashplayerstats",
                api_column="REB_PCT",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.PERCENTAGE,
                required=True,
                notes="Direct mapping from advanced stats"
            ),
            "ASTPCT": MetricMapping(
                canonical_name="Assist Percentage",
                api_source="leaguedashplayerstats",
                api_column="AST_PCT",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.PERCENTAGE,
                required=True,
                notes="Direct mapping from advanced stats"
            ),
            "PIE": MetricMapping(
                canonical_name="Player Impact Estimate",
                api_source="leaguedashplayerstats",
                api_column="PIE",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Player Impact Estimate from advanced stats (can be negative)"
            ),

            # Advanced metrics
            "USGPCT": MetricMapping(
                canonical_name="Usage Percentage",
                api_source="leaguedashplayerstats",
                api_column="USG_PCT",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.PERCENTAGE,
                required=True,
                notes="Direct mapping from advanced stats"
            ),
            "ORTG": MetricMapping(
                canonical_name="Offensive Rating",
                api_source="leaguedashplayerstats",
                api_column="OFF_RATING",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.RATING,
                required=True,
                notes="Direct mapping from advanced stats"
            ),
            "DRTG": MetricMapping(
                canonical_name="Defensive Rating",
                api_source="leaguedashplayerstats",
                api_column="DEF_RATING",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.RATING,
                required=True,
                notes="Direct mapping from advanced stats"
            ),
            "NRTG": MetricMapping(
                canonical_name="Net Rating",
                api_source="leaguedashplayerstats",
                api_column="NET_RATING",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.RATING,
                required=True,
                notes="Direct mapping from advanced stats"
            ),

            # Additional advanced metrics available in the API
            "AGE": MetricMapping(
                canonical_name="Player Age",
                api_source="leaguedashplayerstats",
                api_column="AGE",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Player age from advanced stats"
            ),
            "GP_ADV": MetricMapping(
                canonical_name="Games Played (Advanced)",
                api_source="leaguedashplayerstats",
                api_column="GP",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Games played from advanced stats"
            ),
            "WINS": MetricMapping(
                canonical_name="Wins",
                api_source="leaguedashplayerstats",
                api_column="W",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Team wins from advanced stats"
            ),
            "LOSSES": MetricMapping(
                canonical_name="Losses",
                api_source="leaguedashplayerstats",
                api_column="L",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Team losses from advanced stats"
            ),
            "WIN_PCT": MetricMapping(
                canonical_name="Win Percentage",
                api_source="leaguedashplayerstats",
                api_column="W_PCT",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.PERCENTAGE,
                required=True,
                notes="Win percentage from advanced stats"
            ),
            "MIN_ADV": MetricMapping(
                canonical_name="Minutes Played (Advanced)",
                api_source="leaguedashplayerstats",
                api_column="MIN",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Minutes played from advanced stats"
            ),

            # Additional advanced metrics available in the API
            "AST_TO": MetricMapping(
                canonical_name="Assist to Turnover Ratio",
                api_source="leaguedashplayerstats",
                api_column="AST_TO",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Assist to turnover ratio from advanced stats"
            ),
            "AST_RATIO": MetricMapping(
                canonical_name="Assist Ratio",
                api_source="leaguedashplayerstats",
                api_column="AST_RATIO",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Assist ratio from advanced stats"
            ),
            "OREB_PCT": MetricMapping(
                canonical_name="Offensive Rebound Percentage",
                api_source="leaguedashplayerstats",
                api_column="OREB_PCT",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.PERCENTAGE,
                required=True,
                notes="Offensive rebound percentage from advanced stats"
            ),
            "DREB_PCT": MetricMapping(
                canonical_name="Defensive Rebound Percentage",
                api_source="leaguedashplayerstats",
                api_column="DREB_PCT",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.PERCENTAGE,
                required=True,
                notes="Defensive rebound percentage from advanced stats"
            ),
            "TOV_PCT": MetricMapping(
                canonical_name="Turnover Percentage",
                api_source="leaguedashplayerstats",
                api_column="TM_TOV_PCT",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Turnover percentage from advanced stats (can exceed 100%)"
            ),
            "EFG_PCT": MetricMapping(
                canonical_name="Effective Field Goal Percentage",
                api_source="leaguedashplayerstats",
                api_column="EFG_PCT",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Effective field goal percentage from advanced stats (can exceed 100%)"
            ),
            "PACE_ADV": MetricMapping(
                canonical_name="Pace",
                api_source="leaguedashplayerstats",
                api_column="PACE",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Pace from advanced stats"
            ),

            # Tracking metrics - Drives
            "DRIVES": MetricMapping(
                canonical_name="Drives",
                api_source="leaguedashptstats",
                api_column="DRIVES",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_FGM": MetricMapping(
                canonical_name="Drive Field Goals Made",
                api_source="leaguedashptstats",
                api_column="DRIVE_FGM",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_FGA": MetricMapping(
                canonical_name="Drive Field Goals Attempted",
                api_source="leaguedashptstats",
                api_column="DRIVE_FGA",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_FG_PCT": MetricMapping(
                canonical_name="Drive Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="DRIVE_FG_PCT",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_FTM": MetricMapping(
                canonical_name="Drive Free Throws Made",
                api_source="leaguedashptstats",
                api_column="DRIVE_FTM",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_FTA": MetricMapping(
                canonical_name="Drive Free Throws Attempted",
                api_source="leaguedashptstats",
                api_column="DRIVE_FTA",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_FT_PCT": MetricMapping(
                canonical_name="Drive Free Throw Percentage",
                api_source="leaguedashptstats",
                api_column="DRIVE_FT_PCT",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_PTS": MetricMapping(
                canonical_name="Drive Points",
                api_source="leaguedashptstats",
                api_column="DRIVE_PTS",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_PTS_PCT": MetricMapping(
                canonical_name="Drive Points Percentage",
                api_source="leaguedashptstats",
                api_column="DRIVE_PTS_PCT",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_PASSES": MetricMapping(
                canonical_name="Drive Passes",
                api_source="leaguedashptstats",
                api_column="DRIVE_PASSES",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_PASSES_PCT": MetricMapping(
                canonical_name="Drive Passes Percentage",
                api_source="leaguedashptstats",
                api_column="DRIVE_PASSES_PCT",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_AST": MetricMapping(
                canonical_name="Drive Assists",
                api_source="leaguedashptstats",
                api_column="DRIVE_AST",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_AST_PCT": MetricMapping(
                canonical_name="Drive Assists Percentage",
                api_source="leaguedashptstats",
                api_column="DRIVE_AST_PCT",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_TOV": MetricMapping(
                canonical_name="Drive Turnovers",
                api_source="leaguedashptstats",
                api_column="DRIVE_TOV",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_TOV_PCT": MetricMapping(
                canonical_name="Drive Turnovers Percentage",
                api_source="leaguedashptstats",
                api_column="DRIVE_TOV_PCT",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_PF": MetricMapping(
                canonical_name="Drive Personal Fouls",
                api_source="leaguedashptstats",
                api_column="DRIVE_PF",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "DRIVE_PF_PCT": MetricMapping(
                canonical_name="Drive Personal Fouls Percentage",
                api_source="leaguedashptstats",
                api_column="DRIVE_PF_PCT",
                endpoint_params={"PtMeasureType": "Drives"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),

            # Tracking metrics - Catch and Shoot
            "CATCH_SHOOT_FGM": MetricMapping(
                canonical_name="Catch Shoot Field Goals Made",
                api_source="leaguedashptstats",
                api_column="CATCH_SHOOT_FGM",
                endpoint_params={"PtMeasureType": "CatchShoot"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "CATCH_SHOOT_FGA": MetricMapping(
                canonical_name="Catch Shoot Field Goals Attempted",
                api_source="leaguedashptstats",
                api_column="CATCH_SHOOT_FGA",
                endpoint_params={"PtMeasureType": "CatchShoot"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "CATCH_SHOOT_FG_PCT": MetricMapping(
                canonical_name="Catch Shoot Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="CATCH_SHOOT_FG_PCT",
                endpoint_params={"PtMeasureType": "CatchShoot"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "CATCH_SHOOT_PTS": MetricMapping(
                canonical_name="Catch Shoot Points",
                api_source="leaguedashptstats",
                api_column="CATCH_SHOOT_PTS",
                endpoint_params={"PtMeasureType": "CatchShoot"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "CATCH_SHOOT_FG3M": MetricMapping(
                canonical_name="Catch Shoot Three Pointers Made",
                api_source="leaguedashptstats",
                api_column="CATCH_SHOOT_FG3M",
                endpoint_params={"PtMeasureType": "CatchShoot"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "CATCH_SHOOT_FG3A": MetricMapping(
                canonical_name="Catch Shoot Three Pointers Attempted",
                api_source="leaguedashptstats",
                api_column="CATCH_SHOOT_FG3A",
                endpoint_params={"PtMeasureType": "CatchShoot"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "CATCH_SHOOT_FG3_PCT": MetricMapping(
                canonical_name="Catch Shoot Three Point Percentage",
                api_source="leaguedashptstats",
                api_column="CATCH_SHOOT_FG3_PCT",
                endpoint_params={"PtMeasureType": "CatchShoot"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "CATCH_SHOOT_EFG_PCT": MetricMapping(
                canonical_name="Catch Shoot Effective Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="CATCH_SHOOT_EFG_PCT",
                endpoint_params={"PtMeasureType": "CatchShoot"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),

            # Tracking metrics - Pull Up Shots
            "PULL_UP_FGM": MetricMapping(
                canonical_name="Pull Up Field Goals Made",
                api_source="leaguedashptstats",
                api_column="PULL_UP_FGM",
                endpoint_params={"PtMeasureType": "PullUpShot"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PULL_UP_FGA": MetricMapping(
                canonical_name="Pull Up Field Goals Attempted",
                api_source="leaguedashptstats",
                api_column="PULL_UP_FGA",
                endpoint_params={"PtMeasureType": "PullUpShot"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PULL_UP_FG_PCT": MetricMapping(
                canonical_name="Pull Up Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="PULL_UP_FG_PCT",
                endpoint_params={"PtMeasureType": "PullUpShot"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PULL_UP_PTS": MetricMapping(
                canonical_name="Pull Up Points",
                api_source="leaguedashptstats",
                api_column="PULL_UP_PTS",
                endpoint_params={"PtMeasureType": "PullUpShot"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PULL_UP_FG3M": MetricMapping(
                canonical_name="Pull Up Three Pointers Made",
                api_source="leaguedashptstats",
                api_column="PULL_UP_FG3M",
                endpoint_params={"PtMeasureType": "PullUpShot"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PULL_UP_FG3A": MetricMapping(
                canonical_name="Pull Up Three Pointers Attempted",
                api_source="leaguedashptstats",
                api_column="PULL_UP_FG3A",
                endpoint_params={"PtMeasureType": "PullUpShot"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PULL_UP_FG3_PCT": MetricMapping(
                canonical_name="Pull Up Three Point Percentage",
                api_source="leaguedashptstats",
                api_column="PULL_UP_FG3_PCT",
                endpoint_params={"PtMeasureType": "PullUpShot"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PULL_UP_EFG_PCT": MetricMapping(
                canonical_name="Pull Up Effective Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="PULL_UP_EFG_PCT",
                endpoint_params={"PtMeasureType": "PullUpShot"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),

            # Tracking metrics - Touches (appears in multiple PtMeasureTypes, using PaintTouch as primary)
            "TOUCHES": MetricMapping(
                canonical_name="Touches",
                api_source="leaguedashptstats",
                api_column="TOUCHES",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats - available in PaintTouch, PostTouch, ElbowTouch PtMeasureTypes"
            ),

            # Tracking metrics - Paint Touches
            "PAINT_TOUCHES": MetricMapping(
                canonical_name="Paint Touches",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCHES",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_FGM": MetricMapping(
                canonical_name="Paint Touch Field Goals Made",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_FGM",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_FGA": MetricMapping(
                canonical_name="Paint Touch Field Goals Attempted",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_FGA",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_FG_PCT": MetricMapping(
                canonical_name="Paint Touch Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_FG_PCT",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_FTM": MetricMapping(
                canonical_name="Paint Touch Free Throws Made",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_FTM",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_FTA": MetricMapping(
                canonical_name="Paint Touch Free Throws Attempted",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_FTA",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_FT_PCT": MetricMapping(
                canonical_name="Paint Touch Free Throw Percentage",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_FT_PCT",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_PTS": MetricMapping(
                canonical_name="Paint Touch Points",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_PTS",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_PTS_PCT": MetricMapping(
                canonical_name="Paint Touch Points Percentage",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_PTS_PCT",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_PASSES": MetricMapping(
                canonical_name="Paint Touch Passes",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_PASSES",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_PASSES_PCT": MetricMapping(
                canonical_name="Paint Touch Passes Percentage",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_PASSES_PCT",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_AST": MetricMapping(
                canonical_name="Paint Touch Assists",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_AST",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_AST_PCT": MetricMapping(
                canonical_name="Paint Touch Assists Percentage",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_AST_PCT",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_TOV": MetricMapping(
                canonical_name="Paint Touch Turnovers",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_TOV",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_TOV_PCT": MetricMapping(
                canonical_name="Paint Touch Turnovers Percentage",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_TOV_PCT",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_FOULS": MetricMapping(
                canonical_name="Paint Touch Personal Fouls",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_FOULS",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "PAINT_TOUCH_FOULS_PCT": MetricMapping(
                canonical_name="Paint Touch Personal Fouls Percentage",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_FOULS_PCT",
                endpoint_params={"PtMeasureType": "PaintTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),

            # Tracking metrics - Post Touches
            "POST_TOUCHES": MetricMapping(
                canonical_name="Post Touches",
                api_source="leaguedashptstats",
                api_column="POST_TOUCHES",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_FGM": MetricMapping(
                canonical_name="Post Touch Field Goals Made",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_FGM",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_FGA": MetricMapping(
                canonical_name="Post Touch Field Goals Attempted",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_FGA",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_FG_PCT": MetricMapping(
                canonical_name="Post Touch Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_FG_PCT",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_FTM": MetricMapping(
                canonical_name="Post Touch Free Throws Made",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_FTM",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_FTA": MetricMapping(
                canonical_name="Post Touch Free Throws Attempted",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_FTA",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_FT_PCT": MetricMapping(
                canonical_name="Post Touch Free Throw Percentage",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_FT_PCT",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_PTS": MetricMapping(
                canonical_name="Post Touch Points",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_PTS",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_PTS_PCT": MetricMapping(
                canonical_name="Post Touch Points Percentage",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_PTS_PCT",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_PASSES": MetricMapping(
                canonical_name="Post Touch Passes",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_PASSES",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_PASSES_PCT": MetricMapping(
                canonical_name="Post Touch Passes Percentage",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_PASSES_PCT",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_AST": MetricMapping(
                canonical_name="Post Touch Assists",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_AST",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_AST_PCT": MetricMapping(
                canonical_name="Post Touch Assists Percentage",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_AST_PCT",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_TOV": MetricMapping(
                canonical_name="Post Touch Turnovers",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_TOV",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_TOV_PCT": MetricMapping(
                canonical_name="Post Touch Turnovers Percentage",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_TOV_PCT",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_FOULS": MetricMapping(
                canonical_name="Post Touch Personal Fouls",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_FOULS",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "POST_TOUCH_FOULS_PCT": MetricMapping(
                canonical_name="Post Touch Personal Fouls Percentage",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_FOULS_PCT",
                endpoint_params={"PtMeasureType": "PostTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),

            # Tracking metrics - Elbow Touches
            "ELBOW_TOUCHES": MetricMapping(
                canonical_name="Elbow Touches",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCHES",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_FGM": MetricMapping(
                canonical_name="Elbow Touch Field Goals Made",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_FGM",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_FGA": MetricMapping(
                canonical_name="Elbow Touch Field Goals Attempted",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_FGA",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_FG_PCT": MetricMapping(
                canonical_name="Elbow Touch Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_FG_PCT",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_FTM": MetricMapping(
                canonical_name="Elbow Touch Free Throws Made",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_FTM",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_FTA": MetricMapping(
                canonical_name="Elbow Touch Free Throws Attempted",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_FTA",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_FT_PCT": MetricMapping(
                canonical_name="Elbow Touch Free Throw Percentage",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_FT_PCT",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_PTS": MetricMapping(
                canonical_name="Elbow Touch Points",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_PTS",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_PASSES": MetricMapping(
                canonical_name="Elbow Touch Passes",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_PASSES",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_AST": MetricMapping(
                canonical_name="Elbow Touch Assists",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_AST",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_AST_PCT": MetricMapping(
                canonical_name="Elbow Touch Assists Percentage",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_AST_PCT",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_TOV": MetricMapping(
                canonical_name="Elbow Touch Turnovers",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_TOV",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_TOV_PCT": MetricMapping(
                canonical_name="Elbow Touch Turnovers Percentage",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_TOV_PCT",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_FOULS": MetricMapping(
                canonical_name="Elbow Touch Personal Fouls",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_FOULS",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_PASSES_PCT": MetricMapping(
                canonical_name="Elbow Touch Passes Percentage",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_PASSES_PCT",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_FOULS_PCT": MetricMapping(
                canonical_name="Elbow Touch Personal Fouls Percentage",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_FOULS_PCT",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),
            "ELBOW_TOUCH_PTS_PCT": MetricMapping(
                canonical_name="Elbow Touch Points Percentage",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_PTS_PCT",
                endpoint_params={"PtMeasureType": "ElbowTouch"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Direct mapping from tracking stats"
            ),

            # Tracking metrics - Efficiency (contains points by play type)
            "EFF_PTS": MetricMapping(
                canonical_name="Efficiency Points",
                api_source="leaguedashptstats",
                api_column="POINTS",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.COUNT,
                required=False,
                notes="Total efficiency points from tracking stats"
            ),
            "EFF_DRIVE_PTS": MetricMapping(
                canonical_name="Efficiency Drive Points",
                api_source="leaguedashptstats",
                api_column="DRIVE_PTS",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.COUNT,
                required=False,
                notes="Drive efficiency points from tracking stats"
            ),
            "EFF_DRIVE_FG_PCT": MetricMapping(
                canonical_name="Efficiency Drive Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="DRIVE_FG_PCT",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Drive efficiency FG% from tracking stats"
            ),
            "EFF_CATCH_SHOOT_PTS": MetricMapping(
                canonical_name="Efficiency Catch Shoot Points",
                api_source="leaguedashptstats",
                api_column="CATCH_SHOOT_PTS",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.COUNT,
                required=False,
                notes="Catch shoot efficiency points from tracking stats"
            ),
            "EFF_CATCH_SHOOT_FG_PCT": MetricMapping(
                canonical_name="Efficiency Catch Shoot Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="CATCH_SHOOT_FG_PCT",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Catch shoot efficiency FG% from tracking stats"
            ),
            "EFF_PULL_UP_PTS": MetricMapping(
                canonical_name="Efficiency Pull Up Points",
                api_source="leaguedashptstats",
                api_column="PULL_UP_PTS",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.COUNT,
                required=False,
                notes="Pull up efficiency points from tracking stats"
            ),
            "EFF_PULL_UP_FG_PCT": MetricMapping(
                canonical_name="Efficiency Pull Up Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="PULL_UP_FG_PCT",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Pull up efficiency FG% from tracking stats"
            ),
            "EFF_PAINT_TOUCH_PTS": MetricMapping(
                canonical_name="Efficiency Paint Touch Points",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_PTS",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.COUNT,
                required=False,
                notes="Paint touch efficiency points from tracking stats"
            ),
            "EFF_PAINT_TOUCH_FG_PCT": MetricMapping(
                canonical_name="Efficiency Paint Touch Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="PAINT_TOUCH_FG_PCT",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Paint touch efficiency FG% from tracking stats"
            ),
            "EFF_POST_TOUCH_PTS": MetricMapping(
                canonical_name="Efficiency Post Touch Points",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_PTS",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.COUNT,
                required=False,
                notes="Post touch efficiency points from tracking stats"
            ),
            "EFF_POST_TOUCH_FG_PCT": MetricMapping(
                canonical_name="Efficiency Post Touch Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="POST_TOUCH_FG_PCT",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Post touch efficiency FG% from tracking stats"
            ),
            "EFF_ELBOW_TOUCH_PTS": MetricMapping(
                canonical_name="Efficiency Elbow Touch Points",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_PTS",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.COUNT,
                required=False,
                notes="Elbow touch efficiency points from tracking stats"
            ),
            "EFF_ELBOW_TOUCH_FG_PCT": MetricMapping(
                canonical_name="Efficiency Elbow Touch Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="ELBOW_TOUCH_FG_PCT",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Elbow touch efficiency FG% from tracking stats"
            ),
            "EFF_FG_PCT": MetricMapping(
                canonical_name="Efficiency Field Goal Percentage",
                api_source="leaguedashptstats",
                api_column="EFF_FG_PCT",
                endpoint_params={"PtMeasureType": "Efficiency"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Overall efficiency FG% from tracking stats"
            ),

            # Speed and Distance metrics (SpeedDistance PtMeasureType)
            "DIST_FEET": MetricMapping(
                canonical_name="Distance Traveled (Feet)",
                api_source="leaguedashptstats",
                api_column="DIST_FEET",
                endpoint_params={"PtMeasureType": "SpeedDistance"},
                data_type=DataType.COUNT,
                required=False,
                notes="Total distance traveled in feet during games"
            ),
            "DIST_MILES": MetricMapping(
                canonical_name="Distance Traveled (Miles)",
                api_source="leaguedashptstats",
                api_column="DIST_MILES",
                endpoint_params={"PtMeasureType": "SpeedDistance"},
                data_type=DataType.COUNT,
                required=False,
                notes="Total distance traveled in miles during games"
            ),
            "DIST_MILES_OFF": MetricMapping(
                canonical_name="Distance Traveled Offense (Miles)",
                api_source="leaguedashptstats",
                api_column="DIST_MILES_OFF",
                endpoint_params={"PtMeasureType": "SpeedDistance"},
                data_type=DataType.COUNT,
                required=False,
                notes="Distance traveled in miles on offense"
            ),
            "DIST_MILES_DEF": MetricMapping(
                canonical_name="Distance Traveled Defense (Miles)",
                api_source="leaguedashptstats",
                api_column="DIST_MILES_DEF",
                endpoint_params={"PtMeasureType": "SpeedDistance"},
                data_type=DataType.COUNT,
                required=False,
                notes="Distance traveled in miles on defense"
            ),
            "AVG_SPEED": MetricMapping(
                canonical_name="Average Speed (MPH)",
                api_source="leaguedashptstats",
                api_column="AVG_SPEED",
                endpoint_params={"PtMeasureType": "SpeedDistance"},
                data_type=DataType.COUNT,
                required=False,
                notes="Average speed in miles per hour"
            ),
            "AVG_SPEED_OFF": MetricMapping(
                canonical_name="Average Speed Offense (MPH)",
                api_source="leaguedashptstats",
                api_column="AVG_SPEED_OFF",
                endpoint_params={"PtMeasureType": "SpeedDistance"},
                data_type=DataType.COUNT,
                required=False,
                notes="Average speed in miles per hour on offense"
            ),
            "AVG_SPEED_DEF": MetricMapping(
                canonical_name="Average Speed Defense (MPH)",
                api_source="leaguedashptstats",
                api_column="AVG_SPEED_DEF",
                endpoint_params={"PtMeasureType": "SpeedDistance"},
                data_type=DataType.COUNT,
                required=False,
                notes="Average speed in miles per hour on defense"
            ),

            # Passing metrics (Passing PtMeasureType)
            "PASSES_MADE": MetricMapping(
                canonical_name="Passes Made",
                api_source="leaguedashptstats",
                api_column="PASSES_MADE",
                endpoint_params={"PtMeasureType": "Passing"},
                data_type=DataType.COUNT,
                required=False,
                notes="Total passes made by player"
            ),
            "PASSES_RECEIVED": MetricMapping(
                canonical_name="Passes Received",
                api_source="leaguedashptstats",
                api_column="PASSES_RECEIVED",
                endpoint_params={"PtMeasureType": "Passing"},
                data_type=DataType.COUNT,
                required=False,
                notes="Total passes received by player"
            ),
            "FT_AST": MetricMapping(
                canonical_name="Free Throw Assists",
                api_source="leaguedashptstats",
                api_column="FT_AST",
                endpoint_params={"PtMeasureType": "Passing"},
                data_type=DataType.COUNT,
                required=False,
                notes="Assists on free throws"
            ),
            "SECONDARY_AST": MetricMapping(
                canonical_name="Secondary Assists",
                api_source="leaguedashptstats",
                api_column="SECONDARY_AST",
                endpoint_params={"PtMeasureType": "Passing"},
                data_type=DataType.COUNT,
                required=False,
                notes="Secondary assists (passes leading to assists)"
            ),
            "POTENTIAL_AST": MetricMapping(
                canonical_name="Potential Assists",
                api_source="leaguedashptstats",
                api_column="POTENTIAL_AST",
                endpoint_params={"PtMeasureType": "Passing"},
                data_type=DataType.COUNT,
                required=False,
                notes="Potential assists (passes that could have led to scores)"
            ),
            "AST_POINTS_CREATED": MetricMapping(
                canonical_name="Assist Points Created",
                api_source="leaguedashptstats",
                api_column="AST_POINTS_CREATED",
                endpoint_params={"PtMeasureType": "Passing"},
                data_type=DataType.COUNT,
                required=False,
                notes="Points created through assists"
            ),
            "AST_ADJ": MetricMapping(
                canonical_name="Adjusted Assists",
                api_source="leaguedashptstats",
                api_column="AST_ADJ",
                endpoint_params={"PtMeasureType": "Passing"},
                data_type=DataType.COUNT,
                required=False,
                notes="Adjusted assist total accounting for secondary assists"
            ),
            "AST_TO_PASS_PCT": MetricMapping(
                canonical_name="Assist to Pass Percentage",
                api_source="leaguedashptstats",
                api_column="AST_TO_PASS_PCT",
                endpoint_params={"PtMeasureType": "Passing"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Percentage of passes that result in assists"
            ),
            "AST_TO_PASS_PCT_ADJ": MetricMapping(
                canonical_name="Adjusted Assist to Pass Percentage",
                api_source="leaguedashptstats",
                api_column="AST_TO_PASS_PCT_ADJ",
                endpoint_params={"PtMeasureType": "Passing"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Adjusted percentage accounting for secondary assists"
            ),

            # Rebounding metrics (Rebounding PtMeasureType)
            "OREB_CONTEST": MetricMapping(
                canonical_name="Offensive Rebounds Contested",
                api_source="leaguedashptstats",
                api_column="OREB_CONTEST",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Contested offensive rebounds"
            ),
            "OREB_UNCONTEST": MetricMapping(
                canonical_name="Offensive Rebounds Uncontested",
                api_source="leaguedashptstats",
                api_column="OREB_UNCONTEST",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Uncontested offensive rebounds"
            ),
            "OREB_CONTEST_PCT": MetricMapping(
                canonical_name="Offensive Rebound Contest Percentage",
                api_source="leaguedashptstats",
                api_column="OREB_CONTEST_PCT",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Percentage of offensive rebounds that were contested"
            ),
            "OREB_CHANCES": MetricMapping(
                canonical_name="Offensive Rebound Chances",
                api_source="leaguedashptstats",
                api_column="OREB_CHANCES",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Total offensive rebound opportunities"
            ),
            "OREB_CHANCE_PCT": MetricMapping(
                canonical_name="Offensive Rebound Chance Percentage",
                api_source="leaguedashptstats",
                api_column="OREB_CHANCE_PCT",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Percentage of offensive rebound chances converted"
            ),
            "OREB_CHANCE_DEFER": MetricMapping(
                canonical_name="Offensive Rebound Chance Deferrals",
                api_source="leaguedashptstats",
                api_column="OREB_CHANCE_DEFER",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Offensive rebound chances deferred to teammates"
            ),
            "OREB_CHANCE_PCT_ADJ": MetricMapping(
                canonical_name="Adjusted Offensive Rebound Chance Percentage",
                api_source="leaguedashptstats",
                api_column="OREB_CHANCE_PCT_ADJ",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Adjusted offensive rebound conversion rate"
            ),
            "AVG_OREB_DIST": MetricMapping(
                canonical_name="Average Offensive Rebound Distance",
                api_source="leaguedashptstats",
                api_column="AVG_OREB_DIST",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Average distance from basket for offensive rebounds"
            ),
            "DREB_CONTEST": MetricMapping(
                canonical_name="Defensive Rebounds Contested",
                api_source="leaguedashptstats",
                api_column="DREB_CONTEST",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Contested defensive rebounds"
            ),
            "DREB_UNCONTEST": MetricMapping(
                canonical_name="Defensive Rebounds Uncontested",
                api_source="leaguedashptstats",
                api_column="DREB_UNCONTEST",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Uncontested defensive rebounds"
            ),
            "DREB_CONTEST_PCT": MetricMapping(
                canonical_name="Defensive Rebound Contest Percentage",
                api_source="leaguedashptstats",
                api_column="DREB_CONTEST_PCT",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Percentage of defensive rebounds that were contested"
            ),
            "DREB_CHANCES": MetricMapping(
                canonical_name="Defensive Rebound Chances",
                api_source="leaguedashptstats",
                api_column="DREB_CHANCES",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Total defensive rebound opportunities"
            ),
            "DREB_CHANCE_PCT": MetricMapping(
                canonical_name="Defensive Rebound Chance Percentage",
                api_source="leaguedashptstats",
                api_column="DREB_CHANCE_PCT",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Percentage of defensive rebound chances converted"
            ),
            "DREB_CHANCE_DEFER": MetricMapping(
                canonical_name="Defensive Rebound Chance Deferrals",
                api_source="leaguedashptstats",
                api_column="DREB_CHANCE_DEFER",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Defensive rebound chances deferred to teammates"
            ),
            "DREB_CHANCE_PCT_ADJ": MetricMapping(
                canonical_name="Adjusted Defensive Rebound Chance Percentage",
                api_source="leaguedashptstats",
                api_column="DREB_CHANCE_PCT_ADJ",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Adjusted defensive rebound conversion rate"
            ),
            "AVG_DREB_DIST": MetricMapping(
                canonical_name="Average Defensive Rebound Distance",
                api_source="leaguedashptstats",
                api_column="AVG_DREB_DIST",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Average distance from basket for defensive rebounds"
            ),
            "REB_CONTEST": MetricMapping(
                canonical_name="Total Rebounds Contested",
                api_source="leaguedashptstats",
                api_column="REB_CONTEST",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Total contested rebounds (offensive + defensive)"
            ),
            "REB_UNCONTEST": MetricMapping(
                canonical_name="Total Rebounds Uncontested",
                api_source="leaguedashptstats",
                api_column="REB_UNCONTEST",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Total uncontested rebounds (offensive + defensive)"
            ),
            "REB_CONTEST_PCT": MetricMapping(
                canonical_name="Total Rebound Contest Percentage",
                api_source="leaguedashptstats",
                api_column="REB_CONTEST_PCT",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Percentage of total rebounds that were contested"
            ),
            "REB_CHANCES": MetricMapping(
                canonical_name="Total Rebound Chances",
                api_source="leaguedashptstats",
                api_column="REB_CHANCES",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Total rebound opportunities (offensive + defensive)"
            ),
            "REB_CHANCE_PCT": MetricMapping(
                canonical_name="Total Rebound Chance Percentage",
                api_source="leaguedashptstats",
                api_column="REB_CHANCE_PCT",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Percentage of total rebound chances converted"
            ),
            "REB_CHANCE_DEFER": MetricMapping(
                canonical_name="Total Rebound Chance Deferrals",
                api_source="leaguedashptstats",
                api_column="REB_CHANCE_DEFER",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Total rebound chances deferred to teammates"
            ),
            "REB_CHANCE_PCT_ADJ": MetricMapping(
                canonical_name="Adjusted Total Rebound Chance Percentage",
                api_source="leaguedashptstats",
                api_column="REB_CHANCE_PCT_ADJ",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.PERCENTAGE,
                required=False,
                notes="Adjusted total rebound conversion rate"
            ),
            "AVG_REB_DIST": MetricMapping(
                canonical_name="Average Total Rebound Distance",
                api_source="leaguedashptstats",
                api_column="AVG_REB_DIST",
                endpoint_params={"PtMeasureType": "Rebounding"},
                data_type=DataType.COUNT,
                required=False,
                notes="Average distance from basket for all rebounds"
            ),

            # Possessions Metrics (For Friction Score)
            "AVG_SEC_PER_TOUCH": MetricMapping(
                canonical_name="Average Seconds Per Touch",
                api_source="leaguedashptstats",
                api_column="AVG_SEC_PER_TOUCH",
                endpoint_params={"PtMeasureType": "Possessions"},
                data_type=DataType.TIME,
                required=False,
                notes="Average duration of a touch"
            ),
            "AVG_DRIBBLES": MetricMapping(
                canonical_name="Average Dribbles Per Touch",
                api_source="leaguedashptstats",
                api_column="AVG_DRIB_PER_TOUCH",
                endpoint_params={"PtMeasureType": "Possessions"},
                data_type=DataType.COUNT,
                required=False,
                notes="Average dribbles per touch"
            ),
            "PTS_PER_TOUCH": MetricMapping(
                canonical_name="Points Per Touch",
                api_source="leaguedashptstats",
                api_column="PTS_PER_TOUCH",
                endpoint_params={"PtMeasureType": "Possessions"},
                data_type=DataType.COUNT,
                required=False,
                notes="Points generated per touch"
            ),
            "TIME_OF_POSS": MetricMapping(
                canonical_name="Time of Possession",
                api_source="leaguedashptstats",
                api_column="TIME_OF_POSS",
                endpoint_params={"PtMeasureType": "Possessions"},
                data_type=DataType.TIME,
                required=False,
                notes="Total time of possession"
            ),
            "FRONT_CT_TOUCHES": MetricMapping(
                canonical_name="Front Court Touches",
                api_source="leaguedashptstats",
                api_column="FRONT_CT_TOUCHES",
                endpoint_params={"PtMeasureType": "Possessions"},
                data_type=DataType.COUNT,
                required=False,
                notes="Touches in front court"
            ),

            # Physical attributes (available ones)
            "HEIGHT": MetricMapping(
                canonical_name="Player Height",
                api_source="commonplayerinfo",
                api_column="HEIGHT",
                endpoint_params={},
                data_type=DataType.STRING,
                required=False,
                notes="Direct mapping from player info"
            ),
            "WEIGHT": MetricMapping(
                canonical_name="Player Weight",
                api_source="commonplayerinfo",
                api_column="WEIGHT",
                endpoint_params={},
                data_type=DataType.COUNT,
                required=False,
                notes="Direct mapping from player info"
            ),

            # Missing metrics (for future reference)
            "AVGDIST": MetricMapping(
                canonical_name="Average Shot Distance",
                api_source="MISSING",
                api_column="MISSING",
                endpoint_params={},
                data_type=DataType.MISSING,
                required=False,
                notes="NOT FOUND in current API - needs investigation"
            ),
            "WINGSPAN": MetricMapping(
                canonical_name="Player Wingspan",
                api_source="MISSING",
                api_column="MISSING",
                endpoint_params={},
                data_type=DataType.MISSING,
                required=False,
                notes="NOT FOUND in current API - may need draft combine data"
            ),
        }
        return mappings

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    def fetch_metric_data(self, metric: str, season: str = "2024-25") -> Optional[Dict[str, Any]]:
        """
        Fetch data for a specific metric.

        Args:
            metric: The canonical metric name
            season: The season to fetch data for

        Returns:
            Dictionary with player data or None if not available
        """
        if metric not in self.metric_mappings:
            logger.error(f"Unknown metric: {metric}")
            return None

        mapping = self.metric_mappings[metric]

        if mapping.data_type == DataType.MISSING:
            logger.warning(f"Metric {metric} is not available in the API: {mapping.notes}")
            return None

        try:
            # Add rate limiting
            time.sleep(random.uniform(0.1, 0.3))

            # Fetch data based on API source
            if mapping.api_source == "leaguedashplayerstats":
                return self._fetch_player_stats_data(metric, mapping, season)
            elif mapping.api_source == "leaguedashptstats":
                return self._fetch_tracking_data(metric, mapping, season)
            elif mapping.api_source == "commonplayerinfo":
                return self._fetch_player_info_data(metric, mapping)
            elif mapping.api_source == "leaguehustlestatsplayer":
                return self._fetch_hustle_data(metric, mapping, season)
            else:
                logger.error(f"Unknown API source: {mapping.api_source}")
                return None

        except Exception as e:
            logger.error(f"Error fetching {metric}: {e}")
            return None

    def _fetch_player_stats_data(self, metric: str, mapping: MetricMapping, season: str) -> Optional[Dict[str, Any]]:
        """Fetch data from player stats endpoints."""
        try:
            if mapping.endpoint_params.get("MeasureType") == "Base":
                response = self.client.get_league_player_base_stats(
                    season=season,
                    season_type=mapping.endpoint_params.get("SeasonType", "Regular Season")
                )
            else:  # Advanced
                response = self.client.get_league_player_advanced_stats(
                    season=season,
                    season_type=mapping.endpoint_params.get("SeasonType", "Regular Season")
                )

            if not response or 'resultSets' not in response:
                logger.warning(f"No data returned for {metric}")
                return None

            return self._extract_player_data(response, mapping.api_column, metric)

        except Exception as e:
            logger.error(f"Error fetching player stats for {metric}: {e}")
            return None

    def _fetch_tracking_data(self, metric: str, mapping: MetricMapping, season: str) -> Optional[Dict[str, Any]]:
        """Fetch data from player tracking endpoints."""
        try:
            pt_measure_type = mapping.endpoint_params.get("PtMeasureType", "Drives")
            response = self.client.get_league_player_tracking_stats(
                season=season,
                pt_measure_type=pt_measure_type
            )

            if not response or 'resultSets' not in response:
                logger.warning(f"No tracking data returned for {metric}")
                return None

            return self._extract_player_data(response, mapping.api_column, metric)

        except Exception as e:
            logger.error(f"Error fetching tracking data for {metric}: {e}")
            return None

    def _fetch_player_info_data(self, metric: str, mapping: MetricMapping) -> Optional[Dict[str, Any]]:
        """Fetch data from player info endpoints."""
        try:
            # For player info, we need to get all players first, then fetch individually
            # This is a simplified approach - we'll return empty for now
            logger.warning(f"Player info metrics require individual player ID fetching: {metric}")
            return {}

        except Exception as e:
            logger.error(f"Error fetching player info for {metric}: {e}")
            return None

    def _fetch_hustle_data(self, metric: str, mapping: MetricMapping, season: str) -> Optional[Dict[str, Any]]:
        """Fetch data from hustle stats endpoints."""
        try:
            response = self.client.get_league_hustle_stats(season=season)

            if not response or 'resultSets' not in response:
                logger.warning(f"No hustle data returned for {metric}")
                return None

            return self._extract_player_data(response, mapping.api_column, metric)

        except Exception as e:
            logger.error(f"Error fetching hustle data for {metric}: {e}")
            return None

    def _extract_player_data(self, response: Dict[str, Any], column_name: str, metric: str) -> Dict[str, Any]:
        """Extract player data from API response."""
        try:
            result_sets = response.get('resultSets', [])
            if not result_sets:
                logger.warning(f"No result sets in response for {metric}")
                return {}

            # Use the first result set
            result_set = result_sets[0]
            headers = result_set.get('headers', [])
            rows = result_set.get('rowSet', [])

            if not headers or not rows:
                logger.warning(f"No data rows in response for {metric}")
                return {}

            # Find the column index
            try:
                column_index = headers.index(column_name)
            except ValueError:
                logger.warning(f"Column {column_name} not found in response for {metric}")
                return {}

            # Extract player data
            player_data = {}
            for row in rows:
                if len(row) > column_index:
                    player_id = row[0] if row else None  # Assuming first column is player ID
                    if player_id:
                        try:
                            value = row[column_index]
                            if value is not None:
                                # Basic type validation
                                mapping = self.metric_mappings.get(metric)
                                if mapping and mapping.data_type == DataType.PERCENTAGE:
                                    if not (0 <= float(value) <= 1):
                                        logger.warning(f"Invalid percentage value for {metric}, player {player_id}: {value}")
                                        continue
                                elif mapping and mapping.data_type == DataType.COUNT:
                                    # Allow negative values for PIE (Player Impact Estimate can be negative)
                                    if metric != "PIE" and float(value) < 0:
                                        logger.warning(f"Invalid count value for {metric}, player {player_id}: {value}")
                                        continue

                            player_data[player_id] = value
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Invalid data type for {metric}, player {player_id}: {e}")
                            continue

            logger.info(f"Extracted {len(player_data)} player records for {metric}")
            return player_data

        except Exception as e:
            logger.error(f"Error extracting player data for {metric}: {e}")
            return {}

    def fetch_all_available_metrics(self, season: str = "2024-25") -> Dict[str, Dict[str, Any]]:
        """
        Fetch data for all available metrics.

        Args:
            season: The season to fetch data for

        Returns:
            Dictionary mapping metric names to their player data
        """
        logger.info("Fetching data for all available metrics...")

        all_data = {}
        available_metrics = [metric for metric, mapping in self.metric_mappings.items()
                           if mapping.data_type != DataType.MISSING]

        # Add progress bar if tqdm is available
        if TQDM_AVAILABLE:
            metric_iterator = tqdm(enumerate(available_metrics, 1),
                                 total=len(available_metrics),
                                 desc="Fetching metrics",
                                 unit="metric")
        else:
            metric_iterator = enumerate(available_metrics, 1)

        for i, metric in metric_iterator:
            if not TQDM_AVAILABLE:  # Only log if no progress bar
                logger.info(f"Fetching {metric} ({i}/{len(available_metrics)})")

            data = self.fetch_metric_data(metric, season)
            if data:
                all_data[metric] = data
            else:
                logger.warning(f"Failed to fetch data for {metric}")

        logger.info(f"Successfully fetched data for {len(all_data)} metrics")
        return all_data

    def fetch_all_available_playoff_metrics(self, season: str = "2024-25") -> Dict[str, Dict[str, Any]]:
        """
        Fetch playoff data for all available metrics.

        Args:
            season: The season to fetch data for

        Returns:
            Dictionary mapping table names to their metric data
        """
        logger.info("Fetching playoff data for all available metrics...")

        all_data = {}

        # Define playoff data sources - mapping table names to API methods
        playoff_data_sources = {
            "player_playoff_stats": [
                "GP", "GS", "MIN", "FGM", "FGA", "FG3M", "FG3A", "FTM", "FTA", "OREB", "DREB",
                "PTS", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS",
                "FGPCT", "FG3PCT", "FTPCT"
            ],
            "player_playoff_advanced_stats": [
                # Basic game info
                "AGE", "GP", "W", "L", "W_PCT", "MIN",
                # Advanced metrics
                "TS_PCT", "USG_PCT", "OFF_RATING", "DEF_RATING", "NET_RATING",
                # Percentage stats
                "REB_PCT", "AST_PCT", "AST_TO", "AST_RATIO", "OREB_PCT", "DREB_PCT", "TM_TOV_PCT", "EFG_PCT", "PACE", "PIE"
            ],
            "player_playoff_tracking_stats": [
                # Drive metrics
                "DRIVES", "DRIVE_FGM", "DRIVE_FGA", "DRIVE_FG_PCT", "DRIVE_FTM", "DRIVE_FTA",
                "DRIVE_FT_PCT", "DRIVE_PTS", "DRIVE_PTS_PCT", "DRIVE_PASSES", "DRIVE_PASSES_PCT",
                "DRIVE_AST", "DRIVE_AST_PCT", "DRIVE_TOV", "DRIVE_TOV_PCT", "DRIVE_PF", "DRIVE_PF_PCT",

                # Catch and shoot metrics
                "CATCH_SHOOT_FGM", "CATCH_SHOOT_FGA", "CATCH_SHOOT_FG_PCT", "CATCH_SHOOT_PTS",
                "CATCH_SHOOT_FG3M", "CATCH_SHOOT_FG3A", "CATCH_SHOOT_FG3_PCT", "CATCH_SHOOT_EFG_PCT",

                # Pull up shot metrics
                "PULL_UP_FGM", "PULL_UP_FGA", "PULL_UP_FG_PCT", "PULL_UP_PTS",
                "PULL_UP_FG3M", "PULL_UP_FG3A", "PULL_UP_FG3_PCT", "PULL_UP_EFG_PCT",

                # Paint touch metrics
                "PAINT_TOUCHES", "PAINT_TOUCH_FGM", "PAINT_TOUCH_FGA", "PAINT_TOUCH_FG_PCT",
                "PAINT_TOUCH_FTM", "PAINT_TOUCH_FTA", "PAINT_TOUCH_FT_PCT", "PAINT_TOUCH_PTS",
                "PAINT_TOUCH_PTS_PCT", "PAINT_TOUCH_PASSES", "PAINT_TOUCH_PASSES_PCT",
                "PAINT_TOUCH_AST", "PAINT_TOUCH_AST_PCT", "PAINT_TOUCH_TOV", "PAINT_TOUCH_TOV_PCT",
                "PAINT_TOUCH_FOULS", "PAINT_TOUCH_FOULS_PCT",

                # Post touch metrics
                "POST_TOUCHES", "POST_TOUCH_FGM", "POST_TOUCH_FGA", "POST_TOUCH_FG_PCT",
                "POST_TOUCH_FTM", "POST_TOUCH_FTA", "POST_TOUCH_FT_PCT", "POST_TOUCH_PTS",
                "POST_TOUCH_PTS_PCT", "POST_TOUCH_PASSES", "POST_TOUCH_PASSES_PCT",
                "POST_TOUCH_AST", "POST_TOUCH_AST_PCT", "POST_TOUCH_TOV", "POST_TOUCH_TOV_PCT",
                "POST_TOUCH_FOULS", "POST_TOUCH_FOULS_PCT",

                # Elbow touch metrics
                "ELBOW_TOUCHES", "ELBOW_TOUCH_FGM", "ELBOW_TOUCH_FGA", "ELBOW_TOUCH_FG_PCT",
                "ELBOW_TOUCH_FTM", "ELBOW_TOUCH_FTA", "ELBOW_TOUCH_FT_PCT", "ELBOW_TOUCH_PTS",
                "ELBOW_TOUCH_PASSES", "ELBOW_TOUCH_AST", "ELBOW_TOUCH_AST_PCT",
                "ELBOW_TOUCH_TOV", "ELBOW_TOUCH_TOV_PCT", "ELBOW_TOUCH_FOULS",
                "ELBOW_TOUCH_PASSES_PCT", "ELBOW_TOUCH_FOULS_PCT", "ELBOW_TOUCH_PTS_PCT",

                # Efficiency metrics
                "EFF_PTS", "EFF_DRIVE_PTS", "EFF_DRIVE_FG_PCT", "EFF_CATCH_SHOOT_PTS",
                "EFF_CATCH_SHOOT_FG_PCT", "EFF_PULL_UP_PTS", "EFF_PULL_UP_FG_PCT",
                "EFF_PAINT_TOUCH_PTS", "EFF_PAINT_TOUCH_FG_PCT", "EFF_POST_TOUCH_PTS",
                "EFF_POST_TOUCH_FG_PCT", "EFF_ELBOW_TOUCH_PTS", "EFF_ELBOW_TOUCH_FG_PCT",
                "EFF_EFG_PCT",

                # Possession metrics
                "AVG_SEC_PER_TOUCH", "AVG_DRIB_PER_TOUCH", "PTS_PER_TOUCH", "TIME_OF_POSS", "FRONT_CT_TOUCHES"
            ]
        }

        # Fetch data for each table
        for table_name, metric_names in playoff_data_sources.items():
            logger.info(f"Fetching playoff data for {table_name}...")

            table_data = {}

            # Fetch each metric for this table
            for metric_name in metric_names:
                try:
                    data = self._fetch_playoff_metric_data(metric_name, season)
                    if data:
                        table_data[metric_name] = data
                        logger.debug(f"  ✓ {metric_name}: {len(data)} records")
                    else:
                        logger.warning(f"  ⚠ No data for {metric_name}")
                except Exception as e:
                    logger.error(f"  ✗ Failed to fetch {metric_name}: {str(e)}")

            if table_data:
                all_data[table_name] = table_data
                logger.info(f"✅ {table_name}: {len(table_data)} metrics fetched")

        logger.info(f"Successfully fetched playoff data for {len(all_data)} tables")
        return all_data

    def _fetch_playoff_metric_data(self, metric_name: str, season: str) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch playoff data for a specific metric.

        Args:
            metric_name: Name of the metric to fetch
            season: Season to fetch data for

        Returns:
            List of player data records for this metric
        """
        try:
            # Map metric names to appropriate API calls
            if metric_name in ["GP", "GS", "MIN", "FGM", "FGA", "FG3M", "FG3A", "FTM", "FTA", "OREB", "DREB", "PTS", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS", "FGPCT", "FG3PCT", "FTPCT"]:
                # Basic stats
                response = self.client.get_league_player_playoff_base_stats(season)
            elif metric_name in ["AGE", "GP", "W", "L", "W_PCT", "MIN", "TS_PCT", "USG_PCT", "OFF_RATING", "DEF_RATING", "NET_RATING", "REB_PCT", "AST_PCT", "AST_TO", "AST_RATIO", "OREB_PCT", "DREB_PCT", "TM_TOV_PCT", "EFG_PCT", "PACE", "PIE"]:
                # Advanced stats - includes all available metrics
                response = self.client.get_league_player_playoff_advanced_stats(season)
            elif metric_name in ["AVG_SEC_PER_TOUCH", "AVG_DRIB_PER_TOUCH", "PTS_PER_TOUCH", "TIME_OF_POSS", "FRONT_CT_TOUCHES"]:
                # Possession stats
                response = self.client.get_league_player_playoff_tracking_stats(season, pt_measure_type="Possessions")
            elif metric_name.startswith(("DRIVE", "CATCH_SHOOT", "PULL_UP", "PAINT_TOUCH", "POST_TOUCH", "ELBOW_TOUCH", "EFF")):
                # Tracking stats - map metric names to PtMeasureType
                measure_type_map = {
                    "DRIVE": "Drives",
                    "CATCH_SHOOT": "CatchShoot",
                    "PULL_UP": "PullUpShot",
                    "PAINT_TOUCH": "PaintTouch",
                    "POST_TOUCH": "PostTouch",
                    "ELBOW_TOUCH": "ElbowTouch",
                    "EFF": "Efficiency"  # This might need different handling
                }

                # Find the measure type from the metric name
                measure_type = None
                for prefix, mt in measure_type_map.items():
                    if metric_name.startswith(prefix):
                        measure_type = mt
                        break

                if measure_type:
                    response = self.client.get_league_player_playoff_tracking_stats(season, pt_measure_type=measure_type)
                else:
                    logger.warning(f"Could not determine measure type for metric {metric_name}")
                    return None
            else:
                logger.warning(f"Unknown metric {metric_name}, skipping")
                return None

            # Extract the data from the API response
            if "resultSets" in response and response["resultSets"]:
                result_set = response["resultSets"][0]
                headers = result_set.get("headers", [])
                rows = result_set.get("rowSet", [])

                # Convert to list of dictionaries
                player_data = []
                for row in rows:
                    if len(row) == len(headers):
                        player_record = dict(zip(headers, row))
                        # Add the metric value explicitly
                        player_data.append(player_record)

                return player_data if player_data else None
            else:
                logger.warning(f"No resultSets found in response for {metric_name}")
                return None

        except Exception as e:
            logger.error(f"Failed to fetch playoff data for {metric_name}: {str(e)}")
            return None

    def get_missing_metrics(self) -> List[str]:
        """Get list of metrics that are missing from the API."""
        return [metric for metric, mapping in self.metric_mappings.items()
                if mapping.data_type == DataType.MISSING]

    def get_available_metrics(self) -> List[str]:
        """Get list of metrics that are available in the API."""
        return [metric for metric, mapping in self.metric_mappings.items()
                if mapping.data_type != DataType.MISSING]

    def validate_data_completeness(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate the completeness of fetched data.

        Args:
            data: Dictionary mapping metric names to their player data

        Returns:
            Validation results
        """
        validation_results = {
            "total_metrics": len(self.metric_mappings),
            "fetched_metrics": len(data),
            "missing_metrics": [],
            "empty_metrics": [],
            "coverage_stats": {}
        }

        # Check for missing metrics
        for metric in self.metric_mappings:
            if metric not in data:
                validation_results["missing_metrics"].append(metric)

        # Check for empty metrics
        for metric, player_data in data.items():
            if not player_data:
                validation_results["empty_metrics"].append(metric)

        # Calculate coverage stats
        for metric, player_data in data.items():
            if player_data:
                validation_results["coverage_stats"][metric] = {
                    "player_count": len(player_data),
                    "non_null_count": sum(1 for v in player_data.values() if v is not None),
                    "coverage_pct": (sum(1 for v in player_data.values() if v is not None) / len(player_data)) * 100
                }

        return validation_results


def create_data_fetcher() -> DataFetcher:
    """Create a new DataFetcher instance."""
    return DataFetcher()


if __name__ == "__main__":
    # Test the data fetcher
    fetcher = create_data_fetcher()

    print("Available metrics:", len(fetcher.get_available_metrics()))
    print("Missing metrics:", len(fetcher.get_missing_metrics()))

    # Test fetching a single metric
    test_metric = "FTPCT"
    print(f"\nTesting fetch for {test_metric}...")
    data = fetcher.fetch_metric_data(test_metric)
    if data:
        print(f"Successfully fetched data for {len(data)} players")
    else:
        print("Failed to fetch data")
