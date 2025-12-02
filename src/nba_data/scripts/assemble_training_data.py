import pandas as pd
import numpy as np
import argparse
import logging
from pathlib import Path
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_data(seasons):
    """Load all data files for requested seasons."""
    rs_data = []
    def_data = []
    po_data = []
    
    for season in seasons:
        # Load Regular Season
        rs_path = f"data/regular_season_{season}.csv"
        if Path(rs_path).exists():
            df = pd.read_csv(rs_path)
            df['SEASON'] = season
            rs_data.append(df)
        else:
            logger.warning(f"Missing {rs_path}")
            
        # Load Defensive Context
        def_path = f"data/defensive_context_{season}.csv"
        if Path(def_path).exists():
            df = pd.read_csv(def_path)
            df['SEASON'] = season
            def_data.append(df)
        else:
            logger.warning(f"Missing {def_path}")
            
        # Load Playoff Logs
        po_path = f"data/playoff_logs_{season}.csv"
        if Path(po_path).exists():
            df = pd.read_csv(po_path)
            df['SEASON'] = season
            po_data.append(df)
        else:
            logger.warning(f"Missing {po_path}")
            
    return (
        pd.concat(rs_data, ignore_index=True) if rs_data else pd.DataFrame(),
        pd.concat(def_data, ignore_index=True) if def_data else pd.DataFrame(),
        pd.concat(po_data, ignore_index=True) if po_data else pd.DataFrame()
    )

def parse_opponent(matchup, player_team_abbrev):
    """
    Parse opponent abbreviation from MATCHUP string.
    Format: "DEN vs. LAL" or "DEN @ LAL"
    """
    # Split by vs. or @
    if ' vs. ' in matchup:
        parts = matchup.split(' vs. ')
    elif ' @ ' in matchup:
        parts = matchup.split(' @ ')
    else:
        return None
        
    # Clean whitespace
    parts = [p.strip() for p in parts]
    player_team_abbrev = player_team_abbrev.strip()
    
    # One part is player's team, the other is opponent
    if parts[0] == player_team_abbrev:
        return parts[1]
    else:
        return parts[0]

