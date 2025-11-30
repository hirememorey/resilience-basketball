# NBA Playoff Resilience Calculator

**Goal:** Identify "16-game players" who perform better than expected in the playoffs given their abilities and defensive context.

## Quick Start

### 1. Setup
```bash
pip install pandas numpy scikit-learn scipy tenacity requests
```

### 2. Collect Data
This step fetches data for Regular Season, Defense, and Playoff Game Logs.
**Note:** Playoff logs take time (~15 mins/season). Run in parallel for speed.

```bash
# Regular Season & Defense (Fast)
python src/nba_data/scripts/collect_regular_season_stats.py --seasons 2018-19 2022-23 2023-24
python src/nba_data/scripts/collect_defensive_context.py --seasons 2018-19 2022-23 2023-24

# Playoff Logs (Slower - Parallelize!)
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2018-19 &
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2022-23 &
python src/nba_data/scripts/collect_playoff_logs.py --seasons 2023-24 &
```

### 3. Run Analysis Pipeline
Once data collection is complete:

```bash
# Assemble dataset from logs
python src/nba_data/scripts/assemble_training_data.py

# Train regression models
python src/nba_data/scripts/train_resilience_models.py

# Generate scores
python src/nba_data/scripts/calculate_resilience_scores.py

# Validate against known stars
python src/nba_data/scripts/validate_face_validity.py

# Generate report
python src/nba_data/scripts/generate_report.py
```

**Output:** `results/resilience_report.md`

---

## Methodology

### The Core Question
"Given a player's regular season ability and the specific opponent defense they faced, did they perform better or worse than expected?"

### The Approach
1.  **Baseline:** Measure Regular Season TS%, Points/75, AST%, Usage.
2.  **Context:** Calculate Opponent Defensive Strength (Rating + eFG% + FTR).
3.  **Model:** Train regression models to predict *Expected Playoff Performance*.
4.  **Score:** `Resilience = (Actual - Expected) / StandardDeviation`.

### Why Game Logs?
We use **Game Logs** instead of Play-by-Play data because the NBA's PBP endpoint is unreliable. Game logs provide per-game granularity, allowing us to group performance by Opponent Series accurately.

---

## Project Structure

```
├── src/
│   └── nba_data/
│       ├── api/                    # NBA Stats API Client
│       └── scripts/                # Collection & Analysis Scripts
├── data/                           # CSV Data & Cache
├── models/                         # Trained Pickle Models
├── results/                        # Final Reports & Scores
├── IMPLEMENTATION_GUIDE.md         # Detailed manual
└── DATA_REQUIREMENTS.md            # Data specs
```
