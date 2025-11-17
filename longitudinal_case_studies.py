"""
Longitudinal Resilience Analysis for Case Studies

Analyzes four case study players:
1. Ben Simmons (2017-2021): Test stagnation hypothesis
2. Joel Embiid (2017-2024): Test development hypothesis  
3. Giannis Antetokounmpo (2017-2021): Test transformation hypothesis
4. James Harden (2016-2025): Test elite versatility ceiling

Includes usage-adjusted efficiency and other critical improvements.
"""

import sqlite3
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List
from scipy import stats
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# Case study players
CASE_STUDIES = {
    "Ben Simmons": {
        "player_id": 1627732,
        "seasons": ["2017-18", "2018-19", "2019-20", "2020-21"],
        "hypothesis": "stagnation"
    },
    "Joel Embiid": {
        "player_id": 203954,
        "seasons": ["2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24"],
        "hypothesis": "development"
    },
    "Giannis Antetokounmpo": {
        "player_id": 203507,
        "seasons": ["2017-18", "2018-19", "2019-20", "2020-21"],
        "hypothesis": "transformation"
    },
    "James Harden": {
        "player_id": 201935,
        "seasons": ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24"],
        "hypothesis": "elite_versatility"
    }
}

DB_PATH = "data/nba_stats.db"


def get_db_connection():
    """Establish database connection."""
    return sqlite3.connect(DB_PATH)


def fetch_player_stats(conn: sqlite3.Connection, player_id: int, season: str, 
                       season_type: str = "Regular Season") -> Optional[pd.Series]:
    """Fetch player advanced stats for a given season."""
    table = "player_advanced_stats" if season_type == "Regular Season" else "player_playoff_advanced_stats"
    
    query = f"""
        SELECT true_shooting_percentage, usage_percentage, points_per_possession,
               turnover_percentage, effective_field_goal_percentage
        FROM {table}
        WHERE player_id = ? AND season = ?
        LIMIT 1
    """
    
    df = pd.read_sql_query(query, conn, params=(player_id, season))
    return df.iloc[0] if not df.empty else None


def fetch_league_averages(conn: sqlite3.Connection, season: str, 
                          season_type: str = "Regular Season") -> Dict[str, float]:
    """Fetch league average stats for a season."""
    table = "player_advanced_stats" if season_type == "Regular Season" else "player_playoff_advanced_stats"
    
    query = f"""
        SELECT 
            AVG(true_shooting_percentage) as avg_ts,
            AVG(usage_percentage) as avg_usage,
            AVG(points_per_possession) as avg_ppp,
            AVG(turnover_percentage) as avg_tov
        FROM {table}
        WHERE season = ? AND true_shooting_percentage IS NOT NULL
    """
    
    df = pd.read_sql_query(query, conn, params=(season,))
    return df.iloc[0].to_dict() if not df.empty else {}


def build_usage_efficiency_model(conn: sqlite3.Connection, player_id: int, 
                                  seasons: List[str]) -> Optional[LinearRegression]:
    """
    Build player-specific TS% = f(usage_rate) model from regular season data.
    Returns regression model or None if insufficient data.
    """
    usage_data = []
    ts_data = []
    
    for season in seasons:
        stats = fetch_player_stats(conn, player_id, season, "Regular Season")
        if stats is not None and pd.notna(stats['usage_percentage']) and pd.notna(stats['true_shooting_percentage']):
            usage_data.append(stats['usage_percentage'])
            ts_data.append(stats['true_shooting_percentage'])
    
    if len(usage_data) < 3:  # Need at least 3 data points
        return None
    
    # Fit linear regression: TS% = a + b * Usage%
    X = np.array(usage_data).reshape(-1, 1)
    y = np.array(ts_data)
    
    model = LinearRegression()
    model.fit(X, y)
    
    return model


