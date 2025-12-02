
import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/evaluate_plasticity.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PlasticityEngine:
    def __init__(self, season):
        self.season = season
        self.data_dir = Path("data")
        self.results_dir = Path("results")
        self.shot_chart_path = self.data_dir / f"shot_charts_{self.season}.csv"

    def calculate_spatial_metrics(self, df_player):
        """Calculates spatial metrics for a player's shot chart."""
        if df_player.empty or len(df_player) < 10: # Min 10 shots
            return None

        median_dist = df_player['SHOT_DISTANCE'].median()
        std_dist = df_player['SHOT_DISTANCE'].std()
        
        # 2D variance
        loc_x_var = df_player['LOC_X'].var()
        loc_y_var = df_player['LOC_Y'].var()
        spatial_variance = np.sqrt(loc_x_var + loc_y_var)

        return {
            'median_shot_distance': median_dist,
            'std_shot_distance': std_dist,
            'spatial_variance': spatial_variance,
            'total_shots': len(df_player)
        }

    def run(self):
        """Main execution function."""
        if not self.shot_chart_path.exists():
            logger.error(f"Shot chart data not found for {self.season} at {self.shot_chart_path}")
            return

        logger.info(f"Loading shot charts for {self.season}...")
        df_shots = pd.read_csv(self.shot_chart_path)

        # Split RS and PO
        df_rs = df_shots[df_shots['SEASON_TYPE'] == 'Regular Season'].copy()
        df_po = df_shots[df_shots['SEASON_TYPE'] == 'Playoffs'].copy()
    
        player_ids = df_shots['PLAYER_ID'].unique()
        plasticity_results = []

        for player_id in player_ids:
            rs_shots = df_rs[df_rs['PLAYER_ID'] == player_id]
            po_shots = df_po[df_po['PLAYER_ID'] == player_id]

            rs_metrics = self.calculate_spatial_metrics(rs_shots)
            po_metrics = self.calculate_spatial_metrics(po_shots)

            if rs_metrics and po_metrics:
                # Calculate Deltas
                dist_delta = po_metrics['median_shot_distance'] - rs_metrics['median_shot_distance']
                variance_delta = po_metrics['spatial_variance'] - rs_metrics['spatial_variance']
                
                # Efficiency drop-off calculation
                rs_median_dist = rs_metrics['median_shot_distance']
                
                # PO eFG% on shots taken further than the player's RS median
                po_shots_further = po_shots[po_shots['SHOT_DISTANCE'] > rs_median_dist]
                
                if not po_shots_further.empty:
                    made = po_shots_further['SHOT_MADE_FLAG'].sum()
                    attempted = len(po_shots_further)
                    fg3m = po_shots_further[po_shots_further['SHOT_TYPE'] == '3PT Field Goal']['SHOT_MADE_FLAG'].sum()
                    
                    eFG_further = (made + 0.5 * fg3m) / attempted if attempted > 0 else 0
                else:
                    eFG_further = np.nan # Not enough shots to measure

                plasticity_results.append({
                    'PLAYER_ID': player_id,
                    'SEASON': self.season,
                    'RS_MEDIAN_SHOT_DISTANCE': rs_metrics['median_shot_distance'],
                    'PO_MEDIAN_SHOT_DISTANCE': po_metrics['median_shot_distance'],
                    'SHOT_DISTANCE_DELTA': dist_delta,
                    'RS_SPATIAL_VARIANCE': rs_metrics['spatial_variance'],
                    'PO_SPATIAL_VARIANCE': po_metrics['spatial_variance'],
                    'SPATIAL_VARIANCE_DELTA': variance_delta,
                    'PO_EFG_BEYOND_RS_MEDIAN': eFG_further,
                    'RS_SHOTS': rs_metrics['total_shots'],
                    'PO_SHOTS': po_metrics['total_shots']
                })
        
        if plasticity_results:
            df_plasticity = pd.DataFrame(plasticity_results)
            output_path = self.results_dir / f"plasticity_scores_{self.season}.csv"
            df_plasticity.to_csv(output_path, index=False)
            logger.info(f"Saved plasticity scores for {len(df_plasticity)} players to {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Calculate Shot Diet Plasticity')
    parser.add_argument('--seasons', nargs='+', help='Seasons to process (e.g. 2023-24)', required=True)
    args = parser.parse_args()

    for season in args.seasons:
        engine = PlasticityEngine(season)
        engine.run()

if __name__ == "__main__":
    main()

