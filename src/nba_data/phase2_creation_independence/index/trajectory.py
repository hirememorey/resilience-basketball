"""
Trajectory Independence Index (TII) Calculator

The TII answers: "If we gave this player 30% usage, would they maintain efficiency?"

This identifies LATENT ENGINES - players whose creation skills are present but 
underutilized due to role/opportunity constraints.

The key insight: Brunson in 2020-21 had:
- Low usage (0.196) but
- High creation_volume_ratio (0.69) when he DID create
- Elite efficiency (0.618 TS)
- Positive pressure response (+0.029 leverage_usg_delta)

The TII would have identified him as a Latent Engine 2 years before his breakout.

Components:
1. Scaling Efficiency (30%): Does efficiency hold when they create?
2. Pressure Appetite (25%): Do they seek high-leverage possessions?
3. Creation Tool Depth (20%): Do they have the tools even if underused?
4. Opportunity Response (15%): Do they step up when given more opportunity?
5. Age Trajectory (10%): How much runway for development?

Formula:
    TII = 0.30 × Scaling_Efficiency
        + 0.25 × Pressure_Appetite
        + 0.20 × Creation_Tools
        + 0.15 × Opportunity_Response
        + 0.10 × Age_Trajectory
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Component weights
WEIGHTS = {
    'scaling_efficiency': 0.30,
    'pressure_appetite': 0.25,
    'creation_tools': 0.20,
    'opportunity_response': 0.15,
    'age_trajectory': 0.10
}

# Thresholds for each component
THRESHOLDS = {
    # Scaling Efficiency
    'ts_elite': 0.58,
    'ts_good': 0.55,
    'cvr_elite': 0.60,
    'cvr_good': 0.50,
    
    # Pressure Appetite
    'leverage_elite': 0.05,
    'leverage_good': 0.00,
    'leverage_hiding': -0.03,
    
    # Creation Tools
    'pull_up_rate_elite': 0.15,  # pull_up_fga / (usg_pct * 82)
    'mid_range_elite': 0.15,    # pct_pts_2pt_mr
    'time_of_poss_elite': 4.0,
    
    # Age
    'age_young': 22,
    'age_prime': 25,
    'age_established': 28,
    'age_veteran': 31
}


def calculate_tii(player_data: pd.Series) -> Dict[str, float]:
    """
    Calculate the Trajectory Independence Index for a player.
    
    Args:
        player_data: Series containing player features for a single season
        
    Returns:
        Dictionary containing:
        - 'tii': The composite Trajectory Independence Index (0-100)
        - 'components': Individual component scores
        - 'tii_archetype': Scaling potential archetype
        - 'confidence': Confidence level
    """
    
    # Calculate each component
    component_scores = {
        'scaling_efficiency': _calculate_scaling_efficiency(player_data),
        'pressure_appetite': _calculate_pressure_appetite(player_data),
        'creation_tools': _calculate_creation_tools(player_data),
        'opportunity_response': _calculate_opportunity_response(player_data),
        'age_trajectory': _calculate_age_trajectory(player_data)
    }
    
    # Calculate weighted TII
    tii = sum(
        component_scores[component] * weight
        for component, weight in WEIGHTS.items()
    )
    
    # Clamp to valid range
    tii = np.clip(tii, 0, 100)
    
    # Determine TII archetype
    tii_archetype = _determine_tii_archetype(tii)
    
    # Calculate confidence
    confidence = _calculate_confidence(player_data)
    
    return {
        'tii': round(tii, 2),
        'components': component_scores,
        'tii_archetype': tii_archetype,
        'confidence': confidence
    }


def _calculate_scaling_efficiency(data: pd.Series) -> float:
    """
    Calculate Scaling Efficiency Score (30%).
    
    Question: Does this player create efficiently WHEN THEY CREATE?
    
    A player taking 2 ISO shots with 60% EFG has more latent ability
    than one taking 8 ISO shots with 40% EFG.
    
    Key insight: High creation_volume_ratio + High TS at LOW usage = latent skill
    
    CRITICAL GATE: Must have creation TOOLS to have scaling efficiency.
    Simmons has high TS but zero pull-ups = cannot scale.
    """
    # Get inputs
    ts_pct = data.get('ts_pct', 0.55)
    cvr = data.get('creation_volume_ratio', 0.50)
    usg_pct = data.get('usg_pct', 0.20)
    subsidy = data.get('subsidy_index', 0.50)
    pull_up_fga = data.get('pull_up_fga', 0.0)
    mid_range = data.get('pct_pts_2pt_mr', 0.0)
    
    # Handle NaN and format
    if pd.isna(ts_pct): ts_pct = 0.55
    if pd.isna(cvr): cvr = 0.50
    if pd.isna(usg_pct): usg_pct = 0.20
    if pd.isna(subsidy): subsidy = 0.50
    if pd.isna(pull_up_fga): pull_up_fga = 0.0
    if pd.isna(mid_range): mid_range = 0.0
    if ts_pct > 1.0: ts_pct /= 100.0
    if usg_pct > 1.0: usg_pct /= 100.0
    
    # CRITICAL GATE: Creation Tools Check
    # You can't have "scaling efficiency" without tools to scale WITH
    # Simmons trap: High TS, High CVR (from assists), but no real pull-up JUMPERS
    # His "pull-ups" are drives ending in layups - not scalable creation
    pull_up_fg3a = data.get('pull_up_fg3a', 0.0)
    if pd.isna(pull_up_fg3a): pull_up_fg3a = 0.0
    
    # Real creation tools require JUMPERS, not just layups after dribbles:
    # - Pull-up 3s (range)
    # - OR significant mid-range game (8%+ of points from mid-range)
    has_range = pull_up_fg3a >= 0.5  # Takes pull-up 3s
    has_mid_range = mid_range >= 0.08  # Significant mid-range
    has_volume_pullups = pull_up_fga >= 2.0  # Enough volume to matter
    
    # Real creation tools = has range OR mid-range AND has volume
    has_real_tools = (has_range or has_mid_range) and has_volume_pullups
    has_some_tools = (has_range or has_mid_range) or (pull_up_fga >= 1.5 and mid_range >= 0.05)
    
    if not has_some_tools:
        # No creation tools = max 40 points on scaling efficiency
        # Their "efficiency" is from dunks/layups, not creation
        tool_penalty = 0.40  # Cap at 40% of max score
    elif not has_real_tools:
        tool_penalty = 0.60  # Has some tools, but limited jumper ability
    else:
        tool_penalty = 1.0   # Full credit
    
    # Sub-metric 1: Efficiency at Creation (40%)
    # High TS + High CVR = skill, not system
    if cvr >= THRESHOLDS['cvr_elite'] and ts_pct >= THRESHOLDS['ts_elite']:
        efficiency_score = 80 + (ts_pct - THRESHOLDS['ts_elite']) / 0.07 * 20
    elif cvr >= THRESHOLDS['cvr_good'] and ts_pct >= THRESHOLDS['ts_good']:
        efficiency_score = 60 + (ts_pct - THRESHOLDS['ts_good']) / 0.03 * 20
    else:
        efficiency_score = max(0, (ts_pct - 0.50) / 0.05 * 40)
    efficiency_score = np.clip(efficiency_score, 0, 100)
    
    # Sub-metric 2: Creation Rate vs Usage (30%)
    # High creation rate at low usage = latent ability
    creation_rate_ratio = cvr / max(usg_pct, 0.10)
    # Ratio of 3+ is elite (e.g., CVR 0.60 at USG 0.20)
    rate_score = min(creation_rate_ratio / 4.0 * 100, 100)
    
    # Sub-metric 3: Subsidy Inverse (30%)
    # Low subsidy = portable efficiency (not system-dependent)
    subsidy_inverse_score = (1 - subsidy) * 100
    
    # Weighted combination with tool penalty
    score = (
        0.40 * efficiency_score +
        0.30 * rate_score +
        0.30 * subsidy_inverse_score
    ) * tool_penalty
    
    return np.clip(score, 0, 100)


def _calculate_pressure_appetite(data: pd.Series) -> float:
    """
    Calculate Pressure Appetite Score (25%).
    
    Question: Does this player SEEK high-leverage possessions?
    
    Key insight: A backup who takes clutch shots when given the chance
    is different from one who hides. Latent Engines have positive
    pressure response even when overall opportunity is limited.
    """
    # Get inputs
    leverage_usg = data.get('leverage_usg_delta', 0.0)
    clutch_usg = data.get('clutch_usg_absolute', 0.15)
    usg_pct = data.get('usg_pct', 0.20)
    leverage_ts = data.get('leverage_ts_delta', 0.0)
    
    # Handle NaN
    if pd.isna(leverage_usg): leverage_usg = 0.0
    if pd.isna(clutch_usg): clutch_usg = 0.15
    if pd.isna(usg_pct): usg_pct = 0.20
    if pd.isna(leverage_ts): leverage_ts = 0.0
    if clutch_usg > 1.0: clutch_usg /= 100.0
    if usg_pct > 1.0: usg_pct /= 100.0
    
    # CRITICAL GATE: Hiding pattern caps the score
    if leverage_usg < THRESHOLDS['leverage_hiding']:
        # Negative leverage = hiding = NOT a latent engine
        # Max score is 40
        leverage_score = 40 * (1 + leverage_usg / 0.10)  # -0.10 → 0, -0.03 → 40
        leverage_score = np.clip(leverage_score, 0, 40)
        return leverage_score
    
    # Sub-metric 1: Leverage USG Delta (50%)
    if leverage_usg >= THRESHOLDS['leverage_elite']:
        leverage_score = 80 + (leverage_usg - THRESHOLDS['leverage_elite']) / 0.10 * 20
    elif leverage_usg >= THRESHOLDS['leverage_good']:
        leverage_score = 60 + (leverage_usg - THRESHOLDS['leverage_good']) / 0.05 * 20
    else:
        leverage_score = 40 + (leverage_usg - THRESHOLDS['leverage_hiding']) / 0.03 * 20
    leverage_score = np.clip(leverage_score, 0, 100)
    
    # Sub-metric 2: Clutch USG Relative (30%)
    # High clutch usage relative to base = seeks pressure
    clutch_ratio = clutch_usg / max(usg_pct, 0.10)
    if clutch_ratio >= 1.1:  # 10%+ increase in clutch
        clutch_score = 80 + (clutch_ratio - 1.1) / 0.3 * 20
    elif clutch_ratio >= 1.0:  # Stable or slightly up
        clutch_score = 60 + (clutch_ratio - 1.0) / 0.1 * 20
    else:  # Drops in clutch
        clutch_score = max(0, 60 * clutch_ratio)
    clutch_score = np.clip(clutch_score, 0, 100)
    
    # Sub-metric 3: Pressure Consistency (20%)
    # Maintains efficiency under pressure
    if leverage_ts >= 0.02:  # Improves under pressure
        pressure_score = 90
    elif leverage_ts >= -0.02:  # Stable
        pressure_score = 70
    elif leverage_ts >= -0.05:  # Slight drop
        pressure_score = 50
    else:  # Collapses
        pressure_score = 30
    
    # Weighted combination
    score = (
        0.50 * leverage_score +
        0.30 * clutch_score +
        0.20 * pressure_score
    )
    
    return np.clip(score, 0, 100)


def _calculate_creation_tools(data: pd.Series) -> float:
    """
    Calculate Creation Tool Depth Score (20%).
    
    Question: Does this player have the TOOLS for high-volume creation?
    
    Key insight: Creation tools (pull-up shooting, mid-range, handle)
    predict scaling ability. A player with tools but low usage has
    latent capacity.
    """
    # Get inputs
    pull_up_fga = data.get('pull_up_fga', 0.0)
    pull_up_fg3a = data.get('pull_up_fg3a', 0.0)
    pull_up_fg3m = data.get('pull_up_fg3m', 0.0)
    mid_range = data.get('pct_pts_2pt_mr', 0.0)
    time_of_poss = data.get('time_of_poss', 2.0)
    usg_pct = data.get('usg_pct', 0.20)
    
    # Handle NaN
    if pd.isna(pull_up_fga): pull_up_fga = 0.0
    if pd.isna(pull_up_fg3a): pull_up_fg3a = 0.0
    if pd.isna(pull_up_fg3m): pull_up_fg3m = 0.0
    if pd.isna(mid_range): mid_range = 0.0
    if pd.isna(time_of_poss): time_of_poss = 2.0
    if pd.isna(usg_pct): usg_pct = 0.20
    if usg_pct > 1.0: usg_pct /= 100.0
    
    # Sub-metric 1: Pull-Up Rate (35%)
    # Normalize by usage - high rate at low usage = tools present
    # Assume 82 games for normalization
    pull_up_rate = pull_up_fga / max(usg_pct * 82, 1)
    if pull_up_rate >= THRESHOLDS['pull_up_rate_elite']:
        pull_up_score = 80 + (pull_up_rate - THRESHOLDS['pull_up_rate_elite']) / 0.10 * 20
    else:
        pull_up_score = (pull_up_rate / THRESHOLDS['pull_up_rate_elite']) * 80
    pull_up_score = np.clip(pull_up_score, 0, 100)
    
    # Sub-metric 2: Mid-Range Game (25%)
    # Mid-range is schematic-proof - elite playoff skill
    if mid_range >= THRESHOLDS['mid_range_elite']:
        mid_score = 80 + (mid_range - THRESHOLDS['mid_range_elite']) / 0.10 * 20
    else:
        mid_score = (mid_range / THRESHOLDS['mid_range_elite']) * 80
    mid_score = np.clip(mid_score, 0, 100)
    
    # Sub-metric 3: Time of Possession (25%)
    # Ball handling ability
    if time_of_poss >= THRESHOLDS['time_of_poss_elite']:
        time_score = 80 + (time_of_poss - THRESHOLDS['time_of_poss_elite']) / 2.0 * 20
    else:
        time_score = (time_of_poss / THRESHOLDS['time_of_poss_elite']) * 80
    time_score = np.clip(time_score, 0, 100)
    
    # Sub-metric 4: Tool Efficiency (15%)
    # Can they hit the shots?
    if pull_up_fg3a > 0:
        pull_up_3_pct = pull_up_fg3m / pull_up_fg3a
        if pull_up_3_pct >= 0.38:
            tool_eff_score = 90
        elif pull_up_3_pct >= 0.35:
            tool_eff_score = 75
        elif pull_up_3_pct >= 0.30:
            tool_eff_score = 55
        else:
            tool_eff_score = 35
    else:
        tool_eff_score = 30  # No pull-up 3s = limited range
    
    # Weighted combination
    score = (
        0.35 * pull_up_score +
        0.25 * mid_score +
        0.25 * time_score +
        0.15 * tool_eff_score
    )
    
    return np.clip(score, 0, 100)


def _calculate_opportunity_response(data: pd.Series) -> float:
    """
    Calculate Opportunity Response Score (15%).
    
    Question: When given MORE opportunity, does this player step up?
    
    Key insight: Natural experiments (playoff usage bump, starter injured)
    reveal scaling ability. Players who maintain efficiency as usage
    increases have latent Engine potential.
    
    NOTE: Without game-by-game data, we use proxies:
    - Usage trajectory (YoY growth with efficiency maintenance)
    - Minutes-efficiency relationship
    """
    # Get inputs (current season)
    usg_pct = data.get('usg_pct', 0.20)
    ts_pct = data.get('ts_pct', 0.55)
    minutes = data.get('minutes', 20.0)
    
    # Handle NaN
    if pd.isna(usg_pct): usg_pct = 0.20
    if pd.isna(ts_pct): ts_pct = 0.55
    if pd.isna(minutes): minutes = 20.0
    if usg_pct > 1.0: usg_pct /= 100.0
    if ts_pct > 1.0: ts_pct /= 100.0
    
    # We don't have YoY data in single-row input
    # Use proxy: efficiency relative to usage level
    
    # Sub-metric 1: Usage-Adjusted Efficiency (50%)
    # High efficiency at ANY usage is good
    # But high efficiency at high usage is better proven
    # High efficiency at low usage = latent potential
    
    # Expected TS drop per usage point (empirical)
    expected_ts = 0.57 - (usg_pct - 0.20) * 0.2  # Higher usage → lower expected TS
    ts_vs_expected = ts_pct - expected_ts
    
    if ts_vs_expected >= 0.03:  # 3%+ above expected
        usg_adj_score = 90
    elif ts_vs_expected >= 0.01:
        usg_adj_score = 75
    elif ts_vs_expected >= -0.01:
        usg_adj_score = 60
    else:
        usg_adj_score = 40
    
    # Sub-metric 2: Minutes Efficiency (30%)
    # Players who maintain efficiency at high minutes have depth
    minutes_score = min(minutes / 35.0 * 100, 100)  # 35+ minutes = full score
    if ts_pct >= 0.58:  # Efficient at high minutes = bonus
        minutes_score *= 1.1
    minutes_score = np.clip(minutes_score, 0, 100)
    
    # Sub-metric 3: Role Upside (20%)
    # Low usage + good efficiency = room to grow
    if usg_pct < 0.22 and ts_pct >= 0.55:
        role_score = 85  # Lots of room to grow efficiently
    elif usg_pct < 0.26 and ts_pct >= 0.55:
        role_score = 70  # Some room to grow
    else:
        role_score = 55  # Already at higher usage or inefficient
    
    # Weighted combination
    score = (
        0.50 * usg_adj_score +
        0.30 * minutes_score +
        0.20 * role_score
    )
    
    return np.clip(score, 0, 100)


def _calculate_age_trajectory(data: pd.Series) -> float:
    """
    Calculate Age Trajectory Score (10%).
    
    Question: Given this player's age, how much development runway?
    
    Young + positive signals = higher value
    Old + positive signals = already peaked
    """
    age = data.get('age', 25.0)
    
    # Handle NaN
    if pd.isna(age): age = 25.0
    
    # Age ceiling score
    if age <= THRESHOLDS['age_young']:  # ≤22
        age_score = 100
    elif age <= THRESHOLDS['age_prime']:  # 23-25
        age_score = 100 - (age - THRESHOLDS['age_young']) * 5
    elif age <= THRESHOLDS['age_established']:  # 26-28
        age_score = 85 - (age - THRESHOLDS['age_prime']) * 6.67
    elif age <= THRESHOLDS['age_veteran']:  # 29-31
        age_score = 65 - (age - THRESHOLDS['age_established']) * 8.33
    else:  # 32+
        age_score = max(20, 40 - (age - THRESHOLDS['age_veteran']) * 5)
    
    return np.clip(age_score, 0, 100)


def _determine_tii_archetype(tii: float) -> str:
    """
    Map TII score to scaling archetype.
    
    | TII Range | Archetype |
    |-----------|-----------|
    | 80+       | Elite Scaling |
    | 65-80     | High Scaling |
    | 50-65     | Moderate Scaling |
    | 35-50     | Limited Scaling |
    | <35       | Low Scaling |
    """
    if tii >= 80:
        return "Elite Scaling"
    elif tii >= 65:
        return "High Scaling"
    elif tii >= 50:
        return "Moderate Scaling"
    elif tii >= 35:
        return "Limited Scaling"
    else:
        return "Low Scaling"


def _calculate_confidence(data: pd.Series) -> str:
    """Calculate confidence level based on data completeness."""
    high_confidence_features = [
        'creation_volume_ratio',
        'leverage_usg_delta',
        'clutch_usg_absolute',
        'pull_up_fga',
        'time_of_poss',
        'subsidy_index',
        'age'
    ]
    
    present = sum(1 for f in high_confidence_features
                  if f in data.index and not pd.isna(data.get(f)))
    
    if present >= 6:
        return 'High'
    elif present >= 4:
        return 'Medium'
    else:
        return 'Low'


def diagnose_player_tii(player_data: pd.Series) -> None:
    """Print detailed TII breakdown for a player."""
    player_name = player_data.get('player_name', 'Unknown')
    season = player_data.get('season', 'N/A')
    
    print(f"\n{'='*70}")
    print(f"TII Diagnosis: {player_name} ({season})")
    print(f"{'='*70}")
    
    # Calculate each component
    scaling = _calculate_scaling_efficiency(player_data)
    pressure = _calculate_pressure_appetite(player_data)
    tools = _calculate_creation_tools(player_data)
    opportunity = _calculate_opportunity_response(player_data)
    age = _calculate_age_trajectory(player_data)
    
    print(f"\nComponent Scores (weighted):")
    print(f"  1. Scaling Efficiency (30%): {scaling:.1f}")
    print(f"     - TS%: {player_data.get('ts_pct', 'N/A')}")
    print(f"     - CVR: {player_data.get('creation_volume_ratio', 'N/A')}")
    print(f"     - USG: {player_data.get('usg_pct', 'N/A')}")
    print(f"     - Subsidy: {player_data.get('subsidy_index', 'N/A')}")
    
    print(f"\n  2. Pressure Appetite (25%): {pressure:.1f}")
    print(f"     - Leverage USG Delta: {player_data.get('leverage_usg_delta', 'N/A')}")
    print(f"     - Clutch USG: {player_data.get('clutch_usg_absolute', 'N/A')}")
    print(f"     - Leverage TS Delta: {player_data.get('leverage_ts_delta', 'N/A')}")
    
    print(f"\n  3. Creation Tools (20%): {tools:.1f}")
    print(f"     - Pull-up FGA: {player_data.get('pull_up_fga', 'N/A')}")
    print(f"     - Mid-range %: {player_data.get('pct_pts_2pt_mr', 'N/A')}")
    print(f"     - Time of Poss: {player_data.get('time_of_poss', 'N/A')}")
    
    print(f"\n  4. Opportunity Response (15%): {opportunity:.1f}")
    print(f"     - Minutes: {player_data.get('minutes', 'N/A')}")
    
    print(f"\n  5. Age Trajectory (10%): {age:.1f}")
    print(f"     - Age: {player_data.get('age', 'N/A')}")
    
    # Final TII
    tii_result = calculate_tii(player_data)
    print(f"\n{'='*50}")
    print(f"FINAL TII: {tii_result['tii']:.1f} → {tii_result['tii_archetype']}")
    print(f"{'='*50}")


# Validation cases
VALIDATION_CASES = {
    # MUST-PASS: Latent Engine Detection
    'Jalen Brunson 2020-21': {
        'player_name': 'Jalen Brunson',
        'season': '2020-21',
        'expected_tii': 80,
        'tolerance': 10,
        'expected_archetype': 'Elite Scaling',
        'rationale': 'Low usage, elite efficiency, positive pressure, tools present'
    },
    'SGA 2019-20': {
        'player_name': 'Shai Gilgeous-Alexander',
        'season': '2019-20',
        'expected_tii': 75,
        'tolerance': 10,
        'expected_archetype': 'High Scaling',
        'rationale': 'With CP3, limited touches but creation tools visible'
    },
    
    # MUST-FAIL: False Latent Engine Rejection
    'Ben Simmons 2019-20': {
        'player_name': 'Ben Simmons',
        'season': '2019-20',
        'expected_tii': 35,
        'tolerance': 10,
        'expected_archetype': 'Limited Scaling',
        'rationale': 'No creation tools, negative pressure response'
    },
    'Domantas Sabonis 2022-23': {
        'player_name': 'Domantas Sabonis',
        'season': '2022-23',
        'expected_tii': 40,
        'tolerance': 10,
        'expected_archetype': 'Limited Scaling',
        'rationale': 'Hiding under pressure, no scaling potential'
    },
    'Julius Randle 2020-21': {
        'player_name': 'Julius Randle',
        'season': '2020-21',
        'expected_tii': 45,
        'tolerance': 10,
        'expected_archetype': 'Limited Scaling',
        'rationale': 'High volume but ISO EFG poor, collapsed in playoffs'
    }
}


if __name__ == '__main__':
    import pandas as pd
    from pathlib import Path
    
    # Load dataset
    dataset_path = Path(__file__).parents[4] / 'results' / 'predictive_dataset_with_friction.csv'
    
    if dataset_path.exists():
        print(f"Loading dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)
        
        # Test key cases
        test_cases = [
            ('Jalen Brunson', '2020-21'),  # Latent Engine
            ('Jalen Brunson', '2023-24'),  # Realized Engine
            ('Ben Simmons', '2019-20'),     # False Latent (hiding)
            ('Shai Gilgeous-Alexander', '2019-20'),  # Latent Engine
            ('James Harden', '2018-19'),   # Already Engine
            ('Domantas Sabonis', '2022-23'),  # False Latent (hiding)
        ]
        
        for player_name, season in test_cases:
            mask = (df['player_name'].str.lower() == player_name.lower()) & (df['season'] == season)
            if mask.any():
                player_data = df[mask].iloc[0]
                diagnose_player_tii(player_data)
            else:
                print(f"\n--- Could not find {player_name} {season} ---")
    else:
        print(f"Dataset not found at {dataset_path}")

