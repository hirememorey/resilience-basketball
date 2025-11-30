# Implementation Guide: Step-by-Step

## Prerequisites

### Required Python Packages
```bash
pip install pandas numpy scikit-learn scipy tenacity requests
```

### Existing Infrastructure
- API client: `src/nba_data/api/nba_stats_client.py` (already built)
- Caching: Built-in with tenacity retries
- Error handling: Rate limiting implemented

---

## Step 1: Data Collection

### 1.1 Create Regular Season Collector

**File:** `src/nba_data/scripts/collect_regular_season_stats.py`

**Purpose:** Fetch and store regular season player statistics.

**Key Functions:**
```python
def fetch_regular_season_stats(season):
    """
    Fetch regular season stats for all players in a season.
    Returns: DataFrame with player stats
    """
    pass

def filter_qualified_players(df):
    """
    Filter to players meeting criteria:
    - GP >= 50
    - MIN >= 20
    """
    return df[(df['GP'] >= 50) & (df['MIN'] >= 20)]

def save_to_csv(df, season):
    """
    Save to data/regular_season_{season}.csv
    """
    pass
```

**Run:**
```bash
python src/nba_data/scripts/collect_regular_season_stats.py --seasons 2018-19 2022-23 2023-24
```

**Expected Output:**
- `data/regular_season_2018-19.csv` (~450 rows)
- `data/regular_season_2022-23.csv` (~450 rows)
- `data/regular_season_2023-24.csv` (~450 rows)

---

### 1.2 Create Defensive Context Collector

**File:** `src/nba_data/scripts/collect_defensive_context.py`

**Purpose:** Fetch and calculate defensive context scores for all teams. This requires **two API calls per season** (one for `Advanced` `MeasureType` to get `DEF_RATING`, and one for `Opponent` `MeasureType` to get opponent base stats) which are then merged.

**Key Functions:**
```python
def fetch_team_defense_stats(season, season_type='Regular Season'):
    """
    Fetch team defensive stats for both Advanced and Opponent measures.
    Returns: Merged DataFrame with all required defensive metrics
    """
    pass

def calculate_defensive_context_score(row):
    """
    Calculate composite defensive context score (0-100).
    Handles calculation of OPP_EFG_PCT and OPP_FTA_RATE from base stats.
    """
    pass
```

**Run:**
```bash
python src/nba_data/scripts/collect_defensive_context.py --seasons 2018-19 2022-23 2023-24
```

**Expected Output:**
- `data/defensive_context_2018-19.csv` (~30 rows)
- `data/defensive_context_2022-23.csv` (~30 rows)
- `data/defensive_context_2023-24.csv` (~30 rows)

---

### 1.3 Create Playoff Game Log Collector

**File:** `src/nba_data/scripts/collect_playoff_logs.py`

**Purpose:** Fetch playoff game logs for all players. This script replaces the previous `playbyplay` collector due to API instability. It fetches both `Base` and `Advanced` game logs for each player and merges them.

**Key Functions:**
```python
def get_playoff_players(season):
    """
    Get a list of all player IDs who participated in the playoffs for a season.
    """
    pass

def fetch_player_playoff_logs(player_id, season):
    """
    Fetch and merge Base and Advanced game logs for a single player.
    Returns: A DataFrame with comprehensive per-game stats.
    """
    pass
```

**Run:**
```bash
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2023-24
```

**Expected Output:**
- `data/playoff_logs_2023-24.csv` (~1700 rows)

**Note:** This script will take 30-40 minutes per season due to API rate limiting.

---

### 1.4 Create Training Data Assembler

**File:** `src/nba_data/scripts/assemble_training_data.py`

**Purpose:** Combine all data sources into a single training dataset, with one row per player, per playoff series.

**Key Functions:**
```python
def aggregate_playoff_series(po_logs):
    """
    Aggregates per-game logs into series-level stats.
    - Parses opponent from MATCHUP string.
    - Groups by player and opponent.
    - Recalculates TS% from totals and computes weighted averages for rates.
    """
    pass

def merge_datasets(series_df, regular_df, defense_df):
    """
    Joins all datasets on appropriate keys.
    - Merges series data with regular season performance.
    - Maps opponent abbreviation to team ID to join with defensive context.
    """
    pass
```

