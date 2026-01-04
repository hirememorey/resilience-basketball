# Current State Audit
Date: January 3, 2026

## Parameter Inventory

List every tunable parameter in the current implementation:

### Component 1: Self-Created Shot (Self-Created)
#### Perimeter Path
| Parameter | Current Value | Justification |
|-----------|---------------|---------------|
| unassisted_rate weight | 0.25 | "What % of made shots are unassisted?" |
| creation_volume weight | 0.30 | "How often does the player create?" |
| self_created_efficiency weight | 0.30 | "How efficient are self-created shots?" |
| creation_tools weight | 0.15 | "Does the player have stepback, fadeaway, etc.?" |

#### Hub Path
| Parameter | Current Value | Justification |
|-----------|---------------|---------------|
| touch_production_elite | 8.0 | Elite threshold for points from touches |
| ts_elite | 0.62 | Elite efficiency threshold (62% TS) |
| leverage_threshold | 0.0 | Must be non-negative (not hiding) |
| usage_threshold | 0.24 | Must have significant usage to qualify |

### Component 2: Pressure Appetite
| Parameter | Current Value | Justification |
|-----------|---------------|---------------|
| clutch_usage_absolute weight | 0.50 | "Actual usage in clutch moments." |
| relative_usage_change weight | 0.30 | "Do you step up or hide?" |
| playoff_elevation weight | 0.20 | "Does your usage hold up in the playoffs?" |

### Component 3: Shot Difficulty Embrace
| Parameter | Current Value | Justification |
|-----------|---------------|---------------|
| pullup_volume weight | 0.40 | "Off-dribble FGA - THE key differentiator" |
| midrange_pct weight | 0.30 | "Percentage of points from mid-range" |
| pullup_3_volume weight | 0.20 | "Off-dribble 3PA" |
| time_of_poss weight | 0.10 | "Possession length proxy" |

### Component 4: Defensive Survival
| Parameter | Current Value | Justification |
|-----------|---------------|---------------|
| clutch_volume_maintenance weight | 0.35 | "Do you maintain/increase usage under pressure?" |
| shot_versatility weight | 0.30 | "Can you be schemed? (Multiple modes = no)" |
| efficiency_resilience weight | 0.25 | "How well does efficiency hold?" |
| fragility_inverse weight | 0.10 | "Supporting signal from existing fragility" |

### Component 5: Force Multiplication
| Parameter | Current Value | Justification |
|-----------|---------------|---------------|
| physical_tools weight | 0.25 | "Do you HAVE the ability to generate FTs and rim shots?" |
| force_volume weight | 0.30 | "Do you USE the tools at high volume?" |
| force_agency weight | 0.25 | "Do you DEMAND the ball (not hide)?" |
| touch_production weight | 0.20 | "Do you produce points via touches?" |

## Gates and Corrections
| Gate | Condition | Justification |
|------|-----------|---------------|
| Hub Path Usage Gate | usage < 0.24 | Must have significant usage to qualify as Hub |
| Hub Path Leverage Gate | leverage_usg_delta < 0.0 | Must not be hiding under pressure (Sabonis filter) |
| Hub Path Touch Gate | touch_prod < 8.0 | Must have elite touch production |
| Hub Path TS Gate | ts_pct < 0.62 | Must have elite efficiency |
| Efficiency Resilience Vol Adj | leverage_usg_delta < 0 | "If you're hiding, efficiency score is discounted" |

## Total Parameter Count: 31