def aggregate_playoff_series(po_logs, team_map):
    """
    Aggregate per-game logs into series-level stats.
    """
    logger.info("Aggregating playoff logs to series level...")
    
    # Ensure numeric columns
    numeric_cols = ['MIN', 'PTS', 'FGM', 'FGA', 'FTA', 'AST', 'POSS', 'AST_PCT', 'USG_PCT']
    for col in numeric_cols:
        if col in po_logs.columns:
            po_logs[col] = pd.to_numeric(po_logs[col], errors='coerce').fillna(0)
            
    # Parse Opponent
    po_logs['OPP_ABBREV'] = po_logs.apply(
        lambda row: parse_opponent(row['MATCHUP'], row['TEAM_ABBREVIATION']), axis=1
    )
    
    # Group by Player, Season, Opponent
    grouped = po_logs.groupby(['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'OPP_ABBREV'])
    
    series_data = []
    
    for name, group in grouped:
        player_id, player_name, season, opp_abbrev = name
        
        # Sums
        total_min = group['MIN'].sum()
        total_pts = group['PTS'].sum()
        total_poss = group['POSS'].sum()
        total_fga = group['FGA'].sum()
        total_fta = group['FTA'].sum()
        games_played = len(group)
        
        # Weighted Averages (AST%, USG%)
        # Avoid division by zero
        if total_min > 0:
            avg_ast_pct = (group['AST_PCT'] * group['MIN']).sum() / total_min
            avg_usg_pct = (group['USG_PCT'] * group['MIN']).sum() / total_min
        else:
            avg_ast_pct = 0
            avg_usg_pct = 0
            
        # Derived Metrics
        # TS% = PTS / (2 * (FGA + 0.44 * FTA))
        if (total_fga + 0.44 * total_fta) > 0:
            ts_pct = total_pts / (2 * (total_fga + 0.44 * total_fta))
        else:
            ts_pct = 0
            
        # PPG per 75 = (PTS / POSS) * 75
        if total_poss > 0:
            ppg75 = (total_pts / total_poss) * 75
        else:
            ppg75 = 0
            
        series_data.append({
            'PLAYER_ID': player_id,
            'PLAYER_NAME': player_name,
            'SEASON': season,
            'OPPONENT_ABBREV': opp_abbrev,
            'po_games_played': games_played,
            'po_minutes_total': total_min,
            'po_poss_total': total_poss,
            'po_fga': total_fga,
            'po_fta': total_fta,
            'po_pts': total_pts,
            'po_ts_pct': ts_pct,
            'po_ppg_per75': ppg75,
            'po_ast_pct': avg_ast_pct,
            'po_usg_pct': avg_usg_pct # Kept for reference
        })
        
    return pd.DataFrame(series_data)

def main():
    parser = argparse.ArgumentParser(description='Assemble Training Data')
    parser.add_argument('--output', default='data/training_dataset.csv', help='Output path')
    args = parser.parse_args()
    
    # Determine available seasons from file system
    files = list(Path('data').glob('regular_season_*.csv'))
    seasons = [f.stem.replace('regular_season_', '') for f in files]
    
    if not seasons:
        logger.error("No data found in data/")
        return

    logger.info(f"Found data for seasons: {seasons}")
    
    # Load Data
    rs_df, def_df, po_df = load_data(seasons)
    
    if rs_df.empty or def_df.empty or po_df.empty:
        logger.error("Missing required data streams. Aborting.")
        return
        
    # 1. Create Team Map (ID -> Abbrev and Abbrev -> ID)
    # Use RS data to get team mappings
    team_map_df = rs_df[['TEAM_ID', 'TEAM_ABBREVIATION']].drop_duplicates()
    abbrev_to_id = dict(zip(team_map_df.TEAM_ABBREVIATION, team_map_df.TEAM_ID))
    
    # 2. Process Playoff Data
    series_df = aggregate_playoff_series(po_df, abbrev_to_id)
    logger.info(f"Generated {len(series_df)} player-series records")
    if not series_df.empty:
        logger.info(f"Sample Series Data: \n{series_df.head()}")
        logger.info(f"Sample Opponents: {series_df['OPPONENT_ABBREV'].unique()}")
    
    # 3. Merge with Regular Season
    # We match on PLAYER_ID and SEASON
    # Rename RS columns first
    rs_cols = {
        'TS_PCT': 'rs_ts_pct',
        'AST_PCT': 'rs_ast_pct',
        'USG_PCT': 'rs_usg_pct',
        'PACE': 'rs_pace',
        'MIN': 'rs_min',
        'FGA': 'rs_fga',
        'FTA': 'rs_fta',
        'PTS': 'rs_pts', # Need to calculate per 75?
        # RS data is per 100 poss!
        # So PTS in RS data is actually Points per 100 Possessions?
        # Let's check collection script. 'PerMode': 'Per100Possessions'
        # Yes. So to get Per 75, we multiply by 0.75
    }
    
    rs_prep = rs_df[['PLAYER_ID', 'SEASON', 'TS_PCT', 'AST_PCT', 'USG_PCT', 'PTS', 'PACE', 'MIN', 'FGA', 'FTA']].copy()
    rs_prep = rs_prep.rename(columns=rs_cols)
    rs_prep['rs_ppg_per75'] = rs_prep['rs_pts'] * 0.75
    
    merged = pd.merge(
        series_df,
        rs_prep,
        on=['PLAYER_ID', 'SEASON'],
        how='inner'
    )
    
    logger.info(f"Merged with RS: {len(merged)} rows")

    # 4. Merge with Defensive Context
    # Map Opponent Abbrev to ID
    
    # DEBUG
    logger.info(f"Type of Opponent Abbrev: {merged['OPPONENT_ABBREV'].dtype}")
    logger.info(f"Sample Opponent Abbrev value: '{merged['OPPONENT_ABBREV'].iloc[0]}' (type: {type(merged['OPPONENT_ABBREV'].iloc[0])})")
    
    sample_key = list(abbrev_to_id.keys())[0]
    logger.info(f"Sample Map Key: '{sample_key}' (type: {type(sample_key)})")
    
    # Attempt direct lookup
    test_val = merged['OPPONENT_ABBREV'].iloc[0]
    if test_val in abbrev_to_id:
        logger.info(f"Direct lookup of '{test_val}' SUCCESS: {abbrev_to_id[test_val]}")
    else:
        logger.info(f"Direct lookup of '{test_val}' FAILED")
        
    merged['OPPONENT_TEAM_ID'] = merged['OPPONENT_ABBREV'].map(abbrev_to_id)
    
    # Debug mapping
    missing_opp = merged[merged['OPPONENT_TEAM_ID'].isna()]['OPPONENT_ABBREV'].unique()
    if len(missing_opp) > 0:
        logger.warning(f"Failed to map these opponents: {missing_opp}")
        logger.info(f"Available abbreviations: {list(abbrev_to_id.keys())[:10]}...")
    
    # Drop rows where opponent mapping failed (e.g. defunct teams or data mismatch)
    merged = merged.dropna(subset=['OPPONENT_TEAM_ID'])
    merged['OPPONENT_TEAM_ID'] = merged['OPPONENT_TEAM_ID'].astype(int)
    
    # Join with Defense
    # Defense data has TEAM_ID and SEASON
    final_df = pd.merge(
        merged,
        def_df[['TEAM_ID', 'SEASON', 'def_context_score']],
        left_on=['OPPONENT_TEAM_ID', 'SEASON'],
        right_on=['TEAM_ID', 'SEASON'],
        how='inner'
    )
    
    # Rename for consistency
    final_df = final_df.rename(columns={'def_context_score': 'opp_def_context_score'})
    
    # Final Cleanup
    cols_to_keep = [
        'PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'OPPONENT_ABBREV',
        'rs_ts_pct', 'rs_ppg_per75', 'rs_ast_pct', 'rs_usg_pct',
        'rs_pace', 'rs_min', 'rs_fga', 'rs_fta', 'rs_pts',
        'opp_def_context_score',
        'po_ts_pct', 'po_ppg_per75', 'po_ast_pct',
        'po_games_played', 'po_minutes_total', 'po_poss_total', 'po_fga', 'po_fta', 'po_pts'
    ]
    
    final_df = final_df[cols_to_keep]
    
    # Save
    final_df.to_csv(args.output, index=False)
    logger.info(f"✅ Successfully saved training dataset to {args.output} ({len(final_df)} rows)")

if __name__ == "__main__":
    main()

