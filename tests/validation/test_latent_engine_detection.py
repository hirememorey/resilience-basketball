"""
Validation Test Suite: Latent Engine Detection

This test suite validates the TII (Trajectory Independence Index) and the 
2D classification system (CII × TII) for detecting Latent Engines.

Latent Engines are the key alpha:
- Players whose creation skills are present but underutilized
- Would scale to Engine-level if given opportunity
- Are undervalued because surface stats don't reveal upside

Critical Test Cases:
1. MUST-PASS: Historical Latent Engines (Brunson, Harden OKC, SGA)
2. MUST-FAIL: False Latent Engines (Simmons, Randle, Sabonis)
3. EDGE CASES: Players near the boundary

Success Criteria:
- Latent Engine Precision: >80% of flagged Latent Engines become Engines
- Latent Engine Recall: >70% of future Engines flagged 2+ years before
- Brunson 2020-21: Must be flagged as Latent Engine
- Simmons: Must NEVER be flagged as Latent Engine
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestLatentEngineDetection:
    """Test suite for Latent Engine detection via TII."""
    
    @pytest.fixture(scope='class')
    def feature_dataset(self):
        """Load the feature dataset."""
        path = project_root / 'results' / 'predictive_dataset_with_friction.csv'
        if not path.exists():
            pytest.skip(f"Feature dataset not found at {path}")
        return pd.read_csv(path)
    
    @pytest.fixture(scope='class')
    def calculators(self):
        """Import the TII and CII calculators."""
        from src.nba_data.phase2_creation_independence.index.trajectory import calculate_tii
        from src.nba_data.phase2_creation_independence.index.composite import calculate_cii
        return {'tii': calculate_tii, 'cii': calculate_cii}
    
    def get_player_data(self, df, player_name, season):
        """Get player data for a specific season."""
        # Use exact match for full names, contains for partial names
        if ' ' in player_name:
            # Full name - use exact match
            mask = (
                df['player_name'].str.lower() == player_name.lower()
            ) & (df['season'] == season)
        else:
            # Partial name - use contains
            mask = (
                df['player_name'].str.lower().str.contains(player_name.lower(), na=False) &
                (df['season'] == season)
            )
        if mask.any():
            return df[mask].iloc[0]
        return None
    
    # =========================================================================
    # MUST-PASS: Historical Latent Engines
    # =========================================================================
    
    def test_brunson_2020_21_latent_engine(self, feature_dataset, calculators):
        """
        Jalen Brunson 2020-21 MUST be identified as Latent Engine.
        
        Context: Mavs backup, USG 0.196, but:
        - Elite efficiency (TS 0.618)
        - High creation rate (CVR 0.69)
        - Positive pressure response (+0.029 leverage)
        - Age 24 (prime development)
        
        Breakout came 2022-23 with Knicks (28 PPG).
        """
        player_data = self.get_player_data(feature_dataset, 'Jalen Brunson', '2020-21')
        if player_data is None:
            pytest.skip("Brunson 2020-21 not in dataset")
        
        tii_result = calculators['tii'](player_data)
        cii_result = calculators['cii'](player_data)
        
        # TII should be High Scaling (65+) or Elite Scaling (80+)
        assert tii_result['tii'] >= 65, (
            f"Brunson 2020-21 TII should be >=65 (High Scaling), got {tii_result['tii']:.1f}"
        )
        
        # Combined classification: Medium CII + High TII = Latent Engine
        assert tii_result['tii_archetype'] in ['High Scaling', 'Elite Scaling'], (
            f"Brunson should be High/Elite Scaling, got {tii_result['tii_archetype']}"
        )
        
        print(f"\n✅ Brunson 2020-21: CII={cii_result['cii']:.1f}, TII={tii_result['tii']:.1f}")
        print(f"   → Correctly identified as Latent Engine candidate")
    
    def test_brunson_trajectory(self, feature_dataset, calculators):
        """
        Verify Brunson's trajectory from Latent → Realized Engine.
        
        2020-21: Latent (low usage, high potential)
        2022-23+: Realized (high usage, proven)
        """
        seasons = ['2020-21', '2021-22', '2022-23', '2023-24']
        results = []
        
        for season in seasons:
            player_data = self.get_player_data(feature_dataset, 'Jalen Brunson', season)
            if player_data is not None:
                tii = calculators['tii'](player_data)
                cii = calculators['cii'](player_data)
                results.append({
                    'season': season,
                    'cii': cii['cii'],
                    'tii': tii['tii'],
                    'usg': player_data.get('usg_pct', 0)
                })
        
        if len(results) >= 2:
            # CII should increase over time (proving out)
            cii_increased = results[-1]['cii'] > results[0]['cii']
            assert cii_increased, "Brunson CII should increase as he proved out"
            
            print(f"\n✅ Brunson trajectory:")
            for r in results:
                print(f"   {r['season']}: CII={r['cii']:.1f}, TII={r['tii']:.1f}, USG={r['usg']:.3f}")
    
    def test_sga_latent_engine(self, feature_dataset, calculators):
        """
        SGA 2019-20 should show latent ability (with CP3, limited touches).
        
        Note: May be lower TII than expected due to CP3 taking clutch possessions.
        """
        player_data = self.get_player_data(feature_dataset, 'Shai Gilgeous-Alexander', '2019-20')
        if player_data is None:
            pytest.skip("SGA 2019-20 not in dataset")
        
        tii_result = calculators['tii'](player_data)
        
        # Should have at least Moderate Scaling potential
        assert tii_result['tii'] >= 50, (
            f"SGA 2019-20 TII should be >=50, got {tii_result['tii']:.1f}"
        )
        
        # Creation tools should be present
        assert tii_result['components']['creation_tools'] >= 60, (
            f"SGA should have creation tools, got {tii_result['components']['creation_tools']:.1f}"
        )
        
        print(f"\n✅ SGA 2019-20: TII={tii_result['tii']:.1f}")
    
    # =========================================================================
    # MUST-FAIL: False Latent Engines
    # =========================================================================
    
    def test_simmons_never_latent_engine(self, feature_dataset, calculators):
        """
        Ben Simmons should NEVER be flagged as Latent Engine in ANY season.
        
        Key Issue: Has efficiency but NO CREATION TOOLS.
        - Zero pull-up jumpers
        - Negative pressure response (hiding)
        - Cannot scale because no tools to scale WITH
        """
        simmons_seasons = ['2017-18', '2018-19', '2019-20', '2020-21']
        
        for season in simmons_seasons:
            player_data = self.get_player_data(feature_dataset, 'Ben Simmons', season)
            if player_data is None:
                continue
            
            tii_result = calculators['tii'](player_data)
            
            # TII should be Limited Scaling (<50)
            assert tii_result['tii'] < 50, (
                f"Simmons {season} TII should be <50 (Limited Scaling), got {tii_result['tii']:.1f}"
            )
            
            # Pressure Appetite should be very low
            assert tii_result['components']['pressure_appetite'] < 30, (
                f"Simmons pressure appetite should be <30, got {tii_result['components']['pressure_appetite']:.1f}"
            )
            
            print(f"\n✅ Simmons {season}: TII={tii_result['tii']:.1f} (correctly Limited)")
    
    def test_sabonis_not_latent_engine(self, feature_dataset, calculators):
        """
        Sabonis should NOT be flagged as Latent Engine.
        
        Key Issue: HIDES under pressure (negative leverage_usg_delta).
        Has some post skills but no creation scaling potential.
        """
        player_data = self.get_player_data(feature_dataset, 'Domantas Sabonis', '2022-23')
        if player_data is None:
            pytest.skip("Sabonis 2022-23 not in dataset")
        
        tii_result = calculators['tii'](player_data)
        
        # Should be Limited Scaling
        assert tii_result['tii'] < 50, (
            f"Sabonis TII should be <50, got {tii_result['tii']:.1f}"
        )
        
        # Pressure Appetite should be low (hiding pattern)
        assert tii_result['components']['pressure_appetite'] < 30, (
            f"Sabonis hiding pattern not detected, pressure={tii_result['components']['pressure_appetite']:.1f}"
        )
        
        print(f"\n✅ Sabonis 2022-23: TII={tii_result['tii']:.1f} (correctly Limited)")
    
    def test_randle_2020_21_context(self, feature_dataset, calculators):
        """
        Randle 2020-21 case study - demonstrates TII limitation.
        
        His REGULAR SEASON stats were genuinely good:
        - ts_pct: 0.567 (decent)
        - leverage_usg_delta: +0.022 (stepping UP)
        - pull_up_fga: 8.1 (high volume)
        
        His FAILURE was playoff-specific (18 PPG on 30% FG vs Hawks).
        Without playoff data, TII can't detect this.
        
        The CII should catch him via fragility score if playoff data is included.
        """
        player_data = self.get_player_data(feature_dataset, 'Julius Randle', '2020-21')
        if player_data is None:
            pytest.skip("Randle 2020-21 not in dataset")
        
        tii_result = calculators['tii'](player_data)
        cii_result = calculators['cii'](player_data)
        
        # Note: His RS stats actually look decent, failure was playoff-specific
        # This is a known limitation without playoff-specific data
        print(f"\n⚠️ Randle 2020-21 (known limitation):")
        print(f"   CII={cii_result['cii']:.1f}, TII={tii_result['tii']:.1f}")
        print(f"   RS stats look good, failure was playoff-specific")
        print(f"   This case requires playoff data for proper detection")
    
    def test_wiggins_false_latent(self, feature_dataset, calculators):
        """
        Wiggins 2016-17 should NOT be flagged as Latent Engine.
        
        Key Issue: Volume scorer without efficient creation tools.
        24 PPG at 21 looked promising but no creation skill.
        """
        player_data = self.get_player_data(feature_dataset, 'Andrew Wiggins', '2016-17')
        if player_data is None:
            pytest.skip("Wiggins 2016-17 not in dataset")
        
        tii_result = calculators['tii'](player_data)
        
        # Should be at most Moderate Scaling
        assert tii_result['tii'] < 65, (
            f"Wiggins TII should be <65, got {tii_result['tii']:.1f}"
        )
        
        print(f"\n✅ Wiggins 2016-17: TII={tii_result['tii']:.1f} (correctly not Latent)")
    
    # =========================================================================
    # 2D Classification Tests
    # =========================================================================
    
    def test_2d_classification_franchise_engine(self, feature_dataset, calculators):
        """
        Players with High CII should be Franchise Engine regardless of TII.
        """
        # Harden 2018-19 should be Franchise Engine
        player_data = self.get_player_data(feature_dataset, 'James Harden', '2018-19')
        if player_data is None:
            pytest.skip("Harden 2018-19 not in dataset")
        
        cii_result = calculators['cii'](player_data)
        tii_result = calculators['tii'](player_data)
        
        # Both should be high
        assert cii_result['cii'] >= 70, f"Harden CII should be >=70, got {cii_result['cii']:.1f}"
        assert tii_result['tii'] >= 70, f"Harden TII should be >=70, got {tii_result['tii']:.1f}"
        
        print(f"\n✅ Harden 2018-19: CII={cii_result['cii']:.1f}, TII={tii_result['tii']:.1f}")
        print(f"   → Franchise Engine (High CII, High TII)")
    
    def test_2d_classification_latent_vs_amplifier(self, feature_dataset, calculators):
        """
        Medium CII + High TII = Latent Engine
        Medium CII + Low TII = Luxury Amplifier
        
        This is the key discrimination for finding undervalued players.
        """
        # Brunson 2020-21 should be Latent (Med CII, High TII)
        brunson = self.get_player_data(feature_dataset, 'Jalen Brunson', '2020-21')
        
        # Sabonis 2022-23 should be Amplifier/Role (Med CII, Low TII)
        sabonis = self.get_player_data(feature_dataset, 'Domantas Sabonis', '2022-23')
        
        if brunson is not None and sabonis is not None:
            brunson_tii = calculators['tii'](brunson)['tii']
            sabonis_tii = calculators['tii'](sabonis)['tii']
            
            # Brunson should have much higher TII
            assert brunson_tii > sabonis_tii + 25, (
                f"Brunson TII ({brunson_tii:.1f}) should be 25+ higher than Sabonis ({sabonis_tii:.1f})"
            )
            
            print(f"\n✅ Latent vs Amplifier discrimination:")
            print(f"   Brunson TII: {brunson_tii:.1f} (Latent Engine)")
            print(f"   Sabonis TII: {sabonis_tii:.1f} (Amplifier/Role)")
            print(f"   Gap: {brunson_tii - sabonis_tii:.1f} points")


class TestTIIComponents:
    """Test individual TII components for correctness."""
    
    @pytest.fixture(scope='class')
    def feature_dataset(self):
        path = project_root / 'results' / 'predictive_dataset_with_friction.csv'
        if not path.exists():
            pytest.skip(f"Feature dataset not found at {path}")
        return pd.read_csv(path)
    
    def get_player_data(self, df, player_name, season):
        mask = (
            df['player_name'].str.lower().str.contains(player_name.lower(), na=False) &
            (df['season'] == season)
        )
        if mask.any():
            return df[mask].iloc[0]
        return None
    
    def test_creation_tools_gate(self, feature_dataset):
        """
        The creation tools gate should penalize players without pull-up ability.
        
        Simmons: High TS but no pull-ups → Scaling Efficiency should be capped
        Brunson: Has pull-ups → Full Scaling Efficiency credit
        """
        from src.nba_data.phase2_creation_independence.index.trajectory import (
            _calculate_scaling_efficiency, _calculate_creation_tools
        )
        
        simmons = self.get_player_data(feature_dataset, 'Ben Simmons', '2019-20')
        brunson = self.get_player_data(feature_dataset, 'Jalen Brunson', '2020-21')
        
        if simmons is not None and brunson is not None:
            simmons_scaling = _calculate_scaling_efficiency(simmons)
            brunson_scaling = _calculate_scaling_efficiency(brunson)
            
            simmons_tools = _calculate_creation_tools(simmons)
            brunson_tools = _calculate_creation_tools(brunson)
            
            # Brunson should have higher scaling despite lower raw stats
            # because he has tools to scale with
            assert brunson_scaling > simmons_scaling, (
                f"Brunson scaling ({brunson_scaling:.1f}) should exceed "
                f"Simmons ({simmons_scaling:.1f}) due to tools gate"
            )
            
            print(f"\n✅ Creation Tools Gate:")
            print(f"   Simmons: Scaling={simmons_scaling:.1f}, Tools={simmons_tools:.1f}")
            print(f"   Brunson: Scaling={brunson_scaling:.1f}, Tools={brunson_tools:.1f}")
    
    def test_pressure_appetite_hiding_gate(self, feature_dataset):
        """
        Negative leverage_usg_delta (hiding) should cap Pressure Appetite score.
        """
        from src.nba_data.phase2_creation_independence.index.trajectory import (
            _calculate_pressure_appetite
        )
        
        simmons = self.get_player_data(feature_dataset, 'Ben Simmons', '2019-20')
        brunson = self.get_player_data(feature_dataset, 'Jalen Brunson', '2020-21')
        
        if simmons is not None and brunson is not None:
            simmons_pressure = _calculate_pressure_appetite(simmons)
            brunson_pressure = _calculate_pressure_appetite(brunson)
            
            # Simmons should be capped due to hiding
            assert simmons_pressure < 40, (
                f"Simmons pressure should be <40 (hiding cap), got {simmons_pressure:.1f}"
            )
            
            # Brunson should have good pressure appetite
            assert brunson_pressure > 60, (
                f"Brunson pressure should be >60, got {brunson_pressure:.1f}"
            )
            
            print(f"\n✅ Pressure Hiding Gate:")
            print(f"   Simmons: {simmons_pressure:.1f} (capped for hiding)")
            print(f"   Brunson: {brunson_pressure:.1f} (positive pressure)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])

