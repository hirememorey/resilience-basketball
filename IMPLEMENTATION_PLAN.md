# NBA Playoff Resilience: First Principles Implementation Plan

## Executive Summary

**Goal:** Identify "16-game players" who perform better than expected in the playoffs given their abilities and defensive context.

**Approach:** Regression-based expected performance model that compares actual playoff performance to statistical expectations.

**Core Question:** "Given a player's demonstrated abilities and the specific defensive context they faced, how does their actual playoff performance compare to what we would statistically expect?"

## The Three-Component System

### 1. Player Ability Baseline
Regular season performance metrics representing their "true skill" without playoff pressure.

### 2. Contextual Difficulty
Quantified defensive quality of opponents faced in playoffs.

### 3. Expected Performance Model
Statistical model predicting playoff performance given #1 and #2.

## Phase 1: Player Ability Baseline

### Data to Collect (Regular Season)
For each player, calculate:
- **Efficiency:** TS% (True Shooting Percentage)
- **Volume:** Points per 75 possessions (pace-adjusted)
- **Playmaking:** AST% (Assist Percentage)
- **Usage:** Usage% (measure of role/responsibility)

### Filtering Criteria
- Minimum 50 games played in regular season
- Minimum 20 MPG average
- Ensures statistical significance

### Storage Format
CSV with columns: `player_id, season, regular_season_TS%, regular_season_PPG_per75, regular_season_AST%, regular_season_Usage%`

## Phase 2: Defensive Context Quantification

### For Each Opponent Team's Defense

Calculate:
- **Defensive Rating:** Points allowed per 100 possessions
- **Opponent eFG%:** Effective Field Goal % allowed
- **Opponent FT Rate:** Opponent Free Throw Rate (FTA/FGA allowed)

### Dynamic Playoff Adjustment

**Key Insight:** Regular season defense ≠ playoff defense

**Approach:**
- If playoff sample < 10 games: Use regular season defensive metrics
- If playoff sample ≥ 10 games: Use playoff-specific defensive metrics
- This creates dynamic defensive context

### Output
Defensive Context Score (DCS) for each opponent team: Composite of defensive metrics, scaled 0-100 (league average = 50)

## Phase 3: Expected Performance Model

### Statistical Approach: Multiple Linear Regression

Build **three separate models** for key metrics:

**Model 1: Playoff TS%**
```
Expected_Playoff_TS% = β₀ + β₁(RS_TS%) + β₂(Def_Context_Score) + β₃(Usage%) + β₄(RS_TS% × Def_Context_Score) + ε
```

**Model 2: Playoff Points per 75 Possessions**
```
Expected_Playoff_PPG = β₀ + β₁(RS_PPG) + β₂(Def_Context_Score) + β₃(Usage%) + β₄(RS_PPG × Def_Context_Score) + ε
```

**Model 3: Playoff AST%**
```
Expected_Playoff_AST% = β₀ + β₁(RS_AST%) + β₂(Def_Context_Score) + β₃(Usage%) + β₄(RS_AST% × Def_Context_Score) + ε
```

### Why Interaction Terms?
The interaction term (RS_Metric × Def_Context_Score) captures that high-skill players maintain performance better against good defenses than low-skill players.

### Training Requirements
- Historical playoff data: Last 5-10 seasons
- Minimum: 100 player-series observations
- Train/test split: 80/20
- Cross-validate on held-out seasons

## Phase 4: Calculate Resilience Scores

### For Each Player-Series Combination

**Step 1: Generate Expected Performance**
Run player's regular season stats + opponent defensive context through trained models.

**Step 2: Calculate Actual Performance**
From playoff play-by-play (with garbage time filtered):
- Actual TS%
- Actual Points per 75
- Actual AST%

**Step 3: Calculate Residuals**
```
Efficiency_Residual = Actual_TS% - Expected_TS%
Volume_Residual = Actual_PPG - Expected_PPG
Creation_Residual = Actual_AST% - Expected_AST%
```

**Step 4: Standardize to Z-scores**
```
Z_Score = (Actual - Expected) / Standard_Error_of_Model
```

**Step 5: Composite Score**
```
Composite_Resilience = 0.35×Z_Efficiency + 0.25×Z_Volume + 0.25×Z_Creation + 0.15×Z_Stability
```
- Stability = inverse of game-to-game variance

### Interpretation
- **0.0** = Exactly as expected
- **+1.0** = 1 standard deviation better than expected
- **+2.0** = Elite playoff riser
- **-1.0** = Underperformed expectations
- **-2.0** = Significant playoff decline

## Phase 5: Contextual Adjustments

### Garbage Time Filter
**Remove possessions where:**
- Game is in 4th quarter or overtime
- Score differential ≥ 15 points
- Time remaining ≤ 5 minutes