def calculate_usage_adjusted_ts_delta(conn: sqlite3.Connection, player_id: int,
                                      season: str, reg_seasons: List[str]) -> Optional[float]:
    """
    Calculate usage-adjusted TS% delta.
    Compares actual playoff TS% to expected TS% at playoff usage rate.
    """
    # Get regular season stats
    reg_stats = fetch_player_stats(conn, player_id, season, "Regular Season")
    if reg_stats is None:
        return None
    
    # Get playoff stats
    po_stats = fetch_player_stats(conn, player_id, season, "Playoffs")
    if po_stats is None:
        return None
    
    # Build usage-efficiency model
    model = build_usage_efficiency_model(conn, player_id, reg_seasons)
    if model is None:
        # Fallback: simple ratio if we can't build model
        if pd.notna(reg_stats['true_shooting_percentage']) and pd.notna(po_stats['true_shooting_percentage']):
            return (po_stats['true_shooting_percentage'] / reg_stats['true_shooting_percentage']) * 100
        return None
    
    # Predict expected TS% at playoff usage rate
    playoff_usage = po_stats['usage_percentage']
    if pd.isna(playoff_usage):
        return None
    
    expected_ts_at_playoff_usage = model.predict([[playoff_usage]])[0]
    actual_playoff_ts = po_stats['true_shooting_percentage']
    
    if pd.isna(actual_playoff_ts) or expected_ts_at_playoff_usage <= 0:
        return None
    
    # Usage-adjusted delta: actual vs expected at that usage
    usage_adjusted_delta = (actual_playoff_ts / expected_ts_at_playoff_usage) * 100
    
    return usage_adjusted_delta


def calculate_performance_resilience(conn: sqlite3.Connection, player_id: int,
                                     season: str, reg_seasons: List[str]) -> Dict[str, float]:
    """
    Calculate Performance Resilience with usage adjustment.
    Returns dict with raw and usage-adjusted metrics.
    """
    reg_stats = fetch_player_stats(conn, player_id, season, "Regular Season")
    po_stats = fetch_player_stats(conn, player_id, season, "Playoffs")
    
    if reg_stats is None or po_stats is None:
        return {}
    
    results = {}
    
    # Raw TS% delta
    if pd.notna(reg_stats['true_shooting_percentage']) and pd.notna(po_stats['true_shooting_percentage']):
        raw_ts_delta = (po_stats['true_shooting_percentage'] / reg_stats['true_shooting_percentage']) * 100
        results['raw_ts_delta'] = raw_ts_delta
    else:
        results['raw_ts_delta'] = None
    
    # Usage-adjusted TS% delta
    usage_adj_delta = calculate_usage_adjusted_ts_delta(conn, player_id, season, reg_seasons)
    results['usage_adjusted_ts_delta'] = usage_adj_delta
    
    # PPP delta
    if pd.notna(reg_stats['points_per_possession']) and pd.notna(po_stats['points_per_possession']):
        ppp_delta = (po_stats['points_per_possession'] / reg_stats['points_per_possession']) * 100
        results['ppp_delta'] = ppp_delta
    else:
        results['ppp_delta'] = None
    
    # TOV% delta (inverted - lower is better)
    if pd.notna(reg_stats['turnover_percentage']) and pd.notna(po_stats['turnover_percentage']):
        if po_stats['turnover_percentage'] > 0:
            tov_delta = (reg_stats['turnover_percentage'] / po_stats['turnover_percentage']) * 100
            results['tov_delta'] = tov_delta
        else:
            results['tov_delta'] = None
    else:
        results['tov_delta'] = None
    
    # Usage change
    if pd.notna(reg_stats['usage_percentage']) and pd.notna(po_stats['usage_percentage']):
        usage_change = po_stats['usage_percentage'] - reg_stats['usage_percentage']
        results['usage_change'] = usage_change
        results['reg_usage'] = reg_stats['usage_percentage']
        results['po_usage'] = po_stats['usage_percentage']
    else:
        results['usage_change'] = None
    
    # Combined performance resilience (weighted average)
    deltas = []
    weights = []
    
    if results['usage_adjusted_ts_delta'] is not None:
        deltas.append(results['usage_adjusted_ts_delta'])
        weights.append(0.5)
    
    if results['ppp_delta'] is not None:
        deltas.append(results['ppp_delta'])
        weights.append(0.3)
    
    if results['tov_delta'] is not None:
        deltas.append(results['tov_delta'])
        weights.append(0.2)
    
    if deltas:
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        results['performance_resilience'] = sum(d * w for d, w in zip(deltas, normalized_weights))
    else:
        results['performance_resilience'] = None
    
    return results


