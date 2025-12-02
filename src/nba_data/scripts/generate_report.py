import pandas as pd
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='results/resilience_report.md')
    args = parser.parse_args()
    
    try:
        df = pd.read_csv('results/resilience_scores_all.csv')
    except FileNotFoundError:
        print("No scores found.")
        return

    with open(args.output, 'w') as f:
        f.write("# Playoff Resilience Report\n\n")
        f.write("## Top 10 Most Resilient Performances\n\n")
        f.write(df.head(10).to_markdown(index=False))
        f.write("\n\n## Bottom 10 Performances\n\n")
        f.write(df.tail(10).sort_values('RESILIENCE_SCORE').to_markdown(index=False))
        
    print(f"Report generated at {args.output}")

if __name__ == "__main__":
    main()


