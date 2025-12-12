"""
Model training module for NBA Playoff Resilience Engine.
Handles model training, hyperparameter tuning, and feature selection.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
import logging
from pathlib import Path
import joblib

try:
    from xgboost import XGBClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import classification_report
except ImportError:
    XGBClassifier = None

logger = logging.getLogger(__name__)


class ResilienceModelTrainer:
    """Trainer for resilience prediction models."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Get default training configuration."""
        return {
            'model_type': 'xgboost',
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'objective': 'multi:softprob',
            'num_class': 4,
            'random_state': 42
        }

    def train_full_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        feature_names: List[str]
    ) -> Tuple[XGBClassifier, object]:
        """
        Train full XGBoost model with all features.

        Args:
            X_train: Training features
            y_train: Training labels
            feature_names: Feature names

        Returns:
            Tuple of (trained_model, label_encoder)
        """
        if XGBClassifier is None:
            raise ImportError("XGBoost not available. Install with: pip install xgboost")

        logger.info(f"Training full model with {len(feature_names)} features")

        # Create and train model
        model = XGBClassifier(**self.config)
        model.fit(X_train, y_train)

        # Create simple label encoder (archetype -> int)
        unique_labels = sorted(y_train.unique())
        label_encoder = {label: i for i, label in enumerate(unique_labels)}
        label_decoder = {i: label for label, i in label_encoder.items()}

        # Add decoder to encoder for convenience
        label_encoder['decoder'] = label_decoder

        logger.info(f"Model trained. Classes: {unique_labels}")

        return model, label_encoder

    def perform_rfe_selection(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        feature_names: List[str],
        n_features: int = 10
    ) -> Tuple[object, object, List[str], Dict]:
        """
        Perform Recursive Feature Elimination to select optimal features.

        Args:
            X: Feature matrix
            y: Target labels
            feature_names: Feature names
            n_features: Number of features to select

        Returns:
            Tuple of (model, encoder, selected_features, rfe_results)
        """
        try:
            from sklearn.feature_selection import RFE
        except ImportError:
            raise ImportError("scikit-learn not available")

        logger.info(f"Performing RFE selection: {len(feature_names)} features → {n_features} features")

        # Create base model
        base_model = XGBClassifier(**{k: v for k, v in self.config.items() if k != 'num_class'})

        # Perform RFE
        rfe = RFE(estimator=base_model, n_features_to_select=n_features)
        rfe.fit(X, y)

        # Get selected features
        selected_features = [feature_names[i] for i in range(len(feature_names)) if rfe.support_[i]]

        # Train final model with selected features
        X_selected = X[selected_features]
        model, encoder = self.train_full_model(X_selected, y, selected_features)

        # Collect RFE results
        rfe_results = {
            'n_features_selected': n_features,
            'selected_features': selected_features,
            'feature_ranking': dict(zip(feature_names, rfe.ranking_)),
            'support_mask': rfe.support_.tolist()
        }

        logger.info(f"RFE complete. Selected features: {selected_features}")

        return model, encoder, selected_features, rfe_results

    def evaluate_model(
        self,
        model: XGBClassifier,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> Dict:
        """
        Evaluate trained model performance.

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels

        Returns:
            Evaluation metrics dictionary
        """
        try:
            from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
        except ImportError:
            raise ImportError("scikit-learn not available")

        # Make predictions
        y_pred = model.predict(X_test)

        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred, average='weighted'),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'test_samples': len(X_test)
        }

        # Per-class metrics
        report = classification_report(y_test, y_pred, output_dict=True)
        metrics['per_class'] = report

        logger.info(f"Model evaluation: Accuracy={metrics['accuracy']:.1%}")

        return metrics