This focuses analysis on competitive basketball only.

### Leverage Weighting (Optional for V1)
Weight close-game performance more heavily:
- Score within 5 points in last 5 minutes = 1.5× weight
- All other possessions = 1.0× weight

## Phase 6: Validation

### Face Validity Test
**Known elite playoff performers should score high:**
- LeBron James (2012-2018)
- Kawhi Leonard (2019)
- Nikola Jokić (2023)
- Dirk Nowitzki (2011)

**Test:** Run model on historical data and verify these players have positive resilience scores.

### Statistical Validation
- Check model residuals are normally distributed
- Verify no systematic biases by position or team
- Ensure R² ≥ 0.3 for predictive power

## Phase 7: Output Format

### Final CSV Structure
```
player_id, player_name, season, series_round, opponent_team,
regular_season_TS%, regular_season_PPG_per75, regular_season_AST%, regular_season_Usage%,
opponent_def_rating, opponent_def_context_score,
expected_playoff_TS%, expected_playoff_PPG_per75, expected_playoff_AST%,
actual_playoff_TS%, actual_playoff_PPG_per75, actual_playoff_AST%,
efficiency_resilience_zscore, volume_resilience_zscore, creation_resilience_zscore,
composite_resilience_score, 
confidence_interval_lower, confidence_interval_upper,
games_played, minutes_played
```

## Implementation Sequence

### Week 1: Data Collection
1. Fetch regular season player stats (5+ seasons)
2. Fetch opponent defensive metrics
3. Fetch playoff play-by-play data
4. Apply garbage time filter
5. Store in structured format

### Week 2: Model Training
1. Prepare training dataset (player baselines + defensive context + actual playoff performance)
2. Train three regression models (TS%, PPG, AST%)
3. Validate models on held-out season
4. Document model coefficients and R² values

### Week 3: Scoring System
1. Generate expected performance for all player-series
2. Calculate residuals
3. Standardize to Z-scores
4. Calculate composite scores
5. Generate output CSV

### Week 4: Validation
1. Face validity checks (known cases)
2. Statistical validation (residual analysis)
3. Documentation of results
4. Refinement based on findings

## Key Principles

### 1. Simplicity First
Start with the minimal viable model. Don't add complexity without proven value.

### 2. Validate Continuously
Test assumptions at each step. If something seems wrong, investigate before proceeding.

### 3. Interpretability Matters
A GM should understand what the score means. Complex black-box models fail this test.

### 4. Reality Check Required
Statistical significance doesn't equal practical validity. Test against known cases.

## Common Pitfalls to Avoid

### ❌ Over-fitting to Recent Data
Use multiple seasons for training, validate on held-out seasons.

### ❌ Ignoring Context
Defensive quality matters. A player facing elite defenses should get credit for maintaining performance.

### ❌ Ratio-Based Metrics Without Context
Simple ratios (Playoff TS% / Regular Season TS%) penalize elite performers. Use expected performance instead.

### ❌ Small Sample Bias
Players with 2-3 playoff games produce unreliable scores. Set minimum thresholds.

### ❌ Adding Features Without Validation
Every additional feature adds complexity. Require proof of improvement (>3% accuracy gain).

## Success Criteria

### Minimum Viable Product (V1)
- [ ] Models trained on 5+ seasons
- [ ] R² ≥ 0.3 for primary metrics
- [ ] Passes face validity test (known cases)
- [ ] Produces interpretable scores
- [ ] CSV output generated

### Stretch Goals (V2)
- [ ] Leverage weighting implemented
- [ ] Teammate quality adjustment
- [ ] Predictive validation (early playoff → later playoff)
- [ ] Confidence intervals calculated

## Data Sources

### Primary: NBA Stats API
- Regular season stats: `stats.nba.com/stats/leaguedashplayerstats`
- Defensive ratings: `stats.nba.com/stats/leaguedashteamstats`
- Playoff play-by-play: `stats.nba.com/stats/playbyplayv2`

### Existing Infrastructure
- API client: `src/nba_data/api/nba_stats_client.py`
- Caching: Implemented with tenacity retries
- Error handling: Built-in with rate limiting

## Next Steps

1. **Read:** `DATA_REQUIREMENTS.md` for detailed data specifications
2. **Review:** `HISTORICAL_CONTEXT.md` for project evolution (optional)
3. **Start:** `IMPLEMENTATION_GUIDE.md` for step-by-step coding instructions

---

**Philosophy:** This approach measures what matters—performance relative to expectations—rather than arbitrary thresholds or ratios. It's grounded in statistical principles, validated against reality, and interpretable for decision-makers.