**Run:**
```bash
python src/nba_data/scripts/assemble_training_data.py --output data/training_dataset.csv
```

**Expected Output:**
- `data/training_dataset.csv` (~600-800 rows)

---

## Step 2: Model Training

### 2.1 Create Model Training Script

**File:** `src/nba_data/scripts/train_resilience_models.py`

**Purpose:** Train three regression models for TS%, PPG, and AST%.

**Key Functions:**
```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import pickle

def prepare_features(df, target_metric):
    """
    Prepare features and target for modeling.
    
    Features:
    - Regular season metric (rs_ts_pct, rs_ppg_per75, rs_ast_pct)
    - Defensive context score
    - Usage %
    - Interaction term (rs_metric × def_context_score)
    
    Target:
    - Playoff metric (po_ts_pct, po_ppg_per75, po_ast_pct)
    """
    # Define feature columns
    rs_metric_col = f'rs_{target_metric}'
    po_metric_col = f'po_{target_metric}'
    
    # Create interaction term
    df[f'{rs_metric_col}_x_dcs'] = df[rs_metric_col] * df['opp_def_context_score']
    
    # Feature matrix
    X = df[[
        rs_metric_col,
        'opp_def_context_score',
        'rs_usg_pct',
        f'{rs_metric_col}_x_dcs'
    ]]
    
    # Target
    y = df[po_metric_col]
    
    return X, y

def train_model(X, y, model_name):
    """
    Train linear regression model with train/test split.
    """
    # Split data (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    
    print(f"\n{model_name} Performance:")
    print(f"  Train R²: {train_r2:.3f}")
    print(f"  Test R²: {test_r2:.3f}")
    print(f"  Test RMSE: {test_rmse:.4f}")
    
    # Save model
    with open(f'models/{model_name}_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    return model, test_rmse

def main():
    """
    Train all three models.
    """
    # Load training data
    df = pd.read_csv('data/training_dataset.csv')
    
    # Train TS% model
    X_ts, y_ts = prepare_features(df, 'ts_pct')
    model_ts, rmse_ts = train_model(X_ts, y_ts, 'ts_pct')
    
    # Train PPG model
    X_ppg, y_ppg = prepare_features(df, 'ppg_per75')
    model_ppg, rmse_ppg = train_model(X_ppg, y_ppg, 'ppg_per75')
    
    # Train AST% model
    X_ast, y_ast = prepare_features(df, 'ast_pct')
    model_ast, rmse_ast = train_model(X_ast, y_ast, 'ast_pct')
    
    # Save model metadata
    metadata = {
        'ts_pct_rmse': rmse_ts,
        'ppg_per75_rmse': rmse_ppg,
        'ast_pct_rmse': rmse_ast
    }
    
    with open('models/model_metadata.pkl', 'wb') as f:
        pickle.dump(metadata, f)
    
    print("\n✅ All models trained and saved to models/ directory")
```

**Run:**
```bash
python src/nba_data/scripts/train_resilience_models.py
```

**Expected Output:**
- `models/ts_pct_model.pkl`
- `models/ppg_per75_model.pkl`
- `models/ast_pct_model.pkl`
- `models/model_metadata.pkl`

**Success Criteria:**
- Test R² ≥ 0.3 for all models
- No severe overfitting (train R² - test R² < 0.15)

---

## Step 3: Generate Resilience Scores

### 3.1 Create Scoring Script

**File:** `src/nba_data/scripts/calculate_resilience_scores.py`

**Purpose:** Generate resilience scores for all player-series combinations.

