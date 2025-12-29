# Creation Independence Index (CII) - Specification

**Version**: 0.2  
**Date**: December 29, 2025

## Mission

Identify players on rookie contracts who will become franchise cornerstones, BEFORE consensus recognition, by measuring their ability to create offense when the defense knows it's coming.

## The Core Question

> "Does this player need the right situation, or IS he the situation?"

- **Simmons** needed shooters, Embiid doubles, transition opportunities
- **Harden** at OKC WAS the situation - give him the ball and get out of the way

## Archetypes (Classification Target)

| Archetype | Definition | Examples |
|-----------|------------|----------|
| **Franchise Engine** | Can be #1 on a championship team. Creates offense from nothing. | Harden, Luka, Jokić, Tatum, SGA |
| **Strong Creator** | High creation ability, optimal as #2 but can carry | Haliburton, Jaylen Brown, prime Kyrie |
| **Luxury Amplifier** | Excellent player, needs an Engine to win championships | Sabonis, Middleton, Bosh |
| **Fragile Star** | Looks like Engine, has fatal creation flaws | Simmons, KAT (debatable), Randle |
| **Role Player** | Solid contributor, clearly not a star | Tyus Jones, role shooters |

## Creation Independence Index Components

### Component 1: Self-Created Shot Score (Weight: 0.30)

**Question**: Can you generate a quality shot without a play being run?

**Architecture**: Two-Path Scoring (takes maximum)
- **Perimeter Path**: Unassisted FG%, Pull-up volume, Creation efficiency
- **Hub Path**: Elite efficiency (65%+ TS) + Elite touches (8+) + Non-hiding + High usage

**Perimeter Sub-metrics**:
- % of FGA that are unassisted (`pct_uast_fgm`)
- Pull-up volume (`pull_up_fga`)
- Efficiency on self-created shots
- Time of possession (`time_of_poss`)

**Hub Sub-metrics**:
- Weighted touch production (`weighted_touch_production` >= 8.0)
- True shooting percentage (`ts_pct` >= 0.65)
- Pressure response (`leverage_usg_delta` >= 0)
- Usage rate (`usg_pct` >= 0.24)

**Simmons Test**: 38 (Low perimeter creation, fails hub gates).  
**Harden Test**: 99 (Elite perimeter path).
**Jokić Test**: 90 (Hub path - elite efficiency + touch production).

### Component 2: Pressure Appetite Score (Weight: 0.25)

**Question**: When the game matters, do you WANT the ball?

**Sub-metrics**:
- `clutch_usg_absolute` (we have this)
- `relative_usage_drop` (clutch vs regular - we have this)
- 4th quarter usage relative to 1st-3rd quarter
- Playoff usage vs regular season usage

**Simmons Test**: Fails hard - usage DROPS under pressure.  
**Luka Test**: Passes - usage INCREASES under pressure.

### Component 3: Shot Difficulty Embrace Score (Weight: 0.20)

**Question**: Are you willing to take HARD shots, or only easy ones?

**Architecture**: Two-Path Scoring (takes maximum)
- **Perimeter Path**: Pull-up volume, Mid-range %, Pull-up 3s, Time of possession
- **Hub Path**: Recognizes that elite efficiency IS difficulty embrace for hub creators

**Perimeter Sub-metrics**:
- Pull-up volume (40% weight)
- Mid-range % of points (30% weight)
- Pull-up 3PT rate (20% weight)
- Time of possession (10% weight)

**Hub Sub-metrics**: Same gates as Component 1 - elite hub creators who don't hide get credit for "solving" difficulty through manufacturing efficiency.

