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
    height: int = 600
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

    # Add all players as background (grey dots)
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

    # Define quadrant boundaries
    perf_threshold = 0.70  # High performance
    dep_threshold = 0.30   # Low dependence

    # Add quadrant lines
    fig.add_hline(
        y=dep_threshold,
        line_dash="dash",
        line_color="black",
        opacity=0.5,
        annotation_text="Low Dependence Threshold",
        annotation_position="bottom right"
    )

    fig.add_vline(
        x=perf_threshold,
        line_dash="dash",
        line_color="black",
        opacity=0.5,
        annotation_text="High Performance Threshold",
        annotation_position="top left"
    )

    # Add quadrant labels
    fig.add_annotation(
        x=0.85, y=0.85,
        text="<b>Franchise Cornerstone</b><br>High Perf + Low Dep",
        showarrow=False,
        font=dict(size=12, color="green"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="green",
        borderwidth=1
    )

    fig.add_annotation(
        x=0.85, y=0.15,
        text="<b>Luxury Component</b><br>High Perf + High Dep",
        showarrow=False,
        font=dict(size=12, color="gold"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gold",
        borderwidth=1
    )

    fig.add_annotation(
        x=0.15, y=0.85,
        text="<b>Depth</b><br>Low Perf + Low Dep",
        showarrow=False,
        font=dict(size=10, color="blue"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="blue",
        borderwidth=1
    )

    fig.add_annotation(
        x=0.15, y=0.15,
        text="<b>Avoid</b><br>Low Perf + High Dep",
        showarrow=False,
        font=dict(size=10, color="red"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="red",
        borderwidth=1
    )

    # Add note about data availability
    fig.add_annotation(
        x=0.5, y=0.02,
        text="<i>Note: Only ~0.1% of players have 2D Risk Matrix classifications</i>",
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
