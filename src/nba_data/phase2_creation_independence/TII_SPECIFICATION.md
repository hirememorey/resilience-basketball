# Trajectory Independence Index (TII) Specification

**Version**: 1.0  
**Date**: December 29, 2025  
**Status**: Design Complete, Implementation Pending

---

## 1. Purpose

The TII answers a fundamentally different question than the CII:

| Index | Question | Example |
|-------|----------|---------|
| **CII** | "Can this player create when schemed RIGHT NOW?" | Harden 2018-19: Yes (high volume, high efficiency) |
| **TII** | "If we gave this player 30% usage, would they maintain efficiency?" | Brunson 2020-21: Yes (low volume, but signals present) |

**The TII identifies Latent Engines** - players whose creation skills are present but underutilized due to role/opportunity constraints.

---

## 2. The Latent Engine Archetype

### Definition
A **Latent Engine** is a player who:
1. Has creation skills but limited opportunity (medium CII)
2. Would scale to Engine-level production if given the chance (high TII)
3. Is likely undervalued because surface stats don't reveal the upside

### Historical Examples

| Player | Latent Season | Signal | Breakout |
|--------|--------------|--------|----------|
| Jalen Brunson | 2020-21 (Mavs backup) | CVR 0.69, TS 0.618, positive leverage | 2022-23 Knicks: Engine |
| James Harden | 2011-12 (OKC 6th man) | Elite ISO EFG, stepped up in playoffs | 2012-13 Rockets: Engine |
| SGA | 2019-20 (with CP3) | Creation tools present, limited touches | 2020-21: Engine |
| Tyrese Maxey | 2022-23 (with Harden) | Pull-up development, pressure appetite | 2024-25: Engine |

### Anti-Examples (False Latent Engines)

| Player | Looked Like | Reality |
|--------|-------------|---------|
| Julius Randle 2020-21 | High stats, All-NBA | Playoffs: 18 PPG on 30% FG. ISO EFG collapsed. |
| Andrew Wiggins 2016-17 | 24 PPG at 21 | No creation tools, low ISO efficiency |
| Mikal Bridges 2022-23 | High usage on Brooklyn | System merchant, efficiency collapsed |

---

## 3. TII Components

### Formula

```
TII = 0.30 × Scaling_Efficiency_Score
    + 0.25 × Pressure_Appetite_Score  
    + 0.20 × Creation_Tool_Depth_Score
    + 0.15 × Opportunity_Response_Score
    + 0.10 × Age_Trajectory_Score
```

Each component normalized to 0-100 scale.

---

### 3.1 Scaling Efficiency Score (30%)

**Question**: Does this player create efficiently WHEN THEY CREATE, regardless of volume?

**Key Insight**: A player taking 2 ISO shots per game with 60% EFG has more latent ability than one taking 8 ISO shots with 40% EFG.

**Formula**:
```
scaling_efficiency = (
    0.40 × efficiency_at_creation_score +
    0.30 × creation_rate_vs_usage_score +
    0.30 × subsidy_inverse_score
)
```

**Sub-Components**:

| Sub-Metric | Weight | Calculation | Rationale |
|------------|--------|-------------|-----------|
| Efficiency at Creation | 40% | TS% weighted by creation_volume_ratio | High TS + High CVR = skill, not system |
| Creation Rate vs Usage | 30% | creation_volume_ratio / usg_pct | High creation rate at low usage = latent ability |
| Subsidy Inverse | 30% | 1 - subsidy_index | Low subsidy = portable efficiency |

**Thresholds**:
- TS% ≥ 0.58 at CVR ≥ 0.60 = Elite (score 80+)
- TS% ≥ 0.55 at CVR ≥ 0.50 = Good (score 60-80)
- TS% < 0.55 or CVR < 0.40 = Limited (score < 50)

**Validation**:
- Brunson 2020-21: TS 0.618, CVR 0.69, USG 0.196 → Should score ~85
- Randle 2020-21: TS 0.536, CVR 0.67, USG 0.283 → Should score ~50 (efficiency collapsed at volume)

---

### 3.2 Pressure Appetite Score (25%)

**Question**: Does this player SEEK high-leverage possessions, even at low overall usage?

**Key Insight**: A backup who takes clutch shots when given the chance is different from one who hides. Latent Engines have positive pressure response even when overall opportunity is limited.

**Formula**:
```
pressure_appetite = (
    0.50 × leverage_usg_delta_score +
    0.30 × clutch_usg_relative_score +
    0.20 × pressure_consistency_score
)
```

**Sub-Components**:

| Sub-Metric | Weight | Calculation | Rationale |
|------------|--------|-------------|-----------|
| Leverage USG Delta | 50% | leverage_usg_delta normalized | Positive = stepping up |
| Clutch USG Relative | 30% | clutch_usg_absolute / usg_pct | High ratio = seeks pressure |
| Pressure Consistency | 20% | leverage_ts_delta stability | Maintains efficiency under pressure |

**Critical Gate**: 
- If leverage_usg_delta < -0.03, max score is 40 (hiding pattern detected)

