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

**The Fix (v3)**: Integrate `ELBOW_TOUCH_EFFICIENCY` and `POST_TOUCH_EFFICIENCY` into the Skill Index.
- **Formula**: $SkillIndex = Max(NormPoss, NormAst, NormTouchPts)$
- **Status**: ✅ **COMPLETE** - This has resolved the "Jokic Paradox" where the league's most resilient player was misclassified.

## 73. The "Scalability Gradient" (Elasticity of Volume) 🎯 CRITICAL (December 2025)

**The Problem**: Early-career stars (Tatum '18, Siakam '19) are penalized for low usage, but arbitrarily projecting everyone to 30% usage creates false positives for "Efficiency Merchants" (Montrezl Harrell). Using a hard gate (e.g., "Only project if Subsidy < 0.4") violates the First Principle of "No Hard Gates."

**The Insight**: Volume Scalability is not binary; it is a continuous function of **Ownership**. A player's ability to absorb new volume is proportional to their Skill Index.

**The Fix**: Instead of a gate, use an **Elastic Projection**.
- `Projected_Volume = Current_Usage + ((Target_Usage - Current_Usage) * (1.0 - Subsidy_Index))`
- **Pure Owner (Subsidy 0.0)**: Gets full credit for the gap to 30% usage.
- **Pure Merchant (Subsidy 1.0)**: Gets zero credit (stays at current usage).
- **Result**: Tatum scales up. Harrell stays put. No magic thresholds required.

## 74. The "Abdication and Choke" Taxes (Fragility v3.5) 🎯 CRITICAL (December 2025)

**The Problem**: Players with high ownership and high volume (Ben Simmons, D'Angelo Russell, KAT) can fool the model into predicting stardom, despite known playoff fragility. "Owned" volume is not enough if that ownership is fragile.

**The Insight**: Stylistic Fragility manifests in two distinct physics-based failure modes:
1.  **Abdication (Fear)**: Usage plummeting in high-leverage moments (`LEVERAGE_USG_DELTA`). Simmons/D-Lo famously stop looking for shots.
2.  **Choking (Incompetence)**: Efficiency plummeting while volume stays high (`LEVERAGE_TS_DELTA`). KAT continues to shoot but the quality collapses under pressure.

**The Fix**: Implement a composite `FRAGILITY_SCORE` that applies multiplicative penalties for both modes.
- **Abdication Tax**: `(leverage_usg_delta * -15.0)`
- **Choke Tax**: `(leverage_ts_delta * -5.0)`
- **Result**: D'Angelo Russell ('19) was successfully demoted from **King** to **Sniper** (Potential 5.8 -> 1.4).

## 75. The "Linearity Trap" (ML vs. Physics) 🎯 CRITICAL (December 2025)

**The Problem**: Despite having a high Fragility Score, some elite players (Simmons, KAT) remain predicted as "Kings" by the Telescope Model.

**The Insight**: In a tree-based or linear model, the "Sum of Parts" for an elite athlete (Elite Defense + Elite Playmaking + 30% Usage) is so high that the "Fragility Penalty" is insufficient to move the needle. The model learns that high volume is the ultimate signal, drowning out the drag coefficient.

**The Fix**: For true "Type 1" protection (False Positives), the engine requires a **Two-Stage Architecture**:
1.  **Filter (The Physics)**: A hard gate based on the Fragility Score.
2.  **Rank (The ML)**: Rank the survivors based on projected potential.
*Principle: You cannot "Average" your way out of a fatal flaw.*

## 76. The "Ground Truth Trap" (Outcomes ≠ Process) 🎯 CRITICAL (December 2025)

**The Problem**: Phase 1 predicted `FUTURE_PEAK_HELIO` (future playoff PIE), but playoff PIE is contaminated by context. Ben Simmons had decent playoff PIE pre-2021 because of Embiid doubles + shooters. The model learned he was "good."

**The Insight**: We were training on **outcomes** (what happened) instead of **process** (how it happened). Outcomes are contextual; process is portable.

**The Fix**: Shift from predicting outcomes to measuring **Creation Independence** - the ability to generate offense when the defense knows it's coming. This is portable across contexts.

**Key Principle**: **Model the process, not the outcome.**

## 77. The "Patch vs. Learn" Trap (Architectural Integrity) 🎯 CRITICAL (December 2025)

**The Problem**: We could catch Simmons by adding an "abdication penalty" to the target variable. This worked (60% pass rate), but it violated the "learn don't patch" principle.

**The Insight**: Every time we add a manual penalty or hard gate, we're admitting the features don't capture the phenomenon. The model should learn from features, not have the answer coded into the target.

**The Fix**: Instead of patching the target, engineer features that directly measure the phenomenon. `clutch_usg_absolute` is better than `leverage_usg_delta` because it answers "what IS the clutch usage?" not "how much did it change?"

**Key Principle**: **If you're patching the target, you're asking the wrong question.**

## 78. The "Creator vs. Converter" Dichotomy (The Right Question) 🎯 CRITICAL (December 2025)

**The Problem**: The old question "How good will this player be?" doesn't distinguish between players who CREATE opportunities and players who CONVERT opportunities created by others.

**The Insight**: The fundamental distinction is:
- **Creators**: Can manufacture efficient offense against engaged defenses. They ARE the situation.
- **Converters**: Can only cash in opportunities the system creates. They NEED the situation.

Ben Simmons is an elite Converter (great in transition, with shooters) but a poor Creator (no self-created jumpers). The old model couldn't see this.

