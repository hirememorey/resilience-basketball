import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        df = pd.read_csv('results/resilience_scores_all.csv')
    except FileNotFoundError:
        logger.error("Results file not found. Run scoring first.")
        return

    # Define test cases
    test_cases = [
        # (Player, Season, Expected Status, Min Score)
        ('Kawhi Leonard', '2018-19', 'ELITE', 1.0), # Raptors Title
        ('Nikola Jokić', '2022-23', 'ELITE', 1.0), # Nuggets Title
        ('Jimmy Butler', '2022-23', 'ELITE', 1.0), # Heat Finals Run
        ('Jamal Murray', '2022-23', 'STRONG', 0.5), # Strong Playoff Performer
        ('Anthony Edwards', '2023-24', 'STRONG', 0.5), # WCF Run
        ('Anthony Davis', '2022-23', 'POSITIVE', 0.0), # Defensive Anchor (Offense varying)
        ('Bam Adebayo', '2022-23', 'POSITIVE', 0.0), # Finals Run
    ]
    
    print("\n🔍 Face Validity Check")
    print("=" * 60)
    
    passed_count = 0
    total_checked = 0
    
    for player_name, season, status, min_score in test_cases:
        # Filter
        # Handle slight name variations (Jokic vs Jokić)
        last_name = player_name.split()[-1]
        if last_name == "Jokić": last_name = "Jokic" # Handle both
        
        player_rows = df[
            (df['PLAYER_NAME'].str.contains(player_name.split()[-1])) & # Search by last name
            (df['SEASON'] == season)
        ]
        
        # Double check full name if multiple matches (e.g. Jalen Williams vs Jaylin Williams)
        # Or simplistic check
        
        if player_rows.empty:
            print(f"⚠️ {player_name} ({season}): NOT FOUND")
            continue
            
        total_checked += 1
        
        # Average resilience across series
        avg_score = player_rows['RESILIENCE_SCORE'].mean()
        
        # Check result
        result = "✅ PASS" if avg_score >= min_score else "❌ FAIL"
        if result == "✅ PASS":
            passed_count += 1
            
        print(f"{result} {player_name} ({season})")
        print(f"   Target: {status} (> {min_score})")
        print(f"   Actual: {avg_score:.3f}")
        print(f"   Series: {player_rows['OPPONENT'].tolist()}")
        print("-" * 60)
        
    if total_checked > 0:
        rate = (passed_count / total_checked) * 100
        print(f"\nFinal Result: {passed_count}/{total_checked} ({rate:.1f}%) passed")
    else:
        print("\nNo test cases found in dataset.")

if __name__ == "__main__":
    main()
