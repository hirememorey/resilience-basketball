"""
Stress Vectors Radar Chart Component

Creates radar chart showing normalized stress vector percentiles.
"""

import plotly.graph_objects as go
import pandas as pd
from typing import List, Tuple


def create_stress_vectors_radar(
    categories: List[str],
    player_percentiles: List[float],
    width: int = 600,
    height: int = 500
) -> go.Figure:
    """
    Create radar chart for stress vectors.

    Args:
        categories: List of category names
        player_percentiles: Player's percentile scores (0-100)
        width: Chart width
        height: Chart height

    Returns:
        Plotly figure object
    """

    # Create radar chart
    fig = go.Figure()

    # Add player data
    fig.add_trace(go.Scatterpolar(
        r=player_percentiles,
        theta=categories,
        fill='toself',
        name='Selected Player',
        line=dict(color='red', width=3),
        fillcolor='rgba(255, 0, 0, 0.1)',
        hovertemplate='%{theta}: %{r:.1f}th percentile<extra></extra>'
    ))

    # Add league average reference (50th percentile)
    league_avg = [50.0] * len(categories)
    fig.add_trace(go.Scatterpolar(
        r=league_avg,
        theta=categories,
        mode='lines',
        name='League Average',
        line=dict(color='grey', width=2, dash='dash'),
        hovertemplate='%{theta}: League Average (50th)<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title=dict(
            text="Stress Vectors Profile<br><sup>Percentile rank vs league average (higher = better)</sup>",
            x=0.5,
            font=dict(size=14)
        ),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='array',
                tickvals=[0, 25, 50, 75, 100],
                ticktext=['0%', '25%', '50%', '75%', '100%']
            )
        ),
        width=width,
        height=height,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_stress_vectors_comparison(
    categories: List[str],
    player_percentiles: List[float],
    comparison_percentiles: List[float],
    comparison_name: str = "Comparison",
    width: int = 600,
    height: int = 500
) -> go.Figure:
    """
    Create radar chart comparing two players' stress vectors.

    Args:
        categories: List of category names
        player_percentiles: First player's percentile scores
        comparison_percentiles: Second player's percentile scores
        comparison_name: Name for comparison player
        width: Chart width
        height: Chart height

    Returns:
        Plotly figure object
    """

    fig = go.Figure()

    # Add first player
    fig.add_trace(go.Scatterpolar(
        r=player_percentiles,
        theta=categories,
        fill='toself',
        name='Selected Player',
        line=dict(color='red', width=3),
        fillcolor='rgba(255, 0, 0, 0.1)',
        hovertemplate='%{theta}: %{r:.1f}th percentile<extra></extra>'
    ))

    # Add comparison player
    fig.add_trace(go.Scatterpolar(
        r=comparison_percentiles,
        theta=categories,
        fill='toself',
        name=comparison_name,
        line=dict(color='blue', width=3),
        fillcolor='rgba(0, 0, 255, 0.1)',
        hovertemplate='%{theta}: %{r:.1f}th percentile<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"Stress Vectors Comparison<br><sup>Percentile rank vs league average</sup>",
            x=0.5,
            font=dict(size=14)
        ),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='array',
                tickvals=[0, 25, 50, 75, 100],
                ticktext=['0%', '25%', '50%', '75%', '100%']
            )
        ),
        width=width,
        height=height,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def get_stress_vector_explanation() -> str:
    """
    Get explanation text for stress vectors.

    Returns:
        Formatted explanation string
    """
    explanation = """
    **Stress Vectors Explained:**

    - **Creation**: Efficiency drop-off when creating own shot (higher = more resilient)
    - **Leverage**: Efficiency and volume scaling in clutch situations (higher = better clutch)
    - **Pressure**: Willingness to take tight shots (higher = more aggressive)
    - **Physicality**: Rim pressure and physical presence (higher = more dominant)
    - **Plasticity**: Shot distribution adaptability (higher = more versatile)

    **Interpretation:**
    - Values shown as percentiles (0-100) compared to league average
    - Higher percentiles indicate stronger performance in that area
    - The filled area represents the player's overall profile
    """

    return explanation