**Key Functions:**
```python
import pickle
import pandas as pd
import numpy as np

def load_models():
    """
    Load trained models and metadata.
    """
    with open('models/ts_pct_model.pkl', 'rb') as f:
        model_ts = pickle.load(f)
    
    with open('models/ppg_per75_model.pkl', 'rb') as f:
        model_ppg = pickle.load(f)
    
    with open('models/ast_pct_model.pkl', 'rb') as f:
        model_ast = pickle.load(f)
    
    with open('models/model_metadata.pkl', 'rb') as f:
        metadata = pickle.load(f)
    
    return model_ts, model_ppg, model_ast, metadata

def generate_expected_performance(player_stats, models):
    """
    Generate expected playoff performance using trained models.
    """
    model_ts, model_ppg, model_ast = models
    
    # Prepare features (same as training)
    features_ts = prepare_features_for_prediction(player_stats, 'ts_pct')
    features_ppg = prepare_features_for_prediction(player_stats, 'ppg_per75')
    features_ast = prepare_features_for_prediction(player_stats, 'ast_pct')
    
    # Predict
    expected_ts = model_ts.predict(features_ts)[0]
    expected_ppg = model_ppg.predict(features_ppg)[0]
    expected_ast = model_ast.predict(features_ast)[0]
    
    return expected_ts, expected_ppg, expected_ast

def calculate_z_scores(actual, expected, rmse):
    """
    Calculate Z-score: (Actual - Expected) / RMSE
    """
    return (actual - expected) / rmse

def calculate_composite_score(z_efficiency, z_volume, z_creation, stability_score):
    """
    Calculate composite resilience score.
    
    Formula: 0.35×Z_Eff + 0.25×Z_Vol + 0.25×Z_Cre + 0.15×Z_Stab
    """
    composite = (
        0.35 * z_efficiency +
        0.25 * z_volume +
        0.25 * z_creation +
        0.15 * stability_score
    )
    return composite

def main():
    """
    Calculate resilience scores for all players.
    """
    # Load models
    model_ts, model_ppg, model_ast, metadata = load_models()
    models = (model_ts, model_ppg, model_ast)
    
    # Load player data (for target season)
    df = pd.read_csv('data/training_dataset.csv')
    
    # Calculate scores for each player
    results = []
    
    for idx, row in df.iterrows():
        # Generate expected performance
        expected_ts, expected_ppg, expected_ast = generate_expected_performance(row, models)
        
        # Get actual performance
        actual_ts = row['po_ts_pct']
        actual_ppg = row['po_ppg_per75']
        actual_ast = row['po_ast_pct']
        
        # Calculate Z-scores
        z_efficiency = calculate_z_scores(actual_ts, expected_ts, metadata['ts_pct_rmse'])
        z_volume = calculate_z_scores(actual_ppg, expected_ppg, metadata['ppg_per75_rmse'])
        z_creation = calculate_z_scores(actual_ast, expected_ast, metadata['ast_pct_rmse'])
        
        # Stability (placeholder for now - can enhance later)
        stability_score = 0.0
        
        # Composite score
        composite = calculate_composite_score(z_efficiency, z_volume, z_creation, stability_score)
        
        # Store results
        results.append({
            'player_id': row['player_id'],
            'player_name': row['player_name'],
            'season': row['season'],
            'series_round': row['series_round'],
            'opponent_team': row['opponent_team'],
            'rs_ts_pct': row['rs_ts_pct'],
            'rs_ppg_per75': row['rs_ppg_per75'],
            'rs_ast_pct': row['rs_ast_pct'],
            'expected_ts_pct': expected_ts,
            'expected_ppg_per75': expected_ppg,
            'expected_ast_pct': expected_ast,
            'actual_ts_pct': actual_ts,
            'actual_ppg_per75': actual_ppg,
            'actual_ast_pct': actual_ast,
            'z_efficiency': z_efficiency,
            'z_volume': z_volume,
            'z_creation': z_creation,
            'composite_resilience_score': composite,
            'games_played': row['po_games_played']
        })
    
    # Convert to DataFrame and save
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('composite_resilience_score', ascending=False)
    results_df.to_csv('results/resilience_scores_all.csv', index=False)
    
    print(f"\n✅ Resilience scores calculated for {len(results_df)} player-series")
    print(f"   Output: results/resilience_scores_all.csv")
    
    # Print top 10
    print("\n🏆 Top 10 Most Resilient Performers:")
    print(results_df[['player_name', 'season', 'composite_resilience_score']].head(10))
```

