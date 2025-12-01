import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_and_clean_data():
    """
    Load plasticity scores and handle duplicates.
    """
    path = Path("results/plasticity_scores.csv")
    if not path.exists():
        logger.error(f"File not found: {path}")
        return None
    
    df = pd.read_csv(path)
    
    # Drop duplicates: keep first entry for each Player-Season combo
    # The original script might output multiple rows per player due to iteration logic
    initial_len = len(df)
    df = df.drop_duplicates(subset=['PLAYER_ID', 'SEASON'], keep='first')
    logger.info(f"Loaded data. Rows: {initial_len} -> {len(df)} (deduplicated)")
    
    return df

def assign_usage_tiers(df):
    """
    Assign players to usage tiers based on Regular Season shots.
    Using RS_SHOTS as a proxy for usage/role since raw USG% might not be in this file.
    High: Top 25% of volume
    Mid: Middle 50%
    Low: Bottom 25%
    """
    # We use RS_SHOTS as a proxy for role size if USG% isn't available
    # Ideally we'd fetch USG%, but RS_SHOTS is a strong correlate for "Role Size"
    
    # Calculate quantiles for the whole dataset
    q_low = df['RS_SHOTS'].quantile(0.25)
    q_high = df['RS_SHOTS'].quantile(0.75)
    
    def get_tier(shots):
        if shots >= q_high:
            return 'High Usage'
        elif shots <= q_low:
            return 'Low Usage'
        else:
            return 'Mid Usage'
            
    df['USAGE_TIER'] = df['RS_SHOTS'].apply(get_tier)
    
    # Print tier stats
    logger.info("Usage Tier Thresholds:")
    logger.info(f"  High (> {q_high:.0f} shots)")
    logger.info(f"  Low (< {q_low:.0f} shots)")
    logger.info(df['USAGE_TIER'].value_counts())
    
    return df

def calculate_tiered_z_scores(df):
    """
    Calculate Z-scores for Adaptability and Dominance within each Usage Tier.
    CRITICAL UPDATE: Normalized relative to the TIER MEDIAN, not zero.
    High Usage players historically see a drop in efficiency/production (Friction).
    We want to measure how they performed relative to that expected friction.
    """
    # Metrics to normalize
    metrics = {
        'COUNTER_PUNCH_EFF': 'ADAPTABILITY_Z',
        'PRODUCTION_RESILIENCE': 'DOMINANCE_Z'
    }
    
    df_final = pd.DataFrame()
    
    for tier in df['USAGE_TIER'].unique():
        tier_df = df[df['USAGE_TIER'] == tier].copy()
        
        for metric, col_name in metrics.items():
            # We use MEDIAN to capture the "Typical Friction" for this tier
            # e.g., If typical High Usage players drop -0.05, that is the new "0"
            median = tier_df[metric].median()
            std = tier_df[metric].std()
            
            logger.info(f"Tier: {tier}, Metric: {metric}, Median (Baseline): {median:.4f}, Std: {std:.4f}")
            
            # Avoid division by zero
            if std == 0:
                tier_df[col_name] = 0.0
            else:
                # Z-Score relative to the Tier's "Natural Friction"
                tier_df[col_name] = (tier_df[metric] - median) / std
        
        df_final = pd.concat([df_final, tier_df])
        
    return df_final

def classify_archetypes(df):
    """
    Assign archetypes based on the Dual-Grade (Z-Score) quadrants.
    """
    def get_archetype(row):
        adapt = row['ADAPTABILITY_Z']
        dom = row['DOMINANCE_Z']
        
        if adapt >= 0 and dom >= 0:
            return "The Master"      # High Skill, High Will
        elif adapt < 0 and dom >= 0:
            return "The Bulldozer"   # Low Skill, High Will (Spend Eff for Vol)
        elif adapt >= 0 and dom < 0:
            return "The Reluctant Sniper" # High Skill, Low Will (Simmons Zone)
        else:
            return "The Crumble"     # Low Skill, Low Will
            
    df['ARCHETYPE'] = df.apply(get_archetype, axis=1)
    return df

