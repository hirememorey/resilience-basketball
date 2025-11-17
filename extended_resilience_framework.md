# Extended Playoff Resilience Framework

## Current State: Where We Are Now

### Project Overview
This project analyzes NBA player performance to identify factors that predict playoff resilience—the ability to maintain or exceed regular-season production in the postseason. We have a complete data pipeline with comprehensive player statistics, shot location data, play-by-play data, and both regular-season and playoff metrics for the 2024-25 NBA season.

### Existing Framework (Implemented)
We currently have a **Two-Pillar Resilience Framework** that measures:

1. **Performance Resilience (The "What")**: Change in core efficiency metrics (TS%, PPP, TOV%) from regular season to playoffs
2. **Method Resilience (The "How")**: Stability of offensive versatility across three sub-pillars:
   - **Spatial Diversity**: Efficiency and volume from different court zones
   - **Play-Type Diversity**: Efficiency and usage across offensive sets (Isolation, P&R, Transition, etc.)
   - **Creation Diversity**: Ability to score through different methods (Catch & Shoot, Pull-ups, Drives)

The Method Resilience score uses a **Herfindahl-Hirschman Index (HHI)** approach, weighted by efficiency relative to league average, converted to a diversity score (0-100 scale).

### The Gap: What's Missing
While the current framework effectively measures **versatility-based resilience**, it doesn't capture other pathways to playoff success:

- **Dominance-based resilience**: Players like Shaq who excel in one method so much that schemes don't matter
- **Role scalability**: Players like Jimmy Butler who maintain efficiency when usage increases
- **Pressure resistance**: Players who maintain efficiency under tight defense
- **Skill evolution**: Players like Giannis who add new skills over time

This document outlines the extended framework to capture these additional dimensions.

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

**Edge Cases**
- Players with multiple co-primary methods: average dominance across top 2-3 methods
- Low-volume specialists: require minimum volume threshold (e.g., 20% of total attempts)
- Method-specific adjustments: post-ups vs. corner 3s have different efficiency baselines

**Integration with Existing Framework**
- Current: Diversity Score measures spread across methods
- New: Dominance Score measures peak capability in best method
- Combined resilience: `High Diversity OR High Dominance → resilient`
- Formula: `Resilience = max(Diversity_Score, Dominance_Score) × 0.6 + min(Diversity_Score, Dominance_Score) × 0.4`

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

**Mathematical Formulation**
- `Scalability_Score = (Slope_Score × 0.5) + (Usage_Adjusted_Performance × 0.5)`
- `Slope_Score = normalize(β × 100)` where β is efficiency slope
- `Usage_Adjusted_Performance = (Actual_Playoff_Efficiency / Expected_Efficiency) × 100`

**Edge Cases**
- Players with consistent usage: measure efficiency variance, not scalability
- Small sample sizes: require minimum games per usage tier
- Role changes: account for position/role shifts, not just usage changes

**Integration with Existing Framework**
- Current: Performance Resilience measures overall efficiency change
- New: Role Scalability explains why efficiency changes (usage increase)
- Combined: `Performance Resilience × Role Scalability → adjusted resilience score`
- Formula: `Adjusted_Resilience = Performance_Resilience × (1 + Scalability_Bonus)`

---

### 3. Dominance Score (Shot Quality-Adjusted Value): Efficiency Under Duress

#### Core Question
Does the player have the ability to create and convert high-difficulty scoring opportunities against dedicated defensive pressure, independent of scheme?

This moves beyond simple efficiency to measure a player's true shot-making talent by accounting for the quality of every single shot attempt. It directly addresses the problem that raw percentages don't distinguish between a player hitting wide-open shots created by others and a player creating and hitting tough shots themselves.

#### Calculation Approach: Shot Quality-Adjusted Value (SQAV)

The Dominance Score is calculated using a Shot Quality-Adjusted Value (SQAV) model, which evaluates every shot against a league-average baseline for that exact shot context.

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
- A "Difficulty Multiplier" can also be applied to give more weight to shots taken under higher pressure (e.g., "Very Tight" defense, "Extensive Creation").

