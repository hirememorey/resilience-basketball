"""
Calculate Alpha Scores: Value - Price

PRINCIPLE 4: Alpha = Value - Price

The Axiom: In a salary-capped league, "Star" is a financial designation as much as a skill one.
- A "Bulldozer" on a rookie contract is High Alpha.
- A "Bulldozer" on a Supermax contract is Negative Alpha.

This script:
1. Loads model predictions (star_level_potential, archetype)
2. Maps predictions to salary data
3. Calculates Alpha = Value - Price
4. Identifies undervalued/overvalued players

Undervalued: Predicted "King" / "Bulldozer" making < $20M (The "Brunson Zone")
Overvalued: Predicted "Victim" / "Sniper" making > $30M (The "Tobias Harris Zone")
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Optional, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_salary_data(salary_file: Optional[Path] = None) -> pd.DataFrame:
    """
    Load salary data from CSV file.
    
    Expected columns:
    - PLAYER_ID or PLAYER_NAME
    - SEASON
    - SALARY (in millions USD)
    
    Data sources:
    - Spotrac: https://www.spotrac.com/nba/
    - Basketball Reference: https://www.basketball-reference.com/contracts/
    - HoopsHype: https://hoopshype.com/salaries/
    
    Args:
        salary_file: Path to salary CSV file. If None, returns empty DataFrame.
        
    Returns:
        DataFrame with salary data
    """
    if salary_file is None:
        logger.warning("No salary file provided. Alpha calculation will be skipped.")
        return pd.DataFrame()
    
    if not salary_file.exists():
        logger.error(f"Salary file not found: {salary_file}")
        return pd.DataFrame()
    
    df = pd.read_csv(salary_file)
    logger.info(f"Loaded salary data: {len(df)} player-seasons")
    
    return df


def get_star_level_column(df: pd.DataFrame) -> str:
    """Find the star level column in the dataframe."""
    possible_names = ['star_level_potential', 'CURRENT_STAR_LEVEL', 'AT_25_USG_STAR_LEVEL', 'AT_30_USG_STAR_LEVEL']
    for col in possible_names:
        if col in df.columns:
            return col
    return None

def get_archetype_column(df: pd.DataFrame) -> str:
    """Find the archetype column in the dataframe."""
    possible_names = ['predicted_archetype', 'CURRENT_ARCHETYPE', 'AT_25_USG_ARCHETYPE', 'AT_30_USG_ARCHETYPE']
    for col in possible_names:
        if col in df.columns:
            return col
    return None

def calculate_value_score(star_level: float, archetype: str) -> float:
    """
    Convert model prediction to a value score (0-100).
    
    Value is based on:
    - Star Level Potential (0-100%)
    - Archetype (King > Bulldozer > Sniper > Victim)
    
    Args:
        star_level: Star level potential (0-1)
        archetype: Predicted archetype
        
    Returns:
        Value score (0-100)
    """
    # Base value from star level
    base_value = star_level * 100
    
    # Archetype multiplier (adjusts value based on archetype quality)
    archetype_multipliers = {
        'King (Resilient Star)': 1.0,      # Full value
        'Bulldozer (Fragile Star)': 0.85,  # Slightly discounted (inefficient)
        'Sniper (Resilient Role)': 0.60,   # Role player value
        'Victim (Fragile Role)': 0.30      # Low value
    }
    
    multiplier = archetype_multipliers.get(archetype, 0.50)
    value_score = base_value * multiplier
    
    return value_score


def calculate_alpha_score(value_score: float, salary_millions: float) -> float:
    """
    Calculate Alpha = Value - Price.
    
    Alpha is positive when value exceeds price (undervalued).
    Alpha is negative when price exceeds value (overvalued).
    
    Args:
        value_score: Value score (0-100)
        salary_millions: Salary in millions USD
        
    Returns:
        Alpha score (can be negative or positive)
    """
    # Normalize salary to 0-100 scale
    # Max salary is ~$50M (supermax), so normalize: salary / 50 * 100
    max_salary = 50.0
    normalized_price = (salary_millions / max_salary) * 100
    
    # Alpha = Value - Price
    alpha = value_score - normalized_price
    
    return alpha


def categorize_alpha(alpha: float, salary_millions: float) -> str:
    """
    Categorize player based on Alpha score and salary.
    
    Categories:
    - "Undervalued Star": High value, low salary (Brunson Zone)
    - "Fair Value": Value ≈ Price
    - "Overvalued": Low value, high salary (Tobias Harris Zone)
    - "Rookie Contract": High value, rookie salary (special case)
    
    Args:
        alpha: Alpha score
        salary_millions: Salary in millions USD
        
    Returns:
        Category string
    """
    if salary_millions < 5.0 and alpha > 20:
        return "Rookie Contract Star"
    elif alpha > 15:
        return "Undervalued Star"
    elif alpha < -15:
        return "Overvalued"
    elif -5 <= alpha <= 5:
        return "Fair Value"
    elif alpha > 5:
        return "Slightly Undervalued"
    else:
        return "Slightly Overvalued"


def calculate_alpha_scores(
    predictions_df: pd.DataFrame,
    salary_df: pd.DataFrame,
    player_id_col: str = 'PLAYER_ID',
    player_name_col: str = 'PLAYER_NAME',
    season_col: str = 'SEASON',
    star_level_col: str = None,
    archetype_col: str = None
) -> pd.DataFrame:
    """
    Calculate Alpha scores for all player-seasons.
    
    Args:
        predictions_df: DataFrame with model predictions
        salary_df: DataFrame with salary data
        player_id_col: Column name for player ID
        player_name_col: Column name for player name
        season_col: Column name for season
        
    Returns:
        DataFrame with Alpha scores added
    """
    # Auto-detect column names if not provided
    if star_level_col is None:
        star_level_col = get_star_level_column(predictions_df)
    if archetype_col is None:
        archetype_col = get_archetype_column(predictions_df)
    
    if star_level_col is None or archetype_col is None:
        logger.error(f"Could not find required columns. Star level: {star_level_col}, Archetype: {archetype_col}")
        logger.info(f"Available columns: {predictions_df.columns.tolist()}")
        return predictions_df
    
    logger.info(f"Using star_level_col: {star_level_col}, archetype_col: {archetype_col}")
    
    if salary_df.empty:
        logger.warning("No salary data available. Adding placeholder Alpha columns.")
        predictions_df['VALUE_SCORE'] = predictions_df.apply(
            lambda row: calculate_value_score(
                row.get(star_level_col, 0),
                row.get(archetype_col, 'Victim (Fragile Role)')
            ),
            axis=1
        )
        predictions_df['SALARY_MILLIONS'] = np.nan
        predictions_df['ALPHA_SCORE'] = np.nan
        predictions_df['ALPHA_CATEGORY'] = 'No Salary Data'
        return predictions_df
    
    # Merge predictions with salary data
    merge_cols = [season_col]
    if player_id_col in predictions_df.columns and player_id_col in salary_df.columns:
        merge_cols.append(player_id_col)
    elif player_name_col in predictions_df.columns and player_name_col in salary_df.columns:
        merge_cols.append(player_name_col)
    else:
        logger.error("Cannot merge: missing player identifier columns")
        return predictions_df
    
    df_merged = pd.merge(
        predictions_df,
        salary_df,
        on=merge_cols,
        how='left',
        suffixes=('', '_salary')
    )
    
    # Calculate value scores
    df_merged['VALUE_SCORE'] = df_merged.apply(
        lambda row: calculate_value_score(
            row.get(star_level_col, 0),
            row.get(archetype_col, 'Victim (Fragile Role)')
        ),
        axis=1
    )
    
    # Calculate Alpha scores (where salary data is available)
    df_merged['ALPHA_SCORE'] = df_merged.apply(
        lambda row: calculate_alpha_score(
            row['VALUE_SCORE'],
            row.get('SALARY', row.get('SALARY_MILLIONS', np.nan))
        ) if pd.notna(row.get('SALARY', row.get('SALARY_MILLIONS', np.nan))) else np.nan,
        axis=1
    )
    
    # Categorize Alpha
    df_merged['ALPHA_CATEGORY'] = df_merged.apply(
        lambda row: categorize_alpha(
            row['ALPHA_SCORE'],
            row.get('SALARY', row.get('SALARY_MILLIONS', np.nan))
        ) if pd.notna(row['ALPHA_SCORE']) else 'No Salary Data',
        axis=1
    )
    
    # Rename salary column if needed
    if 'SALARY' in df_merged.columns and 'SALARY_MILLIONS' not in df_merged.columns:
        df_merged['SALARY_MILLIONS'] = df_merged['SALARY']
    
    logger.info(f"Calculated Alpha scores for {df_merged['ALPHA_SCORE'].notna().sum()}/{len(df_merged)} player-seasons")
    
    return df_merged


def identify_alpha_opportunities(df: pd.DataFrame, star_level_col: str = None) -> Dict[str, pd.DataFrame]:
    """
    Identify specific Alpha opportunities.
    
    Returns:
        Dictionary with:
        - 'undervalued_stars': Predicted stars making < $20M
        - 'overvalued_players': Predicted victims/snipers making > $30M
        - 'rookie_contract_stars': High-value players on rookie contracts
    """
    results = {}
    
    # Auto-detect star level column if not provided
    if star_level_col is None:
        star_level_col = get_star_level_column(df)
    
    if star_level_col is None:
        logger.warning("Could not find star level column for opportunity identification")
        return results
    
    # Undervalued Stars (Brunson Zone)
    undervalued = df[
        (df[star_level_col] >= 0.65) &
        (df['ALPHA_SCORE'] > 15) &
        (df['SALARY_MILLIONS'] < 20.0)
    ].copy()
    results['undervalued_stars'] = undervalued.sort_values('ALPHA_SCORE', ascending=False)
    
    # Overvalued Players (Tobias Harris Zone)
    overvalued = df[
        (df[star_level_col] < 0.55) &
        (df['ALPHA_SCORE'] < -15) &
        (df['SALARY_MILLIONS'] > 30.0)
    ].copy()
    results['overvalued_players'] = overvalued.sort_values('ALPHA_SCORE', ascending=True)
    
    # Rookie Contract Stars
    rookie_stars = df[
        (df[star_level_col] >= 0.65) &
        (df['SALARY_MILLIONS'] < 5.0)
    ].copy()
    results['rookie_contract_stars'] = rookie_stars.sort_values(star_level_col, ascending=False)
    
    logger.info(f"Found {len(undervalued)} undervalued stars, {len(overvalued)} overvalued players, {len(rookie_stars)} rookie contract stars")
    
    return results


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate Alpha Scores')
    parser.add_argument('--predictions', default='results/expanded_predictions.csv', 
                       help='Path to predictions CSV')
    parser.add_argument('--salary', default=None,
                       help='Path to salary data CSV (optional)')
    parser.add_argument('--output', default='results/alpha_scores.csv',
                       help='Output path for Alpha scores')
    
    args = parser.parse_args()
    
    # Load predictions
    predictions_df = pd.read_csv(args.predictions)
    logger.info(f"Loaded {len(predictions_df)} predictions")
    
    # Load salary data (if provided)
    salary_df = pd.DataFrame()
    if args.salary:
        salary_df = load_salary_data(Path(args.salary))
    
    # Calculate Alpha scores
    df_alpha = calculate_alpha_scores(predictions_df, salary_df)
    
    # Identify opportunities
    star_level_col = get_star_level_column(df_alpha)
    opportunities = identify_alpha_opportunities(df_alpha, star_level_col)
    
    # Save results
    df_alpha.to_csv(args.output, index=False)
    logger.info(f"✅ Saved Alpha scores to {args.output}")
    
    # Print summary
    if not salary_df.empty:
        print("\n=== ALPHA OPPORTUNITIES ===")
        star_level_col = get_star_level_column(df_alpha) or 'CURRENT_STAR_LEVEL'
        display_cols = ['PLAYER_NAME', 'SEASON', star_level_col, 'SALARY_MILLIONS', 'ALPHA_SCORE']
        
        print(f"\nUndervalued Stars (Brunson Zone): {len(opportunities['undervalued_stars'])}")
        if len(opportunities['undervalued_stars']) > 0:
            print(opportunities['undervalued_stars'][display_cols].head(10))
        
        print(f"\nOvervalued Players (Tobias Harris Zone): {len(opportunities['overvalued_players'])}")
        if len(opportunities['overvalued_players']) > 0:
            print(opportunities['overvalued_players'][display_cols].head(10))
        
        print(f"\nRookie Contract Stars: {len(opportunities['rookie_contract_stars'])}")
        if len(opportunities['rookie_contract_stars']) > 0:
            print(opportunities['rookie_contract_stars'][display_cols].head(10))
    else:
        print("\n⚠️  No salary data provided. Alpha calculation requires salary data.")
        print("To add salary data:")
        print("1. Collect salary data from Spotrac, Basketball Reference, or HoopsHype")
        print("2. Format as CSV with columns: PLAYER_ID/PLAYER_NAME, SEASON, SALARY (in millions)")
        print("3. Run: python src/nba_data/scripts/calculate_alpha_scores.py --salary data/salaries.csv")

