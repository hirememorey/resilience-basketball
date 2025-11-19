# Extended Playoff Resilience Framework

## Current State: Where We Are Now

### Project Overview
This project analyzes NBA player performance to identify factors that predict playoff resilience—the ability to maintain or exceed regular-season production in the postseason. We have a complete data pipeline with comprehensive player statistics, shot location data, game logs, and both regular-season and playoff metrics across 10 seasons (2015-16 through 2024-25).

### Existing Framework (Implemented)
We have a **Four-Pathway Resilience Framework** that measures multiple dimensions of playoff adaptability:

1. **Versatility Resilience (The "How")**: Stability of offensive method diversity across three sub-pillars:
   - **Spatial Diversity**: Efficiency and volume from different court zones
   - **Play-Type Diversity**: Efficiency and usage across offensive sets (Isolation, P&R, Transition, etc.)
   - **Creation Diversity**: Ability to score through different methods (Catch & Shoot, Pull-ups, Drives)

2. **Dominance Resilience (The "Quality")**: Shot Quality-Adjusted Value measuring efficiency vs. league averages under contest

3. **Primary Method Mastery (The "Specialization")**: Elite efficiency in dominant offensive method

4. **Role Scalability (The "Adaptability")**: Efficiency maintenance when usage increases from regular season to playoffs

The framework uses a **Herfindahl-Hirschman Index (HHI)** for versatility, **Shot Quality-Adjusted Value (SQAV)** for dominance, **efficiency benchmarking** for mastery, and **usage change analysis** for scalability, all converted to 0-100 scales.

### The Gap: What's Missing
While the current framework captures four major pathways to playoff success, one critical analysis remains:

- **Longitudinal Evolution (The "Neuroplasticity Coefficient")**: Testing the hypothesis that early-career learning rate predicts future resilience better than age or athleticism.

**Data Status:**
- ✅ **Game Logs:** Complete (272,276 records, 10 seasons)
- ✅ **Shot Dashboard Historical:** Complete (59,622 records across 10 seasons)
- ✅ **Tracking Stats:** Complete (10 seasons)
- ✅ **Shot Locations:** Complete (9 seasons)
- ✅ **League Averages:** Complete (10 seasons)

This document outlines the complete framework, including the new implementation plan for the Neuroplasticity analysis.

---

## Extended Framework: Four New Metrics

### 1. Primary Method Mastery: Measuring Elite Specialization

#### Core Question
How efficient is the player's primary offensive method, and is it strong enough to remain effective even when schemed against?

#### Calculation Approach

**Step 1: Identify Primary Method**
- For each player, determine their highest-volume method across:
  - Spatial zones (Restricted Area, Paint, Mid-Range, Corner 3, Above Break 3)
  - Play types (Isolation, Pick & Roll, Transition, Post-Up, etc.)
  - Creation methods (Catch & Shoot, Pull-Ups, Drives)
- Primary method = highest weighted volume (volume × efficiency relative to league average)

**Step 2: Measure Absolute Efficiency**
- Use efficiency metrics appropriate to the method:
  - Shooting methods: TS% or eFG%
  - Play types: Points Per Possession (PPP)
  - Creation methods: Points Per Attempt or Points Per Drive
- Compare to historical benchmarks:
  - Percentile rank among all players in that method (all-time or recent era)
  - Distance from elite threshold (e.g., 90th percentile)
  - Standard deviations above mean

**Step 3: Measure Playoff Resistance**
- Compare primary method efficiency: regular season vs. playoffs
- Calculate efficiency retention: `Playoff_Efficiency / Regular_Season_Efficiency`
- If efficiency holds or improves → dominance confirmed
- If efficiency drops significantly → vulnerability despite high regular-season efficiency

**Step 4: Calculate Dominance Score**
- Base score: absolute efficiency percentile (0-100)
- Resilience multiplier: playoff efficiency / regular season efficiency (capped at 1.2)
- Final score: `Base_Score × Resilience_Multiplier`
- Interpretation: 80+ = elite dominance; 60-80 = strong; <60 = not dominant enough

---

