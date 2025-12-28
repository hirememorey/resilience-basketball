"""
Component 4: Defensive Attention Survival Score (Weight: 15%)

Question: When defenses scheme for you, do you survive?

Physics Principle:
Playoff defenses focus on stopping the best player. True stars find counters.
Players who collapse when schemed are "Fragile Stars" - they look good in
regular season but fail when defenses lock in.

Sub-Metrics:
- Efficiency vs Elite Defenses (40%): TS% vs top 10 / TS% vs bottom 10
- Playoff Translation (30%): Playoff TS% / Regular Season TS%
- Inverse Fragility (30%): 1 - FRAGILITY_SCORE

Validation Cases:
- Ben Simmons: ~25 (completely collapses when schemed)
- James Harden: ~85 (found counters, got better under pressure)
- Nikola Jokić: ~90 (elite playoff performer, survives everything)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


# Weights for sub-metrics
WEIGHTS = {
    'efficiency_vs_elite': 0.40,
    'playoff_translation': 0.30,
    'inverse_fragility': 0.30
}


def calculate_defensive_survival_score(player_data: pd.Series) -> float:
    """
    Calculate Defensive Attention Survival Score (0-100).
    
    Args:
        player_data: Series containing player features for a season
        
    Returns:
        Score from 0-100 where:
        - 0-25: Collapses when schemed (Simmons, Randle)
        - 25-50: Struggles under attention
        - 50-70: Maintains production
        - 70-85: Thrives under attention
        - 85-100: Elite survival (Jokić, Butler)
    """
    
    # Sub-metric 1: Efficiency vs Elite Defenses (40%)
    elite_score = _calculate_elite_defense_score(player_data)
    
    # Sub-metric 2: Playoff Translation (30%)
    playoff_score = _calculate_playoff_translation_score(player_data)
    
    # Sub-metric 3: Inverse Fragility (30%)
    fragility_score = _calculate_inverse_fragility_score(player_data)
    
    # Weighted combination
    final_score = (
        WEIGHTS['efficiency_vs_elite'] * elite_score +
        WEIGHTS['playoff_translation'] * playoff_score +
        WEIGHTS['inverse_fragility'] * fragility_score
    )
    
    return round(np.clip(final_score, 0, 100), 2)


def _calculate_elite_defense_score(data: pd.Series) -> float:
    """
    Calculate score based on performance vs elite defenses.
    
    How much does efficiency drop when facing top 10 defenses vs bottom 10?
    
    Benchmarks:
    - Fragile: >15% efficiency drop vs top defenses
    - Average: 5-10% drop
    - Resilient: <5% drop
    - Elite: Actually gets BETTER vs top defenses (film study, adjustments)
    """
    ts_vs_top = data.get('TS_PCT_vs_top10', None)
    ts_vs_bottom = data.get('TS_PCT_vs_bottom10', None)
    
    if ts_vs_top is None or ts_vs_bottom is None:
        # Fallback: use QOC_TS_DELTA if available
        qoc_delta = data.get('QOC_TS_DELTA', 0)
        # QOC_TS_DELTA = TS_vs_top - TS_vs_bottom
        # Negative = worse vs good defenses
        qoc_ratio = 1.0 + qoc_delta  # Convert delta to ratio approximation
    else:
        if ts_vs_bottom > 0:
            qoc_ratio = ts_vs_top / ts_vs_bottom
        else:
            qoc_ratio = 1.0
    
    # Scale: 0.80 ratio (20% drop) = 0, 1.10 ratio (10% better) = 100
    # 0.80 = 0, 0.90 = 33, 1.00 = 67, 1.10 = 100
    score = (qoc_ratio - 0.80) / 0.30 * 100
    return np.clip(score, 0, 100)


def _calculate_playoff_translation_score(data: pd.Series) -> float:
    """
    Calculate score based on playoff vs regular season efficiency.
    
    How well does regular season performance translate to playoffs?
    
    Benchmarks:
    - Playoff fraud: >10% efficiency drop (Randle '21)
    - Average: 3-5% drop (normal playoff grind)
    - Resilient: <3% drop
    - Playoff mode: Actually improves (Butler, Jimmy playoffs)
    """
    playoff_ts = data.get('PLAYOFF_TS_PCT', None)
    rs_ts = data.get('TS_PCT', data.get('ts_pct', 0.55))
    
    if playoff_ts is None:
        # No playoff data - use neutral score
        # Don't penalize young players who haven't had playoffs yet
        return 50.0
    
    if rs_ts > 0:
        playoff_ratio = playoff_ts / rs_ts
    else:
        playoff_ratio = 1.0
    
    # Scale: 0.85 ratio (15% drop) = 0, 1.05 ratio (5% better) = 100
    score = (playoff_ratio - 0.85) / 0.20 * 100
    return np.clip(score, 0, 100)


def _calculate_inverse_fragility_score(data: pd.Series) -> float:
    """
    Calculate score based on inverse of FRAGILITY_SCORE.
    
    FRAGILITY_SCORE captures abdication + choke patterns:
    - Abdication: Usage drops under pressure (Simmons)
    - Choking: Efficiency drops under pressure (KAT)
    
    Higher fragility = lower survival score.
    """
    fragility = data.get('FRAGILITY_SCORE', data.get('fragility_score', 0.5))
    
    # Inverse: Low fragility = high survival
    # Fragility 0.0 → 100 (completely robust)
    # Fragility 0.5 → 50 (average)
    # Fragility 1.0 → 0 (completely fragile)
    score = (1.0 - fragility) * 100
    return np.clip(score, 0, 100)


def get_required_features() -> List[str]:
    """Return list of features required for this component."""
    return [
        # Performance vs defense quality
        'TS_PCT_vs_top10',
        'TS_PCT_vs_bottom10',
        'QOC_TS_DELTA',
        # Playoff translation
        'PLAYOFF_TS_PCT',
        'TS_PCT',
        # Fragility
        'FRAGILITY_SCORE',
    ]


def get_missing_features(df: pd.DataFrame) -> List[str]:
    """Check which required features are missing from dataset."""
    required = get_required_features()
    missing = [f for f in required if f not in df.columns and f.lower() not in df.columns]
    return missing


# Validation test cases from SPECIFICATION.md
VALIDATION_CASES = {
    'Ben Simmons': {
        'expected_score': 25,
        'tolerance': 15,
        'reason': 'Completely collapses when defenses scheme for him'
    },
    'James Harden': {
        'expected_score': 85,
        'tolerance': 10,
        'reason': 'Found counters to defenses, got better under pressure'
    },
    'Nikola Jokić': {
        'expected_score': 90,
        'tolerance': 10,
        'reason': 'Elite playoff performer, survives all schemes'
    },
    'Jimmy Butler': {
        'expected_score': 88,
        'tolerance': 10,
        'reason': 'Famous for playoff mode activation'
    },
    'Julius Randle': {
        'expected_score': 30,
        'tolerance': 15,
        'reason': 'All-NBA RS, disaster in 2021 playoffs'
    },
}


def validate_component(df: pd.DataFrame) -> Dict[str, dict]:
    """
    Validate component against known test cases.
    
    Returns:
        Dict mapping player names to pass/fail results
    """
    results = {}
    
    for player, case in VALIDATION_CASES.items():
        player_mask = df['player_name'].str.lower().str.contains(player.lower())
        
        if not player_mask.any():
            results[player] = {
                'status': 'SKIP',
                'reason': 'Player not in dataset'
            }
            continue
        
        # Get most recent season
        player_df = df[player_mask].sort_values('season', ascending=False)
        player_data = player_df.iloc[0]
        
        score = calculate_defensive_survival_score(player_data)
        expected = case['expected_score']
        tolerance = case['tolerance']
        
        if abs(score - expected) <= tolerance:
            results[player] = {
                'status': 'PASS',
                'score': score,
                'expected': expected
            }
        else:
            results[player] = {
                'status': 'FAIL',
                'score': score,
                'expected': expected,
                'delta': score - expected
            }
    
    return results


if __name__ == '__main__':
    # Quick test with synthetic data
    
    # Test case 1: Simmons pattern (fragile)
    simmons_data = pd.Series({
        'QOC_TS_DELTA': -0.08,       # 8% worse vs good defenses
        'PLAYOFF_TS_PCT': 0.50,      # Poor playoffs
        'TS_PCT': 0.58,              # Good regular season
        'FRAGILITY_SCORE': 0.85,     # Very fragile
    })
    
    # Test case 2: Jokic pattern (survives everything)
    jokic_data = pd.Series({
        'QOC_TS_DELTA': 0.02,        # Actually better vs good defenses
        'PLAYOFF_TS_PCT': 0.62,      # Elite playoffs
        'TS_PCT': 0.60,              # Even better in playoffs
        'FRAGILITY_SCORE': 0.15,     # Very robust
    })
    
    simmons_score = calculate_defensive_survival_score(simmons_data)
    jokic_score = calculate_defensive_survival_score(jokic_data)
    
    print(f"Simmons Score: {simmons_score} (expected ~25)")
    print(f"Jokić Score: {jokic_score} (expected ~90)")
    print(f"Gap: {jokic_score - simmons_score} (should be large)")

