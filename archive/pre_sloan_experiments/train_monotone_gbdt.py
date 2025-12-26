"""
Experimental monotone-constrained GBDT with FP-focused interactions.

Features:
- Base Phoenix RFE feature set (15 forced-in features)
- Added interactions:
  - USG_PCT_X_RS_OPEN_SHOT_FREQUENCY (volume-weighted open-shot reliance)
  - RIM_PRESSURE_DEFICIT (20th pct creators)
  - USG_PCT_X_RIM_PRESSURE_DEFICIT

Split: temporal (train <=2020 seasons, test >2020).
Metrics: overall accuracy, FP star vs Victim, FP star vs high-usage Victim, TP star vs stars.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

sys.path.insert(0, str(Path(__file__).parent))
from train_rfe_model import RFEModelTrainer  # noqa: E402


def parse_season_year(season_str):
    try:
        if isinstance(season_str, str):
            return int(season_str.split("-")[0])
    except Exception:
        return 0
    return 0


def main():
    trainer = RFEModelTrainer()

    # Base Phoenix features + added FP-focused interactions
    base_feats = trainer.load_rfe_features(n_features=15, add_dependence_feats=True)
    extra_feats = [
        "USG_PCT_X_RS_OPEN_SHOT_FREQUENCY",
        "RIM_PRESSURE_DEFICIT",
        "USG_PCT_X_RIM_PRESSURE_DEFICIT",
    ]
    requested_features = list(dict.fromkeys(base_feats + extra_feats))

    df = trainer.load_and_merge_data()
    X, feature_names = trainer.prepare_features(
        df, requested_features, add_dependence_feats=True
    )
    y = df["ARCHETYPE"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # Temporal split (train <=2020, test >2020)
    df["_SEASON_YEAR"] = df["SEASON"].apply(parse_season_year)
    split_year = 2020
    train_mask = df["_SEASON_YEAR"] <= split_year
    test_mask = df["_SEASON_YEAR"] > split_year

    X_train = X.loc[train_mask].fillna(0)
    X_test = X.loc[test_mask].fillna(0)
    y_train = y_encoded[train_mask]
    y_test = y_encoded[test_mask]
    y_train_raw = y[train_mask]
    y_test_raw = y[test_mask]

    # Class weights favoring Victim to reduce FPs
    class_weights = {
        "King (Resilient Star)": 1.0,
        "Bulldozer (Fragile Star)": 1.0,
        "Sniper (Resilient Role)": 1.0,
        "Victim (Fragile Role)": 1.5,
    }
    cw_encoded = {le.transform([cls])[0]: w for cls, w in class_weights.items() if cls in le.classes_}
    sample_weights = y_train.copy().astype(float)
    for idx, label in enumerate(y_train):
        sample_weights[idx] = cw_encoded.get(label, 1.0)

    # Monotone constraints map (positive=1, negative=-1, neutral=0)
    mono_map = {
        "TS_PCT_VS_USAGE_BAND_EXPECTATION": 1,
        "USG_PCT": 1,
        "USG_PCT_X_TS_PCT_VS_USAGE_BAND_EXPECTATION": 1,
        "USG_PCT_X_RS_PRESSURE_APPETITE": 1,
        "USG_PCT_X_RS_LATE_CLOCK_PRESSURE_RESILIENCE": 1,
        "USG_PCT_X_EFG_ISO_WEIGHTED": 1,
        "PREV_EFG_ISO_WEIGHTED": 1,
        "PREV_RS_RIM_APPETITE": 1,
        "SKILL_MATURITY_INDEX": 1,
        "USG_PCT_X_INEFFICIENT_VOLUME_SCORE": -1,
        "CLUTCH_X_TS_FLOOR_GAP": -1,
        "USG_PCT_X_TS_FLOOR_GAP": -1,
        "TS_FLOOR_GAP": -1,
        "USG_PCT_X_RS_OPEN_SHOT_FREQUENCY": -1,
        "RIM_PRESSURE_DEFICIT": -1,
        "USG_PCT_X_RIM_PRESSURE_DEFICIT": -1,
    }
    monotone_constraints = [mono_map.get(f, 0) for f in feature_names]

    model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=len(le.classes_),
        n_estimators=300,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="mlogloss",
        random_state=42,
        monotone_constraints=tuple(monotone_constraints),
    )

    model.fit(X_train, y_train, sample_weight=sample_weights)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=le.classes_, digits=3)

    # FP/TP diagnostics
    star_labels = {"King (Resilient Star)", "Bulldozer (Fragile Star)"}
    star_indices = {le.transform([lbl])[0] for lbl in star_labels if lbl in le.classes_}
    pred_star = pd.Series([p in star_indices for p in y_pred], index=X_test.index)
    actual_victim = pd.Series([cls == "Victim (Fragile Role)" for cls in y_test_raw], index=X_test.index)
    actual_star = pd.Series([cls in star_labels for cls in y_test_raw], index=X_test.index)

    fp_star = int((pred_star & actual_victim).sum())
    victim_count = int(actual_victim.sum())
    fp_star_rate = fp_star / victim_count if victim_count else float("nan")

    # High-usage victim FP rate
    usg_test = df.loc[test_mask, "USG_PCT"]
    if usg_test.max() > 1.0:
        usg_test = usg_test / 100.0
    high_usage_victim = actual_victim & (usg_test > 0.25)
    fp_high_usage = int((pred_star & high_usage_victim).sum())
    high_usage_count = int(high_usage_victim.sum())
    fp_high_usage_rate = fp_high_usage / high_usage_count if high_usage_count else float("nan")

    tp_star = int((pred_star & actual_star).sum())
    star_count = int(actual_star.sum())
    tp_star_rate = tp_star / star_count if star_count else float("nan")

    print("Monotone GBDT (Phoenix+FP interactions)")
    print(f"Features used: {len(feature_names)} -> {feature_names}")
    print(f"Accuracy: {acc:.4f}")
    print("Confusion matrix (rows=true, cols=pred):")
    print(cm)
    print("\nClassification report:\n", report)
    print(f"FP star vs Victim: {fp_star}/{victim_count} ({fp_star_rate*100:.1f}% if defined)")
    print(f"FP star vs high-usage Victim: {fp_high_usage}/{high_usage_count} ({fp_high_usage_rate*100:.1f}% if defined)")
    print(f"TP star vs star labels: {tp_star}/{star_count} ({tp_star_rate*100:.1f}% if defined)")


if __name__ == "__main__":
    main()

