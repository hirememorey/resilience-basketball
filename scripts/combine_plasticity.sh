#!/bin/bash
# Combine Plasticity Scores Script
# This script combines individual season plasticity files into the comprehensive dataset

cd "$(dirname "$0")/.."

echo "🔄 Combining plasticity scores from all seasons..."

# Run the combination script
python src/nba_data/scripts/combine_plasticity_scores.py

echo "✅ Plasticity combination complete!"
