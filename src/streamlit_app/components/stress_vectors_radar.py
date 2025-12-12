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
        player_percentiles: Player's percentile scores (0-100) or None for missing data
        width: Chart width
        height: Chart height

    Returns:
        Plotly figure object
    """

    # Create radar chart
    fig = go.Figure()

    # Handle None values - create custom hover text
    hover_text = []
    plot_values = []
    plot_categories = []
    na_categories = []

    for cat, val in zip(categories, player_percentiles):
        if val is None:
            hover_text.append(f"{cat}: N/A")
            na_categories.append(cat)
        else:
            hover_text.append(f"{cat}: {val:.1f}th percentile")
            plot_values.append(val)
            plot_categories.append(cat)

    # Add player data (only for non-None values)
    if plot_values:
        fig.add_trace(go.Scatterpolar(
            r=plot_values,
            theta=plot_categories,
            fill='toself',
            name='Selected Player',
            line=dict(color='red', width=3),
            fillcolor='rgba(255, 0, 0, 0.1)',
            hovertemplate='%{text}<extra></extra>',
            text=[text for cat, text in zip(categories, hover_text) if cat in plot_categories]
        ))

        # Add markers for N/A categories (at center with special styling)
        if na_categories:
            fig.add_trace(go.Scatterpolar(
                r=[0] * len(na_categories),  # Place at center
                theta=na_categories,
                mode='markers',
                name='Data Unavailable',
                marker=dict(
                    color='gray',
                    size=8,
                    symbol='x',
                    line=dict(color='black', width=1)
                ),
                hovertemplate='%{text}<extra></extra>',
                text=[text for cat, text in zip(categories, hover_text) if cat in na_categories],
                showlegend=True
            ))

    # Add league average reference (50th percentile) - only for categories with data
    league_avg = [50.0] * len(plot_categories)
    if plot_categories:
        fig.add_trace(go.Scatterpolar(
            r=league_avg,
            theta=plot_categories,
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
        player_percentiles: First player's percentile scores (can include None for missing data)
        comparison_percentiles: Second player's percentile scores (can include None for missing data)
        comparison_name: Name for comparison player
        width: Chart width
        height: Chart height

    Returns:
        Plotly figure object
    """

    fig = go.Figure()

    # Helper function to create hover text and filter None values
    def prepare_player_data(percentiles, player_name):
        hover_text = []
        plot_values = []
        plot_categories = []

        for cat, val in zip(categories, percentiles):
            if val is None:
                hover_text.append(f"{cat}: N/A")
            else:
                hover_text.append(f"{cat}: {val:.1f}th percentile")
                plot_values.append(val)
                plot_categories.append(cat)

        return hover_text, plot_values, plot_categories

    # Prepare first player data
    player_hover, player_values, player_cats = prepare_player_data(player_percentiles, 'Selected Player')

    # Prepare comparison player data
    comp_hover, comp_values, comp_cats = prepare_player_data(comparison_percentiles, comparison_name)

    # Add first player (only for non-None values)
    if player_values:
        fig.add_trace(go.Scatterpolar(
            r=player_values,
            theta=player_cats,
            fill='toself',
            name='Selected Player',
            line=dict(color='red', width=3),
            fillcolor='rgba(255, 0, 0, 0.1)',
            hovertemplate='%{text}<extra></extra>',
            text=[text for cat, text in zip(categories, player_hover) if cat in player_cats]
        ))

    # Add comparison player (only for non-None values)
    if comp_values:
        fig.add_trace(go.Scatterpolar(
            r=comp_values,
            theta=comp_cats,
            fill='toself',
            name=comparison_name,
            line=dict(color='blue', width=3),
            fillcolor='rgba(0, 0, 255, 0.1)',
            hovertemplate='%{text}<extra></extra>',
            text=[text for cat, text in zip(categories, comp_hover) if cat in comp_cats]
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
    - "N/A" indicates missing data (player didn't qualify or data unavailable)
    - The filled area represents the player's overall profile
    """

    return explanation
