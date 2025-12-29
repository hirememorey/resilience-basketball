"""
Component 3: Shot Difficulty Embrace Score (Weight: 20%)

Question: Can you create offense when the defense knows you're getting the ball?

Physics Principle:
Creators must generate offense through EITHER:
- Perimeter creation: Pull-ups, mid-range, off-dribble 3s (Tatum, Harden, DeRozan)
- Force creation: Rim attacks through contact at high volume (Giannis, Zion)
- Hub creation: Elite efficiency via post orchestration (Jokić, prime Shaq)

TWO VALID PATHS (same as Component 1):
1. Perimeter Path: Pull-ups, mid-range, off-dribble 3s
2. Hub Path: Elite efficiency at high volume with positive pressure response

For hub creators like Jokić, taking "easy" shots at 70% TS is BETTER than 
taking hard shots at 55% TS. They've solved the difficulty problem by 
manufacturing good looks - that's skill, not avoidance.

CRITICAL INSIGHT (from development):
Raw contested_shot_rate is a TRAP metric. Players like Simmons and Gobert have
the HIGHEST contested rates (~0.76-0.85) because they only take layups/dunks in
traffic. This conflates "embracing difficulty" with "being forced into traffic."

The fix: Use pull-up volume and mid-range as PRIMARY signals for perimeter path,
and add Hub Creation path that rewards elite efficiency + pressure response
WITHOUT rewarding players who hide (Sabonis) or lack the tools (Gobert).

Sub-Metrics (Perimeter Path):
- Pull-up Volume (40%): Off-dribble FGA - THE key differentiator
- Mid-Range % (30%): Percentage of points from mid-range
- Pull-up 3 Volume (20%): Off-dribble 3PA
- Time of Possession (10%): Possession length proxy

Hub Creation Path (gates same as C1):
- Elite efficiency (65%+ TS) at significant usage (24%+)
- Positive pressure response (leverage_usg_delta >= 0)
- Elite touch production (8+ points from touches)
This prevents Sabonis (hides) and Gobert (no touch game) from benefiting.

Validation Cases:
- Ben Simmons: ~10-20 (no perimeter, no hub - fails both paths)
- Rudy Gobert: ~0-5 (pure finisher, fails both paths)
- Domantas Sabonis: ~10-15 (good touches but HIDES - no hub bonus)
- Nikola Jokić: ~75-85 (elite hub creation)
- Giannis Antetokounmpo: ~35-50 (moderate pull-ups, some hub traits)
- Jayson Tatum: ~60-80 (elite perimeter creation)
- DeMar DeRozan: ~75-90 (maximum mid-range embrace)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# WEIGHTS - Inverted from original to remove contested_shot_rate trap
# =============================================================================
WEIGHTS = {
    'pullup_volume': 0.40,      # Primary: Off-dribble jump shots
    'midrange_pct': 0.30,       # Secondary: Mid-range willingness  
    'pullup_3_volume': 0.20,    # Tertiary: Off-dribble 3s
    'time_of_poss': 0.10        # Supporting: Possession length
}

# NOTE: Rim creation is NOT included in Component 3.
# 
# Rationale: Component 3 measures "shot difficulty embrace" - the willingness
# to take HARD SHOTS. Force creators like Giannis get credit in:
# - Component 1 (Self-Created Shot Score): via creation_volume_ratio
# - Component 5 (Force Multiplication): via physicality_score + FTr
#
# Including rim creation here caused Simmons to score similarly to Tatum
# because both "create through drives" - but Simmons has NO OTHER OPTIONS
# while Tatum has pull-ups, mid-range, and step-backs.
#
# The jump shot metrics naturally separate them:
# - Simmons: 0.7 pull_up_fga, 0 pull_up_fg3a
# - Tatum: 10.4 pull_up_fga, 7.2 pull_up_fg3a

# =============================================================================
# SCALING BENCHMARKS - Derived from data analysis
# =============================================================================
BENCHMARKS = {
    # Pull-up FGA per game
    'pullup_fga_floor': 0.0,
    'pullup_fga_ceiling': 10.0,  # Elite: Tatum, DeRozan, Lillard
    
    # Mid-range as % of points
    'midrange_pct_floor': 0.0,
    'midrange_pct_ceiling': 0.30,  # Elite: DeRozan (35%), Middleton (25%)
    
    # Pull-up 3PA per game
    'pullup_3_floor': 0.0,
    'pullup_3_ceiling': 7.0,  # Elite: Lillard, Tatum, Harden
    
    # Time of possession (seconds)
    'time_floor': 2.0,
    'time_ceiling': 7.0,  # Elite: Harden, Luka
}

# Hub Creation thresholds (same as Component 1)
HUB_THRESHOLDS = {
    'touch_production_elite': 8.0,     # 8+ points from touches = elite
    'touch_production_max': 12.0,      # For scaling
    'ts_elite': 0.65,                  # 65%+ TS = elite efficiency (slightly higher than C1)
    'ts_max': 0.72,                    # For scaling
    'leverage_threshold': 0.0,         # Must be non-negative (not hiding)
    'usage_threshold': 0.24,           # Must have significant usage to qualify
}


def calculate_difficulty_embrace_score(player_data: pd.Series) -> float:
    """
    Calculate Shot Difficulty Embrace Score (0-100).
    
    Uses TWO PATHS and takes the maximum (same logic as Component 1):
    1. Perimeter Path: Pull-ups, mid-range, off-dribble 3s (Harden, Tatum, DeRozan)
    2. Hub Path: Elite efficiency at volume with positive pressure (Jokić)
    
    Args:
        player_data: Series containing player features for a season
        
    Returns:
        Score from 0-100 where:
        - 0-20: No creation (Simmons, Gobert)
        - 20-40: Limited creation
        - 40-60: Moderate creation (hybrid bigs, developing guards)
        - 60-80: Strong creation (most stars)
        - 80-100: Elite creation (Tatum, DeRozan, Jokić)
    """
    
    # PATH 1: Perimeter creation (existing logic)
    perimeter_score = _calculate_perimeter_difficulty_score(player_data)
    
    # PATH 2: Hub creation (elite efficiency = solved the difficulty problem)
    hub_score = _calculate_hub_difficulty_score(player_data)
    
    # Take the MAXIMUM of both paths
    final_score = max(perimeter_score, hub_score)
    
    return round(np.clip(final_score, 0, 100), 2)


def _calculate_perimeter_difficulty_score(player_data: pd.Series) -> float:
    """
    Calculate perimeter difficulty score (original logic).
    
    For guards/wings who create via pull-ups, mid-range, stepbacks.
    """
    # Sub-metric 1: Pull-up Volume (40%)
    pullup_score = _calculate_pullup_volume_score(player_data)
    
    # Sub-metric 2: Mid-Range % of Points (30%)
    midrange_score = _calculate_midrange_pct_score(player_data)
    
    # Sub-metric 3: Pull-up 3 Volume (20%)
    pullup_3_score = _calculate_pullup_3_score(player_data)
    
    # Sub-metric 4: Time of Possession (10%)
    time_score = _calculate_time_score(player_data)
    
    # Weighted combination
    score = (
        WEIGHTS['pullup_volume'] * pullup_score +
        WEIGHTS['midrange_pct'] * midrange_score +
        WEIGHTS['pullup_3_volume'] * pullup_3_score +
        WEIGHTS['time_of_poss'] * time_score
    )
    
    return np.clip(score, 0, 100)


def _calculate_hub_difficulty_score(player_data: pd.Series) -> float:
    """
    Calculate hub difficulty score for post-centric orchestrators.
    
    For bigs who "solve" difficulty through elite efficiency rather than
    shot-making. Taking an "easy" shot at 70% TS is BETTER than taking
    a hard shot at 55% TS - they've manufactured the advantage.
    
    REQUIRES ALL THREE GATES (same as Component 1):
    1. Elite efficiency (65%+ TS at significant usage)
    2. Non-hiding pressure response (leverage_usg_delta >= 0)
    3. Elite touch production (8+ points from touches)
    
    This prevents Sabonis (hides), Gobert (no touch game), and
    role players (low usage) from benefiting.
    """
    # Get inputs
    touch_prod = player_data.get('weighted_touch_production', 
                          player_data.get('WEIGHTED_TOUCH_PRODUCTION', 0))
    ts_pct = player_data.get('ts_pct', player_data.get('TS_PCT', 0.55))
    leverage_usg = player_data.get('leverage_usg_delta',
                            player_data.get('LEVERAGE_USG_DELTA', 0))
    usage = player_data.get('usg_pct', player_data.get('USG_PCT', 0.15))
    
    # Handle NaN and percentages
    if pd.isna(touch_prod): touch_prod = 0
    if pd.isna(ts_pct): ts_pct = 0.55
    if pd.isna(leverage_usg): leverage_usg = 0
    if pd.isna(usage): usage = 0.15
    if ts_pct > 1.0: ts_pct = ts_pct / 100.0
    if usage > 1.0: usage = usage / 100.0
    
    # GATE 1: Must have significant usage (not a role player)
    if usage < HUB_THRESHOLDS['usage_threshold']:
        return 0.0
    
    # GATE 2: Must NOT be hiding under pressure
    if leverage_usg < HUB_THRESHOLDS['leverage_threshold']:
        return 0.0
    
    # GATE 3: Must have elite touch production
    if touch_prod < HUB_THRESHOLDS['touch_production_elite']:
        return 0.0
    
    # GATE 4: Must have elite efficiency
    if ts_pct < HUB_THRESHOLDS['ts_elite']:
        return 0.0
    
    # All gates passed - calculate score
    
    # Efficiency score (65% → 70, 72%+ → 100)
    eff_score = (ts_pct - HUB_THRESHOLDS['ts_elite']) / \
                (HUB_THRESHOLDS['ts_max'] - HUB_THRESHOLDS['ts_elite'])
    eff_score = 70 + (eff_score * 30)  # 70-100 range
    eff_score = np.clip(eff_score, 70, 100)
    
    # Touch production score (8 → 75, 12+ → 100)
    touch_score = (touch_prod - HUB_THRESHOLDS['touch_production_elite']) / \
                  (HUB_THRESHOLDS['touch_production_max'] - HUB_THRESHOLDS['touch_production_elite'])
    touch_score = 75 + (touch_score * 25)  # 75-100 range
    touch_score = np.clip(touch_score, 75, 100)
    
    # Combined score (efficiency primary, touch secondary)
    base_score = (eff_score * 0.6 + touch_score * 0.4)
    
    return np.clip(base_score, 0, 100)


def _calculate_pullup_volume_score(data: pd.Series) -> float:
    """
    Calculate score based on pull-up FGA volume.
    
    This is THE key differentiator between shot creators and rim-dependent players.
    
    Data shows:
    - Simmons: 0.7 pull-up FGA
    - Gobert: 0.0 pull-up FGA
    - Tatum: 8.7-10.4 pull-up FGA
    - DeRozan: 8.1-10.1 pull-up FGA
    
    The 10x gap between Simmons and Tatum is the signal we need.
    """
    # Primary: pull_up_fga (available in dataset)
    pullup_fga = data.get('pull_up_fga', 0)
    
    if pd.isna(pullup_fga):
        pullup_fga = 0
    
    # Scale: 0 FGA = 0, 10+ FGA = 100
    floor = BENCHMARKS['pullup_fga_floor']
    ceiling = BENCHMARKS['pullup_fga_ceiling']
    
    score = (pullup_fga - floor) / (ceiling - floor) * 100
    return np.clip(score, 0, 100)


def _calculate_midrange_pct_score(data: pd.Series) -> float:
    """
    Calculate score based on mid-range as percentage of points.
    
    Mid-range is the "dying art" that separates shot creators from
    efficiency optimizers. Elite mid-range scorers have more options
    when the paint and 3pt line are taken away.
    
    Data shows:
    - Simmons: 1.7% of points from mid-range
    - Gobert: 0% of points from mid-range
    - Middleton: 21-27% of points from mid-range
    - DeRozan: 25-35% of points from mid-range
    """
    # Primary: pct_pts_2pt_mr (available in dataset)
    midrange_pct = data.get('pct_pts_2pt_mr', 0)
    
    if pd.isna(midrange_pct):
        midrange_pct = 0
    
    # Scale: 0% = 0, 30%+ = 100
    floor = BENCHMARKS['midrange_pct_floor']
    ceiling = BENCHMARKS['midrange_pct_ceiling']
    
    score = (midrange_pct - floor) / (ceiling - floor) * 100
    return np.clip(score, 0, 100)


def _calculate_pullup_3_score(data: pd.Series) -> float:
    """
    Calculate score based on pull-up 3PA volume.
    
    Pull-up 3s are the hardest shots in basketball - off-dribble, contested,
    from range. Only elite creators attempt these at high volume.
    
    Data shows:
    - Simmons: 0.1 pull-up 3PA
    - Gobert: 0.0 pull-up 3PA
    - Tatum: 5.6-7.2 pull-up 3PA
    - Lillard: 5.7-7.4 pull-up 3PA
    """
    # Primary: pull_up_fg3a (available in dataset)
    pullup_3pa = data.get('pull_up_fg3a', 0)
    
    if pd.isna(pullup_3pa):
        pullup_3pa = 0
    
    # Scale: 0 3PA = 0, 7+ 3PA = 100
    floor = BENCHMARKS['pullup_3_floor']
    ceiling = BENCHMARKS['pullup_3_ceiling']
    
    score = (pullup_3pa - floor) / (ceiling - floor) * 100
    return np.clip(score, 0, 100)


# NOTE: _calculate_rim_creation_score has been removed from Component 3.
# Force creators (Giannis, Zion, Shaq) get credit through:
# - Component 1: Self-Created Shot Score (creation_volume_ratio)
# - Component 5: Force Multiplication Score (physicality_score, FTr)
#
# Including rim creation here caused the "Simmons/Gobert Trap" where
# players who drive but have no jumper scored similarly to stars who
# can do both. The jump shot metrics properly separate them.


def _calculate_time_score(data: pd.Series) -> float:
    """
    Calculate score based on time of possession.
    
    Longer possessions generally mean harder shots (defense is set).
    This is a supporting signal, not primary.
    
    Caveat: Some players (Simmons) have high time of possession because
    they hold the ball then pass. The other sub-metrics handle this.
    """
    time_of_poss = data.get('time_of_poss', 3.0)
    
    if pd.isna(time_of_poss):
        time_of_poss = 3.0
    
    # Scale: 2 sec = 0, 7+ sec = 100
    floor = BENCHMARKS['time_floor']
    ceiling = BENCHMARKS['time_ceiling']
    
    score = (time_of_poss - floor) / (ceiling - floor) * 100
    return np.clip(score, 0, 100)


def get_required_features() -> List[str]:
    """Return list of features required for this component."""
    return [
        # Perimeter path features
        'pull_up_fga',           # Off-dribble FGA
        'pct_pts_2pt_mr',        # Mid-range as % of points
        'pull_up_fg3a',          # Off-dribble 3PA
        'time_of_poss',          # Possession length
        # Hub path features
        'weighted_touch_production', # Touch points
        'ts_pct',                # Efficiency
        'leverage_usg_delta',    # Pressure response
        'usg_pct',               # Usage
    ]


def get_missing_features(df: pd.DataFrame) -> List[str]:
    """Check which required features are missing from dataset."""
    required = get_required_features()
    # Check both exact match and lowercase
    available = set(df.columns) | set(c.lower() for c in df.columns)
    missing = [f for f in required if f not in available and f.lower() not in available]
    return missing


def calculate_sub_scores(player_data: pd.Series) -> Dict[str, float]:
    """Calculate and return all sub-scores for debugging."""
    return {
        'pullup_volume (40%)': round(_calculate_pullup_volume_score(player_data), 2),
        'midrange_pct (30%)': round(_calculate_midrange_pct_score(player_data), 2),
        'pullup_3_volume (20%)': round(_calculate_pullup_3_score(player_data), 2),
        'time_of_poss (10%)': round(_calculate_time_score(player_data), 2),
    }


# =============================================================================
# VALIDATION CASES - Two paths: perimeter and hub creation
# =============================================================================
VALIDATION_CASES = {
    'Ben Simmons': {
        'season': '2019-20',
        'expected_score': 15,
        'tolerance': 10,
        'reason': 'No perimeter creation (0.7 pull-ups), no hub bonus (hides under pressure)'
    },
    'Rudy Gobert': {
        'season': '2020-21',
        'expected_score': 1,
        'tolerance': 3,
        'reason': 'Pure finisher - zero pull-ups, zero mid-range, low touches'
    },
    'Domantas Sabonis': {
        'season': '2022-23',
        'expected_score': 10,
        'tolerance': 8,
        'reason': 'Good touches but HIDES (leverage -0.058) - fails hub gates'
    },
    'Nikola Jokić': {
        'season': '2022-23',
        'expected_score': 80,
        'tolerance': 12,
        'reason': 'Elite hub creation (70% TS, 10.5 touches, steps UP)'
    },
    'Giannis Antetokounmpo': {
        'season': '2019-20',
        'expected_score': 45,
        'tolerance': 12,
        'reason': 'Hybrid - some hub traits, moderate pull-ups'
    },
    'Jayson Tatum': {
        'season': '2023-24',
        'expected_score': 70,
        'tolerance': 12,
        'reason': 'Elite perimeter creation (10+ pull-ups, good 3s)'
    },
    'DeMar DeRozan': {
        'season': '2021-22',
        'expected_score': 78,
        'tolerance': 10,
        'reason': 'Maximum mid-range embrace, elite pull-up volume'
    },
}


def validate_component(df: pd.DataFrame, verbose: bool = True) -> Dict[str, dict]:
    """
    Validate component against known test cases.
    
    Args:
        df: DataFrame with player data
        verbose: If True, print detailed results
        
    Returns:
        Dict mapping player names to pass/fail results
    """
    results = {}
    
    for player, case in VALIDATION_CASES.items():
        player_mask = df['player_name'].str.lower().str.contains(player.lower(), na=False)
        
        if not player_mask.any():
            results[player] = {
                'status': 'SKIP',
                'reason': 'Player not in dataset'
            }
            if verbose:
                print(f"⚠️  SKIP: {player} - not in dataset")
            continue
        
        # Get peak season (highest usage as proxy for peak)
        player_df = df[player_mask].sort_values('usg_pct', ascending=False)
        player_data = player_df.iloc[0]
        season = player_data.get('season', 'unknown')
        
        score = calculate_difficulty_embrace_score(player_data)
        sub_scores = calculate_sub_scores(player_data)
        expected = case['expected_score']
        tolerance = case['tolerance']
        
        passed = abs(score - expected) <= tolerance
        
        results[player] = {
            'status': 'PASS' if passed else 'FAIL',
            'score': score,
            'expected': expected,
            'tolerance': tolerance,
            'delta': round(score - expected, 2),
            'season': season,
            'sub_scores': sub_scores
        }
        
        if verbose:
            status_icon = "✅" if passed else "❌"
            print(f"{status_icon} {player} ({season}): {score:.1f} (expected {expected}±{tolerance})")
            print(f"   Sub-scores: {sub_scores}")
    
    # Summary
    if verbose:
        passed_count = sum(1 for r in results.values() if r.get('status') == 'PASS')
        total_count = sum(1 for r in results.values() if r.get('status') != 'SKIP')
        print(f"\n📊 Results: {passed_count}/{total_count} passed")
    
    return results


if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    # Load actual dataset
    results_dir = Path(__file__).parents[4] / 'results'
    dataset_path = results_dir / 'predictive_dataset_with_friction.csv'
    
    if dataset_path.exists():
        print("=" * 60)
        print("COMPONENT 3: SHOT DIFFICULTY EMBRACE - VALIDATION")
        print("=" * 60)
        print(f"\nLoading data from {dataset_path}...")
        
        df = pd.read_csv(dataset_path)
        print(f"Loaded {len(df)} player-seasons")
        
        # Check for missing features
        missing = get_missing_features(df)
        if missing:
            print(f"\n⚠️  Missing features: {missing}")
        
        # Run validation
        print("\n" + "-" * 40)
        print("VALIDATION RESULTS")
        print("-" * 40)
        results = validate_component(df, verbose=True)
        
        # Additional spot checks
        print("\n" + "-" * 40)
        print("ADDITIONAL SPOT CHECKS")
        print("-" * 40)
        
        spot_checks = ['James Harden', 'Damian Lillard', 'Anthony Davis', 'Joel Embiid']
        for player in spot_checks:
            player_mask = df['player_name'].str.lower().str.contains(player.lower(), na=False)
            if player_mask.any():
                player_df = df[player_mask].sort_values('usg_pct', ascending=False)
                player_data = player_df.iloc[0]
                score = calculate_difficulty_embrace_score(player_data)
                sub_scores = calculate_sub_scores(player_data)
                print(f"{player} ({player_data.get('season', '?')}): {score:.1f}")
                print(f"   {sub_scores}")
    else:
        print(f"Dataset not found at {dataset_path}")
        print("Running with synthetic test data...")
        
        # Synthetic test
        simmons_data = pd.Series({
            'pull_up_fga': 0.7,
            'pct_pts_2pt_mr': 0.017,
            'pull_up_fg3a': 0.1,
            'creation_volume_ratio': 0.63,
            'physicality_score': 0.63,
            'usg_pct': 0.32,
            'time_of_poss': 5.8,
        })
        
        tatum_data = pd.Series({
            'pull_up_fga': 10.4,
            'pct_pts_2pt_mr': 0.087,
            'pull_up_fg3a': 7.2,
            'creation_volume_ratio': 0.72,
            'physicality_score': 0.45,
            'usg_pct': 0.35,
            'time_of_poss': 5.2,
        })
        
        print(f"Simmons Score: {calculate_difficulty_embrace_score(simmons_data):.1f}")
        print(f"  Sub-scores: {calculate_sub_scores(simmons_data)}")
        print(f"Tatum Score: {calculate_difficulty_embrace_score(tatum_data):.1f}")
        print(f"  Sub-scores: {calculate_sub_scores(tatum_data)}")
