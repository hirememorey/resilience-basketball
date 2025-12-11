"""
Impute Missing TS_PCT Values

This script creates a regression model to predict TS_PCT from available features
for players missing TS_PCT data, enabling full coverage for EFFICIENCY_SCORE_VS_EXPECTED.

Strategy:
1. Train regression model on players with TS_PCT data
2. Use model to predict TS_PCT for players without it
3. Merge imputed values back into predictive dataset

Features used for imputation:
- EFG_ISO_WEIGHTED (moderate correlation: 0.357)
- USG_PCT (usage impacts efficiency expectations)
- AGE (experience affects efficiency)
- CREATION_TAX (creation efficiency vs volume)
- LEVERAGE_TS_DELTA (if available)

Usage: python impute_ts_pct.py
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/ts_pct_imputation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TS_PCT_Imputer:
    """Impute missing TS_PCT values using regression modeling."""

    def __init__(self):
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.imputation_features = [
            'EFG_ISO_WEIGHTED',
            'USG_PCT',
            'AGE',
            'CREATION_TAX',
            'LEVERAGE_TS_DELTA'  # Include if available
        ]

    def load_data(self):
        """Load predictive dataset."""
        logger.info("Loading predictive dataset...")

        dataset_path = self.results_dir / "predictive_dataset.csv"
        if not dataset_path.exists():
            raise FileNotFoundError(f"Predictive dataset not found at {dataset_path}")

        self.df = pd.read_csv(dataset_path)
        logger.info(f"Loaded {len(self.df)} player-seasons")

        # Check current TS_PCT coverage
        ts_pct_count = self.df['TS_PCT'].notna().sum()
        coverage_pct = (ts_pct_count / len(self.df) * 100).round(1)
        logger.info(f"Current TS_PCT coverage: {ts_pct_count}/{len(self.df)} ({coverage_pct}%)")

    def prepare_imputation_data(self):
        """Prepare data for imputation modeling."""
        logger.info("Preparing imputation data...")

        # Split into training and prediction sets
        train_mask = self.df['TS_PCT'].notna()
        predict_mask = self.df['TS_PCT'].isna()

        self.df_train = self.df[train_mask].copy()
        self.df_predict = self.df[predict_mask].copy()

        logger.info(f"Training set: {len(self.df_train)} players with TS_PCT")
        logger.info(f"Prediction set: {len(self.df_predict)} players needing imputation")

        # Prepare features for training
        feature_cols = []
        for feature in self.imputation_features:
            if feature in self.df_train.columns:
                non_na_count = self.df_train[feature].notna().sum()
                if non_na_count > len(self.df_train) * 0.8:  # At least 80% coverage
                    feature_cols.append(feature)
                    logger.info(f"Using feature: {feature} ({non_na_count}/{len(self.df_train)} non-null)")
                else:
                    logger.warning(f"Skipping feature {feature}: only {non_na_count}/{len(self.df_train)} non-null")

        self.feature_cols = feature_cols

        # Handle missing values in features (use median imputation for training features)
        for col in feature_cols:
            if self.df_train[col].isna().any():
                median_val = self.df_train[col].median()
                self.df_train[col] = self.df_train[col].fillna(median_val)
                logger.info(f"Imputed missing {col} with median: {median_val:.3f}")

        # Prepare training data
        X_train = self.df_train[feature_cols]
        y_train = self.df_train['TS_PCT']

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)

        return X_train_scaled, y_train

    def train_imputation_model(self, X_train, y_train):
        """Train regression model for TS_PCT imputation."""
        logger.info("Training TS_PCT imputation model...")

        # Split training data for validation
        X_train_split, X_val, y_train_split, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )

        # Train Random Forest (good for this type of regression)
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )

        self.model.fit(X_train_split, y_train_split)

        # Evaluate on validation set
        y_pred_val = self.model.predict(X_val)
        mse = mean_squared_error(y_val, y_pred_val)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_val, y_pred_val)

        logger.info(f"Validation Results:")
        logger.info(f"  RMSE: {rmse:.4f}")
        logger.info(f"  R²: {r2:.4f}")
        logger.info(f"  Mean actual TS_PCT: {y_val.mean():.3f}")
        logger.info(f"  Std actual TS_PCT: {y_val.std():.3f}")

        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        logger.info("Feature Importance:")
        for _, row in feature_importance.iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")

    def impute_missing_values(self):
        """Impute TS_PCT for players missing this data."""
        logger.info("Imputing missing TS_PCT values...")

        # Prepare prediction features
        X_predict = self.df_predict[self.feature_cols].copy()

        # Handle missing values in prediction features (use training medians)
        for col in self.feature_cols:
            if X_predict[col].isna().any():
                # Use the median from training data
                train_median = self.df_train[col].median()
                na_count = X_predict[col].isna().sum()
                X_predict[col] = X_predict[col].fillna(train_median)
                logger.info(f"Imputed {na_count} missing {col} values with training median: {train_median:.3f}")

        # Scale prediction features
        X_predict_scaled = self.scaler.transform(X_predict)

        # Make predictions
        imputed_ts_pct = self.model.predict(X_predict_scaled)

        # Add predictions to dataframe
        self.df_predict['TS_PCT_imputed'] = imputed_ts_pct
        self.df_predict['TS_PCT'] = imputed_ts_pct  # Replace NaN with imputed values

        logger.info(f"Imputed TS_PCT for {len(imputed_ts_pct)} players")
        logger.info(f"Imputed TS_PCT range: {imputed_ts_pct.min():.3f} - {imputed_ts_pct.max():.3f}")
        logger.info(f"Imputed TS_PCT mean: {imputed_ts_pct.mean():.3f}")

        # Quality check: compare imputed values to training distribution
        logger.info("Quality check - imputed vs training TS_PCT:")
        logger.info(f"  Training mean: {self.df_train['TS_PCT'].mean():.3f}")
        logger.info(f"  Imputed mean: {imputed_ts_pct.mean():.3f}")
        logger.info(f"  Training std: {self.df_train['TS_PCT'].std():.3f}")
        logger.info(f"  Imputed std: {np.std(imputed_ts_pct):.3f}")

    def update_predictive_dataset(self):
        """Update the predictive dataset with imputed TS_PCT values."""
        logger.info("Updating predictive dataset with imputed values...")

        # Combine training data (unchanged) with imputed data
        df_combined = pd.concat([self.df_train, self.df_predict], ignore_index=True)

        # Sort by original index to maintain order
        df_combined = df_combined.sort_index()

        # Verify we have full coverage now
        final_coverage = df_combined['TS_PCT'].notna().sum()
        final_coverage_pct = (final_coverage / len(df_combined) * 100).round(1)
        logger.info(f"Final TS_PCT coverage: {final_coverage}/{len(df_combined)} ({final_coverage_pct}%)")

        # Save updated dataset
        output_path = self.results_dir / "predictive_dataset.csv"
        df_combined.to_csv(output_path, index=False)
        logger.info(f"Updated predictive dataset saved to {output_path}")

        # Also save a version with imputation flag for analysis
        df_combined['TS_PCT_is_imputed'] = df_combined['TS_PCT_imputed'].notna()
        analysis_path = self.results_dir / "predictive_dataset_with_ts_pct_imputation.csv"
        df_combined.to_csv(analysis_path, index=False)
        logger.info(f"Analysis version saved to {analysis_path}")

    def run(self):
        """Run the complete TS_PCT imputation pipeline."""
        logger.info("Starting TS_PCT imputation process...")

        self.load_data()
        X_train, y_train = self.prepare_imputation_data()
        self.train_imputation_model(X_train, y_train)
        self.impute_missing_values()
        self.update_predictive_dataset()

        logger.info("✅ TS_PCT imputation completed successfully!")


def main():
    try:
        imputer = TS_PCT_Imputer()
        imputer.run()
    except Exception as e:
        logger.error(f"Error in TS_PCT imputation: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()