**Thresholds**:
- leverage_usg_delta ≥ +0.05 = Elite (score 80+)
- leverage_usg_delta ≥ 0.00 = Good (score 60-80)
- leverage_usg_delta < -0.03 = Hiding (score capped at 40)

**Validation**:
- Brunson 2020-21: leverage_usg_delta +0.029 → Should score ~75
- Simmons 2019-20: leverage_usg_delta -0.085 → Should score ~20

---

### 3.3 Creation Tool Depth Score (20%)

**Question**: Does this player have the TOOLS for high-volume creation, even if currently underused?

**Key Insight**: Creation tools (pull-up shooting, mid-range, time of possession) predict scaling ability. A player with tools but low usage has latent capacity.

**Formula**:
```
creation_tools = (
    0.35 × pull_up_rate_score +
    0.25 × mid_range_score +
    0.25 × time_of_poss_score +
    0.15 × tool_efficiency_score
)
```

**Sub-Components**:

| Sub-Metric | Weight | Calculation | Rationale |
|------------|--------|-------------|-----------|
| Pull-Up Rate | 35% | pull_up_fga / (usg_pct × games) | High rate at low usage = tools present |
| Mid-Range Game | 25% | pct_pts_2pt_mr | Mid-range = schematic-proof shot |
| Time of Possession | 25% | time_of_poss normalized | Ball handling ability |
| Tool Efficiency | 15% | pull_up_fg3m / pull_up_fg3a | Can they hit the shots? |

**Usage-Adjusted Normalization**:
- For low-usage players (<22% USG), we look at RATE not VOLUME
- pull_up_fga of 3.0 at 20% usage = same rate as 4.5 at 30% usage

**Validation**:
- Brunson 2020-21: pull_up_fga 3.1 at USG 0.196, time_of_poss present → Should score ~70
- Gobert any year: No pull-ups, no mid-range → Should score ~10

---

### 3.4 Opportunity Response Score (15%)

**Question**: When given MORE opportunity (playoffs, star injured), does this player step up?

**Key Insight**: Natural experiments (playoff usage bump, starter injured) reveal scaling ability.

**Formula**:
```
opportunity_response = (
    0.50 × usage_trajectory_score +
    0.30 × efficiency_at_higher_usage_score +
    0.20 × minutes_efficiency_ratio_score
)
```

**Sub-Components**:

| Sub-Metric | Weight | Calculation | Rationale |
|------------|--------|-------------|-----------|
| Usage Trajectory | 50% | YoY usage growth | Earning more touches = scaling |
| Efficiency at Higher Usage | 30% | TS stability as usage increased | Maintains efficiency = skill |
| Minutes-Efficiency Ratio | 20% | efficiency × minutes correlation | More minutes, same efficiency = depth |

**Data Limitation**: 
- We don't have game-by-game data for "when star sat"
- Proxy: YoY usage growth with efficiency maintenance

**Validation**:
- Brunson 2020-21→2021-22: USG 0.196→0.215, TS maintained → Should score ~70
- One-year wonders: USG up, TS down → Should score ~30

---

### 3.5 Age Trajectory Score (10%)

**Question**: Given this player's age, how much runway do they have for development?

**Key Insight**: A 22-year-old with latent signals has more value than a 30-year-old with the same signals.

**Formula**:
```
age_trajectory = age_ceiling_score × trajectory_bonus
```

**Age Ceiling Score**:
| Age | Score | Rationale |
|-----|-------|-----------|
| ≤22 | 100 | Maximum development runway |
| 23-25 | 85 | Prime development years |
| 26-28 | 65 | Established but can still grow |
| 29-31 | 40 | Limited upside |
| ≥32 | 20 | What you see is what you get |

**Trajectory Bonus** (multiplier 0.8-1.2):
- Positive skill trajectory (tools improving) = 1.2
- Stable trajectory = 1.0
- Declining trajectory = 0.8

**Validation**:
- Brunson 2020-21 (age 24): Should score ~85 × 1.1 = 94
- 30-year-old backup: Should score ~40 × 1.0 = 40

---

## 4. TII Thresholds and Classification

### TII Score Interpretation

| TII Range | Label | Interpretation |
|-----------|-------|----------------|
| 80+ | Elite Scaling Potential | Would likely be Engine if given opportunity |
| 65-80 | High Scaling Potential | Strong candidate for increased role |
| 50-65 | Moderate Scaling Potential | Could scale but not guaranteed |
| 35-50 | Limited Scaling Potential | Probably ceiling-limited |
| <35 | Low Scaling Potential | Role player ceiling |

---

## 5. 2D Classification Matrix (CII × TII)

The combination of CII (current ability) and TII (scaling potential) creates a 2D classification:

```
                           TII (Scaling Potential)
                    Low (<50)    Med (50-70)    High (>70)
               ┌─────────────┬─────────────┬─────────────┐
    High (80+) │  Franchise  │  Franchise  │  Franchise  │
               │   Engine    │   Engine    │   Engine    │
CII            ├─────────────┼─────────────┼─────────────┤
(Current)      │   Luxury    │   Strong    │   LATENT    │
    Med (50-80)│  Amplifier  │  Creator    │   ENGINE    │ ← Alpha
               ├─────────────┼─────────────┼─────────────┤
               │    Role     │ Developing  │ Developing  │
    Low (<50)  │   Player    │  Prospect   │   Star      │
               └─────────────┴─────────────┴─────────────┘
```

