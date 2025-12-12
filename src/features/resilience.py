import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def calculate_simple_resilience():
    # 1. Load Data
    data_path = Path("data/training_dataset.csv")
    if not data_path.exists():
        print("❌ Training data not found!")
        return
        
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} rows.")
    
    # 2. Recalculate Metrics (Fixing potential upstream errors)
    
    # --- Regular Season ---
    # Estimate RS Possessions per Game: (MIN * PACE) / 48
    df['rs_poss_est'] = (df['rs_min'] * df['rs_pace']) / 48
    
    # RS True Shot Attempts
    df['rs_tsa'] = df['rs_fga'] + 0.44 * df['rs_fta']
    
    # RS Volume (TSA per 75)
    # If rs_poss_est is 0, avoid div/0
    df['rs_vol_75'] = np.where(
        df['rs_poss_est'] > 0,
        (df['rs_tsa'] / df['rs_poss_est']) * 75,
        0
    )
    
    # RS Efficiency (TS%) - Recalculate to be safe
    # TS% = PTS / (2 * TSA)
    df['rs_ts_pct_calc'] = np.where(
        df['rs_tsa'] > 0,
        df['rs_pts'] / (2 * df['rs_tsa']),
        0
    )
    
    # --- Playoffs ---
    # PO True Shot Attempts
    df['po_tsa'] = df['po_fga'] + 0.44 * df['po_fta']
    
    # PO Volume (TSA per 75)
    df['po_vol_75'] = np.where(
        df['po_poss_total'] > 0,
        (df['po_tsa'] / df['po_poss_total']) * 75,
        0
    )
    
    # PO Efficiency (TS%)
    df['po_ts_pct_calc'] = np.where(
        df['po_tsa'] > 0,
        df['po_pts'] / (2 * df['po_tsa']),
        0
    )
    
    # 3. Calculate Ratios
    df['vol_ratio'] = np.where(
        df['rs_vol_75'] > 0,
        df['po_vol_75'] / df['rs_vol_75'],
        0
    )
    
    df['eff_ratio'] = np.where(
        df['rs_ts_pct_calc'] > 0,
        df['po_ts_pct_calc'] / df['rs_ts_pct_calc'],
        0
    )
    
    # 4. Resilience Quotient
    df['resilience_quotient'] = df['vol_ratio'] * df['eff_ratio']
    
    # 5. Dominance Score (PO PPG per 75)
    df['dominance_score'] = np.where(
        df['po_poss_total'] > 0,
        (df['po_pts'] / df['po_poss_total']) * 75,
        0
    )
    
    # 6. Filtering
    # We want significant series.
    # DeRozan 2016 series were ~220-260 mins.
    # Let's set min minutes to 150 (approx 4-5 games of starter minutes)
    MIN_PO_MINUTES = 150 
    MIN_DOMINANCE = 10 # Keep it low to include "Victims" but exclude bench warmers
    
    df_filtered = df[
        (df['po_minutes_total'] >= MIN_PO_MINUTES) & 
        (df['dominance_score'] >= MIN_DOMINANCE)
    ].copy()
    
    print(f"Filtered to {len(df_filtered)} significant player-series (Min {MIN_PO_MINUTES} mins, {MIN_DOMINANCE} Dom).")
    
    # 7. Archetypes
    def classify_archetype(row):
        rq = row['resilience_quotient']
        dom = row['dominance_score']
        
        # Thresholds
        RQ_THRESHOLD = 0.95
        DOM_THRESHOLD = 20.0
        
        if dom >= DOM_THRESHOLD:
            if rq >= RQ_THRESHOLD:
                return "King (Resilient Star)"
            else:
                return "Bulldozer (Fragile Star)"
        else:
            if rq >= RQ_THRESHOLD:
                return "Sniper (Resilient Role)"
            else:
                return "Victim (Fragile Role)"

    df_filtered['archetype'] = df_filtered.apply(classify_archetype, axis=1)
    
    # 8. Save Results
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    # Save CSV
    cols_to_save = [
        'PLAYER_NAME', 'SEASON', 'OPPONENT_ABBREV', 
        'resilience_quotient', 'dominance_score', 'archetype',
        'vol_ratio', 'eff_ratio', 'rs_vol_75', 'po_vol_75',
        'rs_ts_pct_calc', 'po_ts_pct_calc', 'po_minutes_total'
    ]
    df_filtered[cols_to_save].sort_values(['PLAYER_NAME', 'SEASON']).to_csv(output_dir / "resilience_archetypes.csv", index=False)
    print(f"Saved results to {output_dir / 'resilience_archetypes.csv'}")
    
    # 9. Plot
    plot_archetypes(df_filtered, output_dir)

def plot_archetypes(df, output_dir):
    plt.figure(figsize=(12, 10))
    
    # Color map
    colors = {
        "King (Resilient Star)": "#2ecc71",      # Green
        "Bulldozer (Fragile Star)": "#f1c40f",   # Yellow
        "Sniper (Resilient Role)": "#3498db",    # Blue
        "Victim (Fragile Role)": "#e74c3c"       # Red
    }
    
    sns.scatterplot(
        data=df,
        x='dominance_score',
        y='resilience_quotient',
        hue='archetype',
        palette=colors,
        s=100,
        alpha=0.7
    )
    
    # Reference lines
    plt.axvline(x=20, color='gray', linestyle='--', alpha=0.5)
    plt.axhline(y=0.95, color='gray', linestyle='--', alpha=0.5)
    
    # Annotate notable cases
    notable_players = [
        ("Luka Dončić", "2020-21"),
        ("Jimmy Butler", "2022-23"),
        ("Jamal Murray", "2019-20"),
        ("Ben Simmons", "2020-21"),
        ("DeMar DeRozan", "2015-16"),
        ("Donovan Mitchell", "2019-20"),
        ("Nikola Jokić", "2020-21")
    ]
    
    for player, season in notable_players:
        player_rows = df[(df['PLAYER_NAME'].str.contains(player)) & (df['SEASON'] == season)]
        for _, row in player_rows.iterrows():
            plt.text(
                row['dominance_score'] + 0.2, 
                row['resilience_quotient'], 
                f"{row['PLAYER_NAME']} ({row['OPPONENT_ABBREV']})", 
                fontsize=8,
                alpha=0.8
            )
            
    plt.title('NBA Playoff Resilience Archetypes (2015-2024)', fontsize=16)
    plt.xlabel('Dominance Score (Playoff PTS/75)', fontsize=12)
    plt.ylabel('Resilience Quotient (Vol Ratio × Eff Ratio)', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    plt.savefig(output_dir / "resilience_archetypes_plot.png", dpi=300, bbox_inches='tight')
    print(f"Saved plot to {output_dir / 'resilience_archetypes_plot.png'}")

if __name__ == "__main__":
    calculate_simple_resilience()