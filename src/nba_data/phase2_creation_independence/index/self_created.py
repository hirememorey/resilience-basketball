"""
Component 1: Self-Created Shot Score (Weight: 30%)

Question: Can you generate a quality shot without a play being run?

Physics Principle:
A player who can create their own shot is not dependent on the system.
This is the difference between "IS the situation" vs "NEEDS the situation."

TWO VALID PATHS TO SELF-CREATION:
1. Perimeter Creation (Harden, Luka): Pull-ups, ISO, stepback 3s
2. Hub Creation (Jokić): Post orchestration, elite touch efficiency, playmaking gravity

Both answer "Can you create when schemed?" - just in different ways.
The component takes the MAXIMUM of these two paths.

Sub-Metrics (Perimeter Path):
- Unassisted FG% (25%): What % of made shots are unassisted?
- ISO + Pull-up Volume (30%): How often does the player create?
- Self-Created Efficiency (30%): How efficient are self-created shots?
- Creation Tools (15%): Does the player have stepback, fadeaway, etc.?

Hub Creation Bonus:
- Elite touch production (10+ points from touches) 
- Elite efficiency at volume (65%+ TS)
- Positive pressure response (leverage_usg_delta > 0)

The hub path requires ALL THREE to activate - this prevents Sabonis
(who has good touch production but HIDES under pressure) from benefiting.

Validation Cases:
- Ben Simmons: ~5 (near zero self-created jumpers, no hub creation)
- James Harden: ~95 (elite perimeter creation)
- Luka Dončić: ~95 (elite perimeter creation)
- Nikola Jokić: ~85+ (elite hub creation - 10.5 touch prod, 70% TS, steps UP)
- Domantas Sabonis: ~25-35 (good touch but HIDES under pressure)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Weights for sub-metrics (Perimeter Path)
WEIGHTS = {
    'unassisted_rate': 0.25,
    'creation_volume': 0.30,
    'self_created_efficiency': 0.30,
    'creation_tools': 0.15
}

# Thresholds for Hub Creation Path
HUB_THRESHOLDS = {
    'touch_production_elite': 8.0,     # 8+ points from touches = elite
    'touch_production_max': 12.0,      # For scaling
    'ts_elite': 0.62,                  # 62%+ TS = elite efficiency
    'ts_max': 0.72,                    # For scaling
    'leverage_threshold': 0.0,         # Must be non-negative (not hiding)
    'leverage_bonus': 0.05,            # Stepping up significantly
    'usage_threshold': 0.24,           # Must have significant usage to qualify
}


def calculate_self_created_score(player_data: pd.Series) -> float:
    """
    Calculate Self-Created Shot Score (0-100).
    
    Uses TWO PATHS and takes the maximum:
    1. Perimeter Path: Pull-ups, ISO, unassisted jumpers (Harden, Luka)
    2. Hub Path: Touch production + efficiency + pressure response (Jokić)
    
    Args:
        player_data: Series containing player features for a season
        
    Returns:
        Score from 0-100 where:
        - 0-20: No self-creation (Simmons)
        - 20-50: Limited creation (role players)
        - 50-70: Moderate creation (secondary creators)
        - 70-90: High creation (primary options)
        - 90-100: Elite creation (Harden, Luka, Jokić)
    """
    
    # PATH 1: Perimeter Creation (existing logic)
    perimeter_score = _calculate_perimeter_path_score(player_data)
    
    # PATH 2: Hub Creation (new - for Jokić-type creators)
    hub_score = _calculate_hub_creation_score(player_data)
    
    # Take the MAXIMUM of both paths
    # This allows players to excel via either perimeter OR hub creation
    final_score = max(perimeter_score, hub_score)
    
    return round(np.clip(final_score, 0, 100), 2)


def _calculate_perimeter_path_score(player_data: pd.Series) -> float:
    """
    Calculate perimeter creation score (original logic).
    
    For guards/wings who create via pull-ups, ISO, stepbacks.
    """
    # Sub-metric 1: Unassisted FG Rate (25%)
    unassisted_score = _calculate_unassisted_score(player_data)
    
    # Sub-metric 2: ISO + Pull-up Volume (30%)
    volume_score = _calculate_creation_volume_score(player_data)
    
    # Sub-metric 3: Self-Created Efficiency (30%)
    efficiency_score = _calculate_self_created_efficiency_score(player_data)
    
    # Sub-metric 4: Creation Tools Availability (15%)
    tools_score = _calculate_creation_tools_score(player_data)
    
    # Weighted combination
    score = (
        WEIGHTS['unassisted_rate'] * unassisted_score +
        WEIGHTS['creation_volume'] * volume_score +
        WEIGHTS['self_created_efficiency'] * efficiency_score +
        WEIGHTS['creation_tools'] * tools_score
    )
    
    return np.clip(score, 0, 100)


def _calculate_hub_creation_score(player_data: pd.Series) -> float:
    """
    Calculate hub creation score for post-centric orchestrators.
    
    For bigs who create via post touches, playmaking gravity, and efficiency.
    Examples: Jokić, prime Shaq, Hakeem
    
    REQUIRES ALL THREE to activate (multiplicative, not additive):
    1. Elite touch production (8+ points from touches)
    2. Elite efficiency (62%+ TS at significant usage)
    3. Non-hiding pressure response (leverage_usg_delta >= 0)
    
    This prevents Sabonis (good touches but HIDES) from benefiting.
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
    # This is the key differentiator between Jokić and Sabonis
    if leverage_usg < HUB_THRESHOLDS['leverage_threshold']:
        # Negative leverage = hiding = not a hub creator, just a finisher
        return 0.0
    
    # GATE 3: Must have elite touch production
    if touch_prod < HUB_THRESHOLDS['touch_production_elite']:
        return 0.0
    
    # GATE 4: Must have elite efficiency
    if ts_pct < HUB_THRESHOLDS['ts_elite']:
        return 0.0
    
    # All gates passed - calculate score
    
    # Touch production score (8 → 60, 12+ → 100)
    touch_score = (touch_prod - HUB_THRESHOLDS['touch_production_elite']) / \
                  (HUB_THRESHOLDS['touch_production_max'] - HUB_THRESHOLDS['touch_production_elite'])
    touch_score = 60 + (touch_score * 40)  # 60-100 range
    touch_score = np.clip(touch_score, 60, 100)
    
    # Efficiency score (62% → 70, 72%+ → 100)
    eff_score = (ts_pct - HUB_THRESHOLDS['ts_elite']) / \
                (HUB_THRESHOLDS['ts_max'] - HUB_THRESHOLDS['ts_elite'])
    eff_score = 70 + (eff_score * 30)  # 70-100 range
    eff_score = np.clip(eff_score, 70, 100)
    
    # Pressure bonus (stepping UP = bonus)
    if leverage_usg >= HUB_THRESHOLDS['leverage_bonus']:
        pressure_multiplier = 1.1  # 10% bonus for stepping up
    else:
        pressure_multiplier = 1.0  # No penalty, just no bonus
    
    # Combined score (average of touch and efficiency, with pressure bonus)
    base_score = (touch_score * 0.5 + eff_score * 0.5) * pressure_multiplier
    
    return np.clip(base_score, 0, 100)