**Step 4: Aggregate to a Single Dominance Score**
- The final Dominance Score is the sum of the `Context_Value` generated across all shot contexts, representing the total shot-making value a player provides above an average player.
- `Dominance Score = SUM(all_contexts(Context_Value))`
- This score is then normalized (e.g., to a 0-100 scale or as a percentile rank) for comparison.

**Mathematical Formulation**
- `xeFG_c = League_Average_eFG%_in_Context_c`
- `eFG_vs_x_c = Player_eFG_c - xeFG_c`
- `Dominance_Score = Σ_c (eFG_vs_x_c * Attempts_c * Difficulty_Multiplier_c)`

**Integration with Existing Framework**
- This new Dominance Score replaces the previous "Defensive Pressure Resistance" metric with a more sophisticated and granular approach.
- It provides a powerful lens into *why* a player's Method Resilience might be robust; a high Dominance Score suggests their methods are effective even when contested.
- **Combined:** `True_Versatility = Method_Resilience_Score × (1 + (Normalized_Dominance_Score / 100) * Weight)`

---

### 4. Longitudinal Adaptability: Skill Evolution Over Time

#### Core Question
Does the player add new skills over time, and do those skills improve in efficiency?

#### Calculation Approach

**Step 1: Track Method Portfolio Over Time**
- For each season, calculate diversity scores (spatial, play-type, creation)
- Track which methods are "active" (above minimum volume threshold)
- Identify new methods added each season
- Identify methods removed or reduced

**Step 2: Measure Skill Acquisition Rate**
- New methods per season: count of methods added
- Method expansion rate: `(Current_Methods / Previous_Methods) - 1`
- Cumulative skill portfolio: total unique methods used across career
- Final metric: average new methods per season over career

**Step 3: Measure Skill Improvement Rate**
- For each method, track efficiency over time
- Calculate efficiency slope: does efficiency improve, stay flat, or decline?
- Identify methods with improving efficiency (skill development)
- Identify methods with declining efficiency (skill decay or role change)

**Step 4: Calculate Adaptability Score**
- Skill acquisition component: new methods per season (normalized to 0-100)
- Skill improvement component: average efficiency slope across all methods (normalized to 0-100)
- Consistency component: variance in year-over-year changes (lower variance = more consistent)
- Final score: weighted average of acquisition (40%), improvement (40%), consistency (20%)

**Mathematical Formulation**
- `Acquisition_Rate = (New_Methods_This_Season / Career_Avg_Methods) × 100`
- `Improvement_Rate = average(efficiency_slope for each method) × 100`
- `Consistency_Score = 100 - (variance(year_over_year_changes) × scaling_factor)`
- `Adaptability_Score = (Acquisition × 0.4) + (Improvement × 0.4) + (Consistency × 0.2)`

**Edge Cases**
- Young players: require minimum seasons (e.g., 3+) for meaningful trends
- Role changes: distinguish skill acquisition from role-driven method changes
- Injury impacts: account for seasons with reduced games/minutes
- Career stage: different expectations for early career vs. prime vs. decline

**Integration with Existing Framework**
- Current: Method Resilience measures current-season diversity
- New: Adaptability measures trajectory of diversity over time
- Combined: `Current diversity × Adaptability trajectory → predictive resilience`
- Formula: `Predictive_Resilience = Current_Method_Resilience × (1 + Adaptability_Trend)`

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

**Mathematical Formulation**
- `Pathway_Scores = {Versatility, Dominance, Scalability, Evolution}`
- `Primary_Pathway = argmax(Pathway_Scores)`
- `Pathway_Diversity = count(pathways where score > threshold) / 5`
- `Unified_Resilience = Primary_Pathway_Score × (1 + Pathway_Diversity × 0.2)`

---

## Validation and Calibration

### Historical Validation
Test metrics on known cases:
- **Shaq**: Should score high on Primary Method Mastery, low on Versatility
- **Butler**: Should score high on Scalability, moderate on Versatility
- **Harden**: Should score high on Versatility, and now we can precisely measure his Shot-Making Dominance on tough shots.
- **Giannis**: Should score high on Adaptability, improving over time

If metrics don't align with known cases, adjust calculations.