### Archetype Definitions (2D)

| Archetype | CII | TII | Description |
|-----------|-----|-----|-------------|
| **Franchise Engine** | 80+ | Any | Already proven elite creator |
| **Latent Engine** | 50-80 | 70+ | Has skills, needs opportunity → **THE ALPHA** |
| **Strong Creator** | 50-80 | 50-70 | Good creator, unclear ceiling |
| **Luxury Amplifier** | 50-80 | <50 | Good but ceiling-limited |
| **Developing Star** | <50 | 70+ | Raw but high ceiling |
| **Developing Prospect** | <50 | 50-70 | Too early to classify |
| **Role Player** | <50 | <50 | Correctly priced |
| **Fragile Star** | Special | Special | High stats but fatal creation flaws |

### Fragile Star Detection (Special Case)

A **Fragile Star** is detected when:
- High raw stats (points, usage) but
- Low CII (<50) despite high opportunity
- Low creation tool depth
- Negative pressure response

Examples: Simmons, KAT, Randle in playoffs

---

## 6. Features Required

### Already Available (100% coverage in dataset)

| Feature | Used In | Role |
|---------|---------|------|
| ts_pct | Scaling Efficiency | Efficiency metric |
| creation_volume_ratio | Scaling Efficiency, Tools | Creation rate |
| usg_pct | Multiple | Baseline usage |
| leverage_usg_delta | Pressure Appetite | Pressure response |
| clutch_usg_absolute | Pressure Appetite | Clutch usage |
| leverage_ts_delta | Pressure Appetite | Pressure efficiency |
| relative_usage_drop | Pressure Appetite | Usage change |
| pull_up_fga | Creation Tools | Volume |
| pull_up_fg3a | Creation Tools | Range |
| pct_pts_2pt_mr | Creation Tools | Mid-range |
| time_of_poss | Creation Tools | Ball handling |
| subsidy_index | Scaling Efficiency | System dependence |
| age | Age Trajectory | Development runway |
| skill_index | Creation Tools | Skill composite |

### Derived Features (to calculate)

| Feature | Derivation |
|---------|------------|
| creation_rate_vs_usage | creation_volume_ratio / usg_pct |
| clutch_usg_relative | clutch_usg_absolute / usg_pct |
| pull_up_rate_per_usage | pull_up_fga / (usg_pct × 82) |
| yoy_usage_change | Current usg_pct - Previous usg_pct |

### Not Available (would enhance but not blocking)

| Feature | Would Improve |
|---------|---------------|
| Playoff-specific stats | Opportunity Response |
| Game-by-game data | "Star sat" analysis |
| ISO EFG specifically | Scaling Efficiency |

---

## 7. Validation Cases

### Must-Pass Cases (Latent Engine Detection)

| Player | Season | Expected TII | Rationale |
|--------|--------|--------------|-----------|
| Jalen Brunson | 2020-21 | 80+ | Low usage, elite efficiency, positive pressure |
| James Harden | 2011-12 | 85+ | OKC 6th man with elite creation |
| SGA | 2019-20 | 75+ | CP3 teammate, tools present |
| Tyrese Maxey | 2022-23 | 75+ | Harden teammate, development visible |

### Must-Fail Cases (False Latent Engine Rejection)

| Player | Season | Expected TII | Rationale |
|--------|--------|--------------|-----------|
| Ben Simmons | Any | <40 | No creation tools, negative pressure |
| Julius Randle | 2020-21 | <50 | High volume but ISO EFG poor |
| Domantas Sabonis | Any | <50 | Hiding under pressure |
| Andrew Wiggins | 2016-17 | <45 | Volume without efficient creation |

### Edge Cases

| Player | Season | Expected TII | Notes |
|--------|--------|--------------|-------|
| Khris Middleton | 2018-19 | ~55 | Good tools but age/ceiling limit |
| Pascal Siakam | 2019-20 | ~60 | Developed creation but plateaued |

---

## 8. Implementation Plan

### Phase 1: Core Calculator
1. Create `trajectory.py` with `calculate_tii()` function
2. Implement each sub-component
3. Add to composite index

### Phase 2: 2D Classification
1. Update `composite.py` to return both CII and TII
2. Implement 2D archetype classification
3. Update ground truth to 2D format

### Phase 3: Validation
1. Run on all ground truth cases
2. Verify Latent Engine detection accuracy
3. Tune thresholds based on results

---

## 9. Success Metrics

| Metric | Target |
|--------|--------|
| Latent Engine Precision | >80% of flagged Latent Engines become Engines within 3 years |
| Latent Engine Recall | >70% of future Engines flagged as Latent 2+ years before breakout |
| False Positive Rate | <20% of Latent Engine flags are false positives |
| Brunson Detection | Must flag Brunson 2020-21 as Latent Engine |
| Simmons Rejection | Must NOT flag any Simmons season as Latent Engine |

---

**Document Version**: 1.0  
**Last Updated**: December 29, 2025

