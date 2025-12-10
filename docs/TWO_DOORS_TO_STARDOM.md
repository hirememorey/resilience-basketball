# The "Two Doors to Stardom" Implementation Plan

**Date**: December 10, 2025  
**Status**: Design Document - Ready for Implementation  
**Priority**: Critical - Unlocks next level of model accuracy.

---

## 1. First Principles Analysis: The Single Threshold Fallacy

The core of our current problem is the **Single Threshold Fallacy**: we are trying to apply one universal set of rules to identify players who become stars for very different reasons. This single "star-shaped" filter is now catching false positives, but is also too blunt and is incorrectly filtering out some true positives.

From the physics of basketball, there is not one single path to stardom.

*   **Path A: The Skill Path (Polished Diamond)**: A player like Trae Young or Jalen Brunson becomes a star through overwhelming offensive skill, creation, and efficiency, even if they lack elite physical tools.
*   **Path B: The Physicality Path (Uncut Gem)**: A player like a young Giannis Antetokounmpo or Anthony Edwards becomes a star through overwhelming physical tools (rim pressure, athleticism, motor), even if their initial skills (shooting, efficiency) are raw and unpolished.

Our current, single-filter model is optimized for the "Polished Diamond" path. It penalizes inefficiency and system dependence, which is correct for that archetype. However, those same penalties incorrectly punish an "Uncut Gem" whose statistical profile is expected to be messy and inefficient early in their career.

**The Principle:** We must stop thinking about a single filter. The solution is to create **multiple, parallel validation pathways**. A player only needs to qualify for and pass through *one* valid door to be considered a potential star.

---

## 2. The "Two Doors to Stardom" Architecture

The new architecture will have two distinct validation paths.

### Door #1: The "Polished Diamond" Path (The Skill Path)

This path is for players whose primary signal is **elite, portable skill**.

*   **Who is eligible?**: Players who demonstrate elite creation and efficiency signals in the regular season.
    *   **Entry Criteria**: `CREATION_TAX` > 75th percentile OR `EFG_ISO_WEIGHTED` > 75th percentile.
*   **What are the rules for this path?**: For this archetype, inefficiency and dependence are fatal flaws.
    *   **Fatal Flaws**: High `INEFFICIENT_VOLUME_SCORE` or a high `SYSTEM_DEPENDENCE_SCORE` will result in a failure.
    *   **Logic**: We will maintain our current aggressive penalties for these features for any player who goes down this path.

### Door #2: The "Uncut Gem" Path (The Physicality Path)

This path is for players whose primary signal is **overwhelming physical tools or motor**.

*   **Who is eligible?**: Players who demonstrate elite physical tools and aggression, even if their skills are unpolished.
    *   **Entry Criteria**: `RS_RIM_APPETITE` > 90th percentile (or other elite physical metrics).
*   **What are the rules for this path?**: For this archetype, we must have a much higher tolerance for messy inefficiency. We are betting on the physical tools, not the current polish.
    *   **Fatal Flaw**: The true dealbreaker for this path is **passivity**. An athletic freak who doesn't use their gifts is a bust. Therefore, a high `ABDICATION_MAGNITUDE` is the primary fatal flaw.
    *   **Logic**: For players on this path, we will significantly *relax* the penalties for `INEFFICIENT_VOLUME_SCORE` and `CREATION_TAX`.

---

## 3. How This Solves the Problem

This two-path system resolves the tension between our True Positive and False Positive rates.

*   **It Increases True Positives**: A raw, athletic prospect who is currently failing our "Polished Diamond" gates (due to messy efficiency) can now be validated through the "Uncut Gem" door, as long as they are aggressive. This is how we will recapture the failing True Positives.
*   **It Keeps False Positives Down**: The "Fool's Gold" players we are trying to eliminate will not qualify for or pass through either door.
    *   **D'Angelo Russell**: Fails the "Skill" path due to inefficiency. Fails the "Physicality" path due to a lack of elite rim pressure. **He remains filtered.**
    *   **Jordan Poole**: Fails the "Skill" path due to high system dependence. Fails the "Physicality" path due to a lack of elite physical traits. **He remains filtered.**

---

## 4. Implementation Plan for the Next Developer

Your task is to implement this two-path logic within the `predict_conditional_archetype.py` script.

### Step 1: Audit & Categorize Failing True Positives
*   **Action**: Before coding, run a diagnostic on the 7 True Positive cases that are currently failing in the test suite (`test_latent_star_cases.py`).
*   **Goal**: For each player, determine if they fit the "Polished Diamond" or "Uncut Gem" profile at the time of their breakout. Collect their `RS_RIM_APPETITE` and `CREATION_TAX` percentiles. This will validate our core hypothesis.

### Step 2: Implement the "Router"
*   **Action**: In `predict_conditional_archetype.py`, likely within the `predict_archetype_at_usage` function, create a "router" that determines a player's eligibility for each path.
*   **Logic**:
    *   `if player_data['RS_RIM_APPETITE_PERCENTILE'] > 0.90: is_eligible_for_physicality_path = True`
    *   `if player_data['CREATION_TAX_PERCENTILE'] > 0.75: is_eligible_for_skill_path = True`
    *   *Note: You will need to calculate and pass in these percentile values.*

### Step 3: Implement Path-Specific Gate Logic
*   **Action**: Refactor the existing gate logic (`apply_gates` or similar functions) to apply different rule sets based on the player's eligible path.
*   **Logic**:
    ```python
    # Initial star potential from model
    star_potential = model_prediction
    
    # Path-specific validation
    skill_path_passed = False
    if is_eligible_for_skill_path:
        # Apply strict gates for inefficiency and dependence
        star_potential_after_skill_gates = apply_skill_path_gates(player_data, star_potential)
        if star_potential_after_skill_gates > threshold:
             skill_path_passed = True

    physicality_path_passed = False
    if is_eligible_for_physicality_path:
        # Apply relaxed inefficiency gates but strict passivity gates
        star_potential_after_physicality_gates = apply_physicality_path_gates(player_data, star_potential)
        if star_potential_after_physicality_gates > threshold:
            physicality_path_passed = True
            
    # Final determination
    if skill_path_passed or physicality_path_passed:
        final_star_potential = max(star_potential_after_skill_gates, star_potential_after_physicality_gates)
    else:
        # If not eligible or fails both paths, apply default (strict) gates
        final_star_potential = apply_default_gates(player_data, star_potential)
    ```

### Step 4: Validate
*   **Action**: Run the full `test_latent_star_cases.py` test suite.
*   **Goal**:
    *   True Positive pass rate should increase to > 80%.
    *   False Positive pass rate should remain at 80% or higher.

This approach provides a clear, first-principles-based path to solving our core challenge and represents the next evolution of the model's architecture.