### 2. Role Scalability: Efficiency at Different Usage Rates

#### Core Question
Can the player maintain efficiency when usage increases in the playoffs?

#### Calculation Approach

**Step 1: Define Usage Tiers**
- Segment regular-season games by usage rate:
  - Low usage: <20%
  - Medium usage: 20-25%
  - High usage: 25-30%
  - Very high usage: >30%
- For each tier, calculate:
  - Average TS%
  - Average PPP
  - Average TOV%

**Step 2: Measure Efficiency Slope**
- Plot efficiency (TS%) vs. usage rate
- Calculate regression slope: `Efficiency_Change = β × Usage_Change`
- Positive slope = efficiency improves with usage (scalable)
- Negative slope = efficiency declines with usage (not scalable)
- Flat slope = efficiency independent of usage (consistent)

**Step 3: Measure Playoff Usage Change**
- Compare playoff usage rate to regular-season average
- If playoff usage > regular-season average → test scalability
- If playoff usage ≤ regular-season average → scalability less relevant

**Step 4: Calculate Role Scalability Score**
- Efficiency slope score: convert slope to 0-100 scale
  - Positive slope → higher score
  - Negative slope → lower score
- Usage-adjusted efficiency: expected efficiency at playoff usage vs. actual playoff efficiency
  - If actual ≥ expected → scalable
  - If actual < expected → not scalable
- Final score: weighted average of slope score and usage-adjusted performance

---

### 3. Dominance Score (Shot Quality-Adjusted Value): Efficiency Under Duress

#### Core Question
Does the player have the ability to create and convert high-difficulty scoring opportunities against dedicated defensive pressure, independent of scheme?

#### Calculation Approach: Shot Quality-Adjusted Value (SQAV)

**Step 1: Establish Baselines for Every Shot Context**
- Using our comprehensive shot dashboard data (`player_shot_dashboard_stats`), we calculate the league-average Effective Field Goal Percentage (eFG%) for every combination of:
  - **Defender Distance**: Very Tight (0-2ft), Tight (2-4ft), Open (4-6ft), Wide Open (6+ft)
  - **Creation Method**: Catch & Shoot (0 dribbles), 1 Dribble, 2 Dribbles, Moderate (3-6), Extensive (7+)
  - **Shot Clock Pressure**: Very Late (4-0s), Late (7-4s), Average (15-7s), etc.
- This creates a detailed "Expected eFG%" (xeFG%) for any conceivable shot attempt.

**Step 2: Calculate Player's Efficiency vs. Expected Efficiency (eFG% Above Expected)**
- For each player, we compare their actual eFG% in each specific shot context to the league-average baseline (xeFG%) for that same context.
- `eFG_Above_Expected = Player_eFG_in_Context - xeFG_in_Context`
- A positive value indicates better-than-average shot-making for that shot type; a negative value indicates worse.

**Step 3: Weight by Shot Volume and Difficulty**
- The value generated in each context is weighted by the player's attempt volume in that context. This rewards players who not only make tough shots but do so frequently.
- `Context_Value = eFG_Above_Expected × Shot_Attempts_in_Context`

**Step 4: Aggregate to a Single Dominance Score**
- The final Dominance Score is the sum of the `Context_Value` generated across all shot contexts, representing the total shot-making value a player provides above an average player.
- `Dominance Score = SUM(all_contexts(Context_Value))`
- This score is then normalized (e.g., to a 0-100 scale or as a percentile rank) for comparison.

---

### 4. Longitudinal Evolution: The "Neuroplasticity Coefficient"

#### Core Question
Does the player's rate of skill acquisition in their first 3 seasons ($N_c$) predict their future playoff resilience better than draft age or athleticism?

**Current GM Thinking:** "Potential" is based on age (20 vs 24) and body type.
**First Principles Reality:** Improvement is a skill. Some players have high "neuroplasticity" (learning rate), others are static.

#### Implementation Plan (Refined via Post-Mortem)