### Predictive Validation
- Use regular-season metrics to predict playoff performance
- Compare predicted vs. actual playoff efficiency changes
- Measure correlation: do high resilience scores predict playoff success?
- Identify false positives/negatives: who scores high but underperforms, or vice versa?

### Sensitivity Analysis
- Test metric robustness: do small data changes cause large score changes?
- Test weight sensitivity: how do different weightings affect rankings?
- Test threshold sensitivity: how do minimum volume thresholds affect scores?

### Calibration
- Normalize scores to 0-100 scale for interpretability
- Set meaningful thresholds: what score indicates "resilient"?
- Create percentile rankings: where does each player rank?
- Establish confidence intervals: account for sample size and uncertainty

---

## Key Design Decisions

### Decision 1: Absolute vs. Relative Metrics
- **Absolute**: Compare to historical benchmarks (all-time greats)
- **Relative**: Compare to current league average
- **Recommendation**: Use both — absolute for dominance, relative for diversity

### Decision 2: Volume vs. Efficiency Weighting
- **Current approach**: Weight by efficiency relative to league average
- **Alternative**: Weight by absolute volume
- **Recommendation**: Efficiency-weighted volume (current approach) is correct — a high-volume, inefficient method shouldn't count as much

### Decision 3: Playoff Sample Size
- **Problem**: Playoff sample sizes are small (4-28 games vs. 82 regular season)
- **Solution**: Use Bayesian approach — regular-season prior + playoff likelihood → posterior estimate
- **Alternative**: Require minimum playoff games for reliability

### Decision 4: Context Adjustment
- **Problem**: Not all playoff runs are equal (opponent quality, injuries, team context)
- **Solution**: Adjust for opponent defensive rating, teammate quality, injury status
- **Challenge**: Requires additional data and assumptions

### Decision 5: Temporal Scope
- **Single-season**: Current season only
- **Multi-season**: Career trajectory
- **Recommendation**: Both — current resilience (single-season) and predictive resilience (multi-season)

---

## Implementation Considerations

### Data Requirements
- **Shot location data**: For spatial diversity and pressure resistance
- **Play-by-play data**: For usage rate segmentation and pressure scenarios
- **Multi-season data**: For adaptability and longitudinal analysis
- **Historical benchmarks**: For dominance score calibration

### Computational Complexity
- **Dominance Score**: O(n) where n = number of methods
- **Role Scalability**: O(m) where m = number of games (requires game-level data)
- **Pressure Resistance**: O(p) where p = number of shots (requires shot-level data)
- **Adaptability**: O(s × m) where s = seasons, m = methods per season

### Statistical Considerations
- **Sample size requirements**: Minimum attempts/games for reliability
- **Confidence intervals**: Account for uncertainty in small samples
- **Multiple comparisons**: Adjust p-values when testing multiple hypotheses
- **Causality vs. correlation**: Metrics measure association, not causation

---

## Implementation Roadmap

### Phase 1: Dominance Score (Highest Priority)
**Why**: Addresses the Shaq problem — captures elite specialization
**Requirements**:
- Primary method identification logic
- Historical benchmark database (or percentile calculations)
- Playoff efficiency comparison
**Dependencies**: Existing shot location and playtype data

### Phase 2: Role Scalability (High Priority)
**Why**: Addresses the Butler problem — captures usage efficiency
**Requirements**:
- Game-level usage rate data
- Efficiency-by-usage-tier calculations
- Regression analysis for efficiency slopes
**Dependencies**: Play-by-play data or game-level statistics

### Phase 3: Dominance Score (Medium Priority)
**Why**: Addresses the Harden problem — captures efficiency under contest via SQAV
**Requirements**:
- Shot dashboard data (already collected)
- League-average calculations for all shot contexts
- Efficiency vs. expected eFG% calculations
**Dependencies**: Shot dashboard data (already available)

### Phase 4: Longitudinal Adaptability (Lower Priority)
**Why**: Addresses the Giannis problem — captures skill evolution
**Requirements**:
- Multi-season data collection
- Method portfolio tracking over time
- Efficiency trend analysis
**Dependencies**: Historical season data (not yet collected)