def calculate_spatial_diversity(conn: sqlite3.Connection, player_id: int,
                                season: str, season_type: str) -> Optional[float]:
    """Calculate spatial diversity score using shot location data."""
    st_query = season_type.replace(" ", "")
    query = f"""
        SELECT loc_x, loc_y, shot_made_flag, shot_type
        FROM player_shot_locations
        WHERE player_id = ? AND season = ? AND season_type = ?
    """
    
    df = pd.read_sql_query(query, conn, params=(player_id, season, st_query))
    if df.empty:
        return None
    
    # Define court zones
    x, y = df['loc_x'].abs(), df['loc_y']
    is_ra = (x <= 4) & (y <= 4.25)
    is_paint = (x <= 8) & (y <= 19) & ~is_ra
    is_mid_range = (
        ((x > 8) & (y <= 19)) |
        ((x <= 22) & (y > 19)) |
        (df['shot_type'] == '2PT Field Goal') & ~is_ra & ~is_paint
    )
    is_corner_3 = (x > 22) & (y <= 7.8)
    is_above_break_3 = (df['shot_type'] == '3PT Field Goal') & ~is_corner_3
    
    conditions = [
        is_ra, is_paint, is_mid_range,
        (is_corner_3) & (df['loc_x'] < 0),
        (is_corner_3) & (df['loc_x'] >= 0),
        is_above_break_3
    ]
    choices = [
        'Restricted Area', 'In The Paint (Non-RA)', 'Mid-Range',
        'Left Corner 3', 'Right Corner 3', 'Above the Break 3'
    ]
    
    df['zone'] = pd.Series(np.select(conditions, choices, default='Other'), index=df.index)
    
    # Calculate zone stats
    zone_attempts = df['zone'].value_counts()
    zone_makes = df[df['shot_made_flag'] == 1]['zone'].value_counts()
    three_pm = df[(df['shot_made_flag'] == 1) & (df['shot_type'] == '3PT Field Goal')]['zone'].value_counts()
    
    stats_df = pd.DataFrame({
        'attempts': zone_attempts,
        'makes': zone_makes,
        '3pm': three_pm
    }).fillna(0)
    
    if stats_df['attempts'].sum() == 0:
        return None
    
    # Calculate eFG%
    stats_df['efg'] = (stats_df['makes'] + 0.5 * stats_df['3pm']) / stats_df['attempts']
    
    # Get league averages for zones (simplified - would need actual league averages)
    # For now, use equal weighting
    stats_df['weighted_volume'] = stats_df['attempts'] * stats_df['efg']
    
    # Calculate HHI
    proportions = stats_df['weighted_volume'] / stats_df['weighted_volume'].sum()
    hhi = (proportions ** 2).sum()
    diversity_score = (1 - hhi) * 100
    
    return diversity_score


def calculate_playtype_diversity(conn: sqlite3.Connection, player_id: int,
                                  season: str, season_type: str) -> Optional[float]:
    """Calculate play-type diversity score."""
    table = "player_playtype_stats" if season_type == "Regular Season" else "player_playoff_playtype_stats"
    
    query = f"""
        SELECT play_type, possessions, points_per_possession
        FROM {table}
        WHERE player_id = ? AND season = ?
    """
    
    df = pd.read_sql_query(query, conn, params=(player_id, season))
    if df.empty:
        return None
    
    # Simplified - would need league averages for proper weighting
    df['weighted_volume'] = df['possessions'] * df['points_per_possession']
    
    if df['weighted_volume'].sum() == 0:
        return None
    
    proportions = df['weighted_volume'] / df['weighted_volume'].sum()
    hhi = (proportions ** 2).sum()
    diversity_score = (1 - hhi) * 100
    
    return diversity_score


