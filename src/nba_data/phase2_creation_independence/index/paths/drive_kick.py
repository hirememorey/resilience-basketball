"""
Drive-and-Kick Engine Path

Measures ability to create offense through penetration and passing.

Theoretical Basis:
Drive-and-kick creation generates advantage by collapsing the defense toward
the rim, creating open shots for teammates. This is distinct from ISO creation
because the value shows up in teammate production, not just self-scoring.

Key insight: A drive is only valuable if it forces defensive rotation. This
requires either:
1. A credible scoring threat (defense must help)
2. Elite passing vision (can find the open man)

Weight Justification:
- Drive volume (25%): Frequency of paint attacks
- Drive outcomes (25%): Points + assists per drive
- Assist creation (25%): Passes that lead to shots (even if missed)
- Rim pressure (15%): Successful drive completion rate
- Independence (10%): Ball dominance (time of possession)
"""

from .base import CreationPath

class DriveKickPath(CreationPath):
    
    WEIGHTS = {
        'drive_volume': {
            'value': 0.25,
            'justification': 'Frequency of rim attacks measures aggression',
            'source': 'First principles - more drives = more creation opportunities'
        },
        'drive_outcomes': {
            'value': 0.25,
            'justification': 'Points + assists per drive measures productivity',
            'source': 'First principles - drives must produce value'
        },
        'assist_creation': {
            'value': 0.25,
            'justification': 'Potential assists capture passes that lead to shots',
            'source': 'Captures creation value even when teammates miss'
        },
        'rim_pressure': {
            'value': 0.15,
            'justification': 'Successful drive rate (FGA + AST + fouls drawn)',
            'source': 'Measures ability to complete drives productively'
        },
        'independence': {
            'value': 0.10,
            'justification': 'Time of possession indicates ball dominance',
            'source': 'First principles - creators hold the ball longer'
        }
    }
    
    THRESHOLDS = {
        'elite_drives': 15.0,          # LeBron/Giannis level
        'elite_pts_created_per_drive': 1.5,  # Points + assist value per drive
        'elite_assist_creation_rate': 0.25,   # 25% of touches lead to potential assists
        'elite_time_per_touch': 4.0,   # Seconds - ball dominant players
    }
    
    def calculate(self, player_data: dict) -> float:
        """Calculate Drive-and-Kick path score."""
        
        # Component 1: Drive volume
        drives = player_data.get('drives_per_game', 0)
        volume_score = min((drives / self.THRESHOLDS['elite_drives']) * 100, 100)
        
        # Component 2: Drive outcomes (points created per drive)
        drive_pts = player_data.get('drive_pts', 0)
        drive_ast = player_data.get('drive_ast', 0)
        
        if drives > 0:
            # Need to be careful about per-game vs total scaling if data is inconsistent
            # But normally these come from tracking data per game
            pts_created_per_drive = (drive_pts + (drive_ast * 2.5)) / max(drives, 0.1)
            outcomes_score = min((pts_created_per_drive / self.THRESHOLDS['elite_pts_created_per_drive']) * 100, 100)
        else:
            outcomes_score = 0
        
        # Component 3: Assist creation rate
        potential_ast = player_data.get('potential_ast', 0)
        touches = player_data.get('touches', 1)
        assist_creation_rate = potential_ast / max(touches, 1)
        assist_score = min((assist_creation_rate / self.THRESHOLDS['elite_assist_creation_rate']) * 100, 100)
        
        # Component 4: Rim pressure (successful drive rate)
        drive_fga = player_data.get('drive_fga', 0)
        drive_pf = player_data.get('drive_pf', 0)
        
        if drives > 0:
            successful_rate = (drive_fga + drive_ast + drive_pf) / max(drives, 0.1)
            rim_score = min((successful_rate / 0.90) * 100, 100)
        else:
            rim_score = 0
        
        # Component 5: Independence (time per touch)
        time_of_poss = player_data.get('time_of_poss', 0)  # In seconds
        time_per_touch = time_of_poss / max(touches, 1)
        independence_score = min((time_per_touch / self.THRESHOLDS['elite_time_per_touch']) * 100, 100)
        
        # Weighted combination
        score = (
            volume_score * self.WEIGHTS['drive_volume']['value'] +
            outcomes_score * self.WEIGHTS['drive_outcomes']['value'] +
            assist_score * self.WEIGHTS['assist_creation']['value'] +
            rim_score * self.WEIGHTS['rim_pressure']['value'] +
            independence_score * self.WEIGHTS['independence']['value']
        )
        
        return round(score, 1)
    
    def get_component_breakdown(self, player_data: dict) -> dict:
        """Return detailed breakdown."""
        drives = player_data.get('drives_per_game', 0)
        drive_pts = player_data.get('drive_pts', 0)
        drive_ast = player_data.get('drive_ast', 0)
        
        pts_created_per_drive = 0
        if drives > 0:
            pts_created_per_drive = (drive_pts + (drive_ast * 2.5)) / max(drives, 0.1)
            
        potential_ast = player_data.get('potential_ast', 0)
        touches = player_data.get('touches', 1)
        assist_creation_rate = potential_ast / max(touches, 1)
        
        drive_fga = player_data.get('drive_fga', 0)
        drive_pf = player_data.get('drive_pf', 0)
        successful_rate = 0
        if drives > 0:
            successful_rate = (drive_fga + drive_ast + drive_pf) / max(drives, 0.1)
            
        time_of_poss = player_data.get('time_of_poss', 0)
        time_per_touch = time_of_poss / max(touches, 1)
        
        return {
            'drives_raw': drives,
            'volume_score': min((drives / self.THRESHOLDS['elite_drives']) * 100, 100),
            'pts_created_per_drive_raw': pts_created_per_drive,
            'outcomes_score': min((pts_created_per_drive / self.THRESHOLDS['elite_pts_created_per_drive']) * 100, 100),
            'assist_rate_raw': assist_creation_rate,
            'assist_score': min((assist_creation_rate / self.THRESHOLDS['elite_assist_creation_rate']) * 100, 100),
            'rim_pressure_raw': successful_rate,
            'rim_pressure_score': min((successful_rate / 0.90) * 100, 100),
            'time_per_touch_raw': time_per_touch,
            'independence_score': min((time_per_touch / self.THRESHOLDS['elite_time_per_touch']) * 100, 100),
        }

