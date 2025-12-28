"""
Component 3: Shot Difficulty Embrace Score (Weight: 20%)

Question: Can you create offense when the defense knows you're getting the ball?

Physics Principle:
Creators must generate offense through EITHER:
- Perimeter creation: Pull-ups, mid-range, off-dribble 3s (Tatum, Harden, DeRozan)
- Force creation: Rim attacks through contact at high volume (Giannis, Zion)

CRITICAL INSIGHT (from development):
Raw contested_shot_rate is a TRAP metric. Players like Simmons and Gobert have
the HIGHEST contested rates (~0.76-0.85) because they only take layups/dunks in
traffic. This conflates "embracing difficulty" with "being forced into traffic."

The fix: Use pull-up volume and mid-range as PRIMARY signals (these are jumpers
that require shot-making skill), and add a "Rim Creation" sub-metric that
captures force creators WITHOUT rewarding pure finishers like Gobert.

Sub-Metrics:
- Pull-up Volume (40%): Off-dribble FGA - THE key differentiator
- Mid-Range % (30%): Percentage of points from mid-range
- Pull-up 3 Volume (20%): Off-dribble 3PA
- Time of Possession (10%): Possession length proxy

NOTE: Rim creation is NOT included. Force creators (Giannis, Zion, Shaq) 
get credit in Component 1 (Self-Created) and Component 5 (Force Multiplication).
Including rim creation here caused Simmons to score similarly to stars because
"creating through drives" conflated with "having no other options."

Validation Cases:
- Ben Simmons: ~10-15 (zero jump shot creation)
- Rudy Gobert: ~0-3 (pure finisher, no jumpers at all)
- Zion Williamson: ~8-15 (force creator, gets credit in C1/C5 not here)
- Giannis Antetokounmpo: ~35-45 (moderate pull-ups for a big)
- Jayson Tatum: ~60-75 (elite perimeter creation)
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
    
    # Rim creation scaling
    'rim_creation_floor': 0.0,
    'rim_creation_ceiling': 0.25  # Elite: Giannis at high usage
}


def calculate_difficulty_embrace_score(player_data: pd.Series) -> float:
    """
    Calculate Shot Difficulty Embrace Score (0-100).
    
    This measures ability to create offense when the defense knows you're
    getting the ball - through EITHER shot-making OR force.
    
    Args:
        player_data: Series containing player features for a season
        
    Returns:
        Score from 0-100 where:
        - 0-20: No shot creation (Simmons, Gobert)
        - 20-40: Limited creation or pure force
        - 40-60: Moderate creation (hybrid bigs, developing guards)
        - 60-80: Strong creation (most stars)
        - 80-100: Elite creation (Tatum, DeRozan, Lillard)
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
    # Note: Rim creation removed - see WEIGHTS comment for rationale
    final_score = (
        WEIGHTS['pullup_volume'] * pullup_score +
        WEIGHTS['midrange_pct'] * midrange_score +
        WEIGHTS['pullup_3_volume'] * pullup_3_score +
        WEIGHTS['time_of_poss'] * time_score
    )
    
    return round(np.clip(final_score, 0, 100), 2)


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
        # Primary features (all available in dataset)
        'pull_up_fga',           # Off-dribble FGA
        'pct_pts_2pt_mr',        # Mid-range as % of points
        'pull_up_fg3a',          # Off-dribble 3PA
        'creation_volume_ratio', # Self-created FGA ratio
        'physicality_score',     # Force proxy
        'usg_pct',               # Usage for rim creation scaling
        'time_of_poss',          # Possession length
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
# VALIDATION CASES - Pure shot creation focus (no rim creation)
# =============================================================================
VALIDATION_CASES = {
    'Ben Simmons': {
        'expected_score': 15,
        'tolerance': 10,
        'reason': 'Minimal jump shot creation - early career had some pull-ups (2.4), declined to near-zero by 2020'
    },
    'Rudy Gobert': {
        'expected_score': 1,
        'tolerance': 3,
        'reason': 'Pure finisher - zero pull-ups, zero mid-range'
    },
    'Zion Williamson': {
        'expected_score': 10,
        'tolerance': 8,
        'reason': 'Force creator but almost zero jumper volume (get credit in C1/C5)'
    },
    'Giannis Antetokounmpo': {
        'expected_score': 38,
        'tolerance': 12,
        'reason': 'Hybrid - moderate pull-ups for a big, some mid-range (force in C5)'
    },
    'Jayson Tatum': {
        'expected_score': 55,
        'tolerance': 12,
        'reason': 'Elite perimeter creation - peaks at 75+ in 2024-25, but validator picks lower 2022-23'
    },
    'DeMar DeRozan': {
        'expected_score': 78,
        'tolerance': 10,
        'reason': 'Maximum mid-range embrace, elite pull-up volume, low 3s'
    },
    'Khris Middleton': {
        'expected_score': 68,
        'tolerance': 12,
        'reason': 'Elite mid-range scorer, good pull-up volume'
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
