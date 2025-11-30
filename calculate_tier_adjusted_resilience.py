#!/usr/bin/env python3
"""
NBA Playoff Resilience Calculator - Phase 1: Tier-Adjusted Resilience

Phase 1 MVP: Minimal Viable Tier Adjustment
- Calculate defensive tiers (3 tiers based on regular season DRTG)
- Assign players to tiers based on primary playoff opponent
- Calculate tier-specific baselines
- Calculate adjusted resilience scores

This is the simplest version that tests if context adjustment improves the metric.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent))

from src.nba_data.api.nba_stats_client import NBAStatsClient
from calculate_resilience_external import ExternalResilienceCalculator


class TierAdjustedResilienceCalculator(ExternalResilienceCalculator):
    """Calculates tier-adjusted playoff resilience using defensive context."""
    
    def __init__(self):
        super().__init__()
        self.defensive_tiers = None
        self.tier_baselines = None
    
    def get_team_defensive_ratings(self, season: str) -> pd.DataFrame:
        """
        Get regular season defensive ratings for all teams.
        
        Returns:
            DataFrame with columns: TEAM_ID, TEAM_NAME, DRTG
        """
        print(f"📊 Fetching team defensive ratings for {season}...")
        
        try:
            # Get team advanced stats from league dashboard
            # The NBA API endpoint is leaguedashteamstats with MeasureType=Advanced
            endpoint = "leaguedashteamstats"
            params = {
                "College": "",
                "Conference": "",
                "Country": "",
                "DateFrom": "",
                "DateTo": "",
                "Division": "",
                "DraftPick": "",
                "DraftYear": "",
                "GameScope": "",
                "GameSegment": "",
                "LastNGames": "0",
                "LeagueID": "00",
                "Location": "",
                "MeasureType": "Advanced",
                "Month": "0",
                "OpponentTeamID": "0",
                "Outcome": "",
                "PORound": "0",
                "PaceAdjust": "N",
                "PerMode": "PerGame",
                "Period": "0",
                "PlayerExperience": "",
                "PlayerPosition": "",
                "PlusMinus": "N",
                "Rank": "N",
                "Season": season,
                "SeasonSegment": "",
                "SeasonType": "Regular Season",
                "ShotClockRange": "",
                "StarterBench": "",
                "TeamID": "0",
                "TwoWay": "0",
                "VsConference": "",
                "VsDivision": ""
            }
            
            response = self.client._make_request(endpoint, params)
            
            if not response.get('resultSets') or not response['resultSets'][0].get('rowSet'):
                print("❌ No team data received")
                return self._get_team_drtg_from_player_data(season)
            
            headers = response['resultSets'][0]['headers']
            rows = response['resultSets'][0]['rowSet']
            df = pd.DataFrame(rows, columns=headers)
            
            # Extract team ID, name, and defensive rating
            # Defensive rating column name varies - try common ones
            drtg_col = None
            for col in ['DEF_RATING', 'D_RATING', 'DEFRTG', 'DRTG']:
                if col in df.columns:
                    drtg_col = col
                    break
            
            if drtg_col is None:
                print("⚠️  Could not find defensive rating column, using player data aggregation")
                return self._get_team_drtg_from_player_data(season)
            
            team_drtg = df[['TEAM_ID', 'TEAM_NAME', drtg_col]].copy()
            team_drtg.columns = ['TEAM_ID', 'TEAM_NAME', 'DRTG']
            team_drtg = team_drtg.sort_values('DRTG', ascending=True)  # Lower is better
            
            print(f"✅ Retrieved DRTG for {len(team_drtg)} teams")
            return team_drtg
            
        except Exception as e:
            print(f"❌ Error fetching team defensive ratings: {e}")
            return self._get_team_drtg_from_player_data(season)
    
    def _get_team_drtg_from_player_data(self, season: str) -> pd.DataFrame:
        """Fallback: Calculate team DRTG by aggregating player data."""
        print("📊 Using fallback: aggregating team DRTG from player data...")
        
        try:
            response = self.client.get_league_player_advanced_stats(
                season=season, 
                season_type="Regular Season"
            )
            
            if not response.get('resultSets') or not response['resultSets'][0].get('rowSet'):
                print("❌ No player data available")
                return pd.DataFrame()
            
            headers = response['resultSets'][0]['headers']
            rows = response['resultSets'][0]['rowSet']
            df = pd.DataFrame(rows, columns=headers)
            
            # Find defensive rating column
            drtg_col = None
            for col in ['DEF_RATING', 'D_RATING', 'DEFRTG']:
                if col in df.columns:
                    drtg_col = col
                    break
            
            if drtg_col is None:
                print("❌ Could not find defensive rating in player data")
                return pd.DataFrame()
            
            # Group by team and calculate average (weighted by minutes if possible)
            team_drtg = df.groupby(['TEAM_ID', 'TEAM_NAME'])[drtg_col].mean().reset_index()
            team_drtg.columns = ['TEAM_ID', 'TEAM_NAME', 'DRTG']
            team_drtg = team_drtg.sort_values('DRTG', ascending=True)
            
            print(f"✅ Calculated DRTG for {len(team_drtg)} teams from player data")
            return team_drtg
            
        except Exception as e:
            print(f"❌ Error in fallback method: {e}")
            return pd.DataFrame()
    
    def calculate_defensive_tiers(self, season: str) -> Dict[int, int]:
        """
        Calculate defensive tiers based on regular season DRTG.
        
        Returns:
            Dict mapping TEAM_ID -> Tier (1, 2, or 3)
            Tier 1: Best defenses (ranks 1-10)
            Tier 2: Average defenses (ranks 11-20)
            Tier 3: Weakest defenses (ranks 21-30)
        """
        print("\n🏆 Calculating Defensive Tiers")
        print("=" * 50)
        
        team_drtg = self.get_team_defensive_ratings(season)
        
        if team_drtg.empty:
            print("❌ Could not get team defensive ratings")
            return {}
        
        # Assign tiers: 1-10 = Tier 1, 11-20 = Tier 2, 21-30 = Tier 3
        team_drtg['rank'] = range(1, len(team_drtg) + 1)
        team_drtg['tier'] = pd.cut(
            team_drtg['rank'],
            bins=[0, 10, 20, 30],
            labels=[1, 2, 3]
        ).astype(int)
        
        # Create mapping
        tier_mapping = dict(zip(team_drtg['TEAM_ID'], team_drtg['tier']))
        
        # Store for later use
        self.defensive_tiers = team_drtg[['TEAM_ID', 'TEAM_NAME', 'DRTG', 'rank', 'tier']]
        
        # Print summary
        print(f"\nTier 1 (Elite Defense, ranks 1-10):")
        tier1 = team_drtg[team_drtg['tier'] == 1]
        for _, row in tier1.iterrows():
            print(f"  {row['TEAM_NAME']:25s} | DRTG: {row['DRTG']:.1f} | Rank: {row['rank']}")
        
        print(f"\nTier 2 (Average Defense, ranks 11-20):")
        tier2 = team_drtg[team_drtg['tier'] == 2]
        for _, row in tier2.iterrows():
            print(f"  {row['TEAM_NAME']:25s} | DRTG: {row['DRTG']:.1f} | Rank: {row['rank']}")
        
        print(f"\nTier 3 (Weak Defense, ranks 21-30):")
        tier3 = team_drtg[team_drtg['tier'] == 3]
        for _, row in tier3.iterrows():
            print(f"  {row['TEAM_NAME']:25s} | DRTG: {row['DRTG']:.1f} | Rank: {row['rank']}")
        
        return tier_mapping
    
    def get_playoff_matchups(self, season: str) -> Dict[int, List[int]]:
        """
        Get playoff matchups: which teams played each other.
        
        Returns:
            Dict mapping TEAM_ID -> List of opponent TEAM_IDs
        """
        print(f"📊 Getting playoff matchups for {season}...")
        
        # Get playoff game logs to infer matchups
        # We'll use the team game logs endpoint
        endpoint = "teamgamelogs"
        params = {
            "DateFrom": "",
            "DateTo": "",
            "GameSegment": "",
            "LastNGames": "0",
            "LeagueID": "00",
            "Location": "",
            "MeasureType": "Base",
            "Month": "0",
            "OpponentTeamID": "0",
            "Outcome": "",
            "PORound": "0",
            "PaceAdjust": "N",
            "PerMode": "Totals",
            "Period": "0",
            "PlusMinus": "N",
            "Rank": "N",
            "Season": season,
            "SeasonSegment": "",
            "SeasonType": "Playoffs",
            "ShotClockRange": "",
            "VsConference": "",
            "VsDivision": ""
        }
        
        try:
            response = self.client._make_request(endpoint, params)
            
            if not response.get('resultSets') or not response['resultSets'][0].get('rowSet'):
                print("⚠️  Could not get playoff game logs, using simplified approach")
                return {}
            
            headers = response['resultSets'][0]['headers']
            rows = response['resultSets'][0]['rowSet']
            df = pd.DataFrame(rows, columns=headers)
            
            # Build matchup dictionary
            # The MATCHUP column format is usually "TEAM @ OPPONENT" or "TEAM vs. OPPONENT"
            # We need to extract opponent abbreviation and map to team ID
            
            # First, get all unique teams and their abbreviations
            team_abbrev_map = {}
            for _, row in df.iterrows():
                team_id = row['TEAM_ID']
                team_abbrev = row.get('MATCHUP', '').split()[0]  # First part is the team
                if team_id not in team_abbrev_map:
                    team_abbrev_map[team_id] = team_abbrev
            
            # Create reverse mapping: abbreviation -> team_id
            abbrev_to_id = {abbrev: tid for tid, abbrev in team_abbrev_map.items()}
            
            # Now build matchups
            matchups = {}
            for _, row in df.iterrows():
                team_id = row['TEAM_ID']
                matchup_str = row.get('MATCHUP', '')
                
                if team_id not in matchups:
                    matchups[team_id] = []
                
                # Extract opponent abbreviation from matchup string
                # Format: "TEAM @ OPPONENT" or "TEAM vs. OPPONENT"
                parts = matchup_str.split()
                if len(parts) >= 3:
                    opponent_abbrev = parts[-1]  # Last part is opponent
                    opponent_id = abbrev_to_id.get(opponent_abbrev)
                    
                    if opponent_id and opponent_id not in matchups[team_id]:
                        matchups[team_id].append(opponent_id)
            
            print(f"✅ Found matchups for {len(matchups)} teams")
            return matchups
            
        except Exception as e:
            print(f"⚠️  Error getting playoff matchups: {e}")
            return {}
    
    def assign_players_to_tiers(self, df: pd.DataFrame, season: str, tier_mapping: Dict[int, int]) -> pd.DataFrame:
        """
        Assign each player to a defensive tier based on their primary playoff opponent.
        
        For MVP: Use primary opponent (most games played against).
        """
        print("\n🎯 Assigning Players to Defensive Tiers")
        print("=" * 50)
        
        # Get playoff matchups
        matchups = self.get_playoff_matchups(season)
        
        # Get playoff data to find player teams
        po_data = self.get_season_data(season, "Playoffs")
        if po_data.empty:
            print("❌ No playoff data available")
            df['opponent_tier'] = None
            df['opponent_team_id'] = None
            df['opponent_team_name'] = None
            return df
        
        # Create player -> team mapping
        player_teams = po_data[['PLAYER_NAME', 'TEAM_ID', 'TEAM_NAME']].drop_duplicates()
        player_team_map = dict(zip(player_teams['PLAYER_NAME'], player_teams['TEAM_ID']))
        
        # Initialize columns
        df['opponent_tier'] = None
        df['opponent_team_id'] = None
        df['opponent_team_name'] = None
        
        # Get team name mapping for display
        if self.defensive_tiers is not None:
            team_name_map = dict(zip(
                self.defensive_tiers['TEAM_ID'], 
                self.defensive_tiers['TEAM_NAME']
            ))
        else:
            team_name_map = {}
        
        assigned_count = 0
        
        # For each player, find their team's primary opponent
        for idx, row in df.iterrows():
            player_name = row['player_name']
            player_team_id = player_team_map.get(player_name)
            
            if player_team_id is None:
                continue
            
            # Find opponents for this team
            opponents = matchups.get(player_team_id, [])
            
            if not opponents:
                # If no matchup data, try to infer from playoff teams
                # For MVP, we'll skip players without clear opponents
                continue
            
            # Use primary opponent (first one, or could weight by games)
            primary_opponent_id = opponents[0] if opponents else None
            
            if primary_opponent_id and primary_opponent_id in tier_mapping:
                opponent_tier = tier_mapping[primary_opponent_id]
                df.at[idx, 'opponent_tier'] = opponent_tier
                df.at[idx, 'opponent_team_id'] = primary_opponent_id
                df.at[idx, 'opponent_team_name'] = team_name_map.get(primary_opponent_id, f"Team {primary_opponent_id}")
                assigned_count += 1
        
        print(f"✅ Assigned {assigned_count} players to defensive tiers")
        print(f"   {len(df) - assigned_count} players without clear opponent assignment")
        
        # Show distribution
        if assigned_count > 0:
            tier_counts = df['opponent_tier'].value_counts().sort_index()
            print("\nTier Distribution:")
            for tier, count in tier_counts.items():
                if pd.notna(tier):
                    print(f"  Tier {int(tier)}: {count} players")
        
        return df
    
    def calculate_tier_baselines(self, df: pd.DataFrame) -> Dict[int, Dict[str, float]]:
        """
        Calculate average TS% ratio and Production ratio for each tier.
        
        Returns:
            Dict mapping tier -> {'ts_ratio_avg': float, 'production_ratio_avg': float}
        """
        print("\n📊 Calculating Tier Baselines")
        print("=" * 50)
        
        if df.empty or 'opponent_tier' not in df.columns:
            print("❌ No player data or tier assignments")
            return {}
        
        # Filter out players without tier assignments
        df_with_tiers = df[df['opponent_tier'].notna()].copy()
        
        if df_with_tiers.empty:
            print("❌ No players with tier assignments")
            return {}
        
        baselines = {}
        
        for tier in [1, 2, 3]:
            tier_players = df_with_tiers[df_with_tiers['opponent_tier'] == tier]
            
            if len(tier_players) == 0:
                print(f"⚠️  Tier {tier}: No players found")
                continue
            
            # Calculate averages
            ts_ratio_avg = tier_players['ts_resilience_ratio'].mean()
            
            # Calculate production ratio if available
            if 'absolute_production_ratio' in tier_players.columns:
                production_ratio_avg = tier_players['absolute_production_ratio'].mean()
            elif 'composite_resilience' in tier_players.columns:
                # If we have composite but not production ratio, estimate from composite
                # Composite = (TS% + Production) / 2, so Production = 2*Composite - TS%
                # But this is approximate - better to calculate directly
                # For MVP, use TS% ratio as proxy if production not available
                production_ratio_avg = ts_ratio_avg
                print(f"  ⚠️  Production ratio not available, using TS% ratio as proxy")
            else:
                # Fallback: use TS% ratio
                production_ratio_avg = ts_ratio_avg
                print(f"  ⚠️  Production ratio not available, using TS% ratio as proxy")
            
            baselines[tier] = {
                'ts_ratio_avg': ts_ratio_avg,
                'production_ratio_avg': production_ratio_avg,
                'player_count': len(tier_players)
            }
            
            print(f"\nTier {tier} Baseline (n={len(tier_players)} players):")
            print(f"  Average TS% Ratio: {ts_ratio_avg:.3f}")
            print(f"  Average Production Ratio: {production_ratio_avg:.3f}")
        
        self.tier_baselines = baselines
        return baselines
    
    def calculate_adjusted_scores(self, df: pd.DataFrame, baselines: Dict[int, Dict[str, float]]) -> pd.DataFrame:
        """
        Calculate adjusted resilience scores.
        
        Adjusted Score = Player Ratio / Tier Baseline Ratio
        """
        print("\n🎯 Calculating Adjusted Scores")
        print("=" * 50)
        
        df = df.copy()
        
        # Initialize adjusted score columns
        df['adjusted_ts_score'] = None
        df['adjusted_production_score'] = None
        df['adjusted_composite_score'] = None
        
        for tier in [1, 2, 3]:
            if tier not in baselines:
                continue
            
            tier_players = df['opponent_tier'] == tier
            baseline = baselines[tier]
            
            # Calculate adjusted TS% score
            df.loc[tier_players, 'adjusted_ts_score'] = (
                df.loc[tier_players, 'ts_resilience_ratio'] / baseline['ts_ratio_avg']
            )
            
            # Calculate adjusted production score
            if 'absolute_production_ratio' in df.columns:
                df.loc[tier_players, 'adjusted_production_score'] = (
                    df.loc[tier_players, 'absolute_production_ratio'] / baseline['production_ratio_avg']
                )
            else:
                # Use TS% score as placeholder if production not available
                df.loc[tier_players, 'adjusted_production_score'] = df.loc[tier_players, 'adjusted_ts_score']
            
            # Calculate adjusted composite score
            df.loc[tier_players, 'adjusted_composite_score'] = (
                (df.loc[tier_players, 'adjusted_ts_score'] + 
                 df.loc[tier_players, 'adjusted_production_score']) / 2
            )
        
        # Add categories for adjusted scores
        df['adjusted_category'] = pd.cut(
            df['adjusted_composite_score'],
            bins=[0, 0.85, 0.95, 1.05, 1.15, float('inf')],
            labels=['Severely Fragile', 'Fragile', 'Neutral', 'Resilient', 'Highly Resilient']
        )
        
        print(f"✅ Calculated adjusted scores for {df['adjusted_composite_score'].notna().sum()} players")
        
        return df
    
    def calculate_tier_adjusted_resilience(self, season: str = "2023-24", min_usage: float = 0.20) -> pd.DataFrame:
        """
        Main method: Calculate tier-adjusted resilience for all qualified players.
        """
        print("\n" + "=" * 70)
        print("NBA PLAYOFF RESILIENCE CALCULATOR - PHASE 1: TIER-ADJUSTED RESILIENCE")
        print("=" * 70)
        print(f"\nSeason: {season}")
        print(f"Minimum Usage: {min_usage}")
        
        # Step 1: Calculate defensive tiers
        tier_mapping = self.calculate_defensive_tiers(season)
        if not tier_mapping:
            print("❌ Could not calculate defensive tiers")
            return pd.DataFrame()
        
        # Step 2: Get base resilience data (TS% and Production ratios)
        print("\n📊 Getting Base Resilience Data")
        print("=" * 50)
        
        # Use composite calculator to get both TS% and Production ratios
        from calculate_composite_resilience import CompositeResilienceCalculator
        composite_calc = CompositeResilienceCalculator()
        df = composite_calc.calculate_season_composite_resilience(season, min_usage)
        
        if df.empty:
            print("❌ No qualified players found")
            return pd.DataFrame()
        
        print(f"✅ Found {len(df)} qualified players")
        
        # Step 3: Assign players to tiers
        df = self.assign_players_to_tiers(df, season, tier_mapping)
        
        # Step 4: Calculate tier baselines
        baselines = self.calculate_tier_baselines(df)
        if not baselines:
            print("❌ Could not calculate tier baselines")
            return df  # Return unadjusted data
        
        # Step 5: Calculate adjusted scores
        df = self.calculate_adjusted_scores(df, baselines)
        
        return df


def validate_tier_adjustment(df: pd.DataFrame):
    """Validate tier adjustment by comparing adjusted vs unadjusted scores."""
    print("\n" + "=" * 70)
    print("VALIDATION: Adjusted vs Unadjusted Scores")
    print("=" * 70)
    
    if df.empty or 'adjusted_composite_score' not in df.columns:
        print("❌ No adjusted scores to validate")
        return
    
    # Filter to players with adjusted scores
    df_valid = df[df['adjusted_composite_score'].notna()].copy()
    
    if df_valid.empty:
        print("❌ No players with adjusted scores")
        return
    
    print(f"\nAnalyzing {len(df_valid)} players with tier adjustments\n")
    
    # Compare scores
    df_valid['score_change'] = df_valid['adjusted_composite_score'] - df_valid['composite_resilience']
    df_valid['score_change_pct'] = (df_valid['score_change'] / df_valid['composite_resilience']) * 100
    
    # Test cases: Shai, Murray, Butler
    test_cases = {
        "Shai Gilgeous-Alexander": "Shai",
        "Jamal Murray": "Murray",
        "Jimmy Butler": "Butler"
    }
    
    print("Test Cases:")
    print("-" * 70)
    for full_name, short_name in test_cases.items():
        player_data = df_valid[df_valid['player_name'] == full_name]
        if not player_data.empty:
            row = player_data.iloc[0]
            print(f"\n{short_name} ({full_name}):")
            print(f"  Unadjusted Composite: {row['composite_resilience']:.3f}")
            print(f"  Adjusted Composite: {row['adjusted_composite_score']:.3f}")
            print(f"  Change: {row['score_change']:+.3f} ({row['score_change_pct']:+.1f}%)")
            print(f"  Opponent Tier: {row.get('opponent_tier', 'N/A')}")
            print(f"  Unadjusted Category: {row.get('composite_category', 'N/A')}")
            print(f"  Adjusted Category: {row.get('adjusted_category', 'N/A')}")
        else:
            print(f"\n{short_name}: Not found in dataset")
    
    # Summary statistics
    print("\n" + "-" * 70)
    print("Summary Statistics:")
    print(f"  Mean Score Change: {df_valid['score_change'].mean():+.3f}")
    print(f"  Median Score Change: {df_valid['score_change'].median():+.3f}")
    print(f"  Players Improved: {(df_valid['score_change'] > 0).sum()} ({(df_valid['score_change'] > 0).sum()/len(df_valid)*100:.1f}%)")
    print(f"  Players Declined: {(df_valid['score_change'] < 0).sum()} ({(df_valid['score_change'] < 0).sum()/len(df_valid)*100:.1f}%)")
    
    # Check if Shai problem is fixed
    shai_data = df_valid[df_valid['player_name'] == "Shai Gilgeous-Alexander"]
    if not shai_data.empty:
        shai_adjusted = shai_data.iloc[0]['adjusted_composite_score']
        if shai_adjusted > 0.95:
            print("\n✅ SHAI PROBLEM POTENTIALLY FIXED: Adjusted score > 0.95")
        else:
            print(f"\n⚠️  SHAI PROBLEM PERSISTS: Adjusted score = {shai_adjusted:.3f}")


def main():
    """Main function to run Phase 1 tier-adjusted resilience calculation."""
    
    calculator = TierAdjustedResilienceCalculator()
    season = "2023-24"
    
    # Calculate tier-adjusted resilience
    df = calculator.calculate_tier_adjusted_resilience(season, min_usage=0.20)
    
    if df.empty:
        print("\n❌ Could not calculate tier-adjusted resilience")
        return
    
    # Validate
    validate_tier_adjustment(df)
    
    # Save results
    output_file = f"data/tier_adjusted_resilience_{season.replace('-', '_')}.csv"
    Path("data").mkdir(exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to {output_file}")
    
    # Show top/bottom players by adjusted score
    print("\n" + "=" * 70)
    print("TOP 10 PLAYERS BY ADJUSTED COMPOSITE SCORE")
    print("=" * 70)
    
    df_sorted = df[df['adjusted_composite_score'].notna()].sort_values(
        'adjusted_composite_score', 
        ascending=False
    )
    
    for idx, (_, row) in enumerate(df_sorted.head(10).iterrows(), 1):
        print(f"{idx:2d}. {row['player_name']:30s} | "
              f"Adjusted: {row['adjusted_composite_score']:.3f} | "
              f"Unadjusted: {row['composite_resilience']:.3f} | "
              f"Tier: {row.get('opponent_tier', 'N/A')}")


if __name__ == "__main__":
    main()