def _calculate_unassisted_score(data: pd.Series) -> float:
    """
    Calculate score based on unassisted field goal rate.
    
    Higher unassisted rate = more self-created scoring.
    
    Benchmarks:
    - Simmons: ~0.20-0.30 (mostly assisted on dunks)
    - Average: ~0.50
    - Harden/Luka: ~0.80+ (creates most of his own)
    """
    # Primary Source: pct_uast_fgm (0.0 - 1.0)
    # Available in predictive_dataset_with_friction.csv
    unassisted_rate = data.get('pct_uast_fgm', None)
    
    # Fallback keys just in case
    if unassisted_rate is None:
        unassisted_rate = data.get('PCT_UAST_FGM', None)

    if unassisted_rate is None:
        # Fallback: estimate from creation_volume_ratio
        # If 50% of shots are self-created, roughly 50% are unassisted
        cvr = data.get('creation_volume_ratio', 0.5)
        unassisted_rate = 0.20 + (cvr * 0.60)  # Map 0->0.20, 1->0.80

    # Handle percentage vs decimal
    if unassisted_rate > 1.0:
        unassisted_rate = unassisted_rate / 100.0
        
    # Scale: 
    # 0.20 (20%) -> 0 score
    # 0.85 (85%) -> 100 score
    score = (unassisted_rate - 0.20) / 0.65 * 100
    return np.clip(score, 0, 100)


