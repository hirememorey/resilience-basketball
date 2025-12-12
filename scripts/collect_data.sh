#!/bin/bash
# NBA Playoff Resilience Engine - Data Collection Script
# Collects all required data from NBA APIs and sources

set -e  # Exit on any error

echo "📊 NBA Playoff Resilience Engine - Data Collection"
echo "================================================="

# Check if we're in the right directory
if [ ! -f "docs/README.md" ]; then
    echo "❌ Error: Run this script from the project root directory"
    exit 1
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found. Continuing with system Python..."
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Default values
WORKERS=8
SEASONS="2015-16 2016-17 2017-18 2018-19 2019-20 2020-21 2021-22 2022-23 2023-24"
OVERWRITE=false
USE_CACHE=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --workers)
      WORKERS="$2"
      shift 2
      ;;
    --seasons)
      SEASONS="$2"
      shift 2
      ;;
    --overwrite)
      OVERWRITE=true
      shift
      ;;
    --no-cache)
      USE_CACHE=false
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  --workers N       Number of parallel workers (default: 8)"
      echo "  --seasons 'S...'  Seasons to collect (default: 2015-16 to 2023-24)"
      echo "  --overwrite       Overwrite existing data"
      echo "  --no-cache        Don't use cached data"
      echo "  --help           Show this help"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

echo "🔧 Configuration:"
echo "   Workers: $WORKERS"
echo "   Seasons: $SEASONS"
echo "   Overwrite: $OVERWRITE"
echo "   Use cache: $USE_CACHE"
echo ""

# Function to run data collection step
run_collection_step() {
    local step_name="$1"
    local command="$2"

    echo "📥 $step_name..."
    if eval "$command"; then
        echo "✅ $step_name completed"
    else
        echo "❌ $step_name failed"
        return 1
    fi
}

# Create necessary directories
mkdir -p data/cache
mkdir -p logs

# Step 1: Collect regular season stats
run_collection_step \
    "Regular Season Stats" \
    "python -m src.data.collector --seasons '$SEASONS' --workers $WORKERS --regular-season"

# Step 2: Collect playoff data
run_collection_step \
    "Playoff Data" \
    "python -m src.data.collector --seasons '$SEASONS' --workers $WORKERS --playoffs"

# Step 3: Collect shot charts
run_collection_step \
    "Shot Charts" \
    "python -m src.data.collector --seasons '$SEASONS' --workers $WORKERS --shot-charts"

# Step 4: Collect shot quality data
run_collection_step \
    "Shot Quality Data" \
    "python -m src.data.collector --seasons '$SEASONS' --workers $WORKERS --shot-quality"

# Step 5: Validate data completeness
echo "🔍 Validating data completeness..."
python -c "
import sys
sys.path.insert(0, 'src')
from src.utils.validation import validate_data_completeness

try:
    results = validate_data_completeness()
    print(f'✅ Data completeness: {results[\"overall_completeness\"]:.1%}')
    print(f'   Players: {results[\"total_players\"]}')
    print(f'   Seasons: {results[\"total_seasons\"]}')

    if results['overall_completeness'] < 0.8:
        print('⚠️  Data completeness is low. Some predictions may be unreliable.')
        print('   Run with --overwrite to re-collect missing data.')
    else:
        print('✅ Data completeness is good!')
except Exception as e:
    print(f'❌ Data validation failed: {e}')
    exit 1
"

# Step 6: Generate predictive dataset
echo "🔬 Generating predictive dataset..."
if python -c "
import sys
sys.path.insert(0, 'src')
from src.data.storage import generate_predictive_dataset

try:
    dataset = generate_predictive_dataset()
    print(f'✅ Predictive dataset generated: {len(dataset)} player-seasons')
    print(f'   Saved to: data/processed/predictive_dataset.csv')
except Exception as e:
    print(f'❌ Predictive dataset generation failed: {e}')
    exit 1
"; then
    echo "✅ Predictive dataset generated"
else
    echo "❌ Predictive dataset generation failed"
    exit 1
fi

echo ""
echo "🎉 Data collection complete!"
echo "==========================="
echo ""
echo "Generated files:"
echo "- data/processed/predictive_dataset.csv (main dataset)"
echo "- data/raw/nba_api/ (raw API responses)"
echo "- data/raw/shot_charts/ (spatial shooting data)"
echo "- data/interim/features/ (calculated features)"
echo ""
echo "Next steps:"
echo "1. Train model: ./scripts/train_model.sh"
echo "2. Validate: python scripts/validate.py"
echo "3. Make predictions: python scripts/predict.py --player \"Luka Dončić\" --season \"2023-24\""
echo ""
echo "To re-run with different settings:"
echo "./scripts/collect_data.sh --workers 4 --seasons \"2023-24\""
echo ""
echo "Happy analyzing! 📊"