def calculate_creation_diversity(conn: sqlite3.Connection, player_id: int,
                                  season: str, season_type: str) -> Optional[float]:
    """Calculate creation diversity score."""
    table = "player_tracking_stats" if season_type == "Regular Season" else "player_playoff_tracking_stats"
    
    query = f"""
        SELECT 
            catch_shoot_field_goals_attempted,
            pull_up_field_goals_attempted,
            drives,
            catch_shoot_effective_field_goal_percentage,
            pull_up_effective_field_goal_percentage,
            drive_points
        FROM {table}
        WHERE player_id = ? AND season = ?
    """
    
    df = pd.read_sql_query(query, conn, params=(player_id, season))
    if df.empty:
        return None
    
    row = df.iloc[0]
    
    cs_attempts = row['catch_shoot_field_goals_attempted'] or 0
    pu_attempts = row['pull_up_field_goals_attempted'] or 0
    drives = row['drives'] or 0
    
    cs_efg = row['catch_shoot_effective_field_goal_percentage'] or 0
    pu_efg = row['pull_up_effective_field_goal_percentage'] or 0
    drive_ppd = (row['drive_points'] / drives) if drives > 0 else 0
    
    creation_data = pd.DataFrame([
        {'type': 'Catch & Shoot', 'volume': cs_attempts, 'efficiency': cs_efg},
        {'type': 'Pull-Up', 'volume': pu_attempts, 'efficiency': pu_efg},
        {'type': 'Drives', 'volume': drives, 'efficiency': drive_ppd}
    ])
    
    creation_data['weighted_volume'] = creation_data['volume'] * creation_data['efficiency']
    
    if creation_data['weighted_volume'].sum() == 0:
        return None
    
    proportions = creation_data['weighted_volume'] / creation_data['weighted_volume'].sum()
    hhi = (proportions ** 2).sum()
    diversity_score = (1 - hhi) * 100
    
    return diversity_score


def calculate_method_resilience(conn: sqlite3.Connection, player_id: int,
                                 season: str) -> Dict[str, float]:
    """Calculate Method Resilience for both regular season and playoffs."""
    results = {}
    
    for season_type in ["Regular Season", "Playoffs"]:
        spatial = calculate_spatial_diversity(conn, player_id, season, season_type)
        playtype = calculate_playtype_diversity(conn, player_id, season, season_type)
        creation = calculate_creation_diversity(conn, player_id, season, season_type)
        
        # Weighted combination
        weights = {'spatial': 0.4, 'playtype': 0.4, 'creation': 0.2}
        components = []
        total_weight = 0
        
        if spatial is not None:
            components.append(spatial * weights['spatial'])
            total_weight += weights['spatial']
        if playtype is not None:
            components.append(playtype * weights['playtype'])
            total_weight += weights['playtype']
        if creation is not None:
            components.append(creation * weights['creation'])
            total_weight += weights['creation']
        
        if components and total_weight > 0:
            method_score = sum(components) / total_weight
            results[f'{season_type.lower().replace(" ", "_")}_method_resilience'] = method_score
        else:
            results[f'{season_type.lower().replace(" ", "_")}_method_resilience'] = None
        
        results[f'{season_type.lower().replace(" ", "_")}_spatial'] = spatial
        results[f'{season_type.lower().replace(" ", "_")}_playtype'] = playtype
        results[f'{season_type.lower().replace(" ", "_")}_creation'] = creation
    
    # Calculate delta
    reg_method = results.get('regular_season_method_resilience')
    po_method = results.get('playoffs_method_resilience')
    
    if reg_method is not None and po_method is not None:
        results['method_resilience_delta'] = po_method - reg_method
    else:
        results['method_resilience_delta'] = None
    
    return results