**The Fix**: Ask the right question: "Can this player create when schemed?" The answer is the **Creation Independence Index**.

**Key Principle**: **Creators are portable; Converters are contextual.**

## 79. The "Feature Reframe" Insight (Deltas vs. Absolutes) 🎯 CRITICAL (December 2025)

**The Problem**: `leverage_usg_delta` (change in clutch usage) treats a player going from 40% → 35% the same as 15% → 10%. But these are very different situations - one is still a go-to player, one is hiding.

**The Insight**: Deltas lose information about the baseline. Sometimes the absolute value matters more than the change.

**The Fix**: Add `clutch_usg_absolute = usg_pct + leverage_usg_delta` to measure the actual clutch usage, not just the change. Luka at 38% clutch usage is very different from Simmons at 12%.

**Key Principle**: **Absolutes tell you what happened; deltas tell you how it changed. You need both.**

## 80. The "Archetype over Regression" Insight (Classification > Prediction) 🎯 CRITICAL (December 2025)

**The Problem**: Regression to predict "potential score" is falsely precise. We don't actually know if a player will score 7.2 vs 7.8 HELIO. But we DO know if they're a "Franchise Engine" or "Fragile Star."

**The Insight**: The decision isn't "how good exactly?" It's "what type of player is this?" A max contract decision needs to know: can they be your #1? That's a classification question.

**The Fix**: Phase 2 uses archetype classification:
- Franchise Engine
- Strong Creator  
- Luxury Amplifier
- Fragile Star
- Role Player

**Key Principle**: **Classify the archetype, don't predict the score.**

## 81. The "Creation Signature" (UAST + Pullup) 🎯 CRITICAL (December 2025)

**The Problem**: Unassisted FG% alone can be misleading (Ben Simmons has a high UAST% because he creates transition dunks, but cannot create half-court jumpers).

**The Insight**: True Creation Independence is the intersection of **Unassisted Frequency** and **Pull-up Volume**. 
- **James Harden ('19)**: 87% UAST + 13.7 Pull-up FGA (Elite Engine)
- **Ben Simmons ('19)**: 56% UAST + 1.2 Pull-up FGA (Dependent Finisher)
- **Nikola Jokic ('24)**: 40% UAST + 2.1 Pull-up FGA + 66% Contested (Hub Engine)

**The Fix**: Use the interaction of these metrics in the Self-Created Shot Score. High UAST without Pull-up volume is a signal of transition/rim pressure, not schemed-creation.

**Key Principle**: **Creation is the ability to generate a shot when the defense is set.**

## 82. The "Traffic vs. Difficulty" Trap (Contested Shot Rate) 🎯 CRITICAL (December 2025)

**The Problem**: Using `contested_shot_rate` as a proxy for "shot difficulty embrace" is fundamentally flawed.

**The Data**:
- Ben Simmons: 76% contested rate
- Rudy Gobert: 85% contested rate (HIGHEST)
- Jayson Tatum: 50% contested rate

A naive implementation would score Gobert as the player who "most embraces difficulty."

**The Insight**: Contested shot rate conflates two very different phenomena:
- **Active Difficulty Embrace**: Tatum taking a contested fadeaway (resilience/skill)
- **Passive Difficulty Exposure**: Gobert dunking in traffic because he can't shoot elsewhere

Simmons and Gobert have HIGH contested rates because they ONLY take shots at the rim. The paint is packed because defenses don't respect their jumper.

**The Fix**: Use jump shot volume metrics (`pull_up_fga`, `pct_pts_2pt_mr`, `pull_up_fg3a`) as primary signals for Component 3. These metrics:
- Create a 15x gap between Simmons (0.7 pull-up FGA) and Tatum (10.4 pull-up FGA)
- Automatically penalize players who can't take jumpers
- Properly reward mid-range specialists (DeRozan: 35% of points from mid-range)

**Key Principle**: **Measure the shot type, not just the defender proximity.**

## 83. The "Force Creator" Archetype (Giannis/Shaq/Zion) 🎯 IMPORTANT (December 2025)

**The Problem**: Some Franchise Engines (Giannis, Shaq, Zion) don't take many jumpers but ARE the situation.

**The Insight**: Creation Independence has two valid paths:
1. **Perimeter Creation**: Pull-ups, mid-range, off-dribble 3s (Harden, Tatum, DeRozan)
2. **Force Creation**: Rim attacks through contact at high volume (Giannis, Shaq)

Both are valid. The difference from Simmons/Gobert is:
- **Agency**: Giannis DEMANDS the ball; Gobert waits for lobs
- **Volume**: Giannis takes 20+ FGA; Gobert takes 6-8
- **Pressure Response**: Giannis' usage INCREASES in clutch; Simmons' DECREASES

**The Fix**: 
- Component 3 (Shot Difficulty) focuses on JUMP SHOT creation
- Force creators get credit through Component 1 (`creation_volume_ratio`) and Component 5 (`physicality_score`, `FTr`)
- The CII composite correctly identifies both archetypes as Engines through different paths

**Key Principle**: **Multiple valid paths to the same destination. Don't conflate the path with the destination.**

## See Also
- `2D_RISK_MATRIX_IMPLEMENTATION.md` - ✅ **COMPLETE** - 2D framework implementation
- `UNIVERSAL_PROJECTION_IMPLEMENTATION.md` - ✅ **COMPLETE** - Universal projection implementation (v2 with Subsidy Index)
- `LUKA_SIMMONS_PARADOX.md` - Theoretical foundation
- `phase2_creation_independence/SPECIFICATION.md` - **NEW** - CII specification
