"""
Gravity Engine Path

Measures ability to create offense through off-ball movement and spacing.

Theoretical Basis:
Gravity players create advantage by distorting the defensive shape through
off-ball movement and the threat of their shot. This is a form of creation
because it forces defensive rotations before the ball even arrives.

Key insight: Gravity requires BOTH elite shooting threat AND elite movement.
Without a shot, movement is ignored. Without movement, spacing is static.

Weight Justification:
- Screen assist value (20%): Direct measure of generating value for others via positioning
- Catch-and-shoot efficiency (25%): High efficiency suggests good movement to get open
- Off-ball volume (20%): High % of catch-and-shoot FGA indicates movement reliance
- Pull-up threat (20%): Defense must respect the on-ball threat to honor off-ball gravity
- Movement proxy (15%): Miles traveled per game or paint touches (if available)
"""

from .base import CreationPath

class GravityPath(CreationPath):
    
    WEIGHTS = {
        'screen_ast_value': {
            'value': 0.20,
            'justification': 'Generates points for teammates through off-ball screening',
            'source': 'Curry/Draymond archetype'
        },
        'catch_shoot_efficiency': {
            'value': 0.25,
            'justification': 'High efficiency on assisted looks suggests elite spacing creation',
            'source': 'First principles - making hard catch-and-shoots is a skill'
        },
        'offball_volume': {
            'value': 0.20,
            'justification': 'High volume of movement-based shots',
            'source': 'Distinguishes movers from stationary shooters'
        },
        'pullup_threat': {
            'value': 0.20,
            'justification': 'Defense must fear the pull-up to respect the gravity',
            'source': 'Theoretical basis - gravity requires multi-level threat'
        },
        'movement_proxy': {
            'value': 0.15,
            'justification': 'Distance traveled or activity rate',
            'source': 'Proxy for physical activity'
        }
    }
    
    THRESHOLDS = {
        'elite_screen_ast': 4.0,
        'elite_cs_fg3_pct': 0.42,
        'elite_offball_rate': 0.50, # 50% of shots are catch-and-shoot
        'elite_pullup_pts_per_fga': 1.2,
        'elite_movement_dist': 2.8, # Miles per game
    }
    
    def calculate(self, player_data: dict) -> float:
        """Calculate Gravity Engine path score."""
        
        # Component 1: Screen assist volume
        screen_ast = player_data.get('screen_ast', 0)
        screen_value_score = min((screen_ast / self.THRESHOLDS['elite_screen_ast']) * 100, 100)
        
        # Component 2: Catch-and-shoot efficiency (3PT)
        cs_fg3_pct = player_data.get('catch_shoot_fg3_pct', 0.36)
        # Scale 0.30 -> 0, 0.45 -> 100
        cs_eff_score = (cs_fg3_pct - 0.30) / 0.15 * 100
        cs_eff_score = max(0, min(cs_eff_score, 100))
        
        # Component 3: Off-ball volume (C&S FGA / Total FGA)
        cs_fga = player_data.get('catch_shoot_fga', 0)
        total_fga = player_data.get('fga', 1)
        offball_rate = cs_fga / max(total_fga, 1)
        offball_volume_score = min((offball_rate / self.THRESHOLDS['elite_offball_rate']) * 100, 100)
        
        # Component 4: Pull-up threat
        pull_up_pts = player_data.get('pull_up_pts', 0)
        pull_up_fga = player_data.get('pull_up_fga', 0)
        if pull_up_fga > 0:
            pull_up_eff = pull_up_pts / pull_up_fga
            pull_up_threat_score = min((pull_up_eff / self.THRESHOLDS['elite_pullup_pts_per_fga']) * 100, 100)
        else:
            pull_up_threat_score = 0
            
        # Component 5: Movement Proxy
        # If 'dist_miles' not available, use 'paint_touches' as weak proxy for activity
        dist_miles = player_data.get('dist_miles', player_data.get('paint_touches', 0) / 2.0)
        movement_score = min((dist_miles / self.THRESHOLDS['elite_movement_dist']) * 100, 100)
        
        # NOTE: In the bare implementation, we DO NOT apply the shooting gate
        # (ts_pct < 0.55 or three_pt_rate < 0.25) proposed in the specification.
        # We want pure calculation first.
        
        # Weighted combination
        score = (
            screen_value_score * self.WEIGHTS['screen_ast_value']['value'] +
            cs_eff_score * self.WEIGHTS['catch_shoot_efficiency']['value'] +
            offball_volume_score * self.WEIGHTS['offball_volume']['value'] +
            pull_up_threat_score * self.WEIGHTS['pullup_threat']['value'] +
            movement_score * self.WEIGHTS['movement_proxy']['value']
        )
        
        return round(score, 1)
    
    def get_component_breakdown(self, player_data: dict) -> dict:
        """Return detailed breakdown."""
        screen_ast = player_data.get('screen_ast', 0)
        cs_fg3_pct = player_data.get('catch_shoot_fg3_pct', 0.36)
        cs_fga = player_data.get('catch_shoot_fga', 0)
        total_fga = player_data.get('fga', 1)
        offball_rate = cs_fga / max(total_fga, 1)
        
        pull_up_pts = player_data.get('pull_up_pts', 0)
        pull_up_fga = player_data.get('pull_up_fga', 0)
        pull_up_eff = pull_up_pts / max(pull_up_fga, 0.1)
        
        dist_miles = player_data.get('dist_miles', player_data.get('paint_touches', 0) / 2.0)
        
        return {
            'screen_ast_raw': screen_ast,
            'screen_value_score': min((screen_ast / self.THRESHOLDS['elite_screen_ast']) * 100, 100),
            'cs_fg3_pct_raw': cs_fg3_pct,
            'cs_eff_score': max(0, min((cs_fg3_pct - 0.30) / 0.15 * 100, 100)),
            'offball_rate_raw': offball_rate,
            'offball_volume_score': min((offball_rate / self.THRESHOLDS['elite_offball_rate']) * 100, 100),
            'pullup_eff_raw': pull_up_eff,
            'pull_up_threat_score': min((pull_up_eff / self.THRESHOLDS['elite_pullup_pts_per_fga']) * 100, 100),
            'dist_miles_proxy': dist_miles,
            'movement_score': min((dist_miles / self.THRESHOLDS['elite_movement_dist']) * 100, 100),
        }

