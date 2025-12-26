# API Reference

Complete reference for all public functions, classes, and modules in the NBA Playoff Resilience Engine.

## Core Prediction API

### `predict_archetype()`

The main prediction function that predicts playoff archetype for any player.

```python
from src.model.predictor import predict_archetype

def predict_archetype(
    player_data: dict,
    usage_level: Optional[float] = None,
    confidence_threshold: float = 0.5
) -> ArchetypePrediction:
    """
    Predict playoff archetype for a player.

    Args:
        player_data: Player season data with stress vectors
        usage_level: Usage % to predict at (0.0-1.0). If None, uses current usage
        confidence_threshold: Minimum confidence to return prediction

    Returns:
        ArchetypePrediction named tuple with:
        - archetype: str ('King', 'Bulldozer', 'Sniper', 'Victim')
        - confidence: float (0.0-1.0)
        - features: dict of feature values used
        - dependence_score: float (2D Risk Matrix Y-axis)

    Raises:
        ValueError: If required features missing
        ModelLoadError: If model files not found

    Example:
        >>> from src.data.client import get_player_data
        >>> player = get_player_data("Luka Dončić", "2023-24")
        >>> result = predict_archetype(player, usage_level=0.30)
        >>> print(f"{result.archetype} ({result.confidence:.1%})")
        Bulldozer (89.7%)
    """
```

### `predict_with_risk_matrix()`

Predict using the 2D Risk Matrix framework (recommended for new applications).

```python
from src.model.predictor import predict_with_risk_matrix

def predict_with_risk_matrix(
    player_data: dict,
    usage_level: Optional[float] = None
) -> RiskMatrixPrediction:
    """
    Predict using 2D Risk Matrix (Performance + Dependence).

    Args:
        player_data: Player season data
        usage_level: Optional usage override

    Returns:
        RiskMatrixPrediction with:
        - performance_score: float (0-100)
        - dependence_score: float (0-100)
        - risk_category: str ('Franchise Cornerstone', 'Luxury Component', etc.)
        - confidence: float

    Example:
        >>> result = predict_with_risk_matrix(player_data)
        >>> print(f"Category: {result.risk_category}")
        >>> print(f"Performance: {result.performance_score}")
        Category: Franchise Cornerstone
        Performance: 92.3
    """
```

## Data Collection API

### `NBAApiClient`

Main client for NBA Stats API interactions.

```python
from src.data.client import NBAApiClient

class NBAApiClient:
    """NBA Stats API client with rate limiting and error handling."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize client with optional API key."""

    def get_player_stats(self, player_id: int, season: str) -> dict:
        """Get player stats for season."""

    def get_team_stats(self, team_id: int, season: str) -> dict:
        """Get team stats for season."""

    def get_game_log(self, player_id: int, season: str) -> pd.DataFrame:
        """Get detailed game log."""

    def get_shot_chart(self, player_id: int, season: str) -> pd.DataFrame:
        """Get shot chart data with coordinates."""
```

### Data Collection Functions

```python
from src.data.collector import collect_player_season_data

def collect_player_season_data(
    player_id: int,
    season: str,
    include_shot_charts: bool = True,
    include_playbyplay: bool = False
) -> dict:
    """
    Collect all data for a player-season.

    Args:
        player_id: NBA player ID
        season: Season string ('2023-24')
        include_shot_charts: Include spatial shooting data
        include_playbyplay: Include play-by-play data (slow)

    Returns:
        Complete player-season dataset
    """
```

## Feature Engineering API

### Stress Vector Calculations

```python
from src.features.resilience import calculate_resilience_quotient

def calculate_resilience_quotient(
    playoff_stats: dict,
    regular_season_stats: dict
) -> float:
    """
    Calculate Resilience Quotient (RQ).

    RQ = (PO Efficiency / RS Efficiency) × (PO Volume / RS Volume)

    Args:
        playoff_stats: Playoff season stats
        regular_season_stats: Regular season stats

    Returns:
        RQ value (typically 0.5-1.5, higher = more resilient)
    """
```

```python
from src.features.creation import calculate_creation_tax

def calculate_creation_tax(player_data: dict) -> float:
    """
    Calculate creation efficiency drop-off.

    Measures how much efficiency drops when player creates own shot
    vs. getting catch-and-shoot opportunities.

    Args:
        player_data: Player season data with shot chart

    Returns:
        Creation tax (negative = efficiency drops when creating)
    """
```

```python
from src.features.leverage import calculate_leverage_deltas

def calculate_leverage_deltas(
    clutch_stats: dict,
    regular_stats: dict
) -> dict:
    """
    Calculate leverage deltas (clutch performance).

    Args:
        clutch_stats: High-leverage stats (last 5min + OT)
        regular_stats: Full game stats

    Returns:
        {
            'leverage_ts_delta': TS% delta in clutch,
            'leverage_usg_delta': Usage delta in clutch
        }
    """
```

### Universal Projection

```python
from src.features.projection import project_features_to_usage

def project_features_to_usage(
    player_data: dict,
    target_usage: float,
    current_usage: float
) -> dict:
    """
    Project player features to different usage level.

    Uses empirical distributions to scale features together,
    solving the "Static Avatar Fallacy".

    Args:
        player_data: Current player data
        target_usage: Target usage % (0.0-1.0)
        current_usage: Current usage % (0.0-1.0)

    Returns:
        Projected feature values at target usage
    """
```

## Model Training API

### `ResilienceModelTrainer`

Class for training and evaluating models.

