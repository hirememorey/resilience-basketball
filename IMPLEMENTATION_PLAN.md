# NBA Playoff Resilience: The Sloan Path Implementation Plan

## Executive Summary

**Goal:** Identify "16-game players" who perform better than expected in the playoffs and **explain why** using mechanistic data.

**Target:** Submission to MIT Sloan Sports Analytics Conference.

**Core Breakthrough (Dec 2025):** We have solved the **Luka/Simmons Paradox** by establishing the **Dual-Grade Archetype System**. Resilience is defined as the interaction between **Adaptability** (Resilience Quotient) and **Dominance** (Absolute Value).

---

## ✅ Completed Phases (The Foundation)

We have successfully built the Descriptive, Predictive, and Mechanistic engines.

*   **Phase 1: Data Integrity:** ✅ Solved. Full historical dataset (2015-2024) collected and verified.
*   **Phase 2: Descriptive Resilience:** ✅ Solved. The "Dual-Grade" system correctly classifies historical outliers.
*   **Phase 3: Predictive Engine:** ✅ Initial "Plasticity" model showed promise; now needs retraining on the new Archetype labels.
*   **Phase 4: The Paradox Fix:** ✅ Solved. `LUKA_SIMMONS_PARADOX.md` details the resolution.
*   **Phase 5: The "Stylistic Stress Test" (V2):** ✅ Solved. Validated that Self-Creation and Clutch Usage predict resilience.

---

## ✅ Phase 6: The "Shaq Problem" Fix (V3 Model)

**Status:** ✅ **Success.** (Dec 2025)

**Outcome:** We successfully upgraded the predictive engine to **V3** by incorporating **Pressure Vectors** (Shot Difficulty) to solve the "Shaq Problem" (Dominant Rigidity).

### Key Achievements
1.  **Prediction Accuracy:** 53.5% (up from 50.5% in V2).
2.  **Validation:** Confirmed that **Pressure Appetite** (willingness to take tight shots) is the 2nd strongest predictor of playoff resilience.
3.  **Methodology:** Successfully aggregated 5 years of defender distance data using `leaguedashplayerptshot`.

### Artifacts
*   **Model:** `models/resilience_xgb.pkl`
*   **Dataset:** `results/pressure_features.csv`
*   **Report:** `results/predictive_model_report.md`
*   **Scripts:**
    *   `src/nba_data/scripts/collect_shot_quality_aggregates.py`
    *   `src/nba_data/scripts/calculate_shot_difficulty_features.py`

---

## ✅ Phase 7: The "Physicality" & "Expansion" Phase (COMPLETED)

**Status**: ✅ **COMPLETE** (Dec 2025)

**Objective**: Capture the missing "Force" dimension and complete historical data expansion.

### **Step 1: The Physicality Vector Refinement - ✅ DONE**

**Status**: ✅ **SUCCESS** - First-Principles Upgrade

**Consultant Feedback Integration**: Following external consultant review, we replaced whistle-dependent FTr Resilience with process-dependent **Rim Pressure Resilience**.

**Implementation**:
*   **Script**: `src/nba_data/scripts/calculate_rim_pressure.py`
*   **Metric**: `Rim Pressure Resilience` = PO Rim Appetite / RS Rim Appetite (Restricted Area attempts %)
*   **Integration**: Fully integrated into predictive model with 18 features.
*   **Impact**: `RIM_PRESSURE_RESILIENCE` (5.3%) outperforms old `FTr_RESILIENCE` (3.8%).

### **Step 2: Historical Data Expansion - ✅ DONE**

**Status**: ✅ **COMPLETE** - Full 10-Season Dataset

**Progress**:
1.  **Data Collection**:
    *   ✅ Shot charts for all 10 seasons (2015-16 to 2024-25)
    *   ✅ RS game logs for 2015-16 to 2018-19 (historical context)
    *   ✅ Defensive context for 2024-25 season
    *   ✅ Complete stress vectors across all seasons

2.  **Model Training**:
    *   ✅ 5,312 player-season records (up from ~4,750)
    *   ✅ Stable accuracy at **58.3%** (consistent performance)
    *   ✅ All 18 stress vector features available

**Key Insight**: Context features (Quality of Competition) are sparse (~35% availability) and don't provide significant additional predictive signal. Model performance stabilized at 58.3% indicating robust core features.

### **Step 3: Pressure Vector Clock Refinement - ✅ DONE**

**Status**: ✅ **COMPLETE** (Dec 2025)

**Consultant Feedback Integration**: Following consultant feedback that "players who take bad shots early (low IQ) fail, but players who take bad shots late (bailouts) are valuable," we refined the Pressure Vector to distinguish late-clock vs early-clock pressure.

**Implementation**:
*   **Script**: `src/nba_data/scripts/collect_shot_quality_with_clock.py` (collects clock data)
*   **Script**: `src/nba_data/scripts/calculate_shot_difficulty_features.py` (calculates clock features)
*   **Features Added**:
    *   `RS_LATE_CLOCK_PRESSURE_APPETITE`: % of tight shots taken in late clock
    *   `RS_LATE_CLOCK_PRESSURE_RESILIENCE`: eFG% on tight shots in late clock
    *   `RS_EARLY_CLOCK_PRESSURE_APPETITE`: % of tight shots taken in early clock
    *   `RS_EARLY_CLOCK_PRESSURE_RESILIENCE`: eFG% on tight shots in early clock
    *   Plus corresponding PO features and deltas
