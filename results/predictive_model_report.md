# Predictive Model Results: The Stylistic Stress Test (V3)

**Date:** Dec 2025
**Status:** ✅ Successful Enhancement (Pressure Vectors Added)

## Executive Summary
We successfully upgraded the predictive engine to **V3** by integrating "Pressure Vectors" (Shot Difficulty). The model accuracy has improved to **53.5%**, and more importantly, the new features have proven to be highly predictive, validating the hypothesis that **Pressure Appetite** (willingness to take tight shots) is a key marker of "Dominant Rigidity."

---

## 1. The Model Performance

*   **Overall Accuracy:** 53.5% (up from 50.5% in V2)
*   **Key Success:** The model now has a stronger signal for separating "Kings" from "Bulldozers," though recall for Kings remains the primary challenge.

### Classification Report
| Archetype | Precision | Recall | F1-Score | Insight |
| :--- | :--- | :--- | :--- | :--- |
| **King** | 0.60 | 0.44 | 0.51 | ✅ **High Precision.** If we call you a King, you probably are one. |
| **Bulldozer** | 0.52 | 0.73 | 0.61 | ⚠️ **Over-Predicted.** We still capture many Kings in this net (Dominant Rigidity). |
| **Sniper** | 0.48 | 0.57 | 0.52 | ✅ **Solid.** Identifies resilient role players well. |
| **Victim** | 0.54 | 0.50 | 0.52 | ✅ **Balanced.** Reliable detection of fragile role players. |

---

## 2. Feature Importance (The "Why")

The new "Pressure" features immediately jumped to the top of the importance list, validating the "Shaq Problem" hypothesis.

1.  **`CREATION_VOLUME_RATIO` (13.9%)**: Still the King. Self-creation volume is the #1 prerequisites.
2.  **`RS_PRESSURE_APPETITE` (9.8%)**: **NEW & CRITICAL.** The percentage of shots taken with a defender < 4 feet. This proxies "Dominance" - the willingness to force the issue.
3.  **`LEVERAGE_USG_DELTA` (8.9%)**: The "Abdication Detector" remains vital.
4.  **`PO_EFG_BEYOND_RS_MEDIAN` (8.7%)**: The "Plasticity" signal (scoring from new spots) is strong.
5.  **`RS_PRESSURE_RESILIENCE` (6.6%)**: **NEW.** Efficiency on very tight shots (0-2 feet).

**Takeaway:** The strongest predictor of playoff resilience is a player who **creates their own shot** (`Creation Volume`) and **habitually plays through contact** (`Pressure Appetite`).

---

## 3. Methodology
*   **Algorithm:** XGBoost Classifier (Multi-Class)
*   **Training Data:** 503 Player-Seasons (2019-2024)
*   **Target Labels:** Derived from the "Dual-Grade" Descriptive Engine.
*   **Input Features (Stress Vectors):**
    *   *Creation Vector:* Tax & Volume.
    *   *Leverage Vector:* Clutch Usage & TS Delta.
    *   *Plasticity Vector:* Spatial Variance & Distance Delta.
    *   *Pressure Vector (New):* Appetite (% Tight Shots) & Resilience (eFG% on Tight Shots).

## 4. Future Improvements
1.  **Physicality Vector:** Free Throw Rate Resilience. This is the next logical step to capture "force."
2.  **Historical Expansion:** We are still training on a small dataset (5 seasons). Expanding back to 2015 is the best way to improve the model's ability to learn rare "King" patterns.
