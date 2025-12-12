#!/bin/bash
# NBA Playoff Resilience Engine - Environment Setup Script
# This script sets up the complete development environment in one command

set -e  # Exit on any error

echo "🏀 NBA Playoff Resilience Engine - Environment Setup"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "docs/README.md" ]; then
    echo "❌ Error: Run this script from the project root directory"
    exit 1
fi

echo "📍 Project root detected: $(pwd)"

# Function to check command availability
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not found. Please install Python 3.8+"
    exit 1
fi

if ! command_exists pip; then
    echo "❌ pip is required but not found. Please install pip"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create required directories
echo "📁 Creating required directories..."
mkdir -p data/{raw/{nba_api,shot_charts,playbyplay},interim/{features,labels,projections},processed,external}
mkdir -p models/{production,staging,archive}
mkdir -p results/{experiments,reports,predictions,diagnostics}
mkdir -p logs

# Create .env file template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env template..."
    cat > .env << 'EOF'
# NBA Playoff Resilience Engine - Environment Variables
# Copy this file and fill in your values

# NBA API Configuration (optional - uses public API if not set)
# NBA_API_KEY=your_api_key_here

# Development settings
DEBUG=true
LOG_LEVEL=INFO

# Data collection settings
MAX_WORKERS=8
REQUEST_TIMEOUT=30

# Model settings
MODEL_CACHE_DIR=models/
DATA_CACHE_DIR=data/cache/
EOF
    echo "✅ Created .env template (edit with your API keys if needed)"
fi

# Run basic validation
echo "🔍 Running basic validation..."
python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import pandas as pd
    print(f'✅ pandas {pd.__version__}')
except ImportError:
    print('❌ pandas not installed')

try:
    import numpy as np
    print(f'✅ numpy {np.__version__}')
except ImportError:
    print('❌ numpy not installed')

try:
    import xgboost as xgb
    print(f'✅ xgboost {xgb.__version__}')
except ImportError:
    print('❌ xgboost not installed')

try:
    import sklearn
    print(f'✅ scikit-learn {sklearn.__version__}')
except ImportError:
    print('❌ scikit-learn not installed')

print('✅ Basic imports successful')
"

# Test basic functionality
echo "🧪 Testing basic functionality..."
if python -c "
import sys
sys.path.insert(0, 'src')
try:
    from src.config import get_config
    config = get_config()
    print('✅ Configuration system working')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    sys.exit(1)
"; then
    echo "✅ Basic functionality test passed"
else
    echo "❌ Basic functionality test failed"
    exit 1
fi

# Create data cache directory
mkdir -p data/cache

# Final instructions
echo ""
echo "🎉 Setup complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your NBA API key (optional)"
echo "2. Run data collection: ./scripts/collect_data.sh"
echo "3. Train a model: ./scripts/train_model.sh"
echo "4. Make predictions: python scripts/predict.py --player \"Luka Dončić\" --season \"2023-24\""
echo ""
echo "Useful commands:"
echo "- Validate setup: python scripts/validate.py"
echo "- Debug issues: python scripts/debug.py --diagnostic"
echo "- Get help: cat docs/README.md"
echo ""
echo "Happy predicting! 🏀"
