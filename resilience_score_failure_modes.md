# Resilience Score Failure Modes & Solutions

## Critical Issue: Usage Rate Changes

### The Problem
Players who increase usage in the playoffs typically see TS% decline due to:
- Taking harder shots (more contested, later in shot clock)
- Less selective shot-taking (forced to create offense)
- Increased defensive attention
- Fatigue from higher minutes

**Example:** A player goes from 20% usage (TS% = 60%) to 30% usage (TS% = 55%). 
- Raw calculation: 55/60 = 91.7% → penalized for "decline"
- Reality: Maintaining 55% TS% at 30% usage is elite performance

### Solution: Usage-Adjusted Efficiency

**Option 1: Expected Efficiency Model**
```
1. Build regression model: TS% = f(usage_rate) using regular season data
2. For each player, calculate expected TS% at playoff usage rate
3. Compare actual playoff TS% vs expected TS% at that usage
4. Usage_Adjusted_TS%_Delta = Actual_Playoff_TS% / Expected_TS%_at_Playoff_Usage
```

**Option 2: Usage Tier Comparison**
```
1. Segment regular season games by usage tiers:
   - Low: <20%
   - Medium: 20-25%
   - High: 25-30%
   - Very High: >30%

2. Calculate player's TS% within each usage tier during regular season
3. If playoff usage falls in "High" tier, compare playoff TS% to regular season "High" tier TS%
4. This controls for usage level rather than penalizing usage increase
```

**Option 3: League-Wide Usage-Efficiency Curve**
```
1. Calculate league-average TS% at each usage rate (using all players, all seasons)
2. For each player:
   - Expected_TS%_at_playoff_usage = league_avg_TS%_at_that_usage
   - Player_TS%_vs_expected = player_TS% / Expected_TS%
   - This measures: "How much better is this player than average at this usage level?"
```

**Recommended Approach:** Combine Option 1 + Option 2
- Use player-specific usage-efficiency curve (Option 1) as primary
- Use usage tier comparison (Option 2) as validation/sanity check
- This accounts for both player-specific tendencies and general usage-efficiency tradeoff

---

## Other Non-Obvious Failure Modes

### 1. Small Sample Size Bias (Playoff Games)

**The Problem:**
- Regular season: 82 games → stable statistics
- Playoffs: 4-28 games → high variance, statistical noise
- A player could have "bad" 4-game series despite being resilient
- Or "lucky" hot streak that doesn't reflect true ability

**Failure Mode:**
- Single playoff series can skew entire resilience score
- Players with fewer playoff games get penalized/rewarded by noise
- Cannot distinguish signal from noise

**Solutions:**
- **Bayesian Approach:** Regular season as prior, playoff as likelihood → posterior estimate
  ```
  Posterior_TS% = (Prior_TS% × Prior_Weight + Playoff_TS% × Playoff_Weight) / Total_Weight
  Where weights are based on sample size (games/minutes)
  ```
- **Minimum Sample Size Threshold:** Require 10+ playoff games for reliable metrics
- **Confidence Intervals:** Report resilience score with uncertainty bounds
- **Multi-Season Aggregation:** Combine multiple playoff runs for same player

---

### 2. Opponent Quality Differences

**The Problem:**
- Regular season: Mix of good/bad teams
- Playoffs: Only good teams (top 16 in league)
- Average playoff opponent is significantly better defensively
- League-wide efficiency drops in playoffs (harder for everyone)

**Failure Mode:**
- Player maintains same efficiency vs better opponents → actually improved
- But raw comparison shows "decline" because league context changed
- Comparing apples (regular season context) to oranges (playoff context)

**Solutions:**
- **Opponent-Adjusted Metrics:** Weight by opponent defensive rating
  ```
  Adjusted_TS% = TS% × (League_Avg_DRTG / Opponent_DRTG)
  ```
- **League-Wide Context Adjustment:** 
  ```
  Context_Adjusted_Delta = Player_Delta - League_Average_Delta
  If league TS% drops 3% in playoffs, and player drops 2%, they're actually +1% resilient
  ```
- **Relative Performance:** Compare player's percentile rank (regular season) vs percentile rank (playoffs)
  - If player was 80th percentile in regular season and 75th percentile in playoffs
  - They maintained relative position despite harder context