def _calculate_creation_volume_score(data: pd.Series) -> float:
    """
    Calculate score based on ISO and pull-up volume.
    
    Measures how often the player is asked/chooses to create.
    
    Benchmarks:
    - Role player: <2 pull-ups/game
    - Primary creator: 6-8 pull-ups/game
    - Elite heliocentric: 10+ pull-ups/game
    """
    # 1. Pull-up FGA (Best proxy for creation volume currently available)
    pull_up_fga = data.get('pull_up_fga', 0)
    
    # 2. Time of Possession (Secondary indicator of on-ball load)
    time_of_poss = data.get('time_of_poss', 0)
    
    # 3. Creation Volume Ratio (Rate stat)
    # This is (ISO + Pull-ups) / Total FGA
    cvr = data.get('creation_volume_ratio', 0)
    
    # Composite Volume Metric
    # We want absolute volume, but weighted by the rate (to penalize "fake" volume if any)
    # Pull-ups are the gold standard for self-creation.
    
    # Score based on Pull-up FGA:
    # 0 -> 0
    # 2 -> 25
    # 5 -> 60
    # 10+ -> 100
    
    # Linear interpolation
    # Min: 0.5 (generous floor), Max: 10.0 (Elite)
    volume_score = (pull_up_fga - 0.5) / 9.5 * 100
    
    # Boost if high Time of Possession (indicates ISOs that might not end in pull-ups, e.g. drives)
    if time_of_poss > 6.0: # Harden/Luka level
        volume_score *= 1.1
        
    return np.clip(volume_score, 0, 100)


def _calculate_self_created_efficiency_score(data: pd.Series) -> float:
    """
    Calculate score based on efficiency on self-created shots.
    
    Measures ability to score EFFICIENTLY when creating.
    
    Benchmarks:
    - Poor: <50% TS
    - Average: 55% TS
    - Elite: 60%+ TS on high volume
    """
    # Ideally: EFG_ISO_WEIGHTED (dropped in current pipeline)
    # Proxy: TS_PCT adjusted by Creation Volume
    
    ts_pct = data.get('ts_pct', 0.55)
    
    # Handle percentage vs decimal
    if ts_pct > 1.0:
        ts_pct = ts_pct / 100.0
        
    # We need to distinguish "Efficient because dunks" vs "Efficient creator"
    # High Unassisted Rate + High Efficiency = Elite Creator
    # Low Unassisted Rate + High Efficiency = Finisher (Gobert)
    
    unassisted_rate = data.get('pct_uast_fgm', data.get('creation_volume_ratio', 0.5))
    if unassisted_rate > 1.0: unassisted_rate /= 100.0
    
    # If unassisted rate is low (<30%), their efficiency is likely NOT self-created.
    # We penalize the efficiency score for low unassisted rate.
    relevance_factor = np.clip((unassisted_rate - 0.2) / 0.4, 0, 1) # 0.2->0, 0.6->1
    
    # Baseline Score (50% TS = 0, 62% TS = 100)
    base_score = (ts_pct - 0.50) / 0.12 * 100
    base_score = np.clip(base_score, 0, 100)
    
    return base_score * relevance_factor


def _calculate_creation_tools_score(data: pd.Series) -> float:
    """
    Calculate score based on availability of creation tools.
    
    Does the player have stepback, fadeaway, floater, etc.?
    
    Proxy: 
    - High Pull-up 3 frequency (Range)
    - High Time of Possession (Handle)
    - High Creation Volume Ratio (Bag depth)
    """
    # 1. Range: Pull-up 3s
    pull_up_3a = data.get('pull_up_fg3a', 0)
    range_score = min(pull_up_3a / 6.0 * 100, 100) # 6+ pull-up 3s = Elite range
    
    # 2. Handle: Time of Possession
    time_poss = data.get('time_of_poss', 0)
    handle_score = min(time_poss / 8.0 * 100, 100) # 8+ seconds = Elite handle
    
    # 3. Bag Depth: Creation Volume Ratio
    cvr = data.get('creation_volume_ratio', 0)
    bag_score = min(cvr / 0.70 * 100, 100) # 70% self-created = Deep bag
    
    # Combined: Range (40%) + Handle (30%) + Bag (30%)
    score = (range_score * 0.4) + (handle_score * 0.3) + (bag_score * 0.3)
    
    return np.clip(score, 0, 100)


