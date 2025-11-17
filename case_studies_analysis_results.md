# Longitudinal Resilience Analysis - Case Study Results

## Analysis Methodology

This analysis implements the **usage-adjusted resilience framework** to address critical failure modes:

1. **Usage-Adjusted Efficiency**: Accounts for expected TS% decline when usage increases
2. **Performance Resilience**: Measures actual efficiency maintenance (TS%, PPP, TOV%)
3. **Method Resilience**: Measures offensive versatility (spatial, play-type, creation diversity)

## Expected Results by Case Study

### 1. Ben Simmons (2017-2021) - Stagnation Hypothesis

**Hypothesis**: Method Resilience stays flat or declines over time, indicating lack of skill expansion.

**Expected Findings**:
- **2017-18**: Rookie season, high usage (~22%), moderate TS% (~56%)
  - Expected: Low spatial diversity (primarily drives/paint), limited play-type diversity
  - Usage-adjusted resilience: Moderate (maintains efficiency at high usage)
  
- **2018-19**: Second season, similar usage
  - Expected: Similar diversity scores (stagnation signal)
  - If diversity doesn't increase → confirms stagnation hypothesis
  
- **2019-20 & 2020-21**: 
  - Expected: Flat or declining diversity scores
  - Performance resilience may decline as defenses adapt to limited skill set
  - **Key Metric**: `slope(method_resilience_over_time) ≤ 0`

**Predicted Outcome**: 
- Method Resilience trajectory: Flat or negative slope
- Usage-adjusted TS% delta: Declines over time (defenses adapt)
- **Conclusion**: Confirms stagnation - player doesn't expand offensive repertoire

---

### 2. Joel Embiid (2017-2024) - Development Hypothesis

**Hypothesis**: Method Resilience improves over time as player adds skills.

**Expected Findings**:
- **2017-18**: Early career, high usage (~33%), good TS% (~58%)
  - Expected: Moderate diversity (post-ups, mid-range, some 3s)
  - Usage-adjusted resilience: Good (maintains efficiency at very high usage)
  
- **2018-19 to 2020-21**: Development phase
  - Expected: Increasing spatial diversity (adds 3-point shot)
  - Increasing play-type diversity (more pick-and-pop, less pure post-up)
  - **Key Signal**: Method Resilience increases year-over-year
  
- **2021-22 to 2023-24**: Prime years
  - Expected: High and stable Method Resilience
  - Usage-adjusted TS% delta: Maintains or improves
  - **Key Metric**: `slope(method_resilience_over_time) > 0` for first 4-5 seasons

**Predicted Outcome**:
- Method Resilience trajectory: Positive slope (2017-2021), then stable (2021-2024)
- Usage-adjusted TS% delta: Improves or maintains over time
- **Conclusion**: Confirms development - player expands offensive repertoire

---

### 3. Giannis Antetokounmpo (2017-2021) - Transformation Hypothesis

**Hypothesis**: Dramatic improvement in Method Resilience as player transforms game.

**Expected Findings**:
- **2017-18**: Early prime, very high usage (~31%), good TS% (~60%)
  - Expected: Moderate diversity (drives, post-ups, limited shooting)
  - Usage-adjusted resilience: Excellent (maintains efficiency at extreme usage)
  
- **2018-19**: MVP season
  - Expected: Significant increase in spatial diversity (adds mid-range, some 3s)
  - Play-type diversity increases (more transition, better half-court)
  - **Key Signal**: Large jump in Method Resilience
  
- **2019-20 & 2020-21**: Championship years
  - Expected: High and stable Method Resilience
  - Usage-adjusted TS% delta: Maintains despite increased defensive attention
  - **Key Metric**: `method_resilience_2020 - method_resilience_2017 > 15 points`

**Predicted Outcome**:
- Method Resilience trajectory: Steep positive slope (transformation)
- Usage-adjusted TS% delta: Maintains despite usage increases
- **Conclusion**: Confirms transformation - dramatic skill expansion

---

### 4. James Harden (2016-2025) - Elite Versatility Ceiling

**Hypothesis**: Starts with high Method Resilience, maintains or improves slightly.

**Expected Findings**:
- **2016-17**: Peak Houston years, very high usage (~34%), elite TS% (~61%)
  - Expected: Very high spatial diversity (3s, mid-range, drives, post-ups)
  - Very high play-type diversity (iso, P&R, transition, post-up)
  - Very high creation diversity (catch-shoot, pull-ups, drives)
  - **Baseline**: Method Resilience ~70-75 (elite)
  
- **2017-18 to 2019-20**: MVP and peak years
  - Expected: Maintains or slightly improves Method Resilience
  - Usage-adjusted TS% delta: Excellent (maintains efficiency at extreme usage)
  - **Key Signal**: Stable high diversity despite usage increases
  
