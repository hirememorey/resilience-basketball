import numpy as np
import pandas as pd
from typing import Dict, List, Union

def calculate_z_scores(scores: Dict[int, float]) -> Dict[int, float]:
    """
    Convert raw scores to Z-Scores (Standardized).
    Z = (X - Mean) / StdDev
    
    This is crucial for combining metrics with different distributions (e.g., HHI vs Percentiles).
    """
    if not scores:
        return {}
    
    values = list(scores.values())
    mean = np.mean(values)
    std = np.std(values)
    
    if std == 0:
        return {k: 0.0 for k in scores.keys()}
        
    z_scores = {k: (v - mean) / std for k, v in scores.items()}
    return z_scores

def normalize_z_scores(z_scores: Dict[int, float], target_mean: float = 50, target_std: float = 15) -> Dict[int, float]:
    """
    Convert Z-Scores back to a 0-100 scale (roughly).
    Score = (Z * TargetStd) + TargetMean
    Capped at 0-100.
    """
    normalized = {}
    for k, z in z_scores.items():
        score = (z * target_std) + target_mean
        normalized[k] = max(0, min(100, score))
    return normalized

def standardize_metric(scores: Dict[int, float]) -> Dict[int, float]:
    """
    Full pipeline: Raw -> Z-Score -> Normalized (0-100).
    Ensures all metrics share the same distribution before aggregation.
    """
    z = calculate_z_scores(scores)
    return normalize_z_scores(z)

