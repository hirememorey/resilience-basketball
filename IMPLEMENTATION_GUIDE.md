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

**Note:** We use a "Merge Strategy" for data collection. For both Regular Season and Playoffs, we fetch `Base` (for counting stats) and `Advanced` (for rate stats) endpoints and merge them. This ensures we have all necessary metrics (PTS, TS%, AST%, USG%) which are not available in a single call.

### 1.1 Create Regular Season Collector

**File:** `src/nba_data/scripts/collect_regular_season_stats.py`

**Purpose:** Fetch and store regular season player statistics (Base + Advanced).

**Key Functions:**
```python
def fetch_regular_season_stats(client, season):
    """
    Fetch regular season stats for all players in a season.
    Merges 'Base' and 'Advanced' endpoints.
    Returns: DataFrame with player stats
    """
    # 1. Fetch Base
    # 2. Fetch Advanced
    # 3. Merge on PLAYER_ID
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

**Purpose:** Fetch and calculate defensive context scores for all teams. Merges `Advanced` (for DEF_RATING) and `Opponent` (for eFG%/FTR) stats.

**Run:**
```bash
python src/nba_data/scripts/collect_defensive_context.py --seasons 2018-19 2022-23 2023-24
```

**Expected Output:**
- `data/defensive_context_2018-19.csv` (~30 rows)
- ...

---

### 1.3 Create Playoff Logs Collector (Robust Fallback)

**File:** `src/nba_data/scripts/collect_playoff_logs.py`

**Purpose:** Fetch playoff game logs for every player. Replaces the unreliable `playbyplayv2` endpoint.

**Why Logs?** The PlayByPlay endpoint is fragile. Game logs are robust and provide per-game granularity required for series-level analysis. We merge `Base` and `Advanced` logs to get full metrics.

**Key Functions:**
```python
def fetch_player_playoff_logs(client, player_id, season):
    """
    Fetch and merge Base and Advanced playoff game logs.
    """
    # 1. Fetch Base Logs
    # 2. Fetch Advanced Logs
    # 3. Merge on GAME_ID
    pass
```

**Run:**
```bash
# Run in parallel for speed (approx 40 mins total)
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2018-19 &
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2022-23 &
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2023-24 &
```

**Expected Output:**
- `data/playoff_logs_2018-19.csv` (~1700 rows)
- `data/playoff_logs_2022-23.csv` (~1700 rows)
- ...

---

### 1.4 Create Training Data Assembler

**File:** `src/nba_data/scripts/assemble_training_data.py`

**Purpose:** Combine all data sources into single training dataset. Aggregates game logs into series-level stats.

**Key Logic:**
- Parses `MATCHUP` string (e.g. "DEN vs. LAL") to identify opponent.
- Aggregates stats per Player-Opponent pair.
- Recalculates efficiency metrics from sums to avoid "average of averages" bias.
- Merges with Regular Season baseline.
- Merges with Opponent Defensive Context.

**Run:**
```bash
python src/nba_data/scripts/assemble_training_data.py --output data/training_dataset.csv
```

**Expected Output:**
- `data/training_dataset.csv` (~600-1000 rows)

---

## Step 2: Model Training

### 2.1 Create Model Training Script

**File:** `src/nba_data/scripts/train_resilience_models.py`

**Purpose:** Train three regression models for TS%, PPG, and AST%.

**Run:**
```bash
python src/nba_data/scripts/train_resilience_models.py
```

**Expected Output:**
- `models/ts_pct_model.pkl`
- `models/ppg_per75_model.pkl`
- `models/ast_pct_model.pkl`
- `models/model_metadata.pkl`

---

## Step 3: Generate Resilience Scores

### 3.1 Create Scoring Script

**File:** `src/nba_data/scripts/calculate_resilience_scores.py`

**Purpose:** Generate resilience scores for all player-series combinations.

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

**Run:**
```bash
python src/nba_data/scripts/validate_face_validity.py
```

---

## Step 5: Generate Final Report

### 5.1 Create Reporting Script

**File:** `src/nba_data/scripts/generate_report.py`

**Run:**
```bash
python src/nba_data/scripts/generate_report.py --output results/resilience_report.md
```

---

## Quick Start Summary

```bash
# 1. Collect data (Run in parallel, approx 40 mins)
python src/nba_data/scripts/collect_regular_season_stats.py --seasons 2018-19 2022-23 2023-24 &
python src/nba_data/scripts/collect_defensive_context.py --seasons 2018-19 2022-23 2023-24 &
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2018-19 &
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2022-23 &
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2023-24 &

# Wait for completion...

# 2. Assemble training data
python src/nba_data/scripts/assemble_training_data.py

# 3. Train models
python src/nba_data/scripts/train_resilience_models.py

# 4. Generate scores
python src/nba_data/scripts/calculate_resilience_scores.py

# 5. Validate & Report
python src/nba_data/scripts/validate_face_validity.py
python src/nba_data/scripts/generate_report.py
```