---

### 3. Role Changes & Context Shifts

**The Problem:**
- Player might be asked to do different things in playoffs
- Example: 3&D role player → primary creator due to injury
- Or: Primary scorer → facilitator due to defensive attention
- Role change ≠ skill decline

**Failure Mode:**
- Method Resilience score penalizes players for adapting role
- Diversity score might decrease if player specializes in new role
- But this specialization might be optimal team strategy

**Solutions:**
- **Role-Aware Analysis:** Track position/role changes separately
- **Intentional vs Forced Changes:** Distinguish between:
  - Intentional: Coach asks player to do X (strategic)
  - Forced: Player can't do Y anymore (decline)
- **Team Context:** Adjust for teammate quality changes (injuries, trades)

---

### 4. Shot Quality Changes (Teammate-Dependent)

**The Problem:**
- Player's TS% depends on shot quality
- Shot quality depends on teammates creating open shots
- In playoffs, teammates might:
  - Face better defense (harder to create open shots)
  - Get injured (worse shot creators)
  - Get schemed against (defense takes away easy shots)

**Failure Mode:**
- Player's TS% drops, but it's because teammates create worse shots
- Not because player got worse
- Current framework conflates player skill with team context

**Solutions:**
- **Shot Quality Metrics:** Use shot dashboard data (defender distance, shot clock)
  - Compare: Regular season shot quality vs Playoff shot quality
  - If shot quality drops, adjust expectations
- **Expected Points Model:** 
  ```
  Expected_Points = Σ(shot_attempts × league_avg_points_per_shot_at_that_quality)
  Player_Value_Added = Actual_Points - Expected_Points
  Compare Value_Added in regular season vs playoffs
  ```
- **Assist Quality:** Track how many open shots player creates for teammates
  - If player's assists lead to better shots in playoffs → resilient facilitator

---

### 5. Defensive Attention Changes

**The Problem:**
- In playoffs, defenses scheme specifically against star players
- Double teams, traps, help defense all increase
- Player faces harder shots even if same usage
- But also creates more open shots for teammates (not captured in TS%)

**Failure Mode:**
- Player's individual TS% drops due to defensive attention
- But team offense improves (player draws attention, teammates benefit)
- Current framework only measures individual efficiency, misses team impact

**Solutions:**
- **On/Off Court Impact:** Compare team efficiency when player on vs off court
- **Assist Quality:** Measure points created via assists (not just TS% of own shots)
- **Defensive Attention Metrics:** Track double-team rate, help defense frequency
- **Team-Context Adjusted:** If team ORTG improves despite player TS% drop → resilient

---

### 6. Age/Development Effects (Longitudinal Confound)

**The Problem:**
- Young players naturally improve year-over-year
- Old players naturally decline year-over-year
- Longitudinal analysis conflates:
  - Natural development/decline
  - True resilience improvement/decline

**Failure Mode:**
- Giannis improves resilience 2017-2021 → skill expansion OR natural development?
- LeBron declines resilience 2015-2020 → less resilient OR just older?

**Solutions:**
- **Age-Adjusted Trajectories:** Compare player to age-matched peers
  ```
  Expected_Resilience_at_Age = f(age, position, historical_data)
  Adjusted_Resilience = Actual_Resilience - Expected_Resilience_at_Age
  ```
- **Cohort Analysis:** Compare to players who entered league same year
- **Prime-Adjusted:** Separate analysis for:
  - Pre-prime (age 19-24): Expect improvement
  - Prime (age 25-30): Expect stability
  - Post-prime (age 31+): Expect decline

---

### 7. Minutes/Rest Differences

**The Problem:**
- Playoff rotations shorten (starters play more minutes)
- Less rest between games
- Fatigue accumulates over series
- Player might be less efficient due to fatigue, not skill

**Failure Mode:**
- TS% drops in playoffs → looks like decline
- But might just be fatigue from 40+ minutes vs 32 minutes

**Solutions:**
- **Per-Minute Normalization:** Compare efficiency per 36 minutes, not per game
- **Rest-Adjusted:** Account for days of rest between games
- **Minutes Tier Analysis:** Compare playoff efficiency at playoff minutes vs regular season efficiency at similar minutes
- **Fatigue Modeling:** Track efficiency by game number in series (Game 1 vs Game 7)

