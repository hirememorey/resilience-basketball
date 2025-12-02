# Predictive Model Results: The Stylistic Stress Test (V2)

**Date:** Dec 2025
**Status:** ✅ Successful Proof of Concept

## Executive Summary
We successfully trained an XGBoost classifier to predict Playoff Archetypes (King, Bulldozer, Victim, Sniper) using only Regular Season data. The model validates the "Stress Vector" hypothesis, achieving **50.5% accuracy** (2x random chance) and confirming that **Self-Creation Volume** and **Clutch Usage** are the strongest leading indicators of playoff resilience.

---

## 1. The Model Performance

*   **Overall Accuracy:** 50.5% (vs 25% baseline)
*   **Key Success:** The model effectively distinguishes between "Resilient Role Players" (Snipers) and "Fragile Role Players" (Victims).

### Classification Report
| Archetype | Precision | Recall | F1-Score | Insight |
| :--- | :--- | :--- | :--- | :--- |
| **Sniper** | 0.52 | 0.57 | 0.55 | ✅ **Best Performer.** We can predict who will stay efficient. |
| **Victim** | 0.51 | 0.53 | 0.52 | ✅ **Solid.** We correctly identify >50% of playoff collapses. |
| **Bulldozer** | 0.42 | 0.53 | 0.47 | ⚠️ **Over-Predicted.** We tend to label high-usage stars as inefficient "Bulldozers." |
| **King** | 0.55 | 0.41 | 0.47 | ❌ **Hardest to Predict.** True transcendence is elusive in RS data. |

---

## 2. Feature Importance (The "Why")

The feature importance ranking strongly validates our First Principles:

1.  **`CREATION_VOLUME_RATIO` (25.9%)**: **The dominant factor.** The percentage of a player's shots that are self-created (3+ dribbles) is the #1 predictor of their playoff destiny.
    *   *Takeaway:* You cannot be a "King" if you rely on others to create your offense.
2.  **`LEVERAGE_USG_DELTA` (16.2%)**: **The "Abdication" Detector.** Whether a player's usage goes UP or DOWN in clutch time is more important than their efficiency.
    *   *Takeaway:* Resilient players demand the ball. Fragile players hide.
3.  **`EFG_PCT_0_DRIBBLE` (13.5%)**: **The Baseline.** Elite catch-and-shoot ability provides a safety floor (Sniper archetype).

---

## 3. Methodology
*   **Algorithm:** XGBoost Classifier (Multi-Class)
*   **Training Data:** 503 Player-Seasons (2019-2024)
*   **Target Labels:** Derived from the "Dual-Grade" Descriptive Engine.
*   **Input Features:**
    *   *Creation Vector:* Tax (Efficiency Drop) & Volume Ratio.
    *   *Leverage Vector:* Clutch Usage Delta & Clutch TS Delta.
    *   *Baseline:* 0-Dribble Efficiency.

## 4. Future Improvements
1.  **Context Vector:** We skipped the "Quality of Competition" vector due to data complexity. Adding this (Performance vs Top 5 Defenses) is the likely path to 60%+ accuracy.
2.  **Tracking Data:** `avg_speed` and `touch_time` could help distinguish between "Movement Shooters" (Klay) and "Stationary Shooters" (Tucker).


