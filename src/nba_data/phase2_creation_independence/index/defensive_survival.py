"""
Component 4: Defensive Attention Survival Score (Weight: 15%)

Question: When defenses scheme for you, do you survive?

Physics Principle:
When playoff defenses game-plan against you, TRUE survivors find counters.
FRAGILE stars collapse (Simmons 2021, KAT in playoffs).

CRITICAL INSIGHT - The Abdication Efficiency Trap:
Ben Simmons maintains positive leverage_ts_delta (+0.04 to +0.09) because 
when he HIDES, he only takes his best shots (uncontested layups).
His efficiency is maintained through VOLUME ABDICATION, not skill.

The TRUE signal for survival is:
1. MAINTAIN VOLUME under pressure (don't hide)
2. Have MULTIPLE scoring modes (can't be schemed if versatile)
3. Find COUNTERS when Plan A is taken away

Validation Cases:
- Ben Simmons: ~20-30 (abdicates volume, one-dimensional)
- James Harden: ~80-90 (steps UP under pressure, many modes)
- Nikola Jokić: ~85-95 (infinite options, anti-schemable)
- KAT: ~35-45 (usage/efficiency both drop under pressure)

Data Analysis (from actual dataset):
- Simmons leverage_usg_delta: -0.034 → -0.085 (DECREASING - hiding)
- Harden leverage_usg_delta: +0.077 → +0.097 (INCREASING - stepping up)
- Simmons pull_up_fga: 2.4 → 0.7 (ONE option, declining)
- Harden pull_up_fga: 8.9 → 13.7 (MANY options, elite)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# WEIGHTS - Based on first principles analysis
# =============================================================================
WEIGHTS = {
    'clutch_volume_maintenance': 0.35,   # Do you maintain/increase usage under pressure?
    'shot_versatility': 0.30,            # Can you be schemed? (Multiple modes = no)
    'efficiency_resilience': 0.25,       # How well does efficiency hold?
    'fragility_inverse': 0.10            # Supporting signal from existing fragility
}

# =============================================================================
# BENCHMARKS - Derived from data analysis
# =============================================================================
BENCHMARKS = {
    # leverage_usg_delta ranges
    'usg_delta_floor': -0.15,    # Severe hiding (worst abdicators)
    'usg_delta_neutral': 0.0,    # No change
    'usg_delta_ceiling': 0.15,   # Stepping up significantly
    
    # Shot versatility thresholds
    'pullup_fga_elite': 8.0,      # Elite pull-up creators
    'pullup_3_elite': 5.0,        # Elite off-dribble 3 shooters
    'midrange_elite': 0.15,       # Significant mid-range game (15%+ of points)
    
    # Efficiency delta thresholds
    'ts_delta_floor': -0.15,      # Severe efficiency collapse
    'ts_delta_neutral': 0.0,
    'ts_delta_ceiling': 0.10,     # Actually better under pressure (rare)
}


def calculate_defensive_survival_score(player_data: pd.Series) -> float:
    """
    Calculate Defensive Attention Survival Score (0-100).
    
    This measures ability to maintain production when defenses scheme.
    
    Args:
        player_data: Series containing player features for a season
        
    Returns:
        Score from 0-100 where:
        - 0-25: Collapses under schematic pressure (Fragile Stars)
        - 25-50: Limited options, vulnerable to schemes
        - 50-70: Adequate options, can survive some attention
        - 70-85: Multiple modes, hard to scheme
        - 85-100: Anti-schemable (Harden, Jokić, Luka)
    """
    
    # Sub-metric 1: Clutch Volume Maintenance (35%)
    # Do you STAY in the game or hide when it matters?
    volume_score = _calculate_clutch_volume_score(player_data)
    
    # Sub-metric 2: Shot Versatility (30%)
    # Multiple modes = harder to scheme against
    versatility_score = _calculate_shot_versatility_score(player_data)
    
    # Sub-metric 3: Efficiency Resilience (25%)
    # How well does efficiency hold under pressure?
    # But ONLY matters if you're also maintaining volume!
    efficiency_score = _calculate_efficiency_resilience_score(player_data)
    
    # Sub-metric 4: Fragility Inverse (10%)
    # Supporting signal from existing fragility calculation
    fragility_inverse = _calculate_fragility_inverse_score(player_data)
    
    # Weighted combination
    final_score = (
        WEIGHTS['clutch_volume_maintenance'] * volume_score +
        WEIGHTS['shot_versatility'] * versatility_score +
        WEIGHTS['efficiency_resilience'] * efficiency_score +
        WEIGHTS['fragility_inverse'] * fragility_inverse
    )
    
    return round(np.clip(final_score, 0, 100), 2)


def _calculate_clutch_volume_score(data: pd.Series) -> float:
    """
    Calculate score based on usage maintenance under pressure.
    
    THE KEY SIGNAL: Do you maintain/increase volume when it matters?
    
    Benchmarks (from actual data):
    - Simmons: -0.085 (severe hiding) → Score ~10-20
    - Harden: +0.097 (stepping up) → Score ~90+
    - KAT: -0.081 (hiding) → Score ~15
    - Giannis: -0.026 (slight deferral, acceptable) → Score ~60
    
    The physics: Abdicating volume is a FAILURE of resilience, even if
    efficiency is maintained. You can't scheme against someone who hides,
    but hiding means you're not a #1 option.
    """
    leverage_usg_delta = data.get('leverage_usg_delta', 
                           data.get('LEVERAGE_USG_DELTA', 0))
    
    if pd.isna(leverage_usg_delta):
        leverage_usg_delta = 0
    
    # Scale: 
    # -0.15 (severe hiding) → 0
    # 0.00 (neutral) → 50
    # +0.15 (stepping up) → 100
    floor = BENCHMARKS['usg_delta_floor']
    ceiling = BENCHMARKS['usg_delta_ceiling']
    
    score = (leverage_usg_delta - floor) / (ceiling - floor) * 100
    
    return np.clip(score, 0, 100)


def _calculate_shot_versatility_score(data: pd.Series) -> float:
    """
    Calculate score based on variety of scoring modes.
    
    Players with multiple options are HARDER TO SCHEME:
    - Simmons: Rim only (1 mode) → easy to scheme (hack-a-Simmons)
    - Harden: Stepback, drive, floater, lob (4+ modes) → impossible to scheme
    - Jokić: Post, 3pt, any pass angle (∞ modes) → literally anti-schemable
    
    We measure this through:
    1. Pull-up FGA (off-dribble jumpers = more modes)
    2. Pull-up 3PA (range = more modes)
    3. Mid-range % (dying art = valuable counter)
    4. Creation volume ratio (high creation = many options)
    """
    # 1. Pull-up FGA (Weight: 35%)
    pullup_fga = data.get('pull_up_fga', 0)
    if pd.isna(pullup_fga): pullup_fga = 0
    pullup_score = min(pullup_fga / BENCHMARKS['pullup_fga_elite'] * 100, 100)
    
    # 2. Pull-up 3PA (Weight: 25%)
    pullup_3a = data.get('pull_up_fg3a', 0)
    if pd.isna(pullup_3a): pullup_3a = 0
    pullup_3_score = min(pullup_3a / BENCHMARKS['pullup_3_elite'] * 100, 100)
    
    # 3. Mid-range % of points (Weight: 20%)
    midrange_pct = data.get('pct_pts_2pt_mr', 0)
    if pd.isna(midrange_pct): midrange_pct = 0
    midrange_score = min(midrange_pct / BENCHMARKS['midrange_elite'] * 100, 100)
    
    # 4. Creation Volume Ratio (Weight: 20%)
    # High creation = many ways to score
    cvr = data.get('creation_volume_ratio', 0)
    if pd.isna(cvr): cvr = 0
    creation_score = min(cvr / 0.70 * 100, 100)  # 70% creation = max
    
    # Weighted combination
    score = (
        0.35 * pullup_score +
        0.25 * pullup_3_score +
        0.20 * midrange_score +
        0.20 * creation_score
    )
    
    return np.clip(score, 0, 100)


def _calculate_efficiency_resilience_score(data: pd.Series) -> float:
    """
    Calculate score based on efficiency maintenance under pressure.
    
    CRITICAL INSIGHT: This only matters if you're ALSO maintaining volume.
    The "Abdication Efficiency Trap" shows that you can maintain TS% by 
    just stopping shooting - that's NOT survival.
    
    We weight efficiency resilience BY volume maintenance:
    - If usage drops significantly, efficiency score is penalized
    - If usage maintains/rises, efficiency score counts fully
    
    Benchmarks:
    - Simmons: TS delta +0.04, but USG delta -0.08 → Fake efficiency
    - Harden: TS delta -0.05, but USG delta +0.10 → Real resilience
    - KAT: TS delta -0.13, USG delta -0.08 → Double collapse
    """
    leverage_ts_delta = data.get('leverage_ts_delta', 
                          data.get('LEVERAGE_TS_DELTA', 0))
    leverage_usg_delta = data.get('leverage_usg_delta',
                           data.get('LEVERAGE_USG_DELTA', 0))
    
    if pd.isna(leverage_ts_delta): leverage_ts_delta = 0
    if pd.isna(leverage_usg_delta): leverage_usg_delta = 0
    
    # Base efficiency score
    # Scale: -0.15 → 0, 0 → 60, +0.10 → 100
    floor = BENCHMARKS['ts_delta_floor']
    ceiling = BENCHMARKS['ts_delta_ceiling']
    base_score = (leverage_ts_delta - floor) / (ceiling - floor) * 100
    base_score = np.clip(base_score, 0, 100)
    
    # Volume-adjusted multiplier
    # If you're hiding (negative usg delta), efficiency score is discounted
    # If you're stepping up (positive usg delta), efficiency score counts fully
    # Range: 0.5 (hiding) to 1.0 (stepping up)
    if leverage_usg_delta >= 0:
        volume_multiplier = 1.0
    else:
        # Negative usage delta = hiding
        # -0.15 → 0.5 multiplier
        # 0 → 1.0 multiplier
        volume_multiplier = max(0.5, 1.0 + (leverage_usg_delta / 0.30))
    
    adjusted_score = base_score * volume_multiplier
    
    return np.clip(adjusted_score, 0, 100)


def _calculate_fragility_inverse_score(data: pd.Series) -> float:
    """
    Calculate inverse of existing fragility score.
    
    The fragility score (0-1) captures abdication + choke patterns.
    We invert it: Low fragility = High survival.
    
    This is a supporting signal (10% weight) to incorporate existing
    calculations, not primary driver.
    """
    fragility = data.get('fragility_score', 
                  data.get('FRAGILITY_SCORE', 0.5))
    
    if pd.isna(fragility):
        fragility = 0.5  # Neutral default
    
    # Handle if it's stored as percentage (0-100) vs decimal (0-1)
    if fragility > 1.0:
        fragility = fragility / 100.0
    
    # Invert: 0 fragility = 100 score, 1 fragility = 0 score
    score = (1.0 - fragility) * 100
    
    return np.clip(score, 0, 100)


def get_required_features() -> List[str]:
    """Return list of features required for this component."""
    return [
        'leverage_usg_delta',      # Clutch usage change
        'leverage_ts_delta',       # Clutch efficiency change
        'pull_up_fga',             # Pull-up volume
        'pull_up_fg3a',            # Pull-up 3 volume
        'pct_pts_2pt_mr',          # Mid-range %
        'creation_volume_ratio',   # Creation rate
        'fragility_score'          # Existing fragility
    ]


def get_missing_features(df: pd.DataFrame) -> List[str]:
    """Check which required features are missing from dataset."""
    required = get_required_features()
    available = set(df.columns) | set(c.lower() for c in df.columns)
    missing = [f for f in required if f not in available and f.lower() not in available]
    return missing


def calculate_sub_scores(player_data: pd.Series) -> Dict[str, float]:
    """Calculate and return all sub-scores for debugging."""
    return {
        'clutch_volume (35%)': round(_calculate_clutch_volume_score(player_data), 2),
        'shot_versatility (30%)': round(_calculate_shot_versatility_score(player_data), 2),
        'efficiency_resilience (25%)': round(_calculate_efficiency_resilience_score(player_data), 2),
        'fragility_inverse (10%)': round(_calculate_fragility_inverse_score(player_data), 2),
    }


def diagnose_defensive_survival(player_data: pd.Series):
    """Prints a detailed breakdown of the defensive survival score for a player."""
    player_name = player_data.get('player_name', 'Unknown')
    season = player_data.get('season', 'N/A')
    print(f"\n{'='*60}")
    print(f"Diagnosing Defensive Survival: {player_name} ({season})")
    print(f"{'='*60}")

    # 1. Clutch Volume Maintenance
    leverage_usg_delta = player_data.get('leverage_usg_delta', 0)
    volume_score = _calculate_clutch_volume_score(player_data)
    print(f"\n1. Clutch Volume Maintenance (W: 35%): {volume_score:.1f}")
    print(f"   leverage_usg_delta: {leverage_usg_delta:.3f}")
    if leverage_usg_delta < -0.05:
        print(f"   ⚠️  HIDING under pressure (abdication pattern)")
    elif leverage_usg_delta > 0.05:
        print(f"   ✅ STEPPING UP under pressure (engine pattern)")
    else:
        print(f"   → Neutral usage change")

    # 2. Shot Versatility
    pullup_fga = player_data.get('pull_up_fga', 0)
    pullup_3a = player_data.get('pull_up_fg3a', 0)
    midrange_pct = player_data.get('pct_pts_2pt_mr', 0)
    cvr = player_data.get('creation_volume_ratio', 0)
    versatility_score = _calculate_shot_versatility_score(player_data)
    print(f"\n2. Shot Versatility (W: 30%): {versatility_score:.1f}")
    print(f"   pull_up_fga: {pullup_fga:.1f} (benchmark: 8.0)")
    print(f"   pull_up_fg3a: {pullup_3a:.1f} (benchmark: 5.0)")
    print(f"   pct_pts_2pt_mr: {midrange_pct:.3f} (benchmark: 0.15)")
    print(f"   creation_volume_ratio: {cvr:.3f} (benchmark: 0.70)")
    
    # Mode count estimate
    modes = 0
    if pullup_fga >= 2.0: modes += 1  # Has pull-up game
    if pullup_3a >= 1.0: modes += 1   # Has range
    if midrange_pct >= 0.05: modes += 1  # Has mid-range
    if cvr >= 0.50: modes += 1  # High creation
    print(f"   Estimated scoring modes: {modes}/4")

    # 3. Efficiency Resilience
    leverage_ts_delta = player_data.get('leverage_ts_delta', 0)
    efficiency_score = _calculate_efficiency_resilience_score(player_data)
    print(f"\n3. Efficiency Resilience (W: 25%): {efficiency_score:.1f}")
    print(f"   leverage_ts_delta: {leverage_ts_delta:.3f}")
    if leverage_usg_delta < -0.03:
        print(f"   ⚠️  Volume-adjusted (hiding → efficiency discounted)")
    else:
        print(f"   → Efficiency counts fully (volume maintained)")

    # 4. Fragility Inverse
    fragility = player_data.get('fragility_score', 0.5)
    fragility_score = _calculate_fragility_inverse_score(player_data)
    print(f"\n4. Fragility Inverse (W: 10%): {fragility_score:.1f}")
    print(f"   fragility_score: {fragility:.3f}")

    # Final Score
    final_score = calculate_defensive_survival_score(player_data)
    print(f"\n{'='*40}")
    print(f"FINAL DEFENSIVE SURVIVAL SCORE: {final_score:.2f}")
    print(f"{'='*40}")
    
    # Interpretation
    if final_score >= 85:
        print("→ Anti-schemable (Franchise Engine territory)")
    elif final_score >= 70:
        print("→ Hard to scheme (Strong Creator)")
    elif final_score >= 50:
        print("→ Adequate survival (role-dependent)")
    elif final_score >= 25:
        print("→ Vulnerable to schemes (Fragile Star)")
    else:
        print("→ Collapses under attention (Not a viable #1)")


# =============================================================================
# VALIDATION CASES - Season-specific to capture patterns accurately
# =============================================================================
VALIDATION_CASES: Dict[str, Dict] = {
    'Ben Simmons': {
        'season': '2019-20',  # Peak abdication pattern
        'expected_score': 32,
        'tolerance': 12,
        'reason': 'One-dimensional (rim only), severe abdication (-0.085 LUD)'
    },
    'James Harden': {
        'season': '2018-19',  # Peak engine year
        'expected_score': 78,
        'tolerance': 12,
        'reason': 'Maximum versatility (13.7 pullup FGA), steps UP (+0.096 LUD)'
    },
    'Nikola Jokić': {
        'season': '2021-22',  # MVP season
        'expected_score': 55,
        'tolerance': 15,
        'reason': 'Steps UP massively (+0.114 LUD) but low shot versatility (hub archetype)'
    },
    'Luka Dončić': {
        'season': '2020-21',  # Best clutch engagement
        'expected_score': 70,
        'tolerance': 15,
        'reason': 'Elite versatility (11.7 pullup FGA), slight step-up (+0.014 LUD)'
    },
    'Karl-Anthony Towns': {
        'season': '2017-18',  # Most fragile season
        'expected_score': 22,
        'tolerance': 12,
        'reason': 'Double collapse: efficiency (-0.132 LTD) AND volume (-0.081 LUD)'
    },
    'Giannis Antetokounmpo': {
        'season': '2020-21',  # Championship season
        'expected_score': 55,
        'tolerance': 15,
        'reason': 'Force creator, moderate pull-ups, some clutch deferral'
    },
}


def validate_component(df: pd.DataFrame, verbose: bool = True) -> Dict[str, dict]:
    """
    Validate component against known test cases.
    
    Uses season-specific validation to capture patterns accurately.
    Each player has a designated season that best exemplifies their pattern.
    
    Args:
        df: DataFrame with player data
        verbose: If True, print detailed results
        
    Returns:
        Dict mapping player names to pass/fail results
    """
    results = {}
    
    for player, case in VALIDATION_CASES.items():
        # Fuzzy match for player name (handles accents)
        player_mask = df['player_name'].str.lower().str.contains(
            player.lower().replace('ć', '.').replace('ö', '.'), 
            na=False
        )
        
        if not player_mask.any():
            results[player] = {
                'status': 'SKIP',
                'reason': 'Player not in dataset'
            }
            if verbose:
                print(f"⚠️  SKIP: {player} - not in dataset")
            continue
        
        player_df = df[player_mask]
        
        # Use specified season if available, otherwise fall back to highest usage
        target_season = case.get('season')
        if target_season and (player_df['season'] == target_season).any():
            player_data = player_df[player_df['season'] == target_season].iloc[0]
            season = target_season
        else:
            # Fallback to highest usage season
            player_data = player_df.sort_values('usg_pct', ascending=False).iloc[0]
            season = player_data.get('season', 'unknown')
            if verbose and target_season:
                print(f"   (Note: {target_season} not found, using {season})")
        
        score = calculate_defensive_survival_score(player_data)
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
    from pathlib import Path
    
    # Load actual dataset
    results_dir = Path(__file__).parents[4] / 'results'
    dataset_path = results_dir / 'predictive_dataset_with_friction.csv'
    
    if dataset_path.exists():
        print("=" * 60)
        print("COMPONENT 4: DEFENSIVE SURVIVAL - VALIDATION")
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
        
        # Detailed diagnosis for key players
        print("\n" + "=" * 60)
        print("DETAILED DIAGNOSIS")
        print("=" * 60)
        
        diagnosis_players = [
            ('Ben Simmons', '2019-20'),   # Peak abdication
            ('James Harden', '2018-19'),  # Peak engine
            ('Karl-Anthony Towns', '2017-18'),  # Known fragile
        ]
        
        for player_name, season in diagnosis_players:
            player_mask = df['player_name'].str.lower().str.contains(
                player_name.lower().replace('ć', '.').replace('ö', '.'), 
                na=False
            )
            season_mask = df['season'] == season
            
            combined = player_mask & season_mask
            if combined.any():
                diagnose_defensive_survival(df.loc[combined].iloc[0])
            else:
                print(f"\n⚠️  Could not find {player_name} in {season}")
                
    else:
        print(f"Dataset not found at {dataset_path}")
        print("Running with synthetic test data...")
        
        # Synthetic test cases
        simmons_data = pd.Series({
            'player_name': 'Ben Simmons',
            'season': '2019-20',
            'leverage_usg_delta': -0.085,
            'leverage_ts_delta': 0.043,
            'pull_up_fga': 0.7,
            'pull_up_fg3a': 0.1,
            'pct_pts_2pt_mr': 0.009,
            'creation_volume_ratio': 0.56,
            'fragility_score': 0.50,
        })
        
        harden_data = pd.Series({
            'player_name': 'James Harden',
            'season': '2018-19',
            'leverage_usg_delta': 0.096,
            'leverage_ts_delta': -0.003,
            'pull_up_fga': 13.7,
            'pull_up_fg3a': 12.1,
            'pct_pts_2pt_mr': 0.024,
            'creation_volume_ratio': 0.87,
            'fragility_score': 0.079,
        })
        
        print("\nSynthetic Test Results:")
        print("-" * 40)
        diagnose_defensive_survival(simmons_data)
        diagnose_defensive_survival(harden_data)
