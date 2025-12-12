"""
NBA Playoff Resilience Engine - Streamlit App

Interactive web application to visualize the 2D Risk Matrix and Stress Vectors.
"""

import streamlit as st
import pandas as pd
import numpy as np
import logging
from pathlib import Path

# Add src to path for imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our components
from src.streamlit_app.utils.data_loaders import (
    create_master_dataframe,
    get_season_options,
    get_players_for_season,
    get_player_data,
    prepare_radar_chart_data
)
from src.streamlit_app.components.risk_matrix_plot import create_risk_matrix_plot, create_archetype_summary_chart
from src.streamlit_app.components.stress_vectors_radar import create_stress_vectors_radar, get_stress_vector_explanation

# Import shared utilities
from src.nba_data.utils.projection_utils import (
    calculate_empirical_usage_buckets,
    calculate_feature_percentiles,
    project_stress_vectors_for_usage,
    prepare_features_for_prediction
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit
st.set_page_config(
    page_title="NBA Playoff Resilience Engine",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .player-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2ca02c;
        margin-bottom: 0.5rem;
    }
    .archetype-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 1.2rem;
        margin: 0.5rem 0;
    }
    .cornerstone { background-color: #d4edda; color: #155724; border: 2px solid #28a745; }
    .luxury { background-color: #fff3cd; color: #856404; border: 2px solid #ffc107; }
    .depth { background-color: #cce7ff; color: #004085; border: 2px solid #007bff; }
    .avoid { background-color: #f8d7da; color: #721c24; border: 2px solid #dc3545; }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application."""

    # Title
    st.markdown('<div class="main-header">🏀 NBA Playoff Resilience Engine</div>', unsafe_allow_html=True)
    st.markdown("*Identify players who consistently perform better than expected in the playoffs*")

    # Load data
    try:
        df_master = create_master_dataframe()
        model, encoder = load_model_and_encoder()
        usage_buckets = calculate_empirical_usage_buckets(df_master)
        percentiles = calculate_feature_percentiles(df_master)
    except Exception as e:
        st.error(f"❌ Failed to load data: {str(e)}")
        st.stop()

    # Sidebar controls
    with st.sidebar:
        st.header("🎯 Player Selection")

        # Season selector - show all seasons, but note which have plasticity data
        all_seasons = get_season_options(df_master)

        # Check if RESILIENCE_SCORE column exists
        if 'RESILIENCE_SCORE' in df_master.columns:
            seasons_with_plasticity = df_master[df_master['RESILIENCE_SCORE'].notna()]['SEASON'].unique()
            seasons_with_plasticity = sorted(seasons_with_plasticity)
        else:
            seasons_with_plasticity = []
            st.error("❌ **Error**: Plasticity data could not be loaded. Radar charts will show default values.")

        selected_season = st.selectbox(
            "Select Season",
            all_seasons,
            index=len(all_seasons)-1,  # Default to most recent season
            help="Choose the season to analyze"
        )

        # Check if selected season has plasticity data
        if 'RESILIENCE_SCORE' not in df_master.columns:
            st.warning(f"⚠️ **Note**: Plasticity data is not available. All radar charts will show default values.")
        elif selected_season not in seasons_with_plasticity:
            st.warning(f"⚠️ **Note**: The {selected_season} season doesn't have plasticity data yet. Radar charts will show default values. Plasticity analysis requires playoff data.")
        else:
            st.info(f"✅ **Note**: The {selected_season} season has complete plasticity data available.")

        # Player selector (filtered by season)
        df_season = get_players_for_season(df_master, selected_season)

        # Add dependence range filter
        st.subheader("🔍 Filter Options")

        # Dependence range filter
        dep_min, dep_max = st.slider(
            "Dependence Score Range",
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.05,
            format="%.0f%%",
            help="Filter players by system dependence level (0% = completely independent, 100% = highly system-dependent)"
        )

        # Performance range filter
        perf_min, perf_max = st.slider(
            "Performance Score Range",
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.05,
            format="%.0f%%",
            help="Filter players by star-level potential (0% = limited, 100% = elite)"
        )

        # Apply filters to season data (outside sidebar for global scope)
        df_filtered = df_season.copy()

        # Filter by dependence score if available
        if 'DEPENDENCE_SCORE' in df_filtered.columns:
            df_filtered = df_filtered[
                (df_filtered['DEPENDENCE_SCORE'].isna()) |
                ((df_filtered['DEPENDENCE_SCORE'] >= dep_min) & (df_filtered['DEPENDENCE_SCORE'] <= dep_max))
            ]

        # Filter by performance score if available
        if 'PERFORMANCE_SCORE' in df_filtered.columns:
            df_filtered = df_filtered[
                (df_filtered['PERFORMANCE_SCORE'].isna()) |
                ((df_filtered['PERFORMANCE_SCORE'] >= perf_min) & (df_filtered['PERFORMANCE_SCORE'] <= perf_max))
            ]

        # Update player options based on filters
        player_options = sorted(df_filtered['PLAYER_NAME'].unique())

        selected_player_name = st.selectbox(
            "Select Player",
            player_options,
            help="Choose a player to analyze (filtered by your criteria above)"
        )

        # Get player data
        player_data = get_player_data(df_master, selected_player_name, selected_season)

        if player_data is None:
            st.error("❌ Player data not found")
            st.stop()

        # Show filter summary
        st.markdown("---")
        st.subheader("📊 Current Filters")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Dependence Range", f"{dep_min:.0%} - {dep_max:.0%}")
        with col2:
            st.metric("Performance Range", f"{perf_min:.0%} - {perf_max:.0%}")

        filtered_count = len(df_filtered)
        total_count = len(df_season)
        st.caption(f"Showing {filtered_count} of {total_count} players in {selected_season}")

    # Main content area (moved outside sidebar block)
    if player_data is not None:
        display_player_analysis(player_data, df_season, df_filtered, model, encoder, usage_buckets, percentiles)

    # Main content area
    if player_data is not None:
        display_player_analysis(player_data, df_season, df_filtered, model, encoder, usage_buckets, percentiles)


def load_model_and_encoder():
    """Load the trained model and encoder."""
    try:
        import joblib
        model = joblib.load('models/resilience_xgb_rfe_10.pkl')
        encoder = joblib.load('models/archetype_encoder_rfe_10.pkl')
        return model, encoder
    except FileNotFoundError as e:
        st.error(f"❌ Model files not found: {e}")
        st.error("Please run model training first.")
        st.stop()


def display_player_analysis(player_data, df_season, df_filtered, model, encoder, usage_buckets, percentiles):
    """Display the main player analysis interface."""

    # Player header
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f'<div class="player-header">👤 {player_data["PLAYER_NAME"]}</div>', unsafe_allow_html=True)
        st.subheader(f"Season: {player_data['SEASON']}")

    with col2:
        risk_category = player_data.get('RISK_CATEGORY')
        if pd.notna(risk_category):
            archetype_class = get_archetype_css_class(risk_category)
            st.markdown(f'<div class="archetype-badge {archetype_class}">{risk_category}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="archetype-badge depth">Analysis Pending</div>', unsafe_allow_html=True)

    # Key metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        perf_score = player_data.get('PERFORMANCE_SCORE')
        if pd.notna(perf_score):
            st.metric("Performance Score", f"{perf_score:.1%}",
                     help="Probability of star-level playoff performance")
        else:
            st.metric("Performance Score", "Data Unavailable",
                     help="2D Risk Matrix analysis not yet completed for this player")

    with col2:
        dep_score = player_data.get('DEPENDENCE_SCORE')
        if pd.notna(dep_score):
            st.metric("Dependence Score", f"{dep_score:.1%}",
                     help="How dependent production is on system/team context")
        else:
            st.metric("Dependence Score", "Data Unavailable",
                     help="2D Risk Matrix analysis not yet completed for this player")

    with col3:
        usage_pct = player_data.get('USG_PCT', 0)
        st.metric("Usage Rate", f"{usage_pct:.1%}",
                 help="Percentage of team possessions used while on court")

    # Add data availability notice
    if pd.isna(perf_score) or pd.isna(dep_score):
        st.info("ℹ️ **Note**: This player doesn't have 2D Risk Matrix classifications yet. Only a few key players have been analyzed. The stress vectors and usage projections are still available below.")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Risk Matrix", "🎯 Stress Profile", "🔮 What-If Simulator"])

    with tab1:
        display_risk_matrix_tab(player_data, df_season, df_filtered)

    with tab2:
        display_stress_profile_tab(player_data, df_filtered)

    with tab3:
        display_usage_simulator_tab(player_data, df_season, model, encoder, usage_buckets, percentiles)


def display_risk_matrix_tab(player_data, df_season, df_filtered):
    """Display the 2D Risk Matrix tab."""

    st.header("📊 2D Risk Matrix: Performance vs Dependence")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Create and display the risk matrix plot with filtered data
        fig = create_risk_matrix_plot(df_filtered, player_data)
        st.plotly_chart(fig, use_container_width=True, key="risk_matrix_plot_main")

    with col2:
        st.subheader("📈 Archetype Distribution")
        summary_fig = create_archetype_summary_chart(df_filtered)
        st.plotly_chart(summary_fig, use_container_width=True, key="archetype_summary_chart_main")

        st.subheader("🎯 Quadrant Guide")
        st.markdown("""
        **Franchise Cornerstone** 🟢
        - High Performance + Low Dependence
        - Max contract, build around

        **Luxury Component** 🟡
        - High Performance + High Dependence
        - Valuable in system, risky as #1

        **Depth** 🔵
        - Low Performance + Low Dependence
        - Reliable but limited role

        **Avoid** 🔴
        - Low Performance + High Dependence
        - Empty calories
        """)

        # Add dependence continuum explanation
        st.markdown("---")
        st.subheader("🌈 Dependence Continuum")
        st.markdown("""
        **Color Scale**: Blue = Low Dependence (portable) → Red = High Dependence (system-reliant)

        Use the sidebar filters to explore players within specific dependence ranges:
        - **0-30%**: Highly portable talents
        - **30-70%**: Moderate system dependence
        - **70-100%**: Heavy system reliance
        """)


def display_stress_profile_tab(player_data, df_season):
    """Display the stress vectors profile tab."""

    st.header("🎯 Stress Vectors Profile")

    # Prepare radar chart data
    categories, percentiles = prepare_radar_chart_data(df_season, player_data)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Create and display radar chart
        radar_fig = create_stress_vectors_radar(categories, percentiles)
        st.plotly_chart(radar_fig, use_container_width=True, key="stress_vectors_radar_main")

    with col2:
        st.subheader("📊 Profile Summary")

        # Show percentile scores
        for cat, pct in zip(categories, percentiles):
            if pct is None:
                icon = "⚪"
                desc = "Data N/A"
                st.write(f"{icon} **{cat}**: N/A ({desc})")
            else:
                if pct >= 75:
                    icon = "🟢"
                    desc = "Elite"
                elif pct >= 50:
                    icon = "🟡"
                    desc = "Above Avg"
                elif pct >= 25:
                    icon = "🟠"
                    desc = "Below Avg"
                else:
                    icon = "🔴"
                    desc = "Weak"

                st.write(f"{icon} **{cat}**: {pct:.1f}th percentile ({desc})")

        st.markdown("---")
        st.markdown(get_stress_vector_explanation())


def display_usage_simulator_tab(player_data, df_season, model, encoder, usage_buckets, percentiles):
    """Display the what-if usage simulator tab."""

    st.header("🔮 What-If Usage Simulator")
    st.markdown("Explore how this player's archetype might change at different usage levels")

    # Current usage
    current_usage = player_data.get('USG_PCT', 0.20)

    # Usage slider
    col1, col2 = st.columns([2, 1])

    with col1:
        target_usage = st.slider(
            "Projected Usage %",
            min_value=0.10,
            max_value=0.40,
            value=float(current_usage),
            step=0.01,
            format="%.1f%%",
            help="Adjust usage level to see projected archetype"
        )

        # Show current vs projected
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Current Usage", f"{current_usage:.1%}")
        with col_b:
            st.metric("Projected Usage", f"{target_usage:.1%}")
        with col_c:
            change = (target_usage - current_usage) / current_usage * 100
            st.metric("Change", f"{change:+.1f}%")

    # Project features for new usage level
    try:
        projected_data = project_stress_vectors_for_usage(
            player_data, target_usage, usage_buckets, percentiles
        )

        # Prepare features for model prediction
        feature_names = list(model.feature_names_in_)
        features_array = prepare_features_for_prediction(projected_data, feature_names, model)

        # Make prediction
        probabilities = model.predict_proba(features_array)[0]

        # Get archetype prediction
        pred_class = model.predict(features_array)[0]
        predicted_archetype = encoder.inverse_transform([pred_class])[0]

        # Calculate star-level potential
        star_level_potential = probabilities[encoder.classes_ == 'King (Resilient Star)'][0] + \
                              probabilities[encoder.classes_ == 'Bulldozer (Fragile Star)'][0]

        # Display results
        col1, col2, col3 = st.columns(3)

        with col1:
            archetype_class = get_archetype_css_class(predicted_archetype)
            st.markdown(f'<div class="archetype-badge {archetype_class}">{predicted_archetype}</div>', unsafe_allow_html=True)

        with col2:
            st.metric("Projected Star Potential", f"{star_level_potential:.1%}")

        with col3:
            # Show if flash multiplier was applied
            if projected_data.get('_FLASH_MULTIPLIER_ACTIVE', False):
                st.success("✨ **Flash Multiplier Applied!** Elite efficiency on low volume detected.")
            else:
                st.info("Standard projection applied")

        # Show updated radar chart
        st.subheader("📊 Projected Stress Profile")
        categories, new_percentiles = prepare_radar_chart_data(df_season, projected_data)
        radar_fig = create_stress_vectors_radar(categories, new_percentiles)
        st.plotly_chart(radar_fig, use_container_width=True, key="projected_stress_radar_main")

        # Show probability breakdown
        st.subheader("🎲 Archetype Probabilities")
        prob_cols = st.columns(4)

        archetype_names = {
            'King (Resilient Star)': 'King',
            'Bulldozer (Fragile Star)': 'Bulldozer',
            'Sniper (Resilient Role)': 'Sniper',
            'Victim (Fragile Role)': 'Victim'
        }

        for i, (full_name, short_name) in enumerate(archetype_names.items()):
            prob = probabilities[encoder.classes_ == full_name][0]
            with prob_cols[i % 4]:
                st.metric(short_name, f"{prob:.1%}")

    except Exception as e:
        st.error(f"❌ Error in usage simulation: {str(e)}")
        logger.error(f"Usage simulation error: {e}", exc_info=True)


def get_archetype_css_class(risk_category) -> str:
    """Get CSS class for archetype badge."""
    # Handle null/NaN values
    if pd.isna(risk_category) or not isinstance(risk_category, str):
        return 'depth'  # Default for unknown categories

    if 'Cornerstone' in risk_category:
        return 'cornerstone'
    elif 'Luxury' in risk_category:
        return 'luxury'
    elif 'Depth' in risk_category:
        return 'depth'
    elif 'Avoid' in risk_category:
        return 'avoid'
    else:
        return 'depth'  # Default


if __name__ == "__main__":
    main()
