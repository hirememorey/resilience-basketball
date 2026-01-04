"""
Multi-Path Combination Logic

Combines all creation paths into a single Self-Created Score.

Design Principles:
1. Take MAX of all paths (specialized dominance)
2. Award bonus for multi-modal ability
3. No gates or adjustments at this level
"""

from typing import Dict
from .iso import ISOCreatorPath
from .drive_kick import DriveKickPath
from .post_hub import PostHubPath
from .gravity import GravityPath

class MultiPathCombiner:
    
    # Multi-modal bonus thresholds
    ELITE_THRESHOLD = 75.0  # Score needed to be "elite" at a path
    GOOD_THRESHOLD = 60.0   # Score needed to be "good" at a path
    
    # Bonus amounts
    BONUS_THREE_ELITE = 15.0   # Elite at 3+ paths (prime LeBron)
    BONUS_TWO_ELITE = 8.0      # Elite at 2 paths (Harden, Luka)
    BONUS_GOOD_SECONDARY = 3.0 # Good at secondary path
    
    def __init__(self):
        self.iso_path = ISOCreatorPath()
        self.drive_kick_path = DriveKickPath()
        self.post_hub_path = PostHubPath()
        self.gravity_path = GravityPath()
    
    def calculate(self, player_data: dict) -> Dict:
        """
        Calculate combined Self-Created Score.
        
        Returns:
            Dictionary with:
            - final_score: 0-100 combined score
            - path_scores: Individual path scores
            - primary_mode: Highest-scoring path
            - multi_modal_bonus: Bonus applied
            - elite_paths: List of paths at elite level
        """
        
        # Calculate all paths
        path_scores = {
            'iso': self.iso_path.calculate(player_data),
            'drive_kick': self.drive_kick_path.calculate(player_data),
            'post_hub': self.post_hub_path.calculate(player_data),
            'gravity': self.gravity_path.calculate(player_data),
        }
        
        # Find primary mode (max)
        primary_mode = max(path_scores, key=path_scores.get)
        base_score = path_scores[primary_mode]
        
        # Calculate multi-modal bonus
        elite_paths = [name for name, score in path_scores.items() 
                       if score >= self.ELITE_THRESHOLD]
        good_paths = [name for name, score in path_scores.items() 
                      if score >= self.GOOD_THRESHOLD]
        
        if len(elite_paths) >= 3:
            multi_modal_bonus = self.BONUS_THREE_ELITE
        elif len(elite_paths) >= 2:
            multi_modal_bonus = self.BONUS_TWO_ELITE
        elif len(good_paths) >= 2:
            multi_modal_bonus = self.BONUS_GOOD_SECONDARY
        else:
            multi_modal_bonus = 0.0
        
        # Final score (capped at 100)
        final_score = min(base_score + multi_modal_bonus, 100.0)
        
        return {
            'final_score': round(final_score, 1),
            'path_scores': path_scores,
            'primary_mode': primary_mode,
            'base_score': base_score,
            'multi_modal_bonus': multi_modal_bonus,
            'elite_paths': elite_paths,
            'good_paths': good_paths,
        }
    
    def get_full_breakdown(self, player_data: dict) -> Dict:
        """Return complete breakdown including all path components."""
        result = self.calculate(player_data)
        result['component_breakdowns'] = {
            'iso': self.iso_path.get_component_breakdown(player_data),
            'drive_kick': self.drive_kick_path.get_component_breakdown(player_data),
            'post_hub': self.post_hub_path.get_component_breakdown(player_data),
            'gravity': self.gravity_path.get_component_breakdown(player_data),
        }
        return result

