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
                data_type=DataType.COUNT,
                required=True,
                notes="Direct mapping from advanced stats"
            ),
            "DRTG": MetricMapping(
                canonical_name="Defensive Rating",
                api_source="leaguedashplayerstats",
                api_column="DEF_RATING",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Direct mapping from advanced stats"
            ),
            "NRTG": MetricMapping(
                canonical_name="Net Rating",
                api_source="leaguedashplayerstats",
                api_column="NET_RATING",
                endpoint_params={"MeasureType": "Advanced", "PerMode": "PerGame", "SeasonType": "Regular Season"},
                data_type=DataType.COUNT,
                required=True,
                notes="Direct mapping from advanced stats"
            ),

            # Tracking metrics (available ones)
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
                                    if float(value) < 0:
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
                "GP", "GS", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS",
                "FGPCT", "FG3PCT", "FTPCT"
            ],
            "player_playoff_advanced_stats": [
                "TSPCT", "USGPCT", "ORTG", "DRTG", "NRTG",
                "TRBPCT", "ASTPCT", "PIE"
            ],
            "player_playoff_tracking_stats": [
                "DRIVES", "DRIVE_FGM"
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
            if metric_name in ["GP", "GS", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TOV", "PF", "PLUS_MINUS", "FGPCT", "FG3PCT", "FTPCT"]:
                # Basic stats
                response = self.client.get_league_player_playoff_base_stats(season)
            elif metric_name in ["TSPCT", "USGPCT", "ORTG", "DRTG", "NRTG", "TRBPCT", "ASTPCT", "PIE"]:
                # Advanced stats
                response = self.client.get_league_player_playoff_advanced_stats(season)
            elif metric_name in ["DRIVES", "DRIVE_FGM"]:
                # Tracking stats
                response = self.client.get_league_player_playoff_tracking_stats(season)
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