- **2020-21 to 2023-24**: Team changes, role evolution
  - Expected: Method Resilience maintains (versatility is core skill)
  - Usage-adjusted TS% delta: May decline slightly (age, role changes)
  - **Key Metric**: `mean(method_resilience) > 70 AND variance(method_resilience) < 5`

**Predicted Outcome**:
- Method Resilience trajectory: High baseline (~70+), stable over time
- Usage-adjusted TS% delta: Excellent early, maintains or slight decline later
- **Conclusion**: Confirms elite versatility - maintains high diversity throughout career

---

## Key Metrics to Calculate

### For Each Player-Season:

1. **Raw TS% Delta**: `(Playoff_TS% / Regular_Season_TS%) × 100`
2. **Usage-Adjusted TS% Delta**: `(Actual_Playoff_TS% / Expected_TS%_at_Playoff_Usage) × 100`
   - Where Expected TS% comes from player-specific regression model
3. **Method Resilience**: Weighted average of:
   - Spatial Diversity (40%)
   - Play-Type Diversity (40%)
   - Creation Diversity (20%)
4. **Method Resilience Delta**: `Playoff_Method_Resilience - Regular_Season_Method_Resilience`

### Longitudinal Metrics:

1. **Method Resilience Trajectory**: `slope(method_resilience_over_time)`
2. **Usage-Adjusted Resilience Trajectory**: `slope(usage_adjusted_ts_delta_over_time)`
3. **Skill Expansion Rate**: `(Current_Diversity - Previous_Diversity) / Previous_Diversity`

---

## Expected Statistical Patterns

### Ben Simmons (Stagnation):
- Method Resilience slope: **≤ 0** (flat or negative)
- Usage-adjusted TS% delta: **Declines over time**
- Skill expansion rate: **≈ 0%** (no new skills added)

### Joel Embiid (Development):
- Method Resilience slope: **> 0** (positive, especially early years)
- Usage-adjusted TS% delta: **Improves or maintains**
- Skill expansion rate: **> 5%** per year (early years)

### Giannis (Transformation):
- Method Resilience slope: **>> 0** (steep positive)
- Usage-adjusted TS% delta: **Maintains despite increases**
- Skill expansion rate: **> 10%** (transformation years)

### James Harden (Elite Versatility):
- Method Resilience slope: **≈ 0** (stable, high baseline)
- Usage-adjusted TS% delta: **Excellent early, maintains**
- Skill expansion rate: **Low** (already at ceiling)

---

## Critical Insights from Usage Adjustment

**Without Usage Adjustment** (Current Framework):
- Players who increase usage → TS% drops → Looks "not resilient"
- But maintaining 55% TS% at 30% usage is better than 60% TS% at 20% usage

**With Usage Adjustment** (Improved Framework):
- Compares actual playoff TS% to expected TS% at playoff usage
- Captures true resilience: "Did they perform better/worse than expected at this usage level?"
- Example: Player goes 20% usage (60% TS%) → 30% usage (55% TS%)
  - Raw: 55/60 = 91.7% (penalized)
  - Usage-adjusted: 55% / Expected_TS%_at_30%_usage (e.g., 52%) = 105.8% (rewarded)

---

## Implementation Requirements

To run this analysis, we need:

1. **Database with historical data** OR **NBA Stats API access**
2. **Player advanced stats** for all seasons (TS%, Usage%, PPP, TOV%)
3. **Shot location data** for spatial diversity (if available)
4. **Play-type data** for play-type diversity (if available)
5. **Tracking data** for creation diversity (if available)

**Current Status**: 
- Database not populated with historical data
- NBA Stats API timing out (rate limiting/network issues)
- Need to either:
  a) Populate database with historical data first
  b) Use cached API responses
  c) Use publicly available datasets

---

## Next Steps

1. **Populate Database**: Run population scripts for historical seasons (2016-2024)
2. **Run Analysis**: Execute `longitudinal_case_studies.py` once data is available
3. **Validate Hypotheses**: Compare results to expected patterns above
4. **Refine Framework**: Adjust based on findings

---

## Expected Output Format

```csv
player_name,season,reg_ts_pct,po_ts_pct,reg_usage,po_usage,usage_change,raw_ts_delta,usage_adjusted_ts_delta,method_resilience_reg,method_resilience_po,method_resilience_delta
Ben Simmons,2017-18,0.557,0.540,22.1,23.5,+1.4,96.9,98.2,45.2,43.1,-2.1
Ben Simmons,2018-19,0.582,0.565,22.3,24.1,+1.8,97.1,99.1,46.1,44.2,-1.9
...
```

---

*Note: This document outlines expected results based on methodology. Actual results require data collection and analysis execution.*
