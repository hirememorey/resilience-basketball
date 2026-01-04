"""
Post Hub Path

Measures ability to create offense from post position through touches,
efficiency, and passing.

Theoretical Basis:
Hub creation is different from perimeter creation. It relies on structural positioning
rather than 1v1 separation. A player who can camp in the post/elbow and generate
efficient offense (scoring or passing) is an Engine, even if they don't take
pull-up jumpers.

Key Distinction:
- Finisher (Gobert/Capela): Needs the pass to be open (assisted dunks)
- Hub (Jokic/Embiid): CREATES the opening via positioning + touch (self-created)

Weight Justification:
- Post efficiency (30%): Must be hyper-efficient to justify slowing down offense
- Assist rate (30%): Hubs create for others (passing out of doubles)
- Post volume (25%): Must have enough touches to be a primary option
- Usage (15%): Must be a focal point
"""

from .base import CreationPath

class PostHubPath(CreationPath):
    
    WEIGHTS = {
        'efficiency': {
            'value': 0.30,
            'justification': 'Hubs must be efficient to justify static positioning',
            'source': 'First principles - post ups are inefficient unless elite'
        },
        'assist_rate': {
            'value': 0.30,
            'justification': 'Passing is key to punishing double teams',
            'source': 'Jokic/Sabonis archetype'
        },
        'post_volume': {
            'value': 0.25,
            'justification': 'Must have volume to be a hub',
            'source': 'Distinguishes primary options from role players'
        },
        'usage': {
            'value': 0.15,
            'justification': 'High usage confirms focal point status',
            'source': 'Standard usage metric'
        }
    }
    
    THRESHOLDS = {
        'elite_post_touches': 8.0,
        'elite_ts': 0.60,          # Post players need higher efficiency
        'elite_ast_pct': 0.30,     # Jokic level
        'elite_usage': 0.28,
        'baseline_ts': 0.55,       # League average
    }
    
    def calculate(self, player_data: dict) -> float:
        """Calculate Post Hub path score."""
        
        # Component 1: Post touch volume
        # If 'post_touches' not directly available, estimate from touches
        # This is a simplification; ideally we have specific post touch data
        touches = player_data.get('touches', 0)
        post_touches = player_data.get('post_touches', touches * 0.3) 
        post_volume_score = min((post_touches / self.THRESHOLDS['elite_post_touches']) * 100, 100)
        
        # Component 2: Efficiency (TS%)
        ts_pct = player_data.get('ts_pct', self.THRESHOLDS['baseline_ts'])
        # Post players need to be efficient. Scale 0.50 -> 0, 0.70 -> 100
        efficiency_score = (ts_pct - 0.50) / 0.20 * 100
        efficiency_score = max(0, min(efficiency_score, 100))
        
        # Component 3: Assist rate
        ast_pct = player_data.get('ast_pct', 0.15)
        assist_score = min((ast_pct / self.THRESHOLDS['elite_ast_pct']) * 100, 100)
        
        # Component 4: Usage
        usg_pct = player_data.get('usg_pct', 0.20)
        usage_score = min((usg_pct / self.THRESHOLDS['elite_usage']) * 100, 100)
        
        # NOTE: In the bare implementation, we DO NOT apply the efficiency gate
        # that was in the original proposal (where efficiency < 0.55 zeroed out the score).
        # We want the pure calculation first.
        
        # Weighted combination
        score = (
            post_volume_score * self.WEIGHTS['post_volume']['value'] +
            efficiency_score * self.WEIGHTS['efficiency']['value'] +
            assist_score * self.WEIGHTS['assist_rate']['value'] +
            usage_score * self.WEIGHTS['usage']['value']
        )
        
        return round(score, 1)
    
    def get_component_breakdown(self, player_data: dict) -> dict:
        """Return detailed breakdown."""
        touches = player_data.get('touches', 0)
        post_touches = player_data.get('post_touches', touches * 0.3)
        ts_pct = player_data.get('ts_pct', 0.55)
        ast_pct = player_data.get('ast_pct', 0.15)
        usg_pct = player_data.get('usg_pct', 0.20)
        
        efficiency_score = (ts_pct - 0.50) / 0.20 * 100
        efficiency_score = max(0, min(efficiency_score, 100))
        
        return {
            'post_touches_estimated': post_touches,
            'post_volume_score': min((post_touches / self.THRESHOLDS['elite_post_touches']) * 100, 100),
            'ts_pct_raw': ts_pct,
            'efficiency_score': efficiency_score,
            'ast_pct_raw': ast_pct,
            'assist_score': min((ast_pct / self.THRESHOLDS['elite_ast_pct']) * 100, 100),
            'usg_pct_raw': usg_pct,
            'usage_score': min((usg_pct / self.THRESHOLDS['elite_usage']) * 100, 100),
        }

