import pandas as pd
df = pd.read_csv('results/predictive_dataset_with_friction.csv')
print("Time of Poss stats:")
print(df['time_of_poss'].describe(percentiles=[0.90, 0.95, 0.98, 0.99]))

# We can't check AST_PCT as it's not in the CSV, but we can infer it's similar.