**CRITICAL LESSONS LEARNED:**
1.  **Efficiency Floor:** Volume alone is noise. Ben Simmons "attempted" mid-range shots but didn't "learn" them. A skill is only acquired if Efficiency > (League Avg - 5%).
2.  **Coordinate Truth:** Do not trust `shot_zone_basic` strings. Use raw `loc_x` and `loc_y` to define zones (e.g., Floater Range vs. Rim).
3.  **Prodigy Paradox:** Segment "Day 1 Starters" (High Usage Rookies) from "Raw Prospects" (Low Usage). The signal is strongest in the latter.

**Step 1: The "Skill Test" (Unit Test)**
- **Objective:** Calibrate thresholds before running full analysis.
- **Test Case:**
  - **Ben Simmons (2016-2019):** Must show 0 new skills.
  - **Pascal Siakam (2016-2019):** Must show > 2 new skills.
- **Pass Condition:** If logic fails these two, do not proceed.

**Step 2: Calculate Neuroplasticity Score ($N_c$)**
- **Cohort:** Rookies from 2015-16 to 2018-19.
- **Metrics:**
  - **Method Expansion:** `Unique_Viable_Methods_Year3 - Unique_Viable_Methods_Year1`
  - **Efficiency Velocity:** Slope of efficiency for primary method.
- **Weighted Scoring:**
  - Adding "Self-Created 3s" = 3 points.
  - Adding "Rim Finishing" = 2 points.
  - Adding "Spot-up Shooting" = 1 point.

**Step 3: Define Target Variable ("Prime Value")**
- We cannot rely solely on playoff data due to survivorship bias (good players on bad teams).
- **Target:** `Prime_Value_Score` = Regular Season VORP (Years 4-8) + Playoff Resilience Bonus.

**Step 4: Validation**
- **Output:** Scatter plot of $N_c$ vs. Prime Value.
- **Hypothesis Check:** Does $N_c$ have a higher correlation coefficient ($R^2$) than Draft Age?

---

## Unified Resilience Framework: Integrating All Metrics

### Core Concept: Multiple Pathways to Resilience

Resilience is not one-dimensional. Players can achieve playoff success through different pathways:

1. **Pathway 1: Versatility Resilience** (high diversity across many methods)
2. **Pathway 2: Primary Method Mastery** (elite specialization in one method)
3. **Pathway 3: Shot-Making Dominance** (maintains elite efficiency on high-difficulty shots)
4. **Pathway 4: Scalability Resilience** (efficient at high usage, role adaptable)
5. **Pathway 5: Evolution Resilience** (adds skills, improves over time)

### Unified Score Calculation

**Step 1: Measure Each Pathway**
- Versatility: `Method Resilience Score`
- Primary Method Mastery: `Primary_Method_Mastery_Score × Playoff Efficiency Retention`
- Shot-Making Dominance: `Dominance Score (SQAV)`
- Scalability: `Role Scalability × Usage-Adjusted Performance`
- Evolution: `Adaptability Score × Current Skill Portfolio Quality`

**Step 2: Determine Pathway Relevance**
- Not all pathways matter equally for all players
- Identify primary pathway: which pathway best describes the player?
- Calculate pathway-specific resilience: score for primary pathway
- Calculate pathway diversity: does the player excel in multiple pathways?

**Step 3: Calculate Unified Resilience Score**
- Primary pathway score: resilience in dominant pathway
- Pathway diversity bonus: bonus for excelling in multiple pathways
- Final score: `Primary pathway × (1 + Pathway_Diversity_Bonus)`

---

## Next Steps for Developers

**IMMEDIATE PRIORITY: Implement the Neuroplasticity Experiment**

1.  **Read the "Post-Mortem" Section Above:** Understand why previous attempts failed (Simmons False Positive).
2.  **Write `calculate_neuroplasticity.py`:**
    - Implement `get_zone_from_xy(x, y)` helper.
    - Implement `check_skill_viability(volume, efficiency)` helper.
    - Run the Simmons/Siakam unit test.
3.  **Run the Regression:** Compare $N_c$ vs. Draft Age predicting Prime Value.
4.  **Visualize:** Generate the "Top Learners" list and Scatter Plot.
