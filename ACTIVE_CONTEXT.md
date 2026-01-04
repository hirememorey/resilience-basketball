# Active Context: NBA Playoff Resilience Engine

**Last Updated**: January 3, 2026
**Status**: 🚧 **In Progress - Phase 3 (Principled Adjustments)**
**Current Priority**: Refactoring Component 1 (Self-Created Shot) and fixing Component 3 (Difficulty Embrace) architecture.

---

## The Pivot (Phase 2d)
We realized our "Self-Created Shot Score" was suffering from **Modal Bias**: it accurately measured ISO creation (Harden/Luka) but failed to capture other valid forms of advantage generation (Drive-and-Kick, Gravity, Post).

We are moving to a **Multi-Path Architecture**:
> **"Creation is not just isolation; it is the generation of advantage. That advantage can be generated through 1v1 skill, rim pressure, gravity, or positioning."**

---

## 🛠 Active Development (Multi-Path Implementation)

### Current Progress
- [x] **Phase 1 (Bare Model)**: Created bare path modules and CII calculator with no gates.
- [x] **Phase 2 (Diagnostics)**: Diagnosed failure modes for LeBron, Curry, Giannis, Jokić.
- [ ] **Phase 3 (Adjustments)**: Implementing fixes based on diagnostics.

### Key Findings (Diagnosis Phase)
1.  **Jokić Failure**: Component 3 (Difficulty Embrace) lacks the Hub Path logic found in Component 1, unfairly penalizing him for efficiency.
2.  **LeBron/Giannis Failure**: Drive-and-Kick path formula underestimates the value of elite rim pressure volume.
3.  **Curry Failure**: Gravity path proxies (screen assists) are weak or missing; needs better formula.
4.  **Data Gaps**: Missing tracking data for Ja Morant and Donovan Mitchell (2021-22).

### The Solution: Multi-Path Evaluation
We will evaluate **four distinct creation pathways** and take the maximum score (plus a multi-modal bonus):

| Path | Name | Physics of Advantage | Primary Exemplars |
|------|------|----------------------|-------------------|
| **A** | **ISO Creator** | 1v1 Skill → Forces Help | Harden, Luka, Shai |
| **B** | **Drive-and-Kick** | Rim Pressure → Collapses Defense | LeBron, Giannis, Russ |
| **C** | **Post Hub** | Positioning/Size → Forces Doubles | Jokić, Embiid |
| **D** | **Gravity Engine** | Movement Threat → Distorts Shape | Curry, Klay, Miller |

**New Formula**:
`Self_Created_Score = Max(Path_A, Path_B, Path_C, Path_D) + Multi_Modal_Bonus`

---

## 🚀 Deployment Targets

### Phase 1: Drive-and-Kick (Immediate)
-   **Objective**: Correctly classify **LeBron James** and **Giannis Antetokounmpo** as Franchise Engines.
-   **New Metrics**: Drives per game, Points/Assists per Drive, Rim Pressure Rate.

### Phase 2: Gravity Engine (Follow-up)
-   **Objective**: Correctly classify **Steph Curry** as Franchise Engine.
-   **New Metrics**: Screen Assists, Catch-and-Shoot Efficiency, Off-Ball Volume.

---

## System Architecture

### 2D Classification Logic (Current)
1.  **Engine Filter**: `CII >= 74` → **Franchise Engine**
2.  **Latent Filter**: `Positive Leverage` + `High TII` + `Age <= 28` → **Latent Engine**
3.  **Fragile Filter**: `High Usage (>22%)` + `Low CII` + (`Negative Leverage` OR `No Tools`) → **Fragile Star**
4.  **Amplifier Filter**: `Negative Leverage` + `Has Tools` → **Luxury Amplifier**

### CII Components (Refactored)

| Component | Weight | Question | Method |
|-----------|--------|----------|--------|
| **1. Self-Created Shot** | **30%** | **Can you generate advantage?** | **MAX(ISO, Drive, Hub, Gravity)** |
| 2. Pressure Appetite | 25% | Do you want the ball in clutch? | Usage Maintenance |
| 3. Difficulty Embrace | 20% | Do you take tough shots? | Pull-up/Contested Vol **(needs Hub logic)** |
| 4. Defensive Survival | 15% | Do you survive schemes? | Efficiency Maintenance |
| 5. Force Multiplication | 10% | Do you create physically? | FTr / Physicality |

---

## Project Structure

### Active Directories
- `src/nba_data/phase2_creation_independence/`
    - `index/`
        - `self_created.py` (Target for Refactor)
        - `paths/` (New modular path logic)
            - `iso.py`, `drive_kick.py`, `post_hub.py`, `gravity.py`, `combined.py`
    - `MULTIPATH_SPECIFICATION.md` (See `implementation_plan_multipath.md`)

### Reference Documents
- **`implementation_plan_multipath.md`** - The active blueprint.
- **`KEY_INSIGHTS.md`** - See Insight #89 (Creation Polymorphism).

---

## Next Steps (Phase 3)

### Priority 1: Fix Component Architecture (Critical)
- [ ] Refactor `difficulty_embrace.py` to include Hub Path logic (Jokić fix).

### Priority 2: Fix Path Formulas (High)
- [ ] Tune Drive-Kick formula weights/thresholds (LeBron/Giannis fix).
- [ ] Tune Gravity formula and proxies (Curry fix).

### Priority 3: Data Pipeline
- [ ] Investigate missing tracking data for 2021-22 (Ja Morant/Mitchell).
