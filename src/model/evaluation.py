"""
Model evaluation module for NBA Playoff Resilience Engine.
Handles model validation, metrics calculation, and performance analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
import logging
from pathlib import Path

try:
    from sklearn.metrics import (
        accuracy_score, f1_score, precision_score, recall_score,
        classification_report, confusion_matrix
    )
except ImportError:
    # Fallback if sklearn not available
    pass

logger = logging.getLogger(__name__)


def evaluate_model_performance(
    model,
    encoder,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    detailed: bool = True
) -> Dict:
    """
    Comprehensive model evaluation.

    Args:
        model: Trained model
        encoder: Label encoder
        X_test: Test features
        y_test: Test labels
        detailed: Whether to include detailed metrics

    Returns:
        Dictionary of evaluation metrics
    """
    try:
        # Make predictions
        y_pred = model.predict(X_test)

        # Basic metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred, average='weighted'),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'test_samples': len(X_test),
            'n_features': X_test.shape[1]
        }

        if detailed:
            # Classification report
            report = classification_report(y_test, y_pred, output_dict=True)
            metrics['classification_report'] = report

            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            metrics['confusion_matrix'] = cm.tolist()

            # Feature importance (if available)
            if hasattr(model, 'feature_importances_'):
                feature_names = getattr(X_test, 'columns', [f'feature_{i}' for i in range(X_test.shape[1])])
                feature_importance = dict(zip(feature_names, model.feature_importances_))
                metrics['feature_importance'] = feature_importance

        logger.info(f"Model evaluation complete: {metrics['accuracy']:.1%} accuracy")

        return metrics

    except Exception as e:
        logger.error(f"Model evaluation failed: {e}")
        return {'error': str(e)}


def validate_latent_star_cases(model, encoder) -> Dict:
    """
    Validate model against known latent star test cases.

    Args:
        model: Trained model
        encoder: Label encoder

    Returns:
        Validation results dictionary
    """
    # This would contain the 32 critical test cases
    # For now, return a placeholder structure
    return {
        'test_name': 'latent_star_cases',
        'total_cases': 0,
        'passed_cases': 0,
        'pass_rate': 0.0,
        'results': [],
        'note': 'Test cases validation not yet implemented in new structure'
    }


def analyze_model_errors(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    y_pred: pd.Series
) -> Dict:
    """
    Analyze model errors and failure patterns.

    Args:
        model: Trained model
        X_test: Test features
        y_test: True labels
        y_pred: Predicted labels

    Returns:
        Error analysis dictionary
    """
    errors = X_test[y_test != y_pred].copy()
    error_labels = y_test[y_test != y_pred]
    error_predictions = y_pred[y_test != y_pred]

    analysis = {
        'total_errors': len(errors),
        'error_rate': len(errors) / len(X_test),
        'error_breakdown': {}
    }

    # Analyze errors by true label
    for true_label in error_labels.unique():
        mask = error_labels == true_label
        error_preds = error_predictions[mask]

        analysis['error_breakdown'][true_label] = {
            'count': len(error_preds),
            'most_common_wrong_prediction': error_preds.mode().iloc[0] if len(error_preds) > 0 else None
        }

    return analysis


def compare_models(model1, model2, X_test, y_test, model1_name="Model 1", model2_name="Model 2") -> Dict:
    """
    Compare two models on the same test set.

    Args:
        model1: First model
        model2: Second model
        X_test: Test features
        y_test: Test labels
        model1_name: Name for first model
        model2_name: Name for second model

    Returns:
        Comparison dictionary
    """
    # Evaluate both models
    results1 = evaluate_model_performance(model1, None, X_test, y_test, detailed=False)
    results2 = evaluate_model_performance(model2, None, X_test, y_test, detailed=False)

    comparison = {
        'models': [model1_name, model2_name],
        model1_name: results1,
        model2_name: results2,
        'winner': model1_name if results1['accuracy'] > results2['accuracy'] else model2_name,
        'accuracy_difference': results1['accuracy'] - results2['accuracy']
    }

    return comparison