**Run:**
```bash
python src/nba_data/scripts/calculate_resilience_scores.py
```

**Expected Output:**
- `results/resilience_scores_all.csv` (all player-series with scores)

---

## Step 4: Validation

### 4.1 Create Face Validity Checker

**File:** `src/nba_data/scripts/validate_face_validity.py`

**Purpose:** Check if known elite playoff performers score high.

**Key Functions:**
```python
def load_results():
    """
    Load resilience scores.
    """
    return pd.read_csv('results/resilience_scores_all.csv')

def check_known_cases(df):
    """
    Test known elite playoff performers.
    
    Expected high scores:
    - LeBron James (2012, 2016, 2018)
    - Kawhi Leonard (2019)
    - Nikola Jokić (2023)
    - Dirk Nowitzki (2011)
    """
    known_elite = [
        ('LeBron James', '2011-12'),
        ('LeBron James', '2015-16'),
        ('Kawhi Leonard', '2018-19'),
        ('Nikola Jokić', '2022-23'),
    ]
    
    print("\n🔍 Face Validity Check: Known Elite Performers")
    print("=" * 60)
    
    for player_name, season in known_elite:
        player_data = df[
            (df['player_name'] == player_name) &
            (df['season'] == season)
        ]
        
        if len(player_data) == 0:
            print(f"❌ {player_name} ({season}): NOT FOUND in dataset")
        else:
            score = player_data['composite_resilience_score'].mean()
            rank = (df['composite_resilience_score'] > score).sum() + 1
            total = len(df)
            
            status = "✅ PASS" if score > 0.5 else "❌ FAIL"
            print(f"{status} {player_name} ({season}): Score={score:.2f}, Rank={rank}/{total}")
    
    print("=" * 60)

def main():
    df = load_results()
    check_known_cases(df)
```

**Run:**
```bash
python src/nba_data/scripts/validate_face_validity.py
```

**Success Criteria:**
- At least 75% of known elite performers have positive resilience scores

---

### 4.2 Create Statistical Validation Script

**File:** `src/nba_data/scripts/validate_model_assumptions.py`

**Purpose:** Check model residuals and assumptions.

**Key Functions:**
```python
from scipy import stats
import matplotlib.pyplot as plt

def check_residual_normality(df):
    """
    Test if residuals are normally distributed.
    """
    residuals_ts = df['actual_ts_pct'] - df['expected_ts_pct']
    residuals_ppg = df['actual_ppg_per75'] - df['expected_ppg_per75']
    residuals_ast = df['actual_ast_pct'] - df['expected_ast_pct']
    
    # Shapiro-Wilk test
    stat_ts, p_ts = stats.shapiro(residuals_ts)
    stat_ppg, p_ppg = stats.shapiro(residuals_ppg)
    stat_ast, p_ast = stats.shapiro(residuals_ast)
    
    print("\n📊 Residual Normality Tests (Shapiro-Wilk)")
    print(f"  TS%: p-value = {p_ts:.4f} {'✅ Normal' if p_ts > 0.05 else '⚠️ Non-normal'}")
    print(f"  PPG: p-value = {p_ppg:.4f} {'✅ Normal' if p_ppg > 0.05 else '⚠️ Non-normal'}")
    print(f"  AST%: p-value = {p_ast:.4f} {'✅ Normal' if p_ast > 0.05 else '⚠️ Non-normal'}")

def check_systematic_bias(df):
    """
    Check for systematic biases by position, team, etc.
    """
    # Group by regular season TS% quartiles
    df['rs_ts_quartile'] = pd.qcut(df['rs_ts_pct'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
    
    bias_check = df.groupby('rs_ts_quartile')['composite_resilience_score'].mean()
    
    print("\n🔍 Systematic Bias Check")
    print("  Average resilience score by regular season TS% quartile:")
    print(bias_check)
    
    # Ideally, scores should be near 0 for all quartiles
    if (bias_check.abs() < 0.3).all():
        print("  ✅ No systematic bias detected")
    else:
        print("  ⚠️ Potential bias - investigate further")

def main():
    df = pd.read_csv('results/resilience_scores_all.csv')
    check_residual_normality(df)
    check_systematic_bias(df)
```

