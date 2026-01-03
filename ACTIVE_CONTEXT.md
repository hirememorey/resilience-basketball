# Active Context: NBA Playoff Resilience Engine

**Last Updated**: January 2, 2026
**Status**: 🚧 **RESTRUCTURING** - Implementing Multi-Path Creation Framework
**Current Priority**: Refactoring Component 1 (Self-Created Shot) to capture non-ISO creation (LeBron/Curry).

---

## The Pivot (Phase 2d)
We realized our "Self-Created Shot Score" was suffering from **Modal Bias**: it accurately measured ISO creation (Harden/Luka) but failed to capture other valid forms of advantage generation (Drive-and-Kick, Gravity, Post).

We are moving to a **Multi-Path Architecture**:
> **"Creation is not just isolation; it is the generation of advantage. That advantage can be generated through 1v1 skill, rim pressure, gravity, or positioning."**

---

## 🛠 Active Development (Multi-Path Implementation)

### The Problem: The "LeBron/Curry Gap"
Current Component 1 (ISO-centric) systematic failures:
-   **LeBron James (2016)**: CII 68.8 (Expected 78+). **Cause**: Drive-and-kick creation masked as "assisted" or low pull-up volume.
-   **Steph Curry (2017)**: CII 68.7 (Expected 78+). **Cause**: Off-ball gravity and relocation creation not captured by on-ball metrics.

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
| 3. Difficulty Embrace | 20% | Do you take tough shots? | Pull-up/Contested Vol |
| 4. Defensive Survival | 15% | Do you survive schemes? | Efficiency Maintenance |
| 5. Force Multiplication | 10% | Do you create physically? | FTr / Physicality |

---

## Project Structure

### Active Directories
- `src/nba_data/phase2_creation_independence/`
    - `index/`
        - `self_created.py` (Target for Refactor)
        - `path_iso.py` (New)
        - `path_drive_kick.py` (New)
        - `path_post_hub.py` (New)
        - `path_gravity.py` (New)
    - `MULTIPATH_SPECIFICATION.md` (See `implementation_plan_multipath.md`)

### Reference Documents
- **`implementation_plan_multipath.md`** - The active blueprint.
- **`KEY_INSIGHTS.md`** - See Insight #89 (Creation Polymorphism).

---

## Next Steps

### Priority 1: Data Collection & Preparation
- [ ] Implement `collect_tracking_data.py` (NBA.com API)
- [ ] Merge tracking data with `predictive_dataset_with_friction.csv`

### Priority 2: Path Implementation
- [ ] Extract Path A (ISO) and Path C (Hub) from existing logic.
- [ ] Implement Path B (Drive-and-Kick).
- [ ] Integrate into `calculate_self_created_score`.

### Priority 3: Validation
- [ ] Verify LeBron '16 and Giannis '21 classify as Franchise Engines.
