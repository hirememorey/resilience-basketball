import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sqlite3
from scipy import stats

def get_db_connection():
    return sqlite3.connect("data/nba_stats.db")

def calculate_prime_value(player_id, start_year_index=4, end_year_index=8):
    """
    Calculate 'Prime Value' (avg VORP/BPM equivalent) for Years 4-8.
    We will use Win Shares or PER as a proxy if VORP isn't available in our schema,
    or derive a 'Value' metric from available advanced stats (WS/48 or BPM-proxy).
    
    In our current schema, we have 'player_advanced_stats'.
    We can use 'win_percentage' * 'usage_percentage' as a rough 'Value' proxy 
    or 'pie' (Player Impact Estimate) if available. 
    Let's use PIE as it's a catch-all NBA.com metric.
    """
    conn = get_db_connection()
    
    # Get all seasons
    query = f"""
        SELECT season, pie, games_played
        FROM player_advanced_stats
        WHERE player_id = {player_id}
        ORDER BY season ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) < start_year_index:
        return 0
        
    # Take years 4-8 (indices 3 to 7)
    prime_years = df.iloc[3:8] 
    
    if prime_years.empty:
        return 0
        
    # Weighted average by games played
    total_gp = prime_years['games_played'].sum()
    if total_gp == 0:
        return 0
        
    weighted_pie = (prime_years['pie'] * prime_years['games_played']).sum() / total_gp
    return weighted_pie

def visualize_correlation():
    print("📊 Generating Neuroplasticity Correlation Plot...")
    
    # Load Neuroplasticity Results
    try:
        df_nc = pd.read_csv("data/neuroplasticity_results.csv")
    except FileNotFoundError:
        print("Error: data/neuroplasticity_results.csv not found. Run cohort analysis first.")
        return

    # Filter for Raw Prospects (Usage < 20%)
    df_raw = df_nc[df_nc['usg_y1'] < 0.20].copy()
    
    print(f"analyzing {len(df_raw)} 'Raw Prospect' players...")
    
    # Calculate Prime Value for each
    prime_values = []
    for _, row in df_raw.iterrows():
        # Find player_id from name (this is inefficient, better to keep ID in csv, but fine for viz)
        # Actually we didn't save ID in CSV. Let's look it up or modify CSV generation.
        # Modification: We should rely on the fact we can get it from DB by name or 
        # re-run the calculation if needed. 
        # BETTER: Let's just add player_id to the CSV generation in previous step.
        # Fallback: lookup by name.
        
        conn = get_db_connection()
        try:
            pid = pd.read_sql_query(f"SELECT player_id FROM players WHERE player_name = \"{row['player_name']}\"", conn).iloc[0]['player_id']
            val = calculate_prime_value(pid)
            prime_values.append(val)
        except:
            prime_values.append(0)
        conn.close()
            
    df_raw['prime_value'] = prime_values
    
    # Filter out players who didn't make it to Year 4 (Prime Value = 0)
    df_plot = df_raw[df_raw['prime_value'] > 0].copy()
    
    # Calculate Correlation
    r_value, p_value = stats.pearsonr(df_plot['nc_score'], df_plot['prime_value'])
    
    print(f"Correlation (R): {r_value:.3f}")
    print(f"P-Value: {p_value:.4f}")
    
    # Plot
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")
    
    # Scatter plot
    sns.scatterplot(data=df_plot, x='nc_score', y='prime_value', 
                    s=100, alpha=0.7, color='#1d428a') # NBA Blue
    
    # Regression line
    sns.regplot(data=df_plot, x='nc_score', y='prime_value', 
                scatter=False, color='#c8102e') # NBA Red
    
    # Label outliers/top players
    texts = []
    for _, row in df_plot.iterrows():
        if row['nc_score'] > 8 or row['prime_value'] > 0.15:
            plt.text(row['nc_score']+0.2, row['prime_value'], 
                     row['player_name'].split()[-1], fontsize=9)
            
    plt.title(f"Neuroplasticity (Years 1-3) vs Prime Value (Years 4-8)\nRaw Prospects (Y1 Usage < 20%) | R={r_value:.2f}", 
              fontsize=15, fontweight='bold')
    plt.xlabel("Neuroplasticity Score ($N_c$)", fontsize=12)
    plt.ylabel("Prime Value (Avg PIE Years 4-8)", fontsize=12)
    
    plt.axhline(y=0.10, color='gray', linestyle='--', alpha=0.5, label="League Avg Value")
    plt.axvline(x=5.0, color='gray', linestyle='--', alpha=0.5, label="High Learner Threshold")
    
    plt.tight_layout()
    plt.savefig("data/neuroplasticity_correlation.png")
    print("✅ Plot saved to data/neuroplasticity_correlation.png")

if __name__ == "__main__":
    visualize_correlation()


