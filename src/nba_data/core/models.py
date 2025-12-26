"""
Core Domain Models for NBA Resilience Engine

This module defines the Strict Schemas (Pydantic models) that serve as the
Single Source of Truth for data integrity.

Principles:
1.  Fail Fast: If data doesn't match the schema, crash immediately.
2.  No Magic Numbers: Field constraints are defined here.
3.  Typed Interfaces: Functions should pass these objects, not loose Dicts.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import numpy as np

class PlayerID(BaseModel):
    id: int
    name: str

class ShootingStats(BaseModel):
    """Encapsulates shooting efficiency and volume for a specific context."""
    player_id: int
    season: str
    context: str # e.g., "0 Dribbles", "Iso"
    fga: float = Field(..., ge=0)
    fgm: float = Field(..., ge=0)
    efg_pct: float = Field(..., ge=0, le=1.5) # Allow >1.0 for small sample weirdness, but cap reasonable errors

    @field_validator('efg_pct')
    def check_valid_pct(cls, v):
        if np.isnan(v): return 0.0
        return v

class PlaytypeStats(BaseModel):
    """Synergy Playtype data."""
    player_id: int
    play_type: str # "Isolation", "PRBallHandler", etc.
    frequency: float = Field(..., ge=0, le=1.0)
    ppp: float = Field(..., ge=0, le=3.0) # Points Per Possession
    possessions: float = Field(..., ge=0)

class PlayerSeason(BaseModel):
    """
    The Atomic Unit of the project: A player's performance in a specific season.
    Aggregates all "Stress Vectors".
    """
    player_id: int
    player_name: str
    season: str
    
    # Metadata
    age: Optional[float] = None
    minutes: float = Field(..., ge=0)
    
    # Base Stats
    usg_pct: float = Field(..., ge=0, le=100.0) # Normalized to 0-100 usually, or 0-1? Let's assume 0-100 based on usage
    ts_pct: float = Field(..., ge=0, le=1.5)
    
    # Vector 1: Creation (Self-Reliance)
    shot_quality_generation_delta: Optional[float] = None
    creation_volume_ratio: Optional[float] = Field(None, ge=0, le=1.0)
    
    # Vector 2: Resilience (Playoff Translation)
    helio_potential_score: Optional[float] = None
    friction_coeff_iso: Optional[float] = None
    
    # Vector 3: Context
    avg_opponent_dcs: Optional[float] = None # Defensive Context Score

    class Config:
        extra = "ignore" # Allow extra fields during transition, but eventually forbid

