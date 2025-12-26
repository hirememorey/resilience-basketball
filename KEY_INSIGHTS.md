- Haliburton ranks in top 15 (efficient playmaker)
- Westbrook ranks in top 10 (high-load playmaker, despite efficiency issues)
- Curry ranks in top 10 (elite efficiency + moderate load)

**Key Principle**: **Physics compliance over mathematical purity**. A target that fails archetype tests is falsified, no matter how theoretically sound.

Role players can excel in high-stress situations by taking easier shots (wide-open catch-and-shoot 3s). Weight proxy scores by shot quality metrics (creation volume, shot difficulty) to distinguish load-bearing resilience from situational success. Formula: `weighted_proxy_score = proxy_score × sqrt(creation_volume) × shot_quality_penalty`.

## 63. The "Garbage Time Elite" (Context Failure) - Point Differential Filtering Required 🎯 CRITICAL (December 2025)

Players can appear elite against "Top 10 Defenses" in blowouts when starters are resting. Always filter proxy calculations to competitive windows (±15 points) to ensure measured resilience reflects true high-stakes performance, not garbage time inflation.

## 67. The "Linear Growth" Fallacy (Stardom is Non-Linear) 🎯 CRITICAL (December 2025)

**The Problem**: A model trained with linear objectives (like RMSE) will be systematically conservative, under-predicting the non-linear "phase transition" from good player to superstar. It sees a 1.1 prediction for a 7.7 outcome (Jalen Brunson).

**The Insight**: The physics of stardom are not linear. The value of a player who can carry a 30% usage is exponentially greater than one who can carry 25%.

**The Fix**: Engineer features that capture this non-linearity.
- `HELIO_POTENTIAL_SCORE = SHOT_QUALITY_GENERATION_DELTA * (USG_PCT^1.5)`
- This teaches the model that creation at high volume is exponentially more valuable than creation at low volume, allowing it to predict the "superstar leap."

**Key Principle**: **Model linear relationships, but feature-engineer non-linear physics.**

## 68. The "Lottery Star" Trap (Censored Data) 🎯 CRITICAL (December 2025)

**The Problem**: If a future star is stuck on a lottery team (Booker '18, Fox '20), the current model had no "outcome" data. The default was to mark them as `0`, effectively training the model that "High Usage + Good Creation on a Bad Team = Failure."

**The Insight**: Team success is a noisy proxy for individual scalability. Lack of playoff data is not a "Zero" outcome; it is **Censored Data**.

**The Fix**: Adopt "Revealed Capacity" logic. Training targets must be `NaN` (dropped) for players who did not participate in the outcome window, rather than `0.0`. This preserves the signal of what *could* happen, conditional on opportunity.

## 69. The "Unit Mismatch" Trap (API Per-Game vs Total) 🎯 CRITICAL (December 2025)

**The Problem**: Blindly applying volume thresholds (e.g., >50 FGA) to API data without verifying units.

**The Insight**: The `leaguedashplayerptshot` endpoint returns **Per-Game** statistics for dribble categories, not season totals. A threshold of 50 FGA/Game is physically impossible.

**The Fix**: Always run a diagnostic `.describe()` on raw API data before setting gates. The 75th percentile for "0 Dribble" FGA is ~4.5 per game. Calibrate gates to the actual observed distribution, not a theoretical total.

## 70. The "System Merchant" Mirage (Subsidy Index) 🎯 CRITICAL (December 2025)

**The Problem**: A model that projects total observed efficiency assumes a player "owns" their percentage. In reality, some players "rent" their efficiency from their ecosystem (e.g., Jordan Poole '22 benefiting from Steph Curry's gravity). When projected to higher usage (new context), this "Subsidy" vanishes.

**The Insight**: Skill is the ability to generate efficient looks via **Ownership**.
-   **Old Assumption**: Speed = Skill. (False: Fast running without the ball is often dependent activity).
-   **New Assumption (The Ownership Matrix)**: Skill is either **Ball Dominance** (Time of Poss) or **Playmaking** (Ast%). Passengers have neither.

**The Fix**: Implement the **Subsidy Index v2** using player tracking data.
- **Formula**: $SkillIndex = Max(NormalizedTimeOfPoss, NormalizedAstPct)$
- **Tax**: $SubsidyIndex = 1.0 - SkillIndex$
- **Result**: Jordan Poole (Fast, but dependent) is exposed. Nikola Jokic (Slow, but dominant creator) is valued correctly.

**Key Principle**: **Filter for ownership before projecting for magnitude.**

## 71. The "Activity Merchant" Trap (Speed != Skill) 🎯 CRITICAL (December 2025)

**The Problem**: Defining "Motor" as simply "Speed" or "Distance Traveled" penalizes genius-level stationary processors (Jokic, Luka) and rewards frantic system players (Poole).

**The Insight**: High speed without ball dominance or playmaking is often **Dependent Activity** (cutting, running off screens). True "Motor" for a primary option is Decision Velocity, not Foot Speed.

**The Fix**: Remove `AvgSpeed` from the Skill Index calculation entirely. Focus on `TimeOfPoss` (On-Ball Load) and `AstPct` (Creation Load).

## 72. The "Big Man Blindspot" (Touch vs. Dominance) 🎯 CRITICAL (December 2025)

**The Problem**: Even with the new Subsidy Index, elite finishing bigs (Christian Wood, Sabonis) can look like "System Merchants" because they don't hold the ball long (`TimeOfPoss`) or run point (`AstPct`). However, their efficiency is sometimes "owned" via elite touch/post-work.

**The Insight**: Big Man ownership looks different than Guard ownership. It manifests as **Efficiency Maintenance at Volume** on "Touch" plays (Post-ups, Elbow touches).

**The Fix (Next Steps)**: Integrate `ELBOW_TOUCH_EFFICIENCY` and `POST_TOUCH_EFFICIENCY` into the Skill Index for players > 6'9".

## See Also
- `2D_RISK_MATRIX_IMPLEMENTATION.md` - ✅ **COMPLETE** - 2D framework implementation
- `UNIVERSAL_PROJECTION_IMPLEMENTATION.md` - ✅ **COMPLETE** - Universal projection implementation (v2 with Subsidy Index)
- `LUKA_SIMMONS_PARADOX.md` - Theoretical foundation