def get_required_features() -> List[str]:
    """Return list of features required for this component."""
    return [
        # Perimeter path
        'pct_uast_fgm',              # Unassisted rate
        'pull_up_fga',               # Volume
        'pull_up_fg3a',              # Range
        'creation_volume_ratio',     # Bag/Rate
        'time_of_poss',              # Handle
        'ts_pct',                    # Efficiency
        # Hub path
        'weighted_touch_production', # Touch points
        'leverage_usg_delta',        # Pressure response
        'usg_pct',                   # Usage
    ]


def get_missing_features(df: pd.DataFrame) -> List[str]:
    """Check which required features are missing from dataset."""
    required = get_required_features()
    missing = [f for f in required if f not in df.columns]
    return missing

def diagnose_player_score(player_data: pd.Series):
    """Prints a detailed breakdown of the self-created score for a player."""
    player_name = player_data.get('player_name', 'Unknown')
    season = player_data.get('season', 'N/A')
    print(f"\n{'='*60}")
    print(f"Diagnosing Self-Created Score: {player_name} ({season})")
    print(f"{'='*60}")

    # PATH 1: Perimeter Creation
    print(f"\n--- PATH 1: PERIMETER CREATION ---")
    
    # 1. Unassisted Score
    unassisted_rate = player_data.get('pct_uast_fgm', 0)
    if unassisted_rate > 1.0: unassisted_rate /= 100.0
    unassisted_score = _calculate_unassisted_score(player_data)
    print(f"  Unassisted (W: 25%): {unassisted_score:.1f}")
    print(f"    - pct_uast_fgm: {unassisted_rate:.3f}")

    # 2. Volume Score
    pull_up_fga = player_data.get('pull_up_fga', 0)
    time_of_poss = player_data.get('time_of_poss', 0)
    volume_score = _calculate_creation_volume_score(player_data)
    print(f"  Volume (W: 30%): {volume_score:.1f}")
    print(f"    - pull_up_fga: {pull_up_fga:.2f}")
    print(f"    - time_of_poss: {time_of_poss:.2f}")

    # 3. Efficiency Score
    ts_pct = player_data.get('ts_pct', 0)
    if ts_pct > 1.0: ts_pct /= 100.0
    efficiency_score = _calculate_self_created_efficiency_score(player_data)
    relevance_factor = np.clip((unassisted_rate - 0.2) / 0.4, 0, 1)
    print(f"  Efficiency (W: 30%): {efficiency_score:.1f}")
    print(f"    - ts_pct: {ts_pct:.3f}")
    print(f"    - relevance_factor: {relevance_factor:.2f}")

    # 4. Tools Score
    pull_up_3a = player_data.get('pull_up_fg3a', 0)
    cvr = player_data.get('creation_volume_ratio', 0)
    tools_score = _calculate_creation_tools_score(player_data)
    print(f"  Tools (W: 15%): {tools_score:.1f}")
    print(f"    - pull_up_fg3a: {pull_up_3a:.2f} (Range)")
    print(f"    - creation_volume_ratio: {cvr:.3f} (Bag)")

    perimeter_score = _calculate_perimeter_path_score(player_data)
    print(f"  → Perimeter Path Score: {perimeter_score:.1f}")

    # PATH 2: Hub Creation
    print(f"\n--- PATH 2: HUB CREATION ---")
    touch_prod = player_data.get('weighted_touch_production', 0)
    leverage_usg = player_data.get('leverage_usg_delta', 0)
    usage = player_data.get('usg_pct', 0)
    
    print(f"  Touch Production: {touch_prod:.1f} (threshold: {HUB_THRESHOLDS['touch_production_elite']})")
    print(f"  TS%: {ts_pct:.3f} (threshold: {HUB_THRESHOLDS['ts_elite']})")
    print(f"  Leverage USG Delta: {leverage_usg:.3f} (threshold: {HUB_THRESHOLDS['leverage_threshold']})")
    print(f"  Usage: {usage:.3f} (threshold: {HUB_THRESHOLDS['usage_threshold']})")
    
    hub_score = _calculate_hub_creation_score(player_data)
    
    # Show gate status
    gates_passed = []
    if usage >= HUB_THRESHOLDS['usage_threshold']:
        gates_passed.append("✅ Usage")
    else:
        gates_passed.append("❌ Usage (too low)")
    
    if leverage_usg >= HUB_THRESHOLDS['leverage_threshold']:
        gates_passed.append("✅ Pressure (not hiding)")
    else:
        gates_passed.append("❌ Pressure (HIDING)")
        
    if touch_prod >= HUB_THRESHOLDS['touch_production_elite']:
        gates_passed.append("✅ Touch Production")
    else:
        gates_passed.append("❌ Touch Production (below elite)")
        
    if ts_pct >= HUB_THRESHOLDS['ts_elite']:
        gates_passed.append("✅ Efficiency")
    else:
        gates_passed.append("❌ Efficiency (below elite)")
    
    print(f"  Gate Status: {' | '.join(gates_passed)}")
    print(f"  → Hub Path Score: {hub_score:.1f}")

    # FINAL
    final_score = calculate_self_created_score(player_data)
    print(f"\n{'='*40}")
    print(f"FINAL SELF-CREATED SCORE: {final_score:.2f}")
    print(f"  (MAX of Perimeter {perimeter_score:.1f} and Hub {hub_score:.1f})")
    print(f"{'='*40}")


