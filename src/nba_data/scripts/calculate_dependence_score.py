import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Normalization constants (Elite Standards)
ELITE_RIM_APPETITE = 0.40
ELITE_FTR = 0.50
ELITE_SQ_DELTA = 0.06
ELITE_CREATION_TAX = 0.0  # Neutral or better is elite
MIN_CREATION_TAX = -0.10  # Assumed floor for normalization (Replacement Level Creator)
ELITE_EFG_ISO = 0.60
MIN_EFG_ISO = 0.30

def calculate_dependence_scores_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates DEPENDENCE_SCORE for a dataframe of players using the 'Two Doors' framework.
    
    Door A: Physicality (Rim Pressure, Free Throws)
    Door B: Skill (Shot Quality Generation, Creation Efficiency)
    
    Dependence = 1.0 - Max(Physicality, Skill)
    """
    if df.empty:
        return df

    # CRITICAL: Enforce Single Source of Truth
    # The dataframe MUST already contain SHOT_QUALITY_GENERATION_DELTA from the upstream pipeline.
    if 'SHOT_QUALITY_GENERATION_DELTA' not in df.columns:
        raise ValueError("Critical Feature Missing: SHOT_QUALITY_GENERATION_DELTA must be present in input DataFrame before calculating dependence.")

    # We need to compute PHYSICALITY_SCORE and SKILL_SCORE for each row
    # We can use apply() for simplicity and readability, as this matches the row-based logic
    
    # Define a wrapper to apply to each row
    def apply_scoring(row):
        scores = calculate_dependence_score(row)
        return pd.Series({
            'DEPENDENCE_SCORE': scores.get('dependence_score', 1.0),
            'RAW_DEPENDENCE_SCORE': scores.get('raw_dependence_score', 1.0),
            'PROJECTED_DEPENDENCE_SCORE': scores.get('projected_dependence_score', 1.0),
            'PHYSICALITY_SCORE': scores.get('physicality_score', 0.0),
            'SKILL_SCORE': scores.get('skill_score', 0.0)
        })

    # Apply calculations
    score_cols = df.apply(apply_scoring, axis=1)
    
    # Assign back to dataframe
    df['DEPENDENCE_SCORE'] = score_cols['DEPENDENCE_SCORE']
    df['RAW_DEPENDENCE_SCORE'] = score_cols['RAW_DEPENDENCE_SCORE']
    df['PROJECTED_DEPENDENCE_SCORE'] = score_cols['PROJECTED_DEPENDENCE_SCORE']
    df['PHYSICALITY_SCORE'] = score_cols['PHYSICALITY_SCORE']
    df['SKILL_SCORE'] = score_cols['SKILL_SCORE']
    
    return df

def calculate_dependence_score(row: pd.Series) -> dict:
    """
    Calculates Dependence Score for a single player (row).
    This now includes a projection based on latent potential.
    """
    # 1. Calculate Raw Physicality and Skill Scores
    physicality_score = _calculate_physicality_score(row)
    skill_score = _calculate_skill_score(row)
    
    # 2. Calculate Raw Dependence Score (pre-projection)
    raw_dependence = 1.0 - max(physicality_score, skill_score)
    
    # 3. Calculate Projected Dependence by applying latent discount
    projected_dependence = _apply_latent_dependence_projection(row, raw_dependence)
    
    # 4. Clip to valid range [0, 1]
    final_dependence_score = max(0.0, min(1.0, projected_dependence))
    
    return {
        'dependence_score': final_dependence_score,
        'raw_dependence_score': raw_dependence,
        'projected_dependence_score': projected_dependence,
        'physicality_score': physicality_score,
        'skill_score': skill_score
    }

def _apply_latent_dependence_projection(row: pd.Series, raw_dependence: float) -> float:
    """
    Adjusts the raw dependence score downwards based on latent creation potential.
    Includes principled mitigations for common failure modes.
    """
    latent_score = float(row.get('latent_score', 0.0))
    sq_delta = float(row.get('SHOT_QUALITY_GENERATION_DELTA', 0.0))
    inefficient_volume_score = float(row.get('INEFFICIENT_VOLUME_SCORE', 0.0))

    if np.isnan(latent_score): latent_score = 0.0
    if np.isnan(sq_delta): sq_delta = 0.0
    if np.isnan(inefficient_volume_score): inefficient_volume_score = 0.0

    # If no latent potential, no adjustment is made.
    if latent_score <= 0.0:
        return raw_dependence

    # --- 1. Base Discount Calculation ---
    # Principle: Potential Energy has a Vector.
    # We use a sqrt function to reflect that the journey to independence is non-linear
    # and harder to complete than the initial flashes of skill. Max 25% discount.
    max_discount = 0.25
    base_discount = max_discount * np.sqrt(min(latent_score, 1.0))

    # --- 2. Mitigations (Continuous Gradients, Not Hard Gates) ---
    
    # Mitigation A: The "Jordan Poole Anomaly" (False Prophet)
    # Principle: Pressure acts as a Filter. True creators generate quality shots.
    # We use a sigmoid function to create a smooth gradient.
    # If sq_delta is highly positive, full discount. If negative, discount is dampened.
    # k=50 makes the transition around 0 quite sensitive.
    shot_creation_truth_serum = 1 / (1 + np.exp(-50 * sq_delta))

    # Mitigation B: The "Tank Commander" Trap (Empty Calories)
    # Principle: Efficiency must survive Volume.
    # We create a penalty that scales with inefficient volume.
    # A score of 0.10 or higher results in a near-zero multiplier.
    efficiency_gate = max(0.0, 1.0 - (inefficient_volume_score * 10))

    # --- 3. Final Discount Calculation ---
    # The final discount is the base discount, modulated by our two "truth serums".
    final_discount = base_discount * shot_creation_truth_serum * efficiency_gate
    
    projected_dependence = raw_dependence - final_discount
    
    return projected_dependence


def _calculate_physicality_score(row: pd.Series) -> float:
    """
    Door A: The Force
    Measures ability to impose will via Rim/FTs.
    """
    # Extract inputs with defaults
    rim_appetite = float(row.get('RS_RIM_APPETITE', 0.0))
    ftr = float(row.get('RS_FTr', 0.0))
    creation_vol_ratio = float(row.get('CREATION_VOLUME_RATIO', 0.0))
    
    # Handle NaN
    if np.isnan(rim_appetite): rim_appetite = 0.0
    if np.isnan(ftr): ftr = 0.0
    if np.isnan(creation_vol_ratio): creation_vol_ratio = 0.0
    
    # Normalize inputs
    # Elite Rim Appetite: 0.40 (Normalize 0-0.40)
    norm_rim = min(rim_appetite / ELITE_RIM_APPETITE, 1.0)
    
    # Elite FTr: 0.50 (Normalize 0-0.50)
    norm_ftr = min(ftr / ELITE_FTR, 1.0)
    
    # Weighted Sum: FTr (60%) + Rim (40%)
    raw_score = (norm_ftr * 0.60) + (norm_rim * 0.40)
    
    # The Sabonis Constraint:
    # If CREATION_VOLUME_RATIO < 0.15 (System Finisher/Hub), multiply by 0.5
    if creation_vol_ratio < 0.15:
        raw_score *= 0.5
        
    return max(0.0, min(1.0, raw_score))

def _calculate_skill_score(row: pd.Series) -> float:
    """
    Door B: The Craft
    Measures ability to generate mathematical advantage.
    """
    # Extract inputs
    sq_delta = float(row.get('SHOT_QUALITY_GENERATION_DELTA', 0.0))
    creation_tax = float(row.get('CREATION_TAX', -0.20)) # Default to poor if missing
    efg_iso = float(row.get('EFG_ISO_WEIGHTED', 0.40)) # Default to avg if missing
    
    # Handle NaN
    if np.isnan(sq_delta): sq_delta = 0.0
    if np.isnan(creation_tax): creation_tax = -0.20
    if np.isnan(efg_iso): efg_iso = 0.40
    
    # The Empty Calories Constraint is applied *after* the initial calculation.
    
    # Normalize Inputs
    
    # Elite SQ Delta: 0.06 (Normalize 0-0.06)
    norm_sq = min(sq_delta / ELITE_SQ_DELTA, 1.0) if sq_delta > 0 else 0.0
    
    # Elite Creation Tax: 0.0 (Neutral or better)
    # Map from [MIN_CREATION_TAX, ELITE_CREATION_TAX] to [0, 1]
    # e.g. [-0.25, 0.0] -> [0, 1]
    if creation_tax >= ELITE_CREATION_TAX:
        norm_tax = 1.0
    else:
        norm_tax = (creation_tax - MIN_CREATION_TAX) / (ELITE_CREATION_TAX - MIN_CREATION_TAX)
        norm_tax = max(0.0, min(1.0, norm_tax))
        
    # EFG ISO Weighted
    # Map from [MIN_EFG_ISO, ELITE_EFG_ISO] to [0, 1]
    if efg_iso >= ELITE_EFG_ISO:
        norm_efg = 1.0
    else:
        norm_efg = (efg_iso - MIN_EFG_ISO) / (ELITE_EFG_ISO - MIN_EFG_ISO)
        norm_efg = max(0.0, min(1.0, norm_efg))
    
    # Weights: Creation Tax (60%) + SQ Delta (20%) + EFG (20%)
    # PHYSICS CORRECTION: Prioritize Resilience (Tax) over Production (Delta)
    skill_score = (norm_tax * 0.60) + (norm_sq * 0.20) + (norm_efg * 0.20)

    # Elite Delta Bonus: If SQ Delta is elite, give a boost
    # Reduced impact to prevent overriding resilience failures
    if sq_delta > 0.04:
        skill_score += 0.1

    # The Jordan Poole Penalty (Luxury Component Constraint):
    # High Production (SQ Delta > 0.04) but Dependent on System (Creation Tax < -0.03)
    # This identifies "System Merchants" and penalizes their Skill Score.
    if sq_delta > 0.04 and creation_tax < -0.03:
        skill_score *= 0.75 # Penalize score by 25%
    
    # The Empty Calories Constraint:
    # If SHOT_QUALITY_GENERATION_DELTA < 0.0 (Negative), SKILL_SCORE is Hard Capped at 0.1
    # This forces Dependence Score to be at least 0.90 (High Dependence)
    if sq_delta < 0.0:
        skill_score = min(skill_score, 0.10)
        
    return max(0.0, min(1.0, skill_score))