---

### 8. Statistical Noise in Small Categories

**The Problem:**
- Method Resilience uses HHI on multiple categories
- Some categories have very few attempts (e.g., 5 corner 3 attempts)
- Small sample sizes → high variance → unreliable diversity scores
- One hot/cold streak in small category skews entire diversity score

**Failure Mode:**
- Player takes 2 corner 3s in regular season (both miss) → 0% eFG%
- Player takes 2 corner 3s in playoffs (both make) → 100% eFG%
- Massive swing in weighted volume for that zone
- Skews spatial diversity score despite being noise

**Solutions:**
- **Minimum Volume Thresholds:** Only include categories with N+ attempts (e.g., 20+ shots)
- **Bayesian Smoothing:** Shrink small-sample estimates toward league average
  ```
  Smoothed_eFG% = (Player_eFG% × Attempts + League_Avg_eFG% × Prior_Weight) / (Attempts + Prior_Weight)
  ```
- **Confidence-Weighted Diversity:** Weight diversity components by sample size
  ```
  Weighted_Diversity = Σ(Diversity_Component_i × Confidence_i) / Σ(Confidence_i)
  Where Confidence = min(1, attempts / threshold)
  ```

---

### 9. League-Wide Efficiency Changes Over Time

**The Problem:**
- NBA efficiency changes year-to-year (rule changes, style evolution)
- 2017 league TS% ≠ 2024 league TS%
- Comparing across seasons uses different baselines
- Longitudinal analysis confounds player change with league change

**Failure Mode:**
- Player's TS% stays constant 2017-2024
- But league TS% increased 2% over that period
- Player actually declined relative to league, but absolute comparison shows stability

**Solutions:**
- **League-Relative Metrics:** Always compare to league average for that season
  ```
  Relative_TS% = Player_TS% / League_Avg_TS%
  Compare Relative_TS% across seasons, not absolute TS%
  ```
- **Z-Score Normalization:** 
  ```
  Z_Score = (Player_TS% - League_Mean_TS%) / League_StdDev_TS%
  Compare Z-scores across seasons (standardized units)
  ```

---

### 10. Position/Role Mismatch

**The Problem:**
- Different positions have different efficiency baselines
- Centers: Higher TS% (more shots at rim)
- Guards: Lower TS% (more 3s, pull-ups)
- Comparing diversity scores across positions is apples-to-oranges

**Failure Mode:**
- Center: High spatial diversity (rim + mid-range + 3s) = 70
- Guard: High spatial diversity (3s + mid-range + drives) = 70
- But center's "diversity" is easier (rim shots are high-efficiency)
- Guard's "diversity" is harder (3s and mid-range are lower-efficiency)

**Solutions:**
- **Position-Adjusted Baselines:** Compare to position-specific league averages
- **Position-Relative Scores:** Percentile rank within position, not absolute score
- **Role-Aware Analysis:** Separate analysis for:
  - Primary creators (usage >25%)
  - Secondary creators (usage 15-25%)
  - Role players (usage <15%)

---

### 11. Injury Effects (Playing Hurt)

**The Problem:**
- Players often play through injuries in playoffs
- Injury reduces efficiency, not resilience
- But framework interprets as "not resilient"

**Failure Mode:**
- Kawhi Leonard plays through knee injury
- TS% drops significantly
- Framework says "not resilient"
- But if healthy, would be resilient

**Solutions:**
- **Injury-Adjusted Analysis:** Flag known injury seasons/games
- **Health Status Tracking:** Use injury reports, minutes restrictions as signals
- **Sensitivity Analysis:** Report resilience scores with/without injury-affected games

---

### 12. Team System Changes (Coaching Adjustments)

**The Problem:**
- Different coaches use players differently
- System changes affect shot distribution (not player skill)
- Player might look "less diverse" in new system
- But it's coaching, not player decline

