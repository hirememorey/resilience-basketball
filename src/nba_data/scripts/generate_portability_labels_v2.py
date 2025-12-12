"""
Generate causal-ish portability labels (high/medium/low) using playoff vs RS deltas
and dependence/abdication signals.

Inputs:
- results/resilience_archetypes.csv (vol_ratio, eff_ratio)
- results/predictive_dataset.csv (dependence/context/abdication features)

Score construction (0..~1.2, then clipped to 0..1.2):
- base = min(vol_ratio, 1.2) * min(eff_ratio, 1.2)
- penalties:
  - assisted_pct_penalty = clip(ASSISTED_FGM_PCT - 0.50, 0, 0.5)
  - open_shot_penalty     = clip(OPEN_SHOT_FREQUENCY - 0.25, 0, 0.5)
  - abd_penalty           = clip(-LEVERAGE_USG_DELTA, 0, 0.3)
  - clutch_penalty        = clip(-LEVERAGE_TS_DELTA, 0, 0.3)
  -> base *= (1 - assisted_pct_penalty) * (1 - open_shot_penalty)
  -> base *= (1 - abd_penalty) * (1 - clutch_penalty)
- portable creation/pressure bump:
  if CREATION_VOLUME_RATIO >= 0.60 and rim_appetite >= 0.25 (if available):
      base = min(base + 0.05, 1.2)
- final score clipped to [0, 1.2]

Classes:
- high:   score >= 0.95 and vol_ratio >= 0.90 and eff_ratio >= 0.95
          and assisted_fgm_pct <= 0.55 and open_shot_freq <= 0.30
          and (rim_appetite missing or rim_appetite >= 0.22)
- medium: score >= 0.80
- low:    else

Outputs: results/portability_labels_v2.csv with score and component columns.
"""

import pandas as pd
from pathlib import Path


def clip(val, lo, hi):
    return max(lo, min(hi, val))


def compute_portability(row):
    vol = float(row.get("vol_ratio", 0) or 0)
    eff = float(row.get("eff_ratio", 0) or 0)
    assisted = float(row.get("ASSISTED_FGM_PCT", 0) or 0)
    open_shot = float(row.get("OPEN_SHOT_FREQUENCY", 0) or 0)
    lev_usg = float(row.get("LEVERAGE_USG_DELTA", 0) or 0)
    lev_ts = float(row.get("LEVERAGE_TS_DELTA", 0) or 0)
    creation_vol = float(row.get("CREATION_VOLUME_RATIO", 0) or 0)
    rim_appetite = row.get("RS_RIM_APPETITE", None)
    if rim_appetite is None:
        rim_appetite = row.get("RIM_APPETITE", None)
    rim_appetite = float(rim_appetite or 0)

    base = min(vol, 1.2) * min(eff, 1.2)

    assisted_pen = clip(assisted - 0.50, 0, 0.5)
    open_pen = clip(open_shot - 0.25, 0, 0.5)
    abd_pen = clip(-lev_usg, 0, 0.3)
    clutch_pen = clip(-lev_ts, 0, 0.3)

    base *= (1 - assisted_pen) * (1 - open_pen)
    base *= (1 - abd_pen) * (1 - clutch_pen)

    if creation_vol >= 0.60 and rim_appetite >= 0.25:
        base = min(base + 0.05, 1.2)

    score = clip(base, 0, 1.2)

    # Class thresholds
    if (
        score >= 0.95
        and vol >= 0.90
        and eff >= 0.95
        and assisted <= 0.55
        and open_shot <= 0.30
        and (rim_appetite == 0 or rim_appetite >= 0.22)
    ):
        cls = "high"
    elif score >= 0.80:
        cls = "medium"
    else:
        cls = "low"

    return cls, score, {
        "vol_ratio": vol,
        "eff_ratio": eff,
        "assisted_fgm_pct": assisted,
        "open_shot_frequency": open_shot,
        "leverage_usg_delta": lev_usg,
        "leverage_ts_delta": lev_ts,
        "creation_volume_ratio": creation_vol,
        "rim_appetite": rim_appetite,
    }


def main():
    root = Path(__file__).resolve().parents[3]
    arche_path = root / "results" / "resilience_archetypes.csv"
    feat_path = root / "results" / "predictive_dataset.csv"
    out_path = root / "results" / "portability_labels_v2.csv"

    df_arche = pd.read_csv(arche_path)
    df_feat = pd.read_csv(feat_path)

    # Keep only needed columns from features
    cols_needed = [
        "PLAYER_NAME",
        "SEASON",
        "ASSISTED_FGM_PCT",
        "OPEN_SHOT_FREQUENCY",
        "LEVERAGE_USG_DELTA",
        "LEVERAGE_TS_DELTA",
        "CREATION_VOLUME_RATIO",
        "RS_RIM_APPETITE",
        "RIM_APPETITE",
    ]
    df_feat_sub = df_feat[[c for c in cols_needed if c in df_feat.columns]].copy()

    df = pd.merge(df_arche, df_feat_sub, on=["PLAYER_NAME", "SEASON"], how="inner")

    records = []
    for _, row in df.iterrows():
        cls, score, comps = compute_portability(row)
        rec = {
            "PLAYER_NAME": row["PLAYER_NAME"],
            "SEASON": row["SEASON"],
            "PORTABILITY_CLASS": cls,
            "PORTABILITY_SCORE": score,
        }
        rec.update(comps)
        records.append(rec)

    out_df = pd.DataFrame(records)
    out_df.to_csv(out_path, index=False)
    print(f"Wrote portability labels to {out_path} ({len(out_df)} rows)")
    print(out_df["PORTABILITY_CLASS"].value_counts())


if __name__ == "__main__":
    main()