**Run:**
```bash
python src/nba_data/scripts/validate_model_assumptions.py
```

---

## Step 5: Generate Final Report

### 5.1 Create Reporting Script

**File:** `src/nba_data/scripts/generate_report.py`

**Purpose:** Generate human-readable summary report.

**Output:**
- Top 20 most resilient players
- Top 20 most fragile players
- Summary statistics
- Model performance metrics

**Run:**
```bash
python src/nba_data/scripts/generate_report.py --output results/resilience_report.md
```

---

## Testing Strategy

### Unit Tests
Create `tests/test_data_pipeline.py`:
```python
import pytest
import pandas as pd

def test_opponent_parser():
    """Test opponent parsing logic."""
    from src.nba_data.scripts.assemble_training_data import parse_opponent
    
    assert parse_opponent("DEN vs. LAL", "DEN") == "LAL"
    assert parse_opponent("MIA @ BOS", "MIA") == "BOS"
    assert parse_opponent("PHX vs. LAC", "LAC") == "PHX"

def test_defensive_context_score():
    """Test DCS calculation."""
    from src.nba_data.scripts.collect_defensive_context import calculate_defensive_context_score
    
    # League average defense
    dcs = calculate_defensive_context_score(110.0, 0.52, 0.25)
    assert 45 <= dcs <= 55  # Should be near 50
    
    # Elite defense
    dcs = calculate_defensive_context_score(105.0, 0.48, 0.22)
    assert dcs > 60
    
    # Weak defense
    dcs = calculate_defensive_context_score(115.0, 0.56, 0.28)
    assert dcs < 40

# Run tests
pytest tests/test_data_pipeline.py
```

---

## Troubleshooting

### Issue: API Rate Limiting
**Solution:** Increase sleep time between requests, use caching aggressively.

### Issue: Missing Playoff Data
**Solution:** Some players/teams may not have data. Skip and log warnings.

### Issue: Model R² < 0.3
**Solution:** Check for data quality issues, verify feature engineering, consider adding features.

### Issue: Face Validity Fails
**Solution:** Investigate known cases, check if expected performance is reasonable.

---

## Next Steps After Implementation

1. **Run on 2024-25 season** (current season)
2. **Generate rankings** for all playoff performers
3. **Validate predictions** by comparing to actual outcomes
4. **Iterate** based on results

---

## Quick Start Summary

```bash
# 1. Collect data
python src/nba_data/scripts/collect_regular_season_stats.py --seasons 2018-19 2022-23 2023-24
python src/nba_data/scripts/collect_defensive_context.py --seasons 2018-19 2022-23 2023-24
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2018-19 2022-23 2023-24

# 2. Assemble training data
python src/nba_data/scripts/assemble_training_data.py --output data/training_dataset.csv

# 3. Train models
python src/nba_data/scripts/train_resilience_models.py

# 4. Generate scores
python src/nba_data/scripts/calculate_resilience_scores.py

# 5. Validate
python src/nba_data/scripts/validate_face_validity.py
python src/nba_data/scripts/validate_model_assumptions.py

# 6. Generate report
python src/nba_data/scripts/generate_report.py --output results/resilience_report.md
```

---

**Estimated Time:**
- Data collection: 30-40 minutes per season (can be run in parallel)
- Model training: < 1 minute
- Scoring: < 1 minute
- Validation: < 1 minute
- **Total:** ~45 minutes (mostly unattended)

---

**Next:** Review `IMPLEMENTATION_PLAN.md` for conceptual overview, or start implementing data collection scripts.
