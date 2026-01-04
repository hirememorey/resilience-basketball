"""
Base class for all creation paths.
Each path must be a pure calculation with no gates or adjustments.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class CreationPath(ABC):
    """
    Abstract base class for creation path calculations.
    
    Design Principles:
    1. Pure calculation - no side effects
    2. No gates or thresholds that modify scores
    3. All weights must be documented with justification
    4. Returns 0-100 score
    """
    
    # Document all weights with justification
    WEIGHTS: Dict[str, Dict[str, Any]] = {}
    
    @abstractmethod
    def calculate(self, player_data: dict) -> float:
        """
        Calculate path score for a player.
        
        Args:
            player_data: Dictionary of player statistics
            
        Returns:
            Score from 0-100
        """
        pass
    
    @abstractmethod
    def get_component_breakdown(self, player_data: dict) -> dict:
        """
        Return detailed breakdown of score components.
        
        Returns:
            Dictionary with each sub-component score
        """
        pass
    
    @classmethod
    def get_weight_justifications(cls) -> dict:
        """Return documentation for all weights."""
        return cls.WEIGHTS

