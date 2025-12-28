"""
Ground Truth Labels Module

Contains curated expert-labeled player archetypes for training and validation.

The labels in player_labels.csv are the source of truth for archetype classification.
These are NOT derived from outcomes - they are expert judgments about creation ability.
"""

import pandas as pd
from pathlib import Path

def load_ground_truth() -> pd.DataFrame:
    """Load the curated ground truth labels."""
    labels_path = Path(__file__).parent / "player_labels.csv"
    
    # Skip comment lines (starting with #)
    df = pd.read_csv(labels_path, comment='#')
    
    return df


def get_archetype_distribution() -> dict:
    """Get count of players in each archetype."""
    df = load_ground_truth()
    return df['archetype'].value_counts().to_dict()

