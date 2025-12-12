#!/bin/bash
# NBA Playoff Resilience Engine - Model Training Script
# Trains the production model using latest data and best practices

set -e  # Exit on any error

echo "🤖 NBA Playoff Resilience Engine - Model Training"
echo "================================================"

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
MODEL_TYPE="rfe"  # rfe or full
N_FEATURES=15
EXPERIMENT_NAME=""
SKIP_VALIDATION=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --model-type)
      MODEL_TYPE="$2"
      shift 2
      ;;
    --features)
      N_FEATURES="$2"
      shift 2
      ;;
    --experiment)
      EXPERIMENT_NAME="$2"
      shift 2
      ;;
    --skip-validation)
      SKIP_VALIDATION=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  --model-type TYPE   Model type: 'rfe' (default) or 'full'"
      echo "  --features N        Number of features for RFE (default: 15)"
      echo "  --experiment NAME   Experiment name for tracking"
      echo "  --skip-validation   Skip post-training validation"
      echo "  --help             Show this help"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Generate experiment name if not provided
if [ -z "$EXPERIMENT_NAME" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    EXPERIMENT_NAME="${MODEL_TYPE}_${N_FEATURES}feat_${TIMESTAMP}"
fi

echo "🔧 Configuration:"
echo "   Model type: $MODEL_TYPE"
echo "   Features: $N_FEATURES"
echo "   Experiment: $EXPERIMENT_NAME"
echo "   Skip validation: $SKIP_VALIDATION"
echo ""

# Create experiment directory
EXPERIMENT_DIR="results/experiments/$EXPERIMENT_NAME"
mkdir -p "$EXPERIMENT_DIR"

echo "📁 Experiment directory: $EXPERIMENT_DIR"

# Check if data exists
if [ ! -f "data/processed/predictive_dataset.csv" ]; then
    echo "❌ Error: Predictive dataset not found. Run data collection first:"
    echo "   ./scripts/collect_data.sh"
    exit 1
fi

# Function to run training step
run_training_step() {
    local step_name="$1"
    local command="$2"

    echo "🔬 $step_name..."
    if eval "$command"; then
        echo "✅ $step_name completed"
    else
        echo "❌ $step_name failed"
        return 1
    fi
}

# Step 1: Prepare training data
run_training_step \
    "Preparing training data" \
    "python -c \"
import sys
sys.path.insert(0, 'src')
from src.data.storage import prepare_training_data

try:
    X_train, X_test, y_train, y_test, feature_names = prepare_training_data()
    print(f'✅ Training data prepared: {len(X_train)} train, {len(X_test)} test samples')
    print(f'   Features: {len(feature_names)}')
except Exception as e:
    print(f'❌ Training data preparation failed: {e}')
    exit(1)
\""

# Step 2: Train model
if [ "$MODEL_TYPE" = "rfe" ]; then
    run_training_step \
        "Training RFE model" \
        "python -c \"
import sys
sys.path.insert(0, 'src')
from src.model.trainer import ResilienceModelTrainer
import joblib
import pandas as pd

try:
    # Load training data
    from src.data.storage import prepare_training_data
    X_train, X_test, y_train, y_test, feature_names = prepare_training_data()

    # Train RFE model
    trainer = ResilienceModelTrainer({})
    model, encoder, selected_features, rfe_results = trainer.train_rfe_model(
        X_train, y_train, feature_names, n_features=$N_FEATURES
    )

    # Save model
    model_path = f'models/staging/resilience_xgb_rfe_${N_FEATURES}_${EXPERIMENT_NAME}.pkl'
    encoder_path = f'models/staging/archetype_encoder_rfe_${N_FEATURES}_${EXPERIMENT_NAME}.pkl'

    joblib.dump(model, model_path)
    joblib.dump(encoder, encoder_path)

    # Save metadata
    metadata = {
        'model_type': 'rfe',
        'n_features': $N_FEATURES,
        'selected_features': selected_features,
        'rfe_results': rfe_results,
        'experiment_name': '$EXPERIMENT_NAME',
        'training_samples': len(X_train),
        'feature_importance': dict(zip(selected_features, model.feature_importances_))
    }

    import json
    with open(f'models/staging/model_metadata_${EXPERIMENT_NAME}.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)

    print(f'✅ RFE model trained and saved to staging/')
    print(f'   Selected features: {len(selected_features)}')
    print(f'   Top features: {selected_features[:5]}')

except Exception as e:
    print(f'❌ RFE model training failed: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
\""
else
    run_training_step \
        "Training full model" \
        "python -c \"
import sys
sys.path.insert(0, 'src')
from src.model.trainer import ResilienceModelTrainer
import joblib

try:
    # Load training data
    from src.data.storage import prepare_training_data
    X_train, X_test, y_train, y_test, feature_names = prepare_training_data()

    # Train full model
    trainer = ResilienceModelTrainer({})
    model, encoder = trainer.train_full_model(X_train, y_train, feature_names)

    # Save model
    model_path = f'models/staging/resilience_xgb_full_${EXPERIMENT_NAME}.pkl'
    encoder_path = f'models/staging/archetype_encoder_full_${EXPERIMENT_NAME}.pkl'

    joblib.dump(model, model_path)
    joblib.dump(encoder, encoder_path)

    # Save metadata
    metadata = {
        'model_type': 'full',
        'experiment_name': '$EXPERIMENT_NAME',
        'training_samples': len(X_train),
        'total_features': len(feature_names),
        'feature_importance': dict(zip(feature_names, model.feature_importances_))
    }

    import json
    with open(f'models/staging/model_metadata_${EXPERIMENT_NAME}.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)

    print(f'✅ Full model trained and saved to staging/')

except Exception as e:
    print(f'❌ Full model training failed: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
\""
fi

# Step 3: Evaluate model
run_training_step \
    "Evaluating model" \
    "python -c \"
import sys
sys.path.insert(0, 'src')
from src.model.evaluation import evaluate_model_performance
import json

try:
    # Load the newly trained model
    import joblib
    if '$MODEL_TYPE' == 'rfe':
        model_path = f'models/staging/resilience_xgb_rfe_${N_FEATURES}_${EXPERIMENT_NAME}.pkl'
        encoder_path = f'models/staging/archetype_encoder_rfe_${N_FEATURES}_${EXPERIMENT_NAME}.pkl'
    else:
        model_path = f'models/staging/resilience_xgb_full_${EXPERIMENT_NAME}.pkl'
        encoder_path = f'models/staging/archetype_encoder_full_${EXPERIMENT_NAME}.pkl'

    model = joblib.load(model_path)
    encoder = joblib.load(encoder_path)

    # Evaluate
    from src.data.storage import prepare_training_data
    X_train, X_test, y_train, y_test, feature_names = prepare_training_data()

    results = evaluate_model_performance(model, encoder, X_test, y_test)

    # Save evaluation results
    with open(f'$EXPERIMENT_DIR/evaluation_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f'✅ Model evaluation completed')
    print(f'   Accuracy: {results.get(\"accuracy\", \"N/A\"):.1%}')
    print(f'   F1 Score: {results.get(\"f1_score\", \"N/A\"):.3f}')
    print(f'   Results saved to: $EXPERIMENT_DIR/evaluation_results.json')

except Exception as e:
    print(f'❌ Model evaluation failed: {e}')
    exit(1)
\""

# Step 4: Run validation (unless skipped)
if [ "$SKIP_VALIDATION" = false ]; then
    run_training_step \
        "Running validation suite" \
        "python scripts/validate.py --model-path models/staging/ --output $EXPERIMENT_DIR/validation_results.json"
fi

# Step 5: Generate experiment summary
echo "📊 Generating experiment summary..."
python -c "
import json
import os
from pathlib import Path

experiment_dir = Path('$EXPERIMENT_DIR')
summary = {
    'experiment_name': '$EXPERIMENT_NAME',
    'model_type': '$MODEL_TYPE',
    'n_features': $N_FEATURES,
    'timestamp': '$TIMESTAMP'
}

# Load evaluation results
eval_file = experiment_dir / 'evaluation_results.json'
if eval_file.exists():
    with open(eval_file) as f:
        summary['evaluation'] = json.load(f)

# Load validation results
val_file = experiment_dir / 'validation_results.json'
if val_file.exists():
    with open(val_file) as f:
        summary['validation'] = json.load(f)

# Load metadata
if '$MODEL_TYPE' == 'rfe':
    meta_file = Path(f'models/staging/model_metadata_${EXPERIMENT_NAME}.json')
else:
    meta_file = Path(f'models/staging/model_metadata_${EXPERIMENT_NAME}.json')

if meta_file.exists():
    with open(meta_file) as f:
        summary['metadata'] = json.load(f)

# Save summary
with open(experiment_dir / 'experiment_summary.json', 'w') as f:
    json.dump(summary, f, indent=2, default=str)

print('✅ Experiment summary generated')
print(f'   Location: $EXPERIMENT_DIR/experiment_summary.json')
"

echo ""
echo "🎉 Model training complete!"
echo "=========================="
echo ""
echo "Experiment: $EXPERIMENT_NAME"
echo "Location: $EXPERIMENT_DIR"
echo ""
echo "Generated files:"
echo "- models/staging/ (new model files)"
echo "- $EXPERIMENT_DIR/evaluation_results.json"
if [ "$SKIP_VALIDATION" = false ]; then
    echo "- $EXPERIMENT_DIR/validation_results.json"
fi
echo "- $EXPERIMENT_DIR/experiment_summary.json"
echo ""
echo "Next steps:"
echo "1. Review results: cat $EXPERIMENT_DIR/experiment_summary.json"
echo "2. Promote to production if good: cp models/staging/* models/production/"
echo "3. Make predictions: python scripts/predict.py --player \"Luka Dončić\" --season \"2023-24\""
echo ""
echo "To compare with production model:"
echo "python scripts/debug.py --model-comparison"
echo ""
echo "Happy modeling! 🤖"