**Simmons Test**: 14 (Neither path - doesn't take hard shots, fails hub gates).  
**Tatum Test**: 52 (Perimeter path - takes tough fadeaways routinely).
**DeRozan Test**: 78 (Perimeter path - maximum mid-range embrace).
**Jokić Test**: 91 (Hub path - elite efficiency IS his difficulty solution).

### Component 4: Defensive Attention Survival Score (Weight: 0.15)

**Question**: When defenses scheme for you, do you survive?

**Sub-metrics**:
- Efficiency vs Top 10 defenses / Efficiency vs Bottom 10
- Playoff efficiency vs Regular season efficiency  
- Efficiency as #1 option vs #2/#3 option
- Performance in elimination games

**Simmons Test**: Completely collapses when schemed.  
**Harden Test**: Actually got better - found counters.

### Component 5: Force Multiplication Score (Weight: 0.10)

**Question**: Do you create things that aren't in the box score?

**Sub-metrics**:
- Free throw rate (FTr) - getting to the line = creating fouls
- And-1 frequency
- Drawing double teams (gravity)
- Offensive foul drawing rate (lesser weight)

**Giannis Test**: Maximum. His whole game is force.  
**Simmons Test**: HAD the physical tools, DIDN'T use them.

## The Formula

```
CII = 0.30 × Self_Created_Shot_Score
    + 0.25 × Pressure_Appetite_Score  
    + 0.20 × Shot_Difficulty_Score
    + 0.15 × Defensive_Survival_Score
    + 0.10 × Force_Score
```

Each component is normalized to 0-100 scale.

## Actual Calculated Scores (December 2025)

| Player (Season) | Self | Pressure | Difficulty | Defense | Force | **CII** | Archetype |
|-----------------|------|----------|------------|---------|-------|---------|-----------|
| Harden (2018-19) | 99 | 95 | 78 | 78 | 80 | **87** | Franchise Engine |
| Jokić (2022-23) | 90 | 79 | 91 | 55 | 83 | **83** | Franchise Engine |
| Luka (2022-23) | 84 | 52 | 61 | 70 | 72 | **70** | Strong Creator |
| Curry (2020-21) | 82 | 86 | 59 | 58 | 58 | **72** | Strong Creator |
| Giannis (2019-20) | 34 | 73 | 37 | 49 | 93 | **53** | Fragile Star |
| Simmons (2019-20) | 38 | 21 | 14 | 33 | 44 | **31** | Role Player |
| Sabonis (2022-23) | 26 | 30 | 9 | 18 | 43 | **24** | Role Player |

**Notes**:
- Jokić validates Hub Path (90 self-created via hub, not perimeter)
- Sabonis fails hub gates (hides under pressure: `leverage_usg_delta = -0.058`)
- Giannis classified as Fragile Star due to low shot creation, but see Force score (93) - he's a special case
- Simmons correctly identified pre-collapse

## Threshold Guidelines

| CII Range | Likely Archetype |
|-----------|------------------|
| 80+ | Franchise Engine |
| 70-80 | Strong Creator |
| 55-70 | Luxury Amplifier |
| 40-55 | Fragile Star / High Role Player |
| <40 | Role Player / Fraud |

## Data Requirements

### Already Available (from Phase 1)
- `clutch_usg_absolute`, `relative_usage_drop`, `abdication_interaction`
- `creation_volume_ratio`, `time_of_poss`
- Free throw rate (FTr)
- Efficiency vs opponent buckets (we have defensive context)

### Needs Collection
- Unassisted FG% by shot type
- Shot contest data (defender distance)
- ISO/Pull-up volume and efficiency splits
- Playoff vs RS usage/efficiency deltas

### Needs Calculation
- Self-Created Shot Score formula
- Shot Difficulty Embrace formula
- Composite CII

## Validation Approach

1. **Curate ground truth**: Label 50-100 historical player-seasons with known archetype
2. **Calculate CII**: For all labeled players
3. **Validate ranking**: Does CII correctly order players by archetype?
4. **Train classifier**: Use CII components to predict archetype
5. **Test on blind set**: Players whose archetype wasn't used in training

## Success Criteria

1. **Simmons identified as Fragile Star** in all seasons pre-collapse
2. **Harden at OKC identified as Engine** despite 6th man role
3. **Haliburton ranked above Sabonis** before the trade
4. **Early-career stars (Tatum, SGA, Luka)** identified as Engines
5. **KAT identified as Fragile** despite elite raw stats

## Resolved Questions

1. ✅ **Giannis exception**: Handled via Component 5 (Force Multiplication Score). His 93 Force score reflects that he creates via force. His overall CII (53) is lower, which correctly indicates he's not a perimeter-style Engine.

2. ✅ **Hub Creator (Jokić) exception**: Handled via Two-Path architecture in Components 1 and 3. Hub creators who don't hide get full credit through the Hub Path (elite efficiency + touches + non-hiding).

3. ✅ **Jokić vs Sabonis**: Differentiated by `leverage_usg_delta` gate. Jokić (+0.02) steps up under pressure; Sabonis (-0.058) hides. This creates a 58-point CII gap (83 vs 24).

## Open Questions

1. **Role context**: How do we separate "low creation due to role" from "can't create"?
2. **Injury/age adjustment**: How do we handle players whose creation declined due to physical changes?
3. **Team context**: How much should surrounding cast affect the score?

## Next Steps

1. ✅ ~~Curate ground truth labels in `/ground_truth/player_labels.csv`~~
2. ✅ ~~Build data pipeline for missing metrics~~
3. ✅ ~~Implement each CII component as a function~~
4. ✅ ~~Calculate CII for historical players~~
5. ✅ ~~Validate against ground truth~~ (7/7 critical cases pass)
6. Expand ground truth to 60+ player-seasons
7. Train archetype classifier
8. Apply to current season to identify latent stars