VALIDATION_CASES: Dict[str, Dict] = {
    'Ben Simmons': {
        'season': '2019-20',
        'expected_score': 15,
        'tolerance': 15,
        'reason': 'No perimeter creation, no hub creation (hides under pressure)'
    },
    'James Harden': {
        'season': '2018-19',
        'expected_score': 95,
        'tolerance': 10,
        'reason': 'Elite perimeter creation (stepback king)'
    },
    'Luka Dončić': {
        'season': '2022-23',
        'expected_score': 95,
        'tolerance': 10,
        'reason': 'Elite perimeter creation (maximum bag)'
    },
    'Nikola Jokić': {
        'season': '2022-23',
        'expected_score': 85,
        'tolerance': 12,
        'reason': 'Elite hub creation (10.5 touch prod, 70% TS, steps UP)'
    },
    'Domantas Sabonis': {
        'season': '2022-23',
        'expected_score': 30,
        'tolerance': 15,
        'reason': 'Good touch production but HIDES (leverage -0.06) - no hub bonus'
    },
}


if __name__ == '__main__':
    from pathlib import Path
    
    dataset_path = Path(__file__).parents[4] / 'results' / 'predictive_dataset_with_friction.csv'
    
    if not dataset_path.exists():
        print("Dataset not found. Cannot run diagnosis.")
    else:
        print(f"Loading dataset from {dataset_path}...")
        df = pd.read_csv(dataset_path)
        # Normalize column names to lower case for consistency
        df.columns = [c.lower() for c in df.columns]

        players_to_diagnose = {
            'Luka Dončić': ['2022-23', '2024-25'],
            'Khris Middleton': ['2020-21', '2024-25'], # Peak vs recent
            'James Harden': ['2018-19', '2024-25'], # Peak vs recent
            'Ben Simmons': ['2018-19', '2023-24'], # Pre-injury vs post
            'Giannis Antetokounmpo': ['2020-21', '2024-25'],
            'Anthony Davis': ['2019-20', '2024-25']
        }

        for player_name, seasons in players_to_diagnose.items():
            for season in seasons:
                player_data = df[(df['player_name'].str.lower() == player_name.lower()) & (df['season'] == season)]
                
                if not player_data.empty:
                    diagnose_player_score(player_data.iloc[0])
                else:
                    print(f"\n--- Could not find data for {player_name} in {season} ---")