**Failure Mode:**
- Player traded to new team with different system
- Shot distribution changes (coach's preference)
- Method Resilience score drops
- But player skill unchanged

**Solutions:**
- **Team-Context Tracking:** Flag team/coach changes
- **System-Aware Analysis:** Compare to players in same system
- **Intentional vs Forced:** Distinguish system-driven changes from skill-driven

---

### 13. Playoff Series-Specific Factors

**The Problem:**
- Matchup-specific: Player struggles vs specific defender/team
- Scheme-specific: Opponent has perfect defensive scheme for player
- Small sample: One bad matchup = entire playoff run looks bad

**Failure Mode:**
- Player faces perfect defensive matchup (e.g., Gobert vs small guard)
- Struggles in that series
- But would excel vs other playoff teams
- Framework penalizes for matchup-specific struggles

**Solutions:**
- **Matchup-Adjusted:** Weight by opponent defensive rating vs player type
- **Multi-Series Analysis:** If player has multiple playoff runs, aggregate across all
- **Matchup Context:** Track specific defender matchups, not just team

---

### 14. Facilitation Not Captured (The "Harden Problem")

**The Problem:**
- Current framework focuses on scoring efficiency (TS%)
- But some players create value through facilitation
- Player's TS% drops, but assists create better shots for teammates
- Team offense improves despite individual TS% decline

**Failure Mode:**
- James Harden: TS% drops, but creates 10+ open 3s per game for teammates
- Current framework: "Not resilient" (TS% declined)
- Reality: "Highly resilient" (team offense improved)

**Solutions:**
- **Points Created Metric:** TS% + (Assists × Expected_Points_Per_Assist)
- **On-Court Impact:** Team ORTG when player on court
- **Assist Quality:** Track shot quality of assisted shots (defender distance)
- **Facilitation Score:** Separate metric for passers vs scorers

---

## Recommended Implementation Priority

### Phase 1: Critical Fixes (Must Have)
1. **Usage-Adjusted Efficiency** - Addresses primary failure mode
2. **Small Sample Size Handling** - Bayesian approach for playoff games
3. **Opponent Quality Adjustment** - Context matters

### Phase 2: Important Fixes (Should Have)
4. **Shot Quality Adjustment** - Use shot dashboard data
5. **Facilitation Metrics** - Capture passing value
6. **League-Relative Metrics** - For longitudinal analysis

### Phase 3: Refinements (Nice to Have)
7. **Age-Adjusted Trajectories** - For longitudinal analysis
8. **Position-Adjusted Baselines** - Fair comparisons
9. **Injury Tracking** - Context awareness
10. **Role Change Detection** - Intentional vs forced

---

## Revised Performance Resilience Calculation

```
1. Calculate Usage-Adjusted TS%:
   - Build player-specific TS% = f(usage_rate) model from regular season
   - Expected_TS%_at_playoff_usage = model.predict(playoff_usage)
   - Usage_Adjusted_TS%_Delta = Playoff_TS% / Expected_TS%_at_Playoff_Usage

2. Calculate Opponent-Adjusted TS%:
   - Opponent_DRTG_Weighted = average opponent DRTG (weighted by games)
   - Adjusted_TS% = TS% × (League_Avg_DRTG / Opponent_DRTG_Weighted)
   - Apply to both regular season and playoffs

3. Calculate Shot Quality-Adjusted TS%:
   - Expected_Points = Σ(shots × league_avg_points_at_that_shot_quality)
   - Quality_Adjusted_TS% = Actual_Points / Expected_Points × League_Avg_TS%
   - Compare quality-adjusted TS% across seasons

4. Calculate Facilitation Value:
   - Points_Created_Via_Assists = Σ(assists × expected_points_per_assist)
   - Total_Value = TS%_Points + Points_Created_Via_Assists
   - Compare Total_Value across seasons

5. Combine with Bayesian Smoothing:
   - Regular_Season_TS%_Adjusted (prior, high weight)
   - Playoff_TS%_Adjusted (likelihood, low weight if few games)
   - Posterior_TS%_Adjusted = weighted_average
   - Performance_Resilience = Posterior_Playoff / Posterior_Regular_Season
```

---

## Key Insight: Resilience is Context-Dependent

The fundamental challenge: **Resilience cannot be measured in isolation.**

A player's "resilience" depends on:
- Their usage rate (higher usage = harder to maintain efficiency)
- Opponent quality (better opponents = harder to maintain efficiency)
- Shot quality (worse shots = harder to maintain efficiency)
- Team context (worse teammates = harder to maintain efficiency)
- Age/development (younger = expect improvement, older = expect decline)

**Solution:** Always adjust for context before comparing.
