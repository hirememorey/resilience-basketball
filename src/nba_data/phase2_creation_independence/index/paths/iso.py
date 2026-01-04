"""
ISO Creator Path

Measures ability to create scoring opportunities through isolation play.

Theoretical Basis:
ISO creation is the most direct form of offensive self-reliance. A player
who can consistently score in 1v1 situations needs no system or teammates
to generate offense. This path captures:

1. Unassisted FG% - What portion of made shots were self-created?
2. Pull-up volume - How often does the player create off the dribble?
3. Efficiency - Is the ISO creation actually productive?
4. Usage - Is this a primary or secondary skill?

Weight Justification:
- Unassisted (35%): Most direct measure of self-creation
- Pull-up (30%): Volume of creation attempts matters
- Efficiency (20%): Creation must be productive
- Usage (15%): Context of role
"""

from .base import CreationPath

class ISOCreatorPath(CreationPath):
    
    WEIGHTS = {
        'unassisted': {
            'value': 0.35,
            'justification': 'Direct measure of self-created makes vs assisted makes',
            'source': 'First principles - unassisted shots are definitionally self-created'
        },
        'pullup_volume': {
            'value': 0.30,
            'justification': 'Pull-up attempts measure creation frequency off the dribble',
            'source': 'First principles - pull-ups require ball-handling creation'
        },
        'efficiency': {
            'value': 0.20,
            'justification': 'Creation must be productive to have value',
            'source': 'First principles - inefficient creation is negative value'
        },
        'usage': {
            'value': 0.15,
            'justification': 'High usage in ISO context indicates primary role',
            'source': 'First principles - volume indicates team reliance'
        }
    }
    
    # Normalization thresholds (based on league data, not validation outcomes)
    THRESHOLDS = {
        'elite_pullup_fga': 10.0,  # Top 5% of pull-up volume
        'elite_usg': 0.30,         # All-Star level usage
        'baseline_ts': 0.55,       # League average TS%
        'ts_range': 0.15,          # Range from average to elite (0.55 to 0.70)
    }
    
    def calculate(self, player_data: dict) -> float:
        """Calculate ISO Creator path score."""
        
        # Component 1: Unassisted FG%
        uast_pct = player_data.get('pct_uast_fgm', 0)
        uast_score = min(uast_pct * 100, 100)
        
        # Component 2: Pull-up volume
        pull_up_fga = player_data.get('pull_up_fga', 0)
        pullup_score = min((pull_up_fga / self.THRESHOLDS['elite_pullup_fga']) * 100, 100)
        
        # Component 3: Efficiency
        ts_pct = player_data.get('ts_pct', self.THRESHOLDS['baseline_ts'])
        efficiency_score = (ts_pct - (self.THRESHOLDS['baseline_ts'] - 0.10)) / (self.THRESHOLDS['ts_range'] + 0.10) * 100
        efficiency_score = max(0, min(efficiency_score, 100))
        
        # Component 4: Usage
        usg_pct = player_data.get('usg_pct', 0.20)
        usage_score = min((usg_pct / self.THRESHOLDS['elite_usg']) * 100, 100)
        
        # Weighted combination
        score = (
            uast_score * self.WEIGHTS['unassisted']['value'] +
            pullup_score * self.WEIGHTS['pullup_volume']['value'] +
            efficiency_score * self.WEIGHTS['efficiency']['value'] +
            usage_score * self.WEIGHTS['usage']['value']
        )
        
        return round(score, 1)
    
    def get_component_breakdown(self, player_data: dict) -> dict:
        """Return detailed breakdown."""
        uast_pct = player_data.get('pct_uast_fgm', 0)
        pull_up_fga = player_data.get('pull_up_fga', 0)
        ts_pct = player_data.get('ts_pct', 0.55)
        usg_pct = player_data.get('usg_pct', 0.20)
        
        efficiency_score = (ts_pct - (self.THRESHOLDS['baseline_ts'] - 0.10)) / (self.THRESHOLDS['ts_range'] + 0.10) * 100
        efficiency_score = max(0, min(efficiency_score, 100))
        
        return {
            'unassisted_raw': uast_pct,
            'unassisted_score': min(uast_pct * 100, 100),
            'pullup_raw': pull_up_fga,
            'pullup_score': min((pull_up_fga / self.THRESHOLDS['elite_pullup_fga']) * 100, 100),
            'efficiency_raw': ts_pct,
            'efficiency_score': efficiency_score,
            'usage_raw': usg_pct,
            'usage_score': min((usg_pct / self.THRESHOLDS['elite_usg']) * 100, 100),
        }

