"""
Longitudinal Resilience Analysis for Case Studies
Uses NBA Stats API directly when database is not available.

This script analyzes four case study players with usage-adjusted efficiency.
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from sklearn.linear_model import LinearRegression
import time
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

NBA_STATS_BASE = "https://stats.nba.com/stats"


def make_nba_api_request(endpoint: str, params: Dict) -> Optional[Dict]:
    """Make request to NBA Stats API with rate limiting."""
    url = f"{NBA_STATS_BASE}/{endpoint}"
    
    headers = {
        'Accept': '*/*',
        'Referer': 'https://www.nba.com/',
        'Origin': 'https://www.nba.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        time.sleep(0.6)  # Rate limiting
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  API Error for {endpoint}: {e}")
        return None


def get_player_advanced_stats(player_id: int, season: str, season_type: str = "Regular Season") -> Optional[Dict]:
    """Fetch player advanced stats from NBA API."""
    endpoint = "leaguedashplayerstats"
    
    params = {
        "Season": season,
        "SeasonType": season_type,
        "PlayerID": player_id,
        "PerMode": "PerGame",
        "MeasureType": "Advanced"
    }
    
    data = make_nba_api_request(endpoint, params)
    if not data or 'resultSets' not in data or not data['resultSets']:
        return None
    
    result_set = data['resultSets'][0]
    if not result_set['rowSet']:
        return None
    
    headers = result_set['headers']
    row = result_set['rowSet'][0]
    
    stats = dict(zip(headers, row))
    
    # Extract key metrics
    return {
        'true_shooting_percentage': stats.get('TS_PCT'),
        'usage_percentage': stats.get('USG_PCT'),
        'points_per_possession': stats.get('PTS') / stats.get('POSS', 1) if stats.get('POSS') else None,
        'turnover_percentage': stats.get('TOV_PCT'),
        'effective_field_goal_percentage': stats.get('EFG_PCT')
    }


def build_usage_efficiency_model(player_id: int, seasons: List[str]) -> Optional[LinearRegression]:
    """Build player-specific TS% = f(usage_rate) model."""
    usage_data = []
    ts_data = []
    
    for season in seasons:
        stats = get_player_advanced_stats(player_id, season, "Regular Season")
        if stats and stats.get('usage_percentage') and stats.get('true_shooting_percentage'):
            usage_data.append(stats['usage_percentage'])
            ts_data.append(stats['true_shooting_percentage'])
    
    if len(usage_data) < 2:
        return None
    
    X = np.array(usage_data).reshape(-1, 1)
    y = np.array(ts_data)
    
    model = LinearRegression()
    model.fit(X, y)
    
    return model


def calculate_usage_adjusted_ts_delta(player_id: int, season: str, reg_seasons: List[str]) -> Optional[float]:
    """Calculate usage-adjusted TS% delta."""
    reg_stats = get_player_advanced_stats(player_id, season, "Regular Season")
    po_stats = get_player_advanced_stats(player_id, season, "Playoffs")
    
    if not reg_stats or not po_stats:
        return None
    
    if not reg_stats.get('true_shooting_percentage') or not po_stats.get('true_shooting_percentage'):
        return None
    
    # Build usage-efficiency model
    model = build_usage_efficiency_model(player_id, reg_seasons)
    if not model:
        # Fallback: simple ratio
        return (po_stats['true_shooting_percentage'] / reg_stats['true_shooting_percentage']) * 100
    
    # Predict expected TS% at playoff usage
    playoff_usage = po_stats.get('usage_percentage')
    if not playoff_usage:
        return None
    
    expected_ts = model.predict([[playoff_usage]])[0]
    actual_ts = po_stats['true_shooting_percentage']
    
    if expected_ts <= 0:
        return None
    
    return (actual_ts / expected_ts) * 100


def analyze_player_season(player_name: str, player_id: int, season: str, reg_seasons: List[str]) -> Dict:
    """Analyze a single season for a player."""
    print(f"    {season}...", end=" ", flush=True)
    
    reg_stats = get_player_advanced_stats(player_id, season, "Regular Season")
    po_stats = get_player_advanced_stats(player_id, season, "Playoffs")
    
    result = {
        'player_name': player_name,
        'player_id': player_id,
        'season': season
    }
    
    if reg_stats:
        result['reg_ts_pct'] = reg_stats.get('true_shooting_percentage')
        result['reg_usage'] = reg_stats.get('usage_percentage')
        result['reg_ppp'] = reg_stats.get('points_per_possession')
    else:
        result['reg_ts_pct'] = None
        result['reg_usage'] = None
        result['reg_ppp'] = None
    
    if po_stats:
        result['po_ts_pct'] = po_stats.get('true_shooting_percentage')
        result['po_usage'] = po_stats.get('usage_percentage')
        result['po_ppp'] = po_stats.get('points_per_possession')
    else:
        result['po_ts_pct'] = None
        result['po_usage'] = None
        result['po_ppp'] = None
    
    # Calculate raw TS% delta
    if result['reg_ts_pct'] and result['po_ts_pct']:
        result['raw_ts_delta'] = (result['po_ts_pct'] / result['reg_ts_pct']) * 100
    else:
        result['raw_ts_delta'] = None
    
    # Calculate usage-adjusted TS% delta
    usage_adj_delta = calculate_usage_adjusted_ts_delta(player_id, season, reg_seasons)
    result['usage_adjusted_ts_delta'] = usage_adj_delta
    
    # Usage change
    if result['reg_usage'] and result['po_usage']:
        result['usage_change'] = result['po_usage'] - result['reg_usage']
    else:
        result['usage_change'] = None
    
    print("✓")
    return result


def main():
    """Run longitudinal analysis."""
    print("="*80)
    print("LONGITUDINAL RESILIENCE ANALYSIS - CASE STUDIES")
    print("="*80)
    print("\nNote: This uses the NBA Stats API directly.")
    print("This may take several minutes due to rate limiting...\n")
    
    all_results = []
    
    for player_name, config in CASE_STUDIES.items():
        print(f"\n{player_name} ({config['hypothesis']} hypothesis):")
        print(f"  Seasons: {', '.join(config['seasons'])}")
        
        player_results = []
        
        for i, season in enumerate(config['seasons']):
            reg_seasons = config['seasons'][:i+1]
            result = analyze_player_season(
                player_name, config['player_id'], season, reg_seasons
            )
            player_results.append(result)
        
        all_results.extend(player_results)
        print(f"  ✓ Completed {player_name}")
    
    # Create DataFrame
    df = pd.DataFrame(all_results)
    
    # Save results
    output_file = "longitudinal_case_studies_results.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*80}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*80}\n")
    
    # Print summary
    print("\nSUMMARY RESULTS:")
    print("="*80)
    
    for player_name in CASE_STUDIES.keys():
        player_df = df[df['player_name'] == player_name]
        if not player_df.empty:
            print(f"\n{player_name}:")
            print("-" * 80)
            
            for _, row in player_df.iterrows():
                print(f"\n  {row['season']}:")
                
                if row['reg_ts_pct']:
                    print(f"    Regular Season: TS%={row['reg_ts_pct']:.3f}, Usage={row['reg_usage']:.1f}%")
                
                if row['po_ts_pct']:
                    print(f"    Playoffs: TS%={row['po_ts_pct']:.3f}, Usage={row['po_usage']:.1f}%")
                
                if row['usage_change']:
                    print(f"    Usage Change: {row['usage_change']:+.1f}%")
                
                if row['raw_ts_delta']:
                    print(f"    Raw TS% Delta: {row['raw_ts_delta']:.1f}%")
                
                if row['usage_adjusted_ts_delta']:
                    print(f"    Usage-Adjusted TS% Delta: {row['usage_adjusted_ts_delta']:.1f}%")
                    print(f"    → {'Resilient' if row['usage_adjusted_ts_delta'] >= 95 else 'Vulnerable'}")
    
    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)


if __name__ == "__main__":
    main()
