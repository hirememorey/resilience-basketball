"""
2D Risk Matrix Visualization for Sloan Presentation

This script creates the "money slide" for the Sloan presentation: a 2D scatter
plot that maps players onto the Resilience/Scalability Risk Matrix.

Axes:
-   X-Axis (Resilience): A metric representing a player's ability to maintain
    performance under playoff pressure. We will use HELIO_POTENTIAL_SCORE as a proxy
    for resilience against top-tier competition.
-   Y-Axis (Scalability): A metric representing how well a player's efficiency
    projects to a higher usage role. We will calculate this by projecting every
    player to a standardized "Engine" usage rate (e.g., 28%) and measuring the
    projected efficiency (TS%).

Quadrants:
1.  Helio-Engine (Top-Right): High Resilience, High Scalability
2.  Ceiling-Raiser (Bottom-Right): High Resilience, Low Scalability
3.  Floor-Raiser (Top-Left): Low Resilience, High Scalability
4.  Empty Calories (Bottom-Left): Low Resilience, Low Scalability
"""

import pandas as pd
import streamlit as st
import altair as alt
from pathlib import Path
import sys
import os

# Add project root to path. This is a bit of a hack for Streamlit's execution model.
# It assumes the script is run from the root of the project.
sys.path.append(os.getcwd())
from src.nba_data.utils.projection_utils import project_efficiency

st.set_page_config(layout="wide")


@st.cache_data
def load_data():
    """Load and prepare the predictive dataset."""
    results_dir = Path("results")
    predictive_path = results_dir / "predictive_dataset.csv"
    if not predictive_path.exists():
        st.error(f"Fatal: Predictive dataset not found at {predictive_path}")
        st.stop()
        
    df = pd.read_csv(predictive_path)
    
    # Filter for the most recent season available in the dataset for a cleaner plot
    latest_season = df['SEASON'].max()
    df = df[df['SEASON'] == latest_season].copy()
    
    # Filter for players with a meaningful role
    df = df[df.get('RS_TOTAL_VOLUME', 1000) >= 500].copy()
    
    return df

@st.cache_data
def calculate_scalability(df: pd.DataFrame, target_usg: float) -> pd.DataFrame:
    """
    Calculate the Scalability Score for each player by projecting their TS%
    to a standardized target usage rate.
    """
    projections = df.apply(
        lambda row: project_efficiency(
            base_usg=row['USG_PCT'],
            base_ts=row['TS_PCT'],
            shot_quality_generation_delta=row['SHOT_QUALITY_GENERATION_DELTA'],
            target_usg=target_usg
        ),
        axis=1
    )
    
    proj_df = pd.json_normalize(projections)
    df['SCALABILITY_SCORE'] = proj_df['projected_ts']
    df['ARCHETYPE'] = proj_df['archetype']
    
    # Handle cases where projection was not possible
    df['SCALABILITY_SCORE'].fillna(df['TS_PCT'], inplace=True)
    
    return df

def create_chart(df: pd.DataFrame, resilience_metric: str, target_usg: float):
    """Create the 2D Risk Matrix scatter plot using Altair."""
    
    # Define quadrant boundaries (e.g., median values)
    median_resilience = df[resilience_metric].median()
    median_scalability = df['SCALABILITY_SCORE'].median()

    # Create the main scatter plot
    scatter = alt.Chart(df).mark_circle(size=80, opacity=0.7).encode(
        x=alt.X(f'{resilience_metric}:Q', title='Resilience (Helio Potential Score)'),
        y=alt.Y('SCALABILITY_SCORE:Q', title=f'Scalability (Projected TS% @ {target_usg*100:.0f}% USG)', scale=alt.Scale(zero=False)),
        color=alt.Color('ARCHETYPE:N', title='Creator Archetype'),
        tooltip=['PLAYER_NAME', 'SEASON', resilience_metric, 'SCALABILITY_SCORE', 'ARCHETYPE']
    ).properties(
        title='2D Risk Matrix: Resilience vs. Scalability'
    )
    
    # Add player labels for notable players
    # Filter for players who are far from the median (i.e., archetypes)
    df['dist_from_median'] = np.sqrt(
        ((df[resilience_metric] - median_resilience)**2) +
        ((df['SCALABILITY_SCORE'] - median_scalability)**2)
    )
    notable_players = df.nlargest(15, 'dist_from_median')
    
    labels = alt.Chart(notable_players).mark_text(
        align='left',
        baseline='middle',
        dx=7,
        fontSize=11
    ).encode(
        x=f'{resilience_metric}:Q',
        y='SCALABILITY_SCORE:Q',
        text='PLAYER_NAME'
    )

    # Add quadrant lines
    h_line = alt.Chart(pd.DataFrame({'y': [median_scalability]})).mark_rule(strokeDash=[5,5], color='gray').encode(y='y')
    v_line = alt.Chart(pd.DataFrame({'x': [median_resilience]})).mark_rule(strokeDash=[5,5], color='gray').encode(x='x')
    
    # Combine the charts
    chart = (scatter + labels + h_line + v_line).interactive()
    
    return chart

def main():
    """Streamlit app main function."""
    st.title("Sloan Presentation: The Universal Avatar")
    st.header("2D Risk Matrix: Resilience vs. Scalability")
    
    data = load_data()
    
    st.sidebar.header("Configuration")
    target_usg = st.sidebar.slider(
        "Target 'Engine' USG% for Scalability Projection",
        min_value=0.20,
        max_value=0.35,
        value=0.28,
        step=0.01
    )
    
    # For this visualization, HELIO_POTENTIAL_SCORE is the best proxy for Resilience
    resilience_metric = 'HELIO_POTENTIAL_SCORE'
    
    # Calculate scalability score
    chart_data = calculate_scalability(data, target_usg)
    
    st.write(f"""
    This chart plots players based on two fundamental physics principles:
    -   **Resilience (X-Axis)**: A player's ability to perform in the toughest contexts, represented by their `{resilience_metric}`.
    -   **Scalability (Y-Axis)**: A player's projected efficiency (`TS%`) when their usage is scaled up to a standardized **{target_usg*100:.0f}%**, the typical load of a primary offensive engine.
    """)
    
    # Create and display the chart
    risk_matrix_chart = create_chart(chart_data, resilience_metric, target_usg)
    st.altair_chart(risk_matrix_chart, use_container_width=True)
    
    st.subheader("Quadrant Definitions")
    st.markdown("""
    -   **Helio-Engine (Top-Right)**: Elite. Can handle high usage efficiently against tough competition. (e.g., Jokic, Luka)
    -   **Ceiling-Raiser (Bottom-Right)**: High-quality role players. Resilient and effective, but efficiency may drop if usage increases significantly. (e.g., KCP, Derrick White)
    -   **Floor-Raiser (Top-Left)**: "Good Stats, Bad Team" players. Can scale up usage efficiently, but may struggle against elite playoff defenses. (e.g., Jordan Poole in WAS)
    -   **Empty Calories (Bottom-Left)**: Low resilience and low scalability. These players are typically filtered out by the model.
    """)
    
    st.subheader("Data Inspector")
    st.dataframe(chart_data[['PLAYER_NAME', 'SEASON', resilience_metric, 'SCALABILITY_SCORE', 'ARCHETYPE', 'USG_PCT', 'TS_PCT']].sort_values(by=resilience_metric, ascending=False))

if __name__ == "__main__":
    main()

