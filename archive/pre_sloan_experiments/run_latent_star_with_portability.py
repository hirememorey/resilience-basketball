"""
Evaluate latent star cases with a portability-aware post-processor.

Logic:
- Get baseline archetype prediction via ConditionalArchetypePredictor.
- Compute portability score/class per player using the causal v2 rule:
    score = vol*eff (capped) with penalties for assisted reliance, open-shot reliance,
    abdication (USG drop), clutch collapse (TS drop), plus a small bump for portable
    creation+rimp pressure. Same thresholds as generate_portability_labels_v2.py.
- Post-process:
    If predicted archetype in {King, Bulldozer} and portability_class == "low":
        downgrade to Victim
    If predicted archetype == King and portability_class == "medium":
        downgrade to Bulldozer
- Report matches vs expected_outcome from test_latent_star_cases.
"""

import sys
from pathlib import Path
from typing import Tuple
import logging

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from predict_conditional_archetype import ConditionalArchetypePredictor  # noqa: E402

# Import test cases via absolute path to avoid module resolution issues
REPO_ROOT = Path(__file__).resolve().parents[3]
TEST_PATH = REPO_ROOT / "tests" / "validation" / "test_latent_star_cases.py"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tests" / "validation"))
from test_latent_star_cases import get_test_cases  # type: ignore  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def clip(val, lo, hi):
    return max(lo, min(hi, val))


def compute_portability(data: dict) -> Tuple[str, float]:
    vol = float(data.get("vol_ratio", data.get("PO_VOL_75", 0) / data.get("RS_VOL_75", 1) if data.get("RS_VOL_75") else 0) or 0)
    eff = float(data.get("eff_ratio", data.get("po_ts_pct_calc", 0) / data.get("rs_ts_pct_calc", 1) if data.get("rs_ts_pct_calc") else 0) or 0)
    assisted = float(data.get("ASSISTED_FGM_PCT", data.get("ASSISTED_FG_PCT", 0)) or 0)
    open_shot = float(data.get("OPEN_SHOT_FREQUENCY", data.get("RS_OPEN_SHOT_FREQUENCY", 0)) or 0)
    lev_usg = float(data.get("LEVERAGE_USG_DELTA", 0) or 0)
    lev_ts = float(data.get("LEVERAGE_TS_DELTA", 0) or 0)
    creation_vol = float(data.get("CREATION_VOLUME_RATIO", 0) or 0)
    rim_appetite = float(data.get("RS_RIM_APPETITE", data.get("RIM_APPETITE", 0)) or 0)

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

    return cls, score


def post_process(archetype: str, portability_class: str) -> str:
    if archetype in ["King (Resilient Star)", "Bulldozer (Fragile Star)"]:
        if portability_class == "low":
            return "Victim (Fragile Role)"
        if archetype == "King (Resilient Star)" and portability_class == "medium":
            return "Bulldozer (Fragile Star)"
    return archetype


def main():
    predictor = ConditionalArchetypePredictor()
    cases = get_test_cases()
    label_map = {
        "King": "King (Resilient Star)",
        "Bulldozer": "Bulldozer (Fragile Star)",
        "Sniper": "Sniper (Resilient Role)",
        "Victim": "Victim (Fragile Role)",
    }

    results = []
    rows = []
    for case in cases:
        data = predictor.get_player_data(case.name, case.season)
        if data is None:
            results.append((case, None, None, None, "not_found"))
            continue
        usage = case.test_usage or data.get("USG_PCT", 0.25)
        pred = predictor.predict_archetype_at_usage(data, usage)
        base_arch = pred.get("archetype") or pred.get("predicted_archetype")
        port_cls, port_score = compute_portability(data)
        adj_arch = post_process(base_arch, port_cls)
        results.append((case, base_arch, adj_arch, port_cls, "ok"))
        rows.append(
            {
                "player": case.name,
                "season": case.season,
                "expected": case.expected_outcome,
                "base": base_arch,
                "adjusted": adj_arch,
                "portability": port_cls,
                "usage": usage,
            }
        )

    total = len(results)
    passes_base = 0
    passes_adj = 0
    for case, base_arch, adj_arch, port_cls, status in results:
        if status != "ok":
            continue
        expected_full = label_map.get(case.expected_outcome, case.expected_outcome)
        if base_arch == expected_full:
            passes_base += 1
        if adj_arch == expected_full:
            passes_adj += 1

    logger.info(f"Cases evaluated: {total}")
    logger.info(f"Passes (baseline performance only): {passes_base}/{total}")
    logger.info(f"Passes (with portability post-process): {passes_adj}/{total}")

    # Detailed deltas for star predictions
    fp_downgrades = 0
    tp_drops = 0
    for case, base_arch, adj_arch, port_cls, status in results:
        if status != "ok":
            continue
        is_star_base = base_arch in ["King (Resilient Star)", "Bulldozer (Fragile Star)"]
        is_star_adj = adj_arch in ["King (Resilient Star)", "Bulldozer (Fragile Star)"]
        expected_star = case.expected_outcome in ["King", "Bulldozer"]
        if is_star_base and not is_star_adj and not expected_star:
            fp_downgrades += 1
        if is_star_base and not is_star_adj and expected_star:
            tp_drops += 1
    logger.info(f"Star→nonstar downgrades on non-star expectations (helpful FPs reduced): {fp_downgrades}")
    logger.info(f"Star→nonstar downgrades on star expectations (TP lost risk): {tp_drops}")

    # Emit a concise table for debugging
    header = ["player", "season", "expected", "base", "adjusted", "portability"]
    lines = []
    for r in rows:
        lines.append("\t".join(str(r[h]) for h in header))
    logger.info("Per-case predictions (expected | base -> adjusted | portability):")
    logger.info("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