def visualize_archetypes(df):
    """
    Generate the 2D Scatter Plot.
    """
    plt.figure(figsize=(12, 10))
    sns.set_style("whitegrid")
    
    # Define colors for archetypes
    palette = {
        "The Master": "#2ecc71",          # Green
        "The Bulldozer": "#f1c40f",       # Yellow/Orange
        "The Reluctant Sniper": "#3498db", # Blue
        "The Crumble": "#e74c3c"          # Red
    }
    
    # Main scatter
    sns.scatterplot(
        data=df,
        x='DOMINANCE_Z',
        y='ADAPTABILITY_Z',
        hue='ARCHETYPE',
        palette=palette,
        s=60,
        alpha=0.6
    )
    
    # Add Quadrant Lines
    plt.axhline(0, color='black', linestyle='--', alpha=0.5)
    plt.axvline(0, color='black', linestyle='--', alpha=0.5)
    
    # Label Quadrants
    plt.text(3.5, 3.5, "THE MASTER\n(+Adapt, +Dominance)", ha='right', va='top', fontweight='bold')
    plt.text(-3.5, 3.5, "THE RELUCTANT SNIPER\n(+Adapt, -Dominance)", ha='left', va='top', fontweight='bold')
    plt.text(3.5, -3.5, "THE BULLDOZER\n(-Adapt, +Dominance)", ha='right', va='bottom', fontweight='bold')
    plt.text(-3.5, -3.5, "THE CRUMBLE\n(-Adapt, -Dominance)", ha='left', va='bottom', fontweight='bold')
    
    # Annotate Key "Litmus Test" Players
    # We specifically look for the exact seasons mentioned in the prompt
    annotations = [
        ("Giannis Antetokounmpo", "2020-21"),
        ("Ben Simmons", "2020-21"),
        ("Luka Doncic", "2023-24"), # Note: Might not be in dataset yet, check existing
        ("Nikola Jokic", "2022-23"),
        ("James Harden", "2018-19")
    ]
    
    texts = []
    for player, season in annotations:
        p_data = df[(df['PLAYER_NAME'] == player) & (df['SEASON'] == season)]
        if not p_data.empty:
            x = p_data['DOMINANCE_Z'].values[0]
            y = p_data['ADAPTABILITY_Z'].values[0]
            label = f"{player} '{season[2:]}"
            
            plt.plot(x, y, 'ko', markersize=5) # Mark the point
            texts.append(plt.text(x, y+0.1, label, fontsize=9, fontweight='bold'))
            logger.info(f"Found annotation target: {label} -> ({x:.2f}, {y:.2f})")
        else:
            logger.warning(f"Could not find annotation target: {player} {season}")

    plt.title("NBA Playoff Resilience Archetypes: Adaptability vs. Dominance\nNormalized by Usage Tier", fontsize=15)
    plt.xlabel("Dominance (Production Resilience Z-Score)\n<-- Passive | Assertive -->", fontsize=12)
    plt.ylabel("Adaptability (Counter-Punch Efficiency Z-Score)\n<-- Fragile | Scalable -->", fontsize=12)
    
    # Save
    output_path = Path("results/resilience_archetypes_plot.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"Saved plot to {output_path}")
    plt.close()

def main():
    logger.info("Starting Resilience Archetype Analysis...")
    
    # 1. Load
    df = load_and_clean_data()
    if df is None:
        return
    
    # 2. Validate Litmus Test (Raw Scores)
    # Before standardization, let's look at the raw values for our key players
    logger.info("--- LITMUS TEST (RAW SCORES) ---")
    litmus_players = [
        ("Ben Simmons", "2020-21"),
        ("Giannis Antetokounmpo", "2020-21"),
        ("James Harden", "2018-19")
    ]
    
    for p, s in litmus_players:
        row = df[(df['PLAYER_NAME'] == p) & (df['SEASON'] == s)]
        if not row.empty:
            adapt = row['COUNTER_PUNCH_EFF'].values[0]
            dom = row['PRODUCTION_RESILIENCE'].values[0]
            logger.info(f"{p} ({s}): Adapt={adapt:.4f}, Dominance={dom:.4f}")
        else:
            logger.warning(f"Litmus player not found: {p} {s}")
            
    # 3. Tier Assignment
    df = assign_usage_tiers(df)
    
    # 4. Calculate Z-Scores
    df = calculate_tiered_z_scores(df)
    
    # 5. Classify
    df = classify_archetypes(df)
    
    # 6. Save Data
    output_csv = Path("results/resilience_archetypes.csv")
    cols = ['PLAYER_NAME', 'SEASON', 'USAGE_TIER', 'ARCHETYPE', 
            'ADAPTABILITY_Z', 'DOMINANCE_Z', 
            'COUNTER_PUNCH_EFF', 'PRODUCTION_RESILIENCE']
    df[cols].to_csv(output_csv, index=False)
    logger.info(f"Saved classified data to {output_csv}")
    
    # 7. Visualize
    visualize_archetypes(df)
    
    # 8. Player Lookup (if requested)
    lookup_ids = [203507, 1629029, 201935, 1627732, 203999] # Giannis, Luka, Harden, Simmons, Jokic
    logger.info("\n--- PLAYER LOOKUP RESULTS ---")
    lookup_df = df[df['PLAYER_ID'].isin(lookup_ids)].sort_values(['PLAYER_NAME', 'SEASON'])
    
    if not lookup_df.empty:
        print("\n" + lookup_df[['PLAYER_ID', 'PLAYER_NAME', 'SEASON', 'ARCHETYPE', 'ADAPTABILITY_Z', 'DOMINANCE_Z']].to_string(index=False))
    else:
        logger.warning("No players found for lookup.")

    logger.info("Analysis Complete.")

if __name__ == "__main__":
    main()

