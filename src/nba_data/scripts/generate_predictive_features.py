import pandas as pd
import numpy as np
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def calculate_game_score(row):
    """Calculate Game Score metric."""
    # GmSc = PTS + 0.4*FG - 0.7*FGA - 0.4*(FTA - FT) + 0.7*ORB + 0.3*DRB + STL + 0.7*AST + 0.7*BLK - 0.4*PF - TOV
    try:
        pts = row['PTS']
        fgm = row['FGM']
        fga = row['FGA']
        fta = row['FTA']
        ftm = row['FTM']
        orb = row.get('OREB', 0)
        drb = row.get('DREB', 0)
        stl = row['STL']
        ast = row['AST']
        blk = row['BLK']
        pf = row['PF']
        tov = row['TOV']
        
        gmsc = pts + 0.4*fgm - 0.7*fga - 0.4*(fta - ftm) + 0.7*orb + 0.3*drb + stl + 0.7*ast + 0.7*blk - 0.4*pf - tov
        return gmsc
    except KeyError as e:
        # logger.warning(f"Missing column for Game Score: {e}")
        return 0

def generate_features(season):
    """Generate predictive features for a given season."""
    logger.info(f"Generating features for {season}...")
    
    # 1. Load Data
    logs_path = Path(f"data/rs_game_logs_{season}.csv")
    def_path = Path(f"data/defensive_context_{season}.csv")
    
    if not logs_path.exists() or not def_path.exists():
        logger.error(f"Missing input files for {season}")
        return
        
    logs = pd.read_csv(logs_path)
    def_df = pd.read_csv(def_path)
    
    # 2. Identify Top 10 Defenses
    # Sort by DEF_RATING ascending (lower is better)
    top_10_def = def_df.sort_values('DEF_RATING', ascending=True).head(10)
    top_10_ids = top_10_def['TEAM_ID'].tolist()
    
    logger.info(f"Top 10 Defenses for {season}: {top_10_def['TEAM_NAME'].tolist()}")
    
    # 3. Feature Engineering
    
    # Add Game Score
    logs['GAME_SCORE'] = logs.apply(calculate_game_score, axis=1)
    
    # Add Opponent ID mapping (MATCHUP column usually has "LAL vs. DEN" or "LAL @ DEN")
    # But the logs usually have 'MATCHUP' and 'OPPONENT_TEAM_ID' isn't always there?
    # Let's check the columns.
    # The collected logs merge Base and Advanced. Base usually has MATCHUP.
    # Neither usually has explicit OPPONENT_TEAM_ID unless we join.
    # However, Base logs DO have a column 'MATCHUP'.
    # And importantly, we don't easily have the opponent team ID directly in the row unless we parse it.
    # Wait, the client.get_player_game_logs endpoint result usually contains 'MATCHUP'
    # Example: "BOS @ MIA"
    # We need to map "MIA" to its ID to check if it's in top_10_ids.
    
    # Create Team Abbrev -> ID map from defensive context?
    # No, defensive context has IDs and Names, but maybe not abbreviations.
    # Let's check regular_season_{season}.csv for the mapping of ID <-> Abbrev
    rs_path = Path(f"data/regular_season_{season}.csv")
    rs_df = pd.read_csv(rs_path)
    team_map = rs_df[['TEAM_ID', 'TEAM_ABBREVIATION']].drop_duplicates()
    abbrev_to_id = dict(zip(team_map.TEAM_ABBREVIATION, team_map.TEAM_ID))
    
    def parse_opponent_id(matchup, player_team_abbrev):
        if pd.isna(matchup): return None
        # Split by vs. or @
        if ' vs. ' in matchup:
            parts = matchup.split(' vs. ')
        elif ' @ ' in matchup:
            parts = matchup.split(' @ ')
        else:
            return None
            
        parts = [p.strip() for p in parts]
        
        # Opponent is the part that is NOT the player's team
        # BUT we need the player's team abbreviation for this row.
        # The logs might not have TEAM_ABBREVIATION if we didn't ensure it.
        # Usually Base logs have 'TEAM_ABBREVIATION'.
        
        if parts[0] == player_team_abbrev:
            opp_abbrev = parts[1]
        else:
            opp_abbrev = parts[0]
            
        return abbrev_to_id.get(opp_abbrev)

    # Apply parsing
    logs['OPPONENT_TEAM_ID'] = logs.apply(lambda row: parse_opponent_id(row['MATCHUP'], row['TEAM_ABBREVIATION']), axis=1)
    
    # Filter logs vs Top 10
    logs['IS_TOP_10_DEF'] = logs['OPPONENT_TEAM_ID'].isin(top_10_ids)
    
    # Aggregation
    player_stats = []
    
    grouped = logs.groupby(['PLAYER_ID', 'PLAYER_NAME'])
    
    for name, group in grouped:
        player_id, player_name = name
        
        # Overall consistency
        gmsc_std = group['GAME_SCORE'].std()
        if pd.isna(gmsc_std): gmsc_std = 0
        
        # Vs Top 10 Stats
        vs_top10 = group[group['IS_TOP_10_DEF']]
        
        if len(vs_top10) > 0:
            # Calculate weighted averages for rates, simple avg for others
            # TS% = PTS / (2 * (FGA + 0.44 * FTA))
            # We need to sum the components first
            t10_pts = vs_top10['PTS'].sum()
            t10_fga = vs_top10['FGA'].sum()
            t10_fta = vs_top10['FTA'].sum()
            t10_poss = vs_top10['POSS'].sum() if 'POSS' in vs_top10.columns else 0 # Check POSS column
            
            if (t10_fga + 0.44 * t10_fta) > 0:
                ts_pct_top10 = t10_pts / (2 * (t10_fga + 0.44 * t10_fta))
            else:
                ts_pct_top10 = 0
                
            # PPG per 75 vs Top 10
            # Note: POSS is usually in Advanced logs.
            if t10_poss > 0:
                ppg75_top10 = (t10_pts / t10_poss) * 75
            else:
                ppg75_top10 = 0
                
            # AST% vs Top 10 (Average of game AST% weighted by minutes?)
            # Or calculated from totals if we had team totals (which we don't).
            # Weighted average by MIN is best approximation for rate stats
            t10_min = vs_top10['MIN'].sum()
            if t10_min > 0:
                ast_pct_top10 = (vs_top10['AST_PCT'] * vs_top10['MIN']).sum() / t10_min
                usg_pct_top10 = (vs_top10['USG_PCT'] * vs_top10['MIN']).sum() / t10_min
            else:
                ast_pct_top10 = 0
                usg_pct_top10 = 0
                
            games_vs_top10 = len(vs_top10)
            
        else:
            ts_pct_top10 = 0
            ppg75_top10 = 0
            ast_pct_top10 = 0
            usg_pct_top10 = 0
            games_vs_top10 = 0
            
        player_stats.append({
            'PLAYER_ID': player_id,
            'PLAYER_NAME': player_name,
            'SEASON': season,
            'consistency_gmsc_std': gmsc_std,
            'ts_pct_vs_top10': ts_pct_top10,
            'ppg_per75_vs_top10': ppg75_top10,
            'ast_pct_vs_top10': ast_pct_top10,
            'usg_pct_vs_top10': usg_pct_top10,
            'games_vs_top10': games_vs_top10
        })
        
    results_df = pd.DataFrame(player_stats)
    
    # Save
    out_path = f"data/predictive_features_{season}.csv"
    results_df.to_csv(out_path, index=False)
    logger.info(f"Saved predictive features to {out_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate Predictive Features')
    parser.add_argument('--seasons', nargs='+', help='Seasons to process', required=True)
    args = parser.parse_args()
    
    for season in args.seasons:
        generate_features(season)

if __name__ == "__main__":
    main()

