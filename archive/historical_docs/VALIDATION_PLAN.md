# Problem Validation Plan

## Objective

Validate whether TS% ratio systematically fails to identify players who elevate their total production in playoffs despite efficiency decline.

## Hypothesis

Certain players (like Jimmy Butler) consistently elevate their total production in playoffs even when TS% declines. TS% ratio alone fails to identify these players.

## Validation Approach

### Phase 1: Multi-Season Data Collection

**Seasons Analyzed**: 2015-16, 2016-17, 2017-18, 2018-19, 2021-22, 2022-23, 2023-24
- Excludes: 2019-20 (COVID bubble), 2020-21 (play-in tournament)

**Filters**:
- ≥20% usage in regular season
- ≥4 playoff games
- ≥15 minutes per playoff game

**Metrics Calculated**:
1. **TS% Ratio**: `Playoff TS% ÷ Regular Season TS%`
2. **Production Ratio**: `Playoff Production ÷ Regular Season Production`
   - Production = `PTS + 1.5×AST + 0.5×REB` (per game)
3. **Disagreement Score**: `|TS% Ratio - Production Ratio|`

### Phase 2: Failure Identification

**Type 1 Failure** (Critical):
- TS% says "fragile" (<0.95)
- Production says "resilient" (>1.05)
- Example: Butler 2022-23 (TS% 0.873, Production 1.154)

**Type 2 Failure** (Less Critical):
- TS% says "resilient" (>1.05)
- Production says "fragile" (<0.95)

### Phase 3: Consistency Analysis (The "Butler Test")

For players with 3+ playoff seasons:
- Count seasons showing Type 1 failure
- Calculate consistency score: `Type 1 Failures ÷ Total Seasons`
- Identify "Consistent Overperformers": ≥50% of seasons show Type 1 failure

### Phase 4: Problem Scope Quantification

**Metrics**:
1. Overall Type 1 failure rate (% of all cases)
2. High-usage Type 1 failure rate (% of ≥25% usage players)
3. Number of consistent overperformers
4. Correlation between TS% ratio and Production ratio

### Phase 5: Known Cases Validation

**Test Cases**:
- **Jimmy Butler**: Should show Type 1 failure in multiple seasons
- **Jamal Murray**: Should show agreement (not Type 1 failure)
- **Ben Simmons**: Should show agreement (not Type 1 failure)

## Success Criteria

### Problem Validated If:
- Type 1 failures: ≥10% of cases
- Consistent overperformers: ≥3 players
- Correlation: <0.7 between TS% and Production
- Butler shows Type 1 failure in ≥2 seasons

### Problem Not Validated If:
- Type 1 failures: <5% of cases
- Consistent overperformers: 0-2 players
- Correlation: >0.9 between TS% and Production

## Usage

```bash
# Run validation
python validate_problem_exists.py
```

**Outputs**:
- `data/problem_validation_data.csv` - Raw data for all player-seasons
- `data/problem_validation_report.md` - Comprehensive validation report

## Next Steps Based on Results

### If Problem Validated:
1. Proceed with composite metric validation
2. Test if composite metric fixes Type 1 failures
3. Compare composite accuracy vs TS% baseline

### If Problem Not Validated:
1. Archive composite approach
2. Accept TS% ratio as sufficient
3. Focus on understanding TS% limitations rather than fixing them