*   **Impact**: `RS_LATE_CLOCK_PRESSURE_RESILIENCE` (4.8% importance, ranked 3rd) validates that late-clock bailout ability is a strong predictor.

**Key Insight**: The clock distinction reveals that shot timing matters as much as shot difficulty. Late-clock pressure resilience is a strong positive signal, while early-clock pressure provides negative signal.

**Data Collection Achievement (Dec 2025):**
*   ✅ Expanded clock data collection to all 10 seasons (2015-16 through 2024-25)
*   ✅ Optimized collection script with ThreadPoolExecutor parallelization (~4-5x faster)
*   ✅ Implemented data quality fixes: eFG% capped at 1.0, minimum sample size thresholds
*   ✅ Achieved 100% clock feature coverage (up from 12%)
*   ✅ Model accuracy improved to **59.4%** (up from 58.3% baseline)

### **Step 4: Component Analysis & Latent Star Detection - ✅ COMPLETE**

**Status**: ✅ **COMPLETE** (Dec 2025)

**Consultant Feedback Integration**: Following consultant feedback to move from "Classifying Behavior" to "Quantifying Value," we implemented component analysis and latent star detection.

**Implementation**:
*   **Component Analysis Script**: `src/nba_data/scripts/component_analysis.py`
    *   Correlates stress vectors directly with playoff outcomes (PIE, NET_RATING, OFF_RATING, etc.)
    *   Shows actionable correlations (e.g., `CREATION_VOLUME_RATIO → PO_PTS_PER_75: r=0.633`)
    *   Generates visualizations and reports
*   **Playoff PIE Collection**: `src/nba_data/scripts/collect_playoff_pie.py`
    *   Fetches playoff advanced stats (PIE, NET_RATING, OFF_RATING, DEF_RATING)
    *   Collected 2,175 player-seasons with 100% PIE coverage
*   **Latent Star Detection**: `src/nba_data/scripts/detect_latent_stars.py`
    *   Identifies "Sleeping Giants" - players with high stress profiles but low usage
    *   Currently identifies 25 candidates

**Key Findings**:
*   **Top Correlations**:
    *   `CREATION_VOLUME_RATIO → PO_PTS_PER_75`: r=0.633 (p<0.001)
    *   `LEVERAGE_USG_DELTA → PO_PTS_PER_75`: r=0.512 (p<0.001)
    *   `RS_LATE_CLOCK_PRESSURE_RESILIENCE`: Strong predictor of playoff performance
*   **Component Analysis Outputs**:
    *   `results/component_analysis_correlations.csv` - Full correlation matrix
    *   `results/component_analysis_report.md` - Detailed analysis with actionable insights
    *   `results/component_analysis_heatmap.png` - Correlation visualizations

**Current State of Latent Star Detection**:
*   ✅ **Implemented**: Basic detection system identifies players with top stress profiles
*   ⚠️ **Needs Refinement**: Currently includes established stars (LeBron, Luka) - needs filtering
*   🎯 **Next Steps**: Refine criteria to focus on true "sleeping giants" (role players with high stress profiles)

**Artifacts**:
*   `data/playoff_pie_data.csv` - Playoff PIE and advanced stats
*   `results/latent_stars.csv` - Current latent star candidates
*   `results/latent_star_detection_report.md` - Analysis report

---

### **Step 5: Sloan Paper Preparation - READY**

**Status**: 🎯 **READY FOR DRAFTING**

**Core Narrative**:
1.  **The Luka/Simmons Paradox**: Volume matters as much as efficiency ("Abdication Tax")
2.  **The Dual-Grade Archetype System**: Separating Adaptability from Dominance
3.  **Mechanistic Stress Vectors**: Creation, Leverage, Pressure (with Clock Distinction), Rim Pressure, and Context
4.  **Component Analysis**: Direct correlations between stress vectors and playoff outcomes (PIE, NET_RATING)
5.  **Predictive Validation**: **59.4% accuracy** with mechanistic explanations and full clock data coverage

---

## Historical Implementation Details (For Context)

### The V2 Plan: The "Stylistic Stress Test" Pipeline (COMPLETED)
**The Hypothesis:** A player's resilience is visible in RS situations that mimic the three core stylistic shifts of the playoffs: **1) Increased Self-Creation**, **2) Higher Leverage**, and **3) Schematic Pressure**.

#### Step 1: Feature Engineering (The "Stress Vectors")
*   **Vector 1: The "Isolation" Vector (Self-Creation)** - ✅ Implemented
*   **Vector 2: The "Clutch" Vector (Leverage)** - ✅ Implemented
*   **Vector 3: The "Pressure" Vector (Shot Difficulty)** - ✅ Implemented (V3)

#### Step 2: Modeling (Non-Linearity is Key)
*   **Methodology:** An **XGBoost Classifier**. - ✅ Implemented
*   **Target:** The `archetype` column from `results/resilience_archetypes.csv`. - ✅ Implemented
