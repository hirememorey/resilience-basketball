# Predictive Model Results: The Stylistic Stress Test (V4)

**Date:** Dec 2025
**Status:** ✅ Successful Enhancement (Physicality + History Added)

## Executive Summary
We successfully upgraded the predictive engine to **V4** by integrating the **Physicality Vector** and expanding the training dataset to **9 seasons (2015-2024)**. The model accuracy has improved to **57.2%**, a significant leap from the V3 baseline.

---

## 1. The Model Performance

*   **Overall Accuracy:** 57.2% (up from 53.5% in V3)
*   **Key Success:** The model is now robust across nearly a decade of data.

### Classification Report
| Archetype | Precision | Recall | F1-Score | Insight |
| :--- | :--- | :--- | :--- | :--- |
| **King** | 0.58 | 0.66 | 0.62 | ✅ **Strong Recall.** We are correctly identifying 2/3rds of true Kings. |
| **Bulldozer** | 0.59 | 0.57 | 0.58 | ✅ **Solid.** Good balance for high-volume stars. |
| **Sniper** | 0.53 | 0.50 | 0.52 | ⚠️ **Noisier.** Role players are harder to pin down. |
| **Victim** | 0.58 | 0.56 | 0.57 | ✅ **Reliable.** We can spot fragility. |

---

## 2. Feature Importance (The "Why")

The new features have reshaped the model's understanding of resilience.

1.  **`LEVERAGE_USG_DELTA` (13.8%)**: **#1 Predictor.** The "Abdication Detector" is now the strongest signal. Resilient players demand the ball in the clutch.
2.  **`CREATION_VOLUME_RATIO` (9.7%)**: Still a top tier predictor. Self-creation is non-negotiable.
3.  **`RS_PRESSURE_APPETITE` (7.3%)**: The "Dominance" signal remains vital.
4.  **`PO_EFG_BEYOND_RS_MEDIAN` (7.0%)**: The "Plasticity" signal (scoring from new spots).
5.  **`RS_FTr` (6.6%)**: **NEW.** Regular Season Free Throw Rate is a top-5 feature. Physicality matters.

**Takeaway:** The profile of a resilient player is someone who **demands the ball in the clutch**, **creates their own shot**, **forces the issue physically**, and **adapts their shot diet**.

---

## 3. Methodology
*   **Algorithm:** XGBoost Classifier (Multi-Class)
*   **Training Data:** 899 Player-Seasons (2015-2024)
*   **Input Features (Stress Vectors):**
    *   *Creation Vector:* Tax & Volume.
    *   *Leverage Vector:* Clutch Usage & TS Delta.
    *   *Plasticity Vector:* Spatial Variance & Distance Delta.
    *   *Pressure Vector:* Appetite & Resilience.
    *   *Physicality Vector (New):* FTr Resilience & Base FTr.

## 4. Next Steps
The model is now ready for the Sloan paper write-up. Future improvements should focus on:
1.  **Hyperparameter Tuning:** We haven't optimized the XGBoost parameters yet.
2.  **Contextual Filtering:** Can we filter out noise from players with bad team spacing?