def analyze_player_longitudinal(conn: sqlite3.Connection, player_name: str,
                                 player_id: int, seasons: List[str]) -> pd.DataFrame:
    """Run longitudinal analysis for a single player."""
    results = []
    
    for season in seasons:
        print(f"  Analyzing {player_name} - {season}...")
        
        # Get all previous seasons for usage model
        season_idx = seasons.index(season)
        reg_seasons = seasons[:season_idx + 1]  # Include current season
        
        # Performance Resilience
        perf_res = calculate_performance_resilience(conn, player_id, season, reg_seasons)
        
        # Method Resilience
        method_res = calculate_method_resilience(conn, player_id, season)
        
        # Combine results
        result = {
            'player_name': player_name,
            'player_id': player_id,
            'season': season,
            **perf_res,
            **method_res
        }
        
        results.append(result)
    
    return pd.DataFrame(results)


def main():
    """Run longitudinal analysis for all case studies."""
    print("="*80)
    print("LONGITUDINAL RESILIENCE ANALYSIS - CASE STUDIES")
    print("="*80)
    print()
    
    conn = get_db_connection()
    
    all_results = []
    
    for player_name, config in CASE_STUDIES.items():
        print(f"\n{'='*80}")
        print(f"Analyzing: {player_name} ({config['hypothesis']} hypothesis)")
        print(f"Seasons: {', '.join(config['seasons'])}")
        print(f"{'='*80}")
        
        try:
            df = analyze_player_longitudinal(
                conn, player_name, config['player_id'], config['seasons']
            )
            all_results.append(df)
            print(f"✓ Completed {player_name}")
        except Exception as e:
            print(f"✗ Error analyzing {player_name}: {e}")
            import traceback
            traceback.print_exc()
    
    conn.close()
    
    if all_results:
        # Combine all results
        combined_df = pd.concat(all_results, ignore_index=True)
        
        # Save results
        output_file = "longitudinal_case_studies_results.csv"
        combined_df.to_csv(output_file, index=False)
        print(f"\n{'='*80}")
        print(f"Results saved to: {output_file}")
        print(f"{'='*80}\n")
        
        # Print summary
        print("\nSUMMARY BY PLAYER:")
        print("="*80)
        
        for player_name in CASE_STUDIES.keys():
            player_df = combined_df[combined_df['player_name'] == player_name]
            if not player_df.empty:
                print(f"\n{player_name}:")
                print("-" * 80)
                
                # Performance Resilience trajectory
                perf_cols = ['usage_adjusted_ts_delta', 'performance_resilience']
                available_perf = [col for col in perf_cols if col in player_df.columns]
                if available_perf:
                    print("Performance Resilience (Usage-Adjusted):")
                    for _, row in player_df.iterrows():
                        perf_val = row.get('usage_adjusted_ts_delta') or row.get('performance_resilience')
                        if perf_val is not None:
                            print(f"  {row['season']}: {perf_val:.1f}")
                
                # Method Resilience trajectory
                if 'regular_season_method_resilience' in player_df.columns:
                    print("\nMethod Resilience:")
                    for _, row in player_df.iterrows():
                        reg_method = row.get('regular_season_method_resilience')
                        po_method = row.get('playoffs_method_resilience')
                        delta = row.get('method_resilience_delta')
                        if reg_method is not None:
                            print(f"  {row['season']}: Reg={reg_method:.1f}, PO={po_method:.1f if po_method else 'N/A'}, Δ={delta:.1f if delta else 'N/A'}")
        
        print("\n" + "="*80)
        print("Analysis complete!")
        print("="*80)
    else:
        print("\nNo results generated. Check database connection and data availability.")


if __name__ == "__main__":
    main()
