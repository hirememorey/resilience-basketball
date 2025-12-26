"""
Generate portability labels from playoff vs regular-season deltas.

Portability intuition (first principles):
- Portability ~ Efficiency x Volume under playoff pressure.
- If playoff volume holds and efficiency holds/improves, player is portable.
- If one collapses materially, player is fragile.

Heuristic (derived from resilience_archetypes.csv):
- vol_ratio: playoff volume vs RS (po_vol_75 / rs_vol_75 already provided as vol_ratio)
- eff_ratio: playoff TS vs RS (po_ts_pct_calc / rs_ts_pct_calc already provided as eff_ratio)
- portability_score = vol_ratio * eff_ratio (captures efficiency x volume)

Classes:
- High: portability_score >= 1.0 AND vol_ratio >= 0.90 AND eff_ratio >= 0.95
- Medium: portability_score >= 0.85
- Low: otherwise

Outputs: results/portability_labels.csv with columns:
PLAYER_NAME, SEASON, PORTABILITY_CLASS, PORTABILITY_SCORE, VOL_RATIO, EFF_RATIO
"""

import pandas as pd
from pathlib import Path


def compute_portability(row):
    vol = row.get("vol_ratio", 0.0)
    eff = row.get("eff_ratio", 0.0)
    score = vol * eff
    if score >= 1.0 and vol >= 0.90 and eff >= 0.95:
        cls = "high"
    elif score >= 0.85:
        cls = "medium"
    else:
        cls = "low"
    return cls, score, vol, eff


def main():
    root = Path(__file__).resolve().parents[3]
    src_path = root / "results" / "resilience_archetypes.csv"
    out_path = root / "results" / "portability_labels.csv"

    df = pd.read_csv(src_path)
    records = []
    for _, row in df.iterrows():
        cls, score, vol, eff = compute_portability(row)
        records.append(
            {
                "PLAYER_NAME": row["PLAYER_NAME"],
                "SEASON": row["SEASON"],
                "PORTABILITY_CLASS": cls,
                "PORTABILITY_SCORE": score,
                "VOL_RATIO": vol,
                "EFF_RATIO": eff,
            }
        )

    out_df = pd.DataFrame(records)
    out_df.to_csv(out_path, index=False)
    print(f"Wrote portability labels to {out_path} ({len(out_df)} rows)")
    print(out_df["PORTABILITY_CLASS"].value_counts())


if __name__ == "__main__":
    main()