```python
from src.model.trainer import ResilienceModelTrainer

class ResilienceModelTrainer:
    """Train and evaluate resilience prediction models."""

    def __init__(self, config: dict):
        """Initialize with training configuration."""

    def train_xgboost_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        feature_names: list
    ) -> XGBClassifier:
        """Train XGBoost model with optimal hyperparameters."""

    def perform_rfe_selection(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_features: int = 10
    ) -> tuple:
        """Perform Recursive Feature Elimination."""

    def evaluate_model(
        self,
        model: XGBClassifier,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> dict:
        """Evaluate model performance."""
```

## Utility Functions

### Data Validation

```python
from src.utils.validation import validate_player_data

def validate_player_data(player_data: dict) -> dict:
    """
    Validate player data completeness and quality.

    Args:
        player_data: Player season data

    Returns:
        Validation results with missing fields, data quality score
    """
```

### Configuration

```python
from src.config import get_config

def get_config(environment: str = 'development') -> dict:
    """
    Get configuration for environment.

    Args:
        environment: 'development', 'production', or 'testing'

    Returns:
        Configuration dictionary
    """
```

## Command Line Interface

### Prediction CLI

```bash
# Predict single player
python scripts/predict.py --player "Luka Dončić" --season "2023-24"

# Predict at specific usage
python scripts/predict.py --player "Jalen Brunson" --season "2022-23" --usage 0.30

# Batch predictions
python scripts/predict.py --input-file players.csv --output-file predictions.csv
```

### Validation CLI

```bash
# Run full test suite
python scripts/validate.py

# Run specific test category
python scripts/validate.py --category "latent_stars"

# Generate validation report
python scripts/validate.py --report results/validation_report.md
```

### Debug CLI

```bash
# System diagnostic
python scripts/debug.py --diagnostic

# Player analysis
python scripts/debug.py --player "Jordan Poole" --season "2021-22" --detailed

# Model analysis
python scripts/debug.py --model-analysis
```

## Data Structures

### `ArchetypePrediction`

```python
from typing import NamedTuple

class ArchetypePrediction(NamedTuple):
    """Prediction result for archetype classification."""
    archetype: str          # 'King', 'Bulldozer', 'Sniper', 'Victim'
    confidence: float       # 0.0-1.0
    features: dict          # Feature values used in prediction
    dependence_score: float # 2D Risk Matrix Y-axis (0-100)
    performance_score: float # 2D Risk Matrix X-axis (0-100)
```

### `RiskMatrixPrediction`

```python
class RiskMatrixPrediction(NamedTuple):
    """2D Risk Matrix prediction result."""
    performance_score: float  # X-axis: What outcomes achieved (0-100)
    dependence_score: float   # Y-axis: How portable production is (0-100)
    risk_category: str        # 'Franchise Cornerstone', 'Luxury Component', etc.
    confidence: float         # Overall prediction confidence (0-100)
    reasoning: dict           # Mechanistic explanations
```

### Player Data Schema

```python
# Complete player-season data structure
player_data = {
    # Basic info
    'player_id': int,
    'player_name': str,
    'season': str,
    'team_id': int,

    # Usage metrics
    'usg_pct': float,          # Usage percentage
    'min': float,              # Minutes per game
    'games_played': int,

    # Efficiency metrics
    'efg_pct': float,          # Effective FG%
    'ts_pct': float,           # True Shooting%
    'fg_pct': float,

    # Stress vectors (calculated)
    'creation_tax': float,
    'leverage_ts_delta': float,
    'leverage_usg_delta': float,
    'rim_pressure_resilience': float,
    'pressure_resilience': float,

    # Shot chart data
    'shot_chart': pd.DataFrame,  # x, y coordinates, make/miss

    # Clutch data (if available)
    'clutch_stats': dict,

    # Metadata
    'data_completeness': float,  # 0-1 score
    'last_updated': str,
}
```

## Error Types

### `ModelLoadError`
Raised when model files cannot be loaded.

```python
class ModelLoadError(Exception):
    """Model file not found or corrupted."""
    pass
```

### `DataValidationError`
Raised when player data fails validation.

```python
class DataValidationError(Exception):
    """Player data incomplete or invalid."""
    pass
```

### `APIError`
Raised when NBA API requests fail.

```python
class APIError(Exception):
    """NBA API request failed."""
    pass
```

## Configuration Options

### Model Configuration

```yaml
# config/default.yaml
model:
  algorithm: xgboost
  n_estimators: 100
  max_depth: 6
  learning_rate: 0.1
  subsample: 0.8

  # RFE settings
  rfe_n_features: 15
  rfe_step: 1

  # Sample weighting
  victim_weight: 3.0  # Penalize false positives more
```

### Data Collection Configuration

```yaml
# config/default.yaml
data:
  nba_api:
    base_url: "https://stats.nba.com/stats"
    timeout: 30
    max_retries: 3
    backoff_factor: 2

  collection:
    workers: 8
    seasons: ["2015-16", "2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]
    include_shot_charts: true
    include_playbyplay: false
```

### Feature Engineering Configuration

```yaml
# config/default.yaml
features:
  resilience:
    min_games_threshold: 20
    min_minutes_threshold: 10

  creation:
    iso_frequency_threshold: 0.10
    pnr_frequency_threshold: 0.15

  leverage:
    clutch_minutes_threshold: 15
    leverage_threshold: -0.05  # Abdication tax

  projection:
    usage_buckets: [0.15, 0.20, 0.25, 0.30, 0.35]
    scaling_method: empirical_median
```

This API reference covers the most important public interfaces. For internal implementation details, see the source code or ask in the development chat.
