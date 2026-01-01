# Active Context: NBA Playoff Resilience Engine

**Last Updated**: December 31, 2025
**Status**: 🚧 **REFINING** - Implementing Phase 2c "Creation Viability"
**Current Priority**: Fixing "The Mudiay/Curry Anomaly" via Viability-Dampened Volume

---

## The Pivot
We discovered that Phase 1 was asking the **wrong question**:
- **Phase 1 asked**: "How good will this player be?" (predicting future playoff PIE)
- **Phase 2 asks**: "Can this player create when schemed?" (measuring creation independence)

The fundamental question is now:
> **"Does this player need the right situation, or IS he the situation?"**

---

## 🛠 Active Development (Phase 2c: The Viability Refinement)

### The Problem: The Mudiay/Curry Anomaly
We identified a flaw in the `Self-Created Shot Score` where "Creation Motion" (volume) was rewarded regardless of "Creation Viability" (efficiency).
-   **Emmanuel Mudiay (2017)**: High Volume + Terrible Efficiency = **Strong Creator** (False Positive)
-   **Steph Curry (2017)**: Moderate Volume + Elite Efficiency = **Undervalued** (False Negative)

### The Solution: Viability-Dampened Volume
We are moving from a "Motion" model to a "Work" model.
1.  **Creation Premium**: Compare Player TS% to *Taxed* Teammate TS% (accounting for the difficulty of creation vs finishing).
2.  **Viability Coefficient**: Dampen volume scores based on the Creation Premium.
    -   Positive Premium (Iverson/Luka): Full credit for volume.
    -   Negative Premium (Mudiay): Severe penalty on volume.

---

## 🚀 Deployment Results (December 2025)

We successfully deployed the 2D Classification System (CII × TII) to the 2024-25 season dataset (most recent complete data).

### Key Findings

| Category | Definition | Identified Players |
| :--- | :--- | :--- |
| **Franchise Engine** | The system. #1 Option. | Jokić, Brunson, SGA, Trae Young, Ant Edwards |
| **Latent Engine** | **THE ALPHA**. Young, undervalued, high potential. | **Darius Garland, Cade Cunningham, Anfernee Simons, Paolo Banchero** |
| **Strong Creator** | Elite #2. Reliable. | Kyrie Irving, Devin Booker, DeMar DeRozan, Chris Paul |
| **Fragile Star** | **THE TRAP**. High usage, fatal flaws. | **Jordan Poole, Coby White, RJ Barrett, Kyle Kuzma** |

### The "Alpha" List (Latent Engines < 26)
These players have the Creation Independence (CII) and Trajectory (TII) markers of future superstars but may not be priced as such yet:
1.  **Darius Garland**: +0.021 Leverage, Elite TII (78.3)
2.  **Cade Cunningham**: +0.039 Leverage, High CII (70.0)
3.  **Anfernee Simons**: +0.048 Leverage (Steps Up), Elite TII (75.7)
4.  **Paolo Banchero**: Age 22, already High CII (68.1)

---

## System Architecture

### 2D Classification Logic (Refined Phase 2b)

The classification now includes **Age Gates**, **Usage Gates**, and **Career Pattern Analysis**:

1.  **Engine Filter**: `CII >= 74` → **Franchise Engine**
2.  **Latent Filter**: `Positive Leverage` + `High TII` + `Age <= 28` → **Latent Engine**
    *   *Correction*: Veterans (>28) with these stats are mapped to **Strong Creator**.
3.  **Fragile Filter**: `High Usage (>22%)` + `Low CII` + (`Negative Leverage` OR `No Tools`) → **Fragile Star**
    *   *Protection*: Low usage players (<22%) are classified as **Role Players**, avoiding false positives for elite role players like Derrick White.
4.  **Amplifier Filter**: `Negative Leverage` + `Has Tools` → **Luxury Amplifier**

### Components

| Component | Weight | Question |
|-----------|--------|----------|
| **CII (Current)** | 100% | "Can you create right now?" |
| - Self-Created Shot | 30% | Unassisted volume + efficiency |
| - Pressure Appetite | 25% | Do you want the ball in clutch? |
| - Difficulty Embrace | 20% | Do you take tough shots? |
| - Defensive Survival | 15% | Do you survive schemes? |
| - Force Multiplication | 10% | Physicality/Free Throws |
| **TII (Trajectory)** | N/A | "Do you have scaling potential?" |

---

## Project Structure

### Active Directories
- `src/nba_data/phase2_creation_independence/` - Core logic
    - `index/` - Component calculators (`classify_2d.py` is the main engine)
    - `ground_truth/` - Expert labels
- `src/nba_data/scripts/` - Data collection (Use `deploy_2025_26_analysis.py` for execution)
- `results/` - Output CSVs (Look for `classification_2d_2024_25.csv`)

### Key Files
- **`IMPLEMENTATION_GUIDE.md`** - Technical manual
- **`LUKA_SIMMONS_PARADOX.md`** - Theoretical foundation
- **`KEY_INSIGHTS.md`** - Lessons learned

---

## Next Steps

### Priority 1: Creation Viability (The Mudiay Fix)
- [ ] Implement `calculate_creation_viability` in `self_created.py`.
- [ ] Implement `teammate_relative_efficiency` calculation.
- [ ] Apply viability dampener to `volume_score` and `unassisted_score`.
- [ ] Validate Mudiay (2017) drops to Role Player and Curry (2017) remains Strong Creator.

### Priority 2: Visualization & Reporting
- [ ] Build a Streamlit dashboard to visualize the 2D grid (CII vs TII).
- [ ] Create "Player Cards" showing their CII component breakdown.

### Priority 3: Monitoring
- [ ] Monitor the "Latent Engine" list (Garland, Cunningham, Simons) during the 2025-26 season.
- [ ] Watch the "Fragile Stars" (Poole, Kuzma) for playoff collapse.

---

## Quick Start

To run the analysis:
```bash
python scripts/deploy_2025_26_analysis.py
```

To classify a single player:
```python
from src.nba_data.phase2_creation_independence.index.classify_2d import diagnose_2d_classification
diagnose_2d_classification("Cade Cunningham", "2024-25", df)
```
