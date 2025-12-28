# Creation Independence Index (CII) - Specification

**Version**: 0.1  
**Date**: December 27, 2025

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

**Sub-metrics**:
- % of FGA that are unassisted
- ISO + Pull-up volume per 100 possessions
- Efficiency on self-created shots (vs assisted)
- Stepback/fadeaway availability (shot creation tools)

**Simmons Test**: Near zero. No self-created jumpers.  
**Harden Test**: Elite. Stepback 3 available anytime.

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

**Sub-metrics**:
- % of shots contested/tightly guarded
- Average defender distance on shots
- Mid-range volume (harder than layups or corner 3s)
- Pull-up 3PT rate (harder than catch-and-shoot)

**Simmons Test**: Only takes layups/dunks - never embraces difficulty.  
**Tatum Test**: Takes tough fadeaways routinely.

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

## Expected Scores

| Player | Self | Pressure | Difficulty | Defense | Force | **CII** | Archetype |
|--------|------|----------|------------|---------|-------|---------|-----------|
| Harden (OKC) | 95 | 85 | 90 | 85 | 90 | **89** | Engine |
| Luka | 95 | 95 | 90 | 80 | 80 | **90** | Engine |
| Tatum | 90 | 85 | 85 | 80 | 75 | **84** | Engine |
| SGA | 85 | 85 | 80 | 85 | 90 | **85** | Engine |
| Giannis | 50 | 95 | 60 | 80 | 100 | **73** | Engine (via force) |
| Haliburton | 75 | 80 | 70 | 80 | 65 | **75** | Strong Creator |
| Brown | 70 | 70 | 75 | 75 | 70 | **72** | Strong Creator |
| KAT | 65 | 45 | 55 | 45 | 55 | **54** | Fragile Star |
| Sabonis | 35 | 70 | 45 | 55 | 60 | **50** | Amplifier |
| Harris | 50 | 55 | 50 | 50 | 45 | **51** | Amplifier |
| Simmons | 5 | 20 | 10 | 25 | 35 | **17** | Fragile Star |

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

## Open Questions

1. **Giannis exception**: How do we handle Engines who create via force, not skill?
2. **Role context**: How do we separate "low creation due to role" from "can't create"?
3. **Injury/age adjustment**: How do we handle players whose creation declined due to physical changes?
4. **Team context**: How much should surrounding cast affect the score?

## Next Steps

1. Curate ground truth labels in `/ground_truth/player_labels.csv`
2. Build data pipeline for missing metrics
3. Implement each CII component as a function
4. Calculate CII for historical players
5. Validate against ground truth
6. Train archetype classifier

