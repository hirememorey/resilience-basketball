# NBA Playoff Resilience Engine - Streamlit App

Interactive web application for visualizing the 2D Risk Matrix and exploring player archetypes.

## Features

- **📊 2D Risk Matrix**: Interactive scatter plot showing Performance vs Dependence for all players
- **🎯 Stress Vectors Profile**: Radar chart showing normalized player strengths across 5 dimensions
- **🔮 What-If Simulator**: Explore how archetypes change at different usage levels
- **🎨 Beautiful UI**: Professional design with real-time updates

## Architecture

```
src/streamlit_app/
├── main.py                 # Main app entry point
├── utils/
│   └── data_loaders.py     # Cached data loading functions
├── components/
│   ├── risk_matrix_plot.py # 2D scatter plot component
│   └── stress_vectors_radar.py # Radar chart component
└── requirements.txt        # App-specific dependencies
```

## Quick Start

### Prerequisites

1. **Install dependencies**:
```bash
pip install -r src/streamlit_app/requirements.txt
```

2. **Ensure data is available**:
```bash
# These files must exist for the app to work
ls results/
# - predictive_dataset.csv
# - resilience_archetypes.csv

ls models/
# - resilience_xgb_rfe_15.pkl
# - archetype_encoder_rfe_15.pkl
```

### Run the App

```bash
# From project root
python scripts/run_streamlit_app.py

# Or directly with streamlit
streamlit run src/streamlit_app/main.py
```

The app will open at `http://localhost:8501`

## Usage Guide

### 1. Player Selection
- Choose a season from the dropdown
- Select a player (filtered by chosen season)
- The app immediately shows their archetype and key metrics

### 2. Risk Matrix Tab
- **X-axis**: Performance Score (star-level potential)
- **Y-axis**: Dependence Score (system dependence)
- **Quadrants**: Franchise Cornerstone (🟢), Luxury Component (🟡), Depth (🔵), Avoid (🔴)
- **Hover**: See details for any player
- **Selected Player**: Highlighted with star marker

### 3. Stress Profile Tab
- **Radar Chart**: Percentile rankings across 5 stress vectors
- **Interpretation**: Higher percentiles = better performance
- **Comparison**: Against league average (50th percentile)

### 4. What-If Simulator Tab
- **Usage Slider**: Adjust projected usage from 10% to 40%
- **Live Updates**: See how archetype changes in real-time
- **Flash Multiplier**: Automatic detection of "elite efficiency on low volume"
- **Probability Breakdown**: See confidence in each archetype

## Key Features Explained

### 2D Risk Matrix
The core insight: Performance and Dependence are orthogonal dimensions.

- **Performance**: "Will this player produce?" (what actually happened)
- **Dependence**: "Is this production portable?" (system dependence)

### Stress Vectors
Five fundamental basketball physics dimensions:

1. **Creation**: Efficiency drop-off when creating own shot
2. **Leverage**: Clutch performance scaling
3. **Pressure**: Willingness to take tight shots
4. **Physicality**: Rim pressure and physical dominance
5. **Plasticity**: Shot distribution adaptability

### Universal Projection
Features scale together using empirical distributions, not linear scaling:
- **Linear scaling**: CREATION_VOLUME_RATIO: 0.1 → 0.15 (still role player)
- **Universal projection**: CREATION_VOLUME_RATIO: 0.1 → 0.6977 (star-level volume)

## Technical Details

### Performance Optimizations
- **Caching**: `st.cache_data` prevents reloading large CSVs
- **Lazy Loading**: Data loaded only when needed
- **Efficient Updates**: Only selected player data recomputed on changes

### Error Handling
- **Graceful Failures**: Clear error messages if data is missing
- **Data Validation**: Checks for required files on startup
- **Fallback Values**: Sensible defaults when data is incomplete

### Responsive Design
- **Mobile Friendly**: Adapts to different screen sizes
- **Dark Mode Compatible**: Works with Streamlit's theme system
- **Interactive Charts**: Plotly enables hover states and zooming

## Troubleshooting

### Common Issues

**"Model files not found"**
```bash
# Train the model first
python src/nba_data/scripts/train_rfe_model.py
```

**"Predictive dataset not found"**
```bash
# Run feature generation
python src/nba_data/scripts/evaluate_plasticity_potential.py
python src/nba_data/scripts/calculate_simple_resilience.py
```

**"No data for season"**
- Check that `results/resilience_archetypes.csv` contains the season
- Run data collection for missing seasons

### Performance Tips

- **Large Datasets**: The app loads all seasons at once for speed
- **Memory Usage**: ~500MB for full dataset (acceptable for modern systems)
- **Browser**: Chrome recommended for best Plotly performance

## Deployment

For production deployment:

```bash
# Install additional dependencies
pip install streamlit-cloud  # or your deployment platform

# Run with production settings
streamlit run src/streamlit_app/main.py --server.port $PORT --server.address 0.0.0.0
```

## Contributing

When adding new features:

1. **Follow the component pattern**: New visualizations go in `components/`
2. **Use caching**: `@st.cache_data` for expensive operations
3. **Add error handling**: Graceful failures with clear messages
4. **Update this README**: Document new features and usage

## Architecture Principles

- **Static Data, Dynamic Inference**: Pre-compute expensive data, keep model inference fast
- **First Principles UI**: Answer "Is he good?" immediately, then provide depth
- **Scientific Rigor**: All visualizations provide proper context and normalization
- **Performance First**: Low latency even with large datasets