### Phase 5: Unified Framework Integration
**Why**: Combines all pathways into actionable resilience score
**Requirements**:
- Pathway identification logic
- Unified score calculation
- Validation against historical cases
**Dependencies**: All previous phases

---

## Current Implementation Status

### ✅ Completed
- **Phase 1A MVP: Core Resilience Calculator** (`phase1a_resilience_calculator.py`)
  - Performance Resilience: TS% delta from regular season to playoffs
  - Spatial Diversity: Court zone versatility using shot location data
  - Play-type Diversity: Offensive set effectiveness using synergy stats
  - Tested on 175 qualified players (4+ playoff games) with 91.6% data quality
  - **Key Results:**
    - 31.2% of players highly resilient (score >75)
    - 2.3% low resilience (score <25)
    - Play-type diversity correlates with playoff performance (-0.131)
    - Framework successfully distinguishes resilient vs vulnerable players

- Two-pillar framework (Performance + Method Resilience)
- Method Resilience calculation (spatial, play-type diversity)
- League average benchmarks for efficiency weighting
- Data validation and quality assurance systems

### 🚧 In Progress
- **Phase 1B: Longitudinal Analysis** - Multi-season resilience trajectories
  - Testing hypothesis: Player development correlates with resilience improvement
  - Test cases: Ben Simmons (2017-2021), Joel Embiid (2017-2024), Giannis Antetokounmpo (2017-2021), James Harden (2016-2025)
  - Goal: Validate that skill expansion leads to playoff adaptability

### 📋 To Do
1. **Collect multi-season data** for longitudinal player analysis
2. **Extend calculator** for year-over-year resilience tracking
3. **Implement Primary Method Mastery** calculation (elite specialization)
4. **Implement Role Scalability** (efficiency at different usage rates)
5. **Implement Dominance Score (SQAV)** - shot quality-adjusted value
6. **Build Unified Resilience Score** combining all pathways
7. **Validate against historical cases** and predictive accuracy
8. **Address context blindness** - adjust for teammate quality, opponent strength, role changes
9. **Incorporate facilitation metrics** - celebrate passers who create open shots for teammates

---

## Key Files Reference

- **Current Implementation**: `src/nba_data/scripts/calculate_resilience_scores.py`
- **Database Schema**: `src/nba_data/db/schema.py`
- **League Averages**: `src/nba_data/scripts/calculate_league_averages.py`
- **Shot Dashboard Data**: `src/nba_data/scripts/populate_shot_dashboard_data.py`
- **Foundational Principles**: `foundational_principles.md`

---

## Questions for Future Development

1. **How do we weight the pathways?** Should all pathways be equal, or should some be weighted more heavily?
2. **What's the minimum sample size?** How many playoff games/attempts are needed for reliable metrics?
3. **How do we handle role changes?** Should we adjust for position/role shifts, or treat them as part of adaptability?
4. **What about team context?** Should we adjust for teammate quality, coaching, or opponent strength?
5. **How do we validate?** What's the gold standard for "resilient" players, and how do we measure if we're right?

---

## Next Steps for Developers

**IMMEDIATE PRIORITY: Phase 1B - Longitudinal Analysis**

1. **Read this document** to understand the extended framework and current progress
2. **Review Phase 1A implementation** in `phase1a_resilience_calculator.py` to understand the working MVP
3. **Focus on longitudinal testing** - implement multi-season data collection and analysis for:
   - Ben Simmons (2017-2021): Test stagnation hypothesis
   - Joel Embiid (2017-2024): Test development hypothesis
   - Giannis Antetokounmpo (2017-2021): Test transformation hypothesis
   - James Harden (2016-2025): Test elite versatility ceiling
4. **Extend calculator** to track resilience trajectories over player careers
5. **Validate hypothesis**: Players who expand their games should show improving resilience
6. **Address critical framework gaps** identified in Phase 1A:
   - **Context blindness**: Adjust for teammate quality, opponent strength, role changes
   - **Performance oversimplification**: Include facilitation metrics (assist quality, open shot creation)
   - **Celebrate facilitators**: Players who create easy shots for teammates should score higher than those who just take them

---

*Last Updated: [Current Date]*
*Framework Version: 2.0 (Extended)*
