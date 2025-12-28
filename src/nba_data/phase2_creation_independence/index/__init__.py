"""
Creation Independence Index (CII) Module

This module calculates the Creation Independence Index for NBA players,
measuring their ability to create offense when the defense knows it's coming.

Components:
- Self-Created Shot Score (30%)
- Pressure Appetite Score (25%)
- Shot Difficulty Embrace Score (20%)
- Defensive Attention Survival Score (15%)
- Force Multiplication Score (10%)

Usage:
    from phase2_creation_independence.index import calculate_cii
    
    cii_score = calculate_cii(player_data)
"""

from .composite import calculate_cii

__all__ = ['calculate_cii']

