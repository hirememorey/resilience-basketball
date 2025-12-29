"""
Component 5: Force Multiplication Score (Weight: 10%)

Question: Do you create things that aren't in the box score via physicality?

Physics Principle:
Force creators (Giannis, Shaq, Zion) don't need jumpers - they ARE the situation
via rim attacks, free throws, and physicality. But having physical TOOLS is not
the same as USING them.

CRITICAL INSIGHT - The "Simmons Trap":
Ben Simmons has elite physicality_score (0.93-0.98) because he's 6'11" and athletic.
But he doesn't USE this under pressure:
- Simmons leverage_usg_delta: -0.085 (HIDING when it matters)
- Giannis leverage_usg_delta: -0.01 to +0.06 (maintains/increases volume)

Having physical tools ≠ Using them. The true signal is:
1. Do you HAVE the physical tools? (physicality_score, FTr)
2. Do you USE them at volume? (usage, touch_production)
3. Do you DEMAND the ball? (leverage_usg_delta > 0 = stepping up)
4. Do you CREATE through force? (creation_volume_ratio at high usage)

Validation Cases:
- Giannis Antetokounmpo: ~95-100 (Maximum force creation)
- Zion Williamson: ~85-95 (Elite force when healthy)
- Ben Simmons: ~30-45 (Has tools, doesn't USE them under pressure)
- Stephen Curry: ~40-55 (Gravity via shooting, not force)
- Joel Embiid: ~90-100 (Post force + FT generation)

Data Analysis (from actual dataset):
- Giannis: physicality 1.0, touch_prod 5-6, usage 32-37%, leverage_usg -0.01
- Simmons: physicality 0.93, touch_prod 2-3, usage 20%, leverage_usg -0.085
- Curry: physicality 0.44, touch_prod 0.5, usage 30%, leverage_usg +0.10
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
    'physical_tools': 0.25,      # Do you have rim/FT generation ability?
    'force_volume': 0.30,        # Do you USE the tools at high volume?
    'force_agency': 0.25,        # Do you DEMAND the ball (not hide)?
    'touch_production': 0.20     # Do you produce points via touches?
}

# =============================================================================
# BENCHMARKS - Derived from data analysis
# =============================================================================
BENCHMARKS = {
    # Physicality score (already 0-1 normalized in dataset)
    'physicality_elite': 0.90,   # Giannis/Embiid level
    'physicality_avg': 0.50,     # Average player
    
    # Usage for force creators
    'usage_elite': 0.30,         # True #1 option
    'usage_role': 0.18,          # Role player
    
    # Weighted touch production (points from touches)
    'touch_production_elite': 5.0,   # Giannis level
    'touch_production_avg': 2.0,     # Average rotation player
    
    # Creation volume ratio for force (do you create or just finish?)
    'cvr_force_elite': 0.65,     # Creating, not just dunking lobs
    'cvr_force_min': 0.40,       # Below this = pure finisher (Gobert)
    
    # Leverage usage delta (pressure response)
    'leverage_stepping_up': 0.03,    # Clearly taking more responsibility
    'leverage_hiding': -0.03,        # Clearly abdicating
}


def calculate_force_multiplication_score(player_data: pd.Series) -> float:
    """
    Calculate Force Multiplication Score (0-100).
    
    This measures ability to create offense through physicality and force.
    
    Args:
        player_data: Series containing player features for a season
        
    Returns:
        Score from 0-100 where:
        - 0-25: Pure finisher or no force game (Gobert, Rudy Gay)
        - 25-45: Has tools but doesn't use them (Simmons pattern)
        - 45-65: Moderate force game (average physical player)
        - 65-85: Strong force creator (physical star)
        - 85-100: Elite force multiplication (Giannis, Embiid, Zion)
    """
    
    # Sub-metric 1: Physical Tools (25%)
    # Do you HAVE the ability to generate FTs and rim shots?
    tools_score = _calculate_physical_tools_score(player_data)
    
    # Sub-metric 2: Force Volume (30%)
    # Do you USE these tools at high volume? (usage + creation)
    volume_score = _calculate_force_volume_score(player_data)
    
    # Sub-metric 3: Force Agency (25%)
    # Do you DEMAND the ball or hide? (leverage_usg_delta + absolute usage)
    agency_score = _calculate_force_agency_score(player_data)
    
    # Sub-metric 4: Touch Production (20%)
    # How much production comes from touches? (post, paint, elbow)
    touch_score = _calculate_touch_production_score(player_data)
    
    # Weighted combination
    final_score = (
        WEIGHTS['physical_tools'] * tools_score +
        WEIGHTS['force_volume'] * volume_score +
        WEIGHTS['force_agency'] * agency_score +
        WEIGHTS['touch_production'] * touch_score
    )
    
    return round(np.clip(final_score, 0, 100), 2)


def _calculate_physical_tools_score(data: pd.Series) -> float:
    """
    Calculate score based on physical tools availability.
    
    physicality_score is already a composite of FTr (60%) + Rim Appetite (40%)
    This directly measures "can you get to the rim and line?"
    
    Benchmarks:
    - Giannis: 1.0 (maximum)
    - Simmons: 0.93-0.98 (elite - he HAS the tools)
    - Curry: 0.44 (not a force player)
    """
    physicality = data.get('physicality_score', 
                    data.get('PHYSICALITY_SCORE', 0.5))
    
    if pd.isna(physicality):
        physicality = 0.5
    
    # Handle if stored as percentage (0-100) vs decimal (0-1)
    if physicality > 1.0:
        physicality = physicality / 100.0
    
    # Scale: 0.3 → 0, 1.0 → 100
    score = (physicality - 0.30) / 0.70 * 100
    
    return np.clip(score, 0, 100)


def _calculate_force_volume_score(data: pd.Series) -> float:
    """
    Calculate score based on usage of physical tools at volume.
    
    THE SIMMONS TRAP: He has physicality 0.93+ but only 20% usage.
    Giannis has physicality 1.0 AND 32%+ usage.
    
    We combine:
    1. Usage % (do you touch the ball enough to force?)
    2. Creation Volume Ratio (do you create or just finish lobs?)
    
    Benchmarks:
    - Giannis: 32% usage, 0.65 CVR → elite force volume
    - Simmons: 20% usage, 0.56 CVR → moderate (not using tools)
    - Gobert: 14% usage, 0.25 CVR → pure finisher
    """
    usage = data.get('usg_pct', data.get('USG_PCT', 0.18))
    cvr = data.get('creation_volume_ratio', 
            data.get('CREATION_VOLUME_RATIO', 0.40))
    
    if pd.isna(usage): usage = 0.18
    if pd.isna(cvr): cvr = 0.40
    
    # Handle percentages stored as whole numbers
    if usage > 1.0: usage = usage / 100.0
    if cvr > 1.0: cvr = cvr / 100.0
    
    # Usage Score: 15% → 0, 35% → 100
    usage_score = (usage - 0.15) / 0.20 * 100
    usage_score = np.clip(usage_score, 0, 100)
    
    # Creation Score: Below 40% CVR = pure finisher, 70%+ = elite creator
    # This distinguishes Giannis (creates attacks) from Gobert (finishes lobs)
    cvr_score = (cvr - 0.35) / 0.35 * 100
    cvr_score = np.clip(cvr_score, 0, 100)
    
    # Combine: Usage (60%) + Creation (40%)
    # Usage is more important - you can't force if you don't touch it
    score = 0.60 * usage_score + 0.40 * cvr_score
    
    return np.clip(score, 0, 100)


def _calculate_force_agency_score(data: pd.Series) -> float:
    """
    Calculate score based on DEMANDING the ball vs hiding.
    
    THE KEY DIFFERENTIATOR: Simmons vs Giannis
    - Simmons: 20% usage, leverage_usg_delta = -0.085 (low base, HIDING further)
    - Giannis: 32% usage, leverage_usg_delta = -0.05 (high base, slight deferral OK)
    - Curry: 33% usage, leverage_usg_delta = +0.06 (high base, steps UP)
    
    INSIGHT: Absolute clutch usage matters more than delta for force creators.
    Giannis at 27% clutch usage (32% - 5%) is still ELITE agency.
    Simmons at 12% clutch usage (20% - 8%) is hiding.
    
    We combine:
    1. Clutch Usage Absolute (primary signal) - do you DEMAND the ball?
    2. Leverage Delta (secondary signal) - are you stepping up or hiding?
    """
    leverage_usg_delta = data.get('leverage_usg_delta',
                           data.get('LEVERAGE_USG_DELTA', 0))
    usage = data.get('usg_pct', data.get('USG_PCT', 0.20))
    clutch_usg_absolute = data.get('clutch_usg_absolute',
                            data.get('CLUTCH_USG_ABSOLUTE', None))
    
    if pd.isna(leverage_usg_delta): leverage_usg_delta = 0
    if pd.isna(usage): usage = 0.20
    if usage > 1.0: usage = usage / 100.0
    
    # Calculate clutch usage if not provided
    if clutch_usg_absolute is None or pd.isna(clutch_usg_absolute):
        clutch_usg_absolute = usage + leverage_usg_delta
    if clutch_usg_absolute > 1.0:
        clutch_usg_absolute = clutch_usg_absolute / 100.0
    
    # 1. Absolute Clutch Usage Score (60% of agency)
    # 15% clutch usage = 0, 35% clutch usage = 100
    # This is THE key signal - do you DEMAND the ball in crunch time?
    absolute_score = (clutch_usg_absolute - 0.12) / 0.23 * 100
    absolute_score = np.clip(absolute_score, 0, 100)
    
    # 2. Leverage Delta Score (40% of agency)
    # Stepping up (+) vs hiding (-)
    # -0.10 → 0, 0 → 50, +0.10 → 100
    leverage_score = (leverage_usg_delta + 0.10) / 0.20 * 100
    leverage_score = np.clip(leverage_score, 0, 100)
    
    # 3. Combine with absolute usage getting primary weight
    # High absolute + slight deferral > Low absolute + stepping up
    # Because Giannis at 27% > Simmons at 15%
    score = 0.60 * absolute_score + 0.40 * leverage_score
    
    return np.clip(score, 0, 100)


def _calculate_touch_production_score(data: pd.Series) -> float:
    """
    Calculate score based on production from touches.
    
    weighted_touch_production measures points from post, paint, elbow touches.
    This is where force creators extract value.
    
    Benchmarks:
    - Giannis: 5-6 points from touches (elite)
    - Simmons: 2-3 points from touches (moderate)
    - Curry: 0.5-1 points from touches (not a touch player)
    """
    touch_prod = data.get('weighted_touch_production',
                   data.get('WEIGHTED_TOUCH_PRODUCTION', 2.0))
    
    if pd.isna(touch_prod):
        touch_prod = 2.0
    
    # Scale: 0.5 → 0, 6.0 → 100
    score = (touch_prod - 0.5) / 5.5 * 100
    
    return np.clip(score, 0, 100)


def get_required_features() -> List[str]:
    """Return list of features required for this component."""
    return [
        'physicality_score',          # Physical tools (FTr + Rim)
        'usg_pct',                    # Volume
        'creation_volume_ratio',      # Creating vs finishing
        'leverage_usg_delta',         # Pressure response
        'weighted_touch_production'   # Touch production
    ]


def get_missing_features(df: pd.DataFrame) -> List[str]:
    """Check which required features are missing from dataset."""
    required = get_required_features()
    # Check both lower and upper case versions
    available = set(df.columns) | set(c.lower() for c in df.columns)
    missing = [f for f in required if f not in available and f.lower() not in available]
    return missing


def calculate_sub_scores(player_data: pd.Series) -> Dict[str, float]:
    """Calculate and return all sub-scores for debugging."""
    return {
        'physical_tools (25%)': round(_calculate_physical_tools_score(player_data), 2),
        'force_volume (30%)': round(_calculate_force_volume_score(player_data), 2),
        'force_agency (25%)': round(_calculate_force_agency_score(player_data), 2),
        'touch_production (20%)': round(_calculate_touch_production_score(player_data), 2),
    }


def diagnose_force_multiplication(player_data: pd.Series):
    """Prints a detailed breakdown of the force multiplication score for a player."""
    player_name = player_data.get('player_name', 'Unknown')
    season = player_data.get('season', 'N/A')
    print(f"\n{'='*60}")
    print(f"Diagnosing Force Multiplication: {player_name} ({season})")
    print(f"{'='*60}")

    # 1. Physical Tools
    physicality = player_data.get('physicality_score', 0.5)
    tools_score = _calculate_physical_tools_score(player_data)
    print(f"\n1. Physical Tools (W: 25%): {tools_score:.1f}")
    print(f"   physicality_score: {physicality:.3f}")
    if physicality >= 0.90:
        print(f"   ✅ Elite physical tools (Giannis/Embiid tier)")
    elif physicality >= 0.60:
        print(f"   → Above average physicality")
    else:
        print(f"   → Not a force player (shooter archetype)")

    # 2. Force Volume
    usage = player_data.get('usg_pct', 0.20)
    cvr = player_data.get('creation_volume_ratio', 0.50)
    volume_score = _calculate_force_volume_score(player_data)
    print(f"\n2. Force Volume (W: 30%): {volume_score:.1f}")
    print(f"   usg_pct: {usage:.1%}")
    print(f"   creation_volume_ratio: {cvr:.3f}")
    if usage >= 0.30 and cvr >= 0.60:
        print(f"   ✅ High volume force creator")
    elif usage >= 0.25:
        print(f"   → Moderate volume")
    else:
        print(f"   ⚠️  Low volume - not using physical tools")

    # 3. Force Agency
    leverage_usg_delta = player_data.get('leverage_usg_delta', 0)
    agency_score = _calculate_force_agency_score(player_data)
    print(f"\n3. Force Agency (W: 25%): {agency_score:.1f}")
    print(f"   leverage_usg_delta: {leverage_usg_delta:.3f}")
    if leverage_usg_delta > 0.03:
        print(f"   ✅ STEPS UP under pressure (demands the ball)")
    elif leverage_usg_delta < -0.05:
        print(f"   ⚠️  HIDING under pressure (Simmons pattern)")
    else:
        print(f"   → Neutral pressure response")

    # 4. Touch Production
    touch_prod = player_data.get('weighted_touch_production', 2.0)
    touch_score = _calculate_touch_production_score(player_data)
    print(f"\n4. Touch Production (W: 20%): {touch_score:.1f}")
    print(f"   weighted_touch_production: {touch_prod:.1f}")
    if touch_prod >= 5.0:
        print(f"   ✅ Elite touch production (post/paint dominant)")
    elif touch_prod >= 3.0:
        print(f"   → Good touch production")
    else:
        print(f"   → Perimeter-oriented or low volume")

    # Final Score
    final_score = calculate_force_multiplication_score(player_data)
    print(f"\n{'='*40}")
    print(f"FINAL FORCE MULTIPLICATION SCORE: {final_score:.2f}")
    print(f"{'='*40}")
    
    # Interpretation
    if final_score >= 85:
        print("→ Elite force creator (Giannis/Embiid tier)")
    elif final_score >= 65:
        print("→ Strong force game (physical star)")
    elif final_score >= 45:
        print("→ Moderate force (physical but not dominant)")
    elif final_score >= 25:
        print("→ Has tools but doesn't use them (Simmons pattern)")
    else:
        print("→ Not a force player (shooter/finisher)")


# =============================================================================
# VALIDATION CASES - Season-specific to capture patterns accurately
# =============================================================================
VALIDATION_CASES: Dict[str, Dict] = {
    'Giannis Antetokounmpo': {
        'season': '2019-20',  # Peak force year (MVP, 36% usage, STEPS UP in clutch)
        'expected_score': 93,
        'tolerance': 8,
        'reason': 'Maximum force: physicality 1.0, 36% usage, leverage +6%, elite production'
    },
    'Ben Simmons': {
        'season': '2019-20',  # Peak physical season, peak abdication
        'expected_score': 40,
        'tolerance': 12,
        'reason': 'Has tools (0.95 physicality) but HIDES (leverage_usg -0.085)'
    },
    'Stephen Curry': {
        'season': '2020-21',  # MVP-level season
        'expected_score': 50,
        'tolerance': 12,
        'reason': 'Gravity via shooting not force (0.54 physicality), but STEPS UP'
    },
    'Joel Embiid': {
        'season': '2022-23',  # MVP season
        'expected_score': 90,
        'tolerance': 10,
        'reason': 'Post force + FT machine'
    },
    'Zion Williamson': {
        'season': '2020-21',  # Healthy breakout year
        'expected_score': 85,
        'tolerance': 12,
        'reason': 'Elite physical force (when healthy)'
    },
    'Rudy Gobert': {
        'season': '2020-21',  # DPOY season
        'expected_score': 35,
        'tolerance': 12,
        'reason': 'Physical but no agency (low usage, finisher only)'
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
        
        score = calculate_force_multiplication_score(player_data)
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
        print("COMPONENT 5: FORCE MULTIPLICATION - VALIDATION")
        print("=" * 60)
        print(f"\nLoading data from {dataset_path}...")
        
        df = pd.read_csv(dataset_path)
        # Normalize column names to lower case for consistency
        df.columns = [c.lower() for c in df.columns]
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
            ('Giannis Antetokounmpo', '2020-21'),   # Elite force
            ('Ben Simmons', '2019-20'),              # Has tools, doesn't use
            ('Stephen Curry', '2020-21'),            # Gravity not force
        ]
        
        for player_name, season in diagnosis_players:
            player_mask = df['player_name'].str.lower().str.contains(
                player_name.lower().replace('ć', '.').replace('ö', '.'), 
                na=False
            )
            season_mask = df['season'] == season
            
            combined = player_mask & season_mask
            if combined.any():
                diagnose_force_multiplication(df.loc[combined].iloc[0])
            else:
                print(f"\n⚠️  Could not find {player_name} in {season}")
                
    else:
        print(f"Dataset not found at {dataset_path}")
        print("Running with synthetic test data...")
        
        # Synthetic test cases
        giannis_data = pd.Series({
            'player_name': 'Giannis Antetokounmpo',
            'season': '2020-21',
            'physicality_score': 1.0,
            'usg_pct': 0.320,
            'creation_volume_ratio': 0.668,
            'leverage_usg_delta': -0.050,
            'weighted_touch_production': 6.3,
        })
        
        simmons_data = pd.Series({
            'player_name': 'Ben Simmons',
            'season': '2019-20',
            'physicality_score': 0.947,
            'usg_pct': 0.206,
            'creation_volume_ratio': 0.560,
            'leverage_usg_delta': -0.085,
            'weighted_touch_production': 2.7,
        })
        
        curry_data = pd.Series({
            'player_name': 'Stephen Curry',
            'season': '2020-21',
            'physicality_score': 0.545,
            'usg_pct': 0.331,
            'creation_volume_ratio': 0.606,
            'leverage_usg_delta': 0.059,
            'weighted_touch_production': 0.9,
        })
        
        print("\nSynthetic Test Results:")
        print("-" * 40)
        diagnose_force_multiplication(giannis_data)
        diagnose_force_multiplication(simmons_data)
        diagnose_force_multiplication(curry_data)
