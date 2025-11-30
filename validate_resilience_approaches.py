#!/usr/bin/env python3
"""
Validation Script: Simple vs Opponent-Adjusted Resilience Ratios

This script validates whether opponent strength adjustment improves resilience measurement
by comparing simple ratios to opponent-adjusted ratios and testing against known cases.

Known Test Cases:
- Jimmy Butler (2022-23): Should show high resilience
- Jamal Murray (2022-23): Should show high resilience  
- Ben Simmons (2020-21): Should show low resilience
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from scipy.stats import spearmanr

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from src.nba_data.api.nba_stats_client import NBAStatsClient
from calculate_resilience_external import ExternalResilienceCalculator

# Team abbreviation to team ID mapping (common abbreviations)
TEAM_ABBREVIATIONS = {
    'ATL': 1610612737, 'BOS': 1610612738, 'BKN': 1610612751, 'CHA': 1610612766,
    'CHI': 1610612741, 'CLE': 1610612739, 'DAL': 1610612742, 'DEN': 1610612743,
    'DET': 1610612765, 'GSW': 1610612744, 'HOU': 1610612745, 'IND': 1610612754,
    'LAC': 1610612746, 'LAL': 1610612747, 'MEM': 1610612763, 'MIA': 1610612748,
    'MIL': 1610612749, 'MIN': 1610612750, 'NOP': 1610612740, 'NYK': 1610612752,
    'OKC': 1610612760, 'ORL': 1610612753, 'PHI': 1610612755, 'PHX': 1610612756,
    'POR': 1610612757, 'SAC': 1610612758, 'SAS': 1610612759, 'TOR': 1610612761,
    'UTA': 1610612762, 'WAS': 1610612764
}


class OpponentStrengthCalculator:
    """Calculates opponent defensive ratings for player game logs."""
    
    def __init__(self, client: NBAStatsClient):
        self.client = client
        self._team_drtg_cache = {}  # {season: {team_id: drtg}}
        self._league_avg_drtg_cache = {}  # {season: avg_drtg}
    
    def get_team_defensive_ratings(self, season: str, season_type: str = "Regular Season") -> Dict[int, float]:
        """
        Get defensive ratings for all teams in a season.
        
        Returns:
            Dict mapping team_id to defensive_rating
        """
        cache_key = f"{season}_{season_type}"
        if cache_key in self._team_drtg_cache:
            return self._team_drtg_cache[cache_key]
        
        print(f"📡 Fetching team defensive ratings for {season} {season_type}...")
        
        try:
            # Get team stats - we'll use player stats aggregated by team
            # The API doesn't have a direct team stats endpoint, so we'll calculate from player stats
            if season_type == "Regular Season":
                response = self.client.get_league_player_advanced_stats(season=season, season_type=season_type)
            else:
                # For playoffs, use the playoff advanced stats method
                response = self.client.get_league_player_playoff_advanced_stats(season=season)
            
            if not response.get('resultSets') or not response['resultSets'][0].get('rowSet'):
                print(f"❌ No team data received for {season} {season_type}")
                return {}
            
            headers = response['resultSets'][0]['headers']
            rows = response['resultSets'][0]['rowSet']
            df = pd.DataFrame(rows, columns=headers)
            
            # Group by team and calculate average defensive rating
            # Note: DEF_RATING in player stats is the team's defensive rating when that player is on court
            # We'll use the average as a proxy for team defensive rating
            team_drtg = {}
            if 'DEF_RATING' in df.columns and 'TEAM_ID' in df.columns:
                team_avg = df.groupby('TEAM_ID')['DEF_RATING'].mean()
                team_drtg = team_avg.to_dict()
            
            # Calculate league average
            if team_drtg:
                league_avg = np.mean(list(team_drtg.values()))
                self._league_avg_drtg_cache[cache_key] = league_avg
                print(f"✅ Retrieved defensive ratings for {len(team_drtg)} teams (League avg: {league_avg:.2f})")
            
            self._team_drtg_cache[cache_key] = team_drtg
            return team_drtg
            
        except Exception as e:
            print(f"❌ Error fetching team defensive ratings: {e}")
            return {}
    
    def parse_matchup_opponent(self, matchup: str, player_team_id: int) -> Optional[int]:
        """
        Parse opponent team ID from matchup string.
        
        Matchup format examples:
        - "MIA vs. BOS" (home game, opponent is BOS)
        - "MIA @ BOS" (away game, opponent is BOS)
        """
        if not matchup or pd.isna(matchup):
            return None
        
        matchup = str(matchup).strip()
        
        # Try to extract team abbreviation
        if " vs. " in matchup:
            parts = matchup.split(" vs. ")
            if len(parts) == 2:
                # Home game - opponent is second part
                opp_abbr = parts[1].strip()
                return TEAM_ABBREVIATIONS.get(opp_abbr)
        elif " @ " in matchup:
            parts = matchup.split(" @ ")
            if len(parts) == 2:
                # Away game - opponent is second part
                opp_abbr = parts[1].strip()
                return TEAM_ABBREVIATIONS.get(opp_abbr)
        
        return None
    
    def get_player_id_by_name(self, player_name: str, season: str) -> Optional[int]:
        """Get player ID by name from API."""
        try:
            response = self.client.get_league_player_advanced_stats(season=season, season_type="Regular Season")
            if not response.get('resultSets') or not response['resultSets'][0].get('rowSet'):
                return None
            
            headers = response['resultSets'][0]['headers']
            rows = response['resultSets'][0]['rowSet']
            df = pd.DataFrame(rows, columns=headers)
            
            if 'PLAYER_ID' in df.columns and 'PLAYER_NAME' in df.columns:
                match = df[df['PLAYER_NAME'] == player_name]
                if not match.empty:
                    return int(match.iloc[0]['PLAYER_ID'])
            return None
        except Exception as e:
            print(f"⚠️  Error getting player ID for {player_name}: {e}")
            return None
    
    def get_player_opponent_drtg(self, player_name: str, season: str, season_type: str) -> Tuple[float, int]:
        """
        Get average opponent defensive rating for a player's games.
        
        Returns:
            Tuple of (average_opponent_drtg, number_of_games)
        """
        # Get team defensive ratings
        team_drtg = self.get_team_defensive_ratings(season, season_type)
        if not team_drtg:
            league_avg = self._league_avg_drtg_cache.get(f"{season}_{season_type}", 110.0)
            return league_avg, 0
        
        # Get player ID
        player_id = self.get_player_id_by_name(player_name, season)
        if not player_id:
            print(f"⚠️  Could not find player ID for {player_name}")
            league_avg = self._league_avg_drtg_cache.get(f"{season}_{season_type}", 110.0)
            return league_avg, 0
        
        # Get player game logs
        try:
            print(f"📊 Getting opponent DRTG for {player_name} ({season} {season_type})...")
            response = self.client.get_player_game_logs(player_id=player_id, season=season, season_type=season_type)
            
            if not response.get('resultSets') or not response['resultSets'][0].get('rowSet'):
                print(f"⚠️  No game logs found for {player_name}")
                league_avg = self._league_avg_drtg_cache.get(f"{season}_{season_type}", 110.0)
                return league_avg, 0
            
            headers = response['resultSets'][0]['headers']
            rows = response['resultSets'][0]['rowSet']
            df = pd.DataFrame(rows, columns=headers)
            
            # Get player's team ID from first game
            player_team_id = None
            if 'TEAM_ID' in df.columns and not df.empty:
                player_team_id = int(df.iloc[0]['TEAM_ID'])
            
            # Parse opponents from matchup strings
            opponent_drtgs = []
            if 'MATCHUP' in df.columns:
                for _, row in df.iterrows():
                    matchup = row['MATCHUP']
                    opponent_id = self.parse_matchup_opponent(matchup, player_team_id)
                    if opponent_id and opponent_id in team_drtg:
                        opponent_drtgs.append(team_drtg[opponent_id])
            
            if opponent_drtgs:
                avg_opp_drtg = np.mean(opponent_drtgs)
                num_games = len(opponent_drtgs)
                print(f"  ✅ Found {num_games} games, avg opponent DRTG: {avg_opp_drtg:.1f}")
                return avg_opp_drtg, num_games
            else:
                print(f"  ⚠️  Could not parse opponents, using league average")
                league_avg = self._league_avg_drtg_cache.get(f"{season}_{season_type}", 110.0)
                return league_avg, len(df) if not df.empty else 0
            
        except Exception as e:
            print(f"⚠️  Error getting opponent DRTG for {player_name}: {e}")
            league_avg = self._league_avg_drtg_cache.get(f"{season}_{season_type}", 110.0)
            return league_avg, 0


class ResilienceValidator:
    """Validates simple vs opponent-adjusted resilience approaches."""
    
    def __init__(self):
        self.client = NBAStatsClient()
        self.resilience_calc = ExternalResilienceCalculator()
        self.opponent_calc = OpponentStrengthCalculator(self.client)
        
        # Known test cases
        self.test_cases = {
            "Jimmy Butler III": {"season": "2022-23", "expected": "high"},
            "Jamal Murray": {"season": "2022-23", "expected": "high"},
            "Ben Simmons": {"season": "2020-21", "expected": "low"}
        }
    
    def calculate_simple_resilience(self, player_name: str, season: str) -> Optional[Dict]:
        """Calculate simple resilience ratio (baseline)."""
        return self.resilience_calc.calculate_player_resilience(player_name, season)
    
    def calculate_opponent_adjusted_resilience(self, player_name: str, season: str) -> Optional[Dict]:
        """
        Calculate opponent-adjusted resilience ratio.
        
        Uses ratio-based normalization:
        Adjusted TS% = TS% × (League Avg DRTG / Opponent DRTG)
        Resilience = Adjusted Playoff TS% ÷ Adjusted Regular Season TS%
        """
        # Get simple resilience first
        simple = self.calculate_simple_resilience(player_name, season)
        if not simple:
            return None
        
        # Get opponent DRTG for regular season and playoffs
        rs_opp_drtg, rs_games = self.opponent_calc.get_player_opponent_drtg(
            player_name, season, "Regular Season"
        )
        po_opp_drtg, po_games = self.opponent_calc.get_player_opponent_drtg(
            player_name, season, "Playoffs"
        )
        
        # Get league averages
        rs_league_avg = self.opponent_calc._league_avg_drtg_cache.get(
            f"{season}_Regular Season", 110.0
        )
        po_league_avg = self.opponent_calc._league_avg_drtg_cache.get(
            f"{season}_Playoffs", 110.0
        )
        
        # Calculate adjusted TS%
        rs_ts = simple['rs_ts_pct']
        po_ts = simple['po_ts_pct']
        
        # Normalize by opponent strength
        if rs_opp_drtg > 0:
            rs_adjusted = rs_ts * (rs_league_avg / rs_opp_drtg)
        else:
            rs_adjusted = rs_ts
        
        if po_opp_drtg > 0:
            po_adjusted = po_ts * (po_league_avg / po_opp_drtg)
        else:
            po_adjusted = po_ts
        
        # Calculate adjusted resilience ratio
        if rs_adjusted > 0:
            adjusted_ratio = po_adjusted / rs_adjusted
        else:
            adjusted_ratio = simple['ts_resilience_ratio']
        
        result = simple.copy()
        result.update({
            'rs_opp_drtg': rs_opp_drtg,
            'po_opp_drtg': po_opp_drtg,
            'rs_adjusted_ts': rs_adjusted,
            'po_adjusted_ts': po_adjusted,
            'opponent_adjusted_ratio': adjusted_ratio,
            'rs_games': rs_games,
            'po_games': po_games
        })
        
        return result
    
    def validate_known_cases(self) -> pd.DataFrame:
        """Validate both approaches against known test cases."""
        print("\n" + "="*70)
        print("VALIDATING AGAINST KNOWN CASES")
        print("="*70)
        
        results = []
        
        for player_name, case_info in self.test_cases.items():
            season = case_info["season"]
            expected = case_info["expected"]
            
            print(f"\n📊 Testing {player_name} ({season}) - Expected: {expected} resilience")
            
            # Calculate both metrics
            simple = self.calculate_simple_resilience(player_name, season)
            adjusted = self.calculate_opponent_adjusted_resilience(player_name, season)
            
            if simple and adjusted:
                simple_ratio = simple['ts_resilience_ratio']
                adjusted_ratio = adjusted['opponent_adjusted_ratio']
                
                # Determine if results match expectation
                simple_match = (simple_ratio > 1.0) if expected == "high" else (simple_ratio < 1.0)
                adjusted_match = (adjusted_ratio > 1.0) if expected == "high" else (adjusted_ratio < 1.0)
                
                results.append({
                    'player_name': player_name,
                    'season': season,
                    'expected': expected,
                    'simple_ratio': simple_ratio,
                    'adjusted_ratio': adjusted_ratio,
                    'simple_match': simple_match,
                    'adjusted_match': adjusted_match,
                    'rs_opp_drtg': adjusted.get('rs_opp_drtg', 0),
                    'po_opp_drtg': adjusted.get('po_opp_drtg', 0),
                    'rs_ts': simple['rs_ts_pct'],
                    'po_ts': simple['po_ts_pct']
                })
                
                print(f"  Simple Ratio: {simple_ratio:.3f} {'✅' if simple_match else '❌'}")
                print(f"  Adjusted Ratio: {adjusted_ratio:.3f} {'✅' if adjusted_match else '❌'}")
                print(f"  RS Opp DRTG: {adjusted.get('rs_opp_drtg', 0):.1f}")
                print(f"  PO Opp DRTG: {adjusted.get('po_opp_drtg', 0):.1f}")
            else:
                print(f"  ⚠️  Could not calculate resilience for {player_name}")
        
        return pd.DataFrame(results)
    
    def compare_rankings(self, season: str = "2023-24", max_players: int = 10) -> Dict:
        """Compare rankings between simple and opponent-adjusted approaches."""
        print(f"\n📊 Comparing rankings for {season} (limited to {max_players} players for testing)...")
        
        # Get all qualified players
        simple_df = self.resilience_calc.calculate_season_resilience(season, min_usage=0.20)
        
        if simple_df.empty:
            print("❌ No data available for comparison")
            return {}
        
        # Limit to top N players for testing
        simple_df = simple_df.head(max_players)
        print(f"  Testing with {len(simple_df)} players...")
        
        # Calculate opponent-adjusted ratios for all players
        adjusted_data = []
        for idx, row in simple_df.iterrows():
            player_name = row['player_name']
            print(f"  Processing {idx+1}/{len(simple_df)}: {player_name}...")
            adjusted = self.calculate_opponent_adjusted_resilience(player_name, season)
            if adjusted:
                adjusted_data.append({
                    'player_name': player_name,
                    'opponent_adjusted_ratio': adjusted['opponent_adjusted_ratio']
                })
        
        adjusted_df = pd.DataFrame(adjusted_data)
        
        if adjusted_df.empty:
            print("❌ No opponent-adjusted data available")
            return {}
        
        # Merge and rank
        comparison = simple_df[['player_name', 'ts_resilience_ratio']].merge(
            adjusted_df, on='player_name', how='inner'
        )
        
        comparison['simple_rank'] = comparison['ts_resilience_ratio'].rank(ascending=False)
        comparison['adjusted_rank'] = comparison['opponent_adjusted_ratio'].rank(ascending=False)
        comparison['rank_diff'] = comparison['simple_rank'] - comparison['adjusted_rank']
        
        # Calculate correlation
        correlation, p_value = spearmanr(
            comparison['ts_resilience_ratio'],
            comparison['opponent_adjusted_ratio']
        )
        
        return {
            'comparison_df': comparison,
            'correlation': correlation,
            'p_value': p_value,
            'n_players': len(comparison)
        }
    
    def generate_report(self) -> str:
        """Generate validation report."""
        print("\n" + "="*70)
        print("GENERATING VALIDATION REPORT")
        print("="*70)
        
        # Validate known cases
        known_cases = self.validate_known_cases()
        
        # Compare rankings for recent season (limited for testing)
        # ranking_comparison = self.compare_rankings("2023-24", max_players=10)  # Commented out for initial testing
        ranking_comparison = None  # Skip full ranking comparison for now
        
        # Generate report
        report_lines = [
            "# Resilience Approach Validation Report",
            "",
            "## Known Cases Validation",
            ""
        ]
        
        if not known_cases.empty:
            for _, row in known_cases.iterrows():
                report_lines.append(f"### {row['player_name']} ({row['season']})")
                report_lines.append(f"- Expected: {row['expected']} resilience")
                report_lines.append(f"- Simple Ratio: {row['simple_ratio']:.3f} {'✅' if row['simple_match'] else '❌'}")
                report_lines.append(f"- Adjusted Ratio: {row['adjusted_ratio']:.3f} {'✅' if row['adjusted_match'] else '❌'}")
                report_lines.append("")
        
        if ranking_comparison:
            report_lines.extend([
                "## Ranking Comparison (2023-24)",
                "",
                f"- Spearman Correlation: {ranking_comparison['correlation']:.3f}",
                f"- P-value: {ranking_comparison['p_value']:.4f}",
                f"- Players compared: {ranking_comparison['n_players']}",
                ""
            ])
        
        report = "\n".join(report_lines)
        return report


def main():
    """Main validation function."""
    print("🏀 RESILIENCE APPROACH VALIDATION")
    print("="*70)
    print("Comparing Simple vs Opponent-Adjusted Resilience Ratios")
    print()
    
    try:
        validator = ResilienceValidator()
        
        # Run validation - start with known cases only for proof of concept
        print("Starting with known cases validation...")
        known_cases = validator.validate_known_cases()
        
        # Save known cases results
        if not known_cases.empty:
            output_file = "data/known_cases_validation.csv"
            Path("data").mkdir(exist_ok=True)
            known_cases.to_csv(output_file, index=False)
            print(f"\n💾 Known cases results saved to {output_file}")
        
        # Generate report
        report = validator.generate_report()
        
        print("\n" + "="*70)
        print("VALIDATION REPORT")
        print("="*70)
        print(report)
        
        # Save report
        report_file = "data/resilience_validation_report.md"
        Path("data").mkdir(exist_ok=True)
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n💾 Report saved to {report_file}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

