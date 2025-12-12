"""
2D Risk Matrix Visualization Component

Creates the interactive scatter plot showing Performance vs Dependence for all players.
"""

import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import Optional, Union


def create_risk_matrix_plot(
    df_season: pd.DataFrame,
    selected_player: Optional[pd.Series] = None,
    width: int = 800,
    height: int = 600,
    show_continuum: bool = True
) -> go.Figure:
    """
    Create 2D Risk Matrix scatter plot.

    Args:
        df_season: All players in the selected season
        selected_player: Data for the highlighted player (optional)
        width: Plot width
        height: Plot height

    Returns:
        Plotly figure object
    """

    # Create base scatter plot
    fig = go.Figure()

    # Add all players with dependence-based color continuum
    if show_continuum and 'DEPENDENCE_SCORE' in df_season.columns:
        # Use dependence score for color gradient (blue = low dependence, red = high dependence)
        colors = df_season['DEPENDENCE_SCORE']
        colorbar_title = "Dependence<br>Score"

        fig.add_trace(go.Scatter(
            x=df_season['PERFORMANCE_SCORE'],
            y=df_season['DEPENDENCE_SCORE'],
            mode='markers',
            marker=dict(
                color=colors,
                colorscale='RdBu_r',  # Red-Blue reversed (blue = low, red = high)
                size=6,
                opacity=0.7,
                line=dict(width=1, color='darkgrey'),
                colorbar=dict(
                    title=colorbar_title,
                    tickformat='.0%',
                    len=0.8
                ),
                showscale=True
            ),
            name='All Players',
            hovertemplate=
            '<b>%{customdata[0]}</b><br>' +
            'Performance: %{x:.1%}<br>' +
            'Dependence: %{y:.1%}<br>' +
            'Archetype: %{customdata[1]}<extra></extra>',
            customdata=df_season[['PLAYER_NAME', 'RISK_CATEGORY']].values
        ))
    else:
        # Fallback to grey dots if continuum not available
        fig.add_trace(go.Scatter(
            x=df_season['PERFORMANCE_SCORE'],
            y=df_season['DEPENDENCE_SCORE'],
            mode='markers',
            marker=dict(
                color='lightgrey',
                size=6,
                opacity=0.6,
                line=dict(width=1, color='darkgrey')
            ),
            name='All Players',
            hovertemplate=
            '<b>%{customdata[0]}</b><br>' +
            'Performance: %{x:.1%}<br>' +
            'Dependence: %{y:.1%}<br>' +
            'Archetype: %{customdata[1]}<extra></extra>',
            customdata=df_season[['PLAYER_NAME', 'RISK_CATEGORY']].values
        ))

    # Load data-driven thresholds
    try:
        import json
        thresholds_path = "results/dependence_thresholds.json"
        with open(thresholds_path, 'r') as f:
            thresholds = json.load(f)
        perf_threshold = 0.70  # High performance (fixed)
        dep_threshold = thresholds.get('low_threshold', 0.3570)  # Low dependence threshold
        high_dep_threshold = thresholds.get('high_threshold', 0.4482)  # High dependence threshold
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to default values
        perf_threshold = 0.70
        dep_threshold = 0.3570
        high_dep_threshold = 0.4482

    # Add quadrant lines with data-driven thresholds
    fig.add_hline(
        y=dep_threshold,
        line_dash="dash",
        line_color="blue",
        opacity=0.5,
        annotation_text=f"Low Dependence (< {dep_threshold:.0%})",
        annotation_position="bottom right"
    )

    fig.add_hline(
        y=high_dep_threshold,
        line_dash="dash",
        line_color="red",
        opacity=0.5,
        annotation_text=f"High Dependence (≥ {high_dep_threshold:.0%})",
        annotation_position="top right"
    )

    fig.add_vline(
        x=perf_threshold,
        line_dash="dash",
        line_color="black",
        opacity=0.5,
        annotation_text="High Performance (≥70%)",
        annotation_position="top left"
    )

    fig.add_vline(
        x=0.30,
        line_dash="dash",
        line_color="black",
        opacity=0.5,
        annotation_text="Low Performance (<30%)",
        annotation_position="bottom left"
    )

    # Add quadrant labels with data-driven context
    fig.add_annotation(
        x=0.85, y=(dep_threshold + 1.0) / 2,  # High performance, low dependence
        text="<b>Franchise Cornerstone</b><br>High Perf + Low Dep<br><i>Max contract, build around</i>",
        showarrow=False,
        font=dict(size=11, color="green"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="green",
        borderwidth=2
    )

    fig.add_annotation(
        x=0.85, y=high_dep_threshold / 2,  # High performance, high dependence
        text="<b>Luxury Component</b><br>High Perf + High Dep<br><i>Valuable in system, risky as #1</i>",
        showarrow=False,
        font=dict(size=11, color="orange"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="orange",
        borderwidth=2
    )

    fig.add_annotation(
        x=0.15, y=(dep_threshold + 1.0) / 2,  # Low performance, low dependence
        text="<b>Depth</b><br>Low Perf + Low Dep<br><i>Reliable but limited</i>",
        showarrow=False,
        font=dict(size=10, color="blue"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="blue",
        borderwidth=2
    )

    fig.add_annotation(
        x=0.15, y=high_dep_threshold / 2,  # Low performance, high dependence
        text="<b>Avoid</b><br>Low Perf + High Dep<br><i>Empty calories</i>",
        showarrow=False,
        font=dict(size=10, color="red"),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="red",
        borderwidth=2
    )

    # Add middle region labels for continuum
    fig.add_annotation(
        x=0.85, y=(dep_threshold + high_dep_threshold) / 2,
        text="<b>Moderate Dep.</b><br>High Perf",
        showarrow=False,
        font=dict(size=9, color="darkgreen"),
        bgcolor="rgba(255,255,255,0.7)",
        bordercolor="darkgreen",
        borderwidth=1
    )

    fig.add_annotation(
        x=0.15, y=(dep_threshold + high_dep_threshold) / 2,
        text="<b>Moderate Dep.</b><br>Low Perf",
        showarrow=False,
        font=dict(size=9, color="darkred"),
        bgcolor="rgba(255,255,255,0.7)",
        bordercolor="darkred",
        borderwidth=1
    )

    # Add note about continuum
    fig.add_annotation(
        x=0.5, y=0.02,
        text="<i>Dependence Continuum: Blue = Low Dependence (portable) → Red = High Dependence (system-reliant)</i>",
        showarrow=False,
        font=dict(size=10, color="gray"),
        xref="paper", yref="paper"
    )

    # Highlight selected player if provided
    if selected_player is not None:
        player_color = get_archetype_color(selected_player.get('RISK_CATEGORY', ''))

        fig.add_trace(go.Scatter(
            x=[selected_player['PERFORMANCE_SCORE']],
            y=[selected_player['DEPENDENCE_SCORE']],
            mode='markers',
            marker=dict(
                color=player_color,
                size=15,
                symbol='star',
                line=dict(width=3, color='black')
            ),
            name='Selected Player',
            hovertemplate=
            '<b>%{customdata[0]} (SELECTED)</b><br>' +
            'Performance: %{x:.1%}<br>' +
            'Dependence: %{y:.1%}<br>' +
            'Archetype: %{customdata[1]}<extra></extra>',
            customdata=[[selected_player['PLAYER_NAME'], selected_player.get('RISK_CATEGORY', '')]]
        ))

    # Update layout
    fig.update_layout(
        title=dict(
            text="2D Risk Matrix: Performance vs Dependence",
            x=0.5,
            font=dict(size=16)
        ),
        xaxis=dict(
            title="Performance Score (Star-Level Potential)",
            range=[-0.05, 1.05],
            tickformat=".0%"
        ),
        yaxis=dict(
            title="Dependence Score (System Dependence)",
            range=[-0.05, 1.05],
            tickformat=".0%"
        ),
        width=width,
        height=height,
        showlegend=True,
        hovermode='closest'
    )

    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')

    return fig


def get_archetype_color(risk_category: Union[str, float, None]) -> str:
    """
    Get color for risk category.

    Args:
        risk_category: Risk category string (or NaN/null for unknown)

    Returns:
        Color string
    """
    color_map = {
        'Franchise Cornerstone': 'green',
        'Luxury Component': 'gold',
        'Depth': 'blue',
        'Avoid': 'red',
        'Moderate Performance': 'orange',
        'High Dependence': 'red',
        'Moderate Dependence': 'blue'
    }

    # Handle null/NaN values
    if pd.isna(risk_category) or not isinstance(risk_category, str):
        return 'grey'  # Default color for unknown categories

    # Extract base category if it contains additional info
    base_category = risk_category.split('(')[0].strip()

    # Handle compound categories from 2D risk matrix
    if 'Franchise Cornerstone' in risk_category:
        return 'green'
    elif 'Luxury' in risk_category or 'High Dependence' in risk_category:
        return 'gold'
    elif 'Depth' in risk_category or 'Moderate Dependence' in risk_category:
        return 'blue'
    elif 'Avoid' in risk_category:
        return 'red'
    elif 'Moderate Performance' in risk_category:
        return 'orange'

    return color_map.get(base_category, 'grey')


def create_archetype_summary_chart(df_season: pd.DataFrame) -> go.Figure:
    """
    Create a summary bar chart showing archetype distribution.

    Args:
        df_season: All players in the season

    Returns:
        Plotly figure object
    """

    # Count archetypes
    archetype_counts = df_season['RISK_CATEGORY'].value_counts()

    # Create color mapping
    colors = []
    for category in archetype_counts.index:
        colors.append(get_archetype_color(category))

    fig = go.Figure(data=[
        go.Bar(
            x=archetype_counts.index,
            y=archetype_counts.values,
            marker_color=colors,
            text=archetype_counts.values,
            textposition='auto',
        )
    ])

    fig.update_layout(
        title="Archetype Distribution",
        xaxis_title="Risk Category",
        yaxis_title="Number of Players",
        showlegend=False
    )

    return fig
